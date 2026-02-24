#!/usr/bin/env python3
"""
ASTRA — Kimi 2.5 Prompt Templates
Weekly Trade Idea Report Generator
OpenClaw Empire
"""

import json
import os
import re
import requests
from pathlib import Path

# ══════════════════════════════════════════════════════════════════
# SYSTEM PROMPT — loaded once, defines ASTRA's personality
# and strict rules for the trade report
# ══════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are ASTRA — Algorithmic Swing Trade Research Assistant — operating within the OpenClaw Empire trading system for Dibs, a professional trading operations specialist based in Sydney, Australia.

Your role in this module is to generate The Daily Trade Idea — a weekly swing trade report based on 4-hour chart analysis. You are precise, disciplined, and never speculate beyond the data you are given.

## YOUR CORE RULES — NON-NEGOTIABLE

### Rule 1: Numbers Only From the JSON
Every price, level, indicator value, and percentage in your report MUST come directly from the JSON data object you are given. You cannot recall prices from memory. You cannot estimate or approximate.

### Rule 2: Earnings & Events — Never Say "No Events" Without Checking
If the economic calendar JSON shows no events, you write: "No high-impact events found in today's data pull — verify independently before trading."

### Rule 3: "No Trade" is a Valid and Valuable Output
If a setup does not pass all 5 gates, you write a clear "NO TRADE" card. You explain WHY there is no trade.

### Rule 4: 4H Timeframe Only
All analysis is based on the 4-hour chart. You may reference daily context for trend bias but all entries, stops, and targets are 4H based.

### Rule 5: Murphy Pattern Rules
When you identify a chart pattern from the JSON:
- Name it exactly as it appears in Murphy's "Technical Analysis of the Financial Markets"
- State the chapter reference
- Describe what makes this pattern valid on the current chart

### Rule 6: COT Data Context
When COT data shows large speculator net positioning:
- Net long > 50,000: "Speculators strongly positioned long — tailwind"
- Net long 0–50,000: "Speculators modestly long — mild tailwind"
- Net short 0 to −50,000: "Speculators modestly short — mild headwind"
- Net short < −50,000: "Speculators heavily short — caution or counter-trend"
- Divergence (specs short, price bullish): flag as "COT Divergence — size down"

### Rule 7: Stop Sizing
Stops are always 1.5x ATR from entry. This is non-negotiable.

### Rule 8: Invalidation
Every trade idea must state the exact invalidation condition.

## YOUR PERSONALITY
You are intelligent, direct, and institutionally-minded. You write like a senior analyst at a prop trading desk — not like a retail trading newsletter.

No hype. No "this could be massive." No predictions dressed as certainties. You think probabilistically.

You are aware that Dibs trades CFDs on CMC Markets and City Index for Gold, Silver, ES, NQ, and FX.

## OUTPUT FORMAT
You output a JSON object with this structure:

{
  "report_date": "YYYY-MM-DD",
  "week_of": "Week of [Date]",
  "market_context": {
    "summary": "2-3 sentence macro context",
    "vix_reading": "string interpretation",
    "dxy_direction": "string",
    "yield_context": "string",
    "key_events_warning": "string"
  },
  "instruments": {
    "GOLD": { ...trade idea or no_trade object... },
    "SILVER": { ...}, etc
  }
}
"""

# ══════════════════════════════════════════════════════════════════
# USER PROMPT — generated each week from the data JSON
# ══════════════════════════════════════════════════════════════════

def build_user_prompt(data_json: dict) -> str:
    """Build the user prompt by injecting the fetched data JSON."""
    
    import json as _json
    
    instruments_summary = {}
    for key, inst in data_json.get("instruments", {}).items():
        if not inst:
            instruments_summary[key] = {"error": "data fetch failed"}
            continue
        
        instruments_summary[key] = {
            "current_price": inst.get("current_price"),
            "price_change_pct": inst.get("price_change_pct"),
            "trend_4h": inst.get("trend"),
            "pattern": inst.get("pattern"),
            "indicators": {
                "ema20_4h": inst.get("indicators", {}).get("ema20_4h"),
                "ema50_4h": inst.get("indicators", {}).get("ema50_4h"),
                "rsi_4h": inst.get("indicators", {}).get("rsi_4h"),
                "atr_4h": inst.get("indicators", {}).get("atr_4h"),
                "high_20bars": inst.get("indicators", {}).get("high_20bars"),
                "low_20bars": inst.get("indicators", {}).get("low_20bars"),
            },
            "setup": inst.get("setup"),
            "cot_detail": inst.get("cot_detail"),
            "weekly_context": inst.get("weekly_context"),
            "gates": inst.get("gates"),
            "trade_valid": inst.get("trade_valid"),
        }
    
    macro = data_json.get("macro", {})
    econ = data_json.get("econ_calendar", {})
    
    prompt = f"""You are generating The Daily Trade Idea for the week of {data_json.get('week_of', 'this week')}.
