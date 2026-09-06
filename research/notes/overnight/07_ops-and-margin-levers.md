# ABNB operational levers, peer benchmarks and a lever-by-lever margin model to FY2028

- **Workstream:** 07 (overnight run, 6-7 Sep 2026). **Date:** 2026-09-06. **Author:** Krishang Surapaneni (compiled with Claude Code).
- **Builds on, does not replace:** `research/notes/2026-09-05_margin-drivers.md` (cost stack, bridge, FY26/27 scenarios, FCF bridge, BKNG head-to-head) and `research/notes/2026-09-05_capital-return-panel.md`. Where this note disagrees with those, it says so under "Corrections to existing work".
- **Files written**
  - `analysis/src/overnight/07_cost_lines_per_night.py` -> `data/processed/overnight/07_cost_lines_per_night.csv` (22 quarters, 1Q21-2Q26) and `07_cost_components_annual.csv` (FY2019-FY2025 disclosed components)
  - `analysis/src/overnight/07_ops_initiatives.py` -> `data/processed/overnight/07_ops_initiatives.csv` (22 initiatives, scored)
  - `analysis/src/overnight/07_peer_benchmark.py` -> `data/processed/overnight/07_peer_margin_benchmark.csv` (10 companies x FY2021-FY2025)
  - `analysis/src/overnight/07_margin_lever_model.py` -> `data/processed/overnight/07_margin_levers_fy26_fy28.csv` (levers, per-lever attribution, results, reconciliation, path-to-40%)
- **Sources:** SEC XBRL company facts (10 tickers), every ABNB 10-K FY2020-FY2025 and 10-Q 1Q23-2Q26 (MD&A results-of-operations narrative, sales-and-marketing split table, Note 13 commitments, Item 1 headcount), all 23 shareholder letters, IR call transcripts 2023-Q1 to 2026-Q2, and the team's existing processed CSVs.

---

## 1. Bottom line

1. **Since 2022 Airbnb has spent every efficiency it found, and it has spent it on marketing.** On a same-quarter cash basis, Q2 2022 to Q2 2026: revenue per night rose $4.04 (from $20.29 to $24.33) and cash cost per night rose $2.44 (from $13.49 to $15.93). Of that $2.44, **$2.08, or 85%, is sales and marketing** ($1.18 brand and performance, $0.90 field operations). Operations and support fell $0.14 and G&A fell $0.29; product development rose $0.30 and cost of revenue rose $0.51 (it scales with GBV, and ADR rose). The Adjusted EBITDA margin moved from 33.8% to 35.0%. The whole four-year margin story is: ADR paid for a marketing ramp, and the AI support savings are real but roughly a tenth of the size.

2. **The 2026 spending mix is different from the 2025 one and the existing note has it the wrong way round.** In FY2025 the S&M growth was field operations and policy (+43% to $993M) while brand and performance marketing grew 10%. In 1H 2026 that reversed: **brand and performance marketing +32% ($1,091M vs $824M) and field operations +24%**. The 2026 ramp is paid media in emerging markets and partnerships, not new-business go-to-market. That matters because media spend is discretionary quarter to quarter and reversible; field-operations headcount is not.

3. **Of 22 identifiable operational initiatives since 2022, 14 are realised, 3 are in progress and 5 are not evidenced.** The realised ones are almost all cost-per-unit wins in support, G&A, payments and headcount. The five not evidenced are the ones the equity story leans on: AI engineering productivity, cloud efficiency, performance-marketing efficiency, the AI spend inside the 2026 guide, and the hotels build-out. `07_ops_initiatives.csv` carries the claim, the source, the filed evidence and the score for each.

4. **AI customer support is the one new lever that is genuinely working, and it is worth about 0.4 points of margin a year, not 2.** Management's disclosures: AI resolves ~1/3 of contacts (4Q25), >40% (1Q26), ~45% in 50+ languages (2Q26); support cost per booking -10% (1Q26) and -16% (2Q26); third-party service-provider cost -$17M in 2Q26. Independently, operations and support cash cost per night went $2.13 (1H25) -> $2.05 (1H26), **-3.8%**, worth **+0.39 points of margin**. The reported line still grew 8% because payroll (+$41M), customer relations (+$14M) and insurance (+$9M) ate most of it. The lever is real; it is not a re-rating event on its own.

5. **The AI cost is visible in the commitments note before it is visible in the P&L.** Non-cancelable purchase obligations went $719M (Dec 2024) -> **$1,749M (Dec 2025)**, and the data-hosting commitment went from "at least $672 million... through 2027" to "**at least $1.7 billion... through 2031**" (10-K Note 13). Server costs are already +$15M in 1H26 on reserved-instance amortisation. Chesky said in Feb 2026 "our investment in AI will not affect the P&L"; Mertz said in Aug 2026 the guide "does assume a material increase in terms of the AI spend". The commitments note settles the argument in Mertz's favour.

