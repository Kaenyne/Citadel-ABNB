# Inside Airbnb supply panel: 13 cities, 168 dumps, Dec 2022 to Aug 2026

**What this is:** listing-level panel built from Inside Airbnb `listings.csv.gz` dumps (CC-BY 4.0) for 13 cities across Airbnb's four reporting regions, with same-listing (like-for-like) nightly price, listing retention, review velocity, host concentration and the exposed-nights input for the regulatory tracker. Plan-of-attack branch 1.
**Compiled:** 2026-09-05. Author: Krishang, with Claude Code. Script: `analysis/src/inside_airbnb_supply_panel.py` (discover, download, build, figures). Outputs in `data/processed/inside_airbnb_*.csv` and `analysis/figures/inside_airbnb_*.png`.
**Cities:** New York, Los Angeles, Chicago, Austin, Nashville, New Orleans, San Diego (NA); Paris, London, Barcelona, Rome (EMEA); Sydney (APAC); Mexico City (LatAm).

---

## 1. Headline findings

1. **Same-listing nightly prices fell through 2025 in every city with a clean year-over-year pair.** Matched entire-home listings, median change in the listed nightly rate versus the same listing a year earlier: Rome -5% to -8% (Mar to Sep 2025), Paris -1% to -4%, Austin -4% to -5%, Nashville -8% to -11%. Rome had been +9% to +12% in early 2024. Airbnb's reported ADR rose low single digits over the same period, so the reported ADR growth is mix and FX, not like-for-like pricing power. Only 30% to 37% of matched Rome, Paris, Austin and Nashville listings raised their price in 2025; 53% to 69% of Rome listings had raised it in 2024.
2. **Supply churn is high and steady: 20% to 30% of a city's listings are gone a year later, and 20% to 35% of today's listings did not exist a year ago.** Year-ago retention in the latest pairs: Rome 82%, New Orleans 78%, Chicago 78%, Paris 78%, San Diego 77%, Nashville 76%, Mexico City 76%, Sydney 74%, Austin 70%, London 70%, NYC 70%, LA 67%, Barcelona 63%. Exits skew to listings that were not being booked: in NYC only 16% of exiting listings had a review in the prior 12 months, in LA 43%, Paris 50%, London 53%.
3. **Professionalisation keeps rising.** In the latest dumps, 55% to 81% of listings belong to hosts with more than one listing in the city (Barcelona 81%, Nashville 72%, Chicago 70%, Mexico City 69%; Paris is the outlier at 36%), and 24% to 63% belong to hosts with five or more. The multi-listing share rose year over year in all 13 cities (0.3 to 10 points; Austin and NYC the most). Superhost share also rose in most cities (Austin +10 points, San Diego +4 to +7, Paris +1 to +5). The single largest host runs 908 entire homes in NYC (3.0% of the city's listings), 636 in Paris, 600 in Barcelona (3.7%), 501 in London.
4. **Bookings velocity (reviews in the last twelve months, all listings) is growing slowly in mature cities and fast in LatAm and APAC.** Latest full-scope dump versus the year-ago dump: Mexico City +19%, Chicago +14%, Sydney +10%, LA +8%, Rome +7%, San Diego +6%, London +5%, Nashville +5%; Paris -1%, NYC +1%, Barcelona -2%, New Orleans +3%, Austin -8%. Rome's growth decayed from +35% (Dec 2023) to +7% (Aug 2026).
5. **Regulated cities show it in the data.** NYC after Local Law 18: 55% entire-home share (lowest in the panel), 81% of listings require 30+ nights, listing count down 16% year over year and 908-listing corporate hosts dominate what is left. Barcelona listings down 16% to 21% year over year ahead of the 2028 licence expiry. Paris and Rome carry registration numbers on 80% to 86% of listings; London and Mexico City have none.

## 2. Data: what Inside Airbnb actually publishes, and three breaks in the series

Theo's acquisition layer (`analysis/src/acquisition/run_inside_airbnb.py`, manifests in `data/manifests/`) pulled the *current* dump for 120 markets on the same day; this panel is the *historical* series for 13 of them, built from the older files. Inside Airbnb shows only the latest dump per city on its page, but older files stay on its CDN. `discover` takes the quarterly dump dates seen in Wayback captures of the get-the-data page (Jan 2023 to Feb 2026), HEAD-checks each, and probes Dec 2025 to Aug 2026 day by day. Result: 279 known dumps, 168 still downloadable (2.6 GB), manifest in `data/raw/inside_airbnb/manifest.csv`.

| City | Live dumps | First | Last |
|---|---|---|---|
| Rome | 21 | 2022-12-13 | 2026-08-25 |
| Paris | 17 | 2023-12-12 | 2026-08-15 |
| Austin, Nashville | 15 each | 2024-06 | 2026-08 |
| San Diego | 13 | 2025-03-16 | 2026-08-29 |
| Chicago, LA | 12 each | 2025-03 | 2026-08 |
| NYC, New Orleans, Mexico City | 11 each | 2025-06 to 2025-10 | 2026-08 |
| Barcelona, London, Sydney | 10 each | 2025-09 | 2026-08 |

Older dumps (2022 to mid-2025 for most cities) return 403; the CDN keeps roughly a year. The NYC pre/post Local Law 18 series (dumps Dec 2022 to Aug 2025 existed; all 403 now) has to be requested from Inside Airbnb through its data request form. Do that this week; the request should name NYC 2023-06-05, 2023-10-01, 2023-11-01, 2024-01-05, 2024-03-07 as a minimum.

Three breaks the script handles, all of which would produce nonsense if ignored:

| Break | Dumps affected | Symptom | Handling |
|---|---|---|---|
| **Price basis change.** Through Sep 2025 `price` is the listing's nightly rate for the first available night. From Mar 2026 the dumps add a `price_quote_*` block (a quote for a specific stay, fee-inclusive) and `price` equals `price_quote_price_per_night`, a total-price-divided-by-nights figure with cleaning and service fees inside. | All 2026 dumps with prices | Same-listing "price" up 24% to 29% at the median between Jun 2025 and Jun 2026 in Rome, LA and Paris; Mexico City median 1,264 to 2,100 | `price_basis` column (`listed_nightly`, `none`, `quote_per_night`); like-for-like price is computed only when both dumps share a basis (`price_comparable`) |
| **No price at all.** | Dec 2025 to Feb 2026 monthly dumps, all cities; some to Mar/Apr 2026 | `price` blank for every listing | basis `none`; price pairs skipped, everything else kept |
| **Partial scope.** The Dec 2025 to May 2026 monthly dumps cover a subset of listings in most cities (Paris 38k vs 78k, London 54k vs 93k, NYC 2026-06-08 4.5k vs 30k). Austin's scope also shrank permanently from Sep 2025 (15k to 11k). | 41 of 168 dumps | Listing counts drop 20% to 90% and bounce back | `partial_scope` flag: listing count under 80% of the largest dump of the same city within 200 days. Level series use full-scope dumps only; matched-id metrics are robust to scope but retention across a scope change (Austin Sep 2024 to Sep 2025: 47%) is not churn |

Also: `host_since` is blank in 2026 dumps and replaced by `hosts_time_as_host_years/months` (handled). The two are not the same clock: `host_since` is account creation (median 7.5 to 9.3 years in the 2025 dumps), time-as-host is shorter (median 4.7 to 8.3 years in Aug 2026). Hosts under one year account for 4% to 15% of listings in Aug 2026 (Mexico City 15%, Sydney 12%, NYC 4%). Price is null when the listing's calendar shows no availability, which is 10% to 40% of listings depending on city and era, so every price statistic is on available listings. NYC's 2026 quotes are for 30-night stays (Local Law 18), so its per-night quote is a monthly rate divided by 30 and is not comparable with other cities.

## 3. Definitions

| Field | Definition |
|---|---|
| Like-for-like price change | Listing ids present in both dumps of a city, entire homes, price in both, same price basis; per-city price winsorised at 1st/99th percentile and bounded 10 to 10,000; median of log(price_b / price_a), reported as a percentage. `lfl_price_up_share` is the share of matched listings with a higher price (over 0.5%) |
| Year-ago pair | For each dump, the earlier dump of the same city 270 to 460 days back closest to 365 days, preferring one with the same price basis |
| Retention | Share of dump-A listing ids still present in dump-B. `new_share_b` is the share of dump-B ids absent from dump-A |
| Reviews LTM | `number_of_reviews_ltm` summed over listings. A bookings-velocity proxy: reviews lag stays by weeks and the review rate is roughly half of stays |
| Estimated nights, exposed nights | Inside Airbnb's occupancy model: reviews LTM / 0.5 review rate x max(3, minimum nights) nights per stay, capped at 70% of 365. Exposed nights = the same, restricted to entire homes with minimum nights under 30 (the listings STR rules target) |
| Multi-listing, professional | `calculated_host_listings_count` > 1, and >= 5 |
| Superhost share | Share of listings whose host is a Superhost |

## 4. Tables

### 4.1 Same-listing nightly price, year over year (listed-nightly basis only, 15 pairs)

| City | Dump | Year-ago dump | Matched priced entire homes | Median price change | Share raising price | Median price a → b |
|---|---|---|---|---|---|---|
| Rome | 2023-12-15 | 2022-12-13 | 12,692 | +9.1% | 62% | 105 → 119 |
| Rome | 2024-03-22 | 2023-03-15 | 12,399 | +12.3% | 69% | 123 → 140 |
| Rome | 2024-06-15 | 2023-06-10 | 13,446 | +4.7% | 57% | 154 → 160 |
| Rome | 2024-09-11 | 2023-09-07 | 14,471 | +2.0% | 53% | 154 → 160 |
| Rome | 2024-12-12 | 2023-12-15 | 15,066 | 0.0% | 46% | 117 → 116 |
| Rome | 2025-03-05 | 2024-03-22 | 14,830 | -7.6% | 33% | 138 → 125 |
| Rome | 2025-06-12 | 2024-06-15 | 15,979 | -5.0% | 36% | 159 → 149 |
| Rome | 2025-09-14 | 2024-09-11 | 17,096 | -5.7% | 34% | 155 → 145 |
| Paris | 2024-12-06 | 2023-12-12 | 27,623 | 0.0% | 32% | 155 → 150 |
| Paris | 2025-03-03 | 2024-03-16 | 30,308 | -4.2% | 30% | 166 → 155 |
| Paris | 2025-06-06 | 2024-06-10 | 34,344 | -0.9% | 36% | 180 → 174 |
| Austin | 2025-06-13 | 2024-06-17 | 6,059 | -3.6% | 37% | 164 → 156 |
| Austin | 2025-09-16 | 2024-09-13 | 6,053 | -4.8% | 34% | 160 → 150 |
| Nashville | 2025-06-19 | 2024-06-22 | 3,975 | -7.9% | 33% | 177 → 161 |
| Nashville | 2025-09-23 | 2024-09-18 | 3,900 | -11.0% | 30% | 181 → 156 |

Local currency (EUR for Rome and Paris, USD for Austin and Nashville). Full table with sequential pairs and the 2026 quote-basis pairs in `data/processed/inside_airbnb_like_for_like.csv`. The 2026 quote-basis month-to-month medians are mostly exactly zero (hosts do not reprice monthly), so that series is only useful once a year of it exists.

### 4.2 Latest full-scope dump per city (Aug 2026)

| City | Listings | Entire home | Min nights < 30 | Licensed | Superhost | Multi-listing host | 5+ listings host | Top-10 hosts | Reviews LTM | Reviews LTM y/y | Exposed nights (entire, <30 min) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NYC | 30,234 | 55% | 19% | 17% | 22% | 57% | 36% | 9.7% | 144,693 | +1% | 219k |
| LA | 43,735 | 74% | 53% | 30% | 39% | 65% | 40% | 3.5% | 386,762 | +8% | 1.65m |
| Chicago | 8,778 | 77% | 67% | 66% | 47% | 70% | 50% | 12.0% | 136,135 | +14% | 591k |
| Austin | 11,079 | 83% | 87% | 32% | 49% | 63% | 39% | 6.7% | 136,702 | -8% | 683k |
| Nashville | 10,164 | 91% | 87% | 11% | 61% | 72% | 55% | 12.3% | 180,772 | +5% | 882k |
| New Orleans | 7,303 | 80% | 59% | 81% | 47% | 68% | 47% | 11.6% | 88,655 | +3% | 371k |
| San Diego | 13,342 | 83% | 71% | 77% | 55% | 68% | 43% | 8.7% | 196,361 | +6% | 933k |
| Paris | 78,504 | 89% | 80% | 80% | 22% | 36% | 24% | 3.4% | 557,710 | -1% | 2.65m |
| London | 92,783 | 66% | 98% | 0% | 19% | 55% | 34% | 2.4% | 583,379 | +5% | 2.22m |
| Barcelona | 16,227 | 69% | 59% | 63% | 24% | 81% | 63% | 18.3% | 216,064 | -2% | 801k |
| Rome | 37,483 | 75% | 93% | 86% | 41% | 61% | 33% | 2.9% | 570,095 | +7% | 2.55m |
| Sydney | 20,767 | 79% | 86% | 94% | 34% | 63% | 45% | 6.5% | 218,924 | +10% | 1.07m |
| Mexico City | 30,621 | 67% | 99% | 0% | 43% | 69% | 45% | 3.9% | 506,063 | +19% | 1.98m |

Reviews LTM y/y compares with the full-scope dump nearest 12 months earlier (Sep 2025 for most cities). Exposed nights feed the regulatory tracker in `research/regulatory/`; they are Inside Airbnb's model, not bookings data.

### 4.3 Churn composition, latest year-ago pair per city

| City | Pair | Retention | New share of dump B | Exits with a review LTM | Exits entire home | Exits multi-listing | Adds entire home | Adds multi-listing |
|---|---|---|---|---|---|---|---|---|
| NYC | Oct 2025 → Aug 2026 | 70% | 17% | 16% | 48% | 43% | 53% | 70% |
| LA | Sep 2025 → Aug 2026 | 67% | 30% | 43% | 70% | 64% | 72% | 73% |
| Paris | Sep 2025 → Aug 2026 | 78% | 19% | 50% | 87% | 40% | 89% | 55% |
| London | Sep 2025 → Aug 2026 | 70% | 27% | 53% | 68% | 61% | 74% | 68% |
| Barcelona | Sep 2025 → Aug 2026 | 63% | 25% | 49% | 39% | 70% | 55% | 86% |
| Rome | Sep 2025 → Aug 2026 | 82% | 17% | 63% | 76% | 57% | 72% | 67% |
| Austin | Sep 2025 → Aug 2026 | 70% | 33% | 69% | 85% | 60% | 76% | 67% |
| Nashville | Sep 2025 → Aug 2026 | 76% | 29% | 78% | 89% | 74% | 90% | 79% |
| Chicago | Sep 2025 → Aug 2026 | 78% | 24% | 63% | 74% | 73% | 73% | 73% |
| New Orleans | Sep 2025 → Aug 2026 | 78% | 21% | 60% | 88% | 66% | 72% | 79% |
| San Diego | Sep 2025 → Aug 2026 | 77% | 24% | 63% | 82% | 72% | 78% | 73% |
| Sydney | Sep 2025 → Aug 2026 | 74% | 37% | 70% | 81% | 66% | 79% | 71% |
| Mexico City | Sep 2025 → Aug 2026 | 76% | 33% | 61% | 60% | 63% | 66% | 64% |

New listings are more likely than exits to belong to multi-listing hosts in 10 of 13 cities: the churn itself professionalises the base.

## 5. How this feeds the pitch

- **ADR decomposition.** Same-listing price deflation of 1% to 11% in 2025 against reported ADR growth of low single digits (see `data/processed/abnb_kpi_vs_category_quarterly.csv`) is the cleanest evidence that ADR is mix and FX. Slide candidate: figure `inside_airbnb_lfl_price_yoy.png` next to reported ADR y/y. Caveat on the slide: four cities, listed nightly rate not realised rate, local currency.
- **Supply growth quality.** Listing counts are flat to down in 10 of 13 cities year over year (up only in Mexico City, Sydney and Nashville) while reviews grow, which is consistent with Airbnb's "quality over quantity" listing removals (Q2 2026 letter) and with the professional share rising. Use 4.2 and `inside_airbnb_multi_listing_share.png`.
- **Regulatory exposure.** Exposed nights per city (4.2) are the base for the regulatory tracker's nights-at-risk estimate. NYC is the template for what a 30-night rule does: entire-home share 55%, top-10 hosts 10% of supply, review velocity flat.
- **Build-forward.** Inside Airbnb now publishes monthly. Re-run `discover` and `download` before the 5 Nov print to add Sep and Oct 2026 dumps; the quote-basis like-for-like series becomes usable once Mar 2026 has a year-ago comparator (Mar 2027), so for the pitch the price story rests on the 2023 to 2025 listed-nightly series.

## 6. Caveats

- Inside Airbnb scrapes public listing pages on a date; it is not bookings data. Price is the listed rate for the first available night (or, from 2026, a fee-inclusive quote), not realised ADR.
- Listing counts depend on Inside Airbnb's city boundary and scraping completeness, both of which changed in 2025 to 2026 (section 2). Use matched-id metrics for trends and full-scope dumps for levels.
- Reviews lag stays and the review rate drifts; the ratio to stays is assumed constant within a city.
- 13 cities are a convenience sample of Airbnb's largest urban markets, over-weighting regulated cities. Non-urban supply (where Airbnb's growth is) is not covered.
- Licence: CC-BY 4.0. Attribute "Inside Airbnb (insideairbnb.com)" on every slide that uses these numbers.
