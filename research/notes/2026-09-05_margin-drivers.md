# ABNB margins: what has moved them, what management says moves them, and what is guided

- **Sources:** all 23 earnings-call transcripts Q4 2020 to Q2 2026 (Airbnb IR corrected transcripts for Q4 2021 and Q1 2023 onward; stockanalysis.com / Motley Fool for Q4 2020 to Q4 2022); all 23 shareholder letters (8-K Ex. 99.1); 10-Ks FY2020 to FY2025; 10-Qs Q1 2021 to Q2 2026; SEC XBRL company facts. Source IDs S22 to S25 in `research/sources/README.md`.
- **Date:** 2026-09-05
- **Author:** Krishang Surapaneni (compiled with Claude Code). Companion dataset: `data/processed/abnb_quarterly_costlines.csv` (script `analysis/src/abnb_costlines_from_xbrl.py`). Builds on `research/airbnb_earnings_call_study.md` for KPIs and stock reactions.

---

## 1. Bottom line

1. **Margin expansion is over by choice, not by exhaustion.** Adjusted EBITDA margin went from -5% (2019) to 27% (2021), 35% (2022) and 37% (2023). Since the Q4 2023 call management has guided a *floor* rather than a target: at least 35% (2024, delivered 36%), at least 34.5% (2025, delivered 35%), "stable" then at least 35% then at least 35.5% (2026). Ellie Mertz, Q2 2026: "there's a relative floor in our ability to continue to invest against that." Margin is now the residual after growth spending, and every upgrade to the margin guide in 2025 and 2026 came from revenue upside that was only partly reinvested.

2. **Four things built the 4,000 bps.** (a) A permanent reset of marketing: brand and performance marketing fell from $1.14B in 2019 (24% of revenue) to $0.72B in 2021 and has stayed at 12% to 13% of revenue since, with roughly 90% of traffic direct or unpaid. (b) A fixed-cost reset: the May 2020 layoff and move to a functional organization; headcount was still 5% below 2019 at end-2022 on 75% more revenue. (c) Variable-cost work on payments, community support and cloud. (d) An ADR windfall: rates rose 35% to 40% versus 2019 while the take rate stayed flat, so revenue per night rose against a largely fixed cost per night. Management admitted the last one repeatedly ("the tailwind of average daily rate definitely helped our margins", Stephenson, Q4 2021; "higher average daily rates have helped our overall margins, so it kind of accelerated overall profitability", Q2 2023).

3. **What moves a given quarter versus guidance is timing, not economics.** Five recurring swing factors: brand-marketing phasing (pulled into H1 from 2023 on, then heavier Q2 than Q1 in 2024); calendar (Easter and leap day added about 3 points to Q1 2024 revenue growth and reversed in Q2 2024 and Q1 2025); FX (roughly half of revenue is non-USD, most costs are USD; a hedging program started in 2025); one-offs (payment-processor incentives in Q2 2023, gift-card breakage in Q4 2023, about $935M of tax withholding and lodging-tax reserves in Q4 2023 G&A that GAAP took and Adjusted EBITDA excluded); and booking-versus-stay timing that moves the implied take rate (Reserve Now, Pay Later since 2025).

4. **The cost mix has rotated since 2022: sales and marketing up, everything else down.** Same-quarter comparisons (Q2, GAAP incl. SBC): sales and marketing 18.0% of revenue in 2022 to 24.3% in 2026; operations and support 12.3% to 10.0%; G&A 11.6% to 8.6%; cost of revenue 18.5% to 17.5%; product development 17.8% to 18.6%. Inside sales and marketing the growth is not ads: in 2025 brand and performance marketing grew 10% while "field operations and policy" (go-to-market, supply acquisition for services, experiences, hotels, expansion markets, policy) grew 43% to $993M. In 1H 2026 marketing spend is growing again (+30% in Q2) on "paid growth initiatives in emerging markets and partnerships".

5. **The 2026 guide of at least 35.5% is built on three offsets to that spending.** AI customer support (support cost per booking -10% in Q1 2026 and -16% in Q2; over 40% of contacts self-resolved; third-party support vendor cost fell $17M in Q2), slower headcount growth than 2025, and revenue leverage on cost of revenue and G&A. Against that: a "material increase" in AI spend inside the guide (Mertz, Q2 2026), Q3 2026 margin guided down slightly from 50%, and a take rate held flat for 2026 by customer incentives for new businesses. No 2027 guide and no long-term margin target since "30% or greater" in 2021.

6. **For the model.** Q3 is a 50% to 54% margin quarter and Q1 is 14% to 20%, so quarterly margins tell you little without the same-quarter comparison. The two lines to forecast are sales and marketing as a percent of revenue (management has said core-market brand spend is a fixed amount per market, so leverage is possible but is being redeployed to new markets) and operations and support per booking (the AI lever). Cost of revenue is a GBV function (merchant fees about 2% of GBV), not a revenue function, so take-rate changes flow almost entirely to margin. ADR ex-FX remains the single most powerful and least controllable driver.

7. **On a cash basis the bridge is simple (sections 3.5, 10, 11).** From 2022 to 2025 revenue per night added 5.1 margin points (ADR ex-FX 3.7, FX 0.7, take rate 0.7) and sales and marketing took back 4.2 of them; every other cash line was within half a point, and product development has been flat at 10% to 11% of revenue in cash since 2022 (its GAAP creep is SBC). Projected bottom-up, FY2026 lands at 35.9% base (bear 35.3%, bull 37.7%) with the implied Q4 at 31.5%, and FY2027 at 36.5% base (33.8% to 39.8%). The most valuable lever management controls is support cost per night (-10% is worth about a point of margin); the most valuable one it does not is ADR ex-FX (+1 point is worth about half a point).

---

## 2. Scope and method

