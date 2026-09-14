# VERIFY fee-takerate — round 1

Verifier pass on the implementer's "complete" report. Independent re-run, registry
validation, leakage audit, six-plus number checks, acceptance-test spot-check, honesty
read.

**Verdict: PARTIAL — safe to score and quote, with three fixes named below before this
is treated as closed.**

---

## 1. Re-run

```
cd "<repo>"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/fee_takerate/run.py
```

Exit code **0**. Wall time **1.55 s** (`1.28s user 0.11s system`). Console output is
byte-identical to the acceptance-test detail strings already in the note, with one
immaterial exception: A10's permutation p-value came back **0.724** this run vs the
note's **0.72** — `np.random.permutation` is called with no seed in `stage_c`, so the
Monte-Carlo p-value is not bit-reproducible run to run. Both runs agree the effect is
not significant (n=20, 2 informative quarters); this doesn't change any conclusion, but
seed it for a memo-grade artifact.

Existing outputs were moved to `data/processed/forecast_methods/fee_takerate_prev/`
before the re-run (plus copies of the three registry CSVs) so the diff is clean. The
21-row acceptance table, the uplift table, the mechanism table, the migrated-share path,
and both live-object tables (3Q26, 4Q26, FY27) reproduced to full float precision
against the pre-existing files.

## 2. Registry format

Ran the harness's own scorer against the live registry:

```
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/harness/score.py
```

Exit code 0 — **the registry validates**: no `RegistryError`, no PIT violation, no
quantile-monotonicity error. Checked directly:

* Required columns present and non-null on all three files (0 nulls across the 12
  required columns, all rows).
* `take_rate_kernel` / `take_rate_lastyear`: 50 rows each, W1 28 / W2 20 / LIVE 2,
  `prior_basis` split 25/25 PIT vs full_sample, 15 distinct vintage dates spanning
  2023-02-14 to 2026-08-06 — all in `GUIDE_DATES_ALL`.
