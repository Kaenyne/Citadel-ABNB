# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A17 with B11 and B12). This question is the lower tail of R16's 4Q26 nights distribution; the model is R16's `r16_model.py` with the threshold turned round (`datasets/b13_model.py`, numpy only, seed 20260917, 400,000 draws, ~5 s; writes `b13_summary.csv`, `b13_views.csv`, `b13_conditional.csv`, `b13_sensitivity.csv`). Nothing in R16's parameters was changed, so X01 has one 4Q26 object: P(≤131.0m) 0.26 here, P(≥134.0m) 0.27 there, mean ≈ 8.3.

## 0. Metadata
- question_name: bonus-q4-nights-print-weak
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § B13)
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
Will 4Q26 Nights and Seats Booked growth print ≤ +7.5% y/y?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if 4Q26 nights ≤ 131.0m. Resolution ~11 Feb 2027.
### Fine Print
(none in the registry.) Conventions adopted, mirroring R16: (1) the resolving number is the press-release "Nights and Seats Booked" for 4Q26 in millions to one decimal; 131.0m resolves Yes (+7.47% on 121.9m), 131.1m resolves No — the title's "+7.5%" is a label, the level 131.0m governs; (2) a restatement of 4Q25 does not move the level; (3) the Feb print on its actual date.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | R16's 4Q26 distribution (reused unchanged): V1 decomposition — 3Q26 print N(9.67, 1.70) (R01 final-calibrated) → 4Q26 = 8.1 + 0.5 × (Q3 − 9.67) + N(0, 1.4) with a 12% short tail at 5.5 ± 1.5, printed to 0.1m; V2 management-guide route — C02's 4Q26 bucket vector (a) 0.21 / (b) 0.19 / (c) 0.39 / (d) 0.17 / (e) 0.04 × bucket midpoint + cushion N(1.2, 1.3); V3 the Street bar 134.0m; blend 0.5 / 0.3 / 0.2. R16 final P(≥134.0m) 0.27 (CI 0.15–0.42) | `../risk-q4-nights-print-meets-street/research-log.md` §5–6; `../risk-q4-nights-print-meets-street/datasets/r16_model.py` | 2026-09-17 | 2026-09-17 | yes |
| 2 | Team 4Q26 nights objects: adopted baseline +8.12% (131.8m; band 8.0–8.86, case A NA-only lap 8.9 at the top, case B global lap 8.1); RNPL unified module base +7.61% (131.2m; bear 6.58 / 129.9m, bull 8.35 / 132.1m — the module's base sits 0.2m above the 131.0m threshold and its bear case 1.1m below); short case +5.0% (128.0m, revenue −6.7% vs base); bridge pattern before laps 10.6 | `data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv`; `data/processed/rnpl_short_audit/rnpl_nights_module.csv` (rows base/bear/bull 4Q26); `data/processed/margin_build/40_line_build/40_short_case_revenue_path.csv`; `research/notes/2026-09-10_h1-to-h2-bridge.md` §1 | 2026-09-11 to 2026-09-15 | 2026-09-17 | yes |
| 3 | Q3 → Q4 nights transitions (letters): 3Q22 25.09 → 4Q22 20.16 (−4.9); 3Q23 13.54 → 4Q23 12.02 (−1.5); 3Q24 8.48 → 4Q24 12.35 (+3.9); 3Q25 8.79 → 4Q25 9.82 (+1.0). Mean step −0.4, range −4.9 to +3.9 (n 4); the two negative steps came off the reopening/2022–23 base, the two positive ones off the 2024–25 base. A 4Q26 print ≤ 7.5 with a 3Q26 print at the nowcast 9.5–9.9 needs a step of −2.0 to −2.4, inside the observed range (2 of 4 steps were more negative) | `data/processed/abnb_driver_history_quarterly.csv` (nights_m_yoy_pct) | 2026-08-06 | 2026-09-17 | yes |
| 4 | Management's 4Q delivery record, 4 of 4 Q4 guides met: 3Q22 "moderate slightly" (25.1 → 20.2); 3Q23 "moderate" (13.5 → 12.0); 3Q24 "higher than Q3" (8.5 → 12.35); 3Q25 "mid-single-digit ... due to the challenging Q4 2024 comparison" (4–6 → 9.82, +3.8 above the top). Bucket era: 4Q25 printed +4.8 over the bucket midpoint, 1Q26 +1.15; directional "stable" guides resolved +0.49, −1.59, −0.81, −0.58, +1.39 vs the prior rate. No Q4 nights guide has been missed to the downside | `data/processed/overnight/02_guidance_ledger.csv` rows 51, 85, 119, 158, 167; R16 log claim 5 | 2026-09-07 | 2026-09-17 | yes |
| 5 | Bloomberg MODL 4Q26 nights: 28 estimates, low 130.0m (+6.6%), mean 134.0m (+9.9%), high 136.0m (+11.6%) (12 Sep screenshot); the low estimate is 1.0m below the threshold, so one of 28 Street estimates already resolves Yes; the bar is the 2Q26 beat carried forward (132.4 → 133.9 on 7 Aug → 134.2) | `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv`, `E_street_nights_estimate_path.csv`; `research/notes/2026-09-13_market-implied-model.md` §10 | 2026-09-13 | 2026-09-17 | yes |
| 6 | At-print Street bar vs print (16 prints 4Q21–2Q26): actual − bar since 2023 mean +0.9%, sd 1.5%, ≥0 in 10 of 12; the worst misses vs the at-print bar were −2.5% (2Q22), −2.1% (4Q21, 3Q22), −1.7% (4Q22). A −2.2% miss of the 134.0m bar is 131.0m — the question's threshold equals the largest at-print miss in the sample, but the bar on 4 Feb 2027 will be the November guide plus cushion, not 134.0m | `data/processed/reverse_dcf/E/E_street_sign_history.csv`; R16 log claim 6 | 2026-09-13 | 2026-09-17 | yes |
| 7 | Pre-registered team card: a 4Q26 nights guide implying ≤7.5% on 5 Nov "supports the lap hypothesis"; ≥9.5% weakens it; 7.6–9.4 inconclusive. C02 puts the "mid single digits / moderate" bucket (d) at 0.17 and "high single digits" (c) at 0.39 | `data/processed/overnight2/D/D1_prereg_thresholds.csv`; `../q4-nights-bucket/research-log.md` §6 | 2026-09-11 / 2026-09-17 | 2026-09-17 | yes |
| 8 | Management tone: Chesky 8 Sep 2026 (Goldman) "Almost every market is accelerating. Almost every country is accelerating"; "Four of the five countries are accelerating"; no quarter-to-date metric disclosed; EXPE 9 Sep "trends we've seen in July were consistent with what we'd seen in the second quarter"; BKNG 9 Sep: US strongest, Europe/Asia under pressure, no new forecast | `data/processed/q3nowcast/G/intra_quarter_commentary.csv` rows dated 2026-09-08/09 | 2026-09-08 | 2026-09-17 | no |
| 9 | Kalshi KXABNBA (FY26 nights & experiences booked), 2026-09-17T08:27:05Z: >565m 0.79/0.99, >570m 0.63/0.99, >575m 0.36/0.76, >580m 0.19/0.99, >585m 0.10/0.16 (volume null): implied FY26 ≈ 572–575m, which with 1H26 304.5m and a Q3 near 148m implies 4Q26 ≈ 120–123m — inconsistent with every model and with the Q3 ladder (KXABNB >146m 0.60 last, >148m 0.53): zero weight (R16, F01, C02 reached the same verdict) | [sources/kalshi_KXABNBA_open_20260917T082705Z.json](sources/kalshi_KXABNBA_open_20260917T082705Z.json), [sources/kalshi_KXABNB_open_20260917T082705Z.json](sources/kalshi_KXABNB_open_20260917T082705Z.json) | 2026-09-17 | 2026-09-17 | no |
| 10 | Monte Carlo (this log): V1 P(≤131.0m) 0.421 (Q4 mean 7.79, sd 1.85; E[Q4 | Yes] 6.07, E[Q4 | No] 9.04; P(≥134.0) 0.122 reproduces R16); V2 0.156 (cushion 0.6: 0.227; 2.0: 0.099); V3 0.024 (N(134.0, 1.5); sd 2.5: 0.119); blend 0.5/0.3/0.2 = 0.262; by Q3 band (V1): <9.0 → 0.63, 9.0–10.0 → 0.43, 10.0–10.6 → 0.33, ≥10.6 → 0.21; V1 with the RNPL module centre 7.61 → 0.52, case A 8.9 → 0.28, Street centre 9.93 no tail → 0.07 | [datasets/b13_summary.csv](datasets/b13_summary.csv), [datasets/b13_views.csv](datasets/b13_views.csv), [datasets/b13_conditional.csv](datasets/b13_conditional.csv), [datasets/b13_sensitivity.csv](datasets/b13_sensitivity.csv) | 2026-09-17 | 2026-09-17 | yes |
| 11 | Brief sensitivities: 1pt of 4Q26 nights ≈ 1.22m ≈ $30M of 4Q26 revenue; 1pt of FY27 revenue growth ≈ $158M; margin 0.59pp per 1pt of 2H26 revenue (held), FY27 0.66; FY27 EPS ≈ $0.0014 per $M EBITDA; 1pt of FY27 nights ≈ $4.90/share (joint solve) or $1.50 (fixed multiple); decelerating prints −5.6% day-1 excess; February Q4 prints positive 6 of 6 | `docs/pitch-forecasts/00_BRIEF.md` | 2026-09-16 | 2026-09-17 | yes |
| 12 | Web (17 Sep, 1 WebSearch): no analyst 4Q26 nights preview beyond the Bloomberg bar; results were the 4Q25/1Q26/2Q26 releases and general 2026 outlook pieces; the batch's neutral 72-hour check (Icons collection, $250M Housing Accelerator, fake-listing purge) carried nothing on Q4 bookings | [sources/web_search_log.md](sources/web_search_log.md) | 2026-09-17 | 2026-09-17 | no |

Newest load-bearing source: the 13–15 Sep repo builds and the 17 Sep R16/C02/R01 logs (2–4 days old against a 147-day window); the 5 Nov print is the next real input.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`; skill files; example log; finished logs R16 (log, JSON, `r16_model.py`, summary/views CSVs), F01, S02, S01 (JSON)
2. [repo] `data/processed/rnpl_short_audit/rnpl_nights_module.csv`; `data/processed/margin_build/40_line_build/40_short_case_revenue_path.csv`; `data/processed/abnb_driver_history_quarterly.csv` (nights y/y)
3. [repo] `data/processed/q3nowcast/G/intra_quarter_commentary.csv` (rows 2026-09-08 to 09-11)
4. [Kalshi API] markets?series_ticker=KXABNBA, KXABNB (2026-09-17T08:27:05Z), saved
5. [computed] `datasets/b13_model.py` (R16 structure, threshold ≤131.0m)
6. WebSearch: Airbnb fourth quarter 2026 bookings outlook
7. WebSearch: Airbnb news this week (batch final 72-hour neutral recency check; charged to B11 — nothing on Q4 bookings; no change)

WebSearch calls charged to B13: 1 (query 6). Batch total 4 of 15.

## 3. Leading Hypothesis Entities
Airbnb, Nights and Seats Booked, Reserve Now Pay Later, ex-NA lap, Bloomberg MODL, 4Q26 shareholder letter, February 2027, Ellie Mertz

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| The RNPL module's base (7.61, band 6.6–8.4) is the centre, so P ≈ 0.5 | kept as a V1 sensitivity (0.52), not the centre | the adopted team baseline is 8.1 (case B) with the module 0.5 below it; R16 and X01 use 8.1, and this log must use the same object |
| The short case (+5.0%) is a scenario with its own weight | kept as the 12% tail at 5.5 ± 1.5 | the short case is a revenue stress path, not a probability-weighted forecast; the tail already carries it (no tail: 0.36; 25% tail: 0.49 on V1) |
| Management guides Q4 on 5 Nov and never delivers below the bucket (V2 ≈ 0.10–0.23) | kept as the outside view, weight 0.3 | 4 of 4 Q4 guides met, bucket-era beats +4.8 / +1.15; but the bucket vector already puts 0.17 on "mid single / moderate", where the print ≤7.5 with P 0.59 |
| The Street's low estimate (130.0m) shows the Street prices the tail | discarded as evidence | one of 28; the mean is the Q2 beat carried forward (claim 5); the Street dispersion is the anchor, not a forecast |
| Q3 → Q4 step base rate (mean −0.4, n 4) as a direct rate | folded into V1 | V1's pass-through (0.5) and residual (1.4) reproduce the step's spread; the two negative steps (2022, 2023) came off reopening comps, the 2026 comp (9.82) is the hardest since 2023 |
| Kalshi FY26 ladder as a live market | discarded | zero volume and inconsistent with the Q3 ladder (claim 9) |
| A Q4 product launch (Winter Release, RNPL for new booking types) lifts Q4 by ≥1pt | inside V1's residual and V2's cushion | R08 puts a quantified 2027 lever at 0.15 |

## 5. Independent Estimates
- base_rate_estimate: 0.18 — management's Q4 delivery route (V2): C02's bucket vector × the record that Airbnb prints at or above its nights bucket; cushion N(1.2, 1.3) gives 0.16, cushion N(0.6, 1.3) (no low-ball) 0.23; taken at 0.18, leaning to the lower cushion because the 3Q26 floor was set with no low-ball and the 4Q26 comp is the hardest of the year
- decomposition_estimate: 0.42 — V1: 3Q26 print N(9.67, 1.70) → 4Q26 = 8.1 + 0.5 × (Q3 − 9.67) + N(0, 1.4), 12% short tail (claim 10); RNPL module centre 7.61 gives 0.52, case A 8.9 gives 0.28, Street centre 9.93 with no tail 0.07
- anchor_estimate: 0.05 — no tradable market (claim 9); the Street's own dispersion around the 134.0m bar gives 0.02 at sd 1.5m (28 estimates, range 130–136) and 0.12 at sd 2.5; gap-adjusted to 0.05 because the bar is the 2Q26 beat carried forward and will be reset by the November guide
- anchor_value: 0.02 (Bloomberg MODL N(134.0m, 1.5m), 28 estimates, 2026-09-12; NO tradable market)
- final_estimate: 0.26 (credible interval 0.14–0.40)
- final_minus_anchor: +0.24 (vs the raw 0.02; +0.21 vs the gap-adjusted 0.05). Justified independently: the anchor is the Street's dispersion around a bar every repo model sits below; the final is R16's 0.5/0.3/0.2 blend of V1 (0.42), V2 (0.16) and V3 (0.02) = 0.262, rounded to 0.26. The three estimates disagree by 37 points for the same reason as in R16: whether the ex-NA lap arithmetic (V1) or management's four-for-four Q4 delivery (V2) is the better read of a quarter that has not started; the blend weights are R16's and are not re-litigated here so that the two tails come from one distribution. Coherence: this blend gives P(≤131.0m) 0.26, P(131.1–133.9m) 0.47, P(≥134.0m) 0.27 (R16), mean ≈ 8.3

## 6. Final Numbers
**Binary.** P(4Q26 Nights and Seats Booked ≤ 131.0m, ≤ +7.47% y/y) = **0.26**, credible interval **0.14–0.40** (weight grid 0.20–0.33; V1 alone 0.42; V2 alone 0.10–0.23; V3 0.02–0.12).
Conditional on the 3Q26 print (V1 structure, scaled ×0.62 to the final): Q3 < 9.0 → ≈ 0.39; 9.0–10.0 → ≈ 0.26; 10.0–10.6 → ≈ 0.21; ≥ 10.6 → ≈ 0.13. Conditional on the 5 Nov 4Q26 bucket (V2 parts): "low double digits" ≈ 0.01; "around 10" ≈ 0.02; "high single digits" ≈ 0.12; "mid single / moderate" ≈ 0.60.
E[4Q26 nights | Yes] ≈ 6.1% (129.3m); E[4Q26 | No] ≈ 9.0%.
One 4Q26 object for X01: P(≤7.47) 0.26 / P(7.47–9.93) 0.47 / P(≥9.93) 0.27.
Extreme-probability gate: not triggered (0.26). Resolution audit: 131.0m printed resolves Yes on the millions to one decimal (convention 1).

## 7. Sensitivity
V1 rows from `datasets/b13_sensitivity.csv`; V2 rows as labelled; the final moves by 0.5× a V1 move, 0.3× a V2 move and 0.2× a V3 move.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Q4 centre 8.1 (case B) | RNPL module 7.61: V1 0.52 → final 0.31; case A 8.9: V1 0.28 → 0.19; Street 9.93 no tail: V1 0.07 → 0.09; short case 5.0 as the centre: V1 0.94 → 0.52 |
| Short tail 12% | none: V1 0.36 → 0.23; 25%: V1 0.49 → 0.30 |
| Q3→Q4 pass-through 0.5 | 0.3: 0.26; 0.8: 0.27 |
| Residual sd 1.4 | 1.0: 0.25; 2.0: 0.28 |
| Q3 centre 9.67 (R01) | external stack 9.2: 0.29; team 9.9: 0.25; naive sd 2.16: 0.27 |
| V2 cushion N(1.2, 1.3) → used 0.18 | 0.6 (no low-ball): 0.23 → final 0.28; 2.0 (4Q25 style): 0.10 → 0.24; C02 vector shifted down (d 0.24): 0.20 → 0.27; shifted up (a 0.30): 0.12 → 0.25 |
| V3 sd 1.5m | 2.5m: 0.12 → final 0.28; 1.0m: 0.002 → 0.26 |
| Blend 0.5 / 0.3 / 0.2 | 0.6/0.3/0.1: 0.30; 0.4/0.4/0.2: 0.24; 0.7/0.2/0.1: 0.33; equal thirds: 0.20; V1 only: 0.42 |
| Joint weak (module 7.61, tail 25%, Q3 9.2; V2 cushion 0.6) | 0.40 |
| Joint strong (case A 8.9, beta 0.8, no tail, Q3 9.9; V2 cushion 2.0) | 0.14 |

Pre-mortem ("it is 11 Feb 2027 and 4Q26 printed ≤131.0m", the Yes side, 0.26): (1) the ex-NA lap bit harder than the pinned 45% split (the RNPL module's bear case, 6.6, is 1.1m below the threshold) — priced through the module sensitivity and the tail; (2) the 3Q26 print came in at 9.0 or below and Q4 followed (V1's <9.0 band gives 0.63; 0.39 scaled); (3) management guided "mid single digits" on 5 Nov with October in hand (C02 0.17) and delivered at the low end; (4) a demand shock (Middle East, US consumer) in November–December, unpriced beyond the residual. ("It printed above", the modal case, 0.74): the four-for-four Q4 delivery record and the 4Q25 precedent, where the same lap-style models under-called Q4 by ~4pts. Asymmetry: the memo's short case is written on nights ≤8.5%; a print ≤7.5% is the case in which the 4Q26 leg is right by a wide margin, and the 0.26 should be quoted as "one in four", not as the base case.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-18 to 2026-10-02 | September Inside Airbnb dumps; R01 re-centred | each −0.5pt on the 3Q26 centre ≈ +0.02 here (pass-through 0.5) |
| 2026-10-02 | Prelim memo freeze | quote 0.26 (0.14–0.40) as the "short case on the number" leg, paired with R16's 0.27 |
| 2026-10-21 to 2026-11-03 | HLT, BKNG, MAR Q3 prints and Q4 guides | BKNG Q4 room-night guide ≤ +3%: +0.02; ≥ +5% or HLT/MAR raising: −0.02 |
| 2026-11-05 | 3Q26 print and the 4Q26 bucket | re-centre on the bucket: "mid single / moderate" → ~0.60; "high single digits" → ~0.12; "around 10" → ~0.02; "low double digits" → ~0.01; an RNPL negative acknowledgement (C07 Yes) +0.05 |
| 2026-11-06 | Bloomberg 4Q26 bar reset | record the new bar; the question stays on 131.0m |
| 2026-12-01 to 2027-01-31 | STR/CoStar Oct–Dec, NTTO, Similarweb; EXPE/BKNG Q4 prints | tighten the Q4 sd from 1.85 to ~1.0 by late January; EXPE room nights decelerating ≥2pt: +0.03 |
| ~2027-02-11 | 4Q26 release | resolve on 131.0m; feed F01, R14, X01 |

## 9. Impact
If Yes (E[4Q26 nights | Yes] ≈ 6.1% vs the team's 8.1; 3Q26 also lower in the joint draw, E[Q3 | Yes] ≈ 9.0 vs 9.9), deltas versus the memo's base case; the RNPL module says a Q4 miss of this size persists (module 1Q27 6.5, FY27 6.4), so persistence into FY27 is taken at 70% (R16 used 60% for the upside):

| Item | Delta if B13 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | **−0.9** (joint draw: E[Q3 | Q4 ≤ 7.47] ≈ 9.0 vs 9.9) | `b13_model.py` structure (pass-through 0.5) |
| 4Q26 nights (pts) | **−2.0** (6.1 − 8.1) | claim 10 |
| ADR (pts) | 0.0 (nights and ADR independent lines; a weaker-demand ADR effect would be negative but is unmeasured) | ADR v3 card |
| 4Q26 revenue ($M) | **−60** (2.0pt × $30M) | claim 11 |
| FY27 revenue ($M) | **−220** (70% persistence: −1.4pt of FY27 nights ≈ 1.4pt of growth × $158M) | claim 11; RNPL module persistence |
| FY26 adj. EBITDA margin (pp) | **−0.27** (0.59pp per 1pt of 2H26 revenue: $60M ≈ 2.0% of Q4 revenue → −1.2pp in Q4 × 0.23 FY weight) | claim 11 |
| FY27 adj. EBITDA margin (pp) | **−0.92** (0.66 × 1.4) | claim 11 |
| FY27 EPS ($) | **−0.20** ($220M × 0.66 = $145M EBITDA × $0.0014) | claim 11 |
| Stock ($/share) | **−8 to −12**: 1.4pt of FY27 nights × $4.90 = −$6.9 (joint solve) plus the Feb-print reaction to a print below every Street estimate but one (decelerating-print base rate −5.6% against the February 6-of-6 positive record; ~−$3 net of what S03 already carries) | claim 11; S03 log |
| **EV = P × impact** | **0.26 × −$10 ≈ −$2.6/share** | |
| Materiality | **Material** (≥ $1/share). Mirror of R16 (+$2.7): the two tails of one distribution; the memo should carry the pair as "the Q4 number is one in four to meet the Street and one in four to print ≤7.5%" | |

RESUME: the next agent (audit response) should re-run `datasets/b13_model.py` (deterministic, ~5 s) and check that it reproduces R16's P(≥134.0m) 0.122 on V1 (column `p_ge_134_check`); attack the same three choices as R16 — the blend weights (V1-only 0.42 to equal-thirds 0.20), the V2 cushion, and whether the Street dispersion belongs in the blend at all; if R16's revision 2 changes any parameter, change it here identically so X01 keeps one 4Q26 object. After 5 Nov, re-centre on the bucket per §8.
