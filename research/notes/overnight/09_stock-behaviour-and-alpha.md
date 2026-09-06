# ABNB stock behaviour beyond the print: drift, seasonality, factors, events, options and simple rules

- **Date:** 2026-09-06. **Author:** Krishang Surapaneni (compiled with Claude Code), overnight workstream 09.
- **Script:** `analysis/src/overnight/09_stock_behaviour.py` (rebuilds every CSV and figure below from the raw inputs; `py -3.13`).
- **Price data:** `data/processed/overnight/09_prices_daily.csv` — yfinance adjusted closes, 1 Dec 2020 to 4 Sep 2026, for ABNB, QQQ, SPY, XLY, IVE, IVW, IWM, MTUM, BKNG, EXPE, TRIP, MAR, HLT, H, UBER, DASH, JETS, UUP, ^TNX, ^VIX. Cross-checked against `data/processed/abnb_daily_close.csv`: 1,440 overlapping sessions, max absolute difference $0.005.
- **Other inputs:** `09_ff_factors_daily.csv` (Ken French 5 factors + momentum, through 31 Jul 2026); `09_analyst_actions.csv` (466 sell-side actions, yfinance/Benzinga feed); `09_short_interest.csv` (84 semi-monthly settlements, marketbeat + nasdaq.com, Feb 2023 to 14 Aug 2026); `data/processed/abnb_earnings_reactions.csv` (23 prints); `abnb_major_moves_events.csv` (41 moves ≥7%); `predictive/02_peer_prints.csv` (BKNG/EXPE/MAR/HLT print dates); `citadel-abnb/research/regulatory/factors.json` (32 dated regulatory factors); `citadel-abnb/data/processed/abnb_options_ledger.csv` (5 Sep 2026 IV snapshot); BLS release-date archives (`bls.gov/schedule/<year>/home.htm`, fetched 6 Sep 2026); a live yfinance ABNB option chain pulled 6 Sep 2026; fintel.io 13F snapshot.
- **Outputs:** 24 CSVs `data/processed/overnight/09_*.csv`, 6 figures `analysis/figures/overnight/09_*.png`.

**Read this first.** 218 tests are logged in `09_test_ledger.csv`; 55 of the 215 carrying a p-value are below 0.05 against roughly 11 expected by chance. At a Bonferroni threshold of p = 0.00023 **only eight survive: seven of them are the analyst-action tests, whose significance is a mechanical artefact of those events sitting on print days (§6), and the eighth is a price-target correlation that dissolves once the overlapping samples are removed (§9). Nothing else in this note clears a multiple-comparisons hurdle.** The excess of nominal hits over chance is also inflated by non-independence: the drift is tested at six nested windows × four groups, R2 and R2b are the same trade, and the seasonal block and R7 are the same fact. Read everything below as a base rate to quote, not a signal to trade.

---

## 1. Bottom line

