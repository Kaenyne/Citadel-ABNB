# GE-JOINT-QUANT — joint cohort build and pitch eligibility

Quant subagent ·15 September2026 ·`codex/submission-readiness-v1`. Additive implementation in `analysis/src/forecast_methods/gbv_joint_cohort_v1/quant_v1/`; data in the corresponding `data/processed/forecast_methods/` package. Preregistered before execution; timing correction recorded separately before first fit.

## Verdict

**Built, but not eligible for a current corporate booking-cohort headline or live model promotion.** Direct current booking/recognition/fee/cancellation data are unavailable. Separately, the parsimonious inferred decomposition fails the preregistered precision and deletion tests by wide margins. The early-origin guide predictor improves point RMSE but loses that advantage after deleting2024, and paired uncertainty includes no improvement. This does not prove actual cohorts vary excessively; it proves the held data/model do not pin their composition tightly enough to support the proposed percentages. Low variation conditional on fixed weights is not identification.

## What ran

Exact commands are in the package README. `run.py` completed with exit0 and all200 prespecified year-cluster bootstrap draws in both windows; `diagnostics.py` completed with exit0 and2,000 paired evaluation resamples. Eleven core economic/edge/leakage tests passed via `python -m unittest discover -s analysis/src/forecast_methods/gbv_joint_cohort_v1/quant_v1 -p test_quant.py -v`. Independent reviewer separately tests actual APIs and stored outputs. A full deterministic rebuild is being checked in a new `rebuild_v1` directory and will receive its own validation receipt; this note does not predeclare that unfinished check passed. No registry writes or scoring by this subagent; parent coordinates these separately.

Inputs are the frozen KPI panel/publication calendar, K2 processed historical shares, and the PR60 historical-commit EUROCONTROL QTD75 panel. The data audit found no direct current cohort panel. Input/source/output SHA-256 manifests accompany each run; core existing-input hashes were unchanged. The flight addendum uses exact UTC timestamps from the data agent's17-row commit-lineage reconciliation, conservatively excluding same-day commits at date-only company origins. Raw flight mirror and40-state/day completeness were not independently recertified locally.

## One matrix, two views

For a booking quarter b and recognition quarter t, A[b,t] is an **assumed effective allocation of fee revenue**. Backward share is A divided by the sum of allocated revenue in recognition quarter t. The matrix also shows A divided by actual corporate revenue, retaining the unallocated residual. Effective forward conversion is that same A divided by reported GBV in booking quarter b. Each row/column therefore reconciles without mixing denominators.

Airbnb reported GBV is net of cancellation/alteration effects occurring in the reporting period; it does not isolate original gross bookings. Effective fee-per-net-GBV is not a completion or survival probability. No additional generic cancellation haircut is applied. Ordinary and long-term recognition, actual fees, cohort cancellations and repricing remain unobserved. Recent booking rows are right-censored; older historical rows are left-censored by the sample. The primary tail covers lags3–4 only; sensitivity specifications cover lag3 only and lags3–8. Exposure beyond each finite support remains unknown.

The primary model estimates3 independent pooled weights and4 seasonal scales (7 parameters). The current, lag1, lag2 and average(lag3,lag4) exposures have fitted W1 weights40.43%,0.89%,58.68%,0%; W2 weights43.59%,0%,56.41%,0%. These are exposure coefficients, not actual booking-cohort percentages. Boundary solutions do not establish that lag1 or older bookings contribute zero. The four same-season scales use a two-annual-observation EWM half-life.

## Identification and estimation uncertainty

| Test, all retrospective | W1 | W2 | Prespecified requirement |
|---|---:|---:|---|
| Corporate quarters |14|10|W1 begins2023Q1; W2 begins2024Q1|
| Independent calendar-year clusters, last year partial |4|3|Disclose limited independence|
| Near-fit shapes on1773 evaluated shapes |219|103|No implied probability over shapes|
| Greedy count separated by at least10pp somewhere |39|21|Diagnostic count, not all possible solutions|
| Largest near-fit share range across quarters/groups |60.84pp|52.25pp|At most10pp|
| Largest90% bootstrap mean-season share interval |75.93pp|97.19pp|At most10pp|
| Largest leave-one-year mean-season share shift |26.58pp|50.33pp|At most5pp|
| Optimized full-sample relative RMSE |0.755%|0.578%|Descriptive fit, not promotion|

