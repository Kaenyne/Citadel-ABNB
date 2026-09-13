# A2 power refutation

From the repository root, using the repository virtual environment:

```text
python analysis/src/forecast_methods/refute_a2_power_v1/run.py
```

Inputs are read-only A2 outputs, its registry and the underlying returns_v1 event table. The script independently recomputes the primary sign using registry PIT guide dollars and consensus denominators, checks rounded guide-gap signs and source return joins, and writes a new audit JSON, event tables and threshold sensitivity table under `data/processed/forecast_methods/refute_a2_power_v1/`.

Alpha 5% one-sided and 80% power describe reference binomial and iid normal designs. No economic minimum effect or dependence model is inferred from the small sample. The additional 0.5pp and 1.5pp cutoffs are new refuter stress tests, not evidence that the original package tried these thresholds. No forecasts are registered; the parent owns scoring and the shared workboard.