6. **Against peers, Airbnb's ceiling on Adjusted EBITDA is roughly Booking's, about 37-38%, and the gap that actually matters is SBC.** FY2025: ABNB adjusted EBITDA margin 35.1% vs BKNG 36.8%; on an identically-computed EBITDA proxy (op income + D&A + SBC) 34.6% vs 37.4%. But GAAP operating margin is 20.8% vs 32.8% and SBC is 13.1% of revenue vs 2.3%. **On SBC-adjusted FCF margin the ranking flips: ABNB 24.6%, BKNG 31.5%.** Airbnb's headline FCF advantage (37.7% vs 33.8%) is entirely stock compensation plus a shrinking float and low cash taxes. Of the ten names benchmarked, only META (60.9% EBITDA proxy) and NFLX (31.0% with 0.8% SBC) are structurally better businesses on this measure; UBER (15.6%), DASH (18.4%), EXPE (21.4%), TRIP (14.8%), SPOT (14.8%) and DUOL (27.7%) are all below.

7. **The lever model says FY2026 36.1%, FY2027 36.6%, FY2028 37.5% in the base case** (revenue $14.2B / $15.8B / $17.6B). Bear 34.6% / 32.0% / 30.4%; bull 37.6% / 40.7% / 43.7%. This reconciles with the existing scenarios to +0.25 points (FY26 base) and +0.05 points (FY27 base). **The path to 40% has about a 21% probability by FY2028** on a correlated Monte Carlo over the lever ranges (p10 33.3%, median 37.6%, p90 41.3%; P(<34%) 14%). It requires either take rate +20 bps a year for three years, or S&M cash growth held to 12% a year (against +25% in 2026), or nights growth of 11%+ a year. It does not happen through operations and support alone: even a -16% cut in support cost per night every year for three years is needed to get there on that lever alone.

8. **Below Adjusted EBITDA the story gets worse, not better, and nobody models it.** In the base case FCF/Adjusted EBITDA falls from 107% (2025) to 99% / 95% / 93% as cash taxes converge on the provision ($370M -> $538M -> $703M) and interest income falls ($705M -> $660M -> $590M) against $120-125M a year of new interest expense on the March 2026 notes. **SBC-adjusted FCF margin is 22.5-22.7% in the base case, against a 35-37% headline Adjusted EBITDA margin.** That 14-point wedge is the number the pitch has to defend, and it is not shrinking on any plausible SBC path.

---

## 2. Cost-line deep dive (part 1)

`07_cost_lines_per_night.csv`: 22 quarters, each line GAAP and cash (ex-SBC), in dollars, per night, per $100 of GBV, as a percent of revenue and year on year, plus SBC by function, D&A, interest income, tax provision, FCF and the unearned-fee change. New this run: **the quarterly sales-and-marketing split** (brand and performance marketing vs field operations and policy) built from the 10-Q three-month tables with Q4 derived as the 10-K full year less the three quarters.

### 2.1 Same-quarter cash cost per night, Q2

| $ per night, cash | 2Q22 | 2Q23 | 2Q24 | 2Q25 | 2Q26 | change 22-26 |
|---|---|---|---|---|---|---|
| Revenue per night | 20.29 | 21.58 | 21.97 | 23.04 | 24.33 | **+4.04** |
| Cost of revenue | 3.76 | 3.75 | 4.04 | 4.05 | 4.27 | +0.51 |
| Operations & support | 2.32 | 2.59 | 2.51 | 2.30 | 2.18 | **-0.14** |
| Product development | 2.22 | 2.26 | 2.24 | 2.46 | 2.52 | +0.30 |
| Brand & performance marketing | 2.72 | 3.14 | 3.07 | 3.32 | 3.90 | **+1.18** |
| Field operations & policy, cash | 0.65 | 0.77 | 1.14 | 1.43 | 1.55 | **+0.90** |
| G&A | 1.81 | 1.89 | 1.93 | 1.76 | 1.52 | -0.29 |
| **Total cash cost per night** | **13.49** | **14.40** | **14.94** | **15.33** | **15.93** | **+2.44** |
| Adj. EBITDA margin | 33.8% | 33.0% | 32.5% | 33.7% | 35.0% | +1.2 pts |
| SBC % revenue | 11.7 | 12.2 | 13.9 | 13.7 | 13.5 | +1.8 pts |

The Q3 version (3Q22 -> 3Q25) tells the same story at a quarter of the size: revenue per night +$1.72, cash cost +$0.99, of which S&M +$0.80. Cost of revenue per $100 of GBV has been remarkably stable at $2.26-2.40 since 2022 (2Q26: $2.33), which is why cost of revenue only looks like a leak when expressed per night: it scales with GBV and ADR has risen.

