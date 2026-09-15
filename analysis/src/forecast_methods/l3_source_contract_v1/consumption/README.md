# SC-C: lossless L3 consumption classification

This package labels the 1,187 frozen L3 bundle rows and audits the existing L4 interface. It creates no forecast, model adoption, valuation, registration or combined adjustment. It changes no L4 file. `usable_as_conditional_scenario` permits a clearly labelled existing scenario exhibit; `direct_l4_model_application=blocked` remains separate for every row.

From the isolated L3 repository root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 -B -m pytest analysis/src/forecast_methods/l3_source_contract_v1/consumption/test_consumption.py -q
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 -B analysis/src/forecast_methods/l3_source_contract_v1/consumption/run.py --out data/processed/forecast_methods/l3_source_contract_v1/consumption/results_v3
```

Use a new `--out` for every rebuild. Existing directories are refused, including failed ones. Runtime dependencies: Python standard library; pytest for tests. All rebuild inputs are local frozen evidence; no external L4 worktree, network, Git execution, collector or clock refresh is needed.

Canonical results are `results_v3`, with 27 focused tests. Prior results and verification receipts are retained. Independent review prompted stricter direct-classifier date/unit checks and clarified operating-only FX multiplier and ADR growth-rate definitions; every original value and classification count remains unchanged. The original unresolved aggregate multiplier is not certified for use on pre-hedge revenue merely by adding a hedge number. V3 further specifies that each fee theta requires only its named monthly triplet: September 14/16/18 or October 12/14/16. Both triplets are needed only for both outputs, with no automatic pooling.

`consumption_matrix.csv` preserves the original 28 fields as strings, in their original order, without converting numeric values or missing cells. Appended fields define permitted use, the six-status classification, direct-model blocker, exact additional inputs, source-row SHA256, row ordinal, bounds meaning, metric definition, parent baseline and dependencies. All 33,236 original cells must match. The output date September 14 is a new classification date; original September 13 bundle dates and earlier source dates remain intact.

`information_gaps.csv` contains the exact requirements linked by `gap_ids`. `interface_audit.csv` records committed-L4 compatibility and provenance findings; `guide_basis_audit.csv` retains the original selected LSEG-family revenue-comparator fields and labels the different forecast objects. This basis audit subtracts existing captured values only; it does not estimate a guide expectation or construct a new forecast. `existing_data_inventory.csv` is a frozen, bounded local inventory. `source_manifest.csv`, `summary.json` and `manifest.json` provide provenance, counts and hashes.

The two unavailable fee rows and two incomplete hotel rows remain blank. Four complete hotel observations are comparator-only, not observed ABNB inputs. Failed NCLH and conversion tests remain descriptive evidence; they are not discarded as bad observations. Thus observed-input and rejected counts are both zero. FX replacement level, delta and multiplier are mutually exclusive representations of one scenario; reference-level factors remain descriptive. Free-w promotion FAIL and the fixed operational policy remain unchanged; W2 is nested in W1. Bounds retain component/RSS or six-block sensitivity meanings, not forecast probabilities.

The evidence freezer `freeze_evidence.py` is a separate, explicit one-time acquisition tool, not called by `run.py`. It used actual L4 Git commit `29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`, verified nine blobs and compared working bytes only for audit. Compact exact contract code/helpers and captured output rows are frozen in `inputs_v2`. Tests execute the exact contract functions from that snapshot with synthetic fixtures, including root-quote and commit-membership gaps. The original L4 loader's documented parent-verification requirement is preserved.

At 2026-09-14 04:28:03 UTC (00:28:03 New York), the two configured local fee stores contained no wave CSV. All 16 checked files across fee stores and local ABNB primary disclosures matched baseline content after CRLF normalization. The 12 byte differences were newline-only. `inputs_v1` retains the first inventory before the content comparison was added; canonical `inputs_v2` separates byte changes from new information. A 04:35:15 UTC filename-only scan of the original data/research trees found no alternative fee capture directory among matched nonignored paths. These scoped inventories do not prove that no disclosure exists elsewhere. No collector was started or awaited; the future schedule was not treated as an observation.

## RESUME

Reproduce into a new directory, compare file hashes, and read the independent B-on-C review before parent integration. L4 or quant owners may use this as an evidence contract and gap list. Model integration still requires an explicit accepted version, exact baseline/hedge/currency provenance and appropriate same-basis expectations. No missing data is solved by relabelling it as zero, causal or observed.
