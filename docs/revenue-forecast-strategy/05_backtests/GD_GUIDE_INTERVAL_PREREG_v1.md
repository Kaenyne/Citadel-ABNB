# GD guide integer-letter interval sensitivity — preregistration

15 September 2026. Additive, frozen-point sensitivity; no model fits, feature changes, source-prediction changes or registry changes. The prior raw-midpoint results remain canonical raw comparisons and retain their chart labels.

## Scope and frozen convention

Before calculating interval results, freeze each actual first-issued guide midpoint's measurement interval to `[midpoint - 0.5, midpoint + 0.5]` USD millions. Each reported guide endpoint has integer-dollar-million rounding uncertainty of ±0.5; the midpoint of two such endpoints has the same worst-case ±0.5 bound. This is rounding uncertainty, not the company's full guide range or predictive uncertainty. The signed scoring residual is `sign(prediction-midpoint) * max(abs(prediction-midpoint)-0.5, 0)`. Points inside or on the interval have zero distance.

Read accepted horizon `results_v2/predictions.csv` only. Cover all p+2, p+3 and p+4 horizons in W1 (2023Q1+) and W2 (2024Q1+), excluding live rows. Compute the four-production-model intersection and, separately, candidate-specific intersections of joint/fixed with both simple baselines. Keep the exact raw samples, paired target-year cluster bootstrap seeds/draws (2,000 draws, 90% interval), target-year and target-quarter deletions, thresholds and coverage rules. Paired raw and interval statistics use identical draws. Main comparisons concern the joint/fixed candidates against fixed, direct guide growth and revenue growth; self-comparisons are omitted. No oracle interval promotion test is needed.

The horizon gate remains n≥8 in each window, RMSE ratio≤0.90 against both simple baselines in both windows, every deletion ratio<1, and the paired 90% ratio upper limit<1 against direct guide growth in both windows. Retain the existing common-sample versus standalone eligibility distinction and report overlap of W1/W2 samples.

Also read the parent's saved calendar-flight `results_v1/predictions.csv`, with unchanged model order, samples, seed and pair-by-pair RNG progression. Recalculate the same comparisons, 2,000 year-cluster intervals and year/quarter deletions. Retain its distinct remedy gate: n≥8, ≥10% improvement over the matching no-flight model, no deletion reversal against that model, and point RMSE better than direct guide growth, in each window. This does not add a new CI gate to that preregistered test.

## Validation and interpretation

Reproduce the existing raw statistics/gates before accepting the interval output; compare all gate outcomes side by side. Test points inside, on and outside the rounding interval, sign, zero-width equivalence to raw errors and covariance-free paired loss arithmetic. Rebuild deterministically to a new directory and verify input hashes unchanged. Empty or zero-baseline samples must be identified, not silently treated as wins. Sampling uncertainty, rounding sensitivity and predictive uncertainty remain separate.

Inspection of both frozen harness scorers shows raw `err = p - y` and raw RMSE/MAE, despite the repository's interval-scoring rule. Record a separate HCR requesting an additive versioned scoring change. Do not edit the frozen harness or describe its current output as interval scored. This local audit changes no registered score.

## RESUME

Run the new `gbv_decision_0915_v1/interval_v1/run.py` against saved points, preserve raw/interval comparisons and report whether the decision changes. Parent owns any registry/scorer action and final synthesis; a future harness maintainer should resolve the separate interval HCR with versioned compatibility tests.
