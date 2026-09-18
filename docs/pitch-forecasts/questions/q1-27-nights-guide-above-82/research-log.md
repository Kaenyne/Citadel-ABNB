# RESEARCH LOG

Revision 2 (2026-09-17, audit response to A08, Fable 5.1). Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A08). Companion questions: F02 `q1-27-revenue-guide-growth` (same 4Q26-print object), F03, F04. Reproduction: [datasets/f01_model_v2.py](datasets/f01_model_v2.py) (numpy only, seed 20260917, 400,000 draws, ~10 s; writes `f01_v2_summary.csv`, `f01_v2_sensitivity.csv`, `q4_adopted_v2_summary.csv`). Revision-1 `f01_model.py` and its CSVs are left untouched as the audit trail. Audit: `docs/pitch-forecasts/audits/A08-research-audit.md`; response: `audits/A08-audit-response.md`.

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
- revision: 2
- revised: 2026-09-17
- agent: fable

## 0b. Question (verbatim)
### Title
Will Airbnb's 1Q27 nights guidance at the Feb print imply year-over-year growth of ≥ +8.2%?
### Resolution Criteria
Yes if the letter gives a 1Q27 nights descriptor or number implying ≥8.2% on 1Q26's 156.2m (i.e., ≥169.0m): "high single digits" resolves Yes only if a number ≥8.2 or "high single digit to low double digit" is given; "high single digits" alone resolves by the midpoint convention 8.0 → No. "Low double digits" → Yes. No descriptor → No.
### Fine Print
This is the RNPL module's pre-registered falsifier. Resolution date ~11 Feb 2027.

