# Email Assistant - TOOLS

## Configured

| Tool | Status | Config Key | Notes |
|------|--------|------------|-------|
| Gmail API | ⚠️ PENDING | `GMAIL_API_KEY` | Not configured — needs OAuth or service account |

## Planned

| Tool | Purpose | ETA |
|------|---------|-----|
| Notion Integration | Archive important emails to database | TBD |

## Missing / Needed

| Tool | Use Case | Priority |
|------|----------|----------|
| Calendar Integration | Detect meeting requests, avoid conflicts | High |
| Signature Analysis | Match user's writing style in drafts | Medium |

## Configuration Notes

### Gmail API Setup Required
- Enable Gmail API in Google Cloud Console
- Configure OAuth consent screen
- Store credentials securely
- Required scopes: `gmail.readonly`, `gmail.send`, `gmail.modify`

### Priority Rules (Not Yet Defined)
- VIP sender list
- Subject keyword triggers
- Time-sensitive indicators

---

*Add environment-specific notes here as tools are configured.*
