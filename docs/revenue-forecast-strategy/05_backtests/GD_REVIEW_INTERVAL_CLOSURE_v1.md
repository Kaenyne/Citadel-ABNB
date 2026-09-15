# GD-REVIEW final interval closure

15 September 2026. Independent reviewer: chart_auditor. Completes the rounding-convention item left pending in `GD_REVIEW_RESULTS_v2.md`. Read this closure with that corrected main review; it supersedes the pending status and the original v1 implication that the frozen scorer was interval-based. No existing note, source, forecast, registry or scorer was edited by the reviewer.

**PASS. The rounding check changes no gate component or promotion outcome. The decision remains: retain GBV conversion as a supporting forecast/scenario tool; neither broad guide superiority nor the current short thesis is established.**

The preregistered measurement interval is the issued-guide midpoint ±$0.5M. This is an integer-rounding bound, not management's full guide range or a predictive confidence interval. The reviewer independently calculated signed distance by projection:

`distance = prediction − clip(prediction, actual_midpoint − 0.5, actual_midpoint + 0.5)`.

This agrees with the author's signed dead-zone formula, including points inside, on and just outside either bound. Zero width reproduces raw residuals; negative/nonfinite widths and nonfinite input errors are rejected. Frozen `harness/score.py` and `harness_v1_1/score.py` still use raw midpoint errors. The required convention is addressed by this additive sensitivity and `GD_GUIDE_INTERVAL_HCR_v1.md`, which remains a future versioned harness request. No frozen code was changed.

The independent saved-output replay verifies the exact original common-four and candidate-specific samples at all three horizons, the calendar-flight samples, all raw/interval scores, raw matches to previous output, exact paired year-cluster bootstrap progression, every deletion and each gate component. All16 paired promotion rows and their component flags are unchanged. Examples:

| Scope | Interval result | Interpretation |
|---|---|---|
| Fixed p+4, nine common rows, identical W1/W2 | Guide-growth ratio0.888513; 90% interval[0.772025,0.979507] | Restricted common-sample PASS retained |
| Fixed p+4, standalone W1 n12 / W2 n10 | Guide-growth ratios1.100956 /0.909360 | Broad promotion still FAIL |
| Joint, common and standalone horizons | All gates remain FAIL | No promotion created by rounding |
| Calendar-flight remedies, both windows | Both models remain FAIL | Earlier remedy verdict retained |

Two distinct independent reviewer suites passed: **6,154 saved-source/arithmetic/statistical/gate checks** and **13 actual-code edge checks**. These overlap the earlier economic objects and are not additional quarters or an independent holdout. The author's394 raw replication checks,8 edge checks and deterministic two-build verification are separate suites; do not sum them into one scientific sample size.

Canonical interval data: `data/processed/forecast_methods/gbv_decision_0915_v1/interval_v1/results_v1/`. Its manifest SHA256 is `3c0ab087c76bdbdfb36b326607d03a7e58beac1e7d00b941d43f980f2eff7abf`. Reviewer source: `analysis/src/forecast_methods/gbv_decision_0915_v1/review_v1/interval_checks.py`, SHA256 `549010cf83aa26f7a90e2bb19d7ec981fe40a0aecff04629dae772778fbc6a14`. Reviewer receipt/checks: `data/processed/forecast_methods/gbv_decision_0915_v1/review_v1/interval_v1/`. The statistical replay imports no author scoring code; a separate tiny edge-test section deliberately exercises the actual interval function. No model was fitted.

Reproduce from the worktree root into a NEW output directory:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' 'analysis/src/forecast_methods/gbv_decision_0915_v1/review_v1/interval_checks.py' --out 'data/processed/forecast_methods/gbv_decision_0915_v1/review_v1/interval_replay_v2'
```

The high-level narrative in the parent's `GD_DECISION_REPORT_v1.md` was also read against the reviewed numeric evidence. No actionable content issue was found. The reviewer did not independently render the visual pack; the parent owns that visual QA. Parent reports both frozen scorers completed with328 rows and the prior292 scores/126 protected files unchanged; those preservation checks are separate from this interval receipt.

## RESUME

GD-REVIEW and its final interval follow-up are complete with no unresolved numerical blocker. Use `GD_REVIEW_RESULTS_v2.md` together with this closure and the parent's completion report. Keep the favorable conditional revenue comparison, the restricted fixed-model pass, the broader-eligibility failure and source limitations visible. The remaining harness change request is maintenance work; it does not change today's reviewed decision or require additional model fitting before the Excel decision worksheet and supported two-page draft.
