# Hotel demand: what the earlier data measured, and the claim to test

As of September 7, 2026. This clarification takes precedence over any interpretation of the earlier listing exercise as a completed hotel-demand study.

## The data I previously used

The earlier +6.8% listing growth and +1.0% annual reviews-per-listing growth came from **hotel-labeled rows inside existing Inside Airbnb listing snapshots**. They did not come from hotel reservation systems, and they did not measure what happened to a hotel's total business after it joined Airbnb.

| Input | What it contains | What I did with it | What it cannot establish |
|---|---|---|---|
| Existing Inside Airbnb `listings.csv.gz` snapshots | Airbnb listing IDs, property-type labels, review counts, advertised prices, minimum stays and calendar availability | Filtered `Hotel`, `Boutique hotel` and rooms in either; compared listing counts and review activity over time | Physical hotel count, room allotment, confirmed reservations, total hotel occupancy, new-product coverage or causal demand uplift |
| External industry/city capacity sources | Hotel rooms, establishments or available room nights, depending on source | Built a separately sourced capacity table | Which physical hotels are listed on Airbnb or whether joining increased their bookings |
| Earnings materials | Management's platform-level statements | Recorded the single-digit hotel-night share and relative growth rate | A fixed-property before/after experiment or hotel-level all-channel demand uplift |

The 25 cities were my selection: the repository's 13-city listing-churn panel plus 12 extensions. **That starting panel is not Jessie's separate 13-market accommodation-choice study.** I did not identify an agreed 25-country universe. I also did not compare Airbnb homes against an independently matched hotel database.

A concrete example: the existing August 2026 NYC listing file contains listing ID **253828**, named *Duplex w/ Terrace @ Box House Hotel*, and ID **253839**, named *Loft w/ Terrace @ Box House Hotel*. Both have property type `Room in boutique hotel`. Their trailing-year review counts in that capture are **0 and 1**, respectively, and their first-review dates are **2012-04-30 and 2011-11-20**. These are two listing rows with a common hotel name, not proof of two newly acquired hotels. Neither a zero review count nor zero displayed availability proves zero bookings or a sellout.

Local source: `data/raw/listing_churn_panel/new-york-city_2026-08-10_listings.csv.gz`, with those rows last scraped August 11. The [capture register](../../data/processed/hotel_funnel_audit/unique_reused_captures.csv) records the original comparison inputs and hashes. The August example is explanatory; it is not part of the June endpoint used in the 25-city comparison.

The old listing exercise is therefore **supplementary activity evidence**. The market-capacity table is **separate TAM research**. Neither is a completed test of hotel acquisition productivity.

## What Chesky actually said

The Q2 2026 transcript's influx passage concerns interest from hotels **wanting to join Airbnb**. The same answer discusses Airbnb traffic conversion and supplier reception. An analyst subsequently asks for hotel booking-share/conversion examples; the response gives the aggregate hotel growth multiple without a quantified fixed-hotel uplift. This transcript is a third-party transcription of the call, not an independently measured hotel-performance dataset. [Q2 call transcript, first and third analyst exchanges](https://www.fool.com/earnings/call-transcripts/2026/08/13/airbnb-abnb-q2-2026-earnings-call-transcript/)

The official Q2 shareholder letter separately reports hotel nights growing approximately three times as fast as home nights while remaining a single-digit night share. That is a **platform category growth rate**. It can rise through more properties, more inventory allocated per property, more exposure or better conversion; it does not isolate additional demand for the same hotels. [Official Q2 2026 letter](https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm)

