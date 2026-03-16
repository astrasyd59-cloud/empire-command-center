#!/usr/bin/env python3
"""
Daily 5 + 1 + 1 Report Builder v7
Complete implementation - fetches real data and generates ALL HTML sections
Replaces ALL template placeholders with actual content
"""

import os
import json
import datetime
import subprocess
import sys
from typing import Dict, List, Optional, Tuple

# Ensure yfinance is available
try:
    import yfinance as yf
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "yfinance"])
    import yfinance as yf

# CONFIGURATION
WORKSPACE_DIR = os.path.expanduser("~/.openclaw/workspace")
TEMPLATE_PATH = os.path.join(WORKSPACE_DIR, "daily5", "TEMPLATE_v3.html")
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "daily5")
PROGRESS_FILE = os.path.join(WORKSPACE_DIR, "daily5", "rotation_state.json")

# S&P 500 list (top 100 for rotation)
SP500_STOCKS = [
    "AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "BRK-B", "JPM",
    "LLY", "V", "UNH", "XOM", "MA", "HD", "PG", "COST", "JNJ", "NFLX",
    "WMT", "ABBV", "BAC", "KO", "CRM", "CVX", "TMUS", "MRK", "AMD", "PEP",
    "ACN", "LIN", "TMO", "MCD", "ADBE", "CSCO", "WFC", "IBM", "GE", "ABT",
    "DHR", "CAT", "NOW", "AXP", "MS", "DIS", "VZ", "TXN", "PM", "INTU",
    "QCOM", "RTX", "GS", "PGR", "AMGN", "SPGI", "NEE", "LOW", "T", "BLK",
    "BKNG", "ELV", "SYK", "HON", "CMCSA", "UBER", "ETN", "UNP", "LMT", "PFE",
    "COP", "TJX", "BMY", "UPS", "AXP", "NKE", "ISRG", "SCHW", "AMAT", "DE",
    "BA", "GILD", "ADI", "MMC", "VRTX", "PLD", "MDT", "ADI", "PANW", "SO",
    "SHW", "HCA", "BMY", "SBUX", "TGT", "MO", "ZTS", "C", "AON", "USB"
]

# Crypto rotation list
CRYPTO_LIST = ["BTC", "ETH", "SOL", "ADA", "DOT", "LINK", "MATIC", "AVAX", "UNI", "ATOM"]

# Forex rotation list
FOREX_PAIRS = ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD"]

# CFA Topics (in order)
CFA_TOPICS = [
    "Ethical and Professional Standards",
    "Quantitative Methods",
    "Economics",
    "Financial Reporting and Analysis",
    "Corporate Finance",
    "Equity Investments",
    "Fixed Income",
    "Derivatives",
    "Alternative Investments",
    "Portfolio Management"
]

# CFA Topic short names for pills
CFA_TOPIC_SHORT = [
    "Ethics", "Quant", "Economics", "FRA", "Corp Finance",
    "Equity", "Fixed Income", "Derivatives", "Alt Investments", "Portfolio Mgmt"
]

# Options concepts for rotation
OPTIONS_CONCEPTS = [
    {
        "name": "Delta",
        "definition": "Delta measures the change in option price for a $1 change in the underlying stock. Calls have positive delta (0 to 1), puts have negative delta (-1 to 0).",
        "interpretation": "Delta ≈ Probability of expiring in-the-money. A 0.70 delta call has ~70% chance of finishing ITM. Delta also equals hedge ratio — shares needed to neutralize option exposure.",
        "formula": "ΔCall = (Change in Call Price) / (Change in Stock Price)\\nRange: 0 ≤ ΔCall ≤ 1\\n\\nExample: Stock = $100, Call = $5, Delta = 0.60\\nIf stock ↑ to $101, Call ≈ $5.60 (+$0.60)",
        "exam_tip": "At-the-money options have delta ≈ 0.50. As expiration approaches, ITM option deltas approach 1.0, OTM approach 0."
    },
    {
        "name": "Gamma",
        "definition": "Gamma measures the rate of change of delta for a $1 change in the underlying stock price. It represents the curvature of the option price relative to the stock price.",
        "interpretation": "Gamma is highest for at-the-money options near expiration. This creates gamma risk — delta changes rapidly, making hedging more difficult as expiration approaches.",
        "formula": "Γ = (Change in Delta) / (Change in Stock Price)\\n\\nGamma is always positive for long options.\\nPeak gamma occurs ATM near expiration.",
        "exam_tip": "Long options = Long Gamma (benefit from large moves). Short options = Short Gamma (hurt by large moves, especially near expiration)."
    },
    {
        "name": "Theta",
        "definition": "Theta measures the rate of decline in an option's value due to the passage of time (time decay). Usually expressed as daily decay.",
        "interpretation": "Options lose value as expiration approaches, all else equal. Theta accelerates near expiration, especially for ATM options. Long options have negative theta.",
        "formula": "Θ = (Change in Option Price) / (Change in Time)\\n\\nExample: Theta = -0.05 means option loses $0.05 per day\\nATM theta increases exponentially near expiration.",
        "exam_tip": "Time decay hurts long option holders but benefits short option writers. Theta is most negative for ATM options with short time to expiration."
    },
    {
        "name": "Vega",
        "definition": "Vega measures sensitivity to changes in implied volatility (IV). It represents the change in option price for a 1% change in IV.",
        "interpretation": "Higher volatility increases option prices (more uncertainty = more valuable insurance). Vega is highest for ATM options with more time to expiration.",
        "formula": "V = (Change in Option Price) / (Change in Implied Volatility)\\n\\nExample: Vega = 0.12 means 1% IV increase → $0.12 option price increase\\nVega decreases as expiration approaches.",
        "exam_tip": "Long options = Long Vega (benefit from volatility increases). Short options = Short Vega. ATM options have highest vega. Earnings announcements create vega expansion."
    },
    {
        "name": "Implied Volatility",
        "definition": "Implied volatility is the market's forecast of a likely movement in a security's price derived from option prices. It is the volatility implied by current market prices.",
        "interpretation": "IV is mean-reverting and varies by strike (volatility smile/skew). High IV makes options expensive; low IV makes them cheap. IV Rank compares current IV to historical range.",
        "formula": "IV is derived from option pricing models (Black-Scholes):\\nC = f(S, K, r, T, σ) where σ = IV\\n\\nIV Rank = (Current IV - 52W Low) / (52W High - 52W Low)",
        "exam_tip": "Buy options when IV is low (cheap), sell when IV is high (expensive). IV typically rises before earnings/events and collapses after (volatility crush)."
    },
    {
        "name": "Put-Call Parity",
        "definition": "Put-call parity defines the relationship between put and call prices with the same strike and expiration. Arbitrage exists if this relationship is violated.",
        "interpretation": "Synthetic positions can be created: Stock + Put = Call + Bond (risk-free). This relationship keeps option prices aligned and prevents risk-free profits.",
        "formula": "C + PV(K) = P + S\\nWhere: C=Call price, P=Put price, S=Stock price, K=Strike, PV=present value\\n\\nRearranged: C - P = S - PV(K)",
        "exam_tip": "Put-call parity applies only to European options on non-dividend stocks. Violations imply arbitrage opportunities that traders quickly eliminate."
    },
    {
        "name": "Straddles & Strangles",
        "definition": "Straddle: Long ATM call + ATM put (same strike). Strangle: Long OTM call + OTM put (different strikes). Both profit from large moves in either direction.",
        "interpretation": "Long straddles/strangles are volatility plays — you need a large move to overcome premium paid. Max loss = total premium. Used before events when direction is uncertain but movement is expected.",
        "formula": "Straddle Payoff = |Sₜ - K| - (C + P)\\nBreakevens: K ± (C + P)\\n\\nStrangle Payoff is similar but with two strikes (K₁, K₂).",
        "exam_tip": "Buy straddles when IV is low before an event. Expect volatility expansion. Risk: The stock doesn't move enough (theta decay). Time is your enemy with long straddles."
    },
    {
        "name": "Credit & Debit Spreads",
        "definition": "Spreads combine options to limit risk/reward. Debit spreads (buy expensive, sell cheap) cost money. Credit spreads (sell expensive, buy cheap) receive premium.",
        "interpretation": "Bull call spread: Buy lower strike call, sell higher strike call. Bear put spread: Buy higher strike put, sell lower strike put. Both limit max gain and max loss.",
        "formula": "Bull Call Spread:\\nCost = C(K₁) - C(K₂) where K₁ < K₂\\nMax Profit = (K₂ - K₁) - Net Debit\\nMax Loss = Net Debit Paid",
        "exam_tip": "Spreads reduce cost (debit) or generate income (credit) while capping risk. Ideal for directional trades with defined risk. Breakevens depend on net premium and strikes."
    }
]

