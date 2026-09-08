# 30. Quarterly margin walk and EPS proxy, 3Q26 to 4Q27

Krish with Claude Code, 7 Sep 2026. Script `analysis/src/overnight/30_margin_walk.py` (`py -3.13`; run after `29_q4_fy27_bridge.py`, which it consumes). Outputs `data/processed/overnight/30_margin_assumptions.csv`, `30_quarterly_pnl.csv`, `30_margin_walk.csv`, `30_fy_summary.csv`, `30_mgmt_language.csv`; figure `analysis/figures/overnight/30_margin_walk.png`. Top line is the workstream-29 revenue bridge by scenario; cost lines are the workstream-07 quarterly cash stack (`07_cost_lines_per_night.csv`) driven by their natural units. Street EPS from workstream 04 is a comparison column only.

## Bottom line

1. **Base case holds the FY26 floor with 0.7 points to spare (36.2%) and Q4 2026 margin is up year on year (29.7% against 28.3%) even with revenue growth dropping to 12%.** The Q4 walk: revenue per night adds 1.3 points (ADR ex-FX +1.9, FX −0.3, timing −0.3), cost of revenue takes 0.8 (AI hosting in the run rate), support gives 0.5 back, G&A 0.7 (the 4Q25 base carried an $83m item that Adjusted EBITDA added back), and brand marketing is flat per night because the H2 phasing puts the spend in Q3. Bear 23.7%, bull 33.6%.
2. **Base Q3 2026 margin is 50.8%, above the "down slightly from 50.1%" ceiling.** This disagrees with the 49.0% on the frozen 5 November card and workstream 7's 49.0%, and it should be read as a cross-note conflict, not a resolution. The mechanism: 1H26 cash costs grew 16.3% and 14.7%; this walk phases H2 brand marketing at +28% in Q3 and +10% in Q4 and still lands cash costs at +14.3% in Q3 against revenue +16.5%. To reach 49.0% the quarter needs cash costs near +19%, which is above any quarter since 2022. Management's ceilings have been met 9 of 10 times by a mean 1.4 points, so a print above 50.1% would be a first. Either the revenue base ($4,775m, +1% on the midpoint) is too high or the cost base too low; the bear (48.3%) is what "down slightly" looks like on our lever set. Carry both numbers to 5 November and score them.
3. **FY27 base margin is 36.4%, flat on FY26 (+0.2 points), and 1H27 is 28.0% against 28.3% in 1H26.** The FY walk: revenue per night +1.4 (ADR ex-FX +1.8, FX −0.4), cost of revenue −0.6, support +0.4, brand marketing −0.9, field ops −0.3, G&A +0.2. **The FX step in the revenue bridge is worth about 0.4 margin points on the year and 0.3 in Q4, not the 1.6 the flow-through rule of thumb gives**, because the walk holds cost per night and lets lower revenue per night deleverage every line; the rule of thumb applies to a spot move on a fixed cost base, whereas here the cost lines also carry lower growth. Bear FY27 30.6% (−3.5 points), bull 41.3% (+3.3).
4. **EPS: the base is on the Street for every period, and the bear and bull are 35% either side.** GAAP EPS proxy, base: Q3 $2.86 (Street $2.87), Q4 $0.81 ($0.82), FY26 $5.30 ($5.23-5.28), FY27 $5.90 ($6.02-6.14). Bear FY27 $3.62, bull $8.03. So the Street's FY27 EPS is the base case with a slightly better margin; there is no EPS variant in the base, only in the shape (1H27 EPS $1.62 against $1.61 in 1H26, i.e. flat, on revenue up 10%).
5. **What management says (base case, probabilities are judgement):** 5 Nov, FY26 floor replaced by "approximately 36%" (70%); Q4 margin guided "up year over year" (60%); Q4 revenue at +11-13% with an FX sentence (55%); marketing "faster than revenue" but softer than 1H (65%); no 2027 number (75%). February: FY27 floor "at least 35.5%" (55%), FY27 revenue "low double digits" with FX quantified as a headwind (55%), 1Q27 guide implying +9-11% with "approximately one point FX headwind" (50%). The whole table is in `30_mgmt_language.csv`.

## The quarterly P&L, base case

| | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 |
|---|---|---|---|---|---|---|
| Revenue, $m | 4,771 | 3,111 | 2,944 | 3,992 | 5,341 | 3,527 |
| Revenue y/y | +16.5% | +12.0% | +9.9% | +10.7% | +11.9% | +13.4% |
| Cash costs ex-SBC, $m | 2,368 | 2,207 | 2,412 | 2,623 | 2,630 | 2,461 |
| Adj. EBITDA, $m | 2,423 | 924 | 552 | 1,389 | 2,731 | 1,086 |
| Adj. EBITDA margin | 50.8% | 29.7% | 18.7% | 34.8% | 51.1% | 30.8% |
| Prior-year margin | 50.1% | 28.3% | 19.4% | 35.0% | 50.8% | 29.7% |
| Brand & performance marketing, $m | 486 (+28%) | 430 (+10%) | 594 (+16%) | 672 (+16%) | 564 (+16%) | 499 (+16%) |
| SBC, $m | 451 | 452 | 451 | 536 | 496 | 497 |
| GAAP operating margin | 40.9% | 14.5% | 2.7% | 20.9% | 41.5% | 16.1% |
| Net income, $m | 1,693 | 472 | 164 | 766 | 1,871 | 554 |
| Diluted shares, m | 591 | 585 | 579 | 573 | 568 | 562 |
| GAAP EPS proxy | 2.86 | 0.81 | 0.28 | 1.34 | 3.30 | 0.99 |
| Street EPS | 2.87 | 0.82 | | | | |

