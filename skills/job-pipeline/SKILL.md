---
name: job-pipeline
description: Tracks Dibs's job applications as GitHub Issues in the empire-command-center repo. Each application is one issue with stage tracking, URLs, and notes. Astra uses this to manage the full job hunt lifecycle — from application through offer/rejection. Replaces the blunt Keyrock cron reminders with a proper pipeline.
user-invocable: true
---

# Job Pipeline — GitHub Issues Tracker

## Purpose

Every job application Dibs makes becomes a **GitHub Issue** in `astrasyd59-cloud/empire-command-center` with the label `job-hunt`. Stages are tracked via comments. The issue closes when the application ends (offer accepted, rejected, or withdrawn).

---

## Stages

```
📩 Applied → 📞 Phone Screen → 🤝 Interview → 🏁 Final Round → 💼 Offer
                                                              ↘️ ❌ Rejected
                                                         🚫 Withdrawn (anytime)
```

---

## Commands

### Log a new application
```bash
python3 ~/.openclaw/workspace/scripts/job_pipeline.py create \
  --company "Keyrock" \
  --role "Operations Manager" \
  --url "https://jobs.ashbyhq.com/Keyrock/3ad23ed6-95bd-4cad-92bb-705d8489f148/application" \
  --source "LinkedIn" \
  --notes "Referred through network"
```

### Update application stage (e.g., after interview)
```bash
python3 ~/.openclaw/workspace/scripts/job_pipeline.py update \
  --issue 42 \
  --stage "Interview" \
  --note "First round with HR — went well, technical round next week"
```

### List all applications
```bash
python3 ~/.openclaw/workspace/scripts/job_pipeline.py list
```

### Get Telegram-ready status summary
```bash
python3 ~/.openclaw/workspace/scripts/job_pipeline.py status
```

---

## Astra's Job Tracking Protocol

### When Dibs mentions a new application
1. Ask: "Want me to log this in the job pipeline?"
2. Get: company name, role title, URL
3. Run `create` command
4. Confirm: "✅ Logged as Issue #[N]"

### When Dibs gets a response (interview, rejection)
1. Ask which company/role
2. Run `update` with correct issue number and stage
3. If rejected → issue closes automatically
4. Send confirmation to Dibs

### Wednesday + Friday job follow-up cron (9 AM)
When the "Job Application Follow-up" cron fires, Astra should:
1. Run `status` command to get current pipeline view
2. Send the status summary to Dibs via Telegram
3. Identify any applications that are >7 days old with no update → flag for follow-up

---

## Pipeline View on GitHub

All tracked applications:
```
https://github.com/astrasyd59-cloud/empire-command-center/issues?q=label%3Ajob-hunt
```

Open applications only:
```
https://github.com/astrasyd59-cloud/empire-command-center/issues?q=label%3Ajob-hunt+state%3Aopen
```

---

## Logging Existing Applications

Dibs has these active applications (as of March 2026 — log them):

| Company | Role | URL | Source |
|---------|------|-----|--------|
| Keyrock | Operations/Trading | https://jobs.ashbyhq.com/Keyrock/3ad23ed6-95bd-4cad-92bb-705d8489f148/application | LinkedIn |
| Crypto Trading Firm | Operations Manager | Seek #90364610 | Seek |
| Unknown | Operations | Seek #90413303 | Seek |
| Unknown | Operations | Seek #90436888 | Seek |

Run this to backfill all known applications:
```bash
python3 ~/.openclaw/workspace/scripts/backfill_job_pipeline.py
```

---

## Rules

- ❌ Never create duplicate issues for the same role at the same company
- ✅ Always include the job URL when creating (makes it easy to reference)
- ✅ Update stage same day Dibs gets news about it
- ✅ Write meaningful notes on updates — not just "update"
- ✅ Close rejected/withdrawn issues — keep the pipeline clean

---

## Slash Commands (Dibs can trigger via Telegram)

- `/pipeline` — show current job pipeline status
- `/applied [company] [role] [url]` — log a new application
- `/interview [issue#]` — mark as moved to interview stage
- `/rejected [issue#]` — mark as rejected and close
