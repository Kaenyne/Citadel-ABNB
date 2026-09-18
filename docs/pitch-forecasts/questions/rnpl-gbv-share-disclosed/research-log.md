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
- revision: 2
- revised: 2026-09-17
- agent: fable
- batch: A04 (shared research with C05 and C07; the full query log is repeated here)
- audit: `docs/pitch-forecasts/audits/A04-research-audit.md` (Astra); response `docs/pitch-forecasts/audits/A04-audit-response.md`

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
| 4 | Rollout timing: US from the beginning of 3Q25 (US guests, domestic, flexible/moderate policies); global 17 Feb 2026 with UK 18 Feb, AU 23 Feb, APAC 23 Feb, CA 4 Mar; BRL, INR, TRY payers excluded (D025–D029). So 1Q26's "roughly 20%" had only 5–6 of 13 weeks of ex-US availability and 2Q26 was the first full global quarter, yet the disclosed share moved only from "roughly 20%" to "over 20%": the one observed increment, 1Q26→2Q26, bounds the residual ramp (share model v2 ties the Q3 ramp to a fraction of that increment) | data/processed/overnight2/D/rnpl_statement_ledger.csv; research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md §1.2 | 2026-09-11 | 2026-09-17 | yes |
| 5 | Take-up among the offered/eligible is high: "About 70% of people that we offer ... take us up" (3Q25 call, D005: people offered RNPL, US); "over 70% adoption by eligible bookings" (4Q25 letter, D022: eligible bookings, global GBV basis); "the U.S. we are seeing the highest level of adoption, but the other markets are not far behind" (D036). These are different denominators and geographies and do not establish saturation; further share growth can come from eligibility (policy mix, booking types), from ex-US adoption catching up, or from both | ledger D005, D022, D036 | 2026-05-07 | 2026-09-17 | yes |
| 6 | Balance-sheet solve on unearned fees alone puts the unpaid RNPL share of the backlog at 15.4% (B = 1.00, no longer-dated book) to 23.1% (B = 1.10) at 30 Jun 2026 on the note baseline. It is a consistency check on the stock; the source audit leaves unpaid share and book length inseparable, so it does **not** identify or bound the quarterly booking-flow share and is not used as a constraint in the share model (revision 2) | data/processed/rnpl_short_audit/verify_bs_uf_only_solve.csv; research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md; docs/rnpl-short-audit/04_balance-sheet-verification.md | 2026-09-11 | 2026-09-17 | no |
| 7 | Persistence base rate, revision 2 (partially recoded 16-metric matrix, see C05 claim 5): continuation All 93/113 = 0.82, W1 60/78 = 0.77, W2 40/56 = 0.71; metric-quarters are not independent decisions. Ramping metrics management is proud of are updated every quarter with a new number (app share 58 → 63 → 64%; single-fee listings "over a quarter" → "approximately half"; first-time bookers +8 → +10 → +11%; Guest Favorites cumulative nights every quarter from 1Q24 to 4Q25 except 4Q24). The directly comparable RNPL-share history is 1/1 (1Q26 → 2Q26) | datasets/persistence_rates_v2.csv; datasets/metric_persistence_matrix_v2_4Q20-2Q26.csv; data/raw/letters/1Q26, 2Q26; ledger D041, D047 | 2026-09-17 | 2026-09-17 | yes |
| 8 | Management's rounding vocabulary for shares: "roughly 20%", "over 20%", "over 70%", "over a quarter", "approximately half": milestones, not precise figures (D022, D031, D041, D043, D047). Used as an assumption in two places: "over 20%" is read as 20.5–23.5 (at 23.5+ the vocabulary would be "nearly a quarter"), and a reading at or above 25% is assumed likelier to be stated than a 22% reading (level-dependent disclosure gate 0.75 / 0.68 / 0.55) | data/processed/overnight2/D/rnpl_statement_ledger.csv | 2026-09-11 | 2026-09-17 | yes |
| 9 | (Revision 2, corrected) Q3 is **not** Airbnb's lowest-GBV quarter: 2023–25 means Q1 $22.6bn, Q2 $21.3bn, Q3 $20.4bn, Q4 $17.8bn; Q4 is lower in every year. The Q3 take rate of 18.3% reflects peak check-ins (recognized revenue) over that quarter's bookings, not a short booking lead time, and the mechanics note says lead time is undisclosed. RNPL's payment rule ("shortly before the end of the listing's free cancellation period", D002) means a booking inside the free-cancellation window has little to defer, but no evidence puts a sign or size on a Q3 mix effect; rev-1's directional U(−2, 0) penalty is withdrawn and replaced by symmetric noise U(−1, +1) | data/processed/abnb_driver_history_quarterly.csv; docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §1.3–1.4; https://news.airbnb.com/reserve-now-pay-later/ (D002) | 2026-09-11 | 2026-09-17 | yes |
| 10 | Share-ramp Monte Carlo v2 (this log; every input an assumption, labelled in the script): 1Q26 true share U(19,21); 1Q26→2Q26 increment U(0.5,3.5) with 2Q26 constrained to [20.5, 23.5]; Q3 residual ramp = U(0,0.5) × that increment; July expansion 0.75·Exp(mean 1.4) + 0.25·Exp(mean 3.5), capped 8; mix noise U(−1,+1). P(true share rounds to ≥25) 0.389, P(21–24) 0.606, P(≤20) 0.005 (N = 200k, seed 7). Variants: no July expansion 0.044 / 0.921 / 0.035; Exp(1.4) only 0.321; Exp(3.5) only 0.593; no residual ramp 0.287; full ramp 0.493; rev-1 penalty restored 0.234; "over 20%" capped at 22.5: 0.286. Audit's no-season benchmark on rev-1 inputs 0.400 / 0.599 / 0.000; rev-1 as published 0.216 / 0.769 / 0.015 (withdrawn) | datasets/share_ramp_model_v2_2026-09-17.csv (script .py alongside; rev-1 script and CSV kept) | 2026-09-17 | 2026-09-17 | yes |
| 11 | Pre-registered team card: "≥25% with nights ≥10% weakens the drag hypothesis; flat or down vs 2Q26 while nights decelerate supports; 21–24% inconclusive" | data/processed/overnight2/D/D1_prereg_thresholds.csv row 6 | 2026-09-11 | 2026-09-17 | no |
| 12 | No market on the disclosure was found in the searches recorded (Polymarket public-search; Kalshi open-events scan); Kalshi's Q3 nights ladder (P(>148m) 0.525; P(>146m) 0.645; `volume_fp` 3,237 contracts, `open_interest_fp` 2,178, `volume_24h_fp` 0, `updated_time` 2026-08-04 batch stamp) is the only adjacent price; the companion Kalshi file is an FY2026 annual nights ladder | sources/kalshi_KXABNB-26NOVNEB_20260917T025351Z.json; datasets/kalshi_q3_nights_implied_v2_2026-09-17.csv; sources/polymarket_public-search_airbnb_20260917T025229Z.json | 2026-09-17 | 2026-09-17 | yes |
| 13 | Management's 2Q26 framing shifted to "no single product"; the share was one of only two product updates it chose to give, so the share is the RNPL number most likely to survive the reframing | data/raw/transcripts/web/2Q26.html (Mertz: "we wanted to provide an update on two") | 2026-08-06 | 2026-09-17 | yes |
| 14 | Third-party commentary (rentalscaleup 3 Jul 2026; staystra 29 Apr 2026) repeats "roughly 20%" and the 16 to 17% cancellation rate; nothing in the pages fetched suggests a share step-up or a terms change; Chesky's 8 Sep Communacopia transcript (fetched) has no RNPL mention | https://www.rentalscaleup.com/insurance-pay-later-cancellation-fees-what-airbnb-now-earns-on-top-of-your-stay-rates/ ; https://staystra.com/airbnb-reserve-now-pay-later-hosts-cancellation-policy-2026/ ; https://stockanalysis.com/stocks/abnb/transcripts/739626-goldman-sachs-communacopia-technology-conference-2026/ | 2026-07-03 | 2026-09-17 | no |
| 15 | Final 72-hour recency check (2026-09-17): no relevant result found in the searches recorded (queries 17, 29) for RNPL news, a terms change or a management comment this week; no result snapshots saved | WebSearch queries 17, 29 | 2026-09-17 | 2026-09-17 | no |
| 16 | (Revision 2) Print-state weights from the run's R01/R02: P(nights ≥10.0%) 0.42, P(≥10.6%) 0.32; used only in the strong-print sensitivity of the disclosure gate | docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/forecasts/2026-09-17-forecast.json; risk-q3-nights-accelerates/forecasts/2026-09-17-forecast.json | 2026-09-17 | 2026-09-17 | no |

