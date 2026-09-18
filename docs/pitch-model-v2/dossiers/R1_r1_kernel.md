# R1 — Kernel: λ by season and the lag weights

## 1. Header
- Line: R1 · Judge's question: "Why should revenue be two-thirds last quarter's bookings plus one-third the quarter before?"
- Digger: opus · Date: 2026-09-18 · Commit: e39d9e4

> Brief names commit `f1ce2cd`; the working tree at run time was `e39d9e4` on `theo/pitch-model-v2`.
> All three receipts carry `e39d9e4`. Every number below was produced or re-read at that commit.

**One-paragraph answer.** Because Airbnb books GBV when the reservation is made and recognises the
fee when the guest checks in, a quarter's revenue is a weighted sum of *earlier* quarters' GBV. The
⅔/⅓ split is not a measured cohort share — it is a **forecasting weight**, and it is the one part
of this line that survives both windows: on a strict point-in-time sweep of the carried weight the
RMSE-minimising value is **0.65–0.75 on W1 and W2 and in all three training windows**
(`kernel_phi_v2/D3`), so ⅔ sits inside the optimum on both windows. Everything else about the
weight is weaker than the memo's phrasing: the in-sample lag polynomial does **not** recover ⅔/⅓
(it puts 0.23–0.41 on the *current* quarter and the pre-registered φ₀ = 0 test failed), the LOO
argmin moves from 0.13 to 0.76 depending on the estimation window, and the block-bootstrap 95%
interval on that argmin spans roughly [0.00, 0.90]. The saving grace is that the weight barely
matters: re-estimating λ at each w absorbs almost all of the change, so the entire w ∈ [0.20, 0.80]
band moves the 4Q26 print by **$13M (0.42%)** and the ⅔-vs-0.38 fight is worth **$6M (0.20%)**.

## 2. The number

All rows are scenario **base**. λ and the weights do not vary by scenario. λ is the seasonal
conversion in `Revenue_q = λ_s × [w₁·GBV_{q−1} + w₂·GBV_{q−2}]`, w₁ = ⅔, w₂ = ⅓.

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base | λ_Q1 (season, 3-cell mean 1Q24–1Q26) | 12.66 | 12.33 | 13.03 | pct | prints to 2Q26 (2026-08-06); pkg 2026-09-11 |
| base | λ_Q2 (season, 3-cell mean 2Q24–2Q26) | 13.71 | 13.45 | 13.95 | pct | prints to 2Q26 (2026-08-06); pkg 2026-09-11 |
| base | λ_Q3 (season, 3-cell mean 3Q23–3Q25) | 17.24 | 17.15 | 17.39 | pct | prints to 2Q26 (2026-08-06); pkg 2026-09-11 |
| base | λ_Q4 (season, 3-cell mean 4Q23–4Q25) | 12.03 | 11.95 | 12.12 | pct | prints to 2Q26 (2026-08-06); pkg 2026-09-11 |
| base | λ_Q1 — 4-cell variant (2023Q1+, n=14, package default) | 12.69 | 12.33 | 13.03 | pct | same |
| base | λ_Q2 — 4-cell variant (2023Q1+, n=14, package default) | 13.71 | 13.45 | 13.95 | pct | same |
| base | **w₁ — fixed rule, GBV[q−1]** | **66.67** | 65.0 | 75.0 | pct | PIT sweep `D3`, both windows, 3 training windows |
| base | **w₂ — fixed rule, GBV[q−2]** | **33.33** | 25.0 | 35.0 | pct | complement of w₁ |
| base | w₁ — identification interval (LOO argmin, block bootstrap, 400 draws) | 66.67 | 0.0 | 90.0 | pct | `03_weight_summary.csv` |
| base | **joint rule w₀ — GBV[t] (same quarter)** | **35.90** | — | — | pct | GD audit origin 2026-09-15, n_train 20 |
| base | **joint rule w₁ — GBV[t−1]** | **47.29** | — | — | pct | GD audit origin 2026-09-15, n_train 20 |
| base | **joint rule w₂ — GBV[t−2]** | **16.81** | — | — | pct | GD audit origin 2026-09-15, n_train 20 |
| base | **joint rule w₃ — mean(GBV[t−3], GBV[t−4])** | **0.00** | — | — | pct | GD audit origin 2026-09-15, n_train 20 |
| base | joint rule λ_Q1 / λ_Q2 / λ_Q3 / λ_Q4 (not comparable to the fixed λ) | 11.20 / 13.29 / 17.65 / 12.68 | — | — | pct | GD audit origin 2026-09-15 |
| base | λ_Q3 control — centre (3Q26 identity at base $27,866.7M) | 17.239 | — | — | pct → $4,804M | 5 Nov 2026 print |
| base | λ_Q3 control — **warning** threshold, 1σ on Q3's own sd (n=3) | 17.086 | — | — | pct → $4,761M | 5 Nov 2026 print |
| base | λ_Q3 control — **escalate** threshold, 2σ on Q3's own sd (n=3) | 16.934 | — | — | pct → $4,719M | 5 Nov 2026 print |
| base | λ_Q3 control — 1σ on pooled σ (all seasons, wide chart) | 16.888 | — | — | pct → $4,706M | 5 Nov 2026 print |
| base | λ_Q3 control — 2σ on pooled σ (all seasons, wide chart) | 16.536 | — | — | pct → $4,608M | 5 Nov 2026 print |

