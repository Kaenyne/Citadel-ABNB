# M1. Driver-based cost lines v2: per-unit costs on the revenue drivers, point-in-time

Margin build run, 13-14 Sep 2026. Slug `M1_driver_lines`. Registry method `driver-lines`. Script
`analysis/src/margin_build/M1_driver_lines/run.py` (`py -3.13`, exit 0). Author: agent M1.

## 0. Pre-registration (written 2026-09-14 before any fit; nothing below this section existed at that time)

**Objects registered.** Two, one per target family, specs inside:

| object | targets | spec_ids |
|---|---|---|
| `margin_v2` | `adj_ebitda_margin_pct`, `adj_ebitda_musd`, `total_cash_costs_musd` | `a_unit_rw`, `a_unit_eq`, `b_elastic_rw` (**main**), `b_elastic_eq`, `c_mix_rw`, `d_steps_rw`, `e_revknown_rw` |
| `lines_v2` | `cor_cash_musd`, `ops_cash_musd`, `pd_cash_musd`, `sm_cash_musd`, `ga_cash_ex_reserves_musd` | same seven |

Both replays (`PIT`, `full_sample`) for every spec; horizons h=0,1,2 at the 14 W1 guide dates (W2 rows are the 10-date subset);
LIVE h=0..5 at 2026-08-06 and 2026-09-11 (3Q26..4Q27) on the WS06 base revenue path; FY26/27/28 in a separate annual CSV with bear/base/bull.

**Model (every spec).** For line L in {cor, ops, pd, sm, ga ex lodging reserves}, in four-quarter log differences (no seasonal dummies,
no intercept; the y/y form is what makes the model fittable at the first W1 vintage, where the 1Q21+ sample gives 4 observations):

    d4 log L_q = g_L + b_L * d4 log D_q + sum_k c_Lk * d4 step_k,q + e_q,     d4 x_q = x_q - x_{q-4}

Driver D: GBV$ for cor, nights for ops, revenue for sm; none for pd and ga (trend only). Observation weights `0.5^((T - t)/4)`
(half-life 4 quarters, T = last printed quarter at the vintage) for `_rw`; equal for `_eq`. Fit sample: y/y observations from 1Q22
(levels 1Q21 onward; 2020 never in the base year) — the "incl. 2020" variant (observations from 1Q21) is reported in the grid table,
not registered. Minimum 4 observations; below that the 2021 observations are added and the row is flagged.

Adj EBITDA = revenue - sum(lines) + other_net, other_net = D&A + non-reserve add-backs (= adj EBITDA - revenue + sum(lines) in the
targets, an identity), forecast as trailing-4 share of revenue x revenue (a rule, counted as 1 parameter). Margin = adj EBITDA / revenue.

Driver inputs at a backtest vintage are point-in-time: revenue = the frozen harness revenue leg (`revenue_forecast_pit`: guide-cushion at
h=0, naive y[q-4] x (1 + last y/y) beyond); nights = nights[q-4] x (revenue growth) / (1 + last printed y/y change in revenue per night);
GBV = GBV[q-4] x (revenue growth) / (1 + last printed y/y change in take rate). h=4,5 chain on the model's own q-4 forecast.
Spec `e_revknown_rw` replaces these with the actual revenue, nights and GBV (oracle drivers) so the reader can split cost error from revenue error.

| spec | b_L | extra terms | fitted params (lines) | n_params in registry (+1 other_net rule, +1 sd) |
|---|---|---|---|---|
| `a_unit` | imposed: cor 1 on GBV, ops 1 on nights, sm/pd/ga 0 (31b-style per-unit trend) | none | 5 (g_L) | 7 |
| `b_elastic` | fitted for cor, ops, sm; pd/ga trend only | none | 8 | 10 |
| `c_mix` | as b | d4 of ex-NA nights share (pp, WS10 `na_nights_share_est_pct`) on cor and ops; forecast by persistence of the last printed d4 share; LIVE from WS06 `na_share_3Q26/4Q26`, then held | 10 | 12 |
| `d_steps` | as b | d4 of step dummies from WS04: E02 (interchange Apr-2022, cor), E09 (hosting re-cut 1Q25, cor), E05 (AI support agent 2Q25, ops), E10 (recruiting cut 1Q23, pd); a step enters only once it has >= 2 post-step observations at the vintage, else its coefficient is 0 | 12 | 14 |
| `e_revknown` | as b, oracle drivers | none | 8 | 10 |

**Quantiles.** q05..q95 Gaussian on the walk-forward residual pool of the same (spec, target, horizon): PIT = errors of quarters printed
before the vintage (last 12), full_sample = all realised errors; relative errors for $ targets, additive for the margin; LIVE h=3..5 borrow
the h=2 pool; fewer than 3 residuals -> 10 % relative / 3 pp additive, flagged. The model runs at every guide date from 2022-02-15 so the
early W1 vintages have a pool. This copies the harness baseline convention exactly so coverage is comparable.

**Pass lines (PIT replay, scorer's `mae_ratio_*` < 1 at the same window, horizon and replay):**

- P1 (primary, the prompt's test): the main spec `b_elastic_rw` beats `seasonal_naive` on `adj_ebitda_margin_pct` MAE at h=0 AND h=1 in W1
  AND W2, equal- AND recency-weighted (8 comparisons; all 8 must hold). `pct_rev_last4` is not defined for the margin ratio in the harness, so
  the second half of the prompt's test is run on `adj_ebitda_musd`:
- P2: `b_elastic_rw` beats `seasonal_naive` AND `pct_rev_last4` on `adj_ebitda_musd` MAE at h=0 and h=1, both windows, both weightings (16 comparisons).
- P3 (reported, not required): vs `street` on the margin at h=0 in W2, recency-weighted (Street is the hardest baseline: 1.31 / 1.12 pp).
- Per line (reported, not a pass line): expectation stated now — cor and ops beat `seasonal_naive` and `pct_rev_last4`; pd, sm, ga do NOT beat
  `pct_rev_last4` materially (discretionary lines). If that expectation fails in either direction it is written up.
- Variant selection: the winning spec is reported with the caveat that choosing among seven specs on the same 14/10 quarters is in-sample
  selection; the pitch spec is chosen by P1/P2 on the pre-named main spec, not by the grid.
- Stability: leave-one-year-out b_L (drop 2022, 2023, 2024, 2025, 2026 in turn) on the full sample; b_L is called stable if the LOYO range is
  inside +/-0.5 of the full-sample value.

Tests counted at the end of the note. Failed tests stay in the note.
