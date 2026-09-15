# Canonical economic publication v2

Canonical results: `data/processed/forecast_methods/quant_thesis_validation_v1/economics_v1/results_v2/`. Numerical source `results_v1` is preserved. V2 renames an ambiguous endpoint column and adds conditional-status / zero empirical-validation-count metadata. Every original numeric cell remains identical as text. The accompanying final documentation is `RESULTS_v1.md` plus `PUBLICATION_REPAIR_v2.md`.

Reproduce with fresh destinations from the worktree root:

```powershell
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B analysis/src/forecast_methods/quant_thesis_validation_v1/economics_v1/run.py --out data/processed/forecast_methods/quant_thesis_validation_v1/economics_v1/reproduction_calculation_NEW
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B analysis/src/forecast_methods/quant_thesis_validation_v1/economics_v1/publish_v2.py --input data/processed/forecast_methods/quant_thesis_validation_v1/economics_v1/reproduction_calculation_NEW --out data/processed/forecast_methods/quant_thesis_validation_v1/economics_v1/reproduction_publication_NEW
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -m unittest discover -s analysis/src/forecast_methods/quant_thesis_validation_v1/economics_v1 -p 'test_*.py' -v
```

The numerical runner audits source bindings and equations. The publisher verifies source-output hashes before copying, checks every original cell is unchanged, and refuses an existing output directory. Receipt paths can differ between reproductions; numeric CSV outputs should match exactly.
