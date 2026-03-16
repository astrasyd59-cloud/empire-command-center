#!/usr/bin/env python3
"""
Daily 5 + 1 Brief Builder v6
==============================
"""

import os
import json
import subprocess
import urllib.request
import urllib.parse
import datetime
import time
import sys

# CONFIG
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT = os.environ.get("TELEGRAM_CHAT", "791589970")
GITHUB_REPO_DIR = os.environ.get("GITHUB_REPO_DIR", "/home/astra/.openclaw/workspace")
DEPLOY_SUBDIR = "daily5"
GITHUB_PAGES_BASE = "https://astrasyd59-cloud.github.io/empire-command-center"

# Today's data
TODAY = datetime.date.today()
DATE_STR = TODAY.strftime("%Y-%m-%d")
DATE_PRETTY = TODAY.strftime("%B %d, %Y")

# Market Data (from this morning's cron run)
STOCKS = [
    {"ticker": "AAPL", "price": "$272.46", "change": "+2.36%", "dir": "up", "signal": "LONG",
     "entry": "$270-272", "target": "$285", "stop": "$265", "pattern": "Bull Flag 4H",
     "rationale": "Breaking above resistance. Strong momentum above EMA20 with volume confirmation.",
     "street": "GS raised PT to $285 citing services growth."},
    {"ticker": "NVDA", "price": "$192.58", "change": "+0.54%", "dir": "up", "signal": "LONG",
     "entry": "$190-193", "target": "$210", "stop": "$185", "pattern": "Ascending Triangle",
     "rationale": "Consolidating after earnings. AI demand remains strong.",
     "street": "MS maintains Overweight. H200 ramp driving estimates higher."},
    {"ticker": "MSFT", "price": "$387.75", "change": "+0.85%", "dir": "up", "signal": "NEUTRAL",
     "entry": "$380-385", "target": "$405", "stop": "$370", "pattern": "Range Bound",
     "rationale": "Trading in established range. Awaiting catalyst.",
     "street": "Citi sees Azure growth stabilizing. PT $420."},
    {"ticker": "AMZN", "price": "$210.17", "change": "+2.39%", "dir": "up", "signal": "LONG",
     "entry": "$205-210", "target": "$225", "stop": "$198", "pattern": "Breakout",
     "rationale": "Breaking above 200-day MA. Retail + AWS momentum.",
     "street": "Bernstein upgrades to Outperform. Prime growth accelerating."},
    {"ticker": "GOOGL", "price": "$310.83", "change": "-0.21%", "dir": "down", "signal": "NEUTRAL",
     "entry": "$305-310", "target": "$325", "stop": "$295", "pattern": "Consolidation",
     "rationale": "Awaiting AI product announcements. Search stable.",
     "street": "RBC maintains Sector Perform. Gemini integration key."},
]

CRYPTO = {
    "bitcoin": {"usd": 95423, "usd_24h_change": 0.8, "usd_market_cap": 1.89e12},
    "ethereum": {"usd": 1858, "usd_24h_change": 0.16, "usd_market_cap": 2.23e11},
    "solana": {"usd": 82.49, "usd_24h_change": 1.2, "usd_market_cap": 3.86e10},
}

MACRO = {
    "VIX": {"value": "19.37", "change": "-7.81%", "dir": "down"},
    "DXY": {"value": "97.84", "change": "+0.14%", "dir": "up"},
    "10Y": {"value": "4.03%", "change": "-1.40%", "dir": "down"},
    "GOLD": {"value": "$5,178", "change": "-0.50%", "dir": "down"},
    "SPX": {"value": "6,838", "change": "-1.04%", "dir": "down"},
}

MURPHY_QUOTES = [
    ("The trend is your friend until the end where it bends.", "John Murphy", "Technical Analysis, Ch.4"),
    ("Volume must confirm the trend.", "John Murphy", "Technical Analysis, Ch.7"),
]

CFA_QUESTIONS = [
    {
        "q": "A stock has a beta of 1.2. If the market drops 5%, what is the expected return?",
        "opts": ["A. -4%", "B. -5%", "C. -6%", "D. -7%"],
        "ans": "C",
        "exp": "Expected return = Beta × Market return = 1.2 × -5% = -6%"
    },
    {
        "q": "Which valuation metric is most appropriate for comparing companies with different capital structures?",
        "opts": ["A. P/E ratio", "B. EV/EBITDA", "C. P/B ratio", "D. Dividend yield"],
        "ans": "B",
        "exp": "EV/EBITDA is capital structure neutral as it uses Enterprise Value (debt + equity)."
    },
]

