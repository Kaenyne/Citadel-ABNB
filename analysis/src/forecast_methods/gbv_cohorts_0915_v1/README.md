# Booking-cohort feasibility figures

Descriptive charts only; no new model, fitted parameters, forecasts or harness registration.

From the worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' analysis/src/forecast_methods/gbv_cohorts_0915_v1/run.py
```

Requires Python, numpy, pandas and matplotlib. On another machine use its Python interpreter. Outputs PNG, SVG, CSV and a source-hash manifest in `outputs/gbv-cohorts-20260915-v1`. For another run supply `--out` pointing to a **new** directory; existing output directories are refused.

The aggregate ratio is verified against frozen KPI inputs. The K2 plot reuses saved exploratory estimates; raw reservation files are not present on this machine and the underlying estimation was not rerun. See the new `improvement_0915_theo_cohort_audit_v1.md` note for source definitions and limitations.
