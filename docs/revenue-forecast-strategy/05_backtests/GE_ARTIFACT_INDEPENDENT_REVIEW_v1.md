# GE artifact independent review v1

Date: 2026-09-15. Reviewer: roadmap_auditor, independent of the workbook author. Scope: the saved Excel workbook's numerical values, formula dependencies, chart sources/caches, and analytical claims. This review does not independently assess the two-page PDF's rendering or approve a trade.

## Verdict

**PASS for the specified numerical and claim scope.** The final workbook is the native-Excel-refreshed file with SHA256 `76eb08303679e32d00149bae53502749d0ced8e37a3e453bc91d973194345017`. All seven charts have complete caches tied to the correct worksheet ranges. All 200 formulas have populated cached values, without Excel error cells or broken internal relationships. No unresolved numerical defect was found.

This is an artifact correctness verdict. The underlying forecast remains conditional; the historical replay and event study have not established an investable earnings edge. The workbook retains that distinction.

## Files and source closure

Repository-relative paths below resolve from this worktree's root.

| File | SHA256 at final review |
|---|---|
| `outputs/gbv-event-20260915/ABNB_GBV_guidance.xlsx` | `76eb08303679e32d00149bae53502749d0ced8e37a3e453bc91d973194345017` |
| `outputs/gbv-event-20260915/artifact_inputs.json` | `17354476a0597a1d78389cd4b75eee50d5b6b38ff5fe3e088f59e667489e32e6` |
| `analysis/src/forecast_methods/gbv_event_v1/artifacts/build.mjs` | `60a1bb2835d459037dea18589247dc066935a0ae26e1b92450bab71dc5b03fbf` |

The eight files in the artifact payload manifest match their hashes. The nine upstream source hashes recorded by `integration_v2/model.json` also match. The model JSON is identical to the embedded model payload; every field of the seven CSV-derived payload collections was compared with its source CSV, preserving numeric, string, Boolean and missing values. The Sources worksheet retains the eight manifest paths and hashes. The canonical event source is `events_v1/run_v3`.

## Numerical and dependency checks

All monetary values here are USD millions unless stated otherwise.

| Target | Latest GBV input | Second GBV input | Revenue | Guide treatment/value |
|---|---|---|---:|---|
| 2026Q3 | 2026Q2: 27,200 | 2026Q1: 29,200 | 4,808.362929493917 | Observed midpoint 4,730 on Decision; calculated 4,723.784000645656 is only a diagnostic on Conversion |
| 2026Q4 | 2026Q3: 26,008.556 | 2026Q2: 27,200 | 3,179.343654286404 | Conditional 3,123.419115173388 |
| 2027Q1 | 2026Q4: 23,008.326 | 2026Q3: 26,008.556 | 3,055.680580442422 | Conditional 3,001.9312702955167 |
| 2027Q2 | 2027Q1: 32,424.358475969053 | 2026Q4: 23,008.326 | 4,048.395307573128 | Conditional 3,977.1841815226035 |

The four columns implement `weighted GBV = (2/3)*latest + (1/3)*second`, `revenue = weighted GBV * lambda`, and `guide = revenue/(1+cushion)`. The exact worksheet precedents use Inputs C7/C6, C8/C7, C9/C8, and C10/C9 respectively. The final Q2 calculation therefore depends explicitly on assumed Q1 2027 GBV; it does not invent a new 2027Q2 GBV input or extend the forecast horizon.

Q4 Street revenue is 3,161.02149. With the default assumed Street cushion, its guide proxy is 3,105.4192370896376. The conditional dollar gap is **17.999878083750446**; the relative gap is **0.005796279571134377**, or approximately 0.5796%. The revenue-equating Q3 GBV threshold is **25,780.296790209697**, a change of **-0.008776312294704214**, or approximately -0.8776%. The corresponding conversion change is **-6.938714561976478 basis points**. These thresholds hold other inputs fixed and compare with revenue expectations; they are not observed Street GBV/conversion expectations.

