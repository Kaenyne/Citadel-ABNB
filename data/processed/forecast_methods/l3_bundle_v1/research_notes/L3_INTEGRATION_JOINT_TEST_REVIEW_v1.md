# L3 final integration check v1 — import collision; five adapters preserve metadata

Independent reviewer: nclh subagent. 2026-09-13. Conversion author confirmed model/run/tests stable and results_v1 complete before this review. No shared source code or existing output was edited; no bundle or commit was created.

The reviewer executed the **exact combined pytest command** defined by `analysis/src/forecast_methods/l3_integration_v1/run.py`, using the project interpreter, flags `-B -X utf8 -m pytest`, and the same ordered targets: cohort_fx_v2 tests, fee_panel_v1/test_fee_panel.py, l3_adr_hotel_v1/test_audit.py, nclh_transfer_v1/test_nclh.py, l3_integration_v1/test_bundle.py, conversion_validation_v1, then `-q`.

Result: **exit 1; 127 passed, 5 failed, 3 subtests passed in 11.88 seconds**. Full command, elapsed subprocess time and output are preserved under `data/processed/forecast_methods/l3_integration_v1/independent_joint_pytest_v1/` in `receipt.json` and `stdout.txt`.

All five failures are conversion test AttributeErrors on `r.load` or `r.run`. NCLH's earlier collected test module imports its runner as the generic module name `run`. Conversion later adds its directory to sys.path and imports `run as r`, but Python reuses the already cached NCLH module. Changing sys.path does not bypass sys.modules. The conversion suite's standalone success therefore does not establish compatibility with this combined command.

The lead was notified to isolate suite processes or use unique package-qualified/importlib module names. This is an integration/import defect, not evidence that conversion numerical results fail. The original joint failure must remain in the receipt history; rerun the repaired aggregate command before claiming complete integration.

The separate, read-only five-adapter normalization check **passes all 1,187 rows**: cohort FX 1,080, fee 2, ADR/hotel 86, NCLH 12, conversion 7. Values including nulls, units, evidence status, original source period and original source information date are preserved exactly in every package. All individual and concatenated schemas validate; no duplicated semantic keys or columns appear. Canonical sources are cohort_fx_v2/results_v2, fee_panel_v1/reviewed_v3, l3_adr_hotel_v1 root, nclh_transfer_v1/results_v4 and conversion_validation_v1/results_v1.

Conversion's five full-sample parameter rows remain descriptive, jointly five-parameter and not adopted as operational replacements; its two PIT RMSE ratios retain n=14/n=10 and the no-guide-input qualification. One minor units interpretation should accompany consumption: `seasonal_conversion_Q#` values such as 12.9319 are coefficient levels in percent of weighted GBV, although their label says `percentage_points_of_weighted_GBV`. They are not percentage-point additions to revenue growth. The `shared_lag_w` unit and no-measured-booking-probability limitation are explicit. Bootstrap bounds remain labelled small-year-block sensitivities, not assured forecast intervals.

## RESUME

Lead should close the module-import collision and preserve a passing repaired joint-test receipt. The five-adapter normalization is accepted with the coefficient-unit interpretation above. Then verify the actual production bundle and committed bytes; this review did not create or verify that final artifact and does not adopt a forecast.
