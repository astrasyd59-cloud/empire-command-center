# THE DAILY BRIEF v7 — SPECIFICATION REVIEW
## Changes from v6 to v7

**Received:** February 24, 2026, 5:14 PM AEDT  
**Files:** Master instruction spec (markdown) + HTML template  
**Status:** Reviewing changes

---

## MAJOR CHANGES IDENTIFIED

### 1. NAME CHANGE
- **Old:** "The Daily 5 + 1 Crypto"  
- **New:** "The Daily Brief"  
- **Tagline:** *Institutional Market Intelligence · CFA Level I Preparation*

### 2. CRITICAL FIX: GOLD PRICE
- **Issue:** Gold was showing $2,950 (wrong contract/stale data)  
- **Fix:** Must verify gold spot price before publishing (~$5,000 Feb 2026)  
- **Implementation:** Live fetch via `yf.Ticker("GC=F")` + cross-check CoinGecko

### 3. STOCK COUNTER (NEW)
- Each stock card must show: `<span class="stock-counter">N / 503</span>`  
- Shows cumulative position in S&P 500 rotation  
- **503 tickers** (not 500, not 505) — accounts for dual share classes

### 4. TRADING SETUPS TABLE — REMOVED
- No longer included in The Daily Brief  
- Separate "Daily Trade Idea" report to be created  
- When Dibs asks: *"Trade ideas are in the separate Daily Trade Idea report."*

### 5. QUIZ — MANDATORY
- **5 questions every single day** — no exceptions  
- If token limits tight: cut street commentary, NOT the quiz  
- Inline calculations on every answer option  
- Cumulative tracking in `/home/astra/logs/quiz_log.json`

### 6. STREET COMMENTARY — DISCLAIMER
- All analyst quotes are **AI-synthesised approximations**  
- Must add: `⚠️ AI-synthesised from known public analyst positions. Verify via Bloomberg/Refinitiv before citing.`  
- Real sourcing: Bloomberg Terminal, Refinitiv Eikon, Seeking Alpha Premium, CMC/City Index research

### 7. S&P 500 COUNT = 503
- Use **503 tickers** in all progress counters  
- Not 500, not 505  
- Accounts for dual share classes (GOOGL/GOOG, BRK.A/BRK.B)

---

## DAILY STRUCTURE (v7)

### Header
- Masthead: "The Daily Brief"  
- Date, time, data source  
- Disclaimer banner (AI-synthesised quotes warning)

### Macro Strip
- S&P 500, VIX, 10Y Yield, Fed Funds, 3M T-Bill, DXY, Gold, Oil  
- Live as of [time] ET  
- **Gold verification note** required

### Progress Tracker
- S&P 500 coverage: N/503  
- CFA Curriculum: N/10 topics  
- Quiz accuracy (lifetime)  
- Options concepts: N/12  
- CFA topic pills (active/done/pending)

### 5 Stock Cards (Each)
- Header: Ticker, stock counter (N/503), sector badge, price, change, market cap  
- Metrics grid: 1D Chg, P/E, Div Yield, Beta, EPS, ROE, 52W Low, 52W High  
- **Street Commentary** (with AI disclaimer)  
- **Chart Pattern** SVG (Murphy reference)  
- **CFA Lens** (formula + explanation)  
- **Fun Fact**

### Options Education Section
- Rotating 12-concept sequence  
- Payoff diagram SVG  
- Applied example  
- Formula block  
- Fun fact

### Economics Section
- This Week's Economic Events (real data from Fed, BLS, BEA, ECB, RBA)  
- Impact labels: HAWKISH / DOVISH / NEUTRAL / RISK-OFF  
- Supply & Demand diagram SVG  
- CFA micro concept

### CFA Quiz Section
- 5 questions mandatory  
- Q1-2: Today's stock concepts  
- Q3: Options concept  
- Q4: Economics/macro  
- Q5: Wild card (rotation through all 10 topics)  
- Each answer shows calculation  
- Cumulative score tracking

### Glossary
- 4 terms relevant to today's content

### Footer
- ASTRA session log  
- Report URL  
- Next session preview

---

## CFA CURRICULUM SEQUENCE

### 10 Topics (Official CFA Institute)
1. Ethical & Professional Standards (15-20%)
2. Quantitative Methods (6-9%)
3. Economics (6-9%)
4. Financial Statement Analysis (11-14%)
5. Corporate Issuers (6-9%)
6. Equity Investments (11-14%)
7. Fixed Income (11-14%)
8. Derivatives (5-8%)
9. Alternative Investments (7-10%)
10. Portfolio Management (8-12%)

### Daily Question Distribution
- Q1: Today's stock concept (e.g., P/E for tech)
- Q2: Today's stock concept (different formula/numbers)
- Q3: Today's options concept
- Q4: Economics/macro
- Q5: Wild card (rotate through all 10 topics)

---

## OPTIONS EDUCATION SEQUENCE (12 Concepts)

1. Long Call
2. Long Put
3. Covered Call
4. Bull Call Spread
5. Bear Put Spread
6. Cash-Secured Put
7. Iron Condor
8. Protective Put (Portfolio Insurance)
9. Straddle / Strangle
10. Delta Hedging
11. IV Rank & Options Pricing
12. Greeks Deep Dive

---

## CHART PATTERN LIBRARY (Murphy)

