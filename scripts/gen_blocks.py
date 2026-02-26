#!/usr/bin/env python3
"""
Stage 2C: Generate simplified HTML blocks for testing
This creates placeholder HTML blocks so we can test Stage 3 (Python assembler)
"""

import json
from datetime import datetime
from pathlib import Path

BASE = Path("/home/astra/.openclaw/workspace")
DATA_FILE = BASE / "daily5/today_data.json"

# Load data
with open(DATA_FILE) as f:
    d = json.load(f)

def format_price(price):
    return f"${price:,.2f}"

def format_change(pct):
    arrow = "▲" if pct > 0 else "▼"
    return f"{arrow} {pct:+.2f}%"

# Generate simplified stock cards
stock_cards = []
for ticker, info in d["stocks"].items():
    card = f'''
<div class="asset-card">
  <div class="asset-card-header">
    <div class="asset-left">
      <div class="ticker-row"><span class="ticker">{ticker}</span><span class="sector-badge">{info.get("sector", "Unknown")}</span></div>
      <div class="company-name">{info.get("industry", "")}</div>
    </div>
    <div class="asset-right">
      <div class="price-main">{format_price(info["price"])}</div>
      <div class="price-change {'positive' if info['change_pct'] > 0 else 'negative'}">{format_change(info['change_pct'])}</div>
    </div>
  </div>
  <button class="collapse-toggle"><span>Details · Technicals · CFA Lens</span><span class="arrow">▼</span></button>
</div>
'''
    stock_cards.append(card)

d["stock_cards_html"] = "\n".join(stock_cards)

# Generate simplified crypto card
d["crypto_card_html"] = f'''
<div class="asset-card crypto-card">
  <div class="asset-card-header">
    <div class="asset-left">
      <div class="ticker-row"><span class="ticker">{d["crypto"]["ticker"]}</span><span class="sector-badge">Digital Asset</span></div>
      <div class="company-name">Smart Contract Platform</div>
    </div>
    <div class="asset-right">
      <div class="price-main">{format_price(d["crypto"]["price"])}</div>
      <div class="price-change positive">{format_change(d["crypto"]["change_pct"])}</div>
    </div>
  </div>
  <button class="collapse-toggle"><span>Details · Network Metrics · CFA Lens</span><span class="arrow">▼</span></button>
</div>
'''

# Generate simplified forex card
d["forex_card_html"] = f'''
<div class="asset-card forex-card">
  <div class="asset-card-header">
    <div class="asset-left">
      <div class="ticker-row"><span class="ticker">{d["forex"]["pair"]}</span><span class="sector-badge">Forex — G10</span></div>
      <div class="company-name">US Dollar / Japanese Yen</div>
    </div>
    <div class="asset-right">
      <div class="price-main">{d["forex"]["rate"]:.2f}</div>
      <div class="price-change {'positive' if d["forex"]["change_pct"] > 0 else 'negative'}">{format_change(d["forex"]["change_pct"])}</div>
    </div>
  </div>
  <button class="collapse-toggle"><span>Rate Context · Policy Divergence · CFA Lens</span><span class="arrow">▼</span></button>
</div>
'''

# Generate trading setups rows
setups = [
    ("CVX", "Support", "LONG", 181.00, 177.00, 195.00, "3.5:1"),
    ("SBUX", "Mean Rev", "NEUTRAL", 96.00, 91.00, 108.00, "2.4:1"),
    ("ABT", "Trend", "LONG", 113.50, 109.00, 128.00, "3.2:1"),
    ("LOW", "Channel", "LONG", 263.00, 255.00, 295.00, "4.0:1"),
    ("TGT", "Value", "WATCH", 113.00, 108.00, 130.00, "3.4:1"),
    ("ETH", "Momentum", "LONG", 2050, 1900, 2500, "3.0:1"),
    ("USD/JPY", "Range", "SHORT", 158.50, 160.00, 152.00, "4.3:1"),
]

setup_rows = []
for asset, setup, bias, entry, stop, target, rr in setups:
    bias_class = {"LONG": "bias-bull", "SHORT": "bias-bear", "NEUTRAL": "bias-neutral", "WATCH": "bias-neutral"}[bias]
    row = f'''
<tr>
  <td><strong>{asset}</strong></td>
  <td><span class="setup-badge">{setup}</span></td>
  <td><span class="setup-badge {bias_class}">{bias}</span></td>
  <td>{entry}</td><td>{stop}</td><td>{target}</td>
  <td><span class="rr-badge">{rr}</span></td>
</tr>
'''
    setup_rows.append(row)

d["setup_rows_html"] = "\n".join(setup_rows)

# Generate options card
d["options_card_html"] = '''
<div class="options-card">
  <div class="options-header">Today's Options Concept: Covered Call Strategy</div>
  <div class="options-sub">CFA Level I · Derivatives · Income Generation on CVX</div>
  <div class="options-concept-grid">
    <div class="option-concept-box">
      <h4>What is a Covered Call?</h4>
      <p>Own 100 shares of stock, sell 1 call option against it. You collect premium immediately, but cap upside above the strike.</p>
    </div>
    <div class="option-concept-box">
      <h4>Applied to CVX Today</h4>
      <p>Own CVX @ $184.22<br>Sell $190 Call @ $2.80 premium<br>Yield = 1.52% (30-day)</p>
    </div>
  </div>
  <div class="payoff-chart-wrap">
    <div class="payoff-chart-title"><span>Covered Call Payoff Diagram</span><span>Strike: $190 · Premium: $2.80</span></div>
    <svg class="payoff-svg" viewBox="0 0 540 220">
      <line x1="60" y1="110" x2="520" y2="110" stroke="var(--border-strong)" stroke-width="1"/>
      <polyline points="60,180 240,110 480,50" fill="none" stroke="var(--blue)" stroke-width="2"/>
    </svg>
  </div>
</div>
'''

# Generate quiz questions
d["quiz_html"] = '''
<div class="quiz-question" id="q1">
  <div class="quiz-q-num">Question 1 of 5 · Equity Valuation</div>
  <div class="quiz-q-text">Using the Gordon Growth Model, what is the intrinsic value of a stock paying $3.00 dividend growing at 7% with 12% required return?</div>
  <div class="quiz-options">
    <button class="quiz-option">A) $42.86</button>
    <button class="quiz-option">B) $64.20</button>
    <button class="quiz-option">C) $60.00</button>
    <button class="quiz-option">D) $55.71</button>
  </div>
</div>
'''

# Generate glossary
d["glossary_html"] = '''
<div class="term-entry">
  <div class="term-word">Gordon Growth Model</div>
  <div class="term-def">A dividend discount model that values a stock as the present value of an infinite stream of growing dividends: V₀ = D₁ ÷ (r − g).</div>
  <div class="term-origin">Equity Valuation · CFA Level I · Reading 26</div>
</div>
<div class="term-entry">
  <div class="term-word">P/E Ratio</div>
  <div class="term-def">Price-to-Earnings ratio compares a company's share price to its earnings per share. Used for relative valuation.</div>
  <div class="term-origin">Equity Valuation · CFA Level I · Reading 27</div>
</div>
'''

# Write updated data
with open(DATA_FILE, 'w') as f:
    json.dump(d, f, indent=2)

print("[OK] HTML blocks generated")
print(f"[OK] Data file updated: {DATA_FILE}")
print(f"[OK] Stock cards: {len(stock_cards)}")
print(f"[OK] Setup rows: {len(setup_rows)}")