- Transcripts: Q1 2023 to Q2 2026 and Q4 2021 from Airbnb's own FactSet corrected transcripts (investors.airbnb.com CDN); Q4 2020 to Q4 2022 from stockanalysis.com with Motley Fool as a cross-check. Every passage mentioning margin, EBITDA, cost lines, marketing, headcount, SBC, take rate, FX or guidance was pulled with speaker tags and read: prepared remarks and full Q&A for margin questions.
- Letters: the "Adjusted EBITDA", cost commentary and "Outlook" sections of all 23 letters.
- Filings: the MD&A results-of-operations narrative for each cost line in every 10-K and 10-Q (what actually moved merchant fees, insurance, community support, payroll, marketing), the sales-and-marketing split table and employee counts from 10-Ks.
- Numbers: GAAP cost lines from SEC XBRL (Q4 derived as FY less nine months; operations and support backed out of total costs). Adjusted EBITDA from letters. All GAAP lines include stock-based compensation, which Adjusted EBITDA excludes, so line-item percentages in sections 3.3 and 4 overstate cash cost; total SBC is shown separately.
- Cash stack, bridge and scenarios (sections 3.5, 10, 11): SBC by function and the Adjusted EBITDA reconciliation parsed from every letter's footnotes (`analysis/src/abnb_exsbc_stack.py`), then decomposed and projected in `analysis/src/abnb_margin_bridge.py`. Nights, GBV and ADR from `data/processed/abnb_quarterly_kpis_from_study.csv`.
- Caveat: speaker attribution in the 2020 to 2022 web transcripts is imperfect; quotes from those calls are attributed by content (Chesky versus Stephenson) and cross-checked against the letters.

---

## 3. The margin record

### 3.1 Full year

| FY | Revenue $M | Adj. EBITDA $M | Adj. EBITDA margin | FCF margin | Employees (Dec 31) | Brand+perf. marketing $M | Field ops & policy $M | Total S&M % rev |
|---|---|---|---|---|---|---|---|---|
| 2019 | 4,805 | -253 | -5% | 2% | ~7,200* | 1,140 | 481 | 34% |
| 2020 | 3,378 | -251 | -7% | neg. | 5,597 | 479 | 697 | 35% |
| 2021 | 5,992 | 1,592 | 27% | 37% | 6,132 | 723 | 463 | 20% |
| 2022 | 8,399 | 2,903 | 35% | 41% | 6,811 | 1,030 | 486 | 18% |
| 2023 | 9,917 | 3,653 | 37% | 39% | 6,907 | 1,208 | 555 | 18% |
| 2024 | 11,102 | 4,041 | 36% | 40% | ~7,300 | 1,455 | 693 | 19% |
| 2025 | 12,241 | 4,297 | 35% | 38% | ~8,200 | 1,595 | 993 | 21% |
| 2026E (guide) | at least mid-teens growth | | at least 35.5% | | growth "lower than 2025" | | | |

*2019 headcount is implied from Stephenson's Q4 2022 remark that end-2022 headcount (6,811) was 5% below 2019. Adjusted EBITDA is the sum of the quarterly letter figures. S&M split from 10-K tables; FCF margins from letters.

### 3.2 Quarterly Adjusted EBITDA margin (seasonality is large; compare same quarters)

| | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| 2021 | -7% | 16% | 49% | 22% |
| 2022 | 15% | 34% | 51% | 27% |
| 2023 | 14% | 33% | 54% | 33% |
| 2024 | 20% | 33% | 52% | 31% |
| 2025 | 18% | 34% | 50% | 28% |
| 2026 | 19% | 35% | guided "down slightly" | |

### 3.3 GAAP cost lines as a percent of revenue (incl. SBC), same-quarter view

| Line | Q2 22 | Q2 23 | Q2 24 | Q2 25 | Q2 26 | | Q3 22 | Q3 23 | Q3 24 | Q3 25 |
|---|---|---|---|---|---|---|---|---|---|---|
| Cost of revenue | 18.5 | 17.4 | 18.4 | 17.6 | 17.5 | | 13.9 | 13.5 | 12.5 | 13.4 |
| Operations & support | 12.3 | 12.8 | 12.3 | 10.7 | 10.0 | | 10.1 | 9.3 | 9.9 | 8.9 |
| Product development | 17.8 | 18.2 | 18.9 | 19.7 | 18.6 | | 12.7 | 12.3 | 14.0 | 14.3 |
| Sales & marketing | 18.0 | 19.6 | 20.9 | 22.3 | 24.3 | | 13.3 | 11.9 | 13.8 | 15.6 |
| G&A | 11.6 | 11.1 | 11.5 | 9.9 | 8.6 | | 8.3 | 8.9 | 9.0 | 8.1 |
| Total SBC (memo) | 11.7 | 12.2 | 13.9 | 13.7 | 13.5 | | 8.1 | 8.4 | 9.7 | 9.7 |
| Adj. EBITDA margin | 34 | 33 | 33 | 34 | 35 | | 51 | 54 | 52 | 50 |

Full year 2022 to 2025 tells the same story: cost of revenue 17.8% to 17.0%, operations and support 12.4% to 10.8%, product development 17.9% to 19.2%, sales and marketing 18.0% to 21.1%, G&A 11.3% to 11.0% (2023 was 20.4% because of the one-time tax items), SBC 11.1% to 12.9%. Full series in the CSV.

### 3.4 ADR against US lodging prices: Airbnb has been pricing up while hotels priced down

Source: `data/processed/abnb_kpi_vs_category_quarterly.csv` (ADR from the shareholder letters; BEA PCE hotels-and-motels price index and CPI lodging away from home, quarterly averages; built from the BEA extract in `data/raw/bea/` and FRED). Implied ADR (GBV divided by nights) matches reported ADR within 50 cents every quarter, so the letters' ADR is a clean GBV-per-night figure.

| | Q1 24 | Q2 24 | Q3 24 | Q4 24 | Q1 25 | Q2 25 | Q3 25 | Q4 25 | Q1 26 | Q2 26 |
|---|---|---|---|---|---|---|---|---|---|---|
| ABNB ADR y/y | +2.6 | +2.1 | +1.4 | +0.9 | -0.9 | +2.9 | +4.7 | +5.9 | +9.0 | +5.3 |
| BEA hotels & motels price y/y (US) | -0.9 | -1.7 | -1.5 | +1.8 | -0.1 | -2.6 | -3.1 | -3.2 | -2.2 | +4.9 |
| CPI lodging away from home y/y | -0.6 | -1.2 | -0.9 | +1.8 | +0.5 | -1.6 | -1.9 | n/a | -0.2 | +4.7 |
| ABNB nights y/y | +9 | +9 | +8 | +12 | +8 | +7 | +9 | +10 | +9 | +10 |
| BEA real US accommodations y/y | +5.7 | +4.1 | +1.4 | -1.7 | -2.8 | +1.1 | +2.1 | +2.8 | +4.7 | +0.9 |

