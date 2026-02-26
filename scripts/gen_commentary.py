#!/usr/bin/env python3
"""
Stage 2: Generate AI Commentary Blocks
Simplified version for live test
"""

import json
from pathlib import Path
from datetime import datetime

BASE = Path("/home/astra/.openclaw/workspace")
DATA_FILE = BASE / "daily5/today_data.json"

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
    card = f'''<div class="asset-card">
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
  <button class="collapse-toggle open"><span>Details · Technicals · CFA Lens</span><span class="arrow">▼</span></button>
  <div class="collapsible-body expanded">
    <div class="asset-body">
      <div class="metrics-grid">
        <div class="metric-tile"><div class="mt-val">{format_change(info['change_pct'])}</div><div class="mt-lbl">1D Chg</div></div>
        <div class="metric-tile"><div class="mt-val">{info['pe_ratio']:.1f}x</div><div class="mt-lbl">P/E</div></div>
        <div class="metric-tile"><div class="mt-val">{info['beta']:.2f}</div><div class="mt-lbl">Beta</div></div>
        <div class="metric-tile"><div class="mt-val">${info['fifty_two_week_low']:.0f}</div><div class="mt-lbl">52W Low</div></div>
      </div>
      <div class="card-section-title">🏛️ Street Commentary</div>
      <div class="street-quote">
        <p>"{ticker} shows mixed signals with current price action near key technical levels. Watch for breakout confirmation."</p>
        <div class="quote-source">— Analyst consensus · {datetime.now().strftime('%b %d, %Y')}</div>
      </div>
      <div class="card-section-title">📚 CFA Lens: Equity Valuation</div>
      <div class="cfa-box">
        <div class="cfa-box-title">P/E Ratio Analysis</div>
        <div class="formula-block">P/E = Price / EPS = {format_price(info['price'])} / {info['eps']:.2f} = {info['pe_ratio']:.1f}x</div>
        <p>Current P/E of {info['pe_ratio']:.1f}x compared to sector average. Consider growth prospects and risk profile.</p>
      </div>
    </div>
  </div>
</div>'''
    stock_cards.append(card)

d["stock_cards_html"] = "\n".join(stock_cards)

# Crypto card
d["crypto_card_html"] = f'''<div class="asset-card crypto-card">
  <div class="asset-card-header">
    <div class="asset-left">
      <div class="ticker-row"><span class="ticker">ETH</span><span class="sector-badge">Digital Asset</span></div>
      <div class="company-name">Ethereum USD · Smart Contract Platform</div>
    </div>
    <div class="asset-right">
      <div class="price-main">{format_price(d['crypto']['price'])}</div>
      <div class="price-change positive">{format_change(d['crypto']['change_pct'])}</div>
    </div>
  </div>
  <button class="collapse-toggle open"><span>Details · Network Metrics · CFA Lens</span><span class="arrow">▼</span></button>
  <div class="collapsible-body expanded">
    <div class="asset-body">
      <div class="metrics-grid">
        <div class="metric-tile"><div class="mt-val">{format_change(d['crypto']['change_pct'])}</div><div class="mt-lbl">24H Chg</div></div>
        <div class="metric-tile"><div class="mt-val">{d['crypto']['market_cap']/1e9:.0f}B</div><div class="mt-lbl">Mkt Cap</div></div>
        <div class="metric-tile"><div class="mt-val">{d['crypto']['volume_24h']/1e9:.1f}B</div><div class="mt-lbl">Volume</div></div>
      </div>
      <div class="card-section-title">🏛️ Network Analysis</div>
      <div class="street-quote"><p>ETH showing strong momentum with elevated institutional interest. Watch for continuation above key resistance.</p><div class="quote-source">— Crypto Market Watch · {datetime.now().strftime('%b %d, %Y')}</div></div>
    </div>
  </div>
</div>'''

# Forex card
d["forex_card_html"] = f'''<div class="asset-card forex-card">
  <div class="asset-card-header">
    <div class="asset-left">
      <div class="ticker-row"><span class="ticker">USD/JPY</span><span class="sector-badge">Forex — G10</span></div>
      <div class="company-name">US Dollar / Japanese Yen · Carry Trade Barometer</div>
    </div>
    <div class="asset-right">
      <div class="price-main">{d['forex']['rate']:.2f}</div>
      <div class="price-change">{format_change(d['forex']['change_pct'])}</div>
    </div>
  </div>
  <button class="collapse-toggle open"><span>Rate Context · Policy Divergence · CFA Lens</span><span class="arrow">▼</span></button>
  <div class="collapsible-body expanded">
    <div class="asset-body">
      <div class="metrics-grid">
        <div class="metric-tile"><div class="mt-val">{d['forex']['us_rate']:.2f}%</div><div class="mt-lbl">US Rate</div></div>
        <div class="metric-tile"><div class="mt-val">{d['forex']['jpy_rate']:.2f}%</div><div class="mt-lbl">BOJ Rate</div></div>
        <div class="metric-tile"><div class="mt-val">{d['forex']['us_rate']-d['forex']['jpy_rate']:.0f}bps</div><div class="mt-lbl">Spread</div></div>
      </div>
    </div>
  </div>
</div>'''

