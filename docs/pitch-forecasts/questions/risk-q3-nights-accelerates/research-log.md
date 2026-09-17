# RESEARCH LOG

Revision 2 (2026-09-17, audit response to A09, Fable). Revision 1 (2026-09-17, initial forecast, Fable) is superseded where §10 says so. Batch A09 (with R01 and R03; the ledger and query log are repeated in full so this log is self-contained). Reproduction: revision 2 `datasets/a09_v2_print_distribution.py` (the copy that runs is in `../risk-q3-nights-meets-guide/datasets/`; it writes `a09_v2_*.csv` and `a09_v2_final.json` into this folder; seed 20260917); revision 1 `datasets/a09_nights_error_distribution.py` and its `a09_*.csv` left untouched. The adopted print-state object for every downstream user is `../risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json`. Audit: `docs/pitch-forecasts/audits/A09-research-audit.md`; response `audits/A09-audit-response.md`.

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
- revision: 2
- revised: 2026-09-17
- agent: fable

## 0b. Question (verbatim)
### Title
Will 3Q26 nights growth print ≥ +10.6% y/y (an acceleration vs 2Q26's +10.34% under the positioning card's 0.25pt dead band)?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if 3Q26 nights ≥ 147.8m. Resolution 5 Nov 2026. Same derivation rule as R01.
### Fine Print
(R01's fine print applies: derive from the team's nowcast distribution and the walk-forward error distribution of the index, not from web sources; report the implied probability and its sensitivity to the index's error sd.)

Conventions adopted (revision 2): (1) resolves on the printed millions to one decimal: 147.8m is Yes (10.63%), 147.7m is No (10.55%); the 10.6% in the title is the rounded form of the 147.8m threshold and the millions govern; (2) the latent quantity is continuous and the print rounds to one decimal, so "printed ≥ 147.8m" is latent ≥ 147.75m, i.e. growth ≥ 10.5913% on the fixed 133.6m base (A09-18; the printed-exact 10.6287% gives a number 0.007 lower); (3) the "dead band" language is descriptive; the question resolves on the number only; S01's own dead band (accelerating ≥ 10.59%) is a different cut by 0.001pt and carries the same probability to three decimals; (4) the denominator is fixed at 133.6m (R01 convention 3); (5) date-move convention as R01. Question fidelity: reading (a) as in R01 — the headline is the nowcast-derived probability; the outside view and the market are labelled alternatives with zero weight (A09-01).

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Reviews stays index (E): walk-forward RMSE 1.48pp vs naive 2.16 (0.68) over 10 scored quarters 1Q24–2Q26 (W2); W1 (2022Q1+, 14 quarters) 0.71–0.84 vs naive; jackknife 0.63–0.86; r 0.86, r 2024Q1+ 0.42; slope 0.32; first differences lose to naive (1.45–1.53); lag-1 0.87–0.91 | `research/notes/q3nowcast/E_reviews-stays-index.md` §1 items 1, 4; tables 2.6, 2.9 | 2026-09-11 | 2026-09-17 | yes |
| 2 | Seven level rows (E_aug): 10.05, 9.20, 9.23, 9.35, 9.06, 8.57, 8.68 (mean 9.16); anchored-on-2Q26 9.8–10.7 (mean 10.34); "3Q26 nights +9.5%, band 8.5 to 11.0, stands"; the brief and memo carry +9.5% (146.3m). Revision 2 centre 9.5 (revision 1's 9.55 withdrawn, no source) | `research/notes/q3nowcast/E_aug_august-batch-refresh.md` §1 item 5, table 2.5; `data/processed/q3nowcast/E_aug/q3_2026_nowcast.csv`; `00_BRIEF.md` rule 6 | 2026-09-11 / 2026-09-16 | 2026-09-17 | yes |
| 3 | Walk-forward errors (pred − actual, W2, 1Q24…2Q26), headline row: +2.00 +0.78 +0.52 −2.66 +1.35 +1.84 −0.25 +0.56 +1.89 −0.74 (mean +0.53; 7 of 10 over-predictions); **all seven rows under-predicted in 3 of 10 quarters: 4Q24 (−2.7 to −4.8), 3Q25 (−0.06 to −0.98) and 2Q26 (−0.7 to −1.8) (corrected, A09-06)**. A ≥ 147.8m print from the headline row's own demeaned errors at centre 9.5 needs an error ≤ −1.09: 2 of 10 (4Q24, 2Q26). W1 headline: mean +1.64, sd 1.83, RMSE 2.41 (the 2023 normalisation bias) | `data/processed/q3nowcast/E_aug/backtest_wf_paths.csv`; `datasets/a09_v2_windows.csv` | 2026-09-11 | 2026-09-17 | yes |
| 4 | Vintage caveat: 0.683 → 0.757 (RMSE 1.634, honest) / 0.841 (1.816, literal) after re-reading 1Q23 from the fresh 2023 vintage; W1 0.837; the 3Q26 band is not changed. **Revision 2 sd 1.70 = midpoint of 1.634–1.816; the ×1.107 / ×1.231 error scaling is a stress test, not refitted residuals (A09-05)** | `docs/revenue-forecast-strategy/05_backtests/WPK_reviews-index-2023-vintage.md` §2.3, §4, §5; `data/processed/q3nowcast_v2/E/t1_fail_e5_rerun.csv` | 2026-09-14 | 2026-09-17 | yes |
| 5 | The index reads July–August stays (to 17 Aug), not July–September bookings; late-quarter booking shifts (RNPL, lead time) are invisible; **September is 30/92 = 32.6% of the quarter's days; with the August cut-off about 45–48% of the quarter's days are unobserved (A09-20)**; partial-to-full gap +0.02/−0.6 (sd 0.2); NYC, LA, SF, Montreal absent from the August row | `docs/q3nowcast/SYNTHESIS.md` §3 item 3; E note §1 items 1, 3, table 2.8; E_aug §1 item 2 | 2026-09-11 | 2026-09-17 | yes |
| 6 | External: stack +9.2 (6.8–12.0); mixed, not uniform (A09-10): STR US RevPAR +8.2 (July) fading to +4.4/+1.7 by late August then +16.1 in the Labor Day week (calendar artefact), ADR +5.7 → +0.6; TSA QTD −2.65%; CPI lodging 4.9 → 3.1; NTTO overseas −7.0 vs −14.1 (improving); Marriott July +7 (+5 ex World Cup); Expedia July consistent with Q2 (neutral); Chesky 8 Sep "almost every market is accelerating", no number. "Nothing points to the +10.5% or more that the pre-registered card calls the surprise" | `research/notes/q3nowcast/G_external-sources-q3-read.md` §1; `docs/q3nowcast/SYNTHESIS.md` §3 item 1 | 2026-09-11 | 2026-09-17 | no (context) |
| 7 | Bridge: H1→Q3 transition −0.3 (−1.3 to +1.1); 3Q26 9.5 pattern / 10.0 no lap / 8.5 half lap; "No scenario in this bridge produces a Q3 nights acceleration"; "Q3 nights at or above 10.5% is the surprise" | `research/notes/2026-09-10_h1-to-h2-bridge.md` §1 items 1–2, §4 | 2026-09-10 | 2026-09-17 | no (context) |
| 8 | Reconciliation: team model path 9.9 (146.8m), band 8.5–10.3; only WS10's bull case (12.4) clears the guide by more than a rounding; "a deceleration against 2Q26's 10.3% remains the base case in every model except the naive carry-forward" | `research/notes/2026-09-10_nights-baseline-reconciliation.md` §1 | 2026-09-10 | 2026-09-17 | no (context; 9.9 is a centre sensitivity) |
| 9 | RNPL module 3Q26: base 9.49 (8.8–10.3), bull 10.25 (147.3m: July expansion +0.30, US partial-lap +0.34, propensity 2pp), bear 8.76; the July expansion is "the largest single offset to the 3Q26 lap" and unquantified | `docs/rnpl-short-audit/00_SYNTHESIS.md` §1 item 3; `data/processed/rnpl_short_audit/rnpl_nights_module.csv` | 2026-09-11 | 2026-09-17 | no (R03 input) |
| 10 | Guidance ledger, nights guides 2Q22–2Q26: 16 resolved; **13 met, 2 above range, 1 not met in the company's favour (1Q26→2Q26 "slightly decelerate", printed +1.24); 15/16 met or exceeded (corrected coding, A09-07)**; accelerating guides 2Q23→3Q23 ("modest sequential increase", +2.5) and 3Q24→4Q24 ("higher", +3.9) both met (n 2); bucket beats +4.8 and +1.15 over the midpoint on buckets set 1–4pts below the printed rate; the 3Q26 bucket midpoint (11.0) is +0.66 above the printed rate, the first bucket set above it; no comparable sample for a cushion parameter | `data/processed/overnight/02_guidance_ledger.csv`; `audits/A09-reproduce.stdout.txt` | 2026-09-07 | 2026-09-17 | no (alternative view) |
| 11 | Positioning card: Street bar 148.9m = +11.45% is an accelerating bar (fourth in 16 prints; the prior three were all met with a printed acceleration, mean +4.2% excess day-1); 12 of 13 sign matches; 28 of 28 Bloomberg estimates ≥ +10.0% (12 Sep); "the price carries a 3Q26 nights rate of about 10.6 to 11.2%" in proxy units — positioning evidence, not an outcome distribution | `research/notes/2026-09-13_market-implied-model.md` §10; `data/processed/reverse_dcf/E/E_street_sign_history.csv`, `E_street_distribution_vs_team.csv` | 2026-09-13 | 2026-09-17 | no |
| 12 | Sequential-change reference class: a change ≥ +0.25pt occurred in 6 of 16 transitions since 3Q22 (0.375), W1 5/14 (0.36), W2 4/10 (0.40), Q2→Q3 3 of 4 (+0.5, +2.5, −0.2, +1.4). Outside view; zero headline weight | `datasets/a09_v2_alternatives.csv` | 2026-09-17 | 2026-09-17 | no (alternative view) |
| 13 | Guide set 6 Aug with July in hand; named offsets: global RNPL ramp, July expansion, hotels ~3x, first-time bookers +11%, Experiences supply +80% | `docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md` §5.4 | 2026-09-11 | 2026-09-17 | no |
| 14 | Kalshi KXABNB at 2026-09-17T03:21:58Z (**fields corrected, A09-04**): >148m 0.50/0.55 (last 0.53, `volume_fp` 428.14, OI 423.14), >146m 0.63/0.66 (last 0.60, vol 998.66), >150m 0.32/0.36 (last 0.30, vol 590.96); `volume_24h_fp` 0 everywhere; interpolated mids P(≥147.8m) 0.537 (last trades 0.537); the cumulative volumes equal the 29 Jul Octagon snapshot (999/428/591), so no contract has traded since 29 July and the last-trade prices are Octagon's 60/53/30%; zero weight | `sources/kalshi_markets_KXABNB_open_20260917T032158Z.json`; `sources/octagon_kalshi_q3_nights_ladder_asof_2026-07-29.txt` | 2026-09-17 / 2026-07-29 | 2026-09-17 | no (anchor; zero weight) |
| 15 | Downstream: S01 rev 2 uses accelerating (≥10.59) 0.32 / flat 0.085 / decelerating 0.595 from R01/R02 rev 1 (its breaker cell accel & guide at/above 0.112, mean +2.9; accel & guide below 0.209, mean +1.55; E[day-1 \| accelerating] +2.02%); S02 rev 2 uses accel 0.32; C01's sensitivity: nights at 10.6 (joint bull) P(guide below) 0.49. Revision 2 replaces the state weights (accel 0.261) via `adopted_print_states_v2.json` | `day1-move-5nov/forecasts/2026-09-17-forecast.json`, `datasets/s01_v2_cells.csv`, `s01_v2_conditionals.csv`; `close-15dec-2026/forecasts/2026-09-17-forecast.json`; `q4-revenue-guide-vs-street/research-log.md` §7 | 2026-09-17 | 2026-09-17 | yes (coherence) |
| 16 | Reaction base rates (fiscal-quarter windows, audit-reproduced): W1 decelerating prints −5.59% excess (n 8, 0 positive), accelerating +6.04% (n 5); W2 −5.97% (n 5) and +8.83% (n 4); the three prints where an accelerating bar met an accelerating print averaged +4.2% (n 3: +3.7, −5.1, +14.0). Small samples; context for the stock line, which is read from S01 rev 2 | `docs/pitch-forecasts/00_BRIEF.md`; `data/processed/reverse_dcf/C/C_print_panel.csv`; `E_street_sign_history.csv`; `audits/A09-reproduce.stdout.txt` | 2026-09-13 | 2026-09-17 | no (context) |
| 17 | **Revision 2 constructions at 147.75m, centre 9.5** (`a09_v2_constructions.csv`): normal sd 1.70 **0.260 (adopted)**; sd 1.475 0.230; 1.634 0.252; 1.816 0.274; 2.159 0.307; empirical W2 plug-in 0.20, kernel 0.194, ×1.107 stress 0.208; W1 demeaned plug-in 0.214, kernel 0.257; seven-row W2 mixture 0.156; revision 1's alt-data leg 0.218 | `datasets/a09_v2_constructions.csv`, `a09_v2_distribution_grid.csv` | 2026-09-17 | 2026-09-17 | yes |
| 18 | **Labelled alternatives, zero weight**: sequential class 0.375; management-delivery construction 10.0 + N(0.6, 0.5) + N(0, 1.3) → 0.50 (grid 0.40–0.64), an assumption with no comparable sample (A09-07); Kalshi 0.537; revision-1 blend 0.316 (withdrawn); Astra's benchmark at the printed-exact threshold 0.253 | `datasets/a09_v2_alternatives.csv` | 2026-09-17 | 2026-09-17 | no |
| 19 | **Adopted distribution** N(9.5, 1.70): P(≥147.8m) 0.260; P(147.0–147.7m) 0.126; P(<147.0m) 0.614; S01 states accel 0.261 / flat 0.104 / decel 0.636; E[nights \| ≥147.8m] 11.62; E[nights \| <147.8m] 8.75. Revision 1's N(9.67, 1.70) with P(≥10.6) 0.29 vs a blended 0.32 (two objects for one event, A09-11) is superseded | `datasets/a09_v2_final.json`; `../risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json` | 2026-09-17 | 2026-09-17 | yes |
| 20 | Impact inputs: close $167.51; brief sensitivities as R01 claim 21; FY26 base $14,268M / $5,098M, FY27 $15,829M / $5,483M; held-cost identity for margins and EPS with the 0.77-flow-through flex beside it (A09-14); S01 rev-2 state means +2.02 / −0.89 / −4.30 and the base-case cell −4.62 (A09-12, A09-13). **Q3→Q4 persistence: revision 1's "2 of 2 bucket-era cases" was false (3Q22 25.1 → 4Q22 20.2; 3Q23 13.5 → 4Q23 12.0; 3Q25 8.8 → 4Q25 9.8: 1 of 3 since 2022); persistence 0.6 / 0.4 is a labelled judgement (A09-15)** | `00_BRIEF.md`; `23_forecast_annual.csv`; `s01_v2_cells.csv`; `data/processed/reverse_dcf/C/C_print_panel.csv` | 2026-09-16 / 2026-09-17 | 2026-09-17 | yes (impact) |
| 21 | Web: no public 3Q26 nights consensus; Q3 EPS consensus $2.75 (29 analysts); Finimize/B. Riley RNPL +150bp Q2 after +200bp Q1; final 72-hour check: fall-travel PR only, nothing on QTD bookings | search snippets (§2 queries 13, 14, 18); `risk-july-rnpl-expansion-offsets-lap/sources/finimize_rnpl_expansion_2026.txt` | 2026-09-17 | 2026-09-17 | no |
| 22 | Audit A09: benchmark R02 0.25 (14–38) from N(9.5, 1.70) at 147.8m; the headline plug-in count 2/10 and the 6/16 sequential class reproduce; the "2 of 2 persistence" does not | `docs/pitch-forecasts/audits/A09-research-audit.md` | 2026-09-17 | 2026-09-17 | yes (audit trail) |

Newest load-bearing source: 17 Sep (computed tables); alt-data inputs 11–14 Sep. Next real input: the September Inside Airbnb dumps.

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
19. [computed] `datasets/a09_nights_error_distribution.py` (revision 1)
20. [rev 2, repo] `audits/A09-research-audit.md`; S01 rev 2 (`s01_joint_v2.py`, `s01_v2_cells.csv`, `s01_v2_conditionals.csv`); S02 rev 2 (`abnb_path_mixture_v2.py`); C02 rev 2; C06 rev 2
21. [rev 2, repo, pandas] `backtest_wf_paths.csv` both windows, all seven rows; `02_guidance_ledger.csv` outcome counts; `data/processed/reverse_dcf/C/C_print_panel.csv` (3Q→4Q growth pairs); `23_forecast_annual.csv`; Kalshi JSON fixed-point fields
22. [rev 2, computed] `audits/A09-reproduce.py` (exit 0) → `A09-reproduce.stdout.txt`
23. [rev 2, computed] `../risk-q3-nights-meets-guide/datasets/a09_v2_print_distribution.py` → `datasets/a09_v2_*.csv`, `a09_v2_final.json`

WebSearch calls charged to R02: 1 (query 18); batch total 4 of 15; none added in revision 2.

## 3. Leading Hypothesis Entities
Airbnb, Nights and Seats Booked, acceleration, Inside Airbnb reviews stays index, Ellie Mertz, Reserve Now Pay Later, Bloomberg MODL 148.9m, Kalshi KXABNB, 5 November 2026

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Blend the nowcast object with the outside view and the ladder (revision 1's 0.32) | **discarded as the headline (A09-01)**; legs reported as alternatives | The fine print specifies the object; the alternatives (0.375 sequential, 0.50 management delivery as an assumption, 0.537 untraded ladder) are printed beside the headline for the memo |
| Acceleration is the modal outcome because the Street (mean 11.5, all 28 ≥ 10.0) and the guide midpoint (11.0) say so | discarded as modal; visible in the alternatives | The bar is the guide echoed (claim 11); the guide midpoint has a cushion habit but this bucket was set above the printed rate for the first time (claim 10) |
| The stays index's under-prediction quarters (4Q24, 3Q25, 2Q26) show it misses accelerations, so weight it less for R02 specifically | kept, priced in the sd | Two of the three were product accelerations management had pre-announced; 2 of 10 demeaned errors clear −1.09 (claim 3), which is what the plug-in 0.20 says; the normal at sd 1.70 gives 0.26 |
| Anchor on the 2Q26 print and add the index change (10.2–10.7 → P ≈ 0.45) | discarded, reported | First differences lose to naive at 1.45–1.53 (claim 1) |
| Empirical error shape as the object (0.19–0.21) | kept as the check, not adopted | n 10 at 0.1pp granularity; the interval's floor |
| A 2Q26 repeat: the guide says "slightly decelerate", the print accelerates 1.2pt | inside the sd | 2Q26 was the one guide miss in the company's favour; the R02 event needs +0.25 on a quarter whose comp is 1.4pt harder than 2Q26's (3Q25 +8.8 vs 2Q25 +7.4) |
| Seats (Experiences and Services) add enough to the KPI to make the acceleration | inside the sd; not separately modelled | Supply +80% on a base management says is not material to the growth rate; a 0.3pt seats contribution is inside one-fifth of the sd |
| The dead band makes 147.5–147.7m a "flat" print that some readers call acceleration | irrelevant to resolution | Convention 1: 147.8m governs |
| A September shock takes the quarter down | inside the sd | Bridge §6: ≤ 1pt, mostly invisible |

## 5. Independent Estimates
- base_rate_estimate: 0.375 — the sequential-change reference class: an acceleration ≥ +0.25pt in 6 of 16 transitions since 3Q22 (W1 5/14 0.36; W2 4/10 0.40; Q2→Q3 3 of 4) (claim 12); reported as the outside view, zero weight under the fine print; the management-delivery construction (0.50) is an assumption-driven variant of the same view, not independent (claim 18)
- decomposition_estimate: 0.26 — the question's object: latent growth ~ N(9.5, 1.70); P(latent ≥ 147.75m ⇔ growth ≥ 10.5913%) = 0.260 (claims 17, 19). Non-parametric check at the same centre: 0.19–0.21 (W2 empirical), 0.21–0.26 (W1 demeaned)
- anchor_estimate: 0.537 — Kalshi mids interpolated at 147.8m (2026-09-17T03:21:58Z); no trade since 29 July, zero 24h volume (claim 14). Weight zero
- anchor_value: 0.537 (Kalshi, 2026-09-17T03:21:58Z, untraded since 2026-07-29)
- final_estimate: 0.26 (credible interval 0.18–0.34)
- final_minus_anchor: −28 points. The anchor is the Street bar, i.e. the guide, quoted on a ladder that has not traded through the guide; the final is the nowcast object the question specifies. The three estimates disagree by 28 points; it is the same disagreement as R01 (stay-date alt data vs management's July-in-hand booking data) and it is wider here because an acceleration needs the index to be wrong by ≥ 1.1pt in the direction it has been wrong by that much twice in ten quarters, both times on a product step management had pre-announced. Against Astra's 0.25 the difference is the rounding convention (0.007). Coherence: R02 ≤ R01 (0.26 ≤ 0.39) holds; S01's accelerating weight should move 0.32 → 0.26 (its own sensitivity row puts the unconditional median about −0.3 lower and the breaker cell at about 0.09 from 0.11); X01 should use 0.26 for the breaker state

## 6. Final Numbers
**Binary.** P(3Q26 Nights and Seats Booked printed ≥ 147.8m, i.e. ≥ +10.6% y/y) = **0.26** (0.260), credible interval **0.18–0.34** (centre ±0.4pt and sd 1.475–2.159 span 0.17–0.35; the empirical constructions sit at 0.16–0.26).

The same adopted N(9.5, 1.70) as R01 (`adopted_print_states_v2.json`): P(≥147.8m) 0.260, P(147.0–147.7m) 0.126, P(<147.0m) 0.614; on S01's dead band accelerating (≥10.59) 0.261, flat 0.104, decelerating 0.636. E[nights | ≥147.8m] 11.62.

Sensitivity to the index's error sd (fine print), centre 9.5, threshold 147.75m: sd 1.00 → 0.14, 1.25 → 0.19, 1.475 → 0.23, 1.634 → 0.25, **1.70 → 0.26**, 1.816 → 0.27, 1.90 → 0.28, 2.159 → 0.31, 2.50 → 0.33. At centre 9.2: 0.08–0.29; at 9.9: 0.25–0.39; at 10.0: 0.28–0.41. Unlike R01, the sd matters as much as the centre here because the threshold is 1.09pt above the centre: a wider error is the main route to an acceleration in the nowcast object. Both windows (A09-05): W1 demeaned 0.21–0.26; W1 undemeaned 0.09 (bias, not a forecast).

Extreme-probability gate: not triggered. Resolution audit: printed 147.8m governs; the printed-exact threshold gives 0.253; a restated base does not change the event (R01 convention 3).

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Centre 9.5 | 9.9 (model path): 0.34; 10.0: 0.36; 9.2 (external stack): 0.21; 9.0: 0.17 |
| Index error sd 1.70 | 1.475: 0.23; 1.634 / 1.816: 0.25 / 0.27; 2.159: 0.31 |
| Parametric normal as the object | Empirical W2 (plug-in / kernel / ×1.107): 0.20 / 0.19 / 0.21; W1 demeaned 0.21 / 0.26; seven-row mixture 0.16 |
| Rounding convention (latent ≥ 147.75m) | Printed-exact 147.8m = 10.6287%: 0.253 |
| Question read as allowing the revision-1 blend | 0.60/0.30/0.10: 0.32; no-market 0.67/0.33: 0.29; outside view only 0.375–0.50; market only 0.537 (all reported, none adopted) |
| September dumps move the centre ±0.5pt | +0.5: 0.36; −0.5: 0.17 (rule: P = 1 − Φ((10.5913 − c) / 1.70)) |

Pre-mortem ("it is 5 Nov and the print was 147.8m or more"): (1) **2Q26 again**: the July expansion plus the global RNPL ramp lifted booking-date demand the stays index cannot see, the pattern of the three under-prediction quarters; priced through the sd and, for the RNPL path, in R03. (2) **The comp was not as hard as the arithmetic says**: 3Q25 (+8.8) contained the US RNPL launch but adoption ramped through Q4 (over 70% by 4Q25), so the lap inside 3Q26 is partial (+0.35 correction, claim 9). (3) **Management low-balled again**: a 10–12 bucket with an expected 11.5–12 is consistent with the +4.8 and +1.15 beats; this is the alternative view the question excludes and the memo must print beside the number (0.50 under the delivery assumption). (4) **Seats**: an Experiences/Services seat contribution of 0.5pt would by itself turn a 10.1 print into 10.6. ("It was below 147.8m"): (5) the outside series were right and the bar was the guide; this is the 0.74 side and the memo's base case; (6) the empirical shape is real and 0.20 was the better number. Asymmetry: R02 is the memo's thesis-breaker probability; overstating it dilutes the pitch, understating it is the classic short's error against a company with a 15-of-16 delivery record; 0.26 leaves the breaker as a one-in-four event on the nowcast object, and the alternatives say one-in-two.

## 8. Monitoring Calendar
Update rule (A09-21): re-centre the same object, P = 1 − Φ((10.5913 − c) / 1.70): c 8.5 → 0.11; 9.0 → 0.17; 9.2 → 0.21; **9.5 → 0.26**; 9.7 → 0.30; 9.9 → 0.34; 10.0 → 0.36; 10.3 → 0.43; 10.6 → 0.50.

| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-18 to 2026-09-30 | September Inside Airbnb dumps; re-run E and `a09_v2_print_distribution.py` | Re-centre by the rule; +0.5pt ≈ +0.10; a centre ≥ 9.9 → 0.34; ≤ 9.2 → 0.21; re-base S01/S02/X01 from the adopted JSON |
| 2026-10-02 | Prelim memo | Quote 0.26 (0.18–0.34) as the thesis-breaker probability on the nowcast object, with the alternatives (0.375 / 0.50 assumption / 0.537 untraded) beside it; keep it coherent with X01's breaker state |
| 2026-10-13 | September CPI lodging | Context only |
| ~2026-10-15 | NTTO September; call date fixed | Context only |
| ~2026-10-21 | Hilton Q3 | Context only; score-sheet record |
| 2026-10-28 to 10-30 | BKNG, EXPE Q3 | Context only; apply the rule if the nowcast is re-centred |
| ~2026-11-03 | Marriott Q3 | Context only |
| 2026-11-05 (after close) | 3Q26 release | Resolve on 147.8m printed; record the sign state for S01/X01 (accelerating / flat / decelerating) |

## 9. Impact
If 3Q26 nights print ≥ 147.8m (E[nights | ≥147.8m] = 11.62% under the adopted N(9.5, 1.70), vs the memo's base case 9.5), deltas versus the memo's base case (`datasets/a09_v2_impact.csv`, R02 row; same distribution as the probability):

| Item | Delta if R02 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | **+2.1** (11.62 − 9.5) | conditional mean, claim 19 |
| 4Q26 nights (pts) | **+1.3** (60% persistence; **judgement**, A09-15: 1 of 3 accelerating Q3s since 2022 was followed by a Q4 at or above the Q3 rate, which does not estimate a persistence factor) | persistence 0.3 / 0.9 give +0.6 / +1.9 |
| ADR (pts) | 0.0 | independent line; the RNPL mix effect is unquantified (R03) |
| 3Q26 revenue ($M) | +102 (2.12 × $48M); GBV +$502M | brief sensitivity (context) |
| 4Q26 revenue ($M) | **+78** = ⅔ × $502M × 12.03% + 1.27pt × $30M | kernel carry + brief sensitivity |
| FY27 revenue ($M) | **+134** (0.85pt × $158M; 40% persistence, **judgement**) | brief sensitivity |
| FY26 adj. EBITDA margin (pp) | **+0.80 held** ((5,098 + 180) / (14,268 + 180) − 35.73%); +0.51 flex | 23_forecast_annual base; A09-14 |
| FY27 adj. EBITDA margin (pp) | **+0.55 held**; +0.36 flex | same |
| FY27 EPS ($) | **+0.19 held** ($134M × $0.0014); +0.14 flex | A09-14 |
| Stock ($/share), 5 Nov reaction session | **+9.8 vs the R02-No world** (E[day-1 \| accelerating] +2.0% from S01 rev 2 against −3.8% in the non-accelerating draws: +5.85pt × $167.51); +7.2 vs the unconditional (−2.3%); +11.1 vs the memo's base-case cell (−4.6%) | S01 rev-2 `s01_v2_cells.csv`; A09-12, A09-13 |
| Fundamental re-rating line (separate horizon, **not added**) | +$3.5 (0.85pt × 0.44 turns × $9.5) | A09-13 |
| **EV = P × impact** | **0.26 × $9.8 = $2.5/share** (vs the R02-No world); 0.26 × $11.1 = $2.9 vs the base-case cell | published rounded inputs (A09-19) |
| Materiality | **Material.** R02 is a subset of R01 (0.26 of R01's 0.39), so the two EVs must not be added; the memo should carry R01 as the risk line and R02 as the breaker case inside it | |

## 10. Revision notes
| Change | Finding |
|---|---|
| Metadata: revision 2, revised 2026-09-17; reproduction and audit paths in the header | — |
| Headline = the nowcast object (reading (a)); blend withdrawn; final 0.32 → **0.26**; alternatives reported with zero weight | A09-01 |
| Fixed 133.6m denominator; rounding convention (latent ≥ 147.75m = 10.5913%); printed-exact alternative 0.253 | A09-02, A09-18 |
| Kalshi claim 14 rewritten with the real fields; no-trade-since-29-July demonstrated by the volume identity; weight 0 | A09-04 |
| Both windows reported; ×1.107 scaling relabelled a stress test; sd 1.70 sourced | A09-05 |
| Claim 3: three common under-prediction quarters; the threshold count restated on the demeaned errors at centre 9.5 (2/10 clear −1.09) | A09-06 |
| Claim 10 recoded (13/2/1; 15/16); cushion construction relabelled an assumption and moved to the alternatives | A09-07 |
| Claim 6 rewritten as mixed evidence; "every measured outside series decelerates" withdrawn | A09-10 |
| One distribution N(9.5, 1.70) for the probability and the impact (revision 1 used a blended 0.32 beside a normal giving 0.29) | A09-11 |
| Stock line from S01 rev-2 state means conditioned on the R02 event; revision-1 hand-picked cells withdrawn | A09-12 |
| Reaction horizon and re-rating line separated; EV on the reaction line vs the complement | A09-13 |
| Margins as annual ratios under held costs (FY26 +0.80, FY27 +0.55) with the flex beside them; EPS +0.19 held | A09-14 |
| "2 of 2 bucket-era cases" deleted; persistence labelled judgement with a sensitivity file | A09-15 |
| EV from the published rounded P and impact ($2.5, not $7.2) | A09-19 |
| Claim 5: September = 32.6% of the quarter's days | A09-20 |
| One monitoring update rule; external-series rows demoted to context | A09-21 |
| Centre 9.55 → 9.5; deltas versus the memo's own 3Q26 base (9.5, not 9.9) | response |

## RESUME
Same object and same script as R01 (`../risk-q3-nights-meets-guide/datasets/a09_v2_print_distribution.py`). For R02 an auditor should test the sd choice and the parametric form hardest: at centre 9.5 the object runs 0.23–0.31 across sd 1.475–2.159, and the empirical W2 shape says 0.20. When the September dumps land, re-run E, re-centre by the §8 rule, and re-base S01's accelerating weight and X01's breaker state from `adopted_print_states_v2.json`.
