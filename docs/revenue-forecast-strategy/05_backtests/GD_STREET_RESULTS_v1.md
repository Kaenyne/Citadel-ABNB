# GD-STREET — same-origin revenue consensus and the guide-expectations boundary

Codex data subagent · 15 September 2026 · branch `codex/submission-readiness-v1`. Claimed in `WORKBOARD_GBV_DECISION_0915_v1.md`; calendar-origin arm preregistered in `GD_CALENDAR_ORIGIN_ADDENDUM_v1.md` before its performance test. All work is additive under `gbv_decision_0915_v1/street_v1/`.

## Verdict

**Conditional positive evidence for the joint model's next-quarter total-revenue forecast; no demonstrated superiority on the guide objective over the simple direct-guide-growth baseline.** At the fixed between-prints information date, the joint model's eventual-revenue RMSE is substantially below the held DoltHub revenue consensus in both windows, including matched-sample bootstrap and deletion checks. This favorable finding survives and must not be discarded because physical booking cohorts are unidentified. However, the selected historical publisher-date snapshots lack row-specific archival proof, the two windows largely overlap, and the guide comparison uses an assumed cushion proxy rather than measured market expectations for management's guide. Those limits prevent a certified guide-surprise or trading-edge claim.

The initial release-day comparison has zero quarterly Street coverage at every requested horizon. The preregistered calendar-date arm repairs that mismatch for the next guide only. Two and three future guide announcements still lack exact quarterly consensus observations; annual consensus is not allocated into quarters.

## Source audit and timestamp interpretation

The explicit source is **DoltHub post-no-preference/earnings**, read from the held `sales_estimate_ABNB_BKNG_EXPE.csv`. There are 1,160 ABNB rows, 290 publisher snapshot dates and four slots per date. Only the 580 Current/Next Quarter rows can map to quarterly targets. One quarterly row has missing consensus and is excluded; all 579 eligible quarterly dollar values reconcile to the inherited processed weekly panel. No other vendor, press quote, annual estimate or later snapshot fills a hole.

G1b's retained second provenance attempt independently reproduces: all four numeric fields in all twelve rows at three snapshots equal the values stored at their specific historical commits. That is useful evidence for those three snapshots. It does **not** demonstrate that all 290 snapshots are immutable or that their values were public on the publisher's stamped calendar date. The three known sales-estimate commits occurred the following day: snapshots 7 August 2022, 11 February 2024 and 3 August 2025 were committed on 8 August, 12 February and 4 August respectively. Raw SQL datetime strings do not encode a timezone. The earliest snapshots predate the repository's creation and were initially backfilled; they are not treated as independently git-dated originals.

None of the fourteen snapshots selected for the new calendar-origin comparison is one of those three historically checked snapshots. Every reported performance number below is therefore an **inherited publisher-date snapshot diagnostic**. Row-specific archival-certified comparison coverage is zero. This does not establish that the selected values leaked or were revised; it accurately states what is unverified. Three selected snapshots are only one calendar day before the origin, which makes actual commit time particularly material.

A bounded public `web__run` request attempted one batched G1b-style commit-log query for all fourteen selected dates. The tool returned an internal error and rejected the URL as non-retryable; zero commit/AS OF rows were received. No retry, credentials or access workaround followed. Exact request and failure receipt: `street_v1/public_fetch_attempt_v1.json`. Historical provenance remains conditional.

## Origins and coverage

The original arm is immediately after the company release for last-reported quarter p, using only publisher snapshots strictly before that calendar date. The extra arm is **start(p+2) minus 16 calendar days**, independently preregistered before its performance test. For today's p=2026Q2, that is 15 September 2026. The offset was not searched or optimized.

All seventeen origin groups have identical company actuals and issued guides between the original release and the later calendar date. The data package independently checks no intervening published company result or guide. It then binds all **153** historical calendar/model comparison rows to the quant's separate `calendar_arm_v1/predictions.csv`; guide, revenue, cushion and outcome cells agree. No new model fitting was required for the date shift. The quant's original oracle rows are excluded from every Street comparison.

| Arm / target | W1 origins / quarterly consensus | W2 origins / quarterly consensus | Interpretation |
|---|---:|---:|---|
| Release day, p+2 | 14 / 0 | 10 / 0 | Quarterly slots had not rolled to the target |
| Release day, p+3 | 14 / 0 | 10 / 0 | Exact quarterly target absent |
| Release day, p+4 | 14 / 0 | 10 / 0 | Exact quarterly target absent |
| Calendar minus 16 days, p+2 | 14 / 14 | 10 / 10 | Latest publisher snapshots are 1–7 days old |
| Calendar minus 16 days, p+3 | 14 / 0 | 10 / 0 | Annual values do not repair quarterly coverage |
| Calendar minus 16 days, p+4 | 14 / 0 | 10 / 0 | Annual values do not repair quarterly coverage |

