# F power refutation

From repository root: `./.venv/Scripts/python.exe -X utf8 analysis/src/forecast_methods/refute_f_power_v1/run.py`

Reads the frozen F package and D1 source, recomputes endpoint arithmetic, Wilson intervals, exact illustrative binomial power, scenario and sample counts; writes only its own audit JSON. Does not register or invoke any scorer. The dated pre-registration is in `data/processed/forecast_methods/refute_f_power_v1/PREREG.md`. Results are conditional on frozen upstream fitted inputs; this is not a new stock-model fit.
