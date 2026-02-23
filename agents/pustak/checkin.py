#!/usr/bin/env python3
"""Pustak daily reading check-in"""
import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8502489875:AAGsXYXpn2O31knH9bGjFpuicZSoN6U6T1g')
CHAT_ID = '791589970'

message = """📚 **READING CHECK-IN**

Did you hit 10 pages today?

Reply:
• ✅ Yes — How many pages? What book?
• ❌ No — What happened? Tomorrow we restart.

Streak counting starts now."""

try:
    requests.post(
        f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
        json={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'Markdown'},
        timeout=10
    )
    print("Check-in sent")
except Exception as e:
    print(f"Error: {e}")
