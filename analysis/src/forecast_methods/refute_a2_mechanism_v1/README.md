# A2 mechanism refutation

From the repository root, with `.venv` Python:

```text
python analysis/src/forecast_methods/refute_a2_mechanism_v1/run.py
```

Reads A2's registered PIT kernel point, L0, the source KPI and guide ledgers, and the sanctioned returns files. Independently rebuilds consensus gaps, GBV surprises, partial correlations, next-open 20-bar OHLC returns, fixed hedge sensitivities and season diagnostics. The script validates source reconstruction, writes only its own new output folder, registers nothing and runs neither scorer. No model is tuned or selected by these diagnostics. See `REFUTE_A2_mechanism.md` for the pre-registration and verdict.
