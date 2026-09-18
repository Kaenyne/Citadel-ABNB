# Joint effective booking-share / GBV-conversion audit

Run from the repository root, using the existing virtual environment. All inputs are read-only; every output directory must be new.

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_joint_cohort_v1/quant_v1/run.py
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_joint_cohort_v1/quant_v1/diagnostics.py --core data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/results_v1 --out data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/diagnostics_v1
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -m unittest discover -s analysis/src/forecast_methods/gbv_joint_cohort_v1/quant_v1 -p test_quant.py -v
```

For reproduction use `run.py --out <new directory>`, then `diagnostics.py --core <that directory> --out <another new directory>`. The 200 bootstrap draws are the preregistered count; do not use a lower draw-count run as final evidence. A full run takes several minutes because it preserves three optimizer starts for every clustered bootstrap fit.

The source preregistration and timing addendum are `JOINT_COHORT_QUANT_PREREG_v1.md` and `JOINT_COHORT_QUANT_PREREG_ADDENDUM_v1.md` under `docs/revenue-forecast-strategy/05_backtests/`. Read the result note before interpreting any percentage. `verdict.json` uses `FAIL_no_current_direct...` for an evidence-policy gate; supplemental `evidence_status.json` clarifies that actual cohort measurement is **UNAVAILABLE**, not empirically rejected.

## What is built

One matrix supports backward allocation shares and forward effective fee dollars per net reported GBV dollar. It includes current-quarter bookings, one/two earlier quarters and a finite older tail. The primary fitted shape has 7 degrees of freedom: 3 independent pooled exposure weights and 4 seasonal scales. Guide conversion adds one shared trailing-eight **arithmetic mean** cushion estimate. The PR60 flight ablation adds one slope. The flexible LP has 36 season-by-lag coefficients on 14 or10 observations and is labelled an identification diagnostic, not a forecasting competitor.

Neither reported GBV nor these fitted allocations identify original gross-booking survival, cancellation rates, RNPL causality, or actual Airbnb revenue by reservation cohort. The main finite tail has lags3 and4; tail3 and lags3–8 are separate sensitivity runs, with older exposure unknown. K2 bounds act on backward column shares in a separately marked, stale Melbourne accommodation assumption; they do not become forward coefficients.

## Output guide

- `model_matrix.csv`: assumed seasonal-model A dollars, column-conditional backward share, A/actual revenue attribution, A/reported booking-quarter GBV effective coefficient, residual, lag and finite-tail flags.
- `realized_conditional_matrix.csv`: same fitted exposure shape rescaled to actual revenue for an exact accounting identity. This is an assumed allocation and cannot establish cohort observations.
- `nearfit_shapes.csv`, `nearfit_bounds.csv`: coarse simplex shapes fitting within0.25pp RMSE of the best, with conditional share and coefficient ranges. These are sensitivity sets, not confidence intervals.
- `bootstrap_intervals.csv`, `parameter_year_deletion.csv`: conditional parameter uncertainty from200 year-cluster resamples and deletion of each year. Few independent years materially limit inference.
- `conditional_temporal_variance.csv`: sample within-season variation under an imposed fixed shape. Tail `effective_coefficient_sum` sums coefficients on distinct denominators, not one pooled cohort conversion rate.
- `conditional_dollar_covariance.csv`, `covariance_identity.csv`: dollar covariance and full variance identity.
- `flexible_identification_bounds.csv`, `flexible_design_rank.csv`, `flexible_witness_matrices.csv`: normalized fractional-LP share bounds, rank/nullity, and alternative allocations with dollar residuals. Support and fit tolerances are explicit.
- `stale_k2_conditional_bounds.csv`: conditional feasibility and ranges under old Melbourne share assumptions. Infeasibility concerns these joint assumptions and spec, not observed current Airbnb cohorts.
- `pit_predictions.csv`: t−2 earnings origin, before t−1 release issues target-t guide; both t and t−1 GBV are forecast without seeing realized values. Forecast/actual/oracle are separate columns. `pit_skipped_origins.csv` lists all warmup failures.
- `pit_scores.csv`, `pit_score_deletions.csv`: paired-origin revenue/guide comparison against fixed2/3–1/3 EWM; primary `tail34`, alternatives separate.
- Supplemental `paired_forecast_uncertainty.csv`: 2,000 paired year-cluster RMSE-ratio/loss-difference resamples.
- Supplemental `pr60_flight_*`: actual one-slope auxiliary forecast test with exact stored UTC commit gating and recorded training pairs. Source raw mirror/40-state coverage is not recertified locally.
- Supplemental `forward_booking_rows.csv`: row totals and explicit left/right censoring within available history; tail beyond4 unknown.
- Supplemental `live_nearfit_*` and `nearfit_*covariance*`: conditional Q3'26–Q2'27 model sensitivity and covariance, not promoted forecasts or probabilistic intervals. Q3'26 guide was already issued and is labelled an implied-guide diagnostic.

## Decision

Do not quote modeled booking-cohort percentages as established pitch facts. A smaller candidate improves point guide RMSE in the sampled replay but fails deletion stability; paired intervals include no improvement. Retain it as a research challenger. Do not replace the live forecast. The useful next input is a directly observed booking-date × recognition-date value matrix with fee/cancellation definitions and historical vintages; aggregate flight/review/calendar signals cannot substitute for it.
