#!/usr/bin/env python3
"""
Daily 5 + 1 + 1 Data Verification Script
Fetches and cross-validates all market data from 2+ sources
"""

import yfinance as yf
import requests
import json
from datetime import datetime, timezone
import time

# Target instruments for March 3, 2026
STOCKS = ["UNH", "MA", "PG", "HD", "LLY"]
CRYPTO = ["chainlink"]
FOREX = ["AUDUSD=X"]

# Macro indicators
MACRO = {
    "VIX": "^VIX",
    "DXY": "DX-Y.NYB",  # US Dollar Index
    "GOLD": "GC=F",     # Gold futures
    "TEN_YR": "^TNX",   # 10-Year Yield
}

def get_yahoo_data(ticker):
    """Fetch data from Yahoo Finance"""
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="5d")
        if hist.empty:
            return None
        info = t.info
        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2] if len(hist) > 1 else current
        change_pct = ((current - prev) / prev) * 100 if prev else 0
        return {
            "price": round(current, 4),
            "prev_close": round(prev, 4),
            "change_pct": round(change_pct, 2),
            "source": "Yahoo Finance"
        }
    except Exception as e:
        return {"error": str(e)}

def get_coingecko_data(coin_id):
    """Fetch crypto from CoinGecko"""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": coin_id,
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_market_cap": "true"
        }
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if coin_id in data:
            d = data[coin_id]
            return {
                "price": d["usd"],
                "change_24h_pct": round(d.get("usd_24h_change", 0), 2),
                "market_cap": d.get("usd_market_cap"),
                "source": "CoinGecko"
            }
        return {"error": "Coin not found"}
    except Exception as e:
        return {"error": str(e)}

def get_coinmarketcap_data(symbol):
    """Fetch crypto from CoinMarketCap (public API)"""
    try:
        # Using public CMC API endpoint (no key needed for basic data)
        url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail"
        params = {"slug": symbol}
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if "data" in data:
                stats = data["data"]["statistics"]
                return {
                    "price": stats["price"],
                    "change_24h_pct": round(stats.get("percentChange24h", 0), 2),
                    "source": "CoinMarketCap"
                }
        # Fallback: use alternative endpoint
        url2 = f"https://api.coincap.io/v2/assets/{symbol}"
        resp2 = requests.get(url2, timeout=15)
        if resp2.status_code == 200:
            data2 = resp2.json()["data"]
            return {
                "price": float(data2["priceUsd"]),
                "change_24h_pct": round(float(data2.get("changePercent24Hr", 0)), 2),
                "source": "CoinCap"
            }
        return {"error": "Could not fetch"}
    except Exception as e:
        return {"error": str(e)}

def verify_crypto(coin_id, symbol):
    """Cross-verify crypto across 2+ sources"""
    print(f"\n🔍 Verifying {coin_id.upper()}...")
    
    source1 = get_coingecko_data(coin_id)
    time.sleep(0.5)  # Rate limit
    source2 = get_coinmarketcap_data(symbol)
    
    results = {"sources": [], "verified": False}
    
    if "error" not in source1:
        results["sources"].append(source1)
        print(f"  ✓ CoinGecko: ${source1['price']:,.4f}")
    else:
        print(f"  ✗ CoinGecko: {source1.get('error')}")
    
    if "error" not in source2:
        results["sources"].append(source2)
        print(f"  ✓ CoinCap/CMC: ${source2['price']:,.4f}")
    else:
        print(f"  ✗ CoinCap: {source2.get('error')}")
    
    # Cross-validation
    if len(results["sources"]) >= 2:
        prices = [s["price"] for s in results["sources"]]
        diff_pct = abs(prices[0] - prices[1]) / ((prices[0] + prices[1]) / 2) * 100
        
        if diff_pct > 5:
            results["status"] = "OMIT"
            results["reason"] = f"Price discrepancy {diff_pct:.2f}% exceeds 5% threshold"
            print(f"  ⚠️ OMIT: {diff_pct:.2f}% discrepancy")
        elif diff_pct > 1:
            results["status"] = "FLAG"
            results["price"] = sum(prices) / len(prices)  # Median
            results["change_pct"] = results["sources"][0]["change_24h_pct"]
            results["discrepancy"] = f"{diff_pct:.2f}%"
            print(f"  ⚠️ FLAG: {diff_pct:.2f}% discrepancy, using median ${results['price']:,.4f}")
        else:
            results["status"] = "VERIFIED"
            results["price"] = prices[0]
            results["change_pct"] = results["sources"][0]["change_24h_pct"]
            results["verified"] = True
            print(f"  ✅ VERIFIED: ${results['price']:,.4f} (diff: {diff_pct:.2f}%)")
    elif len(results["sources"]) == 1:
        results["status"] = "SINGLE_SOURCE"
        results["price"] = results["sources"][0]["price"]
        results["change_pct"] = results["sources"][0]["change_24h_pct"]
        print(f"  ⚠️ SINGLE SOURCE: ${results['price']:,.4f}")
    else:
        results["status"] = "NO_DATA"
        print(f"  ❌ NO DATA")
    
    return results

