# F vintage audit

From the repository root:

```text
./.venv/Scripts/python.exe -X utf8 analysis/src/forecast_methods/refute_f_vintage_v1/run.py
```

Rebuilds the frozen stock statistic and live scenario with independent arithmetic, audits all 12 registration dates, and writes receipts under `data/processed/forecast_methods/refute_f_vintage_v1/`. It uses F's declared ADR as a conditional input. No package functions, scorers, registrations or network requests run; source files remain unchanged. Existing coefficient alternatives are a retrospective structural sensitivity, not new empirical evidence.
