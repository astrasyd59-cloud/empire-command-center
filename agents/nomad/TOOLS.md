# TOOLS.md - Nomad

## Active Tools

| Tool | Purpose | Status |
|------|---------|--------|
| Notion Database | Citizenship & Visa Tracker | ✅ Configured |
| Travel Planning Tools | Flight/research booking | ✅ Available |

## Pending Integrations

| Tool | Purpose | Status |
|------|---------|--------|
| Government APIs | Real-time visa status checks | ⏳ Pending |
| Embassy Portals | Appointment booking, document submission | ⏳ Manual |
| Document Scanner | Passport/visa digitization | ⏳ To configure |

## Tool Wishlist / Missing

| Tool | Why Needed | Priority |
|------|------------|----------|
| Immigration Lawyer Integration | Complex case consultation, appeals | High |
| Real-Time Visa Status API | Live application tracking | Medium |
| Tax Advisor Coordination | Residency optimization, compliance | Medium |
| Apostille Service Connection | Document authentication | Low |

## Manual Workarounds

Until integrations are available:

### Visa Status Tracking
- User provides application reference numbers
- Manual check reminders on embassy websites
- Screenshot/document updates shared by user

### Document Management
- Notion database stores metadata
- File attachments reference local/cloud storage
- Checklists manually updated as items complete

### Research Sources
- Official government immigration websites
- Embassy/consulate websites and email inquiries
- Reputable immigration forums and communities
- News alerts for policy changes

## Notion Database Schema (Proposed)

### Databases
1. **Visas & Permits**
   - Type, country, issue date, expiry date, conditions
   - Application status, reference number
   
2. **Residency Tracking**
   - Jurisdiction, status, days present count
   - Eligibility date for permanent residency/citizenship
   
3. **Citizenship Pathways**
   - Target country, pathway type, requirements checklist
   - Timeline, milestones, notes

4. **Travel Log**
   - Entry/exit dates, purpose, visa used
   - Days present calculations
