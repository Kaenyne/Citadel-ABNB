# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A08). Companion questions: F02 `q1-27-revenue-guide-growth` (same 4Q26-print tree), F03, F04. Reproduction: [datasets/f01_model.py](datasets/f01_model.py) (numpy only, seed 20260917, 400,000 draws, ~5 s; writes `f01_summary.csv`, `f01_sensitivity.csv`).

## 0. Metadata
- question_name: q1-27-nights-guide-above-82
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` F01)
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
Will Airbnb's 1Q27 nights guidance at the Feb print imply year-over-year growth of ≥ +8.2%?
### Resolution Criteria
Yes if the letter gives a 1Q27 nights descriptor or number implying ≥8.2% on 1Q26's 156.2m (i.e., ≥169.0m): "high single digits" resolves Yes only if a number ≥8.2 or "high single digit to low double digit" is given; "high single digits" alone resolves by the midpoint convention 8.0 → No. "Low double digits" → Yes. No descriptor → No.
### Fine Print
This is the RNPL module's pre-registered falsifier. Resolution date ~11 Feb 2027.

Conventions adopted (stated, not changing the question; registry: letter governs, call counts only if the letter is silent): (1) directional sentences are read against the printed 4Q26 rate — "relatively stable / similar to Q4" → Yes iff the 4Q26 print ≥ 8.2%; "nearly as strong as Q4" (the 4Q22 form) → Yes iff the 4Q26 print ≥ 9.2% (read as ~1pt below); "moderate / lower than Q4" with no bucket → No; "higher than Q4" → Yes iff the 4Q26 print ≥ 7.5%; (2) "approximately 9%", "around 9%", "high single digit to low double digit", "around 10%", "low double digits" → Yes; "mid-to-high single digits", "high single digits", "mid single digits" → No; (3) a nights descriptor embedded in the GBV sentence (the 4Q25 construction, "driven by high-single-digit growth in Nights and Seats Booked") counts; a GBV bucket with no nights qualifier → No (no descriptor); (4) the Feb print on its actual date; a leap-day or calendar adjustment stated by management does not change the resolution (the reported descriptor governs; 2027 has no calendar item of that kind).

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | February Q1 nights descriptors, all four resolved cases (verbatim, with the 4Q print and the 1Q actual): 4Q22 → "Nights and Experiences Booked year-over-year growth to be nearly as strong as Q4 2022" (Q4 printed 20.2; 1Q23 actual 18.6); 4Q23 → "we expect the growth rate of nights booked in Q1 2024 to moderate relative to Q4 2023" (12.0; 9.5); 4Q24 → "relatively stable compared to Q1 2024 after excluding Leap Day, which contributed to approximately one percentage point of growth in Q1 2024" (12.3 printed; comparator 8.5; 7.9); 4Q25 → "GBV to increase in the low teens year-over-year, driven by high-single-digit growth in Nights and Seats Booked" (9.8 printed; bucket 7–9, mid 8; 9.15). All four sat at or below the just-printed Q4 rate; three were 1–4 points below it. 4Q21 → "significantly exceed Q1 2019 levels" (no y/y descriptor). Extract: [datasets/feb_letter_guides_4Q20-4Q25.csv](datasets/feb_letter_guides_4Q20-4Q25.csv) | `data/processed/overnight/02_guidance_ledger.csv`; `data/raw/letters/4Q22_d451233dex991.htm`, `4Q23_d646462dex991.htm`, `4Q24_d915198dex991.htm`, `4Q25_d58192dex991.htm` | 2023-02-14 to 2026-02-12 | 2026-09-17 | yes |
| 2 | Under this question's own convention, the four February descriptors would have resolved against an 8.2-type bar as follows: 4Q22 "nearly as strong" with Q4 at 20.2 → Yes-type; 4Q23 "moderate" → No; 4Q24 "stable ex leap day" with a comparator of 8.5 → Yes-type (marginal); 4Q25 "high-single-digit" → No. 2 of 4; but the two Yes-types came with Q4 prints of 20.2 and 12.3, far above the 8.2 bar; with a Q4 print near 8, the same directional forms would resolve No or marginally | derived from claim 1 | 2026-09-17 | 2026-09-17 | yes |
| 3 | Bucket era (since the 3Q25 letter): the stated bucket midpoint sat 3.8 (3Q25→4Q25) and 1.8 (4Q25→1Q26) points below the printed rate when the comp hardened, and 0.7 above (2Q26→3Q26) when it eased; realised nights beat the bucket top in 2 of 2 resolved cases (by 3.8 and 0.15). "Buckets are the most beatable line in the letter" | C02 log claims 3–4; `docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md` §3.1–3.2 | 2026-09-17 | 2026-09-17 | yes |
| 4 | Format base rate: 12 of 16 pre-2025 next-quarter nights guides were directional; in the bucket era 3 of 4 were buckets (1Q26→2Q26 was directional: "slightly decelerate ... roughly 100bps headwind related to the conflict in the Middle East"); every letter since 2Q22 (17 of 17) carried a next-quarter nights sentence; C02 priced P(directional-only) ≈ 0.25 and P(no descriptor) 0.04 | C02 log claims 1, 3, 20 | 2026-09-17 | 2026-09-17 | yes |
| 5 | 4Q26 nights views (the print management will have in hand): team baseline +8.1% (131.8m; band 8.0–8.9, case A NA-only lap 8.9 at the top), RNPL unified module +7.61% (band 6.6–8.4), Bloomberg MODL 134.0m (+9.9%, n 28, range 130–136m, 12 Sep screenshot), short case +5.0% (128.0m); C02's 4Q26 bucket vector (a) 0.21 / (b) 0.19 / (c) 0.39 / (d) 0.17 / (e) 0.04. 4Q25 base 121.9m (+9.82%) | `data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv`; `data/processed/rnpl_short_audit/rnpl_nights_module.csv`; `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv`; `data/processed/margin_build/40_line_build/40_short_case_revenue_path.csv`; C02 log §6 | 2026-09-15 | 2026-09-17 | yes |
| 6 | Team 1Q27 nights objects: WS06 v2 base +8.21% (169.0m; includes a +1.0 Middle East base effect and a 40% ex-NA RNPL lap; bear 4.71, bull 10.52); RNPL module base +6.47% (166.3m; bear 5.28, bull 7.34) = team 8.17 less uplift lap −1.00, pull-forward −0.46, deferral −0.15, propensity −0.10; PR #32 NA-only lap 8.17 / global lap 6.42; B3 driver base +9.30. Sequential step 4Q26→1Q27 across these objects: +0.09 (v2), −1.14 (module), −0.73 (PR #32 NA-only), −2.48 (global) | `data/processed/margin_build/06_fy27_path_v2/06_comparison_quarterly.csv`; `data/processed/rnpl_short_audit/rnpl_nights_module.csv`; `data/processed/nights_quarterly_total.csv`; `data/processed/rnpl_short_audit/fy27_quarterly_phasing_rnpl_aware.csv` | 2026-09-14 | 2026-09-17 | yes |
| 7 | The 8.2% bar is PR #32's NA-only-lap FY27 rate (169.0m in 1Q27) and the module's pre-registered falsifier: "A 1Q27 guide at or above +8.2% in February kills the module (both the ex-NA lap and the pull-forward reversal would have to be absent)" | `docs/rnpl-short-audit/00_SYNTHESIS.md` §2 (February falsifier row), §5; `research/notes/nights_quarterly.md` | 2026-09-11 | 2026-09-17 | yes |
| 8 | Comp arithmetic for 1Q27: 1Q26 printed +9.15% after "an estimated roughly 100bps headwind related to the conflict in the Middle East" (ex-conflict "approximately 10%"), so the 1Q27 comp is ~0.65pt easier than 4Q26's (9.82) on the reported number and ~1.65pt easier ex-conflict; against that, ex-NA RNPL (live 17 Feb–4 Mar 2026) laps for 5–6 of 13 weeks of 1Q27 and fully from 2Q27; the July 2026 eligibility expansion laps in 3Q27 | `data/raw/letters/1Q26_d23351dex991.htm`; ledger D025–D029, D044; `docs/margin-build/notes/06_fy27_path_v2.md` findings 2, 5 | 2026-09-14 | 2026-09-17 | yes |
| 9 | Management tone into 2027: Chesky, 8 Sep 2026 Goldman conference: "Almost every market is accelerating. Almost every country is accelerating," "India is growing 60% year-over-year," "We're going to have some major announcements next year" (V023); 2Q26 call (Mertz): "Even against tougher comps in the back half of the year, we are raising our full year guidance"; management set the 3Q26 bucket at the printed rate with July in hand | `research/notes/q3nowcast/G_external-sources-q3-read.md` §1.8; `data/processed/margin_build/05_mgmt_statements_v2/05_statements.csv` V023; C02 log claim 7 | 2026-09-08 | 2026-09-17 | yes |
| 10 | Pre-registered 5 Nov card: a 4Q26 nights guide implying ≤7.5% supports the lap/drag hypothesis, ≥9.5% weakens it; a bundle figure ≥2.5 pts weakens it (C05 puts P(quantified ≥2.5) at 0.08) | `data/processed/overnight2/D/D1_prereg_thresholds.csv`; C05 log | 2026-09-11 | 2026-09-17 | no |
| 11 | No market prices the 1Q27 nights guide. Kalshi KXABNBA FY26 nights ladder (2026-09-17T03:18:45Z): >565m 0.79/0.88, >570m 0.63/0.71, >575m 0.37/0.41, >580m 0.19/0.28 (volume/open interest null); implied FY26 ≈ 572m, which with 1H26 304.5m and the Q3 ladder's ~148m implies 4Q26 ≈ 120m (−1.6% y/y): mutually inconsistent, zero weight (C02 reached the same verdict). Polymarket public-search "Airbnb 2027" / "Airbnb guidance": nothing on 2027 | [sources/kalshi_KXABNBA_open_20260917T031845Z.json](sources/kalshi_KXABNBA_open_20260917T031845Z.json), [sources/kalshi_KXABNB_open_20260917T031845Z.json](sources/kalshi_KXABNB_open_20260917T031845Z.json), [sources/polymarket_search_airbnb_2027_20260917T031845Z.json](sources/polymarket_search_airbnb_2027_20260917T031845Z.json) | 2026-09-17 | 2026-09-17 | no |
| 12 | Reverse-DCF market-implied FY27 nights path 8–9% (Street/team base), management-delivered 10.0%; Bloomberg 4Q26 bar 9.9% — the only Street-side objects adjacent to a 1Q27 nights expectation | `docs/reverse_dcf/SYNTHESIS.md`; `docs/margin-build/notes/06_fy27_path_v2.md` comparison table | 2026-09-13 | 2026-09-17 | yes |
| 13 | Web recency (search snippets, pages not fetched): no analyst 1Q27 nights preview; the 4Q26 print date is not announced; final 72-hour neutral check found nothing bearing on the February guide | [sources/web_search_log.md](sources/web_search_log.md) | 2026-09-17 | 2026-09-17 | no |
| 14 | Monte Carlo (this log): P(Yes) 0.183 on the base tree; by 4Q26 print: <7.5 → 0.02 (weight 0.42), 7.5–8.5 → 0.14 (0.22), 8.5–9.5 → 0.30 (0.19), ≥9.5 → 0.51 (0.17); by format: bucket 0.16, directional 0.29, none 0. Sensitivities in [datasets/f01_sensitivity.csv](datasets/f01_sensitivity.csv) | [datasets/f01_summary.csv](datasets/f01_summary.csv) | 2026-09-17 | 2026-09-17 | yes |

Newest load-bearing source: the 14–15 Sep repo builds (claims 5–6) and the 17 Sep C02/C05 logs; 2–3 days old against a 147-day window. The 5 Nov print is the next real input.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`; skill files; example log; finished logs C01, C02, C04/C09, C05–C07
2. [repo] `docs/rnpl-short-audit/00_SYNTHESIS.md`, `02_fy27-decomposition-rnpl-synergy.md`, `03_short-thesis-viability.md`; `data/processed/rnpl_short_audit/rnpl_nights_module*.csv`, `fy27_quarterly_phasing_*.csv`, `fy27_nights_lap_grid.csv`
3. [repo] `research/notes/nights_quarterly.md`; `data/processed/nights_quarterly_na.csv`, `nights_quarterly_total.csv`
4. [repo] `docs/margin-build/notes/06_fy27_path_v2.md`; `data/processed/margin_build/06_fy27_path_v2/06_comparison_quarterly.csv`, `06_revenue_path_wide.csv`
5. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv` — every 4Q-print row (nights, revenue, margin, S&M); `abnb_guidance_reaction_panel.csv` nq_nights_dir / nq_nights_guide_pts
6. [repo] Outlook sections of the 4Q22, 4Q23, 4Q24, 4Q25 letters (regex extract)
7. [repo] `data/processed/overnight2/D/D1_prereg_thresholds.csv`; `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv`; `research/notes/q3nowcast/G_external-sources-q3-read.md`; `05_mgmt_statements_v2/05_statements.csv` V015–V026
8. [Kalshi API] markets?status=open&series_ticker=KXABNBA ; KXABNB (2026-09-17T03:18:45Z)
9. [Polymarket API] public-search?q=Airbnb 2027 ; ?q=Airbnb guidance (2026-09-17T03:18:45Z)
10. WebSearch: Airbnb news (neutral pass, batch-shared)
11. WebSearch: Airbnb 2027 revenue growth outlook analyst expectations (batch-shared)
12. WebSearch: Airbnb fourth quarter 2026 results date February 2027 (batch-shared)
13. [computed] `datasets/f01_model.py` (base + 15 sensitivities)
14. WebSearch: Airbnb latest this week (final 72-hour neutral recency check — nothing new)

WebSearch calls charged to this batch: 5 across F01–F04.

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, Nights and Seats Booked, "high single digits", Reserve Now Pay Later, 4Q26 shareholder letter, February 2027

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| "High single digits" repeated for 1Q27 (the modal outcome; resolves No) | leading (≈0.50 of all outcomes) | Every repo model has 1Q27 at 6.4–8.2 (claim 6); the February descriptor has sat at or below the Q4 print 4 of 4 times (claim 1); a 4Q26 print of ~8 with a bucket 1 point below it is "high single digits" or "mid-to-high single digits" |
| "Low double digits" / "around 10" / "similar to Q4" with Q4 ≥ 8.2 (Yes) | kept, 0.22 | Needs a 4Q26 print ≥ 8.5–9.5 (P ≈ 0.36) and management choosing to guide at or above it on the easier ex-conflict comp (claims 8–9); the joint bull row (Street 4Q26 print, no cushion) reaches 0.59 |
| Directional "moderate relative to Q4" with no bucket (No) | kept inside the 0.24 directional share | The 4Q23 form; used when the comp hardens or October/January is noisy; the 1Q27 comp is easier, which lowers its odds and raises "stable/similar" — but "similar" only resolves Yes if the Q4 print itself is ≥ 8.2 |
| A numeric point ("approximately 9%") | inside Yes via the 8.5–9.5 bucket split (0.45) | Airbnb has given numeric nights guides only as buckets; a hyphenated "high single to low double" is the more likely Yes-form |
| Use the Kalshi FY26 ladder as the 4Q26 conditioning | discarded | zero liquidity and inconsistent with the Q3 ladder (claim 11) |
| Management guides 1Q27 on an ex-lap or ex-conflict basis ("excluding the RNPL comparison") | discarded as a resolution route | The reported descriptor governs; a stated ex-item rate would be a number for the reported quarter only if management said so |
| The ex-NA RNPL lap is absent (module falsified) so the descriptor is ≥ 8.2 by construction | kept as the bull branch (Δ +0.1, cushion 0.5): P 0.59 | This is the branch the question is designed to detect; it needs the 4Q26 print to land at the Street's 9.9 rather than the team's 8.1 |

## 5. Independent Estimates
- base_rate_estimate: 0.19 — reference class "February Q1 nights descriptor vs the Q4 print" (claim 1): 4 of 4 at or below the print, 3 of 4 by 1–4 points; P(Yes) ≈ P(4Q26 print ≥ 9.2) × P(descriptor within 1pt | that) + P(print in 8.2–9.2) × P(descriptor at the print | that) ≈ 0.25 × 0.60 + 0.17 × 0.25 ≈ 0.19, with the print distribution from claim 5 (mean 7.8, sd 1.8)
- decomposition_estimate: 0.18 — the tree in claim 14: 4Q26 print N(8.1, 1.6) with a 12% short-case tail (5.5 ± 1.5) → management's 1Q27 expectation = print + N(−0.4, 1.2) (the mean of the team objects' 4Q26→1Q27 steps is −1.0; management's beat record argues for less) → format (bucket 0.72 / directional 0.24 / none 0.04) → bucket midpoint = expectation − N(1.0, 0.9) → language map (≥9.5 Yes; 8.5–9.5 Yes 0.45; 7.5–8.5 Yes 0.10; <7.5 Yes 0.02; directional per the conventions)
- anchor_estimate: 0.40 — no market; the Street-side object is Bloomberg's 4Q26 bar 9.9% (n 28, 12 Sep) and the reverse-DCF market path (FY27 nights 8–9%); pushing a 9.9 print with no short tail through the same tree gives 0.44, and the market path's 8–9% sits at the bar
- anchor_value: 0.40 (Bloomberg MODL 4Q26 nights 134.0m / +9.9%, screenshot 2026-09-12, through the tree; NO tradable market, Kalshi ladders zero weight)
- final_estimate: 0.22 (credible interval 0.12–0.35)
- final_minus_anchor: −18 points. Justified independently: the anchor is the Street's Q4 bar, which sits above every repo model (team 8.1, module 7.6) and above the 45th-percentile team number; the base rate and the decomposition are built from the letters and the team's 4Q26/1Q27 objects and agree at 0.18–0.19; the final is nudged up to 0.22 for management's September tone, the easier ex-conflict comp and the bucket-beat record (the bull branch), none of which the tree's −0.4 step fully carries

## 6. Final Numbers
**Binary.** P(1Q27 nights descriptor implies ≥ +8.2% y/y, ≥169.0m) = **0.22**, credible interval **0.12–0.35**.
Structure: 0.18 (tree) + 0.04 for the branch where management guides at the print on the easier comp (Δ +0.1, cushion 0.5 → 0.26 at the team print; 0.59 at the Street's). Inside the number: P(no descriptor) 0.04 (No), P(directional-only) 0.24 (Yes only via "similar/stable" with a Q4 print ≥ 8.2, ≈ 0.07 of the 0.22).
Coherence: P(4Q26 print ≥ 8.2) ≈ 0.42; P(management's internal 1Q27 expectation ≥ 8.2) ≈ 0.36; the descriptor sits below the expectation, so P(Yes) < 0.36. For the RNPL module: a Yes falsifies it; P(falsified) 0.22 is consistent with the module's own bull case (7.34) sitting below the bar.
Extreme-probability gate: not triggered (0.22).

## 7. Sensitivity
Single-assumption reruns of `datasets/f01_model.py` from the base tree (0.183); the final carries the same deltas.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| 4Q26 print centred 8.1 with a 12% short tail | RNPL module 7.6: 0.14; Street bar 9.9, no tail: 0.44; short case 5.0 certain: 0.02; no short tail: 0.20 |
| Management's 1Q27 step vs the Q4 print −0.4 | WS06 v2 +0.1: 0.24; RNPL module −1.1: 0.12; PR #32 global lap −2.5: 0.04 |
| Bucket cushion 1.0 (expectation less 1pt) | none (guide at expectation): 0.26; 2.0 (3Q25/4Q25 style): 0.13 |
| Format: bucket 0.72 / directional 0.24 | directional 0.45: 0.21; bucket 0.90: 0.16 |
| 8.5–9.5 midpoint → Yes 0.45 (hyphenated / "approximately 9%") | 0.25: 0.17; 0.65: 0.20 |
| Joint bull (Street print 9.9, step +0.1, cushion 0.5) | 0.59 |
| Joint bear (print 6.5, step −1.1, cushion 2.0) | 0.03 |

Pre-mortem ("it is 11 Feb 2027 and the letter said 'low double-digit growth in Nights and Seats Booked' for 1Q27"): (1) 4Q26 printed ≥ 9.5% — the Street's bar, not the team's; the ex-NA fee/cancellation lap was smaller than WS-D's 0.7–0.9 pts or the July RNPL expansion offset it — priced at 0.17 through the print draw; (2) January bookings ran double digits on the easy Middle East base and management guided at the run-rate, as it did for 3Q26 — priced via Δ ≥ +0.1 and cushion ≤ 0.5 (the bull row); (3) a new 2027 product (R08) or an RNPL extension was launched in January and management chose the bucket to showcase it — not separately priced, inside the format/Δ draws (~0.03); (4) management gave "high single digit to low double digit", a hyphenated form it has used for FY revenue but never for nights — priced at 0.45 of the 8.5–9.5 bucket. Asymmetry: the memo's use of this question is as the module's falsifier; a confident No that resolves Yes would mean the RNPL lap story was wrong, which is exactly the case the interval's top (0.35) is meant to hold.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-18 to 2026-10-02 | September Inside Airbnb dumps; 3Q26 nights band refreshed | Each +0.5pt on the 3Q26 centre moves the 4Q26 centre ~+0.25 (corr 0.5) and P(Yes) ~+0.02 |
| 2026-10-02 | Prelim memo freeze | Quote 0.22 (0.12–0.35); say it is the module's falsifier and that a 4Q26 print ≥ 9.5 is the path to Yes |
| 2026-11-05 | 3Q26 print: 4Q26 nights bucket (C02), bundle figure (C05), RNPL share (C06), 3Q26 print | Re-centre the 4Q26 print on the bucket: "low double digits" → centre 10.0 (P → ~0.44); "high single digits" → 8.0 (P → ~0.18); "mid single digits"/"moderate" → 6.5 (P → ~0.06). A bundle figure ≥ 2.5 pts: +0.05 |
| 2026-12-01 to 2027-01-31 | Kalshi 4Q26 nights ladder if listed; STR/NTTO/Similarweb for October–December; EXPE/BKNG Q4 guides (EXPE reads through) | Re-set the 4Q26 print sd (1.6 → 1.0 by late January); EXPE guiding Q1 room nights ≥ its Q4 rate: +0.03 |
| 2027-01-20 to 2027-01-31 | Airbnb announces the 4Q26 call date | Fix the resolution date |
| 2027-02-11 (est.) | 4Q26 letter: 4Q26 nights print and the 1Q27 descriptor | Resolve per the §0b conventions; read the GBV sentence for an embedded nights descriptor before resolving "no descriptor". Audit read: at a 4Q26 print < 7.5 the pre-print P was ≈ 0.02; 7.5–8.5 ≈ 0.14; 8.5–9.5 ≈ 0.30; ≥ 9.5 ≈ 0.51 |

RESUME: the next agent (audit response) should re-run `datasets/f01_model.py` (deterministic, ~5 s), check claim 1 against the four February letters, and attack the two load-bearing choices: the 4Q26 print mixture (mean 7.8; the Street's 9.9 gives 0.44) and the management step Δ (−0.4; the module's −1.1 gives 0.12). Both are in §7. The language map for the 8.5–9.5 midpoint (Yes 0.45) is the resolver-convention risk and moves the number by only ±0.015.
