# VERIFY tracker-backlog — round 1

Verifier pass on the implementer's `tracker-backlog` report. Repo root:
`Citadel-ABNB`. Python: `/Users/theomachado/.venvs/citadel-abnb/bin/python`.

## 1. Rerun

```bash
cd "<repo>"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/tracker_backlog/run.py
```

Existing `data/processed/forecast_methods/tracker_backlog/` copied to a `_prev`
sibling first, then the entry point re-run into the live folder. **Exit code 0.
Wall time ~3s.** All 10 output files (`01_backlog_rebuild.csv` ...
`04c_booking_curve_prior_caveat.txt`) are **byte-identical** to the pre-existing
outputs (`diff -q` on every file: SAME). The two registry files
(`tracker-backlog__revenue_yoy_next_q.csv`, `tracker-backlog__nights_yoy_next_q.csv`)
are also byte-identical (MD5 match before/after rerun). The package is fully
deterministic — no RNG, no external network calls in the run path. `_prev` folder
was deleted after the diff.

## 2. Registry format check

Loaded both files via `harness.load_registry(method="tracker-backlog")`: shape
(768, 31) across the 2 objects; all 12 required columns present and non-null.
`load_registry()` itself appends `format_version`/`_source_file` for convenience,
which correctly trips `validate_registry_frame` if you feed it the loaded frame
back in unmodified (that is expected harness behaviour, not a package defect) —
re-ran `validate_registry_frame` on the files exactly as written to disk (minus the
`format_version` column `register()` itself appends) and it passed clean on both.

* **PIT rule**: merged every row against `calendar.csv`'s `print_date` — 0 rows with
  `vintage_date >= print_date` of the target quarter. 0 rows with `vintage_date`
  outside `GUIDE_EVENTS_ALL` or today.
* **spec_id**: 8 values present (`unearned_raw`, `unearned_rnpl_scenario_k{0.5,1.0,1.5}`,
  `funds_raw`, `funds_rnpl_scenario_k{0.5,1.0,1.5}`) x 2 windows x 2 replays = 64
  groups, every one with exactly the expected 14 (W1) or 10 (W2) rows. 8 x 2 x 2 x
  (14+10) = 384 rows per object, matching the claimed count exactly.
