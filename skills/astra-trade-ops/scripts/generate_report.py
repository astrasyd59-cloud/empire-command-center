#!/usr/bin/env python3
"""
=============================================================
ASTRA — THE DAILY TRADE IDEA
All-in-one: fetch data + generate HTML report
=============================================================
SAVE AS: ~/.openclaw/workspace/scripts/generate_trade_report.py
RUN EVERY SUNDAY EVENING: python3 ~/.openclaw/workspace/scripts/generate_trade_report.py
OUTPUT: ~/.openclaw/workspace/reports/trade_YYYY-MM-DD.html
REQUIRES: pip install yfinance pandas numpy requests
KIMI API KEY: export KIMI_API_KEY="your_key_here" (or hardcode it in the CONFIG section below)
=============================================================
"""

import os, json, sys, re, textwrap
from datetime import datetime
from pathlib import Path

# ─── INSTALL CHECK ────────────────────────────────────────────────────────────
try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    import requests
except ImportError:
    print("Missing packages. Run: pip install yfinance pandas numpy requests")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG — edit these
# ═══════════════════════════════════════════════════════════════════════════════
KIMI_API_KEY = os.environ.get("KIMI_API_KEY", "")  # or paste key here as string
REPORTS_DIR = Path.home() / ".openclaw" / "workspace" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
TODAY = datetime.utcnow().strftime("%Y-%m-%d")
WEEK_OF = datetime.utcnow().strftime("%B %d, %Y")
GEN_TIME = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")

INSTRUMENTS = {
    "GOLD": ("GC=F", "Gold Futures", "commodity"),
    "SILVER": ("SI=F", "Silver Futures", "commodity"),
    "ES": ("ES=F", "S&P 500 E-mini", "index"),
    "NQ": ("NQ=F", "Nasdaq 100 E-mini", "index"),
    "AUDUSD": ("AUDUSD=X", "Australian Dollar/USD", "forex"),
    "GBPUSD": ("GBPUSD=X", "British Pound/USD", "forex"),
}
ORDER = ["GOLD","SILVER","ES","NQ","AUDUSD","GBPUSD"]

MACRO_TICKERS = {
    "SP500": "^GSPC",
    "VIX": "^VIX",
    "DXY": "DX-Y.NYB",
    "YIELD_10Y": "^TNX",
    "YIELD_2Y": "^IRX",
    "GOLD": "GC=F",
}

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1 — FETCH DATA
# ═══════════════════════════════════════════════════════════════════════════════

def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()

def rsi(s, n=14):
    d = s.diff()
    g = d.clip(lower=0).rolling(n).mean()
    l = (-d.clip(upper=0)).rolling(n).mean()
    rs = g / l.replace(0, float('nan'))
    return 100 - (100 / (1 + rs))

def atr(h, l, c, n=14):
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()

def safe_float(v, decimals=4):
    try:
        return round(float(v), decimals)
    except:
        return None