Notes that must travel with the table:

- **The joint weights are a different rule, not a re-estimate of the same one.** Joint is
  `R[t] = λ_s × (w₀G[t] + w₁G[t−1] + w₂G[t−2] + w₃·mean(G[t−3],G[t−4]))` — 4 seasonal multipliers
  plus 3 free normalised weights = **7** conversion parameters, against **4** for fixed. Its λ
  values differ from the fixed λ because its base includes same-quarter GBV; **never mix a joint λ
  with a fixed base or vice versa.**
- **The joint weights are not stable.** Across the audit's own fitted origins w₀ runs 0.359→0.605
  and w₁ runs 0.334→0.525 (`horizon_v1/results_v2/origin_fits.csv`); the 35.90/47.29/16.81/0.00
  quoted above is the 2026-09-15 origin only.
- **λ within-season ranges** (the "stability" claim): Q4 **0.171pp**, Q3 0.245pp, Q2 0.497pp,
  Q1 0.709pp. Only Q4 is as tight as the state-of-play line implies.
- **The control thresholds are a composite chart.** A λ_Q3 miss cannot separate RNPL cancellation
  of carried bookings from weak in-quarter (φ₀) booking; the tight chart rests on n = 3 cells and
  the pooled chart is 2.3× wider, so a print between $4,608M and $4,761M is a signal on one chart
  and noise on the other. Quote both.

## 3. Derivation chain

1. Printed 10-Q / 10-K revenue and GBV, 2020Q3–2026Q2 (24 quarters). Filing basis: *"The entire
   amount of a booking is reflected in GBV in the quarter it occurs regardless of when payment is
   collected. Revenue is recognized upon check-in; accordingly, GBV has generally been a leading
   indicator of revenue."* — 2Q26 Form 10-Q, captured verbatim at
   `docs/pitch-forecasts/questions/rnpl-gbv-share-disclosed/sources/10q_2Q26_rnpl_passages.txt` →
2. `data/processed/overnight/02_kpi_panel_quarterly.csv` — columns `quarter, revenue_musd,
   gbv_musd, fx_pts_revenue, fx_pts_adr` (the only file `kernel.py` reads; cross-checked against
   `harness/targets.csv` on revenue and GBV over 24 quarters, stage [0] of the run log) →
3. `analysis/src/forecast_methods/kernel_lambda/kernel.py` `build_panel()` → `run.py` stages A–F
   (`KPI` constant at `run.py:32`) →
4. **λ cells**: `data/processed/forecast_methods/kernel_lambda/01_lambda_table.csv`, column
   `lam_w23`, rows `2021Q1`…`2026Q2`. **Season means**:
   `04_season_lambda_by_weight.csv`, rows `w = 0.6667`, column `lambda_pct`. **Acceptance**:
   `01_acceptance_test.csv`, column `match_2dp` (12/12 True). **Weights**: `03_weight_summary.csv`,
   columns `argmin_w_loo`, `boot_w_ci_lo/hi`. **Flatness cost**: `05_flatness_cost_4q26.csv`.
   **Live**: `08_live_3q26.csv`, `09_live_4q26_grid.csv`, `10_ledger_share.csv`.

Side chains for the other §2 rows:

- **PIT-optimal weight band**: same KPI panel → `analysis/src/forecast_methods/kernel_phi_v2/run.py`
  (stage D) → `data/processed/forecast_methods/kernel_phi_v2/D3_carried_weight_pit_sweep.csv`,
  columns `carried_w, W1_rmse_pct, W2_rmse_pct`.
- **λ_Q3 control thresholds**: same panel → `kernel_phi_v2/run.py` (stage C) →
  `C5_control_chart_5nov.csv`, columns `lambda_lower`, `revenue_lower_musd` by `sigma_basis` × `rule`.
