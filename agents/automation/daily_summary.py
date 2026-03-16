#!/usr/bin/env python3
"""
DAILY SUMMARY SCRIPT - Sends daily bot usage stats at 21:00
Run via cron: 0 21 * * * cd /home/astra/.openclaw/workspace && python3 agents/automation/daily_summary.py
"""
import os
import sys
import sqlite3
import requests
from datetime import datetime, timedelta

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENCLAW_WORKSPACE = os.getenv("OPENCLAW_WORKSPACE", "/home/astra/.openclaw/workspace")
STATS_DB = os.path.join(OPENCLAW_WORKSPACE, "agents/automation/bot_stats.db")

# Get the admin chat ID from environment or use a default
# User should set TELEGRAM_ADMIN_CHAT_ID in .env
ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_CHAT_ID")

def get_daily_stats(date_str):
    """Get stats for a specific date"""
    try:
        conn = sqlite3.connect(STATS_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                links_received, links_success, links_failed,
                pdfs_received, pdfs_success, pdfs_failed,
                voice_notes, text_messages
            FROM daily_stats 
            WHERE date = ?
        ''', (date_str,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'links_received': row[0],
                'links_success': row[1],
                'links_failed': row[2],
                'pdfs_received': row[3],
                'pdfs_success': row[4],
                'pdfs_failed': row[5],
                'voice_notes': row[6],
                'text_messages': row[7]
            }
        return None
        
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return None

def get_recent_errors(date_str, limit=5):
    """Get recent errors for the day"""
    try:
        conn = sqlite3.connect(STATS_DB)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT event_type, timestamp, error_message
            FROM events
            WHERE date(timestamp) = ? AND status = 'failed'
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (date_str, limit))
        
        errors = cursor.fetchall()
        conn.close()
        return errors
        
    except Exception as e:
        print(f"Error fetching errors: {e}")
        return []

def format_daily_summary(date_str, stats, errors):
    """Format the daily summary message"""
    if not stats:
        return f"📊 **Daily Summary for {date_str}**\n\nNo activity recorded today."
    
    # Calculate success rates
    link_rate = (stats['links_success'] / stats['links_received'] * 100) if stats['links_received'] > 0 else 0
    pdf_rate = (stats['pdfs_success'] / stats['pdfs_received'] * 100) if stats['pdfs_received'] > 0 else 0
    
    # Total items processed
    total_items = stats['links_received'] + stats['pdfs_received'] + stats['voice_notes'] + stats['text_messages']
    total_success = stats['links_success'] + stats['pdfs_success']
    total_failed = stats['links_failed'] + stats['pdfs_failed']
    
    message = f"""📊 **DAILY SUMMARY** — {date_str}

**📥 Items Received: {total_items}**

🔗 **Links:** {stats['links_received']}
   ✅ Success: {stats['links_success']} ({link_rate:.0f}%)
   ❌ Failed: {stats['links_failed']}

📄 **PDFs:** {stats['pdfs_received']}
   ✅ Success: {stats['pdfs_success']} ({pdf_rate:.0f}%)
   ❌ Failed: {stats['pdfs_failed']}

🎤 **Voice Notes:** {stats['voice_notes']}
📝 **Text Messages:** {stats['text_messages']}

**📈 Overall:** {total_success} successful / {total_failed} failed"""
    
    # Add recent errors if any
    if errors:
        message += "\n\n**⚠️ Recent Errors:**\n"
        for event_type, timestamp, error_msg in errors[:3]:
            time_only = timestamp.split('T')[1][:5] if 'T' in timestamp else timestamp
            error_short = error_msg[:60] if error_msg else "Unknown error"
            message += f"• {event_type.upper()} at {time_only}: `{error_short}...`\n"
    
    message += "\n_This is your 21:00 daily report from Astra."
    
    return message

def send_telegram_message(chat_id, message):
    """Send message via Telegram bot"""
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        return False
    
    if not chat_id:
        print("Error: No chat_id provided. Set TELEGRAM_ADMIN_CHAT_ID in .env")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ Daily summary sent to {chat_id}")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

def main():
    print("=" * 60)
    print("📊 DAILY SUMMARY SCRIPT")
    print("=" * 60)
    
    # Get yesterday's date (since this runs at 21:00, we report on today)
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\n📅 Date: {today}")
    print(f"💾 Database: {STATS_DB}")
    
    # Check if database exists
    if not os.path.exists(STATS_DB):
        print(f"⚠️ Stats database not found at {STATS_DB}")
        print("   Run the telegram bot first to initialize the database.")
        sys.exit(1)
    
    # Get stats
    stats = get_daily_stats(today)
    errors = get_recent_errors(today)
    
    # Format message
    message = format_daily_summary(today, stats, errors)
    
    print(f"\n📤 Sending summary...")
    
    # Send to Telegram
    if ADMIN_CHAT_ID:
        success = send_telegram_message(ADMIN_CHAT_ID, message)
    else:
        print("⚠️ TELEGRAM_ADMIN_CHAT_ID not set")
        print("   Set this in your .env file to receive daily summaries.")
        print("\n📋 Summary that would be sent:")
        print("-" * 40)
        print(message)
        print("-" * 40)
        success = False
    
    print("\n" + "=" * 60)
    print("✅ Done")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
