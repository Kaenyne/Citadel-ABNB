# 08. Alt data and a high-frequency demand index: point-in-time features, walk-forward backtests, composite indexes

**Date:** 2026-09-06. Author: Krishang Surapaneni (compiled with Claude Code), overnight workstream 08.
**Question:** Build point-in-time alt-data features (Google Trends, the XBRL bookings backlog, Eurostat platform nights, Inside Airbnb demand proxies), combine them into Demand / Supply / Price composites, and test walk-forward whether any of it forecasts ABNB nights, GBV, ADR or revenue better than a naive baseline. Then nowcast 3Q26 and compare with the guide.

**Scripts.** `analysis/src/overnight/08_trends_pull.py` (Google Trends via pytrends), `08_inside_airbnb_demand.py` (168 listing dumps, 13 cities), `08_altdata_backtests.py` (panel, 598 feature tests, 42 index backtests, composites, nowcast, figure). All run with `py -3.13`; the last one rebuilds every CSV below from the raw inputs in one pass.

**Outputs.** `data/processed/overnight/`: `08_trends_weekly.csv`, `08_trends_quarterly_features.csv`, `08_panel_quarterly.csv` (the aligned quarterly panel, 85 features), `08_feature_tests_all.csv` (every test), `08_trends_tests.csv`, `08_backlog_tests.csv`, `08_eurostat_tests.csv`, `08_ia_tests.csv`, `08_test_scoreboard.csv` (tests run / flagged / beat-naive by family), `08_demand_index_quarterly.csv`, `08_demand_index_p22_quarterly.csv`, `08_supply_index_quarterly.csv`, `08_price_index_quarterly.csv`, `08_index_backtests.csv`, `08_survivor_robustness.csv`, `08_survivor_wf_path.csv`, `08_ia_dump_metrics.csv`, `08_ia_city_yoy.csv`, `08_q3_2026_nowcast.csv`, `08_q3_2026_components.csv`, `08_q3_2026_guide_reconciliation.csv`. Figure `analysis/figures/overnight/08_indexes_vs_kpis.png`.

**Sources.** ABNB KPIs and y/y: `data/processed/abnb_driver_history_quarterly.csv` (shareholder letters). ADR ex-FX and the FX effect: `data/processed/predictive/03_quarterly_panel.csv` (letters, 2Q22-2Q26). Backlog: `data/processed/abnb_backlog_indicators.csv` (SEC XBRL `ContractWithCustomerLiabilityCurrent`, `FundsHeldForClients`). Eurostat `tour_ce_omr` platform nights: `data/processed/eurostat_platform_nights_monthly.csv` and workstream 10's fresh API pull `data/processed/overnight/10_eurostat_platform_monthly_latest.csv` (the script uses whichever runs further). Peers: `data/processed/predictive/02_peer_prints.csv` (MAR/HLT RevPAR, BKNG/EXPE room nights). Macro: FRED keyless CSVs pulled 6 Sep 2026 (DTWEXBGS, DEXUSEU, ICSA, AIRRPMTSID11, CUSR0000SEHB) into the scratch dir, plus `data/raw/bea/bea_pce_travel_monthly_2015_2026.csv`. Inside Airbnb: `data/raw/inside_airbnb/*_listings.parquet`, 168 dumps, 13 cities, Dec 2022 to Aug 2026 (CC-BY 4.0). Common Crawl: `data/processed/cc_listing_survival.csv`. Guide: `data/processed/abnb_revenue_guidance_vs_actual.csv`. Google Trends: pulled 6 Sep 2026, 9 terms, US and worldwide, 2019-01-06 to 2026-09-06.

**Read first.** `research/notes/predictive/03_macro-altdata-nowcast.md` (890 macro pairs; the headline that most level correlations post-2022 are the 2023 normalisation trend) and `research/notes/2026-09-05_eu-platform-and-backlog.md` (which already found the funds-held relationship in-sample and flagged the RNPL break in unearned fees). This note does not re-report those; it tests them out-of-sample and adds Trends and a fixed-city Inside Airbnb panel.

---

## 1. Bottom line

1. **No composite index beats a naive baseline. Not one of the three.** Walk-forward from 2024Q1 with an expanding fit (n = 10 quarters), RMSE relative to "same as last quarter": Demand index 1.66 on nights, 1.28 on GBV, 1.28 on revenue; Supply index 1.19 on nights, 1.44 on ADR; Price index 1.09 on ADR, 1.40 on ADR ex-FX. Ratios above 1 mean worse than doing nothing. Non-negative-least-squares weights refit each quarter do not rescue them (1.40 / 1.35 / 1.39 on nights / GBV / revenue). The composite that comes closest is a demand index whose z-baseline starts in 2023Q1 rather than 2021Q1 (0.78 on nights, 0.81 on revenue) but that is n = 7 walk-forward quarters and its correlation with nights over 2024Q1+ is only +0.25, so I do not believe it.

