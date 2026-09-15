# WP-Q1 — source identity, availability and precision

2026-09-14 · source_auditor (wave 1 A) · branch `codex/quant-thesis-validation-v1` · exclusive new source_audit_v1 directories · independent reviewer: lead and wave 3 G.

## Verdict

Evidence identity **PASS**; source availability and precision **PARTIAL with explicit limitations**. All 108 immutable bundle files verify against the exact supplied manifest hash. The frozen series can support a qualified reconstruction of information available before later historical origins; it is not an archive of original unrevised numerical vintages. Original shareholder-letter bytes and exact SEC acceptance clocks are absent from the committed letter store. No source-contract supplement exists in the frozen baseline. The new audit preserves those limits and does not promote recorded verification flags into independent source verification.

## Authoritative inputs and exact commands

Worktree root: `C:/Users/wille/Desktop/Citadel - ABNB/.worktrees/quant-thesis-validation-v1`.

L3 commit `8821961853e4068febbfe2712f9a4e1036c9e629`; research source commit `7fb6fe0f248d5492b899672b9b70545da62d63ee`; one explicit L4 operating-coefficient input from commit `29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`. Each commit exists as a local commit object. No moving L3/L4 worktree was read. The bundle manifest hash is `9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970`.

```powershell
& "C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe" -B -X utf8 analysis/src/forecast_methods/quant_thesis_validation_v1/source_audit_v1/run.py --out data/processed/forecast_methods/quant_thesis_validation_v1/source_audit_v1/results_v3
```

Canonical run exit 0, approximately 10 seconds. Reproduction must use a new output directory. Versions 1 and 2 exited 0 and remain preserved. One intentional rerun into results_v2 raised FileExistsError before writing (exit 1), confirming overwrite refusal. A first attempt to add L4's exact lambda used `target_quarter` rather than the actual `quarter` column; it failed before output creation. The field was corrected and version 3 completed. No empirical result was discarded or tuned. Fitted parameter count: **0**.

## Results and source contracts

| Check or object | n | Result and interpretation |
|---|---:|---|
| Bundle file hash checks | 108 | 108 Git and 108 local files match supplied hashes exactly |
| Direct input identities | 17 files | Exact Git SHA-256 plus local SHA-256 recorded; 14 L3 text files differ only by checkout CRLF. These are explicitly reconciled, not silently called byte-identical |
| Accepted conversion-source identities | 10 files | Match accepted source bytes directly or their documented CRLF rendering |
| Frozen KPI panel | 24 quarters | 2020Q3–2026Q2; 22 lag-complete; no sample extension |
| Core KPI source cells | 120 | Revenue, GBV, nights, revenue FX and ADR FX. Status, units, period, source, availability and precision limits exported |
| Numeric guide ranges / guide cells | 20 / 60 | Targets 2021Q4–2026Q3; 19 realized revenue outcomes by frozen snapshot. Every retained quote independently parses to both recorded endpoints |
| Missing core KPI cells | 10 | Early revenue/ADR FX inputs. Missingness exported, never changed to zero |
| Maximum evaluation targets | 14 W1 / 10 W2 | Nested maximum coverage; a new origin can have fewer usable forecasts |
| Original raw letter files in baseline path | 0 | Metadata, 23 SEC source URLs and excerpts are retained. Raw bytes are not independently recoverable from this snapshot |
| Complete archived unprinted-GBV forecasts at target-start minus 18 days | 0 identified | No complete comparable series in inspected baseline. Uniform frozen-rule reconstruction is appropriate; do not select favorable individual archive values |

Canonical artifacts are under `data/processed/forecast_methods/quant_thesis_validation_v1/source_audit_v1/results_v3/`: `input_manifest.csv`, `bundle_checks.csv`, `accepted_source_reconciliation.csv`, `observation_availability.csv`, `material_input_ledger.csv`, `unavailable_cells.csv`, `source_precision_sensitivity.csv`, and `summary.json`.

