# 📊 STATUS.md — Beacon

## Health
⚠️ DEGRADED

## Last Success
Feb 20, 18:00 UTC

## Last Failure
Feb 20, 17:45 UTC (notifications webhook)

## Uptime
92%

## Known Issues
- Notifications webhook not posting (HIGH priority)
- Channel permission drift (MEDIUM priority)

## Performance
- Webhook response: 145ms
- Channel query: 89ms
- Permission check: 234ms

## Dependencies
- Discord API: ✅
- Bot Token: ✅
- Webhooks: ⚠️
- Channel IDs: ✅
- Roles: ✅

## Recommended Actions
1. Fix #notifications webhook (recreate if needed)
2. Run permission audit
3. Document permission matrix
