# 42 — What moved ABNB after each print, and how much of it was margins

Written 22 Sep 2026. Companion file: `data/processed/margin_build/42_margin_reaction/42_event_reasons.csv` (23 prints, 4Q20-2Q26;
built by a one-off script from `abnb_earnings_reactions.csv`, `03_surprise_history.csv`, `03_consensus_at_dates.csv`, the shareholder
letters in `data/raw/letters/` and the call transcripts in `data/raw/transcripts/web/`, main repo tree). Returns are close-to-close from the
pre-print close, ABNB and ABNB minus QQQ. "FY revision" is the LSEG mean for the forward fiscal year (FY-next for November prints,
FY-current otherwise) five trading days after the print versus the day before. "Next-Q revision" (extra columns `nq_*`) is the same for the
quarter being guided. Press reads are cited by URL where a search was used (eight searches, none on airbnb.com).

## Every print with |day-1 move| >= 5%

| Print (reaction day) | ABNB / ex-QQQ | What drove it | Margin role | Evidence |
|---|---|---|---|---|
| 4Q20 (26 Feb 2021) | +13.3 / +12.9 | Revenue $859M vs ~$748M Street; rebound from -9.1% rates day | none | letter `4Q20_d147144dex991.htm`; margin guide only "lowest during Q1" |
| 3Q21 (5 Nov 2021) | +13.0 / +12.9 | Record quarter: EBITDA +35% vs Street at 49% margin, Q4 guide above Street; FY22 EBITDA consensus +16% | secondary (positive) | letter `3Q21_d245727dex991.htm`: "greater year-over-year ... margin expansion in Q4 2021 than ... Q3 2021" |
| 1Q22 (4 May 2022) | +7.7 / +4.3 | Q2 revenue guide 18% above Street, "low double-digit EBITDA margin ... improvement"; Fed-day rally, then -20% in five sessions (macro) | secondary (positive) | letter `1Q22_d711122dex991.htm` |
| 3Q22 (2 Nov 2022) | -13.4 / -10.0 | Q4 nights growth to "moderate slightly", revenue guide at/below Street, Fed +75bp same day. Q4 EBITDA consensus rose 3.5% | none | letter `3Q22_d408297dex991.htm`; CNBC 2 Nov 2022 |
| 4Q22 (15 Feb 2023) | +13.4 / +12.6 | Q1 revenue guide $1.75-1.82B vs $1.69B; Q1 EBITDA consensus +15%; flat-margin FY23 guide accepted | secondary (neutral) | letter `4Q22_d451233dex991.htm`; CNN 15 Feb 2023 |
| 1Q23 (10 May 2023) | -10.9 / -12.0 | Nights growth guided below revenue growth, ADR down (press); Q2 EBITDA consensus -13% on "400 basis points higher" S&M | secondary | letter `1Q23_d453262dex991.htm`; CNBC 9 May 2023 |
| 1Q24 (9 May 2024) | -6.9 / -7.1 | Q2 revenue guide $2.68-2.74B vs $2.74B, nights "stable"; Q2 EBITDA consensus -6.8% vs revenue -0.6%; FY24 unchanged | secondary | letter `1Q24_d813800dex991.htm`; CNBC 8 May 2024 |
| 2Q24 (7 Aug 2024) | -13.4 / -12.3 | Shorter lead times, "slowing demand from U.S. guests", Q3 revenue guide 3% below Street; Q3 margin to "decline" | secondary (co-driver) | letter `2Q24_d831385dex991.htm`; Bloomberg 6 Aug 2024 |
| 3Q24 (8 Nov 2024) | -8.7 / -8.8 | Q4 margin to "decline ... due to higher marketing and product development expenses"; S&M +27.5%, PD +25%; Q4 EBITDA consensus -9.6% with revenue 0.0% | **primary** | letter `3Q24_d886752dex991.htm`; call `3Q24.html` (Clarke: "27%-28%"); Benzinga 8 Nov 2024 |
| 4Q24 (14 Feb 2025) | +14.4 / +14.0 | EBITDA +17% and nights +12% vs Street; $200-250M new-business budget with a 34.5% floor at the Street's 34.46% | none (budget pre-priced) | letter `4Q24_d915198dex991.htm`; CNBC 14 Feb 2025 |
| 2Q25 (7 Aug 2025) | -8.0 / -8.4 | "tougher year-over-year comparison ... putting pressure on growth rates later in the year"; Q3/Q4 margin down YoY on "investments in new growth and policy initiatives". Consensus did not move (FY26 EBITDA +0.1%) | secondary | letter `2Q25_d17531dex991.htm`; Reuters/Investing.com 7 Aug 2025 |
| 2Q26 (7 Aug 2026) | +17.4 / +16.3 | Nights +10% accelerating, FY26 revenue "at least mid teens", margin floor 35.5%; FY26/FY27 EBITDA consensus +2.1/+2.6% | secondary (positive) | letter `2Q26_d70413dex991.htm`; Benzinga 7 Aug 2026 |