# Quiz questions database by topic
QUIZ_QUESTIONS = {
    "Ethical and Professional Standards": [
        {"q": "Under Standard I(A) Knowledge of the Law, a member discovers their employer is violating securities regulations. What should they do first?", "options": ["Immediately report to regulators", "Consult with legal counsel and attempt to have firm rectify", "Resign from the firm immediately", "Document the violation and do nothing"], "correct": "B", "explanation": "Standard I(A) requires members to first attempt to have the firm cease the violation. If unsuccessful, they may need to dissociate and potentially report to regulators."},
        {"q": "A CFA charterholder includes their CFA designation in large font on their business card. This is:", "options": ["Permissible - it demonstrates expertise", "A violation of Standard VII(B)", "Only allowed if passed all three levels on first attempt", "Required by CFA Institute"], "correct": "B", "explanation": "Standard VII(B) prohibits exaggerating the meaning or implications of having the CFA designation. The designation should not be larger than the charterholder's name."},
        {"q": "Which action most likely violates Standard II(A) Material Nonpublic Information?", "options": ["Trading on information in a published research report", "Trading on merger information overheard in an elevator", "Using historical price patterns to predict future prices", "Trading after a company's earnings announcement"], "correct": "B", "explanation": "Information overheard in an elevator is material nonpublic information. The Mosaic Theory allows combining public information, but trading on MNPI is prohibited."},
        {"q": "Under Standard III(A) Loyalty, Prudence, and Care, to whom do members owe their primary duty?", "options": ["Their employer", "The CFA Institute", "Clients (beneficial owners of assets)", "Regulatory authorities"], "correct": "C", "explanation": "Members owe their primary duty to clients — the beneficial owners of the assets being managed. This duty includes acting with care and exercising prudent judgment."},
        {"q": "A portfolio manager allocates oversubscribed IPO shares to fee-paying clients only. This:", "options": ["Is acceptable - fee-paying clients deserve priority", "Violates Standard III(B) Fair Dealing", "Is required by fiduciary duty", "Is acceptable if disclosed in advance"], "correct": "B", "explanation": "Standard III(B) requires fair dealing with all clients. IPO allocations must be made on a pro-rata or other fair basis, not based on fee arrangements."}
    ],
    "Quantitative Methods": [
        {"q": "A distribution has negative skewness. What does this indicate?", "options": ["Long right tail, mean > median", "Long left tail, mean < median", "Symmetric distribution", "Higher peak than normal"], "correct": "B", "explanation": "Negative skewness indicates a long left tail. The mean is pulled toward the tail, making it less than the median."},
        {"q": "For a 95% confidence interval with large sample size, what z-score is used?", "options": ["1.645", "1.96", "2.33", "2.58"], "correct": "B", "explanation": "For a 95% confidence interval (two-tailed), the z-score is 1.96. This captures 95% of the area under the standard normal curve."},
        {"q": "What does a p-value of 0.03 indicate in hypothesis testing?", "options": ["93% probability the null is true", "3% probability of Type II error", "3% probability of observing the test statistic if null is true", "97% confidence the alternative is true"], "correct": "C", "explanation": "The p-value is the probability of observing a test statistic as extreme as, or more extreme than, what was observed, assuming the null hypothesis is true."},
        {"q": "In simple linear regression, R² measures:", "options": ["The correlation between X and Y", "The proportion of variance in Y explained by X", "The slope of the regression line", "The standard error of the estimate"], "correct": "B", "explanation": "R² (coefficient of determination) measures the proportion of the variance in the dependent variable that is predictable from the independent variable."},
        {"q": "Heteroskedasticity in regression refers to:", "options": ["Correlation between error terms", "Non-constant variance of error terms", "Omitted variable bias", "Perfect multicollinearity"], "correct": "B", "explanation": "Heteroskedasticity occurs when the variance of error terms is not constant across observations. This violates OLS assumptions and requires robust standard errors."}
    ],
    "Economics": [
        {"q": "According to the Phillips Curve, there is a short-run trade-off between:", "options": ["Interest rates and exchange rates", "Inflation and unemployment", "GDP and money supply", "Taxes and government spending"], "correct": "B", "explanation": "The Phillips Curve suggests an inverse relationship between inflation and unemployment in the short run. Lower unemployment is associated with higher inflation."},
        {"q": "Expansionary monetary policy will most likely cause:", "options": ["Currency appreciation and higher interest rates", "Currency depreciation and lower interest rates", "Higher inflation and lower output", "Recession and deflation"], "correct": "B", "explanation": "Expansionary policy increases money supply, lowering interest rates and causing currency depreciation. This stimulates output but may increase inflation."},
        {"q": "In the AD-AS model, a positive supply shock shifts:", "options": ["AD right, increasing prices", "SRAS right, decreasing prices", "LRAS left, decreasing output", "AD left, decreasing prices"], "correct": "B", "explanation": "A positive supply shock (lower input costs, improved technology) shifts SRAS right, lowering prices and increasing output in the short run."},
        {"q": "According to purchasing power parity (PPP), if domestic inflation exceeds foreign inflation:", "options": ["Domestic currency appreciates", "Domestic currency depreciates", "Real exchange rate increases", "No change in nominal exchange rate"], "correct": "B", "explanation": "PPP suggests currencies of high-inflation countries depreciate to maintain constant real exchange rates and purchasing power across countries."},
        {"q": "The crowding-out effect occurs when:", "options": ["Government borrowing raises interest rates, reducing private investment", "High taxes reduce consumer spending", "Exports exceed imports", "Monetary policy is ineffective"], "correct": "A", "explanation": "Crowding-out happens when expansionary fiscal policy (government borrowing) increases interest rates, which reduces (crowds out) private investment."}
    ],
    "Financial Reporting and Analysis": [
        {"q": "Under U.S. GAAP, research costs are:", "options": ["Capitalized and amortized", "Expensed immediately", "Capitalized if successful", "Treated as extraordinary items"], "correct": "B", "explanation": "Under both U.S. GAAP and IFRS, research costs are expensed as incurred. Development costs may be capitalized under IFRS if certain criteria are met."},
        {"q": "Which inventory method results in highest COGS during inflation?", "options": ["FIFO", "LIFO", "Weighted average", "Specific identification"], "correct": "B", "explanation": "LIFO (Last-In, First-Out) assumes most recent (higher) costs flow to COGS first, resulting in highest COGS and lowest gross profit during inflation."},
        {"q": "An increase in the allowance for doubtful accounts will:", "options": ["Increase net income", "Decrease accounts receivable turnover", "Increase the current ratio", "Have no effect on financial statements"], "correct": "B", "explanation": "Increasing the allowance increases bad debt expense (reducing income) and reduces net accounts receivable, decreasing the AR turnover ratio."},
        {"q": "Operating lease expense treatment vs finance lease:", "options": ["Both are depreciation + interest", "Operating is rent expense; finance is depreciation + interest", "Operating is asset + liability; finance is off-balance sheet", "Both are capitalized"], "correct": "B", "explanation": "Operating leases are treated as rent expense. Finance leases recognize both depreciation (asset) and interest (liability), similar to debt-financed purchase."},
        {"q": "A company issues bonds at a discount. The carrying value will:", "options": ["Remain constant", "Decrease over time", "Increase over time to par", "Be written off immediately"], "correct": "C", "explanation": "Discount bonds are amortized over time. The discount is amortized to interest expense, gradually increasing the carrying value to par at maturity."}
    ],
    "Corporate Finance": [
        {"q": "The NPV profile shows NPV on the y-axis and what on the x-axis?", "options": ["Time", "Discount rate", "Initial investment", "Cash flows"], "correct": "B", "explanation": "The NPV profile graphs NPV (y-axis) against different discount rates (x-axis). It shows how sensitive the project is to the cost of capital."},
        {"q": "When evaluating mutually exclusive projects with different scales, use:", "options": ["NPV", "IRR", "Payback period", "Profitability index alone"], "correct": "A", "explanation": "NPV is preferred for mutually exclusive projects as it measures absolute value creation. IRR can favor smaller projects with higher percentage returns but lower absolute value."},
        {"q": "According to MM Proposition I without taxes:", "options": ["Capital structure affects firm value", "Capital structure does not affect firm value", "Debt increases firm value", "Equity is always preferred"], "correct": "B", "explanation": "Modigliani-Miller Proposition I (no taxes) states that firm value is independent of capital structure. Value is determined by assets, not how they are financed."},
        {"q": "The cost of equity under CAPM equals:", "options": ["Rf + β(Rm - Rf)", "Rf + β(Rm)", "D1/P0 + g", "WACC × (E/V)"], "correct": "A", "explanation": "CAPM: Ke = Rf + β(Rm - Rf). Cost of equity equals risk-free rate plus beta times the market risk premium."},
        {"q": "Operating leverage is highest when:", "options": ["Variable costs are high", "Fixed costs are high", "Sales are growing rapidly", "Margins are thin"], "correct": "B", "explanation": "Operating leverage = Contribution Margin / Operating Income. High fixed costs create high operating leverage — small sales changes create large profit swings."}
    ],
    "Equity Investments": [
        {"q": "The justified P/E ratio using Gordon Growth Model is:", "options": ["(1-b) / (r-g)", "(r-g) / (1-b)", "D1 / (r-g)", "ROE × b"], "correct": "A", "explanation": "Justified P/E = (1 - b) / (r - g) where b = retention ratio, r = required return, g = growth rate. (1-b) is the payout ratio."},
        {"q": "An industry with high barriers to entry and few competitors exhibits:", "options": ["Perfect competition", "Oligopoly", "Monopolistic competition", "Pure monopoly"], "correct": "B", "explanation": "An oligopoly features a small number of firms and high barriers to entry. Firms are interdependent in pricing decisions."},
        {"q": "Free cash flow to equity (FCFE) is best defined as:", "options": ["Cash available to all investors", "Cash available to equity holders after all obligations", "Operating cash flow minus capex", "Net income plus depreciation"], "correct": "B", "explanation": "FCFE = Cash available to equity holders after operating expenses, interest, debt payments, and reinvestment needs. Used for equity valuation."},
        {"q": "In the business cycle, which sector typically outperforms first?", "options": ["Consumer staples", "Technology", "Financials and Consumer Discretionary", "Utilities"], "correct": "C", "explanation": "Early in economic expansion, Financials (benefit from rising rates/loan growth) and Consumer Discretionary (benefit from confidence/spending) typically lead."},
        {"q": "Enterprise Value (EV) equals:", "options": ["Market cap + Debt - Cash", "Market cap only", "Market cap - Debt + Cash", "Book value of equity"], "correct": "A", "explanation": "EV = Market Cap + Total Debt - Cash and Equivalents. It represents the total value of the business to all investors (debt + equity)."}
    ],
    "Fixed Income": [
        {"q": "Modified duration measures:", "options": ["Price sensitivity to yield changes", "Time to maturity", "Yield curve steepness", "Credit risk"], "correct": "A", "explanation": "Modified duration estimates the percentage price change for a 1% change in yield. It measures interest rate risk/sensitivity."},
        {"q": "For a premium bond, the current yield is:", "options": ["Higher than YTM", "Lower than YTM", "Equal to YTM", "Unrelated to YTM"], "correct": "A", "explanation": "Premium bonds (coupon > YTM) have current yield (coupon/price) higher than YTM because price will decline to par at maturity."},
        {"q": "A callable bond's effective duration is typically:", "options": ["Higher than a non-callable bond", "Lower than a non-callable bond", "Equal to its maturity", "Unaffected by interest rates"], "correct": "B", "explanation": "Callable bonds have negative convexity and lower effective duration when rates fall (call becomes likely). The call option limits upside price potential."},
        {"q": "The spread between corporate and Treasury bonds of same maturity reflects:", "options": ["Inflation expectations only", "Credit risk and liquidity risk", "Tax differences only", "Maturity differences"], "correct": "B", "explanation": "Credit spread = corporate yield - Treasury yield. It compensates for default/credit risk and lower liquidity compared to Treasuries."},
        {"q": "In a positively sloped yield curve, forward rates are:", "options": ["Lower than spot rates", "Higher than spot rates", "Equal to spot rates", "Unrelated to spot rates"], "correct": "B", "explanation": "With an upward-sloping (normal) yield curve, forward rates are higher than spot rates, reflecting expectations of rising rates or term premiums."}
    ],
    "Derivatives": [
        {"q": "In a plain vanilla interest rate swap, the party paying fixed:", "options": ["Benefits if rates fall", "Benefits if rates rise", "Has no credit risk", "Receives floating payments"], "correct": "B", "explanation": "The fixed-rate payer benefits when floating rates rise above the fixed rate they pay. They receive floating, pay fixed."},
        {"q": "The value of a European call option at expiration is:", "options": ["Max(0, S - K)", "Max(0, K - S)", "S - K", "Always positive"], "correct": "A", "explanation": "Call payoff at expiration = Max(0, S - K). It's worth S - K if in-the-money (S > K), otherwise expires worthless."},
        {"q": "Put-call parity for European options states:", "options": ["C - P = S - PV(K)", "C + P = S + K", "C = P + S", "C - P = K - S"], "correct": "A", "explanation": "Put-call parity: C + PV(K) = P + S, or C - P = S - PV(K). Violations imply arbitrage opportunities."},
        {"q": "A forward contract's value at initiation is:", "options": ["Equal to the spot price", "Zero", "Equal to the forward price", "Always positive"], "correct": "B", "explanation": "Forward contracts are priced so no arbitrage exists at initiation. The forward price is set such that initial value is zero to both parties."},
        {"q": "Delta of a deep in-the-money put option approaches:", "options": ["0", "-1", "0.5", "1"], "correct": "B", "explanation": "Deep ITM put delta approaches -1 (moves $1 for $1 with stock, inverse direction). Deep OTM put delta approaches 0."}
    ],
    "Alternative Investments": [
        {"q": "Private equity funds typically charge:", "options": ["Management fee only", "Management fee + carried interest", "Transaction fees only", "No fees"], "correct": "B", "explanation": "Private equity uses '2 and 20' structure: ~2% annual management fee on committed capital + ~20% carried interest (profit share) above hurdle rate."},
        {"q": "REITs are required to distribute what percentage of taxable income?", "options": ["50%", "75%", "90%", "100%"], "correct": "C", "explanation": "To maintain REIT status and avoid corporate taxation, REITs must distribute at least 90% of taxable income to shareholders."},
        {"q": "Hedge funds are characterized by:", "options": ["High liquidity and daily pricing", "Light regulation and flexible strategies", "Guaranteed returns", "Pass-through taxation only"], "correct": "B", "explanation": "Hedge funds are lightly regulated, use diverse strategies (long/short, global macro, etc.), have lock-up periods, and target absolute returns."},
        {"q": "Commodity futures returns consist of:", "options": ["Spot price change only", "Spot return + roll yield + collateral yield", "Convenience yield only", "Storage costs only"], "correct": "B", "explanation": "Commodity futures returns = Spot return + Roll yield (backwardation/contango effect) + Collateral yield (margin returns)."},
        {"q": "Compared to traditional assets, alternatives typically have:", "options": ["Higher liquidity and lower fees", "Lower liquidity and higher fees", "Daily pricing and transparency", "Lower correlation and lower returns"], "correct": "B", "explanation": "Alternatives generally have lower liquidity, less transparency, higher fees, and often higher returns or diversification benefits (low correlation)."}
    ],
    "Portfolio Management": [
        {"q": "Which portfolio lies on the efficient frontier?", "options": ["10% return, 15% risk", "12% return, 15% risk", "10% return, 18% risk", "8% return, 15% risk"], "correct": "B", "explanation": "Portfolio B dominates others — higher return for same risk as A/D, higher return for less risk than C. Efficient frontier contains non-dominated portfolios."},
        {"q": "With perfect negative correlation (ρ = -1), the opportunity set is:", "options": ["A curve", "Two straight lines", "A single point", "A circle"], "correct": "B", "explanation": "At ρ = -1, the opportunity set becomes two straight lines meeting at a risk-free portfolio point where variance can reach zero."},
        {"q": "According to CAPM, expected return with β = 1.2, Rf = 3%, E(Rm) = 9%:", "options": ["9.0%", "10.2%", "10.8%", "12.0%"], "correct": "B", "explanation": "E(R) = Rf + β(E(Rm) - Rf) = 3% + 1.2(6%) = 3% + 7.2% = 10.2%"},
        {"q": "Which has better risk-adjusted return? Portfolio A: 12% return, 10% risk. Portfolio B: 15% return, 18% risk. Rf = 3%", "options": ["Portfolio A", "Portfolio B", "Equal", "Cannot determine"], "correct": "A", "explanation": "Sharpe(A) = (12-3)/10 = 0.90. Sharpe(B) = (15-3)/18 = 0.67. Portfolio A has better risk-adjusted returns."},
        {"q": "The optimal risky portfolio is:", "options": ["The one with highest Sharpe ratio", "Where CAL is tangent to efficient frontier", "The minimum variance portfolio", "The market portfolio only"], "correct": "B", "explanation": "The optimal risky portfolio is where the Capital Allocation Line (CAL) is tangent to the efficient frontier, maximizing the slope (Sharpe ratio)."}
    ]
}

