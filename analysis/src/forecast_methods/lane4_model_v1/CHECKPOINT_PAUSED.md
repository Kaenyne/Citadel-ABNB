# L4 financial-model checkpoint

Paused 13 September 2026 on the user's changed priority. No final workbook was exported. All development files and failed runs are preserved.

## Completed

- Read spreadsheet skill, complete API quick start, creation/edit workflows, finance/style rules, original model code and valuation conventions.
- Loaded bundled runtimes and created a package-local ignored node_modules junction.
- Imported the original workbook with Artifact Tool, inspected its nine sheets, and produced source Costs/Cash/Valuation inspection files and available PNGs in `data/processed/forecast_methods/lane4_model_v1/`.
- Independent six-lens arithmetic on the published annual CSV reproduces the required $180.876286 EBITDA lens and $156.786845 mean within $0.001. A separate read-only invocation of the original model returned $180.8762933753 and $156.7868471198.
- Wrote `run.py` (Python model, inherited cost/cash/share assumptions, immutable run directories, input manifest), `build.mjs` (single-selector active model and case-capture workflow), `inspect_source.mjs`, and package `.gitignore`.
- Generated `development_run_01/` and `development_run_02/` data directories. Both retain model inputs, annual results, scenario summaries and valuation results. The second includes the source manifest.
- The builder passed the 84 scenario-output numerical comparisons and the legacy reproduction checks before its later stale-capture assertion failed. No successful final check receipt or workbook exists.

## Commands and outcomes

1. Bundled Node `inspect_source.mjs`: nine-sheet inventory and source inspection/render files written. Process ultimately returned exit 1 without a diagnostic message; do not call this fully passed.
2. Read-only import of `13_driver_model.py`: exit 0; original exact arithmetic reproduced.
3. `mark_artifact_operation_started.mjs --operation-kind create --expected-output-count 1 --output-format xlsx`: exit 0, called exactly once. Do not repeat in this conversation.
4. Bundled Python `run.py --revenue-dir data/processed/forecast_methods/lane4_revenue_v1/development_run_02 --run-id development_run_01`: exit 1 after writing results because manifest relative paths mixed absolute and relative paths. Fixed by resolving the revenue directory.
5. Same command with `--run-id development_run_02`: exit 1 in `build.mjs` at `Capture stale detection failed`. Prior numerical comparisons passed. Artifact Tool also warned that Assumptions was missing a required sheetId during early initialization.

## Remaining issues when this package resumes

- Fix stale detection: captured-input equality currently produces booleans counted through COUNTIFS(..., FALSE); investigate engine behavior and use an explicit numeric mismatch count if needed. Preserve blank-versus-zero semantics.
- Create every sheet before writing cross-sheet formulas. `init()` currently links Summary to Assumptions before Assumptions exists, causing the sheetId warning.
- Strengthen selected-missing-input behavior and its perturbation test. The current test only checks a blank in an unselected case.
- Review how later-quarter inherited nights/ADR levels should respond when earlier operating assumptions change. Python propagates prior-year operating levels; workbook currently writes their initial values as editable case inputs rather than calculating that inheritance dynamically.
- Finalize the label for generic ±1% sensitivities: net after-hedge consolidated-revenue perturbations, not measured RNPL or a hedge-preserving pre-hedge FX factor.
- Point final runs at the revenue agent's immutable final snapshot rather than development_run_02; its final handoff was not yet consumed.
- Complete formula-error scan, exported XLSX inspection, all-sheet visual review, formula-cached-value checks, README/tests/result note/RESUME and independent review.
- Neither old nor new revenue estimates or valuation outputs were registered, committed or adopted by this subagent.

## RESUME

Do not resume until the parent assigns the financial model again. The user's new priority is a five-parameter seasonal GBV-to-revenue conversion study. After the listed repairs and verification of a final revenue snapshot, run the bundled Python interpreter on `analysis/src/forecast_methods/lane4_model_v1/run.py --revenue-dir <verified snapshot> --run-id <new unique id>`. Preserve all existing run directories and the original source workbook.
