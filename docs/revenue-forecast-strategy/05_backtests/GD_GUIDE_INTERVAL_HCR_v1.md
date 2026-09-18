# HCR — versioned integer-letter interval scoring

15 September 2026. Status: OPEN; research discrepancy documented, frozen harness untouched.

## Concrete discrepancy

The repository rule says letter integers are scored as ±0.5 intervals. Actual inspection finds `err = p - y` in `analysis/src/forecast_methods/harness/score.py:81` and `analysis/src/forecast_methods/harness_v1_1/score.py:82`; the following lines compute raw MAE, RMSE and bias. This is raw-midpoint scoring. A nearby distribution/fallback path also measures distance to the midpoint. The source predictions are not at fault. No existing registered output should be retroactively described as interval scored.

For a guide whose two published endpoints are integer USD millions, their midpoint has a worst-case rounding interval of midpoint ±0.5 USD million. A point forecast 0.3m above that midpoint has raw absolute error 0.3m and interval distance zero. A forecast 2m below has raw error −2m and signed interval distance −1.5m. This local convention is distinct from measuring distance to the entire management guidance range.

## Requested bounded change

Have the harness maintainer add a versioned scoring path with explicit measurement-interval metadata and both raw and interval point metrics. Apply the same rounding convention to candidates and baselines when computing relative point-loss statistics. Preserve raw compatibility output and never overwrite existing frozen scorer/results. Specify separately which sources and output objects carry integer rounding and how missing/noninteger observations behave; do not indiscriminately assign the guide convention to all objects.

This request does not silently redefine CRPS, probabilistic calibration, predictive bands, model registration dates or origin eligibility. If interval-censored distribution scoring is desired, preregister that separate definition and its tests before implementation. The current local work tests guide point loss only.

## Acceptance checks and present effect

Require within-interval, boundary, signed outside-interval, zero-width raw equivalence, units, candidate/baseline symmetry and zero-baseline-loss handling tests. Reproduce existing raw results exactly within numerical tolerance; record intentional interval differences as a new score version. Bind input hashes and demonstrate deterministic rebuild.

The additive local audit in `gbv_decision_0915_v1/interval_v1/results_v1` recalculates all three guide horizons on both common4 and standalone candidate eligibility, and the parent's calendar-flight guide test. It uses the original samples, 2,000 paired year-cluster draws, deletion rules and gates. Zero gate components and zero promotion outcomes change. This closes the current decision's sensitivity to integer rounding, but it does not resolve the general harness discrepancy or establish the forecasting edge.

## RESUME

Parent should reference raw registered scorer results honestly and the separate local interval receipt for this decision. A future harness maintainer should claim this HCR and implement a new version only after agreeing object-specific interval metadata and compatibility tests. Do not edit the frozen scorer or reclassify current registered metrics as interval based.
