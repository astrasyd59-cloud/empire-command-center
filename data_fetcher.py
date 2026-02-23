# data_fetcher.py - Market Data Module for ASTRA
# Fetches fresh price data for Daily 5 + 1 Crypto reports
# Sources: yfinance (stocks), CoinGecko (crypto), Alpaca (intraday)

import yfinance as yf
import requests
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class MarketDataFetcher:
    """
    Unified market data fetcher for ASTRA reports.
    
    Usage:
        fetcher = MarketDataFetcher()
        
        # Daily report data
        stocks = fetcher.get_daily_stocks(["AAPL", "JPM", "XOM", "UNH"])
        crypto = fetcher.get_crypto_price(["bitcoin"])
        
        # Intraday for ad-hoc analysis
        intraday = fetcher.get_intraday("SPY", minutes=60)
    """
    
    def __init__(self, alpaca_key: Optional[str] = None, alpaca_secret: Optional[str] = None):
        """
        Initialize fetcher with optional API keys.
        
        Args:
            alpaca_key: Alpaca API key (optional, for intraday data)
            alpaca_secret: Alpaca API secret (optional)
        """
        self.alpaca_key = alpaca_key or os.getenv("ALPACA_API_KEY")
        self.alpaca_secret = alpaca_secret or os.getenv("ALPACA_API_SECRET")
        self.session = requests.Session()
        
    def get_daily_stocks(self, tickers: List[str]) -> Dict[str, dict]:
        """
        Fetch daily closing prices and key metrics for stocks.
        Uses yfinance (free, no API key needed).
        
        Args:
            tickers: List of stock symbols (e.g., ["AAPL", "JPM"])
            
        Returns:
            Dict with price, change%, market cap, etc.
            
        Example:
            {
                "AAPL": {
                    "price": 264.58,
                    "change_pct": 2.59,
                    "prev_close": 257.83,
                    "market_cap": "3.89T",
                    "pe_ratio": 33.45,
                    "dividend_yield": 0.39,
                    "beta": 1.11,
                    "eps": 7.91,
                    "roe": 160.1
                }
            }
        """
        results = {}
        
        try:
            # Download data for all tickers at once
            data = yf.download(tickers, period="5d", auto_adjust=True, progress=False)
            
            # Get info for each ticker
            for ticker in tickers:
                try:
                    ticker_obj = yf.Ticker(ticker)
                    info = ticker_obj.info
                    hist = data['Close'][ticker] if len(tickers) > 1 else data['Close']
                    
                    current_price = hist.iloc[-1]
                    prev_close = hist.iloc[-2] if len(hist) > 1 else current_price
                    change_pct = ((current_price - prev_close) / prev_close) * 100
                    
                    results[ticker] = {
                        "price": round(current_price, 2),
                        "change_pct": round(change_pct, 2),
                        "prev_close": round(prev_close, 2),
                        "market_cap": self._format_market_cap(info.get("marketCap")),
                        "pe_ratio": round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else None,
                        "dividend_yield": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else 0,
                        "beta": round(info.get("beta", 0), 2) if info.get("beta") else None,
                        "eps": round(info.get("trailingEps", 0), 2) if info.get("trailingEps") else None,
                        "roe": round(info.get("returnOnEquity", 0) * 100, 1) if info.get("returnOnEquity") else None,
                        "timestamp": datetime.now().isoformat()
                    }
                except Exception as e:
                    results[ticker] = {"error": str(e)}
                    
        except Exception as e:
            return {"error": f"Failed to fetch stock data: {str(e)}"}
            
        return results
    
    def get_crypto_price(self, coins: List[str]) -> Dict[str, dict]:
        """
        Fetch current crypto prices from CoinGecko.
        Free tier: 30 calls/min, no API key needed.
        
        Args:
            coins: List of CoinGecko coin IDs (e.g., ["bitcoin", "ethereum"])
            
        Returns:
            Dict with price, 24h change, market cap
            
        Example:
            {
                "bitcoin": {
                    "price": 96420,
                    "change_24h_pct": -8.45,
                    "market_cap": 1910000000000,
                    "volume_24h": 28400000000
                }
            }
        """
        try:
            ids = ",".join(coins)
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": ids,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_market_cap": "true",
                "include_24hr_vol": "true"
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = {}
            for coin in coins:
                if coin in data:
                    coin_data = data[coin]
                    results[coin] = {
                        "price": coin_data["usd"],
                        "change_24h_pct": round(coin_data.get("usd_24h_change", 0), 2),
                        "market_cap": coin_data.get("usd_market_cap"),
                        "volume_24h": coin_data.get("usd_24h_vol"),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    results[coin] = {"error": "Coin not found"}
                    
            return results
            
        except Exception as e:
            return {"error": f"Failed to fetch crypto data: {str(e)}"}
    
    def get_intraday(self, symbol: str, minutes: int = 60) -> Dict:
        """
        Fetch intraday price data for ad-hoc analysis.
        Uses Alpaca if API keys available, otherwise falls back to yfinance.
        
        Args:
            symbol: Stock symbol (e.g., "SPY", "AAPL")
            minutes: How many minutes of data (default 60)
            
        Returns:
            Dict with OHLCV data for the period
        """
        # Try Alpaca first if keys available
        if self.alpaca_key and self.alpaca_secret:
            try:
                return self._get_alpaca_intraday(symbol, minutes)
            except:
                pass  # Fall back to yfinance
        
        # Fallback to yfinance (15-min delayed, but free)
        return self._get_yfinance_intraday(symbol, minutes)
    
    def _get_alpaca_intraday(self, symbol: str, minutes: int) -> Dict:
        """Fetch intraday data from Alpaca Markets."""
        from alpaca_trade_api.rest import REST
        
        api = REST(self.alpaca_key, self.alpaca_secret, base_url='https://data.alpaca.markets')
        
        # Calculate number of 5-min bars needed
        limit = max(minutes // 5, 1)
        
        bars = api.get_bars(symbol, "5Min", limit=limit).df
        
        return {
            "symbol": symbol,
            "interval": "5min",
            "data": bars.to_dict('records'),
            "source": "alpaca",
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_yfinance_intraday(self, symbol: str, minutes: int) -> Dict:
        """Fetch intraday data from yfinance (fallback)."""
        ticker = yf.Ticker(symbol)
        
        # yfinance provides 1-hour data for recent periods
        hist = ticker.history(period="1d", interval="15m")
        
        # Take last N bars to match requested minutes
        bars_needed = max(minutes // 15, 1)
        recent = hist.tail(bars_needed)
        
        return {
            "symbol": symbol,
            "interval": "15min",
            "data": recent.to_dict('records'),
            "source": "yfinance",
            "note": "15-min delayed data",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_hyperliquid_data(self, coin: str = "BTC") -> Dict:
        """
        Fetch market data from Hyperliquid API.
        Good for crypto derivatives data.
        
        Args:
            coin: Crypto symbol (e.g., "BTC", "ETH")
            
        Returns:
            Dict with mark price, funding, open interest
        """
        try:
            url = "https://api.hyperliquid.xyz/info"
            payload = {"type": "metaAndAssetCtxs"}
            
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Parse asset contexts to find our coin
            for asset in data.get("assetCtxs", []):
                if asset.get("coin") == coin:
                    return {
                        "coin": coin,
                        "mark_price": float(asset.get("markPx", 0)),
                        "funding_rate": float(asset.get("funding", 0)),
                        "open_interest": float(asset.get("openInterest", 0)),
                        "volume_24h": float(asset.get("dayNtlVlm", 0)),
                        "source": "hyperliquid",
                        "timestamp": datetime.now().isoformat()
                    }
            
            return {"error": f"Coin {coin} not found on Hyperliquid"}
            
        except Exception as e:
            return {"error": f"Failed to fetch Hyperliquid data: {str(e)}"}
    
    def get_daily_5_plus_1(self) -> Dict:
        """
        Fetch complete data for Daily 5 + 1 Crypto report.
        
        Returns:
            Dict with 4 stocks + 1 crypto, formatted for report generation
        """
        # Default stocks for Daily 5 (rotates daily, this is example)
        stocks = ["AAPL", "JPM", "XOM", "UNH"]
        crypto = ["bitcoin"]
        
        stock_data = self.get_daily_stocks(stocks)
        crypto_data = self.get_crypto_price(crypto)
        
        return {
            "stocks": stock_data,
            "crypto": crypto_data,
            "generated_at": datetime.now().isoformat(),
            "data_source": "yfinance + coingecko"
        }
    
    def _format_market_cap(self, market_cap: Optional[int]) -> str:
        """Format market cap in trillions/billions/millions."""
        if not market_cap:
            return "N/A"
        
        if market_cap >= 1e12:
            return f"{market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            return f"{market_cap/1e9:.2f}B"
        elif market_cap >= 1e6:
            return f"{market_cap/1e6:.2f}M"
        else:
            return str(market_cap)


# Quick test function
def test_fetcher():
    """Test the data fetcher."""
    print("Testing MarketDataFetcher...")
    
    fetcher = MarketDataFetcher()
    
    # Test stocks
    print("\n1. Fetching stock data...")
    stocks = fetcher.get_daily_stocks(["AAPL", "JPM"])
    for ticker, data in stocks.items():
        if "error" not in data:
            print(f"  {ticker}: ${data['price']} ({data['change_pct']}%)")
        else:
            print(f"  {ticker}: ERROR - {data['error']}")
    
    # Test crypto
    print("\n2. Fetching crypto data...")
    crypto = fetcher.get_crypto_price(["bitcoin"])
    for coin, data in crypto.items():
        if "error" not in data:
            print(f"  {coin}: ${data['price']:,.0f} ({data['change_24h_pct']}%)")
        else:
            print(f"  {coin}: ERROR - {data['error']}")
    
    print("\n✅ Test complete!")


if __name__ == "__main__":
    test_fetcher()
