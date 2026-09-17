# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A12 with R10, R11, R15). Reproduction: [datasets/r16_model.py](datasets/r16_model.py) (numpy only, seed 20260917, 400,000 draws, ~5 s; writes `r16_summary.csv`, `r16_views.csv`, `r16_conditional.csv`, `r16_sensitivity.csv`). Consensus-vintage table: [datasets/r16_revenue_consensus_5m_vs_actual.csv](datasets/r16_revenue_consensus_5m_vs_actual.csv) (from the L0 register's DoltHub history).

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
- revision: 1
- agent: fable

## 0b. Question (verbatim)
### Title
Will 4Q26 Nights and Seats Booked growth print ≥ +9.9% y/y (the Bloomberg 4Q26 bar of 134m as of 12 Sep 2026)?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if 4Q26 nights ≥ 134.0m (base 121.9m). Resolution ~11 Feb 2027.
### Fine Print
(none in the registry.) Conventions adopted: (1) the resolving number is the press-release "Nights and Seats Booked" for 4Q26 in millions to one decimal; 134.0m resolves Yes (+9.93% on 121.9m), 133.9m resolves No; the threshold is the fixed 12 Sep bar, not the bar on the print date; (2) if Airbnb restates 4Q25, the printed 4Q26 figure still resolves against 134.0m (the question fixes a level); (3) the Feb print on its actual date.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Bloomberg MODL 4Q26 nights: 28 estimates, low 130.0m (+6.6%), mean 134.0m (+9.9%), high 136.0m (+11.6%); team baseline 132.7m (+8.9%), 131.8m (+8.1%) with the ex-NA lap ("inside the range, lower half", 45th percentile). EEG path of the 4Q26 bar: 132.4m (May) → 132.4 (5 Aug) → 133.9 (7 Aug, +1.1% on the 2Q26 print) → 134.22 (12 Sep legend) | `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv`, `E_street_nights_estimate_path.csv`; `research/notes/2026-09-13_market-implied-model.md` §10 | 2026-09-13 (screenshot 2026-09-12) | 2026-09-17 | yes |
| 2 | Adopted 4Q26 nights baseline +8.12% (131.8m), band 8.0–8.86 (case B WS-D global lap at the pinned 45% ex-NA split; case A NA-only lap 8.9 at the top); RNPL module base 7.61% (131.2m; bear 6.58, bull 8.35); bridge pattern (H1 mean + 2023–25 transition) 10.6 before laps; short case 5.0% | `data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv`; `research/notes/adrv3/N_fx-estimator-and-q4-lap-decisions.md` memo 2; `docs/overnight2/SYNTHESIS.md` §1, §3; `data/processed/rnpl_short_audit/rnpl_nights_module.csv`; `research/notes/2026-09-10_h1-to-h2-bridge.md` §1 | 2026-09-11 to 2026-09-15 | 2026-09-17 | yes |
| 3 | 3Q26 print distribution (R01 final-calibrated): N(9.67, 1.70), P(≥10.0) 0.42; Q3→Q4 pass-through 0.5 (F01 convention); F01's tree (Q4 N(8.1, 1.6) + 12% short tail at 5.5 ± 1.5) gives P(4Q26 ≥ 8.2) 0.42 and P(≥ 9.5) 0.17 | `docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/research-log.md` §6; `q1-27-nights-guide-above-82/research-log.md` claim 14 | 2026-09-17 | 2026-09-17 | yes |
| 4 | Nights history (letters): 3Q24 8.48 → 4Q24 12.35 (+3.9); 3Q25 8.79 → 4Q25 9.82 (+1.0); 3Q23 13.54 → 4Q23 12.02 (−1.5); 3Q22 25.09 → 4Q22 20.16 (−4.9). 4Q25 printed +9.82 against a +12.35 comp; the 4Q26 comp is 9.82 | `data/processed/abnb_driver_history_quarterly.csv` | 2026-08-06 | 2026-09-17 | yes |
| 5 | Q4 nights guides given at Q3 prints, 4 of 4 met: 3Q22 "moderate slightly" (25.1 → 20.2); 3Q23 "moderate" (13.5 → 12.0); 3Q24 "higher than Q3" (8.5 → 12.35); 3Q25 "mid-single-digit ... due to the challenging Q4 2024 comparison" (4–6 → 9.82, +3.8 above the top). Bucket era: 4Q25 printed +4.8 over the bucket midpoint, 1Q26 +1.15; "stable" directional guides resolved +0.49, −1.59, −0.81, −0.58, +1.39 vs the prior rate | `data/processed/overnight/02_guidance_ledger.csv` rows 51, 85, 119, 158, 167; R01 log claim 10 | 2026-09-07 | 2026-09-17 | yes |
| 6 | Street bar at the print vs the printed nights (at-print consensus, 16 prints 4Q21–2Q26): actual minus bar in % = −2.1, +1.2, −2.5, −1.7, −2.1, +0.3, +0.8, +0.4, +1.2, +2.1, −0.2, +0.8, +1.4, +3.7, +0.3, +2.0; since 2023 (12 prints) mean +0.9%, sd 1.5%, ≥0 in 10 of 12; the bar matched the guide's sign in 12 of 13 guided prints; Q4 prints: 4Q22 −1.7%, 4Q23 +0.8%, 4Q24 +2.1%, 4Q25 +3.7% | `data/processed/reverse_dcf/E/E_street_sign_history.csv`, `E_guide_vs_street_sign.csv`; `data/processed/forecast_methods/L0/L0_vintage_register.csv` (AP-…-nights rows) | 2026-09-13 | 2026-09-17 | yes |
| 7 | Revenue consensus 5 months before the print vs the actual (DoltHub weekly history, nearest vintage to print −150 days, 2023Q1–2026Q2, n 14): +8.2, +2.2, +7.2, +2.7, +4.0, −0.4, −3.1, +2.5, −1.7, +1.2, +1.6, +3.7, +6.7, +3.7%; median +2.6%, ≥0 in 11 of 14; the 3-month vintage: median +2.9% — a five-month-ahead Street number is usually below the print for revenue, where the guide-and-cushion mechanism operates; no five-month nights vintage exists in the register | `datasets/r16_revenue_consensus_5m_vs_actual.csv` (from `L0_vintage_register.csv`, vendor DoltHub post-no-preference/earnings) | 2026-09-11 | 2026-09-17 | yes |
| 8 | C02's 4Q26 bucket vector for the 5 Nov letter: (a) ≥10 / "low double digits" 0.21, (b) "around 10" 0.19, (c) "high single digits" 0.39, (d) mid single / "moderate" 0.17, (e) none 0.04 | `docs/pitch-forecasts/questions/q4-nights-bucket/research-log.md` §6 | 2026-09-17 | 2026-09-17 | yes |
| 9 | Pre-registered team card: a 4Q26 nights guide ≤7.5% supports the lap hypothesis, ≥9.5% weakens it, 7.6–9.4 inconclusive; both team cases (8.1, 8.9) sit inside the inconclusive band | `data/processed/overnight2/D/D1_prereg_thresholds.csv`; N memo §3 | 2026-09-11 | 2026-09-17 | no |
| 10 | Kalshi KXABNBA-27FEBNEB (FY26 nights & experiences booked), 2026-09-17T07:55:03Z: >565m bid 0.79 / ask 0.99, >570m 0.63/0.99, >575m 0.36/0.76, >580m 0.19/0.99, >585m 0.10/0.16, >590m 0.01/0.13; volume and open interest null; last prices imply FY26 ≈ 572–575m, which with 1H26 304.5m and a 3Q26 near 148m implies 4Q26 ≈ 120–123m (−1.6 to +0.9% y/y), inconsistent with every model and with the Q3 ladder: zero weight (F01 and C02 reached the same verdict) | https://api.elections.kalshi.com/trade-api/v2/markets?status=open&limit=100&series_ticker=KXABNBA ([sources/kalshi_KXABNBA_open_20260917T075503Z.json](sources/kalshi_KXABNBA_open_20260917T075503Z.json)) | 2026-09-17 | 2026-09-17 | no |
| 11 | Monte Carlo V1 (this log): P(≥134.0m) 0.122 on the base tree; Q4 mean 7.79, sd 1.85; E[Q4 | Yes] 10.72; by Q3 band: <9.0 → 0.03, 9.0–10.0 → 0.08, 10.0–10.6 → 0.13, ≥10.6 → 0.26. V2 guide route (C02 vector × cushion N(1.2, 1.3) over the bucket midpoint): 0.47 (cushion N(0.6, 1.3): 0.37; N(2.0, 1.5): 0.60) | `datasets/r16_views.csv`, `r16_conditional.csv`, `r16_sensitivity.csv` | 2026-09-17 | 2026-09-17 | yes |
| 12 | Management tone: Chesky 8 Sep (Goldman) "Almost every market is accelerating"; Mertz 2Q26 "Even against tougher comps in the back half of the year, we are raising our full year guidance"; the 3Q26 bucket was set at the printed rate with July in hand | R01 log claim 13; F01 log claim 9 | 2026-09-08 | 2026-09-17 | no |
| 13 | Brief sensitivities: 1pt of 4Q26 nights ≈ 1.22m ≈ $30M of 4Q26 revenue; 1pt of FY27 revenue growth ≈ $158M; margin 0.59pp per 1pt of 2H26 revenue (held), FY27 0.66; FY27 EPS ≈ $0.0014 per $M EBITDA; 1pt of FY27 nights ≈ $4.90/share (joint solve) or $1.50 (fixed multiple); February Q4 prints positive 6 of 6; accelerating prints +6.0% day-1 excess | `docs/pitch-forecasts/00_BRIEF.md` | 2026-09-16 | 2026-09-17 | yes |
| 14 | Web (batch-shared recency pass, R01/F01 logs 17 Sep): no analyst 4Q26 nights preview beyond the Bloomberg bar; nothing on quarter-to-date bookings | F01 log claim 13; R01 log claim 23 | 2026-09-17 | 2026-09-17 | no |