- **The 2025 to 2026 ADR tailwind was Airbnb-specific, not category inflation.** From Q2 2025 to Q1 2026 ABNB's ADR rose 3% to 9% while US hotel prices fell 2% to 3%. Part of that is FX (roughly half of revenue is non-USD and the dollar weakened) and mix, which management separates in the letters; but even the ex-FX ADR (+4% in 1H 2026) was running 5 to 6 points above hotels. This is the gap the Q2 2026 analysts asked about ("ADR vs. hotels") and it is the single biggest source of the revenue upside that funded the margin raises.
- **Q2 2026 is the first quarter the gap closed**: hotels +4.9%, ABNB +5.3%. If hotel pricing has turned, ABNB's real ADR advantage is gone and revenue growth reverts to nights plus take rate.
- **Share test.** ABNB nights growth has exceeded real US accommodations spending growth in every quarter since Q3 2022, by 4 to 14 points. The US lodging category is running low-single-digit real; Airbnb's growth is share, not category. The caveat is that BEA counts US-resident spend only and ABNB nights are global, so the comparison is directional.

---

### 3.5 The cash cost stack: what Adjusted EBITDA actually pays for

Source: `data/processed/abnb_quarterly_cost_stack_exsbc.csv` (script `analysis/src/abnb_exsbc_stack.py`). Each GAAP line less its own SBC from the letters' footnote, checked against the Adjusted EBITDA reconciliation every quarter (identity holds to within $2M except 4Q23, where the letter's quarterly SBC and the XBRL-derived Q4 differ by $20M and the $935M tax reserve sits in G&A).

| FY | Cost of revenue | Ops & support | Product dev | S&M | G&A | D&A and add-backs | Adj. EBITDA margin |
|---|---|---|---|---|---|---|---|
| 2022 | 17.8 | 11.6 | 11.4 | 16.7 | 8.9 | +1.0 | 34.6 |
| 2023 | 17.2 | 11.3 | 10.7 | 16.4 | 18.2* | +10.2* | 36.8 |
| 2024 | 16.9 | 10.7 | 10.5 | 17.8 | 8.3 | +0.7 | 36.4 |
| 2025 | 17.0 | 10.1 | 10.9 | 19.4 | 8.7 | +1.3 | 35.1 |

Percent of revenue, cash basis. *2023 G&A carries about $935M of Italy withholding and lodging-tax reserves that Adjusted EBITDA adds back; ex that item G&A was about 8.8%.

Same-quarter cash view, Q2: S&M 16.6% (2022), 18.1%, 19.2%, 20.6%, 22.4% (2026); operations and support 11.5%, 12.0%, 11.4%, 10.0%, 9.0%; product development 10.9%, 10.5%, 10.2%, 10.7%, 10.4%; G&A 8.9%, 8.7%, 8.8%, 7.7%, 6.2%. Product development on a cash basis has been flat for four years; the GAAP creep in that line is entirely SBC (product SBC $145M in Q2 2022 to $298M in Q2 2026, 55% to 61% of all SBC).

Three things the cash view changes about the story in section 4:

- **Product development is not where the money went.** Cash product spend has been 10% to 11% of revenue every year since 2022. Headcount growth shows up in SBC, which Adjusted EBITDA excludes and free cash flow does not.
- **Operations and support is the quiet source of leverage**: cash cost per night fell from $2.48 (2022) to $2.32 (2025) and to about $2.05 in 1H 2026, before the AI agent had reached voice or most languages.
- **Sales and marketing is the whole margin story since 2023.** Cash S&M per night rose from $3.56 (2022) to $4.46 (2025) and ran $5.05 in 1H 2026 (annualized). Every other cash line per night is flat or down.

---

## 4. Anatomy of the P&L: what each line is and what management says moves it

**Cost of revenue (17% to 18% of revenue; 21% to 24% in Q1s).** Merchant fees and chargebacks (payment processing was about 2% of GBV in 2019 and 2021 per the 10-K), cloud hosting, SMS and authentication, amortization of internal-use software. Drivers cited: pay-in volume (so GBV, not revenue), chargeback rate (fell in 2024 and 2025 after the quality purge, ticked up "slightly" in 1H 2026), processor rebates and incentives (one-time benefit in Q2 2023; "higher payment processor rebates and incentives" offsetting fee growth in Q1 2026), server costs (reserved-instance amortization up in 2026). Because this line scales with GBV, the implied take rate is the swing: a flat take rate with ADR growth is margin-accretive, and the 2026 customer incentives that hold the take rate flat are a direct margin cost.

**Operations and support (11% to 12%, falling).** Third-party community-support agents, in-house support payroll, "customer relations" (refunds, credits, make-goods, host protection payouts), host liability insurance premiums (scale with nights), facilities and IT allocation. Management's stated levers: contact-rate reduction through product fixes and listing quality (Guest Favorites listings get fewer contacts; 550,000+ low-quality listings removed), dedicated Superhost support, and since 2025 the AI agent. The Q2 2026 10-Q is the first filing to name it: "a $17 million decrease in third-party service provider costs due to lower agent contact volume resulting from increased use of AI in community support." Offsets in 2026: higher make-good payouts and case reserves, and insurance premiums.

**Product development (17% to 19%, roughly flat, rising in GAAP because of SBC).** Almost entirely payroll. This is where headcount growth lands: "we will be slightly increasing our pace of head count growth across our product development organization" (Mertz, Q4 2024). Management position since 2021: grow it slower than revenue, but 2024 and 2025 broke that (+19% and +14% versus revenue +12% and +10%). 2026: "we don't need to grow our head count at levels that we did in the past because we're getting so much more output and speed from our existing workforce" (Mertz, Q2 2026); SBC and headcount growth guided lower than 2025.

