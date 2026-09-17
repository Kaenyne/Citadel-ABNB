# RESEARCH LOG

## 0. Metadata
- question_name: bundle-attribution-quantified
- question_url: n/a (internal pitch-forecast question C05, `docs/pitch-forecasts/QUESTIONS.md`)
- type: multiple_choice
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
- batch: A04 (shared research with C06 and C07; the full query log is repeated in each log)

## 0b. Question (verbatim)
### Title
Will Airbnb quantify the growth contribution of the RNPL / cancellation-policy / single-fee bundle (or of RNPL alone) for 3Q26 at the 5 Nov print, and at what level?
### Resolution Criteria
**Type.** Multiple choice.
**Options.** (a) quantified at ≥2.5 points of nights (or ≥3.5 points of GBV); (b) quantified at 1.5 to <2.5 points of nights (2.0–<3.5 GBV); (c) quantified at <1.5 points of nights (<2.0 GBV); (d) not quantified in points (qualitative only, or share-of-GBV only).
### Fine Print
"Over 200bp" style lower bounds map to the bucket containing the bound. A figure for a subset of features counts. Resolution date 5 Nov 2026.

Conventions adopted for ambiguities (stated here, forecast under them):
1. "For 3Q26" means a figure for the bundle's (or any subset's) year-over-year contribution to 3Q26 nights or GBV growth, in points or basis points, in the letter, the call (prepared remarks or Q&A) or the 10-Q. A GBV figure alone maps by the GBV thresholds in the options.
2. A figure that is only the prior-year comp ("RNPL added about 2 points to Q3 2025 growth, which we lapped") is not a 3Q26 contribution and resolves (d). A figure stated as the 3Q26 y/y effect of the lap or of cancellations ("the RNPL comparison reduced Q3 growth by about 2 points", "cancellations cost roughly 1 point") is a quantified contribution below 1.5 and resolves (c). Both readings are priced in section 5.
3. Letter governs where letter and call differ; if only the call carries a figure, the call figure resolves (the letter is silent, not different).

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | 4Q25 call (Mertz): "In total, we estimate these three features delivered over 200 basis points of growth in nights booked and roughly 300 basis points of growth in GBV in Q4." (ledger D014, mirror transcript) | data/processed/overnight2/D/rnpl_statement_ledger.csv; data/raw/transcripts/web/4Q25.html | 2026-02-12 | 2026-09-17 | yes |
| 2 | 1Q26 call (Mertz): "In total, we estimate these three features delivered approximately three points of nights booked growth and approximately four points of GBV growth in Q1." (D032) | data/raw/transcripts/web/1Q26.html | 2026-05-07 | 2026-09-17 | yes |
| 3 | 2Q26 call gave no points figure. Mertz: "Of the many changes that have collectively contributed to our strong growth, we wanted to provide an update on two ... First, we continue to see Reserve Now, Pay Later benefit the business. It drove more bookings, longer booking lead times, and contributed to the increase in ADR. Specifically in Q2, over 20% of our total GBV was booked using this flexible payment option." Chesky: "there is no one thing." (D043, D045) | data/raw/transcripts/web/2Q26.html | 2026-08-06 | 2026-09-17 | yes |
| 4 | The 2Q26 drop happened while nights accelerated (+10.34% vs +9.15% in 1Q26) and the print was received at +17.4%; the figure was dropped during a strong quarter as a deliberate "collective actions" reframing, not because the number turned bad | data/processed/abnb_driver_history_quarterly.csv; docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §5.1 | 2026-09-11 | 2026-09-17 | yes |
| 5 | Persistence base rate, computed here over 17 quantified metrics × 23 prints (4Q20–2Q26; regex scan of letters and call mirrors): a metric disclosed at t is disclosed at t+1 in 91/111 = 0.82 of metric-quarters; after a one-quarter gap it returns the following quarter in 5/19 = 0.26 of cases; the five series that stopped flattering (cross-border share, LTS share, urban share, listings growth %, 1BR-vs-hotel) returned 0/5 | datasets/metric_persistence_matrix_4Q20-2Q26.csv; datasets/metric_gap_events.csv | 2026-09-17 | 2026-09-17 | yes |
| 6 | In 23 prints, a product/driver contribution stated in points of nights or GBV growth appears in exactly two (4Q25, 1Q26: the bundle). Every other points-attribution is calendar (Easter/leap, 4Q25 and 1Q25), FX (1Q25 and the guides), an exogenous shock (Middle East ~1 point, 1Q26) or a share statement (LatAm +200bp of business share, 2Q25) | quantified-driver regex scan of data/raw/letters/*.htm and data/raw/transcripts/web/*.html (query 5) | 2026-09-17 | 2026-09-17 | yes |
| 7 | The Middle East cancellation drag, quantified at ~1 point in 1Q26 ("Absent the impact of the conflict, we estimate growth ... would have been approximately 10%") and as "roughly 100bps headwind" in the 2Q26 guide, was not quantified in 2Q26 ("the impact to our business from the conflict was less than we had anticipated"): a quantified driver dropped the next quarter | data/raw/letters/1Q26_d23351dex991.htm; data/raw/transcripts/web/2Q26.html | 2026-08-06 | 2026-09-17 | no |
| 8 | Management declined to size RNPL's share of the US acceleration when asked (Richard Clarke, 3Q25 call): the answer substituted the ~70% take-up figure (D007; declined_to_quantify row 2025Q3). 37 declines in 23 calls, four in 2Q26 | data/processed/abnb_declined_to_quantify.csv | 2026-09-05 | 2026-09-17 | yes |
| 9 | Analyst questions naming RNPL on the call: 3Q25 one, 4Q25 one, 1Q26 two, 2Q26 zero (scan of Q&A text) | data/raw/transcripts/web/{3Q25,4Q25,1Q26,2Q26}.html (query 12) | 2026-08-06 | 2026-09-17 | no |
| 10 | Lap schedule: US RNPL live from "the beginning of Q3" 2025 (call) / August (letter) so it laps in 3Q26 (partial-quarter residual +0.30 to +0.35); NA cancellation redesign and fee tranche 1 (Oct–Dec 2025, 0.66 pts of total nights) and the ex-NA legs (0.70–0.88 fee/cancellation; 0.87–1.05 ex-NA RNPL) are still inside the 3Q26 y/y window; the July 2026 eligibility expansion is fresh treatment (D044) | research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md §2.2, §2.5; docs/rnpl-short-audit/00_SYNTHESIS.md point 2 | 2026-09-11 | 2026-09-17 | yes |
| 11 | Mechanical bundle contribution management could truthfully state for 3Q26: gross legs still in window 2.63–3.24 points, less the y/y cancellation drag (−0.15 to −0.93), net 1.7–3.1, central about 2.3–2.5, straddling the (a)/(b) boundary | datasets/bundle_3q26_mechanical_contribution.csv (computed from claim 10) | 2026-09-17 | 2026-09-17 | yes |
| 12 | Management's two prior figures were rounded to the nearest whole point or "over 200bp"; its rounding vocabulary is "over X", "roughly X", "approximately X" (D014, D031, D032, D043, D047) | data/processed/overnight2/D/rnpl_statement_ledger.csv | 2026-09-11 | 2026-09-17 | yes |
| 13 | Team 3Q26 nights nowcast +9.5% (band 8.5–10.0; reviews index walk-forward RMSE 1.48pp vs naive 2.16); RNPL module 9.49 (band 8.8–10.3); 3Q25 base 133.6m so 10.0% = 147.0m | docs/pitch-forecasts/00_BRIEF.md rule 6; docs/q3nowcast/SYNTHESIS.md; docs/rnpl-short-audit/00_SYNTHESIS.md | 2026-09-16 | 2026-09-17 | yes |
| 14 | Kalshi KXABNB-26NOVNEB (Q3 2026 nights & experiences booked), fetched 2026-09-17T02:53:51Z: P(>146m, +9.3%) mid 0.645 (bid .63/ask .66); P(>148m, +10.8%) 0.525 (.50/.55); P(>150m, +12.3%) 0.34; P(>144m, +7.8%) 0.795. Volume and open-interest fields null (thin) | https://api.elections.kalshi.com/trade-api/v2/markets?event_ticker=KXABNB-26NOVNEB ; sources/kalshi_KXABNB-26NOVNEB_20260917T025351Z.json | 2026-09-17 | 2026-09-17 | no |
| 15 | No Polymarket or Kalshi market exists on any Airbnb disclosure, RNPL metric, or the 5 Nov call content; Polymarket has only closed "beat earnings" and open price-ladder markets for ABNB (public-search 2026-09-17T02:52:29Z); Kalshi has only the two nights markets (4,000 open events scanned) | sources/polymarket_public-search_airbnb_20260917T025229Z.json; sources/polymarket_public-search_abnb-earnings_20260917T025229Z.json; sources/kalshi_KXABNBA-27FEBNEB_20260917T025351Z.json | 2026-09-17 | 2026-09-17 | yes |
| 16 | Pre-registered team card: "a figure ≥2.5 points weakens the drag hypothesis; none given or ≤1.5 supports; qualitative update only inconclusive (what 2Q26 gave)" | data/processed/overnight2/D/D1_prereg_thresholds.csv row 7 | 2026-09-11 | 2026-09-17 | no |
| 17 | Chesky at Goldman Communacopia (8 Sep 2026) did not mention RNPL, cancellations or payment options and gave no Q3 quantitative update; no other Airbnb management appearance 1 Aug–11 Sep | https://stockanalysis.com/stocks/abnb/transcripts/739626-goldman-sachs-communacopia-technology-conference-2026/ ; data/processed/q3nowcast/G/intra_quarter_commentary.csv rows 27–36 | 2026-09-08 | 2026-09-17 | no |
| 18 | 3Q26 results expected 5 Nov 2026 after close (search results; IR calendar not yet posted) | https://investors.airbnb.com/press-releases/default.aspx (query 20) | 2026-09-17 | 2026-09-17 | no |
| 19 | Airbnb's "Project Hawaii" innovation model makes attribution diffuse by design; 2Q26 message "there was no single product" | docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §4 row 12 Feb 2026; data/raw/transcripts/web/2Q26.html | 2026-08-06 | 2026-09-17 | no |
| 20 | Management frames the bundle "net of cancellation" (D033) and says the 2H26 comps are tougher "against the rollout of Reserve Now, Pay Later in 2025" (D040, 1Q26 letter): the lap vocabulary already exists and is qualitative | data/raw/letters/1Q26_d23351dex991.htm | 2026-05-07 | 2026-09-17 | yes |
| 21 | Final 72-hour recency check (2026-09-17): no RNPL announcement, terms change or management comment in the last week; latest RNPL newsroom items are the Feb–Mar 2026 market launches | WebSearch "Airbnb "Reserve Now, Pay Later" news this week"; "Airbnb news" | 2026-09-17 | 2026-09-17 | no |

## 2. Query Log
1. [repo] pandas dump of data/processed/overnight2/D/rnpl_statement_ledger.csv (60 rows, all columns)
2. [repo] data/processed/overnight2/D/D1_prereg_thresholds.csv
3. [repo] regex extraction of "Reserve Now|RNPL|Pay Later|cancellation" passages from the 3Q25, 4Q25, 1Q26, 2Q26 letters and call mirrors, saved to sources/letters_calls_3Q25-2Q26_rnpl_passages.txt
4. [repo] same extraction from data/raw/regulatory/quantification/abnb_2026q2_10q.html, saved to sources/10q_2Q26_rnpl_passages.txt
5. [repo] regex scan of all 23 letters and calls for quantified driver attributions ("approximately|roughly|over ... N points|basis points ... growth|Nights|GBV")
6. [repo] metric-persistence matrix, 17 metrics × 23 prints, saved to datasets/metric_persistence_matrix_4Q20-2Q26.csv; gap events to datasets/metric_gap_events.csv
7. [repo] RNPL passages in data/raw/regulatory/quantification/abnb_2025_10k.json
8. [repo] data/processed/abnb_declined_to_quantify.csv (37 rows)
9. [SEC API] https://data.sec.gov/submissions/CIK0001559720.json (10-Q/10-K accession list since 2025-07)
10. [Polymarket API] public-search?q=airbnb ; public-search?q=ABNB%20earnings (2026-09-17T02:52:29Z)
11. [Kalshi API] events?status=open&limit=200, 20 pages (4,000 events) grep airbnb|abnb|earnings, then markets?event_ticker=KXABNB-26NOVNEB and KXABNBA-27FEBNEB (02:53:51Z)
12. [repo] analyst-question scan of the 3Q25–2Q26 call Q&A for RNPL and cancellation asks
13. [repo] 2Q26 letter and call passages on "Middle East" and "World Cup" (was the conflict drag re-quantified? no)
14. [SEC fetch] abnb-20250930.htm (3Q25 10-Q) and abnb-20260331.htm (1Q26 10-Q), raw grep for RNPL terms
15. [repo] research/notes/overnight/03_management-language-and-stock.md, "claims that were quietly dropped" section
16. [repo] data/processed/overnight/02_guidance_ledger.csv scan for RNPL rows (none)
17. WebSearch: Airbnb news (neutral pass)
18. WebSearch: Airbnb Reserve Now Pay Later September 2026
19. WebSearch: Airbnb Reserve Now Pay Later cancellations analyst Q3 2026
20. WebSearch: Airbnb third quarter 2026 results date November
21. WebFetch: https://news.airbnb.com/reserve-now-pay-later/ (terms; no updated date)
22. WebFetch: https://staystra.com/airbnb-reserve-now-pay-later-hosts-cancellation-policy-2026/ (published 2026-04-29)
23. WebFetch: https://www.rentalscaleup.com/insurance-pay-later-cancellation-fees-what-airbnb-now-earns-on-top-of-your-stay-rates/ (published 2026-07-03)
24. WebFetch: https://finance.yahoo.com/news/airbnb-set-report-q3-earnings-181600069.html (a November 2025 preview: STALE, zero weight)
25. [repo] grep research/notes/q3nowcast/, docs/q3nowcast/, data/processed/q3nowcast/G/intra_quarter_commentary.csv for conference RNPL mentions (none)
26. WebSearch: Airbnb Mertz conference September 2026 "Reserve Now, Pay Later" (no September appearance found)
27. [repo] grep 1Q26/2Q26 letter and call for "extended cancellation" (none; the rentalscaleup "June 2026 extended cancellation option" line is unverified, zero weight)
28. WebFetch: stockanalysis.com Communacopia 8 Sep 2026 transcript (no RNPL mention)
29. WebSearch: Airbnb "Reserve Now, Pay Later" news this week (final 72-hour recency check; nothing new)

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, Reserve Now Pay Later, RNPL, single service fee, cancellation policy, 3Q26 shareholder letter, 5 November 2026

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| The 2Q26 silence was a one-off and the points figure returns as a routine update (P(quantified) 0.5 or more) | discarded | The drop coincided with an explicit reframing ("no single product", "update on two") during a strong quarter (claims 3, 4, 19); one-quarter-gap return rate is 5/19 (claim 5); analyst RNPL questions fell to zero in 2Q26 (claim 9) |
| Management quantifies the lap to explain a deceleration ("the RNPL comparison cost about 2 points") | kept as the main (c) route (about 0.05) | Management already has qualitative lap vocabulary (claim 20) and quantified an exogenous drag once (claim 7) but has never quantified a drag from its own product (claim 8); most likely only if nights print below 9% |
| Management quantifies an RNPL-alone contribution ("RNPL added about 2 points globally") | kept inside (a)/(b) | Counts under the fine print; the mechanical number is 2.3–2.5 (claim 11) so a stated figure would most likely read "over 2 points" (b) |
| A GBV-only figure resolves differently from a nights figure | handled | Options carry GBV thresholds; "roughly 3 points of GBV" maps to (b) |
| A share-of-GBV disclosure ("over 20%") is a quantification | discarded | Fine print: share-of-GBV only is (d); that object is C06 |
| A points figure in the 10-Q MD&A | discarded as a route | Airbnb's MD&A has never carried a product contribution in points (10-Q evolution dataset in the C07 folder); the 2Q26 10-Q named RNPL only for ADR direction and cancellation rates |
| Q&A forces a number | kept, small (about 0.04) | Management answered 0 of 1 direct sizing asks with a number (claim 8); the two prior figures came in prepared remarks |

## 5. Independent Estimates
- base_rate_estimate: P(d) = 0.74, vector (a 0.08, b 0.12, c 0.06, d 0.74). One-quarter-gap return rate 5/19 = 0.26 (claim 5); the flattering/non-flattering split gives 0/5 vs 5/14 and the bundle sits between the two classes, so no regime adjustment; conditional split of the quantified mass a 0.30 / b 0.45 / c 0.25 from claims 11–12
- decomposition_estimate: P(quantified) = 0.265, P(d) = 0.735. Print-state mixture: P(nights ≥10.0%) 0.42 × P(quantify | strong) 0.15 + P(9.0–9.99%) 0.30 × 0.28 + P(<9.0%) 0.28 × 0.42 = 0.063 + 0.084 + 0.118. Print-state weights blend the team band (claim 13: P(≥10) about 0.37 at sd 1.48 around 9.5) with the Kalshi ladder (claim 14: P(≥10.8%) 0.525); conditional split as above, with (c) enlarged to 0.25 of the quantified mass for the lap/cancellation-drag reading of convention 2
- anchor_estimate: none available. No market or consensus exists on the disclosure (claim 15); the only adjacent price is Kalshi's nights ladder (claim 14), used solely to weight the print states; the team's pre-registered card (claim 16) treats "qualitative update only" as the modal outcome without a probability
- anchor_value: n/a (NO_EXTERNAL_ANCHOR; Kalshi P(3Q26 nights > 148m) = 0.525 at 2026-09-17T02:53:51Z is the conditioning input, not an anchor on this question)
- final_estimate: a 0.08, b 0.12, c 0.07, d 0.73
- final_minus_anchor: n/a. Base-rate and decomposition agree within 1 point on P(d); they share the ledger and the 2Q26 silence, so the agreement is partly by construction; the print-state weights are the only input the base rate does not use

## 6. Final Numbers
| Option | Probability |
|---|---|
| (a) quantified ≥2.5 pts nights (≥3.5 GBV) | 0.08 |
| (b) quantified 1.5 to <2.5 pts (2.0–<3.5 GBV) | 0.12 |
| (c) quantified <1.5 pts (<2.0 GBV), incl. a quantified lap or cancellation drag for 3Q26 | 0.07 |
| (d) not quantified in points | 0.73 |
Sum 1.00. P(any quantification) = 0.27. No option is at or below 2%, so the extreme-probability gate is not triggered; the thinnest option (c) is held at 0.07 because it carries two distinct routes (a small RNPL-alone figure; a quantified drag) either of which a resolver could count.
Tail-trade note: reallocating to (a 0.09, b 0.13, c 0.08, d 0.70) costs about 0.01 in expected log score if (d) resolves and caps the loss if any quantified bucket resolves; the vector above is the calibrated one, the 0.70 variant is the defensive one.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| The 2Q26 drop was an active reframing (return rate 0.26) | If incidental and the figure is routine (return rate near the 0.82 continuation for still-relevant metrics): P(d) 0.45; a 0.16, b 0.25, c 0.14 |
| Print-state weights (P(≥10%) 0.42) | Nights print ≥10.6% (acceleration): P(d) 0.85; a 0.06, b 0.06, c 0.03. Nights ≤8.5%: P(d) 0.58; a 0.05, b 0.12, c 0.25 |
| Convention 2 (prior-year comp figure = d; 3Q26 lap drag = c) | If a resolver counts any prior-year comp figure as a 3Q26 quantification under (c): c 0.13, d 0.67 |
| Conditional split a/b/c = 0.30/0.45/0.25 given quantification | If management rounds up to "approximately 3 points" again (mechanical high end 3.1, claim 11): a 0.15, b 0.08 |
| July eligibility expansion small (+0.1 to +0.3) | If the expansion is worth 1 point or more and management wants credit for it: P(quantified) 0.35, a 0.14 |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-17 to 2026-10-30 | Airbnb IR: 3Q26 results date announcement (expected mid-October); any newsroom RNPL post | Confirm 5 Nov; a newsroom post quantifying RNPL's contribution or a new eligibility expansion raises P(quantified) by about 5 points |
| 2026-10-13 | Single-fee migration deadline (EEA/CH) per host notices (unverified in repo, RED_TEAM §7) | No direct effect; a management statement on fee-migration completion in the letter makes a fee-leg quantification slightly likelier (+2 points to a/b) |
| 2026-10-26 to 2026-11-04 | Sell-side previews; any Airbnb conference appearance | If a preview says the company will "size the RNPL lap", +5 points to the quantified mass; if Mertz appears and declines to size RNPL, −3 points |
| 2026-11-04 | Freeze the print-state weights: last nowcast band vs Kalshi ladder | Recompute the decomposition with the final band; move P(d) per the sensitivity table |
| 2026-11-05 after close | 3Q26 letter, 10-Q, press release; call 4:30pm ET | Resolve: read the letter first (governs), then the call; classify per conventions 1–3; if the letter has a points figure, resolve immediately |
| 2026-11-05 to 2026-11-06 | Post-call | If a quantified lap drag is stated, record which convention the resolver applied, for C07 coherence |
