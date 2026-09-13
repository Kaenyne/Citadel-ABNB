# C2 public macro and arrivals pulls

Canonical reviewed capture for this task: `data/processed/forecast_methods/macro_pulls/review_capture/`.
The root capture is retained as the first-run receipt; `final_capture/` retains the corrected DATATUR/BLS run.
Each invocation writes a new directory and refuses to overwrite a nonempty one. Nothing touches the harness, L0, another package, or Airbnb.

From the repository root, with `.venv` activated:

```powershell
python analysis/src/forecast_methods/macro_pulls/run.py
python -m pytest analysis/src/forecast_methods/macro_pulls/test_run.py -q
python analysis/src/forecast_methods/macro_pulls/run.py --offline-from data/processed/forecast_methods/macro_pulls/review_capture
```

On this Windows host without an activated environment, replace `python` with `& ".venv/Scripts/python.exe"`.
Dependencies: requests, pandas, numpy, openpyxl, beautifulsoup4; pytest for the edge-case checks. Network mode makes one GET per endpoint with bounded connection/read timeouts and four workers. An HTTP failure is recorded once; it is not retried automatically. `--output-dir` selects a new directory. `--offline-from` verifies each normalized input's SHA-256 before rebuilding the analysis. `--refresh-series datatur,bls_cpi_lodging` with `--offline-from` refreshes only named adapters and retains the prior manifest reference.

## Sources and publication timing

Lags below describe publication, never an instruction to synthesize release dates. `published_on` is populated only for the observation months explicitly tied to a dated primary release/calendar; older dates remain null. `knowable_from` is the retrieval day for this revised value. All historical `pit_usable` flags are false: a first-release date alone does not establish that today's revised value was available then.