Street cushion Inputs C53:C56 are separate input values. Conversion row 17 references them rather than our cushion row 12. Changing our cushion alone therefore does not silently move the benchmark. The shared-cushion cancellation claim applies only when both values are equal. Q1/Q2 2027 Street revenue and all direct guide expectations remain absent; dependent comparisons remain text `n.a.`. Q3's future-guide comparisons are marked `Already issued`.

All 25 Q4 sensitivity cells independently reconcile with the GBV and conversion perturbations. Builder inspection confirms local guards for nonpositive conversion/GBV and cushion <= -1. Its perturbation assertions cover valid zero cushion, missing cushion, missing Q1 GBV, zero lambda, zero latest GBV and cushion -1, with input restoration. Those are author-run tests; this reviewer separately inspected the final saved formulas/caches and verified the resulting default state.

## Historical audit and event presentation

- The six RMSE cells match the frozen all-three-method paired interval-score rows, with W1 n=12 and W2 n=10. The guide-growth baseline is superior to the candidate in W2. No successful promotion is claimed.
- The six diagonal variance entries and two covariance contributions match the source moments. Their two formula totals reconcile with the source population variance. Every one of the 12 event-level Shapley decompositions sums to raw guide error. Covariance is included rather than assuming independent error components.
- The workbook explicitly identifies the historical replay as the frozen **ex-COVID** conversion variant and the current four-quarter working path as seasonal **EWM**. It expressly says the replay's errors are not a direct backtest or calibrated interval for the current EWM path. Oracle-GBV improvement remains an ex-post diagnostic, and W1/W2 are described as nested historical samples rather than a new holdout.
- Event data includes all 23 dated earnings events, including events without a numeric guide or admissible consensus. All 391 displayed event data fields reconcile with the canonical event source, including missing observations. The 23 close-to-close excess returns reconcile with separate ticker compounding rather than addition of the excess gap and session returns.
- The scatter plots use all 16 available published-guide/revenue-proxy observations. They do not condition on large realized stock moves. The four association rows correctly display n, Pearson correlation, slope and slope confidence bounds from the all-event source rows; all displayed slope intervals include zero.
- The narrative labels guide/revenue comparisons as proxies, separates the after-release signal from the already-completed gap, avoids call-leg attribution without intraday data, and does not assign a calibrated stock-price target or a net trading-performance claim.
- Input notes retain shared ancestry from the prior component-derived L4 scenario, rather than presenting the GBV input as independent confirmation. No second discretionary RNPL/fee/FX haircut is added.

## Saved chart verification

| Chart | Saved category/X values | Saved Y values | Observations per series |
|---|---|---|---:|
| Four-quarter path | Decision B10:B13 | C10:C13; D10:D13 | 4 |
| Conditional revenue and implied guide | Conversion H6:H9 | I6:I9; J6:J9 | 4 |
| Guide error | Forecast audit B6:B8 | C6:C8; D6:D8 | 3 |
| Correlated errors | Forecast audit B16:B19 | C16:C19; D16:D19 | 4 |
| Published-guide proxy versus gap | Event study I6:I21 | J6:J21 | 16 |
| Published-guide proxy versus session | Event study I6:I21 | K6:K21 | 16 |
| Full earnings universe | Event study B49:B71 | C49:C71; D49:D71 | 23 |

The final OOXML has 24 populated category/value caches. Every cached point, including both scatter X ranges, equals its referenced worksheet value. No external-workbook link parts were found. The ZIP integrity check and all final internal relationship checks pass.

## Findings resolved before final review

