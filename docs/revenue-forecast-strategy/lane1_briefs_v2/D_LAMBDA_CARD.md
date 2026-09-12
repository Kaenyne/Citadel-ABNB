# D — λ control chart and backlog split as pre-registration card rows

**Role in Lane 1:** No modelling. Turns K1's thresholds and splits into scorable card rows.

## Files this agent reads
- `docs/revenue-forecast-strategy/05_backtests/K1_KERNEL_WEIGHTS_AND_BACKLOG.md`, `PREREG_ABNB-INT-v1.md`
- `analysis/src/forecast_methods/kernel_engine_v2/` outputs (`control_chart.csv`) if K0 is done

## Task
Write `05_backtests/D_CARD_ADDENDUM_LAMBDA.md` (do NOT edit the card): rows for λ_Q3 with thresholds 17.09 / 16.93%; the paid / booked-unpaid /
not-yet-booked split for Q3 and Q4; the excess-unpaid series (+2.0 / +8.1 / +9.7pp) with its scoring rule; the funds-payable y/y line
(+5 to +11% = deferral on schedule) marked pending decision D-06. Each row: item, value, band, scoring rule, data source on 6 Nov, owner.

## Pass line (pre-registered)
A stranger could score every row on 6 Nov with only the press release and the 10-Q.

## Outputs (all new files)
`05_backtests/D_CARD_ADDENDUM_LAMBDA.md`

## Report back (final message; ≤ 250 words)
The rows, verbatim.

## Rules that bind this agent (do not skip)

- **Read only:** this file, `docs/thesis-kernel-topdown/03_NUMBERS_CHEATSHEET.md`, `analysis/src/forecast_methods/harness/README.md`, and the
  files named below. Nothing else unless a step says so (token discipline).
- **Copy, never overwrite.** New folder under `analysis/src/forecast_methods/`, new outputs under `data/processed/forecast_methods/`, registry
  files only under a NEW method name, your note as a NEW file under `docs/revenue-forecast-strategy/05_backtests/`. Never edit `harness/`,
  `L0/`, another package, `20_frozen_q3_2026.csv`, `research/thesis.md`, or any tracked data file.
- **Point-in-time.** Refit at guide dates; consensus only from `data/processed/forecast_methods/L0/L0_vintage_register.csv` (vendor + timestamp
  before the date); windows W1 (1Q23+) and W2 (1Q24+), both; letter integers scored as [x−0.5, x+0.5].
- **Pre-register the pass line** (below) in your note before running; publish a failure as a result.
- **Portable commands:** use `python` from the project venv (`.venv`), never a machine-specific path. Run from the repo root.
- **No decisions, no kill-list numbers, no scraping, no credentials, no licensed data in git.** The eleven team decisions are in
  `docs/revenue-forecast-strategy/AGENT_BRIEF.md` §3; the kill list in §6.

## Note template

```
# <ID> — <title>          agent · date · branch · time spent
## Verdict (plain language, first): pass / fail / partial / underpowered vs the pre-registered line
## What ran: exact commands, exit codes, wall time
## Results: tables with n on every row; PIT vs full-sample labelled; vendor + timestamp on every consensus number
## What failed or could not be done, and why
## Interpretation (honest)
## RESUME: one paragraph for the next agent
```

## Resumption routing

This is a copy of the original Lane-1 brief with its K0 dependency corrected to the verified v2 package. Parent has claimed the workboard row and owns all workboard edits, scorer runs, git commits and pushes. Write only your own new package, outputs, registry method, figure and note. Do not run score.py. Read the verified K0 v2 README for the public interface; never import failed v1. Do not retrieve any airbnb.com, UF or licensed source. Existing supplied summary CSVs may be read. If public requests fail, use offline deliverables and label them. Report one exact proposed memo sentence and actual token usage if available (otherwise unavailable).