**Sales and marketing (18% to 21% and rising).** Two halves. Brand and performance marketing: brand is described as a fixed spend per market ("effectively a fixed amount of spend for each market in terms of the minimum amount that you need to spend for that market to be efficient", Mertz, Q4 2024), performance is a "surgical topper" used to balance supply and demand, and PR is the top of the funnel. Field operations and policy: local teams, supply acquisition, go-to-market for services, experiences and hotels, policy and communications. The 2025 investment of about $200M in new businesses landed here and in product development, and Mertz was explicit that it was "not an increase in programmatic marketing." In Q2 2026 management guided marketing to keep growing faster than revenue, citing emerging-market paid growth and partnerships (Delta is a revenue share).

**G&A (9% to 11%).** Payroll for finance, legal, HR; professional fees; D&O insurance; non-income taxes including lodging-tax reserves and the Italy withholding settlement (about $935M in Q4 2023). Leverage here is real and unglamorous; non-income taxes fell $38M in 1H 2026.

**Stock-based compensation (about 13% of revenue).** Excluded from Adjusted EBITDA. Guided +20% for 2023 and 2024, came in +20% and +26%; +13% in 2025 "driven by headcount growth"; 2026 growth "lower than 2025." Until the last double-trigger IPO RSUs vested (2024), SBC grew faster than headcount for accounting reasons. This matters for the EBITDA-to-FCF bridge and for the gap between Adjusted EBITDA margin (35%) and GAAP operating margin (21% in Q2 2026).

**Two cross-cutting drivers management names every year.** ADR: "Full year revenue and Adjusted EBITDA will be highly sensitive to movements in ADR" (Q4 2021 letter); the 2023 guide of flat margin was explicitly "offset the headwinds from lower ADR with incremental variable cost efficiencies and fixed cost discipline." FX: "approximately 46% [to 58%] of our GAAP revenue was denominated in non-USD currencies, while a minority of our total costs and expenses were denominated in non-USD currencies" (letters 2022 to 2024), so a strong dollar compresses margin; a revenue hedging program limits the 2025 to 2026 tailwind (Mertz, Q1 2025).

---

## 5. Quarter-by-quarter: what management said the margin did, what it guided, and why

Adjusted EBITDA margin is the reported figure. "Guided" is the forward statement made on that call or letter; "outcome" is what the next print showed.

