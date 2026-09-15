# F — RNPL variable and thesis

Agent sub-F · 2026-09-13 · branch `codex/lane2-full` · new package `rnpl_v2` · approximately 35 minutes estimated active work (not separately timed); preregistration 15:19 UTC to completion 17:12 UTC: 1 hour 53 minutes elapsed

## Verdict

**PARTIAL.** The frozen stock reconstruction reproduces K1's CSVs, but the three excess-unpaid observations are **+1.969114 / +8.047784 / +9.705899pp**, which round to **+2.0 / +8.0 / +9.7**, not the pre-registered +8.1 middle value. The original joint identification of u and m is rejected on the later accounting correction already present in Theo's note. The corrected fee-only u is a conditional sensitivity, and m remains unidentified. All three nights paths run; twelve LIVE registry rows were written; historical alarm rates and one D-10 option are specified. D-06's practical direction is supported, but a categorical line-specific claim that all unearned fees use historical exchange rates is not explicitly disclosed. These limits are retained rather than calling the brief a pass. Historical forecast effectiveness is **underpowered/unmeasured: W1 n=0, W2 n=0**.

## Pre-registered pass line

Written 2026-09-13 at approximately 11:19 EDT before execution:

The excess-unpaid series reproduces (+2.0 / +8.1 / +9.7pp); the λ chart's historical false-alarm rate is published with n; the model runs under all
three nights inputs with 3Q26 / 4Q26 revenue for each; D-06 has a documented, quoted answer; D-10 has one proposed refutation condition. Any
item missing → partial, with the missing item named.

Implementation choices fixed before execution: reuse K0 v2 lambda forecasts and control chart; reproduce K1 fee-stock allocation from its frozen ex-COVID pooled coefficients, without refitting; use 2022Q1–2025Q2 seasonal norms; label all stock estimates retrospective. Reproduce the original joint equations as a rejected diagnostic and report the corrected fee-only `u = 1 - UF_ratio/B`, with B = 1.00/1.05/1.10. Migration share is unidentifiable from these balances. The three nights paths are 9.9/8.9, 9.3/7.6, and 9.9/8.1 percent; hold ADR fixed across paths. The two-lag kernel has no contemporaneous GBV coefficient, so Q3 revenue is invariant to these nights paths and Q4 only sees Q3's path. D1 leakage is a separately disclosed conditional stress, not an estimated incremental loss; do not compound it into a nights path that already contains the same cancellation tail. Register LIVE rows only, with exact scenario notes and no historical D1 backdating. Parent runs both scorers.

## What ran

Commands from the repository root, using its `.venv` interpreter:

```text
./.venv/Scripts/python.exe -X utf8 -m pytest analysis/src/forecast_methods/rnpl_v2/tests -q
./.venv/Scripts/python.exe -X utf8 analysis/src/forecast_methods/rnpl_v2/run.py --as-of 2026-09-13 --register
./.venv/Scripts/python.exe -X utf8 -m pytest analysis/src/forecast_methods/rnpl_v2/tests -q
./.venv/Scripts/python.exe -X utf8 analysis/src/forecast_methods/rnpl_v2/run.py --as-of 2026-09-13
```

The initial package test returned exit 1, 11 passed/1 failed in 2.94 seconds; retained in `data/processed/forecast_methods/rnpl_v2/first_test_failure.txt`. It exposed the source headline rounding error after the stock reconstruction had already matched frozen K1. The implementation test was corrected once to compare frozen full-precision CSVs and explicitly assert the 8.0 rounded value; the acceptance rule remains unchanged and failed. Final package test: exit 0, **12 passed** in 2.31 seconds wall time. Initial registration run: exit 0 in 8.98 seconds, twelve rows. After adding primary-filing sentence verification, the final rebuild without registration returned exit 0 in 5.21 seconds; six exact sentences verified. The PNG was inspected and is legible. Both scorers and frozen tests are owned by the parent at CLOSE; this agent did not run them.

Reads beyond the initial list were limited to dependencies explicitly named by K1 and necessary to implement its stock reconstruction/filing check: its frozen coefficient and B1/B3 outputs, `kernel_phi_v2/stage_b.py`, the referenced balance-sheet verification note, and the two local public filing extracts. No network, Airbnb site, credential, licensed-store or existing-model action occurred. Code uses K0 v2 for every forecast lambda and control chart; it does not re-estimate lambda.

