# 05. The macro environment to end-2027 and how it reaches ABNB's print, guide and stock

**Date:** 2026-09-06 (overnight run). **Author:** Krishang Surapaneni (compiled with Claude Code, workstream 05).
**Question:** Which macro variables actually move Airbnb's nights, ADR, revenue and margin; what does the macro path look like from here to end-2027; and what does that imply for the 5 Nov 2026 guide, the Feb 2027 guide and the stock?
**Script:** `analysis/src/overnight/05_macro_transmission.py` (`py -3.13`; re-pulls 28 FRED series, rebuilds every CSV below).
**Data written (`data/processed/overnight/`):** `05_macro_sensitivities.csv`, `05_macro_tests_all.csv`, `05_macro_quarterly_panel.csv`, `05_fx_fits.csv`, `05_fx_schedule.csv`, `05_macro_scenarios.csv`, `05_shock_episodes.csv`, `05_regional_growth.csv`, `05_crossborder_share.csv`, `05_reaction_by_accel.csv`, cache `05_fred_cache/`.
**Figures (`analysis/figures/overnight/`):** `05_fx_mechanism.png`, `05_macro_vs_nights.png`, `05_sensitivity_bars.png`.

---

## Bottom line

1. **Exactly one macro variable transmits to Airbnb with high confidence, and it is FX.** Of 1,408 macro x lag x target x window pairs tested, three survive every check and all three are the same mechanism. EUR/USD y/y (quarterly average) explains the FX contribution to ADR growth with r = +0.97 on n = 14 (perm p 0.001; r = +0.99 on n = 17 from 1Q22): **ADR FX (pp) = -0.61 + 0.460 x EUR/USD y/y**. The trade-weighted dollar is the mirror image, r = -0.95: **ADR FX (pp) = 0.52 - 0.715 x broad USD y/y** (the "0.5 - 0.72 x USD" rule from the predictive study, re-estimated and confirmed).

2. **Revenue FX is the same mechanism but it arrives about two quarters late, and that is the most useful thing in this note.** Reported-minus-constant-currency revenue growth does not track spot FX; it tracks EUR/USD y/y lagged one to two quarters, because revenue is recognised at check-in on bookings made one to two quarters earlier (Reserve Now Pay Later, now over 20% of GBV, has lengthened that further) and because management hedges. The proof is out-of-sample: the 2Q26 letter guides Q3 revenue "inclusive of an approximate three percentage point FX tailwind after factoring in our hedging program", and the contemporaneous fit predicts **-1.6 pp** for 3Q26 while the two-quarter-lagged fit predicts **+2.9 pp**. The lagged spec is right; the contemporaneous one, which has the higher in-sample r, is wrong for forecasting.

3. **Which means the Q4 2026 FX tailwind is already gone, and it is already knowable today.** EUR/USD y/y was +11.1% in 1Q26, +2.6% in 2Q26 and **-1.6% quarter-to-date in 3Q26** (to 28 Aug). Feed those through: revenue FX goes from **about +3 pp in 3Q26 to about -0.4 pp in 4Q26 and -1.0 pp in 1Q27**, and **84% of the 4Q26 input is FX that has already happened**, not a forecast. **A Q4 revenue guide roughly 3 pp below the Q3 guided rate is arithmetic, not a demand signal.** ADR's reported FX contribution falls from +5.0 pp (1Q26) and +1.3 pp (2Q26) to roughly flat in 3Q26 (range -1.3 to +0.8) and about -0.7 pp in 4Q26.

4. **Nothing forecasts nights. Not one macro series.** After two artefact guards — does the relationship hold from 1Q24, and does it survive first-differencing — **zero** macro variables reach high confidence against nights y/y and one reaches medium (CPI lodging away from home, r +0.81, and it is coincident, not leading). Every classic hit collapses: BEA accommodations spend (r +0.88 on levels, +0.28 from 2024), air revenue passenger miles (+0.83 / +0.04), leisure-and-hospitality employment (+0.81 / +0.19), 2-year Treasury (+0.81 / +0.08), all-items CPI (+0.84 / +0.32), Eurostat EU27 platform nights (+0.62 / +0.07). These are the 2023 normalisation trend. Since 1Q24 nights have sat in a 7.4% to 12.3% band while sentiment fell 20 points, unemployment rose, claims swung 20 points and the dollar moved 12 points, with no relationship to any of it. Michigan sentiment against nights y/y is **r -0.05**.

5. **The shock evidence says the same thing more usefully than the regressions do.** Spring 2025: Michigan sentiment collapsed 16.5 points y/y to 52.2, Canadian trips to the US fell about a quarter, BEA inbound foreign travel fell 5.0% y/y — and global nights growth went from 7.9% to 7.4%. Half a point. 1H 2026: the largest airfare shock since 2022 (CPI airline fares **+25.5% y/y** in July 2026, Gulf jet fuel +65% y/y, TSA throughput **-3.7% y/y** in late August) coincided with **the fastest nights growth in two years (+10.3%) and +4% ex-FX ADR**. Expensive flights push demand into domestic and drive-to stays, where Airbnb is over-indexed. Macro shocks that gut an airline move Airbnb's nights by fractions of a point.

6. **ADR ex-FX is the one place a non-mechanical macro relationship is worth watching, at hypothesis strength — and it points down for 2027.** Initial jobless claims y/y (r -0.78), airline-fare CPI (+0.70) and Gulf jet fuel (+0.70) agree, and all three currently nowcast 3Q26 ex-FX ADR at **+3.6% to +4.1%**, i.e. the +4% run-rate holds. But the EIA has Brent falling from $86.81 average in 2026 to **$69.39 in 2027** and wholesale jet fuel from $3.24 to $2.50/gal. Lapping a +25% airfare spike is worth roughly **-1.3 to -1.7 pp of ex-FX ADR in 2027** on those coefficients. Cheaper flights are a volume positive and a price negative, and the price side lands first.

7. **Macro reaches the stock through the guide, not through the data.** No macro series forecasts the 1-day reaction. What sets it is the sign of nights acceleration: post-2022, accelerating quarters average **+6.7% day-1 (n 5)**, decelerating quarters **-5.4% (n 9)**. The 2Q26 print was +17.4%, the largest ever. **The risk into 5 Nov is not that macro deteriorates. It is that a mechanically FX-depressed Q4 revenue guide gets read as a demand deceleration.** The historical record says the market keys on nights, not on the revenue guide (4Q24: revenue guide below the Street, stock +14.4% on the nights beat), so this should be survivable — but it is the specific thing to be positioned for.

8. **Probability-weighted, the macro path gives FY27 nights +8.5%, revenue +10.3% and an Adjusted EBITDA margin of 36.4%** — about 2 points below the driver model's base-case FY27 revenue growth, entirely because of the FX schedule rather than any demand assumption.

---

## Section 1. The sensitivity table

`data/processed/overnight/05_macro_sensitivities.csv` carries one row per macro variable x target (256 rows) with the effect size, lag, window, n, r, Spearman, permutation p, leave-one-out RMSE against two benchmarks, the two artefact-guard statistics, and a confidence label with its reason.

**Method.** Quarterly panel 2019Q1-2026Q3 (3Q26 partial, flagged). Each FRED series is averaged by calendar quarter and expressed as y/y % (indices and levels) or as the 4-quarter change in percentage points (rates: Fed funds, unemployment, saving rate, sentiment, yields). Targets come from `abnb_driver_history_quarterly.csv`, from the letters via `predictive/03_quarterly_panel.csv` (ADR ex-FX and the ADR FX effect) and from Theo's `quarterly_actuals.csv` (reported minus constant-currency revenue growth = revenue FX points). Each pair is fitted by OLS at lag 0 and lag 1 on two windows (from 1Q23 and from 1Q22), with a 1,000-shuffle permutation p and a leave-one-out linear nowcast scored against naive-last-quarter and the LOO mean. **1,408 pairs were tested**; at 5% we would expect about 70 false positives, and the series are far from independent, so nothing here rests on a p-value alone.

**The two artefact guards** (this is the correction to the earlier work). A pair is demoted to "none" if |r| >= 0.6 on the post-2022 window but either (a) |r| from 1Q24 onward is below 0.40 or flips sign, or (b) the relationship between the **quarter-on-quarter changes** in the two series has |r| below 0.35 or flips sign. Guard (a) catches the 2023-normalisation trend that `research/notes/predictive/03_macro-altdata-nowcast.md` finding 2 identified. Guard (b) catches it independently: two series that merely share a downward trend produce a high level correlation and a near-zero difference correlation. The mechanical FX pairs pass both. Before the guards, 21 pairs carried medium confidence and all-items CPI "nowcast" nights at r +0.84; after, 16 do and CPI does not.