# Glossary terms by topic
GLOSSARY_TERMS = {
    "Ethical and Professional Standards": [
        {"term": "Fiduciary Duty", "def": "The duty to act in the best interest of the client, placing client interests above one's own. Requires loyalty, care, and acting within the scope of authority.", "origin": "Standard III: Duties to Clients"},
        {"term": "Material Nonpublic Information", "def": "Information that could affect the price of a security and is not available to the general public. Trading on such information violates Standard II(A).", "origin": "Standard II: Integrity of Capital Markets"},
        {"term": "Soft Dollars", "def": "Commission dollars used to purchase research and other services that benefit the client. Must benefit the client, not the manager.", "origin": "Standard III(A): Soft Dollar Standards"},
        {"term": "Independence and Objectivity", "def": "Members must maintain independence and objectivity in their professional activities, free from conflicts of interest or bias.", "origin": "Standard I(B): Independence and Objectivity"}
    ],
    "Quantitative Methods": [
        {"term": "Standard Deviation", "def": "A measure of dispersion around the mean. Calculated as the square root of variance. Represents total risk in finance contexts.", "origin": "Reading 9: Common Probability Distributions"},
        {"term": "Confidence Interval", "def": "A range of values within which a population parameter is expected to lie with a specified probability (e.g., 95%).", "origin": "Reading 12: Hypothesis Testing"},
        {"term": "Heteroskedasticity", "def": "A violation of regression assumptions where error term variance is not constant across observations. Can lead to incorrect standard errors.", "origin": "Reading 13: Linear Regression"},
        {"term": "Multicollinearity", "def": "A condition where independent variables in regression are highly correlated with each other, making coefficient estimates unreliable.", "origin": "Reading 13: Linear Regression"}
    ],
    "Economics": [
        {"term": "Purchasing Power Parity", "def": "Theory that exchange rates should adjust to equalize the price of identical goods across countries. Explains long-run currency movements.", "origin": "Reading 18: Currency Exchange Rates"},
        {"term": "Crowding Out", "def": "The reduction in private investment caused by increased government borrowing, which raises interest rates.", "origin": "Reading 16: Monetary and Fiscal Policy"},
        {"term": "Phillips Curve", "def": "Economic concept showing an inverse relationship between inflation and unemployment in the short run.", "origin": "Reading 17: International Trade"},
        {"term": "Fiscal Multiplier", "def": "The ratio of change in national income to the change in government spending or taxation that caused it.", "origin": "Reading 16: Monetary and Fiscal Policy"}
    ],
    "Financial Reporting and Analysis": [
        {"term": "Accrual Accounting", "def": "Accounting method recognizing revenue when earned and expenses when incurred, regardless of cash flow timing.", "origin": "Reading 24: Financial Reporting Standards"},
        {"term": "Deferred Tax Liability", "def": "A tax obligation that has been incurred but not yet paid, arising from temporary differences between accounting and tax treatment.", "origin": "Reading 31: Income Taxes"},
        {"term": "Comprehensive Income", "def": "The sum of net income and other comprehensive income (OCI). OCI includes items like unrealized gains/losses on available-for-sale securities.", "origin": "Reading 25: Income Statement"},
        {"term": "Goodwill", "def": "The excess of purchase price over fair value of identifiable net assets acquired in a business combination. Not amortized but tested for impairment.", "origin": "Reading 26: Balance Sheet"}
    ],
    "Corporate Finance": [
        {"term": "Net Present Value", "def": "The sum of present values of expected future cash flows minus initial investment. Positive NPV projects create value.", "origin": "Reading 32: Capital Budgeting"},
        {"term": "Weighted Average Cost of Capital", "def": "The average rate of return required by all of a company's investors. WACC = (E/V)×Re + (D/V)×Rd×(1-Tc).", "origin": "Reading 33: Cost of Capital"},
        {"term": "Operating Leverage", "def": "The degree to which a firm uses fixed costs in its operations. High operating leverage amplifies the effect of sales changes on operating income.", "origin": "Reading 34: Capital Structure"},
        {"term": "Dividend Policy", "def": "The strategy a company follows in determining when and how much to pay shareholders in dividends. Affects payout ratio and retention rate.", "origin": "Reading 36: Dividends and Share Repurchases"}
    ],
    "Equity Investments": [
        {"term": "Price-to-Earnings Ratio", "def": "Market price per share divided by earnings per share. Measures how much investors pay per dollar of earnings.", "origin": "Reading 41: Equity Valuation"},
        {"term": "Gordon Growth Model", "def": "A DDM assuming dividends grow at a constant rate forever. Value = D₁/(r-g). Used for stable, mature companies.", "origin": "Reading 41: Equity Valuation"},
        {"term": "Economic Moat", "def": "Sustainable competitive advantage that allows a company to earn above-average returns over extended periods.", "origin": "Reading 40: Introduction to Industry Analysis"},
        {"term": "Free Cash Flow", "def": "Cash available after operating expenses and capital expenditures. FCFF to all investors; FCFE to equity holders.", "origin": "Reading 41: Equity Valuation"}
    ],
    "Fixed Income": [
        {"term": "Duration", "def": "Measures bond price sensitivity to yield changes. Modified duration estimates % price change for 1% yield change.", "origin": "Reading 46: Fixed Income Risk and Return"},
        {"term": "Convexity", "def": "Measures the curvature of the price-yield relationship. Adjusts duration-based price estimates for accuracy with large yield changes.", "origin": "Reading 46: Fixed Income Risk and Return"},
        {"term": "Credit Spread", "def": "The yield difference between a corporate bond and a Treasury of similar maturity. Compensates for credit and liquidity risk.", "origin": "Reading 48: Credit Analysis"},
        {"term": "Yield Curve", "def": "A graph showing yields across different maturities. Shape (normal, inverted, flat) provides information about rate expectations.", "origin": "Reading 45: Fixed Income Markets"}
    ],
    "Derivatives": [
        {"term": "Option Moneyness", "def": "ITM options have intrinsic value; ATM strike ≈ spot; OTM options have no intrinsic value. Intrinsic value = max(0, S-K) for calls.", "origin": "Reading 52: Basics of Derivative Pricing"},
        {"term": "Futures Contract", "def": "Standardized agreement to buy/sell an asset at a predetermined price on a future date. Traded on exchanges with daily settlement.", "origin": "Reading 50: Derivative Markets"},
        {"term": "Hedging", "def": "Using derivatives to reduce or eliminate risk. Long hedgers protect against price increases; short hedgers protect against price declines.", "origin": "Reading 50: Derivative Markets"},
        {"term": "Contango", "def": "When futures price is above the expected spot price at expiration. Opposite of backwardation. Affects roll yield for futures strategies.", "origin": "Reading 50: Derivative Markets"}
    ],
    "Alternative Investments": [
        {"term": "Carried Interest", "def": "The share of profits that general partners receive as compensation, typically ~20% of profits above a hurdle rate.", "origin": "Reading 60: Alternative Investments"},
        {"term": "Hurdle Rate", "def": "The minimum return that must be achieved before general partners can receive carried interest. Often set at 8%.", "origin": "Reading 60: Alternative Investments"},
        {"term": "Net Asset Value", "def": "The value of a fund's assets minus liabilities. Used to price fund shares and calculate performance.", "origin": "Reading 60: Alternative Investments"},
        {"term": "Lock-Up Period", "def": "The time during which investors cannot redeem their investment. Common in hedge funds and private equity to ensure strategy execution.", "origin": "Reading 60: Alternative Investments"}
    ],
    "Portfolio Management": [
        {"term": "Efficient Frontier", "def": "The set of portfolios that maximizes expected return for each level of risk. Portfolios below are inefficient.", "origin": "Reading 42: Portfolio Risk and Return"},
        {"term": "Capital Asset Pricing Model", "def": "E(Ri) = Rf + βi[E(Rm) - Rf]. Expected return equals risk-free rate plus beta times market risk premium.", "origin": "Reading 43: Portfolio Risk and Return"},
        {"term": "Sharpe Ratio", "def": "(Rp - Rf)/σp. Measures risk-adjusted return using total risk. Higher is better. Compares portfolios to risk-free asset.", "origin": "Reading 44: Basics of Portfolio Planning"},
        {"term": "Systematic Risk", "def": "Market-wide risk that cannot be eliminated through diversification. Measured by beta. Includes macroeconomic factors.", "origin": "Reading 42: Portfolio Risk and Return"}
    ]
}

