# Quant preannouncement guide validation v1

Canonical result: `data/processed/forecast_methods/quant_thesis_validation_v1/prospective_v1/results_v1`.

From the quant worktree root:

```powershell
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/prospective_v1/test_prospective.py
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/prospective_v1/run.py --out data/processed/forecast_methods/quant_thesis_validation_v1/prospective_v1/reproduction_NEW
```

Python dependencies are pandas, NumPy and timezone data; Git must expose the fixed L3 commit. The runner rejects existing output paths, verifies both frozen protocol hashes and immutable inputs, invokes exact inherited public K0 and naive-baseline APIs on explicitly filtered panels, and writes the point forecasts, all inputs and a hash receipt **before** joining outcomes. It then evaluates the locked hypothesis, exports exclusions, paired/year/season scores, seven interactions plus rounding, covariance-aware MSE reconciliation and chronological descriptive bands. There is no network request, new model search, shared registry write or scorer mutation.

Separate stages are also supported with `--stage forecast --out NEW_FORECAST` and `--stage evaluate --forecast-dir EXISTING_FROZEN_FORECAST --out NEW_EVALUATION`. Evaluation verifies the forecast receipt before reading outcomes. The default `all` stage performs those same stages in order under one fresh parent output folder.

Read `docs/revenue-forecast-strategy/quant_thesis_validation_v1/FINAL_PROTOCOL_v1.md` and the versioned prospective note for the frozen test and limitations. Research verdict **FAIL** is a successful run and produces exit 0; malformed inputs or broken identities raise errors. No production method is adopted.
