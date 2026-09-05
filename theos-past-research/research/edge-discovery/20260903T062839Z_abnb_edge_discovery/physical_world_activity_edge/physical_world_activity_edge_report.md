# ABNB physical-world activity edge — E0 source discovery report

## Agent hierarchy

1. **ABNB Edge-Data Research Orchestrator** — main Codex task; owns orchestration, user communication, and the final source decision.
2. **abnb_alt_data** — permanent research lead; owns governance, canonical registries, point-in-time methodology, reconciliation, and the ranked combined slate.
3. **physical_world_activity_edge** — physical sensors, mobility, transportation, remote sensing, environmental, infrastructure, maritime/island, and realized-event activity lane.
4. **supply_scarcity_web_edge** — STR, regulatory, scarcity, and public-web lane.

## Scope and decision

This is E0 discovery only. No candidate was compared with an ABNB outcome, no hypothesis was registered or revised, and no model, correlation, backtest, or feature search was run. Evidence was limited to official-provider search-result reconnaissance and existing project materials. Exact source pages were not requested because all ten `ScrapeCandidate` assessments denied collection under the audited gate. Consequently, the tiny-sample manifest records zero requests and no cached payloads.

The strongest historical point-in-time candidate is **Washington State Ferries (WSF) ridership**, because dated quarterly PDF reports appear to preserve the information set available soon after each period. It remains conditional on exact path-specific terms/robots approval or a lawful user-supplied export, plus an event-by-event publication audit. **NASA Black Marble** has the highest raw ex-ante score and global reach, but it is an experimental proxy and is blocked pending approved Earthdata credential sync and granule-vintage validation. **NOAA HMS smoke/fire** has strong daily operational timing, but its current annual bundles appear to have been regenerated; they cannot be treated as original vintages without further evidence.

Most other sources expose historical observations, not historical publication vintages. That distinction is dispositive: an old observation in a current database is not proof that the value was available at a historical guidance cutoff.

## Ranked candidate slate

Operational rank prioritizes current strict usability and auditable timing; it is intentionally not a sort of the raw score alone.

| Rank | Source | Score | Status | Strict eligible events now | Main reason to keep or reject |
|---:|---|---:|---|---:|---|
| 1 | WSF ferry ridership | 77 | `backtestable_now` conditional | 0 verified | Dated quarterly PDFs offer the cleanest vintage path; narrow geography and permission audit remain. |
| 2 | NASA Black Marble VNP46A2 | 80 | `pending_sync` | 0 | Global daily 500 m archive and production metadata; indirect mechanism, reprocessing risk, and Earthdata authentication. |
| 3 | NOAA HMS smoke/fire | 77 | `pending_permission` | 0 | Daily release windows and 2005+ archive; regenerated bundles and a 2022 product regime break weaken vintage claims. |
| 4 | NPS visitor use | 71 | `pending_permission` | 0 | Monthly history from 1979, but preliminary data arrive by the 15th and remain revisable until Q1 finalization; no vintages found. |
| 5 | FTA NTD monthly ridership | 67 | `pending_permission` | 0 | Formal first-full-week release and two-month lag; current rolling products do not reconstruct historical releases. |
| 6 | TfL Santander Cycles hires | 61 | `pending_permission` | 0 | Weekly files since September 2015; automation language for Santander Cycles is ambiguous and replacement behavior is unknown. |
| 7 | Melbourne pedestrian counts | 58 | `pending_permission` | 0 | Hourly observations since 2009 and monthly updates; undefined portal terms, mutable history, and sensor relocation risk. |
| 8 | MarineCadastre AIS | 62 | `prospective_only` | 0 | Differentiated maritime/island activity, but partial 2020–2025 range, unavailable ordering service, and no defensible vintage schedule. |
| 9 | CDOT continuous traffic counts | 57 | `pending_permission` | 0 | Hourly physical counts at 118 stations; history start, review/repair policy, release lag, and vintages are unresolved. |
| 10 | NYC 311 service requests | 60 | `prospective_only` | 0 | Daily municipal-stress flow, but records mutate, taxonomies drift, and resolved fields would leak later information. |

## Recommended source-selection shortlist

1. **WSF historical pilot, conditional.** Select only after exact permission evidence or receipt of a lawful user-supplied export. Audit every quarterly PDF's public availability strictly before each historical cutoff. The fixed primary formula, if later preregistered, is the year-over-year change in leisure-route foot passengers minus the year-over-year change in the fixed Seattle/Bainbridge plus Seattle/Bremerton commuter-control basket. The one permitted sensitivity would substitute total riders for foot passengers while preserving the route sets.
2. **NOAA HMS conditional historical pilot.** Select only if original daily artifacts, timestamps, and path permissions survive audit. The fixed candidate formula is the 28-day area-weighted count of medium/heavy-smoke days over a preregistered destination basket, using only classifications produced strictly before cutoff. The one sensitivity is binary any-smoke exposure. The 2022 methodology/input change must be treated as a regime boundary.
3. **NPS or FTA prospective/control family.** Neither is historical-replay-ready from current evidence. They are defensible only for prospective vintage capture, or if an authoritative archive of preliminary/release-specific files is located.

Moonshot candidates are NASA Black Marble and MarineCadastre AIS. Black Marble is the stronger one because it is global and daily, but a future collector would need fixed resort and resident-control polygons, preregistered quality/moon/cloud/snow/fire masks, and granule production timestamps. Its proposed E0 formula is median quality-screened radiance year-over-year change over the 28 days produced strictly before cutoff, less a matched resident-control basket; the one sensitivity is the share of valid pixels with positive year-over-year change.

## Point-in-time and cutoff findings

