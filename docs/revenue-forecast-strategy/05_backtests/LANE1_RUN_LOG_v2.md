# Lane 1 resumed run log

## 0b. Data-access check

### Preserved original full output

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



Original full check output is preserved in LANE1_RUN_LOG.md, first section: 39/39 required paths; 47 passed; frozen kernel acceptance PASS on all 12 cells; calendar 25, targets 25, registry methods 13, vintage register 161, exact regional cells 72; pre-guide LSEG Q3 4610.0; FRED/NTTO/Eurostat HTTP 200; yfinance succeeded; Rscript unavailable. No raw or licensed files added. This resumption starts from codex/lane1-full at f68965a2a57c78dac58dc4ccce43626ae7f489d2 in shared Kaenyne/Citadel-ABNB, after explicit user instruction to redo the failed gate. Original base main: b1dcdf91f77156b4cdbcf9a334db9b04cab30135. V2 test results will be appended here.

## Corrections and execution constraints

V1 was prematurely stopped on an acceptance-test rounding bug. It was pushed unvalidated and remains labelled failed. V2 is a new package; the failure record is preserved. Downstream packages must import v2. Runtime permits three child agents alongside the parent; the six independent packages will therefore run in two concurrent batches, with X prioritized. No human intervention is required for this scheduling limit.

## Totals

Pending. Actual token accounting is unavailable from the agent runtime; do not substitute the prompt budget for usage.

## V2 development checks

First v2 check: 1 failed, 62 passed (18.51s); CLI acceptance FAIL because the supplemental two-decimal check retained binary bankers rounding for 17.145. All twelve full-precision identities were already inside their 0.001pp publication intervals. Corrected only the display comparator to explicit decimal half-up for published Q3/Q4 references; the interval acceptance threshold and analytical values are unchanged. This failed development run is retained here.

## Gate 1 passed

Module command: python -X utf8 -m pytest analysis/src/forecast_methods/kernel_engine_v2/tests -q
63 passed in 24.29s; exit 0.

Frozen command: python -X utf8 -m pytest analysis/src/forecast_methods/harness/tests analysis/src/forecast_methods/L0 -q
...............................................                          [100%]
47 passed in 5.44s

CLI command: python -X utf8 analysis/src/forecast_methods/kernel_engine_v2/run.py
acceptance test: PASS on all 12 cells
quarter  lambda_pct  expected_pct display_2dp  match_reference_precision
 2023Q3   17.390785        17.391       17.39                       True
 2023Q4   11.946140        11.946       11.95                       True
 2024Q1   13.034483        13.034       13.03                       True
 2024Q2   13.448613        13.449       13.45                       True
 2024Q3   17.145482        17.145       17.15                       True
 2024Q4   12.117264        12.117       12.12                       True
 2025Q1   12.325497        12.325       12.33                       True
 2025Q2   13.945946        13.946       13.95                       True
 2025Q3   17.181818        17.182       17.18                       True
 2025Q4   12.025974        12.026       12.03                       True
 2026Q1   12.612245        12.612       12.61                       True
 2026Q2   13.736041        13.736       13.74                       True
LIVE DEFAULT ewm (historical default selection is nested before each origin)
 variant window  n  rmse_pct                       basis
ex_covid     W1 14  1.829421 retrospective_LOO_selection
ex_covid     W2 10  2.067514 retrospective_LOO_selection
   last3     W1 14  1.829421 retrospective_LOO_selection
   last3     W2 10  2.067514 retrospective_LOO_selection
     ewm     W1 14  1.804318 retrospective_LOO_selection
     ewm     W2 10  2.020128 retrospective_LOO_selection
quarter       point  guide_mid_musd               status
 2026Q3 4808.362929     4723.784001         printed_lags
 2026Q4 3214.775751     3158.227962 conditional_scenario
 2027Q1 3121.422848     3066.517133 conditional_scenario
{
  "as_of": "2026-09-12",
  "acceptance_pass": true,
  "acceptance_n": 12,
  "live_default": "ewm",
  "historical_default": "nested W1 LOO within the pre-origin information set; ex_covid fallback below eight common cells",
  "run_seconds": 5.384324299986474,
  "under_60_seconds": true,
  "guide_origins": 14,
  "guide_origins_refused": 14,
  "rnpl_scenario_available": "2026-09-11",
  "frozen_files_modified": false,
  "registered_forecasts": 0
}

The complete module tests were run before starting A. Full source v1 is unchanged; v2 is the selected dependency.

## Checkpoint and baseline scorer