- **Joint weights**: KPI panel + guidance ledger →
  `analysis/src/forecast_methods/gbv_decision_0915_v1/…` (Willem's 15 Sep package) →
  `data/processed/forecast_methods/gbv_decision_0915_v1/horizon_v1/results_v2/origin_fits.csv`,
  row `origin_date = 2026-09-15`, columns `weight_group_0…3`, `lambda_Q1_pct…lambda_Q4_pct`.

## 4. Governing sources

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-06-30 | 2Q26 Form 10-Q, verbatim capture at `docs/pitch-forecasts/questions/rnpl-gbv-share-disclosed/sources/10q_2Q26_rnpl_passages.txt` | GBV recorded at booking regardless of collection; revenue recognised upon check-in; GBV is a leading indicator; RNPL bookings show higher cancellation rates and may decorrelate GBV/revenue/cash | **governs** — the accounting premise that makes a lag kernel legitimate at all |
| 2026-09-11 | `05_backtests/kernel-lambda.md` + `analysis/src/forecast_methods/kernel_lambda/` | λ table, acceptance 12/12 to 2dp, weight grid, flatness cost, φ₀ ≠ 0 (KL-3 failed), live 3Q26 $4,804M / 4Q26 $3,200M | **governs** for λ, the fixed weights and the flatness cost |
| 2026-09-11 | `05_backtests/VERIFY_kernel-lambda_r1.md` (independent verifier) | PASS; byte-identical rerun; 10/10 recomputations exact; adds the finding that the decision document's 2.44% RMSE / 2.6pp predictive sd is not a reproducible walk-forward number | **governs** over the implementer's note where they differ (they do not) |
| 2026-09-11 | `05_backtests/K1_KERNEL_WEIGHTS_AND_BACKLOG.md` + `kernel_phi_v2/` | φ₁+φ₂ = 0.58–0.64 identified, the φ₁/φ₂ split is not; **PIT-optimal carried weight 0.65–0.70**; paid/booked/unbooked three-way split; the 5 Nov λ_Q3 control chart | **governs** for the control thresholds and for "⅔ forecasts even though it does not fit" |
| 2026-09-11 | `05_backtests/K2_KERNEL_FROM_LEAD_TIMES.md` + `kernel_leadtime_v2/` | Bottom-up from 268,110 Melbourne reservations: value-weighted φ₀ 0.46–0.56, ~54% of a Q3 stay quarter booked before it starts; mean lead 58 days ≈ 1.9 months, consistent with unearned fees ÷ revenue of 0.66–0.88 q | **governs** as the only booking-data evidence; **it is 2014–17 Melbourne, not current Airbnb** |
| 2026-09-12 | `05_backtests/K0_KERNEL_ENGINE_v2.md` + `kernel_engine_v2/` | Acceptance 12/12 re-passes under an independent implementation; live default `ewm`; 3Q26 $4,808.36M, 4Q26 $3,214.78M; **guide origins 14, refused 14** | **governs** the independent-implementation check and the strict-origin availability finding |
| 2026-09-15 | `05_backtests/GD_HORIZON_RESULTS_v1.md` + `GD_HORIZON_ELIGIBILITY_ADDENDUM_v1.md` + `gbv_decision_0915_v1/` | Fixed vs joint vs guide-growth at p+2/p+3/p+4; joint weights 35.90/47.29/16.81/0.00; fixed p+4 passes the gate on common-9 but reverses on its own eligible W1 history | **governs** the fixed-vs-joint comparison; **supersedes** any earlier claim that the kernel has an established edge at the next guide |
| 2026-09-15 | `05_backtests/GD_DECISION_REPORT_v2.md` | "Retain GBV conversion as a supporting forecast and scenario tool; pivot the central pitch away from an asserted precise booking-cohort/RNPL edge" | **governs** the disposition of this line; **supersedes** `GD_DECISION_REPORT_v1.md` |
| 2026-09-15 | `~/Citadel-ABNB-untracked/.../NET_GBV_REVERSE_HANDOFF_v1.md` + `_RESULTS_v2.md` | "Zero new forecasting coefficients… fixed weight 2/3"; do-not-register decision; the H1-26 collection residual (−$399.53M) mixes payment, refunds, fee/mix, recognition, FX and cohort timing | **governs** — confirms nothing in that package re-estimates the kernel weight, and forbids using its residual as a revenue haircut |
| ≤2026-09-17 | `05_backtests/RED_TEAM.md` | No multiplicity correction: kernel-lambda registered 7 revenue-level variants and the scoreboard quotes the best two; "survives both windows" is a weak filter at n = 14/10 across ~37 objects | **governs** as the standing caveat on every "survives both" claim in §6 |

**Web fetches (1 of 5 used, logged per rule 3):**

1. `https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm` —
   2Q26 Form 10-Q, asked for the revenue-recognition sentence, the GBV definition and the RNPL
   cancellation language. **Returned a truncated excerpt (financial statements only); none of the
   three passages were in the retrieved section.** No claim in this dossier rests on that fetch;
   the verbatim passage in §3 comes from the repo's own dated capture of the same filing. No
   airbnb.com page was fetched, no credentials typed.

## 5. Reproduction receipt

- Receipt: `data/processed/pitch_model_v2/receipts/R1/receipt.json`
- Command: `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id R1 --watch data/processed/forecast_methods/kernel_lambda --cmd "python3 analysis/src/forecast_methods/kernel_lambda/run.py"` · Exit: 0 · Wall: 7.1s · Interpreter: python3 (3.13 / pandas 3.0)
- Output: `data/processed/forecast_methods/kernel_lambda/04_season_lambda_by_weight.csv` cell `lambda_pct, row w=0.6667 & season=3` = 17.239361851242432 · Committed value: 17.239361851242432 · Tolerance: ±0.0005pp · **Match: yes**
- Also matched byte-for-byte in the same run: `01_lambda_table.csv` (all 22 λ cells),
  `01_acceptance_test.csv` (12/12 `match_2dp` True, max |diff| 0.0005pp against the architect
  table), `02_weight_grid.csv`, `03_weight_summary.csv`, `04_season_lambda_by_weight.csv`,
  `05_flatness_cost_4q26.csv`, `07_*`, `08_live_3q26.csv`, `09_live_4q26_grid.csv`,
  `10_ledger_share.csv`, `11_parameter_count.csv`, `12_prereg_card.csv`, `13_*` — 16 of 17 outputs
  unchanged. `restored: true`; `git status` clean on every watched path afterwards.
- **The one file that moved**: `06_lag_polynomial.csv`, max |diff| **6.67e-06** (a φ₀ bootstrap CI
  bound). That file is the *diagnostic-only* 7-parameter lag polynomial, not the published kernel;
  its φ point estimates moved by ≤3.1e-07 and its λ columns by ≤1.6e-06. Interpreter drift, not a
  numbers change; well inside the ±0.0005pp tolerance.

Two supporting receipts, same directory, same commit:

| receipt file | command | exit | wall | restored | files changed | max abs diff |
|---|---|---|---|---|---|---|
| `receipt_kernel_lambda.json` (= `receipt.json`) | `kernel_lambda/run.py` | 0 | 7.1s | true | 1 of 17 | 6.67e-06 |
| `receipt_kernel_engine_v2.json` | `kernel_engine_v2/run.py --as-of 2026-09-12` | 0 | 0.6s | true | 2 of 11 | 3.64e-12 (+ a timestamp-only JSON) |
| `receipt_kernel_phi_v2.json` | `kernel_phi_v2/run.py` | 0 | 31.0s | true | 22 of 30 | **113.3** ($M, in `A5_dollar_map_2q26_gbv.csv`) |

The third row is itself a finding and is reported as a partial reproduction, not a clean one.
`kernel_engine_v2` re-derives the acceptance table 12/12 from independent code and reprints
3Q26 $4,808.36M / 4Q26 $3,214.78M / 1Q27 $3,121.42M to the digit. `kernel_phi_v2` reproduces the
load-bearing **D3 PIT weight sweep to 1.3e-14** but its φ estimates move by up to 0.0028 and its
φ bootstrap CIs by up to 0.0149 across interpreter versions — i.e. **the identity and the
forecasting weight are machine-precision reproducible while the φ decomposition is not stable even
to three decimals.** That is exactly what K1's own identification finding predicts, and it is the
cleanest available demonstration that the cohort split must not be quoted as measured.

Rule 1 observed: no `harness/score.py` and no margin scorer was run. All W1/W2 metrics in §6 are
read out of the existing `data/processed/forecast_methods/harness/scoreboard.csv`, not regenerated.

## 6. Test record

**Pre-registered lines.** KL-1 to KL-4 in `12_prereg_card.csv` (kernel-lambda, 11 Sep) and the
frozen promotion gate in `GD_HORIZON_RESULTS_v1.md` (15 Sep): *n ≥ 8 in both windows, ≥ 10% lower
RMSE than **both** simple baselines, no year/quarter deletion reversal, and a 90% paired
year-bootstrap ratio upper bound below 1 against direct guide growth.*

**(a) Accounting identity — the λ table.** PIT n/a (it is an identity on printed data).

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| acceptance (all cells) | 12 | \|λ computed − architect\| | **0.0005pp max** | — | — | — | all 12 within 3dp rounding interval (≤0.0005pp) | **pass** |
| acceptance, independent impl. (`kernel_engine_v2`) | 12 | same, 2dp display | **12/12 True** | — | — | — | 12/12 at 2dp | **pass** |
| Q4 within-season dispersion | 3 | range of λ_Q4 | **0.171pp** | — | — | — | 0.171pp as stated | **pass** |

**(b) Revenue level at the guide date, PIT prior replay** (harness scoreboard, RMSE ratio to naive;
the pre-registered filter is "survives both windows"):

| window | n | metric | this line (w=⅔) | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W1 | 14 | RMSE ratio to naive | **0.831** | 1.000 | **0.377** | 1.073 | < 1 on both windows | pass (beats naive) |
| W2 | 10 | RMSE ratio to naive | **0.727** | 1.000 | **0.319** | 0.871 | < 1 on both windows | pass (beats naive) |
| W1 | 14 | MAE % / RMSE % / bias % | 2.313 / 3.066 / **+2.230** | 2.743 / 3.405 | 1.086 / 1.204 | 3.216 / 3.746 | — | — |
| W1 | 14 | PIT-KS p (calibration) | **0.0027** | — | — | — | not rejected at 5% | **FAIL** |
| W2 | 10 | PIT-KS p (calibration) | **0.0298** | — | — | — | not rejected at 5% | **FAIL** |
| W1 / W2 | 14 / 10 | best variant `last3_ex_covid` ratio | **0.555 / 0.472** | 1.000 | 0.377 / 0.319 | 1.073 / 0.871 | survives both | pass, but see multiplicity caveat |
| W1 / W2 | 14 / 10 | `w = 0.38` sensitivity ratio | 1.433 / 1.196 | 1.000 | 0.377 / 0.319 | 1.073 / 0.871 | survives both | **FAIL** (both windows) |
| W1 / W2 | 14 / 10 | `w = 0.33` sensitivity ratio | 1.584 / 1.311 | 1.000 | 0.377 / 0.319 | 1.073 / 0.871 | survives both | **FAIL** (both windows) |

**(c) The lag weight itself.**

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W1 (2023Q1+) | 12 | PIT RMSE-minimising carried weight, ex-COVID | **w = 0.65** (1.906%) | — | — | — | ⅔ inside the optimum | **pass** |
| W2 (2024Q1+) | 10 | same | **w = 0.65** (2.036%) | — | — | — | ⅔ inside the optimum | **pass** |
| all-history training | 12 / 10 | same | w = 0.70 / **0.75** | — | — | — | ⅔ inside the optimum | pass |
| in-sample LOO, 4 estimation windows | 22 / 18 / 14 / 12 | argmin w | **0.76 / 0.68 / 0.32 / 0.13** | — | — | — | KL-4: weight not identified better than ±0.2 | **CONFIRMED (and worse)** — boot CI ≈ [0.00, 0.90] |
| all | 3 windows | φ₀ (same-quarter GBV weight), simplex lag poly | **0.225 / 0.405 / 0.390** | — | — | — | KL-3: φ₀ not distinguishable from 0 | **FAIL** — CI excludes 0.02 in all three; free fit wins LOO in all three |
| all | 22 → 4Q26 | cost of the whole w ∈ [0.20, 0.80] band | **$13M (0.42%)**; ⅔-vs-0.38 **$6M (0.20%)** | — | — | — | — | the mitigating fact |

**(d) The forecast at the guide that matters — Willem's 15 Sep audit** (raw issued-guide-midpoint
RMSE, $M; "this line" = the fixed ⅔/⅓ rule):

