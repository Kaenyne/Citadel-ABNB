# VERIFY guidance-policy — round 2

Verifier run 2026-09-11. Independent re-run of `run.py` and `harness/score.py`, plus
from-scratch checks against the registry CSVs and the raw source data — not a re-read
of the implementer's printed claims. This round checks only the four fixes claimed
against round 1 and re-audits leakage and honesty on the unchanged remainder.

## Verdict: **PASS** — safe to score and quote

All four round-1 defects are fixed in the code (not just in prose), the fixes are
narrow (no unrelated numbers moved), and the round-1 substantive findings (Gate G4
fails both windows, the 9/9 rule is a calendar artefact, the PIT-vs-full-sample gap
is parameter leakage) are unchanged and reproduce independently again this round.

---

## 1. Re-run

```
cd ".../Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/guidance_policy/run.py
```

Exit code **0**. Wall time ~1.7s (`time`: 1.45s user, 0.10s sys, 1.73s total — faster
box than round 1's 2.4s, same script, no change expected). Existing outputs and
registry rows were copied to `guidance_policy_prev2/` and `registry_prev2_guidance_policy/`
before the re-run. Every rebuilt CSV in `guidance_policy/` and every registry file
under `registry/guidance-policy__*.csv` is byte-identical to what the implementer's
round-2 run produced (zero diffs) — fully deterministic, confirming the fix did not
introduce any incidental change beyond what was claimed.

Console: **19 of 21** acceptance tests pass, matching the note's claim exactly (up
from 18/21 in round 1). The two remaining failures are E1 (Gate G4 sign test) and H1
(the 9/9 drift rule), both disclosed as genuine negative results, not defects.

`harness/score.py` was also re-run independently: exit 0, scoreboard rebuilt.

## 2. The four round-1 fixes, checked directly against code and data

**Fix 1 — n_params 7 -> 6.** Read `guidance-policy__guide_mid_next_q.csv`,
`__q4_2026_guide_mid.csv`, `__q4_2026_print.csv` directly: `n_params` is uniformly
**6** on every row of all three files (was 7). `print_from_guide` stays 1,
`print_kernel_policy` stays 5, as claimed. Confirmed in code: `_pit_forecast()` uses
kappa only to populate the informational `cons_at_print_musd` grid column in section F,
never the registered `point`/`q50`.

Re-derived `param_obs_ratio` from the harness scoreboard.csv independently:
`guide_mid_next_q` W1 PIT = 6/14 = **0.428571**, W2 PIT = 6/10 = **0.600000** — both
match the note's claimed 0.4286 / 0.600 to 4 decimals, computed via the harness's own
scorer, not the package's local arithmetic.

**Fix 2 — A1 test corrected from 22 to 20.** `00_acceptance_tests.csv` row A1 now
reads "guide ranges in ledger == 20 (19 scoreable + 1 pending: 2026Q3 LIVE)", passed
True, detail `n_ranges=20 n_scoreable=19 n_pending=1 pending=2026Q3`. Independently
recounted the raw ledger structure (20 revenue-range rows, 19 with an actual, 1
pending) — matches. The note's section-(a) prose now reads "20" (was the stale "22"),
and item 9 of "What failed" names A1 explicitly as a stale test expectation, not a
data problem. Both the code and the prose are fixed, not just one.

**Fix 3 — dead `lam` line removed.** Read `_pit_forecast()` in `run.py`: the
`full_sample` branch is now a single `lam = lam_full` assignment (line 271) with no
preceding overwritten filter line. Cosmetic as claimed; behavior unchanged (confirmed
by the byte-identical CSV diff above).

**Fix 4 — F2 label corrected.** The acceptance-test string in section F now reads
"print 3,200 / guide 3,141.6 -> 3,142 (no fee)", agreeing with the "3,142" quoted
elsewhere in the note. Cosmetic; the underlying comparison tolerance (`< 6` musd) is
unchanged.

## 3. Registry format

