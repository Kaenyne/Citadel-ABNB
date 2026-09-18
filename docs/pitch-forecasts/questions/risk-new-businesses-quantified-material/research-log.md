# RESEARCH LOG

## 0. Metadata
- question_name: risk-new-businesses-quantified-material
- question_url: n/a (internal pitch-forecast question R09, `docs/pitch-forecasts/QUESTIONS.md`)
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
- batch: A11 (with R06 and R08)
- audit: `docs/pitch-forecasts/audits/A11-research-audit.md` (independent Opus auditor standing in for Codex); response `docs/pitch-forecasts/audits/A11-audit-response.md`

## 0b. Question (verbatim)
### Title
By the Feb print, will management disclose that hotels, Experiences or Services together account for ≥3% of nights and seats booked, or ≥3% of GBV, or give a FY27 revenue figure for them of ≥$500M?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes on any of the three disclosures. Resolution ~11 Feb 2027.
### Fine Print
(none in the registry.) Conventions adopted here and forecast under:
1. Sources: the 3Q26 and 4Q26 letters and calls, the 3Q26 10-Q, and the FY26 10-K if filed on or before the Feb print date. (Revision 2, A11-10) Two of the last three 10-Ks filed on the print day (2026-02-12, 2025-02-13; the FY2023 10-K three days after, 2024-02-16), so the 10-K is a live venue for the Feb window. Conference remarks do not count.
2. The share must be of total Nights and Seats Booked or total GBV. A city- or market-level share ("over 10% of nights in New York") does not count. A share for one line alone (e.g. hotels 4% of nights) counts, since the three lines "together" are then ≥3%. (Revision 2, A11-01) The resolver may also **add** separately disclosed shares of the same denominator from the same reporting window (e.g. "hotels about 2% of nights" in the letter and "seats about 1.5% of nights and seats" on the call): the question asks about the three lines together, so two disclosed sub-3% figures summing to ≥3% resolve Yes.
3. Buckets: "single-digit" and "low-single-digit" resolve No; "mid-single-digit" (midpoint 5) and "high-single-digit" resolve Yes; "approximately 3%" or "over 3%" resolves Yes; "nearly 3%" resolves No.
4. A FY27 revenue figure counts if it is a company statement of expected FY27 revenue for any combination of the three lines and is ≥$500M ("on track for over $500 million next year"); a multi-year "$1 billion opportunity" does not.
5. (Revision 2, A11-23) Denominator: Airbnb's letters use "nights booked" as shorthand for the reported KPI (the FY2025 10-K defines Nights and Seats Booked as nights booked for stays plus seats booked for experiences and services). A share stated "of nights booked" is therefore accepted as a share of the reported Nights and Seats Booked metric without conversion; the strict alternative (convert at the ~2% seats share, so "3% of nights" = 2.94% and fails) is priced as a sensitivity.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | 2Q26 letter: "While hotels still represent a single-digit percentage of nights booked, they're seeing significant growth. In fact, hotel nights booked grew approximately three times as fast as our homes business."; Experiences supply "nearly 80% year-over-year"; "seats booked accelerating year-over-year and quarter-over-quarter"; ~35% of first-time hotel guests return to book a home | data/raw/letters/2Q26_d70413dex991.htm | 2026-08-06 | 2026-09-17 | yes |
| 2 | 1Q26 call (Mertz): "hotels today is a relatively small portion of the business. It's a single-digit per[cent]"; 2Q26 call (Mertz to Mizuho on timeframe/scale): "hotels are only a single-digit percent of nights booked on the platform, so a relatively small segment" | data/raw/transcripts/web/1Q26.html; data/processed/abnb_declined_to_quantify.csv row 34 | 2026-08-06 | 2026-09-17 | yes |
| 3 | 2Q25 call (Mertz to Barclays, "1% or zero?"): "we have not historically broken out nights booked versus experiences booked. We were not going to do that today. ... the seats booked today are indeed immaterial" | data/processed/abnb_declined_to_quantify.csv row 27 | 2025-08-06 | 2026-09-17 | yes |
| 4 | FY2025 10-K (filed 2026-02-12, the print day; revision 2, A11-10): "Substantially all of our revenue comes from stays booked on our platform." and "For experiences and services, we only earn a host fee." Revenue is disaggregated by geographic region only; no hotel, Experiences or Services revenue, nights or GBV figure anywhere in the 10-K. KPI definition: "Nights and Seats Booked ... represents the sum of the total number of nights booked for stays and the total number of seats booked for experiences and services"; HotelTonight is excluded from the listing counts | data/raw/filings/abnb_10k_FY2025.htm (regex scan, queries 4, 17); sources/edgar_submissions (R06 folder) | 2026-02-12 | 2026-09-17 | yes |
| 5 | Airbnb has never given revenue for hotels, Experiences or Services; the repo's FY25 bases are constructions: hotels ~$290M (assumes 3.5% of 533m nights × ~$140 ADR × ~11% commission), Experiences ~$90M, Services ~$12M; FY27 base $509M / $196M / $92M (bear $400/135/38M) | research/notes/overnight/11_competition-supply-and-overlays.md §6 and caveats | 2026-09-07 | 2026-09-17 | yes |
| 6 | Seats share of the nights+seats denominator: 1.3% FY25 → 2.8% FY27 base (about 2% in FY26); seats dilution of ADR −0.18pp FY25 → −0.48 FY26 → −0.57 FY27 (team path). Seats alone reach 3% only in FY27–28. (Revision 2, A11-01) The true combined share is therefore the hotel share plus about two points and is very likely ≥3% already; the binding constraint on the question is disclosure, not magnitude | docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §2.1–2.2 (line 268: "seats share of denominator 1.3% FY25 → 2.8% FY27 base"); research/notes/2026-09-07_adr-decomposition.md | 2026-09-11 | 2026-09-17 | yes |
| 7 | Arithmetic on the letters' own statements: with homes at +9.5% and hotels at ~3x (+30%), a hotel share of 2% contributes 0.6pt of nights growth, 3% 0.9pt, 3.5% 1.05pt, 5% 1.5pt. This identifies nothing about the share itself. (Revision 2, A11-11) P(the share is ≥3%) is now derived from the supply requirement (claim 20), not from the wording; the observation that "single-digit" for a 1–2% share would more naturally be "low-single-digit" is kept as weak, non-load-bearing colour. The team's 3.5% (claim 5) is an assumption inside a revenue construction | computed (query 11); claim 5; claim 20 | 2026-09-17 | 2026-09-17 | yes |
| 8 | Hotel supply: "thousands of boutique and independent hotels across more than 20 top destinations"; >100 NYC hotels / 20,000 rooms (Q4'25); Lark Hotels (75+ properties) Aug 2026; two Booking.com hires (D'Amico VP Hotels May 2026; Pepijn Rijvers CBO over Homes, Hotels and Global Markets from 1 Sep 2026); 15% Airbnb credit and price-match run to 31 Dec 2026 | data/raw/letters/2Q26_d70413dex991.htm; research/notes/overnight/11_competition-supply-and-overlays.md; https://news.airbnb.com/ (1 Sep 2026) | 2026-09-01 | 2026-09-17 | yes |
| 9 | 4Q25 call (Chesky): "the opportunity with hotels is massive, and we plan to share more about our approach later this year" (2026); "half of experiences bookings ... unattached" | data/raw/transcripts/web/4Q25.html | 2026-02-12 | 2026-09-17 | yes |
| 10 | Disclosure habit: Airbnb discloses category shares when they flatter (long-term stays ~20% of nights, cross-border share, urban share, app share of nights 64% in 2Q26, first-time bookers growth since 4Q25) and drops series that stop flattering (cross-border, LTS, urban, listings growth % all last given 1Q24 or earlier); regional nights went from exact % to buckets in 3Q24. (Revision 2) Independently supported by C05 revision 2's recoded matrix: continuation 0.82 / 0.77 / 0.71 (All / W1 / W2), return after a gap 4/18 | docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §4 and open item 7; docs/pitch-forecasts/questions/bundle-attribution-quantified/datasets/persistence_rates_v2.csv | 2026-09-17 | 2026-09-17 | yes |
| 11 | "Small business" descriptors have never been upgraded to a number. (Revision 2, A11-09) Independent upgrade opportunities: the seats descriptor ("immaterial") was set at the 2Q25 call, giving four later prints (3Q25, 4Q25, 1Q26, 2Q26); the hotels descriptor ("single-digit") was set at the 1Q26 call, giving one later print (2Q26): **0 upgrades in 5 opportunities**, Laplace (0+1)/(5+2) = 0.143 per print. The revision-1 count of 8 included the Goldman conference (excluded by convention 1), the FY2025 10-K, and the 2Q26 letter and call counted as two | datasets/new_business_disclosure_history.csv (8 rows; 5 are print opportunities) | 2026-08-06 | 2026-09-17 | yes |
| 12 | Team's own expectation note: "the first absolute bookings or GBV figure ... would be the disclosure upgrade the sell side wants"; catalyst calendar: "Disclosure of GBV contribution would be the trigger"; hotels "treat as re-rating not one-day" | research/notes/overnight/11_competition-supply-and-overlays.md §"what to expect"; research/notes/catalyst_calendar.md | 2026-09-07 | 2026-09-17 | no |
| 13 | 2Q26 10-Q: no hotel mention; Experiences and Services appear only in the opex narrative (third-party supply costs) and the KPI definition | data/raw/regulatory/quantification/abnb_2026q2_10q.html (query 5) | 2026-08-06 | 2026-09-17 | no |
| 14 | Chesky at Goldman (8 Sep 2026) on hotels: "we have a lower commission. We have younger travelers." No share figure; new-business revenue not sized except the undated "$1 billion" seller-services remark | https://www.investing.com/news/transcripts/airbnb-at-goldman-sachs-conference-chesky-sees-wider-runway-93CH-4892583 | 2026-09-08 | 2026-09-17 | no |
| 15 | Web: no relevant result in the searches recorded beyond third-party repetition of "single-digit share" and "3x homes"; no analyst estimate of Experiences/Services bookings or revenue surfaced (revision 2, A11-24 wording) | WebSearch queries 10, 12 (sources/web_search_log.md) | 2026-09-17 | 2026-09-17 | no |
| 16 | No Polymarket or Kalshi market on Airbnb segment disclosures | sources/polymarket_search_airbnb_20260917T034148Z.json; sources/kalshi_events_KXABNB_20260917T034148Z.json | 2026-09-17 | 2026-09-17 | no |
| 17 | Sibling object (revision 2, A11-08): C05 revision 2 P(any quantification of the bundle at 5 Nov) = 0.28, anchor null (NO_EXTERNAL_ANCHOR); produced by this run, not an external anchor | docs/pitch-forecasts/questions/bundle-attribution-quantified/forecasts/2026-09-17-forecast.json (revision 2) | 2026-09-17 | 2026-09-17 | no |
| 18 | Team path already carries hotel and seats dilution (−0.5pp of ADR) and the take-rate incentives (take rate guided flat for FY26 "accounting for higher customer incentives related to new businesses"); Experiences/Services cost sits in field ops (~$200M FY25 launch spend) | docs/margin-build/notes/40_line_build.md "Business mix"; 03_insider_mechanics.md §2.3 | 2026-09-15 | 2026-09-17 | yes |
| 19 | Final 72-hour recency check (query 14): no relevant result in the searches recorded; newsroom snapshot saved 2026-09-17T13:22Z shows no new-business metric (latest items: housing accelerator 14 Sep, Rijvers CBO 1 Sep) (revision 2, A11-24) | WebSearch `Airbnb news this week`; sources/newsroom_news.airbnb.com_20260917T132231Z.html | 2026-09-17 | 2026-09-17 | no |
| 20 | (Revision 2, A11-11) Supply arithmetic: 3% of ~575m FY26 nights is 17.2m hotel nights; the hotel funnel audit's requirement table gives 3,914 signed properties per 1m first-year nights at a 5% Airbnb channel share and 1,957 at 10%, so 17.2m nights needs ~67,500 / ~33,800 / ~16,900 properties at 5 / 10 / 20% channel share, against "thousands" of hotels in the new program. On the NYC anchor (20,000 rooms ≈ 5.8m room-nights a year at 80% occupancy) scaled to 20 destinations (117m room-nights), 3% needs a ~15% Airbnb channel share. Against that, a pre-existing hotel/aparthotel base (11,061 hotel-tagged listings in the 24-market Inside Airbnb panel in September 2025, before the May 2026 launch) makes 2–3% possible. Unconditional P(hotel share ≥3% of nights at the relevant print) ≈ 0.40–0.45; conditional on management choosing to volunteer the figure (claim 10: it discloses shares that flatter) ≈ 0.55 | data/processed/hotel_funnel_audit/hotel_supply_requirements.csv; research/notes/overnight/11_competition-supply-and-overlays.md; datasets/r09_model_v2.py output | 2026-09-17 | 2026-09-17 | yes |
| 21 | (Revision 2) Cross-check on metric initiation from C05 revision 2's 16-metric × 23-print matrix: after the 1Q21 seed cohort (6 metrics), Airbnb started 10 new quantified metric disclosures over 22 prints, ~0.45 initiations per print for any metric. The 0.12 / 0.20 hazards here are for one specific salient metric and sit well inside that rate | docs/pitch-forecasts/questions/bundle-attribution-quantified/datasets/metric_persistence_matrix_v2_4Q20-2Q26.csv (A11-reproduce.py) | 2026-09-17 | 2026-09-17 | yes |
| 22 | (Revision 2, A11-25) Coherence: the FY27-revenue route here (0.03) implies R08 = Yes (a FY27 revenue figure ≥$500M for a booking-generating line converts to ≥$3.7bn of GBV under R08's convention 2); 0.03 ≤ R08's 0.13 | docs/pitch-forecasts/questions/risk-new-2027-growth-lever/forecasts/2026-09-17-forecast.json | 2026-09-17 | 2026-09-17 | no |

## 2. Query Log
1. [repo] `grep -n -i "business mix|experiences|services|hotel|seats" docs/margin-build/notes/40_line_build.md`; same on research/notes/overnight/10_regional-and-segment-decomposition.md and 11_competition-supply-and-overlays.md
2. [repo] `grep -n -i "seat" research/notes/2026-09-07_adr-decomposition.md`; §2 and §4 of docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md
3. [repo] regex extraction of hotel / Experiences / Services / "single-digit" / "percentage points" passages from the 3Q25, 4Q25, 1Q26, 2Q26 letters; same keywords on the 4Q24–2Q26 call transcripts
4. [repo] regex scan of data/raw/filings/abnb_10k_FY2025.htm for hotel, "Experiences and Services", "seats booked", "not material", "substantially all"
5. [repo] regex scan of data/raw/regulatory/quantification/abnb_2026q2_10q.html for hotel, experiences and services
6. [repo] data/processed/hotel_funnel_audit/README.md, hotel_model_summary.json, hotel_mix_scenarios.csv, hotel_market_capacity_anchors.csv (capacity anchors, not shares)
7. [repo] pandas filter of data/processed/abnb_declined_to_quantify.csv for hotel|experience|service|seat
8. [API] Polymarket public-search `airbnb`; Kalshi events series KXABNB (2026-09-17T03:41:48Z)
9. [WebFetch] https://news.airbnb.com/
10. [WebSearch] `Airbnb hotels share of nights booked 2026`
11. [model] hotel-share contribution arithmetic and seats-share arithmetic (python, query output in the R09 dataset notes); `python datasets/r09_model.py`
12. [WebSearch] `Airbnb Experiences Services bookings size 2026 analyst estimate revenue`
13. [WebFetch] Investing.com Goldman Communacopia 2026 summary; CNBC 20 May 2026 (403)
14. [WebSearch, final 72-hour recency] `Airbnb news this week`
15. [repo, revision 2] `py -3.13 -B docs/pitch-forecasts/audits/A11-reproduce.py` (route replay, 5-vs-8 descriptor denominator, C05 rev-2 initiation count, 10-K and February 8-K filing dates)
16. [repo, revision 2] `data/processed/hotel_funnel_audit/hotel_supply_requirements.csv` read in full (4 scenario rows); supply arithmetic in `datasets/r09_model_v2.py`
17. [repo, revision 2] regex over data/raw/filings/abnb_10k_FY2025.htm for the Nights and Seats Booked definition, HotelTonight, and "disaggregat" (revenue disaggregation is by geography only)
18. [repo, revision 2] docs/pitch-forecasts/questions/bundle-attribution-quantified/forecasts/2026-09-17-forecast.json and datasets/persistence_rates_v2.csv (C05 revision 2)
19. [web, revision 2] `curl -sL https://news.airbnb.com/` saved to sources/newsroom_news.airbnb.com_20260917T132231Z.html
20. [model, revision 2] `py -3.13 datasets/r09_model_v2.py` (outputs r09_v2_summary.csv, r09_v2_sensitivity.csv)

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, Pepijn Rijvers, hotels, boutique and independent hotels, Experiences, Services, Nights and Seats Booked, 4Q26 shareholder letter, FY2026 10-K

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Hotel descriptor upgraded (any move from "single-digit" to a number or a finer bucket) at the 5 Nov print, the Feb print or the same-day FY26 10-K | kept, main route (upgrade hazard 0.12 Nov, 0.20 Feb incl. the 10-K venue; revision 2, A11-10/A11-12) | New CBO with a hotels-first mandate, credit expiry 31 Dec, "share more about our approach later this year" (claims 8, 9); Laplace on the corrected 5-opportunity denominator 0.143 per print (claim 11); against: management's deliberate "relatively small segment" framing (claim 2) |
| ... and the upgraded figure or bucket is ≥3% | kept, P 0.55 conditional (revision 2, was 0.65) | Supply arithmetic puts the unconditional probability at ~0.40–0.45 (claim 20); lifted to 0.55 because Airbnb volunteers a category share when it flatters (claim 10), so an upgrade is more likely when the number is a good one |
| Hotels disclosed below 3% **and** a seats figure disclosed, summing to ≥3% (aggregation route; revision 2, A11-01) | kept, ~0.02 | Requires two disclosures, one of them the seats split management has refused (claim 3): P(hotel upgraded) 0.30 × P(<3) 0.45 × P(seats figure also given) ~0.15 → ~0.02 |
| Seats (Experiences + Services) share ≥3% disclosed on its own | kept, ~0.02 | Seats ~2% of the denominator in FY26 (claim 6); management called them immaterial and refused the split (claim 3) |
| GBV share ≥3% disclosed | kept, ~0.02 | Hotel ADR is ~0.8x a home night and tickets are small, so the GBV share is below the nights share; GBV shares of a line have never been given |
| FY27 revenue figure ≥$500M for the lines | kept, ~0.03 | Never a line revenue figure (claims 4, 5); the FY27 base construction ($800M) is above $500M, so the figure would qualify if ever given; coherent with R08 (claim 22) |
| A combined "new businesses now X% of nights and seats" sentence in the Feb annual review | kept, ~0.03 | Not management's vocabulary to date; the Feb letter does carry annual reviews |
| FY2026 10-K adds a segment or a line-level figure | kept as a venue inside the hotel route, not a separate route (revision 2, A11-10, accepted in part) | Two of the last three 10-Ks filed on the print day, so the 10-K is inside the window; but revenue is disaggregated by geography only and a FY26 line-revenue figure would not satisfy any of the three tests (the question needs a nights/GBV share or a FY27 revenue figure); the 10-K counts only through a share statement in its KPI discussion, which is the hotel route by another venue (+0.02 on the Feb hazard) |
| City-level hotel shares ("over 10% in NYC") | discarded | Convention 2 |

## 5. Independent Estimates
- base_rate_estimate: 0.24 — Upgrade hazard for a "small" descriptor on the corrected denominator (claim 11): 0 of 5 opportunities, Laplace 0.143 per print; two prints → 0.265; × P(figure ≥3%) 0.55 = 0.146; plus the other routes (seats 0.02, GBV 0.02, FY27 revenue 0.03, combined sentence 0.03, aggregation 0.02 → 0.114 combined) → union 0.244. Regime check: any-metric initiations run at ~0.45 per print (claim 21), so a hazard of 0.14 for one salient metric is not an outlier.
- decomposition_estimate: 0.26 — `datasets/r09_model_v2.py`: hotel-descriptor upgrade hazards 0.12 (Nov) and 0.20 (Feb annual review, new CBO, credit expiry, the promised "approach" update, plus the same-day 10-K venue) → P(upgraded) 0.296 × 0.55 = 0.163; other routes 0.114; union 0.259.
- anchor_estimate: none — No market (claim 16). The revision-1 anchor (C05 at 0.27) was another forecast from this run, stale (C05 revision 2 is 0.28) and not independent of the run's disclosure priors (A11-08); withdrawn as an anchor and kept as a labelled sibling comparison (claim 17). The three-estimate requirement of the skill is unmet: two internal estimates and no external anchor.
- anchor_value: n/a (NO_EXTERNAL_ANCHOR)
- final_estimate: 0.25
- final_minus_anchor: n/a. Against the sibling comparisons: 0.00 vs the audit's independent 0.25 (its construction, Nov 0.10 / Feb 0.18 / true 0.55 / aggregation 0.025, gives 0.246 inside this model); 0.00 vs revision 1 (the number is unchanged; the construction is not); −0.03 vs C05 revision 2's 0.28 (a different object).

Reconciliation: base rate 0.24 and decomposition 0.26 differ only in the Feb hazard (the base rate treats both prints alike; the decomposition gives the Feb annual review, the hotels update and the 10-K venue more weight). Both now share the corrected denominator, the supply-derived 0.55 and the aggregation route, so the agreement is by construction and not evidence of anything. Final 0.25.

## 6. Final Numbers
**P(Yes) = 0.25**, credible interval 0.13–0.38.
Route split of the Yes mass: hotel descriptor upgraded to a figure or bucket ≥3% (nights) ≈ 0.16; combined new-business share ≈ 0.03; FY27 revenue ≥$500M ≈ 0.03; seats or GBV share ≈ 0.04; aggregation of two sub-3% figures ≈ 0.02 (overlaps removed in the union).
Extreme-probability gate: not triggered.
Coherence (claim 22): FY27-revenue route (0.03) ≤ R08 (0.13); R06 independent.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Hotel upgrade hazards 0.12 / 0.20; if halved (management keeps "single-digit" until hotels are ~10%) | 0.19 |
| Hotel upgrade hazards; if doubled (the Feb letter carries a hotels section with numbers) | 0.38 |
| Hotel upgrade hazards; if the flat Laplace 0.143 at both prints | 0.24 |
| P(figure ≥3%) 0.55; if 0.40 (unconditional supply arithmetic, no selective-disclosure lift) | 0.22 |
| P(figure ≥3%); if 0.65 (revision 1) | 0.29 |
| P(figure ≥3%); if 0.85 (hotels 4–6%) | 0.34 |
| Combined new-business share sentence in the Feb letter 0.03; if 0.10 | 0.31 |
| Aggregation route 0.02; if the resolver may not sum two figures (0) / if 0.05 | 0.24 / 0.28 |
| Convention 5 (share "of nights" accepted); if the strict denominator applies (a stated share must be ≥3.1%) | 0.25 (P(≥3) 0.50 → 0.245) |
| Convention 3 (mid-single-digit = Yes); if only an explicit number counts (hazards × 0.75) | 0.23 |
| Auditor's construction (0.10 / 0.18, true 0.55, aggregation 0.025) | 0.25 |
| Revision-1 construction (0.12 / 0.18, true 0.65, no aggregation) | 0.26 |
| Joint bull (0.20/0.35, true 0.85, combined 0.10, revenue 0.06, aggregation 0.05) | 0.54 |
| Joint bear (0.06/0.10, true 0.40, others 0.01) | 0.11 |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-10-02 | Prelim memo freeze | Quote 0.25 (0.13–0.38) |
| 2026-10-15 to 11-04 | Newsroom: any hotels strategy post (Rijvers' first 60 days), Experiences/Services metrics, Winter Release | A company post with a share of total nights ≥3% → resolve Yes if repeated in the letter; raise to 0.45 on the post |
| 2026-11-05 | 3Q26 letter and call | Numeric or mid/high-single-digit hotel share ≥3 → Yes; "single-digit" repeated → 0.19 (Feb hazard 0.20 × 0.55 plus the other routes); an absolute seats or hotel-nights figure below the bar → 0.15 (the vocabulary changed, the bar was not met); a hotel share stated below 3% → 0.17 (the aggregation route opens: any seats figure by Feb then resolves it) |
| 2026-12-31 | 15% hotel credit expires | No move; sets up the Feb hotels discussion |
| 2027-02-11 | 4Q26 letter, call, FY27 guide | Resolve per conventions 1–5 |
| 2027-02-11 to 02-16 | FY2026 10-K | Counts if filed by the print date (two of the last three were same-day); read the KPI discussion for a share statement |

## 9. Impact
If Yes (a disclosure, not a change in the business: the shares exist whether or not they are stated):

| Item | Delta if Yes | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | disclosure does not change the print; hotel and seats volumes are already inside reported nights |
| 4Q26 nights (pts) | 0 | as above |
| ADR (pts) | 0 (already in the team path: hotel and seats dilution −0.5pp) | claims 6, 18 |
| 4Q26 revenue ($M) | 0 | as above |
| FY27 revenue ($M) | 0 | the FY27 path carries the new-business bases (claim 5); a disclosure would move the Street's model, not ours |
| FY26 adj. EBITDA margin (pp) | 0 | Experiences/Services cost already in field ops (claim 18) |
| FY27 adj. EBITDA margin (pp) | 0 | as above |
| FY27 EPS ($) | 0.00 | as above |
| Stock ($/share) | +2 (narrative: a disclosed 3–5% share growing ~30% reads as ~1pt of structural growth, ≈ $1.50–4.90/pt; haircut because the same disclosure reveals that homes grow ~1pt slower than reported nights (claim 7) and makes the ADR/take-rate dilution explicit, both of which support the short) | claim 7, claim 12, docs/pitch-forecasts/00_BRIEF.md sensitivities |
| EV = P × stock impact | 0.25 × $2 ≈ **+$0.5/share** | |
| Materiality | **Immaterial** (EV < $1/share). The memo can drop it, or fold it into the ADR paragraph: a hotel-share disclosure is as likely to confirm the mix drag as to reframe growth | |

## 10. Revision notes
| Change | Finding |
|---|---|
| Metadata: revision 2, revised 2026-09-17; audit and response paths added | — |
| Convention 2: the resolver may add separately disclosed shares of the same denominator; aggregation route added at 0.02 (§4, model) | A11-01 |
| Convention 5 added: a share "of nights booked" is accepted as a share of the reported KPI; strict alternative priced in §7 | A11-23 |
| Convention 1 and claim 4: FY2025 10-K date corrected to 2026-02-12 (the print day); 10-K restored as a venue inside the hotel route (+0.02 on the Feb hazard); the auditor's revenue-disaggregation reading noted as unable to resolve the question by itself | A11-10 (accepted in part) |
| Claim 11: descriptor denominator recounted to 5 independent opportunities (Laplace 0.143 per print); base-rate estimate rebuilt (0.21 → 0.24) | A11-09 |
| Claim 7 and claim 20: P(figure ≥3%) derived from the supply requirement file (unconditional ~0.40–0.45, conditional 0.55) rather than from the wording; 0.65 → 0.55 | A11-11 |
| Model: hazard renamed "descriptor upgraded" (any move from "single-digit" to a number or a finer bucket) with the ≥3 multiplier kept; `r09_model_v2.py` | A11-12 |
| Anchor withdrawn (NO_EXTERNAL_ANCHOR); C05 revision 2 (0.28) kept as a labelled sibling comparison (claim 17); three-estimate requirement stated unmet | A11-08 |
| Claim 21: C05 rev-2 metric-initiation cross-check (~0.45 initiations per print, any metric) | audit §Scope suggestion |
| Claim 22 and §6: coherence with R08 recorded | A11-25 |
| Claims 15 and 19: newsroom snapshot saved; "no relevant result in the searches recorded" wording | A11-24 |
| §6: P(Yes) 0.25 unchanged (model 0.259; revision 1 0.260 by a different construction); route split re-stated; §7 rebuilt from `r09_v2_sensitivity.csv`; §8 November branches updated | — |
| Queries 15–20 appended; `datasets/r09_model_v2.py`, `r09_v2_summary.csv`, `r09_v2_sensitivity.csv` added (revision-1 files untouched) | — |
