# MEMORY.md — DiscordOps Context

## Project: Discord Command Center Setup

**Date:** 2026-02-19  
**Requested by:** Dibs (via Astra)  
**Scope:** Build fresh Discord server for Empire operations

---

## Current State

- Dibs has existing server "Dibs's server" with #dti channel
- **Decision:** Start fresh or repurpose existing
- Preference: Clean slate for Empire operations

---

## Requirements

### Must-Have Channels

1. **#briefings** — Daily morning reports
   - Astra posts automated daily briefings here
   - Includes: emails, calendar, notion tasks, trading summary
   - Time: 6:30 AM Sydney time

2. **#agents** — Sub-agent activity logs
   - Chitra (Notion) reports here
   - Future agents (Trading, Job Hunt) report here
   - All agent completions, errors, status updates

3. **#trading** — Trading operations
   - Trade alerts and opportunities
   - Journal prompts ("Log your trade")
   - Market summaries
   - Position updates

4. **#jobs** — Career operations
   - Job application tracking
   - Interview reminders
   - LinkedIn activity
   - Networking follow-ups

5. **#general** — Catch-all
   - Dibs questions
   - Astra responses
   - Random thoughts

6. **#system** — Technical
   - Webhook status
   - Integration errors
   - Rate limit warnings
   - DiscordOps logs

### Nice-to-Have (Future)

- **#voice** — Voice channel for future voice briefings
- **#resources** — Shared links, files, documents
- **#archive** — Old briefings, completed projects

---

## Integrations Needed

| Integration | Channel | Purpose |
|-------------|---------|---------|
| Astra Webhook | #briefings | Daily automated posts |
| Astra Webhook | #agents | Agent activity logs |
| Astra Webhook | #trading | Trading alerts |
| Astra Webhook | #jobs | Job hunt updates |
| Google Calendar | #briefings | Event reminders |
| Notion | #agents | Task completion logs |

---

## User Preferences

- **Style:** Professional but not corporate
- **Dark mode:** Preferred (default)
- **Mobile-first:** Dibs checks on phone often
- **Noise level:** Low. Only important alerts.
- **Tone:** Direct, no fluff

---

## Constraints

- **No @everyone pings** unless critical
- **Keep it clean** — archive old messages regularly
- **Secure** — no sensitive data in channel names
- **Scalable** — structure supports future agents

---

## Success Criteria

1. All webhooks tested and working
2. Astra can post to all channels
3. Channel purposes are obvious
4. Dibs knows which channel to check for what
5. Server invite link ready for Dibs

---

## Handoff Checklist (To Astra)

- [ ] Server invite link
- [ ] All webhook URLs documented
- [ ] Channel structure explained
- [ ] Test post sent to each channel
- [ ] Maintenance guide (how to add new channels/webhooks)

---

_Status: Awaiting approval to begin_
