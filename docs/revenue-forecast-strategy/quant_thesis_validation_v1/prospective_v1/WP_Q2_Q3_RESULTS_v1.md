# WP-Q2/Q3 — guide forecasts formed before the announcement

2026-09-14 · author source_auditor, wave 2 D · `codex/quant-thesis-validation-v1` · independent reviewer: uncertainty_auditor, wave 3 G · new prospective_v1 directories only.

## Verdict

The preregistered forecasting hurdle **FAILS**. The retained K0 kernel with uniformly reconstructed unprinted GBV improves on revenue-growth persistence plus a common cushion, but it does not beat direct guide-growth persistence in W2 and is not stable to deleting individual calendar years against that comparator. This answers the preannouncement question with a negative promotion result. It does not refute the kernel as a useful benchmark and does not establish a trading edge.

Every forecast originated at the latest QQQ session close on or before target-quarter start minus 18 calendar days. W1 has **12 usable candidate targets of 14**, W2 **10 of 10**, on the all-three comparison intersection. The two missing W1 forecasts are **2023Q1 and 2023Q3**: the exact inherited K0 default ex-COVID rule has no accepted same-season observation at those origins. No fallback estimator was added. Both comparator methods have all 14/10 point forecasts; their own and pair-specific samples are reported separately.

## Frozen protocol and authoritative inputs

Final protocol SHA-256: `dd010ed6d158f1003b9ec55147e16a3f9464010c571b20fe25dad254202cb8ec`. Incorporated proposal SHA-256: `93cb753261d549512d82e11115aa53ca77ecda97f578605fe7a90197db30f4ed`.

All shared inputs are read as Git objects from L3 `8821961853e4068febbfe2712f9a4e1036c9e629`. The only new historical-availability input is source_audit_v1/results_v2/observation_availability.csv, including its conservative 2020Q3 comparative-source date. The exact K0 engine and frozen harness naive public API are hash-checked and called with already filtered observations. No future GBV is inserted into the training panel. No target guide, consensus, fee, FX, RNPL, ADR or alternative-data multiplier enters this empirical forecast.

An unprinted GBV lag is forecast using its observed year-ago level times the latest observed GBV year-over-year ratio. The median of at most eight realized actual/guide ratios, with a three-observation minimum, converts revenue into a guide. B1 applies the same year-over-year persistence logic directly to previously issued guides. B2 uses the frozen revenue-naive point divided by the identical candidate cushion statistic. The exact K0 variant selection is re-run using the origin's panel, including its existing sparse-data default and retrospective model-selection policy.

The panel is a **frozen retrospective reconstruction, not a recovered archive of original unrevised vintages or historical forecasts**. Earlier research has already seen these quarters. This protocol controls new implementation flexibility and information timing; it does not create an untouched external holdout. The historical source-date correction predates every evaluated W1 origin. Date-only sources become eligible only after their full local publication day; the selected mid-month session anchors have regular 16:00 ET closes.

## Exact commands and run history

From `C:/Users/wille/Desktop/Citadel - ABNB/.worktrees/quant-thesis-validation-v1`:

```powershell
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/prospective_v1/run.py --stage forecast --out data/processed/forecast_methods/quant_thesis_validation_v1/prospective_v1/forecast_v1
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/prospective_v1/test_prospective.py
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/prospective_v1/run.py --out data/processed/forecast_methods/quant_thesis_validation_v1/prospective_v1/results_v1
```

The point-only first stage exited 0 (8.5 seconds). The first adversarial test run passed 12 of 13 tests and identified an empty-history boolean-mask bug in interval calibration. This was repaired **before evaluation**; a harmless frame-fragmentation warning was removed by selecting only the four required input columns. The unchanged point forecasts were then rebuilt and hash-frozen in the canonical complete run. Final tests: **13/13 pass**, 2.6 seconds wall time. Complete run: exit 0, 4.1 seconds wall time. There was one empirical specification and no post-result method selection or hurdle change. Both the preliminary point-only output and completed run remain preserved.

