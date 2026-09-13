# A2 — Guide surprise under the harness convention

**Partial.** The memo may describe a limited guide-sign expectations association under the letter-close convention: 7/8 high-signal cells are correct on W1 and 6/7 on W2. It may not claim an established executable expectations edge. Direction-adjusted next-open 20-day returns average **−0.31pp / −0.98pp**, and both bootstrap 90% intervals cross zero. The registered mechanism criterion is met; the trade criterion fails. These are signals formed with the letter's freshly printed GBV, at the same event that reveals the guide, not forecasts proven available before that release. Agent sub_a2 · 2026-09-13 · branch `codex/lane2-full`.

## Pre-registered pass line

Written **2026-09-13 15:00:09 UTC**, before the package's first empirical run.

PASS only if, on BOTH W1 and W2: (1) sign hit-rate ≥ 70% on |S| > 1pp cells with at least 6 such cells; (2) the direction-adjusted mean
`excess_open_20d_pct` is positive with a bootstrap 90% interval excluding zero; (3) the partial correlation of S with `excess_open_20d_pct`,
controlling for the GBV surprise and the raw guide gap, keeps the sign of the raw correlation. Fewer than 6 cells in either window → underpowered.
(1) met and (2) or (3) not → "partial: mechanism confirmed, trade unproven". The first paragraph of the note answers: may the memo claim an
expectations edge on the guide? — yes / no / partial / underpowered.

Additional analysis choices fixed before running: K0 `kernel_guide(quarter, d+1 day)` implements the letter-close information set, with its median trailing-eight cushion and nested variant selection. The ex-COVID variant is shown separately. The full_sample replay fixes the K0 full-history variant but still refits lambda and cushion at each historical date; it is a retrospective specification diagnostic, excluded from the verdict. No historical row may use current consensus, an inadmissible L0 row, or a later stamp. An explicitly quarantined L0 row cannot be rescued from the merged table that generated it. Dollar guide rounding is conservatively represented by midpoint ±$0.5m, with ambiguous signs excluded explicitly. The high-signal cutoff is strictly greater than 1 percentage point.

Permutation tests shuffle the observed target-sign labels over eligible high-signal cells, use a one-sided at-least-as-many-hits statistic, 9,999 draws and a +1 correction. Correlations use all available pairs and 2,000 circular moving-block bootstrap draws with length 2. Conditional return means use the same block length and 2,000 draws, with 90% intervals. The seed is 20260913. Controls are computed on a shared complete-case sample, so the reported raw correlation uses the identical rows as each partial correlation. The pass control is joint GBV surprise plus raw guide gap; separate GBV, gap and revenue controls and the three-control model are diagnostics. Ridge uses an unpenalized intercept, slope prior 1, fixed penalty 1 and at least six prior pairs. No tuning follows results. Zero return means a specified no-trade strategy, never a missing observation.

## What ran

Commands from the repository root with its `.venv` interpreter:

```text
python -m pytest analysis/src/forecast_methods/alpha_a2/tests -q
python analysis/src/forecast_methods/alpha_a2/run.py
```

The initial 13 tests passed, exit 0, 1.75 seconds. The final reviewed **14 tests passed**, exit 0, 2.27 seconds. The complete reviewed rebuild and registration exited **0 in 25.741 seconds**, creating 48 rows under the new method `alpha-a2__guide_mid_next_q`. The first successful build took 23.770 seconds; the provenance-output build took 24.611 seconds; both receipts remain preserved. The first rebuild failed at registration because K0 returned null quantiles for one-observation lambda histories; that failure is preserved in `run_receipt_initial.txt`. The local adapter correction and its limits are explained below. Final receipts are `test_receipt_reviewed.txt`, `run_receipt_reviewed.txt` and `audit.json`; the latter hashes every package input, including K0's own dependencies. Neither scorer was run by this subagent; the parent owns CLOSE and both scorer receipts.

After M appended new current consensus, the integration rebuild exposed a mixed-timestamp parser bug. The final integration fix passes **16 tests**, exit 0, 2.29 seconds, and rebuilds/registers in **21.170 seconds**, exit 0. Its receipts are `test_receipt_after_m.txt`, `run_receipt_after_m.txt`, `after_m_rebuild_comparison.json` and the refreshed `audit.json`. Historical statistics and registry bytes are unchanged; the current LSEG-family comparison is updated below. The initial evidence is preserved in a dated copy.