- The 23-event readiness cohort is covered nominally by WSF, NASA, HMS, NPS, FTA, TfL, Melbourne, and NYC histories, but **zero event observations are marked strictly eligible in this lane today** because the required artifact-level availability or vintage evidence has not been completed.
- WSF cadence suggests up to 23/23 events may ultimately be usable. This is an estimate, not an eligibility determination.
- NASA and HMS also span the cohort, but collection-version and archive-regeneration risks must be resolved first.
- NPS and FTA have documented lags and revisions. Applying those lags to today's revised history would not recreate the original information set.
- MarineCadastre's evidenced 2020–2025 subset is incomplete for the full cohort, and CDOT history was not established.
- Missing or equality-at-cutoff timestamps remain ineligible under the governing strict-before rule.

## Permissions and collection disposition

All exact URLs and intended paths were recorded before any prospective request. Each candidate was represented as `abnb_alt_data.scraping_policy.ScrapeCandidate` and assessed with `assess_scrape_candidate`. Every decision returned `allowed=false`, principally because path-specific robots guidance was unclear; several candidates also had unclear terms, and NASA required unsynced authentication. No retries, identity rotation, permission workarounds, or exact-site requests were attempted.

The only potential environment variable identified is `EARTHDATA_TOKEN`. It must remain empty until the user approves NASA and confirms credential syncing through an ignored local `.env`. No credential was created, read, displayed, or logged, and this lane did not edit `.env.example` or any canonical registry.

## Negative and inconclusive evidence preserved

- **NPS:** its transparent preliminary/finalization schedule is valuable evidence against using the current API history as vintage data.
- **FTA NTD:** raw versus complete files, estimates, and a two-month lag make naive current-history replay unsafe.
- **TfL:** permissive general open-data messaging does not override more specific Santander Cycles automation restrictions or ambiguity.
- **Melbourne:** CC BY labeling does not resolve automation where the portal's own terms are undefined.
- **NOAA HMS:** the operational archive is useful, but annual-bundle regeneration dates are evidence against treating today's bundle as a contemporaneous snapshot.
- **MarineCadastre:** the unavailable AccessAIS service and partial date range prevent a readiness claim.
- **CDOT:** raw physical counts can suffer outages and flat values; no documented vintage chain was found.
- **NYC 311:** mutable resolved fields and semantic drift dominate the attractive daily frequency; any future use must exclude addresses, coordinates, BBLs, and free text and aggregate only creation-time counts.

## Authoritative primary evidence

- WSF: [ridership data](https://wsdot.wa.gov/travel/washington-state-ferries/about-us/ferries-accountability-and-service-data/ridership-data), [ridership and utilization definitions](https://wsdot.wa.gov/about/data/multimodal-mobility-dashboard/dashboard/WSF/ridership-utilization.htm), [2023 Q1 dated report](https://wsdot.wa.gov/sites/default/files/2023-04/WashingtonStateFerries-TrafficStatistics-2023Q1.pdf).
- NASA: [Black Marble official webinar](https://www.earthdata.nasa.gov/s3fs-public/2023-05/LAADS%20DAAC%20Webinar%20_Final%20Presentation_4_26_23_0.pdf), [Earthdata Login requirements](https://urs.earthdata.nasa.gov/documentation/what_do_i_need_to_know).
- NOAA: [HMS product page](https://www.ospo.noaa.gov/products/land/hms.html), [annual archive bundles](https://satepsanone.nesdis.noaa.gov/pub/FIRE/web/HMS/Smoke_Polygons/Shapefile/Annual_Bundles/), [2022 product-change notice](https://www.ospo.noaa.gov/data/messages/2022/05/MSG_20220527_1253.html).
- NPS: [visitor-use statistics dashboard](https://home.nps.gov/subjects/socialscience/visitor-use-statistics-dashboard.htm), [statistics FAQ](https://home.nps.gov/subjects/socialscience/statistics-faq.htm), [official API help](https://irmaservices.nps.gov/v3/rest/Stats/help).
- FTA: [monthly ridership](https://www.transit.dot.gov/ntd/monthly-ridership), [data-products FAQ](https://www.transit.dot.gov/ntd/ntd-data-products-frequently-asked-questions-0).
- TfL: [open-data policy](https://tfl.gov.uk/info-for/open-data-users/our-open-data), [cycling data directory](https://cycling.data.tfl.gov.uk/), [website terms](https://tfl.gov.uk/corporate/terms-and-conditions/website).
- Melbourne: [hourly pedestrian counts](https://data.melbourne.vic.gov.au/explore/dataset/pedestrian-counting-system-monthly-counts-per-hour/information/), [portal terms](https://data.melbourne.vic.gov.au/terms/terms-and-conditions/).
- MarineCadastre: [AccessAIS](https://marinecadastre.gov/accessais/), [AIS program](https://marinecadastre.gov/ais/).
- CDOT: [traffic data explorer](https://dtdapps.codot.gov/otis/trafficdata), [official open-data service](https://dtdapps.codot.gov/server/rest/services/Webapps/open_data_sde/FeatureServer).
- NYC: [311 current table](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2020-to-Present/erm2-nwe9), [2025 table update](https://opendata.cityofnewyork.us/311-service-requests-from-2010-to-present-updates/), [open-data policies](https://cityofnewyork.github.io/opendatatsm/publicpolicies.html).

## E0 stop

The lane stops here. The attached candidate registry, scorecard, archive matrix, permission audit, preflight records, gate decisions, and zero-request tiny-sample manifest are source-selection evidence only. No source family should enter E1 until the user selects it and the lead completes the canonical registry and hypothesis prerequisites.
