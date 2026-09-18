# Q4 — Identification and uncertainty audit, corrected presentation v2

Canonical note: v2. Preserved v1 had two mistyped sixth-decimal W2 table values; this copy corrects those to the already-correct CSV and clarifies the source-precision coefficient. Numerical outputs and code are unchanged.

2026-09-14 · uncertainty_auditor (`/root/uncertainty_auditor`) · `codex/quant-thesis-validation-v1` · Wave 1 C · reviewer: lead. Claim recorded in the new mission workboard. All outputs are new files in the exclusive `quant_thesis_validation_v1/uncertainty_audit_v1` package. The differentiated-equity-pitch skill and analysis protocol supply definition, source and causality checks; the user's 3–12 month research horizon and prohibition on forced direction/probabilities govern.

**Verdict: arithmetic reproduction PASS; precise structural identification and a calibrated complete Q4 guide distribution are unsupported by this evidence alone.** The accepted five-parameter descriptive fit and its failed free-weight promotion test remain intact. The existing fixed 2/3 operational estimator is retained. This audit confirms the numerical distinctions needed to explain that decision and supplies exact operational stress equations without adopting free-weight draws or fabricating probabilities.

## Evidence identity and what ran

The working HEAD is exactly `8821961853e4068febbfe2712f9a4e1036c9e629`. L3 research source is `7fb6fe0f248d5492b899672b9b70545da62d63ee`. The immutable bundle manifest SHA-256 is `9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970`; all 108 bound files pass. Those bundle rows are research/scenario records, not additional independent forecast observations. The 24 output bindings in conversion's acceptance receipt pass. The receipt hash is `bf91d81a78e79368b8815ac33f626f0c12509158f4fe24161f34fd97d09bd973`, and accepted specification hash is `f7cec04de2cdacfaad0fd7bb774992d933130e76918cca788bce151d482ddb40`.

Read the L3 publication handoff, conversion preregistration/results/closure, both independent reviews, acceptance receipt, specification and claim ledger. Viewed all three final PNG charts. Their descriptive labels, tiny-block caveats and matched 14/10 chart coverage are preserved. Figure 03's guide+cushion comparator is explicitly post-guide. The accepted receipt closes the specification's original pending-review status; it does not authorize production adoption. Original-workspace QVS notes were read as hashed external inputs, without following their links into the moving L3 worktree. K1/K2 are legacy evidence subordinate to later accepted results.