| window | n | metric | this line (fixed) | joint (7p) | guide-growth | revenue-growth/cushion | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W1, next guide (p+2) | 11 | guide-mid RMSE $M | 74.59 | 64.29 | **59.06** | 118.69 | ≥10% better than both simple baselines | **FAIL** |
| W2, next guide (p+2) | 10 | guide-mid RMSE $M | 77.01 | 63.83 | **61.31** | 124.25 | ≥10% better than both simple baselines | **FAIL** |
| W1 = W2, second (p+3) | 10 | guide-mid RMSE $M | 99.32 | **94.61** | 98.95 | 124.33 | ≥10% better than both | **FAIL** |
| W1 = W2, third (p+4) | 9 | guide-mid RMSE $M | **117.74** | 131.44 | 132.46 | 149.84 | ratio 0.889, interval 0.773–0.980, no deletion reversal | **pass (common-9 sample only)** |
| W1, third (p+4), fixed's own eligible history | 12 | guide-mid RMSE $M | 159.10 | — | **144.57** | 153.30 | same gate | **FAIL** (ratio 1.101) |
| W2, third (p+4), fixed's own eligible history | 10 | guide-mid RMSE $M | **114.36** | — | 125.70 | 143.93 | same gate | **FAIL** (ratio 0.910, misses the 10% hurdle) |