The canonical complete run writes 63 method rows across 21 target origins, 2021Q4–2026Q4, plus all used data/training/cushion/GBV traces. Its forecast freeze is physically written before the outcome join. Forecast-freeze SHA-256: `f305a65ad356a06c6f73f433347aa84f78b302c00905fc51de2416efe1d52823`. Final run.py SHA-256: `9c583df337902d33a242a0e1bafdfdd749d4468ccb7eb8548da330e1afbabdac`.

System fitted-statistic accounting: candidate 5 (four seasonal lambda coefficients across the system plus one median cushion statistic), B1 zero, B2 one shared cushion statistic. Fixed lag weight and GBV persistence add zero fitted coefficients. Existing K0 model selection remains part of the method and is not concealed by this parameter count. Per-origin lambda and cushion sample counts are exported.

## Matched forecast losses

USD millions. Interval-fair errors use the project midpoint ±0.5m scoring convention. This is an administrative loss convention for nominal management guidance, not a measured economic-precision band and not the full management range. Raw errors are always retained.

| Window | n | Method | Interval RMSE | Interval MAE | Signed bias | Raw RMSE |
|---|---:|---|---:|---:|---:|---:|
| W1 | 12 | Candidate K0/GBV | 63.445 | 52.134 | −7.180 | 63.856 |
| W1 | 12 | B1 guide-growth | 74.331 | 64.064 | +15.048 | 74.762 |
| W1 | 12 | B2 revenue-naive/cushion | 117.309 | 95.518 | +3.934 | 117.717 |
| W2 | 10 | Candidate K0/GBV | 63.696 | 51.221 | −3.514 | 64.099 |
| W2 | 10 | B1 guide-growth | 60.834 | 57.226 | −1.593 | 61.305 |
| W2 | 10 | B2 revenue-naive/cushion | 121.926 | 99.790 | −10.111 | 122.335 |

Candidate/B1 interval-RMSE ratios are **0.85355 W1 / 1.04704 W2**; candidate/B2 **0.54083 / 0.52242**. MAE is lower than both comparators in both matched windows, but the frozen hurdle required lower RMSE against both, plus year stability. The lower MAE cannot rescue the failed primary criterion.

All coverage floors pass: 12/10 ≥8/6, all four seasons, four/three target calendar years. W2 is nested in W1. Deleting 2023 from W1 reproduces the W2 loss and removes candidate superiority against B1; deleting 2024 or 2026 from W2 also leaves the candidate with higher B1-comparison MSE. All year deletions remain favorable against B2. Year and season slices are descriptive and do not alter the verdict.

## What produces guide error

The seven exact terms U, C, P, UC, UP, CP and UCP reconcile raw guide error; ROUND converts the identity to interval-fair error. U is the upstream GBV main term, C conversion and P guide-policy, using eventual actual identities only in evaluation. Their interpretation is accounting, not identified causal shocks. The ordered simpler bridge is also exported and labeled as an order-dependent allocation of interactions.

| Window | n | Mean U, USDm | Mean C, USDm | Mean P, USDm | Interval MSE, USDm² |
|---|---:|---:|---:|---:|---:|
| W1 | 12 | −6.772 | +8.951 | −8.709 | 4,025.227 |
| W2 | 10 | −3.474 | +11.144 | −10.324 | 4,057.205 |

Every term's first and second moment, all 28 pair cross moments and population-denominator covariances are retained. The full second-moment-plus-cross-term identity matches MSE within **4.3e−10 USDm²**. Main-term second moments do not sum to total MSE because cross terms are material; no independence or quadrature assumption was used. Measurement precision and specification error can sit within the conversion term, which cannot thereby be labeled FX or RNPL.

## Chronological descriptive bands

Calibration uses only previous forecasts made under this same origin protocol whose target guide was issued before the new origin, last eight errors maximum, six minimum. It uses raw relative guide errors and the fixed 80% order-statistic rule. No K0 post-letter error or future target enters calibration.

