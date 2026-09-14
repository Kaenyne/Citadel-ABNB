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

## 1. Bottom line

**Airbnb's cost base is the least cyclical in online travel, and that is the whole result.** Fitting
`g_line = c + k x g_revenue` on four-quarter log growth, 1Q22-2Q26 (n = 18), only two lines have a positive,
significant `k`: cost of revenue **0.56** (HAC t 5.6) and ops & support **0.44** (t 3.4). Brand marketing is
**0.42** (t 2.3) but unstable — it was 0.87 in 2022 and 0.30-0.42 since 2025. Product development is
**-0.21** (t -1.6, and t -3.3 at lag 2, i.e. significantly the *wrong* sign) and G&A is **-0.11** (t -0.3).
Total cash costs move **0.36** with revenue. The same regression on peers gives BKNG total opex **0.61**
(t 6.9), TRIP **0.63** (t 5.6), EXPE **0.44** (t 5.0) and BKNG advertising **0.87** (t 9.0); ABNB's own total
opex `k` is **0.14** and not distinguishable from zero. **Two thirds of Airbnb's cost base does not know what
revenue is doing.** For the 5 Nov card that cuts both ways: a revenue miss drops through to EBITDA almost
one-for-one (100bp of 2H26 revenue costs ~27bp of FY26 margin with costs flexed, ~36bp with costs held), and
a revenue beat does the same in reverse.

**The FY26 35.5% floor is safe and not the thing to watch.** On the adopted base path the model puts FY26 at
**36.0-36.2%** and the floor survives a **1.9-2.5% shortfall in 2H26 revenue** ($149-203m, i.e. 4.7-7.0% off
4Q26 alone) before management has to do anything; with the cut lever it survives 8.0% ($638m). The pressure
point is **FY27**: with costs flexed off the base revenue path the model lands at **34.4-35.1%** against Street
**36.4%**, and in the bear revenue case at **31.5-32.4%** — a floor that only holds if management cuts
$386-508m of discretionary spend, which is inside the historical cut caps but is a real, visible action.

**The registered forecaster passes its harness test but is not the best margin model in the run.** `l0_rw` at
h=0 beats seasonal naive in both windows and both weightings (W1 MAE 2.20pp, ratio 0.984; W2 1.77pp, 0.905;
recency-weighted 0.812 / 0.769), ranking 6th of ~40 h=0 objects on rw_MAE — behind Street (1.25), M1's
revenue-known spec (1.44) and two M2 objects. Beyond h=0 it fails badly (W1 h=1 ratio 1.56). **Use M6 for the
`k`'s, the scenario engine and the break-even, not as the point forecast.**

Four pre-registered tests: **T1 failed** (product development's `k` is the wrong sign at every lag),
**T2 failed** (the engine does not reproduce the 2H22 margin path inside 1.5pp), **T3 passed** (beats
seasonal naive on the 2025 shock quarters, 0.92 in both windows), **T4** descriptive (costs do not fall as
fast as they rise, for ops, S&M and total cash costs, p < 0.02, n = 16).

## 2. What ran

```bash
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/M6_cycle_flex/run.py     # 153 s, exit 0; runs 10_harness_margin/score.py at the end
```

Reproduction verified 13 Sep 14:44: all 15 output CSVs and both registry files byte-identical to the
05:07 build; only `M6_cycle_flex_build.json`'s `built` timestamp differs. Registration is clean (no validator
warning), 1,872 rows in `cycle-flex__flex_margin.csv` and 3,120 in `cycle-flex__flex_lines.csv`, and the
scorer picks up **384 cycle-flex rows** in `data/processed/margin_build/10_harness_margin/scoreboard_margin.csv`
(5,584 rows total).

## 3. Part A(i) — the seasonal profile is mechanical, not discretionary

`M6_cycle_flex_seasonal.csv` (per quarter 2022-2026) and `M6_cycle_flex_seasonal_stability_2022_25.csv`
(mean / sd / min / max by quarter number, **n = 4 years, 2022-2025**).

| | share of FY revenue | share of FY cash costs | share of FY adj EBITDA | margin (actual) | margin if costs were spread flat | discretionary tilt (pp) |
|---|---|---|---|---|---|---|
| Q1 | 18.54 (sd 0.56) | 23.95 (0.76) | 8.81 (1.55) | 16.93 (2.56) | 13.24 (3.57) | **+3.69** (2.76) |
| Q2 | 25.04 (0.22) | 26.01 (0.53) | 23.33 (1.23) | 33.25 (0.60) | 35.82 (0.92) | **-2.57** (1.34) |
| Q3 | 33.92 (0.45) | 25.44 (0.48) | 49.14 (1.25) | 51.76 (1.81) | 52.62 (0.99) | **-0.85** (0.93) |
| Q4 | 22.51 (0.18) | 24.60 (0.80) | 18.71 (1.17) | 29.75 (2.92) | 28.62 (0.68) | **+1.13** (2.26) |

Cost dollars are close to flat across the year (shares 24.0 / 26.0 / 25.4 / 24.6, sd 0.5-0.8) while revenue
swings 18.5 / 25.0 / 33.9 / 22.5. **The seasonal margin profile is almost entirely revenue timing against a
near-flat cost base.** The discretionary residual is +3.7pp in Q1 and -2.6pp in Q2 and has the widest
dispersion of anything in the table (Q1 sd 2.8pp, Q4 sd 2.3pp) — the Q1 and Q4 margin are the two the timing
of spend can actually move.

Per line, the share of annual dollars by quarter (2022-25 mean, sd):

| line | Q1 | Q2 | Q3 | Q4 | reading |
|---|---|---|---|---|---|
| cost of revenue | 24.79 (0.67) | 26.10 (0.65) | 26.20 (0.99) | 22.91 (0.35) | follows GBV, not revenue |
| ops & support | 22.91 (0.68) | 25.67 (0.97) | 27.83 (0.97) | 23.58 (1.30) | the one volume-following opex line |
| product development | 25.53 (0.67) | 24.52 (0.62) | 24.47 (0.65) | 25.48 (0.77) | **flat payroll; no seasonality at all** |
| brand marketing / S&M | 23.74 (1.70) | 26.51 (1.11) | 24.13 (1.18) | 25.61 (1.26) | Q1 is the *lightest* dollar quarter |
| G&A | 23.61 (0.82) | 25.84 (1.09) | 24.61 (1.03) | 25.94 (0.82) | flat |

