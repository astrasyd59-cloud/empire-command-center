---
name: trading-journal
description: Tracks Dibs's trading activity — entries, exits, P&L, and trade reviews. Stores trades as structured data (JSON/CSV) and generates periodic performance reports. Helps identify patterns, track progress toward $100+ trades, and maintain accountability.
user-invocable: true
---

# Trading Journal Skill

## Purpose

Every trade Dibs makes gets logged. No exceptions. Small trades ($10-15) now build the discipline for larger trades later. This skill tracks:

- Entry/exit prices, position size, stop/target
- P&L (realized and unrealized)
- Trade rationale (setup, conviction level)
- Post-trade review (what worked, what didn't)
- Performance metrics (win rate, R-multiple, expectancy)

---

## Quick Commands

### Log a new trade
```bash
python3 ~/.openclaw/workspace/skills/trading-journal/scripts/log_trade.py \
  --symbol "AAPL" \
  --direction "LONG" \
  --entry 175.50 \
  --stop 172.00 \
  --target 182.00 \
  --size 100 \
  --setup "Breakout above resistance" \
  --conviction 7 \
  --notes "Earnings next week, keeping size small"
```

### Close a trade
```bash
python3 ~/.openclaw/workspace/skills/trading-journal/scripts/close_trade.py \
  --trade-id 42 \
  --exit-price 180.25 \
  --exit-notes "Hit target, strong momentum"
```

### View open positions
```bash
python3 ~/.openclaw/workspace/skills/trading-journal/scripts/list_trades.py --open
```

### Generate weekly report
```bash
python3 ~/.openclaw/workspace/skills/trading-journal/scripts/weekly_report.py
```

### Get P&L summary
```bash
python3 ~/.openclaw/workspace/skills/trading-journal/scripts/pnl_summary.py --this-week
```

---

## Trade Data Structure

Each trade is stored as JSON:

```json
{
  "trade_id": 42,
  "date_opened": "2026-03-15",
  "time_opened": "09:30:00",
  "symbol": "AAPL",
  "direction": "LONG",
  "entry_price": 175.50,
  "position_size": 100,
  "stop_loss": 172.00,
  "target": 182.00,
  "risk_per_share": 3.50,
  "total_risk": 350.00,
  "setup": "Breakout above resistance",
  "conviction": 7,
  "notes_open": "Earnings next week, keeping size small",
  "status": "OPEN",
  "date_closed": null,
  "time_closed": null,
  "exit_price": null,
  "pnl_dollars": null,
  "pnl_percent": null,
  "r_multiple": null,
  "notes_close": null,
  "reviewed": false
}
```

---

## Astra's Protocol

### When Dibs mentions a trade

**Ask these questions (every time):**
1. Symbol and direction (LONG/SHORT)?
2. Entry price and position size?
3. Stop loss and target?
4. What's the setup? (breakout, pullback, earnings, etc.)
5. Conviction level (1-10)?

Then: Log it immediately. Confirm with trade ID.

### When Dibs closes a trade

Ask:
1. Which trade (symbol or ID)?
2. Exit price?
3. Why exit? (target hit, stop hit, manual, news)

Then: Update the trade, calculate P&L, show R-multiple.

### Weekly Review (Sundays)

Generate report covering:
- Total trades taken
- Win rate
- Average R-multiple
- Best/worst trade
- Pattern: What setups worked? What didn't?
- Progress toward $100+ average trade size

---

## Storage

**Location:** `~/.openclaw/workspace/trading/journal/`

```
trading/
├── journal/
│   ├── trades/
│   │   ├── 2026-03-15_trade_001.json
│   │   ├── 2026-03-15_trade_002.json
│   │   └── ...
│   ├── weekly_reports/
│   │   ├── 2026-week-11.html
│   │   └── ...
│   └── summary.csv
```

---

## Progress Tracking

Dibs's goal: Build to $100+ trades consistently

**Current baseline:** $10-15 profit per trade
**Target:** $100+ average profit per trade
**Milestone tracking:**
- ✅ $10-20 trades (current)
- ⏳ $25-50 trades
- ⏳ $50-75 trades  
- ⏳ $75-100 trades
- ⏳ $100+ trades (target)

Report milestone progress in weekly reviews.

---

## Rules

1. **Log EVERY trade.** No exceptions. Small trades matter for pattern recognition.
2. **Define stop/target before entry.** No undefined risk trades.
3. **Review every Sunday.** Non-negotiable.
4. **Be honest in notes.** "FOMO entry" is a valid note. Learn from it.
5. **Track conviction levels.** See if high-conviction trades perform better.

---

## Integration with Daily 5

When Daily 5 generates trade setups, copy relevant ones to the journal watchlist. If Dibs takes the trade, link it to the Daily 5 batch number for tracking.

---

*Skill version: 1.0 | Created: March 15, 2026*
