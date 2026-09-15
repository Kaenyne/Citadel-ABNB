# Canonical contract-review interface

`README.md` documents the successful technical-rebuild wrapper and independent uncertainty checker. The final analytical artifact judgment is `docs/revenue-forecast-strategy/quant_thesis_validation_v1/final_contract_review_v1/FINAL_REVIEW_v1.md`; its exact manually reviewed files are listed in `FINAL_REVIEW_SPEC_v1.json` and bound in `data/processed/forecast_methods/quant_thesis_validation_v1/final_contract_review_v1/final_receipt_v1/receipt.json`.

From the worktree root:

```powershell
python -B analysis/src/forecast_methods/quant_thesis_validation_v1/final_contract_review_v1/run.py --out data/processed/forecast_methods/quant_thesis_validation_v1/final_contract_review_v1/technical_rebuild_NEW
python -B analysis/src/forecast_methods/quant_thesis_validation_v1/final_contract_review_v1/bind_final_artifacts.py --spec docs/revenue-forecast-strategy/quant_thesis_validation_v1/final_contract_review_v1/FINAL_REVIEW_SPEC_v1.json --out data/processed/forecast_methods/quant_thesis_validation_v1/final_contract_review_v1/final_binding_NEW
```

Use Python3.11+ with Git. All code uses only the standard library. Existing output paths are rejected. The final binder verifies protected/external hashes, every specified independent-review binding, the17-stage root run and59 exact file comparisons, claim CSV/JSON equality, and the two actual figure links. It binds exact canonical source/claim/interface/visual files, but cannot independently recreate a human visual or claim judgment. A changed canonical artifact requires a new manual review and additive specification/receipt.

The prior `EARLY_REVIEW_v1.md` remains a historical checkpoint. Later clarification and final review close its wording/interface issues, including the corrected2023Q1/Q3 abstentions. The final analytical review does not independently approve this reviewer's economics; it relies on A's independently checked economic receipt. The analytical commit and L4 transfer seal are verified separately after local commit, without repeating calculations.