W1 targets are 2023Q1–2026Q2; W2 starts 2024Q1. All 84 arm/target/origin rows remain in `origin_consensus.csv`, including missing values and later first-appearance dates clearly labelled diagnostic-only. For example, the Q4 2025 quarterly consensus first appears on 10 August 2025, after the original Q2 release origin of 6 August. It may enter the fixed September calendar arm, never the original August forecast.

## Comparable performance, next guide only

The following table uses the **same eleven W1 and ten W2 target quarters for every displayed model and Street**, the common intersection across joint, fixed and both simple baselines. The joint model lacks three early W1 points. Own-coverage results, including the fixed model's full fourteen W1 forecasts, remain separately in `results_v3/paired_metrics.csv`; do not rank those different samples as if matched.

All values are USD millions. Revenue errors compare eventual revenue with eventual revenue. Guide errors compare the issued guide with model guide and the explicitly assumed Street implied-guide proxy.

| Forecast / benchmark | Revenue RMSE W1, n=11 | Revenue RMSE W2, n=10 | Guide RMSE W1, n=11 | Guide RMSE W2, n=10 |
|---|---:|---:|---:|---:|
| Joint GBV model | **57.443** | **56.231** | 64.287 | 63.831 |
| Fixed GBV kernel | 78.236 | 80.951 | 74.592 | 77.012 |
| Direct guide-growth baseline | 83.635 | 87.147 | **59.063** | **61.305** |
| Revenue-growth baseline | 126.684 | 132.582 | 118.691 | 124.249 |
| DoltHub revenue / common-cushion guide proxy | 89.916 | 92.504 | 86.491 | 88.798 |

The direct-guide baseline's revenue value is itself guide times the common cushion, not a separately sourced revenue forecast. Its guide performance is the relevant simple benchmark for the user's objective. Common rows span four target years in W1 and three in W2, with partial years at the ends. The windows overlap and are not independent replications or pristine holdouts.

### Joint model versus the explicit DoltHub series

| Object, common n=11 / 10 | W1 RMSE ratio | W1 paired year-bootstrap 90% range | W2 RMSE ratio | W2 paired year-bootstrap 90% range |
|---|---:|---:|---:|---:|
| Eventual revenue | 0.639 | 0.528–0.888 | 0.608 | 0.508–0.767 |
| Issued guide versus common-cushion proxy | 0.743 | 0.548–1.075 | 0.719 | 0.542–0.991 |

The revenue advantage survives every individual target-quarter and target-year deletion: the largest retained-sample joint/Street RMSE ratio is 0.769 in W1 and 0.725 in W2. The guide-proxy advantage also remains below one under these individual deletions, but its W1 bootstrap interval crosses one. Each bootstrap resamples target-year clusters 2,000 times with fixed seed 20260915. These are uncertainty diagnostics on a very small historical sample, not live predictive intervals or proof of an executable trade.

For the **raw different-object** guide-versus-eventual-revenue comparison, joint/Street RMSE ratios are 0.958 and 0.908, and both year-bootstrap intervals cross one. This is deliberately preserved because the cushion convention materially changes the result. A revenue consensus is not intended to predict the issued guide; raw guide error against it cannot be presented as the Street missing its own forecast objective.

### Direction is a separate question from loss size

Against the common-cushion guide proxy, the joint predicted gap has the right sign on 8/11 W1 cases and 8/10 W2 cases. The realized adjusted gap is positive in 9/11 and 8/10 cases, respectively. An always-positive majority prediction would therefore achieve 81.8% and 80.0%, versus the model's 72.7% and 80.0%. These results do not establish incremental sign forecasting. No threshold was tuned and zero remains its own class. All raw/adjusted sign cells are in `sensitivity_v1/sign_confusion.csv`; no stock returns or new trading strategy were tested here.

## What the present Q4 comparison actually says

At the actual 15 September 2026 information date, the held 13 September DoltHub snapshot does contain Q4 2026 eventual-revenue consensus: **$3,200m, ten analysts**. The retained commit-log head identifies its sales-estimate update on 14 September; this is current held-source evidence, not a direct guide-expectation survey. Quarterly Q1/Q2 2027 values remain absent.

Using the already reviewed 15 September common-input points and the same 1.856743% arithmetic-mean cushion:

| Q4 comparison | Joint | Fixed |
|---|---:|---:|
| Model revenue | 3,244.389 | 3,219.235 |
| Model guide | 3,185.247 | 3,160.552 |
| Model guide minus **revenue** consensus | −14.753 | −39.448 |
| Model guide minus **common-cushion implied-guide proxy** | +43.580 | +18.885 |
| Common-cushion relative gap | +1.387% | +0.601% |

