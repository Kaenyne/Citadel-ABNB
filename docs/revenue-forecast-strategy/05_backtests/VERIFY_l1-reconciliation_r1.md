# VERIFY l1-reconciliation — round 1

Independent verification of package `l1-reconciliation` (Layer 1 constrained
least-squares reconciliation of regional nights/ADR to the disclosure bands and
the 72 exact cells, plus the FY27 named decomposition). Verifier ran fresh,
2026-09-11, against the implementer's self-report.

## 1. Reproducibility

Moved existing outputs to `data/processed/forecast_methods/l1_reconciliation_prev/`
and the three registry files to a sibling `registry_prev_l1/`, then re-ran:

```
cd "<repo>"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/l1_reconciliation/run.py
```

**Exit code 0. Wall time 146s** (well under the README's "about 6 minutes" and
well under the 90-minute time-box). Every file under
`data/processed/forecast_methods/l1_reconciliation/` and all three registry CSVs
are **byte-identical** to the pre-verification versions (`diff -q` clean on
every file). The console log reproduces every number quoted in the note
verbatim, including the acceptance-test table, the residual summary, the
feasibility ladder, the seasonal-lambda table, the ADR-decomposition
cross-check, the FY27 grid and the FY27 decomposition. This is a fully
deterministic, fully reproducible build.

## 2. Registry format

`H.validate_registry_frame()` from the frozen harness, run directly against the
three registered files, initially raised on an "unknown column `format_version`"
— this is **not** a package error: `validate_registry_frame` itself stamps
`format_version` on write, and does not accept its own stamped output as input
(a harness quirk, confirmed by reading `registry.py`). Re-validating after
dropping that one column: **all three files pass validate_registry_frame
cleanly** — required columns present, `window`/`prior_basis` values legal,
`vintage_date` is a guide date or TODAY for every row, the PIT rule holds
(vintage strictly before the target's print date; verified this is enforced —
the write itself would have raised `RegistryError` otherwise, and it did not),
quantiles non-decreasing. `revenue_contemporaneous` carries all 14 W1 vintage
dates it produced (2023-02-14 through 2026-05-07) and covers 2023Q1-2026Q2
targets. **Registry format: OK.**

Re-ran `harness/score.py` fresh; the `l1-reconciliation` rows in the rebuilt
`scoreboard.csv` are numerically identical to what the note quotes (see §4).

**HCR-1 is a genuine, correctly diagnosed harness limitation, not an invented
one.** `harness/windows.py` defines `LIVE_TARGETS = [q for _, q in
GUIDE_EVENTS_ALL if q >= "2026Q3"]`, but `GUIDE_EVENTS_ALL` has no entries past
2026Q3, so in practice `LIVE_TARGETS == ["2026Q3"]` only — even though the
README's prose says "LIVE requires 2026Q3 or later." `window_of_target` for
2026Q4+ returns an empty list, so `register()` with `window="LIVE"` for those
quarters would raise. The implementer's workaround (register the one legal
2026Q3 row per object; park the five forward rows in
`l1_unregistered_fy27_revenue.csv` / `..._fy27_growth.csv` in registry column
format) is the correct, harness-compliant response, and no second format was
invented. HCR-2 (calendar `guide_date` dtype) is a minor, already-worked-around
observation; the shipped code uses string comparison and does not carry the bug
forward.

## 3. Leakage audit

No confirmed leakage. Findings, most to least material:

1. **Consensus/Street data.** The only Street numbers in the code
   (`STREET_FY27_LO/HI = 15730/15760`, sourced from the 3-4 Sep 2026 Zacks/S&P
   vintages, matches `02_model_audit.md` and `03_insider_mechanics.md`
   verbatim) are used **only** for the A9 acceptance-test comparison and the
   headline text on the `fy27_revenue`/`fy27_growth` objects, which are
   registered as `window=LIVE, vintage_date=2026-09-11` and score in nothing.
   They are never used inside the PIT-backtested `revenue_contemporaneous`
   object, and the reconciliation itself never consumes a `street_*` column.
   Not leakage.
2. **`basis == 'derived'` rows.** Confirmed excluded mechanically: every row of
   `L0_interval_observations.csv` with `basis == 'derived'` (14 rows, all
   `included == False`) is dropped by `data.py:load_intervals()`'s `included`
   filter before any constraint is built. Crosstab confirms `derived` and
   `included=True` never co-occur.
