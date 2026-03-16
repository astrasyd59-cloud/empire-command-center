---
name: astra-trade-ops
description: Comprehensive trading operations automation for ASTRA including report generation, position monitoring, database logging, and web dashboard. Use when managing swing trades on Gold, Silver, ES, NQ, AUDUSD, GBPUSD via CMC Markets/City Index. Handles weekly trade reports, overnight price monitoring with Telegram alerts, trade journaling to PostgreSQL, and browsable web dashboard for historical analysis.
---

# ASTRA Trade Operations

Automated trading infrastructure for 4H swing trading with institutional-grade risk management.

## Quick Start

Generate weekly trade report:
```bash
source ~/openclaw_venv/bin/activate
python3 scripts/generate_report.py
```

Monitor open positions overnight:
```bash
python3 scripts/monitor_position.py --asset ES --alert-pct 3.0
```

View dashboard:
```bash
python3 scripts/dashboard_server.py
# Open http://localhost:8080
```

## Workflows

### Weekly Trade Report (Sunday Evening)

1. Fetch 4H data for 6 instruments via yfinance
2. Calculate indicators: EMA 20/50, RSI(14), ATR(14)
3. Detect Murphy patterns (Bull Flag, Double Bottom, etc.)
4. Apply 5-gate validation:
   - Gate 1: Macro clear (VIX, DXY, yields)
   - Gate 2: Trend clear (above/below EMAs)
   - Gate 3: Pattern confirmed
   - Gate 4: R:R ≥ 2:1
   - Gate 5: Position sizing viable
5. Generate HTML report with entry/stop/target levels
6. Save to database and deploy to GitHub Pages

### Overnight Position Monitoring

1. Run via cron every hour during market hours
2. Check current price vs entry price
3. If move ≥ alert threshold: send Telegram notification
4. Log price to database regardless
5. Check for stop loss hits if defined

### Trade Entry Logging

When user enters a trade:
1. Parse entry details (asset, size, direction, rationale)
2. Insert into `trades` table
3. Set up monitoring for that position
4. Log rationale to `astra_notes` table

## Database Schema

See [references/database_schema.md](references/database_schema.md) for full PostgreSQL schema including:
- `trades` table — all entries and exits
- `market_data` table — price candles
- `astra_notes` table — analysis and rationale
- `alerts` table — triggered notifications

## Asset-Macro Correlations

See [references/macro_drivers.md](references/macro_drivers.md) for:
- Gold/Silver → DXY inverse, real yields
- ES/NQ → VIX inverse, 10Y yields
- AUDUSD → DXY, commodity prices, China data
- GBPUSD → DXY, BOE expectations

## Scripts Reference

| Script | Purpose | Frequency |
|--------|---------|-----------|
| `generate_report.py` | Weekly trade analysis | Sunday 8 PM |
| `monitor_position.py` | Price alerts | Every hour |
| `log_to_db.py` | Database operations | On demand |
| `dashboard_server.py` | Web UI | Always on |

## Configuration

Required environment variables:
```bash
export KIMI_API_KEY=""           # Optional, for AI analysis
export TELEGRAM_BOT_TOKEN=""      # For alerts
export TELEGRAM_CHAT_ID=""        # Your Telegram ID
export DB_PASSWORD=""             # PostgreSQL password
```

## Telegram Alert Format

```
🚨 ALERT: ES moved +3.2%
Position: SHORT 0.3 lots
Entry: 6,865
Current: 7,085
P&L: -$660 (unrealized)
Action: Monitor for stop hit
```

## Report Output Locations

- HTML report: `~/.openclaw/workspace/reports/trade_YYYY-MM-DD.html`
- Latest: `~/.openclaw/workspace/reports/latest_trade.html`
- GitHub Pages: `https://[username].github.io/empire-command-center/reports/latest_trade.html`
- Database: `openclaw_db.trades`, `openclaw_db.astra_notes`

## Common Tasks

**Enter a new trade:**
```python
python3 scripts/log_to_db.py --type trade --asset ES --direction SHORT --size 0.3 --entry 6865 --rationale "Weak momentum post-selloff"
```

**Check open positions:**
```bash
psql -U astra_user -d openclaw_db -c "SELECT * FROM trades WHERE status='open';"
```

**View recent notes:**
```bash
psql -U astra_user -d openclaw_db -c "SELECT * FROM astra_notes ORDER BY created_at DESC LIMIT 5;"
```

## Risk Management Rules

Hardcoded in all scripts:
- Stop loss = 1.5 × ATR(14) on 4H
- Max risk per trade = 1% of account
- Minimum R:R = 2:1 for valid setup
- Daily loss limit = 5% of account (kill switch)

## Cron Setup

```bash
# Weekly report — Sunday 8 PM
0 20 * * 0 /home/astra/openclaw_venv/bin/python /home/astra/.openclaw/workspace/skills/astra-trade-ops/scripts/generate_report.py

# Position monitoring — every hour during market hours
0 6-23 * * 1-5 /home/astra/openclaw_venv/bin/python /home/astra/.openclaw/workspace/skills/astra-trade-ops/scripts/monitor_position.py --all-open
```

## Troubleshooting

**"No module named yfinance"**
→ Run: `source ~/openclaw_venv/bin/activate && pip install yfinance pandas numpy requests`

**"Connection refused" to database**
→ Check PostgreSQL: `sudo systemctl status postgresql`

**Gold price looks wrong (e.g., $2,950 instead of $5,200)**
→ yfinance returned wrong contract. Wait 5 min and retry.

## See Also

- [references/trading_glossary.md](references/trading_glossary.md) — Murphy patterns, order types, risk terms
- [references/database_schema.md](references/database_schema.md) — Full SQL schema
- [references/macro_drivers.md](references/macro_drivers.md) — Asset correlations and drivers
