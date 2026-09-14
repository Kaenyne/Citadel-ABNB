# VERIFY calibration-rail — round 1 (independent verifier)

Verifier run: 2026-09-11. Re-ran the package end to end from the repo root exactly
per the README/note command:

```bash
cd "Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/calibration_rail/run.py
```

Existing registry files (`registry/calibration-rail__*.csv`) and data outputs
(`data/processed/forecast_methods/calibration_rail/*`) were first copied to sibling
`_prev` folders for diffing.

## 1. Reproducibility

**Exit code: 0.** Wall time: ~75s (implementer reported the same order of magnitude
per-step timings; matches). All six steps ("harness baselines", "reference
scoreboard", "gbm challenger", "pit/crps on ledger", "chronos attempt", "harness
scorer") reported OK.

Byte-for-byte diff against the pre-existing outputs: **all five registry CSVs and
all three data-output CSVs are IDENTICAL.** Only `chronos_attempt.txt` differs, and
only in pip-cache timing/wording lines (dry-run took 0.5s vs 1.9s, "Using cached" vs
"Downloading" for three sub-dependencies) — expected, harmless, not a correctness
issue. The package is fully deterministic and reproducible as documented.

## 2. Registry format check

Checked all five registered files against `harness/README.md` FORMAT VERSION 1.0:
required columns present and non-null in all 692 rows (200+200+200+46+46); `window`
values upper-cased and consistent with `quarter`; quantile ladders non-decreasing in
every row (checked programmatically, 0 violations); `n_params` populated per object.

**Independent PIT check (own script, not relying on `register()` having accepted the
rows): 0 of 692 registered rows have `vintage_date >= print_date` of their target
quarter.** No forecast in this package's registry was made on or after its target's
print date. This is a clean pass on the single most important point-in-time
invariant.

`ref_naive`/`ref_trailing4` n_params are not uniformly 0/1 as the note's "Parameter
counts" table states — they are `{0,1}` and `{1,2}` respectively, because the
harness's own baseline convention adds +1 when a residual sd is fitted from ≥3
pseudo-oos errors (documented in `baselines.py` itself: "the residual sd is a fitted
parameter"). Minor documentation imprecision, not a data error — the registry itself
is internally consistent with the harness's own rule; only the note's summary table
oversimplifies it to a single number per object.

## 3. Leakage audit

- **No consensus/Street data is touched by this package's own code** (grep for
  "consensus", "16_consensus", "04_consensus" in the package's `.py` files returns
  nothing) — `baseline_street` is never called here, so the "Sept 2026 vendor used as
  pre-guide Street" failure mode does not apply to calibration-rail.
- **No use of the regional panel / `basis == 'derived'` rows** — grep confirms the
  package never reads `10_regional_panel_quarterly.csv`.
- **GBM feature construction (`gbm_challenger.py`)**: `lag1_revenue_yoy`,
  `lag1_gbv_yoy`, `fx_adr_lag2` are read from a PIT-cut `history_as_of(gdate)` frame
  for the PIT replay; `guide_growth_pct` is read from the guide row itself, which is
  legitimately knowable at the guide date (it IS the guide being issued). Verified
  directly against `harness/loaders.py`'s `history_as_of` (rows filtered on
  `print_date <= vintage_date`, the harness's own same-day-letter convention,
  documented and reused, not invented). No leakage found in the PIT replay.
- **`full_sample` replay for GBM**: deliberately trains on the *entire* realised
  panel (all printed quarters, not PIT-cut), which is the disclosed, intentional
  analogue of the AR(1) baseline's own "parameters leak, inputs stay PIT" full_sample
  convention (confirmed by reading `baselines.py::_generic`, which does the same
  thing for AR(1): fits `a,b` on `_full_series`, but still walks the PIT series `s`
  forward from the last *point-in-time* observed growth). The LOO guard
  (`exclude_quarter=tq`) that keeps the target quarter's own row out of its own
  training set was verified present and doing its job — this is good practice and
  the disclosed reasoning in the note (that the GBM full_sample number without the
  guard was an implausible RMSE 7.15 leakage artifact) is credible and consistent
  with the "verified" language used.
