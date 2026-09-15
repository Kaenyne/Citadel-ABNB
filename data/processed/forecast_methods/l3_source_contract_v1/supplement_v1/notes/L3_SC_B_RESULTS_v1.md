# SC-B — accounting, denominators and FX/RNPL source contract

cohort_fx · 2026-09-14 · codex/lane3-full · exclusively new `l3_source_contract_v1/accounting/` analysis/data and `L3_SC_B_*` notes. Zero fitted parameters. Preregistered in `L3_SC_B_PREREG_v1.md` before tests.

## Verdict

**Accounting/interface implementation complete for independent review; physical RNPL flow, contractual fixing and forward hedge evidence remain unavailable.** The package preserves all 1,080 original FX rows and every original field, while assigning explicit definitions and consumption restrictions. There are 540 conditional arithmetic rows and 540 diagnostic rows. **None is admitted for direct L4 application.** No coefficient, model, forecast, registry, original bundle, L4 artifact or investment conclusion changes.

Canonical output: `data/processed/forecast_methods/l3_source_contract_v1/accounting/results_v2/`. The original `results_v1` and its verification remain as checkpoints; their accounting, definition, timing, facts and source tables are unchanged. A final validator enhancement additionally rejects changed exported denominators, malformed fact dates and unknown event evidence. Its new run source hashes are bound in v2.

## Scope and explicit distinctions

| Audited object | n | Result |
|---|---:|---|
| Original cohort-FX adapter rows | 1,080 | All original 17 columns retained as exact CSV strings |
| Adjustment/definition contracts | 38 | Numerator, denominator, units, cohort/recognition period, provenance, dates, FX, hedge, overlap and route/reason |
| Event clocks | 9 | Separate booking, cancellation, cash, fixing, settlement, two recognition clocks, FX accounting and hedge release |
| Compact primary facts | 16 | Observed disclosure or management expectation, with period/units and section identifiers |
| Hashed source objects | 7 | Two cached public filings, three accepted FX artifacts and two original-workspace QVS notes |
| Meaningful integrity/failure-mode tests | 31 | PASS |
| Fresh-output reconstruction files | 8 | 8/8 byte-identical |
| Direct L4 application approvals | 0 | Exact downstream baseline/manifest and accounting reconciliation absent |
| New empirical forecasts/refits | 0 | Original research conclusions preserved |

The contract distinguishes fixed coefficients from changing arithmetic contribution fractions. For a fixed two-lag kernel, first-lag attribution is `2*G1/(2*G1+G2)`, not necessarily 2/3. In the currency extension, reference weights are `C0_bc/sum(C0_bc)`, and differ from reported-dollar weights. Neither is a measured booking-to-stay probability. Actual backward revenue-origin shares divide `C[b,t]` by the sum over booking cohorts b; forward cohort-recognition shares divide the same cell by the sum over recognition periods t. Those denominators cannot be interchanged.

Reported GBV, a gross original booking cohort, unpaid balances at a snapshot, recognized service-fee flow, and recognized RNPL flow each have different scopes. Existing cancellations in reported net GBV and historical lambda are part of the baseline. A gross cancellation rate or a stock proxy cannot automatically become incremental loss on target revenue. The conditional RNPL u remains inside the full reference-revenue denominator; the extension adds neither demand nor a cancellation haircut.

## Primary disclosure facts and important qualifications

The exact compact paraphrases are in `primary_facts.csv`; event rows point to those fact IDs rather than repeating excerpts. No extended quotations were saved.

**Long-stay correction:** the earlier general check-in wording needs a monthly qualification for stays of at least 28 nights. The contract preserves initial and anniversary recognition clocks, and does not allocate an entire long stay's lifetime fees to its first check-in. The same filing separately describes subsidiary translation, monetary remeasurement, net fee accounting and payment-currency risk; none establishes a universal reservation-level FX fixing date. [FY2025 10-K, Note 2 and Item 7A; filed February 12, 2026](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm).

**Observed versus future hedges:** Q2/H1 revenue hedge losses are disclosed historical amounts, −$19M/−$34M. H1 contains Q2; they must not be summed as separate periods. The approximately $26M next-twelve-month expectation and $3.4B outstanding notional have different units and time scope from a future quarterly revenue hedge. They cannot supply Q3/Q4 hedge dollars. [Q2 2026 10-Q, Note 6; filed August 6, 2026](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm).

For a genuinely matched historical period, `R_ex_identified_revenue_hedges = R_reported - H_signed`. Removing only that known component does not certify every other currency or fee component of a fitted kernel. No historical lambda was retrofitted here. Future baseline hedge decomposition remains unavailable. Payment-related monetary remeasurement and nondesignated derivative offsets belong in their stated P&L reconciliation, not in an extra revenue translation line.

The annual non-USD share is an annual descriptive anchor. It supplies neither a quarterly seven-currency split nor an origin/destination matrix. Currency-of-contract, booking-currency mix and monthly fixing weights remain separate required inputs.

## One consistent conditional route

The bound original FX algebra uses `C0=C_reported/(e_booking/e_reference)`, `R0=sum(C0)`, `B=sum(C0*f_booking)` and `T=sum(C0*((1-u)*f_booking+u*sum(p*f_timing)))`.

| Original metric | Allowed role | Route |
|---|---|---|
| Reference-normalized revenue, R0 | Diagnostic | No reported-baseline adjustment |
| Ordinary booking kernel, B | Identity diagnostic | No addition |
| Retimed revenue, T | Conditional arithmetic exhibit | Replace exactly B with T |
| Incremental replacement, T−B | Conditional arithmetic exhibit | Add once to exactly B |
| Replacement multiplier, T/B | Conditional arithmetic exhibit | Multiply exactly B once |
| Reference level multiplier, T/R0 | Diagnostic | Never multiply reported B |

