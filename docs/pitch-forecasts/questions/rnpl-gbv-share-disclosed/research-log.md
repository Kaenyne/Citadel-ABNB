# RESEARCH LOG

## 0. Metadata
- question_name: rnpl-gbv-share-disclosed
- question_url: n/a (internal pitch-forecast question C06, `docs/pitch-forecasts/QUESTIONS.md`)
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
- batch: A04 (shared research with C05 and C07; the full query log is repeated here)

## 0b. Question (verbatim)
### Title
What RNPL share of 3Q26 GBV will Airbnb disclose at the 5 Nov print?
### Resolution Criteria
**Type.** Multiple choice.
**Options.** (a) ≥25%; (b) 21–24% (incl. "nearly a quarter", "mid-twenties" if the midpoint is <25); (c) "over 20%" repeated, "roughly 20%", or ≤20%; (d) not disclosed.
### Fine Print
Nights-share or bookings-share disclosures resolve as (d) unless a GBV share is also given. Resolution date 5 Nov 2026.

Conventions adopted: (1) a share stated on the call counts when the letter is silent (registry convention: "not stated" resolves only where neither states the item); (2) "a quarter of GBV" / "approximately 25%" / "25%" resolves (a); "nearly a quarter", "almost 25%", "low-to-mid twenties", "23%" resolves (b); "over 20%", "more than 20%", "roughly 20%", "about a fifth" resolves (c); (3) a share stated for a period other than 3Q26 ("year to date", "in October") does not resolve a–c unless a 3Q26 share is also given.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | 1Q26 letter: "in Q1, roughly 20% of global GBV came from Reserve Now, Pay Later bookings" (D031); 1Q26 call (Chesky) repeats "roughly 20% of global GBV" | data/raw/letters/1Q26_d23351dex991.htm; data/raw/transcripts/web/1Q26.html | 2026-05-07 | 2026-09-17 | yes |
| 2 | 2Q26 call (Mertz): "Specifically in Q2, over 20% of our total GBV was booked using this flexible payment option." (D043). The 2Q26 letter carries no share (it says RNPL is available "on more listings in more countries"): venue downgraded from letter to call | data/raw/transcripts/web/2Q26.html; data/raw/letters/2Q26_d70413dex991.htm | 2026-08-06 | 2026-09-17 | yes |
| 3 | 2Q26 call: "in July, we expanded the types of bookings eligible for Reserve Now, Pay Later" (D044): types unnamed, size unquantified; fresh eligibility inside 3Q26 | data/raw/transcripts/web/2Q26.html | 2026-08-06 | 2026-09-17 | yes |
| 4 | Rollout timing: US from the beginning of 3Q25 (US guests, domestic, flexible/moderate policies); global 17 Feb 2026 with UK 18 Feb, AU 23 Feb, APAC 23 Feb, CA 4 Mar; BRL, INR, TRY payers excluded (D025–D029). So 1Q26's "roughly 20%" had only 5–6 of 13 weeks of ex-US availability and 2Q26 was the first full global quarter, yet the disclosed share moved only from "roughly 20%" to "over 20%" | data/processed/overnight2/D/rnpl_statement_ledger.csv; research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md §1.2 | 2026-09-11 | 2026-09-17 | yes |
| 5 | Take-up is already saturated among the eligible: "About 70% of people that we offer ... take us up" (3Q25 call, D005); "over 70% adoption by eligible bookings" on global GBV in 4Q25 (D022); "the U.S. we are seeing the highest level of adoption, but the other markets are not far behind" (D036). Further share growth needs eligibility growth (policy mix, booking types), not adoption | ledger D005, D022, D036 | 2026-05-07 | 2026-09-17 | yes |
| 6 | Balance-sheet solve on unearned fees alone puts the unpaid RNPL share of the backlog at 14–15% (book no longer-dated) to 22–23% (10% longer-dated) at 30 Jun 2026, consistent with a 20–21% flow share; no evidence of a share materially above the disclosed figure | research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md (STATUS block, bottom line 3); docs/rnpl-short-audit/04_balance-sheet-verification.md | 2026-09-11 | 2026-09-17 | yes |
| 7 | Persistence base rate: a quantified metric disclosed at t is disclosed at t+1 in 91/111 = 0.82 of metric-quarters (17 metrics, 4Q20–2Q26); ramping metrics management is proud of are updated every quarter with a new number (app share 58 → 63 → 64%; single-fee listings "over a quarter" → "approximately half"; first-time bookers +8 → +10 → +11%) | datasets/metric_persistence_matrix_4Q20-2Q26.csv; data/raw/letters/1Q26, 2Q26; ledger D041, D047 | 2026-09-17 | 2026-09-17 | yes |
| 8 | Management's rounding vocabulary for shares: "roughly 20%", "over 20%", "over 70%", "over a quarter", "approximately half": milestones, not precise figures (D022, D031, D041, D043, D047) | data/processed/overnight2/D/rnpl_statement_ledger.csv | 2026-09-11 | 2026-09-17 | yes |
| 9 | Q3 is Airbnb's lowest-GBV, shortest-lead-time booking quarter (quarterly take rate 18.3% in Q3 vs 9.2% in Q1 because Q3 bookings are "shoulder-season, last-minute"); RNPL requires payment "shortly before the end of the listing's free cancellation period", so bookings made inside or near the free-cancellation window have little or no deferral to offer | docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §1.3; https://news.airbnb.com/reserve-now-pay-later/ (D002) | 2026-09-11 | 2026-09-17 | yes |
| 10 | Share-ramp Monte Carlo (this log): 2Q26 true share U(21,23), ex-US ramp U(0,2), July expansion Exp(mean 1.4) capped at 6, Q3 lead-time seasonal U(−2,0): P(true share rounds to ≥25) 0.216, P(21–24) 0.769, P(≤20) 0.015 (N=200k, seed 7). Variants: July expansion Exp(mean 4) gives 0.553/0.441/0.006; no seasonal drag gives 0.401/0.599/0.000 | datasets/share_ramp_model_2026-09-17.csv (script .py alongside; variants reproduced by changing exp_mean and seas) | 2026-09-17 | 2026-09-17 | yes |
| 11 | Pre-registered team card: "≥25% with nights ≥10% weakens the drag hypothesis; flat or down vs 2Q26 while nights decelerate supports; 21–24% inconclusive" | data/processed/overnight2/D/D1_prereg_thresholds.csv row 6 | 2026-09-11 | 2026-09-17 | no |
| 12 | No market exists on the disclosure; Kalshi's Q3 nights ladder (P(>148m) 0.525; P(>146m) 0.645; thin, null volume) is the only adjacent price | sources/kalshi_KXABNB-26NOVNEB_20260917T025351Z.json; sources/polymarket_public-search_airbnb_20260917T025229Z.json | 2026-09-17 | 2026-09-17 | yes |
| 13 | Management's 2Q26 framing shifted to "no single product"; the share was one of only two product updates it chose to give, so the share is the RNPL number most likely to survive the reframing | data/raw/transcripts/web/2Q26.html (Mertz: "we wanted to provide an update on two") | 2026-08-06 | 2026-09-17 | yes |
| 14 | Third-party commentary (rentalscaleup 3 Jul 2026; staystra 29 Apr 2026) repeats "roughly 20%" and the 16 to 17% cancellation rate; nothing suggests a share step-up or a terms change through September; Chesky's 8 Sep Communacopia remarks did not mention RNPL | https://www.rentalscaleup.com/insurance-pay-later-cancellation-fees-what-airbnb-now-earns-on-top-of-your-stay-rates/ ; https://staystra.com/airbnb-reserve-now-pay-later-hosts-cancellation-policy-2026/ ; https://stockanalysis.com/stocks/abnb/transcripts/739626-goldman-sachs-communacopia-technology-conference-2026/ | 2026-07-03 | 2026-09-17 | no |
| 15 | Final 72-hour recency check (2026-09-17): no RNPL news, terms change or management comment this week | WebSearch queries 17, 29 | 2026-09-17 | 2026-09-17 | no |

