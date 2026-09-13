# R — Regional reconciliation refresh

partial — the refresh reproduces 72/72 exact revenue cells, but the 2024 ex-FX ADR residual is still −1.394pp and regional ADR intervals exceed ±10%. Agent sub-R, 2026-09-12 (local date), branch `codex/lane1-full`. No historical arrivals coefficient survives the vintage requirement; no FY27 forecast edge is established in W1 or W2.

## Pre-registered pass line

Gate G2 must reproduce all 72 exact regional revenue cells. The maximum absolute annual ex-FX ADR residual against the supplied ADR anchors must improve to less than 0.8 percentage points in every comparable year, or the failure must be explained. Regional ADR levels must be identified to better than ±10%. A bootstrap conditional on anchor priors does not establish identification; sensitivity to prior strength and observational rank will be reported separately.

Arrivals may enter the historical model only with a documented public release date strictly before the guide origin. Current downloads without historical release vintages may be used for a labelled live/descriptive sensitivity but never relabelled PIT. Selection requires better rolling out-of-sample regional nights error in both W1 and W2 on matched available cells; otherwise no arrivals series earns a forecast coefficient. Five-series scouting does not justify automatic selection.

FY27 output is an exploratory scenario of regional nights and ADR. The exact identity GBV = total nights × blended ADR will be preserved. Geographic mix is an attribution within ADR and must not be added twice. Unit size, LOS, seats, FX and the remaining price/subregional-mix term are non-additive attribution lines. Assumed channels will remain labelled, and confidence in annual revenue will not be inferred from a conditional composition bootstrap.

## What ran

The pass line above was written before the first model fit or arrivals download. New source is `analysis/src/forecast_methods/l1_reconciliation_v3/`; outputs are under `data/processed/forecast_methods/l1_reconciliation_v3/`. The copied v2 algebra and all original files remain intact. Commands below use the project virtual environment from the repository root:

```text
python analysis/src/forecast_methods/l1_reconciliation_v3/fetch_arrivals.py
python analysis/src/forecast_methods/l1_reconciliation_v3/run.py --bootstrap 40
python -m pytest analysis/src/forecast_methods/l1_reconciliation_v3/test_refresh.py -q
```

The downloader exited 0: seven public endpoints returned HTTP 200. The first completed core build exited 0 in 115.39 seconds; the final reproducibility run exited 0 in **169.81 seconds**, reproducing the same numbers, with all 40 requested bootstrap fits retained and convergence checked. That build's tests passed all **five tests in 2.06 seconds**, including historical exclusion of the undated current FX-slope estimates. Development receipts: an initial run exited 1 because this new loader used `quarter` instead of the frozen calendar's `print_quarter`; that interface bug was fixed. An intermediate bootstrap run was interrupted after excessive small-matrix BLAS threading; the final command explicitly limits BLAS to one thread. Neither attempt was reported as a passed run. No scorer was run by this package.

Parent subsequently rejected the registration dates, as detailed below. The one correction attempt passed **seven tests in 2.59 seconds** and `python -X utf8 analysis/src/forecast_methods/l1_reconciliation_v3/run.py --candidates-only` exited 0 in **2.02 seconds**. This path performs zero regional model refits and creates only local candidates and registration status. All 12 point values match the preserved rejected rows within 1e-10; all 19 pre-existing analytical output files remain byte-identical. `registration_correction_receipt.json` records these checks.

The core model has 57 fitted parameters (three share logits per quarter × 18 quarters, plus three persistent regional take-rate tilts), 127 interval disclosure constraints and 16 soft annual ADR anchors. The four EWM kernel coefficients are supplied by K0 v2, giving 61 parameters in the local candidate metadata. Intervals and anchors are correlated; their count is not an effective independent sample size. Hyperparameters are fixed rather than selected on the reported results: 5% log-ADR anchor scale, inherited smoothing/ridge, four-quarter blocks, seed 20260912, 40 refits. Sensitivity uses 2.5%, 10%, and effectively no ADR anchor.

## Results

