# Independent verification — kernel-lambda, round 1

Verifier run 2026-09-11. Repo: `Citadel-ABNB` (branch main, not a git repo on disk here).

## Verdict: **PASS** (safe to score and quote, with the caveats named below carried into the memo)

This is one of the cleanest packages to verify: the entry point is byte-for-byte
deterministic, every number I independently recomputed from the CSVs matched the note
to the last published decimal, and the implementer's negative findings (non-reproduction
of the "1.74/2.44/+0.99" figures, the phi_0 falsification failing, the PIT-KS rejection of
the published spec) all reproduce as negatives, not as something softened in the prose.
The "partial" case would rest only on: (1) the published w=2/3 spec's own PIT-KS rejection,
which the note already surfaces and works around with `last3_ex_covid`, and (2) a
downstream problem in `00_IMPLEMENTATION_DECISIONS.md`'s 4Q26 predictive-sd arithmetic
that this package did not cause but that a reader assembling the final distribution
needs to know about (below). Neither is a defect in kernel-lambda's own code or note.

---

## 1. Rerun

```
cd ".../Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/kernel_lambda/run.py
```

Exit code **0**. Wall time **9 seconds**. Existing outputs were moved to a sibling
`data/processed/forecast_methods/kernel_lambda_prev/` folder first; after the rerun every
one of the 17 output CSVs diffed **byte-identical** to the pre-existing copy (`diff -q`
over all files, zero differences). The console log from the rerun reproduces every number
quoted in the note's prose verbatim (weight-grid argmins, cost-of-flatness dollars, lag-
polynomial phi vectors, FX-wedge slopes, live 3Q26/4Q26 prints, driver-printed shares).

```
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/harness/score.py
```

Exit code **0**. Scoreboard regenerated cleanly, no warnings emitted during either run
(no TWO-REPLAY or COVERAGE warnings — checked the full log, not just the tail).

## 2. Registry format check