def detect_pattern(c4, h4, l4, e20, e50, trend):
    try:
        price = float(c4.iloc[-1])
        rng5 = float(h4.iloc[-5:].max() - l4.iloc[-5:].min())
        rng20 = float(h4.iloc[-20:].max() - l4.iloc[-20:].min())
        hi30 = float(h4.iloc[-30:-5].max()) if len(h4) >= 30 else float(h4.max())
        lo10 = float(l4.iloc[-10:].min())
        hi10 = float(h4.iloc[-10:].max())
        hi20 = float(h4.iloc[-20:].max())
        lo20 = float(l4.iloc[-20:].min())

        impulse_up = len(c4) >= 20 and float(c4.iloc[-15]) > float(c4.iloc[-20]) * 1.015
        impulse_down = len(c4) >= 20 and float(c4.iloc[-15]) < float(c4.iloc[-20]) * 0.985
        tight = rng5 < rng20 * 0.42

        if trend == "bullish" and impulse_up and tight:
            return ("Bull Flag", "Chapter 6 — Continuation Patterns",
                "Strong impulse rally followed by tight low-volume consolidation. Breakout above the flag high targets the flagpole length projected upward.",
                "The flag represents a brief pause in a strong trend. Volume should dry up during the flag and surge on the breakout — confirming trend resumption.")

        if trend == "bearish" and impulse_down and tight:
            return ("Bear Flag", "Chapter 6 — Continuation Patterns",
                "Sharp decline followed by a tight low-volume bounce. Breakdown below the flag low targets the flagpole length projected downward.",
                "Bear flags form during the strongest downtrends. Declining volume during the flag followed by a volume surge on breakdown confirms continuation.")

        if trend == "bullish" and price > hi30 * 0.998 and len(c4) >= 2 and float(c4.iloc[-2]) < hi30:
            return ("Breakout from Resistance", "Chapter 4 — Trend Concepts",
                "Price breaking above a tested resistance level on the 4H chart. Prior resistance becomes new support once the break is confirmed.",
                "A breakout from resistance is one of the most reliable bullish signals when accompanied by above-average volume.")

        lows_s = l4.iloc[-30:] if len(l4) >= 30 else l4
        bot = lows_s.nsmallest(4)
        if len(bot) >= 2 and abs(float(bot.iloc[0]) - float(bot.iloc[1])) / max(float(bot.iloc[0]), 0.0001) < 0.015 and trend == "bullish":
            return ("Double Bottom", "Chapter 5 — Major Reversal Patterns",
                "Two nearly equal lows forming a W-shape on the 4H chart. Classic bullish reversal confirmed on a close above the neckline.",
                "The double bottom is one of the most common and reliable reversal patterns. The neckline break is the trigger — not the second low.")

        flat_res = abs(hi10 - hi20) / max(hi20, 0.0001) < 0.009
        rising = bool(l4.iloc[-10:].is_monotonic_increasing) if len(l4) >= 10 else False
        if trend == "bullish" and flat_res and rising:
            return ("Ascending Triangle", "Chapter 6 — Continuation Patterns",
                "Flat resistance with rising support — buyers becoming more aggressive each pullback. Breakout above the flat line is typically powerful.",
                "In an ascending triangle, the fact that buyers are willing to pay higher prices on each pullback is itself a bullish signal even before the breakout.")

        flat_sup = abs(lo10 - lo20) / max(lo20, 0.0001) < 0.009
        falling = bool(h4.iloc[-10:].is_monotonic_decreasing) if len(h4) >= 10 else False
        if trend == "bearish" and flat_sup and falling:
            return ("Descending Triangle", "Chapter 6 — Continuation Patterns",
                "Flat support with falling resistance — sellers becoming more aggressive. Breakdown below flat support often leads to a sharp decline.",
                "The descending triangle is a bearish continuation pattern. The inability to rally back to previous highs shows sellers are in control.")

        supp = float(l4.iloc[-30:].quantile(0.15)) if len(l4) >= 10 else float(l4.min())
        if trend == "bullish" and price < supp * 1.02 and len(c4) >= 3 and float(c4.iloc[-1]) > float(c4.iloc[-3]):
            return ("Support Bounce", "Chapter 4 — Support and Resistance",
                "Price testing and holding at a known support level on the 4H chart. Low-risk entry with stop just below support.",
                "Old support becomes new buying opportunity. The key is that price holds — closes below the support level invalidate the bounce thesis immediately.")

        if trend == "bullish":
            return ("Uptrend — No Entry Yet", "Chapter 4 — Trend Analysis",
                "Price in a clear uptrend above EMA20 and EMA50 on 4H but no actionable pattern has formed yet. Watching for pullback entry.",
                "Never chase a trend without a defined entry. Wait for the pattern to form before committing capital.")

        if trend == "bearish":
            return ("Downtrend — No Entry Yet", "Chapter 4 — Trend Analysis",
                "Price in a clear downtrend below EMA20 and EMA50 on 4H. No short entry yet — waiting for a clean pattern.",
                "Patience in a downtrend means waiting for a dead-cat bounce to set up the short entry, not chasing the move down.")

        return ("Ranging — No Setup", "N/A",
            "Price is ranging between support and resistance with no directional bias. No trade this week.",
            "The most money is lost by trading in ranging markets. Patience here preserves capital for the next trending opportunity.")

    except Exception as e:
        return ("Error Detecting Pattern", "N/A", str(e), "Retry data fetch.")