* Confirmed both harness-change-request claims by reading the harness source
  directly: `score.py`'s `GROUP_KEYS = ["method","object","target","window",
  "prior_basis"]` has no `spec_id` (line 29); `baselines.py`'s `BASELINE_SPECS`
  (line 336-345) hard-codes metric lists to `["revenue_musd","revenue_yoy",
  "gbv_musd","nights_m"]` for naive/ar1/trailing4, omitting `nights_yoy`. Both
  change requests are accurate, not invented.

**Registry format: OK.**

## 3. Leakage audit

* `build_pairs`/`walk_forward` in `gate_g1.py` train on `pairs[pairs.quarter < tq]`
  (string-lexicographic `YYYYQn` ordering, chronologically consistent) rather than
  calling `history_as_of(vintage_date)` directly — this is a simplification, not a
  leak: it assumes every quarter before the target quarter printed before the
  target's guide date, which is exactly what the PIT-rule check in §2 confirms
  holds for every registered row.
* RNPL correction (`rnpl_correction_pct`) is keyed only to the **feature's own
  quarter** (`qprev`), never to a future quarter or the target quarter itself — no
  forward leakage in the scenario add-back.
* Verified the RNPL-share values against `03_insider_mechanics.md` directly:
  "1Q26 | ~20% of global GBV" (line 223) and "Jul 2026 | ... >20% of 2Q26 GBV"
  (line 224) / "RNPL | >20% of GBV" (2Q26 table, line 500) support the 20%/22%
  labelled-as-disclosed values, though **note the 2Q26 figure the doc actually
  discloses is only ">20%", not the specific 22% used** — 22% is the implementer's
  own point choice within a disclosed floor, which the note's phrasing ("is
  management-disclosed") slightly overstates; the underlying floor is disclosed,
  the specific point is not. Minor, doesn't change PIT-safety (both bounds are
  same-day-letter admissible). 3Q25 (5%) and 4Q25 (12%) correctly and honestly
  labelled as researcher scenario guesses — no disclosure for either found anywhere
  in `03_insider_mechanics.md`.
* Full-sample constants (`COVERAGE_NORM_FULL_SAMPLE`, a 2023-25 full-sample mean)
  are used **only** inside `circularity.py`'s arithmetic-identity test and
  `rebuild.py`'s labelled, non-consumed descriptive column — never as a Gate G1
  forecast input. No full-sample-fit leakage into the scored objects.
* No consensus/Street vintage values (04 Sep / 11 Sep 2026) appear anywhere in this
  package — it does not consume `16_consensus_at_print_merged.csv` or
  `04_current_consensus.csv` at all.
* No `basis == 'derived'` rows enter Gate G1 or the registry — the derived/circular
  restated series is written to `01_backlog_rebuild.csv` as a labelled column only
  and never joined into `gate_g1.py`'s feature frame.
* No letter-rounded integers are scored as points in this package (Gate G1 targets
  are `revenue_yoy`/`nights_yoy` from the harness's own `targets.csv`, not
  hand-transcribed letter figures).

**No PIT leakage found in the registered forecast objects.**

## 4. Number check (8 spot-checks against the CSVs, 6+ required)

All recomputed directly from the package's own output CSVs and cross-checked
against `03_insider_mechanics.md` / `08_backlog_tests.csv` where cited.

1. `1Q26`: `0.880 x 3608.0 = 3175.04` — file says `implied_pro_forma_musd = 3175.04`. Match.
2. `2Q26`: `0.697 x 4730.0 = 3296.81` — file says `3296.81`. Match.
3. `1Q26` `d_q_computed_pct = 16.174` vs quoted `16.2` — file confirms, flag `d_q_matches_quoted=True`. Match.
4. Formula-vs-number: multiply form `+16.6%`/`+15.4%` vs divide form `+19.73%`/`+18.61%` — file `02b_formula_vs_number_check.csv` confirms exactly, `multiply_form_matches_quoted=True/True`, `divide_form_matches_quoted=False/False`. Match.
5. Gate G1 raw revenue_yoy (unearned), W1: ratio_vs_naive **1.171207**, ratio_vs_ar1 **1.029443** — note quotes 1.171/1.029. Match.
6. Gate G1 raw nights_yoy (unearned): W1 ratio_vs_naive **0.904400**/ar1 **0.389867**, W2 **1.183406**/**0.705135** — note quotes 0.904/0.390, 1.183/0.705. Match.
7. RNPL-corrected revenue_yoy (unearned) k=1.0: W1 **0.680213**/**0.597880**, W2 **0.592608**/**0.573172** — note quotes 0.680/0.598, 0.593/0.573. Match.
8. Booking-curve Dirichlet shares: b0_1Q **0.251049**, b1_2Q **0.207703**, b2_4Q_capped **0.541247** — note quotes 0.251/0.208/0.541. Match.

**Two minor prose inaccuracies found (do not affect any scored/registered number):**

* The note states the booking-curve source (`booking_curves_by_market.csv`) has
  **"601 rows"**; the file actually has **600 data rows** (120 markets x 5 horizon
  bands). 601 is `wc -l` including the header, not the row count. Cosmetic, but a
  real number-check miss — the implementer's own acceptance criteria call for
  numbers to be recomputed from the CSVs, and this one wasn't.
* The note states the region breakdown file `04b_booking_curve_prior_by_region.csv`
  has **"120 rows"**; it actually has **267 data rows / 89 unique regions x 3
  buckets** — the same sentence then separately (and correctly) says "~90 finer
  region rows" a few words later, so the note is internally inconsistent about its
  own file's row count. The quoted share **range (~0.17-0.36)** for b0_1Q is
  correct (actual: 0.169-0.365).

## 5. Reconciliation gap against `02_model_audit.md` §4.1 — not caught by the implementer

This is the one substantive finding of this verification round.

`02_model_audit.md` line 438 reports, from the same underlying backlog-features
walk-forward programme, a **"survivor"**: `bl_funds_yoy_lag1 -> rev_yoy, ratio
0.600`. That number is real — it is the `wf_ratio_vs_naive = 0.6001434572214646`
value on the `"2023Q1..2026Q2, WF from 2024Q1"` row of
`08_backlog_tests.csv` for `bl_funds_yoy_lag1`/`rev_yoy` (verified directly from
the CSV).

`gate_g1.py`'s own re-derivation of the **same feature, same target, same W2
window** (`funds_raw`, `revenue_yoy`, W2, PIT) gives **ratio_vs_naive = 0.985111**
— a beat, but a much narrower one, nowhere near the "survivor" the audit flagged.
The W1 rows for the *unearned* feature reproduce the legacy file almost exactly
(differences in the 5th decimal, consistent with the implementer's claim), but the
implementer's reproduction claim is **carefully scoped to "both
unearned_fees_yoy_lag1 targets"** — it never claims to reproduce the funds feature,
and indeed it doesn't, by a wide margin, on W2.

Root cause (diagnosed here, not by the implementer): the legacy
`08_backlog_tests.csv` file's own `"window"` column shows it used a **different
training sample for its W2 row** than for its W1 row — `"2022Q1..2026Q2, WF from
2023Q1"` for W1 vs `"2023Q1..2026Q2, WF from 2024Q1"` for W2, i.e. the legacy script
**dropped 2022 data from the training set** when producing its W2 number, rather
than using an expanding window that includes 2022 for both. `gate_g1.py` instead
uses a single expanding window from the earliest available data (2022Q1) for
**both** W1 and W2, differing only in which dates are *scored* — which is what the
binding standing instruction actually specifies ("expanding window, two evaluation
windows... W1 origin 1Q23... W2 origin 1Q24"), so `gate_g1.py`'s convention is
arguably the more correct one under this engagement's own rules, not the legacy
script's. `funds_held_yoy_pct` has a much sharper 2022 reopening outlier
(70.3% -> 52.1% -> 18.5% y/y in 4Q21-2Q22) than `unearned_fees_yoy_pct`'s
comparable run, which plausibly explains why dropping/keeping 2022 swings the
funds OLS fit far more than the unearned OLS fit (verified the raw KPI-panel
values directly; did not re-run the legacy script to confirm this is the full
explanation).

**This is not a bug in the registered numbers** — the registered `funds_raw` W2
rows (0.985/0.953, narrowly clearing naive/AR1) are internally consistent and
correctly derived under the package's own stated methodology. But the note never
surfaces that this methodology produces a *materially weaker* funds-feature result
than a previously-published "survivor" claim for the identical feature/target/
window, and doesn't explain why. Given the note already flags an analogous
AR(1)-baseline reconciliation gap for `nights_yoy` (the harness-canonical AR1 vs.
the legacy exploratory AR1, 6.67 vs 3.97) as a known issue, this funds/revenue W2
gap deserved the same treatment and was missed.

## 6. Acceptance tests

All 9 acceptance tests the implementer listed were independently re-run or
directly recomputed from the CSVs in this session and found to be accurately
reported:

* T1 circularity checks (2): confirmed, values match to rounding.
* Circularity confirmed on all 4 rows: confirmed (`multiply_vs_implied_pct_diff`
  max = 0.0% across all 4).
* Formula-vs-number discrepancy: confirmed exactly.
* "Raw walk-forward reproduces 08_backlog_tests.csv" (unearned only, as scoped):
  confirmed for the cited RMSE/ratio pairs; see §5 for the unscoped funds-feature
  gap the note doesn't mention.
* Gate G1 raw revenue fails both windows/both baselines: confirmed.
* Gate G1 raw nights partially clears (AR1 both windows, naive W1 only): confirmed.
* run.py exit code 0: confirmed (this session's own rerun). The implementer's
  specific claim of "3 separate full runs" could not be independently verified
  (only re-ran once here), but the rerun was byte-identical to the pre-existing
  outputs, which is strong evidence of determinism and is consistent with the claim.
* Registry validates against harness format v1.0: confirmed, see §2.

No acceptance test was marked passed without supporting evidence in the output
files.

## 7. Honesty of interpretation

The note's headline framing is honest and, if anything, conservative: it leads
with a FATAL circularity finding against its own architecture, correctly strikes
the restated series as a pin/feature/likelihood input everywhere, reports Gate G1
failing for revenue exactly as pre-registered, and labels the one promising result
(RNPL-corrected unearned feature clearing all four cells) as "promising, NOT
gate-clearing" with the multiple-comparison and researcher-scenario caveats stated
up front rather than buried. The two harness change requests are accurate and
useful. The known-issues list is genuinely self-critical (nights_yoy partial
clearance, AR1 baseline reconciliation gap, funds-specific k not swept). The one
place this discipline slipped is the funds/W2 reconciliation gap in §5 — a real,
diagnosable discrepancy against a previously-published finding that a careful
implementer would have caught by extending their own reproduction check to the
feature they were about to build a scenario correction on top of.

## Verdict: **PARTIAL** — safe to score with the following caveats stated

Score and quote this package's registered objects; they are PIT-clean, correctly
formatted, and every number checked reproduces from the CSVs. But attach these
caveats when it is used downstream:

1. **(Priority 1)** The `funds_raw` / `revenue_yoy` W2 result (0.985/0.953, a
   narrow pass) is a much weaker version of a previously-reported "survivor"
   (0.600) for the identical feature/target/window in `02_model_audit.md`. The
   discrepancy traces to a training-sample convention difference (this package
   uses full history from 2022Q1 for both windows, matching the standing
   instruction; the legacy script apparently truncated to 2023Q1+ for its W2 row)
   and is plausible given 2022's outlier funds-held y/y swing, but was not
   diagnosed or disclosed by the implementer. Anyone building on the funds feature
   (especially the RNPL-scenario funds variants) should know this before trusting
   the "funds gets worse under RNPL correction" framing — re-verify against the
   legacy convention before using it as evidence either way.
2. The RNPL-scenario correction's headline "clears naive AND AR1 on both windows
   for both targets at k=0.5-1.0" result rests on 2 of 14/10 dates per window
   using a researcher-assumed (not disclosed) RNPL GBV share, and on picking the
   best of 3 pre-registered k values after seeing both windows' scores (a mild
   multiple-comparison exposure, already flagged by the implementer) — treat as a
   lead for the 5 Nov call, not a validated signal, exactly as the note says.
3. The 2Q26 RNPL share (22%) is presented as "management-disclosed" but the
   primary source only discloses ">20%"; the specific point value is the
   implementer's choice, not a disclosure. Doesn't affect PIT-safety but should be
   phrased as "researcher point estimate within a disclosed floor," not
   "disclosed."
4. Two minor row-count errors in the note's prose (601 vs actual 600 rows in the
   booking-curve source; "120 rows" vs actual 267 rows / 89 regions in the region
   breakdown file) — cosmetic, don't affect any registered number or the Dirichlet
   shares themselves (which are correct), but should be fixed for accuracy.
5. The `nights_yoy` raw feature's partial Gate G1 clearance (AR1 both windows,
   naive W1 only) should be quoted as partial, not as a clean pass — the note
   already does this correctly; repeating here since it's the honest headline for
   this package's core (non-RNPL-corrected) claim.

Nothing here requires re-running the package or invalidates the registered CSVs —
the fix is disclosure (a short addendum to the note reconciling item 1, and
correcting the two row counts in item 4), not re-computation.
