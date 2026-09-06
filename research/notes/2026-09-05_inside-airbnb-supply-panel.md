# Inside Airbnb supply panel: 13 cities, 168 dumps, Dec 2022 to Aug 2026

**What this is:** listing-level panel built from Inside Airbnb `listings.csv.gz` dumps (CC-BY 4.0) for 13 cities across Airbnb's four reporting regions, with same-listing (like-for-like) nightly price, listing retention, review velocity, host concentration and the exposed-nights input for the regulatory tracker. Plan-of-attack branch 1.
**Compiled:** 2026-09-05. Author: Krishang, with Claude Code. Script: `analysis/src/inside_airbnb_supply_panel.py` (discover, download, build, figures). Outputs in `data/processed/inside_airbnb_*.csv` and `analysis/figures/inside_airbnb_*.png`.
**Cities:** New York, Los Angeles, Chicago, Austin, Nashville, New Orleans, San Diego (NA); Paris, London, Barcelona, Rome (EMEA); Sydney (APAC); Mexico City (LatAm).
**Corrected 2026-09-07** (audit finding A04, workstream 21): partial Inside Airbnb scrapes were contaminating 25 of the 103 year-ago pairs. See [section 7, Correction 7 Sep 2026](#7-correction-7-sep-2026-pair-eligibility-audit-finding-a04) and `research/notes/overnight/21_inside-airbnb-pair-eligibility.md`. Numbers below are the corrected ones.

---

## 1. Headline findings

1. **Quoted nightly prices on matched, surviving listings fell through 2025 in the four cities where a comparable year-over-year pair exists.** Matched entire-home listings present in both dumps, priced in both, on the same price basis and with both dumps full scope (13 eligible pairs, four cities, local currency): median change in the *listed* nightly rate versus the same listing a year earlier is Rome -5.0% to -7.6% (Mar to Sep 2025), Paris -0.9% to -4.2% (Mar and Jun 2025), Nashville -7.9% to -11.0% (Jun and Sep 2025), Austin -3.6% (Jun 2025, the only eligible Austin pair). Rome had been +2.0% to +12.3% through 2024. This is a quoted asking rate on listings that survived a year, not a realised ADR and not a market-wide index: it says nothing about listings that exited or about the nights actually sold. Airbnb's reported ADR rose low single digits over the same period, which is *consistent with* reported ADR growth being mix and FX rather than like-for-like pricing power, but four cities cannot establish that. Only 30% to 37% of these matched listings raised their price in 2025; 46% to 69% of Rome listings had raised it in the 2024 pairs.
2. **Supply churn is high and steady: roughly 20% to 30% of a city's listings are gone a year later, and 20% to 37% of today's listings did not exist a year ago.** Year-ago retention on the latest *comparable* pair per city (both dumps full scope): Rome 82%, Chicago 78%, New Orleans 78%, Paris 78%, San Diego 77%, Nashville 76%, Mexico City 76%, Sydney 74%, London 70%, NYC 69%, LA 67%, Barcelona 63%. **Austin has no comparable year-ago pair** and is excluded: its Sep 2025 dump is a partial scrape and every later Austin pair straddles a permanent listing-count step (15.2k to ~11k from Sep 2025), so its apparent 37% to 53% retention is a coverage artefact, not churn. Exits skew to listings that were not being booked: in NYC only 16% of exiting listings had a review in the prior 12 months, in LA 43%, Barcelona 49%, Paris 50%, London 53%.
3. **Professionalisation keeps rising.** In the latest dumps, 55% to 81% of listings belong to hosts with more than one listing in the city (Barcelona 81%, Nashville 72%, Chicago 70%, Mexico City 69%; Paris is the outlier at 36%), and 24% to 63% belong to hosts with five or more. The multi-listing share rose year over year in all 13 cities (0.3 to 10 points; Austin and NYC the most). Superhost share also rose in most cities (Austin +10 points, San Diego +4 to +7, Paris +1 to +5). The single largest host runs 908 entire homes in NYC (3.0% of the city's listings), 636 in Paris, 600 in Barcelona (3.7%), 501 in London.
4. **Bookings velocity (reviews in the last twelve months, all listings) is growing slowly in mature cities and fast in LatAm and APAC.** Latest full-scope dump versus the nearest full-scope dump about twelve months earlier: Mexico City +19%, Chicago +14%, Sydney +11%, LA +8%, Rome +7%, San Diego +6%, London +5%, Nashville +5%, New Orleans +3%, NYC +1%, Paris -1%, Barcelona -2%. **Austin -8% is not usable**: its only full-scope comparator is 438 days back and on the pre-Sep-2025 scope (15,187 listings vs 11,079), so the fall is coverage, not demand. Rome's growth decayed from +35% (Dec 2023) to +7% (Aug 2026).
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
| **Partial scope.** The Dec 2025 to May 2026 monthly dumps cover a subset of listings in most cities (Paris 38k vs 78k, London 54k vs 93k, NYC 2026-06-08 4.5k vs 30k). The subset is a uniform sample, not a geographic truncation: all 20 Paris arrondissements are still present in the 38k dump, so neighbourhood coverage does not detect it. Austin's scope also shrank permanently from Sep 2025 (15k to 11k). | 41 of 168 dumps (32 on the point-in-time rule) | Listing counts drop 20% to 90% and bounce back; a partial dump at the end of a pair looks like a mass exit of listings | `partial_scope` flag: listing count under 80% of the largest dump of the same city within +/- 200 days. Level series use full-scope dumps only. **Corrected 7 Sep 2026:** the flag is now joined onto BOTH endpoints of every pair before selection and drives `pair_eligible` / `exclusion_reason`; 25 of 103 year-ago pairs are ineligible. A second, point-in-time flag (`partial_scope_pit`, trailing window only) is stored for predictive replay |

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
| Pair eligibility (added 7 Sep 2026) | A pair carries a market interpretation only if **both** dumps are full-scope scrapes. `pair_eligible` uses the retrospective `partial_scope` flag (+/- 200-day reference window); `pair_eligible_pit` uses the point-in-time flags (trailing 200-day and 400-day windows, never revised by a later scrape) and is the one predictive replay must use. Ineligible pairs stay in `inside_airbnb_like_for_like.csv` with an `exclusion_reason`; the `retention_clean`, `matched_reviews_ltm_chg_clean` and `lfl_price_chg_median_clean` columns are null on them, and the figures read those columns |
| Span-step warning | `span_step_warning`: both endpoints are full-scope for their own era but the pair straddles a step in the city's listing count (either endpoint under 80% of the largest dump between them). Austin from Sep 2025 and Barcelona 2026 are the cases. An Inside Airbnb scope reduction and a genuine market contraction are **not** separable from listing counts alone, so this is a warning to carry on the slide, not an exclusion |

## 4. Tables

### 4.1 Quoted nightly price on matched listings, year over year (listed-nightly basis, both dumps full scope, 13 eligible pairs)

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
| Paris | 2025-03-03 | 2024-03-16 | 30,308 | -4.2% | 30% | 166 → 155 |
| Paris | 2025-06-06 | 2024-06-10 | 34,344 | -0.9% | 36% | 180 → 174 |
| Austin | 2025-06-13 | 2024-06-17 | 6,059 | -3.6% | 37% | 164 → 156 |
| Nashville | 2025-06-19 | 2024-06-22 | 3,975 | -7.9% | 33% | 177 → 161 |
| Nashville | 2025-09-23 | 2024-09-18 | 3,900 | -11.0% | 30% | 181 → 156 |

**What this is.** Quoted (listed) nightly asking rates in local currency (EUR for Rome and Paris, USD for Austin and Nashville) on entire-home listings that were present and priced in **both** dumps of the pair, on the same price basis, with **both dumps full scope** (`price_pair_eligible=True` in `inside_airbnb_like_for_like.csv`). It is a survivor-cohort asking price, not a realised ADR, not weighted by nights sold, and not representative of the whole market: exiting listings and new listings are both outside it. Coverage: 4 of 13 cities and 13 pairs, Dec 2023 to Sep 2025 — the price-basis change (section 2) ends the comparable series in Sep 2025.

**Corrected 7 Sep 2026 (A04):** two rows were dropped from this table because one endpoint is a partial scrape — Paris 2024-12-06 vs 2023-12-12 (0.0%, the 2023-12-12 Paris dump is 74,329 listings against 95,885 in Jun 2024, `scope_vs_peer` 0.78) and Austin 2025-09-16 vs 2024-09-13 (-4.8%, the Sep 2025 Austin dump is 10,533 against 15,187 in Jun 2025, `scope_vs_peer` 0.68). Both rows remain in the CSV with `pair_eligible=False`. The headline range for Austin therefore rests on a single pair.

Full table with sequential pairs and the 2026 quote-basis pairs in `data/processed/inside_airbnb_like_for_like.csv`. The 2026 quote-basis month-to-month medians are mostly exactly zero (hosts do not reprice monthly), so that series is only useful once a year of it exists.

### 4.2 Latest full-scope dump per city (Aug 2026)

| City | Listings | Entire home | Min nights < 30 | Licensed | Superhost | Multi-listing host | 5+ listings host | Top-10 hosts | Reviews LTM | Reviews LTM y/y | Exposed nights (entire, <30 min) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NYC | 30,234 | 55% | 19% | 17% | 22% | 57% | 36% | 9.7% | 144,693 | +1% | 219k |
| LA | 43,735 | 74% | 53% | 30% | 39% | 65% | 40% | 3.5% | 386,762 | +8% | 1.65m |
| Chicago | 8,778 | 77% | 67% | 66% | 47% | 70% | 50% | 12.0% | 136,135 | +14% | 591k |
| Austin | 11,079 | 83% | 87% | 32% | 49% | 63% | 39% | 6.7% | 136,702 | n/a | 683k |
| Nashville | 10,164 | 91% | 87% | 11% | 61% | 72% | 55% | 12.3% | 180,772 | +5% | 882k |
| New Orleans | 7,303 | 80% | 59% | 81% | 47% | 68% | 47% | 11.6% | 88,655 | +3% | 371k |
| San Diego | 13,342 | 83% | 71% | 77% | 55% | 68% | 43% | 8.7% | 196,361 | +6% | 933k |
| Paris | 78,504 | 89% | 80% | 80% | 22% | 36% | 24% | 3.4% | 557,710 | -1% | 2.65m |
| London | 92,783 | 66% | 98% | 0% | 19% | 55% | 34% | 2.4% | 583,379 | +5% | 2.22m |
| Barcelona | 16,227 | 69% | 59% | 63% | 24% | 81% | 63% | 18.3% | 216,064 | -2% | 801k |
| Rome | 37,483 | 75% | 93% | 86% | 41% | 61% | 33% | 2.9% | 570,095 | +7% | 2.55m |
| Sydney | 20,767 | 79% | 86% | 94% | 34% | 63% | 45% | 6.5% | 218,924 | +10% | 1.07m |
| Mexico City | 30,621 | 67% | 99% | 0% | 43% | 69% | 45% | 3.9% | 506,063 | +19% | 1.98m |

Reviews LTM y/y compares with the full-scope dump nearest 12 months earlier (Sep 2025 for most cities). **Corrected 7 Sep 2026 (A04):** Austin's y/y was previously shown as -8% against its Sep 2025 dump, which is a partial scrape; its nearest full-scope comparator is 2025-06-13 (438 days back, 15,187 listings vs 11,079), so no comparable Austin y/y exists and the cell now reads n/a. Sydney rounds to +11%, not +10%, on the same rule. Every other city's figure is unchanged. Exposed nights feed the regulatory tracker in `research/regulatory/`; they are Inside Airbnb's model, not bookings data.

### 4.3 Churn composition, latest ELIGIBLE year-ago pair per city

| City | Pair | Retention | New share of dump B | Exits with a review LTM | Exits entire home | Exits multi-listing | Adds entire home | Adds multi-listing |
|---|---|---|---|---|---|---|---|---|
| NYC | Oct 2025 → Aug 2026 | 69% | 17% | 16% | 48% | 43% | 53% | 70% |
| LA | Sep 2025 → Aug 2026 | 67% | 30% | 43% | 70% | 64% | 72% | 73% |
| Paris | Sep 2025 → Aug 2026 | 78% | 19% | 50% | 87% | 40% | 89% | 55% |
| London | Sep 2025 → Aug 2026 | 70% | 27% | 53% | 68% | 61% | 74% | 68% |
| Barcelona | Sep 2025 → Aug 2026 | 63% | 25% | 49% | 39% | 70% | 55% | 86% |
| Rome | Sep 2025 → Aug 2026 | 82% | 17% | 63% | 76% | 57% | 72% | 67% |
| Nashville | Sep 2025 → Aug 2026 | 76% | 29% | 78% | 89% | 74% | 90% | 79% |
| Chicago | Sep 2025 → Aug 2026 | 78% | 24% | 63% | 74% | 73% | 73% | 73% |
| New Orleans | Sep 2025 → Aug 2026 | 78% | 21% | 60% | 88% | 66% | 72% | 79% |
| San Diego | Sep 2025 → Aug 2026 | 77% | 24% | 63% | 82% | 72% | 78% | 73% |
| Sydney | Sep 2025 → Aug 2026 | 74% | 37% | 70% | 81% | 66% | 79% | 71% |
| Mexico City | Sep 2025 → Aug 2026 | 76% | 33% | 61% | 60% | 63% | 66% | 64% |

New listings are more likely than exits to belong to multi-listing hosts in every one of the 12 cities shown (on unrounded shares; Chicago, San Diego and Mexico City are within a point): the churn itself professionalises the base. The earlier note said 10 of 13, which counted rounded ties as misses.

**Corrected 7 Sep 2026 (A04):** Austin was previously in this table at 70% retention on the Sep 2025 → Aug 2026 pair. That pair's earlier endpoint (2025-09-16, 10,533 listings) is a partial scrape and is now `pair_eligible=False` (`partial_scope_a`); the best remaining Austin pair, Jun 2025 → Jul 2026, straddles Austin's permanent listing-count step (15,187 → 11,172) and reads 51%, which is coverage rather than churn. Austin therefore has no usable year-ago churn read and is dropped from the table. NYC is 69.5% and now rounds to 69%. All other rows are unchanged: their endpoints were already full-scope.

## 5. How this feeds the pitch

- **ADR decomposition.** Quoted nightly prices on matched, surviving entire-home listings fell 0.9% to 11.0% in the 2025 pairs against reported ADR growth of low single digits (see `data/processed/abnb_kpi_vs_category_quarterly.csv`). That is *consistent with* ADR growth being mix and FX; it is not proof, because the cohort is four cities (Rome, Paris, Austin, Nashville), 13 pairs, Dec 2023 to Sep 2025, asking rates rather than realised rates, and survivors only. Slide candidate: figure `inside_airbnb_lfl_price_yoy.png` next to reported ADR y/y. The slide must carry: four cities of 13 in the panel; median change in the **quoted** nightly rate on listings observed in both dumps; local currency, unweighted by nights; both dumps full-scope scrapes; Austin rests on one pair; series ends Sep 2025 at the price-basis change.
- **Supply growth quality.** Listing counts are flat to down in 10 of 13 cities year over year (up only in Mexico City, Sydney and Nashville) while reviews grow, which is consistent with Airbnb's "quality over quantity" listing removals (Q2 2026 letter) and with the professional share rising. Use 4.2 and `inside_airbnb_multi_listing_share.png`.
- **Regulatory exposure.** Exposed nights per city (4.2) are the base for the regulatory tracker's nights-at-risk estimate. NYC is the template for what a 30-night rule does: entire-home share 55%, top-10 hosts 10% of supply, review velocity flat.
- **Build-forward.** Inside Airbnb now publishes monthly. Re-run `discover` and `download` before the 5 Nov print to add Sep and Oct 2026 dumps; the quote-basis like-for-like series becomes usable once Mar 2026 has a year-ago comparator (Mar 2027), so for the pitch the price story rests on the 2023 to 2025 listed-nightly series.

## 6. Caveats

- Inside Airbnb scrapes public listing pages on a date; it is not bookings data. Price is the listed rate for the first available night (or, from 2026, a fee-inclusive quote), not realised ADR.
- Listing counts depend on Inside Airbnb's city boundary and scraping completeness, both of which changed in 2025 to 2026 (section 2). Use matched-id metrics for trends and full-scope dumps for levels - and matched-id metrics are **not** immune: a partial scrape at either end of a pair makes retention and matched-review change meaningless, which is why every pair now carries `pair_eligible` (section 7).
- Coverage classification is itself revisable. The `partial_scope` flag compares a dump to the largest dump within +/- 200 days, so a *later*, larger scrape can reclassify a past dump. Nine dumps in this panel are labelled partial only because of a later scrape (five Mexico City monthlies, Nashville 2026-04-25 and 2026-05-26, Paris 2023-12-12, Sydney 2026-02-17). Anything replaying a decision as of a past date must use `partial_scope_pit` / `pair_eligible_pit`, never `partial_scope`.
- Reviews lag stays and the review rate drifts; the ratio to stays is assumed constant within a city.
- 13 cities are a convenience sample of Airbnb's largest urban markets, over-weighting regulated cities. Non-urban supply (where Airbnb's growth is) is not covered.
- Licence: CC-BY 4.0. Attribute "Inside Airbnb (insideairbnb.com)" on every slide that uses these numbers.

## 7. Correction 7 Sep 2026: pair eligibility (audit finding A04)

**What was wrong.** `partial_scope` was computed on the snapshot table and applied to the snapshot-level charts, but it was never joined onto the two endpoints of a year-ago pair. Every one of the 103 year-ago pairs went onto the retention and matched-review charts and into `inside_airbnb_like_for_like.csv` without a coverage flag. **25 of the 103 pairs have at least one partial-scrape endpoint.** The clearest case is Paris 3 Mar 2025 (86,064 listings) against 21 Mar 2026 (38,075 listings, a partial scrape): 33.15% retention, which reads as two thirds of Paris leaving the platform in a year. The Jun 2026 Paris dump is back at 77,679 listings and the Sep 2025 → Aug 2026 pair retains 78%. Nothing left.

**What changed in the code** (`analysis/src/inside_airbnb_supply_panel.py`):

- `add_scope_flags(s)` classifies every dump's coverage twice and stores both: `partial_scope` (retrospective, largest dump of the city within +/- 200 days) and `partial_scope_pit` / `partial_scope_pit_long` (point-in-time, trailing 200-day and 400-day windows, so a later scrape can never revise a past label). 41 of 168 dumps are partial retrospectively, 32 point-in-time.
- `add_pair_eligibility(p, s)` joins both endpoints' flags onto every pair **before** any selection and adds `pair_eligible`, `exclusion_reason`, `pair_eligible_pit`, `exclusion_reason_pit`, endpoint coverage ratios, and a `span_step_warning` for pairs whose endpoints are each normal for their era but straddle a step in the city's listing count.
- The same eligibility policy is applied to matched reviews and to matched prices: `retention_clean`, `matched_reviews_ltm_chg_clean` and `lfl_price_chg_median_clean` are null on ineligible pairs, and the figures plot those columns. `price_pair_eligible` additionally requires the existing same-price-basis check (`price_comparable`, unchanged and still essential) and at least 500 matched priced entire homes.
- Ineligible pairs are **kept** in `inside_airbnb_like_for_like.csv` with their reason and are drawn as grey crosses on the retention and reviews figures, so a reader can see what was rejected.
- Fixture test: `analysis/src/overnight/21_test_pair_eligibility.py` (17 checks, all passing). A synthetic city with a partial dump holding a strict subset of the same listings produces 44% raw retention and must not survive into the clean series; a genuine 50% exit at unchanged scope must survive; a run of consecutive partial dumps (the real Nashville Dec 2025 - May 2026 shape) must be caught by the long trailing window.

**Before / after, year-ago retention by city.** Retention arithmetic is unchanged; what changed is which pairs may carry a market interpretation. Full per-pair table in `data/processed/overnight/21_pair_eligibility_delta.csv`, per-city in `21_retention_by_city_delta.csv`.

| City | Year-ago pairs | Now excluded | Mean retention, all pairs (old charts) | Mean retention, eligible only | Delta, pts | Min, all | Min, eligible | Matched reviews y/y, all | Matched reviews y/y, eligible |
|---|---|---|---|---|---|---|---|---|---|
| Austin | 11 | 6 | 51.0% | 55.6% | +4.6 | 36.8% | 48.9% | +0.2% | -0.7% |
| Barcelona | 3 | 0 | 63.0% | 63.0% | 0.0 | 62.7% | 62.7% | +10.5% | +10.5% |
| Chicago | 9 | 2 | 66.6% | 74.2% | +7.6 | 39.6% | 64.9% | +11.1% | +12.1% |
| London | 3 | 0 | 71.0% | 71.0% | 0.0 | 69.6% | 69.6% | +9.7% | +9.7% |
| Los Angeles | 9 | 0 | 70.0% | 70.0% | 0.0 | 64.9% | 64.9% | +6.1% | +6.1% |
| Mexico City | 6 | 2 | 70.5% | 73.7% | +3.2 | 64.0% | 67.7% | +10.6% | +10.6% |
| Nashville | 11 | 6 | 61.2% | 75.2% | +14.0 | 44.1% | 72.2% | +6.7% | +5.1% |
| New Orleans | 6 | 1 | 67.9% | 73.3% | +5.3 | 41.2% | 68.9% | +7.2% | +6.1% |
| New York | 2 | 0 | 69.9% | 69.9% | 0.0 | 69.5% | 69.5% | +4.2% | +4.2% |
| Paris | 13 | 6 | 59.8% | 73.2% | +13.4 | 33.1% | 69.3% | +9.9% | +6.5% |
| Rome | 17 | 2 | 77.3% | 79.1% | +1.8 | 63.4% | 72.8% | +7.6% | +7.5% |
| San Diego | 10 | 0 | 73.2% | 73.2% | 0.0 | 65.9% | 65.9% | +6.2% | +6.2% |
| Sydney | 3 | 0 | 75.3% | 75.3% | 0.0 | 74.1% | 74.1% | +5.4% | +5.4% |
| **Panel** | **103** | **25** | **66.9%** | **72.6%** | **+5.8** | **33.1%** | **48.9%** | **+7.2%** | **+6.9%** |

Panel mean retention rises 66.9% → 72.6% and the panel minimum rises from 33.1% (Paris, the contaminated pair) to 48.9% (Austin, which still straddles its scope step). Matched-review y/y barely moves (+7.2% → +6.9%): a partial scrape drops listings but the survivors' review counts are unaffected, so the review series was much less damaged than the retention series. Six cities (Barcelona, London, LA, NYC, San Diego, Sydney) are unchanged.

**Point-in-time complication.** 27 pairs are ineligible on the point-in-time rule against 25 retrospectively; 22 are in both sets. Three pairs the retrospective rule rejects were **not** rejectable at the time (Mexico City 2025-06-25 → 2026-03-30 and → 2026-04-29, Nashville 2025-06-19 → 2026-05-26): their later dump only looks partial once a larger scrape exists. Nine dumps in total are in that position. Conversely the point-in-time rule rejects five pairs the retrospective rule accepts, because a run of consecutive partial dumps hides itself from a 200-day trailing window and only the 400-day lookback catches it — that lookback also fires on Austin's permanent scope reduction and Barcelona's contraction, which is the conservative answer for a frozen forecast but is not evidence the market shrank. **Rule for any predictive replay: use `pair_eligible_pit`, and record the flag with the prediction, so a later scrape cannot silently rewrite a frozen call.**

**Not fixed here, by design.** An Inside Airbnb scope reduction and a genuine market contraction cannot be separated from listing counts alone. The partial dumps are uniform subsamples, not geographic truncations (all 20 Paris arrondissements appear in the 38k dump), so neighbourhood coverage does not discriminate either. `span_step_warning` marks the five affected pairs (four Austin, one Barcelona) rather than deciding for the reader.