## 2. Query Log
1. [repo] pandas dump of data/processed/overnight2/D/rnpl_statement_ledger.csv (60 rows)
2. [repo] data/processed/overnight2/D/D1_prereg_thresholds.csv
3. [repo] regex extraction of RNPL/cancellation passages from the 3Q25–2Q26 letters and call mirrors, saved to sources/letters_calls_3Q25-2Q26_rnpl_passages.txt
4. [repo] same for data/raw/regulatory/quantification/abnb_2026q2_10q.html, saved to sources/10q_2Q26_rnpl_passages.txt
5. [repo] quantified-driver regex scan of all 23 letters and calls
6. [repo] metric-persistence matrix (17 metrics × 23 prints), saved to datasets/metric_persistence_matrix_4Q20-2Q26.csv and metric_gap_events.csv
7. [repo] RNPL passages in abnb_2025_10k.json
8. [repo] data/processed/abnb_declined_to_quantify.csv
9. [SEC API] data.sec.gov/submissions/CIK0001559720.json
10. [Polymarket API] public-search?q=airbnb ; ?q=ABNB%20earnings (2026-09-17T02:52:29Z)
11. [Kalshi API] events?status=open (20 pages), then markets?event_ticker=KXABNB-26NOVNEB, KXABNBA-27FEBNEB (02:53:51Z)
12. [repo] analyst-question scan of 3Q25–2Q26 call Q&A for RNPL/cancellation asks
13. [repo] 2Q26 Middle East / World Cup passages
14. [SEC fetch] 3Q25 and 1Q26 10-Qs, raw grep for RNPL terms
15. [repo] research/notes/overnight/03_management-language-and-stock.md dropped-claims section
16. [repo] 02_guidance_ledger.csv scan for RNPL rows (none)
17. WebSearch: Airbnb news
18. WebSearch: Airbnb Reserve Now Pay Later September 2026
19. WebSearch: Airbnb Reserve Now Pay Later cancellations analyst Q3 2026
20. WebSearch: Airbnb third quarter 2026 results date November
21. WebFetch: news.airbnb.com/reserve-now-pay-later/
22. WebFetch: staystra.com RNPL hosts 2026 page
23. WebFetch: rentalscaleup.com insurance-pay-later page
24. WebFetch: finance.yahoo.com Q3 preview (2025 vintage: stale, zero weight)
25. [repo] grep q3nowcast notes and G/intra_quarter_commentary.csv for conference RNPL mentions
26. WebSearch: Airbnb Mertz conference September 2026 "Reserve Now, Pay Later"
27. [repo] grep 1Q26/2Q26 letter and call for "extended cancellation" (none)
28. WebFetch: stockanalysis.com Communacopia 8 Sep 2026 transcript (no RNPL mention)
29. WebSearch: Airbnb "Reserve Now, Pay Later" news this week (final 72-hour check; nothing new)
30. [computed] datasets/share_ramp_model_2026-09-17.py → .csv (Monte Carlo, claim 10)

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Reserve Now Pay Later, RNPL, GBV share, 3Q26 earnings call, 5 November 2026

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| The share jumps to ≥25% because the July eligibility expansion is large | kept as minority (a) | Adoption among the eligible is already about 70% (claim 5), the first full global quarter added only "over 20%" vs "roughly 20%" (claim 4), Q3 lead-time seasonality works against deferral (claim 9); expansion size unknown, modelled Exp(mean 1.4) |
| Management drops the share entirely now that "no single product" is the message | kept as (d) 0.30 | Continuation base rate 0.82 (claim 7) but the venue already fell from letter to call (claim 2) and the number barely moved; a non-milestone number is the kind Airbnb omits |
| Management gives an annual/cumulative share ("over 20% year to date") rather than a Q3 share | kept inside (d) | Convention 3: a non-3Q26 period resolves (d); about 0.03 inside (d) |
| The share is disclosed as nights share or bookings share only | discarded as a route | Airbnb has always used the GBV basis for this metric (claims 1, 2); fine print sends nights/bookings-only to (d); about 0.02 inside (d) |
| The share falls below 20% (seasonal or cancellation attrition of the flow) | kept inside (c) via 0.015 of true-share mass (claim 10) | A disclosed decline is unlikely to be volunteered; if true, more likely (d); the Monte Carlo's seasonal drag U(−2,0) is what carries this case |
| A Q3 share is answered only in Q&A | kept | Counts under convention 1; analysts asked zero RNPL questions in 2Q26, so P(asked) about 0.5; adds little because management volunteers the number when it flatters |