Timeframe: 4H (all entries, stops, targets must be 4H based).

## LIVE MARKET DATA (fetched {data_json.get('generated_at', 'recently')})

### Macro Environment
- S&P 500: {macro.get('SP500', {}).get('value')} ({macro.get('SP500', {}).get('change_pct', 0):+.2f}%)
- VIX: {macro.get('VIX', {}).get('value')} ({macro.get('VIX', {}).get('change_pct', 0):+.2f}%)
- DXY (Dollar Index): {macro.get('DXY', {}).get('value')} ({macro.get('DXY', {}).get('change_pct', 0):+.2f}%)
- 10Y Yield: {macro.get('YIELD_10Y', {}).get('value')}%
- 2Y Yield: {macro.get('YIELD_2Y', {}).get('value')}%
- Yield Curve Spread (10Y-2Y): {macro.get('YIELD_CURVE_SPREAD')} ({'INVERTED' if macro.get('YIELD_CURVE_INVERTED') else 'NORMAL'})

### Economic Calendar
Week of: {econ.get('week_of')}
Events this week: {_json.dumps(econ.get('events', []), indent=2) if econ.get('events') else 'Not yet scraped — flag as unverified in your output'}
Note: {econ.get('note', '')}

### Instrument Data (4H Charts)
{_json.dumps(instruments_summary, indent=2, default=str)}

### Gate Check Results
Valid setups (all 5 gates passed): {data_json.get('valid_setups', [])}
No trade this week: {data_json.get('no_trade', [])}

## YOUR TASK
1. Write a 2-3 sentence macro context paragraph
2. For EACH of the 6 instruments, write either a TRADE idea or NO_TRADE card
3. Use ONLY the numbers above — do not supplement with your own knowledge of prices
4. Reference Murphy's pattern name exactly for each setup
5. Include COT context for every instrument
6. State ATR-based stop calculation explicitly
7. Output valid JSON following the schema in your system prompt

If the economic calendar is empty/unverified, add this warning to EVERY trade:
"⚠️ Economic calendar unverified this week. Check for FOMC, NFP, and CPI dates before entering any position."