### 2.2 Components management discloses (`07_cost_components_annual.csv`)

| Component | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 | Source |
|---|---|---|---|---|---|---|
| Merchant fees + chargebacks, % of GBV | 1.80 | 1.89 | 1.87 | 1.84 | 1.82 | FY2021 10-K levels, later years accumulate the MD&A deltas (derived) |
| Brand + performance marketing, $M | 723 | 1,030 | 1,208 | 1,455 | 1,595 | 10-K S&M split table |
| Field operations and policy, $M | 463 | 486 | 555 | 693 | 993 | same |
| Employees at Dec 31 | 6,132 | 6,811 | 6,907 | ~7,300 | ~8,200 | 10-K Item 1 |
| Third-party support workers | - | 11,000 | 11,000 | 11,000 | 13,000 | 10-K Item 1 |
| Revenue per employee, $k | 977 | 1,233 | 1,436 | 1,521 | **1,493** | derived |
| Cloud/hosting cost increase, $M | - | +25 | +31 | +26 | +27 | 10-K MD&A (level never disclosed) |
| Insurance cost increase, $M | +42 | +30 | +16 | +25 | +14 | 10-K MD&A ops & support |
| Purchase obligations at Dec 31, $M | - | 1,068 | 934 | 719 | **1,749** | 10-K Note 13 |
| Data-hosting commitment, $M (through) | - | 942 (2027) | 842 (2027) | 672 (2027) | **1,700 (2031)** | 10-K Note 13 |
| Cash taxes paid, $M | 17 | 68 | 132 | 350 | 232 | 10-K supplemental cash flow |
| Interest income as % of FCF | 0.6 | 5.5 | 18.8 | 18.2 | 15.3 | derived |

Two things to take from this table. **Revenue per employee fell in 2025 for the first time** (-1.8% after +56% over 2021-2024): the headcount lever is spent. And **the data-hosting commitment quadrupled in duration and 2.5x'd in size at end-2025**, which is the AI build showing up as a balance-sheet commitment four to eight quarters before it reaches cost of revenue.

### 2.3 What is still not disclosed

Payment processing has not been given as a level since the FY2021 10-K; cloud cost has never been given as a level, only as a year-on-year increase; there is no contribution margin, revenue or booking count for Services, Experiences or Hotels; and Adjusted EBITDA is never given by cost line. Everything above that is derived says so in the CSV's `source` column.

---

## 3. Operational initiative inventory (part 2)

`07_ops_initiatives.csv`: 22 initiatives, each with first announcement date, the primary source for the claim, the cost line it lands in, the filed evidence (computed from the CSVs, not typed), a quantified effect and a score.

**Realised (14).** Marketing reset (brand and performance 23.7% of revenue in 2019 -> 12.1-13.1% since 2021); the 2020 workforce reduction and functional reorganisation; headcount discipline 2021-2024; the payments reset (merchant fees 2.51% of GBV in 2020 -> 1.80% in 2021); the 2Q23 payment-processor incentive (explicitly non-recurring); the third-party support network; **AI customer support**; G&A discipline (8.9% -> 6.2% of revenue in Q2, though about a point of that is lapping tax reserves); Reserve Now Pay Later; FX hedging; the investment-grade notes; the buyback program (diluted shares -4.6% y/y in 2Q26); insurance containment; and the policy of redeploying fixed core-market brand budget into expansion markets.

**In progress (3).** Co-Host Network (a supply program with no disclosed cost effect); the Services and Experiences launch investment (spent, and then some: field ops +$300M in 2025 against a $200-250M guide, with no return metric ever disclosed); and the 15.5% single-fee rollout ("Project Hawaii"), which has not moved the implied take rate yet (Q2 implied take rate 12.96% in 2024, 13.17% in 2025, 13.26% in 2026 - the rise is the usual booking-versus-stay timing, not the fee).

**Not evidenced (5).**
- **AI engineering productivity.** 60% of code AI-authored, 80% more features shipped, concept-to-launch -60%. Product development cash was $1,178M in 1H25 and $1,310M in 1H26, +11%, and the 10-Q says the entire increase is payroll on higher average headcount. Zero P&L saving. It is a growth option, not a margin lever.
- **Cloud and hosting.** Costs and commitments are both rising (section 2.2).
- **Performance-marketing efficiency.** "90% of our traffic remains direct or unpaid" has been said on five calls; brand and performance marketing grew 32% in 1H26 against revenue +17%. Both cannot be true as an efficiency claim.
- **AI spend inside the 2026 guide.** Unquantified, and the two statements on the record contradict each other.
- **Hotels / enterprise build-out.** Cost only so far: four senior hires from Booking and Uber, hotels in 20 cities, a $58M WeRoad investment, the Lark Hotels partnership. No budget, no revenue.

