# Airbnb listing churn and destinations: measurement framework

Prepared 2026-09-06. Local research branch: `wollberg7/listing-churn-framework`.

**Decision:** determine whether Airbnb is losing productive accommodation supply, whether
that supply continues serving travelers elsewhere, and how much of the observed change
is inactive inventory, temporary pauses, or listing-ID replacement.

**Recommendation:** measure both listing-ID disappearance and persistent property-level
Airbnb exit. Follow the same physical rental unit across listing IDs and platforms, then
attach dated evidence about its subsequent use and any sale. A disappeared listing is
an investigation candidate. It does not by itself establish a sale, competitive migration,
or permanent exit from short-term rental supply.

**Execution update, 2026-09-07:** the [broad execution](2026-09-07_listing-churn-broad-panel.md)
now covers the full 13-market team history and the wider public quarterly archive.
It supersedes the two-city pilot as the headline rate analysis. The
[original pilot](2026-09-07_listing-churn-execution.md) retains the fixed 20-case
destination investigation and its evidence ledger. A unique
population property-churn rate and a representative destination breakdown remain
unidentified. The original aggregate audit below is retained with its original commit;
the execution uses a newer pinned team commit. Measurement thresholds remain research
design choices, not Airbnb definitions or validated classifier performance.

## 1. What the existing data can support

