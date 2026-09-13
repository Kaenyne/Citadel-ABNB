# L3 conversion validation — independent analytical review v1

Reviewer cohort_fx, independent of conversion author adr_hotel · 2026-09-13 · codex/lane3-full.
Reviewed preregistration, analytical code and first complete `results_v1` output. Publication/visual repairs are listed separately below.

## Verdict

**Descriptive calibration and chronological validation accepted; free-weight promotion FAIL.** A separate direct five-parameter solver reproduces the profiled fit across all six sample/loss specifications, and an independent chronological reconstruction reproduces the primary W1/W2 negative result. The four seasonal rates plus shared w are a defensible audited reduced-form calibration to the requested 22 quarters; w is not identified as a booking probability or actual revenue share. No production, workbook, guide, memo, valuation or trade adoption follows.

The core numerical audit is closed. Before publication, the author must complete the acknowledged chart/comparator presentation correction and the lead-requested test-import isolation repair; a subsequent receipt can verify those changes without rerunning the research acceptance rule. The first output and failures remain preserved.

## Independent fit and chronology checks

Used `scipy.optimize.least_squares` to estimate the five parameters directly, with positive coefficients, w in [0,1], three starting weights (0.1/0.5/0.9), and both specified USD and relative-error losses. This does not invoke the package's analytical profile estimator. Across six sample/loss specifications, maximum absolute w difference was **3.63e-8**, maximum coefficient difference **2.25e-9**, and SSEs agreed to floating-point precision.

| Sample | n | USD-loss w | Relative-loss w | Interpretation |
|---|---:|---:|---:|---|
| All 2021Q1–2026Q2 | 22 | 0.786478481 | 0.761633419 | Requested primary descriptive sample |
| Exclude 2021 | 18 | 0.538730547 | 0.684866409 | Regime/loss sensitivity |
| 2023Q1 onward | 14 | 0.356962970 | 0.312643585 | Regime/loss sensitivity |

The primary seasonal rates are **12.931911/13.224232/17.302744/12.111558%** (Q1–Q4), fitted jointly with w. Their variation across regimes is part of the identification result, not a reason to substitute a preferred sample after the test.

For each of the 14 historical origins, the reviewer independently built the available lagged-GBV/known-revenue rows from the frozen calendar and solved the five-parameter regression directly. The matched fixed-w comparison independently used the season-specific through-origin OLS identity at w=2/3. Training count rises from 8 to 21. This reconstruction did not call the package's `predict` or `fit` functions for its primary chronological estimate.

| Window | n | Independent free RMSE, $M | Independent fixed RMSE, $M | Free/fixed ratio | Hurdle |
|---|---:|---:|---:|---:|---|
| W1 | 14 | 63.197127 | 54.227498 | 1.165407 | FAIL |
| W2 | 10 | 57.392447 | 56.515722 | 1.015513 | FAIL |

The final package results differ from the direct solver by less than $0.000001M of RMSE. The extra parameter improves descriptive in-sample fit but does not beat the identically fitted fixed benchmark chronologically on either window. Retaining the existing operational fixed specification is consistent with the preregistered rule; the new all22 fixed OLS coefficients are not silently promoted as its substitute.

## Information sets and matched comparisons

At 2023Q1, 2024Q2 and 2026Q2, replacing target/future revenue and GBV by 1e12 leaves the tested current-origin predictions unchanged (n=3 perturbations). Same-day prior-quarter prints are correctly admitted; target-quarter outcomes/GBV remain excluded. The available-date validation and target-present rejection tests pass.

All five frozen registry comparators' W1 subsets exactly match their separately registered W2 rows on quarter, vintage date and point (n=10 each): legacy season mean, legacy last3 excluding 2021, naive, AR(1), guide+cushion. Therefore constructing W2 as that subset is valid for these actual inputs. Guide+cushion uses management's already-issued target guide; it remains an explicitly advantaged post-guide revenue benchmark and gives no evidence about forecasting the guide itself.

The first attempted full runner aborted when unchanged K0 lacked an admissible same-season estimate. The repaired analytical run records **2023Q1/Q2 abstentions**: K0 n=12 in W1 and n=10 in W2. Its RMSE ratios are computed against fixed/naive errors on those same available cells, not against a larger denominator set. Main free/fixed/registry comparisons remain n=14/10. No invented K0 forecast fills the gap.

## Uncertainty, intervals and year sensitivity

