# GBV decision audit — retain the tool, change the pitch claim

15 September 2026. Scope: the Q3 2026–Q2 2027 track, with Q3 guidance already issued and three unknown guides remaining. User-requested extended audit by a quant researcher, source/Street auditor and independent reviewer, with parent integration, an additional timing-repair experiment and visual explanation. This report concerns forecasting guidance and its trade relevance. It introduces no 2028 forecast, DCF or stock-price target.

**Recommendation: retain GBV conversion as a supporting forecast and scenario tool; pivot the central pitch away from an asserted precise booking-cohort/RNPL edge. Begin the Excel decision model now. The evidence does not yet justify a submission claiming that this model predicts a below-expectations guide and a corresponding stock decline.** A wholesale switch to the bottom-up model is also premature: its strongest relevant results have their own unresolved vintage and identification problems.

The work supports three different statements with different strength. Booking carry is economically real. Aggregate GBV forecasts have useful, conditional predictive evidence. Precise cohort conversion and a reliable guidance-surprise trade are not established. Confusing those statements caused the earlier conversation to swing too far between acceptance and rejection.

## What “joint cohort” actually means

Imagine a table with booking quarters down the rows and revenue-recognition quarters across the columns. Each cell would contain the Airbnb fees eventually recognized from one booking quarter in one revenue quarter. A truly observed table would need reservation-level booking dates, stay dates, values, fees and cancellation histories. We do not have a representative current corporate table of those observations.

The model instead constructs a **conditional allocation** from quarterly GBV and revenue. It estimates the timing weights and four seasonal multipliers together. The same allocation then answers two accounting questions: what booking quarters contribute to this revenue quarter, and where one booking quarter's allocated fees are recognized. Those two views must have different denominators; revenue share is not booking survival. “Joint” denotes that consistency, not a newly observed cohort dataset.

For target quarter t, the main rules are:

`Fixed: R[t] = lambda[season(t)] × ((2/3)G[t−1] + (1/3)G[t−2])`

`Joint: R[t] = lambda[season(t)] × (w0 G[t] + w1 G[t−1] + w2 G[t−2] + w3 mean(G[t−3],G[t−4]))`

`Expected guide midpoint = expected revenue / (1 + historical guide cushion)`

The fixed rule imposes a zero same-quarter predictor coefficient. It can work as an empirical forecasting approximation, but it cannot be described as proof that guests never book and stay within the same quarter. The joint rule explicitly allows same-quarter activity and an older tail. Its current fitted predictor weights are35.90%,47.29%,16.81%,0.00%; the four seasonal multipliers plus three free normalized weights total seven conversion parameters, versus four seasonal multipliers in fixed. The guide bridge adds one estimated cushion. Neither the weights nor the zero tail are measured reservation shares.

Different timing weights can produce similar revenue predictions because adjacent GBV quarters co-move and the seasonal multipliers compensate. The prior identification analysis found broad admissible cohort allocations and unstable shares. That prevents precise cohort claims, but it does not by itself invalidate an aggregate revenue forecast. The right test for that forecast is chronological performance against competitive baselines.

Reported GBV is also a net aggregate, not an untouched gross origination ledger. Cancellation and alteration treatment, fees, stay timing, mix and exchange rates can enter the effective conversion relationship. A seasonal multiplier is not a pure cancellation-survival probability. Do not infer an RNPL loss by applying an additional blanket haircut to a net amount that may already reflect cancellations.

## Three or four quarters is the correct horizon, but the inputs still become forecasts

The current decision date is15September. The latest company quarter is Q2, published6August. Q3's guide is already public. The three unknown guide targets are Q4 2026, Q1 2027 and Q2 2027, historically tested as p+2,p+3,p+4 from last reported quarter p. Future earnings updates can improve subsequent forecasts, but that information is unavailable to today's trade.

For the current Q4 joint forecast, only17.88% of its predicted dollars multiply already reported GBV; fixed has33.91%. Q1/Q2 2027 use100% projected GBV under the current fitted rules. This is **model input exposure**, not the share of Airbnb revenue already booked. Future stays may already exist while the corporate quarterly GBV needed by our model remains unreported. A shorter trading horizon therefore helps scope the task, but does not turn future inputs into known backlog.

## What the new tests found

The test contract was frozen before execution: preserve the existing joint/fixed specifications, use only information available by each origin, and compare against both direct issued-guide growth and realized revenue-growth with the common cushion. The guide-growth rule extends the growth rate of the latest already-issued guide to the target's year-ago guide. It is a strong, simple competitor that must be beaten before claiming incremental guide information.

Main table: **raw issued-guide-midpoint RMSE, USD millions**, identical model rows within each horizon/window. W1 starts2023Q1; W2 starts2024Q1. Lower is better.

