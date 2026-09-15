# L3 source-contract audit — accepted local handoff

Lead · 2026-09-14 · `codex/lane3-full`. The bounded follow-up is complete and independently reviewed. Acceptance covers source precision, accounting definitions, consumption permissions and reproducibility. It does not adopt a new forecast model, FX adjustment or investment stance.

Start with `L3_SC_PRESENTATION_CLAIMS_v1.md` for presentation wording, then the canonical tables below. The original L3 research and bundle remain immutable. All earlier failed tests, missing-data findings, superseded audit outputs and repair notes are preserved.

## Accepted specification and original evidence

Retain the existing **fixed 2/3–1/3 operational seasonal estimation policy**. The five-parameter full-sample descriptive specification is `R_t = lambda_s [w GBV_(t-1) + (1-w) GBV_(t-2)]`, fit to 22 lag-complete quarters from 2021Q1 through 2026Q2. Its shared w is 0.7864784807845561; Q1–Q4 lambdas are 0.1293191114179443, 0.1322423247632188, 0.17302744066064013 and 0.12111558318740108. These are descriptive joint calibration outputs, not production replacements or physical cohort shares.

The matched free/fixed chronological USD RMSE ratios remain **1.16540739036 for W1, n=14, and 1.01551294817 for W2, n=10: promotion FAIL**. W2 is nested in W1. The newly fitted matched fixed OLS comparator is not the inherited operational estimator. Joint uncertainty and year sensitivity remain as originally audited; six calendar-year blocks do not deliver precise structural identification. No historical data, fitted parameter, forecast, registry row or scorer changed in this follow-up. New fitted parameters: **zero**.

Original local bundle commit: `8821961853e4068febbfe2712f9a4e1036c9e629`. Original research source: `7fb6fe0f248d5492b899672b9b70545da62d63ee`. Original bundle manifest SHA-256: `9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970`. Author-emitted status fields in immutable outputs may still describe their original pre-review stage. Final independent review receipts govern audit acceptance; neither those receipts nor legacy status strings authorize production adoption.

## Canonical packages and independent review

All paths below are relative to `data/processed/forecast_methods/l3_source_contract_v1/`. The integrated, consumable reproduction is **`results_v2/`**, also copied into the local supplement's `payload/`.

| Package | Canonical author output | Author | Independent closure | Scope accepted |
|---|---|---|---|---|
| Precision | `precision/results_v2/` | adr_hotel | nclh: `L3_SC_REVIEW_A_v2.md` | 24 quarters, 96 metric cells; source availability, precision and fixed-lambda sensitivity |
| Accounting | `accounting/results_v4/` | cohort_fx | adr_hotel: `L3_SC_REVIEW_B_v1.md` | 38 definitions, nine event clocks, 16 primary facts, 1,080 original FX rows |
| Consumption | `consumption/results_v3/` | nclh | cohort_fx: `L3_SC_REVIEW_C_v2.md` and final `v3.md` | 1,187 losslessly classified rows; committed L4 interface and bounded inventory |
| Presentation claims | New lead claim note | lead | nclh: `L3_SC_REVIEW_CLAIMS_v1.md` | Numerical, denominator and presentation scope |
| Packaging/preservation | New parent code | lead | adr_hotel: `L3_SC_REVIEW_PACK_v1.md` | Committed source membership, compact input binding and original byte preservation |

The root reproduction passed **107 tests: 16 integration/packaging, 31 precision, 33 accounting and 27 consumption**. All three runners exited 0. All **25 canonical package output files** reproduced byte-for-byte (9 precision, 8 accounting, 8 consumption). Parent checks preserve all **33,236 original cells** across the 1,187-row, 28-column source table. Package-level semantic-key and accounting identity checks also passed. The aggregate review acceptance JSON binds exact source, compact input, result and review-file hashes; the packer requires real committed blobs and refuses mismatched or missing evidence.

The first root reproduction, `results_v1/`, remains available. The final version incorporates the reviewed monthly fee requirement clarification and stronger pack input binding. These are metadata/integrity repairs; no financial value, model result or consumption status changed. Additional closed findings covered future/malformed dates, metric units, nonfinite/boolean values, unavailable-source labels and direct admission of an altered source. Initial failure demonstrations and earlier outputs remain in the research commit.

## Source conclusions and materiality

The precision ledger covers GBV, GAAP revenue, aggregate booked units and ADR for all 24 quarters from 2020Q3 through 2026Q2. **92 original-release cells were checked; four original IPO-quarter cells remain unavailable.** The classifications are 67 exact, 18 rounding, four later precision, two definition differences and five unresolved. Finer values or later corroboration were found for 18 GBV quarters. This does not certify every column of the wide panel.

Material unresolved items include the unavailable original IPO body, the frozen approximate IPO date versus the verified November 16 filing date, Q4 2020 revenue precision, the Q2 2025 letter/filing GBV presentation difference, and a Q2 2022 later rounded-history discrepancy. A current original URL is not a historical byte archive. Source publication dates, earliest checked values, exact intraday availability, lambda vintage and audit dates remain distinct. The one-day IPO-date discrepancy precedes every W1 origin; this date observation alone is not a model refit or a certification of unavailable original values.

