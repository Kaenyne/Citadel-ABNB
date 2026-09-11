# RNPL: conversion, cancellation timing, and the Q3/Q4 2026 bridge

Research date: September 10, 2026. This is a separate review of the RNPL component; existing forecasts and workbooks have not been edited. Numerical scenarios below are sensitivities, not fitted estimates.

## What the evidence supports

RNPL can raise initial booking conversion, lower the eventual survival of each booking, and bring bookings forward. These can all happen while increasing completed nights. The investable question is whether current forecasts overestimate the net benefit or underestimate the cancellation tail as rollout matures.

Airbnb's reported Nights and Seats Booked is a transaction-period metric: bookings created in a quarter less cancellations and alterations occurring in that quarter, including cancellations of older bookings. It is not stays completed that quarter. A Q2 booking canceled in Q3 raises Q2 nights and lowers Q3 nights. Revenue is a separate check-in-period outcome. Source: [Q2 2026 10-Q, key business metrics](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm).

There is a material attribution error in the existing H1/H2 bridge: Q1's approximately 3 percentage points of nights growth and 4 points of GBV growth refer to the combined effect of RNPL, redesigned cancellation policies, and simplified fees. They are not a disclosed RNPL-only or US-only contribution. Source: [Q1 2026 call, printed page 6](https://s26.q4cdn.com/656283129/files/doc_financials/2026/q1/Airbnb-Q1-26-Earnings-Call-Transcript.pdf). Therefore subtracting all 3 points for a US RNPL anniversary is not an evidence-based base case.

## Rollout and measurement anchors

| Period | Evidence | Modeling implication |
|---|---|---|
| Beginning Q3 2025 | Management dates launch to beginning Q3; US guests, domestic stays, flexible/moderate policies; approximately 70% take-up when offered | Eligibility and adoption are different denominators; 70% is not platform penetration |
| August 14, 2025 | Public US launch announcement | Announcement date is not the experimental treatment start |
| Q4 2025 call | Aggregate cancellation rate described as roughly 16% historically versus 17%; higher within RNPL; management says tested cohorts remain net beneficial through check-in and cancellation curves track tests | An approximate calibration constraint, not a nightly cohort survival dataset or an unrecognized future charge |
| February 17, 2026 | Global domestic and international availability announced, subject to eligible listings | International rollout anniversary differs from US anniversary |
| Q1 2026 | Roughly 20% of global GBV attributed to RNPL; longer booking windows and higher-priced home mix | GBV share is not nights share; backlog share can differ again |
| Q2/July 2026 | Over 20% of Q2 GBV; management says July expanded eligible booking types | Q3 simultaneously has a US lap and fresh treatment expansion |