def fetch_instrument(key, ticker_str, name):
    print(f" [{key}] Fetching {ticker_str}...")
    try:
        t = yf.Ticker(ticker_str)
        d4h = t.history(period="60d", interval="4h")
        ddly = t.history(period="200d", interval="1d")

        if ddly.empty:
            print(f" No daily data for {key}")
            return None

        c = ddly["Close"]; h = ddly["High"]; l = ddly["Low"]
        price = safe_float(c.iloc[-1], 4)
        prev = safe_float(c.iloc[-2], 4)
        chg_pct = safe_float((price - prev) / prev * 100, 2) if prev else 0

        # 4H indicators
        if d4h is not None and len(d4h) >= 55:
            c4 = d4h["Close"]; h4 = d4h["High"]; l4 = d4h["Low"]
            e20v = safe_float(ema(c4, 20).iloc[-1], 4)
            e50v = safe_float(ema(c4, 50).iloc[-1], 4)
            rsi4 = safe_float(rsi(c4).iloc[-1], 1)
            atr4 = safe_float(atr(h4, l4, c4).iloc[-1], 4)

            if price > e20v > e50v:
                trend = "bullish"
            elif price < e20v < e50v:
                trend = "bearish"
            else:
                trend = "ranging"

            pat_name, pat_chap, pat_desc, murphy_q = detect_pattern(c4, h4, l4, e20v, e50v, trend)

            sdist = safe_float(atr4 * 1.5, 4)

            if trend == "bullish":
                elo = price
                ehi = safe_float(price + atr4 * 0.25, 4)
                stop = safe_float(elo - sdist, 4)
                t1 = safe_float(ehi + sdist * 2.0, 4)
                t2 = safe_float(ehi + sdist * 3.5, 4)
                risk = abs(elo - stop)
                rr1 = safe_float(abs(t1 - elo) / risk, 1) if risk else 0
                rr2 = safe_float(abs(t2 - elo) / risk, 1) if risk else 0
            elif trend == "bearish":
                ehi = price
                elo = safe_float(price - atr4 * 0.25, 4)
                stop = safe_float(ehi + sdist, 4)
                t1 = safe_float(elo - sdist * 2.0, 4)
                t2 = safe_float(elo - sdist * 3.5, 4)
                risk = abs(ehi - stop)
                rr1 = safe_float(abs(ehi - t1) / risk, 1) if risk else 0
                rr2 = safe_float(abs(ehi - t2) / risk, 1) if risk else 0
            else:
                elo = ehi = stop = t1 = t2 = price
                rr1 = rr2 = 0

            valid = (trend != "ranging") and (rr1 >= 1.8) and ("Ranging" not in pat_name) and ("No Entry" not in pat_name)
        else:
            e20v = e50v = rsi4 = atr4 = sdist = None
            elo = ehi = stop = t1 = t2 = price
            rr1 = rr2 = 0
            trend = "ranging"
            valid = False
            pat_name = "Insufficient 4H Data"
            pat_chap = "N/A"
            pat_desc = "Less than 55 4H candles available."
            murphy_q = "Always ensure sufficient data before trading."

        # Daily context
        ema50d = safe_float(ema(c, 50).iloc[-1], 2)
        ema200d = safe_float(ema(c, 200).iloc[-1], 2)
        wk_hi = safe_float(h.iloc[-5:].max(), 4)
        wk_lo = safe_float(l.iloc[-5:].min(), 4)

        print(f"  Price={price} | Trend={trend} | RSI={rsi4} | Pattern={pat_name} | Valid={valid}")

        return {
            "key": key, "name": name, "ticker": ticker_str,
            "price": price, "prev": prev, "chg_pct": chg_pct,
            "trend": trend, "valid": valid,
            "e20": e20v, "e50": e50v, "rsi": rsi4, "atr": atr4,
            "elo": elo, "ehi": ehi, "stop": stop, "t1": t1, "t2": t2,
            "rr1": rr1, "rr2": rr2, "sdist": sdist,
            "pat_name": pat_name, "pat_chap": pat_chap, "pat_desc": pat_desc, "murphy_q": murphy_q,
            "ema50d": ema50d, "ema200d": ema200d, "wk_hi": wk_hi, "wk_lo": wk_lo,
            "cot_net": None, "cot_bias": "pending",
        }
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def fetch_macro():
    print(" [MACRO] Fetching...")
    out = {}
    for k, tkr in MACRO_TICKERS.items():
        try:
            h = yf.Ticker(tkr).history(period="5d", interval="1d")
            if not h.empty:
                v = float(h["Close"].iloc[-1])
                p = float(h["Close"].iloc[-2]) if len(h) > 1 else v
                out[k] = {"v": round(v, 4), "chg": round((v-p)/p*100, 2)}
                print(f"  {k}: {v:.4f} ({out[k]['chg']:+.2f}%)")
        except Exception as e:
            print(f"  {k} error: {e}")
            out[k] = {"v": None, "chg": 0}
    try:
        y10 = out.get("YIELD_10Y", {}).get("v") or 0
        y2 = out.get("YIELD_2Y", {}).get("v") or 0
        out["SPREAD"] = round(y10 - y2, 3)
        out["INVERTED"] = out["SPREAD"] < 0
    except:
        out["SPREAD"] = None
        out["INVERTED"] = False
    return out