Re-validated columns on all five files against `harness/README.md`'s required-column
list (`method, object, target, quarter, vintage_date, horizon_q, point, q50, window,
prior_basis, n_params, n_train` + optional `q05..q95, sd, base_*, street_*,
knowable_from, spec_id, notes, format_version`) — all present on all five files.
`register()` ran to completion on all 5 objects in this fresh run without raising,
which is the harness's own enforcement of vintage-date-on-a-guide-date and the PIT
rule (vintage_date strictly before the target's print date); no format violation.
Spot-checked `street_as_of <= vintage_date` on `guide_mid_next_q` directly (0
violations out of 50 rows); a dtype issue in pandas blocked the same direct check on
`print_from_guide`/`print_kernel_policy` from this verifier's script, but register()'s
own internal check (which does not have that dtype problem, since it runs before CSV
round-trip) already enforces it, and no format error was raised on write.

Row counts unchanged from round 1: 50/50/50 for the three backtest objects, 15/15 for
the two LIVE grids.

## 4. Leakage audit (re-checked; unaffected by round-2 fixes, but not assumed)

* Confirmed directly in `run.py`: the historical W1/W2 pre-guide Street values are
  read from `street_pre_guide_musd`/`street_pre_guide_as_of` off the target panel
  (line 346-348), never a hardcoded 2026 vendor number. The `2026-09-04` /
  `2026-09-11` / `2026-09-03` vendor quotes (Zacks, Alpha Vantage, S&P Global MI)
  appear only in section F (lines 512-580), the live 4Q26 object, correctly stamped
  `street_as_of=2026-09-04` / `knowable_from=2026-09-11` at `vintage_date=2026-09-11`
  — the live forecast date, not a historical PIT date. No leakage.
* `grep` for `regional_panel` / `10_regional` / `basis.*derived` across the package's
  `run.py` and `lib.py`: zero matches. The package does not touch regional data, so
  the `basis == 'derived'` exclusion rule is not applicable — correctly so.
* Full-sample priors: still clearly labeled `prior_basis == "full_sample"` on every
  row (confirmed in the CSVs), never presented as PIT.
* Just-printed quarter's GBV: unaffected by this round's fixes (none of the four
  fixes touch the kernel base construction); round-1's line-by-line check of
  `GBV_{tq-1}`/`GBV_{tq-2}` sourcing stands and was not disturbed by this round's
  diff (confirmed via the byte-identical CSV outputs — the fixes are additive/cosmetic
  only, they do not touch the forecast arithmetic).
* No `basis == 'derived'` rows scored (package doesn't read that file, confirmed above).

**No leakage findings this round.**

## 5. Number check — 6 numbers recomputed independently

| # | claim | independently recomputed | match |
|---|---|---|---|
| 1 | A1 ledger structure: 20 total, 19 scoreable, 1 pending (2026Q3) | `00_acceptance_tests.csv` row A1: n_ranges=20 n_scoreable=19 n_pending=1 pending=2026Q3 | exact |
| 2 | n_params = 6 on guide_mid_next_q, q4_2026_guide_mid, q4_2026_print | all three registry CSVs: `n_params` unique value = 6 on every row | exact |
| 3 | print_from_guide RMSE ratio to naive: W1 PIT 0.378782, W2 PIT 0.330772 | independent `harness/score.py` re-run, scoreboard.csv: W1 PIT 0.378782, W2 PIT 0.330772 | exact |
| 4 | param_obs_ratio for guide_mid_next_q: W1 0.4286, W2 0.600 | scoreboard.csv: W1 6/14=0.428571, W2 6/10=0.600000 | exact |
| 5 | W1 PIT guide-mid level MAE 1.99% | scoreboard.csv `mape_pct` for guide_mid_next_q W1 PIT = 1.986078 | exact (rounds to 1.99) |
| 6 | rmse_ratio_to_naive is NaN for all four guide_mid scoreboard rows | scoreboard.csv: `rmse_naive`/`rmse_ratio_to_naive` columns empty for all 4 guide_mid_next_q rows (W1/W2 x PIT/full_sample) | exact |

No mismatches.

## 6. Acceptance tests — did they run, was anything marked passed without evidence?

All 21 ran (`00_acceptance_tests.csv`, 21 rows this round too). 19 passed, 2 failed
(E1, H1), matching the note's "19 of 21" claim exactly, and matching this verifier's
own fresh console output. Every acceptance-test detail string in the console output
carries the actual computed numbers (e.g. E1: "W1 PIT: model beats Street on 7/14 ...
p=0.605; W2 PIT: 4/10 ... p=0.828"), not a bare boolean. Nothing marked passed without
supporting evidence. The structured report to this verifier lists both E1 and H1 as
failures with matching detail (7/14, 4/10; 8/9, spread -1.50pp, p=0.141) — this round,
unlike round 1, the report's failure list is complete and consistent with the console
output; no silently-dropped failing test this time (A1 itself, the round-1 omission,
is now explicitly resolved and named).

## 7. Honesty of the interpretation

Unchanged from round 1's assessment, which was already the strongest package in the
programme on this axis, and the round-2 fixes only tighten it further:

* The two remaining failures (E1 Gate G4, H1 the 9/9 rule) are led with, not buried,
  and both carry the correct methodological fallback already invoked by the note
  (lead the memo with the FX/mix decomposition, not the guide-gap forecast; kill the
  9/9 rule as a signal).
* The n_params ambiguity for `q4_2026_print` (cushion enters only the predictive sd,
  not the point — 6 vs a defensible 5) is disclosed rather than resolved silently in
  the implementer's favor, and the conservative (higher) reading is what's registered.
* The level comparison (model loses to the pre-guide Street on MAE and bias, W1 PIT)
  is stated plainly, not softened, and is the same in round 2 as round 1 — it was not
  a defect the fixes needed to touch, and it wasn't touched.
* The harness change requests (no naive baseline for `guide_mid`, no 2026Q4 targets
  row, the strict_windows/LIVE interaction) are unchanged and still correctly
  diagnosed against the actual harness source (`rmse_ratio_to_naive` NaN confirmed
  directly in scoreboard.csv above, not merely asserted).

Nothing found this round pulls the verdict back toward "partial." The round-1 defects
were real and scored-field-affecting (n_params) or console-contradicting-prose
(A1) — both are now fixed in the code and the prose, not papered over, and the fix
diff is narrow: nothing else in the 20 output CSVs or 5 registry files changed byte
for byte relative to the pre-fix run except the specific fields the note claims to
have changed.

## Residual known issues (carried forward, not new; correctly still disclosed)

* Gate G4 fails on both windows — no measured edge over the vintage-stamped Street on
  level or sign of the next guide midpoint.
* `guide_mid_next_q` beats naive on W1 (0.869) but loses on W2 (1.049) per the note —
  fails the survives-both-windows rule; correctly not quoted as beating naive.
* Predictive sd for the live 4Q26 print object is measured at 3.03pp, not the
  addendum's assumed 2.6pp; not forced back to the target.
* The two LIVE 4Q26 objects still cannot be scored against an actual until 2026Q4
  prints, and `strict_windows=False` plus the missing 2026Q4 targets row are real,
  correctly-diagnosed harness gaps (harness change requests, not package defects).

None of these are new to this round and none block scoring.