**Result counts: 3 high, 16 medium, 55 low, 182 none.**

### Deliverable: effect on each target per +1 unit of the macro variable

Effect is the OLS slope on the 1Q23-2Q26 window at the stated lag (L0 = same quarter, L1 = one-quarter lead); the unit is "percentage points of the target per one unit of the macro variable" (one % of y/y for indices, one pp of 4-quarter change for rates). Confidence in brackets.

| Macro variable | nights y/y | ADR ex-FX y/y | FX effect on ADR (pp) | revenue y/y | FX effect on revenue (pp) | EBITDA margin chg (pp) |
|---|---|---|---|---|---|---|
| **Broad trade-weighted USD, y/y %** | +0.22 L1 (none, r +0.32) | -0.10 L1 (none) | **-0.593 L0 (HIGH, r -0.95)** | -0.47 L0 (none) | **-0.535 L0 (medium, r -0.80)** | -0.28 L1 (none) |
| **EUR/USD, y/y %** | -0.20 L1 (none) | +0.05 L1 (none) | **+0.460 L0 (HIGH, r +0.97)** | +0.17 L0 (none) | **+0.313 L1 (HIGH, r +0.82)** | +0.17 L1 (none) |
| GBP/USD, y/y % | -0.29 L1 (low) | -0.08 L0 (none) | +0.403 L0 (medium, r +0.78) | -0.29 L1 (none) | +0.39 L0 (none) | +0.27 L0 (none) |
| USD/CAD, y/y % | +0.39 L1 (none) | -0.19 L1 (low) | -0.619 L0 (medium, r -0.83) | -0.18 L0 (none) | -0.54 L0 (none) | -0.31 L0 (none) |
| USD/MXN, y/y % | -0.10 L0 (none) | -0.03 L0 (none) | -0.08 L0 (low) | -0.28 L0 (none) | -0.10 L0 (low) | -0.14 L1 (low) |
| USD/BRL, y/y % | -0.11 L1 (none) | -0.06 L1 (low) | -0.14 L0 (low) | -0.29 L0 (medium, r -0.68) | -0.16 L0 (none) | -0.14 L0 (low) |
| USD/JPY, y/y % | +0.22 L1 (low) | +0.08 L0 (none) | -0.195 L1 (medium, r -0.69) | +0.32 L0 (none) | -0.15 L1 (low) | +0.11 L0 (none) |
| **Michigan sentiment, 4q chg (pts)** | **-0.01 L1 (none, r -0.05)** | -0.05 L1 (low) | -0.09 L1 (none) | -0.07 L1 (none) | +0.02 L0 (none) | +0.13 L0 (low) |
| PCE services nominal, y/y % | +2.04 L0 (none, artefact) | -0.25 L1 (none) | -0.98 L1 (low) | +2.00 L0 (low) | -0.93 L0 (none) | +0.20 L1 (none) |
| Real disposable income, y/y % | -0.15 L1 (none) | **-0.349 L1 (medium, r -0.65)** | +0.12 L1 (none) | +0.94 L0 (none) | +0.36 L1 (none) | +0.77 L1 (low) |
| CPI all items, y/y % | +2.91 L0 (none, artefact) | +0.31 L0 (none) | -0.77 L1 (low) | +3.33 L0 (none, artefact) | -0.86 L1 (low) | +0.25 L0 (none) |
| CPI lodging away from home, y/y % | **+0.789 L0 (medium, r +0.81)** | -0.19 L1 (low) | -0.25 L0 (none) | +0.90 L0 (none) | -0.12 L1 (none) | +0.42 L1 (none) |
| **CPI airline fares, y/y %** | +0.08 L0 (none, r +0.33) | **+0.067 L0 (medium, r +0.70)** | -0.09 L1 (low) | +0.09 L1 (none) | -0.10 L1 (none) | -0.09 L1 (low) |
| Unemployment rate, 4q chg (pp) | -9.70 L0 (none, artefact) | -0.77 L0 (none) | +1.67 L1 (none) | -13.34 L0 (medium, r -0.69) | +2.76 L1 (none) | -1.09 L1 (none) |
| **Initial jobless claims, y/y %** | -0.22 L1 (low) | **-0.172 L0 (medium, r -0.78)** | +0.15 L1 (low) | -0.22 L1 (none) | +0.17 L1 (low) | +0.19 L1 (none) |
| Fed funds, 4q chg (pp) | +1.12 L0 (none, artefact) | -0.19 L1 (none) | -0.37 L0 (none) | +1.50 L0 (none, artefact) | -0.29 L0 (none) | +0.61 L1 (low) |
| 10y Treasury, 4q chg (pp) | +3.64 L0 (none, artefact) | -0.35 L0 (none) | -1.27 L1 (none) | +3.06 L1 (low) | -1.54 L1 (low) | +1.32 L0 (none) |
| Personal saving rate, 4q chg (pp) | -0.12 L1 (none) | -0.39 L1 (low) | +0.29 L1 (none) | +1.43 L0 (low) | +0.63 L1 (none) | +1.04 L1 (none) |
| Air revenue passenger miles, y/y % | +0.39 L0 (none, artefact) | -0.04 L1 (none) | -0.14 L1 (none) | +0.45 L0 (none, artefact) | -0.12 L0 (none) | +0.13 L1 (none) |
| BEA PCE accommodations nominal, y/y % | +0.43 L0 (none, artefact) | +0.03 L0 (none) | -0.13 L1 (none) | +0.578 L0 (medium, r +0.80) | -0.11 L1 (none) | +0.13 L0 (none) |
| BEA foreign travel in the US (inbound), y/y % | +0.12 L0 (none, artefact) | -0.00 L1 (none) | -0.04 L1 (low) | +0.13 L0 (none) | -0.04 L1 (low) | +0.03 L0 (none) |
| BEA US travel abroad (outbound), y/y % | +0.11 L0 (none, artefact) | -0.00 L1 (none) | -0.06 L0 (low) | +0.08 L1 (low) | -0.065 L0 (medium, r -0.63) | -0.00 L1 (none) |
| Eurostat EU27 platform nights, y/y % | +0.19 L1 (none, artefact) | +0.00 L0 (none) | -0.14 L1 (none) | +0.369 L0 (medium, r +0.68) | -0.10 L0 (none) | -0.02 L1 (none) |
| **Gulf Coast jet fuel, y/y %** | +0.00 L0 (none, r +0.02) | **+0.027 L0 (medium, r +0.70)** | -0.03 L1 (none) | +0.07 L1 (none) | -0.04 L1 (none) | -0.03 L1 (none) |
| WTI crude, y/y % | -0.03 L0 (none) | +0.030 L0 (low) | -0.11 L1 (low) | -0.05 L1 (none) | -0.08 L1 (none) | +0.04 L0 (none) |

**How to read it.** The only cells to put in a model are the two FX columns. The `adr_exfx_yoy` medium cells (claims, airfares, jet fuel, real DPI) are a watch list: they agree with each other, they have a story, and they all currently say ex-FX ADR holds near +4% — but the target is integer-rounded in the letters and n is 14. The nights column is empty on purpose. The `rev_yoy` medium cells (unemployment, BEA accommodations, Eurostat platform nights, consumer credit, USD/BRL) are coincident readings of the same quarter, not leads, and BEA month-3 lands about a week before the print on a revised vintage.

**Why the margin column is empty.** No macro variable relates to the y/y change in Adjusted EBITDA margin above low confidence (best |r| 0.60, the saving rate, which fails both guards). Margin moves through revenue. Using the margin-bridge sensitivities from `research/notes/2026-09-05_margin-drivers.md` — **+0.35 margin points per +1 pt of nights growth, +0.46 per +1 pt of ADR ex-FX, +0.47 per +1 pt of FX, +0.64 per +1 pt of take-rate-driven revenue** — the chain-implied margin effect of each macro variable is in `margin_effect_via_chain_pp` in the CSV. For the dollar: **+1% on the broad dollar costs 0.59 pp of ADR FX and 0.54 pp of revenue FX, worth about -0.28 pp of EBITDA margin through the chain**, before any cost response.

---

## Section 2. The FX mechanism, and the schedule by quarter 3Q26-4Q27

Fits are in `05_fx_fits.csv`; the quarterly schedule under three EUR/USD paths is `05_fx_schedule.csv`; the chart is `05_fx_mechanism.png`.

**ADR (and GBV) FX follows spot in the same quarter.**

