# Overnight run: state ledger and continuation instructions

Owner: Krish (asleep). Orchestrator: Claude Code session in `C:\Users\krish\citadel-abnb-overnight` (branch `krish/overnight-synthesis`). Started 2026-09-06 ~01:20 local. This file is the single source of truth for continuing the run after a usage-limit pause, a crash, or a new session. Update the status table whenever a workstream finishes.

## How to continue (any orchestrator, any session)

1. Read `docs/overnight/00_BRIEF.md` (shared brief) and this file.
2. For each workstream below with status not `done`: check whether its note `research/notes/overnight/NN_*.md` exists and ends with a "For the model" section. If yes, mark `done`. If no, check whether an agent is still running on it (ListAgents in-session; or file mtimes under `data/processed/overnight/NN_*` and `analysis/src/overnight/NN_*` newer than 40 minutes = probably still running). If not running, relaunch it with `Agent` (subagent_type general-purpose, **model: "opus"**) using the prompt file `docs/overnight/prompts/NN.md`, prefixed with: "RESUME: check existing NN_* files first and continue from them."
3. When workstreams 01-12 are all `done`, launch wave 2 in this order: 13 (model build) and 15 (red team) in parallel; then 14 (synthesis) after 13 finishes. Prompts in `docs/overnight/prompts/13.md`, `14.md`, `15.md`. All on Opus.
4. After 14 finishes: `git add` the `overnight/` folders plus `docs/overnight/`, `model/` outputs, and commit on this branch with message "Overnight synthesis run 6-7 Sep 2026: workstreams 01-15" (co-author trailer per session rules). Do not push unless Krish's earlier instruction covered it (it did not; leave unpushed). Then write the final summary to `docs/overnight/FINAL_SUMMARY.md` (the synthesis note's bottom line plus the file map) so Krish sees it on waking.
5. Never run `git checkout`, `merge`, `stash` or touch `C:\Users\krish\citadel-abnb` (main tree) or other worktrees.

Manual restart if the session is gone: open a terminal in `C:\Users\krish\citadel-abnb-overnight`, run `claude`, and paste: "Continue the overnight run per docs/overnight/RUN_STATE.md. Use model opus for every subagent."

## Status (update in place)

| WS | Topic | Status | Agent launched | Note path | Last update |
|---|---|---|---|---|---|
| 01 | Data census matrix | done | yes | research/notes/overnight/01_data-census.md | 02:05 |
| 02 | KPI panel + guidance ledger | done | yes | 02_kpi-panel-and-guidance-ledger.md | 02:12 |
| 03 | Management language vs stock | done | yes | 03_management-language-and-stock.md | 02:24 |
| 04 | Consensus reconstruction | done | yes | 04_consensus-and-reaction.md | 02:16 |
| 05 | Macro outlook + transmission | done | yes | 05_macro-outlook-and-transmission.md | 02:44 |
| 06 | Consumer choice + WTP | done | yes | 06_consumer-choice-and-willingness-to-pay.md | 02:40 |
| 07 | Ops + margin levers | done | yes | 07_ops-and-margin-levers.md | 02:36 |
| 08 | Alt-data index + backtests | done | yes | 08_altdata-index-and-backtests.md | 02:49 |
| 09 | Stock behaviour + alpha | done | yes | 09_stock-behaviour-and-alpha.md | 02:27 |
| 10 | Regional decomposition | done | yes | 10_regional-and-segment-decomposition.md | 02:30 |
| 11 | Competition, supply, overlays | done | yes | 11_competition-supply-and-overlays.md | 02:05 |
| 12 | Valuation multiple regime | done | yes | 12_valuation-multiple-regime.md | 02:19 |
| 13 | Driver model build (Excel + Python) | done | yes | 13_driver-model-build.md | |
| 14 | Master synthesis | done | yes | 14_master-synthesis.md | |
| 15 | Red-team verification | done | yes | 15_red-team.md | |
| 16 | Web gap fill (Chrome) | done | yes | 16_web-gap-fill.md | 10:48 |
| 17 | Excel COM audit of the workbook | done | yes | 17_excel-audit.md | 11:40 |
| 18 | WS16/WS17 corrections + share-count fix | done | yes | 18_corrections-applied.md | 12:35 |