Bear and bull rows are in `30_quarterly_pnl.csv`. Full-year: `30_fy_summary.csv`.

| FY | Bear | Base | Bull | Street / guide |
|---|---|---|---|---|
| FY26 revenue, $m | 13,879 | 14,168 | 14,458 | 14,100-14,160 |
| FY26 adj. EBITDA margin | 34.0% | **36.2%** | 38.0% | floor 35.5% |
| FY26 GAAP EPS proxy | 4.63 | **5.30** | 5.93 | 5.23-5.28 |
| FY27 revenue, $m | 14,318 | 15,804 | 16,910 | 15,730-15,760 |
| FY27 adj. EBITDA margin | 30.6% | **36.4%** | 41.3% | none |
| FY27 GAAP EPS proxy | 3.62 | **5.90** | 8.03 | 6.02-6.14 |
| 1H27 margin vs 1H26 28.3% | 24.4% | 28.0% | 31.3% | |

## The levers

Cash lines, y/y against the same quarter a year earlier; bear / base / bull. Each row's evidence is in `30_margin_assumptions.csv`.

| Lever | 3Q26 | 4Q26 | FY27 quarters | Anchor |
|---|---|---|---|---|
| Cost of revenue per $ GBV | +4 / +2 / 0% | same | +2 / +1 / −0.5% | flat 1.82-1.89% of GBV since 2022; server cost +$15m 1H26; $1.7bn hosting commitment |
| Ops & support per night | −3 / −5 / −7% | same | −3 / −5 / −6% | −3.8% realised 1H26; support cost per booking −16% (2Q26) |
| Product development cash | +12.5 / +11 / +10% | same | +10.5 / +10 / +9% | 1H26 +11%, all payroll |
| Brand & performance marketing | +35 / **+28** / +20% | +25 / **+10** / +5% | +14 / +16 / +12% | 1H26 +32%; Q3 "investment timing"; H2 base +19%; 07: floor breached above ~+29% H2 |
| Field ops & policy cash | +20 / +14 / +10% | +15 / +10 / +6% | +10 / +14 / +12% | 1H26 +24%; 4Q25 base was +71% y/y |
| G&A cash | +5 / +2 / 0% | same | +5.5 / +5.5 / +5% | 1H26 +1%; 4Q25 base ex the $83m add-back |
| SBC | +16 / +13 / +10% | same | +14 / +10 / +6% | 1H26 +14.7%; guided below 2025 |
| Tax rate | 20 / 19 / 18% | same | 21 / 20 / 19% | guide 17-19%; tax guides have run hot |
| Interest income, $m/qtr | 160 / 168 / 175 | 150 / 162 / 172 | 135 / 155 / 172 | 1H26 $338m; rates and float falling |
| Interest expense, $m/qtr | 31 | 31 | 31 | $2.5bn notes |
| Diluted shares, % per qtr | −0.8 / −1.0 / −1.2 | same | same | $1.1bn/qtr buyback at ~$180 less RSU issuance |

Field operations cash is GAAP field operations less all S&M SBC (workstream 7 convention). GBV growth is nights plus ADR ex-FX plus the FX revenue points; D&A $20m a quarter.

## What the walk changes about the picture

- **The floor is safe in the base and only the bear breaks it** (34.0%, a 1.5-point miss, on brand marketing +35% / +25% in H2 and nights at 7%). That matches workstream 7's reading that the floor has cushion and the base does not.
- **Margin is not where the 2027 debate is.** Base FY27 margin is flat. The revenue bridge's shape problem (1H27 growth near +10%) shows up in EPS as a flat first half, not as a margin collapse, because ADR ex-FX keeps paying for the cost base. If ADR ex-FX goes to 1% (the bear), the same cost base takes 2 points out of the margin on its own.
- **The Q3 conflict is worth a decision before 5 November.** Two internally consistent constructions give 49.0% and 50.8%. The difference is whether cash costs grow 19% or 14% in the quarter. The 10-Q's S&M split will settle it on the day; before then, the pre-registered card keeps 49.0% and this note's 50.8% is the bottom-up alternative, both logged.
- **Below the line matters more than the margin for EPS.** Interest income falls roughly $30m a quarter over the horizon, the tax rate steps from 19% to 20%, and the share count falls 1% a quarter. Together they are worth about $0.15 of FY27 EPS, which is the whole gap between base and Street.

## Caveats

- Cost levers are judgement anchored on 1H26 run rates and workstream 7's annual set; none is a disclosure. The phasing of H2 brand marketing (Q3 heavy) is inferred from "investment timing" language and the 1H run rate, and it moves the Q3 / Q4 margins by about a point each in opposite directions without changing FY26.
- The 3Q27 and 4Q27 columns compare against our own 3Q26 and 4Q26, so their y/y figures compound any error in the 2026 half.
- The revenue-per-night split in the walk allocates leverage across ADR ex-FX, FX and the residual in proportion to their contribution; it is an attribution convention, not a measurement.
- Q1 2026 net income $160m and Q2 $816m from the letters; the EPS proxy is GAAP net income over a modelled diluted count, not a company EPS.
- Nothing here predicts the stock: the print-day evidence is in workstreams 02, 04 and 20.