## Results

All dollar values are USD millions. No consensus is consumed. CSVs and `input_manifest.csv` reside in `data/processed/forecast_methods/rnpl_v2/`; hashes cover the KPI panel, frozen fit, D1 grid, K0, this script and the local public filing extracts.

### Paid backlog and stock allocation

Paid backlog is reported unearned fees plus funds payable. Coverage is that stock divided by next-quarter revenue; it is not a revenue share. The last observation uses the 6 August Q3 guide midpoint of $4,730M, explicitly labelled. The fee-stock allocation uses K1's frozen 8-parameter ex-COVID pooled fit, not the forecasting two-lag weights. No `reported/(1-d)` restated-fee feature is constructed. Norms are retrospective, 2022Q1–2025Q2.

| Quarter-end norm; next revenue quarter | n | UF coverage | FP coverage | Paid backlog coverage | Paid / unpaid / unbooked share of next revenue, % |
|---|---:|---:|---:|---:|---|
| Q1-end → Q2 | 4 | 0.8676 | 3.0421 | 3.9097 | 36.51 / 21.40 / 42.10 |
| Q2-end → Q3 | 4 | 0.6944 | 2.6885 | 3.3830 | 41.49 / 23.50 / 35.01 |
| Q3-end → Q4 | 3 | 0.6570 | 2.6252 | 3.2823 | 34.99 / 32.41 / 32.60 |
| Q4-end → Q1 | 3 | 0.6759 | 2.6605 | 3.3363 | 30.31 / 27.38 / 42.31 |

The paid/unpaid/unbooked levels depend on the fitted allocation and remain unidentified as literal reservation shares. They are explanatory model outputs, not direct public outcomes. The stock-only excess formula is `100 × [(1 − UF / frozen_fee_stock) − same-season_pre_RNPL_norm]`, which does not use the Q3 revenue guide.

| Stock quarter | n recent / n norm | Excess unpaid, pp | Rounded to 0.1pp | Literal acceptance |
|---|---:|---:|---:|---|
| 2025Q4 | 1 / 3 | 1.969114 | 2.0 | Reproduces |
| 2026Q1 | 1 / 4 | 8.047784 | 8.0 | **Fails +8.1** |
| 2026Q2 | 1 / 4 | 9.705899 | 9.7 | Reproduces |

All frozen K1 fee-stock values reproduced within rtol 1e-11, and the excess matches K1 B3 full precision within 1e-10pp. The difference is in the prose headline, not a new model result. This note is a dated correction; K1 remains untouched.

### u sensitivity and the rejected joint solve

The legacy equations assume `UF_ratio = (1-u)(1-m)B` and `FP_ratio = (1-u)(1+k*m)B`. They move fees into funds payable when hosts migrate, contrary to Note 2. `solve_sensitivity.csv` retains their output in columns explicitly prefixed `rejected_`; `current_m_pct` is null. Even the pre-migration 2025Q3 diagnostic returns a negative m, and changing B cannot move m because B cancels in the ratio. These numbers are not current estimates and do not enter forecasts.

The available conditional alternative is `u = 1 − UF_ratio/B`. It assumes stable fee/payment mix and a chosen book-length scale; B, RNPL's unpaid stock share and changes in Pay Less Upfront cannot be separately identified. Current norms are 2022Q1–2025Q2 and Q2 uses the actual guide midpoint, making these sensitivities different from the legacy note's shorter norms and $4,800M hypothetical revenue.

| Quarter | n norm / n B scenarios | B=1.00 u | B=1.05 u | B=1.10 u | Current m |
|---|---:|---:|---:|---:|---|
| 2025Q4 | 3 / 3 | 3.70% | 8.29% | 12.46% | Unidentified |
| 2026Q1 | 4 / 3 | 12.69% | 16.85% | 20.63% | Unidentified |
| 2026Q2 | 4 / 3 | 13.81% | 17.92% | 21.65% | Unidentified |

Thus the H1 conditional u range is **12.69–21.65%**, not the withdrawn joint-solve range. These are stock sensitivities, not the disclosed quarterly RNPL flow share, and not an estimated cancellation hazard.

