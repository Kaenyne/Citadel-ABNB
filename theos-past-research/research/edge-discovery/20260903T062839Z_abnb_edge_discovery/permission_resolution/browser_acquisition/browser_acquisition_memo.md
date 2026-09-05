# Browser-Only Aggregate Acquisition Memo

Run: `20260903T062839Z_abnb_edge_discovery`
Observation time: `2026-09-03T18:14:31Z`
Collection mode: public-provider portal controls and visible chart tooltips only

## Outcome

The browser path produced 65 non-personal aggregate observations from four official, free public-data sources. No API endpoint was called. Two official annual workbooks were manually downloaded through the browser for local privacy/schema review; only report-level aggregates were copied into the research ledger, and no address, contact, host, operator, or other personal field was retained there.

This is a real extraction, but it is not yet an ABNB alpha result. The observations are current portal views, not original historical vintages. They are therefore suitable for monitoring, coverage diagnostics, and prospective snapshot collection; they are not admitted into a look-ahead-safe historical backtest.

## Vancouver short-term-rental licensing

Official pages:

- Current dataset: <https://opendata.vancouver.ca/explore/dataset/business-licences/information/>
- Historical dataset: <https://opendata.vancouver.ca/explore/dataset/business-licences-2013-to-2024/information/>

The portal was filtered to `Business type = Short Term Rental`. Aggregate facets were read without opening or retaining raw address-level rows.

### Issued records by folder year

| Folder year | Historical page | Current page | Treatment |
|---:|---:|---:|---|
| 2018 | 3,248 | — | Monitoring only; not an original vintage |
| 2019 | 4,209 | — | Monitoring only; not an original vintage |
| 2020 | 2,797 | — | Monitoring only; not an original vintage |
| 2021 | 2,179 | — | Monitoring only; not an original vintage |
| 2022 | 2,591 | — | Monitoring only; not an original vintage |
| 2023 | 3,188 | — | Monitoring only; not an original vintage |
| 2024 | 2,982 | 2,989 | Overlap break; do not splice automatically |
| 2025 | — | 3,075 | Prospective candidate |
| 2026 | — | 3,915 | Partial-year/current-state candidate |

The seven-record 2024 difference demonstrates that the two portal views are not interchangeable vintages. For all statuses, the 2024 difference is one record (4,569 historical versus 4,568 current).

### Reconciliation checks

- Current folder-year totals: `4,568 + 4,201 + 4,722 = 13,491`, equal to the filtered portal total.
- Current status totals: `9,979 + 1,625 + 1,289 + 539 + 59 = 13,491`.
- Current issued folder-year totals: `2,989 + 3,075 + 3,915 = 9,979`.
- Historical status totals: `21,194 + 4,716 + 4,214 + 2,134 + 205 = 32,463`.
- Historical issued folder-year totals shown for 2018-2024 sum to 21,194. The visible portal facet therefore accounts for the complete issued subset.

The open-data licence permits reuse with attribution, but that does not override privacy discipline. Only provider-calculated aggregates were retained.

## Melbourne pedestrian activity

Official page: <https://data.melbourne.vic.gov.au/explore/dataset/pedestrian-counting-system-monthly-counts-per-hour/analyze/>

The Analyze view was set to:

- X axis: `Sensing_Date`
- Timescale: `Year`
- Points: `Show all`
- Aggregation: `SUM`
- Measures: `Direction_1`, `Direction_2`, and `Total_of_Directions`

### Visible annual aggregates

| Sensing year | Direction 1 | Direction 2 | Total directions | Source rows | Treatment |
|---:|---:|---:|---:|---:|---|
| 2024 | 49,324,560 | 49,914,384 | 99,238,944 | 253,428 | Incomplete or migration-limited; control only |
| 2025 | 159,981,654 | 161,780,597 | 321,762,251 | 815,447 | Closed year but mutable current view; control only |
| 2026 | 107,688,032 | 109,363,514 | 217,051,546 | 550,863 | Partial through observation date; control only |

For every year, `Direction_1 + Direction_2 = Total_of_Directions` exactly. The 2024 observation count is dramatically lower than 2025, so the 2024 total must not be treated as a comparable annual demand measure. Changes in the sensor panel, outages, and portal migration must be controlled before signal testing.

This series is geographically remote from Airbnb's largest disclosed markets and is therefore best treated as a physical-activity control or methodology pilot, not direct ABNB demand evidence.

## NYC 311 tourism-stress proxy

Official page: <https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9>

The provider's visible query builder was used to count August 2026 service requests for two first-level problem categories by borough:

- Candidate category: `Noise - Street/Sidewalk`
- Negative/control category: `Noise - Residential`
- Date window: `2026-08-01 00:00:00` inclusive through `2026-09-01 00:00:00` exclusive
- Retained fields: problem label, borough, and aggregate count only

