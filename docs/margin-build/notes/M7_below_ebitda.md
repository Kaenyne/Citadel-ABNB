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

---

## Bottom line

1. **The below-EBITDA bridge is the reliable half of the P&L.** Six of the seven objects beat the seasonal naive at h=0
   in **both** windows under **both** weightings. Interest income — the line the prompt flags as large relative to net
   income — is the best result in the package: MAE **$17.9M (W1, n 14)** and **$10.5M (W2, n 10)** at h=0, i.e. 0.32x /
   0.42x the seasonal naive and 0.81x / 0.68x the hardest baseline (`seasonal_naive_drift`), on a line running
   $155-190M a quarter. One parameter (a yield beta of 0.876) plus a residual sd.
2. **The waterfall reproduces the Street's EPS from the Street's EBITDA.** Feed the LSEG 3Q26 consensus adj. EBITDA
   ($2,361.5M) through M7's D&A, SBC, interest, tax and share-count rules and you get **$2.83** against the LSEG EPS mean
   of **$2.85**. That two-cent gap is the whole below-the-line disagreement between this model and the sell side for 3Q26;
   the EPS debate on 5 Nov is an EBITDA debate, not a bridge debate.
3. **FCF is the failure.** Quarterly FCF does not beat the seasonal naive (best spec 1.02x W1 / 0.93x W2 equal-weighted,
   1.09x / 1.05x recency-weighted — so it fails both-windows and fails the recency test outright). Airbnb's quarterly cash
   flow is dominated by the funds-payable / unearned-fee swing, which is almost perfectly seasonal; y[q-4] is very hard to
   beat. The **annual** FCF test passes (3 of 4 complete years FY2022-25, the pre-registered line).
4. **LIVE, on M1's driver-lines adj EBITDA:** 3Q26 EPS **$3.00** (Street $2.85), 4Q26 **$0.78** (Street $0.86),
   FY26 **$5.39** (Street $5.31), FY27 **$5.84** (Street $6.23), FY28 **$6.40** (Street $7.52). FY26 FCF **$4.91-5.13bn**
   (Street $4.92bn). We are above the Street on 3Q26 because M1's EBITDA is $125M above it; we are **below** the Street
   from FY27 because M1 holds the margin at 35.1% while the Street underwrites 36.4% (FY27) and 37.7% (FY28).
   The FY27-28 EPS gap to the Street is almost entirely an EBITDA-margin disagreement, not a tax, share-count or interest one.
5. **Rate sensitivity is the biggest non-EBITDA swing factor.** +/-100bp on the T-bill is +/-$49M of pre-tax income a
   quarter, ~+/-$0.07 of quarterly EPS and **+/-$0.29 on FY27 EPS** — larger than the whole ETR 16-19% range (+/-$0.11
   at the FY27 level) and larger than the buyback-renewal question (-$0.20).

## What ran (exact commands, interpreter `py -3.13`)

```
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/M7_below_ebitda/run.py       # ~6 min, exit 0; PIT grid -> registry -> LIVE -> scorer -> figures
py -3.13 analysis/src/margin_build/M7_below_ebitda/figures.py   # figures only
py -3.13 analysis/src/margin_build/10_harness_margin/score.py   # re-run by run.py itself
```

**Reproducibility check (13 Sep, 14:44-14:47).** `run.py` was re-run from scratch over the outputs written overnight and
every one of the twelve processed CSVs and all seven registry files came back **byte-identical**; only `M7_build_log.txt`
differs, in its timestamp line. Exit code 0. A second run at 14:49-14:53 (after the FY28 patch below) also exited 0.
FRED pulls (`DTB3`, `DGS1`, `DGS2`) are cached under `data/raw/margin_build/M7_below_ebitda/` with a committed manifest at
`data/manifests/margin_build/M7_below_ebitda.csv`; delete the raw files to force a re-pull.

**Registration check.** 9,648 rows across the seven objects (`below-ebitda__{da,eps,fcf,interest_income,sbc,share_count,tax}.csv`):
4,992 W1, 3,456 W2, 1,200 LIVE (vintages 2026-08-06 and 2026-09-11, quarters 3Q26-4Q27); both replays present on every row
(`replays_present = 2`). The harness validator accepted all of them. `score.py` writes the scoreboard, of which **768 rows are
`below-ebitda`** — the scorer picks the method up on all seven objects and all 15 targets.

## Method — the seven objects, their equations and their parameters

Free parameters are counted the frozen way: rule parameters + 1 for the fitted residual sd.

