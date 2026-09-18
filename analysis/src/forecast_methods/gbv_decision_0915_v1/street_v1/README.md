# Same-origin DoltHub comparison

Read-only audit of exact quarterly slots, archived proof coverage and two preregistered origin arms. No network, annual-to-quarter allocation, registration or original-file mutation.

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/street_v1/run.py --out data/processed/forecast_methods/gbv_decision_0915_v1/street_v1/source_v1
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/street_v1/run.py --out data/processed/forecast_methods/gbv_decision_0915_v1/street_v1/results_v1 --predictions data/processed/forecast_methods/gbv_decision_0915_v1/horizon_v1/results_v1/predictions.csv
```

Choose a NEW output path on rerun. Company release dates stay fixed. The extra `calendar_minus16` arm uses start(p+2)-16 calendar days as preregistered; model points can be reused only if the frozen calendar shows no intervening company release or guide. Consensus always requires an exact Current/Next Quarter target and snapshot strictly before that arm's date. Annual slots never fill missing quarters. The source-only command performs no forecast performance test.

`origin_consensus.csv` preserves every target-origin and later first-appearance diagnostics, including missing comparisons. `paired_rows.csv` and `paired_metrics.csv` use identical samples per comparison. Revenue consensus is an eventual-revenue expectation. A common cushion yields only an implied-guide proxy. The raw guide-versus-revenue comparison is explicitly different-object. Row-specific historical proof and inherited publisher-date eligibility are separate columns; twelve matching rows at three snapshots do not certify all290snapshot dates. Bootstrap ratios resample target years2000times with seed20260915 and are not live predictive intervals.
