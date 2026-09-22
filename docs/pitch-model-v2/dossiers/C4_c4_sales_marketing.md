# C4 — Sales and marketing, the swing line

## 1. Header
- Line: C4 · Judge's question: "Why is S&M the whole FY27 disagreement, and what if management just cuts it?"
- Digger: opus · Date: 2026-09-18 · Commit: e39d9e4 (branch `theo/pitch-model-v2`; the brief named f1ce2cd, which is an ancestor — every file cited below is unchanged between the two)

**One-paragraph answer.** S&M is the only cost line at Airbnb whose level is a decision rather than a driver. It is 21–24% of revenue and rising, it has an estimated intercept of +17% growth a year at zero revenue growth (M6 `c_sm` 0.155), and its historical response to a revenue *fall* is −0.12 (t −0.50) against +1.83 on the way up (p 0.003, n 16). Put those together and FY27 EBITDA is a spending question: on the line build's other four cost lines, the Street's FY27 adj. EBITDA of $5,766M requires S&M of $3,328M, i.e. +9.5% y/y; our bottom-up build has $3,460M (+13.8%) and the calibrated run's residual allocation has $3,721M (+21.8%). Management *can* cut — the 2023 episode dummy is −12.7pp on S&M growth (t −3.40) and M6's cut engine reaches an FY27 35.0% floor inside historically observed caps — but the cut required is $386–508M of programme, a visible decision, and nothing in the build forecasts whether it happens. For 3Q26 the question is already closed: the quarter's S&M is solved backwards from management's own "margin down slightly" sentence, not forecast forward from a growth rate.

## 2. The number

**Sources.** Rows marked **LB** come from the bottom-up line build (`40_line_build`, 15 Sep 2026 — every parameter has a named 10-K/10-Q source). Rows marked **CC** come from the calibrated combination (`23_final_model`, 14 Sep, post-WS31 audit), whose S&M is a *mechanical residual allocation* of the adopted margin, not a built line (76.6% of the line residual is put into S&M by PIT error variance). **LB is the later note and the one its own author proposes as "the pitch's line view"; CC is the object that was backtested (on margin, not on lines).** Where the two differ, both are shown.

### S&M in USD m

| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base **LB** | 3Q26 | 778.3 | 710.2 | 844.8 | USD m | 2026-09-11 data / 2026-09-15 build |
| base **CC** | 3Q26 | 781.1 | — | — | USD m | 2026-09-11 |
| base **LB** | 4Q26 | 758.1 | 713.7 | 802.5 | USD m | 2026-09-11 / 15 |
| base **CC** | 4Q26 | 770.6 | — | — | USD m | 2026-09-11 |
| base **LB** | FY26 | 3,040.4 | 3,003.1 | 3,073.7 | USD m | 2026-09-11 / 15 |
| base **CC** | FY26 | 3,055.8 | — | — | USD m | 2026-09-11 |
| base **LB** | FY27 | 3,459.6 | 3,285.6 | 3,692.7 | USD m | 2026-09-11 / 15 |
| base **CC** | FY27 | 3,720.9 | — | — | USD m | 2026-09-11 |
| short **LB** | 3Q26 | 778.3 | 710.2 | 844.8 | USD m | 2026-09-15 |
| short **LB** | 4Q26 | 758.1 | 581.4 | 802.5 | USD m | 2026-09-15 |
| short **LB** | FY26 | 3,040.4 | 2,863.7 | 3,073.7 | USD m | 2026-09-15 |
| short **LB** | FY27 | 3,459.6 | 3,285.6 | 3,692.7 | USD m | 2026-09-15 |
| breaker **LB** | 3Q26 | 785.4 | 710.2 | 844.8 | USD m | 2026-09-15 |
| breaker **LB** | 4Q26 | 713.7 | 581.4 | 758.1 | USD m | 2026-09-15 |
| breaker **LB** | FY26 | 3,003.1 | 2,863.7 | 3,040.4 | USD m | 2026-09-15 |
| breaker **LB** | FY27 | 3,285.6 | 3,040.4 | 3,459.6 | USD m | 2026-09-15 |

### S&M as % of revenue, and y/y growth

| scenario | source | 3Q26 % / y/y | 4Q26 % / y/y | FY26 % / y/y | FY27 % / y/y |
|---|---|---|---|---|---|
| base | **LB** | 16.20% / +33.1% | 23.85% / +19.8% | 21.31% / +28.0% | 21.86% / +13.8% |
| base | **CC** | 16.26% / +33.5% | 24.25% / +21.7% | 21.42% / +28.6% | 23.51% / +21.8% |
| short | **LB** | 16.63% / +33.1% | 25.56% / +19.8% | 21.82% / +28.0% | 23.20% / +13.8% |
| breaker | **LB** | 16.35% / +34.3% | 22.46% / +12.8% | 21.05% / +26.4% | 20.76% / +9.4% |
| *memory: actual* | panel | 3Q25 $585M / 14.29% | 4Q25 $633M / 22.79% | FY25 $2,376M / 19.41% | 1H26 $1,504M / 23.93%, +29.9% |
| *memory: Street-implied* | residual | — | — | — | **$3,328M / 21.04% / +9.5%** |

