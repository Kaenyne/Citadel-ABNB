# 10_harness_margin — the margin harness (targets, PIT slice, baselines, recency-weighted scorer, registry)

Built 13 Sep 2026 on top of the FROZEN revenue harness (`analysis/src/forecast_methods/harness/`, FORMAT 1.0).
The frozen calendar, guide-date windows, registry validator and metric primitives are **imported**, never copied
or modified. Every margin method (M1-M7) registers through this package.

## Run

```bash
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/10_harness_margin/run.py      # rebuild everything, ~40 s, exit 0
py -3.13 analysis/src/margin_build/10_harness_margin/score.py    # rescore after you register a method
py -3.13 analysis/src/margin_build/10_harness_margin/tests.py    # 11 unit tests (also runs under pytest)
```

**Interpreter.** Use `py -3.13` (pandas 2.3, numpy, scipy, statsmodels, sklearn). The package only needs pandas
and numpy and also runs under the repo venv `python` (pandas 3), which has no scipy / statsmodels / sklearn; the
outputs are identical under both (verified 13 Sep 04:33). Method authors should fit with `py -3.13`.

`run.py` overwrites only its own outputs under `data/processed/margin_build/10_harness_margin/` and the seven
`baselines-margin__*.csv` files in the registry; it never touches another method's registry file.

## What you get (API)

```python
import sys; sys.path.insert(0, r"C:\Users\krish\citadel-abnb-margins\analysis\src\margin_build\10_harness_margin")
from harness_margin import (
    load_targets, history_as_of, series_as_of, full_series, TARGET_METRICS, UNITS,   # the target panel + PIT slice
    GUIDE_DATES_W1, GUIDE_DATES_W2, GUIDE_DATE_LIVE, TODAY, LIVE_VINTAGES,          # the calendar (frozen)
    W1_TARGETS, W2_TARGETS, windows_for,                                            # window membership
    register, load_registry, validate_margin_frame, REGISTRY_COLUMNS,               # FORMAT 1.0 registry
    score_registry,                                                                 # the scorer, in memory
    revenue_forecast_pit,                                                           # the PIT revenue leg
    fy_guide_in_force, q_guide_in_force, load_guides,                               # management margin guides
    load_street,                                                                    # WS03 Street, vintage-stamped
    Q, W, M,                                                                        # frozen quarters/windows/metrics
)
```

### Usage example for a method author (15 lines)

```python
import sys, pandas as pd; sys.path.insert(0, r"C:\Users\krish\citadel-abnb-margins\analysis\src\margin_build\10_harness_margin")
from harness_margin import history_as_of, register, GUIDE_DATES_W1, TODAY, windows_for, revenue_forecast_pit, Q
rows = []
for vd in GUIDE_DATES_W1 + [TODAY]:                              # 14 W1 guide dates (W2 is a subset) + LIVE
    h = history_as_of(vd)                                        # quarters printed on or before vd, nothing later
    q0 = Q.quarter_of_date(vd)
    for hz in range(0, 3 if vd != TODAY else 6):                 # h=0,1,2 backtest; h=0..5 LIVE (3Q26..4Q27)
        q = Q.shift(q0, hz)
        rev, leg = revenue_forecast_pit(vd, q)                   # PIT revenue input (guide-cushion / naive)
        point = h["adj_ebitda_margin_pct"].iloc[-4:].mean()      # <-- your model goes here
        for win in windows_for(vd, q):                           # W1 / W2 / LIVE as the rules allow
            rows.append(dict(method="m1-costlines", object="margin_v1", target="adj_ebitda_margin_pct", quarter=q,
                             vintage_date=vd, horizon_q=hz, point=point, q50=point, q10=point - 2, q90=point + 2,
                             window=win, prior_basis="PIT", n_params=3, n_train=len(h), spec_id="rw_hl4"))
register(pd.DataFrame(rows), allow_single_replay=True)           # then add the full_sample replay and drop the flag
```

Then `py -3.13 analysis/src/margin_build/10_harness_margin/score.py` and quote your rows from
`data/processed/margin_build/10_harness_margin/scoreboard_margin.csv`.

## 1. Targets — `data/processed/margin_build/10_harness_margin/targets.csv`

One row per quarter 2020Q1..2027Q4; actuals 1Q20-2Q26 (26 quarters) from WS02 `02_panel_quarterly.csv` (final,
13 Sep 04:26; validated: no nulls 1Q21-2Q26, |rebuild gap| <= 2, adj EBITDA within $1.5M of the repo cost stack);
2026Q3-2027Q4 are forward rows (no actuals) so LIVE registrations can find the quarter. Fallback loader (env
`MARGIN_HARNESS_PANEL=fallback`) rebuilds the panel from the repo files `abnb_quarterly_cost_stack_exsbc.csv`,
`abnb_quarterly_costlines.csv`, `abnb_fcf_bridge.csv`, `abnb_capital_return_quarterly.csv`,
`overnight/02_kpi_panel_quarterly.csv`; the test suite checks it agrees with WS02 on adj EBITDA to $1.5M.
`targets_source.json` records which source was used and the validation log.

