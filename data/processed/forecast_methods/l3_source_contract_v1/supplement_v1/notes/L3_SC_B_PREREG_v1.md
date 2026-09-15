# SC-B — accounting and FX/RNPL source contract preregistration

cohort_fx · 2026-09-14 · codex/lane3-full · new `l3_source_contract_v1/accounting/` only.

## Scope and acceptance

This is an evidence and interface audit, with zero fitted parameters and no new forecast or thesis test. Preserve the original committed L3 bundle and its 1,080 cohort-FX rows. Build a self-contained accounting dictionary plus one metadata-enriched contract row per original FX row; preserve original values, bounds and evidence labels. Cover booking, cancellation processing, cash receipt, contractual FX fixing, settlement, short-stay recognition and the disclosed monthly long-stay qualification. Every adjustment definition and exported row must identify numerator, denominator, units, cohort/recognition period, source/date, admissible origin, evidence, embedded FX, hedge basis, baseline overlap, and exactly one conditional/diagnostic route or an explicit unusability reason.

The accounting acceptance line is complete definitions and rejection of invalid consumption, not identification of missing physical flows. RNPL remains within GBV; no incremental demand, automatic cancellation haircut, stock-to-flow mapping, or recognition-date FX fact will be invented. Missing hedge reconciliation and measured RNPL revenue flow remain unavailable. Fixed kernel coefficients, arithmetic contribution weights, forward cohort allocations and backward revenue-origin shares stay distinct. The fixed operational kernel and the accepted descriptive/free-weight FAIL results remain unchanged.

## Sources and cutoff

Review public SEC FY2025 10-K and Q2 2026 10-Q directly, plus existing accepted bundle and the two original-workspace QVS notes. Preserve original filing dates and source vintages; retrieval/audit date is September 14, 2026. Current retrieval does not prove archived historical availability of the precise downloaded bytes. Keep only compact paraphrased facts, section/URL references and source hashes. The existing local FY2025 extraction has distributor cover pages and is not SEC HTML; label its hash accordingly. No consumer/help Airbnb pages, licensed retrieval, raw-store copying, collection or outreach.

## Validation before completion

Meaningful deterministic checks: missing/blank metadata and future origins rejected; denominator/unit mismatches rejected; mixing mutually exclusive FX routes or re-applying FX to reported USD GBV rejected; unsupported hedge/stock/recognition-fixing assumptions rejected; all 1,080 source rows retained exactly; every schema key has a unique explicit route or reason; fresh-output rebuild reproduces bytes and existing output reuse fails. Synthetic arithmetic counterexamples only illustrate algebra and do not produce ABNB forecasts. Independent review is SC-A; SC-B later reviews SC-C. Each failed validation or material definition disagreement is preserved in a new note.

## RESUME

Author completes the compact source ledger, event and denominator definitions, validator and reproducible runner, then freezes a new output for SC-A review. Lead reconciles cross-package definitions and publishes only a local source-contract supplement; original L3 and L4 outputs remain unchanged.
