# GBV decision visuals

Five scientific figures and one five-page PDF summarize the reviewed model, horizon accuracy, Street comparison, live input exposure and tested repair. Charts bind to immutable result tables and use raw midpoint RMSE. They do not claim predictive intervals, physical cohort identification or a trading return. Prior render versions are retained; v3 resolves dollar-text rendering and legend placement.

From the worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_decision_0915_v1/visuals_v3/run.py --out outputs/gbv-decision-20260915-v3
```

Use a new output suffix to reproduce; existing figures are immutable. The accepted output folder contains a source/output hash manifest. The current coefficient illustration is the20-quarter live joint fit in horizon `results_v2/origin_fits.csv`; displayed percentages are predictor weights, not revenue shares.
