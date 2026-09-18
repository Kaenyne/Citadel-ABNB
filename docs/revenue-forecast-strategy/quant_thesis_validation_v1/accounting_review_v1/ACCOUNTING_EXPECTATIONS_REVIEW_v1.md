# Q5/Q6 — Independent accounting and expectations review

2026-09-14 · `/root/uncertainty_auditor` reviewing parent `/root` · `codex/quant-thesis-validation-v1` · new `accounting_review_v1` files only · final adjudicator: parent.

**Verdict: reviewed bridge PASS as deterministic historical-snapshot arithmetic, with its timestamp finding closed in v2. No actionable management-guide surprise, causal RNPL revenue magnitude or after-hedge FX adjustment is established.** The parent's corrected bridge compares revenue with revenue and labels inferred guide expectations as hypothetical. It leaves unidentified flow and hedge quantities unavailable. This preserves the strongest supported result without turning successful arithmetic into investment evidence.

## Independent scope and receipt

Reviewed parent's `CHAIN_PROTOCOL_v1.md`, `expectations_bridge_v2.py` and five `expectations_v2` files. Consumed exact L4 extracts in `evidence_v3/l4`, including final revenue reconciliation, financial review, final review memo and decision register; read L3's immutable cohort accounting note, scenario metadata, conversion acceptance and fee snapshot. No moving worktree head was consumed. Four critical L4 CSVs were independently matched byte-for-byte to their Git object contents at `29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70` using `git show`.

The independent implementation uses `revenue = intercept + slope*G1`, where `slope=2*lambda/3` and `intercept=lambda*G2/3`, then inverts that line. For stress cells it uses the exact multiplicative ratio to the baseline. It imports no parent calculation functions and checks all three panels, every cushion row and all 35 stress cells.

