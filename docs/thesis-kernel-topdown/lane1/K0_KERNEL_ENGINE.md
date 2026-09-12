# K0 — Kernel engine (the spine; run by the parent, never a subagent)

**Role in Lane 1:** Builds the one module every other Lane-1 package imports. Gate 1: nothing else starts until this passes.

## Files this agent reads
- `analysis/src/forecast_methods/kernel_lambda/` (copy from; do not edit) and `kernel_phi_v2/` (K1 outputs)
- `data/processed/overnight/02_kpi_panel_quarterly.csv`, `02_guidance_cushion_series.csv`, `02_guidance_ledger.csv`
- `analysis/src/forecast_methods/harness/README.md` (calendar, guide dates, registry format)
- `docs/revenue-forecast-strategy/05_backtests/kernel-lambda.md` and `K1_KERNEL_WEIGHTS_AND_BACKLOG.md` (what was already estimated)

## Task
Build `analysis/src/forecast_methods/kernel_engine_v1/` with `README.md`, `engine.py`, `tests/`, `run.py`:
1. `pit_lambda(season, as_of, variant)` — λ_s from quarters printed strictly before `as_of`; variants: same-season mean ex-COVID
   (drop quarters with |nights y/y| > 25%), last-3 same-season, exponentially weighted. Choose the default by leave-one-out on W1 and
   FREEZE it in the README with the LOO table.
2. `kernel_forecast(q, as_of)` — λ_s(q) × (⅔ GBV_{q−1} + ⅓ GBV_{q−2}) using only GBV printed before `as_of`; raises if a needed GBV is not yet printed.
3. `kernel_guide(q, as_of, cushion='median'|'mean')` — forecast ÷ (1 + trailing-8 cushion through the last print before `as_of`).
4. Uncertainty: block bootstrap of within-season λ residuals ⊕ cushion sd; conformal-lite band from walk-forward residuals (state n_cal). Return 50/80.
5. `term_structure(as_of)` — q+1 (both GBVs printed) and q+2 (GBV_{q+1} from the ledger nowcast: RNPL-corrected unearned-fees growth per K1, interval carried).
6. `control_chart(as_of)` — seasonal mean ± 2 within-season sd; the 5 Nov rule (λ_Q3 = revenue ÷ $27,867M; < 17.09% warn; < 16.93% escalate); historical false-alarm count.
7. **Regional-ready interface (required, even though Lane 1 runs consolidated first):** every function must accept an optional per-region GBV
   frame (columns quarter, region, gbv_usd_booking_dated) and, when given, compute per-region kernels with per-region λ and return the
   consolidated sum; with no regional frame it behaves exactly as above. Package X (`X_REGIONAL_KERNEL_OD_FX.md`) will supply that frame.
   Do NOT implement regional λ estimation here — only the interface and the summation.
8. `run.py` prints the acceptance table and writes `data/processed/forecast_methods/kernel_engine_v1/lambda_table.csv`, `term_structure_<as_of>.csv`, `control_chart.csv`.

## Pass line (pre-registered)
The 12-cell λ table reproduces to 2 decimals (Q3 17.391 / 17.145 / 17.182; Q4 11.946 / 12.117 / 12.026 for 2023–2025); `pytest` green,
including a test that every function refuses data printed on or after `as_of`; `run.py` exits 0 in under a minute.

## Outputs (all new files)
`analysis/src/forecast_methods/kernel_engine_v1/` · `data/processed/forecast_methods/kernel_engine_v1/` · `docs/revenue-forecast-strategy/05_backtests/K0_KERNEL_ENGINE.md`

## Report back (final message; ≤ 250 words)
The λ table as printed; the frozen default variant and its LOO; the 5 Nov thresholds; the term structure for 4Q26 and 1Q27 as of today; pytest summary.

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
