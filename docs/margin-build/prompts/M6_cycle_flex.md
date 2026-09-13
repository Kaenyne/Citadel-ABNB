# M6: Cycle and cost-flex model: how costs respond to growth deceleration, and the scenario engine

Read `docs/margin-build/prompts/M_common.md` first. Slug: `M6_cycle_flex`. Method name: `cycle-flex`.
Inputs: WS02 (`02_macro_cycle_episodes.csv`, panel, seasonality), WS05 statements on cuts/holds, WS06/06v revenue paths (bear/base/bull),
WS03 peer consensus (BKNG, EXPE) and the repo's peer financials (`data/processed/overnight/07_peer_margin_benchmark.csv`, `abnb_vs_bkng_annual.csv`;
pull BKNG/EXPE quarterly cost lines from EDGAR companyfacts if useful), FRED macro (UMich sentiment, real PCE services, TSA throughput if WS04 pulled it).

## Two parts

A. **Cyclicality, measured.** (i) Seasonal: the within-year margin profile decomposed into the mechanical part (revenue timing vs flat costs) and
the discretionary part (Q1 brand campaign, Q4 hiring) using WS02's per-night and %-of-revenue views; how stable the Q1/Q2/Q3/Q4 margin shares
have been 2022-25 and what a 2026 Q3/Q4 profile looks like under the adopted revenue path. (ii) Macro: for each episode (2020, 2H22, 2023 ADR
normalisation, 2025 NA slowdown) the response of each cash line's growth to the change in revenue growth, with lags 0-2 quarters; an asymmetry
test (do costs fall as fast as they rise); what management cut and when (WS05). Fit a small pooled regression: line growth_q = c + k * revenue
growth_{q-lag} + episode dummies, recency weighted; report k per line with n and whether it is stable. Compare with BKNG/EXPE k's.

B. **Scenario engine.** A function `flex(cost_path_base, revenue_path_scenario)` that maps the bear/bull revenue paths into cost paths using
the estimated k's (with a "management holds spend" and a "management cuts to defend the floor" variant, the latter using the 31a/WS05 statements on
the margin floor and the FY24-25 evidence of brand-marketing phasing). Register the base LIVE path as a normal object (it should be close to M1's
base) and write bear/bull as scenario columns; the harness scores only the base.

## Tests (pre-register)

Backtest the flex model as a forecaster of the lines at h=0/1 in W1/W2 (it will be a weak forecaster in calm quarters; the point is the shock
quarters: report MAE on 2H22 and 2025 quarters separately). Pass line: k for sm and pd significantly different from zero with the expected sign
at some lag in the pooled regression, and the scenario engine reproduces the 2H22 margin path within 1.5 points when fed the actual revenue path.

## LIVE

Margin 3Q26-4Q27 and FY26-28 under bear/base/bull revenue with costs flexed vs held; the FY26 floor (35.5%) break-even: how much revenue
shortfall the floor survives under each cost-response variant; the seasonal Q1 2027 trough estimate. Feed the scenario table to WS23.