**(e) Information-set availability** (`kernel_engine_v2`, strict pre-guide origins):

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W1 | 14 | guide origins where the printed-lag kernel is available *before* the letter | **0 / 14** | 14 | 14 | 14 | ≥8 per window | **FAIL** |
| W2 | 10 | same | **0 / 10** | 10 | 10 | 10 | ≥8 per window | **FAIL** |
| W1 | 6 | historical control-chart false alarms | 1 / 6 | — | — | — | descriptive | — |

**Strongest known failure:** at the only guide the pitch trades — the next one — the fixed ⅔/⅓
kernel is beaten by a one-line baseline that simply extends the last issued guide's growth rate
($74.59M vs $59.06M RMSE on W1 n = 11; $77.01M vs $61.31M on W2 n = 10), and under the
pre-registered standalone-eligibility audit neither the fixed nor the joint rule clears its
promotion gate at any of the three horizons.

Three further failures that must travel with this line, in descending severity:

1. **The PIT backtest exists only because of a harness convention.** `kernel_engine_v2` refuses
   14/14 W1 and 10/10 W2 guide origins on strict pre-letter information sets, because the
   just-printed GBV arrives *in* the same letter that carries the guide. Every PIT number in
   table (b) rests on the harness's documented "same-day letter is in the information set"
   deviation. That is legitimate for reconstructing *management's* view on guide morning; it is
   not a pre-guide alpha claim, and it must never be presented as one.