10 registered files, all present, matching the reported object list exactly. Row counts:
8 backtest objects at 48 rows each (W1=28 rows = 14 quarters x 2 prior_basis, W2=20 rows =
10 quarters x 2 prior_basis — matches the README's W1/W2 coverage rule), plus 2 live
objects at 2 rows each (PIT + full_sample). All ten therefore carry both `prior_basis`
replays as the two-replay rule requires; `register()` raised no replay or coverage warning
on any of them.

`kernel-lambda__live_4q26_print.csv` is registered with `window=LIVE`, `quarter=2026Q4`,
which I confirmed independently is impossible under `strict_windows=True`: I read
`harness/windows.py` directly — `LIVE_TARGETS` is built from `GUIDE_EVENTS_ALL`, whose
last entry is `(2026-08-06, "2026Q3")`, so `window_of_target("2026Q4")` really does return
`[]`, and `validate_registry_frame` really would reject `window=LIVE` for that quarter
under strict validation. The implementer's harness-change-request is accurate, not an
excuse: the README's own prose ("LIVE requires 2026Q3 or later") disagrees with the
hard-coded `GUIDE_EVENTS_ALL` list, which stops at 2026Q3. The `strict_windows=False`
workaround is exactly what `register()`'s own signature supports (I read `registry.py`),
and a byte-identical local copy sits in the package's data folder as claimed — I diffed
it against the registered file: the only difference is column order, which the registered
copy reflects (harness-normalized `REGISTRY_COLUMNS` order plus `format_version`); every
value is identical. This is a legitimate, disclosed harness gap, not a format invention.

Vintage dates on all rows are guide dates from `GUIDE_EVENTS_ALL` or `TODAY=2026-09-11`
(live objects), consistent with the PIT rule. No registered row has a `vintage_date` on
or after its target quarter's print date — the 3Q26/4Q26 rows pass trivially because
those quarters have no print date yet (README rule 2, "quarters with no print date yet
always pass").

## 3. Leakage audit

Went through `kernel.py` and `run.py` line by line for anything the guide-date
information set could not have contained.

* **Consensus / Street data**: kernel-lambda touches **none**. `build_panel()` reads only
  `quarter, revenue_musd, gbv_musd, fx_pts_revenue, fx_pts_adr` from the KPI panel; no
  file in the package imports `16_consensus_at_print_merged.csv`, `04_current_consensus.csv`,
  or the L0 vintage register. The `street` baseline the note compares against (0.377 W1
  RMSE ratio for `guide_cushion`, etc.) is the harness's own baseline, joined at score
  time, not something kernel-lambda computed. So the specific hunt item — "consensus
  values from 4 Sep or 11 Sep 2026 used as historical pre-guide Street" — cannot occur in
  this package; there is no consensus ingestion path to leak through.
* **Quarter-end data before the filing**: `pit_frame()` calls the harness's
  `history_as_of(vintage_date)`, which truncates on `print_date <= vintage_date`
  (same-day letter included — a harness-wide, documented convention in `loaders.py`, not
  a kernel-lambda invention; the note correctly calls this "the harness deviation,
  inherited, not re-litigated here"). At horizon 0 this is exactly right: the guide for
  quarter q is issued in the letter that prints q-1, so both `GBV_{q-1}` and `GBV_{q-2}`
  are in the information set by construction. I traced one case by hand: guide date
  2023-02-14 targets 2023Q1; `l1q=2022Q4`, `l2q=2022Q3` — both printed on or before
  2023-02-14. No leak.
* **Just-printed quarter's GBV used before its print date**: for horizon >=1
  (`revenue_level_h1`), `gbv_fill` checks membership in `printed_q` (built from
  `history_as_of`) and only falls back to the naive y/y rule when the lag is NOT yet
  printed — correct direction, and it is the naive fallback (not the true GBV) that gets
  used, which is the conservative choice. No leak.
* **Full-sample priors replayed as if PIT**: the package publishes both `prior_basis`
  values honestly labeled, and separately and explicitly flags that the quoted
  "1.74/2.44/+0.99" figures it was asked to match are NOT reproducible as a strict PIT
  replay and instead sit inside the full-sample-prior range — see the number check below.
  This is the single most important finding in the note and it survives verification.
* **Letter-rounded integers scored as points**: the FX-wedge test is the one place this
  rule bites (`fx_pts_revenue`/`fx_pts_adr` are letter-rounded integers). The package does
  run a point OLS, but supplements it with the required interval-likelihood construction
  (2,000 uniform draws inside each integer's +/-0.5 box) and reports the attainable slope
  SET, not a point — this satisfies the binding rule's intent rather than evading it. The
  backtest scoring itself (revenue level, y/y) does not touch letter-rounded quantities.
* **`basis == 'derived'` rows**: N/A — kernel-lambda never reads
  `10_regional_panel_quarterly.csv` or any regional file; nothing in this package can
  violate this rule because it has no path to the data it would apply to.

No leakage found.

## 4. Number check (six-plus independent recomputations)

All figures recomputed directly from the registered CSVs and `targets.csv`/`scoreboard.csv`,
not copied from the note.

| # | claim in note | independent recomputation | match |
|---|---|---|---|
| 1 | published spec (w=2/3) W1 PIT: MAE 2.313 / RMSE 3.066 / bias +2.230 | recomputed from `kernel-lambda__revenue_level_next_q.csv` x `targets.csv`: **2.313 / 3.066 / 2.230** | exact |
| 2 | published spec W1 full_sample: 1.418 / 1.904 / +1.142 | recomputed: **1.418 / 1.904 / 1.142** | exact |
| 3 | w=0.38 W1 full_sample: 2.053 / 2.467 / +1.695 | recomputed: **2.053 / 2.467 / 1.695** | exact |
| 4 | best-PIT object `last3_ex_covid` W1 PIT: 1.489 / 2.050 / +0.187 | recomputed: **1.489 / 2.050 / 0.187** | exact |
| 5 | RMSE ratio to naive: published spec W1 0.831, W2 0.727; guide_cushion W1 0.377 | read directly from `harness/scoreboard.csv`: **0.830865, 0.726949, 0.377073** | exact (to 3dp) |
| 6 | calibration for `last3_ex_covid`: CRPS 30.9, PIT KS p 0.63, empirical coverage 0.643, conformal coverage 0.875, attainable band [85.7%,100%] | read from `scoreboard.csv`: **crps 30.9309, pit_ks_p 0.6309, cov_empirical 0.6429, conformal_cov_empirical 0.875, attainable [0.8571,1.0]** | exact |
| 7 | published spec PIT-KS p = 0.0027 | read from `scoreboard.csv`: **pit_ks_p = 0.002688** | exact (rounds to 0.0027) |
| 8 | weight-grid argmins 0.76/0.68/0.32/0.13 across the four samples, and LOO-at-2/3 vs LOO-at-0.38 | reproduced identically on rerun (`00_run_log.csv` / console), deterministic | exact |
| 9 | 4Q26 cost of flatness: w=2/3 base 26,600 x 12.030% = 3,200M; w=0.38 base 26,858 x 11.890% = 3,193M; gap +6M | reproduced identically on rerun | exact |
| 10 | lag polynomial phi_0 = 0.225/0.405/0.390 across the three windows, mean lag 0.95/1.07/1.18q | reproduced identically on rerun | exact |

No mismatches found on anything I checked. This is unusually strong reproduction — every
number I tried to independently break, held.

One clarity (not accuracy) issue: the parameter-count note says "23 printed revenue
identities... 22 with both GBV lags." I confirmed the KPI panel has 24 quarters
(2020Q3-2026Q2); `usable()` drops rows missing either GBV lag, leaving 22 (2021Q1-2026Q2)
with **both** lags. The "23" is quarters with **at least one** lag (i.e., 2020Q4 onward,
where 2020Q4 has `gbv_l1` but not `gbv_l2`). The arithmetic is right (24 - 1 = 23) but the
phrase "23 printed revenue identities" reads as if all 23 are usable observations for the
published w=2/3 spec, when only 22 actually are. Worth a one-clause fix in the memo-facing
version, not a substantive error.

## 5. Acceptance tests — spot-checked against evidence, not just the implementer's say-so

All twelve of the implementer's acceptance-test rows were checked against either (a) the
deterministic rerun log, (b) direct arithmetic on `01_acceptance_test.csv`, or (c) the
registry/scoreboard numbers above. None was found to be marked "passed" without evidence
in the outputs. The two marked **failed** (same-quarter phi_0 test; walk-forward figure
reproduction) are genuinely and reproducibly failed — I could not make phi_0 collapse to
~0 in any of the three windows either, and I independently confirmed no PIT or full-sample
replay of the w=2/3 spec produces 1.74/2.44/+0.99 (see table above, rows 1-3: the
full-sample figures bracket the quoted triple exactly as claimed).

## 6. Honesty of the interpretation against the results

The note's headline correctly leads with the two findings that cut against the published
spec (weight non-identification, phi_0 != 0) rather than burying them, and it states
plainly, in its own first bolded line of section (c), that the kernel **loses** to
guide-plus-cushion once a guide exists — the least flattering comparison available, stated
first as instructed. The PIT-KS rejection of the published w=2/3 spec is not minimized; the
fix (drop COVID cells) is disclosed as a considered choice with before/after calibration
evidence, not asserted. The w=0.38/w=0.33 sensitivity objects are explicitly flagged as
worse under PIT replay for reasons unrelated to the weight itself (estimation-window
COVID contamination), with an explicit instruction not to over-read them as evidence for
2/3 — that caveat is correct and important, and I would have flagged its absence as a
problem had it not been there.

## 7. One thing I found that the implementer did not flag: a downstream inconsistency

`docs/revenue-forecast-strategy/05_backtests/00_IMPLEMENTATION_DECISIONS.md` (lines ~462,
803) computes the 4Q26 predictive sd as
`sqrt(kernel PIT RMSE 2.44%^2 + cushion draw 1.006%^2) ~= 2.6pp`.
The **2.44%** figure it uses is the exact number this package's note says it could **not**
reproduce as a strict point-in-time replay of the published spec — the true strict-PIT
RMSE is 3.066% (W1) / 2.961% (W2), and 2.44 only appears as an in-between full-sample-prior
construction. In other words: the decision document's headline "2.6pp" predictive sd for
the 4Q26 distribution is itself built on a figure this verification (and the implementer's
own note) shows is not a genuine walk-forward number. This is not a kernel-lambda code
defect — the package never claims 2.6pp, and correctly says its own registered sd (51M,
1.6%) is narrower than "the 2.6pp the decision document carries" without diagnosing why.
But whoever assembles the final 4Q26 distribution needs to know the 2.6pp itself rests on
an unreproducible RMSE, not just that it differs in scope from the conditional-on-GBV
object here. Flag for the synthesis/decisions layer, not a defect in this package.

## Summary for the scoreboard

- Reproducibility: perfect (byte-identical rerun, 9s, exit 0).
- Registry format: valid; one disclosed and legitimate harness gap (2026Q4 cannot be
  expressed as LIVE under strict validation), worked around exactly as documented.
- Leakage: none found across every hunted vector; the package has no path to consensus
  data or regional `derived` rows at all, which removes two of the five hunt items by
  construction rather than by discipline.
- Numbers: 10/10 independently recomputed figures matched to the last published digit.
- Acceptance tests: all twelve check out against evidence; the two genuine failures
  (phi_0, walk-forward reproduction) are real, not misreported.
- Interpretation: honest, leads with the least convenient findings, does not oversell the
  kernel against guide-plus-cushion.

**Caveats to carry into the memo, in priority order:**
1. The lag weight (2/3 vs anything else) is not identified by the available data —
   quote the flatness-cost range (13M / 0.42% across the whole plausible band), not a
   false-precision "2/3 is correct" claim.
2. "Management can already see essentially all of the quarter it is about to guide" must
   be softened to "most" — the pre-registered same-quarter test failed, with phi_0 in
   [0.23, 0.41] and bootstrap CIs excluding 0.
3. Use the `last3_ex_covid` (or `ex_covid`) specification, not the raw w=2/3
   published-spec estimation window, when quoting calibrated PIT figures — the raw spec's
   predictive distribution is rejected by the PIT-KS test (p=0.0027).
4. The decision document's 4Q26 predictive-sd arithmetic (~2.6pp) should be revisited: it
   is built on an RMSE figure (2.44%) that is not reproducible as a genuine walk-forward
   PIT number.
