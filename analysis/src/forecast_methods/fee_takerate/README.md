# fee-takerate

Take rate by mechanism: the fee schedule function, the migrated share, pass-through
theta, and the printed take rate as an OUTPUT.

**theta is UNIDENTIFIED for the mandatory cohort.** See the first line of the note.

## Run

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/fee_takerate/run.py
```

Exit code 0. Rebuilds everything, writes progressively, re-runnable. Then score:

```bash
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/harness/score.py
```

## Files

| file | what it is |
|---|---|
| `fee_schedule.py` | **THE** fee function, **THE** de-gross-up, **THE** migrated share. Nobody else touches these three. Self-tests with `python fee_schedule.py`. |
| `run.py` | entry point; stages (a)-(f) of the spec, plus stage (e2) which rebuilds the backtest scorecard |

## Reproducibility note (fixed after verification r1)

`06c_backtest_scorecard.csv` and `06d_seasonal_naive_benchmark.csv` were previously stale
files on disk that no code path regenerated. They are now produced by `stage_g` in
`run.py`, from the harness's own `score_registry` over this package's registry rows.
`run.py` genuinely rebuilds every file listed under **Outputs** below.

**Do not read `harness/scoreboard.csv` for this package's RMSE ratios.** The shared
registry contains no baseline for `target = take_rate_pct`, so the scoreboard reports
`rmse_ratio_to_naive = NaN` on every fee-takerate row. NaN means *no denominator was
registered*, not *beats naive*. Both denominators are built locally in `stage_g`
(growth naive from `harness.baseline_naive`; seasonal naive as tau[q-4], because
`harness.baseline_naive_seasonal` returns 0.0 on this metric -- it is classified
growth-like by name). See the harness change request in the note.

## Ownership (binding)

* The single ADR de-gross-up lives in `fee_schedule.host_payout_from_reported_adr()`
  and nowhere else. `l1-reconciliation` must NOT de-gross-up.
* The ADR workbook "reprice" row and `13_driver_model.py`'s `take_bps` lever are the
  same event as the migration modelled here. Both are **deleted**; the replacement is
  `05b_takerate_mechanism_fy27.csv`.
* The migrated share is **exogenous and dated**. It is never fitted against GBV.
  It lives in `fee_schedule.LISTING_SHARE_PATH` and `CONCENTRATION_M`.
* theta is an **explicit argument** of every price-moving function. There is no default.

## Source warning: the deadlines are NOT in the repo

`data/processed/overnight/06_fee_timeline.csv` has 19 rows, latest `2026-08`. The
**15-Sep-2026 (ex-EEA)** and **13-Oct-2026 (EEA + CH)** migration deadlines appear
**nowhere in it** — verified by acceptance test A8. They are carried in
`fee_schedule.LISTING_SHARE_PATH` as an explicit dated assumption with no repo source.
Somebody must source them before they go in the memo.

## Outputs

`data/processed/forecast_methods/fee_takerate/`:
`00_acceptance_tests.csv`, `01_theta_reproduction.csv`, `02_uplift_by_theta.csv`,
`03_migrated_share_path.csv`, `04a/04b` take-rate history + regression,
`05a/05b/05c` mechanism build and driver-model comparison,
`06_backtest_takerate_raw.csv`, `06b` perfect-foresight error, `06c` scorecard,
`06d` seasonal-naive benchmark, `07a` 3Q26 live, `07b` 4Q26 fee step,
`07c` FY27 contribution, `07d` mechanism path all quarters,
`08_dual_basis_capture_plan.csv`, `09_parameter_counts.csv`.

Registry: `fee-takerate__take_rate_kernel.csv`, `fee-takerate__take_rate_lastyear.csv`,
`fee-takerate__take_rate_mechanism.csv`.