Conventions adopted (stated, not changing the question; registry: letter governs, call counts only if the letter is silent): (1) directional sentences are read against the printed 4Q26 rate and resolve Yes only when the sentence's own implication clears the bar — "relatively stable / similar to Q4" → Yes iff the 4Q26 print ≥ 8.2%; **"higher than Q4" → Yes iff the 4Q26 print ≥ 8.2%** [rev 2: was 7.5 in rev 1, corrected per A08-02 — a sentence implying only "> 7.5" does not imply ≥ 8.2]; "nearly as strong as Q4" (the 4Q22 form) → Yes iff the 4Q26 print ≥ 9.2% (a stated convention: "nearly" is read as within ~1 point; sensitivities at 8.7 and "never Yes" in §7 move the number by ≤ 1 point); "moderate / lower than Q4" with no bucket → No; (2) "approximately 9%", "around 9%", "high single digit to low double digit", "around 10%", "low double digits" → Yes; "mid-to-high single digits", "high single digits", "mid single digits" → No; (3) a nights descriptor embedded in the GBV sentence (the 4Q25 construction, "driven by high-single-digit growth in Nights and Seats Booked") counts; a GBV bucket with no nights qualifier → No (no descriptor); (4) the Feb print on its actual date; a leap-day or calendar adjustment stated by management does not change the resolution (the reported descriptor governs; 2027 has no calendar item of that kind).

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | February Q1 nights descriptors, all four explicit-y/y cases (verbatim, with the 4Q print and the 1Q actual): 4Q22 → "Nights and Experiences Booked year-over-year growth to be nearly as strong as Q4 2022" (Q4 printed 20.2; 1Q23 actual 18.6); 4Q23 → "we expect the growth rate of nights booked in Q1 2024 to moderate relative to Q4 2023" (12.0; 9.5); 4Q24 → "relatively stable compared to Q1 2024 after excluding Leap Day, which contributed to approximately one percentage point of growth in Q1 2024" (12.3 printed; comparator 8.5; 7.9); 4Q25 → "GBV to increase in the low teens year-over-year, driven by high-single-digit growth in Nights and Seats Booked" (9.8 printed; bucket 7–9, mid 8; 9.15). All four sat at or below the just-printed Q4 rate; three were 1–4 points below it. 4Q21 → "we expect Q1 2022 Nights and Experiences Booked to significantly exceed Q1 2019 levels" (comparator 83.1m; 1Q21 actual 64.4m, so merely exceeding 83.1m implied > +29.0% y/y — a provable Yes-type case by comparator, though without a y/y descriptor). Extract: [datasets/feb_letter_guides_4Q20-4Q25.csv](datasets/feb_letter_guides_4Q20-4Q25.csv) | `data/processed/overnight/02_guidance_ledger.csv`; `data/processed/overnight/02_kpi_panel_quarterly.csv` (1Q21 nights 64.4m); `data/raw/letters/4Q21_d251410dex991.htm`, `4Q22_d451233dex991.htm`, `4Q23_d646462dex991.htm`, `4Q24_d915198dex991.htm`, `4Q25_d58192dex991.htm` | 2022-02-15 to 2026-02-12 | 2026-09-17 | yes |
| 2 | [rev 2] Under this question's own convention the five February sentences would have resolved against an 8.2-type bar as follows: 4Q21 comparator → Yes-type (implied > 29%); 4Q22 "nearly as strong" with Q4 at 20.2 → Yes-type; 4Q23 "moderate" → No; 4Q24 "stable ex leap day" with a comparator of 8.5 → Yes-type (marginal); 4Q25 "high-single-digit" → No. **3 of 5** (rev 1 said 2 of 4 by excluding 4Q21 — A08-13). The three Yes-types came with Q4 prints of 25+ (2021 recovery), 20.2 and 12.3, far above the 8.2 bar; with a Q4 print near 8–9 the same directional forms resolve No or marginally, so the count is regime-dependent and is not used as the forecast | derived from claim 1 | 2026-09-17 | 2026-09-17 | yes |
| 3 | Bucket era (since the 3Q25 letter): the stated bucket midpoint sat 3.8 (3Q25→4Q25) and 1.8 (4Q25→1Q26) points below the printed rate when the comp hardened, and 0.7 above (2Q26→3Q26) when it eased; realised nights beat the bucket top in 2 of 2 resolved cases (by 3.82 and 0.15). "Buckets are the most beatable line in the letter" | C02 log claims 3–4; `docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md` §3.1–3.2; recomputed in `audits/A08-reproduce.py` | 2026-09-17 | 2026-09-17 | yes |
| 4 | [rev 2] Format base rate: **16 of 16** pre-2025 next-quarter nights guides in the ledger were directional (rev 1's "12 of 16" was wrong — A08-12); in the bucket era 3 of 4 were buckets (1Q26→2Q26 was directional: "slightly decelerate ... roughly 100bps headwind related to the conflict in the Middle East"); every letter since 2Q22 (17 of 17) carried a next-quarter nights sentence; C02 priced P(directional-only) ≈ 0.25 and P(no descriptor) 0.04. The 72 / 24 / 4 split used here is a **regime judgment** (bucket era n 4), not an empirical estimate | C02 log claims 1, 3, 20; `02_guidance_ledger.csv` filtered by print year < 2025 (`A08-reproduce.py`) | 2026-09-17 | 2026-09-17 | yes |
| 5 | 4Q26 nights views (the print management will have in hand): team baseline +8.1% (131.8m; band 8.0–8.9, case A NA-only lap 8.9 at the top), RNPL unified module +7.61% (band 6.6–8.4), Bloomberg MODL 134.0m (+9.9%, n 28, range 130–136m, 12 Sep screenshot), short case +5.0% (128.0m); C02's 4Q26 bucket vector (a) 0.21 / (b) 0.19 / (c) 0.39 / (d) 0.17 / (e) 0.04. 4Q25 base 121.9m (+9.82%) | `data/processed/h2_bridge_v3/h2_bridge_v3_rebased_lines.csv`; `data/processed/rnpl_short_audit/rnpl_nights_module.csv`; `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv`; `data/processed/margin_build/40_line_build/40_short_case_revenue_path.csv`; C02 log §6 | 2026-09-15 | 2026-09-17 | yes |
| 6 | Team 1Q27 nights objects: WS06 v2 base +8.21% (169.0m; includes a +1.0 Middle East base effect and a 40% ex-NA RNPL lap; bear 4.71, bull 10.52); RNPL module base +6.47% (166.3m; bear 5.28, bull 7.34) = team 8.17 less uplift lap −1.00, pull-forward −0.46, deferral −0.15, propensity −0.10; PR #32 NA-only lap 8.17 / global lap 6.42; B3 driver base +9.30. Sequential step 4Q26→1Q27 across these objects: +0.09 (v2), −1.14 (module), −0.73 (PR #32 NA-only), −2.48 (global) | `data/processed/margin_build/06_fy27_path_v2/06_comparison_quarterly.csv`; `data/processed/rnpl_short_audit/rnpl_nights_module.csv`; `data/processed/nights_quarterly_total.csv`; `data/processed/rnpl_short_audit/fy27_quarterly_phasing_rnpl_aware.csv` | 2026-09-14 | 2026-09-17 | yes |
| 7 | The 8.2% bar is PR #32's NA-only-lap FY27 rate (169.0m in 1Q27) and the module's pre-registered falsifier: "A 1Q27 guide at or above +8.2% in February kills the module (both the ex-NA lap and the pull-forward reversal would have to be absent)" | `docs/rnpl-short-audit/00_SYNTHESIS.md` §2 (February falsifier row), §5; `research/notes/nights_quarterly.md` | 2026-09-11 | 2026-09-17 | yes |
| 8 | [rev 2, corrected per A08-18] Comp arithmetic for 1Q27. The 1Q26 letter makes two separate statements: (i) on the Q1 print — "Absent the impact of the conflict, we estimate growth of Nights and Seats Booked would have been approximately 10% year-over-year" (reported 9.15%, i.e. a ~0.85pt conflict shortfall in the 1Q27 base); (ii) in the **Q2 2026 outlook** — "we expect Nights and Seats booked growth to slightly decelerate, relative to Q1 2026, assuming an estimated roughly 100bps headwind related to the conflict" (the 100bp figure is Q2's assumption, not Q1's shortfall; rev 1 conflated them). Relative to 4Q26's own comp (4Q25 printed 9.82), the reported 1Q26 comp (9.15) is 0.67pt easier; the ex-conflict comparator (~10%) is 0.18pt *harder*, not "1.65pt easier" as rev 1 said. Any 2027 recovery of the conflict-lost nights is a base effect worth up to ~+0.85pt on 1Q27 growth *if* cancellations normalise, and is inside WS06 v2's +1.0 Middle East base effect (claim 6). Against that, ex-NA RNPL (live 17 Feb–4 Mar 2026) laps for 5–6 of 13 weeks of 1Q27 and fully from 2Q27; the July 2026 eligibility expansion laps in 3Q27 | `data/raw/letters/1Q26_d23351dex991.htm` (Business and Financial Performance; Outlook Q2 2026); ledger D025–D029, D044; `docs/margin-build/notes/06_fy27_path_v2.md` findings 2, 5 | 2026-09-14 | 2026-09-17 | yes |
| 9 | Management tone into 2027: Chesky, 8 Sep 2026 Goldman conference: "Almost every market is accelerating. Almost every country is accelerating," "India is growing 60% year-over-year," "We're going to have some major announcements next year" (V023); 2Q26 call (Mertz): "Even against tougher comps in the back half of the year, we are raising our full year guidance"; management set the 3Q26 bucket at the printed rate with July in hand | `research/notes/q3nowcast/G_external-sources-q3-read.md` §1.8; `data/processed/margin_build/05_mgmt_statements_v2/05_statements.csv` V023; C02 log claim 7 | 2026-09-08 | 2026-09-17 | yes |
| 10 | Pre-registered 5 Nov card: a 4Q26 nights guide implying ≤7.5% supports the lap/drag hypothesis, ≥9.5% weakens it; a bundle figure ≥2.5 pts weakens it (C05 puts P(quantified ≥2.5) at 0.08) | `data/processed/overnight2/D/D1_prereg_thresholds.csv`; C05 log | 2026-09-11 | 2026-09-17 | no |
| 11 | [rev 2, corrected per A08-19] No market prices the 1Q27 nights guide. Kalshi KXABNBA FY26 nights ladder (captured 2026-09-17T03:18:45Z): >565m 0.79/0.88, >570m 0.63/0.71, >575m 0.37/0.41, >580m 0.19/0.28; lifetime `volume_fp` 0–294 contracts per strike (>575m: 277.2; open interest 87.0), `volume_24h_fp` 0 at every strike, `updated_time` 2026-08-04 on every market — an inactive, stale ladder, not "null" fields. Its implied FY26 ≈ 572m sits below what the Q3 ladder's ~148m and 1H26's 304.5m would leave for Q4 (≈120m, −1.6% y/y); the two ladders are adjacent snapshots of different populations at different times, so the comparison shows staleness rather than a mathematical inconsistency. Zero weight (C02 reached the same verdict). Polymarket public-search "Airbnb 2027" / "Airbnb guidance": nothing on 2027 | [sources/kalshi_KXABNBA_open_20260917T031845Z.json](sources/kalshi_KXABNBA_open_20260917T031845Z.json), [sources/kalshi_KXABNB_open_20260917T031845Z.json](sources/kalshi_KXABNB_open_20260917T031845Z.json), [sources/polymarket_search_airbnb_2027_20260917T031845Z.json](sources/polymarket_search_airbnb_2027_20260917T031845Z.json) | 2026-09-17 | 2026-09-17 | no |
| 12 | Reverse-DCF market-implied FY27 nights path 8–9% (Street/team base), management-delivered 10.0%; Bloomberg 4Q26 bar 9.9% — the only Street-side objects adjacent to a 1Q27 nights expectation | `docs/reverse_dcf/SYNTHESIS.md`; `docs/margin-build/notes/06_fy27_path_v2.md` comparison table | 2026-09-13 | 2026-09-17 | yes |
| 13 | Web recency (search snippets, pages not fetched): no analyst 1Q27 nights preview; the 4Q26 print date is not announced; final 72-hour neutral check found nothing bearing on the February guide | [sources/web_search_log.md](sources/web_search_log.md) | 2026-09-17 | 2026-09-17 | no |
| 14 | [rev 2] **Adopted 4Q26 nights object** (R16/B13, this run): blend 0.5 × decomposition V1 (3Q26 ~ N(9.67, 1.70) → 4Q26 = 8.1 + 0.5 × (Q3 − 9.67) + N(0, 1.4), 12% short tail 5.5 ± 1.5) + 0.3 × guide route V2 (C02's 5 Nov bucket vector × bucket midpoint + cushion N(0.9, 1.3)) + 0.2 × Street bar V3 (N(9.93, 1.23), MODL 134.0m ± 1.5m). As implemented here: mean 8.70, sd 2.05, median 8.78, P(≥134.0m) 0.29 (R16 quotes 0.27), P(≤131.0m) 0.27 (B13 0.26), P(< 7.5) 0.27, 7.5–8.5 0.17, 8.5–9.5 0.19, ≥ 9.5 0.36, P(≥ 8.2) 0.61. R16's "mean ~8.3" is the V1-conditional-means shortcut (0.27 × 10.7 + 0.73 × 7.5); the blend's mean is 8.7. Rev 1's print mixture (N(8.1, 1.6) + 12% tail) had mean 7.79 and P(≥134.0m) 0.12 | `questions/risk-q4-nights-print-meets-street/datasets/r16_model.py`, `r16_views.csv`; `questions/bonus-q4-nights-print-weak/datasets/b13_summary.csv`; [datasets/q4_adopted_v2_summary.csv](datasets/q4_adopted_v2_summary.csv) | 2026-09-17 | 2026-09-17 | yes |
| 15 | [rev 2] Monte Carlo (this log, `f01_model_v2.py`): P(Yes) **0.287** on the adopted object with the corrected resolver; by 4Q26 print: < 7.5 → 0.02 (weight 0.27), 7.5–8.5 → 0.11 (0.17), 8.5–9.5 → 0.29 (0.19), ≥ 9.5 → 0.56 (0.37); by format: bucket 0.28, directional 0.36, none 0. Decomposition of the move from rev 1's 0.183: resolver fix (up_floor 7.5 → 8.2, "nearly as strong" explicit) −0.010 on the old object; adopted object +0.113. On the rev-1 object the corrected tree gives 0.173. Sensitivities in [datasets/f01_v2_sensitivity.csv](datasets/f01_v2_sensitivity.csv) | [datasets/f01_v2_summary.csv](datasets/f01_v2_summary.csv) | 2026-09-17 | 2026-09-17 | yes |

Newest load-bearing source: the 14–15 Sep repo builds (claims 5–6) and the 17 Sep C02/R16/B13 logs (claim 14); 2–3 days old against a 147-day window. The 5 Nov print is the next real input.

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
13. [computed] `datasets/f01_model.py` (rev 1 base + 15 sensitivities)
14. WebSearch: Airbnb latest this week (final 72-hour neutral recency check — nothing new)
15. [rev 2, repo] `docs/pitch-forecasts/audits/A08-research-audit.md`; `audits/A08-reproduce.py` run from the repo root (`py -3.13 -B`; output in `A08-reproduce.stdout.txt`)
16. [rev 2, repo] `questions/risk-q4-nights-print-meets-street/` (R16 model, views, log §5–6); `questions/bonus-q4-nights-print-weak/` (B13); `questions/q4-revenue-guide-vs-street/forecasts/2026-09-17-forecast.json` (C01 rev 2)
17. [rev 2, repo] `data/raw/letters/1Q26_d23351dex991.htm` — the two Middle East sentences (claim 8); `02_kpi_panel_quarterly.csv` 1Q21 nights (claim 1); `02_guidance_ledger.csv` pre-2025 nights formats (claim 4); saved Kalshi JSON fields `volume_fp`, `volume_24h_fp`, `open_interest_fp`, `updated_time` (claim 11)
18. [rev 2, computed] `datasets/f01_model_v2.py` (adopted object + 26 sensitivities)

WebSearch calls charged to this batch: 5 across F01–F04 (none added in revision 2).

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, Nights and Seats Booked, "high single digits", Reserve Now Pay Later, 4Q26 shareholder letter, February 2027

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| "High single digits" repeated for 1Q27 (the modal outcome; resolves No) | leading (≈0.45 of all outcomes) | Every repo model has 1Q27 at 6.4–8.2 (claim 6); the February descriptor has sat at or below the Q4 print 4 of 4 explicit cases (claim 1); a 4Q26 print of ~8–9 with a bucket 1 point below it is "high single digits" or "mid-to-high single digits" |
| "Low double digits" / "around 10" / "similar to Q4" with Q4 ≥ 8.2 (Yes) | kept, 0.28 | Needs a 4Q26 print ≥ 8.5–9.5 (P ≈ 0.55 on the adopted object, 0.36 on the rev-1 object) and management choosing to guide at or above it; the 5 Nov "low double digits" bucket branch alone gives 0.67 |
| Directional "moderate relative to Q4" with no bucket (No) | kept inside the 0.24 directional share | The 4Q23 form; used when the comp hardens or October/January is noisy; the reported 1Q27 comp is 0.67pt easier than 4Q26's, which lowers its odds and raises "stable/similar" — but "similar" only resolves Yes if the Q4 print itself is ≥ 8.2 |
| A numeric point ("approximately 9%") | inside Yes via the 8.5–9.5 bucket split (0.45) | Airbnb has given numeric nights guides only as buckets; a hyphenated "high single to low double" is the more likely Yes-form |
| Use the Kalshi FY26 ladder as the 4Q26 conditioning | discarded | inactive and stale (claim 11) |
| Management guides 1Q27 on an ex-lap or ex-conflict basis ("excluding the RNPL comparison") | discarded as a resolution route | The reported descriptor governs; a stated ex-item rate would be a number for the reported quarter only if management said so |
| The ex-NA RNPL lap is absent (module falsified) so the descriptor is ≥ 8.2 by construction | kept as the bull branch (Street-centred print, Δ +0.1, cushion 0.5): P 0.57 | This is the branch the question is designed to detect; it needs the 4Q26 print to land at the Street's 9.9 rather than the team's 8.1 — the adopted object gives that 0.2 weight directly (V3) |
| [rev 2] Use rev 1's own print mixture (mean 7.8) rather than the adopted R16/B13 object | discarded | The run adopts one 4Q26 distribution for every question that conditions on the Q4 print (R16/B13 coherence note); the rev-1 mixture was the V1 decomposition alone, which R16 weights 0.5 |

## 5. Independent Estimates
[rev 2] Independence label (A08-03): the three estimates below are **partially dependent** — all three read the same February letters and the same 4Q26 object; the anchor is a model-created probability, not an observed price. Agreement between them is not independent corroboration.
- base_rate_estimate: 0.24 — reference class "February Q1 nights descriptor vs the Q4 print" (claims 1–2): 4 of 4 explicit descriptors at or below the print, 3 of 4 by 1–4 points; P(Yes) ≈ P(4Q26 print ≥ 9.2) × P(descriptor within 1pt | that) + P(print in 8.2–9.2) × P(descriptor at the print | that) ≈ 0.42 × 0.45 + 0.19 × 0.25 ≈ 0.24, with the print distribution from claim 14 (rev 1: 0.19 on the mean-7.8 mixture)
- decomposition_estimate: 0.29 — the tree in claim 15: adopted 4Q26 object → management's 1Q27 expectation = print + N(−0.4, 1.2) (the mean of the team objects' 4Q26→1Q27 steps is −1.0; management's beat record argues for less) → format (bucket 0.72 / directional 0.24 / none 0.04) → bucket midpoint = expectation − N(1.0, 0.9) → language map (≥9.5 Yes; 8.5–9.5 Yes 0.45; 7.5–8.5 Yes 0.10; <7.5 Yes 0.02; directional per the §0b conventions with "higher" at 8.2 and "nearly as strong" at 9.2)
- anchor_estimate: 0.43 — no market; the Street-side object is Bloomberg's 4Q26 bar 9.9% (n 28, 12 Sep) pushed through the same tree as a certain centre with no short tail (NOT_INDEPENDENTLY_DERIVED: the anchor shares the tree's step, format, cushion and language map; only the print centre is the Street's). The reverse-DCF market path's FY27 nights 8–9% sits at the bar
- anchor_value: 0.43 (Bloomberg MODL 4Q26 nights 134.0m / +9.9%, screenshot 2026-09-12, through the tree; NO tradable market, Kalshi ladders zero weight)
- final_estimate: 0.28 (credible interval 0.16–0.42)
- final_minus_anchor: −15 points. Named asymmetry: the anchor treats the Street's Q4 bar as certain; the adopted object gives it 0.2 weight against the team decomposition (0.5, mean 7.8) and the guide route (0.3), and every repo 1Q27 object sits at or below the bar (claim 6). The base rate and the decomposition sit at 0.24–0.29; the rev-1 +0.04 judgment for the bull branch is dropped because the adopted object now carries the guide route and the Street bar explicitly. Astra's independent estimate is 0.26 (three judgmental states); this revision lands 2 points above it

## 6. Final Numbers
**Binary.** P(1Q27 nights descriptor implies ≥ +8.2% y/y, ≥169.0m) = **0.28**, credible interval **0.16–0.42**.
Structure: the tree on the adopted 4Q26 object (0.287), rounded; no separate judgment term (rev 1 added +0.04 for the bull branch, now inside V2/V3 of the adopted object). Inside the number: P(no descriptor) 0.04 (No), P(directional-only) 0.24 (Yes only via "similar/stable/higher" with a Q4 print ≥ 8.2 or "nearly as strong" with ≥ 9.2, ≈ 0.09 of the 0.28), bucket ≈ 0.20 of the 0.28.
Coherence: P(4Q26 print ≥ 8.2) ≈ 0.61 (adopted object); P(management's internal 1Q27 expectation ≥ 8.2) ≈ 0.53; the descriptor sits below the expectation, so P(Yes) < 0.53. With R16/B13: P(4Q26 ≥ 134.0m) 0.29 and P(Yes | that band) ≈ 0.56 account for 0.20 of the 0.28. For the RNPL module: a Yes falsifies it; P(falsified) 0.28 is consistent with the module's own bull case (7.34) sitting below the bar.
Extreme-probability gate: not triggered (0.28).

## 7. Sensitivity
Single-assumption reruns of `datasets/f01_model_v2.py` from the base tree (0.287); the final carries the same deltas.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Adopted 4Q26 object (mean 8.7; 0.5/0.3/0.2 blend) | rev-1 mixture N(8.1,1.6)+12% tail: 0.17; V1 decomposition only: 0.18; equal thirds: 0.33; V1 centre 7.61 (RNPL module): 0.26; V1 centre 8.9 (case A): 0.33; Street bar 9.93 certain, no tail: 0.43 |
| Resolver: "higher than Q4" Yes iff print ≥ 8.2 | rev-1 7.5: 0.29 (+0.4pt); "nearly as strong" never Yes: 0.28; Yes iff ≥ 8.7: 0.29 |
| Management's 1Q27 step vs the Q4 print −0.4 | WS06 v2 +0.1: 0.36; RNPL module −1.1: 0.20; PR #32 global lap −2.5: 0.08 |
| Bucket cushion 1.0 (expectation less 1pt) | none (guide at expectation): 0.39; 2.0 (3Q25/4Q25 style): 0.21 |
| Format: bucket 0.72 / directional 0.24 | directional 0.45: 0.30; bucket 0.90: 0.28 |
| 8.5–9.5 midpoint → Yes 0.45 (hyphenated / "approximately 9%") | 0.25: 0.27; 0.65: 0.31 |
| 5 Nov 4Q26 bucket (conditioning, V2 branch certain) | "low double digits": 0.67; "around 10": 0.54; "high single digits": 0.28; "mid single / moderate": 0.07 |
| Joint bull (Street-centred print 9.9, no tail, step +0.1, cushion 0.5) | 0.57 |
| Joint bear (V1 centre 6.5, step −1.1, cushion 2.0) | 0.11 |

Pre-mortem ("it is 11 Feb 2027 and the letter said 'low double-digit growth in Nights and Seats Booked' for 1Q27"): (1) 4Q26 printed ≥ 9.5% — the Street's bar, not the team's; the ex-NA fee/cancellation lap was smaller than WS-D's 0.7–0.9 pts or the July RNPL expansion offset it — priced at 0.36 through the adopted object (V2/V3 carry it); (2) January bookings ran double digits on the conflict-depressed base (claim 8: up to ~0.85pt of base effect) and management guided at the run-rate, as it did for 3Q26 — priced via Δ ≥ +0.1 and cushion ≤ 0.5 (the bull row); (3) a new 2027 product (R08) or an RNPL extension was launched in January and management chose the bucket to showcase it — not separately priced, inside the format/Δ draws (~0.03); (4) management gave "high single digit to low double digit", a hyphenated form it has used for FY revenue but never for nights — priced at 0.45 of the 8.5–9.5 bucket. Asymmetry: the memo's use of this question is as the module's falsifier; a confident No that resolves Yes would mean the RNPL lap story was wrong, which is exactly the case the interval's top (0.42) is meant to hold.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-18 to 2026-10-02 | September Inside Airbnb dumps; 3Q26 nights band refreshed | Each +0.5pt on the 3Q26 centre moves the V1 4Q26 centre ~+0.25 (pass-through 0.5) and P(Yes) ~+0.015 |
| 2026-10-02 | Prelim memo freeze | Quote 0.28 (0.16–0.42); say it is the module's falsifier and that a 4Q26 print ≥ 9.5 is the path to Yes |
| 2026-11-05 | 3Q26 print: 4Q26 nights bucket (C02), bundle figure (C05), RNPL share (C06), 3Q26 print | Re-set the 4Q26 object on the bucket (§7 row): "low double digits" → ~0.67; "around 10" → ~0.54; "high single digits" → ~0.28; "mid single digits"/"moderate" → ~0.07. A bundle figure ≥ 2.5 pts: +0.05 |
| 2026-12-01 to 2027-01-31 | Kalshi 4Q26 nights ladder if listed; STR/NTTO/Similarweb for October–December; EXPE/BKNG Q4 guides (EXPE reads through) | Re-set the 4Q26 print sd (2.05 → ~1.0 by late January); EXPE guiding Q1 room nights ≥ its Q4 rate: +0.03 |
| 2027-01-20 to 2027-01-31 | Airbnb announces the 4Q26 call date | Fix the resolution date |
| 2027-02-11 (est.) | 4Q26 letter: 4Q26 nights print and the 1Q27 descriptor | Resolve per the §0b conventions; read the GBV sentence for an embedded nights descriptor before resolving "no descriptor". Audit read: at a 4Q26 print < 7.5 the pre-print P was ≈ 0.02; 7.5–8.5 ≈ 0.11; 8.5–9.5 ≈ 0.29; ≥ 9.5 ≈ 0.56 |

## 10. Revision notes
| Change | Finding |
|---|---|
| "Higher than Q4" resolves Yes only if the 4Q26 print ≥ 8.2 (was 7.5); "nearly as strong" made explicit (Yes iff ≥ 9.2, sensitivities 8.7 / never). Effect on the rev-1 object: 0.183 → 0.173 | A08-02 (accepted) |
| 4Q26 print replaced by the adopted R16/B13 object (mean 8.7, P(≥134.0m) 0.29); tree 0.173 → 0.287; final 0.22 → 0.28; interval 0.12–0.35 → 0.16–0.42 | run instruction (one 4Q26 object); reconciles with Astra's 0.26 |
| Rev-1 "+0.04 bull-branch judgment" dropped (now inside V2/V3) | A08-02 / A08-03 |
| §5 relabelled: estimates partially dependent; anchor NOT_INDEPENDENTLY_DERIVED (Street bar through the tree = 0.43); Astra's 0.26 recorded | A08-03 (accepted) |
| Format base rate corrected to 16/16 directional pre-2025; 72/24/4 split labelled a regime judgment | A08-12 (accepted) |
| 4Q21 comparator case added (implied > 29%); reference-class count 3/5, explicitly not used as the forecast | A08-13 (accepted) |
| Claim 8 rewritten: the 100bp figure is the Q2 2026 outlook assumption; ex-conflict comparator 0.18pt harder, reported comp 0.67pt easier; recovery modelled as a base effect inside WS06 v2's +1.0 | A08-18 (accepted) |
| Claim 11 rewritten with the actual Kalshi fields (`volume_fp`, `volume_24h_fp`, `open_interest_fp`, `updated_time`); "inconsistent" → "stale adjacent snapshots" | A08-19 (accepted) |
| Monitoring calendar re-keyed to the adopted object's conditional table | consequence of the above |

RESUME: the next agent (X01 / synthesis) should read the F01 number as 0.28 on the adopted 4Q26 object and take the 5 Nov bucket row of §7 as the update rule; re-run `datasets/f01_model_v2.py` if R16/B13 change their blend (the sampler `q4_adopted` mirrors `r16_model.py` and must be kept in step). The remaining load-bearing judgments are the management step Δ (−0.4) and the bucket cushion (1.0), each worth ±0.08.