The official Q1 transcript describes converting travelers already visiting Airbnb who might otherwise leave, and hoteliers' interest in another distribution channel. That supports testing customer recapture and channel economics, rather than assuming hotels' total demand rose. [Official Q1 2026 transcript, printed pages 16 and 19–20](https://s26.q4cdn.com/656283129/files/doc_financials/2026/q1/Airbnb-Q1-26-Earnings-Call-Transcript.pdf)

## Three different outcomes

| Question | Outcome to measure | What would count as evidence |
|---|---|---|
| Does Airbnb deliver bookings to hotels? | Net Airbnb room nights and net channel revenue per live hotel / allocated available room night | Actual channel-coded reservations, cancellations, stay dates, channel activation and offered inventory |
| Does joining increase the hotel's total business? | All-channel occupied room nights, ADR and revenue after distribution costs | Joining hotels outperform a credible counterfactual after accounting for market conditions, prices and capacity changes |
| Does adding hotels grow Airbnb? | Total Airbnb lodging conversion/contribution, including any loss of home bookings | New hotel bookings rescue searches that would otherwise leave, or add profitable trips; not merely substitution from Airbnb homes or HotelTonight |

An increase in Airbnb's share of a hotel's bookings can be valuable even when the hotel's total room nights do not rise. Conversely, high channel booking volume can be unprofitable after fees, discounts and credits.

## Why NYC is a useful test

In February 2026, management reported more than 100 NYC hotels with more than 20,000 rooms available on the site. This is an existing reported supply anchor, not a new finding from the listing files. It does not disclose time-weighted room allotments or how many room nights Airbnb sold. [Official Q4 2025 transcript, printed page 18](https://s26.q4cdn.com/656283129/files/doc_financials/2025/q4/Airbnb-Q4-25-Earnings-Call-Transcript.pdf)

NYC is a plausible setting for high **marginal value to Airbnb**: when a traveler cannot find a suitable bookable home, a suitable hotel might retain a transaction otherwise lost to another site. Listing an existing hotel adds an Airbnb sales channel; it does not create new physical rooms in NYC. The size of the benefit requires matched searches, availability and transactions, not a city room-stock number alone.

For the operator, high occupancy can limit the extra room nights available to sell. NYC Tourism's March 2026 release reports **84.2% full-year 2025 hotel occupancy**, unchanged from 2024, and **38.1 million room nights sold**, up 2%. These are historical city aggregates, not results for participating independent hotels in September 2026. They supply market context, not evidence of Airbnb causality. [NYC Tourism, 2025 performance released March 2026](https://www.business.nyctourism.com/press-media/press-releases/NYC-Tourism-Annual-Report-March-2026)

**Illustration only:** a 100-room hotel has 3,000 available room nights in a 30-day month. At a counterfactual 90% occupancy, it would sell 2,700. If it sells 200 room nights through Airbnb after joining but total occupied room nights are 2,790, the measured uplift against that counterfactual is **90 nights / 3,000 = 3 percentage points of occupancy**, not 200 incremental nights. Under the example's fixed capacity/prices and otherwise unchanged channels, the remaining 110 Airbnb nights replace other-channel nights. A real study must estimate the counterfactual, not assume it.

## The minimum data worth obtaining

The smallest useful dataset is a **hotel-by-week panel of actual reservations**, with verified first bookable Airbnb dates, physical property IDs, room capacity and originating channel. Keep Airbnb's consumer storefront separate from the HotelTonight connectivity provider and pre-existing HotelTonight sales. Retain booking dates, arrival/departure dates, booked room quantities, cancellations, no-shows, revenue, commissions and promotions. No guest names or personal contact details are needed.

Use property-verified NYC joiners and comparable non-joiners or not-yet-joiners. Compare the change in all-channel room nights, occupancy and net revenue between these groups, retaining pre-period trends and separating weekday/weekend and peak/quiet dates. Control for renovations, openings, closures, room allotment changes and events; hotels may join specifically when demand is weak, so an uncontrolled before/after increase is not causal proof. The number of properties and observation weeks must be set from obtainable coverage and a power check, not a fabricated sample-size guarantee.

Public listing/review/rate monitoring can screen candidate hotels and document dates when they were observed bookable. It cannot replace all-channel reservation outcomes or an exact activation date. Without those outcomes, the honest deliverable remains an activity/availability screen, not a claim of a large demand surge.

The requested independent agent's [separate assessment](2026-09-07_hotel-demand-independent-review.md) evaluates concrete data providers, public evidence and access limits. It is an independent review of the question; sources shared with the existing team are still counted only once. No hotel outreach, data purchase or reservation experiment was conducted.
