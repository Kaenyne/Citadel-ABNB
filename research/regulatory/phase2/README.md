# Airbnb regulatory exposure: matched inventory and performance evidence

Research cutoff: **5 September 2026**. This follow-up executes the priority inventory matching and performance-data work for Barcelona, Maui, NYC and Spain. The [original quantitative inventory](../quantification/README.md) still covers all 32 regulatory factors. This update improves selected cohorts; it does not establish a complete causal earnings forecast for every jurisdiction.

**We can now replace some assumed affected-listing counts with identifier-matched cohorts. The largest remaining uncertainty is the booked value attached to those identifiers and how much revenue Airbnb retains elsewhere.**

## What changed

| Market | New evidence | Investment-model implication |
|---|---|---|
| Barcelona | 5,910 short-minimum entire-home Airbnb ads match 5,146 distinct six-digit HUTB identifiers in the city's register | Use a deduplicated licence cohort for sensitivity analysis, subject to validity checks. The earlier 6,698 HUTB-text ads were a broader preliminary screen. |
| Maui | 4,350 short-minimum entire-home ads match 92 historical Minatoya parcels, containing 3,862 distinct nonzero unit identifiers | Model matched units, with separate 2029/2031 phases and unresolved exemptions. Ads and physical units differ. |
| NYC | Company-commissioned research reports guest-nights declining from 6.56m to 2.88m in the first post-LL18 year | A 56.1% reported activity decline is a more relevant benchmark than treating an 83% listing decline as an 83% fee-revenue loss. |
| Hawaii/Maui performance | Downloaded 19 monthly workbooks, preserving both current-year and prior-year observations | Latest published comparisons are useful, but monthly files do not reconcile to restated 2026 YTD totals. Do not splice them into a causal model. |
| Spain mitigation | Refinitiv retrieval led to Airbnb's announced $50m rural-Spain commitment over three years | Include mitigation spending as a distinct possible earnings channel. Its accounting timing and incrementality remain unknown. |