**Scenario definitions (all reproduced, none invented).**
- **base** = `40_line_build` scenario `base` (2H26 cost budget reconciled to management's 3Q26 "margin down slightly" sentence) on the bridge-v3 / WS06-v2b revenue path. CC = `23_final_model` `23_lines_quarterly.csv`, scenario `base`.
- **short** = `40_line_build` §8b `short_costs_at_budget`: the nights-lap + RNPL revenue override (3Q26 −2.6%, 4Q26 −6.7%, FY27 +4.5%) with **costs left at management's budget**. S&M *dollars are identical to base by construction*; only the denominator moves. Its `low` for 4Q26/FY26 is `short_with_q4_marketing_cut` ($176.7M off 4Q26 marketing, ~35% of the quarter's marketing, the cut that holds the FY26 35.5% floor).
- **breaker ("the ramp pauses")** = `40_line_build`'s own documented favourable **cost column** (`cost_bull`): 2H26 marketing +18% rather than +25%, FY27 marketing +10% rather than +15%, field ops +14%/+8% rather than +18%/+11% — every one of those a parameter with a source in `40_params.csv`. `low` is the **hard pause** (FY27 marketing and field growth set to 0, i.e. FY27 S&M flat on FY26 dollars = $3,040M / 19.21%), recomputed in `c4_sm_recompute.py`.
- Base `low`/`high` for 3Q26 are the two sourced ends of the reconciliation: `evidence_only` ($710.2M, the 2H26 step never lands) and `40_sentence_implied.csv` ($844.8M, +44.4% — the whole $97M sentence gap loaded into marketing with no AI-hosting step).
- `low`/`high` are **dollar** bounds only; their percentage of revenue depends on which revenue path they are put on, so they are deliberately not converted. The $581.4M / $2,863.7M bounds are the short case's cut applied to that case's own 4Q26 and FY26 S&M.

**The number that answers the judge.** At $4,804M of 3Q26 revenue, **$48.0M of S&M is 1.0pp of margin**; at $15,829M of FY27 revenue, **$158.3M is 1.0pp**. The FY27 spread between the calibrated run and the Street-implied residual is $393M = **2.48pp of FY27 margin**; between the line build and the Street it is $132M = **0.83pp**. The FY27 adj. EBITDA gap being argued about is $283M (CC $5,483M vs Street $5,766M).

### 2a. Model inputs (machine-readable)

Per DEC-0011: the workbook's cost stack is the line build (`40_line_build`), management's 3Q26 sentence is treated as a budget (base 3Q26 S&M $778M), the calibrated combination's dollar object is reserved for the 5 Nov card, and the evidence-only $710M case is carried as the upside risk. `sm_pct_rev` is S&M over each scenario's own revenue path; `sm_yoy_pct` is against the prior-year actual (3Q25 585, 4Q25 633, FY25 cash S&M 2,376) and, for FY27, against that scenario's own FY26.

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| sm_musd | base (line build) | 3Q26 | 778.3 | USD m | 40_lines_quarterly.csv sm_cash, scenario base |
| sm_musd | base (line build) | 4Q26 | 758.1 | USD m | 40_lines_quarterly.csv sm_cash, scenario base |
| sm_musd | base (line build) | FY26 | 3040.4 | USD m | 40_annual.csv sm_cash, FY26 base |
| sm_musd | base (line build) | FY27 | 3459.6 | USD m | 40_annual.csv sm_cash, FY27 base |
| sm_musd | short | 3Q26 | 778.3 | USD m | 40_short_case_quarterly.csv, costs at budget |
| sm_musd | short | 4Q26 | 758.1 | USD m | 40_short_case_quarterly.csv, costs at budget |
| sm_musd | short | FY26 | 3040.4 | USD m | 1H26 actual 1504 plus 2H26 short |
| sm_musd | short | FY27 | 3459.6 | USD m | dollars equal base by construction |
| sm_musd | breaker (ramp pauses) | 3Q26 | 785.4 | USD m | 40_lines_quarterly.csv sm_cash, scenario cost_bull |
| sm_musd | breaker (ramp pauses) | 4Q26 | 713.7 | USD m | 40_lines_quarterly.csv sm_cash, scenario cost_bull |
| sm_musd | breaker (ramp pauses) | FY26 | 3003.1 | USD m | 40_annual.csv sm_cash, FY26 cost_bull |
| sm_musd | breaker (ramp pauses) | FY27 | 3285.6 | USD m | 40_annual.csv sm_cash, FY27 cost_bull |
| sm_pct_rev | base (line build) | 3Q26 | 16.20 | pct | on revenue 4804.0 |
| sm_pct_rev | base (line build) | 4Q26 | 23.85 | pct | on revenue 3178.1 |
| sm_pct_rev | base (line build) | FY26 | 21.31 | pct | on revenue 14268.1 |
| sm_pct_rev | base (line build) | FY27 | 21.86 | pct | on revenue 15828.6 |
| sm_pct_rev | short | 3Q26 | 16.63 | pct | on revenue 4680.9 |
| sm_pct_rev | short | 4Q26 | 25.56 | pct | on revenue 2965.9 |
| sm_pct_rev | short | FY26 | 21.82 | pct | on revenue 13932.8 |
| sm_pct_rev | short | FY27 | 23.20 | pct | on revenue 14913.5 |
| sm_pct_rev | breaker (ramp pauses) | 3Q26 | 16.35 | pct | base revenue path 4804.0 |
| sm_pct_rev | breaker (ramp pauses) | 4Q26 | 22.46 | pct | base revenue path 3178.1 |
| sm_pct_rev | breaker (ramp pauses) | FY26 | 21.05 | pct | base revenue path 14268.1 |
| sm_pct_rev | breaker (ramp pauses) | FY27 | 20.76 | pct | base revenue path 15828.6 |
| sm_yoy_pct | base (line build) | 3Q26 | 33.05 | pct | vs 3Q25 585 |
| sm_yoy_pct | base (line build) | 4Q26 | 19.76 | pct | vs 4Q25 633 |
| sm_yoy_pct | base (line build) | FY26 | 27.96 | pct | vs FY25 2376 |
| sm_yoy_pct | base (line build) | FY27 | 13.79 | pct | vs FY26 3040.4 |
| sm_yoy_pct | short | 3Q26 | 33.05 | pct | vs 3Q25 585 |
| sm_yoy_pct | short | 4Q26 | 19.76 | pct | vs 4Q25 633 |
| sm_yoy_pct | short | FY26 | 27.96 | pct | vs FY25 2376 |
| sm_yoy_pct | short | FY27 | 13.79 | pct | vs FY26 3040.4 |
| sm_yoy_pct | breaker (ramp pauses) | 3Q26 | 34.26 | pct | vs 3Q25 585 |
| sm_yoy_pct | breaker (ramp pauses) | 4Q26 | 12.75 | pct | vs 4Q25 633 |
| sm_yoy_pct | breaker (ramp pauses) | FY26 | 26.39 | pct | vs FY25 2376 |
| sm_yoy_pct | breaker (ramp pauses) | FY27 | 9.41 | pct | vs FY26 3003.1 |
| card_sm_musd | base | 3Q26 | 781.1 | USD m | calibrated combination 23_lines_quarterly.csv sm_cash_musd; 5 Nov card only |
| sm_evidence_only_musd | alt_floor | 3Q26 | 710.2 | USD m | 40_lines_quarterly.csv sm_cash, scenario evidence_only; upside risk |