| Call | Margin (YoY) | Why, per management | Forward margin guidance and reasons | Outcome |
|---|---|---|---|---|
| Q4 2020 (Feb 2021) | -2% (vs -25%) | All opex lines ex-SBC down YoY; discretionary cuts, variable-cost work, fixed-cost cuts | No FY guide. Q1 lowest margin; H1 below H2 (seasonality plus investment); S&M and ops-and-support % higher in H1 (Made Possible by Hosts campaign, support hiring ahead of rebound). Stephenson: "we would expect to achieve over time 30% EBITDA margins or greater." Chesky: never again spend 2019's marketing % | Q1 2021 -7% |
| Q1 2021 | -7% (vs -40%) | Improved variable costs, marketing efficiency, fixed-cost management; ADR +35% mostly mix | Q2 margin breakeven to slightly positive; H2 above H1. Warned ADR mix reversal "may impact our revenue and margins." Product development to grow slower than revenue | Q2 16% |
| Q2 2021 | 16% (+2,000 bps vs 2019) | Revenue recovery plus improved cost structure | Q3 to be highest EBITDA dollars and margin ever; S&M and ops-and-support % lower in H2. Stephenson on sustainability: "we can achieve this 30% margins or more" and ADR is helping | Q3 49% |
| Q3 2021 | 49% (+3,000 bps vs 2019) | Record revenue, continued cost management | Q4 margin expansion YoY greater than Q3's; marketing % "in this kind of range for the foreseeable future"; ADR to moderate as urban, APAC, LatAm return | Q4 22% |
| Q4 2021 (Feb 2022) | 22% (vs -25%); FY 27% (vs -5%) | Revenue growth plus expense discipline; ADR tailwind | First positive Q1 ever. FY2022 margin "directionally in line with 2021": marketing % flat (a "new baseline" reached), fixed-cost leverage and variable-cost gains "potentially offset by lower ADR." Ops-and-support % roughly flat (investing in support) | FY2022 35%; ADR did not fall |
| Q1 2022 | 15% (vs -7%) | Per-unit variable cost, marketing efficiency, fixed-cost discipline; 16% fewer people than Q1 2020 | Q2 margin up low-double-digit points YoY; FY "modest" expansion, weighted to H1; S&M % flat | Q2 34% |
| Q2 2022 | 34% (vs 16%) | Same; $2B buyback announced | Q3 margin "at or slightly below" 49% on expense timing; FY expansion. Stephenson: "heavily in growth mode... not in profit maximization mode"; headcount growth high-single-digit | Q3 51% |
| Q3 2022 | 51% (vs 49%) | All recurring opex lines ex-SBC except S&M grew slower than revenue; hiring plan unchanged | Q4 margin in line to modestly above 22%. FCF margin sustainable via variable-cost gains and fixed leverage; ADR moderation "a little bit of headwind"; 2023 marketing % similar to 2022; experiences will not show in the P&L | Q4 27% |
| Q4 2022 (Feb 2023) | 27% (vs 22%); FY 35% | Revenue growth, expense discipline | FY2023 margin flat with 2022: ADR down modestly (mix plus new host pricing tools) offset by variable-cost efficiencies and fixed-cost discipline (headcount +2% to 4%). Q1 margin slightly down on brand-marketing pull-forward (S&M +150 bps in Q1, flat FY). "I have a long list of things that we can invest in... I am not in profit maximization mode" | FY2023 37%; ADR rose |
| Q1 2023 | 14% (vs 15%) | Brand spend pulled into H1 and extended to more countries (Germany, Brazil) | Q2 EBITDA similar nominal, margin lower; S&M +400 bps YoY in Q2; FY broadly in line with 2022. Stephenson: margin expansion "not my primary focus right now" | Q2 33% |
| Q2 2023 | 33% (vs 34%) | Marketing timing | Q3 record EBITDA and margin above Q3 2022; FY "modestly higher" than 2022 (first upgrade). "I don't have a new long-term target." AI to give fixed and variable cost leverage over time | Q3 54% |
| Q3 2023 | 54% (vs 51%) | All opex ex-SBC except G&A ($49M lodging taxes) grew slower than revenue; fixed headcount +4% | Q4 record EBITDA, margin above Q4 2022; FY about 150 bps above 2022. SBC +20% in 2023 and 2024, then in line with headcount | Q4 33%; FY 37% |
| Q4 2023 (Feb 2024) | 33% (vs 27%); FY 37% | Stable ADR, cost discipline; ~$1B non-recurring taxes in GAAP G&A only | **First "floor": FY2024 at least 35%**, "slightly down," to keep "flexibility to invest": international expansion budget, high-ROI marketing channels, product headcount. Marketing % flat; brand into 20 countries. Q1 margin up on Easter timing. Long-term expansion to come "from hosting guest services and experiences" (Stephenson) | FY2024 36% |
| Q1 2024 | 20% (vs 14%) | Easter timing, cost discipline | Q2 nominal flat to up, margin down: Easter reversal, one-time payment-processing incentives in Q2 2023, heavier Q2 marketing. FY at least 35%. Expansion markets: same take rate, attractive contribution profit | Q2 33% |
| Q2 2024 | 33% (flat) | Broad cost discipline; H1 marketing % flat | Q3 EBITDA about flat nominal, margin down: marketing to grow faster than revenue (LatAm market launches, performance marketing). FY at least 35%; FCF margin several points above EBITDA. "We don't anticipate any kind of sea change in the foreseeable future around overall profitability levels" | Q3 52%; stock -14% on nights guide, not margin |
| Q3 2024 | 52% (vs 54%) | S&M grew faster than revenue (global markets, performance marketing); SBC now +25% | Q4 margin down several points on marketing and product development (timing plus Icons, expansion markets). **FY raised to about 35.5%.** 2025 philosophy: find variable-cost efficiencies every year, reinvest in core, expansion markets, new products; investments "front run the revenue" | Q4 31% |
| Q4 2024 (Feb 2025) | 31% (vs 33%); FY 36% | S&M and product-development investment | Q1 2025 margin down on calendar and FX (flat ex those). **FY2025 at least 34.5%** including $200M to $250M to launch new businesses, hitting marketing and product development, heaviest in the first nine months. Efficiencies: payment processing, customer service, G&A; core marketing flat % of revenue; take rate +20 bps from FX fee | FY2025 35% |
| Q1 2025 | 18% (vs 20%) | Calendar and FX; product-development investment | Q2 margin flat to slightly down; marketing faster than revenue (Summer Release). FY at least 34.5%; investment impact now "most pronounced in the second half." FX turned from headwind to tailwind but hedging and LatAm limit it | Q2 34%; stock -7% |
| Q2 2025 | 34% (vs 32.5%) | Higher revenue | Q3 EBITDA above $2.0B, margin below Q3 2024 on "new growth and policy initiatives"; Q4 similar decline. FY at least 34.5% incl. about $200M (refined). The $200M is headcount, field operations, vendors, not programmatic marketing; some carries into 2026 as fixed headcount | Q3 50% |
| Q3 2025 | 50% (vs 52%) | Growth and policy investment | Q4 EBITDA flat to down, margin down. **FY raised to about 35%.** 2026: "maintaining strong margins while continuing to invest"; 2025 was the heavy launch year | Q4 28%; FY 35% |
| Q4 2025 (Feb 2026) | 28% (vs 31%); FY 35% | Investment; take rate 13.6% vs 14.1% (FX, RNPL timing) | Q1 2026 margin flat. **FY2026 "stable"** as efficiencies are reinvested "primarily in marketing, product, and technology." Cost of revenue and ops-and-support to "scale somewhat linearly"; incremental spend in go-to-market and supply acquisition (homes, experiences, services, hotels) and product development. AI "will not affect the P&L" via capex; SBC growth lower than 2025 | Q1 19%, +24% nominal |
| Q1 2026 | 19% (vs 18%) | Revenue beat; support cost per booking -10% | Q2 EBITDA and margin up YoY. **FY raised to at least 35%.** Topline upside partly reinvested: high-ROI marketing, expansion markets, AI initiatives (an internal AI expense "that will ramp over the course of the year") | Q2 35% |
| Q2 2026 (Aug 2026) | 35% (+100 bps) | Revenue growth plus efficiencies in ops-and-support and product development, partly offset by S&M | Q3 EBITDA up, margin "down slightly" versus 50% on investment timing. **FY raised to at least 35.5%**, "stronger topline growth and underlying operating leverage in our core business." Guide "does assume a material increase in terms of the AI spend"; offsets are support cost per booking -16% and slower headcount growth. Take rate flat for 2026 (RNPL timing, customer incentives for new businesses). No 2027 view; "there's a relative floor" | Q3 reports Nov 2026 |

### 5.1 The revenue guidance cushion: every guided quarter has beaten the midpoint

Source: next-quarter revenue ranges and reported actuals from Theo's guidance dataset (`theos-past-research/research/guidance/data/normalized/`, extracted from the SEC-filed shareholder letters with pinpoint excerpts), copied to `data/processed/abnb_revenue_guidance_vs_actual.csv`. The first three guides (Q1 to Q3 2021) were qualitative and are excluded. Guidance is in reported currency, so FX explains part of the beat in weak-dollar quarters (Q4 2025 to Q2 2026).

