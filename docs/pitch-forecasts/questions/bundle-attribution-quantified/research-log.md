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
- revision: 2
- revised: 2026-09-17
- agent: fable
- batch: A04 (shared research with C06 and C07; the full query log is repeated in each log)
- audit: `docs/pitch-forecasts/audits/A04-research-audit.md` (Astra); response `docs/pitch-forecasts/audits/A04-audit-response.md`

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
2. A figure that is only the prior-year comp ("RNPL added about 2 points to Q3 2025 growth, which we lapped") is not a 3Q26 contribution and resolves (d). A figure stated as the 3Q26 y/y effect of the lap or of cancellations ("the RNPL comparison reduced Q3 growth by about 2 points", "cancellations cost roughly 1 point") is a quantified contribution below 1.5 and resolves (c). Both readings are priced in section 5. (Revision 2: C07's classification table now counts the same quantified-lap sentence as C07 = Yes, so the two logs agree on the object; the joint event is inside both numbers.)
3. Letter governs where letter and call differ; if only the call carries a figure, the call figure resolves (the letter is silent, not different).
4. (Revision 2) An RNPL-alone figure and a three-feature bundle figure are different objects: the fine print counts either, but the mechanical size of an RNPL-alone 3Q26 contribution (claim 11, `rnpl_only` branch) is 1.3–1.7 points gross, so an RNPL-alone statement lands in (c) or low (b), and only a bundle statement reaches (a).

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | 4Q25 call (Mertz): "In total, we estimate these three features delivered over 200 basis points of growth in nights booked and roughly 300 basis points of growth in GBV in Q4." (ledger D014, mirror transcript) | data/processed/overnight2/D/rnpl_statement_ledger.csv; data/raw/transcripts/web/4Q25.html | 2026-02-12 | 2026-09-17 | yes |
| 2 | 1Q26 call (Mertz): "In total, we estimate these three features delivered approximately three points of nights booked growth and approximately four points of GBV growth in Q1." (D032) | data/raw/transcripts/web/1Q26.html | 2026-05-07 | 2026-09-17 | yes |
| 3 | 2Q26 call gave no points figure. Mertz: "Of the many changes that have collectively contributed to our strong growth, we wanted to provide an update on two ... First, we continue to see Reserve Now, Pay Later benefit the business. It drove more bookings, longer booking lead times, and contributed to the increase in ADR. Specifically in Q2, over 20% of our total GBV was booked using this flexible payment option." Chesky: "there is no one thing." (D043, D045) | data/raw/transcripts/web/2Q26.html | 2026-08-06 | 2026-09-17 | yes |
| 4 | The 2Q26 drop coincided with nights accelerating (+10.34% vs +9.15% in 1Q26; `abnb_driver_history_quarterly.csv`) and a +17.4% day-one reaction (+16.3% excess). The reading that the figure was dropped as a deliberate "collective actions" reframing rather than because the number turned bad is an **inference from the coincidence of timing and message** (claim 3), not an established fact; it is carried as the leading hypothesis with the alternative (the number was simply no longer flattering after the US lap approached) priced in section 7 | data/processed/abnb_driver_history_quarterly.csv; data/processed/abnb_guidance_reaction_panel.csv; docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §5.1 | 2026-09-11 | 2026-09-17 | yes |
| 5 | Persistence base rate, revision 2 (partial recode of the 16-metric × 23-print matrix after audit A04-02/03: three false-positive cells removed, the Guest Favorites cumulative-nights row completed from the letters; all other cells uncertified): continuation All 93/113 = 0.82, W1 (target ≥1Q23) 60/78 = 0.77, W2 (target ≥1Q24) 40/56 = 0.71; return after a one-quarter gap All 4/18 = 0.22, W1 4/16 = 0.25, W2 4/15 = 0.27. Metric-quarters are not independent management decisions (per-metric counts in `persistence_by_metric_v2.csv`). The five "stopped flattering" series (0/5 returns) are a retrospective grouping and are reported as descriptive only; the other 13 gap events returned 4/13 | datasets/metric_persistence_matrix_v2_4Q20-2Q26.csv; datasets/persistence_rates_v2.csv; datasets/metric_gap_events_v2.csv; datasets/metric_persistence_matrix_v2_recode.py (rev-1 files kept alongside) | 2026-09-17 | 2026-09-17 | yes |
| 6 | In 23 prints, a product/driver contribution stated in points of nights or GBV growth appears in exactly two (4Q25, 1Q26: the bundle). Every other points-attribution is calendar (Easter/leap, 4Q25 and 1Q25), FX (1Q25 and the guides), an exogenous shock (Middle East ~1 point, 1Q26) or a share statement (LatAm +200bp of business share, 2Q25). RNPL-specific: bundle points disclosed in 2 of 4 post-launch prints, continuation 1/2, completed return-after-gap trials n = 0 (the 3Q26 print is the first) | quantified-driver regex scan of data/raw/letters/*.htm and data/raw/transcripts/web/*.html (query 5); audit A04-04 | 2026-09-17 | 2026-09-17 | yes |
| 7 | The Middle East cancellation drag, quantified at ~1 point in 1Q26 ("Absent the impact of the conflict, we estimate growth ... would have been approximately 10%") and as "roughly 100bps headwind" in the 2Q26 guide, was not quantified in 2Q26 ("the impact to our business from the conflict was less than we had anticipated"): a quantified driver dropped the next quarter | data/raw/letters/1Q26_d23351dex991.htm; data/raw/transcripts/web/2Q26.html | 2026-08-06 | 2026-09-17 | no |
| 8 | Management declined to size RNPL's share of the US acceleration when asked (Richard Clarke, 3Q25 call): the answer substituted the ~70% take-up figure (D007; declined_to_quantify row 2025Q3). 37 declines in 23 calls, four in 2Q26 | data/processed/abnb_declined_to_quantify.csv | 2026-09-05 | 2026-09-17 | yes |
| 9 | Analyst questions naming RNPL on the call: 3Q25 one, 4Q25 one, 1Q26 two, 2Q26 zero (scan of Q&A text) | data/raw/transcripts/web/{3Q25,4Q25,1Q26,2Q26}.html (query 12) | 2026-08-06 | 2026-09-17 | no |
| 10 | Lap schedule: US RNPL live from "the beginning of Q3" 2025 (call) / August (letter) so it laps in 3Q26 (partial-quarter residual +0.30 to +0.35); NA cancellation redesign and fee tranche 1 (Oct–Dec 2025, 0.66 pts of total nights) and the ex-NA legs (a 1.75-point ex-NA bundle split 40–50% fee/cancellation, 60–50% RNPL: 0.70/1.05 or 0.88/0.87, **paired**) are still inside the 3Q26 y/y window; the July 2026 eligibility expansion is fresh treatment (D044) | research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md §2.2, §2.5; docs/rnpl-short-audit/00_SYNTHESIS.md point 2 | 2026-09-11 | 2026-09-17 | yes |
| 11 | Scenario-implied bundle contribution for 3Q26 under the team's fitted allocation (revision 2, paired endpoints): gross legs in window 2.81–3.06 points; less the y/y-differenced cancellation-propensity slice (−0.15 to −0.93, a scenario slice that may partly double-count the cancellations already netted in the fitted baseline), net 1.88–2.91, central 2.4–2.6, straddling the (a)/(b) boundary. RNPL-alone branch: 1.27–1.70 gross, 0.34–1.55 net, i.e. (c) or low (b). These are conditional scenario calculations on a fitted allocation of management's own net figure, not measurements of what management "could truthfully state" | datasets/bundle_3q26_mechanical_contribution_v2.csv (rev-1 file kept; its 2.63–3.24 / 1.7–3.1 range summed incompatible endpoints, audit A04-05) | 2026-09-17 | 2026-09-17 | yes |
| 12 | Management's two prior figures were rounded to the nearest whole point or "over 200bp"; its rounding vocabulary is "over X", "roughly X", "approximately X" (D014, D031, D032, D043, D047). GBV contributions ran about one point above nights in both disclosures | data/processed/overnight2/D/rnpl_statement_ledger.csv | 2026-09-11 | 2026-09-17 | yes |
| 13 | Print-state weights (revision 2): from the run's R01/R02 forecasts, which landed after revision 1 and are the run's reconciled print-state numbers: P(nights ≥10.0%) = 0.42 (R01), P(≥10.6%) = 0.32 (R02), implied N(9.67, 1.70) giving P(<9.0%) 0.347 and P(9.0–9.99%) 0.233. Team band alone (brief rule 6: N(9.5, 1.48)) gives 0.368 / 0.264 / 0.368; Kalshi is a separately reported sensitivity only. 3Q25 base 133.6m so 10.0% = 147.0m | docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/forecasts/2026-09-17-forecast.json; risk-q3-nights-accelerates/forecasts/2026-09-17-forecast.json; docs/pitch-forecasts/00_BRIEF.md rule 6; docs/q3nowcast/SYNTHESIS.md | 2026-09-17 | 2026-09-17 | yes |
| 14 | Kalshi KXABNB-26NOVNEB (Q3 2026 nights & experiences booked), fetched 2026-09-17T02:53:51Z: P(>146m, +9.3%) mid 0.645 (bid .63/ask .66); P(>148m, +10.8%) 0.525 (.50/.55); P(>150m, +12.3%) 0.34; P(>144m, +7.8%) 0.795. Fixed-point fields (revision 2): `volume_fp` 3,237.21 contracts across the ladder (998.66 at 146m), `open_interest_fp` 2,178.46, `volume_24h_fp` 0 at every strike, `updated_time` 2026-08-04T18:47:36Z identical across strikes (a batch metadata stamp: it does not prove when each quote last changed). Rev-1's "volume null" read obsolete field names | https://api.elections.kalshi.com/trade-api/v2/markets?event_ticker=KXABNB-26NOVNEB ; sources/kalshi_KXABNB-26NOVNEB_20260917T025351Z.json; datasets/kalshi_q3_nights_implied_v2_2026-09-17.csv | 2026-09-17 | 2026-09-17 | no |
| 15 | No market on any Airbnb disclosure, RNPL metric or call content was found in the searches recorded: Polymarket public-search returned only closed "beat earnings" and open price-ladder markets for ABNB (2026-09-17T02:52:29Z); the Kalshi open-events scan (20 pages, 4,000 events, grep airbnb/abnb/earnings) returned the Q3 nights ladder and an **FY2026 annual** nights ladder (KXABNBA-27FEBNEB, strikes 570–590m; not a Q4 market). Absence is claimed only for these recorded searches | sources/polymarket_public-search_airbnb_20260917T025229Z.json; sources/polymarket_public-search_abnb-earnings_20260917T025229Z.json; sources/kalshi_KXABNBA-27FEBNEB_20260917T025351Z.json | 2026-09-17 | 2026-09-17 | yes |
| 16 | Pre-registered team card: "a figure ≥2.5 points weakens the drag hypothesis; none given or ≤1.5 supports; qualitative update only inconclusive (what 2Q26 gave)" | data/processed/overnight2/D/D1_prereg_thresholds.csv row 7 | 2026-09-11 | 2026-09-17 | no |
| 17 | Chesky at Goldman Communacopia (8 Sep 2026) did not mention RNPL, cancellations or payment options and gave no Q3 quantitative update (transcript fetched); no other Airbnb management appearance 1 Aug–11 Sep was found in the repo's intra-quarter commentary file or the searches recorded (no conference-page snapshot saved) | https://stockanalysis.com/stocks/abnb/transcripts/739626-goldman-sachs-communacopia-technology-conference-2026/ ; data/processed/q3nowcast/G/intra_quarter_commentary.csv rows 27–36 | 2026-09-08 | 2026-09-17 | no |
| 18 | 3Q26 results expected 5 Nov 2026 after close (search results; IR calendar not yet posted) | https://investors.airbnb.com/press-releases/default.aspx (query 20) | 2026-09-17 | 2026-09-17 | no |
| 19 | Airbnb's "Project Hawaii" innovation model makes attribution diffuse by design; 2Q26 message "there was no single product" | docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §4 row 12 Feb 2026; data/raw/transcripts/web/2Q26.html | 2026-08-06 | 2026-09-17 | no |
| 20 | Management frames the bundle "net of cancellation" (D033) and says the 2H26 comps are tougher "against the rollout of Reserve Now, Pay Later in 2025" (D040, 1Q26 letter; "tougher comps in the back half" repeated on the 2Q26 call without naming RNPL): the lap vocabulary already exists and is qualitative | data/raw/letters/1Q26_d23351dex991.htm; data/raw/transcripts/web/2Q26.html | 2026-08-06 | 2026-09-17 | yes |
| 21 | Final 72-hour recency check (2026-09-17): no relevant result found in the searches recorded (queries 17, 18, 26, 29) for an RNPL announcement, terms change or management comment in the last week; the latest RNPL newsroom items retrieved are the Feb–Mar 2026 market launches. No search-result snapshots were saved; this is a statement about the recorded searches, not a proof of absence | WebSearch "Airbnb "Reserve Now, Pay Later" news this week"; "Airbnb news" | 2026-09-17 | 2026-09-17 | no |

## 2. Query Log
1. [repo] pandas dump of data/processed/overnight2/D/rnpl_statement_ledger.csv (60 rows, all columns)
2. [repo] data/processed/overnight2/D/D1_prereg_thresholds.csv
3. [repo] regex extraction of "Reserve Now|RNPL|Pay Later|cancellation" passages from the 3Q25, 4Q25, 1Q26, 2Q26 letters and call mirrors, saved to sources/letters_calls_3Q25-2Q26_rnpl_passages.txt
4. [repo] same extraction from data/raw/regulatory/quantification/abnb_2026q2_10q.html, saved to sources/10q_2Q26_rnpl_passages.txt
5. [repo] regex scan of all 23 letters and calls for quantified driver attributions ("approximately|roughly|over ... N points|basis points ... growth|Nights|GBV")
6. [repo] metric-persistence matrix, 16 metrics × 23 prints, saved to datasets/metric_persistence_matrix_4Q20-2Q26.csv; gap events to datasets/metric_gap_events.csv
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
30. (rev 2) [repo] re-read of the 1Q25 and 3Q25 call mirrors around "cancellation rate" (both hits are Richard Clarke's questions; no management rate) and the 2Q26 call around "Middle East" (qualitative), to verify audit A04-02
31. (rev 2) [repo] grep of all 23 letters for "Guest Favorite" with a digit: cumulative nights booked at Guest Favorite listings stated in 1Q24 (>100m), 2Q24 (>150m), 3Q24 (>200m), 1Q25 (>350m), 2Q25 (>400m), 3Q25 (~500m), 4Q25 (>500m); none in 4Q24, 1Q26, 2Q26
32. (rev 2) [computed] datasets/metric_persistence_matrix_v2_recode.py → persistence_rates_v2.csv (both windows), metric_gap_events_v2.csv, persistence_by_metric_v2.csv
33. (rev 2) [computed] docs/pitch-forecasts/audits/A04-response-datasets.py → bundle_3q26_mechanical_contribution_v2.csv, c05_state_decomposition_v2.csv, kalshi_q3_nights_implied_v2_2026-09-17.csv
34. (rev 2) [repo] research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md §2.3 and §2.5; data/processed/overnight2/D/D1_bundle_crosscheck.csv (1Q26 row "fitted, so agreement is by construction")
35. (rev 2) [repo] risk-q3-nights-meets-guide and risk-q3-nights-accelerates forecast JSONs and §5–6 of their logs (print-state weights)

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, Reserve Now Pay Later, RNPL, single service fee, cancellation policy, 3Q26 shareholder letter, 5 November 2026

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| The 2Q26 silence was a one-off and the points figure returns as a routine update (P(quantified) 0.5 or more) | discarded | The drop coincided with an explicit reframing ("no single product", "update on two") during a strong quarter (claims 3, 4, 19; the reframing reading is an inference); one-quarter-gap return rate 0.22–0.27 in both windows (claim 5); analyst RNPL questions fell to zero in 2Q26 (claim 9) |
| Management quantifies the lap to explain a deceleration ("the RNPL comparison cost about 2 points") | kept as the main (c) route (about 0.06, concentrated in the sub-9% print state) | Management already has qualitative lap vocabulary (claim 20) and quantified an exogenous drag once (claim 7) but has never quantified a drag from its own product (claim 8); most likely only if nights print below 9% |
| Management quantifies an RNPL-alone contribution ("RNPL added about 1.5 points globally") | kept inside (b)/(c) (revision 2: convention 4) | Counts under the fine print; the RNPL-alone mechanical number is 1.3–1.7 gross (claim 11), so a stated RNPL-alone figure lands in (c) or low (b), not (a) |
| A GBV-only figure resolves differently from a nights figure | handled | Options carry GBV thresholds; "roughly 3 points of GBV" maps to (b) |
| A share-of-GBV disclosure ("over 20%") is a quantification | discarded | Fine print: share-of-GBV only is (d); that object is C06 |
| A points figure in the 10-Q MD&A | discarded as a route | Airbnb's MD&A has never carried a product contribution in points (10-Q evolution dataset in the C07 folder); the 2Q26 10-Q named RNPL only for ADR direction and cancellation rates |
| Q&A forces a number | kept, small (about 0.04) | Management answered 0 of 1 direct sizing asks with a number (claim 8); the two prior figures came in prepared remarks |
| The figure was dropped because it stopped flattering (not a reframing) | kept as the alternative to claim 4 | Under this reading the return rate is the "stopped flattering" 0/5 descriptive group, i.e. lower than the pooled 0.22–0.27; it pushes P(d) up, not down, so it is inside the interval on (d) rather than a separate route |

## 5. Independent Estimates
- base_rate_estimate: P(d) = 0.75, vector (a 0.07, b 0.11, c 0.07, d 0.75). One-quarter-gap return rate 4/18 = 0.22 (All), 4/16 = 0.25 (W1), 4/15 = 0.27 (W2) on the partially recoded matrix (claim 5); RNPL-specific completed trials n = 0, so the pooled rate is a descriptive analogue rather than a frequency of this event; regime-conditioned toward 0.25 (the bundle sits between the "stopped flattering" 0/5 group and the other 4/13). Conditional split of the quantified mass a 0.28 / b 0.44 / c 0.28 from claims 11–12 with the RNPL-alone branch pulling (c) up
- decomposition_estimate: P(quantified) = 0.284, P(d) = 0.716, vector (a 0.069, b 0.114, c 0.101, d 0.716). Print-state mixture on the R01/R02 states (claim 13): P(≥10.0%) 0.42 × P(quantify | strong) 0.18 + P(9.0–9.99%) 0.233 × 0.30 + P(<9.0%) 0.347 × 0.40 = 0.076 + 0.070 + 0.139; state-specific splits of the quantified mass a/b/c = 0.45/0.45/0.10 (strong: a positive bundle figure), 0.30/0.45/0.25 (middle), 0.10/0.35/0.55 (weak: the lap/drag reading of convention 2 and the RNPL-alone branch dominate). On the team normal alone the same model gives (0.068, 0.117, 0.107, 0.707); on rev-1's blended states (0.072, 0.114, 0.092, 0.722) (`c05_state_decomposition_v2.csv`). The conditional quantification probabilities (0.18/0.30/0.40) and the splits are judgments, labelled as such
- anchor_estimate: none available. No market or consensus exists on the disclosure (claim 15); the only adjacent price is Kalshi's nights ladder (claim 14), reported as a sensitivity and not used in the headline; the team's pre-registered card (claim 16) treats "qualitative update only" as the modal outcome without a probability
- anchor_value: n/a (NO_EXTERNAL_ANCHOR; Kalshi P(3Q26 nights > 148m) = 0.525 at 2026-09-17T02:53:51Z is adjacent only). The three-estimate requirement of the skill is therefore unmet: two internal estimates and no external anchor
- final_estimate: a 0.07, b 0.11, c 0.10, d 0.72
- final_minus_anchor: n/a. Base rate and decomposition agree within 3.5 points on P(d) and share the ledger and the 2Q26 silence, so the agreement is partly by construction; the print-state weights and the state-specific splits are the only inputs the base rate does not use. Audit A04 reached (0.10, 0.14, 0.08, 0.68) with team-normal states and higher conditionals (0.20/0.30/0.45); the largest gap (4 points on (d)) is the conditional-quantification judgment in the strong state (0.18 here vs 0.20) and the flat split; no option differs by more than 4 points

## 6. Final Numbers
| Option | Probability |
|---|---|
| (a) quantified ≥2.5 pts nights (≥3.5 GBV) | 0.07 |
| (b) quantified 1.5 to <2.5 pts (2.0–<3.5 GBV) | 0.11 |
| (c) quantified <1.5 pts (<2.0 GBV), incl. a quantified lap or cancellation drag for 3Q26 and an RNPL-alone figure | 0.10 |
| (d) not quantified in points | 0.72 |
Sum 1.00. P(any quantification) = 0.28. No option is at or below 2%, so the extreme-probability gate is not triggered; (c) rises from 0.07 to 0.10 because it now carries three distinct routes (a quantified lap or drag in a weak print; an RNPL-alone figure, which the mechanical branch puts below 1.7 points; a small bundle figure).
Tail-trade note: reallocating to (a 0.08, b 0.12, c 0.11, d 0.69) costs ln(0.69/0.72) = −0.043 in realized log score if (d) resolves (about −0.03 in expectation across outcomes at these probabilities) and caps the loss if any quantified bucket resolves; the vector above is the calibrated one, the 0.69 variant is the defensive one.
Coherence: the quantified-lap portion of (c) (about 0.06) is a subset of C07 = Yes (0.27, revision 2) by construction.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| The 2Q26 drop was an active reframing (return rate 0.22–0.27) | If incidental and the figure is routine (return rate near the 0.71–0.82 continuation for still-relevant metrics): P(d) 0.45; a 0.16, b 0.24, c 0.15 |
| Print-state weights (R01/R02: 0.42 / 0.233 / 0.347) | Team normal alone: (0.07, 0.12, 0.11, 0.70). Kalshi ladder alone (P(≥10.8%) 0.525 ⇒ states about 0.55 / 0.20 / 0.25): (0.08, 0.11, 0.08, 0.73). Nights print ≥10.6% (acceleration, realized): (0.08, 0.08, 0.02, 0.82). Nights ≤8.5% (realized): (0.04, 0.14, 0.22, 0.60) |
| Convention 2 (prior-year comp figure = d; 3Q26 lap drag = c) | If a resolver counts any prior-year comp figure as a 3Q26 quantification under (c): (0.07, 0.11, 0.16, 0.66) |
| Conditional quantification (0.18 / 0.30 / 0.40 by state) | Audit's (0.20 / 0.30 / 0.45): (0.074, 0.124, 0.112, 0.69). Rev-1's (0.15 / 0.28 / 0.42) with a flat 0.30/0.45/0.25 split: (0.08, 0.12, 0.07, 0.73) |
| Split of the quantified mass (state-specific) | If management rounds up to "approximately 3 points" again in any state (mechanical high end 2.9–3.1, claim 11): (0.13, 0.07, 0.08, 0.72) |
| July eligibility expansion small (+0.1 to +0.3) | If the expansion is worth 1 point or more and management wants credit for it: P(quantified) 0.36, (0.13, 0.13, 0.10, 0.64) |
| Cancellation-drag slice partly inside the fitted baseline | If the drag is fully additional (net 1.88–2.91 taken literally), the bundle central falls to about 2.3, moving 0.02 from (a) to (b): (0.05, 0.13, 0.10, 0.72) |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-17 to 2026-10-30 | Airbnb IR: 3Q26 results date announcement (expected mid-October); any newsroom RNPL post | Confirm 5 Nov; a newsroom post quantifying RNPL's contribution or a new eligibility expansion raises P(quantified) by about 5 points |
| 2026-09-30 | September Inside Airbnb dumps; R01/R02 re-centred | Recompute the state mixture with the revised R01/R02 states (`c05_state_decomposition_v2.csv` inputs); each +0.5pt on the nights centre moves about 0.02 from (c) to (d) |
| 2026-10-13 | Single-fee migration deadline (EEA/CH) per host notices (unverified in repo, RED_TEAM §7) | No direct effect; a management statement on fee-migration completion in the letter makes a fee-leg quantification slightly likelier (+2 points to a/b) |
| 2026-10-26 to 2026-11-04 | Sell-side previews; any Airbnb conference appearance | If a preview says the company will "size the RNPL lap", +5 points to the quantified mass (mostly (c)); if Mertz appears and declines to size RNPL, −3 points |
| 2026-11-04 | Freeze the print-state weights: final R01/R02 values | Recompute the decomposition; Kalshi remains a sensitivity |
| 2026-11-05 after close | 3Q26 letter, 10-Q, press release; call 4:30pm ET | Resolve: read the letter first (governs), then the call; classify per conventions 1–4; if the letter has a points figure, resolve immediately; record whether the figure is bundle or RNPL-alone |
| 2026-11-05 to 2026-11-06 | Post-call | If a quantified lap drag is stated, record which convention the resolver applied, for C07 coherence (C07's table now counts it as Yes) |

## 9. Audit trail (revision 2)
Rev-1 datasets (`metric_persistence_matrix_4Q20-2Q26.csv`, `metric_gap_events.csv`, `bundle_3q26_mechanical_contribution.csv`, `kalshi_q3_nights_implied_2026-09-17.csv`) are left in place as the audit trail; every number quoted above comes from the `_v2` files. The audit's reproduction script is saved as `docs/pitch-forecasts/audits/A04-reproduce.py` and ran clean on `py -3.13` (output in the response).

## 10. Revision notes
| Change | Finding |
|---|---|
| Metadata: revision 2, revised 2026-09-17; audit and response paths added | — |
| Claim 5 rebuilt on the partially recoded matrix (three false-positive cells removed: 1Q25 and 3Q25 "cancellation rate" were analyst questions, 2Q26 Middle East was qualitative; Guest Favorites cumulative-nights row completed from the letters, five cells added); both windows published; metric count corrected to 16; metric-quarters flagged as non-independent; the 0/5 group labelled retrospective | A04-02, A04-03 |
| Claim 6 adds the RNPL-specific counts (2/4, continuation 1/2, completed return trials n = 0); the pooled rate is labelled a descriptive analogue; base rate labelled accordingly | A04-04 |
| Claim 10–11 and the bridge rebuilt with paired ex-NA endpoints (gross 2.81–3.06, net 1.88–2.91), a separate RNPL-only branch, the drag labelled a scenario slice possibly inside the fitted baseline, and "could truthfully state" replaced by "scenario-implied under these assumptions"; convention 4 added | A04-05, A04-06 |
| Print-state weights: headline on the run's R01/R02 states (0.42 / 0.233 / 0.347); team normal and Kalshi reported as sensitivities; the rev-1 undocumented blend withdrawn; Kalshi claim now says it is not used in the headline | A04-10 |
| Claim 14: Kalshi fixed-point volume / OI / 24h / updated_time parsed and saved (`kalshi_q3_nights_implied_v2_2026-09-17.csv`); the Feb file identified as an FY2026 annual market | A04-11 |
| Claim 4 relabelled as an inference (reframing vs stopped-flattering), with the alternative priced in §4 and §7; §5 states plainly that the three-estimate requirement is unmet | A04-13 |
| §7 sensitivity vectors all fully specified and normalized | A04-16 |
| §6 tail-trade note corrected: ln(0.69/0.72) = −0.043 realized if (d), not "about −0.01"; expected-score comparison stated | A04-17 |
| Claims 15, 17, 21 reworded to "no relevant result found in the searches recorded"; no snapshots claimed | A04-18 |
| Final vector (0.08, 0.12, 0.07, 0.73) → (0.07, 0.11, 0.10, 0.72): (c) up for the quantified-lap route now shared with C07 and the RNPL-alone branch; (d) down 1 point on the recoded return rate and the state weights | A04-01, A04-05/06, A04-10 |
