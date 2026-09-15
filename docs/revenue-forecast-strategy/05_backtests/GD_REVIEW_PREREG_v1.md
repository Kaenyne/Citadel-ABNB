# GD-REVIEW — methodological challenge and bounded diagnostic preregistration

15 September 2026. Independent reviewer: chart_auditor. Written after reading `WORKBOARD_GBV_DECISION_0915_v1.md` and before inspecting new horizon/Street results or executing any new diagnostic. Existing L3/L4/GE/joint results are already known; none is an untouched holdout. Own code/data: `gbv_decision_0915_v1/review_v1/`. No optimized alternative, feature search or new event-return mining.

## Correct question and prior-evidence interpretation

A reduced-form aggregate forecast can be useful without recovering actual reservation cohorts. Missing physical booking-to-fee data blocks physical cohort/RNPL claims, not admissibility of a GBV forecasting equation. Conversely, a coherent accounting story or large revenue-versus-GBV levels correlation does not establish incremental forecasting information beyond seasonality, scale and growth.

L3's matched free/fixed OLS ratios of 1.1654 / 1.0155 test the extra estimated lag weight. They do not reject the retained operational fixed kernel. L3 admits just-printed GBV at letter close, and its coefficient policy differs from the retained K0 policy; its $54–57M fixed-OLS error cannot be transferred directly to forecasts made before that print. L4 confirms integration and conditional scenario arithmetic, not new statistical accuracy or an adopted trade.

The earlier GE fixed candidate has pre-event guide RMSE $63.445M / $63.696M on W1/W2 n12/10, versus direct guide-growth $74.331M / $60.834M. Those results are mixed, not uniformly useless. Its same-origin oracle-GBV guide RMSE of approximately $36.37M / $38.70M identifies a possible input-improvement route but is not an achievable guarantee. The newer joint candidate improves next-guide RMSE about14% /17% versus fixed on n11/10; that favorable result remains visible despite failed deletion robustness. Its poor physical-cohort precision is a separate finding.

## Frozen falsifications and acceptance interpretation

1. **Incremental forecasting information.** Use only the accepted joint and fixed rules. At each origin p release and target p+2/p+3/p+4, compare on identical rows with both direct issued-guide growth and revenue-growth plus common cushion. Direct guide-growth may use the latest p+1 guide actually issued at the origin; its year-ago guide anchor must also have been issued. Revenue-growth anchors and latest-growth inputs must already be printed. This is the principal practical falsification of a levels/seasonality-only story. No random shuffling of nonstationary levels is added.
2. **Information timing and training.** Independently reconstruct every source date, future GBV status and trained quarter. Poison unavailable actuals, target guides and future consensus to verify forecast invariance; keep positive controls showing known inputs matter. A same-release conditional revenue forecast must not be relabelled pre-event guidance skill. All live points use the actual common cutoff and all eligible prior history, not only a retrospective W1 subset.
3. **Horizon specificity.** Each horizon has its own sample and verdict. Longer-horizon W1/W2 rows may be identical after the training requirement; explicitly report overlap and independent target-year counts. Do not borrow next-guide errors or bands for the full Q3 2026–Q2 2027 strip. Recursively forecast missing GBV from the frozen rule; at horizons up to four quarters, verify the appropriate year-ago base is already observed rather than using a newly realized future value.
4. **Baseline fairness.** Common score rows are the intersection of candidate and required comparators, with all original abstentions retained. Show native coverage separately. No benchmark chosen because its realized errors are conveniently large. Published guidance plus cushion is an advantaged post-guide revenue benchmark, not an admissible forecast of that already-issued guide. Frozen-harness ratios lacking baseline-vintage matching do not decide promotion.
5. **Research gate, not proof.** Apply the parent's frozen promotion rule exactly, including both strong baselines, n, deletions and the paired90% interval against guide growth. A failed gate does not prove uselessness. A pass remains a reused-data research recommendation, not confirmatory family-wise statistical proof across two models, three horizons and nested windows. Do not treat all those comparisons as independent replications or retrospectively relax a gate.
6. **Street objects and provenance.** Revenue consensus forecasts eventual revenue; compare that target directly when assessing same-object accuracy. Dividing consensus by a common cushion produces an assumed guide comparator. The same divisor cancels in relative model/Street disagreement, so it creates no independent guide-expectation observation. Keep DoltHub's explicit inherited vendor family, original as-of dates and capture/revision provenance. No future snapshot fills an unavailable origin. Preserve favorable or contradictory evidence and distinguish a model difference from a tradable expectations edge.
7. **Variance and stock relevance.** Known/projected GBV contribution dollars are model exposures, not observed booking shares. Component covariance must be retained; low total error may coexist with uncertain decomposition. Do not label error SD, near-fit spread, oracle error or resampled estimates as calibrated next-event probabilities. Existing event studies retain their multiplicity and daily-price limits; no return-mining extension is authorized by this review.

## One added diagnostic, specified before execution

Using only the new frozen per-origin predictions and unavailable perfect-future-GBV diagnostic, define, separately for each model/horizon/window on the same complete rows:

`input_component = predicted_guide - oracle_GBV_guide`

`remaining_component = oracle_GBV_guide - issued_guide`

Their sum equals the raw guide forecast error. Independently publish n, component mean/RMS, total RMSE and sample variance, the cross moment and covariance, and reconcile both identities:

`MSE(error) = E(input²) + E(remaining²) + 2 E(input×remaining)`

`Var(error) = Var(input) + Var(remaining) + 2 Cov(input, remaining)`.

This is an algebraic fixed-parameter counterfactual diagnostic, not causal attribution or a unique physical decomposition. The remaining component combines conversion, cushion, misspecification and their interactions. Do not report diagonal terms as additive percentages of loss, or claim perfect GBV must improve each event or each sample. If the oracle replacement does not retain the origin's exact fitted parameters/cushion, this diagnostic is unavailable until that incompatibility is disclosed. No additional fit or random model search is needed.

## Feasible remedies to evaluate, not presumed winners

By2 October: a versioned common-origin forecast/consensus sheet; a reproducible Q3 GBV input sensitivity and break-even level; a dated original-source audit of any proposed GBV proxy; and distinct next-guide versus two/three-guide-ahead scenarios. A new proxy earns predictive use only with admissible historical vintages, matched GBV-target evaluation and forecast-level improvement on fixed origins. A direct PMS sample could test field availability and population selection, but purchasing a broad cohort dataset or rebuilding physical survival before submission is not a prerequisite for using a reduced-form forecast and is unlikely to create an honest long historical validation instantly.

If oracle headroom is small or unstable, better booking inputs alone cannot solve the problem; review conversion/cushion/benchmark behavior before spending on data. If oracle headroom is material, a small, predefined source pilot is more decision-useful than another unconstrained lag-weight search. A prospective frozen prediction ledger is useful immediately, while its future outcomes cannot be claimed as validation available before the deadline. A pivot to fees, RNPL, geography or another stock-pitch pillar requires its own comparative evidence; GBV failing a gate does not make the replacement true.

## RESUME

After horizon and Street outputs are frozen, audit numeric identities, common origins, source admission and live points; run only the specified error/covariance diagnostic in a new output directory. Deliver separate engineering, statistical, physical-identification and strategy verdicts. Recommend central role, supporting role or pivot from the full accumulated evidence rather than the latest joint-model failure alone.