Newest load-bearing source: the 13–15 Sep repo builds and the 17 Sep C02/R01 logs (2–4 days old against a 147-day window); the 5 Nov print is the next real input.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`; skill files; example log; finished logs F01, R01, C08, C05, R08
2. [repo] `research/notes/adrv3/N_fx-estimator-and-q4-lap-decisions.md`; `docs/overnight2/SYNTHESIS.md`; `research/notes/nights_quarterly.md`; `data/processed/rnpl_short_audit/rnpl_nights_module.csv`; `data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv`
3. [repo] `research/notes/2026-09-13_market-implied-model.md` §10; `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv`, `E_street_sign_history.csv`, `E_guide_vs_street_sign.csv`, `E_street_nights_estimate_path.csv`
4. [repo] `research/notes/2026-09-10_h1-to-h2-bridge.md` (Q4 rows); `data/processed/abnb_driver_history_quarterly.csv` (nights y/y)
5. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv` nights rows (Q4 guides 3Q22–3Q25); `abnb_guidance_reaction_panel.csv` Q4 rows
6. [repo, pandas] `data/processed/forecast_methods/L0/L0_vintage_register.csv`: nights at-print rows (19), DoltHub revenue history (1,159 rows) → `datasets/r16_revenue_consensus_5m_vs_actual.csv`
7. [Kalshi API] markets?series_ticker=KXABNBA, KXABNB (2026-09-17T07:55:03Z), saved
8. [computed] `datasets/r16_model.py`
9. (no WebSearch charged to R16; the batch's neutral recency pass on Airbnb is in the R01/F01 logs of 17 Sep, and R10's FOMC query is the batch's final 72-hour check)

## 3. Leading Hypothesis Entities
Airbnb, Nights and Seats Booked, Bloomberg MODL, Ellie Mertz, Reserve Now Pay Later, 4Q26 shareholder letter, February 2027

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| The Street's mean is the median of informed estimates, so P ≈ 0.5 | kept as the anchor (V3), weight 0.2 | the 4Q26 bar is 2Q26's beat carried forward one-for-one (claim 1) and every repo model sits 0.9–2.3pt below it (claim 2); the at-print record (10 of 12 beats) is on a bar that already contains the November guide |
| Team decomposition: the ex-NA lap takes Q4 to 8.1 and the bar is out of reach (P ≈ 0.12) | kept as V1, weight 0.5 | sourced dates for the global October-2025 legs; but the 4Q25 precedent (printed 9.8 against a 12.4 comp after a "mid-single" guide) shows the same models under-called Q4 by ~4pts a year ago |
| Management guides Q4 on 5 Nov and delivers with a cushion (V2 ≈ 0.37–0.47) | kept as the outside view, weight 0.3 at 0.40 | 4 of 4 Q4 guides met, bucket-era beats +4.8 / +1.15; the cushion parameter is the least-measured input |
| Revenue five-month consensus record (beaten 11 of 14) transfers to nights | discarded as a direct rate | revenue is guided with a cushion (19/19 beats); nights are guided in words; the register has no five-month nights vintage (claim 7) |
| Kalshi FY26 ladder as a live market | discarded | mutually inconsistent with the Q3 ladder and zero liquidity (claim 10) |
| A Q4 product launch (Winter Release, RNPL for new booking types) lifts Q4 by ≥1pt | inside V1's residual sd and V2's cushion | R08 puts a quantified 2027 lever at 0.15; an unquantified Q4 lift is what the 4Q24 precedent (+3.6 vs pattern) looked like |
| Restatement flips resolution | tail < 1% | convention 2 |

## 5. Independent Estimates
- base_rate_estimate: 0.40 — the management-guide route (V2): C02's bucket vector for the 5 Nov 4Q26 descriptor × the record that Airbnb prints at or above its nights bucket (cushion N(1.2, 1.3) over the midpoint gives 0.47; N(0.6, 1.3) gives 0.37; used 0.40, leaning to the lower cushion because the 3Q26 floor was set with no low-ball and Q4 comps are the hardest of the year)
- decomposition_estimate: 0.12 — V1: 3Q26 print N(9.67, 1.70) → 4Q26 = 8.1 + 0.5 × (Q3 − 9.67) + N(0, 1.4), 12% short tail at 5.5 ± 1.5 (claims 2–3, 11); the RNPL module centre (7.61) gives 0.07, the NA-only case A (8.9) 0.24, the Street centre with no tail 0.51
- anchor_estimate: 0.50 — the bar is the mean of 28 estimates (claim 1); the at-print bar has been beaten 10 of 12 times since 2023 (claim 6), but that bar will be reset by the November guide, so the fixed 134.0m level is not the object that record was scored on; gap-adjusted anchor kept at 0.50
- anchor_value: 0.50 (Bloomberg MODL mean 134.0m, 28 estimates, 2026-09-12; NO tradable market — Kalshi FY26 ladder zero weight)
- final_estimate: 0.27 (credible interval 0.15–0.42)
- final_minus_anchor: −23 points. Justified independently: the anchor is the object under test (the bar), not evidence about the print; every repo model sits below it; the final is the 0.5/0.3/0.2 blend of V1 (0.12), V2 (0.40) and V3 (0.50) = 0.28, rounded to 0.27 for the model-family agreement below 8.9. The three estimates disagree by 38 points and the disagreement is one thing: whether the ex-NA lap arithmetic (sourced dates, one pinned split) or management's four-for-four Q4 delivery record is the better read of a quarter that has not started. Coherence: F01's tree (the decomposition alone) puts P(4Q26 ≥ 9.5) at 0.17, so P(≥ 9.93) ≈ 0.12 there; R16 sits 15 points higher because it adds the guide route and the anchor, which F01 did not price. X01 should use one 4Q26 distribution: the blend here implies a Q4 mixture with mean ≈ 8.3 and P(≥ 9.93) 0.27

## 6. Final Numbers
**Binary.** P(4Q26 Nights and Seats Booked ≥ 134.0m, ≥ +9.93% y/y) = **0.27**, credible interval **0.15–0.42** (weight grid 0.23–0.36; V1 alone 0.12; V2 alone 0.37–0.47).
Conditional on the 3Q26 print (V1 structure, scaled to the final): Q3 < 9.0 → ≈ 0.08; 9.0–10.0 → ≈ 0.18; 10.0–10.6 → ≈ 0.29; ≥ 10.6 → ≈ 0.50. Conditional on the 5 Nov 4Q26 bucket (V2 parts): "low double digits" ≈ 0.85; "around 10" ≈ 0.70; "high single digits" ≈ 0.25; "mid single / moderate" ≈ 0.03.
E[4Q26 nights | Yes] ≈ 10.7% (135.0m); E[4Q26 | No] ≈ 7.5%.
Extreme-probability gate: not triggered (0.27). Resolution audit: 134.0m printed resolves Yes on the millions to one decimal (convention 1).

## 7. Sensitivity
V1 rows from `datasets/r16_sensitivity.csv`; V2 rows as labelled; the final moves by 0.5× a V1 move and 0.3× a V2 move.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Q4 centre 8.1 (case B) | RNPL module 7.61: V1 0.07 → final 0.25; case A 8.9: V1 0.24 → 0.33; Street 9.93 no tail: V1 0.51 → 0.47; bridge no-lap 10.6: V1 0.67 → 0.55 |
| Short tail 12% | none: 0.28; 25%: 0.26 |
| Q3→Q4 pass-through 0.5 | 0.3: 0.26; 0.8: 0.29 |
| Residual sd 1.4 | 1.0: 0.25; 2.0: 0.30 |
| Q3 centre 9.67 (R01) | external stack 9.2: 0.26; team 9.9: 0.28; naive sd 2.16: 0.28 |
| V2 cushion N(1.2, 1.3) → used 0.40 | 0.6 (no low-ball): 0.36 → final 0.26; 2.0 (4Q25 style): 0.60 → 0.33; C02 vector shifted up (a 0.30): 0.56 → 0.32; shifted down (a 0.12): 0.38 → 0.27 |
| Blend 0.5 / 0.3 / 0.2 | 0.6/0.3/0.1: 0.23; 0.4/0.4/0.2: 0.32; 0.7/0.2/0.1: 0.21; equal thirds: 0.34; V1 only: 0.12 |
| Joint bull (case A 8.9, beta 0.8, no tail, Q3 9.9; V2 cushion 2.0) | 0.44 |
| Joint bear (module 7.61, tail 25%, Q3 9.2; V2 cushion 0.6) | 0.15 |

Pre-mortem ("it is 11 Feb 2027 and 4Q26 printed ≥134.0m"): (1) **the ex-NA lap did not bite** — the October-2025 cancellation and fee legs were smaller ex-NA than the pinned 45% split, or the July eligibility expansion and hotels/Experiences seats offset them; this is the 4Q25 precedent (printed 9.8 after a "mid-single" guide against a 12.4 comp) and is what V2 carries; (2) **the 3Q26 print came in at the Street's 11.5 and Q4 followed** (V1's ≥10.6 band gives 0.26 on its own; 0.50 scaled); (3) **management guided "low double digits" again on 5 Nov with October in hand** (C02 0.21) and delivered; (4) a Q4 product or pricing launch lifted bookings (unpriced beyond the residual). ("It printed below"): the modal case (0.73): the lap plus the hardest comp of the year. Asymmetry: the memo's short is written against a Q4 miss of the Street bar; the 0.27 is the probability the memo's 4Q26 leg is simply wrong on the number, and it should be quoted as such rather than buried.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-18 to 2026-10-02 | September Inside Airbnb dumps; R01 re-centred | Each +0.5pt on the 3Q26 centre ≈ +0.02 here (pass-through 0.5) |
| 2026-10-02 | Prelim memo freeze | Quote 0.27 (0.15–0.42); say plainly it is the probability the Q4 leg of the short is wrong on the number |
| 2026-10-21 to 2026-11-03 | Hilton, Booking, Marriott Q3 prints and Q4 guides | BKNG Q4 room-night guide ≥ +5% or HLT/MAR raising: +0.02; BKNG ≤ +3%: −0.02 |
| 2026-11-05 | 3Q26 print and the 4Q26 bucket | Re-centre on the bucket: "low double digits" → ~0.85; "around 10" → ~0.70; "high single digits" → ~0.25; "mid single / moderate" → ~0.03; a bundle figure ≥2.5 pts (C05 (a)) +0.05 |
| 2026-11-06 | Bloomberg 4Q26 bar reset | Record the new bar; the question stays on 134.0m |
| 2026-12-01 to 2027-01-31 | STR/CoStar Oct–Dec, NTTO, Similarweb; EXPE/BKNG Q4 prints (late Jan/early Feb, EXPE reads through) | Tighten the Q4 sd from 1.85 to ~1.0 by late January; EXPE room nights accelerating: +0.03 |
| ~2027-02-11 | 4Q26 release | Resolve on 134.0m; feed F01, R14, X01 |