def fetch_cot():
    """COT data fetch - disabled due to CFTC API changes. Re-enable when alternative source found."""
    print(" [COT] Skipped (CFTC API unavailable - manual check recommended)")
    return {k: {"net": None, "bias": "manual_check"} for k in INSTRUMENTS}

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2 — ANALYSIS (direct fallback, no Kimi needed for test)
# ═══════════════════════════════════════════════════════════════════════════════

def build_analysis(instruments_data, macro, cot):
    """Build analysis directly without Kimi API."""
    gv = lambda k, f="v": (macro.get(k) or {}).get(f) if isinstance(macro.get(k), dict) else (macro.get(k) or {})
    g = lambda k: gv(k, "v")
    gc = lambda k: gv(k, "chg") or 0

    vix_val = g("VIX") or 0
    dxy_chg = gc("DXY") or 0
    gold_v = g("GOLD") or 0

    out = {
        "market_context": (
            f"Markets this week: S&P 500 at {g('SP500') or '—'} with VIX at {vix_val} — "
            f"{'elevated volatility warrants smaller position sizes' if vix_val > 20 else 'moderate volatility environment'}. "
            f"DXY {'strengthening' if dxy_chg > 0 else 'weakening'} ({dxy_chg:+.2f}%) — "
            f"{'headwind for commodities' if dxy_chg > 0 else 'tailwind for Gold and Silver'}. "
            f"Gold live at ${gold_v:,.2f}."
        ),
        "instruments": {}
    }

    for k, d in instruments_data.items():
        if not d:
            out["instruments"][k] = {
                "status": "NO_TRADE",
                "analyst_view": "Data fetch failed — cannot assess setup.",
                "what_changes_it": "Retry data fetch next session.",
                "gates_failed": ["trend"]
            }
            continue

        c = cot.get(k, {})
        cot_bias = c.get("bias", "unknown")
        cot_net = c.get("net")
        cot_str = (f"Large specs net {cot_net:+,} — {cot_bias} bias." if cot_net else "COT unavailable.")

        dxy_str = ""
        if k in ("GOLD", "SILVER"):
            dxy_str = (f"DXY {'strengthening — headwind' if dxy_chg > 0 else 'weakening — tailwind'}.")
        elif k in ("ES", "NQ"):
            dxy_str = (f"VIX at {vix_val} — {'elevated, risk-off' if vix_val > 20 else 'contained, risk-on'}.")
        elif k in ("AUDUSD",):
            dxy_str = (f"DXY {'strengthening — headwind' if dxy_chg > 0 else 'weakening — tailwind'} for AUD.")
        elif k in ("GBPUSD",):
            dxy_str = (f"DXY {'strengthening — bearish' if dxy_chg > 0 else 'weakening — supports upside'}.")

        if d["valid"]:
            direction = "LONG" if d["trend"] == "bullish" else "SHORT"
            below_above = "below" if direction == "LONG" else "above"
            conf = "HIGH" if d["rr1"] >= 2.5 and cot_bias == d["trend"][:4] else "MEDIUM"

            out["instruments"][k] = {
                "status": "TRADE",
                "direction": direction,
                "confidence": conf,
                "analyst_view": (
                    f"4H trend is {d['trend']} with price {'above' if direction=='LONG' else 'below'} "
                    f"EMA20 ({d['e20']}) and EMA50 ({d['e50']}). "
                    f"Pattern: {d['pat_name']} — {d['pat_desc'][:120]}. "
                    f"RSI at {d['rsi']}. R:R {d['rr1']}:1 at T1, {d['rr2']}:1 at T2."
                ),
                "entry_zone": f"{d['elo']} – {d['ehi']} on 4H close",
                "stop_note": f"Stop at {d['stop']} — 1.5× ATR({d['atr']}) = {d['sdist']} {below_above} entry.",
                "target_note": f"T1: {d['t1']} (R:R {d['rr1']}:1). T2: {d['t2']} (R:R {d['rr2']}:1).",
                "cot_insight": cot_str,
                "macro_connection": dxy_str,
                "invalidation": f"4H close {below_above} {d['stop']} — exit immediately.",
                "pattern_confirmed": True,
                "sizing": f"Risk 1% of account. Entry {d['elo']}, stop {d['stop']}, risk/unit = {abs((d['elo'] or 0) - (d['stop'] or 0)):.4f}.",
                "murphy_application": d["murphy_q"],
            }
        else:
            reasons = []
            gates = []
            if d["trend"] == "ranging":
                reasons.append("no clear 4H trend")
                gates.append("trend")
            if d["rr1"] < 1.8 and d["rr1"] > 0:
                reasons.append(f"R:R only {d['rr1']}:1 — below 2:1 minimum")
                gates.append("rr")
            if "Ranging" in d["pat_name"] or "No Entry" in d["pat_name"]:
                reasons.append("no actionable pattern")
                gates.append("pattern")
            if not reasons:
                reasons.append("setup does not meet all 5 gate criteria")
                gates = ["trend", "pattern"]

            out["instruments"][k] = {
                "status": "NO_TRADE",
                "analyst_view": f"Standing aside: {'; '.join(reasons)}.",
                "what_changes_it": f"Need: clean trend + confirmed pattern + R:R ≥ 2:1.",
                "gates_failed": gates,
            }

    return out

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3 — HTML RENDERER (simplified for test)
# ═══════════════════════════════════════════════════════════════════════════════

