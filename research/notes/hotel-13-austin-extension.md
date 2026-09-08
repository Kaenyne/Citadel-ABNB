# Austin hotel supply frame for the 13-market extension

As of September 7, 2026. Austin is included in the user-confirmed original 13-market listing panel. This work covers Austin only; the active scope is `analysis/config/hotel_markets_13.csv`.

**Obtained an official property-level operating-license frame with recorded capacity: 216 active hotel, motel and B&B licenses representing 29,080 units/rooms.** The City of Austin dataset was updated September 7, 2026 at 11:02:35 UTC. This is municipal license coverage, not a metro census or an Airbnb booking dataset. [City of Austin registry](https://data.austintexas.gov/Public-Safety/Hotel-Motel-and-B-B-Licenses/av8n-pmdr)

| Source license type | Active licenses | Recorded units/rooms |
|---|---:|---:|
| Hotel | 168 | 25,424 |
| Motel | 43 | 3,636 |
| Bed and Breakfast | 5 | 20 |
| **Total active** | **216** | **29,080** |

The preserved file contains 225 unique license IDs and 30,119 recorded units/rooms across all statuses. Excluded from the active subtotal: six denied records with 535 units/rooms, one expired record with 142, and two suspended records with 362. All capacity fields parse as positive integers. Totals reconcile to status/type groups and the API metadata row count. No STR license types occur in this extract.

**This is not yet boutique/independent TAM.** The source's `Hotel` category contains Firehouse Hostel and Holly House HOA. Ownership, brand affiliation, actual room configuration and boutique positioning remain unverified. The 15 active Hotel-classified records with fewer than 50 units/rooms sum to 344, but that is only a size-based screening subset.

The raw `ADDRESS` field combines property names and addresses. All 225 strings are distinct, which does not prove distinct physical buildings. Tommie Austin and Thompson Austin share an address and have separate names, license IDs and room counts; preserve both until a physical-property/room-allocation crosswalk establishes their relationship. No speculative address deduplication was applied.

`NUMBEROFUNITSROOMS` records licensed capacity, not daily sellable capacity or rooms allotted to Airbnb. `ISSUEDATE` is not a hotel opening or Airbnb onboarding date; 191 records share December 31, 2025. Active license status alone does not establish current operation, bookability or demand. Physical hotel count, independent rooms, boutique rooms, Airbnb inventory and bookings remain missing rather than zero.

The inherited Visit Austin figure now has a more specific primary reference and explicit vintage: **early 2026, 51,000+ hotel rooms citywide and 15,000+ downtown**. The source does not reconcile its destination boundaries with municipal license coverage or define a metro boundary. Do not sum this headline with the registry, add downtown to citywide, or interpret 29,080 / 51,000 as a measured coverage ratio. A known large hotel named in the FAQ, JW Marriott, was not resolved to a registry record in this bounded review; completeness remains unverified. [Visit Austin Meeting FAQ](https://www.austintexas.org/meeting-professionals/why-austin/meeting-faq/)

This reuses the earlier `HOTEL-AUS` capacity claim; the explicit vintage and registry are the extension. Jessie's existing Austin `mydx-h5dy` data concern STR licenses and are a different population. A search of visible frozen team text found no `av8n-pmdr` or this hotel-registry title; the parent's independent URL check also found no match. That is bounded overlap verification, not certification of unshared files.

Texas hotel-tax definitions also cover homes, apartments and other short-term lodging. Accordingly, hotel-tax registrations and receipts were not relabeled as conventional hotel properties or Airbnb hotel production. No records request, form, outreach or purchase was made. [Texas Comptroller FAQ](https://comptroller.texas.gov/taxes/hotel/faq.php)

The useful next step is a property/brand classification and identity match to Airbnb, followed by actual channel production. This frame supplies names, addresses, ZIP codes, license status and capacity for that work. It cannot establish that supply joining Airbnb generates incremental demand.

Files:

- Source ledger: `research/sources/hotel_13_austin_sources.json`.
- Preserved source CSV and metadata: `data/raw/hotel_13_market_extension/austin/`.
- Machine-readable totals: `summary.json` in that directory.
- Active license records: `active_license_records.json`; size-screen candidates: `small_hotel_license_candidates.json`.
- Reproduction: run `summarize_austin.py` in that directory against the preserved inputs. It does not re-download or alter earlier analyses.

Three successful source-download hashes were verified independently by the parent. Direct Visit Austin HTML download returned HTTP 403; its complete FAQ text was read with the web tool. The dataset catalog's older August timestamp was superseded by the actual September 7 API metadata saved with the extract.
