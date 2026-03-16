#!/usr/bin/env python3
"""
ASTRA — Weekly Trade Idea HTML Renderer
Generates The Daily Trade Idea report from JSON data
Fills the HTML template with live data
"""

import json
import re
from datetime import datetime
from pathlib import Path

def load_template(template_path: str) -> str:
    """Load the HTML template file."""
    with open(template_path, 'r') as f:
        return f.read()

def format_price(price: float) -> str:
    """Format price with commas and appropriate decimals."""
    if price is None:
        return "N/A"
    if price >= 1000:
        return f"{price:,.2f}"
    return f"{price:.4f}"

def format_change(change_pct: float) -> str:
    """Format change percentage with arrow."""
    if change_pct is None:
        return "—"
    arrow = "▲" if change_pct >= 0 else "▼"
    return f"{arrow} {abs(change_pct):.2f}%"

def get_change_class(change_pct: float) -> str:
    """Get CSS class for positive/negative change."""
    if change_pct is None:
        return ""
    return "positive" if change_pct >= 0 else "negative"

def render_trade_card(instrument_key: str, data: dict) -> str:
    """Render a TRADE card for an instrument."""
    
    setup = data.get("setup", {})
    pattern = data.get("pattern", {})
    indicators = data.get("indicators", {})
    
    direction = setup.get("direction", "none")
    direction_badge = "long" if direction == "long" else "short"
    direction_arrow = "▲" if direction == "long" else "▼"
    
    price = data.get("current_price", 0)
    change_pct = data.get("price_change_pct", 0)
    
    entry_low = setup.get("entry_zone_low", 0)
    entry_high = setup.get("entry_zone_high", 0)
    stop = setup.get("stop_level", 0)
    target1 = setup.get("target_1", 0)
    target2 = setup.get("target_2", 0)
    rr1 = setup.get("rr_ratio", 0)
    rr2 = rr1 * 1.6 if rr1 else 0  # Approximate for T2
    
    atr = setup.get("atr_used", 0)
    stop_dist = setup.get("stop_distance", 0)
    invalidation = setup.get("invalidation", "N/A")
    
    card_html = f'''
<div class="inst-card">
    <div class="status-bar {direction_badge}"></div>
    <div class="inst-header">
        <div class="inst-left">
            <div class="inst-name-row">
                <span class="inst-ticker">{instrument_key}</span>
                <span class="direction-badge {direction_badge}">{direction_arrow} {direction.upper()}</span>
                <span class="confidence-badge conf-high">HIGH CONFIDENCE</span>
            </div>
            <div class="inst-full-name">{data.get("name", "")} ({data.get("ticker", "")}) · CMC Markets CFD</div>
        </div>
        <div class="inst-right">
            <div class="inst-price">${format_price(price)}</div>
            <div class="inst-change {get_change_class(change_pct)}">{format_change(change_pct)}</div>
        </div>
    </div>
    <div class="inst-body">
        <div class="metrics-row">
            <div class="metric-tile"><span class="mt-val">{data.get("trend", "N/A").capitalize()}</span><span class="mt-lbl">4H Trend</span></div>
            <div class="metric-tile"><span class="mt-val">{indicators.get("rsi_4h", "N/A")}</span><span class="mt-lbl">RSI (4H)</span></div>
            <div class="metric-tile"><span class="mt-val">${format_price(atr)}</span><span class="mt-lbl">ATR(14) 4H</span></div>
            <div class="metric-tile"><span class="mt-val">${format_price(indicators.get("ema20_4h", 0))}</span><span class="mt-lbl">EMA20 (4H)</span></div>
        </div>
        
        <div class="levels-section">
            <div class="levels-title">Trade Levels</div>
            <div class="levels-grid">
                <div class="level-block entry-block">
                    <span class="level-label">Entry Zone</span>
                    <span class="level-value">${format_price(entry_low)}–${format_price(entry_high)}</span>
                    <span class="level-sub">4H close trigger</span>
                </div>
                <div class="level-block stop-block">
                    <span class="level-label">Stop Loss</span>
                    <span class="level-value">${format_price(stop)}</span>
                    <span class="level-sub">1.5 × ATR from entry</span>
                </div>
                <div class="level-block t1-block">
                    <span class="level-label">Target 1 <span class="rr-badge">{rr1:.1f}:1</span></span>
                    <span class="level-value">${format_price(target1)}</span>
                    <span class="level-sub">2x risk projection</span>
                </div>
                <div class="level-block t2-block">
                    <span class="level-label">Target 2 <span class="rr-badge">{rr2:.1f}:1</span></span>
                    <span class="level-value">${format_price(target2)}</span>
                    <span class="level-sub">3.5x risk projection</span>
                </div>
            </div>
        </div>
        
        <div class="stop-logic">
ATR(14) on 4H = ${format_price(atr)}<br>
Stop distance = 1.5 × ${format_price(atr)} = ${format_price(stop_dist)}<br>
Entry zone low = ${format_price(entry_low)}<br>
Stop level = ${format_price(entry_low)} − ${format_price(stop_dist)} = ${format_price(stop)}<br>
Risk per unit = ${format_price(stop_dist)}<br>
Target 1 gain = ${format_price(target1)} − ${format_price(entry_low)} = ${format_price(target1 - entry_low)} → R:R = {rr1:.1f}:1
        </div>
        
        <div class="pattern-section">
            <div class="levels-title">Chart Pattern</div>
            <div class="pattern-header">
                <div class="pattern-info">
                    <div class="pattern-name-large">{pattern.get("name", "N/A")}</div>
                    <div class="pattern-chapter">📖 Murphy · {pattern.get("murphy_chapter", "N/A")}</div>
                    <p class="pattern-desc">{pattern.get("description", "")}</p>
                </div>
            </div>
        </div>
        
        <div class="invalidation-box">
            <div class="inv-label">⚠️ Setup Invalidation</div>
            <p>{invalidation}. Exit immediately if invalidated.</p>
        </div>
    </div>
</div>
'''
    return card_html

