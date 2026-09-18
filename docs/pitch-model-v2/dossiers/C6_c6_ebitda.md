# C6 — Adjusted EBITDA and margin, 3Q26 to FY27

## 1. Header
- Line: C6 · Judge's question: "Pick one FY27 margin. Why 34.6% or 35.7%, and what does the Street's 36.5% require?"
- Digger: opus · Date: 2026-09-18 · Commit: e6d9832 (branch `theo/pitch-model-v2`; the brief named b098ac2 and the tree was at 11b3d39 when I started — the orchestrator committed e6d9832 mid-wave. `git diff 11b3d39 e6d9832` touches only `analysis/src/pitch_model_v2/*`; **no file under `data/processed/margin_build/` or `docs/margin-build/` differs across any of the three**, so every number below is identical at b098ac2, 11b3d39 and e6d9832.)

**One-paragraph answer.** Pick **35.7%** for the model and carry **34.6%** as the calibrated scenario, because the two numbers are not rival forecasts — neither is a forecast. The 34.64% is the top-down combination extrapolated to h≥2, where it *fails its own pre-registered test* (1.026x the seasonal naive in W2); the 35.66% is a bottom-up cost stack whose four discretionary lines have no backtest at all. What separates them is one line: FY27 S&M, 23.51% of revenue under the run's mechanical residual allocation versus 21.86% built from the 10-K split. DEC-0011 already chose the line build as the cost stack, so 35.66% is the internally consistent choice and 34.64% belongs beside it as the run's own view. The Street's 36.45% is a third thing again: on our revenue it is $5,769M of FY27 EBITDA, **$125M above the line build and $286M above the combination**, and it requires — with every other line of our build held — FY27 marketing growth of about **+9%** instead of our +15%, an FY27 incremental margin of **43.7%** against our 35.0% (LB) / 24.7% (CC), and a margin **above FY24's 36.40% all-time peak** in a year management has already started calling an investment year. It is a spending call in all three directions and nothing in this repo forecasts it.

## 2. The number

**Two objects, both ours, and they must not be blended.**
- **LB — the line build** (`40_line_build`, 15 Sep 2026): a bottom-up cost stack, every parameter sourced to a 10-K/10-Q line in `40_params.csv`, with 2H26 reconciled to management's "margin down slightly" sentence treated as a **budget** (DEC-0011). This is the model's base.
- **CC — the calibrated combination** (`23_final_model`, 14 Sep 2026, post-WS31 audit): a six-member leave-future-out margin combination times the bridge-v3 revenue leg. It is the **only** object here that was backtested, and per DEC-0011 its dollar object is **reserved for the 5 Nov card**, not for the workbook.

At 3Q26 the two are $20.5M apart (0.43pp) and at FY26 they are $1.0M apart (0.007pp). At FY27 they are $161M apart (1.02pp), and that gap is the judge's question.

### Adjusted EBITDA, USD m

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base **LB** | 3Q26 | 2,419.6 | 2,361.2 | 2,517.0 | USD m | 2026-09-11 data / 2026-09-15 build |
| base **LB** | 4Q26 | 898.9 | 775.3 | 1,011.7 | USD m | 2026-09-11 / 15 |
| base **LB** | FY26 | 5,098.5 | 4,916.5 | 5,296.8 | USD m | 2026-09-11 / 15 |
| base **LB** | FY27 | 5,644.2 | 4,409.2 | 6,635.9 | USD m | 2026-09-11 / 15 |
| short | 3Q26 | 2,289.8 | — | — | USD m | 2026-09-15 |
| short | 4Q26 | 699.6 | 699.6 | 876.3 | USD m | 2026-09-15 |
| short | FY26 | 4,769.4 | 4,769.4 | 4,946.1 | USD m | 2026-09-15 |
| short | FY27 | 4,761.4 | — | — | USD m | 2026-09-15 |
| breaker (ramp pauses) | 3Q26 | 2,443.3 | — | — | USD m | 2026-09-15 |
| breaker (ramp pauses) | 4Q26 | 970.9 | — | — | USD m | 2026-09-15 |
| breaker (ramp pauses) | FY26 | 5,194.2 | — | — | USD m | 2026-09-15 |
| breaker (ramp pauses) | FY27 | 6,023.5 | — | — | USD m | 2026-09-15 |
| alt_combination **CC** | 3Q26 | 2,399.1 | 2,336.5 | 2,461.7 | USD m | 2026-09-11 / 14 |
| alt_combination **CC** | 4Q26 | 918.4 | 800.0 | 1,036.8 | USD m | 2026-09-11 / 14, `23_forecast_quarterly` q10/q90 |
| alt_combination **CC** | FY26 | 5,097.5 | — | — | USD m | 2026-09-11 / 14 |
| alt_combination **CC** | FY27 | 5,483.3 | — | — | USD m | 2026-09-11 / 14 (SCENARIO) |
| street (LSEG) | 3Q26 | 2,361.5 | — | — | USD m | 2026-09-11, n 36, EBITDA sd 20.0 |
| street (LSEG) | 4Q26 | 913.7 | — | — | USD m | 2026-09-11, n 36, sd 26.5 |
| street (LSEG) | FY26 | 5,053.7 | — | — | USD m | 2026-09-11, n 44, sd 40.2 |
| street (LSEG) | FY27 | 5,766.1 | — | — | USD m | 2026-09-11, n 44, sd 154.2 |

