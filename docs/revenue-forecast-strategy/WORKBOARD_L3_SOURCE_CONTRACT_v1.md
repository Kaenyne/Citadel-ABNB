# L3 source-contract follow-up — claims and bounded audit protocol

2026-09-13 · lead · `codex/lane3-full`, starting at local commit `8821961853e4068febbfe2712f9a4e1036c9e629`. Publication remains unauthorized after the earlier automatic approval rejection. This follow-up is local only.

| Package | Status | Author | Exclusive new paths | Acceptance |
|---|---|---|---|---|
| SC-A source precision | claimed | adr_hotel | `l3_source_contract_v1/precision/` under new analysis/data package roots; `05_backtests/L3_SC_A_*.md` | All24 quarters checked/unavailable; primary conversion metrics GBV/revenue/nights/ADR scoped explicitly; differences classified with source, first-known date and arithmetic sensitivity |
| SC-B accounting/denominators | claimed | cohort_fx | `l3_source_contract_v1/accounting/`; `05_backtests/L3_SC_B_*.md` | Event timing and every proposed adjustment have explicit numerator, denominator, units, source/vintage, hedge/FX/overlap and allowed route or unavailability reason |
| SC-C consumption/gaps | claimed | nclh | `l3_source_contract_v1/consumption/`; `05_backtests/L3_SC_C_*.md` | All1187 original rows classified into six statuses without losing values/metadata; committed L4 interface inspected read-only; available new captures/disclosures checked without collection |
| SC-INTEGRATION | claimed | lead | new package root runner/README, results and manifests; `05_backtests/L3_SC_LEAD_*.md` | Original committed objects/checksums preserved; cross-package definitions reconciled; rotated independent review; reproducible supplement and manual L4/quant handoff |

Wave2 rotates reviewers: C reviews A, A reviews B, B reviews C. Reviewers write their own NEW independent review files under `05_backtests/L3_SC_REVIEW_*.md` and do not approve their own authored package. No nested delegation; parent plus three active workers maximum.

This is an evidence/accounting audit, not a new forecast selection test. No free-w refit, historical data rewrite, new forecast series, trade test, registry or L4/quant edit. Accepted full22 descriptive coefficients and failed free/fixed RMSE ratios1.165407390/1.015512948 (W1n14/W2n10) are frozen conclusions; W2 is nested in W1. Preserve existing fixed2/3–1/3 operational seasonal estimation policy.

Analytic precision materiality is predeclared as `dR_t/dGBV_(t−1)=lambda_s*2/3` and `dR_t/dGBV_(t−2)=lambda_s*1/3`, holding the explicitly identified inherited lambda constant. Combined input differences are linear sums. This is a local sensitivity calculation, not a refitted model or point-in-time forecast replacement. Where no compatible inherited lambda is available, retain a normalized derivative or an unavailable status. Later filing precision is never moved into an earlier information set. No empirical performance pass line is introduced or changed.

Source search is bounded to available primary filings/original earnings material and existing sanctioned local outputs. Unavailable primary values or dates remain gaps. Each table states its metric scope, so checking all24 quarters does not imply every unrelated derived column of the wide KPI panel was audited. All prior negative/partial findings remain. Completion depends on classifying evidence honestly and closing review defects, not on obtaining unidentified physical cohort shares or future data.
