# L4 linked financial and valuation model

Final artifact: `model/lane4_v1/outputs/lane4_model/snapshot_v4/ABNB_L4_review.xlsx`.
Final calculations and receipts: `data/processed/forecast_methods/lane4_model_v1/snapshot_v4/`.
Source revenue bundle: `data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1/`.

Run from the repository root in PowerShell using the bundled runtimes:

```powershell
& 'C:\Users\wille\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'analysis/src/forecast_methods/lane4_model_v1/run.py' --run-id <new-unique-id>
& 'C:\Users\wille\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s 'analysis/src/forecast_methods/lane4_model_v1' -p 'test_*.py' -v
```

The runner refuses to overwrite an existing run directory. Omitting `--run-id` creates a UTC timestamped directory. `--no-workbook` runs only the independent financial calculations. All original files remain read-only. On a new machine, use the runtime loader to locate the bundled Node executable and create an ignored package-local `node_modules` junction to its bundled modules. The workbook is authored with `@oai/artifact-tool`, not Python spreadsheet writers. `run.py` uses only Python's standard library.

## What the workbook does

`Assumptions!E4` is the only case selector. Operating assumptions feed one Revenue build, which feeds Costs, Cash and Valuation. Summary links the completed outputs. The fixed prior-quarter weight is visible once at `Assumptions!F140`; replacing it requires the matched seasonal coefficients from one accepted L3 conversion version. This package does not estimate a new weight or coefficient.

The fixed 2/3 K0 benchmark covers Q3:26, Q4:26 and Q1:27. Those quarters replace consolidated legacy revenue, including overlapping new-business revenue. There is no old take-rate/FX wedge or separate Services/advertising revenue addition. Related inherited operating investment remains in the cost schedule. Q3 contemporaneous nights do not change Q3 revenue; Q3 nights change Q4 revenue and Q4 nights first change Q1:27 revenue. Q3's displayed implied guide is an already-issued-guide diagnostic.

Quarterly operating growth and revenue growth after coverage, and FY28 annual growth, are inherited editable assumptions. The new valuation convention is 31 December 2027, using FY27-end net cash and shares. The separate legacy reconciliation preserves the old approximately September-2027 label with FY27-end balances. Neither is an adopted target. The $181.94 price dated 4 September 2026 is retained only for the inherited repurchase/issuance path, with no current-spot return calculation.

K0 provides GBV without identifying nights or ADR. Its support costs use the review-case nights as an explicit assumption; its revenue and processing costs use its own GBV. The implied later-year operating decomposition remains conditional on that support-cost proxy.

## Cash and earnings conventions

The model retains the original cost-per-GBV, support-per-night, operating-expense, SBC, tax, capex, working-capital, buyback and withholding schedules. Operating income proxy equals adjusted EBITDA less SBC less total EBITDA addbacks. D&A is included in total addbacks and is not deducted twice.

FCF equals adjusted EBITDA plus interest income minus interest expense minus cash taxes plus change in unearned fees plus working-capital residual minus capex. SBC-adjusted FCF subtracts SBC from FCF. Zero change in unearned fees is an inherited cash assumption, not an RNPL estimate. Cash and shares start at 30 June 2026 and consume only second-half 2026 flows in the first roll. Net cash excludes customer funds and corresponding liabilities; no incremental debt financing is assumed. The 597 million share anchor is diluted weighted-average shares used as a period-end proxy, and the issuance/EPS schedules remain proxies.

## Pending integration and sensitivities

L3 conversion-study acceptance and L3 FX/RNPL integration are distinct pending items. A blank incremental sensitivity is visibly unestimated; it is not a measured zero. No RNPL share is inferred from unpaid-backlog stocks.

The two illustrative ±1% cases perturb net after-hedge consolidated revenue in Q3:26, Q4:26 and Q1:27. FY27 Q3/Q4 inherit the changed prior-year revenue bases, FY27 Q2 stays unchanged, and FY28 grows the resulting FY27 total. They are not pre-hedge FX multipliers or measured RNPL effects. No probabilities or causal growth-to-multiple mapping are used.

## Refresh the requested case comparison

The seven columns in Case comparison are saved results captured by changing the one selector, recalculating, reading completed results, and restoring the selected case. They are explicitly not simultaneous live case builds. A cell-by-cell input comparison marks the saved results stale after changes, preserving the distinction between blank and zero.

After saving an edited workbook, recapture into a new directory:

```powershell
& 'C:\Users\wille\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' 'analysis/src/forecast_methods/lane4_model_v1/build.mjs' --refresh '<saved-workbook.xlsx>' --out '<new-output-directory>'
```

The input workbook is not overwritten. Arbitrary edited inputs are recalculated but are not expected to match the original frozen Python snapshot. Compare edited outputs against the appropriate independent assumptions when making a new research claim.

## Validation and limits

Seven Python tests cover the legacy identities, cash/share timing, D&A treatment, K0 cost proxy, sensitivity directions, invalid discount rates and impossible share counts. The builder independently compares 84 case outputs to Python within $0.001 million/$0.001 per share, reproduces both legacy prices, verifies quarter timing and unchanged actuals, changes a later cost assumption, distinguishes selected/unselected missing inputs, distinguishes zero from pending sensitivity, and checks capture staleness. Final formula scan reports zero errors. Saved-workbook recapture is exercised separately.

Artifact Tool performs formula recalculation, export and visual rendering. Native desktop Excel was not automated. PNG rendering writes complete inspectable images, but this Windows runtime consistently returns exit 1 after its success message during process teardown; this is reported as an unresolved renderer exit-code limitation, not a passed command. Workbook build and recapture exit 0. Every sheet was visually reviewed, including the costs/cash schedules, DCF strip, source inputs, case comparison and operating/financial assumption sections. Failed development directories and the paused checkpoint remain preserved.

## RESUME

Consume only explicit accepted L3 bundle versions and hashes. Replace a benchmark weight only together with its matched seasonal coefficients, keep FX adjustments consistent with the baseline's hedge treatment, run the affected tests and build into a new run directory, then refresh the memo/card from its scenario_summary.csv. Preserve all earlier outputs. Publication, registration, scorer runs and investment decisions remain with the parent/team.
