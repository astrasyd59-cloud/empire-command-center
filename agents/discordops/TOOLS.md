# TOOLS.md - DiscordOps

## Active Tools

### Discord API v10
- **Access Method:** Bot Token
- **Capabilities:** Full server management for configured guild
- **Documentation:** <https://discord.com/developers/docs>

### Server Configuration
- **Guild ID:** `1474172694164406314`
- **Environment:** Production
- **Access Level:** Administrator (assumed based on responsibilities)

## Credentials & Access

| Resource | Identifier | Notes |
|----------|------------|-------|
| Guild ID | 1474172694164406314 | Target server for all operations |
| Bot Token | [REDACTED] | Stored securely, never commit to files |

## Webhook Inventory

> **⚠️ TODO:** Document all active webhooks
> - Channel name/ID
> - Webhook name and ID
> - Purpose/Integration
> - Created date
> - Last verified date

## Missing Capabilities

| Capability | Impact | Workaround |
|------------|--------|------------|
| Audit Logging API | Cannot programmatically review all permission changes | Manual audit via Discord client |
| Advanced Permission Rules | Limited conditional permission logic | Design around Discord's native system |

## Environment Notes

- All changes should be tested in a development server when possible
- Production changes require extra verification
- Keep webhook URLs in secure storage, never in plain text files
