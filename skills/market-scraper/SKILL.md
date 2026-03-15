---
name: market-scraper
description: Uses Playwright (stealth mode) to scrape live market commentary from financial sites that block normal web_fetch requests — Bloomberg, Reuters, FT, Seeking Alpha, MarketWatch. Feeds real sourced commentary into the Dibs Daily report. Use when web_fetch returns 403 or Cloudflare challenge pages on financial sites.
user-invocable: true
---

# Market Scraper — Playwright for Financial Sites

## Purpose

Many financial news sites (Bloomberg, FT, Reuters paywalled articles) block `web_fetch` with 403 errors or Cloudflare challenges. This skill uses `playwright-scraper-skill` stealth mode to bypass that and extract real commentary for the Dibs Daily report.

---

## Decision Tree — Which Method?

```
Try web_fetch first (fastest):
  web_fetch("https://reuters.com/markets/...")

Got 403 / Cloudflare page / empty content?
  → Use Playwright Simple (dynamic JS sites)
  
Still failing / anti-bot protected?
  → Use Playwright Stealth (Cloudflare sites)
```

---

## Command Reference

### Quick fetch (dynamic but not anti-bot protected)
```bash
node ~/.openclaw/workspace/skills/playwright-scraper-skill/scripts/playwright-simple.js \
  "https://www.marketwatch.com/investing/stock/AAPL"
```

### Stealth fetch (Bloomberg, Cloudflare, paywalls)
```bash
node ~/.openclaw/workspace/skills/playwright-scraper-skill/scripts/playwright-stealth.js \
  "https://www.bloomberg.com/markets"
```

### First-time setup (only once)
```bash
cd ~/.openclaw/workspace/skills/playwright-scraper-skill
npm install
npx playwright install chromium
```

---

## Daily 5 Scraping Protocol

For each of the 5 S&P stocks, use this escalation:

### Attempt 1 — Fast (web_fetch)
```
web_fetch("https://finance.yahoo.com/quote/AAPL/news")
web_fetch("https://seekingalpha.com/symbol/AAPL")
```

### Attempt 2 — Dynamic (playwright-simple)
```bash
node skills/playwright-scraper-skill/scripts/playwright-simple.js \
  "https://www.cnbc.com/quotes/AAPL"
```

### Attempt 3 — Stealth (playwright-stealth)
```bash
SAVE_HTML=true \
node skills/playwright-scraper-skill/scripts/playwright-stealth.js \
  "https://www.reuters.com/markets/companies/AAPL.O/"
```

---

## Macro Data Scraping

For macro commentary (VIX context, Fed commentary, DXY narrative):

```bash
# Bloomberg Markets overview (often Cloudflare protected)
node skills/playwright-scraper-skill/scripts/playwright-stealth.js \
  "https://www.bloomberg.com/markets"

# Reuters markets (usually works with simple)
node skills/playwright-scraper-skill/scripts/playwright-simple.js \
  "https://www.reuters.com/markets/"

# FT Markets
node skills/playwright-scraper-skill/scripts/playwright-stealth.js \
  "https://markets.ft.com/data"
```

---

## Output Handling

Playwright Simple returns JSON:
```json
{
  "url": "https://...",
  "title": "AAPL Stock News",
  "content": "...[article text]...",
  "elapsedSeconds": "4.2"
}
```

Playwright Stealth saves:
- JSON output to stdout
- Screenshot: `playwright-output/screenshot.png`
- HTML: `playwright-output/page.html` (if `SAVE_HTML=true`)

---

## What NOT to Scrape

- ❌ Paywalled full articles (FT, Bloomberg subscribers only) — you'll get paywall walls, not content
- ❌ Sites that require login to see data (most broker analytics)
- ✅ News headlines, summaries, market overview pages
- ✅ Yahoo Finance, Reuters, CNBC public pages
- ✅ Google Finance, MarketWatch free content

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `Module not found` | Run `npm install` in the skill folder first |
| `browserType.launch: executable doesn't exist` | Run `npx playwright install chromium` |
| Still getting 403 after stealth | Increase wait: `WAIT_TIME=15000 node playwright-stealth.js URL` |
| Content is login wall | Site requires subscription — use a different source |
