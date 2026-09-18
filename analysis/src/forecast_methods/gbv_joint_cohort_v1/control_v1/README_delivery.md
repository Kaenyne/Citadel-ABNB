# Joint cohort delivery controls — 15 September 2026

All commands run from the `submission-readiness-v1` worktree root. Outputs are additive and commands refuse to replace existing results. Use a fresh output directory when reproducing. The original `register_replay.py` and `visualize.py` are superseded, preserved development versions; use the v2 scripts below.

## Registration and scoring

The executed registration command was:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/gbv_joint_cohort_v1/control_v1/register_replay_v2.py --predictions data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/results_v1/pit_predictions.csv --out data/processed/forecast_methods/gbv_joint_cohort_v1/control_v1/registered_v1 --write
```

This already created `gbv-joint-cohort-v1__primary-guide.csv` and `gbv-joint-cohort-v1__primary-revenue.csv` in the registry. Do not rerun `--write` against these files. For an independent format check, omit `--write` and supply a new `--out`. There are 42 historical point-in-time replay rows: 11 W1 and 10 W2 per target. Overlapping W2 quarters are intentional. Only the primary fitted model is registered; sensitivity, oracle and live diagnostic rows are excluded.

The exact scorer checks were:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/gbv_joint_cohort_v1/control_v1/run.py --out data/processed/forecast_methods/gbv_joint_cohort_v1/control_v1/before_v1
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/gbv_joint_cohort_v1/control_v1/run.py --out data/processed/forecast_methods/gbv_joint_cohort_v1/control_v1/after_v1 --before data/processed/forecast_methods/gbv_joint_cohort_v1/control_v1/before_v1
```

Both frozen scorer implementations returned 0 and agreed on all 292 score rows after registration. All 288 preexisting score rows and 122 original protected files were unchanged. The two new registry files bring the protected inventory to 124. The `after_v1/receipt.json` is authoritative.

**Decision-use limitation:** the frozen scorer's naive lookup does not key by origin date or forecast horizon. Its baseline-relative ratios and pass flags are not admissible for this early-origin method. Use the same-origin fixed-kernel comparisons in `quant_v1/results_v1/pit_scores.csv` and deletion/paired-uncertainty diagnostics. This limitation is documented in `JOINT_COHORT_HARNESS_CHANGE_REQUEST_v1.md`; no frozen code was changed. Registration records a failed research challenger, not approval to replace the live model. Single-replay and W1 warmup-coverage warnings remain visible.

## Visuals

The executed chart command was:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/gbv_joint_cohort_v1/control_v1/visualize_v2.py --results data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/results_v1 --out outputs/gbv-joint-cohort-20260915-v2
```

Both PNGs were visually inspected. SVG equivalents and a source-hash manifest accompany them. The first chart shows conditional identification ranges, not observed cohort histories or confidence intervals. The second shows the historical early-origin guide replay, actual n and the failed deletion gate. Forecast tests use 11/10 origins; retrospective share diagnostics use 14/10 company quarters. These counts must not be substituted for each other.

## Next agent

Read `improvement_0915_theo_joint_results_v1.md` and the final independent review before using any output in a pitch. The current package does not authorize a physical cancellation/RNPL conversion claim, a fixed corporate cohort percentage, a live forecast replacement or a price target.