| Future guide announcement | W1/W2 n | Joint | Fixed lag | Guide growth | Revenue growth / cushion |
|---|---:|---:|---:|---:|---:|
| Next |11/10|64.29/63.83|74.59/77.01|59.06/61.31|118.69/124.25|
| Second |10/10|94.61|99.32|98.95|124.33|
| Third |9/9|131.44|117.74|132.46|149.84|

At the next guide, joint improves on fixed but loses on RMSE to simple guide growth. Joint's MAE is lower than guide growth, so the model is not worse under every loss function; its larger misses matter to an earnings trade. The third-guide fixed result initially meets the full declared gate on nine common observations: ratio0.889 versus guide growth, paired90% interval0.773–0.980, and no deletion reversal.

**That favorable restricted finding is retained.** The independent review also identified a selection issue: the common sample inherits the joint model's warm-up abstentions. In a separately preregistered scope check, restoring all quarters that fixed and both simple baselines could forecast gives W1 n12 fixed RMSE159.10 versus guide growth144.57, reversing the comparison. W2 n10 fixed114.36 versus125.70 misses the10% improvement threshold. Neither model earns broad promotion at any of the three horizons on its own eligible history.

The gate requires n≥8 in both windows, at least10% lower RMSE than both simple baselines, no individual year/quarter reversal, and a90% paired year-bootstrap ratio upper bound below1 versus guide growth. These are demanding claim criteria, not a mathematical definition of usefulness. W2 is nested within W1; at the longer common horizons the two windows are identical. There are only three or four target-year clusters. Two thousand bootstrap draws do not create two thousand independent quarters. These are reused historical data across multiple methods and horizons, not a fresh holdout.

Canonical sources: `GD_HORIZON_RESULTS_v1.md`, `GD_HORIZON_ELIGIBILITY_ADDENDUM_v1.md`, and the `horizon_v1/results_v2/` and `eligibility_audit_v1/` outputs.

## A positive finding against the available Street series

The original prior-release origins have no eligible future-quarter DoltHub consensus rows. The vendor's current/next-quarter labels roll after earnings; that is benchmark absence, not a model defeat. A separate calendar origin was specified before calculating its performance: start(p+2) minus16 days, matching15September today. The corporate information set is checked to be unchanged before reusing any earlier release point.

On the common11/10 observations, **joint eventual-revenue RMSE57.44/56.23 is lower than DoltHub89.92/92.50**. Ratios0.639/0.608 survive the year/quarter deletion checks, and90% paired upper bounds are0.888/0.767. This is meaningful favorable evidence for the aggregate revenue approach. It must not be erased because another aspect of the model failed.

It remains qualified. The14 selected historical snapshots lack individual archival equality/first-availability proof; the limited prior source audit certified other snapshot cells. The bounded public verification query failed, and its exact receipt is retained. Missing certification is not proof of leakage, but it prevents describing this as a fully certified Street backtest. The comparator is the held DoltHub family, not all sell-side analysts or a renamed licensed vendor. Farther-quarter consensus remains unavailable.

Revenue consensus is also not an observed forecast of the guide management will issue. Dividing it by our cushion creates an assumed guide proxy. On that comparison joint has favorable point RMSE, but weaker uncertainty results; the simple guide-growth baseline is still better. Joint's proxy-surprise sign accuracy does not beat the corresponding majority-sign baseline. A revenue improvement therefore does not automatically become a directionally reliable guide call.

Canonical sources: `GD_STREET_RESULTS_v1.md`, `street_v1/results_v3/`, `common_v1/`, and `sensitivity_v1/`.

## Current estimates do not establish the proposed short

The following are conditional research guide points, USD millions, calculated15September with company information through6August. The shared trailing-eight arithmetic-mean revenue/guide cushion is1.856743%. No calibrated live prediction interval is attached.

| Target | Joint | Fixed lag | Guide growth | Revenue growth / cushion |
|---|---:|---:|---:|---:|
|Q4 2026|3,185.25|3,160.55|3,133.92|3,178.40|
|Q1 2027|3,052.13|3,070.96|3,040.71|3,063.98|
|Q2 2027|4,078.02|4,126.14|4,159.14|4,128.03|

The held13September Q4 eventual-revenue consensus is3,200m. Comparing the joint guide3,185.25m directly to it looks negative by14.75m, but compares different objects. The same-cushion implied guide is3,141.67m, making the joint difference **+43.58m** and fixed **+18.88m**. Neither is a measured investor expectation of management's guide.

Those modest positive differences do not prove a long trade either. They are smaller than the models' historical next-guide RMSE, which is a scale comparison rather than a calibrated live confidence interval. The shared cushion cancels in the relative model-versus-Street comparison; changing it equally on both sides cannot manufacture a new signal. Management's actual future guidance policy and the market's expected policy remain separate uncertainties. This is another reason to expose the cushion in Excel instead of fitting a new policy until this historical sample produces the preferred sign.

