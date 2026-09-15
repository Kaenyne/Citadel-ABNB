# L3 source-contract supplement

Local follow-up to accepted L3 bundle commit `8821961853e4068febbfe2712f9a4e1036c9e629`; original research source is `7fb6fe0f248d5492b899672b9b70545da62d63ee`. This package audits source precision/availability, accounting denominators and downstream consumption. It does not refit a forecasting model, change frozen data, register forecasts or integrate L4's workbook, valuation or memo.

The prior five-parameter full22 fit remains descriptive; free/fixed chronological RMSE1.165407390/1.015512948 fails promotion. Preserve the existing fixed2/3–1/3 operational seasonal estimator, which is different from the newly fitted matched fixed-OLS comparator. W2 is nested in W1. Conditional FX/ADR, missing fee theta, failed NCLH transfer and comparator-only hotels remain qualified accordingly.

## Reproduce

From the repository root, with the existing Python environment (pandas and pytest plus dependencies specified by child READMEs):

```powershell
python -B -X utf8 analysis/src/forecast_methods/l3_source_contract_v1/run.py --out data/processed/forecast_methods/l3_source_contract_v1/rebuild_NEW
python -B -X utf8 analysis/src/forecast_methods/l3_source_contract_v1/preserve.py --compare data/processed/forecast_methods/l3_source_contract_v1/preservation_start.json --out data/processed/forecast_methods/l3_source_contract_v1/preservation_NEW.json
```

On this host use `C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe`. Every destination must be new and inside the new source-contract data root. No network is required for the offline runners: source facts, original-release/filing evidence and inspected interface/inventory snapshots are frozen compact inputs. Public-source retrieval and any inventory capture helpers are separate commands; they are not rerun automatically.

`run.py` executes independent integration tests, each child package's tests in a separate process, and three child runners. It retains commands, exit codes, durations and stdout even if a step fails. It checks exact preservation of all original1187 consumption rows, blocks numeric missingness or scenario assumptions being promoted to observed inputs, and verifies the old bundle and core data before/after. It produces no combined revenue or guide forecast.

`preserve.py` reads actual commit and tree objects, verifies108 old bundle files against both Git and worktree bytes, ties70 output and34 review-note payloads to the original research commit, and compares frozen core files/registries with the start receipt. Existing frozen suites are not rerun merely because this new audit exists.

## Package ownership and evidence

- `precision/`: all24 quarters receive checked/unavailable coverage for scoped GBV/revenue/nights/ADR fields; direct and derived values, precision, classification and first-known dates remain separate. Sensitivities hold a named inherited lambda fixed.
- `accounting/`: event timing, denominator and FX/hedge/baseline definitions, conditional routes and explicit blocked routes. Correct arithmetic does not identify physical flows.
- `consumption/`: all1187 original bundle rows retain their complete fields and receive one of six statuses; exact missing-input needs and a committed L4 interface inspection accompany them.

Source dates, audit retrieval dates, and filesystem timestamps are different fields. Long stays need monthly recognition qualification. Monetary remeasurement, revenue hedge reclassification and future hedge assumptions are different objects. Cancellation effects require a baseline reconciliation. Revenue consensus is not observed guide expectations.

## Freeze a reviewed local handoff

After committing new source/results/notes and the independently closed `review_acceptance_v1.json`:

```powershell
python -B -X utf8 analysis/src/forecast_methods/l3_source_contract_v1/pack.py --results data/processed/forecast_methods/l3_source_contract_v1/results_v2 --out data/processed/forecast_methods/l3_source_contract_v1/supplement_NEW
python -B -X utf8 analysis/src/forecast_methods/l3_source_contract_v1/pack.py --verify --out data/processed/forecast_methods/l3_source_contract_v1/supplement_NEW
```

The packer reads committed blobs and refuses changed/uncommitted sources or an existing destination. Its root checksum manifest covers all files except itself, including any nested checksum manifests. The final local handoff supplies actual source and supplement-containing commits and hashes. Publication to the public repository remains unauthorized.

## RESUME

Read the final lead handoff and independently reviewed package conclusions. L4 consumes the permitted observed/conditional inputs with all conditions attached; the quant task owns any new preannouncement or investment robustness tests. Further physical flow data or future captures can reopen only their affected claims in new versions. The original bundle and failed model promotion result remain intact.
