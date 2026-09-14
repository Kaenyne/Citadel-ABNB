# WP-Q1 immutable source audit

Run from the quant worktree root:

```powershell
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/source_audit_v1/run.py --out data/processed/forecast_methods/quant_thesis_validation_v1/source_audit_v1/reproduction_NEW
```

The runner uses Python's standard library and Git only. It reads immutable Git objects from L3 commit `8821961853e4068febbfe2712f9a4e1036c9e629` and one explicit L4 file from `29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`, compares local source bytes, checks the 108-file bundle and accepted conversion source hashes, parses 20 retained guidance quotes, and exports source availability and precision tables. Existing output directories are refused. There is no outcome fitting, scoring, registration or network request. Missing source data remain missing.

Canonical output is `results_v3`. `results_v1` used a rounded illustrative Q3 lambda; `results_v2` added accepted-source identity and parsed guidance display precision. Version 3 uses the exact committed L4 operational lambda for the source-precision dollar sensitivity. Earlier outputs are preserved. See the WP-Q1 note for limitations and the one repaired L4 column-name error before version 3 completed.
