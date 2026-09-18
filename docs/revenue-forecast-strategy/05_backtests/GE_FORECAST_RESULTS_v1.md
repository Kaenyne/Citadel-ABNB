# GE forecast reliability — completed fixed-model audit

15 September 2026. Owner: roadmap_auditor. Preregistered scope: `GE_PREREG_v1.md`; no new fitted parameters, forecast optimization, shared registrations or scorer changes. Source research commit `4533811d8405403b7f465bda3b69790e4367b2d6` in the preserved quant-validation worktree. Canonical audit output: `data/processed/forecast_methods/gbv_event_v1/forecast_v1/results_v1/`.

**Verdict: the earlier-origin candidate still fails promotion.** Reproduction and accounting checks pass. The new audit quantifies missing-GBV risk and shows why variance cannot be added as if bookings, conversion and guidance policy were independent. It does not establish an event-trading edge or four-quarter probability bands.

## What ran

From the submission-readiness worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/gbv_event_v1/forecast/run.py --out data/processed/forecast_methods/gbv_event_v1/forecast_v1/results_v1
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/gbv_event_v1/forecast/test_forecast.py
```

Both final commands exited0. All20 original CSVs reproduced byte-for-byte, all13 original adversarial tests passed, and all10 new audit tests passed. The new tests include future-value poisoning at every21 frozen origin, symmetric attribution identities, covariance reconciliation, oracle labeling, saved input dates and manifest integrity. Every617 used-date check is strictly before the applicable origin. These counts measure engineering checks, not independent historical observations. Initial run failed before source calculations at Git's safe.directory ownership check; a process-local exact-directory setting resolved it without editing persistent Git configuration. `forecast_v1/attempt_1.json` retains that failure.

The existing method uses fixed two-thirds/one-third GBV lags, inherited K0 seasonal estimation, latest observed GBV year-over-year persistence for the unprinted lag, and the trailing-eight median realized revenue/guide divisor (at least three observations). Candidate complexity remains five estimated statistics: four seasonal conversions and one cushion, plus the inherited selection policy. New fitted parameters: zero.

## Historical forecasting reliability

Targets are first-issued guide midpoints. Origins are quarter start minus18calendar days, rolled to the prior/same QQQ close; matched historical origins are48–62days before guide issuance. W1=2023Q1–2026Q2, n12; W2=2024Q1–2026Q2, n10 nested. Candidate abstains in W1 2023Q1/Q3 under the retained seasonal eligibility policy. Baselines are compared on exactly the same rows.

| Method | W1 guide RMSE, USDm | W2 guide RMSE, USDm | W1/W2 MAE, USDm | W1/W2 bias, USDm |
|---|---:|---:|---:|---:|
| Existing early-origin candidate |63.445|63.696|52.134 /51.221|-7.180 /-3.514|
| Direct guide-growth baseline |74.331|60.834|See frozen_scores.csv|See frozen_scores.csv|
| Revenue-growth plus cushion baseline |117.309|121.926|See frozen_scores.csv|See frozen_scores.csv|

Primary errors use the existing administrative midpoint±0.5USDm convention. Raw midpoint candidate RMSE is63.856/64.099; the verdict is unchanged. The failed requirement was lower RMSE against both baselines in both windows plus year-deletion stability. Removing2023 from W1 leaves the recent window and loses to guide growth; in W2 removing2024 or2026 also fails. Leave-one-event comparisons beat guide growth on11/12 W1 deletions but only4/10 W2 deletions. No refit or deletion-based selection occurs.

Largest raw errors are2025Q3 (-119.361USDm) and2026Q2 (-104.276USDm). Together they contribute51.34% of W1 and61.14% of W2 raw squared error. This concentration is a sensitivity finding, not a reason to omit those outcomes.

## How much error belongs to unavailable GBV?

The oracle diagnostic replaces the forecast weighted-GBV input with eventual printed GBV and retains the exact early-origin lambda and cushion. It is unavailable before the announcement and does not refit at letter close.

| Raw error target | W1 RMSE, USDm | W2 RMSE, USDm |
|---|---:|---:|
| Candidate guide versus issued guide |63.856|64.099|
| Oracle-GBV guide versus issued guide |36.373|38.697|
| Candidate revenue versus realized revenue |65.685|66.580|
| Oracle-GBV conversion revenue versus realized revenue |48.664|52.690|

The guide and revenue rows have different targets and must not be conflated. The oracle improves aggregate errors in this sample; it does not make conversion error or policy risk vanish. It also is not the accepted L3 letter-close fixed-OLS experiment: that separate comparison uses different seasonal estimation and W1 n14. No unmatched bar is presented as proof of pre-event accuracy.

## Exact symmetric error allocation and covariance

Let guide be `X × lambda × P`, with `P=1/(1+cushion)`. Ex-post reference factors are actual weightedGBV, realizedrevenue/actualweightedGBV, and issuedguide/realizedrevenue. Average each factor's marginal contribution over all six orders of replacing these factors with their predicted values. These three Shapley contributions sum exactly to the raw guide error; rounding is a separate adjustment. The calculation is independently checked against the seven polynomial main/interaction terms in the original source. Attribution is symmetric but is not a unique causal decomposition of FX, RNPL or fees.

| Raw guide-error attribution | W1 RMS contribution, USDm | W2 RMS contribution, USDm |
|---|---:|---:|
| Weighted GBV |61.331|64.375|
| Conversion |47.708|51.679|
| Cushion/policy |31.417|34.376|

These RMS figures **cannot be added** or interpreted as independent loss percentages. W1 raw MSE=7024.518 diagonal second moments minus2946.907 cross moments=4077.611USDm². W2=7996.646-3887.971=4108.675USDm². Variance excludes mean effects: W1=6825.525-2798.273=4027.252; W2=7759.693-3662.674=4097.019USDm². Assuming independent effects would imply population SD82.617/88.089USDm versus actual63.461/64.008. Historical offsets need not persist in the next event. All pair cross moments, covariances and correlations are exported.

## Limitations and decision use

All original failures, abstentions, source dates and scenario labels remain. The history is a frozen-panel reconstruction, not an unrevised original-vintage archive or untouched holdout. Full source tables are loaded, then functional date filtering determines predictions; all-origin future-value poisoning leaves predictions unchanged. Forecasts freeze before scoring joins, not before source tables physically enter memory.

Six eligible bands cover6/6 guides with mean full width221.175USDm. The same six outcomes occur in both windows. This does not establish calibrated80% probabilities or tails. Most importantly, repeated historical late-prior-quarter origins **do not validate today's September2026 forecasts out to Q1/Q2 2027**. Longer-horizon four-quarter scenarios need explicit assumptions and cannot inherit a $64m RMSE or these coverage percentages as calibrated forward bands.

The user-facing workbook should show (1) paired pre-event losses, (2) the ex-post GBV substitution comparison with its availability warning, (3) per-event three-factor error bars including cancellation, and (4) variance/covariance reconciliation. Event return interpretation belongs to GE-EVENT. The failed forecasting hurdle and absence of calibrated longer-horizon uncertainty must remain in the two-page memo.

## RESUME

GE-FORECAST is complete. Parent may consume `forecast_audit.json`, `pre_event_forecasts.csv`, `per_event_decomposition.csv`, `score_summary.csv`, `variance_reconciliation.csv`, `shapley_cross_moments.csv` and the preserved influence/band tables. Join event dates through target quarter without discarding abstentions. Preserve oracle status and distinguish revenue from guide targets. Rebuild only into a new directory; no further model search, registration or annual projection is required by this package.