All kernel estimates come from imported `kernel_engine_v2.engine`. No lambda formula was independently estimated. Calls use `as_of=d+1 calendar day` and check `knowable_from<=d`, then register the historical vintage as `d`. The full-sample replay fixes the **ewm** variant selected on the full available history but refits lambda and cushion using each historical information set. Its specification choice is retrospective and never enters the verdict. The separate ex-COVID replay happens to equal the nested default at every historical origin in this sample.

## Results — PIT default

| Statistic | W1: targets 2023Q1–2026Q2 | W2: targets 2024Q1–2026Q2 |
|---|---:|---:|
| Candidate letters | 14 | 10 |
| Admissible attributed pre-guide consensus | 13/14 | 9/10 |
| Available kernel guide | 12/14 | 10/10 |
| Evaluable signal and guide-gap pairs | 11/14 | 9/10 |
| Absolute signal >1pp; rounded-sign eligible | 8; 8 | 7; 7 |
| Guide-sign hits | 7/8 = **87.5%** | 6/7 = **85.7%** |
| Wilson 95% interval | 52.9–97.8%, n=8 | 48.7–97.4%, n=7 |
| One-sided sign-label permutation p | 0.0687, n=8 | 0.1428, n=7 |
| corr(S, actual guide gap) | 0.677, n=11 | 0.655, n=9 |
| Length-2 block-bootstrap 95% interval for correlation | −0.230 to 0.911, n=11 | −0.416 to 0.916, n=9 |
| Direction-adjusted next-open 20-day mean | **−0.308pp**, n=8 | **−0.983pp**, n=7 |
| Bootstrap 90% interval for that mean | **−3.707 to +3.424pp**, n=8 | **−4.229 to +2.453pp**, n=7 |
| Joint GBV-surprise + raw-guide-gap partial correlation | −0.538, n=6 | −0.538, n=6 |
| Raw return correlation on those same six rows | −0.069, n=6 | −0.069, n=6 |
| Conditions 1 / 2 / 3 | met / failed / provenance-limited | met / failed / provenance-limited |
| Verdict | partial | partial |

W2 is a subset of W1. The repeated n=6 control sample is exactly the same six observations, not independent confirmation. No rounded guide interval straddles zero in the high-signal set. Percentage signals and gaps use the exact registered consensus denominator; guide endpoints are treated as rounded dollars, conservatively midpoint ±$0.5 million. There are no letter-integer growth targets in this test.

The full-sample **specification-selection sensitivity** has 13/14 and 9/10 evaluable pairs: sign hit rates are 7/10 (70.0%) and 5/7 (71.4%). Its signed 20-day means are −3.193pp (90% interval −5.896 to −0.524, n=10) and −1.827pp (−5.211 to +1.585, n=7). It supplies no positive trade result. Its additional early observations are possible because its hindsight-selected ewm variant admits pandemic-era seasonal observations that the PIT fallback excludes. This is not a replacement headline sample.

Expanding ridge produces five out-of-sample gap predictions, all in W2, from 2025Q2 through 2026Q2. Prior sample sizes are 6–10; slope estimates rise from 0.100 at the first forecast to 0.489 at the last. Out-of-sample gap RMSE is 1.780pp (n=5). This regression is a diagnostic, is not sufficiently populated for the registered high-signal pass test, and does not replace the raw kernel signal. Every forecast's latest training date appears in `ridge_expanding.csv`.

## Availability and Lane 1 reconciliation

All 19 candidate rows, including five older extension letters, remain in `cells.csv`.

| Exclusion | W1 count | W2 count | Reason |
|---|---:|---:|---|
| 2023Q1 and 2023Q3 kernel undefined | 2/14 | 0/10 | K0 nested default falls back to ex-COVID, with no admissible same-season lambda at those origins. |
| 2024Q3 consensus unavailable | 1/14 | 1/10 | L0 `PG-2024Q3-revenue` is explicitly `pit_usable=False`, has no timestamp, and records that its merged-table source says `NEXT-QUARTER CONSENSUS NOT FOUND`. |
| All other headline letters | 11/14 evaluable | 9/10 evaluable | Admissible kernel, stamped vendor consensus and executable returns. |

