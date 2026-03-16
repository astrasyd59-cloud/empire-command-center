#!/bin/bash
# Ledger Memory Maintenance Script
# Run every 30 minutes via cron
# Usage: */30 * * * * /home/astra/.openclaw/workspace/agents/ledger/ledger-maintenance.sh

WORKSPACE="/home/astra/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
LOG_FILE="$MEMORY_DIR/system-health.log"

# Ensure today's memory file exists
if [ ! -f "$MEMORY_DIR/$DATE.md" ]; then
    cat > "$MEMORY_DIR/$DATE.md" << EOF
# Memory Log - $DATE

## Session Start: $TIME
## Last Update: $TIME (by Ledger - Automated)

### Current Mission
[See MISSION.md]

### Activities Log
- [$TIME] Automated check-in

### Key Decisions
- None recorded

### Blockers
- [ ] None recorded

### Action Items (Next Session)
- [ ] Awaiting user input

### System Health
- Status: Automated check at $TIME
EOF
fi

# Update the "Last Update" timestamp
sed -i "s/## Last Update:.*/## Last Update: $TIME (by Ledger - Automated)/" "$MEMORY_DIR/$DATE.md"

# Check Notion API (if credentials exist)
NOTION_STATUS="⏳ Not configured"
if [ -f "$HOME/.openclaw/credentials/notion.env" ]; then
    # Extract token from env file
    NOTION_TOKEN=$(grep -o 'ntn_[^"]*' "$HOME/.openclaw/credentials/notion.env" 2>/dev/null | head -1)
    # Real-time API test
    if [ -n "$NOTION_TOKEN" ]; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
            "https://api.notion.com/v1/users/me" \
            -H "Authorization: Bearer $NOTION_TOKEN" \
            -H "Notion-Version: 2022-06-28" 2>/dev/null)
        if [ "$HTTP_CODE" = "200" ]; then
            NOTION_STATUS="✅ Operational"
        else
            NOTION_STATUS="❌ HTTP $HTTP_CODE (check token)"
        fi
    fi
fi

# Check Discord (if webhook configured)
DISCORD_STATUS="⏳ Not configured"
if [ -f "$WORKSPACE/.discord-webhook" ]; then
    DISCORD_STATUS="🟡 Webhook present (not tested)"
fi

# Log system health
{
    echo "[$DATE $TIME] System Health Check"
    echo "  - Notion API: $NOTION_STATUS"
    echo "  - Discord: $DISCORD_STATUS"
    echo "  - Memory file: $DATE.md"
    echo ""
} >> "$LOG_FILE"

# Update system health section in today's memory file
sed -i "/### System Health/,/---/{s/- Notion API:.*/- Notion API: $NOTION_STATUS/; s/- Discord:.*/- Discord: $DISCORD_STATUS/}" "$MEMORY_DIR/$DATE.md"

# Archive old memory files on Sundays (day 0)
if [ $(date +%w) -eq 0 ]; then
    find "$MEMORY_DIR" -name "*.md" -mtime +7 -exec mv {} "$MEMORY_DIR/archive/" \;
fi

echo "[$TIME] Ledger maintenance complete"