## RNPL: a supported mechanism, an unmeasured magnitude

Airbnb's Q2 filing explains that GBV records the booking irrespective of collection timing, while revenue is recognized at check-in. It also states RNPL bookings have higher cancellation rates than historically paid bookings and that adoption can weaken the historical association among GBV, revenue and cash. That supports investigating conversion risk; it supplies no incremental loss estimate for our next guide. Payment delay alone is a cash-timing effect. [Airbnb Q2 2026 Form10-Q](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm).

The separately specified post-2025Q3 diagnostic contains only four outcomes. Production forecasts mostly **underpredicted** issued guides: joint bias−77.51m in four of four quarters, fixed−48.80m in three of four. This does not prove RNPL has no effect, but it contradicts claiming that our observed overprediction already demonstrates RNPL-driven revenue destruction. Oracle residuals have different signs, so attribution cannot ignore input/conversion error covariance.

An identified RNPL cancellation loss needs payment-plan status, booking and cancellation timestamps, booking/stay values and appropriate comparison cohorts, plus reconciliation to reported net GBV. Changes in an unpaid cash stock, availability flips or review counts do not supply that causal estimate by themselves.

## Which gaps are worth solving?

Perfect future GBV, substituted only as an unavailable diagnostic while holding fitted conversion/cushion fixed, lowers fixed-model common W2 guide RMSE from77.01 to48.81m at the next guide and117.74 to47.19m at the third. Joint also improves. This identifies possible input headroom, not a guarantee any available alternative-data feature can deliver it. The oracle combines future information with a held model and cannot register as a forecast.

Error components offset. For example, next-guide joint W2 variance is8615.45m² from the production-minus-oracle component plus3067.08m² from the oracle residual minus7745.42m² from twice their covariance, leaving3937.11m² total. It would be wrong to add separate uncertainties independently or label them causal shares of failure.

We tested one concrete repair rather than proposing it abstractly: use the PR60 flight statistic at the calendar information date, with actual commit gating, the same timing for training and a single bounded slope. Only two of nine evaluation features were current-quarter readings. Joint RMSE worsened67.12→80.30m; fixed improved78.81→75.68m but missed the10% hurdle and remained worse than guide growth63.51m. Both remedy gates fail. The source's current availability does not reverse that result. Details and the non-earnings-origin harness change request are in `GD_CALENDAR_FLIGHT_RESULTS_v1.md`.

| Gap | What could solve it | What does not solve it |
|---|---|---|
| Unreported future GBV | A historically dated, relevant booking/demand signal, tested on frozen common origins | Adding more lags to the same small corporate history |
| Precise physical cohorts | Representative booking/stay/value/cancellation records or validated cohort aggregates | Relabeling fitted coefficients as observed shares |
| RNPL incremental cancellations | Payment-plan-linked outcomes with controls and reconciliation to net GBV | Treating deferred collection as lost revenue |
| Revenue-to-guide behavior | Explicit cushion sensitivity and independently supported guidance-policy information | Choosing a cushion after seeing historical errors |
| Market guide expectation | Dated analyst previews/surveys that explicitly predict the issued guide | Renaming eventual-revenue consensus |
| Source chronology | Exact vintage/commit checks on the14 used snapshots and original feature archives | A date label in a current reconstructed CSV |
| Earnings-call price response | Accurate release/call clocks and permitted intraday ABNB/market observations | Daily candles described as isolated call legs |
| Model uncertainty | Honest small-sample diagnostics and prospective frozen forecasts | More resampling presented as more independent evidence |

## A pivot must earn its place too

The alternative-pillar audit used the latest closure notes and PR60 corrections, not favorable superseded summaries.

| Alternative | Latest evidence relevant to the pitch | Decision today |
|---|---|---|
| Bottom-up reviews / nights | PR60 fresh-vintage W2 ratio0.757 misses its0.75 gate; the prior fixed vintage wedge does not survive the refresh | Potential corroboration; do not assume a validated substitute |
| ADR / mix | Hotel/macro ADR relationships can fit descriptively, but use realized mix/FX and retrospective weights; the hotel panel measures no actual Airbnb hotel demand | Needs an as-of rebuild before a forecast-edge claim |
| Fee pass-through | Engineering controls close, but the inspected fee workflow has no live result wave and no measured pass-through estimate | A concrete collection opportunity, not a completed catalyst estimate |
| RNPL / unpaid stock | Incremental cancellation magnitude is unidentified; cash accounting does not identify revenue impairment | Conditional risk scenario only |
| Regional / FX | Regional reconciliation can balance while O-D currency observations and eligible guide forecasts remain absent | Sensitivity, not a central empirical replacement |
| Consensus revision / price response | Existing revision and event tests fail their prespecified strength/stability criteria; primary event multiplicity results do not establish a robust guide-to-price mapping | Keep event context; no calibrated price claim |

