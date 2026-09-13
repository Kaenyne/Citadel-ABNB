# Common rules for every method workstream (M1-M7)

Read `docs/margin-build/00_BRIEF.md`, then `analysis/src/margin_build/10_harness_margin/README.md`, then your own prompt.

1. **Pre-register** in your note, before any fit: the objects you will register, the target metrics, the pass line (e.g. "beats seasonal_naive
   on adj EBITDA margin MAE at h=0 in both W1 and W2, equal- and recency-weighted"), and the free-parameter count per object.
2. **Point-in-time refits.** For every W1 guide date (14) and W2 guide date (10; a subset), fit using only `history_as_of(vintage_date)` and
   inputs whose `knowable_from <= vintage_date`; forecast horizons h=0 (the quarter being guided), h=1, h=2 where the target quarter is inside
   the window. Then the LIVE forecasts from the latest allowed vintage date: 3Q26, 4Q26, 1Q27-4Q27 (h up to 5), plus FY26, FY27, FY28 annual
   in a separate CSV (annuals are not scored by the harness; write them to `data/processed/margin_build/<slug>/<slug>_annual_forecasts.csv`).
3. **Both replays.** Register `prior_basis=PIT` (parameters re-estimated at each vintage) and `prior_basis=full_sample` (parameters from the
   full history, applied at each vintage, to show how much of the accuracy is hindsight). The harness warns if one is missing.
4. **Recency weighting.** Fit with exponentially decaying observation weights (half-life 4 quarters) as your main spec AND equal weights as a
   variant (`spec_id`); the scorer reports both weightings of the error. Say which one you would put in the pitch and why.
5. **Quantiles.** Supply q05, q10, q25, q50, q75, q90, q95 from the PIT residual distribution (or a conformal wrapper); coverage is scored.
6. **Revenue path.** For LIVE forecasts, cost lines are conditional on the adopted revenue path: 3Q26/4Q26 from bridge v3 and 1Q27-4Q27 from
   WS06 (`06_revenue_path_3q26_4q27_v2b.csv` if it exists, else the original). Produce base / bear / bull columns where the revenue path has them.
   For backtests, the revenue input at each vintage must itself be PIT: use the frozen harness `baselines` guide-cushion revenue forecast
   (or the actual, as a separate "revenue-known" spec so the reader sees how much error is revenue vs cost).
7. **Outputs.** `analysis/src/margin_build/<slug>/run.py` (rebuild everything, exit 0) + `README.md`; registry files via the harness;
   `data/processed/margin_build/<slug>/` for everything else; figures under `analysis/figures/margin_build/`; note `docs/margin-build/notes/<slug>.md`
   with: bottom line, pre-registration, method (equations, parameters), backtest table (both windows, both weightings, h=0/1/2, vs every baseline,
   n each), what failed, LIVE forecast table (3Q26, 4Q26, 1Q27-4Q27, FY26-28; adj EBITDA $ and margin; lines) with the consensus and management
   comparison columns from WS03/WS05, "For the model", "For the 5 Nov card", RESUME.
8. Run `python analysis/src/margin_build/10_harness_margin/score.py` after registering and quote the scoreboard rows in your note.
9. You may be messaged later by the orchestrator with the scoreboard and the red-team findings and asked for a short rebuttal or an adjusted
   registration; keep your reasoning in your note so you can answer.
10. Budget: about 2-3 hours. Prefer a finished, honest, small model over an unfinished ambitious one.
