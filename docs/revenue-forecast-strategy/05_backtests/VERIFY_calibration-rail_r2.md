# VERIFY calibration-rail — round 2

## 1. Reproduction
`run.py` re-run end to end from repo root with the pinned venv python, after moving
existing outputs to `_prev_r2` siblings for diffing. Exit code **0**, all 6 steps OK,
wall time ~64s (58s of which is the GBM nested-CV step). Every regenerated file
(5 registry CSVs + `claims_confirmation.csv`, `pit_crps_ledger_detail.csv`,
`pit_crps_ledger_summary.csv`, `chronos_attempt.txt`) is **byte-identical** to the
pre-existing copy — fully deterministic, no hidden randomness in the reported outputs.

## 2. Registry format check
All 692 `method=="calibration-rail"` rows across the 5 registered objects
(`ref_naive`, `ref_ar1`, `ref_trailing4`, `gbm_revenue`, `gbm_surprise_guide`) were
loaded via `harness.load_registry` and checked against the 12 required columns in
`harness/README.md`: none missing, no nulls in any required column. Confirmed
programmatically:
- `vintage_date` < `print_date` of `quarter` for every row (0 violations) — no
  after-the-fact information used.
- `vintage_date` is a member of `GUIDE_DATES_ALL` or equals today (2026-09-11) for
  every row (0 violations).
- `n_params` genuinely varies per row (naive 0/1, ar1 2/3, trailing4 1/2, GBM flat 4)
  matching the harness's own "+1 once >=3 pseudo-oos residuals exist" convention in
  `baselines.py::_generic`. The `N_PARAMS` dict hardcoded at the top of
  `reference_scoreboard.py` (`{"ref_naive": 0, "ref_ar1": 2, "ref_trailing4": 1}`) is
  dead code — it is never referenced in `build_extra_baselines`; the actual `n_params`
  written comes entirely from the harness baseline function's own return dict. Cosmetic
  only (harmless dead code), noted for the implementer's own cleanliness, not scored.

Registry format: **valid**.

## 3. Leakage audit
- No `basis == 'derived'` exposure: this package never touches
  `10_regional_panel_quarterly.csv` (grep confirms zero references) — not applicable.
- No stale consensus vintages: this package's only Street exposure is via the
  harness's own `baseline_street`, which already raises `StreetVintageError` on any
  post-vintage `as_of`, and via the ledger's pre-computed `bl_*` columns (historical,
  not a live consensus pull). No 4-Sep/11-Sep-2026 vintage used as historical Street.
- GBM features (`lag1_revenue_yoy`, `lag1_gbv_yoy`, `guide_growth_pct`,
  `fx_adr_lag2`) are built from `history_as_of(gdate)` in the PIT replay — verified by
  reading `_row_features`/`_build_training_table`: lag1/lag2 come from the PIT-cut
  `hist` frame, `guide_mid(q)` and `y[q-4]` come from the unfiltered `t_full` table
  but only for values that are legitimately knowable at `gdate` (the guide itself, and
  a 4-quarters-back print). No violation found.
- `full_sample` GBM replay uses all printed quarters through 2026Q2 as candidate
  training rows (a genuine parameter/row leak), but with an explicit leave-one-out
  guard excluding the target quarter's own row — verified in code and cross-checked
  against the harness's own `baselines.py` full_sample convention (`_generic`, lines
  ~204-212), which is analogously leaky by design. Disclosed in the note as
  "optimistic," consistent with what the code does.
- Letter-rounded integers: not applicable — this package's targets are continuous
  (revenue_musd, revenue_yoy, nights_yoy, etc.), not letter-rounded guide integers.
- No use of the just-printed quarter's own GBV/revenue as a feature before its print
  date: confirmed by code reading — all lagged features reference q-1/q-2, and the
  only same-quarter reads (`guide_mid`) are for the guide itself, which is what the
  vintage date literally is.

**Leakage audit: clean.** No findings.

## 4. Number check (recomputed independently from the regenerated CSVs)
| # | Claim in note | Recomputed | Match |
|---|---|---|---|
| 1 | Claim 1 guide+cushion MAPE: PIT 1.068%, full_sample 0.990%, n=14 | 1.068412%, 0.989764%, n=14 (`claims_confirmation.csv`) | exact |
| 2 | Claim 2 RMSE (pp): bl_zero 1.873, bl_last_quarter 1.760, bl_guide 2.588, bl_guide_plus_cushion 2.642, bl_expanding_mean 3.926, n=100 | same values to 3dp | exact |
| 3 | nights_yoy W1 PIT RMSE: naive 2.877 < trailing4 5.341 < ar1 6.673 | recomputed directly from registry+targets: 2.877 / 5.341 / 6.673 | exact |
| 4 | Part (d): 284 of 391 rows scored, all PIT in [0,1], min 0.025 max 0.975 | 284 rows, min 0.025, max 0.975, 0 out-of-range | exact |
| 5 | Part (d) counts: 12 BIASED / 21 calibrated / 1 OVERCONFIDENT of 34 groups | same counts from `pit_crps_ledger_summary.csv` | exact |
| 6 | eu_platform_yoy_lag1 revenue_surprise_pct: PIT mean 0.025, KS p=1.2e-19, n=12; pr_hotel_revpar_yoy revenue_surprise_pct PIT mean 0.078 KS p=1.6e-7 n=11; pr_hotel_revpar_yoy nights_surprise_pct PIT mean 0.796 KS p=0.0072 n=8 | 0.025/1.2e-19/12; 0.0775/1.57e-7/11; 0.796/0.0072/8 | exact |
| 7 | guide_cushion / ar1 GBM-table reference row (W1 PIT): RMSE 35.46/103.54, ratio 0.377/1.101, bias +10.6/-48.8, cov 0.643/0.286 | 35.457/103.542, 0.377/1.101, +10.60/-48.78, 0.643/0.286 | exact |
| 8 | n_cal=6, alpha=0.2 attainable band [85.7%,100%], k=6=max of 6 | `conformal_attainable_grid.csv` row for n_cal=6,alpha=0.2: k=6, band [0.8571,1.0] | exact |