The three financial routes are equivalent alternatives within one scenario and exclusivity group. Their effects cannot be stacked. A hand-calculated counterexample rejects applying `T/R0` to already translated B. Recognition-timed fixing is a hypothesis even where the accounting recognition clock is known. The payment/fixing-proxy scenario remains a separately identified hypothesis. None is relabeled measured timing or chosen as a point forecast.

`validate_conditional_use` accepts only one unchanged bound source row. It requires the exact original baseline ID/amount, scenario and quarter; reference-basis recognized-revenue u denominator; hypothetical timing; unchanged embedded hedge treatment; current evidence date; and zero extra FX, hedge, demand or cancellation additions. It explicitly returns `production_adoption=false`. Changed source values, denominators, units, targets and financial routes fail. A conditional exhibit permission does not create a direct L4 API or override SC-C's downstream compatibility restrictions.

Company reported-minus-constant-currency growth, the model/model FX growth gap, the model/model RNPL timing gap, a reference level multiplier and current incremental dollars divided by prior revenue are separate definitions. In particular a changed prior-year timing component makes the full YoY timing bridge differ from a current-delta-only approximation. The tests include that counterexample. Management integer-growth rounding and hedge treatment must be reconciled before claiming exact FX percentage-point attribution.

The QVS guide-basis note also remains binding context: revenue consensus and management-guide expectations are different forecast objects. A common-cushion illustration does not convert revenue consensus into observed guide expectations. SC-B makes no new guide or surprise calculation.

## Provenance, timing and limitations

Primary SEC pages were browsed directly on September 14. The manifest hashes the existing local Q2 SEC HTML and the existing FY2025 distributor PDF-text JSON, explicitly identifying each byte basis. The latter has distributor cover pages; its hash is **not** claimed to be an SEC HTML hash. Original filing dates, September 13 bundle/source vintages and September 14 audit dates remain separate. `first_known_date` identifies the reviewed document's publication, not the earliest date an accounting policy ever existed. The exact newly retrieved bytes are not claimed to be an archived historical capture.

A direct Python HTTP attempt failed with Windows sandbox socket error 10013 before downloading source bytes. The web tool successfully opened and verified both primary pages, so no escalation or user intervention was needed. No raw filing store or external FX bundle was copied into this supplement. The runner uses compact in-package facts plus the committed processed adapter; no external-workspace or network dependency is required. The two QVS notes are hashed research references, not runtime inputs.

Unidentified items remain explicit: current global fee/currency cohort matrices; measured RNPL recognized-revenue u; contractual fixing rules; monthly-recognition allocations; additional cancellations beyond baseline; precise future hedge releases; prehedge certification of inherited lambda; and the downstream baseline manifest. Unknowns are not zero values and do not count as failed economic hypotheses. This is not a new W1/W2 test or an adoption vote.

## Exact commands and results

From `C:/Users/wille/Desktop/Citadel - ABNB/.worktrees/lane3-full`:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 -m pytest analysis/src/forecast_methods/l3_source_contract_v1/accounting/test_accounting.py -q -p no:cacheprovider
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/l3_source_contract_v1/accounting/run.py --out data/processed/forecast_methods/l3_source_contract_v1/accounting/results_v2
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/l3_source_contract_v1/accounting/run.py --out data/processed/forecast_methods/l3_source_contract_v1/accounting/results_verify_v2
```

Final tests: **31 passed in 0.94 seconds, exit 0**. Final runners: **exit 0**, tool-wall durations 0.52 and 0.57 seconds. Earlier validation checkpoint: 28 passed in 0.86 seconds. No test failure occurred. The additional three cases strengthened source/denominator validation without changing any fact or contract value.

Reproduction check:

```python
from pathlib import Path
p = Path('data/processed/forecast_methods/l3_source_contract_v1/accounting/results_v2')
q = p.parent / 'results_verify_v2'
assert len(list(p.iterdir())) == 8
assert all(f.read_bytes() == (q/f.name).read_bytes() for f in p.iterdir())
```

| Canonical artifact | SHA-256 |
|---|---|
| accounting_contract.csv | `56d4d59e363aba9c597adf20e134e3aeca4eeb5cc27a301216ee36087bfb6324` |
| definition_contract.csv | `4208d5651be262c724d2b0040584d134b3ebd057da512fe2f87e58ff7639307d` |
| timing_contract.csv | `4688515ff8aaa42acebb56427b74addc582e2d1cb25165c833eebb5a267d86fe` |
| SHA256SUMS.json | `5f1c21af88dffb2bd7333471535875128de76b22163868e5f718076dc0193df5` |
| run.py | `e7053ee9c2595df1569621cb1ffbec253fc3537e423f73f148422823c7807ac0` |
| source_contract.json | `aa27e2a4e56137ed0bb34aa34146415d5dcca16ab79ca27dca6832a5d3744595` |
| test_accounting.py | `8e55d7757c2d9802537333f3abd7e499170e7391f3efaf006592959a561153f7` |

No harness change request. No registration or scorer execution was appropriate.

## RESUME

SC-A independently reviews this accounting package; defects must be repaired in new frozen outputs and retained notes. Lead reconciles SC-B's conditional/diagnostic definitions with SC-C's complete consumption classification, verifies original bundle preservation, and runs this package into another new output. SC-B then reviews SC-C. Only the new source-contract supplement and reviewed accounting limitations should be handed to L4/quant; no original model or production adoption changes automatically.
