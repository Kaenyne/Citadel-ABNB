# SC-B — final author receipt after independent input-binding repair

cohort_fx · 2026-09-14 · codex/lane3-full. Canonical output: `data/processed/forecast_methods/l3_source_contract_v1/accounting/results_v4/`. This supersedes prior output pointers while retaining all v1–v3 outputs and notes. Independent reviewer: SC-A / adr_hotel; this author receipt is not self-approval.

**33 tests pass; eight output files reproduce byte-identically.** Every original FX row/value remains unchanged. Counts remain 1,080 source rows, 38 definitions, nine event clocks, 16 compact primary facts, 540 conditional arithmetic exhibits, 540 diagnostics and zero direct L4 admissions. Missing RNPL flow/fixing/hedge evidence remains unavailable; the fixed model and all research conclusions remain unchanged.

SC-A identified by code inspection that the conditional gate rebuilt canonical rows without rechecking the source hash, although the main runner checked it. The shared bound-source loader now protects both paths. The new temporary-copy regression changes an actual conditional row, re-enriches it and rejects its attempted admission at the expected-hash gate. The original source is never mutated. SC-A independently ran its copied-adapter +$1M attack against repaired code and observed the same explicit rejection; no pre-repair exploit execution is claimed. The repair protocol is preserved in `L3_SC_B_INPUT_BINDING_REPAIR_v1.md`.

The source manifest now supplies the exact `local_hash_path` for all seven audit anchors, including cached SEC/distributor files. Those files remain read-only source references; no new raw-source runtime dependency or fresh-byte provenance claim is introduced. Five core outputs—accounting contracts, definitions, timing, primary facts and summary—are byte-identical to v3. Only source-path provenance and source/checksum receipts changed.

Exact commands, from the isolated L3 root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 -m pytest analysis/src/forecast_methods/l3_source_contract_v1/accounting/test_accounting.py -q -p no:cacheprovider
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/l3_source_contract_v1/accounting/run.py --out data/processed/forecast_methods/l3_source_contract_v1/accounting/results_v4
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/l3_source_contract_v1/accounting/run.py --out data/processed/forecast_methods/l3_source_contract_v1/accounting/results_verify_v4
```

All exit 0. Tests: **33 passed in 1.21 seconds**. Runners: tool-wall **0.68 and 0.51 seconds**. Direct comparison: **8/8 byte-identical**. There was no empirical model test or forecast execution; new fitted parameters remain zero. Review findings and all earlier checkpoints are preserved.

| Artifact | SHA-256 |
|---|---|
| accounting_contract.csv | `e4738571b2e3dfe7b031cdeac5e9dcf2a3a8be039a51cb44cfa0f5768aad9ee2` |
| definition_contract.csv | `e8da83695b725aced23ec208fe723eabe760cdefab3feaecbd1a362d3ec65561` |
| source_manifest.csv | `a72db19f588a0ba6de1b62f912573e01c570ea0b5722686392a5fa6f7aa5f331` |
| SHA256SUMS.json | `d03ca7a1f56c6f2db3af78ec5696a9492a9d8e396b3e0244cf27e49c0fd4bede` |
| run.py | `a66257d5484b178e9c8cecfba391391dc3b6bf611014cf1b29d5fbd6db0d6e79` |
| source_contract.json | `2b4bfa3547cf53d13e4055c0a894c312007ea6c1f59b604b4ff643f22b1b21db` |
| test_accounting.py | `93319197efc5fcd4ddea87d736ab56c73f224ff41650070a410b8ed5cedbcdf1` |
| README.md | `3e9d89c7fd2ae513d8a2df31c40a54badf14f8e04fe73699925c46de51d67002` |

## RESUME

SC-A completes independent primary/identity verification against exact v4 hashes. Lead should bind that approval and this receipt into the source-contract supplement, separately from the original L3 bundle. SC-B's review of SC-C is already closed in `L3_SC_REVIEW_C_v2.md`; neither review authorizes direct L4 model application, a hedge-neutrality claim or investment adoption.
