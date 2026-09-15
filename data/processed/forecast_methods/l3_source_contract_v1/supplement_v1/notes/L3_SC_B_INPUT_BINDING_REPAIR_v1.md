# SC-B — independent-review input binding repair

cohort_fx · 2026-09-14 · finding from independent reviewer SC-A (adr_hotel). Prior outputs through v3 remain intact; next canonical output is results_v4.

The main runner validates the frozen adapter SHA-256, but the direct conditional-use gate recreated canonical rows from the source without checking that hash. If the underlying source were modified and then freshly enriched, its changed row could be accepted as canonical. Existing frozen outputs and the main runner were protected; the callable admission path was not equally protected.

Repair uses one `load_bound_rows()` loader for both the runner and the conditional gate, verifying the source against the in-package expected SHA before reading it. `read_rows()` resolves SOURCE at call time. A regression test will use a temporary copy, change an actual conditional row's value, re-enrich it and attempt admission; the source-hash gate must reject it. The original frozen adapter is never mutated. No numerical or economic assumption changes.

The source manifest also gains `local_hash_path`, identifying the exact cached bytes previously hashed. SEC_K25 uses `data/raw/regulatory/quantification/abnb_2025_10k.json`, a distributor PDF-text extraction; SEC_Q226 uses `data/raw/regulatory/quantification/abnb_2026q2_10q.html`. Both paths are relative to the isolated L3 root. Other paths identify their committed processed artifact or original-workspace QVS note. These are audit anchors, not new runtime dependencies or claims of fresh SEC-byte retrieval.

## RESUME

Run the adversarial test and full focused suite, freeze/reproduce new results_v4, and send SC-A exact paths/hashes for independent closure. Direct L4 application and all unresolved accounting inputs remain unchanged.
