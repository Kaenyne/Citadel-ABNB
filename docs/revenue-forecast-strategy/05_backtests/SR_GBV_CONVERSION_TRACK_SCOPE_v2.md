# Our track: lagged GBV conversion to revenue and guidance

15 September 2026. User correction to the four-quarter scope package. This note supersedes the proposed ownership, input construction and required cost integration in `SR_FOUR_QUARTER_SCOPE_v1.md` and `SR_QUARTER_SUBMISSION_READINESS_v1.md`. Their Q3 2026 through Q2 2027 maximum forecast horizon remains.

## Correct objective and ownership

Our track forecasts quarterly revenue and management's forward revenue guidance using lagged GBV and seasonal conversion. Its objective is to test whether this provides more accurate levels and more informative expectations comparisons than Street forecasts. That superiority is a hypothesis to establish, not a conclusion assumed in the build.

Krishang owns the separate nights/ADR/take-rate/FX component approach described by the user. Its outputs can be displayed as a comparator. Rebuilding those components or integrating the detailed bottom-up cost model is not a prerequisite for completing our conversion track.

## Governing equations

`B[t] = (2/3) * GBV[t-1] + (1/3) * GBV[t-2]`

`Revenue_hat[t] = seasonal_lambda[t] * B[t]`

`Guide_hat[t] = Revenue_hat[t] / (1 + assumed_guidance_cushion[t])`

B is a weighted lagged-GBV predictor, not a measured stock of guaranteed future revenue. Lambda is the aggregate seasonal conversion coefficient, not the commission take rate. The retained weights are predictive coefficients, not identified physical booking-cohort shares.

Reported-USD GBV and the historical conversion calibration already reflect currency and booking/accounting effects. Do not multiply a fresh take rate or generic FX factor onto this result. A separately identified incremental change requires its own compatible treatment. RNPL can motivate conversion/timing scenarios or a test for a conversion break; it does not automatically authorize another cancellation haircut.

## Four-quarter coverage

| Target | Inputs to weighted GBV | Work in this track |
|---|---|---|
| Q3 2026 | Printed Q2 and Q1 2026 GBV | Revenue-level conversion estimate; Q3 guidance is already known |
| Q4 2026 | Forecast Q3 and printed Q2 2026 GBV | Primary forward revenue/guide estimate |
| Q1 2027 | Forecast Q4 and Q3 2026 GBV | Subsequent revenue/guide estimate |
| Q2 2027 | Forecast Q1 2027 and Q4 2026 GBV | Extend the explicit conversion calculation; replace the inherited-growth fallback in a new version |

The essential new input for Q2 is a documented **Q1 GBV level or scenario**, not a mandatory rebuild of nights and ADR. Current L4's Q3/Q4 GBV cases were imported from component assumptions; that lineage must remain explicit. If our GBV inputs come from Krishang, the two approaches share input uncertainty and cannot be described as fully independent forecasts. Direct GBV proxies and component-derived GBV comparisons can be evaluated separately.

## Workbook and visual priorities

For each quarter show: lagged GBV inputs and their information dates; weighted base B; seasonal lambda and its historical behavior; modeled revenue; assumed guidance cushion; modeled guide; comparable dated Street forecasts; and forecast sensitivities.

The key comparison can also be inverted: `Street-implied lambda = Street revenue / B`, conditional on the same GBV base. Show what conversion or GBV level would reconcile our estimate with Street, then test whether the difference is economically and statistically meaningful. Use guide expectations separately; converting revenue consensus into an implied guide requires a visible cushion assumption.

Primary charts: seasonal conversion history; GBV-to-revenue-to-guide bridge; our levels versus comparable Street and Krishang outputs; and GBV/conversion/cushion sensitivity. Costs, full financial statements, H2 2027 and 2028 are outside this track's required build. Nights-guidance language remains a separate event observation or companion forecast; the conversion equation does not produce it by itself.

## Accuracy boundary

L3 supports retaining the fixed-weight operating benchmark because free-weight fitting failed its promotion hurdle. That comparison is not a demonstration of superiority to Street. Historical letter-close evaluations use just-published GBV; a preannouncement trade additionally requires forecasting unprinted GBV. The earlier-origin candidate did not pass both-window promotion. A forecast disagreement is not itself a measured accuracy advantage.

Street consensus records show analyst outputs, not every analyst's internal methodology. Describe Krishang's approach as the user-specified comparison; do not claim all Street analysts use it without evidence.

## Completion and RESUME

Scope clarification complete for the existing four-quarter package, with a bounded independent evidence review by chart_auditor. No model values, workbook, code, registrations or tests changed. Continue with a four-quarter **GBV conversion** implementation and Excel, document GBV input provenance, explicitly add Q2 revenue/guide coverage, and evaluate matched forecast accuracy at the information origin relevant to the trade. Keep Krishang's component model separate and show a reconciliation only as a comparison.
