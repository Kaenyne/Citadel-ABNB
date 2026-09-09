# LOS step 1: what a night costs by length of stay, from host discount structures

`analysis/src/adr/14a_los_discount_ratios.py` -> `data/processed/adr/14a_los_discount_by_listing_summary.csv`, `14a_los_bucket_price_ratios.csv`

## Method
Every 2026 Inside Airbnb dump from 16 Mar carries one stay quote per listing. `price_quote_raw`
holds a line-item ledger: an undiscounted base, then signed discount lines summing to the
discounted subtotal — verified to 5e-6 relative error on 183k quotes, so nothing is inferred.
Because the discounts are a share of that base, each listing's discount **rate** is recoverable
whatever its quoted length. For each quote we form the per-night price factor against its own
undiscounted rate and index bucket means to the under-7 bucket, weighting by
`estimated_occupancy_l365d`. 34 markets, 139 quote dumps, 2.61m parsed quotes (609k in the latest-dump cross-section).

**Every line-item type found:** base = `nightly_subtotal` ("3 nights x …") or, for 28+, `other`
"Average monthly price" (mislabelled — it is the whole-stay subtotal). Host discounts =
Weekly stay / Monthly stay / **Long stay** (a separate custom-threshold label) / Special offer /
Early booking / Last-minute. Platform = `other` "Airbnb monthly stay savings". Excluded:
Taxes, Resort fee, Total / Monthly total. No service or cleaning fee lines exist — subtotal basis.

## Headline (latest dump per market, ex 6 regulatory-min markets, <7 = 1.00)

| region | 7-27n host | 7-27n host+platform | 28+n host | 28+n host+platform |
|---|---|---|---|---|
| NA | 0.964 | 0.964 | 0.878 | 0.858 |
| EMEA | 0.968 | 0.968 | 0.876 | 0.855 |
| LatAm | 0.972 | 0.972 | 0.874 | 0.857 |
| APAC | 0.958 | 0.958 | 0.840 | 0.820 |
| **Global (10-K nights wts)** | **0.966** | **0.966** | **0.872** | **0.852** |

Pooled over all 2026 dumps: 0.955 / 0.862 — same picture, ~1pt lower. Including the six
regulatory-min markets raises 28+ to 0.888 / 0.869.

## Selection caveat
Each listing is quoted once, for its first available window, so bucket membership is set by
`minimum_nights`. Even after excluding the six markets where `min_nights>=28` exceeds 30% of
listings (NYC 75%, LA 46%, Singapore 46%, Hong Kong 45%, Barcelona 37%, New Orleans 36%),
**94% of 28+ quotes still come from listings that require 28+.** These are ratios by *quoted*
bucket, not a realised mix, and the incidence shares are conditional on the bucket. The bucket
shares here (28+ = 8% of quotes, 5.6% of quote-weighted nights) are far below the ~17-18% of
nights Airbnb discloses for long-term stays — do not use them as the mix; that is 14b's job.

## Surprises
- **Airbnb funds a real slice of the monthly discount.** "Airbnb monthly stay savings" is on
  59% of 28+ quotes at 2.7% of the subtotal — ~2pp of the 28+ wedge is platform money, not the
  host's. Incidence is 67% in EMEA and 64% in APAC but only **34% in LatAm**.
- The monthly discount is not universal: 55% of 28+ quotes carry one, but it averages **20.7%**
  when present. Weekly: 43% incidence, 9.2% mean — remarkably uniform across regions.
- The under-7 bucket is *not* undiscounted: 16% of short quotes carry a last-minute discount
  (9% mean) and 8% a Special offer (18% mean), because the quoted window is the first available
  and therefore near-term. Indexing to the under-7 mean nets this out; the LOS-only variant
  (`ratio_los_only`, 0.946 / 0.853 global) is the cleaner isolation of length effects.
- APAC discounts hardest at 28+ (0.840) on both higher monthly incidence (63%) and rate.
