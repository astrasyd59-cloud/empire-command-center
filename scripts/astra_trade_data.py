#!/usr/bin/env python3
"""
ASTRA — Weekly Trade Idea Data Fetcher
Instruments: Gold, Silver, ES, NQ, AUDUSD, GBPUSD
Timeframe: 4H (swing trade, weekly report)
Run: Every Sunday ~8 PM AEST (10 AM UTC)
Output: /home/astra/data/weekly_trade_data.json
"""

import yfinance as yf
import pandas as pd
import numpy as np
import json
import requests
import os
from datetime import datetime, timedelta
from pathlib import Path

# ── Output directory ─────────────────────────────────────────────
OUTPUT_DIR = Path("/home/astra/.openclaw/workspace/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "weekly_trade_data.json"
LOG_FILE = OUTPUT_DIR / "fetch_log.txt"

# ── Instruments ──────────────────────────────────────────────────
INSTRUMENTS = {
    "GOLD": {"ticker": "GC=F", "name": "Gold Futures", "category": "commodity", "cmc_symbol": "GOLD"},
    "SILVER": {"ticker": "SI=F", "name": "Silver Futures", "category": "commodity", "cmc_symbol": "SILVER"},
    "ES": {"ticker": "ES=F", "name": "S&P 500 E-mini", "category": "index", "cmc_symbol": "US500"},
    "NQ": {"ticker": "NQ=F", "name": "Nasdaq 100 E-mini", "category": "index", "cmc_symbol": "US100"},
    "AUDUSD": {"ticker": "AUDUSD=X", "name": "Australian Dollar/USD", "category": "forex", "cmc_symbol": "AUDUSD"},
    "GBPUSD": {"ticker": "GBPUSD=X", "name": "British Pound/USD", "category": "forex", "cmc_symbol": "GBPUSD"},
}

MACRO = {
    "VIX": "^VIX",
    "DXY": "DX-Y.NYB",
    "YIELD_10Y": "^TNX",
    "YIELD_2Y": "^IRX",
    "SP500": "^GSPC",
}

def log(msg):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# ── Indicator Calculations ────────────────────────────────────────
def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def atr(high, low, close, period=14):
    h_l = high - low
    h_pc = (high - close.shift(1)).abs()
    l_pc = (low - close.shift(1)).abs()
    tr = pd.concat([h_l, h_pc, l_pc], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()

def rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(window=period).mean()
    loss = (-delta.clip(upper=0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def detect_pattern(df_4h, df_daily):
    """Simple rule-based pattern detection on 4H chart."""
    if df_4h is None or len(df_4h) < 30:
        return {"name": "No Pattern", "murphy_chapter": "N/A", "bias": "neutral", "description": "Insufficient data"}
    
    close = df_4h["Close"]
    high = df_4h["High"]
    low = df_4h["Low"]
    recent = close.iloc[-20:]
    ema20 = ema(close, 20).iloc[-1]
    ema50 = ema(close, 50).iloc[-1]
    current_close = close.iloc[-1]
    current_atr = atr(high, low, close, 14).iloc[-1]
    
    rolling_high_10 = high.iloc[-10:].max()
    rolling_low_10 = low.iloc[-10:].min()
    rolling_high_20 = high.iloc[-20:].max()
    rolling_low_20 = low.iloc[-20:].min()
    rolling_high_5 = high.iloc[-5:].max()
    rolling_low_5 = low.iloc[-5:].min()
    
    trend_up = current_close > ema20 > ema50
    trend_down = current_close < ema20 < ema50
    
    # ── Bull Flag ──
    prior_range = high.iloc[-20:-5].max() - low.iloc[-20:-5].min()
    recent_range = rolling_high_5 - rolling_low_5
    strong_move = close.iloc[-15] > close.iloc[-20] * 1.015
    tight_consol = recent_range < prior_range * 0.4
    
    if trend_up and strong_move and tight_consol:
        return {
            "name": "Bull Flag",
            "murphy_chapter": "Chapter 6 — Continuation Patterns",
            "bias": "bullish",
            "description": "Strong impulse rally followed by tight, low-volume consolidation. Breakout above flag high targets the flagpole length projected upward."
        }
    
    # ── Bear Flag ──
    strong_down = close.iloc[-15] < close.iloc[-20] * 0.985
    if trend_down and strong_down and tight_consol:
        return {
            "name": "Bear Flag",
            "murphy_chapter": "Chapter 6 — Continuation Patterns",
            "bias": "bearish",
            "description": "Sharp decline followed by tight, low-volume bounce. Breakdown below flag low targets the flagpole length projected downward."
        }
    
    # ── Breakout from Resistance ──
    prior_resistance = high.iloc[-30:-5].max()
    breakout = current_close > prior_resistance * 0.998 and close.iloc[-2] < prior_resistance
    if breakout and trend_up:
        return {
            "name": "Breakout from Resistance",
            "murphy_chapter": "Chapter 4 — Trend Concepts",
            "bias": "bullish",
            "description": "Price breaking above a tested resistance level. Prior resistance now acts as support. Entry on close above, stop below the breakout level."
        }
    
    # ── Double Bottom ──
    lows = low.iloc[-30:]
    sorted_lows = lows.nsmallest(5)
    if len(sorted_lows) >= 2:
        low1 = sorted_lows.iloc[0]
        low2 = sorted_lows.iloc[1]
        if abs(low1 - low2) / low1 < 0.015 and trend_up:
            return {
                "name": "Double Bottom",
                "murphy_chapter": "Chapter 5 — Major Reversal Patterns",
                "bias": "bullish",
                "description": "Two nearly equal lows forming a W-shape. Classic bullish reversal. Confirmed on break above the neckline (the high between the two lows)."
            }
    
    # ── Ascending Triangle ──
    flat_resistance = abs(rolling_high_10 - rolling_high_20) / rolling_high_20 < 0.008
    rising_lows = low.iloc[-10:].is_monotonic_increasing
    if flat_resistance and rising_lows and trend_up:
        return {
            "name": "Ascending Triangle",
            "murphy_chapter": "Chapter 6 — Continuation Patterns",
            "bias": "bullish",
            "description": "Flat resistance with rising support — buyers becoming more aggressive. Breakout above the flat resistance is typically powerful and sustained."
        }
    
    # ── Support Bounce ──
    key_support = low.iloc[-30:].quantile(0.15)
    near_support = current_close < key_support * 1.02
    bouncing = close.iloc[-1] > close.iloc[-3]
    if near_support and bouncing and trend_up:
        return {
            "name": "Support Bounce",
            "murphy_chapter": "Chapter 4 — Support and Resistance",
            "bias": "bullish",
            "description": "Price testing and holding at a known support level. Low-risk entry with tight stop just below the support zone."
        }
    
    # ── Descending Triangle (bearish) ──
    flat_support = abs(rolling_low_10 - rolling_low_20) / rolling_low_20 < 0.008
    falling_highs = high.iloc[-10:].is_monotonic_decreasing
    if flat_support and falling_highs and trend_down:
        return {
            "name": "Descending Triangle",
            "murphy_chapter": "Chapter 6 — Continuation Patterns",
            "bias": "bearish",
            "description": "Flat support with falling resistance — sellers becoming more aggressive. Breakdown below flat support often leads to sharp decline."
        }
    
    # ── No clear pattern ──
    if trend_up:
        return {"name": "Uptrend — No Pattern", "murphy_chapter": "Chapter 4", "bias": "bullish", "description": "Price in uptrend but no actionable pattern identified. Wait for a cleaner setup."}
    elif trend_down:
        return {"name": "Downtrend — No Pattern", "murphy_chapter": "Chapter 4", "bias": "bearish", "description": "Price in downtrend but no actionable pattern identified. Wait for a cleaner setup."}
    else:
        return {"name": "Ranging — No Setup", "murphy_chapter": "N/A", "bias": "neutral", "description": "Price ranging between support and resistance. No directional bias. Stand aside."}

def run_gate_checks(instrument_data, econ_events):
    """Run the 5-gate trade validity check."""
    gates = {}
    major_event_this_week = any(e.get("impact") == "HIGH" for e in econ_events)
    
    # Gate 1: Major macro event?
    gates["gate1_macro"] = {
        "pass": not major_event_this_week,
        "label": "Macro Events Clear",
        "reason": "High-impact event this week — setup valid but size down" if major_event_this_week else "No high-impact events — clean trading week"
    }
    
    # Gate 2: Trend clear?
    trend = instrument_data.get("trend", "ranging")
    gates["gate2_trend"] = {
        "pass": trend in ["bullish", "bearish"],
        "label": "Trend Clear",
        "reason": f"Trend: {trend}" if trend != "ranging" else "Ranging/choppy — no directional bias"
    }
    
    # Gate 3: Pattern identified?
    pattern_bias = instrument_data.get("pattern", {}).get("bias", "neutral")
    gates["gate3_pattern"] = {
        "pass": pattern_bias != "neutral",
        "label": "Pattern Identified",
        "reason": instrument_data.get("pattern", {}).get("name", "None")
    }
    
    # Gate 4: COT confirmation?
    cot_bias = instrument_data.get("cot_bias", "unknown")
    trend_dir = "long" if trend == "bullish" else "short"
    cot_pass = cot_bias == trend_dir or cot_bias == "unknown"
    gates["gate4_cot"] = {
        "pass": cot_pass,
        "label": "COT Confirmation",
        "reason": f"COT: {cot_bias} — {'confirms' if cot_pass else 'DIVERGES from'} price direction"
    }
    
    # Gate 5: R:R >= 2:1?
    rr = instrument_data.get("setup", {}).get("rr_ratio", 0)
    gates["gate5_rr"] = {
        "pass": rr >= 2.0,
        "label": "R:R ≥ 2:1",
        "reason": f"R:R = {rr:.1f}:1" if rr > 0 else "R:R not calculable — no setup"
    }
    
    all_pass = all(g["pass"] for g in gates.values())
    gates["overall"] = {
        "trade_valid": all_pass,
        "gates_passed": sum(1 for g in gates.values() if isinstance(g, dict) and g.get("pass", False))
    }
    return gates

def fetch_instrument(key, config):
    log(f"Fetching {key} ({config['ticker']})...")
    try:
        ticker = yf.Ticker(config["ticker"])
        
        # 4H data — last 60 days
        df_4h = ticker.history(period="60d", interval="4h")
        if df_4h.empty:
            log(f" WARNING: No 4H data for {key}")
            df_4h = None
        
        # Daily data — last 200 days
        df_daily = ticker.history(period="200d", interval="1d")
        if df_daily.empty:
            log(f" WARNING: No daily data for {key}")
            return None
        
        # Current price
        current_price = df_daily["Close"].iloc[-1]
        prev_close = df_daily["Close"].iloc[-2]
        price_change = current_price - prev_close
        price_change_pct = (price_change / prev_close) * 100
        
        # 4H Indicators
        if df_4h is not None and len(df_4h) >= 50:
            c4 = df_4h["Close"]
            h4 = df_4h["High"]
            l4 = df_4h["Low"]
            
            ema20_4h = ema(c4, 20).iloc[-1]
            ema50_4h = ema(c4, 50).iloc[-1]
            ema200_4h = ema(c4, 200).iloc[-1] if len(c4) >= 200 else None
            rsi_4h = rsi(c4, 14).iloc[-1]
            atr_4h = atr(h4, l4, c4, 14).iloc[-1]
            
            # Trend determination
            if current_price > ema20_4h > ema50_4h:
                trend_4h = "bullish"
            elif current_price < ema20_4h < ema50_4h:
                trend_4h = "bearish"
            else:
                trend_4h = "ranging"
            
            # Key levels
            high_20bars = h4.iloc[-20:].max()
            low_20bars = l4.iloc[-20:].min()
            high_5bars = h4.iloc[-5:].max()
            low_5bars = l4.iloc[-5:].min()
            
            # Stop and target calculation
            stop_distance = atr_4h * 1.5
            
            if trend_4h == "bullish":
                entry_zone_low = current_price
                entry_zone_high = current_price + atr_4h * 0.3
                stop_level = entry_zone_low - stop_distance
                target_1 = entry_zone_high + (stop_distance * 2)
                target_2 = entry_zone_high + (stop_distance * 3.5)
            elif trend_4h == "bearish":
                entry_zone_high = current_price
                entry_zone_low = current_price - atr_4h * 0.3
                stop_level = entry_zone_high + stop_distance
                target_1 = entry_zone_low - (stop_distance * 2)
                target_2 = entry_zone_low - (stop_distance * 3.5)
            else:
                entry_zone_low = current_price - atr_4h * 0.2
                entry_zone_high = current_price + atr_4h * 0.2
                stop_level = None
                target_1 = None
                target_2 = None
            
            # R:R
            if stop_level and target_1:
                risk = abs(entry_zone_low - stop_level) if trend_4h == "bullish" else abs(entry_zone_high - stop_level)
                reward = abs(target_1 - entry_zone_high) if trend_4h == "bullish" else abs(entry_zone_low - target_1)
                rr_ratio = reward / risk if risk > 0 else 0
            else:
                rr_ratio = 0
            
            # Pattern detection
            pattern = detect_pattern(df_4h, df_daily)
            
            indicators = {
                "ema20_4h": round(ema20_4h, 4),
                "ema50_4h": round(ema50_4h, 4),
                "ema200_4h": round(ema200_4h, 4) if ema200_4h else None,
                "rsi_4h": round(rsi_4h, 1),
                "atr_4h": round(atr_4h, 4),
                "high_20bars": round(high_20bars, 4),
                "low_20bars": round(low_20bars, 4),
            }
            
            setup = {
                "direction": "long" if trend_4h == "bullish" else ("short" if trend_4h == "bearish" else "none"),
                "entry_zone_low": round(entry_zone_low, 4),
                "entry_zone_high": round(entry_zone_high, 4),
                "stop_level": round(stop_level, 4) if stop_level else None,
                "target_1": round(target_1, 4) if target_1 else None,
                "target_2": round(target_2, 4) if target_2 else None,
                "rr_ratio": round(rr_ratio, 2),
                "atr_used": round(atr_4h, 4),
                "stop_distance": round(stop_distance, 4),
                "invalidation": f"4H close below {round(stop_level, 2)}" if stop_level and trend_4h == "bullish" else (f"4H close above {round(stop_level, 2)}" if stop_level else "N/A"),
            }
        else:
            trend_4h = "unknown"
            indicators = {}
            setup = {"direction": "none", "rr_ratio": 0}
            pattern = {"name": "No Pattern", "bias": "neutral", "murphy_chapter": "N/A", "description": "Insufficient 4H data"}
        
        # Weekly context
        c_d = df_daily["Close"]
        ema50_daily = ema(c_d, 50).iloc[-1]
        ema200_daily = ema(c_d, 200).iloc[-1]
        rsi_daily = rsi(c_d, 14).iloc[-1]
        week_high = df_daily["High"].iloc[-5:].max()
        week_low = df_daily["Low"].iloc[-5:].min()
        month_high = df_daily["High"].iloc[-22:].max()
        month_low = df_daily["Low"].iloc[-22:].min()
        
        log(f" ✓ {key}: ${current_price:.4f} | Trend: {trend_4h} | RSI: {indicators.get('rsi_4h', 'N/A')} | Pattern: {pattern['name']}")
        
        return {
            "key": key,
            "name": config["name"],
            "category": config["category"],
            "ticker": config["ticker"],
            "current_price": round(current_price, 4),
            "prev_close": round(prev_close, 4),
            "price_change": round(price_change, 4),
            "price_change_pct": round(price_change_pct, 2),
            "trend": trend_4h,
            "indicators": indicators,
            "setup": setup,
            "pattern": pattern,
            "cot_bias": "unknown",
            "weekly_context": {
                "week_high": round(week_high, 4),
                "week_low": round(week_low, 4),
                "month_high": round(month_high, 4),
                "month_low": round(month_low, 4),
                "ema50_daily": round(ema50_daily, 4),
                "ema200_daily": round(ema200_daily, 4),
                "rsi_daily": round(rsi_daily, 1),
            }
        }
    except Exception as e:
        log(f" ERROR fetching {key}: {e}")
        return None

def fetch_macro():
    log("Fetching macro data...")
    result = {}
    for key, ticker_str in MACRO.items():
        try:
            t = yf.Ticker(ticker_str)
            hist = t.history(period="5d", interval="1d")
            if not hist.empty:
                val = hist["Close"].iloc[-1]
                prev = hist["Close"].iloc[-2] if len(hist) > 1 else val
                result[key] = {
                    "value": round(val, 4),
                    "prev": round(prev, 4),
                    "change_pct": round(((val - prev) / prev) * 100, 2)
                }
                log(f" ✓ {key}: {val:.4f}")
        except Exception as e:
            log(f" ERROR {key}: {e}")
            result[key] = {"value": None, "prev": None, "change_pct": None}
    
    # Yield curve
    if result.get("YIELD_10Y", {}).get("value") and result.get("YIELD_2Y", {}).get("value"):
        result["YIELD_CURVE_SPREAD"] = round(result["YIELD_10Y"]["value"] - result["YIELD_2Y"]["value"], 4)
        result["YIELD_CURVE_INVERTED"] = result["YIELD_CURVE_SPREAD"] < 0
    
    return result

def fetch_cot_data():
    """Fetch CFTC Commitment of Traders data."""
    log("Fetching COT data from CFTC...")
    cot_url = "https://www.cftc.gov/dea/newcot/deahistfo_disaggregated.txt"
    cot_names = {
        "GOLD": "GOLD - COMMODITY EXCHANGE INC.",
        "SILVER": "SILVER - COMMODITY EXCHANGE INC.",
        "ES": "E-MINI S&P 500 - CHICAGO MERCANTILE EXCHANGE",
        "NQ": "E-MINI NASDAQ-100 - CHICAGO MERCANTILE EXCHANGE",
        "AUDUSD": "AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE",
        "GBPUSD": "BRITISH POUND STERLING - CHICAGO MERCANTILE EXCHANGE",
    }
    result = {k: {"net_speculator": None, "bias": "unknown", "trend": "unknown"} for k in cot_names}
    
    try:
        response = requests.get(cot_url, timeout=30)
        if response.status_code != 200:
            log(f" COT fetch failed: HTTP {response.status_code}")
            return result
        
        lines = response.text.split("\n")
        headers = [h.strip().upper() for h in lines[0].split(",")]
        
        try:
            name_idx = headers.index("MARKET_AND_EXCHANGE_NAMES")
            long_idx = headers.index("NONCOMM_POSITIONS_LONG_ALL")
            short_idx = headers.index("NONCOMM_POSITIONS_SHORT_ALL")
        except ValueError:
            log(" COT column parsing failed")
            return result
        
        recent_rows = {}
        for line in lines[1:]:
            if not line.strip():
                continue
            cols = line.split(",")
            if len(cols) <= max(name_idx, long_idx, short_idx):
                continue
            
            mkt_name = cols[name_idx].strip().upper().replace('"', '')
            for key, cot_name in cot_names.items():
                if cot_name in mkt_name and key not in recent_rows:
                    try:
                        longs = int(cols[long_idx].replace('"', '').strip())
                        shorts = int(cols[short_idx].replace('"', '').strip())
                        net = longs - shorts
                        result[key] = {
                            "net_speculator": net,
                            "longs": longs,
                            "shorts": shorts,
                            "bias": "long" if net > 0 else "short",
                            "trend": "strongly_long" if net > 50000 else ("long" if net > 0 else ("strongly_short" if net < -50000 else "short"))
                        }
                        recent_rows[key] = True
                        log(f" ✓ COT {key}: net {net:+,} ({result[key]['bias']})")
                    except (ValueError, IndexError):
                        pass
    except requests.RequestException as e:
        log(f" COT fetch error: {e}")
    
    return result

def fetch_economic_calendar():
    """Fetch upcoming week's economic events."""
    log("Building economic calendar...")
    today = datetime.utcnow()
    week_dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    
    always_watch = [
        {"event": "FOMC Meeting / Fed Statement", "impact": "HIGH", "affects": ["GOLD", "SILVER", "ES", "NQ", "AUDUSD", "GBPUSD"]},
        {"event": "US Non-Farm Payrolls (NFP)", "impact": "HIGH", "affects": ["GOLD", "AUDUSD", "GBPUSD", "ES", "NQ"]},
        {"event": "US CPI Inflation", "impact": "HIGH", "affects": ["GOLD", "SILVER", "ES", "NQ", "AUDUSD", "GBPUSD"]},
        {"event": "RBA Rate Decision", "impact": "HIGH", "affects": ["AUDUSD"]},
        {"event": "BOE Rate Decision", "impact": "HIGH", "affects": ["GBPUSD"]},
        {"event": "US GDP (Preliminary/Revised)", "impact": "HIGH", "affects": ["ES", "NQ", "AUDUSD", "GBPUSD"]},
        {"event": "PCE Price Index", "impact": "HIGH", "affects": ["GOLD", "ES", "NQ"]},
    ]
    
    return {
        "week_of": today.strftime("%B %d, %Y"),
        "week_dates": week_dates,
        "events": [],
        "always_watch": always_watch,
        "note": "ASTRA: This calendar requires a live scrape each Sunday.",
        "has_high_impact_event": False,
    }

def run_all_gates(instruments_data, econ_calendar):
    """Run gate checks for each instrument."""
    for key, data in instruments_data.items():
        if data:
            gates = run_gate_checks(data, econ_calendar.get("events", []))
            data["gates"] = gates
            data["trade_valid"] = gates["overall"]["trade_valid"]
            data["gates_passed"] = gates["overall"]["gates_passed"]
    return instruments_data

def main():
    log("=" * 60)
    log("ASTRA Weekly Trade Idea Data Fetch — Starting")
    log("=" * 60)
    
    report_date = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Fetch all instruments
    instruments_data = {}
    for key, config in INSTRUMENTS.items():
        data = fetch_instrument(key, config)
        instruments_data[key] = data
    
    # Fetch macro
    macro_data = fetch_macro()
    
    # Fetch COT
    cot_data = fetch_cot_data()
    
    # Apply COT bias
    for key in instruments_data:
        if instruments_data[key] and key in cot_data:
            instruments_data[key]["cot_bias"] = cot_data[key].get("bias", "unknown")
            instruments_data[key]["cot_detail"] = cot_data[key]
    
    # Economic calendar
    econ_calendar = fetch_economic_calendar()
    
    # Run gate checks
    instruments_data = run_all_gates(instruments_data, econ_calendar)
    
    # Summary
    valid_trades = [k for k, v in instruments_data.items() if v and v.get("trade_valid")]
    no_trade = [k for k, v in instruments_data.items() if v and not v.get("trade_valid")]
    
    log(f"\nSummary:")
    log(f" Valid setups: {valid_trades if valid_trades else 'None this week'}")
    log(f" No trade: {no_trade}")
    
    # Build output
    output = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "report_date": report_date,
        "week_of": econ_calendar["week_of"],
        "timeframe": "4H (swing trade)",
        "instruments": instruments_data,
        "macro": macro_data,
        "cot": cot_data,
        "econ_calendar": econ_calendar,
        "valid_setups": valid_trades,
        "no_trade": no_trade,
        "astra_notes": "All prices fetched live. COT from CFTC. Patterns detected algorithmically.",
    }
    
    # Save
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2, default=str)
    
    log(f"\n✓ Data saved to {OUTPUT_FILE}")
    log(f" Valid setups this week: {len(valid_trades)}")
    log("=" * 60)
    return output

if __name__ == "__main__":
    main()
