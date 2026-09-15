# REFUTE F — power

Agent refute_f_power · 2026-09-13 · parent branch `codex/lane2-full` · approximately 9 minutes active work

## Verdict

**SURVIVED.** The exact sentence survives as explicitly conditional arithmetic. It does not establish statistical significance, predictive usefulness, or a causal effect. Historical forecast effectiveness is **underpowered/unmeasured, W1 n=0 and W2 n=0**. This verdict is narrower than a pass for package F, whose original acceptance line remains PARTIAL.

Exact sentence reviewed: “Our frozen-model estimate of excess unpaid share rose from 2.0pp in Q4 2025 to 9.7pp in Q2 2026, and an assumed 4pp incremental RNPL cancellation stress yields $3,185M of Q4 2026 revenue under the team nights path; these conditional estimates do not identify an RNPL causal effect.”

The strongest attack is that the apparent evidence comprises deterministic scenarios and repeated labels, with no observed RNPL treatment/control contrast. That attack defeats any empirical claim that 4pp is measured, or that the revenue stress is predictively validated. The exact sentence already excludes those claims by describing the coefficient as assumed and the outputs as conditional.

## Pre-registered pass line

Written **2026-09-13 17:36:35 UTC**, before numerical audit execution, in `data/processed/forecast_methods/refute_f_power_v1/PREREG.md`:

> Not applicable — the refuter's output is the verdict. A refuter that only praises has failed. "Partial" does not count as survived.

The preregistration fixed independent endpoint/stress arithmetic checks, specification counts, 95% Wilson intervals, and exact illustrative one-sided binomial power at alpha 5%, power 80%, against a 5% alarm null. No incremental RNPL MDE would be invented without a cohort denominator and estimable contrast. No frozen inputs, upstream outputs, registry, or scorer were changed.

## What ran

From the repository root:

```text
./.venv/Scripts/python.exe -X utf8 analysis/src/forecast_methods/refute_f_power_v1/run.py
```

Exit **0**, shell wall time **1.78 seconds**. A preliminary read-only Python CSV inventory also exited 0 in 0.29 seconds. The audit uses its own Wilson formula and exact SciPy binomial survival probabilities, reads the F CSVs and original D1 grid, and writes `data/processed/forecast_methods/refute_f_power_v1/audit.json`. Its assertions verify both source endpoint arithmetic and the selected scenario's revenue. No test failed. No registration or scorer execution occurred; those remain the parent's responsibility.

Inputs: `ALPHA_F_RNPL.md`; `lane2/CONVENTION.md`; F's `paid_backlog.csv`, `seasonal_norms.csv`, `live_scenarios.csv`, `leakage_grid.csv`, `lambda_chronological_alarms.csv`, `false_alarm_rates.csv`, and `input_manifest.csv`; `registry/rnpl-v2__revenue_next_q.csv`; original `overnight2/D/D1_rnpl_cohort_scenarios.csv`. Mandatory AGENT_BRIEF and WORKBOARD were read first under repository instructions. No consensus, external research, licensed store, or Airbnb site was used.

## Results

### Arithmetic and effective sample

The seasonal norms were recalculated from F's frozen fee-stock rows, rather than accepted from the displayed excess column. This audit conditions on the upstream frozen stock fit; it does not refit its parameters.

| Object | Actual n | Independent calculation | Evidence basis |
|---|---:|---:|---|
| Q4 2025 excess unpaid | 1 recent quarter / 3 same-season norm quarters | 1.969113826pp | Retrospective frozen-model estimate |
| Q1 2026 excess unpaid | 1 / 4 | 8.047784019pp | Retrospective; rounds to 8.0, not 8.1 |
| Q2 2026 excess unpaid | 1 / 4 | 9.705898804pp | Retrospective frozen-model estimate |
| Q4 2025 to Q2 2026 change | 2 endpoints, not independent fitted estimates | 7.736784978pp | Difference between seasonally normalized model outputs |
| Q4 team pure kernel | 1 conditional cell | $3,214.775750894M | LIVE, current information |
| Q4 assumed cancellation coefficient | 1 selected scenario / 0 measured incremental effects | 4.000pp | Assumed, not estimated |
| Q4 implied RNPL GBV flow share | 1 selected D1 cell | 23.003172029% | Inverse identity from rounded 19.29% nights share and 1.25 ADR ratio |
| Q4 stress revenue | 1 selected cell | $3,185.195735041M | $3,214.775750894 × (1 − 0.23003172029 × 0.04) |
| Q4 stress reduction | 1 selected cell | $29.580015853M / 0.920126881% | Conditional gross loss, not measured incremental loss |
| Historical forecast observations | W1 0 / W2 0 | No backtest statistic | Underpowered/unmeasured |