The brief's assertion that every W1 letter becomes evaluable conflicts with these source facts. The parent's contemporaneous instruction explicitly agreed to preserve the quarantine. The merged row is a duplicate of the disputed source, so using it would not resolve the missing vintage. Guide dollars for 2024Q3 are still registered because that level forecast does not consume consensus; only its consensus-relative test is unavailable.

The older 2021Q4–2022Q4 extension has 0/5 evaluable default signals: no initial realised cushion and then no admissible ex-COVID seasonal lambda. Two consensus rows are usable and attributed, two are explicitly unattributed, and one is absent. Unattributed source values remain flagged for inspection and are excluded from every headline statistic. The full-sample sensitivity has 2/5 evaluable extension cells, 1/2 sign hits, and is underpowered; it cannot fill the main sample.

`lane1_reconciliation.csv` compares exclusions and counts only after fresh A2 computation. The 11 overlapping fresh kernel dollar values agree with Lane 1's post-letter arithmetic diagnostic to at most 4.55e-13 USD million. No Lane 1 diagnostic value was an input to the signal, return test, regression or registry. The different eligibility comes from the explicit new convention and new return source, not a re-labelling of the old test.

## Executable returns, controls and baselines

All return legs are `returns_v1.excess_open_{1,5,20,60}d_pct`, event-matched by letter date. Entry is the next trading-day open; each horizon exits at the specified close. The overnight gap and legacy close-to-close series enter no return statistic. Positive/negative columns below are raw ABNB-minus-QQQ means; pooled columns multiply by the signal sign.

| High-signal kernel strategy | W1 mean, n; bootstrap 90% interval (pp) | W2 mean, n; bootstrap 90% interval (pp) |
|---|---|---|
| Positive S, 20 days | −1.601, n=5; [−6.034, +2.832] | −1.601, n=5; [−6.034, +2.832] |
| Negative S, 20 days | −1.847, n=3; [−3.264, −0.430] | −0.560, n=2; degenerate length-2 interval |
| Pooled signed, 1 day | −0.157, n=8; [−2.217, +2.170] | −1.072, n=7; [−2.767, +0.591] |
| Pooled signed, 5 days | −1.229, n=8; [−3.662, +1.545] | −2.420, n=7; [−3.979, −0.639] |
| Pooled signed, 20 days | −0.308, n=8; [−3.707, +3.424] | −0.983, n=7; [−4.229, +2.453] |
| Pooled signed, 60 days | −1.639, n=8; [−3.518, +0.447] | −1.252, n=7; [−3.909, +1.106] |

The n=2 negative subset's length-2 circular block resamples the whole pair and cannot estimate uncertainty; its numerically zero-width interval is not confidence in the mean. No subset inference with n<6 is promoted. The n=7 five-day negative return does not rescue a positive 20-day trading claim. Intervals use retained chronological observations, are descriptive, and do not establish independent event returns or account for transaction costs.

Baseline comparisons below use the same current-kernel `|S|>1pp` opportunity set, with each baseline's available sign. The full `conditional_returns.csv` also reports all available observations for each strategy, all horizons and both raw-sign sides.

| Baseline: signed next-open 20-day return | W1 mean, n; bootstrap 90% interval (pp) | W2 mean, n; bootstrap 90% interval (pp) |
|---|---|---|
| Trade sign(actual guide gap) | +2.647, n=8; [−0.703, +6.094] | +2.393, n=7; [−0.621, +5.515] |
| Zero rule | 0.000, n=8; [0, 0] | 0.000, n=7; [0, 0] |
| Previous letter's surprise sign | −1.414, n=7; [−4.507, +2.398] | −0.913, n=6; [−5.360, +3.398] |

The actual guide-gap baseline is executable only after the letter and hence admissible for this next-open comparison. The previous-letter rule abstains when that immediately preceding letter's gap is unavailable. The zero rule is explicitly no trading; its zeros are not missing returns. The kernel does not establish an incremental advantage over these baselines.

