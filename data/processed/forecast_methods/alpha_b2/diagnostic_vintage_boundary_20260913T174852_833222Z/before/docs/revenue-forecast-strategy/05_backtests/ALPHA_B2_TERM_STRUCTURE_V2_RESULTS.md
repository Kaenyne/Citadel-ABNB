# B2 — Term structure and next-quarter consensus revisions: results

Codex B2 subagent · 2026-09-13 · `codex/lane2-full` · new `alpha_b2/` code and outputs only · approximately 25 minutes.

## Verdict

**FAIL.** The kernel signal has the right correlation sign, but its strong-signal hit rate is 55.6% in W1 and 57.1% in W2, below the pre-registered 70% requirement. Correlation intervals include zero; signal-aligned executable returns average below zero on both horizons in both windows. B2 establishes no reliable consensus-revision or trading edge. FY-guide tests have only two observations and are underpowered. The prescribed unseasonal GBV extrapolation produces large LIVE levels that should remain arithmetic sensitivities.

## Pre-registered pass line

Recorded before execution in [the immutable preregistration](ALPHA_B2_TERM_STRUCTURE_V2.md), 13 September 2026:

PASS only if on BOTH windows: S1 predicts the sign of R_d on ≥ 70% of |S1| > 0.5% cells with ≥ 6 cells, and corr(S1, R_d) > 0.4. T2 and T3 are
reported, not gating. Fewer than 6 cells → underpowered. Verdict word in the first paragraph.

## What ran

From the repository root, using the repository virtual environment:

```text
.venv\Scripts\python.exe -m pytest analysis/src/forecast_methods/alpha_b2/tests -q
.venv\Scripts\python.exe analysis/src/forecast_methods/alpha_b2/run.py
```

| Execution | Exit | Result / wall time |
|---|---:|---|
| Initial tests | 0 | 16 tests passed, 2.86s reported by pytest |
| Initial complete run | 1 | Optional harness baseline input received raw string dates; no registration occurred; elapsed time before exception not recorded |
| Integration fix tests | 0 | 17 tests passed, 4.22s |
| Registration run | 0 | 49 rows registered, 8.40s |
| Final tests, including chronological mixed-timezone selection | 0 | 18 tests passed, 2.75s |
| Final reproducibility run | 0 | 49 identical registry rows preserved, 9.43s |
| Horizon metadata correction tests | 0 | 23 tests passed, 2.74s |
| Authorized horizon metadata correction run | 0 | 49 horizon fields and 45 explanatory notes corrected; forecast values unchanged, 7.38s |

Receipts are `tests_{first,second,final}_receipt.txt`, `run_{first,second,final}_receipt.txt`, `tests_horizon_correction_receipt.txt` and `run_horizon_correction_receipt.txt` under `data/processed/forecast_methods/alpha_b2/`. The failed receipt is retained. The original final research run is `run_20260913T171104_950676Z/`; current outputs with corrected registry units are `data/processed/forecast_methods/alpha_b2/run_20260913T171654_499731Z/`. Each run gets a new directory; the preregistration and earlier output files remain untouched. Input hashes record the exact bytes parsed, including the L0 snapshot.

## Method and timing

The code imports `kernel_engine_v2`. At each letter date d, it uses `as_of=d+1 calendar day` and asserts latest printed input date ≤ d. Seasonal lambda, point-in-time variant selection, and the trailing-eight median cushion therefore include data printed in that letter, matching A2. No lambda is re-derived locally. Full-sample replay instead uses coefficients and cushion fitted through RUN_DATE; it is explicitly retrospective and cannot pass the research gate.

The q+2 base follows the specified rule: GBV(q+1) = GBV(q) × (1 + mean of the last four exact observed GBV y/y rates). The LIVE Q1 2027 extension persists that growth again for GBV Q4. Changing w from 0.33 to 0.5 to 2/3 holds the imported lambda fixed. These bands measure arithmetic sensitivity; they are not fitted alternatives or probability intervals.

Historical consensus requires the correct role, attribution, PIT usability and date. L0's quarantined `PG-2024Q3-revenue` remains unavailable despite a number in the merged panel. Current rows never enter historical signals or outcomes. Historical same-day morning consensus is accepted. LIVE timestamp parsing accepts dates and UTC/offset timestamps, selects by the actual chronological instant, and excludes observations later than the run time.

## Results

The primary correlation uses every evaluable S1/revision pair. Sign statistics use |S1| > 0.5%; unchanged consensus is a distinct zero sign, so a nonzero directional signal does not get a hit.

| PIT window | Origins | Paired n | Strong n | Hits | Hit rate, 95% Wilson | Correlation, 95% two-event block interval | Sign permutation p | Correlation permutation p |
|---|---:|---:|---:|---:|---|---|---:|---:|
| W1 | 14 | 11 | 9 | 5 | 55.6% [26.7%, 81.1%] | 0.687 [−0.357, 0.956] | 0.155 | 0.017 |
| W2 | 10 | 9 | 7 | 4 | 57.1% [25.0%, 84.2%] | 0.671 [−0.620, 0.963] | 0.289 | 0.045 |