- Bull Flag (Ch 6)
- Bear Flag (Ch 6)
- Breakout from Resistance (Ch 4)
- Double Bottom/W (Ch 5)
- Double Top/M (Ch 5)
- Head & Shoulders (Ch 5)
- Ascending Triangle (Ch 6)
- Descending Triangle (Ch 6)
- Support Bounce (Ch 4)
- Cup & Handle (Ch 6)

---

## ECONOMICS: S&D SCENARIOS (Rotate)

1. Interest rate cut → demand shifts right
2. Oil supply shock → supply shifts left
3. Tech earnings beat → labor demand shifts right
4. Fed rate hike → bond prices fall
5. Strong USD → export demand shifts left
6. Inflation spike → real wages fall → consumer spending shifts left

---

## DATA SOURCES

### Stocks
```python
import yfinance as yf
def get_stock_data(ticker):
    t = yf.Ticker(ticker)
    hist = t.history(period="2d")
    info = t.info
    return {
        'price': hist['Close'].iloc[-1],
        'prev_close': hist['Close'].iloc[-2],
        'change_pct': ((hist['Close'].iloc[-1] / hist['Close'].iloc[-2]) - 1) * 100,
        'pe': info.get('trailingPE'),
        'eps': info.get('trailingEps'),
        'beta': info.get('beta'),
        'div_yield': info.get('dividendYield'),
        'market_cap': info.get('marketCap'),
        'roe': info.get('returnOnEquity'),
        '52w_high': info.get('fiftyTwoWeekHigh'),
        '52w_low': info.get('fiftyTwoWeekLow'),
    }
```

### Macro
- Gold: `yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1]`
- VIX: `^VIX`
- 10Y Yield: `^TNX`
- S&P 500: `^GSPC`
- DXY: `DX-Y.NYB`
- Oil: `CL=F`
- BTC: `BTC-USD`

### Economic Events
- Federal Reserve calendar: federalreserve.gov
- BLS: bls.gov (CPI, jobs)
- BEA: Bureau of Economic Analysis (GDP)
- CME FedWatch Tool

---

## QUIZ RULES (STRICT)

### Every Question Must Have:
1. Topic label: `Q1 · Equity Valuation · P/E Ratio`
2. CFA tag badge: `CFA L1 · Equity · Chapter 41`
3. Question text with **bold key numbers**
4. Four options (A/B/C/D) each with:
   - Answer text
   - Calculation shown below: `→ $264.58 ÷ $7.91 = 33.45x ✓`
5. Feedback on selection (correct + why wrong answers fail)

### Distractors (Wrong Answers)
- Must be realistic (common mistakes)
- Show incorrect calculation so Dibs understands
- Never obviously silly

### Cumulative Tracking
File: `/home/astra/logs/quiz_log.json`
```json
{
  "2026-02-24": {
    "score": 4,
    "total": 5,
    "topics": ["Equity", "DuPont", "Options", "Macro", "Fixed Income"],
    "correct": [1,1,1,1,0]
  }
}
```

---

## FILE LOCATIONS (NUC)

- Quiz log: `/home/astra/logs/quiz_log.json`
- Daily log: `/home/astra/logs/daily_log.md`
- Report index: `/home/astra/logs/report_index.json`
- Archive index: GitHub Pages `daily5/index.html`

---

## ASTRA'S DAILY CHECKLIST

1. Fetch live data (gold, VIX, yields, S&P 500, DXY, oil, BTC, 5 stocks)
2. **Verify gold price** — must match current spot (~$5,000 Feb 2026)
3. Select 5 stocks from S&P 500 sequence, market cap order
4. Assign stock counter — each card shows position (e.g., "47 / 503")
5. Select chart pattern based on actual price action. Draw SVG.
6. Select CFA concept for each stock based on curriculum
7. Pull economic events from week's calendar
8. Draw S&D diagram for week's key macro theme
9. Advance options sequence — next concept in 12-step list
10. Draw options payoff SVG — always include
11. Generate 5 quiz questions with inline calculations
12. Write 4 glossary terms tied to today's content
13. Publish to GitHub Pages, update `report_index.json` and `index.html`
14. Update daily log on NUC at `/home/astra/logs/daily_log.md`
15. Send Telegram notification with report URL + today's quiz score

---

## SEPARATE REPORT: DAILY TRADE IDEA

- **Name:** "The Daily Trade Idea"
- **Frequency:** Daily, after market close
- **Content:** 1–3 high-conviction setups with entry/stop/target/R:R
- **Includes:** Chart pattern, trigger conditions, invalidation level
- **NO CFA content, NO quizzes, NO macro education**
- Template to be created separately

---

## MY ASSESSMENT

### Critical Path Items
1. ✅ Gold price fix (already identified and fixing)
2. ⚠️ Stock counter implementation (N/503) — new requirement
3. ⚠️ Trading setups removal — need to update template
4. ⚠️ Quiz mandatory — was already doing, but now stricter
5. ⚠️ AI disclaimer on all street commentary — new
6. ⚠️ 503 tickers (not 500) — update all counters
7. ⚠️ HTML template v7 — new design system

### Implementation Complexity
- **High:** New HTML template with full styling system
- **Medium:** Quiz engine with cumulative tracking
- **Medium:** Options education sequence (12 concepts)
- **Low:** Gold verification, stock counters, disclaimers

### Recommendations
1. **Phase 1:** Fix gold + implement critical fixes (counters, disclaimers, 503)
2. **Phase 2:** Deploy new HTML template with existing content
3. **Phase 3:** Build quiz engine with tracking
4. **Phase 4:** Full v7 feature parity (options sequence, S&D diagrams)

---

*Spec review complete. Ready to implement.*
