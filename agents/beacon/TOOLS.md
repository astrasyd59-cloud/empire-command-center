# 🔧 TOOLS.md — Beacon

## Discord API v10
- Authentication: Bot Token
- Credential: DISCORD_BOT_TOKEN
- Rate Limits: 50 req/sec
- Status: ✅ WORKING
- Endpoints: /channels, /webhooks, /roles

## Discord Webhooks
- Purpose: Post messages
- Credentials: DISCORD_WEBHOOK_BRIEFING, DISCORD_WEBHOOK_NOTIFICATIONS
- Status: ⚠️ PARTIAL (briefing OK, notifications need fix)

## Required ENV
```
DISCORD_BOT_TOKEN=token
DISCORD_GUILD_ID=id
DISCORD_BRIEFING_CHANNEL_ID=id
DISCORD_NOTIFICATIONS_CHANNEL_ID=id
DISCORD_WEBHOOK_BRIEFING=url
DISCORD_WEBHOOK_NOTIFICATIONS=url
```

## Missing Tools
- Message content filter
- Moderation APIs
- Voice channel API
