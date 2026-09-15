# L4 revenue v2 — accepted L3 integration and expectations basis

Execution 14 September 2026; information snapshot 13 September 2026. Worker B, `/root/l4_reconciliation`. Starting L4 commit `29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`. Parent preregistration: `L4_INTEGRATION_PREREG_v2.md`. New source/output paths only; no registration, scorer, commit or source estimation by this worker.

The reference Q4 revenue remains **$3,179.343654 million** and its conditional guide remains **$3,123.419115 million**, using a 1.790491031% trailing-eight median cushion. Accepted L3 evidence supports retaining the existing fixed 2/3 K0 seasonal policy after free-weight promotion failed. It supplies no financially eligible central FX adjustment. The primary observed expectations comparison is **+$18.322164 million revenue, +0.579628%**, against captured Yahoo/LSEG revenue consensus. Explicit dated expectations for management's guide are unavailable.

## Immutable sources and adoption

Consumed only the source worker's immutable copies under `data/processed/forecast_methods/lane4_sources_v2/snapshot_v1/`. Accepted bundle commit is `8821961853e4068febbfe2712f9a4e1036c9e629`; research source is `7fb6fe0f248d5492b899672b9b70545da62d63ee`. Manifest SHA-256 is `9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970`. This runner independently rechecks all 108 manifest hashes; the source worker separately verified 104 source-lineage objects and 32 acceptance bindings against Git bytes. Integrity verification is not independent statistical refitting. No changing L3 worktree or optional supplement was read.

| Accepted chronological comparison | W1 | W2 |
|---|---:|---:|
| Matched free-weight USD revenue RMSE, $m | 63.197127 | 57.392447 |
| Matched fixed 2/3 OLS USD revenue RMSE, $m | 54.227498 | 56.515722 |
| Free/fixed ratio | 1.165407390 | 1.015512948 |
| Matched targets | 14 | 10 |
| Preregistered promotion | FAIL | FAIL |

The matched fixed OLS counterfactual is distinct from K0's existing EWM/selection policy. Neither the free nor fixed all-history OLS coefficients replace that policy. W2 is nested in W1. Historical origins are letter-close and include the just-printed prior quarter's GBV; they are not before-release forecasts using predicted GBV. Today's Q4 forecast needs unprinted Q3 GBV, and future guide cushion is uncertain. L4 adds zero fitted parameters and zero new historical validation observations. Baseline inherited lambda training n is five for Q3/Q4 and six for Q1; cushion n is eight.

## Unchanged operating benchmark

USD millions; these are conditional review objects, not adopted forecasts. ADRv3 with-K replaces without-K in the explicit nights-times-ADR input; no additive take-rate, fee, cancellation, FX or RNPL wedge is applied.

| Target | Reference revenue | Conditional guide | Input timing |
|---|---:|---:|---|
| 2026Q3 | 4,808.362929 | 4,723.784001 | Uses printed Q1/Q2 GBV; guide already issued, so implied guide is diagnostic |
| 2026Q4 | 3,179.343654 | 3,123.419115 | Uses forecast Q3 GBV $26,008.556m and printed Q2 $27,200m |
| 2027Q1 | 3,055.680580 | 3,001.931270 | Uses forecast Q4 GBV $23,008.326m and forecast Q3 GBV |

Q3 team nights of 146.8m and ADR $177.17 produce Q3 forecast GBV. Q4 case B nights of 131.8m and ADR $174.57 produce Q4 GBV. A change in Q3 bookings first affects Q4 revenue; a Q4 booking change first affects 2027Q1. The USD arithmetic contribution shares are computed from weighted GBV; they are neither physical booking shares nor identified constant-currency exposures.

All five original operating cases and all 15 forecast rows remain unchanged within a maximum $0.0000000000041m serialization difference. `v1_v2_baseline_reconciliation.csv` records every row. The earlier $3,059.403011m H2 guide to $3,158.227962m inherited K0 guide reconciliation remains visible: GBV +$32.580444m, seasonal-lambda policy +$2.717883m, cushion +$63.526624m, no additional overlay, no new KPI print. The separate review-with-K guide is $34.808847m below the inherited K0 conditional guide because its explicit operating GBV differs.

Q3's already-issued midpoint is $4,730m, range $4,690–4,770m, issued 6 August 2026. Multiplying that midpoint by median/mean cushions implies revenue of $4,814.690226m/$4,817.823947m, respectively, versus the kernel's $4,808.362929m. These remain alternative once-guided comparisons, not a silently adopted Q3 replacement.

## Expectations are compared on the same basis

Each vendor retains its timestamp and panel family; no consensus was refreshed or restamped during 14 September execution.