2. **The published w = ⅔ spec's predictive distribution is rejected** (PIT-KS p = 0.0027 W1 /
   0.0298 W2), driven by +2.23pp PIT bias from the 2021 λ cells. The fix is the ex-COVID
   estimation window (p = 0.63 / 0.74), and the memo must say which window it used.
3. **No multiplicity correction anywhere.** kernel-lambda registered 7 revenue-level variants and
   the scoreboard quotes the best two; across ~37 registered objects at n = 14/10, "survives both
   windows" is a weak filter (`RED_TEAM.md`). The "ex_covid" exclusion is itself an ex-post
   judgement about which quarters were outliers.

## 7. Kill list and consistency

- **Kill-list check: none of this line's numbers is on the kill list.** Specifically avoided:
  the −3.4pp Q4 FX step (this package's §(d) shows the check-in remeasurement inside λ is *not*
  distinguishable from zero at n = 12–15, slope +0.233, se 0.252, t = 0.93 — and the FX step is an
  **output** of the kernel arithmetic, never to be subtracted again); "82% of Q4 FX already
  determined"; "+4.05% fee uplift"; restated unearned fees as a pin; the 1.71M quote panel.
- **Kill-list wording observed.** This dossier does not say "nothing beats guide × cushion". It
  says: **no single object beats guide × cushion on both windows** — and the kernel does not beat
  it at all (0.555 vs 0.377 on W1, 0.472 vs 0.319 on W2, best variant).
- **A governing note quotes a withdrawn number (rule 4).**
  `05_backtests/00_IMPLEMENTATION_DECISIONS.md` (≈ lines 462 and 803) builds the 4Q26 predictive
  sd as `sqrt(2.44%² + 1.006%²) ≈ 2.6pp`. The **2.44% is not reproducible as a walk-forward PIT
  RMSE** — the strict PIT figures are 3.066% (W1) / 2.961% (W2), and 2.44 only appears as a
  full-sample-prior construction. The implementer flagged the non-reproduction; the verifier traced
  it into the decision document. **Do not quote 2.44% as walk-forward, and do not quote 2.6pp as
  the 4Q26 predictive sd without rebuilding it.** Same class of error: the "honest figures to
  match" triple 1.74 / 2.44 / +0.99 is a full-sample-prior construction, not a PIT one.
- **Conflicts with other lines.**
  - *With R2 (3Q26 revenue).* This line's 3Q26 object is $4,804M (w = ⅔, λ_Q3 17.239%, base
    $27,866.7M). `kernel_engine_v2` with its frozen `ewm` λ variant gives **$4,808.36M** — a $4M
    spread purely from the λ-averaging rule. R2 must pick one and say which. The kernel's
    registered predictive sd (51M, 1.6%) **conditions on a given GBV** and must be convolved with
    the GBV distribution before it is quoted as a 4Q26 band.
  - *With D5 / B4 (FX).* The λ-internal FX wedge is not distinguishable from zero; the revenue-FX
    effect is already inside the lagged GBV base. Any FX adjustment applied on top of a kernel
    output is a double count.
  - *With D7 (take rate).* Take rate is an output of GBV × λ arithmetic here, not an input; the
    two lines must not both be "set".
  - *With B3 (FY27).* FY27 growth spans +9.18% to +11.52% across the weight grid because w moves
    FY26 as well as FY27; the "+0.09pp edge" exists only at w = ⅔ and is −2.25pp at w = 0.33.
    FY27 remains exploratory.
  - *With the memo's first sentence.* "Management can already see essentially all of the quarter
    it is about to guide" is **weakened and must be softened to 'most'**: φ₀ = 0.23–0.41 on the
    ledger (kernel-lambda), 0.36–0.39 (K1), and 0.46–0.56 on booking data (K2). Do not write
    "100% determined".
  - *With K2's provenance.* K2's φ is measured on 268,110 **Melbourne 2014–17** reservations. It
    corroborates the *shape* (short-dated with a long thin tail; ~54% of a Q3 stay quarter booked
    before it begins) and its 58-day value-weighted mean lead agrees with Airbnb's own unearned
    fees ÷ revenue of 0.66–0.88 quarters — but it is not a current Airbnb cohort table and must
    not be labelled one.
  - *No claim of independent confirmation from the h2 bridge conversion file* — it is the same six
    ratios from the same two columns of the same panel at w = 0.667.

## 8. Open choices

