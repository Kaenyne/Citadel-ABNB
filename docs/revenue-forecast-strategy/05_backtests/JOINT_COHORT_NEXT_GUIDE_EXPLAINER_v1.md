# Joint cohort and fixed lag — what the next guide estimates mean

15 September 2026 · parent explanatory continuation of `improvement_0915_theo` · `codex/submission-readiness-v1`

## Decision

Both frozen methods can produce a point estimate of the next Q4 2026 revenue guide. Neither the visual overlap with historical guidance nor the close agreement between today's two estimates establishes precise next-event accuracy or an advantage against the Street. The prior failed robustness/promotion decision remains unchanged.

The earlier conversational recommendation to remove this mechanism from the central pitch needs this distinction: weak identification of booking cohorts does not logically invalidate a statistical forecast of total revenue. The present work has not demonstrated the stronger claim that our measured booking stream lets us reliably anticipate guidance better than contemporaneous Street expectations. The GBV forecasting method remains a research/supporting tool while that claim is unproven.

## The comparable snapshot

These are new calculations dated 15 September 2026 using the last company publication in the frozen panel, 6 August 2026 (Q2). The joint model follows the exact primary historical forecasting rule on all 20 complete published quarters, 2021Q3–2026Q2. It does not reuse W1/W2 retrospective-only sensitivity fits. The fixed rule uses five prior Q4 conversion ratios. Both share the identical GBV projection and guidance adjustment.

| Calculated research estimate, USD millions | Joint | Fixed lag |
|---|---:|---:|
| Q4 revenue | 3,244.389 | 3,219.235 |
| Q4 first-issued revenue-guide midpoint | 3,185.247 | 3,160.552 |
| Shared trailing-eight actual/guide mean cushion | 1.856743% | 1.856743% |

Their guide estimates differ by $24.695m. These are point calculations, not confidence limits. The number of decimal places records arithmetic rather than forecast precision. No live-model adoption, new Street comparison or price target is implied.

The copied historical rules have seven joint revenue parameters plus one guidance cushion, and four fixed seasonal scales plus one cushion. The fixed forecast of one quarter uses its one relevant seasonal scale; its reported n=5 is the number of prior Q4 observations. Joint n=20 is the complete multiseason training panel, with five observations per season. They are not interchangeable sample denominators.

## Fixed lag, in plain English

For Q4, form a predictor from two-thirds of Q3 GBV plus one-third of Q2 GBV, then multiply it by the historically estimated Q4 conversion factor:

`Q4 revenue estimate = Q4 seasonal factor × [(2/3 × Q3 GBV) + (1/3 × Q2 GBV)]`.

The fixed part is the two GBV exposure weights. The seasonal factor is still estimated from published history, with recent annual observations weighted more heavily. In this calculation the factor is 12.040367%.

These weights are not observed percentages of Q4 revenue by booking cohort. The factor is fitted to total revenue, so it can implicitly absorb the usual contribution of same-quarter bookings, timing, fee composition and other recurring relationships. The method has no explicit same-quarter booking component with which to diagnose a changing lead-time or cancellation mix.

## Joint cohort, in plain English

Use the target quarter's GBV, the preceding quarter, two quarters earlier and a finite older tail; estimate how to combine them alongside four seasonal scales. The same fitted dollar matrix can be read as revenue composition by booking quarter or effective fee conversion per reported GBV dollar.

This live fit assigns predictor weights 35.895645% to Q4 GBV, 47.291024% to Q3, 16.813331% to Q2 and zero to the assumed Q1/Q4-prior-year tail, with Q4 scale 12.681513%. These are regression-style exposure weights, not measured reservation shares. The zero tail is a fitted boundary, not proof older bookings contribute no revenue. The previously reported large identification ranges still apply as a warning against a literal cohort interpretation.

Both revenue estimates are divided by `1 + 0.01856743` to estimate the guide, using the observed mean actual-revenue/issued-guide gap over the last eight completed quarters. This is an empirical guidance-policy assumption, not a known management commitment.

## What is actually known before the release?

| GBV input | Status at the calculation cutoff | Value, USD millions |
|---|---|---:|
| Q2 2026 | Reported in frozen company panel | 27,200.000 |
| Q3 2026 | Forecast from latest known year-on-year growth | 26,505.532 |
| Q4 2026 | Forecast from the same growth-carry rule | 23,611.915 |

Both methods need unreported Q3 GBV; the joint model additionally uses projected Q4 GBV. The projected growth is 15.744681%, carried from the latest reported company quarter, not an observed booking pickup reading. This calculation introduces no new September alternative-data signal. Known earlier GBV totals do not provide a matched remaining booking ledger showing which bookings will be recognized in Q4.

The accounting mechanism itself is real. Airbnb reports that GBV is recorded when booked and describes it as a leading indicator of revenue; ordinary stay fee revenue is recognized at check-in, with monthly recognition for long stays. GBV includes host earnings, fees, cleaning fees and taxes and nets cancellations/alterations occurring during the reporting period. These definitions explain both why booking information can help and why a quarterly GBV total is not the same object as a fee-revenue backlog for a particular future quarter. [Airbnb 2025 Form 10-K, Key Business Metrics and Revenue Recognition](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm), accessed 15 September 2026.

Public availability also matters for differentiation: we cannot assume the Street ignores information explicitly disclosed as a leading indicator. The proposed edge requires evidence about the timing, conversion or information content beyond a public total, or a robust demonstration that our aggregate model predicts guide surprises better at matching information dates.

## Reading the historical chart correctly

The chart plots issued company guidance against two model forecasts in revenue levels. It includes no Street forecast. A $60m error is visually small on an axis spanning approximately $2bn–$4bn. Capturing the seasonal peaks and troughs does not establish precision on the smaller guide-versus-expectations gap that the pitch needs.

The historical primary guide RMSE is $64.287m/$63.831m for joint versus $74.592m/$77.012m for fixed on W1 n=11/W2 n=10, with overlapping windows. The joint advantage reverses when 2024 is removed, and paired uncertainty includes no improvement. These RMSE values are historical error scales, not calibrated plus/minus bounds for this next event. Today's approximately $25m model disagreement is smaller than those historical error scales; agreement between two methods sharing inputs is not independent confirmation.

Useful total-revenue prediction and correct physical-cohort measurement are separate requirements. A predictive aggregate model need not identify every booking cohort. A pitch claiming that RNPL bookings will cancel or a specific pre-booked stream will convert less strongly does need direct supporting evidence for that mechanism. The current evidence supports neither a precise physical-cohort percentage nor a promoted Street-relative trading claim.

## What ran and scope

The additive quant runner `analysis/src/forecast_methods/gbv_joint_cohort_v1/next_guide_v1/run.py` imports the unchanged accepted core and emits `points.csv`, GBV status, contribution, training and cushion tables under `data/processed/forecast_methods/gbv_joint_cohort_v1/next_guide_v1/results_v1/`. This is a frozen-rule live calculation, not another optimization search across methods. Parent stages two point-only LIVE guide records through FORMAT 1.1 using `control_v1/register_next_guide_v1.py`; the completion workboard records registration/scorer receipts and the independent review.

## RESUME

Use the $3.185bn joint and $3.161bn fixed estimates only as dated research point calculations. Explain the fixed weights as a predictor and the joint weights as inferred exposures, keeping actual cohort identification and forecast usefulness separate. The central unresolved investment question is whether an advance forecast beats the Street's information-date-matched expectations by enough to matter after forecast uncertainty. That test or compatible direct booking-to-fee data is needed before claiming the proposed edge; no further parameter tuning or price target follows from this clarification.
