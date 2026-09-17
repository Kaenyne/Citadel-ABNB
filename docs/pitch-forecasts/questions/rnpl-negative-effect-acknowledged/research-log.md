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
- revision: 1
- agent: fable
- batch: A04 (shared research with C05 and C06; the full query log is repeated here)

## 0b. Question (verbatim)
### Title
Will Airbnb management, in the 3Q26 letter, 10-Q or call, state that RNPL reduced or will reduce a reported metric (nights, GBV, revenue, take rate, unearned fees, FCF or cash) in 3Q26 or 4Q26, beyond the boilerplate "higher cancellation rates" and "timing" language already in the 2Q26 10-Q?
### Resolution Criteria
**Type.** Binary.
**Resolution.** Yes if any of: a quantified negative effect (points, dollars, or "meaningful"/"notable" drag) on any reported metric; an explicit statement that cancellations from RNPL cohorts exceeded expectations or the tested curve; a statement that the net benefit has declined or turned; or a change to RNPL terms motivated by cancellations. No if statements are limited to net-positive reiteration, unchanged boilerplate, or timing effects described as neutral.
### Fine Print
The 2Q26 10-Q sentences ("higher cancellation rates than historic bookings"; GBV/revenue/cash timing "may become less correlated"; FCF seasonality) are the boilerplate baseline; repeating them verbatim is No. Resolution date 5 Nov 2026 (10-Q filing date if later).

