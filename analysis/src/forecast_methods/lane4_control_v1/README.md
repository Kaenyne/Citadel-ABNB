# Lane 4 provenance and scorer control

Run from the isolated L4 repository root, using a Python environment with the repository requirements. Every snapshot name must be new; existing receipts are refused.

```powershell
python -X utf8 analysis/src/forecast_methods/lane4_control_v1/run.py init --snapshot baseline --fx-dependency "C:/Users/wille/Desktop/Citadel - ABNB/FX_ENGINE_SESSION_BUNDLE"
python -X utf8 analysis/src/forecast_methods/lane4_control_v1/run.py verify --snapshot initial --tests
python -X utf8 analysis/src/forecast_methods/lane4_control_v1/run.py verify --snapshot close --tests
```

The runner hashes every pre-existing tracked file and the explicitly supplied external read-only FX bundle. It imports the existing Lane 2 comparator and scorer wrapper, calls both actual scorers with only output paths redirected, and compares all 284 completed Lane 2 score rows with exact keys/discrete values/missingness and strictly less than 1e-9 absolute floating error (zero relative tolerance). No protected source or output is overwritten. New LIVE rows are not evidence of historical effectiveness. The parent runs this after registrations; subagents never score.

The supplied `baseline`, `initial` and `close` receipts are immutable. On a reproduction, use a new verification name, such as `review_recheck_01`; do not rerun `init` on a later commit. The `close` snapshot follows the September 13 registration of 14 LIVE rows across four new scenario objects. Both scorers see 4,232 rows / 76 objects; all 284 existing historical score rows are exactly unchanged.

## Independent export and arithmetic review

These checks read the actual exported XLSX and revenue tables. They do not author the workbook or reuse its financial calculations as the test oracle. Use new output receipt names:

```powershell
python analysis/src/forecast_methods/lane4_control_v1/review_revenue.py --revenue-dir data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1 --output data/processed/forecast_methods/lane4_control_v1/revenue_recheck_01.json
python analysis/src/forecast_methods/lane4_control_v1/review_exports.py --workbook model/lane4_v1/outputs/lane4_model/snapshot_v4/ABNB_L4_review.xlsx --model-dir data/processed/forecast_methods/lane4_model_v1/snapshot_v4 --output data/processed/forecast_methods/lane4_control_v1/workbook_recheck_01.json
```

The revenue check reconstructs all 15 scenario-quarter rows from reported/forecast GBV and the preserved K0 public API. The workbook check reads OOXML formulas and cached values, refuses errors/external links, and independently checks 91 cells against reproducible Python outputs and the legacy valuation anchors. Final workbook hash and exact tolerances are in `independent_workbook_review_final.json`.

## Registration policy

`register.py` validates all scenario frames through the unchanged FORMAT 1.1 validator before writing any registry file. It requires the actual run date and matching forecast information date, separate current scenarios, no accepted L3 replacement hidden in a baseline, and no existing destination file. It intentionally refuses to re-register the already published method/object names. The exact completed command was:

```powershell
python analysis/src/forecast_methods/lane4_control_v1/register.py --revenue-dir data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1 --snapshot registration_final --register
```

Do not rerun that mutation. A future accepted L3 model or new vintage needs an explicitly reviewed new package/object and a real current date. The new point forecasts have no historical observations or calibrated probability distribution; copying each deterministic point to the schema's q50 field does not supply one.

Before publication, `review_staging.py --output <new-receipt.json>` compares every new branch index blob with its actual bytes, refuses changes to pre-existing files and runtime/bundle files, and captures a bounded `git diff --cached --check` result. New L4 paths have scoped exact-byte Git attributes to preserve checksum-backed outputs across checkouts. The initial normalization mismatch and its repair are recorded in `staging_failure_01.json`; the final staged-file audit passes.

## RESUME

Use a new verification snapshot for every subsequent check. The baseline manifest is immutable. Preserve any failure receipt and investigate before continuing affected work. The original workspace FX path is intentionally external and must be supplied explicitly on a new machine; never stage that bundle wholesale.
