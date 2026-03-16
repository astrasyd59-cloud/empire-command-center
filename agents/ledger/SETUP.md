# Ledger Agent Setup Instructions

## Quick Setup

### 1. Install Cron Job

Run this command to install Ledger's automated maintenance:

```bash
crontab -e
```

Add this line:
```
*/30 * * * * /home/astra/.openclaw/workspace/agents/ledger/ledger-maintenance.sh
```

### 2. Verify Installation

```bash
# Check cron is installed
crontab -l

# Test the script manually
/home/astra/.openclaw/workspace/agents/ledger/ledger-maintenance.sh

# Check the log
tail /home/astra/.openclaw/workspace/memory/system-health.log
```

### 3. Optional: Configure Notion API Check

Create `.notion-token` file for automated health checks:

```bash
echo "your_notion_integration_token" > /home/astra/.openclaw/workspace/.notion-token
chmod 600 /home/astra/.openclaw/workspace/.notion-token
```

### 4. Optional: Configure Discord Webhook Check

Create `.discord-webhook` file:

```bash
echo "your_discord_webhook_url" > /home/astra/.openclaw/workspace/.discord-webhook
chmod 600 /home/astra/.openclaw/workspace/.discord-webhook
```

## Manual Operations

### Force Memory Update
```bash
/home/astra/.openclaw/workspace/agents/ledger/ledger-maintenance.sh
```

### Archive Old Logs
```bash
find /home/astra/.openclaw/workspace/memory -name "*.md" -mtime +7 -exec mv {} /home/astra/.openclaw/workspace/memory/archive/ \;
```

### View System Health
```bash
tail /home/astra/.openclaw/workspace/memory/system-health.log
```

## Troubleshooting

### Script Not Running
1. Check permissions: `ls -la agents/ledger/ledger-maintenance.sh`
2. Should be executable: `-rwxr-xr-x`
3. Fix with: `chmod +x agents/ledger/ledger-maintenance.sh`

### Cron Not Working
1. Check cron service: `systemctl status cron`
2. Check user crontab: `crontab -l`
3. Check system logs: `grep CRON /var/log/syslog`

### Memory File Issues
1. Check disk space: `df -h`
2. Check file permissions: `ls -la memory/`
3. Ensure directory exists: `mkdir -p memory/archive`

## Files Created

| File | Purpose |
|------|---------|
| `agents/ledger/SOUL.md` | Ledger's identity and purpose |
| `agents/ledger/ledger-maintenance.sh` | Automated maintenance script |
| `memory/2026-02-20.md` | Today's memory log |
| `MISSION.md` | Current mission tracker |
| `memory/archive/` | Archive directory for old logs |