Exact successful command from the assigned worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 'analysis/src/forecast_methods/quant_thesis_validation_v1/uncertainty_audit_v1/run.py' --out 'data/processed/forecast_methods/quant_thesis_validation_v1/uncertainty_audit_v1/results_v1'
```

Exit 0; tool wall time 1.67 seconds. The maximum reproduced primary score difference is 1.1571e-9 USD million, consistent with decimal serialization. No new model fit, weight search, resampling or registration ran. The saved bootstrap rows were summarized, not regenerated. The runner records all read input hashes and has no imports from the old estimator. It rejects reused output destinations. No scorer, existing file, licensed/raw store or production object changed.

## Seven uncertainty objects that must stay distinct

All historical descriptions below use frozen public values and are retrospective, not original unrevised source-vintage reconstruction. A statistic's sample size is not the number of economic regimes it covers.

| Object | Reproduced evidence and n | What it means | What it cannot establish |
|---|---|---|---|
| Arithmetic first-lag contribution `a=wG1/[wG1+(1-w)G2]` at fixed w=2/3 | W1 n=14: pooled SD 4.644020pp, within-season SD 0.516084pp; Q4 n=3: SD 0.3113pp | Variation in a chosen formula as historical GBV proportions move | Structural uncertainty about w, measured revenue-cohort shares or complete forecast error |
| Estimated w and seasonal coefficient uncertainty | Accepted all22: five estimated parameters; w 0.78647848; six-year-block percentiles 0.307910–0.857332 | Sensitivity of descriptive reduced-form estimates to the available years | Precise structural confidence bounds, physical probabilities or a newly adopted operational model |
| Realized seasonal lambda variation | W1 n=14: pooled within-season SD 0.210897pp; Q4 n=3: mean 12.0298%, SD 0.0856pp, range 0.1711pp | Revenue divided by the fixed weighted-GBV denominator, absorbing multiple drivers | Isolated fees, cancellation effects, cash collection or commission take rate |
| Source precision and measurement | One Q3'26 denominator sensitivity: filing-based 27,247/29,187 versus frozen 27,200/29,200 gives +27 USDm to weighted GBV | A change in stated input precision conditional on a held-fixed coefficient | An admissible historical revision before the later filing's availability, or a probabilistic error bound |
| Conditional conversion predictive error | Saved matched free/fixed RMSE 63.1971/54.2275 USDm (W1 n=14), 57.3924/56.5157 (W2 n=10); nominal bands cover the same 7/8 outcomes in each window | Chronological historical errors when lagged GBV is printed at the letter-close origin | Preannouncement guide performance or the full September-to-November error distribution |
| Future GBV uncertainty | Q4 September forecast requires unprinted Q3 GBV; the accepted conversion experiment contains no historical upstream-GBV forecast-error distribution for this origin | Separate upstream error requiring the frozen new protocol and matched-origin reconstruction | A zero-risk input, or an error distribution supplied by the conversion coefficient bootstrap |
| Management guide policy | `Q=R/(1+c)`; c must use admissible past outcomes at each origin; explicit guide expectations remain a separate data object | Conditional transformation from own revenue forecast into a guide estimate | Observed consensus guide expectations, an executable surprise edge, or a probability from midpoint-beat counts |

Full prediction additionally needs residual model misspecification, structural change, source availability and their dependence. Do not add these standard deviations in quadrature unless the covariance assumptions can be justified and recorded. A small arithmetic SD cannot substitute for the missing components.

## Fixed arithmetic reproduced

The frozen KPI panel contains 24 quarters, 2020Q3–2026Q2; 22 possess both lagged GBVs. At fixed w=2/3, `a=2G1/(2G1+G2)`. Sample variance uses n−1. Within-season SD uses season-demeaned squared deviations divided by n−4.

| Window | n | Mean a | SD a, pp | Within-season SD a, pp | Within-season SD lambda, pp |
|---|---:|---:|---:|---:|---:|
| All lag-complete | 22 | 67.727674% | 5.142174 | 1.970898 | 0.436968 |
| Excluding 2021 | 18 | 67.585714% | 4.560148 | 0.769174 | 0.225790 |
| W1 | 14 | 67.473252% | 4.644020 | 0.516084 | 0.210897 |
| W2 | 10 | 67.521026% | 4.672721 | 0.558622 | 0.252945 |

W1 season means account for 99.0500% of a sum-of-squares and 99.1150% of lambda sum-of-squares. This is an arithmetic decomposition, not a causal variance-explained or predictability claim. There are only 4/4/3/3 W1 observations in Q1/Q2/Q3/Q4, and 3/3/2/2 in W2. W1 and W2 overlap. The pronounced change when 2021 enters is part of the result, not an exclusion justified by the desired conclusion. Year-deletion outputs retain all years and their changing sample sizes.

## Accepted comparison reproduced without reopening selection

| Primary comparison | W1 n=14 | W2 n=10 |
|---|---:|---:|
| Free shared w revenue RMSE, USDm | 63.197127 | 57.392447 |
| Matched fixed-2/3 OLS revenue RMSE, USDm | 54.227498 | 56.515722 |
| Free/fixed ratio | 1.165407 | 1.015513 |
| Preregistered promotion outcome | FAIL | FAIL |
| Saved paired year-block ratio percentiles | 0.848335–1.525124 | 0.806881–1.135943 |
| Target-year blocks | 4 | 3 |

The all22 free model estimates four seasonal coefficients plus shared w; matched fixed OLS estimates four. Its accepted coefficient levels are 12.931911%, 13.224232%, 17.302744% and 12.111558%. Neither is the existing operational lambda estimator. The failed comparison supports retaining the tested simpler policy; it does not prove 2/3 uniquely optimal or statistically dominant across regimes. An extra parameter improves training SSE by construction, so the full-sample plot cannot carry the selection decision.

The 2,000 saved paired resamples per window retain only four/three underlying target years. The 1,000 saved parameter resamples retain six years, with partial 2026. Repeated draws do not create new regimes. Leave-year-out fits use future years relative to the omitted early year and are descriptive; the all22, ex2021 and post2023 fitted weights 0.78648, 0.53873 and 0.35696 remain existing sensitivity evidence. No favorable alternate loss or subsample replaces the accepted test.

The nominal 80% interval arithmetic reproduces: both primary models cover 7 of 8 eligible outcomes, specifically 2024Q3–2026Q2, in both W1 and W2. Mean full width is 9.738132% of forecast for free w and 9.105477% for matched fixed. These are eight total cases per model, not sixteen. The sample and serial dependence preclude an 80% coverage guarantee.

## Joint dependence and compensation

For a season whose historical ratio `G1/G2≈r_s`, write `R≈lambda_s[1+w(r_s−1)]G2`. The combination `k_s=lambda_s[1+w(r_s−1)]` may be more stable than either coefficient. At exactly fixed r, maintaining the same combination requires

`lambda_new=lambda_old*[1+w_old(r−1)]/[1+w_new(r−1)]`.

This is an algebraic compensation relation, not a new fitted model. The audit preserves each existing joint parameter row and uses each season's all22 mean G1/G2 as the fixed reference. These references have n=6/6/5/5 observations and are not a live operational forecast.

| Season | r_s | Corr(w, lambda), 1,000 saved draws | Lambda SD, pp | Effective slope k_s SD, pp | Covariance effect on linear variance |
|---|---:|---:|---:|---:|---|
| Q1 | 0.860655 | +0.906127 | 0.325648 | 0.123287 | Reduces |
| Q2 | 1.513025 | −0.991467 | 0.766664 | 0.200937 | Reduces |
| Q3 | 1.022113 | +0.812700 | 0.177463 | 0.231212 | Increases |
| Q4 | 0.937281 | +0.845903 | 0.127119 | 0.066086 | Reduces |

The Q3 counterexample matters: dependence does not universally narrow the answer. The exact decomposition about the draw means is `k=mean(lambda)[1+mean(w)(r−1)] + [1+mean(w)(r−1)]dLambda + mean(lambda)(r−1)dw + (r−1)dLambda*dw`. Output records both marginal variance terms, twice their covariance, joint linear variance and the exact product variance. Dropping the interaction also changes the result, notably for Q2. Independent marginal tail combinations are not sampled joint states. These descriptive free-w draws must not enter an operational fixed-w forecast unless a separate adoption decision explicitly changes the model.

## Source precision and legacy identification cautions

Holding W1 Q3 mean realized lambda fixed at 0.1723936185, the +27 USDm denominator change above gives +4.654628 USDm revenue. QVS said approximately +4.659 USDm holding the operational lambda fixed at approximately 0.1725489 (the parent identified this estimator). Its arithmetic is 27*0.1725489=4.6588203 USDm. The difference comes from the held-fixed lambda estimator, not a filing transcription error. Any reused dollar sensitivity must state which coefficient it holds fixed. The source auditor owns verification of the filing publication date and exact precision fields. This illustrative calculation does not update a frozen input or calibrate measurement uncertainty.

K1's pooled five-lag specification uses eight free parameters on 14–20 quarters; season-specific weights use 20 on 16–20. In its ex-COVID pooled sensitivity, phi1 spans approximately 0–0.724, phi2 0–0.640 and their sum 0.152–0.871. The fitted sums near 0.58–0.64 are point estimates from different samples, not a tight uncertainty interval. Adjacent rolling-12 fits share eleven observations. They do not independently measure current recognition shares. The older retrospective weight sweep is not a substitute for the later accepted matched L3 comparison.

K2's 268,110 reservations come from one old Melbourne panel with one clean 12-month period, March 2016–February 2017. Booking-date capture truncation, imported tails, surviving-stay selection, unverified price units, price-times-nights rather than complete GBV, and a six-month season mapping all limit transport to current global ABNB. Christmas is not shifted by hemisphere: Q2/Q4 seasonal translations are especially uncertain. More reservations in that panel do not create more current global regimes. K2's tail/validation bands are identification/scenario ranges; its later recommendation to treat them as roughly ±1 SD is inconsistent with their construction and must not be used.

Let `C[b,t]` be fee revenue from booking cohort b recognized in period t. A backward revenue-origin share is `alpha[b,t]=C[b,t]/R[t]`, where `R[t]=sum_b C[b,t]`. A forward cohort-recognition allocation is `beta[b,t]=C[b,t]/T[b]`, where `T[b]=sum_t C[b,t]`. They obey `beta=alpha*R[t]/T[b]` and have different conservation directions. Without cohort totals, a backward stay-origin proxy cannot become a forward GBV allocation. Reported net GBV also includes cancellations processed during the reported period that may belong to older bookings; it is not a pure gross cohort total. Unpaid balance-sheet stocks are not recognized fee-revenue flow weights.

## Exact operational stress and break-even equations

Use the retained operational w and lambda policy. Let `B=wG1+(1−w)G2`, `R=lambda*B*kappa`, and `Q=R/(1+c)`. `kappa=1` at baseline; a changed kappa is a clearly labeled *incremental* mapping stress only after checking that it is not already represented in GBV, lambda or another overlay. No empirical RNPL/fee/FX magnitude is supplied by this symbol.

The exact finite change is

`Q'/Q = (lambda'/lambda)*(B'/B)*(kappa'/kappa)*(1+c)/(1+c')`.

This retains interaction terms and can be applied to jointly specified deterministic states. No probability is implied. Dollar partial sensitivities at held-fixed other inputs are `dR/dlambda=B*kappa`, `dR/dG1=lambda*w*kappa`, `dR/dG2=lambda*(1−w)*kappa`, and `dQ/dc=−R/(1+c)^2`. If w is allowed to vary in an explicit diagnostic, `dR/dw=lambda*(G1−G2)*kappa`; a simultaneous refit adds `B*kappa*dLambda/dw`, so the held-fixed derivative cannot represent a refitted uncertainty experiment.

For a revenue consensus S, the equal-revenue boundaries are

`G1*=[S/(lambda*kappa)−(1−w)G2]/w`, `lambda*=S/(B*kappa)`, and `kappa*=S/(lambda*B)`.

For an explicitly observed guide expectation H, `c*=R/H−1` and `G1*=[H(1+c)/(lambda*kappa)−(1−w)G2]/w`. If no H exists, define a hypothetical Street guide `H=S/(1+cStreet)` only as a conditional construction. The equal-guide boundary is `cOwn*=R(1+cStreet)/S−1`. With the same cushion on both sides, the sign of the guide difference equals the revenue difference; with differing cushions it need not. All boundaries assume positive denominators, 0<w≤1 and c>−1. If no economically admissible boundary exists, report that instead of a misleading crossing.

Reported USD GBV already contains currency translation; a gross FX multiplier added again is double counting. Fee and RNPL stresses must be residual changes relative to the baseline, with gross/net cancellations and stock/flow denominators reconciled. Do not combine stochastic free-w parameters with the operational fixed-w bridge. When dependence lacks calibration, publish the joint assumptions and dollar boundaries rather than a synthetic confidence envelope.

## Claim-safe wording and measurable falsifiers

| Status | Presentation sentence | Observation that would weaken or resolve it |
|---|---|---|
| Supported selection result | Estimating a shared lag weight failed the accepted chronological RMSE hurdle, so the existing fixed rule remains the benchmark. | A separately preregistered, matched-origin successor improves both windows with defensible uncertainty and economic benefit. |
| Conditional descriptive stability | Recent within-season conversion is stable in this small historical sample. | Repeated signed same-season residuals or errors larger than the existing origin-valid error scale; report them without a causal label. |
| Unidentified physical weights | The kernel's coefficient is not a measured booking-to-revenue allocation. | Current global fee-weighted booking/cohort recognition totals with cancellations and payment timing reconcile both row and column sums. |
| Conditional regime risk | Longer lead times, changed payment/cancellation timing, mix, fee or currency exposures can change the reduced-form mapping. | Observable booking-to-stay distributions, realized cancellation adjustments and reconciled fee/exposure measures account for a sustained forecast residual. |
| Unsupported full distribution | Conversion-only intervals do not represent the complete September Q4-guide forecast uncertainty. | New prospective validation supplies upstream GBV and guide-policy errors on matched admissible origins and records their interaction. |
| Conditional expectations comparison | Own revenue must be compared with dated revenue consensus; guide expectations are separate. | A dated explicit expectation for management's guide or a validated translation supplies the missing object. |

The parent can set economically meaningful live thresholds using the exact break-even equations. The legacy Q3 lambda thresholds 17.09%/16.93% use only three season observations and are composite controls; they do not identify RNPL cancellation causality or provide Gaussian tail probabilities. A mapping break is not proof of one preferred mechanism. A policy-cushion break may alter the guide even with an accurate revenue forecast.

## Failures, limitations and next review

No analytical check failed. Pandas emitted performance warnings for adding columns to the wide frozen panel; the 24-row calculations completed. No fresh empirical probability calibration, external source-precision audit, upstream-GBV evaluation or accounting causal estimate was attempted within this bounded Q4 assignment. Those remain the explicitly assigned source/protocol/accounting work streams, not reasons to extend the old weight search. The audit's reproduction code is new implementation and requires lead review; it does not certify itself as independent of its author.

## RESUME

Wave 1 Q4 is complete for lead review. Use the new result CSVs and exact operational boundaries when assembling the live bridge, preserving source/parameter/GBV/guide-policy distinctions and all covariance caveats. Wait for the frozen prospective protocol and worker A's output, then independently reproduce that new implementation without signing one's own underlying audit. Write subsequent accounting review and reproduction receipts as new versioned files within this exclusive package. No existing output may be overwritten; no scorer is required until a separately authorized research registration occurs.
