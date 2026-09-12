# VERIFY fx-lag — round 2

Verifier run: 2026-09-11. Independent re-run and audit of the implementer's round-2 report against
`docs/revenue-forecast-strategy/05_backtests/fx-lag.md`, the code in
`analysis/src/forecast_methods/fx_lag/`, the outputs in `data/processed/forecast_methods/fx_lag/`,
and the three registry files under `data/processed/forecast_methods/registry/`.

## Verdict: PASS (safe to score and quote), with the caveats already named in the note carried forward

The round-1 defect (full-sample-prior replay silently reusing PIT points) is genuinely fixed, not
relabelled. Every number I re-derived independently from the CSVs matches the note to the printed
precision. The registry format is valid. No new leakage found. The honesty of the interpretation is
high — failed reproductions are reported as failures, caveats are named rather than smoothed over,
and no result is stated more strongly than the sample size supports.

## 1. Re-run

Moved the existing `data/processed/forecast_methods/fx_lag/` contents and the three registry files
to sibling `_prev` locations, then ran the entry point fresh from the repo root with the pinned
interpreter:

```
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/fx_lag/run.py
```

Exit code 0. Wall time about 21 seconds (close to the note's "about 25 seconds"; the ~4s gap is
run-to-run machine noise, not a discrepancy worth flagging). Console printed the regression-guard
line: `replay check: max |point delta| = 6.5733pp, 0 of 96 rows identical`, matching the note.

`diff -rq` between the fresh output directory and the pre-run copy: zero differences across all 28
data files. All three registry CSVs byte-identical to their pre-run copies. Determinism confirmed
independently, matching the implementer's claim exactly.

## 2. Registry format check

Loading the three registry files and calling the harness's own `validate_registry_frame` on the raw
CSVs on disk throws an "unknown columns ['format_version']" error — but this is because `register()`
in `harness/registry.py` calls `validate_registry_frame` on the dataframe BEFORE appending the
`format_version` column and writing (confirmed by reading `registry.py` lines 150-227). The presence
of `format_version` in the written CSV is the harness's own post-validation addition, not a package
defect. Validation genuinely passed at write time: `run.py`'s console output shows
`registered 40 rows`, `registered 48 rows`, `registered 2 rows` with no RegistryError raised, and the
two coverage warnings that did print are the expected, documented ones (H2 W1 covers 10/14 quarters
because its ADR-FX driver starts 2Q22) — they are warnings, not validation failures, and the note
reports them accurately as "not quotable as a W1 winner" rather than suppressing them.

All required columns present (`method`, `object`, `target`, `quarter`, `vintage_date`, `horizon_q`,
`point`, `q50`, `window`, `prior_basis`, `n_params`, `n_train`); optional columns filled where
applicable; `street_vendor`/`street_as_of` correctly absent (no consensus number is consumed
anywhere in this package — confirmed by grep, see §3). `n_train` is now correct per `prior_basis`:
independently recomputed, PIT rows range 5-14 (h2) and 7-20 (h3); full-sample rows are 14 throughout
for both objects — matches the note's claim exactly.

## 3. Leakage audit

- **Consensus/Street from Sep 2026 used as historical pre-guide Street**: not applicable — this
  package consumes no consensus data anywhere. `grep -n "street\|consensus"` across the package's
  `.py` files shows only one hit, in `stages.py`'s `four_way_reconciliation()`, which reads the
  repo's own precomputed `05_fx_schedule.csv` "consensus" path purely for a reconciliation exhibit
  (§9 of the note) explicitly labelled "REJECTED as an input" — it is never fed into a registered
  forecast. `street_vendor`/`street_as_of` are correctly absent from the registry.
- **Quarter-end data used at a guide date preceding filing**: `pit_fx.py` builds the target quarter's
  basket from FRED FX through `asof` (day before the guide) with spot held constant thereafter, and
  filters `L0_exact_regional_revenue.csv` on `knowable_from <= asof`. Read the source directly and
  confirmed this is implemented as described, not just asserted.
- **Full-sample priors replayed as if PIT**: this was the round-1 bug; independently confirmed fixed.
  See §4.
- **Just-printed quarter's GBV used before its print date**: the only GBV figures used (in
  `exfx_acceleration()` and `kernel_carried_fx()`) are explicitly-labelled scenario assumptions for
  3Q26 ("frozen card", "architect central", "low", "high") used to illustrate the ex-FX-acceleration
  arithmetic in §8 of the note, not fed into any registered forecast — and 3Q26 has not printed as of
  the run date, so there is no actual figure that could leak.
- **Letter integers scored as points**: Object A and the ADR-FX stage-b fits are explicitly scored on
  the interval likelihood `[x-0.5, x+0.5]` / `[x-0.05, x+0.05]`, confirmed in `fits.py` and reflected
  in the note's explicit statement that 40% of apparent revenue-FX error is rounding, not model error.
- **`basis == 'derived'` rows**: not applicable to this package's inputs. This package uses
  `L0_exact_regional_revenue.csv`, not the regional nights-band panel that carries the `derived`
  basis value. Independently read `L0_exact_regional_revenue.csv`: `basis` takes only `filed` (56
  rows) and `back_out` (16 rows); zero rows tagged `derived` or `restated`, matching the note's and
  `00_pit_caveats.csv`'s claim exactly.

No leakage found.

## 4. Fix verification — the round-1 defect

