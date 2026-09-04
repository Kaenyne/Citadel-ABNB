# Airbnb (ABNB) — research notes for the Citadel pitch

Compiled 2026-09-04 from filings, earnings releases, and alt-data pulls. Figures are as-reported unless marked as estimates. Companion analysis: `../analysis/air_traffic_study/README.md` (air-traffic correlation study).

## Competition constraints

- Citadel Intercollegiate Stock Pitch Competition 2026: 2-page memo (incl. appendix) + model; long or short; 3–12 month horizon; universe of eight tickers (ABNB, ADBE, CPRT, GEV, NCLH, NKE, SBUX, SPOT). Prelims due Oct 2, 2026; finalists notified Oct 12; event Oct 22–24, NYC.
- Judges are Citadel fundamental PMs/analysts: they reward a variant view vs. consensus, catalysts inside the window, and explicit risk/reward. With eight tickers, ABNB long is likely the most-submitted idea — differentiation must come from the specific variant view and the data behind it.

## Business model

- Two-sided marketplace: ~8.3M listings, hosts + guests. Revenue = fees on gross booking value; take rate ≈ 13–14% (Q2 2026: $3.6B revenue on $27.2B GBV = 13.2%).
- Guests pay at booking, hosts are paid at check-in → Airbnb holds float and earns interest; negative working capital. Revenue is recognized at check-in, so nights *booked* (Q1 peak) lead revenue (Q3 peak).
- Asset-light: capex negligible, FCF ≈ operating cash flow.
- Growth vectors management names: hotels (boutique inventory; hotel nights growing ~3x faster than homes; ~35% of first-time hotel bookers return to book homes), Experiences (supply +~80% YoY in Q2 2026), Services (grocery, car rental, airport pickup, luggage, resort passes), international expansion markets (India, Brazil, Japan; expansion-market origin nights growing ~2x core), AI in product and support (support cost per booking –16% YoY; ~45% of issues resolved without a human).

## Financials

| | FY2024 | FY2025 | TTM Jun-26 |
|---|---|---|---|
| Revenue | $11.10B | $12.24B (+10%) | $13.16B |
| Gross margin | ~83% | ~83% | ~83% |
| Operating income (GAAP) | $2.55B (23%) | $2.54B (21%) | $2.74B (21%) |
| Net income | $2.65B | $2.51B ($4.04 EPS) | $2.69B ($4.42) |
| Operating cash flow ≈ FCF | | $4.65B | $4.86B |
| Buybacks | | $4.35B | $4.68B |

- Adjusted EBITDA margin runs ~35% (stock comp etc. below the line) — GAAP operating margin ~21%; don't mix them.
- Balance sheet: cash ~$12.1B, debt ~$2.5B, net cash ~$9.6B (Aug 2026).

### Quarterly KPIs (see `data/processed/airbnb_quarterly_kpis.csv` for the full series)

- Q2 2026: revenue $3.6B (+17%), GBV $27.2B (+16%; +15% ex-FX), nights & seats booked +10% (accelerating from Q1), adj. EBITDA $1.3B (35% margin), net income $816M, first-time bookers +11% (best in four years; Gen Z-driven), $1.1B buyback.
- Q3 2026 guide: revenue $4.69–4.77B (+15–17%, includes ~3-pt FX tailwind), GBV mid-teens, adj. EBITDA margin slightly down YoY (investment timing), take rate ~flat YoY.
- FY2026 guide (raised Aug 2026): revenue growth at least mid-teens; adj. EBITDA margin at least 35.5%. Take rate flat for 2026 due to incentives in new businesses.
- Regional revenue (by listing location) growth, Q2 2026: North America +15.8% (highest in ~3 years), EMEA +15.6%, Latin America +26.0%, Asia Pacific +16.9%. Full series in `data/processed/airbnb_regional_revenue_quarterly.csv`.

## Valuation and stock (as of Aug 31 – Sep 1, 2026)

- Price ~$183; market cap ~$108B; EV ~$98B; 52-week range $110.81–$193.45; +40% over 12 months.
- Forward P/E ~34x; trailing EV/EBITDA ~35x; FCF yield ~4.5%; short interest ~3.2% of float.
- Consensus: Buy (45 analysts), average target ~$177 — stock trades above the average target after the Aug 7 print (+17.4% on the day, 15.8M shares, ~4–5x normal volume; highest since April 2022). Pre-print week was flat (–0.3%).
- Peers: Booking Holdings ~$150B EV, ~14.6x EV/EBITDA, ~18x fwd P/E; Expedia (Vrbo) ~$35B EV, ~12.7x EV/EBITDA, ~14x fwd P/E, +43% 12-mo. ABNB trades at ~2x Booking's earnings multiple.