## 5. Independent Estimates
- base_rate_estimate: a 0.16, b 0.28, c 0.38, d 0.18. P(disclosed) 0.82 (claim 7) × true-share split (claim 10: 0.216 / 0.769 / 0.015) × language mapping (claim 8: ≥25 → (a) 0.9 else (c); 21–24 → (b) 0.45 / (c) 0.55; ≤20 → (c)); conditional on disclosure a 0.194, b 0.346, c 0.460
- decomposition_estimate: a 0.14, b 0.24, c 0.32, d 0.30. P(disclosed) 0.70 (0.82 continuation, cut for the letter-to-call downgrade, the "no single product" reframing and the milestone habit: a 22–23% reading may simply be omitted) × the same conditional split
- anchor_estimate: none available. No market or consensus on any RNPL disclosure (claim 12); the team card (claim 11) gives thresholds, not probabilities
- anchor_value: n/a (NO_EXTERNAL_ANCHOR; Kalshi P(3Q26 nights > 148m) = 0.525 at 2026-09-17T02:53:51Z is adjacent only)
- final_estimate: a 0.15, b 0.24, c 0.31, d 0.30
- final_minus_anchor: n/a. The two internal estimates differ by 12 points on (d); the difference is the disclosure-continuation adjustment for the venue downgrade and the milestone habit, which the pooled base rate cannot see; the decomposition is weighted about 3:1 because the 0.82 continuation pools metrics that were still moving with ones that were not. (a) is nudged +1 point above the decomposition and (c) −1 point for model uncertainty on the July expansion, the one input the Monte Carlo cannot pin (an Exp(mean 4) expansion more than doubles (a), claim 10)

