# Listing destinations: before and after Airbnb disappearance

Prepared 2026-09-07 by Codex for the team. Sources: existing Inside Airbnb cohorts,
the fixed destination pilot, public property advertisements and Internet Archive.

**The history check establishes pre-existing direct-channel advertising for one
matched property, supports another direct-channel match, and finds a dated lead for
pre-existing Vrbo advertising. It does not establish any newly occurring platform
migration or a population destination split.** These are four targeted follow-ups
of the strongest earlier San Diego leads, not four representative observations.

## How many listings?

| Count | Meaning |
|---|---|
| **9 million+** | Airbnb's reported active listings worldwide, page last updated May 2026. [Airbnb](https://news.airbnb.com/about-us) |
| **1,584,439** | Distinct starting listing IDs in our September 2025 cohort: 118 markets, 35 source country labels. |
| **334,331** | Starting IDs missing at the June 2026 observations: **21.10%** over actual intervals of 268–295 days. |

Our cohort and the company count have different dates and definitions. Do not
divide them to claim global coverage. Listing IDs are not verified unique physical
properties; disappearance is not verified permanent exit. See the
[broad-panel measurement](2026-09-07_listing-churn-broad-panel.md).

## What the before/after investigation found

**SD-07 provides the strongest independently dated example.** The archived manager
page has a unit address and 3-bedroom/2-bath layout agreeing with the municipal
anchor. The earlier Expedia catalog match has the exact baseline permit and tax
identifiers. That chain supports the property identity.

