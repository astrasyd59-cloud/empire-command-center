---
name: daily5-builder
description: The canonical guide for building the Daily 5 + 1 + 1 report. Defines the exact script to run, where to find the template, how to deploy to GitHub Pages, and how to deliver via Telegram. This skill IS the source of truth — overrides any instructions from memory or past sessions.
user-invocable: true
---

# Daily 5 + 1 + 1 Builder

## ⚠️ CRITICAL — Read This Before EVERY Build

**The Daily 5 system has a locked configuration. ALWAYS defer to this skill and `DAILY5_SYSTEM_LOCK.md` over anything else, including your own memory of past sessions.**

---

## What the Daily 5 Is

A daily financial intelligence report delivered at **5:55 AM AEDT** every day (365 days/year including weekends).

Format: `daily5/YYYY-MM-DD.html`

**Content structure (v6 — LOCKED):**
- 5 S&P 500 stocks (sequential rotation through all 503)
- 1 Crypto asset (daily rotation, no repeats)
- 1 Forex pair (daily rotation)
- Macro Strip: VIX, 10Y Yield, Fed Funds, DXY, Gold
- CFA section: formulas + quiz (rotating through 10 topics)
- Options education (rotating through 8 concepts)
- Glossary (4 terms, matching CFA topic)
- Progress trackers (S&P coverage, CFA topics, quiz accuracy)

---

## Step-by-Step Build Process

### Pre-Build Checklist (MANDATORY)
Before running any scripts, confirm:

1. **Read DAILY5_SYSTEM_LOCK.md** — get today's rotation state
   ```
   read: ~/.openclaw/workspace/memory/DAILY5_SYSTEM_LOCK.md
   ```

2. **Read today's memory file** — check for any blockers or notes
   ```
   read: ~/.openclaw/workspace/memory/YYYY-MM-DD.md
   ```

3. **Confirm rotation state** out loud:
   ```
   📋 Today's build:
   - Date: YYYY-MM-DD (AEDT)
   - S&P batch: [positions X-Y] ([STOCKS])
   - Crypto: [COIN]
   - Forex: [PAIR]
   - CFA Topic: [TOPIC] (Topic N of 10)
   - Template: v6 (TEMPLATE_v3.html) ✅
   ```

---

### Step 1 — Fetch Market Data

The main builder script fetches data automatically via yfinance:

```bash
cd ~/.openclaw/workspace
python3 scripts/daily5_builder_v7.py
```

**What this script does:**
- Reads/updates `daily5/rotation_state.json` (the canonical rotation counter)
- Fetches live stock prices via yfinance
- Fetches crypto prices via yfinance (`{COIN}-USD`)
- Fetches forex rates via yfinance
- Fetches macro data (VIX `^VIX`, 10Y `^TNX`, DXY `DX-Y.NYB`, Gold `GC=F`)
- Generates the full HTML report using TEMPLATE_v3.html
- Saves output to `daily5/YYYY-MM-DD.html`

**Rotation state file:** `daily5/rotation_state.json`
- This is automatically updated by the script on each run
- Do NOT manually edit unless the state is corrupted
- If corrupted, cross-reference with `DAILY5_SYSTEM_LOCK.md`

---

### Step 2 — Add Web-Sourced Commentary

After the script runs, enhance the street commentary sections with real sources.

Use the `web-research` skill to find:
- Analyst ratings/quotes for each of the 5 stocks
- Today's crypto news and ETF flow data
- Today's forex policy divergence context
- Live macro commentary (Bloomberg, Reuters)

Insert sourced quotes into the HTML before deployment. Every commentary block must have a source URL.

---

### Step 3 — Verify the Report

Before pushing, do a quick sanity check:

```bash
# Open in browser to verify visually
xdg-open ~/.openclaw/workspace/daily5/YYYY-MM-DD.html
```

