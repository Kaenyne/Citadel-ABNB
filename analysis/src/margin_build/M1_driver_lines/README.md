# M1_driver_lines — driver-based cost lines v2 (per-unit costs on the revenue drivers), point-in-time

Registry method `driver-lines`, objects `margin_v2` (adj EBITDA margin, adj EBITDA $, total cash costs) and `lines_v2`
(cor, ops, pd, sm, G&A ex lodging reserves), seven `spec_id`s each, both replays. Note: `docs/margin-build/notes/M1_driver_lines.md`.

## Run

```bash
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/M1_driver_lines/run.py      # ~25 s, exit 0; rebuilds everything and re-runs score.py
```

Interpreter: `py -3.13` (pandas 2.3, numpy, matplotlib). Only pandas/numpy/matplotlib are used; no scipy/statsmodels.
The script imports the margin harness (`analysis/src/margin_build/10_harness_margin/harness_margin`) for the PIT slice,
the calendar, the frozen revenue leg, the window rule, the validator and the recency weights. It never modifies anything
outside its own folders and the two `driver-lines__*.csv` registry files.

Revenue path for LIVE: `data/processed/margin_build/06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv` (WS06v's long-format
file, pivoted to wide in `load_ws06`) if present, else `06_revenue_path_wide.csv` (the file used is printed on the first line and
stored in `M1_driver_lines_build.json`). Last build 2026-09-13 04:58 used the v2b file.

## Outputs (`data/processed/margin_build/M1_driver_lines/`)

| file | what |
|---|---|
| `M1_driver_lines_forecasts_wide.csv` | every forecast quarter-row: vintage, horizon, spec, replay, scenario, drivers, five lines, other_net, adj EBITDA, margin |
| `M1_driver_lines_registry_long.csv` | the long registry frame before the split into the two objects (with actuals and quantiles) |
| `M1_driver_lines_params_by_vintage.csv` | g, b, mix and step coefficients per line, spec and PIT vintage (+ full sample) |
| `M1_driver_lines_grid_margin.csv` | in-script margin MAE grid for all ten specs incl. the three grid-only variants, vs seasonal naive and Street |
| `M1_driver_lines_per_line_mape.csv` | per-line MAPE vs seasonal naive and pct_rev_last4 (same PIT revenue leg) |
| `M1_driver_lines_loyo_elasticities.csv` | leave-one-year-out b_L for cor, ops, sm |
| `M1_driver_lines_live_quarterly.csv` | LIVE 3Q26-4Q27 by line, scenario and spec, with consensus / WS31b / WS30 / management columns |
| `M1_driver_lines_annual_forecasts.csv` | FY26 (1H26 actual + forecasts), FY27, FY28 (base only) with incremental margins and comparison columns |
| `M1_driver_lines_scoreboard_rows.csv` | this method's rows of the harness scoreboard |
| `M1_driver_lines_build.json` | build stamp |

Figures: `analysis/figures/margin_build/M1_driver_lines_backtest_margin.png`, `M1_driver_lines_live_margin.png`.
Registry: `data/processed/margin_build/registry/driver-lines__margin_v2.csv`, `driver-lines__lines_v2.csv`.
