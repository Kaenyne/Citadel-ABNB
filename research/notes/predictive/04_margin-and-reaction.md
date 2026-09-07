# ABNB predictive study 04: what explains the earnings-day reaction, and can the margin surprise be predicted?

- **Sources:** `data/external/abnb_earnings_reactions.csv` (ABNB vs QQQ 1/5/20-session moves for all 23 prints, from Theo's `market_returns.csv`); `data/processed/abnb_revenue_guidance_vs_actual.csv` (19 guided quarters); `data/processed/abnb_quarterly_kpis_from_study.csv` and `data/processed/abnb_quarterly_cost_stack_exsbc.csv` (1Q21 to 2Q26 KPIs, cash cost lines, SBC); the 44 `adj_ebitda_margin` rows of Theo's `guidance_items.csv` (branch `krish/guidance-margin-items`, copied to `data/external/guidance_items_with_margin.csv`); `research/notes/2026-09-05_margin-drivers.md` section 5 (margin guide by quarter); `data/processed/hotel_price_monitor_monthly.csv` (CPI lodging); `data/external/abnb_daily_close.csv`; `research/notes/2026-09-05_abnb-major-moves.md` (attributed causes). 2020 quarterly KPIs (needed for 2021 y/y) hand-entered from the shareholder letters and checked against the letter-stated growth rates. Prior work extended: Theo's IC brief (`theos-past-research/docs/forecasting/abnb_ic_brief/generated/metrics.json`): guidance y/y vs excess return r = 0.08 (n = 16), sequential guide change r = 0.03 (n = 19), direction aligned 7 of 19.
- **Date:** 2026-09-06
- **Author:** Krishang Surapaneni (compiled with Claude Code)
- **Scripts and outputs:** `analysis/src/predictive/04_reaction_function.py` -> `data/processed/predictive/04_print_features.csv` (22 prints, 2021Q1 to 2026Q2, 47 columns) and `04_reaction_results.csv` (394 rows: univariate, multivariate, two-way sorts, pre-print). `analysis/src/predictive/04_margin_predictability.py` -> `04_margin_predictability.csv` and `04_margin_predictability_quarters.csv`.

**Read this first.** Everything below is on n = 14 to 22 prints. The contemporaneous block runs 21 features x 3 horizons (63 tests per sample); the pre-print block 12 signals x 5 targets (60). At alpha = 0.05 each block is expected to throw about three false positives; a Bonferroni-corrected threshold is roughly p = 0.001, and no reaction result reaches it. Nothing here is a trading signal. The useful output is the ordering of what matters in the print and the small set of things that fail to matter.

---

## 1. Bottom line

1. **No single number in the letter explains the 1-day reaction.** The best contemporaneous features are the next-quarter revenue guide's y/y growth (r = +0.36, p = 0.12, n = 20), whether the quarter's margin guide held (r = +0.35, p = 0.14, n = 20) and the FY margin floor action (r = +0.28, p = 0.20, n = 22; from 2022Q1 r = +0.45, Spearman 0.51, p = 0.03). None passes a multiple-comparisons hurdle and the guide-level correlation collapses to r = +0.15 once the 2021 recovery prints are dropped, which is consistent with Theo's r = 0.08. The revenue beat itself is r = +0.24 (n = 19), and the beat-adjusted guide (guide above what the cushion pattern implies) is r = -0.03: the market does not reward the cushion.
2. **Direction is a nights-acceleration story, size is not.** Prints where nights growth accelerated versus the prior quarter were up on the day 7 of 9 times (mean excess +3.2%); decelerations were down 10 of 12 (mean -2.7%). Sign concordance 17 of 21 (81%, binomial p = 0.007; Mann-Whitney p = 0.06). Pearson r is only -0.18 because the 2021 base effects (+183 and -168 pts) dominate the magnitude, so treat this as a directional rule, not a slope. This is the quantitative version of the major-moves note: "earnings reactions key off nights, not the reported quarter."
3. **The double-miss cell is the only reliably bad one.** Below-median revenue beat and below-median guide-implied acceleration: 5 of 5 prints negative, mean 1-day excess -7.9%, 5-day -8.3%, 20-day -7.4% (2022Q2, 2022Q3, 2023Q1, 2023Q3, 2025Q2). Margin guide met with nights accelerating: 6 of 7 positive, mean +5.0%; margin met with nights decelerating: 2 of 11 positive, mean -2.1%. Margin met or missed on its own is uninformative (mean +0.7% vs -9.2%, but only 2 misses).
4. **The ex-ante 3-factor model has no out-of-sample value.** Nights acceleration + guide-implied acceleration + margin vs bound: in-sample R-squared 0.15 (1-day), leave-one-out R-squared -0.10; 5-day -2.3; 20-day -8.0. Coefficient signs are stable (0.95 to 1.00 of LOO fits) but none is significant (p 0.39 to 0.50). Do not use it for a point forecast of the move.
5. **One pre-print signal survives leave-one-out, with a caveat.** The prior quarter's S&M cash deleverage (S&M growth minus revenue growth, known at the prior print) correlates +0.59 with the next print's 1-day excess return (p = 0.014, permutation p = 0.014, Spearman 0.68, n = 17); LOO RMSE 7.9% versus 9.1% for the mean (LOO R-squared 0.24). It holds ex-2022Q3 (r = 0.59), ex-2026Q2 (0.55) and from 2023Q1 (0.66, n = 14). Sorted at the median: above-median prior deleverage, mean +3.5% (4 of 8 positive); below, -5.9% (1 of 9 positive). The mechanism is plausible (management says investment "front runs the revenue", so heavy S&M quarters precede nights acceleration) but it is one hit in 60 tests and the sign is counter-intuitive, so it is a hypothesis to test on 5 November, not a position. Every other pre-print signal (prior reaction, streak, prior beat size, guide width, guide y/y, FY floor action, 20-day run-up, hotel CPI) fails LOO against the mean for the 1-day target. The prior beat size does predict the 5-day excess negatively (r = -0.48, p = 0.044, LOO R-squared 0.19): a big beat last quarter is followed by a weaker week this quarter.
6. **Margin surprises are small, and management's directional margin guide has held 13 of 14 times since 1Q23.** Actual minus bound has mean +0.4 pts, median -0.5, range -2.5 to +6.3, RMSE 2.8 pts using the bound as the forecast. The one "miss" (2Q25, guided flat-to-down vs 32.5%, delivered 33.7%) was to the upside; so was the only other since 2022 (3Q22, guided at or below 49%, delivered 50.5%). The quarterly margin guide is a ceiling in 9 of the 14 quarters, and the ceiling has been set at the prior-year margin every time, so "margin vs bound" and "margin vs same quarter prior year" are the same number for those quarters.
7. **S&M deleverage is the only cost line with predictive content for margin, and most of it is arithmetic.** Contemporaneous S&M deleverage explains the y/y margin change with r = -0.82 (n = 14) and a coefficient of -0.24, which is simply S&M's 20 to 22% share of revenue. The lagged version (prior quarter's deleverage) is r = -0.62 (p = 0.017, permutation 0.017), LOO RMSE 2.6 pts versus 2.8 for the guide bound, 3.0 for "same as last quarter's surprise" and 3.0 for the mean. That is a 7% improvement over the guide on 14 points; the two-factor lagged model (ADR ex-FX + S&M deleverage) does not improve on the guide at all (2.78 vs 2.79). Ops-and-support per night, take-rate change, SBC ratio change, FX and hotel CPI all fail LOO against the naive forecasts when lagged. The contemporaneous margin model (ADR ex-FX + S&M deleverage) has LOO RMSE 2.0 pts versus 2.8 for the guide and 2.8 for the prior-year margin, but its inputs are in the print itself, so it explains rather than predicts.