Near-fit means relative RMSE within0.25 percentage points of the minimum on a0.05 simplex grid, plus continuous optimum and fixed-kernel reference. These are conditional sensitivity ranges. The bootstrap resamples years, preserves chronological EWM base weights with multiplicity, rejects draws missing a season, and refits3 deterministic optimizer starts. Its intervals condition on this model family and the few held years; they are not measured reservation-population intervals.

One concrete joint comparison is2025Q4. Among the W1 near-fit shapes, same-quarter revenue attribution spans8.83–61.72% and its matching effective forward fee conversion spans1.20–8.40% of2025Q4 reported GBV. W2 permits17.83–66.95% and2.43–9.12%. These pairs come from the same dollar identity; they must not be reinterpreted as cancellation rates. The uncertainty is large even inside the smaller7-parameter class, so this conclusion does not depend on the saturated LP.

The flexible LP uses36 coefficients (4seasons×9lags) with only14/10 corporate observations. Main fit tolerance is±1%, with0.5/2% and lag3/4 tail cuts retained. By season the9-column design has only3–4 observations in W1 and2–3 in W2. Same-quarter share widths are10.75–68.70pp across W1 target cells and42.54–88.11pp in W2; several other group bounds span0–100%. These deliberately flexible bounds illustrate nonidentification under weak assumptions. They are not statistical confidence intervals or a sufficient standalone reason to reject parsimonious prediction.

K2 stress restrictions operate on column shares, not beta weights. Some combinations of old Melbourne share bounds, geographic-season mapping, seasonal coefficient stability and1% aggregate fit are infeasible. This rejects those combined assumptions; it does not reveal which assumption is wrong or validate a current share. Every feasible and failed case remains in `stale_k2_conditional_bounds.csv`.

## Temporal variation versus model uncertainty

Holding the optimized shape fixed can produce calm-looking histories. For Q4, W1 same-quarter conditional share averages36.22%, with sample SD0.789pp across only3quarters. W2 averages39.61%, SD0.755pp across2quarters. W1 same-quarter effective fee conversion averages5.072%, SD0.019pp; W2 averages5.486%, SD0.028pp. These low SDs are conditional accounting outputs. They do not resolve the much wider uncertainty about the shape itself.

All four seasons and both metrics are in `conditional_temporal_variance.csv`, with sample denominator n−1 and n in every cell. The older-tail coefficient field is explicitly a sum of coefficients applied to distinct booking-quarter denominators, not one pooled cohort conversion. Detailed per-lag matrix rows are authoritative for forward interpretation.

Allocation uncertainty largely offsets inside the total. Under W1 near-fit shapes, the conditional2026Q4 same-quarter share spans8.83–61.72%, while the total revenue sensitivity range is only$44.16m and the implied guide range$43.36m. W2 ranges are$29.34m and$28.80m. These are model sensitivity ranges, not predictive intervals and not new live forecast recommendations. Under the unweighted W1 near-fit grid, individual contribution variances sum to466,638m², cross-covariances contribute−466,532m², leaving total variance106.36m². The paired sum reconciles; adding independent contribution bands would be wrong. Grid shapes have no assigned probability, so this variance is a sensitivity summary, not a probabilistic risk forecast.

## Early-origin guide forecast race

Target t is forecast at the t−2 earnings release, before the t−1 earnings release issues its guide. For example, an August Q2 origin predicts the November Q3 release's Q4 guide. Both t−1 and t GBV are unknown and forecast recursively from seasonal year-ago GBV times the latest already-published GBV growth. The oracle subsequently substitutes both realized GBV values only for an explicitly nontradable diagnostic. Same-event target guide never enters training or cushion estimation.

