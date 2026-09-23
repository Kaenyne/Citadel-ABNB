# Independent reproduction

Reviewer `/root/uncertainty_auditor` independently reconstructs author `/root/source_auditor` source metadata and prospective points, K0 selection, losses, year deletions, attribution, covariance and chronological bands. Author APIs are used only for adversarial perturbations and fresh reruns. Parent decides acceptance; the research verdict remains FAIL.

Run from `C:/Users/wille/Desktop/Citadel - ABNB/.worktrees/quant-thesis-validation-v1` in PowerShell. The completed canonical invocation was:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/independent_reproduction_v1/run_v2.py --out data/processed/forecast_methods/quant_thesis_validation_v1/independent_reproduction_v1/complete_run_v2
```

To repeat, use a **new** destination such as `complete_run_v3`. All runners reject existing output directories. Runtime dependencies are Python, NumPy and pandas, plus the author's existing project dependencies. No network is required. Git must retain baseline `8821961853e4068febbfe2712f9a4e1036c9e629`.

`run_v2.py` runs both author packages into fresh subdirectories, executes both independently written reviewers, compares all 33 fresh author files with their canonical files, verifies the 13 input bindings and creates the combined receipt. The individual reviewers also compare against their first retained reruns (`source_rebuild_v1` and `prospective_rebuild_v1`); the wrapper additionally checks the current invocation's fresh outputs. Keep these proof directories when moving the package. The combined receipt lists exact reviewer code, source and author correction hashes. The child receipts list all author result hashes.

Initial commands retained in the audit trail:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/source_audit_v1/run.py --out data/processed/forecast_methods/quant_thesis_validation_v1/independent_reproduction_v1/source_rebuild_v1
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/independent_reproduction_v1/source_review.py --out data/processed/forecast_methods/quant_thesis_validation_v1/independent_reproduction_v1/source_review_v1
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/prospective_v1/run.py --out data/processed/forecast_methods/quant_thesis_validation_v1/independent_reproduction_v1/prospective_rebuild_v1
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 -m unittest discover -s analysis/src/forecast_methods/quant_thesis_validation_v1/prospective_v1 -p test_prospective.py -v
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/independent_reproduction_v1/prospective_review.py --out data/processed/forecast_methods/quant_thesis_validation_v1/independent_reproduction_v1/prospective_review_v1
```

`run.py` and `complete_run_v1` are the retained first combined attempt. Its raw-checkout-versus-Git hash assumption failed on Windows line endings after all numerical reviews passed. `run_v2.py` repairs only that check: exact Git blob hashes remain mandatory, while the local checkout is allowed the separately recorded CRLF-to-LF transformation. No empirical specification or score was changed.

Interpret the result using `docs/revenue-forecast-strategy/quant_thesis_validation_v1/independent_reproduction_v1/INDEPENDENT_REPRODUCTION_v1.md`. All dollar tolerances are 1e-6 USD million; squared-error comparisons use the same conservative numerical tolerance in their own squared units. Calculations compare full-precision values, not presentation-rounded tables. No registration or commit is performed.