| Guided quarter | Guided on | Range $M | Midpoint | Actual | vs midpoint | vs top of range |
|---|---|---|---|---|---|---|
| Q4 2021 | Q3 2021 call | 1,390 to 1,480 | 1,435 | 1,532 | +6.8% | +3.5% |
| Q1 2022 | Q4 2021 call | 1,410 to 1,480 | 1,445 | 1,509 | +4.4% | +2.0% |
| Q2 2022 | Q1 2022 call | 2,030 to 2,130 | 2,080 | 2,104 | +1.2% | -1.2% |
| Q3 2022 | Q2 2022 call | 2,780 to 2,880 | 2,830 | 2,884 | +1.9% | +0.1% |
| Q4 2022 | Q3 2022 call | 1,800 to 1,880 | 1,840 | 1,902 | +3.4% | +1.2% |
| Q1 2023 | Q4 2022 call | 1,750 to 1,820 | 1,785 | 1,818 | +1.8% | -0.1% |
| Q2 2023 | Q1 2023 call | 2,350 to 2,450 | 2,400 | 2,484 | +3.5% | +1.4% |
| Q3 2023 | Q2 2023 call | 3,300 to 3,400 | 3,350 | 3,397 | +1.4% | -0.1% |
| Q4 2023 | Q3 2023 call | 2,130 to 2,170 | 2,150 | 2,218 | +3.2% | +2.2% |
| Q1 2024 | Q4 2023 call | 2,030 to 2,070 | 2,050 | 2,142 | +4.5% | +3.5% |
| Q2 2024 | Q1 2024 call | 2,680 to 2,740 | 2,710 | 2,748 | +1.4% | +0.3% |
| Q3 2024 | Q2 2024 call | 3,670 to 3,730 | 3,700 | 3,732 | +0.9% | +0.1% |
| Q4 2024 | Q3 2024 call | 2,390 to 2,440 | 2,415 | 2,480 | +2.7% | +1.6% |
| Q1 2025 | Q4 2024 call | 2,230 to 2,270 | 2,250 | 2,272 | +1.0% | +0.1% |
| Q2 2025 | Q1 2025 call | 2,990 to 3,050 | 3,020 | 3,096 | +2.5% | +1.5% |
| Q3 2025 | Q2 2025 call | 4,020 to 4,100 | 4,060 | 4,095 | +0.9% | -0.1% |
| Q4 2025 | Q3 2025 call | 2,660 to 2,720 | 2,690 | 2,778 | +3.3% | +2.1% |
| Q1 2026 | Q4 2025 call | 2,590 to 2,630 | 2,610 | 2,678 | +2.6% | +1.8% |
| Q2 2026 | Q1 2026 call | 3,540 to 3,600 | 3,570 | 3,608 | +1.1% | +0.2% |
| Q3 2026 | Q2 2026 call | 4,690 to 4,770 | 4,730 | reports 5 Nov 2026 | | |

- **19 for 19 above the midpoint**, mean beat +2.5%, and above the top of the range 15 times. The smallest beats (+0.9% to +1.2%) all came in Q2 or Q3 guides, the biggest (+3% to +7%) in Q4 and Q1 guides, so the cushion is widest in the seasonally small quarters.
- **The range has narrowed and so has the cushion.** Range width as a percent of the midpoint: 6% (2021), 4.4% (2022), 3.2% (2023), 2.0% (2024 and 2025), 1.6% (2026). Average beat versus midpoint: 2.7% (2022), 2.5% (2023), 2.4% (2024), 1.9% (2025), 1.8% (2026 so far). Management is guiding tighter and closer, which is consistent with the shorter booking window and the RNPL timing effects it keeps citing.
- **Applied to Q3 2026:** the $4.69B to $4.77B guide is +14.5% to +16.5% YoY on Q3 2025's $4,095M. The 2025 to 2026 average cushion of about 2% puts the actual near $4.82B, or +18%, roughly a point above the FY "at least mid-teens" pace. A print below the midpoint would be the first since guidance began.
- **The margin guide shows the same habit** (section 7): every full-year margin floor since 2023 has been beaten by 60 to 180 bps. Treat both floors as floors, not forecasts, in the model.

---

## 6. The recurring drivers, sorted

**Structural tailwinds management leans on**
- Marketing model: brand is fixed per market, performance is surgical, 90% of traffic direct. Leverage in core markets is used to fund expansion markets rather than dropped to the bottom line (Q4 2024 call).
- Variable-cost efficiency "every year": payments (processor rebates, chargebacks), community support (contact rates, AI agent), infrastructure. Mertz's stated operating rule since Q3 2024: find efficiencies in the core each year and reinvest part of them.
- Quality flywheel: removing listings and steering to Guest Favorites lowers contacts, chargebacks and cancellations, which shows up in operations and support and cost of revenue.
- Revenue per night: ADR, FX-adjusted, plus monetization that does not raise cost (guest travel insurance revenue +40% in 2025; single 15.5% service fee migration; FX service fee since mid-2024).
- Capital-light new businesses: "mostly head count... hundreds of people, not thousands" (Chesky, Q2 2024); partner-fulfilled services "we do not see a big incurring of cost" (Q2 2026); hotels "not really an incremental investment" (Q3 2025).

**Structural headwinds and commitments**
- Sales and marketing growing faster than revenue since 2024: +22% and +20% in 2024 and 2025 against revenue +12% and +10%, then +30% in 1H 2026 against revenue +18% (2023 was the last year it lagged, +16% against +18%).
- Product-development headcount and SBC (about 13% of revenue) rising with the "AI-native" build-out and new offerings; some 2025 launch costs are now fixed.
- AI inference and tooling spend, described as material in the 2026 guide even though management frames it as opex not capex.
- Customer incentives for new businesses, which appear as contra-revenue and hold the take rate flat in 2026.
- Insurance premiums and make-good payouts scale with nights; RNPL raised the aggregate cancellation rate from about 16% to about 17%.

**Timing and noise that explain most guidance "misses"**
- Brand-marketing phasing between quarters (Q1 2023, Q2 2023, Q2 2024, Q3 2024, Q3 2026 all guided down on timing).
- Easter and leap day (Q1 2024 up, Q2 2024 and Q1 2025 down).
- FX on the revenue line versus a USD cost base; management quantified FX as a 600 bps drag on Q1 2022 revenue growth and a roughly 3-point tailwind in 1H 2026.
- One-offs: Q2 2023 processor incentives, Q4 2023 gift-card breakage, Q4 2023 tax reserves (GAAP only), Q3 2025 discrete tax items (below EBITDA).
- Booking-versus-stay timing in the implied take rate (RNPL lowers unearned fees in Q1 and Q2 and raises them in Q3).

