# TOOLS.md - Pustak

## Active Tools

| Tool | Status | Details |
|------|--------|---------|
| Cron Job | ✅ Running | Daily 9 PM check-in prompt |

## Planned Tools

| Tool | Status | Details |
|------|--------|---------|
| Notion Database | 📝 Not created | Reading Tracker schema pending |

## Infrastructure

- **Host**: Local workspace (`~/.openclaw/workspace/agents/pustak/`)
- **Schedule**: System cron at 21:00 daily
- **Storage**: Notion (external), local memory files

## Missing Capabilities

| Missing | Impact | Priority |
|---------|--------|----------|
| Comprehension Testing | Cannot verify retention | Medium |
| Recommendation Engine | No book suggestions | Low |
| User Feedback Mechanism | One-way only currently | High |
| Full Agent Deployment | Currently cron-only | High |

## Wishlist

- Integration with e-reader APIs (Kindle, Kobo)
- OCR for physical book page tracking
- Spaced repetition for key book insights
