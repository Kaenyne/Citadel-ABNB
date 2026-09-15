# L3 lead audit and decision record

2026-09-13 · lead, with independent package authors/reviewers · `codex/lane3-full`.

## Decision

The requested GBV-to-revenue validation is complete analytically: accept the separately named **22-quarter descriptive specification**, and **reject promotion of its freely estimated lag weight**. Preserve the existing fixed 2/3–1/3 operational benchmark. Acceptance of research or code does not adopt any workbook assumption, management guide forecast, valuation, memo, registry entry or investment direction; those decisions remain with L4 and the team.

The model is `R_t = lambda_s × [w GBV_(t−1) + (1−w) GBV_(t−2)]`, in USD millions, with four seasonal through-origin coefficients and one bounded shared weight. Primary loss is revenue-dollar SSE. The full 2021Q1–2026Q2 sample has 22 lag-complete quarters and five fitted parameters. The fixed matched-OLS comparator has four fitted parameters and exactly the same seasonal estimator. Neither calibration silently replaces the inherited K0 estimation policy.

| Requested primary calibration | Estimate |
|---|---:|
| Shared first-lag coefficient w | 0.786478481 |
| Q1 conversion coefficient | 12.931911% |
| Q2 conversion coefficient | 13.224232% |
| Q3 conversion coefficient | 17.302744% |
| Q4 conversion coefficient | 12.111558% |

These are joint reduced-form coefficients. The seasonal values are percentage levels of the weighted lagged-GBV driver, not growth additions or commission take rates. The weight is not a measured booking probability, payment share or fraction of future revenue already booked.

| Matched chronological window | n | Free-w RMSE, $M | Fixed matched-OLS RMSE, $M | Free/fixed | Promotion |
|---|---:|---:|---:|---:|---|
| W1, 2023Q1–2026Q2 | 14 | 63.197127 | 54.227498 | 1.165407 | FAIL |
| W2, 2024Q1–2026Q2 | 10 | 57.392447 | 56.515722 | 1.015513 | FAIL |

Every origin refits after truncating observations to the guide-date letter close. The prior-quarter print is admitted; target revenue and target GBV are excluded. Five frozen registry comparators match their actual separately registered W2 cells. Guide+cushion already observes management's target guide and remains an advantaged post-guide revenue benchmark. No guide-surprise forecasting claim follows. Unchanged K0 abstains in 2023Q1/Q2: its W1 n=12 comparison uses the same available cells on both sides and must not be mixed into the full-n14 chart.

Weight sensitivity is material: excluding 2021 gives 0.538731 (n=18), and 2023 onward gives 0.356963 (n=14). A thousand calendar-year resamples produce a 0.307910–0.857332 percentile sensitivity range, using only six year blocks including partial 2026. Paired chronological ratio ranges are 0.848335–1.525124 in W1 (four blocks) and 0.806881–1.135943 in W2 (three). Both span one. The overlapping windows and few blocks do not establish statistical superiority of either model. Sequential bands cover 7/8 eligible quarters per method; this is a small-sample diagnostic, not a coverage guarantee.

## Other accepted L4 research inputs

| Package | Implementation | Research result and permissible use | New fitted parameters |
|---|---|---|---:|
| Cohort FX v2 | PASS, independently repaired | PARTIAL: auditable exposure-preserving weights, rate tables and 180 conditional scenarios; u, timing and hedge basis remain unidentified; historical W1/W2 n=0/0 | 0 |
| Fee consumer v1 | PASS, independently repaired | PARTIAL: 0/6 scheduled waves available as of September13; theta remains missing. Frozen 2,600-listing frame and residence/overlap/precision gates retained | 0 with current data |
| ADR/hotel audit v1 | PASS | Descriptive reconstruction accepted. ADR-A/B n=10/9 differ from main W1/W2. Target-quarter mix/FX and retrospective choices prohibit PIT-edge claims. Actual hotel nights/revenue/current independent rooms available in 0/13 covered markets | 0 in this audit; inherited choices itemized in package note |
| NCLH transfer v1 | PASS, independently repaired | FAIL: passenger-ticket RMSE ratios 1.376459/3.840746, n=14/10, and all seasonal stability hurdles fail. Comparable revenue guidance/consensus n=0. No ABNB adjustment | 6 independent parameters |

For hotels, **0/13 markets have the requested actual production observations**; missing quantities are not zero outcomes. Cohort FX preserves RNPL inside total exposure and replaces only compatible booking-timing FX. Reported USD GBV already embeds currency translation; no full factor can be added to its revenue kernel. The illustrative -$2.434M scenario is not an expected drag. Unresolved hedge treatment prohibits adding hedge dollars. ADR components explain a single alternative total, and Q4's imposed fee increment is cumulative. These restrictions travel with each adapter row and the accounting notes.

## Independence, failures and repairs

