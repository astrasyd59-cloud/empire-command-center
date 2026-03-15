#!/usr/bin/env python3
"""
Job Application Pipeline — GitHub Issues Tracker
Manages job applications as GitHub Issues in empire-command-center repo.

Usage:
  python3 job_pipeline.py create   -- Create a new job application issue
  python3 job_pipeline.py list     -- List all open applications
  python3 job_pipeline.py status   -- Print a summary for Telegram
  python3 job_pipeline.py update   -- Update an existing issue (by number)

Args for create (all optional, falls back to prompts if not set):
  --company "Keyrock"
  --role "Operations Manager"
  --url "https://jobs.ashbyhq.com/Keyrock/..."
  --source "LinkedIn"
  --notes "Referred by X"

Args for update:
  --issue 42
  --stage "Interview"  (Applied|Phone Screen|Interview|Final Round|Offer|Rejected|Withdrawn)
  --note "Had first round with HR"
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO        = "astrasyd59-cloud/empire-command-center"
LABEL       = "job-hunt"
AEDT        = timezone(timedelta(hours=11))
STAGES      = ["Applied", "Phone Screen", "Interview", "Final Round", "Offer", "Rejected", "Withdrawn"]
STAGE_EMOJI = {
    "Applied":      "📩",
    "Phone Screen": "📞",
    "Interview":    "🤝",
    "Final Round":  "🏁",
    "Offer":        "💼",
    "Rejected":     "❌",
    "Withdrawn":    "🚫",
}


def run_gh(args: list, capture=True) -> str | None:
    """Run a gh CLI command. Returns stdout or None on failure."""
    cmd = ["gh"] + args
    try:
        result = subprocess.run(
            cmd, capture_output=capture, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"[GH ERROR] {result.stderr.strip()}")
            return None
        return result.stdout.strip() if capture else ""
    except FileNotFoundError:
        print("[ERROR] `gh` CLI not found. Install it: https://cli.github.com")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("[ERROR] GitHub CLI timed out")
        return None


def now_aedt() -> str:
    return datetime.now(AEDT).strftime("%Y-%m-%d %H:%M AEDT")


def now_date() -> str:
    return datetime.now(AEDT).strftime("%Y-%m-%d")


def ensure_label():
    """Create the job-hunt label if it doesn't exist."""
    run_gh([
        "label", "create", LABEL,
        "--repo", REPO,
        "--color", "0075ca",
        "--description", "Job application tracking",
        "--force"
    ], capture=False)


def create_issue(company: str, role: str, url: str, source: str = "Unknown", notes: str = "") -> str | None:
    """Create a new job application as a GitHub Issue."""
    ensure_label()

    today    = now_date()
    title    = f"[JOB] {company} — {role}"
    stage    = "Applied"
    emoji    = STAGE_EMOJI[stage]

    body = f"""## Application Details

| Field | Value |
|-------|-------|
| **Company** | {company} |
| **Role** | {role} |
| **Applied** | {today} |
| **Source** | {source} |
| **Stage** | {emoji} {stage} |

## Application URL
{url if url else "Not recorded"}

## Notes
{notes if notes else "None"}

---

## Stage History
- `{today}` — {emoji} {stage}

---
*Tracked by Astra · {now_aedt()}*
"""

    result = run_gh([
        "issue", "create",
        "--repo", REPO,
        "--title", title,
        "--body", body,
        "--label", LABEL,
    ])

    if result:
        print(f"[OK] Created issue: {result}")
        return result
    return None


def update_issue(issue_number: int, stage: str, note: str = "") -> bool:
    """Update the stage of an existing job application issue."""
    if stage not in STAGES:
        print(f"[ERROR] Invalid stage '{stage}'. Choose: {', '.join(STAGES)}")
        return False

    emoji   = STAGE_EMOJI[stage]
    today   = now_date()
    comment = f"""### Stage Update — {emoji} {stage}

**Date:** {today}
**Note:** {note if note else "No additional notes"}

*Updated by Astra · {now_aedt()}*"""

    result = run_gh([
        "issue", "comment",
        str(issue_number),
        "--repo", REPO,
        "--body", comment,
    ])

    # Close the issue if terminal stage
    if stage in ("Rejected", "Withdrawn"):
        run_gh([
            "issue", "close",
            str(issue_number),
            "--repo", REPO,
            "--comment", f"Closing — {emoji} {stage} on {today}",
        ])
        print(f"[OK] Issue #{issue_number} closed as {stage}")

    return result is not None


def list_applications() -> list[dict]:
    """List all open job applications."""
    result = run_gh([
        "issue", "list",
        "--repo", REPO,
        "--label", LABEL,
        "--state", "all",
        "--limit", "50",
        "--json", "number,title,state,createdAt,body",
    ])

    if not result:
        return []

    try:
        issues = json.loads(result)
        return issues
    except json.JSONDecodeError:
        print("[ERROR] Could not parse GitHub response")
        return []


def print_status_summary():
    """Print a Telegram-ready status summary."""
    issues = list_applications()

    if not issues:
        print("📋 No job applications tracked yet.")
        return

    open_apps    = [i for i in issues if i["state"] == "OPEN"]
    closed_apps  = [i for i in issues if i["state"] == "CLOSED"]

    lines = [f"💼 **Job Pipeline — {now_date()}**\n"]
    lines.append(f"Open: {len(open_apps)} | Closed: {len(closed_apps)}\n")

    if open_apps:
        lines.append("**Active Applications:**")
        for issue in open_apps:
            num   = issue["number"]
            title = issue["title"].replace("[JOB] ", "")
            lines.append(f"  #{num} — {title}")

    if closed_apps:
        lines.append("\n**Closed (last 5):**")
        for issue in closed_apps[:5]:
            num   = issue["number"]
            title = issue["title"].replace("[JOB] ", "")
            lines.append(f"  #{num} — ~~{title}~~")

    lines.append(f"\nhttps://github.com/{REPO}/issues?q=label%3Ajob-hunt")
    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Job Application Pipeline")
    parser.add_argument("command", choices=["create", "list", "status", "update"])
    parser.add_argument("--company",  help="Company name")
    parser.add_argument("--role",     help="Job title")
    parser.add_argument("--url",      help="Job posting URL")
    parser.add_argument("--source",   help="Where you found it (LinkedIn, Seek, Referral...)")
    parser.add_argument("--notes",    help="Any notes about the application")
    parser.add_argument("--issue",    type=int, help="Issue number to update")
    parser.add_argument("--stage",    help=f"New stage: {', '.join(STAGES)}")
    parser.add_argument("--note",     help="Note for the stage update")
    args = parser.parse_args()

    if args.command == "create":
        company = args.company or input("Company: ").strip()
        role    = args.role    or input("Role: ").strip()
        url     = args.url     or input("Job URL (or Enter to skip): ").strip()
        source  = args.source  or "Not specified"
        notes   = args.notes   or ""
        create_issue(company, role, url, source, notes)

    elif args.command == "update":
        if not args.issue:
            print("[ERROR] --issue required for update")
            sys.exit(1)
        if not args.stage:
            print(f"[ERROR] --stage required. Options: {', '.join(STAGES)}")
            sys.exit(1)
        update_issue(args.issue, args.stage, args.note or "")

    elif args.command == "list":
        issues = list_applications()
        for i in issues:
            state = "✅" if i["state"] == "OPEN" else "❌"
            print(f"{state} #{i['number']} — {i['title']}")

    elif args.command == "status":
        print_status_summary()


if __name__ == "__main__":
    main()