Verify:
- [ ] Date in report header matches today (AEDT)
- [ ] Correct S&P stocks are shown (right batch)
- [ ] Correct crypto coin (not yesterday's)
- [ ] Correct forex pair
- [ ] All prices have timestamps: "As of XX:XX ET · DATE"
- [ ] At least some sourced commentary present
- [ ] Dark/light theme works
- [ ] CFA section shows correct topic

---

### Step 4 — Deploy to GitHub Pages

```bash
cd ~/.openclaw/workspace
git add daily5/YYYY-MM-DD.html
git add daily5/rotation_state.json
git commit -m "Daily 5: YYYY-MM-DD — [STOCKS] + [CRYPTO] + [FOREX]"
git push origin main
```

**GitHub Pages URL (after push):**
```
https://astrasyd59-cloud.github.io/empire-command-center/daily5/YYYY-MM-DD.html
```

Allow 1-2 minutes for GitHub Pages to update after push.

---

### Step 5 — Send Telegram Message

After GitHub Pages is live, send to Dibs via Telegram:

**Message format:**
```
📊 Daily 5 + 1 + 1 — [DAY], [DATE]

Today: [STOCK1], [STOCK2], [STOCK3], [STOCK4], [STOCK5] + [CRYPTO] + [FOREX]

📈 Market snapshot:
• S&P 500: [LEVEL] ([CHANGE]%)
• VIX: [LEVEL]
• 10Y Yield: [RATE]%

🔗 [date]
https://astrasyd59-cloud.github.io/empire-command-center/daily5/YYYY-MM-DD.html

CFA Focus: [TOPIC] | Options: [CONCEPT]
```

Use the `message` tool to send this to Dibs's Telegram (user ID: 791589970).

---

## Key File Locations

| File | Path | Purpose |
|------|------|---------|
| Builder script | `scripts/daily5_builder_v7.py` | Main build engine — DO NOT EDIT casually |
| Template | `daily5/TEMPLATE_v3.html` | HTML template — v6 format — LOCKED |
| Rotation state | `daily5/rotation_state.json` | Canonical rotation counter |
| System lock | `memory/DAILY5_SYSTEM_LOCK.md` | Human-readable rotation state backup |
| Daily output | `daily5/YYYY-MM-DD.html` | Generated report (one per day) |

---

## Delivery Schedule

| Time (AEDT) | Action |
|-------------|--------|
| 05:25 AM | Heartbeat pre-flight check |
| 05:55 AM | BUILD AND DELIVER — non-negotiable |
| 06:15 AM | Verify GitHub Pages is live, confirm Telegram delivered |

**If 5:55 AM passes and report is not delivered → alert Dibs immediately**

---

## Error Recovery

### Script fails
1. Check Python environment: `python3 --version`
2. Check yfinance: `python3 -c "import yfinance; print('ok')"`
3. If market is closed: prices will still be fetched (last closing prices)
4. If yfinance times out: use manual fallback data and note in report

### Rotation state corrupted
1. Read `DAILY5_SYSTEM_LOCK.md` for last known good state
2. Read recent memory files to find last rotation entry
3. Manually update `rotation_state.json`:
   ```json
   {
     "last_date": "YYYY-MM-DD",
     "stock_index": [N],
     "crypto_index": [N],
     "forex_index": [N],
     "cfa_index": [N]
   }
   ```
4. Ask Dibs if still unsure which batch we're on

### Git push fails
1. Check git status: `git status`
2. Check remote: `git remote -v`
3. If auth fails: check GitHub token in `~/.openclaw/credentials/github.env`

---

## What This Skill Replaces

This skill is the canonical source of truth. It supersedes:
- ❌ Ad-hoc instructions given in chat sessions (those are not persistent)
- ❌ Guessing the template version (always v6, TEMPLATE_v3.html)
- ❌ Restarting rotation from batch 1 (always read rotation_state.json first)
- ❌ Skipping web research because "I remember the commentary" (always fetch fresh)
