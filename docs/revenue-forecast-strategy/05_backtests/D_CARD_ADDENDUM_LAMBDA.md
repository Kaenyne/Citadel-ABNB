# D — lambda and backlog card addendum

Agent: sub-D · preregistered 2026-09-12 · branch `codex/lane1-full`

**partial** — the lambda identity and reported funds-payable growth are scoreable from the specified publications if both are available on 6 November; the model backlog split and excess-unpaid series are not directly observable from those publications. The literal all-rows pass line is not met. This addendum preserves the existing card and makes no team decision.

## Pass line, written before verification

“A stranger could score every row on 6 Nov with only the press release and the 10-Q.”

Verification will check the arithmetic behind the fixed lambda cutoffs, the source's quarter labels and its limits on identification, and whether every proposed outcome is actually observable on 6 November 2026. An unavailable model decomposition will be recorded as unavailable; it will not be awarded a pass. Historical descriptive samples will be labelled separately from W1/W2 predictive tests. No forecasts will be registered because this package creates scoring instructions, not a forecasting method.

## Results: proposed rows, verbatim

All shares are percentages; excess-unpaid changes are percentage points. Owners below are existing roles, not new assignments. Details and boundary conventions immediately below are part of each row.

| Item; n | Value | Band | Scoring rule | Source on 6 Nov | Owner |
|---|---|---|---|---|---|
| Q3 2026 lambda; historical n=3 | 100 × revenue / 27,866.666667 | 17.09 / 16.93% | At least 17.09: no alarm; 16.93–17.09: warn; below 16.93: escalate. Boundary overlap: ambiguous. | Q3 revenue, release/10-Q | P1 |
| Q3-end split; norm n=3 | Paid 35.0 / unpaid 32.4 / unbooked 32.6 | No identified band | Descriptive estimate of next-quarter revenue; not scoreable as a disclosed outcome. | No direct release/10-Q field | P1 |
| Q4-end split; norm n=3 | Paid 30.3 / unpaid 27.4 / unbooked 42.3 | No identified band | Descriptive estimate of next-quarter revenue; quarter-end also remains future on 6 Nov. | No direct release/10-Q field | P1 |
| Excess unpaid; n=3 recent quarters | +2.0 / +8.1 / +9.7pp | No forecast band | Recompute with frozen stock model; classify against +9.7pp. Without model stock, unavailable; no RNPL causal verdict. | Unearned fees in 10-Q; model stock additionally required | P1 |
| Funds payable; n=1 prospective print | +5 to +11%: deferral on schedule | Inclusive [5,11]% | Record reported growth and band membership; interpretation pending D-06, numbering conflict unresolved. | 10-Q funds payable; prior-year base 7,209M | Theo |

## Exact scoring instructions

**Lambda.** All dollar inputs are USD millions. The frozen base is `(2 × 27,200 + 29,200) / 3 = 27,866.666666…`; retain that full precision. The percentage thresholds requested by the brief correspond to revenue **4,762.413333…** and **4,717.826666…**, respectively. K1's approximate dollar labels 4,761 and 4,719 came from more precise statistical cutoffs, 17.086 and 16.934; they are not equivalent to the specified 17.09 and 16.93 thresholds. This addendum uses the specified percentages as the controlling rule and does not silently switch to those legacy dollar labels.

For revenue printed as an integer number of USD millions `r`, the scoring interval is `[r−0.5,r+0.5]`; transform both ends through `100 × revenue / base`. If the entire interval is at least 17.09, record NO ALARM. If its lower endpoint is at least 16.93 and its upper endpoint is strictly below 17.09, record WARN. If its upper endpoint is strictly below 16.93, record ESCALATE. Otherwise record AMBIGUOUS. For an exact amount, 17.09 belongs to NO ALARM and 16.93 belongs to WARN. The lag base is frozen as the card's definition; this is not a confidence interval for true unrounded historical GBV. Missing publication or unusable units means ABSENT, never SUPPORT. Record the file, page, unit, extraction time and any subsequent restatement separately.

K0 v2's `control_chart.csv` reports Q3 mean **17.2393618512%**, standard deviation **0.1323888064pp**, n=3, and an ordinary mean-minus-two-SD level of **16.9745842384%**. That is a different chart from K1's prediction-dispersion rule and does not replace these fixed thresholds. A lambda alarm is a revenue-conversion alarm: it cannot identify RNPL cancellations separately from weaker in-quarter bookings. Three historical Q3 cells do not calibrate a reliable false-alarm probability.

**Splits and quarter labels.** K1 §2.3 labels the row by the **quarter-end**, and the estimated shares refer to **next-quarter revenue**. Thus 35.0/32.4/32.6 is the Q3-end norm for Q4 revenue; 30.3/27.4/42.3 is the Q4-end norm for Q1 revenue. If “Q3 and Q4” means the target revenue quarters, the relevant norms are instead **Q2-end → Q3: 41.5/23.5/35.0** (n=4) and **Q3-end → Q4: 35.0/32.4/32.6** (n=3). The latest K1 Q2 2026 estimate for Q3 revenue is **36.0/30.5/33.6**, n=1, conditioned on that quarter's guide; its 100.1% sum is rounding. None of these is a new estimate of the September or December 2026 stock.

The source explicitly says the level of booked-but-unpaid fees is not identified. A balance sheet reports paid liabilities, not an allocation of every booking to its future stay quarter or all unpaid bookings. The percentage totals summing to 100 is an accounting construction, not outcome verification. Do not award a hit to these rows because the shares sum correctly. Record NOT OBSERVABLE FROM SPECIFIED SOURCES and retain the explanatory snapshot; no support/refutation statistic follows.

