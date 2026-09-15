# Quant support — guide comparison and decision logic

13 September 2026 · parent task `01a09cd6-dbfc-7fe0-b673-430fd3e309e8` · support package WP-QVS. New explanatory note only; no model, forecast, registry, existing file or investment decision changed. This note records parent work alongside the independent supporting quant agent.

## Verdict

The existing fixed kernel remains the operational benchmark after L3's free-weight candidate failed its preregistered chronological promotion criterion. This supports retaining the simpler forecasting rule; it does not establish exact physical recognition shares, statistical dominance in every regime or a trading edge. A presentation must also compare like forecast objects. L4's negative guide-minus-revenue-consensus arithmetic does not itself establish a negative surprise to expectations for management's guide.

## Current L3 evidence inspected

Canonical source: `C:/Users/wille/Desktop/Citadel - ABNB/.worktrees/lane3-full/data/processed/forecast_methods/conversion_validation_v1/results_v2/` and the final closure/result notes in that worktree's `docs/revenue-forecast-strategy/05_backtests/`.

| Quantity | W1: 2023Q1–2026Q2, n=14 | W2: 2024Q1–2026Q2, n=10 |
|---|---:|---:|
| Free-weight USD revenue RMSE, millions | 63.1971 | 57.3924 |
| Matched fixed-weight OLS USD revenue RMSE, millions | 54.2275 | 56.5157 |
| Free/fixed ratio | 1.165407390 | 1.015512948 |
| Promotion result under the preregistered criterion | FAIL | FAIL |

These are L3's results, read and attributed here; the parent did not refit the models. W2 is nested in W1. Matched fixed OLS is not identical to K0's operational seasonal estimator. The full-history fitted weight, 0.78647848 on n=22, is descriptive and is not adopted. Excluding 2021 or using only 2023 onward produces materially different fitted weights in L3's existing sensitivity analysis. The independent support report discusses that evidence further.

Parent read the final acceptance JSON and recomputed 32 SHA-256 bindings: 24 output bindings, five source files, two reviews, and the separately repeated accepted-specification binding. All 32 matched. This is artifact-integrity verification, not an independent repetition of all statistical tests. Receipt SHA-256: `bf91d81a78e79368b8815ac33f626f0c12509158f4fe24161f34fd97d09bd973`.

Historical origins are letter-close vintages, including the just-printed previous quarter's GBV. They do not establish that the guide can be anticipated before that release. Today's conditional Q4 calculation additionally needs forecast Q3 GBV. Its complete uncertainty therefore includes upstream booking error as well as conversion, FX/RNPL assumptions and management's cushion.

## The same-basis comparison

Source: `C:/Users/wille/Desktop/Citadel - ABNB/.worktrees/lane4-full/docs/revenue-forecast-strategy/05_backtests/L4_REVENUE_RECONCILIATION_v1.md` and `L4_CLOSE_HANDOFF_v1.md`. This is one deterministic Q4 2026 reference, n=1; historical validation n=0. The consensus value is the existing captured Yahoo/LSEG-family revenue consensus from 13 September 2026 at 15:20 UTC. It was not refreshed by this support package.

All dollar amounts below are USD millions. Calculated labels do not turn the inputs into adopted forecasts.

| Object / calculation | Value | Interpretation |
|---|---:|---|
| L4 conditional review revenue, R | 3,179.343654 | Existing conditional model output |
| Captured Street revenue consensus, S | 3,161.021490 | Revenue consensus, not explicit guide consensus |
| Like-basis revenue gap, R − S | +18.322164 | +0.579628% of captured Street revenue |
| L4 cushion assumption, c | 1.790491031% | Trailing-eight median, n=8 realized outcomes |
| Implied L4 guide, R/(1+c) | 3,123.419115 | Conditional management-guide calculation |
| Implied guide minus revenue consensus | −37.602375 | Different forecast objects; not a measured guide-expectations surprise |
| Hypothetical Street guide, S/(1+c) | 3,105.419237 | Illustration applying the same cushion; not observed Street guide expectations |
| Like-basis hypothetical guide gap | +17.999878 | Conditional on imposing exactly the same cushion on both revenue forecasts |

This is a basis check, not a bullish or bearish recommendation. It shows why a sign can change when revenue and guide definitions are aligned. The correct evidence would be explicit dated expectations for management's guide, or a transparent, separately justified model translating revenue consensus into such expectations. Do not label the hypothetical transformed value as a reported consensus number.

## What the presentation should establish

1. **Prediction:** explain which fixed rule survives chronological comparison and at what information date; do not claim a precisely identified physical booking cohort split.
2. **Materiality:** report how joint conversion uncertainty and forecast GBV affect the guide in dollars. Small variation in an arithmetic contribution weight is not the complete forecast-error distribution.
3. **Expectations:** compare like objects, retain each vendor and date, and do not infer a guide surprise mechanically from a revenue-to-guide cushion.
4. **Investment implication:** establish earnings/cash consequences and the evidence for expectations changing. Neither L3 implementation acceptance nor these accounting identities overcome L2's lack of an established executable trading edge.

No extra statistical significance test was run. Time-series model evaluation should use historical training information only and a forecast horizon matching the intended use; see [Hyndman and Athanasopoulos, rolling-origin evaluation](https://otexts.com/fpp3/tscv.html). A variance significance question requires a specified null and valid assumptions rather than a generic p-value; see [NIST, chi-square variance test](https://www.itl.nist.gov/div898/handbook/eda/section3/eda358.htm). Those references describe methods, not ABNB-specific evidence.

## Exact arithmetic reproduction

Read-only command, from the original workspace root; exit 0. Decimal precision avoids altering the captured source inputs.

```powershell
@'
from decimal import Decimal
R = Decimal('3179.343654286')
S = Decimal('3161.021490')
c = Decimal('0.01790491031')
print('Revenue gap USDm:', R-S)
print('Revenue gap percent:', 100*(R/S-1))
print('Conditional own guide USDm:', R/(1+c))
print('Guide minus revenue consensus USDm:', R/(1+c)-S)
print('Hypothetical Street guide USDm:', S/(1+c))
print('Hypothetical like-basis guide gap USDm:', (R-S)/(1+c))
'@ | & '.venv/Scripts/python.exe' -B -
```

## RESUME

Read this note alongside the independent WP-QVS variance/claims report. L3 retains ownership of conversion estimation and validated specification delivery; L4 retains model and memo integration. When reviewing the presentation, keep the dated revenue comparator separate from guide expectations, preserve joint uncertainty and upstream GBV risk, and use only immutable accepted source versions. Any integration, revised forecast or investment adoption is separate from this read-only support audit.
