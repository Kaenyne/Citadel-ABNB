# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A13 with R12 and R13). Reproduction: `datasets/r14_model.py` (numpy/pandas/scipy, seed 20260917, 400,000 draws, ~40 s with sensitivities; Part A writes `r14_base_rates.json` from the repo's reaction file and S02's term structure, Part B the mixture). A previous attempt at this batch was cut off before writing; its model was rebuilt with the corrected Q4 counts, the measured Q4 residual and the options-implied Feb event sd.

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
- revision: 1
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
| 1 | Q4-print day-1 raw returns: 4Q20 +13.3, 4Q21 +3.6, 4Q22 +13.4, 4Q23 −1.7, 4Q24 +14.4, 4Q25 +4.6 (excess +12.9, +3.7, +12.6, −2.8, +14.0, +4.4): positive 5 of 6 (raw and excess); ≥ +5% raw **3 of 6** (4Q20, 4Q22, 4Q24); ≥ +3.5% 5 of 6; mean +7.9, median +9.0. The memo's "The Q4 print has been positive on day 1 in 6 of 6 observations" (line 77) and the brief's "February Q4 prints positive 6 of 6" are the calendar-February excess-return count (09 note §5), not the day-1 count; the task brief's "4 of 6 ≥ +5%" is also wrong (4Q25 +4.6 misses). All 23 prints ≥ +5% raw: 6 (0.26); post-2022 (1Q23–2Q26, n 14): 3 (0.21); 3Q22+ (n 16): 3 (0.19); post-2022 Q4 prints: 2 of 4 | `data/processed/abnb_earnings_reactions.csv`; `datasets/r14_base_rates.json`; `deck/drafts/memo_v2_short_2026-09-16.md` line 77; `docs/pitch-forecasts/00_BRIEF.md` "Reaction base rates" | 2026-09-16 | 2026-09-17 | yes |
| 2 | Sign rule S1 (pre-stated headline, 3Q22–2Q26): E[excess] = −0.67 + 3.35 × sign(nights acceleration, 0.25pt dead band); decelerating prints closed up 1 of 9 on excess (3 of 9 raw), mean −3.6% excess / −2.9% raw; accelerating 4 of 6, +3.4% excess / +3.3% raw; residual sd 8.8. Sign coding: accel 3Q22 3Q23 4Q24 3Q25 4Q25 2Q26; decel 4Q22 1Q23 2Q23 4Q23 1Q24 2Q24 1Q25 2Q25 1Q26; flat 3Q24. Nothing pre-stated clears Holm | `research/notes/reverse_dcf/C_reaction-function.md` §1, §7; `../day1-move-5nov/datasets/s01_cells.csv` | 2026-09-13 / 2026-09-17 | 2026-09-17 | yes |
| 3 | Q4-print residuals against S1 (measured here): 4Q22 (decel, +12.6 excess) +16.6; 4Q23 (decel, −2.8) +1.2; 4Q24 (accel, +14.0) +11.3; 4Q25 (accel, +4.4) +1.7; mean +7.7 (sd 7.5, n 4) vs −2.6 for the twelve non-Q4 prints: gap +10.3 points, Welch t 2.4, post-hoc (not among C's 17 pre-stated specs). C §5's related cut: "decelerating guide at a Q4 print +7.1% (n 4) vs non-Q4 −5.8% (n 7)"; C's reading: "every Q4 print guides a decelerating Q1 on a hard comp ... a guide that says what the calendar says is not news" | `datasets/r14_base_rates.json` s1_resid_*; `C_reaction-function.md` §5 | 2026-09-17 / 2026-09-13 | 2026-09-17 | yes |
| 4 | Panel cell means (raw, S01 `s01_cells.csv`): accel & guide at/above Street +7.4 (n 3), accel & below −0.8 (3), flat −8.7 (1), decel & at/above +0.8 (5), decel & below −7.6 (4); guide-vs-Street +1.4–1.9 excess per 1% (fragile); unconditional post-2022 raw mean −1.1, all-print +1.2 | `../day1-move-5nov/datasets/s01_cells.csv`; `C_reaction-function.md` §1 item 3 | 2026-09-17 | 2026-09-17 | yes |
| 5 | Team objects for the 4Q26 print: 3Q26 nights N(9.55, 1.48) (nowcast band); 4Q26 nights team baseline 8.1 (ex-NA lap 8.0–8.2), sd 1.6, with a 12% short-case tail N(5.5, 1.5) (F01/F02 tree); Street 3Q26 +11.1% (148.9m), 4Q26 +9.9% (134.0m, n 28): both the team and the Street expect 4Q26 to decelerate vs 3Q26 | `../q1-27-nights-guide-above-82/research-log.md` §5, JSON "model"; `docs/pitch-forecasts/00_BRIEF.md` §6; `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv`; `docs/overnight2/SYNTHESIS.md` (4Q26 8.0–8.2) | 2026-09-11 to 2026-09-17 | 2026-09-17 | yes |
| 6 | F02 (revision 1): 1Q27 revenue guide midpoint growth p5/25/50/75/95 = 3.6 / 7.0 / 9.4 / 12.0 / 15.6%; LSEG 1Q27 mean +12.4% (n 21, 13 Aug), gap-adjusted Street +11.0%; P(guide ≥ 11.0%) ≈ 0.33 (between p50 and p75); P(< 10%) 0.56. F01: P(1Q27 nights descriptor ≥ 8.2%) 0.22. F03: FY27 margin guide (d) below 35.5% / investment-year 0.38 | `../q1-27-revenue-guide-growth/forecasts/2026-09-17-forecast.json`; `../q1-27-nights-guide-above-82/forecasts/2026-09-17-forecast.json`; `../fy27-margin-guide/forecasts/2026-09-17-forecast.json` | 2026-09-17 | 2026-09-17 | yes |
| 7 | Options at the 16 Sep close: 15 Jan 2027 ATM IV 37.21% (T 0.3315), 19 Mar 2027 38.02% (T 0.5041); the Mar expiry holds both prints, the Jan expiry one, so the variance difference net of background is the Feb event: sd 8.5% at 33.85% background (S01's least-squares background), 9.5% at 32.3% (Oct ATM), 11.2% at 29%, 6.8% at 36%; central 9.0, range 8.5–9.5. 5 Nov event sd 9.1% (S02) / 9.0% (S01). S03 carried Feb day-1 sd 8.0–8.5 | `../close-15dec-2026/datasets/implied_term_structure_20260917T031221Z.csv`; `datasets/r14_base_rates.json` feb_event_sd_by_bg_vol; S01 §5; S03 claim 25 | 2026-09-16 / 2026-09-17 | 2026-09-17 | yes |
| 8 | S03 (revision 1): Feb day-1 means by 5 Nov branch +4.0 / +2.5 / +2.5 / +2.0 (the +7.9 base rate shrunk ~65%), sd 8.0–8.5; unconditional Feb day-1 mean +2.6%, P(≥ +5%) 0.39, P(< 0) 0.38 ("feeds R14"); "the February print itself we do not claim to call"; Jan/Feb seasonal +2% carried in the price path, not in the event | `../close-12feb-2027/research-log.md` §4–6 | 2026-09-17 | 2026-09-17 | yes |
| 9 | Seasonal (09 note §5, n 5–6): Jan +6.9% excess (4/6), Feb +7.7% (6/6, p 0.005); "the seasonal is the summer-booking-season expectations cycle, in which ABNB is bid into the February FY guide"; 54 tests run; "a base rate to put on the calendar, not a proven effect" | `research/notes/overnight/09_stock-behaviour-and-alpha.md` §5 | 2026-09-06 | 2026-09-17 | no |
| 10 | Model (this log, `datasets/r14_model.py`, seed 20260917): P(≥ +5%) **0.257**; P(< 0) 0.51; P(≥ +10%) 0.11; P(≤ −5%) 0.27; P(≤ −8%) 0.16; mean −0.1, sd 9.1; percentiles p5/10/25/50/75/90/95 = −14.2 / −10.6 / −5.5 / −0.2 / +5.2 / +10.6 / +14.3; P(4Q26 accelerates vs 3Q26) 0.12, flat 0.08, decel 0.80; P(≥5 | accel) 0.44, flat 0.14, decel 0.24; P(≥5 | guide ≥ Street) 0.41, below 0.18; E[r | r ≥ 5] +10.8; E[4Q26 nights | r ≥ 5] 7.92 vs 7.79; P(guide ≥ Street | r ≥ 5) 0.52; P(4Q26 ≥ 9.9 | r ≥ 5) 0.14 | `datasets/r14_summary.json`, `r14_sensitivity.csv` | 2026-09-17 | 2026-09-17 | yes |
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

WebSearch calls charged to R14: 1 (query 8); batch total 3 of 15.

## 3. Leading Hypothesis Entities
Airbnb, ABNB, 4Q26 print, 12 Feb 2027, 1Q27 revenue guide, LSEG Street, nights-acceleration sign rule, February seasonal, options-implied event sd, 5 Nov 2026 print

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Memo's "6 of 6 positive" as the base rate | discarded; corrected | day-1 raw is 5 of 6 positive, 3 of 6 ≥ +5% (claim 1); the 6/6 is the calendar-month excess |
| Q4 class base rate (3 of 6, 0.50) taken at full weight | kept at half weight | n 6 and three of the six are reopening/first-profit years; the post-2022 Q4 count is 2 of 4; blended with the all-print 0.26 → 0.38 |
| Q4 residual (+10.3 pts vs S1, t 2.4) carried in full | discarded; carried at +3 | post-hoc on n 4 after 400+ tests in C; +5 and +10 are sensitivities (0.34, 0.59) |
| S03's Feb day-1 mixture (mean +2.6, P(≥5) 0.39) adopted as is | discarded; reported | S03 applied the shrunk +7.9 base rate in every branch without the 4Q26 print-sign or guide-vs-Street terms; this log applies the reaction panel's cells to the Feb print (both team and Street expect a decelerating Q4 print; F02 puts the 1Q27 guide below Street) and adds the Q4 uplift on top; the two are reconciled in §6 |
| Independence from the 5 Nov print | discarded | the 3Q26 draw sets the 4Q26 sign comparator (corr 0.5); after a decel-guide-below November the 1Q27 guide bar resets lower (F02's gap-adjusted Street) — carried through p_guide_ge 0.33 |
| Use the 5 Nov event sd (9.0–9.5) for February | replaced | the Jan/Mar interpolation isolates the Feb event at 8.5–9.5 (claim 7); 8.5 used, 7.5 and 9.5 as sensitivities |
| Q4 print pre-released or moved to March | tail; conventions (2) | no precedent; the same event on its actual date |

## 5. Independent Estimates
- base_rate_estimate: 0.38 — the Q4 class 3 of 6 ≥ +5% (Laplace 0.50) at half weight with the all-print 6 of 23 (0.26) and the post-2022 3 of 14 (0.21): 0.5 × 0.50 + 0.5 × 0.26 ≈ 0.38
- decomposition_estimate: 0.26 — mixture (claim 10): P(4Q26 accel) 0.12 / flat 0.08 / decel 0.80 from the team objects; P(1Q27 guide ≥ Street) 0.33; cell means shrunk 35% toward −1.0; Q4 uplift +3; t5 residual sd 8.5; QQQ sd 1.3
- anchor_estimate: 0.27 — risk-neutral symmetric distribution at the Jan/Mar-implied Feb event sd 9.0% (mode −0.4): P(≥ +5%) 0.274 (0.263 at 8.5, 0.285 at 9.5); no tradable market on the reaction
- anchor_value: 0.27 (options-implied Feb event sd 9.0%, 16 Sep close, captured 2026-09-17T03:12Z)
- final_estimate: **0.30** (credible interval 0.20–0.42)
- final_minus_anchor: +0.03. Inside 10 points; independence stated: the decomposition (0.26) lands near the symmetric anchor because two opposite repo signals roughly cancel — the decelerating-print / guide-below-Street expectation (about −3 points on the mean) against the Q4-print residual carried at +3 — and the final is then pulled up 4 points toward the class base rate (0.38), whose signal (Q4 prints reward the annual reset) is not in the options price. The number is not a haircut off the anchor; it would read 0.26 without the base rate and 0.34 at a +5 uplift

## 6. Final Numbers
P(day-1 close-to-close return after the 4Q26 print ≥ +5%) = **0.30**, credible interval **0.20–0.42**.
Companion (model, before the base-rate pull): P(< 0) 0.51; P(≥ +10%) 0.11; P(≤ −5%) 0.27; P(≤ −8%) 0.16; mean −0.1, sd 9.1; p5/25/50/75/95 = −14 / −5.5 / −0.2 / +5.2 / +14. With the final's +4-point pull the implied mean is about +0.8%.
By state: P(≥5 | 4Q26 accelerates vs 3Q26) 0.44 (weight 0.12); flat 0.14 (0.08); decelerates 0.24 (0.80). By guide: P(≥5 | 1Q27 revenue guide ≥ Street) 0.41 (0.33); below 0.18 (0.67).
Coherence with S03: S03 carried this event at P(≥5) 0.39 with mean +2.6 (branch means +2.0 to +4.0); this log's 0.30 / mean ≈ +0.8 would lower S03's 12 Feb median by roughly 1.5–2% ($2–3) and P(≥ $180) by ~0.02 if adopted; the orchestrator should use R14's number for the Feb event in X01 and note the S03 gap rather than re-run S03 (the difference is inside S03's stated noise on the median).
Extreme-probability gate: not triggered.

## 7. Sensitivity
Single-assumption reruns of `datasets/r14_model.py` (`r14_sensitivity.csv`); base 0.257, the final carries the same deltas.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Q4 uplift +3 (30% of the measured +10.3) | none: 0.16; +5: 0.34; full +10: 0.59 |
| Cell means shrunk 35% toward −1.0 | unshrunk: 0.24; market-neutral (all cells −1.0): 0.34 |
| 4Q26 nights N(8.1, 1.6) with a 12% short tail | Street 9.9, no tail: 0.33 (P accel 0.53); RNPL module 7.6: 0.25; 3Q26 at the Street 11.1 and 4Q26 9.9: 0.25 |
| P(1Q27 guide ≥ Street) 0.33 | 0.50: 0.30; 0.15: 0.22 |
| Residual sd 8.5 (t5) | 7.5: 0.24; 9.5: 0.28; normal: 0.29 |
| Unconditional centre −1.0 | −2.6 (post-2022 excess mean): 0.24; +1.2 (all-print raw mean): 0.29 |
| Base-rate pull (+4 points) | none: 0.26; full weight on the Q4 class (0.50): 0.38 |
| Joint bull (Street nights, guide ≥ Street 0.5, uplift 5) | 0.47 |
| Joint bear (module nights, guide ≥ Street 0.15, no uplift) | 0.12 |

Pre-mortem ("it is 12 Feb 2027 and I was wrong"): (1) **+13% day like 4Q22/4Q24** — a decelerating Q4 print with a 1Q27 guide above the reset Street and an FY27 margin floor at or above FY26 (F03 (a)/(b) 0.25) after a November that had already cut the bar; this is exactly the pattern the Q4 residual measures, carried at 30%; priced at P(≥10) 0.11. (2) **The November short case makes February a relief print** — after a −10% November and target cuts, the Feb bar is the guide (E card: "the bar is the guide") and a mere in-line print is bought; the guide-below-Street cell is shrunk and the Q4 uplift applies in every branch, but a "relief" mechanism conditional on a bad November is not separately modelled; it sits in the interval's top. (3) **Accelerating Q4 print on late RNPL bookings and easy Middle-East comps** — P(accel) 0.12 in the model (0.53 on the Street's numbers); the sensitivity row covers it (0.33). (4) **A macro day** — QQQ ±3% on 12 Feb shifts the whole table; QQQ sd 1.3 in the model only. (5) **Resolved No at +4.6% again (4Q25)** — the threshold sits inside the mode of the up-print cell; P(3 ≤ r < 5) ≈ 0.09 is the near-miss mass either way. Asymmetry: the memo uses this as the two-way risk of holding the short through February; understating it hides the exit decision (cover before Feb), so the final leans toward the class base rate rather than the model.

## 8. Monitoring Calendar
Update procedure: re-run `datasets/r14_model.py` with the 3Q26 print and the 4Q26 bucket after 5 Nov (re-centre n3 on the print, n4 on the bucket midpoint); after mid-January re-pull the Feb weekly straddle for the event sd.
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-10-02 | prelim memo due | quote 0.30 (0.20–0.42); replace "6 of 6" with "5 of 6 positive, 3 of 6 ≥ +5%" in the memo |
| 2026-11-05/06 | 3Q26 print: nights, 4Q26 bucket, guide vs Street, reaction | re-centre: 3Q26 ≥ 10.6 and "low double digits" for Q4 → 0.25 (harder Q4 comparator); 3Q26 ≤ 9.5 and "high single digits" → 0.32 (lower Q4 bar; relief mechanism); day-1 ≤ −8% → 0.34 |
| 2026-12-15 | S02/S04 resolve; sell-side FY27 revisions in | Street 1Q27 revenue mean ≤ $2,950M (bar reset) → p_guide_ge 0.45 → 0.33; ≥ $3,050M → 0.27 |
| 2027-01-12 to 01-20 | 4Q26 date announced; Feb weeklies list; 15 Jan expiry rolls | fix the resolution session; replace the Jan/Mar sd with the Feb weekly straddle (each ±1pt of sd ≈ ∓/±0.02) |
| 2027-01-25 | STR 4Q26 US RevPAR (R11/B15); NTTO December | RevPAR ≥ +4%: 4Q26 centre +0.3 → 0.31; ≤ +1%: −0.3 → 0.29 |
| 2027-02-04 | EXPE/BKNG 4Q prints (EXPE reads through) | EXPE day-1 |5%|+ on its Q1 guide: shift n4 by 0.25pt in the same direction |
| 2027-02-11/12 | 4Q26 print and reaction session | resolve on the first session's close ÷ the release-day close |

## 9. Impact
If R14 resolves Yes (day-1 ≥ +5%; E[r | ≥ 5] ≈ +10.8%), deltas versus the memo's base case:

| Item | Delta if R14 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 (already printed by then) | — |
| 4Q26 nights (pts) | **+0.1 (indirect)**: E[4Q26 nights | up day] 7.92 vs 7.79 unconditional; the up-day is mostly the guide and the residual, not the print level (P(4Q26 ≥ 9.9 | up) 0.14) | claim 10 |
| ADR (pts) | 0 | — |
| 4Q26 revenue ($M) | +3 (indirect: 0.1pt × $30M) | brief sensitivity |
| FY27 revenue ($M) | **+40 (indirect)**: P(1Q27 guide ≥ Street | up) 0.52 vs 0.33 → conditional 1Q27 guide midpoint ≈ +10.3% vs F02's +9.4% (+$25M on the 1Q27 guide) → ≈ 0.25pt of FY27 growth × $158M | claim 6, claim 10; judgement on the carry-through |
| FY26 / FY27 adj. EBITDA margin (pp) | 0 / +0.1 (indirect: 0.42 × 0.25pt flex) | brief sensitivity |
| FY27 EPS ($) | +0.02 (indirect: $40M × 0.42 × $0.0014) | brief sensitivity |
| Stock ($/share) | **+$17.8 vs the model's unconditional Feb-day mean** (+10.8 − (−0.1) = 10.9 points × ~$163, the S02 15 Dec median rolled to the pre-print level); **+$13.4 vs S03's carried +2.6% mean**; vs a decel-guide-below November path (S03 branch median $153 on 12 Feb) the same 10.9 points are ≈ +$16 | claim 10; S02/S03 §6 |
| **EV = P × impact** | **0.30 × $17.8 = $5.3/share** (0.30 × $13.4 = $4.0 against S03's carried mean) | |
| Materiality | **Material** (≥ $1/share by a wide margin) — the largest two-way risk after 5 Nov itself; the memo should say the February leg is a coin-flip on sign with a 0.30 chance of a ≥5% up day and price the exit before it | |

## RESUME
The next agent (audit response) should re-run `datasets/r14_model.py` (deterministic, ~40 s) and attack: (1) the Q4 uplift +3 — the measured residual is +10.3 (n 4, t 2.4, post-hoc); the number ranges 0.16 (none) to 0.59 (full), so the shrink is the load-bearing judgement; check the S1 coefficients (−0.67, +3.35) and the sign coding in Part A against `C_reaction-function.md` §7 and `s01_cells.csv`; (2) the base-rate pull of +4 points (Q4 class 3 of 6 at half weight) — an auditor may prefer no pull (0.26) or the class alone (0.38); (3) the S03 coherence gap (S03 0.39 vs R14 0.30) — decide which the orchestrator uses in X01 and whether S03's 12 Feb median (−$2–3) should be revised. After 5 Nov, re-centre n3/n4 on the print and the bucket before anything else.