All 23 guidance-event timestamps are disclosed webcast-start proxies for certainly-public-by time; they are explicitly not exact SEC acceptance times. Conservative use of the audited source fields begins after the stated release date's end of day. An intraday strategy needs independently verified release clocks. The harness calendar's `2020Q3` date of 2020-11-15 is explicitly approximate. Its original build sources 2020Q3 GBV, nights and revenue from comparative tables in the 2021Q3 letter. The new availability map uses **2021-11-04 as a conservative date justified by that cited source**, not as a claim about the first public disclosure of 2020Q3. This correction does not change membership at W1 preannouncement origins beginning in late 2022. Frozen calendar and input files remain unchanged.

The frozen early revenue levels have finer precision than some retained letter excerpts, for example 2020Q4 859.1 versus the retained integer letter excerpt 859.0. Their exact original precision vintages remain unresolved. Later disclosure and round-off must not be described as evidence of restatements. For W1/W2 reconstruction this source limitation remains disclosed even where all relevant dates are comfortably in the past.

The 2023Q4 letter is dated February 13, 2024; its 10-K is dated February 16. Filing precision cannot enter a February 13 decision through that later source. Q2 2026's 10-Q and letter share August 6 as a date; no assertion is made about their intraday order.

## Source precision and economic sensitivity

The [SEC Q2 2026 filing, Key Business Metrics](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm) reports Q2 GBV 27,247 USDm and H1 GBV 56,434 USDm. Subtraction implies Q1 29,187 USDm. The [Q2 shareholder letter](https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm) reports Q2 GBV 27.2 USDbn and nights/seats 148.3m. These two primary sources were separately read through the web tool on September 14; offline reconstruction verifies the committed filing HTML and its hash. The cited H1-minus-Q2 Q1 calculation is an August 6 vintage and cannot be backfilled to May 7 from this source.

| Calculation holding w=2/3 and exact inherited Q3 lambda fixed | n | USDm effect |
|---|---:|---:|
| Q2 precise GBV minus frozen 27,200 | 1 | +47 |
| Q1 H1-minus-Q2 GBV minus frozen 29,200 | 2 filing cells | −13 |
| Weighted lagged-GBV base change | 2 quarters | +27 |
| Revenue change at exact L4 Q3 lambda 17.2548908953131% | 2 quarters | **+4.658820542** |
| Joint worst-case input display envelope, each GBV ±50m | 2 quarters | **±8.627445448** |

The coefficient is read directly from L4's immutable `lane4_revenue_v1/snapshot_v1/forecast.csv`; it is not estimated here. Its availability is the September 13 research snapshot, while the precise filing inputs were available by August 6. The envelope is a conditional deterministic input-precision range holding lambda fixed, **not an SD, confidence interval, full forecast-error interval, or refit result**. Version 1/2's +4.6548m and ±8.620m used the rounded 17.24% illustrative coefficient and are superseded solely for this numerical detail.

Guidance source display precision is recorded exactly: 19 ranges have endpoints in two-decimal billions (10m display quantum); Q3 2023 uses one decimal (100m). These are nominal management choices, not empirical measurement noise around an unobserved exact target. Use raw midpoint error and, when required, the project's midpoint ±0.5 USDm interval scoring convention, clearly labeled as a convention. Do not infer midpoint ±5m/±50m bands or count the entire guide range as the midpoint target interval.

## Limits and permitted use

The ledger covers core forecast and source-precision inputs, not all 119 fields of the original panel or the separate economic bridge's L4 inputs. Later whole-chain agents retain responsibility for their exact external input identities. Historical comparative source documents, overwritten source webpages, current XBRL vintages and unpublished original source files cannot be promoted to contemporaneously archived forecasts. The current reduced-form reconstruction can be decision-useful with these qualifications; it does not become a prospective untouched holdout or exact original-vintage dataset.

No protected file was edited, no scorer was run and no forecast was registered. All writes are within this task's exclusive new source_audit_v1 directories. The parent performs the global protected-hash comparison. The review gate is still pending independent reproduction by wave 3 G.

## RESUME

Consume results_v3, retaining its Git identities and date/precision labels; parent should freeze the origin protocol using uniformly reconstructed unprinted GBV, raw guide-midpoint errors plus the administrative interval convention, and the conservative availability map. Wave 3 G should rerun this command into a fresh output path, compare all eight generated artifacts, inspect the 2020Q3 comparative-date limit and verify that no later filing enters an earlier origin. Source auditor now rotates to implement the parent's hash-frozen protocol; no further source collection is required to finish this bounded question.
