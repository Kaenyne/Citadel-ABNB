# Valuation reconciliation v1

Run from repo root with the `.venv` Python interpreter:

```text
python analysis/src/forecast_methods/valuation_v1/run.py
python analysis/src/forecast_methods/valuation_v1/run.py --refresh
python -m pytest analysis/src/forecast_methods/valuation_v1/tests -q
```

The default run uses only git inputs and a previously saved public positioning snapshot, if present. `--refresh` requests Yahoo Finance through yfinance; failures produce an explicit offline status. Outputs go only to `data/processed/forecast_methods/valuation_v1/`.

This package computes descriptive regression replications and conditional valuation arithmetic. It does not forecast a supported quarterly harness target; the new reserved method name is `valuation-v1`, but no misleading registry row is emitted. The parent owns scorer runs.

Read `valuation_page.md` for the compact exhibit and the package note for provenance limits. Monthly changes overlap and the final observation is 4 September rather than a completed month. HAC confidence intervals do not fix inherited component vintages or identify a causal effect. The monthly reported-quarter labels are checked against the frozen calendar, but no complete component-vintage provenance exists in the supplied monthly CSV. Guide-date regressions are recalculated using only strictly earlier month-end observations and remain inherited-vintage diagnostics.

There are four fitted parameters (intercept and three slopes). Six football-field lenses are not independent forecasts. The 9.18%, 10.35%, 11.52% growth scenarios are mapped to a multiple change around the existing 16.5x / 11.3086% base-model anchor; EBITDA, cash and shares stay fixed. The output is a conditional sensitivity, not an independently estimated target range or a decision.
