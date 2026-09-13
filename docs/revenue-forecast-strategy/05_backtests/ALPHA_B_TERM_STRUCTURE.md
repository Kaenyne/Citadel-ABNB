# B′ — Kernel FY term structure and guide revisions

Pre-registration written 2026-09-12 before executing this package's results; sub-B; branch `codex/lane1-full`.

**Underpowered.** The supplied data produce zero eligible FY-revision tests on W1 and W2. Live scenarios can be computed, but do not establish revision predictability or return alpha. The immutable pre-registered pass line, written before execution, is: T predicts the sign of the next FY-guide revision on at least 70% of eligible dates with |T/FY guide midpoint| > 0.5%, and corr(T, revision) > 0.4 on both W1 and W2. A missing denominator or target is ineligible, not a zero revision. The original 60-day FY-consensus revision test is secondary and uses the same thresholds. Return results use executable `open_*` columns only, with the 20/60-day sample counts stated separately.

W1 uses guide targets 2023Q1 through 2026Q2; W2 uses 2024Q1 through 2026Q2. The 2026-08-06 event remains LIVE. Data and consensus must be published strictly before the origin date, including same-day exclusion. The full FY forecast requires all four quarters; no summing an incomplete annual forecast. Kernels come from `kernel_engine_v2`, without re-estimating lambda in B. Live weight sensitivities hold K0's fitted lambda fixed and must be labelled arithmetic sensitivities, not alternate fitted kernels or confidence bounds. Historical nowcast assumptions with no vintage are refused. The observed FY growth buckets are not dollar midpoint guides; converting them into numerical revenue guidance requires an explicit sensitivity separately labelled as such. Letter rounding uses ±0.5 intervals.

## What ran

From the repository root with the project `.venv` interpreter:

```text
python -m pytest analysis/src/forecast_methods/alpha_b/tests -q
python analysis/src/forecast_methods/alpha_b/run.py --as-of 2026-09-12
```

Final tests: **6 passed in 3.52 seconds**, exit 0. CLI: **exit 0**, 10.624 seconds on the first successful final calculation; the latest `summary.json` records the rebuild runtime. Initial implementation checks caught an integer-season API mismatch and an incorrect calendar-row interpretation; both were corrected before this result. The additional calendar test verifies the first origin is 14 February 2023, the last is 7 May 2026, and the August 2026 LIVE event is excluded. No score.py invocation or external data retrieval occurred in B. Source CSV hashes are in `alpha_b/input_hashes.json`.

## Historical results and eligibility

| Measure | W1 | W2 |
|---|---:|---:|
| Guide origins audited | 14 | 10 |
| Complete four-quarter pre-guide kernel FY forecasts | 0 | 0 |
| Origins with strictly earlier, attributed FY revenue consensus | 0 | 0 |
| Eligible FY-guide revision pairs | 0/14 | 0/10 |
| Hit rate; Wilson 95% interval | unavailable, n=0 | unavailable, n=0 |
| Correlation | unavailable, n=0 | unavailable, n=0 |
| 30/60/90-day FY-consensus revision pairs | 0/0/0 | 0/0/0 |
| Kernel FY versus realised FY pairs | 0 | 0 |
| Executable open 20/60-day return pairs | 0/0 | 0/0 |
| No-revision baseline scored pairs | 0 | 0 |
| Last-revision-continues baseline scored pairs | 0 | 0 |

These are **empty tests**, not zero errors, successful no-revision predictions or failed directional forecasts. There is **no baseline exists** for an RMSE ratio on this empty paired sample. W2 is a subset of W1, not independent confirmation. A hypothetical repeated same-ten-quarter comparison would be **vacuous**; B makes no survivor claim.

The FY ledger has 47 rows across many metrics. Its only revenue guidance rows are three FY2026 growth-language buckets: 11%, 14%, 15%, dated 12 February, 7 May and 6 August 2026. The underlying language has open-ended phrases and broad ranges. Their encoded centres are not management-issued dollar midpoint guides, nor measurement intervals of a letter-rounded integer. B does not turn the language into a numerical FY revenue target. Actual letter-rounded quarterly revenue has a ±$0.5M interval; summing four quarters yields a conservative ±$2M annual interval in the audit, with no scored annual forecast pairs.

K0 has no admissible historical RNPL-scenario vintage for the missing GBV quarters. The prior quarter's GBV arrives with the guide at the same date, so a strictly earlier information set must abstain. This data/vintage limitation is separate from the absence of historical FY comparators. The specified `abnb_earnings_reactions.csv` has no `open_*` fields and no 60-day fields. Close returns were not substituted. The ledger's no-revision and last-revision rules consequently have no common eligible outcome sample.

## Live term structure, as of 12 September 2026

All amounts are USD millions. Both horizons depend on K0's RNPL scenario dated 11 September 2026; Q1 also persists the first missing quarter's GBV growth into a second missing quarter. K0 owns every lambda estimate. The coefficients have five prior Q4 and six prior Q1 seasonal observations; the reported intervals are small-sample descriptive scenario distributions with no validated coverage.

