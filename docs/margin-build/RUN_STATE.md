# Margin build run: state ledger and continuation instructions

Owner: Krish (asleep from ~00:00 14 Sep 2026). Orchestrator: Claude Code (Fable 5.1) session in the main tree, working in
`C:\Users\krish\citadel-abnb-margins` (branch `krish/margin-build`). This file is the single source of truth for continuing
the run after a usage-limit pause, a crash, or a new session. Update the status table whenever a stage changes.

## How to continue (any orchestrator, any session)

1. Read `docs/margin-build/00_BRIEF.md` and this file. Then `ListAgents` to see what is still running.
2. For each workstream below with status not `done`: if its note `docs/margin-build/notes/<NN_slug>.md` exists and ends with a
   "For the model" section, mark it `done`. Otherwise, if no agent is running on it (ListAgents; or file mtimes under
   `data/processed/margin_build/<NN_slug>/` older than 40 min), relaunch it with `Agent` (subagent_type general-purpose,
   **model opus** (Krish's instruction 14 Sep 14:45, after the Fable limit; the table's model column is superseded)) using its prompt file `docs/margin-build/prompts/<NN>_*.md`, prefixed with
   `RESUME: check your output folder first and continue from what is on disk.` Pass the prompt file's full text as the prompt.
3. **Concurrency cap: at most 4 subagents running at once.** Respect stage order and the dependencies column.
4. After every stage completes: `git add` the margin_build folders (`docs/margin-build`, `analysis/src/margin_build`,
   `data/processed/margin_build`, `data/manifests/margin_build`, `analysis/figures/margin_build`, `model/ABNB_margin_model*.xlsx`)
   and commit on the branch with a message naming the stage. Verify nothing licensed is staged (`git diff --cached --stat`; no `data/raw`,
   nothing matching `*bloomberg*`, `*factset*`, `lseg`). Do not push until stage 4 is done.
5. Stage 4 (Codex audit) runs `codex exec` read-only from the worktree with `docs/margin-build/prompts/30_codex_audit.md`
   (see that file for the exact command); output `docs/margin-build/audit/CODEX_ASTRA_AUDIT.md`. Then 31 applies fixes, then 32 writes
   the morning report, updates `docs/revenue-forecast-strategy/WORKBOARD.md` (append rows only), commits, pushes, opens a draft PR.
6. Never run `git checkout`, `merge`, `stash`, `reset` here, and never touch `C:\Users\krish\citadel-abnb` or other worktrees.
7. A heartbeat cron in the orchestrator session fires every 30 minutes with the instruction to read this file and act on steps 2-5.

Manual restart if the session is gone: open a terminal in `C:\Users\krish\citadel-abnb` (main tree), run `claude`, and paste:
"Continue the margin build run per C:\Users\krish\citadel-abnb-margins\docs\margin-build\RUN_STATE.md. Fable subagents, max 4 concurrent."

## Stages and status (update in place)

Status values: `pending`, `running`, `done`, `failed`, `skipped`.

