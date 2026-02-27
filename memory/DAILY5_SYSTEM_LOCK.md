# Daily 5 + 1 + 1 — System Lock

**Status:** ✅ FORMAT LOCKED — v6 Template Active
**Last Updated:** Feb 27, 2026

---

## 🔒 LOCKED CONFIGURATION

### Template
- **Version:** v6 (Feb 26 format)
- **Location:** `daily5/TEMPLATE_v3.html`
- **Features:** Dark/light theme, progress tracker, CFA pills, macro dashboard, trading setups, options ed, CFA quiz, glossary

### Schedule
- **Time:** 5:55 AM AEDT daily (every day including weekends)
- **Automation:** Cron job active
- **Delivery:** Telegram + GitHub Pages

### Data Source
- **Primary:** Yahoo Finance (yfinance)
- **Backup:** Manual input if APIs fail
- **No API keys required** for basic data

### Content Rotation

**S&P 500 (Sequential through all 503):**
- ✅ Feb 28: Positions 6-10 (WMT, JPM, V, MA, PG)
- ⏳ Mar 1: Positions 11-15 (LLY, HD, MRK, COST, PEP)
- 🔜 Next: Positions 16-20

**Crypto (Daily rotation, NO repeats):**
- ✅ Feb 28: SOL
- ⏳ Mar 1: ADA
- 🔜 Next: DOT, LINK, AVAX, MATIC (cycle through)

**Forex (Daily rotation):**
- ✅ Feb 28: EUR/USD
- ⏳ Mar 1: GBP/USD
- 🔜 Next: USD/JPY, AUD/USD, USD/CAD (cycle through)

**CFA Topics (Rotate through 10):**
1. Equity Valuation
2. Financial Reporting
3. Quantitative Methods
4. Corporate Finance
5. Fixed Income
6. Derivatives
7. Portfolio Management
8. Economics
9. Alternative Investments
10. Ethics

---

## ⚠️ CRITICAL REMINDERS

1. **Never use old templates** — Only TEMPLATE_v3.html
2. **Git push is mandatory** — Local updates don't show on GitHub Pages
3. **Rotation must continue** — Don't restart at position 1
4. **No BTC/ETH spam** — Crypto rotation is real, no repeats
5. **Weekends included** — 365 days/year, market open or not

---

## 📁 Files

- `daily5/YYYY-MM-DD.html` — Daily reports
- `daily5/TEMPLATE_v3.html` — Locked v6 template
- `daily5/generate_report.py` — Report builder script
- `daily5/data_YYYY-MM-DD.json` — Daily data cache

---

*Format locked. Do not deviate. Execute exactly.*
