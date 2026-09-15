# improvement_0915_theo

Date: 15 September 2026. Owner: Theo's GBV-conversion track.

Purpose: capture improvements identified while discussing the model in plain English, before selecting assumptions or changing code. The objective remains forecasting upcoming quarterly guidance and evaluating its relationship to earnings-event stock moves, through Q2 2027 at most.

## Improvement 1 — Explicit treatment of bookings made and consumed within the target quarter

**Research status: identified / to scope. Not implemented or validated.**

**Documentation status: complete.** Recorded at Theo's request; no model, forecast, workbook or trading conclusion was changed.

### Observation

A guest can book an Airbnb today and check in tomorrow. Revenue in a target quarter can therefore arise both from reservations made earlier and from reservations made within that same quarter.

The current delivered GE model predicts revenue using a weighted combination of the two previous quarters' GBV and a seasonal historical conversion ratio. It has no explicit term for bookings made and consumed in the target quarter, and it does not observe which earlier reservations are scheduled for that quarter.

This does **not** mean it assumes same-quarter revenue is zero. Historical total revenue used to estimate the conversion ratio already includes that activity. Its contribution is absorbed implicitly into the historical relationship between lagged GBV and total revenue. Likewise, the fixed lag weights are predictive coefficients, not measured shares of revenue attributable to booking cohorts.

### Why this matters for our thesis

The model cannot separately tell whether a change in conversion reflects more last-minute bookings, reservations moving between quarters, cancellations, or genuinely incremental completed stays. RNPL could shift when people book without changing when they travel. A timing shift could consequently be mistaken for a change in economic conversion.

This is an identification limitation, not proof that the existing predictor is inaccurate or that a replacement will forecast guidance better.

### Improvement to investigate

Explore whether the evidence supports separating:

1. Reservations already made and scheduled to generate revenue in the target quarter, allowing for cancellations and changes.
2. Reservations expected to be made and consumed during the target quarter.

Prior-quarter aggregate GBV is not itself a measured backlog scheduled for the target quarter. Establish what booking-date, stay-date and cancellation evidence is available at each forecast date before selecting a method or assigning cohort shares.

Review the repository's existing K1/K2, kernel_phi and lead-time research first. The limitation recorded here applies to the current delivered GE model; it is not a claim that no previous research considered same-quarter bookings. Earlier estimates must be reconciled and validated for this use before being reused.

### Safeguards and open questions

- Do not simply add a same-quarter revenue estimate to the current forecast: historical conversion already absorbs that contribution. Recalibrate the relationship to avoid double counting.
- Do not replace the fixed weights with invented booking-cohort percentages. Earlier free-weight fitting failed promotion; a more detailed model must earn its additional complexity.
- Determine whether available data can identify booking cohorts and target-quarter consumption, rather than only aggregate correlations.
- Distinguish what is observable when management issues guidance from what will only become known afterward.
- Test whether this separation improves point-in-time guidance forecasts against the existing benchmark. Pre-register the test and require the repository's two historical windows before claiming improvement.
- Keep any RNPL timing or cancellation mechanism separate from an assumed directional trade. This observation alone establishes neither a weaker guide nor a short thesis.

### Work performed and validation

Recorded the user's observation and reconciled it with the governing equations and limitations in `SR_GBV_CONVERSION_TRACK_SCOPE_v2.md` and the delivered GE model. No numerical experiment ran, no parameters were added, and no forecast was registered. Tests and harness scoring are not applicable to this documentation-only action. No performance claim is made.

## RESUME

Continue the plain-English discussion with Theo before coding. The next issue to examine is how much prior-quarter GBV can actually be attributed to stays in a particular future quarter, and what evidence would distinguish a booking-timing shift from a change in eventual revenue. Preserve Improvement 1 as identified / to scope until data feasibility, methodology and a preregistered validation plan are agreed. Add subsequent discussion notes in new versioned files under the repository's copy-never-overwrite rule.
