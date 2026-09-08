# Party size: where Airbnb actually competes with hotels

Thesis (Jessie): small parties choose between a hotel and an Airbnb; large parties default to Airbnb regardless of stay length. The data agrees, and it tells you *where* the stay-length / kitchen findings matter.

## Headline

| Party size | Hotel cost/night (rooms × $159 ADR) | Airbnb entire home (price a guest is quoted) | Airbnb ÷ hotel | Who wins on price |
|---|---|---|---|---|
| 1 | $159 | $86 | 0.54x | contestable (budget hotels compete) |
| **2** | $159 | **$164** | **1.03x** | **line ball — the real battleground** |
| 3 | $317 | $191 | 0.60x | Airbnb |
| 4 | $317 | $227 | 0.72x | Airbnb (families w/ small kids can still fit 1 hotel room) |
| 5–6 | $476 | $277–330 | 0.58–0.69x | Airbnb |
| 7–8+ | $635 | $377–483 | 0.59–0.76x | Airbnb — and they get a shared living space + kitchen on top |

**Corrected 7 Sep 2026.** This table previously read 0.69 / 1.22 / 0.72 / 0.86 / 0.70–0.82 / 0.70–0.88 because
it multiplied the Jun-2026 Inside Airbnb `price` by 1.14 for the guest service fee. From the Mar-2026 dumps that
field is already a fee-inclusive stay quote, so the fee was counted twice and every ratio was 12.3% too high. The
couples cell is the one that changes character: Airbnb is ~3% dearer than a hotel there, not 22%, so the price gap
that made it "the hotel's segment" is mostly an artefact. What still favours hotels for couples is the 1–2-night
cleaning-fee penalty and check-in convenience — the argument below survives, the price evidence for it does not.

- **Cross-over is 3 people.** The moment a group needs a second hotel room, an entire-home Airbnb is 14–30% cheaper *before* counting the kitchen and shared space. Large groups are captive: price and product both point to Airbnb, stay length irrelevant.
- **At 2 people Airbnb costs ~22% more than a hotel room** (and a private room is 27% cheaper) — this is the only segment where the hotel is a live alternative, so it's where kitchen, stay length, loyalty points, and direct-booking all actually bite.
- **Contestable share of Airbnb stays: ~25–50%.** Private rooms + entire homes sleeping 1–2 = 25% of booked stays; add homes sleeping 3–4 (often booked by couples) = 48%. Homes sleeping 5+ = 52% of stays, 7+ alone = 33% — captive.
- **Airbnb's own numbers rhyme:** family travel ≈ 1 in 5 nights (H1 2024, +15% y/y), multigenerational bookings +35%, ~40% of U.S. listings have 3+ bedrooms; 20% of Thanksgiving family bookings were 10+ guests (Airbnb newsroom, Oct 2024).

## Why stay length still matters — in the contestable half

- Airbnb's per-stay **cleaning fee** is amortised over nights; a 1–2 night couple's trip is where Airbnb loses to a hotel on price, and where the +1.2–1.5-night kitchen effect (see `kitchen_wholehome_stay_length.md`) is Airbnb's lever: the longer the trip, the more the kitchen saves and the less the cleaning fee hurts.
- Small units are Airbnb's *longest* stays (sleeps 1–2 = 5.6 nights vs 7+ = 4.3): the contestable segment self-selects into longer, work-adjacent, kitchen-using trips. Short couple trips are where hotels are winning by default.
- So the competitive map is a 2×2: **large party** → Airbnb at any length; **small party, 3+ nights** → Airbnb favoured (kitchen, per-night cost); **small party, 1–2 nights** → hotel favoured (no cleaning fee, loyalty, check-in convenience). Hotels' extended-stay build-out (37% of pipeline, Kalibri) is an attack on the small-party/long-stay cell, not the group cell.

## Pitch angles

- **Bull:** ~half of Airbnb's stays sit in a segment hotels can't price-match without adding rooms; hotel supply growth, loyalty programs and direct-booking leakage only touch the other half. Group/family travel is growing faster than the platform (family +15% vs total nights +8–10%).
- **Bear:** the captive segment books the *shortest* stays and is event/weekend-driven (Nashville 4+ bed = 3.8 nights) — cyclical, price-sensitive on ADR, and exposed to STR regulation (whole-home caps hit exactly this supply). And the contestable couple segment is where Airbnb is losing share to hotels on 1–2 night trips.
- **Next:** replace `accommodates` (capacity) with actual party size — Airbnb's reviews/guest counts aren't public, so use the team's Inside Airbnb store to bucket by *bedrooms* instead of capacity as a robustness check; pull metro-level ADR (STR top-25) since big-city hotel ADR ($200–300) pushes the cross-over down to 2 people in NYC/SF/Boston.

## Method & caveats

- Airbnb price: listing-weighted average of city medians of `price` for active entire homes (≥1 review in last 12 months) with `accommodates` = party size; 7 U.S. cities, 52.4k listings. **No fee is added**: on the Jun-2026 dumps `price` is `price_quote_price_per_night`, a stay quote already inclusive of the guest service fee and of cleaning amortised over the stay (verified identical across 10,321 Austin entire homes). The earlier build used 9 cities and applied ×1.14 to this same basis.
- Because the quote basis is what a guest actually pays, it is also immune to the 13 Oct 2026 host-only fee migration: switching hosts gross up the listed rate ~14.8% and the checkout fee disappears, so the *listed* series carries a 12–18% step that is not pricing power while the *quoted* price is roughly unchanged (`host_only_fee_history_and_elasticity.md`).
- Hotel: 2 people per room × CoStar/STR FY2024 U.S. ADR $158.67; taxes and resort fees excluded on both sides.
- `accommodates` is capacity, not party size; couples do book 4-sleepers, so the contestable share is a range (25–50%).
- Stay-share figures reuse the 8-city booked-run dataset (273k runs, ≤30 nights) from `kitchen_wholehome_stay_length.md`.

## Files

- `data/processed/insideairbnb_price_by_accommodates.csv` — per-city medians/quartiles by room type × accommodates
- `data/processed/party_size_cost_crossover.csv` — the table above
- `analysis/src/party_size_crossover.py` — chart
- `docs/figures/party_size_crossover.png`

## Sources

- Inside Airbnb June-2026 U.S. scrapes: https://insideairbnb.com/get-the-data/
- CoStar/STR FY2024 U.S. hotel ADR $158.67, occupancy 63%: https://www.asianhospitality.com/costar-u-s-hotels-post-record-adr-revpar-in-2024/
- Airbnb guest service fee (~14%): https://www.airbnb.com/help/article/1857
- Airbnb newsroom, family/group travel stats (Oct 28 2024): https://news.airbnb.com/how-and-where-families-are-traveling-this-thanksgiving/
- Kalibri Labs extended-stay pipeline share: https://www.kalibrilabs.com/extended-stay-development/
- Airbnb FY2025 10-K (nights per booking by region): https://www.sec.gov/Archives/edgar/data/1559720/000155972026000004/abnb-20251231.htm
