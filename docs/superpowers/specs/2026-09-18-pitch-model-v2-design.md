# Pitch model v2 — design

**18 September 2026 · Theo with Claude (Fable 5.1) · branch `theo/pitch-model-v2` · workspace `~/Citadel-ABNB`**

## 1. Purpose

Build the Excel model that is submitted with the two-page memo on 2 October 2026. Every number a judge can point at must be reproduced from the repo's own code, carry its evidence next to it, and be recomputable live inside Excel. The long/short call is a derived output of the model, decided last, not an input assumed first.

The three existing workbooks (`model/ABNB_driver_model.xlsx`, `model/lane4_v2/.../ABNB_L4_review.xlsx`, `model/ABNB_pitch_model.xlsx`) are built by scripts that copy output values into cells. The number survives; the argument, the test it passed, and the test it failed stay in the 238 backtest notes. This design puts the argument in the file.

Success test, agreed with Theo: a judge opening the file can (a) trace every input to its evidence, source note, reproduction receipt, and test record; (b) change one driver and watch the chain recompute through revenue, guide, margin, EPS, and price; and (c) see the call fall out of the lines.

Proof bar, agreed: a value enters only if a subagent re-ran the package script or recomputed it from the processed CSV and the number matched.

## 2. Non-negotiables inherited from the repo

`CLAUDE.md` rules apply unchanged: copy never overwrite; point-in-time or it does not count (W1 from 1Q23, W2 from 1Q24; a result must survive both to be quoted); pre-register before testing; never commit to `main`; never commit licensed raw exports; no scraping beyond sanctioned sources; never type credentials; quote nothing on the kill lists (`docs/revenue-forecast-strategy/AGENT_BRIEF.md` §6, `docs/margin-build/SYNTHESIS.md` §9).

All new work lives in new folders: `analysis/src/pitch_model_v2/`, `model/pitch_model_v2/`, `docs/pitch-model-v2/`, `data/processed/pitch_model_v2/`. Nothing under the frozen folders is touched.

## 3. Workspace

The OneDrive checkout cannot host this programme. The disk was at 4 GB free on 18 Sep; OneDrive had evicted most tracked files and the git pack files themselves to cloud-only placeholders (`ls -lO` shows `dataless`), and three `git merge --ff-only` attempts died with `mmap failed: Operation timed out`. The programme runs in the local clone `~/Citadel-ABNB`, fast-forwarded to `88a5dfc` on 18 Sep, on branch `theo/pitch-model-v2`.

Python: `python3` is 3.13 with pandas 3.0, openpyxl 3.1.5, statsmodels 0.14.6, scipy 1.17, duckdb 1.5.5, and, installed 18 Sep, pyarrow 25, pymc 6.3, arviz 1.3, scikit-learn 1.9, lightgbm 4.7, linearmodels 7.0. Diggers run scripts with `python3` from the clone root.

Untracked work that exists only in the OneDrive checkout (10 `forecast_methods` packages with their `data/processed` outputs, 24 notes under `05_backtests/`, `START_HERE_2026-09-15.md`) is copied into the clone on its own branch `theo/local-untracked-2026-09-15` so diggers can read it. It is not merged into `theo/pitch-model-v2`.

## 4. The unit of work: a line

A line is one number the judge sees. Thirty lines, in five blocks, ordered by how much of the thesis rests on them. "Where it lives" is the governing note or package as read on 18 Sep; the later audit always wins over the earlier claim.

