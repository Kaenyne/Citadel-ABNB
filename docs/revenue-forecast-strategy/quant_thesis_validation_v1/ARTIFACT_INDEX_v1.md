# Canonical deliverables and permitted consumption

All paths below are relative to the quant worktree root, with these prefixes: **D** = docs/revenue-forecast-strategy/quant_thesis_validation_v1; **T** = data/processed/forecast_methods/quant_thesis_validation_v1; **C** = analysis/src/forecast_methods/quant_thesis_validation_v1. Prior versions and failed attempts remain the audit trail. The later L4 handoff binds exact analytical-commit identities and final seal status.

| Required deliverable | Canonical artifact |
|---|---|
|1. Mission, workboard, resume | D/MISSION_WORKBOARD_v1.md; D/WORKBOARD_FINAL_v3.md; final handoff RESUME |
|2. Immutable evidence, availability, precision | T/evidence_v3/{identity.json,external_manifest.json,protected_manifest.json}; T/source_audit_v1/results_v3; D/source_audit_v1/ADDITIONAL_Q2_2025_SOURCE_DISCREPANCY_v1.md |
|3. Preregistration and attempts | D/FINAL_PROTOCOL_v1.md; D/protocol_design_v1/PROTOCOL_PROPOSAL_v1.md; D/CHAIN_PROTOCOL_v1.md; D/PROTOCOL_FREEZE_v1.json; T/prospective_v1/results_v1/attempt_ledger.json; D/ATTEMPT_AND_REPAIR_LEDGER_v1.md |
|4. Complete empirical and uncertainty results | T/prospective_v1/results_v1/{forecast,evaluation}; T/uncertainty_audit_v1/results_v2; D/prospective_v1/WP_Q2_Q3_RESULTS_v1.md; D/uncertainty_audit_v1/UNCERTAINTY_AUDIT_v2.md |
|5. Expectations and economic break-even | T/expectations_v2; T/economics_v1/results_v2; D/accounting_review_v1/ACCOUNTING_EXPECTATIONS_REVIEW_v1.md; D/economics_v1/{RESULTS_v1.md,PUBLICATION_REPAIR_v2.md} |
|6. Claim ledger | T/claims_v2/{claim_ledger.csv,claim_ledger.json,publication_metadata.json}; verdict applies to tested_claim, while permitted_sentence supplies bounded wording |
|7. Presentation and figures | D/PRESENTATION_DEFENSE_v2.md; T/figures_forecast_v3/preannouncement_forecast_test.{png,svg}; T/figures_v1/expectations_break_even.{png,svg} |
|8. Independent reproduction and reviews | T/independent_reproduction_v1/complete_run_v2/independent_completion_receipt.json; T/adversarial_review_v1/results_v2/receipt.json; T/accounting_review_v1/results_v1/independent_receipt.json; T/final_contract_review_v1/uncertainty_checks_v1/receipt.json; latest H/I final artifact receipts bound in handoff |
|9. Immutable L4 handoff | Subsequent local handoff directory: analytical commit, exact file hashes, final acceptance and permitted use; no production integration or public publication |
|10. One-page decision summary | D/delivery_v3/ABNB_decision_summary.pdf; D/DECISION_SUMMARY_v3.json; the rendered canonical PDF was independently and visually inspected |
| Reproducibility interface | C/run.py; C/README.md; T/reproductions/final_v1/{run_receipt.json,canonical_comparison.csv};17 stages exit0 and59 exact comparisons |

The accepted immutable inputs stay at L3 `8821961853e4068febbfe2712f9a4e1036c9e629` and L4 `29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`. The source Git objects, external note copies and protocol hash manifest provide the archive identity. New reconstruction outputs do not replace either lane's forecast, workbook, model or registry.

The actual forecast origins cannot be represented truthfully by shared harness formats1.0/1.1 with guide-specific target availability/precision. The frozen protocol records that limitation; all63 method-origin rows, training/input vintages, failures and abstentions remain in the exclusive local ledger. No registration occurred, so no new scorer run is required; existing scorer and registry bytes are protected and verified.