| Fit (1Q22-2Q26, n 17) | slope | intercept | r | LOO RMSE | naive-last RMSE |
|---|---|---|---|---|---|
| ADR FX pp on EUR/USD y/y | +0.451 | -0.569 | +0.990 | 0.51 | 2.04 |
| ADR FX pp on broad USD y/y | -0.715 | +0.525 | -0.964 | 0.99 | 2.04 |

**Revenue FX lags spot by one to two quarters.** Eleven specifications were fitted, then scored on the one genuine out-of-sample observation available: management's own Q3 2026 guide of "approximately three percentage points" of FX tailwind after hedging.

| Spec (1Q22-2Q26, n 17) | r | LOO RMSE | predicted 3Q26 revenue FX | error vs the +3.0 pp guide |
|---|---|---|---|---|
| EUR/USD y/y, lag 2 | +0.63 | 3.04 | **+2.92 pp** | 0.08 |
| Broad USD y/y, average of lags 1-2 | -0.61 | 3.06 | +2.50 pp | 0.50 |
| **EUR/USD y/y, average of lags 1-2 (spec used)** | **+0.80** | **2.30** | **+2.19 pp** | **0.81** |
| EUR/USD y/y, average of lags 0-1-2 | +0.91 | 1.61 | +1.29 pp | 1.71 |
| Broad USD y/y, average of lags 0-1 | -0.89 | 1.72 | +1.25 pp | 1.75 |
| EUR/USD y/y, lag 0 (highest in-sample r among level specs) | +0.91 | 1.62 | **-1.61 pp** | 4.61 |
| EUR/USD y/y, average of lags 0-1 (lowest in-sample LOO) | +0.95 | 1.22 | -0.59 pp | 3.59 |

The specs that fit history best get the future wrong. The forecasting spec is **revenue FX (pp) = -0.64 + 0.413 x [average of EUR/USD y/y in the two prior quarters]**, chosen as the lowest-LOO spec within 1 pp of the guide. The residual spread across the credible lagged specs is about **±0.8 pp**, and that is the honest error bar on every revenue-FX number below.

### The schedule

EUR/USD quarterly averages are actuals through 2Q26 and quarter-to-date to 28 Aug 2026 for 3Q26. `driver_realised_share` is the fraction of the revenue-FX driver that is already observed FX rather than a forecast.

| Quarter | EUR/USD (consensus) | EUR/USD y/y | ADR FX (pp) | Revenue FX (pp), consensus | strong USD | weak USD | Driver realised |
|---|---|---|---|---|---|---|---|
| 3Q25 actual | 1.17 | +6.4% | +2.7 | 0.0 | | | 100% |
| 4Q25 actual | 1.16 | +9.1% | +2.9 | +1.0 | | | 100% |
| 1Q26 actual | 1.17 | +11.1% | +5.0 | +3.0 | | | 100% |
| 2Q26 actual | 1.16 | +2.6% | +1.3 | +4.0 | | | 100% |
| **3Q26 qtd** | 1.15 | **-1.6%** | **-1.3 to +0.8** | **+2.2 (guide ~+3)** | +2.2 | +2.2 | 100% |
| **4Q26** | 1.16 | -0.4% | **-0.7** | **-0.4** | -0.4 | -0.4 | **84%** |
| 1Q27 | 1.16 | -0.4% | -0.8 | -1.0 | -1.6 | -0.5 | 34% |
| 2Q27 | 1.17 | +0.6% | -0.3 | -0.8 | -2.5 | +0.5 | 0% |
| 3Q27 | 1.18 | +2.1% | +0.4 | -0.6 | -3.2 | +1.3 | 0% |
| 4Q27 | 1.18 | +1.7% | +0.2 | -0.1 | -3.0 | +2.2 | 0% |
| **FY27 average** | | | **-0.1** | **-0.6** | **-2.6** | **+0.9** | |

**Read the 4Q26 row first. Revenue FX is about -0.4 pp under all three paths, because 84% of its driver is FX that has already happened.** The swing from 3Q26's ~+3 pp to 4Q26's ~-0.4 pp is a **3.4 pp mechanical cut to reported revenue growth with no change in demand**. The paths only separate from 2Q27.

The two ADR-FX fits disagree on 3Q26 (EUR-based -1.3 pp, broad-USD-based +0.8 pp) because the broad basket is holding up better than the euro cross: 3Q26 quarter-to-date y/y, EUR/USD -1.6% but **USD/MXN -7.3% and USD/BRL -5.8%** (both tailwinds) against **USD/JPY +8.9%** (a headwind). Airbnb's revenue mix is **44% North America, 40% EMEA, 8% LatAm, 8% APAC** (2Q26 XBRL, `data/processed/overnight/10_xbrl_revenue_geography.csv`), so the euro cross dominates but does not decide. Call 3Q26 ADR FX **roughly flat, range -1.3 to +0.8 pp**, versus +1.3 in 2Q26 and +5.0 in 1Q26.

---

## Section 3. What the shocks actually did (`05_shock_episodes.csv`)

| Episode | Macro | Guided | Printed | Stock | Lesson |
|---|---|---|---|---|---|
| **2022 rate shock** (2Q22-4Q22) | Fed funds +3.9 pp y/y; broad USD +9.0% y/y (3Q22); Michigan -27.7 pts y/y; CPI 8.6% | 3Q22 call (1 Nov 2022): Q4 nights growth to moderate to ~20% from 25% | 4Q22 nights +20.2%, revenue +24.2%, ADR -0.5% (ex-FX +5, FX -5.5) | 3Q22 print **-13.4%** day-1 (excess -10.0), 20d excess -13.0% | Macro hit ADR through FX and the multiple, not nights. The 25→20 nights guide-down drove the day. |
| **2024 US softness** (2Q24-3Q24) | Michigan +9.2 pts y/y; real DPI +3.0%; BEA accommodations +3.7%; US hotel RevPAR flat | 2Q24 call (6 Aug 2024): Q3 nights to moderate, shorter lead times, slowing US demand | 3Q24 nights +8.5% (from 8.7%), then 4Q24 re-accelerated to +12.3% on product changes | 2Q24 **-13.4%** day-1, 20d excess -16.5%; 3Q24 -8.7% | A 0.2-pt nights deceleration with "lead time" language cost 13%. The macro series barely moved. **The market prices the words.** |
| **Spring-2025 tariff / sentiment shock** (2Q25) | Michigan 52.2 in Apr-May, **-16.5 pts y/y**; claims +4.0% y/y; BEA inbound foreign travel **-5.0% y/y**; Canadian trips to the US -25% for 2025 (StatCan) | 1Q25 call (1 May 2025): Q2 nights to moderate from +7.9%; US "relatively softer"; lead times -7% y/y in April; **inbound to the US is 2-3% of the business** | **2Q25 nights +7.4%**; revenue +12.7% (+2.5% vs midpoint); nights accelerated April→July; lead times normalised by June | Tariff days 3 Apr -7.2% / 9 Apr +14.8% (in line with BKNG, EXPE); 1Q25 print +1.0%; **2Q25 print -8.0% on H2 moderation language, not on the shock** | **A 16.5-point sentiment collapse plus a quarter of Canadian arrivals moved global nights by half a point.** Corridor substitution and the 2-3% inbound share cap the exposure. |
| **1Q26-2Q26 Middle East conflict** | CPI airline fares +24.6% y/y (2Q26 SA average; BLS headline July 2026 +25.5%); Gulf jet fuel +83.0% y/y; WTI +48.1%; Michigan -7.0 pts y/y; IAG cut FY26 capacity to flat; Air France-KLM cut twice | 1Q26 call (7 May 2026): "nights and seats booked grew 9% after accounting for an approximate 100-basis-point headwind from the conflict"; Q2 nights to "decelerate slightly" with a further ~100 bp headwind | **2Q26 nights +10.3% — accelerated**; Europe recovered to high-single digits; revenue +16.5%; ADR +5% (+4% ex-FX); "the impact to our business from the conflict was less than we had anticipated" | 1Q26 +0.7%; **2Q26 +17.4% day-1, +22.1% over 5 sessions** — the largest earnings-day move in the company's history | **The largest airfare shock since 2022 coincided with the fastest nights growth in two years.** Management guided the headwind conservatively and beat it. |

**Composite lesson.** Airbnb's nights have absorbed, in four years, a 500 bp hiking cycle, a 27-point sentiment collapse, a tariff shock, a 25% loss of Canadian inbound and a 25% airfare spike, without once leaving a 7-12% growth band outside 2021-22 base effects. **The macro risk to this stock is not to the KPI.** It is (i) FX arithmetic in the reported line, (ii) the multiple, and (iii) management's choice of words about the next quarter.

