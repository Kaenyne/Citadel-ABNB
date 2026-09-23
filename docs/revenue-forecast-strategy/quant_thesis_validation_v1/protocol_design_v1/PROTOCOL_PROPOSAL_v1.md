# Q2/Q3 — decision-origin protocol proposal v1

2026-09-14 · worker B `/root/test_designer` · `codex/quant-thesis-validation-v1` · new documentation only. Parent must freeze a separate final version before worker A evaluates new historical outcomes. Worker C independently reproduces that implementation. This document proposes choices, not results or a promotion decision.

## Recommendation

Evaluate one reconstructed, genuinely preannouncement management-guide forecast: fixed K0 seasonal conversion policy applied to one simple forecast of unprinted GBV, then divided by the median of the last eight realized actual/guide ratios. Use the target quarter's start minus 18 calendar days, rolled back to the latest US equity session, as the primary information date. This matches the September-to-November pitch horizon without using a future-known earnings schedule to select historical origins. Compare against two simple forecasts on identical cells. Retain every abstention and failure.

The existing historical quarters have been explored extensively. This is a newly frozen historical information-set reconstruction, not an untouched external holdout, archived forecast track record, or prospective real-time experiment. A successful research implementation can produce a failed forecasting hurdle. Neither outcome changes L4 production objects or authorizes a trade.

## Evidence and completed design work

Authoritative L3 baseline: `8821961853e4068febbfe2712f9a4e1036c9e629`; L4 external baseline: `29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`. Read the ordered project brief/workboard, this mission's workboard, K0 API and implementation, frozen harness 1.0/1.1, Lane 2 convention, L3 conversion preregistration/results/final closure, and original-workspace QVS variance and guide-basis notes read-only. L3's failed free-weight promotion and retained operational policy are binding. No free-weight search, all22 fixed-OLS replacement, or new performance evaluation ran in this design task.

The source auditor reports date-only historical release records, rather than exact SEC acceptance timestamps, and a conservative correction for the approximate 2020Q3 publication date. Use the final source-availability manifest; source precision cannot be backfilled from a later filing. None of the intended W1 origins precedes the auditor's conservative 2021-11-04 availability for 2020Q3 comparative GBV.

## Locked target, origin and hypothesis

Target `M_q` is the midpoint of the **first issued revenue guide for quarter q**, in USD millions, from the prior quarter's earnings release. Do not replace first guidance with a later revision. The public issuance date of this target is distinct from the later date when quarter-q revenue prints. No quarter-q guide, management range, guidance language, or morning-of-release consensus may enter a forecast made before that guide.

For each q, define calendar anchor `A_q = start_date(q) - 18 calendar days`. Define origin as the latest regular US equity trading session on or before A_q, at that session's close in `America/New_York`. Freeze the session dates from the committed QQQ rows of `returns_v1/ohlc_daily.csv`; only date membership is used, never prices or returns. Check that the selected date is no more than four calendar days before the anchor and that both relevant source data and target guide remain unprinted at the cutoff. For a half-day, use its true earlier close; none may silently become 16:00. If the source calendar cannot establish a requested session, abstain rather than invent a date. The fixed historical anchors lie in mid-March/June/September/December, away from routine half-days.

For Q4 2026, A is Sunday 2026-09-13 and the session cutoff is Friday 2026-09-11 16:00 ET. This is 55 calendar days before the project's 2026-11-05 guide date. It is not the actual 2026-09-14 execution date. Label any computed Q4 point a **reconstructed September-11 origin**, not an archived September-11 forecast. The November release date is used only to report realized/assumed lead time; it does not select the primary origin. Do not silently substitute the later L4 September-13 consensus snapshot into this experiment.

Report for every historical target the anchor, actual cutoff, guide issuance date and calendar-day lead. No return or trading test is included. Hypothesis: this one K0/GBV construction reduces guide-midpoint forecast loss relative to both locked simple alternatives at this information date.

