# REFUTE F — mechanism lens

Agent `refute_f_mechanism` · 2026-09-13 · branch `codex/lane2-full`

## Verdict

**SURVIVED.** The exact sentence survives as a retrospective frozen-model diagnostic followed by an explicitly assumed gross stress. It does not establish RNPL causation or incremental expected revenue loss. Single-fee migration cannot move fees from unearned fees into funds payable solely by changing the payer: both host and guest service fees enter unearned fees. Changes in total fee yield or payment timing remain plausible confounds. A 15.20% relative decline in effective fee yield versus the same-season norm would mechanically reproduce the Q2 2026 diagnostic without extra unpaid bookings, but no such decline is measured here. The conditional revenue arithmetic reproduces to **$3,185.195735M**, a **$29.580016M** gross haircut to **$3,214.775751M**. Historical forecast or causal validation remains **underpowered/unmeasured: W1 n=0, W2 n=0**.

Exact sentence under review: “Our frozen-model estimate of excess unpaid share rose from 2.0pp in Q4 2025 to 9.7pp in Q2 2026, and an assumed 4pp incremental RNPL cancellation stress yields $3,185M of Q4 2026 revenue under the team nights path; these conditional estimates do not identify an RNPL causal effect.”

## Pre-registered pass line

Written 2026-09-13 17:39:04 UTC, before executing the independent audit. REFUTER.md states: “Not applicable — the refuter's output is the verdict. A refuter that only praises has failed. ‘Partial’ does not count as survived.”

I will attempt to refute the exact limited sentence through (1) fee routing under single-fee migration; (2) total fee-rate/mix changes that reproduce the unpaid diagnostic without RNPL; (3) payment-program and FX alternatives; (4) frozen-stock reconstruction and share interpretation; (5) gross flow-share cancellation stress versus incremental recognized-revenue loss; (6) duplicated risk and the timing of the team nights path. Reproduce reported endpoints to 0.05pp and scenario revenue to $0.5M, without importing the RNPL implementation. A demonstrated alternative mechanism refutes causal attribution, which the exact sentence explicitly disclaims; it refutes the sentence itself only if its numerical or conditional wording is false. No forecast registration or scorer run will occur.

## What ran

Command from the repository root:

```text
./.venv/Scripts/python.exe -X utf8 analysis/src/forecast_methods/refute_f_mechanism_v1/run.py
```

Exit **0**, shell wall time **1.72 seconds**, measured audit calculation **0.21 seconds**. The first and only execution passed. Pandas emitted a performance warning when adding a column to its fragmented CSV read; it did not affect calculations or produce a test failure. No coefficient was refitted. The independent stock reconstruction loops over each booking vintage's remaining recognition tail; it does not import `rnpl_v2`. The scenario uses K0's unchanged public `pit_lambda` API, the raw KPI nights/GBV, the disclosed fixed ADR, and the original D1 grid. The registry is read-only and both LIVE replay rows reconcile. No registry mutation, scorer, external fetch or Airbnb-site access occurred.

Outputs and hashes: `data/processed/forecast_methods/refute_f_mechanism_v1/`. The source and command README are under `analysis/src/forecast_methods/refute_f_mechanism_v1/`. I independently read FY2025 10-K Note 2 pages 60–64 and the Q2 2026 10-Q MD&A from the local public filing extracts named in the package manifest. Required brief/workboard/REFUTER/convention reads preceded the audit. The parent owns the shared workboard update.

## Results

All dollar figures are USD millions. No vendor consensus is consumed. The stock is retrospective, using eight inherited K1 fit parameters and four seasonal means; it is not a PIT validation. K0 supplies the LIVE Q4 coefficient of **12.0403669385%** from **n=5** seasonal observations; it is not estimated in this audit. All scenario sensitivities below have **n=1 assumed case**, not one observed effect. W2 is nested in W1, not independent evidence.

### Independent reconstruction and fee-only counterfactual

