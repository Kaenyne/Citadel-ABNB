# Airbnb hotel supply and promotion research: expanded evidence

Evidence cutoff: September 7, 2026. Security: Airbnb, NASDAQ: ABNB, USD. This workstream tests whether accessible supply and commercial-term evidence can constrain a hotel revenue forecast over the next four quarters. It does not supply an absolute hotel bookings or revenue series.

**We obtained 14,600 hotel-registry rows across three source populations and captured 143 current Airbnb hotel pages representing 141 name/address clusters. Actual hotel bookings obtained in this workstream: zero.** These counts describe different units and cannot be pooled into a demand sample. The work materially improves the property sampling frame and inventory-denominator evidence; it does not establish incremental revenue or statistical significance of hotel demand.

## What was actually obtained

| Source population | Raw observations | Usable identification/count | Physical room information | Vintage and limitation |
|---|---:|---:|---:|---|
| NYC DCWP hotel licenses | 826 license rows | 785 Active/Ready for Renewal rows with unexpired licenses; 761 normalized address clusters | No room-count field | Source updated August 20, 2026. Status and addresses are retained, including duplicates and exceptions. This is a legal-premises frame, not 761 proven boutique hotels. |
| Atout France classified hotels | 13,306 hotel rows, extracted from 21,434 accommodation rows | 13,302 normalized name/address identities after four duplicate classification records | 606,429 rooms after deduplication; raw total 606,632 | September 7, 2026 export. Classified hotels only; includes chains and excludes unclassified establishments. |
| Paris subset of France | 1,589 hotel rows | 1,589 name/address identities | 85,815 rooms | Paris postal codes 75001–75020 **and 75116**. This is already included in the France row; never add it again. |
| Singapore Hotels Licensing Board | 468 property features | 468 unique object IDs and name/postcode pairs | 74,597 rooms | Data from July 2025; portal updated March 8, 2026. Includes some hostels and serviced properties. Affiliation and September 2026 operating status remain unverified. |
| Airbnb hotel page captures | 145 unique discovered URLs attempted | 143 HTTP 200 hotel-style pages; 141 name/address clusters | 41 conservative registry links supply 3,499 physical rooms | September 7, 2026 captures. Two HTTP 410 failures retained in the fetch log. No dates supplied and no price quotes obtained. |