---

## 4. Peer benchmark (part 3)

`07_peer_margin_benchmark.csv`: ABNB, BKNG, EXPE, TRIP, UBER, DASH, META, NFLX, DUOL, SPOT, FY2021-FY2025, from SEC XBRL company facts (SPOT is an IFRS 20-F filer in EUR, converted at the FRED AEXUSEU annual average). `ebitda_proxy_margin_pct` = (operating income + D&A + SBC) / revenue and is the only margin computed identically for all ten; `reported_adj_ebitda_margin_pct` uses each company's own definition and is blank where the company does not publish one.

| FY2025 | ABNB | BKNG | EXPE | TRIP | UBER | DASH | META | NFLX | DUOL | SPOT |
|---|---|---|---|---|---|---|---|---|---|---|
| Revenue $M | 12,241 | 26,917 | 14,733 | 1,891 | 52,017 | 13,717 | 200,966 | 45,183 | 1,038 | 19,430 |
| Revenue growth | +10.3% | +13.4% | +7.6% | +3.1% | +18.3% | +27.9% | +22.2% | +15.9% | +38.7% | +14.6% |
| Reported adj. EBITDA margin | 35.1% | 36.8% | 23.8% | 16.9% | 16.8% | 20.3% | - | - | - | - |
| **EBITDA proxy margin** | **34.6%** | **37.4%** | 21.4% | 14.8% | 15.6% | 18.4% | 60.9% | 31.0% | 27.7% | 14.8% |
| GAAP operating margin | 20.8% | 32.8% | 12.7% | 4.2% | 10.7% | 5.3% | 41.4% | 29.5% | 13.1% | 12.8% |
| **SBC % revenue** | **13.1%** | 2.3% | 2.7% | 5.7% | 3.5% | 7.7% | 10.2% | 0.8% | 13.2% | 1.4% |
| S&M % revenue | 21.1% | 30.4% | 49.9% | n/a | 9.4% | 18.1% | 6.0% | 7.3% | 12.1% | 8.3% |
| Marketing only % revenue | 13.0% | 30.4% | 26.5% | 41.8% | 3.1% | 11.7% | 1.0% | - | 8.4% | - |
| FCF margin | 37.7% | 33.8% | 21.1% | 8.6% | 18.8% | 15.8% | 22.9% | 20.9% | 35.6% | 16.7% |
| FCF / EBITDA proxy | 109% | 90% | 99% | 58% | 120% | 86% | 38% | 67% | 129% | 113% |
| **SBC-adjusted FCF margin** | **24.6%** | **31.5%** | 18.4% | 2.9% | 15.3% | 8.2% | 12.8% | 20.1% | 22.4% | 15.3% |
| Revenue per employee $k | 1,493 | 1,108 | 921 | 730 | 1,530 | 437 | 2,548 | 2,824 | 1,153 | 2,666 |

Notes on gaps: BKNG's FY2024 reported adjusted EBITDA is blank because the Q4 2024 release text is images and the FY2025 10-K only gives a segment measure on a different definition (segment 2023 = $7,415M vs $7,100M in the release) - use the EBITDA proxy for that comparison. TRIP restructured its income statement in 2024 and no longer reports a "Selling and marketing" line, so `sm_pct_rev` stops after FY2023; marketing-only is available every year.

**Where ABNB sits.** Third of ten on EBITDA proxy margin (behind META and BKNG), first on FCF margin, and **sixth on SBC-adjusted FCF margin**. It has the second-highest SBC ratio in the set after DUOL. On revenue per employee it is mid-pack: better than every travel peer but half of META, NFLX and SPOT.

**Realistic ceiling.** Booking is the right ceiling and it is close: 37.4% EBITDA proxy against Airbnb's 34.6%, and Booking has been between 30.0% and 37.4% for five years while running a completely different cost mix (30% of revenue on marketing, 12.6% on personnel; Airbnb 13% on marketing, ~38% on people-heavy lines). Nobody in travel earns much more than that. **Treat 38% as the realistic Adjusted EBITDA ceiling for a business that keeps growing nights at 8-10%, and 40% as a case that requires a new revenue line (advertising, loyalty) rather than a cost programme.**

