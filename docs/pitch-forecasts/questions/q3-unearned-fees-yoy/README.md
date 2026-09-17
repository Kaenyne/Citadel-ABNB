# C12 — q3-unearned-fees-yoy

- **id:** C12
- **title:** Will unearned fees on Airbnb's 30 Sep 2026 balance sheet be ≤ −3% year over year?
- **type:** binary
- **resolution date:** 3Q26 10-Q filing (expected 2026-11-05 with the letter)
- **registry entry:** `docs/pitch-forecasts/QUESTIONS.md` § C12
- **batch:** A05

## Files

| path | contents |
|---|---|
| `research-log.md` | revision 1 research log (schema: forecast skill `references/research-log-format.md`) |
| `forecasts/2026-09-17-forecast.json` | binary `final`, decomposition, estimates, sensitivity, monitoring |
| `datasets/c12_model.py` | three routes (y/y gap, sequential, level norm) and the mixture; numpy/pandas only, seeded; `py -3.13 docs/pitch-forecasts/questions/q3-unearned-fees-yoy/datasets/c12_model.py` from the repo root |
| `datasets/c12_history.csv` | unearned fees, GBV, gap, sequential change, coverage ratio 1Q23–2Q26 |
| `datasets/c12_routes.csv` | the three routes and the mixture: P(≤ −3%), median, 10–90%, P(≥ +6%) |
| `datasets/c12_sensitivity.csv` | 20 single-assumption reruns |
| `datasets/c12_deferral_table.csv` | unearned-fees y/y by unpaid share u and GBV growth (deferral, migration, FX decomposition) |
| `sources/` | web query log with URLs and timestamps (market JSON is under `../q3-take-rate-above-1810/sources/`) |

## Headline (revision 1)

P(unearned fees at 30 Sep 2026 ≤ −3% y/y, ≤ $1,765M) = **0.55**, credible interval 0.40–0.70; median print ≈ $1,755M (−3.6%). Decomposition of the central path: GBV +13 points, deferral −17 (unpaid share 18% vs 3.5% in the 3Q25 base), migration +1 (the host-only fee sits in unearned fees, so migration lifts the line), FX 0. Anchor: the programme's deferral-only table (−1.7% at u 15%, −3% at u ≈ 16%) → 0.45.
