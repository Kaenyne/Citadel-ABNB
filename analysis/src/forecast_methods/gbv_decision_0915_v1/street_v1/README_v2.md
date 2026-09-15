# Accepted Street audit commands

`run.py` preserves the first source-only audit and original cross-arm join failure. Use `run_v2.py` for a complete comparison; it validates each origin arm separately. Existing files are never overwritten.

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/street_v1/run_v2.py --out NEW_STREET_OUTPUT --predictions data/processed/forecast_methods/gbv_decision_0915_v1/horizon_v1/results_v2/predictions.csv
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/street_v1/score_sensitivity.py --paired data/processed/forecast_methods/gbv_decision_0915_v1/street_v1/results_v3/paired_rows.csv --out NEW_SENSITIVITY_OUTPUT
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/street_v1/common_model_compare.py --out NEW_COMMON_OUTPUT
```

Canonical artifacts: `street_v1/results_v3`, `street_v1/common_v1`, and `street_v1/sensitivity_v1`. Source-only `source_v1` and failed partial `results_v1` remain. `common_model_compare.py` binds the quant's independently checked calendar-origin artifact and selects the intersection of all four model samples before producing fair comparison tables. `score_sensitivity.py` reports both year/quarter deletions and zero-threshold sign confusion, including majority-class accuracy. No stocks or return strategies are fitted. Read `GD_STREET_RESULTS_v1.md` for the conditional provenance and different forecast-object limitations.
