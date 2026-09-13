# F — RNPL as a variable in the model and as thesis F (subagent)

**Role in Lane 2:** the memo's RNPL leg. Everything it needs is in the repo; EDGAR (public) only if a filing sentence must be quoted verbatim
and the repo notes do not already carry it.

## Files this agent reads
- `docs/thesis-kernel-topdown/lane2/CONVENTION.md` (first); `docs/thesis-kernel-topdown/prompts/WP-F_rnpl_variable.md` (the full spec — this brief
  binds it to the Lane 2 rules)
- `docs/revenue-forecast-strategy/05_backtests/K1_KERNEL_WEIGHTS_AND_BACKLOG.md` (parts B–C), `05_backtests/tracker-backlog.md` (why the restated
  unearned-fees pin is circular — never use it), `05_backtests/D_CARD_ADDENDUM_LAMBDA.md` (Lane 1's card rows; do not duplicate, extend)
- `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md`, `analysis/src/rnpl_balance_sheet_bridge.py`, `docs/RNPL_HANDOFF.md`,
  `research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md`, `data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv`
- `analysis/src/forecast_methods/kernel_engine_v2/` (import for the kernel; never re-derive λ); `data/processed/overnight/02_kpi_panel_quarterly.csv`

## Task
Build `rnpl_v2/` exactly as WP-F §"Build" items 1–6 (paid backlog and seasonal coverage norms; u and m by the joint solve with the excess-unpaid
series; decision D-06 answered from the filing notes with the sentences quoted; the leakage kernel revenue_q = c_s Σ φ_k GBV_{q−k}(1 − L_q) with
L from the D1 grid; the λ control chart with seasonal bands, the 5 Nov thresholds 17.09 / 16.93% and the historical false-alarm rate; nights as a
switchable input — team baseline, Theo re-base, ex-NA lap — with 3Q26 / 4Q26 revenue under each; the thesis-F write-up with the tells and ONE
refutation condition offered for D-10 as an option, not adopted).
Point-in-time: the leakage kernel is registered historically only where every input existed at the guide date (balance-sheet lines from the
10-Q filed on/before d; D1 grid parameters are scenario inputs dated 11 Sep 2026 and are NOT backdated — say so on every historical row that
uses them, or leave those rows out and register the LIVE rows only).

## Pass line (pre-registered — copy verbatim into the note before running)
The excess-unpaid series reproduces (+2.0 / +8.1 / +9.7pp); the λ chart's historical false-alarm rate is published with n; the model runs under all
three nights inputs with 3Q26 / 4Q26 revenue for each; D-06 has a documented, quoted answer; D-10 has one proposed refutation condition. Any
item missing → partial, with the missing item named.

## Outputs (all new files)
`analysis/src/forecast_methods/rnpl_v2/` (run.py, README, tests) · `data/processed/forecast_methods/rnpl_v2/` · registry `rnpl-v2__revenue_next_q`
(three nights variants as three objects or a `spec_id`; LIVE rows 2026Q3 / 2026Q4 at RUN_DATE; historical PIT rows only under the rule above) via
`harness_v1_1` · note `05_backtests/ALPHA_F_RNPL.md` with proposed card rows F1–F4 (do not edit the card).

## Report back (final message; ≤ 250 words)
u and m ranges; the excess-unpaid series; false-alarm rate with n; 3Q26 / 4Q26 revenue under the three nights inputs; the D-06 answer in one
sentence with the filing reference; the D-10 condition; the verdict.

## Rules that bind this agent (do not skip)

- **Read only:** this file, `docs/thesis-kernel-topdown/lane2/CONVENTION.md`, `docs/thesis-kernel-topdown/03_NUMBERS_CHEATSHEET.md`,
  `analysis/src/forecast_methods/harness/README.md`, `analysis/src/forecast_methods/harness_v1_1/README.md`, and the files named above.
  Nothing else unless a step says so (token discipline).
- **Copy, never overwrite.** New folder under `analysis/src/forecast_methods/`, new outputs under `data/processed/forecast_methods/`, registry
  files only under a NEW method name, your note as a NEW file under `docs/revenue-forecast-strategy/05_backtests/`. Never edit `harness/`,
  `harness_v1_1/`, `L0/` (append-only with a dated backup — only M may append), another package, `20_frozen_q3_2026.csv`, `research/thesis.md`,
  or any tracked data file.
- **Point-in-time as defined in `CONVENTION.md`** — a guide-date vintage includes that letter; morning-of-print consensus is pre-letter;
  `role = current` rows never appear at a historical date; executable returns are `excess_open_*` from `returns_v1`. Windows W1 (1Q23+, 14)
  and W2 (1Q24+, 10), both; letter integers scored as [x−0.5, x+0.5].
- **Pre-register the pass line** (below) in your note before running; publish a failure as a result. n < 6 evaluable cells in either window is
  "underpowered", never "pass".
- **Register through `harness_v1_1.registry.register`** (W1/W2 rows: guide-date vintages, both replays PIT and full_sample; LIVE rows: vintage
  = RUN_DATE). Do not run either scorer — the parent does at CLOSE.
- **Your own new test has a bug?** Fix it once, keep the failing output in your outputs folder as a receipt, say so in the note. Do not stop.
  A failing *frozen* test (harness / L0) is a STOP.
- **Portable commands:** `python` from `.venv`, run from the repo root, paths via `pathlib`.
- **No decisions, no kill-list numbers, no credentials, no licensed data in git, nothing that touches airbnb.com** (only L, and only if
  sanctioned). The eleven team decisions are in `docs/revenue-forecast-strategy/AGENT_BRIEF.md` §3; the kill list in §6.

## Note template

```
# <ID> — <title>          agent · date · branch · time spent
## Verdict (plain language, first): pass / fail / partial / underpowered vs the pre-registered line
## Pre-registered pass line (verbatim, with the timestamp it was written)
## What ran: exact commands, exit codes, wall time
## Results: tables with n on every row; PIT vs full-sample labelled; vendor + timestamp on every consensus number
## What failed or could not be done, and why
## Interpretation (honest)
## RESUME: one paragraph for the next agent
```