1. Division guards were missing from break-even and sensitivity formulas for zero lambda, zero latest GBV, or cushion -1. The author added the guards and perturbation assertions before the reviewed final export.
2. The Street cushion originally moved with our cushion. The author separated the assumptions and verified benchmark invariance when only our cushion changes.
3. Raw artifact-tool export had correct chart references but empty chart caches in all seven charts. The final native Microsoft Excel 16 refresh populated every cache. The reviewer independently verified the post-refresh file rather than accepting a successful-save message as sufficient evidence.
4. A sentence added rounded variance components as though they reconciled exactly. The author replaced it with a reference to the exact cells and the correctly rounded total, 4,027.3 USDm squared.
5. An optional renderer shutdown failed after outputs were written. This was a distinct runtime issue, not evidence of corrupted workbook numbers. The author separated optional rendering from the default author/export command, which then completed successfully. The earlier native Excel sandbox logon-session failure was also retained by the author and resolved by a scoped native refresh. Neither failure is represented as a successful initial run.

`outputs/gbv-event-20260915/native_excel_checks.json` records the author's Microsoft Excel COM 16.0 validation: guide/gap tie-outs, observed Q3 guide, input propagation, zero versus missing cushion, fixed expectation benchmark, restoration and seven chart refreshes. This reviewer did not personally operate Excel COM; independent verification used the saved OOXML.

## Review method and limits

Read-only Python standard-library audits used `zipfile`, `xml.etree.ElementTree`, `csv`, `json`, `hashlib`, `math` and `posixpath`. PowerShell supplied the audit programs as here-strings to the repository Python executable. The following compact command rechecks the delivered identity, ZIP integrity and populated chart-cache counts; it is a receipt check rather than a substitute for all numerical comparisons described above:

```powershell
@'
from pathlib import Path
import hashlib, zipfile, xml.etree.ElementTree as E
p = Path(r'C:/Users/wille/Desktop/Citadel - ABNB/.worktrees/submission-readiness-v1/outputs/gbv-event-20260915/ABNB_GBV_guidance.xlsx')
assert hashlib.sha256(p.read_bytes()).hexdigest() == '76eb08303679e32d00149bae53502749d0ced8e37a3e453bc91d973194345017'
ns = {'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'}
with zipfile.ZipFile(p) as z:
    assert z.testzip() is None
    charts = [s for s in z.namelist() if s.startswith('xl/charts/chart') and s.endswith('.xml')]
    assert len(charts) == 7
    counts = [int(e.attrib['val']) for s in charts for e in E.fromstring(z.read(s)).findall('.//c:ptCount', ns)]
    assert len(counts) == 24 and min(counts) > 0
print('Final workbook identity, ZIP integrity and chart-cache counts pass.')
'@ | & 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -
```

The initial comprehensive audit completed **25,152 assertions**, including a full scan of styled/blank cells for Excel error types, formula-cache checks, source hashes, CSV payload equality, exact numerical reconciliation and chart references. After the author's native refresh, a bounded final audit completed **20,229 assertions**, again including exhaustive error-cell scanning, while checking the changed saved structure, 200 formula caches, default forecast state, populated chart caches and relationship targets. These counts are implementation checks, not additional financial observations or statistical evidence. Analytical sample sizes remain 12/10 forecast targets and 23/16/15 event/proxy observations as described above. Additional parameters fitted by this review: **zero**.

The reviewer did not modify the workbook, builder, registry, scorers, frozen data or event-model files. The author owns visual QA and the final delivery instructions. Rebuilding the raw export alone does not reproduce the native-refresh chart caches; delivery instructions must include the refresh step or label that limitation. This note's approval applies to the exact final workbook hash above.

## RESUME

The workbook's numerical, dependency, source, chart-cache and analytical-claim review is complete with no open blocking finding. Deliver the exact hashed native-refreshed workbook after the parent's visual/PDF checks and delivery note are complete. Preserve the conditional forecast and failed-promotion language; maintain the four-quarter scope. If changing any inputs or rebuilding the workbook, re-run the relevant perturbation checks and refresh/cache verification before treating the resulting file as covered by this review. The next research decision concerns point-in-time guide expectations and prospective forecast/trade evidence, not additional cosmetic workbook checks.