1. **ABNB has stopped being a macro stock and become an idiosyncratic one.** Beta to QQQ fell from 1.28 (2022) to 0.91 (2026); beta to hotels (MAR/HLT/H) fell from 1.24 to 0.45; beta to the 10-year yield is statistically zero in every single year (|t| ≤ 0.9). 64% of 2026 daily variance is idiosyncratic, and the whole of 2026's +34% price move is model alpha (+32.7 pts) — QQQ contributed +14.2 pts and consumer discretionary −12.9. The 2025–26 story is company-specific re-rating, not beta.
2. **The post-print drift is real, it is negative, and it lives entirely in the up-prints.** Over the 20 sessions *after* the reaction day (day 1 excluded), the mean excess return vs QQQ across 23 prints is **−3.7%** (t = −2.16, p = 0.042, negative in 15 of 23). Split by the sign of day 1: prints that popped drift **−7.1%** over the next 20 sessions (t = −2.58) and **−14.8%** over 60 (t = −2.36, negative 8 of 10). Prints that fell drift **−0.7%** / **+0.4%** — indistinguishable from zero. Pops fade; drops do not bounce.
3. **But the fade has broken in the current regime.** The last three up-prints (Q3'25, Q4'25, Q2'26) drifted −1.4%, +5.5% and +3.2%. Restricted to 2023 onward the all-print drift is −2.3% (t = −1.15, not significant). The "sell the pop" rule is a 2021–22 and 2024 phenomenon that has not worked since mid-2025.
4. **The run-up into the print carries no information.** 20-session excess run-up vs day-1 excess return: r = −0.004 (n = 23). Day-1 reaction vs the following 20 sessions: r = −0.42 (p = 0.045) — mild reversal, consistent with (2).
5. **May is the one genuine calendar effect and it is large.** ABNB has underperformed QQQ in May in **all six years**, by an average of **−14.5%** (p = 0.0016), and underperformed the BKNG/EXPE average in all six (−6.4%, p = 0.045). Only about −3.0 pts of that is the Q1 print day. February is the mirror image: +7.7% excess, 6 of 6 (p = 0.005). November has been negative 5 of 5 (−5.1%, p = 0.03). n = 5–6 and these were found by scanning 54 seasonal tests, so treat them as base rates.
6. **Almost nothing outside the print moves the stock.** Peer prints (BKNG, EXPE, MAR, HLT), CPI releases, buyback authorisations, Summer Release product launches and every dated European regulatory event produce abnormal returns indistinguishable from zero. Three exceptions in six years: the S&P 500 inclusion **announcement** (+7.1% abnormal on 5 Sep 2023, t = 2.7 — the effective date itself was −0.1% and the following 20 sessions gave back −9.7%), the tariff shock (Apr 2025) and the AI-disintermediation scare (3 Feb 2026, −6.2%, t = −3.9).
7. **Analyst actions are a consequence, not a cause.** Price-target raises show +2.9% same-day CAR across all 206 events (t = 6.0) — but once you drop the ones inside a print week the effect is **−0.2%, p = 0.25**. Same for cuts (−3.8% → −0.3%) and upgrades (+2.6% → +0.5%). The sell side moves after the stock.
8. **The option market is not pricing a 5 Nov event premium yet.** On the 5 Sep 2026 ledger the Nov-20 straddle (13.38% of spot, 76 dte) and the Dec-18 straddle (15.65%, 104 dte) scale as √time to within 0.002 pts, i.e. an implied event premium of **zero** 60 days out. The historical base rate is the useful number: mean absolute day-1 move **7.1%**, median **6.9%**, and 10 of 23 prints moved ≥8%.
9. **Positioning is neutral-to-crowded-long and has no predictive content.** Short interest is 2.17% of shares (14 Aug 2026), near its lowest since 2023 (range 1.74–5.44%, mean 2.84%) and uncorrelated with forward 1- and 3-month returns (|r| ≤ 0.15). The sell side is at 49% Buy, its highest reading since 2023 (trough 26.7%), and the mean live price target ($179.9) is now **below** the $181.94 spot.
10. **Only two of 21 backtested rules survive; neither is tradeable as stated.** "Short the pop" (R2) and the May seasonal (R7) both have stable leave-one-year-out signs, but R2 has failed in both 2026 prints and R7 was selected after looking at the table. Every momentum variant and every mean-reversion variant loses to buy-and-hold.

---

## 2. Test accounting

| Block | Tests logged | Notes |
|---|---|---|
| 1 Factor models | 2 entries covering 88 coefficient t-tests | 8 samples × 5 macro betas, 8 samples × 6 FF betas |
| 2 Earnings drift | 28 | 6 windows × 4 groups, plus robustness and 3 correlations |
| 3 Seasonality | 54 | 3 series × (12 months + 4 quarters + 2 halves) |
| 4 Event studies | 96 | 16 event groups × 6 windows |
| 6 Rule backtests | 21 | 11 rules × horizons, plus the buy-and-hold benchmark |
| 7 Positioning | 17 | short interest, ratings, price-target premium |
| **Total logged** | **218** | 55 of 215 with p < 0.05 vs ~11 expected; 8 clear Bonferroni, all discounted |

Full ledger: `data/processed/overnight/09_test_ledger.csv`. 55 of the 215 tests with a p-value are below 0.05 against 10.8 expected. Dropping the 60 analyst-action tests leaves 36 of 155 below 0.05 against 7.8 expected — still an excess, but the remaining tests are heavily non-independent (nested event windows, overlapping holding periods, and the same underlying fact entering through several blocks). Only eight tests clear a Bonferroni threshold of 0.00023, and all eight are discounted in §6 and §9.

---

## 3. Factor exposure (`09_factor_model_by_period.csv`, `09_factor_betas_rolling.csv`, `09_ff_factor_model.csv`, figures `09_rolling_betas.png`, `09_variance_decomposition.png`)

Model: daily ABNB return on QQQ, XLY orthogonalised to QQQ, an equal-weight travel basket (BKNG, EXPE, MAR, HLT, H, JETS) orthogonalised to both, the daily change in the 10-year yield (bp) and UUP. Sequential orthogonalisation makes the return contributions additive.

| Year | n | β QQQ | β XLY⊥ | β travel⊥ | β 10y (per bp) | t | β UUP | R² | Idio share of variance | Ann. vol | Ann. idio vol |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2021 | 252 | 1.10 | 0.49 | 0.55 | −0.001 | −0.03 | 0.17 | 0.20 | 80% | 53.3% | 47.7% |
| 2022 | 251 | 1.28 | 1.06 | 0.86 | 0.006 | 0.35 | 0.13 | 0.70 | 30% | 60.5% | 33.4% |
| 2023 | 250 | 1.26 | 1.27 | 0.78 | −0.002 | −0.12 | 0.38 | 0.45 | 55% | 42.4% | 31.4% |
| 2024 | 252 | 0.99 | 0.62 | 0.57 | 0.010 | 0.43 | −0.16 | 0.34 | 66% | 33.3% | 27.1% |
| 2025 | 250 | 0.93 | 0.68 | 0.53 | 0.020 | 0.88 | −0.02 | 0.50 | 50% | 37.6% | 26.5% |
| 2026 | 169 | 0.91 | 1.07 | 0.51 | −0.002 | −0.05 | 0.06 | 0.36 | 64% | 39.1% | 31.2% |

Univariate betas, same samples:

| Year | to QQQ | to SPY | to OTAs (BKNG/EXPE) | to hotels (MAR/HLT/H) |
|---|---|---|---|---|
| 2022 | 1.40 | 1.74 | 1.06 | 1.24 |
| 2023 | 1.23 | 1.69 | 0.85 | 0.95 |
| 2024 | 0.93 | 1.35 | 0.57 | 0.72 |
| 2025 | 1.00 | 1.26 | 0.67 | 0.78 |
| 2026 | 0.54 | 1.16 | 0.54 | 0.45 |
| Rolling 126d at 4 Sep 2026 | 0.86 | — | 0.64 | 0.49 |

- **Rates.** The 10-year beta has never been significant in any year. The 2022 "ABNB is a duration stock" story shows up as a QQQ beta of 1.28, not as a rates beta. If the pitch wants a rates argument it has to run through the multiple, not through a daily beta.
- **What drove 2025–26 (return attribution, `contrib_*` columns).** 2025: total +10.1 pts, of which QQQ +20.0, XLY⊥ −2.1, travel⊥ +0.6, macro −0.7, alpha −7.7. 2026 to 4 Sep: total +34.0 pts, of which QQQ +14.2, XLY⊥ **−12.9**, travel⊥ −0.1, macro +0.1, **alpha +32.7**. In other words, in 2026 ABNB has fought a falling consumer-discretionary tape and won on stock-specific news (the Q2 print alone was +17.4%).
- **Fama-French 5 + momentum (`09_ff_factor_model.csv`).** Market beta is stable at 1.25–1.32 across every sample. The one persistent style tilt is **negative momentum**: β_MOM = −0.37 full sample (t = −6.6), −0.53 from 2023 (t = −7.7), −0.77 in 2026 (t = −6.6). ABNB behaves as a contrarian/anti-momentum name — it rallies when the momentum factor sells off. SMB and HML loadings are insignificant post-2021.

---

## 4. Earnings drift and run-up (`09_earnings_drift_by_print.csv`, `09_earnings_drift_stats.csv`, `09_earnings_drift_robustness.csv`, `09_runup_vs_reaction.csv`, figure `09_earnings_drift.png`)

Event time is anchored 21 sessions before the reaction day; the path is cumulative ABNB minus QQQ. Day 1 is the reaction day; drift windows exclude it.

| Window | Group | n | Mean | Median | % positive | t | p | Wilcoxon p |
|---|---|---|---|---|---|---|---|---|
| run-up −20..−1 | all | 23 | +1.1% | +0.2% | 52% | 0.65 | 0.52 | 0.54 |
| day 1 | all | 23 | +0.6% | −0.1% | 48% | 0.30 | 0.76 | 0.89 |
| drift +1..+5 | all | 23 | **−2.8%** | −2.4% | 43% | −2.45 | **0.023** | 0.042 |
| drift +1..+20 | all | 23 | **−3.7%** | −3.7% | 35% | −2.16 | **0.042** | 0.052 |
| drift +1..+60 | all | 22 | −6.5% | −6.3% | 36% | −1.86 | 0.077 | 0.11 |
| drift +1..+20 | day 1 up | 11 | **−7.1%** | −8.8% | 27% | −2.58 | **0.027** | 0.067 |
| drift +1..+20 | day 1 down | 12 | −0.7% | −3.4% | 42% | −0.37 | 0.72 | 0.68 |
| drift +1..+60 | day 1 up | 10 | **−14.8%** | −17.3% | 20% | −2.36 | **0.042** | 0.049 |
| drift +1..+60 | day 1 down | 12 | +0.4% | +1.3% | 50% | 0.17 | 0.87 | 0.85 |
| drift +1..+20 | from 2023 | 15 | −2.3% | −3.2% | 40% | −1.15 | 0.27 | 0.30 |

**Is the −3.7% distinguishable from zero, and is it concentrated?** Leave-one-year-out (`09_earnings_drift_robustness.csv`): every one of the six folds keeps a negative mean, between −3.0% and −4.7%, with p from 0.022 to 0.113. Dropping the single worst print gives −3.2% (p = 0.078); dropping the best gives −4.5% (p = 0.013); dropping both tails gives −3.9% (p = 0.026). So it is not one event — but it is only marginally significant on 23 observations, and it thins out badly in the recent sub-sample. **It survives concentration checks and fails the regime check.**

**Run-up.** No relationship in either direction: run-up vs day 1 r = −0.004 (p = 0.98), run-up vs subsequent 20-day drift r = −0.11 (p = 0.62). Buying 20 sessions before the print and selling at the release close (rule R3) earns +1.0% mean excess on 23 tries, t = 0.59.

**Reconciliation with existing work** (`09_reconciliation_vs_existing.csv`). Our day-1 excess matches Theo's `abnb_earnings_reactions.csv` to within ±2.5 pts (mean absolute difference 0.6 pt; the residual is a QQQ dividend-adjustment convention). Our 20-session-from-release excess matches to within ±3.0 pts. The note's headline "mean 20-day excess −4.7%" is a 22-print figure that pre-dates Q2'26 completing. With Q2'26 in (+22.5%), the same measure is **−3.6% over 23 prints**; excluding Q2'26 it is −4.8%, i.e. the old number was right for its sample.

---

## 5. Seasonality (`09_seasonality.csv`, `09_monthly_returns.csv`, figure `09_seasonality.png`)

Calendar-month total returns since Jan 2021 (n = 5 or 6 per month).

| Month | ABNB mean | Excess vs QQQ | p | Excess vs BKNG/EXPE avg | p | Sign consistency (excess vs QQQ) |
|---|---|---|---|---|---|---|
| Jan | +8.1% | +6.9% | 0.23 | +7.5% | 0.26 | 4/6 |
| **Feb** | +6.9% | **+7.7%** | **0.005** | +5.0% | 0.38 | **6/6** |
| Mar | −1.7% | −2.5% | 0.45 | −1.6% | 0.66 | 2/6 |
| Apr | −2.2% | −3.2% | 0.26 | −1.8% | 0.53 | 3/6 |
| **May** | −9.3% | **−14.5%** | **0.0016** | **−6.4%** | **0.045** | **0/6** |
| Jun | +2.4% | −0.4% | 0.93 | +2.2% | 0.51 | 3/6 |
| Jul | +5.9% | +3.7% | 0.44 | +0.7% | 0.85 | 3/6 |
| Aug | −0.1% | −0.7% | 0.89 | −2.4% | 0.70 | 3/6 |
| Sep | +1.0% | +3.1% | 0.44 | +1.7% | 0.37 | 4/6 |
| Oct | +0.1% | −2.7% | 0.44 | −1.2% | 0.59 | 1/5 |
| **Nov** | −0.6% | **−5.1%** | **0.027** | −11.4% | 0.09 | **0/5** |
| Dec | +0.1% | +0.6% | 0.90 | −4.6% | 0.28 | 2/5 |

The individual Mays: −17.5%, −19.5%, −16.2%, −14.8%, −3.4%, −15.6% (2021→2026). The individual Novembers: −0.9%, −10.0%, −4.0%, −4.4%, −6.0%. Calendar Q2 excess is −6.0% (n = 18 months, p = 0.02); Q4 excess vs the OTAs is −5.7% (p = 0.03). May-to-October vs November-to-April shows nothing (−1.9% vs +0.9%, both p > 0.3), so this is not a "sell in May" artefact of the market — it is ABNB-specific.

Mechanically, February holds the Q4 print (which has been the good one: +13.3, +3.6, +13.4, −1.7, +14.4, +4.6) and May holds the Q1 print (mean day-1 excess −3.0%). But the print day is only a fifth of May's −14.5%; the rest is a whole-month bleed. The honest reading: **the seasonal is the summer-booking-season expectations cycle, in which ABNB is bid into the February FY guide and sold through the spring when the Q1 print resets the nights trajectory.** With n = 6 and 54 seasonality tests run, this is a base rate to put on the calendar, not a proven effect.

---

## 6. Non-earnings events (`09_event_study_events.csv`, `09_event_study_summary.csv`)

Market model: ABNB on QQQ, estimated over sessions −140 to −21, abnormal returns cumulated over [0,0], [0,1], [0,5], [0,20], [−1,+1] and [−5,−1]. Events falling inside a ±2-day window around ABNB's own print are reported both with and without exclusion.

**Peer prints** (dates from `predictive/02_peer_prints.csv`, ABNB print weeks excluded):

| Peer | n | CAR[0,0] | t | CAR[0,1] | t | CAR[0,5] | t |
|---|---|---|---|---|---|---|---|
| BKNG | 13 | −0.60% | −1.28 | −0.51% | −0.73 | −2.90% | −1.47 |
| EXPE | 8 | −0.55% | −0.62 | +1.55% | 2.54 | +3.44% | 0.84 |
| MAR | 11 | −0.82% | −2.67 | −0.77% | −1.09 | +1.96% | 0.70 |
| HLT | 17 | +0.44% | 1.21 | +0.31% | 0.48 | −0.07% | −0.04 |

Two nominal hits (EXPE [0,1], MAR [0,0]) out of 24 peer tests, both marginal on n = 8–11, and the signs contradict a single read-through story. **There is no tradeable peer read-across into ABNB.** This is consistent with the major-moves note ("Booking's own prints never moved ABNB 7%") and with predictive study 02.

**Macro prints** (BLS release dates 2021–26, 60 CPI and 60 jobs releases in the sample):

| Event | n | CAR[0,0] | t | p | CAR[0,1] | t | p |
|---|---|---|---|---|---|---|---|
| CPI release | 60 | −0.17% | −0.50 | 0.62 | −0.23% | −0.41 | 0.68 |
| Jobs report | 60 | **+1.04%** | 2.47 | **0.016** | +1.28% | 2.33 | 0.023 |

CPI days do nothing beyond ABNB's ordinary QQQ beta. Payroll days show a genuine positive abnormal return — ABNB reacts more than its QQQ beta implies to labour-market news, which is what you would expect of a discretionary-travel name whose demand is employment-linked. It is one hit in a large multiple-comparison exercise but the sign is economically sensible; log it and re-check on the next 12 payroll days rather than trading it.

**Analyst actions** (`09_analyst_actions.csv`, same-day session assumed):

| Group | n | CAR[0,0] | t | p |
|---|---|---|---|---|
| PT raise, all | 206 | +2.94% | 5.98 | 9e-09 |
| PT raise, ex-print week | 91 | −0.20% | −1.15 | 0.25 |
| PT cut, all | 141 | −3.78% | −8.80 | 5e-15 |
| PT cut, ex-print week | 53 | −0.32% | −1.08 | 0.29 |
| Upgrade, all | 23 | +2.64% | 2.38 | 0.026 |
| Upgrade, ex-print week | 17 | +0.55% | 1.34 | 0.20 |
| Downgrade, all | 19 | −1.53% | −2.91 | 0.009 |
| Downgrade, ex-print week | 16 | −1.16% | −2.39 | 0.031 |
| Initiation | 14 | −0.01% | −0.03 | 0.98 |

115 of 206 price-target raises and 88 of 141 cuts land in a print week. Once those are removed, everything collapses to zero except a small residual downgrade effect (−1.2%, n = 16). **Sell-side revisions are a print echo.** A stand-alone downgrade is worth about a percent; a stand-alone upgrade or initiation is worth nothing.

**Named single events** (per-event abnormal returns; the estimation-window daily σ is 1.5–2.8%, so |CAR| under ~4% on the day is inside noise):

| Date | Event | CAR[0,0] | t | CAR[0,5] | CAR[0,20] |
|---|---|---|---|---|---|
| 2023-09-01 | S&P 500 inclusion announced (after close Fri) | +0.97% | 0.37 | +11.79% | +8.68% |
| 2023-09-05 | First session after the announcement / NYC LL18 platform enforcement begins | **+7.05%** | **2.71** | +12.01% | +2.62% |
| 2023-09-18 | Index inclusion effective | −0.12% | −0.05 | −2.25% | −9.72% |
| 2024-06-21 | Barcelona announces 2028 licence phase-out | +1.42% | 0.79 | +2.89% | +1.37% |
| 2025-05-13 | 2025 Summer Release (Services + Experiences) | +1.25% | 0.54 | −3.86% | −1.26% |
| 2025-05-19 | Spanish consumer ministry removal order | −1.09% | −0.47 | −6.13% | −4.17% |
| 2025-12-01 | €64.1m Spanish fine (month only) | +2.04% | 1.32 | +4.71% | +19.74% |
| 2026-05-19 | Spanish registry partially annulled | −1.82% | −1.04 | −5.00% | +1.25% |
| 2026-05-20 | EU STR data regulation applies / 2026 Summer Release | +1.71% | 0.97 | −2.37% | +1.51% |
| 2026-09-04 | Reuters: draft EU rules would curb Airbnb | — | — | — | — |
| 2026-02-03 | AI-disintermediation scare | **−6.15%** | **−3.93** | −6.86% | +6.39% |
| 2025-04-03 | Liberation Day tariffs | −2.78% | −1.25 | −2.11% | −2.39% |
| 2025-04-09 | 90-day tariff pause | +4.15% | 1.84 | +0.41% | +1.97% |

- **Index inclusion is a pre-effective-date event, and it is worth about 7%.** The +7.05% came on the first session after the Friday-evening announcement; the effective date itself was a non-event (−0.1%) and the 20 sessions after it gave back −9.7%. Classic index-demand front-run and unwind.
- **NYC Local Law 18 enforcement began the same session as the S&P pop.** The two are inseparable in the data. Given that the day was strongly *positive*, the strongest statement available is that the market did not price LL18 at all — consistent with Airbnb's disclosure that NYC was ~1% of global revenue.
- **No European regulatory event has ever moved this stock.** Barcelona's 2028 phase-out, Spain's removal order, Spain's €64.1m fine, the Spanish registry annulment and the EU data regulation all sit inside a 2σ band on the day, and the [0,5] windows have no consistent sign. This is a direct, dated counterweight to the regulatory-risk bear case and it agrees with the probability-weighted profile in `2026-09-05_regulatory-forecast-profile.md`: expected 2027 revenue loss ~1–2%, i.e. below the noise floor of a daily event study.
- **Buyback announcements cannot be measured.** All four authorisations ($2.0bn 2 Aug 2022, $2.5bn 9 May 2023, $6.0bn 13 Feb 2024, $6.0bn 6 Aug 2025 — sourced from the 2Q22, 1Q23, 4Q23 and 2Q25 shareholder letters) were announced inside the shareholder letter, on the print. Airbnb has never made an off-cycle capital-return announcement. There is no clean buyback event in this stock.
- **Product launches are not catalysts.** Both Summer Releases (13 May 2025, 20 May 2026) are inside noise on the day and negative over the following week. The market waits for the launch to show up in nights and margin, which is exactly what the Q2'25 reaction (−8.0% on the $200m spend) said.

---

## 7. Implied vs realised move (`09_implied_vs_realised.csv`, `09_implied_move_live.json`)

There is no historical option-chain source in the repo or free on the web, so the per-print implied move for the 22 past prints does not exist and I did not fabricate one. What can be measured:

**Realised day-1 moves, all 23 prints.** Mean absolute move **7.07%**, median **6.87%**, last eight prints mean 6.91%. Ten of 23 were ≥8%; five were ≤1.1%. The distribution is bimodal — big or nothing.

| | |
|---|---|
| Largest up | +17.4% (Q2'26), +14.5% (Q4'24), +13.3% (Q4'20), +13.4% (Q4'22), +13.0% (Q3'21) |
| Largest down | −13.4% (Q2'24), −13.4% (Q3'22), −10.9% (Q1'23), −8.7% (Q3'24), −8.0% (Q2'25) |
| Smallest | +0.29% (Q3'25), +0.50% (Q2'23), +0.73% (Q1'26), +1.01% (Q1'25) |

**The size of the move is unforecastable from its own history.** A naive "implied = mean absolute move of the prior four prints" has MAE 5.66 pts against a mean realised move of 7.07 pts — i.e. worse than useless. Scaled against trailing 60-day daily vol, the day-1 move has ranged from 0.18σ to 8.7σ.

**The live term structure prices no event premium yet.** From `abnb_options_ledger.csv` (5 Sep 2026): the Nov-20 straddle is 13.38% of spot at 76 dte and the Dec-18 straddle 15.65% at 104 dte; √time scaling of the near straddle gives 15.652% for the far one against an actual 15.65%, so the implied event premium is **0.002 pts**. From a live yfinance chain (6 Sep 2026): ATM IV 37.81% for the 23 Oct expiry (pre-print) and 38.14% for the 20 Nov expiry (post-print). Treating 23 Oct as clean vol gives an implied earnings jump σ of only 2.3%; attributing all the incremental total variance to the jump gives 10.7% (expected absolute move 8.5%). The two estimators bracket the truth, and the fact that they bracket so widely is the finding: **60 days out, the earnings jump is not yet in the term structure.** Re-run the script in the last week of October, when the 6 Nov weekly is listed and the kink becomes measurable, and compare the implied number to the 7.1% historical mean.

---

## 8. Simple rules backtest (`09_rules_backtest.csv`, `09_rules_trades.csv`, figure `09_rules_backtest.png`)

All returns are excess vs QQQ, after a 10bp round-trip cost. LOYO = leave-one-year-out refits.

| Rule | h | n | Hit rate | Mean excess | t | p | LOYO range | Sign stable |
|---|---|---|---|---|---|---|---|---|
| B0 always long ABNB vs QQQ (monthly) | 21 | 57 | 46% | −0.53% | −0.43 | 0.67 | — | — |
| R1 buy day-1 close after a **down** print | 20 | 12 | 42% | −0.59% | −0.33 | 0.75 | −1.2 to −0.1 | yes |
| R1 buy day-1 close after a down print | 60 | 12 | 50% | +1.07% | 0.42 | 0.68 | −0.6 to +2.7 | no |
| **R2 short day-1 close after an up print** | 20 | 11 | 64% | **+5.89%** | 2.34 | **0.042** | +3.9 to +8.2 | **yes** |
| **R2 short after an up print** | 60 | 10 | 80% | **+12.82%** | 2.30 | **0.047** | +10.5 to +15.0 | **yes** |
| R2b buy after an up print | 20 | 11 | 36% | −6.09% | −2.42 | 0.036 | −8.4 to −4.1 | yes |
| R3 buy −20d, sell at the release close | 20 | 23 | 52% | +1.03% | 0.59 | 0.56 | −0.2 to +2.3 | no |
| R4 buy a −7% non-earnings day | 5 | 9 | 67% | +1.54% | 1.40 | 0.20 | −1.2 to +2.2 | no |
| R4 buy a −7% non-earnings day | 20 | 9 | 56% | +3.30% | 0.93 | 0.38 | +2.2 to +4.5 | yes |
| R4 buy a −7% non-earnings day | 60 | 9 | 56% | +2.53% | 0.65 | 0.54 | +1.1 to +6.0 | yes |
| R5 buy after 3 consecutive down days | 5 | 146 | 47% | +0.69% | 1.59 | 0.11 | +0.2 to +1.2 | yes |
| R5 buy after 3 down days | 20 | 146 | 57% | +1.99% | 2.26 | 0.025 | +1.1 to +3.0 | yes |
| R6 12-1 momentum, long when relative 12-1 > 0 | 21 | 4 | 50% | −1.55% | −0.27 | 0.81 | — | no |
| R6c 12-1 momentum, long when absolute 12-1 > 0 | 21 | 27 | 48% | −0.91% | −0.51 | 0.61 | −2.3 to −0.3 | yes |
| **R7 short ABNB vs QQQ through May** | 21 | 6 | **100%** | **+14.38%** | 6.19 | **0.002** | +13.4 to +16.6 | **yes** |
| R7b long ABNB vs QQQ through February | 21 | 6 | 100% | +7.57% | 4.78 | 0.005 | +6.6 to +8.5 | yes |
| R7c short ABNB vs QQQ through November | 21 | 5 | 100% | +4.95% | 3.33 | 0.029 | +3.7 to +6.0 | yes |

**Survivors.**
- **R2, "short the pop", is the only earnings-based rule with a stable sign and a t-stat above 2 at both horizons.** But look at the trades (`09_rules_trades.csv`): it made +16.1, +7.1, +12.2, +17.6, +11.6, +11.0 and +1.4 points on the 2021, 2022, 2023 and 2025 pops and **lost** on the last two (−6.1% on Q4'25, −2.8% on Q2'26); the other two losses were the small 2021 pops. Five of the seven winners are pre-2024, and the two biggest are 2021-02 and 2022-05. This is a de-rating-era rule, not a current one.
- **R7, the May short, is the strongest number in the note** (6/6, t = 6.2, p = 0.002, LOYO range +13.4% to +16.6%) and is also the most obviously data-mined, because it was constructed after reading the seasonality table. It is the same fact as §5, not independent evidence.

**Non-survivors.** Buying after a down print earns nothing at either horizon (R1) — drops do not bounce. Buying the run-up earns nothing (R3). Buying a −7% non-earnings day is directionally right but never significant on n = 9 (R4). The 3-down-day reversal at 20 sessions (R5, +2.0%, p = 0.025) is on 146 heavily overlapping windows, so its t-stat is badly inflated; at 5 and 10 sessions it is nothing. **Every momentum variant loses money** — consistent with the −0.5 loading on the FF momentum factor. And the buy-and-hold benchmark itself is −0.53% per month vs QQQ, so any rule with a mean below that is worse than doing nothing.

---

## 9. Positioning (`09_positioning_short_interest.csv`, `09_positioning_ratings.csv`, `09_positioning_tests.csv`, `09_institutional_snapshot.csv`, figure `09_positioning.png`)

**Short interest.** 84 semi-monthly settlements, Feb 2023 to 14 Aug 2026, converted to % of shares outstanding using basic weighted-average shares from `abnb_capital_return_quarterly.csv`. Mean 2.84%, range 1.74–5.44%. The latest four readings are 2.52%, 2.36%, 2.18%, 2.17% — a steady covering through the summer 2026 rally, and near the low end of the range. Tested against forward excess returns from the FINRA publication date (settlement + 9 days), the level gives r = +0.06 (1m) and +0.15 (3m); the change gives −0.08 and +0.04. **Nothing.** There is no short squeeze left to harvest and no crowded-short signal.

**Sell-side rating distribution.** Built as a running most-recent-rating-per-firm panel from 466 actions. At 4 Sep 2026: 49 covering firms, **49% Buy, 43% Hold, 8% Sell** — the highest Buy share since 2023 (trough 26.7% in 2024). The mean live price target (32 targets set in the last 400 days) is **$179.88 against a $181.94 spot, a −1.1% premium**: the stock has run past the Street.

| Signal | Sample | n | r | p |
|---|---|---|---|---|
| Buy share vs forward 3m excess | monthly, overlapping | 66 | +0.13 | 0.30 |
| 3-month change in Buy share vs forward 1m | monthly | 65 | −0.24 | 0.05 |
| PT premium vs forward 3m excess | monthly, overlapping | 66 | +0.44 | 0.0002 |
| PT premium vs forward 3m excess | **non-overlapping quarterly** | 22 | +0.51 | 0.015 |
| PT premium controlling for trailing 3m excess | quarterly | 21 | +0.55 | 0.010 |
| Trailing 3m excess vs forward 3m excess | quarterly | 21 | **−0.71** | 0.0003 |
| PT premium vs forward 3m excess | **quarterly, from 2023** | 13 | +0.23 | 0.46 |
| Trailing 3m excess vs forward 3m excess | quarterly, from 2023 | 13 | −0.42 | 0.15 |

The price-target premium looks powerful and it is really just quarterly mean reversion in disguise — trailing 3-month excess return predicts the next quarter with r = −0.71 over 2021–26. Both effects halve and lose significance in the 2023-onward half of the sample, which is the half that contains no 2021–22 boom-bust. **Do not put a "targets say upside" or "targets say downside" line on the card.** The honest reading is directional colour only: with the mean target now below spot and Buy share at a five-year high, the sell side has no headroom left to upgrade into the 5 Nov print.

**13F concentration.** Only a single free public snapshot exists (fintel.io, filings as of 30 Jun 2026): 2,210 institutions, 468.9m shares reported long, top-5 holders 22.4% and top-10 33.2% of disclosed shares, 1,020 buyers vs 884 sellers. **The concentration-versus-forward-returns test could not be run** — building the quarterly history needs a parse of ABNB positions out of thousands of EDGAR 13F-HR information tables, which is a half-day job and is listed under "what to build next". Do not cite a 13F trend we have not measured.

---

## 10. Corrections to existing work

1. `research/notes/2026-09-05_abnb-major-moves.md` §2b: "Mean 20-session excess across 22 prints is −4.7%". Correct for its sample. With Q2'26's window now complete (+22.5% excess), the same measure across 23 prints is **−3.6%** (median −3.5%, negative in 15 of 23). Excluding Q2'26 our figure is −4.8%, so the two are consistent. Worth updating the number the pitch quotes.
2. Same note, §4.3: "Macro sensitivity has fallen. Beta to rates is no longer the main risk." The direction is right, but the daily rates beta was **never** statistically different from zero in any year, including 2022 (β = +0.006 per bp, t = 0.35). The 2022 repricing runs through the QQQ beta (1.28) and the multiple, not through a direct rates loading. Phrase it as "ABNB never had a rates beta; it had a long-duration-growth beta, and that has fallen from 1.28 to 0.91."
3. `abnb_earnings_reactions.csv` has no 20-session row for 2026Q2. It is now computable: **+22.5%** excess vs QQQ from the release close (day-1 +16.8%, drift +1..+20 of +3.2%). Recorded in `09_earnings_drift_by_print.csv` and `09_reconciliation_vs_existing.csv`.
4. `data/processed/abnb_options_ledger.csv` exists only in the main tree (`C:\Users\krish\citadel-abnb`), not in the overnight tree. Its `event_implied_move_pct` field is 0.0 for ABNB's Nov-20 expiry, which reads as a failed calculation rather than a real zero — although as §7 shows, the correct answer at 76 dte does happen to be approximately zero.

---

## 11. For the 5 Nov card

- **Base rate for the day.** Mean absolute day-1 move **7.1%**, median **6.9%**; 10 of 23 prints moved ≥8%, 5 of 23 moved ≤1.1%. Day-1 excess vs QQQ is positive 11 of 23 with mean +0.6% — the print is a coin flip in direction and a big number in size.
- **Options are not yet pricing the event.** As of 5 Sep the Nov/Dec straddle term structure is pure √time (implied event premium 0.00 pts). Re-run `09_stock_behaviour.py` in the last week of October: if the implied move comes in below ~7% the straddle is cheap against the base rate, above ~9% it is rich. This is the cheapest concrete trade-structure input we have.
- **If it pops, history says fade it — but the fade has stopped working.** Up-prints drifted −7.1% over the following 20 sessions and −14.8% over 60 (n = 11 / 10). The last three up-prints did not fade. Frame it as "the burden of proof is on why this time sustains", not as a short.
- **If it drops, do not buy the dip on drift grounds.** Down-prints drift −0.7% / +0.4% — zero. There is no post-drop bounce in this stock at any horizon tested.
- **November is the worst month in the sample:** ABNB has underperformed QQQ in every November since 2021, by −5.1% on average. The Q3 print sits inside that window. Whatever the pitch's direction, the November calendar is a headwind for a long entered on the print.
- **Positioning gives no cushion.** Short interest 2.17% of shares, near a three-year low — no squeeze fuel. 49% Buy is the highest since 2023 and the mean price target ($179.88) is already below spot ($181.94): the sell side is out of room to upgrade.
- **Ignore the peripheral catalysts.** The EU Affordable Housing Act presentation (9 Sep 2026) sits in a class of events — Barcelona 2028, Spain's removal order and fine, the EU data regulation — none of which has ever produced a statistically distinguishable move. Same for buyback announcements (never off-cycle), the Summer Release, and analyst upgrades outside a print week.

---

## 12. For the model

| Parameter | Value | Unit | Source |
|---|---|---|---|
| Beta to SPY, 2-year daily | **1.22** | — | `09_factor_model_by_period.csv` / daily regression 2024-09 to 2026-09 |
| Beta to SPY, 3-year daily | 1.29 | — | same |
| Beta to SPY, 2026 YTD | 1.16 | — | `09_factor_model_by_period.csv`, row `2026` |
| Fama-French market beta (mkt_rf), from 2023 | 1.32 | — | `09_ff_factor_model.csv` |
| **Recommended cost of equity** | **10.5–11.5%** | % | Rf 4.78% (^TNX, 4 Sep 2026) + β 1.2–1.3 × ERP 4.5–5.5% |
| Beta to QQQ, latest rolling 126d | 0.86 | — | `09_factor_betas_rolling.csv`, last row |
| Beta to hotels (MAR/HLT/H), 2026 | 0.45 | — | `09_factor_model_by_period.csv` |
| Beta to OTAs (BKNG/EXPE), 2026 | 0.54 | — | same |
| Beta to 10-year yield | **0.0** (t ≤ 0.9 in every year) | % per bp | same — do not model a rates beta |
| FF momentum loading, from 2023 | −0.53 (t = −7.7) | — | `09_ff_factor_model.csv` |
| Annualised total volatility, 2026 | 39.1% | % | `09_factor_model_by_period.csv` |
| Annualised idiosyncratic volatility, 2026 | 31.2% | % | same — use this for option-based sizing, not total vol |
| Idiosyncratic share of daily variance, 2026 | 64% | % | same |
| Mean absolute day-1 earnings move | 7.07% (median 6.87%) | % | `09_implied_vs_realised.csv`, n = 23 |
| Mean 20-session post-print excess drift | −3.7% (t = −2.16) | % | `09_earnings_drift_stats.csv`, n = 23 |
| Short interest, latest | 2.17% of shares out (12.86m shares, 14 Aug 2026) | % | `09_positioning_short_interest.csv` |
| Sell-side mix, 4 Sep 2026 | 49% Buy / 43% Hold / 8% Sell, 49 firms | — | `09_positioning_ratings.csv` |
| Mean live price target, 4 Sep 2026 | $179.88 (32 targets), −1.1% vs spot | USD | same |
| Top-10 13F concentration, 30 Jun 2026 | 33.2% of disclosed shares | % | `09_institutional_snapshot.csv` (fintel.io) |

**Multiple regime.** The factor attribution says the 2026 re-rating is not a market or sector move: QQQ contributed +14.2 pts of the +34.0 pt return, consumer discretionary contributed −12.9, and +32.7 pts is stock-specific alpha. A valuation model that assumes the multiple mean-reverts with the sector will be wrong for the same reason it was wrong in 2026 — the multiple is being set by the nights/RNPL/Services narrative, not by the tape. Pair this with `2026-09-05_driver-model.md`'s reverse DCF: the implied-growth question is the whole debate, and beta contributes almost nothing to it.

---

## 13. What to build next

1. **Re-run the options block in late October** once the 6 Nov weekly is listed. That converts §7 from "not measurable yet" into an actual implied-vs-base-rate comparison and gives the card a trade structure.
2. **Build the 13F concentration history from EDGAR** (13F-HR information tables, filter to ABNB CUSIP 009066101, quarterly since 4Q20). That is the one test in this workstream that could not be run.
3. **Intraday decomposition of the print reaction.** Everything here is close-to-close, so the after-hours move and the next-day open-to-close are conflated. The major-moves note repeatedly cites "−5% AH, flat on the day" cases (Q2'21, Q1'25, Q1'26); separating them would sharpen the reaction function in `predictive/04`.
4. **Test the May seasonal out of sample on peers.** If BKNG and EXPE show the same May pattern in a longer history, ABNB's version is an industry expectations cycle and can be modelled; if not, six observations is all we will ever have.
5. **Track the jobs-day abnormal return forward.** +1.04% per payroll release (t = 2.47, n = 60) is economically sensible for a discretionary-travel name and is worth a pre-registered check on the next 12 releases rather than a retro-fitted claim.