The implied-guide proxy is $3,141.667m. The shared cushion cancels from relative model/Street comparisons, so the positive adjusted gap is simply the positive model-revenue disagreement restated. Choosing the raw negative comparison cannot establish a short thesis, and choosing the adjusted positive comparison cannot establish a long thesis. Neither is a measured expectation for what management will guide, and neither maps directly to a stock return.

## Targeted data gaps and practical remedies

The machine-readable eight-row map is `street_v1/targeted_gap_map_v1.csv`. It reuses the prior twenty-three-source schema audit rather than recrawling the catalogue.

1. **Unknown GBV:** the PR 60 EUROCONTROL QTD75 series is a real dated demand feature. The old release-origin ablation failed on eight identical-window cases and should remain visible. At today's September calendar date, Q3's reading is actually available, so a newly preregistered fixed-calendar ablation is a different, relevant information set; the parent owns it. Historical commit delays vary and must be applied row by row. Original raw forty-state/day completeness is not locally recertified.
2. **Street timing:** recover commit and AS OF records for the fourteen exact selected snapshots before certifying the inherited comparison. For Q1/Q2 beyond the held quarterly slots, obtain archived exact-quarter estimates with actual timestamps; splitting an annual estimate would add an assumption, not repair the source gap.
3. **Actual guide expectations:** dated analyst previews containing management-guide expectations would distinguish eventual-revenue estimates from expected guide ranges. This directly addresses the trading question more than another free fit of conversion weights.
4. **Conversion/timing:** current direct booking/check-in/value/cancellation records could identify cohort behavior. The old Melbourne priors, review posting dates and calendar reopening margins do not contain that complete object. L3's free-weight fit already failed prospective promotion, so adding more free weights without new identifying data is unlikely to resolve the economic question.
5. **Existing reviews and calendar proxies:** recover the archived raw stores and vintage structure; incorporate the PR 60 review-survivorship failures and missed short-lead bookings before testing any extra contribution. These may become useful predictors without claiming that they measure physical conversion or RNPL causality.
6. **Price relevance:** exact release/call clocks and properly archived intraday prices could separate the event legs; the held daily panel cannot. The earlier event study's primary multiplicity and stability failures remain, including its openly retained favorable secondary results. No new return strategy was searched here.

These are distinct gaps. Missing direct cohorts do not mathematically prevent a useful reduced-form revenue forecast; equally, a useful revenue forecast does not by itself prove guidance surprise, RNPL causality or an executable price edge.

## Reproduction, failures and controls

Canonical numerical output: `data/processed/forecast_methods/gbv_decision_0915_v1/street_v1/results_v3/`, bound to quant horizon `results_v2/predictions.csv`. Fair common-model figures should use `common_v1/common_model_metrics.csv`. Deletion/sign tables in `sensitivity_v1/` bind the previous production-identical Street v2 paired rows; the only horizon v2 repair changed excluded oracle metadata, not the production forecasts used here.

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/street_v1/run_v2.py --out NEW_STREET_OUTPUT --predictions data/processed/forecast_methods/gbv_decision_0915_v1/horizon_v1/results_v2/predictions.csv
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/street_v1/score_sensitivity.py --paired data/processed/forecast_methods/gbv_decision_0915_v1/street_v1/results_v3/paired_rows.csv --out NEW_SENSITIVITY_OUTPUT
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/street_v1/common_model_compare.py --out NEW_COMMON_OUTPUT
```

All canonical runners completed successfully. Main comparison approximately six seconds; sensitivity approximately three seconds; common display approximately fifteen seconds. The source-only run completed first and made no performance comparison. The first comparison failed an intentionally strict join validator because both origin arms share a release-date model key. It was repaired in a **new** `run_v2.py` by joining each arm separately with a one-to-many validator; the failed partial `results_v1/` is preserved. No duplicate key is silently tolerated.

Checks cover raw-to-processed consensus reconciliation, quarter-end mapping, positive values/counts, unique publisher-date/slot keys, twelve historical AS OF equality rows, guide outcomes against the frozen calendar, no intervening company information, 153 exact calendar point matches, the common-cushion cancellation identity and input hashes before/after. No new fitted parameters were added by this package. No original forecasts, source data, registry files, scorers, model workbook or memo were modified.

## Harness change requests

None. This package registers no forecasts and runs no scorers.

## RESUME

Use `common_v1` for any side-by-side chart so the joint, fixed, simple baselines and Street share identical targets. Preserve the conditional joint eventual-revenue gain and the direct-guide-growth baseline's stronger guide error simultaneously. Resolve selected-snapshot archival timing before certifying an inherited Street edge; obtain actual guide-expectation evidence before treating a cushion proxy as the market's bar. Parent integrates the separately preregistered calendar-flight ablation and broader alternative-pillar audit. Keep p+3/p+4 Street coverage missing, not interpolated from annual data, and keep all source qualifications and failed earlier arms visible.
