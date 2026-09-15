# Joint cohort data admissibility audit

Read-only audit of actual local schemas, source manifests, and date coverage. Does not fetch data, expose individual review/calendar records, fit a model, or register forecasts.

From the worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_joint_cohort_v1/data_audit_v1/run.py
```

Output defaults to `data/processed/forecast_methods/gbv_joint_cohort_v1/data_audit_v1/`. Use `--out NEW_DIRECTORY` for a repeat run. Existing output directories are refused. `evidence_inventory.csv` is the explicit economic admissibility judgment; `field_profile.csv` verifies available column names, nonnull counts and safe date-field ranges. Ranges are lexical where source formatting is irregular; they are not invented dates. `sample_manifest_locality.csv` reconciles advertised sample paths to files actually present; nested/non-string manifest file entries are counted separately and not resolved speculatively. `summary.json` contains PR60 ancestry and input SHA-256 hashes. Missing files remain missing and are never silently replaced with manifest descriptions. All current direct-cohort eligibility flags are false because no inspected local source meets the full economic field requirements; a dated aggregate demand predictor is a different object.