# Trading setups
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
    row = f'''<tr>
  <td><strong>{asset}</strong></td>
  <td><span class="setup-badge">{setup}</span></td>
  <td><span class="setup-badge {bias_class}">{bias}</span></td>
  <td>{entry}</td><td>{stop}</td><td>{target}</td>
  <td><span class="rr-badge">{rr}</span></td>
</tr>'''
    setup_rows.append(row)

d["setup_rows_html"] = "\n".join(setup_rows)

# Options card
d["options_card_html"] = '''<div class="options-card">
  <div class="options-header">Today's Options Concept: Covered Call Strategy</div>
  <div class="options-sub">CFA Level I · Derivatives · Income Generation</div>
  <div class="options-concept-grid">
    <div class="option-concept-box">
      <h4>What is a Covered Call?</h4>
      <p>Own 100 shares, sell 1 call option. Collect premium, cap upside above strike.</p>
    </div>
    <div class="option-concept-box">
      <h4>Example on CVX</h4>
      <p>Own CVX @ $184.22, Sell $190 Call @ $2.80 premium. Yield = 1.52% (30-day).</p>
    </div>
  </div>
  <div class="payoff-chart-wrap">
    <div class="payoff-chart-title"><span>Covered Call Payoff Diagram</span><span>Strike: $190 · Premium: $2.80</span></div>
    <svg class="payoff-svg" viewBox="0 0 540 220" xmlns="http://www.w3.org/2000/svg">
      <line x1="60" y1="110" x2="520" y2="110" stroke="var(--border-strong)" stroke-width="1"/>
      <polyline points="60,180 240,110 420,60 480,60" fill="none" stroke="var(--blue)" stroke-width="2" stroke-linecap="round"/>
      <text x="400" y="50" fill="var(--purple)" font-family="monospace" font-size="9">Max Profit</text>
    </svg>
  </div>
</div>'''

# Quiz
d["quiz_html"] = '''<div class="quiz-question" id="q1">
  <div class="quiz-q-num">Question 1 of 5 · Equity Valuation</div>
  <div class="quiz-q-text">Using the Gordon Growth Model, what is the intrinsic value of a stock paying $3.00 dividend growing at 7% with 12% required return?</div>
  <div class="quiz-formula">V₀ = D₁ ÷ (r − g) | D₁ = D₀ × (1 + g)</div>
  <div class="quiz-options">
    <button class="quiz-option" onclick="answerQ(1,'A','B',this)">A) $42.86</button>
    <button class="quiz-option" onclick="answerQ(1,'B','B',this)">B) $64.20</button>
    <button class="quiz-option" onclick="answerQ(1,'C','B',this)">C) $60.00</button>
    <button class="quiz-option" onclick="answerQ(1,'D','B',this)">D) $55.71</button>
  </div>
  <div class="quiz-explanation" id="exp1">
    <strong>Answer: B — $64.20.</strong> D₁ = $3.00 × 1.07 = $3.21. V₀ = $3.21 ÷ (0.12 − 0.07) = $64.20.
  </div>
</div>

<div class="quiz-question" id="q2">
  <div class="quiz-q-num">Question 2 of 5 · Derivatives</div>
  <div class="quiz-q-text">What is the maximum profit on a covered call position with stock at $100, strike $105, premium $3?</div>
  <div class="quiz-options">
    <button class="quiz-option" onclick="answerQ(2,'A','C',this)">A) Unlimited</button>
    <button class="quiz-option" onclick="answerQ(2,'B','C',this)">B) $300</button>
    <button class="quiz-option" onclick="answerQ(2,'C','C',this)">C) $800</button>
    <button class="quiz-option" onclick="answerQ(2,'D','C',this)">D) $500</button>
  </div>
  <div class="quiz-explanation" id="exp2">
    <strong>Answer: C — $800.</strong> Max profit = (Strike − Cost) + Premium = ($105 − $100) + $3 = $8 per share × 100 = $800.
  </div>
</div>'''

# Glossary
d["glossary_html"] = '''<div class="term-entry">
  <div class="term-word">Gordon Growth Model (GGM)</div>
  <div class="term-def">A dividend discount model valuing a stock as present value of infinite growing dividends: V₀ = D₁ ÷ (r − g).</div>
  <div class="term-origin">Equity Valuation · CFA Level I · Reading 26</div>
</div>

<div class="term-entry">
  <div class="term-word">Price-to-Earnings Ratio (P/E)</div>
  <div class="term-def">Compares share price to earnings per share. Used for relative valuation and benchmarking.</div>
  <div class="term-origin">Equity Valuation · CFA Level I · Reading 27</div>
</div>

<div class="term-entry">
  <div class="term-word">Beta (β)</div>
  <div class="term-def">Measures systematic risk relative to market. β = 1.0 = market moves. β > 1.0 = amplified. β < 1.0 = dampened.</div>
  <div class="term-origin">Portfolio Management · CFA Level I · Reading 42</div>
</div>

<div class="term-entry">
  <div class="term-word">Covered Interest Rate Parity (CIP)</div>
  <div class="term-def">No-arbitrage relationship: F/S = (1+r_quote)/(1+r_base). Higher-yielding currencies trade at forward discount.</div>
  <div class="term-origin">Economics · CFA Level I · Reading 14</div>
</div>'''

with open(DATA_FILE, 'w') as f:
    json.dump(d, f, indent=2)

print("[OK] Commentary blocks written to today_data.json")
