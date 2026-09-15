# Comparable Q4 2026 next-guide snapshot

This is a bounded continuation of accepted `quant_v1/run.py`, imported without modification and checked against its accepted SHA-256. Workboard/spec: `WORKBOARD_JOINT_COHORT_NEXT_GUIDE_v1.md`. No new feature search, model rule or performance test.

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_joint_cohort_v1/next_guide_v1/run.py
```

For a rebuild supply `--out` with a new directory. Existing output directories are refused. Output files: `points.csv` (joint/fixed comparison), `gbv_inputs.csv` (reported/forecast flags), `contributions.csv` (dollar arithmetic), `cushion_history.csv` (last8 completed quarters), `training_rows.csv`, `model.json`, and source/code/output hashes in `manifest.json`.

The snapshot is calculated15September2026 using company inputs last published6August2026. Both Q3 and Q4GBV are forecast from the same latest-published growth carry rule. The joint model refits on all20 complete published quarters,2021Q3–2026Q2, as the accepted historical replay specifies. This differs from the earlier14/10-quarter W1/W2 descriptive sensitivity fits. The fixed comparator uses the same projectedQ3GBV and shared arithmetic-mean8-quarter cushion.

Values are research snapshots, not promoted forecasts. The prior forecast-robustness failure and unavailable physical-cohort data remain unchanged. No predictive interval, new Street comparison, RNPL causal estimate or stock target is supplied. Fitted exposure weights/dollar contributions do not measure actual reservation cohorts.