Let `F` be the frozen forecast fee stock, `UF` reported unearned fees, and `p_norm = mean(UF/F)` in the same season over 2022Q1–2025Q2. The diagnostic is `100 × (p_norm − UF/F)`. If paid booking exposure is unchanged and only effective fee yield changes, the factor `t = (UF/F)/p_norm` exactly reproduces the diagnostic. This is a counterexample to identification, not a claim that the fee change occurred. The reported fee stock is not a directly observed outstanding-reservation denominator.

| Stock quarter | n observation / seasonal norm | Frozen F | UF | Normalized paid fraction, norm → current | Excess unpaid, pp | Fee yield decline that alone reproduces excess | UF shortfall to norm |
|---|---:|---:|---:|---|---:|---:|---:|
| 2025Q4 | 1 / 3 | 3,447.742 | 1,743.000 | 52.524% → 50.555% | 1.969114 | 3.748983% | 67.890 |
| 2026Q1 | 1 / 4 | 4,970.266 | 2,733.000 | 63.035% → 54.987% | 8.047784 | 12.767213% | 399.996 |
| 2026Q2 | 1 / 4 | 5,229.521 | 2,831.000 | 63.841% → 54.135% | 9.705899 | 15.203268% | 507.572 |

Maximum difference from the package's three full-precision diagnostics is **1.07e-14pp**. The two quoted endpoints round correctly. The omitted middle observation rounds to **8.0pp**, which the package already corrects. These counterfactual fee declines are percentages of fee yield, not percentage points of guest fee, host fee, or GBV take rate.

### Explicit refutation attempts

| # | Claim → attack | Evidence and n | Result for the attacked proposition |
|---|---|---|---|
| 1 | Excess unpaid reflects payment deferral → single-fee migration merely moves guest-fee dollars from UF into FP. | FY2025 10-K Note 2 p.63 explicitly records host and guest fees in UF and guest payments net of service fees in FP; n=1 primary accounting policy. Holding total fees and payment time constant, a payer switch gives ΔUF=0. | **SURVIVED** the rerouting attack. The earlier two-equation migration mechanism is refuted, but F already rejects it. |
| 2 | The residual is an RNPL-specific unpaid share → lower total fee yield or booking composition generates the same residual. | The algebraic fee-only counterexample above exactly explains all three observations with no extra unpaid share; n=3 sensitivities, seasonal norms n=3/4/4. No measured migration rate or cohort fee yield resolves this alternative. | **PARTIALLY**: fee economics can mimic the signal; causation is not identified. The exact sentence survives because it calls the number a frozen-model estimate and explicitly disclaims causation. |
| 3 | UF is an FX-clean RNPL variable → payment-program substitution or translation changes UF independently of RNPL cancellation risk. | 10-K pp.63–64 records the full service fee on the first Pay Less Upfront installment, even while remaining host funds are unpaid. The Q2 10-Q attributes timing changes to flexible payment options collectively. 10-K pp.60–61 separates subsidiary translation from monetary/nonmonetary remeasurement; n=2 filings. Neither states that every UF balance always uses historical FX. | **PARTIALLY**: UF is a payment-timing diagnostic with program/mix/currency exposure. It does not isolate RNPL or cancellation hazard. F's qualified D-06 wording, and thus the exact limited sentence, survive. |
| 4 | The 2.0→9.7pp rise is numerical evidence → restated fees, the Q3 guide denominator, or literal unpaid-reservation counts are necessary to reproduce it. | Independent raw-KPI/frozen-coefficient reconstruction matches n=3 values within 1.07e-14pp. It consumes actual UF, never a restated fee series, and no next-quarter revenue or guide denominator. Its denominator remains a fitted fee stock. | **SURVIVED** arithmetic and circularity attacks. Reading it as observed reservation share is **REFUTED**; the sentence does not make that stronger claim. |
| 5 | Assumed 4pp cancellation stress means $3,185M → incorrect share conversion or revenue multiplication changes the quoted number. | D1 central Q4 nights share, inverted with RNPL/non-RNPL ADR ratio 1.25, gives GBV share 23.003172%; multiplying by 4pp gives L=0.920126881%. n=1 scenario, n=2 identical team registry replays. $3,214.775751 × (1−L) = $3,185.195735. | **SURVIVED** numerical attack. Using exact 23% instead changes revenue by $0.004079M, immaterial to the claim's rounding. |
| 6 | This gross stress is incremental recognized-revenue loss → booked flow share differs from the surviving revenue cohort, rebooking offsets losses, and historical λ/net GBV already contain cancellation risk. | Q2 10-Q discloses higher RNPL cancellations but no numeric hazard or remaining survival curve; n=1 filing. The D1 selected cell carries a 25% rebooking offset that the simple gross stress intentionally does not use; n=1 assumed cell. Applying that offset alone yields $3,192.591M. Full embedding gives $3,214.776M. | **REFUTED** as an empirically measured incremental-loss mechanism. **SURVIVED** for the exact explicitly assumed stress. The $29.580M is a gross scenario haircut, not an identified RNPL cost. |
| 7 | The team Q4 nights path drives the Q4 stress → the two-lag kernel only sees Q3 nights through Q3 GBV. | Team and ex-NA scenarios have identical Q3 nights and different Q4 nights, yet identical Q4 revenue; n=2 paths. Theo differs in Q3 nights, and its Q4 registered row withholds added leakage. | **PARTIALLY**: “under the team nights path” is true, but only its Q3 component enters Q4. It does not demonstrate the Q4 nights slowdown causing Q4 revenue weakness. The exact conditional sentence survives. |

