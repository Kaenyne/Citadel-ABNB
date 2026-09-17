# RESEARCH LOG

Revision 2 (2026-09-17, audit-response revision of the 2026-09-17 initial forecast, Fable 5.1, batch A13 with R12 and R13; responds to `docs/pitch-forecasts/audits/A13-research-audit.md`, response in `audits/A13-audit-response.md`). Reproduction: `datasets/r14_model.py` Part A (unchanged; `r14_base_rates.json` holds the record, the S1 residual and the Feb event sd) and `datasets/r14_model_v2.py` (numpy/scipy, seed 20260917, 400,000 draws, ~40 s with sensitivities; outputs `r14_v2_summary.json`, `r14_v2_sensitivity.csv`, `r14_v2_stdout.txt`). Revision 1's `r14_model.py` and its outputs are left untouched. What changed: the Q4 premium was being added to cells that already contained the Q4 prints (fixed with ex-Q4 cells and a leave-one-out premium), the 1Q27 guide probability was F02 revision 1's (now revision 2's 0.45), the post-2022 record was mis-transcribed (2 of 14, not 3), and the impact table was one-sided (§10).

## 0. Metadata
- question_name: risk-feb-print-up-day
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § R14)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2027-02-11
- resolution_date: 2027-02-12
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 2
- revised: 2026-09-17
- agent: fable

## 0b. Question (verbatim)
### Title
Will ABNB's close-to-close return on the first session after the 4Q26 print be ≥ +5%?
### Resolution Criteria
Yes if the day-1 return ≥ 0.05. Resolution ~12 Feb 2027.
### Fine Print
(none in the registry beyond the resolution sentence; registry conventions: "Day-1 return = close on the first trading session after the release divided by the close on the release day, minus one"; "Feb print" = the 4Q26 results release and call, expected ~11 Feb 2027)

