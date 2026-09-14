# C2 — Macro and arrivals pulls

Codex sub_c2 · 2026-09-13 · codex/lane2-full · new package macro_pulls · about 20 minutes

## Verdict

**PARTIAL infrastructure; FAIL against the full pre-registered pass line.** The reviewed capture contains 35,124 rows from the requested source families, but only 124 observation rows have verified publication dates; unknown dates remain null. The corrected NTTO total-arrivals full-quarter series produces nights-level RMSE ratios to the frozen naive of **1.0324 on W1 (n=14)** and **0.6771 on W2 (n=10)**. It does not reproduce a 0.72–0.74 level ratio or survive both windows. The old 0.7199–0.7429 W2 figures reproduce only under the legacy growth-rate definition. All historical PIT admissions are zero because revised downloads and current-quarter features have no certified guide-date vintages. **No forecast registered; neither scorer run.**

## Pre-registered pass line

Written 2026-09-13T17:13:04Z, before any pipeline execution:

Every series has a documented URL, cadence and publication lag in the README and a `published_on` column; the NTTO series, run through the
frozen harness baselines on `nights_m`, reproduces the existing survivor ratio (0.72–0.74× to naive on the same cells) — if it does not, publish
the ratio you get and why. No registration is required unless a series becomes a forecast object.

## What ran

Canonical reviewed output: `data/processed/forecast_methods/macro_pulls/review_capture/`; its `manifest.json` is the source/URL/UTC timestamp/hash ledger. The root capture is retained intact as the initial failure receipt; `final_capture/` retains the corrected DATATUR/BLS pull. Every rerun writes a new directory.

Exact commands, run from repository root (activate `.venv` to use `python`; this host used the explicit executable):

```powershell
& ".venv/Scripts/python.exe" "analysis/src/forecast_methods/macro_pulls/run.py"
& ".venv/Scripts/python.exe" "analysis/src/forecast_methods/macro_pulls/run.py" --offline-from "data/processed/forecast_methods/macro_pulls" --refresh-series "datatur,bls_cpi_lodging" --output-dir "data/processed/forecast_methods/macro_pulls/final_capture"
& ".venv/Scripts/python.exe" "analysis/src/forecast_methods/macro_pulls/run.py" --offline-from "data/processed/forecast_methods/macro_pulls/final_capture" --output-dir "data/processed/forecast_methods/macro_pulls/review_capture"
& ".venv/Scripts/python.exe" -m pytest "analysis/src/forecast_methods/macro_pulls/test_run.py" -q
```

All exit codes 0. Initial network run: 42.12 seconds from first pull stamp to manifest completion, ending 17:24:49 UTC. Two-adapter refresh completed 17:27:00 UTC. Offline review run: 5.99 seconds, completed 17:28:22 UTC. Final tests: **9 passed in 1.91 seconds**. Independent offline check of all 14 normalized CSV hashes plus an exact rebuild of the three NTTO analysis CSVs passed in 6.47 seconds; receipts in `macro_pulls/validation/validation.json` and `test_receipt.txt`. The check imported the new `run.py`, called `backtest()` on the reviewed `ntto.csv`, and compared `ntto_replay_cells.csv`, `ntto_replay_summary.csv`, and `ntto_feature_comparison.csv` using `pandas.testing.assert_frame_equal(check_exact=True)`.

Only the scoped public HTTPS downloads required sandbox network escalation; no approval was rejected. No login, credential, licensed source, or Airbnb request occurred.

## Results

All rows below are **current retrieved revisions**, not historical PIT observations. Source URLs, specific series definitions, cadence and lags are documented in `analysis/src/forecast_methods/macro_pulls/README.md` and the manifest. No consensus values are consumed.

