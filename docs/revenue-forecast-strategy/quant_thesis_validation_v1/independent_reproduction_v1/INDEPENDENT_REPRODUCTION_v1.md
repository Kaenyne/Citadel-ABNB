# Independent source and prospective reproduction

2026-09-14. Reviewer G: `/root/uncertainty_auditor`; implementation author A/D: `/root/source_auditor`. Parent adjudicates this review. No reviewer self-approval of the reviewer's prior uncertainty or accounting implementation is implied.

The source and prospective calculations reproduce. The prospective method **fails the frozen research hurdle**. Numerical reproducibility supports that conclusion; it does not establish an investment edge, original unrevised data vintages, calibrated predictive probabilities, or production promotion.

| Check | Independent evidence | Finding |
|---|---|---|
| Source audit rerun | All 8 canonical `source_audit_v1/results_v3` files byte-identical | PASS |
| Nominal guides | Decimal arithmetic reconstructs all 20 retained quoted endpoint pairs and midpoints; 19 display quanta of $10m and 1 of $100m | PASS for retained quotes; midpoint +/-$0.5m remains an administrative scoring convention |
| Availability | All 24 dates independently checked against calendar/source records; date-only inputs require publication date strictly before origin date | PASS as conservative reconstruction; original letter bytes and publication clocks absent |
| Frozen sources | 13 prospective input bindings checked; 10 baseline files match exact Git blobs and differ on disk only by CRLF/LF | PASS; raw Git hashes and local hashes separately recorded |
| Prospective rerun | All 25 canonical files byte-identical, including forecast freeze, points, errors and FAIL verdict | PASS |
| Separate numerical implementation | 793 checks; maximum absolute discrepancy 5.215953e-10, below 1e-6 tolerance | PASS |
| Information filtering | Independent origin/available-quarter reconstruction; future KPI, guide and cushion poisoning at every one of 21 origins leaves forecast status and point unchanged | PASS for tested functional independence |
| Source loading wording | Full tables are loaded before forecast freeze; points/input ledgers freeze before scoring and the target-outcome join | CLOSED with author's additive correction; no physical blinding claim |
| Research hurdle | W1/W2 n=12/10; W2 loses to B1; year-deletion requirement also fails versus B1 | FAIL preserved |
| Error covariance | Independent dimensionless expansion and cross-moment matrix exactly reconcile interval MSE | PASS; covariance cannot be discarded |
| Prediction bands | Chronological calibration inputs, finite-sample order rank and endpoints reproduce | Descriptive only; candidate coverage is 6/6 in both nested windows |

## Protocol and identity

L3 source baseline is `8821961853e4068febbfe2712f9a4e1036c9e629`. The accepted L3 manifest SHA-256 is `9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970`; source rerun verified all 108 bundled file bindings. No moving L3 worktree was consumed.

Final protocol SHA-256: `dd010ed6d158f1003b9ec55147e16a3f9464010c571b20fe25dad254202cb8ec`.

Reviewed prospective runner SHA-256: `9c583df337902d33a242a0e1bafdfdd749d4468ccb7eb8548da330e1afbabdac`.

Forecast-freeze SHA-256: `f305a65ad356a06c6f73f433347aa84f78b302c00905fc51de2416efe1d52823`.

Prediction CSV SHA-256: `cf9e8fca5eb03272b06ac10747b2bca2c1f68983fa9dc72d58aff0570159f53c`.

The completion receipt binds the author correction, all reviewer code and both detailed independent receipts. The latter bind source/author outputs file by file. The source manifest records exact baseline Git identity separately from Windows checkout text equality.

## Independent reconstruction

The reviewer implemented quarter arithmetic, origin selection, observed data filtering, seasonal lambda estimation and K0 dynamic variant selection without invoking the author's point functions. Origin is target-quarter start minus 18 calendar days rolled back to a recorded QQQ trading session close, at 16:00 America/New_York. Independent time-zone conversion matches saved origin timestamps. Every historical target's first guide is later than its origin.

For missing GBV, the retained rule uses the same quarter last year multiplied by the latest observed year-over-year GBV ratio. It never substitutes the later realized missing quarter. The candidate uses `(2*G1_hat+G2_hat)/3`, the available K0 seasonal lambda, and the median of the last eight eligible actual/first-guide ratios, with at least three observations. The exact ex-COVID, last-three and exponentially weighted K0 choices and nested leave-one-out selection were reconstructed. B1 uses observed prior guide growth; B2 uses the analogous revenue growth estimate and the same cushion statistic. Missing ingredients cause abstention. Initial W1 candidate abstentions are **2023Q1 and 2023Q3**.

Separate adversarial checks call the author's forecast API only after poisoning all not-yet-available KPI values, guide endpoints/midpoints and cushion actual/midpoint inputs. These checks cover all 21 origins and all three method statuses/points. The author's 13 tests also passed, but are reported separately from the reviewer's independent implementation. These controls demonstrate functional isolation against the tested perturbations. The full source files were present and loaded; this was not a blind holdout.

