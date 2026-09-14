# REFUTE F — vintage audit

Agent `refute_f_vintage` · 2026-09-13 · branch `codex/lane2-full` · audit started 17:35 UTC

## Verdict

**SURVIVED.** The exact conditional sentence survives the vintage lens. Independent arithmetic reproduces +1.969114pp in Q4 2025, +9.705899pp in Q2 2026 and $3,185.195735M in the selected Q4 2026 stress. No restated unearned-fee input or historical D1 backdating is required. This verdict is confined to the sentence's explicit frozen-model and assumed-stress wording: historical forecast effectiveness remains **underpowered/unmeasured, W1 n=0 and W2 n=0**. The hardest attack establishes that the unpaid-share levels are retrospective and materially dependent on the selected fit. They cannot be relabelled as observed RNPL stock or estimates available at those historical quarter-ends.

## Pre-registered pass line

Written 2026-09-13 17:35 UTC, before executing the independent audit:

> Not applicable — the refuter's output is the verdict. A refuter that only praises has failed. "Partial" does not count as survived.

Exact sentence under review: “Our frozen-model estimate of excess unpaid share rose from 2.0pp in Q4 2025 to 9.7pp in Q2 2026, and an assumed 4pp incremental RNPL cancellation stress yields $3,185M of Q4 2026 revenue under the team nights path; these conditional estimates do not identify an RNPL causal effect.”

Planned attacks: independently rebuild the frozen stock allocation and same-season excess; look for restated unearned-fee circularity; remove future revenue/guide denominators from the stock statistic; reconstruct the live Q4 stress from primitive arithmetic and the declared ADR assumption; check every registration's date and scenario label for September-parameter backdating; inspect whether the freeze is retrospective and can be mistaken for historical PIT; test sensitivity to one inherited coefficient fit rather than treating model structure as observed stock. No new forecasts will be registered and no scorer will be run.

## What ran

The parent was notified of this claim before the audit and owns the shared workboard update. This agent created only `analysis/src/forecast_methods/refute_f_vintage_v1/`, `data/processed/forecast_methods/refute_f_vintage_v1/` and this note. The required brief/workboard reads preceded the narrower REFUTER instructions. Subsequent reads covered the package note, named source inputs, package code/output/registry, the convention, and the named K0/K1 implementations needed to inspect their arithmetic. No network, external account, new forecast registration or scorer ran.

Exact execution command, from the repository root:

```text
./.venv/Scripts/python.exe -X utf8 analysis/src/forecast_methods/refute_f_vintage_v1/run.py
```

Exit **0**; shell-reported wall time **1.214 seconds**, internal calculation **0.191 seconds**. The initial audit execution passed; there is no discarded test failure. It imports no F or K0 model functions. Instead it independently sums the booking-cohort fee stock, estimates the documented lambda variants from the raw KPI panel and applies the declared conditional ADR and D1 cell. The ADR is an assumed input taken at full precision from F's scenario output; this audit does not independently establish an economically correct ADR forecast or refit the stock coefficients.

Read-only inspections also used `Get-Content` on the named files and:

```text
rg -n "restat|unpaid_share_stock|basis=|source_date|SOURCE_DATE|vintage_date|window=|knowable_from" analysis/src/forecast_methods/rnpl_v2/run.py data/processed/forecast_methods/rnpl_v2/acceptance.json
```

Exit **0**. Detailed receipts, immutable-input hashes, stock reconstruction, alternative-fit sensitivity, lambda selection and Q4 training observations are in the new audit output folder. No source output was regenerated.

## Results and explicit refutation attempts

No consensus is consumed, so vendor and consensus-timestamp checks are not applicable. Dollars are USD millions. A “survived” row below means the attack did not defeat the **exact sentence**, not that its wider economic interpretation passed a predictive test.