| WS | Topic | Model | Depends on | Status | Launched | Note path | Last update |
|---|---|---|---|---|---|---|---|
| 01 | Repo census of margin-relevant inputs | fable | - | done | 23:55 | notes/01_input_census.md | 00:15 |
| 02 | Financial panel: every P&L, add-back, below-EBITDA and FCF line, quarterly and annual, with seasonality | fable | - | done | 23:55 | notes/02_financial_panel.md | 04:50 |
| 03 | Point-in-time consensus for EBITDA/EPS/FCF/cost lines (LSEG + Bloomberg), surprise history | fable | - | done | 23:55 | notes/03_consensus_pit.md | 00:20 |
| 04 | External / alt-data signals for each cost line (archives, third-party public, macro) | fable | - | done | 23:55 | notes/04_alt_signals.md | 00:35 |
| 05 | Management statements v2 (all events incl. conferences) and 5 Nov guide-language pattern | fable | - | done | 00:15 | notes/05_mgmt_statements_v2.md | 04:30 |
| 06 | FY27 quarterly revenue path v2: audit and fix PR #32 lap on real quarters, reconcile to bridge v3 exit and WS29 | fable | - | done | 00:20 | notes/06_fy27_path_v2.md | 04:45 |
| 06v | Independent check of 06 (arithmetic, PIT, reconciliation); writes corrections into 06's folder as `_v2b` if needed | fable | 06 | done | 04:45 | notes/06v_fy27_path_check.md | 05:35 |
| 10 | Margin harness: targets panel, baselines, recency-weighted scorer, registry (imports frozen harness calendar/validator) | fable | 02, 03 | done | 00:35 | notes/10_harness_margin.md | 05:15 |
| M1 | Driver-based cost lines v2 (per-unit costs on nights, GBV, ADR, regional mix, seats, FX), PIT refits | fable | 10, 01 | done | 05:15 | notes/M1_driver_lines.md | 05:50 |
| M2 | Time-series and ratio methods (seasonal margin, incremental margin, % of revenue with drift) + baselines | fable | 10 | done | 05:15 | notes/M2_margin_ts.md | 06:05 |
| M3 | Guidance-policy model: FY floor + cushion, Q4-implied margin, language pattern; forecasts the guide and the actual given the guide | opus | 10, 05 | running (relaunched 14:45 on opus) | 06:05 | notes/M3_guide_policy_margin.md | 14:45 |
| M4 | Alt-data-augmented line model (headcount, ads, support, payments, rates), incremental value vs M1 | opus | 10, 04, M1 | running (relaunched 14:45 on opus) | 05:50 | notes/M4_alt_augmented.md | 14:45 |
| M5 | Consensus-anchored model: Street EBITDA at guide date + systematic bias and revenue-surprise flow-through | fable | 10, 03 | pending | | notes/M5_street_bias.md | |
| M6 | Cycle and cost-flex model: cost response to growth deceleration; scenario engine over bear/base/bull revenue paths | opus | 10, 06v | running (relaunched 14:45 on opus) | 05:35 | notes/M6_cycle_flex.md | 14:45 |
| M7 | Below-EBITDA bridge: SBC, D&A, interest income, tax, share count, EPS; FCF bridge; backtests | opus | 10 | running (relaunched 14:45 on opus) | 05:15 | notes/M7_below_ebitda.md | 14:45 |
| 20 | Scoreboard: all methods and baselines, both windows, equal and recency weighted, coverage, parameter counts, error correlations | opus | M1-M7 | pending | | notes/20_scoreboard.md | |
| 21 | Red team: leakage/PIT audit, overfitting, kill-list compliance, for every method | opus | M1-M7 | pending | | notes/21_red_team.md | |
| 22 | Discussion round: orchestrator sends 20+21 to each method agent for rebuttal/adjustment; collected in DISCUSSION.md | orchestrator | 20, 21 | pending | | DISCUSSION.md | |
| 23 | Triangulation: final combined model, quarterly forecasts 3Q26-4Q27 + FY28, vs consensus and management, cyclicality, scenarios, workbook, SYNTHESIS.md | opus | 22 | pending | | SYNTHESIS.md | |
| 30 | Codex (gpt-6-astra) read-only audit of the final model | codex | 23 | pending | | audit/CODEX_ASTRA_AUDIT.md | |
| 31 | Apply the audit: triage, fix, re-run, re-score, record accept/reject | opus | 30 | pending | | audit/AUDIT_RESPONSE.md | |
| 32 | Morning report, explainer HTML artifact, WORKBOARD rows, commit, push, draft PR | opus + orchestrator | 31 | pending | | MORNING_REPORT.md | |

## Log

- 14 Sep ~06:10 FABLE LIMIT reached (separate from the 5-hour window): M3, M4, M6, M7 killed. M3 had nothing on disk; M4 run.py + pre-registration only; M6 and M7 had code, outputs, registry files and pre-registration notes but no results write-up.
- 14 Sep 14:45 Krish (awake): 'move what you can to opus'. All four relaunched on Opus with RESUME prefixes; every remaining stage (20, 21, 23, 31, 32) switched to Opus. Heartbeat cron recreated as cf29b46b with the Opus instruction.

- 14 Sep 06:05 M2 done (7 objects, 29 specs; drift/ratio objects FAIL vs naive; q_sentence_direction|k_fit_rw passes: 2.07/1.64pp, rw 1.53/1.38, ratio 0.92/0.84; best in EBITDA $ and beats Street there; nothing beats Street on margin PIT; LIVE 3Q26 sentence rule 48.1% $2,309M vs Street 49.8%, naive-with-drift 51.35%). M3 launched.

- 14 Sep 05:50 M1 done (driver-lines registered; pass lines FAIL: margin h=0 MAE 2.26/1.91pp = naive equal-weighted, 0.87/0.85 rw; h=1 worse than naive because of the revenue leg; oracle-revenue spec beats naive everywhere; cor elasticity 0.81 on GBV stable, ops 0.76 on nights, sm 0.42 unstable; LIVE base 3Q26 51.6% vs LSEG 49.8%, gap = S&M; FY26 36.2%, FY27 35.1% vs LSEG 36.4%). M4 launched.

