# LANE 2 RUN LOG

## 0b. Audit — data access and infrastructure

Parent: Codex (no subagent at Gate 1). Branch: `codex/lane2-full`. Starting commit: `051b03a864593f35c75236c8e1bcf4e0cc40c67e` (merged main, PR #54). Audit recorded UTC: 2026-09-13 12:16:40 UTC. Task began approximately 2026-09-13 12:13 UTC.

The existing checkout was on Lane 1. `git fetch origin` obtained the merged Lane 2 kit; `git switch -c codex/lane2-full origin/main` selected it without changing the existing unrelated untracked files. The 55-path manifest below was extracted directly from section 0b(1) of `docs/thesis-kernel-topdown/prompts/CODEX_LANE2_FULL_PROMPT.md` and checked with PowerShell `Test-Path -PathType Leaf` (portable adaptation of the supplied shell loop).

### (1) Files — verbatim output

```text
ok       docs/thesis-kernel-topdown/lane2/CONVENTION.md
ok       docs/thesis-kernel-topdown/lane2/README.md
ok       docs/thesis-kernel-topdown/lane2/RULES.md
ok       docs/thesis-kernel-topdown/lane2/H11_HARNESS_V1_1.md
ok       docs/thesis-kernel-topdown/lane2/RET_OPEN_RETURNS.md
ok       docs/thesis-kernel-topdown/lane2/A2_GUIDE_SURPRISE_V2.md
ok       docs/thesis-kernel-topdown/lane2/B2_TERM_STRUCTURE_V2.md
ok       docs/thesis-kernel-topdown/lane2/F_RNPL_VARIABLE.md
ok       docs/thesis-kernel-topdown/lane2/C2_MACRO_PULLS.md
ok       docs/thesis-kernel-topdown/lane2/L_POLICY_MONITOR.md
ok       docs/thesis-kernel-topdown/lane2/M_CONSENSUS_STAMP.md
ok       docs/thesis-kernel-topdown/lane2/REFUTER.md
ok       docs/thesis-kernel-topdown/lane2/CLOSE.md
ok       docs/thesis-kernel-topdown/03_NUMBERS_CHEATSHEET.md
ok       docs/revenue-forecast-strategy/AGENT_BRIEF.md
ok       docs/revenue-forecast-strategy/WORKBOARD.md
ok       analysis/src/forecast_methods/harness/README.md
ok       analysis/src/forecast_methods/harness/score.py
ok       analysis/src/forecast_methods/harness_v1_1/README.md
ok       analysis/src/forecast_methods/harness_v1_1/registry.py
ok       analysis/src/forecast_methods/harness_v1_1/score.py
ok       analysis/src/forecast_methods/returns_v1/README.md
ok       analysis/src/forecast_methods/returns_v1/run.py
ok       analysis/src/forecast_methods/kernel_engine_v2/README.md
ok       analysis/src/forecast_methods/kernel_engine_v2/run.py
ok       data/processed/forecast_methods/harness/calendar.csv
ok       data/processed/forecast_methods/harness/targets.csv
ok       data/processed/forecast_methods/harness/scoreboard.csv
ok       data/processed/forecast_methods/returns_v1/ohlc_daily.csv
ok       data/processed/forecast_methods/returns_v1/earnings_reactions_open_v1.csv
ok       data/processed/forecast_methods/returns_v1/manifest.json
ok       data/processed/forecast_methods/L0/L0_vintage_register.csv
ok       analysis/src/forecast_methods/L0/test_l0.py
ok       data/processed/overnight/02_kpi_panel_quarterly.csv
ok       data/processed/overnight/02_guidance_ledger.csv
ok       data/processed/overnight/02_guidance_cushion_series.csv
ok       data/processed/overnight/02_fy_guide_revisions.csv
ok       data/processed/overnight/16_consensus_at_print_merged.csv
ok       data/processed/overnight/04_consensus_at_print.csv
ok       data/processed/forecast_methods/alpha_a/pit_cells.csv
ok       data/processed/forecast_methods/alpha_a/post_letter_diagnostic.csv
ok       docs/revenue-forecast-strategy/05_backtests/K1_KERNEL_WEIGHTS_AND_BACKLOG.md
ok       docs/revenue-forecast-strategy/05_backtests/tracker-backlog.md
ok       docs/revenue-forecast-strategy/05_backtests/D_CARD_ADDENDUM_LAMBDA.md
ok       docs/RNPL_HANDOFF.md
ok       research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md
ok       analysis/src/rnpl_balance_sheet_bridge.py
ok       research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md
ok       data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv
ok       analysis/src/forecast_methods/regional_kernel_v1/public_inputs.csv
ok       analysis/src/forecast_methods/l1_reconciliation_v3/fetch_arrivals.py
ok       docs/thesis-kernel-topdown/prompts/WP-F_rnpl_variable.md
ok       docs/thesis-kernel-topdown/prompts/WP-C2_macro_pulls.md
ok       docs/thesis-kernel-topdown/prompts/WP-L_policy_monitor.md
ok       docs/thesis-kernel-topdown/prompts/WP-M_consensus_stamp.md
MANIFEST TOTAL 55 | PRESENT 55 | MISSING 0
```

Exit code: 0.

Starting commit, interpreter, and frozen scoreboard hash:

```text
051b03a864593f35c75236c8e1bcf4e0cc40c67e
3.12.14 (main, Aug 25 2026, 14:01:42) [MSC v.1944 64 bit (AMD64)]
C:\Users\wille\Desktop\Citadel - ABNB\.venv\Scripts\python.exe
frozen scoreboard sha256 0ed4f213c641286e04251e81652f275d49afc21a4184e88428041ce472d148be
```

### (2) Tests and acceptance

Completed through the frozen scorer; then STOP because the frozen scoreboard changed. Exact receipts and the results table follow the pre-registration section below. Commands use `.venv/Scripts/python.exe -X utf8` from the repository root, equivalent to `python -X utf8` after venv activation. The existing environment is retained.

## Gate 1 — pre-registration and claim

Recorded BEFORE tests/results at 2026-09-13 12:16:40 UTC. Parent claims WP-H11 verification and WP-RET verification. No research package or subagent is running. Exact pre-registered lines from the two supplied briefs follow verbatim.

H11:

> 47 frozen tests green · 37 FORMAT 1.1 tests green · 1.1 scorer exit 0 with 276 rows identical to the frozen board · RUN_DATE prints today's date.
> Anything else → STOP (this is infrastructure, not a research result).

RET:

> 8 tests green · 23 events · every `entry_date` strictly after its `event_date` · `excess_open_*` = ABNB − QQQ to 1e-9. Anything else → STOP.

The broader 0b audit additionally requires 63 kernel tests and kernel acceptance PASS on all 12 cells. Any failing frozen test, incorrect mandatory test count, or change to the frozen board halts the run. No pass is inferred from an unexecuted check.

## Gate 1 — STOP / infrastructure failure

Stopped after 0b(2), before the FORMAT 1.1 scorer, loader/network checks, RET rebuild, or any subagent. Stop confirmed at 2026-09-13 14:21:28 UTC. All completed command outputs, including the complete scorer table, are preserved verbatim in [commands.txt](LANE2_GATE1_STOP_RECEIPTS_20260913/commands.txt). The full frozen-board diff is preserved in [frozen_scoreboard.patch](LANE2_GATE1_STOP_RECEIPTS_20260913/frozen_scoreboard.patch).

| Check | Observed result | Exit |
|---|---|---|
| Required manifest | 55 present / 55; MISSING 0 | 0 |
| Frozen harness + L0 tests | 47 passed in 17.31s | 0 |
| FORMAT 1.1 tests | 37 passed in 13.06s | 0 |
| Returns tests | 8 passed in 0.94s | 0 |
| Kernel tests | 63 passed in 10.22s | 0 |
| Kernel acceptance | `acceptance test: PASS on all 12 cells`; run_seconds 1.222899399988819 | 0 |
| Frozen scorer | 4,109 registry rows / 69 objects; 276 scoreboard rows | 0 |
| Frozen board unchanged | **FAIL**: ` M data/processed/forecast_methods/harness/scoreboard.csv` | — |
| FORMAT 1.1 scorer | Not run after STOP | — |
| Loader and network audit | Not run after STOP | — |
| RET rebuild, manifest dates, explicit event/date summary | Not run after STOP; passing test suite alone does not complete RET | — |

The 37-test FORMAT 1.1 suite passed, including `test_historical_scores_are_identical_to_the_frozen_scoreboard`; this does not supersede the mandatory clean-Git check after the actual frozen scorer.

### Read-only failure diagnosis

```text
rows committed 276 | rows regenerated 276
columns equal True
row keys equal True
parsed differing cells 975 | affected rows 194
columns with differences {'mae': 82, 'rmse': 78, 'bias': 92, 'mape_pct': 86, 'rmse_naive': 108, 'rmse_ratio_to_naive': 92, 'crps': 114, 'pinball_mean': 90, 'pit_mean': 96, 'pit_ks_p': 108, 'conformal_mean_width': 29}
line-ending-normalized bytes equal False
maximum abs difference by numeric column {'mae': 6.821210263296962e-13, 'rmse': 9.094947017729282e-13, 'bias': 7.958078640513122e-13, 'mape_pct': 2.842170943040401e-14, 'rmse_naive': 3.410605131648481e-13, 'rmse_ratio_to_naive': 3.552713678800501e-15, 'crps': 4.547473508864641e-13, 'pinball_mean': 2.2737367544323206e-13, 'pit_mean': 1.1102230246251565e-15, 'pit_ks_p': 1.9484414082171497e-14, 'conformal_mean_width': 7.275957614183426e-12}
rmse exactly equal False
committed git blob sha256 40870de594a4575cbd21fcf43cbf0e60c61016f4d3ccbfe9bbc06e287e45f70c
regenerated sha256 5b91a737c5760376450aa6d8a6f4259f815b846375d95d20a661e00d7d56a23d
```

Git reports 197 removed / 197 added CSV lines. Pandas parsing identifies 975 differing numeric cells across 194 rows; the row keys and column names remain identical. The largest absolute RMSE difference is 9.094947017729282e-13; the largest absolute numeric difference is 7.275957614183426e-12 in conformal_mean_width. These are consistent with platform/library floating-point variation; the causal dependency has not been isolated. No significance, ranking, or thesis conclusion is inferred. This is not only a CRLF/LF issue: line-ending-normalized bytes differ. The original checkout SHA-256 differs from the Git blob SHA-256 because of checkout serialization, so both are recorded separately rather than conflated.

Environment:

```json
{
  "platform": "Windows-11-10.0.26200-SP0",
  "python": "3.12.14 (main, Aug 25 2026, 14:01:42) [MSC v.1944 64 bit (AMD64)]",
  "numpy": "2.5.3",
  "pandas": "3.0.5",
  "scipy": "1.18.1",
  "pytest": "9.1.1"
}
```

### Scope and publication at STOP

No code, registry rows, L0 values, package notes, licensed sources, public data pulls, or financial claims were created or changed. Kernel acceptance rewrote only `run_metadata.json`; its generated change was restored with the audit-authorized `git restore --source=HEAD --worktree -- data/processed/forecast_methods/kernel_engine_v2`. The first restore attempt hit the sandbox's `.git/index.lock` permission boundary; the approved retry succeeded. The frozen-scoreboard regeneration remains an uncommitted local diagnostic until cleanup is recorded below; its full diff is retained separately.

A2: not run; evaluable-cell counts unavailable (not zero); vintage/power/mechanism refuters not run. F: not run; three refuters not run. B2: not run. No new LIVE rows were registered; no Lane 2 memo-ready claims file or PR body was created. The branch exists locally at the merged-main starting commit. No checkpoint was committed or pushed because Gate 1 did not pass; the pass-only checkpoint and all downstream stages were not reached. No PR was opened.

The code, numerical calculations, and frozen tests have not been repaired or relaxed. The user's explicit STOP rule applies even at floating-point scale. No team decision was made.


### Cleanup receipt (does not change the STOP verdict)

The full failing diff was saved before the generated frozen-board change was reverted with `git restore --source=HEAD --worktree -- data/processed/forecast_methods/harness/scoreboard.csv`. The Git-index sandbox required approval; the approved command exited 0. No scorer or downstream package was run again. `git status --short` for the frozen harness and kernel outputs is empty, and the original checkout SHA-256 is restored:

```text
warning: in the working copy of 'docs/revenue-forecast-strategy/WORKBOARD.md', LF will be replaced by CRLF the next time Git touches it
restored frozen scoreboard sha256 0ed4f213c641286e04251e81652f275d49afc21a4184e88428041ce472d148be
receipt sizes {'commands.txt': 16798, 'frozen_scoreboard.patch': 282226}
```

Final reporting time: 2026-09-13 14:34:24 UTC. Wall time is approximately 141 minutes from the approximately 12:13 UTC task start, including approval waits. No runtime token-usage total was provided. Reporting artifacts and WORKBOARD status are local and uncommitted; the original frozen board is clean. No branch push or PR occurred.


## RESUME

Resolve the exact reproducibility requirement for the frozen scorer across the committed environment and this Windows environment before resuming Lane 2. Inspect the preserved patch, dependency versions, and command receipts; do not normalize away this failed run or label it PASS. A future authorized run must complete all missing 0b/Gate 1 checks against the committed frozen board, then pass the gate before spawning A2. The fee-panel check remains the user's separate macOS check for 14 Sep at 09:00; it was not executed on this Windows host.
