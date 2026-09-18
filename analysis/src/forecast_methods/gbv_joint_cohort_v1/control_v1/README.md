# Preservation and scoring

Run from the worktree root with the repo Python interpreter:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/gbv_joint_cohort_v1/control_v1/run.py --out data/processed/forecast_methods/gbv_joint_cohort_v1/control_v1/before_v1
```

For the after check, use a new `--out` and point `--before` to the first output directory. Both unchanged scorer `main()` functions execute with runtime output-path redirection through the prior audited preservation helper. No frozen source or scoreboard is edited. This wrapper performs no registration.