| Primary model, paired origins | W1 | W2 |
|---|---:|---:|
| n |11|10|
| Candidate revenue RMSE ($m) |57.443|56.231|
| Fixed-kernel revenue RMSE ($m) |78.236|80.951|
| Candidate guide RMSE ($m) |64.287|63.831|
| Fixed-kernel guide RMSE ($m) |74.592|77.012|
| Guide RMSE ratio |0.862|0.829|
|90% paired year-bootstrap ratio interval |0.543–1.574|0.604–1.125|
| Guide ratio after deleting2024 |1.064 (n7)|1.030 (n6)|

The point10% improvement threshold passes, but no-deletion-reversal fails. Deleting2024Q2 also reverses W1 (ratio1.022,n10). Both paired intervals include1, and there are only4/3 evaluation-year clusters. No established guide edge can be claimed.

The first3 W1 origins are excluded because the primary lag3–4 model has only5/6/7 complete training rows before the minimum8; W1 reported n is11, not14. Tail3 has n12/10 and guide ratios0.857/0.863. The longer lag3–8 tail has only7 common origins in each window and cannot meet the minimum8-origin promotion gate. Its missing early history is not imputed.

Both candidate and baseline use the same arithmetic mean of the last8 completed actual/issued-guide ratios minus1, known at the origin. This is internally paired but differs from the median cushion used by earlier GE work; do not claim identical forecasts or directly attribute all differences from old package scores to cohort modeling. Parameter counts are7 for the revenue shape+scales and8 including the shared guide cushion; growth carry-forward is an observed-input rule, not an additional fitted regression coefficient.

## Actual PR60 integration

The one-slope flight ablation forecasts the change from latest known GBV growth using the gap between an eligible historical EUROCONTROL flight growth measure and company GBV growth. Only actual stored commit timestamps at/before the conservative origin cutoff enter; target outcomes must already be published for training. Minimum6 training pairs, one coefficient constrained to[−2,2], maximum2-quarter feature age. Missing eligibility remains in the skip file. This is a demand input to unknown GBV, never evidence of the cohort split.

There are8 common eligible evaluation origins in both windows. Candidate guide RMSE worsens from$69.610m without flights to$73.504m with flights; the no-flight fixed baseline is$67.581m on those same8 origins. Flight candidate/baseline ratio is1.088. The inherited PR60 feature therefore does not qualify for inclusion under this frozen ablation. Current corporate cohort measurement remains unavailable irrespective of this forecast failure.

## Pitch use and next step

The pitch may say the aggregate conversion approach has an explicit same-quarter research challenger and that several very different booking allocations explain similar totals. It should not claim a measured current split, a measured cancellation/RNPL conversion rate, an established forecasting edge, or a new price target from this package. Keep the live fixed-kernel benchmark unchanged until the challenger survives a broader independent validation.

The next useful acquisition is an actual booking-month×recognition-month matrix with consistent original booking value, fee bridge, cancellations/modifications, region/channel and as-of vintages. A matched PMS sample can make the inverse problem informative; repeated availability/review/flight aggregates cannot manufacture the missing booking event. Analyze coverage and fee mapping before extrapolating a professional-manager panel to corporate revenue. The model infrastructure here will accept credible restrictions on the same dollar matrix when available.

## Harness change requests

None from this subagent. Parent may register the rejected but valid early-origin primary replay under a new method, preserving all failure labels and original protected files. Full-sample allocations, oracle values, and conditional sensitivity ranges are not historical forecasts for registration. Current live guide/price recommendations are unchanged.

## RESUME

Finish the independent reviewer and deterministic rebuild receipts, then let the parent deliver the decision visuals and paired registration/scoring. The central finding is not that true cohorts are known to be unstable; direct measurement is missing, inferred shares are weakly identified, and the smaller predictive challenger is promising on point RMSE but fails robustness. Preserve the complete joint dollar matrix, residuals, finite-tail/censoring flags, unknown physical-survival labels, source limits and every failed test when moving to a future directly observed sample.