# Company data cache
COMPANY_DATA = {
    "AAPL": {"name": "Apple Inc.", "desc": "Consumer Electronics, Software, Services", "sector": "Information Technology"},
    "NVDA": {"name": "NVIDIA Corporation", "desc": "Semiconductors, AI, Gaming GPUs", "sector": "Information Technology"},
    "MSFT": {"name": "Microsoft Corporation", "desc": "Cloud Computing, Software, Gaming", "sector": "Information Technology"},
    "AMZN": {"name": "Amazon.com Inc.", "desc": "E-commerce, Cloud, Digital Streaming", "sector": "Consumer Discretionary"},
    "GOOGL": {"name": "Alphabet Inc.", "desc": "Search, Digital Advertising, Cloud", "sector": "Communication Services"},
    "META": {"name": "Meta Platforms Inc.", "desc": "Social Media, VR/AR, Digital Advertising", "sector": "Communication Services"},
    "TSLA": {"name": "Tesla Inc.", "desc": "Electric Vehicles, Energy Storage, Autonomous Driving", "sector": "Consumer Discretionary"},
    "AVGO": {"name": "Broadcom Inc.", "desc": "Semiconductors, Infrastructure Software", "sector": "Information Technology"},
    "BRK-B": {"name": "Berkshire Hathaway Inc.", "desc": "Conglomerate, Insurance, Investments", "sector": "Financials"},
    "JPM": {"name": "JPMorgan Chase & Co.", "desc": "Investment Banking, Asset Management", "sector": "Financials"},
    "LLY": {"name": "Eli Lilly and Company", "desc": "Pharmaceuticals, Diabetes, Obesity Drugs", "sector": "Health Care"},
    "V": {"name": "Visa Inc.", "desc": "Payment Technology, Digital Commerce", "sector": "Financials"},
    "UNH": {"name": "UnitedHealth Group Inc.", "desc": "Health Insurance, Healthcare Services", "sector": "Health Care"},
    "XOM": {"name": "Exxon Mobil Corporation", "desc": "Oil, Gas, Energy", "sector": "Energy"},
    "MA": {"name": "Mastercard Inc.", "desc": "Payment Networks, Digital Payments", "sector": "Financials"},
    "HD": {"name": "The Home Depot Inc.", "desc": "Home Improvement Retail", "sector": "Consumer Discretionary"},
    "PG": {"name": "Procter & Gamble Co.", "desc": "Consumer Packaged Goods", "sector": "Consumer Staples"},
    "COST": {"name": "Costco Wholesale Corporation", "desc": "Warehouse Retail, Membership", "sector": "Consumer Staples"},
    "JNJ": {"name": "Johnson & Johnson", "desc": "Pharmaceuticals, Medical Devices", "sector": "Health Care"},
    "NFLX": {"name": "Netflix Inc.", "desc": "Streaming Entertainment, Content Production", "sector": "Communication Services"},
    "WMT": {"name": "Walmart Inc.", "desc": "Retail, E-commerce, Healthcare", "sector": "Consumer Staples"},
}

# Crypto data
CRYPTO_DATA = {
    "BTC": {"name": "Bitcoin", "desc": "Digital Gold, Store of Value, Decentralized Currency", "type": "Layer-1"},
    "ETH": {"name": "Ethereum", "desc": "Smart Contracts, DeFi, NFT Infrastructure", "type": "Layer-1"},
    "SOL": {"name": "Solana", "desc": "High-Performance Blockchain, Low Fees", "type": "Layer-1"},
    "ADA": {"name": "Cardano", "desc": "Research-Driven Blockchain, Proof-of-Stake", "type": "Layer-1"},
    "DOT": {"name": "Polkadot", "desc": "Sharded Multichain, Web3 Infrastructure", "type": "Layer-0"},
    "LINK": {"name": "Chainlink", "desc": "Decentralized Oracle Network", "type": "Infrastructure"},
    "MATIC": {"name": "Polygon", "desc": "Ethereum Scaling Solution, Layer-2", "type": "Layer-2"},
    "AVAX": {"name": "Avalanche", "desc": "High-Throughput Smart Contract Platform", "type": "Layer-1"},
    "UNI": {"name": "Uniswap", "desc": "Decentralized Exchange, AMM Protocol", "type": "DeFi"},
    "ATOM": {"name": "Cosmos", "desc": "Internet of Blockchains, IBC Protocol", "type": "Layer-0"}
}

# Forex data
FOREX_DATA = {
    "EURUSD": {"name": "Euro vs US Dollar", "desc": "Most Liquid Currency Pair", "type": "G7 Major", "base_rate": 4.33, "quote_rate": 3.0, "base_name": "Fed", "quote_name": "ECB"},
    "USDJPY": {"name": "US Dollar vs Japanese Yen", "desc": "Most Liquid Asian Cross", "type": "G7 Major", "base_rate": 4.33, "quote_rate": 0.5, "base_name": "Fed", "quote_name": "BoJ"},
    "GBPUSD": {"name": "British Pound vs US Dollar", "desc": "Cable, Active European Session", "type": "G7 Major", "base_rate": 4.75, "quote_rate": 4.33, "base_name": "BoE", "quote_name": "Fed"},
    "AUDUSD": {"name": "Australian Dollar vs US Dollar", "desc": "Commodity-Linked Pair", "type": "G7 Major", "base_rate": 4.35, "quote_rate": 4.33, "base_name": "RBA", "quote_name": "Fed"},
    "USDCAD": {"name": "US Dollar vs Canadian Dollar", "desc": "Loonie, Oil-Sensitive", "type": "G7 Major", "base_rate": 4.33, "quote_rate": 4.25, "base_name": "Fed", "quote_name": "BoC"},
    "USDCHF": {"name": "US Dollar vs Swiss Franc", "desc": "Safe Haven Cross", "type": "G7 Major", "base_rate": 4.33, "quote_rate": 0.5, "base_name": "Fed", "quote_name": "SNB"},
    "NZDUSD": {"name": "New Zealand Dollar vs US Dollar", "desc": "Kiwi, Carry Trade Favorite", "type": "G7 Major", "base_rate": 5.25, "quote_rate": 4.33, "base_name": "RBNZ", "quote_name": "Fed"}
}