---

## 7. What the forward view looks like and what has to be true

**Guided:** FY2026 Adjusted EBITDA margin at least 35.5% on at least mid-teens revenue growth; Q3 2026 margin down slightly from 50%; take rate flat; SBC and headcount growth below 2025; effective tax rate mid-to-high teens. Nothing for 2027.

**Management's stated logic:** the core business has "extremely strong" unit economics and a "relative floor"; each year efficiencies are harvested (support cost per booking, payments, G&A, headcount productivity from AI tooling) and mostly reinvested in marketing, international expansion, new offerings and AI; margin expands only when revenue upside exceeds what management chooses to reinvest, which is what happened in 2026 (guide raised twice as revenue growth moved from "low double digits" to "at least mid-teens"). Long term, Mertz says "there is opportunity for further margin expansion" (Q3 2024) and both CFOs have located it in services, experiences and other incremental offerings rather than in the take rate or in core cost cuts.

**What has to be true for at least 35.5% in 2026:** H2 revenue growth holds mid-teens while lapping RNPL (US launch Q3 2025, merchandising Q4 2025) and as the roughly 3-point FX tailwind fades; ADR ex-FX stays positive (+4% in 1H 2026); the AI support savings keep compounding (management expects further declines as voice and more languages roll out); S&M growth slows from the 30% pace of 1H; no repeat of Q4 2025's 28% margin (the Q4 2026 margin implied by the FY floor is roughly 29% to 31% depending on Q3).

**Where a downside comes from:** ADR or FX reversal with a USD cost base; management choosing to reinvest more (the floor language leaves room to go down to the floor); a nights slowdown that makes brand spend per market deleverage; incentives for hotels, services and experiences pressuring take rate; SBC and headcount re-accelerating for the AI build.

