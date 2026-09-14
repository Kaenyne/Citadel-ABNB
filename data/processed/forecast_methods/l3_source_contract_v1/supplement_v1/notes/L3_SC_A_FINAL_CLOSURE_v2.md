# SC-A final closure

2026-09-14. Author `adr_hotel`; independent review by `nclh` is closed in `L3_SC_REVIEW_A_v2.md`. Canonical outputs: `data/processed/forecast_methods/l3_source_contract_v1/precision/results_v2`.

The reviewer reran all five original adversarial cases against the repaired code: all reject. All31 tests pass, and an independent nine-file reconstruction matches canonical V2 byte for byte. Source facts, numerical results, coverage and classifications remain unchanged. V1 failures/results remain preserved; V2 clarifies aggregate-unit and analysis-date metadata and hardens validation.

Final scope remains96cells over24quarters and four metrics only. There are92 checked original values and four unavailable original IPO values;18GBV quarters have finer or later corroborating evidence. Main categories67exact/18rounding/4laterprecision/2definitiondifferences/5unresolved remain descriptive. The unresolved original2020Q4 revenue and2025Q2 GBV differences, later2022Q2 display inconsistency, IPO availability gap and six missing GBV precision quarters remain open evidence needs. Current held-fixed sensitivity is+4.658820541731m, n=1 arithmetic, zero fitted parameters and no revised forecasts. Fixed2/3–1/3 policy and free-w FAIL remain unchanged.

Final run.py SHA256 `f82b66018b7a3cdd337b1c479307460c712ff2f219d95e7d02024f031dcfb2a5`; input manifest `af137faedf8df00513234e500b265b6809b1a595d6c4a87329f245614f4e5a80`; V2 output manifest `c805076609dd5975061cfb0ab9a36b853e6b7426e3a7c2f997e3c5ef7c4323e5`. No analytical source changed after the lead's completed full integration run.

## RESUME

Lead may integrate the independently accepted V2 source audit with final SC-B/SC-C contracts. Keep original histories and every prior output unchanged. Report the narrow four-metric scope and the distinction between source-value availability and September analysis/coefficient dates. Evidence gaps remain honest gaps; they do not authorize source rewriting, forecast adjustment or model refitting.
