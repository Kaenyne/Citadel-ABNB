# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A10). Companion questions: R04 `risk-single-fee-take-rate-accretion-stated`, R07 `risk-adr-residual-persists`. Reused as inputs: C04 `fy26-margin-sentence` (quarterly sentence ledger `datasets/quarterly_margin_sentence_ledger.csv`, Monte Carlo), C09, the margin build (`docs/margin-build/`). Reproduction: `datasets/r05_model.py` (numpy/pandas, seed 20260917, n 400,000; seconds).

## 0. Metadata
- question_name: risk-q3-margin-sandbagged
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § R05)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2026-11-04
- resolution_date: 2026-11-05
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable

## 0b. Question (verbatim)
### Title
Will 3Q26 adjusted EBITDA margin print ≥ 51.5% (i.e., "down slightly" was sandbagged by ≥1.4pp vs 3Q25's 50.09%)?
### Resolution Criteria
Yes if reported 3Q26 adj. EBITDA ÷ revenue ≥ 0.515. Resolution 5 Nov 2026.
### Fine Print
(none beyond the registry header conventions.)

Conventions adopted: (1) the ratio is computed on the press release's adjusted EBITDA and revenue in $ millions (unrounded), not the letter's rounded percentage; 3Q25 base 2,051 / 4,095 = 50.085%; (2) the threshold is +1.415pp above the 3Q25 margin, i.e. +1.9pp above the "down slightly" centre the line build uses (49.59%); (3) if the print date moves, the same release on its actual date; (4) any restatement of 3Q25 does not change the threshold (the question fixes 0.515 on 3Q26's own ratio).

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | 2Q26 letter (6 Aug 2026): "we expect Adjusted EBITDA to increase year-over-year and Adjusted EBITDA Margin to be down slightly compared to Q3 2025, due to timing of investments this year"; FY26 "at least 35.5%"; Q3 revenue $4.69–4.77bn. Mertz on the call: "a material increase in terms of the AI spend over the course of the year"; "some incremental investment" in marketing in 2H | `data/raw/letters/2Q26_d70413dex991.htm`; `data/raw/transcripts/web/2Q26.html` | 2026-08-06 | 2026-09-17 | yes |
| 2 | Q3 margin history: 3Q22 50.52%, 3Q23 53.99%, 3Q24 52.47%, 3Q25 50.09% ($2,051M / $4,095M); 3Q25 was guided "lower than in Q3 2024" and printed −2.4pp. A 51.5% print would be the first Q3 margin expansion since 2023 | `data/processed/abnb_driver_history_quarterly.csv` (adj_ebitda_margin_pct) | 2025-11-06 | 2026-09-17 | yes |
| 3 | Quarterly margin-sentence record (ceilings and points, y/y pts, 3Q22–2Q26, n 10 ceilings after de-duplicating the 2Q25 letter's two Q4 sentences): realised minus ceiling = 3Q22 +1.3 (ceiling "at or slightly below 49%" vs 3Q21 49.2, printed 50.5), 1Q23 −0.8, 2Q23 −0.8, 2Q24 −0.5, 3Q24 −1.5, 4Q24 −2.5, 1Q25 −1.4, 2Q25 +1.2, 3Q25 −2.4, 4Q25 −2.5; exceeded the ceiling at all in 2 of 10, by ≥1.4pp in 0–1 of 10 (3Q22 at +1.3 on the y/y basis, +1.5 on the level basis the ledger records). The 1Q26 "approximately flat" point printed +1.0; the 2Q26 "up" floor printed +1.3 | `datasets/r05_ceiling_record.csv` (from `../fy26-margin-sentence/datasets/quarterly_margin_sentence_ledger.csv`, itself from `data/processed/overnight/02_guidance_ledger.csv`) | 2026-09-17 | 2026-09-17 | yes |
| 4 | Margin build WS22 Q6 and SYNTHESIS §9: "The sentence is not sandbagging": the harness `q_guide_implied` baseline (the sentence as a level) has realised gaps W1 (n 14) mean +0.47pp, median −0.60, above the sentence in 6 of 14; W2 (n 10) mean −0.19pp, median −0.94, above in 4 of 10, last 8 quarters mean −0.86pp; "the quarterly sentence has been missed slightly more often than beaten. There is no empirical licence to override it"; the 60–140bp beat is an FY-floor phenomenon. "Slightly" has meant a mean absolute 1.49pp (0.96 on the two clean cases) | `docs/margin-build/DISCUSSION.md` Q6; `docs/margin-build/SYNTHESIS.md` §9; `data/processed/margin_build/M1_driver_lines/M1_driver_lines_live_guide_reconciled.csv` | 2026-09-14 | 2026-09-17 | yes |
| 5 | 5 Nov card: 3Q26 margin 49.94% (`final-margin|combined|stack_clip`, h=0), 80% band 47.9–52.0 (split conformal qhat80 2.20pp on W1 n 14; 2.08 on 2024Q1+ n 10; Gaussian-from-MAE 1.30pp; the error distribution is fat-tailed: 2023Q4 −3.91, 2024Q1 −2.60 vs median |error| 0.60); PIT bias −0.67 (last five −0.27); bias-corrected 50.21%, which the "down slightly" sentence caps at 50.085%; adj. EBITDA $2,399M, P(beat Street $2,362M) 0.78; "both routes land in 49.9–50.1%"; W1/W2 h=0 MAE 1.13 / 0.79pp, 0.50x / 0.40x the seasonal naive, 0.71x / 0.60x the Street | `data/processed/margin_build/23_final_model/23_card_5nov.csv`, `23_bands.csv`, `23_combination_live.csv`; `docs/margin-build/SYNTHESIS.md` §1–2 | 2026-09-14 | 2026-09-17 | yes |
| 6 | Line build (15 Sep): built from the evidence alone (1H26 10-Q component deltas, 10-K S&M split, hosting commitments, per-booking support statements) costs grow +11.5% in 3Q26 against revenue +17%, i.e. **52.4%** ($2,516M) at the team's $4,804M — this contradicts the sentence; landing the sentence at the guide midpoint needs ~$97M more Q3 cost (70% marketing timing, 30% hosting); base 50.4% / $2,420M on management's budget (cash costs $2,405M, S&M $778–781M +33.5% y/y); "if the sentence is conservative (it has been beaten in 4 of 10 quarters), 3Q26 is the evidence build, $2,516M". M1's driver lines put 3Q26 at 51.57% ($71.5M above the ceiling's cost) before the clip; M2-SARIMA 51.50% on cash costs $2,330M with S&M $708M (+21%), which M2 itself rejects ("recommends weight 0 on it") because 1H26 S&M ran +34%/+26% | `docs/margin-build/notes/40_line_build.md`; `data/processed/margin_build/M1_driver_lines/M1_driver_lines_live_guide_reconciled.csv`; `docs/margin-build/DISCUSSION.md` Q6 (M2) | 2026-09-15 / 2026-09-14 | 2026-09-17 | yes |
| 7 | Revenue-leg arithmetic (this log): a 51.5% print needs cash costs ≤ $2,330M at the team's $4,804M (−$75M vs the $2,405M budget), ≤ $2,301M at the Street's $4,744M (−$104M), ≤ $2,352M at a $4,850M print (−$53M). If the whole gap is S&M, 3Q26 S&M ≤ $706M = +20.7% y/y on 3Q25's $585M (vs the budget's +33.5%, 1H26's +34.1%/+26.4% and the SARIMA line's +21%); at the Street's revenue +15.7%. $48M of S&M = 1.0pp of 3Q26 margin | `datasets/r05_results.csv` rows 21–28; `docs/margin-build/SYNTHESIS.md` §1 item 3 | 2026-09-17 | 2026-09-17 | yes |
| 8 | Street 3Q26: LSEG 49.78% / $2,361.5M (n 36, EBITDA sd $20M, 11 Sep 2026), revenue $4,744M; Bloomberg MODL take-rate mean 18.00. M5: at h=0 the post-2022 Street under-calls the margin by +1.13pp mean (W2, sd 1.41); the beat has shrunk monotonically (2023 +2.1, 2024 +2.8, 2025 +1.1, 1H26 +0.7); analyst dispersion on 3Q26 is at a record low (sd/mean 0.0085), and dispersion is the one conditioning variable that works; M5 LIVE composite 50.19% (50.03–50.30), P(margin beat) 0.62 | `data/processed/margin_build/23_final_model/23_vs_consensus.csv`; `docs/margin-build/notes/M5_street_bias.md` bottom line 4–5 | 2026-09-14 | 2026-09-17 | yes |
| 9 | Regime diagnostics: combination MAE 0.45pp on the last four quarters (Street 0.69, naive 1.81); 1.62 in the 1H25 deceleration shock; 3.06 in 2H23 (the lodging-tax quarter). Error scale is regime-dependent; the recent regime is calm | `data/processed/margin_build/23_final_model/23_diag_shock_vs_calm.csv` | 2026-09-14 | 2026-09-17 | yes |
| 10 | Management's 2026 sentences have run conservative: 1Q26 "approximately flat" → +1.0; 2Q26 "up" → +1.3 (margin +100bp "driven by strong revenue growth and cost efficiencies in operations and support and product development"; support cost per booking −16%). Three consecutive upside surprises to the sentence (2Q25 +1.2, 1Q26 +1.0, 2Q26 +1.3 over a zero floor) are the recent-regime argument for Yes; the counter is that all three sentences were flat/up, not "down slightly", and the last two "down" sentences (3Q25, 4Q25) printed −2.4 and −2.5, exactly as said | `data/processed/overnight/02_guidance_ledger.csv` rows 165, 174, 136; `research/notes/host_only_fee_history_and_elasticity.md` §4 | 2026-08-06 | 2026-09-17 | yes |
| 11 | Budget identity: 1pp of 3Q26 margin = −1.51pp of the 4Q26 margin required for a given FY sentence; a 51.5% Q3 lifts management's internal FY26 by ~+0.5pp and, in the C04 Monte Carlo, moves the "approximately 36%" option from 0.42 toward ~0.45–0.50 with (c) ≥36.5% rising to 0.35 on the 52.4% case | `data/processed/margin_build/23_final_model/23_card_budget_identity.csv`; `../fy26-margin-sentence/research-log.md` §7 | 2026-09-17 | 2026-09-17 | no |
| 12 | Cost-stack Monte Carlo (this log): revenue N(4,804, 50); cash costs = $2,405M budget + N(0, 60) + 0.20 × (revenue − 4,804), with a 25% "slip" component in which $30–97M of the flagged Q3 step (marketing timing / hosting) does not land in Q3: P(≥51.5) 0.19, median 50.24%, P(above the 50.085 ceiling) 0.54. Sensitivities: slip 0% → 0.11, 50% → 0.27; cost sd 40 → 0.13, 80 → 0.24; revenue centre 4,744 → 0.13, 4,770 → 0.16, 4,850 → 0.25. Gaussian on the card: sd 1.72 (qhat80 W1) → 0.18, sd 1.62 (2024Q1+) → 0.17, sd 1.30 (MAE) → 0.12, bias-corrected 50.21 → 0.21; M5 composite N(50.19, 1.34) → 0.16; Street + raw h=0 bias N(50.9, 1.41) → 0.34; line-build base N(50.4, 1.5) → 0.23 | `datasets/r05_model.py`, `r05_results.csv` | 2026-09-17 | 2026-09-17 | yes |
| 13 | Kalshi KXABNB Q3 nights ladder (2026-09-17T03:34:27Z): >146m 0.63/0.66, >148m 0.50/0.55, >150m 0.32/0.36; implied median ≈148.2m (+10.9%). Adjacent only: a nights beat raises revenue and, via the 20% variable-cost term, the margin by ~+0.15pp per $50M. No market on 3Q26 EBITDA or margin (Kalshi, Polymarket scans) | `sources/kalshi_markets_KXABNB_open_20260917T033427Z.json`; `sources/polymarket_search_*_20260917T033427Z.json` | 2026-09-17 | 2026-09-17 | no |
| 14 | Web pass (2 WebSearch calls attributable, one specific): no sell-side 3Q26 margin preview; only the company's 6 Aug language; final 72-hour check (stock −7.4% w/w, Housing Accelerator) carries nothing on Q3 spend | `sources/web_queries_2026-09-17.md` | 2026-09-17 | 2026-09-17 | no |
| 15 | Sensitivities for the impact table: $48M of S&M = 1.0pp of 3Q26 margin; $0.0666 of 3Q26 EPS per 1pp of margin; FY27 EPS ≈ $0.0014 per $M of EBITDA; line-build sensitivity "sentence 'slightly' −0.5pp more → FY27 margin −0.30pp" (symmetric: +1.4pp above the sentence, if run-rate, ≈ +0.8pp FY27; if timing, 0); EBITDA/revenue surprises carry no day-1 information (|t| < 0.6); "margin guide met" correlates +0.35 with day-1 excess (n 20, p 0.14) | `docs/pitch-forecasts/00_BRIEF.md` sensitivities; `data/processed/margin_build/40_line_build/40_sensitivities.csv`; `research/notes/reverse_dcf/C_reaction-function.md` §1; `research/notes/predictive/04_margin-and-reaction.md` §3 | 2026-09-16 / 2026-09-13 | 2026-09-17 | yes (impact only) |

## 2. Query Log
1. [repo] read `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`, skill and schema, example log; C04, C09, C01, C11, S01 logs (read-only)
2. [repo] `docs/margin-build/notes/40_line_build.md` (all); `docs/margin-build/SYNTHESIS.md` §1–2; `notes/M5_street_bias.md` bottom line and backtest; `DISCUSSION.md` Q6 (group A and M2)
3. [repo] `data/processed/margin_build/23_final_model/23_bands.csv`, `23_diag_shock_vs_calm.csv`, `23_card_5nov.csv`, `23_vs_consensus.csv`, `23_combination_live.csv`; `M1_driver_lines/M1_driver_lines_live_guide_reconciled.csv`; `40_line_build/40_short_case_summary.csv`, `40_sensitivities.csv`
4. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv` rows metric ∈ {adj_ebitda_margin_yoy_pts, adj_ebitda_margin_pct} (43 rows, quotes and outcomes); `data/processed/abnb_driver_history_quarterly.csv` (Q3 margins, S&M); `abnb_guidance_reaction_panel.csv` (nq_margin_dir, fy_margin_action)
5. [repo] `../fy26-margin-sentence/datasets/quarterly_margin_sentence_ledger.csv` → `datasets/r05_ceiling_record.csv`
6. [Kalshi API] KXABNB open markets; [Polymarket public-search] airbnb, Airbnb Q3, Airbnb margin, Airbnb ADR (2026-09-17T03:34:27Z)
7. [WebSearch] Airbnb news (neutral, shared)
8. [WebSearch] Airbnb Q3 2026 earnings preview adjusted EBITDA margin analyst expectations (company language only)
9. [python] `datasets/r05_model.py` → `r05_results.csv` (base rate, Gaussian routes, cost-stack Monte Carlo, revenue-leg arithmetic)
10. [WebSearch] Airbnb ABNB this week (final 72-hour neutral recency check, shared, 2026-09-17) — nothing new

WebSearch calls used by this question: 3 of 5 (two shared).

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, 3Q26 adjusted EBITDA margin, "down slightly", timing of investments, sales and marketing, AI hosting spend, LSEG consensus, 3Q26 shareholder letter

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| The sentence is the cost budget; costs land at ~$2,405M and the print is 49.9–50.4% (card and line-build base) | leading (~0.55 of the mass below 50.5) | claims 4, 5, 6: the quarterly sentence has been missed more often than beaten (4 of 10 above), both model routes land at 49.9–50.1, and the Q3 marketing step is management's stated plan |
| The evidence-only build is right (52.4%): the flagged marketing/hosting step is smaller or slips into Q4 | kept (~0.19 via the 25% slip component; this is the whole Yes mass) | claim 6: the 10-Q component deltas and the 10-K split do not add up to a decline; M1 51.6% and SARIMA 51.5% agree on the arithmetic but both are rejected by their own authors because S&M ran +26–34% in 1H26 (claim 6, 7) |
| Recent-regime sandbag: three consecutive upside surprises to the sentence (2Q25, 1Q26, 2Q26) | kept inside the base rate's Laplace term | claim 10: those sentences were flat/up; the last two "down" sentences printed exactly as said (−2.4, −2.5); n 3 |
| A revenue beat carries the margin over 51.5% | discarded as sufficient on its own | claim 7: even a $4,850M print (top of range +1.7%) still needs −$53M of cost vs budget; the variable-cost term returns ~20% of any revenue beat to costs |
| Street + raw h=0 bias (50.9%) is the right centre | discarded as the centre, kept as the upper sensitivity (0.34) | M5's dispersion-conditioned composite (50.19%) is the validated version; the raw bias averages 2023–24 beats that have shrunk to +0.7 in 1H26 (claim 8) |
| A one-off (lodging-tax reserve release, insurance recovery) lifts adjusted EBITDA | inside the cost sd; ~0.02 | adjusted EBITDA excludes lodging-tax reserves; a G&A release of $50M+ would be needed |
| Print date moves / restatement | no effect | conventions (3), (4) |

## 5. Independent Estimates
- base_rate_estimate: 0.17 — reference class "quarterly ceiling sentence exceeded by ≥1.4pp": 0–1 of 10 (3Q22 at +1.3/+1.5 depending on basis), Laplace (1+1)/(10+2) = 0.17; the wider class "printed above the sentence at all" 2 of 10 (0.20) and the 2026 regime (2 of 2 sentences beaten, by ~1pp) argue for the upper half of that, the two exact "down" prints of 2025 for the lower half
- decomposition_estimate: 0.19 — cost-stack Monte Carlo (claim 12): revenue N(4,804, 50), costs = budget $2,405M + N(0, 60) + 20% of the revenue surprise, with a 25% chance that $30–97M of the flagged Q3 step slips out of the quarter; median 50.24%, P(≥51.5) 0.19; the Gaussian routes on the card (0.12–0.21) and the M5 composite (0.16) bracket it
- anchor_estimate: 0.16 — no market prices the margin; the designated anchor is the Street-based object the build validated at h=0: M5 `dispersion_conditioned` composite 50.19% (Street 49.78% + its shrunken, dispersion-scaled bias), sd 1.34pp from its P(margin beat) 0.62 → P(≥51.5) 0.16 (LSEG 11 Sep 2026, n 36)
- anchor_value: 0.16 (M5 LIVE composite on the LSEG 11 Sep consensus; the raw Street 49.78% at its own EBITDA sd $20M gives ~0.00, and Street + unshrunken bias gives 0.34)
- final_estimate: 0.17 (credible interval 0.10–0.27)
- final_minus_anchor: +1 point. NOT_INDEPENDENTLY_DERIVED flag: raised by the arithmetic and answered: the three estimates are built on different objects (the sentence record; the cost stack; the Street plus its bias) and all land at 0.16–0.19, which is agreement, not deference; the final is the decomposition rounded down a point for the two exact "down" prints of 2025.

## 6. Final Numbers
**Binary.** P(3Q26 adj. EBITDA margin ≥ 51.5%) = **0.17**, credible interval **0.10–0.27**.
Companion probabilities from the same model: P(print above the 50.085% ceiling, i.e. the sentence missed to the upside) ≈ 0.54 (the card says 0.54 for a margin beat vs Street and the bias-corrected point sits on the ceiling); P(≥ 51.0%) ≈ 0.27; P(≥ 52.0%) ≈ 0.10; P(≤ 49.0%) ≈ 0.20.
Extreme-probability gate: not triggered.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| 25% chance the flagged Q3 step slips out of the quarter | 0%: 0.11; 50%: 0.27 |
| Cost error sd $60M (≈1.25pp) | $40M: 0.13; $80M: 0.24 |
| Revenue centre $4,804M (bridge v3) | Street $4,744M: 0.13; guide top $4,770M: 0.16; $4,850M: 0.25 |
| Centre = the card (49.94) / budget | evidence-only build 52.4% as the centre (sentence fully sandbagged): ~0.70; line-build base 50.4 at sd 1.5: 0.23 |
| Anchor object = M5 composite (50.19, sd 1.34) | Street + raw h=0 bias (50.9, 1.41): 0.34; raw Street at its own sd: ~0.00 |
| Base-rate class = ceilings exceeded by ≥1.4pp (Laplace 0.17) | "above the sentence at all" 2 of 10 (0.20) with the 2026 regime at 2 of 2: 0.25 |

Pre-mortem ("it is 5 Nov and the margin printed 51.5%+"): (1) the marketing step was a 2H plan, not a Q3 plan, and lands in Q4 with the 2027 launch campaigns (priced at 0.25 slip; also raises C09 "down" and lowers the FY26 sentence risk for the short); (2) the AI hosting "material increase" was a full-year comment already in 1H26's run-rate, so no Q3 step at all (inside the slip component); (3) revenue printed ≥ $4,850M on a nights beat (Kalshi median +10.9%) and support cost per booking fell another 10%+ (revenue sensitivity 0.25); (4) G&A ran down y/y again (1H26 −5.4%) against M1's +5.8% (claim 6's line table: +0.60pp). "It printed 49.5% and the memo called the sentence conservative": the base case; the log keeps 0.17 for that reason. Asymmetry: a confident No that resolves Yes would also flip C04 toward "approximately 36%" or higher and remove the memo's Q4-margin-squeeze argument, so the interval is kept wide to 0.27.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-17 to 2026-10-02 | September Inside Airbnb dumps; nights band refresh; Kalshi KXABNB ladder | Each +$50M of 3Q26 revenue ≈ +0.03 on P; band centred ≥ 10.5 → 0.21 |
| 2026-10-02 | Prelim memo due | Quote 0.17 (0.10–0.27) with the cost arithmetic (S&M ≤ +21% y/y needed) |
| 2026-10-15 to 2026-11-03 | Sell-side previews; BKNG/EXPE Q3 prints (marketing intensity read-across); any management conference remark on Q3 spend or 2027 launches | A peer marketing pause or a management "spend shifted to Q4" remark → 0.25; a confirmed Q3 brand campaign → 0.12 |
| 2026-11-04 | LSEG 3Q26 EBITDA mean re-capture (register) | Street ≥ 50.3% (bias absorbed) → 0.20; unchanged → hold |
| 2026-11-05 (after close) | 3Q26 release: adjusted EBITDA, revenue, S&M line (10-Q) | Resolve; audit read: S&M ≤ $710M with revenue ≥ $4,800M implies the pre-print P should have been ~0.35; S&M ≥ $770M implies ~0.08 |

## 9. Impact
If the event happens (3Q26 margin ≥ 51.5%, taken at 51.5% against the card's 49.94%, +1.6pp / +$75M of EBITDA on $4,804M):

| Line | Delta if Yes | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | a cost outcome; no information on nights (a revenue beat is inside the P, not implied by it) |
| 4Q26 nights (pts) | 0 | — |
| ADR (pts) | 0 | — |
| 4Q26 revenue ($M) | 0 | — |
| FY27 revenue ($M) | 0 | — |
| FY26 adj. EBITDA margin (pp) | +0.5 | +$75M on $14,268M (claim 5, 12); if the step merely slipped into Q4 the FY26 effect is ~0 and the C09 "down" branch rises |
| FY27 adj. EBITDA margin (pp) | +0.4 | half-weight between "timing" (0) and "run-rate" (+0.8pp, the line-build sensitivity −0.30pp per −0.5pp of 'slightly', claim 15, applied to +1.4pp) |
| FY27 EPS ($) | +0.09 | 0.4pp × $15,829M = $63M × $0.0014 (3Q26 EPS itself +$0.10 = 1.6pp × $0.0666) |
| Stock ($/share) | +3 | EBITDA surprises carry no day-1 information (claim 15); the level effect of +$63M of FY27 EBITDA at ~16x on 620m shares ≈ +$1.6, plus a higher probability of the "approximately 36%" FY26 sentence (C04 (b) 0.42 → ~0.48, claim 11) worth ~+$1–2 via the sentence-reaction correlation |
| **EV = P × stock** | **0.17 × $3 ≈ +$0.5/share** | **Immaterial** (< $1/share): the memo can drop it as a stock risk; keep the arithmetic as the reply to "the sentence is sandbagged" |

RESUME: the next agent (audit response) should re-run `datasets/r05_model.py` (seconds), check the ceiling record in `datasets/r05_ceiling_record.csv` against the letters (the 3Q22 row is a level sentence converted to y/y and is the only near-qualifier), and challenge the 25% slip weight and the $60M cost sd, which together move the number between 0.11 and 0.27; the impact table is immaterial at any P below ~0.33, so the audit's effort is better spent on R04 and R07.
