# TOOLS.md

## Active Tools

### Notion Database: Side Hustle Pipeline
- **Status**: ⏳ Pending setup
- **Purpose**: Central hub for all side hustle tracking
- **Databases needed**:
  - Projects (active, completed, pipeline)
  - Clients (contact info, history, ratings)
  - Income (by source, date, project)
  - Pipeline (leads, proposals, follow-ups)

## Pending Integrations

### Platform APIs

| Platform | API Status | Capabilities When Available |
|----------|------------|----------------------------|
| Upwork | ⏳ Pending | Job tracking, proposals, earnings |
| Fiverr | ⏳ Pending | Gig analytics, orders, messages |
| Toptal | ⏳ Not available | Manual tracking only |
| LinkedIn | ⏳ Pending | Networking, lead gen tracking |

### Wishlist
- [ ] Automated client outreach system
- [ ] Contract management (HelloSign/Docusign)
- [ ] Invoice tracking (FreshBooks/QuickBooks integration)
- [ ] Time tracking (Toggl/Harvest)
- [ ] Calendar integration for deadlines

## Manual Tracking Templates

Until APIs are available, maintain:

1. **Weekly Pipeline Review** (Notion/Spreadsheet)
   - Active proposals
   - Follow-ups needed
   - New opportunities to explore

2. **Monthly Income Reconciliation**
   - Cross-reference platform earnings
   - Track non-platform income
   - Calculate effective hourly rates

3. **Quarterly Client Health Check**
   - Review all client relationships
   - Identify upsell opportunities
   - Plan outreach to dormant clients

## Tool Credentials

> **Note**: Store any API keys or sensitive credentials securely.
> Use environment variables or secure vault — never commit to files.

```
# Template for .env (not committed)
NOTION_TOKEN=secret_xxx
NOTION_DATABASE_PROJECTS=xxx
NOTION_DATABASE_CLIENTS=xxx
NOTION_DATABASE_INCOME=xxx
UPWORK_API_KEY=xxx (when available)
FIVERR_API_KEY=xxx (when available)
```
