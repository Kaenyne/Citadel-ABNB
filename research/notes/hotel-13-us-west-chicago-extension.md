# Chicago, Los Angeles and San Diego hotel supply frames

As of September 7, 2026. These are three of the user-confirmed original 13 listing-panel markets, not three countries from the separate Airbnb-listing coverage panel. The work establishes observable hotel supply frames; it does not establish Airbnb distribution, boutique/independent ownership, hotel booking demand or revenue.

| Market | Auditable result | Exact unit and scope | Still missing |
|---|---:|---|---|
| Chicago | 215 current licenses; 214 account-site pairs; 209 exact addresses | City-licensed hotel activity, seven or more sleeping rooms. Different administrative units, not three estimates of physical hotels. | Citywide hotel rooms; physical-property reconciliation; independent/boutique rooms. |
| Los Angeles | 173 hotel profiles; 172 report rooms; their room fields sum to **35,501** | Official municipal Tourism Marketing District directory subset, generally lodging with at least 50 rooms. Undated property profile facts retrieved September 7. | One profile room field; smaller properties; fully reconciled city stock; independent/boutique rooms. |
| San Diego | **40,158 city hotel rooms** | Official April 30, 2026 tourism fact sheet; separate infrastructure census date unspecified. | Reconciled city property register and independent/boutique room split. |

The Los Angeles subset is materially more useful than the earlier 98,600-room regional headline: it provides named properties, addresses and downloadable room fields that can be matched to Airbnb. It remains a restricted and partly unreconciled supply frame. The San Diego number is the prior team's source, now reverified with a clearer publication date; it is not a new independent discovery.

## Chicago: current licenses, not historical renewals

