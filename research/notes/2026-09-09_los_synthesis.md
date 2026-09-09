# Length of stay in the ADR ex-FX model: synthesis of 14a/b/c

Krish with Claude Code, 9 Sep 2026. Three parallel builds (notes `2026-09-09_los_a_discount_ratios.md`,
`_los_b_bucket_shares.md`, `_los_c_calendar_runs.md`; scripts `analysis/src/adr/14a-c`), then the
back-test and the workbook wiring below.

## The term

    LOS mix, pp of ADR y/y = sum over buckets of d(nights share) x (per-night price ratio - 1)
    buckets: under 7 nights (ratio 1), 7-27 (0.966), 28+ (0.852)

Ratios from 14a: host weekly/monthly/long-stay discounts plus Airbnb's own "monthly stay savings",
nights-weighted, 139 quote dumps, six regulatory-minimum markets excluded. Stable across regions
(28+ ratio 0.82 APAC to 0.86 elsewhere). Discount effect only: the lower base rate of listings
that accept long stays is composition and belongs with the unit-size and sub-regional terms.

## What replaced the placeholder

14b found Airbnb disclosed TWO stay-length shares in 1Q21-2Q23 (7+ nights ~45-50% and 28+ nights
17-24% of gross nights booked), so 2021-22 bucket shares are disclosed outright and the ALOS
identity solves the short-bucket mean (2.47 nights) instead of assuming it. 2023 solves off the
28+ share alone; 2024-25 carry on ALOS only. 14c's calendar panel independently shows the 28+
share of occupancy-weighted nights falling 17.4% -> 15.5% from Sep-25 to Aug-26, about -2pp a
year, in every region (LatAm most, NA least), which is the same slope the ALOS carry implies.

| global | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|
| 28+ share of nights | 20.2% | 18.2% | 15.9% | 13.4% |
| d(28+ share), pp | -0.9 | -2.0 | -2.4 | -2.5 |
| **LOS mix term, pp** | **+0.16** | **+0.33** | **+0.34** | **+0.35** |
| old -0.15 elasticity term | +0.26 | +0.62 | +0.21 | +0.04 |

## Back-test verdict

The measured term is smaller and smoother than the bounded elasticity and stays within 0.3pp of
it every year, so the 07 decomposition's residual is not materially re-cut. It is a level term of
+0.3pp a year while long stays keep losing share; it does not move quarter to quarter.

## Forecast and workbook

5_Forecast now carries "Length-of-stay mix, pp": bear 0.0 (shares stabilise), base +0.3 (28+
share keeps falling ~2pp a year), bull +0.45 (LatAm-style -3pp). The pricing row was re-based
again to exclude it (base 2.2%). The ex-FX sum is pricing + LOS + unit size + fee + geo mix +
interaction. The same bucket shares give ALOS for the nights model (nights = bookings x ALOS);
do not forecast ALOS separately from them.

## Caveats carried

- 2024-25 shares rest on ALOS alone; against 1H24's disclosed 17% the carry reads ~1pp low.
- The 28+ mean stay is unmeasured (Airbnb has never stated it); 45 nights used, 35-60 gridded,
  and the term moves by under 0.1pp across the grid.
- Calendar run levels are inflated by host blocks by a region-specific factor; use 14c for
  change over time within a region only, never to rebase regional ALOS.
- NYC and LA long stays are regulatory; excluded from every aggregate.
