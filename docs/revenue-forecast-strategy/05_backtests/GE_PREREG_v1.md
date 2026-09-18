# GE preregistration — GBV conversion and earnings-event risk

15 September 2026. Written before this package's additional calculations. The underlying historical events have already been examined in prior work; this is a fixed analysis plan for an audit, not an untouched holdout or a fresh confirmatory study.

## Objective and scope

Evaluate the existing fixed-weight GBV conversion method for a position formed before earnings, distinguish that from post-release entries, and produce an honest four-quarter Excel and two-page memo. Forecast targets: Q3 2026, Q4 2026, Q1 2027 and Q2 2027 maximum. Retain seasonal K0 conversion, two-thirds/one-third lag weights and explicit guidance cushion. No component-model rebuild, multiple search, 2028 projection or forced short conclusion.

## Forecast audit plan

Reuse the quant-validation earlier-origin candidate and its frozen information rules. Verify that every historical forecast excludes the event's as-yet-unpublished GBV. Retain a letter-close/oracle-input comparison separately to measure the cost of unavailable GBV, never as a pre-event strategy.

Report matching-row n, bias, MAE and RMSE in W1 (2023Q1 onward) and W2 (2024Q1 onward), plus missing rows. W2 is nested. Compare the frozen candidate with persistence and direct guide-growth benchmarks on identical rows. No model-selection search. The existing promotion rule remains: lower RMSE versus both baselines in both windows, MAE no worse, and lower paired MSE after every year deletion. Publish failures.

Measure guide forecast error against the issued guide, and revenue forecast error against revenue separately. Where sufficient data exists, decompose guide error into GBV-input, conversion and cushion effects using an exact symmetric/Shapley decomposition over the three factors. Report covariance contributions so correlated risks are not presented as independent. Ex-post quantities are explanatory diagnostics, not features available before the event. If fields are missing, report the missing decomposition instead of inventing it.

Variance and sensitivity are the purpose. No new optimized predictor or adopted probability distribution. Any empirical interval describes its actual horizon/sample; sparse four-quarter history does not justify calibrated long-horizon probabilities.

## Event-reaction audit plan

Use the full existing eligible earnings-event universe, not a sample selected for unusually large moves. Preserve exact report dates and event quarter labels. Primary windows are pre-release close to next open (gap) and next open to next close (regular-session leg); also report close-to-close and available +5/+20-day returns separately. Use ABNB and a matched QQQ benchmark, and exact compounding where comparing legs.

Intraday call/release legs require actual timestamped intraday quotes and release/call timestamps. Daily OHLC cannot identify the price move during the call, release-versus-call attribution, wick order, or a stop/target's intraday execution. Inventory and label that coverage. Do not reconstruct imaginary candles from daily high/low or infer event-time ordering.

Primary signal comparisons: (1) first-issued forward revenue-guide midpoint versus pre-event realized-revenue consensus, explicitly a different-object proxy; (2) the guide versus an implied guide benchmark using an explicitly stated, pre-event cushion convention. The second remains a conditional expectation proxy, not an observed forecast of management's guide. Actual matching guide expectations are preferred where observed. Keep vendor families/timestamps separate; do not silently let the new DoltHub rows replace other panels.

For the fixed primary comparison, report Pearson/Spearman correlation and a simple slope with uncertainty, leave-one-event/year sensitivity and counts in each sign group. One parsimonious control with current-quarter revenue surprise may be reported if matched coverage supports it. Primary outcomes are gap and next-session excess return; account for this comparison family and do not interpret isolated unadjusted p-values as discovery. Any extra vendor/cushion thresholds are robustness displays, not a search for a profitable rule.

Separate signals known before release from signals observable only after guidance is published. Event correlations are descriptive associations with simultaneous earnings news, not established causal laws. No strategy promotion without a pre-event signal, positive net-after-assumed-cost results on both windows, robustness to event/year deletion and sufficient qualifying events. If fewer than six qualifying events in either window, label the strategy underpowered. Explicit costs are sensitivity assumptions, not observed borrow/option prices.

## Delivery rules

The four-quarter model exposes lagged GBV, lambda, cushion, revenue, guide, dated expectations and break-even conversion/GBV. Q3's already-issued guide is an observed comparison; do not forecast an unknown Q3 guide. Q2 requires a clearly labeled Q1 2027 GBV input and explicit conversion, not inherited revenue growth. Preserve shared-input lineage with Krishang where present.

If the evidence cannot establish a forecast or trading edge, the completed workbook and two-pager must say so and present conditional event scenarios and falsifiers. An empirically unsupported bearish target, probability or call-leg claim is omitted rather than fabricated. Models, tests, source files, artifacts and notes are written only to new paths. The parent owns any necessary harness registration/scoring and final publication review.