G2 matches 72/72 cells from `L0_exact_regional_revenue.csv`; maximum absolute error is **2.27e−13 USD millions**, across 18 quarters and four regions. Total quarterly GBV and Nights-and-Seats also close. This is an exact **accounting identity by construction**, not an out-of-sample validation of regional GBV, take rates or arrivals.

Annual ex-FX ADR comparison, full-sample, four regions and four quarters in every row (`annual_adr_residuals.csv`):

| Year | Within-region ex-FX, pp | ADR-note comparator, pp | Residual, pp | Under 0.8pp? |
|---|---:|---:|---:|---|
| 2023 | 2.8185 | 3.10 | −0.2815 | Yes |
| 2024 | 2.0457 | 3.44 | **−1.3943** | **No** |
| 2025 | 3.3999 | 3.41 | −0.0101 | Yes |

The comparators are the three annual within-region ex-FX terms reported in the named `l1-reconciliation.md` §4. They were not fitted as anchors. Annual **levels** are shrunk toward `01_regional_annual.csv`; the reported/ex-FX attribution uses disclosed regional FX pairs where available and the existing basket elsewhere. Shrinking ADR levels does not settle the competing regional-versus-consolidated FX allocation that generated the old 2024 discrepancy. The residual is left visible and no calibration plug is introduced. This R package does not supersede X's regional FX recomputation.

Regional ADR identification fails the pass line (`regional_adr_intervals.csv`, `anchor_sensitivity.csv`): the largest conditional p10–p90 relative halfwidth is **25.69%**, in Latin America 2025Q1 (p10 $131.82, median $155.25, p90 $211.60; n=40 refits). The largest movement from changing/removing annual-anchor strength is **34.62%** across the 72 regional quarter cells. The local observational interval Jacobian has rank **57/57**, with zero numerical null dimensions at the fitted point; full local rank does not imply narrow uncertainty or validate the assumed persistent regional take-rate structure. These are conditional model diagnostics, not proof that each regional price is empirically identified.

Bootstrapping exact identity residuals gives a **zero-width band**, because those residuals are exactly zero. That degenerate result is recorded in `diagnostics.json`, not represented as precision. The nonzero bands below instead come from four-quarter reweighting and refitting of the disclosure residuals, preserving the identities in every draw.

## FY27 attribution and kernel sensitivity

All ADR attribution rows have **zero additional weight** in total revenue; they explain the ADR factor inside the identity `GBV = nights × blended ADR`. Projection growth assumptions are carried from the supplied regional forecast file, not selected or adopted as team decisions. The intervals are conditional composition p10/p90 from 40 converged block refits; they exclude growth-scenario, FX, lambda and booking-path forecast uncertainty.

| FY27 ADR attribution | Point, pp | Conditional p10 / p90, pp | Basis and n |
|---|---:|---:|---|
| Geographic mix | **−1.0650** | −1.1932 / −0.9740 | Computed share identity; n=40 |
| Within-region reported ADR | +3.0000 | +3.0000 / +3.0000 | Fixed common growth assumption; n=40 identical scenarios |
| Mix × price cross | −0.0320 | −0.0358 / −0.0292 | Computed; n=40 |
| **Blended ADR subtotal** | **+1.9030** | **+1.7710 / +1.9968** | Computed; n=40 |
| Unit-size mix, within the +3pp | +0.63 | +0.63 / +0.63 | Carried assumption; no estimated sampling interval |
| LOS, within the +3pp | +0.04 | +0.04 / +0.04 | Carried assumption; no estimated sampling interval |
| Seats/hotel composition | 0.00 | 0.00 / 0.00 | Composition held flat in this actual build |
| FX y/y carry | 0.00 | 0.00 / 0.00 | Flat-yoy scenario, not a forecast that FX will be zero |
| Joint price + subregional mix remainder | **+2.33** | +2.33 / +2.33 | Arithmetic remainder conditional on those assumptions; not separately identified |

The old B3 table's −0.50pp seats assumption is not silently carried into a build that holds seats composition constant; this explains why this scenario's remainder is +2.33pp. The old assumptions are preserved in their original note.