## 3. Derivation chain
1. Filing facts → FY25 10-K S&M split (brand & performance marketing $1,595M; field operations & policy $993M, cash $781M after $212M of S&M SBC); 1Q26/2Q26 10-Q marketing +$126M / +$132M ("paid growth initiatives in emerging markets and partnerships"); 2Q26 call "some incremental investment … in sales and marketing" in 2H; 6 Aug 2026 guide $4,690–4,770M and "adjusted EBITDA margin down slightly vs 3Q25". All quoted with their source in `data/processed/margin_build/40_line_build/40_params.csv` (rows `sm|*`, `recon|*`).
2. `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv` → `sm_cash` = GAAP S&M less S&M SBC (3Q25 585, 4Q25 633, 1Q26 696, 2Q26 808) ; `data/processed/abnb_quarterly_costlines.csv` ties FY25 GAAP S&M to $2,588M on $12,241M.
3. `analysis/src/margin_build/40_line_build/run.py` `build()` lines 117–123, 144–146, 172 → marketing chain (FY25 base × 1H/2H shares × growth, plus the Q3 reconciliation step) + field chain, spread on the 2023–25 mean quarterly S&M shares (Q1 .2397 / Q2 .2703 / Q3 .2370 / Q4 .2530).
4. `data/processed/margin_build/40_line_build/40_lines_quarterly.csv`, column `sm_cash`, rows `3Q26…4Q27` × scenario; `40_annual.csv` column `sm_cash`, rows FY26/FY27 × scenario; `40_short_case_quarterly.csv` / `40_short_case_summary.csv` for the short case and the $176.7M cut.
5. Parallel chain (CC): `analysis/src/margin_build/23_final_model/forecast.py` → `data/processed/margin_build/23_final_model/23_lines_quarterly.csv`, column `sm_cash_musd`, rows `2026Q3…2027Q4`, scenario `base`. Here S&M is `sm_model` (M1 driver line) **plus** `sm_alloc`, the 76.6% share of the line residual needed to reconcile the five lines to the adopted margin (3Q26: 730.08 + 51.06 = 781.14).
6. Street-implied FY27 S&M: `23_vs_consensus.csv` FY27 (`lseg_revenue_musd` 15,819.3, `lseg_ebitda_musd` 5,766.0, LSEG 11 Sep, n 44, EBITDA sd $154.2M) less `40_annual.csv` FY27/base `cor_cash + ops_cash + pd_cash + ga_cash` ($6,807.3M) plus `da` ($82.5M) = **$3,328.5M = 21.04%**. Recorded in `docs/pitch-forecasts/questions/fy27-sm-share-above-219/research-log.md` claim 5.
7. Elasticities: `data/processed/margin_build/M6_cycle_flex/M6_cycle_flex_k_table.csv`, rows `1Q22+|rw|sm|lag0` (k 0.418, t 2.25, p 0.024, n 18, R² 0.13) and `1Q22+|rw|sm|asym_up_dn` (k_up +1.83, k_dn −0.12, k_dn−k_up −1.95, p_equal 0.0030, n 16).