Press URLs: CNBC https://www.cnbc.com/2022/11/02/shares-of-airbnb-tumble-9percent-on-low-fourth-quarter-guidance.html; CNN
https://www.cnn.com/2023/02/15/business/airbnb-earning/index.html; CNBC https://www.cnbc.com/2023/05/09/airbnb-abnb-q1-earnings-report-2023.html;
CNBC https://www.cnbc.com/2024/05/08/airbnb-beats-earnings-expectations-for-first-quarter-but-offers-weaker-than-expected-guidance.html;
Bloomberg https://www.bloomberg.com/news/articles/2024-08-06/airbnb-gives-soft-outlook-on-signs-of-slowing-demand-from-us; Benzinga
https://www.benzinga.com/general/travel/24/11/41850614/airbnbs-margins-under-pressure-despite-q3-beat-analysts-caution; CNBC
https://www.cnbc.com/2025/02/14/airbnb-shares-pop-most-on-record-after-q4-earnings-beat.html; Reuters via
https://www.investing.com/news/stock-market-news/airbnb-forecasts-quarterly-revenue-above-estimates-plans-6-billion-share-buyback-4174361;
Benzinga https://www.benzinga.com/trading-ideas/movers/26/08/61045576/airbnb-stock-surges-after-strong-q2-results.

## Margin/cost-driven drops

Only one print survives an adversarial reading as margin-primary; two more are co-driven.

**3Q24, 8 Nov 2024, -8.7% (-8.8% ex-QQQ; -7.7% ex-QQQ over five days).** Reported: revenue $3,732M (+0.4% vs LSEG), adjusted EBITDA
$1,958M (+5.3% vs LSEG), margin 52.5% vs 54.0% a year earlier (-1.5pt); EPS $2.13 vs $2.14. Nothing in the print was a miss on growth:
nights beat, and Q4 nights growth was guided "higher than Q3 2024". The margin news was the whole story. The letter: "Q4 2024 Adjusted
EBITDA Margin is expected to decline relative to the same time period last year due to higher marketing and product development expenses"
and the FY24 margin narrowed to "approximately 35.5%" (from "at least 35%"). Bernstein's Clarke on the call computed the Q4 implication:
"somewhere in the 20s, around 27%-28%" against a Street Q4 margin of 29.9%. Mertz confirmed "a several-point margin compression relative to
last Q4 ... in terms of both the product development line item as well as marketing" and pre-announced the 2025 shape: "we will be adding
members to our teams and spending to our marketing to support these growth levers"; Chesky: "some of the investment behind those new
services will front-run the revenue". Consensus: Q4 2024 EBITDA -9.6% with Q4 revenue 0.0%; FY2025 EBITDA -2.1% with FY2025 revenue +0.5%
and FY2025 margin -0.92pt (35.83% to 34.91%). The cost lines the press quoted (S&M +27.5%, PD +25% YoY) are in the letter. Verdict:
margin_costs, primary.

**2Q24, 7 Aug 2024, -13.4% (-12.3%; -15.6% over five days).** Reported in line (EBITDA +3.7%, revenue +0.3%, margin flat YoY). The
headline was demand: "shorter booking lead times globally and some signs of slowing demand from U.S. guests", nights growth to
"moderate", Q3 revenue guide $3.67-3.73B against a $3,837M Street (-3.6% at the midpoint). But the margin leg was as large in the
numbers: "Adjusted EBITDA Margin to decline relative to Q3 2023 ... Marketing expense is expected to grow faster than revenue". Q3 EBITDA
consensus -7.7% = revenue -3.2% plus margin -2.5pt; FY2025 EBITDA -6.4% = revenue -2.5% plus margin -1.5pt. Roughly 60% of the forward
EBITDA cut came through margin. Growth news explains the sentiment (third downbeat guide in a row per Bloomberg); costs explain more than
half of the estimate cut. Verdict: both, margin secondary.

