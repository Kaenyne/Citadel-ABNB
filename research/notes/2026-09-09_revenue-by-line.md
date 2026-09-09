# Revenue by business line (WS14)

Krish with Claude Code, 9 Sep 2026, branch `krish/revenue-by-line` (stacked on `krish/seats-dilution`).
Script `analysis/src/overnight/14_revenue_by_line.py`; outputs `data/processed/overnight/14_revenue_by_line_{quarterly,annual,kpis}.csv`;
workbook `model/ABNB_revenue_by_line.xlsx` (live formulas, one sheet per case).

## Why

The driver model (13) runs revenue as printed-KPI arithmetic: Nights and Seats Booked x blended ADR x
blended take rate, plus a "new business outside GBV" line. Hotels, Experiences and Services all sit
inside those printed figures at different prices and take rates, so as the mix moves every blended
input moves for mix reasons at once. This build runs the economics by line and lets the printed KPIs
fall out as outputs.

| Line | Units | Price | Take |
|---|---|---|---|
| Stays | home nights = printed Nights and Seats less hotels and seats | home ADR | stays take rate, backed out (13.4% FY25) |
| Hotels | 18.7m FY25, +35/30/25% base | $140 FY25, moves with home ADR | 11% commission |
| Experiences | GBV / $75 ticket | $75 | 20% host fee |
| Services | GBV / $120 ticket | $120 | 15% host fee |
| Ads | outside GBV, WS11 | | |

Printed Nights and Seats per quarter is 13's regional build, unchanged. Home ADR ex-FX defaults to
13's blended ADR ex-FX plus the seats-dilution drag (15), so the printed ADR reconciles to 13 within
$0.5; `--adr-workbook` substitutes the ADR workbook's case path (5_Forecast ex the new-business row).
Hotel nights, seats and tickets are assumptions: Airbnb discloses none of them.

## What it shows, base case

| | FY26 | FY27 | FY28 |
|---|---|---|---|
| Printed Nights and Seats y/y | +9.9% | +8.9% | +8.0% |
| **Home nights y/y** | **+8.2%** | **+6.8%** | **+5.7%** |
| Home ADR y/y (reported) | +5.8% | +3.2% | +3.1% |
| Blended ADR y/y (printed) | +5.2% | +2.5% | +2.3% |
| Stays revenue y/y | +14.7% | +8.7% | +9.4% |
| Hotels / Experiences / Services revenue y/y | +43 / +50 / +250% | +32 / +45 / +119% | +30 / +40 / +80% |
| Total revenue y/y | +15.9% | +10.9% | +12.3% |
| New business share of revenue | 4.2% | 6.1% | 8.5% |
| Seats share of the denominator | 1.9% | 2.9% | 4.0% |
| Stays take rate / blended | 13.5 / 13.4% | 13.3 / 13.2% | 13.3 / 13.3% |

Two things the blended model could not say. First, the core home business is growing 2-2.5pp slower
than the printed nights figure by FY27, because hotels and seats are a rising share of the unit count;
the printed +8.9% is +6.8% homes. Second, the printed ADR understates home pricing by 0.6-0.7pp a year
for the same reason. Both are the seats-dilution mechanism, now inside the revenue model rather than
bolted onto the ADR forecast.

## Reconciliation to 13

Revenue is $46m (0.3%) below 13 in FY26 base, $114m (0.7%) in FY27, $283m (1.6%) in FY28; bull FY28 is
$877m (4.2%) below. The gap is hotels: 13 monetises every dollar of GBV at the blended 13.4%, this build
monetises hotel GBV at 11%, and the hotel share of GBV grows fastest in the bull case. Seats go the other
way (15-20% host fees) but on far smaller GBV. The two blended KPIs 13 forecasts, nights and ADR, are
unchanged by construction; take rate is the line that moves.

## Caveats

- The split of FY25 and 1H26 actuals into lines is assumed (hotel nights from "single-digit % of
  nights", experiences GBV ~$450m, services ~$80m); the totals are actual.
- Seats and hotel nights are spread across quarters on the nights seasonality; Experiences are
  probably more summer-weighted.
- Home nights are a residual of 13's printed-nights build. If the regional buckets management gives
  are read as home nights rather than Nights and Seats, the residual is too low by the hotel and
  seat growth; 13 treats them as the printed KPI and this build follows.
- Hotel commission (11%) is undisclosed; a 13% commission closes the FY27 gap to 13 by about half.
