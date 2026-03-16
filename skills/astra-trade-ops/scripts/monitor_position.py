#!/usr/bin/env python3
"""
ASTRA Position Monitor
Overnight price monitoring with Telegram alerts
"""

import os, sys, argparse
from datetime import datetime
from pathlib import Path

try:
    import yfinance as yf
    import psycopg2
    import requests
except ImportError as e:
    print(f"Missing package: {e}")
    print("Run: pip install yfinance psycopg2-binary requests")
    sys.exit(1)

# Database config
DB_CONFIG = {
    'dbname': 'openclaw_db',
    'user': 'astra_user',
    'password': os.environ.get('DB_PASSWORD', 'astra2026secure'),
    'host': 'localhost',
    'port': '5432'
}

# Telegram config (optional)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '791589970')

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def get_open_positions():
    """Fetch all open trades from database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, asset, side, entry_price, size, alert_threshold_pct, entry_time
        FROM trades WHERE status = 'open'
    """)
    positions = cursor.fetchall()
    cursor.close()
    conn.close()
    return positions

def get_current_price(ticker_str):
    """Fetch current price from yfinance."""
    try:
        t = yf.Ticker(ticker_str)
        hist = t.history(period="1d", interval="1h")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
    except Exception as e:
        print(f"Error fetching {ticker_str}: {e}")
    return None

def calculate_pnl(entry, current, size, direction):
    """Calculate P&L in dollars."""
    if direction.upper() == 'LONG':
        return (current - entry) * size * 100  # Simplified multiplier
    else:  # SHORT
        return (entry - current) * size * 100

def send_telegram_alert(message):
    """Send alert via Telegram bot."""
    if not TELEGRAM_BOT_TOKEN:
        print(f"[TELEGRAM] Would send: {message[:80]}...")
        return
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("[TELEGRAM] Alert sent successfully")
        else:
            print(f"[TELEGRAM] Failed: {response.status_code}")
    except Exception as e:
        print(f"[TELEGRAM] Error: {e}")

def log_price_to_db(trade_id, price, pnl):
    """Log current price and P&L to market_data table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO market_data (asset, timeframe, open, high, low, close, volume, timestamp)
        VALUES ('MONITOR', '1h', %s, %s, %s, %s, 0, %s)
    """, (price, price, price, price, datetime.now()))
    
    # Update trade with current P&L
    cursor.execute("""
        UPDATE trades SET pnl = %s, updated_at = %s WHERE id = %s
    """, (pnl, datetime.now(), trade_id))
    
    conn.commit()
    cursor.close()
    conn.close()

def check_position(position):
    """Check a single position for alerts."""
    trade_id, asset, side, entry_price, size, alert_pct, entry_time = position
    
    # Map asset to ticker
    ticker_map = {
        'ES': 'ES=F', 'NQ': 'NQ=F',
        'GOLD': 'GC=F', 'SILVER': 'SI=F',
        'AUDUSD': 'AUDUSD=X', 'GBPUSD': 'GBPUSD=X',
        'SP500': '^GSPC', 'BTC': 'BTC-USD'
    }
    ticker = ticker_map.get(asset, asset)
    
    current_price = get_current_price(ticker)
    if not current_price:
        print(f"  [{asset}] Could not fetch price")
        return
    
    # Calculate move percentage
    move_pct = ((current_price - entry_price) / entry_price) * 100
    if side.upper() == 'SHORT':
        move_pct = -move_pct  # Invert for shorts
    
    pnl = calculate_pnl(entry_price, current_price, size, side)
    
    print(f"  [{asset}] Entry: {entry_price:.2f} | Current: {current_price:.2f} | Move: {move_pct:+.2f}% | P&L: ${pnl:,.2f}")
    
    # Log to database
    log_price_to_db(trade_id, current_price, pnl)
    
    # Check alert threshold
    threshold = alert_pct or 3.0  # Default 3%
    if abs(move_pct) >= threshold:
        emoji = "🚨" if move_pct < 0 else "📈"
        message = f"""{emoji} <b>ALERT: {asset} moved {move_pct:+.2f}%</b>

Position: {side.upper()} {size} lots
Entry: {entry_price:.2f}
Current: {current_price:.2f}
P&L: ${pnl:,.2f} (unrealized)

Action: {'Monitor for stop hit' if move_pct < 0 else 'Consider taking partial profits'}
"""
        send_telegram_alert(message)
        print(f"  [{asset}] ALERT TRIGGERED: {move_pct:+.2f}%")

def monitor_all():
    """Monitor all open positions."""
    print(f"\n{'='*60}")
    print(f"ASTRA POSITION MONITOR — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")
    
    positions = get_open_positions()
    
    if not positions:
        print("No open positions to monitor.")
        return
    
    print(f"Monitoring {len(positions)} open position(s):\n")
    
    for position in positions:
        check_position(position)
    
    print(f"\n{'='*60}")
    print("Monitor complete.")
    print(f"{'='*60}\n")

def main():
    parser = argparse.ArgumentParser(description='ASTRA Position Monitor')
    parser.add_argument('--all-open', action='store_true', help='Monitor all open positions')
    parser.add_argument('--asset', type=str, help='Specific asset to monitor')
    parser.add_argument('--alert-pct', type=float, default=3.0, help='Alert threshold percentage')
    
    args = parser.parse_args()
    
    if args.all_open:
        monitor_all()
    elif args.asset:
        # Single asset monitoring
        print(f"Monitoring {args.asset} with {args.alert_pct}% threshold...")
        # Would need to fetch specific trade or use current price
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