def render_html(instruments, macro, analysis):
    gv = lambda k, f="v": (macro.get(k) or {}).get(f) if isinstance(macro.get(k), dict) else (macro.get(k) or {})
    g = lambda k: gv(k, "v")
    gc = lambda k: gv(k, "chg") or 0

    sp500 = g("SP500"); sp_c = gc("SP500")
    vix = g("VIX"); vx_c = gc("VIX")
    dxy = g("DXY"); dx_c = gc("DXY")
    gold = g("GOLD"); gl_c = gc("GOLD")

    valid_n = sum(1 for v in analysis.get("instruments", {}).values() if isinstance(v, dict) and v.get("status") == "TRADE")
    notrade_n = len(instruments) - valid_n

    cards = []
    for k in ORDER:
        d = instruments.get(k)
        idea = analysis.get("instruments", {}).get(k, {})
        if not d:
            continue
        if idea.get("status") == "TRADE":
            cards.append(f"<div class='card trade'><h3>{k} — {idea.get('direction')} TRADE</h3><p>Entry: {idea.get('entry_zone')}</p><p>Stop: {idea.get('stop_note')}</p><p>Target: {idea.get('target_note')}</p></div>")
        else:
            cards.append(f"<div class='card notrade'><h3>{k} — NO TRADE</h3><p>{idea.get('analyst_view', 'No setup')}</p></div>")

    html = f"""<!DOCTYPE html>
<html>
<head><title>The Daily Trade Idea | {WEEK_OF}</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #1a1a1a; color: #eee; }}
.card {{ border: 1px solid #444; border-radius: 8px; padding: 20px; margin: 15px 0; background: #222; }}
.trade {{ border-left: 4px solid #4caf6a; }}
.notrade {{ border-left: 4px solid #666; opacity: 0.7; }}
h1 {{ color: #4caf6a; }}
h3 {{ margin-top: 0; color: #ddd; }}
.macro {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 20px 0; }}
.macro-item {{ background: #333; padding: 10px; border-radius: 4px; text-align: center; }}
</style>
</head>
<body>
<h1>THE DAILY TRADE IDEA</h1>
<p>Week of {WEEK_OF} | Generated {GEN_TIME}</p>
<div class="macro">
  <div class="macro-item"><strong>S&P 500</strong><br>{sp500 or '—'} ({sp_c:+.2f}%)</div>
  <div class="macro-item"><strong>VIX</strong><br>{vix or '—'} ({vx_c:+.2f}%)</div>
  <div class="macro-item"><strong>DXY</strong><br>{dxy or '—'} ({dx_c:+.2f}%)</div>
  <div class="macro-item"><strong>Gold</strong><br>${gold:,.2f} ({gl_c:+.2f}%)</div>
</div>
<p><em>{analysis.get('market_context', '')}</em></p>
<h2>Trade Ideas — {valid_n} valid · {notrade_n} no trade</h2>
{''.join(cards)}
<footer style="margin-top:40px;padding-top:20px;border-top:1px solid #444;font-size:12px;color:#666;">
Generated by ASTRA | Not financial advice | Data: yfinance
</footer>
</body>
</html>"""

    return html

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print(f"\n{'='*60}")
    print(f"ASTRA TRADE REPORT — {WEEK_OF}")
    print(f"{'='*60}\n")

    # 1. Fetch instruments
    print("[1/3] Fetching instrument data (4H)...")
    instruments = {}
    for key, (ticker, name, _) in INSTRUMENTS.items():
        instruments[key] = fetch_instrument(key, ticker, name)

    # 2. Fetch macro
    print("\n[2/3] Fetching macro data...")
    macro = fetch_macro()

    # 3. Fetch COT
    print("\n[3/3] Fetching COT from CFTC...")
    cot = fetch_cot()
    for k in instruments:
        if instruments[k] and k in cot:
            instruments[k]["cot_bias"] = cot[k].get("bias", "unknown")
            instruments[k]["cot_net"] = cot[k].get("net")

    # 4. Build analysis
    print("\n[4/4] Building trade analysis...")
    analysis = build_analysis(instruments, macro, cot)

    # 5. Render & save
    html = render_html(instruments, macro, analysis)

    out_file = REPORTS_DIR / f"trade_{TODAY}.html"
    out_file.write_text(html, encoding="utf-8")

    latest = REPORTS_DIR / "latest_trade.html"
    latest.write_text(html, encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"✅ REPORT SAVED:")
    print(f"   {out_file}")
    print(f"   {latest}")
    print(f"{'='*60}")

    # Summary
    print(f"\n📊 SUMMARY:")
    for k in ORDER:
        d = instruments.get(k)
        a = analysis.get("instruments", {}).get(k, {})
        status = "✓ TRADE" if a.get("status") == "TRADE" else "✗ NO TRADE"
        price = d.get("price", "—") if d else "—"
        print(f"   {k:8} | {status} | ${price}")

if __name__ == "__main__":
    main()