### D-06: what the filings establish

Six exact filing sentences are independently byte-normalized and verified by `filing_evidence.json`. Local public primary sources: `data/raw/regulatory/quantification/abnb_2025_10k.json` (page labels below) and `abnb_2026q2_10q.html`, Item 2 MD&A.

FY2025 10-K, Note 2, p.61:

> “Monetary assets and liabilities are remeasured at the exchange rate on the balance sheet date and nonmonetary assets and liabilities are measured at historical exchange rates.”

Its p.60 separately says foreign subsidiaries with non-USD functional currencies translate assets and liabilities at the balance-sheet date. Thus translation and non-functional-currency remeasurement must not be conflated. Funds payable is a cash obligation and is exposed to closing-rate monetary remeasurement. Treating service-linked unearned fees as nonmonetary is an accounting inference consistent with the observed small residual; the filing does **not** explicitly name unearned fees as a line receiving historical-rate treatment, and refundable fees complicate a categorical claim. “FX-clean” is an empirical shorthand here, not a universal accounting guarantee.

FY2025 10-K, Note 2, p.63:

> “Host and guest fees are recorded as cash with a corresponding amount in unearned fees.”

The preceding sentence records guest payments **net of service fees** in funds payable (full sentence preserved in the evidence file). Therefore the fee migration does not reclassify guest-fee dollars out of UF into FP. A change in total fee rate can still change the amount of UF; “migration-neutral” is about the routing, not the fee economics. Note 2 pp.63–64 also records the full fee at the first Pay Less Upfront installment, so shifts between that program and RNPL can change the UF/FP ratio without identifying m.

2Q26 10-Q, Item 2, operating-cash-flow discussion:

> “Accordingly, unearned fees are not recorded, and operating cash flows are not generated until payment is received.”

The same MD&A attributes the timing change to flexible-payment adoption and says RNPL has experienced higher cancellations. It also states:

> “As adoption of RNPL and our other flexible payment options continues to grow, the timing among GBV, revenue, and cash receipts may become less correlated.”

The earlier verification note's reported balance-minus-cash-flow reconciliations are consistent with the practical direction: FY2025 FP residual +$627M versus UF +$5M; H1 2026 FP −$161M versus UF +$3M (each n=1 period; these residual amounts are inherited, not independently re-extracted here). Such residuals can include noncash/reclassification effects; they must not automatically be called exact FX without reconciliation. **D-06 proposal: use UF as the cleaner payment-timing diagnostic; retain FP as a monetary balance requiring a translation/noncash reconciliation.** Do not retain the original opposite attribution or declare a measured m. The exact blanket UF historical-rate assertion remains unverified, so the literal D-06 request is partial.

### Kernel, nights and leakage

K0's four seasonal coefficients and fixed 2/3 lag weight are imported. The fixed Q3 ADR of **$180.144527** reconciles the K0-implied Q3 GBV to the team nights path; it is a conditional anchor, not a new ADR estimate. The three nights paths are 9.9/8.9, 9.3/7.6 and 9.9/8.1 percent. Their Q3 GBV values are $26,449.972 / $26,305.568 / $26,449.972M.

D1 central cell: `share_central`, `adr_plus25`, `delta_4pp`, `lead_2.2`, `uplift_7`, rebooking offset 0.25; n=1 selected scenario. Inverting the exact nights-share identity gives Q3/Q4 GBV flow shares 22%/23%; the requested simple stress is L=share×4pp=**0.88%/0.92%**. The full D1 grid has 2,025 cells and produces 4,050 quarter rows. Its maximum gross leakage is 1.4998% Q3 / 1.6198% Q4; zero-propensity cells give zero. This equation intentionally does not reuse D1's already lagged reported-nights-growth effect or its rebooking offset. Flow share is not live backlog share, and this gross stress is not a measured incremental revenue loss.

| Path | n quarters | Q3 pure kernel | Q3 registered stress | Q4 pure kernel | Q4 full D1 stress | Q4 registered |
|---|---:|---:|---:|---:|---:|---:|
| Team | 2 | 4,808.363 | 4,766.049 | 3,214.776 | 3,185.196 | 3,185.196 |
| Theo re-base | 2 | 4,808.363 | 4,766.049 | 3,203.185 | 3,173.711 | **3,203.185** |
| Ex-NA lap midpoint | 2 | 4,808.363 | 4,766.049 | 3,214.776 | 3,185.196 | 3,185.196 |

