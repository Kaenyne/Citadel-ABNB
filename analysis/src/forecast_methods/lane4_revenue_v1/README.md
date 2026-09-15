# L4 revenue and guide reconciliation v1

Run from the repository root with Python/pandas/numpy (K0's existing dependencies):

```text
python -X utf8 -m pytest analysis/src/forecast_methods/lane4_revenue_v1/tests -q
python -X utf8 analysis/src/forecast_methods/lane4_revenue_v1/run.py
```

The default output is `data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1/`.
An existing directory is always refused. Reproduce to a new destination:

```text
python -X utf8 analysis/src/forecast_methods/lane4_revenue_v1/run.py --as-of 2026-09-13 --output data/processed/forecast_methods/lane4_revenue_v1/rebuild_02
```

The runner writes no registry and changes no K0/harness/L0 input. Failed runs remain on disk. Parent owns registration and both scorers. Source hashes are in `source_ledger.csv`. All monetary figures are USD millions except ADR in USD/night; nights are millions. Information is admitted at daily precision in this current review package (same-day sources explicitly allowed). K0 retains its stricter pre-date cutoff internally. These LIVE scenarios have no retrospective W1/W2 validation; the new method cannot be run before its September 13 availability date.

The fixed 2/3 K0 conversion policy is an inherited **benchmark**, with conversion-dependent conclusions provisional pending an explicit accepted L3 conversion handoff. L3 owns estimation and validation of conversion alternatives. No new weight or conversion method is fitted in this package. This status is separate from pending cohort FX/RNPL integration.

## Outputs

- `forecast.csv`: three quarters per scenario; benchmark reported-revenue kernel and implied guide. Q3 implied guide is diagnostic because management already issued Q3 guidance on August 6. Q4 and Q1 are prospective conditional guides. `conversion_status` and `fx_integration_status` identify the two pending research interfaces separately.
- `operating_inputs.csv`: published ADRv3 midpoint card dollar ADR times its nights, without rounding the product. Q3 team nights are 146.8m; Q4 case B is 131.8m and alternative case A is 132.7m. K0 comparison has GBV only; nights/ADR are unavailable, not imputed.
- `cohort_weights.csv`: lag coefficient times actual/forecast USD GBV, divided by the weighted sum. These are USD-baseline contributions, not measured booking-to-stay probabilities or constant-FX currency weights.
- `guide_reconciliation.csv`: exact H2 v3 to K0 sequential attribution: GBV, lambda, cushion, separate overlays, information date. Order was fixed before execution; interaction attribution depends on that order.
- `issued_guide_comparison.csv`: already-issued Q3 midpoint times current trailing-eight median/mean cushion, alongside kernel revenue.
- `cushion_inputs.csv`, `sensitivity.csv`: observed cushion summaries and transparent level sensitivities. A 1% relative nights/ADR change is not a one-percentage-point YoY change. Legacy Q4 cushion applies only to Q4. No probability is attached.
- `fee_mechanics_comparison.csv`: with-K published ADR replaces without-K ADR. No extra take-rate uplift is added. Dollar differences inherit the published card's cents rounding; K is imposed mechanics, not a measured causal coefficient.
- `consensus_source_rows.csv`: all eligible existing Q4 current-vintage rows. `consensus_selection.csv` selects the latest observation per panel family; Yahoo and Alpha Vantage count once. `consensus_comparison.csv` carries vendor, timestamp, analyst count and source. Old S&P and Zacks anchors are not restamped.
- `integration_status.json`: pending L3 conversion and FX handoffs. Incremental FX, hedge dollars and FX-neutral revenue remain null. Benchmark reported revenue remains available, visibly unreconciled for L3's proposed timing mechanism.

Historical lambda absorbs typical pricing, cancellations, fees, translation and reported hedge effects. This adapter does not add a gross FX factor, cancellation stress, seats deduction, regional adjustment or second fee reprice. Mean reversion replaces the residual with 2.398pp while retaining K and the other terms; it is a sensitivity, not a newly estimated price series.

## L3 FX contract (no live bundle supplied)

Use `--l3-manifest path/to/manifest.json` only after the parent receives an explicit user-carried L3 handoff and verifies its claimed commit's file contents. The loader checks SHA-256, safe local paths and commit syntax; **it does not prove the files belong to that Git commit**. Parent verification remains required before promotion. Never read L3's changing worktree implicitly.

The manifest requires `bundle_version`, a 40-character `commit`, `information_date`, and `files` entries with relative `path`, `sha256`, and `role`. A file with role `revenue_adapter` contains a JSON list of rows. Each row requires:

| Field | Required meaning |
|---|---|
| `quarter`, `metric`, `scenario` | YYYYQn, `revenue_timing_multiplier`, distinct scenario |
| `value`, `lower`, `upper`, `units` | Positive ratio, bounds explicitly null or bracketing point, `ratio` |
| `information_date`, `evidence_status`, `source_ref` | Dated provenance; assumed exposures stay labelled |
| `treatment` | `incremental_replacement_of_embedded_booking_fx` |
| `baseline_scenario`, `baseline_revenue_musd` | Exact L4 scenario and revenue, tied within $0.000001m |
| `reference_basis`, `embedded_fx` | Shared reference identifier; `booking_fx_already_in_USD_GBV` |
| `hedge_treatment` | `reconciled_baseline_hedges_held_unchanged` |
| `baseline_hedge_musd`, `hedge_source_ref`, `hedge_evidence_status` | Explicit verified hedge contribution h; source; `verified_baseline_reconciliation` |
| `cohorts` | Supplied cohort/currency rows described below |

Each cohort requires booking quarter, currency, `reference_gbv_musd`, `booking_fx_ratio`, `rate_direction=USD_per_currency`, `rnpl_share`, `share_denominator=surviving_recognized_revenue_reference_exposure`, reference basis, evidence status, information date and source. Its `rnpl_allocation` contains recognition quarter, weight, FX ratio and information date. At this quarterly interface recognition quarter must equal target quarter; granular L3 timing may be collapsed into that quarter's exposure-weighted currency ratio. An alternative payment/fixing-date hypothesis requires a separately named contract, not relabelling recognition.

Both kernel lags must be supplied. Currency reference exposures times booking FX must reconstruct each exact USD GBV input. Fixed coefficients times reference values produce weights w; w sums to one and each RNPL allocation sums to one. The supplied multiplier must equal F_retimed/F_booking. Algebra tests use **synthetic fixtures only**, not Airbnb RNPL estimates.

Final application is `(R - h) × timing_multiplier + h`. It preserves hedge dollars rather than multiplying them. Missing h or its reconciliation blocks final after-hedge FX application; h is not guessed zero. The same adjustment cannot be applied twice. Management-stated after-hedge YoY FX, economic translation levels and changes in YoY contribution are different objects; none is an additive revenue overlay here.

## Research limitations and RESUME

This is implementation and reconciliation, not a forecasting-performance claim. It imports K0 selection unchanged. K0 conditional GBV relies on undisclosed RNPL ramps and growth persistence. ADRv3's reported-dollar conditional successes use n=10/n=9 windows distinct from the main harness; its rule was selected after earlier analysis, its integer-fair ex-FX target did not pass both windows, and K's small improvement does not identify causal pass-through. A2 remains PARTIAL, B2 FAIL and RNPL migration unidentified. L2 stock diagnostics never become cohort RNPL shares. No direction, target, probability or card adoption is made.

Use snapshot_v1 with the linked workbook and memo; retain development failures. Parent should verify source hashes, register only genuinely new supported scenario objects and run both scorers to new snapshots. When the user provides L3 conversion and FX handoffs, verify commit contents and hashes, reconcile exposures and hedge treatment to this baseline, then rebuild into a new version. Keep conversion-dependent claims provisional and missing FX/RNPL values unavailable until those inputs are accepted.
