# WS31 — response to the Codex/Astra audit of WS23

Agent: WS31 (apply the audit), 14 Sep 2026. Worktree `C:\Users\krish\citadel-abnb-margins`, interpreter `py -3.13`.
Audit under review: `docs/margin-build/audit/CODEX_ASTRA_AUDIT.md` (18 findings: 1 critical, 12 major, 5 minor).

**Status: DONE. All 18 findings closed — 17 accepted and fixed, 1 (finding 16) accepted in part with
the deferred half named. None rejected.** The build and the scorer were re-run in order
(`23_final_model/run.py`, which ends by calling `score.py`, then `20_scoreboard/run.py`), both exit 0,
and the workbook was regenerated. **No critical finding is outstanding**: the print-date gate (01) is
fixed and replayed, h=0 is unchanged, and every pass/fail verdict in the build survives the correction.
`_pre_audit` copies of every CSV and registry file whose numbers
changed are in `data/processed/margin_build/23_final_model/_pre_audit/`,
`data/processed/margin_build/10_harness_margin/_pre_audit/`,
`data/processed/margin_build/registry/*_pre_audit.csv.bak` and `model/ABNB_margin_model_pre_audit.xlsx`.

## Triage

| id | severity | decision | what changed | files | evidence |
|---|---|---|---|---|---|
| 01 | critical | **accept — fix** | Both calibration pools (the member-error pool that sets the weights, and the combination's own error pool that sets the conformal band) are now gated by the target quarter's `print_date <= vintage_date`, not by quarter order. Same gate in `diagnostics.py`. Backtest replayed, registry rebuilt, scorer re-run. | `23_final_model/combine.py`, `diagnostics.py` | Reproduced the auditor's claim: at the 2023-05-09 vintage the h=1 target 2023Q3 was being weighted on 2023Q2 errors although 2023Q2 printed 2023-08-03. |
| 02 | major | **accept — fix** | The line stack now displays the full reconciliation: `sum(five cash lines) − add-backs = total cash costs`, `revenue − total cash costs = adj EBITDA`. New columns `sum_five_lines_musd`, `addbacks_musd`, and an assertion in `run.py`. | `forecast.py`, `workbook.py`, `run.py`, `23_lines_quarterly.csv`, `23_forecast_quarterly.csv` | Five 3Q26 lines summed to 2,437.4 against a displayed total of 2,404.9; the 32.5 gap was `other_net`, present in the CSV but not in the P&L or the Bridge sheet. |
| 03 | major | **accept — fix** | One add-back schedule everywhere: the cost reconciliation now uses **M7's D&A** as the only add-back (`addbacks_musd = da_musd`), dropping M1's `other_net` rule (0.68% of revenue) which carried ~11.9 of unsupported non-D&A add-backs. Historically `other_net − D&A` averages ≈ −1.2 on the last ten actual quarters, so D&A alone is the supportable schedule. The GAAP bridge is unchanged (`op income = adj EBITDA − SBC − D&A`) and now agrees with the cost stack by construction. | `forecast.py`, `run.py` | `other_net − D&A` = +11.881 in 3Q26 under M1's rule; the same difference in all six forecast quarters. Actuals 2024Q1-2026Q2: −12 to +6, mean −1.2. |
| 04 | major | **accept — fix** | The **adopted** dollar forecast (the margin combination × the revenue leg) is now built, scored and registered in its own right as `final-margin__combined_dollar_from_margin`. The 80% band, the Gaussian sd and P(beat) all come from that one object. The four-member dollar combination (`final-margin\|combined` on `adj_ebitda_musd`) stays, explicitly labelled a cross-check. The 0.77 beat probability is **retired** and restated as the band-consistent figure. | `combine.py`, `forecast.py`, `23_bands.csv`, `23_card_5nov.csv`, registry | The published band implied sd 77.98 and P 0.685; the published 0.77 used sd 51.95 from a different object. |
| 05 | major | **accept — fix** | Bear/bull quarterly and annual statements are now built at the **flex** cost response (M6 `k = 0.364` on total cash costs), not at the base margin. Base is unchanged. The held/full-flex variants stay in `23_scenarios.csv` as labelled sensitivities. | `forecast.py`, `23_lines_quarterly.csv`, `23_forecast_quarterly.csv`, `23_forecast_annual.csv` | P&L bear/base/bull 3Q26 margins were all 49.9399%; the scenario engine gave 49.6117 / 49.9399 / 50.4226. |
| 06 | major | **accept — fix** | EPS bands now propagate M7's measured bridge error (sd $0.083, W2 h=0 with EBITDA known, `M7_discussion_blend_eps.csv`) in quadrature with the EBITDA-driven term, and the column is labelled `eps_q10/q90_joint`. | `forecast.py`, `23_forecast_quarterly.csv`, `23_card_5nov.csv` | The 3Q26 EPS half-width was exactly `EBITDA half-width × (1−ETR)/shares`; no bridge residual entered. |
| 07 | major | **accept — fix** | CFO is rebuilt from the updated net income: `CFO = NI + D&A + SBC + ΔunearnedFees + other`, using M7's own working-capital and other components, quarterly and annual. FCF = CFO − capex. Reconciliation assertion in `run.py`. | `forecast.py`, `run.py` | `ΔFCF = ΔEBITDA` was applied pretax while NI moved after tax; omitted tax effect −15.7 (3Q26), −13.6/−13.8 (FY26/FY27). |
| 08 | major | **accept — fix** | Member identifiers, `street_vendor`, `street_as_of` and `knowable_from` (max input availability date, always ≤ vintage) are propagated onto every registry row; the composite is classified `consensus_anchored=yes` in `notes`, and the Street-independent variant is named there. | `combine.py`, registry files | 768 h=0/h=1 rows carried a Street-consuming member with a blank vendor stamp; all 1,152 rows had a blank `knowable_from`. |
| 09 | major | **accept — fix (with one documented limit)** | `n_params` now publishes the honest total (2 wrapper + 52 inherited = 54) and `notes` carries the split; `n_train` now counts **observations** (the prior quarters the weights were fitted on), not members. `n_members` cannot become a registry column — FORMAT 1.0 is frozen and `validate_registry_frame` raises on unknown columns — so it is carried as `n_members=<k>` inside `notes` and as a first-class column in `23_combination_by_quarter.csv`. | `combine.py`, registry files, `SYNTHESIS.md` | Every row read `n_params=2`, `n_train∈{3,4,6}` (the member count). |
| 10 | major | **accept — rewrite** | §2 "Hindsight" and "The caveat that is not in the p-values" rewritten: results are **retrospective and conditional on the selected pool**; the hindsight share and the leave-one-out table are no longer offered as evidence against selection bias; the model is declared frozen for prospective evaluation from this vintage. | `SYNTHESIS.md` | Pool membership is fixed in every replay; there is no untouched evaluation set. |
| 11 | major | **accept — rewrite** | "attained coverage 82-91%" is withdrawn. `23_bands.csv` columns renamed `rank_grid_cov80_lo/hi` (a theoretical rank-resolution grid from n), and the observed registry coverage (13/14 W1, 10/10 W2 at h=0) is reported separately as a different quantity. The live interval is labelled descriptive, not validated. | `forecast.py`, `23_bands.csv`, `SYNTHESIS.md` | Endpoints were order-statistic ratios computed from n, not a coverage measurement. |
| 12 | major | **accept — rewrite** | The FY floor is restored to an **inequality**: "FY ≥ 35.5% implies 4Q26 ≥ ~27.6% given our 3Q26 and revenue". The claim that an unchanged sentence makes the print a sell is removed and replaced by what the inequality does and does not say. | `SYNTHESIS.md`, `23_card_budget_identity.csv` (header note) | 28.90% already satisfies the floor. |
| 13 | major | **accept — rewrite** | "Airbnb has no cost dial" is withdrawn. The peer regression is reported as **imprecise**: k = 0.139, t = 0.468, n = 18, SE ≈ 0.297, 95% CI ≈ −0.44 to +0.72 — it does not exclude substantial flexibility, and the model's own cash-cost elasticity is 0.364 on a different cost definition. | `SYNTHESIS.md` | Recomputed SE from k and t. |
| 14 | minor | **accept — fix** | `lseg_sd_musd` split into `lseg_revenue_sd_musd` and `lseg_ebitda_sd_musd`; the ambiguous column is dropped and the workbook Consensus sheet updated. | `forecast.py`, `23_vs_consensus.csv`, `workbook.py` | Quarterly rows carried revenue sd (24.3 / 48.6) in a column read as EBITDA sd. |
| 15 | minor | **accept — fix** | Annual tax provision and net income are the **sum of the quarters** (1H26 actuals + forecast quarters for FY26); the annual ETR is derived afterwards. FY28, which has no quarterly build, keeps the rate approach and says so. | `forecast.py`, `23_forecast_annual.csv`, `run.py` assertion | FY26 base NI 3,145.928 vs 3,146.125 from the quarters. |
| 16 | minor | **accept in part / defer in part** | **Done:** the workbook README sheet now states in the first rows that it is a **frozen report generated from the CSVs**, not an input-driven model, and names the rebuild command. **Deferred:** wiring Inputs → forecast cells and annual sums as live formulas, and saving formula caches. Reason: openpyxl cannot evaluate formulas (only Excel can write caches), and converting the sheet set into a linked model is a rebuild, not an audit fix — over the 20-minute line. | `workbook.py` | 42 formulas, all local to Bridge, all caches blank. |
| 17 | minor | **accept — fix** | `r.clip` → `r["clip"]`. | `combine.py` | All 1,152 `notes` contained `<bound method NDFrame.clip ...>`. |
| 18 | minor | **accept — fix** | `MARGIN_VERIFY_ONLY=1` added: every step writes to `.../23_final_model/_verify/` instead of the committed outputs, the registry write is skipped, and `run.py` prints a per-file comparison (max absolute numeric difference, added/removed rows) against the committed CSVs. | `combine.py`, `diagnostics.py`, `forecast.py`, `workbook.py`, `run.py`, `README.md` | Auditor could not execute the build (no scipy in the accessible interpreter). |

**Rejected findings: none.** Every finding reproduced or was accepted on its reasoning; the only partial
is 16, where half the remedy is out of scope for an audit response and is recorded as deferred with the reason.

## What moved

Every number, before -> after, is in `docs/margin-build/SYNTHESIS.md` **§11 Post-audit changes**, and
the code-level account is the appended "Audit response" section of
`docs/margin-build/notes/23_triangulate.md`. The short version:

- **h=0 is unchanged everywhere.** Margin MAE 1.126 (W1) / 0.788 (W2), the ratios, the sign tests,
  the leave-one-out table, the adopted points (3Q26 49.94% / $2,399M, 4Q26 28.90%, FY26 35.73% /
  $5,098M, FY27 34.64% / $5,483M, EPS $5.28 / $5.73).
- **h=1 / h=2 moved** with the date gate: h=1 MAE 1.962 -> 1.952 (W1), 1.275 -> 1.269 (W2);
  h=2 2.255 -> 2.229 (W1), 1.762 -> 1.766 (W2); h=2 W1 cov80 0.833 -> 0.750. Verdicts unchanged.
- **The card:** 3Q26 dollar band $2,299-2,499M -> **$2,337-2,462M**; P(beat) 0.77 -> **0.779**;
  EPS band $2.74-3.02 -> **$2.70-3.05**; 3Q26 S&M $790M/+35% -> **$781M/+33.5%**.
- **Statements:** FY26 base NI 3,145.93 -> 3,146.12; FY FCF mid 4,830 / 5,283 / 5,716 ->
  **4,844 / 5,297 / 5,731**; FY27 bear/bull margin 34.51/34.71 -> **32.15/36.53**.
- **Registry:** provenance populated, `n_params` 2 -> 54 (2 + 52 inherited), `n_train` now
  observations, the `bound method` notes bug gone, and a new object
  `final-margin__combined_dollar_from_margin` (576 rows) carrying the adopted dollar construction.

## Re-run log

```bash
py -3.13 analysis/src/margin_build/23_final_model/run.py      # exit 0; steps 1-4, assertions, score.py
py -3.13 analysis/src/margin_build/20_scoreboard/run.py       # exit 0
```

Run sequentially, never concurrently (both shell out to `score.py`). A read-only replay is
`MARGIN_VERIFY_ONLY=1 py -3.13 analysis/src/margin_build/23_final_model/run.py`, which writes
nothing and prints a per-file diff — that is the mode the next auditor should use.