1. **Fixed (⅔/⅓, 4 conversion parameters) vs joint (7 parameters) as the pitch's conversion rule.**
   Options: (a) present **fixed** and carry joint as a labelled sensitivity; (b) switch to
   **joint**; (c) present both side by side with no central rule.
   *Evidence for joint:* it beats fixed at the next guide on both windows ($64.29M vs $74.59M W1;
   $63.83M vs $77.01M W2) and at p+3 ($94.61M vs $99.32M); it allows the same-quarter booking the
   data insist on (φ₀ = 0.23–0.41 on the ledger, 0.46–0.56 on booking data), so it is the rule that
   does not require a premise the pre-registered KL-3 test already falsified; its fitted
   35.90/47.29/16.81/0.00 is closer to K2's measured lead-time shape than ⅔/⅓ is.
   *Evidence for fixed:* joint still **loses to a one-line guide-growth baseline** at the next
   guide ($64.29M vs $59.06M), so its win over fixed buys nothing the pitch can trade; fixed is
   the only rule in the whole audit with a **gate-passing** result (p+4 common-9: ratio 0.889,
   interval 0.773–0.980, no deletion reversal); fixed has 4 conversion parameters against joint's
   7, on 22 identities; fixed has the **smaller oracle error** at every horizon ($48.81M vs
   $54.56M at p+2), i.e. more parameters are not buying a better converter; the joint weights are
   unstable across the audit's own origins (w₀ 0.359→0.605, w₁ 0.334→0.525); and ⅔ is the
   PIT-optimal carried weight on **both** windows and all three training windows (0.65–0.75), which
   is the only weight result in this line that survives W1 and W2.
   *Recommendation:* **(a) — present fixed, show joint as a labelled sensitivity, and state the
   same-quarter finding in words rather than by switching specs.** Why: joint's advantage is real
   but does not cross the baseline that matters, while fixed carries the only passing gate, half
   the parameters and the better oracle; switching to a 7-parameter rule to buy a win over a
   4-parameter rule that both still lose to guide-growth adds specification risk without adding a
   claim. *This choice is the humans', not mine.*

2. **λ estimation window: published spec (all history) vs `ex_covid` vs `last3_ex_covid`.**
   Options: (a) publish `last3_ex_covid`; (b) publish the raw ⅔ spec; (c) publish `ewm`
   (`kernel_engine_v2`'s frozen live default). Evidence: the raw spec's predictive distribution is
   **rejected** (PIT-KS p = 0.0027 W1 / 0.0298 W2) with +2.23pp bias; `last3_ex_covid` fixes both
   (p = 0.63 / 0.74; ratio 0.555 / 0.472) but is the best of 7 registered variants with no
   multiplicity correction, and "ex-COVID" is an ex-post outlier judgement. Recommendation: **(a)
   `last3_ex_covid`, disclosed as one of seven registered variants**, with the raw spec's numbers
   shown beside it so the selection is visible.

3. **What to claim about the share of the 4Q26 driver already printed at the 2 Oct pitch date.**
   Options: (a) "one third" (w = ⅔); (b) "one third to five eighths" (0.333 at w = ⅔, 0.620 at
   w = 0.38); (c) drop the claim. Evidence: this is the **one place** where the unidentified weight
   materially changes a claim, and it moves it the *opposite* way from everywhere else; the audit's
   own live figure is 33.91% for fixed and 17.88% for joint, and both are **model-input exposure,
   not booked revenue**. Recommendation: **(b), with the exposure label attached.**

4. **Which σ basis for the 5 Nov λ_Q3 control chart.** Options: (a) Q3's own sd, n = 3 (warning
   $4,761M, escalate $4,719M); (b) pooled σ across seasons ($4,706M / $4,608M); (c) both.
   Evidence: the tight chart's σ rests on three cells; the pooled chart is 2.3× wider; a print
   between $4,608M and $4,761M is a signal on one and noise on the other; and λ cannot separate
   cancellation from weak in-quarter booking either way. Recommendation: **(c) both, plus the
   discriminating cross-check** — (3Q26 unearned-fees y/y) − (3Q26 GBV y/y): ≤ −18pts means the
   unpaid book is at or above the 1H26 run-rate, −12 to −18pts is in line, wider than −8pts
   weakens the drag.

5. **Whether to present a point-in-time backtest of this line at all.** Options: (a) present it,
   explicitly labelled "guide-morning information set, includes the same-day letter"; (b) drop the
   backtest and present the kernel purely as management's own arithmetic; (c) present it and also
   show the 0/14 and 0/10 strict-origin refusal. Evidence: under strict pre-letter origins the
   printed-lag kernel has **zero** eligible observations in either window. Recommendation:
   **(c)** — a judge who finds the refusal himself will discount everything else on the page.

6. **The 4Q26 card value.** Options, all conditional on GBV_3Q26 = $26,300M: kernel w = ⅔ print
   $3,200M / guide $3,141M; `kernel_engine_v2` `ewm` $3,214.78M / $3,158.23M; joint $3,185.25M;
   fixed (audit fit) $3,160.55M; guide-growth $3,133.92M. Evidence: the spread across *rules* is
   $81M — thirteen times the $6M the ⅔-vs-0.38 weight fight is worth — so the card's uncertainty
   is the rule and the GBV input, not the weight. Recommendation: **quote the kernel print with the
   rule named and the guide-growth challenger beside it**, and convolve with the GBV_3Q26
   distribution before attaching any band (do **not** reuse the 2.6pp figure — see §7).

## 9. Judge Q&A

