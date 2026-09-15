# Independent accounting and expectations review

Canonical reviewer script: `run_v2.py`. The initial `run.py` targeted the parent's v1 outputs and is preserved without execution after the parent issued v2 metadata. Both scripts are new review-only work, with no author calculation imports. The canonical run verifies four source files directly against L4 Git commit `29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`, independently reproduces the parent's v2 arithmetic using Decimal and an affine kernel representation, and compares every shared numeric field between parent v1 and v2.

From the quant worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 'analysis/src/forecast_methods/quant_thesis_validation_v1/accounting_review_v1/run_v2.py' --out 'data/processed/forecast_methods/quant_thesis_validation_v1/accounting_review_v1/results_v2'
```

Completed output is `results_v1`; select a new destination on a repeat. Existing destinations and destinations outside this exclusive package are refused. Standard Python library only. No model fit, resampling, external fetch, registration or production mutation occurs.

The independent receipt binds the exact reviewed parent code, protocol, outputs and four source CSVs. It does not certify future changes. The accounting interpretation and independent SEC verification are in `docs/revenue-forecast-strategy/quant_thesis_validation_v1/accounting_review_v1/ACCOUNTING_EXPECTATIONS_REVIEW_v1.md`.

## RESUME

Wave 2 F is complete. Parent should incorporate the same-basis comparisons and missing causal-link ledger into its final argument. Worker C next independently reproduces the prospective package authored by worker A, once the canonical implementation/output version is supplied.
