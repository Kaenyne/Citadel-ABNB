# Margin build — file map

Every file this run produced, one line each. Written by WS32, 14 Sep 2026. Branch `krish/margin-build`,
worktree `C:\Users\krish\citadel-abnb-margins`. Interpreter for everything: **`py -3.13`** (the repo venv
`python` has only pandas and numpy on this machine — see `00_BRIEF.md`).

**Read in this order:** `../MORNING_REPORT.md` (ten minutes) → `../SYNTHESIS.md` (the model, the forecasts,
the card) → `../audit/AUDIT_RESPONSE.md` (what was withdrawn) → `21_red_team.md` (the honest ceiling) →
the method note you want to argue with.

---

## Top-level documents (`docs/margin-build/`)

| File | What it is |
|---|---|
| `00_BRIEF.md` | The shared brief every agent in the run read: where to work, output locations, Python, standards, what already existed on margins. |
| `MORNING_REPORT.md` | **Start here.** The ten-minute version for Krish: the view in eight lines, the model in a paragraph, the backtest table, alt data, cyclicality, the 5 Nov card, the audit, what to read next, decisions to make, the run log. |
| `SYNTHESIS.md` | The full write-up of the final model (WS23, post-audit): how it is built, the backtest evidence, the forecast set, cyclicality, the card, what failed, the alt-data verdict, open items, quotable statements with their evidence, the file map, and §11 — every number the audit moved. |
| `DISCUSSION.md` | The WS22 discussion round: three parallel agents answering the red team and the scoreboard, with an orchestrator digest at the top. Assembled from `discussion/group_{A,B,C}.md`. |
| `RUN_STATE.md` | The run ledger: stage table with status, and a reverse-chronological log of every launch, result, usage-limit pause, stall and relaunch. The single source of truth for continuing the run. |
| `discussion/group_A.md` | M1, M4, M6 answer the red team. Oracle specs withdrawn, step dummies gated, FY28 replaced, line wins re-scored against a drift baseline. |
| `discussion/group_B.md` | M2, M3 answer the red team. The `nov_sentence_pin` object, the withdrawn M3 LIVE numbers, the sentence-magnitude finding. |
| `discussion/group_C.md` | M5, M7 and the harness answer the red team. The clip-floor audit, the conformal recipe, the significance columns, the LIVE revenue-leg recommendation. |
| `audit/CODEX_ASTRA_AUDIT.md` | The external read-only audit (Codex / gpt-6-astra, WS30): 18 findings — 1 critical, 12 major, 5 minor — each with file:line, how it was verified, and a proposed fix. |
| `audit/AUDIT_RESPONSE.md` | WS31's triage table: every finding, the decision, what changed, which files, and the evidence. 17 fixed, 1 part-deferred, 0 rejected. |
| `audit/_codex_smoke.txt` | The `codex exec` smoke-test transcript from before the audit ran. |
| `prompts/*.md` | The prompt each workstream was launched with, one per workstream plus `M_common.md`. Kept so any result can be traced to the instruction that produced it. |

---

## Notes, one per workstream (`docs/margin-build/notes/`)

### Stage 1 — inputs

