#!/bin/bash
# Weekly Agent Audit - Sunday 09:00 Sydney Time
# Full SKILLS/MISSION/TOOLS verification

echo "=== WEEKLY AGENT AUDIT - $(date) ===" > ~/.openclaw/logs/weekly_audit_$(date +%Y%m%d).log

for agent_dir in ~/.openclaw/workspace/agents/*/; do
    agent=$(basename "$agent_dir")
    echo "" >> ~/.openclaw/logs/weekly_audit_$(date +%Y%m%d).log
    echo "--- $agent ---" >> ~/.openclaw/logs/weekly_audit_$(date +%Y%m%d).log
    
    # Check all required files
    for file in SOUL.md MISSION.md SKILLS.md TOOLS.md STATUS.md; do
        if [ -f "$agent_dir/$file" ]; then
            echo "✅ $file" >> ~/.openclaw/logs/weekly_audit_$(date +%Y%m%d).log
        else
            echo "❌ $file MISSING" >> ~/.openclaw/logs/weekly_audit_$(date +%Y%m%d).log
        fi
    done
done

echo "" >> ~/.openclaw/logs/weekly_audit_$(date +%Y%m%d).log
echo "=== END WEEKLY AUDIT ===" >> ~/.openclaw/logs/weekly_audit_$(date +%Y%m%d).log