Eight independent recomputations, all exact matches. No number-check failures.

**One arithmetic error found, internal to the note itself (not from re-running
code):** the falsification-test paragraph in §(c) and in "Fixes after verification,
item 4" both state the full-registry `revenue_musd, n_cal=6, alpha=0.2` slice is
"66 rows" with the distribution `{1.0: 37, 0.75: 16, 0.875: 11, 0.5: 2, 0.25: 2}`.
Those five counts sum to **68, not 66** — a 2-row arithmetic slip present in the note
as written, independent of any registry drift. Separately, re-running `score.py`
just now (after other packages' concurrent registrations landed between the note's
last run and this verification pass) makes the live number drift further: the same
slice now has **72 rows**, `{1.0: 40, 0.75: 16, 0.875: 12, 0.5: 2, 0.25: 2}`.
calibration-rail's own 8-row sub-claim (`{0.75: 4, 1.0: 4}`) is unaffected and still
exact — that part of the fix is solid. The wider-registry claim is a moving target by
construction (other packages keep registering), so it should be read as "as of this
package's last score.py run," not as a stable fact, and the note's own arithmetic
should be corrected the next time this note is touched.

## 5. Cosmetic leftover from the round-1 fix (not itself wrong, but inconsistent)
The "Parameter counts" table at the bottom of the note (added in the round-1 fix)
correctly states `ref_ar1: 2-3`. The earlier GBM comparison table in §(b), which
carries an `ar1 (reference)` row for context, still shows a flat `n_params=2,
param/obs=0.143` for that row. The live scoreboard's own aggregation
(`score.py` takes `max(n_params)` per group) reports 3 / 0.214 for that exact
(baselines, ar1, revenue_musd, W1, PIT) row — verified directly. This is the same
class of oversimplification the round-1 fix addressed for `ref_naive`/`ref_trailing4`
but was not carried through to this one reference row in §(b)'s table. It does not
touch any RMSE/MAPE/CRPS/coverage number (those were independently confirmed exact
above) — only the `n_params`/`param/obs` columns of one contextual reference row.

## 6. Acceptance tests
All five acceptance tests were actually re-run, not asserted: reproduced Claim 1
(exact), Claim 2 (exact), the nights/AR(1) partial-disconfirm (exact, with the correct
5.341 trailing4 number), the n_cal=6 attainable-coverage grid (exact), and exit-code-0
(reproduced twice, byte-identical outputs both times). No acceptance test was marked
passed without evidence — every "PASS" has a matching recomputation in this report.

## 7. Honesty of interpretation
The note's interpretation matches its own numbers throughout: it correctly states
guide+cushion is simultaneously the best LEVEL predictor and among the worst
surprise-vs-Street predictors without contradiction; it states the GBM challenger
ties-or-loses to guide+cushion on every window scoreable and does not inflate that
into a positive result; it discloses the GBM's 10-of-14 W1 coverage gap and the
resulting weakness of `survives_both_windows=True`; it discloses the full_sample
replay's optimism for both baselines and the GBM; it names the exchangeability
violation on every conformal-coverage sentence rather than once; and its "optimal
mix" conclusion (100% guide+cushion on revenue level, no tested method above
`bl_last_quarter` on surprise-vs-Street) is stated as a negative/honest result rather
than dressed up, and is correctly noted as resting only on parts (a)/(b)/(c), which
this round independently reconfirms are defect-free. The round-1 fix bullets are
themselves honest about what changed and what didn't. No overclaiming found.

## Verdict: PARTIAL — safe to score with two named caveats

The package's code, registry, and PIT discipline are clean: byte-reproducible,
zero leakage findings across 692 rows, and 8/8 independently recomputed numbers exact.
Quote parts (a), (b), (c)'s per-package numbers, and (d) freely.

Caveats before quoting the *full-registry* falsification claim in §(c):
1. The stated "66 rows" is a 2-row arithmetic slip against its own listed
   distribution (which sums to 68) — fix the count when next touching the note.
2. The full-registry distribution is a moving target across concurrently-running
   packages (68→72 rows already, between the note's last run and this verification);
   cite it as "as of run X" or re-derive at scoring time, not as a fixed number.
Also fix, low priority: the flat `ar1 (reference) n_params=2 / param-obs 0.143` cell
in §(b)'s GBM table to match the corrected `2-3` range already in the parameter-count
table below it.
