# HEARTBEAT.md — Astra Proactive Protocol

**Version:** 2.0 | **Last Updated:** 2026-03-14 | **Heartbeat interval:** 30 min

---

## ⚡ What to Do Every Heartbeat

Run through this checklist on every 30-minute heartbeat tick. Be efficient. Most checks should resolve in seconds. Only alert Dibs if something actually needs attention.

---

## 🕐 Time-Based Rules (AEDT)

| Time Window | Action |
|-------------|--------|
| **05:25–05:55 AM** | Pre-flight for Daily 5 — verify rotation state is ready, data scripts available |
| **05:55 AM** | If Daily 5 has NOT been sent today → trigger morning briefing build |
| **06:00–09:00 AM** | Verify Daily 5 was delivered. If not → alert Dibs immediately |
| **09:00 AM–11:00 PM** | Normal checks. Alert only if something is broken or Dibs hasn't been in contact for >12h |
| **11:00 PM–05:25 AM** | Silent mode unless CRITICAL (data pipeline failure, system down) |

---

## 📋 Checklist (Run Every 30 Min)

### 1. Daily 5 System — HIGHEST PRIORITY
- [ ] Has today's Daily 5 report been built? (`daily5/YYYY-MM-DD.html` exists for today?)
- [ ] Was it pushed to GitHub Pages?
- [ ] Was the Telegram delivery confirmed?
- If 06:00 AM passes without delivery → **alert Dibs: "Daily 5 not delivered — investigating"**

### 2. Rotation State
- [ ] Is today's memory file (`memory/YYYY-MM-DD.md`) updated with the rotation state?
- [ ] Do you know the current S&P batch, crypto coin, forex pair, and CFA topic for today?
- If unknown → read `DAILY5_SYSTEM_LOCK.md` and update the memory file

### 3. Active Blockers
- [ ] Are there open blockers from the last session? (Check today's memory file)
- Current known: **Notion API 401 flapping** — do NOT alert for this unless a new pattern emerges
- Alert for: new API failures, script crashes, missing credentials

### 4. User Contact
- [ ] Has Dibs been active in the last 12 hours?
- If no contact in >18 hours → send: "Hey — everything good? Just checking in."
- Do NOT alert during silent hours (11 PM–8 AM AEDT)

### 5. System Health
- [ ] Is OpenClaw Gateway running?
- [ ] Are cron sessions active?
- [ ] Context usage: if >80% → warn Dibs to run `/compact`
- [ ] Memory file for today exists and is not a stub?

---

## 📢 Alert Templates (Use These Exactly)

### Daily 5 Not Delivered
```
🚨 Daily 5 Alert — [TIME] AEDT
Report not delivered yet. Investigating.
Status: [what failed]
ETA: [estimate or "looking into it"]
```

### System Down
```
⚠️ System Alert — [TIME] AEDT
[Component] is down.
Details: [error]
Action taken: [what you did/tried]
```

### Check-In (No Contact >18h)
```
Hey — everything ok? Haven't heard from you in a while.
All systems green on my end.
```

---

## 🤫 When to Stay Silent (HEARTBEAT_OK)

Reply `HEARTBEAT_OK` (suppresses notification) when ALL of the following are true:
- Daily 5 was delivered today OR it's before 5:55 AM AEDT
- No new blockers
- Context usage <80%
- No pending action items that are overdue
- User has been active within 12 hours OR it's within silent hours

Otherwise, send an alert or update.

---

## 📌 Known Issues (Don't Alert on These)
- **Notion API 401 flapping** — Known intermittent issue, Astra aware. Only alert if down for >2 consecutive hours during waking hours.

---

## 🔴 CRITICAL — Check These Files Before Doing Anything
1. `memory/YYYY-MM-DD.md` — Today's activity log
2. `memory/DAILY5_SYSTEM_LOCK.md` — Report config and rotation state
3. `MISSION.md` — Current mission and phase status

_Updated: 2026-03-14 | Heartbeat v2.0 — Proactive Mode ACTIVE_