---

## 2. Definitions

- **Print t** = the quarter reported. Targets: ABNB minus QQQ close-to-close over 1, 5 and 20 sessions from the reaction day (Theo's series; the 20-session window for 2026Q2 is not yet complete). Mean 1-day excess across the 22 prints: -0.1%, standard deviation 8.4%; 5-day mean -2.9%, 20-day mean -4.8% (the post-print drift is negative on average).
- **Contemporaneous features** (all in the letter): revenue vs guide midpoint and vs top of range (%); revenue, nights, GBV y/y and their acceleration vs prior quarter's y/y (pts); ADR y/y; take rate vs same quarter prior year (bps); Adjusted EBITDA margin vs same quarter prior year (pts); margin vs the bound guided for the quarter at the prior print (pts, economic sign: positive = above the bound; and met/missed); next-quarter guide midpoint y/y minus current reported y/y ("guide-implied acceleration", pts); guide midpoint grossed up by the trailing-4 average beat, as y/y, minus the trailing-4 average reported y/y ("guide vs cushion trend", pts); FY margin floor action (introduced / raised / held / none, scored 0.5 / 1 / 0 / 0; a floor at the same value as a prior point estimate counts as raised); S&M cash growth minus revenue growth (deleverage, pts); ops-and-support cash per night y/y (%); SBC % of revenue vs prior year (pts). Cost-line features start at 2022Q1 (no 2020 cost lines), so n = 18 for those.
- **Pre-print signals** (knowable before print t): prior print's 1-day excess and the signed streak of same-sign reactions; prior print's realised beat vs midpoint; the width and y/y of the guide for quarter t; the FY floor action at the prior print; prior quarter's S&M deleverage and its trailing-4 mean; prior quarter's margin vs bound and nights acceleration; quarter-average CPI lodging y/y; ABNB's raw 20-session run-up into the print (no QQQ daily series in the repo, so raw not excess).
- **Samples:** `all` (2021Q1 to 2026Q2), `from_2022Q1` (drops the pandemic-comp prints; acceleration features in 2021 are +183 / -168 pts), `ex_2026Q2` (drops the +16.3% outlier). All three are in the results CSV.

---

## 3. Feature ranking: 1-day excess return

Sorted by |Pearson r| on the full sample. Permutation p from 20,000 shuffles of the target. LOO R-squared is leave-one-out univariate OLS against the leave-one-out mean; negative means the feature forecasts worse than the mean.

| Feature | n | Pearson r | p | Spearman | perm p | LOO R2 | r from 2022Q1 |
|---|---|---|---|---|---|---|---|
| Next-quarter guide midpoint y/y | 20 | +0.36 | 0.12 | +0.31 | 0.12 | +0.07 | +0.15 |
| Margin guide met (1/0) | 20 | +0.35 | 0.14 | +0.38 | 0.12 | +0.11 | +0.34 |
| FY margin floor action score | 22 | +0.28 | 0.20 | +0.31 | 0.20 | -0.01 | +0.45 |
| Ops-and-support cash per night y/y | 18 | -0.26 | 0.30 | -0.29 | 0.30 | +0.01 | -0.26 |
| Revenue beat vs midpoint | 19 | +0.24 | 0.33 | +0.29 | 0.33 | -0.01 | +0.20 |
| Revenue beat vs top of range | 19 | +0.22 | 0.36 | +0.32 | 0.36 | -0.04 | +0.18 |
| GBV acceleration | 21 | -0.22 | 0.34 | -0.22 | 0.35 | -0.16 | -0.13 |
| Margin vs guide bound (pts) | 20 | +0.19 | 0.42 | +0.05 | 0.42 | -0.03 | +0.06 |
| Nights acceleration | 21 | -0.18 | 0.44 | +0.20 | 0.45 | -0.18 | +0.11 |
| ADR y/y | 22 | +0.17 | 0.44 | +0.32 | 0.45 | -0.02 | +0.06 |
| Revenue acceleration | 21 | -0.17 | 0.47 | +0.10 | 0.49 | -0.23 | +0.22 |
| Guide-implied acceleration | 20 | +0.11 | 0.65 | +0.17 | 0.66 | -0.02 | +0.09 |
| Revenue y/y | 22 | +0.10 | 0.65 | +0.12 | 0.63 | -0.37 | +0.06 |
| GBV y/y | 22 | +0.10 | 0.65 | +0.37 | 0.63 | -0.51 | +0.12 |
| Nights y/y | 22 | +0.09 | 0.68 | +0.34 | 0.66 | -0.27 | +0.11 |
| SBC % revenue change | 18 | -0.09 | 0.74 | -0.21 | 0.73 | -0.13 | -0.09 |
| Margin vs same quarter prior year | 22 | +0.08 | 0.73 | +0.13 | 0.71 | -0.21 | +0.05 |
| FY floor raised (1/0) | 22 | +0.07 | 0.75 | +0.07 | 0.75 | -0.09 | +0.18 |
| S&M deleverage | 18 | +0.07 | 0.79 | +0.16 | 0.79 | -0.06 | +0.07 |
| Guide vs cushion trend | 19 | -0.03 | 0.91 | +0.12 | 0.91 | -0.09 | +0.02 |
| Take rate vs prior year | 22 | +0.03 | 0.91 | -0.10 | 0.91 | -0.07 | -0.07 |

Longer horizons: for the 5-day excess the leader is guide vs cushion trend (r = +0.36, p = 0.13, n = 19; LOO R2 +0.08) then guide-implied acceleration (+0.30, p = 0.21; Spearman 0.46); for 20 days, guide vs cushion trend (+0.40, p = 0.10, n = 18), ADR y/y (+0.37, p = 0.10) and margin vs prior year (+0.34, p = 0.13). None is significant after any correction; the sign flip of the revenue beat between 1 day (+0.24) and 5 days (-0.17) says the beat is priced in the first session and then gives back.

**Extension of Theo's result.** His guide y/y vs excess return r = 0.08 used ABNB minus SPY next close for 16 events. Ours is +0.36 vs QQQ on 20 events, but +0.15 from 2022Q1: the difference is the 2021 prints, where +70% guides met +13% days. His direction-aligned 7 of 19 for the sequential guide compares with 13 of 20 (65%, binomial p = 0.26) for guide-implied acceleration here. Guidance level and direction still do not carry the reaction.

---

## 4. Two-way sorts

Mean 1-day excess return (%), with 5- and 20-day means and the share of prints positive on day 1.

**Revenue beat (above / below median of +2.5%) x guide-implied acceleration (above / below median of -3.9 pts).** The guide implied acceleration in the literal sense (guide y/y above reported y/y) only 3 times in 20, so the median split is the informative one; the zero split is in the CSV (above-median beat with a decelerating guide: n = 8, +2.9%; below-median beat with a decelerating guide: n = 9, -4.8%, median -8.4%).

| Cell | n | mean 1d | median 1d | mean 5d | mean 20d | share positive 1d |
|---|---|---|---|---|---|---|
| Beat above median, guide less deceleration | 4 | 0.0 | -0.8 | -0.5 | +0.6 | 25% |
| Beat above median, guide more deceleration | 5 | +5.5 | +4.3 | -3.9 | -8.5 | 80% |
| Beat below median, guide less deceleration | 5 | -0.9 | -0.5 | -0.4 | -7.2 | 40% |
| Beat below median, guide more deceleration | 5 | -7.9 | -8.4 | -8.3 | -7.4 | 0% |

Reading: the beat, not the guide, orders the cells on day 1, and the bottom-right cell is the only one with a consistent sign. The top-right cell (big beat, weak guide, +5.5%) is 2021Q4, 2022Q1, 2022Q4, 2024Q1 and 2024Q4, i.e. Q4 and Q1 prints, where the seasonal cushion is biggest and the guide for the small following quarter always looks like deceleration; the market has learned to look through it.

**Margin guide met / missed x nights acceleration / deceleration.**

| Cell | n | mean 1d | median 1d | mean 5d | mean 20d | share positive 1d |
|---|---|---|---|---|---|---|
| Margin met, nights accelerating | 7 | +5.0 | +4.3 | +1.4 | -0.6 | 86% |
| Margin met, nights decelerating | 11 | -2.1 | -2.8 | -4.3 | -6.5 | 18% |
| Margin missed, nights accelerating | 1 (2022Q3) | -10.0 | | -7.3 | -13.0 | 0% |
| Margin missed, nights decelerating | 1 (2025Q2) | -8.4 | | -6.9 | -5.3 | 0% |

**One-way splits, for reference (1-day excess):**

| Split | accel n / mean | decel n / mean | direction concordance | binomial p | Mann-Whitney p |
|---|---|---|---|---|---|
| Nights acceleration | 9 / +3.2 | 12 / -2.7 | 17 of 21 (81%) | 0.007 | 0.06 |
| Guide-implied acceleration (> 0) | 3 / +5.6 | 17 / -1.2 | 13 of 20 (65%) | 0.26 | 0.18 |
| Revenue acceleration | 7 / +0.8 | 14 / -0.6 | 13 of 21 (62%) | 0.38 | 0.49 |
| GBV acceleration | 9 / -0.2 | 12 / -0.1 | 13 of 21 (62%) | 0.38 | 0.75 |
| Margin guide met vs missed | 18 / +0.7 | 2 / -9.2 | 10 of 20 (50%) | 1.00 | 0.13 |

The nights result is the one that would survive a reasonable correction for the five one-way tests (0.007 x 5 = 0.035). Note that the two 2021 base-effect prints go the "right" way (2021Q2 accelerating +183 pts, +0.7%; 2021Q3 decelerating -168 pts, +12.9% is the one big exception), and that 2022Q1 (nights acceleration exactly 0.0) is classed as decelerating and was +4.3%.

**Multivariate (ex-ante spec: nights acceleration + guide-implied acceleration + margin vs bound, n = 19):**

| Target | R2 in-sample | LOO R2 | LOO RMSE | mean-only RMSE | coefficients (p; LOO sign stability) |
|---|---|---|---|---|---|
| 1-day | 0.15 | -0.10 | 9.7 | 9.3 | nights -0.05 (0.50; 0.95), guide +0.30 (0.39; 1.00), margin +0.42 (0.50; 1.00) |
| 5-day | 0.16 | -2.33 | 18.4 | 10.1 | nights -0.09 (0.25; 1.00), guide +0.24 (0.54; 1.00), margin -0.30 (0.66; 0.89) |
| 20-day | 0.05 | -8.04 | 23.4 | 7.8 | nights -0.04 (0.48; 0.89), guide 0.00 (0.99; 0.56), margin -0.33 (0.55; 0.89) |

---

## 5. Pre-print signals

Full sample. Target is the next print's outcome. LOO RMSE is for a univariate OLS refit leaving each print out, versus the leave-one-out mean.

| Pre-print signal | n | vs 1-day excess: r (p) | perm p | LOO RMSE vs mean | vs 5-day excess: r (p) |
|---|---|---|---|---|---|
| Prior quarter S&M deleverage (pts) | 17 | **+0.59 (0.014)** | 0.014 | **7.9 vs 9.1** | +0.48 (0.051) |
| Trailing-4 S&M deleverage | 17 | +0.34 (0.18) | 0.18 | 9.2 vs 9.1 | +0.38 (0.13) |
| Prior quarter nights acceleration | 20 | +0.24 (0.30) | 0.31 | 10.0 vs 9.1 | +0.31 (0.19) |
| FY floor action at prior print | 22 | +0.19 (0.39) | 0.38 | 8.9 vs 8.6 | +0.28 (0.21) |
| Prior print's beat vs midpoint | 18 | -0.13 (0.60) | 0.60 | 9.7 vs 8.9 | **-0.48 (0.044)**, LOO 9.0 vs 10.0 |
| 20-session run-up into print (raw) | 22 | +0.13 (0.58) | 0.58 | 8.9 vs 8.6 | +0.16 (0.49) |
| Quarter CPI lodging y/y | 14 | +0.12 (0.70) | 0.70 | 10.2 vs 9.0 | -0.02 (0.94) |
| This quarter's guide midpoint y/y | 19 | +0.11 (0.65) | 0.66 | 8.9 vs 8.7 | -0.27 (0.26) |
| This quarter's guide width (% of mid) | 19 | +0.09 (0.73) | 0.73 | 9.1 vs 8.7 | -0.25 (0.29) |
| Prior reaction streak (signed) | 22 | +0.08 (0.73) | 0.73 | 9.2 vs 8.6 | -0.14 (0.53) |
| Prior print's 1-day excess | 22 | -0.06 (0.78) | 0.78 | 9.0 vs 8.6 | -0.24 (0.28) |
| Prior quarter margin vs bound | 19 | -0.01 (0.98) | 0.98 | 10.0 vs 9.3 | -0.11 (0.64) |

Robustness of the one hit: r = 0.59 ex-2022Q3 (the -37 pt leverage point), 0.55 ex-2026Q2, 0.66 from 2023Q1 (n = 14, p = 0.010, Spearman 0.74). Fitted line: 1-day excess = -2.1 + 0.35 x prior S&M deleverage. There is no post-print momentum or reversal to trade: prior 1-day excess vs next 1-day excess r = -0.06, and the streak is r = +0.08.

**Pre-print signals vs the next margin surprise.** On the full sample the guide's y/y and the guide width correlate 0.8 to 0.9 with the y/y margin change, but that is the 2022 recovery (guides of +60% y/y alongside +12 pt margin expansion). From 2023Q1, in the margin script's sample, the guide y/y is r = +0.46 (p = 0.10) and beats the naive forecasts only marginally (LOO 2.82 vs 2.79 for the guide bound). The pre-print revenue variables do not predict the margin surprise; the lagged S&M line does (section 6).

**Pre-print signals vs the next revenue beat.** The guide width is r = +0.55 (p = 0.015, n = 19; wider range, bigger beat) but LOO R-squared is only 0.09 and the range has narrowed to 1.5 to 1.7% since 2025, so it says little for 3Q26. The beat has been positive 19 of 19 times (base rate, not signal).

---

## 6. Margin predictability (1Q23 to 2Q26, 14 quarters)

**The surprise series.** Bound = the numeric bound guided for that quarter at the prior print (Theo's `guidance_items.csv`, NEXTQ rows). Economic sign throughout (positive = margin came in above the bound); the brief's alternative sign for ceiling guides ("ceiling minus actual, positive = held") is in the CSV as `surprise_specsign_pts` and is positive 13 of 14 times, mean +2.0 pts.

| Quarter | Margin | Guide type / bound | vs bound (pts) | vs prior year (pts) | Prior-quarter S&M deleverage (pts) | Contemporaneous S&M deleverage (pts) | Contemporaneous model LOO forecast |
|---|---|---|---|---|---|---|---|
| 1Q23 | 14.4 | ceiling 15.0 | -0.6 | -0.8 | -9.5 | +9.9 | 13.4 |
| 2Q23 | 33.0 | ceiling 34.0 | -1.0 | -0.8 | +9.9 | +10.6 | 32.6 |
| 3Q23 | 54.0 | floor 51.0 | +3.0 | +3.5 | +10.6 | -14.0 | 57.5 |
| 4Q23 | 33.3 | floor 27.0 | +6.3 | +6.7 | -14.0 | -12.3 | 30.5 |
| 1Q24 | 19.8 | floor 14.0 | +5.8 | +5.4 | -12.3 | -4.3 | 17.3 |
| 2Q24 | 32.5 | ceiling 33.0 | -0.5 | -0.4 | -4.3 | +6.5 | 33.7 |
| 3Q24 | 52.5 | ceiling 54.0 | -1.5 | -1.5 | +6.5 | +17.4 | 51.5 |
| 4Q24 | 30.9 | ceiling 33.0 | -2.2 | -2.4 | +17.4 | +17.3 | 30.9 |
| 1Q25 | 18.4 | ceiling 20.0 | -1.7 | -1.4 | +17.3 | +2.3 | 20.9 |
| 2Q25 | 33.7 | ceiling 32.5 | +1.2 | +1.2 | +2.3 | +8.6 | 33.0 |
| 3Q25 | 50.1 | ceiling 52.5 | -2.4 | -2.4 | +8.6 | +14.5 | 53.1 |
| 4Q25 | 28.3 | ceiling 30.8 | -2.5 | -2.6 | +14.5 | +14.3 | 30.2 |
| 1Q26 | 19.4 | point 18.4 | +1.0 | +1.0 | +14.3 | +16.2 | 16.9 |
| 2Q26 | 35.0 | floor 33.7 | +1.3 | +1.3 | +16.2 | +9.9 | 34.1 |

Mean surprise vs bound +0.4 pts, median -0.5, 6 of 14 above the bound. Floors have been beaten by +1.3 to +6.3 pts (4 of 4); ceilings undershot by -0.5 to -2.5 (8 of 9, the exception 2Q25); the one point guide (1Q26) beaten by +1.0. In other words, the quarterly margin guide is precise to about 1 to 2.5 pts when it is a ceiling and loose by 3 to 6 pts when it is a floor; the FY floor behaves like the quarterly floors (beaten by 60 to 180 bps every year, margin-drivers note section 7).

**Predictors of the surprise vs bound** (same statistics; "naive last" = last quarter's surprise as the forecast, RMSE 3.03; "guide exact" RMSE 2.79; LOO mean RMSE 2.97). The y/y surprise gives the same ranking because the two targets are nearly identical (ceiling = prior-year margin).

| Predictor | Known before print? | n | Pearson r (p) | Spearman | perm p | LOO RMSE | beats guide exact (2.79)? | beats naive last (3.03)? |
|---|---|---|---|---|---|---|---|---|
| S&M deleverage, same quarter | no (in the print) | 14 | -0.79 (0.001) | -0.67 | 0.002 | 2.06 | yes | yes |
| **S&M deleverage, prior quarter** | **yes** | 14 | **-0.62 (0.017)** | -0.52 | 0.017 | **2.61** | **yes (by 7%)** | yes |
| S&M cash growth, same quarter | no | 14 | -0.59 (0.027) | -0.41 | 0.026 | 2.69 | yes | yes |
| Take-rate change, same quarter | no | 14 | +0.56 (0.036) | +0.71 | 0.036 | 2.82 | no | yes |
| S&M cash growth, prior quarter | yes | 14 | -0.55 (0.044) | -0.33 | 0.042 | 2.79 | no (2.79 vs 2.79) | yes |
| Revenue guide y/y for the quarter | yes | 14 | +0.46 (0.10) | +0.68 | 0.10 | 2.82 | no | yes |
| Revenue beat vs midpoint, same quarter | no | 14 | +0.45 (0.11) | +0.24 | 0.11 | 2.96 | no | yes |
| Ops-and-support per night y/y, same quarter | no | 14 | -0.41 (0.14) | -0.33 | 0.14 | 2.91 | no | yes |
| S&M deleverage, trailing 2 quarters | yes | 14 | -0.39 (0.17) | -0.31 | 0.17 | 3.03 | no | no |
| SBC % revenue change, prior quarter | yes | 14 | -0.31 (0.29) | -0.20 | 0.29 | 2.93 | no | yes |
| Take-rate change, prior quarter | yes | 14 | +0.27 (0.36) | +0.32 | 0.35 | 2.99 | no | yes |
| ADR ex-FX y/y, prior quarter | yes | 14 | -0.18 (0.54) | -0.19 | 0.55 | 3.03 | no | no |
| Ops-and-support per night y/y, prior quarter | yes | 14 | +0.16 (0.57) | +0.34 | 0.58 | 3.14 | no | no |
| CPI lodging y/y, quarter average | yes | 14 | +0.13 (0.67) | +0.38 | 0.67 | 3.10 | no | no |
| FX impact on revenue growth (letter, by year) | yes | 14 | +0.04 (0.90) | +0.14 | 0.90 | 3.06 | no | no |
| Prior print's beat, guide width, reaction streak | yes | 14 | |r| < 0.20 | | > 0.5 | 3.03 to 3.14 | no | no |

The contemporaneous S&M coefficient is -0.24 pts of margin per point of deleverage, which is S&M's share of revenue: this row is an accounting identity, not a finding. The lagged row is the finding, and it works because S&M growth is persistent (the 2024Q3 to 2026Q1 run of +14 to +17 pt deleverage was announced in advance as the new-business launch budget). Take rate is the only other line with a same-quarter relationship (r = +0.56), and it was the stated reason for the 4Q25 miss (-50 bps on FX and RNPL timing); its lagged version is r = +0.27 and does not beat the guide.

**Margin model.** margin(t) = margin(t-4) + b0 + b1 x ADR ex-FX y/y + b2 x S&M deleverage, leave-one-out. ADR ex-FX = letter value where given (4Q25 +3, 1Q26 +4, 2Q26 +4), else ADR y/y minus the letter's annual FX impact on revenue growth (2022 -6, 2023 +1, 2024 0, 2025 0), which is coarse.

| Fit | n | R2 | LOO R2 | LOO RMSE of margin forecast (pts) | RMSE using guide bound | RMSE using prior-year margin | coefficients |
|---|---|---|---|---|---|---|---|
| Contemporaneous, from 1Q23 | 14 | 0.73 | 0.49 | **2.00** | 2.79 | 2.85 | b0 +1.3, ADR +0.41 (p 0.15), S&M -0.24 (p < 0.01) |
| S&M deleverage only, from 1Q23 | 14 | 0.67 | 0.51 | 1.96 | 2.79 | 2.85 | b0 +2.1, S&M -0.23 (p < 0.01) |
| ADR ex-FX only, from 1Q23 | 14 | 0.02 | -0.25 | 3.13 | 2.79 | 2.85 | ADR +0.22 (p 0.66) |
| Contemporaneous, from 1Q22 | 18 | 0.78 | 0.53 | 4.51 | 4.85 | 7.16 | ADR +0.77 (p 0.01), S&M -0.30 (p < 0.01) |
| **Lagged inputs (pre-print), from 1Q23** | 14 | 0.43 | 0.02 | **2.78** | 2.79 | 2.85 | ADR(t-1) -0.40 (p 0.28), S&M(t-1) -0.16 (p 0.02) |

So: with the print in hand, ADR adds nothing once S&M is known (the ADR-only model is worse than the guide), and the whole 2.0 vs 2.8 improvement is the S&M line. Before the print, the two-factor model ties the guide (2.78 vs 2.79) and the single lagged S&M line beats it by 0.2 pts. Coefficient signs are stable in every LOO fold.

**3Q26 nowcast from what is known today** (2Q26 S&M deleverage +9.9 pts, 2Q26 ADR ex-FX +4%, 3Q26 ceiling guide 50.1%, 3Q25 margin 50.1%): lagged univariate 49.8% (surprise vs ceiling -0.3 pts); lagged two-factor 49.1% (-1.0 pt y/y). Both say "down slightly", which is what management guided. There is no margin edge for 5 November from the cost lines; the honest forecast is 49 to 50% with a 2.6 pt standard error, and the ceiling has held 8 of 9 times.

---

## 7. What this implies for the 5 November prediction card

**Contemporaneous variables to score in the print, in order:**

1. **Nights growth acceleration vs 2Q26's +10.3%.** The single directional variable: 17 of 21 prints moved with its sign. 3Q26 nights above +10.3% y/y (i.e. above about 147.4M on 3Q25's 133.6M) is the accelerating case. Since 2Q26 was itself an acceleration (+1.2 pts) and management flagged "growth and policy initiatives" spend, the base case from the base rate alone is roughly a 55 to 60% chance of acceleration given the run of three small accelerations in the last four quarters; the reaction data do not sharpen that.
2. **Revenue beat vs the $4,730M midpoint together with the 4Q26 guide's implied acceleration.** The only reliably negative cell is a below-median beat (under about +2.5%, i.e. below roughly $4,850M) combined with a 4Q guide whose y/y sits more than 3.9 pts below the reported 3Q y/y: 5 of 5 negative, mean -7.9%. A beat above +2.5% with a decelerating 4Q guide has been positive 4 of 5 times. The cushion-adjusted guide has no 1-day content (r = -0.03), so do not read the 4Q guide through the cushion on the day; it shows up, if at all, over 20 days (r = +0.40, p = 0.10).
3. **Margin vs the 50.1% ceiling, read jointly with nights.** Margin holding the guide is the norm (13 of 14) and carries no information alone; margin met with nights accelerating is +5.0% on average (6 of 7 positive), met with nights decelerating -2.1% (2 of 11 positive). A margin above 50.1% would be only the third upside "miss" since 2022 and both prior ones were sold (-10.0%, -8.4%) because nights disappointed at the same time.
4. **FY floor action.** Raised at 3 of the last 4 prints. The raise itself is weakly positive (r = +0.45 from 2022Q1, p = 0.06) but a fourth raise to 36% is now partly expected; a hold at 35.5% would be the first non-raise since 4Q25 and is the asymmetric risk.
5. **S&M deleverage in the print.** Each point of S&M growth above revenue growth costs 0.24 pts of margin; 2Q26 was +9.9 after +16.2. If S&M deleverage in 3Q26 is above +10, expect margin at or below 49%; if it falls toward +5, expect 50 to 51%. This is arithmetic, not prediction, but it is the fastest way to check the margin number against the cost lines on the night.

**Pre-print signals, and what they say now:**

- **Prior-quarter S&M deleverage +9.9 pts** (2Q26): the one signal with LOO value (LOO R-squared 0.24 on n = 17). Fitted 1-day excess +1.3% versus the sample mean of -1.4%; it sits just above the median split (above-median readings: 4 of 8 positive, mean +3.5%; below: 1 of 9 positive, mean -5.9%). Mild positive tilt; one hit in 60 tests; treat as a hypothesis whose falsification on 5 November is itself informative.
- **Prior beat +1.1%** (2Q26 vs the $3,570M midpoint, small): the 5-day relationship (r = -0.48) says small prior beats precede better weeks; mild positive tilt, weak.
- **Prior reaction +16.3%, streak +1, 20-day run-up +3.2%:** no predictive content (r between -0.06 and +0.13). Do not build a mean-reversion or momentum view into the card.
- **FY floor raised last print:** r = +0.19 for the next 1-day reaction; no LOO value.
- **Guide width 1.7%, guide y/y +15.5%, CPI lodging +2.8% (July):** no LOO value for the reaction or the margin surprise.
- **Margin:** lagged S&M deleverage implies 49.8% versus the 50.1% ceiling, a -0.3 pt surprise with a 2.6 pt standard error; the guide is as good a forecast as anything we can build before the print.

**Net for the card:** the reaction on 5 November is not forecastable from anything known today beyond a mild positive tilt from the S&M signal that would not survive multiple-comparisons correction. What is forecastable is the *conditional* reaction: nights acceleration is the sign, the revenue beat sets the size on day 1, and the double-miss cell (small beat plus weak 4Q guide) is the only combination with a consistent history (-8%). Margin will land within about 2.5 pts of 50% and will not be the driver unless it misses to the downside, which has not happened since guidance began.

---

## 8. Caveats

- **Multiple comparisons.** 189 contemporaneous and 180 pre-print tests in the reaction file, 66 in the margin file. The smallest contemporaneous p is 0.06 (FY floor action, from 2022Q1), the smallest pre-print p is 0.014 and the smallest lagged margin p is 0.017. None passes Bonferroni. The nights direction result (binomial p = 0.007 on 21 prints) is the strongest single statistic and it survives a correction for the five one-way tests, but it is a sign test, not a magnitude.
- **Sample.** 22 prints, 18 with cost lines, 14 with a numeric quarterly margin guide. Leave-one-out on 14 points can be moved by a single quarter; the 2Q26 print (+16.3%) and the 2022Q3 S&M reading (-37 pts) were checked and neither drives the reported results.
- **2021 base effects.** Acceleration features in 2021 are +183 / -168 pts. Pearson correlations on the full sample for nights, GBV and revenue acceleration are not interpretable; use the `from_2022Q1` sample or the Spearman column.
- **Sign convention for ceiling guides.** The brief asked for "ceiling minus actual, positive = beat". A margin above a "down slightly" ceiling is economically good, so the primary series uses actual minus bound throughout; the brief's version is `surprise_specsign_pts` and shows the guide held 13 of 14 times.
- **FY floor action coding** is rule-based on Theo's bound values (floor at a prior point value counts as raised; a 0.25 pt tolerance). 2022Q3 has no FY item and is coded "none" although the call said "FY expansion".
- **FX** is the letter's annual revenue-growth impact applied to every quarter of the year, except where the letter gave ADR ex-FX. Quarterly FX varied (1Q22 about -3, 4Q22 about -7).
- **2020 KPIs** are hand-entered from the letters; they reproduce the letter-stated 2021 y/y growth for nights and GBV to the nearest point.
- Theo's series are ABNB minus QQQ (this file) versus ABNB minus SPY next close in his brief, so his r values are not directly comparable to ours.