## 4. Governing sources

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-09-15 | `docs/margin-build/notes/40_line_build.md` (+ `40_line_build/` outputs) | FY27 S&M $3,460M = **21.9%** of revenue built from the 10-K split; 3Q26 S&M $778M (+33%); FY26 21.3%; the $176.7M 4Q26 cut that holds the floor | **Governs the line view.** Latest note on this line. Supersedes the run's allocation as the composition view ("the quarterly lines … can replace the run's `23_lines_quarterly.csv` allocation as the pitch's line view") |
| 2026-09-15 04:35 | `docs/margin-build/SYNTHESIS.md` §11 first bullet | FY27 S&M restated **$3,740M / 23.6% → $3,721M / 23.5%** | Governs the CC allocation number. Supersedes §3/§9's pre-WS32 $3,740M |
| 2026-09-14 | `docs/margin-build/SYNTHESIS.md` §11 + `audit/AUDIT_RESPONSE.md` (WS31, 18 findings, all closed) | 3Q26 S&M **$781.1M / +33.5%** (from $790.2M / +35.0%, audit finding 03: the add-back schedule is D&A only, $11.9M less residual to allocate) | **Governs.** Supersedes the pre-audit $790M/+35%, which is in `23_final_model/_pre_audit/` and must not be quoted |
| 2026-09-14 | `docs/margin-build/audit/CODEX_LINE_BUILD_CHECK.md` (gpt-6-astra, read-only) | 7 findings on the line build, all fixed; the S&M reconciliation allocation independently verified — **the marketing part of the gap is Q3-only and the hosting part persists**, and FY27 marketing includes the Q3 step before +15% | Governs; confirms the S&M chain. The audit quotes the step as $67.42M and hosting $28.89M **pre-fix**; the committed post-fix values are **$68.15M of Q3 marketing and $29.21M per quarter of hosting** (my recompute, §5) — inside the audit's own "no number moved by more than $3M" |
| 2026-09-17 | `docs/pitch-forecasts/questions/fy27-sm-share-above-219/` (F04 rev 2) | Street-implied FY27 S&M **21.04%** (rev-1's 20.52% omitted D&A and is withdrawn); P(FY27 S&M ≥ 21.9%) = **0.55**, CI 0.40–0.68; model median 22.16% | **Governs the Street residual.** Supersedes rev 1 |
| 2026-09-17 | `docs/pitch-forecasts/questions/bonus-marketing-cut-signalled/` (B03 rev 1) | P(management signals a marketing/S&M moderation at the 5 Nov print) = **0.18** (CI 0.10–0.30); base rate 4 of 23 prints, **0 of 10 since 1Q22… 0 of 5 Novembers**; impact if Yes FY26 +1.2pp / FY27 +1.1pp, stock ≈ −$3 | Governs. (memo v3 quotes this as 0.21 — see §7) |
| 2026-09-13 | `docs/margin-build/notes/M6_cycle_flex.md` §4, T1, T4 | `k_sm` 0.418 (t 2.25) passes its half of T1 (**T1 fails jointly on `k_pd`**); intercept `c_sm` 0.155 → +17%/yr at zero revenue growth; asymmetry k_up +1.83 / k_dn −0.12, p 0.003; `k_sm` **unstable across vintages** 0.87 (2022) → 0.27–0.42 | Governs the elasticity. Its FY26 floor break-even (1.87–2.54% / $149–203M) is **superseded** by SYNTHESIS §4 (0.63%/0.94%) and is on the kill list |
| 2026-09-13 | `docs/margin-build/notes/M1_driver_lines.md` | Both pre-registered pass lines FAIL; "every line but G&A beats the naive by 20–70%" **withdrawn**; S&M LOYO elasticity unstable 0.27–1.10; "treat S&M as a spending decision with a PIT trend and take the level from management" | Governs the honest status of a modelled S&M line |
| 2026-09-13 | `docs/margin-build/notes/21_red_team.md` R11 | Three driver models put 3Q26 at 51.2–51.6% against a 50.09% ceiling and a 49.78% Street; "the gap is the S&M line. Somebody has to decide whether management's ceiling is binding" | Governs the framing of the open choice (§8.1) |
| 2026-09-11 | `research/notes/overnight/14_master-synthesis.md` §"5 Nov card" item 6 | Brand & performance marketing y/y is "the single most informative line in the release"; FY26 margin 37.0% at +17%, 36.2% at +25%, 35.5% at +31% | **The tell governs; the margin numbers are superseded** by the 14–15 Sep build (SYNTHESIS §3 carries nothing forward from the WS07 lever model) |
| 2026-09-17 | `deck/drafts/memo_v3_short_2026-09-17.md` ¶3, §Bridge | "S&M goes from 19.4% (FY25) to 21.3% (FY26E) to 21.9–23.5% (FY27E)"; the $177M 4Q26 cut; short-case EPS bridge | Consistent with the above; the 21.9–23.5% band is the LB/CC pair, correctly labelled |

**Web fetches: 0.** Every filing fact this line needs (FY25 10-K S&M split, the 1H26 10-Q marketing and payroll deltas, the 6 Aug 2026 guide and margin sentence, the 2Q26 call language) is already quoted with its source inside `40_params.csv` and `02_panel_quarterly.csv`, and the line build's parameter sheet was independently re-verified by the Codex/Astra read-only check. Nothing was added that a fetch could have settled, so the five-fetch budget was not used.

## 5. Reproduction receipt
- Receipt: `data/processed/pitch_model_v2/receipts/C4/receipt.json` (the 40_line_build run; a copy is kept as `receipt_40_line_build.json`, and the earlier 23_final_model run is `receipt_23_verify.json` with `stdout_23_verify.txt`)
- Command: `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id C4 --watch data/processed/margin_build/40_line_build --watch model/ABNB_margin_line_build.xlsx --cmd "python3 analysis/src/margin_build/40_line_build/run.py"` · Exit: 0 · Wall: 0.7s · Interpreter: python3 (3.13.0 / **pandas 3.0.0**)
- Output: `data/processed/margin_build/40_line_build/40_lines_quarterly.csv` column `sm_cash`, rows `3Q26`/`4Q26` scenario `base` = **778.3158 / 758.1075**; `40_annual.csv` column `sm_cash`, FY26/FY27 base = **3,040.423 / 3,459.624** · Committed value: identical (git reported **no change** to any of the seven S&M-bearing CSVs) · Tolerance: ±$0.5M · **Match: yes**
- Second command: `… --watch data/processed/margin_build/23_final_model --cmd "MARGIN_VERIFY_ONLY=1 python3 analysis/src/margin_build/23_final_model/run.py"` · Exit: 0 · Wall: 5.9s · Interpreter: python3 / pandas 3.0.0. Its own comparison block (saved at `receipts/C4/stdout_23_verify.txt`) reports **24 of 24 committed CSVs "identical"**, worst `max|d|` 1.6e-11, including `23_lines_quarterly.csv` at 4.5e-13; the 25th file is the registry copy, which verify-only does not write to the committed tree. All eight step-4b reconciliation assertions passed. `_verify/` was removed; `git status` is clean and both receipts record `"restored": true`.
- Third command (my own, read-only, in the receipt folder): `python3 data/processed/pitch_model_v2/receipts/C4/c4_sm_recompute.py` — an independent re-implementation of the S&M chain from `40_params.csv`. It reproduces all **24 committed S&M cells** (4 scenarios × 6 quarters) to `max|diff| = 1.1e-13 USD m` (`c4_sm_line_recompute_check.csv`) and emits the §2 table as `c4_sm_scenarios.csv`.
- **Interpreter note (the brief asked):** both margin packages were written for Windows `py -3.13` with pandas 2.3, but **both ran clean on macOS `python3` with pandas 3.0.0**; `.venv-pd2` was not needed.
- **The one non-match, and why it is not one.** The 40_line_build re-run changed exactly one committed file: `40_sensitivities.csv`, where rows 20 and 22 swap their `d_fy27_eps_usd` values (0.0938 apart). Verified cause: line 313 sorts with `sort_values("d_fy27_margin_pp", key=lambda s: -s.abs())`, and **exactly three rows have `d_fy27_margin_pp == 0.0` exactly** (`etr_fy27`, `tbill_3m`, `rnpl_share_shift_pts`) — a tie whose order is not stable across pandas versions. No value changed; no row is an S&M row; the two S&M sensitivity rows (`marketing_growth_fy27` −0.669pp / −$0.153, `marketing_growth_2h26` −0.044pp) are byte-identical. The workbook `.xlsx` also differs, as any openpyxl re-write does.

## 6. Test record

The line in the model is `sm_cash_musd`. Per `docs/margin-build/SYNTHESIS.md` §7, line objects must be scored against `seasonal_naive_drift`, **not** `seasonal_naive` (S&M grows 20–30% a year, so last year's level is a straw man: its W1 MAE is $94.3M against drift's $32.2M). All rows `prior_basis = PIT`, from `data/processed/margin_build/10_harness_margin/scoreboard_margin.csv`.

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| W1 | 14 | `sm_cash_musd` MAE h=0, best object (`driver-lines\|lines_v2\|a_unit_rw`) | $34.20M → **1.062x drift** | drift $32.20M (naive $94.30M → 0.341x) | n/a (no guide for a cost line) | not published for lines | M1 §P1/P2: `b_elastic_rw` beats `seasonal_naive` and `pct_rev_last4` on margin/EBITDA at h=0 **and** h=1, both windows | **FAIL** (M1: P1 3 of 8, P2 14 of 16) |
| W2 | 10 | same | $31.58M → **1.032x drift** | drift $30.60M | — | — | same | **FAIL** |
| W1 | 14 | `sm_cash_musd` MAE h=0, best alt-augmented (`lines_aug\|best1_eq`) | $34.45M → **1.070x drift** | — | — | — | M4: beat the baseline in both windows with a stable sign | **FAIL in W1** |
| W2 | 10 | same | $29.51M → **0.964x drift** | — | — | — | same | pass in W2 only → **fails both-window rule** |
| W1 / W2 | 14 / 10 | the spec actually inside the run (`FAMILY_A` → `lines_v2\|b_elastic_rw`) | 1.176x / 1.139x drift | — | — | — | — | **FAIL, both windows** |
| W1 / W2 | 13 / 9 | `a_unit_rw` at h=1 | 0.808x / 0.793x drift | — | — | — | not pre-registered at h≥1 | passes both windows — but **post hoc**, on n 13/9, and this spec is not the one any published S&M number uses |
| 1Q22+ | 18 | M6 `k_sm` (revenue elasticity of S&M, lag 0, rw) | **0.418**, t 2.25, p 0.024, R² 0.13 | — | — | — | M6 T1: `k_sm` **and** `k_pd` positive with HAC t ≥ 2.0 at some lag | **T1 FAIL** (jointly; `k_sm` passes, `k_pd` is negative at every lag, t −3.25 at lag 2) |
| 1Q22+ | 16 | M6 T4 asymmetry, S&M | k_up **+1.83**, k_dn **−0.12**, k_dn−k_up **−1.95** | — | — | — | descriptive, no pass line (n 16) | reported; p_equal **0.0030** |
| W1 / W2 | 14 / 10 | the margin object the S&M line is reconciled to (`final-margin\|combined\|stack_clip`, h=0) | MAE 1.126 / 0.788pp | 0.504x / 0.402x seasonal naive | — | 0.708x / 0.601x | SYNTHESIS §2 pre-reg | **PASS at h=0 only**; h=1 loses to the Street 1.189x / 1.278x, h=2 fails in W2 1.026x naive |
| — | — | `40_line_build` S&M line | **no backtest exists** | — | — | — | none written | not tested (its own note: "product development, marketing and G&A are spending decisions; the numbers above are views with sources, not estimates") |

**The comparison that flatters us, stated so a judge cannot spring it.** Against `seasonal_naive` (y[q−4]) the S&M line looks excellent — 0.36–0.40x in W1, 0.27–0.32x in W2, with NW(1) p ≤ 0.005 and sign-test p 0.029 / 0.011 — and M1's *pre-registered per-line expectation had been that S&M would **not** beat `pct_rev_last4` materially*, which it did comfortably (M1 §4d: 0.17–0.37x for pd and sm). Both of those are artefacts of the line growing 20–30% a year: any baseline that assumes zero growth loses to any baseline that assumes trend growth. The moment the comparator is the drift baseline that SYNTHESIS §7 mandates, every S&M object at h=0 is 1.06–1.18x in W1. M1's own LOYO check adds that S&M is the one line whose elasticity is *not* stable (0.27–1.10).

**Strongest known failure:** no S&M object in the build beats a seasonal-naive-**drift** baseline at h=0 in both windows — the best is 1.062x in W1 — so the S&M number the pitch quotes is either a mechanical residual of a margin combination that itself fails at h≥1, or an unbacktested spending view, and the FY27 level that carries the whole variant thesis is explicitly "a spending scenario, not a forecast".

## 7. Kill list and consistency

**Kill-list check.** Nothing withdrawn is quoted here. Specifically avoided, and named because the C4 literature contains them:
- **3Q26 S&M $790.2M / +35.0%** — the pre-audit CC number, superseded by $781.1M / +33.5% (WS31 finding 03). It survives in `23_final_model/_pre_audit/23_lines_quarterly.csv` and in any note written before 14 Sep; do not quote it. This is the conflict the brief flagged, and it is **resolved in favour of $781M / +33.5%**.
- **FY27 S&M $3,740M / 23.6%** — superseded by $3,721M / 23.5% at SYNTHESIS §11's 15 Sep 04:35 amendment.
- **"Airbnb has no cost dial"** — withdrawn (WS31 finding 13). The correct statement is the one used in §9 below: the peer regression is k 0.14 with t 0.47, n 18, SE ≈ 0.30, 95% CI ≈ −0.44 to +0.72 — **imprecise, not zero**, and it does not exclude BKNG 0.61, TRIP 0.63 or EXPE 0.44. The model's own working number is M6's **cash-cost** elasticity 0.364 (t 6.58), a different cost definition.
- **M6's FY26 floor break-even "survives a 1.9–2.5% / $149–203M 2H26 shortfall"** — on the kill list; the governing figure is 0.63% ($50M) held / 0.94% ($75M) flexed.
- **M5's "+0.41pt beat" as a model output**, **M3's LIVE 4Q26 34.51% / FY26 37.03%**, **M6's FY28 31.3%**, any **oracle spec**, and **"survives both windows" as evidence of skill** — none used. Note that the `survives_both_windows = True` flag *is* True for several S&M specs in the scoreboard; it is computed against `seasonal_naive`, has a ~30% null pass rate at this n, and W2 ⊂ W1, so §6 reports the drift comparison instead.
- **"Nothing beats guide × cushion"** — not asserted; the correct form is "no single object beats it on both windows".
- **WS31b's 4Q26 margin profile (24.7–25.9%)** — not cited; it is unreconciled and SYNTHESIS §8 item 1 forbids citing it.

**Conflicts found and their resolution.**
1. **3Q26 S&M $781M (CC) vs $778M (LB).** Both post-audit, both reproduced exactly. The $2.8M difference is the residual allocation vs the built line. Not a conflict — quote the pair, or quote LB and say the calibrated run is $3M higher.
2. **FY27 S&M 21.86% (LB) vs 23.51% (CC) vs 21.04% (Street-implied).** Real and unresolved; it is the §8.2 choice. Memo v3's "21.9–23.5%" already carries it as a band, which is the honest treatment.
3. **New — the governing note overstates its own result.** `40_line_build.md` says the two builds "disagree on 2027 by one point, entirely in S&M". Its own `40_vs_run.csv` says otherwise: summing FY27, S&M is **−$261.3M** but cost of revenue is **+$168.8M** (the AI-hosting run-rate step), product development −$68.8M, ops +$19.9M, G&A −$19.5M, netting to **+$160.9M of EBITDA**. S&M is the largest single term and 1.65pp of FY27 revenue, but ~65% of it is offset by cost of revenue, so "entirely in S&M" is wrong about the *internal* comparison. It is defensible about the comparison **to the Street** — but only because the Street's S&M was *derived as a residual using the line build's own other four lines* ($6,807M), which F04's research log states plainly ("The Street's S&M is a residual of an EBITDA panel, not a modelled line"). **Recommended wording for the memo: "against the Street, on our own other four cost lines, the FY27 gap is S&M" — with the conditional clause kept.**
4. **B03 probability quoted two ways.** The question folder's README and forecast JSON say **0.18** (CI 0.10–0.30); memo v3's list of dropped bonus items says **0.21**. 0.18 is the forecast; 0.21 is the folder's *anchor*. The memo should carry 0.18.
5. **F04's headline (P = 0.55 that FY27 S&M ≥ 21.9%) sits almost exactly on the line build's own 21.857%.** That is not an accident — it is the model's median (22.16%) being one-sixth of a point above a bar the central case is one-twentieth of a point below. Treat 21.9% as a coin toss and do not present the line build's 21.86% as "below the bar" without saying the bar is inside its own noise.
6. **Consistency with C6 (margin) and C7 (EPS):** the S&M numbers here are the same objects C6 must use; `$48.0M = 1.0pp of 3Q26 margin` and `$0.0666 of 3Q26 EPS per 1pp` chain to C7's bridge. Consistent with R6's FY27 revenue $15,829M and D3's path. No conflict with memo v3.

## 8. Open choices

1. **Is management's 3Q26 margin sentence a binding budget, or a floor to be beaten?** This is the same question 21_red_team R11 left open ("somebody has to decide whether management's ceiling is binding, because every margin number on the memo follows from that one call"), and it *is* the 3Q26 S&M number. Options: **(a)** reconciled base — take the sentence as the cost budget, S&M $778M (+33%), 3Q26 margin 50.37% (LB) / 49.94% (CC); **(b)** evidence-only — build S&M from the disclosed components alone, $710M (+21%), 3Q26 margin 52.39%; **(c)** carry (a) as the point and (b) as the upside. — **Recommendation: (c), with (a) as the point.** Why: WS22 group A shows the quarterly sentence has been *missed* slightly more often than beaten (W2 mean −0.19pp, above in 4 of 10), so it is a real ceiling rather than sandbagging; but (b) is $68M of S&M = 1.4pp of 3Q26 margin (and +2.0pp in full, once the hosting half of the gap comes out too), which is the single largest upside risk to a short, so it must be on the page, not in a footnote.
2. **Which FY27 S&M share does the memo lead with: 21.9% (LB) or 23.5% (CC)?** Options: **(a)** 21.9% — bottom-up, every parameter sourced, but never backtested and it applies management's stated deceleration to a base that already contains the 3Q26 step; **(b)** 23.5% — the allocation of an object that *was* scored, but only on margin at h=0, and the allocation rule is mechanical (76.6% of the residual to S&M by PIT error variance) and produces a G&A number (+9.4%) its own synthesis calls "uncomfortable" against a −5.4% 1H26 actual; **(c)** the band 21.9–23.5%, as memo v3 already does. — **Recommendation: (c).** Why: the two builds are not independent evidence for one number, the gap is 1.65pp of FY27 revenue = $261M = more than half the disagreement with the Street, and F04 puts P(≥21.9%) at 0.55 with a credible interval of 0.40–0.68 — i.e. the repo's own probabilistic view says the point is unidentified. Lead with the band and with the *mechanism* (the +17%/yr intercept and the −0.12 down-elasticity), not with a decimal.
3. **How is the "breaker" presented — as a scenario column or as a stated flip condition?** Options: **(a)** a third P&L column (FY27 S&M $3,286M / 20.76%, FY27 margin ≈ 38.0% on base revenue per `40_line_build.md`'s scenario grid) ; **(b)** a one-line flip rule on the 5 Nov tell: brand & performance marketing y/y below ~+20% in the 3Q26 10-Q, or any forward "moderated / optimised / slower than revenue" statement (B03, P = 0.18); **(c)** both. — **Recommendation: (c), with (b) in the score sheet.** Why: the breaker at the ramp level *is* the Street's number (+9.4% y/y against a Street-implied +9.5%), so presenting it as a column makes the disagreement legible in one row; and B03's base rate is the strongest thing we have — 4 of 23 prints since 4Q20, **1 of 18 since 1Q22, 0 of 10 since 1Q24 and 0 of 5 Novembers** carried such a statement.
4. **Does the memo claim "the whole FY27 gap is S&M"?** Options: **(a)** as written; **(b)** with the conditional clause ("on our own other four cost lines, the Street's FY27 EBITDA implies S&M of $3,328M"); **(c)** drop the claim and quote the EBITDA gap only. — **Recommendation: (b).** Why: §7 conflict 3. The claim is true of the Street comparison and false of the internal one, and a judge who asks "how do you know the Street's S&M?" has to be told it is a residual, not a published line.
5. **Whose line stack goes in the workbook — LB's built lines or CC's allocated ones?** Options: **(a)** LB throughout, with CC's margin object kept for the 5 Nov card's dollar point / band / P(beat); **(b)** CC throughout; **(c)** LB for composition, CC for every number that is scored. — **Recommendation: (a) = (c).** Why: it is what `40_line_build.md` itself proposes ("the 5 Nov card keeps the run's dollar object for the beat probability — it was backtested; this build was not — and uses this note for the composition"), it keeps every line traceable to a filing, and it avoids putting the +9.4% G&A allocation artefact on the page. The cost: the LB stack's 3Q26 EBITDA is $2,420M against the card's $2,399M, so the workbook must show the $21M reconciliation.

## 9. Judge Q&A
1. Q: **Why is S&M the whole FY27 disagreement?** A: Because it is the only line big enough and discretionary enough to move FY27 EBITDA by $283M. On our other four cost lines, the Street's FY27 adj. EBITDA of $5,766M (LSEG, 11 Sep, n 44, sd $154M) implies S&M of $3,328M — 21.04% of revenue and +9.5% y/y. Our bottom-up build has $3,460M (21.86%, +13.8%) and the calibrated run's allocation $3,721M (23.51%, +21.8%). At $158M per point of FY27 margin, that is a 0.83pp to 2.48pp disagreement about one spending decision. The corollary the Street is implicitly making: its FY27 incremental margin is 43.7% against our 24.7% (CC) / 34.8% (LB), on a line that ran +29.9% y/y in 1H26 and is guided to "some incremental investment" in 2H.
2. Q: **What if management just cuts it?** A: Then we are wrong, and the repo says so in three numbers. (i) It has done it once: the 2023 ADR-normalisation year carries an S&M episode dummy of −12.7pp (t −3.40), S&M growth going +28.6% in 2Q23 to +3.8% in 3Q23. (ii) M6's cut engine reaches an FY27 35.0% floor inside historically observed caps in every scenario (φ < 1 everywhere), but it costs $386–508M of product-development/S&M/G&A programme — a visible change, not a rounding. (iii) The 4Q26 version is priced: in our short case, $176.7M off 4Q26 marketing (~35% of the quarter's marketing) restores FY26 to exactly 35.5% and 4Q26 EBITDA from $700M to $876M. Against that: the down-elasticity is −0.12 with t −0.50 — historically S&M growth does **not** decelerate when revenue growth falls below trend (k_up +1.83 vs k_dn −0.12, p 0.003, n 16) — the fitted intercept says S&M still grows ~17% a year at zero revenue growth, and management has made a forward moderation statement in 0 of the last 10 prints and 0 of 5 Novembers (B03, P = 0.18 for 5 Nov).
3. Q: **Is $781M for 3Q26 a forecast or a plug?** A: Honestly, a plug — and it barely matters for this quarter. In the calibrated run it is the M1 driver line ($730M) plus $51M of the residual needed to reconcile the five cash lines to the adopted 49.94% margin, allocated 76.6% to S&M by PIT error variance. In the line build it is $710M of evidence plus 70% of the $97M gap between the evidence and management's own "margin down slightly" cost budget, giving $778M. The two routes land $3M apart, which is 0.06pp of margin. What is *not* a plug is the constraint: at $4,804M of revenue, $48M of S&M is 1.0pp, and landing the sentence on marketing alone would need 2H26 marketing +61% (3Q26 S&M $845M, +44%), which is not credible — hence the 70/30 split with AI hosting.
4. Q: **Can you measure Airbnb's cost flexibility at all?** A: Not precisely. The peer regression of total opex on revenue gives k 0.14 with t 0.47 on n 18 — SE ≈ 0.30, a 95% interval of roughly −0.44 to +0.72, which does **not** exclude flexibility as large as BKNG's 0.61, TRIP's 0.63 or EXPE's 0.44. It is imprecise, not zero. The model's own working number is M6's cash-cost elasticity of 0.364 (t 6.58) on a different cost definition, and the S&M-specific elasticity is 0.418 (t 2.25, R² 0.13, n 18) — which is itself unstable, falling from 0.87 in the 2022 vintage to 0.27–0.42 now. The defensible statement is the asymmetry and the band: flexing recovers 30–40% of a revenue miss, so use 0.35–0.6pp of FY27 margin per point of revenue.
5. Q: **What single disclosure on 5 November settles this?** A: The brand-and-performance versus field-operations split inside the 10-Q's S&M discussion. 1H26 ran brand and performance +32% ($1,091M against $824M) with field ops +24%; our base takes 2H26 marketing to +25% and FY27 to +15%. Below roughly +20% in 3Q26 is the first evidence the reinvestment cycle is easing and the breaker column starts to bind; above +28–30% and the FY26 sentence lands on the floor rather than above it. Any forward "moderated / optimised / slower than revenue" sentence resolves B03 Yes and is worth about +1.1pp of FY27 margin on the cost side.

## 10. Grade
Grade: B — both packages reproduce exactly (exit 0; 23_final_model 24 of 24 CSVs identical to 1.6e-11, 40_line_build's seven S&M-bearing CSVs unchanged, and an independent re-implementation of the S&M chain matches all 24 cells to 1.1e-13), but the object itself is descriptive, not predictive: no S&M line object beats a seasonal-naive-drift baseline at h=0 in both windows, the margin combination the CC allocation rests on fails at h≥1, the line build has no backtest at all, and FY27 is labelled a spending scenario by its own authors.
