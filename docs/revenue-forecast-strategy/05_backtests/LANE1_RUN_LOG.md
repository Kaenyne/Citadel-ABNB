# Lane 1 run log

## 0b. Data-access check

Started 2026-09-12 13:28:32 UTC. Working branch: `codex/lane1-full`; base: `origin/main` at `b1dcdf91f77156b4cdbcf9a334db9b04cab30135` (PR #48 merged). Original workspace: `main` at `86dacad487e7763f4eea392271d5cadf6bcf7ccf`. Remote: `https://github.com/Kaenyne/Citadel-ABNB.git`.

The main-branch prompt predates section 0b. Its exact 39-path manifest was read from the prompt-only follow-up commit `9c2892b31870e59cdfc17e3b7609d744eabe711d` on the kit branch, matching the user's instructions. The analytical base remains merged `main`.

### Required paths — verbatim output

```text
START_BRANCH codex/lane1-full
START_COMMIT b1dcdf91f77156b4cdbcf9a334db9b04cab30135
BASE origin/main; PR #48 merged
Original workspace: main at 86dacad487e7763f4eea392271d5cadf6bcf7ccf
File manifest: origin/theo/thesis-kernel-topdown at 9c2892b31870e59cdfc17e3b7609d744eabe711d, prompt section 0b
ok       data/processed/overnight/02_kpi_panel_quarterly.csv
ok       data/processed/overnight/02_kpi_panel_long.csv
ok       data/processed/overnight/02_guidance_ledger.csv
ok       data/processed/overnight/02_guidance_cushion_series.csv
ok       data/processed/overnight/02_fy_guide_revisions.csv
ok       data/processed/overnight/16_consensus_at_print_merged.csv
ok       data/processed/overnight/04_consensus_at_print.csv
ok       data/processed/abnb_earnings_reactions.csv
ok       data/processed/abnb_daily_close.csv
ok       data/processed/overnight/10_xbrl_revenue_geography.csv
ok       data/processed/overnight/10_regional_panel_quarterly.csv
ok       data/processed/overnight/10_regional_forecast.csv
ok       data/processed/overnight/10_fx_daily.csv
ok       data/processed/overnight/10_fx_basket.csv
ok       data/processed/overnight/10_regional_fx_passthrough.csv
ok       data/processed/overnight/05_crossborder_share.csv
ok       data/processed/overnight/08_feature_tests_all.csv
ok       data/processed/overnight/12_exit_multiple_recommendation.csv
ok       data/processed/overnight/12_peer_multiples.csv
ok       data/processed/overnight/13_valuation_summary.csv
ok       data/processed/overnight/13_model_annual.csv
ok       data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv
ok       data/processed/nights_baseline_reconciliation.csv
ok       data/processed/abnb_backlog_indicators.csv
ok       data/processed/adr/01_regional_annual.csv
ok       data/processed/adr/04_regional_quarterly.csv
ok       data/processed/forecast_methods/L0/L0_vintage_register.csv
ok       data/processed/forecast_methods/L0/L0_exact_regional_revenue.csv
ok       data/processed/forecast_methods/L0/L0_interval_observations.csv
ok       data/processed/forecast_methods/kernel_phi_v2
ok       data/processed/forecast_methods/l1_reconciliation_v2
ok       data/processed/forecast_methods/fx_lag_v2
ok       data/processed/forecast_methods/registry
ok       analysis/src/forecast_methods/harness/README.md
ok       analysis/src/forecast_methods/kernel_lambda/run.py
ok       docs/thesis-kernel-topdown/lane1/K0_KERNEL_ENGINE.md
ok       docs/thesis-kernel-topdown/lane1/X_REGIONAL_KERNEL_OD_FX.md
ok       docs/revenue-forecast-strategy/AGENT_BRIEF.md
ok       docs/revenue-forecast-strategy/WORKBOARD.md
MANIFEST TOTAL 39 | PRESENT 39 | MISSING 0
ok       docs/thesis-kernel-topdown/lane1/README.md
ok       docs/thesis-kernel-topdown/lane1/A_GUIDE_SURPRISE.md
ok       docs/thesis-kernel-topdown/lane1/B_TERM_STRUCTURE.md
ok       docs/thesis-kernel-topdown/lane1/V_VALUATION_RECONCILIATION.md
ok       docs/thesis-kernel-topdown/lane1/D_LAMBDA_CARD.md
ok       docs/thesis-kernel-topdown/lane1/R_REGIONAL_REFRESH.md
ok       docs/thesis-kernel-topdown/lane1/C3_GBV_FEATURES.md
ok       docs/thesis-kernel-topdown/lane1/REFUTER.md
ok       docs/thesis-kernel-topdown/lane1/CLOSE.md
FILE ACCESS PASS
```

### Test, acceptance, loader and network checks

All required checks passed. No subagents were spawned before completion.

```text
COMMAND: python -m pytest analysis/src/forecast_methods/harness/tests analysis/src/forecast_methods/L0 -q
...............................................                          [100%]
47 passed in 22.15s

ISOLATED REPRODUCTION: 113 tracked files copied; original frozen files unchanged
COMMAND: python analysis/src/forecast_methods/kernel_lambda/run.py (copied repository root, original .venv interpreter)
[0] KPI panel and harness targets agree on revenue and GBV over 24 quarters
[A] acceptance test: PASS on all 12 cells to 2dp; Q4 within-season range 0.171pp (expected 0.171)
[A] extra usable cells not in the architect table: 1Q23 12.803, 2Q23 13.724
[B] n22_2021Q1plus     n=22 argmin(LOO) w=0.76 LOO 3.141% | at 2/3 3.273% | at 0.38 4.944% | +5% flat band [0.67,0.86] | boot 95% CI on argmin [0.26,0.90] (n_boot=400)
[B] n18_2022Q1plus     n=18 argmin(LOO) w=0.68 LOO 1.891% | at 2/3 1.891% | at 0.38 2.210% | +5% flat band [0.53,0.84] | boot 95% CI on argmin [0.08,0.88] (n_boot=400)
[B] n14_2023Q1plus     n=14 argmin(LOO) w=0.32 LOO 1.534% | at 2/3 1.834% | at 0.38 1.544% | +5% flat band [0.17,0.48] | boot 95% CI on argmin [0.00,0.86] (n_boot=400)
[B] n12_accept_cells   n=12 argmin(LOO) w=0.13 LOO 1.548% | at 2/3 2.154% | at 0.38 1.705% | +5% flat band [0.00,0.30] | boot 95% CI on argmin [0.00,0.86] (n_boot=400)
[B] cost of flatness on 4Q26 at GBV_3Q26=26,300: w=2/3 base 26,600 x 12.030% = 3,200M ; w=0.38 base 26,858 x 11.890% = 3,193M ; gap +6M (+0.20%)
[B] sensitivity band w in [0.33, 2/3]: 4Q26 print 3,192-3,200M
[C] lag poly n22_2021Q1plus     n=21 p=7 phi = [0.225, 0.604, 0.172, 0.000] mean lag 0.95q  rel-RMSE 1.26%  phi0 95% block-boot CI [0.162,0.517] P(phi0>0.02)=0.99
[C]   phi0=0 restricted: phi = [0, 0.866, 0.134, 0.000] mean lag 1.13q  in-sample 2.18%  ||  LOO free 2.95% vs phi0=0 3.30% (n=21)
[C] lag poly n18_2022Q1plus     n=18 p=7 phi = [0.405, 0.179, 0.360, 0.056] mean lag 1.07q  rel-RMSE 0.88%  phi0 95% block-boot CI [0.096,0.633] P(phi0>0.02)=0.98
[C]   phi0=0 restricted: phi = [0, 0.658, 0.231, 0.111] mean lag 1.45q  in-sample 1.45%  ||  LOO free 1.45% vs phi0=0 2.30% (n=18)
[C] lag poly n14_2023Q1plus     n=14 p=7 phi = [0.390, 0.041, 0.569, 0.000] mean lag 1.18q  rel-RMSE 0.75%  phi0 95% block-boot CI [0.032,0.920] P(phi0>0.02)=0.97
[C]   phi0=0 restricted: phi = [0, 0.313, 0.687, 0.000] mean lag 1.69q  in-sample 1.13%  ||  LOO free 1.28% vs phi0=0 1.74% (n=14)
[D] FX wedge architect_12_cells           n=12 slope +0.233 se 0.252 t +0.93 p 0.35  interval-likelihood slope set [+0.087,+0.373]  distinguishable from zero: False
[D] FX wedge all_seasons_2023Q1plus_n14   n=14 slope +0.184 se 0.216 t +0.85 p 0.39  interval-likelihood slope set [+0.051,+0.304]  distinguishable from zero: False
[D] FX wedge all_available                n=15 slope +0.193 se 0.207 t +0.94 p 0.35  interval-likelihood slope set [+0.055,+0.322]  distinguishable from zero: False
registered   48 rows -> kernel-lambda__revenue_level_next_q.csv
[C] registered kernel-lambda__revenue_level_next_q: 48 rows ({'W1': 28, 'W2': 20})
registered   48 rows -> kernel-lambda__revenue_level_next_q_w038.csv
[C] registered kernel-lambda__revenue_level_next_q_w038: 48 rows ({'W1': 28, 'W2': 20})
registered   48 rows -> kernel-lambda__revenue_level_next_q_w033.csv
[C] registered kernel-lambda__revenue_level_next_q_w033: 48 rows ({'W1': 28, 'W2': 20})
registered   48 rows -> kernel-lambda__revenue_yoy_next_q.csv
[C] registered kernel-lambda__revenue_yoy_next_q: 48 rows ({'W1': 28, 'W2': 20})
registered   48 rows -> kernel-lambda__revenue_level_h1.csv
[C] registered kernel-lambda__revenue_level_h1: 48 rows ({'W1': 28, 'W2': 20})
registered   48 rows -> kernel-lambda__revenue_level_next_q_last3.csv
[C] registered kernel-lambda__revenue_level_next_q_last3: 48 rows ({'W1': 28, 'W2': 20})
registered   48 rows -> kernel-lambda__revenue_level_next_q_ex_covid.csv
[C] registered kernel-lambda__revenue_level_next_q_ex_covid: 48 rows ({'W1': 28, 'W2': 20})
registered   48 rows -> kernel-lambda__revenue_level_next_q_last3_ex_covid.csv
[C] registered kernel-lambda__revenue_level_next_q_last3_ex_covid: 48 rows ({'W1': 28, 'W2': 20})
[E] 3Q26 print object: 27,867M x 17.239% = 4,804M (w=2/3, no GBV forecast).  sensitivity w in [0.33,0.667]: 4,804-4,819M
[E] 4Q26 central (GBV_3Q26=26,300, w=2/3): base 26,600M x 12.030% = print 3,200M, guide mid 3,141M (cushion +1.86%).  No fee step, no FX added.
[E] driver-printed share pitch_2026-10-02 (2026Q4): w=2/3 0.333 | w=0.38 0.620
[E] driver-printed share guide_2026-11-05 (2026Q4): w=2/3 1.000 | w=0.38 1.000
[E] driver-printed share guide_2027-02 (2027Q1): w=2/3 1.000 | w=0.38 1.000
[E] driver-printed share guide_2027-05 (2027Q2): w=2/3 1.000 | w=0.38 1.000
registered    2 rows -> kernel-lambda__live_3q26_print.csv
registered    2 rows -> kernel-lambda__live_4q26_print.csv
[E] live_4q26_print: registered with strict_windows=False (quarter 2026Q4 maps to no window); also written locally
[done] all stages complete
KERNEL_EXIT_CODE 0

COMMAND: loader check from prompt section 0b
calendar rows 25 | targets rows 25 | registry files 13 methods
vintage register rows 161 | LSEG 6 Aug Q3 = 4610.0
72 exact regional cells: 72

Network probes inside sandbox: FRED 000; NTTO 000; Eurostat 000; yfinance connection refused.
Authorized probes outside sandbox:
FRED 200
NTTO 200
Eurostat 200
yfinance 170.19000244140625
no Rscript (X replicates the engine in Python)
```

The full frozen kernel runner executed without source changes against an isolated copy of 113 tracked files. All regenerated outputs and registrations remained in that temporary copy and were discarded after verification; the shared checkout's existing packages, registry and harness outputs were not overwritten. Console output above documents legacy-run reproduction, not approval of historical investment claims. No new forecasts have been registered.

Public-data mode: FRED/NTTO/Eurostat/yfinance online with tool-level network authorization; sandbox-only requests are blocked. Python dependency installation completed with exit code 0. GitHub CLI was not found on PATH or in standard installation locations.


## Setup

The pre-existing `.venv` referenced an inaccessible Microsoft Store Python 3.13 executable. It was recreated using bundled Python 3.12.14. Installation command: `.venv/Scripts/python.exe -m pip install -r requirements.txt pymc arviz scikit-learn pyarrow linearmodels lightgbm duckdb yfinance pytest`.

The sandbox denied writes to `.git/FETCH_HEAD` and PyPI network access. Fetch, branch creation and dependency installation required tool-level approval. No credentials were read or entered. No licensed service was contacted. Unrelated untracked workspace files were preserved.

## Gate 1 — STOP

The K0 pass line was written before execution in `K0_KERNEL_ENGINE.md`. The first module pytest command returned exit code 1; Gate 1 is not green. Per the user's STOP condition, no test was changed or rerun to bypass this result, and no downstream analytical work was started.

```text
COMMAND: python -m pytest analysis/src/forecast_methods/kernel_engine_v1/tests -q
..................F............................                          [100%]
================================== FAILURES ===================================
________________ test_acceptance_twelve_exact_accounting_cells ________________

    def test_acceptance_twelve_exact_accounting_cells():
        expected={"2024Q1":13.034,"2025Q1":12.325,"2026Q1":12.612,
                  "2024Q2":13.449,"2025Q2":13.946,"2026Q2":13.736,
                  "2023Q3":17.391,"2024Q3":17.145,"2025Q3":17.182,
                  "2023Q4":11.946,"2024Q4":12.117,"2025Q4":12.026}
        got=E.lambda_table(AS_OF).set_index("quarter").lambda_pct
        for quarter,value in expected.items():
>           assert round(float(got[quarter]),2)==round(value,2)
E           assert 12.33 == 12.32
E            +  where 12.33 = round(12.325497287522605, 2)
E            +    where 12.325497287522605 = float(np.float64(12.325497287522605))
E            +  and   12.32 = round(12.325, 2)

analysis\src\forecast_methods\kernel_engine_v1\tests\test_engine.py:45: AssertionError
============================== warnings summary ===============================
analysis/src/forecast_methods/kernel_engine_v1/tests/test_engine.py: 69 warnings
  C:\Users\wille\Desktop\Citadel - ABNB\analysis\src\forecast_methods\kernel_engine_v1\engine.py:79: PerformanceWarning: DataFrame is highly fragmented.  This is usually the result of calling `frame.insert` many times, which has poor performance.  Consider joining all columns at once using pd.concat(axis=1) instead. To get a de-fragmented frame, use `newframe = frame.copy()`
    f["print_date"] = f.quarter.map(_calendar())

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED analysis/src/forecast_methods/kernel_engine_v1/tests/test_engine.py::test_acceptance_twelve_exact_accounting_cells
1 failed, 46 passed, 69 warnings in 6.85s
```

The defect is in the new acceptance comparator: it separately rounds a full-precision computed value and a three-decimal published reference. For 2025Q1, `round(12.325497287522605, 2)` is `12.33`, whereas `round(12.325, 2)` is `12.32`. The existing frozen runner uses a different, three-decimal tolerance comparison and passed. This does not establish a revenue/GBV arithmetic error, but the required new-module pytest is failing, so Gate 1 fails. The test and implementation remain as executed for audit. No live default was frozen from a results run; `run.py` and its runtime acceptance remain unexecuted.

Post-failure preservation check (not a retry of Gate 1):

```text
COMMAND: python -m pytest analysis/src/forecast_methods/harness/tests analysis/src/forecast_methods/L0 -q
...............................................                          [100%]
47 passed in 11.60s
```

No previously tracked source, data, package note, harness file or L0 file was altered; only the explicitly requested workboard and this new run log changed. New K0 source, tests and documentation are unvalidated and must not be used as an accepted kernel.

## Checkpoints and totals at the STOP

- Shared repository: `https://github.com/Kaenyne/Citadel-ABNB.git`.
- Base: `b1dcdf91f77156b4cdbcf9a334db9b04cab30135`, merged PR #48.
- Preflight checkpoint: `7ce13286b4c86ba445a20a58f1eba7173eb7a96a`, pushed to `origin/codex/lane1-full` and independently verified with `git ls-remote`.
- Gate 1: failed; no accepted K0 package.
- Gate 2: not started. A verdict and all three A refuters: not run.
- B, V, D, R, C3, X: not spawned. X verdict and FX conclusion change: not assessed; B4 is not superseded by this run.
- Refuters: 0. Proposed or surviving memo claims: 0.
- Subagents spawned: 0. Gate failure occurred before spawning was authorized.
- Scorer and final analytical close: not run because Gate 1 STOP applies.
- GitHub CLI: unavailable; no PR has been created. Use the shared repository's compare link if a review of this blocked checkpoint is desired.
- Tokens: exact usage unavailable from this runtime; no estimate reported as a measurement.
- Start: 2026-09-12 13:28:32 UTC. STOP accounting timestamp: 2026-09-12 21:39:25 UTC. Elapsed wall time: 8h 10m 53s, including tool-approval waits. Preservation/push time is recorded separately below.

## RESUME

Resume only after the user responds to the Gate 1 STOP. Resolve the acceptance-test rounding boundary against the brief's stated precision, retaining this failed test output as evidence. Then rerun and independently assess the entire Gate 1 contract, including a full K0 entry-point run under 60 seconds and the frozen 47-test suite, before spawning A. Review the unvalidated module's scenario, timestamp and regional limitations before promoting it. Do not silently convert the preflight runner's successful acceptance check into a Gate 1 pass.

## Preservation checkpoint

Failure artifacts prepared at 2026-09-12 21:49:39 UTC. Elapsed since start: 8:21:07 (includes approval waits). Only the failed implementation, its evidence and blocked-status documentation are staged; no analytical work resumed after the STOP.