## Log

- 01:20 worktree created from origin/main; 11 open branches union-merged; raw-data junctions added.
- 01:25 wave 1 launched on default model (12 agents). 01:45 stopped on Krish's instruction (usage); 01:47 relaunched all 12 on Opus, resuming from files on disk.
- 01:55 Krish: 5-hour window at 70%; asked for automatic continuation after the limit resets without stopping the run. This ledger, the prompt files, and an in-session heartbeat cron (every ~25 min) were added.
- 02:05 WS01 and WS11 finished (opus). Prompt files 01-15 written to docs/overnight/prompts/. Heartbeat cron e919020b active (17,42 past each hour).
- 02:12 WS02 finished: 194-row guidance ledger; revenue range is a floor (15/19 above top); cushion halved to 1.9%; 3Q26 cushion-adjusted rev $4.82bn.
- 02:16 WS04 finished: consensus 23/23 prints; beat-vs-Street 22/23 (no day-1 alpha, all LOO negative); nights-vs-Street-nights beat drives 20-day excess (n 18, LOO +0.13); Q3-26 Street rev $4.74bn.
- 02:19 WS12 finished: multiple driven by NTM growth (+0.48x/pt), not margin; premium to peers is entirely the SBC add-back; recommended exit multiples 13.5/16.5/18.5x -> $137/$191/$242 vs model 18/22/25.5x; spot above mean PT; day-1 moves are re-ratings (corr 0.97).
- 02:24 WS03 finished: sentiment useless (r 0.08); long-term-framing share of prepared remarks r +0.69 with day-1 (948 tests, none pass BH); credibility 62% (multi-year 26%, Chesky 42%, pricing 0/7); WebSearch budget exhausted session-wide.
- 02:27 WS09 finished: post-print drift -3.7% at 20d (up-prints -14.8% at 60d, down-prints zero); May underperformance 6/6, Nov 5/5; rates beta never significant; 2026 move is idiosyncratic; no implied event premium yet; cost of equity 10.5-11.5%.
- 02:30 WS10 finished: regional panel reconciles within 1.1pp; BKNG room-night acceleration leads EMEA/total (r 0.88/0.91, n 7); NA slowdown was inbound shock (Canada -31% -> +5% Jun 2026); 3Q26 base nights +10.3%, rev $4,775m; FY27 rev +12.4%; FX tailwind rolls off FY27.
- 02:36 WS07 finished: 85% of cash cost/night rise is S&M; 1H26 ramp is brand+performance +32% (correction to margin note); AI support +0.39 pts; lever base FY26 36.1/FY27 36.6/FY28 37.5; P(>=40% by FY28)=21%; FY26 floor breaks only if H2 brand+perf >+29%.
- 02:40 WS06 finished: hotel price tailwind reversed (CoStar Jul ADR +5.7%); ~half of ADR growth is bedroom mix (>=1.79 bedrooms/night, $103 per bedroom-night); single host fee = +40-45bps take rate at best; 1.71m fee-inclusive quotes show discount share 11%->31% Mar-Aug 2026; FY27 ADR ex-FX +2.5%, take rate 13.3%.
- 02:44 WS05 finished: no high-confidence macro driver of nights; revenue FX lags spot 1-2 quarters (fit -0.64 + 0.413 x mean EUR/USD y/y t-1,t-2), 4Q26 rev FX ~ -0.4pp vs +3pp in 3Q26; Fed regime hike-vs-hold; scenarios 30/50/20 -> prob-weighted FY27 rev +10.3%, margin 36.4%; Q4 guide +11-13% expected.
- 02:46 Wave 2 started early: WS13 (model) and WS15 (red team) launched on opus while WS08 still runs; both told to pick up 08's note when it appears. WS14 (synthesis) launches after 13 and 15 finish.
- 02:49 WS08 finished: no composite beats naive; 598 tests, one new survivor = funds held for clients y/y -> next-quarter revenue y/y (WF RMSE ratio 0.60, n 14); Trends 0/162, Eurostat stops Mar 2026, Inside Airbnb fixed panel n=0; 3Q26 FX-to-ADR +0.80pp, guide midpoint reproduced by nights +11%, ADR +4.05%. All of wave 1 (01-12) done.
- 02:58 heartbeat: 13 and 15 running (11 min); 01-12 done; nothing to do.
- 03:27 WS15 finished: 98 claims checked (83 confirmed, 9 wrong, 2 unsupported, 4 unverifiable), 16 cross-note conflicts, all 34 scripts re-run clean. Key: WS08 funds-held survivor is window-dependent (0.59x vs 1.85x AR(1)); WS01 census read a half-finished WS08; exit multiple is the whole pitch ($190 vs $249); four FY27 revenue growths across notes are not independent. WS13 still running.
- 03:29 WS13 finished: model/ABNB_driver_model.xlsx (9 sheets, 2,303 formulas, 216 outputs reconcile to Python); base FY27 rev $15.84bn (+11.3%), EBITDA 35.9%, FCF/sh $9.58; football field base $112/$163/$221 vs $181.94; base price fell $248 -> $184, $55 of it exit multiple. WS14 synthesis launched.
- 03:31 heartbeat: 01-13 and 15 done; 14 (synthesis) running since 03:29; nothing to do.
- 03:42 WS14 finished: research/notes/overnight/14_master-synthesis.md and docs/overnight/FINAL_SUMMARY.md written. All 15 workstreams complete. Committing.
- 03:44 Committed b4c4c59 on krish/overnight-synthesis (295 files, not pushed). Heartbeat cron deleted. Run complete.
- 10:48 Follow-up: WS16 (web gap fill via Chrome) done: 2Q24 next-Q consensus $3.84bn (guide -3.65%, 9/9 guide-below-Street negative at 20d); Zacks ADR consensus exists (5 prints); red-team corrections 11/15 withdrawn (single-fee ~50% is in the 2Q26 call transcript); direct-booking pilot 0-15bp not -0.8pt; 12 line edits proposed for 14_master-synthesis.md. WS17 (Excel COM audit) running.
- 11:40 WS17 (Excel COM audit) done: Excel 16.0 rebuilt the workbook, 0 error cells in 5,544, 216/216 outputs and 2,348/2,348 formula cells matching to 4.2e-15. 16 findings, 11 fixed with no number moving (the scenario selector was inert; the reverse-DCF answer was a paste). One high-severity item left open: the FY2026 share roll double-counted the 1H26 buyback.
- 12:35 WS18 done: share-count fix applied in 13_driver_model.py and 13_excel_builder.py (FY2026 rolls the 2Q26 count on 2H26 flows only, matching the net-cash line). FY26E shares 580.3M -> 588.9M; every per-share and price output -1.45 to -1.55%; base football-field mean $162.65 -> $160.22, base EV/EBITDA lens $184 -> $181, bear mean $76, bull mean $233. Workbook regenerated and re-audited in Excel: 0 errors in 5,547 cells, 216/216 outputs, 2,349/2,349 formula cells, scenario switch 143 comparisons / 0 mismatches. WS16's 12 line edits applied to 14_master-synthesis.md plus a new section 11 "Post-run corrections"; FINAL_SUMMARY.md, 13_driver-model-build.md and model/assumptions.md renumbered. Ledger: data/processed/overnight/18_corrections_applied.csv and 18_share_fix_delta.csv. Nothing committed.
