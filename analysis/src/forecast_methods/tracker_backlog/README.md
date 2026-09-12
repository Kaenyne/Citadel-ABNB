# tracker-backlog

The booked-base tracker: unearned fees and funds held as a backlog identity, the
circularity test on the "restated" unearned-fees series, and Gate G1 (redefined:
raw, non-circular series only).

## Run

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/tracker_backlog/run.py
```

Exit code 0 on success. Steps run in order (circularity test first, per the standing
instruction) and each writes its own output files, so a crash partway through still
leaves everything already computed. Individual steps can also be run directly:
`circularity.py`, `rebuild.py`, `gate_g1.py`, `booking_curve_prior.py`.

## What each step does

1. **`circularity.py` (T1, must run first).** Tests whether the architect's
   `unearned_fees_restated = reported * (1 + d_q)` is identically
   `coverage_norm(season) * next_quarter_revenue`. Verdict: **yes, to <0.001% on all 4
   dated rows** (3Q25, 4Q25, 1Q26, 2Q26). The 2Q26 row uses the 3Q26 *guide midpoint*,
   not a print, so it is doubly circular. Also checks the formula-vs-number
   discrepancy in `03_insider_mechanics.md` (states `reported/(1-d_q)`, but every
   quoted y/y number is reproduced only by `reported*(1+d_q)`); reproduced exactly.
   **Ruling: STRUCK as a pin, as a feature, and from every window/likelihood in every
   package.** Outputs: `02_circularity_test.csv`, `02b_formula_vs_number_check.csv`,
   `02c_circularity_verdict.csv`.
2. **`rebuild.py` (a).** Rebuilds unearned fees, funds held, GBV, revenue, nights and
   y/y growth quarterly since 4Q20 (23 quarters) from `abnb_backlog_indicators.csv`,
   writes out the balance-sheet identity (with the not-disclosed terms named, not
   fitted), and computes the derived/circular restated series for completeness
   (labelled `basis=derived`, never consumed downstream). Output:
   `01_backlog_rebuild.csv`.
3. **`gate_g1.py` (c).** Gate G1, redefined: does the RAW backlog y/y growth (unearned
   fees, funds held; no restatement) beat naive/AR(1) for next-quarter revenue growth
   and next-quarter nights growth, refit expanding-window PIT at every W1/W2 guide
   date? Tests a labelled RNPL-GBV-share **scenario** correction (k=0.5/1.0/1.5x the
   disclosed/scenario RNPL GBV share, added to the feature — never fit against the
   target). Registers `tracker-backlog__revenue_yoy_next_q.csv` and
   `tracker-backlog__nights_yoy_next_q.csv` (384 rows each: 2 features x 4 spec
   variants x {W1,W2} x {PIT,full_sample}, both replays). Outputs:
   `03_gate_g1_walkforward_summary.csv`, `03b_gate_g1_all_registry_rows.csv`,
   `03c_gate_g1_ratios_by_spec.csv` (the RMSE-ratio table quoted in the note),
   `03d_funds_w2_legacy_reconciliation.csv` (added post-verification-round-1: the
   `funds_raw`/`revenue_yoy`/W2 ratio reproduced under both this package's own
   full-history training convention and the legacy `08_backlog_tests.csv` truncated
   convention, reconciling the two — see the note's "Fixes after verification"
   section).
4. **`booking_curve_prior.py` (d).** Turns the 120-market blocked-rate-by-horizon
   snapshot into pseudo-Dirichlet concentration parameters over 3 lag buckets, for
   kernel-lambda to use as a soft plausibility check only — never a point input. See
   the docstring for why (nights not dollars, booked+host-blocked conflated, single
   vintage). Outputs: `04_booking_curve_dirichlet_prior.csv`,
   `04b_booking_curve_prior_by_region.csv`, `04c_booking_curve_prior_caveat.txt`.
5. **(e) Inside Airbnb monthly capture spec: NOT built, NOT run.** Full specification
   is in the note (`docs/revenue-forecast-strategy/05_backtests/tracker-backlog.md`,
   section (e)), per the standing instruction "do not run the capture."

## Harness change requests (see note for detail)

1. `score.py`'s `GROUP_KEYS` has no `spec_id`, so multiple spec_id variants
   registered under one object per the README's own suggested pattern get pooled
   into one blended scoreboard row. `gate_g1.py` works around this locally
   (`03c_gate_g1_ratios_by_spec.csv`).
2. `baselines.py`'s `BASELINE_SPECS` hard-codes metric coverage to
   `["revenue_musd","revenue_yoy","gbv_musd","nights_m"]`; `nights_yoy` (a valid
   `targets.csv` column, used by this package) has no registered `baselines__naive`/
   `baselines__ar1` row. Worked around by calling `baseline_naive`/`baseline_ar1`
   directly (they are metric-agnostic) rather than reading the registry.