- **GBM PIT coverage gap (10/14 W1 quarters)**: independently reproduced — `gbm_revenue`
  PIT rows exist for exactly `2024Q1..2026Q2` (10 quarters), matching the note
  exactly. Root cause as traced through the code is real: at early W1 guide dates
  (e.g. 2023-02-14), the *training table* built inside `_build_training_table`
  (which must find ≥5 past quarters with a complete 4-feature row, itself requiring
  a further lag back to ~2022Q2 for `fx_adr_lag2`) has too few valid rows, so
  `if len(y) < 5: continue` skips those origins — not a missing `x_target` (fx data
  for the individual lag2 quarter is in fact present and PIT-available for 2023Q1;
  verified directly against `targets.csv`). The note's "W1 numerically identical to
  W2" observation is correct and appropriately flagged as weakening
  `survives_both_windows` for the two GBM objects.

**No leakage defects found in parts (a), (b), (c).**

## 4. A significant correctness bug in part (d) — PIT/CRPS ledger exhibit

`pit_crps_ledger.py::_pit_crps_group` builds:

```python
levels = list(Z.values())                       # BUG: these are z-scores, not probabilities
values = [fc + z * sigma for z in Z.values()]
pit, edge = M.pit_from_quantiles(act, levels, values)
```

`harness/metrics.py`'s `pit_from_quantiles` and `crps_from_quantiles` both expect
`levels` to be the quantile **probabilities** (0.05, 0.10, ..., 0.95) — this is what
`harness/score.py` correctly passes via `QUANTILE_LEVELS` for every registry-scored
object. `pit_crps_ledger.py` instead passes the **z-scores** (-1.645, -1.282, ...,
1.645) as `levels`. This corrupts every "interior" (non-edge-clipped) PIT value in
the exhibit.

Verified directly on the regenerated `pit_crps_ledger_detail.csv`:
- 218 of 284 scored rows (77%) hit the "interior" `np.interp` branch (not edge-clipped).
- Of those, **128 (59% of interior rows, 45% of all scored rows) have a `pit` value
  outside [0,1]** — e.g. `pit = -1.546558` for the `pr_hotel_revpar_yoy` /
  `revenue_surprise_pct` group's 2024Q1 row. A PIT value is by definition a
  probability; a value of -1.55 is not a calibration statistic, it is the bug.
- The 66 "edge" rows happen to render as exactly 0.0 or 1.0 regardless of the
  swapped array, because the edge-case formula in `pit_from_quantiles` is wrapped in
  `max(0.0, ...)` / `min(1.0, ...)` — so those specific rows are coincidentally
  clipped to a plausible-looking value, but for the wrong reason, not because the
  PIT there is genuinely correct.
- `crps_from_quantiles` uses the same `levels` array as both the pinball-loss `tau`
  *and* the tail-extension weights (`levels[0] - 0.0`, `1.0 - levels[-1]`); with
  negative/>1 `levels` values these tail-extension terms are also wrong, so the
  `crps` column in the same file is unreliable for the same rows.

