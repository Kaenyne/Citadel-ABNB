# M2 — Time-series and ratio methods for adjusted EBITDA margin and the cost lines (`margin-ts`)

Slug `M2_margin_ts`. Method name in the registry: `margin-ts`. Written 14 Sep 2026 (Sunday, early morning) by the M2 agent.
Code: `analysis/src/margin_build/M2_margin_ts/` (`run.py`, `m2_margin_ts.py`, `README.md`). Data:
`data/processed/margin_build/M2_margin_ts/`. Registry: `data/processed/margin_build/registry/margin-ts__*.csv`.
Interpreter `py -3.13`.

## Pre-registration (written before any fit was run; 14 Sep 2026 ~05:30)

**Targets.** Primary: `adj_ebitda_margin_pct` (pp) and `adj_ebitda_musd` (USD m). Secondary (objects 3-5): the five cash
lines ex-SBC in USD m (`cor/ops/pd/sm/ga_cash_musd`; G&A forecast ex lodging-tax reserves, also registered against
`ga_cash_ex_reserves_musd`), as % of revenue (`*_cash_pct_rev`), per night (`*_cash_per_night`), `total_cash_costs_musd/_pct_rev`.

**Objects (method `margin-ts`) and free parameters (excluding the residual sd, +1 in the registry when fitted).**

| # | object | rule | specs (`spec_id`) | params |
|---|---|---|---|---|
| 1 | `yoy_margin_change` | margin_q = margin_{q-4} + delta; delta = weighted mean of the last k observed y/y margin changes | `k4_rw` (main), `k2_rw`, `k4_ew`, `k2_ew`, `k4_rw_shrink50` (delta x 0.5) | 2 (k, delta); shrink +1 |
| 2 | `incremental_margin` | EBITDA_q = EBITDA_{q-4} + m (Rev_q - Rev_{q-4}); m = weighted mean of the last k y/y incremental margins (pairs with abs(dRev) < 10% of Rev_{q-4} excluded); revenue = frozen-harness PIT leg | `k4_rw` (main), `k8_rw`, `k4_ew`, `k8_ew`, `k8_median`, `k4_rw_revknown` (actual revenue, diagnostic) | 2 (k, m) |
| 3 | `pct_rev_seasonal` | each line % of revenue = same-quarter-last-year ratio + weighted mean of the last k y/y ratio changes; a sixth "other" component (total cash costs minus the five lines, the add-backs, about -0.5% of revenue) at last year's ratio; EBITDA = revenue leg - sum | `drift_k4_rw` (main), `drift_k4_ew`, `drift_k8_rw`, `nodrift`, `drift_k4_rw_revknown` | 6 (5 drifts + k) |
| 4 | `per_night_seasonal` | each line per night = last year's per-night x (1 + weighted mean of the last k y/y per-night growth rates) x nights leg (backtest: nights_{q-4} x (1 + last observed y/y nights growth), chained; LIVE: WS06 nights); "other" per night at last year's value; EBITDA = revenue leg - sum | `g_k4_rw` (main), `g_k4_ew`, `g_k8_rw`, `nogrowth`, `g_k4_rw_nightsknown` | 6 (5 growth rates + k) |
| 5 | `sarima_margin` | statsmodels SARIMAX on the margin (1Q21 onward; 2020 excluded as a fixed choice) and on log of each line; candidates (0,0,0)(0,1,0)4+c, (1,0,0)(0,1,0)4+c, (0,0,0)(0,1,1)4+c, (0,1,1)(0,1,1)4; order chosen by AICc on the training window only, candidates needing more parameters than n_diff-3 excluded; equal weights only (SARIMAX has no observation weights) | `margin_aicc`, `lines_aicc` | up to 3 + 1 (selection) |
| 6 | `ensemble_simple` | mean of the main specs of objects 1-4 on margin and on EBITDA $ | `eq4` (equal), `invmae4` (inverse past PIT MAE at the same horizon, last 8 errors printed before the vintage; equal when fewer than 3) | 0 / 4 |
| 7 | `q_sentence_direction` | margin_q = margin_{q-4} + k x d, d = sign of management's quarterly margin sentence in force (ceiling -1, floor +1, point 0); k fitted PIT as the weighted regression-through-origin of realised y/y changes on d over past sentence quarters (WS10's flagged object) | `k_fit_rw` (main), `k_fit_ew`, `k_fit_median`, `k_abs_rw` (k = weighted mean abs y/y change, last 8 quarters) | 1 (k) |

Recency weights: exponential, half-life 4 quarters, anchored at the latest printed quarter at the vintage (`_rw`); equal weights (`_ew`).
Replays: `PIT` = parameters re-estimated at each vintage from `history_as_of(vintage)`; `full_sample` = the same estimator evaluated
on the full history through 2Q26 (at TODAY) and applied at every vintage, PIT inputs. Quantiles q05-q95: Gaussian on the walk-forward
PIT residual pool of the same object / spec / target / horizon (last 12 errors of quarters printed on or before the vintage; full_sample:
all realised errors; relative for $ levels, additive for ratios; fallback 10% / 3 pp when fewer than 3; LIVE h=3-5 borrow the h=2 pool),
the same convention as the WS10 baselines so coverage is comparable. Vintages: every frozen guide date 2021-11-04 .. 2026-08-06 plus
TODAY = 2026-09-11 (only W1 / W2 / LIVE rows are registered; the 2021-22 vintages feed the residual pools). Horizons h=0,1,2 backtest,
h=0..5 LIVE (3Q26-4Q27; FY28 quarters chained to h=9 for the annual file only).

**Revenue and nights inputs.** Backtests: the frozen-harness PIT revenue leg (`revenue_forecast_pit`: guide-cushion at h=0, naive
beyond), nights naive as above; `_revknown` / `_nightsknown` specs use the actual (diagnostic: how much error is revenue vs cost).
LIVE at TODAY: base / bear / bull from WS06 `06_revenue_path_3q26_4q27.csv` (3Q26 and 4Q26 rows carry bridge v3; `_v2b` used if present),
FY28 base quarters from `06_revenue_path_wide.csv`. LIVE at 2026-08-06: the harness PIT leg (the adopted path post-dates that vintage).

**Pass lines (a claim needs both windows, both weightings).**

- P1 (primary): at least one of objects 1-4 has `mae_ratio_seasonal_naive` < 1 AND `rw_mae_ratio_seasonal_naive` < 1 on
  `adj_ebitda_margin_pct` at h=0 in W1 (n=14) and W2 (n=10).
- P2: the same object also does so at h=1 and h=2.
- P3 (lines): objects 3 and 4 beat `seasonal_naive_drift` (the hardest line baseline) on `{line}_cash_musd` at h=0 in both windows,
  both weightings, for at least 3 of 5 lines.
- P4 (calibration): PIT `cov80` of the main spec on the margin at h=0 lies in [0.60, 0.95] in both windows.
- P5: `ensemble_simple|invmae4` beats `eq4` on margin MAE at h=0 in both windows.
- P6 (sentence rule): `q_sentence_direction|k_fit_rw` beats `seasonal_naive` at h=0 in both windows, both weightings. Stretch: MAE below
  the Street's 1.59 / 1.31 pp (rw 1.25 / 1.12).
- P7 (the bar that matters for the pitch): does any object beat the Street at h=0 in both windows? Expected answer: no. Written up either way.

Test count: every (object, spec) x window x horizon cell on the margin is one test against seasonal naive; the count is reported
in the results section. Nothing is dropped after the fact.