### Adjusted EBITDA margin, %

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base **LB** | 3Q26 | 50.37 | 49.66 | 52.39 | pct | 2026-09-15 |
| base **LB** | 4Q26 | 28.28 | 24.82 | 31.34 | pct | 2026-09-15 |
| base **LB** | FY26 | 35.73 | 34.71 | 36.80 | pct | 2026-09-15 |
| base **LB** | FY27 | 35.66 | 29.50 | 40.05 | pct | 2026-09-15 |
| short | 3Q26 | 48.92 | — | — | pct | 2026-09-15 |
| short | 4Q26 | 23.59 | 23.59 | 29.55 | pct | 2026-09-15 |
| short | FY26 | 34.23 | 34.23 | 35.50 | pct | 2026-09-15 |
| short | FY27 | 31.93 | — | — | pct | 2026-09-15 |
| breaker (ramp pauses) | 3Q26 | 50.86 | — | — | pct | 2026-09-15 |
| breaker (ramp pauses) | 4Q26 | 30.55 | — | — | pct | 2026-09-15 |
| breaker (ramp pauses) | FY26 | 36.40 | — | — | pct | 2026-09-15 |
| breaker (ramp pauses) | FY27 | 38.05 | — | — | pct | 2026-09-15 |
| alt_combination **CC** | 3Q26 | 49.94 | 47.86 | 52.02 | pct | 2026-09-11 / 14 |
| alt_combination **CC** | 4Q26 | 28.90 | — | — | pct | h=1 rule: the Street carries it |
| alt_combination **CC** | FY26 | 35.73 | — | — | pct | 35.727, floor 35.5 |
| alt_combination **CC** | FY27 | 34.64 | — | — | pct | SCENARIO, h>=2 fails |
| street (LSEG) | 3Q26 | 49.78 | — | — | pct | 2026-09-11 |
| street (LSEG) | 4Q26 | 28.90 | — | — | pct | 2026-09-11 |
| street (LSEG) | FY26 | 35.62 | — | — | pct | 2026-09-11, floor 35.5 |
| street (LSEG) | FY27 | 36.45 | — | — | pct | 2026-09-11 |

**Scenario definitions (all reproduced, none invented), matching C4's mapping exactly.**
- **base (LB)** = `40_lines_quarterly.csv` / `40_annual.csv` scenario `base`. Low/high are the sourced ends of the same build's own grid: `both_bear` and `both_bull` (revenue and cost parameters adverse / favourable together), except the 3Q26 high, which is `evidence_only` ($2,517.0M / 52.39%) — the build with the sentence reconciliation switched off, the case DEC-0011 names as the upside risk.
- **short** = `40_short_case_quarterly.csv` / `40_short_case_summary.csv`, case `short_costs_at_budget`: nights at the guide low in 3Q26 then ~3pts below the team path, ADR ex-FX flat, RNPL overlays (ops per booking +4%, chargebacks +$0.15, funds held −10%), **costs left at management's budget**. Its 4Q26/FY26 high is `short_with_q4_marketing_cut` — $176.7M off 4Q26 marketing, the cut that restores FY26 to exactly 35.50%.
- **breaker ("the ramp pauses")** = `40_annual.csv` scenario `cost_bull`: 2H26 marketing +18% rather than +25%, FY27 marketing +10% rather than +15%, field ops +14%/+8% rather than +18%/+11%, plus the favourable hosting/ops/pd/G&A parameters — each one a row in `40_params.csv`. Same base revenue path.
- **alt_combination (CC)** = `23_final_model` spec `stack_clip`; 3Q26 dollars are `final-margin|combined_dollar_from_margin`, band = that object's own conformal qhat80 $62.58M. 4Q26 is the **Street** by the pre-registered h=1 rule; FY26 is 1H26 actual + 3Q26 CC + 4Q26 Street; FY27 is the sum of four scenario quarters.
- **street** = the LSEG-family panel at 2026-09-11 in `23_vs_consensus.csv` (DEC-0013). FY27 36.45% is the *implied* margin (EBITDA ÷ revenue); the LSEG margin *field* reads 35.06% and is not used here.

**The identity (DEC-0003).** Adjusted EBITDA = revenue − cash costs + D&A + lodging-tax reserves. It holds to **4.5e-13** on all 48 line-build rows and all 6 short-case rows, and to **6.8e-13** on the run's quarters (where D&A is already inside the add-back column). Forward, lodging reserves are 0 in every scenario (`lodging_reserves_fwd` = 0; 4Q25's $81M is treated as a one-off), so D&A **is** the entire add-back: $20.634M a quarter, $80.27M FY26 (1H26 actual $39M + two forecast quarters), $82.54M FY27.

**The number that answers the judge.** $158.3M is 1.0pp of FY27 margin; $48.0M is 1.0pp of 3Q26. So:

| FY27 view | margin | EBITDA on **our** $15,829M revenue | vs LB | implied FY27 S&M on our other four lines | implied S&M y/y | incremental margin |
|---|---|---|---|---|---|---|
| **line build (LB)** | **35.66%** | $5,644.2M | — | $3,459.6M / 21.86% | +13.8% | **35.0%** |
| calibrated combination (CC) | 34.64% | $5,483.3M | −$160.9M | $3,620.5M / 22.87% | +19.1% | 24.7% |
| Street | 36.45% | $5,769.5M | **+$125.3M** | $3,334.4M / 21.07% | **+9.7%** | **43.7%** |
| short | 31.93% | $4,761.4M on its own $14,914M | — | — | +12.7% | −0.8% |
| breaker | 38.05% | $6,023.5M | +$379.3M | $3,080.4M / 19.46% | +2.6% | 53.1% |

Incremental margin is measured against each view's **own** FY26 base, the SYNTHESIS convention (CC 24.7%, Street 43.7%). Read across the `d_fy27_margin_pp` column of `40_sensitivities.csv`: marketing growth is −0.669pp per +5pts, so the Street's +0.79pp over the line build is **FY27 marketing at about +9.1% instead of +15%**, holding the other twenty-two parameters. FY25 actual margin was 35.10% and FY24 36.40%; the Street is asking FY27 to set a new all-time high.

### 2a. Model inputs (machine-readable)