No close-before-release diagnostic is proposed for v1. With these quarterly-only inputs, the previous quarter's GBV and revenue still remain unprinted until the release, and the immediately preceding earnings release is already known at the primary origin. Thus moving only the cutoff normally supplies no new observation. A diagnostic that merely duplicates the same forecast is not an independent horizon validation. If the source audit identifies a genuinely new eligible input between dates, a second origin would require a pre-evaluation parent addendum; at most one such diagnostic is permitted and it cannot replace the primary result.

## Operational forecast contract

Let q be the guided target quarter, `G1=GBV_(q-1)`, `G2=GBV_(q-2)` and w=2/3. All dollar quantities are USD millions; lambda returned by K0 is percent and is divided by 100 exactly once.

1. Build a point-in-time input panel from the frozen KPI levels and audited conservative publication dates. Filter every metric by `available_at <= origin_close`; date-only releases become eligible only after their full local publication day. Keep later-period rows and later filing precision out of the forecasting process. Pass an already filtered panel into K0 with `as_of = origin calendar date`: K0's strict-date refusal is compatible because same-day inputs are unavailable at this close. Record the public wrapper date and actual cutoff separately; do **not** use the Lane 2 `d+1` post-letter wrapper here.
2. Obtain `lambda_hat = K0.pit_lambda(season(q), as_of, variant=None, panel=filtered_panel)['lambda_pct']/100`. Use the exact accepted implementation. It keeps w fixed, recomputes its existing variant-selection rule inside each origin and defaults to ex-COVID when its common W1 LOO cells are fewer than eight. Preserve K0's three candidate variants, half-life two, tie order, exclusion rule `abs(nights_yoy_pct)<=25` and missing-growth exclusion. No custom seasonal estimator, hindsight-selected live EWM, or new fallback is allowed. The retrospective selection policy remains a limitation inherited from K0, not newly concealed flexibility.
3. Let j be the latest quarter whose GBV is admissibly observed. For every missing required lag k in {q-1,q-2}, use the one rule `GBV_hat_k = GBV_(k-4) * GBV_j / GBV_(j-4)`. Require j and j-4 as actual observations and the seasonal anchor k-4 as an actual observation. Never insert another forecast as a training observation or into j. Use actual admissible GBV for any required lag already known. The normal q-1 forecast is `GBV_(q-5)*GBV_(q-2)/GBV_(q-6)`. This is latest observed year-over-year growth persistence, retaining seasonal dollar scale without estimating an extra growth coefficient. The economic rationale is persistence in booking growth across adjacent quarters with strong seasonal levels, not a causal assertion that all current-quarter bookings are known.
4. This rule is a **reconstructed forecast**, not contemporaneously archived. A pre-freeze availability inventory should establish whether any complete, comparable earlier-origin archived GBV series exists. Sparse morning-of-print or September-current estimates cannot replace earlier origins. Do not mix archived and reconstructed GBV by row. Any archive discovery is an inventory result; it cannot become an unregistered competing rule after outcomes are examined.
5. Compute `B_hat = (2*GBV_hat_(q-1) + GBV_hat_(q-2))/3` and `R_hat = lambda_hat * B_hat`. Forecast GBV is supplied only in this explicit arithmetic bridge, never fabricated as a positive-revenue row passed into K0's training panel. The public `kernel_forecast` intentionally refuses unprinted lags; bypassing that refusal by falsifying a print date is prohibited.
6. Get the last at most eight realized actual/guide-mid ratios from the same accepted cushion-series source used by K0. Require that each target-quarter actual had become public before the origin. Compute `d_hat = median(actual/value_mid)` and `M_hat = R_hat/d_hat`. Record every cushion quarter, ratio, input date and n. The divisor is 1+cushion, not the cushion itself. Use `cushion_series.actual` exactly as K0 does for estimating the operational divisor; source-audit differences from the frozen KPI revenue are separately disclosed, never silently repaired.

No separate FX, RNPL, fee, ADR, alternative-data or regional multiplier enters this test. Reported USD GBV already contains currency translation and cancellations in its accounting basis. Existing conditional scenarios belong to the separate economic/uncertainty work, not fitted model terms here.

### Minimum inputs and abstention

