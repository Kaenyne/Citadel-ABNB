# L4 v2: linked operating, financial and valuation review

Final numerical/artifact version: `data/processed/forecast_methods/lane4_model_v2/snapshot_v2/` and `model/lane4_v2/outputs/lane4_model/snapshot_v2/ABNB_L4_review.xlsx`. Information date is 13 September 2026, execution date 14 September. This is a conditional review, not an adopted target or direction.

From the L4 worktree root:

```powershell
$l4Python = 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$l4Node = 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
& $l4Python -B analysis/src/forecast_methods/lane4_model_v2/run.py --revenue-dir data/processed/forecast_methods/lane4_revenue_v2/snapshot_v1 --run-id reproduction_v1
& $l4Python -B -m unittest discover -s analysis/src/forecast_methods/lane4_model_v2 -p test_model.py -v
```

Each new run ID must not exist. The runner reproduces the legacy $180.876286 EBITDA lens and $156.786845 six-lens arithmetic mean before building the new financial model. The latter is reproduced only as historical arithmetic; no mean is used as a new target. `run.py` independently calculates the financial schedule, then `build.mjs` authors formulas with the bundled `@oai/artifact-tool`, recalculates, tests changes to inputs/missing-data behavior and captures all nine requested cases. The local `node_modules` junction points to the bundled runtime and is ignored by Git; recreate it to the loader-reported node_modules path on another host.

The single active selector is Assumptions!E4. Its nine operating cases are reference with imposed fee mechanics, without fee mechanics, K0 GBV-only, alternative nights A, ADR mean reversion, isolated net after-hedge revenue -1%/+1%, and the main conditional soft/firm envelopes. Raw case assumptions sit below the active rows. K0 GBV has no identified nights/ADR decomposition; inherited reference nights drive support costs. No old revenue take-rate/FX wedge or separate new-business revenue is added to consolidated kernel revenue. New-initiative costs are retained as inherited absolute dollars.

Case comparison is a saved snapshot from selector -> recalculate -> read -> restore. Changed inputs flag it STALE. Refresh an edited saved workbook into a NEW directory:

```powershell
& $l4Node analysis/src/forecast_methods/lane4_model_v2/build.mjs --refresh model/lane4_v2/outputs/lane4_model/snapshot_v2/ABNB_L4_review.xlsx --out model/lane4_v2/outputs/lane4_model/recapture_new
```

The main horizon is **13 September 2027**, twelve months from the frozen information date. Net cash and diluted-share proxy equal FY26 ending balance plus **256/365** of FY27 net changes, assuming uniform within-year flows. EV is full FY27 adjusted EBITDA times inherited conditional 16.5x. The separate 31 December 2027 value uses the same EV and later cash/shares. Share plans and assumed issue/repurchase prices are inherited, so share counts are identical across operating cases; editable capital assumptions can change them. The $181.94 anchor is dated 4 September 2026 and used only for share mechanics, not as a current quote/return denominator. Q2:27 onward and FY28 growth retain inherited assumptions; Q3/Q4:27 grow their scenario-adjusted 2026 bases.

Operating income = adjusted EBITDA - SBC - total EBITDA addbacks. D&A is already within total addbacks and is not subtracted twice. FCF = adjusted EBITDA + net interest - cash taxes + change in unearned fees + working-capital residual - capex. SBC-adjusted FCF subtracts SBC once from FCF. Customer funds and matching liabilities are excluded from net cash. The June 2026 starting balances use only H2 flows for FY26 cash/shares. EPS/end shares are proxies, not a separately modeled weighted-average EPS measure.

Conversion validation is complete: free-weight promotion failed W1/W2; existing fixed 2/3 K0 seasonal policy remains. New all22 free/fixed OLS coefficients are descriptive only. Main soft/firm cases use coherent operating inputs, fixed weight, assumed lambda +/-0.10pp and cushion changes. They do not combine the isolated net-revenue factor with lambda stress. Cushions change guides only. All scenario ranges are conditional envelopes, not confidence intervals. FX/RNPL source acceptance is separate from financial eligibility: matching pre-hedge baseline and H/H_new are absent, current source scope is Q3 only, and incremental FX remains null, not estimated zero.

The Summary comparison explicitly selects one Yahoo/LSEG-family Q4 revenue estimate dated 2026-09-13T15:20Z. R-S is the same-basis revenue gap. G-S compares different objects and is not guide surprise. S/(1+c) imposes the model cushion and is never labeled observed guide expectations.

## Validation and known limitations

Nine model tests pass. All 126 nine-case workbook outputs tie to Python within 3.64e-10. Formula scan finds zero errors; independent parent OOXML checks verify caches and no external links. The recapture command succeeds. All eight sheets were rendered and inspected, including both assumption regions. `render_all.mjs` emits valid PNGs for every sheet but its bundled runtime process exits 1 after output; the reason is unresolved. This is a rendering-process limitation, not a passed exit status. Calculation/export/recapture exit 0. Logs and development failures remain preserved. See final QA receipts and the L4 model note.

## RESUME

Use snapshot_v2 plus the final QA receipt, not development outputs or the pre-final snapshot_v1. Parent owns registration and local commits; this package registers nothing. Any accepted future FX adapter requires matching certified pre-hedge denominator, explicit signed H/H_new and quarter-specific cohorts. Any conversion-policy replacement requires separate research acceptance and joint coefficients, not a descriptive fitted weight. Rebuild to a new ID, recapture scenarios, verify independent financial tieouts, and inspect output images before changing the final artifact designation.