Conventions adopted (the question is forecast under these; each is priced as a resolver risk in section 5):
1. The recurring letter sentences "absent RNPL, unearned fees [and FCF] would have grown year-over-year" (D037, D051), the take-rate "timing of when guests booked ... reflects the growth of RNPL" sentence (D049) and the FY26 take-rate "accounting for the timing of bookings versus check-in with RNPL" sentence (D050) are timing effects already on the record before the 2Q26 10-Q and resolve No when repeated in substance, even though the numbers they describe are negative. A new dollar or point quantification of such a timing effect ("RNPL reduced FCF by roughly $X") resolves Yes under the "quantified negative effect" clause.
2. Lap or comparison statements ("tougher comparisons against the RNPL rollout", "we lapped RNPL in the US") describe the prior-year base and resolve No; a statement that cancellations from RNPL cohorts reduced 3Q26 or 4Q26 nights/GBV (quantified, or with "meaningful"/"notable") resolves Yes.
3. A cancellation-rate figure alone ("17% to 18%") is not a listed reported metric; it resolves Yes only if tied to a listed metric or to expectations ("higher than we tested").
4. The 3Q26 10-Q counts in full; Airbnb has filed each 10-Q on the print day (2Q26: 6 Aug; 1Q26: 7 May), so the expected resolution date is 5 Nov.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | The 2Q26 10-Q MD&A sentence "To date, RNPL bookings, which require no payment at the time of booking, have experienced higher cancellation rates than historic bookings in which some or all of the cash was received at the time of booking. As adoption of RNPL and our other flexible payment options continues to grow, the timing among GBV, revenue, and cash receipts may become less correlated." is verbatim in the filing; also "The increase in ADR was driven in part by the continued adoption of RNPL" and the FCF timing sentences | data/raw/regulatory/quantification/abnb_2026q2_10q.html; sources/10q_2Q26_rnpl_passages.txt | 2026-08-06 | 2026-09-17 | yes |
| 2 | 10-Q language evolution: the 3Q25 10-Q does not name RNPL and has no cancellation or timing sentence; the FY25 10-K names RNPL only in the business description and the FX-exposure list ("unbilled amounts for confirmed bookings under the terms of our payment programs"); the 1Q26 10-Q refers only to "deferred payment programs" with timing language ("shifts the timing of when net cash provided by operating activities is recognized"); the 2Q26 10-Q is the first filing to name RNPL and the first to state higher cancellation rates. One escalation step in four filings | datasets/10q_rnpl_language_evolution.csv; https://www.sec.gov/Archives/edgar/data/1559720/000155972025000030/abnb-20250930.htm ; https://www.sec.gov/Archives/edgar/data/1559720/000155972026000014/abnb-20260331.htm ; data/raw/regulatory/quantification/abnb_2025_10k.json | 2026-08-06 | 2026-09-17 | yes |
| 3 | Prior prints scored under the question's criteria: strict reading 0 of 4 Yes; generous reading 3 of 4 (4Q25 "16% to 17%"; 1Q26 "FCF declined slightly ... primarily due to the working capital impact from the continued expansion of RNPL"; 2Q26 take-rate timing) | datasets/prior_prints_scored_under_c07_criteria.csv | 2026-09-17 | 2026-09-17 | yes |
| 4 | Management's standing position, five times on the record: cohorts tested to be "net beneficial ... by the time the cohorts ... had reached their check-in date" (D019); "the cancellation curves have been very close to what we saw from a tested perspective" (D020); "we are already absorbing the elevated level of cancellations" (D021); "a meaningful lift to all booking metrics, net of cancellation" (D033); "Across all regions ... the net impact is positive" (D035) | data/processed/overnight2/D/rnpl_statement_ledger.csv; data/raw/transcripts/web/4Q25.html, 1Q26.html | 2026-05-07 | 2026-09-17 | yes |
| 5 | The only cancellation shock Airbnb has ever sized in growth points was exogenous (Middle East, "approximately 10%" ex-conflict vs "over 9%" reported, 1Q26 letter, D042); it has never quantified a drag from its own product and declined the one direct sizing ask (D007) | data/raw/letters/1Q26_d23351dex991.htm; data/processed/abnb_declined_to_quantify.csv row 2025Q3 | 2026-05-07 | 2026-09-17 | yes |
| 6 | Team cohort engine: the y/y-differenced cancellation drag is −0.15 to −0.93 points of 3Q26 nights (central −0.57 in the unified module) and the level lap is 2–15× larger; the 34-market calendar test found no RNPL cancellation signature (pre-registered null). The team's own evidence does not expect a cancellation quarter bad enough to force an admission | research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md §1.6–1.7, §2.3; docs/rnpl-short-audit/00_SYNTHESIS.md points 1–3; research/notes/overnight2/A_calendar-reopening-34-markets.md (via 03_short-thesis-viability.md rank 6) | 2026-09-11 | 2026-09-17 | yes |
| 7 | The one asymmetry that could make 3Q26 the quarter the net turns: gross uplift scales with the flow of new RNPL bookings (flattening at about 70% adoption) while cancellations scale with the stock reaching payment deadlines (still growing; 46% of 3Q26 excess cancellations come from earlier cohorts) | research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md §4 last paragraph, §2.4 | 2026-09-11 | 2026-09-17 | yes |
| 8 | Management's own forward-testable 3Q26 prediction: RNPL "results in lower unearned fees in Q1 and Q2 and higher unearned fees in Q3" (D038); the cash-timing channel flips positive for RNPL in Q3, so the letter's unearned-fee/FCF sentences are more likely to be framed as RNPL adding to Q3 cash than reducing it | data/raw/letters/1Q26_d23351dex991.htm; data/processed/overnight2/D/D1_prereg_thresholds.csv row 3 | 2026-05-07 | 2026-09-17 | yes |
| 9 | The July 2026 change to RNPL was an expansion of eligible booking types (D044), the opposite direction of a cancellation-motivated tightening; no terms change was announced between 6 Aug and 17 Sep (newsroom, help centre, search) | data/raw/transcripts/web/2Q26.html; https://news.airbnb.com/reserve-now-pay-later/ ; queries 18, 29 | 2026-09-17 | 2026-09-17 | yes |
| 10 | Host-side friction is documented ("phantom bookings"; hosts cannot opt out; staystra 29 Apr 2026) and is the mechanism by which a terms change could arrive; nothing indicates one is planned | https://staystra.com/airbnb-reserve-now-pay-later-hosts-cancellation-policy-2026/ | 2026-04-29 | 2026-09-17 | no |
| 11 | Team 3Q26 nights nowcast +9.5% (band 8.5–10.0), module 9.49 (8.8–10.3); guide "low double-digit" (≥10.0%); a print below the guide floor raises the pressure to explain and the probability that cancellations are named as a cause | docs/pitch-forecasts/00_BRIEF.md rule 6; docs/q3nowcast/SYNTHESIS.md | 2026-09-16 | 2026-09-17 | yes |
| 12 | Kalshi Q3 nights ladder (2026-09-17T02:53:51Z, thin): P(>146m, +9.3%) 0.645; P(>144m, +7.8%) 0.795; implies P(≤146m) about 0.355 and P(≤144m) about 0.205 | sources/kalshi_KXABNB-26NOVNEB_20260917T025351Z.json; datasets/kalshi_q3_nights_implied_2026-09-17.csv | 2026-09-17 | 2026-09-17 | no |
| 13 | No market exists on any Airbnb management statement (Polymarket public-search; Kalshi 4,000 open events scanned) | sources/polymarket_public-search_airbnb_20260917T025229Z.json; sources/kalshi_KXABNBA-27FEBNEB_20260917T025351Z.json | 2026-09-17 | 2026-09-17 | yes |
| 14 | Analyst RNPL/cancellation questions on the call: 1, 1, 2, 0 (3Q25–2Q26); a question is the main route to an unscripted admission and the frequency is falling | data/raw/transcripts/web/*.html (query 12) | 2026-08-06 | 2026-09-17 | no |
| 15 | Management credibility scorecard: unscripted Q&A claims realised 52%, quantified claims 82%; "declined to quantify" 37 instances in 23 calls, four in 2Q26 | research/notes/overnight/03_management-language-and-stock.md §4 | 2026-09-05 | 2026-09-17 | no |
| 16 | Chesky, Communacopia 8 Sep 2026: no mention of RNPL, cancellations or payment options | https://stockanalysis.com/stocks/abnb/transcripts/739626-goldman-sachs-communacopia-technology-conference-2026/ | 2026-09-08 | 2026-09-17 | no |
| 17 | Final 72-hour recency check (2026-09-17): no RNPL terms change, host-policy announcement or management comment this week | WebSearch queries 17, 29 | 2026-09-17 | 2026-09-17 | no |

## 2. Query Log
1. [repo] pandas dump of data/processed/overnight2/D/rnpl_statement_ledger.csv (60 rows)
2. [repo] data/processed/overnight2/D/D1_prereg_thresholds.csv
3. [repo] regex extraction of RNPL/cancellation passages from the 3Q25–2Q26 letters and call mirrors, saved to sources/letters_calls_3Q25-2Q26_rnpl_passages.txt
4. [repo] same for data/raw/regulatory/quantification/abnb_2026q2_10q.html, saved to sources/10q_2Q26_rnpl_passages.txt
5. [repo] quantified-driver regex scan of all 23 letters and calls
6. [repo] metric-persistence matrix (17 metrics × 23 prints), saved to datasets/metric_persistence_matrix_4Q20-2Q26.csv
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

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Reserve Now Pay Later, RNPL, cancellations, 3Q26 Form 10-Q, 5 November 2026

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| A bad cancellation quarter forces an admission ("cancellations ran above our tested curves") | kept as the main Yes route (state S, P 0.20; P(Yes given S) 0.65) | Team engine bounds the drag at −0.15 to −0.93 points and the calendar test is null (claim 6); the stock-vs-flow asymmetry (claim 7) is why S is not negligible |
| 10-Q MD&A escalates again (a new sentence tying higher cancellations to Nights and Seats Booked or GBV) | kept inside both states | One escalation step in four filings (claim 2); an added clause is plausible even in a normal quarter (about 0.04 in not-S) |
| The letter's unearned-fees/FCF sentence is read by the resolver as "RNPL reduced a reported metric" | priced as resolver risk (about 0.03) | Convention 1 says No; in Q3 the RNPL cash effect is predicted positive by management (claim 8), which makes a negative cash sentence less likely anyway |
| A lap quantification is read as a negative effect | priced as resolver risk (about 0.02) | Convention 2 says No |
| A terms change (deposit, shorter deferral, host opt-out) motivated by cancellations | kept, small (about 0.03) | July went the other way (claim 9); host friction exists (claim 10) but there is no signal of a tightening |
| Management reverses its "net positive" language voluntarily | discarded as a standalone route | Five consistent statements (claim 4); reversal only under S |
| Nothing new: net-positive reiteration plus unchanged boilerplate | base case (about 0.80) | Strict-reading base rate 0/4 (claim 3); the FY26 guide-raise cadence and the "no single product" framing point to a routine RNPL paragraph |

## 5. Independent Estimates
- base_rate_estimate: 0.17. Strict reading of the four prints since launch: 0/4 Yes, Laplace (0+1)/(4+2); the generous reading (3/4) is rejected by the fine print, which makes the timing sentences the baseline
- decomposition_estimate: 0.21. P(S: RNPL cancellations materially worse in 3Q26) 0.20 × P(Yes given S) 0.65 + P(not S) 0.80 × P(Yes given not S) 0.10, where P(Yes given not S) = 10-Q creep 0.04 + terms change 0.03 + resolver reads a timing/lap sentence as Yes 0.03. P(S) is anchored on the team band (P(nights < 9.0%) about 0.37 on the nowcast, about 0.28 blended with Kalshi) times the share of a weak print that management would attribute to cancellations rather than to the lap, macro or the World Cup comp (about 0.6)
- anchor_estimate: none available. No market on any management statement (claim 13); the nearest adjacent price is Kalshi P(3Q26 nights ≤ 146m) about 0.355 (claim 12), used only inside P(S)
- anchor_value: n/a (NO_EXTERNAL_ANCHOR)
- final_estimate: 0.20 (credible interval 0.12–0.32)
- final_minus_anchor: n/a. The base rate and decomposition are within 4 points; they are partly independent (the base rate uses only the scored prints; the decomposition uses the engine, the print band and the 10-Q history)

## 6. Final Numbers
P(Yes) = 0.20; credible interval 0.12–0.32.
Extreme-probability gate: not triggered (0.20 is inside 5–95%).
Coherence: P(Yes) here should not exceed P(3Q26 nights < 9.0%) + P(Yes given a strong print), about 0.37 + 0.10; it does not. If C05 resolves (c) via a quantified cancellation drag, C07 resolves Yes by construction; that joint event is about 0.03 and sits inside both numbers.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Convention 1 (repeated unearned-fee/FCF/take-rate timing sentences = No) | If the resolver counts any repeated "absent RNPL, X would have grown" sentence as Yes: 0.60 (the sentence has appeared in both 2026 letters; in Q3 management predicts the opposite sign, so not 0.85) |
| Convention 2 (lap statements = No) | If a quantified lap ("about 2 points of tougher comp") counts as Yes: 0.27 |
| P(S) = 0.20 | Nights print ≤ 8.5% with GBV-minus-nights gap > 7 points: P(S) 0.55, giving 0.42. Nights ≥ 10.6%: P(S) 0.05, giving 0.11 |
| P(Yes given S) = 0.65 | If management holds the "net positive, close to tests" line even in a bad quarter (0.40): 0.16 |
| 10-Q creep probability 0.04 in a normal quarter | If the 10-Q adds a clause linking cancellations to Nights and Seats Booked as routine risk disclosure (0.15): 0.29 |
| A terms tightening announced before 5 Nov | Yes moves to 0.70 or more immediately (the criteria's fourth clause) |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-17 to 2026-11-04 | Airbnb newsroom, help-centre article 2143 (RNPL terms), host resource centre | Any change to payment timing, deposits, eligibility restrictions or host opt-out: if motivated by cancellations, move to 0.70 or more; if framed as expansion, −2 points |
| 2026-10-13 | EEA/CH single-fee deadline (unverified) | No effect |
| 2026-10-26 to 2026-11-04 | Sell-side previews; any Inside Airbnb October dump | A preview flagging "RNPL cancellations" as a Q3 risk: +3 points; the team's calendar-reopening refresh showing a signature: +5 points |
| 2026-11-04 | Freeze print-state weights (nowcast band vs Kalshi) | Recompute P(S) per the sensitivity rows |
| 2026-11-05 after close | Letter, press release, 10-Q (same day), call 4:30pm ET | Resolve: search the 10-Q for the RNPL paragraph and diff against the 2Q26 text (datasets/10q_rnpl_language_evolution.csv); then the letter's cash-flow and take-rate paragraphs; then the call for "tested", "curve", "expectations", "elevated"; classify per conventions 1–4 |
| 2026-11-06 | If the 10-Q is not filed on 5 Nov | Hold resolution until the filing; the letter/call verdict stands provisionally |
