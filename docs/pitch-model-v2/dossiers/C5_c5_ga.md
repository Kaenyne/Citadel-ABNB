# C5 — General & administrative, ex lodging-tax reserve

## 1. Header
- Line: C5 · Judge's question: "What drives this cost line, and what did the 10-Q say about it?"
- Digger: sonnet · Date: 2026-09-18 · Commit: 0b0961e (branch `theo/pitch-model-v2`; the brief named b098ac2, an ancestor — `git diff --stat b098ac2 0b0961e` on `analysis/src/margin_build/40_line_build`, `data/processed/margin_build/40_line_build` and `data/processed/margin_build/02_financial_panel` returns nothing, i.e. unchanged)

**One-paragraph answer.** G&A ex the lodging-tax reserve is the smallest and least-modelled of the five cost lines: two growth rates (2H26 +5%, FY27 +5%) applied to the prior-year actual half/year `ga_cash_ex_lodging`, spread on the 2023-25 quarterly G&A shares — no per-unit driver (nights, GBV, bookings, revenue) touches it at all. The 2H26 rate traces to a real, verified 10-Q sentence: the 2Q26 10-Q says G&A rose "$4 million, or 1%" in 1H26 because a "$38 million increase in payroll-related expenses driven by higher average headcount" was "largely offset by a $38 million decrease in non-income taxes" (quarter alone: +$32M payroll / −$28M non-income taxes), and the base case reads the one-off tax relief as non-repeating so 2H26 growth (+5%) runs above the 1H26 print (−5.4%). The FY27 rate (+5%) has no 10-Q source at all — it is carried from an internal note (31b) — and the management "extremely disciplined" language `40_params.csv` cites for it is **misattributed**: the only such quote in the repo's call-transcript ledger is Ellie Mertz on the **3Q24** call, about **total** EBITDA margin expansion since 2020, not G&A and not 2Q26 (§4/§7). At the guide midpoint this puts 3Q26 at $265.4M (5.5% of revenue) and FY27 at $1,044.5M (6.6% of revenue), of which $0 is a lodging-reserve add-back in every published scenario (the 4Q25 $81M reserve is treated as a one-off, not a run rate). Structurally this line is unlike every other line C1–C4 cover: it receives **none** of the 3Q26 evidence-vs-sentence reconciliation gap (that's 70% marketing / 30% hosting), so its dollars are byte-identical between `base`, `evidence_only` and the short case — the only lever in this whole build is the two growth-rate judgment calls. And of the five cost lines in the margin build, G&A is the **one line with no measured forecasting skill at all**: re-scored against the honest drift-naive baseline (the discussion-group re-score, 14 Sep 2026, which supersedes the run's own headline claim), its ratio is 1.018 (W1) / 1.098 (W2) in one independent model and 1.001 (W1) / 1.055 (W2) in another — statistically indistinguishable from a coin flip (p 0.66–0.99) in both windows, both models.

## 2. The number

**Sources.** All rows come from the bottom-up line build (`40_line_build`, 15 Sep 2026 build note; every parameter in `40_params.csv` carries a named source) per DEC-0011, which the brief binds as the workbook's cost stack for this batch, and DEC-0003, which binds the history basis to `ga_cash_ex_lodging` (GAAP G&A less SBC, ex the lodging/withholding/transactional-tax reserve). `base` = `40_lines_quarterly.csv` / `40_annual.csv` scenario `base`. `short` = `40_short_case_quarterly.csv` scenario `short_costs_at_budget` — **G&A dollars in the short case are identical to base to the last cent** (verified below): the short-case overlays (`rnpl_ops_uplift_pct`, `chargeback_add_per_booking`, `rnpl_share_shift_pts`) touch ops & support, cost of revenue and interest income, never G&A, and G&A is spending-decision dollars, not a function of the short case's lower nights/GBV/revenue path — only `ga_pct_rev` moves, because the denominator (short revenue) is lower. `breaker` = `40_line_build`'s own documented favourable **cost column** (`cost_bull`: `ga_growth_2h26` 2.0% vs 5.0% base, `ga_growth_fy27` 3.0% vs 5.0% base) on the base revenue path.

### G&A ex lodging reserve, in USD m

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base | 3Q26 | 265.39 | — | — | USD m | 2026-09-11 data / 2026-09-15 build |
| base | 4Q26 | 276.41 | — | — | USD m | 2026-09-11 / 15 |
| base | 1Q27 | 249.23 | — | — | USD m | 2026-09-11 / 15 |
| base | 2Q27 | 271.58 | — | — | USD m | 2026-09-11 / 15 |
| base | 3Q27 | 256.54 | — | — | USD m | 2026-09-11 / 15 |
| base | 4Q27 | 267.19 | — | — | USD m | 2026-09-11 / 15 |
| base | FY26 | 995.80 | — | — | USD m | 2026-09-11 / 15 |
| base | FY27 | 1,044.54 | — | — | USD m | 2026-09-11 / 15 |
| short | 3Q26 | 265.39 | — | — | USD m | 2026-09-15 |
| short | 4Q26 | 276.41 | — | — | USD m | 2026-09-15 |
| short | 1Q27 | 249.23 | — | — | USD m | 2026-09-15 |
| short | 2Q27 | 271.58 | — | — | USD m | 2026-09-15 |
| short | 3Q27 | 256.54 | — | — | USD m | 2026-09-15 |
| short | 4Q27 | 267.19 | — | — | USD m | 2026-09-15 |
| short | FY26 | 995.80 | — | — | USD m | 2026-09-15 |
| short | FY27 | 1,044.54 | — | — | USD m | 2026-09-15 |
| breaker (cost_bull) | 3Q26 | 257.81 | 240.68 | 272.97 | USD m | 2026-09-15 |
| breaker (cost_bull) | 4Q26 | 268.51 | 249.23 | 284.31 | USD m | 2026-09-15 |
| breaker (cost_bull) | 1Q27 | 240.68 | — | — | USD m | 2026-09-15 |
| breaker (cost_bull) | 2Q27 | 262.26 | — | — | USD m | 2026-09-15 |
| breaker (cost_bull) | 3Q27 | 247.74 | — | — | USD m | 2026-09-15 |
| breaker (cost_bull) | 4Q27 | 258.03 | — | — | USD m | 2026-09-15 |
| breaker (cost_bull) | FY26 | 980.32 | — | — | USD m | 2026-09-15 |
| breaker (cost_bull) | FY27 | 1,008.70 | — | — | USD m | 2026-09-15 |
| *cost_bear (context, not one of the three required scenarios)* | 3Q26 | 272.97 | | | USD m | 2026-09-15 |
| *cost_bear* | FY27 | 1,091.10 | | | USD m | 2026-09-15 |
| *memory: actual* | 4Q23 | $211M ex-reserve / $1,203M GAAP | | | | 2026-09-18 (H0, DEC-0003) |
| *memory: actual* | 3Q25 $257M | 4Q25 $259M | FY25 $995M | 1H26 $453M (1Q26 $226M / 2Q26 $227M) | | 2026-09-18 (H0) |

`low`/`high` for `base`/`short` are left blank for the same reason C1/C4 leave them blank: G&A's base case has no published alternate bound of its own (its `evidence_only` row is identical to `base` — see §3 — so it is not a separate bound either). `low`/`high` for `breaker` at 3Q26/4Q26 are the `cost_bear` and `base` rows that bracket `cost_bull` in `40_lines_quarterly.csv` (dollar bounds, not a formal confidence interval); FY26/FY27 `low`/`high` are omitted because `cost_bear` (the true adverse column) sits *above*, not below, `base` and `cost_bull` — G&A only has one economically meaningful direction of surprise risk (spend runs hotter than budgeted), so a symmetric low/high band around `breaker` would misstate the shape.

**The number that answers the judge.** At $4,804.0M of 3Q26 base revenue, **$8.1M of G&A ($265.4M breaker vs $273.0M cost_bear at 3Q26) is 0.17pp of margin** — the smallest single-line sensitivity in the entire build (`40_sensitivities.csv`: `ga_growth_2h26` +3pts moves FY27 margin −0.19pp / −$0.04 EPS, tied with `pd_growth_fy27`/`pd_ai_tooling_fy27` for the smallest of nine cost-parameter sensitivities reported). G&A's FY27 share of revenue falls from 6.98% (FY26) to 6.60% (FY27) purely from revenue growing faster than a flat 5% G&A growth rate — there is no operating-leverage *claim* being made here, just arithmetic.

### 2a. Model inputs (machine-readable)

Per DEC-0011 the workbook's cost stack is `40_line_build` and per DEC-0003 "G&A" means `ga_cash_ex_lodging`. `ga_pct_rev` is G&A over each scenario's own revenue path (short's own lower revenue, base/breaker's own base revenue). `lodging_reserve_musd` is `40_params.csv`'s `lodging_reserves_fwd`, which is 0.0 in base, bear and bull alike — no forecast period carries a reserve or a release — shown explicitly below so the choice is on record rather than silently assumed. The two history rows put DEC-0003's reconciling line (the $931M 4Q23 lodging/withholding/transactional-tax reserve) on record per the brief's requirement.

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| ga_musd | base (line build) | 3Q26 | 265.39 | USD m | 40_lines_quarterly.csv ga_cash_ex_lodging, scenario base; params ga_growth_2h26 5.0% (2Q26 10-Q: "$4 million, or 1%" G&A increase in 1H26, "$38 million increase in payroll-related expenses ... largely offset by a $38 million decrease in non-income taxes"; base assumes the tax offset does not repeat in 2H26) |
| ga_musd | base (line build) | 4Q26 | 276.41 | USD m | 40_lines_quarterly.csv ga_cash_ex_lodging, scenario base; same params |
| ga_musd | base (line build) | 1Q27 | 249.23 | USD m | 40_lines_quarterly.csv ga_cash_ex_lodging, scenario base; param ga_growth_fy27 5.0% (no 10-Q source; carried from internal note 31b, see §4 sourcing caveat) |
| ga_musd | base (line build) | 2Q27 | 271.58 | USD m | 40_lines_quarterly.csv ga_cash_ex_lodging, scenario base; ga_growth_fy27 5.0% |
| ga_musd | base (line build) | 3Q27 | 256.54 | USD m | 40_lines_quarterly.csv ga_cash_ex_lodging, scenario base; ga_growth_fy27 5.0% |
| ga_musd | base (line build) | 4Q27 | 267.19 | USD m | 40_lines_quarterly.csv ga_cash_ex_lodging, scenario base; ga_growth_fy27 5.0% |
| ga_musd | base (line build) | FY26 | 995.80 | USD m | 40_annual.csv ga_cash, FY26 base = 1H26 actual 1Q26 $229M + 2Q26 $225M (panel ga_cash, GAAP-basis, carries the tiny 1H26 net reserve/release) + 3Q26/4Q26 build (ex-lodging, lodging_reserves_fwd 0.0) |
| ga_musd | base (line build) | FY27 | 1044.54 | USD m | 40_annual.csv ga_cash, FY27 base = sum of the four FY27 quarters above |
| ga_musd | short | 3Q26 | 265.39 | USD m | 40_short_case_quarterly.csv, scenario short_costs_at_budget; identical to base — the short case never overrides a ga_* parameter and routes none of the reconciliation gap here (verified in my recompute to < 1e-6 USD m, receipt below) |
| ga_musd | short | 4Q26 | 276.41 | USD m | 40_short_case_quarterly.csv, scenario short_costs_at_budget; identical to base |
| ga_musd | short | 1Q27 | 249.23 | USD m | 40_short_case_quarterly.csv, scenario short_costs_at_budget; identical to base |
| ga_musd | short | 2Q27 | 271.58 | USD m | 40_short_case_quarterly.csv, scenario short_costs_at_budget; identical to base |
| ga_musd | short | 3Q27 | 256.54 | USD m | 40_short_case_quarterly.csv, scenario short_costs_at_budget; identical to base |
| ga_musd | short | 4Q27 | 267.19 | USD m | 40_short_case_quarterly.csv, scenario short_costs_at_budget; identical to base |
| ga_musd | short | FY26 | 995.80 | USD m | not a published 40_annual.csv row (short has no annual row); my recompute (c5_ga_scenarios.csv) = same 1H26 actual + short-case 3Q26/4Q26 G&A dollars (identical to base) |
| ga_musd | short | FY27 | 1044.54 | USD m | my recompute; sum of the four short-case FY27 G&A quarters (identical to base) |
| ga_musd | breaker (cost_bull) | 3Q26 | 257.81 | USD m | 40_lines_quarterly.csv ga_cash_ex_lodging, scenario cost_bull; ga_growth_2h26 2.0% bull (same 10-Q-sourced parameter, favourable column) |
| ga_musd | breaker (cost_bull) | 4Q26 | 268.51 | USD m | 40_lines_quarterly.csv ga_cash_ex_lodging, scenario cost_bull |
| ga_musd | breaker (cost_bull) | 1Q27 | 240.68 | USD m | 40_lines_quarterly.csv ga_cash_ex_lodging, scenario cost_bull; ga_growth_fy27 3.0% bull |
| ga_musd | breaker (cost_bull) | 2Q27 | 262.26 | USD m | 40_lines_quarterly.csv ga_cash_ex_lodging, scenario cost_bull |
| ga_musd | breaker (cost_bull) | 3Q27 | 247.74 | USD m | 40_lines_quarterly.csv ga_cash_ex_lodging, scenario cost_bull |
| ga_musd | breaker (cost_bull) | 4Q27 | 258.03 | USD m | 40_lines_quarterly.csv ga_cash_ex_lodging, scenario cost_bull |
| ga_musd | breaker (cost_bull) | FY26 | 980.32 | USD m | 40_annual.csv ga_cash, FY26 cost_bull |
| ga_musd | breaker (cost_bull) | FY27 | 1008.70 | USD m | 40_annual.csv ga_cash, FY27 cost_bull |
| ga_pct_rev | base (line build) | 3Q26 | 5.52 | pct | on revenue 4804.04 |
| ga_pct_rev | base (line build) | 4Q26 | 8.70 | pct | on revenue 3178.11 |
| ga_pct_rev | base (line build) | 1Q27 | 8.16 | pct | on revenue 3053.13 |
| ga_pct_rev | base (line build) | 2Q27 | 6.74 | pct | on revenue 4028.98 |
| ga_pct_rev | base (line build) | 3Q27 | 4.86 | pct | on revenue 5280.73 |
| ga_pct_rev | base (line build) | 4Q27 | 7.71 | pct | on revenue 3465.76 |
| ga_pct_rev | base (line build) | FY26 | 6.98 | pct | on revenue 14268.14 |
| ga_pct_rev | base (line build) | FY27 | 6.60 | pct | on revenue 15828.61 |
| ga_pct_rev | short | 3Q26 | 5.67 | pct | on short revenue 4680.90 (nights-lap + RNPL revenue override) |
| ga_pct_rev | short | 4Q26 | 9.32 | pct | on short revenue 2965.87 |
| ga_pct_rev | short | 1Q27 | 8.79 | pct | on short revenue 2835.53 |
| ga_pct_rev | short | 2Q27 | 7.22 | pct | on short revenue 3762.97 |
| ga_pct_rev | short | 3Q27 | 5.14 | pct | on short revenue 4988.17 |
| ga_pct_rev | short | 4Q27 | 8.03 | pct | on short revenue 3326.83 |
| ga_pct_rev | short | FY26 | 7.15 | pct | on short-case FY26 revenue 13932.77 (1H26 actual + short 3Q26/4Q26) |
| ga_pct_rev | short | FY27 | 7.00 | pct | on short-case FY27 revenue 14913.51 |
| ga_pct_rev | breaker (cost_bull) | 3Q26 | 5.37 | pct | base revenue path 4804.04 |
| ga_pct_rev | breaker (cost_bull) | 4Q26 | 8.45 | pct | base revenue path 3178.11 |
| ga_pct_rev | breaker (cost_bull) | 1Q27 | 7.88 | pct | base revenue path 3053.13 |
| ga_pct_rev | breaker (cost_bull) | 2Q27 | 6.51 | pct | base revenue path 4028.98 |
| ga_pct_rev | breaker (cost_bull) | 3Q27 | 4.69 | pct | base revenue path 5280.73 |
| ga_pct_rev | breaker (cost_bull) | 4Q27 | 7.45 | pct | base revenue path 3465.76 |
| ga_pct_rev | breaker (cost_bull) | FY26 | 6.87 | pct | base revenue path 14268.14 |
| ga_pct_rev | breaker (cost_bull) | FY27 | 6.37 | pct | base revenue path 15828.61 |
| lodging_reserve_musd | base (line build) | 3Q26 | 0.00 | USD m | 40_params.csv lodging_reserves_fwd = 0.0 (base, bear and bull all 0.0); "None assumed; 4Q25's $81M was a one-off" (FY25 10-K / 4Q25 letter) |
| lodging_reserve_musd | base (line build) | 4Q26 | 0.00 | USD m | same |
| lodging_reserve_musd | base (line build) | 1Q27 | 0.00 | USD m | same |
| lodging_reserve_musd | base (line build) | 2Q27 | 0.00 | USD m | same |
| lodging_reserve_musd | base (line build) | 3Q27 | 0.00 | USD m | same |
| lodging_reserve_musd | base (line build) | 4Q27 | 0.00 | USD m | same |
| lodging_reserve_musd | base (line build) | FY26 | 0.00 | USD m | same; the only non-zero lodging reserve inside FY26 is the actual, already-printed 1H26 net figure ($3M 1Q26 + −$2M 2Q26 release, panel `lodging_tax_reserves`), which is part of the FY26 actual leg, not a forecast assumption |
| lodging_reserve_musd | base (line build) | FY27 | 0.00 | USD m | same |
| ga_cash_ex_lodging_musd | actual | 4Q23 | 211.00 | USD m | 02_panel_quarterly.csv ga_cash_ex_lodging; DEC-0003 basis (GAAP G&A $1,203M less SBC $61M less the $931M lodging/withholding/transactional-tax reserve = $211M cash G&A); FY23 10-K |
| ga_gaap_musd | actual | 4Q23 | 1203.00 | USD m | 02_panel_quarterly.csv ga_gaap; FY23 10-K, GAAP general and administrative expense as reported (includes the $61M SBC allocated to G&A and the $931M lodging/withholding/transactional-tax reserve) |

## 3. Derivation chain
1. 2Q26 10-Q MD&A, "General and Administrative" (§ Results of Operations): "General and administrative expense increased by $4 million, or 1% [1H26 y/y] ... primarily due to a $38 million increase in payroll-related expenses driven by higher average headcount, and a $4 million increase in various fees and penalties, largely offset by a $38 million decrease in non-income taxes" (three-months figure: +$32M payroll / −$28M non-income taxes); FY24/FY25 10-K G&A levels; FY23 10-K lodging/withholding/transactional-tax reserve ($931M, 4Q23) →
2. `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv` — columns `ga_gaap`, `sbc_ga`, `ga_cash` (= `ga_gaap` − `sbc_ga`), `lodging_tax_reserves`, `ga_cash_ex_lodging` (= `ga_cash` − `lodging_tax_reserves`), DEC-0003 basis, all 14 quarters 1Q23–2Q26 →
3. `analysis/src/margin_build/40_line_build/run.py` — parameters `ga_growth_2h26`, `ga_growth_fy27`, `lodging_reserves_fwd` (`40_params.csv`); formula `ga_2h26 = (ga_cash_ex_lodging[3Q25]+ga_cash_ex_lodging[4Q25]) × (1+ga_growth_2h26/100)`, `ga_fy27 = (ga_cash_ex_lodging[1Q26]+ga_cash_ex_lodging[2Q26]+ga_2h26) × (1+ga_growth_fy27/100)`, spread on `SHARE["ga"]` (2023-25 mean quarterly shares: Q1 23.86% / Q2 26.00% / Q3 24.56% / Q4 25.58%, from WS02 `02_seasonality.csv`) →
4. `data/processed/margin_build/40_line_build/40_lines_quarterly.csv` (columns `ga_cash_ex_lodging`, `lodging_reserves`, `ga_cash`, `ga_cash_pct_rev`), `40_annual.csv`, `40_short_case_quarterly.csv` — cross-checked by my own independent recompute, `data/processed/pitch_model_v2/receipts/C5/c5_ga_recompute.py` → `c5_ga_scenarios.csv` / `c5_ga_line_recompute_check.csv` / `c5_ga_history_basis_check.csv`.

## 4. Governing sources
| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-09-15 | `40_line_build.md` / `40_params.csv` | ga_growth_2h26 5.0% (bear 8.0 / bull 2.0), ga_growth_fy27 5.0% (bear 8.0 / bull 3.0), lodging_reserves_fwd 0.0; G&A ex reserves FY25 8.1% → FY26E 7.0% → FY27E 6.6% of revenue | **governs** — reproduced byte-identical this batch (C1's receipt, `data/processed/pitch_model_v2/receipts/C1/receipt.json`, commit 11b3d39, exit 0, `40_line_build`/`40_annual`/`40_lines_quarterly` unchanged) |
| 2026-09-18 | `DECISIONS.md` DEC-0003 | history G&A basis is `ga_cash_ex_lodging`; the ~$931M 4Q23 lodging-tax reserve sits in a reconciling line, not in "G&A" | **governs** |
| 2026-09-18 | `DECISIONS.md` DEC-0011 | cost stack for composition is `40_line_build`; management's 3Q26 margin sentence is treated as a budget (the reconciliation step) | **governs** — but note the reconciliation step routes 70% to marketing and 30% to hosting, **0% to G&A**; G&A is unaffected by DEC-0011's budget mechanism, unlike C1 (cost of revenue) and C4 (S&M) |
| 2026-09-13/14 | `M1_driver_lines.md` §1.1 / §4c (pre-registered per-line test) | "every line but G&A beats the seasonal naive by 20-70% [at h=0]"; G&A eq-weighted ratio 0.778 (W1) / 0.954 (W2) beats seasonal_naive, rw-weighted 1.101 (W1) / 1.176 (W2) does not | **superseded in part** by the same file's same-day discussion response (below) for the "every line but G&A" framing on `total_cash_costs`, but the per-line G&A numbers themselves stand — see §6 |
| 2026-09-14 | `M1_driver_lines.md` §D4 (discussion response, WS22, R14 — re-scored vs the honest drift-naive baseline) | G&A ex reserves ratio vs drift: 1.018 (W1, t +0.09, p 0.93, 8/14 quarters better), 1.098 (W2, t +0.45, p 0.66, better count n/a) — **no measured skill in either window** | **governs** — this is the later, harsher, same-day re-score; supersedes the framing (not the raw numbers) of §1.1/§4c |
| 2026-09-14 | `M6_cycle_flex.md` §7 (pre-registered `lines_v2` test) | G&A `l0_rw` survives eq-weighting (ratio 0.766 W1 / 0.916 W2, both <1) but fails rw-weighting (1.091 W1 / 1.161 W2, both >1) against seasonal_naive; "**G&A and ops & support fail the both-windows/both-weightings bar** as individual lines" | **governs** |
| 2026-09-14 | `M6_cycle_flex.md` §D4 (discussion response, same R14 drift re-score) | G&A ratio vs drift: 1.001 (W1, t +0.01, p 0.99, 9/14), 1.055 (W2, t +0.28, p 0.78, 6/10) — "**k_ga = −0.110 ... not significant; treat ga as held**" | **governs** — the later, harsher, same-day re-score; independently confirms M1's finding with a different model |
| n/a (`analysis/src/overnight/31a_mgmt_margin_statements.py`, statement S098) | call transcript ledger | `40_params.csv`'s `'extremely disciplined' (2Q26)` citation for `ga_growth_2h26`/`ga_growth_fy27` | **mis-sourced, flagged not corrected** (rule 2 forbids editing the package) — the only "extremely disciplined" statement in the repo's own transcript ledger is tagged `call:3Q24`, speaker Ellie Mertz, quote "We've been extremely disciplined in terms of delivering over 400 basis points of EBITDA margin expansion since 2020" — about **total** EBITDA margin, not G&A, and **3Q24**, not 2Q26. The two 10-Q dollar deltas in the same param note ($38M payroll / $38M non-income taxes) are independently verified against `abnb-20260630.htm` (§3) and are correct |

The later, more-audited object always wins here: the M1/M6 discussion-group re-scores (14 Sep, same day as the original notes, response to red-team item R14) are the governing test-record numbers in §6, not the pre-registration's own framing.

## 5. Reproduction receipt
- Receipt (package run, cited not reproduced by me — hard constraint forbids re-running `40_line_build`): `data/processed/pitch_model_v2/receipts/C1/receipt.json` — command `python3 analysis/src/margin_build/40_line_build/run.py`, commit 11b3d398bcc12c74597855084420e81aa5a1631e, exit 0, wall 0.7s, `restored: true`; only `40_sensitivities.csv` (a documented tie-order artefact, not G&A-related) and the `.xlsx` changed and were restored.
- Receipt (my own scratch recompute): `data/processed/pitch_model_v2/receipts/C5/receipt.json`
- Command: `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id C5 --watch data/processed/margin_build/40_line_build --cmd "python3 data/processed/pitch_model_v2/receipts/C5/c5_ga_recompute.py"` · Exit: 0 · Wall: 0.2s · Interpreter: python3 (3.13.0, pandas 3.0.0) · `restored: true`, `changed: []`, `new_files: []` (the recompute script writes only into its own receipt folder, outside the watched package, so the watch confirms zero side effects on `40_line_build`)
- Output: `data/processed/pitch_model_v2/receipts/C5/c5_ga_line_recompute_check.csv`, all 28 cells (6 quarters × {base, cost_bull, cost_bear} vs `40_lines_quarterly.csv`, 6 quarters short-case identity vs `40_short_case_quarterly.csv`, 6 FY26/FY27 cells vs `40_annual.csv`) · Committed value vs my independent re-implementation of the two-parameter G&A chain from `40_params.csv`: **max |diff| = 1.14e-13 USD m** · Tolerance: 1e-6 USD m · **Match: yes**
- This independently re-implements the entire G&A chain (`ga_2h26`, `ga_fy27`, the `SHARE["ga"]` quarterly spread, the FY26/FY27 annual roll-up) from the committed parameter sheet and panel actuals, and separately confirms — by direct comparison of `40_short_case_quarterly.csv` against `40_lines_quarterly.csv`'s `base` scenario — that G&A dollars in the short case are bit-identical to base for all six quarters, which is not stated anywhere in the source notes and had to be verified by inspection.

## 6. Test record
The panel column is `ga_cash_ex_reserves_musd` (`M1_driver_lines`) / `ga_cash_ex_lodging` (`40_line_build`, same series). Two independent driver-model objects have been scored against it (`M1_driver_lines`'s `b_elastic_rw` — a y/y trend, no driver — and `M6_cycle_flex`'s `l0_rw` — a revenue-elasticity `k_ga`); the line build's own two-parameter judgment-rate formula (the object quoted in §2) has never itself been scored — it is descriptive, not backtested. All rows PIT, h=0 unless noted.

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W1 | 14 | `ga_cash_ex_reserves_musd`, M1 `b_elastic_rw`, vs seasonal_naive (eq/rw) | MAE $16.0M, MAPE 7.0% | ratio 0.778 (eq) / **1.101** (rw) | n/a | not published for lines | M1 §P per-line expectation: "ga does NOT beat pct_rev_last4 materially" | **eq: beats (unexpectedly); rw: FAILS** |
| W2 | 10 | same | MAE $18.9M, MAPE 8.1% | 0.954 (eq) / **1.176** (rw) | — | — | same | **eq: beats; rw: FAILS** |
| W1 | 14 | same, vs pct_rev_last4 (eq/rw) | — | 0.403 (eq) / 0.546 (rw) | — | — | expectation: does not beat materially | beats both weightings (expectation **WRONG** — a y/y trend captures growth+seasonality a revenue-share rule misses) |
| W2 | 10 | same | — | 0.464 (eq) / 0.576 (rw) | — | — | same | beats both weightings |
| W1 | 14 | `ga_cash_ex_reserves_musd`, M6 `l0_rw` (`k_ga` = −0.110, t −0.29, **not significant**), vs seasonal_naive | MAE $15.8M | ratio 0.766 (eq) / **1.091** (rw); survives eq **True**, rw **False** | — | — | M6: beat seasonal_naive, both windows, both weightings | **rw FAILS** |
| W2 | 10 | same | MAE $18.1M | 0.916 (eq) / **1.161** (rw); survives eq **True**, rw **False** | — | — | same | **rw FAILS** |
| W1 | 14 | `ga_cash_ex_reserves_musd`, M1 `b_elastic_rw`, re-scored vs **drift** (harsher; discussion-group R14, 14 Sep, governs) | ratio **1.018** | t +0.09, p **0.93**, 8 of 14 quarters better | — | — | — | **FAILS (worse than drift, no skill)** |
| W2 | 10 | same | ratio **1.098** | t +0.45, p **0.66** | — | — | — | **FAILS** |
| W1 | 14 | `ga_cash_ex_reserves_musd`, M6 `k_ga`, re-scored vs **drift** (R14, governs) | ratio **1.001** | t +0.01, p **0.99**, 9 of 14 better | — | — | — | **FAILS (zero skill)** |
| W2 | 10 | same | ratio **1.055** | t +0.28, p **0.78**, 6 of 10 better | — | — | — | **FAILS** |
| — | 2 | `40_line_build`'s own two-parameter formula, backcast | not run — no FY25/1H26 backcast row exists for G&A in `40_backcast.csv` (only cost of revenue and ops & support are backcast there) | — | — | — | none written | **no test exists at all for this exact object** |
| W1/W2 | 14/10 | `total_cash_costs_musd` (all five lines, for context) vs drift | 1.164 / 1.170 (M6) / 1.165 / 1.170 (M1) | worse than drift, both windows | — | — | — | **FAIL** (M1/M6 D4) |

**Strongest known failure:** of the five cost lines in the entire margin build, G&A is the **only one with zero measured forecasting skill against the honest baseline in every test that exists** — not "descriptive because untested" like C1's exact formula, but actively tested and failing: two independent models (M1's y/y trend, M6's revenue-elasticity) each re-scored against drift-naive on the same 14/10 quarters both land at a ratio of essentially 1.00–1.10 with p-values of 0.66–0.99, i.e. statistically indistinguishable from a coin flip, in both windows, in both models. (It beats the recency-weighted seasonal-naive baseline in neither model in either window, and beats the weak equal-weighted seasonal-naive and pct_rev_last4 baselines only because those are undemanding baselines for a growing dollar line, per M1's own correction of its pre-registered expectation.) The two growth-rate assumptions that actually drive the $2,040M of FY26+FY27 G&A ($995.8M + $1,044.5M) are therefore judgment calls with a real, correctly-quoted 10-Q anchor for one half of one of them (2H26 payroll/non-income-tax deltas) and an internally-recycled, unsourced number for the other three-quarters of the assumption set (FY27 growth, and the "extremely disciplined" framing behind it, which is mis-cited — see §4/§7).

## 7. Kill list and consistency
- Kill-list check: none of `AGENT_BRIEF.md` §6's kill-list items (the −3.4pp FX step, "82% of Q4 FX already determined," "+4.05% fee uplift," the 9/9 drift rule, "half of ADR growth is bigger units," any FY27 level edge without its band, restated unearned fees, the 1.71M quote panel, "nothing beats guide × cushion," mixed-vintage consensus, M5's hierarchical cushion model, the 120-market panel, the Stan state space) touch G&A; none are quoted here.
- Conflicts / corrections:
  1. **`40_params.csv`'s `'extremely disciplined' (2Q26)` citation is mis-sourced** (§4). This is not a kill-list item (nobody has withdrawn it as a number — it drives no dollar directly, only rhetorical framing for the FY27 growth-rate judgment call), but it should not be repeated in the memo as a 2Q26 G&A-specific management statement. The correctly-sourced 2Q26 10-Q dollar deltas ($32M/$28M quarter, $38M/$38M half) are independently re-verified against the filing text in this repo (`docs/pitch-forecasts/questions/bonus-insider-selling/sources/tenq/abnb-20260630.htm`) and stand.
  2. **`M1_driver_lines.md` §1.1's "every line but G&A beats the seasonal naive by 20-70%"** is technically imprecise even before the drift re-score: G&A *does* beat seasonal_naive under equal weighting in both windows (0.778/0.954) — it is specifically the recency-weighted comparison (1.101/1.176) that fails. The same file's own §4d later states this more precisely ("G&A does not [beat the seasonal naive]" citing "0.78-1.18," conflating the two weightings). I use the disaggregated eq/rw numbers in §6 rather than either summary sentence.
  3. No conflict with C1/C4: those dossiers' reconciliation-step framing (70% marketing / 30% hosting) is consistent with this dossier's finding that G&A receives 0% of the gap and is therefore untouched by DEC-0011's budget mechanism.

