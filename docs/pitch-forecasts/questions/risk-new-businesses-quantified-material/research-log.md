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
- revision: 1
- agent: fable
- batch: A11 (with R06 and R08)

## 0b. Question (verbatim)
### Title
By the Feb print, will management disclose that hotels, Experiences or Services together account for ≥3% of nights and seats booked, or ≥3% of GBV, or give a FY27 revenue figure for them of ≥$500M?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes on any of the three disclosures. Resolution ~11 Feb 2027.
### Fine Print
(none in the registry.) Conventions adopted here and forecast under:
1. Sources: the 3Q26 and 4Q26 letters and calls, the 3Q26 10-Q, and the FY26 10-K only if filed on or before the Feb print date (Airbnb's 10-K has filed 0–4 days after the print). Conference remarks do not count.
2. The share must be of total Nights and Seats Booked or total GBV. A city- or market-level share ("over 10% of nights in New York") does not count. A share for one line alone (e.g. hotels 4% of nights) counts, since the three lines "together" are then ≥3%.
3. Buckets: "single-digit" and "low-single-digit" resolve No; "mid-single-digit" (midpoint 5) and "high-single-digit" resolve Yes; "approximately 3%" or "over 3%" resolves Yes; "nearly 3%" resolves No.
4. A FY27 revenue figure counts if it is a company statement of expected FY27 revenue for any combination of the three lines and is ≥$500M ("on track for over $500 million next year"); a multi-year "$1 billion opportunity" does not.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | 2Q26 letter: "While hotels still represent a single-digit percentage of nights booked, they're seeing significant growth. In fact, hotel nights booked grew approximately three times as fast as our homes business."; Experiences supply "nearly 80% year-over-year"; "seats booked accelerating year-over-year and quarter-over-quarter"; ~35% of first-time hotel guests return to book a home | data/raw/letters/2Q26_d70413dex991.htm | 2026-08-06 | 2026-09-17 | yes |
| 2 | 1Q26 call (Mertz): "hotels today is a relatively small portion of the business. It's a single-digit per[cent]"; 2Q26 call (Mertz to Mizuho on timeframe/scale): "hotels are only a single-digit percent of nights booked on the platform, so a relatively small segment" | data/raw/transcripts/web/1Q26.html; data/processed/abnb_declined_to_quantify.csv row 34 | 2026-08-06 | 2026-09-17 | yes |
| 3 | 2Q25 call (Mertz to Barclays, "1% or zero?"): "we have not historically broken out nights booked versus experiences booked. We were not going to do that today. ... the seats booked today are indeed immaterial" | data/processed/abnb_declined_to_quantify.csv row 27 | 2025-08-06 | 2026-09-17 | yes |
| 4 | FY2025 10-K: "Substantially all of our revenue comes from stays booked on our platform." and "For experiences and services, we only earn a host fee." No hotel, Experiences or Services revenue, nights or GBV figure anywhere in the 10-K | data/raw/filings/abnb_10k_FY2025.htm (regex scan, query 4) | 2026-02-13 | 2026-09-17 | yes |
| 5 | Airbnb has never given revenue for hotels, Experiences or Services; the repo's FY25 bases are constructions: hotels ~$290M (assumes 3.5% of 533m nights × ~$140 ADR × ~11% commission), Experiences ~$90M, Services ~$12M; FY27 base $509M / $196M / $92M (bear $400/135/38M) | research/notes/overnight/11_competition-supply-and-overlays.md §6 and caveats | 2026-09-07 | 2026-09-17 | yes |
| 6 | Seats share of the nights+seats denominator: 1.3% FY25 → 2.8% FY27 base (about 2% in FY26); seats dilution of ADR −0.18pp FY25 → −0.48 FY26 → −0.57 FY27 (team path). Seats alone reach 3% only in FY27–28, so the ≥3% test is carried by hotels | docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §2.1–2.2; research/notes/2026-09-07_adr-decomposition.md | 2026-09-11 | 2026-09-17 | yes |
| 7 | Arithmetic on the letters' own statements: with homes at +9.5% and hotels at ~3x (+30%), a hotel share of 2% contributes 0.6pt of nights growth, 3% 0.9pt, 3.5% 1.05pt, 5% 1.5pt; "single-digit" used for a 1–2% share would more naturally be "low-single-digit". Team assumption 3.5%; this log's P(true share ≥3%) = 0.65 | computed (query 11); claim 5 | 2026-09-17 | 2026-09-17 | yes |
| 8 | Hotel supply: "thousands of boutique and independent hotels across more than 20 top destinations"; >100 NYC hotels / 20,000 rooms (Q4'25); Lark Hotels (75+ properties) Aug 2026; two Booking.com hires (D'Amico VP Hotels May 2026; Pepijn Rijvers CBO over Homes, Hotels and Global Markets from 1 Sep 2026); 15% Airbnb credit and price-match run to 31 Dec 2026 | data/raw/letters/2Q26_d70413dex991.htm; research/notes/overnight/11_competition-supply-and-overlays.md; https://news.airbnb.com/ (1 Sep 2026) | 2026-09-01 | 2026-09-17 | yes |
| 9 | 4Q25 call (Chesky): "the opportunity with hotels is massive, and we plan to share more about our approach later this year" (2026); "half of experiences bookings ... unattached" | data/raw/transcripts/web/4Q25.html | 2026-02-12 | 2026-09-17 | yes |
| 10 | Disclosure habit: Airbnb discloses category shares when they flatter (long-term stays ~20% of nights, cross-border share, urban share, app share of nights 64% in 2Q26, first-time bookers growth since 4Q25) and drops series that stop flattering (cross-border, LTS, urban, listings growth % all last given 1Q24 or earlier); regional nights went from exact % to buckets in 3Q24 | docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §4 and open item 7; docs/pitch-forecasts/questions/bundle-attribution-quantified/research-log.md claim 5 | 2026-09-11 | 2026-09-17 | yes |
| 11 | "Small business" descriptors have never been upgraded to a number: seats "immaterial" (2Q25) unchanged through 5 prints; hotels "single-digit" unchanged through 3 print-statements (1Q26 call, 2Q26 letter, 2Q26 call): 0 upgrades in 8 descriptor-prints | datasets/new_business_disclosure_history.csv | 2026-08-06 | 2026-09-17 | yes |
| 12 | Team's own expectation note: "the first absolute bookings or GBV figure ... would be the disclosure upgrade the sell side wants"; catalyst calendar: "Disclosure of GBV contribution would be the trigger"; hotels "treat as re-rating not one-day" | research/notes/overnight/11_competition-supply-and-overlays.md §"what to expect"; research/notes/catalyst_calendar.md | 2026-09-07 | 2026-09-17 | no |
| 13 | 2Q26 10-Q: no hotel mention; Experiences and Services appear only in the opex narrative (third-party supply costs) and the KPI definition | data/raw/regulatory/quantification/abnb_2026q2_10q.html (query 5) | 2026-08-06 | 2026-09-17 | no |
| 14 | Chesky at Goldman (8 Sep 2026) on hotels: "we have a lower commission. We have younger travelers." No share figure; new-business revenue not sized except the undated "$1 billion" seller-services remark | https://www.investing.com/news/transcripts/airbnb-at-goldman-sachs-conference-chesky-sees-wider-runway-93CH-4892583 | 2026-09-08 | 2026-09-17 | no |
| 15 | Web: every third-party write-up repeats "single-digit share" and "3x homes"; no analyst estimate of Experiences/Services bookings or revenue surfaced | WebSearch queries 3–4 (sources/web_search_log.md) | 2026-09-17 | 2026-09-17 | no |
| 16 | No Polymarket or Kalshi market on Airbnb segment disclosures | sources/polymarket_search_airbnb_20260917T034148Z.json; sources/kalshi_events_KXABNB_20260917T034148Z.json | 2026-09-17 | 2026-09-17 | no |
| 17 | Sibling object: C05 log P(any quantification of the bundle at 5 Nov) = 0.27 | docs/pitch-forecasts/questions/bundle-attribution-quantified/research-log.md §6 | 2026-09-17 | 2026-09-17 | no |
| 18 | Team path already carries hotel and seats dilution (−0.5pp of ADR) and the take-rate incentives (take rate guided flat for FY26 "accounting for higher customer incentives related to new businesses"); Experiences/Services cost sits in field ops (~$200M FY25 launch spend) | docs/margin-build/notes/40_line_build.md "Business mix"; 03_insider_mechanics.md §2.3 | 2026-09-15 | 2026-09-17 | yes |
| 19 | Final 72-hour recency check (query 9): no new-business metric released | WebSearch `Airbnb news this week` | 2026-09-17 | 2026-09-17 | no |

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

## 3. Leading Hypothesis Entities
Airbnb, Ellie Mertz, Brian Chesky, Pepijn Rijvers, hotels, boutique and independent hotels, Experiences, Services, Nights and Seats Booked, 4Q26 shareholder letter, FY2026 10-K

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Hotel share upgraded from "single-digit" to a number or a mid/high bucket at the 5 Nov or Feb print | kept, main route (disclosure hazard 0.12 Nov, 0.18 Feb) | New CBO with a hotels-first mandate, credit expiry 31 Dec, "share more about our approach later this year" (claims 8, 9); against: 0 upgrades in 8 descriptor-prints, management's deliberate "relatively small segment" framing (claims 2, 11) |
| ... and the disclosed figure is ≥3% | kept, P 0.65 conditional | Arithmetic and the wording favour 3–6% (claim 7); the 3.5% team figure is an assumption, not a disclosure (claim 5) |
| Seats (Experiences + Services) share ≥3% disclosed | kept, ~0.02 | Seats ~2% of the denominator in FY26 (claim 6); management called them immaterial and refused the split (claim 3) |
| GBV share ≥3% disclosed | kept, ~0.02 | Hotel ADR is ~0.8x a home night and tickets are small, so the GBV share is below the nights share; GBV shares of a line have never been given |
| FY27 revenue figure ≥$500M for the lines | kept, ~0.03 | Never a line revenue figure (claims 4, 5); the FY27 base construction ($800M) is above $500M, so the figure would qualify if ever given |
| A combined "new businesses now X% of nights and seats" sentence in the Feb annual review | kept, ~0.03 | Not management's vocabulary to date; the Feb letter does carry annual reviews |
| FY2026 10-K adds a segment or a materiality statement | discarded as a route | Single reportable segment; the FY2025 10-K says "substantially all" revenue is stays (claim 4) and the 10-K typically files after the print (convention 1) |
| City-level hotel shares ("over 10% in NYC") | discarded | Convention 2 |

## 5. Independent Estimates
- base_rate_estimate: 0.21 — Upgrade hazard for a "small" descriptor: 0 of 8 descriptor-prints (claim 11), Laplace (0+1)/(8+2) = 0.10 per print; two prints → 0.19; × P(true hotel share ≥3%) 0.65 = 0.12; plus the other three routes (~0.10 combined) → 0.21.
- decomposition_estimate: 0.26 — `datasets/r09_model.py`: hotel-share disclosure hazards 0.12 (Nov) and 0.18 (Feb, annual review, new CBO, credit expiry, the promised "approach" update) → P(disclosed) 0.28 × 0.65 = 0.18; other routes 0.10; union 0.26.
- anchor_estimate: 0.27 — No market (claim 16). Nearest sibling: C05's P(any quantification of the bundle at 5 Nov) = 0.27 (claim 17), another management-quantification-behaviour object with different content.
- anchor_value: 0.27
- final_estimate: 0.25
- final_minus_anchor: −0.02 — the base rate and the decomposition are built from the new-business disclosure history (claims 1–4, 9–11), not from C05; the coincidence is that both objects are "will management put a number on a small thing", and Airbnb's answer to that has been about one in four.

Reconciliation: base rate 0.21 and decomposition 0.26 differ only in the Feb hazard (the base rate treats both prints alike; the decomposition gives the Feb annual review and the hotels update more weight). Final 0.25.

## 6. Final Numbers
**P(Yes) = 0.25**, credible interval 0.14–0.38.
Route split of the Yes mass: hotel share disclosed ≥3% (nights) ≈ 0.18; combined new-business share ≈ 0.03; FY27 revenue ≥$500M ≈ 0.03; seats or GBV share ≈ 0.02 (overlaps removed in the union).
Extreme-probability gate: not triggered.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Hotel disclosure hazards 0.12 / 0.18; if halved (management keeps "single-digit" until hotels are ~10%) | 0.18 |
| Hotel disclosure hazards; if doubled (the Feb letter carries a hotels section with numbers) | 0.40 |
| P(true hotel share ≥3%) 0.65; if hotels are really 2–3% of nights (0.40) | 0.20 |
| P(true hotel share ≥3%); if 4–6% (0.85) | 0.31 |
| Combined new-business share sentence in the Feb letter 0.03; if 0.10 | 0.31 |
| Convention 3 (mid-single-digit = Yes); if only an explicit number counts | 0.21 |
| Joint bull (0.20/0.35, true 0.85, combined 0.10, revenue 0.06) | 0.52 |
| Joint bear (0.06/0.09, true 0.40, others 0.01) | 0.10 |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-10-02 | Prelim memo freeze | Quote 0.25 (0.14–0.38) |
| 2026-10-15 to 11-04 | Newsroom: any hotels strategy post (Rijvers' first 60 days), Experiences/Services metrics, Winter Release | A company post with a share of total nights ≥3% → resolve Yes if repeated in the letter; raise to 0.45 on the post |
| 2026-11-05 | 3Q26 letter and call | Numeric or mid/high-single-digit hotel share ≥3 → Yes; "single-digit" repeated → 0.19; an absolute seats or hotel-nights figure below the bar → 0.15 (the vocabulary changed, the bar was not met) |
| 2026-12-31 | 15% hotel credit expires | No move; sets up the Feb hotels discussion |
| 2027-02-11 | 4Q26 letter, call, FY27 guide | Resolve per conventions 1–4 |
| 2027-02-12 to 02-16 | FY2026 10-K | Counts only if filed by the print date; otherwise note for the audit |

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