### Regional and cross-border detail (`05_regional_growth.csv`, `05_crossborder_share.csv`)

| Quarter | NA | EMEA | LatAm | APAC | Global nights | Eurostat EU27 platform nights | BEA inbound to US | Broad USD y/y |
|---|---|---|---|---|---|---|---|---|
| 4Q24 | mid-single | low-double | low-20s | low-20s | +12.3% | +17.4% | +7.6% | +3.5% |
| 1Q25 | low-single | mid-single | low-20s | mid-teens | +7.9% | +6.3% | -0.4% | +5.8% |
| 2Q25 | low-single | mid-single | high-teens | mid-teens | +7.4% | +17.6% | -5.0% | -0.1% |
| 3Q25 | mid-single | mid-single | low-20s | mid-teens | +8.8% | +9.8% | -8.6% | -2.0% |
| 4Q25 | mid-single | high-single | high-teens | mid-teens | +9.8% | +10.9% | -8.3% | -4.0% |
| 1Q26 | high-single | mid-single (ME cancellations) | high-teens | high-teens | +9.2% | +9.7% | -4.8% | -6.7% |
| 2Q26 | high-single (highest in ~3 years) | high-single | ~20% | high-teens | +10.3% | n/a | -0.4% | -2.5% |

Two things matter. First, **BEA inbound foreign travel spending in the US ran -4.8% to -8.6% y/y for five straight quarters while Airbnb's North America nights accelerated from low-single to high-single digits.** Inbound to the US is 2-3% of the business (management, 1Q25 call) and North America is 44% of revenue; the inbound collapse is real and invisible in the KPI. Second, the **cross-border share of gross nights was last disclosed at 46% in 1Q24** (51% in 1Q19, 33% in 3Q21) and has not been disclosed since, so any corridor or FX-mix analysis after 1Q24 works from a stale mix.

---

## Section 4. The macro outlook, September 2026 to end-2027

Everything below is dated and sourced. Where a number is my judgement rather than a published forecast it says so.

### 4.1 US growth, labour and the consumer

