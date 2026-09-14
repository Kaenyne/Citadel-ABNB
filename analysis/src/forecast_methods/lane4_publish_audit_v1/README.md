# L4 pre-publication audit

Audits the final L4 artifacts at commit
`3da2903e2c78f6beea358819e7c561b07a5f49a3`. The runner also accepts a descendant
commit containing only additions, so the audit records can be committed without
changing the audited model/source bytes. No new research fit or forecast is
registered. Old artifacts and publication-status notes are preserved.

From the L4 worktree root, run each check with a new run ID:

```powershell
$l4Python = 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe'
& $l4Python -B -X utf8 analysis/src/forecast_methods/lane4_publish_audit_v1/run.py --check sources --run-id audit_new
& $l4Python -B -X utf8 analysis/src/forecast_methods/lane4_publish_audit_v1/run.py --check revenue --run-id audit_new
& $l4Python -B -X utf8 analysis/src/forecast_methods/lane4_publish_audit_v1/run.py --check model --run-id audit_new
& $l4Python -B -X utf8 analysis/src/forecast_methods/lane4_publish_audit_v1/run.py --check review --run-id audit_new
& $l4Python -B -X utf8 analysis/src/forecast_methods/lane4_publish_audit_v1/run.py --check numeric --run-id audit_new
& $l4Python -B -X utf8 analysis/src/forecast_methods/lane4_publish_audit_v1/run.py --check preservation --run-id audit_new
```

Different checks can run independently. Each check refuses to overwrite its own
receipt/log. The four focused suites contain 94 tests. Numeric checks invoke the
independent revenue and raw-OOXML audits; preservation verifies 4,381 original
tracked-file hashes, 76 registry files, 135 original external FX dependency
files and the 108 accepted L3 bundle entries. No unchanged historical scorer is
rerun because no registry or scored output changed.

The source and financial publication reviews separately inspect committed
bindings, the complete L4 push payload and final claim definitions. The old
preview-runtime exit and serialized-whitespace diagnostics remain documented;
unchanged workbook/PDF layouts reuse the completed visual review.

## RESUME

Read `L4_PUBLICATION_AUDIT_v1.md` plus the two independent publication reviews.
The user's audit-and-push request supersedes earlier local-only instructions.
Publish only the reviewed L4 branch through an ordinary non-force push; do not
merge into main, contact teammates or sign investment decisions.