Meta columns: `quarter, print_date, knowable_from, has_actual, source, eps_source`. 1Q20 and 2Q20 pre-date the
first shareholder letter; they became public in the 424B4 prospectus and are stamped `2020-12-10`. Every other
print date comes from the frozen calendar.

Target metrics (42, units in `targets_units.csv`):

| group | columns | unit |
|---|---|---|
| denominators | `revenue_musd, nights_m, gbv_musd` | USD m, m, USD m |
| adj EBITDA | `adj_ebitda_musd, adj_ebitda_margin_pct, adj_ebitda_margin_yoy_pp, adj_ebitda_per_night` | USD m, %, pp, USD/night |
| six cash lines ex-SBC | `{cor,ops,pd,sm,ga}_cash_musd`, `ga_cash_ex_reserves_musd`, `total_cash_costs_musd` (= revenue - adj EBITDA) | USD m |
| same as ratios | `{cor,ops,pd,sm,ga}_cash_pct_rev`, `total_cash_costs_pct_rev`, `{line}_cash_per_night`, `revenue_per_night` | %, USD/night |
| GAAP bridge | `sbc_musd, sbc_pct_rev, da_musd, op_income_musd, op_margin_pct, pretax_income_musd, tax_provision_musd, tax_rate_pct, net_income_musd, eps_diluted, diluted_shares_m, interest_income_musd` | USD m, %, USD/share, m |
| cash | `cfo_musd, capex_musd, fcf_musd, fcf_margin_pct` | USD m, % |

`ga_cash_musd` includes the 4Q23 $931M lodging-tax reserve (it sits in GAAP G&A); `ga_cash_ex_reserves_musd`
strips lodging-tax reserves. `tax_rate_pct` is wild in small-pretax quarters (3Q23 -161%); use with care.

## 2. `history_as_of(vintage_date, metric=None)`

The point-in-time slice: rows whose `print_date <= vintage_date` (the same-day letter is included, exactly as the
frozen harness does; pass `include_same_day=False` for the strict reading). `series_as_of` returns a Series
indexed by quarter. Nothing printed after the vintage is visible, whatever the vintage.

## 3. Windows and vintages

- W1: 14 guide dates 2023-02-14 .. 2026-05-07, target quarters 2023Q1..2026Q2. W2: 10 dates 2024-02-13 .., 2024Q1..2026Q2.
- LIVE vintages: `2026-08-06` (the 3Q26 guide) and **`TODAY = 2026-09-11`**. The frozen validator accepts no other
  non-guide date, so the prompt's 2026-09-12 is stamped 2026-09-11 (the WS03 "current" row is the 11 Sep LSEG row).
- `windows_for(vintage, quarter)` returns the windows a row may carry: a W1 row needs a W1 guide date AND a W1 target
  quarter (so h=1/h=2 rows from the last W1 dates that land in 2026Q3+ are dropped, not re-labelled LIVE); W2 likewise;
  LIVE needs a LIVE vintage and a quarter >= 2026Q3 (up to 2027Q4).
- Horizons: `horizon_q = quarters from the quarter containing vintage_date` (h=0 is the quarter being guided).
  Backtests h=0,1,2; LIVE h=0..5.

## 4. Registry — `register(df)`

Wraps the frozen `validate_registry_frame` (column set, slugging, vintage-date rule, PIT rule against the frozen
calendar, `street_as_of` / `knowable_from` <= `vintage_date`, quantile monotonicity, two-replay rule, coverage warnings)
and adds: `target` must be a column of the margin `targets.csv`; the margin window rule above (the frozen strict
check would reject LIVE 2026Q4 — its LIVE list holds 2026Q3 only, which is how every revenue package registered
2026Q4 too); an h=0 coverage warning (14 / 10 vintage dates). Files go to
`data/processed/margin_build/registry/<method>__<object>.csv`. Required columns are the frozen twelve
(`method, object, target, quarter, vintage_date, horizon_q, point, q50, window, prior_basis, n_params, n_train`);
optional `q05 q10 q25 q75 q90 q95 sd base_* street_vendor street_as_of knowable_from spec_id notes`.
**Put grid variants in `spec_id`**: the margin scorer keys on it (the frozen one does not).

## 5. Baselines — method `baselines-margin`, seven objects

