# GD-REVIEW — independent GBV decision review

15 September 2026. Owner: chart_auditor. Completes GD-REVIEW in `WORKBOARD_GBV_DECISION_0915_v1.md`. All review code and receipts are new files under `gbv_decision_0915_v1/review_v1/`. No original model, input, frozen scorer, registry or earlier note was edited by the reviewer. This note follows `GD_REVIEW_PREREG_v1.md`, `GD_REVIEW_REGIME_ADDENDUM_v1.md`, and the parent's calendar-origin, eligibility and calendar-flight addenda. History was already inspected; this is not a fresh holdout.

## Decision

**Keep GBV conversion as a supporting forecasting and scenario tool; do not center the short pitch on an established GBV-derived guide miss.** The fuller evidence is materially more favorable to aggregate forecasting than a verdict based solely on physical-cohort nonidentification would suggest. The joint model beats the inherited quarterly revenue consensus on the matched September-style sample. The fixed model also passes the declared longest-horizon gate on a restricted common sample. Preserve both findings. Neither establishes general superiority in guide forecasting or an executable short signal.

There is no requirement to observe real reservation cohorts before admitting a reduced-form forecast. Direct cohort measurement is **UNAVAILABLE**, rather than an empirical failure of total forecasting. Separate questions have separate verdicts:

| Question | Independent verdict |
|---|---|
| Engineering, calculations and publication-date controls | PASS for the reviewed reconstructed research outputs and prepared registrations |
| Incremental guide-forecast superiority | Not established broadly: joint fails all three horizon gates; fixed passes the restricted p+4 common sample but fails on its complete standalone eligible history |
| Same-object revenue comparison with inherited Street snapshots | Favorable to joint on n11/10, conditional on the source-vintage limitations; not an observed expectation of management's guide |
| Physical cohort shares, cancellation survival and RNPL causality | Direct measurement UNAVAILABLE; existing precision/recovery assumptions fail separately; aggregate forecasting remains admissible |
| Current short catalyst / executable returns | Not established by this work; the two live GBV points exceed the common-cushion implied-guide comparator |

## What the full track says

L3's matched free-weight/fixed OLS ratios 1.1654 / 1.0155 reject adopting the extra estimated lag weight under that test; they do not reject the retained fixed operational conversion rule. Letter-close L3 accuracy admits the just-published lagged GBV and cannot be quoted as pre-event accuracy. L4 closed conditional model integration, not a new forecast edge or stock-return result. The earlier GE calendar-origin fixed model had mixed performance against direct guide growth, and its oracle-GBV diagnostic suggested useful input headroom. The newer joint study's favorable 14% / 17% improvement against fixed was real but deletion-sensitive. Physical-cohort uncertainty must not be substituted for these separate forecasting findings.

The new horizon comparison holds four models to identical rows. Dollar errors below are **raw issued-guide-midpoint RMSE, $M**; they are not the frozen harness's ±$0.5M interval errors.

| Last printed p → target | W1/W2 common n | Joint | Fixed | Direct issued-guide growth | Revenue growth / cushion |
|---|---:|---:|---:|---:|---:|
| p+2: next unknown guide | 11 / 10 | 64.29 / 63.83 | 74.59 / 77.01 | 59.06 / 61.31 | 118.69 / 124.25 |
| p+3: second unknown guide | 10 / 10 | 94.61 | 99.32 | 98.95 | 124.33 |
| p+4: third unknown guide | 9 / 9 | 131.44 | 117.74 | 132.46 | 149.84 |

The p+3 and p+4 W1/W2 sets are identical, not two replications. There are only three target-year clusters at those horizons. p+2 W2 is nested in W1. Multiple models/horizons/windows are reused historical comparisons, not independent confirmatory evidence.

Fixed p+4 on the declared nine common rows has ratios 0.888879 to guide growth and 0.785792 to revenue growth, paired 90% guide-growth ratio interval [0.772894, 0.979642], and no year/quarter deletion reversal. **The original restricted gate PASS is correct and retained.** The separately preregistered eligibility audit adds otherwise available fixed-model origins that joint's warmup excluded. On its own eligible history, fixed p+4 has W1 n12 RMSE159.10 versus144.57/153.30, ratios1.10052/1.03780; W2 n10 ratio0.909831 versus guide growth misses the predefined 10% hurdle. All candidate-specific gates fail. This is a scope limitation, not permission to erase the favorable restricted result or choose the sample producing the desired verdict.

Sources: `horizon_v1/results_v2/{scores_common,paired_comparisons,score_deletions,promotion_gates,coverage}.csv`; `horizon_v1/eligibility_audit_v1/{coverage_change,comparisons,deletions,promotion_gates}.csv` under `data/processed/forecast_methods/gbv_decision_0915_v1/`.

## The Street timing repair changes the evidence