## 2. Query Log
1. [repo] pandas dump of data/processed/overnight2/D/rnpl_statement_ledger.csv (60 rows)
2. [repo] data/processed/overnight2/D/D1_prereg_thresholds.csv
3. [repo] regex extraction of RNPL/cancellation passages from the 3Q25–2Q26 letters and call mirrors, saved to sources/letters_calls_3Q25-2Q26_rnpl_passages.txt
4. [repo] same for data/raw/regulatory/quantification/abnb_2026q2_10q.html, saved to sources/10q_2Q26_rnpl_passages.txt
5. [repo] quantified-driver regex scan of all 23 letters and calls
6. [repo] metric-persistence matrix (16 metrics × 23 prints), saved to datasets/metric_persistence_matrix_4Q20-2Q26.csv and metric_gap_events.csv
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
30. [computed] datasets/share_ramp_model_2026-09-17.py → .csv (rev-1 Monte Carlo, withdrawn)
31. (rev 2) [repo] data/processed/abnb_driver_history_quarterly.csv, 2023–25 GBV and take-rate means by fiscal quarter (audit A04-07 check: Q4 is the lowest-GBV quarter)
32. (rev 2) [repo] docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §1.3–1.4 (take-rate timing ratio; lead time undisclosed)
33. (rev 2) [repo] data/processed/rnpl_short_audit/verify_bs_uf_only_solve.csv, 2Q26 rows at B = 1.00 / 1.05 / 1.10 on every normalization (15.4 / 19.4 / 23.1% on the note baseline)
34. (rev 2) [repo] letters grep for Guest Favorites cumulative nights (row recode); re-read of the 1Q25/3Q25 call "cancellation rate" hits (analyst questions) and the 2Q26 Middle East passage (qualitative)
35. (rev 2) [computed] datasets/metric_persistence_matrix_v2_recode.py (in the C05 folder; outputs copied here) → persistence_rates_v2.csv, metric_gap_events_v2.csv
36. (rev 2) [computed] datasets/share_ramp_model_v2_2026-09-17.py → .csv (claim 10)
37. (rev 2) [computed] docs/pitch-forecasts/audits/A04-response-datasets.py → kalshi_q3_nights_implied_v2_2026-09-17.csv
38. (rev 2) [repo] R01/R02 forecast JSONs (claim 16)

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Reserve Now Pay Later, RNPL, GBV share, 3Q26 earnings call, 5 November 2026

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| The share reaches ≥25% because the July eligibility expansion is material and/or ex-US adoption keeps ramping | kept as (a), now 0.25 | Every driver is unquantified by management (claims 3, 5); the v2 model puts the true share at ≥24.5 with probability 0.39 (0.29–0.59 across the labelled variants, claim 10); rev-1's 0.22 rested on a directional Q3 penalty with no evidence (claim 9) |
| Management drops the share entirely now that "no single product" is the message | kept as (d) 0.29 | Continuation 0.71–0.82 across windows (claim 7) but the venue already fell from letter to call (claim 2) and the number barely moved; a non-milestone number is the kind Airbnb omits (claim 8) |
| Management gives an annual/cumulative share ("over 20% year to date") rather than a Q3 share | kept inside (d) | Convention 3: a non-3Q26 period resolves (d); about 0.03 inside (d) |
| The share is disclosed as nights share or bookings share only | discarded as a route | Airbnb has always used the GBV basis for this metric (claims 1, 2); fine print sends nights/bookings-only to (d); about 0.02 inside (d) |
| The share falls below 20% (seasonal or cancellation attrition of the flow) | kept inside (c), small | P(true ≤20) 0.005 in the v2 base, 0.035 with no July expansion (claim 10); a disclosed decline is unlikely to be volunteered; if true, more likely (d) |
| A Q3 share is answered only in Q&A | kept | Counts under convention 1; analysts asked zero RNPL questions in 2Q26, so P(asked) about 0.5; adds little because management volunteers the number when it flatters |
| The balance-sheet backlog solve caps the flow share near 20–21% | discarded (revision 2) | The solve identifies a stock at an assumed book length, not the quarterly flow share (claim 6, audit A04-09) |
| Q3 lead-time seasonality depresses the RNPL share | discarded as a directional input (revision 2) | Q3 is not the lowest-GBV quarter and lead time is undisclosed (claim 9); kept only as symmetric noise |