Source notes: `WPK_reviews-index-2023-vintage.md`, `L3_ADR_HOTEL_RESULTS.md`, `L3_FEE_AUDIT_CLOSE_v3.md`, `ALPHA_F_RNPL.md`, `X_REGIONAL_KERNEL_OD_FX.md`, `ALPHA_B2_TERM_STRUCTURE_V2_RESULTS.md`, `GE_EVENT_RESULTS_v1.md`. L3 closed a conversion-method choice and L4 closed integration. Neither completion certificate independently establishes a trade edge. The earlier feature catalogue's missing required comparator is a coverage problem, not proof that every listed feature empirically failed.

## Closing plan for the submission

**Move to Excel now, with the uncertainty visible.** The research workbook should contain reported inputs and publication dates; projected GBV by quarter; fixed and joint revenue bridges; the simple guide-growth challenger; the separate revenue-to-guide cushion; actual-object consensus comparisons; independent Q4 GBV/cushion sensitivities; historical errors and source status. Keep Krishang's nights×ADR×take-rate×FX work as a separate cross-check so both tracks reveal where their conclusions agree or diverge. Do not average models merely to conceal disagreement or label model spread a probability interval.

The remaining targeted work should run alongside that workbook, with a firm decision point:

| Proposed completion | Deliverable | Acceptance / stop condition |
|---|---|---|
|18 September|One common-date expectations ledger and archival proof for the selected Street rows, where obtainable|Exact vendor, quarter, publication and revision timing; otherwise retain the conditional label. Separate actual guide expectations from revenue consensus.|
|22 September|One bounded input/guide-policy pilot supported by genuinely new usable information|Predefine fields, dates and model; same-origin comparison to the frozen GBV carry rule and both simple baselines. If a relevant dated input cannot be obtained, stop model expansion.|
|22 September|Central-claim decision with the bottom-up track|Require a current documented disagreement, a measured operating-to-guide bridge, a catalyst and explicit disconfirmation. Do not force a short sign.|
|25 September|Complete Excel and a two-page draft using only supported claims|Audit every central figure to source and formula; show downside/upside scenarios and what would change the view.|
|Before2 October|Final team review and submission preparation|If no directional edge passes the evidence standard, reframe or change the pitch rather than present an unvalidated precise guide miss.|

These are proposed research milestones, not scheduled automations. No new earnings outcome arrives before the stated submission deadline; the next expected print is5November (a project planning date, not a newly verified company announcement). Lock prospective forecasts now for later learning, but do not imply that waiting for that print can validate the preliminary memo in time.

## Reproducibility, scope and visual pack

Accepted package paths are under `gbv_decision_0915_v1/`. The independent reviewer verified horizon formulas, same-origin comparisons, publication-date adversarial checks, the Street tables, the candidate-specific coverage sensitivity, the flight repair and the prepared registration. Main horizon and supplemental outputs reproduce exactly; the flight run reproduces all12 files byte-for-byte. Independent numerical checks establish implementation correctness, not additional economic observations or a competition outcome.

Registration adds421 rows across18 research objects, including18 LIVE points; overlapping windows are deliberately retained. Both unchanged frozen scorers return0 and agree on328 score rows. All292 earlier scores and126 prior protected files remain unchanged. Oracles and non-earnings historical origins are excluded from registration. The frozen scorer omits origin in its baseline join and uses raw midpoint errors; the separate integer-interval supplement and harness change request address the repo's rounding convention without editing frozen code. Use the final completion note to locate that supplement and its independent review.

Canonical review: `GD_REVIEW_RESULTS_v2.md`. The visual pack is `outputs/gbv-decision-20260915-v4/GBV_decision_visuals.pdf`, with five individual PNGs and a source manifest: model mechanics, guide accuracy/coverage, Street versus guide tests, the forward strip/known-input exposure, and the input diagnostic/failed remedy. Graphics were visually inspected; earlier render versions remain preserved.

## RESUME

The requested decision audit is complete in substance: retain aggregate GBV as a useful supporting tool and conditional challenger, cease presenting fitted cohorts or RNPL impairment as established observations, and pivot the central pitch toward a documented guidance-expectation disagreement supported by measured current evidence. Start the Excel model with separate object/date/cushion fields and both forecasting tracks. The highest-value remaining research is targeted provenance, genuinely new timely inputs and guide expectations. Another unrestricted search over cohort weights on the same quarters is not justified. No long or short trade, exact price reaction, or superior replacement approach has been validated by this audit.