Exact executed command from the assigned worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 'analysis/src/forecast_methods/quant_thesis_validation_v1/accounting_review_v1/run_v2.py' --out 'data/processed/forecast_methods/quant_thesis_validation_v1/accounting_review_v1/results_v1'
```

Exit 0; shell wall time 0.93 seconds. **335 numeric checks pass**; maximum absolute difference is `8.763024e-12`, below `1e-6` in the underlying USDm/percent/factor units. These checks validate arithmetic, not 335 historical forecast observations. Empirical validation n remains zero for each deterministic snapshot comparison. All **433 shared numeric fields** between parent's v1 and v2 are exactly unchanged. Metadata change alone corrected S&P/Zacks timestamps to date-only with explicit unavailable time; Yahoo remains minute display with raw capture `15:20:58Z` noted.

The independent receipt binds all consumed parent files and four L4 CSVs. Reviewed parent code SHA-256: `0335d93ec0617e4ad8274ff7cfaf5e90424ca501af3bb2754e08c9a4101f52c6`; parent v2 receipt: `e3b82e92e204e7e7417465a4cf713221c90cff0379f31453d6daedcb88fd48ff`. The receipt is in `data/processed/forecast_methods/quant_thesis_validation_v1/accounting_review_v1/results_v1/independent_receipt.json`. Review conclusions apply to those exact versions. Initial unexecuted review `run.py` is preserved; `run_v2.py` is canonical.

## Basis and crossings reproduced

The L4 Q4 2026 `review_with_k` reference uses forecast Q3 GBV **26,008.556 USDm**, printed Q2 GBV **27,200 USDm**, retained operational lambda **12.040366938%** and trailing-eight median cushion **1.790491031%**, observed through 6 August. This yields revenue **3,179.343654 USDm** and modeled guide **3,123.419115 USDm**. It is one conditional operating case, not an adopted forecast; no fresh market assertion is made.

| Frozen revenue panel | Observation precision | Revenue consensus, USDm | Own revenue gap, USDm / percent | Common-cushion hypothetical guide gap, USDm | G1 equal-revenue boundary, USDm |
|---|---|---:|---:|---:|---:|
| Yahoo Finance, LSEG family | 13 Sep 2026, 15:20 UTC; raw capture 15:20:58 | 3,161.021490 | +18.322164 / +0.579628% | +17.999878 | 25,780.296790 |
| S&P Global via StockAnalysis | 10 Sep 2026; exact time unavailable | 3,160.000000 | +19.343654 / +0.612141% | +19.003400 | 25,767.570974 |
| Zacks | 11 Sep 2026; exact time unavailable | 3,200.000000 | −20.656346 / −0.645511% | −20.293001 | 26,265.894657 |

Each row has n=1 snapshot and empirical forecast-validation n=0. These are three vendor-family anchors with different dates, not three measurements of management-guide expectations. Yahoo and Alpha Vantage count once. S&P and Zacks were not refreshed. The immutable source CSV carries the source URLs, register IDs, analyst counts and capture/observation descriptions.

For the LSEG-family anchor, holding all other inputs fixed, equal revenue requires Q3 GBV **0.877631% below** the reference, lambda **11.970979793%** (a **0.069387pp** decline), or a multiplicative revenue change of **−0.576288%**. These are deterministic break-even values; no likelihood is assigned. For equal *hypothetical* guides with Street cushion fixed to the median, the own cushion must rise to **2.380497175%**, **0.590006pp above** the reference. Explicit guide expectations remain unavailable.

The retained raw subtraction `own guide − revenue consensus` is **−37.602375 USDm** for LSEG. It compares different objects. Under the same hypothetical cushion, the corresponding guide comparison is **+17.999878 USDm**. The corrected bridge therefore prevents the mixed-object negative from becoming evidence of a bearish guide surprise. The sign also differs across correctly matched revenue panels; none is a forced consensus average.

## Management policy changes the message, not actual income

| Own-cushion assumption, n=1 each | Q4 modeled guide, USDm | Direct change in modeled actual revenue / earnings / cash |
|---|---:|---|
| Trailing-eight median, 1.790491031% | 3,123.419115 | Zero from the cushion assumption alone |
| Trailing-eight mean, 1.856743063% | 3,121.387508 | Zero |
| Inherited Q4 cushion, 3.88% | 3,060.592659 | Zero |

The median-to-legacy guide change is **−62.826456 USDm** while modeled revenue stays **3,179.343654 USDm**. A guide is a policy-dependent statement about expected operating outcomes; an identity created by choosing c is not proof that management uses that exact rule. The difference is not an incremental operating loss, FCF shortfall or value reduction. Any market-reaction claim needs dated expectations, an actual preannouncement information set and an independently supported revision/return mechanism.

Post-guide revenue estimates from `issued guide*(1+cushion)` answer a different question from forecasting an unissued guide. Historical midpoint-beat counts do not identify the current c or make a guide surprise executable. The accepted L3 letter-close test uses the just-printed GBV in the same release that contains management's target guide, so it cannot alone certify advance knowledge. L2 A2 remains PARTIAL and B2's revision hurdle remains FAIL.

## Primary accounting checks

Independently opened the SEC filings on 14 September 2026. No Airbnb page, credentialed database or scraping route was used.

**Filing facts Q:** Q2/H1 2026 GBV is 27,247/56,434 USDm. Full booking GBV is recorded regardless of payment; cancellation adjustments follow their processing period. RNPL has higher cancellations than historical paid bookings. Revenue starts at check-in. RNPL delays fee cash collection and can alter FCF timing. Customer funds do not affect FCF apart from interest. Q2/H1 revenue includes hedge losses reclassified from AOCI of 19/34 USDm. The next-12-month expected reclassification disclosure supplies no Q4 allocation. [Q2 2026 10-Q, Key Business Metrics, Note 6 and Cash Flows](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm).

**Filing facts K:** Short stays recognize fee revenue at check-in; long stays recognize the initial month at check-in and later months at monthly anniversaries. Revenue is reported net as agent fees. Host/customer funds are matched by a liability. Foreign subsidiary results use period-average translation, while monetary remeasurement and historical-rate nonmonetary accounting differ. Unbilled confirmed RNPL bookings already create currency exposure; guest and host currency choices can differ. These policies do not provide a transaction-level fixing rule. [2025 10-K, Notes 2 and Item 7A](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm).

The following are analytical implications and missing-data judgments from those facts and L3's accepted accounting contract, not additional observed measurements.

| Link / claim | Classification | Current evidence or exact logic | Missing observation that would resolve it |
|---|---|---|---|
| RNPL remains inside total booked GBV | Supported accounting fact; causal magnitude unidentified | Delayed payment does not delete the booking from the reported KPI; it changes the cash/recognition relationship | Surviving, fee-weighted RNPL booking cohorts with dated subsequent cancellations |
| Unpaid backlog stock equals RNPL recognized-revenue share | Unsupported | Stock at a date, booked flow over a quarter and recognized fee flow have different denominators and durations | Cohort roll-forward connecting stock, new bookings, payment, cancellation, check-in and fee amounts |
| Additional RNPL cancellation deduction | Conditional only after overlap check | Existing net GBV and operating rebases may already contain the cancellation assumption; adding it again can count the same loss twice | Incremental cancellation hazard relative to each baseline, mapped to originating and processing quarters |
| RNPL payment delay forces revenue FX to fix at recognition | Unidentified | Booking, contractual currency/fixing, payment, check-in, translation and host settlement are separate events | Currency-specific contract/fixing convention and actual timing distributions |
| Reported-USD kernel can receive the full gross FX factor again | Rejected construction | Baseline USD GBV already embodies currency translation; its lambda also uses reported revenue | A reconciled constant-reference/pre-hedge component for one replacement |
| L3 timing replacement is a measured revenue effect | Conditional scenario | L3's `T/B` preserves the matching booking baseline and conserves assumed currency/cohort weights; its exposure/RNPL weights are assumptions | Current compatible flow shares, currency mix and timing weights; historical admissible validation remains n=0 |
| Public historical hedge disclosure identifies the future kernel's hedge split | Unidentified | Historical quarter hedge losses and a 12-month outlook do not isolate h embedded in the forecast Q4 lambda | A target-quarter hedge forecast reconciled to the exact reported-revenue baseline |
| Fees or K create a measured uplift | Unidentified magnitude | The with-K/without-K replacement in L4 is an imposed ADR mechanics comparison; L3 snapshot has zero scheduled captures | A valid matched fee-inclusive price/revenue design and pass-through estimate |
| Management-cushion change changes actual earnings/FCF | Rejected for cushion-only scenario | Changing `Q=R/(1+c)` while R/cost inputs stay fixed leaves operating economics unchanged | An independent reason that the new guide changes actual operating expectations, with cost/cash propagation |
| A correctly signed matched-revenue gap is a tradable guide surprise | Unsupported | Observed management-guide consensus is absent and prior executable/revision tests did not establish the chain | Dated explicit guide expectations plus horizon-correct prospective and executable validation |

## FX and RNPL contract adjudication

L3's replacement identity is coherent as a conditional mechanism: compute a common-reference contribution total R0, reconstruct booking-timed reported baseline B, form retimed T using assumed surviving RNPL revenue weights, then replace once using `T/B`. Both sides must use the same cohort/period/currency basis. Applying `T/R0` to the already-translated B is a different, double-counted construction. A multiplicative level factor, change in YoY FX growth contribution and hedge reclassification are distinct objects. The parent adds none of these in its expectations bridge.

An after-hedge replacement would need `R_new=(R_reported−h)*m+h`, with signed h verified for the baseline and target quarter. The public Q2/H1 losses cannot be assigned to future Q4 h, and a 12-month total cannot be divided into quarters without an explicit scenario. Missing h must remain missing. A loss carries negative h; its sign must not be inverted by treating every hedge entry as a benefit.

L3's cohort metadata explicitly has historical W1/W2 n=0, hypothetical currency mix, unidentified RNPL revenue-flow sensitivities and no certified pre-hedge reference. Its 180 scenario rows are not 180 forecast observations. The parameter/stress machinery can implement the assumption but cannot identify it. Replacing a stock-derived unpaid fraction with a new label does not repair its denominator. The independent numerical bridge correctly avoids consuming these conditional timing outputs as an adopted adjustment.

RNPL's effect on cash can differ from its effect on revenue. A timing delay in own service-fee cash changes working capital even when earned revenue is unchanged. A host/customer liability is not corporate excess cash. L4's inherited cash assumptions, including its unearned-fee treatment, therefore remain assumptions requiring the separate economic review. This accounting review does not endorse a year-end 2027 valuation as a 3–12 month target or certify a complete inherited financial model.

## Decision-useful conclusion

The defensible claim is that a transparent operating forecast produces small, vendor-dependent revenue differences and explicit break-even conditions. The LSEG reference's +0.58% revenue gap can be erased by a 0.88% change in the unprinted Q3 GBV input under held-fixed conversion. A 0.59pp relative cushion change can erase its hypothetical guide gap without any change in actual revenue. Neither crossing is a probability statement. The missing cohort, FX, management-policy and expectations links remain economically relevant because they can alter the comparison's sign; arithmetic correctness does not resolve them.

The parent should present source-stamped same-basis differences and observable conditional boundaries, retain separate operating and communication-policy effects, and keep RNPL/FX causal magnitude and trading alpha unproven. No further loss search, extra simulations, forced direction or synthetic expected return is warranted by this review.

## RESUME

Wave 2 F is complete. Parent may consume the exact v2 bridge under the independent receipt and incorporate the missing-observation ledger into its final argument. The v1 timestamp finding is closed by the narrowly checked v2 change; all old files are preserved. Worker C next independently reproduces worker A's frozen-protocol prospective implementation. This review signed off neither its author's prior Q4 audit nor its own reproduction code as independently reviewed; parent remains the adjudicator of those artifacts.