Begin your JSON output now.
"""
    return prompt

# ══════════════════════════════════════════════════════════════════
# KIMI API CALL — sends data to Kimi 2.5 and gets trade ideas back
# ══════════════════════════════════════════════════════════════════

def call_kimi(data_json: dict, api_key: str) -> dict:
    """Call Kimi 2.5 with the market data and get trade ideas back.
    
    API Key: Set in environment variable KIMI_API_KEY
    Endpoint: https://api.moonshot.cn/v1/chat/completions
    Model: moonshot-v1-32k (Kimi 2.5)
    """
    
    user_prompt = build_user_prompt(data_json)
    
    payload = {
        "model": "moonshot-v1-32k",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,  # Low temp = more consistent, less creative
        "max_tokens": 4000,
        "response_format": {"type": "json_object"}  # Force JSON output
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        "https://api.moonshot.cn/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=120
    )
    
    if response.status_code != 200:
        raise Exception(f"Kimi API error: {response.status_code} — {response.text}")
    
    result = response.json()
    content = result["choices"][0]["message"]["content"]
    
    # Parse JSON from Kimi's response
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # If Kimi returns text with JSON embedded, extract it
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        raise Exception("Could not parse JSON from Kimi response")

# ══════════════════════════════════════════════════════════════════
# VALIDATION — checks Kimi's output against fetched data
# Flags any price that doesn't match the source data
# ══════════════════════════════════════════════════════════════════

def validate_trade_output(kimi_output: dict, source_data: dict) -> dict:
    """Compare Kimi's price outputs against the fetched source data.
    Flag any significant discrepancies (> 2% off).
    """
    
    validation = {"passed": True, "warnings": [], "errors": []}
    
    for key, inst_data in source_data.get("instruments", {}).items():
        if not inst_data:
            continue
        
        kimi_inst = kimi_output.get("instruments", {}).get(key, {})
        if not kimi_inst or kimi_inst.get("status") == "NO_TRADE":
            continue
        
        source_price = inst_data.get("current_price", 0)
        if source_price == 0:
            continue
        
        # Check entry zone
        entry_low = kimi_inst.get("entry", {}).get("zone_low", 0)
        entry_high = kimi_inst.get("entry", {}).get("zone_high", 0)
        
        if entry_low and abs(entry_low - source_price) / source_price > 0.05:
            validation["warnings"].append(
                f"{key}: Entry zone ${entry_low} seems far from current price ${source_price} (>5%). Verify."
            )
        
        # Check stop is ATR-based
        stop_level = kimi_inst.get("stop", {}).get("level", 0)
        atr_val = inst_data.get("indicators", {}).get("atr_4h", 0)
        
        if stop_level and atr_val:
            stop_dist = abs(entry_low - stop_level) if entry_low else 0
            expected_stop_dist = atr_val * 1.5
            
            if expected_stop_dist > 0 and abs(stop_dist - expected_stop_dist) / expected_stop_dist > 0.2:
                validation["warnings"].append(
                    f"{key}: Stop distance {stop_dist:.2f} deviates from 1.5×ATR={expected_stop_dist:.2f}"
                )
    
    if validation["warnings"] or validation["errors"]:
        validation["passed"] = len(validation["errors"]) == 0
    
    return validation

# ══════════════════════════════════════════════════════════════════
# MAIN ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════

def generate_weekly_report(data_json_path: str, api_key: str, output_path: str):
    """Full pipeline:
    1. Load fetched data
    2. Call Kimi
    3. Validate output
    4. Save final JSON for HTML renderer
    """
    
    with open(data_json_path) as f:
        data = json.load(f)
    
    print("Calling Kimi 2.5...")
    kimi_output = call_kimi(data, api_key)
    
    print("Validating output...")
    validation = validate_trade_output(kimi_output, data)
    
    if not validation["passed"]:
        print("VALIDATION ERRORS:")
        for err in validation["errors"]:
            print(f" ✗ {err}")
    
    if validation["warnings"]:
        print("VALIDATION WARNINGS:")
        for w in validation["warnings"]:
            print(f" ⚠ {w}")
    
    # Merge validation into output
    kimi_output["_validation"] = validation
    kimi_output["_source_data_timestamp"] = data.get("generated_at")
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(kimi_output, f, indent=2)
    
    print(f"✓ Trade idea JSON saved to {output_path}")
    return kimi_output

if __name__ == "__main__":
    import os
    
    generate_weekly_report(
        data_json_path = "/home/astra/.openclaw/workspace/data/weekly_trade_data.json",
        api_key = os.environ.get("KIMI_API_KEY", ""),
        output_path = "/home/astra/.openclaw/workspace/data/weekly_trade_ideas.json"
    )
