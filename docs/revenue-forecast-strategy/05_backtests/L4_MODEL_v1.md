# L4 — linked financial and valuation model

Codex model subagent · 13 September 2026 · branch `codex/lane4-full` · starting commit `1c87628cedbc94ab8a0e8552743c94485ef353b8`. New packages only: `lane4_model_v1` code/data and `model/lane4_v1`. Preregistration: `LANE4_PREREG_v1.md`. Work was temporarily paused by user steering and then resumed under the confirmed L4 role; the checkpoint and failures remain preserved.

## Verdict

Implementation passes the numerical reconciliation, linked-model and control tests. The final workbook is `model/lane4_v1/outputs/lane4_model/snapshot_v4/ABNB_L4_review.xlsx`, with calculations and receipts under `data/processed/forecast_methods/lane4_model_v1/snapshot_v4/`. Its 84 scenario outputs independently tie to Python within $0.001 million/$0.001 per share, and the exact original accounting calculations reproduce. Conversion-dependent research conclusions remain provisional pending the separately accepted L3 study; FX/RNPL integration is separately pending. No direction, target or probabilities are adopted. Native Excel was not operated; Artifact Tool recalculation/export and read-only OOXML checks are the tested engines. The renderer emits valid reviewed PNGs but returns exit 1 at teardown, an unresolved operational limitation.

## What ran

From repository root, using the bundled Python and Node paths in the package README:

```text
python analysis/src/forecast_methods/lane4_model_v1/run.py --run-id snapshot_v4
python -m unittest discover -s analysis/src/forecast_methods/lane4_model_v1 -p test_*.py -v
node analysis/src/forecast_methods/lane4_model_v1/build.mjs --refresh model/lane4_v1/outputs/lane4_model/snapshot_v4/ABNB_L4_review.xlsx --out data/processed/forecast_methods/lane4_model_v1/snapshot_v4/recapture_qa
node analysis/src/forecast_methods/lane4_model_v1/render.mjs <workbook> <sheet> <range> <new-PNG-path>
```

Final build exit 0, 9.23 seconds in the shell receipt. Seven Python tests exit 0, 0.056 test seconds in the recorded run. Saved-workbook recapture exit 0, including final v4 (8.31 seconds). Rendered views cover all eight sheets across preserved iterations and the relevant deeper assumption and DCF ranges; final v4 Summary, Case comparison, Valuation, legacy rates and financial-input sections were explicitly re-rendered and reviewed. Rendering command teardown exits 1 after writing its success message and valid PNG. Total active work spans multiple user-steered turns; no reliable single uninterrupted elapsed-time statistic is claimed.

Final QA verifies 78/78 source hashes unchanged, zero mismatches. The model's 84 independent ties have maximum absolute delta $0.000000000364 million. Parent's separate OOXML audit on final v4 and its saved-workbook recapture passes 91 cached-value checks, with 1,576 formulas, zero spreadsheet errors, zero external links and maximum difference $0.000007375. Parent also visually reviewed the three final output views and independently confirmed their readability. Workbook SHA-256: `7301722b233041baca2738c76a6aeaa239dda712f43fc42e5d28efcadacf7e4a`. The separate revenue agent independently reproduced the financial cash/share/value bridge and found no quantitative blocker.

## Results

All rows below are deterministic current scenarios, n=1 per scenario; W1/W2 forecasting performance is not applicable. The six lenses are dependent calculations on the same scenario, not six independent observations. No consensus value is used as an annual model driver.

| Calculation | n | Reproduced value | Required reference | Absolute difference |
|---|---:|---:|---:|---:|
| Legacy FY27 EBITDA lens, independent published-CSV equations | 1 | $180.876286421 | $180.876286 | $0.000000421 |
| Legacy six-lens arithmetic mean | 1 | $156.786844934 | $156.786845 | $0.000000066 |

| Scenario (n=1 each) | Q4:26 guide $m | FY27 revenue $m | FY27 EBITDA $m | FY27 FCF $m | FY27 net cash $m | EBITDA-lens value/share | Six-lens mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| Review with fee mechanics | 3,123.419 | 15,952.233 | 5,807.533 | 5,536.825 | 10,282.596 | $184.663 | $160.479 |
| Review without fee mechanics | 3,120.062 | 15,939.531 | 5,797.986 | 5,527.888 | 10,273.218 | $184.372 | $160.196 |
| K0 GBV with reference support-cost nights | 3,158.228 | 16,057.899 | 5,888.213 | 5,612.434 | 10,369.794 | $187.131 | $162.788 |
| Alternative nights A | 3,123.419 | 15,965.564 | 5,814.851 | 5,543.504 | 10,283.701 | $184.875 | $160.687 |
| ADR mean reversion | 3,074.812 | 15,824.413 | 5,708.741 | 5,444.169 | 10,168.445 | $181.627 | $157.529 |
| Illustrative net after-hedge revenue −1% | 3,092.185 | 15,833.199 | 5,687.879 | 5,422.886 | 10,091.256 | $180.894 | $156.824 |
| Illustrative net after-hedge revenue +1% | 3,154.653 | 16,071.268 | 5,927.186 | 5,650.765 | 10,473.937 | $188.432 | $163.866 |

