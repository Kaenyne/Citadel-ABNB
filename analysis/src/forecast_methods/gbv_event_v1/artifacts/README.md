# GBV guidance workbook

Author: parent agent. Native spreadsheet authoring uses the bundled `@oai/artifact-tool`, with one four-quarter working build. No full annual/component model. The final workbook was recalculated, tested and saved in Microsoft Excel 16.0; all temporary input changes were restored. The PDF has its own builder under `../artifacts_pdf/`.

From this worktree root, with the bundled Python/Node on PATH and the bundled node_modules exposed to this directory:

```powershell
python analysis/src/forecast_methods/gbv_event_v1/artifacts/stage.py --events run_v3
node analysis/src/forecast_methods/gbv_event_v1/artifacts/build.mjs
& ./analysis/src/forecast_methods/gbv_event_v1/artifacts/verify_excel.ps1
```

The first command stages the canonical audited integration/forecast/event files. The second authors the editable workbook, checks four-quarter outputs and perturbations, scans formula errors and exports. The third uses a separate hidden Excel instance to recalculate the file, verify representative dependencies and fill native chart caches; it closes only its own workbook/application. It requires a Windows logon session with Excel installed. In the managed sandbox this failed with COM0x80070520; a scoped approved execution succeeded. No workbook macros or external links are enabled. The ordinary author/export command exits0.

For initial visual QA, `node .../build.mjs --render` produces 12 sheet-region PNGs. The bundled renderer produced correct previews, but its Windows native teardown subsequently exited0xC0000409 after all saves and assertions completed. An explicit JS exit did not resolve that native failure; that attempt was removed. Rendering is therefore a separate optional diagnostic, never silently converted to success. Default author/export avoids the renderer and exits0. After any fresh export, run the native Excel verification to populate chart caches. An attempted API cache workaround was abandoned before exporting when the scatter API lacked a category formula; final charts keep their original cell bindings.

Final `outputs/gbv-event-20260915/ABNB_GBV_guidance.xlsx` contains seven sheets and seven native charts. `artifact_inputs.json` records exact source payloads and hashes. `workbook_checks.json`, `formula_error_inspection.ndjson`, `native_excel_checks.json` and the independent artifact review record validation. Rebuilding writes this package's own dated deliverable paths; choose another output directory/version before starting a new research vintage. It does not alter protected historical files or register forecasts.

The direct guide expectation inputs are intentionally blank. The chosen Street cushion starts equal to ours but is independently editable, so changing our policy cushion does not automatically move the expectation benchmark. The break-even GBV/lambda rows equate revenue to the named Street revenue and hold other inputs fixed; they are not observed Street operating forecasts or estimated trading probabilities. The precision comparison and historical audit tables are frozen references, not changing outputs of the working scenario.

Read `GE_DELIVERY_v1.md` and `GE_ARTIFACT_INDEPENDENT_REVIEW_v1.md` for the current analytical conclusion and engine/export checks.
