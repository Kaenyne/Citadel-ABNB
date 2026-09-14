# F mechanism refuter

Independent reconstruction of the frozen fee stock, fee-only counterfactual, and the disclosed RNPL gross cancellation stress. No RNPL package function is imported, no coefficients are fitted, and no forecasts are registered. K0 supplies its unchanged Q4 lambda. Outputs are new files under `data/processed/forecast_methods/refute_f_mechanism_v1/`.

Run from the repository root:

```text
./.venv/Scripts/python.exe -X utf8 analysis/src/forecast_methods/refute_f_mechanism_v1/run.py
```

The script stops if any claimed endpoint or scenario arithmetic fails its preregistered tolerance. Counterfactual fee rates and rebooking offsets are sensitivities, not empirical estimates.
