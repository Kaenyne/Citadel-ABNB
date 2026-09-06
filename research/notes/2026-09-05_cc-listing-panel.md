# Common Crawl matched-listing panel: airbnb.com/rooms pages, 50 crawls, Jan 2021 to Aug 2026

**What this is:** the panel the plan of attack (section 4) asked for from Common Crawl's archive of Airbnb listing pages: listing survival between crawls, same-listing review velocity, Superhost and Guest Favorite share, and geography mix. Plan-of-attack branch 2. Go/no-go was "stop if fewer than ~500 listings match a year apart"; 208,159 do, so the panel went ahead.
**Compiled:** 2026-09-05. Author: Krishang, with Claude Code. Script: `analysis/src/cc_listing_panel.py` (harvest, survival, fetch, panel, figures), building on `analysis/src/cc_airbnb_probe.py`. Outputs in `data/processed/cc_*.csv` and `analysis/figures/cc_*.png`.
**Policy:** every request went to Common Crawl (index shards and WARC records on `data.commoncrawl.org`); nothing touched airbnb.com. Theo's scraping rule blocks Airbnb-controlled sources; reading a public web archive is outside that rule and the team should log it as such. Common Crawl itself rate-limited this IP twice (index API, then the data host) before the pace was cut to two workers with a delay; the script now pauses on a block and resumes from cached files.

---

## 1. Headline findings

1. **No price, confirmed at scale.** 3,000 full page renders across six years and zero contain a nightly price (`structuredDisplayPrice` is null or absent in every era). The archive cannot give a pricing panel; Inside Airbnb does (`research/notes/2026-09-05_inside-airbnb-supply-panel.md`).
2. **Listing survival is 85% to 90% a year on, and older listings die slower than in Inside Airbnb's city dumps.** Among listings the crawler re-fetched after a first successful capture, the share still returning a live page was 90% in 2022, 85% in 2023 and 2024, and 88% in 2025 and 2026 (informative crawls only, section 2). By listing age: 92% at 2 to 12 months, 87% at 1 to 2 years, 86% at 2 to 3 years, 84% past three years. These are higher than Inside Airbnb's 63% to 82% year-ago retention because the crawler only re-visits pages it can still reach by link, which selects for listings that are still marketed.
3. **Same-listing review velocity has been flat for five years.** On 1,487 matched pairs (median 481 days apart), listings added a mean of 15 to 27 reviews a year depending on the window, with medians of 8 to 23. The most recent window (2025 to 2026, 81 pairs) is 19 reviews a year mean, 11 median, with 6% of listings adding no review, versus 21 mean, 12 median and 13% no review in 2021 to 2022. No acceleration and no collapse in bookings per surviving listing.
4. **The captured base has professionalised.** Superhost share of parsed captures rose from 58% (2021) to 61% (2026); entire-home share from 80% to 90%; median review count from 30 to 75. Guest Favorite, parsed reliably from 2025, is 71% of 2025 captures and 52% of 2026 captures. Hosts in 2025 to 2026 captures have a median 7 years hosting and 198 host-level reviews.
5. **The archive's geography shifted toward North America.** North American listings were 28% of 2021 captures and 48% of 2026 captures; Europe fell from 48% to 34%. This is the crawler's reach (the 2026 US pages arrive with `utm_source=chatgpt.com`), not Airbnb's supply mix, and it is the main reason cross-year comparisons in 4 need the same-listing framing.

## 2. What was harvested