## 8. Open choices
1. **The FY27 G&A growth rate (5.0% base / 8.0% bear / 3.0% bull) has no 10-Q source — only an internal note (31b) and a mis-cited management quote.** Options: (a) keep 5.0% as a bare judgment call, footnoted as unsourced; (b) anchor it to the 1H26 realised print (−5.4% y/y, i.e., materially lower) on the theory that the tax relief is more likely to partially persist than management's language suggests; (c) anchor it to the FY24→FY25 realised G&A growth rate (10.67%→10.96% of revenue per the WS10 census, i.e., roughly flat-to-up as a share, implying a higher $ growth rate than 5%). Recommendation: (a), with the footnote — because DEC-0016 (no leaning) forbids picking a number to fit a target, and none of (b)/(c) has a materially stronger evidentiary basis than the status quo; the honest answer is that this parameter is unmeasured, not that a different unmeasured number is better.
2. **Which baseline the memo should quote G&A's test performance against.** Options: (a) the pre-registered per-line expectation ("does not beat pct_rev_last4 materially" — WRONG, it does); (b) the seasonal_naive both-windows-both-weightings bar (mixed: eq passes, rw fails); (c) the drift-naive re-score (fails cleanly, both windows, both models, p 0.66–0.99). Recommendation: (c) for the memo and the judge Q&A, because it is the latest, most-audited, and least generous test, and because §6 shows it is the one where G&A is unambiguously the weakest of the five lines — DEC-0016's "no leaning" principle argues for quoting the harshest available honest test, not the most flattering one.
3. **Whether to flag the `'extremely disciplined' (2Q26)` mis-citation as a fix request to the `40_line_build` owner.** Options: (a) flag only, as done here (rule 2 forbids editing the package myself); (b) also file it against `docs/margin-build/audit/CODEX_LINE_BUILD_CHECK.md`'s pattern (a Codex-style finding) for the next audit pass. Recommendation: (b) — it is a small, mechanically checkable citation error (wrong quarter, wrong speaker context) of exactly the kind that audit's methodology already catches for other lines, and it currently sits in a live parameter's source note where a reader could mistake it for G&A-specific evidence of managed spend.

