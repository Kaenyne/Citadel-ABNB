# Calendar-timed flight ablation

One predefined timing repair, specified in `GD_CALENDAR_FLIGHT_PREREG_v1.md` before execution. It uses the same forecast rules as the accepted horizon package, changes the feature/training observation clock to the calendar origin used for the current decision, and adds one bounded slope. No live guide is emitted. All source files and previous failures remain unchanged.

Run from the worktree root, choosing a new output directory:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/calendar_flights_v1/run.py --out data/processed/forecast_methods/gbv_decision_0915_v1/calendar_flights_v1/results_v1
```

The initial output already exists; use a fresh suffix when reproducing. Accepted results are `results_v1`; independent replication is `rebuild_v1`. `run.py` asserts future-outcome and future-flight invariance, no-flight reconstruction, publication/commit gates, six-model common coverage and unchanged input hashes. Independent review is in `review_v1/supplement_v2`.

Primary result: nine common historical targets (identical W1/W2 sets), two genuinely current-quarter flight features. Joint RMSE rises from67.12m to80.30m; fixed falls from78.81m to75.68m but misses the10% gate and remains worse than guide-growth63.51m. Both fail. These are raw midpoint errors; the separate `interval_v1` supplement handles letter rounding. No claim of physical cohort measurement or cancellation causality follows.

Historical origins are `start(target) −16 calendar days`, not earnings dates. Frozen W1/W2 validators cannot register them. Retain exact dates locally and use the harness change request in `GD_CALENDAR_FLIGHT_RESULTS_v1.md`; never backdate a forecast to make it validate.
