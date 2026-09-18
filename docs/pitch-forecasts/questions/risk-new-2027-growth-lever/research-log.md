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
- revision: 2
- revised: 2026-09-17
- agent: fable
- batch: A11 (with R06 and R09)
- audit: `docs/pitch-forecasts/audits/A11-research-audit.md` (independent Opus auditor standing in for Codex); response `docs/pitch-forecasts/audits/A11-audit-response.md`

## 0b. Question (verbatim)
### Title
By the Feb print, will management announce and quantify a new product or pricing initiative expected to add ≥1 point to 2027 nights or GBV growth?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if a letter or call gives a numeric expected contribution (≥1pt, or ≥$1bn GBV) for a product launched or announced after 16 Sep 2026 (or a named 2027 rollout, e.g., RNPL for new booking types, a new payment product, an AI booking agent, hotels at scale). Resolution ~11 Feb 2027.
### Fine Print
(none in the registry.) Conventions adopted here and forecast under:
1. "Letter or call" = the 3Q26 and 4Q26 shareholder letters, the two earnings calls (prepared remarks and Q&A) and any 8-K/10-Q/10-K text; investor-conference remarks (Goldman, Morgan Stanley) do not count. Priced separately in §7.
2. "Numeric expected contribution" = an explicit figure or explicit bound ("approximately 1 point", "over 100 basis points", "at least $1 billion of GBV", "$300 million of revenue in 2027"). Order-of-magnitude phrases ("hundreds of millions", "as much as Hawaii", "multi-billion opportunity", "many multiples of RNPL") do not count. (Revision 2, A11-07) A revenue figure converts to GBV at the trailing take rate (13.4%) **only for revenue earned on bookings that pass through GBV and Nights and Seats Booked** (stays, hotels, Experiences, Services, RNPL-enabled bookings); an explicit 2027 revenue figure ≥$135M for such a product qualifies. Revenue from pure take-rate or advertising levers that add no bookings (seller services, sponsored listings, host tooling fees, a fee change) does not convert and does not count, because the question asks about nights or GBV growth. A nights figure qualifies at ≥1 point.
3. "Expected to add to 2027" = the statement must be forward-looking and tied to 2027 (or "next year" said in 2026, or the FY27 guide). A backward-looking attribution ("delivered 3 points in Q1") does not count; an undated opportunity ("a $1 billion business in three to five years") does not count.
4. The product must be launched or announced after 16 Sep 2026, or be a named 2027 rollout of an existing product (the RNPL, payments, AI-agent and hotels examples in the criteria). The May 2026 Summer Release products (car rentals, groceries, hotels in 20 cities) count only if the statement is about their 2027 expansion.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | In 23 prints (4Q20–2Q26) a product contribution stated in points of nights or GBV appears exactly twice, both backward-looking: 4Q25 call "over 200 basis points of growth in nights booked and roughly 300 basis points of growth in GBV in Q4"; 1Q26 call "approximately three points of nights booked growth and approximately four points of GBV growth in Q1". The 2Q26 call gave no figure ("there is no one thing") | data/raw/transcripts/web/4Q25.html; 1Q26.html; 2Q26.html; docs/pitch-forecasts/questions/bundle-attribution-quantified/research-log.md claims 1–3, 6 | 2026-08-06 | 2026-09-17 | yes |
| 2 | Forward-looking product statements with any number, all prints and conferences 2023–26 (10 rows): none is an explicit figure tied to a year for a growth metric. Closest: 4Q24 call "a great business could get to $1 billion of revenue" (3–5 years, undated); 4Q25 call "Project Y will deliver hundreds of millions more this year" and "pricing initiatives will drive as much revenue this year as Hawaii"; 1Q26 call "payments and pricing roadmap ... hundreds of millions of dollars in revenue each year"; GS26 "$1 billion incremental high margin revenue" (seller services, undated, conference) | datasets/forward_product_quantification_history.csv (from data/raw/transcripts/web/*.html and 05_statements.csv) | 2023-03-07 to 2026-09-08 | 2026-09-17 | yes |
| 3 | The only dated, numeric forward product statement in the record is a cost: FY25 new-business investment "$200–250M" (4Q24 letter, 13 Feb 2025) | data/raw/letters/4Q24_d915198dex991.htm; docs/margin-build/notes/05_mgmt_statements_v2.md (V012) | 2025-02-13 | 2026-09-17 | yes |
| 4 | Chesky, Goldman Communacopia 8 Sep 2026: "We're going to have some major announcements next year. I can't share too much except to say that I think I want to shift Airbnb from a marketplace to much more of a community." (V023). Also "straight shot to $1 billion incremental high margin revenue" for seller services (V022), sponsored listings named. (Revision 2) Under convention 2 as corrected, a dated version of the seller-services figure would not count: it is a take-rate lever with no GBV or nights contribution | https://www.investing.com/news/transcripts/airbnb-at-goldman-sachs-conference-chesky-sees-wider-runway-93CH-4892583 ; data/processed/margin_build/05_mgmt_statements_v2/05_statements.csv | 2026-09-08 | 2026-09-17 | yes |
| 5 | The margin build's hint H07 reads V023 as launch cost before revenue in FY27 ("the S100 pattern"), no budget given; FY25's launch cost $200–250M | data/processed/margin_build/05_mgmt_statements_v2/05_fy27_hints.csv (H07) | 2026-09-15 | 2026-09-17 | no |
| 6 | 2Q26 call, Chesky on pricing: "We are essentially building an entirely new pricing model ... powered by AI ... a new pricing model that we're rolling out"; "many multiples bigger than RNPL" (D053); the CFO: "the single service fee ... allows us to provide more simplified pricing recommendations" | data/raw/transcripts/web/2Q26.html; data/processed/overnight2/D/rnpl_statement_ledger.csv D053 | 2026-08-06 | 2026-09-17 | yes |
| 7 | Management's stated cadence: "one or a couple of businesses to launch every single year for the next five years" (4Q24 call); "on pace to every year having at least a new business. I probably shouldn't say too much more beyond that for next year" (3Q25 call, answering TD Cowen on 2026 launches) | data/raw/transcripts/web/4Q24.html; 3Q25.html | 2025-11-06 | 2026-09-17 | yes |
| 8 | Release calendar from the letters: Summer Releases 24 May 2021, 11 May 2022, 3 May 2023, 1 May 2024, 13 May 2025, 20 May 2026; Winter Releases 9 Nov 2021, 16 Nov 2022, 8 Nov 2023, 16 Oct 2024; no Winter Release in 2025 (the Oct 2025 cancellation-policy and fee changes were newsroom posts); airbnb.com/release/2025-winter and /2026-winter return 404 | data/raw/letters/*.htm (query 4); curl HEAD (query 9) | 2026-09-17 | 2026-09-17 | yes |
| 9 | The Feb letter previews the year's launches but has never attached a growth number: 4Q24 letter previewed the May 2025 launch with the $200–250M cost; 4Q25 letter/call previewed the 20 May 2026 release and hotels ("share more about our approach later this year"). 0 of 6 Feb letters (4Q20–4Q25) carry a forward product growth figure | data/raw/letters/4Q24_d915198dex991.htm; 4Q25_d58192dex991.htm; data/raw/transcripts/web/4Q25.html | 2026-02-12 | 2026-09-17 | yes |
| 10 | Management declined to quantify new-business contribution when asked in 2024Q3, 2025Q2 (attach rate: "We don't have any numbers to share"), 2025Q3 (expected contribution next year), 2026Q2 (2027 margin: "not going to give you a specific guide for 2027 and beyond"); 37 declines in 23 calls | data/processed/abnb_declined_to_quantify.csv rows 22, 26, 31, 33 | 2026-08-06 | 2026-09-17 | yes |
| 11 | "Project Hawaii" innovation model makes attribution diffuse by design; the 2Q26 message was "collective actions", not a single product | docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md §4 (12 Feb 2026 row); data/raw/transcripts/web/2Q26.html | 2026-08-06 | 2026-09-17 | yes |
| 12 | 1pt of FY27 nights ≈ $4.90/share (joint solve) or $1.50 (fixed multiple); 1pt of FY27 revenue growth ≈ $158M (the brief's convention: 1% of FY27 line-build revenue $15,829M; one point of growth applied to the FY26 base $14,268M would be $143M — revision 2, A11-20); FY27 margin per 1pt of revenue 0.66pp held / 0.42pp flex; FY27 EPS ≈ $0.0014 per $M of EBITDA; line build FY27 adj. EBITDA $5,483M, margin 34.64% | docs/pitch-forecasts/00_BRIEF.md sensitivities; docs/margin-build/SYNTHESIS.md §3 annual table | 2026-09-16 | 2026-09-17 | yes |
| 13 | Sibling object (revision 2, A11-08): C05 revision 2 gives P(any quantification of the bundle's 3Q26 contribution at the 5 Nov print) = 0.28 (vector a 0.07 / b 0.11 / c 0.10 / d 0.72), with its own anchor null (NO_EXTERNAL_ANCHOR). A backward-looking figure for an existing product at one print; produced by this run, not an external anchor | docs/pitch-forecasts/questions/bundle-attribution-quantified/forecasts/2026-09-17-forecast.json (revision 2) | 2026-09-17 | 2026-09-17 | no |
| 14 | Newsroom snapshot saved 2026-09-17T13:22Z (revision 2, A11-24): latest items "Airbnb launches new housing accelerator" (14 Sep), Rijvers CBO (1 Sep); no product announcement, no Winter Release date, no product with a number in the snapshot | sources/newsroom_news.airbnb.com_20260917T132231Z.html | 2026-09-14 | 2026-09-17 | no |
| 15 | No Polymarket or Kalshi market on Airbnb product announcements or guidance content | sources/polymarket_search_airbnb_20260917T034148Z.json; sources/kalshi_events_KXABNB_20260917T034148Z.json | 2026-09-17 | 2026-09-17 | no |
| 16 | Chesky teased "Airbnb's next chapter" on X for a 5 Mar 2026 reveal (off-cycle product communication exists; content not verified here) | https://stocktwits.com/news-articles/markets/equity/airbnb-ceo-brian-chesky-drops-cryptic-next-chapter-tease/chi8gaoRbZ7 | 2026-03-05 | 2026-09-17 | no |
| 17 | Final 72-hour recency check (query 16): no relevant result in the searches recorded (Chesky CNBC/Goldman AI remarks, Icons collection, housing accelerator; none with a product number) (revision 2, A11-24 wording) | WebSearch `Airbnb news this week` (sources/web_search_log.md) | 2026-09-17 | 2026-09-17 | no |
| 18 | (Revision 2) Base-rate classes: all prints 0/23 → Laplace 0.040 per print, two prints 0.078; prints since the new-business strategy was announced (4Q24–2Q26) 0/7 → 0.111 per print, two prints 0.210; Feb letters 0/6 → 0.125; 3Q prints 0/5 → 0.143. No 3Q call has ever given a forward next-year product number (regex over the 3Q22–3Q25 transcripts: the only hit is an analyst's question about the $200M proving sticky), and the 3Q letter carries no annual guide | datasets/r08_model_v2.py output; data/raw/transcripts/web/3Q22–3Q25.html (query 18) | 2026-09-17 | 2026-09-17 | yes |
| 19 | (Revision 2, A11-06, A11-21) Impact arithmetic from the line build: +$158M of FY27 revenue at the 0.42 flex rate = +$66M of EBITDA; launch opex at half of FY25's $200–250M = $100–125M ($112M midpoint) → FY27 EBITDA $5,437M on $15,987M = 34.01%, −0.63pp vs 34.64%; EPS −$0.064 (net EBITDA −$46M × $0.0014). The EBITDA dollar change is −$46M, not the −$100M a naive reading of the 0.63pp would suggest, because the denominator grew at a below-average incremental margin; capitalised at the market's ~18x FY27 EBITDA ($99bn / $5,483M) over 590m shares the debit is −$1.40/share | datasets/r08_v2_impact.csv; docs/margin-build/SYNTHESIS.md §3 | 2026-09-17 | 2026-09-17 | yes |
| 20 | (Revision 2, A11-25) Coherence: R09's FY27-revenue route (a company statement of FY27 revenue ≥$500M for hotels, Experiences or Services, 0.03) implies R08 = Yes under convention 2 (booking-generating revenue at 13.4% → ≥$3.7bn of GBV); 0.03 ≤ 0.13 holds | docs/pitch-forecasts/questions/risk-new-businesses-quantified-material/forecasts/2026-09-17-forecast.json | 2026-09-17 | 2026-09-17 | no |

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
17. [repo, revision 2] `py -3.13 -B docs/pitch-forecasts/audits/A11-reproduce.py` (tree replay, Laplace classes, impact arithmetic on the line build); docs/margin-build/SYNTHESIS.md lines 295–310 (annual table)
18. [repo, revision 2] regex over data/raw/transcripts/web/3Q22–3Q25.html for "(next year|2023|2024|2025|2026) … (point|percent|billion|million)" (forward next-year numbers at 3Q prints)
19. [repo, revision 2] docs/pitch-forecasts/questions/bundle-attribution-quantified/forecasts/2026-09-17-forecast.json (C05 revision 2: p_any_quantification 0.28, anchor null)
20. [web, revision 2] `curl -sL https://news.airbnb.com/` saved to sources/newsroom_news.airbnb.com_20260917T132231Z.html
21. [model, revision 2] `py -3.13 datasets/r08_model_v2.py` (outputs r08_v2_summary.csv, r08_v2_sensitivity.csv, r08_v2_impact.csv)

## 3. Leading Hypothesis Entities
Airbnb, Brian Chesky, Ellie Mertz, 4Q26 shareholder letter, February 2027 call, AI pricing model, Reserve Now Pay Later, hotels, seller services, sponsored listings, Winter Release, Project Hawaii

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| A Winter Release (Oct/Nov 2026) launches a product and the 5 Nov letter attaches an expected 2027 contribution | kept, small (~0.03) | No Winter Release in 2025 and none announced for 2026 (claim 8); letters describe releases qualitatively; the 3Q letter carries no annual guide and no 3Q call has ever given a forward next-year product number (claim 18); the two points-figures in the record were backward-looking (claim 1) |
| The Feb 2027 letter/call decomposes the FY27 revenue guide by driver ("including roughly X points from pricing / hotels") | kept, main route (~0.10 conditional; revision 2, was 0.12) | Management gave backward points twice in 2026 and now has a pricing team it calls "many multiples bigger than RNPL" (claims 1, 6); against: it has never decomposed a forward guide by product, declined four direct requests (claim 10), reframed to "collective actions" in 2Q26 (claim 11), and 0 of 6 Feb letters carry such a figure (claim 9) |
| Chesky repeats "$1 billion incremental high margin revenue" (seller services) on the Feb call and dates it | discarded as a Yes route (revision 2, A11-07) | Seller services and sponsored listings are take-rate levers with no GBV or nights contribution; under convention 2 as corrected a dated figure does not convert. Removing this route is the −0.02 on the Feb conditional |
| "Hundreds of millions" / "as much as Hawaii" style statements repeated for 2027 and counted by a lenient resolver | priced as a sensitivity (moves to 0.21), not in the headline | Convention 2 requires an explicit figure; such phrases appeared in 3 of the last 5 prints (claim 2), so the loose reading matters |
| Goldman/other conference remark with a number, no letter/call | discarded | Convention 1 (not a letter or call) |
| RNPL expansion to new booking types quantified for 2027 | kept inside the Feb route | RNPL global lap is a 1Q27 headwind management would rather not quantify; a forward RNPL figure has never been given (claim 1) |
| Hotels at scale quantified for 2027 ("hotels expected to add about a point") | kept inside the Feb route | A booking-generating lever that does convert; hotels grow ~3x homes (R09 claim 1) so a point is arithmetically available at a 3–4% share; against: management has kept the share itself in a bucket (R09) |
| Negative quantification ("the lap will cost ~2 points") | discarded | The question requires "add"; a drag does not resolve Yes |

## 5. Independent Estimates
- base_rate_estimate: 0.08 — Explicit forward, dated, product-specific growth figures: 0 of 23 prints (claims 1–3); Laplace (0+1)/(23+2) = 0.04 per print, two prints in the window → 0.08. Regime classes (claim 18): the 7 prints since the new-business strategy 0/7 → 0.21 over two prints (upper reading; every one of those prints had something to quantify and none did); Feb-letter class 0/6 → 0.125 for the Feb print alone. The all-print 0.08 is reported as the base rate; the regime classes bracket it at 0.08–0.21 and are the reason the elicitation below is not lower.
- decomposition_estimate: 0.12 — Judgmental elicitation, not a data decomposition (revision 2, A11-22; `datasets/r08_model_v2.py`): P(a new product or named 2027 rollout is announced by Feb) 0.92 (claims 4, 7, 9; it scales the answer by at most 1.3 points) × P(explicit ≥1pt / ≥$1bn-GBV-equivalent 2027 figure | named) = 1 − (1−0.035)(1−0.10) = 0.1315 → 0.121. The two conditionals are judgements: November 0.035 because a 3Q letter carries no annual guide and no 3Q call has ever previewed the next year numerically (claim 18), so it sits just below the all-print Laplace; February 0.10 because the Feb letter always previews the year and now carries an FY27 guide, management gave two backward points-figures in 2026 and calls the pricing programme "many multiples bigger than RNPL" (claims 1, 6, 9), against a 0-of-6 Feb record (Laplace 0.125) and the corrected convention 2 removing the seller-services route (A11-07, −0.02). Lenient resolver (order-of-magnitude phrases count): 0.21.
- anchor_estimate: none — No market (claim 15). The revision-1 anchor (C05 at 0.27) was another forecast from this run, stale (C05 revision 2 is 0.28) and not independent of this run's disclosure priors (A11-08); it is withdrawn as an anchor and kept as a labelled sibling comparison (claim 13): a backward-looking figure for an existing product at one print, a looser object than this question's forward, new-or-2027, two-print object. The three-estimate requirement of the skill is unmet: two internal estimates and no external anchor.
- anchor_value: n/a (NO_EXTERNAL_ANCHOR)
- final_estimate: 0.13
- final_minus_anchor: n/a. Against the sibling comparisons: 0.00 vs the audit's independent 0.13 (its tree 1 − 0.97 × 0.90 = 0.127 sits inside this model at 0.127 with p_named 1.0); −0.02 vs revision 1; −0.15 vs C05 revision 2's 0.28 (a different, looser object).

Reconciliation: the base rate (0.08) is the record; the elicitation (0.12) adds the regime (Chesky's explicit 2027 promise, the pricing team, a Feb letter that guides FY27) and sits between the all-print and Feb-class Laplace readings. The disagreement is the forward/backward distinction: management quantifies what a product *did* only when it flatters (4Q25, 1Q26) and has never quantified what a product *will* do. Final 0.13 (the elicitation rounded up toward the Feb-class Laplace 0.125 and the regime class 0.21).

## 6. Final Numbers
**P(Yes) = 0.13**, credible interval 0.06–0.24.
Split: 5 Nov print ≈ 0.03; Feb print ≈ 0.10. Under a lenient resolver (order-of-magnitude phrases count): 0.21.
Extreme-probability gate: not triggered.
Coherence (claim 20): R09's FY27-revenue route (0.03) ≤ R08 (0.13); R06 independent.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Explicit figure required (convention 2); if "hundreds of millions" / "as much as Hawaii" phrases count | 0.21 |
| Convention 2 restricted to booking-generating revenue; if take-rate revenue (seller services) converts as in revision 1 (Feb 0.12) | 0.14 |
| P(number \| named) at the Feb print 0.10; if the Feb letter decomposes the FY27 guide by driver (0.20) | 0.21 |
| P(number \| named) at Feb; if the 2Q26 "no one thing" framing persists (0.06) | 0.09 |
| P(number \| named) at the Nov print 0.035; if 0.05 (revision 1) | 0.13 |
| P(a lever is named by Feb) 0.92; if 0.75 | 0.10 |
| Conference remarks count as "call" (convention 1 reversed) | 0.15 (the $1bn seller-services figure would still fail conventions 2 and 3) |
| Auditor's tree (named 1.0, Nov 0.03, Feb 0.10) | 0.13 |
| Joint bull (named 0.95, Nov 0.08, Feb 0.22, lenient) | 0.35 |
| Joint bear (named 0.8, Nov 0.02, Feb 0.05) | 0.06 |

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-10-02 | Prelim memo freeze | Quote 0.13 (0.06–0.24) |
| 2026-10-01 to 11-04 | Any Winter Release / newsroom launch (2021–24 dates were 16 Oct–16 Nov) | A launch with a management number ("expected to drive X points in 2027") → resolve Yes only if repeated in the letter/call; raise to 0.35 on the announcement alone |
| 2026-11-05 | 3Q26 letter and call | A forward 2027 figure for a booking-generating lever → Yes. A qualitative preview of 2027 launches only → 0.11. A backward bundle figure (C05 (a)/(b)) → 0.15 (management in a numeric mood). A seller-services / sponsored-listings figure alone → no move (convention 2) |
| 2027-01-15 | Sell-side previews of the FY27 guide; any Chesky interview naming 2027 products | Tone only; no move unless a number appears in company material |
| 2027-02-11 | 4Q26 letter and call: FY27 guide and 2027 launch preview | Resolve per conventions 1–4; a "pricing model expected to add approximately X points" or "$X of GBV in 2027" for a named product → Yes |

## 9. Impact
If Yes (management quantifies a ≥1pt 2027 lever), taken at face value for the impact table; the memo's own view of the lever's realism belongs in the thesis text. Launch-cost assumption named (revision 2, A11-06): $100–125M of FY27 launch opex, half of FY25's $200–250M (claim 3), midpoint $112M.

| Item | Delta if Yes | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | a 2027 lever does not change the 3Q26 print |
| 4Q26 nights (pts) | 0 | as above (a Q4 launch could add a few tenths at most; not priced) |
| ADR (pts) | 0 | pricing-tool levers push ADR down, hotels dilute; sign ambiguous, held at 0 |
| 4Q26 revenue ($M) | 0 | as above |
| FY27 revenue ($M) | +158 (1pt of FY27 growth, the brief's convention = 1% of FY27 line-build revenue; $143M on the FY26 base) | claim 12 |
| FY26 adj. EBITDA margin (pp) | 0 | launch cost, if any, lands in FY27 |
| FY27 adj. EBITDA margin (pp) | −0.6 (range −0.55 to −0.71: flex EBITDA on +$158M ≈ +$66M, less $100–125M of launch opex → 34.01–34.09% vs 34.64%) | claims 3, 12, 19; `datasets/r08_v2_impact.csv` |
| FY27 EPS ($) | −0.06 (range −0.05 to −0.08; net EBITDA −$34M to −$59M × $0.0014; +$0.09 with no launch cost) | claims 12, 19 |
| Stock ($/share) | +3.5 = growth credit +4.9 (1pt of FY27 nights, joint solve: the multiple-growth channel is what a credible new lever moves) less margin debit −1.4 (net EBITDA −$46M capitalised at ~18x over 590m shares) (revision 2, A11-21) | claims 12, 19 |
| EV = P × stock impact | 0.13 × $3.5 ≈ **+$0.5/share** | |
| Materiality | **Immaterial** (EV < $1/share; under the fixed-multiple sensitivity the net is +$0.1/share and EV ≈ 0). Keep as one clause in the risks: "management may name a 2027 lever; it has never put a forward number on one, and a launch year costs margin before it adds revenue." | |

## 10. Revision notes
| Change | Finding |
|---|---|
| Metadata: revision 2, revised 2026-09-17; audit and response paths added | — |
| Convention 2: revenue-to-GBV conversion restricted to booking-generating revenue; take-rate and advertising revenue excluded; §4 seller-services route discarded; Feb conditional 0.12 → 0.10 | A11-07 |
| §5 decomposition relabelled a judgmental elicitation; reasoning for the 0.035 / 0.10 conditionals written out; November 0.05 → 0.035 (3Q letter carries no annual guide; no 3Q call has ever previewed next year numerically, claim 18) | A11-22 |
| Anchor withdrawn (NO_EXTERNAL_ANCHOR); C05 revision 2 (0.28) kept as a labelled sibling comparison (claim 13); three-estimate requirement stated unmet; \|final − anchor\| no longer reported against C05 | A11-08 |
| Claim 18 added: base-rate classes (all prints 0/23, regime 0/7, Feb letters 0/6, 3Q prints 0/5) and the 3Q-call check | audit missed (see response) |
| §9: FY27 margin −0.3 → −0.6pp; EPS 0.00 → −$0.06; launch-cost assumption named; stock shown as growth credit +4.9 and margin debit −1.4 (net +3.5); EV +$0.7 → +$0.5; the debit capitalises the EBITDA dollar change (−$46M), not the margin-pp change | A11-06, A11-21 (accepted in part) |
| Claim 12: the $158M convention stated (1% of FY27 revenue; $143M on the FY26 base) | A11-20 |
| Claim 20 and §6: coherence with R09's FY27-revenue route recorded | A11-25 |
| Claims 14 and 17: newsroom snapshot saved; "no relevant result in the searches recorded" wording | A11-24 |
| §6: P(Yes) 0.15 → 0.13, interval 0.08–0.27 → 0.06–0.24; lenient 0.24 → 0.21; §7 rebuilt from `r08_v2_sensitivity.csv`; §8 November branches updated | A11-07, A11-22 |
| Queries 17–21 appended; `datasets/r08_model_v2.py`, `r08_v2_summary.csv`, `r08_v2_sensitivity.csv`, `r08_v2_impact.csv` added (revision-1 files untouched) | — |
