#!/usr/bin/env python3
"""
Dibs Daily — Deliver Script v2
Rewritten 2026-03-15

Sends the Dibs Daily report link to Telegram with real dynamic data
pulled from today's rotation_state.json. Replaces the old hardcoded
deliver.py that always showed the same stocks.

Usage:
  python3 deliver.py              # Send today's report
  python3 deliver.py --dry-run   # Preview the message only
"""

import json
import requests
import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────
BASE            = Path("/home/astra/.openclaw/workspace")
ROTATION_FILE   = BASE / "daily5/rotation_state.json"
CRED_PATH       = Path.home() / ".openclaw/credentials/telegram.env"
DELIVERY_LOG    = BASE / "daily5/delivery_log.json"

# ─── Telegram ─────────────────────────────────────────────────────────
CHAT_ID         = "791589970"
GITHUB_BASE_URL = "https://astrasyd59-cloud.github.io/empire-command-center/daily5"

# ─── Asset lookup maps ────────────────────────────────────────────────
CRYPTO_NAMES = {
    "BTC": "Bitcoin",  "ETH": "Ethereum",  "SOL": "Solana",
    "ADA": "Cardano",  "DOT": "Polkadot",  "LINK": "Chainlink",
    "MATIC": "Polygon","AVAX": "Avalanche","UNI": "Uniswap",
    "ATOM": "Cosmos"
}

FOREX_NAMES = {
    "EURUSD": "EUR/USD", "USDJPY": "USD/JPY", "GBPUSD": "GBP/USD",
    "AUDUSD": "AUD/USD", "USDCAD": "USD/CAD", "USDCHF": "USD/CHF",
    "NZDUSD": "NZD/USD"
}

# 100-stock rotation list (same order as daily5_builder_v7.py)
SP500_STOCKS = [
    "AAPL","NVDA","MSFT","AMZN","GOOGL","META","TSLA","AVGO","BRK-B","JPM",
    "LLY","V","UNH","XOM","MA","HD","PG","COST","JNJ","NFLX",
    "WMT","ABBV","BAC","KO","CRM","CVX","TMUS","MRK","AMD","PEP",
    "ACN","LIN","TMO","MCD","ADBE","CSCO","WFC","IBM","GE","ABT",
    "DHR","CAT","NOW","AXP","MS","DIS","VZ","TXN","PM","INTU",
    "QCOM","RTX","GS","PGR","AMGN","SPGI","NEE","LOW","T","BLK",
    "BKNG","ELV","SYK","HON","CMCSA","UBER","ETN","UNP","LMT","PFE",
    "COP","TJX","BMY","UPS","AXP","NKE","ISRG","SCHW","AMAT","DE",
    "BA","GILD","ADI","MMC","VRTX","PLD","MDT","ADI","PANW","SO",
    "SHW","HCA","BMY","SBUX","TGT","MO","ZTS","C","AON","USB"
]

CRYPTO_LIST  = ["BTC","ETH","SOL","ADA","DOT","LINK","MATIC","AVAX","UNI","ATOM"]
FOREX_PAIRS  = ["EURUSD","USDJPY","GBPUSD","AUDUSD","USDCAD","USDCHF","NZDUSD"]
CFA_TOPICS   = [
    "Ethical & Professional Standards","Quantitative Methods","Economics",
    "Financial Reporting & Analysis","Corporate Finance","Equity Investments",
    "Fixed Income","Derivatives","Alternative Investments","Portfolio Management"
]


def aedt_now():
    """Return current datetime in AEDT (UTC+11 until first Sun April)."""
    aedt = timezone(timedelta(hours=11))
    return datetime.now(aedt)


def load_rotation():
    """Load rotation state from JSON file."""
    if not ROTATION_FILE.exists():
        print(f"[ERROR] Rotation state file not found: {ROTATION_FILE}")
        return None
    with open(ROTATION_FILE) as f:
        return json.load(f)


def load_telegram_token():
    """Load Telegram bot token from credentials file."""
    if not CRED_PATH.exists():
        print(f"[ERROR] Telegram credentials not found: {CRED_PATH}")
        return None
    with open(CRED_PATH) as f:
        for line in f:
            line = line.strip()
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                return line.split("=", 1)[1].strip('"\'')
    print("[ERROR] TELEGRAM_BOT_TOKEN not found in credentials file")
    return None


