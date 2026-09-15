# L4 revenue integration v2

Consume the accepted immutable L3 bundle, preserve the operational fixed2/3 K0 seasonal estimator, correct expectations comparisons, and propagate conditional assumptions without estimating a competing model. Information date is frozen at13 September2026; execution date is recorded independently. No registrations, scorers, original files or external FX stores are modified.

From the lane4-full worktree root in PowerShell:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/lane4_revenue_v2/run.py
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -m pytest analysis/src/forecast_methods/lane4_revenue_v2/tests -q -p no:cacheprovider
```

The default writes a NEW `data/processed/forecast_methods/lane4_revenue_v2/snapshot_v1/`. Existing destinations are refused before writing. Rebuild with `--output data/processed/forecast_methods/lane4_revenue_v2/rebuild_<new_ID>`. A different information date is refused. Failed newly-created runs retain `FAILED_RUN.json`. Python requires the existing repository pandas/pytest environment; no install is needed. Output CSVs and source files have scoped `-text` Git attributes for exact bytes. No source estimation runs here.

## Inputs and accounting

`adapter.py` delegates seasonal lambda estimation to the unchanged `kernel_engine_v2` public API. Explicit quarterly USD GBV is independent of the frozen reported panel. ADR/nights must multiply exactly for forecast rows; published rounded actuals remain published inputs. Revenue for quarter t uses two prior GBV quarters. Current Q3 bookings first affect Q4 revenue; Q4 bookings first affect2027Q1. Q3 guide is already issued, so all Q3 implied-guide outputs are diagnostics.

`integration.py` rechecks all108 accepted bundle hashes under the fixed manifest identity before reading source copies. The source worker's separate receipt proves actual Git-object/source lineage and32 acceptance bindings; this package attributes that review and does not claim a fresh statistical replication. L3 free-weight promotion failed W1/W2; matched fixed OLS is distinct from the operational K0 seasonal policy. Baseline fifteen rows are checked against v1 within$0.001m.

`l3_contract.py` is a guarded future application interface, not an RNPL estimator. It requires certified matching pre-hedge multiplier, explicit signed baseline H and scenario H_new, compatible reference exposures and cohorts, and reconciled fixing/recognition timing. It calculates `R_new=m_pre*(R-H)+H_new`. Missing H is never zero; unchanged H_new requires an explicit named assumption. After-hedge/unresolved ratios cannot enter as pre-hedge. The accepted bundle is **not eligible** for central FX application: baseline hedge split and compatible pre-hedge certification are missing, exposures/RNPL shares are conditional, and Q4/Q1 target-specific source rows do not exist. Null estimated FX is unresolved, not an estimate of zero.

## Output contract

Dollar units are USD millions unless a copied source filename retains `_usd` fields. Percentage-point stresses and decimal cushions are separately named.

| Files | Object and permitted use |
|---|---|
| `forecast.csv`, `operating_inputs.csv`, `cohort_weights.csv` | Five original conditional operating cases, unchanged dollars; updated accepted-conversion and unresolved-FX status |
| `expectations_comparison.csv` | Own revenue minus separately dated vendor revenue consensus is primary. Own guide minus revenue is a labelled different-object diagnostic. Hypothetical Street guide applies an explicitly assumed Street cushion; it is not observed guide consensus |
| `hypothetical_street_cushion.csv` | Common or alternative Street-cushion assumptions; not a source of observed guide expectations |
| `joint_scenarios.csv`, `joint_scenario_bridge.csv`, `conditional_envelope.csv` | Main fixed-K0 reference/soft/firm conditional cases and exact sequential operating/conversion/cushion dollar attribution. No probability or predictive-band claim |
| `joint_expectations.csv` | Q4 main-case comparison to the frozen Yahoo/LSEG revenue observation, with the separate hypothetical common-cushion guide calculation |
| `descriptive_joint_draws.csv`, `descriptive_joint_extremes.csv` | All1000 existing **rejected free-weight model** five-parameter tuples projected on fixed reference GBV/cushion; min/max Q4-result intact tuple vectors and full22 point. Separate descriptive exhibit, never a K0 band or a production/bear/bull scenario |
| `net_revenue_sensitivity.csv` | Isolated illustrative ±1% consolidated net-after-hedge revenue change; not estimated FX; not combined with conversion stresses |
| `filing_precision_sensitivity.csv` | Exact-filing Q1/Q2 GBV partial input-precision comparison, holding frozen K0 calibration unchanged; no panel/card overwrite |
| `accounting_eligibility.json`, `cohort_baseline_compatibility.csv`, `fx_isolated_diagnostics.csv` | Exact source-worker financial-eligibility records and source-only Q3 timing diagnostics; not applied or extrapolated |
| `accepted_conversion_validation.csv` | Accepted L3 chronological results, read without refit, with horizon and selection limitations |
| `v1_v2_baseline_reconciliation.csv`, `source_ledger.csv`, `run_receipt.json`, `SHA256SUMS.json` | Baseline preservation, provenance and output receipt |

Main `joint_soft` replaces full operating ADR once with its mean-reversion residual case, subtracts0.10 percentage point from each inherited seasonal lambda, uses the legacy3.88% Q4 cushion and trailing-eight mean elsewhere. `joint_firm` uses case-A Q4 nights, adds0.10pp to each inherited seasonal lambda and retains median cushion. Both use net factor1: no additive fee, cancellation, FX or RNPL overlay. The lambda stress size is an assumption, not an estimated confidence bound. The three-quarter vectors preserve quarter timing; no unseasonal compounding creates an annual forecast.

The main bridge first changes operating GBV, then lambda, then cushion. Descriptive joint tuples preserve all four seasonal lambdas with their shared weight and source draw/year identity. Q4-minimum and Q4-maximum tuples need not minimize/maximize Q3 or Q1. Source resampling describes only the fitted rejected model; it omits residual outcomes, forecast GBV error and future cushion uncertainty.

## RESUME

Use final snapshot_v1 and its hashes. L4 model integration owns financial statement and13 September2027 valuation propagation; parent owns registration review. A future empirical FX adjustment requires a newly supplied immutable compatible contract supplement and explicit financial eligibility. Do not refit L3 or overwrite these outputs.