Conventions adopted: (1) raw close-to-close (not QQQ-excess), Nasdaq official closes via yfinance; (2) the release is expected after the close on Thursday 11 Feb 2027 (every Airbnb Q4 release since 2021 has been after the close in the second half of February or mid-February: 25 Feb 2021, 15 Feb 2022, 14 Feb 2023, 13 Feb 2024, 13 Feb 2025, 12 Feb 2026); the resolving session is the first full session after the actual release; a pre-market release would make that day's close the object; (3) ≥ 5.00% on the unrounded ratio; (4) a halt on the reaction day delays, not changes, the object; (5) the forecast is unconditional on the 5 Nov print (the 5 Nov branches are inside the mixture through the 3Q26 nights draw).

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Q4-print day-1 raw returns: 4Q20 +13.3, 4Q21 +3.6, 4Q22 +13.4, 4Q23 −1.7, 4Q24 +14.4, 4Q25 +4.6 (excess +12.9, +3.7, +12.6, −2.8, +14.0, +4.4): positive 5 of 6 (raw and excess); ≥ +5% raw **3 of 6** (4Q20, 4Q22, 4Q24); ≥ +3.5% 5 of 6; mean +7.9, median +9.0. The memo's "The Q4 print has been positive on day 1 in 6 of 6 observations" (line 77) and the brief's "February Q4 prints positive 6 of 6" are the calendar-February excess-return count (09 note §5), not the day-1 count; the task brief's "4 of 6 ≥ +5%" is also wrong (4Q25 +4.6 misses). All 23 prints ≥ +5% raw: 6 (0.26, Laplace 0.28); **post-2022 (1Q23–2Q26, n 14): 2 (0.14, Laplace 0.19)** — only 4Q24 (+14.4) and 2Q26 (+17.4) clear +5% since 1Q23 (revision 1 wrote "3 of 14 (0.21)", a transcription error against `r14_base_rates.json` `post2022_ge5_raw` 2; A13-05); 3Q22+ (n 16): 3 (0.19, Laplace 0.22); post-2022 Q4 prints: 2 of 4 | `data/processed/abnb_earnings_reactions.csv`; `datasets/r14_base_rates.json`; `deck/drafts/memo_v2_short_2026-09-16.md` line 77; `docs/pitch-forecasts/00_BRIEF.md` "Reaction base rates" | 2026-09-16 | 2026-09-17 | yes |
| 2 | Sign rule S1 (pre-stated headline, 3Q22–2Q26): E[excess] = −0.67 + 3.35 × sign(nights acceleration, 0.25pt dead band); decelerating prints closed up 1 of 9 on excess (3 of 9 raw), mean −3.6% excess / −2.9% raw; accelerating 4 of 6, +3.4% excess / +3.3% raw; residual sd 8.8. Sign coding: accel 3Q22 3Q23 4Q24 3Q25 4Q25 2Q26; decel 4Q22 1Q23 2Q23 4Q23 1Q24 2Q24 1Q25 2Q25 1Q26; flat 3Q24. Nothing pre-stated clears Holm | `research/notes/reverse_dcf/C_reaction-function.md` §1, §7; `../day1-move-5nov/datasets/s01_cells.csv` | 2026-09-13 / 2026-09-17 | 2026-09-17 | yes |
| 3 | Q4-print residuals against S1 (measured here): 4Q22 (decel, +12.6 excess) +16.6; 4Q23 (decel, −2.8) +1.2; 4Q24 (accel, +14.0) +11.3; 4Q25 (accel, +4.4) +1.7; mean +7.7 (sd 7.5, n 4) vs −2.6 for the twelve non-Q4 prints: gap +10.3 points, Welch t 2.4, post-hoc (not among C's 17 pre-stated specs). C §5's related cut: "decelerating guide at a Q4 print +7.1% (n 4) vs non-Q4 −5.8% (n 7)"; C's reading: "every Q4 print guides a decelerating Q1 on a hard comp ... a guide that says what the calendar says is not news". **C §10 item 3's own disclaimer, quoted where the effect is used (A13-23): "With four observations this could be 'the market looks through the Q1 comp' or four coincidences; it was found after the guide-direction test failed and is a reading, not a result."** The S1 gap is a sign-only residual; the model conditions on sign AND guide-vs-Street, which absorbs part of it — hence the leave-one-out premium in claim 4 is the one used | `datasets/r14_base_rates.json` s1_resid_*; `C_reaction-function.md` §5, §10 | 2026-09-17 / 2026-09-13 | 2026-09-17 | yes |
| 4 | Panel cell means (raw, S01 `s01_cells.csv`): accel & guide at/above Street +7.4 (n 3: 3Q25, **4Q25**, 2Q26), accel & below −0.8 (3: 3Q22, 3Q23, **4Q24**), flat −8.7 (1: 3Q24), decel & at/above +0.8 (5: **4Q22**, 2Q23, **4Q23**, 2Q25, 1Q26), decel & below −7.6 (4: 1Q23, 1Q24, 2Q24, 1Q25). All four post-2022 Q4 prints sit inside these cells, so a Q4 premium added to the full cells counts the Q4 prints twice (A13-03). **Ex-Q4 cell means: aa +8.85 (n 2), ab −8.35 (n 2), fl −8.7 (n 1), da −2.60 (n 3), db −7.55 (n 4); the four Q4 prints' deviations from their ex-Q4 cells: 4Q22 +16.0, 4Q23 +0.9, 4Q24 +22.75, 4Q25 −4.25, mean +8.85** (the leave-one-out Q4 premium, vs the S1 gap +10.3); state-weighted, the full cells already sit +1.45 raw / +0.95 after the 0.65 shrink above the ex-Q4 cells. Guide-vs-Street +1.4–1.9 excess per 1% (fragile); unconditional post-2022 raw mean −1.1, all-print +1.2 | `../day1-move-5nov/datasets/s01_cells.csv`; `C_reaction-function.md` §1 item 3; `audits/A13-reproduce.py` block "R14 the Q4 uplift is already inside the S01 cells" | 2026-09-17 | 2026-09-17 | yes |
| 5 | Team objects for the 4Q26 print, as adopted after A09 revision 2: **3Q26 nights N(9.5, 1.70)** (`adopted_print_states_v2.json`; revision 1 used the nowcast band N(9.55, 1.48)); 4Q26 from the F01/F02 revision-2 V1 leg: **4Q26 = 8.1 + 0.5 × (3Q26 − 9.5) + N(0, 1.4)** with a 12% short-case tail N(5.5, 1.5) (revision 1: an independent N(8.1, 1.6) draw at corr 0.5 — the two constructions give nearly the same sign distribution, A13-17); Street 3Q26 +11.1% (148.9m), 4Q26 +9.9% (134.0m, n 28): both the team and the Street expect 4Q26 to decelerate vs 3Q26 | `../risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json`; `../q1-27-revenue-guide-growth/forecasts/2026-09-17-forecast.json` (revision 2, `model.structure`); `docs/pitch-forecasts/00_BRIEF.md` §6; `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv`; `docs/overnight2/SYNTHESIS.md` (4Q26 8.0–8.2) | 2026-09-11 to 2026-09-17 | 2026-09-17 | yes |
| 6 | **F02 (revision 2)**: 1Q27 revenue guide midpoint growth p5/10/25/50/75/90/95 = 5.1 / 6.2 / 8.3 / 10.5 / 12.8 / 14.8 / 16.1%, mean 10.6, sd 3.4; LSEG 1Q27 mean +12.4% (n 21, 13 Aug), gap-adjusted Street +11.0%; interpolating the table at 11.0 → **P(guide ≥ 11.0%) ≈ 0.45** (revision 1's table gave 0.33); P(< 10%) 0.45. **F01 (revision 2)**: P(1Q27 nights descriptor ≥ 8.2%) 0.28 (revision 1: 0.22). F03: FY27 margin guide (d) below 35.5% / investment-year 0.38 | `../q1-27-revenue-guide-growth/forecasts/2026-09-17-forecast.json` (revision 2); `../q1-27-nights-guide-above-82/forecasts/2026-09-17-forecast.json` (revision 2); `../fy27-margin-guide/forecasts/2026-09-17-forecast.json` | 2026-09-17 | 2026-09-17 | yes |
| 7 | Options at the 16 Sep close: 15 Jan 2027 ATM IV 37.21% (T 0.3315), 19 Mar 2027 38.02% (T 0.5041); the Mar expiry holds both prints, the Jan expiry one, so the variance difference net of background is the Feb event: sd 8.5% at 33.85% background (S01's least-squares background), 9.5% at 32.3% (Oct ATM), 11.2% at 29%, 6.8% at 36%; central 9.0, range 8.5–9.5. 5 Nov event sd 9.1% (S02) / 9.0% (S01). The mixture's total day-1 sd is **9.04** on the revision-2 construction (cell dispersion 2.8 + t5 residual 8.5 + QQQ 1.3), i.e. the object it is meant to match (A13-16) | `../close-15dec-2026/datasets/implied_term_structure_20260917T031221Z.csv`; `datasets/r14_base_rates.json` feb_event_sd_by_bg_vol; `datasets/r14_v2_summary.json` sd, mu_sd; S01 §5 | 2026-09-16 / 2026-09-17 | 2026-09-17 | yes |
| 8 | **S03 (revision 2)**: adopts R14 revision 1's object — Feb day-1 branch means +2.5 / +1.0 / +0.5 / −0.5 by 5 Nov branch, sd 9.0 → unconditional mean +0.7%, P(≥ +5%) 0.32, P(< 0) 0.47 ("X01 should use R14"); its sensitivity row prices the mapping: zero means in every branch → 12 Feb decomposition median $163.5 vs $165 (−$1.5), P(≤150) 0.36 vs 0.35, P(≥180) 0.34 vs 0.35. Revision 1 of S03 (superseded) carried +4.0 / +2.5 / +2.5 / +2.0, mean +2.6%, P(≥5) 0.39 | `../close-12feb-2027/forecasts/2026-09-17-forecast.json` (revision 2, `feb_print_event`, `sensitivity`[0]); `../close-12feb-2027/research-log.md` claim 25, §7 | 2026-09-17 | 2026-09-17 | yes |
| 9 | Seasonal (09 note §5, n 5–6): Jan +6.9% excess (4/6), Feb +7.7% (6/6, p 0.005); "the seasonal is the summer-booking-season expectations cycle, in which ABNB is bid into the February FY guide"; 54 tests run; "a base rate to put on the calendar, not a proven effect" | `research/notes/overnight/09_stock-behaviour-and-alpha.md` §5 | 2026-09-06 | 2026-09-17 | no |
| 10 | **Model, revision 2** (`datasets/r14_model_v2.py`, seed 20260917): P(≥ +5%) **0.225**; P(< 0) 0.55; P(≥ +10%) 0.10; P(≤ −5%) 0.30; P(≤ −8%) 0.18; P(3 ≤ r < 5) 0.08; mean −0.9, sd 9.0; percentiles p5/10/25/50/75/90/95 = −14.9 / −11.3 / −6.2 / −1.0 / +4.3 / +9.9 / +13.6; P(4Q26 accelerates vs 3Q26) 0.14, flat 0.08, decel 0.78; P(≥5 \| accel) 0.37, flat 0.14, decel 0.21; P(≥5 \| guide ≥ Street) 0.32, below 0.15; E[r \| r ≥ 5] +10.9, E[r \| r ≤ −5] −10.7; up-tail contribution 0.225 × 10.9 = +2.4 points, down-tail 0.30 × (−10.7) = −3.2 points (they sum toward the mean); E[4Q26 nights \| r ≥ 5] 7.92 vs 7.79; P(guide ≥ Street \| r ≥ 5) 0.63 (vs 0.45); P(4Q26 ≥ 9.9 \| r ≥ 5) 0.14. Bridge from revision 1 (`r14_v2_sensitivity.csv`): revision-1 construction 0.258 (file 0.257) → ex-Q4 cells + leave-one-out uplift 2.66 alone 0.205 → + F02 rev-2 0.45 **0.225** (full cells + uplift 1.7 + 0.45: 0.238; rev-1 cells + 0.45 alone: 0.288) | `datasets/r14_v2_summary.json`, `r14_v2_sensitivity.csv` | 2026-09-17 | 2026-09-17 | yes |
| 11 | No tradable market on the February reaction (Kalshi KXABNB/KXABNBA, Polymarket "airbnb" scans 03:10Z and 03:56Z); no 2027 print date announced (S03 query 13); the 72-hour recency check found nothing on the Feb print or FY27 guidance | `sources/web_search_log.md`; S03 §2 | 2026-09-17 | 2026-09-17 | no |

Newest load-bearing source: the reaction file and the computed tables (16–17 Sep, zero to one day old against a 148-day window); the C note is 4 days old. Within the rule; the object's real inputs (the 5 Nov print and the January data) do not exist yet.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`, skill and format references, example log; finished logs S01, S02, S03, S04, R01, F01 and the F02/F03 JSONs; `deck/drafts/memo_v2_short_2026-09-16.md` (grep "6 of 6", "February")
2. [repo] `data/processed/abnb_earnings_reactions.csv` (all rows), `data/processed/overnight/05_reaction_by_accel.csv`, `data/processed/abnb_guidance_reaction_panel.csv` (header)
3. [repo] `research/notes/reverse_dcf/C_reaction-function.md` §1, §5, §7, §10; `../day1-move-5nov/datasets/s01_cells.csv`, `options_event_sd.csv`, `options_term_structure.csv`
4. [repo] `../close-15dec-2026/datasets/implied_term_structure_20260917T031221Z.csv`, `../close-12feb-2027/datasets/implied_dist_20260917T031221Z.json`
5. [repo] `research/notes/catalyst_calendar.md` (grep Feb/Dec/Jan)
6. [computed] `datasets/r14_model.py` Part A (Q4 counts, S1 residuals, Feb event sd) and Part B (mixture, sensitivities, anchor table)
7. [Kalshi API / Polymarket] scans reused from this batch (R12 sources, 03:56Z) and S02 (03:10Z)
8. WebSearch: Airbnb news past 3 days (final 72-hour neutral recency check for the batch — result: fake-listing purge, $250M housing fund, World Cup host piece; nothing on the Feb print; no change)
9. [revision 2, repo] `../q1-27-revenue-guide-growth/forecasts/2026-09-17-forecast.json` and `../q1-27-nights-guide-above-82/forecasts/2026-09-17-forecast.json` (revision 2), `../close-12feb-2027/forecasts/2026-09-17-forecast.json` and log claim 25 (revision 2), `../risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json`, `../day1-move-5nov/datasets/s01_cells.csv` (cell membership), `C_reaction-function.md` §10 item 3
10. [revision 2, computed] `audits/A13-reproduce.py` (the auditor's script; output in `audits/A13-reproduce.stdout.txt`): record 2 of 14; ex-Q4 cells and the leave-one-out premium 8.85; event sd table; mixture 0.2571 (rev 1) → 0.2027 → 0.2212
11. [revision 2, computed] `datasets/r14_model_v2.py` → `r14_v2_summary.json`, `r14_v2_sensitivity.csv` (claim 10, §7)

WebSearch calls charged to R14: 1 (query 8); batch total 3 of 15. No new web queries in revision 2.

## 3. Leading Hypothesis Entities
Airbnb, ABNB, 4Q26 print, 12 Feb 2027, 1Q27 revenue guide, LSEG Street, nights-acceleration sign rule, February seasonal, options-implied event sd, 5 Nov 2026 print

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Memo's "6 of 6 positive" as the base rate | discarded; corrected | day-1 raw is 5 of 6 positive, 3 of 6 ≥ +5% (claim 1); the 6/6 is the calendar-month excess |
| Q4 class base rate (3 of 6, 0.50) taken at full weight | kept at half weight | n 6 and three of the six are reopening/first-profit years; the post-2022 Q4 count is 2 of 4; blended with the all-print 0.26 and the post-2022 Laplace 0.19 → 0.36 |
| Q4 premium added to the full S01 cells (revision 1: +3.0 = 30% of the S1 gap +10.3) | withdrawn (A13-03) | the full cells already contain 4Q22/4Q23/4Q24/4Q25, so the premium was booked twice; revision 2 uses the ex-Q4 cells and the leave-one-out premium +8.85 at the same 30% (+2.66); the equivalent on full cells is +1.7 |
| Q4 premium (leave-one-out +8.85, C's "reading, not a result") carried in full | discarded; carried at 30% | post-hoc on n 4 after 400+ tests in C; the guide-vs-Street term and the premium are two views of one mechanism ("a guide that says what the calendar says is not news") and are not both carried at full strength: the guide penalty enters through cells shrunk 35% toward −1.0 and the premium at 30% (A13-23); 0 / 50% / 100% are sensitivities (0.15 / 0.29 / 0.51) |
| S03's Feb day-1 object adopted as is | discarded; reported | S03 revision 2 adopted R14 revision 1's object (claim 8); R14 owns the event and S03 maps it; the revision-2 gap is stated in §6 for the orchestrator |
| Independence from the 5 Nov print | discarded | the 3Q26 draw sets the 4Q26 comparator through the V1 conditional (claim 5); after a decel-guide-below November the 1Q27 guide bar resets lower (F02's gap-adjusted Street) — carried through p_guide_ge 0.45 |
| Use the 5 Nov event sd (9.0–9.5) for February | replaced | the Jan/Mar interpolation isolates the Feb event at 8.5–9.5 (claim 7); the t5 residual 8.5 gives a total model sd of 9.0 |
| Q4 print pre-released or moved to March | tail; conventions (2) | no precedent; the same event on its actual date |

## 5. Independent Estimates
- base_rate_estimate: 0.36 — the Q4 class 3 of 6 ≥ +5% (Laplace 0.50) at half weight with the other half the mean of the all-print 6 of 23 (0.26) and the corrected post-2022 2 of 14 (Laplace 0.19): 0.5 × 0.50 + 0.5 × 0.22 ≈ 0.36 (the auditor's 0.5 × 0.50 + 0.5 × 0.19 = 0.345; revision 1's 0.38 used the all-print rate alone and the wrong post-2022 count)
- decomposition_estimate: 0.225 — mixture (claim 10): P(4Q26 accel) 0.14 / flat 0.08 / decel 0.78 from the adopted objects; P(1Q27 guide ≥ Street) 0.45; ex-Q4 cell means shrunk 35% toward −1.0; leave-one-out Q4 premium at 30% (+2.66); t5 residual sd 8.5 (total sd 9.0); QQQ sd 1.3
- anchor_estimate: 0.27 — risk-neutral symmetric distribution at the Jan/Mar-implied Feb event sd 9.0% (mode −0.4): P(≥ +5%) 0.274 (0.263 at 8.5, 0.285 at 9.5); no tradable market on the reaction
- anchor_value: 0.27 (options-implied Feb event sd 9.0%, 16 Sep close, captured 2026-09-17T03:12Z)
- final_estimate: **0.26** (credible interval 0.17–0.37)
- final_minus_anchor: −0.01. Inside 10 points; independence stated: the decomposition (0.225) sits 5 points below the symmetric anchor because the decelerating-print / guide-below-Street expectation (about −3.5 points on the mean once the double-counted premium is removed) outweighs the Q4 premium carried at 30%; the final is then pulled up 3–4 points toward the class base rate (0.36), whose signal (Q4 prints reward the annual reset) is not in the options price. Weights 0.50 decomposition / 0.35 anchor / 0.15 base rate → 0.26. The number is not a haircut off the anchor; it would read 0.22 without the base rate and 0.29 at a 50% premium. Revision 1's 0.30 was the average of two errors pointing in opposite directions (the double-counted premium, +3.5 points; the stale F02, −3 points) plus a 4-point base-rate pull on a miscounted record

## 6. Final Numbers
P(day-1 close-to-close return after the 4Q26 print ≥ +5%) = **0.26**, credible interval **0.17–0.37**.
Companion (model, before the base-rate pull): P(< 0) 0.55; P(≥ +10%) 0.10; P(≤ −5%) 0.30; P(≤ −8%) 0.18; mean −0.9, sd 9.0; p5/25/50/75/95 = −15 / −6.2 / −1.0 / +4.3 / +13.6. With the final's +3.5-point pull the implied mean is about −0.3%.
By state: P(≥5 | 4Q26 accelerates vs 3Q26) 0.37 (weight 0.14); flat 0.14 (0.08); decelerates 0.21 (0.78). By guide: P(≥5 | 1Q27 revenue guide ≥ Street) 0.32 (0.45); below 0.15 (0.55).
Coherence with S03 (revision 2, claim 8): S03 carries this event at P(≥5) 0.32 with mean +0.7 (branch means +2.5 / +1.0 / +0.5 / −0.5, mapped from R14 revision 1's 0.30 / +0.8). R14 revision 2 is 0.26 with a model mean of −0.9 (≈ −0.3 with the base-rate pull), so S03's branch means would come down by roughly 1 point (e.g. +1.5 / 0 / −0.5 / −1.5); S03's own sensitivity row prices that at about −$1 to −$1.5 on the 12 Feb median and ±0.01 on the thresholds — inside S03's stated noise. This is the orchestrator's call at X01 time (S03 is not edited here); X01 should use R14 revision 2 for the February event.
Extreme-probability gate: not triggered.

## 7. Sensitivity
Single-assumption reruns of `datasets/r14_model_v2.py` (`r14_v2_sensitivity.csv`); base 0.225, the final carries the same deltas.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Q4 premium +2.66 (30% of the leave-one-out +8.85) on ex-Q4 cells | none: 0.15; 50% (+4.4): 0.29; full (+8.85): 0.51; 30% of the S1 gap (+3.1): 0.24; revision-1 construction (full cells + 3.0): 0.29 at p_guide 0.45 |
| Ex-Q4 cells | full cells + uplift 1.7 (the auditor's equivalent): 0.24; full cells + 3.0 (revision 1): 0.29 |
| Cell means shrunk 35% toward −1.0 | unshrunk: 0.19; market-neutral (all cells −1.0): 0.32 |
| 4Q26 = 8.1 + 0.5 (3Q26 − 9.5) + N(0, 1.4), 12% tail | Street 9.9 sd 1.2, no tail: 0.29 (P accel 0.54); RNPL module 7.6: 0.22; 3Q26 at the Street 11.1 and 4Q26 9.9: 0.21; 3Q26 N(9.67, 1.70): 0.22 |
| P(1Q27 guide ≥ Street) 0.45 | 0.60: 0.25; 0.30: 0.20; 0.33 (F02 rev 1): 0.205 |
| Residual sd 8.5 (t5; total 9.0) | 8.0 (total 8.6): 0.21; 9.5 (total 10.0): 0.24; normal: 0.26 |
| Unconditional centre −1.0 | −2.6 (post-2022 excess mean): 0.21; +1.2 (all-print raw mean): 0.25 |
| Base-rate pull (+3.5 points) | none: 0.22; full weight on the Q4 class (0.50): 0.36 |
| Joint bull (Street nights, guide ≥ Street 0.6, premium 50%) | 0.41 |
| Joint bear (module nights, guide ≥ Street 0.30, no premium) | 0.12 |

Pre-mortem ("it is 12 Feb 2027 and I was wrong"): (1) **+13% day like 4Q22/4Q24** — a decelerating Q4 print with a 1Q27 guide above the reset Street and an FY27 margin floor at or above FY26 (F03 (a)/(b) 0.25) after a November that had already cut the bar; this is exactly the pattern the Q4 premium measures, carried at 30%; priced at P(≥10) 0.10. (2) **The November short case makes February a relief print** — after a −10% November and target cuts, the Feb bar is the guide (E card: "the bar is the guide") and a mere in-line print is bought; the guide-below-Street cell is shrunk and the premium applies in every branch, but a "relief" mechanism conditional on a bad November is not separately modelled; it sits in the interval's top. (3) **Accelerating Q4 print on late RNPL bookings and easy Middle-East comps** — P(accel) 0.14 in the model (0.54 on the Street's numbers); the sensitivity row covers it (0.29). (4) **A macro day** — QQQ ±3% on 12 Feb shifts the whole table; QQQ sd 1.3 in the model only. (5) **Resolved No at +4.6% again (4Q25)** — the threshold sits inside the mode of the up-print cell; P(3 ≤ r < 5) ≈ 0.08 is the near-miss mass either way. (6) **The ex-Q4 cells are too thin** (aa n 2, ab n 2, da n 3) and the leave-one-out premium is itself an n-4 reading — the market-neutral row (0.32) is the answer if the cells carry no information. Asymmetry: the memo uses this as the two-way risk of holding the short through February; understating it hides the exit decision (cover before Feb), so the final leans toward the class base rate rather than the model.

## 8. Monitoring Calendar
Update procedure: re-run `datasets/r14_model_v2.py` with the 3Q26 print and the 4Q26 bucket after 5 Nov (re-centre n3 on the print, the 4Q26 conditional on the bucket midpoint); after mid-January re-pull the Feb weekly straddle for the event sd.
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-10-02 | prelim memo due | quote 0.26 (0.17–0.37); replace "6 of 6" with "5 of 6 positive, 3 of 6 ≥ +5%" in the memo; delete the $5.3/share EV line (§9) |
| 2026-11-05/06 | 3Q26 print: nights, 4Q26 bucket, guide vs Street, reaction | re-centre: 3Q26 ≥ 10.6 and "low double digits" for Q4 → 0.22 (harder Q4 comparator); 3Q26 ≤ 9.5 and "high single digits" → 0.28 (lower Q4 bar; relief mechanism); day-1 ≤ −8% → 0.30 |
| 2026-12-15 | S02/S04 resolve; sell-side FY27 revisions in | Street 1Q27 revenue mean ≤ $2,950M (bar reset) → p_guide_ge 0.55 → 0.28; ≥ $3,050M → p_guide_ge 0.35 → 0.24 |
| 2027-01-12 to 01-20 | 4Q26 date announced; Feb weeklies list; 15 Jan expiry rolls | fix the resolution session; replace the Jan/Mar sd with the Feb weekly straddle (each ±1pt of sd ≈ ∓/±0.02) |
| 2027-01-25 | STR 4Q26 US RevPAR (R11/B15); NTTO December | RevPAR ≥ +4%: 4Q26 centre +0.3 → 0.27; ≤ +1%: −0.3 → 0.25 |
| 2027-02-04 | EXPE/BKNG 4Q prints (EXPE reads through) | EXPE day-1 \|5%\|+ on its Q1 guide: shift the 4Q26 centre by 0.25pt in the same direction |
| 2027-02-11/12 | 4Q26 print and reaction session | resolve on the first session's close ÷ the release-day close |

## 9. Impact
If R14 resolves Yes (day-1 ≥ +5%; E[r | ≥ 5] ≈ +10.9%), deltas versus the memo's base case. Two-sided per A13-02: the additive line is the operating carry the up-day selects; the price tail is reported separately and unpriced because it is already inside S03 revision 2's 12 Feb distribution.

| Item | Delta if R14 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 (already printed by then) | — |
| 4Q26 nights (pts) | **+0.1 (indirect)**: E[4Q26 nights \| up day] 7.92 vs 7.79 unconditional; the up-day is mostly the guide and the residual, not the print level (P(4Q26 ≥ 9.9 \| up) 0.14 vs 0.12) | claim 10 |
| ADR (pts) | 0 | — |
| 4Q26 revenue ($M) | +4 (indirect: 0.14pt × $30M) | brief sensitivity |
| FY27 revenue ($M) | **+40 (indirect, reverse-causal: the up-day selects worlds with a better guide, it does not cause them)**: P(1Q27 guide ≥ Street \| up) 0.63 vs 0.45 → on F02 revision 2's N(10.6, 3.4) the conditional means are 13.6% above and 8.1% below the 11.0% bar, so the +0.18 shift is worth ≈ +1.0pt on the 1Q27 guide midpoint ≈ +$26M on $2,678M; carry-through to FY27 at ~40% persistence of the Q1 delta across four quarters ≈ +0.25pt of FY27 growth × $158M ≈ +$40M (the persistence is a judgement; full persistence would be +$105M, none +$26M) | claims 6, 10; brief sensitivity |
| FY26 / FY27 adj. EBITDA margin (pp) | 0 / +0.1 (indirect: 0.42 × 0.25pt flex) | brief sensitivity |
| FY27 EPS ($) | +0.02 (indirect: $40M × 0.42 × $0.0014) | brief sensitivity |
| Stock ($/share), **additive operating carry** | **≈ +$1.5**: 0.25pt of FY27 growth × 0.40–0.48 turns × $9–10/turn ≈ +$1.0, plus ≈ $17M of FY27 EBITDA ≈ +$0.5 | brief sensitivities |
| **EV = P × impact (additive)** | **0.26 × $1.5 ≈ $0.4/share** | |
| Two-way price tail (reported, **not additive**, S03's object) | on a short held through 11 Feb: P 0.26 of a ≈ +10.9% up day (≈ +$17–18 at a ~$163 pre-print price) against P 0.30 of a ≈ −10.7% down day (≈ −$17); up-tail 0.225 × 10.9 = +2.4 points vs down-tail 0.30 × (−10.7) = −3.2 points, netting to the model mean (−0.9); the whole distribution is already inside S03 revision 2's 12 Feb percentiles. Revision 1's "+$17.8/share, EV $5.3, Material" was the up tail's contribution to the unconditional mean, mechanically positive for any upper tail, and is withdrawn | claim 10; S03 revision 2 |
| Materiality | **Immaterial as a standalone EV line** (additive EV ≈ $0.4/share; the memo should delete the $5.3); **material as an exit-timing statement**: the February leg is a coin-flip on sign (P(< 0) 0.55) with a 0.26 chance of a ≥5% up day and a 0.30 chance of a ≥5% down day, so the memo should price the decision to cover before 11 Feb rather than book an EV | |

## 10. Revision notes
| # | Change (revision 1 → revision 2) | Finding |
|---|---|---|
| 1 | §9 impact split two-sided: additive operating carry +$1.5, EV $0.4, immaterial as a standalone line; the two-way tail reported unpriced as S03's object; the +$17.8 / $5.3 / "Material" line withdrawn; materiality restated as exit timing | A13-02 |
| 2 | Mixture rebuilt on ex-Q4 cells (aa +8.85, ab −8.35, fl −8.7, da −2.60, db −7.55) with the leave-one-out Q4 premium +8.85 at 30% (+2.66) instead of full cells + 30% of the S1 gap: 0.258 → 0.205 alone; claim 4 rewritten; §7 bracket 0.15–0.29 (30% ↔ 50%), not 0.16–0.59 | A13-03 |
| 3 | P(1Q27 guide ≥ Street) 0.33 (F02 rev 1) → 0.45 (F02 rev 2); F01 0.22 → 0.28; claim 6 rewritten; 0.205 → 0.225 with the two fixes together | A13-04 |
| 4 | Claim 1 and the JSON record: post-2022 ≥ +5% "3 of 14 (0.21)" → **2 of 14 (0.14, Laplace 0.19)**; base rate 0.38 → 0.36 | A13-05 |
| 5 | §6 coherence paragraph rewritten against S03 revision 2 (0.32 / +0.7, R14-mapped), with the ≈ −$1 to −$1.5 mapping and the decision left to the orchestrator; the "do not re-run S03" instruction withdrawn; claim 8 rewritten | A13-11 |
| 6 | Claim 7: the model's total sd (9.04) reported against the 9.0% event sd; the residual stays 8.5 because on the revision-2 cells the total already matches; 8.0 / 9.5 as sensitivities | A13-16 (in part) |
| 7 | Claim 5: 3Q26 N(9.5, 1.70) (A09 rev-2 adopted object) and the F01/F02 rev-2 V1 conditional for 4Q26 (immaterial: 0.222 at N(9.67, 1.70), 0.225 here) | A13-17 |
| 8 | §9 FY27 revenue line re-derived against F02 revision 2 (conditional means 13.6 / 8.1, +0.18 shift → +$26M on the 1Q27 guide) with the carry-through assumption stated (40% persistence → +$40M) and labelled reverse-causal | A13-18 |
| 9 | Claim 3: C §10's disclaimer quoted; §4 states why the guide-vs-Street penalty and the Q4 premium are not both carried at full strength | A13-23 |
| 10 | Headline **0.30 (0.20–0.42) → 0.26 (0.17–0.37)**; decomposition 0.26 → 0.225; base rate 0.38 → 0.36; anchor unchanged 0.27; final − anchor +0.03 → −0.01; companions, state and guide conditionals, and the monitoring ladder re-based | A13-03/04/05 |

## RESUME
The next agent (X01 or a further revision) should re-run `datasets/r14_model_v2.py` (deterministic, ~40 s) and decide with the orchestrator whether S03's February branch means come down ≈1 point to match this revision (≈ −$1 to −$1.5 on S03's 12 Feb median; S03 is not edited here). The load-bearing judgements are the 30% weight on the leave-one-out Q4 premium (0.15 at none, 0.29 at 50%) and the 35% shrink on cells that are now n 2–4 (market-neutral 0.32). After 5 Nov, re-centre the 3Q26 draw on the print and the 4Q26 conditional on the bucket before anything else.
