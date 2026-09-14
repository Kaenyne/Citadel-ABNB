# L3 fee panel — implementation complete, research partial

Lead · 2026-09-13 · codex/lane3-full · all files new. Preregistered in L3_FEE_PREREG_v1.md before execution.

The offline consumer is implemented and its first 13 tests pass. **No theta is estimated**: zero of six scheduled wave captures is available on September 13. The 40% overlap and 95% interval-width <0.58 hurdles are untested, not passed. Investment adoption remains pending; L4 receives explicit nulls rather than a fee overlay.

## What ran

From the isolated worktree root, using `C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe`:

```powershell
python -m pytest analysis/src/forecast_methods/fee_panel_v1/test_fee_panel.py -q
python analysis/src/forecast_methods/fee_panel_v1/run.py --as-of 2026-09-13 --out data/processed/forecast_methods/fee_panel_v1
```

First tests exit 0: 13 passed in 9.38 seconds. First research run exit 0, 7.06 seconds tool wall time. Outputs in `data/processed/forecast_methods/fee_panel_v1/`. The runner rejects an existing output directory; reproduce into a new destination.

## Results and source correction

| Object | n | Result | Interpretation |
|---|---:|---|---|
| Scheduled captures present | 0 / 6 | none | September 14/16/18 and October 12/14/16 are still future |
| Frozen sample frame | 2,600 listings | 1,403 non-EEA; 439 EEA/CH; 758 unknown | Coarse residence proxy, not verified deadline compliance |
| Existing dry run | 225 rows / 207 listings | 6 rows have known residence after frozen-frame join | No assumption that search results track the 2,600 sample |
| Standard fee neutral denominator | 1 conditional identity | log(0.97/0.845) = 0.1379594441 | Theta denominator in log-price regression |
| Mexico/Brazil fee denominator | 1 conditional identity | log(0.97/0.84) = 0.1438941797 | Separate 16% fee regime; old 3% host fee assumed |
| Main harness forecast performance | W1 n=0 / W2 n=0 | unmeasured | No forecast registration |

The earlier A3 note §4 says there are two observations before each deadline and one after. The listed calendar actually provides **one before and two after**. The design cannot establish a pre-trend. A3's suggestion to put unknown residence in the full-sample DiD is superseded here by the user's explicit exclusion from the primary estimate. Neither listing geography nor professional-host status identifies actual migration dates; professionals are reported as a stratum, not known untreated hosts.

The old fee normalizations mix a log-change denominator and arithmetic repricing. This package defines theta solely as a fraction of log payout-neutral repricing. The corresponding price multiplier is `exp(theta * log((1-old_fee)/(1-new_fee)))`; it is not the old linear theta rule. Both neutral denominators and arithmetic neutral changes are exported. No Airbnb-wide revenue uplift follows without migrated revenue shares, guest-fee basis, pricing elasticity and the existing forecast's embedded fee treatment.

## Estimation and failure behavior

Each complete listing/stay is differenced between mean post log price and the one pre log price. Fixed listing/market level differences cancel; common date drift and stay-window differences are controlled. This does not remove market-specific price trends. The treated regressor is residence-defined treatment times its listing fee regime's log neutral reprice. Standard errors cluster by listing across stay windows; 95% intervals use t(G-1). Parameter count is 2 plus the number of observed stay-window dummy columns, normally 3. No parameters are fitted at n=0.

Every observed pre stratum must retain 40% across both post captures before the primary estimate is allowed. Coverage, both pairwise overlaps and the balanced three-date intersection are exported, with pre-set retention denominator and Jaccard as a separate diagnostic. Small or unbalanced treatment/control groups block estimation. A failed gate yields descriptive city/stay/currency median indices; those indices can move with search composition. Even a precision pass is labelled a deadline association, not causal pass-through.

## RESUME

After an already scheduled capture file is supplied, rerun into a new output version with the real information date. For repeated same-day runs select explicit input files rather than silently pooling duplicates. Obtain any further residence/stratum metadata only from sanctioned existing data and record its date. Do not expand scraping or change schedules. September and October cannot be treated as causally equivalent without evidence that the already-treated October comparator has stable pricing. L4 must retain unidentified theta until usable matched data and a reviewed economic basis support replacement of an existing assumption.