2. **Two things beat naive, and one of them is new.** Out of 468 evaluable walk-forward pairs, 29 beat naive at all and 7 beat it by 20% or more. Six of those seven are the mechanical FX pair and macro/peer series already tested in note 03 (dollar → ADR, hotel RevPAR → nights, BEA hotels → nights, CPI lodging → nights). **The one genuinely new survivor is funds held for clients, y/y at the prior quarter end, against next-quarter revenue growth**: r +0.89 on 2023Q1-2026Q2 (n = 14, Spearman +0.85, permutation p 0.000), LOO RMSE 2.14 pp against 4.42 for the LOO mean, walk-forward RMSE 2.57 pp against 4.29 naive (**ratio 0.60**) and 4.37 AR(1) (0.59), direction right in 8 of 10 quarters. Jackknifing one walk-forward quarter at a time moves the ratio only between 0.55 and 0.66. It is knowable: the balance sheet lands with the 10-Q, a day or two after the prior print, roughly seven weeks before the next one.

3. **Google Trends is the biggest negative in this note.** 432 tests (216 pairs on two windows). On the full 2022Q1-2026Q2 window, **zero** of 162 evaluable pairs beat naive walk-forward; on the post-2022 window, 7 of 162 do and none by more than 17%. Sixty-five pairs are "flagged" on the full window by |r| > 0.5 and permutation p < 0.05, which is what a decelerating search index looks like next to a decelerating KPI. The cleanest illustration: worldwide "airbnb" y/y has r = +0.87 with nights y/y (n = 18) and a walk-forward RMSE **3.9x** naive. Search does not forecast the print.

4. **Eurostat platform nights are a category check, not a nowcast.** 64 tests; the best any Eurostat feature does walk-forward is 0.93 vs naive, and that is on the lag-0 quarter, which is not published before the print. The knowable lag-1 feature is 1.09 on nights and 1.19 on GBV. The series also stops at March 2026 (confirmed by a fresh API pull today), a five-month lag, so **there is no July-August 2026 data and 2026Q2 will probably still be incomplete on 5 November.** The point-in-time reading available for the Q3 print is 2026Q1 EU27 platform nights +9.7% y/y.

5. **Inside Airbnb demand proxies do not yet have a test.** 36 tests, **zero** flagged, and the four that beat naive do so by 4-19% on n = 7 walk-forward quarters with r between +0.12 and +0.41. The reason is composition, not the metric: the cross-city median runs on 1 city in 2023Q4-2024Q4, 2-5 cities through 2026Q1, 9 in 2026Q2 and only 13 in 2026Q3, so the fixed-13-city series has **n = 0** usable quarters. `reviews_l30d` on year-ago-matched listings is the most promising (sign right 6 of 7, ratio 0.81) and is the one to capture monthly from now.

6. **The 3Q26 nowcast sits below the guide, and the gap is the RNPL confound, not a call.** Funds held (+10.5% y/y at 2Q26 end) fits 3Q26 revenue growth of **+12.0%** (±2.0 pp) against a guide of $4,690-4,770m, i.e. +14.5% to +16.5% on 3Q25's $4,095m. But the same model under-predicted 1Q26 by 3.4 pp and 2Q26 by 2.8 pp, in the two quarters where Reserve Now Pay Later depressed the funds-held line; add that back and it lands on the guide. The mechanical assembly (nights + ADR) says the same: nights 10.3-11.0%, ADR +4.05% (ex-FX run-rate 3.25 + FX +0.80), GBV +14.8 to +15.5%, and revenue anywhere from +10.6% to +15.5% depending only on the revenue-minus-GBV gap, which was -4.2 pp in 3Q25 and +0.8 pp in 2Q26. **My honest position: nothing in this workstream contradicts the guide, and the single number I would put on a slide is the FX contribution to ADR, +0.8 pp.**

---

## 2. Method

Everything is quarterly. Monthly and weekly inputs are averaged (or summed, for Eurostat nights) by calendar quarter and expressed as y/y %, with a first difference added for the main features. Each feature is labelled with when it becomes knowable, and features that are not knowable before the print are tested but flagged (`available_before_print` in every test CSV).

Two windows are reported for every pair: **2022Q1-2026Q2** (n ≤ 18, walk-forward from 2023Q1) and **2023Q1-2026Q2** (n ≤ 14, walk-forward from 2024Q1). The second is the one to read, for the reason note 03 gives: 2022 still carries reopening base effects, and everything correlates with everything in a common deceleration.

Per pair: Pearson r and p, Spearman, a 1,000-shuffle permutation p, leave-one-out OLS RMSE against the LOO mean, and then the thing that actually matters — an **expanding-window walk-forward**. At each quarter t the model is refit on data strictly before t, predicts t, and is scored against three baselines refit the same way: naive last quarter y[t-1], prior year y[t-4], and an AR(1). `wf_ratio_vs_naive` below 1 means the feature helped. Sign accuracy is the share of walk-forward quarters where the predicted change from y[t-1] has the actual sign.

