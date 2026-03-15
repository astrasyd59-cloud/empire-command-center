---
name: persistent-memory-writer
description: Writes structured session notes, rotation state, and key decisions to today's memory file (memory/YYYY-MM-DD.md). Solves the blank memory stubs problem — keeps the agent's memory alive between sessions automatically. Also tracks S&P/Crypto/Forex rotation counters so the agent always knows where it left off.
user-invocable: true
---

# Persistent Memory Writer

## Purpose

Solves the "where was I?" problem. After March 5, daily memory files became empty stubs. This skill defines exactly how to write proper memory entries so that context survives between sessions.

---

## When to Write Memory

Write to the daily memory file in these situations:
1. **End of any session** where meaningful work was done
2. **After completing the Daily 5 report** — record the rotation state
3. **When the user asks you to "save this" or "remember this"**
4. **After any decision is made** that affects future sessions
5. **When `/remember` or `/save` is typed** by the user

---

## How to Write Memory

### Find Today's File
The memory file is at:
```
{baseDir}/../../memory/YYYY-MM-DD.md
```
Replace `YYYY-MM-DD` with today's date in AEDT (Australian Eastern time, UTC+11 in summer).

If the file doesn't exist, create it with the template below.

---

### Memory File Template (for new files)

```markdown
# Memory Log - YYYY-MM-DD

## Session Start: HH:MM AEDT
## Last Update: HH:MM AEDT

### 🔄 Rotation State (CRITICAL — Read This Every Session)

| Asset | Value | Notes |
|-------|-------|-------|
| S&P 500 batch | Positions X-Y | Next: [STOCK LIST] |
| Crypto | [COIN] | Next after: [NEXT COIN] |
| Forex | [PAIR] | Next after: [NEXT PAIR] |
| CFA Topic | [TOPIC] | Topic number [N] of 10 |

### Activities Log
- [HH:MM] [Activity description]

### Key Decisions
- [Decision made and rationale]

### Blockers
- [ ] [Blocker description]

### Action Items (Next Session)
- [ ] [Task to be done]
```

---

### Rotation State Entry Format

After every Daily 5 report, write the rotation update entry:

```markdown
### 🔄 Rotation State — Updated [HH:MM AEDT]

**Daily 5 Report Completed:** [DATE]

| Asset | Today | Next |
|-------|-------|------|
| S&P 500 | Positions [X-Y]: [STOCKS] | Positions [X+5 to Y+5] |
| Crypto | [COIN] | [NEXT COIN] |
| Forex | [PAIR] | [NEXT PAIR] |
| CFA Topic | [TOPIC] ([N]/10) | [NEXT TOPIC] |

**Delivery:** ✅ Telegram sent / ❌ Failed ([reason])
**GitHub Pages:** ✅ Pushed / ❌ Failed ([reason])
```

---

### Session Summary Entry Format

At end of session, append:

```markdown
### 📝 Session Summary — [HH:MM AEDT]

**Duration:** ~[X] minutes
**Primary task:** [What was done]
**Completion:** ✅ Complete / ⚠️ Partial / ❌ Failed

**What happened:**
- [Bullet 1]
- [Bullet 2]

**User feedback received:**
- [Any corrections or preferences the user stated]

**To remember for next session:**
- [Critical context that must survive]
```

---

## Slash Commands

When the user types any of these, trigger a memory write:

- `/remember [text]` — Append a memory note to today's file
- `/save` — Save the current session summary
- `/rotation` — Show and save the current rotation state
- `/what-did-we-do` — Summarise today's memory log for the user

---

## S&P Rotation Logic (Never Lose Your Place)

The S&P 500 list has 503 stocks. Rotation is sequential, never random.

**To find the next batch:**
1. Read today's memory file for the last rotation entry
2. Take the last position number (e.g., if today was 11-15, next is 16-20)
3. If you reach 503, restart from 1 on the next cycle
4. NEVER guess — always read the file first

**If memory file is empty or stub:**
1. Check `DAILY5_SYSTEM_LOCK.md` for the last recorded rotation
2. Check `MEMORY.md` for backup rotation state
3. If truly unknown, ask: "What S&P batch did we do yesterday?"

---

## Critical Rules

- ❌ Never overwrite existing memory entries — always append
- ❌ Never assume the rotation state — always read from file
- ✅ Always include timestamp in AEDT
- ✅ Always write rotation state after each Daily 5 report
- ✅ If file doesn't exist, create it with the template above