| id | Line | Where it lives today | Digger |
|---|---|---|---|
| D1 | 3Q26 nights, level and y/y | reviews stays index (`q3nowcast/E`, `q3nowcast_v2/E`), `WPK_reviews-index-2023-vintage.md`, external stack, `docs/q3nowcast/SYNTHESIS.md` | Opus |
| D2 | 4Q26 nights and the RNPL / ex-NA lap | `overnight2/D`, `B3_FY27_DECOMPOSITION.md`, adopted Q4 object in `docs/pitch-forecasts/` | Opus |
| D3 | FY27 nights path | FY27 path v2 inside bridge v3 (`analysis/src/h1_to_h2_bridge_v3.py`) | Sonnet |
| D4 | ADR ex-FX and its decomposition (geo mix, unit size, LOS, seats, residual) | ADR v3 card (`docs/adrv3`), `research/notes/2026-09-07_adr-decomposition.md`, `L3_ADR_HOTEL_RESULTS.md` | Opus |
| D5 | ADR FX and revenue FX by quarter | `fx_lag_v2`, `data/processed/overnight/05_fx_schedule.csv`, `B4_FX_EXHIBIT.md` | Sonnet |
| D6 | GBV, with the regional cross-check | identity nights × ADR; `X_REGIONAL_KERNEL_OD_FX.md`, `R_REGIONAL_REFRESH.md` | Sonnet |
| D7 | Take rate and the fee migration | `B1_TAKE_RATE_RECONCILIATION.md`, `fee-takerate.md`, `L3_FEE_*` | Opus |
| R1 | Kernel: λ by season and the lag weights | `kernel_lambda`, `K1_*`, `K2_*`, `GD_DECISION_REPORT_v2.md` (fixed vs joint) | Opus |
| R2 | 3Q26 revenue: kernel vs guide+cushion vs bridge | `K1_*`, `B1_*`, bridge v3 | Opus |
| R3 | Guide cushion, trailing eight | `guidance_policy` | Sonnet |
| R4 | 4Q26 guide midpoint the model implies | `B2_Q4_GUIDE_EXHIBIT.md`, bridge v3 | Opus |
| R5 | 4Q26 and FY26 revenue | bridge v3 | Sonnet |
| R6 | FY27 revenue and its band | `B3_*`, FY27 path v2 | Opus |
| C1 | Cost of revenue | `docs/margin-build/notes/40_line_build.md`, `40_params.csv` | Sonnet |
| C2 | Operations and support | line build | Sonnet |
| C3 | Product development | line build | Sonnet |
| C4 | Sales and marketing, the swing line | line build, `23_final_model` combination, sentence clip | Opus |
| C5 | G&A ex lodging reserve | line build | Sonnet |
| C6 | Adjusted EBITDA and margin, 3Q26 to FY27 | `final-margin__combined` vs line build; the two open FY27 builds (34.6% vs 35.7%) | Opus |
| C7 | SBC, D&A, interest, tax, share count, EPS | line build below-EBITDA schedule, `abnb_capital_return_quarterly.csv` | Sonnet |
| C8 | FCF and SBC-adjusted FCF | `abnb_fcf_bridge.csv`, quality-of-growth notes | Sonnet |
| V1 | Street rows, vendor and date stamped | `L0_vintage_register.csv`, `M_CONSENSUS_2026-09-13.md`, `G1b_*` | Sonnet |
| V2 | Exit multiple and the turns-per-point rule | `valuation_v1`, `V_VALUATION_RECONCILIATION.md`, `docs/overnight/FINAL_SUMMARY.md` | Opus |
| V3 | Reverse DCF, market-implied and management-implied | `analysis/src/reverse_dcf` | Sonnet |
| V4 | Scenario prices and their probabilities | `docs/pitch-forecasts/` X01, S02, reaction function | Opus |
| V5 | The call: direction, target, horizon | derived from V1–V4; recorded in the decision log | Theo and Claude |
| E1 | 5 Nov print partition | `a09_v2_print_distribution` in `docs/pitch-forecasts/` | Sonnet |
| E2 | Guide-below-Street, descriptor, FY-sentence probabilities | pitch-forecasts C01, C02, C04, read against `GD_DECISION_REPORT_v2.md` | Opus |
| E3 | Day-1 and 15 Dec reaction | `abnb_guidance_reaction_panel.csv`, S01, S02 | Opus |
| E4 | Flip rules and thresholds | `PREREG_ABNB-INT-v1.md`, `D_CARD_ADDENDUM_LAMBDA.md` | Sonnet |

Out of scope as lines, in scope as dossier footnotes: World Cup sizing, hotels and Experiences, fee-deadline dates.

## 5. The dossier contract

One markdown file per line at `docs/pitch-model-v2/dossiers/<id>_<slug>.md`, reproduction outputs under `data/processed/pitch_model_v2/receipts/<id>/`. Same template for every line.

1. **Header.** Line id, the question a judge will ask, digger model, date, clone commit hash.
2. **The number.** Point, range, value per scenario, units, period, vintage date.
3. **Derivation chain.** Every hop from raw KPI or filing → processed CSV → package script → output, each named by path. "From the note" is not a hop.
4. **Governing sources.** Notes touching the line in date order; the latest audit named; older claims it superseded listed.
5. **Reproduction receipt.** Exact command, exit code, wall time, output file and cell, value obtained, tolerance, match yes/no. If not reproducible: why, and what was.
6. **Test record.** W1 and W2 results vs naive, guide+cushion, and Street baselines; pass/fail against the pre-registered line; the strongest known failure.
7. **Kill list and consistency.** Nothing from either kill list; conflicts with other lines or with memo v3 flagged (e.g. the 0.68x reviews-index claim that `WPK_reviews-index-2023-vintage.md` withdrew).
8. **Open choices.** Two to four decisions for Theo and Claude, each with options and a recommendation. Diggers never decide.
9. **Judge Q&A.** Three questions a Citadel judge would ask and the answer the record supports.
10. **Grade.** A: reproduced and survives both windows. B: reproduced but single-window or descriptive. C: not reproduced or inherited. Only A and B become model inputs; C enters only as a labelled scenario or a footnote.

Digger rules: read-only on the repo except its own dossier file and receipt folder; repo first, web second and only public filings; no airbnb.com scraping; no credentials; never touch frozen folders; return the dossier as a file, not a chat answer.

