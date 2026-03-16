#!/usr/bin/env python3
"""
ASTRA Database Logger
Log trades, notes, and analysis to PostgreSQL
"""

import os, sys, argparse
from datetime import datetime

try:
    import psycopg2
except ImportError:
    print("Missing psycopg2. Run: pip install psycopg2-binary")
    sys.exit(1)

DB_CONFIG = {
    'dbname': 'openclaw_db',
    'user': 'astra_user',
    'password': os.environ.get('DB_PASSWORD', 'astra2026secure'),
    'host': 'localhost',
    'port': '5432'
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def log_trade(asset, direction, size, entry_price, stop_loss=None, target_1=None, 
              target_2=None, rationale=None, status='open'):
    """Log a new trade entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO trades (asset, side, entry_price, exit_price, size, pnl, 
                          entry_time, exit_time, reason, status)
        VALUES (%s, %s, %s, NULL, %s, NULL, %s, NULL, %s, %s)
        RETURNING id;
    """, (asset, direction.upper(), entry_price, size, datetime.now(), rationale, status))
    
    trade_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✓ Trade logged with ID: {trade_id}")
    return trade_id

def log_note(note_type, content, related_asset=None):
    """Log an analysis note or rationale."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO astra_notes (note_type, content, related_asset, created_at)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """, (note_type, content, related_asset, datetime.now()))
    
    note_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✓ Note logged with ID: {note_id}")
    return note_id

def close_trade(trade_id, exit_price, pnl=None):
    """Close an open trade."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Calculate P&L if not provided
    if pnl is None:
        cursor.execute("SELECT entry_price, side, size FROM trades WHERE id = %s", (trade_id,))
        row = cursor.fetchone()
        if row:
            entry, side, size = row
            if side == 'LONG':
                pnl = (exit_price - entry) * size * 100
            else:
                pnl = (entry - exit_price) * size * 100
    
    cursor.execute("""
        UPDATE trades 
        SET status = 'closed', exit_price = %s, exit_time = %s, pnl = %s
        WHERE id = %s;
    """, (exit_price, datetime.now(), pnl, trade_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✓ Trade {trade_id} closed. P&L: ${pnl:,.2f}")

def list_open_trades():
    """Display all open trades."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, asset, side, entry_price, size, entry_time, reason
        FROM trades WHERE status = 'open' ORDER BY entry_time DESC;
    """)
    
    trades = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not trades:
        print("No open trades.")
        return
    
    print(f"\n{'='*80}")
    print(f"OPEN TRADES ({len(trades)})")
    print(f"{'='*80}\n")
    
    for t in trades:
        trade_id, asset, side, entry, size, time, reason = t
        print(f"ID: {trade_id} | {asset} {side} {size} lots @ {entry}")
        print(f"   Entry time: {time}")
        print(f"   Rationale: {reason or 'N/A'}")
        print()

def main():
    parser = argparse.ArgumentParser(description='ASTRA Database Logger')
    parser.add_argument('--type', choices=['trade', 'note', 'close'], required=True,
                       help='Type of entry to log')
    
    # Trade args
    parser.add_argument('--asset', help='Asset symbol (ES, GOLD, etc.)')
    parser.add_argument('--direction', choices=['LONG', 'SHORT'], help='Trade direction')
    parser.add_argument('--size', type=float, help='Position size (lots)')
    parser.add_argument('--entry', type=float, help='Entry price')
    parser.add_argument('--stop', type=float, help='Stop loss price')
    parser.add_argument('--target1', type=float, help='Target 1 price')
    parser.add_argument('--target2', type=float, help='Target 2 price')
    parser.add_argument('--rationale', help='Trade rationale or notes')
    
    # Note args
    parser.add_argument('--note-type', default='analysis', 
                       help='Type of note (analysis, alert, review)')
    
    # Close args
    parser.add_argument('--trade-id', type=int, help='Trade ID to close')
    parser.add_argument('--exit', type=float, help='Exit price')
    parser.add_argument('--pnl', type=float, help='Realized P&L')
    
    # List
    parser.add_argument('--list-open', action='store_true', help='List all open trades')
    
    args = parser.parse_args()
    
    if args.list_open:
        list_open_trades()
        return
    
    if args.type == 'trade':
        if not all([args.asset, args.direction, args.size, args.entry]):
            print("Error: --asset, --direction, --size, and --entry are required for trades")
            sys.exit(1)
        
        log_trade(
            asset=args.asset,
            direction=args.direction,
            size=args.size,
            entry_price=args.entry,
            stop_loss=args.stop,
            target_1=args.target1,
            target_2=args.target2,
            rationale=args.rationale
        )
    
    elif args.type == 'note':
        if not args.rationale:
            print("Error: --rationale is required for notes")
            sys.exit(1)
        
        log_note(
            note_type=args.note_type,
            content=args.rationale,
            related_asset=args.asset
        )
    
    elif args.type == 'close':
        if not args.trade_id or not args.exit:
            print("Error: --trade-id and --exit are required to close a trade")
            sys.exit(1)
        
        close_trade(args.trade_id, args.exit, args.pnl)

if __name__ == "__main__":
    main()
