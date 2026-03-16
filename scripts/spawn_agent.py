#!/usr/bin/env python3
"""
OpenClaw Sub-Agent Spawner
==========================
Spawns isolated background processes for complex reports.
Main ASTRA handles chat. This handles execution.

Usage: python3 spawn_agent.py daily5
       python3 spawn_agent.py sol_vs_hype
       python3 spawn_agent.py status
"""

import os
import sys
import json
import subprocess
import time
import signal

# CONFIG
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT = os.environ.get("TELEGRAM_CHAT", "791589970")
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SCRIPTS_DIR, ".agent_state.json")

# TASK REGISTRY
TASKS = {
    "daily5": {
        "script": "daily5_builder.py",
        "description": "Daily 5+1 Brief",
        "timeout": 300,
    },
    "sol_vs_hype": {
        "script": "sol_vs_hype.py",
        "description": "SOL vs HYPE Analysis",
        "timeout": 600,
    },
}

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 spawn_agent.py <task>")
        print(f"Tasks: {list(TASKS.keys())}")
        return
    
    task_name = sys.argv[1]
    if task_name not in TASKS:
        print(f"Unknown task: {task_name}")
        return
    
    task = TASKS[task_name]
    script_path = os.path.join(SCRIPTS_DIR, task["script"])
    
    print(f"[SPAWN] Starting {task['description']}...")
    
    # Run the script
    proc = subprocess.Popen(
        [sys.executable, script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    
    print(f"[SPAWN] PID {proc.pid} · Running in background")
    print(f"[SPAWN] Timeout: {task['timeout']}s")

if __name__ == "__main__":
    main()
