#!/bin/bash
# Monthly Agent Audit - 1st of month, 10:00 Sydney Time
# Complete framework review

report_file="~/.openclaw/logs/monthly_audit_$(date +%Y%m).log"

echo "=== MONTHLY AGENT AUDIT - $(date) ===" > "$report_file"
echo "" >> "$report_file"
echo "Total Agents: $(ls -d ~/.openclaw/workspace/agents/*/ | wc -l)" >> "$report_file"
echo "Total Files: $(find ~/.openclaw/workspace/agents -name '*.md' | wc -l)" >> "$report_file"
echo "" >> "$report_file"

# Count operational vs not deployed
operational=0
not_deployed=0

for agent_dir in ~/.openclaw/workspace/agents/*/; do
    agent=$(basename "$agent_dir")
    status_file="$agent_dir/STATUS.md"
    
    if [ -f "$status_file" ]; then
        if grep -q "✅ OPERATIONAL\|✅ READY" "$status_file"; then
            ((operational++))
        elif grep -q "⏳ NOT DEPLOYED\|⚠️" "$status_file"; then
            ((not_deployed++))
        fi
    fi
done

echo "Operational Agents: $operational" >> "$report_file"
echo "Not Deployed: $not_deployed" >> "$report_file"
echo "" >> "$report_file"
echo "=== END MONTHLY AUDIT ===" >> "$report_file"