def build_message(rotation, today_str, today_aedt):
    """Build the Telegram message with live rotation data."""
    # Get today's stocks
    stock_idx    = rotation.get("stock_index", 0)
    crypto_idx   = rotation.get("crypto_index", 0)
    forex_idx    = rotation.get("forex_index", 0)
    cfa_idx      = rotation.get("cfa_index", 0)

    stocks       = SP500_STOCKS[stock_idx:stock_idx + 5]
    crypto_sym   = CRYPTO_LIST[crypto_idx % len(CRYPTO_LIST)]
    forex_sym    = FOREX_PAIRS[forex_idx % len(FOREX_PAIRS)]
    cfa_topic    = CFA_TOPICS[cfa_idx % len(CFA_TOPICS)]
    crypto_name  = CRYPTO_NAMES.get(crypto_sym, crypto_sym)
    forex_name   = FOREX_NAMES.get(forex_sym, forex_sym)
    batch_num    = (stock_idx // 5) + 1
    sp_start     = stock_idx + 1
    sp_end       = min(stock_idx + 5, 100)
    stocks_fmt   = " · ".join(stocks)
    day_name     = today_aedt.strftime("%A")
    date_fmt     = today_aedt.strftime("%d %b %Y")
    time_fmt     = today_aedt.strftime("%H:%M")
    report_url   = f"{GITHUB_BASE_URL}/{today_str}.html"

    message = f"""📊 <b>Dibs Daily</b> · {day_name} {date_fmt}

📈 <b>S&P Batch {batch_num}</b> ({sp_start}–{sp_end}/100)
{stocks_fmt}

🔷 <b>Crypto:</b> {crypto_name} ({crypto_sym})
💱 <b>Forex:</b> {forex_name}
📚 <b>CFA:</b> {cfa_topic}

━━━━━━━━━━━━━━━━
⏰ Generated: {time_fmt} AEDT
🔗 <a href="{report_url}">Open Report →</a>"""

    return message


def send_telegram(token, message, dry_run=False):
    """Send the message via Telegram API."""
    if dry_run:
        print("\n── DRY RUN ─────────────────────────")
        print(message)
        print("────────────────────────────────────\n")
        return True

    url     = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id":                  CHAT_ID,
        "text":                     message,
        "parse_mode":               "HTML",
        "disable_web_page_preview": False,
        "link_preview_options":     {"is_disabled": False}
    }

    try:
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code == 200:
            print(f"[OK] Dibs Daily sent to Telegram at {datetime.now().strftime('%H:%M:%S')}")
            return True
        else:
            print(f"[ERROR] Telegram API: {resp.status_code} — {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to reach Telegram: {e}")
        return False


def log_delivery(today_str, success, error=None):
    """Append delivery result to log file."""
    log = []
    if DELIVERY_LOG.exists():
        try:
            with open(DELIVERY_LOG) as f:
                log = json.load(f)
        except Exception:
            log = []

    log.append({
        "date":         today_str,
        "delivered_at": datetime.now().isoformat(),
        "success":      success,
        "error":        error
    })

    # Keep last 30 entries only
    log = log[-30:]

    with open(DELIVERY_LOG, "w") as f:
        json.dump(log, f, indent=2)


def main():
    dry_run = "--dry-run" in sys.argv

    today_aedt = aedt_now()
    today_str  = today_aedt.strftime("%Y-%m-%d")

    print(f"[DELIVER] Dibs Daily — {today_str}")
    print(f"[DELIVER] Mode: {'DRY RUN' if dry_run else 'LIVE'}")

    # Check report exists
    report_path = BASE / f"daily5/{today_str}.html"
    if not report_path.exists():
        print(f"[WARN] Report file not found: {report_path}")
        print("[WARN] Sending delivery anyway — report may not be on GitHub Pages yet")

    # Load rotation state
    rotation = load_rotation()
    if not rotation:
        log_delivery(today_str, False, "Rotation state file missing")
        sys.exit(1)

    # Build message
    message = build_message(rotation, today_str, today_aedt)

    # Load Telegram token
    token = load_telegram_token()
    if not token and not dry_run:
        log_delivery(today_str, False, "Telegram token missing")
        sys.exit(1)

    # Send
    success = send_telegram(token, message, dry_run=dry_run)

    # Log
    log_delivery(today_str, success, None if success else "Telegram API error")

    if success:
        print(f"[DONE] Delivery complete — {today_str}")
    else:
        print(f"[FAIL] Delivery failed — check {DELIVERY_LOG}")
        sys.exit(1)


if __name__ == "__main__":
    main()