Composites are equal-weighted means of point-in-time expanding z-scores (each component's z at quarter t uses only its own history to t), so no component's scale is set with future data. A second version refits non-negative least-squares weights on the components each quarter. Targets: nights y/y, GBV y/y, revenue y/y, ADR y/y, ADR ex-FX, the ADR FX effect, and the letters' regional nights bands coded to midpoints (low-single 2, mid-single 5, high-single 8, low-double 11 — an approximation, and with n = 7 for North America it is not a real test).

**Test count.** 299 distinct feature→target pairs, each on two windows = **598 feature tests**, plus **42 index backtest rows**. At 5% we would expect roughly 30 false positives on correlation alone, and the features are far from independent (nine Trends terms in eleven transforms across two geographies). This is why the whole note is written off the walk-forward column and not off r.

---

## 3. Scoreboard: what actually beat the naive baseline

From `08_test_scoreboard.csv`. "Flagged" = |r| > 0.5 and permutation p < 0.05. "Beat naive" = walk-forward RMSE ratio < 1 with at least 6 walk-forward quarters.

| Family | Window | Tests | Flagged | Evaluable WF | Beat naive | Beat naive **and** AR(1) | Beat naive by ≥20% | Best ratio |
|---|---|---|---|---|---|---|---|---|
| Google Trends | 2022Q1+ | 216 | 65 | 162 | **0** | 0 | 0 | 1.88 |
| Google Trends | 2023Q1+ | 216 | 32 | 162 | 7 | 7 | 0 | 0.84 |
| Backlog (XBRL) | 2022Q1+ | 21 | 11 | 21 | 1 | 1 | 0 | 0.90 |
| Backlog (XBRL) | 2023Q1+ | 21 | 5 | 21 | 3 | 3 | **1** | **0.60** |
| Eurostat | 2022Q1+ | 32 | 19 | 30 | **0** | 0 | 0 | 1.03 |
| Eurostat | 2023Q1+ | 32 | 9 | 24 | 1 | 1 | 0 | 0.93 |
| Inside Airbnb | 2022Q1+ | 18 | **0** | 12 | 4 | 4 | 0 | 0.81 |
| Inside Airbnb | 2023Q1+ | 18 | **0** | 12 | 4 | 0 | 0 | 0.81 |
| Macro/peer components | 2022Q1+ | 12 | 5 | 12 | 3 | 3 | 1 | 0.69 |
| Macro/peer components | 2023Q1+ | 12 | 5 | 12 | 6 | 6 | 5 | 0.64 |

Totals: 598 tests, 151 flagged, 468 evaluable walk-forward, **29 beat naive, 7 beat it by 20% or more**. Those seven collapse to six distinct pairs, five of which are macro or peer series already in note 03.

### The pairs that survive, with robustness

`08_survivor_robustness.csv` and `08_survivor_wf_path.csv`. "jk" = the range of the walk-forward ratio when any one walk-forward quarter is dropped.

| Feature → target | Knowable when | n (2023Q1+) | r 2023Q1+ | r 2024Q1+ | WF n | WF ratio vs naive | jk range | vs AR(1) | Sign acc | Read |
|---|---|---|---|---|---|---|---|---|---|---|
| Funds held y/y (prior Q end) → revenue y/y | 10-Q, ~7 wks before print | 14 | +0.89 | +0.83 | 10 | **0.60** | 0.55-0.66 | 0.59 | 8/10 | real, and the only new one |
| Fitted FX contribution → ADR FX effect | daily FX, real time | 14 | +0.95 | +0.97 | 10 | **0.44** | 0.39-0.50 | 0.41 | 8/10 | mechanical (note 03) |
| Trade-weighted USD y/y → ADR y/y | daily, real time | 14 | -0.92 | -0.99 | 10 | **0.64** | 0.54-0.75 | 0.51 | 8/10 | mechanical (note 03) |
| Hotel RevPAR y/y (MAR/HLT) → nights y/y | peer prints, ~2 wks before | 14 | +0.88 | **+0.45** | 10 | 0.68 | 0.61-0.79 | 0.64 | 6/10 | 2023-trend; r 0.33 from 2025 |
| BEA hotels nominal y/y → nights y/y | month 3 ~1 wk before print | 14 | +0.88 | **+0.33** | 10 | 0.71 | 0.52-0.93 | 0.68 | 6/10 | 2023-trend (note 03 finding 2) |
| Funds held y/y → GBV y/y | as above | 14 | +0.55 | +0.49 | 10 | 0.97 | 0.86-1.20 | 0.86 | 4/10 | no — revenue only |
| Inside Airbnb reviews_l30d matched y/y → nights y/y | dumps 1-8 wks before | 11 | +0.29 | +0.12 | 7 | 0.81 | 0.71-1.06 | 1.04 | 6/7 | not yet a test (composition) |
| Demand index, z from 2023Q1 → nights y/y | mixed | 11 | +0.37 | +0.25 | 7 | 0.78 | 0.71-0.90 | 0.99 | 6/7 | does not beat AR(1) |

The two macro rows are the diagnostic that makes the point: their correlation with nights **halves** when 2023 is dropped (0.88 → 0.45 and 0.88 → 0.33) while their walk-forward ratio stays under 1, because 2024-26 nights growth is nearly flat and almost any smooth series beats "last quarter" on a flat target. That is the shape of a trend artefact, exactly as note 03 describes, and it is why I am not promoting them.

### The backlog result in detail

`08_backlog_tests.csv`, walk-forward path in `08_survivor_wf_path.csv`.

| Quarter | Funds held y/y at prior Q end | Predicted rev y/y | Actual rev y/y | Error | Naive error |
|---|---|---|---|---|---|
| 2024Q1 | 12.6 | 16.9 | 17.8 | -0.9 | -1.2 |
| 2024Q2 | 13.1 | 13.7 | 10.6 | +3.0 | +7.2 |
| 2024Q3 | 9.8 | 11.4 | 9.9 | +1.5 | +0.8 |
| 2024Q4 | 1.1 | 8.7 | 11.8 | -3.1 | -2.0 |
| 2025Q1 | 5.0 | 5.4 | 6.1 | -0.6 | +5.7 |
| 2025Q2 | 7.0 | 7.8 | 12.7 | -4.9 | -6.6 |
| 2025Q3 | 9.7 | 9.9 | 9.7 | +0.2 | +2.9 |
| 2025Q4 | 17.3 | 11.1 | 12.0 | -0.9 | -2.3 |
| 2026Q1 | 15.0 | 14.5 | 17.9 | **-3.4** | -5.9 |
| 2026Q2 | 10.5 | 13.7 | 16.5 | **-2.8** | +1.3 |

Mechanism: funds held for clients are guest payments collected and held until check-in, so the quarter-end balance is paid-for booked GBV for stays that will be recognised as revenue next quarter. The failure mode is visible in the last two rows and is the same one that already killed unearned fees: Reserve Now Pay Later defers guest payment toward the stay date, so the balance under-states bookings and the model under-predicts. `abnb_backlog_indicators.csv` carries the `rnpl_era` flag and the unearned-fee gap (2.6, 9.7, 13.2 pp over 3Q25-1Q26). **Unearned fees are dead as an indicator**: -0.9% y/y at 2Q26 end against revenue +16.5%, and on the post-2022 window the pair fails walk-forward (1.16 vs naive). This confirms and extends section 3 of `2026-09-05_eu-platform-and-backlog.md`; what is new here is that the funds-held relationship survives a genuine expanding-window walk-forward, which it had not been put through.

---

## 4. Google Trends: what was pulled and why it fails

Weekly interest, 2019-01-06 to 2026-09-06, US and worldwide, stitched across two overlapping windows (Google returns weekly resolution only for windows under about five years; window B is rescaled onto window A by the median overlap ratio, per term). Two comparative payloads anchored on "airbnb" — {airbnb, vrbo, booking.com, hotels.com, expedia} and {airbnb, airbnb near me, hotels near me, vacation rental, hotel} — plus three single-term pulls, because small terms round to 0-1 inside a payload containing "hotel". 20 of 20 requests succeeded. Features: y/y of each term, y/y of the 4-peer sum, Airbnb's share of the 5-term basket in points and y/y points, airbnb-minus-peers and airbnb-minus-hotel spreads, near-me ratios, and first differences of all of them, in both geographies: 44 features, 216 pairs, 432 tests.

Descriptively (from `08_trends_quarterly_features.csv`), the series moves a lot and the KPI does not:

| Quarter | US airbnb y/y | US 4-peer y/y | US airbnb share of basket | share y/y, pts | ABNB nights y/y |
|---|---|---|---|---|---|
| 2024Q2 | -1.8 | -13.8 | 57.5% | +3.2 | 8.7 |
| 2025Q2 | -9.0 | -7.3 | 57.0% | -0.5 | 7.4 |
| 2025Q4 | +1.0 | +16.2 | 52.6% | -3.5 | 9.8 |
| 2026Q1 | +4.2 | +19.4 | 51.8% | -3.4 | 9.2 |
| 2026Q2 | -2.9 | +20.1 | 51.8% | -5.3 | 10.3 |
| 2026Q3 (10 of 13 wks) | -1.5 | +1.2 | 52.8% | -0.7 | ? |

Airbnb's share of the five-term basket fell 5.7 points from 2024Q2 to 2026Q2 while nights growth went **up** from 8.7% to 10.3%. If share-of-search meant anything for this company at this horizon, that could not happen. The share-of-search feature's walk-forward ratio against nights is 1.10 on the post-2022 window.

Three specific cautions for anyone who re-runs this:
- **Google rescales history on every pull.** The 0-100 index is renormalised to the max of the requested window and sampled, so a feature computed today is not the feature an analyst computed in 2024. Nothing here is truly point-in-time and I have not claimed it is.
- **Single-term pulls are noisy at the quarter level.** "vacation rental" US y/y prints +54% (2026Q1), +70% (2026Q2), +9% (2026Q3); "airbnb near me" +42%, +55%, +3%. Those are not demand swings.
- **The regional-band targets are not tests.** North America has n = 7 band observations coded to midpoints; on that target 30-odd Trends features show |r| > 0.8 with permutation p < 0.05. Both series trend, and nothing more should be read into it. They are in `08_trends_tests.csv` for completeness and are excluded from every conclusion above.

---

## 5. Eurostat and Inside Airbnb

**Eurostat `tour_ce_omr`.** EU27 platform nights (Airbnb, Booking, Expedia, TripAdvisor as reported by the platforms). A fresh API pull today reached **March 2026** — a five-month publication lag — so Jul-Aug 2026 do not exist and, extrapolating the lag, 2026Q2 will not be a complete quarter by 5 November. The quarterly EU27 y/y available at the Q3 print is 2026Q1 **+9.7%** (2025Q4 +10.9%, 2025Q3 +9.8%). Against the letters' EMEA nights band (n = 8, bands to midpoints) the lag-1 feature gives 0.94-1.02 vs naive; against global nights y/y, 1.09; against GBV, 1.19; against revenue, 1.17. The only sub-1 result in the family is the lag-0 quarter against revenue (0.93), and lag-0 is published after the print, so it does not count. Italy's nights y/y is the best single country (r +0.61 with global nights, ratio 1.03) which on 32 tests is what you would expect from noise. **Verdict: a category benchmark to sanity-check EMEA growth after the fact — which is how `2026-09-05_eu-platform-and-backlog.md` uses it — and not a nowcast.**

**Inside Airbnb.** 168 dumps, 13 cities, Dec 2022 to Aug 2026; 103 year-ago dump pairs, 69 usable after dropping partial-scope dumps and pairs outside 300-430 days. Per dump: listings, `reviews_ltm`, `reviews_l30d`, blocked share at 30 and 90 days (1 − availability/days, on listings with `has_availability`), entire-home share; then the same on ids matched to the year-ago dump of the same city. `reviews_l30d` and availability are point-in-time on the scrape date, so a year-ago dump is required for a y/y; availability conflates booked, host-blocked and inactive, so blocked share is a proxy and nothing more.

The blocker is composition. The cross-city median rests on 1 city (Rome) for 2023Q4-2024Q4, 2-5 cities to 2026Q1, 9 in 2026Q2 and 13 in 2026Q3. The fixed-13-city variant therefore has **n = 0** quarters with a year-ago comparison, exactly as note 03 predicted. On the chained series, nothing is flagged (0 of 36) and the best walk-forward is `reviews_l30d` matched y/y at 0.81 with r +0.29 on n = 11. Listings y/y is actively harmful (3.63 vs naive) — it is a supply and regulation series (Barcelona, Spain delistings), not demand. Like-for-like price ends 2025Q3 because Inside Airbnb dropped listed prices; r +0.13 with ADR y/y on n = 8.

The current readings, for the record: 13-city median matched `reviews_ltm` +9.0% y/y in 2026Q3 to date (from +7.1% in 2026Q2 on 9 cities), listings -1.9% y/y.

---

## 6. The composites, and why they fail

Definitions (equal-weight point-in-time z-scores, `08_*_index_quarterly.csv`):
- **Demand** = Eurostat platform nights y/y (lag 1), hotel RevPAR y/y (MAR/HLT), air RPM y/y (lag 1), BEA hotels nominal y/y, Inside Airbnb matched `reviews_ltm` y/y, US Trends share-of-search y/y pts, worldwide Trends "airbnb" y/y. 7 components from 2024Q3, 4 in 2026Q3 to date.
- **Supply** = Inside Airbnb listings y/y, Common Crawl survival y/y pts. 2 components.
- **Price** = Inside Airbnb like-for-like price y/y, CPI lodging away from home y/y, BEA hotel price y/y, the fitted FX contribution to ADR. 3 components since 2025Q4 (like-for-like price is dead).

| Index | Target | Method | WF n | WF RMSE | naive | AR(1) | ratio vs naive | ratio vs AR(1) | sign acc |
|---|---|---|---|---|---|---|---|---|---|
| Demand | nights y/y | equal-weight z | 10 | 3.58 | 2.16 | 2.27 | 1.66 | 1.58 | 5/10 |
| Demand | nights y/y | NNLS, expanding | 12 | 3.00 | 2.15 | 3.08 | 1.40 | 0.98 | 7/12 |
| Demand | GBV y/y | equal-weight z | 10 | 4.38 | 3.42 | 3.88 | 1.28 | 1.13 | 5/10 |
| Demand | revenue y/y | equal-weight z | 10 | 5.50 | 4.29 | 4.37 | 1.28 | 1.26 | 7/10 |
| Demand ex Inside Airbnb | nights y/y | equal-weight z | 10 | 3.47 | 2.16 | 2.27 | 1.61 | 1.53 | 4/10 |
| Demand, z from 2023Q1 | nights y/y | equal-weight z | 7 | 1.84 | 2.38 | 1.86 | **0.78** | 0.99 | 6/7 |
| Demand, z from 2023Q1 | revenue y/y | equal-weight z | 7 | 3.49 | 4.31 | 4.34 | **0.81** | 0.80 | 7/7 |
| Supply | nights y/y | equal-weight z | 5 | 1.19 | 1.00 | 1.31 | 1.19 | 0.91 | 3/5 |
| Supply | ADR y/y | equal-weight z | 5 | 4.22 | 2.92 | 3.54 | 1.44 | 1.19 | 2/5 |
| Price | ADR y/y | equal-weight z | 10 | 2.35 | 2.17 | 2.68 | 1.09 | 0.88 | 4/10 |
| Price | ADR ex-FX y/y | equal-weight z | 10 | 1.27 | 0.91 | 1.14 | 1.40 | 1.11 | 3/7 |
| FX contribution alone | ADR FX effect | single | 10 | 0.86 | 1.97 | 2.08 | **0.44** | 0.41 | 8/10 |
| FX contribution alone | ADR y/y | single | 10 | 1.38 | 2.17 | 2.68 | **0.64** | 0.51 | 8/10 |
| Funds held alone | revenue y/y | single | 10 | 2.57 | 4.29 | 4.37 | **0.60** | 0.59 | 8/10 |

**The diagnosis.** Look at the component z-scores in `08_demand_index_quarterly.csv`: from 2024Q3 to 2026Q2 every one of them sits between -0.3 and -1.2, and the index barely moves (-0.29 to -0.59). The expanding mean is anchored on 2021-22 reopening levels, so each component says "still below the 2021 boom" every quarter and the index carries no quarter-to-quarter information. That is the composite version of note 03's finding 2. Restarting the z baseline in 2023Q1 fixes the saturation and is the only composite that beats naive — but it ties AR(1) (0.99), has 7 walk-forward quarters, and its correlation with nights over 2024Q1+ is +0.25. I am recording it, not recommending it.

**The second diagnosis** is that the Price index is beaten by one of its own components. FX alone gets 0.64 against ADR; adding CPI lodging, BEA hotel prices and Inside Airbnb prices makes it 1.09. Dilution, not aggregation. The NNLS version confirms it by putting a weight of 1.57 on the FX component and 0.44 on CPI lodging and zero on everything else.

---

## 7. Negatives, listed

- Google Trends: 432 tests, 0 of 162 evaluable pairs beat naive on the full window, 7 of 162 on the post-2022 window, none by more than 17%, and none survive as a family. Airbnb's share of search fell 5.7 pts over two years while nights growth rose.
- Airbnb "near me" and "vacation rental" single-term pulls swing 40-70 pp y/y between adjacent quarters. Noise.
- Eurostat: 64 tests, best knowable feature 1.09 vs naive on nights. Not a nowcast, and it stops at March 2026.
- Inside Airbnb: 36 tests, 0 flagged, fixed-13-city series has n = 0 usable quarters. Listings y/y is a supply/regulation series and forecasts nights 3.6x worse than naive.
- Unearned fees: was the best backlog indicator pre-RNPL, now -0.9% y/y against +16.5% revenue growth. Walk-forward 1.16 vs naive on the post-2022 window. Dead.
- Funds held → **GBV** does not work (0.97 vs naive, sign 4/10). Only revenue.
- Common Crawl survival: appears in the beat-naive list (0.69 vs nights) on n = 11 with r -0.58 — wrong sign for a demand read (better survival, slower nights) and it is an annual-ish supply-quality series. Discard; note 03 reached the same conclusion by a different route.
- Composite indexes: all three fail. The equal-weight demand index is worse than naive on all three targets under both weighting schemes.
- The regional nights bands (n = 7 for North America, n = 10 for EMEA, coded from qualitative language) are not a usable target and every high correlation against them in the CSVs should be ignored.

---

## 8. 3Q26 nowcast

Point-in-time feature values at 6 Sep 2026 (`08_q3_2026_components.csv`):

| Feature | 2026Q3 value | Knowable since |
|---|---|---|
| Funds held y/y, 2Q26 quarter end | +10.46% | 2Q26 10-Q, early Aug 2026 |
| Unearned fees y/y, 2Q26 quarter end | -0.91% | same |
| Trade-weighted USD y/y, quarter to date | -0.39% | daily |
| EUR/USD y/y, quarter to date | -1.56% | daily |
| Fitted FX contribution to ADR | **+0.80 pp** | daily (fit: FX effect = 0.52 − 0.72 × USD y/y, n = 17, r 0.96) |
| Initial claims y/y | -10.4% | weekly |
| BEA hotels nominal spend y/y (Jul) | +6.14% | monthly, ~5 wks |
| CPI lodging away from home y/y (Jul) | +1.18% | monthly |
| Inside Airbnb 13-city matched reviews_ltm y/y | +9.0% | Aug dumps |
| Inside Airbnb listings y/y | -1.9% | Aug dumps |
| US Trends share of search, y/y pts | -0.68 | weekly (10 of 13 wks) |
| Eurostat EU27 platform nights y/y | n/a for 2026Q2; 2026Q1 was +9.7% | ~5-month lag |

Single-feature fits on 2023Q1-2026Q2 (`08_q3_2026_nowcast.csv`; ± is the residual SD of the fit, not a forecast interval):

| Target | Feature | Point | ± | Naive (2Q26) | Prior year (3Q25) |
|---|---|---|---|---|---|
| Revenue y/y | funds held y/y (lag 1) | **+12.0%** | 2.0 | 16.5 | 9.7 |
| GBV y/y | funds held y/y (lag 1) | +12.6% | 3.0 | 15.7 | 13.9 |
| ADR FX effect | fitted FX contribution | **+0.96 pp** | 0.7 | 1.3 | 2.7 |
| ADR y/y | trade-weighted USD y/y | +3.1% | 1.1 | 5.3 | 4.7 |
| ADR ex-FX y/y | initial claims y/y | +4.1% | 0.8 | 4.0 | 2.0 |
| Nights y/y | demand index (z from 2023Q1) | +10.0% | 1.5 | 10.3 | 8.8 |
| Nights y/y | demand index ex Inside Airbnb | +10.2% | 2.8 | 10.3 | 8.8 |

**Mechanical assembly.** ADR y/y = ex-FX run-rate (3.25%, the mean of 3Q25-2Q26 letters) + fitted FX contribution (+0.80) = **+4.05%**. GBV y/y = (1+nights)(1+ADR) − 1. Revenue y/y = GBV y/y + the revenue-minus-GBV gap (stay-vs-booking timing, take rate, hedging), which ran -4.2 pp in 3Q25, -3.9 in 4Q25, -1.3 in 1Q26 and +0.8 in 2Q26. `08_q3_2026_guide_reconciliation.csv`:

| Nights y/y | ADR y/y | GBV y/y | rev − GBV gap | Revenue y/y | Revenue $m | vs guide mid $4,730m |
|---|---|---|---|---|---|---|
| 10.3 (naive) | 4.05 | 14.8 | -2.15 (TTM mean) | 12.7 | 4,613 | -2.5% |
| 10.3 | 4.05 | 14.8 | 0.0 (as 2Q26) | 14.8 | 4,701 | -0.6% |
| 11.0 (guide "low double digit") | 4.05 | 15.5 | -2.15 | 13.3 | 4,641 | -1.9% |
| 11.0 | 4.05 | 15.5 | 0.0 | 15.5 | 4,730 | **0.0%** |
| 11.0 | 4.05 | 15.5 | -4.2 (as 3Q25) | 11.3 | 4,558 | -3.6% |
| 12.0 | 4.05 | 16.5 | 0.0 | 16.5 | 4,772 | +0.9% |

The guide midpoint is reproduced exactly by nights +11%, ADR +4.05% and a zero revenue-minus-GBV gap. That is internally consistent with what management actually said in the 2Q26 letter — "GBV growth to be in the mid teens, driven by low double-digit growth in Nights and Seats Booked" (`theos-past-research/research/guidance/data/normalized/source_excerpts.csv`, ABNB-2026Q2-DRIVER-061) — and the assembly at nights +11% produces GBV +15.5%, i.e. mid-teens, from an independently estimated ADR. So the guide is not aggressive on the drivers; it assumes the 2Q26 revenue-minus-GBV gap persists. Everything below the guide in this table is a gap assumption, not a demand call. ABNB has beaten the midpoint in 19 of 19 guided quarters (mean +2.5%; note 03 finding 5), which is another reason not to publish a sub-guide number off a model that just under-predicted twice in a row.

---

## 9. Corrections and consistency with existing work

- No errors found in other people's files. `abnb_backlog_indicators.csv`, `eurostat_platform_nights_monthly.csv`, `predictive/03_quarterly_panel.csv` and `predictive/02_peer_prints.csv` all reproduced as documented.
- `2026-09-05_eu-platform-and-backlog.md` fits 3Q26 revenue growth at +11.5% from funds held; my post-2022 refit gives +12.0%. The difference is the fit window (theirs 4Q21-1Q26, mine 1Q23-2Q26). Same conclusion, and I would use the wider one for the headline and note the ±2 pp.
- This note **does not** contradict note 03 on hotel RevPAR and BEA. Those pairs beat naive here because 2024-26 nights growth is nearly flat, not because they carry information: their correlation with nights falls from +0.88 (2023Q1+) to +0.45 and +0.33 (2024Q1+).
- Two small fixes were made to `08_altdata_backtests.py` during this run: the Eurostat features are now built on a contiguous quarterly index (previously the lag-1 feature was missing for 2026Q2 and 2026Q3 because the source series ends mid-index), and the quarterly panel CSV is now written after the index columns are added.

---

## 10. Build forward: what to start capturing now

The honest summary of this workstream is that the free alt data we hold is either too short, too composition-unstable or too coarse to test. Three captures started today would give a real test by the pitch and a much better one by FY27.

1. **Monthly Inside Airbnb capture on the fixed 13 cities** (plus Theo's 34 US markets), same calendar day each month, storing per city: listings, `reviews_ltm`, `reviews_l30d`, blocked share at 30/90/180 days on listings with `has_availability`, entire-home share, and the calendar file's per-date median price. Twelve captures give the first fixed-panel y/y; `reviews_l30d` on year-ago-matched ids is the metric to score (6 of 7 signs right on the chained panel, ratio 0.81). Inside Airbnb's CDN keeps roughly a year, so a month missed is a month lost.
2. **Weekly Google Trends capture with the pull date stamped**, same payloads and windows as `08_trends_pull.py`. My conclusion is that Trends does not forecast the print, so this is cheap insurance rather than a priority — but because Google renormalises history on every pull, the only way to ever make a point-in-time claim is to have stored the vintages.
3. **Log the funds-held and unearned-fee balances the day each 10-Q posts**, with the RNPL disclosure language alongside. The one live indicator in this note is the one that is being distorted by a product change, and the only way to calibrate the distortion is to track the funds-held-minus-GBV growth gap each quarter (3.8 pp at 2Q25, 5.2 pp at 2Q26).
4. **Do not spend more time on**: composite z-score indexes built off these components, Google Trends share-of-search, Eurostat as a nowcast (it is a post-hoc category check), Inside Airbnb listed prices (discontinued), Common Crawl as a demand series, or the qualitative regional bands as a regression target.

---

## 11. For the model

Parameters this workstream supplies to the driver model. Every one is knowable today.

| Name | Value | Unit | Source |
|---|---|---|---|
| `fx_contribution_to_adr_3q26` | +0.80 | pp of ADR y/y | fit `FX effect = 0.52 − 0.72 × USD y/y`, n = 17, r 0.96, on FRED DTWEXBGS QTD to 6 Sep 2026 (`08_panel_quarterly.csv`) |
| `fx_fit_intercept` / `fx_fit_slope` | 0.52 / −0.72 | pp, pp per % | refit of note 03's relationship on 2022Q2-2026Q2 |
| `adr_exfx_runrate` | +3.25 | % y/y | mean of 3Q25-2Q26 letters ex-FX ADR (`predictive/03_quarterly_panel.csv`) |
| `adr_yoy_3q26` | +4.05 | % y/y | ex-FX run-rate + FX contribution |
| `rev_minus_gbv_gap_ttm` | −2.15 | pp | trailing-4Q mean of revenue y/y minus GBV y/y; range −4.2 to +0.8 |
| `funds_held_yoy_2q26` | +10.46 | % y/y | SEC XBRL `FundsHeldForClients` (`abnb_backlog_indicators.csv`) |
| `backlog_rev_fit_slope` | 0.60 | pp revenue y/y per pp funds-held y/y | OLS 1Q23-2Q26, n = 14, r 0.89 (`08_backlog_tests.csv`) |
| `backlog_rev_nowcast_3q26` | +12.0 (±2.0) | % y/y | above; add ~3 pp for the RNPL under-prediction seen in 1Q26 and 2Q26 |
| `eu_platform_nights_yoy_1q26` | +9.7 | % y/y | Eurostat `tour_ce_omr`, latest published quarter |
| `ia_13city_reviews_ltm_yoy` | +9.0 | % y/y | Inside Airbnb Aug 2026 dumps, matched ids (`08_ia_city_yoy.csv`) |
| `ia_13city_listings_yoy` | −1.9 | % y/y | same |

Nothing else in this workstream should enter the model. In particular, do **not** put a Google Trends term, a share-of-search feature, a Eurostat lag-1 feature or any of the three composite indexes into a forecast equation.

## 12. For the 5 Nov card

1. **The one number to publish: the FX contribution to 3Q26 ADR is +0.80 pp** (against +1.3 in 2Q26 and +5.0 in 1Q26). Reported ADR y/y should therefore land near **+4.0%**, converging on the ex-FX run-rate of 3-4%. This is mechanical (r 0.96, walk-forward 0.44 vs naive) and already knowable. If reported ADR comes in above ~5%, the ex-FX pricing story changed, and that is the thing to react to.
2. **The one number to watch, with its confound stated: funds held +10.5% y/y at 2Q26 end fits revenue +12.0%, below the guide's +14.5% to +16.5%.** Do not present this as a miss call. The same model under-shot 1Q26 by 3.4 pp and 2Q26 by 2.8 pp because RNPL defers guest cash to check-in; adding that back lands on the guide. The check on 5 November is whether the funds-held-minus-GBV growth gap (5.2 pp at 2Q26, up from 3.8 pp a year earlier) widens again. If it does, the indicator is broken like unearned fees and should be retired; if it narrows while revenue holds, the indicator was right and the RNPL ramp is done.
3. **Do not say the guide looks conservative or aggressive on demand.** The guide midpoint is exactly reproduced by nights +11% (management's "low double-digit"), ADR +4.05% (estimated independently, from FX plus the ex-FX run-rate) and a zero revenue-minus-GBV gap — and that combination lands GBV at +15.5%, matching management's "mid teens". The whole difference between any alt-data nowcast and the guide is the revenue-minus-GBV gap term, not demand.
4. **Have the "we tested the alt data" answer ready.** 598 tests across Google Trends, the XBRL backlog, Eurostat platform nights and a 13-city Inside Airbnb panel; 29 pairs beat a naive baseline walk-forward, 7 by more than 20%, and after removing the mechanical FX pair and macro series already known to be 2023-trend artefacts, exactly one survives. Three composite demand/supply/price indexes all lose to "same as last quarter". That is a stronger position in a Q&A than a fabricated edge.
5. **If asked about Europe:** the EU27 platform category grew 9.7% in 1Q26 (Eurostat, five-month lag, no data past March 2026). Airbnb grows with the category in nights, not faster; the positive EMEA revenue gap since 3Q25 is the euro.
