# Database Schema

Complete PostgreSQL schema for ASTRA trading operations.

## Tables

### trades

Stores all trade entries and exits.

```sql
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    asset VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL, -- BUY or SELL
    entry_price DECIMAL(18, 8) NOT NULL,
    exit_price DECIMAL(18, 8),
    size DECIMAL(18, 8) NOT NULL,
    pnl DECIMAL(18, 8),
    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_time TIMESTAMP,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'open' -- open, closed, cancelled
);
```

**Example queries:**

```sql
-- All open trades
SELECT * FROM trades WHERE status = 'open';

-- Closed trades this month
SELECT * FROM trades 
WHERE status = 'closed' 
  AND exit_time >= DATE_TRUNC('month', CURRENT_DATE);

-- Win rate
SELECT 
    COUNT(*) as total_trades,
    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
    ROUND(100.0 * SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate
FROM trades WHERE status = 'closed';
```

### market_data

Stores price candles for analysis.

```sql
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    asset VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL, -- 1m, 5m, 15m, 1h, 4h, 1d
    open DECIMAL(18, 8) NOT NULL,
    high DECIMAL(18, 8) NOT NULL,
    low DECIMAL(18, 8) NOT NULL,
    close DECIMAL(18, 8) NOT NULL,
    volume DECIMAL(18, 8) NOT NULL,
    timestamp TIMESTAMP NOT NULL
);
```

**Example queries:**

```sql
-- Latest price for each asset
SELECT DISTINCT ON (asset) asset, close, timestamp
FROM market_data ORDER BY asset, timestamp DESC;

-- 4H candles for Gold last 7 days
SELECT * FROM market_data 
WHERE asset = 'GC=F' AND timeframe = '4h'
  AND timestamp >= NOW() - INTERVAL '7 days'
ORDER BY timestamp DESC;
```

### astra_notes

Stores analysis, rationale, and observations.

```sql
CREATE TABLE astra_notes (
    id SERIAL PRIMARY KEY,
    note_type VARCHAR(50) NOT NULL, -- analysis, alert, review
    content TEXT NOT NULL,
    related_asset VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Example queries:**

```sql
-- Recent analysis on Gold
SELECT * FROM astra_notes 
WHERE related_asset = 'GOLD' AND note_type = 'analysis'
ORDER BY created_at DESC LIMIT 5;

-- All notes from today
SELECT * FROM astra_notes 
WHERE created_at >= CURRENT_DATE
ORDER BY created_at DESC;
```

### alerts (optional)

Stores triggered alerts for audit trail.

```sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    trade_id INTEGER REFERENCES trades(id),
    alert_type VARCHAR(50) NOT NULL, -- price_move, stop_hit, target_hit
    message TEXT NOT NULL,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent BOOLEAN DEFAULT FALSE
);
```

## Indexes

```sql
-- Speed up common queries
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_trades_asset ON trades(asset);
CREATE INDEX idx_trades_entry_time ON trades(entry_time);
CREATE INDEX idx_market_data_asset_time ON market_data(asset, timestamp);
CREATE INDEX idx_astra_notes_asset ON astra_notes(related_asset);
CREATE INDEX idx_astra_notes_created ON astra_notes(created_at);
```

## Backup

```bash
# Export database
pg_dump -U astra_user openclaw_db > backup_$(date +%Y%m%d).sql

# Import database
psql -U astra_user openclaw_db < backup_20260224.sql
```

## Connection

```python
import psycopg2

conn = psycopg2.connect(
    dbname='openclaw_db',
    user='astra_user',
    password='astra2026secure',
    host='localhost',
    port='5432'
)
```
