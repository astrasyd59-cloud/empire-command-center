#!/usr/bin/env python3
"""
Daily 5 + 1 Brief Builder v6
==============================
Run: python3 daily5_builder.py
Cron: 0 5 * * * /usr/bin/python3 /path/to/daily5_builder.py
"""

import os
import json
import subprocess
import urllib.request
import urllib.parse
import datetime
import time
import sys

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT = os.environ.get("TELEGRAM_CHAT", "791589970")
GITHUB_REPO_DIR = os.environ.get("GITHUB_REPO_DIR", "/home/astra/.openclaw/workspace")
DEPLOY_SUBDIR = "daily5"
GITHUB_PAGES_BASE = "https://astrasyd59-cloud.github.io/empire-command-center"

print("[INFO] Daily 5 Builder v6 initialized")
print(f"[INFO] Repo: {GITHUB_REPO_DIR}")
print(f"[INFO] Deploy: {GITHUB_PAGES_BASE}/{DEPLOY_SUBDIR}/")