Per DEC-0011 the workbook's cost stack is the line build, so `adj_ebitda_musd` / `adj_ebitda_margin_pct` under scenario `base (line build)` are the model's numbers; the calibrated combination's dollar object appears only as the `card_*` rows and under scenario `alt_combination`. `da_musd` is the D&A that the DEC-0003 identity adds back and is identical across the three scenarios (the M7 rule, $20.634M a quarter; FY26 includes $39M of 1H26 actual). Street rows are the LSEG-family panel of 2026-09-11 per DEC-0013. Scenario keys follow C4 exactly.

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| adj_ebitda_musd | base (line build) | 3Q26 | 2419.6 | USD m | 40_lines_quarterly.csv adj_ebitda scenario base |
| adj_ebitda_musd | base (line build) | 4Q26 | 898.9 | USD m | 40_lines_quarterly.csv adj_ebitda scenario base |
| adj_ebitda_musd | base (line build) | FY26 | 5098.5 | USD m | 40_annual.csv FY26 base; 1H26 actual 1780 plus 2H26 |
| adj_ebitda_musd | base (line build) | FY27 | 5644.2 | USD m | 40_annual.csv FY27 base |
| adj_ebitda_musd | short | 3Q26 | 2289.8 | USD m | 40_short_case_quarterly.csv short_costs_at_budget |
| adj_ebitda_musd | short | 4Q26 | 699.6 | USD m | 40_short_case_quarterly.csv short_costs_at_budget |
| adj_ebitda_musd | short | FY26 | 4769.4 | USD m | 40_short_case_summary.csv fy26_ebitda |
| adj_ebitda_musd | short | FY27 | 4761.4 | USD m | 40_short_case_summary.csv fy27_ebitda |
| adj_ebitda_musd | breaker (ramp pauses) | 3Q26 | 2443.3 | USD m | 40_lines_quarterly.csv scenario cost_bull |
| adj_ebitda_musd | breaker (ramp pauses) | 4Q26 | 970.9 | USD m | 40_lines_quarterly.csv scenario cost_bull |
| adj_ebitda_musd | breaker (ramp pauses) | FY26 | 5194.2 | USD m | 40_annual.csv FY26 cost_bull |
| adj_ebitda_musd | breaker (ramp pauses) | FY27 | 6023.5 | USD m | 40_annual.csv FY27 cost_bull |
| adj_ebitda_margin_pct | base (line build) | 3Q26 | 50.37 | pct | on revenue 4804.0 |
| adj_ebitda_margin_pct | base (line build) | 4Q26 | 28.28 | pct | on revenue 3178.1 |
| adj_ebitda_margin_pct | base (line build) | FY26 | 35.73 | pct | on revenue 14268.1; floor 35.5 |
| adj_ebitda_margin_pct | base (line build) | FY27 | 35.66 | pct | on revenue 15828.6; the memo's 35.7 |
| adj_ebitda_margin_pct | short | 3Q26 | 48.92 | pct | on revenue 4680.9 |
| adj_ebitda_margin_pct | short | 4Q26 | 23.59 | pct | on revenue 2965.9; 29.55 with the 176.7 marketing cut |
| adj_ebitda_margin_pct | short | FY26 | 34.23 | pct | on revenue 13932.8; 35.50 with the cut |
| adj_ebitda_margin_pct | short | FY27 | 31.93 | pct | on revenue 14913.5 |
| adj_ebitda_margin_pct | breaker (ramp pauses) | 3Q26 | 50.86 | pct | base revenue path 4804.0 |
| adj_ebitda_margin_pct | breaker (ramp pauses) | 4Q26 | 30.55 | pct | base revenue path 3178.1 |
| adj_ebitda_margin_pct | breaker (ramp pauses) | FY26 | 36.40 | pct | base revenue path 14268.1 |
| adj_ebitda_margin_pct | breaker (ramp pauses) | FY27 | 38.05 | pct | base revenue path 15828.6 |
| da_musd | base (line build) | 3Q26 | 20.6 | USD m | M7 rule 20.633971 per quarter |
| da_musd | base (line build) | 4Q26 | 20.6 | USD m | M7 rule 20.633971 per quarter |
| da_musd | base (line build) | FY26 | 80.3 | USD m | 1H26 actual 39.0 plus two forecast quarters |
| da_musd | base (line build) | FY27 | 82.5 | USD m | four forecast quarters |
| da_musd | short | 3Q26 | 20.6 | USD m | unchanged by the short overlays |
| da_musd | short | 4Q26 | 20.6 | USD m | unchanged by the short overlays |
| da_musd | short | FY26 | 80.3 | USD m | unchanged by the short overlays |
| da_musd | short | FY27 | 82.5 | USD m | unchanged by the short overlays |
| da_musd | breaker (ramp pauses) | 3Q26 | 20.6 | USD m | no D and A parameter in the cost_bull column |
| da_musd | breaker (ramp pauses) | 4Q26 | 20.6 | USD m | no D and A parameter in the cost_bull column |
| da_musd | breaker (ramp pauses) | FY26 | 80.3 | USD m | no D and A parameter in the cost_bull column |
| da_musd | breaker (ramp pauses) | FY27 | 82.5 | USD m | no D and A parameter in the cost_bull column |
| card_ebitda_musd | base | 3Q26 | 2399.1 | USD m | 23_card_5nov.csv combined_dollar_from_margin stack_clip |
| card_ebitda_low_musd | base | 3Q26 | 2336.5 | USD m | point minus own conformal qhat80 62.58; card prints 2337 |
| card_ebitda_high_musd | base | 3Q26 | 2461.7 | USD m | point plus own conformal qhat80 62.58; card prints 2462 |
| p_beat | base | 3Q26 | 0.779 | probability | Gaussian sd 48.8 on the same object; descriptive not validated |
| combination_fy27_margin_pct | alt_combination | FY27 | 34.64 | pct | the run's FY27 beside the line build's 35.66; SCENARIO |
| adj_ebitda_musd | alt_combination | 3Q26 | 2399.1 | USD m | same object as card_ebitda_musd |
| adj_ebitda_musd | alt_combination | 4Q26 | 918.4 | USD m | the Street by the h=1 rule |
| adj_ebitda_musd | alt_combination | FY26 | 5097.5 | USD m | 1H26 actual plus 3Q26 CC plus 4Q26 Street |
| adj_ebitda_musd | alt_combination | FY27 | 5483.3 | USD m | SCENARIO; h>=2 fails its test |
| adj_ebitda_margin_pct | alt_combination | 3Q26 | 49.94 | pct | band 47.86 to 52.02 |
| adj_ebitda_margin_pct | alt_combination | 4Q26 | 28.90 | pct | equals the Street to 5e-7 |
| adj_ebitda_margin_pct | alt_combination | FY26 | 35.73 | pct | 35.727 exactly |
| adj_ebitda_musd | street | 3Q26 | 2361.5 | USD m | LSEG n 36 EBITDA sd 20.0 |
| adj_ebitda_musd | street | 4Q26 | 913.7 | USD m | LSEG n 36 EBITDA sd 26.5 |
| adj_ebitda_musd | street | FY26 | 5053.7 | USD m | LSEG n 44 EBITDA sd 40.2 |
| adj_ebitda_musd | street | FY27 | 5766.1 | USD m | LSEG n 44 EBITDA sd 154.2 |
| adj_ebitda_margin_pct | street | 3Q26 | 49.78 | pct | on the Street's own revenue 4744.3 |
| adj_ebitda_margin_pct | street | 4Q26 | 28.90 | pct | on the Street's own revenue 3161.8 |
| adj_ebitda_margin_pct | street | FY26 | 35.62 | pct | on the Street's own revenue 14189.6 |
| adj_ebitda_margin_pct | street | FY27 | 36.45 | pct | implied EBITDA over revenue; the LSEG margin field reads 35.06 |