| Control | W1 raw → partial, n | W2 raw → partial, n |
|---|---|---|
| GBV surprise | −0.069 → −0.463, n=6 | −0.069 → −0.463, n=6 |
| Raw guide gap | +0.016 → −0.392, n=11 | −0.052 → −0.441, n=9 |
| Revenue surprise | +0.016 → +0.062, n=11 | −0.052 → +0.003, n=9 |
| GBV surprise + raw guide gap (pass control) | −0.069 → −0.538, n=6 | −0.069 → −0.538, n=6 |
| All three | −0.069 → −0.474, n=6 | −0.069 → −0.474, n=6 |

GBV and revenue surprises compare the printed-quarter actual to L0's `AP-<quarter>-gbv/revenue` observations, after unit conversion to USD million. Each vendor field, timestamp, source value, register ID and missingness reason is in `cells.csv`. **All six GBV controls carry `vendor_not_recorded` even though L0 marks them `vendor_attributed=True` and `pit_usable=True`.** The numerical calculation follows those source eligibility flags; it does not establish named-vendor provenance. `controls.csv` exposes the six unrecorded-vendor rows. A control sample requiring an actual named GBV vendor would contain zero of these six observations and would be unavailable. Thus the numerical sign check passes, but **condition 3 is provenance-limited and not established**. `statistics.csv` preserves the numerical sign-match field separately and does not mark the criterion as met. This reporting correction was requested during final parent review; no numerical result or eligibility was changed.

The joint pass control mechanically keeps an already **negative** raw sign; it does not demonstrate a positive expected-return relationship. The full W1 raw return correlation is nearly zero and reverses after controlling for the guide gap alone. Six complete cases and two or three controls cannot support a causal interpretation.

## Live 5 November guide scenario

The forecast vintage is **2026-09-13**, for the Q4 guide expected on 5 November. K0's conditional RNPL ledger nowcast supplies the missing Q3 GBV. The guide midpoint is **$3,158.228 million**, with descriptive q05/q95 **$2,955.150–$3,347.143 million** and q10/q90 **$2,998.031–$3,301.396 million**. This is a conditional model scenario, not an adopted team target or calibrated coverage guarantee.

| Independent panel (one observation each, n=1) | Vendor and stamp | Consensus (USD m) | S = K/C−1 |
|---|---|---:|---:|
| LSEG family | Yahoo Finance (LSEG family); 2026-09-13T15:20Z | 3,161.02149 | −0.0883742% |
| S&P | S&P Global Market Intelligence via StockAnalysis; 2026-09-10 | 3,160 | −0.0561% |
| Zacks | Zacks; 2026-09-11 | 3,200 | −1.3054% |

The current comparison uses information captured through **2026-09-13T17:16:21.504563Z**, the actual UTC start of the integration rebuild. The newer Yahoo observation replaces Alpha Vantage's 2026-09-11 $3,158 million comparison (+0.0072%); both belong to the same LSEG family and are counted once. The new source is `CU-2026Q4-revenue-Yahoo-20260913T1520Z`, captured by M at 15:20:58Z and registered with the minute stamp 15:20Z. Exact register IDs and stamps are in `live_november_guide_scenario.csv`. The model's guide dollars are independent of the consensus denominator, so the registry has one live row per replay rather than three copies of the same forecast. The live comparison crosses the 1pp signal cutoff only against Zacks; the historical trade test does not validate trading that scenario.

## What failed or could not be done

The empirical pass line failed on returns, not on a missing return file. W1 and W2 have enough high-signal cells for the registered minimum, but hit-rate uncertainty remains wide and neither one-sided permutation p is below 0.05. Neither this threshold nor any other unregistered significance line is substituted for the preregistered verdict.

The first build reached registry validation with four PIT guide-level rows whose seasonal lambda history had n=1: 2023Q2, 2023Q4, 2024Q1 and 2024Q3. K0 could compute their point but could not estimate kernel dispersion, leaving q50 and bounds null. The validator correctly refused this. The adapter was fixed once, without modifying K0 or any signal: where K0's ladder is missing, it applies the empirical trailing-cushion ratios to K0's guide point and reports **cushion-only conditional quantiles**, explicitly marking kernel dispersion unavailable. Six/eight realised cushion ratios support those four ladders. They must not be read as complete predictive uncertainty. This is a registration and interval-availability correction made after the initial run, not a pre-registered uncertainty model; pass statistics are unchanged. Available K0 ladders are retained unchanged for other rows. A new test checks ordering, the median and invalid cushion inputs. The initial failed output remains preserved.

