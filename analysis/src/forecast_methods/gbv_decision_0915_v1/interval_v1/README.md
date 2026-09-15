# Guide integer-letter interval sensitivity

An additive audit of saved guide predictions. It imports no forecasting code and estimates zero new parameters. Both raw midpoint and signed distance to midpoint ±0.5 USD million are evaluated with identical samples, paired year-cluster draws and deletions. It covers the three-horizon common-four-model and standalone candidate comparisons, plus the saved calendar-flight remedy test. No predictions, live points, registry rows or frozen scorers change.

From the worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/interval_v1/run.py --out data/processed/forecast_methods/gbv_decision_0915_v1/interval_v1/results_v1
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/interval_v1/run.py --out data/processed/forecast_methods/gbv_decision_0915_v1/interval_v1/rebuild_v1
```

Existing output directories fail rather than overwrite. For further reproduction choose a new directory. Inputs and outputs are hashed; the script validates all saved raw pair statistics and promotion gates before writing. `scores.csv` contains model loss on each exact sample; the common4 sample is repeated for each candidate for explicit pairing and must not be summed as independent observations. `comparisons.csv` contains n, targets, paired 90% ratio intervals and worst deletion ratio. `deletions.csv` retains every paired year/quarter deletion. `gates.csv` records each scoring basis; `gate_changes.csv` compares all gate components. `receipt.json` records edge and raw replication checks. `manifest.json` binds the code, preregistration and source/output hashes.

Accepted `results_v1` and `rebuild_v1` are byte-identical. There are no gate changes. The restricted fixed p+4 common9 result passes under both scoring conventions; broader standalone eligibility and all joint/calendar-flight promotion tests fail. The interval represents integer-rounding uncertainty, not the corporate guide range, a prediction interval or a new validation sample. Both frozen harness scorers still use raw midpoint error; see `GD_GUIDE_INTERVAL_HCR_v1.md`.
