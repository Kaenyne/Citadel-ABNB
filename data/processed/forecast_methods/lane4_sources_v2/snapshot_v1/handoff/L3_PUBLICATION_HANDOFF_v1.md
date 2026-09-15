# L3 publication handoff to L4

2026-09-13 · branch `codex/lane3-full` · no L4 workbook, valuation, memo or registry edits.

## Immutable identity and reading order

- Bundle: `data/processed/forecast_methods/l3_bundle_v1/`.
- Committed research source: `7fb6fe0f248d5492b899672b9b70545da62d63ee`.
- Bundle checksum-manifest SHA-256: `9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970`.
- `SHA256SUMS.json` covers 108 exact files; bundle schema validates all 1,187 research rows across five packages. The manifest itself is identified by the hash above.
- The lead's final delivery supplies the published bundle-containing commit and draft PR; do not assume uncommitted files are visible to another task. Review and merge remain human decisions.

Begin with `payload/conversion/final_review_acceptance.json`, its hash-bound `accepted_validation_spec.json`, `claim_ledger.csv`, and figures `01_seasonal_conversion`, `02_weight_identification`, `03_chronological_validation` (each PNG and SVG). The review receipt explicitly closes the initial pending-review status without overwriting the original specification. Independent review notes and all accounting limitations are included under `research_notes/`.

## Accepted specification and presentation-safe claims

`R_t = lambda_s × [w GBV_(t−1) + (1−w) GBV_(t−2)]`, USD millions. Fit four seasonal through-origin rates and one shared bounded weight using USD-level least squares on all 22 lag-complete quarters, 2021Q1–2026Q2. This is an accepted **descriptive** calibration: w=0.786478481, with Q1/Q2/Q3/Q4 coefficients 12.931911% / 13.224232% / 17.302744% / 12.111558%.

At every guide-date origin, refit on available observations only. Free/fixed matched-OLS RMSE is 1.165407 in W1 (n14) and 1.015513 in W2 (n10), so the preregistered promotion hurdle fails both windows. **Retain the existing fixed 2/3–1/3 operational benchmark.** Neither newly fitted free-w nor all22 fixed-OLS coefficients are silently adopted as replacements.

The fitted weight is year-sensitive: 0.538731 excluding 2021 and 0.356963 using 2023 onward. Its six-year-block percentile sensitivity is 0.307910–0.857332. Paired chronological ranges span one in both windows. These small overlapping samples support caution about identification; they do not establish statistical superiority or an exact booking share. Conversion coefficients are not commission take rates, w is not a recognition probability, and a tight descriptive fit does not prove forecasting edge. Guide+cushion already uses the target guide and does not test forecasting that guide.

Other accepted inputs are conditional FX weights/scenarios and ADR composition evidence. Fee theta remains missing because 0/6 scheduled captures are available on September13. NCLH transferability fails and supplies no ABNB adjustment. Hotel observations are comparators, with actual hotel production unavailable. Do not double-count reported-USD FX, imposed ADR fee mechanics, RNPL demand or hedge effects. Keep evidence, units, missingness and replacement fields intact.

## Validation and reproduction

All six new suites pass: **132 tests plus 3 subtests**. All five offline runners exit0 and **69 generated files reproduce byte-for-byte**, including the 24 conversion numerical/chart outputs. An additional **155 existing tests pass**; **4,046 protected hashes** and **284 scorer rows** remain unchanged. Detailed commands/results/failures are in `L3_LEAD_AUDIT_v1.md`, package notes and `data/processed/forecast_methods/l3_integration_v1/reproduction_v1/reproduction.json`. Original failures and all earlier output versions remain preserved.

From the repository root, using the documented Python environment:

```powershell
python -B -X utf8 analysis/src/forecast_methods/l3_integration_v1/run.py --out outputs/l3_reproduction_NEW
python -B -X utf8 analysis/src/forecast_methods/l3_integration_v1/bundle.py --verify --out data/processed/forecast_methods/l3_bundle_v1
python -B -X utf8 analysis/src/forecast_methods/l3_integration_v1/score_snapshot.py --out outputs/l3_scores_NEW
```

On this host the interpreter is `C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe`. The FX runner's optional `--fx-bundle` argument points to the original read-only R interface bundle; it affects only its provenance manifest, not the financial calculations. The final integrated run included that argument; its exact command is retained in the lead audit. Fresh runs always require new output paths.

To rebuild the handoff, check out research commit `7fb6fe0f248d5492b899672b9b70545da62d63ee` in an isolated checkout, then use:

```powershell
python -B -X utf8 analysis/src/forecast_methods/l3_integration_v1/bundle.py --out data/processed/forecast_methods/l3_bundle_NEW --input cohort_fx=data/processed/forecast_methods/cohort_fx_v2/results_v2/l4_adapter.csv --input fee_panel=data/processed/forecast_methods/fee_panel_v1/reviewed_v3/l4_inputs.csv --input adr_hotel=data/processed/forecast_methods/l3_adr_hotel_v1/l4_adr_hotel_inputs.csv --input nclh=data/processed/forecast_methods/nclh_transfer_v1/results_v4/l4_evidence.csv --input conversion=data/processed/forecast_methods/conversion_validation_v1/results_v2/l4_conversion_inputs.csv
```

The new bundle version name changes its metadata and root manifest; canonical payload bytes should remain identical. Code/selected payloads must be committed and clean. The original bundle is immutable. Source-worktree provenance hashes are line-ending-specific; bundle-local attributes preserve payload bytes through Git.

## Pasteable message for L4

L3 is complete and independently audited on published branch `codex/lane3-full`; use the bundle-containing commit supplied with this handoff. Consume `data/processed/forecast_methods/l3_bundle_v1`, built from research commit `7fb6fe0f248d5492b899672b9b70545da62d63ee`; verify `SHA256SUMS.json` (manifest hash `9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970`). Start with conversion's final acceptance receipt, specification, claim ledger and three charts. The full22 descriptive fit is accepted, but free-w forecast promotion fails W1/W2, so retain the existing fixed 2/3–1/3 operational benchmark. FX and ADR are conditional inputs; fee theta is unavailable; NCLH transfer fails; hotel data are comparator evidence. L4 retains ownership of the combined guide forecast, workbook, valuation, memo and registrations. All adoption remains pending your and the team's review.

## RESUME

Fetch the published commit, verify the bundle, and consume only the accepted claims and explicitly conditional inputs. No additional L3 collection is required to complete the current handoff. Future fee captures or newly identified cohort, timing, hedge or dated ADR inputs can reopen only their affected research questions in new versions. Preserve the benchmark and prior research while L4 performs its own integration.
