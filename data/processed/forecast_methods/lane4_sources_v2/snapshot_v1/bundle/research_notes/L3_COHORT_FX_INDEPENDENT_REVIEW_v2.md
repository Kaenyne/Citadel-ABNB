# L3 cohort FX independent review v2 — findings closed

Reviewer: nclh subagent, independent of FX authorship. Date: 2026-09-13. This closes the four defects preserved in `L3_COHORT_FX_INDEPENDENT_REVIEW_v1.md`. **Reusable implementation accepted for its documented conditional scope; research remains PARTIAL, with no investment adoption.** Canonical reviewed code is `analysis/src/forecast_methods/cohort_fx_v2/`; canonical outputs are `data/processed/forecast_methods/cohort_fx_v2/results_v2/`. The earlier v2 root outputs are a checkpoint before final period-coverage validation.

## Independent closure tests

The reviewer reran each original attack on isolated in-memory data, using the repaired v2 code:

| ID | Repaired behavior |
|---|---|
| FX-R1: quote after source information date | Rejects with `Quote cutoff after source information date` |
| FX-R2: observed cutoff before the target rate period | Rejects with `Observed quote cutoff outside its period` |
| FX-R3: one quote for the fixed annual reference | Rejects with `Incomplete 2025 reference daily coverage` |
| FX-R4: one quote for a completed quarter | Rejects with `Incomplete observed period coverage: 2026Q2/EUR` |

R1/R2 were narrowed to EUR rows so the intended foreign-rate inconsistency, rather than the old v1 USD identity metadata, causes each rejection. All four raise the expected explicit ValueError. The full repaired suite was independently executed:

```powershell
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" -m pytest analysis/src/forecast_methods/cohort_fx_v2/tests -q
```

Exit 0, **46 tests passed in 3.50 seconds** on the review execution. The author's first mixed-date parser regression failure is preserved in its repair history; this closure uses the corrected code.

The implementation now distinguishes date-only source cutoffs from precise instants; quotes cannot postdate their sources. Observed rates must refer to fully elapsed periods and have their last quote inside that period. The annual reference requires at least 240 daily observations, endpoints within seven calendar days of year boundaries, and no internal gap over ten days. Each required observed period/slice requires at least 80% of ordinary weekdays, bounded endpoints and internal gaps. These are explicit conservative coverage proxies, not a complete holiday-calendar audit or transaction-exposure weighting. Unsupported coverage fails instead of silently imputing historical means.

## Economic output preservation

The reviewer compared current canonical v2 outputs with original v1 outputs. All numeric columns and table dimensions match in six major files: `scenario_summary.csv`, `cohort_currency_detail.csv`, `cohort_currency_recognition_weights.csv`, `yoy_bridge.csv`, `l4_adapter.csv` and `rates.csv`. Source/package references and deterministic USD cutoff metadata can change; sensitivity economics do not. The complete 180-scenario conservation/replacement checks and independent reference-rescaling test recorded in v1 remain applicable.

Reviewed SHA256:

| Object | Hash |
|---|---|
| v2 engine.py | `b6cf645f3b265475f5c676e17526bcb3f656950bcc79e7b5d34b4de200256860` |
| v2 run.py | `7e0eb300fedef876a59ff7ea3fa97ba6df5408314d720da939d1da0c17f8d859` |
| canonical l4_adapter.csv | `e16d610554b64d9537ed4b3e7e4a36854b27cbb3e9dbda62f6d9229c7f74443f` |
| canonical output_checksums.csv | `733d20de4a0f767d6f3c82dd90cb0190482765a03d4df9d139b0ee80ca5edebc` |

This is a code/data-integrity approval for the reviewed scope. The recognition-period RNPL FX convention is still a hypothesis; u/p and currency mix remain sensitivities; the kernel's pre-hedge basis remains unresolved; the year-ago construction is retrospective; and no historical forecast edge is supported at W1/W2 n=0. No scalar sensitivity may be adopted automatically as expected ABNB FX, revenue or guide.

## RESUME

Lead may bundle only the canonical v2/results_v2 adapter and payload, retaining v1 findings, v2 closure and the accounting/treatment fields. L4 must apply at most one compatible replacement route and reconcile the exact inherited baseline's embedded FX/hedges before adopting any scenario. Future reference-period or data-source changes must meet the coverage and chronology gates or use a new explicitly labelled specification.