## 5. Independent Estimates
- base_rate_estimate: a 0.25, b 0.22, c 0.28, d 0.26. P(disclosed) 0.74 (the W1 continuation 0.77 and W2 0.71 bracket it; claim 7) × the v2 true-share split (claim 10: 0.389 / 0.606 / 0.005) × language mapping (claim 8: ≥25 → (a) 0.85 / (b) 0.05 / (c) 0.10; 21–24 → (b) 0.45 / (c) 0.55; ≤20 → (c)). **Not independent of the decomposition**: the a/b/c split comes from the same share model and wording map; only the disclosure gate is from the persistence data
- decomposition_estimate: a 0.248, b 0.200, c 0.259, d 0.293. Level-dependent disclosure gate (0.75 | true ≥25; 0.68 | 21–24; 0.55 | ≤20; overall about 0.70, the milestone-habit assumption of claim 8, inside the W1–W2 continuation range once the venue downgrade and the "no single product" reframing are allowed for) × the same true-share split and language mapping. With a flat 0.70 gate: (0.232, 0.205, 0.264, 0.300)
- anchor_estimate: none available. No market or consensus on any RNPL disclosure (claim 12); the team card (claim 11) gives thresholds, not probabilities
- anchor_value: n/a (NO_EXTERNAL_ANCHOR; Kalshi P(3Q26 nights > 148m) = 0.525 at 2026-09-17T02:53:51Z is adjacent only). The skill's three-independent-estimates requirement is unmet: the two internal estimates share the share model, and there is no external anchor
- final_estimate: a 0.25, b 0.20, c 0.26, d 0.29
- final_minus_anchor: n/a. The final adopts the decomposition (level-dependent gate) with (c) and (d) rounded; the base rate differs by 3–4 points on (d) only because of the flat 0.74 gate. Audit A04's reassessment (0.25, 0.19, 0.26, 0.30), built on its no-season benchmark of rev-1's inputs, is within 1 point on every option: the v2 model's wider starting share, ramp tied to the observed Q2 step and expansion mixture net out against each other and land at P(true ≥25) 0.39 vs the benchmark's 0.40