Every EBITDA-lens value uses the inherited 16.5x multiple and FY27 ending shares of 574.598178 million. The review case's FY27 earnings proxy is $3,355.023538 million, enterprise value $95,824.286607 million and equity value $106,106.882756 million. Ending cash and share schedules are visible. The old $181.94 reference dated 4 September 2026 is used only for repurchase/issuance mechanics; no current-price return is presented.

## Scope and accounting interpretation

The model recomputes the fixed seasonal kernel inside the workbook from active GBV and imported lambda, with the 2/3 policy weight visible in one cell. The bridge replaces total consolidated revenue in Q3:26, Q4:26 and Q1:27. The old take-rate/FX wedge and separate new-business revenue addition are removed from covered periods. Operating investment is retained as an explicit cost assumption. There are no newly fitted parameters: four imported seasonal coefficients, one fixed policy weight, existing operating cases and inherited financial drivers are used.

Q2:27 onward uses the original total-revenue year-over-year growth rates on the appropriate updated prior-year revenue bases; FY28 extends the resulting FY27 total with inherited annual growth. Later-quarter nights and ADR also grow matching prior-year operating quantities. These extensions are assumptions, not kernel estimates. K0 identifies GBV only: reference-case nights are explicitly assumed for support costs, while its own GBV drives processing costs and revenue. Its missing ADR decomposition is not filled with a measured-looking claim.

The ±1% illustrations perturb net after-hedge consolidated revenue in Q3:26, Q4:26 and Q1:27. FY27 Q3/Q4 inherit the changed prior-year bases, FY27 Q2 stays unchanged, and FY28 grows the new FY27 total. FY27 revenue therefore changes by ±$119.034436 million, not ±1% of the entire year. These are not pre-hedge FX factors, identified RNPL coefficients, confidence intervals or probability-weighted branches. Blank pending incremental amounts are displayed as unestimated.

Operating income proxy = adjusted EBITDA − SBC − total EBITDA addbacks. D&A is included in total addbacks and is not deducted twice. FCF = adjusted EBITDA + interest income − interest expense − cash taxes + change in unearned fees + working-capital residual − capex. SBC-adjusted FCF subtracts SBC. The zero unearned-fee cash assumption is inherited and does not estimate RNPL migration. Net cash excludes customer funds and matched liabilities; incremental debt financing is held unchanged. Shares start from the original weighted-average proxy and roll only H2 flows after June 2026. Earnings per share divides by ending modeled shares and is labelled a proxy.

New valuation values use 31 December 2027 and FY27-end cash/shares explicitly. The legacy reproduction separately explains the approximately September-2027 label attached to those same year-end balances. The FY28 EBITDA lens is discounted one year. The original FCF-based DCF convention is retained and labelled; this work does not claim a newly underwritten unlevered enterprise DCF. No growth-to-multiple regression is used.

## What failed or remained unavailable

The first data run failed when the input manifest mixed relative and absolute paths; directory resolution repaired it. The first workbook run passed numerical ties but failed stale-capture detection using COUNTIFS on booleans; explicit numeric mismatches repaired it. A later zero-sensitivity test exposed blank/zero handling in the original formula choice; explicit ISNUMBER and case-specific ISBLANK checks repaired it. Early cross-sheet initialization warned about missing sheetId; all sheets are now created before those links. All failed output directories are preserved. Visual review then corrected late DCF number formats, legacy rate precision, missing DCF labels and misleading editable historical/inert growth inputs, creating successive immutable snapshots with unchanged numerical results.

L3 conversion and FX/RNPL bundles have not been accepted by this package. No research estimate or forecast probability was fabricated. The spreadsheet comparison is a tested saved-capture workflow with a visible stale-input warning; it is not a second hidden build or a claim that all scenario columns recalculate continuously. Native Excel recalculation is untested. Rendering produces complete PNGs but its process-level exit status remains abnormal; the successful numerical build/export should not be confused with a successful rendering command.

## Harness change requests

None. This package made no forecast registrations and ran no scorer. Parent owns forecast registration, final frozen-hash/scorer preservation, review and publication.

## RESUME

Use snapshot_v4 for the memo, unsigned card and decision register. Future conversion integration needs a versioned accepted L3 weight together with its matched seasonal coefficients; future FX/RNPL integration needs a separately accepted adapter with explicit baseline and hedge treatment. Rebuild into a new output directory, rerun affected model/control tests, recapture all seven cases after editable input changes, and independently reconcile the revised financial outputs. Preserve the original model, all failed evidence and every earlier snapshot. No team adoption is implied by implementation completion.