def build_html():
    import random
    quote = random.choice(MURPHY_QUOTES)
    
    # Build stock cards
    stock_cards = ""
    for i, s in enumerate(STOCKS):
        signal_class = "signal-long" if s["signal"] == "LONG" else ("signal-short" if s["signal"] == "SHORT" else "signal-watch")
        dir_class = "positive" if s["dir"] == "up" else "negative"
        
        stock_cards += f"""
        <div class="stock-card" style="animation-delay:{i*0.1}s">
            <div class="stock-header">
                <div class="ticker-block">
                    <span class="ticker">{s['ticker']}</span>
                    <span class="stock-price">{s['price']} <span class="{dir_class}">{s['change']}</span></span>
                </div>
                <span class="signal-badge {signal_class}">{s['signal']}</span>
            </div>
            <div class="levels-row">
                <div class="level-item"><span class="lbl">Entry</span><span class="lvl-val">{s['entry']}</span></div>
                <div class="level-item"><span class="lbl">Target</span><span class="lvl-val green">{s['target']}</span></div>
                <div class="level-item"><span class="lbl">Stop</span><span class="lvl-val red">{s['stop']}</span></div>
            </div>
            <div class="rationale">{s['rationale']}</div>
            <div class="street-commentary">🏦 {s['street']}</div>
        </div>"""
    
    # Build macro strip
    macro_html = "".join(f"""<div class="macro-item">
        <span class="macro-lbl">{k}</span>
        <span class="macro-val" style="color:{'#00d084' if v['dir']=='up' else '#ff4757'}">{v['value']}</span>
        <span class="macro-chg">{v['change']}</span>
    </div>""" for k, v in MACRO.items())
    
    # Build crypto cards
    btc = CRYPTO["bitcoin"]
    eth = CRYPTO["ethereum"]
    sol = CRYPTO["solana"]
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Daily 5 + 1 | {DATE_PRETTY}</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&amp;family=DM+Mono:wght@400;500&amp;family=DM+Sans:wght@300;400;500&amp;display=swap" rel="stylesheet">
    <style>
        :root {{ --bg: #07070d; --bg-card: #111118; --border: rgba(212,175,55,0.15); --gold: #d4af37; --green: #00d084; --red: #ff4757; --text: #e8e8e8; --dim: #7a7a8c; --head: 'Playfair Display', serif; --mono: 'DM Mono', monospace; --body: 'DM Sans', sans-serif; }}
        body {{ background: var(--bg); color: var(--text); font-family: var(--body); font-size: 14px; line-height: 1.6; margin: 0; padding: 20px; }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        .logo {{ font-family: var(--head); font-size: 48px; font-weight: 900; color: var(--gold); text-align: center; margin-bottom: 8px; }}
        .subtitle {{ text-align: center; color: var(--dim); font-family: var(--mono); font-size: 12px; margin-bottom: 24px; }}
        .macro-strip {{ display: flex; flex-wrap: wrap; gap: 4px; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 12px; margin-bottom: 24px; }}
        .macro-item {{ display: flex; flex-direction: column; align-items: center; padding: 6px 14px; border-right: 1px solid var(--border); }}
        .macro-lbl {{ font-family: var(--mono); font-size: 10px; color: var(--dim); }}
        .macro-val {{ font-family: var(--mono); font-size: 15px; font-weight: 500; }}
        .murphy-block {{ border-left: 3px solid var(--gold); background: rgba(212,175,55,0.06); padding: 16px; margin-bottom: 24px; border-radius: 0 8px 8px 0; }}
        .murphy-quote {{ font-family: var(--head); font-style: italic; font-size: 18px; }}
        .murphy-attr {{ font-family: var(--mono); font-size: 10px; color: var(--dim); margin-top: 8px; }}
        .section-title {{ font-family: var(--mono); font-size: 11px; letter-spacing: 3px; color: var(--gold); text-transform: uppercase; padding: 8px 0; margin-bottom: 16px; border-bottom: 1px solid var(--border); }}
        .stock-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; margin-bottom: 32px; }}
        .stock-card {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 18px; }}
        .stock-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
        .ticker {{ font-family: var(--head); font-size: 24px; font-weight: 700; }}
        .stock-price {{ font-family: var(--mono); font-size: 13px; }}
        .signal-badge {{ font-family: var(--mono); font-size: 10px; padding: 4px 10px; border-radius: 4px; }}
        .signal-long {{ background: rgba(0,208,132,0.15); color: var(--green); border: 1px solid rgba(0,208,132,0.3); }}
        .signal-watch {{ background: rgba(255,179,71,0.15); color: #ffb347; border: 1px solid rgba(255,179,71,0.3); }}
        .levels-row {{ display: flex; gap: 8px; margin-bottom: 10px; }}
        .level-item {{ background: #1a1a25; padding: 6px 10px; border-radius: 6px; min-width: 70px; }}
        .lbl {{ font-family: var(--mono); font-size: 9px; color: var(--dim); display: block; }}
        .lvl-val {{ font-family: var(--mono); font-size: 12px; font-weight: 500; }}
        .green {{ color: var(--green); }} .red {{ color: var(--red); }}
        .positive {{ color: var(--green); }} .negative {{ color: var(--red); }}
        .rationale {{ font-size: 12px; color: var(--dim); margin-bottom: 8px; }}
        .street-commentary {{ font-size: 11px; color: var(--dim); }}
        .crypto-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; margin-bottom: 32px; }}
        .crypto-card {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 16px; }}
        .crypto-name {{ font-family: var(--mono); font-size: 10px; color: var(--dim); text-transform: uppercase; }}
        .crypto-price {{ font-family: var(--head); font-size: 22px; font-weight: 700; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">THE DAILY 5 + 1</div>
        <div class="subtitle">{DATE_PRETTY} · 5 Equities · 1 Crypto · Macro · Murphy</div>
        
        <div class="macro-strip">{macro_html}</div>
        
        <div class="murphy-block">
            <div class="murphy-quote">"{quote[0]}"</div>
            <div class="murphy-attr">— {quote[1]} · {quote[2]}</div>
        </div>
        
        <div class="section-title">Equity Picks</div>
        <div class="stock-grid">{stock_cards}</div>
        
        <div class="section-title">Crypto</div>
        <div class="crypto-grid">
            <div class="crypto-card">
                <div class="crypto-name">Bitcoin</div>
                <div class="crypto-price">${btc['usd']:,.0f}</div>
                <div style="color:{'#00d084' if btc['usd_24h_change'] >= 0 else '#ff4757'}">{btc['usd_24h_change']:+.1f}%</div>
            </div>
            <div class="crypto-card">
                <div class="crypto-name">Ethereum</div>
                <div class="crypto-price">${eth['usd']:,.0f}</div>
                <div style="color:{'#00d084' if eth['usd_24h_change'] >= 0 else '#ff4757'}">{eth['usd_24h_change']:+.1f}%</div>
            </div>
            <div class="crypto-card">
                <div class="crypto-name">Solana</div>
                <div class="crypto-price">${sol['usd']:,.2f}</div>
                <div style="color:{'#00d084' if sol['usd_24h_change'] >= 0 else '#ff4757'}">{sol['usd_24h_change']:+.1f}%</div>
            </div>
        </div>
    </div>
</body>
</html>"""

def deploy(html):
    deploy_dir = os.path.join(GITHUB_REPO_DIR, DEPLOY_SUBDIR)
    os.makedirs(deploy_dir, exist_ok=True)
    
    filepath = os.path.join(deploy_dir, f"{DATE_STR}.html")
    index_path = os.path.join(deploy_dir, "index.html")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"[INFO] Written: {filepath}")
    
    # Git deploy
    try:
        subprocess.run(["git", "-C", GITHUB_REPO_DIR, "add", "-A"], check=True)
        subprocess.run(["git", "-C", GITHUB_REPO_DIR, "commit", "-m", f"Daily 5+1 {DATE_STR}"], check=False)
        subprocess.run(["git", "-C", GITHUB_REPO_DIR, "push"], check=True)
        print("[INFO] Git push complete")
        return True
    except Exception as e:
        print(f"[ERROR] Git: {e}")
        return False

def main():
    print(f"[INFO] Building Daily 5+1 for {DATE_STR}")
    html = build_html()
    deployed = deploy(html)
    
    if deployed:
        url = f"{GITHUB_PAGES_BASE}/{DEPLOY_SUBDIR}/"
        print(f"[DONE] Report live: {url}")
        
        # Send Telegram
        if TELEGRAM_TOKEN:
            import urllib.request
            msg = f"📊 Daily 5 + 1 Ready\\n📅 {DATE_PRETTY}\\n\\n🔗 {url}"
            data = urllib.parse.urlencode({"chat_id": TELEGRAM_CHAT, "text": msg, "parse_mode": "Markdown"}).encode()
            try:
                urllib.request.urlopen(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data=data, timeout=10)
            except:
                pass
    else:
        print("[ERROR] Deploy failed")

if __name__ == "__main__":
    main()