Exact prior-release origins have zero eligible held DoltHub target p+2/p+3/p+4 quarterly rows. That is missing benchmark coverage, not a GBV loss. The predefined alternate date `start(p+2) −16 calendar days` matches 15 September for the current decision. Independent reconstruction confirms no intervening company print or initial guide for the reused points. It restores next-guide revenue consensus coverage: 14 W1 origins and10 W2, with snapshots one to seven days old. p+3/p+4 remain unavailable; no annual allocation or later-snapshot fill is justified.

On the fair joint/fixed/both-baseline common n11/10 sample, **joint revenue RMSE57.44/56.23 beats inherited DoltHub89.92/92.50**. Ratios0.638854/0.607882 have paired 90% upper bounds0.887521/0.767463. This favorable same-object result should be retained. Source certification is still incomplete: no selected historical row has row-specific AS OF equality proof in the held evidence. Limited proof of12 cells across3 other snapshots does not certify all14 used snapshots. Missing proof is not demonstrated future leakage; the result is conditional on inherited publisher-date vintages. Do not rename DoltHub's inherited family a licensed vendor or extrapolate to all Street analysts.

Issued-guide errors versus a common-cushion Street proxy are a different object: joint ratios0.743281/0.718833 have 90% upper bounds1.075301/0.991463. Direct guide growth remains more accurate on the same n11/10 rows. The candidate's guide-proxy sign accuracy8/11 and8/10 is no better than the simple majority counts9/11 and8/10. No additional return signal was mined.

Both source arms, own-coverage metrics and fair common-model tables remain published. Sources: `street_v1/results_v3/`, `street_v1/common_v1/`, `street_v1/sensitivity_v1/`; limitations in `GD_STREET_RESULTS_v1.md`.

## Live numbers and what they imply

Same 15 September cutoff, company information through 6 August, joint fit on all20 complete published quarters and fixed seasonal fits on the appropriate five/six published same-season observations. Q3 GBV26,505.53M and Q4 GBV23,611.91M are forecasts; Q2 GBV27,200M is reported. Trailing-eight arithmetic-mean actual/guide cushion is1.856743%. No forecast distribution was calibrated. Q3 guidance is already issued.

| Unknown guide target | Joint guide, $M | Fixed guide, $M | Direct guide-growth, $M |
|---|---:|---:|---:|
| 2026Q4 | 3,185.25 | 3,160.55 | 3,133.92 |
| 2027Q1 | 3,052.13 | 3,070.96 | 3,040.71 |
| 2027Q2 | 4,078.02 | 4,126.14 | 4,159.14 |

The September13 inherited Q4 eventual-revenue consensus is3,200M. Dividing by the assumed common cushion gives an implied guide comparator3,141.67M. Joint and fixed guides are respectively **+43.58M / +18.88M**, or **+1.387% / +0.601%**, above that proxy. Comparing their guides directly with revenue consensus instead gives −14.75M / −39.45M, but compares different objects. The shared cushion cancels in relative model/Street disagreement; it manufactures no observation of expected management guidance. These points therefore do not currently establish a below-Street guide thesis. Q1/Q2 2027 quarterly Street comparisons and exact future guide-event dates remain unavailable in the reviewed files.

At current Q4 inputs, projected GBV drives82.12% of joint predictor dollars and66.09% of fixed dollars. Q1/Q2 2027 live predictor dollars are100% projected in these fitted rules. These are model exposures, never observed booking shares. Sources: `horizon_v1/results_v2/predictions.csv`, `gbv_inputs.csv`, `gbv_contributions.csv`; `street_v1/common_v1/live_comparison.csv`.

## Variance, structural risk and a tested remedy

The independent preregistered decomposition keeps the exact origin fit and cushion. On p+2 W1 joint rows, input-component MSE7,555.99 plus oracle-residual MSE2,706.49 plus twice cross moment−6,129.62 equals total MSE4,132.86 ($M squared). Component errors offset substantially. It is invalid to add component RMS values or present diagonal loss terms as additive shares. The residual combines conversion/cushion/misspecification; no causal attribution follows. Fixed p+2 oracle guide RMSE46.81/48.81 versus production74.59/77.01 leaves possible input headroom, but unattainable perfect inputs are not a promised performance improvement from any particular proxy. At p+4 fixed common rows, oracle47.19 versus production117.74 leaves more headroom, conditional on the fitted rule and restricted sample.

The preregistered descriptive post-2025Q3 split has only four quarters, so identifies no RNPL effect or structural break. Its next-guide production errors are mostly **underprediction**: joint bias−77.51M, four of four below issued guide; fixed bias−48.80M, three of four below. Oracle residual biases are instead+20.17M/+11.86M. This does not support a simple claim that observed guide errors prove cancellation-driven revenue destruction. Payment/fee regime shifts remain legitimate future model risk; cash collection delay need not imply lost revenue. Source: `review_v1/horizon_v1/{covariance_reconciliation,regime_descriptive}.csv`. The parent's cited Q2 filing supplies the business-risk mechanism; this table does not estimate its magnitude.

