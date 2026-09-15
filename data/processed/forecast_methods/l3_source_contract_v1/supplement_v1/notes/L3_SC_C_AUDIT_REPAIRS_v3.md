# SC-C final fee-triplet clarification

2026-09-14. Reviewer B identified one additional requirement-label issue: September and October fee theta are estimated separately. Each coefficient requires its named monthly triplet, not all six waves. Parent authorized this narrow metadata repair after v2 review closure.

Canonical output is now `data/processed/forecast_methods/l3_source_contract_v1/consumption/results_v3/`. September's row requires September 14/16/18 only; October's row requires October 12/14/16 only, with the appropriate monthly treatment/control and existing prereg gates. Both triplets are needed only for both outputs; there is no automatic pooling. Fee theta remains unavailable in both rows, and all original values, source dates, classifications and empirical conclusions are unchanged. No capture was refreshed or awaited.

Compared with v2, only the two fee rows' appended `exact_additional_inputs` and `dependency_contract` fields changed in the consumption matrix. The shared FEE_CAPTURE gap description is clarified consistently. All 33,236 original cells and all 1,187 statuses remain identical. Prior outputs and review notes remain intact.

The focused suite now has **27 passing tests**, adding independent-month dependency checks and an unknown/pooling-month rejection. All **eight output files** rebuild byte-identically to `results_verify_v3`. Exact commands, code/output hashes and the cell comparison are retained in `verification_v3/receipt.json`.

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 -B -m pytest analysis/src/forecast_methods/l3_source_contract_v1/consumption/test_consumption.py -q
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 -B analysis/src/forecast_methods/l3_source_contract_v1/consumption/run.py --out data/processed/forecast_methods/l3_source_contract_v1/consumption/results_v3
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 -B analysis/src/forecast_methods/l3_source_contract_v1/consumption/run.py --out data/processed/forecast_methods/l3_source_contract_v1/consumption/results_verify_v3
```

All commands exited 0. Final matrix SHA-256: `e01442ae80e0e203a93541c5dd40485a8be4edbba09c60b31b3dd007a3220ae1`; output manifest SHA-256: `8243dc27810af147d4333bd25bc9331f76bceec8bcab66690f0a524a0ff1e374`.

## RESUME

Reviewer B should bind the narrow monthly-triplet clarification and unchanged source-cell counts to final v3 hashes. Parent should rebuild its supplement into a new root output version. No additional research or review scope is opened by this correction.
