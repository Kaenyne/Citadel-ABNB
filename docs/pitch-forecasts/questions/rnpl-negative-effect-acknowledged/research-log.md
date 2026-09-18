# RESEARCH LOG

## 0. Metadata
- question_name: rnpl-negative-effect-acknowledged
- question_url: n/a (internal pitch-forecast question C07, `docs/pitch-forecasts/QUESTIONS.md`)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-16
- close_date: 2026-11-05
- resolution_date: 2026-11-05
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 2
- revised: 2026-09-17
- agent: fable
- batch: A04 (shared research with C05 and C06; the full query log is repeated here)
- audit: `docs/pitch-forecasts/audits/A04-research-audit.md` (Astra); response `docs/pitch-forecasts/audits/A04-audit-response.md`

## 0b. Question (verbatim)
### Title
Will Airbnb management, in the 3Q26 letter, 10-Q or call, state that RNPL reduced or will reduce a reported metric (nights, GBV, revenue, take rate, unearned fees, FCF or cash) in 3Q26 or 4Q26, beyond the boilerplate "higher cancellation rates" and "timing" language already in the 2Q26 10-Q?
### Resolution Criteria
**Type.** Binary.
**Resolution.** Yes if any of: a quantified negative effect (points, dollars, or "meaningful"/"notable" drag) on any reported metric; an explicit statement that cancellations from RNPL cohorts exceeded expectations or the tested curve; a statement that the net benefit has declined or turned; or a change to RNPL terms motivated by cancellations. No if statements are limited to net-positive reiteration, unchanged boilerplate, or timing effects described as neutral.
### Fine Print
The 2Q26 10-Q sentences ("higher cancellation rates than historic bookings"; GBV/revenue/cash timing "may become less correlated"; FCF seasonality) are the boilerplate baseline; repeating them verbatim is No. Resolution date 5 Nov 2026 (10-Q filing date if later).