| Quarter | Revenue point | Descriptive q10–q90 | Fixed-lambda weight sensitivity, w=0.33…2/3 | Conditional guide midpoint | n lambda / missing GBV quarters |
|---|---:|---:|---:|---:|---:|
| 2026Q4 | 3,214.78 | 3,056.18–3,357.90 | 3,214.78–3,245.18 | 3,158.23 | 5 / 1 |
| 2027Q1 | 3,121.42 | 2,827.30–3,396.50 | 3,121.42–3,245.15 | 3,066.52 | 6 / 2 |

The weight band changes the GBV weights while holding K0's fitted two-thirds-weight coefficient fixed. It is an **arithmetic sensitivity**, not a refitted family of models and not an uncertainty interval. A future refitted-weight study must re-estimate the conversion coefficient within each historical information set; B does not claim that study has been performed.

| Period | Exact vendor label in register | Timestamp | Consensus | Kernel less consensus (%) | n |
|---|---|---|---:|---:|---:|
| 2026Q4 | S&P Global Market Intelligence via StockAnalysis | 2026-09-10 | 3,160 | +1.733 | 1 |
| 2026Q4 | Alpha Vantage (aggregated sell-side panel) | 2026-09-11 | 3,158 | +1.798 | 1 |
| 2026Q4 | Yahoo Finance | 2026-09-11 | 3,160 | +1.733 | 1 |
| 2026Q4 | Zacks | 2026-09-11 | 3,200 | +0.462 | 1 |
| 2027Q1 | unavailable | unavailable | unavailable | unavailable | 0 |
| FY2026 | S&P Global Market Intelligence | 2026-09-03 | 14,160 | +1.053 | 1 |
| FY2026 | S&P Global Market Intelligence via StockAnalysis | 2026-09-10 | 14,160 | +1.053 | 1 |
| FY2026 | Alpha Vantage (aggregated sell-side panel) | 2026-09-11 | 14,155 | +1.089 | 1 |
| FY2026 | Yahoo Finance | 2026-09-11 | 14,160 | +1.053 | 1 |
| FY2026 | Zacks | 2026-09-11 | 14,100 | +1.483 | 1 |

No cited live vintage is older than 30 days; ages are 1–9 days. Vendor rows can share upstream estimates and are not independent observations. The two S&P labels are retained verbatim for provenance, not counted as two independent panels. The $3,158 observation is labelled **Alpha Vantage**, as supplied; it is not relabelled LSEG. No stamped 2027Q1 consensus exists in the input register. FY2026 conditional kernel revenue is **$14,309.14M**: two printed quarters plus K0's Q3 and conditional Q4 forecasts. It is not a validated investment forecast. No live September consensus is used at a historical guide origin.

## Parameters and limitations

B adds zero fitted coefficients. An annual kernel uses up to four seasonal conversion coefficients from K0; the live ledger adds two regression coefficients. The weight and RNPL ramps are fixed sensitivity assumptions, and the second missing GBV growth is persisted, not independently fitted. K0 also estimates uncertainty distributions; this is not a claim that all uncertainty has only six degrees of freedom. Historical predictions use K0's strictly pre-origin selection policy rather than the full-history live selection. Code uses K0's pinned `_panel` and `_ledger_nowcasts` helpers to avoid duplicating its internal logic; these are version-specific implementation dependencies.

An LSEG FY history supplied as admissible, attributed register summaries would provide comparator and 30/60/90-day revision targets and permit stale-vintage checks. **LSEG history alone would not fix missing historical GBV-nowcast vintages.** The latter needs a pre-registered, genuinely point-in-time GBV forecast layer or a separately defined post-letter study. Executable open-price data for 20 and 60 trading days are also needed for the return leg. No licensed export or database was requested or accessed.

## Harness change request and registration status

Reserved method/object: `alpha-b__fy_gap_at_print`. No forecasts are submitted. FORMAT 1.0 lacks an annual FY-gap target and FY period, and its admissible live date is 11 September rather than 12 September. Backdating a scenario that became available on 11 September would violate the strict cutoff. The package writes a schema-only candidate and explicit `registry_status.json`; it does not mislabel an annual gap as quarterly revenue. Parent owns scoring and any future harness decision. The scorer cannot adjudicate this empty annual-gap test.

## One proposed memo sentence

“At strict pre-guide dates, the supplied data yield zero eligible FY-guide-revision tests in W1 (0/14) and W2 (0/10), so the live kernel–consensus gap is a conditional scenario, not validated revision alpha.”

Evidence: `data/processed/forecast_methods/alpha_b/historical_origin_audit.csv`, `window_metrics.csv`, `live_term_structure.csv`, `stamped_live_comparisons.csv`, `summary.json`. This sentence makes a data-sufficiency claim, not an investment-direction claim. Actual token usage is unavailable from this agent runtime; no estimate is presented as measured usage.

## RESUME

Read the recorded preregistration and origin audit first. Keep B's negative feasibility result. When admissible historical FY consensus summaries and dated GBV-nowcast inputs exist, add a new B version, specify the forecast/guide timing exactly, compute genuinely complete annual forecasts, and run the fixed threshold, no-revision and last-revision baselines on identical eligible cells in both windows. Obtain executable open-return fields before the return leg. Preserve this note and source hashes, ask the parent to resolve the annual-target/date harness request, and do not turn today's conditional gap into a historical alpha result.
