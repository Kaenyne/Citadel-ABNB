# SC-B accounting and FX/RNPL input contract

This package audits definitions and consumption of the existing 1,080 L3 cohort-FX rows. It does not estimate a model or produce a forecast. Run from the isolated repository root:

```powershell
python -B -X utf8 -m pytest analysis/src/forecast_methods/l3_source_contract_v1/accounting/test_accounting.py -q -p no:cacheprovider
python -B -X utf8 analysis/src/forecast_methods/l3_source_contract_v1/accounting/run.py --out data/processed/forecast_methods/l3_source_contract_v1/accounting/results_NEW_VERSION
```

The output directory must be new. Standard-library Python is sufficient for the runner; pytest is needed only for tests. Runtime reads are the package's compact `source_contract.json` and the committed L3 bundle's FX adapter. There is no network, external workspace, raw filing, model-refit or scorer dependency. Source hashes identify the exact previously cached documents or notes inspected during research; the primary SEC pages were independently browsed on 2026-09-14. A local distributor extraction hash is explicitly not an SEC-HTML hash. Publication dates identify these reviewed documents, not the first historical introduction of each accounting policy.

Outputs:

- `accounting_contract.csv`: all 1,080 original FX rows and all 17 original columns retained as exact strings, with metadata appended. There are 540 conditional arithmetic rows and 540 diagnostics. No row is cleared for direct L4 application.
- `definition_contract.csv`: 38 input definitions, each with numerator, denominator, units, periods, provenance, dates, evidence, FX/hedge/overlap treatment, and one route or explicit unusability reason.
- `timing_contract.csv`: nine clocks, including separate contractual fixing, cash, settlement, monthly long-stay recognition and hedge events.
- `primary_facts.csv` and `source_manifest.csv`: 16 compact paraphrased facts and seven hashed sources, with policy/observed/expected distinctions.
- `summary.json`, `run_inputs.csv`, `SHA256SUMS.json`: counts and deterministic identities.

The three conditional financial routes are mutually exclusive: replace B with T, add T−B to identical B, or multiply identical B by T/B. T/R0 is a reference diagnostic, never another gross factor on reported B. Here B is the bound inherited reported-USD kernel, R0 its conditional fixed-reference normalization, and T the original scenario retiming. No scenario values are selected or modified.

`validate_conditional_use([row], request)` admits one unchanged bound row only for a conditional arithmetic exhibit with the exact baseline identity/amount, dates, scenario, recognized-reference-revenue denominator, hypothetical fixing, explicitly unresolved inherited hedge effects, and no additional demand, cancellation or FX/hedge layer. It never admits production use or certifies hedge preservation. Required request fields and the valid fixture are visible in `test_accounting.py`. There is no direct L4 adapter write or automatic consumption route.

The physical recognized RNPL flow, currency-fixing matrix, current forward/backward cohort distributions and forward-quarter hedge reconciliation remain unavailable. Historical Q2/H1 hedge disclosures do not supply a future hedge forecast. The long-stay monthly qualification corrects oversimplified accounting wording while preserving every original output. Details and the independent review belong in new `L3_SC_B_*`/`L3_SC_REVIEW_*` notes.
