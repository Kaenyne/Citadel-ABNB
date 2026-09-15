# GD-HORIZON — what GBV can support across the next three guides

Quant subagent ·15September2026 ·`codex/submission-readiness-v1`. New code/data package `gbv_decision_0915_v1/horizon_v1/`. Workboard specification and both supplementary conventions were written before their respective calculations. This is an extended audit on previously inspected history, not a new untouched holdout.

## Verdict

**Retain GBV as an auditable forecasting/scenario tool and research challenger; the held tests do not support making the joint-cohort method the pitch's proven forecasting edge.** The joint model fails the demanding promotion gate at each of the next three unissued-guide horizons. The fixed model has a favorable result at the longest horizon on the original common9-row sample, which is preserved. That result does not survive the fixed model's own broader eligible W1 history. Physical cohort identification is a separate question and is not used to reject a reduced-form forecast. Street-relative and executable-return conclusions belong to the separate source/event packages.

## What ran and integrity

Accepted outputs are `horizon_v1/results_v2/`. Initial `results_v1/` is retained: v2 corrects oracle-only availability metadata, recording the later actual-publication `knowable_from`, `point_in_time_eligible=False` and the separate coefficient-information date. Production points and numerical results are unchanged.

The exact commands are in the package README. `run.py --out .../results_v2` and `run.py --out .../rebuild_v2` both exit0. All17 result files and manifests are byte-identical. Four source hashes, including accepted core code, remain unchanged. `validate.py` passes790 saved arithmetic/origin checks, confirms the earlier accepted p+2 replay, reconciles covariance, and poisons all future actuals/issued guides at one real origin across all three horizons without moving a production point. Core manifest SHA-256: `c631affb255e6e6655b73af2b260190a690da4836395931cd31217ade4df17ac`.

The calendar arm and standalone-eligibility audit each exit0 and reproduce all4 output files and manifests exactly. Their receipts are under `horizon_v1/validation_v1/`. No original source or existing forecast is overwritten; no registry/scorer writes are performed by this quant agent. Parent owns controlled registration and scoring.

## Frozen models and timing

Let p be the latest reported company quarter. At its earnings release, actuals for p and the guide for p+1 are available. The three unknown-guide targets are p+2, p+3 and p+4: the next one, two and three guide announcements. Historical targets are2023Q1–2026Q2 for W1 and2024Q1–2026Q2 for W2. The current unknown strip is2026Q4,2027Q1,2027Q2;2026Q3 guidance is already issued.

- **Joint:** unchanged accepted pooled current/lag1/lag2/average(lag3,lag4) exposures, fitted on all complete published history, plus4 seasonal EWM conversion scales. Minimum8 complete rows/all4 seasons,3 fixed optimizer starts. Seven parameters for the revenue model,8 including cushion for guide.
- **Fixed:** unchanged2/3 lag1 plus1/3 lag2 GBV and same-season EWM scale. Four seasonal-model parameters,5 including cushion. The p+3/p+4 cases forecast whichever lagged GBV values are still unprinted.
- **Direct-guide-growth:** target year-ago issued guide multiplied by the latest valid, already-issued guide year-on-year growth. It is allowed to use the p+1 guide issued at the origin. No estimated regression coefficient. Its revenue column is a guide-times-common-cushion proxy, explicitly labelled.
- **Revenue-growth:** target year-ago published revenue multiplied by latest published revenue growth, divided by the shared cushion. No estimated revenue-model coefficient; one cushion estimate for guide.

Unknown GBV always follows the accepted carry rule: seasonal year-ago GBV times latest published GBV year-on-year growth, recursively where needed. Every production input is available at the origin. The arithmetic mean of the last8 completed actual/issued-guide ratios minus1 supplies the common cushion. Missing prerequisites abstain and remain listed. Oracle rows swap future GBV for eventual actual GBV while holding the fitted model/cushion fixed; they are explicitly unavailable forecasts, not eligible performance leaders.

## Main common-sample comparison

For the primary four-model ranking, all four production predictors must be available on the same target/origin. The table gives **guide midpoint RMSE, USD millions**, with n for each window. The longer-horizon W1/W2 samples are identical, not independent replications.