* `take_rate_mechanism`: 6 rows, all `window=LIVE`, `quarter=2026Q3`,
  `vintage_date=2026-09-11` — this is legal under harness rule 1 ("MUST be a guide date
  ... or today, `2026-09-11`"), confirmed by reading `harness/README.md` §2 directly.
* **The harness change request is real, not a misreading.** Read `harness/windows.py`
  and `harness/registry.py` directly: `LIVE_TARGETS = [q for _, q in GUIDE_EVENTS_ALL if
  q >= "2026Q3"]`, and `GUIDE_EVENTS_ALL` is a hard-coded list whose only entry `>=
  2026Q3` is `(2026-08-06, "2026Q3")`. So `WINDOW_MEMBERSHIP["LIVE"] == ["2026Q3"]`
  today, and `registry.py` line 165-171 raises `RegistryError` for any other quarter
  tagged `LIVE`. Registering 2026Q4+ under `window=LIVE` is therefore genuinely
  rejected by the harness as it stands; the local workaround (`07d_*_all_quarters.csv`,
  24 rows in registry format, only the 6 legal 2026Q3 rows actually registered) is the
  correct response and is exactly what the note claims.
* **The second change request is understated, not overstated.** I checked
  `data/processed/forecast_methods/registry/baselines__naive.csv` and
  `baselines__naive_seasonal.csv` directly: neither has **any** row for
  `target=take_rate_pct` (both cover only `revenue_musd, revenue_yoy, gbv_musd,
  nights_m`). So it isn't merely that `baseline_naive` is "the wrong denominator" for
  this target — there is currently **no baseline registered for `take_rate_pct` at
  all**, and `score.py`'s own scoreboard confirms it: I pulled the `fee-takerate` rows
  from `scoreboard.csv` and `rmse_ratio_to_naive` is `NaN` on all eight take-rate rows.
  Anyone reading `scoreboard.csv` directly (rather than this package's local
  `06c_backtest_scorecard.csv`) sees `NaN`, not the 0.07–1.34 ratios quoted in the note.
  Flag this explicitly wherever `scoreboard.csv` is consumed downstream, so nobody reads
  the `NaN` as "beats naive" or "no baseline exists to compare."

## 3. Leakage audit

Went through `fee_schedule.py` and every stage of `run.py` line by line for each of the
named leakage patterns:

* **Consensus at wrong vintage.** No reference anywhere in this package to
  `04_consensus_at_print.csv`, `16_consensus_at_print_merged.csv`, or
  `04_current_consensus.csv`. This package does not touch Street data at all; `base_street`
  / `street_vendor` / `street_as_of` are left blank in the registry (permitted — optional
  columns). No finding.
* **Quarter-end data before its filing.** The PIT machinery is entirely delegated to
  `harness.history_as_of`, which filters on `print_date <= vintage_date` (documented,
  deliberate `include_same_day=True` default — read the docstring, which explains why
  the letter that *carries* the guide is knowable on the guide date itself). This is
  harness-level, shared and frozen; not this package's code to fix, and it is used
  correctly here (`stage_e` passes `include_same_day=True` explicitly, matching spec).
* **Full-sample priors replayed as PIT.** `prior_basis="full_sample"` rows in
  `06_backtest_takerate_raw.csv` are explicitly built from `lam_all = _lambda_table(t)`
  on the *entire* un-filtered target panel, and are correctly labelled
  `prior_basis=full_sample` in both the intermediate file and the registry — never
  conflated with the PIT rows. This is the required "publish both replays side by side,"
  not leakage.
* **Just-printed quarter's GBV used pre-print.** The 3Q26 live object (`stage_df`) uses
  `t.loc["2026Q2","gbv_musd"]` and `t.loc["2026Q1","gbv_musd"]` — both already printed
  as of today (2026-09-11; 2Q26 printed with the 2026-08-06 letter). Not leakage.
* **theta / migrated-share leaking into the historical backtest.** Checked explicitly:
  `stage_e` (the two backtested, scored objects `take_rate_kernel` and
  `take_rate_lastyear`) never calls `FS.LISTING_SHARE_PATH`, `FS.CONCENTRATION_M`,
  `FS.uplift`, or anything from `12_reprice_summary.csv`. The migration/theta machinery
  only enters `stage_df`, which registers exclusively `window=LIVE` rows (2026Q3+, not
  scored against W1/W2). So the forward fee assumption cannot be leaking into the W1/W2
  backtest that is used to justify "take rate is not forecastable" — that conclusion
  rests on GBV-kernel and lagged-take-rate mechanics only, which is the right design.
* **Source dating of the repricing panel itself.** `12_reprice_summary.csv` (`date_a`,
  `date_b`) spans 2026-03-16 to 2026-08-31 — entirely before today (2026-09-11). Not a
  look-ahead relative to "today," and irrelevant to W1/W2 scoring since it never enters
  the backtested objects (previous point).
* **Letter-rounded integers scored as points.** N/A — this package's targets
  (`take_rate_pct`) are continuous printed ratios, not letter-rounded guidance ranges.
* **`basis == 'derived'` regional rows.** N/A — this package never reads
  `10_regional_panel_quarterly.csv` or any regional file.

**No leakage found.**

## 4. Number check (nine independent recomputations from source, not from the note)

| # | claim | recomputed from | result |
|---|---|---|---|
| 1 | A1: theta = mean_jump_pp/13.8, max err 3.3e-16 | `12_reprice_summary.csv` direct | reproduced, 3.33e-16 |
| 2 | A2: 402 non-null theta, 34 markets, range 0.833–1.407 | same | reproduced exactly |
| 3 | A9: 2Q26 13.26 vs 2Q25 13.17 (+9bp); 1Q26 9.17 vs 1Q25 9.27 (-10bp); 3Q25 -69bp; 4Q25 -47bp | `data/processed/overnight/02_kpi_panel_quarterly.csv` `take_rate_pct` column, read directly (not via the harness's `targets.csv`) | all four values match to the reported bp, independent of the note and of the harness loader |
| 4 | A6: split take 14.9869%, single 15.5000%, payout-neutral reprice 14.7929pp | `fee_schedule.py` self-test + direct arithmetic on the disclosed 3%/14.1%/15.5% constants | reproduced |
| 5 | A8: 15-Sep/13-Oct-2026 deadlines absent from `06_fee_timeline.csv` | read the 19-row file directly | confirmed absent — neither date nor "Sep 15"/"Oct 13" appears anywhere in the file |
| 6 | Mechanism FY27 TOTAL: +5.4 / +22.7 / +41.9 bps | `05b_takerate_mechanism_fy27.csv` `TOTAL` rows | 5.368 / 22.737 / 41.941 — matches |
| 7 | single_fee_migration FY27 line: +23.4/23.7/27.9 | same file, `single_fee_migration` rows | 23.368 / 23.737 / 27.941 — matches |
| 8 | 3Q26 live central @ GBV 26,185: take 18.48%, sd 0.40pp, P(≥18.10)=0.83, no-fee 18.35% | `07a_live_3q26_take_rate.csv` | 18.478 / 0.3959 / 0.8301 / 18.347 — matches to the quoted precision |
| 9 | migrated share path table (§2): e.g. 1Q26 listing .14/.18/.22, 3Q26 rev-quarter central 0.394, 4Q26 rev-quarter central 0.625 | `03_migrated_share_path.csv` | matches exactly |

All nine reproduce. **9. checked the parameter count table** (`09_parameter_counts.csv`)
against the note's §7 — matches exactly, total 11.

**One number I initially flagged as a mismatch turned out to be correct on closer
reading, noted here so it isn't re-litigated:** the note's §6 "4Q26 fee step" prose says
"the print moves to 3,200–3,220 M and the guide midpoint to 3,141–3,160 M." Read naively
against `07b_live_4q26_fee_step.csv` central row (`print_with_half_step=3218.2`,
`print_with_full_step=3236.4`, `guide_mid_half=3159.4`, `guide_mid_full=3177.3`) this
looks wrong. But the range is actually **[no-step=3200.0, half-step=3218.2≈"3220"]** and
**[no-step-guide=3141.4≈"3141", half-step-guide=3159.4≈"3160"]** — i.e. it brackets
"nothing flows through" to "the recommended half-step case," not "half" to "full." The
arithmetic reconciles once that's understood; the only real defect is that the note
never states which two numbers bound the range, which cost me a false-positive on first
read and will cost a memo reader the same confusion. **Fix: name the two endpoints of
the 4Q26 print/guide range explicitly** (e.g. "no-step 3,200M to half-step 3,218M≈3,220M")
rather than leaving the reader to infer it.

## 5. Reproducibility gap (the one real finding)

`00_acceptance_tests.csv` and everything else in
`data/processed/forecast_methods/fee_takerate/` regenerated with fresh mtimes on this
re-run — **except** `06c_backtest_scorecard.csv` and `06d_seasonal_naive_benchmark.csv`,
whose mtimes stayed at the *pre-rerun* timestamp (10:42, vs 10:48 for every other file in
the directory). I read all 720 lines of `run.py`: there is no code path that writes
either filename, and a repo-wide grep for both filenames turns up nothing outside the
`data/processed/` output directory itself. **These two files are stale leftovers from
code that no longer exists in the package** — the README's claim that `run.py` "rebuilds
everything" is not currently true for them.

This matters because the §4 PIT-backtest table — the core "neither object beats the
seasonal naive" result — is sourced from `06c`/`06d`, not from anything the current
`run.py` produces. I did **not** find evidence of fabrication: I independently
recomputed the seasonal-naive benchmark from `04a_takerate_history.csv` (mean of
`take_rate_pct_lag4 − take_rate_pct` over the W1/W2 quarter sets) and got RMSE
0.325137/0.317836 for W1/W2 — matching `06d` to 6 decimal places — and the
`06c` MAE/RMSE/bias/CRPS/PIT-mean figures for `take_rate_kernel`/`take_rate_lastyear`
match `harness/score.py`'s own independently-computed `scoreboard.csv` rows exactly
(e.g. kernel W1 PIT RMSE 0.436262 in both). So the *numbers* are correct and
independently corroborated — but the *pipeline* currently can't reproduce them from the
single documented entry point, which is a binding requirement of this programme
("entry point run.py that rebuilds everything"). **Fix: restore the `06c`/`06d`
generation code into `run.py`** (or, if these were meant to be a one-off manual
artifact, say so explicitly in the README rather than implying `run.py` produces them).

**Secondary, minor correctness note on the same two files:** `06d`'s bias sign looks
flipped relative to the convention used everywhere else in the package. My
`take_rate_pct_lag4 − take_rate_pct` (forecast − actual, the same convention that gives
`take_rate_kernel`/`take_rate_lastyear` their positive biases of +0.10 to +0.29pp)
gives **−0.0143pp** for W1 and **+0.0860pp** for W2; `06d` reports **+0.0143** and
**−0.0860** — magnitudes match exactly, signs are both flipped. Immaterial to any
conclusion (both are near zero either way, and the note never leans on the seasonal-
naive's own bias direction), but worth fixing so a reader comparing "kernel bias +0.28"
against "seasonal-naive bias +0.01" isn't misled about which way each is biased.

## 6. Acceptance tests — evidence check

All 15 acceptance tests in `run.py` carry a computed `detail` string with the actual
numbers, not a bare assertion; re-running reproduced every detail string to the digit
(the one exception, A10's permutation p-value, is explained in §1 — unseeded RNG, not
evidence of anything wrong). A5 is a genuine, correctly-computed documented failure
(`mean share_gt_10=0.2149 > mean share_lt_m10=0.2025` on the full 420-row file, `178/420`
rows have more cutters; holds only on the 20-row Austin subsample) — I recomputed this
independently from `12_reprice_summary.csv` and confirm it.

A11, A13, A14, A15 are registered with a hard-coded `True` in `check(...)` — they are
**documentary**, not real pass/fail gates (they report a computed table rather than test
a hypothesis). This isn't deceptive — each one's `detail` string is the actual
computation, and none of them is presented in the note as "passed a test" in a load-
bearing way — but it means "14/15 passed" should not be read as "14 independent
hypotheses were confirmed." Only A1–A10, A12 are real boolean tests; all ten check out
against source data.

## 7. Honesty of interpretation vs. results

This is the strongest part of the submission. Specific, checked examples:

* The note's first paragraph states the theta-identification problem before any result
  — "theta is UNIDENTIFIED... It is not measured anywhere in this repository and it is
  not measured here" — and Finding 1 goes further, showing the carried "central" and
  "low" cases are the *same* Austin observation under two denominators rather than two
  pieces of evidence. This is self-undermining in exactly the way an honest note should
  be.
* Finding 2 is escalated (flagged, not silently picked a default) even though the
  default (`gbv_consistent`) is what's used downstream — the fiat form is kept in code
  "so the decision can be re-ratified," which is the right way to handle a live
  disagreement with an upstream ruling.
* §4's conclusion is an explicit, unhedged negative: "neither object beats it on either
  window in either replay... `survives_both_windows` is **False** for every row,"
  followed by "Nothing in the backtest may be quoted as a forecasting win." I verified
  this against `scoreboard.csv` directly (§2 above) — it's true.
* The driver-model reproduction failure (+0.53%/sd 1.97 claimed elsewhere vs. +0.97%/sd
  2.54 reproduced here) is reported as "Flagged, not reconciled" rather than silently
  matched or silently ignored. I spot-checked `13_driver_model.py` for the +0.53 figure
  and found only a similarly-shaped but not identical number (a `2Q27` scenario tuple
  `(0.53, 2.15)` at line 282) — genuinely inconclusive within this verification's time
  budget, and the implementer's own "unreconciled" flag is the correct level of
  confidence to carry forward, not a false precision I could improve on quickly.
* The 3Q26 pre-registration explicitly weakens its own headline number: "the no-fee
  counterfactual is already 18.35%, so the threshold is cleared by kernel arithmetic
  alone... the test has almost no power against the fee hypothesis." I verified the
  18.35% figure directly from `07a` (§4 above) — accurate, and the self-critique is
  correct arithmetic, not false modesty.

No instance found where a headline number in the note overstates what the underlying
CSV actually shows.

## 8. What must be fixed before this is scored as closed

1. **Wire `06c_backtest_scorecard.csv` and `06d_seasonal_naive_benchmark.csv` generation
   into `run.py`** (or explicitly document them as a frozen manual artifact outside the
   pipeline). This is the only place where "rebuilds everything" is currently false.
2. **Seed the `np.random.permutation` call in `stage_c`** (A10) so the reported p-value
   is bit-reproducible.
3. **Fix the bias-sign convention in `06d`** to match the rest of the package
   (forecast − actual), and **name the two endpoints of the 4Q26 print/guide range
   explicitly in the note prose** (§4 above) so a reader doesn't have to reverse-engineer
   which numbers bound it.
4. Carry forward, unchanged, the fixes the implementer already flagged and I
   independently confirmed as real: the fiat/gbv-consistent de-gross-up ruling needed
   before the memo (Finding 2), and sourcing the 15-Sep/13-Oct-2026 deadlines (confirmed
   genuinely absent from the repo, §3/§4 above).

None of these change the substantive conclusions (theta unidentified; take rate is an
output, not a forecasting lever; backtest is negative on both objects; the fee step is
smaller than the architect's implied 2.5%). They are reproducibility and presentation
fixes, not correctness reversals — hence **partial**, not **fail**.