**1Q24, 9 May 2024, -6.9% (-7.1%; -10.6% over five days).** Reported beat (EBITDA +30% vs LSEG, margin +5.4pt YoY). Q2 revenue guide
$2.68-2.74B vs $2.74B Street and nights growth "relatively stable" (no acceleration) was the press read. The only consensus number that moved
materially was Q2 EBITDA (-6.8%, Street Q2 margin 33.5% to 31.4%) on "flat to up on a nominal basis, but down on an Adjusted EBITDA Margin
basis" with three stated causes: Easter reversal, "one-time payment processing incentive benefits impacting Q2 2023, and higher marketing
expense (partially due to timing)". FY2024 EBITDA consensus was unchanged (+0.3%) and the 35% floor was reiterated. The move was larger than
the estimate change; most of the quarter's margin cut was timing that management itself explained away. Verdict: both, margin secondary.

**2Q25, 7 Aug 2025, -8.0% (-8.4%; -6.9% over five days).** The candidate does not hold as margin-driven. Reported beat (EBITDA +7.4%,
revenue +2.0%, margin +1.2pt YoY). Q3 and Q4 margins were guided down YoY "primarily due to investments in new growth and policy
initiatives" and the budget was restated at "approximately $200 million", but consensus went up, not down: Q3 EBITDA +1.3%, FY2025 EBITDA
+0.8%, FY2026 EBITDA +0.1%, FY2026 margin -0.11pt. Reuters' read was "slower growth in second half"; the letter's line was "putting pressure
on growth rates later in the year", and Mertz declined to guide 2026 margins ("some of the investments this year will carry into next year as
fixed headcount"). This was a deceleration-narrative sell-off with a sticky-cost worry attached, not an estimate cut. Verdict: growth_guide,
margin secondary.

**1Q23, 10 May 2023, -10.9%** is the same shape as 1Q24: press read nights "lower than our revenue growth" and ADR down, but Q2 EBITDA
consensus fell 13% (Street Q2 margin -4.4pt) on "approximately 400 basis points higher" S&M while Q2 revenue consensus fell 0.3%; FY23
margin consensus moved -0.36pt because the full year was reiterated "broadly in-line with full-year 2022".

Pattern: in 1Q23, 1Q24, 2Q24 and 3Q24 the guided-quarter EBITDA consensus fell 7-13% while guided-quarter revenue consensus fell 0-3%.
Margin guidance is where the near-term numbers move; growth is what the press writes about.

## Counter-examples: margins guided down or a budget announced, stock up

- **4Q24, 14 Feb 2025, +14.4%.** The $200-250M new-business budget, the "at least 34.5%" floor (down from 36% delivered) and a Q1
  margin decline were all announced here. Best day ever because the Q4 beat was large (EBITDA +17%, nights +12% vs 108.7M expected) and
  the Street had already taken FY25 margin to 34.46% after the November drop; FY25 EBITDA consensus rose 1.7%. The budget was priced on
  8 Nov 2024, not 14 Feb 2025.
- **4Q25, 13 Feb 2026, +4.6% (+10.3% over five days).** FY26 margin guided "stable year-over-year" (~35.0%) against a 35.4% Street
  (Street cut 0.27pt), but revenue guided to "accelerate to at least low double digits" (FY26 revenue consensus +2.1%).
- **4Q23, 14 Feb 2024, -1.7%.** First "at least 35%" floor, ~1.6pt below the Street; the Street cut only 0.25pt. A floor without a
  named budget is discounted.
- **4Q21, 16 Feb 2022, +3.6%.** FY22 margin "directionally in-line with 2021"; stock up on the Q1 guide.
- Reverse case: **2Q22, 3 Aug 2022, -1.1% (-3.9% ex-QQQ)** with Q3 EBITDA consensus +9.8% and FY22 margin consensus +2.6pt on
  "at or slightly below last year's all-time high margin of 49%". Good margin news did not lift a stock with "stable" nights growth.

## What management says in November about next year

- **3Q21 (Nov 2021).** Letter: nothing on FY22 margin; "Looking to 2022 ... We continue to expect ADR to moderate over time". Call
  (Stephenson): marketing as % of revenue "in this kind of range for the foreseeable future". **Feb 2022 guide:** "Adjusted EBITDA margin to
  be directionally in-line with 2021 ... potentially offset by lower ADR". Delivered FY22 margin was up ~8pt.
