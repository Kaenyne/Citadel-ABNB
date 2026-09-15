# Joint-cohort next-guide clarification — complete

15 September 2026 · `codex/submission-readiness-v1`. Additive completion of `WORKBOARD_JOINT_COHORT_NEXT_GUIDE_v1.md`.

The exact frozen-rule Q4 2026 comparison is calculated, independently checked and recorded. Joint guide midpoint: $3,185.247392m; fixed-lag guide midpoint: $3,160.552138m. Both have a truthful calculation vintage of 15 September 2026 and last published company inputs of 6 August 2026. No new feature, calibrated interval, Street comparison or model promotion was introduced.

## Deliverables

- [Plain-English explanation, next-guide points and limits of the edge claim](05_backtests/JOINT_COHORT_NEXT_GUIDE_EXPLAINER_v1.md)
- [Quant calculation and deterministic validation](05_backtests/JOINT_COHORT_NEXT_GUIDE_v1.md)
- [Independent next-guide review](05_backtests/JOINT_COHORT_NEXT_GUIDE_REVIEW_v1.md)
- Code and README: `analysis/src/forecast_methods/gbv_joint_cohort_v1/next_guide_v1/`
- Source-labelled points, GBV inputs, contributions, training and cushion tables: `data/processed/forecast_methods/gbv_joint_cohort_v1/next_guide_v1/results_v1/`

The quant's complete new-directory rebuild reproduces the six result files and manifest byte-for-byte, with four sources unchanged. The independent reviewer reproduced inputs and arithmetic with 117 checks passing, and accepted both staged registry rows with 20 checks passing. These checks verify the calculation; they are not new economic observations or a predictive-performance test.

## Registration and scoring

Two new research LIVE-only objects were registered through FORMAT 1.1 under `gbv-joint-next-guide-v1`: `joint-guide` and `fixed-guide`. Their point/q50 equality is a format placeholder; no predictive bands or Street values are registered. Exact commands, run from this worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/gbv_joint_cohort_v1/control_v1/register_next_guide_v1.py --points data/processed/forecast_methods/gbv_joint_cohort_v1/next_guide_v1/results_v1/points.csv --out data/processed/forecast_methods/gbv_joint_cohort_v1/control_v1/next_guide_registered_v1 --write
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/gbv_joint_cohort_v1/control_v1/run.py --out data/processed/forecast_methods/gbv_joint_cohort_v1/control_v1/next_guide_after_v1 --before data/processed/forecast_methods/gbv_joint_cohort_v1/control_v1/after_v1
```

Both commands exited zero; both unchanged scorer implementations exited zero and agreed on all 292 historical score rows. All 292 previous scores and all 124 files in the immediate pre-registration preservation inventory were unchanged. The two new registry files raise that inventory to 126. LIVE rows are not scored against unissued guidance. Receipts are `control_v1/next_guide_registered_v1/receipt.json` and `control_v1/next_guide_after_v1/receipt.json` under the processed package. Do not rerun registration against existing object names; use new output names for read-only reproduction.

## RESUME

This clarification is complete. Explain that a GBV aggregate predictor can be useful even when its physical cohort decomposition is unidentified, while keeping the prior failed forecast-promotion verdict visible. The public bookings-to-revenue mechanism is real; precise cohort timing, a causal RNPL effect and a robust advance guide-surprise advantage over the Street remain unproven. Both current estimates depend on projected unreported Q3 GBV, and the joint additionally uses projected Q4 GBV. Further work should target those missing data or a preregistered same-information-date Street comparison rather than reinterpret this close model pair as established precision.