The candidate system carries four seasonal coefficients plus one cushion statistic (5 reported parameters); B1 has 0 fitted parameters and B2 has 1 common statistic. The GBV reconstruction has 0 fitted parameters. This parameter count does not erase the uncertainty from K0 selection or prior dataset exploration.

## Scores and the failed pass line

All values are USD million, interval-adjusted using `sign(e)*max(abs(e)-0.5,0)`. Raw midpoint errors were independently checked too. The primary sample is the all-three intersection.

| Window | n | Candidate RMSE | B1 guide-growth RMSE | B2 revenue-growth/cushion RMSE | Candidate MAE | B1 MAE | B2 MAE |
|---|---:|---:|---:|---:|---:|---:|---:|
| W1, 2023Q1–2026Q2 | 12 | 63.444678 | 74.330786 | 117.309034 | 52.133749 | 64.064048 | 95.518092 |
| W2, 2024Q1–2026Q2 | 10 | 63.696189 | 60.834441 | 121.925895 | 51.220820 | 57.226494 | 99.790033 |

Coverage floors, seasons and years pass, and candidate MAE is no worse than either benchmark. W2 candidate/B1 RMSE is 1.047041578, which fails the requirement to be strictly better than both baselines in both windows. Deleting 2023 from W1 gives candidate-minus-B1 MSE +356.375298. Deleting 2024 or 2026 from W2 gives +1197.418406 and +970.539736. Therefore the required year-deletion stability also fails. Deletions reuse the fixed forecasts; they are not refits or independent experiments. W2 is nested in W1, and there are only four/three calendar-year blocks.

## Exact error decomposition and uncertainty

Let `B` be realized lagged GBV base, `Bhat` the forecast base, `lambda*=R/B`, `h*=M/R`, and `hhat=1/divisor`, where `M` is the eventual first-guide midpoint. Define `u=Bhat/B-1`, `c=lambdahat/lambda*-1`, and `p=hhat/h*-1`. The raw guide error is exactly

`M*(u+c+p+u*c+u*p+c*p+u*c*p)`.

The eighth term `ROUND=e_interval-e_raw` converts that identity into the administrative interval error. Realized `lambda*` and `h*` are ex-post accounting reference ratios, not observable forecasts or independently identified structural causes. The reviewer independently constructed every term and the matrices `X'X/n` and centered population covariance.

| Window | Actual interval MSE | Sum of diagonal raw second moments only | Sum of cross terms | Full reconciled MSE |
|---|---:|---:|---:|---:|
| W1 | 4025.227112 | 7068.043325 | -3042.816213 | 4025.227112 |
| W2 | 4057.204554 | 8044.002950 | -3986.798396 | 4057.204554 |

Cross terms compensate materially for component errors. Summing marginal variances or treating component shocks as independent would overstate these observed errors and invent a stochastic model. The decomposition is descriptive arithmetic, not a probability distribution or evidence that each structural channel has been separately estimated.

The bands use the last eight available same-protocol raw relative errors and order rank `ceil(0.8*(m+1))`, with six errors required. Input timing, ranks and endpoints reproduce. Historical candidate coverage is 6/6 for both windows; these are the same six observations. Small dependent samples and overlapping windows provide no 80% predictive guarantee. No new bootstrap, loss search or empirical alternative specification was run.

## Reconstructed Q4 point

At the frozen **2026-09-11 16:00 ET** origin, 55 days before the assumed November 5 guide date, the candidate guide is $3162.609235m and its pre-cushion revenue arithmetic is $3219.235470m. B1 is $3133.916256m and B2 is $3180.464914m. The candidate descriptive band is approximately $3066.8144m–$3258.4040m, based on eight prior errors. This is a reconstructed research point under the failed specification. September 13 consensus is a different observation date and must not be presented as a same-origin comparison.

## Retained limits and execution history

The earliest retained source for 2020Q3 comparative levels is the 2021Q3 letter dated 2021-11-04. This conservative availability map is not a claim about the first public release. The 2023Q4 letter date is 2024-02-13, distinct from the 2024-02-16 filing date. Ten missing FX cells remain null. No raw shareholder-letter archive, original database vintages or new historical observations were recovered. Source display precision is not the uncertainty around nominal management guidance.

The initial independent scripts succeeded. The first combined runner `run.py` then stopped after those calculations when a raw local-source hash did not equal the Git blob hash. Read-only inspection showed that all ten affected baseline files differ only by Windows CRLF versus Git LF. The retained `complete_run_v1` contains the successful calculation reruns from that attempt. Additive `run_v2.py` retains exact raw Git hash verification and records the local raw hash plus explicit CRLF-to-LF text equality. No source, forecast or score changed. `complete_run_v2` is the canonical combined receipt. Original code and failed-attempt outputs remain present.

## RESUME

Parent should adjudicate this independent review using `complete_run_v2/independent_completion_receipt.json`, the two detailed reviewer receipts and source bindings. Preserve the failed research hurdle and all source/vintage limitations in final claims. The methodological improvement is an auditable prospective-origin reconstruction with explicit failure, not a demonstrated trading edge. No shared forecast registration, scorer mutation or production promotion was performed. Commands and retained-attempt handling are in the independent code directory's README.
