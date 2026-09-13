# B′ FY term structure

Run from the repository root with the project venv interpreter:

```text
python analysis/src/forecast_methods/alpha_b/run.py --as-of 2026-09-12
python -m pytest analysis/src/forecast_methods/alpha_b/tests -q
```

Imports the verified `kernel_engine_v2` for every lambda and kernel forecast. Writes only `data/processed/forecast_methods/alpha_b/`. The note and preregistration are `docs/revenue-forecast-strategy/05_backtests/ALPHA_B_TERM_STRUCTURE.md`. Historical FY calculations abstain when any of the four quarters is unavailable. Consensus needs an attributed vendor and a strictly earlier timestamp. Live RNPL scenarios are conditional assumptions available 11 September; they are never inserted into historical origins. Weight endpoints use K0's fixed lambda and are arithmetic sensitivities, not refitted kernels or probabilistic bounds.

The frozen harness supports quarterly targets, fixed guide dates and 11 September only. It cannot accept a 12 September annual gap. A candidate schema and explicit `registry_status.json` are emitted locally; no false quarterly registration is made. Parent owns scoring.
