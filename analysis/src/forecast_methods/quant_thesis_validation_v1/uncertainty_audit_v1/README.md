# Bounded uncertainty audit

This package reads the immutable L3 bundle at commit `8821961853e4068febbfe2712f9a4e1036c9e629`, the frozen KPI panel and legacy QVS/K1/K2 notes. It reproduces descriptive arithmetic, saved chronological point/error scores and saved parameter/paired percentile summaries. It performs no model fit, lag-weight search, new bootstrap, forecast registration or operational change.

Run from the assigned quant worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 'analysis/src/forecast_methods/quant_thesis_validation_v1/uncertainty_audit_v1/run.py' --out 'data/processed/forecast_methods/quant_thesis_validation_v1/uncertainty_audit_v1/results_v2'
```

`results_v1` is the completed initial calculation; choose a new version for each run. The runner refuses existing destinations, another package's destination, a changed baseline commit, changed bundle identity, mismatched source lags or materially different accepted score/percentile arithmetic. NumPy and pandas are required. The environment emits DataFrame fragmentation performance warnings because the frozen KPI panel is wide; the 24-row calculation completes correctly. No source change is needed for this harmless warning.

Units: revenue and GBV are USD millions; `a_pp` and `lambda_pct` are percentage levels, so their standard deviations are percentage points and variances are percentage points squared. `pooled_within_season_sd` divides season-demeaned sums of squares by n minus the number of observed seasons. Calendar-year deletions are descriptive. Score errors use forecast minus actual.

`joint_parameter_compensation.csv` preserves each accepted `(w, lambda_Q1, ..., lambda_Q4)` row. For season s, it fixes `r_s` to the all22 historical mean `G1/G2` for that season, then calculates `k_s=lambda_s*(1+w*(r_s-1))`. It decomposes the exact product around the draw means into lambda, w and their interaction; covariance is computed between the two linear terms. This is a descriptive research diagnostic from six calendar-year blocks. It is not a distribution for the retained operational kernel. No shuffled or independent marginal scenarios are generated.

Embedded checks reconcile 22 lags/revenue values, 12 primary score metrics, accepted paired error deltas, five parameter percentile triplets, four paired percentile triplets, exact joint-product algebra, and minimal revenue/guide arithmetic. An independent reviewer should inspect the output CSVs and reproduce the main formulas without calling this implementation.

The companion note is `docs/revenue-forecast-strategy/quant_thesis_validation_v1/uncertainty_audit_v1/UNCERTAINTY_AUDIT_v1.md`.

## RESUME

Wave 1 Q4 is complete for lead review. Keep the baseline, input hashes and output versions immutable. The next worker should use the operational stress equations from the note, use only adopted operational parameters, and independently reproduce the prospective implementation once its frozen protocol and outputs exist. No scorer run is required without registrations.
