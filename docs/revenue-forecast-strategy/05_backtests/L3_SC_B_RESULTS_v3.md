# SC-B — final author freeze after hedge-label correction

cohort_fx · 2026-09-14 · codex/lane3-full. Supersedes the output pointer and hedge-preservation wording in `L3_SC_B_RESULTS_v1.md`; preserves that note and all prior outputs. The substantive evidence, 38 definitions, nine clocks and 16 facts are unchanged. Independent approval belongs to SC-A.

**Canonical output is `data/processed/forecast_methods/l3_source_contract_v1/accounting/results_v3/`.** All 1,080 original FX rows retain every original field. Conditional exhibit rows remain 540, diagnostic rows 540, direct L4 admissions zero. The inherited hedge component is explicitly unresolved: no new hedge overlay and no claim of certified unchanged hedge dollars or after-hedge correctness. `L3_SC_B_HEDGE_LABEL_REPAIR_v1.md` records the issue before repair tests and gives the nonzero-H counterexample. A new test rejects the earlier overstrong label. No model or forecast changes.

Commands, from the isolated L3 root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 -m pytest analysis/src/forecast_methods/l3_source_contract_v1/accounting/test_accounting.py -q -p no:cacheprovider
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/l3_source_contract_v1/accounting/run.py --out data/processed/forecast_methods/l3_source_contract_v1/accounting/results_v3
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/l3_source_contract_v1/accounting/run.py --out data/processed/forecast_methods/l3_source_contract_v1/accounting/results_verify_v3
```

Tests: **32 passed in 2.30 seconds, exit 0**. Both runners exit 0, tool-wall 0.55/0.73 seconds. Direct byte comparison: **8/8 files identical**. No empirical test was run; fitted parameters remain zero. Earlier 28/31-test checkpoints had no failures. No source values changed in this repair.

| Artifact | SHA-256 |
|---|---|
| accounting_contract.csv | `e4738571b2e3dfe7b031cdeac5e9dcf2a3a8be039a51cb44cfa0f5768aad9ee2` |
| definition_contract.csv | `e8da83695b725aced23ec208fe723eabe760cdefab3feaecbd1a362d3ec65561` |
| SHA256SUMS.json | `45b4249a02ac1cb013d83a35d2afae0b4e750b80943c3b67934ece3a0c7510a9` |
| run.py | `1d42ab63e0803d5be13e265767e2248202c520d4f8f78b10a36025c6262e6b6a` |
| source_contract.json | `eb1ac4b11d73644a3984a878226b2f96f8df0f7fb3070ae4ce37a66c2114b41c` |
| test_accounting.py | `848c7b3c4b8e7c3afa900dce5ae94d94638f327718730990516bdec50f48608e` |

## RESUME

SC-A reviews v3. Lead should consume that exact output, preserve the unresolved hedge qualification, and cross-check SC-C's classification. New accounting evidence or a reconciled operating-only FX ratio and explicit H would require a new application contract; none has been supplied or adopted here.