Sources: [NYC Issued Licenses](https://data.cityofnewyork.us/Business/Issued-Licenses/w7w3-xahh), [NYC hotel licensing FAQ](https://www.nyc.gov/assets/dca/downloads/pdf/businesses/Hotel-Licensing-Law-FAQ.pdf), [Atout France dataset](https://www.data.gouv.fr/datasets/hebergements-touristiques-classes-en-france), [Singapore HLB dataset and schema](https://data.gov.sg/datasets/d_654e22f14e5bb817423f0e0c9ac4f632/view). Counts and sums above are calculated from the preserved source files; they are not issuer-disclosed Airbnb supply figures.

The NYC law took effect May 3, 2025. Therefore, initial license issuance is not the hotel's opening or Airbnb activation date. Of 826 rows, 420 are Active, 365 Ready for Renewal, 25 Surrendered, 7 Voided, 6 Failed to Renew and 3 Suspended. Ready for Renewal rows are retained as candidates only when the stated expiration is not before September 7, 2026. Twenty-three candidate addresses contain multiple licenses. An address cluster can still contain more than one hotel or brand; no automatic claim of a single physical hotel is made. One candidate lacks a borough value but records a Brooklyn address and 11207 postcode. [DCWP license information](https://www.nyc.gov/site/dca/businesses/licenses.page)

France's four duplicate classification records refer to the same normalized name/address and the same room count, with different classification dates. The processor retains the latest dated classification and preserves both source row numbers. The 203 excess rooms are excluded from the deduplicated total. Paris has 1,172 hotels with fewer than 50 rooms, representing 37,301 rooms: **73.8% of classified properties but 43.5% of classified rooms**. Small size is a useful underwriting stratum; it does not prove independent ownership or Airbnb eligibility. [Atout France](https://www.data.gouv.fr/datasets/hebergements-touristiques-classes-en-france)

## Airbnb property identity and rollout evidence

The observation universe is a search-discovered convenience sample in six cities Airbnb explicitly names in its 2026 hotel rollout. It is **not the prior 13-market or self-selected 25-market sample**, and it is not a census of all 20-plus destinations. Captured property clusters: NYC 54, Paris 33, Singapore 18, London 12, Madrid 12 and Rome 12. [Company rollout announcement](https://news.airbnb.com/airbnb-2026-summer-release)

Two duplicate pairs collapse by exact normalized property name and address: Smyth Tribeca, listing IDs 1517566301851660503 and 1517566511154539655; Hotel Esté, IDs 1085986635249498929 and 1085986635156567442. This directly demonstrates why listing IDs cannot be treated as hotels or rooms. The visible property pages and embedded room-type descriptions may also use different rating denominators; neither is converted to bookings. [Smyth example](https://www.airbnb.com/rooms/1517566301851660503), [Esté example](https://www.airbnb.com/rooms/1085986635156567442)

All 143 captured pages display a hotel-style room selector and price-match language. This establishes the presentation observed that day. It does not establish that a room was available on a specified future date, that all rooms were allocated to Airbnb, or that each property participates in the 15% credit offer. The date-free pages do not provide usable 15% credit badges or realized price quotes. The text saying no rooms are available on a date-free page is **not an occupancy observation**.

The registry crosswalk finds at least one premises/identity candidate for 77 of 141 clusters. It accepts physical room-count links only where a unique exact Paris street/postcode or Singapore postcode match is corroborated by a meaningful hotel-name token. That yields **26 Paris and 15 Singapore properties, 41 total, with 3,499 physical rooms**. NYC premises matches retain legal-name ambiguity and have no room count. Nine additional fuzzy-address candidates are kept in an unaccepted review queue; no rooms from that queue enter the accepted total.

Examples of accepted links: Hôtel Baudelaire Opéra, 29 rooms; Hotel Esté, 76; Platine, 46; Atelier Vavin, 17; One Farrer, 252; Hotel Mi Rochor, 530; and Sofitel Singapore City Centre, 223. Room counts come from the registries, while the Airbnb URLs establish observed page presence. They do not establish Airbnb allocation. [Baudelaire page](https://www.airbnb.com/rooms/1269496732669058195), [One Farrer page](https://www.airbnb.com/rooms/1424428701695755446), [Hotel Mi Rochor page](https://www.airbnb.com/rooms/1424451303692713657)

The product boundary requires care. Captures include Arlo, Hotel 81, Sofitel, Millennium and NH Collection-branded pages. Accordingly, an unbranded-room TAM cannot automatically stand for all hotels observable on Airbnb, while every hotel-style page cannot automatically be called a selected boutique hotel. Use separate fields for physical owner/operator, brand affiliation, hotel-style presentation and observed credit eligibility. [Sofitel page](https://www.airbnb.com/rooms/1566465129273341933), [Millennium Broadway page](https://www.airbnb.com/rooms/1544240785619626206), [NH Collection page](https://www.airbnb.com/rooms/1537582123120267360)

## Actual commercial terms versus assumptions

Airbnb's standard service-fee page says most single-fee hosts pay 15.5%, with typical remaining fees of 14–16%, and says the structure applies to traditional hospitality listings. Separately, the Hotel Supplier Terms describe facilitation fees, possible additional guest fees, and supplier-controlled room **Allocation**, without a numeric commission rate. The standard schedule is a benchmark, not evidence of the realized commission on this selected hotel program. No actual numeric hotel contract or payout statement was obtained. [Standard fees](https://www.airbnb.com/help/article/1857), [Hotel Supplier Terms, sections 3–4](https://www.airbnb.com/help/article/3265)

Three promotional documents must remain distinct:

| Program/document | Observed terms | Financial implication |
|---|---|---|
| Summer Release headline | Up to 15% hotel credit; eligible offer through December 31, 2026; $2,000 maximum; excludes taxes/fees | Do not apply 15% to all hotel GBV. [Announcement](https://news.airbnb.com/airbnb-2026-summer-release) |
| General Hotel Credit, articles 4132/4133 | May 20, 2026 terms; credit after the completed stay; one-year redemption window; percentage discretionary and displayed in booking flow | Credits can carry economic and accounting consequences beyond the hotel stay quarter. [Terms](https://www.airbnb.com/help/article/4132), [Instructions](https://www.airbnb.com/help/article/4133) |
| Targeted Guest Offers, article 4200 | June 29, 2026 terms; user-specific benefits; hotel credit at check-in; $2,000 maximum; January 1, 2027 expiry for this program | This targeted program does not replace the general one-year terms. The share of guests exposed to each program is unknown. [Targeted offers](https://www.airbnb.com/help/article/4200) |

The general credit instructions identify select cities in eight countries: France, Germany, Italy, Netherlands, Singapore, Spain, UK and US. This is a country eligibility statement, not a complete market list. Credits may be redeemed on eligible stays, experiences and services; it is too restrictive to model them as necessarily redeemable only on homes. The public terms establish Airbnb issuance but do not expose contractual funding allocation or realized redemption rates. Article 4200's split funding of a **home discount** must not be applied to hotel credits. [Hotel credit instructions](https://www.airbnb.com/help/article/4133), [Targeted offers](https://www.airbnb.com/help/article/4200)

## How this constrains a revenue and guidance pitch

Use the registries to sample property types and size bands and the captured URLs to initialize a longitudinal supply/pricing study. The 41 room-count links give a dated registry room-count reference for those hotels; the Singapore counts are from July 2025 and may have changed. They do not furnish the fraction offered to Airbnb, dates active, or Airbnb bookings per offered room. Those missing variables still determine the next-four-quarter nights forecast.

The saved 27-case sensitivity grid varies assumed commissions (10%, 12%, 15.5%), credit-eligible booking-value share (25%, 50%, 100%) and redemption (25%, 50%, 75%). Every row is explicitly **illustrative**, not a data observation. The monetary base is hotel room booking value excluding taxes and fees; the assumed $200 ADR uses the same basis. The grid's GBV labels refer to this specified room-value base, not Airbnb's reported company GBV definition. The credit rate is the observed 15% headline; full Airbnb funding, $200 ADR, other variable costs of 1.5% of room booking value and a nonbinding per-reservation credit cap are analyst assumptions. Lifetime promotional cost is not labeled same-quarter GAAP contra-revenue.

For example, $1 billion of hotel room booking value at an assumed 12% commission gives $120 million gross fees. If all of it earns 15% credit and half is redeemed, expected credit cost is $75 million, leaving $45 million before other costs, cannibalization and cross-sell. An assumed additional $15 million of variable costs leaves $30 million contribution before fixed costs. At those assumptions, a $150 million cohort fee-minus-expected-credit target requires $3.33 billion of room booking value or 16.67 million nights at $200 ADR. Those nights yield $100 million of contribution before fixed costs, not $150 million of NTM recognized revenue. A $150 million contribution target would instead require $5 billion of room booking value or 25 million nights. Without credits, the same $150 million cohort fee-minus-expected-credit target requires $1.25 billion of room booking value or 6.25 million nights. A booking-date, check-in and credit-redemption schedule is still needed to translate these cohort economics into NTM reported revenue. These are sensitivity results, not an Airbnb forecast.

The next economically decisive additions are actual Airbnb-source room-night production by stay month and a commission/payout sample; a larger registry alone cannot supply them. Bloomberg/Refinitiv corporate consensus can anchor the forecast hurdle but cannot be assumed to contain these private hotel-level fields. The parent workstream handles the precise terminal request and company-disclosure search.

## Statistical and overlap boundaries

- The registry files provide large population frames, not a probability sample of Airbnb bookings. Their room counts do not make a causal demand test statistically significant.
- The 141 Airbnb clusters were discovered through search. Search inclusion probabilities are unknown, and neighborhood queries overlap. No confidence interval or market-penetration percentage is calculated from this sample.
- A future price panel must repeat the **same** properties, dates, occupancy and cancellation terms; property/date cells are correlated, and multiple listing IDs must remain clustered at the physical property.
- The France national total and Paris subset overlap exactly. General hotel terms and company announcements reuse public management evidence; they are not independent channel checks. The parent agent conducts the updated repository/Jessica/team overlap audit. This workstream does not claim universal non-overlap.
- No Inside Airbnb label/review counts were reprocessed or converted into hotel nights here. No bookings, paid-data purchases or hotel outreach were made.

## Artifacts and checks

Raw inputs, HTTP results, compressed page captures and hashes: `data/raw/hotel_rollout_economics/`. Processed registry files, 143 observations, 141 identity clusters, crosswalk/review queue, coverage JSON, capacity strata and economics grid: `data/processed/hotel_rollout_economics/`. Citation ledger: `research/sources/hotel_rollout_economics_expansion.json`.

Rebuild from repository root with the workspace Python:

```powershell
.\.venv\Scripts\python.exe data\raw\hotel_rollout_economics\fetch_public_inputs.py
.\.venv\Scripts\python.exe data\raw\hotel_rollout_economics\build_supply_frames.py
.\.venv\Scripts\python.exe data\raw\hotel_rollout_economics\match_registry_candidates.py
.\.venv\Scripts\python.exe data\raw\hotel_rollout_economics\summarize_economics.py
```

Registry fetching preserves existing captures unless `--refresh` is provided. Page fetching is opt-in with `build_supply_frames.py --fetch-pages`; recorded discovery queries are not automatically expanded. Checks covered unique license/object IDs, required fields, nonnegative room counts, four duplicate classifications, Paris postal coverage including 75116, duplicate Airbnb identities, failed HTTP captures, and the 27-case arithmetic. A false-positive 15% detector was caught and fixed: review-rating percentages are not promotional credit offers. The NYC FAQ was readable through web research but direct raw download returned HTTP 403, recorded explicitly.
