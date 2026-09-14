# VERIFY l1-reconciliation — round 2

Independent re-verification of package `l1-reconciliation` after the
implementer's six round-1 fixes. Verifier ran fresh, 2026-09-11.

## 1. Reproducibility

Moved existing outputs to `l1_reconciliation_prev_r2/` and the three registry
files to `registry_prev_l1_r2/`, then re-ran:

```
cd "<repo>"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/l1_reconciliation/run.py
```

**Exit code 0.** Started 11:33, output files stamped 11:36 (~180s wall,
consistent with the implementer's claimed 150s — the small delta is normal
machine-load variance, not a regression).

`diff -rq` between the pre-run and post-run `data/processed/forecast_methods/
l1_reconciliation/` directories: **no differences** (every CSV byte-identical,
run_log excluded from the check since it embeds a timestamp). `diff -q` on
all three registry CSVs against the pre-run copies: **clean, byte-identical**.
This independently confirms the implementer's own "byte-identical, nothing
moved" claim rather than merely trusting it.

## 2. Registry format

Ran `harness/registry.py`'s `validate_registry_frame()` directly (dropping
the self-stamped `format_version` column, the same harness quirk round 1
found) against all three files: **all three validate cleanly** —
`revenue_contemporaneous` (44 rows), `fy27_revenue` (1 row), `fy27_growth`
(1 row). Confirmed columns, `window`/`prior_basis` values, and the PIT rule
(vintage strictly before the target's print date — the two LIVE rows carry
`vintage_date=2026-09-11` for target `2026Q3`, whose print date is ~5 Nov
2026, so the rule holds) via the harness's own validator, not by inspection
only.

**Registry format: OK.**

## 3. Fix-by-fix verification (the six items round 1 required)

1. **A6 reworded into A6a/A6b.** Confirmed in `run.py` (lines ~204-225) and in
   `l1_acceptance_tests.csv`: A6a is explicitly framed as mean-vs-most-recent-
   observation, A6b as mean-vs-architect-headline-mean. Both PASS with the
   exact numbers quoted (A6b: 17.2394 vs 17.239, +0.0004pp). Fixed correctly.
2. **Kernel-weight sensitivity corrected to $117M.** `l1_kernel_weight_
   sensitivity.csv` (new file, present) contains
   `kernel_weight_fy27_sensitivity_musd = 117.31093...`, `pct_of_revenue =
   0.7407...`, `pp_of_growth = 2.3434...`, `w_lo/w_hi = 0.33/0.6667` —
   matches the note exactly. It is computed from `l1_fy27_revenue_grid.csv`
   at run time (grid confirms 15,720.3 → 15,837.6, spread 117.3), not
   hand-typed. Fixed correctly.
3. **`fx_pp_table` gained `as_of`, and `pit_point` rebuilds it per guide
   date.** Read `data.py:fx_pp_table()` directly: when `as_of` is given,
   `cut = as_of - 1 day` and basket rows are kept only where
   `qend_date(q) <= cut` (quarter-end strictly before `as_of`), and
   `intervals` are filtered to `knowable_from <= as_of` before the
   disclosed-pair lookup — exactly the harness FX rule. Read `run.py:
   pit_point()` directly: it calls `D.fx_pp_table(ivd, as_of=d)` on the
   already-`knowable_from`-filtered `ivd`, and the resulting `fxd` is what
   is passed into `M.Recon`. The full-sample call site (`fx =
   D.fx_pp_table(iv)` at line 67, `as_of=None`) is correctly reserved for
   the full-sample replay and the LIVE FY27 objects, which is legitimate
   (those are not PIT-scored). All 44 registered PIT rows are byte-identical
   pre/post-fix (§1), which is itself the evidence that the fix changed no
   registered number — consistent with round 1's diagnosis that the old
   code did not leak in practice. Fixed correctly, and the evidence for
   "no leakage before or after" is now doubly confirmed (round-1 reasoning
   + round-2 byte-identical rerun).
4. **"72 filed" relabelled "72 filed-or-exact-back-out."** Independently
   recomputed from `L0_exact_regional_revenue.csv` (loaded with
   `comment="#"` to skip its 5-line header): 72 rows total, `basis` value
   counts **56 filed / 16 back_out** — matches exactly. Note and A1 test
   string both use the corrected phrase.
