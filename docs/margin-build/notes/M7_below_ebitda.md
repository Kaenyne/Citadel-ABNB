# M7. Below-EBITDA bridge (SBC, D&A, interest income, tax, share count, EPS) and the free-cash-flow bridge

Margin build run, 13-14 Sep 2026. Slug `M7_below_ebitda`. Method `below-ebitda`. Interpreter `py -3.13`.
Script `analysis/src/margin_build/M7_below_ebitda/run.py`. Data `data/processed/margin_build/M7_below_ebitda/`.
Registry `data/processed/margin_build/registry/below-ebitda__*.csv`.

## Pre-registration (written 13 Sep 2026 23:55, before any fit was run)

Objects, targets, rules, free parameters (rule parameters + 1 for the fitted residual sd, the frozen convention):

| object | targets | rule (main spec `rw_hl4`; `eq` variant equal-weighted) | params |
|---|---|---|---|
| `interest_income` | `interest_income_musd` | II = beta x r x avg(cash + STI + funds held)/4. beta = recency-weighted mean of the realised ratio II / (r x avgB/4) over the last 8 quarters with 3m T-bill >= 0.5% (ZIRP quarters excluded). r = 3m T-bill (FRED DTB3 daily): realised days of the target quarter to the vintage date, spot at the vintage date held constant for the rest. Funds held at quarter-end = same quarter last year x (1 + last known y/y GBV growth); cash + STI flat at the last balance sheet. | 1 + 1 |
| `sbc` | `sbc_musd`, `sbc_pct_rev` | SBC = SBC[q-4] x (1 + g), g = recency-weighted mean of the last 4 y/y growth rates (chained when q-4 is itself a forecast). % of revenue uses the harness PIT revenue leg. | 1 + 1 |
| `da` | `da_musd` | recency-weighted mean of the last 4 quarters (variant `last_value`). | 1 + 1 |
| `tax` | `tax_rate_pct` | ETR = the FY tax-rate sentence in force for the target quarter's fiscal year (hand ledger from WS05 statements, 6 rows, each with its date), else the trailing-4-quarter ETR (sum of provisions / sum of pretax; winsorised to [10, 30] when a discrete item makes it wild). Variant `ttm` ignores the guides. | 1 + 1 |
| `share_count` | `diluted_shares_m` | shares = last WA diluted count + steps x d, d = recency-weighted mean of the last 4 quarterly changes. Variant `structural` (LIVE and backtest): d = -(trailing-4 buyback $ / share price at the vintage) + implied net award issuance (recency-weighted mean of the last 4 quarters' change + buyback / quarter-average price). | 1 + 1 (structural 2 + 1) |
| `eps` | `eps_diluted`, `net_income_musd`, `op_income_musd`, `pretax_income_musd`, `tax_provision_musd` | waterfall: adj EBITDA - D&A - SBC - expected other add-backs (0) = operating income; + interest income - interest expense (last known; LIVE $37M/q on the March 2026 notes) + other income (recency-weighted mean of the last 8) = pretax; tax = ETR x pretax; NI / diluted shares = EPS. Two adj EBITDA inputs: `ebitda_known` (the actual, so the row isolates below-the-line error) and `ebitda_pit` (the harness baseline in force at the vintage: `q_guide_implied` if it exists for the quarter, else `guide_implied`, else `seasonal_naive_drift`). LIVE: the M1 `driver-lines` base if registered, else M2 `margin-ts`, else `seasonal_naive_drift` (labelled). | 5 + 1 (plus the EBITDA input's own) |
| `fcf` | `cfo_musd`, `fcf_musd`, `fcf_margin_pct`, `capex_musd` | CFO = NI + D&A + SBC + change in unearned fees + change in funds payable + other. Main `swing_x_gbv`: each working-capital swing = same quarter last year x (1 + last known y/y GBV growth) (0 fitted parameters). Variant `balance_ratio`: quarter-end balance = same-quarter ratio to GBV (recency-weighted over the last 3 years) x GBV forecast, swing = balance - prior balance. Other = recency-weighted mean of the last 8 residuals. Capex = recency-weighted mean of the last 4. FCF = CFO - capex. NI from the `eps` chain (`ebitda_pit` main, `ebitda_known` variant). | 2 + 1 (balance_ratio 6 + 1) |

Backtest design: point-in-time refits at each of the 20 frozen guide dates 2021-11-04 .. 2026-08-06 (the first five only feed the residual pools), horizons h=0,1,2, registered for the 14 W1 and 10 W2 dates; LIVE at 2026-08-06 and 2026-09-11 for h=0..5 (3Q26-4Q27). Both replays (`PIT` and `full_sample`). Quantiles Gaussian on the walk-forward residual pool of the same object/target/horizon (PIT: last 12 realised before the vintage; full_sample: all), relative for strictly positive levels, additive for EPS, tax rate and zero-crossing levels; h>=3 borrows the h=2 pool.

Pass lines (a claim needs both windows, both weightings; scored by `10_harness_margin/score.py`):

1. `interest_income`: MAE below `seasonal_naive` at h=0 and h=1 in W1 and W2 (prompt). Stretch (reported, not required): below `seasonal_naive_drift`, the hardest baseline (W1 h0 22.0 / W2 h0 15.5 $M).
2. `fcf`: quarterly `fcf_musd` MAE below `seasonal_naive` at h=0 in both windows (hardest baseline: seasonal_naive, W1 234.6 / W2 203.4 $M); FY FCF: sum of the h=0..3 forecasts made at the February guide date beats the seasonal naive (prior FY actual) on absolute error in at least 3 of the 4 complete years FY2022-25 (n 4; FY2026 pending).
3. `eps`: no pass line (the prompt asks for the error decomposition). Report: on the last 8 prints (3Q24-2Q26, h=0) the share of the `ebitda_pit` EPS error explained by the EBITDA input vs the below-the-line lines, and both against the pre-guide Street EPS.
4. `sbc`, `da`, `tax`, `share_count`: MAE below `seasonal_naive` at h=0 in both windows; reported against `seasonal_naive_drift` / `trailing4`, which are the hard baselines for these targets and which I do not expect to beat by much (the rules are near-equivalent).

Tests counted: 4 pass/fail (1, 2 quarterly, 2 annual, 4 as a block of four targets) plus the descriptive decomposition.
Which weighting goes in the pitch: recency-weighted, because every one of these lines has a 2025-26 regime (notes replacing the converts, OBBBA, the buyback pace, the SBC step-up in 2Q24 and 2Q26).
