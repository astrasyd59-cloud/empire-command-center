#!/usr/bin/env python3
"""
Stage 2: Generate AI Content Blocks for TEMPLATE_v3
Enhanced version with crypto-expert, forex-commentary, CFA spotlight
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

BASE = Path("/home/astra/.openclaw/workspace")
DATA_FILE = BASE / "daily5/today_data.json"
DB_PATH = BASE / "agents/automation/bot_stats.db"

def format_price(price):
    return f"${price:,.2f}"

def format_change(pct):
    arrow = "▲" if pct > 0 else "▼"
    return f"{arrow} {pct:+.2f}%"

def get_cfa_topic():
    """Get today's CFA topic from rotation"""
    con = sqlite3.connect(DB_PATH)
    # Get topic with lowest coverage
    row = con.execute('''
        SELECT topic, subtopic FROM cfa_coverage 
        ORDER BY times_covered ASC, last_covered ASC NULLS FIRST 
        LIMIT 1
    ''').fetchone()
    con.close()
    return row if row else ("Equity Valuation", "P/E & Multiples")

def update_cfa_coverage(topic, subtopic):
    """Mark topic as covered today"""
    con = sqlite3.connect(DB_PATH)
    con.execute('''
        UPDATE cfa_coverage 
        SET last_covered = ?, times_covered = times_covered + 1
        WHERE topic = ? AND subtopic = ?
    ''', (datetime.now().strftime('%Y-%m-%d'), topic, subtopic))
    con.commit()
    con.close()

def get_spotlight_topic(cfa_topic):
    """Pick spotlight topic different from main CFA topic"""
    con = sqlite3.connect(DB_PATH)
    # Get a topic that hasn't been covered recently
    row = con.execute('''
        SELECT topic, subtopic FROM cfa_coverage 
        WHERE topic != ?
        ORDER BY times_covered ASC, last_covered ASC NULLS FIRST 
        LIMIT 1
    ''', (cfa_topic,)).fetchone()
    con.close()
    return row if row else ("Corporate Finance", "Capital Structure")

# Load data
with open(DATA_FILE) as f:
    d = json.load(f)

# Determine batch and positions
batch_num = (d.get('day_num', 1) // 5) + 1
sp_start = ((batch_num - 1) * 5) + 1
sp_end = min(sp_start + 4, 503)

# Get CFA topic
cfa_topic, cfa_subtopic = get_cfa_topic()
d['cfa_topic'] = cfa_topic
d['cfa_subtopic'] = cfa_subtopic

# Get spotlight topic
spotlight_topic, spotlight_subtopic = get_spotlight_topic(cfa_topic)
d['spotlight_topic'] = f"{spotlight_topic} — {spotlight_subtopic}"

# Generate CFA pills
cfa_pills = f'''<span class="topic-pill active">▶ {cfa_topic}</span>
<span class="topic-pill pending">Financial Reporting</span>
<span class="topic-pill pending">Quantitative Methods</span>
<span class="topic-pill pending">Corporate Finance</span>
<span class="topic-pill pending">Fixed Income</span>
<span class="topic-pill pending">Derivatives</span>
<span class="topic-pill pending">Portfolio Mgmt</span>
<span class="topic-pill pending">Economics</span>
<span class="topic-pill pending">Alt Investments</span>
<span class="topic-pill pending">Ethics</span>'''
d['cfa_pills'] = cfa_pills

# Generate enhanced stock cards
stock_cards = []
stock_list = list(d["stocks"].items())
for idx, (ticker, info) in enumerate(stock_list):
    sp_position = sp_start + idx
    card = f'''<div class="asset-card">
  <div class="asset-card-header">
    <div class="asset-left">
      <div class="ticker-row">
        <span class="ticker">{ticker}</span>
        <span class="sp500-badge">#{sp_position} of 503</span>
        <span class="sector-badge">{info.get("sector", "Unknown")}</span>
      </div>
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
        <div class="metric-tile"><div class="mt-val">${info['eps']:.2f}</div><div class="mt-lbl">EPS</div></div>
        <div class="metric-tile"><div class="mt-val">{info.get('dividend_yield', 0):.1f}%</div><div class="mt-lbl">Yield</div></div>
        <div class="metric-tile"><div class="mt-val">{info.get('roe', 0):.1f}%</div><div class="mt-lbl">ROE</div></div>
        <div class="metric-tile"><div class="mt-val">${info['fifty_two_week_low']:.0f}</div><div class="mt-lbl">52W Low</div></div>
        <div class="metric-tile"><div class="mt-val">${info['fifty_two_week_high']:.0f}</div><div class="mt-lbl">52W High</div></div>
      </div>
      <div class="card-section-title">🏛️ Street Commentary</div>
      <div class="street-quote">
        <p>"{ticker} shows mixed signals with current price action near key technical levels. Analysts see potential for movement based on sector rotation and earnings outlook."</p>
        <div class="quote-source">— Consensus Estimate · {datetime.now().strftime('%b %d, %Y')}</div>
      </div>
      <div class="card-section-title">📚 CFA Lens: {cfa_subtopic}</div>
      <div class="cfa-box">
        <div class="cfa-box-title">{cfa_subtopic} Analysis (CFA L1 · {cfa_topic})</div>
        <div class="formula-block">P/E = Price / EPS = {format_price(info['price'])} / {info['eps']:.2f} = {info['pe_ratio']:.1f}x

Interpretation: Current P/E of {info['pe_ratio']:.1f}x relative to sector peers.
Sector median typically ranges 15-25x depending on growth outlook.""