| Revenue consensus observation | $m | Own revenue gap, $m | Gap |
|---|---:|---:|---:|
| Yahoo Finance / LSEG family, 13 Sep 15:20 UTC, n=36 | 3,161.021490 | +18.322164 | +0.579628% |
| S&P Global via StockAnalysis, 10 Sep date-only, n=35 | 3,160.000000 | +19.343654 | +0.612141% |
| Zacks, 11 Sep date-only, n=10 | 3,200.000000 | −20.656346 | −0.645511% |

For Yahoo/LSEG, own guide minus revenue consensus is **−$37.602375m**, a different-object diagnostic, not a measured guide surprise. Imposing exactly the same 1.790491031% cushion on Street revenue produces a **hypothetical** Street guide of $3,105.419237m and conditional same-basis guide gap of **+$17.999878m**. This transformation is not an observed consensus guide. `hypothetical_street_cushion.csv` also exposes zero, mean and legacy 3.88% Street-cushion assumptions; the comparison changes when the Street-cushion assumption changes. Neither arithmetic sign establishes a tradeable guide edge.

## Main fixed-kernel conditional scenarios

These cases preserve fixed 2/3 and inherited seasonal estimation. The assumed lambda shifts are **±0.10 percentage point**, not fitted uncertainty bounds. The soft case replaces the full ADR input once with the existing residual mean-reversion scenario and uses legacy 3.88% Q4 cushion, trailing-eight mean elsewhere. The firm case uses existing Q4 case-A nights and median cushion. Both retain net revenue factor 1. The lambda stress can already absorb unspecified conversion effects; generic net revenue, fee, cancellation and FX overlays are therefore excluded from these combined cases.

| Case | Q3 revenue / guide, $m | Q4 revenue / guide, $m | Q1 revenue / guide, $m |
|---|---:|---:|---:|
| Reference | 4,808.363 / 4,723.784 | 3,179.344 / 3,123.419 | 3,055.681 / 3,001.931 |
| Soft: ADR mean reversion, lambda −0.10pp, stated cushion | 4,780.496 / 4,693.353 | 3,103.871 / 2,987.939 | 2,960.167 / 2,906.206 |
| Firm: case-A nights, lambda +0.10pp, median cushion | 4,836.230 / 4,751.160 | 3,205.749 / 3,149.360 | 3,093.125 / 3,038.717 |

The conditional Q4 revenue gap to Yahoo/LSEG ranges from −$57.150100m to +$44.727868m in these three named cases. This illustrates that the reference +$18.322164m comparison does not survive all stated assumptions with the same sign. The main envelope is a range over these cases only, without probability, confidence or coverage claims. Q3 guides in every case remain diagnostics. `joint_scenario_bridge.csv` reconciles each case sequentially through GBV replacement, lambda stress and cushion replacement. No annual number is created by compounding an unseasonal quarter.

Isolated net-after-hedge revenue ±1% sensitivities are separate in `net_revenue_sensitivity.csv`: Q4 revenue ±$31.793437m and guide ±$31.234191m at unchanged cushion. These are explicitly illustrative consolidated net revenue changes, not measured FX/RNPL effects, and are not compounded with the lambda stress cases.

## Rejected-model joint sensitivity is a separate exhibit

All 1,000 existing L3 year-block resampling draws are consumed intact: one shared w and all four seasonal lambdas, including source draw ID, selected years, sample n and parameter count. The reference operating GBV, median cushion and net factor 1 are held fixed. No independent marginal endpoints are combined, no fit is run, and no rejected-model draw enters the main financial cases.

| Descriptive fitted-model tuple | Q4 revenue, $m | Q4 guide, $m |
|---|---:|---:|
| Full all22 free-weight point, not adopted | 3,180.853103 | 3,124.902013 |
| Minimum Q4 result among existing draws, draw 706 | 3,135.132989 | 3,079.986114 |
| Maximum Q4 result among existing draws, draw 542 | 3,308.262349 | 3,250.070135 |

The same selected tuple projects Q3/Q4/Q1 together. Q4-extreme tuples do not necessarily produce Q3/Q1 extremes. Six year blocks and 1,000 resamples do not provide 1,000 independent years. This is fitted rejected-model sensitivity, not a K0 parameter band or full predictive range; it omits residual outcomes, forecast GBV error and future cushion uncertainty. The full22 five-parameter result does not establish current physical recognition shares.

## FX/RNPL eligibility and source precision

The source worker classifies all 1,187 bundle rows with original fields retained in `row_dispositions.csv`. No row is a directly measured current ABNB revenue-cohort parameter. L3's FX implementation and conditional arithmetic are accepted as research. Its 180 scenario identities reconcile, but no current baseline is financially eligible:

1. The source ratio T/B is not certified on a matching pre-hedge revenue basis.
2. Baseline signed revenue hedge H and scenario H_new are absent. H_new=H is not silently assumed.
3. Reference GBV/currency shares, recognized RNPL revenue share and timing allocations are conditional rather than measured.
4. Source current-target coverage is Q3 only. Q4/Q1 target-specific cohort/rate inputs are absent; no extrapolation occurs.

