#!/usr/bin/env python3
"""
Daily 5 + 1 + 1 Market Data Verification Script
Fetches and cross-verifies market data from multiple sources
Date: March 2, 2026
"""

import json
import requests
import yfinance as yf
from datetime import datetime, timedelta
import time
import os

# Output file
OUTPUT_FILE = "/home/astra/.openclaw/workspace/daily5/verified_data_2026-03-02.json"

# Results container
results = {
    "report_date": "2026-03-02",
    "generated_at": datetime.now().isoformat(),
    "stocks": [],
    "crypto": [],
    "forex": [],
    "macro": []
}

def fetch_yahoo_data(symbol, asset_type="stock"):
    """Fetch data from Yahoo Finance using yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        info = ticker.info
        
        if hist.empty:
            return None
            
        latest = hist.iloc[-1]
        prev = hist.iloc[-2] if len(hist) > 1 else latest
        
        price = latest['Close']
        prev_close = prev['Close']
        change_pct = ((price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
        volume = int(latest['Volume']) if 'Volume' in latest else None
        
        return {
            "price": round(price, 4),
            "prev_close": round(prev_close, 4),
            "change_pct": round(change_pct, 4),
            "volume": volume,
            "source": "Yahoo Finance (yfinance)"
        }
    except Exception as e:
        print(f"Yahoo Finance error for {symbol}: {e}")
        return None

def fetch_coingecko_data(coin_id="polkadot"):
    """Fetch crypto data from CoinGecko API"""
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false"
        }
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if "market_data" not in data:
            return None
            
        market_data = data["market_data"]
        price = market_data["current_price"]["usd"]
        change_pct = market_data["price_change_percentage_24h"]
        
        # Calculate previous close
        prev_close = price / (1 + change_pct/100) if change_pct else price
        
        return {
            "price": round(price, 6),
            "prev_close": round(prev_close, 6),
            "change_pct": round(change_pct, 4) if change_pct else 0,
            "volume": int(market_data["total_volume"]["usd"]) if market_data.get("total_volume") else None,
            "source": "CoinGecko API"
        }
    except Exception as e:
        print(f"CoinGecko error: {e}")
        return None

def fetch_coinmarketcap_data(symbol="DOT"):
    """Fetch crypto data from CoinMarketCap API (free tier)"""
    try:
        # Using public API endpoint (no key required for basic data)
        url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail"
        params = {"slug": "polkadot"}
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code != 200:
            # Fallback to alternative public endpoint
            url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
            # Note: This requires API key, so we'll mark as pending if no key
            return None
            
        data = response.json()
        # Parse CMC response format
        return None  # Will use secondary verification from alternative source
    except Exception as e:
        print(f"CoinMarketCap error: {e}")
        return None

def fetch_alpha_vantage_stock(symbol, api_key=None):
    """Fetch stock data from Alpha Vantage"""
    try:
        if not api_key:
            return None
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": api_key
        }
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if "Global Quote" not in data or not data["Global Quote"]:
            return None
            
        quote = data["Global Quote"]
        price = float(quote["05. price"])
        change_pct = float(quote["10. change percent"].replace('%', ''))
        volume = int(quote["06. volume"])
        
        # Calculate previous close
        change = float(quote["09. change"])
        prev_close = price - change
        
        return {
            "price": round(price, 4),
            "prev_close": round(prev_close, 4),
            "change_pct": round(change_pct, 4),
            "volume": volume,
            "source": "Alpha Vantage API"
        }
    except Exception as e:
        print(f"Alpha Vantage error for {symbol}: {e}")
        return None

def fetch_alpha_vantage_forex(from_symbol="USD", to_symbol="JPY", api_key=None):
    """Fetch forex data from Alpha Vantage"""
    try:
        if not api_key:
            return None
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "CURRENCY_EXCHANGE_RATE",
            "from_currency": from_symbol,
            "to_currency": to_symbol,
            "apikey": api_key
        }
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if "Realtime Currency Exchange Rate" not in data:
            return None
            
        rate = data["Realtime Currency Exchange Rate"]
        price = float(rate["5. Exchange Rate"])
        
        return {
            "price": round(price, 4),
            "prev_close": None,  # Will need to calculate from time series
            "change_pct": None,
            "volume": None,
            "source": "Alpha Vantage API"
        }
    except Exception as e:
        print(f"Alpha Vantage forex error: {e}")
        return None

def fetch_fred_data(series_id="FEDFUNDS", api_key=None):
    """Fetch macro data from FRED API"""
    try:
        if not api_key:
            return None
        url = f"https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 2
        }
        response = requests.get(url, params=params, timeout=15)
        data = response.json()
        
        if "observations" not in data or len(data["observations"]) < 2:
            return None
            
        latest = data["observations"][0]
        prev = data["observations"][1]
        
        price = float(latest["value"])
        prev_close = float(prev["value"])
        change_pct = ((price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
        
        return {
            "price": round(price, 4),
            "prev_close": round(prev_close, 4),
            "change_pct": round(change_pct, 4),
            "volume": None,
            "source": "FRED API"
        }
    except Exception as e:
        print(f"FRED error: {e}")
        return None

def verify_data(primary, secondary, tolerance=0.02):
    """Verify data between two sources"""
    if not primary:
        return "omitted", "Primary source failed"
    
    if not secondary:
        return "pending", "Secondary source unavailable"
    
    if primary.get("price") and secondary.get("price"):
        price_diff = abs(primary["price"] - secondary["price"]) / primary["price"]
        if price_diff <= tolerance:
            return "verified", f"Price difference {price_diff*100:.2f}% within tolerance"
        else:
            return "pending", f"Price discrepancy {price_diff*100:.2f}% exceeds tolerance"
    
    return "pending", "Unable to compare prices"

def process_stock(symbol, name, alpha_key=None):
    """Process a single stock with verification"""
    print(f"Processing {symbol}...")
    
    # Primary: Yahoo Finance
    yahoo_data = fetch_yahoo_data(symbol)
    
    # Secondary: Alpha Vantage (if key available)
    alpha_data = None
    if alpha_key:
        alpha_data = fetch_alpha_vantage_stock(symbol, alpha_key)
    
    # Verify
    status, notes = verify_data(yahoo_data, alpha_data)
    
    # Build result
    result = {
        "symbol": symbol,
        "name": name,
        "asset_type": "stock"
    }
    
    if yahoo_data:
        result.update({
            "price": yahoo_data["price"],
            "change_pct": yahoo_data["change_pct"],
            "prev_close": yahoo_data["prev_close"],
            "volume": yahoo_data["volume"],
            "source_primary": yahoo_data["source"]
        })
    else:
        result.update({
            "price": None,
            "change_pct": None,
            "prev_close": None,
            "volume": None,
            "source_primary": None
        })
    
    result.update({
        "source_secondary": alpha_data["source"] if alpha_data else "Alpha Vantage (no API key or unavailable)",
        "verification_status": status,
        "notes": notes
    })
    
    return result

def process_crypto(symbol="DOT", name="Polkadot"):
    """Process crypto with verification"""
    print(f"Processing {symbol}...")
    
    # Primary: CoinGecko
    coingecko_data = fetch_coingecko_data()
    
    # Secondary: CoinMarketCap (often requires API key)
    cmc_data = fetch_coinmarketcap_data(symbol)
    
    # Also try Yahoo Finance as tertiary
    yahoo_crypto = fetch_yahoo_data("DOT-USD", "crypto")
    
    # Use Yahoo as secondary if CMC fails
    secondary = cmc_data if cmc_data else yahoo_crypto
    
    status, notes = verify_data(coingecko_data, secondary)
    
    result = {
        "symbol": symbol,
        "name": name,
        "asset_type": "crypto"
    }
    
    if coingecko_data:
        result.update({
            "price": coingecko_data["price"],
            "change_pct": coingecko_data["change_pct"],
            "prev_close": coingecko_data["prev_close"],
            "volume": coingecko_data["volume"],
            "source_primary": coingecko_data["source"]
        })
    elif yahoo_crypto:
        result.update({
            "price": yahoo_crypto["price"],
            "change_pct": yahoo_crypto["change_pct"],
            "prev_close": yahoo_crypto["prev_close"],
            "volume": yahoo_crypto["volume"],
            "source_primary": yahoo_crypto["source"]
        })
    else:
        result.update({
            "price": None,
            "change_pct": None,
            "prev_close": None,
            "volume": None,
            "source_primary": None
        })
    
    result.update({
        "source_secondary": secondary["source"] if secondary else "CoinMarketCap (unavailable)",
        "verification_status": status if coingecko_data else "pending",
        "notes": notes if coingecko_data else "Primary source failed, using Yahoo fallback" if yahoo_crypto else "All sources failed"
    })
    
    return result

def process_forex(pair="USD/JPY", alpha_key=None):
    """Process forex pair with verification"""
    print(f"Processing {pair}...")
    
    # Primary: Yahoo Finance
    yahoo_symbol = "JPY=X"  # USD/JPY on Yahoo
    yahoo_data = fetch_yahoo_data(yahoo_symbol, "forex")
    
    # Secondary: Alpha Vantage
    alpha_data = None
    if alpha_key:
        alpha_data = fetch_alpha_vantage_forex("USD", "JPY", alpha_key)
    
    status, notes = verify_data(yahoo_data, alpha_data)
    
    result = {
        "symbol": pair,
        "name": "US Dollar / Japanese Yen",
        "asset_type": "forex"
    }
    
    if yahoo_data:
        result.update({
            "price": yahoo_data["price"],
            "change_pct": yahoo_data["change_pct"],
            "prev_close": yahoo_data["prev_close"],
            "volume": yahoo_data["volume"],
            "source_primary": yahoo_data["source"]
        })
    else:
        result.update({
            "price": None,
            "change_pct": None,
            "prev_close": None,
            "volume": None,
            "source_primary": None
        })
    
    result.update({
        "source_secondary": alpha_data["source"] if alpha_data else "Alpha Vantage (no API key or unavailable)",
        "verification_status": status,
        "notes": notes
    })
    
    return result

def process_macro(symbol, name, yahoo_symbol, fred_series=None, alpha_key=None):
    """Process macro indicator"""
    print(f"Processing {symbol}...")
    
    # Primary: Yahoo Finance
    yahoo_data = fetch_yahoo_data(yahoo_symbol, "macro")
    
    # Secondary: FRED (for Fed Funds) or Alpha Vantage
    secondary_data = None
    if fred_series:
        # Try FRED
        fred_key = os.environ.get("FRED_API_KEY") or alpha_key  # May need separate key
        if fred_key:
            secondary_data = fetch_fred_data(fred_series, fred_key)
    
    status, notes = verify_data(yahoo_data, secondary_data)
    
    result = {
        "symbol": symbol,
        "name": name,
        "asset_type": "macro"
    }
    
    if yahoo_data:
        result.update({
            "price": yahoo_data["price"],
            "change_pct": yahoo_data["change_pct"],
            "prev_close": yahoo_data["prev_close"],
            "volume": yahoo_data["volume"],
            "source_primary": yahoo_data["source"]
        })
    else:
        result.update({
            "price": None,
            "change_pct": None,
            "prev_close": None,
            "volume": None,
            "source_primary": None
        })
    
    secondary_source = "None"
    if secondary_data:
        secondary_source = secondary_data["source"]
    elif fred_series:
        secondary_source = f"FRED ({fred_series}) - API unavailable"
    
    result.update({
        "source_secondary": secondary_source,
        "verification_status": status,
        "notes": notes
    })
    
    return result

def main():
    print("=" * 60)
    print("Daily 5 + 1 + 1 Market Data Verification")
    print("Date: March 2, 2026")
    print("=" * 60)
    
    # Check for API keys
    alpha_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    fred_key = os.environ.get("FRED_API_KEY")
    
    if alpha_key:
        print(f"Alpha Vantage API key: ✓ Found")
    else:
        print(f"Alpha Vantage API key: ✗ Not found (set ALPHA_VANTAGE_API_KEY)")
    
    if fred_key:
        print(f"FRED API key: ✓ Found")
    else:
        print(f"FRED API key: ✗ Not found (set FRED_API_KEY)")
    
    print("-" * 60)
    
    # Process S&P 500 Stocks
    print("\n📈 S&P 500 STOCKS")
    print("-" * 40)
    
    stocks = [
        ("TSLA", "Tesla Inc"),
        ("JNJ", "Johnson & Johnson"),
        ("WMT", "Walmart Inc"),
        ("JPM", "JPMorgan Chase & Co"),
        ("V", "Visa Inc")
    ]
    
    for symbol, name in stocks:
        stock_data = process_stock(symbol, name, alpha_key)
        results["stocks"].append(stock_data)
        time.sleep(0.5)  # Rate limiting
    
    # Process Crypto
    print("\n🪙 CRYPTOCURRENCY")
    print("-" * 40)
    
    crypto_data = process_crypto("DOT", "Polkadot")
    results["crypto"].append(crypto_data)
    time.sleep(0.5)
    
    # Process Forex
    print("\n💱 FOREX")
    print("-" * 40)
    
    forex_data = process_forex("USD/JPY", alpha_key)
    results["forex"].append(forex_data)
    time.sleep(0.5)
    
    # Process Macro
    print("\n📊 MACRO INDICATORS")
    print("-" * 40)
    
    macro_indicators = [
        ("VIX", "CBOE Volatility Index", "^VIX", None),
        ("10Y", "US 10-Year Treasury Yield", "^TNX", None),
        ("DXY", "US Dollar Index", "DX-Y.NYB", None),
        ("GOLD", "Gold Spot Price", "GC=F", None),
        ("FEDFUNDS", "Federal Funds Rate", "^IRX", "FEDFUNDS")  # Using 13-week treasury as proxy on Yahoo
    ]
    
    for symbol, name, yahoo_sym, fred_series in macro_indicators:
        # For Fed Funds, use ^IRX (13-week treasury bill) as proxy on Yahoo
        # FRED would be the authoritative source
        if symbol == "FEDFUNDS":
            macro_data = process_macro(symbol, name, "^IRX", fred_series, fred_key)
        else:
            macro_data = process_macro(symbol, name, yahoo_sym, fred_series, alpha_key)
        results["macro"].append(macro_data)
        time.sleep(0.5)
    
    # Calculate summary statistics
    all_instruments = results["stocks"] + results["crypto"] + results["forex"] + results["macro"]
    verified_count = sum(1 for i in all_instruments if i["verification_status"] == "verified")
    pending_count = sum(1 for i in all_instruments if i["verification_status"] == "pending")
    omitted_count = sum(1 for i in all_instruments if i["verification_status"] == "omitted")
    
    results["summary"] = {
        "total_instruments": len(all_instruments),
        "verified": verified_count,
        "pending": pending_count,
        "omitted": omitted_count,
        "verification_rate": f"{verified_count/len(all_instruments)*100:.1f}%"
    }
    
    # Save to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 60)
    print("DATA COLLECTION COMPLETE")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  Total instruments: {len(all_instruments)}")
    print(f"  ✓ Verified: {verified_count}")
    print(f"  ⏳ Pending: {pending_count}")
    print(f"  ✗ Omitted: {omitted_count}")
    print(f"  Verification rate: {results['summary']['verification_rate']}")
    print(f"\nOutput saved to: {OUTPUT_FILE}")
    
    # Print JSON output
    print("\n" + "=" * 60)
    print("JSON OUTPUT:")
    print("=" * 60)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
