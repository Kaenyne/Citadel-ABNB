# WS10: The margin harness (targets, baselines, recency-weighted scorer, registry)

Read `docs/margin-build/00_BRIEF.md` first. Slug: `10_harness_margin`. Every method M1-M7 registers through you, so build this first, fast, and
document the API in `analysis/src/margin_build/10_harness_margin/README.md`. Read the frozen revenue harness
`analysis/src/forecast_methods/harness/README.md` and its code: you must reuse its calendar (guide dates W1/W2/LIVE, print dates), its
registry FORMAT 1.0 column set, and its validator logic (import from it; do not copy-paste-and-drift, and do not modify it).

## Inputs

- WS02 panel: `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv` (and provenance).
- WS03 consensus: `data/processed/margin_build/03_consensus_pit/03_consensus_at_dates.csv`, `03_surprise_history.csv`.
- Guidance ledger: `data/processed/overnight/02_guidance_ledger.csv` (margin rows) and WS05 `05_guide_language_pattern.csv` if on disk.
- If WS02 or WS03 is not on disk yet when you start, build against the existing repo panels (`abnb_quarterly_cost_stack_exsbc.csv`,
  `16_consensus_at_print_merged.csv`) with a clearly labelled fallback loader, and re-run when the WS02/03 files appear (check again before you finish).

## Build

1. `targets.csv` under `data/processed/margin_build/10_harness_margin/`: one row per quarter 1Q20-2Q26 with target metrics:
   `adj_ebitda_musd, adj_ebitda_margin_pct, cor_cash_musd, ops_cash_musd, pd_cash_musd, sm_cash_musd, ga_cash_musd` (and the same as `_pct_rev`
   and `_per_night`), `sbc_musd, da_musd, op_income_musd, op_margin_pct, net_income_musd, eps_diluted, fcf_musd, fcf_margin_pct, interest_income_musd,
   tax_rate_pct, diluted_shares_m`, plus the denominators (revenue, nights, GBV) for convenience. Document units.
2. `history_as_of(vintage_date)`: the PIT slice (a quarter's actuals are knowable only from its print date; use the frozen calendar).
3. Baselines, registered as method `baselines-margin` with one object each, for every target, every W1/W2 guide date and the LIVE date (2026-09-12
   or the latest date the validator accepts; if the validator only accepts 2026-09-11 as TODAY, use that and say so), horizons 0-2 quarters
   (the quarter being guided, the next, the one after) where the target quarter is in the window:
   `seasonal_naive` (same quarter last year), `seasonal_naive_drift` (last year's value plus the trailing y/y change in the metric),
   `trailing4` (mean of last four quarters, for ratios), `pct_rev_last4` (cost as % of revenue trailing-4 x the revenue forecast, with the revenue
   forecast taken from the frozen harness `baselines` guide-cushion object so the margin baseline is honest about revenue), `guide_implied`
   (the FY margin floor/point in force at the vintage date minus YTD actuals, for the remaining quarters, prorated by the 2023-25 seasonal shares;
   NaN where no FY margin guide existed), `street` (WS03 consensus at the vintage date, with vendor and as-of).
4. Scorer `score.py`: reads every registry file under `data/processed/margin_build/registry/`, joins actuals and baselines, and writes
   `scoreboard_margin.csv` with, per (method, object, target, window, horizon): n, MAE, RMSE, bias, MAE ratio to each baseline, pinball/CRPS on
   supplied quantiles, 80%/90% coverage, `survives_both_windows`, `n_params`, and ALL of these again recency-weighted (exponential weights,
   half-life 4 quarters, anchored at the latest quarter in the window). Also a `by_quarter` long file so methods can diff their errors.
5. `register(df)`: wraps the frozen validator; enforces `target` in targets.csv; writes to the margin registry folder.
6. `run.py` rebuilds targets, baselines, and the scoreboard (exit 0); unit tests `tests.py` (PIT rule, window membership, baseline arithmetic on
   two hand-checked cases). README with the run command and a 15-line usage example for method authors.
7. Note `docs/margin-build/notes/10_harness_margin.md`: what the harness gives, the baseline scoreboard table (which naive baseline is hardest
   to beat, per target and window, equal vs recency weighted), caveats, "For the model", RESUME.

## Pass line (pre-registered)

`run.py` exits 0; every baseline object covers all 14 W1 and 10 W2 guide dates for adj EBITDA margin; the seasonal-naive MAE on adj EBITDA
margin (h=0, W1) is reported with n=14; tests pass.
