# Publication content scan

Read-only scan of the 631 quant additions at sealed handoff commit `b1e8885a6c294e1b212f9b908a9ce5fbeb3c1ec4`. Reads Git blobs directly, records identities/sizes/types and emits sensitive-pattern candidates as paths/types/counts only. It does not inspect the complete outgoing ancestry or perform publication.

From the quant worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/publication_audit_v1/content_review/run.py --run-id scan_v1
```

The canonical run exists. Use a fresh run id, such as `scan_recheck_v1`, to reproduce; overwrite is refused. Output stays under `data/processed/forecast_methods/quant_thesis_validation_v1/publication_audit_v1/content_review/<run-id>/`.

The separate human prose/type review and permission boundaries are recorded in `docs/revenue-forecast-strategy/quant_thesis_validation_v1/publication_audit_v1/content_review/CONTENT_REVIEW_v1.md`. The signed review receipt is in the matching data `content_review/review_v1/receipt.json`. Candidate absence is a bounded screening result, not an exhaustive encoded-secret guarantee. No prospective or economic calculation is repeated.