Gate 1 checkpoint 801feaf pushed successfully to origin/codex/lane1-full at shared Kaenyne/Citadel-ABNB. A spawned alone from the version-corrected single brief. Frozen scorer executed unchanged in a SHA-256-verified temporary copy: exit 0, 19.46 seconds, 4,109 registry rows, 69 objects, 276 score groups. All 276 fresh RMSE groups match frozen scoreboard.csv (zero changed). Baseline leaders for PIT revenue: optimal-mix / mix_revenue_musd_parsimonious W1, RMSE 33.884250 at n=14; optimal-mix / mix_revenue_musd_all W2, RMSE 33.922215 at n=10. These frozen baseline forecasts may include same-day information and are not a strict pre-guide alpha comparison. Receipt: data/processed/forecast_methods/lane1_control_v2/before-a/receipt.json.

## Gate 2 parent review — passed (clean negative)

A note first paragraph says underpowered; its pass line was inspected on disk before its run. W1 0/14 and W2 0/10 signals, zero |S|>1pp cells, Wilson/hit-rate/permutation/slope/return estimates explicitly undefined at n=0. Consensus rows and exclusions retain vendor, timestamp, register ID; September values appear only in the dated live scenario. Supplied reactions have zero open_* columns, and no close return was substituted. K0 v2 imported directly, lambda not re-derived. Figure visually inspected: strict empty sample and 11 post-letter points clearly separated. Note includes all three baselines, 1/5/20-day conditional counts and honest unregistered status. No send-back required. A unit suite 12 passed; rebuild exit 0. Frozen harness/L0 after A: 47 passed in 5.10s. Gate 2 therefore permits the independent tail. No historical edge claim admitted.

Original package brief copies change only K0 dependency and execution routing. Six packages will be launched with one brief each, in two batches because runtime permits only three children. X has first priority. Scorer already ran and no A registration changed the registry.

## Parallel tail launched and runner interruption

Gate 2 checkpoint 87a2807 pushed to shared origin/codex/lane1-full. X, B and V launched independently with one brief each; R, C3 and D queued for slots. All can deliver public/offline parts without nonpublic inputs. During the tail, the shared local command runner stalled for approximately 22 minutes; parent command failed before process spawn, while a V read completed after the delay. A fresh parent read succeeded at 2026-09-13 00:14:54 UTC. This infrastructure delay is included in wall time, not reported as analytical work. Existing validated checkpoints remained pushed.

## Tail packages returned so far

B returned underpowered: 6 tests passed; final rebuild exit 0 in 7.667 seconds; W1 0/14 and W2 0/10 eligible FY-revision tests; open 20/60-day pairs 0/0. Live Q4/Q1 calculations are labelled conditional and weight changes are fixed-lambda arithmetic sensitivities. No annual-gap registration was mislabelled as quarterly revenue. Parent read the completed note and receipt. R launched into B's freed slot.

V returned partial: 6 tests passed; final rebuild exit 0; parent visually inspected the 1920x1080 one-screen exhibit. Change-regression slope 0.4860 with HAC95% [0.3172,0.6548], inherited-vintage diagnostics only. Final base EBITDA lens 180.88 versus six-lens mean 156.79 are distinct model objects. Yahoo public refresh succeeded, last close 170.19 on 11 September; snapshot source/timestamps retained. No price/multiple row was forced into the revenue harness. C3 launched into V's freed slot. X remains active; D is the final queued package. No package has yet failed execution or required a re-spawn.

Frozen harness/L0 after B and V: 47 passed in 5.30 seconds. No frozen-file diffs. Parent inspected R and C3 pre-registration notes before their reported results. C3 was reminded that an uncorrected comparator cannot silently replace the required RNPL-corrected baseline.

B/V checkpoint 7f5247a pushed successfully. C3 returned underpowered: seven tests passed; rebuild exit 0 in 0.932s; no promotions/registrations; required comparator has zero cells, while raw-ledger comparisons share three quarters and are vacuous. Parent read complete note and exclusions. D launched into C3's freed slot; all six requested independent tail agents have now been spawned. X and R still completing.

D returned partial: new addendum only, zero fitted parameters or registry rows, 2/5 publication-scoreable rows. Parent independently reproduced the exact fixed-threshold revenue cutoffs 4762.413333 / 4717.826667 and six integer-boundary classifications. Next-quarter labelling, frozen-denominator interpretation and D-06/D-10 numbering conflict remain explicit. No team decision adopted.

X returned underpowered: final 19 tests passed, CLI exit 0 in 22.8s, 24 annual identities, 72 regional cells/18 sums, K0 and Python R-contract checks pass. No measured Airbnb currency matrix; 0/14 W1 and 0/10 W2 PIT observations. Principal after-hedge Q3/Q4 scenarios +3.4–3.8/+1.5–1.7pp; regional ADR-pass-through sensitivity +3.2–3.6/+1.0–1.1pp. Fading-tailwind direction remains and B4 is not superseded. Parent read completed note and interface/coverage receipts. Refuter X briefs explicitly require O-D vintage and FX-mechanism checks.

## Tail complete; one R correction