## 3. Derivation chain

**Base (LB), the model's line:**
1. 10-K / 10-Q facts (FY25 S&M split $1,595M marketing + $781M field cash; payment processing $1,665M incl. $67M chargebacks; hosting commitments $672M-through-2027 re-cut to $1.7bn-through-2031; 1H26 MD&A component deltas; the 6 Aug 2026 guide $4,690–4,770M and the "margin down slightly vs 3Q25" sentence) →
2. `data/processed/margin_build/40_line_build/40_params.csv` (46 named parameters, each with its source) and `02_financial_panel/02_panel_quarterly.csv` (actuals 1Q23–2Q26) and `06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv` (the revenue path) →
3. `analysis/src/margin_build/40_line_build/run.py` — five cash lines built per quarter, the $97.36M sentence gap allocated 70% to 3Q26 marketing / 30% to hosting, D&A and lodging reserves added back →
4. `40_lines_quarterly.csv` columns `adj_ebitda`, `adj_ebitda_margin_pct`, rows `3Q26`/`4Q26`/`1Q27`–`4Q27` scenario `base`; annualised in `40_annual.csv` rows `FY26`/`FY27` scenario `base`.

**alt_combination (CC), the 5 Nov card's object:**
1. LSEG-family consensus vintages, the guidance ledger's quarterly margin sentences, and the M1/M2/M3/M5/M6 member forecasts →
2. `data/processed/margin_build/10_harness_margin/scoreboard_margin.csv` (PIT member errors) →
3. `analysis/src/margin_build/23_final_model/run.py` — inverse-MAE weights shrunk halfway to equal (λ 0.5, fixed a priori), print-date-gated, then clipped to the management sentence →
4. `23_combination_live.csv` row `adj_ebitda_margin_pct / 2026Q3 / stack_clip` → `point` 49.93994; `23_dollar_from_margin_live.csv` same row → `point` 2399.1324 on `revenue_musd` 4804.0355; `23_card_5nov.csv`; `23_forecast_annual.csv` rows FY26/FY27 scenario base.

**Short:** the same `run.py` §8b, revenue-path override plus RNPL overlays on the budgeted cost base → `40_short_case_quarterly.csv`, `40_short_case_summary.csv`.

## 4. Governing sources

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-08-06 | 2Q26 shareholder letter, via `02_guidance_ledger.csv` and `40_params.csv` | 3Q26 revenue guide $4,690–4,770M; "adjusted EBITDA margin down slightly vs 3Q25"; FY26 "at least 35.5%" | **Governs** the 2H26 cost budget and the 50.085% 3Q26 ceiling (3Q25 50.09% − 0.0 under the clip rule; the LB uses −0.5pp = 49.59% at guide revenue) |
| 2026-09-11 | `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv` | actuals to 2Q26: 1H26 revenue $6,286M, adj EBITDA $1,780M, D&A $39M; 3Q25 50.09%, 4Q25 28.29%, FY25 35.10%, FY24 36.40% | **Governs** every base and lap. DEC-0003 sets the basis |
| 2026-09-11 | LSEG-family panel in `23_vs_consensus.csv` (DEC-0013) | 3Q26 $2,361.5M / 49.78% (n 36); 4Q26 $913.7M / 28.90%; FY26 $5,053.7M / 35.62% (n 44); FY27 $5,766.1M / **36.45%** (n 44, sd $154M) | **Governs** the Street rows |
| 2026-09-14 | `docs/margin-build/SYNTHESIS.md` §§1–2, 5–8, 11 (post-WS31 audit) and `23_final_model` | 3Q26 49.94% / $2,399M, band $2,337–2,462M, P(beat) 0.779; 4Q26 28.90% (Street); FY26 35.73% / $5,098M; FY27 34.64% / $5,483M **labelled a spending scenario**; h=0 passes, h=1 fails vs the Street, h=2 fails in W2 | **Governs** the card and every scored claim. Supersedes the whole `_pre_audit/` tree and the pre-audit band $2,299–2,499M, P 0.77, FY26 bear/bull 35.70/35.78 and FY27 bear/bull 34.512/34.707 |
| 2026-09-15 04:35 | SYNTHESIS §11 amendment | FY27 S&M restated $3,740M / 23.6% → $3,721M / 23.5% | **Governs**; supersedes the 14 Sep figure |
| 2026-09-15 | `docs/margin-build/notes/40_line_build.md` + `40_line_build` outputs | 3Q26 $2,420M / 50.37%; 4Q26 $899M / 28.28%; FY26 $5,099M / 35.73%; FY27 $5,644M / 35.66%; evidence-only 3Q26 52.39%; "the only line genuinely forecastable out of sample is cost of revenue" | **Governs** the model's base per DEC-0011. Later than SYNTHESIS and does **not** supersede it — different object |
| 2026-09-17 | `questions/fy26-margin-sentence/` C04 **revision 2** | 5 Nov FY26 sentence: held 35.5% 0.33 / "≈36%" 0.30 / ≥36.5% 0.05 / softer 0.27 / none 0.05 | **Governs**; supersedes revision 1 (0.26/0.42/0.05/0.24/0.03) and outranks M3's bare "approximately 36%, p ≈ 0.45–0.50" |
| 2026-09-17 | `questions/q4-margin-direction-sentence/` C09 **revision 2** | 4Q26 margin sentence: down 0.22 / flat 0.26 / **up 0.47** / none 0.05 | **Governs**; supersedes revision 1 (0.28/0.27/0.40/0.05) |
| 2026-09-17 | `questions/fy27-margin-guide/` F03 **revision 2** (LITERAL convention A08-01) | Feb-2027 FY27 margin guide: ≥36.5% 0.02 / 36.0–36.4% 0.04 / 35.5–35.9% 0.10 / <35.5% or investment-year 0.36 / **no numeric guidance 0.48** | **Governs**; supersedes revision 1 (0.08/0.17/0.27/0.38/0.10), **which the folder's own README still prints** |
| 2026-09-17 | `questions/risk-q3-margin-sandbagged/` R05 **revision 2** | P(3Q26 margin ≥ 51.5%) = **0.22**, CI 0.13–0.32 | **Governs**; supersedes the README's revision-1 headline 0.17 |
| 2026-09-17 | `deck/drafts/memo_v3_short_2026-09-17.md` | team 3Q26 $2,420M / 50.4%, 4Q26 $899M / 28.3%, FY26 35.7%, FY27 $5,644M / 35.7%; short $2,290M / 48.9% … $4,761M / 31.9%; "pick one FY27 margin build (run 34.6% vs line build 35.7%) before 2 Oct" | **Governs** the memo's presentation; it is the source of the judge's question and it leaves the choice open (§8.1 below) |
| 2026-09-18 | DEC-0003, DEC-0011, DEC-0016 (`docs/pitch-model-v2/DECISIONS.md`) | history basis; line build is the cost stack and CC's dollar object is reserved for the 5 Nov card; no leaning | **Governs** this dossier's structure |

