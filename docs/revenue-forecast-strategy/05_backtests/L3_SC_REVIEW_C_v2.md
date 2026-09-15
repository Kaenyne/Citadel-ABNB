# SC-C — independent review closure

Reviewer: cohort_fx (SC-B). Author: nclh (SC-C). Date: 2026-09-14. Canonical reviewed output: `data/processed/forecast_methods/l3_source_contract_v1/consumption/results_v2/`. Code: `analysis/src/forecast_methods/l3_source_contract_v1/consumption/`. This closes the initial findings in `L3_SC_REVIEW_C_v1.md`; original failures and output v1 remain preserved.

## Decision

**Accepted as a lossless evidence-consumption and gap contract. No direct L4 model application or production adoption is authorized.** All 1,187 statuses and all 33,236 original source cells remain unchanged after repair. There are 576 conditional scenario exhibits, 603 descriptive rows, four comparators, four unavailable rows, zero observed-input rows and zero rejected rows. The 1,080 FX rows agree exactly with SC-B's 540 conditional/540 diagnostic split. Missing fee estimates remain missing; valid failed research remains descriptive evidence.

## Findings closed and independent checks

- **F1 date validation closed:** re-executed the original future-row-date and malformed-source-date attacks; both now raise the intended ValueError. An additional exact next-day-midnight timestamp is rejected. The original bundle's September 13 cutoff remains distinct from the September 14 classification date. Source dates cannot follow row dates, and timestamp inputs require an explicit timezone. No old source is refreshed by relabeling its classification date.
- **F2 unit validation closed:** re-executed the first-row USD-to-USD_millions mutation. It is rejected as incompatible source units. Original valid source lexemes remain exact; no value is rescaled silently.
- **F3 hedge compatibility closed:** inspected final `information_gaps.csv`. Its FX_HEDGE entry requires a compatible operating-only multiplier after baseline/lambda/cohort hedge reconciliation, as well as verified target-quarter H. It explicitly forbids certifying the original aggregate T/B merely by supplying H. The known pinned L4 arithmetic `(R-H)*k_operating+H` is distinct from permission to apply an unresolved aggregate scenario ratio.
- **F4 growth units closed:** the ex-FX ADR definition now calls the total YoY value a growth rate in percent and explicitly explains the preserved legacy `percentage_points` source lexeme. It does not redefine source values or treat the total as an additive component contribution.

Independently reran the focused suite: **24 passed in 2.68 seconds, exit 0**. Rechecked the four attacks above, original cell preservation, all status counts and all direct-model blockers. Independently compared `results_v2` with `results_verify_v2`: **8/8 files byte-identical**. The test suite separately performs two fresh subprocess rebuilds and checks output-reuse refusal.

The prior source audit remains valid because the frozen input hashes are unchanged: **nine of nine pinned L4 Git blobs/IDs** were independently verified at `29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`; **16 of 16 local inventory records** matched actual bytes and baseline normalized content, including twelve newline-only differences. No material new source content or eligible fee wave appeared in those scoped snapshots. The filename search and inventory are bounded local observations, not a claim about all external stores or the public web. No collection was started or awaited.

The original research manifest and all 1,187 rows remain incompatible with the pinned L4 JSON adapter. Its root-quote and commit-membership gaps remain explicit upstream responsibilities, not assertions that its current conditional math is economically certified. The same-basis guide audit correctly preserves revenue versus revenue expectations separately from guide versus revenue consensus, without manufacturing observed guide expectations. Existing fixed operational conversion, free-weight FAIL, nested W2, failed NCLH transfer, and unavailable fee identification remain unchanged.

## Exact reviewed identities

The output manifest binds all seven other output files. The frozen input manifest binds the compact interface/inventory/QVS evidence. These identities are from direct reviewer SHA-256 calculations after repair, not merely copied author assertions.

| Artifact | SHA-256 |
|---|---|
| consumption/run.py | `a23279e377e50ba3e65c3c230f89c81d3e28173cc71306fd60da9ce1a80f67ba` |
| consumption/test_consumption.py | `ae821cd20bd2eb3a3e6894b84b0a7cc8f04908d1f3c08e18c009db42119ff521` |
| consumption/README.md | `a085f8631623d20dc0b5017c9bd601863456865d52afc0359c41e511d2b77eb5` |
| consumption/freeze_evidence.py | `f69cb5e7b11aef548ae3894a365d261b36c5cc8eb02cc86d212b2722b412ec87` |
| inputs_v2/manifest.json | `8dbb605edd033daab92a0fb5299b96156940bc1816843376df243dab289c13e1` |
| inputs_v2/l4_interface_snapshot.json | `5b8273e4769be3009a64dbf0244b864b01ff255855abc95f9d781a3af72c5821` |
| inputs_v2/existing_data_inventory.json | `95969a945c2f8b693fa6b6013c07bba0e0be89043a22639232879d93cf6b1ec3` |
| supplemental_path_inventory_v1.json | `973d03ab14924da7d557a3b2dd658e93e2ee07c90b3534f2f2dafed94cb91d23` |
| results_v2/manifest.json | `9e11725fff4a79889d4006931d9c38d9030f2e34a871c14dea3bbc166e033389` |
| results_v2/consumption_matrix.csv | `89d9066af75b091f59b5475dc26336de072215312720993ca6750b85bd684a90` |

Exact focused command, executed from `C:/Users/wille/Desktop/Citadel - ABNB/.worktrees/lane3-full`:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 -m pytest analysis/src/forecast_methods/l3_source_contract_v1/consumption/test_consumption.py -q -p no:cacheprovider
```

The independent closure command imported the final runner by explicit path, deep-copied `read_csv(BUNDLE/'l4_inputs.csv')`, changed exactly one field per attack and called `classify_all`. It then compared every original field in order, all statuses, direct blockers and bytes in the two canonical/verification directories. The command exited 0. It wrote no SC-C or L4 file. This is an accounting/integrity review with zero model refits or new forecasts.

## RESUME

SC-C review is closed for the exact source/input/output hashes above. Lead may bind this note into aggregate source-contract acceptance, verify preservation and reproduce all three packages. L4/quant may read the reviewed evidence/gaps, but any model application needs a separate compatible accepted contract and adoption decision. Future edits to classification logic, evidence snapshots or outputs require new review; they do not inherit this receipt automatically.
