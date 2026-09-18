# GD guide interval sensitivity — unchanged decision

15 September 2026. Preregistered in `GD_GUIDE_INTERVAL_PREREG_v1.md` before interval calculation. Accepted additive output: `data/processed/forecast_methods/gbv_decision_0915_v1/interval_v1/results_v1/`.

**Scoring integer-letter rounding correctly does not change any tested gate.** All16 promotion rows and every component flag agree with their raw-midpoint counterparts. The favorable fixed p+4 result on the restricted common9 sample remains favorable. Joint fails all three horizons, and neither candidate passes on its standalone eligible history. Both calendar-flight remedy candidates still fail. Retain GBV as a forecasting/scenario challenger; this sensitivity adds no evidence of an established guide or Street edge.

## What changed in the local calculation

Each saved point is scored by signed distance to `[issued midpoint−0.5, issued midpoint+0.5]` USD million. This bounds integer rounding of the two published guide endpoints. It is neither the full company guide range nor a probability interval. Raw saved points remain untouched. Both candidates and references receive the same interval treatment.

The original W1/W2 samples, paired 2,000 target-year cluster draws, all target-year and target-quarter deletions and original promotion thresholds are unchanged. Common4 requires joint, fixed and the two simple baselines; standalone eligibility requires each candidate and both simple baselines. Longer-horizon common W1/W2 samples overlap completely, so these are not independent replications. The flight test retains its own preregistered remedy gate rather than acquiring the stricter horizon CI requirement.

## Decision-relevant results

Ratios below1 favor the candidate. Confidence intervals are paired historical 90% year-cluster ratio intervals with only a few distinct years, not future-guide ranges.

| Comparison | Window; n | Raw ratio | Interval ratio | Interval 90% ratio bounds | Gate effect |
|---|---|---:|---:|---|---|
| Joint p+2 / direct guide growth, common4 | W1;11 |1.0885|1.0910|0.7433–1.5274|Fail unchanged|
| Joint p+2 / direct guide growth, common4 | W2;10 |1.0412|1.0436|0.7134–1.3099|Fail unchanged|
| Joint p+3 / direct guide growth, common4 | W1/W2 same10 |0.9561|0.9551|0.8265–1.2986|Fail unchanged|
| Joint p+4 / direct guide growth, common4 | W1/W2 same9 |0.9923|0.9925|0.6509–1.2158|Fail unchanged|
| Fixed p+4 / direct guide growth, common4 | W1/W2 same9 |0.8889|0.8885|0.7720–0.9795|Restricted pass unchanged|
| Fixed p+4 / direct guide growth, standalone | W1;12 |1.1005|1.1010|0.8501–1.2943|Fail unchanged|
| Fixed p+4 / direct guide growth, standalone | W2;10 |0.9098|0.9094|0.8224–0.9795|Magnitude fail unchanged|

For the common next-guide W2 sample, interval RMSE is63.49m for joint,76.62m for fixed and60.83m for direct guide growth (raw63.83m,77.01m and61.31m). For the favorable restricted fixed p+4 sample, interval RMSE117.32m compares with direct guide growth132.05m; on the broader fixed-eligible W1 sample it is158.72m versus144.16m. The substantive sensitivity is sample eligibility, not a half-million-dollar rounding allowance.

The calendar-flight interval test has the same9 targets in W1/W2. Joint-flight/no-flight RMSE ratio is1.1973 (raw1.1964), and fixed-flight/no-flight is0.9600 (raw0.9603). Against direct guide growth, interval ratios are1.2680 and1.1942. Both remedy gates remain failed in both windows. `comparisons.csv` retains each window's original RNG progression and individual ratio intervals.

## Integrity, commands and limitations

The new package estimates zero parameters and imports no forecasting function. Existing joint/fixed/direct/revenue model counts and their unchanged predictions remain documented in `GD_HORIZON_RESULTS_v1.md`; this is a scoring sensitivity only. Eight edge checks pass;394 source-statistic and gate replication checks reproduce the original raw comparisons. All11 input hashes remain unchanged. Both commands exit0 and all7 output files, including the manifest, rebuild byte-for-byte:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/interval_v1/run.py --out data/processed/forecast_methods/gbv_decision_0915_v1/interval_v1/results_v1
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/interval_v1/run.py --out data/processed/forecast_methods/gbv_decision_0915_v1/interval_v1/rebuild_v1
```

No registry, live forecast, chart label or frozen scorer changes. Actual inspection found the frozen v1/v1.1 scorers use raw `point−midpoint` errors. The separate `GD_GUIDE_INTERVAL_HCR_v1.md` requests a versioned correction; we do not claim the frozen scorers already satisfy the interval rule. Reused historical samples, few years and incomplete direct cohort/Street evidence remain the governing limits.

## RESUME

Parent can close integer-rounding sensitivity with the unchanged-gates receipt and retain existing raw chart labels. The independent reviewer should verify saved interval arithmetic and key gates. Keep the restricted common9 positive fixed finding alongside its failed broader eligibility check; do not turn either into an unconditional forecast promotion. The harness HCR remains open for a separately claimed, versioned implementation.
