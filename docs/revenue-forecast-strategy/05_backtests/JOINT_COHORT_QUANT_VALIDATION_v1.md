# GE-JOINT-QUANT — completed deterministic validation

15 September2026, `codex/submission-readiness-v1`. Addendum to `JOINT_COHORT_QUANT_RESULTS_v1.md`; its pending rebuild is now complete.

Core `run.py` was independently rerun into new `quant_v1/rebuild_v1/`, exit0. All21 output files were byte-identical to the original run, as were the manifests. The6 registered input hashes remained unchanged. The validator separately checked120 saved model-matrix rows and30 saved PIT rows for denominator/residual identity, nonnegativity and origins preceding guide events. Original core manifest SHA-256: `9867d8c9822132f4f07a057083fd053f1fc3ff96c7cd6fd8cd6b7a4e9cdc44fb`. Code SHA-256: `6f395b2956762f179701e78f4c6743ba523da55e45cb7c9f742a2151aa2495af`.

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_joint_cohort_v1/quant_v1/run.py --out data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/rebuild_v1
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_joint_cohort_v1/quant_v1/verify.py --first data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/results_v1 --repeat data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/rebuild_v1 --out data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/validation_v1/core_rebuild_receipt.json
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_joint_cohort_v1/quant_v1/diagnostics.py --core data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/rebuild_v1 --out data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/diagnostics_rebuild_v1
```

The supplemental diagnostics also completed their full rerun, including2,000 paired cluster draws, actual PR60 flight ablation and conditional future sensitivities. Every file in the supplemental manifest's output hash map matched the original exactly. Receipts are `quant_v1/validation_v1/core_rebuild_receipt.json` and `diagnostics_rebuild_receipt.json`; all output directories remain additive. Both runs refuse an already existing output directory, so future reruns require new paths.

Original core build directory-to-manifest timestamps span approximately7m22s; repeat approximately7m01s. The integrity result does not alter the analytical verdict: current corporate physical cohort measurement **UNAVAILABLE**, inferred-cohort precision **FAIL**, early-guide predictive promotion **FAIL** despite better point RMSE. Eleven core tests pass. Independent review reports24 distinct reviewer tests plus separate saved-output checks; the review counts overlap and should not be added into a fabricated grand total. No remaining implementation defect was reported by the reviewer.

## RESUME

Quant implementation and validation are complete. Parent can finish the visual explanation and any separately controlled rejected-forecast registration/scoring. Preserve the uncertainty and origin/source qualifications; do not promote the candidate or headline its inferred booking shares. New direct cohort data should enter as compatible observations/restrictions on the same dollar matrix, with a new preregistration and output version.
