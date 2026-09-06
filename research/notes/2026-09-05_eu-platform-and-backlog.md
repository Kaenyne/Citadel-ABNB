# Building on Theo's acquisition layer: the European platform category (Eurostat) and the bookings backlog (XBRL)

**What this is:** two builds on top of Theo's PR #10 (alt-data acquisition, manifests, handoff doc). His handoff names both: T6.5 (deseasonalise and benchmark against the Eurostat platform series, then "state the edge or state that there isn't one") and the deferred-revenue trap (unearned fees stopped tracking bookings when Reserve Now Pay Later launched). Theo's bulk files sit on his external drive, so both series were re-pulled from the public APIs and cached under `data/raw/` (gitignored); everything here reproduces from `analysis/src/abnb_eu_platform_and_backlog.py`.
**Compiled:** 2026-09-05. Author: Krishang, with Claude Code. Outputs: `data/processed/eurostat_platform_nights_monthly.csv`, `eurostat_platform_nights_quarterly.csv`, `eurostat_platform_nights_by_country.csv`, `abnb_backlog_indicators.csv`; figures `analysis/figures/eurostat_platform_vs_abnb_emea.png`, `eurostat_platform_country_growth.png`, `abnb_backlog_indicators.png`.
**Sources:** Eurostat `tour_ce_omr` (experimental statistics: nights at short-stay accommodation booked through Airbnb, Booking, Expedia and TripAdvisor, supplied by the platforms; monthly Jan 2018 to Mar 2026, EU27 and 31 countries; attribute Eurostat). SEC XBRL company facts for Airbnb (`ContractWithCustomerLiabilityCurrent`, `FundsHeldForClients`). Airbnb geographic revenue from the 10-Q R-pages (Jessie's `citadel-abnb-files 2/data/processed/airbnb_regional_revenue_quarterly.csv`). Theo's handoff for the Q3 2026 consensus ($4,744M) and FY2026 consensus ($14,162M).

---

## 1. Bottom line

1. **The European platform category is growing about 10%, and Airbnb's EMEA business grows with it, not faster.** EU27 platform nights: 512M in 2019, 719M in 2023, 854M in 2024 (+18.8%), 952M in 2025 (+11.4%), and +9.7% in Q1 2026. Over 4Q23 to 2Q25 Airbnb's reported EMEA revenue growth ran 2.4 points *below* the category on average; over 3Q25 to 1Q26 it ran 8.6 points above, which is the euro's rise against the dollar (1Q26: EMEA revenue +25% in USD against category nights +10%). In constant currency and in nights, Airbnb is a category-rate grower in Europe. The correlation of category nights growth with Airbnb EMEA revenue growth is 0.81 excluding the FX-distorted 1Q26 (n = 9), so the series is a usable check on the EMEA line once Eurostat publishes, with a lag of about five months.
2. **Regulated markets show up as the slow ones.** 2025 growth: Netherlands +5.8%, Austria +7.1%, Belgium +9.4%, Italy +9.5%, Portugal +10.3%, France +10.5%, Spain +11.1%, against Greece +14.9%, Poland +13.8%, Czechia +13.8%, Germany +13.0%. Q1 2026: Spain +6.5%, Portugal +4.9%, Austria +4.0% against Italy +14.7%, Germany +14.9%, Croatia +15.6%. Spain (20% of EU nights) and Portugal are the two that decelerated most into 2026, consistent with the 2025 delistings. Foreign guests are 61% of EU platform nights and grew in line with domestic in 2025.
3. **Unearned fees were the best single leading indicator Airbnb had, and RNPL broke it.** Quarter-end unearned fees y/y explained next-quarter revenue growth with R² 0.96 over 4Q21 to 2Q25 (slope 0.64, t = 18, n = 14). From 3Q25 the fit fails by 2.6, 9.7 and 13.2 points as RNPL defers guest payment toward check-in; unearned fees are now -0.9% y/y against revenue +16.5%. Theo's trap, confirmed with numbers: do not read the deferred-revenue line as demand.
4. **Funds held for clients still tracked revenue through the RNPL ramp and now points below the Q3 guide.** Funds held y/y explained next-quarter revenue growth with R² 0.78 (slope 0.87, n = 17, fit through 1Q26) and fitted 4Q25 and 1Q26 revenue to within 0.5 and 1.1 points. At 2Q26 funds held grew 10.5%, which fits 3Q26 revenue growth of 11.5%, or $4.56B, against guidance of $4.69B to $4.77B (+14.5% to +16.5%) and consensus $4,744M. The gap between funds-held growth (+10.5%) and GBV growth (+15.7%) widened from 3.8 points a year earlier to 5.2, which is the scale of the RNPL effect on this line too; if RNPL explains all of the shortfall the guide holds. This is the first free indicator that sits below the guide, and it is the one to test on 5 November: the honest statement is "below guide, with an RNPL confound the size of the gap", not "miss".

## 2. Eurostat platform nights: the series

| | 2019 | 2023 | 2024 | 2025 | Q1 2026 y/y |
|---|---|---|---|---|---|
| EU27 nights (M) | 512 | 719 | 854 | 952 | |
| Growth | | | +18.8% | +11.4% | +9.7% |
| Foreign-guest share | | | | 61% | |

Monthly y/y is noisy around Easter (Mar 2025 -7%, Apr 2025 +34%); use quarters. Quarterly EU27 y/y and Airbnb next to it:

| Quarter | EU27 platform nights y/y | Airbnb EMEA revenue y/y (USD) | Airbnb global nights y/y | EMEA minus category, pts |
|---|---|---|---|---|
| 4Q23 | 22.7% | 22.8% | 12.0% | 0.2 |
| 1Q24 | 28.3% | 23.8% | 9.5% | -4.5 |
| 2Q24 | 16.2% | 11.4% | 8.7% | -4.8 |
| 3Q24 | 18.0% | 12.6% | 8.5% | -5.4 |
| 4Q24 | 17.4% | 16.3% | 12.3% | -1.1 |
| 1Q25 | 6.3% | 5.3% | 7.9% | -1.0 |
| 2Q25 | 17.6% | 17.7% | 7.4% | 0.0 |
| 3Q25 | 9.8% | 14.1% | 8.8% | 4.3 |
| 4Q25 | 10.9% | 17.1% | 9.8% | 6.2 |
| 1Q26 | 9.7% | 25.1% | 9.2% | 15.4 |

The category is nights; Airbnb's line is USD revenue (nights x ADR x take rate x FX), so the gap carries ADR and FX. 2024's negative gap is Airbnb losing ground in nights or pricing below the category; 2025 to 2026's positive gap is the euro. A cleaner test needs Airbnb's EMEA nights, which management gives only qualitatively ("high single digits" in 2Q26).

Country detail (14 largest markets) in `eurostat_platform_nights_by_country.csv` and the figure. Also available in the raw pull but not yet used: stays and length of stay (`indic_to`), NUTS 2 and city level (`tour_ce_omn12`, `tour_ce_oan3`), entire versus shared accommodation (`tour_ce_oam`, annual).

## 3. Backlog indicators

| Quarter | Unearned fees $M, y/y | Funds held $M, y/y | Revenue y/y | Next-quarter revenue y/y | Fit from unearned (pre-RNPL model) | Fit from funds held |
|---|---|---|---|---|---|---|
| 1Q24 | 2,434, +12.1% | 8,737, +12.6% | +17.8% | +10.6% | 10.9% | 13.3% |
| 2Q24 | 2,621, +11.7% | 10,342, +13.1% | +10.6% | +9.9% | 10.6% | 13.8% |
| 3Q24 | 1,657, +13.0% | 6,573, +9.8% | +9.9% | +11.8% | 11.4% | 10.9% |
| 4Q24 | 1,616, +13.2% | 5,931, +1.1% | +11.8% | +6.1% | 11.6% | 3.3% |
| 1Q25 | 2,723, +11.9% | 9,175, +5.0% | +6.1% | +12.7% | 10.7% | 6.7% |
| 2Q25 | 2,857, +9.0% | 11,067, +7.0% | +12.7% | +9.7% | 8.9% | 8.5% |
| 3Q25 | 1,820, +9.8% | 7,209, +9.7% | +9.7% | +12.0% | 9.4% | 10.8% |
| 4Q25 | 1,743, +7.9% | 6,959, +17.3% | +12.0% | +17.9% | 8.1% | 17.4% |
| 1Q26 | 2,733, +0.4% | 10,550, +15.0% | +17.9% | +16.5% | 3.3% | 15.4% |
| 2Q26 | 2,831, -0.9% | 12,224, +10.5% | +16.5% | guide +14.5% to +16.5% | 2.5% | **11.5%** |

Unearned fees are guest service fees collected at booking and recognised at check-in (about 0.7x the next quarter's revenue). Funds held for clients are guest payments held for hosts until check-in; they scale with booked GBV that has been paid for, which is why RNPL (payment deferred to a scheduled date near the stay) depresses both. Funds held was less affected through 1Q26 because RNPL sits mostly in bookings inside the payment window by quarter end; the 2Q26 reading is the first where the confound is large enough to matter.

## 4. What to do with this

- **Prediction card for 5 November:** log the funds-held read (Q3 revenue $4.56B, +11.5%) next to the guide midpoint ($4.73B), consensus ($4.744B) and the cushion-based estimate ($4.82B, margin note 5.1). Whichever lands closest tells us whether funds held survives RNPL as an indicator. Ask on the call, or in IR follow-up, for RNPL's share of GBV in the quarter; that is the variable that reconciles the two.
- **EMEA check each quarter:** when Eurostat publishes a quarter (about five months after quarter end), compare category nights growth with Airbnb's EMEA revenue growth ex-FX. A widening negative gap is share loss to Booking; the deck's Europe slide should carry the country chart.
- **Regulatory slide:** Spain and Portugal decelerating below the EU rate in Q1 2026 is the first official-statistics evidence that the 2025 delistings bit; pair with Inside Airbnb's Barcelona listing count (-16% to -21% y/y).
- **Next from Theo's layer:** the Austin daily active-STR count (527 dates) and NOLA licence series against Inside Airbnb's Austin and New Orleans listing counts; the booking-curve cross-section against the supply panel's city metrics. Both are one-day builds once his municipal files are on the shared Drive.

## 5. Caveats

- Eurostat's series is experimental, covers four platforms (not Airbnb alone), counts nights spent at the property (not bookings), and excludes the UK, so it is EU27 against Airbnb's EMEA.
- Ten overlapping quarters for the Airbnb comparison; the 0.81 correlation is on nine after dropping 1Q26.
- The backlog fits are single-regressor OLS on 14 and 17 quarters through a period of decelerating growth; they describe the relationship, they do not identify it.
- Funds held includes host payables and moves with payment timing; the 2Q26 reading is confounded by RNPL to an unknown degree, which is why the note says "below guide with a confound" rather than "miss".
