# M6. Cycle and cost-flex model: how the cost lines respond to revenue growth, and the scenario engine

Margin build run, 13-14 Sep 2026. Slug `M6_cycle_flex`. Registry method `cycle-flex`. Script
`analysis/src/margin_build/M6_cycle_flex/run.py` (`py -3.13`, exit 0). Author: agent M6.

## 0. Pre-registration (written 2026-09-14 before any fit; nothing below this section existed at that time)

**Objects registered.** Two, one per target family, specs inside:

| object | targets | spec_ids |
|---|---|---|
| `flex_margin` | `adj_ebitda_margin_pct`, `adj_ebitda_musd`, `total_cash_costs_musd` | `l0_rw` (**main**), `l0_eq`, `dl_rw`, `revknown_rw` |
| `flex_lines` | `cor_cash_musd`, `ops_cash_musd`, `pd_cash_musd`, `sm_cash_musd`, `ga_cash_ex_reserves_musd` | same four |

Both replays (`PIT`: parameters refit at each vintage; `full_sample`: parameters from the whole history through 2Q26 applied at each
vintage, inputs still PIT). Horizons h=0,1,2 at the 14 W1 guide dates (W2 = the 10-date subset); LIVE h=0..5 at 2026-08-06 and
2026-09-11 (3Q26..4Q27) on the WS06 v2b base revenue path; FY26/27/28 in `M6_cycle_flex_annual_forecasts.csv` with bear/base/bull.

**Model (the "cycle" regression, part A-ii, which is also the registered forecaster).** For cash line L in {cor, ops, pd, sm, ga ex
lodging reserves}, four-quarter log growth on four-quarter log revenue growth:

    g_L,q = c_L + k_L * r_q + e_q                                    (spec l0: lag 0 only; 2 parameters per line)
    g_L,q = c_L + k_L0 r_q + k_L1 r_{q-1} + k_L2 r_{q-2} + e_q      (spec dl: distributed lag; 4 per line)
    g_x,q = log(x_q / x_{q-4}); r_q = log(revenue_q / revenue_{q-4})

Weighted least squares, observation weights 0.5^((T-t)/4) (half-life 4 quarters, T = last printed quarter at the vintage) for `_rw`,
equal for `_eq`. Fit sample: y/y observations from 1Q22 (levels 1Q21 onward, 2020 never a base year). Minimum 4 observations; if a
vintage has fewer, the 2021 observations (2020 base) are added and the row is flagged. Standard errors HAC (Newey-West, 2 lags).
Variants reported in the parameter file but NOT registered: single-lag k at lags 1 and 2; episode dummies (E2 2Q22-1Q23, E3 2Q23-4Q23,
E4 1Q25-4Q25, E5 1Q26-2Q26; baseline 1Q22 and 2024); sample incl. 2021 with an E1 dummy; asymmetry split
g_L = c + k_up * max(r - rbar, 0) + k_dn * min(r - rbar, 0), rbar = trailing-4 mean of r through q-1.

Forecast at a vintage: L_hat_q = L_{q-4} * exp(c_L + k_L * r_hat_q), r_hat_q = log(rev_leg_q / rev_{q-4}) with the frozen harness PIT
revenue leg (`revenue_forecast_pit`: guide-cushion at h=0, naive y[q-4] x (1 + last y/y) beyond). Lagged r in spec dl uses printed
revenue where available, else the same PIT leg. h=4,5 chain on the model's own q-4 forecast. Spec `revknown_rw` substitutes the actual
revenue so the reader can split cost error from revenue error. Adj EBITDA = revenue - sum(lines) + other_net, other_net (D&A and
non-reserve add-backs; an identity in the targets) = trailing-4 share of revenue x revenue (a rule, 1 parameter). Margin = adj EBITDA / revenue.
LIVE rows use the WS06 v2b base revenue path in place of the harness leg (`rev_leg=ws06_v2b_base` in notes), as M1 did.

**Quantiles.** q05..q95 Gaussian on the walk-forward residual pool of the same (spec, target, horizon): PIT = errors of quarters printed
before the vintage (last 12), full_sample = all realised errors; relative errors for $ targets, additive for the margin; LIVE h=3..5 borrow
the h=2 pool; fewer than 3 residuals -> 10 % relative / 3 pp additive, flagged. The model runs at every guide date from 2022-02-15 so the
early W1 vintages have a pool (the harness baseline convention, copied so coverage is comparable).