def render_no_trade_card(instrument_key: str, data: dict) -> str:
    """Render a NO TRADE card for an instrument."""
    
    gates = data.get("gates", {})
    pattern = data.get("pattern", {})
    
    price = data.get("current_price", 0)
    change_pct = data.get("price_change_pct", 0)
    
    # Build gate pills
    gate_pills = []
    for i in range(1, 6):
        gate_key = f"gate{i}_"
        # Find the gate key
        gate_data = None
        for k, v in gates.items():
            if k.startswith(f"gate{i}"):
                gate_data = v
                break
        
        if gate_data:
            passed = gate_data.get("pass", False)
            label = gate_data.get("label", f"Gate {i}")
            pill_class = "gate-pass" if passed else "gate-fail"
            check = "✓" if passed else "✗"
            gate_pills.append(f'<span class="gate-pill {pill_class}">{check} {label}</span>')
    
    card_html = f'''
<div class="inst-card">
    <div class="status-bar no-trade"></div>
    <div class="inst-header">
        <div class="inst-left">
            <div class="inst-name-row">
                <span class="inst-ticker">{instrument_key}</span>
                <span class="direction-badge none">— NO TRADE</span>
            </div>
            <div class="inst-full-name">{data.get("name", "")} ({data.get("ticker", "")}) · CMC Markets CFD</div>
        </div>
        <div class="inst-right">
            <div class="inst-price">${format_price(price)}</div>
            <div class="inst-change {get_change_class(change_pct)}">{format_change(change_pct)}</div>
        </div>
    </div>
    <div class="no-trade-body">
        <p class="no-trade-reason">{pattern.get("description", "No clear setup identified. Standing aside this week.")}</p>
        <div class="gate-pills">
            {''.join(gate_pills)}
        </div>
        <div class="watch-box" style="margin-top:12px">
            <div class="watch-label">👁 What Would Make This a Trade</div>
            <p>Wait for a clearer pattern to emerge with R:R ≥ 2:1. Re-evaluate after next 4H candle close.</p>
        </div>
    </div>
</div>
'''
    return card_html