| Future guide announcement | Window | n | Joint | Fixed GBV | Direct guide growth | Revenue growth/cushion |
|---|---|---:|---:|---:|---:|---:|
| Next: p+2 |W1|11|64.29|74.59|**59.06**|118.69|
| Next: p+2 |W2|10|63.83|77.01|**61.31**|124.25|
| Second: p+3 |W1|10|**94.61**|99.32|98.95|124.33|
| Second: p+3 |W2|10|**94.61**|99.32|98.95|124.33|
| Third: p+4 |W1|9|131.44|**117.74**|132.46|149.84|
| Third: p+4 |W2|9|131.44|**117.74**|132.46|149.84|

The next-guide joint model beats the old fixed GBV comparator but does not beat the stronger direct-guide-growth baseline. Against direct guide growth, joint RMSE ratios are1.088(W1)/1.041(W2), with90% paired year-cluster intervals0.744–1.519/0.714–1.305. At p+3, joint's ratio0.956 represents only4.4% improvement and the interval0.827–1.300 includes no advantage. At p+4, joint's ratio0.992 is effectively flat versus direct guide growth, with interval0.652–1.215. These fail the frozen gate requiring at least10% improvement against both simple baselines in both windows, no deletion reversal and an upper interval below1 versus direct guide growth.

The original fixed p+4 finding is favorable: ratio0.889 versus direct guide growth and0.786 versus revenue growth, with direct-guide-growth interval0.773–0.980. Its largest deletion ratio against guide growth is0.973; against revenue growth0.869. Thus the original common9-row gate **passes**. This is an empirical result worth retaining, not something to discard because actual booking cohorts are unidentified.

`scores_common.csv` also reports MAE, bias, sample error SD, worst absolute miss and relative RMSE; `scores_all_available.csv` describes each model's available rows separately. For perspective, common-sample W2 guide error SD grows from62.75m to96.09m to135.20m for joint, and79.12m to103.22m to124.55m for fixed. These are historical sample statistics, not next-event probability intervals. There are only3–4 independent evaluation-year clusters; the2000 resamples do not create more independent history.

## Why the favorable longest-horizon finding is conditional

The original common-four sample inherits joint's training warmup. The fixed predictor and simple baselines are available earlier. Before computing any result on those extra rows, `GD_HORIZON_ELIGIBILITY_ADDENDUM_v1.md` froze a standalone-eligibility sensitivity: require each candidate and both simple baselines, without requiring the other candidate. All points, windows, thresholds, bootstrap rules and deletion rules remain unchanged; no refit or date tuning.

For fixed p+4, W1 restores2023Q3,2023Q4 and2024Q1; W2 restores2024Q1. Results:

| Fixed p+4 scope | Window | n | Fixed RMSE ($m) | Guide-growth RMSE ($m) | Revenue-growth RMSE ($m) | Fixed/guide ratio |90% ratio interval |
|---|---|---:|---:|---:|---:|---:|---|
| Original common-four sample |W1/W2, identical|9|117.74|132.46|149.84|0.889|0.773–0.980|
| Fixed's own eligible history |W1|12|159.10|144.57|153.30|1.101|0.851–1.293|
| Fixed's own eligible history |W2|10|114.36|125.70|143.93|0.910|0.823–0.980|

The shorter-sample positive finding is real conditional on that sample, but it does not justify an unqualified broad-window promotion. W1 reverses against both simple baselines; W2's9.0% advantage against guide growth misses the prespecified10% magnitude hurdle. Under standalone eligibility, neither candidate passes all requirements at any of the three horizons. The audit's purpose is to show sensitivity to available history, not to claim that the favorable9-row result never happened.

## How much of the predictor is actually known?

The following is **model-dollar exposure to already reported GBV**, not the percentage of revenue already booked and not an observed cohort contribution. It measures how much of a prediction multiplies a reported input, with the remainder multiplying projected GBV.

| Horizon | Historical common W2 n | Joint known-input share, mean | Fixed known-input share, mean |
|---|---:|---:|---:|
|p+2|10|12.00%|32.54%|
|p+3|10|1.76%|0.00%|
|p+4|9|0.97%|0.00%|

At the15September live cutoff, Q4 known-input exposure is17.88% for joint and33.91% for fixed. Both models' Q1/Q2 2027 exposures are0% under the currently fitted zero older-tail weight and fixed-lag specification. This does not mean no future stays have been booked; the corporate GBV needed by these algebraic predictors has not yet been published. Longer horizons depend heavily on the GBV forecast rule, rather than mechanically reading already-reported reservations into revenue.