The new method registers 48 rows: PIT W1 12, PIT W2 10, full_sample W1 14, full_sample W2 10, and LIVE 2. The W1 PIT coverage warning (12 versus 14) is expected and preserved. L0, K0, both harness modules, older package outputs and all frozen inputs remain unchanged. Parent must run both scorers, interpret guide-mid rows without an available naive baseline as **no baseline**, and attach the scorer outcome to its closing receipt.

Parameter count: the historical point has one target-season lambda and one trailing-eight cushion location (2); fixed 2/3–1/3 weights, the fixed ewm half-life and fixed ridge penalty are not fitted. The conditional live point adds two ledger-regression coefficients (4 total). Distribution dispersions/resampling are estimated separately and not included in that point-parameter count. The optional expanding ridge has two fitted parameters, intercept and slope. Controls fit an intercept and one to three covariate coefficients for each residualized variable; their tiny effective samples are disclosed above.

## Interpretation

Suggested memo sentence: **“At letter-close vintages, the kernel agrees with the guide-gap sign in 7/8 W1 and 6/7 W2 cases with |S|>1pp, but the executable next-open 20-day return test does not establish a trading edge.”**

The economical conclusion is a partially supported mechanism and an unproven trade. The pass-control sign condition is too weak to establish favorable direction when the starting correlation is negative. No return alpha, causal effect, before-release forecast performance, adopted direction or target price follows from this package. The next empirical improvement is genuinely pre-release GBV availability and a larger independent vintage sample, not relaxation of the existing exclusions.

## Integration fix after M — mixed current timestamps

M's authorized register append introduced UTC-minute timestamps alongside older date-only timestamps. The parent's preserved failure receipt is `data/processed/forecast_methods/lane2_validation_v1/a2_after_m_failure.txt`: pandas inferred a date-only parser and rejected `2026-09-13T15:20Z`. The old midnight cutoff would also have excluded valid same-day captures even if parsing succeeded.

The live selector now explicitly parses mixed timestamps in UTC, sorts actual normalized instants, excludes captures after the actual UTC run-start cutoff, then selects the newest observation within each independent vendor family. Date-only stamps are ordered at the start of their stated UTC date. The cutoff is recorded in both the live table and audit. Focused tests cover date-only/full UTC coexistence, same-day inclusion, same-day and next-day future exclusions, offset ordering, an exact cutoff boundary and invalid timestamps. Historical selection and all backtest logic are unchanged.

Before rebuilding, 19 existing evidence files, including the live table, original note, audit, history tables and registry, were copied into `data/processed/forecast_methods/alpha_a2/pre_m_refresh_20260913T171409Z/`, with a SHA-256 manifest. The stable L0 register contains 171 rows. After the fix, the LSEG-family denominator changes from **$3,158m (Alpha Vantage, Sep 11)** to **$3,161.02149m (Yahoo, Sep 13 15:20Z)**, moving S from **+0.007218571615%** to **−0.088374201733%**. The $3,158.227962m kernel guide, S&P comparison and Zacks comparison are unchanged.

The historical cells, statistics, conditional returns, controls, ridge forecasts, Lane-1 reconciliation and registry preview are all byte-for-byte identical to the saved evidence. The **48-row registry is byte-for-byte unchanged**, SHA-256 `0db86bcbab4aebd4155f4a0c5f44638ff5afc642425733adf10b7d0cd61e6aa0`. The exact proposed memo sentence is unchanged. `after_m_rebuild_comparison.json` records these checks and both live tables. Neither scorer was run during this fix.

## RESUME

Parent should run both scorers, review the 48 registered rows and the expected W1 coverage warning, and send this completed package to the three Gate-2 refuters. Preserve the 2024Q3 consensus quarantine, the two undefined PIT lambda origins, the distinction between retrospective variant selection and PIT coefficients, and the four conditional cushion-only ladders. The registered verdict is partial; only the narrow sign-association statement is defensible, with no established executable expectations edge. All rebuild commands, source hashes, exact per-date inputs, controls, baselines and failure receipts are in the new alpha_a2 folders; no additional data acquisition or human decision is required to close this package.
