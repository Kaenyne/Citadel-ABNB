# Airbnb listing churn: executed San Diego and Chicago pilot

Prepared 2026-09-07. Observations end 2026-08-30. Destination research through 2026-09-07.

**Scope correction:** the [broad panel execution](2026-09-07_listing-churn-broad-panel.md)
supersedes this pilot as the headline churn analysis. This note remains the record of
the two-city method trial and the destination evidence. Its rates cannot support a
claim about Airbnb overall.

**Destination follow-up:** [before/after platform history](2026-09-07_listing-platform-history.md)
adds archived direct-channel evidence and refines the SD-04 and SD-09 leads. The
original pilot ledger below is preserved; use the follow-up for the latest evidence.

We executed the [framework](2026-09-06_listing-churn-and-destinations-framework.md)
using the team's actual snapshot catalog and reacquired the underlying listing records.
The conservative 90-day persistent-absence result is **7.97% in San Diego after limited
permit-based linkage**, and **8.73% in Chicago at the listing-ID level**. Using only the
team's partial-coverage flags gives **14.78% and 12.14%**, respectively. The spread is a
material data-coverage sensitivity, not a confidence interval.

The destination pilot traced one property to an MLS-reported sale and another to an
MLS-reported residential rental. It also found a matching other-platform catalog entry
and three additional leads. It does **not** establish a market-wide sold/converted/migrated
breakdown or confirm new migration to a competing platform.

## 1. Inputs actually used

