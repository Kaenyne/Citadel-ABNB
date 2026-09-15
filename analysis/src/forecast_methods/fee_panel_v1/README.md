# Fee panel v1

Offline consumer, no network or scheduling. Use an installed Python with numpy, pandas, scipy, statsmodels, pytest.

From repository root:

```powershell
python -m pytest analysis/src/forecast_methods/fee_panel_v1/test_fee_panel.py -q
python analysis/src/forecast_methods/fee_panel_v1/run.py --as-of 2026-09-13 --out data/processed/forecast_methods/fee_panel_v1
```

Every output path must be new. For later captures specify `--as-of YYYY-MM-DD --out NEW_DIR` and optionally repeated `--capture PATH` to select exactly one run per wave date. By default consumes `fee_panels/runs/capture*.csv`. Never use filename dates to override actual capture timestamps. Metadata defaults to the frozen sample; an explicit `--metadata` accepts the same schema (including residence proxy, strata and dump_date). Unknown hosts are excluded from primary estimates, including most search results if no sanctioned metadata is supplied.

Preregistered methods and pass lines: `docs/revenue-forecast-strategy/05_backtests/L3_FEE_PREREG_v1.md`. Theta is a logarithmic payout-neutral repricing fraction, not the legacy arithmetic theta. Old 3% host fee is an assumption; Mexico/Brazil new fee 16%, elsewhere 15.5%. No migration-share or aggregate-revenue inference follows from a precise theta association. A changed fee schedule requires a new version.

All captures are listed prices. First-differencing removes fixed listing/market characteristics but cannot establish parallel trends with one pre observation. October's already-treated comparator requires an untested stability assumption. CSV outputs and JSON summary retain missing claims explicitly. Descriptive indices can change because search composition changes.