Q3 revenue is unchanged by Q3 nights under the two-lag kernel. Q4 uses Q3 GBV, so it sees Theo's Q3 reduction but not the separate Q4 nights changes. Q4 nights first enter Q1 2027, which this package does not forecast. The ex-NA path consequently ties the team Q4 revenue even though its Q4 nights are lower; forcing a difference would break the model's lag structure.

**Overlap guard:** Theo's Q3 nights input already contains a cancellation-tail adjustment. The Q4 registered Theo row therefore applies no additional D1 leakage. Its full-stress value is retained only for sensitivity, not promoted. Q3 applies the same leakage in all variants because contemporaneous nights are absent from that revenue equation. This makes the registered rows explicitly different conditional constructions: Theo's registered Q4 value being above the other stress paths is not evidence of a bullish model signal. Even the other stress rows may overlap cancellation risk already embedded in historical lambda or net booked GBV. No empirical incremental-loss claim is made.

Twelve rows were registered through FORMAT 1.1 under `rnpl-v2__revenue_next_q`, `spec_id=team/theo/exna`, two target quarters and two replay labels. All are LIVE at 2026-09-13; PIT/full_sample use identical current information. No historical D1 parameters are backdated. The model has four inherited fitted seasonal coefficients; scenario paths, fixed weight, rates and overlap rule are assumptions rather than fitted degrees of freedom. The stock diagnostic separately inherits eight K1 fitted parameters and four seasonal mean norms. The grid is not an empirical distribution; no q10/q90 pseudo-confidence interval is registered.

### Lambda chart and empirical alarm rates

The PNG and CSVs use K0 v2's public control-chart API. Current seasonal bands are descriptive mean±2sd; each historical alarm compares to prior same-season observations with at least two training cells. They are distinct from the fixed November card thresholds.

| Rule / population | W1 n / alarms | W2 n / alarms | Interpretation |
|---|---:|---:|---|
| Chronological mean±2sd, pre-RNPL targets through Q2 2025 | 2 / 1 (50.0%) | 2 / 1 (50.0%) | Empirical false alarms relative to an RNPL interpretation; severely underpowered |
| Same chart through Q2 2026 | 6 / 1 (16.7%) | 6 / 1 (16.7%) | Alarms, not all known false; overlapping windows |
| Fixed warning <17.09%, historical Q3 2023–25; W2 subset 2024–25 | 3 / 0 | 2 / 0 | Retrospective same three cells helped set threshold; no calibrated false-alarm probability |
| Fixed escalation <16.93%, same Q3 samples | 3 / 0 | 2 / 0 | Same limitation |

The prospective fixed Q3 denominator is $27,866.666667M. As established by D's addendum, 17.09% corresponds to **$4,762.413333M** and 16.93% to **$4,717.826667M**. Those exact thresholds control; legacy rounded dollar labels do not. Integer revenue is interval-scored ±$0.5M; intervals straddling a threshold are ambiguous. A lambda alarm cannot identify cancellations separately from in-quarter bookings, pricing, FX or fee changes.

### Thesis F and proposed extension to D's card rows

**Proposed memo sentence:** “Our frozen-model estimate of excess unpaid share rose from 2.0pp in Q4 2025 to 9.7pp in Q2 2026, and an assumed 4pp incremental RNPL cancellation stress yields $3,185M of Q4 2026 revenue under the team nights path; these conditional estimates do not identify an RNPL causal effect.”

The observable setup is a widening difference between booking dollars and paid balances, followed by delayed payment and uncertain survival at check-in. In Q3 2025, GBV grew 13.93%, paid backlog 9.71%, and nights 8.80% (n=1 quarter each). **Only GBV ran about four points ahead of the paid backlog; nights did not.** By Q2 2026 the corresponding growth rates are 15.74%, 8.12% and 10.34% (n=1 each). This corrects the brief's combined “GBV/nights” wording. The brief's 13.3x→18.2x multiple comparison is an inherited setup assertion, not re-estimated or used as evidence in this package. The proposed earnings mechanism remains conditional: extra unpaid booking stock can create a conversion problem as its payment deadlines arrive, while rollout anniversaries reduce reported growth without proving weaker underlying demand.

