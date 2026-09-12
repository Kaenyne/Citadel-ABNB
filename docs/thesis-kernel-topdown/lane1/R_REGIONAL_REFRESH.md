# R — Regional reconciliation refresh (composition engine; needs internet for arrivals pulls)

**Role in Lane 1:** Improves the FY27 composition paragraph: regional nights and ADR with intervals, geo mix as an output.

## Files this agent reads
- `analysis/src/forecast_methods/l1_reconciliation_v2/` (copy from; do not edit) and its note `05_backtests/B3_FY27_DECOMPOSITION.md`, `l1-reconciliation.md`
- `data/processed/forecast_methods/L0/` (72 exact cells, interval observations)
- `data/processed/overnight/10_regional_panel_quarterly.csv`, `10_regional_forecast.csv`; `data/processed/adr/01_regional_annual.csv`
- arrivals: NTTO I-94 monthly by country of residence; Eurostat `tour_occ_nim` by country; JNTO / INE Frontur / DATATUR / ISTAT monthly (pull with manifests)

## Task
Build `l1_reconciliation_v3/`: (1) add national arrivals as covariates for the regional latent nights (NA ← NTTO; EMEA ← Eurostat by country;
APAC ← JNTO/Australia; LatAm ← DATATUR/Brazil), lag-aligned to fiscal quarters; (2) shrink regional ADR levels toward the 10-K annual anchors
instead of flat bands; (3) bootstrap the identity residuals; (4) re-run the FY27 attribution block (geo mix, unit size, LOS, seats, FX carried,
remainder) with intervals and the kernel-weight band. Report the ex-FX ADR residual against the ADR note (v2 was −1.4pp at worst).

## Pass line (pre-registered)
Gate G2 still passes (72/72 cells); the ex-FX ADR residual vs the ADR note improves to under 0.8pp in every year, or the note explains why not;
regional ADR levels identified to better than ±10%.

## Outputs (all new files)
`l1_reconciliation_v3/` · registry `l1-reconciliation-v3__fy27_{revenue,growth}` · `05_backtests/R_REGIONAL_REFRESH.md` · arrivals manifest

## Report back (final message; ≤ 250 words)
The FY27 attribution block with intervals; the residual table; which arrivals series earned a place.

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
