# C3 GBV feature screen

Run from the repository root with the project `.venv` Python:

```text
python analysis/src/forecast_methods/gbv_features_v1/run.py
python -m pytest analysis/src/forecast_methods/gbv_features_v1/tests -q
```

No network or raw stores required. Outputs are confined to this package's new processed-data folder. Existing feature machinery is read, never executed because it overwrites historical outputs and can initiate downloads. The new screen keeps fixed univariate OLS with expanding historical snapshots, four minimum training observations and two fitted parameters. Nothing is tuned, so nested selection is unnecessary.

The pass line uses the RNPL-corrected ledger comparator exclusively. Its September research assumption is never backdated. Raw unearned-fees comparisons are separate diagnostics; the fixed supplied R target is retrospective and labelled accordingly. No feature is registered unless the required pass line is satisfied; no current result satisfies it. Parent owns all scorer runs.

`forecast_path.csv` provides per-origin values, dates, training counts, slopes and errors. `availability_and_exclusions.csv` records every rejected origin and reason. `full_failure_table.csv` includes both windows, all features, exact exclusions, matched-cell counts and separate diagnostic ratios. `preregistration.json` stores the original note hash before results. `input_manifest.csv` hashes supplied inputs without copying source content. Integer letter growth is evaluated on ±0.5 intervals in supplementary columns; primary GBV growth is computed from reported dollar amounts.
