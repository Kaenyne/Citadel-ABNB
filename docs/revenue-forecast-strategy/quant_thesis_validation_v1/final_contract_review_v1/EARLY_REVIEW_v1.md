# Wave3 I — early final-contract review

2026-09-14 · reviewer `/root/test_designer` · new review directories only. This reviewer designed the prospective protocol and authored the economic bridge; worker A implemented the prospective experiment and worker C independently reproduces it. **This review does not independently sign off the reviewer's own economic calculations.** Worker A owns that independent review. Parent adjudicates final artifacts.

Early result: no blocking source, information-date, model-promotion or registry issue identified. Final artifact signoff remains pending exact files and independent review receipts. The finding about outcome-loading language must be resolved in final wording, and the prospective package still needed its README when inspected.

## Independently checked evidence

Executed without importing the reviewed implementation:

```powershell
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B analysis/src/forecast_methods/quant_thesis_validation_v1/final_contract_review_v1/early_contract_checks.py
```

Exit0, shell wall time2.831s. Receipt and complete field checks are in `data/processed/forecast_methods/quant_thesis_validation_v1/final_contract_review_v1/early_checks_v1/`.

| Contract check | n | Result |
|---|---:|---|
| Original protected-file hashes |4,444|All match frozen manifest|
| Immutable external evidence hashes |36|All match;34 committed L4 files and2 user-specified QVS notes|
| Source and accounting independent-review bindings |21|All still match reviewed versions|
| Forecast-input and calibration-date fields |829|All strictly precede their forecast information date|
| Forecast-method rows with guide issuance after origin |63|All satisfy target availability; future scheduled guide row explicitly labeled an assumption|
| Source-audit v2/v3 availability map |2 files|Byte-identical; frozen prospective v2 reference remains compatible with canonical v3 audit|
| Target interval construction |All scored guide rows|Administrative midpoint +/-0.5USDm, never full guide-range zero loss|
| Protected registry/harness/model Git status |Named protected paths|No modified or new registry/scorer/model file reported|

Counts above are technical checks, not independent historical observations or regimes. The contract preserves12 matched W1 targets and10 W2 targets, with W2 nested; candidate abstentions in2023Q1/Q2 remain explicit. The new preregistered forecasting verdict remains **FAIL**, including the weaker result against direct guide-growth persistence in W2. No favorable comparator, loss or sample replaces that verdict.

Manual source inspection confirms fixed quarter-start-minus18-day anchors; exact K0 `pit_lambda(...,variant=None)` policy; one reconstructed latest-observed-GBV-growth rule; minimum3 realized cushion observations; explicit first-issued management guide target; direct-guide growth and revenue-naive/common-cushion baselines; matched intersections; raw plus interval-fair errors; fixed-forecast year deletion; eight-term error/covariance reconciliation; and chronological same-method guide-error calibration. No free-weight refit, fabricated archived GBV, post-letter input substitution, current-price assertion or shared registration appeared.

The cohort/FX/RNPL and expectation reviews preserve the difference between backward revenue-origin shares, forward booking allocation and unpaid stock measures. They retain historical hedge disclosures without inventing Q4 hedge allocation, reject applying gross FX twice to reported-USD GBV, and label revenue consensus versus hypothetical guide expectations. The frozen LSEG timestamp, date-only S&P/Zacks precision and separate vendor families are retained. The draft presentation foundations preserve failed revision/trading evidence and formal human adoption boundaries.

## Findings to close before final signoff

1. **Receipt wording, not a forecast-number defect:** `prospective_v1/results_v1/evaluation/evaluation_receipt.json` says “outcomes loaded after forecast freeze.” Actual `load_sources()` reads the full frozen panel and guide ledger first; the prediction function filters them, and the outcome **scoring join** follows the point-forecast hash freeze. Future-outcome poisoning tests demonstrate functional independence. Final wording must say “point forecasts frozen before scoring/outcome join,” never suggest blind process-level loading or an untouched holdout. Do not modify the old receipt; add the clarification to final reviewed artifacts.
2. **Package interface pending at inspection:** prospective `run.py` and tests exist, but its README was not yet present. Add a new README with exact commands, immutable output suffixes, staging, dependencies and failed-attempt boundaries before G8 closes.
3. **Independent review pending:** worker C's final prospective reproduction receipt, worker A's economic/presentation receipt and exact final summary/PDF/claim ledger/handoff/interface must be supplied. The present reviewer cannot certify their own economics merely by reviewing its final labels. Parent's known failed bootstrap file is preserved as archival text and must remain excluded from runnable interface claims.

## Gate status at this checkpoint

| Gate | Research status | Claim limit or pending condition |
|---|---|---|
|G1 evidence identity|PASS with explicit source limits|Original unrevised shareholder-letter bytes and some early precision unavailable; no false vintage recovery|
|G2 information set|PASS for metadata/implementation contract|Historical reconstruction; exact functional numerical reproduction belongs to C|
|G3 assessment|PASS for locked protocol and retained failure|Forecast promotion FAIL; no automatic superiority claim|
|G4 identification|PASS for source/claim contract|Reduced-form coefficients and scenario ranges remain nonstructural; no probability upgrade|
|G5 expectations|PASS under independently bound review|Explicit management-guide expectations unavailable; comparisons remain same-basis/hypothetical|
|G6 economic significance|PENDING independent reviewer A|This reviewer authored E and abstains from own numerical signoff|
|G7 independent review|PENDING final receipts|Require A economic/presentation and C prospective reproduction|
|G8 delivery|PENDING exact final artifacts|Final hashes, README, self-contained summary and reviewed images/PDF still required|

## RESUME
Parent supplies exact final artifact paths and completed independent receipts. Reviewer I checks final wording against evidence, binds the delivered versions by SHA-256, records closed findings and remaining claim limitations, and issues a new final review receipt. This early note is not final acceptance or permission to mark the task complete.
