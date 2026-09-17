# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A03). Companion question: C04 `fy26-margin-sentence` (shared evidence base and Monte Carlo, `datasets/mc_sentence_model.py`; the C04 log carries the fuller claims ledger on the FY sentence and the two logs cite the same source files).

## 0. Metadata
- question_name: q4-margin-direction-sentence
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` C09)
- type: multiple_choice
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-16
- close_date: 2026-11-05
- resolution_date: 2026-11-05
- scoring: spot
- cp_visible: no
- cp_value: n/a

## 0b. Question (verbatim)
### Title
What will Airbnb say about 4Q26 adjusted EBITDA margin versus 4Q25 (28.3%) at the 5 Nov print?
### Resolution Criteria
Multiple choice. Options. (a) down y/y ("lower", "down", "decline"); (b) approximately flat / "similar"; (c) up y/y; (d) no quarterly margin sentence.
### Fine Print
Any numeric 4Q26 margin guide maps to the option its midpoint implies vs 28.3%. Resolution date 5 Nov 2026.

Conventions adopted (stated, not changing the question): a two-sided qualitative sentence resolves on its qualitative midpoint by analogy with the numeric rule — "flat to down slightly" / "in line to slightly lower" → (a); "flat to up" / "in line to modestly higher" (the 3Q22 form) → (c); "approximately flat", "similar", "in line", "relatively flat", "roughly consistent with" → (b). A sentence on adjusted EBITDA dollars only ("Adjusted EBITDA to increase year-over-year") with no margin clause → (d). A sentence with "down slightly" → (a) (the 3Q26 form). Letter governs; the call counts only if the letter is silent. 4Q25 base 28.29% (letter-rounded 28.3%).

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | Every November letter has carried a next-quarter (Q4) margin sentence, 5 of 5: 3Q21 "greater year-over-year ... margin expansion in Q4 2021 than ... Q3 2021" (up; realised +12.2pts); 3Q22 "in-line to modestly higher than last year's margin of 22%" (flat-to-up; realised +4.6); 3Q23 "an Adjusted EBITDA margin that exceeds Q4 2022" (up; +6.7); 3Q24 "expected to decline relative to the same time period last year due to higher marketing and product development expenses" (down; −2.5); 3Q25 "Adjusted EBITDA in Q4 2025 to be flat- to-down slightly ... and for Adjusted EBITDA Margin to decline ... primarily driven by investments in new growth and policy initiatives" (down; −2.5). Every quarter since 2Q21 has carried a next-quarter margin sentence (21 of 21) | data/processed/overnight/02_guidance_ledger.csv; data/raw/letters/3Q21–3Q25_*.htm; datasets/quarterly_margin_sentence_ledger.csv | 2026-09-07 | 2026-09-17 | yes |
| 2 | Direction families of all 21 next-quarter margin sentences 2Q21–2Q26 (my classification, CSV): down 9, flat-to-down 3, approx-flat 1, flat-to-up 1, up 7. Since 2Q24 (n 10): down 6, flat-to-down 2, approx-flat 1, up 1. The three 2026 sentences: 1Q26 "approximately flat year-over-year" (realised +1.0), 2Q26 "up year-over-year" (realised +1.3), 3Q26 "down slightly ... due to timing of investments" (pending) | datasets/quarterly_margin_sentence_ledger.csv (from 02_guidance_ledger.csv) | 2026-09-17 | 2026-09-17 | yes |
| 3 | The directional quarterly margin guide held 13 of 14 times since 1Q23 (the miss, 2Q25 "flat to down slightly", was to the upside, +1.2); the sentence has not been sandbagged: realised minus sentence level W2 mean −0.19pp, median −0.94, above in 4 of 10. Management's stated direction therefore tracks its internal direction with a small conservative tilt, not a large one | research/notes/predictive/04_margin-and-reaction.md §1.6; docs/margin-build/SYNTHESIS.md §9 | 2026-09-14 | 2026-09-17 | yes |
| 4 | At each of the three Novembers with a numeric FY sentence, management's Q4 direction matched the sign of the Street's Q4 consensus versus the prior-year Q4: 2023 Street 29.52 vs 26.60 (+2.9) → "exceeds"; 2024 Street 29.93 vs 33.27 (−3.3) → "decline"; 2025 Street 27.99 vs 30.85 (−2.9) → "decline". The Street sat within 0.4pp of the FY-sentence-implied Q4 in 2023 and 2025 | docs/margin-build/notes/M3_guide_policy_margin.md (q4_implied backtest table); data/processed/margin_build/05_mgmt_statements_v2/05_guide_language_pattern.csv | 2026-09-14 | 2026-09-17 | yes |
| 5 | LSEG 4Q26 consensus (11 Sep 2026, n 36): adj EBITDA margin 28.90% / $913.7M, EBITDA sd $26.5M (≈0.83pp of margin) on revenue $3,158M; 4Q25 actual 28.29%. The Street-implied direction is +0.6pp, inside the "flat" band | data/processed/margin_build/23_final_model/23_vs_consensus.csv; 23_card_5nov.csv | 2026-09-14 | 2026-09-17 | yes |
| 6 | Team 4Q26 margin views: the run quotes the Street 28.90% (combination 29.04%, M3 sentence path 29.90%, range 28.9–29.9); the line build 28.3% / $899M (Q3 marketing step treated as Q3-specific timing because carrying it into Q4 would breach the 35.5% floor at guide revenue); short case 23.6% at budget or 29.6% after a $177M Q4 marketing cut. WS31b's 24.7–25.9% is not carried (contradicted by every method and the Street) | docs/margin-build/SYNTHESIS.md §3, §5; docs/margin-build/notes/40_line_build.md | 2026-09-15 | 2026-09-17 | yes |
| 7 | Budget identity (WS23): at 3Q26 = 49.94%, an FY26 sentence of 36.0 implies 4Q26 = 30.1% (+1.8 y/y), 35.75 → 29.0% (+0.7), 35.5 held → 4Q26 ≥ 27.9% (a lower bound only). 1pp of the FY sentence = 4.49pp of 4Q26. So the FY sentence (C04) and the Q4 direction sentence are one decision: "approximately 36%" all but forces "up"; a held floor is compatible with flat or down | data/processed/margin_build/23_final_model/23_card_budget_identity.csv; docs/margin-build/MORNING_REPORT.md §f | 2026-09-14 | 2026-09-17 | yes |
| 8 | 2Q26 letter/call: Q3 margin "down slightly compared to Q3 2025, due to timing of investments this year"; FY26 "at least 35.5%". Line-build reading: management's two statements are jointly consistent only if most of the Q3 cost step is Q3-specific, i.e. Q4 does not carry it → Q4 margin ≥ ~28.6% at guide revenue (flat to up y/y) | data/raw/letters/2Q26_d70413dex991.htm; data/raw/transcripts/web/2Q26.html; docs/margin-build/notes/40_line_build.md | 2026-08-06 | 2026-09-17 | yes |
| 9 | Precedent for "down" on a rising base: 3Q24's Q4 "decline ... due to higher marketing and product development expenses" was given while the FY sentence was raised to 35.5% (Q4 base 33.27 was high). Chesky, 8 Sep 2026: "We're going to have some major announcements next year" (V023) — launch marketing ahead of 2027 products is the mechanism for a repeat of the 2024 form. Mertz 6 Aug 2026: "material increase in terms of the AI spend over the course of the year" (ramps through 2H26) | data/raw/letters/3Q24_d886752dex991.htm; data/processed/margin_build/05_mgmt_statements_v2/05_statements.csv V023, S162 | 2026-09-08 | 2026-09-17 | yes |
| 10 | WS05 prior for the Q4 sentence: "flat to down / decline year-over-year" 0.6, "expand" 0.4 ("the 4Q25 base is the low one at 28.3"); M3: "decline / flat to down year-over-year" p ~0.6 ("3Q24 and 3Q25 both used it and were right") | docs/margin-build/notes/05_mgmt_statements_v2.md; notes/M3_guide_policy_margin.md | 2026-09-14 | 2026-09-17 | yes |
| 11 | 4Q25 was the lowest Q4 margin since 4Q22 (26.6): Q4 actuals 4Q22 26.60, 4Q23 33.27, 4Q24 30.85, 4Q25 28.29 (2022–25 mean 29.75, sd 2.92). The 4Q25 print carried the RNPL/cancellation-policy launch spend and the US shutdown quarter | docs/margin-build/SYNTHESIS.md §4; data/processed/h2_bridge_v3/h2_bridge_deviations.csv | 2026-09-14 | 2026-09-17 | no |
| 12 | C01 agent's provisional Monte Carlo: P(4Q26 revenue guide midpoint below the Street) 0.80; guide midpoint mean $3,089M, sd $80M (p10 2,985, p90 3,190). Operating leverage on a fixed cost base: 2H26 margin moves 0.59pp per 1pt of revenue with costs held, 0.38pp flexed | docs/pitch-forecasts/questions/q4-revenue-guide-vs-street/datasets/c01_mc_summary.csv; data/processed/margin_build/23_final_model/23_macro_sensitivity.csv | 2026-09-17 | 2026-09-17 | yes |
| 13 | Shared Monte Carlo (400,000 draws, seed 20260917): management's internal 4Q26 margin = 29.3 + 0.5pp per 1% of internal Q4 revenue vs $3,190M + N(0, 1.4), internal Q4 revenue = C01 guide × (1 + N(0.025, 0.010)). Result: internal 4Q26 margin mean 28.94, sd 1.96; P(> 28.29) 0.63; P(> 28.9) 0.51; P(< 27.7) 0.26. Stated direction = internal − N(0.3, 0.4) conservative tilt vs 28.29, with a "flat" band of ±N(0.6, 0.2); (d) 5% exogenous. Raw vector a 0.303, b 0.219, c 0.428, d 0.050. Conditional on the guide midpoint below the Street: a 0.37, b 0.24, c 0.34; not below: a 0.05, b 0.12, c 0.79. Conditional on C04 = (b): a 0.08, b 0.18, c 0.69; on C04 ∈ {a, d}: a 0.47, b 0.26, c 0.22 | datasets/mc_sentence_model.py, mc_sentence_results.json, mc_joint_and_conditionals.json, mc_run_log.txt | 2026-09-17 | 2026-09-17 | yes |
| 14 | No Polymarket or Kalshi market exists on the Q4 margin sentence or 4Q26 margin. Adjacent: Kalshi KXABNB-26NOVNEB 3Q26 nights >148m bid 0.50 / ask 0.55 (last 0.53), >146m 0.63/0.66, >150m 0.32/0.36 (fetched 2026-09-17T02:53:46Z; volume null) — a Q3 revenue beat raises the internal FY margin but says nothing about Q4 spend timing | sources/kalshi_KXABNB_markets.json; sources/polymarket_search_airbnb.json | 2026-09-17 | 2026-09-17 | no |
| 15 | Investing.com projects the next release on "Nov 04, 2026" (EPS 2.86, revenue $4.74B); the company has not announced. The Yahoo/Zacks Q3 preview found in search is dated 2025-11-03 (stale, zero weight) | https://www.investing.com/equities/airbnb-inc-earnings; https://finance.yahoo.com/news/airbnb-set-report-q3-earnings-181600069.html | 2026-09-17 | 2026-09-17 | no |
| 16 | Final 72-hour recency check (WebSearch "Airbnb ABNB this week", 2026-09-17): stock $167.51, −7.4% w/w; $250M Housing Accelerator; Morgan Stanley Equal Weight, Truist/BofA Hold. Nothing on Q4 spend, the print or guidance | sources/web_search_log.md | 2026-09-17 | 2026-09-17 | no |
| 17 | Reaction relevance (for X01, not for this number): "margin guide met" correlates +0.35 with the day-1 excess return (n 20, p 0.14); margin met with nights decelerating averaged −2.1% (2 of 11 positive) | research/notes/predictive/04_margin-and-reaction.md §3–4 | 2026-09-06 | 2026-09-17 | no |

## 2. Query Log
1. [repo] docs/pitch-forecasts/00_BRIEF.md, QUESTIONS.md (C09 block and conventions), examples/example-research-log.md; skill SKILL.md, references/research-log-format.md
2. [repo] docs/margin-build/MORNING_REPORT.md §f; SYNTHESIS.md §3–5, §9; notes/M3_guide_policy_margin.md (q4_implied backtest, sentence forecast table); notes/05_mgmt_statements_v2.md (guide-language pattern, 5 Nov scenarios); notes/40_line_build.md (Q4 treatment of the Q3 step; short case); notes/M6_cycle_flex.md (k's, asymmetry, cut caps)
3. [repo] grep "margin" data/processed/overnight/02_guidance_ledger.csv → classified into datasets/quarterly_margin_sentence_ledger.csv (direction families, November flag); abnb_guidance_reaction_panel.csv nq_margin_dir column
4. [repo] regex extraction of forward-looking "EBITDA Margin" sentences from data/raw/letters/3Q23, 3Q24, 3Q25, 2Q26 letters; 2Q26 transcript around "timing of investments" and the Sheridan incremental-margin question
5. [repo] 05_statements.csv rows dated ≥ 2026-02-01 on margin / investment / Q4 / 2027 (S137–S193, V017–V026); 05_nov2026_scenarios.csv (implied 4Q26 y/y by sentence and Q3 assumption)
6. [repo] data/processed/margin_build/23_final_model/23_card_budget_identity.csv, 23_vs_consensus.csv, 23_macro_sensitivity.csv; h2_bridge_v3 revenue and deviations files; research/notes/predictive/04_margin-and-reaction.md
7. [Polymarket API] public-search?q=Airbnb; ?q=ABNB earnings (2026-09-17T02:52:53Z) — no relevant market
8. [Kalshi API] events?status=open, 15 pages / 3,000 events grep airbnb|abnb; markets?series_ticker=KXABNB, KXABNBA (2026-09-17T02:53:46Z)
9. Airbnb news (WebSearch, neutral pass, shared with C04) — nothing on Q4 or margin
10. Airbnb third quarter 2026 results date November (WebSearch, shared) — vendor projection only
11. [fetch] finance.yahoo.com Q3 preview — 2025 article, stale, discarded; [fetch] investing.com earnings page — Nov 04, 2026 projected
12. Airbnb 2026 adjusted EBITDA margin guidance analysts expect raise (WebSearch, shared) — company language only
13. [repo] q4-revenue-guide-vs-street/datasets/c01_mc_summary.csv, c01_percentiles.csv (C01 provisional)
14. [computed] datasets/mc_sentence_model.py → C09 vector and the C04 × C09 joint; mc_joint_and_conditionals.json
15. Airbnb ABNB this week (WebSearch, final 72-hour recency check, shared) — nothing new

## 3. Leading Hypothesis Entities
Airbnb, 4Q26 adjusted EBITDA margin, Ellie Mertz, 3Q26 shareholder letter, "approximately 36%", timing of investments, LSEG consensus

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| "Up year-over-year" because the budget identity plus "approximately 36%" requires 4Q26 ≈ 30% (+1.8), and the Q3 cost step was described as timing | leading (c 0.40) | claims 7, 8, 13: P(c | C04 = b) 0.69; the 2Q26 statements are only jointly consistent if Q4 does not carry the Q3 step; 4Q25 is a low base (claim 11) |
| "Decline" because 2027 launch marketing and the AI hosting ramp land in Q4 (the 3Q24 form) | kept (a 0.28) | claims 9, 2: 8 of the last 10 quarterly sentences were in the down family, and both prior November Q4 sentences were "decline"; but both were given on high Q4 bases (33.3, 30.9) with the Street already implying a decline (claim 4) |
| "Approximately flat" because the Street's own 4Q26 (+0.6pp) is in the flat band and management's Q4 direction has matched the Street's sign 3 of 3 | kept (b 0.27) | claims 4, 5; the 1Q26 "approximately flat" precedent shows the wording exists in the 2026 lexicon; it is the natural rendering of an internal +0.5 to +1.0 |
| No Q4 margin sentence (dollars only, or nothing) | tail (d 0.05) | 21 of 21 quarterly letters since 2Q21 gave one; 5 of 5 Novembers; the boilerplate itself references "expected Adjusted EBITDA Margins" |
| A numeric 4Q26 margin guide | inside a/b/c by midpoint | never given (all quarterly margin sentences have been directional); ~0.03 |
| Inverse coupling with the Q3 print: a high Q3 (spend did not land) shifts the step into Q4 → "down" | kept as a sensitivity, not a branch | plausible mechanism; the shared MC does not model it explicitly; the 3Q26 evidence-only 52.4% case would raise (a) by ~5 pts |
| WS31b forward profile (4Q26 24.7–25.9%) implying "down" | discarded | retired by the margin build; contradicts every method and the Street (claim 6) |

## 5. Independent Estimates
- base_rate_estimate: (a) 0.30, (b) 0.30, (c) 0.35, (d) 0.05 — raw reference class of all 21 next-quarter margin sentences: down family 12/21 (0.57), flat 1/21, up family 8/21 (0.38); since 2Q24 8/10 down; Novembers 3 up-family / 2 down. Regime-conditioned on the Street's implied Q4 direction (+0.6pp, inside the flat band; management's stated sign matched the Street's 3 of 3, claim 4) and on the 2026 sentences (flat, up, down slightly), which moves the 2024–25 "decline" streak down and the flat family up
- decomposition_estimate: (a) 0.30, (b) 0.22, (c) 0.43, (d) 0.05 — shared Monte Carlo (claim 13): internal 4Q26 margin 28.9 ± 2.0 with P(> LY) 0.63, stated with a 0.3pp conservative tilt and a ±0.6 flat band; the (c) mass is carried by the C04 = "approximately 36%" branch (P(c | b) 0.69)
- anchor_estimate: (a) 0.50, (b) 0.10, (c) 0.35, (d) 0.05 — no external market; anchor is the repo prior (WS05 0.6 "flat to down / decline", 0.4 "expand"; M3 ~0.6 decline family), dated 2026-09-14, mapped to the options with "flat to down" → (a) and (d) taken from the un-priced remainder
- anchor_value: P(a) = 0.50 (repo prior, decline family; 2026-09-14)
- final_estimate: (a) 0.28, (b) 0.27, (c) 0.40, (d) 0.05
- final_minus_anchor: −22 points on (a), the anchor's leading option; +5 points on (c), the final's leading option. Independently derived: the anchor was set from the last two Novembers' wording alone; this forecast conditions on the budget identity (an FY raise forces a Q4 "up"), the Street's +0.6pp implied direction, the low 4Q25 base and the C01 guide distribution. The base rate and decomposition agree on (a) (0.30) and disagree on b/c by 8–13 points — the disagreement is about how management renders an internal +0.5 to +1.0 ("approximately flat" vs "up"), which the 1Q26 vs 2Q26 precedents split evenly; the final splits it.

## 6. Final Numbers
| Option | Probability |
|---|---|
| (a) down y/y ("lower", "down", "decline", "flat to down slightly") | 0.28 |
| (b) approximately flat / "similar" / "in line" | 0.27 |
| (c) up y/y (incl. "flat to up", "modestly higher", "expand") | 0.40 |
| (d) no quarterly margin sentence | 0.05 |
Sum 1.00. Coherence with C04 (final vectors, joint from the shared MC): P(c) ≈ 0.42 × 0.69 + 0.50 × 0.22 + 0.05 × 0.90 + 0.03 × 0.43 ≈ 0.46 before the wording haircut; the final 0.40 reflects the even 1Q26/2Q26 precedent on rendering a small internal gain as "flat" rather than "up". Conditional on the C01 guide midpoint being below the Street: a 0.35, b 0.28, c 0.32, d 0.05; not below: a 0.08, b 0.15, c 0.72, d 0.05.
Extreme-probability gate: no option ≤ 2%; (d) at 0.05 audited — edge cases priced: dollars-only sentence (the 3Q25 form gave both; a dollars-only form has appeared once, 3Q23's Q3 wording, and even then a margin clause followed), letter silent but call gives direction (call counts only if the letter is silent — inside a/b/c).

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| C04 = "approximately 36%" at 0.42 | if C04 (b) were 0.55 (repo prior): c 0.48, a 0.23, b 0.24; if 0.30: c 0.33, a 0.33, b 0.29 |
| Internal 4Q26 margin centre ≈ 28.9–29.3 (Street with leverage) | line-build 28.3 (Q3 step does not recur but Q4 flat): c 0.30, b 0.32, a 0.33; M3 path 29.9–30.1: c 0.55, b 0.22, a 0.18 |
| 4Q26 guide midpoint ≈ $3,090M (C01), below Street with P 0.80 | at the Street ($3,160M): c 0.55, a 0.15, b 0.25; at C01 p10 ($2,985M): c 0.28, a 0.40, b 0.27 |
| Rendering of an internal +0.5 to +1.0 splits evenly between "approximately flat" and "up" | always "up" (2Q26 form): c 0.50, b 0.17; always "flat" (1Q26 form): c 0.31, b 0.36 |
| 2027 launch marketing / AI hosting ramp does not step up in Q4 | it does (3Q24 form, "decline due to higher marketing and product development"): a 0.45, c 0.25, b 0.25 |
| Q3 prints near the ceiling (~50%) | Q3 prints 52%+ (spend slipped into Q4): a +0.05, c −0.05 |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-30 | Quarter end; Kalshi Q3-nights ladder (adjacent) | no direct move; a strong Q3 revenue read raises C04 (b) and hence (c) here by ≤ +2 |
| ~2026-10-15 | Airbnb fixes the 3Q26 print date | confirm resolution date |
| 2026-10-20 to 10-30 | LSEG 4Q26 margin consensus refresh; BKNG/EXPE Q3 prints and Q4 marketing commentary | LSEG 4Q26 ≥ 29.5%: c +5, a −3; ≤ 28.3%: a +5, c −4. Peer commentary on stepped-up Q4 brand spend or 2027 launch marketing: a +3 |
| 2026-10-28 to 11-03 | Any Airbnb product announcement scheduled for Q4/1Q27 (launch marketing precedes launches) | a +3 per named Q4 launch with a marketing campaign |
| 2026-11-04/05 | 3Q26 letter (resolution) | read the FY sentence (C04) first: "approximately 36%" → expect (c); floor held → read the Q4 sentence for the short case (a signals the marketing cut did not happen or spend slipped). Record wording verbatim for X01 |
| any date before the print | Pre-announcement or 8-K on Q3 (never done) | Q3 margin ≥ 51% disclosed: a +5 (spend slipped to Q4) |
