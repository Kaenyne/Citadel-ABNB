# GE-JOINT-REVIEW — independent economic and implementation review

15 September 2026. Reviewer: chart_auditor. Worktree `codex/submission-readiness-v1`, base `2dfe0c2a1852181a246f4b6b9072e05e844d52d5`. Own new code/data directories: `gbv_joint_cohort_v1/review_v1/`. Review preregistration: `analysis/src/forecast_methods/gbv_joint_cohort_v1/review_v1/README.md`. Existing protected model/source/scorer files are read-only.

## Interim verdict

**Source and economic-contract review complete; quant implementation and results review pending.** Thirteen adversarial economic-contract tests and 143 independent source/hash/schema checks pass. These engineering counts are not independent quarters, extra reservations or evidence of predictive success. No model result has been accepted yet. Current direct corporate booking-cohort observations are **UNAVAILABLE** in the inspected local inputs. That means the measurement gate is unmet; it is not an empirical rejection of a physical survival hypothesis. Whether the smaller model improves guidance forecasts is a separate question.

## Economic contract

One booking-quarter by revenue-recognition-quarter dollar matrix must support both views. For matrix A and corporate revenue R, A[b,t]/R[t] measures a contribution to corporate revenue only if A has the appropriate fee-dollar lineage. A[b,t]/sum_b A[b,t] instead gives a share conditional on the allocated subtotal. Both can be reported, but an imperfect fit requires an explicit residual so that allocated revenue plus the residual reconciles to R. Renormalizing away that difference overstates coverage.

Forward conversion divides each matrix row by its own compatible original booking-cohort denominator. Reported quarterly GBV is net of cancellations/modifications recorded in the reporting period and is not an original gross reservation-cohort ledger. The proposed coefficient is therefore an effective fee-dollar allocation per reported GBV dollar. It is not observed survival, completion, cancellations or RNPL causality. A generic haircut added to already net GBV risks counting cancellations twice. Finite lag support, 3+ tails, old pre-sample bookings, future censored recognition and long-stay recognition must stay visible.

Low aggregate conversion variance does not identify a latent split. Unequal booking values mean normalized regression coefficients differ from backward revenue shares. Several incompatible matrices can produce identical observed revenue. Likewise, component variances cannot be summed as independent risks: covariance can offset all variation in the total. Bootstrap dispersion of aggregate-quarter model fits is conditional parameter uncertainty, not physical booking-cohort truth.

## Preregistration findings communicated before results

The original quant preregistration allowed same-day printed GBV at the prior quarter's earnings/guide date. The reviewer flagged that the next-quarter guide is issued in that same event. Such a race can measure conditional later revenue, but cannot claim to forecast that guide before publication. A pre-guide origin must also exclude the current print's lag1 GBV, not merely the target quarter's GBV. Parent agreed and requested an additive timing preregistration and guide/input availability checks. The final review must inspect that amendment and poison the unpublished inputs.

The reviewer also requested actual-revenue shares A/R alongside allocated-subtotal shares A/sumA, explicit cancellation/finite-tail/censor labels, and K2 restrictions on backward shares rather than direct substitution into forward coefficients. Quant confirmed these accounting distinctions before implementation. The quoted-share and forecast promotion thresholds remain those fixed in the quant preregistration; model precision will not be inferred from a good fit alone.

## Independent PR60/source checks

PR60 merge commit `dd3aa1440b152b46fdee8c094875d178b802d74a` is an ancestor of the worktree base. The reviewer independently replayed the data agent's source hashes and locality assertions and inspected important field/code definitions without importing data-audit functions. The exact source review receipt is `data/processed/forecast_methods/gbv_joint_cohort_v1/review_v1/source_v1/receipt.json`; all 143 checks passed across 23 inspected sources.

- K2's four value-weighted groups sum to one with the older tail, and contain 268,110 reservations. Their local Melbourne month labels are retained. This does not supply 268,110 independent quarterly observations. The old correction still misses its 52.306-day reference mean: adjusted estimates span approximately 40.613–43.638 days. This is stale reconstructed accommodation-value evidence with failed truncation recovery, not current corporate fee cohorts or measured year-to-year variance.
- The actual local review header contains listing/review IDs, posting date, reviewer fields and comments. It contains no original booking timestamp, fee value or cancellation history. No personal rows were copied into review outputs.
- WSDM's manifest explicitly records the absence of `created_date` from its sampled reservation columns despite README advertising it. The reservation sample CSV is not locally present. Neither inferred lead time nor current Airbnb representativeness follows from that metadata.
- Sideye's code calls available-to-unavailable transitions bookings and collapses each listing/stay-date history with `groupby(...).last()`. Its separate aggregate booking and stay margins are not a joint reservation matrix, and calendar blocks remain ambiguous.
- EUROCONTROL's saved day75 snapshot dates and recorded lag arithmetic reconcile. Flights may be a dated demand diagnostic, subject to the data agent's completeness/revision caveat, but have no original reservation or fee-recognition identifiers. Source timing alone does not convert flights into cohort observations.

The data agent's initial summary calls the unfulfilled direct-data gate `FAIL`; this review uses **UNAVAILABLE** for the underlying measurement object and reserves empirical FAIL for an executed test against a fixed pass line.

## Exact checks executed so far

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -m pytest analysis/src/forecast_methods/gbv_joint_cohort_v1/review_v1/test_economic_contract.py -q -p no:cacheprovider
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/gbv_joint_cohort_v1/review_v1/source_checks.py --out data/processed/forecast_methods/gbv_joint_cohort_v1/review_v1/source_v1
```

Both exit 0. Tests cover unequal backward/forward denominators, residual normalization, observationally equivalent allocations, 3+ tail, right censoring, net/gross cancellation ambiguity, positive/negative covariance and invalid matrix data. These tests validate the review arithmetic and source acceptance contract; they do not by themselves validate the quant author's code.

## Harness change requests

None from this reviewer. Parent owns any new forecast registration and frozen-scorer checks after implementation review. No physical cohort label should be registered as an observed target without the missing direct data.

## RESUME

Independent reviewer next inspects the additive timing preregistration, quant code and frozen output schemas; then independently recomputes matrix shares/rates, covariance, identification widths and common-origin W1/W2 scores, and runs unavailable-input poisoning against actual forecast functions. Final pitch eligibility must distinguish engineering acceptance, data unavailability, identification/stability failure and forecast performance. Keep current claims provisional until that closure is written.