Downloaded [Chicago's current-active business license view](https://data.cityofchicago.org/Community-Economic-Development/Business-Licenses-Current-Active/uupf-x98q), querying hotel business activity or hotel license description. The response has 226 rows, all issued status `AAI`. Hotel activity is recorded as `Hotel - 7 or More Sleeping Rooms`, activity ID 676 under Regulated Business License. Source metadata was updated September 6, 2026.

The source view filters future expiration dates, but still includes 11 terms whose start date falls after September 7. Filtering `license_start_date <= 2026-09-07 <= expiration_date` yields 215 unique license numbers, 214 distinct `(account_number, site_number)` pairs and 209 exact address strings. Two current licenses refer to the same account/site and the same three-brand Hampton/Hilton Garden/Home2 complex at 123 E Cermak. Separate operators and brands may share addresses, so none of these counts should be relabeled a physical hotel census.

The preliminary legacy Hotel license-code 1370 extraction contained 1,402 historical terms, with the latest expiration in 2015. **Those historical rows are excluded from current supply.** Filtering only the literal license description would therefore have produced the wrong answer. Raw exploratory evidence is preserved.

The current license schema does not report room counts. A separate [Choose Chicago March 2024 presentation](https://cdn.choosechicago.com/uploads/2024/03/DNC_Choose-Chicago-Partner-Event-Presentation-3.6.24_DEE9BA57-5056-A36F-237DF37A967C68B9.pdf), PDF page 4, reports nearly 44,000 rooms in the **central business district**. This dated, rounded CBD observation is retained separately. The earlier approximately 46,000 CBD claim had only search-index evidence and a blocked direct page; it is not promoted into a new verified citywide stock count.

## Los Angeles: 173 official directory profiles, 172 explicit room fields

Downloaded the complete visible table in the [Los Angeles TMD directory](https://www.discoverlosangeles.com/tmd): 173 distinct linked hotel profile URLs, each with property name, postal address and region. All 173 detail requests succeeded. The reproducible extractor accepts only the explicit `Total Rooms:` field, not meeting rooms, maximum attendance or a room number mentioned in prose. It found exactly one such field on 172 pages, with positive values totaling 35,501. Bonnie Lee Inn has no such field and remains null.

Examples of the source field are [AC Hotel Beverly Hills: 176 rooms](https://www.discoverlosangeles.com/hotels/ac-hotel-beverly-hills), AC Hotel Downtown Los Angeles: 347, Moxy Downtown Los Angeles: 380, and JW Marriott Los Angeles L.A. LIVE: 878. Every profile's exact URL, response bytes and SHA-256 are in the manifest and source ledger. This is 173 related source records from one publisher, not 173 independent samples of hotel demand.

The [July 12, 2024 Management District Plan](https://cityclerk.lacity.org/onlinedocs/2014/14-0943-S3_misc_2_09-11-24.pdf) defines the district's municipal boundary and minimum 50-room threshold on PDF page 8. Its July 2024 assessed-business list is on pages 30–34 and has names/addresses but no property room counts. That historical list is preserved as scope evidence and is not added to the current directory row count. The minimum threshold means a large and economically relevant part of small boutique supply is structurally absent.

Three exact-address pairs in the directory correspond to separate brands:

| Shared address | Reported brand-room fields |
|---|---|
| 1260 S Figueroa Street | AC 347; Moxy 380 |
| 901 W Olympic Boulevard | Courtyard 174; Residence Inn 219 |
| 900 W Olympic Boulevard | JW Marriott 878; Ritz-Carlton 123 |

The room total retains each distinct property profile and its own field. It is a **sum of reported profile rooms**, not an independently reconciled physical-room total or a hard current capacity floor. Field vintage, closures, rebrands and dual-brand physical overlap still require validation. Postal names such as Venice, San Pedro and West Hollywood do not by themselves determine municipal jurisdiction; membership follows the TMD directory and plan rather than a naive postal-name filter.

For broader context only, the [2025-labelled travel-trade guide uploaded in January 2026](https://www.discoverlosangeles.com/sites/default/files/2026-01/lat_whatsnew_traveltradesalesguide_8.5x11in_2025.pdf), PDF page 2, reports close to 1,400 hotels and more than 115,000 rooms/suites across the Los Angeles destination region. Its precise denominator boundary is unspecified and it includes surrounding destination locations. It cannot substitute for a municipal city denominator or be added to the 35,501-room subset.

## San Diego: retain city capacity, reject tax accounts as a census

The [San Diego Tourism Authority's April 30, 2026 fact sheet](https://www.sandiego.org/about/san-diego-tourism-fast-facts) reports 40,158 hotel rooms in the **City of San Diego**, 68,954 in **San Diego County**, and 14,878 **downtown**. These are different, partly nested geographies; do not add them. Its 681-property tourism-infrastructure figure combines hotels, motels, bed-and-breakfasts and casino hotels and is not identified as a city-only hotel census. The infrastructure figures lack a separate stock observation date, despite nearby flow tables explicitly covering CY2025. The web tool retrieved the full page; direct Python retrieval returned HTTP403. The saved numeric evidence record explicitly identifies this retrieval difference.

Also downloaded the entire official [active business-tax certificate file](https://seshat.datasd.org/business_tax_certificates/sd_businesses_active_datasd.csv), updated September 7, 2026: **59,419 active tax accounts**. The source's recorded code `72111` identifies **52 hotel/motel account candidates**, while the broader `721` prefix contains **524 accommodation-related accounts**, including **347 short-term-rental accounts**. These are classification results inside a business-tax register, not extra hotel inventory. Examples include an InterContinental San Diego account with an Atlanta address and Hotel Z with a Plano address. Other records use broader accommodation codes, multiple brands or owner/management entities. The file cannot be treated as a hotel-property census or reconciled room capacity.

The 52 narrow candidates and 524 broad candidates are exported separately for later matching. `property_records_obtained` is deliberately **0** for a reconciled San Diego property register; the machine-readable output separately records the 52 candidate tax accounts. This prevents 59,419 businesses, 524 accommodation accounts or 52 hotel-coded accounts from inflating the hotel sample.

## Reproducibility and overlap

- Machine-readable integration output: `data/raw/hotel_13_market_extension/us_west_chicago/market_results.json` (one record for each of chicago, los-angeles and san-diego).
- Source ledger: `research/sources/hotel_13_us_west_chicago_sources.json`.
- LA raw profiles, 173-row property/room CSV and extraction manifest: `data/raw/hotel_13_market_extension/us_west_chicago/`.
- Chicago current-term license CSV and original source response are in the same directory.
- San Diego original 59,419-account file and both candidate exports are in the same directory; only appropriate candidates are research frames.
- Run `collect_la_details.py` to reproduce LA extraction from cached raw profile responses, then `build_market_results.py` to rebuild integration outputs and verify all source hashes. The scripts make no booking requests or form submissions.

An exact-URL search across other accessible `research` JSON/Markdown files found the San Diego fact sheet already in `hotel_funnel_audit.json` as `HOTEL-SAN`. That observation is marked reused/reverified. The new Chicago license extraction and LA directory/property extraction were not found there during this bounded check. Same-source profile pages are explicitly related evidence, not independent demand observations. An absence of overlap in accessible repository files does not certify absence from Jessica's private or off-repository research.

These frames make a subsequent property match and supply-allocation study possible. They do **not** identify Airbnb hotel nights or establish that more hotel listings create incremental bookings. All three markets retain `independent_rooms = null` until brand/ownership classification is obtained and reconciled; no generic independent share is applied to total rooms.
