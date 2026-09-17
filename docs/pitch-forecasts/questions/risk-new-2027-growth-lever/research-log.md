# RESEARCH LOG

## 0. Metadata
- question_name: risk-new-2027-growth-lever
- question_url: n/a (internal pitch-forecast question R08, `docs/pitch-forecasts/QUESTIONS.md`)
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
- batch: A11 (with R06 and R09)

## 0b. Question (verbatim)
### Title
By the Feb print, will management announce and quantify a new product or pricing initiative expected to add ≥1 point to 2027 nights or GBV growth?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if a letter or call gives a numeric expected contribution (≥1pt, or ≥$1bn GBV) for a product launched or announced after 16 Sep 2026 (or a named 2027 rollout, e.g., RNPL for new booking types, a new payment product, an AI booking agent, hotels at scale). Resolution ~11 Feb 2027.
### Fine Print
(none in the registry.) Conventions adopted here and forecast under:
1. "Letter or call" = the 3Q26 and 4Q26 shareholder letters, the two earnings calls (prepared remarks and Q&A) and any 8-K/10-Q/10-K text; investor-conference remarks (Goldman, Morgan Stanley) do not count. Priced separately in §7.
2. "Numeric expected contribution" = an explicit figure or explicit bound ("approximately 1 point", "over 100 basis points", "at least $1 billion of GBV", "$300 million of revenue in 2027"). Order-of-magnitude phrases ("hundreds of millions", "as much as Hawaii", "multi-billion opportunity", "many multiples of RNPL") do not count. A revenue figure converts to GBV at the trailing take rate (13.4%), so any explicit 2027 revenue figure ≥$135M qualifies; a nights figure qualifies at ≥1 point.
3. "Expected to add to 2027" = the statement must be forward-looking and tied to 2027 (or "next year" said in 2026, or the FY27 guide). A backward-looking attribution ("delivered 3 points in Q1") does not count; an undated opportunity ("a $1 billion business in three to five years") does not count.
4. The product must be launched or announced after 16 Sep 2026, or be a named 2027 rollout of an existing product (the RNPL, payments, AI-agent and hotels examples in the criteria). The May 2026 Summer Release products (car rentals, groceries, hotels in 20 cities) count only if the statement is about their 2027 expansion.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | In 23 prints (4Q20–2Q26) a product contribution stated in points of nights or GBV appears exactly twice, both backward-looking: 4Q25 call "over 200 basis points of growth in nights booked and roughly 300 basis points of growth in GBV in Q4"; 1Q26 call "approximately three points of nights booked growth and approximately four points of GBV growth in Q1". The 2Q26 call gave no figure ("there is no one thing") | data/raw/transcripts/web/4Q25.html; 1Q26.html; 2Q26.html; docs/pitch-forecasts/questions/bundle-attribution-quantified/research-log.md claims 1–3, 6 | 2026-08-06 | 2026-09-17 | yes |
| 2 | Forward-looking product statements with any number, all prints and conferences 2023–26 (10 rows): none is an explicit figure tied to a year for a growth metric. Closest: 4Q24 call "a great business could get to $1 billion of revenue" (3–5 years, undated); 4Q25 call "Project Y will deliver hundreds of millions more this year" and "pricing initiatives will drive as much revenue this year as Hawaii"; 1Q26 call "payments and pricing roadmap ... hundreds of millions of dollars in revenue each year"; GS26 "$1 billion incremental high margin revenue" (seller services, undated, conference) | datasets/forward_product_quantification_history.csv (from data/raw/transcripts/web/*.html and 05_statements.csv) | 2023-03-07 to 2026-09-08 | 2026-09-17 | yes |
| 3 | The only dated, numeric forward product statement in the record is a cost: FY25 new-business investment "$200–250M" (4Q24 letter, 13 Feb 2025) | data/raw/letters/4Q24_d915198dex991.htm; docs/margin-build/notes/05_mgmt_statements_v2.md (V012) | 2025-02-13 | 2026-09-17 | yes |
| 4 | Chesky, Goldman Communacopia 8 Sep 2026: "We're going to have some major announcements next year. I can't share too much except to say that I think I want to shift Airbnb from a marketplace to much more of a community." (V023). Also "straight shot to $1 billion incremental high margin revenue" for seller services (V022), sponsored listings named | https://www.investing.com/news/transcripts/airbnb-at-goldman-sachs-conference-chesky-sees-wider-runway-93CH-4892583 ; data/processed/margin_build/05_mgmt_statements_v2/05_statements.csv | 2026-09-08 | 2026-09-17 | yes |
| 5 | The margin build's hint H07 reads V023 as launch cost before revenue in FY27 ("the S100 pattern"), no budget given; FY25's launch cost $200–250M | data/processed/margin_build/05_mgmt_statements_v2/05_fy27_hints.csv (H07) | 2026-09-15 | 2026-09-17 | no |
| 6 | 2Q26 call, Chesky on pricing: "We are essentially building an entirely new pricing model ... powered by AI ... a new pricing model that we're rolling out"; "many multiples bigger than RNPL" (D053); the CFO: "the single service fee ... allows us to provide more simplified pricing recommendations" | data/raw/transcripts/web/2Q26.html; data/processed/overnight2/D/rnpl_statement_ledger.csv D053 | 2026-08-06 | 2026-09-17 | yes |
| 7 | Management's stated cadence: "one or a couple of businesses to launch every single year for the next five years" (4Q24 call); "on pace to every year having at least a new business. I probably shouldn't say too much more beyond that for next year" (3Q25 call, answering TD Cowen on 2026 launches) | data/raw/transcripts/web/4Q24.html; 3Q25.html | 2025-11-06 | 2026-09-17 | yes |
| 8 | Release calendar from the letters: Summer Releases 24 May 2021, 11 May 2022, 3 May 2023, 1 May 2024, 13 May 2025, 20 May 2026; Winter Releases 9 Nov 2021, 16 Nov 2022, 8 Nov 2023, 16 Oct 2024; no Winter Release in 2025 (the Oct 2025 cancellation-policy and fee changes were newsroom posts); airbnb.com/release/2025-winter and /2026-winter return 404 | data/raw/letters/*.htm (query 4); curl HEAD (query 9) | 2026-09-17 | 2026-09-17 | yes |
| 9 | The Feb letter previews the year's launches but has never attached a growth number: 4Q24 letter previewed the May 2025 launch with the $200–250M cost; 4Q25 letter/call previewed the 20 May 2026 release and hotels ("share more about our approach later this year") | data/raw/letters/4Q24_d915198dex991.htm; 4Q25_d58192dex991.htm; data/raw/transcripts/web/4Q25.html | 2026-02-12 | 2026-09-17 | yes |
| 10 | Management declined to quantify new-business contribution when asked in 2024Q3, 2025Q2 (attach rate: "We don't have any numbers to share"), 2025Q3 (expected contribution next year), 2026Q2 (2027 margin: "not going to give you a specific guide for 2027 and beyond"); 37 declines in 23 calls | data/processed/abnb_declined_to_quantify.csv rows 22, 26, 31, 33 | 2026-08-06 | 2026-09-17 | yes |
| 11 | "Project Hawaii" innovation model makes attribution diffuse by design; the 2Q26 message was "collective actions", not a single product | docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §4 (12 Feb 2026 row); data/raw/transcripts/web/2Q26.html | 2026-08-06 | 2026-09-17 | yes |
| 12 | 1pt of FY27 nights ≈ $4.90/share (joint solve) or $1.50 (fixed multiple); 1pt of FY27 revenue growth ≈ $158M; FY27 margin per 1pt of revenue 0.66pp held / 0.42pp flex; FY27 EPS ≈ $0.0014 per $M of EBITDA | docs/pitch-forecasts/00_BRIEF.md sensitivities | 2026-09-16 | 2026-09-17 | yes |
| 13 | Sibling object: C05 log gives P(any quantification of the bundle's 3Q26 contribution at the 5 Nov print) = 0.27 (backward-looking, an existing product, one print) | docs/pitch-forecasts/questions/bundle-attribution-quantified/research-log.md §6 | 2026-09-17 | 2026-09-17 | no |
| 14 | Newsroom to 14 Sep 2026: no product announcement, no Winter Release date; "Airbnb launches new housing accelerator" (14 Sep), Rijvers CBO (1 Sep) | https://news.airbnb.com/ | 2026-09-14 | 2026-09-17 | no |
| 15 | No Polymarket or Kalshi market on Airbnb product announcements or guidance content | sources/polymarket_search_airbnb_20260917T034148Z.json; sources/kalshi_events_KXABNB_20260917T034148Z.json | 2026-09-17 | 2026-09-17 | no |
| 16 | Chesky teased "Airbnb's next chapter" on X for a 5 Mar 2026 reveal (off-cycle product communication exists; content not verified here) | https://stocktwits.com/news-articles/markets/equity/airbnb-ceo-brian-chesky-drops-cryptic-next-chapter-tease/chi8gaoRbZ7 | 2026-03-05 | 2026-09-17 | no |
| 17 | Final 72-hour recency check (query 12): Chesky CNBC/Goldman AI remarks, Icons collection, housing accelerator; no product with a number | WebSearch `Airbnb news this week` | 2026-09-17 | 2026-09-17 | no |

## 2. Query Log
1. [repo] `grep -n -i "multiples bigger|D053|major announcement|next year|roadmap|pricing"` on research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md; pandas dump of matching rows of data/processed/overnight2/D/rnpl_statement_ledger.csv
2. [repo] pandas dump of data/processed/margin_build/05_mgmt_statements_v2/05_statements.csv and 05_fy27_hints.csv rows containing 2026-09-08 / Communacopia (V017–V026, H07)
3. [repo] `grep -n -i "goldman|announce|2027|next year|hotel|experience|services"` on research/notes/q3nowcast/G_external-sources-q3-read.md and docs/margin-build/notes/05_mgmt_statements_v2.md
4. [repo] regex extraction of "Winter Release | Summer Release | Spring Update" passages from all 23 letters; §4 of docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md
5. [repo] regex scan of data/raw/transcripts/web/{4Q24,3Q25,4Q25,1Q26,2Q26}.html for "$1 billion | billion | hotel | pricing | next year | 2027 | percent of nights"
6. [repo] `grep` on research/notes/2026-09-04_abnb-pitch-landscape.md and _catalogue.md for release/quantification rows
7. [repo] pandas filter of data/processed/abnb_declined_to_quantify.csv for hotel|experience|service|pricing|2027
8. [repo] docs/pitch-forecasts/questions/bundle-attribution-quantified/research-log.md (C05) claims 1–8 and §6
9. [web] `curl -I` https://www.airbnb.com/release/2025-winter, /2026-winter, /2024-winter, /2026-summer
10. [WebFetch] https://news.airbnb.com/
11. [WebSearch] `Airbnb Winter Release 2026`
12. [WebSearch] `Chesky "major announcements" next year Airbnb 2027`
13. [WebSearch] `Airbnb AI pricing tool hosts 2026`
14. [WebFetch] Investing.com Goldman Communacopia 2026 transcript summary; StockTwits 5 Mar 2026 tease; CNBC 20 May 2026 (403)
15. [model] `python datasets/r08_model.py`
16. [WebSearch, final 72-hour recency] `Airbnb news this week`

## 3. Leading Hypothesis Entities
Airbnb, Brian Chesky, Ellie Mertz, 4Q26 shareholder letter, February 2027 call, AI pricing model, Reserve Now Pay Later, hotels, seller services, sponsored listings, Winter Release, Project Hawaii

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| A Winter Release (Oct/Nov 2026) launches a product and the 5 Nov letter attaches an expected 2027 contribution | kept, small (~0.05) | No Winter Release in 2025 and none announced for 2026 (claim 8); letters describe releases qualitatively; the two points-figures in the record were backward-looking (claim 1) |
| The Feb 2027 letter/call decomposes the FY27 revenue guide by driver ("including roughly X points from pricing / hotels") | kept, main route (~0.12 conditional) | Management gave backward points twice in 2026 and now has a pricing team it calls "many multiples bigger than RNPL" (claims 1, 6); against: it has never decomposed a forward guide by product, declined four direct requests (claim 10), and reframed to "collective actions" in 2Q26 (claim 11) |
| Chesky repeats "$1 billion incremental high margin revenue" (seller services) on the Feb call and dates it | kept inside the Feb route | Undated at Goldman (claim 4); a dated version is unlikely for a product not yet launched, and sponsored listings would be a take-rate lever whose GBV/nights contribution is nil |
| "Hundreds of millions" / "as much as Hawaii" style statements repeated for 2027 and counted by a lenient resolver | priced as a sensitivity (moves to 0.24), not in the headline | Convention 2 requires an explicit figure; such phrases appeared in 3 of the last 5 prints (claim 2), so the loose reading matters |
| Goldman/other conference remark with a number, no letter/call | discarded | Convention 1 (not a letter or call) |
| RNPL expansion to new booking types quantified for 2027 | kept inside the Feb route | RNPL global lap is a 1Q27 headwind management would rather not quantify; a forward RNPL figure has never been given (claim 1) |
| Negative quantification ("the lap will cost ~2 points") | discarded | The question requires "add"; a drag does not resolve Yes |

## 5. Independent Estimates
- base_rate_estimate: 0.08 — Explicit forward, dated, product-specific growth figures: 0 of 23 prints (claims 1–3); Laplace (0+1)/(23+2) = 0.04 per print, two prints in the window → 0.08. Regime check: management has become more numeric since 4Q25 (two backward points-figures, three order-of-magnitude forward phrases in five prints) but also reframed to "no one thing" in 2Q26; no numeric adjustment applied at this step.
- decomposition_estimate: 0.15 — `datasets/r08_model.py`: P(a new product or named 2027 rollout is announced by Feb) 0.92 (claims 4, 7, 9) × P(explicit ≥1pt / ≥$1bn-GBV-equivalent 2027 figure | named) = 1 − (1−0.05)(1−0.12) = 0.164 → 0.151 under the explicit-figure convention; 0.24 if order-of-magnitude phrases are counted.
- anchor_estimate: 0.27 — No market (claim 15). Nearest sibling object: C05's P(any quantification of the bundle at 5 Nov) = 0.27 (claim 13): a backward-looking figure for an existing product at one print. The gap to this question is forward-looking (never done), a new or 2027 product, and two prints; the first two cut, the third adds.
- anchor_value: 0.27
- final_estimate: 0.15
- final_minus_anchor: −0.12

Reconciliation: the base rate (0.08) is the record; the decomposition (0.15) adds the regime (Chesky's explicit 2027 promise, the pricing team, a Feb letter that guides FY27) and the two-print window; the anchor (0.27) is a looser object. The disagreement is the forward/backward distinction: management quantifies what a product *did* only when it flatters (4Q25, 1Q26) and has never quantified what a product *will* do. Final 0.15.

## 6. Final Numbers
**P(Yes) = 0.15**, credible interval 0.08–0.27.
Split: 5 Nov print ≈ 0.04; Feb print ≈ 0.11. Under a lenient resolver (order-of-magnitude phrases count): 0.24.
Extreme-probability gate: not triggered.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Explicit figure required (convention 2); if "hundreds of millions" / "as much as Hawaii" phrases count | 0.24 |
| P(number | named) at the Feb print 0.12; if the Feb letter decomposes the FY27 guide by driver (0.20) | 0.22 |
| P(number | named) at Feb; if the 2Q26 "no one thing" framing persists (0.06) | 0.10 |
| P(a lever is named by Feb) 0.92; if 0.75 | 0.12 |
| Conference remarks count as "call" (convention 1 reversed) | 0.20 (the $1bn seller-services figure would still need a 2027 date) |
| Joint bull (named 0.95, Nov 0.10, Feb 0.25, lenient) | 0.38 |
| Joint bear (named 0.8, Nov 0.03, Feb 0.06) | 0.07 |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-10-02 | Prelim memo freeze | Quote 0.15 (0.08–0.27) |
| 2026-10-01 to 11-04 | Any Winter Release / newsroom launch (2021–24 dates were 16 Oct–16 Nov) | A launch with a management number ("expected to drive X points in 2027") → resolve Yes only if repeated in the letter/call; raise to 0.35 on the announcement alone |
| 2026-11-05 | 3Q26 letter and call | A forward 2027 figure → Yes. A qualitative preview of 2027 launches only → 0.12. A backward bundle figure (C05 (a)/(b)) → 0.17 (management in a numeric mood) |
| 2027-01-15 | Sell-side previews of the FY27 guide; any Chesky interview naming 2027 products | Tone only; no move unless a number appears in company material |
| 2027-02-11 | 4Q26 letter and call: FY27 guide and 2027 launch preview | Resolve per conventions 1–4; a "pricing model expected to add approximately X points" or "$X of GBV in 2027" for a named product → Yes |

## 9. Impact
If Yes (management quantifies a ≥1pt 2027 lever), taken at face value for the impact table; the memo's own view of the lever's realism belongs in the thesis text:

| Item | Delta if Yes | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | a 2027 lever does not change the 3Q26 print |
| 4Q26 nights (pts) | 0 | as above (a Q4 launch could add a few tenths at most; not priced) |
| ADR (pts) | 0 | pricing-tool levers push ADR down, hotels dilute; sign ambiguous, held at 0 |
| 4Q26 revenue ($M) | 0 | as above |
| FY27 revenue ($M) | +158 (1pt of FY27 growth) | claim 12 |
| FY26 adj. EBITDA margin (pp) | 0 | launch cost, if any, lands in FY27 |
| FY27 adj. EBITDA margin (pp) | −0.3 (flex EBITDA on +$158M ≈ +$66M, less launch opex on the FY25 pattern; FY25's $200–250M was 1.7–2.0pp, a 2027 launch of half that size nets to about −0.3pp) | claims 3, 5, 12 |
| FY27 EPS ($) | 0.00 (range −0.10 to +0.09: +$66M × $0.0014 = +$0.09 gross, −$100M of launch cost = −$0.14) | claim 12 |
| Stock ($/share) | +4.9 (1pt of FY27 nights, joint solve: the multiple-growth channel is what a credible new lever moves) | claim 12 |
| EV = P × stock impact | 0.15 × $4.9 ≈ **+$0.7/share** | |
| Materiality | **Immaterial, borderline** (EV just under $1/share). Keep as one clause in the risks: "management may name a 2027 lever; it has never put a forward number on one." If the memo prefers the fixed-multiple sensitivity ($1.50/pt), EV is $0.2 | |
