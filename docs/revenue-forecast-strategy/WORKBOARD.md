# WORKBOARD — claim before you start, update when you stop

External contributors: the paste-ready prompt for each WP is in `docs/thesis-kernel-topdown/prompts/`; setup in `02_SETUP.md`.

One row per work package (IDs and specs in `AGENT_BRIEF.md` §5). To claim: set `status=claimed`, put your
session/agent name and branch, commit the board on your branch (or just save it if you are on Theo's machine).
If a package is `claimed` or `in-progress` by someone else, pick another or coordinate — never work the same
package in parallel. When done: `status=done`, link the note, re-run `harness/score.py` if you registered anything.

Status values: `open` · `claimed` · `in-progress` · `blocked (reason)` · `done` · `human (needs a person)`

| WP | Title | Lane | Status | Owner / agent | Branch | Started | Last update | Output |
|---|---|---|---|---|---|---|---|---|
| WP-X | Regional kernel + origin–destination FX exposure matrix (R-engine `exposure.csv`); regional recompute of the FX carried through the kernel — supersedes the consolidated basket | Krish (O–D travel analysis) | done (underpowered; B4 retained) | Codex / Lane 1 parent | codex/lane1-full | 2026-09-12 | 2026-09-13 | [X regional FX](05_backtests/X_REGIONAL_KERNEL_OD_FX.md) |
| WP-R | Regional refresh using public arrivals and regional revenue inputs | Krish | done (partial; 0/3 headline survives) | Codex / Lane 1 parent | codex/lane1-full | 2026-09-12 | 2026-09-13 | [R regional refresh](05_backtests/R_REGIONAL_REFRESH.md) |
| WP-K0 | Kernel engine module `kernel_engine_v2/` (PIT λ, kernel guide, term structure, control chart) — spine for Lane 1 | Krish | done (v2 Gate 1 passed) | Codex / Lane 1 parent | codex/lane1-full | 2026-09-12 | 2026-09-13 | [K0 v2](05_backtests/K0_KERNEL_ENGINE_v2.md) |
| WP-V | Valuation reconciliation page for decision WP-H (+0.48 turns/pt → FY27 band → price band vs football field vs branch analogues) | Krish | done (partial) | Codex / Lane 1 parent | codex/lane1-full | 2026-09-12 | 2026-09-13 | [V reconciliation](05_backtests/V_VALUATION_RECONCILIATION.md) |
| WP-H | Direction + target reconciliation (football field vs branch analogues; adopt ex-NA lap?) | all | **human** | Theo · Krish · Jessie | — | — | 2026-09-11 | one line in the card + `05_backtests/H_DIRECTION_DECISION.md` |
| WP-G0 | LSEG Workspace self-registration via UF | Theo | **human** | Theo | — | — | 2026-09-11 | login works at workspace.refinitiv.com/web |
| WP-G1 | LSEG estimates history export → vintage register (ABNB, NCLH, BKNG, EXPE) | Theo | blocked (WP-G0) | — | — | — | 2026-09-11 | `L0/consensus_history_loader.py` run; register rows |
| WP-A | Thesis A backtest — kernel guide vs Street at 14 guide dates, executable returns | Krish | done (underpowered; Gate 2 clean) | Codex / Lane 1 parent | codex/lane1-full | 2026-09-12 | 2026-09-13 | [A guide surprise](05_backtests/ALPHA_A_GUIDE_SURPRISE.md) |
| WP-F | Wire RNPL as a variable (u, L, re-based nights, λ chart, funds-payable score line) + FX-confound check | Theo | open | — | — | — | 2026-09-11 | `rnpl_v2/`, `05_backtests/ALPHA_F_RNPL.md` |
| WP-E1 | Thesis E — NCLH advance-ticket-sales kernel | Jessie | open | — | — | — | 2026-09-11 | `05_backtests/ALPHA_E_NCLH.md` |
| WP-B | Thesis B′ — kernel term structure vs FY-guide revisions (free-data variant; FY consensus after WP-G1) | Krish | done (underpowered) | Codex / Lane 1 parent | codex/lane1-full | 2026-09-12 | 2026-09-13 | [B term structure](05_backtests/ALPHA_B_TERM_STRUCTURE.md) |
| WP-C1 | Calendar pickup ≤ 90 days from consecutive Inside Airbnb dumps → booked-GBV feature | Theo | blocked (September dumps, mid/late Sep) | — | — | — | 2026-09-11 | `pickup_v1/`, `05_backtests/ALPHA_C1_PICKUP.md` |
| WP-C2 | Macro / arrivals pulls (NTTO, Eurostat, JNTO, INE, DATATUR, ISTAT, STR weekly, CPI) → covariates | Theo | open | — | — | — | 2026-09-11 | `data/processed/forecast_methods/macro_pulls/` + manifest |
| WP-C3 | Retarget the 598 alt-data features + stays index at booked GBV and at the residual R | Krish | done (underpowered; no promotions) | Codex / Lane 1 parent | codex/lane1-full | 2026-09-12 | 2026-09-13 | [C3 feature screen](05_backtests/ALPHA_C3_GBV_FEATURES.md) |
| WP-D | λ control chart + backlog split into the pre-registration card (items F1–F4) | Krish | done (partial; 2/5 rows scoreable) | Codex / Lane 1 parent | codex/lane1-full | 2026-09-12 | 2026-09-13 | [D card addendum](05_backtests/D_CARD_ADDENDUM_LAMBDA.md) |
| WP-E2 | Thesis E — BKNG / EXPE deferred merchant bookings kernel | Jessie | open (after E1) | — | — | — | 2026-09-11 | `05_backtests/ALPHA_E_OTA.md` |
| WP-I | Memo v1 (direction committed, kernel → composition → flip rule; one chart, one table) | Writer | blocked (WP-H) | — | — | — | 2026-09-11 | `deck/drafts/memo_v1.md` |
| WP-J | Re-score + refresh `SCOREBOARD_v3.md` after new registrations; verify loop | any | open (recurring) | — | — | — | 2026-09-11 | `05_backtests/SCOREBOARD_v3.md` |
| FXSWAP | H1/H2 bridge FX lines swapped to the adopted estimators (ADR v3 midpoint for ADR FX; fx_lag_v2 kernel +1.0pp for 4Q26 revenue FX); rejected constructions kept as comparison columns | Krish | done | Krish (Claude) | krish/fx-line-swap | 2026-09-12 | 2026-09-12 | `analysis/src/h1_to_h2_bridge_v2.py`, `data/processed/h2_bridge_v2/`, `05_backtests/FXSWAP_h2_bridge_kernel_fx.md` |
| REBASE | H1/H2 bridge v3: nights and ex-FX ADR re-based to the team baseline (9.9% / 8.1%) and the ADR v3 card (3.9% / 4.1%); card reproduced to $0.02bn; 4Q26 GBV-lag revenue $3,178M, implied guide mid $3,059M | Krish | done | Krish (Claude) | krish/fx-line-swap | 2026-09-12 | 2026-09-12 | `analysis/src/h1_to_h2_bridge_v3.py`, `data/processed/h2_bridge_v3/`, `05_backtests/REBASE_h2_bridge_v3_nights_adr.md` |
| WP-K | Ingest the September Inside Airbnb batch (+ unlisted Aug 2026 batch, 86 markets); refresh reviews index and party-size series | Theo | blocked (batch not out) | — | — | — | 2026-09-11 | manifests; refreshed E / I outputs |
| WP-L | Airbnb policy monitor (RNPL, fees, cancellation) — weekly fetch + diff, dated log | Theo | open (small) | — | — | — | 2026-09-11 | `data/manifests/policy_monitor.log` |
| WP-M | Consensus re-stamp weekly + 2–3 Nov (Zacks nights/ADR/GBV) | Theo | open (recurring) | — | — | — | 2026-09-11 | vintage register rows |
| WP-N | Fee-panel runs 14/16/18 Sep — measure panel overlap on 16 Sep; θ DiD after 18 Sep | Jessie | scheduled (launchd) | — | — | — | 2026-09-11 | `05_backtests/N_THETA_DID.md` |
| WP-O | ToS decisions: fee-inclusive quote route; Experiences/Services counts scrape; AirDNA purchase | all | **human** | team | — | — | 2026-09-11 | decision logged here |
| WP-P | Card freeze ABNB-INT-v1 (26 Sep) and 5 Nov score sheet | Writer | blocked (WP-H, WP-F, WP-A) | — | — | — | 2026-09-11 | `PREREG_ABNB-INT-v1.md` signed |

## Done (11 Sep 2026)

| WP | What | Note |
|---|---|---|
| A1 | Consensus stamped, all vendors, vintage register 127 → 167 rows | `05_backtests/A1_consensus_vintages.md` |
| A2 | Inside Airbnb daily capture live (360/360 files, launchd 06:00) | `05_backtests/A2_ia_capture.md` |
| A3 | Fee-deadline panels: dates sourced (S66–S71), 2,600-listing sample, dry run, launchd | `05_backtests/A3_fee_panels.md` |
| B1 | 3Q26 take rate reconciled: 18.14 %, sd 0.46, P(≥ 18.10) 0.53 | `05_backtests/B1_TAKE_RATE_RECONCILIATION.md` |
| B2 | Q4 guide as a distribution: $3,161M (80 % 3,012–3,312); P(below) 0.49 / 0.50 / 0.63 | `05_backtests/B2_Q4_GUIDE_EXHIBIT.md` |
| B3 | FY27 decomposition rebuilt multiplicatively; band +9.18–11.52 %; exploratory | `05_backtests/B3_FY27_DECOMPOSITION.md` |
| B4 | FX exhibit: 4Q26 +1.0pp (CS +0.3–2.2); observed-share triple; four-way table | `05_backtests/B4_FX_EXHIBIT.md` |
| C1 | Pre-registration card v1 with the 11 team decisions | `05_backtests/PREREG_ABNB-INT-v1.md` |
| C2 | Memo v0 (1,153 words) + exhibits; thesis draft | `deck/drafts/memo_v0_2026-09-11.md` |
| D1 | Scoreboard v2 narrative; hand-off message | `05_backtests/SCOREBOARD_v2.md`, `HANDOFF_MESSAGE_2026-09-11.md` |
| K1 | Kernel weights from the ledger; paid/unpaid/not-booked split; RNPL leakage; conditional ranges | `05_backtests/K1_KERNEL_WEIGHTS_AND_BACKLOG.md` |
| K2 | Kernel weights from booking lead times (Melbourne STR 2014–17) | `05_backtests/K2_KERNEL_FROM_LEAD_TIMES.md` |

## Margin build run (13–14 Sep 2026) — branch `krish/margin-build`

Appended by WS32, 14 Sep 2026. Twenty-two workstreams, all `done`. Worktree `C:\Users\krish\citadel-abnb-margins`,
cut from `origin/main` at `fd4272f`. Shared brief `docs/margin-build/00_BRIEF.md`; run ledger
`docs/margin-build/RUN_STATE.md`; read `docs/margin-build/MORNING_REPORT.md` first, then `SYNTHESIS.md`.
Notes are under `docs/margin-build/notes/` (file map in `notes/README.md`). **Rows below are new; no existing row was edited.**

| WP | Title | Lane | Status | Owner / agent | Branch | Started | Last update | Output |
|---|---|---|---|---|---|---|---|---|
| MB-01 | Repo census of every input that could move a cost line, an add-back or a below-EBITDA item (123 rows, 26 gaps) | Krish (margin) | done | WS01 (Claude) | krish/margin-build | 2026-09-13 | 2026-09-14 | `docs/margin-build/notes/01_input_census.md` |
| MB-02 | Financial panel: 34 quarters × 145 columns, 3,066 provenance rows; adj EBITDA rebuilt within $0.97M on all 22 quarters | Krish (margin) | done | WS02 (Claude) | krish/margin-build | 2026-09-13 | 2026-09-14 | `docs/margin-build/notes/02_financial_panel.md` |
| MB-03 | Point-in-time consensus for EBITDA / margin / EPS / FCF, daily 2021–2026, 22 of 22 prints stamped (LSEG + Bloomberg) | Krish (margin) | done | WS03 (Claude) | krish/margin-build | 2026-09-13 | 2026-09-14 | `docs/margin-build/notes/03_consensus_pit.md` |
| MB-04 | External / alt-data signal screen for every cost line: 58 series, 1,146 tests, 2 survivors | Krish (margin) | done | WS04 (Claude) | krish/margin-build | 2026-09-13 | 2026-09-14 | `docs/margin-build/notes/04_alt_signals.md` |
| MB-05 | Management margin statements v2 (377 statements, 31 non-earnings events) and the November guide-language rule | Krish (margin) | done | WS05 (Claude) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/notes/05_mgmt_statements_v2.md` |
| MB-06 | FY27 quarterly revenue path v2: PR #32 lap audited, re-based on the bridge v3 exit; FY27 base $15,829M | Krish (margin) | done | WS06 (Claude) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/notes/06_fy27_path_v2.md` |
| MB-06v | Independent check of MB-06 (arithmetic, PIT, reconciliation): PASS WITH CORRECTIONS; 3Q26 bear/bull fixed as `_v2b` | Krish (margin) | done | WS06v (Claude) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/notes/06v_fy27_path_check.md` |
| MB-10 | Margin harness: targets panel, 7 baselines × 14/10 guide dates, recency-weighted scorer, registry (imports the frozen FORMAT 1.0 calendar and validator) | Krish (margin) | done | WS10 (Claude) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/notes/10_harness_margin.md` |
| MB-M1 | Driver-based cost lines v2 (per-unit costs on nights, GBV, ADR, mix, FX), PIT refits — both pass lines FAIL; cost of revenue survives | Krish (margin) | done (negative result) | M1 (Claude) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/notes/M1_driver_lines.md` |
| MB-M2 | Time-series and ratio methods for margin (seasonal, incremental, % of revenue, SARIMA, sentence rule) — nothing beats last year's margin distinguishably | Krish (margin) | done (negative result) | M2 (Claude) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/notes/M2_margin_ts.md` |
| MB-M3 | Guidance-policy model: FY guide as a budget constraint, Q4-implied margin, November language rule — allocation and budget identity survive; LIVE 4Q26 34.51% withdrawn | Krish (margin) | done (partial) | M3 (Claude) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/notes/M3_guide_policy_margin.md` |
| MB-M4 | Alt-data-augmented line model: 50 pre-registered PIT tests, 1 survivor inside its own placebo rate; alt data does not improve the margin call | Krish (margin) | done (negative result) | M4 (Claude) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/notes/M4_alt_augmented.md` |
| MB-M5 | Consensus-anchored model: Street EBITDA plus systematic bias and revenue-surprise flow-through — the one object that beats the Street at p<0.05 | Krish (margin) | done | M5 (Claude) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/notes/M5_street_bias.md` |
| MB-M6 | Cycle and cost-flex model: cost elasticities to revenue, asymmetry, peer table, scenario engine — measurement survives, the forecaster is a tie | Krish (margin) | done (partial) | M6 (Claude) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/notes/M6_cycle_flex.md` |
| MB-M7 | Below-EBITDA bridge (SBC, D&A, interest income, tax, share count, EPS) and the FCF bridge — interest income is the one edge; quarterly FCF fails | Krish (margin) | done (partial) | M7 (Claude) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/notes/M7_below_ebitda.md` |
| MB-20 | Scoreboard: every method and baseline, both windows, both weightings, coverage, parameter counts, error correlations | Krish (margin) | done | WS20 (Claude) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/notes/20_scoreboard.md` |
| MB-21 | Red team: leakage / PIT audit, overfitting, kill-list compliance — 27 findings (2 critical, 14 major); `survives_both_windows` is ~30% free at this n | Krish (margin) | done | WS21 (Claude) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/notes/21_red_team.md` |
| MB-22 | Discussion round: three parallel agents answer the red team and the scoreboard; methods re-registered, oracle specs removed | Krish (margin) | done | WS22 A/B/C (Claude) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/DISCUSSION.md` |
| MB-23 | Triangulation: the final combined model, quarterly 3Q26–4Q27 + FY28, vs consensus and management, cyclicality, scenarios, workbook | Krish (margin) | done | WS23 (Claude) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/SYNTHESIS.md`, `notes/23_triangulate.md` |
| MB-30 | External read-only audit of the final model (Codex / gpt-6-astra): 18 findings, 1 critical | Krish (margin) | done | WS30 (Codex) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/audit/CODEX_ASTRA_AUDIT.md` |
| MB-31 | Apply the audit: triage, fix, re-run, re-score — 17 fixed, 1 part-deferred, 0 rejected; h=0 unchanged, every verdict survives | Krish (margin) | done | WS31 (Claude) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/audit/AUDIT_RESPONSE.md`, `SYNTHESIS.md` §11 |
| MB-32 | Morning report, explainer page, workboard rows, note file map | Krish (margin) | done | WS32 (Claude) | krish/margin-build | 2026-09-14 | 2026-09-14 | `docs/margin-build/MORNING_REPORT.md`, `docs/explainers/margin_build_2026-09-14.html`, `docs/margin-build/notes/README.md` |

**Open items handed on from this run** (detail in `MORNING_REPORT.md` §i and `SYNTHESIS.md` §8):
(1) the WS22 group C `revenue_leg_live.csv` harness patch is unwritten, so every LIVE dollar row outside WS23 still
sits on the harness naive leg (4Q26 $3,237M vs bridge v3's $3,178M); (2) WS31b's forward profiles put 4Q26 margin
at 24.7–25.9%, 3–4pp below every method here and below the Street, and are still the incumbent repo margin model —
reconcile or retire; (3) there is no 4Q26 object with an edge, and the trade into 5 Nov is structurally an h=1
position; (4) the mechanical residual allocation gives 3Q26 G&A +9.4% y/y against a 1H26 actual of −5.4%;
(5) `SYNTHESIS.md` §3 still carries a pre-audit FY27 S&M of $3,740M / 23.6% — the post-audit CSV says $3,721M / 23.5%.

## Done (14 Sep 2026)

| WP | What | Note |
|---|---|---|
| MB-A | Margin model built and registered: `final-margin\|combined\|stack_clip`, six members plus a zero-parameter management-sentence clip; h=0 MAE 1.126pp (W1, n 14) / 0.788pp (W2, n 10) — 0.50x / 0.40x the seasonal naive, 0.71x / 0.60x the Street, sign p 0.0032 / 0.011 | `docs/margin-build/SYNTHESIS.md` §1–2 |
| MB-B | Adopted dollar object `final-margin\|combined_dollar_from_margin` registered and calibrated in its own right: MAE $30.7M / $25.8M, better than the Street in **14 of 14 and 10 of 10** quarters (sign p 0.0001 / 0.0010) | `SYNTHESIS.md` §2; `23_dollar_from_margin_scores.csv` |
| MB-C | 3Q26 card: margin **49.94%**, adj EBITDA **$2,399M** (80% band $2,337–2,462M, P(beat) **0.779**), EPS **$2.88** (band $2.70–3.05) against Street 49.78% / $2,361.5M / $2.845 | `23_card_5nov.csv` |
| MB-D | 4Q26 quoted from the **Street** (28.90% / $918M): the combination loses to it at h=1 by 19–28% in both windows and the pre-registered consequence was applied; guide path 29.90% | `SYNTHESIS.md` §3; `23_path_rule.csv` |
| MB-E | FY26 **35.73% / $5,098M**, +0.23pp over the "at least 35.5%" floor; the floor breaks on a 2H26 revenue miss of only 0.63% held / 0.94% flexed ($50–75M) | `23_forecast_annual.csv`; `23_fy26_floor_breakeven.csv` |
| MB-F | 5 Nov guide sentence forecast **"approximately 36%"** (numeric floor + 50bp, exact 2 of 2); at our 3Q26 that needs a 4Q26 of **30.12%** against a Street 28.90%. Budget identity: 1pp of FY26 = 4.49pp of 4Q26 | `23_card_budget_identity.csv`; `05_nov2026_scenarios.csv` |
| MB-G | FY27 **scenario** 34.64% / $5,483M against Street 36.45% / $5,766M; incremental margin **24.7% vs 43.7%**, entirely sales & marketing at 23.5% of revenue | `23_forecast_annual.csv`; `23_lines_quarterly.csv` |
| MB-H | Alt data: 58 series / 1,146 screens and 50 pre-registered PIT tests produce **no usable margin signal**; the keepers are a calibrated false-positive prior (2.5–22.5% per pass line) and the "good lines do not make a good margin" mechanism | `notes/04_alt_signals.md`; `notes/M4_alt_augmented.md` |
| MB-I | Cyclicality: seasonality is mechanical (a revenue denominator, not a cost decision); opex elasticity to revenue is **imprecise, not zero** (k 0.14, t 0.47, n 18, 95% CI −0.44 to +0.72); the model uses cash-cost k 0.364, asymmetric | `23_seasonality.csv`; `23_macro_sensitivity.csv`; `M6_cycle_flex_peer_k.csv` |
| MB-J | External audit closed: 18 findings, 17 fixed, 1 part-deferred, **0 rejected**; the critical print-date gate fixed and replayed with h=0 unchanged and every verdict surviving; the 0.77 beat probability and the $2,299–2,499M band withdrawn | `audit/AUDIT_RESPONSE.md`; `SYNTHESIS.md` §11 |
| MB-K | Workbook `model/ABNB_margin_model.xlsx` (9 sheets), labelled a frozen report generated from the CSVs; `MARGIN_VERIFY_ONLY=1` gives a no-write replay with a per-file diff | `analysis/src/margin_build/23_final_model/README.md` |
| MB-L | Morning report, explainer page and note file map | `docs/margin-build/MORNING_REPORT.md`; `docs/explainers/margin_build_2026-09-14.html` |

| 40 | Margin line build by cost item (fees % GBV, chargebacks, hosting + AI step, support per booking, marketing vs field, G&A ex reserves) with base, scenarios and the short case (lap + RNPL); supersedes WS31b profile and the run allocated lines for pitch use | Krish | done | Krish (Claude) | krish/margin-build | 2026-09-15 | 2026-09-15 | `analysis/src/margin_build/40_line_build/`, `data/processed/margin_build/40_line_build/`, `notes/40_line_build.md`, `model/ABNB_margin_line_build.xlsx` |
| 40-TR | Take rate view for the margin build (10bp on FY27 GBV = ~$115M revenue, ~0.7pp margin at fixed cost) | Theo | open | - | - | - | 2026-09-15 | revenue path take-rate line; line build re-run |