The audit reads the team's Inside Airbnb supply branch at immutable commit
[`620f1ee`](https://github.com/Kaenyne/Citadel-ABNB/tree/620f1ee4691d06df964bd73ce84cc35e8766e4a0).
It validates the aggregate counts, reconstructs disappearance from counts rather than
rounded retention, and joins both endpoint coverage flags. It does not merge that branch.

| Available input | Observed scope | Use and limitation |
|---|---|---|
| `inside_airbnb_city_snapshots.csv` on the supply branch | 168 snapshots, 13 markets; 41 source-flagged partial snapshots | Market coverage screen. The flag is a heuristic, not ground truth. |
| `inside_airbnb_like_for_like.csv` on that branch | 258 pair rows, including 103 designated year-ago comparisons | ID disappearance and count reconciliation. Aggregate rows cannot identify which property exited or where it went. |
| Latest designated year-ago pair in each market | 13 comparisons, 313-345 days apart; Austin has a flagged starting snapshot | Report actual dates and intervals. Neither exact annual churn nor a global Airbnb estimate. |
| `data/processed/market_summary_2026.csv` on main | Current market aggregates | Describes mix; one aggregate snapshot does not identify gross exits. |
| `data/manifests/inside_airbnb_download_log.csv` on main | 75 successful listing-file records across 75 markets, one date per market, in the inspected log | Provenance and reacquisition URLs. The README's broader 120-market inventory is not a 120-market historical listing panel available in this checkout. |
| `data/manifests/municipal_download_log.csv` | Includes municipal STR registry acquisitions | Potential license-to-unit links, subject to each registry's actual fields and history. Raw files referenced in these manifests are not present locally. |
| Common Crawl branch, commit `7eb638e` | Archived-page panel and conditional re-fetch statistics | Supplemental dated evidence that a page existed; not a population churn denominator. |

Examples reconstructed from the latest comparison for each city:

| Market | Actual interval | Baseline IDs | IDs missing at endpoint | ID absence | Interpretation |
|---|---|---:|---:|---:|---|
| Los Angeles | 2025-09-01 to 2026-08-10, 343 days | 45,886 | 15,164 | 33.05% | Candidate disappearance; both endpoints still require coverage validation. |
| Rome | 2025-09-14 to 2026-08-25, 345 days | 37,652 | 6,651 | 17.66% | Same limitation; no sale or other-platform attribution. |
| Austin | 2025-09-16 to 2026-08-25, 343 days | 10,533 | 3,140 | 29.81% | Reject as a churn estimate: starting snapshot is flagged for partial scope. |

The full 13-market audit is in
[`listing_churn_existing_data_audit.csv`](../../data/processed/listing_churn_existing_data_audit.csv).
Its `property_churn_rate`, `sale_share`, and `other_platform_share` fields are intentionally
blank, meaning **not identified**, not zero.

Two corrections matter before extending the existing team work:

1. Its scope screen flags counts below 80% of the local maximum within +/-200 days.
   That uses future observations and can confuse real supply contraction with missing
   coverage. Keep it as a retrospective diagnostic; a missing flag does not clear a
   market. Its price-driven selection of some year-ago pairs should also not determine
   a dedicated churn study's time windows.
2. The Common Crawl note describes survival among re-fetched pages at varying ages of
   at least 60 days. Repeated re-fetches are not independent properties, and these are
   not fixed one-year cohorts. Excluding crawls because observed removals are below 2%
   also selects on the outcome. Do not translate that table into annual churn or treat
   the difference from Inside Airbnb as a measured economic result. Validate page
   templates against independent live/dead controls and use positive archive evidence
   for case histories. Non-capture is unobserved, not delisted.

## 2. Define the unit, denominator, and exit clock

Track three separate units: **Airbnb listing ID**, **physical rentable unit**, and
**host account**. A manager with several listings is not several independent hosts;
a building or parcel with several apartments is not one rentable unit. Whole-home and
room-level inventory need separate accounting to avoid treating overlapping offers as
independent homes.

Start with all verified Airbnb-present units in a fixed market boundary at the baseline.
Publish an all-present result and separate pre-specified activity cohorts:

- Recent Airbnb booking activity, if channel-specific booking records are available.
- Otherwise, recent reviews and offered nights as clearly labeled activity proxies.
- No recent activity signal, reported separately; absence of reviews is not proof of
  zero bookings. Never define baseline eligibility using future survival or reviews.

AirDNA's enterprise documentation distinguishes available/reserved activity from site
presence and warns that booking estimates do not perfectly distinguish booked from
blocked nights. Its documentation also says calendars do not identify the actual booking
channel. Preserve vendor definitions and versions rather than assuming an "active" flag
means the same thing across products. [S-CHURN-04](https://enterprise-help.airdna.co/en/articles/8185673-property-performance-data)

For a matched, comparable pair of snapshots:

```text
ID absence(a,b) = IDs in a but not b / IDs in a
ID count(b) = ID count(a) + IDs new to the pair - IDs absent at b
```

"New to the pair" may be an old listing reappearing. Net supply growth does not identify
gross churn: heavy exits and heavy additions can offset each other.

**Proposed persistent-exit rule:** flag first absence at a valid snapshot, then require
at least two valid absent observations spanning at least 90 days from that first absence,
no positive Airbnb-presence observation between them, and no verified replacement
Airbnb ID for the unit. Intervening valid snapshots must agree. Bad or missing snapshots
provide no negative evidence. Report this as an *observed 90-day persistent exit*, not
proof of continuous absence between observations or permanent retirement.

Keep `last_present_date`, `first_absent_date`, `confirmation_date`, and `as_of_date`.
The onset lies in `(last_present_date, first_absent_date]`; do not invent a precise
departure date. Use actual calendar days. Quarterly data cannot support precise monthly
hazards. If an onset interval crosses the reporting-window boundary, its period assignment
is unresolved. Recent candidates without sufficient follow-up are pending, not confirmed.

For a fully ascertained baseline property cohort and a specified reporting window:

```text
Persistent property exit rate = sum(w_i * E_i) / sum(w_i)

E_i = 1 if the unit's first exit episode beginning in the window meets the rule
w_i = 1 for a census; otherwise its documented sampling/representation weight
```

Use observed 12-month cohorts with follow-up beyond the endpoint, rather than multiplying
a monthly rate by 12 or annualizing a 313-day ID-disappearance rate. Report sensitivity
at 30/60/90/180 days where cadence permits, plus subsequent return rates. A return after
a confirmed episode is a reactivation; it does not erase the historical episode. Store
both the originally available label and later revisions. First-exit incidence and the
share still absent at the horizon are different outputs.

For incomplete ascertainment, let `N` be the baseline population, `D` supported persistent
exits, and `U` properties whose churn status remains unresolved. Report `[D/N, (D+U)/N]`
as an identification range, conditional on accurate classifications of the resolved units.
Use weighted counts for a sample. It is not a statistical confidence interval and cannot
repair undetected scrape errors. Do not quietly drop `U` from the denominator.

## 3. Coverage validation precedes every churn label

Accept a negative observation only after checking: successful and structurally complete
ingestion, stable listing-ID schema, consistent geographic boundary and filters, duplicate
IDs, listing-type/geographic composition, expected sentinel listings, and publisher metadata.
Maintain both acquisition time and snapshot/event time. Retain file hashes and source URLs.

Abrupt broad-based disappearance, a changed field definition, or a count drop that later
reverses opens a coverage investigation; it is not an automatic economic exit. A genuine
regulatory contraction can be abrupt too. Prefer independent coverage evidence, retain
the ambiguity when unresolved, and do not use a count rule as the sole classifier.

Inside Airbnb explicitly warns that unavailable calendar nights combine booked and blocked
dates. A zero-availability calendar or a failed page fetch therefore does not establish
exit. Airbnb also allows temporary or indefinite unlisting and later relisting.
[S-CHURN-01](https://insideairbnb.com/data-assumptions/),
[S-CHURN-02](https://www.airbnb.com/help/article/476)

## 4. Build a property crosswalk before attributing destinations

Resolve old and new Airbnb IDs first, then join other STR channels, rental advertisements,
licenses, and property transactions. The crosswalk needs validity dates: the same platform
ID can change manager, and the same physical unit can receive a new ID.

| Match evidence | Treatment |
|---|---|
| Verified exact address **and unit**, or a property-specific registration identifier with compatible unit attributes | Strong anchor; check uniqueness and the identifier's scope. |
| Multiple distinctive interior-photo matches plus compatible bedrooms, bathrooms, room type and location | Candidate for human adjudication; validate on a labeled set before automating. |
| Management-company unit code or explicit links between platform pages | Useful corroboration after confirming the code identifies this unit. |
| Similar title, host name, price, or nearby coordinates alone | Insufficient; retain as a candidate, not a link. |
| One building/parcel, several possible apartments or shared registration number | Ambiguous until unit identity is resolved. |

Inside Airbnb reports location displacement of roughly up to 150 metres and notes that
units in one building can appear scattered. Treat a geographic radius as candidate
generation, not identity proof. AirDNA describes combining proximity with multiple
attributes when matching platforms; a vendor property ID still needs validation and a
dated platform crosswalk for this use case.
[S-CHURN-01](https://insideairbnb.com/data-assumptions/),
[S-CHURN-03](https://enterprise-help.airdna.co/en/articles/8185678-how-airdna-identifies-duplicate-listings)

Store match method, evidence references, conflicts, reviewer decision, and confidence
separately from churn status. Confidence scores must be calibrated against reviewed true
and false matches; an unvalidated similarity score is not a probability. Prefer unresolved
cases to forced matches, especially in apartment buildings. Measure match precision and
recall by property type and market, not just for the easy matched subset.

## 5. Answer "where did it go?" using dated states and separate events

Record destinations at fixed horizons, initially 90 and 180 days after first observed
absence, subject to evidence availability. Preserve later updates and observation gaps.

**Operating state:** Airbnb present; other STR only; long-term rental only; mixed STR/LTR;
confirmed non-rental use; or unresolved. Attach a channel set such as `{Vrbo, direct}`.
If the complete use state is unknown, keep it unresolved and retain any positive channel
evidence separately. Do not force "only" when exclusion of alternatives is unsupported.

**Event flags:** marketed for sale, completed sale/ownership transfer, management change,
permit lapse/revocation, or verified renovation. These can overlap operating states.
In particular, **sold** and **on Vrbo** are not mutually exclusive destinations.

| Proposed answer | Minimum evidence and distinction |
|---|---|
| Returned to Airbnb / new Airbnb ID | Positive dated observation of the same unit under the original or a verified replacement ID. Distinguish an ID replacement from a later reactivation. |
| Continuing on Vrbo, Booking.com or direct booking | Verified unit match plus a dated, functioning accommodation offer after Airbnb exit. Distinguish bookable offer from an actual reservation or stale advertisement. |
| Newly appeared on another platform | Above evidence **and adequate pre-exit coverage** showing it was not already there. Without that, report "observed off Airbnb afterward; start unknown." |
| Dropped Airbnb but retained an existing channel | Other-channel presence before and after, plus supported Airbnb exit. This is channel contraction; it does not prove bookings migrated. |
| Advertised for long-term rental | Exact-unit rental offer with a long-term lease proposition and date. A high Airbnb minimum stay alone is insufficient. |
| Converted to occupied long-term rental | Positive lease/occupancy or other direct confirmation. A rental advertisement alone proves marketing, not a signed tenancy. |
| Marketed for sale / sold | Separate for-sale advertisement from dated closed sale/deed evidence for the matched unit. Distinguish a sale from non-sale title transfers and record transaction versus recording date. Continue tracking use after sale. |
| Renovation, owner use, retirement from renting | Direct supporting evidence; no STR, rental or sale match is simply unknown. |
| Regulation-related event | Matched-unit permit/enforcement record. Expiration alone does not prove conversion, a completed exit, or causation. |

For sale attribution, use county/municipal recorded transactions or a licensed property
transaction feed. Boston, for example, publishes parcel/property resources and sales
information; access to a city resource does not guarantee current transaction coverage
or an exact listing-to-unit link. Licensing and field coverage must be established for
the selected pilot markets. [S-CHURN-05](https://www.boston.gov/departments/assessing/property-data-and-information)

The event record should support an auditable answer such as:
"Unit exited Airbnb within this date interval; its matched Vrbo offer was already live
beforehand and remained offered 180 days later; a subsequent sale is recorded; the buyer's
actual occupancy use remains unknown." Temporal association does not establish why the
host left or where bookings went.

For confirmed exits, calculate horizon destination shares using **all** confirmed exits
as the denominator, including unresolved destinations. Report verified other-channel
presence separately when exclusive use is not established. Sales-event shares can overlap
destination shares and must not be stacked in the same 100% chart. Churn-status uncertainty
and destination uncertainty are separate fields.

## 6. Minimum data contract and validation pilot

| Table | Grain and essential fields |
|---|---|
| `snapshot_coverage` | Market/source/snapshot: boundary version, observation/acquisition dates, row count, status, QA decision, evidence, hash. |
| `listing_observations` | Source/platform listing ID/date: presence vs not observed vs verified absence, unit attributes, activity proxies and their definitions, source reference. Store IDs as strings. |
| `property_crosswalk` | Listing ID to internal unit ID, valid-from/to, match anchors, method, confidence, reviewer, unresolved alternatives. |
| `property_events` | Unit/event: last present, first absent, confirmation, as-of date, episode, event type, sale/rental/channel evidence, uncertainty. |
| `followup_evidence` | Unit/source/check date: search coverage and result, dated fact, event/publication/acquisition times, link or permitted stored evidence, reviewer, license. A failed search is not a verified negative. |
| `cohort_results` | Cohort/window/horizon: baseline count, confirmed exits, unresolved churn status, fate counts, unresolved fate, reactivations, weights, QA and match performance. |

The missing requested source plugs into these tables rather than changing the estimator.
If it is an AirDNA export, request the property file, monthly file, dated listing-to-channel
crosswalk, and documentation of delisted-record retention; an active-only export can erase
the very cohort being studied. If it is Inside Airbnb, obtain all comparable historical
listing snapshots plus identifiers, not just city totals. If it is a property-sales source,
it supplies events and unit anchors but cannot measure Airbnb exit by itself.

Pilot sequence:

1. Pick markets where repeated listing coverage **and unit-level destination evidence**
   overlap. Begin with the team's existing markets; establish actual registry and sales
   availability before selecting them. Keep geography fixed and stratify urban/regulatory,
   seasonal and professional-host exposure. Do not extrapolate an urban sample globally.
2. Obtain historical raw listing snapshots referenced by the team, verify hashes and schema
   versions, then build the candidate exit ledger. Recover exact ID sequences before
   estimating persistence, reactivation, or ID replacement.
3. Draw a reproducible stratified random sample of disappearance candidates and retained
   controls, recording seed, inclusion probabilities and host clusters. A starting workload
   of 400 candidates and 100 retained controls is a planning assumption, not a precision
   guarantee. Effective sample size and clustered intervals determine final sample needs.
4. Search all selected cases with the same source list and follow-up windows. Record failed
   checks and unresolved cases. Adjudicate matches blind to the desired investment thesis;
   independently review a subset of matches, nonmatches and proposed sales.
5. Use controls to detect coincidental sales, baseline multi-homing and matching errors.
   Set acceptable precision after the pilot; do not manufacture an attribution model from
   weak labels. Bootstrap at host level within market/stratum for sampling uncertainty,
   and separately show missing-data and match-error sensitivity.
6. Publish a dated evidence ledger, cohort flow table, destination table, reactivation curve,
   and coverage/matching report. Confirm that snapshot counts reconcile and that every
   classified exit has qualifying follow-up and evidence.

Keep address/unit crosswalks, ownership details and licensed raw records in private local
storage or the team's private Drive. This shared repository is public; commit aggregate
outputs, documented methods and permitted provenance rather than granular household files.

## 7. Translate churn into the Airbnb decision

Report listing-ID exits, property exits, active-property exits and pre-exit activity-weighted
exits side by side. Losing a dormant listing and losing a highly booked home have different
economic significance. Use **pre-exit Airbnb-channel** nights or GBV where available;
all-channel revenue or scrape availability cannot supply that weighting silently.

```text
Nights-weighted exit exposure = baseline Airbnb nights from exiting units
                               / baseline Airbnb nights from all cohort units

Potential lost Airbnb nights = counterfactual Airbnb nights from exiting units
                              * (1 - share recaptured by other Airbnb listings)

Potential revenue impact = lost nights * comparable Airbnb ADR * effective revenue/GBV
```

These are scenario bridges, not automatic causal estimates. Counterfactual nights require
seasonality, trends and replacement supply; prices and revenue/GBV must match the period
and product definition. Without actual Airbnb-channel bookings, show count-weighted and
review-weighted results as separate proxies, with recapture as an explicit assumption.
Conversion to LTR shrinks STR supply; retaining other-platform distribution may increase
competitive risk; a sale followed by continued Airbnb activity need not reduce supply.

**Synthetic arithmetic check, not an empirical result:** start with 1,000 properties and
100 missing IDs. Suppose 20 are verified replacement IDs, 20 return before confirmation,
50 meet the persistent-exit rule, and 10 remain unresolved. Supported property exit is 5%,
with a 5%-6% identification range, versus 10% raw ID disappearance. Among the 50 exits,
suppose 20 have established other-STR-only use, 15 LTR-only use, five confirmed non-rental
use and 10 unknown destinations. Twelve sales could overlap these states. Neither the
unknown destinations nor the sales belong in a forced "all exits went to X" narrative.

## 8. Reproduce the completed audit

From the repository root, with Git and Python available:

```powershell
python analysis/src/audit_listing_churn_inputs.py --source-rev 620f1ee4691d06df964bd73ce84cc35e8766e4a0 --output-dir data/processed
python -m unittest discover -s analysis/tests -p test_audit_listing_churn_inputs.py -v
```

The JSON audit records input commit and SHA-256 hashes. The script uses no third-party
Python packages and performs no network requests. If the pinned commit is missing in a
fresh clone, fetch the shared repository's `krish/inside-airbnb-supply` branch first.
Tests cover stock-flow errors, duplicate observations, missing snapshots, scope flags,
invalid intervals, nonfinite ratios and zero denominators. They validate the aggregate
audit, not an unimplemented property matching or destination classifier.

Sources: team supply panel and code at `620f1ee`; team Common Crawl note and code at
`7eb638ee7e8653a605eee70a1764f392cc1245d8`; main inventory at
`b6cfe82ccc1100614dbb0cd03149965e0dabfbcb`. External primary documentation was checked
2026-09-06 and is linked where used; see the S-CHURN entries in the source log.
