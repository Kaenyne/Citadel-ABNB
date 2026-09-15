# SC-C consumption and information-gap audit

2026-09-14 UTC. Preregistered in L3_SC_C_PREREG_v1.md. The 1,187 frozen bundle rows are now classified without changing any of their 33,236 original cells. No forecast, coefficient, bounds, source vintage, registry, L4 model or investment decision changed. The fixed 2/3–1/3 operational policy remains; the free-weight candidate's promotion FAIL remains and W2 is nested in W1.

Canonical output: `data/processed/forecast_methods/l3_source_contract_v1/consumption/results_v1/`. The main consumption contract is `consumption_matrix.csv`; exact missing inputs are in `information_gaps.csv`. Original numeric lexemes, missing cells, 28 source columns and their order are preserved with CSV string reads/writes. Appended definitions explain each metric, bounds, parent baseline, dependency, permitted current use and model-application blocker. Failed research is retained as evidence, so no valid row is discarded as rejected.

| Consumption status | Rows | Meaning |
|---|---:|---|
| usable_as_observed_input | 0 | No original adapter row is an observed ABNB model input. |
| usable_as_conditional_scenario | 576 | 540 FX replacement representations plus 36 ADR scenarios; labelled existing exhibits only until exact dependencies and adoption are resolved. |
| descriptive_only | 603 | 540 FX identities/reference diagnostics, 44 ADR components/GBV identities, 12 NCLH failed-test diagnostics, 7 conversion calibration/validation rows. |
| comparator_only | 4 | Complete-quarter US hotel/lodging indices; observed category comparators, not observed ABNB pricing. |
| unavailable | 4 | Two fee theta estimates and two incomplete hotel-quarter observations; all original values remain blank. |
| rejected | 0 | Negative research outcomes remain valid descriptive evidence. |

Direct application to the existing L4 machine interface is blocked for all 1,187 rows. That statement is distinct from permission to quote a labelled scenario or diagnostic. No new empirical pass/fail test or fitted parameter was introduced (parameter count 0; no new W1/W2 observation).

## Committed L4 interface

The audit read actual Git blobs at L4 HEAD `29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`, using shared Git objects from the L3 worktree. All nine selected source files have recorded Git object IDs, SHA-256 and byte counts, and their L4 working copies match committed bytes. No uncommitted interface was trusted. Compact exact contract code, its four original helper functions and relevant output rows are frozen under `inputs_v2`, so the offline runner does not require the L4 worktree or Git.

The committed `lane4_revenue_v1/l3_contract.py` loader accepts JSON files with role `revenue_adapter`, a `commit` field and immutable hashes. The existing L3 research bundle has `research_source_commit` and a CSV adapter instead. Its manifest is rejected by that loader; each of the 1,187 research rows is rejected by `apply_row` as incomplete. L4 requires `revenue_timing_multiplier`, an exact baseline scenario/revenue, both lagged reference exposures reconstructing USD GBV, conserved recognition allocations and explicit hedge reconciliation. Renaming fields alone would not satisfy the economic contract.

The actual contract correctly applies `(R-h) × T/B + h`, preserves reconciled hedge dollars, checks the two lag identities, rejects allocation weights that do not sum to one and prevents a second FX application. A synthetic $100m baseline with $10m hedge and a 1.05 multiplier produces $104.5m, not $105m. Missing hedge, mismatched baseline and nonconserving allocation counterexamples reject. These are implementation fixtures, not ABNB estimates.

Two gaps remain explicitly upstream responsibilities. The loader checks commit syntax and payload hashes but does not verify that payload bytes belong to the named Git commit; a synthetic `f` repeated 40 times is accepted. L4's own README states this limitation. The contract checks row dates, rate direction and supplied ratios but does not require underlying FX quote periods, cutoffs, source links, averaging coverage or reference-rate provenance. A valid synthetic row with no root quote metadata is accepted, and contradictory extra quote metadata is ignored. A future rate may be an explicit scenario, but cannot become observed merely through a row date. A separate verified parent contract must preserve booking/reference/recognition quote provenance and timing. The existing L3 rate engine's stronger checks remain relevant; this audit does not modify L4 code.