| Note | What it establishes |
|---|---|
| `01_input_census.md` | 123-row census of every repo input that could move a cost line, an add-back or a below-EBITDA item; 26 gaps with a pull route for each; the top unused inputs. Zero fitted parameters. |
| `02_financial_panel.md` | The financial panel every method reads: 34 quarters × 145 columns (1Q18–2Q26), annual 2018–25, 3,066 provenance rows. Adjusted EBITDA rebuilt from the lines within $0.97M on all 22 testable quarters. Corrects three repo panels on Q4 SBC. |
| `03_consensus_pit.md` | Daily point-in-time Street consensus 2021–2026 (EBITDA, margin, revenue, EPS, FCF, tax, capex) with last-revision dates; values stamped at 23 print/guide dates; the Street under-called margin in 21 of 22 prints. A proposed L0 append, never merged. |
| `04_alt_signals.md` | 58 external series, 1,146 screening tests. Two survivors: short rates → interest income (r 0.83, n 18) and a search-category share → marketing per night (r −0.64, n 18). Everything else fails. |
| `05_mgmt_statements_v2.md` | 377 dated management statements including 155 from 31 non-earnings events; the November guide-language rule (numeric floor → "approximately floor + 50bp"); the 5 Nov 2026 sentence prior. |
| `06_fy27_path_v2.md` | FY27 quarterly revenue path v2: PR #32's lap audited (8 findings, 2 high), re-based on the bridge v3 exit. Base $15,829M (+10.94%), bear $14,948M, bull $16,571M. |
| `06v_fy27_path_check.md` | Independent re-derivation of 06 before reading it: PASS WITH CORRECTIONS. Independent FY27 $15,797M, $32M apart; one medium fix (3Q26 bear/bull were the base in all scenarios) delivered as `_v2b`. |
| `10_harness_margin.md` | The margin harness: targets panel, seven baselines × 14 W1 / 10 W2 guide dates, recency-weighted scorer, registry writer. Imports the frozen FORMAT 1.0 calendar and validator. Seasonal-naive MAE 2.24pp; the Street is the hardest baseline at 1.59pp. |

### Stage 2 — methods (each registers objects into the margin registry)

| Note | Registry method | Verdict |
|---|---|---|
| `M1_driver_lines.md` | `driver-lines` | **Negative result.** Both pass lines failed; building margin from driver-based cost lines is a tie with last year's margin. Cost of revenue (elasticity 0.81 on GBV) is the one survivor. `d_steps_rw` is not point-in-time and is on the kill list. |
| `M2_margin_ts.md` | `margin-ts` | **Negative result.** No object built from Airbnb's own history beats last year's margin by a distinguishable amount; the best has t = −0.22. Its SARIMA LIVE 3Q26 of 51.50% is disowned by its own author. |
| `M3_guide_policy_margin.md` | `guide-policy-margin` | **Partial.** The main spec and the FY cushion failed; the registered LIVE 4Q26 34.51% / FY26 37.03% is withdrawn and stamped NOT QUOTABLE. What survives: the allocation rule (`m[q−4] + delta`), the November sentence rule, and the budget identity. |
| `M4_alt_augmented.md` | `alt-augmented` | **Negative result, best methodology in the run.** 50 pre-registered point-in-time tests under a `knowable_from` gate, 47 leakage placebos, a 1,000-draw random-series false-positive rate. One survivor, indistinguishable from noise. |
| `M5_street_bias.md` | `street-bias` | **The accuracy of the build.** The dollar flow-through object is the only one that beats the Street at p < 0.05. Its margin claim and its dispersion slope of +28.3 are withdrawn; every h=1 correction is worse than doing nothing. |
| `M6_cycle_flex.md` | `cycle-flex` | **Partial — a measurement, not a forecaster.** The forecaster is a tie and fails beyond h=0; FY28 31.3% is withdrawn and the FY26 floor-cushion claim restated. What survives: the cost elasticities, the asymmetry, the peer table, the scenario engine. |
| `M7_below_ebitda.md` | `below-ebitda` | **Partial.** Interest income is the one genuine edge below the line. Quarterly free cash flow fails and must not be quoted; the self-reported tax under-coverage is withdrawn. The EPS bridge reproduces the Street's own number from the Street's own EBITDA. |

### Stage 3 — adjudication and the final model

| Note | What it is |
|---|---|
| `20_scoreboard.md` | The overseer: every method and baseline ranked, both windows, both weightings, coverage, parameter counts, error correlations. Oracle specs excluded by rule. There are only about three independent views in the whole build. 13 numbered open questions. |
| `21_red_team.md` | The adversarial pass: 27 findings (2 critical, 14 major) across 10 reproducible checks. All 8 mechanical point-in-time rules pass on 32 registry files / 87,628 rows — but `survives_both_windows` is ~30% free at this n, and no method built from Airbnb's own history beats the naive at any conventional level. A 9-item kill-list addendum. |
| `23_triangulate.md` | The procedural record for the final model (the readable version is `../SYNTHESIS.md`): what ran, the exact commands, the tables with n, what failed, the parameter count, and an appended "Audit response" section describing the code-level fixes. |
| `README.md` | This file. |