**What cost mix gets to 40%?** Airbnb's FY2025 mix, as a percent of revenue (cash): cost of revenue 17.0, operations and support 10.1, product development 10.9, brand and performance marketing 13.0, field operations 6.4, G&A 8.7, add-backs +1.3 = 35.1%. A 40% mix, on the FY2028 base revenue of $17.6B and 0.9 points of add-backs, needs total cash cost at 60.4% of revenue, roughly: **cost of revenue 16.5, operations and support 7.4, product development 9.7, brand and performance marketing 14.0, field operations 6.3, G&A 6.5.** That is 2.7 points out of support, 1.2 out of product development and 2.2 out of G&A, 0.5 out of cost of revenue - while *letting marketing rise a point*. It is the midpoint of the model's base-case (37.5%: cor 16.9 / ops 7.8 / pd 10.2 / bpm 14.9 / fop 6.7 / G&A 6.9) and bull-case (43.7%: 16.1 / 6.9 / 9.2 / 13.1 / 5.8 / 6.0) FY2028 mixes. It is a support-and-G&A story, not a marketing story, which is the opposite of what a Booking comparison suggests.

---

## 5. Lever-by-lever margin model, FY2026E-FY2028E (part 4)

`07_margin_levers_fy26_fy28.csv`, built by `07_margin_lever_model.py`. Cost lines are driven by their natural unit (cost of revenue by GBV dollars, operations and support by nights, everything else by cash growth); revenue = nights x ADR ex-FX x FX x take rate. It runs below Adjusted EBITDA to a GAAP operating margin, an FCF margin and an SBC-adjusted FCF margin. The attribution uses the same decomposition as `abnb_margin_bridge.py`, so the numbers are comparable with `abnb_margin_bridge.csv`.

### 5.1 Results

| | FY2026E | FY2027E | FY2028E |
|---|---|---|---|
| **Bear** revenue $M / growth | 14,002 / +14.4% | 14,526 / +3.7% | 15,288 / +5.3% |
| Adj. EBITDA margin | 34.6% | 32.0% | 30.4% |
| GAAP operating margin | 20.6% | 16.7% | 14.2% |
| FCF margin / SBC-adjusted FCF margin | 32.8% / 19.7% | 28.4% / 14.0% | 25.8% / 10.4% |
| **Base** revenue $M / growth | 14,215 / +16.1% | 15,809 / +11.2% | 17,566 / +11.1% |
| Adj. EBITDA margin | **36.1%** | **36.6%** | **37.5%** |
| GAAP operating margin | 22.7% | 23.2% | 24.6% |
| SBC % revenue | 12.6% | 12.4% | 12.1% |
| FCF margin / FCF as % of Adj. EBITDA | 35.9% / 99% | 34.9% / 95% | 34.8% / 93% |
| SBC-adjusted FCF margin | 23.4% | 22.5% | 22.7% |
| **Bull** revenue $M / growth | 14,418 / +17.8% | 16,764 / +16.3% | 19,279 / +15.0% |
| Adj. EBITDA margin | 37.6% | 40.7% | 43.7% |
| FCF margin / SBC-adjusted FCF margin | 38.7% / 26.7% | 40.4% / 29.4% | 42.3% / 32.4% |

**Reconciliation to `abnb_margin_scenarios.csv`:** base FY2026 +0.25 pts (36.1% vs 35.9%), base FY2027 +0.05 pts (36.6% vs 36.5%), bull FY2026 -0.14, bull FY2027 +0.92, bear FY2026 -0.66, bear FY2027 -1.83. The base cases agree; my bear is harsher because it splits S&M and lets the field-operations headcount stay while media spend is cut, and because it carries a -2% FX drag in FY2027 that the existing bear puts at -1.5%.

**Implied Q4 2026 margin** (FY less 1H26 actual of $6,286M revenue and $1,780M Adjusted EBITDA, less Q3 at the guide midpoint): bear 26.5%, base 32.5%, bull 36.8%, against Q4 2025's 28.3%. The bear implies a full-year miss of the 35.5% floor, which management has not done in four years of guiding it - so read the bear as a spending-discipline break, not a base case.

### 5.2 Base-case attribution, margin points

| Lever | FY25 -> FY26 | FY27 -> FY28 |
|---|---|---|
| Revenue per night: ADR ex-FX | **+2.29** | +1.59 |
| Revenue per night: FX | +1.32 | 0.00 |
| Revenue per night: take rate | 0.00 | +0.24 |
| Operations & support per night ($2.32 -> $2.20) | +0.51 | +0.42 |
| G&A cash per night | +0.64 | +0.20 |
| Cost of revenue per night (GBV-driven) | -0.95 | -0.34 |
| Product development cash per night | -0.10 | -0.14 |
| **Brand and performance marketing per night ($2.99 -> $3.40)** | **-1.78** | -0.75 |
| Field operations and policy, cash | -0.46 | -0.25 |
| D&A and add-backs | -0.42 | 0.00 |
| **Total change** | **+1.05** | **+0.97** |