### Specifications and duplicated evidence

| Choice or output | Count n | Implication |
|---|---:|---|
| D1 grid axes | 5 share paths × 3 ADR ratios × 5 cancellation cases × 3 lead times × 3 lead uplifts × 3 rebooking offsets | 2,025 scenario cells, all dated 11 September 2026 |
| F leakage outputs | 4,050 rows = 2,025 cells × 2 quarters | Not observations; only 37 distinct leakage values per quarter at 12-decimal rounding |
| Nights paths | 3 | Team, Theo, ex-NA; two target quarters |
| LIVE registry | 12 rows | 6 path-quarter cells × 2 identical current-information replay labels |
| Distinct registered quarter/value pairs | 3 | One Q3 value; two Q4 values; neither repeated paths nor PIT/full_sample double the evidence |
| Fee-only stock sensitivity | 3 B assumptions × 3 recent quarters = 9 cells | Scenario sensitivity, not an identified RNPL share |
| Alarm rules | 3 | Chronological mean±2sd, fixed warning 17.09%, fixed escalation 16.93% |
| Historical populations | 2 window labels; chronological pre-RNPL/all-history subsets | W2 is within W1; its usable chronological rows are actually identical here |
| Return horizons or 0.5/1/1.5pp guide-gap thresholds | 0 in F | Those A/B searches do not apply and are not falsely charged to F |

These are counts of visible specifications and outputs, not an assertion that 2,025 independent hypothesis tests were performed. The package does not report selecting the lowest p-value or optimizing a loss over these scenarios. Conversely, no inferential weight can be assigned to the number of grid cells. There is no empirical reason in this evidence to prefer 4pp over the other assumed cancellation cases.

For the same single team Q4 pure-kernel input, all D1 leakage cells span **$3,162.70–$3,214.78M** (n=2,025 scenarios, 0 validation observations); $3,185.20M is one interior assumption. That span is a sensitivity range, never a confidence interval. It excludes uncertainty in GBV, fitted lambda, and the overlap of stress with cancellations already embedded in the baseline.

Inherited complexity is also material: the stock reconstruction uses 8 fitted K1 coefficients plus 4 seasonal mean norms; the revenue model uses 4 inherited fitted seasonal coefficients and a fixed lag weight. Those quantities and scenario assumptions are not extra independent observations. No endpoint or stress sampling distribution is supplied by F.

### Wilson intervals at the actual n

For counts k/n, the audit uses z=1.959963985 and the standard Wilson score formula. These are descriptive binomial calculations conditional on exchangeable independent alarms. Serial dependence, estimated chart limits, and threshold selection prevent treating them as fully calibrated sampling intervals for an RNPL test.

| Alarm sample/rule | W1 k/n | W1 95% Wilson | W2 k/n | W2 95% Wilson |
|---|---:|---:|---:|---:|
| Chronological pre-RNPL empirical false alarms | 1/2 | 9.45%–90.55% | 1/2 | 9.45%–90.55% |
| All chronological alarms, not all known false | 1/6 | 3.01%–56.35% | 1/6 | 3.01%–56.35% |
| Fixed Q3 warning, retrospective | 0/3 | 0%–56.15% | 0/2 | 0%–65.76% |
| Fixed Q3 escalation, same retrospective cells | 0/3 | 0%–56.15% | 0/2 | 0%–65.76% |

The six chronological cells are 2025Q1–2026Q2, all inside W2. Thus W1 and W2 use exactly the same six quarters, or the same two pre-RNPL quarters. The fixed Q3 samples are 2023–2025 and their 2024–2025 subset. They are not two independent confirmations. The note correctly reports the overlap and retrospective threshold use. Zero fixed-threshold alarms does not establish a low false-alarm probability; its nominal Wilson upper limit alone exceeds 56% at n=3.

No Wilson interval is appropriate for continuous excess-unpaid pp or a deterministic dollar stress. Treating any of the 2,025 scenario rows as Bernoulli trial outcomes would fabricate a denominator.

### Minimum detectable effect

For the actual RNPL causal coefficient or predictive revenue loss, **MDE is not identified**: W1 n=0, W2 n=0; no observed RNPL/control cancellation-rate contrast or sampling variance. An assumed 4pp difference is not a detectable-effect claim.

