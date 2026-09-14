# Shared rules block (embedded verbatim at the end of every Lane 2 brief; kept here so the parent can quote it)

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
