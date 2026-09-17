# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable). Batch A09 (with R01 and R03; the ledger and query log are repeated in full so this log is self-contained). Reproduction: `datasets/a09_nights_error_distribution.py` (seed 20260917; identical to the R01 copy; writes every table cited here into this folder).

## 0. Metadata
- question_name: risk-q3-nights-accelerates
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § R02)
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
Will 3Q26 nights growth print ≥ +10.6% y/y (an acceleration vs 2Q26's +10.34% under the positioning card's 0.25pt dead band)?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if 3Q26 nights ≥ 147.8m. Resolution 5 Nov 2026. Same derivation rule as R01.
### Fine Print
(R01's fine print applies: derive from the team's nowcast distribution and the walk-forward error distribution of the index, not from web sources; report the implied probability and its sensitivity to the index's error sd.)

Conventions adopted: (1) resolves on the printed millions to one decimal: 147.8m is Yes (10.63%), 147.7m is No (10.55%); the 10.6% in the title is the rounded form of the 147.8m threshold and the millions govern; (2) the "dead band" language is descriptive; the question resolves on the number only; (3) restatement and date-move conventions as R01.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Reviews stays index (E): walk-forward RMSE 1.48pp vs naive 2.16 (0.68) over 10 scored quarters 1Q24–2Q26; jackknife 0.63–0.86; r 0.86, r 2024Q1+ 0.42; slope 0.32; first differences lose to naive (1.45–1.53); lag-1 0.87–0.91 | `research/notes/q3nowcast/E_reviews-stays-index.md` §1 items 1, 4; tables 2.6, 2.9 | 2026-09-11 | 2026-09-17 | yes |
| 2 | Seven level rows (E_aug): 10.05, 9.20, 9.23, 9.35, 9.06, 8.57, 8.68 (mean 9.16); anchored-on-2Q26 9.8–10.7 (mean 10.34); "3Q26 nights +9.5%, band 8.5 to 11.0, stands" | `research/notes/q3nowcast/E_aug_august-batch-refresh.md` §1 item 5, table 2.5; `data/processed/q3nowcast/E_aug/q3_2026_nowcast.csv` | 2026-09-11 | 2026-09-17 | yes |
| 3 | Walk-forward errors (pred − actual, 2023Q1+, 1Q24…2Q26), headline row: +2.00 +0.78 +0.52 −2.66 +1.35 +1.84 −0.25 +0.56 +1.89 −0.74 (mean +0.53; 7 of 10 over-predictions); equal-wtd mean −0.46; vm review-wtd −0.05; the only two quarters every row under-predicted are 4Q24 (−2.7 to −4.8) and 2Q26 (−0.7 to −1.8), both product/lead-time accelerations. Bias-corrected centres 9.10–9.83, mean 9.42. A ≥ 10.6 print from the headline row needs an error ≤ −0.55: 2 of 10 (4Q24, 2Q26) | `data/processed/q3nowcast/E_aug/backtest_wf_paths.csv`; `datasets/a09_rows_and_errors.csv` | 2026-09-11 | 2026-09-17 | yes |
| 4 | Vintage caveat: 0.683 → 0.757 (honest) / 0.841 (literal) after re-reading 1Q23 from the fresh 2023 vintage; W1 0.837; the 3Q26 band is not changed because the vintage-matched construction is symmetric in age; factors ×1.107 / ×1.231 applied to the errors here | `docs/revenue-forecast-strategy/05_backtests/WPK_reviews-index-2023-vintage.md` §2.3, §4, §5; `data/processed/q3nowcast_v2/E/t1_fail_e5_rerun.csv` | 2026-09-14 | 2026-09-17 | yes |
| 5 | The index reads July–August stays, not July–September bookings; late-quarter booking shifts (RNPL, lead time) are invisible; September is 40% of the quarter; partial-to-full gap +0.02/−0.6 (sd 0.2); NYC, LA, SF, Montreal absent from the August row | `docs/q3nowcast/SYNTHESIS.md` §3 item 3; E note §1 item 3, table 2.8; E_aug §1 item 2 | 2026-09-11 | 2026-09-17 | yes |
| 6 | External: stack +9.2 (6.8–12.0); STR US RevPAR +8.2 (July) fading to +4.4/+1.7 by late August, ADR +5.7 → +0.6; TSA QTD −2.65%; CPI lodging 4.9 → 3.1; NTTO overseas −7.0 vs −14.1; Marriott July +7 (+5 ex World Cup); Expedia July consistent with Q2; Chesky 8 Sep "almost every market is accelerating", no number. "Nothing points to the +10.5% or more that the pre-registered card calls the surprise" | `research/notes/q3nowcast/G_external-sources-q3-read.md` §1; `docs/q3nowcast/SYNTHESIS.md` §3 item 1 | 2026-09-11 | 2026-09-17 | yes |
| 7 | Bridge: H1→Q3 transition −0.3 (−1.3 to +1.1); 3Q26 9.5 pattern / 10.0 no lap / 8.5 half lap; "No scenario in this bridge produces a Q3 nights acceleration"; "Q3 nights at or above 10.5% is the surprise" | `research/notes/2026-09-10_h1-to-h2-bridge.md` §1 items 1–2, §4 | 2026-09-10 | 2026-09-17 | yes |
| 8 | Reconciliation: team 9.9 (146.8m), band 8.5–10.3; only WS10's bull case (12.4) clears the guide by more than a rounding; "a deceleration against 2Q26's 10.3% remains the base case in every model except the naive carry-forward" | `research/notes/2026-09-10_nights-baseline-reconciliation.md` §1 | 2026-09-10 | 2026-09-17 | yes |
| 9 | RNPL module 3Q26: base 9.49 (8.8–10.3), bull 10.25 (147.3m: July expansion +0.30, US partial-lap +0.34, propensity 2pp), bear 8.76; the July expansion is "the largest single offset to the 3Q26 lap" and unquantified | `docs/rnpl-short-audit/00_SYNTHESIS.md` §1 item 3; `data/processed/rnpl_short_audit/rnpl_nights_module.csv` | 2026-09-11 | 2026-09-17 | yes |
| 10 | Guidance ledger: 16 resolved nights guides since 2Q22, 15 met, 1 not met in the company's favour (1Q26→2Q26 "slightly decelerate" printed +1.19 acceleration); accelerating guides 2Q23→3Q23 ("modest sequential increase", +2.5) and 3Q24→4Q24 ("higher", +3.9) both met; bucket beats +4.8 and +1.15 over the midpoint on buckets set 1–4pts below the printed rate; the 3Q26 bucket midpoint (11.0) is +0.66 above the printed rate, the first bucket set above the printed rate | `data/processed/overnight/02_guidance_ledger.csv`; `q4-nights-bucket/research-log.md` claim 3 | 2026-09-07 | 2026-09-17 | yes |
| 11 | Positioning card: Street bar 148.9m = +11.45% is an accelerating bar (fourth in 16 prints; the prior three were all met with a printed acceleration, mean +4.2% excess day-1); 12 of 13 sign matches; 28 of 28 Bloomberg estimates ≥ +10.0%; "the price carries a 3Q26 nights rate of about 10.6 to 11.2%" in proxy units | `research/notes/2026-09-13_market-implied-model.md` §10; `data/processed/reverse_dcf/E/E_street_sign_history.csv`, `E_street_distribution_vs_team.csv` | 2026-09-13 | 2026-09-17 | yes |
| 12 | Sequential-change base rate: a change ≥ +0.26pt occurred in 6 of 16 transitions since 3Q22 (0.375; Laplace 0.39), 4 of 10 post-2023, 3 of 4 Q2→Q3 (+0.5, +2.5, −0.2, +1.4) | `datasets/a09_base_rates.csv` | 2026-09-17 | 2026-09-17 | yes |
| 13 | Guide set 6 Aug with July in hand; named offsets: global RNPL ramp, July expansion, hotels ~3x, first-time bookers +11%, Experiences supply +80% | `docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md` §5.4 | 2026-09-11 | 2026-09-17 | yes |
| 14 | Kalshi KXABNB at 2026-09-17T03:21:58Z: >148m 0.50/0.55, >146m 0.63/0.66; interpolated P(≥147.8m) 0.539; volume None, liquidity 0; Octagon mirror shows 60/53/30% at 146/148/150m on 29 Jul 2026, before the print and the guide: staleness marker, weight 0.10 | `sources/kalshi_markets_KXABNB_open_20260917T032158Z.json`; `sources/octagon_kalshi_q3_nights_ladder_asof_2026-07-29.txt` | 2026-09-17 / 2026-07-29 | 2026-09-17 | yes |
| 15 | Earlier logs: S01 used P(accelerating ≥ 10.59) = 0.24, flat 0.12, decelerating 0.64 from N(9.55, 1.48); the thesis-breaker cell (accel & guide at/above Street) carries 0.08 with day-1 median +5.0; accel & guide below 0.17 with +1.8; C01 joint bull (nights 10.6) P(guide below) 0.49 | `day1-move-5nov/research-log.md` claims 9, 22, §6; `q4-revenue-guide-vs-street/research-log.md` §7 | 2026-09-17 | 2026-09-17 | yes |
| 16 | Reaction base rates: accelerating prints +6.0% day-1 excess mean, decelerating −5.6% (0 of 8 positive post-2022); the three prints where an accelerating bar met an accelerating print averaged +4.2% | `docs/pitch-forecasts/00_BRIEF.md` (reaction base rates); market-implied §10 table 1 | 2026-09-13 | 2026-09-17 | yes (impact) |
| 17 | Alt-data constructions at 147.8m: headline-row plug-in 0.20; seven-row mixture plug-in 0.14, kernel 0.155, bias-corrected normal 0.23; kernel ×1.107 0.17, ×1.231 0.18; parametric N(9.55, 1.70) 0.27; anchored/first-difference family 0.45 (excluded). Alt-data view used 0.22 | `datasets/a09_alt_data_estimates.csv`, `a09_three_views.csv` | 2026-09-17 | 2026-09-17 | yes |
| 18 | Management-delivery construction: 10.0 + N(0.6, 0.5) + N(0, 1.3) → P(≥10.6) 0.50 (grid 0.39–0.64); outside view used = mean(0.375, 0.50) = 0.44 | `datasets/a09_mgmt_delivery_view.csv` | 2026-09-17 | 2026-09-17 | yes |
| 19 | Blend 0.60/0.30/0.10 → 0.316; weight grid: alt-only 0.22, 0.8/0.2/0 0.26, 0.5/0.3/0.2 0.35, 0.5/0.5/0 0.33, outside-only 0.44, market-only 0.54. Final-calibrated normal (R01 = 0.42): centre 9.67, sd 1.70, P(≥10.6) 0.29, E[nights | ≥10.6] 11.67 | `datasets/a09_three_views.csv`, `a09_weight_sensitivity.csv`, `a09_final.json` | 2026-09-17 | 2026-09-17 | yes |
| 20 | Close $167.51 (16 Sep); brief sensitivities (nights, revenue, margin, EPS, multiple) as in R01 claim 21 | `docs/pitch-forecasts/00_BRIEF.md`; `q4-revenue-guide-vs-street/sources/yfinance_abnb_history_20260917T025239Z.csv` | 2026-09-16 | 2026-09-17 | yes (impact) |
| 21 | Web: no public 3Q26 nights consensus; Q3 EPS consensus $2.75 (29 analysts); Finimize/B. Riley RNPL +150bp Q2 after +200bp Q1; final 72-hour check: fall-travel PR only, nothing on QTD bookings | search snippets (§2 queries 13, 14, 18); `risk-july-rnpl-expansion-offsets-lap/sources/finimize_rnpl_expansion_2026.txt` | 2026-09-17 | 2026-09-17 | no |

Newest load-bearing source: 17 Sep (Kalshi fetch, computed tables); alt-data inputs 11–14 Sep. Next real input: the September Inside Airbnb dumps.

## 2. Query Log
1. [repo] brief, `QUESTIONS.md`, skill and format references, example log; C01, S01, C06, C02, C05 logs and JSONs
2. [repo] `docs/q3nowcast/SYNTHESIS.md`; `research/notes/q3nowcast/E_reviews-stays-index.md`, `E_aug_august-batch-refresh.md`, `G_external-sources-q3-read.md`
3. [repo, pandas] `data/processed/q3nowcast/E/`, `E_aug/`: `q3_2026_nowcast.csv`, `backtest_wf_paths.csv`, `backtest_survivor_robustness.csv`, `index_quarterly.csv`, `partial_vs_full_quarter.csv`, `backtest_abnb_quarterly.csv`
4. [repo] `data/processed/q3nowcast_v2/E/` (`_run_log.txt`, `t1_fail_e5_rerun.csv`, `t1_wedge_constancy.csv`), `E_attrition/` (`run_summary.json`, `prereg_results.csv`); `05_backtests/WPK_reviews-index-2023-vintage.md`
5. [repo] `research/notes/2026-09-10_h1-to-h2-bridge.md`; `2026-09-10_nights-baseline-reconciliation.md`
6. [repo] `docs/rnpl-short-audit/00_SYNTHESIS.md`, `01_*.md`; `data/processed/rnpl_short_audit/rnpl_nights_module.csv`; `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` §2.4; `data/processed/overnight2/D/rnpl_statement_ledger.csv`, `D1_prereg_thresholds.csv`
7. [repo] `research/notes/2026-09-13_market-implied-model.md` §10; `data/processed/reverse_dcf/E/` sign history, guide-vs-bar, Street distribution
8. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv` nights rows
9. [repo] `03_insider_mechanics.md` §5.4
10. [repo] grep "WPK-A" / "0.757" (found via `audits/A01-research-audit.md` A01-08 → the WPK note)
11. [Kalshi API] KXABNB open markets — 2026-09-17T03:21:58Z
12. [Polymarket public-search] airbnb — 03:21:58Z
13. WebSearch: Airbnb news (charged to R01)
14. WebSearch: Airbnb third quarter 2026 nights and seats booked estimate analysts preview (charged to R01)
15. WebSearch: Airbnb Reserve Now Pay Later expanded eligible booking types July 2026 (charged to R03)
16. WebFetch: finimize.com RNPL article
17. WebFetch: octagonai.co airbnb-bookings-in-q3
18. WebSearch: Airbnb bookings demand travel trends this week September 2026 (final 72-hour neutral recency check — nothing new; charged to R02)
19. [computed] `datasets/a09_nights_error_distribution.py`

WebSearch calls charged to R02: 1 (query 18); batch total 4 of 15.

## 3. Leading Hypothesis Entities
Airbnb, Nights and Seats Booked, acceleration, Inside Airbnb reviews stays index, Ellie Mertz, Reserve Now Pay Later, Bloomberg MODL 148.9m, Kalshi KXABNB, 5 November 2026

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Acceleration is the modal outcome because the Street (mean 11.5, all 28 ≥ 10.0) and the guide midpoint (11.0) say so | discarded as modal, kept inside the outside view (0.44) and market (0.54) legs | The bar is the guide echoed (claim 11); the guide midpoint has a cushion habit but this bucket was set above the printed rate for the first time (claim 10); every measured outside series decelerates through August (claim 6) |
| The stays index's under-prediction quarters (4Q24, 2Q26) show it misses accelerations, so weight it less for R02 specifically | kept, priced in the sd widening and the 0.30 outside-view weight | Both misses were pre-announced product accelerations; 2 of 10 errors clear −0.55 (claim 3), which is what the plug-in 0.20 already says |
| Anchor on the 2Q26 print and add the index change (10.2–10.7 → P ≈ 0.45) | discarded, reported | First differences lose to naive at 1.45–1.53 (claim 1) |
| A 2Q26 repeat: the guide says "slightly decelerate", the print accelerates 1.2pt | kept as the main path inside the 0.32 | 2Q26 was the one guide miss in the company's favour; the R02 event needs +0.26 on a quarter whose comp is 1.4pt harder than 2Q26's (3Q25 +8.8 vs 2Q25 +7.4) |
| Seats (Experiences and Services) add enough to the KPI to make the acceleration | inside the sd; not separately modelled | Supply +80% on a base management says is not material to the growth rate; a 0.3pt seats contribution is inside one-fifth of the sd |
| The dead band makes 147.5–147.7m a "flat" print that some readers call acceleration | irrelevant to resolution | Convention 1: 147.8m governs |
| A September shock takes the quarter down | inside the sd | Bridge §6: ≤ 1pt, mostly invisible |

## 5. Independent Estimates
- base_rate_estimate: 0.44 — mean of the sequential-change reference class (an acceleration ≥ +0.26pt in 6 of 16 transitions since 3Q22, 0.375; Q2→Q3 3 of 4) and the management-delivery construction (floor 10.0 + cushion N(0.6, 0.5) + error N(0, 1.3), P(≥10.6) 0.50); the naive record (both accelerating guides met, 2 of 2) is noted, not used as a rate
- decomposition_estimate: 0.22 — alt-data distribution at 147.8m: seven-row kernel mixture with errors ×1.107 (0.17; centre 9.45, sd 1.72) averaged with the parametric N(9.55, 1.70) (0.27); the headline row's own 10 errors give 0.20; the anchored/first-difference family (0.45) excluded
- anchor_estimate: 0.54 — Kalshi mid prices interpolated at 147.8m (2026-09-17T03:21:58Z), stale since 29 July, zero liquidity
- anchor_value: 0.539 (Kalshi, 2026-09-17T03:21:58Z, stale-quote caveat)
- final_estimate: 0.32 (credible interval 0.20–0.42)
- final_minus_anchor: −22 points. The anchor is the Street bar, i.e. the guide, quoted on a ladder that has not traded through the guide; the final is 0.6 × the repo's error-measured nowcast + 0.3 × the outside view + 0.1 × the ladder. The three estimates disagree by 32 points; the disagreement is the same one as R01 (stay-date alt-data vs management's July-in-hand booking data) and it is wider here because acceleration needs the index to be wrong by ≥ 0.55pt in the direction it has been wrong only twice in ten quarters, both times on a product step management had pre-announced. Coherence: S01's mixture used P(accel ≥ 10.59) = 0.24; R02 at 0.32 adds the outside-view and market legs; if X01 adopts 0.32 for the breaker state, S01's unconditional median moves by about +0.7 (each 0.1 of accelerating weight ≈ +0.9 on the median per S01 §7) and P(≤ −8) falls by about 0.02; the breaker cell (accel & guide at/above Street) becomes ≈ 0.10 rather than 0.08

## 6. Final Numbers
**Binary.** P(3Q26 Nights and Seats Booked ≥ 147.8m, i.e. ≥ +10.6% y/y) = **0.32**, credible interval **0.20–0.42** (weight grid 0.22–0.35; sd grid at centre 9.55 0.15–0.34).

Sensitivity to the index's error sd (fine print), centre 9.55: sd 1.00 → 0.15, 1.25 → 0.20, 1.48 → 0.24, 1.63 → 0.26, 1.70 → 0.27, 1.82 → 0.28, 2.16 → 0.31, 2.50 → 0.34. At centre 9.2: 0.08–0.29; at 9.9: 0.24–0.39. Unlike R01, the sd matters as much as the centre here because the threshold is 1.05pt above the centre: a wider error is the main route to an acceleration in the alt-data leg.

Extreme-probability gate: not triggered.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Alt-data centre 9.45–9.55 | Team baseline 9.9: alt-data 0.34 → final 0.39; external stack 9.2: 0.20 → 0.31 |
| Index error sd 1.70 | 1.48: 0.31; 2.16: 0.34 |
| Blend 0.60 / 0.30 / 0.10 | Alt-data only: 0.22; 0.8/0.2/0: 0.26; 0.5/0.5/0: 0.33; 0.5/0.3/0.2: 0.35; outside view only: 0.44; market only: 0.54 |
| Management cushion N(0.6, 0.5), error sd 1.3 | Cushion 0.3: delivery view 0.41 → final 0.30; cushion 1.0: 0.61 → 0.33 |
| Sequential base rate on all 16 transitions (0.375) | Q3-only (3/4, Laplace 0.67): final 0.36; post-2023 (0.40): 0.32 |
| Kalshi weight 0.10 | 0: 0.29; 0.25: 0.37 |
| September dumps move the centre ±0.5pt | +0.5: ≈ 0.39; −0.5: ≈ 0.26 |

Pre-mortem ("it is 5 Nov and the print was 147.8m or more"): (1) **2Q26 again**: the July expansion plus the global RNPL ramp lifted booking-date demand the stays index cannot see, exactly the pattern of the two historical under-predictions; priced at 0.32 with the outside view carrying most of it. (2) **The comp was not as hard as the arithmetic says**: 3Q25 (+8.8) contained the US RNPL launch but the letters say adoption ramped through Q4 (over 70% by 4Q25), so the lap inside 3Q26 is partial (+0.35 correction, claim 9). (3) **Management low-balled again**: a 10–12 bucket with an expected 11.5–12 is consistent with the +4.8 and +1.15 beats; the cushion parameter (0.6) is the least-measured input. (4) **Seats**: an Experiences/Services seat contribution of 0.5pt would by itself turn a 10.1 print into 10.6. ("It was below 147.8m"): (5) the outside series were right and the bar was the guide; this is the 0.68 side and the memo's base case. Asymmetry: R02 is the memo's thesis-breaker probability; overstating it dilutes the pitch, understating it is the classic short's error against a company with a 16-print delivery record; 0.32 leaves the breaker as a one-in-three event, which is what the outside data support.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-18 to 2026-09-30 | September Inside Airbnb dumps; re-run E and `datasets/a09_nights_error_distribution.py` | +0.5pt on the centre ≈ +0.07; a centre ≥ 9.9 → 0.39; ≤ 9.2 → 0.26 |
| 2026-10-02 | Prelim memo | Quote 0.32 (0.20–0.42) as the thesis-breaker probability; keep it coherent with X01's breaker state |
| 2026-10-13 | September CPI lodging | ±0.02 |
| ~2026-10-15 | NTTO September; call date fixed | Overseas arrivals improving past −5%: +0.02 |
| ~2026-10-21 | Hilton Q3 | US RevPAR ≥ +6%: +0.03; ≤ +3%: −0.03 |
| 2026-10-28 to 10-30 | BKNG, EXPE Q3 | EXPE room nights accelerating: +0.03; decelerating ≥ 2pt: −0.03 |
| ~2026-11-03 | Marriott Q3 | Half weight of the Hilton rule |
| 2026-11-05 (after close) | 3Q26 release | Resolve on 147.8m; record the sign state for S01/X01 (accelerating / flat / decelerating) |

## 9. Impact
If 3Q26 nights print ≥ 10.6% (E[nights | ≥10.6] = 11.67% under the final-calibrated normal, vs team 9.9), deltas versus the memo's base case (`datasets/a09_impact.csv`):

| Item | Delta if R02 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | **+1.8** (11.67 − 9.9) | conditional mean, claim 19 |
| 4Q26 nights (pts) | **+1.1** (60% persistence) | judgement; an accelerating Q3 has been followed by a Q4 at or above the Q3 rate in 2 of 2 bucket-era cases (3Q23→4Q23 no, 3Q25→4Q25 yes: 1 of 2 on the longer sample) |
| ADR (pts) | 0.0 | independent line; RNPL mix effect belongs to R03 |
| 4Q26 revenue ($M) | **+65** = ⅔ × (1.77 × 1.34m × $176.8 = $419M GBV) × 12.03% + 1.06 × $30M | kernel carry + brief sensitivity |
| FY27 revenue ($M) | **+140** (0.88pt × $158M; 50% persistence) | brief sensitivity |
| FY26 adj. EBITDA margin (pp) | **+0.6** (0.59 × (85 + 65)/7,980 × ½) | brief sensitivity, held costs (flex 0.38 → +0.36) |
| FY27 adj. EBITDA margin (pp) | **+0.6** (0.66 × 0.88) | brief sensitivity |
| FY27 EPS ($) | **+0.13** ($140M × 0.66 × $0.0014) | brief sensitivity |
| Stock ($/share) | **+22.8 vs the base-case day-1** (breaker cells +2.8% vs −8.6% = +11.4pt × $167.51 = $19.1, plus 0.88 × 0.44 × $9.5 = $3.7 on the multiple line); **+13.3 vs the unconditional** (−2.9%) | S01 cells, brief multiple slope; the accelerating-print base rate (+6.0% excess) and the accelerating-bar history (+4.2%) bracket the cell mean |
| **EV = P × impact** | **0.32 × $22.8 = $7.2/share** (vs base case); $4.2 vs unconditional | |
| Materiality | **Material.** R02 is a subset of R01 (0.32 of R01's 0.42), so the two EVs must not be added; the memo should carry R01 as the risk line and R02 as the breaker case inside it | |

## RESUME
Same script and same three choices to attack as R01 (blend weights, the cushion parameter, the exclusion of the anchored rows). For R02 specifically, an auditor should test the sd choice harder: at centre 9.55 the alt-data leg runs 0.15–0.34 across sd 1.0–2.5, and the revintaged literal factor (×1.231) is defensible as the central case (it moves the final by under 0.01 only because the kernel mixture is already wide). Check the 2-of-10 count of walk-forward errors ≤ −0.55 (claim 3) and the Q2→Q3 transition list (claim 12) by hand.