## 6. The decision loop

Four waves, ordered by dependency:

| Wave | Lines |
|---|---|
| 1 | D1, D4, R1, C4, V2; mechanical D5, R3, V1 |
| 2 | D2, D3, D6, D7, R2, R4, R5, C1, C2, C3, C5, C6, E2 |
| 3 | R6, C7, C8, V3, V4, E1, E3, E4 |
| 4 | V5 |

Per wave: diggers launch in parallel in the background (at most eight in flight); each returned dossier is brought to Theo as a one-screen brief (number, chain in three lines, grade, strongest failure, open choices with a recommendation); Theo decides; the outcome is written to `docs/pitch-model-v2/DECISIONS.md` (line, chosen value, reason, options rejected, date) and to the spec.

Escape routes: a grade-C dossier or a disagreement goes back to the same digger as a targeted follow-up; a later reproduction that changes an earlier decided number reopens that line and the loop does not advance past it; a line that cannot reach grade B becomes a labelled scenario or footnote, recorded as such.

The workbook is regenerated after every wave. V5 is decided last, with the implied return by scenario in view.

## 7. The spec and the builder

**Spec.** `model/pitch_model_v2/spec/lines.yaml`, one entry per line: `id`, `label`, `unit`, `periods`, `kind` (`input` | `formula`), and provenance. An `input` carries `values` per scenario, `dossier`, `receipt`, `grade`, `decision`. A `formula` carries `expr` written only in line ids and periods (e.g. `D6[q] = D1[q] * D4_total[q]`). A line is never both. The loader refuses an input without grade A or B, and a formula that references an unknown id.

**Builder.** `analysis/src/pitch_model_v2/build.py` (Python 3.13, openpyxl) reads the spec and writes `model/pitch_model_v2/ABNB_pitch_model_v2.xlsx`. Every input cell gets an Excel defined name `<id>_<period>` (e.g. `D1_3Q26`). Every formula cell is a real Excel formula in those names, so trace-precedents works back to the inputs. One dropdown cell selects the scenario; inputs resolve through a lookup into a Scenario Data tab. After writing, the builder opens the file in the Excel installed on this Mac via AppleScript, forces a full calculation, and saves so cached values exist for viewers without a calc engine; `--no-recalc` skips this. Exit code 0 on success.

**Tabs.** Judge-facing: Cover, Drivers, Revenue and Guide, Costs and Earnings, Valuation and Call, 5 Nov Event Card, Street. Evidence layer: Evidence (one row per line: grade, chain, receipt, strongest failure), Decision Log (generated from `DECISIONS.md`), Scenario Data.

**QA.** `analysis/src/pitch_model_v2/qa.py` must pass before a build is accepted: zero formula-error cells; every input carries provenance and grade; every formula's names resolve; every input value ties to its receipt within the tolerance stated in the dossier; no licensed raw export embedded (single vendor-stamped consensus aggregates are allowed, as the repo already permits). The builder exits non-zero if QA fails.

## 8. Orchestration

This session is the brain and never digs. Diggers are subagents launched through the Agent tool with the model named in §4, running in the background, returning dossier files. They share the clone; after each wave the git diff is checked and any dossier whose agent wrote outside its own dossier file and receipt folder is refused. Follow-ups go to the same agent so it keeps its context. The workflow structured-output pitfalls recorded in memory apply: agents return files, not tightly constrained schemas.

## 9. Verification and acceptance

1. Each wave ends with `build.py` and `qa.py` green.
2. A tie-out table (`docs/pitch-model-v2/TIEOUT.md`) compares every model number to memo v3 and to the L4 workbook; every difference is explained in the decision log, or the memo is marked wrong.
3. Before V5, a fresh Opus reviewer that has read none of the dossiers receives the spec and attempts to break five lines of its choosing, in the repo's refuter pattern; findings go to the decision log.
4. The programme ends with a PR to `main` carrying `docs/revenue-forecast-strategy/05_backtests/PITCH_MODEL_v2_BUILD.md` (template in AGENT_BRIEF §7) and a WORKBOARD row. Workbook, spec, dossiers, receipts, and decision log are committed; licensed exports are not.

## 10. Schedule (estimate)

Wave 1 by day 2 (20 Sep), wave 2 by day 6 (24 Sep), wave 3 by day 9 (27 Sep), V5 with the adversarial review and PR by day 11 (29 Sep). Three days remain before 2 Oct for the memo to be cut against the model.

## 11. Open items carried into the plan

- Disk: 7 GB free on 18 Sep after installs. Theo decides whether to clear the ~13 GB of caches under `~/Library/Caches` and `~/.cache`.
- The OneDrive copy of untracked work runs with per-file timeouts and three passes; any file that fails all three is listed in the plan's first task and fetched by hand.
- Bloomberg MODL figures appear in memo v3; the model quotes them only as vendor-stamped aggregates, never as an export.