W1 misses two undefined default seasonal kernels (2023Q1 and Q3) and the quarantined 2024Q3 consensus. W2 misses only that quarantine. Among all paired outcomes, W1 has 5 positive / 4 unchanged / 2 negative revisions (n=11); W2 has 5 / 3 / 1 (n=9). S2 has **0 evaluable origins** in both windows: there is no admissible historical q+2 pre-guide consensus at d.

The 10,000 permutations break time order; their p-values are descriptive. Correlation bootstrap resamples paired blocks of two consecutive eligible events and retains 10,000/9,999 finite draws for W1/W2. Missing origins create gaps and the two windows overlap. Neither method supplies strong inferential assurance for this short series.

| Retrospective full-sample replay | Paired n | Strong n | Hits / strong n | Correlation |
|---|---:|---:|---:|---:|
| W1 | 13 | 10 | 6/10 = 60.0% | 0.853 |
| W2 | 9 | 6 | 4/6 = 66.7% | 0.834 |

The look-ahead replay also misses the sign threshold. It is not evidence of an investable result.

| PIT revision baseline | Window | Paired n | Strong n | Hits | Hit rate | Revision MAE / RMSE, pp |
|---|---|---:|---:|---:|---:|---:|
| No revision | W1 | 11 | 9 | 3 | 33.3% | 1.210 / 1.762 |
| Last revision continues | W1 | 10 | 8 | 3 | 37.5% | 2.157 / 2.790 |
| No revision | W2 | 9 | 7 | 2 | 28.6% | 1.428 / 1.942 |
| Last revision continues | W2 | 8 | 6 | 3 | 50.0% | 1.317 / 1.443 |

Baseline samples are explicit; last-revision rows need one additional observed revision. No comparison silently assumes equal n. S1 is a direction signal and is not fitted to predict a numerical revision magnitude.

T2 has only the February→May and May→August 2026 FY revenue-bucket changes. Both are up. The FY sensitivity T is −8.09% and +3.36%, respectively: **1/2 signs correct, 50.0%, Wilson [9.5%, 90.5%]**, in each window. The same two T signals score 1/2 against the next-quarter consensus revision. Correlations are unavailable at n=2. Buckets are management percentage ranges (some with floor language), converted using prior-year revenue; they are not FY Street estimates or exact measurements. The output retains low- and high-anchor sensitivities. Beyond the next two kernel quarters, FY uses prior-year same-quarter revenue, so this construction can materially understate growth in those remaining quarters.

| PIT T3, strong S1 cells | Paired n | Strong n | 20-day mean signal-aligned excess return | 60-day mean signal-aligned excess return | 20-/60-day positive aligned counts |
|---|---:|---:|---:|---:|---:|
| W1 | 11 | 9 | −0.443pp | −0.033pp | 5/9; 4/9 |
| W2 | 9 | 7 | −0.983pp | −1.252pp | 4/7; 3/7 |

Returns use only `excess_open_20d_pct` and `excess_open_60d_pct`; a negative signal reverses the return sign. These descriptive averages precede trading costs and are not a portfolio backtest. T-based aligned return means are −2.520pp at 20 days and +7.774pp at 60 days, with n=2 in each overlapping window; no trade claim is supported.

## Current term structure — LIVE sensitivity only

RUN_DATE 2026-09-13. Each row is one model scenario, not an independent observation. USD millions; raw revenue is before the guide cushion.

| Quarter | w | Scenario n | Raw revenue | Implied guide midpoint |
|---|---:|---:|---:|---:|
| 2026Q4 | 0.33 | 1 | 3,450 | 3,389 |
| 2026Q4 | 0.50 | 1 | 3,540 | 3,478 |
| 2026Q4 | 2/3 | 1 | 3,629 | 3,565 |
| 2027Q1 | 0.33 | 1 | 4,237 | 4,163 |
| 2027Q1 | 0.50 | 1 | 4,348 | 4,272 |
| 2027Q1 | 2/3 | 1 | 4,457 | 4,378 |

| Period / selected consensus panel | Independent panel n | Revenue, USD millions | Vendor and source timestamp |
|---|---:|---:|---|
| 2026Q4, LSEG family | 1 | 3,161.02149 | Yahoo Finance (LSEG family), `2026-09-13T15:20Z` |
| 2026Q4, S&P | 1 | 3,160 | S&P Global Market Intelligence via StockAnalysis, `2026-09-10` |
| 2026Q4, Zacks | 1 | 3,200 | Zacks, `2026-09-11` |
| 2027Q1 | 0 | Unavailable | No admissible `current` revenue row in the captured register |