| Borough | Street/sidewalk noise | Residential noise | Street/residential ratio |
|---|---:|---:|---:|
| Manhattan | 5,909 | 4,168 | 1.418 |
| Bronx | 8,415 | 7,519 | 1.119 |
| Brooklyn | 5,703 | 10,205 | 0.559 |
| Queens | 3,283 | 7,504 | 0.438 |
| Staten Island | 333 | 1,226 | 0.272 |
| Unspecified | 1 | 0 | Not meaningful |
| **Citywide** | **23,644** | **30,622** | **0.772** |

The Manhattan ratio is directionally consistent with a tourism/nightlife exposure hypothesis, but this is only one month and is not causal evidence. Population density, nightlife zoning, reporting propensity, policing, and complaint-channel changes are mandatory controls. The portal states that expected values for many fields change over time, so this observation is a prospective snapshot rather than a frozen historical vintage.

## NYC OSE short-term-rental enforcement

Official reports page: <https://www.nyc.gov/site/specialenforcement/about/data-reports.page>
Reviewed workbooks:

- <https://www.nyc.gov/assets/specialenforcement/downloads/excel/2024_LL87_OSE_Annual_Report.xlsx>
- <https://www.nyc.gov/assets/specialenforcement/downloads/excel/2025_LL87_2025_Annual_Report.xlsx>

The page states that its reports are available for public and research use. The 2024 and 2025 workbooks were downloaded manually in the browser and inspected locally. Their address-level summons/location tabs were excluded from the research artifacts; only totals and narrative percentages were reviewed.

| Measure | 2024 | 2025 | Change |
|---|---:|---:|---:|
| Illegal STR complaints | 2,356 | 2,036 | -13.6% |
| Distinct complaint locations | More than 1,750 | More than 1,537 | Not precisely measurable |
| Inspections | 6,717 | 8,553 | +27.3% |
| — Attempted | 5,286 | 6,463 | +22.3% |
| — Conducted | 872 | 1,012 | +16.1% |
| — Follow-up | 559 | 1,078 | +92.8% |
| Summonses/violations issued | 1,452 | 1,909 | +31.5% |
| Penalties imposed | $5,643,869 | $9,636,307 | +70.7% |
| Penalties paid | $519,645.22 | $631,870.58 | +21.6% |
| Share paid | 9.21% | 6.56% | -2.65 percentage points |
| Immediately hazardous violation locations | 64 | 105 | +64.1% |

Reconciliation checks passed in both workbooks: inspection components tie to the published total; district tables tie to complaints and summonses; and penalties paid divided by penalties imposed reproduces the published collection share. No spreadsheet formula-error strings were found in either focused workbook scan.

Important timing caveats:

- The 2024 report is dated **September 1, 2025**, and the 2025 report is dated **September 1, 2026**. Each year becomes cutoff-eligible only on or after its report date.
- The penalties sheet says imposed and paid data are as of April 2025, while a summons-status note elsewhere says April 2026. The apparent timing inconsistency must be resolved before using penalty collection as a signal.
- The workbook says 51% of complaints, 49% of inspections, and 60% of violations were for multiple dwellings; it also says roughly 67% of locations receiving violations were controlled by corporate entities. These narrative figures are context, not separate model inputs.
- Source workbook SHA-256 values: 2024 `ef4d642ec220428be207217f0daf7f50e285498a2dbdce3075981f38dfc422e9` (296,490 bytes); 2025 `f46321158fb44d9d386429fe96edc9e8950f5ecb7ca9f63e8a351ea61cc0b0` (319,532 bytes). The source workbooks remain outside the research artifact directory because they contain address-level tabs.

## Research disposition

| Source | Acquisition succeeded? | Safe aggregate? | Point-in-time safe? | Present use |
|---|---|---|---|---|
| Vancouver STR licences | Yes | Yes | No, except prospectively from this timestamp | Supply-scarcity monitoring candidate |
| Melbourne pedestrian counts | Yes | Yes | No, except prospectively from this timestamp | Physical-world control and sensor-panel diagnostic |
| NYC 311 tourism-stress proxy | Yes | Yes | No, except prospectively from this timestamp | Tourism-stress candidate with residential-noise control |
| NYC OSE enforcement | Yes | Yes, after local aggregation-only review | 2024 eligible on/after 2025-09-01; 2025 on/after 2026-09-01 | Regulatory-friction / supply-withdrawal candidate |

No source is promoted. The next meaningful step is to extract the 2024 and 2023 OSE report totals to create a short, versioned series; establish dated recurring snapshots for Vancouver and NYC 311; and add weekend-night and fixed-geography definitions to the NYC query design before any signal test. Manual raw-file downloads remain deferred wherever the portal exposes unnecessary personal or address-level fields.
