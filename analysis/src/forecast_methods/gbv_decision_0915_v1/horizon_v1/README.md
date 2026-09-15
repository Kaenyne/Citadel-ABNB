# GBV decision audit — forward guide horizons

This package freezes the accepted joint and fixed GBV rules and compares the next one/two/three **unissued** guides (target p+2/p+3/p+4, where p is the latest published company quarter). It does not rerun feature selection, change weights policy, or infer reservation cohorts. Workboard/spec: `WORKBOARD_GBV_DECISION_0915_v1.md`.

Run from the repository root using the existing virtual environment:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/horizon_v1/run.py --out data/processed/forecast_methods/gbv_decision_0915_v1/horizon_v1/results_v2
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/horizon_v1/calendar_arm.py --release data/processed/forecast_methods/gbv_decision_0915_v1/horizon_v1/results_v2 --out data/processed/forecast_methods/gbv_decision_0915_v1/horizon_v1/calendar_arm_v1
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/horizon_v1/eligibility_audit.py --source data/processed/forecast_methods/gbv_decision_0915_v1/horizon_v1/results_v2 --out data/processed/forecast_methods/gbv_decision_0915_v1/horizon_v1/eligibility_audit_v1
```

Every output directory must be new. The displayed paths contain the accepted saved run already; choose different names for subsequent reproduction. `rebuild_v2/` repeats the full model run; `calendar_arm_rebuild_v1/` and `eligibility_audit_rebuild_v1/` repeat the respective supplements. Integrity checks:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/horizon_v1/validate.py --first data/processed/forecast_methods/gbv_decision_0915_v1/horizon_v1/results_v2 --rebuild data/processed/forecast_methods/gbv_decision_0915_v1/horizon_v1/rebuild_v2 --out data/processed/forecast_methods/gbv_decision_0915_v1/horizon_v1/validation_v1/receipt.json
```

`results_v1` is retained as the initial output. `results_v2` makes the oracle metadata explicit: oracle rows use future actual-publication `knowable_from`, `point_in_time_eligible=False`, and `oracle_future_information_used=True`; the original coefficient-information date remains separate. Production values and statistical results did not change.

## Models and origins

Joint: fit all complete already-published history with the accepted3-start optimizer, pooled current/lag1/lag2/average(lag3,lag4) weights, and4 seasonal scales. Minimum8 complete rows and all4 seasons. Fixed: unchanged2/3 lag1 +1/3 lag2 and same-season EWM conversion. Each unknown GBV is projected using same-quarter year-ago GBV times the latest published GBV growth factor. All cases share an arithmetic-mean trailing8 cushion.

Direct-guide-growth carries the latest **already-issued** guide year-on-year growth onto the target year-ago issued guide. At the p earnings origin, guide p+1 is already available and is admitted. Revenue-growth carries the latest published revenue growth onto target year-ago realized revenue, then divides by the shared cushion. Missing anchors abstain. The direct guide baseline's revenue column is an explicitly labelled guide-times-cushion proxy.

Parameter counts: joint7 revenue/8 guide; fixed4 seasonal scales/5 including cushion; direct guide-growth0 estimated guide parameters/1 for its implied revenue cushion; revenue-growth0 revenue/1 guide cushion. Observed growth-carry transforms are rules, not extra fitted regression coefficients. Historical information dates are calendar release dates after the current actuals and guide are issued. The live cutoff is15September2026, last company data6August2026; live targets stop at2027Q2. Missing exact future issue dates remain blank.

## Output map

- `predictions.csv`: long-format model/origin/target points with eligibility, actual outcomes, cushion, training metadata, and known/projected GBV dollar exposure. Oracle rows are not registerable.
- `wide_predictions.csv`: matched per-origin points; candidate=joint, baseline=fixed; simple baselines and oracle columns explicit.
- `gbv_inputs.csv`, `gbv_contributions.csv`: per-lag forecast/actual status and model-dollar arithmetic. Exposure shares are not observed reservations or backlog coverage.
- `origin_fits.csv`, `baseline_source_anchors.csv`: complete training-quarter lists and already-issued guide/revenue anchors.
- `skipped_predictions.csv`, `coverage.csv`: all missing prerequisites, all available sample counts and primary common-sample targets.
- `scores_common.csv`: identical rows for joint, fixed, guide-growth and revenue-growth. `scores_all_available.csv` is descriptive, not an apples-to-apples ranking.
- `paired_comparisons.csv`, `score_deletions.csv`: paired metrics,2000 fixed-seed year-cluster intervals, and year/quarter deletion stability.
- `error_variance_decomposition.csv`: total error=input-error component+oracle residual, with twice covariance preserved. Oracle information cannot be traded and partial GBV improvements need not translate one-for-one into total-error improvements.
- `promotion_gates.csv`: original common-four-model gate. Read **together with** the standalone eligibility supplement before recommending any model.
- `calendar_arm_v1/`: separate information dates start(p+2) minus16days, preregistered in `GD_CALENDAR_ORIGIN_ADDENDUM_v1.md`. Points are reused only after verifying identical company actual and issued-guide information. Source/release/new dates all remain explicit. This supplies the Street agent a properly dated input, not a Street result.
- `eligibility_audit_v1/`: separately preregistered candidate-specific common rows, requiring candidate+both simple baselines but not the other candidate's availability. Its coverage table shows exactly which earlier rows are restored.

## Interpretation

The fixed p+4 model passes the original common9-row gate, a favorable conditional result that is retained. It fails the broader standalone W1 evaluation once its own earlier eligible origins are included. Joint fails all three horizons. This supports retaining GBV as an auditable forecast/scenario input and challenger, while stopping short of a proven overall forecasting edge or physical-cohort story. W1/W2 overlap; common p+3 and p+4 samples are identical between windows, not independent replications. No historical error SD or model-set range is presented as a calibrated future probability interval. Read `GD_HORIZON_RESULTS_v1.md` for the complete quantitative interpretation.