Read it: in FY2026 the entire margin improvement is the ADR-plus-FX windfall (+3.6 points) minus the marketing ramp (-2.2 points) plus operating leverage in support and G&A (+1.2). **If ADR ex-FX and FX both go to zero, the base case is a 2.5-point margin decline, not a 1-point gain.** That is the single most important sensitivity in the model and it is not a cost lever at all.

### 5.3 Levers, with the range and what each is anchored to

Every lever's bear/base/bull and its evidence string are in the CSV (`row_type = lever`). The ones that matter, base case:

| Lever | FY26 | FY27 | FY28 | Anchor |
|---|---|---|---|---|
| Nights growth | +10.0% | +8.5% | +8.0% | 1H26 actual +9.7%; 8-10% every quarter since 2Q24 |
| ADR ex-FX | +3.5% | +2.5% | +2.5% | letters: +3% (4Q25), +4% (1Q26), +4% (2Q26) |
| FX effect on revenue | +2.0% | 0.0% | 0.0% | 2Q26 letter: ~3-point tailwind after hedging, fading |
| Take rate change | 0 bps | 0 bps | +5 bps | guided flat for 2026; single fee vs new-business incentives |
| Cost of revenue per $ GBV | 0.0% | 0.0% | -0.5% | flat at 1.82-1.89% of GBV since 2022 |
| **Operations & support per night** | **-5.0%** | **-5.0%** | **-5.0%** | support cost per booking -10% (1Q26), -16% (2Q26); 1H26 realised -3.8% |
| Product development cash | +11.0% | +10.0% | +9.5% | 1H26 +11%, all payroll |
| **Brand and performance marketing** | **+25%** | **+16%** | **+13.5%** | 1H26 +32%; base needs H2 at ~+17%, floor breached above ~+29% |
| Field operations and policy cash | +18% | +14% | +12% | +43% in FY2025, +24% in 1H26 |
| G&A cash | +2% | +5.5% | +5.0% | 1H26 +1% (payroll +$38M offset by non-income taxes -$38M) |
| SBC growth | +13% | +10% | +8% | 1H26 SBC $897M vs $782M, +14.7%; guided below 2025's +10% |
| Interest income $M | 660 | 620 | 590 | 1H26 $338M vs $363M; $12.1B cash and ST investments |
| Interest expense $M | 120 | 125 | 125 | $2.5B notes at 4.40-5.25%, $37M in 2Q26 |
| Cash taxes % revenue | 2.6% | 3.4% | 4.0% | FY2025 $232M (1.9%) against a $626M provision; 1H26 ETR 17.1% |

The bear and bull are not always monotonic on the cost lines: in a demand bear management cuts marketing (bear FY27 brand and performance +12% vs base +16%) but revenue falls faster, so the margin still drops. That is deliberate and is flagged in the CSV.

### 5.4 Path to 40%, with a probability

A correlated Monte Carlo (40,000 draws; each lever loads 0.75 on a common annual state, bear and bull read as the 10th and 90th percentile, 0.6 year-to-year persistence):

| | FY2026E | FY2027E | FY2028E |
|---|---|---|---|
| p10 / median / p90 Adj. EBITDA margin | 35.2 / 36.1 / 37.1 | 33.6 / 36.6 / 39.3 | 33.3 / 37.6 / 41.3 |
| P(>= 40%) | 0.0% | 4.8% | **20.8%** |
| P(>= 38%) | 0.4% | 25.3% | 44.3% |
| P(< 34%) | 0.3% | 13.0% | 14.1% |

An independent-draw version is in the CSV as a bound: it collapses both tails (P(>=40%) 0.0%, P(<34%) 0.0% in every year), which is why the correlated version is the one to quote.

**What each single lever would have to do, alone, for a 40% FY2028 margin** (every other lever at base, solved by bisection over all three years):

| Lever | required every year FY26-FY28 | base case FY2028 |
|---|---|---|
| Take rate change | **+19.9 bps per year** | +5 bps |
| S&M cash growth (brand + field together) | **+12.3%** | +13.0% blended (brand +13.5%, field +12.0%) |
| Nights growth | **+11.2%** | +8.0% |
| Product development cash growth | **+0.4%** | +9.5% |
| Operations & support cash cost per night | **-16.4%** | -5.0% |

The take-rate answer is the cheapest: about 60 bps of cumulative take rate over three years, which is what sponsored listings plus the 15.5% single fee plus loyalty would have to deliver. The support answer (-16% per night every year for three years, when the best year on record is -3.8% realised) is not credible on its own. **My judgement: 40% by FY2028 is a ~20% outcome and it happens through monetisation, not through cost.**

---

## 6. Corrections to existing work

