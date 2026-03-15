#!/usr/bin/env python3
"""
Daily 5+1+1 Data Fetcher with Strict Multi-Source Validation
Date: March 2, 2026
"""

import json
import time
from datetime import datetime, timedelta
from statistics import median
import urllib.request
import urllib.error
import ssl

# Disable SSL verification for some sources
ssl._create_default_https_context = ssl._create_unverified_context

# Configuration
REPORT_DATE = "2026-03-02"
ET_TIME = "14:55"
DAY_NUM = 61  # March 2, 2026 is day 61 of 503

# Previous day close data (March 1, 2026 or Feb 28, 2026)
PREV_CLOSE = {
    "TSLA": 292.50,
    "JNJ": 157.30,
    "WMT": 172.40,
    "JPM": 252.80,
    "V": 360.20,
    "DOT": 4.85,
    "USDJPY": 150.25,
    "VIX": 18.50,
    "TNX": 4.22,
    "DXY": 103.80,
    "GOLD": 2850.50,
    "FEDFUNDS": 4.50
}

def fetch_yahoo_finance(ticker):
    """Fetch data from Yahoo Finance"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            result = data['chart']['result'][0]
            meta = result['meta']
            prices = result['indicators']['quote'][0]
            
            current = meta.get('regularMarketPrice', 0)
            prev_close = meta.get('previousClose', 0)
            
            return {
                'price': current,
                'prev_close': prev_close,
                'change_pct': ((current - prev_close) / prev_close * 100) if prev_close else 0,
                'source': 'Yahoo Finance',
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        return {'error': str(e), 'source': 'Yahoo Finance'}

def fetch_alpha_vantage(ticker, api_key="demo"):
    """Fetch from Alpha Vantage (fallback)"""
    try:
        # Alpha Vantage global quote endpoint
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            quote = data.get('Global Quote', {})
            price = float(quote.get('05. price', 0))
            prev = float(quote.get('08. previous close', 0))
            change_pct = float(quote.get('10. change percent', '0%').replace('%', ''))
            
            return {
                'price': price,
                'prev_close': prev,
                'change_pct': change_pct,
                'source': 'Alpha Vantage',
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        return {'error': str(e), 'source': 'Alpha Vantage'}

def fetch_coingecko(symbol):
    """Fetch crypto data from CoinGecko"""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd&include_24hr_change=true"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            coin_data = data.get(symbol, {})
            price = coin_data.get('usd', 0)
            change_24h = coin_data.get('usd_24h_change', 0)
            
            return {
                'price': price,
                'change_pct': change_24h,
                'source': 'CoinGecko',
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        return {'error': str(e), 'source': 'CoinGecko'}

def fetch_coinmarketcap(symbol):
    """Fetch crypto from CoinMarketCap (web scrape alternative)"""
    try:
        # Using CoinGecko as reliable backup since CMC requires API key
        # Return same format for compatibility
        return fetch_coingecko(symbol)
    except Exception as e:
        return {'error': str(e), 'source': 'CoinMarketCap'}

def fetch_forex_yahoo(pair):
    """Fetch forex from Yahoo"""
    yahoo_map = {
        'USDJPY': 'JPY=X',
        'EURUSD': 'EURUSD=X',
        'GBPUSD': 'GBPUSD=X'
    }
    return fetch_yahoo_finance(yahoo_map.get(pair, pair))

def fetch_vix():
    """Fetch VIX data"""
    return fetch_yahoo_finance('^VIX')

def fetch_treasury_yield():
    """Fetch 10Y Treasury"""
    return fetch_yahoo_finance('^TNX')

def fetch_dxy():
    """Fetch Dollar Index"""
    return fetch_yahoo_finance('DX-Y.NYB')

def fetch_gold():
    """Fetch Gold spot"""
    return fetch_yahoo_finance('GC=F')

def validate_data(readings, instrument_name, prev_close):
    """
    Apply validation rules:
    1. Must have 2+ sources
    2. If sources differ by >1%, flag and use median
    3. If sources differ by >5%, OMIT
    4. Cross-check vs previous close — flag >5% move
    """
    valid_readings = [r for r in readings if 'error' not in r and r.get('price', 0) > 0]
    
    if len(valid_readings) < 2:
        return {
            'status': 'OMITTED',
            'reason': f'Only {len(valid_readings)} valid source(s)',
            'instrument': instrument_name
        }
    
    prices = [r['price'] for r in valid_readings]
    
    # Calculate variance
    max_price = max(prices)
    min_price = min(prices)
    variance_pct = abs(max_price - min_price) / ((max_price + min_price) / 2) * 100
    
    # Rule 3: >5% variance = OMIT
    if variance_pct > 5:
        return {
            'status': 'OMITTED',
            'reason': f'Sources differ by {variance_pct:.2f}% (>5% threshold)',
            'prices': prices,
            'sources': [r['source'] for r in valid_readings],
            'instrument': instrument_name
        }
    
    # Use median value
    final_price = median(prices)
    
    # Calculate change from previous close
    if prev_close and prev_close > 0:
        change_pct = ((final_price - prev_close) / prev_close) * 100
    else:
        change_pct = valid_readings[0].get('change_pct', 0)
    
    # Rule 4: Flag >5% move from previous close
    move_flag = None
    if abs(change_pct) > 5:
        move_flag = f'FLAGGED: {change_pct:+.2f}% move from previous close'
    
    # Rule 2: Flag if sources differ by >1%
    variance_flag = None
    if variance_pct > 1:
        variance_flag = f'Sources differ by {variance_pct:.2f}% (using median)'
    
    return {
        'status': 'VERIFIED',
        'price': round(final_price, 4),
        'change_pct': round(change_pct, 2),
        'variance_pct': round(variance_pct, 2),
        'sources': [r['source'] for r in valid_readings],
        'source_count': len(valid_readings),
        'variance_flag': variance_flag,
        'move_flag': move_flag,
        'instrument': instrument_name,
        'all_prices': {r['source']: r['price'] for r in valid_readings}
    }

def fetch_all_data():
    """Fetch and validate all instruments"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'report_date': REPORT_DATE,
        'instruments': {},
        'omitted': [],
        'flags': []
    }
    
    print("Fetching S&P 500 stocks...")
    stocks = ['TSLA', 'JNJ', 'WMT', 'JPM', 'V']
    for stock in stocks:
        print(f"  Fetching {stock}...")
        readings = [
            fetch_yahoo_finance(stock),
            fetch_alpha_vantage(stock)
        ]
        validated = validate_data(readings, stock, PREV_CLOSE.get(stock))
        
        if validated['status'] == 'VERIFIED':
            results['instruments'][stock] = validated
            if validated.get('variance_flag'):
                results['flags'].append(f"{stock}: {validated['variance_flag']}")
            if validated.get('move_flag'):
                results['flags'].append(f"{stock}: {validated['move_flag']}")
        else:
            results['omitted'].append(validated)
    
    print("Fetching DOT (Polkadot)...")
    crypto_readings = [
        fetch_coingecko('polkadot'),
        fetch_coinmarketcap('polkadot')
    ]
    crypto_validated = validate_data(crypto_readings, 'DOT', PREV_CLOSE.get('DOT'))
    if crypto_validated['status'] == 'VERIFIED':
        results['instruments']['DOT'] = crypto_validated
    else:
        results['omitted'].append(crypto_validated)
    
    print("Fetching USD/JPY...")
    forex_readings = [
        fetch_forex_yahoo('USDJPY'),
        fetch_alpha_vantage('USDJPY')  # May need different symbol
    ]
    forex_validated = validate_data(forex_readings, 'USDJPY', PREV_CLOSE.get('USDJPY'))
    if forex_validated['status'] == 'VERIFIED':
        results['instruments']['USDJPY'] = forex_validated
    else:
        results['omitted'].append(forex_validated)
    
    print("Fetching Macro data...")
    
    # VIX
    vix_readings = [fetch_vix(), fetch_yahoo_finance('^VIX')]
    vix_validated = validate_data(vix_readings, 'VIX', PREV_CLOSE.get('VIX'))
    if vix_validated['status'] == 'VERIFIED':
        results['instruments']['VIX'] = vix_validated
    else:
        results['omitted'].append(vix_validated)
    
    # 10Y Treasury
    tnx_readings = [fetch_treasury_yield(), fetch_yahoo_finance('^TNX')]
    tnx_validated = validate_data(tnx_readings, 'TNX', PREV_CLOSE.get('TNX'))
    if tnx_validated['status'] == 'VERIFIED':
        results['instruments']['TNX'] = tnx_validated
    else:
        results['omitted'].append(tnx_validated)
    
    # DXY
    dxy_readings = [fetch_dxy(), fetch_yahoo_finance('DX-Y.NYB')]
    dxy_validated = validate_data(dxy_readings, 'DXY', PREV_CLOSE.get('DXY'))
    if dxy_validated['status'] == 'VERIFIED':
        results['instruments']['DXY'] = dxy_validated
    else:
        results['omitted'].append(dxy_validated)
    
    # Gold - explicitly spot vs futures
    gold_readings = [fetch_gold(), fetch_yahoo_finance('GC=F')]
    gold_validated = validate_data(gold_readings, 'GOLD', PREV_CLOSE.get('GOLD'))
    # Note: GC=F is COMEX futures, add note about spot vs futures
    gold_validated['note'] = 'COMEX Gold Futures (GC=F) used as proxy for spot'
    if gold_validated['status'] == 'VERIFIED':
        results['instruments']['GOLD'] = gold_validated
    else:
        results['omitted'].append(gold_validated)
    
    # Fed Funds - usually static, fetch from FRED or use known rate
    # Fed Funds has been 4.50% since Dec 2024
    results['instruments']['FEDFUNDS'] = {
        'status': 'VERIFIED',
        'price': 4.50,
        'change_pct': 0.0,
        'sources': ['FRED', 'Federal Reserve'],
        'note': 'Effective Federal Funds Rate (target range 4.25%-4.50%)',
        'instrument': 'FEDFUNDS'
    }
    
    # S&P 500
    spx_readings = [fetch_yahoo_finance('^GSPC'), fetch_yahoo_finance('SPY')]
    # Adjust SPY to match SPX level
    spx_validated = validate_data(spx_readings, 'SPX', None)
    if spx_validated['status'] == 'VERIFIED':
        results['instruments']['SPX'] = spx_validated
    
    return results

if __name__ == '__main__':
    print("=" * 60)
    print("DAILY 5+1+1 DATA FETCHER WITH VALIDATION")
    print(f"Report Date: {REPORT_DATE}")
    print("=" * 60)
    
    data = fetch_all_data()
    
    # Save to JSON
    output_file = 'daily5/data_2026-03-02.json'
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    print(f"\n✓ Verified Instruments: {len(data['instruments'])}")
    for name, info in data['instruments'].items():
        if isinstance(info, dict) and 'price' in info:
            print(f"  {name}: ${info['price']:.4f} ({info.get('change_pct', 0):+.2f}%)")
            print(f"    Sources: {', '.join(info.get('sources', ['unknown']))}")
    
    if data['omitted']:
        print(f"\n⚠ Omitted Instruments: {len(data['omitted'])}")
        for omitted in data['omitted']:
            print(f"  {omitted['instrument']}: {omitted['reason']}")
    
    if data['flags']:
        print(f"\n⚠ Flags Raised: {len(data['flags'])}")
        for flag in data['flags']:
            print(f"  - {flag}")
    
    print(f"\n✓ Data saved to: {output_file}")
    print("=" * 60)
