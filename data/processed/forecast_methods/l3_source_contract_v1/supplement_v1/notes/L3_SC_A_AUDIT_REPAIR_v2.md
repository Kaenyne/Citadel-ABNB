# SC-A independent-review repair

2026-09-14 · author `adr_hotel`, findings supplied independently by `nclh` (SC-C). Original results/preregistration remain unchanged. Canonical output is now `data/processed/forecast_methods/l3_source_contract_v1/precision/results_v2`.

The reviewer verified the canonical arithmetic and primary-source spot checks, then demonstrated five malformed-input failures in the public `build/validate` path: future lambda dates were accepted; a NaN frozen revenue value propagated; a source marked unavailable could still certify original observations; finite source values could overflow during unit conversion; and boolean True could become a numeric booking count. These were latent integrity defects even though checksummed canonical inputs did not contain them. The original failure receipt remains in `consumption/independent_A_review_v1/receipt.json`.

The runner now validates frozen panel numbers, rejects booleans, checks finiteness both before and after conversion, requires every observation and derivation parent to have checked primary text, and enforces `lambda_knowable_from <= kernel_origin <= lambda_information_date <= audit_date`. Seven new adversarial cases cover the five findings plus a missing derivation parent and an origin preceding coefficient availability. An eighth test checks clearer output metadata. No source number, coefficient, classification or sensitivity arithmetic changed.

The normalized nights unit is now `million_aggregate_booked_units`; the original source-unit lexeme `million_bookings` is preserved separately. This distinguishes booked nights/participant seats from a reservation count. Sensitivity rows now separately expose `source_value_first_known_date`, `lambda_information_date`, and `analysis_information_date`. All sensitivity analyses were assembled on2026-09-14; the coefficient has inherited information date2026-09-13. Earlier May/August source values do not imply this complete September calculation was available then. No exact intraday source availability is asserted.

Exact commands, from lane3-full:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -m pytest analysis/src/forecast_methods/l3_source_contract_v1/precision/test_precision.py -q -p no:cacheprovider
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/l3_source_contract_v1/precision/run.py --out data/processed/forecast_methods/l3_source_contract_v1/precision/results_v2
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/l3_source_contract_v1/precision/run.py --out data/processed/forecast_methods/l3_source_contract_v1/precision/results_verify_v2
```

31 tests passed in0.44s; both runners exit0. All9 repeat files are byte-identical. V1→V2 changes are confined to `discrepancy_ledger.csv` unit labels, `kernel_sensitivity.csv` date metadata and `output_manifest.json`. Six other files, including summary, are byte-identical. Inputs are unchanged. Coverage remains96cells/24quarters,92 originals checked/4 unavailable, and held-fixed current sensitivity remains+4.658820541731m.

Reviewed anchors: run.py SHA256 `f82b66018b7a3cdd337b1c479307460c712ff2f219d95e7d02024f031dcfb2a5`; input manifest `af137faedf8df00513234e500b265b6809b1a595d6c4a87329f245614f4e5a80`; V2 output manifest `c805076609dd5975061cfb0ab9a36b853e6b7426e3a7c2f997e3c5ef7c4323e5`. The independent reviewer has been asked to repeat the original attacks against these repaired sources; acceptance is recorded by that reviewer separately.

## RESUME

Integrate V2 after independent SC-C closure. Keep V1 and its failure receipt. Preserve unresolved source inconsistencies and original availability gaps. No historical source rewrite, revised forecast, coefficient refit or change to the retained fixed operational policy is authorized by this metadata/integrity repair.