The strongest successful attack is #6 against promotion into expected incremental loss; #2 establishes that the stock residual cannot uniquely identify RNPL. Neither invalidates the exact sentence's numerical and explicitly conditional content. Three of seven attacks expose important limits; they are not described as empirical confirmation.

### Conditional revenue sensitivity

| Assumption | n assumed cases | Q4 2026 revenue |
|---|---:|---:|
| Published gross 4pp stress, Q4 D1 flow share | 1 | 3,185.196 |
| Same stress with 25% rebooking elsewhere on Airbnb | 1 | 3,192.591 |
| Half of the gross loss already embedded in baseline | 1 | 3,199.986 |
| All of the gross loss already embedded in baseline | 1 | 3,214.776 |

These are mutually alternative sensitivities, not confidence bounds or calibrated probabilities. Selecting the quarter's booked-flow share as the recognized-revenue exposure is another unmeasured assumption. The existing filing's qualitative cancellation language cannot estimate it. No W1/W2 performance claim can be made with zero historical scenario registrations.

## What failed or could not be done

No computational check failed. The allowed inputs contain no reservation-level pre/post-migration fee yield, RNPL versus other-program payment cohort, or surviving booking cohort matched to Q4 revenue. The audit therefore cannot measure how much of the +9.7pp belongs to RNPL, fee economics, lead-time changes, FX, or changing program mix. The fee-only alternative's 15.20% decline is a required counterfactual magnitude, not evidence that single-fee migration caused it. A D-06 claim stronger than the package's accounting-qualified wording is unsupported. No test calibration or forecast accuracy is inferred from the conditional grid.

## Interpretation

The exact sentence is acceptable only with its words “frozen-model,” “assumed,” “conditional,” and “do not identify” retained. No corrected endpoint or rounded revenue number is required. For maximum clarity, the revenue clause could say “a gross stress assuming a 4pp incremental cancellation differential and a 23% affected GBV flow share gives $3,185M, versus $3,215M before that stress.” This distinguishes a useful sizing exercise from a forecast of the causal RNPL loss without changing the numbers. It is not a new adopted headline or team decision.

## RESUME

Parent should record **F mechanism SURVIVED** for the exact narrow sentence, link this note, and preserve the qualifications when collecting the three refuter votes. Do not promote the fee-only counterfactual into measured migration or interpret the $29.580M gross haircut as demonstrated incremental RNPL loss. The next discriminating evidence would match outstanding booking value, total expected fees, payment status, payment program, cancellation and rebooking outcomes by stay quarter. Until that exists, retain UF as a qualified diagnostic and the revenue effect as an assumed scenario. No model, registration, scorer or team-decision change is requested.