Listing counts are independently calculated from [Inside Airbnb](https://insideairbnb.com/get-the-data/) June 2026 snapshots. Registry and performance sources, methods and qualifications follow below. The full listing-ID crosswalks are in the SQLite database and the adjacent JSON files.

## Barcelona: licence matching

The June 24 snapshot contains 7,069 entire-home listings advertising a minimum stay below 30 nights. I extracted canonical six-digit HUTB identifiers, required a single identifier and a match to the city's public datastore, and counted both ads and distinct licence numbers. I did not pad ambiguous short numbers or infer matches from similar property names.

| Matching stage | Count |
|---|---:|
| Short-minimum entire-home ads | 7,069 |
| Ads with one registry-matched HUTB identifier | 5,910 |
| Distinct matched licence identifiers | 5,146 |
| Distinct matched identifiers with at least one listing reviewed during the previous year | 4,823 |
| Matched ads within 300 metres of the registered location | 5,748 |
| Distinct licence identifiers represented within that distance | 5,070 |
| Matched ads more than 300 metres away | 162 |

The 300-metre screen is an analyst sensitivity. Airbnb coordinates are approximate, and proximity does not certify legal use. A reused or inaccurate licence can still produce a match. Review activity establishes neither realized revenue nor future productivity. [Inside Airbnb data assumptions](https://insideairbnb.com/data-assumptions/).

The datastore returned all 10,718 records, including 10,622 distinct HUTB identifiers. Its resource metadata was modified May 21, 2026. It lacks an active/cancelled status field and does **not** reconcile to the previously announced 10,101 licences targeted for nonrenewal. Consequently, 5,146 is an identifier-matched candidate cohort, not a certified count of valid licences that will disappear in 2028. The registry-vintage and status reconciliation remains necessary. [City dataset metadata](https://opendata-ajuntament.barcelona.cat/data/api/3/action/package_show?id=habitatges-us-turistic), [downloaded public datastore](https://opendata-ajuntament.barcelona.cat/data/api/3/action/datastore_search?resource_id=b32fa7f6-d464-403b-8a02-0292a64883bf&limit=20000).

## Maui: parcel and unit matching

The County's historical apartment-district table reconciles to **104 parcels and 7,167 units**. Its apartment section is dated June 27, 2024; the combined document also contains a later non-apartment section, which I excluded. The county URL failed, so I used a public mirror of the county-authored PDF. This is historical inventory rather than a current legal-status register. [County-authored list, mirrored PDF](https://u.realgeeks.media/mauipropety/240725TVRList_WEB_202407252055590080.pdf), pages 1–4.

From the June 21 Airbnb snapshot, I matched contiguous tax-map identifiers to the first eight digits of the listed master TMKs. I preserved the last four digits as unit identifiers, and excluded `0000` master identifiers from distinct-unit counts. No coordinate-based parcel inference was used.

| Matching stage | Count |
|---|---:|
| Short-minimum entire-home ads in Maui County | 11,473 |
| Ads with a single matched historical parcel | 4,350 |
| Historical parcels represented | 92 |
| Distinct matched nonzero unit identifiers | 3,862 |
| Distinct unit identifiers represented by a listing reviewed in the past year | 3,045 |
| Matched ads in West Maui parcel screen, 2029 phase | 1,532 |
| Matched ads in remaining parcel screen, 2031 phase | 2,818 |
| Short-minimum entire-home ads lacking a parsed contiguous TMK | 1,358 |

The matched cohort can miss incorrectly formatted identifiers and can include inaccurate self-reported keys. The 4,350 ads include 78 with master-only identifiers, which cannot establish distinct units. Split zoning, timeshare use, parcel portions and individual exemptions require further review. The matched units are not a complete county-wide exposure estimate.

I also matched the retrieved versions of Resolutions 26-110/26-111 and the state's partial 26-129 parcel layer. Their union touches **1,452 matched ads**. These are incomplete, versioned proposal subsets. The linked PDFs do not establish that every latest amendment is incorporated, and the GIS layer covers only eight parcels. Their counts must not be subtracted as enacted exemptions. The [Council committee register](https://mauicounty.us/hlu/) describes referrals of proposed changes; creating hotel-zoning categories and referring properties for review are separate from finally rezoning those properties. [Retrieved 26-110 document](https://mauicounty.legistar.com/View.ashx?GUID=DBCD5114-742F-42ED-B617-96F81350B84E&ID=15655122&M=F), [retrieved 26-111 document](https://mauicounty.legistar.com/View.ashx?GUID=E6A46143-686C-4937-92B2-8248695FE385&ID=15655121&M=F), [26-129 GIS source](https://services1.arcgis.com/x4h61KaW16vFs7PM/ArcGIS/rest/services/maucotmk_2026_Reso26129/FeatureServer).

## Observed activity and revenue evidence

**NYC:** An Airbnb-commissioned Charles River Associates report dated December 20, 2024 reports 6.56m guest-nights in September 2022–August 2023 versus 2.88m in September 2023–August 2024: down 3.68m, or 56.1%. Guest-nights count people multiplied by nights. The LL18 result uses a simple year-over-year comparison, whereas other results in the report use synthetic controls. It therefore does not independently isolate the causal LL18 effect. Its estimated $351m lost gross host earnings includes direct taxes and is not Airbnb fee revenue. Further recapture must avoid double-counting activity already retained inside the measured city/category. [CRA report](https://news.airbnb.com/wp-content/uploads/sites/4/2025/05/The-Costs-of-STR-Restrictions.pdf), PDF pages 8–9 and 15–17.

**Maui:** In the July 2026 report, January–July demand is 1.078m unit-nights versus 0.971m, up 11.0%. Demand multiplied by the reported total rate gives approximately $695.7m versus $573.7m, up 21.3%. This is an analyst-derived all-channel lodging-value proxy, not Airbnb revenue. Total rate includes fees; it must not replace room-only ADR in the fee model. The report describes a July deduplication upgrade and historical restatement. Our monthly-file sum is 58,736 demand nights below the latest YTD figure, so we preserve vintages and withhold causal inference. Future phase-outs, wildfire recovery and other demand changes prevent attribution of these trends to regulation. [DBEDT July report](https://files.hawaii.gov/dbedt/economic/tourism/vacation-rental/hawaii-vacation-rental-performance-2026-07.pdf), [underlying workbook](https://files.hawaii.gov/dbedt/economic/tourism/vacation-rental/hawaii-vacation-rental-performance-2026-07.xlsx).

**Spain:** I refreshed 88 Refinitiv headlines and retrieved the November 2025 rural-strategy story and March 2026 eclipse-booking story. Airbnb confirms a **$50m three-year rural-Spain commitment**. An even allocation would be $16.7m a year, but that is not expense guidance or proof of incremental spending. [Airbnb announcement](https://news.airbnb.com/es/compromiso-rural-una-apuesta-por-el-turismo-descentralizado-en-espana). Reported eclipse-route rural bookings rose 210% for the specified event week; this is an event-specific booking signal, not a measured recapture rate for displaced city bookings. [Airbnb eclipse release](https://news.airbnb.com/es/el-eclipse-empuja-la-demanda-de-viajeros-internacionales-a-los-destinos-rurales/).

The removed-Spain-ad cohort still lacks a usable listing-ID crosswalk and its prior booked revenue. Aggregate INE supply declines cannot fill that gap. One Refinitiv article also describes 1.43m as homes, inconsistent with the directly downloaded INE dwelling series; I did not import that number as listing inventory.

## Updated financial sensitivities

The companion workbook contains 18 alternatives: two matched cohorts, three annual room-value assumptions and three recapture assumptions. Counts are observed identifier matches; economic and behavioral inputs remain assumptions.

`Net revenue loss = matched identifiers × annual room value per identifier × fee rate × remaining legal scope × (1 − recapture)`

Annual room value averages all matched identifiers, including zero-production units, and excludes fees and tax. This avoids adding a second arbitrary productivity discount. Remaining legal scope is 100% in the displayed illustrations; it can be reduced when exemptions are established.

| Illustrative inputs: $60k room value, 15.5% fee, 50% recapture, 70% incremental contribution | Net annual revenue loss | Adjusted EBITDA loss | FY25 revenue share | FY25 margin compression |
|---|---:|---:|---:|---:|
| Barcelona: 5,146 matched licence identifiers | $23.9m | $16.8m | 0.20% | 6.8 bps |
| Maui: 3,862 matched unit identifiers, before exemptions | $18.0m | $12.6m | 0.15% | 5.1 bps |

These are annualized **post-phase-out sensitivities**, not 2026 estimates or a probability-weighted forecast. They cover matched subsets and should not be added to earlier overlapping scenarios. The FY25 denominator is $12,241m revenue and $4,297m adjusted EBITDA. Compression recomputes both the numerator and denominator after loss, rather than using average EBITDA margin as contribution margin. [FY25 shareholder letter](https://www.sec.gov/Archives/edgar/data/1559720/000119312526048670/d58192dex991.htm).

## Guidance and the remaining bridge

The archived calls and filings do not provide a city-by-city regulatory revenue or adjusted EBITDA allowance. The latest outlook raises FY26 revenue growth to at least the mid-teens and adjusted EBITDA margin to at least 35.5%. Known historical effects may be reflected in observed bookings, but that is an inference rather than management confirmation of a quantified allowance. A realized NYC/Spain loss should not automatically be deducted again from current guidance. Future Barcelona and Maui deadlines require a multi-year model. [Latest shareholder letter](https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm), [Q2 2026 filing](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm).

The necessary transaction export is specified in [data requirements](data_requirements.md). It must include delisted properties and historical licence states. Current-listing review histories alone would suffer survivor bias. Nearby destinations receiving displaced bookings are outcomes to measure, not automatically valid untreated controls.

Refinitiv credentials are present and usable. Some targeted requests returned backend 503 errors, while the basic check, Spain search and story retrieval succeeded. Fourteen transcripts remain archived from the preceding work. No AirDNA/AirROI listing-level transaction export or credential was found. Public sources let us improve cohorts and benchmarks; they do not supply the complete transaction panel needed to finish causal revenue attribution.

## Database and reproducibility

Eight tables were added or refreshed in `data/processed/abnb_regulatory.sqlite`: Barcelona listing matches, Maui listing matches, Maui parcels, Hawaii monthly vintages, Hawaii latest-per-month observations, Hawaii YTD vintages, NYC activity benchmarks and matched-cohort scenarios. Adjacent JSON files contain the same research outputs. The crosswalks retain listing IDs and match fields without copying host names into the derived tables.

`analysis/src/pull_regulatory_phase2.py` retrieves public inputs and records URLs, checksums and failed responses. `analysis/src/build_regulatory_phase2.py` builds the matched cohorts and tables. Validation checks registry pagination, the Maui 104-parcel/7,167-unit reconciliation, demand/occupancy identities and SQLite integrity. Workbook checks cover scenario calculations, full-recapture zero loss, missing-input behavior and formula errors. All six tabs were rendered and inspected.
