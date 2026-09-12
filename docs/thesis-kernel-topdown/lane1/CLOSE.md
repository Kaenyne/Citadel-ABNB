# CLOSE — score, assemble memo-ready claims, update the board (run by the parent, never a subagent)

**Role in Lane 1:** Only claims that survived the refuters reach the memo.

## Files this agent reads
- every Lane-1 note and REFUTE file written in this run; `data/processed/forecast_methods/registry/`; `docs/revenue-forecast-strategy/WORKBOARD.md`

## Task
1. `python analysis/src/forecast_methods/harness/score.py`; if leaders changed, write `05_backtests/SCOREBOARD_v3.md` (new file; label empty-ratio
   rows "no baseline exists", vacuous same-ten-quarter survivors as such).
2. Write `05_backtests/LANE1_MEMO_READY_CLAIMS.md`: for each claim that survived (majority of refuters, or the single refuter in CORE): the exact
   sentence the memo may use, the number, the evidence file, the caveat, W1/W2 results. List refuted and partial claims separately with the attack.
3. Update `WORKBOARD.md` rows (status, note links). Do not make the eleven decisions.
4. Commit on your branch; open one PR against `main`; in the description list per package: pass line, result, refuter verdicts, tokens spent.

## Pass line (pre-registered)
Every sentence in the claims file has a number, a file, a caveat and both windows; nothing from the kill list; the scorer ran after the last registration.

## Outputs (all new files)
`05_backtests/LANE1_MEMO_READY_CLAIMS.md` (+ `SCOREBOARD_v3.md` if needed) · updated `WORKBOARD.md` · the PR

## Report back (final message; ≤ 250 words)
The claims file verbatim; the PR link; anything left undone and why.

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
