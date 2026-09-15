# Independent pack/preservation review — closed

2026-09-14 · reviewer `adr_hotel`; author `lead`. Bounded read-only review of parent `pack.py` and `preserve.py`, focused on actual source paths, immutable original evidence, independent-review binding and manifest completeness. No implementation edits or forecast work by reviewer.

One material binding omission was identified by code inspection and repaired by the author. The initial packer required committed code, outputs and notes but did not require the compact data inputs outside the analysis tree in its acceptance record. Final `runtime_inputs()` supplies the actual ten compact inputs: five precision files, four consumption snapshot/manifest files, and the supplemental path inventory. `build()` now includes this set in required acceptance evidence. Accounting's compact specification is already inside the recursively checked code tree; inherited bundle inputs are independently protected by `preserve.verify()`. Each bound file must exist as a blob in the actual HEAD commit, match current bytes and match its recorded SHA256.

The author also made the packer itself compare the complete live preservation result with the **committed** starting receipt before any output directory is created. Previously that start comparison was available through the preservation CLI and was performed in the workflow, but was not enforced by the pack entry point. I inspected the final call flow and independently ran `preserve.verify()`: its result exactly equals `preservation_start.json`, covering108 original bundle files,70 payload-source blobs,34 research-note source blobs and79 protected core file identities/byte hashes. The preintegration receipt also equals the start receipt. No original preservation difference was observed.

Other reviewed paths are sound for the intended invocation. The original manifest hash, accepted base/research commit objects and source-to-payload byte mappings are verified against real Git objects. Existing protected-file changes are rejected, and the old bundle's exact file inventory is checked. The packer refuses an existing destination before source access; copies selected result/note bytes from committed blobs; and binds the expected three distinct author/reviewer pairs with PASS notes included in the same committed acceptance evidence. Review status is a human-issued receipt, not inferred from a passing test suite. All copied files, acceptance, metadata, README and nested manifests are included in the supplement's root checksum inventory; only that root checksum file excludes itself. Verification compares the exact filename/hash mapping, so unexpected files are detected.

With `--results .../l3_source_contract_v1/results_v2`, selection is limited to that root reproduction tree plus `L3_SC_*.md` notes. The synthetic negative adapter in `precision/independent_B_review_v1/` is outside that results tree and is not copied into the consumable payload. Code/compact facts remain available through the recorded research commit. This review does not claim that the not-yet-built final supplement has already passed its own committed build/verify commands; those remain the lead's final packaging step.

Exact reviewed SHA256:

| File | SHA256 |
|---|---|
|pack.py|b5060296741862bd44d0674ac9f4ba59dfe89f3c8d0e0d6aa7e6c4b2aa86bb4f|
|preserve.py|8380d190abc3463c384fad41a0bf64ad11c5e5cd7d8d4670595319f2c2349b88|
|test_pack.py, read for relevant regressions|ef4037f2e4d80ed9f0c0ee6e00ecf803b4a210feb6505cabc1ddfd27a15ac7a7|

No open material findings remain against these code bytes. Prior passing tests were inspected rather than redundantly rerun; the live preservation equality above was independently executed. The code accepts only a local supplement and does not authorize publication, model adoption or changing the fixed operational policy.

## RESUME

Lead should finish the separately reviewed metadata closure, run the final root reproduction into its new version, commit the complete required inputs/code/results/notes/acceptance record, then execute the packer's committed build and exact-manifest verification. Bind this review note with the other evidence. Preserve all old artifacts and retain the explicit unresolved data/production gaps.