**Where an upside comes from:** the AI-support and headcount-productivity lines are already in the run rate and management has under-guided the full-year margin by 60 to 180 bps every year since it started guiding it (2023: flat with 2022's 34.6% guided, 36.8% delivered; 2024: 35% floor, 36.4%; 2025: 34.5% floor, 35.1%; 2026: "stable" in February, at least 35.5% by August). The revenue guide is under-guided the same way (section 5.1: 19 of 19 quarters above the midpoint, mean +2.5%). A year in which management stops the reinvestment cycle would show operating leverage quickly: cost of revenue, operations and support and G&A together fell about 3 points of revenue between 2022 and 2025 while S&M and product development rose about 4.5 points, and the difference is roughly the 1.8-point rise in SBC, which Adjusted EBITDA excludes. On a cash-cost basis the core has been getting cheaper the whole time.

---

## 8. Quotes worth citing

- "What we would expect to achieve over time is 30% EBITDA margins or greater." Dave Stephenson, Q4 2020 call. (The only explicit long-term target; hit in 2021.)
- "We don't intend to ever again spend the amount of money as a percentage of revenue on marketing in the future as we did in 2019." Brian Chesky, Q4 2020 call.
- "The tailwind of average daily rate... definitely helped our margins." Stephenson, Q4 2021 call.
- "We are not in profit maximization mode... we are heavily in growth mode." Stephenson, Q2 2022 call; repeated Q4 2022, Q1 2023, Q2 2023.
- "Also remember that the higher average daily rates have helped our overall margins, so it kind of accelerated overall profitability... I don't have a new long-term target." Stephenson, Q2 2023 call.
- "We are basically giving ourselves a floor in terms of the full-year EBITDA margin guidance." Ellie Mertz, Q4 2023 call.
- "Brand marketing... is effectively a fixed amount of spend for each market... we are not adding dollar for dollar as revenue increases, and therefore, the marketing budget is allowed to expand and be more heavily dedicated to expansion markets." Mertz, Q4 2024 call.
- "The intent both with the core and the new businesses is to invest in growth upfront and to optimize the margins over time." Mertz, Q1 2025 call.
- "The $200 million... is not an increase in programmatic marketing... it is focused in particular on our field operations, our go-to-market activities and supply acquisition." Mertz, Q2 2025 call.
- "Our investment in AI will not affect the P&L. I don't think you'll see it in the P&L." Chesky, Q4 2025 call. Versus: "the updated guidance that we've provided obviously does assume a material increase in terms of the AI spend over the course of the year." Mertz, Q2 2026 call.
- "Given the track record and the somewhat steady EBITDA margins that we have delivered, I think you can see there's a relative floor in our ability to continue to invest against that." Mertz, Q2 2026 call.

---

## 9. Open items

- Adjusted EBITDA by cost line is not disclosed; the ex-SBC cost mix can be rebuilt from the SBC-by-function tables in each letter if the deck needs it.
- Payment processing as a percent of GBV has not been disclosed since the FY2021 10-K; cost of revenue as a percent of GBV (about 2.3% in 2025) is the proxy.
- Contribution margin of services, experiences and hotels has never been quantified; the Q&A record shows analysts asking on Q2 2024, Q3 2025 and Q2 2026 without a number.
- Stock reactions to margin guidance are in `research/airbnb_earnings_call_study.md` section 8; the clearest margin-driven moves were Q4 2023 (floor introduced), Q3 2024 (Q4 margin guide implied 27% to 28%) and Q2 2025.
- The 1Q21 and 2Q21 letters carry no SBC-by-function footnote (it is in the 10-Qs), so the cash stack starts in 3Q21.

---

## 10. Margin bridge: where the 2022 to 2025 margin went

Source: `data/processed/abnb_margin_bridge.csv` (script `analysis/src/abnb_margin_bridge.py`). Method: each cash line is written as cost per night divided by revenue per night. The change in a line's share of revenue is split into a unit-cost effect (cost per night moved, revenue per night held) and a revenue-per-night effect (denominator moved). The revenue-per-night effect is then split log-linearly into take rate, FX and ADR ex-FX, using the reported-versus-ex-FX revenue growth in the letters (FX cost 6 points in 2022, added 1 point in 2023, nil in 2024 and 2025). Nights booked are the unit; revenue follows stays, so the per-night figures are approximate within a year and clean across years.

| Component (margin points) | FY2022 to FY2025 | FY2024 to FY2025 |
|---|---|---|
| ADR ex-FX (revenue per night) | +3.7 | +1.9 |
| FX (revenue per night) | +0.7 | 0.0 |
| Take rate (revenue per night) | +0.7 | -0.8 |
| Operations & support, cash cost per night ($2.48 to $2.32) | +0.8 | +0.5 |
| Cost of revenue per night ($3.81 to $3.91) | -0.5 | -0.4 |
| Product development, cash per night ($2.42 to $2.51) | -0.4 | -0.6 |
| G&A, cash per night ($1.89 to $2.01) | -0.5 | -0.6 |
| Sales & marketing, cash per night ($3.56 to $4.46) | -4.2 | -1.9 |
| D&A and add-backs | +0.3 | +0.6 |
| **Change in Adjusted EBITDA margin** | **+0.5 (34.6% to 35.1%)** | **-1.3 (36.4% to 35.1%)** |

Reading it:

- **Revenue per night paid for the marketing ramp.** ADR ex-FX, FX and take rate together added 5.1 points between 2022 and 2025; sales and marketing alone took back 4.2 of them. Without the ADR windfall, margin would have fallen about 3 points over the period at the same spending.
- **The 2025 decline was take rate plus S&M.** Take rate fell 16 bps (RNPL timing, FX, incentives) for -0.8 points, and S&M cash per night rose 11% for -1.9 points. ADR ex-FX (+1.9) and support efficiency (+0.5) covered most of it.
- **Cost of revenue is a slow leak**: cash cost per night rose from $3.81 to $3.91 because it scales with GBV, not nights, and ADR rose 6.5%. It is only a margin problem when ADR rises faster than take rate.
- **The FY2023 to FY2025 bridge is dominated by the 2023 one-off** (G&A +9.2, add-backs -8.9, netting to +0.2) and is in the CSV but not shown here.

---

## 11. Scenarios: FY2026, FY2027, and the Q3 and Q4 2026 prints

Source: `data/processed/abnb_margin_scenarios.csv`; assumptions in the `SCEN` block of `analysis/src/abnb_margin_bridge.py`. Bottom-up: nights, ADR ex-FX, FX, take rate, cost of revenue per GBV dollar, support cost per night, product development, S&M and G&A cash growth, add-backs at 0.9% of revenue. FY2026 first-half actuals are fixed; Q3 uses the guide midpoint ($4.73B) and Q4 is the remainder.

| | Bear | Base | Bull |
|---|---|---|---|
| FY26 nights / ADR ex-FX / FX | +9.5% / +3% / +2% | +10% / +3.5% / +2% | +10.5% / +4% / +2.5% |
| FY26 take rate vs 13.41% | -5 bps | flat | +5 bps |
| FY26 support cost per night | -4% | -5% | -7% |
| FY26 product dev / S&M / G&A cash growth | +11% / +24% / +1% | +11% / +25% / 0% | +10% / +22% / 0% |
| **FY26 revenue growth** | +14.6% | +16.1% | +18.2% |
| **FY26 Adj. EBITDA margin** | **35.3%** | **35.9%** | **37.7%** |
| Q3 2026E margin (guide: "down slightly" from 50.1%) | 48.3% | 49.0% | 50.2% |
| Q4 2026E margin implied (Q4 2025: 28.3%) | 29.4% | 31.5% | 37.5% |
| FY27 nights / ADR ex-FX / FX | +6% / +1% / -1.5% | +9% / +3% / 0% | +10% / +3.5% / +0.5% |
| FY27 take rate change | -15 bps | flat | +10 bps |
| FY27 support per night / product dev / S&M / G&A | -2% / +8% / +9% / +4% | -5% / +9% / +17% / +5% | -7% / +8% / +18% / +3% |
| **FY27 revenue growth** | +4.3% | +12.3% | +15.3% |
| **FY27 Adj. EBITDA margin** | **33.8%** | **36.5%** | **39.8%** |

- **The floor case.** If FY2026 lands exactly on the 35.5% floor with revenue up 15% to 16% and Q3 at 49%, Q4 must print 29.4% to 29.6%, roughly Q4 2025's 28.3% plus a point. The base case (35.9%) needs Q4 at 31.5%, which is what the 1H run-rate of support savings and a slower S&M growth rate in H2 (+21% versus +30% in H1) delivers. Management has beaten every floor since 2023 by 60 to 180 bps, so a 35.9% base is conservative by that history and aggressive only if the AI spend Mertz flagged is larger than the support savings.
- **Bear is a spending problem more than a demand problem in 2026, and a demand problem in 2027.** In 2026 the bear only misses the floor (35.3%) because S&M keeps its 1H pace and incentives clip the take rate. The 2027 bear (nights +6%, ADR flat ex-FX, FX and take rate against) lands at 33.8% even with S&M growth cut to 9%, because cost of revenue and product headcount do not flex.
- **Bull is what the stack does if management stops reinvesting.** With revenue up 15% and cash costs growing 8% to 18%, margin expands about 2 points a year. This is the "at least 35.5%" language read literally as a floor with upside, and it is the case the multiple would need to see.
- **Sensitivities on the FY2026 base** (margin points, EBITDA $M): +1 point ADR ex-FX +0.46 and +115; +1 point FX +0.47 and +117; +10 bps take rate +0.48 and +107; +1 point nights growth +0.35 and +97; support cost per night -10% +0.96 and +136; S&M cash growth +5 points -0.84 and -119. Take rate and ADR are worth roughly the same per unit of noise; the support line is the most powerful lever management actually controls.
- **What to watch on 5 November:** Q3 margin against 49% (the guide implies 48.5% to 49.5%), S&M cash growth (a print below +25% YoY is the first sign the reinvestment cycle is easing), support cost per booking (management gave -10% and -16% in Q1 and Q2), implied take rate against 17.9%, and whether the FY floor moves to 36%.