## 6. Final Numbers
| Option | Probability |
|---|---|
| (a) ≥25% | 0.25 |
| (b) 21–24% | 0.20 |
| (c) "over 20%" repeated, "roughly 20%", or ≤20% | 0.26 |
| (d) not disclosed | 0.29 |
Sum 1.00. P(disclosed) = 0.71. Extreme-probability gate not triggered (no option ≤2%).
Coherence for R03: P(C06 = a) = 0.25 is the cap on P(R03 = Yes); R03's log records joint ≈ 0.51 × P(a), so R03 recomputes to about 0.13 (from 0.07) if its own model is left unchanged; that recompute belongs to batch A09.
What the number says: a disclosed Q3 share at or above a quarter of GBV is a one-in-four event, a repeat of "over 20%" (or lower) is a one-in-four event, silence is a bit less than one-in-three; the true share crossing 24.5 is close to a coin flip under assumptions the disclosure record cannot pin, which is why (a) and (c) sit close together.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Disclosure gate about 0.70 (level-dependent) | Standing-KPI treatment (0.90 flat): a 0.30, b 0.26, c 0.34, d 0.10. Reframing removes RNPL numbers (0.50 flat): a 0.16, b 0.15, c 0.19, d 0.50. W2 continuation (0.67 flat): a 0.22, b 0.20, c 0.25, d 0.33 |
| July expansion 0.75·Exp(1.4) + 0.25·Exp(3.5) | Large only (Exp 3.5): P(true ≥25) 0.593, giving a 0.38, b 0.15, c 0.20, d 0.27. Small only (Exp 1.4): 0.321, giving a 0.21, b 0.22, c 0.28, d 0.29. No expansion effect at all: 0.044, giving a 0.03, b 0.28, c 0.37, d 0.32 |
| Residual ex-US ramp = U(0, 0.5) × the Q2 step | No residual ramp: a 0.18, b 0.23, c 0.29, d 0.30. Full ramp (0–100% of the Q2 step): a 0.31, b 0.17, c 0.23, d 0.29 |
| "Over 20%" read as 20.5–23.5 | Read narrowly as 20.5–22.5: a 0.18, b 0.23, c 0.29, d 0.30 |
| Symmetric Q3 mix noise U(−1, +1) | Rev-1's directional U(−2, 0) restored: a 0.15, b 0.23, c 0.31, d 0.31 (the withdrawn vector, for reference) |
| Language mapping: 21–24 true is stated as "over 20%" 55% of the time | If management gives a precise figure when it moves ("23%"; mapping 0.65/0.35): a 0.25, b 0.28, c 0.18, d 0.29 |
| Nights print ≥10.6% (strong quarter, management eager to credit RNPL; R02 0.32) | Gate +0.10 across levels: a 0.28, b 0.23, c 0.29, d 0.20 |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-17 to 2026-10-31 | Airbnb newsroom / help-centre changes to RNPL eligibility (policy types, stay lengths, hotels/experiences) | Any named expansion of eligible bookings: move to the large-expansion row (a 0.38); a restriction: cut (a) to 0.15 or below |
| 2026-10-13 | EEA/CH single-fee deadline (unverified date) | No effect on this question |
| 2026-10-26 to 2026-11-04 | Sell-side previews naming an RNPL share expectation | If any preview models ≥25%, +3 points to (a) from (c); record the vendor and date |
| 2026-11-04 | Final R01/R02 print-state values | If P(≥10.6%) rises above 0.45, apply the strong-quarter row (d 0.20) |
| 2026-11-05 after close | 3Q26 letter (governs), press release, 10-Q, call 4:30pm ET | Resolve per conventions 1–3; if the letter gives the share, ignore the call; if only the call, resolve on the call wording; record the (share, nights) pair on the pre-registered card (claim 11) |
| 2026-11-05 | Cross-check with C05/C07 outcomes and R03 | If a bundle points figure appears without a share, resolve (d) here regardless; hand the resolved (a) to R03 |

