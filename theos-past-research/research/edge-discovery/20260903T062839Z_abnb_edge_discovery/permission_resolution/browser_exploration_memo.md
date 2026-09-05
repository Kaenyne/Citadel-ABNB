# Browser Exploration Memo

Run: `20260903T062839Z_abnb_edge_discovery`
Exploration date: 2026-09-03
Mode: official-site, human-style browser navigation only

## Scope and controls

- Visited official landing, documentation, archive, metadata, licence, and visible download pages.
- Did not run bulk extraction, API loops, crawlers, or headless scraping.
- Did not sign in, provide credentials, solve CAPTCHAs, submit contact forms, or bypass access controls.
- Did not download source datasets during this pass.
- Did not retain or reproduce address-, phone-, email-, host-, or operator-level records exposed by public registry pages.
- Browser findings do not retroactively change the automated-scraping gate. They establish a separate manual-browser acquisition path for later approval.

## Source-by-source findings

| Rank | Source | Visible official-site evidence | Manual-browser disposition | Point-in-time observation |
|---:|---|---|---|---|
| 1 | `NASA_BLACK_MARBLE_VNP46A2` | Earthdata catalog returned a CloudFront 403; the search fallback triggered an unusual-traffic challenge. | Blocked; stop without login or challenge handling. | Authenticated granule/version metadata remains unresolved. |
| 2 | `NOAA_HMS_SMOKE` | OSPO product documentation loaded. The official annual-bundle directory visibly lists 2005-2026 ZIP files. | Browsable archive; candidate for a later, single-file manual validation. | Files for 2005-2023 share a 2025-02-04 last-modified date, so the current archive is not proof of original availability. |
| 3 | `WSF_FERRY_RIDERSHIP` | Official page exposes annual PDF reports for 2002-2025, quarterly history for 2009-2026, and a public Tableau dashboard. | Strong manual research candidate. | Many historical reports now use 2026 or 2021 upload paths; current links do not prove original publication timestamps. |
| 4 | `NYC_OSE_STR_SNAPSHOTS` | Official page offers one January 7, 2026 workbook and describes address-, unit-, registration-, and listing-level fields. Applicant names are omitted. | Do not acquire the raw workbook; use only provider-published aggregates or a future privacy-preserving view. | One current snapshot is visible; no historical snapshot panel was found. |
| 5 | `ORANGE_FL_TDT_RELEASES` | Official archive exposes monthly budget-versus-actual reports for FY2020-FY2025 plus annual-history and current XLSX links. Copyright page states all rights reserved. | Browsable for research; defer downloads until reuse scope is clarified. | Archive entries identify fiscal years but did not visibly establish original release timestamps. |
| 6 | `VANCOUVER_STR_LICENSES` | Dataset page exposes current records, separate 1997-2012 and 2013-May 2024 history, daily current updates, a change log, and privacy notes. Dataset-specific Open Government Licence permits worldwide, royalty-free, commercial use with attribution. | Highest-priority browser-only candidate, using the site's analysis UI or a field-minimized manual export. | Historical category breaks and daily update timing are documented; current extracts are not historical snapshots. |
| 7 | `NPS_VISITOR_USE` | Official FAQ states monthly data are generally available by the 15th of the following month, remain preliminary until first-quarter finalization, and extend monthly to 1979 and annually to 1904. REST help page is visible. | Strong browser/manual-report candidate; automated access remains blocked by robots policy. | Publication lag and revision policy are explicitly documented, supporting prospective cutoff control. |
| 8 | `NYC_OSE_ENFORCEMENT_REPORTS` | Official page says materials are available for public and research use; annual enforcement workbooks span 2016-2025 and registration reports span FY2023-FY2026. | High-priority manual-download candidate with workbook-level privacy review. | Annual labels are visible, but original posting timestamps were not established from the current page. |
| 9 | `FTA_NTD_MONTHLY_RIDERSHIP` | Official page states releases usually occur during the first full week, generally the 4th-7th. The current raw workbook has a date-coded filename and warns that prior months and years may be revised. | High-priority prospective manual-download candidate. | Date-coded release files support collection-time evidence going forward; the current page exposes only the latest workbook. |
| 10 | `NOLA_STR_PERMIT_EVENTS` | The public map/table loaded, but its visible rows and schema expose address and individual contact fields. | Reject raw browsing/download; do not retain or process row-level data. | Application and issue dates exist, but the public page is a current mutable table. |
| 11 | `NOLA_STR_ENFORCEMENT_HEARINGS` | Metadata-only page covers hearings from 2018 onward, updates daily, contains an address field, and says no changes have been archived. | Use only a provider-side aggregate view if later justified; no raw acquisition. | No archived restore points were visible. |
| 12 | `SAN_DIEGO_STRO_ACTIVE` | Dataset page exposes a CSV and an explicit PDDL licence, but the public schema/sample includes precise property and individual contact fields. | Reject raw acquisition; request or construct only a provider-side non-personal aggregate. | Current active-licence snapshot only; no historical versions were visible. |
| 13 | `MARINECADASTRE_AIS` | Official pages expose AIS data for 2009-2026, daily national files since 2015, older monthly files, derived track lines and transit counts, metadata, and known data-quality breaks. | Prefer small precomputed transit-count products; avoid raw national point files. | Quarterly page updates and annual coverage are visible, but original file publication timestamps still need evidence. |
| 14 | `NYC_311_TOURISM_STRESS` | Official dataset is updated daily, explicitly says customer identities are not revealed, provides 2010-2019 and 2020-present history, and exposes browser Export/Data controls. | Highest-priority browser-side aggregate candidate. | Historical event dates exist, but the mutable current dataset is not a frozen historical vintage. Start prospective snapshots. |
| 15 | `MELB_PED_HOURLY` | Official page documents hourly counts since 2009, monthly updates, sensor-regime cautions, and a historical attachment through December 2022. City policy applies CC BY 4.0 with attribution. | Highest-priority manual-download candidate. | Sensor-location changes require a frozen sensor panel; archive attachment provides history but not original release timestamps. |

## Recommended browser-first order

1. `MELB_PED_HOURLY`: manually download the published historical attachment; retain only counts, timestamps, and sensor IDs; join to public sensor metadata with regime controls.
2. `VANCOUVER_STR_LICENSES`: use the portal's analysis UI first; if export is later approved, select only year, licence category/status, issue date, and coarse geography.
3. `NYC_311_TOURISM_STRESS`: use browser-side filters/summary tables to define non-personal tourism-stress aggregates, then start dated prospective snapshots.
4. `NYC_OSE_ENFORCEMENT_REPORTS`: manually download one annual workbook and perform a local privacy/schema review before retaining anything.
5. `FTA_NTD_MONTHLY_RIDERSHIP`: manually collect the latest date-coded workbook and begin a prospective release archive.
6. `NPS_VISITOR_USE`: use visible portal reports under the documented monthly publication and revision schedule.

`NOAA_HMS_SMOKE`, `WSF_FERRY_RIDERSHIP`, and `MARINECADASTRE_AIS` remain useful controls or disruption measures, but their current archive presentation does not establish historical publication vintages. NASA remains blocked. The NYC OSE snapshot, NOLA permit/hearing, and San Diego raw STR tables remain excluded because browser-visible fields create unnecessary personal-data exposure.