1. Q: Why should revenue be two-thirds last quarter's bookings plus one-third the quarter
   before?
   A: Two-thirds/one-third is not a measured cohort share and we do not present it as one — it
   is a forecasting weight, chosen because it is the RMSE-minimising carried weight in a strict
   point-in-time sweep on both of our windows (optimum 0.65–0.75, W1 and W2, all three training
   windows). The *reason* revenue lags GBV at all is the accounting: Airbnb books the whole
   reservation into GBV in the quarter it happens and recognises the fee at check-in, so the
   company's own 10-Q calls GBV "a leading indicator of revenue". The size of the lag has two
   independent checks that agree: the value-weighted booking-to-check-in lead in a 268,000-
   reservation panel is 58 days ≈ 1.9 months, and Airbnb's own opening unearned fees divided by
   quarterly revenue implies 0.66–0.88 quarters. Both land near one quarter of carry, which is what
   a ⅔/⅓ kernel is.

2. Q: Can you actually identify that weight from your data?
   A: No, and we say so. The leave-one-out minimiser is 0.76 on 22 quarters, 0.68 on 18, 0.32
   on 14 and 0.13 on 12, and the 95% block-bootstrap interval on the argmin covers roughly the
   whole unit interval. The critic's "the minimum is near ⅓" is true on the 2023Q1+ subsample and
   false on the post-COVID one. What makes this survivable is that it does not matter: re-estimating
   λ at each weight absorbs nearly all of the change, so the entire w ∈ [0.20, 0.80] band moves our
   4Q26 print by $13M, or 0.42%, and the ⅔-versus-0.38 fight is worth $6M, or 0.20%. The one claim
   the weight does move is the share of the driver already printed at our pitch date — 33% at ⅔ and
   62% at 0.38 — and we quote that as a range.

3. Q: You say management can see the quarter it is guiding. Can it?
   A: Most of it, not all of it — and we pre-registered that as falsifiable and it failed. A
   non-negative lag polynomial puts 0.23 to 0.41 of the weight on the *current* quarter's GBV in
   every estimation window, with bootstrap intervals excluding zero and a better out-of-sample
   error than the restricted φ₀ = 0 fit; the ledger-based estimate is 0.36–0.39 and the booking-data
   estimate 0.46–0.56. So roughly 40% of a quarter's revenue is booked inside that quarter. We say
   "most, not all", we never say 100% determined, and the earlier "82% of Q4 FX already determined"
   line has been struck.

4. Q: Does the kernel beat anything?
   A: It beats naive, AR(1), trailing-four and a vintage-stamped pre-guide Street on both
   windows. It **loses** to guide-midpoint-times-cushion by a wide margin once a guide exists
   (RMSE ratio 0.555 vs 0.377 on W1, 0.472 vs 0.319 on W2), and — the result we like least — at the
   next unissued guide it loses to a one-line rule that just extends the last issued guide's growth
   rate, $74.59M versus $59.06M. Under our own pre-registered standalone-eligibility audit neither
   the fixed nor the joint rule passes the promotion gate at any of the three horizons. The kernel
   is a scenario and reconstruction tool with an exactly reproducible accounting core, not a
   validated forecasting edge, and that is how we present it.

5. Q: If revenue is unavailable before the letter, what is your backtest measuring?
   A: Management's information set on guide morning, not ours the day before. Both GBV lags
   arrive in the very letter that carries the guide, so on a strict pre-letter origin our
   independent implementation refuses all 14 W1 and all 10 W2 origins. Our point-in-time numbers
   use the harness's documented convention that the same-day letter is in the information set. That
   is the right convention for asking "what arithmetic is management doing?" and the wrong one for
   claiming pre-guide alpha, and we do not make the second claim.

6. Q: How do you know on 5 November whether this broke?
   A: λ_Q3 becomes an identity on the print: printed 3Q26 revenue divided by $27,866.7M. At or
   above 17.09% ($4,761M) there is no leakage signal. Between 16.93% and 17.09% ($4,719–4,761M) is
   a one-sigma break on Q3's own dispersion — a warning, on three cells of σ, not a confirmation.
   Below 16.93% ($4,719M) is a two-sigma break implying more cancellation drag than management's
   own implied figure, and we escalate. The pooled-σ chart is 2.3× wider ($4,706M / $4,608M) and we
   quote both, because a λ miss cannot by itself separate RNPL cancellations from weak in-quarter
   booking; the discriminating cross-check is unearned-fees y/y minus GBV y/y.

## 10. Grade
Grade: B — the accounting core reproduces to machine precision (exit 0, 16 of 17 outputs
byte-identical, max |diff| 6.67e-06 in a diagnostic-only file, acceptance 12/12 confirmed a second
time by an independent implementation) and ⅔ is the PIT-optimal carried weight on both W1 and W2,
but the line is **descriptive**: its own pre-registered φ₀ = 0 test failed, its published
predictive distribution is rejected on both windows, its PIT backtest exists only under the
same-day-letter convention (0/14 and 0/10 strict origins), and at the next guide it fails the
pre-registered promotion gate against a one-line guide-growth baseline on both windows — so it is
not an A.