- **3Q22 (Nov 2022).** Letter: nothing on 2023 margin. Call (Stephenson): "as average daily rates could moderate next year, that does put a
  little bit of headwind towards our margins"; Chesky on Experiences: "I don't think you'll see that in the P&L from a cost perspective next
  year at all". **Feb 2023 guide:** "maintain the strong Adjusted EBITDA margin we delivered in 2022, as we offset the headwinds from lower ADR
  with incremental variable cost efficiencies and fixed cost discipline"; headcount "2%, 3%, 4%". FY23 delivered ~150bp higher.
- **3Q23 (Nov 2023).** Letter: FY23 margin "approximately 150 bps higher than full-year 2022"; nothing on 2024. Call (Stephenson): "early
  visibility into 2024 is, again, it's too early to tell"; headcount "approximately 4%". **Feb 2024 guide:** "at least 35%" floor, "slightly
  down from what we delivered in 2023 ... flexibility ... to invest"; no dollar budget. FY24 delivered 35.5%.
- **3Q24 (Nov 2024).** Letter: FY24 "approximately 35.5%", Q4 margin down on "higher marketing and product development expenses", and
  "We're excited to share more about our 2025 growth and investment plans early next year". Call (Mertz): "we will be adding members to our
  teams and spending to our marketing"; (Chesky): "some of the investment behind those new services will front-run the revenue".
  **Feb 2025 guide:** "$200 million to $250 million towards launching and scaling new businesses ... at least 34.5%", impact "most pronounced
  during the first nine months of 2025". FY25 delivered ~35%.
- **3Q25 (Nov 2025).** Letter and call: "As we look forward to 2026, we are focused on maintaining strong margins while continuing to invest
  in growth initiatives"; Mertz on the call: "we do not have the same heaviness of the kind of first-year launch ... across experience and
  services, across hotels, across AI, we will be investing in those next year". **Feb 2026 guide:** "Adjusted EBITDA Margin to be stable
  year-over-year as we reinvest top-line efficiencies ... primarily in marketing, product, and technology". Raised to "at least 35%" in May and
  "at least 35.5%" in August 2026.

Conclusion. Management never gives a next-year margin number in November. A lower-margin year is signalled one quarter early by three
tells: (1) a named cost line growing faster than revenue in the guided quarter ("higher marketing and product development expenses",
Nov 2024); (2) "investment plans" attached to next year ("share more about our 2025 growth and investment plans", Nov 2024); (3) a CFO
answer that spend "will carry into next year" (Aug/Nov 2025). When November says only "maintaining strong margins" (Nov 2023, Nov 2025),
February brings a floor at or slightly below the prior year with no dollar budget and the Street cuts 0.2-0.3pt. The one February with a
dollar budget (2025) followed tells (1) and (2) together, and the stock had paid for it in November (-8.7%). For 5 Nov 2026 the test is
whether the letter names a Q4 cost line and whether "2027 investment plans" appears; "maintaining strong margins" alone maps to a
roughly flat FY27 floor in February.

## Limitations

Consensus revisions over five sessions mix the guidance with analysts reacting to the stock, so revision size is not a clean measure of news.
The LSEG series starts at the 1Q21 print, so 4Q20 has no surprise or next-quarter revision and the 1Q21 prior-year margin is not in the
sources (left blank). Analyst-question counts are my reading of the transcripts (a keyword filter then a manual pass), not a coded ontology;
another reader would land within +/-1 per call. Press reads come from one search per event and were not cross-checked across outlets;
3Q21 and 4Q20 have no same-day press source, only the repo's hand-transcribed big-moves file. Driver labels are judgement calls; the
numbers that support them are in the CSV so the labels can be re-cut. Nothing here is a backtest: n = 12 big moves.

## RESUME

The CSV is complete (23 rows) and the note is written; neither is committed. Next agent: (1) fold the `nq_*` columns into the 42 R1/R2
regressions pre-registered in `41_42_prereg.md` (guided-quarter EBITDA revision looks like a stronger day-1 regressor than the FY NTM blend);
(2) check the 2Q24 margin-vs-revenue decomposition against the LSEG Q3 2024 line items; (3) at the 5 Nov 2026 print, score the three November
tells above against the letter text before reading the number.
