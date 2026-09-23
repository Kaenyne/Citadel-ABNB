# Q4 runner portability addendum

2026-09-14 · author-owned repair; parent reviews. The initial uncertainty runner required HEAD to equal the L3 baseline. That would unnecessarily prevent reproduction after the quant task committed its new protocol without changing evidence. Its original source and results remain preserved.

New canonical source is `analysis/src/forecast_methods/quant_thesis_validation_v1/uncertainty_audit_v1/run_v2.py`. It verifies that the baseline commit exists and is an ancestor of the current HEAD, while preserving exact bundle identity, 108 payload hashes, 24 acceptance-output bindings and source-lag/score checks. Its summary now distinguishes `baseline_commit` from `observed_head`. No numerical formula, estimator or uncertainty calculation changed.

Successful command at protocol commit `acab9377aa9b00ecc3dcab380108248b1c982ff9`, exit 0 in 1.48 shell seconds:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 'analysis/src/forecast_methods/quant_thesis_validation_v1/uncertainty_audit_v1/run_v2.py' --out 'data/processed/forecast_methods/quant_thesis_validation_v1/uncertainty_audit_v1/results_v2'
```

This is an author repair verification, not independent review. The canonical analytical note remains `UNCERTAINTY_AUDIT_v2.md`; all numerical tables retain their earlier results. A repeat requires a new destination, such as `results_v3`.

## RESUME

Use the v2 runner after the task's new commits and retain the initial protected L3 evidence. Parent should check this narrow guard change. Do not treat this author-run repair as worker C independently reproducing itself; Wave3 G reviews worker A in separate directories.