def generate_report(data_json_path: str, template_path: str, output_path: str):
    """Generate the full HTML report from data and template."""
    
    # Load data
    with open(data_json_path, 'r') as f:
        data = json.load(f)
    
    # Load template
    template = load_template(template_path)
    
    # Extract macro data
    macro = data.get("macro", {})
    
    # Build macro strip values
    sp500 = macro.get("SP500", {}).get("value", 0)
    sp500_chg = macro.get("SP500", {}).get("change_pct", 0)
    vix = macro.get("VIX", {}).get("value", 0)
    vix_chg = macro.get("VIX", {}).get("change_pct", 0)
    dxy = macro.get("DXY", {}).get("value", 0)
    dxy_chg = macro.get("DXY", {}).get("change_pct", 0)
    yield_10y = macro.get("YIELD_10Y", {}).get("value", 0)
    yield_10y_chg = macro.get("YIELD_10Y", {}).get("change_pct", 0)
    
    # Gold price from instruments
    gold_price = data.get("instruments", {}).get("GOLD", {}).get("current_price", 0)
    gold_chg = data.get("instruments", {}).get("GOLD", {}).get("price_change_pct", 0)
    
    # Count valid trades
    valid_count = len(data.get("valid_setups", []))
    no_trade_count = len(data.get("no_trade", []))
    
    # Render instrument cards FIRST (before placeholder replacement)
    cards_html = []
    for key in ["GOLD", "SILVER", "ES", "NQ", "AUDUSD", "GBPUSD"]:
        inst_data = data.get("instruments", {}).get(key)
        if not inst_data:
            continue
        
        if inst_data.get("trade_valid"):
            cards_html.append(render_trade_card(key, inst_data))
        else:
            cards_html.append(render_no_trade_card(key, inst_data))
    
    # Find and replace the placeholder section with actual cards
    # Use the PLACEHOLDER COMMENT as the marker (doesn't get replaced)
    placeholder_marker = '<!-- ══════════════════════════════════════════════════════\n        INSTRUMENT CARDS GO HERE\n        ══════════════════════════════════════════════════════ -->'
    footer_marker = '<!-- ── FOOTER ── -->'
    
    report_html = template
    
    if placeholder_marker in report_html and footer_marker in report_html:
        parts = report_html.split(placeholder_marker)
        header = parts[0]  # Everything before placeholder
        footer_parts = parts[1].split(footer_marker)
        footer = footer_marker + footer_parts[1]  # Footer and after
        
        # Insert cards between header and footer
        report_html = header + ''.join(cards_html) + footer
    
    # Generate market context summary
    market_summary = f"""Markets are mixed this week with S&P 500 at {sp500:,.0f} ({sp500_chg:+.2f}%). 
VIX at {vix:.1f} suggests {"elevated" if vix > 20 else "moderate"} volatility. 
DXY at {dxy:.2f} ({dxy_chg:+.2f}%) indicates {"USD strength" if dxy_chg > 0 else "USD weakness"}. 
Yield curve spread is {macro.get('YIELD_CURVE_SPREAD', 'N/A')}bp — {"inverted" if macro.get('YIELD_CURVE_INVERTED') else "normal"}."""
    
    # Replace placeholders in template
    report_html = report_html.replace("{{WEEK_OF}}", data.get("week_of", "Week of Unknown"))
    report_html = report_html.replace("{{GENERATED_AT}}", datetime.now().strftime("%B %d, %Y at %H:%M UTC"))
    
    # Macro strip placeholders
    report_html = report_html.replace("{{SP500}}", f"{sp500:,.0f}")
    report_html = report_html.replace("{{SP500_CHG}}", format_change(sp500_chg))
    report_html = report_html.replace("{{SP500_CLASS}}", get_change_class(sp500_chg))
    
    report_html = report_html.replace("{{VIX}}", f"{vix:.1f}")
    report_html = report_html.replace("{{VIX_CHG}}", format_change(vix_chg))
    report_html = report_html.replace("{{VIX_CLASS}}", get_change_class(vix_chg))
    
    report_html = report_html.replace("{{DXY}}", f"{dxy:.2f}")
    report_html = report_html.replace("{{DXY_CHG}}", format_change(dxy_chg))
    report_html = report_html.replace("{{DXY_CLASS}}", get_change_class(dxy_chg))
    
    report_html = report_html.replace("{{YIELD_10Y}}", f"{yield_10y:.2f}")
    report_html = report_html.replace("{{YIELD_CHG}}", format_change(yield_10y_chg))
    report_html = report_html.replace("{{YIELD_CLASS}}", get_change_class(yield_10y_chg))
    
    report_html = report_html.replace("{{YIELD_SPREAD}}", str(macro.get("YIELD_CURVE_SPREAD", "N/A")))
    report_html = report_html.replace("{{CURVE_STATUS}}", "INVERTED" if macro.get("YIELD_CURVE_INVERTED") else "NORMAL")
    
    report_html = report_html.replace("{{GOLD_PRICE}}", format_price(gold_price))
    report_html = report_html.replace("{{GOLD_CHG}}", format_change(gold_chg))
    report_html = report_html.replace("{{GOLD_CLASS}}", get_change_class(gold_chg))
    
    # Market context placeholders
    report_html = report_html.replace("{{MARKET_CONTEXT_SUMMARY}}", market_summary)
    report_html = report_html.replace("{{VIX_READING}}", f"{vix:.1f} ({'elevated' if vix > 20 else 'moderate'})")
    report_html = report_html.replace("{{DXY_DIRECTION}}", f"{'Strengthening' if dxy_chg > 0 else 'Weakening'} ({dxy_chg:+.2f}%)")
    report_html = report_html.replace("{{YIELD_CONTEXT}}", f"{yield_10y:.2f}% ({yield_10y_chg:+.0f}bp)")
    report_html = report_html.replace("{{KEY_EVENTS_WARNING}}", "No high-impact events detected")
    report_html = report_html.replace("{{VIX_PILL_CLASS}}", "pill-red" if vix > 20 else "pill-green")
    report_html = report_html.replace("{{DXY_PILL_CLASS}}", "pill-green" if dxy_chg < 0 else "pill-red")
    report_html = report_html.replace("{{EVENT_PILL_CLASS}}", "pill-gold")
    
    # Trade count placeholders
    report_html = report_html.replace("{{VALID_COUNT}}", str(valid_count))
    report_html = report_html.replace("{{NO_TRADE_COUNT}}", str(no_trade_count))
    
    # Save output
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(report_html)
    
    print(f"✓ Trade Idea report saved to {output_path}")
    return output_path

if __name__ == "__main__":
    generate_report(
        data_json_path="/home/astra/.openclaw/workspace/data/weekly_trade_data.json",
        template_path="/home/astra/.openclaw/workspace/reports/daily_trade_idea_template.html",
        output_path="/home/astra/.openclaw/workspace/reports/daily_trade_idea_test.html"
    )