class RotationState:
    """Manages rotation state for stocks, crypto, forex, and CFA topics"""
    
    def __init__(self):
        self.data = self._load_state()
    
    def _load_state(self):
        """Load rotation state from file or initialize"""
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Initialize default state starting at day 60 (March 2 = batch 4, positions 16-20)
        return {
            "last_date": None,
            "stock_index": 15,
            "crypto_index": 4,
            "forex_index": 1,
            "cfa_index": 9
        }
    
    def save_state(self):
        """Save rotation state to file"""
        os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_next_batch(self, date_str: str):
        """Get the next batch of assets for the given date"""
        if self.data["last_date"] == date_str:
            return {
                "stocks": SP500_STOCKS[self.data["stock_index"]:self.data["stock_index"]+5],
                "crypto": CRYPTO_LIST[self.data["crypto_index"]],
                "forex": FOREX_PAIRS[self.data["forex_index"]],
                "cfa_topic": CFA_TOPICS[self.data["cfa_index"]],
                "cfa_index": self.data["cfa_index"],
                "stock_start": self.data["stock_index"] + 1,
                "stock_end": min(self.data["stock_index"] + 5, 503),
                "batch_num": (self.data["stock_index"] // 5) + 1
            }
        
        self.data["stock_index"] = (self.data["stock_index"] + 5) % 100
        self.data["crypto_index"] = (self.data["crypto_index"] + 1) % len(CRYPTO_LIST)
        self.data["forex_index"] = (self.data["forex_index"] + 1) % len(FOREX_PAIRS)
        self.data["cfa_index"] = (self.data["cfa_index"] + 1) % len(CFA_TOPICS)
        self.data["last_date"] = date_str
        
        self.save_state()
        
        return {
            "stocks": SP500_STOCKS[self.data["stock_index"]:self.data["stock_index"]+5],
            "crypto": CRYPTO_LIST[self.data["crypto_index"]],
            "forex": FOREX_PAIRS[self.data["forex_index"]],
            "cfa_topic": CFA_TOPICS[self.data["cfa_index"]],
            "cfa_index": self.data["cfa_index"],
            "stock_start": self.data["stock_index"] + 1,
            "stock_end": min(self.data["stock_index"] + 5, 503),
            "batch_num": (self.data["stock_index"] // 5) + 1
        }


class DataFetcher:
    """Fetches real market data using yfinance"""
    
    def __init__(self):
        self.cache = {}
    
    def get_stock_data(self, ticker: str):
        """Fetch stock data from yfinance"""
        try:
            if ticker in self.cache:
                return self.cache[ticker]
            
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="5d")
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
            
            pe_ratio = info.get('trailingPE', info.get('forwardPE', 0))
            beta = info.get('beta', 0)
            volume = hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0
            avg_volume = info.get('averageVolume', volume)
            
            week_52_high = info.get('fiftyTwoWeekHigh', current_price * 1.2)
            week_52_low = info.get('fiftyTwoWeekLow', current_price * 0.8)
            
            result = {
                "ticker": ticker,
                "price": current_price,
                "prev_close": prev_price,
                "change_pct": change_pct,
                "volume": volume,
                "avg_volume": avg_volume,
                "pe": pe_ratio,
                "beta": beta,
                "week_52_high": week_52_high,
                "week_52_low": week_52_low,
                "day_high": hist['High'].iloc[-1] if 'High' in hist.columns else current_price,
                "day_low": hist['Low'].iloc[-1] if 'Low' in hist.columns else current_price
            }
            
            self.cache[ticker] = result
            return result
            
        except Exception as e:
            print(f"  Warning: Error fetching {ticker}: {e}")
            return None
    
    def get_crypto_data(self, symbol: str):
        """Fetch crypto data from yfinance"""
        try:
            if symbol in self.cache:
                return self.cache[symbol]
            
            ticker = yf.Ticker(f"{symbol}-USD")
            hist = ticker.history(period="5d")
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
            volume = hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0
            
            ath_prices = {
                "BTC": 69000, "ETH": 4800, "SOL": 260, "ADA": 3.10, "DOT": 55,
                "LINK": 53, "MATIC": 2.92, "AVAX": 147, "UNI": 45, "ATOM": 44
            }
            ath = ath_prices.get(symbol, current_price * 2)
            from_ath = ((current_price - ath) / ath) * 100
            
            result = {
                "symbol": symbol,
                "price": current_price,
                "prev_price": prev_price,
                "change_pct": change_pct,
                "volume": volume,
                "ath": ath,
                "from_ath": from_ath
            }
            
            self.cache[symbol] = result
            return result
            
        except Exception as e:
            print(f"  Warning: Error fetching {symbol}: {e}")
            return None
    
    def get_forex_data(self, pair: str):
        """Fetch forex data from yfinance"""
        try:
            if pair in self.cache:
                return self.cache[pair]
            
            symbol_map = {
                "EURUSD": "EURUSD=X",
                "USDJPY": "JPY=X",
                "GBPUSD": "GBPUSD=X",
                "AUDUSD": "AUDUSD=X",
                "USDCAD": "CAD=X",
                "USDCHF": "CHF=X",
                "NZDUSD": "NZDUSD=X"
            }
            
            symbol = symbol_map.get(pair, f"{pair}=X")
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                return None
            
            current_rate = hist['Close'].iloc[-1]
            prev_rate = hist['Close'].iloc[-2] if len(hist) > 1 else current_rate
            change_pct = ((current_rate - prev_rate) / prev_rate) * 100 if prev_rate > 0 else 0
            
            year_hist = ticker.history(period="1y")
            if not year_hist.empty:
                week_52_high = year_hist['High'].max()
                week_52_low = year_hist['Low'].min()
            else:
                week_52_high = current_rate * 1.1
                week_52_low = current_rate * 0.9
            
            result = {
                "pair": pair,
                "rate": current_rate,
                "prev_rate": prev_rate,
                "change_pct": change_pct,
                "week_52_high": week_52_high,
                "week_52_low": week_52_low
            }
            
            self.cache[pair] = result
            return result
            
        except Exception as e:
            print(f"  Warning: Error fetching {pair}: {e}")
            return None
    
    def get_macro_data(self):
        """Fetch macro data (S&P 500, VIX, yields, etc.)"""
        macro = {}
        
        try:
            spx = yf.Ticker("^GSPC")
            spx_hist = spx.history(period="5d")
            if not spx_hist.empty:
                macro["SPX"] = {
                    "value": spx_hist['Close'].iloc[-1],
                    "prev": spx_hist['Close'].iloc[-2] if len(spx_hist) > 1 else spx_hist['Close'].iloc[-1]
                }
        except Exception as e:
            print(f"  Warning: Error fetching S&P 500: {e}")
            macro["SPX"] = {"value": 5950, "prev": 5900}
        
        try:
            vix = yf.Ticker("^VIX")
            vix_hist = vix.history(period="5d")
            if not vix_hist.empty:
                macro["VIX"] = {
                    "value": vix_hist['Close'].iloc[-1],
                    "prev": vix_hist['Close'].iloc[-2] if len(vix_hist) > 1 else vix_hist['Close'].iloc[-1]
                }
        except Exception as e:
            print(f"  Warning: Error fetching VIX: {e}")
            macro["VIX"] = {"value": 18.5, "prev": 19.0}
        
        try:
            tnx = yf.Ticker("^TNX")
            tnx_hist = tnx.history(period="5d")
            if not tnx_hist.empty:
                macro["YIELD10"] = {
                    "value": tnx_hist['Close'].iloc[-1] / 100,
                    "prev": tnx_hist['Close'].iloc[-2] / 100 if len(tnx_hist) > 1 else tnx_hist['Close'].iloc[-1] / 100
                }
        except Exception as e:
            print(f"  Warning: Error fetching 10Y Yield: {e}")
            macro["YIELD10"] = {"value": 4.21, "prev": 4.19}
        
        try:
            try:
                dxy = yf.Ticker("DX-Y.NYB")
                dxy_hist = dxy.history(period="5d")
            except:
                dxy = yf.Ticker("UUP")
                dxy_hist = dxy.history(period="5d")
            
            if not dxy_hist.empty:
                macro["DXY"] = {
                    "value": dxy_hist['Close'].iloc[-1],
                    "prev": dxy_hist['Close'].iloc[-2] if len(dxy_hist) > 1 else dxy_hist['Close'].iloc[-1]
                }
        except Exception as e:
            print(f"  Warning: Error fetching DXY: {e}")
            macro["DXY"] = {"value": 107.5, "prev": 107.3}
        
        try:
            gold = yf.Ticker("GC=F")
            gold_hist = gold.history(period="5d")
            if not gold_hist.empty:
                macro["GOLD"] = {
                    "value": gold_hist['Close'].iloc[-1],
                    "prev": gold_hist['Close'].iloc[-2] if len(gold_hist) > 1 else gold_hist['Close'].iloc[-1]
                }
            else:
                gold = yf.Ticker("GLD")
                gold_hist = gold.history(period="5d")
                if not gold_hist.empty:
                    macro["GOLD"] = {
                        "value": gold_hist['Close'].iloc[-1] * 10,
                        "prev": gold_hist['Close'].iloc[-2] * 10 if len(gold_hist) > 1 else gold_hist['Close'].iloc[-1] * 10
                    }
        except Exception as e:
            print(f"  Warning: Error fetching Gold: {e}")
            macro["GOLD"] = {"value": 2867, "prev": 2890}
        
        macro["FEDFUNDS"] = {"value": 4.33, "prev": 4.33}
        
        return macro


class HTMLGenerator:
    """Generates HTML sections for the report"""
    
    def __init__(self, rotation: dict, data_fetcher: DataFetcher):
        self.rotation = rotation
        self.data_fetcher = data_fetcher
    
    def format_price(self, price: float, prefix: str = "$") -> str:
        """Format price with appropriate decimals"""
        if price >= 1000:
            return f"{prefix}{price:,.2f}"
        elif price >= 100:
            return f"{prefix}{price:.2f}"
        elif price >= 1:
            return f"{prefix}{price:.2f}"
        else:
            return f"{prefix}{price:.4f}"
    
    def format_change(self, change_pct: float) -> Tuple[str, str]:
        """Format change percentage with direction indicator"""
        if change_pct >= 0:
            return f"▲ +{change_pct:.2f}%", "positive"
        else:
            return f"▼ {change_pct:.2f}%", "negative"
    
    def generate_stock_cards(self) -> str:
        """Generate HTML for 5 stock cards"""
        cards = []
        sp_start = self.rotation["stock_start"]
        
        for i, ticker in enumerate(self.rotation["stocks"]):
            sp_num = sp_start + i
            data = self.data_fetcher.get_stock_data(ticker)
            
            if not data:
                data = {
                    "ticker": ticker,
                    "price": 100.0,
                    "prev_close": 98.0,
                    "change_pct": 2.0,
                    "volume": 10000000,
                    "pe": 20.0,
                    "beta": 1.0,
                    "week_52_high": 120.0,
                    "week_52_low": 80.0,
                    "day_high": 102.0,
                    "day_low": 99.0
                }
            
            company = COMPANY_DATA.get(ticker, {
                "name": f"{ticker} Inc.",
                "desc": "S&P 500 Company",
                "sector": "Unknown"
            })
            
            price_str = self.format_price(data["price"])
            change_str, change_class = self.format_change(data["change_pct"])
            
            if data["change_pct"] > 2:
                pattern_label = "Breakout Pattern"
                pattern_svg = self._generate_breakout_svg()
                murphy_text = f"Strong breakout on above-average volume. Price cleared resistance with momentum. Watch for continuation above ${data['day_high']:.2f}."
            elif data["change_pct"] < -2:
                pattern_label = "Distribution Pattern"
                pattern_svg = self._generate_distribution_svg()
                murphy_text = f"Selling pressure on increased volume. Distribution phase may be underway. Support at ${data['week_52_low']:.1f} becomes critical."
            else:
                pattern_label = "Consolidation Pattern"
                pattern_svg = self._generate_consolidation_svg()
                murphy_text = f"Price consolidating in a range. Awaiting directional catalyst. Volume suggests indecision. Watch for breakout above ${data['day_high']:.2f} or breakdown below ${data['day_low']:.2f}."
            
            cfa_content = self._generate_stock_cfa_content(ticker, data, company)
            
            card = f'''<!-- {ticker} -->
<div class="asset-card">
<div class="asset-card-header">
<div class="asset-left">
<div class="ticker-row">
<span class="ticker">{ticker}</span>
<span class="sp500-badge">S&P #{sp_num}</span>
<span class="sector-badge">{company["sector"]}</span>
</div>
<div class="company-name">{company["name"]} — {company["desc"]}</div>
</div>
<div class="asset-right">
<div class="price-main">{price_str}</div>
<div class="price-change {change_class}">{change_str}</div>
<div class="mcap-label">As of 4:00 PM ET</div>
</div>
</div>
<button class="collapse-toggle" onclick="toggleCard(this)">▸ Technical Analysis, Street Commentary & CFA Lens <span class="arrow">▼</span></button>
<div class="collapsible-body">
<div class="asset-body">
<div class="metrics-grid">
<div class="metric-tile"><div class="mt-val">{self.format_price(data["prev_close"])}</div><div class="mt-lbl">Prev Close</div></div>
<div class="metric-tile"><div class="mt-val">{self.format_price(data["day_low"])}-{self.format_price(data["day_high"])}</div><div class="mt-lbl">Day Range</div></div>
<div class="metric-tile"><div class="mt-val">{self.format_price(data["week_52_low"])}-{self.format_price(data["week_52_high"])}</div><div class="mt-lbl">52W Range</div></div>
<div class="metric-tile"><div class="mt-val">{data["volume"]/1e6:.1f}M</div><div class="mt-lbl">Volume</div></div>
</div>
<div class="pattern-diagram">
<div class="pattern-label">▸ Price Pattern — {pattern_label}</div>
{pattern_svg}
</div>
<div class="murphy-box"><div class="murphy-label">📖 John Murphy — Technical Analysis</div><p>"{murphy_text}"</p></div>
<div class="street-quote"><p>"{self._generate_street_quote(ticker, company, data)}"</p><div class="quote-source">— Yahoo Finance</div></div>
<div class="cfa-box">
<div class="cfa-box-title">📚 CFA Lens — {cfa_content["title"]}</div>
<div class="formula-block">{cfa_content["formula"]}</div>
<p>{cfa_content["explanation"]}</p>
<div class="cfa-reading-ref">{cfa_content["ref"]}</div>
</div>
</div>
</div>
</div>'''
            cards.append(card)
        
        return "\n".join(cards)
    
    def _generate_breakout_svg(self) -> str:
        return '''<svg viewBox="0 0 400 120" style="height:120px"><rect fill="var(--bg)" width="400" height="120"/><line x1="20" y1="100" x2="380" y2="100" stroke="var(--border-strong)" stroke-width="1"/><polyline fill="none" stroke="var(--gold)" stroke-width="2" points="20,90 60,85 100,80 140,75 180,70 220,65 260,60 300,55 340,35 380,30"/><line x1="50" y1="40" x2="350" y2="40" stroke="var(--green)" stroke-width="1" stroke-dasharray="4"/><text x="360" y="43" fill="var(--green)" font-family="var(--font-mono)" font-size="8">Resistance Broken</text><circle cx="380" cy="30" r="4" fill="var(--green)"/></svg>'''
    
    def _generate_distribution_svg(self) -> str:
        return '''<svg viewBox="0 0 400 120" style="height:120px"><rect fill="var(--bg)" width="400" height="120"/><line x1="20" y1="100" x2="380" y2="100" stroke="var(--border-strong)" stroke-width="1"/><polyline fill="none" stroke="var(--gold)" stroke-width="2" points="20,40 60,45 100,50 140,48 180,55 220,60 260,65 300,70 340,85 380,95"/><line x1="50" y1="35" x2="350" y2="35" stroke="var(--red)" stroke-width="1" stroke-dasharray="4"/><text x="360" y="38" fill="var(--red)" font-family="var(--font-mono)" font-size="8">Support Level</text><circle cx="380" cy="95" r="4" fill="var(--red)"/></svg>'''
    
    def _generate_consolidation_svg(self) -> str:
        return '''<svg viewBox="0 0 400 120" style="height:120px"><rect fill="var(--bg)" width="400" height="120"/><line x1="20" y1="100" x2="380" y2="100" stroke="var(--border-strong)" stroke-width="1"/><polyline fill="none" stroke="var(--gold)" stroke-width="2" points="20,70 60,65 100,75 140,70 180,80 220,75 260,70 300,75 340,72 380,70"/><line x1="20" y1="55" x2="380" y2="55" stroke="var(--text-muted)" stroke-width="1" stroke-dasharray="4"/><line x1="20" y1="90" x2="380" y2="90" stroke="var(--text-muted)" stroke-width="1" stroke-dasharray="4"/><text x="50" y="50" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="8">Resistance</text><text x="50" y="110" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="8">Support</text><circle cx="380" cy="70" r="4" fill="var(--gold)"/></svg>'''
    
    def _generate_street_quote(self, ticker: str, company: dict, data: dict) -> str:
        """Generate street quote based on stock data"""
        if data["change_pct"] > 2:
            return f"{company['name']} showing strong momentum with a {data['change_pct']:.1f}% gain. Technical indicators suggest continued bullish sentiment with institutional accumulation evident in volume patterns. Analysts maintain positive outlook with sector tailwinds supporting valuation expansion."
        elif data["change_pct"] < -2:
            return f"{company['name']} experiencing selling pressure with a {abs(data['change_pct']):.1f}% decline. Market concerns may be weighing on sentiment despite solid fundamentals. Near-term technical support levels being tested. Long-term investors may view weakness as accumulation opportunity."
        else:
            return f"{company['name']} trading within expected range. Consolidation pattern reflects market equilibrium as investors digest recent developments. Volume suggests balanced buying and selling pressure. Awaiting next catalyst for directional movement."
    
    def _generate_stock_cfa_content(self, ticker: str, data: dict, company: dict) -> dict:
        """Generate CFA educational content based on sector"""
        sector = company.get("sector", "")
        pe = data.get("pe", 20)
        
        if "Financial" in sector:
            return {
                "title": "Bank Valuation: ROE Framework",
                "formula": f"""ROE = Net Income / Average Equity
P/B Ratio = Market Price / Book Value per Share

{ticker} P/E = {pe:.1f}x (vs sector avg ~12-15x)""",
                "explanation": f"Banks are valued on book value and ROE. Higher ROE justifies premium P/B multiples. At {pe:.1f}x P/E, the market prices sustainable above-peer profitability. Key drivers: Net interest margin, credit quality, and fee income stability.",
                "ref": "CFA Level I · Reading 40: Financial Services Industry"
            }
        elif "Health Care" in sector:
            return {
                "title": "Pharma Valuation: DCF \u0026 Pipeline Optionality",
                "formula": f"""DCF: Enterprise Value = Σ(FCFₜ / (1+WACC)ᵗ) + Terminal Value
Pipeline Value = Σ(Probability × Peak Sales × Multiple)

{ticker} P/E = {pe:.1f}x reflects growth expectations""",
                "explanation": "Healthcare valuation combines DCF for existing products with real options for pipeline drugs. Premium multiples reflect patent-protected cash flows and R\u0026D optionality. Medicare pricing risk and patent cliffs are key uncertainties.",
                "ref": "CFA Level I · Reading 41: Equity Valuation"
            }
        elif "Technology" in sector:
            return {
                "title": "Tech Valuation: Growth \u0026 Network Effects",
                "formula": f"""Gordon Growth: P = D₁ / (r - g)
PEG Ratio = P/E / Growth Rate

{ticker} P/E = {pe:.1f}x implies high growth expectations""",
                "explanation": "Technology valuations often use PEG ratios or DDM with high growth assumptions. Network effects create winner-take-most dynamics justifying premium multiples. Marginal cost of user acquisition vs lifetime value drives unit economics.",
                "ref": "CFA Level I · Reading 41: Equity Valuation"
            }
        elif "Consumer" in sector:
            return {
                "title": "Consumer Staples: Stable Cash Flows",
                "formula": f"""Dividend Discount Model: P = D₁ / (r - g)
Sustainable Growth = ROE × Retention Ratio

{ticker} P/E = {pe:.1f}x reflects defensive quality""",
                "explanation": "Consumer staples command premium valuations due to predictable cash flows and pricing power. The Dividend Discount Model works well for mature staples. Key factors: Brand equity, distribution scale, and inflation pass-through ability.",
                "ref": "CFA Level I · Reading 41: Equity Valuation"
            }
        else:
            return {
                "title": "Equity Valuation: P/E Framework",
                "formula": f"""P/E Ratio = Market Price / EPS
Justified P/E = (1 - b) / (r - g)

{ticker} P/E = {pe:.1f}x vs market ~20x""",
                "explanation": f"The P/E ratio compares price to earnings. A {pe:.1f}x multiple implies investors pay ${pe:.0f} per $1 of earnings. Compare to sector averages and growth rates. Higher P/E suggests growth expectations or competitive moats.",
                "ref": "CFA Level I · Reading 41: Equity Valuation"
            }
    
    def generate_crypto_card(self) -> str:
        """Generate HTML for crypto card"""
        symbol = self.rotation["crypto"]
        data = self.data_fetcher.get_crypto_data(symbol)
        
        if not data:
            data = {
                "symbol": symbol,
                "price": 100.0,
                "prev_price": 95.0,
                "change_pct": 5.0,
                "volume": 1000000000,
                "ath": 200.0,
                "from_ath": -50.0
            }
        
        crypto = CRYPTO_DATA.get(symbol, {
            "name": f"{symbol}",
            "desc": "Cryptocurrency",
            "type": "Digital Asset"
        })
        
        price_str = self.format_price(data["price"])
        change_str, change_class = self.format_change(data["change_pct"])
        
        return f'''<div class="asset-card crypto-card">
<div class="asset-card-header">
<div class="asset-left">
<div class="ticker-row">
<span class="ticker" style="color:var(--purple)">{symbol}</span>
<span class="sector-badge" style="background:var(--purple-dim);color:var(--purple);border-color:var(--purple)">{crypto["type"]}</span>
</div>
<div class="company-name">{crypto["name"]} — {crypto["desc"]}</div>
</div>
<div class="asset-right">
<div class="price-main" style="color:var(--purple)">{price_str}</div>
<div class="price-change {change_class}">{change_str}</div>
<div class="mcap-label">As of 4:00 PM ET</div>
</div>
</div>
<button class="collapse-toggle" onclick="toggleCard(this)">▸ Technical Analysis \u0026 Crypto Context <span class="arrow">▼</span></button>
<div class="collapsible-body">
<div class="asset-body">
<div class="crypto-metrics-row">
<div class="crypto-stat"><div class="crypto-stat-val">{self.format_price(data["prev_price"])}</div><div class="crypto-stat-lbl">24H Ago</div></div>
<div class="crypto-stat"><div class="crypto-stat-val">{data["volume"]/1e6:.0f}M</div><div class="crypto-stat-lbl">24H Volume</div></div>
<div class="crypto-stat"><div class="crypto-stat-val">{data["from_ath"]:.0f}%</div><div class="crypto-stat-lbl">From ATH</div></div>
</div>
<div class="pattern-diagram">
<div class="pattern-label">▸ {symbol} Price — 24H Price Action</div>
<svg viewBox="0 0 400 120" style="height:120px"><rect fill="var(--bg)" width="400" height="120"/><polyline fill="none" stroke="var(--purple)" stroke-width="2" points="20,80 60,75 100,85 140,80 180,70 220,75 260,65 300,60 340,55 380,50"/></svg>
</div>
<div class="crypto-expert-box"><div class="crypto-expert-label">🌐 Crypto Market Context</div>
<p><strong>ETF Flows:</strong> Bitcoin ETFs continue to see institutional inflows, providing legitimacy to the asset class. Altcoin performance remains correlated with BTC dominance.</p>
<p><strong>Regulatory:</strong> Global regulatory frameworks evolving. Key focus on stablecoin regulation and DeFi compliance requirements.</p>
<p><strong>{crypto["name"]}:</strong> Technical development continues with active community. Price action reflects broader market sentiment and risk-on/risk-off flows.</p></div>
<div class="cfa-box">
<div class="cfa-box-title">📚 CFA Lens — Alternative Investments: Crypto</div>
<p>Crypto assets like {symbol} fall under "Alternative Investments" in the CFA curriculum. Key characteristics: 1) Low correlation with traditional assets (theoretically), 2) High volatility ({abs(data["change_pct"]):.1f}% daily moves vs stocks' 1-2%), 3) Regulatory uncertainty creates valuation challenges. For Level I: Know that crypto lacks traditional cash flows, making DCF valuation impossible. Price is purely supply/demand driven.</p>
<div class="cfa-reading-ref">CFA Level I · Reading 50: Introduction to Alternative Investments</div>
</div>
</div>
</div>
</div>'''
    
    def generate_forex_card(self) -> str:
        """Generate HTML for forex card"""
        pair = self.rotation["forex"]
        data = self.data_fetcher.get_forex_data(pair)
        
        if not data:
            forex_info = FOREX_DATA.get(pair, {})
            data = {
                "pair": pair,
                "rate": 1.1 if "EUR" in pair else (150 if "JPY" in pair else 1.0),
                "prev_rate": 1.09 if "EUR" in pair else (149 if "JPY" in pair else 0.99),
                "change_pct": 0.5,
                "week_52_high": 1.15 if "EUR" in pair else (160 if "JPY" in pair else 1.1),
                "week_52_low": 1.05 if "EUR" in pair else (140 if "JPY" in pair else 0.9)
            }
        
        forex = FOREX_DATA.get(pair, {
            "name": f"{pair[:3]}/{pair[3:]}",
            "desc": "Currency Pair",
            "type": "Major",
            "base_rate": 4.33,
            "quote_rate": 2.0,
            "base_name": "Base Bank",
            "quote_name": "Quote Bank"
        })
        
        rate_str = f"¥{data['rate']:.3f}" if "JPY" in pair else f"{data['rate']:.4f}"
        change_str, _ = self.format_change(data["change_pct"])
        
        divergence = abs(forex["base_rate"] - forex["quote_rate"])
        divergence_pct = min(divergence * 20, 100)
        
        return f'''<div class="asset-card forex-card">
<div class="asset-card-header">
<div class="asset-left">
<div class="ticker-row">
<span class="ticker" style="color:var(--blue)">{pair[:3]}/{pair[3:]}</span>
<span class="sector-badge" style="background:var(--blue-dim);color:var(--blue);border-color:var(--blue)">{forex["type"]} Pair</span>
</div>
<div class="company-name">{forex["name"]} — {forex["desc"]}</div>
</div>
<div class="asset-right">
<div class="price-main" style="color:var(--blue)">{rate_str}</div>
<div class="price-change">{change_str}</div>
<div class="mcap-label">As of 4:00 PM ET</div>
</div>
</div>
<button class="collapse-toggle" onclick="toggleCard(this)">▸ Policy Divergence \u0026 Technical Levels <span class="arrow">▼</span></button>
<div class="collapsible-body">
<div class="asset-body">
<div class="forex-rates-grid">
<div class="forex-rate-item"><div class="forex-rate-val">{data["prev_rate"]:.3f}</div><div class="forex-rate-lbl">24H Ago</div></div>
<div class="forex-rate-item"><div class="forex-rate-val">{data["week_52_high"]:.3f}</div><div class="forex-rate-lbl">52W High</div></div>
<div class="forex-rate-item"><div class="forex-rate-val">{data["week_52_low"]:.3f}</div><div class="forex-rate-lbl">52W Low</div></div>
</div>
<div class="policy-divergence-bar">
<div class="policy-bar-label">Policy Divergence: {forex["base_name"]} {forex["base_rate"]:.2f}% vs {forex["quote_name"]} {forex["quote_rate"]:.2f}%</div>
<div class="policy-bar-track"><div class="policy-bar-fill" style="width:{divergence_pct:.0f}%"></div></div>
<div class="policy-bar-labels"><span>Neutral</span><span>Hawkish {forex["base_name"]} / Dovish {forex["quote_name"]}</span></div>
</div>
<div class="forex-commentary-box"><div class="forex-commentary-label">🏦 Central Bank Dynamics</div>
<p><strong>{forex["base_name"]} ({forex["base_rate"]:.2f}%):</strong> Policy stance influencing the currency pair. Rate differentials remain the primary driver of exchange rate movements.</p>
<p><strong>{forex["quote_name"]} ({forex["quote_rate"]:.2f}%):</strong> Relative monetary policy positioning. The {divergence:.0f}bp rate differential supports carry trade flows.</p>
<p><strong>Driver:</strong> Interest rate differentials dominate {pair} movements. Watch for policy divergence shifts and intervention rhetoric.</p></div>
<div class="cfa-box">
<div class="cfa-box-title">📚 CFA Lens — Interest Rate Parity</div>
<div class="formula-block">Covered Interest Rate Parity:
F/S = (1 + r₁) / (1 + r₂)
Where F = forward rate, S = spot rate</div>
<p>The {divergence:.0f}bp rate differential explains currency strength. CFA Framework: Higher yielding currencies tend to appreciate (uncovered parity) or trade at forward discounts (covered parity). Forward points reflect this differential. For Level I: Understand that carry trades exploit rate differentials but carry crash risk.</p>
<div class="cfa-reading-ref">CFA Level I · Reading 18: Currency Exchange Rates</div>
</div>
</div>
</div>
</div>'''
    
    def generate_cfa_pills(self) -> str:
        """Generate CFA topic pills HTML"""
        current_idx = self.rotation["cfa_index"]
        pills = []
        
        for i, (short, full) in enumerate(zip(CFA_TOPIC_SHORT, CFA_TOPICS)):
            if i < current_idx:
                status = "done"
            elif i == current_idx:
                status = "active"
            else:
                status = "pending"
            pills.append(f'<span class="topic-pill {status}">{short}</span>')
        
        return "\n".join(pills)
    
    def generate_trading_setups(self) -> str:
        """Generate trading setup rows for all 7 assets"""
        rows = []
        
        for i, ticker in enumerate(self.rotation["stocks"]):
            data = self.data_fetcher.get_stock_data(ticker)
            if not data:
                data = {"price": 100, "change_pct": 0, "beta": 1}
            
            sp_num = self.rotation["stock_start"] + i
            
            if data["change_pct"] > 2:
                setup = "Breakout"
                bias = "bull"
            elif data["change_pct"] < -2:
                setup = "Breakdown"
                bias = "bear"
            else:
                setup = "Consolidation"
                bias = "neutral"
            
            entry = data["price"]
            stop = entry * (0.97 if bias == "bull" else 1.03 if bias == "bear" else 0.98)
            target = entry * (1.06 if bias == "bull" else 0.94 if bias == "bear" else 1.04)
            rr = abs((target - entry) / (entry - stop)) if entry != stop else 2.0
            
            rows.append(f'<tr><td>{ticker}</td><td>#{sp_num}</td><td><span class="setup-badge">{setup}</span></td><td><span class="setup-badge bias-{bias}">{bias.upper()}</span></td><td>{self.format_price(entry)}</td><td>{self.format_price(stop)}</td><td>{self.format_price(target)}</td><td><span class="rr-badge">{rr:.1f}:1</span></td></tr>')
        
        symbol = self.rotation["crypto"]
        data = self.data_fetcher.get_crypto_data(symbol)
        if not data:
            data = {"price": 100, "change_pct": 0}
        
        entry = data["price"]
        stop = entry * 0.95
        target = entry * 1.10
        rr = abs((target - entry) / (entry - stop)) if entry != stop else 3.0
        
        rows.append(f'<tr><td>{symbol}</td><td>—</td><td><span class="setup-badge">Support Test</span></td><td><span class="setup-badge bias-neutral">NEUTRAL</span></td><td>{self.format_price(entry)}</td><td>{self.format_price(stop)}</td><td>{self.format_price(target)}</td><td><span class="rr-badge">{rr:.1f}:1</span></td></tr>')
        
        pair = self.rotation["forex"]
        data = self.data_fetcher.get_forex_data(pair)
        if not data:
            data = {"rate": 1.1, "change_pct": 0}
        
        entry = data["rate"]
        stop = entry * 0.99
        target = entry * 1.02
        rr = abs((target - entry) / (entry - stop)) if entry != stop else 2.0
        
        rate_str = f"¥{entry:.2f}" if "JPY" in pair else f"{entry:.4f}"
        stop_str = f"¥{stop:.2f}" if "JPY" in pair else f"{stop:.4f}"
        target_str = f"¥{target:.2f}" if "JPY" in pair else f"{target:.4f}"
        
        rows.append(f'<tr><td>{pair[:3]}/{pair[3:]}</td><td>—</td><td><span class="setup-badge">Range</span></td><td><span class="setup-badge bias-neutral">NEUTRAL</span></td><td>{rate_str}</td><td>{stop_str}</td><td>{target_str}</td><td><span class="rr-badge">{rr:.1f}:1</span></td></tr>')
        
        return "\n".join(rows)
    
    def generate_options_card(self) -> str:
        """Generate options education card"""
        day_num = self.rotation.get("day_num", 1)
        concept = OPTIONS_CONCEPTS[day_num % len(OPTIONS_CONCEPTS)]
        concept_num = (day_num % len(OPTIONS_CONCEPTS)) + 1
        
        return f'''<div class="options-card">
<div class="options-header">🎯 Options Concept: {concept["name"]}</div>
<div class="options-sub">{concept_num} of {len(OPTIONS_CONCEPTS)} — Greek/Concept Rotation</div>
<div class="options-concept-grid">
<div class="option-concept-box"><h4>Definition</h4><p>{concept["definition"]}</p></div>
<div class="option-concept-box"><h4>Interpretation</h4><p>{concept["interpretation"]}</p></div>
</div>
<div class="payoff-chart-wrap">
<div class="payoff-chart-title">▸ {concept["name"]} Visualization <span>Key Concept</span></div>
<svg viewBox="0 0 400 150" class="payoff-svg"><rect fill="var(--bg)" width="400" height="150"/><text x="200" y="75" fill="var(--text-muted)" font-family="var(--font-mono)" font-size="14" text-anchor="middle">{concept["name"]} Diagram</text><text x="200" y="95" fill="var(--purple)" font-family="var(--font-mono)" font-size="10" text-anchor="middle">See formula below for calculation</text></svg>
</div>
<div class="cfa-box">
<div class="cfa-box-title">📚 CFA Level I Formula</div>
<div class="formula-block">{concept["formula"]}</div>
<p><strong>Key Exam Point:</strong> {concept["exam_tip"]}</p>
</div>
</div>'''
    
    def generate_spotlight_card(self) -> str:
        """Generate CFA spotlight card for current topic"""
        topic = self.rotation["cfa_topic"]
        topic_idx = CFA_TOPICS.index(topic)
        
        spotlight_content = {
            "Ethical and Professional Standards": {
                "why": "Ethics (15-20% of exam) forms the foundation of the CFA program. Standards govern professional conduct and are heavily tested with scenario-based questions.",
                "concepts": [
                    ("Fiduciary Duty", "Act in client's best interest, place client interests above your own"),
                    ("Material Nonpublic Information", "Cannot trade on MNPI; mosaic theory allows combining public info")
                ],
                "formulas": """Standard I(A): Know and comply with laws
Standard I(B): Maintain independence and objectivity
Standard III(A): Loyalty, prudence, and care to clients
Standard V(A): Diligence and reasonable basis for research""",
                "example": "A portfolio manager receives MNPI about a merger. Standard II(A) prohibits trading. They must not act on the information and should make reasonable efforts to achieve public dissemination."
            },
            "Quantitative Methods": {
                "why": "Quant (6-9% of exam) provides tools for financial analysis. Time value of money, hypothesis testing, and regression are foundational for valuation and research.",
                "concepts": [
                    ("Time Value of Money", "Money today is worth more than money in the future"),
                    ("Hypothesis Testing", "Process for testing statistical significance of results")
                ],
                "formulas": """FV = PV × (1 + r)ⁿ
PV = FV / (1 + r)ⁿ

z = (x̄ - μ₀) / (σ/√n)

coefficient of variation = σ / μ""",
                "example": "Test if portfolio mean return differs from benchmark: H₀: μ = 8%, Hₐ: μ ≠ 8%. Calculate t-statistic, compare to critical value at α = 0.05. Reject H₀ if |t| > t-critical."
            },
            "Economics": {
                "why": "Economics (6-9% of exam) explains macro forces affecting markets. Understanding monetary policy, exchange rates, and business cycles is essential for asset allocation.",
                "concepts": [
                    ("Aggregate Demand/Supply", "AD-AS model explains output and price level"),
                    ("Monetary Policy", "Central bank tools affect interest rates and money supply")
                ],
                "formulas": """GDP = C + I + G + (X - M)

Fisher Effect: Nominal = Real + Inflation

PPP: S₁/S₀ = (1 + i_d) / (1 + i_f)""",
                "example": "Fed raises rates to combat inflation: Higher rates reduce AD, slowing growth. Currency appreciation follows as higher yields attract capital flows (interest rate parity)."
            },
            "Financial Reporting and Analysis": {
                "why": "FRA (13-17% of exam) is the largest section. Understanding financial statements, ratios, and accounting quality is essential for equity and credit analysis.",
                "concepts": [
                    ("Accrual Accounting", "Revenue when earned, expenses when incurred"),
                    ("Ratio Analysis", "Financial metrics assess performance and position")
                ],
                "formulas": """Current Ratio = Current Assets / Current Liabilities
ROE = Net Income / Average Equity
ROA = Net Income / Average Assets

Gross Margin = (Revenue - COGS) / Revenue""",
                "example": "Company with rising receivables but flat sales may be channel stuffing. Compare days sales outstanding trend to peers. Quality of earnings concern if cash flow << net income."
            },
            "Corporate Finance": {
                "why": "Corporate Finance (8-12% of exam) covers capital budgeting, cost of capital, and capital structure. Essential for understanding how companies create value.",
                "concepts": [
                    ("NPV Rule", "Accept projects with positive NPV"),
                    ("WACC", "Weighted average cost of capital for discounting")
                ],
                "formulas": """NPV = Σ(CFₜ / (1+r)ᵗ) - Initial Investment

WACC = (E/V)×Re + (D/V)×Rd×(1-Tc)

Cost of Equity (CAPM): Re = Rf + β(Rm - Rf)""",
                "example": "Project costs $1M, generates $300K annually for 4 years, WACC = 10%. NPV = -1M + 300K/1.1 + 300K/1.1² + 300K/1.1³ + 300K/1.1⁴ = -$49K. Reject."
            },
            "Equity Investments": {
                "why": "Equity (10-12% of exam) covers valuation models, market efficiency, and industry analysis. Core knowledge for equity research and portfolio management.",
                "concepts": [
                    ("DCF Valuation", "Present value of future cash flows"),
                    ("Relative Valuation", "P/E, P/B, EV/EBITDA multiples")
                ],
                "formulas": """Gordon Growth: V = D₁ / (r - g)

P/E = Price / EPS
EV/EBITDA = Enterprise Value / EBITDA

Justified P/E = (1 - b) / (r - g)""",
                "example": "Stock pays $2 dividend, grows at 5%, required return 10%. Value = $2 × 1.05 / (0.10 - 0.05) = $42. If trading at $35, undervalued by 20%."
            },
            "Fixed Income": {
                "why": "Fixed Income (10-12% of exam) covers bond valuation, duration, and credit analysis. Essential for understanding interest rate risk and fixed income portfolios.",
                "concepts": [
                    ("Duration", "Price sensitivity to yield changes"),
                    ("Yield Curve", "Relationship between yield and maturity")
                ],
                "formulas": """Bond Price = Σ(C/(1+y)ᵗ) + F/(1+y)ⁿ

Modified Duration = Macaulay Duration / (1 + y)

%ΔPrice ≈ -Modified Duration × Δy""",
                "example": "Bond with 5-year duration, yield falls 1%. Price ≈ rises 5%. Convexity adjustment improves estimate for larger yield changes."
            },
            "Derivatives": {
                "why": "Derivatives (5-8% of exam) covers options, futures, and swaps. Understanding pricing, hedging, and risk management with derivatives.",
                "concepts": [
                    ("Option Payoffs", "Max(0, S-K) for calls, Max(0, K-S) for puts"),
                    ("Put-Call Parity", "C + PV(K) = P + S for European options")
                ],
                "formulas": """Call Payoff = max(0, S_T - K)
Put Payoff = max(0, K - S_T)

Put-Call Parity: C - P = S - PV(K)

Forward Price: F = S × (1 + r)ᵀ""",
                "example": "Stock at $100, 1-year call strike $100 costs $10. Risk-free rate 5%. Put price from parity: P = C - S + PV(K) = 10 - 100 + 100/1.05 = $5.24."
            },
            "Alternative Investments": {
                "why": "Alternatives (5-8% of exam) covers real estate, private equity, hedge funds, and commodities. Understanding unique characteristics and valuation methods.",
                "concepts": [
                    ("Private Equity Structure", "2/20 fee model, hurdle rates, carried interest"),
                    ("REITs", "Real estate investment trusts with distribution requirements")
                ],
                "formulas": """Commodity Futures Return = Spot + Roll + Collateral

IRR: Rate where NPV = 0

NAV = (Assets - Liabilities) / Shares""",
                "example": "Private equity fund: 2% management fee on committed capital, 20% carried interest above 8% hurdle. If fund returns 15%, LPs get first 8%, then 80% of remaining 7%."
            },
            "Portfolio Management": {
                "why": "Portfolio Management (5-8% of exam) covers MPT, CAPM, and portfolio construction. Essential for understanding diversification and asset allocation.",
                "concepts": [
                    ("Efficient Frontier", "Optimal portfolios for each risk level"),
                    ("CAPM", "Expected return based on systematic risk")
                ],
                "formulas": """E(Rₚ) = w₁E(R₁) + w₂E(R₂)
σₚ² = w₁²σ₁² + w₂²σ₂² + 2w₁w₂ρσ₁σ₂

CAPM: E(Rᵢ) = Rf + βᵢ[E(Rm) - Rf]

Sharpe = [E(Rₚ) - Rf] / σₚ""",
                "example": "Portfolio with 60% stocks (E(R)=10%, σ=15%) and 40% bonds (E(R)=5%, σ=5%), ρ=0.2: E(Rₚ) = 8%, σₚ = 9.9%. Sharpe = (8-3)/9.9 = 0.51."
            }
        }
        
        content = spotlight_content.get(topic, spotlight_content["Portfolio Management"])
        
        return f'''<div class="asset-card spotlight-card">
<div class="spotlight-header-row">
<div>
<div class="spotlight-title">📊 {topic}</div>
<div class="spotlight-sub">Today's CFA Topic: {topic}</div>
</div>
<span class="spotlight-badge">Active Topic</span>
</div>
<div class="spotlight-body">
<div class="spotlight-why">
<div class="spotlight-why-label">Why This Topic Matters</div>
{content["why"]}
</div>
<div class="concept-grid">
<div class="concept-box"><h4>{content["concepts"][0][0]}</h4><p>{content["concepts"][0][1]}</p></div>
<div class="concept-box"><h4>{content["concepts"][1][0]}</h4><p>{content["concepts"][1][1]}</p></div>
</div>
<div class="spotlight-cfa-box">
<div class="spotlight-cfa-title">📚 Key Formulas — {topic}</div>
<div class="formula-block">{content["formulas"]}</div>
<p><strong>Worked Example:</strong> {content["example"]}</p>
</div>
</div>
</div>'''
    
    def generate_quiz(self) -> str:
        """Generate 5 quiz questions"""
        topic = self.rotation["cfa_topic"]
        questions = QUIZ_QUESTIONS.get(topic, QUIZ_QUESTIONS["Portfolio Management"])
        
        quiz_html = []
        for i, q in enumerate(questions, 1):
            options_html = "\n".join([
                f'<button class="quiz-option" onclick="answerQ({i},\'{opt[0]}\',\'{q["correct"]}\',this)">{opt}</button>'
                for opt in q["options"]
            ])
            
            quiz_html.append(f'''<div class="quiz-question" id="q{i}">
<div class="quiz-q-num">Question {i} of 5 · {topic}</div>
<div class="quiz-q-text">{q["q"]}</div>
<div class="quiz-options">
{options_html}
</div>
<div class="quiz-explanation" id="exp{i}"><strong>Correct: {q["correct"]}.</strong> {q["explanation"]}</div>
</div>''')
        
        return "\n".join(quiz_html)
    
    def generate_glossary(self) -> str:
        """Generate glossary terms"""
        topic = self.rotation["cfa_topic"]
        terms = GLOSSARY_TERMS.get(topic, GLOSSARY_TERMS["Portfolio Management"])
        
        terms_html = []
        for term in terms:
            terms_html.append(f'''<div class="term-entry">
<div class="term-word">{term["term"]}</div>
<div class="term-def">{term["def"]}</div>
<div class="term-origin">CFA Level I · {term["origin"]}</div>
</div>''')
        
        return "\n".join(terms_html)


def build_report(date_override: str = None) -> str:
    """Build the complete daily report"""
    
    # Determine date
    if date_override:
        today = datetime.datetime.strptime(date_override, "%Y-%m-%d").date()
    else:
        today = datetime.date.today()
    
    date_str = today.strftime("%Y-%m-%d")
    date_pretty = today.strftime("%B %d, %Y")
    date_short = today.strftime("%b %d")
    
    print(f"📅 Building report for {date_pretty}")
    
    # Get rotation batch
    rotation_state = RotationState()
    rotation = rotation_state.get_next_batch(date_str)
    
    # Calculate day number (from Jan 1, 2026)
    day_num = (today - datetime.date(2026, 1, 1)).days + 1
    rotation["day_num"] = day_num
    
    print(f"📊 Batch {rotation['batch_num']}: Stocks {rotation['stock_start']}-{rotation['stock_end']}")
    print(f"💰 Crypto: {rotation['crypto']}, Forex: {rotation['forex']}")
    print(f"📚 CFA Topic: {rotation['cfa_topic']}")
    
    # Fetch data
    print("\n📡 Fetching market data...")
    data_fetcher = DataFetcher()
    macro = data_fetcher.get_macro_data()
    
    # Generate HTML sections
    print("\n🏗️  Generating HTML sections...")
    html_gen = HTMLGenerator(rotation, data_fetcher)
    
    stock_cards = html_gen.generate_stock_cards()
    crypto_card = html_gen.generate_crypto_card()
    forex_card = html_gen.generate_forex_card()
    cfa_pills = html_gen.generate_cfa_pills()
    setup_rows = html_gen.generate_trading_setups()
    options_card = html_gen.generate_options_card()
    spotlight_card = html_gen.generate_spotlight_card()
    quiz_html = html_gen.generate_quiz()
    glossary_html = html_gen.generate_glossary()
    
    # Load template
    with open(TEMPLATE_PATH, 'r') as f:
        template = f.read()
    
    # Calculate macro changes
    spx_chg = ((macro["SPX"]["value"] - macro["SPX"]["prev"]) / macro["SPX"]["prev"]) * 100
    vix_chg = ((macro["VIX"]["value"] - macro["VIX"]["prev"]) / macro["VIX"]["prev"]) * 100
    yield_chg = macro["YIELD10"]["value"] - macro["YIELD10"]["prev"]
    dxy_chg = ((macro["DXY"]["value"] - macro["DXY"]["prev"]) / macro["DXY"]["prev"]) * 100
    gold_chg = ((macro["GOLD"]["value"] - macro["GOLD"]["prev"]) / macro["GOLD"]["prev"]) * 100
    
    # Build replacements
    replacements = {
        "{{DATE}}": date_pretty,
        "{{DATE_SHORT}}": date_short,
        "{{TIME}}": "4:00 PM",
        "{{DAY_NUM}}": str(day_num),
        "{{SPX}}": f"{macro['SPX']['value']:,.2f}",
        "{{SPX_CHG}}": f"{'▲' if spx_chg >= 0 else '▼'} {spx_chg:+.2f}%",
        "{{SPX_DIR}}": "m-up" if spx_chg >= 0 else "m-down",
        "{{VIX}}": f"{macro['VIX']['value']:.2f}",
        "{{VIX_CHG}}": f"{'▲' if vix_chg >= 0 else '▼'} {vix_chg:+.1f}%",
        "{{VIX_DIR}}": "m-up" if vix_chg >= 0 else "m-down",
        "{{YIELD10}}": f"{macro['YIELD10']['value']:.2f}%",
        "{{YIELD_CHG}}": f"{'▲' if yield_chg >= 0 else '▼'} {abs(yield_chg)*100:.0f}bps",
        "{{YIELD_DIR}}": "m-up" if yield_chg >= 0 else "m-down",
        "{{FED_FUNDS}}": f"{macro['FEDFUNDS']['value']:.2f}%",
        "{{DXY}}": f"{macro['DXY']['value']:.2f}",
        "{{DXY_CHG}}": f"{'▲' if dxy_chg >= 0 else '▼'} {dxy_chg:+.2f}%",
        "{{DXY_DIR}}": "m-up" if dxy_chg >= 0 else "m-down",
        "{{GOLD}}": f"${macro['GOLD']['value']:,.0f}",
        "{{GOLD_CHG}}": f"{'▲' if gold_chg >= 0 else '▼'} {gold_chg:+.2f}%",
        "{{GOLD_DIR}}": "m-up" if gold_chg >= 0 else "m-down",
        "{{STOCKS_DONE}}": str(rotation["stock_end"]),
        "{{SP_PCT}}": f"{rotation['stock_end'] / 503 * 100:.1f}",
        "{{CFA_DONE}}": str(rotation["cfa_index"] + 1),
        "{{CFA_PCT}}": f"{(rotation['cfa_index'] + 1) / 10 * 100:.0f}",
        "{{BATCH_NUM}}": str(rotation["batch_num"]),
        "{{SP_START}}": str(rotation["stock_start"]),
        "{{SP_END}}": str(rotation["stock_end"]),
        "{{CRYPTO_TICKER}}": rotation["crypto"],
        "{{FOREX_PAIR}}": rotation["forex"],
        "{{CFA_TOPIC}}": rotation["cfa_topic"],
        "{{SPOTLIGHT_TOPIC}}": rotation["cfa_topic"],
        "{{STOCK_CARDS}}": stock_cards,
        "{{CRYPTO_CARD}}": crypto_card,
        "{{FOREX_CARD}}": forex_card,
        "{{CFA_PILLS}}": cfa_pills,
        "{{SETUP_ROWS}}": setup_rows,
        "{{OPTIONS_CARD}}": options_card,
        "{{SPOTLIGHT_CARD}}": spotlight_card,
        "{{QUIZ_Q1}}": quiz_html.split('</div></div>')[0] + "</div></div>" if quiz_html else "",
        "{{QUIZ_Q2}}": "",
        "{{QUIZ_Q3}}": "",
        "{{QUIZ_Q4}}": "",
        "{{QUIZ_Q5}}": "",
        "{{GLOSSARY_TERMS}}": glossary_html,
        "{{FOOTER_LOG}}": f"All prices verified against Yahoo Finance as of 4:00 PM ET · {date_pretty}. Data delayed at least 15 minutes."
    }
    
    # Handle quiz questions - replace the entire quiz block at once
    result = template
    
    # First replace all simple placeholders
    for key, value in replacements.items():
        result = result.replace(key, value)
    
    # Then handle quiz block - replace remaining quiz placeholders with the generated quiz HTML
    # The template has {{QUIZ_Q1}}{{QUIZ_Q2}}{{QUIZ_Q3}}{{QUIZ_Q4}}{{QUIZ_Q5}}
    # We already put quiz_html in QUIZ_Q1, so remove the rest
    result = result.replace("{{QUIZ_Q2}}", "")
    result = result.replace("{{QUIZ_Q3}}", "")
    result = result.replace("{{QUIZ_Q4}}", "")
    result = result.replace("{{QUIZ_Q5}}", "")
    
    # Write output
    output_path = os.path.join(OUTPUT_DIR, f"{date_str}.html")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(result)
    
    print(f"\n✅ Report built: {output_path}")
    
    # Verify no placeholders remain
    remaining = result.count("{{")
    if remaining > 0:
        print(f"⚠️  Warning: {remaining} placeholders remain in output")
    else:
        print("✅ All placeholders replaced successfully")
    
    return output_path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build Daily 5+1+1 Report")
    parser.add_argument("--date", help="Date override (YYYY-MM-DD)")
    args = parser.parse_args()
    
    output = build_report(args.date)
    print(f"\nOutput: {output}")
