# ABNB driver model: revenue decomposition, reaction function, scenarios and what the price implies

**What this is:** the first model layer for the pitch, built in Python (`analysis/src/abnb_driver_model.py`) on the margin-drivers branch's cost stack and FY26 to FY27 scenarios, the capital-return panel, and Theo's guidance dataset. Four parts: (1) quarterly revenue growth split into nights, ADR ex-FX, FX and take rate; (2) a regression of the day-one stock move on what each print contained; (3) bear, base and bull cases FY2026E to FY2028E run through every valuation lens the pitch landscape found in use; (4) the growth the current price already discounts. Assumptions with sources in `model/assumptions.md`.
**Compiled:** 2026-09-05. Author: Krishang, with Claude Code. Price used: $181.94 (4 Sep 2026 close). Outputs: `data/processed/abnb_driver_history_quarterly.csv`, `abnb_revenue_decomposition.csv`, `abnb_reaction_inputs.csv`, `abnb_reaction_regression.csv`, `abnb_valuation_scenarios.csv`, `abnb_valuation_sensitivity.csv`, `abnb_reverse_dcf.csv`, `abnb_multiples_today.csv`; figures `analysis/figures/abnb_revenue_decomposition.png`, `abnb_reaction_function.png`, `abnb_football_field.png`.
**Depends on:** `krish/margin-drivers` (cost lines, margin scenarios, capital-return panel) being merged first; the script reads those CSVs from `data/processed/`.

---

## 1. Bottom line

1. **Growth is nights plus mix, and 2026 has borrowed 3 to 4 points from FX.** Nights contributed 8 to 10 points of y/y revenue growth in every quarter since 2Q23. ADR ex-FX added 1 to 3 points through 2024 and 3 to 6 points from 3Q25 to 1Q26, then fell to 1.6 points in 2Q26. FX was a 2-point headwind in 1Q25 and a 3 to 4 point tailwind in 1H26. Take rate is a timing line (revenue at check-in, GBV at booking): -4 points in 3Q25 and 4Q25, +0.7 in 2Q26.
2. **The day-one move does not respond to the print's own numbers.** Across 18 guided prints (1Q22 to 2Q26), the revenue beat versus the guide midpoint explains 4% of the variance in the day-one excess return (coefficient +1.5 points per 1% beat, t = 0.9); adding next-quarter guide acceleration, margin change or nights growth gets to 5% to 7%. The company has beaten its own midpoint 19 times out of 19, so the beat is not news. The reaction runs on things not in this dataset: consensus (not guide), and the qualitative items (take-rate language, margin floor, S&M growth). Consensus at each call (plan branch 3) is the missing regressor, not more prints.
3. **Prints are sold on average.** Mean day-one excess return -1.1% (median -2.2%, 11 of 18 negative), mean five-day -3.1%, mean twenty-day -5.7%. The two biggest up days (2Q26 +16%, 4Q24 +14%) both followed a run of down prints; the pattern is mean-reverting positioning, not beats.
4. **At today's multiples the base case is worth $248 on EV/EBITDA and $172 on SBC-adjusted FCF.** FY2027E base: revenue $16.0B (+12%), Adj. EBITDA $5.8B (36.5%), FCF $5.8B, SBC $2.1B, 567M diluted shares. Holding today's 22x EV/EBITDA gives $248; 19x EV/FCF gives $217; 26x SBC-adjusted FCF gives $172; 26x the GAAP-ish earnings proxy ($6.25) gives $163. The bear case is $176 on EV/EBITDA (18x, revenue +4% in FY27, 33.8% margin), about today's price. Every Buy in the landscape is a multiple that holds or expands on an EBITDA lens; every Sell is a cash-after-SBC lens.
5. **What the price implies.** At 10% WACC and 3% terminal growth, $182 discounts 7.5% a year FCF growth for ten years on reported FCF, or 13.3% a year on SBC-adjusted FCF. Bernstein's "market implies 10.5% to 11%" sits between the two definitions. The base case grows FCF 12% in FY27 and 13% in FY28, so the stock is priced for the base case on reported FCF and for the bull case after SBC.

## 2. Where the stock is (30 Jun 2026 balance sheet, 4 Sep 2026 price)

