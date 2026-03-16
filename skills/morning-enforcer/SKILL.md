---
name: morning-enforcer
description: Defines the exact pre-market routine as a skill. Runs at 5:00 AM AEDT. Ensures the Daily build, git push, and Telegram delivery always happen in the correct sequence — no ad-hoc prompting, no template confusion, no forgotten steps.
user-invocable: true
---

# Morning Enforcer

## Purpose

The Daily report was getting cumbersome because the 5:55 AM cron job tried to do **everything in one LLM turn**: fetch data, build HTML, verify it, push to git, and send Telegram — within a 300 second timeout. This fails silently or produces inconsistent results.

This skill splits the job into two clean stages with the right tools for each step.

---

## ⏰ Timeline (AEDT)

| Time | Stage | What Happens |
|------|-------|-------------|
| 5:00 AM | **Build** | Python script runs, fetches live data, generates HTML |
| 5:25 AM | **Deploy** | Git push to GitHub Pages |
| 5:55 AM | **Deliver** | Telegram message sent to Dibs |
| 6:10 AM | **Verify** | Check GitHub Pages is live, log result |

---

## Stage 1 — Build (5:00 AM)

Run the builder script:

```bash
cd ~/.openclaw/workspace
python3 scripts/daily5_builder_v7.py
```

**Expected output:**
```
[OK] Rotation state loaded — Batch N, stocks X-Y
[OK] Fetching data for: AAPL, NVDA, MSFT, AMZN, GOOGL
[OK] HTML generated: daily5/2026-03-15.html (61KB)
[OK] Rotation state saved
```

**If it fails:**
1. Check Python: `python3 --version` (needs 3.10+)
2. Check yfinance: `python3 -c "import yfinance"`
3. If yfinance timeout → markets may be closed. Script uses last known prices. Still run it.
4. Check `daily5/rotation_state.json` exists and is not corrupt

---

## Stage 2 — Deploy (5:25 AM)

Push the report to GitHub Pages:

```bash
cd ~/.openclaw/workspace
DATE=$(python3 -c "from datetime import datetime,timezone,timedelta; print(datetime.now(timezone(timedelta(hours=11))).strftime('%Y-%m-%d'))")
git add daily5/${DATE}.html daily5/rotation_state.json
git commit -m "Dibs Daily: ${DATE}"
git push origin main
```

**Expected time:** 30-60 seconds
**GitHub Pages propagation:** 1-2 minutes after push

**If git push fails:**
1. Check credentials: `cat ~/.openclaw/credentials/github.env`
2. Check remote: `git remote -v`
3. If auth error, token may be expired → notify Dibs

---

## Stage 3 — Deliver (5:55 AM)

Send the Telegram notification:

```bash
python3 ~/.openclaw/workspace/scripts/deliver.py
```

**This script:**
- Reads `daily5/rotation_state.json` for today's asset list
- Builds the correct Telegram message with real stock names, crypto, forex, CFA topic
- Sends to Dibs (Telegram ID: 791589970)
- Logs the delivery to `daily5/delivery_log.json`

**Dry run (test without sending):**
```bash
python3 ~/.openclaw/workspace/scripts/deliver.py --dry-run
```

---

## Stage 4 — Verify (6:10 AM)

Confirm delivery was successful:

```bash
# Check delivery log
cat ~/.openclaw/workspace/daily5/delivery_log.json | python3 -m json.tool | tail -20

# Verify GitHub Pages is accessible
curl -s -o /dev/null -w "%{http_code}" \
  "https://astrasyd59-cloud.github.io/empire-command-center/daily5/$(date '+%Y-%m-%d').html"
# Should return: 200
```

**If delivery log shows failure** → notify Dibs immediately:
```
⚠️ Dibs Daily delivery failed — [TIME] AEDT
Error: [error from log]
Report built: [yes/no]
Action: [what you're doing about it]
```

---

## What the Cron Job Should Look Like

The cron job in `~/.openclaw/cron/jobs.json` for the main delivery should look like this:

```json
{
  "name": "Dibs Daily Build",
  "schedule": { "expr": "0 5 * * *", "kind": "cron", "tz": "Australia/Sydney" },
  "payload": {
    "kind": "agentTurn",
    "message": "Run the Dibs Daily build: python3 ~/.openclaw/workspace/scripts/daily5_builder_v7.py\n\nThen git commit and push:\ncd ~/.openclaw/workspace && git add daily5/ && git commit -m 'Dibs Daily: $(date +%Y-%m-%d)' && git push origin main\n\nThen run: python3 ~/.openclaw/workspace/scripts/deliver.py\n\nReport result. Do not add any other commentary.",
    "model": "kimi-coding/k2p5",
    "timeoutSeconds": 300
  }
}
```

**Key: The prompt must be EXPLICIT about steps.** Do not say "generate the daily report" — say exactly which scripts to run.

---

## Template Rules (Non-Negotiable)

The report is called **Dibs Daily** — not "Daily 5 + 1 + 1", not "The Daily", not anything else.

Template file: `daily5/TEMPLATE_v3.html` — DO NOT MODIFY without updating `DAILY5_SYSTEM_LOCK.md`

Title line in HTML: `<title>Dibs Daily | YYYY-MM-DD</title>`
Telegram header: `📊 Dibs Daily · [DAY] [DATE]`

---

## Known Issues & Fixes Applied

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| Wrong stocks in Telegram | `deliver.py` had hardcoded stocks | Rewrote `deliver.py` to read `rotation_state.json` |
| Template confusion | Cron job used vague LLM prompt | Explicit script commands in cron message |
| Job timing out | 300s for everything including data fetch | Use Python script for data (fast), LLM just orchestrates |
| Broken local agent job | Uses `ollama/mistral` (not allowed) | Disabled or fixed (see cron notes) |