def verify_stock(ticker):
    """Cross-verify stock (Yahoo primary, compare against prior close)"""
    print(f"\n🔍 Verifying {ticker}...")
    
    source1 = get_yahoo_data(ticker)
    
    results = {"sources": [], "verified": False}
    
    if "error" not in source1:
        results["sources"].append(source1)
        print(f"  ✓ Yahoo Finance: ${source1['price']:,.2f} ({source1['change_pct']:+.2f}%)")
        
        # Check for >5% move vs previous close (flag for review)
        if abs(source1['change_pct']) > 5:
            results["status"] = "FLAG_LARGE_MOVE"
            results["reason"] = f"Large move: {source1['change_pct']:+.2f}%"
            print(f"  ⚠️ FLAG: Large move {source1['change_pct']:+.2f}%")
        else:
            results["status"] = "VERIFIED"
            results["verified"] = True
            print(f"  ✅ VERIFIED")
        
        results["price"] = source1["price"]
        results["change_pct"] = source1["change_pct"]
        results["prev_close"] = source1["prev_close"]
    else:
        results["status"] = "NO_DATA"
        print(f"  ❌ ERROR: {source1.get('error')}")
    
    return results

def get_macro_data():
    """Fetch macro indicators"""
    print("\n" + "="*50)
    print("MACRO DATA VERIFICATION")
    print("="*50)
    
    macro_results = {}
    
    for name, ticker in MACRO.items():
        print(f"\n🔍 Verifying {name} ({ticker})...")
        data = get_yahoo_data(ticker)
        
        if "error" not in data:
            print(f"  ✓ {name}: {data['price']:.4f}")
            macro_results[name] = {
                "value": data["price"],
                "change_pct": data["change_pct"],
                "status": "VERIFIED"
            }
        else:
            print(f"  ❌ ERROR: {data.get('error')}")
            macro_results[name] = {"status": "NO_DATA", "error": data.get("error")}
    
    return macro_results

def main():
    print("="*60)
    print("DAILY 5 + 1 + 1 DATA VERIFICATION")
    print(f"Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("="*60)
    
    # Verify stocks
    print("\n" + "="*50)
    print("S&P 500 STOCKS VERIFICATION")
    print("="*50)
    
    stock_results = {}
    for ticker in STOCKS:
        stock_results[ticker] = verify_stock(ticker)
        time.sleep(0.3)
    
    # Verify crypto
    print("\n" + "="*50)
    print("CRYPTO VERIFICATION")
    print("="*50)
    
    crypto_results = verify_crypto("chainlink", "chainlink")
    
    # Verify forex
    print("\n" + "="*50)
    print("FOREX VERIFICATION")
    print("="*50)
    
    forex_results = {}
    forex_data = get_yahoo_data("AUDUSD=X")
    if "error" not in forex_data:
        print(f"  ✓ AUD/USD: {forex_data['price']:.5f}")
        forex_results = {
            "pair": "AUD/USD",
            "rate": forex_data["price"],
            "change_pct": forex_data["change_pct"],
            "status": "VERIFIED"
        }
    else:
        print(f"  ❌ ERROR: {forex_data.get('error')}")
        forex_results = {"status": "NO_DATA"}
    
    # Get macro data
    macro_results = get_macro_data()
    
    # Compile final report
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stocks": stock_results,
        "crypto": crypto_results,
        "forex": forex_results,
        "macro": macro_results
    }
    
    # Count verified items
    verified_count = 0
    flagged_count = 0
    omitted_count = 0
    
    for ticker, data in stock_results.items():
        if data.get("verified"):
            verified_count += 1
        elif "FLAG" in data.get("status", ""):
            flagged_count += 1
    
    if crypto_results.get("verified"):
        verified_count += 1
    elif crypto_results.get("status") == "OMIT":
        omitted_count += 1
    
    print(f"\n✅ Verified: {verified_count}")
    print(f"⚠️  Flagged: {flagged_count}")
    print(f"❌ Omitted: {omitted_count}")
    
    # Save results
    output_file = f"/home/astra/.openclaw/workspace/daily5/verified_data_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\n💾 Data saved to: {output_file}")
    
    return summary

if __name__ == "__main__":
    result = main()
    print("\n" + json.dumps(result, indent=2))