Conventions adopted (revision 2: a literal classification table, `datasets/c07_classification_table_v2.csv`, replaces rev-1's narrower reading; each row is priced in section 5):
1. The recurring letter sentences "absent RNPL, unearned fees [and FCF] would have grown year-over-year" (D037, D051), the take-rate "timing of when guests booked ... reflects the growth of RNPL" sentence (D049) and the FY26 take-rate sentence (D050) are direction-only timing effects already on the record before the 2Q26 10-Q and resolve No when repeated in substance; they are not promoted to Yes automatically. A **new** dollar or point quantification of such a timing effect ("RNPL reduced unearned fees by roughly $X") resolves Yes under the "quantified negative effect" clause.
2. A qualitative lap or comparison statement ("tougher comparisons against the RNPL rollout", "we lapped RNPL in the US") describes the prior-year base and resolves No. **A quantified lap effect on a listed 3Q26 or 4Q26 metric ("the RNPL comparison reduced Q3 nights growth by about 2 points") resolves Yes** under the "quantified negative effect on any reported metric" clause (revision 2; rev-1 treated this as resolver risk only). C05 counts the same sentence as a 3Q26 quantification under its convention 2, so the two logs now agree on the object.
3. **A statement that RNPL's net benefit or lift has declined or moderated resolves Yes even if the benefit is still described as positive** ("the incremental lift from RNPL is smaller now that we have lapped the US launch"), under the "net benefit has declined" clause (revision 2). A bare lap sentence with no decline in benefit stated stays No under convention 2.
4. A cancellation-rate figure alone ("17% to 18%") is not a listed reported metric; it resolves Yes only if tied to a listed metric or to expectations ("higher than we tested").
5. The 3Q26 10-Q counts in full; Airbnb has filed each 10-Q on the print day (2Q26: 6 Aug; 1Q26: 7 May), so the expected resolution date is 5 Nov.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | The 2Q26 10-Q MD&A sentence "To date, RNPL bookings, which require no payment at the time of booking, have experienced higher cancellation rates than historic bookings in which some or all of the cash was received at the time of booking. As adoption of RNPL and our other flexible payment options continues to grow, the timing among GBV, revenue, and cash receipts may become less correlated." is verbatim in the filing; also "The increase in ADR was driven in part by the continued adoption of RNPL" and the FCF timing sentences | data/raw/regulatory/quantification/abnb_2026q2_10q.html; sources/10q_2Q26_rnpl_passages.txt | 2026-08-06 | 2026-09-17 | yes |
| 2 | 10-Q language evolution: the 3Q25 10-Q does not name RNPL and has no cancellation or timing sentence; the FY25 10-K names RNPL only in the business description and the FX-exposure list ("unbilled amounts for confirmed bookings under the terms of our payment programs"); the 1Q26 10-Q refers only to "deferred payment programs" with timing language ("shifts the timing of when net cash provided by operating activities is recognized"); the 2Q26 10-Q is the first filing to name RNPL and the first to state higher cancellation rates. One escalation step in four filings; there are no completed post-2Q26 trials of escalation beyond that baseline | datasets/10q_rnpl_language_evolution.csv; https://www.sec.gov/Archives/edgar/data/1559720/000155972025000030/abnb-20250930.htm ; https://www.sec.gov/Archives/edgar/data/1559720/000155972026000014/abnb-20260331.htm ; data/raw/regulatory/quantification/abnb_2025_10k.json | 2026-08-06 | 2026-09-17 | yes |
| 3 | Prior prints scored under the question's criteria: strict reading 0 of 4 Yes; generous reading 3 of 4 (4Q25 "16% to 17%"; 1Q26 "FCF declined slightly ... primarily due to the working capital impact from the continued expansion of RNPL"; 2Q26 take-rate timing). Under the revision-2 classification table the 1Q26 FCF sentence is borderline (a direction-only timing effect on a listed metric, "slightly"): literal-table count 0–1 of 4. These four prints are descriptive analogues, not trials of escalation beyond a baseline that was itself set at the last of them (the 2Q26 10-Q); the base rate below is labelled accordingly | datasets/prior_prints_scored_under_c07_criteria.csv; datasets/c07_classification_table_v2.csv | 2026-09-17 | 2026-09-17 | yes |
| 4 | Management's standing position, five times on the record: cohorts tested to be "net beneficial ... by the time the cohorts ... had reached their check-in date" (D019); "the cancellation curves have been very close to what we saw from a tested perspective" (D020); "we are already absorbing the elevated level of cancellations" (D021); "a meaningful lift to all booking metrics, net of cancellation" (D033); "Across all regions ... the net impact is positive" (D035) | data/processed/overnight2/D/rnpl_statement_ledger.csv; data/raw/transcripts/web/4Q25.html, 1Q26.html | 2026-05-07 | 2026-09-17 | yes |
| 5 | The only cancellation shock Airbnb has ever sized in growth points was exogenous (Middle East, "approximately 10%" ex-conflict vs "over 9%" reported, 1Q26 letter, D042); it has never quantified a drag from its own product and declined the one direct sizing ask (D007). Its lap vocabulary so far is qualitative: "tougher comparisons in the back half of this year against the rollout of Reserve Now, Pay Later in 2025" (1Q26 letter, D040) and "tougher comps in the back half of the year" (2Q26 call, RNPL not named) | data/raw/letters/1Q26_d23351dex991.htm; data/raw/transcripts/web/2Q26.html; data/processed/abnb_declined_to_quantify.csv row 2025Q3 | 2026-08-06 | 2026-09-17 | yes |
| 6 | Team cohort engine: the y/y-differenced cancellation drag on 3Q26 nights is −0.15 to −0.93 points in the central column (propensity +1 to +6), −1.37 to −0.10 across the full 2,025-cell grid, and the unified module's bear/base/bull propensity effects are −1.425 / −0.568 / −0.158; the level lap is 2–15× larger; the 34-market calendar test found no RNPL cancellation signature (pre-registered null). The central range is a labelled scenario slice, not an empirical bound; the team's own evidence does not expect a cancellation quarter bad enough to force an admission, and the failure to detect a signature is not proof of no effect | research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md §2.3, §4; data/processed/rnpl_short_audit/rnpl_nights_module.csv; docs/rnpl-short-audit/00_SYNTHESIS.md points 1–3; research/notes/overnight2/A_calendar-reopening-34-markets.md (via 03_short-thesis-viability.md rank 6) | 2026-09-11 | 2026-09-17 | yes |
| 7 | The one asymmetry that could make 3Q26 the quarter the net turns: gross uplift scales with the flow of new RNPL bookings (flattening as the share approaches its ceiling) while cancellations scale with the stock reaching payment deadlines (still growing; 45.7% of 3Q26 excess cancellations come from earlier cohorts in the central cell) | research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md §4 last paragraph, §2.4; data/processed/overnight2/D/D1_cohort_matrix_cancellation.csv | 2026-09-11 | 2026-09-17 | yes |
| 8 | Management's own forward-testable 3Q26 prediction: RNPL "results in lower unearned fees in Q1 and Q2 and higher unearned fees in Q3" (D038); the cash-timing channel flips positive for RNPL in Q3, so the letter's unearned-fee/FCF sentences are more likely to be framed as RNPL adding to Q3 cash than reducing it. This lowers the cash/unearned-fee route in 3Q26 but says nothing about Q4 effects, nights, GBV or take rate | data/raw/letters/1Q26_d23351dex991.htm; data/processed/overnight2/D/D1_prereg_thresholds.csv row 3 | 2026-05-07 | 2026-09-17 | yes |
| 9 | The July 2026 change to RNPL was an expansion of eligible booking types (D044), the opposite direction of a cancellation-motivated tightening; no terms change was found in the newsroom page fetched, the help-centre page fetched or the searches recorded between 6 Aug and 17 Sep (no snapshots saved) | data/raw/transcripts/web/2Q26.html; https://news.airbnb.com/reserve-now-pay-later/ ; queries 18, 29 | 2026-09-17 | 2026-09-17 | yes |
| 10 | Host-side friction is documented ("phantom bookings"; hosts cannot opt out; staystra 29 Apr 2026) and is the mechanism by which a terms change could arrive; nothing in the pages fetched indicates one is planned | https://staystra.com/airbnb-reserve-now-pay-later-hosts-cancellation-policy-2026/ | 2026-04-29 | 2026-09-17 | no |
| 11 | Print-state weights (revision 2): the run's R01/R02 forecasts, P(nights ≥10.0%) 0.42 and P(≥10.6%) 0.32 (implied N(9.67, 1.70): P(<9.0%) 0.347), so P(decelerating vs 2Q26's 10.34%) ≈ 0.64 by interpolation; team band alone N(9.5, 1.48) gives P(<9) 0.368 and P(<10.34) 0.71. A print below the "low double-digit" guide floor raises the pressure to explain and the probability that the lap or cancellations are named as a cause | docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/forecasts/2026-09-17-forecast.json; risk-q3-nights-accelerates/forecasts/2026-09-17-forecast.json; docs/pitch-forecasts/00_BRIEF.md rule 6; docs/q3nowcast/SYNTHESIS.md | 2026-09-17 | 2026-09-17 | yes |
| 12 | Kalshi Q3 nights ladder (2026-09-17T02:53:51Z): P(>146m, +9.3%) 0.645; P(>144m, +7.8%) 0.795; `volume_fp` 3,237 contracts, `open_interest_fp` 2,178, `volume_24h_fp` 0, `updated_time` 2026-08-04 batch stamp. Reported as a sensitivity, not used in the headline (revision 2) | sources/kalshi_KXABNB-26NOVNEB_20260917T025351Z.json; datasets/kalshi_q3_nights_implied_v2_2026-09-17.csv | 2026-09-17 | 2026-09-17 | no |
| 13 | No market on any Airbnb management statement was found in the searches recorded (Polymarket public-search; Kalshi 4,000 open events scanned; the second Kalshi file is an FY2026 annual nights ladder) | sources/polymarket_public-search_airbnb_20260917T025229Z.json; sources/kalshi_KXABNBA-27FEBNEB_20260917T025351Z.json | 2026-09-17 | 2026-09-17 | yes |
| 14 | Analyst RNPL/cancellation questions on the call: 1, 1, 2, 0 (3Q25–2Q26); a question is the main route to an unscripted admission and the frequency is falling | data/raw/transcripts/web/*.html (query 12) | 2026-08-06 | 2026-09-17 | no |
| 15 | Management credibility scorecard: unscripted Q&A claims realised 52%, quantified claims 82%; "declined to quantify" 37 instances in 23 calls, four in 2Q26 | research/notes/overnight/03_management-language-and-stock.md §4 | 2026-09-05 | 2026-09-17 | no |
| 16 | Chesky, Communacopia 8 Sep 2026 (transcript fetched): no mention of RNPL, cancellations or payment options | https://stockanalysis.com/stocks/abnb/transcripts/739626-goldman-sachs-communacopia-technology-conference-2026/ | 2026-09-08 | 2026-09-17 | no |
| 17 | Final 72-hour recency check (2026-09-17): no relevant result found in the searches recorded (queries 17, 29) for an RNPL terms change, host-policy announcement or management comment this week; no snapshots saved | WebSearch queries 17, 29 | 2026-09-17 | 2026-09-17 | no |
| 18 | (Revision 2) C05's scenario bridge: an RNPL-alone 3Q26 contribution is 1.3–1.7 points gross under the team's fitted allocation, so a management statement of the form "RNPL added about 1–1.5 points in Q3, down from about 3 in Q1" is arithmetically natural in a decelerating quarter and would count here under convention 3 (declined benefit) as well as under C05 (c) | docs/pitch-forecasts/questions/bundle-attribution-quantified/datasets/bundle_3q26_mechanical_contribution_v2.csv | 2026-09-17 | 2026-09-17 | yes |

## 2. Query Log
1. [repo] pandas dump of data/processed/overnight2/D/rnpl_statement_ledger.csv (60 rows)
2. [repo] data/processed/overnight2/D/D1_prereg_thresholds.csv
3. [repo] regex extraction of RNPL/cancellation passages from the 3Q25–2Q26 letters and call mirrors, saved to sources/letters_calls_3Q25-2Q26_rnpl_passages.txt
4. [repo] same for data/raw/regulatory/quantification/abnb_2026q2_10q.html, saved to sources/10q_2Q26_rnpl_passages.txt
5. [repo] quantified-driver regex scan of all 23 letters and calls
6. [repo] metric-persistence matrix (16 metrics × 23 prints), saved to datasets/metric_persistence_matrix_4Q20-2Q26.csv
7. [repo] RNPL passages in abnb_2025_10k.json
8. [repo] data/processed/abnb_declined_to_quantify.csv
9. [SEC API] data.sec.gov/submissions/CIK0001559720.json
10. [Polymarket API] public-search?q=airbnb ; ?q=ABNB%20earnings (2026-09-17T02:52:29Z)
11. [Kalshi API] events?status=open (20 pages), then markets?event_ticker=KXABNB-26NOVNEB, KXABNBA-27FEBNEB (02:53:51Z)
12. [repo] analyst-question scan of 3Q25–2Q26 call Q&A for RNPL/cancellation asks
13. [repo] 2Q26 Middle East / World Cup passages
14. [SEC fetch] 3Q25 10-Q (abnb-20250930.htm) and 1Q26 10-Q (abnb-20260331.htm), raw grep for RNPL, "Pay Later", "cancellation rate", "less correlated", "deferred payment programs", saved to datasets/10q_rnpl_language_evolution.csv
15. [repo] research/notes/overnight/03_management-language-and-stock.md dropped-claims and credibility sections
16. [repo] 02_guidance_ledger.csv scan for RNPL rows (none)
17. WebSearch: Airbnb news
18. WebSearch: Airbnb Reserve Now Pay Later September 2026
19. WebSearch: Airbnb Reserve Now Pay Later cancellations analyst Q3 2026
20. WebSearch: Airbnb third quarter 2026 results date November
21. WebFetch: news.airbnb.com/reserve-now-pay-later/
22. WebFetch: staystra.com RNPL hosts 2026 page (2026-04-29)
23. WebFetch: rentalscaleup.com insurance-pay-later page (2026-07-03)
24. WebFetch: finance.yahoo.com Q3 preview (2025 vintage: stale, zero weight)
25. [repo] grep q3nowcast notes and G/intra_quarter_commentary.csv for conference RNPL mentions
26. WebSearch: Airbnb Mertz conference September 2026 "Reserve Now, Pay Later"
27. [repo] grep 1Q26/2Q26 letter and call for "extended cancellation" (none)
28. WebFetch: stockanalysis.com Communacopia 8 Sep 2026 transcript (no RNPL mention)
29. WebSearch: Airbnb "Reserve Now, Pay Later" news this week (final 72-hour check; nothing new)
30. [computed] datasets/prior_prints_scored_under_c07_criteria.csv
31. (rev 2) [repo] grep of the 1Q26 and 2Q26 letters and the 2Q26 call for "lap|comparison|comps|tougher|net benefit|net lift|net impact" (how management has worded the lap so far: qualitative only, claim 5)
32. (rev 2) [repo] research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md §2.3 full-grid range (−1.37 to −0.10) and data/processed/rnpl_short_audit/rnpl_nights_module.csv 3Q26 rows (claim 6)
33. (rev 2) [computed] docs/pitch-forecasts/audits/A04-response-datasets.py → datasets/c07_classification_table_v2.csv, c07_scenario_partition_v2.csv, kalshi_q3_nights_implied_v2_2026-09-17.csv
34. (rev 2) [repo] R01/R02 forecast JSONs and §5–6 of their logs (claim 11)

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Reserve Now Pay Later, RNPL, cancellations, 3Q26 Form 10-Q, 5 November 2026

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| A bad cancellation quarter forces an admission ("cancellations ran above our tested curves") | kept as scenario S1 (P 0.15; P(Yes given S1) 0.65) | Team engine puts the y/y drag at −0.15 to −0.93 in the central column, −1.37 at the worst cell, and the calendar test is null (claim 6); the stock-vs-flow asymmetry (claim 7) is why S1 is not negligible |
| Ordinary performance, decelerating print, and management explains the deceleration with a sentence that qualifies (quantified lap; "lift has moderated"; a new dollar timing figure) | kept as scenario S2 (P 0.49; P(Yes given S2) 0.27) — **new in revision 2** | The registry's "quantified negative effect" and "net benefit has declined" clauses need no cancellation surprise (audit A04-01); management's lap vocabulary is so far qualitative (claim 5) but the arithmetic of a smaller RNPL contribution is natural (claim 18) |
| 10-Q MD&A escalates again (a new sentence tying higher cancellations to Nights and Seats Booked or GBV) | kept inside all three scenarios | One escalation step in four filings (claim 2); an added clause is plausible even in a normal quarter (about 0.05 in S2/S3) |
| The letter's unearned-fees/FCF sentence is read by the resolver as "RNPL reduced a reported metric" | priced as resolver risk (about 0.03 in S2/S3) | Convention 1 says No; in Q3 the RNPL cash effect is predicted positive by management (claim 8), which makes a negative cash sentence less likely anyway; Q4 and other metrics remain open |
| A terms change (deposit, shorter deferral, host opt-out) motivated by cancellations | kept, small (about 0.02 outside S1, 0.10 inside) | July went the other way (claim 9); host friction exists (claim 10) but there is no signal of a tightening |
| Management reverses its "net positive" language voluntarily | discarded as a standalone route | Five consistent statements (claim 4); reversal only under S1; a *moderation* of the benefit (not a reversal) is the S2 route |
| Nothing new: net-positive reiteration plus unchanged boilerplate | base case (about 0.73) | Strict-reading analogue 0/4 (claim 3); the FY26 guide-raise cadence and the "no single product" framing point to a routine RNPL paragraph |

## 5. Independent Estimates
- base_rate_estimate: 0.22. Literal-table reading of the four prints since launch: 0–1 of 4 (the 1Q26 FCF sentence is the borderline case), Laplace (0.5+1)/(4+2) = 0.25; the generous reading (3/4) is rejected by the fine print; discounted to 0.22 because the four analogues are not trials of escalation beyond a baseline set at the last of them (claim 3). Descriptive analogue, not a frequency of this event
- decomposition_estimate: 0.27 (`datasets/c07_scenario_partition_v2.csv`). Mutually exclusive scenarios on the R01/R02 print states (claim 11): S1 adverse RNPL performance 0.15 (P(<9%) 0.347 × share attributed to RNPL rather than lap/macro/World Cup 0.45) × P(Yes | S1) 0.65 [above-tested admission, 10-Q escalation, quantified drag, terms change] + S2 ordinary and decelerating (<10.34%), not S1: 0.64 − 0.15 = 0.49 × P(Yes | S2) 0.27 [quantified lap 0.12, net-benefit-declined/moderated wording 0.15, new $ timing quantification 0.04, 10-Q creep 0.05, terms change 0.02, resolver reads a repeated timing sentence as Yes 0.03; union about 0.30 before the lap/moderation overlap] + S3 routine or accelerating 0.36 × P(Yes | S3) 0.10 [10-Q creep 0.05, terms 0.02, resolver 0.03, moderation wording in a strong quarter 0.02] = 0.0975 + 0.132 + 0.036 = 0.266. On the team band alone (P(<9) 0.368, P(decel) 0.71): S1 0.165, S2 0.545, S3 0.29 → 0.283. The conditional probabilities are judgments, labelled as such
- anchor_estimate: none available. No market on any management statement (claim 13); the nearest adjacent price is Kalshi P(3Q26 nights ≤ 146m) about 0.355 (claim 12), reported as a sensitivity only
- anchor_value: n/a (NO_EXTERNAL_ANCHOR). The three-estimate requirement is unmet: two internal estimates, no external anchor
- final_estimate: 0.27 (credible interval 0.15–0.40)
- final_minus_anchor: n/a. The base rate and decomposition are within 5 points; they are partly independent (the base rate uses only the scored prints; the decomposition uses the engine, the print states and the 10-Q history). Audit A04's judgment (0.25; partition 15/25/60 with 70/40/7.5%) reproduces to 0.25; this log's partition differs by conditioning the middle scenario on a decelerating print (0.49 rather than 0.25 of the mass) with a lower conditional (0.27 vs 0.40), and by a higher routine-scenario conditional (0.10 vs 0.075) for the 10-Q creep route; the two agree within 2 points

## 6. Final Numbers
P(Yes) = 0.27; credible interval 0.15–0.40 (the span from the strict-reading analogue with the rev-1 conventions, about 0.17, to the team-band partition with P(Yes | S2) 0.35, about 0.33, widened for the resolver's reading of convention 3).
Extreme-probability gate: not triggered (0.27 is inside 5–95%).
Coherence: P(Yes) should not exceed P(decelerating print) + P(Yes | routine) ≈ 0.64 + 0.04; it does not. C05 (c)'s quantified-lap portion (about 0.06) is a subset of this Yes by construction (conventions 2 and 3 here, convention 2 there). A terms tightening before 5 Nov resolves Yes with high probability regardless of the print (sensitivity table).

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Convention 1 (repeated unearned-fee/FCF/take-rate timing sentences = No) | If the resolver counts any repeated "absent RNPL, X would have grown" sentence as Yes: 0.60 (the sentence has appeared in both 2026 letters; in Q3 management predicts the opposite sign, so not 0.85) |
| Convention 3 (a "lift has moderated / net benefit declined" sentence = Yes) | If the resolver requires the net benefit to be stated as turned or declining in level (not merely a smaller y/y contribution): P(Yes | S2) 0.17, giving 0.22 |
| Convention 2 (quantified lap = Yes) | If a quantified lap is read as a prior-year comp and resolves No: P(Yes | S2) 0.20, giving 0.19 |
| Print states (R01/R02: P(<9) 0.347, P(decel) 0.64) | Nights print ≤ 8.5% with GBV-minus-nights gap > 7 points (realized): S1 0.45, S2 0.55 → 0.46. Nights ≥ 10.6% (realized, R02 state): S1 0.03, S2 0 → 0.14. Team band alone: 0.28 |
| P(S1) = 0.15 | 0.10 (engine central taken as the ceiling): 0.25; 0.20 (worst-cell grid weight): 0.29 |
| P(Yes given S1) = 0.65 | If management holds the "net positive, close to tests" line even in a bad quarter (0.45): 0.24 |
| P(Yes given S2) = 0.27 | 0.22 (lap sizing judged as unlikely as a self-inflicted drag quantification, claim 5): 0.24; 0.35 (moderation wording routine in a decelerating quarter): 0.31 |
| 10-Q creep probability 0.05 in a normal quarter | If the 10-Q adds a clause linking cancellations to Nights and Seats Booked as routine risk disclosure (0.15): 0.34 |
| A terms tightening announced before 5 Nov | Yes moves to 0.70 or more immediately (the criteria's fourth clause) |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-17 to 2026-11-04 | Airbnb newsroom, help-centre article 2143 (RNPL terms), host resource centre | Any change to payment timing, deposits, eligibility restrictions or host opt-out: if motivated by cancellations, move to 0.70 or more; if framed as expansion, −2 points |
| 2026-09-30 | September Inside Airbnb dumps; R01/R02 re-centred | Recompute the partition with the revised P(<9) and P(decel); each −0.5pt on the nights centre ≈ +0.03 |
| 2026-10-13 | EEA/CH single-fee deadline (unverified) | No effect |
| 2026-10-26 to 2026-11-04 | Sell-side previews; any Inside Airbnb October dump | A preview flagging "RNPL cancellations" as a Q3 risk: +3 points; the team's calendar-reopening refresh showing a signature: +5 points; a preview expecting management to "size the lap": +3 points |
| 2026-11-04 | Freeze print-state weights (final R01/R02) | Recompute S1/S2/S3 per §5 |
| 2026-11-05 after close | Letter, press release, 10-Q (same day), call 4:30pm ET | Resolve with the classification table (`c07_classification_table_v2.csv`): search the 10-Q for the RNPL paragraph and diff against the 2Q26 text (datasets/10q_rnpl_language_evolution.csv); then the letter's growth, cash-flow and take-rate paragraphs for a quantified lap, a "moderated/smaller lift" sentence or a dollar timing figure; then the call for "tested", "curve", "expectations", "elevated", "smaller", "moderat"; classify per conventions 1–5 and record which row fired |
| 2026-11-06 | If the 10-Q is not filed on 5 Nov | Hold resolution until the filing; the letter/call verdict stands provisionally |

## 9. Audit trail (revision 2)
Rev-1 datasets are left in place; the revision-2 classification table and scenario partition are new files. The audit's reproduction script is saved as `docs/pitch-forecasts/audits/A04-reproduce.py` and ran clean on `py -3.13`.

## 10. Revision notes
| Change | Finding |
|---|---|
| Metadata: revision 2, revised 2026-09-17; audit and response paths added | — |
| Conventions rewritten as a literal classification table (`c07_classification_table_v2.csv`): a quantified lap effect on a listed 3Q26/4Q26 metric = Yes; a statement that the net benefit or lift has declined or moderated = Yes even if still positive; qualitative lap sentences and repeated direction-only timing sentences stay No and are not promoted automatically; C05/C07 now agree on the quantified-lap object | A04-01 |
| Claim 3: the four prior prints relabelled as descriptive analogues, literal-table count 0–1 of 4, no completed trials of escalation beyond the 2Q26 baseline; base rate discounted and labelled | A04-04 |
| Print states from the run's R01/R02 (P(<9) 0.347, P(decel) 0.64), team band as sensitivity, Kalshi as sensitivity only; the rev-1 undocumented blend withdrawn | A04-10 |
| Claim 12: Kalshi fixed-point fields parsed and saved; the Feb file identified as FY2026 annual | A04-11 |
| Decomposition rebuilt as mutually exclusive scenarios covering the whole contract (adverse / ordinary-decelerating / routine), with the engine's central range labelled a scenario slice, the full-grid −1.37 and module −1.425 quoted, and Q4 effects and non-cash metrics kept open under claim 8 | A04-12 |
| §5 states plainly that no external anchor exists and the three-estimate requirement is unmet | A04-13 |
| Rev-1 arithmetic corrected: 0.28 × 0.6 = 0.168 (rev-1 wrote 0.20) and the strong-print sensitivity 0.1275 (rev-1 wrote 0.11); revision 2 recomputes both from the new partition (0.14 on a ≥10.6% print) | A04-14 |
| Claims 9, 13, 16, 17 reworded to "no relevant result found in the searches recorded" | A04-18 |
| Final 0.20 (0.12–0.32) → 0.27 (0.15–0.40): +0.07 from the S2 scenario the rev-1 contract reading excluded; the adverse-cancellation route itself is unchanged (0.0975 vs rev-1's 0.13 on a mis-stated 0.20 × 0.65) | A04-01, A04-12, A04-14 |