| object | equation (main spec, `rw` = exponential half-life 4) | free params | variants registered |
|---|---|---|---|
| `interest_income` | `II = beta x r x (cash + STI + funds held)_avg / 4`; `beta` = recency-weighted mean of realised `II / (r x B/4)` over the last 8 quarters with DTB3 >= 0.5% (ZIRP excluded); `r` = realised DTB3 days of the target quarter to the vintage, spot held flat thereafter | **2** | `rate_x_base` x {rw, eq} |
| `sbc` | `SBC[q] = SBC[q-4] x (1 + g)`, `g` = recency-weighted mean of the last 4 y/y rates (13.18% at TODAY); chained when q-4 is itself a forecast | **2** | `yoy` (mean of 4), `yoy_last` (last y/y only) x {rw, eq} |
| `da` | recency-weighted mean of the last 4 quarters ($20.6M); variant = last value ($17.0M) | **2** | `mean4`, `last_value` x {rw, eq} |
| `tax` | the FY tax-rate sentence in force for the target fiscal year (WS05 ledger, 6 dated rows), else the trailing-4-quarter ETR winsorised to [10, 30] | **2** | `guide_or_ttm`, `ttm` x {rw, eq} |
| `share_count` | `shares[q] = shares[last] + h x d`, `d` = recency-weighted mean of the last 4 quarterly changes (-5.32M/q) | **2** | `delta`, `structural` (= -buyback$/price + implied net award issuance) x {rw, eq} |
| `eps` | adj EBITDA - D&A - SBC = operating income; + interest income - interest expense ($37M/q) + other income ($3.7M/q) = pre-tax; x (1 - ETR) = net income; / diluted shares = EPS | **6** (+ the EBITDA input's own) | `ebitda_known` (actual EBITDA in, isolates the bridge), `ebitda_pit` (the harness baseline in force) x {rw, eq} |
| `fcf` | `CFO = NI + D&A + SBC + dUnearnedFees + dFundsPayable + other`; each swing = same quarter last year x (1 + last known GBV y/y); `capex` = rw mean of the last 4 ($8.9M/q); `FCF = CFO - capex` | **3** | `swing_x_gbv`, `swing_x_gbv_seasonal_other` (other = same-quarter rw mean), `balance_ratio` (6 params), each also `_ebitda_known`, x {rw, eq} |

Interest expense is a hard $37M/quarter from the 2Q26 10-Q (the $2.5bn March 2026 notes at 4.40 / 4.65 / 5.25% = ~$119M/yr of
coupon plus issuance-cost amortisation and swap carry; $1.7bn is swapped to SOFR, so +/-100bp is +/-$17M/yr). Expected "other
add-backs" (lodging-tax reserves, acquisition marks) are set to **0** as an expected value — FY2025 realised $83M, all in 4Q25.

**What LSEG's EPS field measures.** WS03 (`docs/margin-build/notes/03_consensus_pit.md`) verified that `TR.EPSMean`'s actual is
the Street-comparable adjusted EPS and that it **matches the repo's GAAP diluted EPS to the cent in every W2 quarter**
(1Q24-2Q26); only 3Q23 and 4Q23 (the valuation-allowance release and the lodging-tax reserve) are handled by LSEG's own actual.
So for ABNB today there is no second "non-GAAP EPS" to model: GAAP diluted EPS **is** the Street definition, and M7 forecasts
one EPS number, flagging the two historical quarters where the bases diverge.

## Backtest — PIT replay, main recency-weighted spec, both windows, h=0/1/2

Point-in-time refits at 20 frozen vintages (2021-11-04 .. 2026-08-06; the first five only feed the residual pools); registered
rows at the 14 W1 and 10 W2 guide dates. `r_sn` = MAE ratio to `seasonal_naive` (equal-weighted errors); `rw_r_sn` = the same
ratio with exponential half-life-4 weights; `r_snd` = ratio to `seasonal_naive_drift`. Lower is better; **< 1 beats it**.

| object / target | h | n W1 | n W2 | MAE W1 | MAE W2 | r_sn W1 | r_sn W2 | rw_r_sn W1 | rw_r_sn W2 | r_snd W1 | r_snd W2 | survives | rw_survives |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| interest_income / `interest_income_musd` | 0 | 14 | 10 | 17.9 | 10.5 | 0.317 | 0.417 | 0.337 | 0.376 | 0.810 | 0.680 | **yes** | **yes** |
| interest_income | 1 | 13 | 9 | 20.4 | 7.8 | 0.409 | 0.358 | 0.367 | 0.315 | 0.540 | 0.281 | **yes** | **yes** |
| interest_income | 2 | 12 | 8 | 25.3 | 11.9 | 0.638 | 0.589 | 0.621 | 0.585 | 0.491 | 0.299 | **yes** | **yes** |
| sbc / `sbc_musd` | 0 | 14 | 10 | 10.8 | 10.9 | 0.195 | 0.185 | 0.178 | 0.173 | 0.931 | 0.961 | **yes** | **yes** |
| sbc | 1 | 13 | 9 | 19.2 | 21.9 | 0.341 | 0.370 | 0.356 | 0.370 | 1.068 | 1.131 | **yes** | **yes** |
| sbc | 2 | 12 | 8 | 25.3 | 30.9 | 0.450 | 0.545 | 0.501 | 0.549 | 1.125 | 1.184 | **yes** | **yes** |
| da / `da_musd` | 0 | 14 | 10 | 2.7 | 2.5 | 0.392 | 0.463 | 0.506 | 0.531 | 0.809 | 1.000 | **yes** | **yes** |
| da | 1 | 13 | 9 | 4.1 | 3.7 | 0.671 | 0.647 | 0.723 | 0.702 | 0.679 | 0.892 | **yes** | **yes** |
| tax / `tax_rate_pct` | 0 | 14 | 10 | 17.95 pp | 7.32 pp | 0.431 | 0.270 | 0.485 | 0.423 | 0.228 | 0.156 | **yes** | **yes** |
| tax | 1 | 13 | 9 | 18.46 pp | 6.90 pp | 0.545 | 0.229 | 0.502 | 0.378 | 0.256 | 0.140 | **yes** | **yes** |
| share_count / `diluted_shares_m` | 0 | 14 | 10 | 4.83 | 4.08 | 0.225 | 0.209 | 0.151 | 0.134 | 0.395 | 0.669 | **yes** | **yes** |
| share_count | 1 | 13 | 9 | 7.79 | 6.23 | 0.381 | 0.313 | 0.244 | 0.209 | 0.689 | 0.863 | **yes** | **yes** |
| eps / `eps_diluted` (`ebitda_pit`) | 0 | 14 | 10 | 0.492 | 0.125 | 0.507 | 0.177 | 0.421 | 0.241 | 0.275 | 0.087 | **yes** | **yes** |
| eps / `eps_diluted` | 1 | 13 | 9 | 0.562 | 0.155 | 0.546 | 0.203 | 0.484 | 0.310 | 0.300 | 0.102 | **yes** | **yes** |
| eps / `eps_diluted` (`ebitda_known`) | 0 | 14 | 10 | 0.458 | 0.066 | 0.472 | 0.093 | 0.352 | 0.138 | 0.256 | 0.046 | **yes** | **yes** |
| eps / `net_income_musd` | 0 | 14 | 10 | 320.6 | 79.4 | 0.510 | 0.174 | 0.424 | 0.236 | 0.274 | 0.084 | **yes** | **yes** |
| eps / `op_income_musd` | 0 | 14 | 10 | 114.6 | 72.9 | 0.553 | 0.424 | 0.494 | 0.428 | 0.312 | 0.199 | **yes** | **yes** |
| eps / `pretax_income_musd` | 0 | 14 | 10 | 121.5 | 80.8 | 0.482 | 0.412 | 0.472 | 0.427 | 0.303 | 0.199 | **yes** | **yes** |
| eps / `tax_provision_musd` | 0 | 14 | 10 | 239.8 | 38.2 | 0.513 | 0.103 | 0.417 | 0.206 | 0.274 | 0.056 | **yes** | **yes** |
| **fcf / `fcf_musd`** | 0 | 14 | 10 | 238.7 | 188.5 | **1.018** | 0.927 | **1.090** | **1.054** | 0.641 | 0.522 | **NO** | **NO** |
| fcf / `cfo_musd` | 0 | 14 | 10 | 239.2 | 189.3 | 1.013 | 0.922 | 1.092 | 1.056 | 0.638 | 0.518 | **NO** | **NO** |
| fcf / `fcf_margin_pct` | 0 | 14 | 10 | 9.32 pp | 7.05 pp | 1.219 | 0.999 | 1.126 | 1.039 | 0.674 | 0.498 | **NO** | **NO** |
| fcf / `capex_musd` | 0 | 14 | 10 | 4.42 | 4.43 | 0.815 | 0.821 | 1.010 | 1.040 | 0.938 | 0.836 | yes (eq only) | **NO** |
| sbc / `sbc_pct_rev` | 0 | 14 | 10 | 0.72 pp | 0.60 pp | 1.050 | 0.731 | 1.094 | 0.994 | 1.131 | 0.966 | **NO** | **NO** |

Against the **Street** — the hardest baseline for EPS, net income and operating income (`hardest_baseline_by_target.csv`):
`eps_diluted` h=0 ratio **0.939 in W1** and **1.044 in W2**; `net_income_musd` 0.938 / 1.030; `op_income_musd` 1.026 / 1.243.
Read honestly: with a point-in-time EBITDA input, this bridge is marginally better than the pre-guide Street over the whole
2023-26 window and marginally worse over 2024-26. **It is not an alpha source against the Street; it is a consistent,
auditable bridge** whose value is that it turns any EBITDA view into EPS and FCF with known error bars.

**Equal- vs recency-weighted.** The two weightings agree on every pass/fail verdict above. They disagree on magnitude in two
places worth naming: `tax_rate_pct` in W2 (MAE 7.32 pp equal-weighted vs 9.03 pp recency-weighted — the recent quarters include
the 43.1% print in 1Q26 and the 9.0% in 2Q26, so recency makes the tax line look *worse*, not better), and `da_musd` W1 h=0
(0.392 vs 0.506 — D&A stepped down through 2025-26, so the older errors flatter the rule). The pitch uses the
**recency-weighted** statistics, as pre-registered: every one of these lines has a 2025-26 regime (the March 2026 notes
replacing the converts, OBBBA, the ~$1.0bn/quarter buyback pace, the SBC step-ups in 2Q24 and 2Q26).

**Spec selection inside each object.** The scoreboard prefers `yoy_last` over `yoy` for SBC (W2 h=0 ratio 0.185 vs 0.330) and
`last_value` over `mean4` for D&A (0.463 vs 0.606). The LIVE **waterfall** was built on the pre-registered main rules
(`yoy` for SBC, `mean4` for D&A), which puts 3Q26 SBC at $452M rather than $458M and D&A at $20.6M rather than $17.0M — a
~$10M pre-tax difference, about $0.01 of EPS. I have not rebuilt the waterfall on the post-hoc winners; the registry carries
both specs and the scorer keys on `spec_id`, so anyone can take the winning spec — but say which you used.

**Coverage.** `cov80` is 1.00 on almost every object (the Gaussian residual pools are wide): the intervals are honest but
conservative. The exceptions are `tax_rate_pct` (0.86 W1 / 0.90 W2) and `tax_provision_musd` (0.71 / 0.70), which are
**under**-covered because the tax line has fat tails from discrete items. Do not quote the tax quantiles as a real 80% interval.

## Pass / fail against the pre-registration

| # | test | pass line | result | verdict |
|---|---|---|---|---|
| 1 | `interest_income` | MAE < `seasonal_naive` at h=0 and h=1 in W1 and W2 | 0.317 / 0.409 (W1), 0.417 / 0.358 (W2); recency 0.337 / 0.367, 0.376 / 0.315 | **PASS** |
| 1s | stretch: also beat `seasonal_naive_drift` | not required | 0.810 / 0.540 (W1), 0.680 / 0.281 (W2); recency 0.741 / 0.418, 0.678 / 0.294 | **PASS** |
| 2a | `fcf` quarterly | MAE < `seasonal_naive` at h=0 in both windows | 1.018 W1 / 0.927 W2 equal-weighted; 1.090 / 1.054 recency | **FAIL** |
| 2b | FY FCF from the February vintage | beats the prior-FY-actual naive in >= 3 of 4 complete years | FY22 err +467 vs naive -1,117; FY23 +742 vs -432 (**loss**); FY24 +348 vs -647; FY25 +40 vs -129 -> **3 of 4** | **PASS** |
| 3 | `eps` decomposition | descriptive, no pass line | delivered below | n/a |
| 4 | `sbc`, `da`, `tax`, `share_count` | MAE < `seasonal_naive` at h=0 in both windows | 0.195 / 0.185, 0.392 / 0.463, 0.431 / 0.270, 0.225 / 0.209; recency all < 1 | **PASS (4/4)** |

FY FCF detail (`M7_fy_fcf_test.csv`, forecast made at the February guide date of each year, actual in brackets):
FY2022 $3,872M (3,405), FY2023 $4,579M (3,837), FY2024 $4,832M (4,484), FY2025 $4,653M (4,613), FY2026 $5,093M (pending).
The model is biased **high** on FY FCF in every year (mean +$399M), but by less than the naive's error in three of four.

Tests counted: **4 pass/fail blocks** (the FCF block splits into a quarterly and an annual leg that disagree) plus the
descriptive EPS decomposition. Score: 4 of 5 legs pass, 1 fails.

## What failed, and why (written up, not deleted)

1. **Quarterly FCF.** The seasonal naive is brutal here. Airbnb's CFO in any quarter is dominated by the change in funds
   payable and unearned fees, which is a near-mechanical function of the booking calendar: 1Q builds the balance
   (+$1.1-1.2bn of unearned fees), 3Q releases it (-$1.3bn). `y[q-4]` captures that almost exactly, so a model that
   *forecasts* the swing from GBV growth adds variance without adding signal. Best spec MAE $238.7M (W1) against the naive's
   $234.6M. Where the model does win is against every other baseline — 0.64x `seasonal_naive_drift` and **0.60x the Street's
   own FCF estimate** (W1 h=0; 0.49x in W2) — so the FCF line is worth carrying, just not as a claimed edge over the naive.
2. **The `other` line of CFO is the whole problem.** `M7_cfo_other_residual_history.csv` shows the residual
   (CFO - NI - D&A - SBC - dUnearnedFees) oscillating +$599M (3Q25) / -$352M (4Q24) / +$342M (1Q24) / -$243M (2Q25) with no
   trend. The `swing_x_gbv_seasonal_other` variant, which models that residual as a same-quarter recency-weighted mean instead
   of a flat $21M, cuts W2 h=0 MAE from $293.8M to $188.5M — a 36% improvement, and the reason it is the spec I would quote —
   but it still cannot clear the naive in W1.
3. **`sbc_pct_rev` fails** (1.050 W1 / 0.731 W2 equal-weighted; 1.094 / 0.994 recency). Forecasting SBC as a ratio to revenue
   is worse than forecasting the dollars, because revenue seasonality dominates the ratio. Use `sbc_musd` and divide.
4. **`capex_musd`** passes equal-weighted (0.815 / 0.821) and fails recency-weighted (1.010 / 1.040). Capex is $5-17M a
   quarter — 0.2% of revenue — so I would not defend either result. Note the model's $8.9M/quarter sits **below** the Street's
   $14.1M for 3Q26; if the Street is right, FY26 FCF is ~$20M lower than shown.
5. **The tax line is unforecastable in the tails.** W1 MAE is 17.95 pp because 3Q23 printed a -161% effective rate (the
   valuation-allowance release) and 1Q26 printed 43.1%. The rule still beats every baseline (0.23x `seasonal_naive_drift`,
   0.53x `trailing4`), but the correct reading is "the ETR rule is right on the FY, wrong on any single quarter".
6. **A defect found and fixed in this session.** The FY28 EBITDA rule (FY27 margin of the source x FY28 revenue) was dividing
   M1's FY27 EBITDA **dollars** by the *scenario's* FY27 revenue, so the bear path produced a higher implied margin and FY28
   bear EBITDA came out **above** base ($6,377M vs $6,022M) — inverted. Fixed in `run.py` (the FY27 margin denominator is now
   always the base revenue path) and re-run: FY28 EBITDA is now $6,022M in base, bear and bull alike, which is the honest
   representation, since the WS06 bear and bull revenue paths stop at 4Q27 and FY28 carries the base revenue. Bear and bull
   differ from base in FY26-27 only through interest income and working capital, **not** through EBITDA — M1 supplies a single
   LIVE EBITDA level, not a margin, so it does not flex with the revenue scenario. Do not read the bear/bull rows as EBITDA
   scenarios.
7. **Not attempted.** Headcount-driven SBC (the 10-K headcount series is annual, n 5, and WS04 found no usable job-postings
   panel), the convertible notes (fully settled; no dilution left to model), and a futures-implied rate path (no free public
   source for SOFR / fed-funds futures inside the sanctioned list — the +/-100bp band is the substitute).

## EPS error decomposition (the prompt's test)

`M7_eps_error_decomposition.csv`, h=0 at each guide date, 19 prints 4Q21-2Q26. On the **last 8 prints (3Q24-2Q26)**:

| measure | MAE ($/share) | bias |
|---|---|---|
| EPS with a PIT EBITDA input (`ebitda_pit`) | **0.123** | +0.053 |
| EPS with the actual EBITDA in (`ebitda_known`) — pure below-the-line error | **0.073** | +0.011 |
| pre-guide **Street** EPS mean | **0.114** | +0.021 |
| attributable to the EBITDA input | 0.077 | +0.042 |
| attributable to the below-the-line lines | 0.073 | +0.011 |

So on recent prints the EPS error splits roughly **50/50** between the EBITDA input and the bridge, and the whole thing is
about the size of the Street's own miss. Inside the $0.073 of below-the-line error, the attribution is:

| line | mean abs contribution to the EPS error ($/share) |
|---|---|
| **tax** | **0.076** |
| SBC | 0.026 |
| interest income | 0.009 |
| share count | 0.004 |

**Tax is the entire below-the-line risk.** SBC is second and three times smaller; interest income and the share count are
rounding. Over the full 19 prints the picture is dominated by two events no rule could have caught: 4Q21 (EPS error -$18.59,
the post-IPO SBC cliff — the model was still fitting 2020 SBC levels) and 3Q23 (-$4.44, the valuation-allowance release, which
alone contributes -$4.34 of the tax attribution). Over the last 12 prints the MAEs are $0.568 (`ebitda_pit`), $0.526
(`ebitda_known`) and $0.584 (Street) — all three inflated by that single 3Q23 quarter.

## LIVE waterfall — vintage 2026-09-11, adj EBITDA from M1 `driver-lines/margin_v2` spec `a_unit_rw`

Revenue / GBV path: `data/processed/margin_build/06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv` (3Q26 / 4Q26 = bridge v3;
1Q27-4Q27 = WS06 v2), FY28 from `06_revenue_path_wide.csv` base. 1H26 is actual; FY26 = 1H26 actual + 2H26 forecast.
All figures $M except per-share and per-cent. Source file: `M7_live_waterfall_quarterly.csv`.

### Quarterly

| line | 3Q26 | 4Q26 | 1Q27 | 2Q27 | 3Q27 | 4Q27 |
|---|---|---|---|---|---|---|
| Revenue | 4,804 | 3,178 | 3,053 | 4,029 | 5,281 | 3,466 |
| **Adj. EBITDA** | **2,486** | **908** | 597 | 1,384 | 2,676 | 905 |
| adj EBITDA margin % | 51.8 | 28.6 | 19.6 | 34.4 | 50.7 | 26.1 |
| less D&A | 20.6 | 20.6 | 20.6 | 20.6 | 20.6 | 20.6 |
| less SBC | 452 | 465 | 464 | 551 | 511 | 526 |
| **GAAP operating income** | **2,014** | **422** | 112 | 813 | 2,144 | 358 |
| op margin % | 41.9 | 13.3 | 3.7 | 20.2 | 40.6 | 10.3 |
| + interest income | 184 | 170 | 185 | 208 | 196 | 176 |
| - interest expense | 37 | 37 | 37 | 37 | 37 | 37 |
| + other income | 4 | 4 | 4 | 4 | 4 | 4 |
| **Pre-tax income** | **2,165** | **558** | 264 | 988 | 2,307 | 501 |
| ETR % | 18.0 | 18.0 | 17.5 | 17.5 | 17.5 | 17.5 |
| tax provision | 390 | 101 | 46 | 173 | 404 | 88 |
| **Net income** | **1,775** | **458** | 218 | 815 | 1,903 | 413 |
| diluted shares (m) | 591.7 | 586.4 | 581.0 | 575.7 | 570.4 | 565.1 |
| **EPS, diluted (GAAP = Street basis)** | **3.00** | **0.78** | **0.38** | **1.42** | **3.34** | **0.73** |
| CFO (main `swing_x_gbv`) | 1,088 | 879 | 1,827 | 1,513 | 1,169 | 889 |
| capex | 8.9 | 8.9 | 8.9 | 8.9 | 8.9 | 8.9 |
| **FCF (main)** | **1,079** | **870** | 1,818 | 1,504 | 1,160 | 880 |
| **FCF (`seasonal_other`, the better-scoring spec)** | **1,465** | **706** | 1,990 | 1,320 | 1,545 | 716 |
| FCF margin % (seasonal_other) | 30.5 | 22.2 | 65.2 | 32.8 | 29.3 | 20.6 |
| *LSEG consensus, row 2026-09-11* | | | | | | |
| Street adj EBITDA | 2,362 | 914 | - | - | - | - |
| Street EPS | 2.85 | 0.86 | - | - | - | - |
| Street net income | 1,703 | 506 | - | - | - | - |
| Street EBIT | 1,909 | 454 | - | - | - | - |
| Street FCF | 1,736 | 724 | - | - | - | - |
| Street capex | 14.1 | 13.1 | - | - | - | - |

Registered LIVE quantiles (main rw specs, vintage 2026-09-11): 3Q26 EPS q10-q90 **2.73-3.09**, 4Q26 **0.53-1.12**, 1Q27
0.21-0.95; 3Q26 interest income **161-206**, 4Q26 144-196; 3Q26 SBC 433-483; 3Q26 diluted shares 579.7-599.0; 3Q26 FCF
995-1,812. (Those registry rows run on the harness's own PIT EBITDA baseline, so the EPS point there is $2.91, not the $3.00
of the M1-based waterfall above; the interval width is what to take from them.)

### The two comparison EBITDA sources (the same bridge, a different EBITDA in)

| source | 3Q26 EBITDA | 3Q26 op income | 3Q26 net income | **3Q26 EPS** | 4Q26 EBITDA | **4Q26 EPS** |
|---|---|---|---|---|---|---|
| M1 `driver-lines` (the model's base) | 2,486 | 2,014 | 1,775 | **3.00** | 908 | **0.78** |
| harness `guide_implied` (FY26 floor 35.5%) | 2,377 | 1,905 | 1,686 | **2.85** | 933 | **0.82** |
| LSEG Street EBITDA | 2,362 | 1,889 | 1,673 | **2.83** | 914 | **0.79** |
| *LSEG Street EPS itself* | | | | *2.85* | | *0.86* |

The third row is the validation in point 2 of the bottom line: **the Street's own EBITDA, run through M7, lands 2c from the
Street's own EPS for 3Q26** (7c for 4Q26, where the Street's implied share count and ETR look slightly kinder than ours).
Equivalently: the Street's $2.85 EPS is arithmetically the same as adj. EBITDA of about $2,377M on this bridge.

### Annual

| line | FY2026 | FY2027 | FY2028 |
|---|---|---|---|
| Revenue | 14,268 | 15,829 | 17,137 |
| **Adj. EBITDA** | **5,174** | **5,562** | **6,022** |
| adj EBITDA margin % | 36.26 | 35.14 | 35.14 |
| D&A | 80 | 83 | 83 |
| SBC | 1,814 | 2,053 | 2,323 |
| SBC % of revenue | 12.7 | 13.0 | 13.6 |
| **GAAP operating income** | **3,280** | **3,427** | **3,616** |
| op margin % | 23.0 | 21.7 | 21.1 |
| interest income | 692 | 765 | 795 |
| interest expense | 132 | 148 | 148 |
| other income | 61 | 15 | 15 |
| **Pre-tax income** | **3,901** | **4,059** | **4,278** |
| ETR % | 17.7 | 17.5 | 17.5 |
| tax provision | 692 | 710 | 749 |
| **Net income** | **3,209** | **3,349** | **3,529** |
| diluted shares (m, average) | 595.8 | 573.0 | 551.7 |
| **EPS, diluted** | **5.39** | **5.84** | **6.40** |
| CFO | 4,946 | 5,397 | 5,837 |
| capex | 39 | 36 | 36 |
| **FCF (main)** | **4,907** | **5,362** | **5,801** |
| **FCF (`seasonal_other`)** | **5,128** | **5,571** | **6,011** |
| FCF margin % (main) | 34.4 | 33.9 | 33.9 |
| *LSEG adj EBITDA* | *5,054* | *5,766* | *6,603* |
| *LSEG EPS* | *5.31* | *6.23* | *7.52* |
| *LSEG net income* | *3,186* | *3,673* | *4,364* |
| *LSEG FCF* | *4,918* | *5,353* | *5,771* |
| *LSEG EBIT* | *3,235* | *3,804* | *4,510* |

FY2026 is 1H26 actual (revenue $6,286M, adj EBITDA $1,780M, net income $976M, FCF $2,957M) plus the 2H26 forecast above;
FY2028 carries a flat FY27 margin by construction and is labelled as such.

**Where we differ from the Street, decomposed.** FY27: our EPS is $0.39 below the Street. Essentially all of it is the adj
EBITDA gap ($5,562M vs $5,766M = -$204M; after D&A, SBC and an 17.5% tax that is about -$0.35), plus roughly -$0.09 from our
higher SBC assumption, offset by **+$0.05** from a lower share count (573.0m against the ~589m implied by the Street's own
NI / EPS pair). Tax contributes $0.00-0.02. FY28: our EPS is $1.12 below and the EBITDA gap ($6,022M vs $6,603M) accounts for
all of it. **The below-the-line bridge is not where this model disagrees with the Street.** The disagreement is M1's flat 35.1%
margin against a Street that underwrites 36.4% then 37.7%.

Note also that our FY26 operating income ($3,280M) sits $45M **above** the Street's EBIT ($3,235M) on an EBITDA that is $120M
above: the Street carries less SBC + D&A than we do (their implied SBC + D&A ~$1,819M against our $1,894M), so we are the more
conservative of the two on stock comp. FY26 FCF lands within $11M of the Street on the main spec.

### Scenarios and sensitivities (all on the M1 base; `M7_live_waterfall_quarterly.csv`, `M7_below_ebitda_annual_forecasts.csv`)

| scenario | what moves | 3Q26 EPS | 4Q26 EPS | FY26 EPS | FY27 EPS | FY27 FCF |
|---|---|---|---|---|---|---|
| base | - | 3.00 | 0.78 | 5.39 | 5.84 | 5,362 |
| rates +100bp | interest income +$49M/q (3Q26 $232M) | 3.07 | 0.84 | 5.51 | **6.13** | 5,525 |
| rates -100bp | interest income -$49M/q (3Q26 $135M) | 2.93 | 0.72 | 5.26 | **5.56** | 5,198 |
| ETR 16% | tax only | 3.07 | 0.80 | 5.48 | 5.95 | 5,423 |
| ETR 19% | tax only | 2.96 | 0.77 | 5.34 | 5.74 | 5,301 |
| no buyback renewal (from 2Q27) | shares stop falling; FY27 average 594.2m vs 573.0m | 3.00 | 0.78 | 5.39 | **5.64** | 5,362 |
| bear revenue path | interest income + working capital only (EBITDA fixed) | 3.00 | 0.78 | 5.38 | 5.81 | 5,365 |
| bull revenue path | same | 3.00 | 0.78 | 5.39 | 5.87 | 5,335 |

Ranked by FY27 EPS impact: **rates (+/-$0.29) > buyback renewal (-$0.20) > the ETR band (+/-$0.11) > the revenue scenario
(+/-$0.03, because EBITDA does not flex)**. The buyback line is a real 2027 decision: the $3.4bn authorisation outstanding at
30 Jun 2026 is exhausted around 1Q27 at the current ~$1.03bn/quarter pace, and the base case assumes renewal (August 2022,
February 2024 and August 2025 were all renewed before exhaustion).

## For the model — parameter sheet

Every row is also in `data/processed/margin_build/M7_below_ebitda/M7_parameter_sheet.csv` (26 rows) for WS23 to copy.

| name | value | unit | source |
|---|---|---|---|
| `interest_income_beta` | **0.876** | ratio of realised yield to the 3m T-bill | rw mean of the last 8 quarters with DTB3 >= 0.5%; WS04's equal-weighted figure is 0.86 |
| `interest_income_rule` | `beta x DTB3 x (cash + STI + funds held)_avg / 4` | $M/quarter | WS04 `04_interest_income_yield_diagnostic.csv` |
| `tbill_3m_spot` (10 Sep 2026) | **3.86** | % (held flat forward) | FRED `DTB3` |
| `tbill_3m_3q26_hat` | 3.76 | % quarter average (realised to 10 Sep + spot) | FRED `DTB3` |
| `ust_1y_spot` | 4.28 | % (12m path proxy, sensitivity only) | FRED `DGS1` |
| `cash_plus_sti_2q26` | 12,069 | $M, held flat | WS02 panel 2Q26 |
| `funds_held_2q26` | 12,224 | $M; grown forward at GBV y/y | WS02 panel; WS06 path |
| `interest_income_rate_sensitivity` | **+/-100bp = +/-$49M/quarter** (~$55M as the base grows) | $M | rule arithmetic on a ~$22-23bn base |
| `sbc_yoy_growth` | **13.18** | % applied to SBC[q-4] | rw mean of 1Q26 +14.5, 2Q26 +14.9, 4Q25 +11.7, 3Q25 +10.2 (WS02) |
| `sbc_by_line_shares_ttm` | ops 6.4 / product dev 62.6 / S&M 13.9 / G&A 17.0 | % of total SBC | WS02, trailing 4 quarters |
| `da_musd_q` | **20.6** (variant 17.0) | $M/quarter | WS02; FY2025 D&A $91M, capex $33M (10-K) |
| `interest_expense_musd_q` | **37.0** | $M/quarter, 3Q26-4Q28 | 2Q26 10-Q; $2.5bn notes at 4.40 / 4.65 / 5.25% = $119M/yr coupon + issuance-cost amortisation + swap carry; $1.7bn swapped to SOFR, +/-100bp = +/-$17M/yr |
| `other_income_musd_q` | 3.7 | $M/quarter | rw mean of the last 8 (WS02 `other_income_expense`) |
| `other_addbacks_expected` | 0.0 | $M | expected value; FY2025 realised $83M, all in 4Q25 |
| `etr_fy26` | **18.0** (1H26 printed 17.1) | % | WS05 S157 "high teens" (1Q26 letter, 7 May 2026) |
| `etr_fy27_fy28` | **17.5** (range 16-19) | % | WS05 S148 long-term mid-to-high teens (OBBBA), 4Q25 letter |
| `buyback_musd_q` | **1,027.75** | $M/quarter (trailing-4 mean of 877 / 1,095 / 1,088 / 1,051) | WS02; $3.4bn authorisation left at 30 Jun 2026, exhausted ~1Q27 at this pace |
| `share_price_used` | 181.94 | USD (last close <= the vintage, 4 Sep 2026) | `data/processed/abnb_daily_close.csv` |
| `award_issuance_m_q` | 0.325 | m shares/quarter, net RSU / option issuance | implied by the diluted count and the buyback |
| `diluted_shares_delta_m_q` | **-5.32** | m/quarter = -buyback/price + issuance | this note |
| `diluted_shares_2q26` | 597.0 | m weighted-average diluted | 2Q26 10-Q (basic 592; A+B outstanding 589.6m at 15 Jul 2026; 9.2m Class H excluded) |
| `wc_rule` | swing = same quarter last year x (1 + GBV y/y) | $M | this note; 0 fitted parameters |
| `other_cf_musd_q` | 21.0 (seasonal variant: 3Q +406, 4Q -143, 1Q +194, 2Q -163) | $M/quarter | rw mean of the last 8 residuals (WS02 cash-flow lines) |
| `capex_musd_q` | **8.9** (the Street carries 14.1) | $M/quarter | rw mean of the last 4 (WS02) |
| `adj_ebitda_source_live` | `driver-lines/margin_v2` spec `a_unit_rw`, vintage 2026-09-11 | $M by quarter | the margin registry |
| `fy28_ebitda_rule` | FY27 margin (on the base revenue path) x FY28 base revenue; flat margin, labelled | | this note |
| `revenue_gbv_path` | `06_revenue_path_3q26_4q27_v2b.csv` for 3Q26-4Q27, `06_revenue_path_wide.csv` for 1Q28+ | | WS06 |

Total free parameters across the seven objects: **18** on the main specs (2+2+2+2+2+6+3), of which 7 are residual sds. The whole
bridge from adj EBITDA to EPS is six numbers: D&A, an SBC growth rate, a rate beta, an interest-expense constant, an ETR and a
quarterly share delta.

## For the 5 Nov card

* **The EPS line management will be judged against is $2.85** (LSEG mean, n 34, sd $0.15). Our bridge says that number is
  arithmetically consistent with adj. EBITDA of about **$2,377M** — $15M above the Street's own EBITDA mean. If EBITDA prints
  at M1's $2,486M and nothing else surprises, EPS prints **$3.00**, a 5% beat. **Each $100M of EBITDA surprise is +$0.14 of
  EPS** at an 18% tax rate and 592m shares; each 1pp of ETR is $0.04.
* **Interest income is the one below-the-line number worth pre-committing to: $184M for 3Q26** (q10-q90 $161-206M), against
  $180M in 3Q25. It is up y/y despite the T-bill falling from 4.10% to 3.76%, because funds held plus cash grew ~13%. A print
  below ~$165M means the balance assumption, not the rate, was wrong.
* **Watch the tax rate, not the tax dollars.** 1H26 printed a 17.1% ETR against the "high teens" sentence; the model carries
  18.0% for 3Q26. Tax is the only below-the-line line with a track record of $0.05+ single-quarter misses (mean absolute
  contribution $0.076/share over the last 8 prints).
* **Expect roughly $452M of SBC (about 12.9% of guided revenue at the guide mid) and $17-21M of D&A.** SBC has grown 10-15%
  y/y for six quarters; a print above ~$480M would be a genuine step-up and would cost $0.05 of EPS under an unchanged EBITDA.
* **Diluted share count ~591-592m**, down ~5.3m/quarter. The $3.4bn authorisation at 30 Jun 2026 supports roughly three more
  quarters at the current pace; a new authorisation announced on 5 Nov is the cheapest FY27 EPS upgrade on the table (+$0.20).
* **FCF: $1.08-1.47bn for 3Q26 against a Street $1.74bn.** We are below the Street on both specs, and the gap is the CFO
  "other" line, which we do not forecast well. Do not make a FCF call at a quarterly horizon on this model; the FY26 number
  ($4.91-5.13bn vs Street $4.92bn) is defensible, the quarterly one is not.
* **Do not quote:** the bear / bull FY28 EBITDA rows (they carry the base EBITDA by construction), the quarterly tax
  quantiles (under-covered), or any FCF "edge over the seasonal naive" — that test failed.

## Corrections to existing work

* **Within this package (fixed this session).** The FY28 EBITDA rule divided M1's FY27 EBITDA dollars by the *scenario's* FY27
  revenue, inverting the bear / bull FY28 ordering. `run.py` now uses the base revenue path as the margin denominator.
  Everything else in the overnight outputs reproduced byte-identically before the patch.
* **WS04's 3Q26 interest-income figure (~$170-175M)** is $9-14M below M7's $184M. Both are right on their own inputs: WS04 uses
  beta 0.86 and a $21-22bn balance held flat at 2Q26; M7 uses beta 0.876 (recency-weighted) and grows funds held at the adopted
  GBV y/y, which lifts the base to ~$23bn in 3Q26. Prefer the M7 number in the model and cite the difference.
* No file outside `docs/margin-build/`, `analysis/src/margin_build/`, `data/{processed,raw,manifests}/margin_build/` and
  `analysis/figures/margin_build/` was written. No git command was run.

## Files written

| path | what |
|---|---|
| `analysis/src/margin_build/M7_below_ebitda/run.py` | the package; rebuilds everything, exit 0 (FY28 denominator patched this session) |
| `analysis/src/margin_build/M7_below_ebitda/figures.py`, `README.md` | figures; the run command |
| `data/processed/margin_build/M7_below_ebitda/M7_live_waterfall_quarterly.csv` | 84 rows: 3Q26-4Q28 x 3 EBITDA sources x 8 scenarios, 51 columns, with the LSEG comparison columns |
| `…/M7_below_ebitda_annual_forecasts.csv` | FY26 / FY27 / FY28 x source x scenario (26 rows) |
| `…/M7_parameter_sheet.csv` | the 26-row "For the model" sheet |
| `…/M7_forecast_grid_all_vintages.csv`, `…/M7_errors_all_vintages.csv` | the working PIT grid and the residual pools |
| `…/M7_registry_preview.csv`, `…/M7_scoreboard_rows.csv` | the 9,648 registered rows with actuals; the method's 768 scoreboard rows |
| `…/M7_eps_error_decomposition.csv` | 19 prints: EPS error split EBITDA vs below-the-line vs Street |
| `…/M7_fy_fcf_test.csv` | the FY FCF test, 5 February vintages |
| `…/M7_interest_income_fit_history.csv`, `…/M7_cfo_other_residual_history.csv` | diagnostics |
| `…/M7_build_log.txt` | the run log |
| `data/processed/margin_build/registry/below-ebitda__{da,eps,fcf,interest_income,sbc,share_count,tax}.csv` | the seven registry files |
| `analysis/figures/margin_build/M7_below_ebitda_{interest_income,fcf_backtest,eps_bridge_3q26}.png` | three figures |
| `data/manifests/margin_build/M7_below_ebitda.csv` | the FRED pull manifest (URL, timestamp, sha256) |

## Discussion response (WS22, group C, 14 Sep 2026)

Reproduced with a NEW script that reads only the scoreboard `run.py` already produced — no registry row,
no processed CSV and no number above changed, so **M7 was not re-run** (and could not be: `run.py` ends by
calling `score.py`, which the discussion round is forbidden to touch):

```
py -3.13 analysis/src/margin_build/M7_below_ebitda/discussion_checks.py    # exit 0, ~30 s
```
-> `M7_discussion_coverage_band.csv`, `M7_discussion_eps_decomp.csv`, `M7_discussion_summary.json`.

| finding | decision | reproduced | before -> after |
|---|---|---|---|
| R10 "tax quantiles under-cover" | **ACCEPT — the claim is withdrawn** | yes, and the note contradicted itself | The "Coverage" paragraph above says `tax_rate_pct` (0.86 W1 / 0.90 W2) and `tax_provision_musd` (0.71 / 0.70) are **under**-covered. Against the **exact binomial 5-95 band** attainable at that n — [0.643, 0.929] at n 14, [0.60, 1.00] at n 10 — 0.86/0.90 are *above* nominal 0.80 and 0.71/0.70 are *inside* the band. Over all 384 M7 cov80 cells, mean coverage **0.941**, **42 above** their band and **2 below** (both `capex_musd` W1 h=1 at 0.538 vs a 0.615 floor; capex is $5-17M a quarter and I would not defend either direction). **Before:** "the quarterly tax quantiles are under-covered, do not quote them as a real 80% interval." **After:** M7's intervals are systematically **too wide**, the tax line included; the reason not to quote them is over-dispersion, not under-coverage. Any 5 Nov band should come from the realised h=0 error distribution, not from the Gaussian-on-last-12 pool. The kill-list entry 7 stands as written. |
| R16 EPS error is the EBITDA input, not the bridge | **ACCEPT with a number** | yes, and it splits by window | At h=0, the share of the `ebitda_pit` EPS MAE contributed by the EBITDA input is **64% in W2** (corr(err, contribution) 0.92; MAE $0.125 vs $0.066 with the actual EBITDA in) but only **17% in W1** (corr 0.23), because W1 carries the 2023 valuation-allowance and lodging-tax quarters where the bridge itself is the error. Quoting rule adopted: **below-the-line accuracy is quoted from `ebitda_known` (W2 h=0 EPS MAE $0.066), total EPS error only from `ebitda_pit` ($0.125)**, never mixed, and the W1 numbers are quoted with the two break quarters named. |
| R13 FRED inputs have no re-pull fallback | **ACCEPT-DEFER** | yes — `load_daily` (run.py:109) reads `data/raw/margin_build/M7_below_ebitda/fred_<series>.csv` and raises `FileNotFoundError` on a clean clone | Not fixed tonight because the only honest way to land it is to re-run `run.py`, which re-runs `score.py`. The patch for the morning, 6 lines in `load_daily`: `p = RAW / f"fred_{series}.csv"; if not p.exists(): RAW.mkdir(parents=True, exist_ok=True); urlretrieve(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}", p)` (keyless, the same call WS04 already uses), then append the file to `data/manifests/margin_build/M7_below_ebitda.csv`. Meanwhile the three files are manifested and the README says to re-pull by hand; the package is reproducible on this machine and nowhere else. |
| R14 line-level wins are close to free | **ACCEPT, not binding on M7** | yes | M7 makes no `adj_ebitda_margin_pct` claim; its lines are below-EBITDA lines with their own hardest baselines (`seasonal_naive_drift` / `trailing4`), which the note already quotes alongside `seasonal_naive`. The one M7 result quoted against `seasonal_naive` alone that should not be is the *pass* of test 4 for `sbc`/`da`/`share_count`: against the drift baseline SBC is 0.93/0.96, D&A 0.81/1.00, shares 0.40/0.67 — so of that block only share count and (weakly) D&A are genuine. |
| R17 h=0 is post-letter | **ACCEPT** | yes | Said on the card: the backtested h=0 rows forecast the quarter whose letter is already out; the 4Q26 EPS/FCF position on 5 Nov is an h=1-type problem, where M7's own MAEs are 15-25% worse. |
| quarterly FCF fails (M7's own result) | unchanged | — | reaffirmed: `fcf_musd` h=0 ratio 1.018 W1 / 0.927 W2 equal-weighted, 1.090 / 1.054 recency; the object is carried for the FY bridge only. |

**WS20's two questions (answered in full in `docs/margin-build/discussion/group_C.md` §4).** (10) The quarterly
FCF rows — `fcf_musd`, `cfo_musd`, `fcf_margin_pct` — are **withdrawn from the quotable set**; the annual FY
result (3 of 4 years, +$399M mean high bias) is the only FCF claim the memo should make. (11) Swapping WS23's
recommended margin blend (50.39%) in for M1 as the EBITDA input: the waterfall is linear, slope
**d(EPS)/d(EBITDA) = (1 − ETR)/shares = $0.001386 per $M = $0.0666 per 1pp of 3Q26 margin**, so 3Q26 EPS goes
**$3.000 -> $2.909** (Street $2.845, and on the Street's own EBITDA this bridge gives $2.827). The interval does
**not** widen if it is propagated properly: bridge sd $0.083 (realised W2 h=0 with EBITDA known) combined with
$0.062 from the blend's margin error gives sd $0.103 and an 80% band of **$2.78-3.04**, inside the registered
$2.73-3.09. `M7_discussion_blend_eps.csv`.

**What M7 now claims.** An auditable bridge, not an edge. Six of seven objects beat seasonal naive at h=0 in both
windows, but the ones that matter are interest income (MAE $17.9M W1 / $10.5M W2, 0.81x / 0.68x the *hardest*
baseline, one fitted parameter) and share count (0.40x / 0.67x the drift). EPS accuracy is quoted two ways and
never mixed: with the actual EBITDA in, W2 h=0 MAE **$0.066**; with a PIT EBITDA baseline in, **$0.125**, of which
64% is the EBITDA input. Against the Street the bridge is 0.94x in W1 and 1.04x in W2 — i.e. no alpha. Quarterly
FCF fails; FY FCF passes 3 of 4 years and is biased +$399M high. All intervals, tax included, are too wide.

## RESUME

M7 is complete and reproducible: `py -3.13 analysis/src/margin_build/M7_below_ebitda/run.py` exits 0 and rewrites every output
byte-identically, the 9,648 registered rows validate through the margin harness, and `score.py` reports 768 `below-ebitda` rows.
The next agent should do three things. **First**, decide which EBITDA the waterfall carries: it currently runs on M1's
`driver-lines` base, and every material difference from the Street (FY27 EPS -$0.39, FY28 -$1.12) traces to M1's flat 35.1%
FY27-28 margin, not to anything below the line — if the synthesis picks a different EBITDA path (M2's sentence rule, M6's
cycle-flex, or a blend), re-register that method and re-run `run.py`; the whole waterfall follows automatically, because
`live_ebitda_sources()` reads the registry and prefers `driver-lines`, then `margin-ts`, then the harness baseline.
**Second**, decide whether to swap the LIVE waterfall onto the post-hoc winning specs (`yoy_last` for SBC, `last_value` for D&A,
`swing_x_gbv_seasonal_other` for FCF — worth about $0.01 of 3Q26 EPS and $385M of 3Q26 FCF); the registry already carries every
spec and the scorer keys on `spec_id`, so this is a labelling decision, not a re-fit. **Third**, do not spend more time trying to
beat the seasonal naive on quarterly FCF — three specs and two weightings all failed, and the diagnosis (the CFO "other"
residual, +$599M to -$352M with no structure) is in `M7_cfo_other_residual_history.csv`; the only untested idea is modelling
funds payable directly off the WS06 GBV-by-month path rather than off quarterly GBV. For the memo, the three numbers to carry
forward are **3Q26 EPS $3.00 (Street $2.85), FY26 EPS $5.39 (Street $5.31), and interest income $184M in 3Q26 with a
+/-$49M per 100bp rate sensitivity**; and the one sentence to carry is that the Street's own EBITDA run through this bridge
reproduces the Street's own EPS to two cents, so the 5 Nov EPS argument is an EBITDA argument.

**RESUME addendum (WS22, 14 Sep).** Tax under-coverage is withdrawn (the intervals are too wide, not too narrow); quarterly FCF is withdrawn from the quotable set; EPS is quoted from `ebitda_known` for the bridge and `ebitda_pit` for the total, never mixed. Two jobs left, both needing a run that may not race the scorer: the FRED fetch-if-missing patch in `load_daily` (R13, 6 lines, written out above) and rebuilding the LIVE waterfall on WS23's blend EBITDA rather than M1's (3Q26 EPS $2.909, computed analytically in `M7_discussion_blend_eps.csv`).
