# SC-A: immutable source precision audit

This offline package audits exactly 24 quarters (2020Q3–2026Q2) and four fields, `gbv_musd`, `revenue_musd`, `nights_m`, `adr_usd`. All other wide-panel columns are outside scope. It neither fits coefficients nor replaces historical data or forecasts. The inherited fixed 2/3–1/3 operational policy and free-weight forecast FAIL remain unchanged.

From the lane3-full worktree root, use a destination that does not exist:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/l3_source_contract_v1/precision/run.py --out data/processed/forecast_methods/l3_source_contract_v1/precision/results_NEW
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -m pytest analysis/src/forecast_methods/l3_source_contract_v1/precision/test_precision.py -q -p no:cacheprovider
```

Canonical output: `data/processed/forecast_methods/l3_source_contract_v1/precision/results_v2`. Independent repeat `results_verify_v2` matches all nine files byte for byte. All31 integrity tests pass. V1 outputs and the independent failure receipt remain preserved. V2 hardens malformed-input checks and makes units and analysis dates explicit; numerical values are unchanged. Frozen compact inputs under `inputs_v1` contain manually recorded primary-source facts, projected original panel values, current inherited lambda rows, calendar and SHA256 manifest. The runner validates those hashes before calculation. Source URLs and provenance describe current SEC text checks, not historical raw-byte archives. Nothing is fetched at runtime.

Outputs: `discrepancy_ledger.csv` (96 rows), `quarter_coverage.csv` (24), `kernel_sensitivity.csv` (51: 48 normalized derivatives, two current component illustrations and one combined illustration), `source_manifest.csv` (47 source attempts), supplemental observations, derived-value arithmetic, summary and manifests. The main ledger distinguishes original observed value/unit from later or finer evidence, normalized units, publication/availability dates, and rounding versus unresolved differences. Empty finer fields mean unavailable precision, not zero discrepancy. Early IPO later corroborations appear in the explicitly named `finer_or_later_corroboration_*` fields and never certify original values. Same-date precision does not establish exact intraday availability.

Result: 92 original cells checked and four original IPO cells unavailable. Classifications: 67 exact, 18 rounding-compatible, four later precision, two definition/derivation differences, five unresolved. These categories are not an estimate of financial reporting errors. The five unresolved include three missing-original IPO cells and two quantitative original-source conflicts; the IPO ADR row also lacks its original source but has separately verified derivation difference. A separate later-display inconsistency remains supplemental.

The current Q3 illustration uses unchanged lambda 17.2548908953%, ewm with five historical seasonal observations, from the inherited cohort FX output. GBV changes +47m for Q2 and −13m for Q1 yield weighted denominator +27m and revenue sensitivity +4.658820541731m. This is one arithmetic example, not a new forecast, validation result or model refit. Revenue/ADR source differences are not passed through a GBV derivative.

## RESUME

Read `L3_SC_A_RESULTS_v1.md`, `L3_SC_A_AUDIT_REPAIR_v2.md` and the assigned independent SC-C review. Consume precision findings only as descriptive source evidence. Preserve original vintages and all output versions; use a new destination for every rerun. Later precision remains unavailable to earlier origins. Any data correction or coefficient refit is a separately authorized future task.