- Team source: commit [`df833f5f3980078beef09c1327940bfa58d57acf`](https://github.com/Kaenyne/Citadel-ABNB/tree/df833f5f3980078beef09c1327940bfa58d57acf),
  `data/processed/inside_airbnb_city_snapshots.csv`. We selected every catalogued San Diego
  and Chicago snapshot beginning September 2025; no dates were selected based on a desired
  measured churn outcome. Source catalog hash and per-file hashes are saved.
- **21 listing files:** 11 San Diego and 10 Chicago. All raw row counts exactly matched
  the team's catalog. The analysis verifies gzip integrity on acquisition, required
  fields, unique string IDs, checksums and count reconciliation.
- **8,441 current San Diego municipal license records**, captured 2026-09-07 from the
  [city's STRO register](https://data.sandiego.gov/datasets/stro-licenses/).
  The dated raw register is retained locally; the download URL changes over time.
- Property-specific public rental, sale, operator and platform pages for the 20-case
  investigation. The [case ledger](../../data/processed/listing_churn_execution/destination_review.csv)
  records sources, event dates, match evidence and limitations.

These are two selected markets, not a representative sample of Airbnb globally. San
Diego was selected for usable permit linkage; Chicago is a comparison with no equivalent
property-ID correction in this implementation. Neither uses AirDNA booking or transaction
data, a comprehensive deed feed, or a complete Vrbo/Booking property panel.

## 2. Measured rates

The denominator is the fixed cohort of baseline listing IDs. A listing qualifies for
endpoint persistent absence only if it is absent at the endpoint, has at least two valid
negative observations spanning at least 90 days **from its first observed absence**, and
has no subsequent positive observation. All positive observations reset the clock,
including observations inside a partial or otherwise excluded file. Returns can happen
after the observation endpoint, and returns between snapshots may be missed.

| Measure | San Diego | Chicago |
|---|---:|---:|
| Baseline scrape completed | 2025-09-25 | 2025-09-24 |
| Endpoint scrape completed | 2026-08-30 | 2026-08-30 |
| Elapsed days | 339 | 340 |
| Baseline listing IDs | 13,162 | 8,660 |
| Original IDs absent at endpoint | 3,035 (23.06%) | 1,941 (22.41%) |
| Original IDs present at endpoint | 10,127 | 6,719 |
| Additional baseline IDs with supported replacement ID at endpoint | 220 | Not estimated |
| Persistent absence, original IDs, conservative coverage | 1,197 (9.09%) | 756 (8.73%) |
| Persistent absence, after available permit linkage, conservative coverage | **1,049 (7.97%)** | **756 (8.73%); IDs only** |
| Pending persistence, after available linkage | 1,766 | 1,185 |
| Persistent absence, after available linkage, team flags alone | **1,946 (14.78%)** | **1,051 (12.14%); IDs only** |

San Diego reconciles as `13,162 = 10,127 original IDs + 220 supported alternative IDs
+ 1,049 persistent absences + 1,766 pending`. Chicago reconciles as
`8,660 = 6,719 original IDs + 756 persistent absences + 1,185 pending`.
The 220 replacements are among all missing IDs, including cases that would otherwise
be pending; they should not simply be subtracted from the original persistent count.

Publication audit correction (September 7): one proposed replacement was already
present in the starting cohort under another permit. It is now excluded from
replacement evidence. The conservative persistent count and reviewed-home sample
are unchanged; the all-listing team-flags count rises from 1,945 to 1,946.

**Interpretation:** these are endpoint prevalence measures of sustained absence from
the observed snapshots. They are not annual first-exit probabilities, confirmed permanent
property exits, gross annual churn hazards, or official Airbnb active-listing churn.
There is no valid basis to annualize them with a compound-rate formula. Licensing
linkage reduces one known source of false exits but does not resolve every physical unit.

### Productive-supply proxy

We also evaluated a baseline-only cohort of entire homes/apartments with minimum stay
below 30 nights and at least one review in the preceding 12 months. This screens for
some recent short-stay activity; it does not establish bookings or revenue.

| Baseline reviewed short-stay homes | San Diego | Chicago |
|---|---:|---:|
| Cohort size | 7,037 | 4,071 |
| Original ID absent at endpoint | 1,321 (18.77%) | 764 (18.77%) |
| Supported alternative Airbnb ID at endpoint | 184 | Not estimated |
| Conservative persistent absence, after available linkage | **387 (5.50%)** | **297 (7.30%); IDs only** |
| Team-flags-only persistent absence, after available linkage | 738 (10.49%) | 404 (9.92%) |
| Conservative persistent cases' share of baseline reviews | 4.22% | 7.61% |

In San Diego, the disappearing inventory appears less productive on this review proxy
than a raw count suggests. Reviews are not booking value, and their weighting is not a
revenue-loss estimate. The Chicago comparison also lacks San Diego's permit correction.

## 3. Coverage and identity checks that change the answer

**Coverage policy.** The team flags Chicago's March and April 2026 files as partial.
But the problem is broader than those flags: San Diego falls from 13,095 records in
January to 11,427 in February, remains around 11,700 through May, then returns to 13,225
in June. Its discovery-source mix changes sharply in the same interval. Chicago shows
similar collection changes. These patterns suggest a collection discontinuity, but do
not prove that every decrease was a collection error.

The conservative sensitivity therefore disallows *negative* evidence from every
February-May 2026 file in both cities, while retaining every observed positive. This
retrospective sensitivity is deliberately broader than the team flag and could exclude
real exits or delay their classification. The team-flags-only specification is also
reported, so the result does not conceal this judgment. Neither specification supplies
a statistically identified lower or upper bound on actual economic churn.

**Actual dates.** Observation dates are the maximum `last_scraped` date within each
file. Several nominal May files finished on June 6, leaving only 85 days to August 30.
A case first missing there cannot meet the 90-day threshold. This completion convention
is conservative for first absence within a scrape window, but individual positive
records may have been observed earlier than the file completed.

**Discovery source.** `source = previous scrape` is retained. Inside Airbnb's
[data dictionary](https://docs.google.com/spreadsheets/d/1iWCNJcSutYqpULSQHlNyGInUvHg2BoUGoNRIGa6Szc4/edit?usp=sharing)
describes those listings as reconfirmed available, not unverified copies. Their current
timestamps also support retaining them. Source-mix changes are a QA diagnostic.

**Limited property linkage.** A replacement requires one unambiguous San Diego STRO
permit in the baseline record, uniqueness of that permit within the baseline and
candidate snapshot, matching room type, and distance at most 300 meters. The radius
allows for [Inside Airbnb's displaced coordinates](https://insideairbnb.com/data-assumptions/).
This is a supported continuation candidate, not a fully validated property crosswalk:
mistyped/reused permits, multi-unit offers, changed permits and duplicate baseline IDs
remain risks. We do not use host ID alone or a generic title to merge properties.

**Threshold sensitivity.** Original-ID persistent counts at 30/60/90/180 days under
conservative coverage are San Diego `2,712 / 1,197 / 1,197 / 1,197` and Chicago
`1,745 / 756 / 756 / 756`. Equality at 60-180 days reflects the long observation gap
after excluding suspect negative evidence. It is not evidence that the threshold is
economically irrelevant. The full snapshot audit and both policies are in
[cohort_summary.csv](../../data/processed/listing_churn_execution/cohort_summary.csv)
and [snapshot_quality.csv](../../data/processed/listing_churn_execution/snapshot_quality.csv).

## 4. Where the listings went: actual case investigation

We selected a simple random sample of **20 cases from 208 eligible San Diego IDs**:
conservative persistent absence after permit linkage, baseline reviewed short-stay
entire homes, and a unique baseline STRO permit. Seed `20260907`; the sample was fixed
before web searches. The 208 are only part of the 387 productive-proxy persistent cases,
which themselves are part of 1,049 all-listing persistent cases. Searchability and permit
availability create selection limits.

| Evidence found | Cases | What the evidence establishes |
|---|---:|---|
| MLS-reported completed sale | 1: SD-20 | Sale reported 2026-07-30; subsequent property use unknown |
| MLS-reported residential rental | 1: SD-01 | Rental reported completed 2026-02-03; lease duration unverified |
| No dated sale/rental outcome established | 18 | Unresolved remains explicit |
| Within those 18: matched other-platform catalog record | 1: SD-07 | Same unit marketed on Expedia; live availability and new migration unverified |
| Within those 18: other-platform/direct leads | 3: SD-04, SD-08, SD-09 | Follow-up leads with incomplete identity, timing or primary-page verification |
| Confirmed newly migrated to another platform | 0 established | No complete before-and-after platform evidence; this is not a zero migration estimate |

**SD-20: reported sale.** The baseline permit links to the exact advertised sale address;
bedroom/bathroom counts and approximate location agree. Redfin reports an SDMLS closed
sale dated July 30, 2026, corroborated by the local closing table. First qualifying
snapshot absence was December 12, 2025. The seven-month gap does not establish that sale
caused delisting. No deed inspection or post-sale occupancy classification was performed.
[Sale source](https://www.redfin.com/CA/San-Diego/3540-Quimby-St-92106/home/5346170),
[closing table](https://www.sdlookup.com/Closings-92106-Point-Loma).

**SD-01: reported residential rental.** The unique municipal permit maps to the exact
unit address, with matching three-bedroom/two-bathroom layout and location. The unit was
first absent January 23, 2026; Zillow records a residential rental advertisement January
24 and removal February 3. The MLS-syndicated listing explicitly reports rented on
February 3. This supports residential-rental use, but an executed lease and its duration
are not observed, so a confirmed 12-month conversion is not claimed.
[Rental status](https://www.rereader.com/rentals/2307-Meade-Ave-San-Diego-CA-92116-427221294),
[listing history](https://www.zillow.com/homedetails/2307-Meade-Ave-San-Diego-CA-92104/2054746633_zpid/).

**SD-07 and SD-09: evidence of other-channel offers, not proof of migration.** SD-07's
Expedia entry matches both permit and tax identifiers, three bedrooms and the municipal
address. A direct operator page also exists, but availability did not load. SD-09 has a
Vrbo-syndicated lead matching both identifiers and unit details; the primary Vrbo request
returned HTTP 429 and was not retried. Its old Airbnb description already mentions other
platforms. These may be pre-existing cross-listings. Search crawl ages sometimes conflict
with opened-page ages, so access date is not used as an event date.
[SD-07 platform record](https://www.expedia.com.hk/en/San-Diego-Hotels-Santa-Barbara-Loft.h112381138.Hotel-Information),
[SD-09 lead](https://agreatertown.com/san-diego-ca/1-br-condo-vacation-rental-in-san-0002277079791).

**Negative controls in the investigation.** A similar-name studio rental had a different
address and was not accepted. A film studio at the same building address as a loft was
not treated as a conversion of the accommodation unit. Old Airbnb search results were
not counted as current reactivations. This prevents a search result from becoming an
unsupported destination label.

The current register matches **80/208 eligible cases and 8/20 sampled cases**, including
both the reported sale and rental. A current license is neither actual operation nor a
destination, and registry updates may lag events.

The pilot's findings are **detection counts**, not estimated population shares. There
are too many unresolved cases and no measured search/classification sensitivity to use
`1/20` as the share of city exits that sold or converted. A sale event can coexist with
any subsequent use; the ledger preserves those axes separately.

## 5. Decision use and remaining uncertainty

The executed evidence rejects treating roughly 23% missing IDs as 23% lost accommodation
supply. Replacement IDs, data coverage and unfinished follow-up materially reduce or
delay the apparent exits. The San Diego activity-proxy result is lower still.

The data support a monitored local persistence metric and real destination examples.
They do not yet support a single validated economic churn point estimate or a competitive
migration share. The most valuable next input is dated unit-level cross-platform
coverage and residential transaction/rental history for a larger, stratified sample,
including permit-missing cases. Repeated comparable Airbnb snapshots are also needed to
resolve pending exits and later returns. Rechecking the 20 fixed cases should preserve
unknowns and retain each observation date rather than overwrite history.

## 6. Reproduce this run

Python standard library only; tested with Python 3.13.14. Git must be on PATH. Use the
shared repository and the immutable source commit, rather than a moving branch name:

```powershell
git fetch origin
python analysis/src/fetch_listing_churn_inputs.py --source-rev df833f5f3980078beef09c1327940bfa58d57acf --markets san-diego chicago --start 2025-09-01 --registry-date 2026-09-07
python analysis/src/execute_listing_churn.py --registry-date 2026-09-07
python analysis/src/summarize_listing_destinations.py
python -m unittest discover -s analysis/tests -p "test_*churn*.py" -v
python -m unittest discover -s analysis/tests -p "test_listing_destinations.py" -v
```

The city register URL is current-state only. A future exact replay needs the cached
2026-09-07 register and metadata; the downloader refuses to relabel today's register as
historical. Inside Airbnb may retire public files; preserve this run's raw captures.
Raw files, full descriptions, exact address matches and granular outcomes are under
`data/raw/listing_churn_execution/` and are Git-ignored. Public outputs contain aggregates,
case IDs, short factual evidence summaries and source links. Manual web evidence is in
`destination_evidence.json` and is never overwritten by the numerical rerun. Online
research is not claimed to be automatically reproducible from an unchanged search index.

Validation covers exact count reconciliation across all 21 files; original and linked
cohort partitions; 89/90-day boundaries; scrape completion timing; returns inside partial
files; ambiguous licenses; replacement IDs; and missing/duplicated/undated evidence cases.