Independent recalculation covered all **56 origin/model interval cells** (four new methods x fourteen origins): each band uses only errors whose actual print dates had passed, the last at most eight errors, and the conservative stated rank. The repaired calibration error is `(actual-point)/point`, consistent with symmetric `point*(1 +/- width)` bands. The original actual-denominator construction was identified by lead and corrected before the first completed research output; the algebra regression test passes. Eight eligible bands per new method yield 7/8 coverage, which is descriptive and not a guarantee of 80% coverage.

The reviewer recomputed all five parameter percentile columns from 1,000 accepted year-block draws, checked five selected draws by rebuilding their sampled year-block datasets and refitting, and verified all twelve leave-one-year-out model fits and held-out RMSEs. All agree. There is one endpoint draw (0.1%); six calendar years, including partial 2026, cannot support precise structural identification. The w percentile sensitivity is **0.307910–0.857332**, not a confidence statement about booking shares. Omitting 2021 moves USD-loss w to 0.538731; the other leave-year-out fits remain roughly 0.782–0.806. LOYO uses future years to predict an omitted earlier year and is correctly labeled sensitivity, not chronological validation.

The reviewer independently reconstructed **all 4,000 paired year-block resamples** using group error sums and the declared random seed, rather than the package's row-concatenation implementation. Draw-level ratios and MSE differences match. The 2.5/97.5 percentile ratio ranges are **0.848335–1.525124 (W1; four target-year blocks)** and **0.806881–1.135943 (W2; three blocks)**. Both span one. The windows overlap and are not independent confirmations; neither narrow-sample significance nor a precise win probability is justified.

The five-percent-above-minimum profile ranges are explicitly grid-labeled in `profile_flatness.csv`. Independent continuous root solving gives USD-loss intervals 0.695881–0.877052 (all22), 0.388796–0.692912 (exclude2021) and 0.216731–0.506263 (2023plus); the reported 0.005-grid interiors are consistent. These are loss flatness diagnostics, not confidence intervals.

## Implementation and presentation findings

Twenty-one analytical/integrity tests pass independently in 2.71 seconds. They cover exact coefficient/weight recovery including boundaries, units, nonfinite inputs, season coverage, 22-row reconciliation, future and missing observations, duplicate/undated data, explicit target exclusion, interval algebra, deterministic fitting and immutable output refusal.

Two integration/presentation items were raised after numerical acceptance:

1. The first chart's W1 raw-RMSE panel mixed K0's 12 available cells with the other models' 14 cells. A count qualifier helps, but it is still not a matched absolute-RMSE comparison. The author accepted replacement with the full-coverage legacy last3 operational comparator, while keeping K0's abstentions and matched available-cell results in tables/notes. This must be inspected in the final chart.
2. Lead reported a bare `run` import collision in a combined test process. The author is isolating package-local module imports. This changes integration plumbing, not the estimator, and requires the combined test receipt before publication.

The JSON correctly distinguishes descriptive calibration, prospective evidence and production retention; accepted protocol does not authorize fitting w into the existing model automatically. The claim ledger correctly prohibits interpreting w as literal recognition probability, lambda as commission take rate, high in-sample fit as forecasting proof, or all future revenue as prebooked.

## Reproduction and reviewed artifacts

Exact independent package test command from the isolated repository root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 -m pytest analysis/src/forecast_methods/conversion_validation_v1/test_conversion.py -q
```

Direct solver: minimize the vector `lambda[season-1]*(w*GBV_l1+(1-w)*GBV_l2)-R` (or divide each component by R for relative loss), with `least_squares`, bounds `[0,0,0,0,0]` to `[1,1,1,1,1]`, tolerance 1e-13 and max_nfev=5000. Use three starts stated above and select lowest SSE. This audit command returned exit 0 in 3.19 tool-wall seconds; independent chronological reconstruction returned exit 0 in 2.06 seconds. Interval/parameter/LOYO checks plus unit tests returned exit 0 in 6.16 tool-wall seconds. Independent paired-draw reconstruction returned exit 0 in 1.12 seconds. All were read-only against frozen and package outputs.

Reviewed analytical model SHA-256 before packaging-only changes: `a9046663fb0e9c705337eb537282f17e54e9f2499c019d33793677007c8d94ae`.
First complete numerical output location: `data/processed/forecast_methods/conversion_validation_v1/results_v1/`.
The author will preserve it and publish a new final output after the presentation/import repairs.

## RESUME

Lead may treat this as closed independent acceptance of the full22 descriptive calibration and its qualified chronological FAIL. Author should finish the acknowledged visual and import-isolation repairs, rebuild a new immutable final version, and retain numerical equivalence plus a combined-test receipt. A final review addendum should identify the final source/output hashes and confirm the repaired chart. L4 may consume the audited calibration as research evidence while retaining the operational fixed benchmark and all pending adoption labels.