Web fetches: **none**. Everything above is in the repo.

## 5. Reproduction receipt
- Receipt: `data/processed/pitch_model_v2/receipts/C6/receipt.json`
- Command: `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id C6 --watch data/processed/margin_build/23_final_model --watch data/processed/margin_build/40_line_build --watch data/processed/margin_build/02_financial_panel --cmd "python3 data/processed/pitch_model_v2/receipts/C6/c6_ebitda_recompute.py"` · Exit: **0** · Wall: 0.2s · Interpreter: `python3` (3.13.0, pandas 3.0.0)
- Output: `data/processed/pitch_model_v2/receipts/C6/c6_checks.csv` — **35 of 37 checks match**, the two non-matches being deliberate detections described below. Headline cells: `23_dollar_from_margin_live.csv` row `2026Q3 / stack_clip`, column `point` = **2,399.1324** recomputed from the six member weights × points in `23_combination_live.csv` (49.93993908638773%) × the bridge-v3 revenue leg 4,804.0355 · Committed value: 2,399.132402388442 · Tolerance: ±$0.5M · **Match: yes**. `40_annual.csv` FY27 base `adj_ebitda` / `adj_ebitda_margin_pct` = **5,644.2042 / 35.65825** rebuilt by summing the four 2027 quarters of `40_lines_quarterly.csv` · Committed: identical to 0.0 · Tolerance ±$0.5M / ±0.005pp · **Match: yes**.
- **No margin package was run by me.** Per the brief and the orchestrator's instruction, the `MARGIN_VERIFY_ONLY=1` run for this wave is **C4's**: `data/processed/pitch_model_v2/receipts/C4/receipt_23_verify.json` (exit 0, wall 5.9s, `"restored": true`, `"changed": []`), whose comparison block at `receipts/C4/stdout_23_verify.txt` reports **24 of 24 committed CSVs identical**, worst `max|d|` 1.6e-11. C4 also holds the `40_line_build` re-run (`receipt_40_line_build.json`, exit 0, restored true), whose only committed-file change is a tie-order swap of two rows in `40_sensitivities.csv` (`d_fy27_margin_pp == 0.0` exactly for three parameters; no value changed). My script reads committed CSVs only and writes only into `receipts/C6/`; `"changed": []`, `"new_files": []`, `"restored": true`.
- Artefacts in the receipt folder: `c6_ebitda_recompute.py` (the script), `c6_checks.csv` (37 checks), `c6_ebitda_scenarios.csv` (the §2 tables), `c6_fy27_bridge.csv` (the FY27 table in §2), `c6_member_recompute.csv` (the six-member rebuild of 49.94%), `stdout.txt`.
- **What was checked, in groups.** A — the DEC-0003 identity on all 48 line-build rows (4.5e-13), all 6 short-case rows (0.0), the run's quarters (6.8e-13), and margin = EBITDA ÷ revenue everywhere (3.6e-15). B — the 3Q26 combination margin rebuilt from committed weights × points (exact to 0.0; weights sum to 1 to 3e-16; the sentence clip did **not** bind, raw = clipped, 0.1455pp under the 50.0855% ceiling). C — the dollar object, its band, and the four-member cross-check $2,411.0M. D — P(beat) 0.779408 and the +$37.61M beat, both exact. E — FY26 = 1H26 actual + 3Q26 + 4Q26 and FY27 = sum of four, for **both** builds, plus 1H26 actual $6,286M / $1,780M, and 4Q26 CC = Street to 4.8e-7pp. F — the Street's FY27 requirement: margin 36.4497%, incremental margin 43.71% (SYNTHESIS 43.7), CC incremental 24.72% (SYNTHESIS 24.7), Street-implied FY27 S&M $3,328.5M (C4/DEC-0011 $3,328M).
- **The two non-matches, and why neither is a reproduction failure.**
  1. **`40_vs_run_and_street.csv` is a stale orphan.** It is tracked (from PR #56) but the current `run.py` writes `40_vs_run.csv`, not it — which is why C4's re-run left it untouched. Its 3Q26 `line_build` adj EBITDA is **$2,615.9M / 54.45%**, which matches **no** committed scenario (nearest is `evidence_only` at $2,517.0M, $98.9M away). `40_vs_run.csv` reproduces the base exactly ($2,419.6425M). **Do not read a line-build number out of `40_vs_run_and_street.csv`.**
  2. **DEC-0003's narrow wording fails on the printed history by up to $15M.** On 1Q23–2Q26 the residual of `revenue − cash costs + D&A + lodging reserves − adj EBITDA` is exactly **−(acquisition impacts + IPO settlement)**: worst $15M (2Q23), mean $4.8M. Using the panel's full `other_addbacks_total` (lodging + acquisition + IPO + restructuring) the identity is **exact (0.0) in all 14 quarters**. Forward this is moot — acquisition impacts and the IPO settlement have no forecast term and lodging reserves are set to 0 — so DEC-0003's form is right for the forecast and needs the extra add-backs when it is used to check a printed quarter.

## 6. Test record

`prior_basis = PIT` throughout, from `23_combination_scores.csv` / `23_dollar_from_margin_scores.csv`, spec `stack_clip`. "Naive" is `seasonal_naive` = y[q−4], which for this line **is management's own sentence as a level**.

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W1 | 14 | `adj_ebitda_margin_pct` MAE h=0 | **1.126pp** (rw 0.823) | 2.237pp → **0.504x** (rw 0.430) | n/a (no guide for a margin ratio) | 1.592pp → **0.708x** | Primary: beat `seasonal_naive` at h=0 **and** h=1, both windows, both weightings | **PASS**; NW(1) t −3.60 p 0.0003, 11 of 14, sign p 0.0032; vs Street sign p 0.029 |
| W2 | 10 | same | **0.788pp** (rw 0.662) | → **0.402x** (rw 0.377) | n/a | → **0.601x** | same | **PASS**; t −3.84 p 0.0001, 9 of 10, sign p 0.011; vs Street sign p 0.055 |
| W1 | 13 | same, h=1 | 1.952pp | 0.831x | n/a | **1.189x** | Secondary: not worse than the best single non-oracle object by >10%; at h=1 not worse than the Street | **FAIL vs the Street.** Consequence applied: **4Q26 is quoted from the Street** |
| W2 | 9 | same, h=1 | 1.269pp | 0.804x | n/a | **1.278x** | same | **FAIL** |
| W1 | 12 | same, h=2 | 2.229pp | 0.900x | n/a | not published | h=2 must beat the naive in both windows | fail in W2 below |
| W2 | 8 | same, h=2 | 1.766pp | **1.026x** | n/a | — | same | **FAIL.** Consequence applied: **FY27 is a scenario, not a forecast** |
| W1 | 14 | `adj_ebitda_musd`, the adopted `combined_dollar_from_margin`, h=0 | **$30.7M** (rw 24.3) | **0.248x** | n/a | **0.470x** (rw 0.389) | same primary | **PASS**; t −3.55 p 0.0004, better than the naive 13 of 14 and **better than the Street 14 of 14**, sign p 0.0001 |
| W2 | 10 | same | **$25.8M** (rw 21.4) | **0.264x** | n/a | **0.445x** | same | **PASS**; 9 of 10 vs naive, **10 of 10 vs Street**, sign p 0.0010 |
| W1 / W2 | 13 / 9 | same, h=1 | $78.3M / $75.1M | 0.601x / 0.828x | n/a | **1.195x / 1.607x** | same | **FAIL** |
| W1 / W2 | 14 / 10 | four-member dollar combination (labelled **cross-check only**) | $39.7M / $30.9M | 0.322x / 0.316x | n/a | 0.608x / 0.531x | WS31 audit 04 demoted it | reported, not quoted |
| — | — | `40_line_build` (the **base** of this dossier) | **no backtest exists** | — | — | — | none written | **not tested.** Its 4-row backcast: FY25 cost of revenue from FY24-knowable rates **−1.0%** (out of sample), FY25 ops & support **+4.6%** (out of sample), 1H26 cost of revenue **+0.8%** (in sample), 1H26 ops & support **0.002%** (a calibration identity, not a test). Its own note: "the only line that is genuinely forecastable out of sample is cost of revenue" |
| — | — | short case | no backtest | — | — | — | none | scenario |
| — | — | interval coverage, h=0 | cov80 **0.93 (W1) / 1.00 (W2)** against nominal 0.80 | — | — | — | — | over-covers. The conformal band is **descriptive**: the pool was chosen after seeing the scoreboard and "attained coverage 82–91%" is **withdrawn** (it was the rank grid, now `rank_grid_cov80_lo/hi`) |

Two further honesty items that belong in the record. **The h=0 result is retrospective**: the six-member pool was selected after seeing the scoreboard, so every ratio and p-value above prices the combination *given* the pool, not the pool. And **the hindsight share (W1 0.019, W2 −0.059) is not evidence against that** — it says the *weights* contain nothing fitted on the future, nothing more. 5 Nov 2026 is the first out-of-sample observation.

**Strongest known failure:** nothing in this build forecasts the adjusted EBITDA margin better than the Street beyond h=0 — the combination loses to the raw Street by 19% (W1) and 28% (W2) at h=1 and fails outright against the seasonal naive at h=2 in W2 (1.026x) — so **both** FY27 numbers the judge is asked to choose between are untested, and the one this dossier adopts (35.66%) comes from a build whose four discretionary cost lines have no backtest at all.

## 7. Kill list and consistency

**Kill-list check.** Nothing withdrawn is quoted. Named explicitly because the C6 literature is full of them:
- **M3's LIVE 4Q26 34.51% / FY26 37.03%** — withdrawn and stamped NOT QUOTABLE; not used. M3 survives here only as the **allocation result** and the **budget identity**.
- **M6's FY28 31.3%** and M1's trend FY28 32.6% — withdrawn / unlabelled; the only FY28 figure that may be shown is the FY27 margin rolled flat (34.64%), and it must carry the "NOT a forecast" label the CSV itself carries. FY28 is out of C6's period in any case.
- **M2's SARIMA LIVE 3Q26 51.50%** — disowned by its own author; not used. (FAMILY_A's 51.435% appears only as a member point inside the combination.)
- **P(3Q26 EBITDA beats Street) = 0.77** — withdrawn (it mixed the margin route's band with the four-member object's sd). The governing number is **0.779**, and the band and the sd now come from the same object.
- **The pre-audit 3Q26 band $2,299–2,499M**, EPS band $2.74–3.02, FY26 bear/bull 35.70/35.78, FY27 bear/bull 34.512/34.707, 3Q26 S&M $790.2M — all superseded on 14–15 Sep. They survive in `23_final_model/_pre_audit/` and `20_scoreboard/_pre_audit/`; **do not read from those folders**.
- **"Attained coverage 82–91%"** — withdrawn; it is the rank grid, not a measurement.
- **"Airbnb has no cost dial"** — withdrawn (k 0.14, t 0.47, n 18, SE ≈ 0.30, 95% CI ≈ −0.44 to +0.72: imprecise, not zero).
- **M6's "the floor survives a 1.9–2.5% 2H26 shortfall"** — on the kill list; the governing figures are **0.63% ($50.1M) costs held / 0.94% ($74.8M) costs flexed** (`23_fy26_floor_breakeven.csv`).
- **WS31b's 4Q26 margin profile 24.7–25.9%** — not cited; SYNTHESIS §8.1 forbids it until it is reconciled or retired.
- **AGENT_BRIEF §6 items:** no FY27 *revenue* level edge is claimed here (the $15,829M path is an input from R6/D3, not a C6 result); "no single object beats guide × cushion on both windows" is the wording used, never "nothing beats it"; no September consensus value is mixed into a historical guide date (the 11 Sep LSEG panel is used only for LIVE rows).
- **`40_vs_run_and_street.csv`** — added to the local do-not-quote list by §5.2 above.