R returned partial with 72/72 accounting identities, a 1.3943pp 2024 ADR attribution residual, and wide conditional regional bands. Parent rejected its two newly created registry files because the frozen LIVE date had been used as a format slot for a later reconstruction. A dedicated R retry preserved all 12 rejected rows byte for byte with SHA manifests under UNREGISTERED_rejected_registry_20260913, removed the two shared-registry files, and removed registry writes from the runner. Actual UTC reconstruction time now accompanies local candidates. Corrective CLI exit 0 in 2.02 seconds; 7 tests passed in 2.59 seconds; all 12 numerical points and 19 analytical files unchanged. Parent inspected the corrected source, tests and receipt. This is the one permitted R send-back, resolved. No accepted registration was added by any tail package. Frozen harness/L0 after removal: 47 passed in 3.41 seconds; no K0 v2 or frozen-file diff.

All six independent tail packages returned. Runtime concurrency required staggered starts (maximum three children); each received one brief. The remaining tail checkpoint precedes 15 independent refuters. Tokens are unavailable from the runtime and will not be estimated.

## Tail checkpoint and final scorer

Tail checkpoint c1fc6e6 pushed to shared Kaenyne/Citadel-ABNB. A vintage, power and mechanism refuters launched independently with one parameterized brief each and no conversation history. X then V, R and B are queued for the three available child slots.

Final frozen scorer ran after the last registry correction through the unchanged, byte-verified temporary-copy adapter: exit 0 in 20.15 seconds; 4,109 rows, 69 objects, 276 groups. All 366 input hashes and all 276 scored rows are identical to the before-A baseline. Zero accepted new registrations; zero changed leaders. SCOREBOARD_v3 is therefore not required or created. Comparison receipt: data/processed/forecast_methods/lane1_control_v2/final/comparison.json. Frozen harness/L0 at close: exactly 47 passed in 8.32 seconds. The only modification relative to the starting base among previously existing files is the explicitly authorized WORKBOARD update; all frozen paths and original package files remain unchanged.

## Refutation checkpoint A

A: vintage survived (7 attacks), power survived (8), mechanism survived (7): 3/3. Independent strict counts reproduce 0/14 and 0/10; the key caveat is that same-day-inclusive consensus alone supplies 13/14 and 9/10 but still does not establish complete pre-release kernel signals. Missingness can reproduce the zero for every forecasting model, so no causal kernel inference follows. Numerical power/Wilson intervals remain undefined at n=0. All three notes include independent commands and explicit attack results.

X vintage and power launched in fresh agents. Creating another fresh X mechanism thread hit the runtime agent-thread limit; attempting an unloaded earlier agent also failed. Reusing the still-live completed A-power agent with only the X-mechanism brief succeeded. Remaining reviews will likewise reuse available completed agents. Each package still receives three distinct agents/lenses, each reading only its assigned note and inputs; the original package author never refutes its own package. This runtime adjustment preserves all 15 required reviews.

## Refutation checkpoint X and concurrent-main check

X: vintage survived (7 attacks), power survived (8), mechanism survived (9): 3/3. The source-vintage review independently verifies all 14/10 guide dates against actual later source releases; modern reconstruction time alone is not a sufficient look-ahead test. Exposure examples reproduce but remain assumed. Mechanism arithmetic verifies 3.879pp gross/3.669pp after-hedge Q3 midpoint and positive but fading FX across all displayed scenarios. Pure predictor rescaling can explain much of the apparent fitted-scale improvement without changing predictions. The near-zero ex-FX residual can change sign with translation convention. X does not justify replacing B4. Total A+X attacks: 46.

A-refuter/scorer checkpoint 5a638dc pushed. Concurrent main advanced 12 commits to cde896a274cf6f36eff64461737bf96c6871858f. Read-only virtual merge check after fetching main returned exit 0 and tree da4246660f871de8952ff1f7f977c8825ee1d4f7: no conflicts. Working analytical inputs were not changed or merged mid-study. V vintage/power/mechanism reviews now running on three distinct agents.

## Refutation V

V: vintage survived (7 attacks), power survived (7), mechanism survived (8): 3/3 on the exact conditional arithmetic sentence. Independent rebuilds of all six lenses produce 180.876286 / mean 156.786845. The component and mean share one operating scenario and are not independent estimates. Supporting-source attacks succeeded: stale convention CSV retains old undiscounted FY28 metadata; exact September cash/share interpolation differs from the adopted year-end convention; one multiple turn rounds to 9.90. The W1 statistical description also fails literal replication: 45 monthly changes yield 0.505028, while the reported 35-row/0.486022 result excludes Jan–Oct 2023. Parent source inspection finds growth/margin filters before differencing, missing from the pre-result note. Supporting statistical claims are excluded, not silently repaired. Cumulative A/X/V attacks: 68.