K0 v2 EWM lambda is imported and held fixed across the kernel-weight sensitivity. Both lagged FY27 GBV inputs are forecasts. The same regional scenario is used at every weight (`fy27_kernel_band.csv`):

| Weight on GBV q−1 | FY26 revenue, $M | FY27 revenue, $M | FY27 growth | Conditional FY27 revenue p10 / p90, $M | Conditional growth p10 / p90 |
|---|---:|---:|---:|---:|---:|
| 0.33 | 14,423.4 | 15,853.7 | +9.916% | 15,824.8 / 15,859.7 | +9.725 / +9.956% |
| 0.50 | 14,332.7 | 15,914.7 | +11.038% | 15,885.3 / 15,920.8 | +10.846 / +11.077% |
| 2/3 | 14,243.9 | 15,974.6 | +12.151% | 15,944.5 / 15,980.8 | +11.959 / +12.190% |

There are **n=40 composition refits per row**. The weight range spans $15.854–15.975bn and +9.916–12.151%; it is a sensitivity range, not a probability interval. These changes versus B3 combine a different regional fit and K0's verified EWM policy; they cannot be attributed solely to annual-anchor shrinkage. No consensus comparison is used or registered.

## Arrivals: access, selection and missing coverage

`arrivals_manifest.json` records URLs, HTTP statuses, retrieval timestamps and content hashes. Only normalized public aggregates were saved; no raw workbook or ZIP is retained. The UTC retrieval date is **2026-09-13**, corresponding to the evening of 12 September locally. This date is the conservative `knowable_from` for every value in each current revised download. An observation month is not its release vintage.

| Candidate | Monthly rows | Historical coefficients admitted | Disposition |
|---|---:|---:|---|
| NTTO I-94 all source countries to US, country-of-residence basis | 66 | 0 | Current revision; excludes domestic and non-US NA activity |
| JNTO Japan inbound, all origins | 67 | 0 | Current revision; excludes domestic Japan and most APAC destinations |
| Eurostat Spain nonresident accommodation nights | 66 | 0 | Current revision; accommodation nights, not Airbnb bookings |
| Eurostat France nonresident accommodation nights | 66 | 0 | Same restriction |
| Eurostat Italy nonresident accommodation nights | 66 | 0 | Same restriction |
| Eurostat Germany nonresident accommodation nights | 66 | 0 | Same restriction |
| DataTur Cuenta de Viajeros download | 0 | 0 | HTTP 200, but only monetary receipts/expenses; rejected as a visitor count |
| Australia / Brazil complements | 0 | 0 | Not integrated; no substituted or invented counts |

Six normalized candidate series contain **397 monthly rows**. Calendar-quarter sums require exactly three months, with no partial-quarter extrapolation; a lag-one-quarter growth covariate is then fit only from date-admissible observations. The implementation can accept archived releases later. All six current-revision correlations have n=14 overlapping fitted regional growth cells, but they are explicitly retrospective descriptive diagnostics in `arrivals_descriptive_coefficients.csv`; no coefficient is included in the forecast. Inbound destination traffic is also an imperfect mechanism for origin/domestic Airbnb booking growth.

