# M2 — Time-series and ratio methods for adjusted EBITDA margin and the cost lines (`margin-ts`)

Slug `M2_margin_ts`. Method name in the registry: `margin-ts`. Written 14 Sep 2026 (Sunday, 05:15-06:30) by the M2 agent.
Code: `analysis/src/margin_build/M2_margin_ts/` (`run.py`, `m2_margin_ts.py`, `README.md`). Data:
`data/processed/margin_build/M2_margin_ts/`. Registry: `data/processed/margin_build/registry/margin-ts__*.csv` (7 objects).
Interpreter `py -3.13`. Build time 72 s, exit 0.

## Bottom line

1. **The four "simplest honest competitors" do not beat the seasonal naive on the margin.** None of `yoy_margin_change`,
   `incremental_margin`, `pct_rev_seasonal`, `per_night_seasonal` has a lower h=0 MAE than y[q-4] in both windows under both
   weightings (pre-registered pass line P1: **FAIL**). Best of the four: `per_night_seasonal|g_k4_rw` (recency-weighted ratio to
   naive 0.94 W1 / 0.93 W2, but equal-weighted 1.08 / 1.05) and `incremental_margin|k8_median` (W2 0.89, W1 1.16). Every drift
   or trend term estimated from 2022-23 pushed the 2023-24 forecasts the wrong way (delta of +10 pp at the Feb-2023 vintage).
2. **Two objects do beat the naive in both windows, both weightings, at h=0** (3 of 29 specs; 0 of 29 at h=1 and h=2):
   `q_sentence_direction|k_fit_rw` — last year's margin +/- k in the direction of management's quarterly sentence, k fitted PIT
   (2.03 pp today) — MAE **2.07 pp W1 (n=14) / 1.64 pp W2 (n=10)**, recency-weighted 1.53 / 1.38, ratio to naive 0.92 / 0.84
   (rw 0.80 / 0.79); and `sarima_margin|lines_aicc` (log-line SARIMA, 13-15 parameters) 2.04 / 1.49, rw 1.59 / 1.35.
   **Neither beats the Street** (1.59 / 1.31; rw 1.25 / 1.12): P7 answer is no, as expected.
3. **The sentence rule's hindsight version beats the Street; its honest version does not.** With k fixed at the full-sample
   value 2.03 pp at every vintage (`full_sample` replay) the MAE is 1.49 / 1.23 pp (ratio to Street 0.93 / 0.94). PIT, k was
   3.5-6.3 pp at the 2023 vintages because the pool then held only 2022's reopening-sized moves, and it drifted down to ~2.0 by
   Aug 2025; the last five h=0 errors (3Q25-2Q26) are +0.3, +0.4, -1.0, +1.0 pp (and 4Q25 at h=1 +0.5), i.e. the rule is
   currently running at Street-level accuracy. WS10's in-sample "k = 1.5" figure (1.43 / 1.17) is the same object with a
   hand-picked k; the PIT number to quote is 2.07 / 1.64.
4. **In EBITDA dollars the sentence rule is the best object in the registry and beats the Street** in both windows, both
   weightings: MAE $56M W1 / $48M W2 (rw $46M / $43M) vs Street $65M / $58M and the `q_guide_implied` baseline (last year's
   margin x the same PIT revenue) $63M / $62M. The improvement over `q_guide_implied` is $7-14M, i.e. the direction term is
   worth about a third of a percentage point of margin on a $2.3B quarter; most of the dollar accuracy is the guide-cushion
   revenue leg, not the margin rule.