| Window | Method | Usable bands n | Raw midpoint coverage |
|---|---|---:|---:|
| W1/W2 | Candidate | 6 / 6 | 6/6 in each nested set |
| W1/W2 | B1 | 8 / 8 | 7/8 |
| W1/W2 | B2 | 9 / 9 | 8/9 |

These are small, overlapping historical samples, not evidence of a guaranteed 80% prediction probability. Missing bands remain missing. Full raw-midpoint, target-interval overlap and target-interval containment coverage, calibration dates and widths are exported; the three coverage definitions coincide in this particular run.

The separately labeled **reconstructed September 11, 2026 origin** for Q4 produces candidate revenue **3,219.235470m** and guide **3,162.609235m**, with reconstructed Q3 GBV **26,505.531915m**; B1 guide **3,133.916256m**, B2 guide **3,180.464914m**. This is not an archived September 11 forecast or an L4 production replacement. The candidate's eight-error descriptive band is **3,066.814429–3,258.404042m**. The 55-day lead is measured to the project's assumed November 5 event, not a newly verified current issuer schedule. The later September 13 consensus observation is outside this origin and is not joined or used to claim a surprise sign.

## Output map, failures and limitations

Under `data/processed/forecast_methods/quant_thesis_validation_v1/prospective_v1/results_v1/forecast/`: `predictions.csv`, `panel_inputs.csv`, `guide_inputs.csv`, `cushion_inputs.csv`, `lambda_training.csv`, `gbv_inputs.csv`, `exclusions.csv`, `input_manifest.json`, `forecast_freeze.json`.

Under `evaluation/`: per-date `errors.csv`; matched/own/pair `scores.csv`; `paired_errors.csv`; `year_deletion.csv`; `year_season_slices.csv`; `coverage.csv`; `contributions.csv`; `contribution_cross_moments.csv`; `mse_reconciliation.csv`; `prediction_bands.csv`; `calibration_inputs.csv`; `band_coverage.csv`; `hurdle_checks.csv`; `verdict.json`; `evaluation_receipt.json`. The root `attempt_ledger.json` records the one evaluated specification and stage ordering.

Adversarial tests cover poisoning future GBV/revenue/target-guide/cushion values; missing/duplicate publication dates; same-day source refusal; missing-lag reconstruction without training contamination; rejection of already-issued target guidance; first-guide selection in the presence of later revisions; abstention when a seasonal anchor is removed; session rollback/stale calendar; administrative midpoint-interval loss versus the full range; live missing outcomes; all-three/pair matching; chronological residual availability; and immutable-output refusal. Target consensus is never read into forecasting.

No compliant shared-harness registration exists for this experiment's actual historical origins and target-specific guide availability. Formats 1.0/1.1 require historical guide-date vintages and have different scoring semantics. No vintage is relabeled and no shared registry or scorer file changes. A reviewed extension would need real origin timestamps, first-guide availability and explicit loss conventions; no extension is needed to complete this local research finding.

The main empirical failure is versus the direct guide comparator, not data coverage or implementation completion. Sparse K0 seasonal observations, source-vintage limitations, inherited retrospective variant selection and unmodeled structural changes limit generalization. The first guide's policy choices are not independent of management's bookings information. Lower forecast loss against one comparator alone does not identify recognition weights, RNPL leakage, consensus revision or stock return.

## RESUME

Wave 3 G should independently reconstruct origins, information membership, exact K0 policy, missing GBV, median cushion, both baselines, scoring, interactions and chronological calibration from the immutable source objects; compare against results_v1 and verify the preliminary point-only ledger matches canonical point fields. Parent should retain FAIL and the 12/10 sample, integrate economic materiality on consistent forecast/consensus dates, and prohibit production or trading promotion. Any review repair must preserve original outputs in a new version. Author now rotates to adversarial economic/presentation review after reviewer handoff.