| # | Claim under attack → attack | n / vintage basis | Evidence and verdict |
|---|---|---|---|
| 1 | +2.0pp→+9.7pp → reconstruct fee stock from raw GBV, frozen coefficients and reported UF without calling F | 2 headline observations; seasonal norms n=3 and n=4; retrospective | **Survived.** Rebuild gives 1.969113826 and 9.705898804pp. The maximum fee-stock difference across all 21 available reconstructed quarters is $9.09e-13M; maximum excess difference is 2.22e-14pp. |
| 2 | Excess is not imposed by RNPL restatement → remove the full revenue/guide inputs and inspect the UF construction | 3 recent observations; retrospective | **Survived.** The statistic uses reported UF divided by fitted fee stock, not a mechanically RNPL-restated fee series. Independent reconstruction works using only quarter, season, GBV and UF. The coefficients remain an inherited model input rather than an observed denominator. |
| 3 | Q2 excess requires later Q3 revenue or its guide → rebuild the equivalent paid/booked ratio at three different revenue denominators | 3 observations × 3 denominator values; retrospective | **Survived.** Using $3,000M, $4,730M or $6,000M cancels from the ratio, with maximum unpaid-share difference 2.22e-16. This only clears the headline stock statistic. F's separately reported coverage and fee-only-u sensitivities do use next-quarter outcomes or the Q3 guide and must retain their retrospective labels. |
| 4 | Historical stock levels were available at the stated quarter-ends → inspect the frozen fit and metadata | 1 inherited 8-parameter fit, n=16 fitted observations; 4 seasonal norms | **Survived as worded; the stronger PIT interpretation is rejected.** F explicitly labels the stock output retrospective. A September frozen fit applied to earlier quarter-ends is not an archived historical forecast, and it is not evidence that 1.969pp was knowable in Q4 2025. “Frozen-model” is essential; adding “retrospective” would be clearer. |
| 5 | 9.7pp is a stable measured unpaid share → apply the two other existing pooled coefficient sets | 3 alternative fits; respective fit n=20/16/14; each has 8 parameters; retrospective | **Survived only as the stated selected-model estimate.** Q2 excess is 13.3417pp for the full-sample fit, 9.7059pp for the selected ex-COVID fit and 10.1010pp for the post-2023 fit. Q4 2025 is 4.9333/1.9691/2.3843pp respectively. This attack defeats an invariant measured-level reading. The direction rises in each case, but the alternatives are correlated structural sensitivities, not independent evidence. |
| 6 | $3,185M under 4pp stress → independently reconstruct seasonal lambda, team nights × declared ADR, and the chosen D1 cell | 1 Q4 scenario; lambda n=5; LIVE 2026-09-13 | **Survived.** EWM lambda 12.040366938% gives pure revenue $3,214.775751M. D1's rounded nights share inverted with a 1.25 ADR ratio implies GBV share 23.003172%, hence gross leakage 0.920126881%. Multiplication gives $3,185.195735M, a $29.580016M stress reduction. |
| 7 | September assumptions inflate a historical backtest → inspect every registry date, window and note | 12 rows; 6 distinct scenario-quarter values × 2 replay labels; LIVE only | **Survived.** Every vintage and knowable date is 2026-09-13; every row states D1 assumptions dated 2026-09-11 and no causal inference. Zero historical rows exist in W1 or W2. PIT/full_sample are identical LIVE repetitions, not twelve observations or two historical replications. The source date is the package's documented assumption date, not an independently authenticated creation timestamp for the D1 CSV. |
| 8 | Correct arithmetic establishes an incremental RNPL loss → inspect what enters the stress and what was measured | 1 selected stress cell; W1/W2 forecast n=0/0 | **Survived because the sentence calls the increment assumed and disclaims identification.** The formula has no estimated remaining backlog survival, incremental cancellation hazard or adjustment for cancellation risk already embedded in lambda/net GBV. “$29.580M expected RNPL loss” would fail this audit; a gross conditional stress is the supported interpretation. |

Independent central reconstruction:

| Quantity | n / basis | Audit value |
|---|---|---:|
| Q4 2025 excess | 1 observed balance; 3 norm quarters; retrospective model | 1.969113826pp |
| Q1 2026 excess | 1 observed balance; 4 norm quarters; retrospective model | 8.047784019pp |
| Q2 2026 excess | 1 observed balance; 4 norm quarters; retrospective model | 9.705898804pp |
| Q4 lambda | 5 same-season observations, 2021Q4–2025Q4; EWM chosen on retrospective W1 LOO n=14, available by run date | 12.040366938% |
| Q3 team nights and fixed ADR | 1 declared path × 1 conditional ADR assumption | 146.8264M × $180.144526612 |
| Q3 conditional GBV | 1 LIVE conditional input | $26,449.972322M |
| Q4 weighted GBV denominator | 1 LIVE scenario; Q3 conditional GBV and Q2 reported GBV | $26,699.981548M |
| Q4 pure / stressed revenue | 1 LIVE selected scenario each | $3,214.775751M / $3,185.195735M |

The omitted middle headline is **8.0pp when rounded to one decimal**, consistent with F's correction. It does not refute the exact sentence, which states only the two endpoints. D1 share rounding explains why leakage is 0.920126881%, rather than exactly 0.920000000%; this changes no whole-million headline.

## What failed or could not be done

The audit cannot establish historical predictive performance, a historical PIT stock series, or a causal RNPL cancellation loss. The necessary archived coefficient vintages and identified remaining-survival inputs do not exist in the audited package. Its historical W1/W2 performance count is zero, not a passed or failed backtest. The stock metric's level is materially model-dependent; the independent calculation confirms arithmetic conditional on frozen coefficients, not coefficient identification. No independent alternative ADR was estimated. The package's reported accounting quotes were outside this lens's numerical tests; the mechanism refuter owns migration attribution.

## Interpretation

No corrected endpoint or Q4 whole-million value is needed. For publication, a clearer vintage wording would be: “Using a retrospective frozen model, excess unpaid share rose from 2.0pp in Q4 2025 to 9.7pp in Q2 2026. At September 13 assumptions, a gross 4pp incremental cancellation stress produces $3,185M of Q4 revenue under the team nights path; neither calculation identifies an RNPL causal effect.” This is a clarification, not evidence of a historical signal. Keep the source note's model dependence and conditional ADR accessible beside the sentence.

## RESUME

Parent should incorporate this **SURVIVED** exact-sentence vintage verdict with the independent power and mechanism verdicts, update its owned workboard/run log, and run both scorers at CLOSE. Keep this audit and its receipts under their new names. If the sentence is strengthened to claim a contemporaneous historical signal, an observed RNPL stock, an expected incremental loss or forecast accuracy, it requires a new audit with archived fits and independent survival evidence. No registry or input repair is requested by this lens.