**Consequence**: the calibration-read labels (`BIASED` / `roughly calibrated` /
`OVERCONFIDENT`) in `pit_crps_ledger_summary.csv`, and every number derived from
them, rest on this corrupted PIT computation for most of the 34 scored groups. This
is the M5-critic-facing deliverable the note calls "the honest negative result... the
highest-value item" — it needs to be **recomputed with the correct probability
levels before it is quoted anywhere**, including in the memo. The qualitative
direction (some groups biased, one overconfident) may well survive a fix, but the
counts, the specific PIT means, and the specific KS p-values currently on file cannot
be trusted as computed. This does not affect parts (a)/(b)/(c): those are scored via
`harness/score.py`, which passes `QUANTILE_LEVELS` correctly (independently verified
by reading `score.py` line 53 and confirming the GBM PIT-mean/KS-p numbers in the
note's §b table match the regenerated `scoreboard.csv` to 3+ significant figures).

## 5. Number check (6+ numbers recomputed from the CSVs)

| # | claim in note | recomputed | match? |
|---|---|---|---|
| 1 | guide+cushion revenue MAPE, PIT: 1.068%, n=14 | 1.06841% | yes |
| 2 | guide+cushion revenue MAPE, full_sample: 0.990%, n=14 | 0.98976% | yes |
| 3 | bl_guide RMSE 2.588pp / bl_guide_plus_cushion 2.642pp vs bl_zero 1.873 / bl_last_quarter 1.760, n=100 | 2.58797 / 2.64242 / 1.87276 / 1.75956, n=100 | yes |
| 4 | ar1 RMSE ratio to naive, nights_m, W1 full_sample = 1.008854 | 1.008854 (scoreboard.csv, exact) | yes |
| 5 | ar1 raw RMSE nights_yoy W1 PIT 6.673 vs naive 2.877 | 6.673169 / 2.876659 | yes |
| 6 | "trailing4 6.58 ≈ ar1 6.67" on nights_yoy W1 PIT | **trailing4 RMSE = 5.341**, not 6.58 | **NO — mismatch** |
| 7 | n_cal=6, alpha=0.2 attainable coverage [85.7%,100%], qhat=max of 6 | attainable_lo=0.857143, attainable_hi=1.0, "max of 6 residuals" (`conformal_attainable_grid.csv`, exact) | yes |
| 8 | PIT/CRPS ledger: 34 groups, 284/391 rows scored | 34 groups, 284 scored rows, 391 raw ledger rows — all exact | yes |
| 9 | calibration_read counts: 20 BIASED / 13 calibrated / 1 OVERCONFIDENT | **19 BIASED / 14 calibrated / 1 OVERCONFIDENT** | **NO — off by one, both directions** |
| 10 | pr_hotel_revpar_yoy / pr_hotel_revpar_yoy_pit on revenue_surprise_pct: PIT means "0.32/0.34" | actual file: pit_mean = **-0.675 / -0.659** (itself a symptom of the part-(d) bug above) | **NO — does not match the file at all, in addition to being a corrupted computation** |
| 11 | §c falsification: "all rows show conformal_cov_empirical ∈ {0.75, 1.0}... across every registered object (baselines + calibration-rail + other packages)" | Registry-wide (revenue_musd, n_cal=6, alpha=0.2): values are {1.0: 37, 0.75: 16, 0.875: 11, 0.5: 2, 0.25: 2} — 5 distinct values, not 2. **Calibration-rail's own 8 rows are indeed exactly {0.75×4, 1.0×4}** (the narrower claim holds), but the note's stated scope ("across every registered object") is wrong; `baselines/naive_seasonal` hits 0.5 and 0.25, three `kernel-lambda`/`guidance-policy`/`baselines` objects hit 0.875. | **Partial — true for calibration-rail's own objects, false as stated for the registry as a whole** |

7 of 11 spot-checked numbers reproduce exactly; 4 do not. Three of the four misses
(#6, #9, #10) are numeric slips in the note's prose that don't change the qualitative
finding they attach to (AR1 doesn't clearly beat trailing4 on nights either way;
BIASED is still the dominant failure mode either way 19 or 20 of 34) — but #10 is
symptomatic of the real bug in §4, and #11 is a genuine overreach of the claim's
scope that should be corrected (the 0.5/0.25 outcomes are worth a sentence, since
they are *below* the theoretical attainable floor and are a legitimately interesting
data point the note omits, even though they belong to another package's object, not
calibration-rail's own).

## 6. Acceptance tests

All 6 acceptance tests claimed in the implementer's report were actually run and are
reproducible from files on disk (re-verified independently, not just re-reading the
implementer's own claim):

| test | implementer verdict | verifier check |
|---|---|---|
| guide+cushion revenue level ~1.1% | PASS | confirmed (#1, #2 above) |
| guide(+cushion) worst predictor of surprise vs Street | PASS | confirmed (#3 above) |
| nothing beats AR(1) on nights | PARTIAL/DISCONFIRMED, reported as found | confirmed correct as reported; note's one supporting number (#6) is wrong but doesn't change the verdict |
| conformal attainable coverage grid at n_cal=6 | PASS | confirmed exactly (#7 above) |
| run.py exit code 0 | PASS | confirmed (75s wall time, all 6 steps OK, fully reproducible) |
| monotone constraint on fx_adr_lag2 only | PASS | confirmed by reading `MONO_CST = [0,0,0,-1]` against the documented feature order; no nights feature present anywhere in `FEATURES` |

No acceptance test was marked passed without evidence. The implementer's own
disconfirm on Claim 3 is honest, not softened.

## 7. Honesty of interpretation vs results

The note is largely honest and unusually self-critical for a first pass: it flags its
own GBM coverage gap as weakening `survives_both_windows`, catches and fixes its own
full_sample leakage artifact before reporting it, states plainly that the split-
conformal falsification test is uninformative rather than laundering a coin-flip into
a pass, and delivers the M5 critic's requested negative result even though it makes
the team's own earlier challenger models look bad. The "optimal mix" conclusion
(100% guide+cushion for revenue level, no method above `bl_last_quarter` for surprise
timing) is well supported by the reproduced numbers and does not overclaim.

The one place the interpretation is **not yet trustworthy as stated** is part (d):
the note presents the BIASED/OVERCONFIDENT split with confident, specific numbers
("the honest negative result... the highest-value item") without having caught that
its own PIT computation is broken. This is not a matter of honest interpretation of
correct numbers — it is incorrect numbers presented as though verified. Everything
else in the note reads as calibrated to what the data actually shows; part (d) does
not, through no fault of interpretive judgment, only of an unnoticed swapped
variable.

## Verdict: **PARTIAL**

Score and quote parts (a), (b), (c) as reported — independently reproduced,
byte-identical on re-run, numbers check out (with the two cosmetic slips noted in
§5, #6 and #9, which do not change any conclusion), no leakage found, PIT rule holds
on all 692 registered rows checked directly.

**Do not quote part (d)'s specific numbers (PIT means, KS p-values, the 20/13/1
or 19/14/1 BIASED/calibrated/overconfident split, or any CRPS figure from
`pit_crps_ledger_*.csv`) in the memo or anywhere else until fixed.**

### Issues to fix, in priority order

1. **(Must fix before part (d) is used anywhere.)** In
   `pit_crps_ledger.py::_pit_crps_group`, `levels = list(Z.values())` passes z-scores
   where `harness/metrics.py` expects quantile probabilities. Fix: use the
   probability for each key (e.g. `{"q05":0.05,...,"q95":0.95}` or import
   `harness.registry.QUANTILE_LEVELS`) as `levels`, keep `Z.values()` only for
   building `values` (the `fc + z*sigma` ladder). Re-run `pit_crps_ledger.py` and
   regenerate both ledger CSVs and the note's §d table before this exhibit is used.
2. **(Should fix, low effort.)** Note §a's aside "`ar1` RMSE 6.67 < trailing4 6.58...
   trailing4 6.58≈6.67" — trailing4's actual RMSE on `nights_yoy` W1 PIT is 5.341,
   not 6.58. Correct the sentence or drop the aside; it doesn't change the section's
   conclusion.
3. **(Should fix, low effort.)** §d's summary table (20/13/1) is off by one from the
   regenerated file (19/14/1); recompute after fixing issue 1 anyway, since the fix
   will change these counts regardless.
4. **(Should fix, low effort.)** §c's falsification-test paragraph claims
   `conformal_cov_empirical ∈ {0.75, 1.0}` "across every registered object" — true
   only for calibration-rail's own 8 rows; the registry as a whole also shows 0.875
   (3 other packages' objects) and 0.5/0.25 (`baselines/naive_seasonal`, notably
   *below* the theoretical attainable floor of 0.857, which is itself worth a
   one-line mention since it is the more interesting anomaly, not the two values the
   note chose to describe). Narrow the claim's scope to "calibration-rail's own
   objects" or broaden the description to the actual 5-value set.
5. **(Documentation nit, optional.)** The "Parameter counts" table lists `ref_naive`
   as a flat 0 and `ref_trailing4` as a flat 1; the registry itself (and the
   harness's own `baselines.py` docstring) shows both take a value one higher when a
   residual sd is fitted (`{0,1}` and `{1,2}` respectively, confirmed in the
   registered CSVs). Cosmetic only — does not affect any comparison in the note.

None of these issues invalidate the package's headline conclusion (100% weight on
guide+cushion for revenue level; no tested method beats `bl_last_quarter` on surprise
timing) or the GBM negative result, which rest entirely on parts (a)/(b)/(c). They do
mean part (d) — the specific calibration-diagnosis numbers — is not yet safe to cite.
