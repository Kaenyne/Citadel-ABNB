# M7_below_ebitda — below-EBITDA bridge (SBC, D&A, interest income, tax, share count, EPS) and the FCF bridge

Method `below-ebitda`, seven objects (`interest_income, sbc, da, tax, share_count, eps, fcf`), registered through the margin
harness (`analysis/src/margin_build/10_harness_margin/`). Note: `docs/margin-build/notes/M7_below_ebitda.md`.

## Run (interpreter `py -3.13`; ~3 minutes; exit 0)

```
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/M7_below_ebitda/run.py     # PIT grid at 20 vintages, registry (7 files), LIVE waterfall, FY26-28, parameter sheet, scorer, figures
py -3.13 analysis/src/margin_build/M7_below_ebitda/figures.py # figures only
```

`run.py` rewrites only `data/processed/margin_build/registry/below-ebitda__*.csv`, everything under
`data/processed/margin_build/M7_below_ebitda/`, the three `analysis/figures/margin_build/M7_below_ebitda_*.png`, and re-runs the
harness scorer (which rewrites the scoreboard files under `10_harness_margin/`). It reads, never writes, WS02/03/04/05/06 and the
other methods' registry files (the LIVE adj EBITDA base is taken from `driver-lines` if registered, else `margin-ts`, else the
`seasonal_naive_drift` baseline; the log line says which).

Inputs pulled from the web: FRED `DTB3`, `DGS1`, `DGS2` daily (keyless) into `data/raw/margin_build/M7_below_ebitda/` (gitignored);
manifest with URL, timestamp and sha256 at `data/manifests/margin_build/M7_below_ebitda.csv`. Re-pull by deleting the raw files
and re-running the two-line snippet in the note ("What ran").

## Outputs (`data/processed/margin_build/M7_below_ebitda/`)

| file | what |
|---|---|
| `M7_forecast_grid_all_vintages.csv` | every component forecast at every vintage / quarter / weighting / replay (the working grid) |
| `M7_errors_all_vintages.csv` | realised errors per (object, target, spec, replay, horizon, quarter) — the residual pools |
| `M7_registry_preview.csv` | the registered rows with actuals attached |
| `M7_scoreboard_rows.csv` | this method's rows from the harness scoreboard |
| `M7_eps_error_decomposition.csv` | last prints at h=0: EPS error with PIT EBITDA vs actual EBITDA vs the pre-guide Street, and the per-line contributions |
| `M7_fy_fcf_test.csv` | FY FCF from each February vintage vs the seasonal naive and the actual |
| `M7_live_waterfall_quarterly.csv` | 3Q26-4Q28 waterfall by EBITDA source (driver-lines / guide_implied / street) and scenario (base, bear, bull, rates +/-100bp, no buyback renewal, ETR 16 / 19) with the LSEG comparison columns |
| `M7_below_ebitda_annual_forecasts.csv` | FY26, FY27, FY28 by source and scenario. FY28 EBITDA = the source's FY27 margin (measured on the **base** revenue path) x FY28 base revenue, so FY28 is identical in base/bear/bull: the WS06 bear and bull revenue paths stop at 4Q27 and M1 supplies a $ level, not a margin. Do not read bear/bull as EBITDA scenarios. |
| `M7_parameter_sheet.csv` | "For the model": every rate, beta, lag, share-count and tax assumption with unit and source |
| `M7_interest_income_fit_history.csv`, `M7_cfo_other_residual_history.csv` | diagnostics |
| `M7_build_log.txt` | run log |

## Reproducibility

Re-run from scratch 13 Sep 14:44-14:47: all twelve processed CSVs and all seven registry files came back byte-identical (only `M7_build_log.txt` differs, in its timestamp line); exit 0. A second run at 14:49-14:53, after the FY28 margin-denominator fix described above, also exited 0 and changed only the FY28 bear/bull rows.