5. **"16 clean annual nights cells" relabelled to a panel-window
   explanation.** Independently recomputed from `L0_interval_observations.
   csv`: `metric == "nights_m"` gives 24 rows, spanning FY2020-FY2025,
   **all `basis == "filed"`, all `included == True`** (no dirty subset) —
   matches the claim exactly. Only 16 (FY2022-FY2025) enter the fit because
   the panel starts 2022Q1; that boundary claim is consistent with the
   panel's own stated 18-quarter span (2022Q1-2026Q2). Note and A2 test
   string both use the corrected phrase.
6. **Ladder/headline ADR-weight caveat.** `l1_feasibility_ladder.csv` now
   carries an `adr_constraint_weight` column, value `1.0` on every stage,
   confirming the ladder fits ADR at full weight (a genuine feasibility
   test) versus the headline fit's `W_CONF["adr"] = 0.25` (confirmed by
   reading the `W_CONF` dict in `run.py`, line 38). The two different
   worst-gap figures (ladder 7.3/4.1pp vs headline 8.25/4.57pp) are now
   attributed to this weight difference in the note's §2.2. Fixed
   correctly.

All six items were independently reproduced from the regenerated CSVs and
the code, not merely re-read from the note's own text.

## 4. Leakage audit (re-checked, not re-trusted from round 1)

Re-examined the same seven risk classes the orchestrator brief names:

1. **Consensus vintages.** `STREET_FY27_LO/HI = 15730.0/15760.0` (only
   occurrence of a Street number in `run.py`) is used exclusively at lines
   ~377-383, inside the A9 acceptance test and headline text on the LIVE
   `fy27_revenue`/`fy27_growth` objects (`window=LIVE, vintage_date=
   2026-09-11`, which score in nothing). Never consumed inside `pit_point`
   or `Recon`. Not leakage.
2. **`basis == 'derived'` rows.** Confirmed mechanically: 14 rows in
   `L0_interval_observations.csv` have `basis == 'derived'`, and all 14
   have `included == False` (0 rows with `derived` and `included == True`
   co-occur). These never enter a likelihood. Not leakage.
3. **Quarter-end KPI/GBV used before its print date.** `pit_point` builds
   `hist = [q for q in qs if qorder(q) < qorder(target_q)]` from `qs`,
   which is itself derived only from `exd = ex[ex.knowable_from <= d]`.
   The take rate used for the one-quarter-ahead roll comes from
   `pan[pan.quarter == lastq]` where `lastq` is the last element of `hist`
   — strictly before the target, itself gated by `knowable_from`. No
   leak observed.
4. **Letter integers scored as points.** Every constraint class is scored
   through a `[lo, hi]` hinge; A2's own test string explicitly says
   "inside ±0.5M," not equality. Confirmed in the acceptance-test detail
   text and the constraint-builder code path (unchanged from round 1).
5. **FX table point-in-time cut.** Covered in detail under Fix 3 above —
   now genuinely rebuilt at `d-1` inside the PIT loop, closing the round-1
   hygiene gap. Not leakage before or after.
6. **`include_same_day` convention.** Unchanged, and correctly attributed
   in the docstring to "the harness's ratified include_same_day
   convention" — this is a harness-level policy (confirmed present in
   `harness/loaders.py` by round 1's direct read), not something this
   package invented or should unilaterally change.
7. **Just-printed quarter's GBV used before its print date.** No occurrence
   found; same code path as item 3.

**No leakage found, in either the fit or the registered forecasts.**

## 5. Number check (eight items independently recomputed from the CSVs)