| Layer | Size | Notes |
|---|---|---|
| CDX index rows, `airbnb.com/rooms/*` plus 8 country domains (co.uk, ca, com.au, de, fr, es, it, com.br) | 2,078,434 rows over 50 crawls (CC-MAIN-2021-04 to 2026-34); 1,200,597 unique listing ids; 1,062,873 with a status-200 full render | 80k to 110k rows per crawl in 2021, 17k to 40k from 2023 (the crawler's Airbnb budget fell). `data/raw/commoncrawl/index/<crawl>__<domain>.jsonl.gz`, summary in `data/processed/cc_index_summary.csv` |
| WARC records | 3,000 full renders (1,500 listings x earliest and latest capture), 0.5 to 1.0 MB HTML each | `data/raw/commoncrawl/records/<crawl>/<id>.warc.gz`, gitignored |
| Parsed captures | 3,000 rows, 100% with review count, Superhost flag, room type and coordinates | `data/processed/cc_listing_panel.csv` |
| Matched pairs | 1,500; 1,487 with a non-negative review delta | `data/processed/cc_matched_listings.csv`, window summary `cc_panel_summary.csv`, capture-year summary `cc_panel_by_year.csv` |
| Survival | 48 crawls with re-fetches, 36 informative | `data/processed/cc_listing_survival.csv`, `cc_listing_survival_by_age.csv` |

Index rows were read straight from each crawl's cdx shards on `data.commoncrawl.org` (binary search of `cluster.idx`, then the 4 to 10 compressed blocks covering the `com,airbnb)/rooms/` key range), because the `index.commoncrawl.org` API blocked this IP after a few dozen queries. Shard rows harvested in the first pass (crawls 2021-04 to 2023-14) carry no capture timestamp; the crawl's ISO-week date stands in (`ts_from_crawl`), which is within two weeks of the truth.

**Informative crawls.** From CC-MAIN-2021-17 to 2022-05 and from CC-MAIN-2025-43 to 2026-04 Airbnb answered 200 for essentially every re-fetched listing, including dead ones (zero to 65 removals against 5.5k to 19k re-fetches), so those 12 crawls carry no removal signal and are excluded from the survival series (`status_informative`, threshold 2% removals). Elsewhere removals run 4% to 16% of re-fetches, mostly 404 and 410.

## 3. Definitions

| Field | Definition |
|---|---|
| Full render | Status 200 and WARC record at least 60 KB compressed. Smaller records are bot-wall stubs or redirects |
| Survival | For each crawl B, listings first captured 200 at least 60 days earlier and re-fetched in B: share returning 200 (live) versus 404/410 (removed) or 3xx (redirect). Absence from B is not evidence of anything |
| Matched pair | Listing with full renders in two crawls at least 270 days apart: earliest and latest capture, sampled with equal quotas by year of the later capture (1,500 of 208,159 eligible) |
| Reviews | `visibleReviewCount` (2021 to 2023), `ratingCount` in the LD+JSON block or `reviewCount` (2024 onward); numbers are quoted strings in 2021 pages |
| Review velocity | (reviews_b - reviews_a) / days apart x 365, on pairs with a non-negative delta |
| Guest Favorite | `isGuestFavorite` true/false; only serialised for qualifying listings in the 2023 to 2024 template, so reported from 2025 |
| Region | Coarse lat/lng boxes: NA, LatAm, Europe, MEA, APAC |

## 4. Tables

### 4.1 Survival of re-fetched listings (informative crawls)

| Capture year of crawl B | Informative crawls | Re-fetched | Live | Removed | Redirect | Survival |
|---|---|---|---|---|---|---|
| 2022 | 5 | 75,888 | 68,341 | 5,277 | 2,265 | 90.1% |
| 2023 | 5 | 63,903 | 54,187 | 9,125 | 589 | 84.8% |
| 2024 | 10 | 99,992 | 85,598 | 13,845 | 467 | 85.6% |
| 2025 | 9 | 91,496 | 80,163 | 10,973 | 341 | 87.6% |
| 2026 | 7 | 81,046 | 71,082 | 9,721 | 230 | 87.7% |

By age since first capture: 2 to 12 months 92.1% (83,812 re-fetches), 1 to 2 years 87.2% (166,527), 2 to 3 years 85.6% (73,383), over 3 years 83.8% (88,603). Per-crawl series and figure: `cc_listing_survival.csv`, `cc_listing_survival.png`.

### 4.2 Same-listing review velocity by window

| Window (year a to year b) | Pairs | Median days apart | Median reviews at a | Reviews per year, mean | Reviews per year, median | No new reviews | Superhost a → b |
|---|---|---|---|---|---|---|---|
| 2021 → 2021 | 250 | 273 | 21 | 18.4 | 9.4 | 19% | 53% → 54% |
| 2021 → 2022 | 249 | 427 | 21 | 21.1 | 11.5 | 13% | 55% → 52% |
| 2021 → 2023 | 158 | 707 | 42 | 26.6 | 19.2 | 8% | 63% → 58% |
| 2021 → 2024 | 97 | 1,102 | 55 | 23.2 | 16.3 | 4% | 67% → 61% |
| 2021 → 2025 | 73 | 1,508 | 39 | 26.8 | 21.6 | 3% | 70% → 68% |
| 2021 → 2026 | 47 | 1,786 | 48 | 24.7 | 13.2 | 2% | 72% → 72% |
| 2022 → 2023 | 87 | 446 | 37 | 19.4 | 14.5 | 5% | 59% → 59% |
| 2022 → 2024 | 70 | 670 | 23 | 16.6 | 12.4 | 6% | 60% → 56% |
| 2023 → 2024 | 80 | 392 | 30 | 15.6 | 9.4 | 9% | 50% → 51% |
| 2024 → 2025 | 94 | 373 | 30 | 16.7 | 11.7 | 12% | 60% → 59% |
| 2024 → 2026 | 65 | 543 | 31 | 20.3 | 11.6 | 8% | 58% → 49% |
| 2025 → 2026 | 81 | 389 | 28 | 19.2 | 10.6 | 6% | 51% → 64% |

Windows with under 30 pairs omitted (2022 → 2022, 2022 → 2025, 2022 → 2026, 2023 → 2023, 2023 → 2025, 2023 → 2026, 2025 → 2025); all rows in `cc_panel_summary.csv`. Longer windows show higher velocity because a listing that survived five years is a better listing (survivorship), which is why the like-for-like reading is the short windows: 2021 → 2022, 2023 → 2024, 2024 → 2025 and 2025 → 2026 sit at 16 to 21 reviews a year mean and 9 to 12 median.

### 4.3 Captures by year

| Capture year | Captures | Superhost | Guest Favorite | Entire home | Median reviews | Median rating | NA | Europe | LatAm | APAC |
|---|---|---|---|---|---|---|---|---|---|---|
| 2021 | 1,129 | 58% | n/a | 80% | 30 | 4.90 | 28% | 48% | 6% | 14% |
| 2022 | 475 | 56% | n/a | 84% | 38 | 4.89 | 31% | 37% | 10% | 17% |
| 2023 | 393 | 55% | n/a | 89% | 50 | 4.90 | 37% | 42% | 7% | 9% |
| 2024 | 413 | 57% | n/a | 91% | 51 | 4.89 | 40% | 37% | 9% | 11% |
| 2025 | 338 | 58% | 71% | 89% | 54 | 4.92 | 40% | 39% | 7% | 11% |
| 2026 | 250 | 61% | 52% | 90% | 75 | 4.92 | 48% | 34% | 5% | 11% |

Captures are the matched sample, so the 2021 column is weighted to listings that survived to a later crawl.

## 5. How this feeds the pitch

- **One or two exhibits, as budgeted.** `cc_review_velocity.png` (bookings per surviving listing flat for five years) is the usable one; `cc_listing_survival.png` supports the supply-churn slide alongside Inside Airbnb's retention series. The professionalisation series duplicates Inside Airbnb with a worse sample and should stay in the appendix.
- **Cross-check for Inside Airbnb.** Both sources say the same thing about supply: high churn, rising professional share, no pricing signal here. Where they differ (survival 85% to 90% here versus 63% to 82% retention there) the gap is the crawler's link-following bias, which is worth one sentence on the slide.
- **Not worth more hours.** The plan capped this at 8 to 12 hours; the harvest and fetch took the bulk of it because of Common Crawl's rate limits. Extending to more pairs is cheap now (`fetch --n`), but the sample bias does not shrink with size.

## 6. Caveats

- Common Crawl's Airbnb sample is whatever the crawler reached: pages linked from elsewhere, skewed to popular and long-lived listings, with a geography that drifted toward North America. It is not a random draw of supply.
- Matched pairs condition on survival to the second capture; velocity estimates apply to surviving listings only.
- Review counts lag stays by weeks; the review rate per stay is assumed stable.
- 11 of 1,500 pairs show a lower review count at the later capture (removed reviews or a parse mismatch) and are excluded from velocity.
- Capture timestamps for crawls before CC-MAIN-2023-23 are the crawl's nominal week; days-apart for those pairs is approximate.
- Region is a lat/lng bounding box, not a country lookup.