| | Value |
|---|---|
| Price, diluted shares, market cap | $181.94, 597M, $108.6B |
| Net cash ex float (cash $6.8B + short-term investments $5.2B - notes $2.5B) | $9.6B |
| Funds held for clients (excluded from net cash) | $12.2B |
| EV | $99.0B |
| LTM revenue / Adj. EBITDA / FCF / SBC | $13.2B / $4.6B / $4.8B / $1.7B |
| EV / LTM EBITDA, EV / LTM FCF, EV / LTM revenue | 21.5x, 20.5x, 7.5x |
| FCF yield, SBC-adjusted FCF yield | 4.4%, 2.9% |
| P / LTM SBC-adjusted FCF | 34.7x |

The landscape's "4.2% SBC-adjusted yield at $140" is 2.9% at $182.

## 3. Revenue decomposition (log-additive, points of y/y growth)

| Quarter | Revenue y/y | Nights | ADR ex-FX | FX | Take rate (timing) |
|---|---|---|---|---|---|
| 1Q24 | +17.8% | 9.9 | 2.8 | 0.0 | 5.3 |
| 2Q24 | +10.6% | 8.8 | 2.2 | 0.0 | -0.4 |
| 3Q24 | +9.9% | 8.5 | 1.5 | 0.0 | 0.0 |
| 4Q24 | +11.8% | 12.3 | 0.9 | 0.0 | -1.6 |
| 1Q25 | +6.1% | 7.9 | 1.1 | -2.0 | -0.9 |
| 2Q25 | +12.7% | 7.6 | 3.1 | 0.0 | 1.7 |
| 3Q25 | +9.7% | 8.8 | 4.8 | 0.0 | -3.9 |
| 4Q25 | +12.0% | 9.9 | 5.1 | 1.0 | -3.6 |
| 1Q26 | +17.9% | 9.5 | 6.4 | 3.0 | -1.2 |
| 2Q26 | +16.5% | 10.6 | 1.6 | 4.0 | 0.7 |

Method: log(1 + revenue growth) = log(1 + nights growth) + log(1 + ADR growth) + log(1 + take-rate growth), each term scaled to points of reported growth; FX is the gap between reported and constant-currency revenue growth in Theo's `quarterly_actuals.csv`, attributed to ADR. Management's own ex-FX ADR (2Q26: +4%) is higher than this split's 1.6 points because the revenue FX effect (4 points) is larger than the ADR FX effect (1 point) when the float and timing move with FX; treat the ex-FX and FX columns together as "ADR" when in doubt. Full series from 1Q22 in the CSV; figure `abnb_revenue_decomposition.png`.

Read-through to the Inside Airbnb panel: same-listing listed prices fell 1% to 11% in 2025 in four cities while ADR ex-FX added 3 to 6 points. The gap is mix (larger homes, more entire homes, geography) and the fee-inclusive total-price display, not like-for-like rate.

## 4. Reaction function

Inputs per print (`abnb_reaction_inputs.csv`): revenue beat versus the prior guide midpoint and top of range, reported revenue and nights growth, next-quarter guide midpoint growth y/y and its acceleration versus the reported quarter, Adj. EBITDA margin change y/y, take-rate change y/y; day-one, five-day and twenty-day excess returns versus QQQ from Theo's `market_returns.csv`.

| Dependent | Regressors | n | R² | Beat coefficient (t) | Guide-acceleration coefficient (t) |
|---|---|---|---|---|---|
| Day-one excess | beat | 18 | 0.04 | +1.46 (0.9) | |
| Day-one excess | guide acceleration | 18 | 0.01 | | +0.10 (0.8) |
| Day-one excess | beat + guide | 18 | 0.05 | +1.54 (0.9) | +0.12 (1.0) |
| Day-one excess | beat + guide + margin y/y | 18 | 0.07 | +1.12 (0.5) | +0.30 (0.6) |
| Five-day excess | beat + guide | 18 | 0.06 | -0.58 (-0.3) | +0.28 (1.1) |

