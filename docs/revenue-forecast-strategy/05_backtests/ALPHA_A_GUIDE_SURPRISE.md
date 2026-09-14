# A — Guide surprise

underpowered. The memo may not claim an established pre-guide expectations edge from this package: W1 has 0 eligible signals across 14 guide dates and W2 has 0 across 10. This is an identification and data-timing failure, not evidence that the true economic effect is zero. Agent sub-A · 2026-09-12 · branch `codex/lane1-full`.

## Preregistered pass line

Pass only if sign hit-rate is at least 70% among strictly point-in-time |S| > 1 percentage-point cells in BOTH W1 (2023Q1–2026Q2) and W2 (2024Q1–2026Q2), AND the signed conditional executable next-open 20-day mean return is positive in both windows. Fewer than six qualifying cells in either window is underpowered. Wilson intervals use 95% confidence. Missing signals, uncertain guide signs, and absent executable returns are excluded with explicit counts; missing is never zero.

Use kernel_engine_v2 without re-deriving lambda; reject input published on or after the historical guide date. Consensus must be a usable L0 revenue vintage with identified vendor and timestamp strictly before that date. Date-only same-day stamps are inadmissible. A post-letter diagnostic may be reported separately but is excluded from every pass statistic and registration. Guide midpoint rounding is represented by its published endpoint precision, conservatively at least ±0.5 USD million. Zero, previous-surprise sign, and consensus-base signals are comparison rules, not substitutes for the requested signal. Ridge penalty is fixed at 1 with slope prior 1 and an unpenalized intercept; fit expanding with at least six prior pairs. Sign-label permutations use 9,999 draws, block-bootstrap intervals use 2,000 draws and length-2 chronological blocks; these descriptive intervals do not establish independence or causation. Random seed 20260912.

## What ran

The pass line above was written before running this package. Commands from the repository root with its `.venv` interpreter:

```text
python -m pytest analysis/src/forecast_methods/alpha_a/tests -q
python analysis/src/forecast_methods/alpha_a/run.py
```

The unit suite passed: **12 passed**, exit 0 (3.68 seconds on final test run). The final rebuild exited 0 in **22.462 seconds**; its measured runtime and full input hashes are in `data/processed/forecast_methods/alpha_a/audit.json`, with console receipt in `run_output.txt`. The first complete run took 22.704 seconds; the run after adding all baseline and conditional-return audit tables took 22.146 seconds. No frozen source, data or registry file was modified; no scorer was run by this agent. K0 is imported as `kernel_engine_v2.engine`; lambda is never re-derived here. K0's 12-cell acceptance gate belongs to the parent-verified K0 v2 receipt.

## Results — strict point-in-time test

| Statistic | W1 | W2 |
|---|---:|---:|
| Guide dates inspected | 14 | 10 |
| Strictly earlier attributed consensus values | 0 | 0 |
| Available strict pre-guide kernel signals | 0 | 0 |
| Cells with absolute signal greater than 1pp | 0 | 0 |
| Directionally scorable rounded-interval cells | 0 | 0 |
| Hits / sign-scored cells | unavailable / 0 | unavailable / 0 |
| Hit-rate; 95% Wilson interval | unavailable; unavailable | unavailable; unavailable |
| Sign-label permutation p-value | unavailable, n=0 | unavailable, n=0 |
| Expanding ridge training pairs / out-of-sample predictions | 0 / 0 | 0 / 0 |
| Ridge slope; 95% length-2 block-bootstrap interval | unavailable; unavailable | unavailable; unavailable |
| Executable 1-day mean return; 95% interval | unavailable, n=0 | unavailable, n=0 |
| Executable 5-day mean return; 95% interval | unavailable, n=0 | unavailable, n=0 |
| Executable 20-day mean return; 95% interval | unavailable, n=0 | unavailable, n=0 |
| Preregistered verdict | underpowered | underpowered |

Return statements hold separately for positive signals, negative signals and direction-adjusted pooled signals, for all nonzero signals and for absolute signals greater than 1pp. Every requested combination is enumerated with its denominator in `conditional_returns.csv`. No zero-percent hit-rate or zero-percent return is fabricated. W2 is a subset of W1; these are not 24 independent observations.

`pit_cells.csv` is the complete per-date audit, including five older candidate dates (2021Q4–2022Q4), giving 19 dates in total. Extension eligibility is also zero. Consensus audit rows preserve **vendor, timestamp, register ID, value and exclusion reason**. Seventeen of the 19 candidate pre-guide records are stamped on the guide date; two have no usable timestamp. Under the requested strict-before-date rule, neither class is admissible. No September-2026 current value is inserted at a historical date. The earlier candidates marked unattributed remain excluded even apart from their timing.

K0 independently rejects the required first GBV lag at each historical guide date because that quarter's GBV is published in the same letter as the guide. It is not available before the specified cutoff. A next-day arithmetic diagnostic is available on 11 of the 19 dates and appears in `post_letter_diagnostic.csv` and the right panel of `signal_vs_gap.png`. The actual guide was already public then: these points enter no hit rate, permutation test, regression, return result or registry row, and cannot establish the requested expectations edge.