1. **`2026-09-05_margin-drivers.md` section 1.4 and section 4** say that inside sales and marketing "the growth is not ads" and cite 2025's +10% brand-and-performance against +43% field operations. That was true for FY2025 and is **no longer true in 2026**: 1H26 brand and performance marketing is +32% ($1,091M vs $824M) and field operations +24%. The note's own section 7 does mention 1H26 marketing "+30% in Q2", so it is an internal inconsistency rather than an error, but the FY2025 framing has been carried into the summary and should be updated. Quarterly series now in `07_cost_lines_per_night.csv`.
2. **`abnb_margin_scenarios.csv` FY2027 bear is probably too kind on the cost side.** It assumes management flexes S&M cash growth to +9% in a year when revenue grows 4.3%. On the split data, +9% total S&M would require brand and performance marketing to be roughly flat while field-operations headcount keeps growing; the FY2026 exit run-rate on brand and performance is +25-32%. My bear uses +12% brand and +10% field and lands at 32.0% against the existing 33.8%.
3. **The margin-drivers note's open item "cash taxes: the FCF bridge uses the tax provision as a proxy" is now quantified.** Reconstructing FCF from Adjusted EBITDA with actual cash taxes leaves a working-capital residual of **-$140M in FY2024 and -$139M in FY2025** (about -1.1% of revenue, and remarkably stable). That is the calibration used in the lever model, and it means the FCF bridge is closeable to within 0.1% of revenue with disclosed items only.
4. **`AdvertisingExpense` in XBRL is not the brand-and-performance marketing line** and should not be used as one: FY2025 tags $843M against the 10-K's $1,595M. The `07_cost_components_annual.csv` row carries both with a warning. Same file: `PurchaseObligation` carries no CY frames in ABNB's company facts, so the numbers now come from 10-K Note 13 directly.
5. **`bkng_head_to_head.py` / margin-drivers section 13 leaves Booking's FY2024 adjusted EBITDA blank.** It is not recoverable from the cached filings on a comparable definition (the FY2025 10-K gives only "Segment Adjusted EBITDA less Capex", which is $315M above the press-release measure in 2023). Use the EBITDA proxy for that year; the peer CSV documents this.

---

## 7. For the model

Parameters this workstream supplies. Every one is in `07_margin_levers_fy26_fy28.csv` with its evidence string.

| Parameter | Value (bear / base / bull) | Unit | Source |
|---|---|---|---|
| FY26 nights growth | 9.5 / 10.0 / 10.3 | % | 1H26 actual +9.7% |
| FY26 ADR ex-FX | 3.0 / 3.5 / 4.0 | % | letters 4Q25-2Q26 |
| FY26 FX effect on revenue | 1.8 / 2.0 / 2.3 | % | 2Q26 letter, post-hedge |
| FY26 take rate change vs 13.41% | -5 / 0 / +5 | bps | 2026 guide |
| FY26 cost of revenue per $ GBV | +0.5 / 0.0 / -0.5 | % change | 2Q26 10-Q merchant fees and chargebacks |
| FY26 ops & support cash per night | -4.0 / -5.0 / -6.0 | % change | 1H26 realised -3.8%; support cost per booking -16% |
| FY26 product development cash | 11.5 / 11.0 / 10.5 | % growth | 1H26 +11% |
| FY26 brand & performance marketing | 28 / 25 / 23 | % growth | 1H26 +32% |
| FY26 field operations & policy cash | 20 / 18 / 16 | % growth | 1H26 +24% |
| FY26 G&A cash | 3 / 2 / 0 | % growth | 1H26 +1% |
| FY27 / FY28 versions of all of the above | see table 5.3 and the CSV | | |
| SBC growth | 16/13/10 (FY26), 14/10/6 (FY27), 12/8/4 (FY28) | % | 1H26 +14.7%, guided below 2025 |
| Interest income | 620/660/700, 540/620/690, 500/590/680 | $M | 1H26 $338M; $12.1B cash |
| Interest expense | ~120-128 | $M/yr | $2.5B notes, 4.40-5.25% |
| Cash taxes | 2.6 / 3.4 / 4.0 (base, FY26/27/28) | % of revenue | FY2025 1.9% vs a 5.1% provision |
| Working-capital residual in the FCF bridge | -1.1 | % of revenue | FY2024 -$140M, FY2025 -$139M |
| Change in unearned fees | 0.0 | % of revenue | RNPL has switched the float off |
| Capex | 0.3 | % of revenue | $33-34M a year |
| D&A | 0.7 | % of revenue | FY2023-FY2025 |
| Add-backs (D&A + other) | 0.9 | % of revenue | FY2025 |
| FCF / Adjusted EBITDA | 99 / 95 / 93 (base FY26/27/28) | % | vs 107% in FY2025 |
| Split of S&M: brand & performance vs field ops, FY2025 | 1,595 / 781 cash (993 GAAP) | $M | 10-K split table less S&M SBC |
| Realistic Adjusted EBITDA ceiling | 38 | % | BKNG's five-year EBITDA-proxy range, 30.0-37.4% |
| P(FY2028 Adjusted EBITDA margin >= 40%) | 21 | % | correlated Monte Carlo, 40,000 draws |