**Excess unpaid.** The three values correspond to **2025Q4, 2026Q1, 2026Q2**, respectively, from K1 §2.4. Pre-RNPL norms use 2022Q1–2025Q2; the corresponding Q4/Q1/Q2 norm counts are 3/4/4. They are retrospective, conditional on the fitted stock model, not historical PIT forecasts. Define a future remeasurement as `E_q = 100 × [(1 − UF_q / F_q) − u0_season]`, where `F_q` is the fee-stock estimate from the **unchanged K1 model** and `u0_season` its unchanged pre-RNPL norm. Do not refit parameters or seasonal norms after seeing the print. Record `E_Q3 − 9.7`: a wholly positive interval means above the latest displayed run-rate, wholly negative means below, and overlap with zero means ambiguous. Treat the displayed reference 9.7 as `[9.65,9.75]` for its one-decimal rounding. This is a proposed descriptive direction rule, with no pass threshold for a trade and no cancellation identification.

Unearned fees alone cannot supply `F_q`. Computing that model stock requires historical GBV, frozen coefficients and the allocation schedule in addition to the release/10-Q. Under the brief's two-publication restriction, score this row UNAVAILABLE and retain all three historical observations. The rounded source columns cannot recreate +8.1pp exactly (45.0 minus 37.0 rounds to 8.0); retain the source's full-precision-derived +8.1 rather than pretending the displayed columns are exact. No model was fitted or stock reconstructed in this non-modelling package.

**Funds payable.** Compute `g = 100 × (FP_2026Q3 / 7,209 − 1)`. Exact band dollar endpoints are **7,569.45M** and **8,001.99M**. For whole-million disclosed balances, interval-score both numerator and the displayed 7,209M denominator using ±0.5M; the minimum growth uses the low numerator/high denominator, and the maximum uses the high numerator/low denominator. Wholly inside [5,11] is INSIDE; wholly below 5 is BELOW; wholly above 11 is ABOVE; boundary overlap is AMBIGUOUS. A missing comparative balance or missing filing is ABSENT. This is a measurable band test, not adopted evidence of the cause.

The Lane-1 brief calls this **pending D-06**; the original card's INT-11 points to **D-10**, and its decisions table uses D-06 for a different subject. Both labels are preserved for human reconciliation; this package does not resolve either. The wording “deferral on schedule” is the inherited candidate label, held pending that decision. K1 §2.4 also says funds payable is affected by FX translation and disputes the original card's fee-migration interpretation. Record reported growth first; a causal interpretation additionally needs the translation reconciliation and the companion unearned-fees/GBV evidence. Do not label a number inside the band as proof of deferral or cancellation, or substitute cash-flow change for year-on-year balance growth.

## What ran and verification

Preregistration was written before arithmetic checks. Read-only source inspection used:

```powershell
rg -n -C 7 '2Q26 \(live|excess.unpaid|17\.09|16\.93' docs/revenue-forecast-strategy/05_backtests/K1_KERNEL_WEIGHTS_AND_BACKLOG.md
rg -n 'INT-11|D-06|D-10' docs/revenue-forecast-strategy/05_backtests/PREREG_ABNB-INT-v1.md
Get-Content data/processed/forecast_methods/kernel_engine_v2/control_chart.csv
```

Arithmetic was checked with the project venv, from the repo root, exit code 0:

```powershell
@'
from decimal import Decimal
base=(Decimal(2)*Decimal(27200)+Decimal(29200))/Decimal(3)
print('base_musd =',base)
for lam in ('17.09','16.93'):
 print('lambda_pct',lam,'exact_revenue_musd',base*Decimal(lam)/100)
for q,values in [('Q2_end_for_Q3',(41.5,23.5,35.0)),('Q3_end_for_Q4',(35.0,32.4,32.6)),('Q4_end_for_Q1',(30.3,27.4,42.3))]:
 print(q,'sum_pct',sum(values))
print('Decision: compare lambda at full precision; legacy whole-dollar equivalents conflict with rounded lambda cutoffs.')
'@ | & ./.venv/Scripts/python.exe -X utf8 -
```

The arithmetic command ran within the 3.5-second source-inspection batch. Output: base 27,866.666666…, threshold revenues 4,762.413333… / 4,717.826666…, and sums of 100.0% for all three norm rows. No package model, registry write, external request, scorer run or existing-card edit was performed. Free fitted parameters: **0**. Two inherited alarm cutoffs and one inherited balance-growth band are prespecified rules, not fitted parameters.

| Verification | n | Result | Standing |
|---|---:|---|---|
| Fixed lambda thresholds | 2 | Exact dollar equivalents reconciled | Arithmetic, not predictive validation |
| Seasonal split sums | 3 | 100.0% each | Descriptive identity only |
| Prospective publication-only scoreability | 5 rows | 2 measurable rows; 3 unobservable model/future rows | Literal pass line not met |
| W1 predictive tests | 0 | Not applicable | No forecast registered |
| W2 predictive tests | 0 | Not applicable | No forecast registered |

## Proposed memo sentence

“The Q3 revenue-conversion card warns below 17.09% and escalates below 16.93%, using three historical Q3 cells; it does not identify RNPL cancellations.”

## RESUME

This addendum is a completed partial result: five rows are specified, two are directly measurable if the publications arrive, and three must remain descriptive or unavailable under the stated source restriction. Before formal card signature, the responsible team should reconcile the funds-payable decision label and interpretation; no decision was taken here. On 6 November, copy these rows to a new scored file, retain the frozen lambda base and rounding rules, record primary-publication page/units/time, and leave unavailable outcomes explicitly unavailable. Any later model-stock reconstruction belongs in a new package with its own frozen inputs; do not overwrite K1, K0 or the existing card.
