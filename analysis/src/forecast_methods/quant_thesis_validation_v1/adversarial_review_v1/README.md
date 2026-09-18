# Independent economic review

```powershell
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/adversarial_review_v1/run.py --out data/processed/forecast_methods/quant_thesis_validation_v1/adversarial_review_v1/reproduction_NEW
```

Uses the Python standard library and immutable L4 Git objects. It does not import or run the economic author's calculation functions. It independently reconstructs financial statement identities, integrates cash/share flows and values lower-revenue counterfactual statement levels before taking differences, then compares canonical economics_v1/results_v2. Existing output directories are refused. Canonical review output: `results_v2`. The initial `results_v1` covered 540 checks; v2 adds the explicitly required repurchase-price/share checks for 567 total, without changing a preceding result.
