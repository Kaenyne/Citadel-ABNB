# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A08). Companion question: F04 `fy27-sm-share-above-219` (conditioned on this vector); F01/F02 share the batch. Reproduction: [datasets/f03_model.py](datasets/f03_model.py) (numpy only, seed 20260917, 400,000 draws, ~5 s; writes `f03_sensitivity.csv`).

## 0. Metadata
- question_name: fy27-margin-guide
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` F03)
- type: multiple_choice
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
What FY27 adjusted EBITDA margin guidance will Airbnb give at the Feb print?
### Resolution Criteria
**Type.** Multiple choice. **Options.** (a) ≥36.5% floor or point; (b) 36.0–36.4%; (c) 35.5–35.9%; (d) <35.5%, "down year over year", or an explicit investment-year framing; (e) no numeric FY27 margin guidance.
### Fine Print
Resolves on the floor if "at least X%" is used, on the midpoint if a range. Resolution date ~11 Feb 2027.

Conventions adopted (stated here, priced in §5–7; they do not change the question): (1) a qualitative flat sentence ("stable year-over-year", "maintain the strong margin we delivered in 2026", "in line with 2026" — the Feb 2022/2023/2026 forms) pins the level at the FY26 reported margin and resolves in the bucket containing that reported figure (to one decimal as the letter prints it); (2) a qualitative expansion sentence ("modestly higher", "expand") resolves in the bucket containing FY26 reported + 0.5pt (management's smallest numeric step); (3) any explicit down/lower/investment-year framing resolves (d) whatever the level (option text); (4) (e) is reserved for no FY27 margin sentence at all, an FY27 adjusted EBITDA dollar sentence with no margin, or a sentence with no identifiable level ("we will continue to invest while delivering strong profitability"); (5) letter governs; the call fills a silent letter. The strict alternative — every qualitative sentence resolves (e) — is reported as a sensitivity (it moves 0.38 of mass into (e)).

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Every February letter since 4Q21 has carried a full-year margin sentence (5 of 5), verbatim: FY22 "we would expect Adjusted EBITDA margin to be directionally in-line with 2021" (prior actual 26.6; delivered 34.6); FY23 "we expect to maintain the strong Adjusted EBITDA margin we delivered in 2022" (34.6; 36.8); FY24 "we expect to maintain an Adjusted EBITDA Margin of at least 35%, providing us flexibility to invest in incremental growth opportunities" (prior 36.84, floor −184bp; 36.4); FY25 "we plan to invest $200 million to $250 million towards launching and scaling new businesses ... Inclusive of these investments, we expect to deliver a full-year Adjusted EBITDA Margin of at least 34.5%" (prior 36.40, −190bp; 35.1); FY26 "we expect our Adjusted EBITDA Margin to be stable year-over-year as we reinvest top-line efficiencies to support growth across the business, primarily in marketing, product, and technology" (prior 35.10, 0). Qualitative-flat 3, numeric floor with a ~185bp haircut 2, down/expand/none 0. Extract: [datasets/feb_letter_guides_4Q20-4Q25.csv](datasets/feb_letter_guides_4Q20-4Q25.csv) | `data/raw/letters/4Q21_d251410dex991.htm`, `4Q22_d451233dex991.htm`, `4Q23_d646462dex991.htm`, `4Q24_d915198dex991.htm`, `4Q25_d58192dex991.htm`; `data/processed/overnight/02_guidance_ledger.csv` | 2022-02-15 to 2026-02-12 | 2026-09-17 | yes |
| 2 | Under this question's buckets the five February sentences would have resolved: FY22 (c-type: 26.6 in-line, i.e. the bucket of the prior print), FY23 (bucket of 34.6), FY24 "at least 35%" (bucket 1.8pt below the print), FY25 "at least 34.5%" (1.9pt below), FY26 "stable" (bucket of 35.1). With FY26 expected to print 35.5–36.4, the haircut form lands in (d) and the flat form in (c)/(b) | derived from claim 1 | 2026-09-17 | 2026-09-17 | yes |
| 3 | The February floor is not mechanical: M3's February rule (prior actual minus the mean past haircut) has MAE 0.82pp, "blown by the two regime breaks (Feb 2024 no haircut history, Feb 2026 'stable' instead of a haircut)" — P4 failed; "the February sentence is where the reinvestment decision for the year is actually made". WS05: "February 2027 FY27 floor: FY26 actual minus 0–190bp (n 3: −184, −190, 0)". H12: "The FY27 guide will be a floor at or slightly below the FY26 print, not a step down ... A step-change in AI opex is the one stated risk" | `docs/margin-build/notes/M3_guide_policy_margin.md` (February rule, P4); `docs/margin-build/notes/05_mgmt_statements_v2.md` §"5 Nov 2026 scenarios"; `data/processed/margin_build/05_mgmt_statements_v2/05_fy27_hints.csv` H12 | 2026-09-14 | 2026-09-17 | yes |
| 4 | FY26 actual (known at the print): team margin build 35.73% ($5,098M) and line build 35.7% ($5,099M); Street 35.62% (LSEG n 44, 11 Sep); floor "at least 35.5%"; C04's November-stage internal FY26 MC mean 35.74, sd 0.53 (p10 35.06, p90 36.42); the November point has been beaten by +10 / +90 / +77bp (n 3) and the Feb floor by +60 / +140bp; no FY margin floor has ever been missed; the FY26 floor breaks on a 2H26 revenue shortfall of 0.6–0.9% with the marketing cut as the defence | `docs/margin-build/SYNTHESIS.md` §3; `notes/40_line_build.md`; C04 log claim 24; `05_guide_language_stats.csv`; `23_fy26_floor_breakeven.csv` | 2026-09-17 | 2026-09-17 | yes |
| 5 | C04 (this run): 5 Nov FY26 sentence (a) held 35.5 0.26 / (b) ~36% 0.42 / (c) ≥36.5 0.05 / (d) softer 0.24 / (e) 0.03; the November sentence then converts to the FY26 print with a +0.1 to +0.9 beat | `docs/pitch-forecasts/questions/fy26-margin-sentence/research-log.md` §6 | 2026-09-17 | 2026-09-17 | yes |
| 6 | Team FY27 margin views: run 34.64% ($5,483M; bear 32.15 / bull 36.53), line build 35.7% ($5,644M; scenario grid 29.5–40.0), short case 31.9%; Street FY27 36.45% ($5,766M, n 44, sd $154M); FY27 incremental margin 24.7% (run) / 34.8% (line build) vs the Street's 43.7%; "the company has given no FY27 margin guidance — WS05 found no FY27 margin hint in any letter or call" | `docs/margin-build/SYNTHESIS.md` §3; `notes/40_line_build.md`; `data/processed/margin_build/23_final_model/23_vs_consensus.csv`; `40_line_build/40_annual.csv`, `40_short_case_summary.csv` | 2026-09-15 | 2026-09-17 | yes |
| 7 | Management on 2027 margin: Mertz 6 Aug 2026 "I'm not going to give you a specific guide for 2027 and beyond, but I think looking at our track record, you can even see a couple of things" (S179); "given the track record and the somewhat steady EBITDA margins that we have delivered, I think you can see there's a relative floor in our ability to continue to invest against that" (S164); "where we have those opportunities, we will lean in" (S180); FY26 guide "assumes a material increase in terms of the AI spend over the course of the year" (S162). Chesky 8 Sep 2026: "We basically have remained pretty steady, 35% margins" (V017); "It's really actually hard to invest a lot of money in this business" (V018); "We're going to have some major announcements next year" (V023) | `data/processed/margin_build/05_mgmt_statements_v2/05_statements.csv` S162, S164, S179, S180, V017, V018, V023 | 2026-09-08 | 2026-09-17 | yes |
| 8 | Cost profile management is describing for FY27 (WS05 hints): AI/hosting ramp in 2H26 means FY27 carries a full year of it (H02, H03: purchase obligations ~$465M/yr in 2027–28 vs $219M in 2026); S&M +30% in 1H26 with $258M of emerging-market and partnership marketing, "FY27 S&M growth above revenue growth is the base case" (H08); launches before revenue in FY27 (H07, FY25's launch cost $200–250M); ops per booking still falling (H05); "Net: management is describing a flat-to-slightly-up FY27 margin held by the floor policy, with the mix of cost inflation moving from marketing to hosting/AI" | `05_fy27_hints.csv`; `docs/margin-build/notes/05_mgmt_statements_v2.md` bottom line 1 | 2026-09-14 | 2026-09-17 | yes |
| 9 | Precedent for the investment-year framing: Feb 2025 named a $200–250M new-business investment and cut the floor 190bp below the print (still "at least", never "down"); Feb 2024 cut 184bp with "flexibility to invest"; the FY25 investment guide was itself cut mid-year (225 → 200, 2Q25). Airbnb has never printed the words "down year-over-year" for a full-year margin | claim 1; `05_guide_language_pattern.csv`; `PREREG_ABNB-INT-v1.md` INT-19 baseline | 2026-09-11 | 2026-09-17 | yes |
| 10 | Reaction context (not used in the number): the FY margin action at every February since 2022 is coded "first" (a new FY guide); the February prints were up-days 6 of 6; Wedbush/Oppenheimer read the Feb 2025 "at least 34.5%" as 100–150bp above buyside expectations | `data/processed/abnb_guidance_reaction_panel.csv`; [sources/web_search_log.md](sources/web_search_log.md) query 3 | 2026-09-17 | 2026-09-17 | no |
| 11 | No market prices this item (Kalshi KXABNB/KXABNBA are nights ladders; Polymarket has nothing on 2027 Airbnb items; fetched 2026-09-17T03:18:45Z) | [sources/kalshi_KXABNBA_open_20260917T031845Z.json](sources/kalshi_KXABNBA_open_20260917T031845Z.json); [sources/polymarket_search_airbnb_guidance_20260917T031845Z.json](sources/polymarket_search_airbnb_guidance_20260917T031845Z.json) | 2026-09-17 | 2026-09-17 | no |
| 12 | Monte Carlo (this log): FY26 actual A ~ N(35.85, 0.55) with an 85% floor-defence (A ≥ 35.5 + |N(0, 0.12)|) and a 15% miss branch N(35.4, 0.4) → P(A < 35.5) 0.09, 35.5–35.9 0.57, 36.0–36.4 0.24, ≥ 36.5 0.10; sentence regimes T1 haircut floor (A − U(1.0, 2.0), rounded down to 0.5) 0.20, T2 floor at the print rounded down to 0.5 (0–25bp) 0.22, T3 qualitative flat 0.30, T4 expand 0.08, T5 explicit down / investment year 0.10, T6 none 0.10 → vector a 0.081, b 0.165, c 0.268, d 0.386, e 0.100; by regime: T1 → d 0.97; T2 → c 0.43 / d 0.30 / b 0.20; T3 → c 0.54 / b 0.26 / a 0.12 | [datasets/f03_sensitivity.csv](datasets/f03_sensitivity.csv) (base row); script stdout | 2026-09-17 | 2026-09-17 | yes |
| 13 | Web: no analyst note on the FY27 margin guide found; the 4Q26 print date is not announced; final 72-hour check found nothing on 2027 guidance | [sources/web_search_log.md](sources/web_search_log.md) | 2026-09-17 | 2026-09-17 | no |

Newest load-bearing source: the 14–15 Sep margin-build notes and the 17 Sep C04 log; 2–3 days old against a 147-day window. The 5 Nov FY26 sentence is the next real input.

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`; skill files; example log; finished logs C01, C02, C04/C09, C05–C07
2. [repo] `docs/margin-build/SYNTHESIS.md` §3, §9; `notes/40_line_build.md`; `notes/M3_guide_policy_margin.md` (February rule, P4, cushion history); `notes/05_mgmt_statements_v2.md`; `data/processed/margin_build/05_mgmt_statements_v2/05_fy27_hints.csv`, `05_statements.csv` (V015–V026; rows dated ≥ 2026-08-01 on margin/S&M)
3. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv` — every 4Q-print row (FY margin, Q1 margin, S&M); `abnb_guidance_reaction_panel.csv` fy_margin_action / fy_margin_floor_vs_prior_fy
4. [repo] Outlook sections of the 4Q22, 4Q23, 4Q24, 4Q25 letters (regex extract; FY22 sentence from the ledger's 4Q21 row)
5. [repo] `data/processed/margin_build/23_final_model/23_vs_consensus.csv`; `40_line_build/40_annual.csv`, `40_params.csv`, `40_sensitivities.csv`, `40_short_case_summary.csv`
6. [Kalshi API] KXABNBA, KXABNB open markets; [Polymarket API] public-search "Airbnb 2027", "Airbnb guidance" (2026-09-17T03:18:45Z)
7. WebSearch: Airbnb news (batch-shared neutral pass)
8. WebSearch: Airbnb marketing spend 2027 margin investment analysts
9. WebSearch: Airbnb fourth quarter 2026 results date February 2027 (batch-shared)
10. [computed] `datasets/f03_model.py` (base + 10 sensitivities)
11. WebSearch: Airbnb latest this week (final 72-hour neutral recency check — nothing new)

WebSearch calls charged to this batch: 5 across F01–F04.

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, 4Q26 shareholder letter, "at least 35%", "stable year-over-year", AI spend, 2027 launches, February 2027

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| A numeric floor 100–200bp below the FY26 print (the Feb 2024/2025 form) → (d) | leading component of (d) (T1 0.20) | 2 of the last 3 Februaries; the 2027 launch/AI cost profile (claim 8) is the same set-up as Feb 2025's $200–250M; but Feb 2026 broke the form with "stable" and the FY26 floor was raised twice mid-year, so it is not the modal regime |
| A qualitative flat sentence ("stable"/"maintain") → bucket of the FY26 print, mostly (c) | leading regime (T3 0.30) | 3 of 5 Februaries; Chesky's "pretty steady, 35% margins" and Mertz's "relative floor" (claim 7) are the flat-margin narrative; it lands in (c) 0.54 / (b) 0.26 because the FY26 print is expected at 35.5–36.4 |
| A numeric floor at the print rounded down ("at least 35.5%") | kept (T2 0.22) | the natural sentence when the print is 35.5–36.0 and management wants a numeric floor without a visible cut; splits c/d/b on the rounding |
| Explicit "down year-over-year" or an investment-year framing | kept (T5 0.10) | never used for a full year (claim 9); the 2027 launches (V023) and the AI ramp are the mechanism; B12 prices the same object |
| Expansion language / a floor above the print | kept (T4 0.08) | the Street's FY27 36.45% needs it; management has never guided a February expansion; 1H26 operating leverage and the "relative floor" language make it a live minority |
| No FY27 margin sentence, or a dollar-only sentence | tail (T6 0.10) | 0 of 5 Februaries; Mertz's "I'm not going to give you a specific guide for 2027" was said in August about the August call, and every February has carried a sentence; 0.10 holds the strict-convention risk that a vague sentence with no identifiable level is read as (e) |
| The Street's FY27 36.45% is management's number | discarded | The Street sits above every management guide historically ("priced for the floor" in FY26; the Feb floor has been 60–190bp below the eventual print, and the Street's FY27 incremental margin 43.7% needs the S&M ramp to stop, claim 6) |
| Strict convention: every qualitative sentence → (e) | reported as a sensitivity (e 0.48) | The question's (d) explicitly includes qualitative "down year over year", so the question intends qualitative sentences to map when their level is identifiable; the convention is stated in §0b and the audit can choose |

## 5. Independent Estimates
- base_rate_estimate: (a) 0.07, (b) 0.15, (c) 0.30, (d) 0.42, (e) 0.06 — reference class "February FY margin sentence" (claim 1): qualitative-flat 3/5 → bucket of the FY26 print (P(c) 0.57, (b) 0.24, (a) 0.10, (d) 0.09 from the FY26 distribution in claim 12); numeric haircut floor 2/5 → (d); Laplace mass 0.06 for the unobserved "none" and folded into (d) for "down"
- decomposition_estimate: (a) 0.08, (b) 0.17, (c) 0.27, (d) 0.39, (e) 0.10 — the regime × FY26-print Monte Carlo in claim 12
- anchor_estimate: (a) 0.03, (b) 0.07, (c) 0.30, (d) 0.55, (e) 0.05 — no market; the designated anchor is the repo's own registered prior (WS05, 14 Sep: "February 2027 FY27 floor: FY26 actual minus 0–190bp (n 3)"; H12: "a floor at or slightly below the FY26 print") mapped through the FY26-print distribution (A − U(0, 1.9) < 35.5 with P ≈ 0.75, in 35.5–35.9 ≈ 0.20)
- anchor_value: P(d) = 0.55 (repo prior WS05/H12, 2026-09-14)
- final_estimate: (a) 0.08, (b) 0.17, (c) 0.27, (d) 0.38, (e) 0.10
- final_minus_anchor: −17 points on (d), the anchor's leading option. Independently derived: the anchor assumes the numeric-floor form every time; the base rate weights the qualitative-flat form by its 3-of-5 frequency, which the 14 Sep prior did not, and the decomposition adds the expand/down/none regimes. The base rate and the decomposition agree within 3 points on every option; the final is the decomposition with (d) trimmed 1 point toward the base rate

## 6. Final Numbers
| Option | Probability |
|---|---|
| (a) ≥36.5% floor or point | 0.08 |
| (b) 36.0–36.4% | 0.17 |
| (c) 35.5–35.9% | 0.27 |
| (d) <35.5%, "down year over year", or an explicit investment-year framing | 0.38 |
| (e) no numeric FY27 margin guidance | 0.10 |
Sum 1.00. Within (d): numeric floor ≥ 100bp below the print ≈ 0.22, floor at the print rounded below 35.5 ≈ 0.06, explicit down / investment year ≈ 0.10. Within (c): "stable/maintain" with a 35.5–35.9 print ≈ 0.16, "at least 35.5%" ≈ 0.11. Leading-option credible range (d): 0.28–0.58 (the §7 span).
Under the strict convention (qualitative sentences → e): (a) 0.02, (b) 0.05, (c) 0.10, (d) 0.36, (e) 0.48.
Coherence: with B12 (guide FY27 margin below FY26 actual or an explicit investment-year framing) — P(B12) should sit near P(d) less the part of (d) that is a floor below 35.5 with an FY26 print also below 35.5 (~0.03), i.e. ≈ 0.35. With F04: P(S&M ≥ 21.9% | option) is given in the F04 log (a 0.25, b 0.40, c 0.52, d 0.70, e 0.55).
Extreme-probability gate: no option ≤ 2%; (a) at 0.08 and (e) at 0.10 were audited anyway — edge cases priced: a range sentence resolving on its midpoint (inside a/b/c), a "stable" sentence with a 36.5 print (inside a), a dollar-only FY27 guide (inside e), the print date moving (no effect).

## 7. Sensitivity
Single-assumption reruns of `datasets/f03_model.py` from the base vector (a 0.08 / b 0.17 / c 0.27 / d 0.39 / e 0.10).
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| FY26 print centred 35.85 (team 35.7, Street 35.6, November-point beat +0.1 to +0.9) | 35.6: a 0.04, b 0.14, c 0.31, d 0.41; 36.1: a 0.14, b 0.18, c 0.21, d 0.36; 36.4: a 0.24, b 0.18, c 0.15, d 0.33 |
| Regime weights T1 0.20 / T3 0.30 | haircut dominant (T1 0.40, T3 0.15): d 0.58, c 0.18; flat dominant (T3 0.45, T1 0.10): d 0.28, c 0.35, b 0.20 |
| Explicit down / investment year 0.10 | 0.25: d 0.52, c 0.21 |
| Expansion language 0.08 | 0.20 (bull): a 0.12, b 0.22, d 0.32 |
| Floor defence 0.85 (FY26 print ≥ 35.5) | 0.50: d 0.49, c 0.24 |
| Convention: qualitative sentences map to the FY26 print's bucket | strict (all qualitative → e): e 0.48, d 0.36, c 0.10, b 0.05, a 0.02 |

Pre-mortem ("it is 11 Feb 2027 and the letter said 'at least 36.5%'", P 0.08): (1) FY26 printed ≥ 36.3 on a Q4 beat of 3–4pts (as in 2023–24) and management held the print as the floor — priced through the FY26 tail (0.10) × T2/T4; (2) the S&M ramp was explicitly declared over ("marketing to grow below revenue in 2027") — B03/F04's low branch, inside T4; (3) the Street's 36.45% became the number management chose to meet — not separately priced. The opposite miss ("no FY27 margin sentence at all", 0.10): Mertz's August refusal repeated in February with a long-term framework instead; priced at T6. Asymmetry: the memo's short case leans on (d) ("investment year"); at 0.38 it is the modal but not the majority outcome, and the memo should say "more likely than any other single form, less likely than not".

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-10-02 | Prelim memo freeze | Quote the vector; state the convention and the strict-reading alternative |
| 2026-11-05 | 3Q26 letter: FY26 sentence (C04), Q4 margin sentence (C09), 4Q26 revenue range, any 2027 investment language | FY26 "approximately 36%": FY26 print centre → 36.1 (a 0.14, d 0.36); held "at least 35.5%" or softer: centre → 35.6 (d 0.41, c 0.31). Any explicit 2027 investment sentence: T5 0.10 → 0.20 (d +0.06) |
| 2026-11-05 to 2026-12-15 | Sell-side FY27 margin revisions after the print; LSEG FY27 mean and sd | If the Street's FY27 margin falls below 36.0, T4 → 0.05 and (a)/(b) −0.03; if it rises above 36.8, T4 → 0.12 |
| 2027-01-15 to 2027-02-05 | 2027 product announcements (V023), any pre-announced launch budget; the 4Q26 call date | A named 2027 launch programme with a dollar figure: T5/T1 +0.10 jointly (d +0.08) |
| 2027-02-11 (est.) | 4Q26 letter: FY26 print, FY27 margin sentence | Resolve per §0b; record the exact sentence for F04's conditional and for B12 |

RESUME: the next agent (audit response) should re-run `datasets/f03_model.py` (deterministic, ~5 s), verify claim 1 against the five February letters, and attack the two load-bearing choices: the regime weights (haircut floor 0.20 vs qualitative flat 0.30) and the convention that qualitative sentences map to the FY26 print's bucket. Both are in §7; the leading option moves between 0.28 and 0.58.