Sources: [Q3 2025 call, printed page 7](https://s26.q4cdn.com/656283129/files/doc_financials/2025/q3/CORRECTED-TRANSCRIPT_-Airbnb-Inc-ABNB-US-Q3-2025-Earnings-Call-6-November-2025-5_00-PM-ET.pdf); [US announcement](https://news.airbnb.com/reserve-now-pay-later); [Q4 2025 call, printed page 11](https://s26.q4cdn.com/656283129/files/doc_financials/2025/q4/Airbnb-Q4-25-Earnings-Call-Transcript.pdf); [global announcement](https://news.airbnb.com/reserve-now-pay-later-is-now-available-worldwide); Q1 call above; [Q2 2026 call transcript hosted by Roic](https://www.roic.ai/quote/ABNB:US/transcripts/2026-year/2-quarter). The Q2 shareholder letter also confirms expansion to additional listings and countries: [SEC-filed letter](https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm).

No quarterly platform-wide eligibility percentage, night-weighted RNPL cancellation series, or cancellation-lag distribution was established from these disclosures. Do not interpolate these as observed data.

## Calculations possible now

### 1. Platform cancellation sensitivity

For comparable, fully matured booking cohorts:

`surviving_nights_growth = (1 + gross_nights_growth) * (1 - current_cancellation_rate) / (1 - prior_cancellation_rate) - 1`

If gross nights grow 10%, a night-weighted rate changing from 16% to 17% gives surviving nights growth of 8.69%; 16% to 18% gives 7.38%. If rates are 17% in both years, growth remains 10%.

These are illustrations. Management's approximate cancellation statistic does not establish this night-weighted cohort denominator. Nor is the prelaunch historical 16% rate automatically the right Q3/Q4 2025 comparison. This formula is not a direct calculation of reported quarterly nights, since cancellations cross booking quarters.

### 2. Infer an RNPL cohort differential conditionally

With consistent night-weighted denominators and matched non-RNPL risk:

`platform_cancellation_rate = p * c_RNPL + (1-p) * c_control`

If RNPL alone explains a 1-point platform increase, its excess cancellation probability is `0.01 / p`. At RNPL nights shares of 15%, 20%, and 25%, this implies 6.67, 5.00, and 4.00 percentage points, respectively. These are conditional scenarios, not observed cohort estimates. Policy changes, traveler selection, and booking lead times can explain part of the aggregate change.

Do not combine the Q4 cancellation-rate comment and Q1 GBV penetration into a same-period causal estimate. The public anchors differ in vintage and denominator.

### 3. Convert GBV penetration into nights and backlog exposure

If `s` is RNPL share of GBV and `r` is RNPL ADR divided by non-RNPL ADR, on consistent definitions:

`p_nights = s / [r*(1-s) + s]`

An illustrative 20% GBV share with 25% higher RNPL ADR means 16.67% of nights. If these bookings remain outstanding 1.5 times as long, a stationary approximation gives:

`p_backlog = p_nights * 1.5 / [(1-p_nights) + p_nights*1.5] = 23.08%`

This is why a modest share of booking flow can be a larger share of unconsumed inventory. Actual backlog requires cohort aggregation because seasonality and cancellations violate the stationary approximation. Net disclosed GBV also need not match a gross booking-flow denominator.

## Highest-value empirical work

### A. Follow reservation cohorts to payment, cancellation, and stay

Best data: a property manager/channel manager reservation-event panel with stable anonymized reservation ID; channel; booking date; stay dates; original and revised nights; cancellation date and canceled nights; lead guest origin; original cancellation policy; listing characteristics; RNPL eligibility and actual choice if available; payment due date/status if available; and replacement bookings. Host payout date is not guest payment date.

Measure night-weighted survival separately by booking age and days to check-in/payment. Estimate probability of a future cancellation conditional on the reservation still being live at the forecast date. A raw ultimate cancellation rate overstates remaining risk for older survivors. Handle right censoring: newly booked Q4 stays have not yet had a full cancellation opportunity. Separate guest cancellation, host cancellation, payment failure, and alterations.

Use the staggered rollout as a cohort-specific difference-in-differences/event study. During the US-only phase, compare eligible US-origin domestic bookings with comparable not-yet-eligible bookings within the same destination, policy, listing, stay week, and lead-time band. US destination alone is not treatment assignment. Check pretrends, keep stable policy cohorts, and isolate the October 2025 policy/fee changes. The February and July expansions offer additional cohorts, but eliminate some earlier controls. RNPL users self-select, so treatment availability estimates the rollout effect more credibly than a raw users/nonusers comparison.

Report both total rollout effect and lead-time-standardized survival. Controlling for lead time alone can remove part of the effect RNPL actually causes. Country demand, World Cup dates, FX, policy transitions, and channel mix also need consideration. Show results by original adoption cohort to distinguish poorer newly eligible mix from deterioration within an established cohort.

Track rebooking: canceled nights at one property may be replaced on Airbnb. For reported net bookings, count the cancellation and the replacement in their respective transaction periods. For completed stays, distinguish original-booking survival from final occupied nights. A property manager panel cannot fully observe platform-wide guest rebooking elsewhere, so its inferred net platform loss has a coverage limit.

### B. Use calendar vintages as a proxy, not a cancellation count

The local `data/processed/booking_curve_daily.csv` and `booking_curves_by_market.csv` contain unavailable-date rates. Existing research documents one snapshot per market; these files cannot measure cancellation or booking survival. Host blocks are included.

With repeated listing-by-stay-date observations, measure unavailable-to-available transitions, subsequent refilling, and remaining vacancy at check-in. Match identical days-to-arrival and seasonal dates in both years; retain listing-level identifiers and calendar horizon checks. Daily observations are materially better than quarterly snapshots. Even daily calendars miss cancellations immediately rebooked and cannot always separate host blocks or bookings from another channel. Without payment/eligibility labels, this is an exposure-associated reopening proxy.

Reviews and official stayed-night series can cross-check realized demand, with controls for review propensity, length of stay, guest count, geography, and channel coverage. They do not identify canceled reservation cohorts. Regional NA-versus-Europe aggregate growth alone does not isolate RNPL.

### C. Use cash balances to constrain payment timing only

Unearned fees and funds held are affected by when guests pay. Weak balances can be consistent with unchanged eventual stay conversion. They can help constrain payment-delay/exposure scenarios if fee mix, seasonality, and balances are modeled, but cannot identify a cancellation rate by themselves. Likewise, the existing fixed GBV-lag revenue conversion can break simply because booking lead times lengthen; a revenue residual is not automatically canceled nights.

## How to put the result into Q3 and Q4

For reported nights, build a booking-month by cancellation-month matrix:

`N_q = G_q - sum_b C_(b,q) + signed_alterations_q`

`G_q` is gross nights booked in q; `C_(b,q)` is nights from booking cohort b canceled during q. Estimate cancellation timing separately by rollout cohort. Include future within-quarter gross bookings and cancellations as well as the opening backlog. For stayed nights and revenue, build a separate booking-month by stay-month matrix.

For a snapshot-based forecast, incremental cancellation risk from a live cohort is:

`live_RNPL_nights * (revised conditional probability of cancellation during q - probability already assumed)`

Sum across cohorts, then add revisions to gross booking uplift, timing, alterations, and replacement bookings. For an explicit RNPL/no-RNPL comparison, apply the model to both 2025 and 2026 before calculating growth. A raw cancellation increase is not automatically an RNPL effect or an incremental surprise.

The 2025 reported denominators are Q3 133.6 million and Q4 121.9 million Nights and Seats Booked, from the Q2 2026 shareholder-letter quarterly summary. Holding those fixed:

| Extra net lost nights versus the forecast, millions | Q3 growth haircut, points | Q4 growth haircut, points |
|---|---:|---:|
| 0.5 | 0.374 | 0.410 |
| 1.0 | 0.749 | 0.820 |
| 2.0 | 1.497 | 1.641 |
| 3.0 | 2.246 | 2.461 |

Thus Q3 10% becomes approximately 9.25% if the evidence supports one million additional net lost nights beyond that forecast. An illustrative 40 million live RNPL nights times a 5-point upward revision to their probability of cancellation during Q3 gives two million cancellations, or 1.50 points before replacement-booking offsets. Neither the 40 million exposure nor the 5-point revision has been measured here.

Q3 has competing forces: old cohorts' cancellation tail and US lap versus global ramp and July eligibility expansion. Q4 may receive the cancellation tail of July's new cohorts and lapse a stronger 2025 product contribution, but the timing must be estimated, not assumed. A permanent product-driven level increase stops contributing y/y once fully lapped even if conversion never deteriorates; that is distinct from cancellation drag. Fresh expansion can offset the lap.

## Recommended interpretation

Keep the roughly 10% forecast as the starting point until its exact target and embedded RNPL assumptions are established. If it already predicts reported net nights using post-rollout history, a generic cancellation haircut risks double counting. If it extrapolates gross reservations or live backlog with pre-RNPL survival, the cohort adjustment is necessary. If it predicts completed stays, it needs a transaction-timing bridge before comparison with reported nights guidance.

The public information supports a real timing/conversion mechanism and useful sensitivities. It does not yet establish a 1.5–3 point incremental H2 drag. The most useful next dataset is the reservation-event panel, with a first deliverable of conditional cancellation curves, night-weighted rollout exposure, and the quarter-by-quarter cancellation matrix.

