# RNPL materiality sensitivities

Illustrative thresholds, not fitted forecasts. Rebuild with `analysis/src/rnpl_materiality.py`.

## Net nights needed

| Growth reduction (points) | Q3 net loss (million nights) | Q4 net loss (million nights) |
|---|---:|---:|
| 0.5 | 0.668 | 0.610 |
| 1 | 1.336 | 1.219 |
| 1.5 | 2.004 | 1.829 |
| 2 | 2.672 | 2.438 |
| 3 | 4.008 | 3.657 |

## Required remaining cancellation-risk revision

A one-point growth reduction; exposures are assumptions. Offsets are incremental net replacement bookings within the same quarter.

| Live RNPL nights (millions) | Q3: no offset | Q3: 25% offset | Q4: no offset | Q4: 25% offset |
|---|---:|---:|---:|---:|
| 10 | 13.36 pp | 17.81 pp | 12.19 pp | 16.25 pp |
| 20 | 6.68 pp | 8.91 pp | 6.10 pp | 8.13 pp |
| 40 | 3.34 pp | 4.45 pp | 3.05 pp | 4.06 pp |
| 60 | 2.23 pp | 2.97 pp | 2.03 pp | 2.71 pp |

Double these probability revisions for a two-point growth reduction.

These are revisions to conditional cancellation probability during the target quarter, beyond risk already in the forecast. They are not comparisons of lifetime RNPL versus non-RNPL cancellation rates.

The JSON also includes 50% rebooking offsets. A scenario is feasible only if the revised total probability remains at most 100%; baseline probabilities are not available here.

Denominators: [Airbnb quarterly summary](https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm). Local KPI denominators verified; loss-to-growth and hazard-to-loss identities checked during generation.

