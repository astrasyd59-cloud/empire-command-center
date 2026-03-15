#!/usr/bin/env python3
# Quick data fetch for March 1, 2026 report
import yfinance as yf
import requests
from datetime import datetime

# Fetch stocks
stocks = ["AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "^VIX", "^TNX", "DX-Y.NYB", "GC=F"]
crypto = ["cardano"]  # ADA

print("=== STOCK DATA (Yahoo Finance) ===")
for ticker in stocks:
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="5d")
        if len(hist) >= 2:
            current = hist['Close'].iloc[-1]
            prev = hist['Close'].iloc[-2]
            change = ((current - prev) / prev) * 100
            info = t.info
            print(f"{ticker}: ${current:.2f} ({change:+.2f}%) | Prev: ${prev:.2f}")
    except Exception as e:
        print(f"{ticker}: ERROR - {e}")

print("\n=== CRYPTO DATA (CoinGecko) ===")
try:
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum,cardano,solana,polkadot,chainlink",
        "vs_currencies": "usd",
        "include_24hr_change": "true"
    }
    r = requests.get(url, params=params, timeout=10)
    data = r.json()
    for coin, d in data.items():
        print(f"{coin}: ${d['usd']:,.4f} ({d.get('usd_24h_change', 0):+.2f}%)")
except Exception as e:
    print(f"Error: {e}")

print(f"\n=== Timestamp: {datetime.now().isoformat()} ===")
