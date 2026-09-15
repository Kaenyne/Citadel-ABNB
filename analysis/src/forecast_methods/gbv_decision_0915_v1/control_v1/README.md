# Additive research registration and unchanged scorer verification

`register.py` consumes only accepted horizon `results_v2/predictions.csv`. It excludes oracle and calendar-origin histories and registers18 distinct method objects: guides from four frozen methods, and revenue from joint/fixed, at three advance horizons. It retains all available historical rows and18 LIVE research points. There are421 registry rows including overlapping W1/W2 entries, not421 independent observations.

The complete prepared payload was independently checked before writing. Registration is not forecast promotion. Growth-rule n_train=0 means no fitted regression; its source anchors are separate. Required q50 copies the point solely for format compatibility; no calibrated distribution is claimed.

Commands used from the worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/control_v1/register.py --predictions data/processed/forecast_methods/gbv_decision_0915_v1/horizon_v1/results_v2/predictions.csv --out data/processed/forecast_methods/gbv_decision_0915_v1/control_v1/registered_v1 --write
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_joint_cohort_v1/control_v1/run.py --out data/processed/forecast_methods/gbv_decision_0915_v1/control_v1/scored_v1 --before data/processed/forecast_methods/gbv_joint_cohort_v1/control_v1/next_guide_after_v1
```

All destinations now exist and must not be overwritten. The registry rejects another write to the same method objects. A future replication can build rows in memory, compare against prepared files, and run the unchanged scorer wrapper into a new directory. `registered_v1/receipt.json` and `scored_v1/receipt.json` are authoritative.

Both frozen scorers exit0 and agree on328 score rows. All292 earlier score rows and126 protected prior files remain unchanged;144 files are now protected. Expected PIT-only and incomplete-warmup warnings are retained in the root registration log. These replays do not fabricate full-sample counterparts. Scorer ratios that omit baseline vintage are not authoritative for this question, and the frozen scorer uses raw midpoint errors. Local paired comparisons and the separate interval-convention supplement govern interpretation.
