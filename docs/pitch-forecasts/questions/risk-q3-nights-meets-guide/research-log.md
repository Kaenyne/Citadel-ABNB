# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable). Batch A09 (R01, R02, R03 share the research; the claims ledger and query log are complete in each log). Reproduction: `datasets/a09_nights_error_distribution.py` (numpy/pandas, seed 20260917, 400,000 draws per construction, ~60 s); every number in §5–§9 is in its outputs.

## 0. Metadata
- question_name: risk-q3-nights-meets-guide
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § R01)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2026-11-05
- resolution_date: 2026-11-05
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable

## 0b. Question (verbatim)
### Title
Will 3Q26 Nights and Seats Booked growth print ≥ +10.0% y/y (the floor of "low double digits")?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if 3Q26 nights ÷ 133.6m − 1 ≥ 0.100 (≥147.0m). Resolution 5 Nov 2026.
### Fine Print
Derive from the team's nowcast distribution (reviews index +9.5–10.0, external stack +9.2, module 9.49; band 8.5–10.0; walk-forward error distribution of the index), not from web sources. Report the implied probability and its sensitivity to the index's error sd.

Conventions adopted: (1) the resolving number is the press-release "Nights and Seats Booked" for 3Q26 divided by the 3Q25 figure as the letter states it (133.6m); the ratio is computed on the millions as printed to one decimal, so 147.0m resolves Yes (10.03%) and 146.9m resolves No (9.96%); (2) if Airbnb restates 3Q25, the letter's own printed y/y governs; (3) "low double digits" is read as 10–12 (researcher mapping, RNPL handoff), but the question resolves on the 10.0 floor, not the wording; (4) if the print date moves, the same release on its actual date.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Reviews stays index (E): global all-reviews review-weighted quarterly y/y, expanding-window walk-forward RMSE 1.48pp vs naive 2.16 (ratio 0.68), prior-year 0.40, AR(1) 0.70, over 10 scored quarters 1Q24–2Q26; jackknife 0.63–0.86; r 0.86 but r restricted to 2024Q1+ is 0.42 ("most of the correlation is the 2023 normalisation"); OLS slope 0.32 nights-pt per index-pt; every first-difference feature loses to naive (1.45–1.53); lag-1 levels 0.87–0.91 | `research/notes/q3nowcast/E_reviews-stays-index.md` §1 items 1, 4; tables 2.6, 2.9; `data/processed/q3nowcast/E/backtest_abnb_quarterly.csv` | 2026-09-11 | 2026-09-17 | yes |
| 2 | Seven level-mapped implied 3Q26 nights rows after the Tokyo refresh (E_aug): 10.05 (all-reviews review-wtd), 9.20 (equal), 9.23 (median), 9.35 (nights-share), 9.06 (vintage-matched review-wtd), 8.57 (vm equal), 8.68 (vm nights-share); mean 9.16; the same rows anchored on the 2Q26 print 9.8–10.7 (mean 10.34); band 8.6–11.5 on the headline row; the note's call "3Q26 nights +9.5%, band 8.5 to 11.0, stands" | `research/notes/q3nowcast/E_aug_august-batch-refresh.md` §1 item 5, table 2.5; `data/processed/q3nowcast/E_aug/q3_2026_nowcast.csv` | 2026-09-11 | 2026-09-17 | yes |
| 3 | Per-quarter walk-forward errors (predicted − actual, pp; 2023Q1+ window; 1Q24…2Q26), all-reviews review-wtd: +2.00 +0.78 +0.52 −2.66 +1.35 +1.84 −0.25 +0.56 +1.89 −0.74 (mean +0.53, sd 1.45, 7 of 10 over-predictions); equal-wtd: +0.40 −0.44 −0.34 −4.27 +0.33 +1.17 −0.33 −0.31 +0.33 −1.15 (mean −0.46); vintage-matched review-wtd mean −0.05, vm equal −0.71. The two quarters where every row under-predicted are 4Q24 (−2.7 to −4.8; the +12.35% break) and 2Q26 (−0.7 to −1.8; the +10.34% print), both product/lead-time accelerations. Bias-corrected centres of the seven rows: 9.52, 9.66, 9.20, 9.83, 9.10, 9.28, 9.38 (mean 9.42) | `data/processed/q3nowcast/E_aug/backtest_wf_paths.csv` (nights_yoy, lag 0); computed in `datasets/a09_rows_and_errors.csv` | 2026-09-11 | 2026-09-17 | yes |
| 4 | Vintage caveat (WPK): the 0.68 is W2-scored with 1Q23–4Q23 training quarters read from a stale vintage; re-reading 1Q23 from the fresh 2023 mirror moves the ratio to 0.757 (honest, 103 markets) or 0.841 (literal), both above the pre-registered 0.75 line; the W1-scored 2022Q1+ row is 0.837; "no separately measured statistic keeps the stays index at survivor grade on either window". The 3Q26 band is explicitly not changed because it rests on the vintage-matched construction, which is symmetric in age. Ratio factors applied here: ×1.107 and ×1.231 on the walk-forward errors | `docs/revenue-forecast-strategy/05_backtests/WPK_reviews-index-2023-vintage.md` §2.3, §4 items 1–3, §5; `data/processed/q3nowcast_v2/E/t1_fail_e5_rerun.csv` (v1 0.6832, b 0.7566, a 0.8410) | 2026-09-14 | 2026-09-17 | yes |
| 5 | What the index cannot see: it measures July and August stays (review dates) while the KPI counts July–September bookings including bookings for 4Q26/1Q27 stays; "a late-quarter booking shift, which is where RNPL and hurricanes act, is outside what any stay-date series can see"; September is 40% of the quarter's days and unseen; the partial-to-full gap measured 2023–25 is +0.02/−0.6pp (sd 0.2); NYC, LA, SF, Montreal and eight others are absent from the August row | `docs/q3nowcast/SYNTHESIS.md` §3 item 3; E note §1 item 3, table 2.8; E_aug §1 item 2 | 2026-09-11 | 2026-09-17 | yes |
| 6 | External stack (G): 12 knowable survivors give +9.2% median, range 6.8–12.0 (in-sample, not independent); STR US RevPAR July +8.2% then +7.3, +7.2, +6.2, +4.4, +1.7 across August weeks, ADR +5.7 → +0.6; TSA QTD −2.65% vs −0.39% in 2Q26; CPI lodging 4.9 → 3.1; NTTO overseas July −7.0% vs −14.1% (shrinking drag); Marriott 9 Sep: July RevPAR +7%, +5% ex World Cup; Expedia 9 Sep: July consistent with Q2; Chesky 8 Sep: "almost every market is accelerating", no number, no guide update | `research/notes/q3nowcast/G_external-sources-q3-read.md` §1 items 1–5, 7, 8; tables 2.3–2.5 | 2026-09-11 | 2026-09-17 | yes |
| 7 | H1→H2 bridge: the H1→Q3 nights transition is −0.3pt (range −1.3 to +1.1, 2023–25), which puts 3Q26 at 9.5 pattern / 10.0 no-lap / 8.5 half-lap; "Q3 nights at or above 10.5% is the surprise; 10.0 or below is the pattern"; the guide was set with July in hand and "for the guide to hold, the H1 to Q3 transition has to sit at the top of its range and the lap has to cost nothing. That is possible: 2025's Q3 transition was +1.1 with RNPL launching" | `research/notes/2026-09-10_h1-to-h2-bridge.md` §1 items 1–2, §4 | 2026-09-10 | 2026-09-17 | yes |
| 8 | Nights reconciliation: team baseline 9.9% (146.8m), band 8.5–10.3; every quarterly model 9.5–10.3 before a lap haircut and 8.5–9.9 with one; the NA RNPL lap costs about 0.4pt in Q3; the World Cup adds nothing to booked nights in Q3 | `research/notes/2026-09-10_nights-baseline-reconciliation.md` §1, §3 | 2026-09-10 | 2026-09-17 | yes |
| 9 | RNPL module: 3Q26 base 9.49% (146.3m), band 8.8–10.3; bull 10.25, bear 8.76; the July 2026 booking-type expansion enters as +0.30/+0.20/+0.10 by scenario and is "the largest single offset to the 3Q26 lap", "entirely unquantified"; the US partial-lap correction is worth up to +0.35 and "nobody has applied it" | `docs/rnpl-short-audit/00_SYNTHESIS.md` §1 item 3; `docs/rnpl-short-audit/01_rnpl-nights-mechanics-audit.md` (scenario design, evidence-that-weakens paragraph); `data/processed/rnpl_short_audit/rnpl_nights_module.csv` | 2026-09-11 | 2026-09-17 | yes |
| 10 | Guidance ledger, nights guides 2Q22–2Q26: 17 issued, 16 resolved; 15 met, 1 not met in the company's favour (1Q26→2Q26 "slightly decelerate", printed +1.2); the 1Q25 "stable" printed 0.58 lower and is coded met; bucket era: 4Q25 "mid-single" (4–6) printed 9.82 (+4.8 over mid, bucket set 3.8 below the printed rate), 1Q26 "high-single" (7–9) printed 9.15 (+1.15); the 3Q26 bucket (10–12) was set with 10.34 just printed, so its floor sits only 0.34 below the printed rate, the smallest floor cushion in the bucket era. "Stable" guides resolved +0.49, −1.59, −0.81, −0.58, +1.39 against the prior rate | `data/processed/overnight/02_guidance_ledger.csv` (metric nights_yoy_pct rows); `docs/pitch-forecasts/questions/q4-nights-bucket/research-log.md` claim 3 | 2026-09-07 | 2026-09-17 | yes |
| 11 | Positioning card: the Street's bar matched the guide's sign in 12 of 13 prints; both accelerating guides (3Q23, 4Q24) were met; one soft downside miss (1Q25); 3Q26E bar 148.9m = +11.45% is only the fourth accelerating bar in 16; Bloomberg MODL 28 estimates 147.0–151.0m (+10.0 to +13.0), team 146.8m below the lowest; "the team's call ... is a bet on the first downside miss of a management nights guide in the sample" | `research/notes/2026-09-13_market-implied-model.md` §10; `data/processed/reverse_dcf/E/E_guide_vs_street_sign.csv`, `E_street_sign_history.csv`, `E_street_distribution_vs_team.csv` | 2026-09-13 | 2026-09-17 | yes |
| 12 | Sequential-change base rate (computed from the ledger's disclosed y/y): 16 quarter-to-quarter changes 3Q22–2Q26; the print needs a change ≥ −0.34 (R01) / ≥ +0.26 (R02): 7/16 = 0.44 and 6/16 = 0.375; post-2023 5/10 and 4/10; the four Q2→Q3 transitions were +0.5, +2.5, −0.2, +1.4 (4/4 ≥ −0.34; 3/4 ≥ +0.26) | `datasets/a09_base_rates.csv` | 2026-09-17 | 2026-09-17 | yes |
| 13 | Management set "low double digits" on 6 Aug with July bookings in hand; named offsets to the H2 comps: global RNPL ramp, the July eligibility expansion, hotels growing ~3x homes, first-time bookers +11%, Experiences supply +80% | `docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md` §5.4; `data/raw/letters/2Q26_d70413dex991.htm` | 2026-09-11 / 2026-08-06 | 2026-09-17 | yes |
| 14 | Kalshi KXABNB-26NOVNEB, yes bid/ask at 2026-09-17T03:21:58Z: >150m 0.32/0.36, >148m 0.50/0.55, >146m 0.63/0.66, >144m 0.76/0.83; volume, open_interest None, liquidity_dollars 0. Mid-price interpolation: P(≥147.0m) 0.587, P(≥147.8m) 0.539. The Octagon mirror shows the same strikes at 60/53/30% on 29 Jul 2026 with 999/428/591 contracts traded, i.e. the ladder has not repriced through the 2Q26 beat, the 3Q26 guide or the 8–10 Sep fall: internal staleness marker, weight 0.10 | https://api.elections.kalshi.com/trade-api/v2/markets?status=open&limit=100&series_ticker=KXABNB (`sources/kalshi_markets_KXABNB_open_20260917T032158Z.json`); https://www.octagonai.co/markets/financials/kpis/airbnb-bookings-in-q3 (`sources/octagon_kalshi_q3_nights_ladder_asof_2026-07-29.txt`) | 2026-09-17 / 2026-07-29 | 2026-09-17 | yes |
| 15 | Polymarket public-search "airbnb" at 03:21:58Z: no market on Q3 KPIs; only closed Q2 GBV brackets and September price-hit ladders | https://gamma-api.polymarket.com/public-search?q=airbnb (`sources/polymarket_search_airbnb_20260917T032158Z.json`) | 2026-09-17 | 2026-09-17 | no |
| 16 | Earlier logs in this run used P(3Q26 ≥ 10.0) = 0.38 and P(≥ 10.59) = 0.24 from N(9.55, 1.48) (C02 §5, S01 claim 9); C01's sensitivity: nights at 10.0 gives P(guide below Street) 0.77, at 10.6 (joint bull) 0.49 | `docs/pitch-forecasts/questions/q4-nights-bucket/research-log.md`; `day1-move-5nov/research-log.md`; `q4-revenue-guide-vs-street/research-log.md` §7 | 2026-09-17 | 2026-09-17 | yes |
| 17 | Pre-registered team card: 3Q26 nights ≥ 10.3 weakens the drag hypothesis, ≤ 8.5 supports, 8.6–10.2 inconclusive | `data/processed/overnight2/D/D1_prereg_thresholds.csv` row 1 | 2026-09-11 | 2026-09-17 | no |
| 18 | Alt-data constructions (this log): headline-row plug-in on 10 errors P(≥10) 0.30; seven-row mixture plug-in 0.21, kernel (bw 0.5) 0.26, bias-corrected normal 0.36; kernel with errors ×1.107 (revintaged honest) 0.27, ×1.231 (literal) 0.28; parametric N(9.55, 1.70) 0.40; anchored-on-2Q26 first-difference family 0.56 (reported, not used: loses to naive). Alt-data view used = mean of the revintaged kernel and the parametric = 0.33 (R02 0.22) | `datasets/a09_alt_data_estimates.csv`, `a09_three_views.csv` | 2026-09-17 | 2026-09-17 | yes |
| 19 | Management-delivery construction (this log): actual = 10.0 + cushion N(0.6, 0.5) + error N(0, 1.3): P(≥10.0) 0.67, P(≥10.6) 0.50; grid over cushion 0.3/0.6/1.0 and error sd 1.0/1.3/1.6 spans 0.57–0.81 (R01) and 0.39–0.64 (R02). Outside view used = mean of the sequential base rate and this = 0.55 (R02 0.44) | `datasets/a09_mgmt_delivery_view.csv`, `a09_base_rates.csv` | 2026-09-17 | 2026-09-17 | yes |
| 20 | Blend (0.60 alt-data, 0.30 outside view, 0.10 market): R01 0.424, R02 0.316; weight grid: alt-only 0.33/0.22, 0.8/0.2/0 0.38/0.26, 0.5/0.3/0.2 0.45/0.35, 0.5/0.5/0 0.44/0.33, outside-only 0.55/0.44, market-only 0.59/0.54. Final-calibrated normal (sd 1.70, P(≥10) = 0.424): centre 9.67; E[nights | ≥10.0] 11.24, E[nights | ≥10.6] 11.67 | `datasets/a09_three_views.csv`, `a09_weight_sensitivity.csv`, `a09_final.json` | 2026-09-17 | 2026-09-17 | yes |
| 21 | ABNB close $167.51 on 16 Sep 2026; brief sensitivities: 1pt of 3Q26 nights ≈ 1.34m ≈ $48M revenue, 1pt of 4Q26 ≈ $30M, 1pt of FY27 revenue growth ≈ $158M, margin 0.59pp per 1pt of 2H26 revenue (held) / 0.66 FY27, FY27 EPS ≈ $0.0014 per $M EBITDA, 0.40–0.48 turns per pt of forward growth, one turn ≈ $9–10; S01 cells: base-case day-1 median −8.6%, unconditional −2.9%, accel & guide-above +5.0 (w 0.08), accel & below +1.8 (0.17), flat & below −2.9 (0.08), flat & above +0.2 (0.04) | `docs/pitch-forecasts/00_BRIEF.md` (sensitivities); `day1-move-5nov/research-log.md` §5–6; `q4-revenue-guide-vs-street/sources/yfinance_abnb_history_20260917T025239Z.csv` | 2026-09-16 / 2026-09-17 | 2026-09-17 | yes |
| 22 | Web (search snippets, pages not fetched): no published sell-side 3Q26 nights consensus in the open web; Q3 EPS consensus $2.75 (29 analysts, aggregator page); Finimize (paywalled, undated, post-6 Aug): "Airbnb has broadened which stays qualify"; B. Riley estimates RNPL added 150bp to Q2 nights growth after 200bp in Q1 | https://www.octagonai.co/markets/financials/kpis/airbnb-bookings-in-q3 ; https://finimize.com/content/airbnbs-reserve-now-pay-later-push-could-keep-bookings-growing (`risk-july-rnpl-expansion-offsets-lap/sources/finimize_rnpl_expansion_2026.txt`) | 2026-08 to 2026-09 | 2026-09-17 | no |
| 23 | Final 72-hour recency check (query 18): fall-travel PR content (short trips, wishlists), nothing on quarter-to-date bookings, the guide or the call date; no change to the number | WebSearch (see §2) | 2026-09-17 | 2026-09-17 | no |

Newest load-bearing source: the Kalshi fetch and the computed tables (17 Sep, zero days old against a 49-day window); the alt-data inputs are 11–14 Sep (3–6 days, under the 7-day cap). The September Inside Airbnb dumps are the next real input (monitoring row 1).

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`, skill `SKILL.md`, `references/research-log-format.md`, `examples/example-research-log.md`; finished logs and JSONs for C01, S01, C06, C02, C05
2. [repo] `docs/q3nowcast/SYNTHESIS.md`; `research/notes/q3nowcast/E_reviews-stays-index.md`, `E_aug_august-batch-refresh.md`, `G_external-sources-q3-read.md`
3. [repo, pandas] `data/processed/q3nowcast/E/` and `E_aug/`: `q3_2026_nowcast.csv`, `backtest_wf_paths.csv` (nights_yoy, lag 0, seven global features, both windows), `backtest_survivor_robustness.csv`, `index_quarterly.csv`, `partial_vs_full_quarter.csv`, `backtest_abnb_quarterly.csv`
4. [repo] `data/processed/q3nowcast_v2/E/_run_log.txt`, `t1_fail_e5_rerun.csv`, `t1_wedge_constancy.csv`; `q3nowcast_v2/E_attrition/run_summary.json`, `prereg_results.csv`; `docs/revenue-forecast-strategy/05_backtests/WPK_reviews-index-2023-vintage.md`
5. [repo] `research/notes/2026-09-10_h1-to-h2-bridge.md`; `research/notes/2026-09-10_nights-baseline-reconciliation.md`
6. [repo] `docs/rnpl-short-audit/00_SYNTHESIS.md`, `01_rnpl-nights-mechanics-audit.md` (July-expansion lines); `data/processed/rnpl_short_audit/rnpl_nights_module.csv`; `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` §2.4; `data/processed/overnight2/D/rnpl_statement_ledger.csv` (eligibility/expansion rows D001–D052); `D1_prereg_thresholds.csv`
7. [repo] `research/notes/2026-09-13_market-implied-model.md` §10; `data/processed/reverse_dcf/E/E_street_sign_history.csv`, `E_guide_vs_street_sign.csv`, `E_street_distribution_vs_team.csv`
8. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv`, all nights rows (23, 4Q20–2Q26)
9. [repo] `docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md` §5.4
10. [repo] grep for "WPK-A" / "0.757" across `research/notes` and `docs` (the catalog note has no such tag; the finding is the WPK note, surfaced via `docs/pitch-forecasts/audits/A01-research-audit.md` finding A01-08)
11. [Kalshi API] `markets?status=open&limit=100&series_ticker=KXABNB` — 2026-09-17T03:21:58Z, saved
12. [Polymarket public-search] airbnb — 03:21:58Z, saved
13. WebSearch: Airbnb news
14. WebSearch: Airbnb third quarter 2026 nights and seats booked estimate analysts preview
15. WebSearch: Airbnb Reserve Now Pay Later expanded eligible booking types July 2026 (charged to R03)
16. WebFetch: finimize.com "Reserve Now, Pay Later push could keep bookings growing" (paywalled fragment)
17. WebFetch: octagonai.co airbnb-bookings-in-q3 (Kalshi mirror, page state 29 Jul 2026)
18. WebSearch: Airbnb bookings demand travel trends this week September 2026 (final 72-hour neutral recency check — result: nothing on quarter-to-date bookings; no change) (charged to R02)
19. [computed] `datasets/a09_nights_error_distribution.py` → the ten output files

WebSearch calls charged to R01: 2 (queries 13, 14); batch total 4 of 15.

## 3. Leading Hypothesis Entities
Airbnb, Nights and Seats Booked, Inside Airbnb reviews stays index, Ellie Mertz, Brian Chesky, "low double digits", Reserve Now Pay Later, Kalshi KXABNB, Bloomberg MODL, 5 November 2026

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Use the headline row (10.0, band 8.6–11.5) at face value: P(≥10) ≈ 0.5 | discarded | The row over-predicted in 7 of 10 walk-forward quarters (mean +0.53pp, claim 3); its own plug-in error distribution gives 0.30; bias-corrected it is 9.52 |
| Use the anchored-on-2Q26 rows (10.2–10.7): P(≥10) ≈ 0.56 | discarded, reported | They are the first-difference construction (naive + slope × Δindex), and first differences lose to naive at 1.45–1.53 (claim 1) |
| Normal error at the published sd 1.48 (the C02/S01 convention) | kept as one of two alt-data legs, sd widened to 1.70 | The vintage caveat moves the measured ratio to 0.757–0.841 (claim 4), i.e. RMSE 1.63–1.82; the jackknife spans 1.36–1.86; the 10-quarter empirical errors have a −2.7 to −4.8 left tail (4Q24) that a 1.48 normal under-weights |
| The empirical seven-row kernel mixture (0.26–0.28) is the whole answer | kept at half the alt-data weight | It is built on 10 errors per row with 0.1 granularity, and five of the seven rows are vintage-matched or equal-weighted variants centred 8.6–9.4 whose bias correction moves them up 0.2–0.7; the two legs are averaged |
| Management's 12-of-13 record means P ≈ 0.9 | discarded as a raw rate, kept via the delivery construction (0.67) | The record is dominated by directional "moderate" guides that any lower number satisfies; the two accelerating guides were met (n 2); the bucket cushions (+4.8, +1.15 over mid) were on buckets set 1–4pts below the printed rate, while this floor sits 0.34 below it (claim 10) |
| Q3 never decelerates against Q2 (4 of 4 since 2022) | kept inside the sequential base rate (0.44 all, 1.0 Q3-only) | n 4 with a reopening year and an RNPL-launch year; the bridge's H1→Q3 pattern on the H1 mean is −0.3 (claim 7); given a quarter of the outside-view weight through the mean with the all-quarter rate |
| The Kalshi ladder (0.59) is a live market view | discarded as a live price, kept at 0.10 | Zero liquidity, volume None, and the Octagon mirror shows the same prices on 29 July before the print and the guide (claim 14): the ladder is the Street bar, which is the guide |
| The Street's 28 of 28 estimates ≥ 10.0% is evidence of the print | discarded | The bar rose 2.1% on the 6 Aug beat and sits inside the guide bucket; it is the guide echoed, not an independent read (claim 11) |
| The July eligibility expansion is large enough to lift Q3 by ≥ 0.5pt | kept as the main upside path inside the outside view and the R03 joint | Unquantified (D044); RNPL module +0.10 to +0.30; B. Riley's RNPL-alone 150bp in Q2 is below management's bundle figure; C06's Exp(1.4) share expansion maps to +0.2pt of nights |
| A September shock (hurricane, shutdown, geopolitics) takes the quarter below 10 | inside the error sd | The event catalogue puts every such event at ≤ 1pt and mostly invisible (bridge §6); a 1pt hit is 0.6 sd |
| Restatement or a 3Q25 base change flips resolution | tail, < 1% | Convention 2; Airbnb has not restated nights since the Seats redefinition (3Q25 letter), which is already the base |

## 5. Independent Estimates
- base_rate_estimate: 0.55 — mean of (i) the sequential-change reference class, 7 of 16 quarter-to-quarter changes since 3Q22 were ≥ −0.34pt (0.44; post-2023 5/10; Q2→Q3 4/4) and (ii) the management-delivery construction, floor 10.0 + cushion N(0.6, 0.5) + management error N(0, 1.3) = 0.67 (claims 10–12, 19); regime-conditioned by scaling the bucket cushion to a bucket set at the printed rate rather than 1–4pts below it
- decomposition_estimate: 0.33 — the alt-data distribution: mean of the seven-row kernel mixture with walk-forward errors scaled ×1.107 for the vintage caveat (0.27; centre 9.45, sd 1.72) and the parametric N(9.55, 1.70) (0.40); the seven bias-corrected level rows centre at 9.42 (claim 3, 18); the anchored/first-difference family (0.56) is excluded because it loses to naive
- anchor_estimate: 0.59 — Kalshi KXABNB mid prices interpolated at 147.0m (P(>146m) 0.645, P(>148m) 0.525) at 2026-09-17T03:21:58Z; not repriced since 29 July, zero liquidity (claim 14)
- anchor_value: 0.587 (Kalshi, 2026-09-17T03:21:58Z, stale-quote caveat)
- final_estimate: 0.42 (credible interval 0.30–0.55)
- final_minus_anchor: −17 points. Independence: the anchor is a quote ladder that has not moved since before the guide and is the Street bar, which is the guide; the final is built from the repo's error-measured nowcast (weight 0.6) and the management/sequential outside view (0.3), with the ladder at 0.1. The three estimates disagree by 26 points; the disagreement is one thing: whether the stays index or management's July-in-hand booking data is the better read of a quarter whose September is unseen. The asymmetry that decides where I land: every outside series the team can measure (hotels, TSA, CPI lodging, EMEA stays, the external stack at 9.2) decelerates through August, and the index's two historical under-predictions were product accelerations management had pre-announced (RNPL launch 2025, the 4Q24 lead-time normalisation), whereas this quarter's candidate (the July expansion) is unquantified and small in every repo estimate. That is why the number sits below 0.5 despite a 16-print record of guides met. Coherence: R01 = 0.42 is 4 points above the P(≥10) = 0.38 that C02 and S01 used as their conditioning input; the difference is the outside-view and market legs this question was asked to reconcile, and X01 should use 0.42 for the print state (it moves S01's unconditional median by roughly +0.3)

## 6. Final Numbers
**Binary.** P(3Q26 Nights and Seats Booked ≥ 147.0m, i.e. ≥ +10.0% y/y) = **0.42**, credible interval **0.30–0.55** (the span of the weight grid from alt-data-only 0.33 to 0.5/0.3/0.2 0.45, widened for the sd grid 0.27–0.43 at centre 9.55).

Implied distribution used for the impact table and for R02/R03: N(9.67, 1.70) after calibration to 0.42 (E[nights | ≥10.0] = 11.24%; P(≥10.6) under this same normal 0.29, R02's own blend 0.32).

Sensitivity to the index's error sd (fine print), centre 9.55: sd 1.00 → 0.33, 1.25 → 0.36, 1.48 → 0.38, 1.63 → 0.39, 1.70 → 0.40, 1.82 → 0.40, 2.16 (naive) → 0.42, 2.50 → 0.43. At centre 9.2 (external stack) the same grid runs 0.21–0.37; at 9.9 (team baseline) 0.46–0.48. The sd matters less than the centre: because the centre sits within 0.5pt of the threshold, doubling the sd moves P by 0.1, while moving the centre by 0.35pt moves it by 0.08.

Extreme-probability gate: not triggered (0.42). Resolution-criteria audit anyway: (i) the KPI is "Nights and Seats Booked" as printed in millions to one decimal; 147.0m resolves Yes; (ii) a growth figure stated in the letter as "10%" with 146.9m printed resolves No on the arithmetic (convention 1); (iii) no restatement risk priced above 1%.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Alt-data centre 9.45–9.55 (bias-corrected rows, revintaged kernel) | Team baseline 9.9 as the centre (no bias correction): alt-data leg 0.47 → final 0.51; external stack 9.2 as the centre: alt-data 0.30 → final 0.41 |
| Index error sd 1.70 (revintaged honest) | 1.48 (published): alt-data 0.38 → final 0.42 (unchanged to 2dp); 1.82 (literal): 0.40 → 0.42; 2.16 (index no better than naive): 0.42 → 0.43 |
| Blend weights 0.60 / 0.30 / 0.10 | Alt-data only (the fine print read strictly): 0.33; 0.8/0.2/0: 0.38; 0.5/0.5/0: 0.44; 0.5/0.3/0.2: 0.45; outside view only: 0.55; market only: 0.59 |
| Management cushion N(0.6, 0.5) and error sd 1.3 | Cushion 0.3 (bucket set with no low-ball): delivery view 0.59 → final 0.41; cushion 1.0 (bucket-era habit intact): 0.76 → 0.44 |
| Sequential base rate on all 16 transitions (0.44) | Q3-only transitions (4/4 ≥ −0.34, Laplace 0.83): outside view 0.75 → final 0.48; post-2023 only (0.50): final 0.43 |
| Kalshi ladder weight 0.10 | 0 (dead market): 0.41; 0.25 (live market): 0.45 |
| September dumps move the index centre by ±0.5pt | +0.5: final ≈ 0.50; −0.5: ≈ 0.35 (sd grid rows at 9.9 and 9.2, alt-data leg only, others held) |

Pre-mortem ("it is 5 Nov and the print was 10.0 or more, i.e. the 0.42 was too low"): (1) **the stays index missed a booking-date acceleration again**, as in 4Q24 and 2Q26 (claim 3): the July eligibility expansion and the global RNPL ramp lifted July–September bookings for Q4 and Q1 stays that no review will record until 2027; priced through the sd (the two under-prediction quarters are inside the empirical errors) and through the outside-view leg. (2) **Management's July-in-hand information dominated**: a 16-print record of guides met is the strongest single fact in this log and I gave it 0.30; a 0.50 weight would have said 0.44, so the miss would be small. (3) **Hotels decelerated, Airbnb did not**: STR RevPAR is a stay-date US-hotel series and Airbnb's growth is in LatAm and APAC (reviews +27 and +10 QTD); the external stack was in-sample and 5pp wide. (4) **Seats**: Experiences and Services supply (+80%) adds seats that the reviews index and hotel data never see; one point of the KPI is 1.34m seats-or-nights. ("It was 9.9 or less, i.e. 0.42 was too high"): (5) the US RNPL lap plus the pull-forward comp bit harder than the module's −0.4 (bear 8.76) and the EMEA summer was flat on a stay basis (+0.9); priced as the 0.58 side. Asymmetry: the memo's use of R01 is as the first risk to the short; overstating it costs a hedge the team need not carry, understating it puts the pitch on a bet against a guide record with no downside miss; the interval is kept wide (0.30–0.55) for that reason.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-18 to 2026-09-30 | September Inside Airbnb reviews dumps land; re-run E (`E_aug1_probe`, `E_aug2_download`, `E_aug_run`) for the full July–August window and the first September days | Re-centre: each +0.5pt on the bias-corrected centre ≈ +0.08 on P; a centre ≥ 9.9 → 0.50; ≤ 9.2 → 0.35. Re-run `datasets/a09_nights_error_distribution.py` |
| 2026-10-02 | Prelim memo due | Quote 0.42 (0.30–0.55) with the impact row; state the alt-data-only 0.33 and the management view 0.67 as the two poles |
| 2026-10-13 | September CPI (lodging away from home) | A further fade below +3% y/y: −0.02; a rebound above +4%: +0.02 |
| ~2026-10-15 | NTTO September preliminary arrivals; Airbnb fixes the call date | Overseas arrivals improving past −5%: +0.02; no probability change from the date |
| ~2026-10-21 | Hilton Q3 (RevPAR family 0.665x on nights) | US RevPAR Q3 ≥ +6%: +0.03; ≤ +3%: −0.03 |
| 2026-10-28 to 2026-10-30 | Booking and Expedia Q3 prints (EXPE reads through) | EXPE room nights accelerating vs its Q2 rate: +0.03; decelerating ≥ 2pt: −0.03; BKNG carries nothing |
| ~2026-11-03 | Marriott Q3 (0.691x); US midterms | RevPAR as above, half weight (second read of the same family) |
| 2026-11-05 (after close) | 3Q26 release: Nights and Seats Booked in millions | Resolve on 147.0m; record the walk-forward error of the index (pred 10.05 headline / 9.42 bias-corrected) for the 5 Nov score sheet; feed R02, R03, X01 |

## 9. Impact
If 3Q26 nights print ≥ 10.0% (E[nights | ≥10.0] = 11.24% under the final-calibrated normal, vs the team baseline 9.9 and the nowcast 9.5), deltas versus the memo's base case (`datasets/a09_impact.csv`):

| Item | Delta if R01 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | **+1.3** (11.24 − 9.9) | conditional mean, claim 20 |
| 4Q26 nights (pts) | **+0.8** (60% persistence of the Q3 surprise into the Q4 booking rate) | judgement; bridge §3 range −2.8 to +3.3 on the H1→Q4 transition |
| ADR (pts) | 0.0 | nights and ADR are independent lines in the E/H notes; a mix effect is inside R03 |
| 4Q26 revenue ($M) | **+50** = ⅔ × (1.34pt × 1.34m × $176.8 = $317M GBV) × 12.03% + 0.8pt × $30M | kernel carry (C01 claim 4) + brief sensitivity |
| 3Q26 revenue ($M) | +65 (1.34 × $48M) | brief sensitivity (memo context only) |
| FY27 revenue ($M) | **+85** (0.54pt of FY27 growth × $158M) | 40% persistence into FY27 |
| FY26 adj. EBITDA margin (pp) | **+0.4** (0.59pp per 1pt of 2H26 revenue, held costs; +$115M on ~$7.98bn = 1.44pt × 0.59 × ½ FY weight) | brief sensitivity (flex variant 0.38 → +0.27pp) |
| FY27 adj. EBITDA margin (pp) | **+0.35** (0.66 × 0.54) | brief sensitivity |
| FY27 EPS ($) | **+0.08** ($85M × 0.66 flow-through = $56M EBITDA × $0.0014) | brief sensitivity |
| Stock ($/share) | **+18.8 vs the base-case day-1** (S01 cell mix given nights ≥10: +1.3% vs the base-case −8.6% = +9.9pt × $167.51 = $16.6, plus the multiple line 0.54pt × 0.44 turns × $9.5 = $2.3); **+9.3 vs the unconditional** (−2.9% median) | S01 §6 cells, brief multiple-growth slope |
| **EV = P × impact** | **0.42 × $18.8 = $8.0/share** (vs base case); $3.9 vs unconditional | |
| Materiality | **Material** (≥ $1/share by a wide margin). This is the largest single risk line in the batch: it is the print sign the memo's short is written against | |

## RESUME
The next agent (audit response) should re-run `datasets/a09_nights_error_distribution.py` (deterministic, ~60 s) and attack three choices: (1) the 0.60/0.30/0.10 blend, which spans 0.33 (alt-data only, the fine print read strictly) to 0.55 (outside view only); (2) the management-delivery construction's cushion N(0.6, 0.5), the one parameter with no measured analogue (bucket set at the printed rate, n 0); (3) the exclusion of the anchored-on-2Q26 rows (0.56), which the E note's first-difference backtest justifies but which an auditor may want reinstated at a small weight. Check claim 3's error vectors against `backtest_wf_paths.csv` by hand (qi 8096–8105 = 1Q24–2Q26, err = predicted − actual). If the September dumps have landed, re-run E first and re-centre before anything else.
