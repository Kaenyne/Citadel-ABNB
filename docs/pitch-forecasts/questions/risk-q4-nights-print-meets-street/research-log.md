# RESEARCH LOG

Revision 2 (2026-09-17, audit response to `audits/A12-research-audit.md`, Fable 5.1; revision 1 of 2026-09-17 was the initial forecast, batch A12 with R10, R11, R15). Reproduction: [datasets/r16_model_v2.py](datasets/r16_model_v2.py) (numpy only, seed 20260917, 1,000,000 draws, ~10 s; writes **`adopted_q4_states_v2.json`** — the one 4Q26 object R16, B13, F01/F02 and X01 must read — plus `r16_v2_summary.csv`, `r16_v2_views.csv`, `r16_v2_conditional.csv`, `r16_v2_sensitivity.csv`). Revision-1 `r16_model.py` and its CSVs are left in place as the audit trail. Consensus-vintage table: [datasets/r16_revenue_consensus_5m_vs_actual.csv](datasets/r16_revenue_consensus_5m_vs_actual.csv).

## 0. Metadata
- question_name: risk-q4-nights-print-meets-street
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § R16)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-16
- close_date: 2027-02-11
- resolution_date: 2027-02-11
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 2
- revised: 2026-09-17
- agent: fable

## 0b. Question (verbatim)
### Title
Will 4Q26 Nights and Seats Booked growth print ≥ +9.9% y/y (the Bloomberg 4Q26 bar of 134m as of 12 Sep 2026)?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if 4Q26 nights ≥ 134.0m (base 121.9m). Resolution ~11 Feb 2027.
### Fine Print
(none in the registry.) Conventions adopted: (1) the resolving number is the press-release "Nights and Seats Booked" for 4Q26 in millions to one decimal; 134.0m resolves Yes (+9.93% on 121.9m), 133.9m resolves No; the threshold is the fixed 12 Sep bar, not the bar on the print date (the 12 Sep legend itself reads 134.22m; the question fixes 134.0m); (2) if Airbnb restates 4Q25, the printed 4Q26 figure still resolves against 134.0m (the question fixes a level); (3) the Feb print on its actual date.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Bloomberg MODL 4Q26 nights: 28 estimates, low 130.0m (+6.6%), mean 134.0m (+9.9%), high 136.0m (+11.6%); team baseline 132.7m (+8.9%), 131.8m (+8.1%) with the ex-NA lap ("inside the range, lower half", 45th percentile). EEG path of the 4Q26 bar: 132.4m (May) → 132.4 (5 Aug) → 133.9 (7 Aug, +1.1% on the 2Q26 print) → 134.22 (12 Sep legend) | `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv`, `E_street_nights_estimate_path.csv`; `research/notes/2026-09-13_market-implied-model.md` §10 | 2026-09-13 (screenshot 2026-09-12) | 2026-09-17 | yes |
| 2 | Adopted 4Q26 nights baseline +8.12% (131.8m), band 8.0–8.86 (case B WS-D global lap at the pinned 45% ex-NA split; case A NA-only lap 8.9 at the top); RNPL module base 7.61% (131.2m; bear 6.58, bull 8.35); bridge pattern (H1 mean + 2023–25 transition) 10.6 before laps; short case 5.0% | `data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv`; `research/notes/adrv3/N_fx-estimator-and-q4-lap-decisions.md` memo 2; `docs/overnight2/SYNTHESIS.md` §1, §3; `data/processed/rnpl_short_audit/rnpl_nights_module.csv`; `research/notes/2026-09-10_h1-to-h2-bridge.md` §1 | 2026-09-11 to 2026-09-15 | 2026-09-17 | yes |
| 3 | **3Q26 print distribution, R01 revision 2 (adopted): N(9.5, 1.70)** — centre = the team nowcast +9.5 (brief rule 6), sd = the fresh-vintage reviews-index RMSE range 1.63–1.82; P(≥10.0) 0.386, P(≥10.6) 0.260; conditional means 11.18 given ≥10.0, 8.44 given <10.0. Revision 1's N(9.67, 1.70) is withdrawn (A09-01). Q3→Q4 pass-through 0.5 (F01 convention) | `docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json`; `audits/A09-audit-response.md` | 2026-09-17 (rev 2 committed 09:13) | 2026-09-17 | yes |
| 4 | Nights history (letters): 3Q24 8.48 → 4Q24 12.35 (+3.9); 3Q25 8.79 → 4Q25 9.82 (+1.0); 3Q23 13.54 → 4Q23 12.02 (−1.5); 3Q22 25.09 → 4Q22 20.16 (−4.9). 4Q25 printed +9.82 against a +12.35 comp; the 4Q26 comp is 9.82 | `data/processed/abnb_driver_history_quarterly.csv` | 2026-08-06 | 2026-09-17 | yes |
| 5 | Q4 nights guides given at Q3 prints, 4 of 4 met: 3Q22 "moderate slightly" (25.1 → 20.2); 3Q23 "moderate" (13.5 → 12.0); 3Q24 "higher than Q3" (8.5 → 12.35); 3Q25 "mid-single-digit ... due to the challenging Q4 2024 comparison" (4–6 → 9.82, +3.8 above the top). Bucket era: 4Q25 printed +4.8 over the bucket midpoint, 1Q26 +1.15; "stable" directional guides resolved +0.49, −1.59, −0.81, −0.58, +1.39 vs the prior rate (mean −0.2, sd 1.3) | `data/processed/overnight/02_guidance_ledger.csv` rows 51, 85, 119, 158, 167; R01 log claim 10 | 2026-09-07 | 2026-09-17 | yes |
| 6 | Street bar at the print vs the printed nights (at-print consensus): **16 of the 19 prints 4Q21–2Q26 are in the panel; 3Q22, 1Q23 and 2Q24 are absent** (from the panel and from the L0 register). Actual minus bar in % = −2.1, +1.2, −2.5, −1.7, −2.1, +0.3, +0.8, +0.4, +1.2, +2.1, −0.2, +0.8, +1.4, +3.7, +0.3, +2.0. **Last 12 prints (2Q23–2Q26): mean +0.87%, sd 1.41, ≥0 in 10 of 12**; a calendar cut at 2023-01-01 gives 13 prints, mean +0.68%, 10 of 13. The bar matched the guide's sign in 12 of 13 guided prints; Q4 prints: 4Q22 −1.7%, 4Q23 +0.8%, 4Q24 +2.1%, 4Q25 +3.7%. **All 19 nights rows in the L0 register carry `vendor = vendor_not_recorded`** (brief rule 5): the panel is the reverse-DCF note's at-print series, not a vendor-stamped LSEG-family consensus, and the memo must not call it that | `data/processed/reverse_dcf/E/E_street_sign_history.csv`, `E_guide_vs_street_sign.csv`; `data/processed/forecast_methods/L0/L0_vintage_register.csv` (metric = nights, 19 rows) | 2026-09-13 | 2026-09-17 | yes |
| 7 | Revenue consensus 5 months before the print vs the actual (DoltHub weekly history, nearest vintage to print −150 days, 2023Q1–2026Q2, n 14): +8.2, +2.2, +7.2, +2.7, +4.0, −0.4, −3.1, +2.5, −1.7, +1.2, +1.6, +3.7, +6.7, +3.7%; median +2.6%, ≥0 in 11 of 14; the 3-month vintage: median +2.9% — a five-month-ahead Street number is usually below the print for revenue, where the guide-and-cushion mechanism operates; no five-month nights vintage exists in the register | `datasets/r16_revenue_consensus_5m_vs_actual.csv` (from `L0_vintage_register.csv`, vendor DoltHub post-no-preference/earnings) | 2026-09-11 | 2026-09-17 | yes |
| 8 | **C02 revision 2** 4Q26 bucket vector for the 5 Nov letter: (a) ≥10 / "low double digits" **0.18**, (b) "around 10" **0.17**, (c) "high single digits" **0.30**, (d) mid single / "moderate" **0.31**, (e) none 0.04 ((c)+(d) = 0.61 is the deceleration-language block). Revision 1 of this log used the C02 revision-1 vector (0.21/0.19/0.39/0.17/0.04), superseded 18 minutes before the rev-1 forecast was written (A12-07) | `docs/pitch-forecasts/questions/q4-nights-bucket/forecasts/2026-09-17-forecast.json` (revision 2, commit `85887c5`) | 2026-09-17 | 2026-09-17 | yes |
| 9 | Pre-registered team card: a 4Q26 nights guide ≤7.5% supports the lap hypothesis, ≥9.5% weakens it, 7.6–9.4 inconclusive; both team cases (8.1, 8.9) sit inside the inconclusive band | `data/processed/overnight2/D/D1_prereg_thresholds.csv`; N memo §3 | 2026-09-11 | 2026-09-17 | no |
| 10 | Kalshi KXABNBA-27FEBNEB (FY26 nights & experiences booked), 2026-09-17T07:55:03Z: >565m bid 0.79 / ask 0.99, >570m 0.63/0.99, >575m 0.36/0.76, >580m 0.19/0.99, >585m 0.10/0.16, >590m 0.01/0.13. **The ladder is populated, not null: `volume_fp` 36–294 contracts per rung (>570m 162, >575m 277, >595m 293, >600m 294), `open_interest_fp` up to 170; but every `updated_time` is 2026-08-04 and `volume_24h_fp` is 0.00 — the last trades pre-date the 6 Aug 2Q26 print that moved the 4Q26 bar from 132.4m to 133.9m.** Last prices imply FY26 ≈ 572–575m, i.e. 4Q26 ≈ 120–123m (−1.6 to +0.9% y/y) with 1H26 304.5m and 3Q26 ≈ 148m: a stale-information artefact, not a disagreement; zero weight (revision 1's "volume and open interest null" read a non-existent field: A12-14, the same parser error as A01-04) | https://api.elections.kalshi.com/trade-api/v2/markets?status=open&limit=100&series_ticker=KXABNBA ([sources/kalshi_KXABNBA_open_20260917T075503Z.json](sources/kalshi_KXABNBA_open_20260917T075503Z.json)) | 2026-09-17 (quotes last updated 2026-08-04) | 2026-09-17 | no |
| 11 | **Adopted mixture (this log, revision 2, `adopted_q4_states_v2.json`)**: 0.5 × V1 + 0.3 × V2 + 0.2 × V3. V1 (decomposition): Q3 ~ N(9.5, 1.70) → Q4 = 8.1 + 0.5 × (Q3 − 9.5) + N(0, 2.0), 12% short tail 5.5 ± 1.5: P(≥134.0m) 0.181, P(≤131.0m) 0.451, mean 7.78, sd 2.29. V2 (guide route): C02 rev-2 vector × (bucket midpoint + cushion N(1.0, 1.3)), "none" → V1: 0.379 / 0.259, mean 9.13. V3 (Street bar): N(9.93, 1.23): 0.514 / 0.025. **Mixture: P(≥134.0m) 0.307, P(131.1–133.9m) 0.384, P(≤131.0m) 0.309; mean 8.61, sd 2.28, median 8.75; p5/p25/p50/p75/p95 = 4.70 / 7.06 / 8.75 / 10.24 / 12.14; E[Q4 | ≥134.0m] 11.16 (135.5m), E[Q4 | <134.0m] 7.48, E[Q4 | ≤131.0m] 5.93; E[Q3 | ≥134.0m] 9.78; corr(Q3, Q4) 0.29** | `datasets/adopted_q4_states_v2.json`, `r16_v2_summary.csv`, `r16_v2_views.csv` | 2026-09-17 | 2026-09-17 | yes |
| 12 | Management tone: Chesky 8 Sep (Goldman) "Almost every market is accelerating"; Mertz 2Q26 "Even against tougher comps in the back half of the year, we are raising our full year guidance"; the 3Q26 bucket was set at the printed rate with July in hand | R01 log claim 13; F01 log claim 9 | 2026-09-08 | 2026-09-17 | no |
| 13 | Brief sensitivities: 1pt of 4Q26 nights ≈ 1.22m ≈ $30M of 4Q26 revenue; 1pt of FY27 revenue growth ≈ $158M (1% of FY27 revenue); margin 0.59pp per 1pt of 2H26 revenue (held), FY27 0.66 held / 0.42 flex; FY27 EPS ≈ $0.0014 per $M EBITDA; 1pt of FY27 nights ≈ $4.90/share (joint solve) or $1.50 (fixed multiple); February Q4 prints positive 6 of 6; accelerating prints +6.0% day-1 excess. **Line build for the margin rows: FY26 revenue $14,268M / adj. EBITDA $5,098M (35.73%); FY27 $15,829M / $5,483M (34.64%)** | `docs/pitch-forecasts/00_BRIEF.md`; `docs/margin-build/SYNTHESIS.md` annual table | 2026-09-16 | 2026-09-17 | yes |
| 14 | Web (batch-shared recency pass, R01/F01 logs 17 Sep): no analyst 4Q26 nights preview beyond the Bloomberg bar; nothing on quarter-to-date bookings | F01 log claim 13; R01 log claim 23 | 2026-09-17 | 2026-09-17 | no |
| 15 | **Observed Q3→Q4 change in nights growth, 2022–2025: −4.93, −1.52, +3.87, +1.03 (mean −0.39, sd 3.74, n 4).** A pure outside view (Q3 ~ N(9.5, 1.70), Δ ~ N(−0.39, 3.74)) gives 4Q26 ~ N(9.1, 4.1) and P(≥134.0m) ≈ 0.42; revision 1's V1 total sd of 1.85 was half the historical scale (A12-12) | `data/processed/abnb_driver_history_quarterly.csv`, `nights_m_yoy_pct` 3Q22–4Q25; audit A12 | 2026-08-06 | 2026-09-17 | yes |
| 16 | Sibling objects that must now read `adopted_q4_states_v2.json`: B13 (rev 1 published P(≤131.0m) 0.26 from a hand-cut V2 at cushion 1.2 and asserted a mixture mean of 8.3); F01 rev 2 (built its own version at cushion 0.9: 0.29 / 0.27, mean 8.70, sd 2.05); F02; X01 | `bonus-q4-nights-print-weak/forecasts/2026-09-17-forecast.json`; `q1-27-nights-guide-above-82/datasets/q4_adopted_v2_summary.csv` | 2026-09-17 | 2026-09-17 | yes |

Newest load-bearing source: the 17 Sep R01 rev-2 and C02 rev-2 objects (0 days old against a 147-day window); the 5 Nov print is the next real input.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`; skill files; example log; finished logs F01, R01, C08, C05, R08
2. [repo] `research/notes/adrv3/N_fx-estimator-and-q4-lap-decisions.md`; `docs/overnight2/SYNTHESIS.md`; `research/notes/nights_quarterly.md`; `data/processed/rnpl_short_audit/rnpl_nights_module.csv`; `data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv`
3. [repo] `research/notes/2026-09-13_market-implied-model.md` §10; `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv`, `E_street_sign_history.csv`, `E_guide_vs_street_sign.csv`, `E_street_nights_estimate_path.csv`
4. [repo] `research/notes/2026-09-10_h1-to-h2-bridge.md` (Q4 rows); `data/processed/abnb_driver_history_quarterly.csv` (nights y/y)
5. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv` nights rows (Q4 guides 3Q22–3Q25); `abnb_guidance_reaction_panel.csv` Q4 rows
6. [repo, pandas] `data/processed/forecast_methods/L0/L0_vintage_register.csv`: nights at-print rows (19), DoltHub revenue history (1,159 rows) → `datasets/r16_revenue_consensus_5m_vs_actual.csv`
7. [Kalshi API] markets?series_ticker=KXABNBA, KXABNB (2026-09-17T07:55:03Z), saved
8. [computed] `datasets/r16_model.py` (revision 1)
9. (no WebSearch charged to R16; the batch's neutral recency pass on Airbnb is in the R01/F01 logs of 17 Sep, and R10's FOMC query is the batch's final 72-hour check)
10. [revision 2, repo] `audits/A12-research-audit.md`; `audits/A12-reproduce.py` run (`py -3.13 -B`, output in `audits/A12-reproduce.stdout.txt`); `risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json`; `q4-nights-bucket/forecasts/2026-09-17-forecast.json` (rev 2); `q1-27-nights-guide-above-82/datasets/q4_adopted_v2_summary.csv`, `f01_model_v2.py` (cushion 0.9, Street sd 1.23); `bonus-q4-nights-print-weak/forecasts/2026-09-17-forecast.json`
11. [revision 2, pandas] `E_street_sign_history.csv` re-read: 16 rows, gaps 3Q22/1Q23/2Q24, last-12 mean +0.874 sd 1.414; L0 register nights rows: 19 × `vendor_not_recorded`
12. [revision 2, json] `sources/kalshi_KXABNBA_open_20260917T075503Z.json` re-parsed on `volume_fp` / `open_interest_fp` / `updated_time`
13. [revision 2, computed] `datasets/r16_model_v2.py` → `adopted_q4_states_v2.json` and the v2 CSVs

## 3. Leading Hypothesis Entities
Airbnb, Nights and Seats Booked, Bloomberg MODL, Ellie Mertz, Reserve Now Pay Later, 4Q26 shareholder letter, February 2027

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| The Street's mean is the median of informed estimates, so P ≈ 0.5 | kept as V3, weight 0.2 (0.51 with the 134.0m rounding) | the 4Q26 bar is 2Q26's beat carried forward one-for-one (claim 1) and every repo model sits 0.9–2.3pt below it (claim 2); the at-print record (10 of 12 beats, mean +0.9%) is on a bar that already contains the November guide; the five-month revenue bar is beaten 11 of 14, which argues V3 is if anything generous to the short (A12) |
| Team decomposition: the ex-NA lap takes Q4 to 8.1 and the bar is out of reach | kept as V1, weight 0.5, **now at residual sd 2.0 (0.18)** | sourced dates for the global October-2025 legs; but the 4Q25 precedent (printed 9.8 against a 12.4 comp after a "mid-single" guide) shows the same models under-called Q4 by ~4pts a year ago, and the historical Q3→Q4 change has sd 3.74 (claim 15): the lap is a mechanism estimate, not a fitted effect, so its residual cannot be half the historical scale |
| Management guides Q4 on 5 Nov and delivers with a cushion | kept as V2, weight 0.3, **C02 rev-2 vector, one cushion N(1.0, 1.3) → 0.38** | 4 of 4 Q4 guides met, bucket-era beats +4.8 / +1.15; the cushion is the least-measured input, so it is one stated value with a sensitivity row, not a hand-cut (rev 1 ran the code at 1.2 and published 0.40, the equivalent of 0.78: A12-01) |
| Revenue five-month consensus record (beaten 11 of 14) transfers to nights | discarded as a direct rate | revenue is guided with a cushion (19/19 beats); nights are guided in words; the register has no five-month nights vintage (claim 7) |
| Kalshi FY26 ladder as a live market | discarded | the ladder's last trade (4 Aug) pre-dates the 6 Aug print that reset the bar (claim 10) |
| Pure sequential outside view (Q4 = Q3 + N(−0.39, 3.74)) as a fourth view | discarded as a view; carried through the wider V1 residual | n = 4 and it ignores the known 9.82 comp; its P(≥134.0m) 0.42 brackets the mixture from above |
| A Q4 product launch (Winter Release, RNPL for new booking types) lifts Q4 by ≥1pt | inside V1's residual and V2's cushion | R08 puts a quantified 2027 lever at 0.15; an unquantified Q4 lift is what the 4Q24 precedent (+3.6 vs pattern) looked like |
| Restatement flips resolution | tail < 1% | convention 2 |

## 5. Independent Estimates
- base_rate_estimate: 0.38 — the management-guide route (V2): C02 rev-2 bucket vector × the record that Airbnb prints at or above its nights bucket, cushion N(1.0, 1.3) over the midpoint (0.6: 0.35; 1.2: 0.40; 2.0/1.5: 0.45; 0: 0.31); the C02 rev-2 vector moves 14 points of mass from "high single digits" to "mid single / moderate", where this route's conditional is 0.01
- decomposition_estimate: 0.18 — V1: 3Q26 print N(9.5, 1.70) (R01 rev 2) → 4Q26 = 8.1 + 0.5 × (Q3 − 9.5) + N(0, 2.0), 12% short tail at 5.5 ± 1.5 (claims 2–3, 11, 15); at the rev-1 residual 1.4 it is 0.11; the RNPL module centre (7.61) gives 0.15, the NA-only case A (8.9) 0.25, the Street centre with no tail 0.47
- anchor_estimate: 0.51 — the bar is the mean of 28 estimates (claim 1) taken as N(134.0m, 1.5m) (0.5 by construction, 0.51 with the one-decimal rounding); the at-print bar has been beaten 10 of 12 times since 2Q23 (claim 6), but that bar will be reset by the November guide, so the fixed 134.0m level is not the object that record was scored on; no gap adjustment
- anchor_value: 0.50 (Bloomberg MODL mean 134.0m, 28 estimates, 2026-09-12; NO tradable market — Kalshi FY26 ladder stale since 4 Aug, zero weight)
- final_estimate: 0.31 (credible interval 0.19–0.44)
- final_minus_anchor: −19 points. Justified independently: the anchor is the object under test (the bar), not evidence about the print; every repo model sits below it; the final is the mixture's own P(≥134.0m) = 0.307 (weights 0.5/0.3/0.2), published unrounded-down: revision 1 hand-cut 0.303 → 0.27 while B13 hand-cut 0.262 → 0.26 from a different cushion, which is how three versions of "one object" came to exist (A12-01). The three estimates disagree by 33 points and the disagreement is one thing: whether the ex-NA lap arithmetic (sourced dates, one pinned split) or management's four-for-four Q4 delivery record is the better read of a quarter that has not started. Audit A12's independent number is 0.30 (0.18–0.44) with E[4Q26 | Yes] 11.1; revision 2 sits 1 point above it because the pass-through reference is re-based to R01 rev 2's 9.5 (the team's 8.1 stays the unconditional centre; the audit's replay kept 9.67 and drifted the centre to 8.0)

## 6. Final Numbers
**Binary.** P(4Q26 Nights and Seats Booked ≥ 134.0m, ≥ +9.93% y/y) = **0.31**, credible interval **0.19–0.44** (weight grid 0.25–0.36; V1 alone 0.18; V2 alone 0.38; V3 0.51).
The adopted object (`datasets/adopted_q4_states_v2.json`): mixture mean 8.61, sd 2.28, median 8.75; **P(≥134.0m) 0.307 / P(131.1–133.9m) 0.384 / P(≤131.0m) 0.309**; E[4Q26 | ≥134.0m] = **11.16% (135.5m)**, E[4Q26 | <134.0m] = 7.48%, E[4Q26 | ≤131.0m] = 5.93%; E[3Q26 | ≥134.0m] = 9.78%. B13 must publish 0.31 (not 0.26) and F01/F02 must replace their 8.70 / 2.05 / 0.29 / 0.27 object with this one.
Conditional on the 3Q26 print (mixture; only V1 carries the Q3 dependence, so the bands are flatter than revision 1's V1-only table): Q3 < 9.0 → 0.26; 9.0–10.0 → 0.30; 10.0–10.6 → 0.32; ≥ 10.6 → 0.38 (each +1pt on R01's centre ≈ +0.03 here). Conditional on the 5 Nov 4Q26 bucket (V2 component): "low double digits" ≈ 0.93; "around 10" ≈ 0.75; "high single digits" ≈ 0.25; "mid single / moderate" ≈ 0.01.
Extreme-probability gate: not triggered (0.31). Resolution audit: 134.0m printed resolves Yes on the millions to one decimal (convention 1).

## 7. Sensitivity
Rows from `datasets/r16_v2_sensitivity.csv` (mixture level; each row re-runs the whole object, so the two tails move together).
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Q4 centre 8.1 (case B) | RNPL module 7.61: 0.28 (B13 tail 0.35); case A 8.9: 0.36 (0.25); Street 9.93 no tail: 0.47 (0.15); bridge no-lap 10.6: 0.54 (0.12) |
| Short tail 12% | none: 0.32; 25%: 0.29 |
| Q3→Q4 pass-through 0.5 | 0.3: 0.30; 0.8: 0.32 |
| V1 residual sd 2.0 | 1.4 (rev 1): 0.28; 2.6: 0.33; 3.74 (raw sequential sd): 0.36 |
| Q3 centre 9.5 (R01 rev 2) | external stack 9.2: 0.30; team 9.9: 0.32; naive sd 2.16: 0.31 |
| V2 cushion N(1.0, 1.3) | 0 (guide at expectation): 0.27; 0.6: 0.29; 1.2: 0.32; 2.0/1.5 (4Q25 style): 0.35 |
| C02 rev-2 vector | rev-1 vector: 0.33; shifted up (a 0.30): 0.35; shifted down (a 0.12, d 0.40): 0.28 |
| Street sd 1.5m | 2.5m: 0.31 (B13 tail 0.33) |
| Blend 0.5 / 0.3 / 0.2 | 0.6/0.3/0.1: 0.27; 0.4/0.4/0.2: 0.33; 0.7/0.2/0.1: 0.25; 0.5/0.5/0: 0.28; equal thirds: 0.36; V1 only: 0.18 |
| Pass-through reference 9.5 | 9.67 kept (audit replay): 0.30 |
| Joint bull (case A 8.9, beta 0.8, no tail, Q3 9.9, cushion 2.0) | 0.46 |
| Joint bear (module 7.61, tail 25%, Q3 9.2, cushion 0.6) | 0.25 |

Pre-mortem ("it is 11 Feb 2027 and 4Q26 printed ≥134.0m"): (1) **the ex-NA lap did not bite** — the October-2025 cancellation and fee legs were smaller ex-NA than the pinned 45% split, or the July eligibility expansion and hotels/Experiences seats offset them; this is the 4Q25 precedent (printed 9.8 after a "mid-single" guide against a 12.4 comp) and is what V2 carries; (2) **the 3Q26 print came in at the Street's 11.5 and Q4 followed** (the ≥10.6 band gives 0.38); (3) **management guided "low double digits" again on 5 Nov with October in hand** (C02 rev 2: 0.18) and delivered (0.93 conditional); (4) a Q4 product or pricing launch lifted bookings, the thing the widened residual now prices. ("It printed below"): the modal case (0.69): the lap plus the hardest comp of the year — and the lower tail (≤131.0m) is as likely as the upper (0.31 vs 0.31): a quarter that has not started, five months out, is genuinely two-tailed. Asymmetry: the memo's short is written against a Q4 miss of the Street bar; the 0.31 is the probability the memo's 4Q26 leg is simply wrong on the number, and it should be quoted as such rather than buried.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-18 to 2026-10-02 | September Inside Airbnb dumps; R01 re-centred | Each +1pt on the 3Q26 centre ≈ +0.03 here (sensitivity rows 9.2 / 9.9); re-run `r16_model_v2.py` with the new `q3_mu`, and re-publish `adopted_q4_states_v2.json` so B13/F01 move with it |
| 2026-10-02 | Prelim memo freeze | Quote 0.31 (0.19–0.44) paired with B13's 0.31 as the two tails of one distribution; say plainly it is the probability the Q4 leg of the short is wrong on the number |
| 2026-10-21 to 2026-11-03 | Hilton, Booking, Marriott Q3 prints and Q4 guides | BKNG Q4 room-night guide ≥ +5% or HLT/MAR raising: +0.02; BKNG ≤ +3%: −0.02 |
| 2026-11-05 | 3Q26 print and the 4Q26 bucket | Re-centre on the bucket: "low double digits" → ~0.93; "around 10" → ~0.75; "high single digits" → ~0.25; "mid single / moderate" → ~0.01; a bundle figure ≥2.5 pts (C05 (a)) +0.05; then collapse the mixture to the V2 component of that bucket plus V1 conditioned on the Q3 print |
| 2026-11-06 | Bloomberg 4Q26 bar reset | Record the new bar; the question stays on 134.0m |
| 2026-12-01 to 2027-01-31 | STR/CoStar Oct–Dec, NTTO, Similarweb; EXPE/BKNG Q4 prints (late Jan/early Feb, EXPE reads through) | Tighten the Q4 sd from 2.3 to ~1.0 by late January; EXPE room nights accelerating: +0.03 |
| ~2027-02-11 | 4Q26 release | Resolve on 134.0m; feed F01, R14, X01 |

## 9. Impact
If Yes (E[4Q26 nights | ≥134.0m] = 11.16% vs the team's 8.1; E[3Q26 | Yes] 9.78 vs 9.5), deltas versus the memo's base case, from the adopted mixture (A12-16), with the margin and EPS rows on ONE flow-through convention (A12-02): costs held (100% of the revenue delta reaches EBITDA; the brief's 0.66pp per point is that convention's margin slope), flex (0.42pp) shown beside it.

| Item | Delta if R16 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | **+0.3** (E[Q3 | Q4 ≥ 134.0m] 9.78 vs 9.5; only V1 carries the joint draw) | `adopted_q4_states_v2.json` conditional means |
| 4Q26 nights (pts) | **+3.1** (11.16 − 8.1) | claim 11 |
| ADR (pts) | 0.0 (nights and ADR independent lines; a larger-home mix effect would be positive but is unmeasured) | ADR v3 card |
| 4Q26 revenue ($M) | **+92** (3.06pt × $30M; the kernel recognises most Q4 bookings in Q4/1Q27) | claim 13 |
| FY27 revenue ($M) | **+290** (60% persistence: +1.8pt of FY27 nights ≈ 1.8pt of growth × $158M, in points of FY27 revenue) | claim 13; judgement on persistence |
| FY26 adj. EBITDA margin (pp) | **+0.41** held ((5,098 + 92) / (14,268 + 92) = 36.14% vs 35.73%); flex +0.26 | claim 13 line build |
| FY27 adj. EBITDA margin (pp) | **+1.18** held ((5,483 + 290) / (15,829 + 290) = 35.82% vs 34.64%); flex +0.75 | claim 13 line build |
| FY27 EPS ($) | **+0.41** held ($290M × $0.0014); flex +$0.26 (revision 1's +$0.23 applied 0.66 as a dollar flow-through on top of the held margin row: withdrawn) | claim 13 |
| Stock ($/share) | **+9 to +13**: 1.8pt of FY27 nights × $4.90 = $8.8 (joint solve) plus the Feb-print reaction to a bar met rather than missed (February Q4 prints positive 6 of 6; accelerating-print base rate +6% vs the decelerating −5.6%; ~+$4 net of what S03 already carries); carried at $11 | claim 13; S03 log |
| **EV = P × impact** | **0.31 × $11 ≈ $3.4/share** | |
| Materiality | **Material** (≥ $1/share). The second-largest risk line after R01; the memo should carry it as "the Q4 number itself could meet the Street even if Q3 decelerates", paired with B13's equal-sized lower tail | |

## 10. Revision notes
| Change | Finding | Effect |
|---|---|---|
| One 4Q26 mixture published (`adopted_q4_states_v2.json`), both tails unrounded, one cushion N(1.0, 1.3); the rev-1 hand-cut V2 (0.40) and the rounded-down 0.27 withdrawn; B13/F01/F02/X01 told to adopt | A12-01 | 0.27 → 0.31; B13's tail 0.26 → 0.31 |
| V2 re-run on the C02 revision-2 vector | A12-07 | −0.02 alone |
| V1 residual sd 1.4 → 2.0; claim 15 (sequential-change sd 3.74) added | A12-12 | +0.03 alone |
| V1 Q3 print re-based to R01 revision 2 N(9.5, 1.70); pass-through reference 9.5 so the team's 8.1 stays the unconditional centre | R01 rev 2 (re-basing obligation named in the audit) | −0.01 alone |
| E[Q4 | Yes] 10.7 → 11.16 and E[Q4 | No] 7.5 → 7.48 from the mixture; §9 rebuilt on them | A12-16 | 4Q26 nights delta +2.6 → +3.1; revenue +$80M → +$92M; FY27 +$250M → +$290M |
| §9 EPS row on the held convention ($290M × 0.0014 = +$0.41), flex pair stated; the 0.66 no longer applied twice | A12-02 | EPS +$0.23 → +$0.41 (held) |
| Claim 10 rewritten: Kalshi fields `volume_fp` / `open_interest_fp` populated, `updated_time` 2026-08-04 (pre-print) is the disqualifier | A12-14 | none |
| Claim 6: 16 of 19 prints, gaps named (3Q22, 1Q23, 2Q24), last-12 sd 1.41, 2023-01-01 cut 10 of 13, L0 vendor field `vendor_not_recorded` flagged | A12-25 | none |
| §5 sentence about F01's "implied ~0.12" deleted (it described F01 revision 1) | A12 coherence ruling | none |
| Sensitivity table rebuilt at the mixture level with both tails; pre-mortem states the two-tailed shape; monitoring row 1 says to re-publish the adopted file | A12-01/12 | — |

RESUME: the next agent should (1) confirm B13 (batch A17) and F01/F02 have adopted `adopted_q4_states_v2.json` (B13 0.31, F01 re-run of `f01_model_v2.py` on this object — its cushion 0.9 / Street sd 1.23 differ from the adopted 1.0 / 1.23); (2) after the September dumps, re-run `r16_model_v2.py` with R01's new centre and re-publish the file; (3) after 5 Nov, collapse the mixture per §8 before anything else; the bucket conditionals in §6 are the audit read.