5. **Cost lines:** the WS10 finding stands — `seasonal_naive_drift` ($ y/y change persistence) is the hardest line baseline
   and is not beaten for product development or sales & marketing by any ratio, per-night or SARIMA object. `per_night_seasonal`
   beats it for cost of revenue (0.82 / 0.82) and ops & support (0.90 / 0.89); `pct_rev_seasonal` for cost of revenue only
   (0.70 / 0.78). P3 (3 of 5 lines) **FAIL**. Adding drift to the % of revenue ratios makes PD and S&M *worse* than the plain
   seasonal ratio (S&M ratio drift of +2.3 pp y/y is real, but it is already in last year's dollars).
6. **Calibration:** PIT 80% intervals cover 86-100% at h=0 — too wide, because the walk-forward residual pools still carry the
   2021-23 errors; only `per_night_seasonal` (0.93 / 0.90) lands inside the pre-registered [0.60, 0.95] band in both windows
   (P4). The sentence rule's interval (sd 1.7 pp today) is the tightest and covered 13/14 W1 quarters.
7. **LIVE 3Q26 (vintage 2026-09-11, bridge v3 revenue $4,804M):** the objects span **47.1% to 51.5%**; sentence rule 48.1%
   (q10-q90 45.9-50.2), ensemble 49.2%, Street 49.78%, seasonal naive 50.09%, **seasonal-naive-with-drift 51.35%** (last year's
   50.09 + 2Q26's +1.26 y/y — the number the Street would print if it extrapolated). 4Q26: 27.9-29.1% vs Street 28.90%.
   FY26: 34.7-36.2% (ensemble 35.3%) vs Street 35.62% and management's "at least 35.5%". FY27: 34.2-36.9% vs Street 36.45%.

What I would put in the pitch from this workstream: the sentence rule with its **recency-weighted** k (the recency weighting is
what brought k down from 3 pp to 2 pp as the 2022 moves aged out; the equal-weighted spec `k_fit_ew` fails the naive bar in W1,
1.13), quoted as 3Q26 margin 48.1% +/- 1.7 pp, and the fact that no time-series object beats the Street on margin. Everything
else here is a floor for M1/M3/M5 to clear.

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

## What ran (exact commands)

```bash
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/M2_margin_ts/run.py            # grid, quantiles, 7 registry files, LIVE/annual, rescore, figures; 72 s, exit 0
py -3.13 analysis/src/margin_build/10_harness_margin/score.py     # rescore only (run.py already calls it)
```

Inputs actually used: harness `targets.csv` (26 actual quarters 1Q20-2Q26), `revenue_leg_pit.csv` via `revenue_forecast_pit`,
`guides_margin.csv` via `q_guide_in_force` (38 numeric margin guides; every quarterly sentence is coded value 0 with its direction in
`guide_type`), WS06 `06_revenue_path_wide.csv` with the WS06v override **`06_revenue_path_3q26_4q27_v2b.csv` (written 04:55, picked up
by the second and third builds; base path unchanged at 3Q26 $4,804M / 4Q26 $3,178M / FY27 $15,829M; the override moves the 3Q26 bear
and bull revenue to $4,755M / $4,878M)**, WS06 `06_consensus_quarterly_2027.csv` (LSEG means pulled 13 Sep for the comparison column).
Registry: 29,020 rows across the 7 objects (624 ensemble, 1,824 incremental, 11,424 pct_rev, 10,644 per_night, 448 sentence, 2,496
SARIMA, 1,560 yoy). The scorer reports 4,432 cells for the whole registry, 1,154 of them mine (PIT replay, all targets); 166 are
margin cells (29 specs x up to 3 horizons x 2 windows).

## Results against the pass lines

| test | result | evidence |
|---|---|---|
| P1 objects 1-4 beat naive on margin, h=0, both windows, both weightings | **FAIL** | best ratios: per_night g_k4_rw ew 1.08 / 1.05, rw 0.94 / 0.93; incremental k8_median ew 1.16 / 0.89 |
| P2 same at h=1, h=2 | not reached | no object 1-4 spec beats naive at h=1 in W1 (best incremental k8_median 0.98 / 1.34) |
| P3 lines beat seasonal_naive_drift for >= 3 of 5 | **FAIL** | per_night: CoR 0.82/0.82, Ops 0.90/0.89 (2 of 5); pct_rev: CoR only |
| P4 cov80 in [0.60, 0.95] for main spec, both windows | **FAIL** except per_night | per_night 0.93 / 0.90 pass; sentence 0.93 / 1.00; yoy 1.00 / 1.00; pct_rev 0.93 / 1.00; incremental 0.86 / 1.00 |
| P5 invmae4 beats eq4 | PASS (weakly) | W1 2.78 vs 3.00; W2 2.01 vs 2.13; weights 0.22-0.30, nearly equal; both worse than naive |
| P6 sentence rule beats naive both windows both weightings | **PASS** | 0.92 / 0.84 ew, 0.80 / 0.79 rw; stretch vs Street FAIL (1.30 / 1.25 x Street MAE) |
| P7 anything beats the Street on margin at h=0 | **NO** (PIT) | only the full_sample replay of the sentence rule does (hindsight k) |

Survivors of the two-flag rule on the margin (PIT replay): h=0: `sarima_margin|lines_aicc`, `q_sentence_direction|k_fit_median`,
`q_sentence_direction|k_fit_rw` (3 of 29 specs); h=1: 0 of 29; h=2: 0 of 25. 166 margin tests, 3 passes.

## Backtest — adjusted EBITDA margin (pp), h=0, PIT replay, sorted by W1 MAE

| object / spec | W1 MAE ew / rw (n=14) | W1 bias | r naive ew / rw | W2 MAE ew / rw (n=10) | W2 bias | r naive ew / rw | r Street W1 / W2 | cov80 W1 / W2 | n_params | both flags |
|---|---|---|---|---|---|---|---|---|---|---|
| **Street (baseline)** | **1.59 / 1.25** | -1.22 | 0.71 / 0.65 | **1.31 / 1.12** | -1.13 | 0.67 / 0.64 | 1 | 1.00 / 1.00 | 1 | yes / yes |
| sarima_margin lines_aicc | 2.04 / 1.59 | -0.29 | 0.91 / 0.83 | 1.49 / 1.35 | +0.35 | 0.76 / 0.77 | 1.28 / 1.13 | 0.93 / 1.00 | 15 | **yes / yes** |
| q_sentence_direction k_fit_median | 2.05 / 1.52 | -1.68 | 0.92 / 0.80 | 1.54 / 1.32 | -1.02 | 0.79 / 0.75 | 1.29 / 1.17 | 0.93 / 1.00 | 2 | **yes / yes** |
| q_sentence_direction k_fit_rw (main) | 2.07 / 1.53 | -1.82 | 0.92 / 0.80 | 1.64 / 1.38 | -1.31 | 0.84 / 0.79 | 1.30 / 1.25 | 0.93 / 1.00 | 2 | **yes / yes** |
| seasonal_naive (baseline) | 2.24 / 1.91 | -0.47 | 1 | 1.96 / 1.75 | +0.19 | 1 | 1.41 / 1.49 | 1.00 / 1.00 | 1 | – |
| pct_rev_seasonal nodrift (= naive) | 2.24 / 1.91 | -0.47 | 1.00 / 1.00 | 1.96 / 1.75 | +0.19 | 1.00 / 1.00 | 1.41 / 1.49 | 1.00 / 1.00 | 2 | no / (rw only) |
| per_night_seasonal g_k4_rw_nightsknown | 2.27 / 1.49 | +1.02 | 1.01 / 0.78 | 1.31 / 1.18 | +0.67 | 0.67 / 0.67 | 1.43 / 1.00 | 0.93 / 1.00 | 7 | no / yes |
| seasonal_naive_drift (baseline) | 2.38 / 1.98 | +0.26 | 1.07 / 1.04 | 2.02 / 1.85 | +0.54 | 1.03 / 1.05 | 1.50 / 1.54 | 1.00 / 1.00 | 1 | no |
| per_night_seasonal g_k4_rw (main) | 2.42 / 1.79 | +0.48 | 1.08 / 0.94 | 2.06 / 1.64 | +0.44 | 1.05 / 0.93 | 1.52 / 1.57 | 0.93 / 0.90 | 7 | no / yes |
| q_sentence_direction k_fit_ew | 2.53 / 2.03 | -2.11 | 1.13 / 1.06 | 2.12 / 1.90 | -1.73 | 1.08 / 1.09 | 1.59 / 1.61 | 0.93 / 1.00 | 2 | no |
| incremental_margin k8_median | 2.59 / 1.94 | +1.28 | 1.16 / 1.01 | 1.74 / 1.67 | +1.33 | 0.89 / 0.95 | 1.63 / 1.33 | 0.93 / 1.00 | 3 | no |
| incremental_margin k8_rw | 2.64 / 2.04 | +0.93 | 1.18 / 1.07 | 1.74 / 1.76 | +1.16 | 0.89 / 1.00 | 1.66 / 1.33 | 0.86 / 1.00 | 3 | no |
| ensemble_simple invmae4 | 2.78 / 2.10 | +0.57 | 1.24 / 1.10 | 2.01 / 1.83 | +0.64 | 1.02 / 1.04 | 1.75 / 1.53 | 1.00 / 1.00 | 5 | no |
| incremental_margin k4_rw (main) | 2.86 / 2.27 | +0.56 | 1.28 / 1.19 | 1.96 / 1.97 | +0.94 | 1.00 / 1.12 | 1.79 / 1.50 | 0.86 / 1.00 | 3 | no |
| ensemble_simple eq4 | 3.00 / 2.17 | +0.95 | 1.34 / 1.14 | 2.13 / 1.88 | +0.75 | 1.09 / 1.07 | 1.88 / 1.62 | 0.93 / 1.00 | 1 | no |
| sarima_margin margin_aicc | 3.61 / 2.54 | +1.88 | 1.61 / 1.33 | 2.42 / 2.15 | +0.83 | 1.24 / 1.22 | 2.27 / 1.85 | 0.79 / 1.00 | 4 | no |
| yoy_margin_change k4_rw (main) | 3.68 / 2.71 | +1.19 | 1.64 / 1.41 | 2.77 / 2.40 | +0.81 | 1.41 / 1.37 | 2.31 / 2.11 | 1.00 / 1.00 | 3 | no |
| pct_rev_seasonal drift_k4_rw (main) | 3.78 / 2.75 | +1.55 | 1.69 / 1.44 | 2.75 / 2.43 | +0.79 | 1.41 / 1.38 | 2.38 / 2.10 | 0.93 / 1.00 | 7 | no |
| q_sentence_direction k_abs_rw | 3.97 / 1.85 | -3.25 | 1.78 / 0.97 | 1.31 / 1.08 | -1.12 | 0.67 / 0.62 | 2.49 / 1.00 | 1.00 / 1.00 | 2 | no / yes |
| pct_rev_seasonal drift_k8_rw | 5.94 / 3.47 | +5.17 | 2.66 / 1.81 | 2.77 / 2.56 | +1.69 | 1.41 / 1.46 | 3.73 / 2.11 | 0.86 / 1.00 | 7 | no |

Remaining specs (yoy k2/k4 ew, shrink; incremental k4_ew, k4_rw_revknown; pct_rev drift_k4_ew, revknown; per_night g_k4_ew, g_k8_rw,
nogrowth) are in `M2_margin_ts_scoreboard_extract.csv`; none passes. Note `pct_rev_seasonal` margin forecasts do not depend on the
revenue leg (margin = 100 - sum of ratios), so `drift_k4_rw_revknown` equals `drift_k4_rw` on the margin; they differ on the $ lines.

**Where the weightings disagree:** `per_night_seasonal|g_k4_rw` and `q_sentence_direction|k_abs_rw` beat the naive recency-weighted
but not equal-weighted in W1 — their 2023 errors were large (per-night growth rates and absolute y/y moves estimated on 2022 data)
and their 2025-26 errors small. Under the brief's "bias toward recent quarters" a reader may prefer the rw column; the two-flag rule
says these are not claims.

**h=1 and h=2 (margin, PIT).** No `margin-ts` spec beats the naive in both windows at either horizon. Best: `incremental_margin|k8_median`
h=1 W1 2.31 (0.98 x naive) but W2 2.11 (1.34 x); h=2 W1 2.02 (0.82 x) but W2 2.08 (1.21 x). The Street at h=1 (1.64 / 0.99) is far ahead
of everything. The sentence rule has a single h=1 row (4Q25 guided two quarters ahead in the 2Q25 letter: forecast 28.75, actual 28.29).

**full_sample replay (hindsight parameters, PIT inputs), h=0:** `q_sentence_direction|k_fit_rw` 1.49 / 1.23 (0.67 / 0.63 x naive;
0.94 x Street) and `k_fit_median` 1.48 / 1.22; `ensemble_simple|invmae4` 1.96 / 1.41; `sarima lines` 2.14 / 1.52; `pct_rev drift` 2.18 / 1.88
and `yoy k4` 2.19 / 1.89 (both just under the naive equal-weighted, not recency-weighted). The gap between the two replays of the sentence
rule (0.6 / 0.4 pp) is the cost of learning k from 2022; the gap for `yoy_margin_change` (1.5 / 0.9 pp) is what a hindsight drift buys.

## Backtest — adjusted EBITDA dollars (USD m), h=0, PIT

| object / spec | W1 MAE ew / rw | W1 bias | W2 MAE ew / rw | W2 bias | r Street W1 / W2 | r q_guide_implied W1 / W2 |
|---|---|---|---|---|---|---|
| **q_sentence_direction k_fit_median** | **53 / 46** | -36 | **45 / 43** | -22 | 0.81 / 0.78 | 0.84 / 0.73 |
| q_sentence_direction k_fit_rw | 56 / 46 | -39 | 48 / 43 | -31 | 0.86 / 0.82 | 0.89 / 0.77 |
| sarima_margin lines_aicc | 57 / 50 | +2 | 50 / 46 | +21 | 0.87 / 0.86 | 0.90 / 0.81 |
| per_night_seasonal g_k4_rw_nightsknown | 61 / 45 | +33 | 47 / 40 | +30 | 0.93 / 0.81 | 0.96 / 0.76 |
| q_guide_implied (baseline; last year's margin x PIT revenue) | 63 / 58 | -3 | 62 / 56 | +16 | 0.97 / 1.06 | 1 |
| Street (baseline) | 65 / 62 | -51 | 58 / 59 | -42 | 1 | 1.03 / 0.94 |
| per_night_seasonal g_k4_rw | 66 / 52 | +23 | 64 / 50 | +27 | 1.02 / 1.10 | 1.05 / 1.04 |
| incremental_margin k8_median | 68 / 54 | +34 | 54 / 49 | +41 | 1.04 / 0.93 | 1.07 / 0.87 |
| ensemble_simple invmae4 | 77 / 64 | +21 | 67 / 60 | +27 | 1.18 / 1.15 | 1.22 / 1.09 |
| incremental_margin k4_rw | 79 / 68 | +12 | 63 / 63 | +28 | 1.20 / 1.08 | 1.24 / 1.02 |
| yoy_margin_change k4_rw | 99 / 80 | +35 | 89 / 76 | +33 | 1.52 / 1.53 | 1.57 / 1.44 |
| pct_rev_seasonal drift_k4_rw | 100 / 81 | +43 | 89 / 77 | +32 | 1.54 / 1.53 | 1.59 / 1.44 |
| seasonal_naive_drift (baseline) | 103 / 93 | -3 | 82 / 86 | +1 | 1.58 / 1.41 | 1.64 / 1.33 |
| seasonal_naive (baseline) | 123 / 116 | -122 | 98 / 106 | -96 | 1.89 / 1.68 | 1.95 / 1.58 |

Every `margin-ts` object survives both windows in dollars (the naive is easy to beat because EBITDA grows); the sentence rule is the
only one that also beats the Street and `q_guide_implied` under both weightings. Its dollar bias is negative ($-22 to -39M) because k
was too large in 2023-24 (the margin bias of -1.3 to -1.8 pp).

## Backtest — cost lines, h=0, PIT (MAE, USD m unless stated; ratio to `seasonal_naive_drift` ew / rw)

| target | pct_rev drift_k4_rw W1 / W2 | per_night g_k4_rw W1 / W2 | sarima lines W1 / W2 | drift baseline MAE W1 / W2 | verdict |
|---|---|---|---|---|---|
| cor_cash_musd | 17.0 (0.70/0.75) / 20.8 (0.78/0.78) | 20.0 (0.82/0.83) / 21.9 (0.82/0.84) | 22.9 (0.94/0.83) / 22.4 (0.84/0.79) | 24.4 / 26.8 | all three beat drift; **pct_rev best** (nodrift even better rw: 16.9 / 16.6) |
| ops_cash_musd | 24.9 (1.32/1.21) / 23.1 (1.21/1.18) | **16.9 (0.90/0.83) / 17.0 (0.89/0.82)** | 21.6 (1.15/1.09) / 22.3 (1.17/1.08) | 18.8 / 17.2 (naive) | per-night beats; ratios fail (ops falls per night, rises per $ slower than revenue) |
| pd_cash_musd | 25.1 (2.49/2.56) / 23.4 (2.52/2.61) | 14.3 (1.42/1.45) / 14.0 (1.51/1.49) | 12.4 (1.23/1.23) / 12.1 (1.30/1.24) | 10.1 / 9.3 | drift wins by a wide margin; PD is a $ trend, not a ratio |
| sm_cash_musd | 40.7 (1.26/1.16) / 32.7 (1.07/1.09) | 37.6 (1.17/1.22) / 36.7 (1.20/1.22) | 37.9 (1.18/1.35) / 34.1 (1.11/1.33) | 32.2 / 30.6 | drift wins; the 2025-26 brand-marketing ramp is a $ step |
| ga_cash_ex_reserves_musd | 18.7 (1.19/1.34) / 19.2 (1.12/1.33) | 15.1 (0.96/1.18) / 17.9 (1.04/1.21) | 16.6 (1.06/1.25) / 19.8 (1.15/1.27) | 15.7 / 17.2 | nothing beats drift; (`ga_cash_musd` incl. reserves: every object 0.1-0.3 x drift, an artefact of the 4Q23 $931M reserve blowing up the drift baseline, not a result) |
| total_cash_costs_musd | 92.0 (1.85/1.92) / 72.2 (1.70/1.92) | 61.2 (1.23/1.38) / 56.7 (1.33/1.45) | 50.2 (1.01/1.07) / 36.0 (0.85/1.01) | 49.7 / 42.5 | drift on the total is very hard; SARIMA lines ties it |
| ratios (pp): cor / ops / pd / sm _cash_pct_rev | 0.64 / 0.95 / 1.01 / 1.51 (W1) | – | 0.84 / 0.82 / **0.50** / 1.34 | naive 0.64 / 0.81 / 0.80 / 1.71; drift – / – / 0.66 / 1.27 | SARIMA is the only object beating the WS10 hardest ratio baseline, for PD % (0.76 / 0.84 x drift) |
| per night (USD): cor / ops / pd / sm | – | 0.12 / 0.16 / 0.13 / 0.31 (W1); 0.15 / 0.14 / 0.12 / 0.26 (W2) | – | drift 0.15 / 0.19 / 0.12 / 0.28 (W1) | per-night growth beats drift for CoR (0.81/0.86, 0.84/0.87) and Ops (0.84/0.76, 0.79/0.73); not PD, S&M |

cov80 on the lines: 0.80-1.00 for pct_rev and per_night $ lines (too wide), 0.64 for per_night PD (W1, too narrow: PD stepped up in 2025).

## What failed, and why (honest reading)

- **Drift terms learned from 2022-23 are poison for 2023-24.** The y/y margin change was +22, +18, +1, +5 pp in 2022; any k>=2 average
  of those forecasts 2023 far too high (yoy k4_rw delta = +10.0 pp at the Feb-2023 vintage, +4.7 in May-2023). The seasonal naive with
  drift (WS10, k=1) is already worse than the plain naive; averaging more changes makes it worse still. This is the mechanism behind
  P1's failure, and it is also why the sentence rule's k was 6.3 pp at its first vintage.
- **Incremental margin is unstable** (m = 0.53 at Feb-2023, 0.33 in Aug-2023, 0.57 in May-2024, 0.21 in Feb-2026, 0.30 today) and the
  guide-cushion revenue leg overshoots in the reopening quarters, so EBITDA is over-forecast (+0.6 to +1.3 pp margin bias). With
  revenue known (`k4_rw_revknown`) the W1 MAE improves only from 2.86 to 2.77 pp: the problem is m, not revenue.
- **Per-night growth needs the nights forecast:** with nights known the W2 MAE drops from 2.06 to 1.31 pp (the Street's level) — a
  reader who trusts the team's nights nowcast (3Q26 +9.9%, band 8.5-11.0) can treat `per_night_seasonal` as a Street-quality margin
  method conditional on nights; with a naive nights leg it is not.
- **SARIMA on the margin itself** picks the airline model on 8-20 observations and over-extrapolates (bias +1.9 pp W1, +3.4 pp at h=2);
  the log-line version is respectable at h=0 but has 13-15 parameters on 22 observations and fails at h=1 (1.28 / 1.47 x naive).
- **The ensembles average four positively biased members**; inverse-MAE weights end up 0.22-0.30, close to equal, so `invmae4`
  cannot fix a shared bias. Inverse-MAE weighting is not a substitute for a member that works.
- **Sentence rule caveats:** (i) k is one number for "down slightly", "decline", "lower", "flat to down slightly" and "expand" alike —
  the ledger codes them all as +/-0 and the direction lives in `guide_type`; M3 can test whether the wording carries magnitude
  (the three "slightly" quarters realised -0.8, +1.2 and, pending, 3Q26). (ii) The rule needs a sentence: it has no h=1/h=2 forecasts
  except when management guides two quarters ahead (once, 2Q25 letter), and no 4Q26+ LIVE row. (iii) The 2Q25 miss (sentence
  "flat to down slightly", actual +1.2 pp) cost 4.0 pp; 1Q26 "approximately flat" (d=0, actual +1.0) is scored as the naive.
  (iv) Bias is negative in both windows (k too big early), so the PIT interval is right-skewed relative to outcomes: 13/14 W1 covered,
  the 1Q23 miss (-5.6 pp) falls outside.
- **Nothing here forecasts h=1 or h=2 better than y[q-4].** For the 4Q26 guide (h=1 from today) the honest time-series number is the
  naive 28.29% or the Street 28.90%.

## LIVE forecasts (vintage 2026-09-11; base = bridge v3 3Q26/4Q26 + WS06 v2b 1Q27-4Q27; bear / bull where the path has them)

Adjusted EBITDA margin, %, PIT replay, base path (q10-q90 in brackets for the main specs; Street = LSEG mean 11-13 Sep; naive = y[q-4]):

| object / spec | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 |
|---|---|---|---|---|---|---|
| q_sentence_direction k_fit_rw | **48.06** (45.9-50.2) | – | – | – | – | – |
| q_sentence_direction k_fit_median | 48.13 (45.8-50.5) | – | – | – | – | – |
| ensemble_simple invmae4 | 49.23 (45.6-52.8) | 28.14 (24.0-32.3) | 19.40 (15.6-23.2) | 34.42 (30.6-38.2) | 48.38 (44.6-52.2) | 27.30 (23.5-31.1) |
| yoy_margin_change k4_rw | 49.74 (45.4-54.1) | 27.95 (23.2-32.7) | 19.03 | 34.60 | 49.39 | 27.60 |
| pct_rev_seasonal drift_k4_rw | 49.66 (45.5-53.8) | 27.87 (23.3-32.5) | 18.96 | 34.53 | 49.24 | 27.45 |
| per_night_seasonal g_k4_rw | 50.67 (47.0-54.3) | 28.20 (23.9-32.5) | 18.64 | 34.14 | 49.41 | 25.59 |
| incremental_margin k4_rw | 47.06 (42.9-51.2) | 28.45 (24.1-32.9) | 20.63 | 34.39 | 45.48 | 28.54 |
| sarima_margin margin_aicc | 50.90 (46.9-54.9) | 29.11 (24.7-33.5) | 20.25 | 35.82 | 51.77 | 29.97 |
| sarima_margin lines_aicc | 51.50 (47.8-55.2) | 28.43 (23.8-33.1) | 19.15 | 33.27 | 49.67 | 24.93 |
| Street (LSEG, `06_consensus_quarterly_2027.csv`) | 49.78 | 28.90 | 20.29 | 35.96 | 51.15 | 30.28 |
| seasonal naive y[q-4] | 50.09 | 28.29 | 19.38 | 34.95 | – | – |
| **seasonal naive with drift (WS10)** | **51.35** | 29.56 | – | – | – | – |
| management | "down slightly" vs 50.09 (2Q26 letter) | FY26 >= 35.5% | – | – | – | – |

Adjusted EBITDA, USD m, base path (Street in the last row):

| object / spec | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 |
|---|---|---|---|---|---|---|
| q_sentence_direction k_fit_rw | 2,309 | – | – | – | – | – |
| ensemble_simple invmae4 | 2,363 | 894 | 593 | 1,387 | 2,555 | 946 |
| yoy_margin_change k4_rw | 2,389 | 888 | 581 | 1,394 | 2,608 | 956 |
| pct_rev_seasonal drift_k4_rw | 2,386 | 886 | 579 | 1,391 | 2,600 | 951 |
| per_night_seasonal g_k4_rw | 2,434 | 896 | 569 | 1,376 | 2,609 | 887 |
| incremental_margin k4_rw | 2,261 | 904 | 630 | 1,385 | 2,401 | 989 |
| sarima_margin lines_aicc | 2,474 | 903 | 585 | 1,340 | 2,623 | 864 |
| Street (LSEG) | 2,362 | 914 | 611 | 1,452 | 2,696 | 1,068 |
| revenue path (base) | 4,804 | 3,178 | 3,053 | 4,029 | 5,281 | 3,466 |

Bear / bull (revenue and nights from WS06 v2b): the ratio and yoy objects move only through the $ base (3Q26 bear/bull EBITDA
2,362 / 2,423 for pct_rev); `incremental_margin` and `per_night_seasonal` respond to the path (3Q26 margin 47.2 / 46.8 and
50.8 / 50.9; 4Q27 per-night 21.9 bear / 28.2 bull because bear nights fall while per-night costs keep growing). Full grid:
`M2_margin_ts_live_forecasts.csv` (scenario column; also every cost line in $, % of revenue and per night, 3Q26-4Q28).

LIVE cost lines, base, USD m (pct_rev drift / per_night growth / SARIMA lines): 3Q26 CoR 648 / 637 / 630, Ops 366 / 365 / 364,
PD 374 / 373 / 374, S&M 797 / 751 / 708, G&A ex-reserves 261 / 269 / 282, total cash costs 2,418 / 2,370 / 2,330; 4Q26 CoR 560 / 556 / 555,
Ops 322 / 318 / 324, PD 372 / 369 / 375, S&M 797 / 800 / 766, G&A 269 / 266 / 284, total 2,292 / 2,282 / 2,275.

Annual (`M2_margin_ts_annual_forecasts.csv`; FY26 = 1H26 actual + 3Q26/4Q26 forecast; FY28 base only, chained h=6-9):

| object / spec | FY26 margin % (EBITDA $M) | FY27 | FY28 | FY26 bear / bull | FY27 bear / bull |
|---|---|---|---|---|---|
| ensemble_simple invmae4 | 35.30 (5,037) | 34.62 (5,480) | 33.52 (5,745) | 35.25 / 35.38 | 34.20 / 34.90 |
| yoy_margin_change k4_rw | 35.45 (5,057) | 35.00 (5,540) | 34.65 (5,937) | 35.43 / 35.49 | 34.86 / 35.07 |
| pct_rev_seasonal drift_k4_rw | 35.41 (5,052) | 34.89 (5,522) | 34.46 (5,906) | 35.39 / 35.45 | 34.75 / 34.95 |
| per_night_seasonal g_k4_rw | 35.82 (5,111) | 34.37 (5,441) | 31.19 (5,345) | 35.58 / 36.09 | 32.69 / 35.54 |
| incremental_margin k4_rw | 34.66 (4,945) | 34.15 (5,406) | 33.80 (5,793) | 34.69 / 34.61 | 34.42 / 33.95 |
| sarima_margin margin_aicc | 36.10 (5,151) | 36.86 (5,834) | 37.71 (6,463) | 36.07 / 36.15 | 36.71 / 36.93 |
| sarima_margin lines_aicc | 36.15 (5,157) | 34.19 (5,412) | 30.38 (5,206) | 35.67 / 36.70 | 30.28 / 37.17 |
| Street (LSEG 11 Sep) | 35.62 (5,054) | 36.45 (5,766) | 37.65 (6,603) | – | – |
| management | >= 35.5% (2Q26 letter) | – | – | – | – |
| revenue (base / bear / bull) | 14,268 / 14,165 / 14,392 | 15,829 / 14,948 / 16,571 | 17,137 | | |

Reading the annuals: every time-series object that has passed any test puts FY26 at 35.3-35.8%, on or just above the floor and at
the Street; for FY27 the ratio / per-night objects extrapolate the 2025-26 S&M ramp and the ops-per-night decline and land at
34.2-35.0%, **1.5-2.2 pp below the Street's 36.45%** — that gap is the S&M drift (+2.3 pp of revenue y/y) carried one more year,
which is a spending decision M1/M3 should overrule with evidence, not a forecast. The SARIMA margin path (36.9 / 37.7) is the
airline model extrapolating the 2024-26 seasonal pattern and is the least trustworthy row (bias +1.9 pp in backtest).

## Figures

`analysis/figures/margin_build/M2_margin_ts_h0_errors_w1.png` (h=0 margin errors by quarter, W1, main specs vs naive and Street);
`analysis/figures/margin_build/M2_margin_ts_live_margin_path.png` (LIVE margin path 3Q26-4Q27 by object vs Street and naive).

## Parameter counts (registry `n_params` = rule parameters + 1 residual sd)

yoy_margin_change 2 (+1 shrink) -> 3-4; incremental_margin 2 -> 3; pct_rev_seasonal 6 (nodrift 1) -> 7 (2); per_night_seasonal 6 (nogrowth 1)
-> 7 (2); sarima_margin margin 2-3 (+1 selection) -> 4, lines 10-15 -> 14-15; ensemble eq4 0 -> 1, invmae4 4 -> 5; q_sentence_direction 1 -> 2.
Fixed choices not counted: half-life 4 quarters (brief), the 10%-of-revenue exclusion in the incremental-margin pairs, SARIMA training
start 1Q21, the 4-candidate SARIMA grid, ENS_ERR_N = 8, RESID_MAX_N = 12 (WS10 convention). Observations: 26 quarters; W1 14 / W2 10 targets.

## Corrections to existing work

None to data. Two notes for other agents: (1) WS10's "k = 1.5 pp rule scores 1.43 / 1.17" is in-sample; the PIT-fitted version scores
2.07 / 1.64 (this note), and the full-sample k is 2.03, not 1.5. (2) The five cash lines ex-reserves do not sum to `total_cash_costs_musd`
(= revenue - adj EBITDA); the residual is the non-reserve add-backs, -0.2 to -1.3% of revenue since 2022 (-0.50% in 2Q26). Any line
model that closes to EBITDA needs this sixth component; here it is carried at last year's ratio / per-night value.

## For the model

| item | value | unit | source |
|---|---|---|---|
| sentence-direction k (rw regression through origin, pool n=16, vintage 2026-09-11) | 2.03 (median 1.95; ew 3.06) | pp | `M2_margin_ts_params_by_vintage.csv`, object q_sentence_direction |
| 3Q26 margin, sentence rule (d = -1, "down slightly") | 48.06, q10-q90 45.9-50.2, sd 1.69 | % | `M2_margin_ts_live_forecasts.csv` |
| 3Q26 EBITDA, sentence rule x bridge v3 revenue $4,804M | 2,309 (bear 2,285 / bull 2,344) | USD m | same |
| honest PIT accuracy of that rule at h=0 | MAE 2.07 W1 (n=14) / 1.64 W2 (n=10); rw 1.53 / 1.38; bias -1.8 / -1.3 | pp | `scoreboard_margin.csv`, spec k_fit_rw |
| Street to beat (unchanged) | 1.59 / 1.31 (rw 1.25 / 1.12) | pp | WS10 |
| seasonal-naive-with-drift 3Q26 | 51.35 (naive 50.09 + 2Q26 y/y +1.26) | % | WS10 baseline registry |
| yoy_margin_change delta (k4, rw) at TODAY | -0.35 | pp | params file |
| incremental margin m (k4, rw) at TODAY | 0.296 (k8 0.308; median 0.355) | $ EBITDA per $ revenue y/y | params file |
| % of revenue drift by line (k4, rw, y/y) | CoR +0.09, Ops -0.77, PD -0.35, S&M +2.30, G&A ex-res -0.85 | pp of revenue | params file |
| per-night growth by line (k4, rw, y/y) | CoR +5.6%, Ops -3.1%, PD +1.9%, S&M +16.8%, G&A -4.8% | % | params file |
| other add-backs component | -0.56 (3Q25 value used for 3Q26) | % of revenue | harness targets, this note |
| ratio-object FY27 margin (base path) | 34.4-35.0 vs Street 36.45 | % | annual file |

## For the 5 Nov card

- Time-series anchor for the 3Q26 print: **48.1% (45.9-50.2)**, i.e. 2.0 pp below 3Q25, from the sentence rule; the Street is at
  49.78% (-0.3 pp y/y) and a naive extrapolation of 2Q26's expansion would say 51.35%. Every tested object that beats the naive sits
  at or below the Street for 3Q26 except the SARIMA lines (51.5%); the objects' spread 47-51.5% is the honest "we do not know"
  from time series alone. EBITDA $2.31-2.47B against the Street's $2.36B.
- 4Q26 (the quarter that will be guided on 5 Nov): nothing here beats y[q-4] at h=1; naive 28.29%, Street 28.90%, objects 27.9-29.1%.
- FY26: 35.3-35.8% from the objects that passed anything; consistent with "at least 35.5%" being met but not with a raise to 36%.
- The sentence rule is a good candidate for the language-pattern method (M3): the 5 Nov 4Q26 sentence's direction has been right
  13/14 times and is worth ~2 pp; the magnitude words are the open question.

## RESUME

M2 is complete: seven objects registered under `margin-ts` (29 specs, both replays, PIT quantiles), scorer re-run, LIVE and annual
tables written, two figures, this note. The next agent (WS20 scoreboard / WS21 red team / M3) should: (1) take `q_sentence_direction|k_fit_rw`
as the time-series anchor and check its leakage surface — `q_guide_in_force` reads the ledger's `print_date` as the guide date and the
k pool uses only quarters whose actual printed <= vintage; (2) note P1 failed and do not quote objects 1-4 on the margin, only the
per-night object conditional on nights (W2 1.31 pp with nights known) if M1 supplies a nights forecast; (3) for lines, treat
`seasonal_naive_drift` as the bar for PD and S&M and `per_night_seasonal|g_k4_rw` for CoR and Ops; (4) if WS06 writes a new `_v2b`,
re-run `run.py` (72 s) — it picks the override up automatically and the note's LIVE tables would need refreshing from
`M2_margin_ts_live_forecasts.csv`; (5) WORKBOARD.md was not touched (outside the write scope in `00_BRIEF.md`; the orchestrator appends
rows at stage 32). Do not add specs to chase the Street: the pre-registered grid is closed at 29.
