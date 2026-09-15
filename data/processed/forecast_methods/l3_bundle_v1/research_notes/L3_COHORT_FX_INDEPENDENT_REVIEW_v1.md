# L3 cohort FX independent review v1 — four rate validation findings

Reviewer: nclh subagent, independent of cohort_fx authorship. Date: 2026-09-13. Reviewed `cohort_fx_v1` source, tests, canonical tables, primary accounting sources and mathematical counterexamples. No authored FX code or output was edited by this reviewer. **Conditional exposure/replacement arithmetic survives; four malformed-rate acceptance defects require repair before implementation closeout.** This is the original finding record, to be followed by a new closure note.

## Findings reproduced

| ID | Severity | Concrete counterexample | v1 result | Required repair |
|---|---|---|---|---|
| FX-R1 | P1 | In the canonical `fx1.00` rate table, set EUR/2026Q1 `information_date=2026-02-01`, `quote_cutoff=2026-03-31`, keeping as-of 13 September | RateBook accepts a quote later than its stated source vintage | Enforce quote cutoff no later than the row's information timestamp; treat deterministic USD identity explicitly |
| FX-R2 | P2 | Set observed EUR/2026Q1 `quote_cutoff=2025-01-01` | RateBook accepts an observed quarterly rate whose cutoff precedes that quarter | Enforce temporal consistency between observed-rate period and quote cutoff |
| FX-R3 | P2 | Retain every other year but only the first 2025 quote per currency, then request Q2/September 2026 rates | rate_table accepts a supposedly complete fixed-2025 reference; EUR reference is one daily value, 1.0261 | Validate fixed-reference coverage and endpoints/gaps, or refuse to label an incomplete reference complete |
| FX-R4 | P2 | Keep full annual-2025 history and every other date, but keep only the last 2026Q2 observation per currency | rate_table emits fully observed Q2 averages with n=1; EUR 1.1417 | Apply an explicit coverage/boundary/gap requirement to each required observed-period slice, including the observed portion of mixed observed/flat periods |

The attacks were run on temporary in-memory copies, leaving all original data untouched. They expose reuse/ingestion risks; they do not establish that the current frozen cache has these defects. The source/date gates already reject ordinary after-as-of inputs, but those tests alone did not catch internally contradictory source stamps or sparsely sampled historical averages.

Reproduction entry points, from repository root:

```python
from cohort_fx_v1.engine import RateBook
from cohort_fx_v1.run import rate_table, FX_PATH
# R1/R2: mutate only the identified EUR/2026Q1 row, then:
RateBook(modified_rates, "2026-09-13")
# R3: keep first 2025 quote per ccy, all non-2025 rows:
rate_table(sparse_2025, {"2026Q2", "2026-09"}, 1)
# R4: keep last Q2-2026 quote per ccy, all non-Q2 rows:
rate_table(sparse_q2, {"2026Q2"}, 1)
```

The four exact input mutations are specified in the table. The author accepted the findings and is producing a versioned replacement, preserving v1. No new fitted FX/RNPL coefficient or research pass claim is authorized by these repairs.

## What independently survived

The review reran the author's suite: **35 passed**. Independent checks across all 180 canonical scenarios found constant inherited booking-kernel baseline (zero dollar spread), each target's w sum equal to one, ordinary-plus-RNPL reference exposure equal to one, each cohort/currency p sum equal to one, zero-RNPL replacement equal to zero, delta exactly T−B within CSV rounding, and replacement multiplier T/B distinct from the normalized-reference multiplier T/R0. Every adapter row retains its scenario-only evidence status and unresolved-hedge gate. All year-ago illustrations explicitly use u=0.

A separate reference-rescaling counterexample multiplied every EUR reference rate in the two-cohort hand example by 2.75. B, T, incremental replacement dollars and T/B were invariant. Normalized reference dollars and w may change with the reference basis; the economically applied replacement does not. This supports the division-by-booking-factor construction. It also confirms why multiplying an already translated B by T/R0 would be incorrect.

The six foreign currencies are converted to USD per foreign unit individually before any exposure weighting; a broad currency index is excluded. No L2 unpaid-stock diagnostic or unidentifiable migration solve is used as a measured revenue-cohort RNPL share. The grid's u/currency/p inputs are labelled assumptions; 180 scenarios do not create 180 observations. Current sources and the 2025 reference are assembled in 2026, so the year-ago comparison remains retrospective; W1/W2 n=0 is correctly stated.

## Accounting and identification review

Independent reading of the [FY2025 10-K](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm) supports check-in recognition for accommodations, separate guest/host currency and payment risk, FX exposure on confirmed unbilled RNPL bookings, and a 56% annual non-USD revenue share. It does not provide a quarterly revenue-cohort currency/RNPL allocation or establish that RNPL's economic FX fixing date is its recognition date. The author preserves that distinction. Long-term stays have monthly recognition rules; the aggregate monthly allocation is a sensitivity, not a reservation-level measurement.

The [Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm) confirms that cash-flow-hedge reclassifications can enter revenue. An inherited lambda fitted on reported revenue cannot automatically certify a hedge-free reference basis. The no-new-hedge rule and conditional-adoption fields correctly prevent an unsupported second adjustment. The result must remain scenario-only until L4 reconciles its chosen baseline's embedded FX/hedges and the u/p/currency evidence.

## RESUME

Independently rerun R1–R4 against the author's versioned repair, inspect the coverage conventions and date precision, verify canonical scenario economics are unchanged, and publish a new closure note. Retain this initial finding record. Closure may approve reusable implementation with explicit assumptions; it cannot promote a measured RNPL timing effect or predictive FX edge.
