# L3 — presentation claims and consumption rules

Lead · 2026-09-14 · supplement to the original accepted L3 validation. This is a claim contract for L4 and the quant task, not a workbook, valuation or investment memo. Final audit acceptance is recorded separately in `review_acceptance_v1.json` and the rotated review notes.

## Conversion claims

The tested specification is `R_t = lambda_s [w G_(t-1) + (1-w) G_(t-2)]`, with revenue and GBV in USD millions, four seasonal coefficients and one shared weight. The descriptive fit uses 22 lag-complete quarters, 2021Q1–2026Q2, and five parameters.

| Quantity | Full-sample descriptive estimate |
|---|---:|
| Shared first-lag coefficient w | 0.7864784808 |
| Q1 lambda | 12.93191114% |
| Q2 lambda | 13.22423248% |
| Q3 lambda | 17.30274407% |
| Q4 lambda | 12.11155832% |

**Presentation-safe:** “Allowing the lag weight to vary did not improve revenue prediction in both chronological evaluation windows. We retain the fixed two-thirds/one-third operating benchmark.” Free-weight / identically fitted fixed-weight USD RMSE is **1.165407390 in W1 (n=14)** and **1.015512948 in W2 (n=10)**. Ratios above one are worse. W2 is nested within W1, so these are not two independent replications. The matched fixed OLS comparator is distinct from the inherited operational seasonal estimation policy; neither its all-sample coefficients nor the descriptive free-weight coefficients have replaced that policy.

**Presentation-safe:** “The five fitted coefficients describe an aggregate seasonal relationship; they do not identify booking cohorts.” Parameter uncertainty and year sensitivity are joint diagnostics based on only six calendar-year blocks, including partial 2026. Do not combine marginal endpoints into a probability-calibrated forecast range. The model weight is not a measured fraction of reservations or revenue: its first-lag arithmetic contribution is `w G1 / [w G1 + (1-w) G2]`. Lambda is not the commission take rate. The original bootstrap and year-omission evidence remain in the frozen conversion bundle.

Historical guide-date evaluation used information available after the associated letter, including the just-printed GBV. It is not a genuine preannouncement investment test. Future revenue uncertainty also includes unobserved GBV and any guide-cushion assumption. New preannouncement testing and investment robustness belong to the quant task.

## Source precision and accounting claims

**Presentation-safe:** “We checked four conversion-related KPI fields across all 24 source quarters, retaining source precision and availability distinctions.” This covers GBV, GAAP revenue, booked units and ADR only. Original IPO-quarter text was unavailable, and unresolved discrepancies remain. Current retrieval of an original URL is not proof of historically archived bytes. The full discrepancy and source ledgers carry those qualifications; this is not certification of every column of the wide KPI panel.

**Presentation-safe:** “Using more precise Q1 and Q2 2026 GBV changes one current-quarter fixed-lambda calculation by about $4.659 million.” The original [Q1 filing](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000014/abnb-20260331.htm) reports $29,187 million; the [Q2 filing](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm) reports $27,247 million. Against the frozen rounded inputs, the weighted GBV difference is `(2/3)(47)+(1/3)(-13) = 27` million. Holding the named inherited Q3 coefficient **0.172548908953** fixed gives **$4.658820541731 million**. This is one arithmetic sensitivity, not a revised forecast, historical performance gain or refit-materiality estimate. Revenue-input discrepancies and coefficient re-estimation effects remain outside this calculation.

**Presentation-safe:** “Booking, payment, currency fixing and revenue recognition have different clocks.” The [FY2025 10-K](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm), Note 2, qualifies long stays of at least 28 nights as monthly contracts: first-month fees at initial check-in, later months at monthly anniversaries. Current-period recognition-origin shares and a booking cohort's eventual recognition allocation have different denominators. Neither fitted weights nor unpaid booking stocks identify those physical flows.

RNPL remains within reported GBV. A booking-share or unpaid-stock proxy cannot supply the required share of surviving recognized-fee exposure. Any cancellation adjustment must reconcile with cancellations already recorded in the baseline. No additional demand or cancellation adjustment is justified merely by labeling a booking RNPL.

Historical revenue hedge losses of $19 million for Q2 2026 and $34 million for H1 are observed disclosures in Note 6 of the Q2 filing. They do not identify the future quarter's hedge contribution. AOCI's expected next-twelve-month release and derivative notional do not supply that missing quarterly amount. Monetary remeasurement, revenue hedges, constant-reference factors and management's YoY FX contribution are different objects.

## Downstream use

The original 1,187-row bundle is preserved exactly. The supplement classifies 576 conditional exhibits, 603 descriptive rows, four comparators and four unavailable rows; none of those original rows is a directly applicable L4 adapter or a newly observed ABNB operating input. Observed primary source facts in the new ledgers remain usable as source evidence. “Conditional” permits a labeled scenario exhibit, not automatic model adoption.

For FX, choose one compatible route: replacement level `T`, increment `T-B`, or ratio `T/B`; these represent the same scenario and must not be added together. `T/R0` is a reference-level diagnostic and cannot multiply the reported-USD baseline. Reported GBV already includes booking-period currency translation. The original aggregate ratios do not certify an operating-only multiplier or preserved hedge dollars. Safe application through L4's inspected interface requires an explicitly reconciled operating ratio and target-quarter hedge H before applying `(R-H) k_operating + H`; H alone does not establish ratio compatibility. The code checks supplied identities and reconciliation fields; upstream evidence must establish the operating-only basis and root quote provenance.

ADR totals already contain their component assumptions and fee-mechanics K. Components are not separate incremental revenue adjustments; residual pricing is not an identified causal estimate. Hotel indices remain comparators, NCLH transfer remains a failed study, and fee-panel theta remains unavailable. Missing estimates are not zeros.

**Presentation-safe:** “Revenue expectations and expected management guidance are different forecast objects.” Comparing an implied guide directly with revenue consensus does not measure a guide surprise. A common-cushion conversion is a conditional construction, not observed guide consensus. L4 owns its forecast, workbook, valuation, memo and registrations; the quant task owns new expectation and investment tests.

## RESUME

Use these claims together with the final lead handoff, package source manifests, independent review closures and original conversion acceptance receipt. Preserve every conditional/unavailable qualifier when moving a claim into presentation material. Further data or a new application decision requires a new reviewed version; this supplement does not change the model, produce an investment stance or authorize public publication.