**Conflicts found and their resolution.**
1. **FY27 34.64% (CC) vs 35.66% (LB) vs 36.45% (Street).** Real, unresolved, and it is §8.1. Both of ours are untested; the 1.02pp between them is $161M and is almost entirely FY27 S&M (23.51% vs 21.86% of revenue). Memo v3 §"Still open" already flags it as a decision due before 2 Oct.
2. **3Q26 49.94% (CC) vs 50.37% (LB, the memo's "50.4%").** Not a conflict of fact — two objects, $20.5M apart, 0.43pp. The LB is higher because its built cost lines land $20.5M below the residual allocation the CC's adopted margin implies. Per DEC-0011 the workbook shows **50.37% / $2,420M** and the 5 Nov card shows **49.94% / $2,399M**; the reconciliation line is $20.5M and must be on the page, or a judge will find it.
3. **4Q26 28.28% (LB) vs 28.90% (CC = Street).** 0.61pp, $19.5M. The CC number is *not* a forecast — at h=1 the pre-registered test failed and the Street was adopted. So at 4Q26 the model's only genuine view is the line build's 28.28%, and it is **below** consensus; the memo should say that rather than quote 28.90% as ours. Cross-check: C09 rev 2 puts P(management says 4Q26 margin is **up** y/y vs 4Q25's 28.29%) at 0.47, which sits between the two.
4. **`40_line_build.md` says the line build's FY27 incremental margin is "34.8%"; recomputed it is 34.97%** (and memo v3 repeats "24.7–34.8%"). A 0.17pp presentation difference on rounded inputs, not a modelling difference. Use 35.0%, or quote the band 24.7–35.0%.
5. **DEC-0003's identity form** — see §5.2. The decision's wording is correct forward and incomplete for a printed quarter.
6. **F03's README and R05's README print revision-1 numbers** that their own forecast JSONs have superseded (F03 0.08/0.17/0.27/0.38/0.10 → 0.02/0.04/0.10/0.36/0.48 under the LITERAL convention; R05 0.17 → 0.22). Memo v3 already uses 0.22 for R05; it does not yet use F03 rev 2, whose leading option is now **"no numeric FY27 margin guidance" at 0.48**. That materially softens any claim that February will print an investment-year guide: P(an explicit <35.5% or investment-year framing) is **0.36**, not "the leading outcome is a guide-down".
7. **Consistency with sibling lines.** C4's S&M (3Q26 LB $778.3M, FY27 LB $3,459.6M / 21.86%, Street-implied $3,328M) chains to this dossier exactly — my recompute returns $3,328.5M from the same residual construction. FY26 revenue $14,268.1M and FY27 $15,828.6M are R6/D3's path; 1H26 actuals are H0's panel under DEC-0003. C7 should take EBITDA from the `base (line build)` rows and D&A from the `da_musd` rows here, and note that adjusted EBITDA excludes $1,813.7M of FY26 SBC (35.6% of FY26 EBITDA).

## 8. Open choices

1. **Which FY27 margin the memo leads with — 35.7% (LB) or 34.6% (CC)?** This is memo v3's own open item and the judge's question. Options: **(a)** 35.66% (LB) as the point, 34.64% (CC) shown beside it as the run's view; **(b)** 34.64% as the point, because it is the object that was scored at h=0 and it widens the gap to the Street to 1.81pp; **(c)** the band 34.6–35.7% with no point. — **Recommendation: (a).** Why: DEC-0011 already put the line build in the workbook, so (b) would make the FY27 margin inconsistent with the S&M, cost-of-revenue and G&A lines the same memo prints; the CC's FY27 is an extrapolation of an object that *failed* its own h=2 test, so "it was backtested" is not true of the number in question; and (a) is the conservative choice for a short (the smaller gap to the Street), which DEC-0016 requires — we must not pick 34.6% because it is the bigger short. Present the CC beside it and say why it is lower: the mechanical residual allocation puts 76.6% of the line residual into S&M, which its own synthesis calls uncomfortable at G&A.
2. **Does the workbook's 3Q26 EBITDA read $2,420M or $2,399M?** Options: **(a)** $2,420M (LB) with the card's $2,399M as a reconciliation footnote; **(b)** $2,399M throughout, so the pitch's headline number is the backtested one; **(c)** both, as a two-row stub. — **Recommendation: (a) with an explicit $20.5M reconciliation row**, per DEC-0011. Why: the workbook must foot to its own cost lines; $20.5M is 0.43pp and $0.028 of EPS, small enough to footnote and too large to ignore. But the **beat probability and the band must stay on the CC object** — they were calibrated on it and on nothing else.
3. **Is 4Q26 quoted at 28.28% (ours) or 28.90% (the Street, which the h=1 rule adopted)?** Options: **(a)** 28.28% as the model's line, noting the combination has no h=1 edge; **(b)** 28.90%, following the pre-registered consequence; **(c)** 28.3–28.9% as a range. — **Recommendation: (a)**, with the pre-registered failure stated in the same sentence. Why: a short memo that quotes consensus as its own 4Q26 number has no 4Q26 view, and the line build *does* have one, built from parameters; but the honest label is "our line build says 28.3%, and we have no tested object that beats the Street at one quarter out".
4. **How is the FY26 floor presented — cushion or inequality?** Options: **(a)** "FY26 35.73% against a 35.5% floor, cushion +0.23pp, which breaks on a 0.63–0.94% 2H26 revenue miss"; **(b)** add that an unchanged "at least 35.5%" sentence is **the absence of a raise, not a guide-down** (WS31 audit 12), and that our own 28.90%/28.28% 4Q26 already satisfies it; **(c)** lead with the 5 Nov sentence forecast instead. — **Recommendation: (b).** Why: (a) alone invites the judge's obvious counter, and the C04 rev-2 vector (held 0.33, "≈36%" 0.30, softer 0.27) says the sentence itself is a three-way coin toss — so the cushion, not the sentence, is the tradeable statement. Whether "no raise" is a sell is a price-reaction question this build has **not** tested.
5. **Does the memo keep the "approximately 36%" sentence forecast and its 30.12% implied 4Q26?** Options: **(a)** keep both, labelled as M3's 2-of-2 rule with p ≈ 0.45–0.50; **(b)** keep the budget identity (1pp of FY26 = 4.49pp of 4Q26; 1pp of 3Q26 = −1.51pp of 4Q26) and drop the point forecast, deferring to C04 rev 2's 0.30; **(c)** drop both. — **Recommendation: (b).** Why: the identity is arithmetic and is the single most useful thing on the 5 Nov card; the point forecast rests on n = 2 and is now contradicted by a purpose-built Monte Carlo that puts "held at 35.5%" *ahead* of "≈36%" (0.33 vs 0.30). Quote the identity, quote C04's vector, and let the 30.12% be the conditional it is.
6. **Is the breaker column shown at 38.05% FY27?** Options: **(a)** yes, as the third P&L column; **(b)** replace it with a flip rule (3Q26 10-Q brand-and-performance marketing y/y below ~+20%); **(c)** both. — **Recommendation: (c)**, matching C4's §8.3. Why: 38.05% is above the Street's 36.45%, which makes the point a judge needs to see — *if the ramp pauses we are wrong by more than the Street is* — and B03's base rate (0 of the last 10 prints and 0 of 5 Novembers carried a forward moderation statement) is the strongest evidence we have that it will not.

## 9. Judge Q&A
1. Q: **Pick one FY27 margin.** A: **35.7%**, with 34.6% shown beside it. Both are ours and neither is a forecast: the 34.64% is the calibrated combination extrapolated to h≥2, where its own pre-registered test fails (1.026x the seasonal naive in W2), and the 35.66% is a bottom-up stack whose four discretionary lines have no backtest. We lead with 35.66% because DEC-0011 already put that cost stack in the workbook — every line of it traces to a 10-K or 10-Q parameter — and because it is the *smaller* short, which is the honest way round: we are not choosing the number that flatters the thesis. The difference between them is one line. Built from the FY25 10-K split (marketing +15%, field +11%), FY27 S&M is 21.86% of revenue; allocated as the run's residual it is 23.51%. That 1.65pp is $261M, and $158M is a point of FY27 margin.
2. Q: **What does the Street's 36.5% require?** A: Four things, and they are the same thing. On our revenue it is $5,769M of FY27 EBITDA — **$125M above our line build, $286M above the run**. It implies FY27 S&M of $3,334M on our other four cost lines, i.e. **+9.7% y/y**, against +13.8% in our build and 1H26's actual **+29.9%**. Mechanically, in the line build's own parameter space, it is **FY27 marketing growth of about +9% instead of +15%** with the other twenty-two parameters unchanged. And it is an **incremental margin of 43.7%** against our 35.0%, on a business whose S&M intercept is +17% growth a year at zero revenue growth and whose S&M does *not* decelerate when revenue does (k_up +1.83, k_dn −0.12, p 0.003, n 16). It also asks FY27 to print **above FY24's 36.40%**, the all-time peak, in the year after a brand ramp. None of that is impossible — management cut S&M growth by 12.7pp in the 2023 episode — but every part of it is a spending decision, and there is no forecastable mechanism behind it.
3. Q: **You say 3Q26 is $2,399M, but your model says $2,420M. Which is it?** A: Both, and the difference is $20.5M — 0.43pp of margin, $0.028 of EPS. $2,399M is `final-margin|combined_dollar_from_margin`, the only object in the build with a measured edge: h=0 MAE $30.7M (W1) / $25.8M (W2), 0.47x / 0.44x the Street's error, better than the Street in **14 of 14 and 10 of 10** quarters, sign p 0.0001 / 0.0010. That is the number the 5 Nov card quotes, with an 80% band of $2,337–2,462M and P(beat) 0.78. $2,420M is the line build, which foots to five cost lines you can audit against the 10-Q. They differ because the run *allocates* a residual to the cost lines while the build *constructs* them. Neither is the source of the beat: the beat is revenue. At the Street's own revenue our margin is worth $8M.
4. Q: **Is 50.4% in 3Q26 just management's sentence read back to you?** A: Partly, and we say so. "Adjusted EBITDA margin down slightly vs 3Q25" is treated as a cost **budget**, not a forecast: built from the 10-Q components alone, 3Q26 costs grow 11.5%, revenue grows 17%, and the quarter prints **52.39%** — so landing the sentence requires management to spend about **$97M more** than the evidence supports, which we allocate 70% to marketing and 30% to AI hosting because those are the two lines management itself flagged. We do it because the quarterly sentence has **not** been sandbagged: over W2 the realised gap to it averages −0.19pp and the print has been *above* it in only 4 of 10 quarters, so it reads as a real ceiling. The upside case is explicit — $2,517M / 52.39% — and R05 rev 2 puts P(margin ≥ 51.5%) at **0.22**. Our 49.94% combination sits 0.15pp under the 50.085% ceiling and the clip never binds.
5. Q: **Where does this break?** A: Three places, in order. **(i) 4Q26**, where we have no edge at all: the combination loses to the raw Street by 19–28% at one quarter out in both windows, so the pre-registered consequence forced us to quote the Street. Our own line build says 28.28% against a Street 28.90%, and the FY26 "at least 35.5%" floor breaks on a 2H26 revenue miss of only **0.63% if costs are held, 0.94% if they flex**. **(ii) The S&M ramp pausing** — the breaker column puts FY27 at 38.05%, *above* the Street, so if we are wrong we are wrong by more than consensus is; the defence is the base rate (0 of the last 10 prints and 0 of 5 November letters carried a forward moderation statement). **(iii) Selection.** The six-member pool was chosen after seeing the scoreboard; there is no untouched evaluation set anywhere in this build, and 5 November is the first genuinely out-of-sample observation. We have frozen the model at this vintage and pre-registered the pass line so that one observation counts.

## 10. Grade
Grade: B — everything reproduces (my receipt is exit 0 with 35 of 37 checks matching, the two exceptions being a stale tracked file and an incomplete identity wording, both documented; C4's `MARGIN_VERIFY_ONLY=1` receipt shows 24 of 24 CSVs identical to 1.6e-11 and the `40_line_build` re-run changed no EBITDA-bearing cell), and the 3Q26 h=0 object would stand on its own at A — but the line C6 is asked for runs to FY27, where the combination fails its pre-registered test in both directions (h=1 vs the Street, h=2 vs the naive) and the line build that supplies the adopted 35.66% has no backtest of any kind, so the object is reproduced but descriptive, which is exactly a B.