## 9. Judge Q&A
1. Q: What drives this cost line, and what did the 10-Q say about it? A: Two growth rates, not a driver — 2H26 G&A grows 5% off the 2H25 base, FY27 grows 5% off the FY26 base, both spread on 2023-25 seasonal shares; no per-unit cost (nights, bookings, GBV, revenue) touches it. The 2H26 rate's real anchor is the 2Q26 10-Q: G&A rose only "$4 million, or 1%" in 1H26 because a "$38 million increase in payroll-related expenses driven by higher average headcount" was "largely offset by a $38 million decrease in non-income taxes" — the base case assumes that tax relief does not repeat, so 2H26 growth (+5%) runs above the 1H26 print (−5.4%). The FY27 rate has no 10-Q source at all.
2. Q: Is G&A's forecast actually validated by any backtest? A: No, and it is the weakest of the five cost lines on this exact point. The line build's own two-parameter formula has never been scored (no FY25/1H26 backcast exists for it, unlike cost of revenue and ops & support). Two separate, independently-built driver models that were tested (`M1_driver_lines`, `M6_cycle_flex`) both re-score G&A against the honest drift-naive baseline at a ratio of essentially 1.00–1.10 with p-values of 0.66–0.99 in both pre-registered windows — statistically zero measured skill, in both models, in both windows. It beats a weak seasonal-naive baseline only under equal weighting, and fails it under recency weighting, in both models.
3. Q: Does management's cost discipline ("extremely disciplined") support the 5%/5% G&A growth assumption? A: The specific quote `40_params.csv` cites for this is mis-sourced — the only "extremely disciplined" statement in this repo's transcript ledger is Ellie Mertz on the 3Q24 call, about total EBITDA margin expansion since 2020, not G&A and not 2Q26. What *is* correctly sourced is the 2Q26 10-Q's payroll/non-income-tax dollar bridge (question 1); the qualitative "management is disciplined on G&A" framing is not independently verified beyond that one filing sentence and should not be over-weighted in the memo.

## 10. Grade
Grade: B — the receipt shows exit 0 and an exact match (my independent recompute of the full G&A chain from `40_params.csv` and the panel matches all 28 committed cells to 1.14e-13 USD m, and I additionally verified — a fact not stated in any source note — that the short case's G&A dollars are bit-identical to base), but the object does not survive both W1 and W2: two independent, previously-scored driver models both show G&A has zero measured skill against the honest drift-naive baseline in either window (p 0.66–0.99), and the line build's own two-parameter formula has never been backtested at all. This is the same category as C1 and C4 (exact reproduction, descriptive/non-predictive object) — not A because no version of this line clears both windows anywhere in the repo, and not C because the reproduction itself is clean, exact, and independently verified rather than merely asserted.
