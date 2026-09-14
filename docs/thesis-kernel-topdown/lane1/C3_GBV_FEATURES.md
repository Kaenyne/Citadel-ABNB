# C3 — Retarget the alt-data features at booked GBV and the kernel residual (ledger features only)

**Role in Lane 1:** Tests the thesis that the earlier 3,500 failures were a target-selection problem.

## Files this agent reads
- `analysis/src/overnight/08_altdata_backtests.py`, `data/processed/overnight/08_feature_tests_all.csv` (the machinery and the feature universe)
- `data/processed/forecast_methods/kernel_phi_v2/` (the residual R_q) · `02_kpi_panel_quarterly.csv`
- `docs/thesis-kernel-topdown/prompts/WP-C3_gbv_features.md`

## Task
Build `gbv_features_v1/`. Pre-register the feature list in the note BEFORE running: RNPL-corrected unearned-fees growth, funds-payable growth,
GBV momentum, NTTO arrivals (if pulled), the reviews stays index if present in the tree (`docs/q3nowcast`), hotel RevPAR. Exclude Google Trends
and sentiment. Targets: (a) booking-dated GBV y/y for the quarter in progress; (b) R_q. PIT, both windows, nested expanding-window CV for anything tuned.

## Pass line (pre-registered)
A feature earns a place only if it beats the ledger baseline (RNPL-corrected unearned fees) on GBV on BOTH windows with a stable sign. Report every
feature that did not, with ratios.

## Outputs (all new files)
`gbv_features_v1/` · registry rows for survivors only · `05_backtests/ALPHA_C3_GBV_FEATURES.md`

## Report back (final message; ≤ 250 words)
Survivors with ratios on both windows; the full failure table; the pre-registered list as written.

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
