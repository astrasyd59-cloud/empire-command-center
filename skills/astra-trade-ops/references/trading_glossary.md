# Trading Glossary

Terms, patterns, and concepts used in ASTRA trading operations.

## Chart Patterns (Murphy)

### Bull Flag
**Chapter 6 — Continuation Patterns**

Strong impulse rally (the pole) followed by tight, low-volume consolidation (the flag) against the trend. Breakout above the flag high confirms continuation.

- **Entry:** 4H close above flag high
- **Stop:** Below flag low or 1.5× ATR
- **Target:** Pole height projected from breakout
- **Volume:** Should dry up during flag, surge on breakout

### Bear Flag
**Chapter 6 — Continuation Patterns**

Sharp decline (the pole) followed by tight, low-volume bounce (the flag). Breakdown below flag low confirms continuation.

- **Entry:** 4H close below flag low
- **Stop:** Above flag high or 1.5× ATR
- **Target:** Pole height projected downward from breakdown

### Double Bottom
**Chapter 5 — Major Reversal Patterns**

Two nearly equal lows forming a W-shape. Confirmed on close above the neckline (the middle peak).

- **Entry:** 4H close above neckline
- **Stop:** Below second low
- **Target:** Distance from lows to neckline, projected upward
- **Note:** Second low can be slightly lower (undercut) to shake out weak hands

### Breakout from Resistance
**Chapter 4 — Trend Concepts**

Price breaking above a tested resistance level. Prior resistance becomes new support once confirmed.

- **Entry:** 4H close above resistance
- **Stop:** Below breakout level (now support)
- **Target:** Next resistance level or measured move
- **Volume:** Above-average volume confirms breakout

### Ascending Triangle
**Chapter 6 — Continuation Patterns**

Flat resistance with rising support — buyers becoming more aggressive each pullback.

- **Entry:** Close above flat resistance
- **Stop:** Below rising support trendline
- **Psychology:** Buyers willing to pay higher prices = bullish

### Descending Triangle
**Chapter 6 — Continuation Patterns**

Flat support with falling resistance — sellers becoming more aggressive.

- **Entry:** Close below flat support
- **Stop:** Above falling resistance trendline
- **Psychology:** Sellers in control, unable to rally back to highs

### Support Bounce
**Chapter 4 — Support and Resistance**

Price testing and holding at a known support level.

- **Entry:** Confirmation candle (bullish reversal) after test
- **Stop:** Below support level
- **Risk:** False break below support = immediate exit

---

## Technical Indicators

### EMA (Exponential Moving Average)
- **EMA 20:** Short-term trend direction
- **EMA 50:** Medium-term trend direction
- **Golden Cross:** EMA 20 crosses above EMA 50 = bullish
- **Death Cross:** EMA 20 crosses below EMA 50 = bearish

### RSI (Relative Strength Index)
- **Range:** 0-100
- **Overbought:** > 70 (possible reversal)
- **Oversold:** < 30 (possible bounce)
- **Divergence:** Price makes higher high, RSI makes lower high = bearish

### ATR (Average True Range)
- Measures volatility
- **ATR(14) on 4H:** Used for stop loss calculation
- **Stop formula:** Entry ± (1.5 × ATR)

---

## Order Types

### Market Order
Execute immediately at best available price. Use for entries when pattern confirms.

### Limit Order
Execute at specified price or better. Use for entry zones (buy at support).

### Stop Loss
Automatic exit when price reaches level. Hard stop = non-negotiable exit.

---

## Risk Management Terms

### R:R (Risk:Reward Ratio)
Potential reward divided by risk. Minimum 2:1 for valid ASTRA setup.

**Example:**
- Entry: $100
- Stop: $95 (risk $5)
- Target: $110 (reward $10)
- R:R = 10:5 = 2:1 ✓

### Position Sizing
Calculating how many units to trade based on 1% risk rule.

**Formula:**
```
Account risk = 1% of account value
Risk per unit = |Entry - Stop|
Position size = Account risk / Risk per unit
```

### Drawdown
Peak-to-trough decline in account value. Max acceptable = 15%.

### Sharpe Ratio
Risk-adjusted return. > 1.0 = good, > 2.0 = excellent.

---

## Market Terms

### CFD (Contract for Difference)
Derivative that tracks asset price without owning underlying. Used via CMC Markets/City Index.

### Spread
Difference between bid and ask price. Cost of entry/exit.

### Slippage
Difference between expected and actual fill price. Common in fast markets.

### Gap
Price jumps from previous close to new open without trading in between.

### Whipsaw
False breakout that quickly reverses. Stops out traders then continues original trend.

---

## COT (Commitment of Traders)

### Large Speculators
Hedge funds, CTA's, professional traders. Follow their positioning.

### Commercials
Producers/users hedging physical exposure. Often contrarian signal.

### Net Position
Longs minus shorts. Positive = net long, Negative = net short.

---

## Timeframes

| Timeframe | Use Case |
|-----------|----------|
| 1m/5m | Scalping, day trading |
| 15m/1h | Intraday swings |
| **4h** | **ASTRA primary — swing trades** |
| 1d | Trend direction, major levels |
| 1w | Long-term bias |

---

## ASTRA-Specific Terms

### 5-Gate Validation
System for filtering trades:
1. Macro clear (no major events)
2. Trend clear (above/below EMAs)
3. Pattern confirmed
4. COT supportive
5. R:R ≥ 2:1

### The Daily Trade Idea
Weekly report with 6 instruments, macro context, and trade setups.

### Phase 1/2/3/4/5
Hyperliquid roadmap phases:
- Phase 1: PostgreSQL setup ✓
- Phase 2: Hyperliquid account
- Phase 3: ASTRA cron agent
- Phase 4: Paper trading
- Phase 5: Live trading

---

## Quick Murphy Quotes

> "The trend is your friend until the end when it bends."

> "Volume should confirm the breakout. A price breakout on low volume is suspect."

> "Never chase a trend without a defined entry. Wait for the pattern."

> "Old support becomes new resistance, and old resistance becomes new support."

> "The most money is lost by trading in ranging markets. Patience preserves capital."
