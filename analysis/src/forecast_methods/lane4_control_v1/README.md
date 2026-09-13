# Lane 4 provenance and scorer control

Run from the isolated L4 repository root, using a Python environment with the repository requirements. Every snapshot name must be new; existing receipts are refused.

```powershell
python -X utf8 analysis/src/forecast_methods/lane4_control_v1/run.py init --snapshot baseline --fx-dependency "C:/Users/wille/Desktop/Citadel - ABNB/FX_ENGINE_SESSION_BUNDLE"
python -X utf8 analysis/src/forecast_methods/lane4_control_v1/run.py verify --snapshot initial --tests
python -X utf8 analysis/src/forecast_methods/lane4_control_v1/run.py verify --snapshot close --tests
```

The runner hashes every pre-existing tracked file and the explicitly supplied external read-only FX bundle. It imports the existing Lane 2 comparator and scorer wrapper, calls both actual scorers with only output paths redirected, and compares all 284 completed Lane 2 score rows with exact keys/discrete values/missingness and strictly less than 1e-9 absolute floating error (zero relative tolerance). No protected source or output is overwritten. New LIVE rows are not evidence of historical effectiveness. The parent runs this after registrations; subagents never score.

## RESUME

Use a new verification snapshot for every subsequent check. The baseline manifest is immutable. Preserve any failure receipt and investigate before continuing affected work. The original workspace FX path is intentionally external and must be supplied explicitly on a new machine; never stage that bundle wholesale.