## 6. Final Numbers
| Option | Probability |
|---|---|
| (a) ≥25% | 0.15 |
| (b) 21–24% | 0.24 |
| (c) "over 20%" repeated, "roughly 20%", or ≤20% | 0.31 |
| (d) not disclosed | 0.30 |
Sum 1.00. P(disclosed) = 0.70. Extreme-probability gate not triggered (no option ≤2%).
Coherence for R03: P(C06 = a) = 0.15 is the cap on P(R03 = Yes); with P(R01) about 0.4 and positive correlation (a big share and strong nights share the July-expansion cause), R03 should sit near 0.08–0.11.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| P(disclosed) 0.70 | If management treats the share as a standing KPI like app share (0.90): a 0.18, b 0.31, c 0.41, d 0.10. If the reframing removes RNPL numbers (0.50): a 0.10, b 0.17, c 0.23, d 0.50 |
| July expansion mean +1.4 pts of GBV share | If the expansion is large (mean +4, e.g. Firm-policy listings made eligible): P(true ≥25) 0.553, giving a 0.35, b 0.14, c 0.21, d 0.30 |
| Q3 lead-time seasonal drag U(−2,0) | If no seasonal effect: P(true ≥25) 0.401, giving a 0.25, b 0.19, c 0.26, d 0.30 |
| Language mapping: 21–24 true is stated as "over 20%" 55% of the time | If management gives a precise figure when it moves ("23%"; mapping 0.65/0.35): a 0.14, b 0.35, c 0.21, d 0.30 |
| Nights print ≥10.6% (strong quarter, management eager to credit RNPL) | P(disclosed) 0.80: a 0.16, b 0.28, c 0.37, d 0.20 |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-17 to 2026-10-31 | Airbnb newsroom / help-centre changes to RNPL eligibility (policy types, stay lengths, hotels/experiences) | Any named expansion of eligible bookings: raise (a) by up to 10 points from (b)/(c); a restriction: cut (a) to 0.10 or below |
| 2026-10-13 | EEA/CH single-fee deadline (unverified date) | No effect on this question |
| 2026-10-26 to 2026-11-04 | Sell-side previews naming an RNPL share expectation | If any preview models ≥25%, +3 points to (a); record the vendor and date |
| 2026-11-05 after close | 3Q26 letter (governs), press release, 10-Q, call 4:30pm ET | Resolve per conventions 1–3; if the letter gives the share, ignore the call; if only the call, resolve on the call wording |
| 2026-11-05 | Cross-check with C05/C07 outcomes | If a bundle points figure appears without a share, resolve (d) here regardless |