HC1 standard errors. Leave-one-out on the beat + guide spec keeps the beat coefficient between +0.9 and +2.6 and R² under 0.16 whichever print is dropped, so no single print (including 2Q26's +16%) makes or breaks it. Correlations with the day-one move: beat +0.20, guide acceleration +0.09, margin change +0.05, take-rate change -0.07.

What this says for 5 November: the guide cushion (about 2%, margin note 5.1) is known and will be met; the move will come from consensus positioning and from the take-rate and margin language. The expectations map (plan branch 9) should be built around consensus and the options-implied move, not around the beat.

## 5. Scenarios FY2026E to FY2028E

| | Bear | Base | Bull |
|---|---|---|---|
| FY27E revenue, growth | $14.6B, +4% | $16.0B, +12% | $16.7B, +15% |
| FY27E Adj. EBITDA margin | 33.8% | 36.5% | 39.8% |
| FY27E FCF, SBC-adjusted FCF | $4.5B, $2.5B | $5.8B, $3.8B | $7.0B, $5.0B |
| FY27E diluted shares | 575M | 567M | 562M |
| FY27E FCF per share, earnings proxy per share | $7.91, $4.94 | $10.27, $6.25 | $12.40, $7.60 |
| Price on EV / EBITDA (18x / 22x / 25.5x) | $176 | $248 | $325 |
| Price on EV / FCF (15x / 19x / 23x) | $140 | $217 | $309 |
| Price on P / SBC-adjusted FCF (20x / 26x / 32x) | $87 | $172 | $283 |
| Price on P / earnings proxy (20x / 26x / 32x) | $99 | $163 | $243 |
| FY28E revenue growth, margin | +6%, 33.5% | +11%, 37.0% | +14%, 40.5% |
| FY28E price on EV / EBITDA | $189 | $287 | $390 |

Sensitivity at the base multiple (22x) on FY27E, price by revenue growth and margin: +8% and 35% gives $230; +12% and 36.5% gives $247; +16% and 38% gives $265; +4% and 33% gives $211. Growth matters less than the multiple: moving FY27 growth from 4% to 16% at a fixed 36.5% margin is worth $24, moving the multiple from 18x to 25.5x on the base case is worth $77. Multiple-by-scenario grid in `abnb_valuation_sensitivity.csv`.

## 6. Reverse DCF: growth the price implies (10-year fade to terminal)

| Cash flow base (LTM) | WACC 9% | WACC 10% | WACC 11% |
|---|---|---|---|
| Reported FCF $4.8B, terminal 3% | 5.3% | 7.5% | 9.5% |
| Reported FCF, terminal 2.5% / 4% | 6.0% / 3.8% | 8.1% / 6.2% | 10.0% / 8.4% |
| SBC-adjusted FCF $3.1B, terminal 3% | 11.0% | 13.3% | 15.5% |
| SBC-adjusted FCF, terminal 2.5% / 4% | 11.7% / 9.3% | 13.9% / 11.9% | 16.0% / 14.3% |

## 7. What to build next

- **Consensus at call** (Bloomberg, plan branch 3): the reaction regression has no explanatory power without it; fill Theo's `consensus_snapshots.csv` and re-run `reaction()` with beat-versus-consensus and guide-versus-consensus.
- **Excel workbook** `model/ABNB_model.xlsx`: Drivers and Scenarios tabs from `model/assumptions.md`, Historicals from `abnb_driver_history_quarterly.csv`. The Python model is the source of truth until then.
- **Regional nights build** (NA, EMEA, LatAm, APAC at 42 / 39 / 9 / 9 percent of revenue) and a hotels/Experiences line, both zero in this model.
- **Post-print drift**: the -5.7% mean twenty-day excess return across 18 prints deserves its own test against the major-moves note before it goes on a slide.

## 8. Caveats

- 18 observations in the regression; the negative result is robust to leave-one-out but the sample cannot support more than two regressors.
- The earnings proxy is Adj. EBITDA less SBC less D&A plus net interest, taxed at 21%; it ignores other income, lodging-tax reserves and the corporate AMT charge that hit 1Q26, so it is a lens, not a GAAP forecast.
- FCF conversion above 100% depends on guest-float growth; a GBV slowdown cuts conversion before it cuts EBITDA.
- Share-count math assumes RSUs are issued at market and 35% withheld for tax; buybacks at a price rising 5% a year.
- FY2026E and FY2027E operating cases are the margin-drivers branch's; if that branch changes, re-run this script.