| Source | n normalized rows | Coverage | n verified `published_on` | Release lag / status |
|---|---:|---|---:|---|
| NTTO I-94 | 25,236 | Jan-2018–Jul-2026; 247 origin/group labels | 0 | Monthly; schedule gives approximate advance/preliminary/final days 8/18/28; exact historical observation dates unresolved |
| JNTO | 4,784 | Jan-2018–Jul-2026; 53 source labels across editions | 24 | July released 19 August: 19 days after month end |
| INE FRONTUR | 1,586 | Jan-2018–Jul-2026 | 15 | July released 1 September: 32 days |
| INE EGATUR | 824 | Jan-2018–Jul-2026; eight expenditure categories/totals | 8 | July released 1 September: 32 days |
| DATATUR | 700 | Jan-2018–Jun-2026; seven traveler/mode categories | 0 | Monthly; approximately six weeks, exact count-series release dates unresolved |
| ISTAT | 402 | Jan-2021–Jul-2026; arrivals and nights × three residence groups | 18 | Q1 release 26 May: 56 days after quarter end; later API months have unknown dates |
| Eurostat EU27 | 297 | Jan-2018–Mar-2026 | 9 | Q1 release 2 July: 93 days after quarter end |
| Eurostat ES | 297 | Jan-2018–Mar-2026 | 9 | Same quarterly dissemination |
| Eurostat FR | 297 | Jan-2018–Mar-2026 | 9 | Same quarterly dissemination |
| Eurostat IT | 297 | Jan-2018–Mar-2026 | 9 | Same quarterly dissemination |
| Eurostat DE | 297 | Jan-2018–Mar-2026 | 9 | Same quarterly dissemination |
| BLS exact-series CPI fallback | 103 | Jan-2018–Aug-2026 | 10 | Usually 10–14 days; August released 11 September |
| FRED requested CSV | 0 | No accepted response | 0 | Manifested read timeout; exploratory request also returned 404 |
| CoStar national ADR/RevPAR | 4 | One week ended 1-Aug-2026 | 4 | Released 6 August, five days; direct HTTP 403 retained, dated official-page web excerpt used |
| **Total** | **35,124** | Distinct observations, including overlapping aggregates | **124** | **No historical PIT promotion** |

