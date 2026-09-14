# Canonical prospective validation instructions

This final README supersedes the legacy README's phrase “before reading outcomes.” No code, source, forecast or numerical result changed. Canonical results remain `data/processed/forecast_methods/quant_thesis_validation_v1/prospective_v1/results_v1`.

From the quant worktree root:

```powershell
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/prospective_v1/test_prospective.py
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/prospective_v1/run.py --out data/processed/forecast_methods/quant_thesis_validation_v1/prospective_v1/reproduction_NEW
```

Requirements are Git, Python, pandas, NumPy and timezone data. The runner rejects existing output paths and verifies immutable L3 inputs and the two frozen protocol hashes. It loads the complete frozen source tables, then filters the information set for each origin before invoking the exact inherited K0 and naive-baseline public APIs. It freezes point forecasts and used-input ledgers **before joining target outcomes for scoring**. Source filtering and all-origin future-value poisoning tests, rather than physical exclusion of outcome-containing files from memory, establish functional independence.

The default run writes `forecast/forecast_freeze.json` before the evaluation stage. To use separate stages, run `--stage forecast --out NEW_FORECAST`, then `--stage evaluate --forecast-dir EXISTING_FROZEN_FORECAST --out NEW_EVALUATION`. Evaluation verifies the forecast-file hashes before its target-outcome join. Each destination must be fresh.

The output includes every abstention, matched/own/pair loss, year and season slice, seven exact error interactions plus rounding, cross moments and covariance-aware MSE identity, and chronological descriptive calibration bands. There is no network request, method search, shared registry write or scorer mutation. Research verdict FAIL is an expected successful execution (exit 0); missing/invalid contracts or failed identities raise errors.

Use this final README with `WP_Q2_Q3_RESULTS_v1.md`, `RECEIPT_WORDING_CORRECTION_v1.md` and `author_handoff_v1/SEMANTIC_CORRECTION_v1.json`. The latter additively corrects the immutable evaluation receipt's source-loading wording. The 12/10 matched sample and failed promotion hurdle remain unchanged. The source panel remains a historical reconstruction, not a recovered original-vintage archive, and no production method or investment direction is adopted.