| object | rule | targets | params* |
|---|---|---|---|
| `seasonal_naive` | y[q-4] | all 42 | 0 |
| `seasonal_naive_drift` | y[q-4] + (y[last] - y[last-4]) (additive y/y change, so it is defined where levels cross zero) | all 42 | 0 |
| `trailing4` | mean of the last 4 observed values | the 19 ratio-class metrics (%, pp, USD/night) | 1 |
| `pct_rev_last4` | mean of last-4 (line / revenue) x revenue leg | 10 $ lines incl. adj EBITDA, SBC, D&A | 2 |
| `guide_implied` | FY margin guide in force (floor at the floor, point at the point, y/y on the prior-FY actual) x FY revenue estimate, minus YTD actual EBITDA, prorated over the remaining quarters by seasonal EBITDA shares (PIT: last 3 complete FYs >= 2021; full_sample: FY2023-25); NaN when no FY guide is in force | `adj_ebitda_margin_pct`, `adj_ebitda_musd` | 3 |
| `q_guide_implied` | the quarterly margin sentence in force, as a level (y/y on last year's actual); the 3Q25 "$2.0B+" floor as $ | same two | 0 |
| `street` | LSEG mean at the vintage (WS03): pre-guide value for the guided quarter (h=0) and the next (h=1); 11 Sep row at TODAY; `street_as_of` = the LSEG calc date (D-1), never a later vintage | `adj_ebitda_musd, adj_ebitda_margin_pct, revenue_musd, eps_diluted, op_income_musd, net_income_musd, fcf_musd` | 0 |

\* `n_params` in the registry = rule parameters + 1 for the residual sd when it is fitted (frozen convention).

Revenue leg (`revenue_forecast_pit`, file `revenue_leg_pit.csv`): the frozen `baselines` guide-cushion
(`guide_mid x median trailing-8 actual/guide`) when a revenue guide for the quarter is in force at the vintage
(h=0, and 3Q26 at both LIVE vintages), else the frozen naive `y[q-4] x (1 + last y/y growth)`, else that rule
chained (2027Q3-Q4). At TODAY: 3Q26 4,815 (cushion), 4Q26 3,237, 1Q27 3,121, 2Q27 4,205, 3Q27 5,611, 4Q27 3,773.

Quantiles: Gaussian on the walk-forward residual pool of the same object / target / horizon — PIT: the last 12 errors
whose target quarter printed before the vintage; full_sample: all realised errors (only the sd leaks; points are PIT
in both replays, except `guide_implied`'s seasonal shares). Relative errors for strictly positive level metrics
(cost lines, revenue, nights, GBV, SBC, D&A, shares, interest income, adj EBITDA), additive for ratios, per-night, EPS
and level metrics that cross zero. LIVE h=3..5 borrow the h=2 pool (labelled in `notes`). Fallback when fewer than 3
residuals: 10% relative / 3 pp additive (labelled `_fallback`, n_params not incremented).

## 6. Scorer — `score.py` -> `scoreboard_margin.csv` / `.md`, `scoreboard_by_quarter.csv`, `hardest_baseline_by_target.csv`, `baseline_scoreboard_summary.md`

Per (`method, object, target, window, horizon_q, prior_basis, spec_id`): `n, first_quarter, last_quarter, mae, rmse,
bias, crps, pinball_mean, cov80 (q10-q90), cov90 (q05-q95), pit_mean, pit_edge_frac`, `mae_ratio_<baseline>` and
`n_match_<baseline>` for each of the seven baselines (PIT replay, matched quarters), `beats_seasonal_naive`,
`survives_both_windows` (beats seasonal_naive at the same horizon and replay in W1 AND W2), rolling split-conformal
coverage (frozen, n_cal 6, alpha 0.2, with the exchangeability caveat), `n_params, n_obs, param_obs_ratio,
replays_present`. **Every accuracy statistic again with prefix `rw_`** (recency-weighted: exponential weights,
half-life 4 quarters, anchored at the latest quarter of the window = 2026Q2, normalised within the group), and
`rw_beats_seasonal_naive`, `rw_survives_both_windows`. A claim needs both `survives_both_windows` flags.
`scoreboard_by_quarter.csv` is the long file (error, CRPS, coverage flag, weight, and the seasonal-naive point and
error on every row) so a method can diff its errors quarter by quarter.

## 7. Other files

`guides_margin.csv` (38 numeric margin guides from the ledger, canonical periods), `street_margin_pit.csv` (336
vintage-stamped LSEG values), `seasonal_shares.csv`, `revenue_leg_pit.csv`, `baseline_grid_all_vintages.csv` (every
baseline point at every vintage 2021-11-04..TODAY with its error and sigma pool size — the residual pools).

## 8. Harness change requests (for the frozen harness; nothing there was edited)

1. `windows.LIVE_TARGETS` holds only 2026Q3 while README §2.5 says "2026Q3 or later"; the margin wrapper applies
   the README rule. 2. The frozen scorer ignores `spec_id`; the margin scorer keys on it.