These extend `D_CARD_ADDENDUM_LAMBDA.md`; the signed card remains untouched.

| Proposed row | n available | Value / future tell | Scoring and limits |
|---|---:|---|---|
| F1 conversion | 3 Q3 observations | Fixed 17.09 / 16.93% thresholds | Retain D's denominator and interval rules; no RNPL causal label |
| F2 stock timing | 3 recent observations | Excess +1.969 / +8.048 / +9.706pp; Q2-end paid/unpaid/unbooked norm 41.49/23.50/35.01 | Descriptive reconstruction using frozen coefficients; not directly observable in the release |
| F3 cash timing | 1 future Q3 print | Record UF growth minus GBV growth and reported FP growth | Retain FP +5–11% only as a neutral descriptive band, **not “deferral on schedule”**; require reconciliation before interpretation |
| F4 management evidence / refutation | 1 future guide event | Record cancellation language; whether the three-feature bundle contribution is re-quantified; exact Q4 nights wording | Preserve bundle scope; silence is not measured zero; apply only the single D-10 proposal below |

**One D-10 option, not adopted:** refute the proposed material near-term RNPL revenue-drag thesis only if **all three** hold at the November print: (1) the Q3 lambda interval is wholly at least 17.09%; (2) the interval for Q3 UF year-on-year growth minus Q3 GBV year-on-year growth is wholly **above −8pp**; and (3) management explicitly guides Q4 nights as **“low double digit” or stronger**. Otherwise record inconclusive for this combined refutation rule, rather than inventing a second funds-payable rule. Missing inputs are absent, not support. For the growth-gap interval, use UF and GBV reported rounding intervals independently, retain their units, and compute ratio extrema; no integer-word mapping is substituted for management's quoted phrase. This is a prespecified decision proposal, not a statistical RNPL identification test or an adopted trade instruction.

## What failed or could not be done

The literal +8.1pp middle value failed while frozen full-precision arithmetic passed. The proposed two-equation migration identification fails the filing routing and is not repaired by fitting it more precisely. Exact line-specific UF historical-rate treatment was not found; generic remeasurement and subsidiary translation policies are quoted without overstating them. Historical scenario forecasts were not registered because D1 inputs did not exist at those guide dates (W1 n=0, W2 n=0); no claim to beat a baseline or forecast Street expectations follows. The simple leakage stress lacks measured remaining survival, incremental hazard and embedded-risk adjustment. The Q4 nights paths cannot affect Q4 revenue under the inherited two-lag model. A calibrated Q3 false-alarm probability is unavailable at n=3. All are limitations of the economic evidence or requested model, not hidden execution failures.

## Interpretation

This package makes the RNPL assumption visible and falsifiable while preserving what it cannot identify. Paid-stock timing is observable in aggregate; m and the RNPL cancellation coefficient are not. The cash-line correction favors UF as the cleaner timing check, subject to the actual currency and payment-program mix. A mechanical scenario run is useful for sizing but does not show that the same loss is incremental to the existing forecast. The next decision-useful inputs are an unbilled confirmed-RNPL stock and remaining survival by booking/payment cohort; no outreach was sent. No team decision, target, fee step, trade direction or workbook value was adopted.

Harness limitation: the frozen scorer groups objects without `spec_id`. It does not currently score these LIVE rows, but a future score must retain individual nights variants rather than treating the pooled object as one forecast. Parent owns both scorer runs and any close receipt.

## RESUME

The new package, evidence file, 12 tests, LIVE registry and full outputs are ready for parent review; parent should run both scorers, record their receipts and update the workboard with PARTIAL and the +8.1→+8.0 source-rounding correction. Preserve the rejected joint diagnostic and do not promote it into a current m estimate. At the next print copy these outputs into a new version, use the frozen stock coefficients, quote exact management wording, apply rounding intervals, and reconcile any monetary translation/noncash movement before interpreting FP. Team review is needed to adopt a D-10 condition or a path; no such choice was made here.