- At least one same-season lambda observation accepted by exact K0 policy, with its own two GBV lags present. Requiring a new two-observation seasonal floor would change the operational method; retain K0's own abstention and display n=1 as sparse where it occurs.
- At least three admissible realized cushion ratios, with at most eight used. This floor follows the frozen harness guide-cushion minimum and prevents a one-observation policy estimate. It is an explicit wrapper minimum, not an assertion that K0 itself requires three.
- For GBV persistence: positive finite actual G_j, G_(j-4), G_(k-4) for each missing lag; one observed year-over-year comparison. No zero-growth fallback if a seasonal anchor or observed comparison is absent.
- All source keys unique, units and quarter identities explicit, all input publication timestamps nonmissing, and target guide strictly after the origin. Forecasts require positive finite denominators and results.
- One row exists for every one of 14 W1 and 10 nested W2 target slots. Missing forecasts are abstentions with machine-readable reason and missing-input list. No replacement quarter, newer filing, fitted fallback, or post hoc minimum relaxation.
- For a comparison to qualify for the research hurdle, require at least eight matched W1 targets and six matched W2 targets, all four seasons in each, and at least three distinct target years in each. These are preregistered information/coverage floors, not a statistical-power guarantee. If unmet, report UNDERPOWERED/INSUFFICIENT COVERAGE rather than PASS or empirical inferiority.

## Locked baselines and matching

Use two comparators; do not add AR variants or feature screens after looking at results.

**B1, direct guide-growth persistence (primary simple comparator).** Apply the same canonical naive seasonal-growth rule to guides themselves: let h be the latest guide target with its first guide published before origin; `M_hat_B1 = M_(q-4)*M_h/M_(h-4)`. Typically h=q-1. This uses a then-known guide for q-1, never the unknown guide for q. Require all three positive finite guide values and publication dates. This is the frozen naive point rule applied transparently to a guide series; it is not an existing frozen registry object. Unlike actual revenue history, previous-quarter guidance is already observable at the origin. No cushion fit is needed.

**B2, revenue-naive with common cushion.** Call the frozen `harness.baselines.baseline_naive(origin_date,q,metric='revenue_musd',prior_basis='PIT',targets=audited_filtered_targets)` and use only its `point`, divided by exactly the candidate's `d_hat`. Supply filtered targets to enforce conservative actual-publication availability. Its formula is `R_(q-4)*(latest observed R_y / R_(y-4))`. Require an actual observed year-over-year comparison, rather than allow the function's no-growth fallback; record any abstention. The baseline's pseudo-residual uncertainty output is not used because it is not calibrated to this horizon.

Score each pair on its intersection and additionally publish the all-three intersection; the all-three intersection is the primary hurdle set. Print each baseline's own availability and omitted targets so the headline cannot hide easy or difficult cells. The candidate receives no different input vintage than its comparisons. Frozen guide+cushion revenue benchmark is inadmissible here because it consumes the very target guide being forecast. Revenue consensus is not observed guide expectations. No consensus comparator is asserted in v1.

Point-estimation parameter accounting: fixed w and upstream GBV persistence add zero fitted parameters; the K0 rule fits a seasonal lambda (four across the full seasonal system) and applies existing model selection; median cushion adds one statistic. Report system n_params=5 and lambda/cushion/GBV observation counts separately, avoiding a misleading single effective degrees-of-freedom claim. B1 has zero fitted coefficients; B2 has one common cushion statistic, with no fitted uncertainty parameter counted because API intervals are discarded.

## Scoring and preregistered research hurdle

Primary loss is USD-million squared signed distance to the target's rounding interval. Never use the entire management guide range as a zero-loss interval: the object being forecast is the midpoint. For a letter integer x expressed in its stated source unit, its reporting interval is `[x-0.5,x+0.5]` in that unit. If endpoint rounding half-widths in USDm are delta_L and delta_H, the midpoint's half-width is `delta_M=(delta_L+delta_H)/2`. Preserve source units; converting a two-decimal-billion endpoint to an integer USDm does not make the source precision one million.

The final source-precision manifest must lock `target_mid_lo`, `target_mid_hi` and `rounding_basis` before evaluation. Where the guide is an explicit announced policy endpoint rather than a rounded measured quantity, retain that semantic distinction in the manifest. If original endpoint precision cannot be established in the bounded audit, use an explicitly labeled **project integer-USDm scoring convention** of midpoint +/-0.5 USDm, and publish raw midpoint errors alongside it; do not claim that convention is verified economic precision. No interval is selected from forecast error size.

