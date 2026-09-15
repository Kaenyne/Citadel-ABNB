# L4 v2 financial model integration

14 September 2026. Information frozen 13 September 2026. New files only in the L4 worktree; zero newly fitted parameters, registrations or commits by this worker.

## Result

Final workbook: `model/lane4_v2/outputs/lane4_model/snapshot_v2/ABNB_L4_review.xlsx`. Final inputs, annual/scenario outputs and formula tieout: `data/processed/forecast_methods/lane4_model_v2/snapshot_v2/`. Revenue input is the immutable `lane4_revenue_v2/snapshot_v1`; accepted L3 source is `lane4_sources_v2/snapshot_v1` extracted from bundle commit `8821961853e4068febbfe2712f9a4e1036c9e629` (research `7fb6fe0f248d5492b899672b9b70545da62d63ee`).

The new same-basis headline is Q4 revenue R=$3,179.343654m versus Yahoo/LSEG-family revenue S=$3,161.021490m, captured 13 September 2026 15:20 UTC: **R-S=+$18.322164m / +0.579628%**. The guide G=$3,123.419115m uses an assumed cushion. G-S=-$37.602375m compares different objects, not measured guide expectations. S/(1+c)=$3,105.419237m is hypothetical, not observed guide consensus. The explicit vendor/timestamp selector is unique and cannot accidentally select the older S&P source.

| Conditional case | Q4 2026 guide, USDm | FY27 revenue, USDm | FY27 EBITDA, USDm | FY27 FCF, USDm | 13 Sep 2027 value/share |
|---|---:|---:|---:|---:|---:|
| Soft envelope | 2,987.939343 | 15,741.165543 | 5,625.060886 | 5,364.484940 | $177.329623 |
| Reference with fee mechanics | 3,123.419115 | 15,952.233241 | 5,807.532522 | 5,536.825326 | $182.867016 |
| Firm envelope | 3,149.360344 | 16,049.945718 | 5,899.671105 | 5,624.273710 | $185.680568 |

These are three assumed envelopes within a nine-case model, excluding the two isolated net-revenue sensitivities. Soft combines ADR mean reversion, an assumed -0.10pp lambda shift, fixed2/3 and a 3.88% Q4 cushion; firm combines alternative nights A, +0.10pp lambda and median cushion. The net factor is one in both; no overlapping generic FX shock is compounded. Cushion changes the guide only, not earnings/cash. The envelopes are not confidence intervals and have no probabilities.

## Financial and horizon conventions

The principal horizon is **13 September 2027**, exactly twelve months from the information date. FY27 full-year EBITDA times inherited conditional16.5x gives EV=$95,824.286607m. FY26-end cash/shares plus256/365 of FY27 net changes, assuming uniform within-year flows, gives cash=$10,029.055795m and shares=578.854211m; equity=$105,853.342402m and value=$182.867016/share. The separate31December2027 comparison is $184.662755 with the same EV and later balances; the $1.795739 difference is date-only. No target average, causal +0.48 multiple mechanism, direction or probability is adopted.

The core financial model retains inherited processing/support, fixed operating costs, SBC, addbacks, D&A, taxes, capex, working capital, repurchases and issuance. All consolidated revenue construction in the three supported quarters is the imported kernel; no old take-rate/FX wedge or new-business revenue overlay remains. Inherited initiative costs remain. D&A is within total EBITDA addbacks; operating income subtracts SBC and total addbacks once. FCF is adjusted EBITDA plus net interest minus cash taxes plus change in unearned fees plus working-capital residual minus capex; SBC-adjusted FCF subtracts SBC. Customer funds are excluded. After the June2026 balance anchor, only H2 flows are added for FY26.

The $181.94 price anchor is the inherited4September2026 repurchase/issuance price, not current spot or return denominator. Ending shares and EPS are proxies; scenario share counts stay fixed under the inherited capital plans. Q2:27+ and FY28 growth are inherited, with Q3/Q4:27 growing changed2026 bases. K0-only GBV lacks a unique nights/ADR decomposition; reference nights remain the explicit support-cost proxy.

Conversion validation is complete and free-weight promotion failed W1/W2 (ratios1.165407/1.015513, n14/10). Existing operational fixed2/3 K0 seasonal policy stays. Neither free-w nor newly fitted all22 fixed-OLS coefficients is adopted. Accepted FX implementation remains ineligible for current financial application: source Q3 reported baseline matches, but pre-hedge certification, H/H_new and Q4/Q1 cohorts are absent; assumed RNPL/currency/recognition shares are not measured. Missing incremental FX is not zero.

## Reproduction and checks

From the worktree root (bundled Node/node_modules and Python paths are in README):

```powershell
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B analysis/src/forecast_methods/lane4_model_v2/run.py --revenue-dir data/processed/forecast_methods/lane4_revenue_v2/snapshot_v1 --run-id snapshot_v2
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -m unittest discover -s analysis/src/forecast_methods/lane4_model_v2 -p test_model.py -v
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe' analysis/src/forecast_methods/lane4_model_v2/build.mjs --refresh model/lane4_v2/outputs/lane4_model/snapshot_v2/ABNB_L4_review.xlsx --out model/lane4_v2/outputs/lane4_model/validation_recapture_v1
```

The final run ID exists; use a new ID to reproduce. All9 unit tests pass. The single active selector is changed/recalculated/captured/restored for nine cases; all126 output checks agree with independent Python within3.64e-10. Missing active versus inactive inputs, valid zero versus unestimated, timing of nights, later costs and stale captures are checked. Legacy arithmetic independently reproduces $180.876286421 and $156.786844934 to$0.001 before the new model. Parent OOXML review found1875 formulas, zero formula errors/external links and316 cache checks within7.375e-6 (legacy source rounding). B independently reconciled759 checks across all quarters/27annual rows within2.91e-11; A checked source/financial bindings independently. See their review notes and final QA receipt.

All eight sheets were visually reviewed; Case comparison includes fully formatted columnM and metadata moved outside the visible area toZ1. The workbook exports/recalculates; nine-case recapture is checked. The artifact renderer writes all PNGs then exits1 without an explanatory error, an unresolved bundled-runtime limitation also seen in v1. It is not reported as a clean renderer exit. PNGs were independently opened and inspected. Initial development failed on a typographic apostrophe converted into unescaped code; corrected, with its failed log/data retained. The pre-final snapshot_v1 was a mutable draft, including an in-place layout iteration before the parent's preservation instruction; snapshot_v2 is the frozen final.

## RESUME

Use snapshot_v2 and `final_QA.json`; do not use the development or pre-final snapshot as the deliverable. The final memo binds this version. Parent owns local integration/commits and any registrations; this worker registered nothing. New accepted research may change eligibility, not silently overwrite coefficients or zero missing FX. Rebuild a new version, preserve coherent inputs, independently tie earnings/cash/shares at the declared date, recapture all cases and inspect images before changing the final designation.