---

## Scripts (`analysis/src/margin_build/<slug>/`)

Every folder has a `run.py` that rebuilds its package end to end (exit 0) and a `README.md` with the command.

| Folder | What it builds |
|---|---|
| `01_input_census/` | The census CSVs and the gap list. |
| `02_financial_panel/` | The quarterly and annual panels, provenance, seasonality, reconciliation, macro episodes, letter vintages (`panel_lib.py` holds the parsers; `figures.py` the charts). |
| `03_consensus_pit/` | The LSEG pull, the Bloomberg parse, the point-in-time consensus panel and the surprise history. |
| `04_alt_signals/` | The external pulls, the signal catalogue, the `knowable_from` table and the 1,146-test grid. |
| `05_mgmt_statements_v2/` | The statement extraction, the guide-language pattern and the November 2026 scenario table. |
| `06_fy27_path_v2/` | The FY27 quarterly revenue path (`fig.py` for the chart). |
| `06v_fy27_path_check/` | The independent re-derivation and the `_v2b` corrections. |
| `10_harness_margin/` | **The margin harness.** Targets, the point-in-time slice, seven baselines, the recency-weighted scorer (`score.py`), the registry validator. Its `README.md` is the API document. |
| `M1_driver_lines/` … `M7_below_ebitda/` | One folder per method; each registers its objects and shells out to `score.py` at the end. |
| `20_scoreboard/` | The ranking tables and the `run.py` status board. |
| `21_red_team/` | `checks/check_01`…`check_10`, each independently reproducible. |
| `22_discussion_group_A/` | The re-scoring scripts written during the discussion round (`repro_drift.py`, `repro_skill.py`). |
| `23_final_model/` | **The final model.** `prereg.json` (the pass line, fixed before any result), `combine.py`, `diagnostics.py`, `forecast.py`, `workbook.py`, `run.py`. |

**Two commands matter, and they must never run concurrently** (method packages invoke `score.py` internally):

```bash
py -3.13 analysis/src/margin_build/23_final_model/run.py     # ~4 min, exit 0, ends by calling score.py
py -3.13 analysis/src/margin_build/20_scoreboard/run.py      # ~60 s, exit 0
```

Read-only replay, writes nothing and prints a per-file diff:
`MARGIN_VERIFY_ONLY=1 py -3.13 analysis/src/margin_build/23_final_model/run.py`.

---

## Data (`data/processed/margin_build/<slug>/`)