Define `e_raw = forecast-midpoint`; `e_if = forecast-clip(forecast,mid_lo,mid_hi)`. Report n, RMSE=`sqrt(mean(e_if^2))`, MAE=`mean(abs(e_if))`, signed bias=`mean(e_if)`; publish the raw counterparts and per-row rounding adjustment. Also report percentage errors using the observed midpoint solely as a scale, without changing the primary USD loss. Report candidate and both matched baseline scores, loss differences, ratios, and every per-date signed/absolute/squared paired loss difference.

The **research forecasting hurdle** passes only if the coverage floors above hold and all of the following hold on the all-three intersection:

1. Candidate interval-fair RMSE is strictly lower than B1 and B2 in both W1 and W2. Use a numerical comparison tolerance of 1e-9 USDm; that is numerical hygiene, not economic materiality.
2. Candidate interval-fair MAE is no greater than either comparator in either window, with the same tolerance.
3. Delete each target calendar year in turn from each matched window, keeping the originally formed forecasts fixed. The remaining candidate interval-fair MSE must remain strictly lower than each baseline's in every deletion. At least two years must remain after deletion. This is paired year sensitivity, not a refit with future years and not a confidence interval.

If #1 fails, label FAIL. If #1 passes but #2 or #3 fails, label NUMERICAL IMPROVEMENT / STABILITY HURDLE FAIL. If any comparison is undefined or coverage inadequate, label INSUFFICIENT COVERAGE. Even a pass permits only “lower historical matched loss under this reconstructed protocol,” subject to independent review. Report improvement in dollars and compare with economic break-even sensitivities; no automatic production promotion, statistical-superiority statement, calibrated probability, expected return or trade adoption follows.

Always publish year and season score slices with n, without changing the window verdict. W2 is nested in W1; four/three target-year blocks at maximum are not independent confirmations. No bootstrap p-value or model-ranking probability is required. No weight, horizon, sample, loss or missingness rule may be changed after seeing results; a correction requires a new dated protocol/version and retention of the initial attempt.

## Exact error attribution and covariance

Use eventual frozen actual `R_q`, eventual GBV lags, and first guide midpoint only in a separate scoring/attribution stage after forecasts are frozen. They are not forecasting inputs. Let `B=w*G1+(1-w)*G2`, `lambda_star=R_q/B`, `d_star=R_q/M_q`, and `h=1/d`. Define deltas `b=B_hat-B`, `l=lambda_hat-lambda_star`, `a=h_hat-h_star`.

Seven exact contributions to raw guide error are:

| Term | Formula | Interpretation |
|---|---|---|
| U | `lambda_star*h_star*b` | Unprinted-GBV main term |
| C | `B*h_star*l` | Conversion main term |
| P | `lambda_star*B*a` | Management-policy main term |
| UC | `h_star*b*l` | GBV/conversion interaction |
| UP | `lambda_star*b*a` | GBV/policy interaction |
| CP | `B*l*a` | Conversion/policy interaction |
| UCP | `b*l*a` | Three-way interaction |

Their sum equals `lambda_hat*B_hat*h_hat-M_q` exactly to numerical tolerance. Lambda_star and d_star are ex-post identities, not identified structural truths or separately estimated causal shocks. Source precision and specification error remain in the conversion accounting term; this does not identify FX or RNPL effects.

Add an eighth contribution `ROUND=e_if-e_raw` when reconciling interval-fair squared error. For each matched window publish mean(A_j), mean(A_j^2), all pair cross moments `2*mean(A_j*A_k)`, and population-denominator covariance `Cov0(A_j,A_k)=mean(A_j*A_k)-mean(A_j)*mean(A_k)`. Then `MSE = sum_j mean(A_j^2) + sum_(j<k) 2*mean(A_j*A_k)`. This identity is valid without independence; negative cross terms/covariances are retained. Do not sum standalone RMSEs, add SDs in quadrature, or label one ordered decomposition a unique causal contribution.