- 14 Sep 05:35 WS06v done: PASS WITH CORRECTIONS (independent FY27 $15,797M +10.71% vs WS06 $15,829M; all diffs are named judgement calls; one MEDIUM fix: 3Q26 bear/bull revenue was base in all scenarios -> v2b sets $4,755M/$4,878M). Margin model reads 06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv (copied in by orchestrator). Open decision for Krish: stacked ex-NA deceleration (base) vs no-2027-lap (+11.9%). M6 launched.

- 14 Sep 05:15 WS10 done (margin harness; 7 baselines x 14/10 dates; seasonal naive MAE 2.24/1.96pp; Street hardest 1.59/1.31pp, bias -1.2pp, only object surviving both windows; quarterly-sentence direction rule 13/14 right, flagged for a method; LIVE vintage 2026-09-11). Stage 2 launched: M1, M2, M7 (06v still running).

- 14 Sep 04:50 WS02 done (34-quarter x 145-column panel, 3,066 provenance rows; adj EBITDA rebuilt within $0.97M all 22 quarters; seasonality mechanical except Q1; G&A ex-lodging series; ops cash per booking $10.74 -> $8.06; correction: repo Q4 SBC totals wrong in three panels). Brief corrected: venv python lacks scipy/statsmodels/sklearn; all modelling on py -3.13.

- 14 Sep 04:45 WS06 done (FY27 revenue base $15,829M +10.94%, bear +5.2%, bull +15.7%; nights +6.6% vs B3 +9.5; front-loaded quarters 1Q27 +14.0% to 4Q27 +9.1%; 8 audit findings on PR #32, two HIGH: no FY27 levels, lap placement inconsistent with bridge v3). WS06v launched.

- 14 Sep 04:32 LSEG desktop API (localhost:9000) refuses connections although Workspace processes are alive; WS03's daily raw pulls (to 11 Sep) are cached so no downstream stage needs LSEG. Krish: re-open/re-sign-in Workspace in the morning if a fresher pull is wanted. Not touching credentials.

- 14 Sep 04:30 WS05 done (377 statements, 183 new, 155 from 31 non-earnings events; November rule: numeric floor -> 'approximately floor+50bp'; 5 Nov prior: approx 36% (0.45), 35.5% held (0.35), at least 36% (0.15); Q4 print beats sentence-implied Q4 by 0.7-4.3pt n 3; margin_total kept 85% n 55).

- 14 Sep 01:24 USAGE LIMIT hit (session limit, reset 3:50am ET): WS02, WS05, WS06, WS10 agents killed mid-work (WS02 had all CSVs but no note; 05/06 only run.py stubs; 10 only targets.csv). Heartbeats queued.
- 14 Sep 04:20 Limit reset; all four relaunched with RESUME prefixes.

- 14 Sep 00:35 WS04 done (58 series, 1,146 tests; survivors: 3m T-bill -> interest income r 0.83 n 18, rule 0.86 x T-bill x earning base; Trends category share -> S&M per night r -0.64 n 18; careers postings vs PD r 0.9 but n 6-7; all else fails). WS10 harness launched on fallback panel, will switch to WS02 when it lands.

- 14 Sep 00:20 WS03 done (LSEG daily PIT consensus 2021-2026, 22/22 prints; Street under-called margin 21/22, W1 +1.82pt, W2 +1.70pt, last four +0.43pt; flow-through beta 0.57 weak; Street anchors on FY floor; 3Q26 cons EBITDA $2,361.5M / 49.78%, FY26 35.62%, FY27 36.45%; Bloomberg file pull-date anchored). WS06 launched.

- 14 Sep 00:15 WS01 done (123-row census, 26 gaps, top-10 unused inputs: interest income = balances x DTB3, 10-Q MD&A deltas, lagged S&M deleverage, regional-mix line, hosting commitments...). WS05 launched.

- 13 Sep 23:10 Krish's brief received; questions answered (targets: adj EBITDA + six lines, GAAP/EPS bridge, FCF, 5 Nov language;
  revenue path: bridge v3 + audited FY27; sources: archives, third-party public, Bloomberg local, LSEG API, EDGAR, transcripts;
  Codex audit-only then Claude fixes; in-session heartbeat resume; Fable, max 4 concurrent, Opus for simple tasks; seasonal + macro cycle; branch/push/PR).
- 13 Sep 23:30 LSEG desktop session tested OK via lseg-data on `py -3.13` with `LSEG_APP_KEY`. Codex exec smoke test OK (read-only, ephemeral).
- 13 Sep 23:55 Stage 1 launched: WS01-04 on Fable (4 concurrent). Heartbeat cron 6c78a4f3 at :13 and :43.
- 13 Sep 23:40 Worktree `citadel-abnb-margins` created from origin/main fd4272f; raw junctions added; brief and ledger written.
