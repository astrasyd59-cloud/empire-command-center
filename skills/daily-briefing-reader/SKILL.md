---
name: daily-briefing-reader
description: Forces the agent to load the Daily 5 system lock file, MEMORY.md, and today's daily memory log before responding to ANY briefing or report request. Eliminates template drift and format confusion.
user-invocable: true
---

# Daily Briefing Reader

## ⚠️ MANDATORY — Do This Before ANYTHING Else

Whenever you are asked to build, generate, update, or deliver the Daily 5 report — or any market briefing — you MUST read the following files in this exact order before proceeding. No exceptions.

### Step 1 — Load the System Lock
Read the file at:
```
{baseDir}/../../memory/DAILY5_SYSTEM_LOCK.md
```
This file defines the LOCKED configuration for the Daily 5 report. Every build must match it exactly. If you do not read this file first, you will produce the wrong output.

**What to check:**
- Template version (currently: v6 — `daily5/TEMPLATE_v3.html` only)
- Schedule (5:55 AM AEDT, 365 days/year)
- S&P 500 rotation position (which batch of 5 stocks are next)
- Crypto rotation (which coin is next — NO repeats)
- Forex rotation (which pair is next)
- CFA topic rotation (which of the 10 topics)

### Step 2 — Load MEMORY.md
Read the file at:
```
{baseDir}/../../MEMORY.md
```
This contains locked user preferences, active projects, and lessons learned (especially around source attribution and price timestamping).

**Critical rules from MEMORY.md to always enforce:**
- All prices MUST be timestamped: "As of [time] ET · [date]"
- All street commentary MUST have source links (MS, JPM, Bloomberg, Reuters)
- Trading setups must be REAL analysis (LONG/SHORT/NEUTRAL with rationale — not all LONG)
- S&P rotation: sequential through 503 (never restart at position 1 mid-cycle)
- Crypto: daily rotation, NO repeats allowed

### Step 3 — Load Today's Memory File
Read the daily memory log file for TODAY's date (AEDT timezone):
```
{baseDir}/../../memory/YYYY-MM-DD.md
```
Replace `YYYY-MM-DD` with today's actual date in Australian Eastern time.

This file will tell you:
- Where yesterday's rotation left off
- Any active blockers (e.g., Notion API status)
- What tasks remain from the last session

---

## After Loading — Confirm Before Building

After reading all three files, confirm the rotation state before generating output:

```
📋 Pre-flight check:
- S&P batch: [X-X] ([STOCK1], [STOCK2], [STOCK3], [STOCK4], [STOCK5])
- Crypto: [COIN]
- Forex: [PAIR]
- CFA Topic: [TOPIC]
- Template: v6 LOCKED ✅
- Timestamp format: "As of [time] ET · [date]" ✅
```

Only proceed once this pre-flight is confirmed.

---

## Failure Modes to NEVER Do

- ❌ Using an old template or format from memory (always read DAILY5_SYSTEM_LOCK.md)
- ❌ Restarting S&P rotation at positions 1-5 unless confirmed last batch was 499-503
- ❌ Repeating yesterday's crypto coin
- ❌ Setting all trading setups to LONG
- ❌ Missing price timestamps
- ❌ Commentary without source links
