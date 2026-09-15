# Independent GBV decision review — replay commands

Run from `C:/Users/wille/Desktop/Citadel - ABNB/.worktrees/submission-readiness-v1`. Every output directory must be NEW. These commands write only additive reviewer outputs; no registry or scorer writes.

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' 'analysis/src/forecast_methods/gbv_decision_0915_v1/review_v1/check_outputs.py' --out 'data/processed/forecast_methods/gbv_decision_0915_v1/review_v1/horizon_replay_v2'
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' 'analysis/src/forecast_methods/gbv_decision_0915_v1/review_v1/boundary_checks.py' --out 'data/processed/forecast_methods/gbv_decision_0915_v1/review_v1/boundary_replay_v2'
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' 'analysis/src/forecast_methods/gbv_decision_0915_v1/review_v1/street_checks_v2.py' --out 'data/processed/forecast_methods/gbv_decision_0915_v1/review_v1/street_replay_v3'
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' 'analysis/src/forecast_methods/gbv_decision_0915_v1/review_v1/supplement_checks_v2.py' --out 'data/processed/forecast_methods/gbv_decision_0915_v1/review_v1/supplement_replay_v3'
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' 'analysis/src/forecast_methods/gbv_decision_0915_v1/review_v1/registration_checks.py' --out 'data/processed/forecast_methods/gbv_decision_0915_v1/review_v1/registration_replay_v2'
```

Canonical passed receipts currently reside in `horizon_v1`, `boundary_v1`, `street_v2`, `supplement_v2`, `registration_v1`. No author code is imported by the arithmetic/source scripts. `boundary_checks.py` deliberately imports the accepted author code for future-information poisoning and positive controls; it uses the unchanged model, not a search. The economic/statistical samples are small and overlap; do not present software check counts as validation sample size.

Full results, limitations, exact failed-attempt explanations and RESUME: `docs/revenue-forecast-strategy/05_backtests/GD_REVIEW_RESULTS_v1.md`. Source tables use raw guide midpoints; the registry's interval scores are separate. Preregistered new descriptive diagnostics are saved in `review_v1/horizon_v1/covariance_reconciliation.csv` and `regime_descriptive.csv`.
