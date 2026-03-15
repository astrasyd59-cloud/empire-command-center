---
name: github-integration
description: How Astra uses the GitHub skill to manage the empire-command-center repo — automated Daily report deployment, CI status checks, and issue creation. Wraps the ClawHub github skill for Dibs's specific repo setup.
user-invocable: true
---

# GitHub Integration for Astra

## Repo Setup

The main GitHub repo powering the Dibs Daily website is:
```
astrasyd59-cloud/empire-command-center
```

GitHub Pages serves from `main` branch:
```
https://astrasyd59-cloud.github.io/empire-command-center/
```

Credentials are in: `~/.openclaw/credentials/github.env`

---

## Daily Tasks (Runs Automatically)

### Check if today's Daily deployed successfully
```bash
gh run list --repo astrasyd59-cloud/empire-command-center --limit 5
```

### View if a deploy failed
```bash
gh run view <run-id> --repo astrasyd59-cloud/empire-command-center --log-failed
```

### Push today's Dibs Daily manually (if cron missed)
```bash
cd ~/.openclaw/workspace
DATE=$(python3 -c "from datetime import datetime,timezone,timedelta; print(datetime.now(timezone(timedelta(hours=11))).strftime('%Y-%m-%d'))")
git add daily5/${DATE}.html daily5/rotation_state.json
git commit -m "Dibs Daily: ${DATE} [manual]"
git push origin main
```

---

## Job Hunt Integration

### Track job applications as GitHub Issues
Create a new job application issue:
```bash
gh issue create \
  --repo astrasyd59-cloud/empire-command-center \
  --title "Application: [COMPANY] — [ROLE]" \
  --body "Applied: $(date +%Y-%m-%d)\nStatus: Applied\nLink: [URL]\n\nNotes:\n- [notes]" \
  --label "job-hunt"
```

### List all open job applications
```bash
gh issue list --repo astrasyd59-cloud/empire-command-center --label job-hunt --state open
```

### Update application status (e.g., after interview)
```bash
gh issue comment <issue-number> \
  --repo astrasyd59-cloud/empire-command-center \
  --body "**Status update:** Interview scheduled — [DATE]\nNext step: [ACTION]"
```

### Close when rejected/accepted
```bash
gh issue close <issue-number> --repo astrasyd59-cloud/empire-command-center \
  --comment "Outcome: [REJECTED/OFFER/WITHDRAWN] — [DATE]"
```

---

## Monitoring (Trigger in HEARTBEAT)

### Check GitHub Pages is live after Daily push
```bash
gh api repos/astrasyd59-cloud/empire-command-center/pages \
  --jq '.status, .html_url'
# Should return: "built" and the URL
```

### Check for any failed runs in the last 24h
```bash
gh run list --repo astrasyd59-cloud/empire-command-center \
  --json status,conclusion,createdAt \
  --jq '.[] | select(.conclusion == "failure") | .createdAt'
```

---

## When to Use GitHub vs git

| Task | Use |
|------|-----|
| Push Daily HTML | `git push` (faster, no API call) |
| Check if deploy worked | `gh run list` (shows GitHub Actions) |
| Create job application record | `gh issue create` |
| Check GitHub Pages status | `gh api repos/.../pages` |
| Review code changes | `gh pr list`, `gh pr view` |
