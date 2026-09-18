# Presentation defense: the economic chain and its missing links

14 September 2026. Lead-owned foundations, prepared while the locked historical experiment runs. This note contains accepted starting evidence and fixed definitions. The final delivery must add the reviewed experiment and economic results; this is not the final research-completion verdict.

## Argument that survives the starting evidence

Historical booked dollars provide a transparent revenue benchmark. The retained model uses a fixed two-thirds first lag, one-third second lag and the existing seasonal coefficient policy. A separately fitted lag weight failed the accepted chronological promotion test: free/fixed revenue RMSE was 63.197/54.227 USDm on W1 n=14 and 57.392/56.516 USDm on nested W2 n=10. That supports retaining the operational rule. It does not identify current physical booking cohorts or prove a trading edge. [L3]

A September Q4 guide forecast also requires an estimate of unprinted Q3 GBV, a management-cushion assumption and a correctly defined expectations comparator. These links must survive individually and together. L4's frozen review revenue is 3,179.344 USDm versus captured LSEG-family revenue consensus of 3,161.021 USDm, a positive 18.322 USDm gap. Its guide of 3,123.419 USDm is a different object. Explicit expectations for management's guide are unavailable. Applying a common cushion to both revenue figures gives a hypothetical positive guide gap of 18.000 USDm, not observed guide-surprise evidence. [E]

## Essential equations

Let G1 and G2 be the two prior booking-quarter GBVs in USDm, w=2/3, and lambda a decimal seasonal conversion coefficient. Let c be actual revenue divided by the previously issued midpoint, minus one, estimated only from then-known past results.

`B = w G1 + (1-w) G2; R = lambda B; M = R/(1+c).`

Actual first-lag arithmetic contribution is `a=wG1/B`. Its W1 pooled standard deviation is 4.644pp and within-season standard deviation 0.516pp. Q4's standard deviation is 0.311pp on only three observations. These are distinct from uncertainty about w, uncertainty about lambda and total forecast error. [U]

When `G1/G2` is nearly constant within season, `R ≈ lambda[1+w(r-1)]G2`. Different w and lambda pairs can generate similar revenue. Preserve joint parameter draws when discussing the accepted descriptive fit; those free-weight draws are not adopted operational parameters. [U]

For a fee-revenue cohort ledger C[b,t], backward shares are `C[b,t]/sum_b C[b,t]`; forward allocations are `C[b,t]/sum_t C[b,t]`. The denominators differ. Unpaid balances are stocks and cannot supply either flow share without a stock-to-flow bridge. [U]

For revenue consensus S, equal-revenue thresholds are `G1*=[S/lambda-(1-w)G2]/w` and `lambda*=S/B`. Against a hypothetical Street guide using cS, own-cushion equality is `cOwn*=R(1+cS)/S-1`. At the captured LSEG reference, a 0.878% reduction in Q3 GBV or a 0.0694pp reduction in Q4 lambda erases the revenue gap, holding all other inputs fixed. Own cushion may rise by only 0.590pp from 1.790% before it equals a hypothetical Street guide retaining that reference cushion. These are conditional boundaries, not probabilities. [E]

Changing only c changes the guide forecast, not actual revenue, earnings or cash. The existing residual-reversion, fee and FX scenarios cannot be stacked as independent shocks if they affect the same booking dollars or embedded conversion. [E, L4]

## Skeptical judge questions and evidence-based answers

| Question | Answer the evidence permits | Observable falsifier or missing evidence |
|---|---|---|
| Does two-thirds literally recognize last quarter's bookings? | No. It is a retained reduced-form coefficient. Accepted free-weight flexibility failed promotion; current global revenue-weighted cohort shares are unavailable. | Current global booking-to-stay-to-fee-recognition ledger with cancellations and consistent denominators. |
| Why does low variance justify confidence? | Arithmetic contribution stability is only one input property. W1 has 14 observations and Q4 only three. Full forecast uncertainty includes unprinted bookings, conversion and guide policy, including dependence. | Out-of-origin losses, persistent signed misses and coverage at the actual decision horizon. |
| Could the model know the guide before the release? | The old letter-close experiment could use GBV from the release containing the guide. It does not answer the earlier-origin question. The locked new reconstruction forecasts unprinted GBV and retains every abstention. | Reviewed preannouncement performance on actual information dates, followed by future genuinely archived forecasts. |
| Is RNPL incremental demand or measured revenue leakage? | Neither magnitude is identified. Full booking value enters GBV without immediate cash; higher cancellation rates and changed timing are disclosed. Net GBV already deducts cancellations when processed. | Cohort gross additions, cancellations by original booking quarter, payment dates, stay dates, fee revenue and adoption comparisons. |
| Where does FX enter, and are you counting it twice? | Reported USD GBV embeds translation. Reported revenue can also include revenue hedge effects. A timing replacement needs compatible currency bases, fixing dates and a reconciled hedge treatment, applied once. | Currency/cohort revenue flows and fixing/settlement dates, plus signed revenue hedge attribution matching the baseline. |
| Is the guide below consensus? | A guide-minus-revenue-consensus subtraction is arithmetically negative here, but it does not measure surprise against guide expectations. Like-basis revenue is modestly above LSEG/S&P and below Zacks. | Dated, explicitly defined expectations for management's guide; future actual guide compared on that basis. |
| Does forecast accuracy imply revisions or profitable returns? | No. A2 remains PARTIAL and B2 failed its revision hurdle. Neither fitting a better equation nor correcting the basis establishes executable alpha. | A preregistered expectation/revision link and next-open returns with sufficient dated observations. |
| Why should a small operating gap drive the target? | It may not. Earnings persistence, incremental costs, cash retention, dilution and the valuation horizon must reconcile. L4's 184.663/share example is dated December 2027 and uses inherited assumptions. | Within-horizon value remains differentiated across defensible cash/share/multiple assumptions; current expectations and price are verified. |
| Why not take the opposite side? | Similar revenue to broad panels can coexist with healthy growth, cash generation and stable conversion. The failed promotion and failed trading/revision evidence limit conviction in a model-driven short. | Sustained operating deterioration beyond source/forecast uncertainty, with a same-basis earnings/cash gap large enough to matter. |
| Can more simulations resolve the uncertainty? | More draws do not add years or identify missing cohort flows. W1/W2 have at most four/three target-year blocks and are nested. | Additional independent regimes or directly observed missing links, not repeated resampling of the same cells. |

## Source and use key

[L3] Immutable bundle at L3 commit 8821961853e4068febbfe2712f9a4e1036c9e629, payload/conversion accepted receipt/specification and chronological tables. [U] uncertainty_audit_v1/UNCERTAINTY_AUDIT_v2.md and its input-bound reproduction tables. [E] expectations_v2/same_basis.csv, break_even.csv and cushion_policy.csv, sourced from L4 commit 29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70. LSEG observation is 13 September 2026 15:20 UTC; S&P September10 and Zacks September11 are date-only older anchors. No current-market refresh is claimed. [L4] exact committed review_v4/decision_register and annual/valuation outputs in evidence_v3/l4. Accounting source: [Q2 2026 Form10-Q](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm), Key Business Metrics and Note6; independently opened September14. Figures remain conditional scenarios or named historical samples, not structural probability estimates.

## RESUME
Add the reviewed prospective forecast and economic tables, select the few decisive figures, and convert these foundations into the final narrative/claim ledger. Independent examiner A must challenge the economic/presentation conclusions after completing the forecast implementation; reviewer B checks final contracts without signing its own financial implementation. Any unresolved limitation restricts wording rather than blocking completed research forever.