FX inputs still need a precisely matched L4 baseline, denominators on surviving recognized-revenue cohorts, u/p/currency assumptions and verified target-quarter hedge contribution. Historical disclosed hedge losses do not automatically identify a forward scenario hedge. Levels in USD require an explicit USDm bridge. Replacement T, incremental T−B and multiplier T/B are mutually exclusive forms of one adjustment. T/R0 and the ordinary baseline B are never extra revenue overlays. ADR requires the selected ex-FX/reported route, prior-year base, nights and lag mapping, and no duplicate K/FX/component addition. None of those requirements is solved by the number of scenario rows.

## Same-basis expectations

The frozen L4 comparison contains conditional Q4 revenue **3179.3436542864 USDm**, implied guide **3123.41911517339 USDm**, and captured Yahoo Finance/LSEG-family revenue consensus **3161.02149 USDm**, observed **2026-09-13 15:20 UTC**. Existing guide minus revenue consensus is **−37.602374826612 USDm**. Revenue minus revenue consensus is **+18.3221642864 USDm**. These quantities are preserved and labelled in `guide_basis_audit.csv`; no new expectation or guide forecast was created. The negative mixed-object gap is not a measured surprise against expectations for management's guide. Explicit dated guide expectations or an independently justified conversion model remain unavailable requirements.

The two original-workspace QVS notes were read as explanatory context and hashed separately. They are not committed in the original workspace starting HEAD and are not treated as authoritative interface code. Their comparison claim was verified against the actual committed L4 values above.

## Bounded source availability

The canonical inventory ran at **2026-09-14 04:28:03.125354 UTC** (**00:28:03 New York**). It checked `data/processed/forecast_methods/fee_panels` and local `data/raw/regulatory/quantification/abnb_*` files in both the original workspace and L3 worktree: 16 file instances, zero actual wave CSVs and zero material new content. Twelve raw-byte differences against baseline Git objects were entirely CRLF/LF normalization; four were byte-identical. The dryrun is not a production wave. The first unqualified byte inventory is retained as `inputs_v1`; `inputs_v2` adds the explicit content comparison and is canonical.

A separate **04:35:15.823023 UTC** filename-only `rg --files --hidden` scan enumerated 2,297 nonignored data paths and 203 nonignored research paths in the original workspace. Matching names located the same fee directory, the existing Q2 2026 10-Q and the already captured September 13 consensus estimate. No alternative fee capture location was found among those matches. The exact command, roots and matches are frozen in `supplemental_path_inventory_v1.json`. Ignored or other external stores and the entire public web are outside this bounded absence claim. No collector was launched or awaited, and no primary hotel/NCLH test was reopened. Existing filing precision remains SC-A's separate scope; fee and incomplete hotel status stay unavailable.

## Verification and reproduction

The focused suite passes **18 tests**. It covers all-cell conservation, exact counts, missing values, duplicate/dropped/unknown rows, false promotion, nonfinite values, provenance, treatment changes, units, scenario dependencies, negative results, immutable output refusal, byte-identical reproduction, and synthetic attacks on actual committed L4 functions. Initial focused 17-test and subsequent 18-test runs passed; no test failure was discarded. The one inventory enhancement separates newline-only bytes from new information and retains both snapshots.

Exact commands from the isolated L3 repository root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 -B -m pytest analysis/src/forecast_methods/l3_source_contract_v1/consumption/test_consumption.py -q
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 -B analysis/src/forecast_methods/l3_source_contract_v1/consumption/run.py --out data/processed/forecast_methods/l3_source_contract_v1/consumption/results_v1
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -X utf8 -B analysis/src/forecast_methods/l3_source_contract_v1/consumption/run.py --out data/processed/forecast_methods/l3_source_contract_v1/consumption/results_verify_v1
```

All exit 0. All **8 output files** rebuild byte-identically. Use fresh directory names for a new run. Commands, stdout hashes, output hashes and code hashes are retained in `verification_v1/receipt.json`. No frozen harness suite was rerun, no registry/scorer changed, and no raw filing body or licensed material was copied into this package.

## RESUME

Reviewer B should inspect schema conservation and accounting/interface interpretations independently. Parent may integrate this supplement with SC-A precision and SC-B accounting evidence while leaving the original bundle untouched. Preserve blocked direct application, same-basis guide expectations, exact reference-rate and hedge requirements, and the fixed operational policy. Any later L4 integration is a separately authorized version with actual source membership and baseline reconciliation; no broad merge, publication, teammate outreach or market-data refresh occurred here.