## Competitors

- Booking Holdings (Booking.com alternative accommodations — more total listings, stronger in Europe, bundles homes with dominant hotel inventory), Expedia/Vrbo (US whole-home), hotel direct booking + loyalty, Viator/GetYourGuide/Klook in experiences, Google in travel search. Airbnb's hotel push puts it in direct OTA competition for hotel inventory.

## Demand and supply signals

- FIFA World Cup 2026 (Jun 11–Jul 19; 16 host cities in US/Canada/Mexico): "millions of guests," 150K+ new listings in host cities, typical host ~$3,000, avg nightly rate < $250, ~14% first-time users, ~19% booked a second stay. Management called it "one obvious contributor" to North America's best quarter in ~3 years but did not quantify; rough estimate $1–2B GBV across Q2/Q3 (1–3 pts of growth), partly displacement. Sales & marketing +27% YoY to $875M in Q2. After the Paris Olympics, >50% of new listings were still active six months later. Q2–Q3 2027 lap the World Cup.
- Listings by country (Inside Airbnb, late 2025; ~8.35M listings): US 1.52M (18%), France 984K (12%), Brazil 560K, Italy 529K, UK 379K, Spain 366K, Mexico 291K, Germany 251K, Canada 177K, Australia 165K. Top 10 = ~63%; no single city is material.
- Largest markets by active listings (AirROI, Aug 2026): Paris 40K, São Paulo 34K, Rio 32K, London 31K, Rome 29K, Buenos Aires 23K, Mexico City 21K, Dubai 20K, Florianópolis 20K, Kuala Lumpur 19K. New York ~10K active (from ~41K in 2023, Local Law 18). Four of the top ten are in Latin America. See `data/processed/top_airbnb_cities_listings_airports.csv`.
- Regulation: NYC LL18 (2023), Barcelona license phase-out by Nov 2028, Spain blocked ~66K listings (May 2025), Portugal/Lisbon licensing rules, Greece new-permit freeze in Athens through 2026 and bans in several islands from Oct 2025, EU STR data-sharing regulation. Dispersion is Airbnb's defense: no city is material to revenue.
- Air traffic is not a demand signal for Airbnb (see README): since 2024, correlation of TSA/BTS/IATA growth with Airbnb nights growth is ~0; Airbnb grew 7–10% nights while US air traffic was flat-to-negative and global international RPKs turned negative in Q2 2026. Regionally, faster-air-growth regions are Airbnb's faster-growth regions (cross-sectional r = +0.81), but timing doesn't line up.

## Debates for the memo

- Bull: accelerating nights growth and first-time bookers, hotels/services/experiences opening new TAM, AI-driven margin leverage, 35%+ EBITDA margins with $5B FCF and buybacks, net cash, growth decoupled from travel macro.
- Bear: 34x forward earnings vs Booking at 18x after a +17% post-print rerating; take rate flat with incentives funding new businesses; Q3 margin guided down; Q3 growth includes ~3-pt FX; single-service-fee rollout to hosts by year-end is a friction risk; World Cup comp in 2027; regulation in top European cities; Middle East headwinds.
- Variant-view candidates: (1) 2027 take rate / margin path from hotels and services vs. consensus; (2) supply retention after mega-events; (3) regional mix shift (LatAm/APAC at ~20% revenue growth) and what it does to GBV per night; (4) decoupling from air travel as evidence of share gain.

## Key dates

- Q3 2026 results: early November 2026 (after the competition finals). Booking Holdings and Expedia report late Oct / early Nov — read-throughs.
- Competition: prelims Oct 2; finals Oct 22–24.

## Sources

Airbnb Q2 2026 results (news.airbnb.com), Airbnb shareholder letters Q1 2022–Q2 2026, Airbnb 10-Q/10-K regional revenue (SEC EDGAR, CIK 1559720), Airbnb World Cup recap (Aug 6, 2026), StockAnalysis.com (financials, statistics), Yahoo Finance price history, Inside Airbnb, AirROI, letbloom country ranking, Citadel competition page, TSA/BTS/IATA/NTTO (see README).
