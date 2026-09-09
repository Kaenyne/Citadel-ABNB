# Party size in the ADR ex-FX model

Krish with Claude Code, 9 Sep 2026. Script `analysis/src/adr/13_party_size_adr.py`; outputs
`data/processed/adr/13_party_size_adr_{quarterly,annual,checks,forecast}.csv`; wired into
`model/ADR_decomposition.xlsx` sheet 5_Forecast (rebuilt by `09_workbook.py`).

## The chain

Party size has no slot in revenue (nights count stays, not guests). It reaches ADR because
bigger parties book bigger homes and price is concave in size. Hedonic on 1.4m quote-basis
listings: d ln price = 0.399 d ln capacity + 0.140 d bedrooms; in the 29-market size panel
bedrooms move 1.37 per unit of log capacity (nights-weighted), so

    elasticity of price to booked capacity = 0.399 + 0.140 x 1.37 = 0.59   (listed basis 0.58)
    size term, pp of ADR y/y = 0.59 x booked-capacity growth, %

Booked capacity = capacity of the listing behind each review, from the party-size study
(123 markets, fixed 2019 market weights, 2011-2026, global and four regions). A review is
about one booking, so this is booking-weighted capacity per stay: the same construct as the
size panel's capacity per booked night, with fifteen years of history instead of one.

## What it says

| y/y, fixed weights | 2Q24 | 2Q25 | 4Q25 | 1Q26 | 2Q26 |
|---|---|---|---|---|---|
| NA booked capacity | +2.6% | +2.7% | +2.7% | +3.0% | +2.4% |
| EMEA | +0.4 | +0.6 | +0.9 | +1.1 | +0.6 |
| APAC | +2.6 | +1.2 | +1.2 | +1.5 | +1.3 |
| LatAm | −0.1 | 0.0 | 0.0 | −0.3 | 0.0 |
| **Global size term, pp of ADR** | **+0.8** | **+0.7** | **+0.8** | **+1.0** | **+0.7** |
| NA size term, pp | +1.5 | +1.6 | +1.6 | +1.8 | +1.4 |

Steady, structural, NA-led. Consistent with the 29-market panel for 2Q26 in the region that
matters (NA +2.4% reviews vs +2.2% panel); APAC 1.3 vs 0.8, LatAm 0.0 vs 0.7, EMEA 0.6 vs
1.8 on nine pairs. The 07 decomposition's annual size term (2024 +0.44, 2025 −0.25pp) rests
on 11 pairs in four cities; the review series (4m reviews a quarter) gives +0.83 / +0.74 and
should replace it.

**It is a level term, not a timing signal.** Against ADR ex-FX y/y (20 usable quarters) the
size term has r −0.17 / +0.17 / −0.02 at leads of 0/1/2 quarters; EMEA shows negative r at
leads 1-2, which is the 2023 reopening drift, not information. FX and the reopening set the
variance of ADR; size sets 0.7-1.0pp of the level, every year.

## Mapping a party-size forecast onto it

Two party-size measures exist and they disagree on purpose. The composition-implied index
(solo/couple/family/group weights) moves AGAINST capacity (annual beta −0.36, p 0.11):
within any home size parties got smaller as families replaced friend-groups, while the mix
moved to bigger homes. So do not drive capacity off the composition index. Stated head-counts
move with capacity (pooled beta 0.41, r 0.50, p 0.002, n 37), and the fill ratio (stated
heads / booked capacity) drifted 1.32 → 1.27 over 2013-25, about −0.3% a year.

**Rule for the model:** d ln booked capacity = d ln people per booking, less ~0.3pp a year of
fill drift, by region. A people-per-booking forecast drops into
`13_party_size_adr_forecast.csv` column `party_size_yoy_pct_at_constant_fill`.

## Forecast cases (global, nights-weighted on 10-K 2025 shares)

| | bear | base | bull |
|---|---|---|---|
| Booked-capacity growth | 0.0% | +1.25% | +1.65% |
| Size term, pp of ADR ex-FX | 0.0 | **+0.74** | +0.98 |

Bear = the mix shift has matured (the sleeps-5+ share of reviews stalled at 25-27% in
2025-26 after rising every year to 2024). Base = trailing 8-quarter capacity growth by region
(NA +2.6, EMEA +0.7, APAC +1.4, LatAm 0.0). Bull = the stronger of the last four quarters and
the 8-quarter peak.

## Workbook

5_Forecast now sums pricing (ex size) + unit size + fee reprice + geographic mix + interaction
to ADR ex-FX, then adds FX. The pricing row was re-based to exclude size (base 2.5% from
3.25%) so the size term is not double counted. The fee row carries +0.5pp (−0.5/+1.5) from
the 8 Sep bound. 4_Drivers moves unit size from LOW-MED to MEDIUM as a level term.
