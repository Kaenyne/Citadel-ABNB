# B2 vintage refutation

From the repository root:

```text
.venv\Scripts\python.exe analysis/src/forecast_methods/refute_b2_vintage_v1/run.py
```

The audit uses independent consensus selection, explicit date-truncated KPI inputs, the imported kernel engine's lambda estimator, a separately constructed trailing-eight median cushion, and executable return components. It compares the published B2 cells, retains counterfactual look-ahead scenarios and a synthetic post-close robustness diagnostic, and writes to a fresh run folder. No registry, original output, or frozen file is changed.