The official [NTTO methodology](https://www.trade.gov/i-94-arrivals-program) describes revisions and the country-of-residence scope. [JNTO's statistical releases](https://www.jnto.go.jp/statistics/data/visitors-statistics/) distinguish current estimates and subsequent revisions. The [Eurostat API](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-getting-started/api) delivers current data and does not turn reference months into historical release dates. The [DataTur download page](https://datatur.sectur.gob.mx/SitePages/cuentaviajeros.aspx) supplied the rejected monetary workbook. These public sources were accessed directly; no paid country file was queried.

| Window | Guide origins | Origins with an admissible arrivals coefficient | Exact cells reproduced in full-sample fit | Forecast verdict |
|---|---:|---:|---:|---|
| W1, 2023Q1–2026Q2 | 14 | **0** | 56 | Underpowered; no historical forecast replay |
| W2, 2024Q1–2026Q2 | 10 | **0** | 40 | Underpowered; no historical forecast replay |

These overlapping accounting cells are not W1/W2 prediction successes. Every candidate's forecast pass line remains untested because the downloaded revisions are unavailable at the historical guide origins. No series earned a place. This is online access with vintage limitations, not an offline-network failure.

## Registration and harness change request

**Registration correction: no R v3 rows remain in the shared registry.** The original runner incorrectly wrote two new files, `l1-reconciliation-v3__fy27_revenue.csv` and `l1-reconciliation-v3__fy27_growth.csv`, with six forward quarterly rows each, using 2026-09-11 as an admitted format slot for a later reconstruction. Parent rejected this: a `full_sample` label and explanatory caveat cannot make an inaccurate vintage acceptable. This was an implementation failure even though the numerical analysis remains a documented partial result.

The one permitted correction first preserved both rejected files byte for byte under `UNREGISTERED_rejected_registry_20260913/`, with their SHA-256 hashes, all 12 exact rejected rows, explicit rejection reason and preservation timestamp in `rejection_manifest.json`. Only those two R-owned, newly created shared-registry files were then removed, after checking their resolved absolute paths were inside the repository. The original `diagnostics.json` timestamp caveat and original `verification_receipt.json` remain unchanged as records of that rejected implementation; `registration_status.json` and `registration_correction_receipt.json` supersede their registration status.

The corrected runner has no registry-writing path. Both the full model run and `--candidates-only` write `UNREGISTERED_fy27_candidates.csv` and `registration_status.json` inside R's own output directory. The local candidates separate the financial input cutoff (2026-09-12) from the actual reconstruction timestamp (**2026-09-13T00:50:59.374312+00:00** in this correction); they do not assert a `vintage_date` or historical issuance. They retain the same six quarterly points per object, from 2026Q3 through 2027Q4, and only the four 2027 revenue rows comprise FY27. Current arrivals remain excluded, and there are no predictive quantiles or W1/W2 forecast-performance rows. Empty baseline comparisons mean **no baseline exists**, not zero error or a pass.

The frozen harness needs an honestly dated reconstruction/current-run slot and suitable annual or multi-quarter representation before these candidates can be registered. That limitation does not authorize using an earlier date. Parent owns scoring and any future promotion; this package does not modify the harness. Regression checks intercept writes outside R's output directory, forbid model refitting in the candidates-only path, check actual creation timestamps, and compare all 12 points to the preserved rejected rows.

## Proposed memo sentence

**The full-sample regional refresh matches all 72 filed revenue cells but leaves a 1.39pp gap in 2024 ex-FX ADR attribution, so its FY27 composition remains conditional.**

Evidence: `disclosure_residuals.csv`, `annual_adr_residuals.csv`, `regional_adr_intervals.csv`, `window_summary.csv`. Caveats: the revenue match is imposed by algebra; the FX split is not independently identified; neither window supplies a historical arrival-based forecast test.

## What remains undone and why

The intended sub-0.8pp residual and ±10% ADR precision were not achieved. No arrivals predictor was admitted; current revised downloads cannot supply the specified historical availability evidence. Australia and Brazil series and a verified DataTur count file were not integrated; expanding current-country coverage alone would not resolve missing historical vintages. FY27 uncertainty remains conditional on supplied growth, seats, FX and kernel specifications, so no predictive revenue interval or Street edge is claimed. The rejected misdated registrations were withdrawn and preserved; registration remains undone because the frozen schema cannot honestly represent the reconstruction date. This is a documented partial result, not a failed test deleted or an unvalidated feature promoted.

## RESUME

Preserve this result and the v2 source. A next version should first resolve the 2024 regional-versus-consolidated FX attribution and acquire actual archived release vintages for the public arrivals candidates, then refit at each guide origin and evaluate matched W1/W2 forecast errors. Country coverage must distinguish inbound destination activity from domestic/origin booking demand. The current six descriptive coefficients and narrow FY27 composition bands cannot be promoted. Parent owns the workboard, scorer, refuters, commits and pushes. Runtime token usage is unavailable from the agent tools; no token estimate is substituted.