The [official CoStar release](https://www.costar.com/products/str-benchmark/resources/press-releases/us-hotel-results-week-ending-1-august) supplies ADR $168.82 (+4.5%) and RevPAR $120.45 (+7.3%). Those four facts are saved in `public_web_extracts.csv`, with their source URL and transcription timestamp. This is a static fallback, not a successful automatic weekly refresh. The manifest distinguishes its excerpt hash from the HTTP-403 response hash. The [BLS calendar](https://www.bls.gov/schedule/news_release/cpi.htm) supplies actual publication dates; no approximate lag is converted into a synthetic release date.

### NTTO reconciliation (retrospective descriptive tests only)

Specification: two estimated parameters, OLS intercept plus slope; expanding training samples starting 2022Q1 for W1 / 2023Q1 for W2, minimum four observations; evaluation begins 2023Q1 / 2024Q1 and ends 2026Q2. No specification or threshold was optimized after seeing the ratios. Frozen nights-level naive, AR(1), and trailing-4 functions are called directly. Guide+cushion and Street do not cover nights.

| Source / feature / target / denominator | W1 n | W1 RMSE ratio | W2 n | W2 RMSE ratio |
|---|---:|---:|---:|---:|
| Legacy cached total full-quarter / growth / legacy last growth | 11 | 0.760291 | 10 | 0.719868 |
| Legacy cached total first-month / growth / legacy last growth | 11 | 1.069510 | 10 | 0.723860 |
| Legacy cached overseas first-month / growth / legacy last growth | 11 | 0.902524 | 10 | 0.742926 |
| Legacy cached total full-quarter / `nights_m` / frozen naive | 11 | 0.741704 | 10 | 0.687758 |
| New total full-quarter, **all corrected cells** / growth / legacy last growth | 14 | 1.091959 | 10 | 0.724559 |
| New total full-quarter, **all corrected cells** / `nights_m` / frozen naive | 14 | 1.032389 | 10 | 0.677116 |
| New total full-quarter, **same test cells as legacy** / growth / legacy last growth | 11 | 1.058524 | 10 | 0.724559 |
| New total full-quarter, **same test cells as legacy** / `nights_m` / frozen naive | 11 | 0.958597 | 10 | 0.677116 |
| New total first-month, all corrected cells / `nights_m` / frozen naive | 14 | 2.930197 | 10 | 0.768992 |
| New overseas first-month, all corrected cells / `nights_m` / frozen naive | 14 | 3.426374 | 10 | 0.949782 |
| Historical PIT-admitted forecasts | **0 of 14** | unavailable | **0 of 10** | unavailable |

Matched-cell comparisons restrict the new model's evaluation dates to the old test dates; the new model still uses the corrected historical training data. Level conversion weights growth errors by prior-year nights; the frozen baseline also has its own guide-date information slice. Neither distinction can be ignored to transplant the growth ratio into a level claim. All AR(1)/trailing-4 comparisons and per-cell inputs remain in the CSVs.

## What failed or could not be done, and why

The advertised `analysis/src/q3nowcast/G/` folder is absent; the actual older scripts are `analysis/src/q3nowcast/G1_collect_external_series.py` and `G2_external_backtests.py`. The cited `public_source_extracts.csv` is in the processed-data package, rather than the source-code package.

1. **Calendar gap in the old NTTO input.** The old normalized cache omits January–September 2022. Its feature builder shifts four available quarterly rows without filling the calendar gap; some comparisons therefore use the wrong year. The new parser admits all source date headers including preliminary labels, reindexes monthly dates, and requires three observed months for a full quarter. This both restores W1's first three test cells and changes training features. Missing-month comparison is recorded in `validation.json`.
2. **Historical publication/vintage gaps.** Unknown `published_on` stays null. Exact-date rows still remain quarantined because a current download can revise a previously published number. Source approximate schedules do not certify historical values. The current-quarter NTTO signal was not demonstrated available at historical guide dates.
3. **Two conservative parser rejections fixed once.** The initial DATATUR parser rejected null placeholders; BLS rejected `-` as a number. Both initial failures are retained in the root `manifest.json`; only those adapters were refreshed after treating placeholders as missing. No values were imputed. Tests include the BLS placeholder and DATATUR unit/direction guard.
4. **DATATUR correction to Lane 1.** `Tipo=Ingresos` identifies inflows, not a monetary unit. The same workbook contains `DescripcionNivel03=Número de Viajeros` count rows. Only inbound rows matching that level are admitted, in persons. Monetary rows are excluded; excursionists remain explicitly distinct from overnight tourists. This resolves the earlier all-money rejection without modifying the old package.
5. **Access and refresh limits.** The requested FRED CSV timed out and CoStar direct HTTP returned 403. The exact BLS series and one dated CoStar public-page excerpt provide labelled fallbacks. JNTO uses a pinned official edition; automatic latest-edition discovery and complete weekly CoStar history remain unfinished. No endpoint was retried indefinitely.
6. **Units and populations.** EGATUR is an explicit allowlist of eight expenditure category totals in EUR millions, not average spend or duration. Eurostat/ISTAT guest nights differ from Airbnb booked nights. Origin and aggregate rows overlap; totals must never be summed with their components.

## Interpretation

Source publication dates and the availability dates of downloaded revisions are separate. An unknown release date will remain null; it will never be invented by adding an assumed lag to the observation month. Current revised values will not be admitted as historical PIT vintages.

Candidates for WP-X are NTTO country-residence arrivals (US inbound only), JNTO nationality visitors (Japan only), FRONTUR residence arrivals, DATATUR explicitly selected traveler counts, and Eurostat/ISTAT stay-night observations. EGATUR is an expenditure covariate; BLS/CoStar are hotel-price context. None is promoted into the booked-GBV model. FRED access and the CoStar automatic pull are current dead ends, with alternatives and evidence retained. The NTTO result is a failed both-window replication, not an expectations edge. No team decision is taken.

## RESUME

Use `macro_pulls/review_capture/manifest.json` and the README as the reviewed handoff. Archive source release editions and recover exact publication dates before attempting historical PIT admission; retain original and revision availability separately. Extend verified JNTO edition discovery and CoStar weekly capture if access becomes available, and investigate FRED without replacing the requested SA series with an NSA series. WP-X may consume the documented current regional covariates with their geographic limitations. Parent should mark WP-C2 done (partial; NTTO both-window pass line failed), link this note, and log the NTTO calendar/DATATUR unit corrections in WORKBOARD. No registry or scorer update is needed for this package.
