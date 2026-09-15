# L4 integration preregistration

Written 2026-09-13 before L4 calculation or test execution. Starting commit `1c87628cedbc94ab8a0e8552743c94485ef353b8` contains completed L1/L2. Public branch heads verified by git ls-remote: L1 `0761555f8e9131b9c8a575959691c4b77f7729dd`, L2 matches starting commit. Main at verification is `a1c8765a6bdc2b6f0f2dd284d5430f61d455d7ff`; this task starts at the specified completed-lane commit, not an unverified merge.

## Objective and scope

Reconcile existing revenue/guide engines and operating inputs; build a linked financial model and two-page review draft. No new alpha test, migration estimator, team decision or automatic merge. ABNB USD millions except explicitly labelled ADR USD/night, nights millions, shares millions, percentage points or decimal factors. Existing core revenue covers consolidated revenue; separately retain outside-scope streams only if documented and reconcile before adding them.

## Methods fixed before execution

1. Import K0 v2 seasonal lambda and its fixed 2/3, 1/3 lag policy. Forecast GBV is supplied through a new thin adapter, never inserted into reported-data rows. Nights times dollar ADR must equal the adapter's GBV. Use team nights with ADRv3 with-K as a labelled review reference, without-K and K0 conditional outputs as comparisons. K is imposed mechanics, not a fitted causal coefficient.
2. Reproduce the existing H1/H2 and K0 guide calculations, then change GBV, lambda, cushion and any explicit overlays in a documented deterministic order. Attribution residual must be below $0.001 million. Identify information dates and reference bases. Q3 operating inputs cannot affect Q3 two-lag revenue; Q4 operating inputs cannot affect Q4 revenue.
3. L3 contract requires quarter, metric, scenario, value/bounds, units, information date, evidence status, source reference and replacement-versus-incremental treatment, plus bundle version/commit and hashes. Pending L3 values stay unavailable, with the unreconciled baseline exposed. Apply only an incremental replacement of embedded FX, or a verified constant-FX reconstruction; do not add gross FX to USD GBV or invent zero hedge dollars. No stock-derived RNPL cohort weights.
4. Reproduce the original $180.876286 EBITDA lens and $156.786845 six-lens mean to $0.001/share before replacing covered forecast revenue. Carry costs, cash, shares and explicit inherited horizon assumptions forward through formulas. No causal growth-to-multiple regression, new probabilities or adopted target.
5. New scenarios are current conditional review objects, not backdated historical research. Register new supported ABNB objects through FORMAT 1.1 only after parent review, under distinct scenario object names. Use actual run dates. No registration for unidentified FX estimates.

## Acceptance and failure treatment

- Source traceability, dimensional identities, quarter timing, missing-input refusal, no duplicate fee/FX/cancellation/seat adjustments and an explicit hedge convention are required.
- Adapter identities: zero RNPL, equal rates, conserved exposure and rejection of future-dated observations. L4 tests contract/application behavior; L3 owns research evidence and cohort construction.
- Workbook formulas recalculate, contain no broken external links or formula errors, and independently tie to calculations at $0.001 million/$0.001 per share. User-editable assumptions must feed financial/valuation outputs.
- Review PDF is exactly two readable pages, with editable source and every page visually inspected. Memo, workbook, card and decisions agree on metrics and evidence status.
- Every pre-existing tracked file remains unchanged. Frozen scorer snapshots preserve exact keys, labels, counts and missingness; floating drift is strictly below 1e-9 absolute with zero relative tolerance. Run actual frozen and FORMAT 1.1 scorers to new destinations after final registration.
- Preserve failed tests and partial evidence. Mechanical implementation completion is separate from research validity and investment adoption. An absent L3 bundle blocks only FX/RNPL integration, not the baseline package.

## RESUME

Run independent provenance/accounting and model/memo consistency reviews after initial integration, repair demonstrated errors, then publish only the new files on codex/lane4-full. The external untracked FX bundle is read-only and must be hashed, never staged wholesale. No outreach or licensed data access.