For a simpler economic readout, also report `lambda_hat*(B_hat-B)/d_hat`, `(lambda_hat*B-R_q)/d_hat`, and `R_q/d_hat-M_q`; these sum to raw error but allocate interactions by order. Label them an **ordered accounting bridge**, not causal attribution, and retain the explicit interaction table above as authoritative.

## Descriptive interval calibration

Optional only in the sense that insufficient history leaves intervals missing, not in the sense that performance chooses whether to report them. For each method and primary origin, keep the last at most eight absolute raw relative guide errors `abs(M_actual-M_hat)/M_hat` from earlier forecasts of that same method/origin protocol, requiring their guides to have been issued before the current origin. Calibration may use first-guidance observations earlier than W1 if the same frozen rule could have formed forecasts and all minimum inputs were met. Do not borrow K0 post-letter errors, conversion-only errors, or future-guide residuals.

Require at least six calibration errors. Let k=ceil((m+1)*0.80); when k<=m choose the kth order statistic a and form `[max(0,M_hat*(1-a)), M_hat*(1+a)]`; otherwise bounds are missing. No fitting, Gaussian fallback, full-sample residuals or inflation tuning. Publish each calibration quarter and availability date, m, rank, raw-midpoint coverage, target-interval overlap and containment coverage, USDm width and width/forecast. These are descriptive historical prediction bands; no exchangeability or 80% coverage guarantee. Their matched coverage sample can be much smaller than point-forecast n.

## Local ledger, harness incompatibilities and completion

Use exclusive new code/data directories under `quant_thesis_validation_v1` with an immutable output destination. The machine-readable ledger should resemble harness rows while preserving actual timestamps, target guide issuance, input provenance, abstentions and target intervals. Keep one PIT reconstruction only; no deliberate future-parameter replay is needed to answer this prospective question. Do not write shared registry files.

**Harness change request:** both FORMAT 1.0 and 1.1 reject historical W1/W2 origins that are not guide dates. FORMAT 1.1 relaxes only LIVE dates. Moreover, the validator's availability cutoff is quarter revenue print, not first guide issuance; it would permit some already-known-guide predictions. `guide_mid` exists in frozen targets and technically joins in `score.py`, but frozen baselines are keyed to other target objects/origins. The frozen scorer uses point-minus-actual errors and does not implement the project's integer-interval loss or target-specific publication metadata. Hence no compliant registration of this experiment at the actual origins can be made without a new reviewed harness extension. Replacing actual vintage with guide date, marking historical rows LIVE, renaming guide as revenue, or supplying future-dated forecasts is prohibited. Record this incompatibility in the final note; no harness modification or scorer invocation is needed because no registration occurs.

Implementation outputs: frozen protocol/source hashes; full origin/input/cushion/training tables; per-target forecast and exclusion ledger; matched scores; paired/year/season sensitivities; interval calibration/coverage; exact contribution/cross-moment tables; experiment-attempt ledger; and a research verdict distinct from production adoption. All tables show n. Unit/leakage tests must include poisoned future GBV/revenue/target-guide rows, missing/duplicate dates, unprinted lag treatment, postdated consensus rejection if read at all, first-guide versus revised-guide selection, two-baseline intersection matching, integer source-unit conversion, chronology of residual availability, and exact contribution/MSE reconciliation. Parameter searches or mirror-the-code arithmetic tests are unnecessary.

Author completion test: proposal states a concrete primary origin, source cutoff, exact retained lambda estimator, one GBV rule, two benchmarks, minimum inputs, missingness, target precision, scoring/hurdle, uncertainty chronology, error interactions, registration decision and ownership; no new performance result is computed. Parent's final freeze should resolve the source-precision convention and archive availability before the implementer starts. Worker C must independently recompute material rows and all-information-set guards, rather than merely rerun the author's assertions.

## RESUME

Parent should save a final protocol with the agreed source-precision fields and archive inventory, bind it by SHA-256, and authorize worker A to implement exactly that version in new directories. Worker B next builds the independently assigned economic bridge from immutable L4 inputs; worker C later reproduces prospective results. Any negative forecast result, sparse intervals or remaining measurement limitation is retained and carried into permitted presentation wording.
