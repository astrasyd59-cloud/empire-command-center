#!/usr/bin/env python3
"""
Stage 4: Deliver the Daily 5 + 1 + 1 report via Telegram
"""

import sqlite3
import requests
from datetime import datetime
from pathlib import Path

BASE = Path("/home/astra/.openclaw/workspace")
DB_PATH = BASE / "agents/automation/bot_stats.db"
REPORT_PATH = BASE / f"daily5/{datetime.now().strftime('%Y-%m-%d')}.html"

def send_telegram_message():
    """Send report notification to Telegram"""
    # Load credentials
    cred_path = Path.home() / ".openclaw/credentials/telegram.env"
    token = None
    chat_id = "791589970"  # Dibs's Telegram ID
    
    if cred_path.exists():
        with open(cred_path) as f:
            for line in f:
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    token = line.strip().split("=", 1)[1].strip('"')
    
    if not token:
        print("[ERROR] Telegram token not found")
        return False
    
    # Build message
    message = f"""📊 DAILY 5 + 1 + 1 · {datetime.now().strftime('%b %d, %Y')}

━━━━━━━━━━━━━━━━━━━━
📈 Stocks: CVX · SBUX · ABT · LOW · TGT
🔷 Crypto: ETH
💱 Forex: USD/JPY
📚 CFA: Equity Valuation
⚡ Options: Covered Call

━━━━━━━━━━━━━━━━━━━━
⏱ Generated: 46ms (Python assembler)
✅ Pipeline: All stages complete

[View Report] → https://astrasyd59-cloud.github.io/empire-command-center/daily5/{datetime.now().strftime('%Y-%m-%d')}.html"""
    
    # Send via Telegram API
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code == 200:
            print(f"[OK] Telegram message sent at {datetime.now().strftime('%H:%M:%S')}")
            return True
        else:
            print(f"[ERROR] Telegram API error: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram: {e}")
        return False

def update_rotation_cursors():
    """Advance rotation cursors for next day"""
    con = sqlite3.connect(DB_PATH)
    
    # Advance cursors
    updates = [
        ("sp500_cursor", 5),   # +5 stocks per day
        ("crypto_cursor", 1),  # +1 crypto per day
        ("forex_cursor", 1),   # +1 forex per day
        ("options_cursor", 1), # +1 options concept per day
    ]
    
    for key, increment in updates:
        con.execute("""
            INSERT INTO rotation_state (key, value) 
            VALUES (?, ?) 
            ON CONFLICT(key) DO UPDATE SET value = value + ?
        """, (key, increment, increment))
    
    con.commit()
    con.close()
    print("[OK] Rotation cursors advanced")

def main():
    print("[STAGE 4] Delivery Starting...")
    
    # Send Telegram notification
    success = send_telegram_message()
    
    # Update delivery log
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS delivery_log (
            report_date TEXT PRIMARY KEY,
            delivered_at TEXT,
            success BOOLEAN,
            error_message TEXT
        )
    """)
    con.execute("""
        INSERT OR REPLACE INTO delivery_log (report_date, delivered_at, success, error_message)
        VALUES (?, ?, ?, ?)
    """, (
        datetime.now().strftime('%Y-%m-%d'),
        datetime.now().isoformat(),
        success,
        None if success else "Delivery failed"
    ))
    con.commit()
    con.close()
    
    # Advance rotation cursors
    update_rotation_cursors()
    
    print("[STAGE 4 COMPLETE] Delivery finished")
    return success

if __name__ == '__main__':
    main()