| Item | Latest | 2026 | 2027 | Source, date |
|---|---|---|---|---|
| Real GDP | 1Q26 +2.1%; 2Q26 +1.5% (second estimate) | 2.2% | 2.3% | Fed SEP medians, 17 Jun 2026; BEA, 26 Aug 2026 |
| Real GDP | | 2.1% | 2.2% | Philadelphia Fed Survey of Professional Forecasters, Q3 2026 |
| Real GDP (hotel forecasters' assumption) | | 2.3% | **2.7%** | CoStar/STR + Tourism Economics, 1 Sep 2026 |
| Unemployment | **4.1%** (Aug 2026) | 4.3% | 4.3% | BLS, 4 Sep 2026; Fed SEP and SPF agree |
| Payrolls | **+162k** (Aug 2026), well above a ~56k expectation | | | BLS, 4 Sep 2026 |
| Initial claims | **206k** (w/e 29 Aug 2026); **-10.4% y/y** on our quarterly series | | | DOL via FRED ICSA |
| CPI | +3.4% headline, +2.5% core (Jul 2026) | | | BLS, 12 Aug 2026 |
| PCE inflation | +3.7% headline, +3.3% core (Jul 2026) | 3.6% | 2.3% | BEA, 26 Aug 2026; Fed SEP |
| Core PCE (Q4/Q4) | | 3.3% | 2.4% | SPF Q3 2026 |
| Michigan sentiment | **55.2** (Jul 2026) | | | University of Michigan |
| Conference Board confidence | **89.4**; expectations **68.2** (-5.8 m/m) | | | The Conference Board, Aug 2026 |
| Personal saving rate | 3.0% (Jul 2026) | | | BEA |
| Credit-card delinquency | 2.85% (2Q26), down from 3.04% | | | FRED DRCCLACBS |

The consumer picture is two-sided and should be presented that way: **surveys are at recession-adjacent levels** (Michigan 55.2, Conference Board expectations 68.2, below the Board's own 80 recession threshold) while **the hard data are fine** (unemployment 4.1%, claims falling y/y, delinquencies improving). Our sensitivity work says **the surveys have never mattered for Airbnb's nights** (Michigan vs nights y/y: r -0.05, n 14). The hard-data series are the ones with even a weak relationship and they are currently benign. *Data-quality flag: July 2026 PCE inflation (3.7% headline, 3.3% core) is running above CPI (3.4% / 2.5%), which is the reverse of the historical relationship; worth re-verifying against the raw releases before quoting.*

### 4.2 The Fed and rates

- Target range **3.50-3.75%** since the 9-10 Dec 2025 cut.
- **28-29 Jul 2026: held 9-3, with all three dissenters (Hammack, Kashkari, Logan) preferring a 25 bp HIKE.** The statement cites "elevated uncertainty that owes, in part, to the conflict in the Middle East" and inflation "in part reflecting supply shocks... including energy".
- **June 2026 dot plot medians: 3.8% end-2026, 3.6% end-2027** — the end-2026 median is above the current 3.625% midpoint, so the Fed's own median dot implies a hike.
- Market-implied hike probability was around **60%** on 4 Sep 2026 after the payrolls beat. BofA and Deutsche Bank both called for a September hike (Reuters, 22 Jun 2026); BofA looked for 75 bp of hikes across 2026.
- **This is the regime change most likely to be missed.** Models built in 2025 assumed a 2026-27 easing cycle. The live debate is hike-versus-hold, under a new chair (Kevin Warsh) whose reaction function strategists say they cannot yet read.
- FOMC dates left in 2026: **15-16 Sep (SEP), 27-28 Oct, 8-9 Dec (SEP)**. 2027: 26-27 Jan, 16-17 Mar (SEP), 27-28 Apr, 8-9 Jun (SEP), 27-28 Jul, 14-15 Sep (SEP), 26-27 Oct, 7-8 Dec (SEP).
- **10-year Treasury 4.77-4.82%** (3-4 Sep 2026); 12-month analyst-panel consensus about 4.55%.
- The **ECB was expected to raise 25 bp on 10 Sep 2026** to a 2.50% deposit rate (57 of 69 economists, Reuters survey cited 18 Aug 2026). **Two central banks tightening into each other is why the euro cross is going nowhere.**

### 4.3 The dollar

- Spot on 4 Sep 2026: **EUR/USD 1.16143, GBP/USD 1.35230, USD/JPY 156.25, USD/CAD 1.38374, USD/MXN 16.8872, USD/BRL 5.12470, DXY 99.176.**
- Quarterly averages that drive the y/y arithmetic: **1.15 quarter-to-date in 3Q26** (to 28 Aug) against 1.17 in 3Q25 — **-1.6% y/y, the first negative print since 4Q24**. DXY made a 52-week high of 101.80 on 24 Jun 2026 and has drifted to ~99 since.
- **Reuters FX poll, 2 Sep 2026 (55-66 strategists): EUR/USD median 1.16 at 3 months, 1.17 at 6 months, 1.18 at 12 months.** That is the consensus path used below.
- **The bank distribution is unusually wide and splits into two camps** (Exchange Rates UK survey of ~25 banks, 23 Aug 2026; survey median 1.18 for 1H27): dollar-bulls **JPMorgan 1.10, HSBC 1.10, Goldman 1.12, Citi 1.13-1.14** (all 2Q27) against euro-bulls **Nomura 1.22 (1Q27) and 1.25 (4Q27), Scotiabank 1.20-1.21, UBS 1.18-1.20, ING 1.18**. BofA (25 Jun 2026) has 1.15 end-2026 and 1.20 end-2027. Morgan Stanley and Deutsche Bank numeric targets: not found.
- **The strong-USD and weak-USD paths in `05_fx_schedule.csv` are not inventions — they are those two bank camps.** strong USD 1.13 → 1.09 → 1.10 (the JPM/HSBC/GS cluster); weak USD 1.19 → 1.25 (the Nomura/Scotiabank cluster). The 15-point gap between the camps is worth about **5.5 pp of ADR FX** on our fitted slope, which is a bigger swing than any plausible demand scenario.
- Drivers, per strategists (Aug-Sep 2026): **bull dollar** — 10-year at 4.82%, resilient payrolls, safe-haven flows from the Hormuz conflict, AI-driven equity inflows; **bear dollar** — Warsh uncertainty, federal debt above $40tn, comparatively hawkish ECB and BoE.
- Also relevant to the Canada corridor: a separate Reuters poll (3 Sep 2026, 32 analysts) has USD/CAD at 1.39 in 3 months and 1.36 in 12 months, after the US imposed 50% tariffs on about $20bn of Canadian imports and the Bank of Canada held at 2.25%.

### 4.4 Energy, airfares and airline capacity

- **EIA Short-Term Energy Outlook, published 11 Aug 2026** (modelling cutoff 6 Aug). Brent quarterly averages: 3Q26 **$85.21**, 4Q26 **$78.00**, FY2026 **$86.81**, **FY2027 $69.39**. WTI FY2026 $80.88, **FY2027 $65.39**. **Wholesale jet fuel $3.24/gal in 2026 falling to $2.50 in 2027 (-23%).**
- **The STEO is already stale.** Brent was **$96.06** and WTI **$92.10** on 4 Sep 2026, with a $99.38 intraday on 3 Sep, after renewed attacks post-cutoff. Capital Economics (4 Sep 2026) has Brent at $100 by end-2026 falling toward $70 in 2027 — same 2027 landing point, higher near-term path.
- **Hormuz is partially and fragilely reopening.** US naval escorts moved about 40 vessels and ~18m bbl through the strait on a recent day, against ~20m bbl/day pre-conflict and a 2Q26 collapse to 4.9m bbl/day.
- Where the fuel and fare series sit now: WTI **+25.2% y/y**, Gulf Coast jet fuel **+65.0% y/y** (spot $4.190/gal on 1 Sep 2026), CPI airline fares **+21.1% y/y** on our seasonally adjusted quarterly average (BLS headline for July 2026 was **+25.5% y/y**), all 3Q26 quarter-to-date, down from +48%, +83% and +24.6% in 2Q26.
- **IATA Global Outlook, June 2026 ("Energy in Crisis"): 2026 RPK growth cut to +2.1% from +4.9%; industry net profit $23bn on a 2.0% margin, the weakest since Covid; Brent assumed at $95 and jet fuel at $152/bbl, +70% y/y; Middle East RPK -11.4%.** IATA gives no 2027 numeric forecast.
- Airlines are recovering fuel in fares and cutting capacity. United took about **$6bn** of added FY26 fuel cost and recovered 80-90% via fares by Q3. American's FY26 fuel expense is up about **83% y/y** with fares offsetting roughly half — which is why its **Q3 2026 adjusted EPS is guided to a loss of $(0.70) to $(0.10) on revenue up 16-19%**. Ryanair is 80% hedged to March 2027 at $67/bbl against spot near $140.
- Capacity: **American cut 4Q26 system capacity 110 bp to +6.5%** (domestic +10.1%, transatlantic +1.8%, Pacific -2.9%) and cut planned 2027 long-haul route additions from 10-13 to 7; **Delta 4Q26 +3.2%, United +5.7%**; Southwest 3Q26 flat-to--1% and 4Q26 +4-5%; **IAG cut FY26 to flat** from "less than 3%"; **Air France-KLM cut twice**, to -1% short/medium-haul and +2-3% group.
- **TSA checkpoint throughput was -3.7% y/y on a 7-day average through 23 Aug 2026** — US air travel volume is being rationed by price.
- **2027 fare views are explicitly contradictory** and should be shown as a spread: Airlines for America's Chris Sununu says fares stay "relatively flat"; United's Scott Kirby expects "gradual increases into 2027"; Delta's Ed Bastian expects fares to stay elevated even after oil falls; Ryanair warns European short-haul fares could rise materially if oil stays high into summer 2027.
- **Transmission to ABNB, using our own coefficients.** ADR ex-FX has medium-confidence positive relationships with airline-fare CPI (+0.067 pp per 1%) and jet fuel (+0.027 pp per 1%). Airline-fare CPI moving from +21% to about -5% costs **-1.7 pp of ex-FX ADR**; the jet-fuel move is the same order. This is the main 2027 pricing headwind, and it is not in the driver model.

### 4.5 Hotels

- **CoStar/STR + Tourism Economics, 7 Aug 2026 revision: FY2026 US RevPAR +4.4% (raised from +2.8%), ADR +3.1% (from +2.0%), occupancy 63.1%.** H1 2026 sold 11.4 million incremental room-nights versus H1 2025, "fueled in part by the World Cup and America 250 celebrations".
- **FY2027: RevPAR +2.1%, ADR +1.6%, occupancy 63.4%**, with 2027 ADR growth explicitly **below inflation** and **June 2027 RevPAR forecast at -0.8%** on the World Cup comparison (1 Sep 2026). Supply growth 0.4% in 2026 and 0.6% in 2027 — still the tightest supply backdrop in decades.
- Every major operator raised FY26 RevPAR guidance at Q2: **Marriott 2.0-3.0% → 3.0-3.5%** (3 Aug), **Hilton 2.0-3.0% → 3.0-3.5%** (28 Jul), **Wyndham -1.0-1.0% → 0.0-1.0%** (22 Jul), **Choice → 0-1.25% US** (5 Aug); **Hyatt maintained 3.5-4.5%** (30 Jul) after a quarter in which Middle East and Africa RevPAR fell 28.3% and the conflict cost about 110 bp of total RevPAR growth.
- **Read-across for the ADR debate.** The margin note flagged that US hotels out-priced Airbnb's ex-FX ADR in 2Q26 for the first time since 4Q24. The 2027 forecast says that reverses: hotels at +1.6% ADR against Airbnb's +4% ex-FX run-rate. That supports a base-case ADR ex-FX assumption around +2.5% — slower, but still a premium.

### 4.6 US inbound, visas and the World Cup

- **Canada is the measured, unambiguous decline — and the measured substitution.** Statistics Canada: in 1Q26 Canadian residents took 5.5m trips including a US visit, **-10.6% y/y**, with US spending **-13.6%** to C$5bn, while **overseas trips rose 6.2% to 4.6m and overseas spending rose 16.7% to C$10.1bn** (via Travelweek, 31 Aug 2026). Full-year 2025 Canadian travel to the US was down about 25%. Florida's H1 2026 Canadian visitation was -13.9% y/y. **Canadians did not stop travelling; they went elsewhere, and Airbnb is a global platform.** The 50% US tariff on ~$20bn of Canadian imports (Sep 2026) makes a near-term corridor recovery unlikely.
- Our own BEA series: inbound foreign travel spending in the US ran **-4.8% y/y in 1Q26 and -0.4% in 2Q26** — still negative, improving off five quarters of decline.
- The **$250 visa integrity fee took effect 1 Oct 2025**; the US Travel Association's estimate at the time was about **$11bn** of lost tourism spending (Forbes, 15 Aug 2025). Press in 2026 carries larger revised numbers — roughly **$18bn** (Forbes, 3 Sep 2026) and Bloomberg's **$40bn** global travel toll (Jul 2026). **I could not retrieve the underlying forecast documents for either, so treat both as directional press figures, not sourced forecasts.** Industry CEOs met the President on 2-3 Sep 2026; the industry restated a 2030 target of 100m annual international visitors against falling arrivals.
- **The 2026 World Cup was smaller than the headlines.** International arrivals to the US during the 11-27 June group stage were **+0.2% y/y** (NTTO via Forbes, 14 Jul 2026). CoStar measured host-city hotel bookings up only **+0.5% y/y**. Cirium measured European flight bookings to host cities **-3.8%** and to New York **-15.8%**. The New York Hotel Association cut its own World Cup revenue forecast **60% to about $60m**. Host-city short-term rentals did better: Kansas City hotel occupancy +8%, STRs at 2-3x normal nightly rates on game days.
- Airbnb's framing: **more than 150,000 homes across host cities listed for the first time**, "millions" hosted, first-time bookers +11% in 2Q26 (highest in four years). **Management did not quantify a revenue or nights contribution.** AirDNA reported international demand for US short-term rentals had fallen for **13 consecutive months** before the tournament reversed it in host markets.
- **For the model the World Cup is a 2Q26 event and therefore a 2Q27/3Q27 comparison problem, not a 4Q26 one.** STR has already put a number on the hotel version (June 2027 RevPAR -0.8%). Airbnb never sized its own benefit, which cuts both ways: nothing to lap on paper, and nothing to point to if 2Q27 nights decelerate.

### 4.7 Europe

- **European Travel Commission, 10 Jul 2026: international arrivals to Europe +5% year-to-date; overnight stays +4.8% in 2Q26.** Greece arrivals +38.3%, Italy +21.1%, Malta +16%; Cyprus -17.9%, Turkiye -2.1%; Northern Europe arrivals +10%. **48% of respondents named affordability and value for money as Europe's key opportunity in 2Q26, up from 32% in 1Q26** — the clearest trade-down signal in the European data, and a positive read for Airbnb against hotels.
- Eurostat total EU tourism nights were up about **1.7% in H1 2026**, against our own Eurostat platform-nights series at **+9.7% y/y in 1Q26** (`data/processed/eurostat_platform_nights_monthly.csv`, latest month March 2026). **Platform nights are growing about 8 points faster than total European nights** — share gain inside a low-growth market, and the best independent corroboration of Airbnb's European acceleration. Use it as corroboration, not as a nowcast: our tests show Eurostat platform nights do not lead ABNB nights (r +0.62 on levels, +0.07 from 2024, fails both guards).
- WTTC (via eTurboNews, 5 Sep 2026) has European leisure spending growing **+3.7% in 2026** and Middle East travel and tourism GDP **contracting 14.5% in 2026**.

### 4.8 What the peers said about 2H26 (Q2 2026 calls; figures from SEC-filed releases)

| Company | Reported | Q2 2026 volume | Guidance | Demand language |
|---|---|---|---|---|
| **Booking (BKNG)** | 4 Aug | Room nights **+5%**; gross bookings +9% (+8% cc); **alternative accommodations +4%** | Q3 room nights **+3-5%**, gross bookings +4-6%, revenue +4-6%; FX about -1% to Q3 revenue | Fogel: "the underlying desire to travel remained resilient"; Q3-to-date "resilient... supported by healthy domestic travel trends" |
| **Expedia (EXPE)** | 5 Aug | Gross bookings +12%; room nights **+6%**; B2B bookings +21% | FY26 raised: bookings $129.5-130.8bn (+8-9%), revenue $16.05-16.22bn, margin expansion raised to +150-175 bp | "exceeded the high end of our guidance" |
| **Marriott (MAR)** | 3 Aug | Worldwide RevPAR +3.4% cc; US and Canada +5.0% | FY26 RevPAR **raised to 3.0-3.5%** | "strong broad-based demand generally expected to continue" |
| **Hilton (HLT)** | 28 Jul | System-wide RevPAR +3.9% cc; net unit growth +6.1% | FY26 RevPAR **raised to 3.0-3.5%** | Raise attributed to World Cup and travel demand |
| **Hyatt (H)** | 30 Jul | RevPAR +5.9% cc; US +6.7%; **MEA -28.3%** | FY26 RevPAR maintained 3.5-4.5% | Conflict cost ~110 bp of RevPAR growth |
| **Wyndham (WH)** | 22 Jul | Global RevPAR **-1% cc**; US +2% | FY26 raised to 0.0-1.0%; 2H domestic to ~2% | LatAm -7%, EMEA -6%, China -5% |
| **Choice (CHH)** | 5 Aug | Global RevPAR +1.7% cc; US +1.3% | FY26 US RevPAR raised to 0-1.25% | US extended-stay +13.0%, 12th straight double-digit quarter |
| **Delta (DAL)** | 10 Jul | TRASM **+12.4%**; domestic unit revenue +12% on +2% capacity; premium +17% | Q3 revenue growth mid-teens; FY26 EPS $6.50-7.50 affirmed | "broad demand strength"; main-cabin unit revenue up double digits for a second quarter |
| **United (UAL)** | 15 Jul | Revenue +16%; PRASM +12.5% | FY26 EPS raised to $9.00-11.00 | "close-in demand remained robust"; contracted business revenue +27% |
| **American (AAL)** | 23 Jul | Revenue +16.3%; premium PRASM +13.4% vs main cabin +8.8% | Q3 revenue +16-19% but adjusted EPS **$(0.70)-$(0.10)** | Managed corporate revenue +26% |
| **Airbnb (ABNB)** | 6 Aug | **Nights +10%**, GBV +16% (+15% cc), revenue +17% (+13% cc), ADR +5% (+4% ex-FX) | Q3 revenue $4.69-4.77bn (+15-17%, ~3 pp FX); GBV mid-teens on **low-double-digit nights**; FY26 raised to "at least mid teens" revenue and "at least 35.5%" margin | Mertz: "the impact to our business from the conflict was less than we had anticipated"; "In Q3, we are not assuming any significant impact related to the conflict" |

**The single most important number in that table is the gap.** Booking guided Q3 room nights to **+3-5%** and its alternative-accommodation nights grew **+4%**; Airbnb guided Q3 nights to **low double digits**. That is a six-to-seven point gap on the same underlying travel demand. **Whatever is driving Airbnb's nights in 2026 is not the macro cycle** — it is share, product (Reserve Now Pay Later at over 20% of GBV, the app at 64% of nights, first-time bookers +11%) and expansion markets (net nights growing about twice as fast as core). That cuts the right way for the bull case, and it also means peer read-across is a poor forecasting tool for ABNB's KPI.

### 4.9 Policy calendar and tail risks

- **Tariffs remain legally unresolved.** The Supreme Court struck down the IEEPA "Liberation Day" tariffs 6-3 around February 2026; roughly $100bn was refunded; successor tariffs were imposed under other authority and 25 states are suing, calling them a pretext (AP, Aug 2026). A second adverse ruling is a live 2027 event cutting both ways on inflation and sentiment. Separately, the US imposed 50% tariffs on about $20bn of Canadian imports after talks collapsed (Sep 2026).
- **Government funding runs to 11 Dec 2026** under a continuing resolution — five weeks after the Q3 print and right at the pitch date. The Oct-Nov 2025 shutdown suppressed CPI and PCE releases; a repeat would blind the nowcast.
- **Midterm elections 3 Nov 2026 — two days before Airbnb's Q3 print.** Not a fundamental driver, but a source of tape volatility inside the reaction window.
- The **Middle East conflict** is the recurring line item in every travel disclosure this year. The EIA base case assumes Hormuz normalises by early 2027; that assumption is doing a lot of work in scenario A below.

---

## Section 5. Three scenarios (`05_macro_scenarios.csv`)

Nights, ADR ex-FX and take rate are **my judgement**, anchored on the realised 2022-26 range (nights 7.4-12.3% outside base effects; ADR ex-FX 0.5-4%). **FX comes from the fitted schedule in Section 2, not from judgement.** Margin is the model base of 36.5% for FY27 moved by the margin-bridge chain (+0.35/pt nights, +0.46/pt ADR ex-FX, +0.47/pt FX, +0.64/pt take-rate revenue), then a judgement cost-response share (A reinvests half the mechanical upside, consistent with the Feb 2025 and Aug 2026 pattern; C recovers 40% of the shortfall through slower S&M growth, the 2022-23 pattern). Revenue growth is multiplicative across nights x ADR ex-FX x revenue FX x take rate.

| | **A. Energy relief, soft dollar** | **B. Muddle through, stagflation-lite** | **C. Recession or renewed shock** |
|---|---|---|---|
| **Probability** | **30%** | **50%** | **20%** |
| Macro | EIA base delivers: Brent $86.81 avg 2026 → **$69.39 in 2027**, jet fuel $3.24 → $2.50/gal; Hormuz normalises. Fed hikes once then cuts from mid-2027; GDP 2.3% → 2.7%; unemployment 4.2-4.3%; PCE to 2.3%; Michigan recovers toward 65. **EUR/USD to 1.21-1.25** (Nomura/Scotiabank camp). Airfares turn negative y/y from 2Q27; airline capacity restored; US inbound stabilises; Europe overnights +4-5% | Brent $80-90 into 1H27 then easing; at most one Fed hike then hold (dots 3.8% / 3.6%); PCE 3.6% → 2.3%, core PCE 3.3% → 2.4%; GDP 2.1-2.2%; unemployment 4.3%; Michigan 50-58 and Conference Board expectations sub-80 but delinquencies still improving. **EUR/USD 1.16-1.18 (Reuters poll median)**; airfares +15-20% until they lap in 2Q27; US hotel RevPAR +4.4% then +2.1%; US inbound flat; Europe overnights +3-4% | Hormuz closes again (Brent >$110) or the Fed over-tightens. Unemployment to 5% by mid-2027; claims +20% y/y; Michigan below 45. **EUR/USD 1.09-1.13** (JPMorgan/HSBC/Goldman camp) on safe-haven flows and a wider differential. Airline capacity cuts deepen from an already-cut base; US inbound -5% further; European long-haul outbound -10%; US hotel RevPAR negative |
| **4Q26 nights y/y** | +11.0% | **+9.5%** | +7.5% |
| 4Q26 ADR ex-FX | +3.5% | +3.0% | +2.0% |
| 4Q26 ADR FX (pp) | +0.4 | -0.7 | -1.9 |
| **4Q26 revenue FX (pp)** | **-0.4** | **-0.4** | **-0.4** |
| 4Q26 take rate (pp) | +0.5 | +0.5 | +0.5 |
| **4Q26 revenue y/y** | **+15.0%** | **+12.9%** | **+9.7%** |
| FY26 EBITDA margin | 36.3% | 36.0% | 35.6% |
| **FY27 nights y/y** | +10.5% | **+8.5%** | +5.5% |
| FY27 ADR ex-FX | +3.0% | +2.5% | +0.5% |
| FY27 ADR FX (pp) | +1.9 | -0.1 | -2.8 |
| **FY27 revenue FX (pp)** | **+0.9** | **-0.6** | **-2.6** |
| FY27 take rate (pp) | 0.0 | 0.0 | -0.3 |
| **FY27 revenue y/y** | **+14.8%** | **+10.5%** | **+3.0%** |
| FY27 margin, mechanical | 38.1% | 36.5% | 33.4% |
| **FY27 margin after cost response** | **37.3%** | **36.5%** | **34.7%** |
| ADR ex-FX cross-check from claims | +0.9 pp | 0.0 pp | -3.4 pp |
| ADR ex-FX cross-check from airfare lap | -1.7 pp | -1.3 pp | -0.7 pp |

**Probability-weighted FY27: nights +8.5%, revenue +10.3%, Adjusted EBITDA margin 36.4%.** That revenue number sits about 2 points below the driver model's base case (nights +9%, ADR ex-FX +3%, FX 0 → +12.3%). **The entire gap is the FX schedule**, not a demand disagreement. `model/assumptions.md` currently carries FY27 base FX at 0%; the fitted schedule on the Reuters-poll path says **-0.6 pp**, and the JPMorgan/Goldman dollar view would make it -2.6 pp.

### The likely shape of guidance, and how the stock has reacted to that shape

**5 November 2026 (Q3 print and Q4 guide).**

| Scenario | The guide | Reaction analogue |
|---|---|---|
| **A** | Q4 revenue **+13-15%**; FY26 revenue lifted from "at least mid teens" toward 16-17%; FY26 margin raised above "at least 35.5%"; nights guided at or above the Q3 rate | 4Q22 (15 Feb 2023, **+13.4%**), 4Q24 (14 Feb 2025, **+14.4%**), 2Q26 (7 Aug 2026, **+17.4%**) — nights guided to accelerate |
| **B** | Q4 revenue **+11-13%**, of which about 3 pp of the step-down from the Q3 15-17% is the FX schedule, not demand; nights high-single to low-double against the RNPL lap; FY26 "at least mid teens" reiterated or nudged to ~16%; margin "at least 35.5%" reiterated; take rate flat; **no FY27 guide** (management has never given one in November) | 4Q25 (13 Feb 2026, **+4.6%**) and 3Q25 (7 Nov 2025, **+0.3%**) if nights hold; 2Q25 (7 Aug 2025, **-8.0%**) if the nights guide slips below the Q3 rate and "moderation" or "lead times" is said aloud |
| **C** | Q4 revenue **+8-10%** with "moderation", "shorter lead times" and "macro uncertainty" in the letter; nights guided below the Q3 rate; FY26 held at mid teens only because nine months is banked; Q4 margin guided down y/y | 3Q22 (-13.4%), 1Q23 (-10.9%), 2Q24 (-13.4%), 3Q24 (-8.7%), 2Q25 (-8.0%) — every one a decelerating nights guide; **post-2022 mean day-1 -5.4% (n 9)** |

Base rates from `05_reaction_by_accel.csv`, all 23 prints: accelerating-nights quarters average **+3.3% day-1 / +3.4% excess** (n 6); decelerating quarters **-3.3% / -4.1%** (n 11), and the gap widens post-2022 to **+6.7% versus -5.4%**. The 20-session excess is **+1.3% for accelerating and -8.0% for decelerating** post-2022 — the move extends rather than reverses (consistent with `research/notes/2026-09-05_abnb-major-moves.md` section 2b).

**February 2027 (Q4 print and FY27 guide).**

| Scenario | The guide |
|---|---|
| **A** | FY27 revenue "mid teens"; Adjusted EBITDA margin guided up, floor at or above 36.5%; FX described as a 2H27 tailwind; buyback authorisation topped up |
| **B** | FY27 revenue "low double digits" (10-12%); margin "approximately stable" or a floor around 36%; FX called out as a modest 1H27 headwind; continued reinvestment in AI, expansion markets and Services |
| **C** | FY27 revenue "mid-to-high single digits"; the margin floor guided **down** (the Feb 2025 pattern, when a 34.5% floor was set to protect reinvestment); named cost actions on marketing and headcount |

**The asymmetry to be aware of.** The Q4 revenue guide will step down about 3 points on FX in every scenario. The historical reaction function keys on **nights**, not on the revenue guide — 4Q24 is the cleanest evidence, when the revenue guide came in below the Street and the stock rose 14.4% on the nights beat. So the FX step-down should not on its own cause a de-rate. But the stock closed at **$181.94 on 4 Sep 2026** after a +17.4% / +22.1% move on 7 Aug, so it is being carried on an acceleration narrative, and the November bar is high.

---

## Section 6. What would change our mind

### Before 5 November 2026 (the Q3 print)

| Date | Release | What we are watching | Threshold that changes the view |
|---|---|---|---|
| **Daily to 30 Sep** | EUR/USD and the broad dollar | The 3Q26 quarterly average vs 1.17 in 3Q25 | If EUR/USD averages below 1.14 for September, ADR FX in 3Q26 goes below -2 pp and reported ADR growth drops to ~+2% |
| **11 Sep** | August CPI (BLS) | Airline fares, lodging away from home | Airline fares below +15% y/y would pull our ADR ex-FX nowcast toward +3% |
| **15-16 Sep** | **FOMC with SEP** | Hike or hold; 2027 dots; growth and unemployment revisions | A hike plus a higher 2027 dot pushes the dollar toward the strong-USD path and takes 1-2 pp off FY27 revenue growth |
| **30 Sep** | Personal Income and Outlays (Aug) + 2Q GDP third estimate | BEA accommodations, inbound/outbound travel, real DPI, saving rate | BEA accommodations nominal below +2% y/y would be the first coincident sign of US softness in the series that actually co-moves |
| **2 Oct** | September Employment Situation | Payrolls, unemployment, claims trend | Unemployment at or above 4.4%, or claims turning positive y/y, flips the ADR ex-FX watch-list signal negative |
| **14 Oct** | September CPI | Airline fares, lodging | as above |
| **20-31 Oct** | **Q3 prints: MAR, HLT, BKNG, EXPE, DAL/UAL/AAL** | BKNG's Q4 room-night guide; hotel FY26 RevPAR revisions; airline 4Q26 capacity and 2027 framing | A BKNG Q4 room-night guide below +3%, or a second hotel FY26 RevPAR cut, is the strongest available evidence of a genuine industry turn |
| **27-28 Oct** | FOMC (no SEP) | Second hike, or a pause signal | |
| **29 Oct** | 3Q26 GDP advance + Personal Income and Outlays (Sep) | Consumer spending in the print quarter | |
| **Late Oct** | Michigan final, Conference Board (Oct) | Sentiment | Note: sentiment has **no** relationship to nights (r -0.05). Watch it for the multiple, not the KPI |
| **3 Nov** | US midterm elections | Tape volatility two days before the print | |
| **5 Nov** | **ABNB Q3 2026** | Nights growth versus the Q3 "low double digit" guide; the **Q4 nights** guide; whether the Q4 revenue guide's FX assumption is disclosed | **The one number that matters: Q4 nights guided at or above the Q3 rate.** If it is, the ~3 pp FX-driven revenue step-down is noise |

### Before the pitch (December 2026)

| Date | Release | Why |
|---|---|---|
| **6 Nov** | October Employment Situation | First post-print labour read |
| **10 Nov** | October CPI | Airline-fare lap begins to show |
| **25 Nov** | 3Q26 GDP second estimate + Personal Income and Outlays (Oct) | |
| **4 Dec** | November Employment Situation | |
| **8-9 Dec** | **FOMC with SEP** | The 2027 dots that set the dollar path underlying our FY27 revenue FX |
| **10 Dec** | November CPI | |
| **11 Dec** | **Government funding expires** | A shutdown suppresses the CPI/PCE releases the nowcast depends on, as in Oct-Nov 2025 |
| **Early Dec** | EIA STEO (Nov and Dec editions) | Whether the 2027 Brent path stays near $69 or is revised up toward the current $96 spot |
| **Continuous** | EUR/USD daily | 4Q26 revenue FX is 84% locked; 1Q27 is 34% locked at quarter end and fully locked by 31 Mar 2027 |

**Things that would falsify the core claims of this note:**
1. A 3Q26 print where reported revenue FX comes in materially away from +3 pp (say below +1.5 or above +4.5) would break the lagged-FX spec and require refitting.
2. A quarter where nights growth moves more than 2 points on a macro variable with no product or comp explanation would resurrect the macro-to-nights channel we have declared dead.
3. A Q4 guide in which management attributes the revenue step-down to demand rather than FX would mean either that they see something we do not, or that the framing risk in point 7 of the bottom line has materialised.

---

## Corrections to existing work

1. **`research/notes/predictive/03_macro-altdata-nowcast.md`, finding 1**, says the FX tailwind to ADR in 3Q26 is "roughly +0.8 pp" from the broad-dollar fit. The EUR/USD fit, which has the higher r (0.99 vs 0.96), gives **-1.3 pp** on the same quarter-to-date data. The honest statement is "roughly flat, in a -1.3 to +0.8 range". Both fits agree that reported ADR growth converges on the ex-FX run-rate of about +4%, so the conclusion survives; the point estimate should be widened.
2. **The same note treats FX-to-revenue as the same contemporaneous mechanism as FX-to-ADR.** It is not. Revenue FX lags spot by one to two quarters because of the booking-to-stay lag and the hedging programme, and the contemporaneous fit predicts -1.6 pp for a quarter management has guided at +3 pp. Section 2 above supersedes it for anything forward-looking.
3. **Several medium-confidence relationships in the first cut of `05_macro_sensitivities.csv` were common-trend artefacts** — all-items CPI and PCE services against nights y/y, consumer credit against nights. The first-difference guard added in this run demotes them. The earlier `r_from2024 < 0.30` threshold alone was too loose (all-items CPI scraped through at 0.319).
4. **`model/assumptions.md` carries FY27 base-case ADR FX at 0% and bear at -1.5%.** The fitted schedule on the Reuters-poll consensus path gives **ADR FX -0.1 pp and revenue FX -0.6 pp** for FY27; the dollar-bull bank camp gives **-2.8 pp and -2.6 pp**. The base is roughly right; the bear is not bearish enough on FX.

---

## For the model

Parameters this workstream supplies. All are in `data/processed/overnight/05_fx_schedule.csv`, `05_macro_sensitivities.csv` and `05_macro_scenarios.csv`.

| Parameter | Value | Unit | Source |
|---|---|---|---|
| ADR FX effect | `-0.569 + 0.451 x EUR/USD y/y` | pp of ADR growth | Fit, 1Q22-2Q26, n 17, r +0.99 |
| ADR FX effect (dollar version) | `+0.525 - 0.715 x broad USD y/y` | pp of ADR growth | Fit, n 17, r -0.96 |
| **Revenue FX effect** | `-0.640 + 0.413 x mean(EUR/USD y/y at t-1, t-2)` | pp of revenue growth | Fit, n 17, r +0.80; validated against the +3.0 pp Q3 2026 guide; error band ±0.8 pp |
| Revenue FX, 4Q26 | **-0.4** | pp | Schedule; 84% of the driver already realised |
| Revenue FX, 1Q27 / 2Q27 / 3Q27 / 4Q27 (consensus) | -1.0 / -0.8 / -0.6 / -0.1 | pp | Reuters poll path (EUR/USD 1.16-1.18) |
| Revenue FX, FY27: consensus / strong USD / weak USD | **-0.6 / -2.6 / +0.9** | pp | Three EUR/USD paths |
| ADR FX, FY27: consensus / strong USD / weak USD | -0.1 / -2.8 / +1.9 | pp | Same |
| ADR ex-FX sensitivity to airline-fare CPI | +0.067 | pp per 1% of fare CPI y/y | n 14, r +0.70, medium confidence |
| ADR ex-FX sensitivity to Gulf jet fuel | +0.027 | pp per 1% y/y | n 14, r +0.70, medium confidence |
| ADR ex-FX sensitivity to initial claims | -0.172 | pp per 1% y/y | n 14, r -0.78, medium confidence |
| **2027 airfare-lap drag on ADR ex-FX** | **-1.3 to -1.7** | pp | Airline-fare CPI from +21% to about -5%, on the coefficient above |
| Macro sensitivity of nights growth | **zero, at any confidence level** | | 1,408 pairs tested; 0 high, 1 medium (coincident) |
| Margin transmission | +0.35 / +0.46 / +0.47 / +0.64 per pt of nights / ADR ex-FX / FX / take-rate revenue | pp of EBITDA margin | `research/notes/2026-09-05_margin-drivers.md`, re-used here |
| Broad USD elasticity of margin | **-0.28 pp per +1% of broad USD y/y** | pp | Chain of the two FX channels |
| Scenario FY27 nights / revenue / margin | A 10.5 / 14.8 / 37.3; B 8.5 / 10.5 / 36.5; C 5.5 / 3.0 / 34.7 | % and % | `05_macro_scenarios.csv` |
| **Probability-weighted FY27** | **nights +8.5%, revenue +10.3%, margin 36.4%** | | 30/50/20 weights |

**One change to request in `model/assumptions.md`:** set FY27 base ADR FX to **-0.1 pp and revenue FX to -0.6 pp** (currently 0%), and set the bear-case FX to **-2.6 pp** rather than -1.5%.

---

## For the 5 Nov card

1. **3Q26 nowcast, all knowable today.** ADR ex-FX **+4%** (three independent fits: claims +4.1, jet fuel +4.0, airfares +3.6). ADR FX **roughly flat**, range -1.3 to +0.8 pp, versus +1.3 pp in 2Q26 and +5.0 in 1Q26. Reported ADR therefore **+3% to +5%**. Revenue FX **about +3 pp**, matching the guide. Nights guided "low double digit", so **at or above 2Q26's +10.3%**. The revenue guide is $4.69-4.77bn (+15-17%); the 2023-26 average beat is about +2%, which puts the print near **$4.82bn, +18%**.
2. **The number that decides the day is the Q4 nights guide, not the Q4 revenue guide.** Post-2022, an accelerating nights guide has averaged **+6.7%** day-1 (n 5) and a decelerating one **-5.4%** (n 9), and the 20-session excess extends the move rather than reversing it (+1.3% vs -8.0%).
3. **Expect the Q4 revenue guide to be roughly 3 points below the Q3 rate, and be ready to say why.** Revenue FX goes from about +3 pp in Q3 to about **-0.4 pp in Q4**, and 84% of that is FX that has already happened. Central case Q4 revenue **+11-13%**; a guide in that band with nights held at or above the Q3 rate is a **neutral-to-good** print, not a deceleration. Below +9%, or nights guided down, is the bear case.
4. **The implied Q4 arithmetic to check on the day.** FY25 revenue was $12,241m and 1H26 is $6,286m. If Q3 prints near $4,820m (the guide midpoint plus the 2023-26 average +2% cushion), then FY26 revenue growth of 15% / 16% / 17% implies Q4 revenue of **$2,971m (+7.0%) / $3,094m (+11.4%) / $3,216m (+15.8%)**. Our base case of +12.9% sits at an FY26 of about 16.2%. Since "at least mid teens" is a floor and every floor since 2023 has been beaten, a Q4 guide in the +11-13% band is the FY26 outcome the company is already steering toward, and about 3 points of it is FX.
5. **Watch for these three sentences in the letter and on the call:** (a) whether the Q4 FX assumption is quantified as it was for Q3 — if it is not, the Street will read the step-down as demand; (b) any use of "moderation", "shorter lead times" or "macro uncertainty", which cost 8-13% in 2022, 2023, 2024 and 2025; (c) whether the World Cup contribution to 2Q26 is finally quantified, because that number becomes the 2Q27 lap.
6. **Context to have ready.** Booking guided Q3 room nights +3-5% and grew alternative-accommodation nights +4%; Airbnb guided low double digits. Hotels are forecast at +2.1% RevPAR and +1.6% ADR in 2027 against Airbnb's +4% ex-FX run-rate. European platform nights are growing about 8 points faster than total European nights. **None of Airbnb's 2026 growth is coming from the macro cycle, which is exactly why the macro path matters far less to this pitch than the FX schedule does.**