These are the latest admissible stamps in the captured register; S&P and Zacks were not refreshed today by B2. Older Yahoo/Alpha Vantage relays are not additional independent LSEG panels. At w=2/3, the implied Q4 guide sits 12.77% above the latest LSEG-family observation; that gap is an output of the unseasonal assumption, not an established edge.

The four observed GBV y/y rates average +16.1919%. Applying that as sequential quarterly growth takes the latest $27.2bn of GBV to $31.604bn for Q3 and $36.722bn for Q4. This discards quarterly seasonality and explains the unusually high revenue levels. A replacement with a same-quarter prior-year anchor would be economically better specified, but requires a separately preregistered version and is not silently substituted here.

## Registration, parameters and limitations

Registered `alpha-b2__revenue_q_plus_2.csv` through `harness_v1_1.registry.register`: **49 rows** — W1 PIT 12 / full-sample 13; W2 PIT 10 / full-sample 10; LIVE 2 per replay. The revenue target uses the raw pre-cushion revenue, with guide values retained separately in the package tables. No consensus enters this registered object. Two parameter summaries affect each revenue forecast: seasonal lambda and trailing-four GBV growth; a guide forecast adds the cushion summary. The fixed weight, exponential half-life and recursion horizon are not fitted. FY uses up to four seasonal coefficients plus growth/cushion summaries.

W1's missing q+2 target 2023Q1 lies before the prescribed first origin; PIT also lacks a q+2 kernel for 2023Q3. These generate coverage warnings, not invented forecasts. W2 registry coverage is complete because registry membership follows q+2 targets, while the revision study windows follow guided q+1 targets. The brief's q+2 label means two quarters after the printed quarter and remains `horizon_from_print=2` in the historical sidecar and object identity; LIVE Q1 2027 has `horizon_from_print=3`. The registry follows the authoritative FORMAT unit, `horizon_q = target-quarter ordinal − vintage-calendar-quarter ordinal`: **1 for all 45 historical rows and both LIVE Q4 2026 replays, 2 for both LIVE Q1 2027 replays**. The initial printed-quarter units in this field were misleading and were corrected after parent audit. No uncertainty ladder is fabricated from arithmetic weights. The parent owns both scorer runs.

The authorized correction ran as:

```text
.venv\Scripts\python.exe -m pytest analysis/src/forecast_methods/alpha_b2/tests -q
.venv\Scripts\python.exe analysis/src/forecast_methods/alpha_b2/run.py --correct-horizon-metadata
```

Before re-registering, it preserved the exact original registry bytes as `run_20260913T171654_499731Z/registry_before_horizon_metadata_correction.csv` (SHA-256 `94906a89197a99c0b0e32cd6326d264f395bbbeaad10df9b6ca4646097db33c0`). The correction changes only `horizon_q` and explanatory `notes`. `metadata_correction_verification.json` records an exact comparison of all other registry fields and byte-identical checks for all seven research CSVs, including cells, statistics, returns, term structure and consensus comparisons. The sidecar horizons, point forecasts, quantiles, samples and FAIL verdict are unchanged. This correction did not run either scorer.

The first run's only execution failure was local integration: raw target CSV dates were supplied to the harness baseline. Letting the harness load its own typed targets fixed it; frozen code was untouched. A final test verifies chronological selection across differently formatted timezone offsets. The identical registry was preserved on rerun.

Before the horizon metadata correction, parent verification reported both scorer exits 0 after the registrations then present: 4,218 total registry rows and 284 scoreboard rows, with the original 276 scores and 81 protected-file hashes preserved. Its independent B2 review reconciled 12 kernel guides, 28 executable-return cells, source roles/timestamps, sample counts and correlations. These are integration checks; they do not change the FAIL research verdict. The parent owns any scorer rerun after the metadata correction.

There is also a timing limitation in the hypothesis itself: S1 is available after the letter, but R starts at pre-letter consensus. R therefore contains consensus adjustment to information already in the public guide, as well as subsequent drift. Positive correlation alone does not isolate future post-entry revisions or establish an independent mechanism. No decisions about direction, price target, fees, RNPL or kill-list quantities were made.

## One proposed memo sentence

“The point-in-time kernel correctly signed next-quarter consensus revisions in 5/9 strong-signal cases in W1 and 4/7 in W2, below the pre-registered 70% threshold, while mean signal-aligned 20- and 60-day executable excess returns were negative in both windows.”

## RESUME

Use the metadata-corrected run directory `run_20260913T171654_499731Z/` and retained receipts; preserve this failed result and the original registry snapshot. The parent should rerun its scorer checks after the metadata correction, update B2's workboard link to this result note, and keep the current arithmetic levels out of headline forecasting. Any next B version should preregister a seasonal GBV anchor, distinguish consensus changes already implied by the announced guide from subsequent drift, and obtain attributed q+2/FY consensus histories before claiming a term-structure edge. The existing source timestamps and sparse FY results must remain visible.
