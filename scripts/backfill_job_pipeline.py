#!/usr/bin/env python3
"""
Backfill script — log all known job applications into GitHub Issues.
Run once to seed the pipeline with existing applications.

Usage:
  python3 backfill_job_pipeline.py
"""

import subprocess
import sys
from pathlib import Path

# Add parent scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))
from job_pipeline import create_issue, ensure_label

# ─── All known applications as of March 2026 ──────────────────────────
APPLICATIONS = [
    {
        "company": "Keyrock",
        "role":    "Operations Manager / Trading Operations",
        "url":     "https://jobs.ashbyhq.com/Keyrock/3ad23ed6-95bd-4cad-92bb-705d8489f148/application",
        "source":  "LinkedIn",
        "notes":   "Weekend application campaign active. Multiple reminders set. Keyrock is a leading crypto market maker — very relevant to current role at crypto trading firm.",
    },
    {
        "company": "Crypto Trading Firm (Seek)",
        "role":    "Operations Manager",
        "url":     "https://www.seek.com.au/job/90364610",
        "source":  "Seek",
        "notes":   "Job ref #90364610. Applied. Follow up if no response after 2 weeks.",
    },
    {
        "company": "Unknown Firm — Seek #90413303",
        "role":    "Operations (details unclear)",
        "url":     "https://www.seek.com.au/job/90413303",
        "source":  "Seek",
        "notes":   "Applied ~3 days ago as of March 2026. Source role details unclear — review job ad and update this issue.",
    },
    {
        "company": "Unknown Firm — Seek #90436888",
        "role":    "Operations (details unclear)",
        "url":     "https://www.seek.com.au/job/90436888",
        "source":  "Seek",
        "notes":   "Applied ~3 days ago as of March 2026. Source role details unclear — review job ad and update this issue.",
    },
]


def main():
    print(f"[BACKFILL] Logging {len(APPLICATIONS)} known applications to GitHub Issues...\n")
    ensure_label()

    for i, app in enumerate(APPLICATIONS, 1):
        print(f"[{i}/{len(APPLICATIONS)}] {app['company']} — {app['role']}")
        result = create_issue(
            company=app["company"],
            role=app["role"],
            url=app["url"],
            source=app["source"],
            notes=app["notes"],
        )
        if result:
            print(f"  ✅ Created: {result}\n")
        else:
            print(f"  ❌ Failed to create issue — check gh auth\n")

    print("[BACKFILL COMPLETE]")
    print("View your pipeline:")
    print("https://github.com/astrasyd59-cloud/empire-command-center/issues?q=label%3Ajob-hunt")


if __name__ == "__main__":
    main()