## Executable-return field audit

The supplied `data/processed/abnb_earnings_reactions.csv` has precisely these columns:

```text
quarter, reaction_date,
abnb_1d_pct, qqq_1d_pct, excess_1d_pct,
abnb_5d_pct, qqq_5d_pct, excess_5d_pct,
abnb_20d_pct, qqq_20d_pct, excess_20d_pct
```

There are **zero `open_*` columns**. The code accepts only explicitly named executable open-entry return columns and refuses the supplied close-based columns. No return series is reconstructed or fetched because there are no eligible signals on which to condition it. This is a missing-field limitation, not an assertion that public OHLC data are unavailable.

## Baselines

`baseline_audit.csv` enumerates zero, previous-surprise sign and consensus-base rules on every date. The zero rule is defined on all dates but does not trade at the 1pp threshold. The previous-surprise rule has 13 available predictor signs on W1, including signs observed after earlier guides; it uses only information before the current origin and preserves the earlier consensus vendor and timestamp. Its current target cannot be scored without admissible current consensus. The consensus-base rule is explicitly defined as consensus divided by one plus the trailing-eight median cushion and is unavailable when consensus is unavailable. **All three have zero evaluable current target pairs on W1 and W2.** No baseline exists for an RMSE ratio on this empty sample. This package makes no assertion that the kernel beats a naive, AR(1), trailing-four or guide-cushion baseline.

## Live scenario for the 5 November Q4 guide

This is a **12 September 2026 forecast**, not a future-dated November vintage. K0's conditional RNPL-scenario guide midpoint is **$3,158.228 million**, with descriptive q10/q90 of **$2,998.031–$3,301.396 million**. These are conditional model outputs, not adopted team targets or validated coverage claims.

| Vendor and source panel | L0 timestamp | Exact consensus, USD m | Conditional signal, % of consensus |
|---|---|---:|---:|
| Alpha Vantage aggregated sell-side, LSEG family | 2026-09-11 | 3,158 | +0.0072% |
| S&P Global Market Intelligence via StockAnalysis | 2026-09-10 | 3,160 | −0.0561% |
| Zacks | 2026-09-11 | 3,200 | −1.3054% |

The brief's approximately $3,159 million family anchor is not itself an L0 observation. The exact designated Alpha Vantage observation is retained rather than manufacturing an average or claiming extra precision. Yahoo's same-family observation is not counted as another independent panel. `live_november_guide_scenario.csv` preserves every register ID and timestamp. The signal differs by vendor, and no historical significance or predictive return is attributed to these three live scenarios.

## Registry limitation and harness change request

Requested method/object: `alpha-a__guide_gap_next_q`. **Zero historical forecast rows and zero live rows are registered.** The frozen harness has no `guide_gap_next_q_pct` target, and its accepted live-origin date is 2026-09-11 rather than the actual 2026-09-12 run date. Using September 11 would backdate the RNPL assumption; using November 5 would falsely assert future information. The accepted `guide_mid` target would change the object from a consensus-relative gap to a guide level. None of these changes is silently made.

`registry_status.json` records the limitation, and an empty format-1.0 template is saved **inside this package's output folder**, named `alpha-a__guide_gap_next_q_UNREGISTERED.csv`. It is deliberately outside the shared registry so no empty or misdated file can be scored as a forecast. Requested future harness changes: support the actual current origin and a guide-gap target with an explicit dated consensus denominator. Parent owns scorer decisions; the harness remains frozen.

## Interpretation and one proposed memo sentence

**“The supplied Lane-1 data do not establish a pre-guide expectations edge: the strict point-in-time test has 0 eligible signals across 14 W1 and 10 W2 guide dates.”**

The claim is confined to this dataset and the requested cutoff. Date-only records may conceal genuinely pre-close information, but there is no sufficiently precise timestamp here to prove it. A new, preregistered design could test a nowcast of the unavailable GBV or an explicitly post-letter trade, provided it used appropriate contemporaneous consensus and executable entry prices. This package does not substitute either design after seeing results.

Parameter count: one seasonal kernel coefficient and one trailing-cushion location for a given target season; kernel weights are fixed by K0. The proposed diagnostic regression has two fitted parameters (intercept and slope), a fixed ridge penalty and a fixed slope prior of one. No ridge model was fitted because there are zero admissible pairs. Bootstrap, permutation and Wilson implementations are tested but yield unavailable results rather than simulated empirical evidence on an empty sample. Token usage is unavailable from the agent runtime and is not estimated.

## RESUME

Parent should review the strict date refusals, exact reaction field audit, live stamps and empty registry decision; run the three independent refuters against the single proposed sentence; and retain this clean negative in the lane close. To revisit the economic hypothesis, obtain public timestamped pre-guide consensus and a pre-guide GBV nowcast or explicitly preregister a post-letter design, then use a new package version and genuinely executable next-open returns. Do not weaken the date rule, backdate the live scenario, overwrite this package or reinterpret the 11 post-letter diagnostic points as an expectations-edge backtest.
