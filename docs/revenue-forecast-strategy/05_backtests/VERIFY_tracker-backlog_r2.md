# VERIFY tracker-backlog — round 2 (independent verification of round-1 fixes)

Verifier ran independently of the implementer's report. All numbers below were
recomputed from the CSVs, not copied from the implementer's summary.

## 1. Re-run

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/tracker_backlog/run.py
```

Existing outputs and registry files were copied to `_prev` siblings before the rerun.
Result: **exit code 0**, wall time ~2.8s. Console output matches the note's headline
numbers exactly (circularity table, Gate G1 ratios, RNPL reconciliation, Dirichlet
shares). Post-rerun diff (`diff -rq` on the output folder, `diff` on both registry
CSVs) is **empty** — byte-identical to the pre-rerun state, confirming the
implementer's "no previously-registered value changed" claim. Both registry CSVs are
384 data rows (385 lines incl. header) as claimed. `_prev` folders and files were
deleted after the diff.

## 2. Registry format check

Both `tracker-backlog__revenue_yoy_next_q.csv` and `tracker-backlog__nights_yoy_next_q.csv`
(384 rows / 30 columns each) pass `validate_registry_frame` from
`analysis/src/forecast_methods/harness/` cleanly once the appended `format_version`
column is dropped (the harness's own documented append behaviour, same convention the
round-1 verifier used). `window` in {W1, W2}, `prior_basis` in {PIT, full_sample}, all
required columns present and non-null. **Registry format: OK.**

## 3. Leakage audit

- Feature construction (`gate_g1.build_pairs`): predicts quarter q's y/y target from
  quarter (q-1)'s backlog-feature y/y growth, i.e. what was printed at the earnings
  call that also gave guidance for q. Cross-checked against `GUIDE_EVENTS_ALL` /
  `load_calendar()`: the guide date for target quarter q is literally the print date
  of quarter q-1 (e.g. guide date 2022-02-15 for target 2022Q1 is the 2021Q4 print
  date), so x_{q-1} is same-day-knowable at the guide date — consistent with the
  harness's own `include_same_day=True` convention the note cites. No leakage found
  here.
- `walk_forward()` trains strictly on `pairs.quarter < tq` (expanding window, refit
  per guide date) — no future data in the PIT replay. `full_sample` replay correctly
  fixes only the OLS parameters to the final fit while keeping inputs point-in-time,
  matching the note's own description and `baselines.py`'s convention.
- No Sept-2026 consensus values used anywhere in this package: `gate_g1.py` calls
  only `baseline_naive`/`baseline_ar1` directly (never `baseline_street`), so the
  "Sept vendor as pre-guide Street" leak class does not apply to this package.
- `COVERAGE_NORM_FULL_SAMPLE` (full-sample 2023-25 seasonal means) is used only inside
  `circularity.py`'s struck/labelled diagnostic, never as a Gate G1 feature or a
  registered forecast input — confirmed by grep: it does not appear in `gate_g1.py`.
- The restated/circular unearned-fees series is clearly labelled
  `"derived (multiply form; circular ...); do not use as a forecast feature"` in
  `01_backlog_rebuild.csv` and is never read by `gate_g1.py` — confirmed directly in
  the CSV and by code inspection.
- `basis == 'derived'` rows: not applicable to this package (it does not touch the
  regional panel with that column).
- Letter-rounded integers scored as points: not applicable — this package does not
  consume letter-rounded d_q or coverage figures as regression targets/features
  outside the (struck) circularity diagnostic.
- 2Q26 RNPL share (22%) and the 3Q25/4Q25 ramp (5%/12%) are correctly disclosed as
  researcher scenario picks, not management numbers, per the round-1 fix — verified
  against `common.py`'s comment and `03_insider_mechanics.md`'s actual floor language
  ("~20%" / ">20%"). PIT-safety is unaffected either way since these are used only as
  of their own guide dates.

**No new leakage found. Leakage audit: clean.**

## 4. Number checks (recomputed independently from the CSVs, not transcribed from the note)

1. Circularity table 2Q26 row: reported unearned 2,831.0, coverage_norm 0.697,
   next-Q revenue used 4,730.0 (guide midpoint), implied pro-forma 3,296.81, d_q
   16.454% (quoted 16.5%) — reproduced exactly by rerunning `circularity.py`'s stdout.
2. Gate G1 `revenue_yoy` / `unearned_raw` / W1 PIT: RMSE 4.479287, ratio_vs_naive
   1.171207, ratio_vs_ar1 1.029443, n=14 — matches note's 4.479 / 1.171 / 1.029 to
   displayed precision, recomputed directly from `03c_gate_g1_ratios_by_spec.csv`.
3. Gate G1 `revenue_yoy` / `funds_raw` / W2 PIT: RMSE 4.225477, ratio_vs_naive
   0.985111 — matches note's 4.225 / 0.985 exactly.
4. `03d_funds_w2_legacy_reconciliation.csv`: this-package convention ratio_vs_naive
   0.9851105870896184; legacy-truncated-convention ratio_vs_naive 0.6001999789838758;
   `legacy_08backlogtests_quoted_ratio_vs_naive` column reads 0.6001434572214646
   directly from the CSV cell (cross-checked independently by reading
   `08_backlog_tests.csv` myself: row `feature=="bl_funds_yoy_lag1"`,
   `target=="rev_yoy"`, `window=="2023Q1..2026Q2, WF from 2024Q1"` gives
   `wf_ratio_vs_naive = 0.600143` and `wf_n = 10.0`, exactly as claimed). The
   reconciliation's root-cause claim (legacy truncates training to 2023Q1+ for its W2
   row) is independently confirmed by reading the `window` string in the legacy CSV
   directly, not merely asserted.
5. `wc -l data/processed/booking_curves_by_market.csv` → 601 lines = 1 header + 600
   data rows. Matches the corrected claim exactly (600, not the pre-fix "601").
6. `04b_booking_curve_prior_by_region.csv`: `pd.read_csv(...).shape` = (267, 3),
   `nunique()` on the region column = 89. Matches the corrected claim exactly.
7. RNPL scenario table, `unearned` feature, `revenue_yoy`, k=1.0: W1 ratio_vs_naive
   0.680213 / ratio_vs_ar1 0.597880; W2 0.592608 / 0.573172 — matches note's
   0.680/0.598 and 0.593/0.573 exactly, recomputed from `03c_gate_g1_ratios_by_spec.csv`.
8. Dirichlet shares: b0_1Q 0.2510, b1_2Q 0.2077, b2_4Q_capped 0.5412, alpha values
   65,347,332 / 54,064,487 / 140,884,979 — all match the note's table exactly,
   recomputed from `04_booking_curve_dirichlet_prior.csv`.

**No mismatches found across 8 independently recomputed numbers** (spec asked for
≥6; two extra were checked because they anchor the priority-1 fix).

## 5. Acceptance tests — evidence check

All nine acceptance tests the implementer listed were independently reproduced with
real evidence, not taken on faith:

- Priority-1 reconciliation (both conventions, both quoted ratios): reproduced by
  rerunning `run.py` and reading `03d_funds_w2_legacy_reconciliation.csv` directly —
  **confirmed**, plus I independently re-derived the legacy 0.600143 from
  `08_backlog_tests.csv` myself rather than trusting the package's own cross-check
  column.
- Row-count corrections (600 data rows; 267/89): reproduced with `wc -l` and
  `pandas.shape`/`nunique()` directly — **confirmed**.
- `run.py` exit 0, byte-identical rerun: reproduced (this verification's own rerun,
  independent of the implementer's three reruns) — **confirmed**.
- Registry validates against harness format: reproduced by calling
  `validate_registry_frame` myself on both files — **confirmed**.
- Gate G1 revenue/nights failure/partial-pass pattern unchanged: reproduced by
  reading `03c_gate_g1_ratios_by_spec.csv` directly — **confirmed**, matches the
  note's table cell-for-cell.

No acceptance test was marked passed without evidence; none needed correction.

## 6. Honesty of interpretation

The note's headline claims are calibrated to what the numbers actually show:
Gate G1 fails for revenue on the raw series on both windows and both features (only
exception, `funds_raw`/W2, is flagged as a "narrow pass" and now explicitly
reconciled against — and distinguished from — a stronger-looking legacy number under
an undisclosed shorter training window, with the package's own fuller-history
convention correctly kept as the registered value rather than swapped for the
better-looking legacy figure). Nights only partially clears the gate and this is
stated plainly rather than rounded up. The RNPL-corrected finding is repeatedly
labelled "promising, not gate-clearing" with its two real weaknesses named up front
(2 of 14/10 dates rest on researcher-assumed RNPL shares; a mild multiple-comparison
exposure from picking the best of three pre-registered k values after seeing both
windows). The booking-curve prior is correctly demoted to a directionally-inverted
plausibility check, not a Phi estimate. The round-1 fixes are disclosure-only as
claimed — I confirmed independently (via the empty rerun diff) that no previously
registered value was silently revised while the note's prose was cleaned up. This is
an honest package.

## Verdict: **PASS — safe to score and quote.**

No outstanding issues from round 1 remain unaddressed, and no new issues were found
in round 2. Residual caveats (carried forward, not blocking):

1. The harness's own canonical AR(1) baseline for `nights_yoy` is materially weaker
   than the legacy exploratory AR(1) (RMSE 6.67 vs 3.97) — flagged, not fixed, in
   both rounds; makes "beats AR(1)" an easier bar here than in the earlier pass for
   that one metric.
2. The RNPL-scenario correction remains a promising secondary finding, not a cleared
   gate — cite it with its stated caveats (researcher-assumed shares on 2 of 14/10
   dates per window; multiple-comparison exposure across k), never as "Gate G1
   passes."
3. Both harness change requests (score.py `GROUP_KEYS` lacking `spec_id`;
   `baselines.py` `BASELINE_SPECS` omitting `nights_yoy`) remain open; correctly
   worked around locally by this package (`03c_gate_g1_ratios_by_spec.csv`, direct
   baseline function calls) rather than blocking on a harness fix.