## Room for better GBV inputs, with covariance preserved

Holding each fitted model/cushion fixed, perfect future GBV reduces common W2 guide RMSE:

| Horizon | n | Joint production → oracle ($m) | Fixed production → oracle ($m) |
|---|---:|---:|---:|
|p+2|10|63.83 →54.56|77.01 →48.81|
|p+3|10|94.61 →54.50|99.32 →45.73|
|p+4|9|131.44 →55.95|117.74 →47.19|

This identifies an input-quality opportunity, not an achievable improvement guarantee. It also shows that more cohort parameters are not automatically better: the simple fixed converter has the smaller oracle error on these samples. A new GBV input still needs a proper as-of backtest, and the previously tested PR60 flight feature did not qualify under its initial frozen ablation.

The error identity is `production−actual = (production−oracle) + (oracle−actual)`. The first component is associated with unprinted GBV inputs; the second retains conversion/cushion residuals. These are paired arithmetic components, not independently causal losses. In W2 p+2 joint guide errors, their variances are8615.45m² and3067.08m², with twice covariance−7745.42m², leaving total3937.11m². The full identity reconciles to numerical precision. Summing separate error variances without covariance would materially overstate total variance, and a partial improvement in one input need not translate one-for-one into total RMSE.

## Current strip, point estimates only

Truthful calculation cutoff15September2026; last company publication6August2026, Q2. USD millions, guide midpoint:

| Target | Joint | Fixed GBV | Direct guide growth | Revenue growth/cushion |
|---|---:|---:|---:|---:|
|2026Q4|3,185.25|3,160.55|3,133.92|3,178.40|
|2027Q1|3,052.13|3,070.96|3,040.71|3,063.98|
|2027Q2|4,078.02|4,126.14|4,159.14|4,128.03|

The Q4 joint/fixed points reproduce the earlier bounded live snapshot. No future guide dates are invented where the held calendar lacks them. No predictive interval, price target or thesis direction is implied. These are forecasts from explicit rules, not direct measurements of reservations, future management statements, or what investors expect.

## Separate calendar information dates for Street matching

The source agent found that consensus quarter slots roll after earnings, leaving the exact release-day arm uncovered for future guide targets. The parent preregistered a separate information date: start(p+2) minus16calendar days, which gives15September for today's Q4 decision. `calendar_arm.py` implements that rule and independently verifies the entire eligible company-actual and issued-guide sets before reusing a release point. All17 historical/live origin groups have identical information sets; all237 rows are reused with explicit new/source/company-release dates. Original release-day points remain intact. No consensus input enters this operation and it is not a Street-performance result; the source agent performs that comparison separately. Missing snapshots are not filled from later dates.

## Decision implication and next work

For the coming Q4 guide, the reduced-form GBV forecast has not established incremental accuracy over simply extending the latest issued-guide growth. The joint-cohort weights have already failed identification/stability tests, and the longest-horizon fixed-model success is sensitive to which eligible history is included. Those facts support a **supporting role** for the GBV forecast and a disciplined challenge to its input assumptions, rather than another round of fitting cohort weights to the same small corporate ledger.

The highest-value prospective quantitative addition is a genuinely informative, historically timestamped GBV input for the unprinted quarters, tested against the existing carry rule and both strong simple baselines. Preserve the current frozen forecasts for prospective scoring. Credible booking-date/stay-date/cancellation/fee observations would additionally support a physical RNPL story, but they are not required merely to test total-revenue forecasting. Any pivot to fee, regional, bottom-up or other pitch evidence should be judged on its own demonstrated edge; this package does not assume another approach is superior because GBV fails a gate.

## Harness change requests

No requested changes to frozen validators/scorers. Parent may register clearly labelled new historical and LIVE forecasts while retaining failed gates. Never register oracle values, actual-outcome fields, or model-exposure shares as forecasts of actual reservation cohorts. Oracle source dates and eligibility are explicit in accepted v2.

## RESUME

Parent combines these horizon results with the independently audited Street/calendar arm and alternative-pillar review, preserving the favorable common9-row fixed finding and its broader-sample failure. Keep GBV available as an interpretable challenger/scenario tool, stop treating inferred cohort precision as established, and prioritize genuinely new timely GBV/expectations evidence or prospective validation before making a central trade-edge claim. All main and supplemental outputs are reproducible; no further fitting is required for this bounded package.
