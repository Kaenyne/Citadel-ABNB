# kernel-lambda

The recognition kernel: a seasonal conversion `lambda_s` applied to **already printed** GBV.

```
Revenue_q  =  lambda_{s(q)} * [ w * GBV_{q-1} + (1-w) * GBV_{q-2} ]      w = 2/3 published
```

## Run command (exact)

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/kernel_lambda/run.py
```

Exit code 0 rebuilds every output. Then score:

```bash
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/harness/score.py
```

## Files

| file | what |
|---|---|
| `kernel.py` | the identity, the weight objectives, the lag polynomial, the bootstraps |
| `run.py` | entry point; stages A-F, each flushing its CSV before the next begins |

## Outputs — `data/processed/forecast_methods/kernel_lambda/`

`00_run_log.csv`, `01_lambda_table.csv`, `01_acceptance_test.csv`, `02_weight_grid.csv`,
`03_weight_summary.csv`, `04_season_lambda_by_weight.csv`, `05_flatness_cost_4q26.csv`,
`06_lag_polynomial.csv`, `07_fx_wedge_regression.csv`, `07_fx_wedge_cells.csv`,
`08_live_3q26.csv`, `09_live_4q26_grid.csv`, `10_ledger_share.csv`,
`11_parameter_count.csv`, `12_prereg_card.csv`, `13_live_registry_rows.csv`.

## Registry objects — `data/processed/forecast_methods/registry/kernel-lambda__*.csv`

| object | target | what |
|---|---|---|
| `revenue_level_next_q` | `revenue_musd` | the published spec: w=2/3, season mean of every same-quarter lambda in the information set, horizon 0 |
| `revenue_level_next_q_last3` | `revenue_musd` | same, season mean over the 3 most recent same-quarter cells |
| `revenue_level_next_q_ex_covid` | `revenue_musd` | same, 2021 lambda cells dropped from estimation |
| `revenue_level_next_q_last3_ex_covid` | `revenue_musd` | both restrictions; the best PIT object |
| `revenue_level_next_q_w038` / `_w033` | `revenue_musd` | mandatory weight sensitivities |
| `revenue_yoy_next_q` | `revenue_yoy` | the published spec mapped to y/y growth |
| `revenue_level_h1` | `revenue_musd` | two quarters ahead; `GBV_{q-1}` is NOT printed and is filled by the naive rule `GBV_{q-5} * (1 + last observed GBV y/y)` |
| `live_3q26_print` | `revenue_musd` | 3Q26, vintage 2026-09-11, no GBV forecast required |
| `live_4q26_print` | `revenue_musd` | 4Q26 at GBV_3Q26 = 26,300; registered with `strict_windows=False` (see the note's harness change request) |

Every object is written for both `prior_basis` replays (`PIT` and `full_sample`).

## Free-parameter count

**5** — four seasonal conversions plus one lag weight — against 23 printed revenue
identities (22 with both GBV lags available). The weight is asserted at 2/3 rather than
fitted, but is counted anyway. The lag-polynomial diagnostic in stage C spends 7.
