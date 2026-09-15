# L3 ADR and hotel audit v1

From the repository root:

```powershell
python -B analysis/src/forecast_methods/l3_adr_hotel_v1/run.py --out data/processed/forecast_methods/l3_adr_hotel_v1_NEW_VERSION
python -B -m unittest discover -s analysis/src/forecast_methods/l3_adr_hotel_v1 -p "test_*.py" -v
```

Python requires pandas, numpy and scipy (Spearman). This package is offline. Only `S1_scoring.py`, whose import has no writers, is imported from the frozen ADR package. Never execute/import `P1_card_v3.py` to rebuild this audit: it writes frozen output on import. The runner disables bytecode writes and requires an explicitly supplied, nonexistent output directory. Replace `NEW_VERSION` with a fresh version name each run; existing output directories are refused before any write. The published original output remains `data/processed/forecast_methods/l3_adr_hotel_v1/`.

The runner rebuilds 16 ADR score rows, independently checks stored score paths, reproduces J3, reconciles residual/card/K arithmetic, reconstructs US public hotel-price comparators from frozen raw series, preserves incomplete quarters, and rebuilds the 13-market hotel coverage audit. Input hashes before and after are mandatory; a failed integrity check returns exit code 1. Runs into separate new directories are deterministic. `checks.csv` carries counts and failures. The independent review's output-immutability repair and fresh-directory comparison are recorded in `L3_ADR_HOTEL_AUDIT_REPAIR_v1.md`; earlier same-directory reproduction commands in the original results note are superseded.

`l4_adr_hotel_inputs.csv` is the adapter. ADR scenarios are mutually exclusive replacements for the same-quarter ADR. Component rows describe the already-included composition and cannot be added again. Reported ADR/ADR dollars contain their named FX bridge. GBV rows are descriptive identity comparisons on explicit unadopted nights cases, not independently forecast GBV. Same-quarter take-rate revenue is checked but deliberately excluded from the adapter. Hotels never enter ABNB ADR as measured pricing. Missing complete-quarter comparators stay blank.

Information date is the 2026-09-13 audit cutoff; ADR source snapshot is 2026-09-11, hotel input observations extend through July 2026. Input release vintages are not reconstructed. The ADR scoring windows are 2024Q1–2026Q2 (n=10) and 2024Q2–2026Q2 (n=9), distinct from the ABNB harness W1/W2. ADRv3 ratios reproduce a descriptive upper-bound exercise using realised target-quarter mix and retrospective fixed FX calibration. Neither source data nor this audit establishes guide-date PIT alpha. The rounded-ex-FX target is reproduced verbatim; the +/-0.5 interval score is an additional sensitivity, not a changed original verdict.

See preregistration `docs/revenue-forecast-strategy/05_backtests/L3_ADR_HOTEL_PREREG.md` and results `L3_ADR_HOTEL_RESULTS.md`. No model/card/team decision or registry is changed.
