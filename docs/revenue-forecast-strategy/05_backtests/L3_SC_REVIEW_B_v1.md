# Independent SC-B accounting contract review — closed

2026-09-14. Reviewer `adr_hotel` (SC-A author); reviewed author `cohort_fx`. This is independent review of the accounting package, not self-approval. Accepted canonical outputs: `data/processed/forecast_methods/l3_source_contract_v1/accounting/results_v4`. Earlier V2/V3 outputs and correction notes remain preserved. No implementation edits by reviewer.

**Closed with one repaired integrity finding.** Economic definitions and numerical source preservation pass. Conditional arithmetic routes are accepted only as exhibits on the identical inherited baseline; direct L4/production use remains unavailable. No new physical-share identification, FX fixing rule, quarterly hedge forecast, model refit or operating forecast is approved.

Finding B1, medium severity: by code inspection, the initial conditional-use validator rebuilt its supposedly immutable canonical row from `enrich_rows(read_rows())` without validating the adapter file's registered SHA256. The full runner performed that check, but the direct admission API did not. Thus changing the underlying adapter and freshly enriching it could bypass the intended immutable binding. This was a code-path finding; the author repaired it before the reviewer's first executable attack, so no pre-repair runtime failure is claimed. The repaired shared bound loader checks the exact input hash in both paths. A copied adapter with a conditional monetary value increased by $1m, then freshly enriched and submitted, is rejected with `frozen bundle FX input changed`. The frozen original file was untouched. The attack receipt is `precision/independent_B_review_v1/receipt.json`; its synthetic `tampered_adapter.csv` is a negative test fixture, never a source or consumable output. The author's regression tests this same failure mode.

Provenance clarification B2: source manifests initially supplied byte hashes without the local byte-source path. V4 now includes `local_hash_path`; I independently recomputed all seven hashes and matched them. The annual-file hash is of the existing distributor PDF-text JSON, not primary SEC HTML; this distinction is explicit. The Q2 hash covers existing cached SEC HTML. These are local-byte anchors and current primary-text checks, not proof of a historical byte archive or precise original release time. Original workspace QVS notes are read-only supporting inputs and not runtime fetch dependencies.

The author's earlier hedge-language correction is accepted and remains explicit. Without identifying embedded hedge component H, multiplying B by T/B cannot prove unchanged hedge dollars; `B*k` and `(B-H)*k+H` differ by `H*(k-1)`. V4 permits only an aggregate conditional exhibit and rejects both certified prehedge/afterhedge claims and the old “hold embedded unchanged” wording. Absence of a new overlay does not resolve inherited H.

Independent checks:

| Check | Evidence |
|---|---|
|Frozen source preservation|All1,080 rows and all17 original fields,18,360 cells, match exactly as strings|
|Mutually exclusive arithmetic|180 scenario groups independently checked with Decimal; `T`, `B+(T-B)`, `B*(T/B)` agree within printed rounding|
|Maximum printed monetary identity difference|$0.0089|
|Maximum printed ratio identity difference|6.40e-12|
|Direct L4 admissions|0/1,080|
|Routes|540 conditional financial rows;540 diagnostic rows; all direct adoption unavailable|
|Local source hashes|7/7 recomputed and matched|
|Canonical output hashes|7/7 manifest members recomputed and matched|
|Author integrity suite independently rerun|33 passed in0.71s|

I reviewed all38 definitions, nine event clocks and16 compact facts. The contract distinguishes fixed lag coefficients from arithmetic contributions and unavailable actual backward/forward cohort shares. The reported contribution `2*G1/(2*G1+G2)` generally differs from2/3; forward and backward physical shares have distinct denominators. RNPL u uses recognized reference-revenue flow, not booked GBV or unpaid backlog. Cancellation processing, cash receipt, host settlement, recognition and contractual currency fixing remain distinct. Recognition cannot establish a currency-fixing rule. Net GBV and cancellation overlap prevents an automatic second haircut. T/R0 is diagnostic, while T/B is the compatible replacement multiplier on B. Model/model YoY differences are separate from management constant-currency growth disclosures and from level multipliers. Guide expectations are not silently replaced by revenue consensus.

Primary source spot checks independently confirmed the long-stay exception: stays of at least28 nights recognize the first month at check-in and later months at monthly anniversaries, rather than all lifetime fees on the first day. [2025 10-K, Note2](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm). The disclosed Q2/H1 revenue hedge losses are19m/34m, signed−19m/−34m in the contract; H1 includes Q2 and must not be summed with it. Expected next-twelve-month losses26m and designated notional3.4B are different objects and cannot supply a quarter's hedge release. [Q2 2026 10-Q, Note6](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm). The source does not identify transaction-level fixing or the recognized RNPL fee/currency matrix; those remain unavailable.

Exact suite command, from lane3-full:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -m pytest analysis/src/forecast_methods/l3_source_contract_v1/accounting/test_accounting.py -q -p no:cacheprovider
```

Additional independent numeric/hash receipt: `data/processed/forecast_methods/l3_source_contract_v1/precision/independent_B_review_v1/closure_receipt.json`. It records exact preserved cell counts, independently calculated identity residuals, all source hash results and reviewed anchors. The lead's full integration separately reran every child successfully; this review does not relabel that as a reviewer-authored rerun.

Exact reviewed SHA256:

| Artifact | SHA256 |
|---|---|
|accounting/run.py|a66257d5484b178e9c8cecfba391391dc3b6bf611014cf1b29d5fbd6db0d6e79|
|accounting/source_contract.json|2b4bfa3547cf53d13e4055c0a894c312007ea6c1f59b604b4ff643f22b1b21db|
|results_v4/SHA256SUMS.json|d03ca7a1f56c6f2db3af78ec5696a9492a9d8e396b3e0244cf27e49c0fd4bede|
|Frozen original FX adapter|e16d610554b64d9537ed4b3e7e4a36854b27cbb3e9dbda62f6d9229c7f74443f|

No open material review findings remain against these bytes. Acceptance covers the source/denominator contract and rejection gates; it does not close the substantive unavailable data needs.

## RESUME

Lead may integrate SC-B results_v4 with SC-A precision results_v2 and SC-C consumption after their separate closures. Carry forward unavailable actual cohort/flow/fixing/hedge bridges, all source-vintage qualifiers and the strict identical-baseline/exclusivity gates. Exclude the synthetic tampered-adapter fixture from the consumable L4 supplement. Preserve prior outputs and original L3 research conclusions; no production adoption or forecast refit follows from this review.
