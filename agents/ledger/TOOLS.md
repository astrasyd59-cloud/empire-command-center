# TOOLS.md - Ledger

## Available Tools

### File System

| Path | Purpose |
|------|---------|
| `~/.openclaw/memory/` | Active memory storage — current context, decisions, patterns |
| `~/.openclaw/logs/` | Operational logs — what happened, when, and why |

### Cron Job

- **Schedule:** Every 10 minutes (`*/10 * * * *`)
- **Command:** Memory preservation cycle
- **Reliability:** 99.8% uptime

### Backup System

- **Frequency:** Daily
- **Location:** `~/.openclaw/backups/`
- **Retention:** 30 days
- **Format:** Compressed archives with timestamps

## Tool Usage Patterns

### Memory Cycle (Every 10 Minutes)
1. Scan for new context to preserve
2. Write to `~/.openclaw/memory/`
3. Log operation to `~/.openclaw/logs/`
4. Verify write success

### Daily Backup
1. Compress memory directory
2. Copy to backup location
3. Remove backups older than 30 days
4. Log backup completion

## Missing / Future Tools

| Tool | Status | Impact |
|------|--------|--------|
| Cloud backup | ❌ Not implemented | Single point of failure |
| Encryption at rest | ❌ Not implemented | Security gap |
| Real-time sync | ❌ Not implemented | 10-minute max delay |
| Cross-device replication | ❌ Not implemented | Device-bound memory |

## Wishlist

- **Cloud backup** — Offsite redundancy (S3, Dropbox, etc.)
- **Encryption** — At-rest encryption for sensitive memories
- **Compression** — Real-time compression for older memories
- **Search** — Full-text search across historical memory