## 9. Audit trail (revision 2)
Rev-1 datasets (`share_ramp_model_2026-09-17.py/.csv`, `metric_persistence_matrix_4Q20-2Q26.csv`, `metric_gap_events.csv`, `kalshi_q3_nights_implied_2026-09-17.csv`) are left in place; every number above comes from the `_v2` files. The audit's reproduction script is saved as `docs/pitch-forecasts/audits/A04-reproduce.py` and ran clean on `py -3.13`.

## 10. Revision notes
| Change | Finding |
|---|---|
| Metadata: revision 2, revised 2026-09-17; audit and response paths added | — |
| Claim 7 rebuilt on the partially recoded matrix with both windows (0.82 / 0.77 / 0.71), non-independence flagged, RNPL-share history stated as 1/1 | A04-02, A04-03, A04-04 |
| Claim 9 corrected: Q3 is not the lowest-GBV quarter (Q4 is; 2023–25 means); take rate reflects check-in timing; lead time undisclosed; directional seasonal penalty withdrawn, replaced by symmetric U(−1, +1) noise | A04-07 |
| Claim 5 rewritten: 70% adoption figures have different denominators/geographies and do not establish saturation; claim 10 / share model v2: every input labelled an assumption; "over 20%" widened to 20.5–23.5; ramp tied to the observed 1Q26→2Q26 increment; July expansion as a mixture with a large-expansion component; large-expansion sensitivity preserved (0.59 true ≥25) | A04-08 |
| Claim 6 downgraded to a consistency check on the stock; removed as a constraint on the flow share; load-bearing flag set to no | A04-09 |
| Claim 12 / 16: Kalshi fixed-point fields parsed and saved; Feb file identified as FY2026 annual; R01/R02 states cited for the strong-print sensitivity only | A04-10, A04-11 |
| §5 states plainly that the base rate and decomposition share the share model and that no external anchor exists; the three-estimate requirement is unmet | A04-13 |
| §5 no longer claims a 3:1 blend: the final adopts the decomposition with rounding; the rev-1 "+1 / −1 nudge" is gone | A04-15 |
| §7 every vector fully specified and normalized; the strong-print row now sums to 1 | A04-16 |
| Claims 12, 14, 15 reworded to "no relevant result found in the searches recorded" | A04-18 |
| Final vector (0.15, 0.24, 0.31, 0.30) → (0.25, 0.20, 0.26, 0.29): (a) +10 on the withdrawn penalty and the wider inputs; (b) −4 and (c) −5 as the mass moved up; (d) −1 on the level-dependent gate. R03 implied recompute noted in §6 | A04-07, A04-08 |