**Free parameters (registry `n_params` = fitted parameters + 1 other_net rule + 1 residual sd):** `l0_rw`, `l0_eq`, `revknown_rw`: 10 + 1 + 1 = 12.
`dl_rw`: 20 + 1 + 1 = 22. Scenario engine on top: the five k_L (already counted), three cut caps (judgement constants, stated below), one
start-quarter rule, one FY27 target rule.

**Scenario engine (part B), `flex(cost_path_base, revenue_path_scenario, variant)`.** With d_q = log(rev_scen_q / rev_base_q) (zero before 3Q26):
- `held`: every line at its base dollars (k = 0): pure operating leverage. other_net scales with revenue in every variant.
- `flex`: L_scen = L_base * exp(k_L * d_q) with the `l0_rw` k's at TODAY (sub-variant `flex_dl` with the `dl_rw` k's and lags).
- `hold_disc` ("management holds spend"): cor and ops flex with their k; pd, sm, ga held at base dollars.
- `cut` ("management cuts to defend the floor"): start from `flex`; if the FY margin is below the target, cut pd / sm / ga from the NEXT
  quarter (4Q26 at the earliest: at 11 Sep the 3Q26 marketing is committed) by the smallest uniform fraction phi of the caps that restores
  the target, phi in [0, 1]; phi > 1 means the floor is not reachable. Caps per quarter vs base dollars: sm 20 %, pd 10 %, ga 5 %
  (from the FY23 evidence: S&M y/y growth +28.6 % in 2Q23 -> +3.8 % in 3Q23, product development +13.0 % -> +1.6 % in 4Q23, G&A never
  cut more than mid-single digits; and the FY24-25 S&M phasing in WS02/WS05). Targets: FY26 >= 35.5 % (the 2Q26 floor, guide
  `ABNB-2Q26-adj_ebitda_margin_pct-FY2026-190`); FY27 >= 35.0 % (WS05 H01/H12: the FY27 sentence is a floor 0-50 bp below the FY26 print).
Base cost path: M1 `driver-lines` `b_elastic_rw` PIT LIVE base at 2026-09-11 (registered before this run started; file
`M1_driver_lines_live_quarterly.csv`), labelled `base=M1_b_elastic_rw`; the cycle-flex own `l0_rw` base as a cross-check
(`base=M6_l0_rw`); the harness `seasonal_naive_drift` only if the M1 file is missing (it is not).
FY26 floor break-even: the revenue shortfall s (uniform % below base on 3Q26+4Q26, and separately on 4Q26 only) at which FY26 margin = 35.5 %,
by bisection, per variant and base. Seasonal 1Q27 trough: the 1Q27 margin under each variant and scenario.

**Pass lines (pre-registered; four tests, counted at the end of the note):**
- T1 (the prompt's first test): in the single-lag regressions at TODAY (full sample, n = 18 y/y observations 1Q22-2Q26, `_rw` weighting;
  `_eq` reported), k_sm and k_pd are positive with HAC t >= 2.0 at SOME lag in {0, 1, 2}. Both lines must pass.
- T2 (the prompt's second test): the engine fed the ACTUAL revenue path reproduces the 2H22 margin path (3Q22, 4Q22 and 1Q23; base path
  = the model's own forecast at the 2022-08-02 vintage under the PIT revenue leg) within 1.5 pp in every one of the three quarters,
  with the full-sample k's (hindsight, labelled); the PIT-k result is reported alongside and does not decide.
- T3 (harness): `l0_rw` beats `seasonal_naive` on `adj_ebitda_margin_pct` MAE at h=0 on the four 2025 shock quarters (1Q25-4Q25, in both
  windows), PIT replay, equal-weighted (from `scoreboard_by_quarter.csv`). Expectation stated now: it does NOT beat the seasonal naive on
  the full W1/W2 windows (a cycle model is weak in calm quarters); the full-window rows are reported and the flags quoted.
- T4 (asymmetry; reported, no pass line because n = 18): k_dn vs k_up per line with the HAC Wald p-value; the sign of (k_dn - k_up) is
  reported as "costs fall slower than they rise" only if p < 0.10.
Peer comparison (reported): the same lag-0 regression for BKNG and EXPE on LSEG quarterly revenue, total operating expense ex cost of
revenue, SG&A and advertising (WS04 raw pull 13 Sep 2026, licensed, derived k's only), same sample 1Q22-2Q26, `_rw` and `_eq`.

Tests counted at the end of the note. Failed tests stay in the note.

---
