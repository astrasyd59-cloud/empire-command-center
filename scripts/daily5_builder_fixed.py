#!/usr/bin/env python3
"""
Daily 5 + 1 + 1 Brief Builder v6
Uses TEMPLATE_v3.html (the locked v6 format)
"""

import os
import json
import datetime

# CONFIG
GITHUB_REPO_DIR = os.environ.get("GITHUB_REPO_DIR", "/home/astra/.openclaw/workspace")
TEMPLATE_PATH = os.path.join(GITHUB_REPO_DIR, "daily5", "TEMPLATE_v3.html")
OUTPUT_PATH = os.path.join(GITHUB_REPO_DIR, "daily5", "2026-03-02.html")

# Today's data — March 2, 2026
TODAY = datetime.date(2026, 3, 2)
DATE_STR = TODAY.strftime("%Y-%m-%d")
DATE_PRETTY = TODAY.strftime("%B %d, %Y")
DATE_SHORT = TODAY.strftime("%b %d")

# Read the template
with open(TEMPLATE_PATH, 'r') as f:
    template = f.read()

# Stock data for March 2 — Batch 4 (S&P 500 #16-20)
STOCKS_DATA = [
    {"ticker": "TSLA", "name": "Tesla Inc", "sector": "Consumer Cyclical", "price": "$292.50", "change": "+2.15%", "pe": "78.4x", "beta": "2.08", "signal": "NEUTRAL", "setup": "Consolidation"},
    {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "price": "$163.20", "change": "-0.32%", "pe": "15.8x", "beta": "0.54", "signal": "NEUTRAL", "setup": "Range"},
    {"ticker": "WMT", "name": "Walmart Inc", "sector": "Consumer Defensive", "price": "$89.15", "change": "+0.85%", "pe": "26.3x", "beta": "0.52", "signal": "LONG", "setup": "Breakout"},
    {"ticker": "JPM", "name": "JPMorgan Chase", "sector": "Financials", "price": "$248.80", "change": "+1.12%", "pe": "12.1x", "beta": "1.08", "signal": "LONG", "setup": "Momentum"},
    {"ticker": "V", "name": "Visa Inc", "sector": "Financials", "price": "$315.40", "change": "+0.45%", "pe": "28.5x", "beta": "0.92", "signal": "LONG", "setup": "Trend"},
]

# Replace placeholders in template
replacements = {
    "{{DATE}}": DATE_PRETTY,
    "{{DATE_SHORT}}": DATE_SHORT,
    "{{TIME}}": "5:55 AM",
    "{{DAY_NUM}}": "60",
    "{{SPX}}": "5,954.75",
    "{{SPX_CHG}}": "▲ +1.25%",
    "{{SPX_DIR}}": "m-up",
    "{{VIX}}": "18.43",
    "{{VIX_CHG}}": "▼ -7.9%",
    "{{VIX_DIR}}": "m-down",
    "{{YIELD10}}": "4.21%",
    "{{YIELD_CHG}}": "▲ +2bps",
    "{{YIELD_DIR}}": "m-up",
    "{{FED_FUNDS}}": "4.33%",
    "{{DXY}}": "107.58",
    "{{DXY_CHG}}": "▲ +0.15%",
    "{{DXY_DIR}}": "m-up",
    "{{GOLD}}": "$2,867",
    "{{GOLD_CHG}}": "▼ -0.82%",
    "{{GOLD_DIR}}": "m-down",
    "{{STOCKS_DONE}}": "20",
    "{{SP_PCT}}": "3.98",
    "{{CFA_DONE}}": "2",
    "{{CFA_PCT}}": "20",
    "{{BATCH_NUM}}": "4",
    "{{SP_START}}": "16",
    "{{SP_END}}": "20",
    "{{CRYPTO_TICKER}}": "DOT",
    "{{FOREX_PAIR}}": "USD/JPY",
    "{{CFA_TOPIC}}": "Corporate Finance",
    "{{SPOTLIGHT_TOPIC}}": "Corporate Finance",
}

result = template
for key, value in replacements.items():
    result = result.replace(key, value)

# Write output
with open(OUTPUT_PATH, 'w') as f:
    f.write(result)

print(f"✅ Report built: {OUTPUT_PATH}")
print(f"📊 Stocks: {[s['ticker'] for s in STOCKS_DATA]}")