The guarded interface requires `R_new=m_pre*(R-H)+H_new`, compatible reference and cohort inputs, and explicit evidence/accounting definitions. Signed positive/negative hedge and changed-hedge tests prevent multiplying embedded hedge dollars or silently guessing zero. An after-hedge ratio is refused as pre-hedge. Payment, FX fixing, recognition and guide dates remain distinct. Accepted source-only Q3 timing diagnostics (flat cached FX, assumed 56% non-USD share and 20% RNPL revenue share) show deltas of −$2.434476m for equal recognition months, −$7.931654m for first month, +$1.274079m for last month, and −$5.090603m for the prior-month payment/fixing hypothesis. They are not applied to the forecast. Unresolved estimated FX remains null; holding the baseline is not estimating economic FX as zero.

The QVS source-precision audit independently attributed the [Q2 filing table](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm): Q2 GBV $27,247m and H1 $56,434m imply Q1 $29,187m, versus frozen $27,200m/$29,200m. This package reads the verified QVS copy, not a refreshed filing or changed panel. A separate partial precision sensitivity, holding K0's rounded-panel calibration fixed, adds $27m to Q3 weighted GBV and $15.666667m to Q4 weighted GBV:

| Target | Revenue delta, $m | Guide delta, $m |
|---|---:|---:|
| 2026Q3 | +4.658821 | +4.576872 |
| 2026Q4 | +1.886324 | +1.853144 |
| 2027Q1 | 0 | 0 |

These are precision accounting comparisons, not a new forecast or new calibration. ADR card denominators and original reported rows remain unchanged. Fee-panel theta is unavailable (0 of 6 scheduled captures); NCLH transfer fails and adds no ABNB adjustment; hotel evidence remains a comparator. ADR total effects already embed FX/fee mechanics; coherent replacements prevent summing overlapping drivers.

## Reproduction, validation and retained failures

From the isolated worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/lane4_revenue_v2/run.py
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -m pytest analysis/src/forecast_methods/lane4_revenue_v2/tests -q -p no:cacheprovider
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/lane4_revenue_v2/run.py --output data/processed/forecast_methods/lane4_revenue_v2/rebuild_01
```

The final default snapshot already exists, so invoking the first command again must refuse. Choose a new output ID to rebuild. Validation receipt and exact command logs: `data/processed/forecast_methods/lane4_revenue_v2/validation_v1/validation_receipt.json`.

| Check | Result |
|---|---|
| Arithmetic, timing, input/hedge, basis and joint dependence tests | 49 passed |
| Output file hashes checked | 30 / 30 |
| Stable files reproduced byte-identically in rebuild_01 | 29 / 29 |
| Existing-output refusal | Exit 1 as required; all final bytes preserved |
| Future information-vintage refusal | Exit 1 before directory creation |
| Old-to-new baseline maximum absolute dollar difference | $4.1e−12m |
| Original legacy bridge residual | −$4.55e−13m |
| New statistical fits / adopted forecasts | 0 / 0 |

No v2 development or test failed. Successful `development_run_01` is retained; expected refusal logs are retained. The earlier v1 failed development receipt remains untouched. Source files and outputs have new scoped exact-byte Git attributes. This worker did not rerun historical research tests or scorers because it did not register forecasts.

Final snapshot identity (`data/processed/forecast_methods/lane4_revenue_v2/snapshot_v1/`):

| File | SHA-256 |
|---|---|
| `SHA256SUMS.json` | `517ca9badf1200e4eef3955abcd9766c1ace7216d909858970ed9b87fbbd5f83` |
| `forecast.csv` | `44381e679cc41d2ae7d952bbad78e2a2008392eeb085451ac8130b4ae509e397` |
| `expectations_comparison.csv` | `d1588d403a7771db5eb4ee65fd52e40503cfaf524ffef320d68f0c23069280a9` |
| `joint_scenarios.csv` | `76a15e37371c530d08ab895aa4f72b5bbe56153b804717d2351be4912567b662` |
| `descriptive_joint_draws.csv` | `f895fba9e400bf8bf8a5f317333ab941bf7efb8999cd90687cc4e19ebb8ce0a6` |

## RESUME

Consume final snapshot_v1 for workbook, memo and decision integration. Keep main fixed-kernel scenarios separate from the rejected-model draw exhibit and isolated net revenue sensitivity; retain vendor timestamps and unavailable guide expectations. The model owner handles financial statements and the explicit 13 September 2027 cash/share horizon. Parent owns independent integration review, forecast registration decisions and local commit. A future financial FX application requires a newly supplied immutable compatible accounting supplement; no competing L3 estimation or silent overlay is authorized. This worker rotates to independent model/memo mathematics and horizon review after revenue completion.
