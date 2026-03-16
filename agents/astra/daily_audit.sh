#!/bin/bash
# Daily Agent Audit - 08:00 Sydney Time
# Checks all agent STATUS.md files and reports health

echo "=== DAILY AGENT AUDIT - $(date) ===" >> ~/.openclaw/logs/daily_audit.log

for agent_dir in ~/.openclaw/workspace/agents/*/; do
    agent=$(basename "$agent_dir")
    status_file="$agent_dir/STATUS.md"
    
    if [ -f "$status_file" ]; then
        # Extract health status
        health=$(grep -E "^## Health" "$status_file" | head -1 | cut -d: -f2 | xargs)
        last_success=$(grep -E "^## Last Success" "$status_file" | head -1 | cut -d: -f2 | xargs)
        
        echo "$agent: $health (Last: $last_success)" >> ~/.openclaw/logs/daily_audit.log
        
        # Alert if degraded
        if echo "$health" | grep -q "⚠️\|❌"; then
            echo "  ⚠️ ALERT: $agent needs attention" >> ~/.openclaw/logs/daily_audit.log
        fi
    else
        echo "❌ $agent: STATUS.md missing" >> ~/.openclaw/logs/daily_audit.log
    fi
done

echo "=== END DAILY AUDIT ===" >> ~/.openclaw/logs/daily_audit.log
