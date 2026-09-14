# A2 vintage refutation

From the repository root:

```text
.venv/Scripts/python.exe analysis/src/forecast_methods/refute_a2_vintage/run.py
```

Read-only audit of A2 inputs and outputs; all audit artifacts are written under `data/processed/forecast_methods/refute_a2_vintage/`. Uses the mandated K0 engine with independently clipped input frames. Does not import A2 calculation functions for the headline reconstruction, register forecasts, or run scorers.
