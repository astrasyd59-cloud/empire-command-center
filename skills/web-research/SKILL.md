---
name: web-research
description: Teaches the agent how to use web_search and web_fetch correctly — including how to find real market commentary from institutional sources (Morgan Stanley, JPMorgan, Bloomberg, Reuters) and how to cite sources properly. Enforces the sourcing rules from MEMORY.md for Daily 5 reports.
user-invocable: true
---

# Web Research Skill

## Purpose

Your MEMORY.md has a hard rule: **all street commentary MUST have source links**. This skill defines exactly how to satisfy that requirement using OpenClaw's native web tools.

---

## Available Web Tools

You have two tools for web research:

### `web_search`
Use for: finding current news, analyst ratings, recent commentary, price targets
```
web_search("AAPL analyst rating Morgan Stanley 2026")
web_search("JPMorgan S&P 500 outlook March 2026")
web_search("Bloomberg VIX overnight futures")
```

### `web_fetch`
Use for: fetching a specific URL you already know, reading an article in full
```
web_fetch("https://www.reuters.com/markets/us/...")
web_fetch("https://finance.yahoo.com/news/...")
```

---

## Daily 5 Research Protocol

For each of the 5 S&P stocks, 1 crypto, and 1 forex pair in the Daily 5 report, follow this sequence:

### Step 1 — Search for analyst commentary
```
web_search("[TICKER] analyst rating price target [MONTH] [YEAR]")
web_search("[TICKER] earnings outlook [MONTH] [YEAR] Morgan Stanley JPMorgan Goldman")
```

### Step 2 — Search for recent news
```
web_search("[TICKER] news [TODAY'S DATE]")
web_search("[TICKER] [COMPANY NAME] latest news")
```

### Step 3 — Get the macro context
For the Macro Strip section, search:
```
web_search("VIX current level today")
web_search("10-year Treasury yield today")
web_search("Federal Reserve rate outlook [MONTH] [YEAR]")
web_search("DXY dollar index today")
web_search("gold price today")
```

### Step 4 — Crypto context
```
web_search("[COIN] crypto news today [DATE]")
web_search("[COIN] ETF flows [MONTH] [YEAR]")
web_search("[COIN] regulatory news latest")
```

### Step 5 — Forex context
```
web_search("[PAIR] forex analysis [DATE]")
web_search("[PAIR] policy divergence [CENTRAL BANK 1] [CENTRAL BANK 2]")
```

---

## How to Cite Sources (Non-Negotiable)

Every piece of street commentary in the Daily 5 report MUST be attributed. Format:

### Good citation format:
```
"[Quote or paraphrase]"
— [Institution/Author], [Date]
Source: [URL]
```

### Examples:
```
"We maintain our Overweight rating with a $220 price target as iPhone upgrade cycle remains intact."
— Morgan Stanley Equity Research, March 2026
Source: https://www.morganstanley.com/ideas/...

"S&P 500 technical support sits at 5,800 as market digests tariff uncertainty."
— Bloomberg Markets, March 14, 2026
Source: https://www.bloomberg.com/markets/...
```

### Acceptable source tiers (in order of credibility):
1. **Tier 1** — Morgan Stanley, Goldman Sachs, JPMorgan, Bank of America, Citi Research
2. **Tier 2** — Bloomberg, Reuters, Financial Times, Wall Street Journal
3. **Tier 3** — Yahoo Finance, CNBC, MarketWatch, Seeking Alpha
4. **Never use** — Generic AI-generated summaries with no source, anonymous posts

---

## SearXNG (Local Search — Preferred)

Your machine runs a local SearXNG instance at `http://localhost:8080`. This aggregates multiple search engines without tracking.

When using `web_search`, it may route through SearXNG automatically. If you need to query it directly:
```
web_fetch("http://localhost:8080/search?q=[QUERY]&format=json")
```

---

## Research Checklist for Daily 5 Reports

Before generating the report, confirm you have found:
- [ ] At least 1 sourced analyst quote per stock (Tier 1 or 2 preferred)
- [ ] At least 1 recent news item per stock (last 24-48h)
- [ ] VIX, 10Y yield, DXY, Gold from a live source (yfinance handles price data)
- [ ] Crypto-specific news for today's coin
- [ ] Forex policy divergence context for today's pair

If real-time sources are unavailable (weekend, market closed), note it explicitly:
```
"Commentary based on most recent available data (market closed). Last update: [DATE]"
```

---

## What NOT to Do

- ❌ Making up analyst quotes ("Goldman Sachs says...") without a real source
- ❌ Using vague attributions ("analysts say..." with no link)
- ❌ Copying yesterday's commentary into today's report
- ❌ Skipping web research because "I know about this stock"
- ❌ Using internal knowledge for time-sensitive price data — always fetch live