| Date | Observation | What it establishes |
|---|---|---|
| **2025-09-08** | [Archived manager advertisement](https://web.archive.org/web/20250908175841/https://missionsands.com/481655/) has populated property details, booking controls and a displayed count of nine reviews. | The property was already advertised directly before the Airbnb exit interval. Reviews are manager-displayed; channel and stay dates are unverified. |
| **2025-09-25** | Last positive Airbnb snapshot in our pilot. | Airbnb still observed the listing after the direct advertisement existed. |
| **2025-12-12** | First qualifying Airbnb absence. | The two snapshots bracket apparent disappearance; the exact delisting date is unverified. |
| **2026-01-16; 2026-05-17** | [January archive](https://web.archive.org/web/20260116210511/https://missionsands.com/481655/) and [May archive](https://web.archive.org/web/20260517234403/https://missionsands.com/481655/) retain the property title and address in metadata, but rental details are unpopulated. | Metadata survived. Continued rental activity is unknown; empty fields could reflect capture/rendering problems or withdrawal. |

A JTB catalog separately claims a March 1, 2026 update. Its date is publisher-reported,
not an independently captured March listing. None of this establishes post-exit
bookings or newly joining Expedia. The direct channel was already present.

The other three cases add useful matching and timing evidence:

| Case | Before Airbnb disappearance | Afterward / current evidence | Assessment |
|---|---|---|---|
| **SD-04** | [Direct rental advertisement archived October 18, 2025](https://web.archive.org/web/20251018073623/https://www.sandiegochecklist.com/product/7br-massive-beach-retreat-sleeps-26-steps-to-ocean/), before last Airbnb presence January 5, 2026. | Current direct-page living-room photo visually matches the photo URL recorded in the Airbnb baseline exactly. Title and 7-bed/5-bath layout also agree. | Supports pre-existing direct advertising. Exact rental bundle and historical photo bytes remain unverified. |
| **SD-09** | [Syndicated Vrbo advertisement](https://agreatertown.com/san-diego-ca/1-br-condo-vacation-rental-in-san-0002277079791) claims update September 7, 2025, 18 days before last Airbnb presence. Permit, tax ID and 1-bed/1-bath layout agree. | Same syndicated record observed September 7, 2026, after first Airbnb absence December 12, 2025. | Strong lead for pre-existing Vrbo cross-listing. Claimed update date is not independent archive evidence; current bookability is unknown. |
| **SD-08** | Historical competing-channel presence unknown. | [Same-title aggregator lead](https://www.ehotelsreviews.com/spacious-4br-outdoor-kitchen-hot-tub-13778183-zh), without a verified unit identity. | Unresolved. Could be a mirror of Airbnb rather than an independent rental channel. |

**SD-04 also demonstrates why matching is difficult.** Its separate
[Vrbo-linked candidate](https://agreatertown.com/san-diego-ca/7-br-apartment-vacation-rental-0002131067840)
has a different STR permit and tax ID from the sampled Airbnb. Despite a similar
title and bedroom count, we do not accept that candidate as the same unit. The
direct-page photo match does not resolve the Vrbo conflict. The direct page also
links a different older Airbnb ID; its URL's analytics timestamp is not a creation date.

For SD-04, the October archive includes the relevant gallery URL, but retrieval of
the archived image returned 404. We compared the currently served photo bytes only.
Photo reuse and multi-unit rental bundles can create false matches even when an
image is identical.

## Work executed and its limits

- Screened baseline descriptions for **13,115 conservative persistent-absence IDs
  across ten markets**, restricted to reviewed short-stay entire homes. Of these,
  **12,967 had nonempty descriptions** and 148 were empty. **Zero** explicit
  mentions of Vrbo, HomeAway, Abritel, FeWo-direkt, Expedia, Houfy or
  Booking.com. All selected IDs were reconciled to their baseline files. This
  measures the yield of a text-based lead generator, not competitor participation.
- Queried eight fixed candidate URLs at two requested dates: **16 Wayback
  availability queries**. Two returned captures; fourteen returned none. These are
  nearest-capture queries, not complete before/after histories.
- Queried the documented exact-URL CDX index for the same eight URLs, January 2022
  through September 7, 2026: **two URLs with 16 indexed captures**, five empty
  responses, one timeout. No response reached the 100-row limit. We inspected
  **four relevant archived HTML captures** and recorded content separately from
  HTTP status. Other indexed captures are not counted as verified advertisements.
- Retrieved and visually compared three current images for SD-04. Preserved raw
  captures and hashes locally; the public ledger contains factual findings and
  source references, not redistributed property descriptions or photos.

The full index recovered a September 8 capture that the simple availability probe
had missed. Also, requesting an April 2026 capture returned an October 2025 page in
another case. **Use the actual returned timestamp and inspect the content.** No
archive result never proves that a property was absent from a platform.
[Internet Archive API documentation](https://archive.org/help/wayback_api.php),
[CDX documentation](https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server).

Some findings come from indexed or web-tool page text because direct retrieval was
unavailable. The two syndicated raw requests returned 403; the earlier Vrbo request
returned 429. Those requests were not retried. No complete historical competitor
inventory, booking feed, deed history or executed lease data was acquired.

## How this should scale

Matching every listing manually would be impractical. Use a probability sample of
disappeared IDs across markets, including cases without permits; keep the sampling
probability and unresolved cases. Generate candidates using exact unit permits or
addresses where available, then check photos, layout and location. Same-building
or title-only matches remain candidates. Audit a random subset of accepted matches
and rejected/unknown cases to measure matching error.

For each supported property identity, retain separate observations of advertising
and operating activity before and after its Airbnb exit interval:

| Other channel before | Other channel after | Interpretation |
|---|---|---|
| Present | Present | Pre-existing cross-listing continues; not new channel entry. |
| Verified absent under reliable coverage | Present | Candidate new channel entry; chronology alone does not establish why Airbnb disappeared. |
| Unknown | Present | First observed there, not necessarily newly listed there. |
| Any state | Unknown or metadata only | Post-exit operation unresolved. |

The missing input for a migration **rate** is historical competitor coverage with
reliable property identities and activity observations. Public archives help test
individual histories but are too sparse to supply reliable absence observations.
Do not estimate destination shares only among the easy-to-match cases. The original
20-case pilot's sale and residential-rental reports remain separate and unchanged;
these additional observations do not identify all remaining destinations.

## Evidence and reproduction

- [Case summary](../../data/processed/listing_platform_history/case_summary.csv)
  and [dated observation ledger](../../data/processed/listing_platform_history/timeline.csv).
- [Reviewed source input](../sources/listing_platform_history.json), including match
  conflicts, date provenance and captured-file checksums.
- [Description screen](../../data/processed/listing_platform_history/mention_screen.csv),
  [availability probes](../../data/processed/listing_platform_history/archive_probe_log.csv),
  [full archive index](../../data/processed/listing_platform_history/archive_capture_index.csv)
  and [CDX query outcomes](../../data/processed/listing_platform_history/cdx_query_log.csv).

```powershell
.\.venv\Scripts\python.exe analysis/src/summarize_platform_history.py
.\.venv\Scripts\python.exe analysis/src/screen_platform_mentions.py
.\.venv\Scripts\python.exe -m unittest discover -s analysis/tests -p test_listing_platform_history.py -v
```

The summary checks the frozen 20-case sample identity and cited raw checksums before
joining Airbnb dates. Six focused tests cover date boundaries, wrong-side nearest
captures, empty indexes and malformed inputs. Raw files stay in ignored
`data/raw/listing_platform_history/`; retain them for exact replay. Optional
`probe_listing_archives.py` and `index_listing_archives.py` reacquire uncached API
responses, which may differ as archive accessibility changes. Captured page content
requires review before updating the source ledger. No migration rate is generated.
