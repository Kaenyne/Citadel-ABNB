# V — Valuation reconciliation page (prepares the human direction decision WP-H)

**Role in Lane 1:** Arithmetic only; no recommendation. Puts the football field, the growth-to-multiple relation and the memo v0 branch prices on one page.

## Files this agent reads
- `docs/overnight/FINAL_SUMMARY.md` (football field, exit-multiple band, +0.48 turns/pt)
- `data/processed/overnight/12_exit_multiple_recommendation.csv`, `12_peer_multiples.csv`, `13_valuation_summary.csv`, `12_abnb_multiples_history` outputs if present
- `data/processed/overnight/13_model_annual.csv` (FY27E EBITDA) and `model/assumptions.md` "Model conventions"
- `docs/revenue-forecast-strategy/05_backtests/B3_FY27_DECOMPOSITION.md` (the FY27 growth band)
- `deck/drafts/memo_v0_2026-09-11.md` (branch prices) · `data/processed/abnb_daily_close.csv` (refresh with `yfinance`)

## Task
Build `valuation_v1/` and write one page: (1) reproduce the EV/EBITDA-vs-forward-growth relation point-in-time (report slope and CI;
expect ≈ +0.48 turns per point); (2) map the FY27 growth band (+9.18 / +10.35 / +11.52% at w 0.33 / 0.50 / ⅔) through it to a multiple band and,
with FY27E EBITDA, to a price band; (3) the football field at 13.5 / 16.5 / 18.5x; (4) the memo v0 branch analogues ($140–152 / $170–185 /
$205–215) and what they were derived from; (5) positioning refreshed (price today via yfinance, short interest, ratings split, target
dispersion as available in the repo files). Present as a side-by-side table with the arithmetic shown. Do not recommend a direction.

## Pass line (pre-registered)
Every number on the page traces to a file or a shown calculation; the growth-to-multiple slope reproduces within its CI; the page fits one screen.

## Outputs (all new files)
`valuation_v1/` · `05_backtests/V_VALUATION_RECONCILIATION.md`

## Report back (final message; ≤ 250 words)
The price band implied by the FY27 growth band; the football field; the branch analogues; the three inconsistencies the team must resolve.

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