Three subagents owned bounded packages while lead owned fees/integration. FX and NCLH authors cross-reviewed each other's inputs; ADR author reviewed fees; FX author independently reviewed conversion; NCLH author independently attacked bundle provenance and joint integration. Lead independently solved the five-parameter conversion fit from five starts, audited chronology and band algebra, and visually inspected all three charts. Its independent fit receipt is `data/processed/forecast_methods/l3_integration_v1/independent_conversion_fit.json`.

Preserved findings include four FX vintage/coverage holes, fee metadata and archival-frame leakage, NCLH timestamp/numeric/provenance guards, bundle ignored-source and nested-checksum vulnerabilities, conversion K0 abstentions, and inconsistent interval normalization caught before the first completed conversion output. Repairs and original results remain in new versioned files; no negative research finding was erased.

The original joint pytest attempt returned **127 passed / 5 failed**, caused by package-local modules both named `run`. Receipt: `data/processed/forecast_methods/l3_integration_v1/independent_joint_pytest_v1/`. Conversion tests now load uniquely named modules; the integration runner also isolates suites in subprocesses. The same six-suite combined command then returned **132 passed, 3 subtests passed in 19.00 seconds**, exit0. Bundling-only note-copy changes separately passed all 15 bundle tests.

The final end-to-end run passed all six test suites and five offline runners. All **69 generated files** reproduce byte-for-byte: FX11, fee6, ADR17, NCLH11 and conversion24, including all six conversion PNG/SVG charts. The separately issued conversion review acceptance is an audit receipt, not an automatically generated mathematical output. Exact commands/exit codes/timings/stdout are in `data/processed/forecast_methods/l3_integration_v1/reproduction_v1/reproduction.json`; byte comparison is in `reproduction_comparison_v1.json`. The executed command was:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -X utf8 analysis/src/forecast_methods/l3_integration_v1/run.py --out data/processed/forecast_methods/l3_integration_v1/reproduction_v1 --fx-bundle 'C:/Users/wille/Desktop/Citadel - ABNB/FX_ENGINE_SESSION_BUNDLE'
```

Exact successful joint test command from the isolated repository root:

```powershell
python -B -X utf8 -m pytest analysis/src/forecast_methods/cohort_fx_v2/tests analysis/src/forecast_methods/fee_panel_v1/test_fee_panel.py analysis/src/forecast_methods/l3_adr_hotel_v1/test_audit.py analysis/src/forecast_methods/nclh_transfer_v1/test_nclh.py analysis/src/forecast_methods/l3_integration_v1/test_bundle.py analysis/src/forecast_methods/conversion_validation_v1 -q
```

## Preservation and publication controls

The isolated branch starts at verified published L2 commit `1c87628cedbc94ab8a0e8552743c94485ef353b8`, containing published L1 `0761555f8e9131b9c8a575959691c4b77f7729dd`. Original checkout and unrelated untracked files were preserved; the external FX bundle is read-only and never staged. Initial and final byte receipts compare **3,911 base-commit files plus 135 external files: 4,046 unchanged**. New package `.gitattributes` preserve exact bytes in Git without altering existing attributes.

Frozen FORMAT1.0 and FORMAT1.1 executed to new snapshots. All **284 score rows** match the published L2 close exactly, with zero maximum numerical difference and identical keys, flags and missingness. All **155 existing frozen/L0/FORMAT/returns/kernel tests** pass. L3 registered no forecasts and changed no frozen data, scorer, engine or model.

```powershell
python analysis/src/forecast_methods/l3_integration_v1/score_snapshot.py --out outputs/l3_scores_NEW
python analysis/src/forecast_methods/l3_integration_v1/provenance.py --compare data/processed/forecast_methods/l3_integration_v1/start_hashes.json --external-fx 'C:/Users/wille/Desktop/Citadel - ABNB/FX_ENGINE_SESSION_BUNDLE' --out outputs/l3_hashes_NEW.json
python analysis/src/forecast_methods/l3_integration_v1/run.py --out outputs/l3_reproduction_NEW
```

The optional external bundle argument to the last command changes only the R-interface provenance manifest, not the financial outputs. Use the saved environment's `C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe` or an equivalent Python environment. Every output path must be new. Source-worktree hash comparisons are line-ending-specific; immutable handoff hashes cover Git-preserved payload bytes.

The bundle builder refuses uncommitted, ignored or changed research source bytes, copies verified HEAD blobs, normalizes five adapters without discarding original metadata, includes accounting/independent-review notes, and hashes all payload files. The subsequent publication handoff identifies the exact research commit, bundle-containing commit, checksum manifest and draft PR. No automatic merge or teammate outreach occurs.

## RESUME

Use the final immutable bundle and its published commit, not earlier checkpoint directories. Read conversion's final acceptance receipt, specification, independent close, claim ledger and matched charts first. Keep the fixed operational benchmark; treat full22 coefficients as descriptive research. Other L3 adapters are conditional or unavailable exactly as labeled. Future fee captures, measured cohort u/p, dated ADR inputs or comparable issuer guidance should trigger new versioned research only for the affected claim. L4 owns workbook integration, guide composition, valuation, memo and registry decisions.