## 9. Impact
If Yes (E[4Q26 nights | Yes] ≈ 10.7% vs the team's 8.1; 3Q26 also higher in the joint draw, E[Q3 | Yes] ≈ 10.5 vs the team's 9.9), deltas versus the memo's base case:

| Item | Delta if R16 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | **+0.6** (joint draw: E[Q3 | Q4 ≥ 9.93] ≈ 10.5 vs 9.9) | `r16_model.py` structure (pass-through 0.5) |
| 4Q26 nights (pts) | **+2.6** (10.7 − 8.1) | claim 11 |
| ADR (pts) | 0.0 (nights and ADR independent lines; a larger-home mix effect would be positive but is unmeasured) | ADR v3 card |
| 4Q26 revenue ($M) | **+80** (2.6pt × $30M; the kernel recognises most Q4 bookings in Q4/1Q27) | claim 13 |
| FY27 revenue ($M) | **+250** (60% persistence: +1.6pt of FY27 nights ≈ 1.6pt of growth × $158M) | claim 13; judgement on persistence |
| FY26 adj. EBITDA margin (pp) | **+0.35** (0.59pp per 1pt of 2H26 revenue on the 4Q26 $80M ≈ 2.6% of Q4 revenue → +1.5pp in Q4 × 0.23 FY weight) | claim 13 |
| FY27 adj. EBITDA margin (pp) | **+1.05** (0.66 × 1.6) | claim 13 |
| FY27 EPS ($) | **+0.23** ($250M × 0.66 = $165M EBITDA × $0.0014) | claim 13 |
| Stock ($/share) | **+8 to +12**: 1.6pt of FY27 nights × $4.90 = $7.8 (joint solve) plus the Feb-print reaction to a bar met rather than missed (February Q4 prints positive 6 of 6; accelerating-print base rate +6% vs the decelerating −5.6%; ~+$4 net of what S03 already carries) | claim 13; S03 log |
| **EV = P × impact** | **0.27 × $10 ≈ $2.7/share** | |
| Materiality | **Material** (≥ $1/share). This is the second-largest risk line after R01 and the memo should carry it as "the Q4 number itself could meet the Street even if Q3 decelerates" | |

RESUME: the next agent (audit response) should re-run `datasets/r16_model.py` (deterministic) and attack (1) the blend weights (V1-only 0.12 to equal-thirds 0.34 spans the interval); (2) the V2 cushion N(1.2, 1.3), which is the one parameter with no measured Q4-bucket analogue beyond the two bucket-era prints; (3) whether the anchor should be the Street mean (0.50) at all, given the EEG path shows the bar is the Q2 beat carried forward. After 5 Nov, re-centre on the bucket per §8 before anything else; the conditional table in §6 is the audit read.
