# Technical publication audit

Run from the preserved worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/publication_audit_v1/technical_review/run_v2.py --out data/processed/forecast_methods/quant_thesis_validation_v1/publication_audit_v1/technical_review/results_v2
```

Use an unused output directory for another run. The script refuses existing destinations and writes only within `publication_audit_v1/technical_review`. It reads the two exact commits, directly reconstructs Git blob identities, rehashes protected/external files and reviewer bindings, verifies the retained 17-stage/59-file execution evidence, and runs the existing 13 prospective plus 7 economics tests. It also checks the root runner's existing-output and path-traversal rejections. Logs retain exact failures; `receipt.json` includes full command argv, source hashes and bounds.

This is a bounded publication audit, not another research iteration. No source edits, model fits, resampling, new empirical alternatives, registrations, commits or network calls are performed. Prior G records are checked for immutable identity only; this reviewer does not independently approve its own G calculations. Prior parent/I approval remains authoritative.

The first helper `run.py` did not use Windows extended-length paths and stopped on a long protected legacy filename. Its failure is retained in `results_v1/ATTEMPT_FAILURE.json`. `run_v2.py` repairs only this review-helper path access. Existing sealed verification scripts already support those paths. No analytical/source modification was needed. The disclosed CRLF and absolute-provenance relocation limits remain unchanged.