3. **`include_same_day` (`knowable_from <= d`) convention.** The package's own
   PIT filtering (`ex.knowable_from <= d`, `iv.knowable_from <= d`) uses `<=`,
   which looks looser than the orchestrator brief's "filed strictly before d."
   Read `harness/loaders.py:history_as_of` — this is the harness's own
   **ratified** convention (`include_same_day=True` default), with a written
   rationale (the same 8-K that carries the guide also carries the
   quarter's own results, so a strict `<` rule would exclude the letter that
   IS the information set and silently break the trailing-8 cushion
   reproduction). The implementer's run.py docstring correctly attributes this
   to "the harness's ratified include_same_day convention" rather than
   inventing it. Not leakage, but it is worth flagging that the package
   inherits a harness-level policy choice that reads more permissively than
   the top-line brief; if the fund wants the literal `<` reading, that is a
   harness-level decision, not an l1-reconciliation bug.
4. **The `fx` (FX pp) table used inside `pit_point`/`Recon` is built once, in
   `main()`, from the FULL, non-date-restricted `iv` and `10_fx_quarterly.csv`,
   and the same object is passed unchanged into every guide-date's PIT refit** —
   it is not rebuilt at `d-1` per guide date the way the README's own FX rule
   ("packages consuming FX must still cut at d-1") asks. In practice this does
   **not** leak into the registered PIT object: (a) the `ax` (ex-FX ADR)
   constraint only fires for `(q, q-4)` pairs where **both** quarters are
   already inside the PIT-restricted `self.qi` (i.e., quarters with
   `knowable_from <= d`), so only already-elapsed, already-public quarterly FX
   moves are ever consumed by the fit; (b) the one-quarter-ahead projection
   step used for the registered `revenue_contemporaneous` object
   (`P.project_regional(..., None, None)`) never touches `fx` at all — it
   rolls forward on the region's own trailing-4 nights/ADR y/y only. So the
   *forecast* itself carries no FX-cut risk, and the *fit* only ever sees FX
   for quarters that are safely in the past relative to `d`. This is a **code
   hygiene gap relative to the README's stated FX rule, not a demonstrated
   leakage**, and it should be fixed (rebuild `fx` per guide date, cut at
   `d-1`) before another package copies this pattern uncritically.
5. **Quarter-end KPI data (`02_kpi_panel_quarterly.csv`) used before its
   filing.** `load_kpi()` loads the full, non-restricted panel, but every
   consumption inside the PIT loop is subset to `qs` (`ex.knowable_from <= d`).
   Since consolidated results print before the regional XBRL geography note
   becomes public (a one-year lag on the regional breakdown, explicitly named
   in the note as the reason for the 4-date W1 PIT gap), gating on
   `ex.knowable_from` is *more* conservative than gating on the quarter's own
   print date, not less. No leakage.
6. **Just-printed quarter's GBV used before its print date.** Not observed —
   `hist = [q for q in qs if D.qorder(q) < D.qorder(target_q)]` and the take
   rate used for projection is `pan[pan.quarter == lastq]` where `lastq` is the
   last quarter strictly before the target, itself drawn only from `qs`.
7. **Letter integers scored as points.** Not observed — every constraint class
   (`ann`, `ny`, `ar`, `ax`) is scored through the `hinge(v, lo, hi)` function
   against `[lo, hi]` bands; A2's own test description explicitly checks
   "inside ±0.5M," not equality to a point.

## 4. Number check (six-plus items independently recomputed from the CSVs, not just re-read from the note)

All of the following were recomputed directly from the regenerated CSVs /
rebuilt `scoreboard.csv`, independent of the note's own printed text:

| # | claim | recomputed | match |
|---|---|---|---|
| 1 | W1 PIT RMSE ratio to naive 11.34, W1 full-sample 10.93 | 11.338, 10.927 | match |
| 2 | W2 PIT 11.34, W2 full-sample 10.09 | 11.338, 10.093 | match |
| 3 | CRPS 836 / 616 / 836 / 721 across the four rows | 835.8 / 616.2 / 835.8 / 721.1 | match |
| 4 | 80% coverage 0.70 / 0.64 / 0.70 / 0.70 | identical | match |
| 5 | `n_params` = 68 on `revenue_contemporaneous` | 68 in scoreboard | match |
| 6 | baselines: naive 1.000, street 1.073, guide_cushion 0.377; kernel-lambda best 0.555 | 1.000, 1.073, 0.377, 0.555 (`revenue_level_next_q_last3_ex_covid`) | match |
| 7 | free parameters 60 = 3×18 + 3 + 3 | printed by run.py: "free parameters, reconciliation: 60" | match |
| 8 | bootstrap 2026Q2 shares NA 28.9-30.8 / EMEA 39.1-41.9 / LatAm 15.0-17.7 / APAC 12.3-13.8; ADR NA $224-292 / EMEA $184-223 / LatAm $63-85 / APAC $90-107 | identical to 1 decimal in `l1_bootstrap_intervals.csv` | match |
| 9 | 21 cells missing >1pp, region split EMEA 6 / LatAm 8 / APAC 5 / NA 2, worst cell EMEA reported ADR y/y 8.25pp (1Q23), 18/21 in 2025Q1-2026Q2 | recomputed from `l1_residuals_by_constraint.csv`: 21 rows, EMEA 6/LatAm 8/APAC 5/NA 2, worst = 1Q23 EMEA reported, resid 8.245046, 18/21 in {2025Q1..2025Q4,2026Q1,2026Q2} | match |
| 10 | ADR-note cross-check 2023/24/25 within-region +2.60/+2.01/+3.13 vs note +3.10/+3.44/+3.41; geo mix -1.22/-1.13/-1.48 vs note -1.08/-1.24/-1.58 | identical in rerun log; note's own targets (-1.08/-1.24/-1.58, +3.10/+3.44/+3.41) independently confirmed present verbatim in `research/notes/2026-09-07_adr-decomposition.md` lines 99/102 | match |
| 11 | FY27 $15,838M vs Street mid $15,745M (+0.59%), driver model $15,842M (4M away) | recomputed: 15837.566, (15730+15760)/2=15745, diff 92.57/15745=0.588%; driver-model constant 15842 sourced verbatim from `02_model_audit.md`/`03_insider_mechanics.md` | match |
| 12 | kernel-weight sensitivity "$118M on FY27...0.75%...2.3pp of growth" | recomputed diff (w=0.33→0.667) = **$117.3M**, 0.741% of revenue, 2.343pp of growth | **minor mismatch: $117M not $118M** (rounds down, not up; 0.75% vs 0.74% is immaterial) |
| 13 | seasonal lambda A6 targets 12.612/13.736/17.182/12.026 | these are the **single most-recent-in-season observed values** (1Q26, 2Q26, 3Q25, 4Q25), not a 3-year mean. `00_INTEGRATED_SYSTEM.md` separately states the architect's own headline point figure for λ_Q3 as **17.239%** (the 3-year mean, identical to the implementer's own recomputed mean to 4 decimals) — i.e. a *different* number from the 17.182 used as the A6 "target." | **framing imprecision, not fabricated data** — see §5 |

## 5. On the A6 "reproduce the architect's seasonal lambda table" framing