For the explicitly named current-Q3 illustration, the precise Q1 2026 GBV is 29,187 USDm (already in the original May filing), and Q2 is 27,247 USDm. The weighted input difference from the frozen rounded values is `(2/3)*47 + (1/3)*(-13) = 27` USDm. At the inherited Q3 lambda **0.172548908953**, held fixed, the arithmetic revenue difference is **+4.658820541731 USDm, n=1 illustration**. Parent independently confirmed all 120 projected source cells (96 KPI values plus 24 quarter labels) and repeated this arithmetic with Decimal. Historical revenue-outcome precision and re-estimation effects are intentionally not quantified; no revised forecast series was created.

## Accounting and L4 consumption contract

Booking, cancellation processing, guest payment, contractual currency fixing, host settlement and revenue recognition have distinct clocks. Long stays of at least 28 nights require monthly-contract recognition qualification: initial check-in for the first month and subsequent monthly anniversaries. Backward current-revenue origin shares and forward booking-cohort recognition shares have different denominators. Neither aggregate weights nor unpaid stocks identify the required physical flows.

Reported GBV already includes RNPL and booking-period FX. Cancellation effects must reconcile with amounts already in the baseline. R0 is the fixed-reference diagnostic; B is the matching ordinary booking-FX kernel; T is its conditional retimed alternative. Choose exactly one compatible route—T, T-B or T/B. Do not add equivalent representations, multiply by T/R0, translate reported GBV twice, or add an unmeasured RNPL demand/cancellation effect.

Disclosed historical revenue hedge losses are observed facts: Q2 2026 is 19 USDm and H1 is 34 USDm (H1 includes Q2). Future quarterly H, the operating-only multiplier and the inherited lambda's hedge decomposition remain unresolved. AOCI expectations and notional do not identify H. Merely supplying H does not certify the original aggregate T/B as operating-only. Safe application needs an independently established operating basis and root quote provenance before L4's supplied-field checks and `(R-H) k_operating + H` arithmetic can be used.

The consumption matrix preserves all original data and assigns **576 conditional exhibits, 603 descriptive rows, four comparators and four unavailable rows; zero observed-input or rejected rows**. Zero of these original rows is a directly admissible L4 model adapter. New primary-source facts remain usable as evidence; conditional status permits labeled exhibits only until the exact additional inputs and compatible adoption contract are supplied. Negative research remains descriptive evidence rather than being discarded.

The read-only interface inspection is pinned to actual L4 commit **`29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`**, with nine source blobs independently verified. Its JSON revenue-adapter schema is not the original L3 research CSV schema. Baseline matching, reference exposures, recognized cohort flow, timing, root quote metadata and hedge reconciliation remain explicit gaps. Its loader checks commit syntax and payload hashes; membership in the named Git commit and root quote provenance require upstream verification. No L4 file was edited.

ADR scenario totals already contain their component assumptions and fee K. Hotel indices remain comparators, NCLH transfer remains FAIL, and theta remains unavailable. Each fee month requires its own triplet—September 14/16/18 or October 12/14/16—with its own identification gates; neither monthly coefficient automatically requires or pools the other month. The local inventory is frozen at **2026-09-14T04:28:03.125354+00:00**, scoped to the inspected stores and supplemental filename search. It found no eligible capture wave or materially new local content. A schedule is not an observation; no collector or wait was started.

## Handoff responsibilities and reproduction

L4 receives the accepted fixed policy, presentation claim contract, primary source evidence, accounting definitions and explicit consumption gaps. L4 owns any combined forecast, workbook, valuation, memo and registry application. Revenue consensus is not expected management guidance; a guide-minus-revenue-consensus gap cannot establish guide surprise. The quant task owns new end-to-end, genuine preannouncement and investment robustness testing. Existing L3 historical origins used post-letter information, including the just-printed GBV. Missing physical cohorts, future hedges and unavailable captures remain valid completed audit classifications; they are not silently imputed or grounds to extend this task indefinitely.

From the isolated L3 worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/l3_source_contract_v1/run.py --out data/processed/forecast_methods/l3_source_contract_v1/rebuild_NEW
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/l3_source_contract_v1/preserve.py --compare data/processed/forecast_methods/l3_source_contract_v1/preservation_start.json --out data/processed/forecast_methods/l3_source_contract_v1/preservation_NEW.json
```

All output destinations must be new. Offline runners consume frozen compact facts and snapshots; public retrieval/inventory helpers are not replayed. Exact execution commands, exit codes and stdout are in `results_v2/reproduction.json` and sibling receipts. `supplement_v1/supplement.json` records the actual committed research source; its root `SHA256SUMS.json` covers every consumable file except itself. The original 108 bundle files, 70 source outputs, 34 original review notes and 79 core file identities remain verified against their committed objects and starting bytes. No existing protected tracked file changed.

The research source commit retains synthetic negative fixtures and superseded outputs for audit. They are not consumable financial data. In particular, `precision/independent_B_review_v1/tampered_adapter.csv` is excluded from the supplement payload; only the selected root `results_v2/` tree is copied. Publication is **local only**. No public push, merge, teammate message or L4/quant edit is authorized or performed by this handoff.

## RESUME

Consume the local supplement only with its exact manifest, research commit and final independent review receipts. Preserve the fixed operating conversion policy and every conditional/unavailable qualifier. Future source facts or an application decision should create a new reviewed version of the affected package. No required work remains in this bounded L3 source/accounting/consumption audit; remaining economic inputs belong to later evidence collection or the explicitly separate L4/quant scope.