---

## 8. For the 5 Nov card (Q3 2026 print)

1. **Q3 margin against 49%.** The guide is "down slightly" from 50.1%. Base 49.0%, bear 48.3%, bull 50.2%. Below 48% and the FY floor is at risk; above 50% and the FY guide goes to 36%+.
2. **Sales and marketing growth is the number to read first, and now it has to be read in two parts.** The 10-Q gives brand and performance marketing and field operations separately; 1H26 ran +32% and +24%. Holding every other base lever, the FY2026 margin as a function of full-year brand-and-performance growth is: +17% -> 37.0%, +20% -> 36.7%, +25% -> 36.2% (base), +28% -> 35.8%, **+31% -> 35.5% (the floor)**. In H2 terms (H2 2025 brand and performance was $771M), the base case needs H2 at about **+17%** and the floor is only breached above about **+29%**, i.e. no deceleration at all from the 1H pace. **So the floor has real cushion and the base case does not.** A Q3 print with brand and performance above +28% y/y means the FY lands near 35.5%, not 36%+; a print below +20% is the first evidence the reinvestment cycle is easing and is worth more to the margin case than any AI datapoint. (`data/processed/predictive/04_margin_predictability.csv`: prior-quarter S&M deleverage predicts a smaller margin beat, r -0.62, n 14.)
3. **Support cost per booking.** Management gave -10% (Q1) and -16% (Q2). Anything better than -16% keeps the +0.4 to +0.5 points of annual margin from operations and support in the run rate; a deceleration toward -8% means the easy contacts are done.
4. **Implied take rate against 17.9%** (Q3 2025: 17.88%; Q3 runs far above the full-year 13.4% because revenue follows stays and Q3 is the stay-heavy quarter). The 15.5% single fee has been rolling out for four quarters and has not yet shown; Q3 is the first clean read. Every 10 bps of full-year take rate is worth about half a point of margin.
5. **Cost of revenue per $100 of GBV against $2.40** (Q3 2025). Watch for the server-cost line: 1H26 was +$15M on reserved-instance amortisation and the data-hosting commitment is now $1.7B through 2031. A step-up here is the AI spend arriving.
6. **Interest income against $180M** (Q3 2025) and interest expense against ~$37M. Net interest is down about $70M a year on a run-rate basis and it comes straight out of FCF, not EBITDA.
7. **Any first 2027 margin comment.** There is no 2027 guide. The base case is 36.6%; management's floor language means the first number they give will be the number, so a "at least 36%" for 2027 on the Q3 or Q4 call would be an upgrade to the base case, and "stable" would be a downgrade.
8. **Headcount language.** 2026 was guided to headcount growth "lower than 2025" (+12%). Revenue per employee fell in 2025 for the first time. If the 10-K in February shows headcount up more than about 8%, the productivity claim behind the AI story is not landing.

---

## 9. Caveats

- The quarterly sales-and-marketing split is GAAP; the cash version subtracts total S&M SBC from field operations, which assumes no stock compensation sits inside brand and performance marketing. That is almost certainly right (it is media and agency spend) but it is an assumption, not a disclosure.
- Payment processing levels after FY2021 are accumulated from MD&A deltas and are derived, not disclosed. Treat the 1.82% of GBV figure as +/- 10 bps.
- The lever model is deterministic in its scenarios; the only probability statement is the Monte Carlo, and its correlation structure (rho 0.75, persistence 0.6, bear/bull as p10/p90) is a judgement, not an estimate. Changing rho to 0.5 roughly halves the tail probabilities; changing it to 0.9 roughly doubles P(<34%).
- FY2028 has no guidance of any kind behind it. Everything in that column is extrapolation with the evidence strings showing what it is anchored to.
- n is not an issue here (this is an accounting decomposition, not a forecasting test), but nothing in this note establishes that any of these levers *predicts* the stock. The predictive study is `research/notes/2026-09-06_predictive-study.md`; its finding that **prior-quarter sales-and-marketing deleverage predicts the next margin surprise against the guide bound with r = -0.62 (n = 14, permutation p 0.017, beats the naive-last baseline)** - more S&M deleverage last quarter, smaller beat this quarter - is the one place where a lever in this note has been tested against a print (`data/processed/predictive/04_margin_predictability.csv`, `sm_delev_pts_lag1`). It is knowable before the print and it is consistent with point 2 of section 8: the H2 2026 marketing ramp argues for a smaller Q3 and Q4 margin beat than the 2023-2025 record would suggest.