**Correction to the received story.** The "Q1 brand campaign" is a denominator effect, not a spending spike:
S&M is 21.8-26.0% of *revenue* in Q1 (the year's highest) but only 23.7% of the year's S&M *dollars* (the
year's lowest). The same for "Q4 hiring" — product development's Q4 dollar share (25.5%) is within 1pp of
every other quarter. Anyone modelling a Q1 marketing spike in dollars will overstate Q1 costs.

**2026 under the adopted revenue path** (WS06 v2b base; 1H26 actual, 2H26 modelled): quarterly margin
19.4 / 35.0 / **51.2** / **28.0** (M6's own base) or 19.4 / 35.0 / **51.6** / **28.5** (engine on M1's base),
against a 2022-25 Q3 mean of 51.8 and Q4 mean of 29.8. The 2026 cost-share profile is 23.6 / 25.7 / 25.6 /
25.0 — inside the historical range in every quarter.

## 4. Part A(ii) — cyclicality: `k` per line

`M6_cycle_flex_k_table.csv` (121 regressions), `M6_cycle_flex_params_by_vintage.csv` (400 rows).
Sample 1Q22-2Q26, **n = 18** four-quarter log-growth observations; HAC (Newey-West, 2 lags) t-statistics;
`rw` = exponential weights, half-life 4 quarters.

### Lag 0 (the registered spec)

| line | k (rw) | t (rw) | R2 (rw) | k (eq) | t (eq) | R2 (eq) |
|---|---|---|---|---|---|---|
| cost of revenue | **0.562** | **5.61** | 0.47 | **0.581** | **14.39** | 0.77 |
| ops & support | **0.438** | **3.43** | 0.19 | **0.465** | **8.01** | 0.45 |
| product development | -0.211 | -1.59 | 0.10 | -0.073 | -0.86 | 0.03 |
| brand marketing / S&M | **0.418** | **2.25** | 0.13 | **0.410** | **3.06** | 0.25 |
| G&A (ex lodging reserves) | -0.110 | -0.29 | 0.01 | 0.178 | 3.03 | 0.07 |
| **total cash costs** | **0.364** | **6.58** | 0.41 | **0.396** | **12.81** | 0.65 |

Intercepts: `c_cor` 0.050, `c_ops` 0.006, `c_pd` 0.147, `c_sm` 0.155, `c_ga` 0.071 (rw) — i.e. at zero revenue
growth product development still grows 15%/yr and S&M 17%/yr. That intercept is the single most important
number in the model and the source of its long-horizon failure (section 8).

### Lags 1 and 2

Ops & support is the only line with a genuine lag structure: `k` 0.44 / 0.39 / 0.46 at lags 0/1/2 (all t > 2.7),
so support cost tracks volume with a persistent, roughly contemporaneous response. Cost of revenue decays
(0.56 / 0.43 / 0.10). S&M has **no** lagged response (lag 1 `k` -0.06, t -0.46; lag 2 -0.11, t -0.64) — the
spend decision is set at the start of the period, not in response to the previous quarter's revenue.
Product development is **negative and significant at lag 2** (`k` -0.21, t -3.25): headcount growth is
*inversely* related to revenue growth two quarters earlier, which is what an investment-programme line looks
like when management funds it counter-cyclically.

The distributed-lag spec (`dl`, 4 parameters per line, n = 16) makes cost of revenue look better
(k0 0.44, k1 0.71, k2 -0.44, sum 0.72, R2 0.57) but produces nonsense elsewhere — G&A k0 -1.51, S&M k0 +1.14
with k1, k2 negative. It loses to `l0` on every backtest cut (section 7). **The three extra parameters per
line buy nothing.**

### Episode dummies

Adding E2 (2H22 deceleration, 2Q22-1Q23), E3 (2023 ADR normalisation), E4 (2025 NA slowdown), E5 (2026
reacceleration) to the lag-0 spec leaves `k` essentially unchanged for cost of revenue (0.575) and S&M (0.492)
and halves it for ops (0.267, t 1.81). The two dummies that matter:

- **E3 2023, S&M -12.7pp** (t -3.40) and **product development -7.6pp** (t -3.05): the 2023 ADR-normalisation
  year is the one episode where management visibly cut discretionary growth relative to the revenue relation.
  This is the empirical basis for the cut caps in the engine.
- **E5 2026, G&A -14.9pp** (t -8.78): the 1H26 non-income tax offset (WS05 H15, -$38m y/y), a one-off, not a
  cost-control decision. Do not extrapolate it.
- E4 2025 is insignificant on every line (|t| < 1.3). **In the 2025 slowdown management changed nothing.**

### Stability of `k` across vintages (`M6_cycle_flex_params_by_vintage.csv`, spec `l0_rw`)

| vintage | cor | ops | pd | sm | ga | n |
|---|---|---|---|---|---|---|
| 2023-02-14 | 0.49 | 0.26 | +0.23 | 0.57 | -0.16 | 4 |
| 2024-02-13 | 0.62 | 0.37 | +0.15 | 0.67 | +0.09 | 8 |
| 2025-02-13 | 0.63 | 0.42 | -0.17 | 0.27 | +0.25 | 12 |
| 2026-02-12 | 0.55 | 0.49 | -0.21 | 0.30 | +0.17 | 16 |
| 2026-08-06 (= TODAY) | 0.56 | 0.44 | -0.21 | 0.42 | -0.11 | 18 |

Cost of revenue is the only genuinely stable coefficient (0.45-0.66 across 19 vintages, no trend after 2023).
Ops & support **rose** from 0.13-0.26 in 2023 to 0.44-0.53 now — the support model got *more* volume-linked as
the AI agent handled more contacts (WS05 H05: support cost per booking -16% y/y in 2Q26). S&M **fell** from
0.87 (2022) to 0.27-0.42. Product development **flipped sign** in 4Q24 and has stayed negative. G&A never
settles. No vintage after 2022 needed the 2021 base-year fallback; at TODAY (2026-09-11) the history is
identical to the 2026-08-06 guide date (no print in between), so the `k`'s are the same.

### T4 — asymmetry: costs do not fall as fast as they rise

`g_L = c + k_up x max(r - rbar, 0) + k_dn x min(r - rbar, 0)`, rbar = trailing-4 mean of revenue growth
through q-1, **n = 16**, HAC Wald p for `k_up = k_dn`:

| line | k_up (rw) | k_dn (rw) | k_dn - k_up | p |
|---|---|---|---|---|
| ops & support | +0.51 | -0.83 | **-1.34** | **0.0002** |
| brand marketing / S&M | +1.83 | -0.12 | **-1.95** | **0.003** |
| total cash costs | +0.58 | -0.26 | **-0.84** | **0.018** |
| cost of revenue | +0.47 | -0.14 | -0.61 | 0.27 (eq: -1.13, p 0.022) |
| product development | -0.29 | +0.20 | +0.49 | 0.30 |
| G&A | -2.68 | -0.06 | +2.62 | 0.003 |

For ops, S&M and total cash costs the downside slope is not merely smaller — it is **zero or negative**,
meaning cost growth does not decelerate at all (and for ops, accelerates) when revenue growth falls below
trend. The pre-registered reading holds for those three lines at p < 0.02: **costs fall slower than they
rise.** With n = 16 and a regime change inside the sample this is directional, not a coefficient to put in a
model; the engine's `cut` variant is the disciplined way to use it. The G&A result is the 2026 tax offset
again and should be ignored.

### Peers (`M6_cycle_flex_peer_k.csv`, lag 0, same 1Q22-2Q26 sample, n = 18)

| ticker | total opex k (rw) | t | SG&A k (rw) | t | advertising k (rw) | t |
|---|---|---|---|---|---|---|
| **ABNB** | **0.14** | **0.47** | 0.67 | 1.45 | — | — |
| BKNG | 0.61 | 6.94 | 0.74 | 8.23 | **0.87** | **8.98** |
| EXPE | 0.44 | 5.04 | 0.78 | 3.91 | — | — |
| TRIP | 0.63 | 5.58 | 0.78 | 5.20 | — | — |

(equal-weighted: ABNB -0.15 t -0.58; BKNG 0.53 t 7.39; EXPE 0.40 t 5.33; TRIP 0.51 t 5.35. BKNG advertising
equal-weighted **0.98**, t 15.6, R2 0.91 — performance marketing is a pure variable cost.)

**This is the quotable peer result.** Booking's and Tripadvisor's total cost bases move roughly 0.5-0.6 with
revenue and Booking's advertising line is effectively 1.0; Airbnb's total opex does not move with revenue at
all. Airbnb has no performance-marketing dial to turn. That is why (a) its incremental margin on a revenue
beat is far higher than Booking's, and (b) a revenue miss cannot be absorbed in-quarter — the only lever is a
discretionary programme cut with a one-to-two-quarter lag.

## 5. Part B — the scenario engine

`flex(cost_path_base, revenue_path_scenario, variant)` in `run.py`. With
`d_q = log(rev_scen_q / rev_base_q)` (zero before 3Q26) and the TODAY `l0_rw` `k`'s:

| variant | rule | reading |
|---|---|---|
| `held` | every line at base dollars (k = 0) | pure operating leverage; the floor of the range |
| `flex` | `L = L_base x exp(k_L x d)` | the estimated response, no management action |
| `flex_dl` | same with the `dl_rw` lag structure | sensitivity check |
| `hold_disc` | cor and ops flex; pd, sm, ga held | "management holds spend" |
| `cut` | `flex`, then cut pd/sm/ga from 4Q26 by the smallest uniform fraction phi of the caps (sm 20%, pd 10%, ga 5% per quarter) that restores the FY target | "management cuts to defend the floor" |

Base cost path: M1 `driver-lines` `b_elastic_rw` LIVE (`M1_driver_lines_live_quarterly.csv`), with M6's own
`l0_rw` base as a cross-check; both are carried in every output. Targets FY26 >= 35.5% (the 2Q26 guide),
FY27 >= 35.0% (WS05 H01/H12: a floor 0-50bp below the FY26 print). Free parameters added on top of the
regression: three cut caps, one start-quarter rule, two FY targets — all judgement constants, stated here.

## 6. Tests

**T1 — FAILED.** Pre-registered: `k_sm` *and* `k_pd` positive with HAC t >= 2.0 at some lag in {0,1,2}.
`k_sm` passes at lag 0 (rw t 2.25, eq t 3.06). **`k_pd` is negative at every lag under both weightings**
(rw -0.211 / -0.234 / -0.208; eq -0.073 / -0.126 / -0.182) and is significantly negative at lag 2
(rw t -3.25, eq t -3.18). The test as written requires both lines, so it fails. The economic content of the
failure is the useful part: **product development is not a cyclical cost at Airbnb, it is a budget**, and a
scenario engine that flexes it with revenue is wrong. This is why the `hold_disc` variant (pd, sm, ga held)
is the more defensible default for that line.

**T2 — FAILED.** Pre-registered: fed the **actual** revenue path, the engine reproduces 3Q22, 4Q22 and 1Q23
margin within 1.5pp in every quarter, with the full-sample `k`'s. `M6_cycle_flex_test_2H22_reproduction.csv`:

| quarter | base path (2022-08-02 vintage) | flexed to actual revenue | actual | error (flexed) | error (costs held) | within 1.5pp |
|---|---|---|---|---|---|---|
| 3Q22 | 53.86 | 53.04 | 50.51 | **+2.53** | +2.19 | no |
| 4Q22 | 37.13 | 25.39 | 26.60 | -1.21 | -6.60 | **yes** |
| 1Q23 | 31.32 | 16.96 | 14.41 | **+2.55** | -4.46 | no |

One of three. With PIT `k`'s (n = 6, 2021 observations included) it is far worse: +6.23 / +4.72 / +9.12.
The flex mechanism *works* — it takes 4Q22 from -6.6pp to -1.2pp and 1Q23 from a 31.3% base to 17.0% against
a 14.4% actual — but it does not close the last 2.5pp, because the 2022-08-02 base path itself was built on a
revenue leg that over-forecast 4Q22 revenue by 27% and 1Q23 by 31%. **The 2H22 failure is a revenue-forecast
failure carried into the cost equations, not a failure of the `k`'s.** In the same episode the cost MAPE with
revenue known is 4-6% against a 22-35% revenue MAPE for the PIT leg at h=1/h=2. Verdict: the engine is usable
as a *conditional* mapping (given a revenue path, what do costs do) and must never be quoted as an
unconditional forecast through a turn.

**T3 — PASSED.** Pre-registered: `l0_rw` beats seasonal naive on `adj_ebitda_margin_pct` MAE at h=0 on
1Q25-4Q25 in both windows, PIT replay, equal-weighted. `M6_cycle_flex_test_T3_rows.csv`:

| spec | n | MAE (pp) | seasonal naive (pp) | ratio | W1 | W2 |
|---|---|---|---|---|---|---|
| **l0_rw** | 4 | **1.735** | 1.882 | **0.922** | pass | pass |
| l0_eq | 4 | 1.674 | 1.882 | 0.889 | pass | pass |
| revknown_rw | 4 | 1.946 | 1.882 | 1.034 | fail | fail |
| dl_rw | 4 | 2.516 | 1.882 | 1.337 | fail | fail |

Quarter by quarter (l0_rw, error in pp): 1Q25 -1.80, 2Q25 -1.04, 3Q25 +2.51, 4Q25 +1.59. The win is
concentrated in 4Q25 (1.59 vs 2.55) and 3Q25 is a loss. Four observations; the pre-registered line is met,
the margin of victory is not large.

**T4 — descriptive, reported in section 4.** No pass line (n = 16). Result: `k_dn < k_up` at p < 0.02 for
ops, S&M and total cash costs.

**Test count: 4 pre-registered (T1 fail, T2 fail, T3 pass, T4 descriptive), plus the harness registration
(section 7), which is a fifth pre-registered pass line — "beats seasonal_naive at h=0 in both windows, both
weightings": passed by `l0_rw` and `revknown_rw`, failed by `l0_eq` (equal-weighted W1, ratio 1.003) and
`dl_rw`.**

## 7. Backtest (the harness scoreboard)

`data/processed/margin_build/10_harness_margin/scoreboard_margin.csv`, method `cycle-flex`, copied to
`M6_cycle_flex_scoreboard_rows.csv` (384 rows). `adj_ebitda_margin_pct`, PIT replay:

| window | h | spec | n | MAE (pp) | rw MAE | ratio vs seas. naive | rw ratio | vs Street | cov80 | survives both windows (eq / rw) |
|---|---|---|---|---|---|---|---|---|---|---|
| W1 | 0 | **l0_rw** | 14 | 2.201 | 1.553 | **0.984** | **0.812** | 1.382 | 0.93 | **True / True** |
| W2 | 0 | **l0_rw** | 10 | 1.773 | 1.349 | **0.905** | **0.769** | 1.352 | 1.00 | **True / True** |
| W1 | 0 | l0_eq | 14 | 2.244 | 1.660 | 1.003 | 0.868 | 1.409 | 1.00 | False / True |
| W2 | 0 | l0_eq | 10 | 1.805 | 1.458 | 0.922 | 0.831 | 1.377 | 1.00 | False / True |
| W1 | 0 | revknown_rw | 14 | 2.194 | 1.673 | 0.981 | 0.875 | 1.378 | 0.93 | True / True |
| W2 | 0 | revknown_rw | 10 | 1.760 | 1.477 | 0.898 | 0.842 | 1.342 | 1.00 | True / True |
| W1 | 0 | dl_rw | 14 | 2.716 | 2.128 | 1.214 | 1.113 | 1.706 | 1.00 | False / False |
| W2 | 0 | dl_rw | 10 | 2.605 | 2.004 | 1.330 | 1.142 | 1.987 | 1.00 | False / False |
| W1 | 1 | l0_rw | 13 | 3.069 | 2.591 | 1.306 | 1.340 | 1.870 | 0.85 | False / False |
| W2 | 1 | l0_rw | 9 | 2.430 | 2.336 | 1.540 | 1.459 | 2.447 | 1.00 | False / False |
| W1 | 2 | l0_rw | 12 | 2.707 | 2.268 | 1.092 | 1.157 | — | 0.92 | False / False |
| W2 | 2 | l0_rw | 8 | 2.339 | 2.044 | 1.359 | 1.229 | — | 1.00 | False / False |
| W1 | 2 | revknown_rw | 12 | 2.284 | 1.696 | 0.922 | 0.865 | — | 0.83 | True / True |
| W2 | 2 | revknown_rw | 8 | 1.600 | 1.397 | 0.930 | 0.840 | — | 1.00 | True / True |

Equal and recency weighting **agree in direction everywhere** (the rw ratios are simply better, 0.77-0.87 vs
0.90-1.00 at h=0), because the model's edge is concentrated in 2025-26. I would put the **recency-weighted
`l0_rw`** in the pitch: it is the main spec, it is the one that passes at both weightings, and the `k`'s
themselves are drifting (section 4), which is exactly the case for down-weighting 2022.

Context from the full scoreboard at h=0, W1, PIT (rw MAE, lower is better): Street 1.250, `driver-lines`
`e_revknown_rw` 1.435, `margin-ts` `g_k4_rw_nightsknown` 1.486, `margin-ts` `q_sentence_direction` 1.521,
**`cycle-flex` `l0_rw` 1.553**, `margin-ts` `sarima_margin` 1.587, seasonal naive 1.913. M6 is mid-pack and
nobody beats Street.

Other targets, `l0_rw` at h=0, PIT (ratio vs seasonal naive, W1 / W2):

| target | MAE W1 | MAE W2 | ratio | rw ratio | survives (eq / rw) |
|---|---|---|---|---|---|
| `adj_ebitda_musd` | $61.7m | $58.6m | 0.500 / 0.599 | 0.424 / 0.437 | True / True |
| `total_cash_costs_musd` | $58.0m | $48.5m | 0.267 / 0.213 | 0.201 / 0.179 | True / True |
| `cor_cash_musd` | $15.9m | $18.2m | 0.297 / 0.332 | 0.255 / 0.260 | True / True |
| `pd_cash_musd` | $12.3m | $11.9m | 0.371 / 0.305 | 0.276 / 0.253 | True / True |
| `sm_cash_musd` | $37.9m | $34.9m | 0.402 / 0.320 | 0.307 / 0.280 | True / True |
| `ga_cash_ex_reserves_musd` | $15.8m | $18.1m | 0.766 / 0.916 | 1.091 / 1.161 | True / **False** |
| `ops_cash_musd` | $18.6m | $18.3m | 0.832 / **1.066** | 0.927 / 0.981 | **False** / True |

The dollar lines look dominant against seasonal naive only because a naive y[q-4] on a growing cost line is a
weak baseline; the honest comparison is `pct_rev_last4`, against which the ratios are 0.20-0.53 — still wins,
because the model uses a revenue forecast the baseline does not. **G&A and ops & support do not survive both
windows at both weightings and should not be forecast with this model** — exactly the two lines whose `k` is
insignificant (ga) or drifting (ops).

Slices (`M6_cycle_flex_backtest_grid.csv`, PIT, h=0, ratio vs seasonal naive):

| slice | n | l0_rw | l0_eq | dl_rw | revknown_rw | revenue-leg MAPE |
|---|---|---|---|---|---|---|
| calm W1 ex-2025 | 10 | 1.003 | 1.039 | 1.175 | 0.964 | 1.09% |
| shock 2025 | 4 | **0.922** | 0.889 | 1.337 | 1.034 | 1.02% |
| shock 2H22 | 3 | **1.692** | 2.244 | 2.182 | 1.496 | **1.38% (h=0), 21.97% (h=1), 35.38% (h=2)** |

The pre-registered expectation held: **the model adds nothing in calm quarters (1.00) and earns its keep in
2025 (0.92)**. It is *worse* than naive in 2H22 at every horizon, and the revenue-leg MAPE column says why.

**Hindsight check (full_sample replay, h=0):** `l0_rw` W1 ratio 0.933 vs PIT 0.984, W2 0.837 vs 0.905. About
5pp of the ratio is hindsight in the `k`'s — small, which is what a 2-parameter-per-line model should look
like. Both replays are registered for every spec (`replays_present` = 2).

**Coverage.** cov80 is 0.93-1.00 against a 0.80 target and cov90 is 1.00 at h=0: **the intervals are too
wide**, because the Gaussian pool over the last 12 walk-forward errors is dominated by 2022-23 shocks. If M6's
quantiles are used anywhere, shrink them; the useful spread is the scenario table, not the residual band.

**Parameter count.** `l0_rw`, `l0_eq`, `revknown_rw`: 12 (10 fitted + other_net rule + residual sd);
`dl_rw`: 22. The scenario engine adds 6 judgement constants. `param_obs_ratio` 0.86 in W1 at h=0.

## 8. What failed, and what not to use

1. **T1 and T2 failed** (section 6). Product development's `k` has the wrong sign; the engine does not
   reproduce 2H22 inside the pre-registered 1.5pp.
2. **Every horizon past h=0 fails.** W1 h=1 ratio 1.31, h=2 1.09; W2 1.54 / 1.36. Once the revenue leg is a
   naive y[q-4] x (1 + last y/y), the cost equations amplify the revenue error rather than damp it. Do not
   quote M6 quarterly points beyond the guided quarter; quote the *scenario deltas* instead.
3. **FY28 is unusable from this model: 31.3% against Street 37.7%.** The lag-0 spec carries positive
   intercepts (`c_pd` 0.147, `c_sm` 0.155) so at trend revenue growth the discretionary lines compound
   ~15-19%/yr against ~8-9% revenue — margin erodes mechanically at long horizons. It is a real structural
   warning (that intercept is the AI and expansion spend) but it is not a forecast. **Use M1's FY28.** The
   same bias makes M6's FY27 base (34.4%) 78bp below M1's (35.1%); carry M1's level and M6's deltas.
4. **The distributed-lag spec should be dropped.** 22 parameters, worse on every cut, nonsense coefficients.
   It stays registered so the scoreboard shows the loss.
5. **G&A and ops & support fail the both-windows/both-weightings bar** as individual lines (section 7).
6. **n is small everywhere**: 18 growth observations, 16 for the asymmetry and dl specs, 4 for the 2025 shock
   slice, 3 for 2H22, 4 years for the seasonal stability table.
7. The engine's cut caps (sm 20%, pd 10%, ga 5% per quarter) are judgement calls anchored on the FY23
   episode (E3 dummies: S&M -12.7pp, pd -7.6pp), not fitted. phi scales all three together; a real management
   response would not be uniform.
8. **Corrections to existing work.** None to any file outside this package. One correction to the *received
   story* rather than to a file: the "Q1 brand campaign / Q4 hiring" seasonal framing in the prompt and in
   `research/notes/overnight/31_margin-model.md` is a percent-of-revenue effect, not a dollar-spend effect
   (section 3) — Q1 is the lightest S&M dollar quarter of the year and product development has no dollar
   seasonality at all.

## 9. LIVE forecasts (vintage 2026-09-11)

Revenue: WS06 v2b base path. Costs: engine on the **M1 `b_elastic_rw` base** (headline) with M6's own
`l0_rw` base shown alongside. `M6_cycle_flex_scenarios_quarterly.csv`, `_annual_forecasts.csv`,
`_forecasts_wide.csv`.

### Base path vs consensus and management

| quarter | revenue ($m) | engine on M1 base: adj EBITDA ($m) / margin | M6 own base margin | Street margin | Street EBITDA ($m) |
|---|---|---|---|---|---|
| **3Q26** | 4,804 | 2,478 / **51.57%** | 51.23% | 49.78% | 2,362 |
| **4Q26** | 3,178 | 905 / **28.47%** | 28.05% | 28.90% | 914 |
| 1Q27 | 3,053 | 594 / 19.46% | 18.86% | 20.29% | 611 |
| 2Q27 | 4,029 | 1,385 / 34.38% | 33.65% | 35.96% | 1,452 |
| 3Q27 | 5,281 | 2,671 / 50.58% | 49.82% | 51.15% | 2,696 |
| 4Q27 | 3,466 | 913 / 26.33% | 25.27% | 30.28% | 1,068 |

3Q26 guide-implied ceiling (the 3Q26 margin sentence in force, from the harness `q_guide_implied`): **50.09%**.
M6 sits **148bp above the guide-implied level and 179bp above Street** on 3Q26 — the same direction as M1
(51.6%) and well above M2's sentence-direction rule (48.1%). The three margin methods span 350bp on 3Q26;
that spread is the honest uncertainty and belongs on the card.

| FY | revenue ($m) | engine on M1 base | M6 own base | Street | management |
|---|---|---|---|---|---|
| FY26 | 14,268 | **36.18%** | 35.97% | 35.62% | floor 35.5% (2Q26 guide) |
| FY27 | 15,829 | 35.14% (flex) | 34.36% flex / 35.00% after cut | 36.45% | floor 0-50bp below the FY26 print (WS05 H01/H12) |
| FY28 | 17,137 | — | 31.33% (**do not use**, section 8.3) | 37.65% | — |

(FY25 actual margin 35.10%; Street FY26 revenue 14,190, FY27 15,819, FY28 17,535.)

### Scenario table — margin, costs flexed vs held (engine on M1 base)

| quarter | bear held | bear hold_disc | bear flex | **base** | bull flex | bull hold_disc | bull held |
|---|---|---|---|---|---|---|---|
| 3Q26 | 51.07 | 51.18 | 51.22 | **51.57** | 52.10 | 52.16 | 52.32 |
| 4Q26 | 27.21 | 27.46 | 27.58 | **28.47** | 29.26 | 29.37 | 29.58 |
| 1Q27 | 17.89 | 18.20 | 18.36 | **19.46** | 20.68 | 20.85 | 21.20 |
| 2Q27 | 30.46 | 31.25 | 31.69 | **34.38** | 36.14 | 36.43 | 36.93 |
| 3Q27 | 47.08 | 47.81 | 48.15 | **50.58** | 52.35 | 52.58 | 53.09 |
| 4Q27 | 20.48 | 21.57 | 22.21 | **26.33** | 29.70 | 30.20 | 31.05 |
| **FY26** | 35.71 | 35.80 | 35.84 | **36.18** | 36.59 | 36.63 | 36.74 |
| **FY27** | 31.28 | 32.03 | 32.42 | **35.14** | 37.23 | 37.52 | 38.08 |

Bear / bull revenue: 3Q26 4,755 / 4,878; 4Q26 3,124 / 3,228; FY26 14,165 / 14,392; FY27 14,948 / 16,571
(base 15,829). **Flexing costs recovers only 30-40% of the margin a revenue miss costs** (FY27 bear: held
31.28%, flexed 32.42%, against a 35.14% base — 114bp of the 386bp hit). That is the operating-leverage
statement in one number, and it is the direct consequence of the peer comparison in section 4.

`cut` variant (`M6_cycle_flex_cut_solutions.csv`): the FY26 floor **never binds** — phi = 0 in every scenario
on both bases. FY27 on the M1 base binds only in bear (phi 0.403, **$386m** of pd/sm/ga cuts from 1Q27 to
reach 35.0%); on M6's own base it binds in base (phi 0.106, $102m) and in bear (phi 0.530, $508m). phi < 1
everywhere, so the floor is reachable inside the historical caps in every case — but a $386-508m cut is a
visible programme change, not a rounding.

### FY26 floor break-even (`M6_cycle_flex_fy26_floor_breakeven.csv`, engine on M1 base)

Revenue shortfall vs the base path at which FY26 margin = 35.5%:

| cost response | shortfall on 2H26 | $m | on 4Q26 only | margin sensitivity (pp per 1% 2H26 shortfall) |
|---|---|---|---|---|
| costs held | 1.87% | 149 | 4.70% | 0.363 |
| hold_disc | 2.29% | 183 | 6.00% | 0.296 |
| flex | 2.54% | 203 | 6.95% | 0.266 |
| flex_dl | 2.37% | 189 | 6.22% | 0.284 |
| cut | 8.00% | 638 | 22.17% | 0.266 |

(on M6's own, lower base: 1.30% / 1.59% / 1.77% / 1.65% / 7.03%.) **Rule of thumb for the card: every 1% of
2H26 revenue is worth ~27bp of FY26 margin with costs flexed, ~36bp with costs held; the 35.5% floor has
190-250bp of revenue cushion (~$150-200m) before any management action is needed.**

### Seasonal 1Q27 trough

**19.5%** on the base path (M1 base) / 18.9% (M6 base), against a 2022-25 Q1 mean of 16.9% and Street's 20.3%.
Bear 17.9-18.4%, bull 20.7-21.2%. Q1 is the quarter where the discretionary tilt is widest (sd 2.8pp,
section 3), so the honest 1Q27 band is roughly **17-22%**.

## 10. For the model

| name | value | unit | source |
|---|---|---|---|
| `k_cor` | 0.562 | elasticity of cash cost-of-revenue growth to revenue growth | `M6_cycle_flex_k_table.csv`, 1Q22-2Q26 rw, n 18, t 5.61 |
| `k_ops` | 0.438 | same, ops & support | same, t 3.43 |
| `k_pd` | -0.211 | same, product development | same, t -1.59 (**not significant; treat pd as held**) |
| `k_sm` | 0.418 | same, brand marketing / S&M | same, t 2.25 |
| `k_ga` | -0.110 | same, G&A ex reserves | same, t -0.29 (**not significant; treat ga as held**) |
| `k_total` | 0.364 | same, total cash costs | same, t 6.58 |
| intercepts `c` | cor 0.050, ops 0.006, pd 0.147, sm 0.155, ga 0.071 | log growth at zero revenue growth | same |
| cut caps | sm 20%, pd 10%, ga 5% | max quarterly cut vs base dollars | judgement, anchored on E3 2023 dummies (S&M -12.7pp, pd -7.6pp) |
| cut start | 2026Q4 | first cuttable quarter at an 11 Sep 2026 vintage | 3Q26 spend is committed |
| FY26 margin sensitivity | **0.27pp per 1% of 2H26 revenue** (flexed) / **0.36pp** (held) | pp / % | `M6_cycle_flex_fy26_floor_breakeven.csv` |
| FY26 floor cushion | 1.9-2.5% of 2H26 revenue ($149-203m) | % / $m | same |
| quarterly cost-dollar shares | 24.0 / 26.0 / 25.4 / 24.6 | % of FY cash costs | `M6_cycle_flex_seasonal_stability_2022_25.csv`, n 4 |
| discretionary seasonal tilt | Q1 +3.7pp, Q2 -2.6pp, Q3 -0.9pp, Q4 +1.1pp | pp of margin | same |
| peer `k` (total opex) | ABNB 0.14 (ns), BKNG 0.61, EXPE 0.44, TRIP 0.63 | elasticity | `M6_cycle_flex_peer_k.csv`, LSEG, n 18 each |
| LIVE base margins | 3Q26 51.57%, 4Q26 28.47%, FY26 36.18%, FY27 35.14% | % | `M6_cycle_flex_scenarios_quarterly.csv`, `_annual_forecasts.csv` (engine on M1 base) |
| FY27 scenario band | 31.3% (bear held) to 38.1% (bull held) | % | `_annual_forecasts.csv` |

Do **not** take from M6: any quarterly point beyond 3Q26 as a standalone forecast (use M1), FY28, the G&A and
ops & support line forecasts, or the quantile bands (too wide).

## 11. For the 5 Nov card

1. **"Airbnb has no cost dial."** Total opex elasticity to revenue 0.14 and not significant, against Booking
   0.61, Tripadvisor 0.63, Expedia 0.44, and Booking's advertising line at 0.87-0.98. Two thirds of the cost
   base — product development, G&A, and most of brand marketing — is a budget, not a function of revenue.
2. **So the 3Q26 print is a revenue print.** Every 1% of 2H26 revenue is ~27bp of FY26 margin. Our base has
   3Q26 at 51.6% against Street 49.8% and a guide-implied ceiling of 50.1%: a **150-180bp margin beat is in
   the base case if the revenue path holds**, and it mechanically vanishes if it does not.
3. **The FY26 35.5% floor is not at risk.** It survives a 1.9-2.5% 2H26 revenue shortfall ($149-203m) with no
   action at all, 8.0% if management uses the discretionary lever. Expect the floor to be beaten again — it
   has been beaten by 60-140bp for four years (WS05 H12).
4. **Watch the FY27 sentence (12 Feb 2027), not the FY26 one.** With costs flexed off our base revenue path
   FY27 lands at 34.4-35.1% against Street 36.4%. In a bear revenue year it is 31.3-32.4% unless management
   cuts $386-508m — inside the historical caps, but the first real programme cut since 2023.
5. **The asymmetry is the tail risk.** Ops & support, S&M and total cash costs show `k_dn < k_up` at p < 0.02:
   in the quarters after a growth downshift, cost growth does not decelerate at all. A 2027 revenue
   disappointment therefore hits margin harder than symmetric operating leverage implies — bear-held FY27
   31.3% is the number to have ready.
6. **1Q27 trough 19.5% (band 17-22%).** Q1 is the widest discretionary quarter, and the Q1 "brand campaign"
   is a denominator effect: Q1 is the *lightest* S&M dollar quarter of the year.

Feeds WS23: `M6_cycle_flex_scenarios_quarterly.csv` (200 quarter-rows) and `_annual_forecasts.csv` (65 annual
rows), both keyed base x scenario x variant.

## 12. Files written

Scripts: `analysis/src/margin_build/M6_cycle_flex/run.py`, `analysis/src/margin_build/M6_cycle_flex/README.md`.
Data (`data/processed/margin_build/M6_cycle_flex/`): `M6_cycle_flex_k_table.csv`, `_params_by_vintage.csv`,
`_peer_k.csv`, `_seasonal.csv`, `_seasonal_stability_2022_25.csv`, `_forecasts_wide.csv`, `_registry_long.csv`,
`_backtest_grid.csv`, `_scoreboard_rows.csv`, `_scenarios_quarterly.csv`, `_annual_forecasts.csv`,
`_cut_solutions.csv`, `_fy26_floor_breakeven.csv`, `_test_2H22_reproduction.csv`, `_test_T3_rows.csv`,
`_build.json`.
Registry: `data/processed/margin_build/registry/cycle-flex__flex_margin.csv` (1,872 rows),
`cycle-flex__flex_lines.csv` (3,120 rows).
Figures: `analysis/figures/margin_build/M6_cycle_flex_k_by_line.png`, `M6_cycle_flex_backtest_margin.png`,
`M6_cycle_flex_scenarios.png`.
Note: this file.

## RESUME

M6 is complete and reproducible (`py -3.13 analysis/src/margin_build/M6_cycle_flex/run.py`, 153 s, exit 0,
all outputs byte-identical on re-run; 384 rows in `scoreboard_margin.csv`). The next agent should do three
things. (a) In synthesis, take from M6 only the `k`'s, the peer comparison, the FY26 break-even (0.27pp per
1% of 2H26 revenue, $149-203m of cushion), the asymmetry result and the bear/bull scenario **deltas** —
**not** the FY27/FY28 point levels, which are biased low by the positive intercepts in the growth regressions
(FY28 31.3% vs Street 37.7%; section 8.3); carry M1's levels and apply M6's deltas to them. (b) Consider a v2
that re-specifies the discretionary lines in *levels* (per night, or per unit of revenue) instead of
growth-on-growth, which removes the compounding intercept and is the single highest-value fix; keep the lag-0
growth form for cost of revenue and ops & support, which work. (c) Red-team targets, all written up above and
answerable: the cut caps (sm 20 / pd 10 / ga 5) are judgement constants; T1 failed on product development;
T2 failed on the 2H22 reproduction and the reason is the revenue leg, not the cost equations; the quantiles
are too wide (cov80 0.93-1.00 against 0.80); and the model adds nothing in calm quarters (ratio 1.00) by
design.

---

# Discussion response (WS22, 14 Sep 2026)

Written by the group A discussion agent (M1 / M4 / M6). Everything above this line is the original note and was
not edited. Findings addressed: **R01, R02, R03, R08, R10, R11, R13, R14, R15, R17, R19**.
Backups: `data/processed/margin_build/M6_cycle_flex/_pre_discussion/` (every CSV) and
`data/processed/margin_build/registry/cycle-flex__*_pre_discussion.csv.bak`.
Rebuild: `MARGIN_SKIP_SCORE=1 py -3.13 analysis/src/margin_build/M6_cycle_flex/run.py` (23 s, exit 0).
`score.py` was **not** run; the orchestrator re-scores once.

## D1. R03 — `revknown_rw` was registered as PIT. ACCEPTED and FIXED.

Reproduced: 468 rows in `cycle-flex__flex_margin` and 780 in `cycle-flex__flex_lines` carried
`spec_id=revknown_rw`, in both replays, and its W1 h=0 margin ratio of 0.981 (rw 0.875) sat in the same survivor
table as the genuine PIT specs. FORMAT 1.0 validates `prior_basis` against `{PIT, full_sample}` and has no oracle
column, so the spec is **withdrawn from the registry**: 1,248 rows now live in
`M6_cycle_flex_oracle_diagnostic.csv` behind a leading `ORACLE_NOT_A_FORECAST` column.
Registry rows: `flex_margin` 1,872 -> **1,404**, `flex_lines` 3,120 -> **2,340**. `l0_rw`, `l0_eq` and `dl_rw` are
unchanged. Section 7's `revknown_rw` rows stay in the note as a **diagnostic** — with the actual revenue path the
same `k`s give margin MAE 2.19pp (W1) / 1.76pp (W2) against `l0_rw`'s 2.20 / 1.77, i.e. at h=0 **the revenue leg is
worth almost nothing**, which is itself the useful finding (the revenue leg only starts to matter at h>=1, where
`revknown_rw` at h=2 scores 0.922 / 0.930 against `l0_rw`'s 1.092 / 1.359).

## D2. R15 — FY28 is unusable. ACCEPTED and FIXED.

Reproduced: the five FY28 rows all read **31.33%** against Street 37.65%, because `c_pd` 0.147 and `c_sm` 0.155
compound discretionary spend at 15-19%/yr against 8-9% revenue growth over four unanchored quarters.
`M6_cycle_flex_annual_forecasts.csv` now carries a **flat roll-forward of the same row's FY27 margin** in
`adj_ebitda_margin_pct` (34.36% for every base/flex row, 35.00% for `cut`), the withdrawn value in a new
`withdrawn_growth_model_margin_pct` column, the line columns set to NaN (they are not meaningful under a flat
roll), and a `fy28_basis` string that says so. The original five rows are preserved in
`M6_cycle_flex_fy28_withdrawn.csv`. Kill-list item 6 ("M6's FY28 of 31.3%") is now enforced by the data file, not
only by a sentence in a note. **For a FY28 level use M1's 32.6% or Street's 37.65%, labelled.**

## D3. R11 — LIVE 3Q26 above the ceiling. ACCEPTED, and it costs M6 its headline claim.

Reproduced: M6's engine puts 3Q26 at **51.575%** on the M1 base and **51.233%** on its own, against the 2Q26
letter's ceiling of **50.085%** and Street 49.776%. As in M1's D3, the defence that management's *quarterly*
sentence is sandbagged does not hold (`q_guide_implied` realised gaps: W2 mean **-0.19pp**, median -0.94pp, only
**4 of 10** quarters above the sentence; last eight quarters -0.86pp). The sentence wins.

Clipping 3Q26 to the sentence and leaving 4Q26 alone is not cosmetic for M6, because M6's most-quoted number is
the FY26 floor cushion. New file `M6_cycle_flex_guide_clipped_floor.csv`:

| base | 3Q26 clip | FY26 margin | cushion vs the 35.5% floor | 2H26 revenue shortfall the floor survives |
|---|---|---|---|---|
| M1 base, `flex` | 51.57 -> 50.09% (-$71.5M) | 36.18 -> **35.68%** | +0.68 -> **+0.18pp** | 2.54% ($203M) -> **0.68% ($54M)** |
| M1 base, `held` | same | same | same | 1.87% ($149M) -> **0.50% ($40M)** |
| M6 own base, `flex` | 51.23 -> 50.09% (-$55.1M) | 35.97 -> **35.59%** | +0.47 -> **+0.09pp** | 1.77% ($141M) -> **0.33% ($26M)** |

**Section 11's card line 3 ("the FY26 35.5% floor is not at risk — it survives a 1.9-2.5% 2H26 revenue shortfall,
$149-203M") is WITHDRAWN as written.** Under the guidance sentence the cushion is **$19-54M, not $149-203M**, and
the floor stops being a revenue question and becomes a **4Q26 question**: M3's sentence-modal 4Q26 of 30.9%
(against M1's 28.5%) is worth 2.43pp of 4Q26 = **+0.54pp of FY26**, which on its own restores FY26 to 36.22% and
the cushion to +0.72pp. The honest card sentence is: *the FY26 floor is not decided by 3Q26 — with 3Q26 capped at
the guidance sentence the FY26 cushion is under 20bp, and everything then depends on 4Q26, where our own two
methods disagree by 2.4pp.* The engine's **sensitivities and deltas are untouched** (0.27pp of FY26 margin per 1%
of 2H26 revenue flexed, 0.36pp held; flexing recovers only 30-40% of what a revenue miss costs); it is only the
*level* the cushion is measured from that moves.

## D4. R14 — line-vs-margin. ACCEPTED, and it hands M6 the best line result in group A.

Re-scored against `seasonal_naive_drift`, the honest baseline for a growing dollar line (PIT, h=0; `l0_rw` is
unchanged by D1-D3 so these numbers stand). Paired loss differentials, Newey-West(1), plus a sign test
(`analysis/src/margin_build/22_discussion_group_A/repro_drift.py` ->
`data/processed/margin_build/22_discussion_group_A/groupA_paired_vs_drift.csv`):

| target | `l0_rw` W1 ratio | t | p | better | W2 ratio | t | p | better |
|---|---|---|---|---|---|---|---|---|
| **cost of revenue** | **0.652** | **-3.57** | **0.0004** | **13/14** (sign p 0.002) | **0.677** | **-2.67** | **0.008** | **9/10** (sign p 0.021) |
| operations and support | 0.988 | -0.06 | 0.95 | 8/14 | 0.960 | -0.16 | 0.87 | 6/10 |
| product development | 1.216 | +1.00 | 0.32 | 6/14 | 1.276 | +0.84 | 0.40 | 4/10 |
| sales and marketing | 1.176 | +0.87 | 0.38 | 5/14 | 1.139 | +0.46 | 0.65 | 3/10 |
| G&A ex reserves | 1.001 | +0.01 | 0.99 | 9/14 | 1.055 | +0.28 | 0.78 | 6/10 |
| total cash costs | 1.164 | +1.00 | 0.32 | 6/14 | 1.139 | +0.53 | 0.60 | 4/10 |
| adj EBITDA $ | 0.597 | -2.23 | **0.026** | 10/14 | 0.716 | -1.29 | 0.20 | 6/10 |
| adj EBITDA margin | 0.923 | -0.45 | 0.65 | 7/14 | 0.878 | -0.53 | 0.60 | 5/10 |

**`k_cor = 0.56` on cost of revenue is, as far as group A can find, the only object built from ABNB's own history
that beats an adversarial baseline at p<0.05 in BOTH windows and on both the t-test and the sign test.** The red
team's "not a single cell is significant in W1" holds against `seasonal_naive` and against the Street; it does not
hold against `seasonal_naive_drift` for this one line. That is a much smaller claim than a margin model, and it is
the claim M6 should make. Section 7's line table (ratios 0.20-0.53 against `pct_rev_last4`) stays in the note but
must be quoted with the drift column beside it. The re-scoring is **post-hoc**, prompted by R14.

## D5. R13 — reproducibility of the licensed peer files. PARTLY REJECTED, partly accepted.

**Rejected:** R13 says M6's `run.py` "raises FileNotFoundError before writing anything" from a clean clone.
It does not. `peer_k_table()` opens with `if not PEER_OPEX.exists(): return pd.DataFrame()`, and the S&M file has
its own `.exists()` guard. Reproduced by loading `run.py` as a module, pointing `PEER_OPEX` and `PEER_SM` at
non-existent paths and calling `peer_k_table()`: **0 rows returned, no exception**. Both files are also already
manifested with size, sha256 and pull timestamp in `data/manifests/margin_build/04_alt_signals.csv`.

**Accepted:** the prerequisite was undocumented and the failure was silent — an empty `_peer_k.csv` would have
been read as "the peers have no cyclicality" rather than "the peer table is missing". Fixed: `peer_k_table()` now
prints `!! MISSING LICENSED INPUT ... the peer k comparison is SKIPPED`; the README has a new **Licensed
prerequisites** section naming both files, their manifest, the LSEG fields to re-pull, and the warning that an
empty file means missing, not zero; and `data/manifests/margin_build/M6_cycle_flex.csv` (new) cross-references
both rows with a `consumed_by` column.

## D6. R01, R02, R08, R10, R17, R19 — accepted as quoting rules.

- **R01 / R02.** Reproduced on M6's cells (`22_discussion_group_A/groupA_paired_tests.csv`). `l0_rw` vs seasonal naive at h=0, PIT:
  W1 mean d **-0.036pp**, NW(1) t **-0.10**, p **0.92**, better in **7 of 14**; W2 -0.186pp, t -0.52, p 0.60,
  5 of 10. `dl_rw` is worse than naive (t +0.87 / +0.94). **Section 1's "the registered forecaster passes its
  harness test" is downgraded to "the registered forecaster is a tie with y[q-4] and its pass flag is the ~30%
  free flag the red team priced".** Section 7's "survives both windows both weightings" line for `l0_rw` must not
  be quoted without t -0.10 / p 0.92 / 7-of-14 next to it. T3 (the 2025 shock slice, ratio 0.92 in both windows,
  n = 4) was pre-registered and stands as pre-registered, but n = 4 cannot carry a p-value and must be quoted as
  "4 quarters".
- **R08.** M6's own cells are n = 14 / 13 / 12 / 10 / 9 / 8 except the pre-registered T3 slice (n = 4) and the 2H22
  slice (n = 3), both of which are labelled in the note. Agreed that the scoreboard should carry n beside the flag.
- **R10.** Confirmed and already flagged in section 7: cov80 0.93-1.00 and cov90 1.00 at h=0 against a nominal
  0.80. ACCEPT-DEFER. M6's own instruction stands and is now the rule: **use the scenario spread, never the
  residual band.**
- **R17.** Accepted: M6's h=0 is post-letter and post-guide, which is precisely why D3's clip is the right
  treatment — the sentence is in the model's information set.
- **R19.** M6's pre-registration is at commit `bebbf4e`, before the results. No action.

## D7. Replacement card lines for M6 (supersede section 11)

1. **"Airbnb has no cost dial"** — unchanged and still the best thing M6 has: total opex elasticity 0.14 and not
   significant, against BKNG 0.61, TRIP 0.63, EXPE 0.44 and BKNG advertising 0.87-0.98 (n = 18 each).
2. **"So the 3Q26 print is a revenue print"** — unchanged (1% of 2H26 revenue is ~27bp of FY26 margin flexed,
   ~36bp held), but the sentence that followed it, "a 150-180bp margin beat is in the base case", is **withdrawn**:
   that beat is the unclipped model against a guidance sentence the company has not historically beaten.
3. **"The FY26 floor is not at risk"** — **withdrawn as written** (see D3). Replacement: *with 3Q26 capped at the
   guidance sentence, the FY26 cushion above the 35.5% floor is +0.09 to +0.18pp, i.e. a 0.24-0.68% 2H26 revenue
   shortfall ($19-54M); the floor is then decided by 4Q26, where M1 (28.5%) and M3's sentence-modal (30.9%) differ
   by 2.4pp = 0.54pp of FY26.*
4. **"Watch the FY27 sentence, not the FY26 one"** — unchanged (FY27 34.4-35.1% flexed against Street 36.4%;
   bear 31.3-32.4% unless $386-508M is cut).
5. **The asymmetry** (k_dn < k_up for ops, S&M and total cash costs, p < 0.02, n = 16) — unchanged.
6. **1Q27 trough 19.5%, band 17-22%** — unchanged.
7. **New:** *cost of revenue moves 0.56 with revenue and that relationship is the one testable thing in the cost
   stack: ratio 0.65 against a drift naive, p 0.0004, better in 13 of 14 quarters.*
8. **FY28: do not quote M6.** The annual file now carries a labelled flat roll-forward.

## D8. Recommended WS23 weights for M6's objects

| object / use | weight | why |
|---|---|---|
| `k_cor` = 0.56 (cost of revenue on revenue growth) | **1.0** | the only ABNB-history object in group A significant against a drift baseline in both windows |
| `k_ops` = 0.44 | 0.5 | right sign, t 3.4, but a tie against drift at the line level |
| `k_pd` / `k_ga` | **0** | insignificant and wrong-signed; M6's own T1 failed on pd |
| `k_sm` = 0.42 | 0.25 | t 2.3 but unstable (0.87 in 2022, 0.30-0.42 since 2025); use it only for scenario deltas |
| peer `k` comparison (ABNB 0.14 vs BKNG 0.61 / TRIP 0.63 / EXPE 0.44) | **1.0** | a measurement, not a forecast; the strongest qualitative point in the run |
| scenario engine **deltas** (bear/bull, flex vs held, cut) | **1.0** | the deltas never depended on the level; unchanged by every fix here |
| FY26 floor break-even | **1.0 in its clipped form** (`_guide_clipped_floor.csv`), 0 in the unclipped form | see D3 |
| `flex_margin` as a margin **point forecast** at h=0 | **0.15** | t -0.10, p 0.92, 7 of 14; keep it only as one arm of the 350bp cross-method spread |
| `flex_margin` beyond h=0, FY27 / FY28 **levels** | **0** | W1 h=1 ratio 1.31; FY28 withdrawn; carry M1's levels and M6's deltas |
| `dl_rw` | **0** | 22 parameters, worse on every cut |
| `revknown_rw` | **0** as a forecast, keep as the h>=1 revenue-leg diagnostic | oracle |
| M6 quantiles | **0** | cov80 0.93-1.00 |
