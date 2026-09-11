# ADR Q3 2026 nowcast: can ADR be forecast like nights? Synthesis

- **Date:** 2026-09-11. **Author:** Krishang Surapaneni (compiled with Claude Code).
- **Branch:** `krish/adr-q3-nowcast`, commits 9c69f73 (I), 4b7e7cf and f2baab8 (J), on top of the WIP sweep 6957b50. Not pushed. Nothing on main changed.
- **Read next:** `research/notes/adrq3/I_adr-mix-terms-3q26.md` and `research/notes/adrq3/J_adr-pricing-residual-and-card-v2.md`.

## 1. The answer

**No, not in the way nights can be.** The nights nowcast worked because the reviews data is a quantity series that beats a naive forecast out of sample. ADR has no price series: 2026 calendars carry no price, Inside Airbnb stopped populating calendar prices with the June 2025 dumps, the fee-inclusive quote index already failed, and none of nine external price proxies beats naive against the pricing residual. The three mix terms you named can be measured for Q3-to-date from the nights data, and they now are, but they are level terms that explain a minority of ex-FX ADR. The like-for-like pricing residual, which carried all of 1H26, remains unobserved and sets the band.

**Card v2 for 3Q26: reported ADR +3.0% y/y, $176.5, band $174.2 to $178.8 (+1.7 to +4.4%).** Ex-FX +3.5%. 4Q26: +3.6%, $173.6, band $171.3 to $175.8. That is 0.2 to 0.3 points below the H card because the measured geographic mix is a larger drag than assumed. FX estimator choice still spans 1.4 points (+2.3% on the euro fit, +3.7% on the baskets).

**Pre-registered test: not passed.** Card v2 with the persistence residual has walk-forward RMSE 0.903 pp against 0.908 for naive "same ex-FX as last quarter" on 1Q24 to 2Q26 (ratio 0.994), 1.042 on 2Q24 to 2Q26, jackknife 0.87 to 1.05. A tie is not a pass. It does beat the AR(1) benchmark (0.79) and the original H component route (0.70), so the measured mix terms fixed the H card's bias, but the residual rule is late by 0.8 to 1.7 points into accelerations and that is the whole error.

## 2. What was measured

| Term | 3Q26-to-date | ADR contribution | Evidence status | Moved vs 2Q26? |
|---|---|---|---|---|
| Party size (unit size) | booked capacity +1.35% y/y on 2.05mm vintage-matched reviews, 119 markets | **+0.80 pp** (0.53 to 1.00), coefficient 0.592 reproduced from script 13 | Measured, reproducible (refreshed dumps reproduce the existing series, r 0.97); level term with no timing signal (r -0.17 vs ex-FX ADR) | No: 2Q26 +0.87 pp, 3Q25 +0.81 pp. NA +2.5%, EMEA +0.7%, APAC +1.6%, LatAm -0.1% |
| Length of stay | 28+ night share of blocked-run nights -0.5 pp y/y at the August vintages, flat on calendar Q3 windows | **+0.06 pp** (-0.08 to +0.29); H had +0.30 assumed | Measured on blocked runs, not bookings; unvalidated (no 2Q26 comparison exists) | Direction matches the 14c snapshots, size smaller |
| Geographic mix | E regional split NA +6.9 / EMEA +0.9 / LatAm +27.5 / APAC +10.0 | **-1.43 pp** (-1.57 to -0.94); H -1.19, WS-C -1.24, 2025 actual -1.58 | Measured split, unvalidated mapping (E-projected shares reproduce the disclosed-share term with RMSE 0.4 to 0.7 pp, n 10) | Larger drag than the card assumed |
| Sum of the three | | **-0.57 pp** vs H card -0.15 | | |
| New business dilution, interaction | from H | -0.48, -0.10 | Assumed | |
| Pricing residual | no observation | **+4.61 pp** persistence rule, band 2.4 (2023-25 mean) to 4.85 (2Q26) | Unobserved; no proxy enters | Unknown. This is the number the print resolves |
| FX | from WS-B | -1.1 (euro fit) to +0.3 (baskets), midpoint -0.4 | Fitted, r 0.99 historically; estimator choice open | |

## 3. What the calendar-price backtest settled

The one new asset was the 2024-25 calendar vintages with listed prices. They close the route rather than open it. Only 98 of 227 pre-2026 vintages carry prices and none after 28 May 2025, leaving six year-apart pairs (Austin, Nashville, Paris, Rome). On 68 million matched listing-dates, 72 to 77 percent of same-listing same-stay-date prices are identical a year later and the matched median year-over-year is exactly zero in every market, lead bucket and stay quarter. Hosts do not reprice existing dates; Airbnb's realised ADR growth comes from composition and from new listings, which a same-listing panel excludes by construction. The composition indices that do move are negatively correlated with the residual (r -0.61 to -0.85, n 6). Do not re-run this unless Inside Airbnb restores prices, and do not request 2026 calendar prices expecting them to help.

Proxies: 164 tests on CPI lodging (three variants), BEA hotel prices, euro-area HICP accommodation and Spain's hotel price index (both newly pulled, manifest in `data/raw/external_prices/`), Marriott and Hilton RevPAR, and coded management wording. Nothing beats naive against the residual (best ratio 1.03). This confirms the decomposition note's null from 7 September with 2026 data added.

## 4. What this means for the pitch

1. **Use card v2's mix terms and keep the residual explicit.** The pitch can say party size adds about 0.8 points, geography subtracts about 1.4, length of stay is flat, FX is -1 to 0, and the remaining 4 to 5 points of ex-FX growth is like-for-like pricing that management attributes to "price appreciation." Showing that decomposition with the unobserved line labelled is more credible than a false point estimate.
2. **The ADR risk is one-sided.** If the pricing residual mean-reverts to its 2023-25 level (2.4 points) instead of persisting (4.6), reported ADR is about +0.8% rather than +3.0%, roughly $2.2 billion of annualised GBV. Hotel ADR growth collapsing to +0.6% by mid-August and lodging CPI falling from +4.9 to +3.1 both point that way; nothing measured points the other way. Carry the mean-reversion case as the downside scenario, not as a tail.
3. **Nights and ADR now come from the same data with the same corrections**, which is the story a judge will credit: survivorship-matched reviews give both the stays growth and the party-size and regional inputs to ADR.
4. **Name the FX estimator.** The 1.4-point spread between the euro fit and the basket build is now the largest controllable uncertainty on the ADR line, larger than everything the mix terms moved.

## 5. Next steps

- **September dumps (mid-to-late September):** re-run I1 and I1b for party size and E for the regional split; card v2 re-runs with one command (`J3_residual_nowcast_card_v2.py`) and picks up the new `I_mix_terms_3q26.csv`.
- **5 November:** score ex-FX ADR against +3.5 and the residual against 4.6; add 3Q26 to the walk-forward. If the print lands at the mean-reversion case, the persistence rule is retired.
- **Do not** build a scraped price panel or request calendar prices; both routes are closed by this run. The reservation-level data request in the RNPL handoff remains the only path to a measured price.
- Fix the BRIEF's claim that 2024-25 calendars carry prices: only through May 2025.

