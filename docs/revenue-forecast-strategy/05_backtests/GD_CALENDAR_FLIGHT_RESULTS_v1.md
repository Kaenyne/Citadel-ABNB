# GD calendar-flight remedy — results and harness change request

15 September2026. Parent-owned bounded remedy, independently checked by chart_auditor. The preregistration `GD_CALENDAR_FLIGHT_PREREG_v1.md` predates both code and performance. This tests whether the previous flight correction becomes useful at the actual between-earnings information date. It preserves the separate failed release-day ablation.

The target is p+2, the next unknown guide. Evaluation origins are start(p+2) minus16 calendar days. For each earlier unprinted GBV target r, a training feature is reconstructed at start(r+1) minus16 days; the eventual GBV outcome must be published before evaluation. Eligible flight rows need the exact stored commit UTC at or before origin midnight, at least75 days, finite growth and no more than two quarters of staleness relative to the latest published company quarter. Current-quarter rows are allowed only when actually committed. The same bounded one-slope rule as the earlier ablation is fitted on at least six complete pairs. Both unknown GBV quarters use that adjusted growth recursively; conversion coefficients and the shared cushion remain frozen at their original fits.

## Results

Nine historical targets survive the training requirement; two warm-up targets are skipped explicitly. W1 and W2 contain the same nine observations across three target-year clusters. Only two evaluation rows use genuinely current-quarter flight data. Positive fitted slopes range0.16382–0.25055. There is one additional fitted parameter, beyond the joint seven conversion parameters or fixed four seasonal multipliers and the common one-parameter guide cushion.

| Model | Raw guide RMSE, USDm | MAE, USDm | Bias, USDm |
|---|---:|---:|---:|
| Joint without flight correction |67.12|47.33|−27.18|
| Joint with flight correction |80.30|58.49|−54.15|
| Fixed without flight correction |78.81|61.37|+12.64|
| Fixed with flight correction |75.68|59.92|−9.02|
| Direct guide growth |63.51|60.17|−5.74|
| Revenue growth / cushion |130.64|109.18|−19.36|

The joint error increases19.64%; the fixed error decreases3.97%, short of the preregistered10% improvement. Both candidates fail deletion stability and remain worse than direct guide growth. Both remedy gates fail. All paired2,000-draw year-bootstrap ratios and individual year/quarter deletions are retained. The separate interval supplement addresses the repo's letter-rounding convention; these displayed scores are raw midpoint errors.

On15September, Q3’s day75 EU40 flight observation is available through the14September06:56:53UTC commit and records3.041507% growth. This is only a documented available feature. No live flight-adjusted guide is emitted, and the feature's availability does not rescue the failed historical test. Inherited commit lineage and absent original daily blobs still qualify its source status.

## Reproduction and validation

Run from the worktree root using the main repo Python interpreter:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/calendar_flights_v1/run.py --out data/processed/forecast_methods/gbv_decision_0915_v1/calendar_flights_v1/results_v1
```

Accepted output already exists; use a new suffix. Replication is stored in `rebuild_v1`. The script checks future-outcome poisoning, future-feature poisoning, no-flight point reconstruction and all source dates. The independent reviewer verified835 source/training/formula/statistical facts without importing the author calculations. No numerical blocker remains; test counts do not increase the nine economic observations.

## HCR: admit genuine non-earnings research origins

Frozen FORMAT1.0/1.1 permit W1/W2 origins only on their guide-date spine, whereas this research asks a different, explicitly dated trading question. A future harness version should accept arbitrary historical information dates supported by timestamped source records, join baselines by target AND origin/horizon, and preserve original-source versus calculated-forecast dates. Do not change the frozen harness in this package. Calendar-arm and flight-arm histories remain explicitly unregistered research tables; the main release-origin forecasts register separately. Oracles are never eligible for registration. A second scoring-convention HCR is documented by the interval supplement.

## RESUME

This timing repair is complete and fails. Keep both flight experiments and their distinct clocks visible. Prioritize a demonstrably informative, historically dated GBV or guide-expectation source before testing another predictor; do not select a new feature/date/weight to fit the same nine outcomes. The current available flight statistic may describe travel activity, but it is neither an Airbnb booking cohort nor a validated guide adjustment.