| Series | URL / data endpoint | Cadence | Documented lag and release source | Scope and units |
|---|---|---|---|---|
| NTTO I-94 | [Monthly country-of-residence XLSX](https://www.trade.gov/sites/default/files/2024-06/Monthly%20Arrivals%202000%20to%20Present%20%E2%80%93%20Country%20of%20Residence%20%28COR%29_1.xlsx) | Monthly | [Program schedule](https://www.trade.gov/i-94-arrivals-program) gives approximate advance/preliminary/final release days 8/18/28; exact historical observation-release links unresolved | US international arrivals, persons, country/residence groups and totals; not domestic travel. Do not sum country and region/total rows. |
| Eurostat platform nights | [tour_ce_omr API, EU27](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tour_ce_omr?lang=en&geo=EU27_2020&indic_to=NGT_SP&unit=NR), same query for ES/FR/IT/DE | Monthly observations; quarterly dissemination | [Tourism release list](https://ec.europa.eu/eurostat/web/tourism/) dates Q1 2026 release 2 July: 93 days from quarter end, 152 days from January end | Guest nights in platform-booked stays; domestic/foreign/total are overlapping categories. Platform guest nights are not Airbnb booked nights. |
| JNTO | [Official history XLSX](https://www.jnto.go.jp/statistics/data/_files/20260819_1615-5.xlsx) | Monthly | [July dated release](https://www.jnto.go.jp/en/news/20260819.pdf): 19 August, 19 days from July end | Japan inbound visitors by source nationality/group; 2018–2026 history, not residence or whole APAC. Endpoint is the explicit captured edition, not a latest-file discovery service. |
| INE FRONTUR | [Table 75719 JSON](https://servicios.ine.es/wstempus/js/EN/DATOS_TABLA/75719?nult=200) | Monthly | [July release](https://www.ine.es/dyngs/Prensa/en/FRONTUR0726.htm): 1 September, 32 days from July end | Spain international tourists by country of residence, persons; base data only |
| INE EGATUR | [Table 13938 JSON](https://servicios.ine.es/wstempus/js/EN/DATOS_TABLA/13938?nult=200) | Monthly | [July release](https://www.ine.es/dyngs/Prensa/en/EGATUR0726.htm): 1 September, 32 days from July end | Eight explicitly allowlisted expenditure totals/categories, EUR millions. No rates, cumulative totals, average spend, or duration. Categories overlap. Source: INE; derived analysis is ours. |
| DATATUR | [Public ZIP](https://datatur.sectur.gob.mx/Documentoscompartidos/cuentaviajeros/BD_CuentaViajeros_descarga.zip) | Monthly | [Official report page](https://datatur.sectur.gob.mx/SitePages/cuentaviajeros.aspx), roughly six weeks; exact count-observation release dates unresolved and remain null | Inbound `Tipo=Ingresos` **and** `DescripcionNivel03=Número de Viajeros`: persons. Seven tourist/excursionist/mode categories; they are not all overnight tourists. Blank cells remain missing. |
| ISTAT | [Monthly arrivals/nights CSV flow](https://esploradati.istat.it/SDMXWS/rest/data/IT1,122_54_DF_DCSC_TUR_13,1.0/all?startPeriod=2021-01), HTTP Accept `text/csv` | Monthly observations; quarterly press releases | [Q1 release](https://www.istat.it/comunicato-stampa/i-flussi-turistici-i-trimestre-2026/): 26 May (56 days from quarter end); next scheduled release 14 September. Later API months have unknown exact release dates. | National unadjusted accommodation arrivals/nights, domestic/foreign/world, all accommodation; flow dimensions explicitly filtered. No double-counting of overlapping totals. |
| CoStar/STR | [Week ended 1 August release](https://www.costar.com/products/str-benchmark/resources/press-releases/us-hotel-results-week-ending-1-august) | Weekly | Release 6 August, five days after week end | National hotel ADR and RevPAR (USD and y/y %). Direct HTTP returned 403. Four factual values from the official page via web fetch are stored in `public_web_extracts.csv`; this is a static dated fallback, not a working automatic weekly refresh. |
| Requested FRED CUSR0000SEHB | [Requested CSV endpoint](https://fred.stlouisfed.org/graph/graph.csv?id=CUSR0000SEHB&cosd=2018-01-01) | Monthly | [BLS CPI calendar](https://www.bls.gov/schedule/news_release/cpi.htm), usually 10–14 days; August 2026 on 11 September | FRED failed (35-second read timeout in manifested run; exploratory direct request also returned 404). No FRED rows fabricated. |
| BLS fallback, exact CUSR0000SEHB | [Public BLS API](https://api.bls.gov/publicAPI/v2/timeseries/data/CUSR0000SEHB?startyear=2018&endyear=2026) | Monthly | Same BLS calendar; known release mappings for November 2025–August 2026 | Seasonally adjusted lodging-away-from-home CPI, index 1982–84=100. `-` means missing and is excluded, never zero. Separately identified provider; no NSA substitution. |

## Outputs and audit

Each source has a tidy CSV even when empty. `manifest.json` records URL, source cadence/lag, actual UTC pull timestamp, status/error, response SHA-256/bytes, normalized rows/hash and release-date coverage. Raw responses are kept in memory only. CoStar's failed-response hash and successful factual-excerpt hash are separate. Current revisions have their retrieval date rather than invented historical vintage dates.

`ntto_replay_cells.csv` and `ntto_replay_summary.csv` expose the old feature reproduction, new calendar-aligned series, and new forecasts restricted to the old test cells. All regressions use two coefficients (intercept plus slope), expanding samples, minimum four training observations, and label historical availability as unverified. `ntto_feature_comparison.csv` makes the revisions visible; `ntto_pit_admission.json` records 0/14 W1 and 0/10 W2 historical PIT admissions.

The legacy growth replay reproduces W2's 0.7199/0.7239/0.7429 ratios. They are not level-forecast ratios. Frozen `baseline_naive`, `baseline_ar1`, and `baseline_trailing4` are called directly on `nights_m`; guidance/Street baselines do not exist for nights. No registry forecast is created and no scorer is run. Revised current-quarter features cannot be treated as known at historical guide dates.

The old NTTO cache lacks January–September 2022. Its row-based `shift(4)` can compare different calendar years. The new feature builder reindexes actual calendar months before constructing the same-month or full-quarter y/y rate, and requires all three months for a full quarter. On all corrected cells, total-full ratios to frozen nights-level naive are **1.0324 W1 (n=14)** and **0.6771 W2 (n=10)**; that does not satisfy both-window acceptance. The matched old-cell comparison is 0.9586 (n=11) / 0.6771 (n=10), also not the advertised 0.72–0.74 band.

## Limitations / next work

NTTO, JNTO, FRONTUR and DATATUR are destination demand covariates; Eurostat and ISTAT add stay-night context, EGATUR adds expenditure, BLS and CoStar add hotel-price context. These are not direct booked-GBV signals or interchangeable regional population measures. Exact historical release dates and vintages remain the main missing input for PIT promotion. Acquire source release archives, add a verified JNTO edition-discovery step, and repair CoStar/FRED access before claiming automated coverage of all eight requested families.
