# Joint cohort model — economic contract and interpretation

15 September 2026. Written before new model results. Implements the user's request to consolidate booking-quarter shares and subsequent conversion, using available repository/PR 60 data, then decide whether the findings are reliable enough for the pitch.

## Correct objective

The decision is whether the joint model provides defensible quantitative evidence for upcoming quarterly guidance. It is not required to support a short. Scope remains Q3 2026 through Q2 2027 at most. PR 60 is already merged in this worktree: merge commit `dd3aa1440b152b46fdee8c094875d178b802d74a`, ancestor of HEAD `2dfe0c2a1852181a246f4b6b9072e05e844d52d5`.

## One matrix, two views

Let A[b,t] denote fee dollars recognized in quarter t from reservations originally booked in quarter b. Revenue composition is A[b,t] divided by total recognized revenue in t. Forward fee conversion is A[b,t] divided by the compatible original value of booking cohort b. They share a numerator but have different denominators. They must reconcile to the same dollar matrix.

The conceptual economic bridge is original bookings × scheduling into future periods × survival/changes × applicable fee recognition. Aggregate financials typically observe products of these quantities, not their individual values. Original gross booking-cohort value is not the same as reported GBV, which nets cancellations and alterations in their reporting quarter. When the code uses reported GBV as denominator, label the coefficient **effective fee dollars per reported booking dollar**, never measured survival or cancellation probability.

Same-quarter reservations are explicit in the candidate. Older cohorts remain explicit; a finite 3–8-lag tail is not all possible older bookings. Long stays can recognize fees at later monthly anniversaries. Unobserved tail and recognition details cannot be eliminated by reassigning their shares without disclosure.

## Three distinct questions

1. **Measurement:** Does the evidence observe booking and recognition/value together for a relevant population? A fitted allocation cannot pass this gate merely by matching corporate revenue.
2. **Identification and stability:** Do materially different plausible allocations fit the same observed data? Separate variation over quarters, parameter uncertainty, sensitivity to assumptions and sampling error. The quant preregistration sets the numerical pass lines before fitting.
3. **Forecast usefulness:** At actual pre-guide information dates, does the minimal candidate improve guidance forecasts against the existing fixed-lag benchmark in both W1 and W2? Target-quarter GBV is unknown at those dates and must be forecast rather than looked up afterward. Preserve all missing-origin and failed results.

These questions can have different answers. A useful forecast need not establish a physical cohort mechanism. Conversely, plausible cohort shares do not establish a guidance-forecast edge. No reported model result alone validates the stock-return response.

## Variance must follow the decision

For each target quarter, model revenue is the sum of cohort dollar contributions. Its variance equals the sum of component variances plus twice their pairwise covariances. Large offsetting cohort uncertainties can coexist with a less variable total. Never add independent component bands or dismiss a total forecast solely because its decomposition is unstable.

Assess the impact on guidance on the same basis: guide equals revenue divided by one plus the guidance-cushion assumption. Separate a conditional interval with fixed cushion from uncertainty in that cushion. Observed historical sample standard deviation is not automatically a predictive interval. Small samples and selected alternative data must remain visible.

## Decision labels

- **Measured statistic eligible for the pitch:** direct, compatible evidence and representative scope; label its population and date.
- **Model estimate eligible only with qualifications:** identified and stable under preregistered tests; clearly disclose assumptions, uncertainty and how it improves the relevant forecast.
- **Scenario or diagnostic only:** useful for understanding sensitivity but not established as the current corporate split or conversion rate.
- **Exclude from the pitch's evidentiary claims:** fails stability/forecast criteria or lacks the data needed to establish the claimed quantity. Explain whether the reason is high variance, non-identification, leakage or unavailable data.

## RESUME

Quant owns model/preregistration/results, data agent owns actual PR 60 field and vintage admissibility, reviewer owns independent checks, and parent owns final integration and visuals. Do not silently replace the current model. Register genuine forecast replays under a new method where the authoritative harness accepts their timing, including failed candidates, then run both unchanged scorers into new output paths. No new corporate cohort fact should be quoted solely because a model generated it.