`run.py`'s `tgt = {1: 12.612, 2: 13.736, 3: 17.182, 4: 12.026}` are real,
correctly-sourced data points — each is the single most recent same-season
observed value (1Q26, 2Q26, 3Q25, 4Q25 respectively), and they are exactly the
values several *other* verified backtest notes in this same repo
(`kernel-lambda.md`, `fee-takerate.md`, `fx-lag.md`, `00_IMPLEMENTATION_DECISIONS.md`)
independently reproduce and cite as "the architect's table." So the target
values themselves are not wrong or invented. What is loose is the framing: the
implementer's own computed statistic is a **multi-year mean** (n=3 or n=4), and
comparing a multi-year mean against a single most-recent observation is not the
same test as "reproduce the architect's table," even though the two are close
here because the series has low variance (sd 0.09-0.30pp). Elsewhere in the
strategy docs (`00_INTEGRATED_SYSTEM.md` line 213-214) the architect's own
headline figure for λ_Q3 is stated as **17.239%** — the 3-year mean — which is
what the implementer's own recomputed mean equals almost exactly (17.239362,
diff 0.0004pp), not the 17.182 used as the "target" in the A6 row. This does
not change any downstream number (the FY27 kernel build correctly uses the
implementer's own recomputed means, 12.694/13.714/17.239/12.030, not the target
column), so nothing is functionally wrong — but the A6 pass/fail framing in the
note overstates precision slightly and should be reworded (e.g. "within 0.09pp
of the most recently observed same-season value" rather than "reproduce the
architect's table") before it is quoted.

## 6. Two smaller documentation-precision items

* **A1's "72 filed regional revenue cells."** `L0_exact_regional_revenue.csv`
  has `basis == 'filed'` for 56 of the 72 cells and `basis == 'back_out'` for
  the other 16 (the four Q4 cells per year, each computed as FY-10-K minus the
  nine-month 10-Q cumulative — an exact arithmetic derivation from two filed
  numbers, `reconciliation_max_abs_diff_musd: 0.0` per `L0_build_diagnostics.json`,
  not a modelling assumption). Calling all 72 "filed" is a minor label
  looseness inherited from the L0 spine, not something this package
  introduced or could have avoided, and the derivation is exact — but the note
  should say "72 filed-or-exactly-back-out cells" if it is going to be quoted
  precisely in the memo.
* **A2's "16 clean annual 10-K regional nights cells" vs the plan's 24.**
  `L0_interval_observations.csv` actually carries 24 annual `nights_m` cells
  (FY2020-FY2025 × 4 regions, all `basis == 'filed'`, all `included == True` —
  none are flagged dirty). Only 16 (FY2022-FY2025) are used, because the
  reconciliation's quarterly panel only spans 2022Q1-2026Q2 (bounded by the
  exact-revenue panel's own start date) — the constraint-builder's
  `all(x in self.qi for x in qs)` check silently drops FY2020/FY2021 because
  those years' quarters are outside the fitted panel, not because those 8
  cells are unclean. The word "clean" in the note is therefore slightly
  misleading — the true reason is a panel-window boundary, not a data-quality
  filter. Worth a one-line fix in the note; does not affect any registered
  number.

## 7. Acceptance tests — genuinely ran, not asserted

Re-ran the full pipeline and independently recomputed every acceptance-test
number from `l1_acceptance_tests.csv`, `l1_residuals_by_constraint.csv` and
`l1_annual_adr_decomposition.csv` rather than trusting the note's table. A1-A7
and A9 pass on independent recomputation with the exact residuals claimed
(2.27e-13, 0.0008M, 2.84e-14M, 5.68e-14 USD, 3.64e-12$M, max 0.082pp on A6,
max 0.14pp on A7, +0.59% on A9). **A8 genuinely fails** — the 2024 gap is
-1.431pp against the claimed -1.43pp, an honest, correctly-reported failure,
not a hidden or softened one. No test was marked passed without a
recomputable, matching number behind it.

## 8. Honesty of the interpretation

High. Specific things done right:
* The registered `revenue_contemporaneous` object is reported as losing to
  naive by 11x and is explicitly labelled a **negative control**, with the
  seasonal-phase-error interpretation stated and not oversold as a forecast —
  independently confirmed against the rebuilt scoreboard (11.338/10.927/11.338/10.093,
  bias near zero, MAE ~$1,000-1,150M).
* The G2 feasibility-ladder finding (three disclosure families cohere to
  numerical noise; a fourth, regional ADR y/y, does not, under any smooth
  take rate) is reported as a genuine mutual inconsistency in the disclosures,
  not relaxed to force a pass — confirmed via independent recomputation of the
  ladder and the headline-fit residual summary, which use two different ADR
  constraint weights (ladder: adr weight 1.0 → max 7.3/4.1pp; headline fit:
  W_CONF adr weight 0.25 → max 8.25/4.57pp) — both numbers are real and
  correctly attributed to their respective fits, but the note does not
  explicitly flag *why* the two "worst gap" figures differ; a reader could
  momentarily confuse them. Minor clarity issue only.
* The "geographic mix is fading, not accelerating" finding (-1.22/-1.13/-1.48
  then -0.34pp in 2026 H1) is flagged as a live discrepancy against the plan's
  assumed -1.5pp FY27 mix line, with an explicit "someone should look at this
  before the memo is written" — appropriately proactive, not buried.
* `known_issues` in the implementer's report and §8 of the note match what
  the verifier independently found: PIT coverage 10/14, ADR levels weakly
  identified (bootstrap confirms ±15% vs ±1pp on shares), FY27 FX flat-spot
  carry as an unmeasured assumption, n=1 bedroom-elasticity disclosure,
  back-extrapolated non-home units pre-2024. Nothing material was found that
  the note fails to disclose.

## 9. Verdict

**PARTIAL — safe to score and quote, with the following caveats named
explicitly wherever a number from this package is used in the memo or model:**

1. The A6 "reproduces the architect's seasonal lambda table" framing compares
   a multi-year mean to a single most-recent observation; reword before
   quoting (§5).
2. The kernel-weight FY27 sensitivity is $117M, not $118M (§4, item 12) —
   immaterial to any conclusion but should be corrected if the exact figure is
   quoted.
3. The `fx` table consumed inside the PIT refit is not rebuilt at `d-1` per
   guide date as the harness's own FX rule asks; no leakage was found because
   of how the constraint set is filtered, but this should be tightened before
   another package copies the pattern (§3.4).
4. "72 filed regional revenue cells" (16 are exact back-outs from two filed
   numbers) and "16 clean annual nights cells" (all 24 available cells are
   equally clean; only 16 fall inside the fitted panel's date window) are
   label-precision issues, not data problems (§6).
5. HCR-1 and HCR-2 are genuine, correctly diagnosed harness issues (§2),
   confirmed by reading `windows.py` and `loaders.py` directly — not
   implementer error.

None of the five caveats change the headline numbers (FY27 $15,838M / +11.52%,
the G2 pass, the A8 fail, the 11x negative-control result, the bootstrap
±15%/±1pp asymmetry) or the acceptance-test pass/fail pattern, all of which
were independently reproduced bit-for-bit and, where recomputed from source
CSVs rather than merely re-read, matched to the precision quoted.