To quantify how weak even the available alarm sample is, the preregistered illustrative design tests a known 5% alarm probability against a larger probability, one-sided alpha ≤5%, exact binomial test, 80% power. This is an alarm-frequency calculation and must not be interpreted as cancellation power. The 5% null is an explicit illustrative design choice, not F's established calibration.

| Independent trials n | Reject at alarms ≥ | Exact size | Detectable alarm probability | Minimum increase above 5% | Power for a 5%→9% alarm change |
|---|---:|---:|---:|---:|---:|
| 2 | 2 | 0.25% | 89.44% | 84.44pp | 0.81% |
| 3 | 2 | 0.725% | 71.29% | 66.29pp | 2.28% |
| 6 | 2 | 3.277% | 42.24% | 37.24pp | 9.52% |

Even the most generous of these sample sizes cannot reliably discriminate modest alarm-rate shifts. Its actual dependent, fitted chart is less interpretable than the ideal independent design; the table is not a claimed bound on its true power.

## Explicit refutation attempts

| Claim targeted | Attack and result | Outcome |
|---|---|---|
| Exact sentence's 2.0→9.7pp endpoint arithmetic | Recalculate seasonal norms and each excess from frozen stock values. Obtain 1.969114→9.705899pp. Both round as stated; the 8.1 middle observation fails, but is absent from the sentence. | **Survived** |
| Exact sentence's “rose” as a frozen-model comparison | Attack shifting seasonal norms and singleton endpoints: Q4 norm n=3 versus Q2 n=4, with shared fitted coefficients. This precludes an unqualified measured population change or trend significance. The exact wording identifies a frozen-model estimate, which the calculation supports. | **Survived**, conditional only |
| Exact sentence's $3,185M under an assumed 4pp stress | Independently invert the raw D1 nights-share identity and recompute the gross revenue loss. $3,185.195735M rounds to $3,185M. It is not an empirical expectation or a net loss after rebooking. | **Survived**, assumed gross stress only |
| Stronger reading: 4pp is statistically supported by many scenarios | Count 2,025 cells and just 37 unique losses per quarter. There are no observed incremental RNPL effects. Grid multiplicity provides no sample size or confidence. The exact sentence's word “assumed” survives; the stronger reading fails. | **Refuted** for empirical support |
| Stronger reading: twelve registered forecasts validate the stress | De-duplicate to six path-quarter cells and only three quarter/value pairs; all are LIVE and the two replay labels use identical data. Historical validation remains 0/0. | **Refuted** for forecast validation |
| Stronger reading: W1 and W2 provide independent support | Both chronological windows are the exact same six cells (and same two pre-RNPL cells); fixed-rule W2 is a subset. The note admits this. | **Refuted** for independent confirmation |
| Stronger reading: zero fixed-rule alarms establish a reliable RNPL detector | At 0/3 the Wilson upper limit is 56.15%; at 0/2 it is 65.76%, even before threshold selection and dependence. Exact sentence does not invoke detector reliability. | **Refuted** for calibrated detector power |
| Exact sentence's limitation on causal identification | Try to recover an incremental RNPL contrast from stock observations, scenario cells, or alarms. None separates RNPL from payment mix, fee economics, booking timing or baseline cancellation exposure. No cohort/control sample or causal MDE exists. | **Survived**; non-identification is necessary |

## What failed or could not be done

A forecast-skill test, a significance test for the frozen excess-share rise, and an incremental RNPL cancellation MDE cannot be constructed from these outputs without additional identification and uncertainty assumptions. Conditional arithmetic is not a substitute. The 8.1pp middle headline remains incorrect; the package's correction to 8.0pp is confirmed. There is no new failing frozen test and no withheld result.

## Interpretation

Keep the exact sentence's qualifiers intact. It is a reproducible description of model outputs and an explicit assumption. It provides no power-based grounds to call the scenario probable, to attach an RNPL causal label to the 7.737pp change, or to use the alarm chart as a calibrated detection system. The strongest decision-useful additional data would be paid/unpaid RNPL cohorts and comparable non-RNPL cohorts with remaining cancellation outcomes; repeatedly expanding the scenario grid cannot supply that evidence. This refuter makes no trade or team decision.

## RESUME

Parent should record SURVIVED for the exact conditional memo sentence under the power lens, preserve F's overall PARTIAL package verdict and the 8.1→8.0 correction, and count neither nested windows nor duplicate LIVE replay labels as independent evidence. The new audit script and JSON reproduce the numbers above without modifying any F input or invoking a scorer. If the sentence later loses “frozen-model,” “assumed,” “conditional,” or its causal-identification limitation, rerun hostile review because the surviving claim would have changed materially.
