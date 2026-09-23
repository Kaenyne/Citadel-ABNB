# Q7 economic bridge — assumptions fixed before sensitivities

2026-09-14 · worker E `/root/test_designer` · no production replacement. Governing parent `CHAIN_PROTOCOL_v1.md` and frozen L4 commit `29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`.

Reconcile all 21 committed annual scenario rows with their component cash costs, EBITDA cap, total addbacks, SBC, operating income, pretax/tax, FCF, cash and share equations. This independently audits equations from existing line items; it does not rebuild the operating forecast. Reconcile the primary FY27 EBITDA valuation lens for each scenario and do not average lenses.

Reference decision date is the inherited snapshot 2026-09-13. Evaluate 2026-12-13, 2027-03-13 and 2027-09-13 (3/6/12 months), plus explicitly out-of-horizon 2027-12-31. Conditional cash/share convention: linearly accrue committed H2 flows between June30 and December31, and committed FY27 flows between December31 and December31. Use actual day-count fractions and no invented quarterly cash-seasonality data. Underlying FY27 EBITDA and multiple stay fixed to isolate this convention; values are not independent price forecasts. Show no-current-price reference181.94 from L4 solely as its dated September4 2026 assumption.

Same-basis operating contrast is own review Q4 revenue less captured LSEG-family revenue, not own guide less revenue consensus. Cases are (i) Q4 only, with zero FY27 earnings persistence; (ii) the same fractional difference applied to Q4 and every FY27 quarter, explicitly an unvalidated persistence scenario. The fractional difference uses own Q4 as denominator, so the counterfactual Q4 level equals captured revenue consensus exactly. No yearly Street consensus is invented.

Cash-cost response eta is0,0.5,1 per incremental revenue dollar, representing fixed cost, partial variable cost and fully offset cash cost. These are stress assumptions, not estimated confidence bounds. Addbacks and AI referral costs retain L4 revenue percentages. For each eta, incremental SBC is either zero (L4 fixed-dollar compensation) or proportional at the respective baseline annual SBC/revenue ratio (alternative cost/dilution stress). Normalized D&A is already included in total addbacks and is not subtracted twice. Tax expense, cash-tax/revenue, capex/revenue and other-working-capital/revenue parameters remain inherited. Change in unearned fees is zero in the central bridge, labeled unestimated rather than an RNPL inference.

No incremental interest, debt, buybacks or customer funds enter the operating contrast. Extra SBC subtracts from operating earnings; SBC-adjusted FCF subtracts it;35% withholding reduces corporate cash;65% issuance divided by the inherited repurchase-price proxy changes shares. Do not capitalize SBC-adjusted FCF and separately deduct the same SBC again. Show reported-FCF and SBC-adjusted metrics separately.

Additional sensitivities: inherited13.5x/16.5x/18.5x EBITDA multiples; net corporate cash changes of +/-USD1bn; share count changes of +/-1%; FY27 repurchase/issuance price assumptions +/-20% with fixed cash spending and original SBC. These are unit sensitivities with no probabilities. Report exact break-even multiple to the dated181.94 reference and local derivative thresholds; no target/current-return assertion.

For the one-quarter contrast at an endpoint before December31, accrue its earnings/cash uniformly through Q4 by elapsed calendar days, again conditional. For the sustained contrast accrue FY27 cash/share flows uniformly; apply the full FY27 earnings contrast to the fixed FY27 valuation metric. This separates endpoint balance timing from valuation of the chosen forward earnings year.

Validation tolerance1e-6 USDm except source display precision. Fail on missing keys, duplicate scenario-years, nonfinite inputs, nonpositive shares/prices, horizon outside supported interval or mismatched committed hashes. Preserve failures and outputs in new versions. No market refresh, calibration, valuation average, new fitted parameters, registration or scorer mutation.

## RESUME
Implement this bounded arithmetic audit, publish the economic contrast and all named limitations, then hand source/output hashes and exact commands to reviewer A. Research completion is distinct from economic evidence for an adopted direction.