The parent's separately preregistered **calendar-timed flight repair** was independently verified using saved quarterly flights and exact commit lineage. Training uses the same calendar offset as evaluation, six or more completed GBV outcomes, a bounded one-slope correction and all earlier eligible outcomes; no hidden future actual or commit enters. On n9 identical W1/W2 targets, joint flight RMSE80.30 is worse than no-flight67.12; fixed75.68 improves on78.81 but misses10%, and both lag direct-guide growth63.51. Only two evaluation features are genuinely current-quarter flight observations. Both remedy gates fail. This is distinct from the earlier release-origin flight failure, and does not reject every possible GBV proxy. No live flight-model guide forecast was emitted. Raw daily flight-state completeness remains unrecertified.

## What can improve the decision before 2 October

1. Preserve a common-date Excel table of reported inputs, unknown GBV forecasts, guide estimates, eventual-revenue consensus and the explicitly assumed cushion comparator. Include the simple guide-growth benchmark and a Q3-GBV/cushion sensitivity. A directional thesis must survive using consistent objects; do not choose the raw/adjusted comparison based on the desired sign.
2. Seek row-specific archival proof for the exact14 used quarterly snapshots, or an independently archived vendor panel at the same dates. Acceptance means exact target, source and before-origin publication/revision chronology, followed by the frozen same-object replay. This repairs source evidence; it creates no direct guide-expectation survey.
3. Evaluate any new booking-demand source as a bounded field/vintage pilot first. Require a relevant GBV outcome, historical before-origin observations, population/coverage documentation, and improvement on frozen common origins. The tested one-slope flight feature does not earn promotion. Avoid another unconstrained lag/feature search on the same few quarters.
4. Treat Q1/Q2 2027 as scenario sensitivities until horizon-specific input/benchmark evidence improves. A prospective frozen forecast ledger starts now, but cannot produce a new earnings outcome before the submission deadline. Physical cohort collection could address causal questions later; it is not a prerequisite for a modest aggregate forecast claim.
5. A central pitch pillar needs a documented current disagreement, a measurable operating/guide bridge and a catalyst with refutation conditions. Bottom-up fee/payment/mix evidence must earn that role independently. GBV gate failures do not make a replacement thesis correct, and no12-month valuation hurdle or post-announcement drift requirement was added here.

## Verification and reproducibility

Separate suites, **not one summed score and not new economic observations**:

| Independent reviewer suite | Result |
|---|---|
| Horizon source/formula/common-sample/statistics/deletion/gate replay, no author imports | 6,143 checks PASS |
| Actual-code future-value/guide poisoning, future-row removal, known-input controls, scope/live-history guards | 32 checks PASS |
| Street source selection, preserved missing rows, point joins, same-object statistics/paired bands/common table | 2,827 checks PASS |
| Candidate-specific eligibility scope, statistics, deletions and gates | 514 checks PASS |
| Calendar-flight source/training eligibility, slope/formulas, scores/paired bands/deletions/gates | 835 checks PASS |
| Prepared registry universe, points, timing, parameters, train counts and no bands/oracles | 3,392 checks PASS:421 rows,18 objects,18 LIVE |

Canonical code: `analysis/src/forecast_methods/gbv_decision_0915_v1/review_v1/{check_outputs.py,boundary_checks.py,street_checks_v2.py,supplement_checks_v2.py,registration_checks.py}`. Run from the worktree root with `.venv/Scripts/python.exe` from the main repo and a new `--out` directory; complete commands are in `review_v1/README_RESULTS_v1.md`. Receipts under the corresponding data folder: `horizon_v1`, `boundary_v1`, `street_v2`, `supplement_v2`, `registration_v1`. They bind exact source manifests and review code hashes.

Canonical horizon results_v2 manifest SHA256: `c631affb255e6e6655b73af2b260190a690da4836395931cd31217ade4df17ac`. Canonical Street results_v3 manifest: `f0d9f359a1c8f75cb3dec7145688185d0ac31f23d117a6fd68a84a5d0393fa76`. Two first reviewer attempts were retained: a `street` versus `DoltHub` comparator-label mismatch, and omission of latest company growth in the independently written flight training residual. Corrected new reviewer versions pass; neither was an author defect or model change. The parent's original-output preservation and deterministic rebuild suites remain separate and are not counted above.

Registration is approved for research. The reviewer has not written the shared registry or run its frozen scorers. Frozen score ratios whose baseline joins omit vintage/horizon cannot replace the local same-origin race. Local raw-midpoint gates must be distinguished from the mandatory interval-scored harness output. No broad model promotion or calibrated predictive interval is implied by registration.

## RESUME

GD-REVIEW is complete with no unresolved numerical blocker in the reviewed canonical outputs. Parent should finish additive registration and both frozen scorers, verify pre-existing scores/files remain unchanged, and consolidate the user-facing decision/visuals. Preserve the favorable conditional joint revenue result and restricted fixed p+4 pass, the standalone coverage failure, the raw-versus-proxy current signal reversal and all source limitations. The next useful work is a consistent decision-date worksheet and bounded provenance/input pilot, not more unconstrained fitting or a claim that physical nonidentification invalidates reduced-form forecasting.
