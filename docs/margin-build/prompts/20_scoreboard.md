# WS20: Scoreboard and comparison of every margin method

Read `docs/margin-build/00_BRIEF.md` and `analysis/src/margin_build/10_harness_margin/README.md`. Slug: `20_scoreboard`. You are an overseer:
you compare, you do not rebuild. Read every method note under `docs/margin-build/notes/M*.md` and every registry file under
`data/processed/margin_build/registry/`.

## Do

1. Re-run `python analysis/src/margin_build/10_harness_margin/score.py` from clean; confirm every method's `run.py` exits 0 (run them; record
   runtimes and any failure; do not fix them, report).
2. Build `data/processed/margin_build/20_scoreboard/20_scoreboard_master.csv`: per (method, object, spec, target, window, horizon, weighting):
   n, MAE, RMSE, bias, ratio to seasonal_naive, ratio to pct_rev_last4, ratio to street, ratio to guide_implied, 80/90 coverage, CRPS, n_params,
   survives_both_windows, PIT-vs-full_sample gap (hindsight share).
3. `20_rankings.md` section: for adj EBITDA margin and adj EBITDA $ at h=0, h=1, h=2: the ranking in W1, in W2, equal- and recency-weighted;
   which objects survive both windows; per-line rankings for the five cash lines; below-EBITDA objects vs their baselines. Note where
   equal-weighted and recency-weighted rankings disagree and what that says about regime change.
4. `20_error_correlations.csv`: correlation matrix of h=0 margin errors across the surviving objects (by_quarter file), to show which methods are
   diversifying; and a table of each method's error in the shock quarters (2H22, 1Q25-2Q25) vs calm quarters.
5. `20_live_comparison.csv`: every method's LIVE forecast for 3Q26, 4Q26, FY26, 1Q27-4Q27, FY27, FY28 (adj EBITDA $, margin; EPS and FCF where
   supplied), side by side with WS03's current consensus (LSEG, Bloomberg), the management floor, WS31b's three profiles and WS30's walk. Spread
   across methods per quarter (max-min) as a crude model-uncertainty measure.
6. `20_parameter_budget.csv`: parameters per object vs accuracy; flag any object whose recency-weighted W2 win disappears in W1.
7. Note `docs/margin-build/notes/20_scoreboard.md`: bottom line (the three best objects per target and horizon, with the numbers, and whether
   any beats guide_implied and street), the rankings, the disagreements, the LIVE table, a recommended weighting scheme for WS23 (with the
   leave-future-out evidence), open questions for the discussion round (numbered, addressed to specific methods), "For the model", RESUME.