Independently recomputed the PIT-vs-full-sample replay comparison directly from the two registry
CSVs (joining on `quarter`, `vintage_date`, `window`, pivoting on `prior_basis`, taking absolute
point deltas):

- `fx-lag__fx_rev_next_q_h2.csv`: **20 matched triples, max abs delta 0.5013pp, 0 rows identical.**
  PIT `n_train` mean 9.5 (range 5-14); full-sample `n_train` constant 14.
- `fx-lag__fx_rev_next_q_h3.csv`: **24 matched triples, max abs delta 2.6195pp, 0 rows identical.**
  PIT `n_train` mean 14.3 (range 7-20); full-sample `n_train` constant 14.

Both numbers match the note's claims exactly ("h2 max PIT-versus-full delta 0.5013pp over 20
triples, h3 2.6195pp over 24"). This directly refutes the round-1 failure mode (byte-identical
points across `prior_basis`) and confirms the fix is substantive, not cosmetic.

## 5. Number check — six-plus figures recomputed from the CSVs

| # | claim in note | recomputed from | match |
|---|---|---|---|
| 1 | Object A gross scale 0.9515, sigma 0.8783, eff. lag CS [0.029, 0.923] | `06_object_a_summary.csv` row 1 | exact |
| 2 | H0 architect-Phi LR 16.762, p 0.0008 (gross); LR 10.214 (~10.2), p 0.0168 (~0.017) (stated) | `06b_object_a_hypothesis_tests.csv` | exact |
| 3 | H2 W1 RMSE 0.9936, bias +0.0975, interval RMSE 0.5782, n=10 | `09c_pit_window_scores.csv` | exact |
| 4 | H3 PIT W2 RMSE 1.70 vs W1 1.49; full-sample W2 0.82 vs W1 1.00 | `09f_replay_delta_pit_vs_full.csv` (1.6974/1.4854/0.8237/0.9996) | exact (to 2dp) |
| 5 | FY27 spot-held: simple mean +0.22, revenue-weighted +0.22, weak-USD +2.3, strong-USD -2.0 | `11b_fy27_annualisation.csv` | exact (0.9/4=0.225->0.22 rounding, file column shows 0.2 to 1dp — consistent) |
| 6 | Replay: h2 max delta 0.5013pp/20 triples, h3 2.6195pp/24 triples | independently recomputed from registry CSVs, §4 above | exact |
| 7 | Repo `05_fx_fits.csv` rev_fx row: n=13, slope -0.5348 (usd_broad, post22) | read `data/processed/overnight/05_fx_fits.csv` directly | exact — the "does not reproduce" claim (my n=14) is a real, correctly-reported failure, not an excuse |
| 8 | Determinism: two runs byte-identical, 28 data files + 3 registry files, exit 0 | independent `diff -rq` on a fresh third run | exact |

No mismatches found in any of the eight numbers checked.

## 6. Acceptance tests — spot-checked against evidence

All ten acceptance-test rows in the implementer's report were checked against the actual output
files rather than taken on faith. All "passed" rows have direct file evidence (see §1-§5 above); the
three "failed" rows (repo rev_fx reproduction, Object C slope reproduction, H2 full-W1 coverage) are
genuinely unreproduced/unresolved on independent inspection, not papered over — confirmed by reading
the repo's own `05_fx_fits.csv` (§5, row 7) and by the registry's own `n_train` distribution showing
H2's PIT rows start at n_train=5 only from a later vintage date (consistent with a 2Q22 driver start
and a five-row gate not being met until roughly the 2024-02 guide, as claimed).

## 7. Honesty assessment

The note is unusually disciplined for a self-report: it downgrades its own prior acceptance-test
line rather than re-passing it quietly, states standard errors alongside every RMSE comparison and
explicitly warns against reading a winner off tables where separations don't clear 1-1.5 SE, keeps
four round-1 failures open rather than declaring victory, and states the practical implication of
each caveat (e.g., "no downstream package should treat the point weights as identified" at 3.5
obs/parameter). The interpretation in §6.3 of the note (hindsight premium larger than any
spec-vs-spec difference) is exactly what the recomputed `09f` numbers show. I found no place where
the prose overstates the underlying numbers.

## Residual caveats (unchanged from the note, correctly carried forward — not new findings)

- Repo `05_fx_fits.csv` rev_fx rows still don't reproduce (n 13 vs 14); unused downstream.
- Architect Object C slope (0.389 vs 0.158) still doesn't reproduce on any of 8 conventions tried;
  n, se, and the |t|<2 conclusion do.
- H2 covers only 10/14 W1 quarters (driver starts 2Q22); not quotable as a W1 winner under the
  survives-both-windows rule — this is a property of the data, not a code defect.
- LIVE registration blocked past 2026Q3 by the harness windows file; FY27 has no annual target slot.
  Both harness change requests remain open and are reasonable asks, not workarounds papering over a
  real gap (the un-registrable rows are written out separately rather than forced into the wrong
  window label).
- FRED daily file ends 2026-08-28; nothing in this package is genuinely "as of 2026-09-11" (11 Sep).
- Fitted basket scale (0.95 gross) implies the judgement currency weights understate true exposure
  by roughly 70% versus the disclosed 0.56 non-USD revenue share — a programme-wide caveat, correctly
  flagged for any package using this basket for a level rather than a change.
- R engine cross-check still skipped, stated as such.

None of these block scoring; all are named plainly enough that a reader of the memo or model would
not be misled.