| Folder | What is in it |
|---|---|
| `01_input_census/` | `01_input_census.csv` (123), `01_gaps.csv` (26), summary by line. |
| `02_financial_panel/` | `02_panel_quarterly.csv` (34 × 145), `02_panel_annual.csv`, provenance, seasonality, reconciliation, macro episodes, letter vintages, build log. |
| `03_consensus_pit/` | `03_consensus_at_dates.csv` (241 stamped rows), the surprise history, `03_L0_append_candidates.csv` (proposed, never merged). Raw LSEG stays in `data/raw/` — licensed. |
| `04_alt_signals/` | `04_signal_catalogue.csv`, `04_signal_panel_quarterly.csv`, `04_signal_knowable_from.csv`, `04_signal_tests.csv`, parsed review/app-store files. |
| `05_mgmt_statements_v2/` | `05_statements.csv` (377), `05_guide_language_pattern.csv` (20 prints), `05_nov2026_scenarios.csv` (45), FY27 hints, reliability by line and by event. |
| `06_fy27_path_v2/` | The FY27 quarterly revenue path, including `06_revenue_path_3q26_4q27_v2b.csv` — the file the margin model reads. |
| `06v_fy27_path_check/` | The independent path and the difference ledger. |
| `10_harness_margin/` | `targets.csv`, `revenue_leg_pit.csv`, **`scoreboard_margin.csv`** (the league table every claim is checked against), `scoreboard_by_quarter.csv`. |
| `M1_driver_lines/` … `M7_below_ebitda/` | Each method's fits, forecasts by vintage, live tables, diagnostics, and its `_pre_discussion/` backup. Notable: `M6_cycle_flex_k_table.csv` and `M6_cycle_flex_peer_k.csv` (the elasticities), `M5_discussion_*` (the clip audit), `M7_parameter_sheet.csv` (the below-EBITDA parameters). |
| `20_scoreboard/` | The ranking tables, the excluded-oracle list, `20_runpy_status.csv`. |
| `21_red_team/` | `21_findings.csv` (27 rows) and each check's output. |
| `23_final_model/` | **The adopted numbers.** `23_forecast_quarterly.csv`, `23_forecast_annual.csv`, `23_lines_quarterly.csv`, `23_card_5nov.csv`, `23_card_budget_identity.csv`, `23_vs_consensus.csv`, `23_bands.csv`, `23_conformal.csv`, `23_seasonality.csv`, `23_macro_sensitivity.csv`, `23_fy26_floor_breakeven.csv`, `23_scenarios.csv`, `23_path_rule.csv`, the combination files, the four `23_diag_*` diagnostics, and the three `23_dollar_from_margin_*` files added by the audit. Pre-audit copies of every file whose numbers moved are in `_pre_audit/`. |
| `registry/` | The FORMAT 1.0 registry, one CSV per method-object. The two that carry the adopted forecast: `final-margin__combined.csv` (1,152 rows) and `final-margin__combined_dollar_from_margin.csv` (576 rows). `*_pre_discussion.csv.bak` and `*_pre_audit.csv.bak` are the backups. |

---

## Everything else

| Path | What it is |
|---|---|
| `model/ABNB_margin_model.xlsx` | The workbook: README, Inputs, Lines, Bridge, Scenarios, Consensus, Seasonality, Weights, Card. **Labelled a frozen report generated from the CSVs**, not an input-driven model (audit finding 16). `ABNB_margin_model_pre_audit.xlsx` is the pre-audit copy. |
| `analysis/figures/margin_build/*.png` | 24 figures, prefixed by slug: the panel's seasonality and cost-per-night charts, the consensus revision paths and FY-floor chart, the FY27 path, and one or more per method. |
| `data/manifests/margin_build/*.csv` | Committed manifests (URL, UTC timestamp, sha256) for every raw pull: WS02 EDGAR filings, WS03 consensus, WS04 signals, WS05 filings and transcripts, WS06, M6's licensed peer inputs, M7's FRED series. |
| `data/raw/margin_build/<slug>/` | The raw pulls themselves — **gitignored, never committed**. Licensed material (LSEG, Bloomberg, Third Bridge) never leaves `data/raw`. |
| `docs/explainers/margin_build_2026-09-14.html` | The shareable explainer page: the model in plain words, the forecast tables, inline-SVG seasonal and cycle charts drawn from the CSVs, the consensus gap, the audit summary. |
| `docs/revenue-forecast-strategy/WORKBOARD.md` | Carries the appended margin-build rows and the "Done (14 Sep 2026)" block. |

---

## Four rules for anyone picking this up

1. **Never run two method packages at once.** They each shell out to `score.py`; the run lost twelve minutes to
   exactly this collision on 14 Sep. Use `MARGIN_SKIP_SCORE=1` if you must run one without re-scoring.
2. **Quote nothing from the kill list.** `AGENT_BRIEF.md` §6 plus the WS21 addendum plus WS22's, consolidated at
   the end of `../SYNTHESIS.md` §9. The most recently added items are the 0.77 beat probability, the
   $2,299–2,499M band, "attained coverage 82–91%", and "Airbnb has no cost dial".
3. **Every margin ratio carries its p-value and its quarters-better count.** "Survives both windows" alone is
   about 30% free at this n and is retired from the run's language.
4. **h=0 is the only horizon with an edge.** Everything from 4Q26 onward is the Street, a guide identity, or a
   labelled scenario. The pitch should say that out loud.
