# WS31: Apply the Codex audit

Read `docs/margin-build/00_BRIEF.md`, `docs/margin-build/audit/CODEX_ASTRA_AUDIT.md`, `docs/margin-build/SYNTHESIS.md`, and the notes for any
method a finding touches. Slug: `31_apply_audit`.

## Do

1. Triage every finding into: accept-and-fix, accept-but-defer (say why, e.g. needs data not on disk), reject (with the evidence that the
   auditor is wrong, reproduced). Write `docs/margin-build/audit/AUDIT_RESPONSE.md` with a table `id | severity | decision | what changed | files |
   evidence` before you start fixing, then update it as you go.
2. Fix accepted findings in place inside `analysis/src/margin_build/` (this run's own code; the copy-never-overwrite rule protects files
   outside this run, not the run's own working files, but keep a `_pre_audit` copy of any CSV whose numbers change, e.g. `23_forecasts_pre_audit.csv`).
3. Re-run, in order: the affected method `run.py`s, `10_harness_margin/score.py`, `23_final_model/run.py`; regenerate the workbook; check exit codes.
4. Update `SYNTHESIS.md` numbers and add a section "Post-audit changes" listing every number that moved (before -> after) and every finding
   rejected with the reason. Update the method notes only with an appended "Audit response" section (do not rewrite history).
5. If a critical finding cannot be fixed tonight, say so at the top of SYNTHESIS.md in bold and in the AUDIT_RESPONSE, and quote the affected
   numbers with the caveat rather than deleting them.
6. Final message: what changed, what did not, what remains open.