| # | claim | recomputed from disk | match |
|---|---|---|---|
| 1 | kernel-weight sensitivity $117.3M / 0.74% / 2.343pp | `l1_kernel_weight_sensitivity.csv`: 117.31093, 0.7407, 2.3434 | match |
| 2 | A6a/A6b all four pass with the exact deltas quoted | `l1_acceptance_tests.csv` reproduces every delta to the note's precision (e.g. Q3 A6b +0.0004pp) | match |
| 3 | 72 exact cells = 56 filed + 16 back_out | `L0_exact_regional_revenue.csv` basis counts: 56 filed, 16 back_out | match |
| 4 | 24 annual nights cells, all filed/included, only 16 in-window | `L0_interval_observations.csv` nights_m: 24 rows, 100% filed, 100% included | match |
| 5 | 14 derived rows, 0 included | `L0_interval_observations.csv`: 14 derived, 0 derived&included | match |
| 6 | ladder `adr_constraint_weight` = 1.0 vs headline `W_CONF["adr"]` = 0.25 | `l1_feasibility_ladder.csv` column = 1.0 throughout; `run.py` line 38 `W_CONF = dict(..., adr=0.25, ...)` | match |
| 7 | scoreboard RMSE ratios 11.338/10.927/11.338/10.093, CRPS 835.8/616.2/835.8/721.1, coverage 0.70/0.64/0.70/0.70, n_params=68 | rebuilt `scoreboard.csv` via `harness/score.py`: identical to 3 decimals on every field | match |
| 8 | A7/A8 diffs: geo-mix -0.14/+0.11/+0.10pp; within-ex-FX -0.50/-1.43/-0.28pp | `l1_annual_adr_decomposition.csv`: `diff_mix_pp` = -0.1368/+0.1094/+0.0997; `diff_within_pp` = -0.4976/-1.4312/-0.2802 | match |

No mismatches found in this round (round 1's single minor mismatch, $118M vs
recomputed $117M, was the thing fixed).

## 6. Acceptance tests

Re-ran the full pipeline (§1) and cross-checked `l1_acceptance_tests.csv`
against independently recomputed source numbers (§5). A1-A7, A6a, A6b and A9
pass with matching residuals; **A8 genuinely still fails** (2024 gap
-1.4312pp, reported as -1.43), an honest, unhidden failure. No acceptance
test was marked passed without a recomputable, matching number behind it —
every "passed: true" in the implementer's self-report was independently
reproducible from disk this round, including the two new/reworded ones
(A6a, A6b).

## 7. Honesty of the interpretation

High, and improved from round 1. The implementer did not touch any
registered number to make the fixes land — the byte-identical rerun is
itself evidence of that discipline — and every item round 1 flagged was
either genuinely fixed (framing, mislabeling, the FX hygiene gap, the
kernel-sensitivity rounding) or left open with the same honest reasoning
round 1 already validated (A8, the G2 fourth-class inconsistency, HCR-1/2,
`include_same_day`). Nothing was papered over: A8 is still reported failing
with the same magnitude, the negative-control framing on
`revenue_contemporaneous` (11x worse than naive, survives neither window) is
unchanged and still correctly labelled as a negative control rather than a
forecast, and the new `adr_constraint_weight` column makes the
ladder-vs-headline distinction machine-checkable rather than merely
asserted in prose.

## 8. Verdict

**PASS — safe to score and quote.**

All six round-1 items were verified fixed against source: three by direct
code inspection (Fix 3's `as_of` mechanics, Fix 6's `W_CONF`/ladder-weight
split, Fix 1's A6a/A6b code), two by independent recomputation from the L0
files (Fix 4's 56/16 revenue-cell split, Fix 5's 24-filed/16-in-window nights
claim), and one by recomputation from the FY27 grid (Fix 2's $117M). The
full pipeline reruns byte-identical end to end (exit 0, ~180s), all three
registry files validate against the harness's own validator, the rebuilt
scoreboard reproduces every quoted metric to three decimals, no leakage was
found in a fresh audit of all seven risk classes, and the one genuine
failure in the package (A8) remains honestly reported and unchanged.

No caveats remain that were not already disclosed by the implementer:
A8 fails (reported); the G2 fourth disclosure class (regional ADR y/y) is
mutually inconsistent with the other three under any smooth take rate
(reported, not relaxed); `revenue_contemporaneous` loses to naive by 11x and
is a deliberate negative control, not a forecast; regional ADR levels are
weakly identified (bootstrap ±15%), which is why only GBV crosses the L1
boundary; FY27 booking-date FX is a flat-spot-carry assumption, not a
measurement; HCR-1/HCR-2/HCR-3 are genuine harness limitations, not
implementer error. All of these were true at round 1 and remain true,
unchanged, after the fixes — which is exactly what "byte-identical
registered outputs" predicts.
