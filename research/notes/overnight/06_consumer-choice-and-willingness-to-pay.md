# 06. How travellers choose hotels vs Airbnb, what they will pay, and what it means for ADR, take rate and nights

Workstream 06 of the overnight run, 6-7 Sep 2026. Written for the pitch team; extends
`research/notes/2026-09-05_margin-drivers.md` section 3.4 (ADR vs US lodging prices) and
`analysis/src/hotel_price_monitor.py`, and uses the Inside Airbnb panels documented in
`research/notes/2026-09-05_inside-airbnb-supply-panel.md`.

---

## 0. Bottom line

1. **The price gap that carried Airbnb's ADR through 2025 has closed.** From 2Q25 to 1Q26 Airbnb's
   reported ADR ran +3% to +9% while US hotel prices fell 2% to 3%. In 2026 hotels reversed: CPI
   lodging went from -1.9% (Jan) to +5.0% (May), and CoStar's US hotel ADR was $171.74 in July 2026,
   +5.7% y/y with RevPAR +8.2%, the sixth straight month of gains. Airbnb's ex-FX ADR was +4% in both
   1H26 quarters. Hotels are now pricing *ahead* of Airbnb ex-FX for the first time since 4Q24.
2. **Airbnb's ADR growth is roughly half mix, and management has finally said so.** 2Q26 is the first
   quarter Airbnb published a bedroom-count metric: Bedroom Nights Booked grew **+12%** against Nights
   and Seats Booked **+10%**, and LTM bedroom nights passed **1 billion** for the first time. Divided
   by 560m LTM nights that implies at least **1.79 bedrooms per booked night**, so ADR per bedroom-night
   is at most about **$103** against a US hotel ADR of $172. Airbnb is not out-pricing hotels; it is
   selling a bigger unit.
3. **Per room, Airbnb and hotels are close. Per person, Airbnb wins by roughly half.** Across seven
   large US cities in 2Q-3Q26, the median all-in Airbnb entire-home quote is **$261/night**, **$144 per
   bedroom-night** and **$59 per guest-capacity-night** (`06_price_per_unit_panel.csv`). A hotel room at
   $172 holding 1.4-1.8 people is $95-$123 per person. The Third Bridge India expert says the same
   thing independently: unbranded villas price at hotel parity *per room*, and a villa is three rooms.
4. **The take-rate question has a real 2026-27 answer, and it is smaller and more ambiguous than the
   bulls think.** By 2Q26 about half of active listings were on the single 15.5% host fee, with the rest
   to migrate by year-end. On Airbnb's own published rates the change is worth roughly **+50bps of take
   rate if the blended guest fee it replaces was 14.1%, but -15bps at 15% and -124bps at 16.5%**. That
   the company guides to "modest upside" implies the low end. It is worth low tens of basis points on a
   13.2% take rate, not a step change, and it is being fully absorbed in 2026 by RNPL booking-timing and
   new-business incentives.
5. **Airbnb's own quote data now shows fee display has collapsed into one number, and near-term
   discounting is climbing hard.** Across 1.7m fee-inclusive quotes from 13 cities, a separate cleaning
   fee line appears in **0.02%** of quotes and a service-fee line in **0%** — the 2025 total-price default
   is real, not cosmetic. Over the same window the share of available quotes carrying a discount rose
   from **10.9% (Mar 2026) to 31.4% (Aug 2026)**, higher in **all 13 cities**. This is the single most
   actionable new datapoint in this note, and its biggest caveat is that no year-ago comparison exists.
6. **For 2027**: assume ADR growth of +2 to +3% ex-FX, of which about half is bedroom/size mix, not price;
   take rate flat to +20bps; and nights growth that is far more sensitive to Airbnb's own supply and
   product than to the hotel price gap.

---

## 1. Price gap and trend

### 1.1 Airbnb ADR against US hotel prices, quarterly

`data/processed/overnight/06_price_gap_series.csv` (script `analysis/src/overnight/06_price_gap.py`).
ADR and ex-FX ADR are as stated in the shareholder letters; CPI lodging is FRED `CUSR0000SEHB`
refreshed 6-Sep-2026; BEA is the PCE hotels-and-motels price index; HLT and MAR RevPAR are from
`data/processed/predictive/02_peer_prints.csv`. CPI and BEA quarterly figures are averages of the
months available (Oct 2025 CPI is missing at source, the shutdown gap), so they differ slightly from
the margin note's section 3.4, which handled that month differently.

| | 1Q25 | 2Q25 | 3Q25 | 4Q25 | 1Q26 | 2Q26 |
|---|---|---|---|---|---|---|
| ABNB ADR ($) | 171.34 | 174.48 | 171.29 | 167.51 | 186.82 | 183.73 |
| ABNB ADR y/y reported | -1% | +3% | +5% | +6% | +9% | +5% |
| ABNB ADR y/y **ex-FX** (letter) | +1% | +2% | +3% | +3% | **+4%** | **+4%** |
| CPI lodging away from home y/y | +0.5 | -1.6 | -1.9 | -1.6 | -0.2 | **+4.7** |
| BEA hotels and motels price y/y | -0.1 | -2.6 | -3.1 | -2.8 | -2.2 | **+5.0** |
| HLT system RevPAR y/y | +2.5 | -0.5 | -1.1 | +0.5 | +3.6 | +3.9 |
| MAR system RevPAR y/y | +4.1 | +1.5 | +0.5 | +1.9 | +4.2 | +3.4 |
| ABNB nights y/y | +7.9 | +7.4 | +8.8 | +9.8 | +9.2 | +10.3 |

The FX wedge (reported minus ex-FX) was +5pp in 1Q26 and +1pp in 2Q26. Roughly half of GBV is non-USD.
**Reported ADR growth in 2026 is mostly a dollar story; the underlying rate is +4%.**

### 1.2 The 2026 turn in hotel pricing, monthly

`06_price_gap_monthly.csv`. Verified 6-Sep-2026.

| Month 2026 | CPI lodging y/y | BEA hotels y/y | STR US hotel ADR | STR ADR y/y | STR RevPAR y/y |
|---|---|---|---|---|---|
| Jan | -1.9 | -4.3 | | | |
| Feb | -1.1 | -3.4 | | | |
| Mar | +2.5 | +1.2 | $168.06 | +3.8 | +5.9 |
| Apr | +4.4 | +4.3 | | | |
| May | +5.0 | +4.9 | | | |
| Jun | +4.7 | +5.7 | | | |
| **Jul** | **+2.8** | **+3.6** | **$171.74** | **+5.7** | **+8.2** |
| Aug | not yet published (BLS CPI due ~10 Sep 2026) | | | | |

Full-year US hotel levels (CoStar): 2022 ADR $148.83 / RevPAR $93.27 / occ 62.7%; 2023 $155.62 / $97.97
/ 63.0%; **2025 $160.54 (+0.9%) / $100.02 (-0.3%) / 62.3%** — 2025 was the first annual occupancy and
RevPAR decline since 2020. CoStar and Tourism Economics raised the 2026 forecast on 7-Aug-2026 to
**RevPAR +4.4%, ADR +3.1%, occupancy 63.1%**, and see **2027 RevPAR +2.1%, ADR +1.6%**.

The 2026 hotel recovery is barbelled and does not compete for Airbnb's guest evenly: in July 2026,
**luxury RevPAR +17.7% and ADR +14.5% against economy RevPAR +3.6%** (Barclays brand tracker via Asian
Hospitality). Group +14%, transient +11%. The academic literature says Airbnb substitutes for the
*low* end (Zervas et al. 2017; Li and Srinivasan 2019), so the segment where Airbnb actually competes
is the one where hotels have the least pricing power.

### 1.3 Airbnb's own like-for-like comparison

Airbnb published a direct comparison twice, on a stated methodology: "average global price (USD) of a
hotel room compared to a stay in a 1-bedroom home on Airbnb. Prices include all fees but exclude taxes.
Sources: CoStar, Airbnb."

| | ABNB 1-bedroom | y/y | Hotel ADR | y/y | ABNB discount |
|---|---|---|---|---|---|
| Sep 2023 (3Q23 letter fn.4) | $120 | +1% | $153 | +10% | -22% |
| Dec 2023 (4Q23 letter fn.3) | $114 | -2% | $149 | +7% | -23% |
| Mar 2024 (Skift, 22-May-2024) | $114 | -2% | $140.16 | +1.6% | -19% |

**Airbnb stopped publishing this comparison after the 4Q23 letter.** That is exactly when the hotel gap
started narrowing in Airbnb's favour on the level but against it on the trend. Treat the disappearance
as a disclosure signal, not evidence, but flag it to the team.

### 1.4 Per-unit normalisation: the honest comparison

Airbnb ADR is per *listing*-night; hotel ADR is per *room*-night. Three normalisations, all in
`06_price_per_unit_panel.csv` and `06_price_gap_series.csv`:

| Basis | Airbnb | Comparator | Gap |
|---|---|---|---|
| Per listing-night, global | ADR $183.73 (2Q26) | US hotel ADR $171.74 (Jul 26) | Airbnb +7% (not comparable: different geography) |
| **Per bedroom-night, global** | **≤ $102.87** (ADR / ≥1.786 bedrooms per night, from >1bn LTM bedroom nights over 560m LTM nights, 2Q26 letter) | US hotel ADR $171.74 | **Airbnb ~40% cheaper** |
| Per bedroom-night, 7 large US cities, all-in quote basis | $144 median (2Q-3Q26) | US hotel ADR $171.74 | Airbnb ~16% cheaper, and these are high-ADR urban markets |
| Per guest-capacity-night, same 7 cities | $59 median | $95-$123 (hotel room / 1.4-1.8 guests) | **Airbnb roughly half** |

Caveats: guest *capacity* is not realised party size; Airbnb does not disclose party size and no
authoritative STR/AHLA guests-per-occupied-room benchmark could be found (the 1.35-1.8 range is an
industry rule of thumb, not a published statistic). The seven cities are Austin, Chicago, Los Angeles,
Nashville, New Orleans, New York and San Diego — all USD, all urban, all with hotel ADRs well above the
US average (NYC hotel ADR was $351.18 in July 2026).

Per-city detail, entire homes, 2Q-3Q26, all-in quote basis, **local currency**:

| City | Median all-in | Per bedroom | Per capacity | Median 1BR | Mean bedrooms |
|---|---|---|---|---|---|
| Nashville | $287 | $130 | $45 | $197 | 2.7 |
| San Diego | $358 | $192 | $75 | $206 | 2.2 |
| Los Angeles | $273 | $153 | $66 | $174 | 2.1 |
| New York | $219 | $154 | $71 | $193 | 1.7 |
| Austin | $235 | $126 | $50 | $164 | 2.4 |
| Chicago | $255 | $137 | $57 | $187 | 2.2 |
| New Orleans | $195 | $102 | $46 | $139 | 2.3 |
| London (GBP) | 227 | 145 | 61 | 172 | 1.8 |
| Paris (EUR) | 199 | 158 | 66 | 164 | 1.5 |
| Rome (EUR) | 176 | 127 | 46 | 150 | 1.6 |
| Sydney (AUD) | 348 | 209 | 93 | 261 | 2.1 |
| Barcelona (EUR) | 220 | 108 | 54 | 152 | 2.2 |

Note the structural difference: Nashville and Austin sell 2.4-2.7 bedroom homes at $126-130 per
bedroom; Paris and New York sell 1.5-1.7 bedroom apartments at $154-158 per bedroom. **Airbnb's price
advantage is a function of unit size, and unit size is a function of market.** The markets where
Airbnb is a genuine hotel substitute (dense European and US cities, small units) are the markets where
it has the least price advantage per room.

### 1.5 Adjacent market data

The whole US short-term-rental market (AirDNA, not Airbnb-only, and skewed to large whole homes):
July 2026 ADR $317.55 (+6.9%), RevPAR $217.17 (+7.2%), occupancy 68.4%, **demand nights +2.0% against
supply +2.6%**. Europe July 2026 ADR EUR 159.2 (+8.2%), RevPAR EUR 110.1 (+7.7%), demand +0.8%,
listings +1.9%. Airbnb's own nights growth of +10% is running five times the AirDNA US category demand
growth: **Airbnb is taking share inside the STR category, not riding it.**

---

## 2. Fees and total-price display

Full dated chronology in `06_fee_timeline.csv`. The load-bearing facts:

**Split fee → single fee.** Airbnb's historic model charged the host 3% and the guest a separate
14.1-16.5% service fee. From Q4 2025 it began migrating property-management-software (API) hosts to a
**single 15.5% host fee**, telling hosts they can raise prices to keep the same net earnings and telling
guests they will still see the full price upfront. Over a quarter of active listings by 1Q26,
**about half by 2Q26**, with "most of the remaining hosts" announced in July 2026 for completion in 2026.

**What that does to take rate — the arithmetic, done properly.** Let the host's nightly subtotal be
$100 and assume the host reprices to hold net earnings constant.

| Guest service fee replaced | Split-model take rate | Single-fee take rate | Delta | Guest all-in price change | ABNB revenue change |
|---|---|---|---|---|---|
| 14.1% | 14.99% | 15.50% | **+51bps** | +0.6% | +4.1% |
| 15.0% | 15.65% | 15.50% | -15bps | -0.2% | -1.2% |
| 16.5% | 16.74% | 15.50% | -124bps | -1.5% | -8.8% |

The sign depends entirely on what the blended guest fee actually was. Management guides to "modest
upside to our take rate from both the migration to the single fee structure as well as our insurance
programs" (Mertz, 1Q26 call), which implies the low end of the guest-fee range for the migrating
cohort. On a 13.2% reported take rate, a 51bp move on the fee base is worth roughly **+40 to +45bps of
reported take rate fully migrated** — real, but one-off, and not the 200-300bps some bulls imply.
There is also a genuine competitive benefit: a single fee lets a host post the same price on Airbnb as
on Booking.com, which uses a host-only model. The India expert says removing the standalone-host
discount takes away the reason those hosts stayed off channel managers, which helps professional
aggregators. Independent commentary (CNBC, 22-Aug-2026) reports host pushback.

**Total-price display.** Optional toggle from December 2022 (4Q22 letter; search ranking began
weighting total price). Global **default** from 21 April 2025, by which point ~17m guests had used the
optional toggle and over 80% of hosts had used at least one pricing tool. The regulatory backdrop
forced the issue anyway: California SB 478 (1 Jul 2024) and the FTC Rule on Unfair or Deceptive Fees
(final Dec 2024, effective 12 May 2025) both cover short-term lodging.

**Direct evidence that display changed.** `06_quote_line_items.csv` and `06_quote_discount_panel.csv`
parse the raw quote JSON that Inside Airbnb captures from Airbnb's public pricing endpoint (available
from March 2026). Across **1.71m available quotes in 13 cities, March to August 2026**:

- a separate **`cleaning_fee` line item appears in 0.02% of quotes** and a **`service_fee` line in 0%**;
- the only line types that appear at scale are `nightly_subtotal`, `discounted_subtotal`,
  `discount_amount`, `taxes` and `other`;
- taxes appear as a separate line in 0.1-0.3% of quotes until July 2026, when they jump to 8-9%.

The all-in price is now genuinely one number. There is no longer a visible fee wedge for a guest to be
surprised by at checkout — which makes third-party claims of a "55.9% median checkout markup"
(AirROI 2026) hard to reconcile with what Airbnb's own endpoint returns; treat that study as
unverified.

**Cleaning-fee crackdown.** 45% of listings had no cleaning fee in May 2021; ~40% and 300,000+ listings
having cut or removed the fee by early 2024. **No newer figure has been published** — Airbnb stopped
updating the statistic once total-price display made the fee invisible in search. A "bring your own
cleaner" lower-fee offer was reported in August 2026 but AirDNA confirmed to Skift it is a pilot.

**The 2022-23 backlash left no measurable brand damage.** Morning Consult (Feb 2023, n=5,000): Airbnb
favourability **42%**, up from 38% in Jan 2022 and 23% in 2018; booking intent among short-term
travellers 51% vs 50%. The "Airbnbust" was a host-side and social-media event, not a demand event.

**Conversion evidence in company disclosure is thin and never quantified as a conversion rate.** The
best the company has given: RNPL + redesigned cancellation policies + single-fee migration together
delivered **about 3 points of nights growth and about 4 points of GBV growth in Q1 2026** (Mertz, 1Q26
call) — i.e. those three features contributed roughly 1 point of ADR as well. No counterfactual is
offered, and the three are not separated.

---

## 3. Choice drivers

Evidence is in `06_choice_drivers.csv`. This section is deliberately blunt about how weak the survey
base is.

### 3.1 What we can stand behind

| Finding | Source | Confidence |
|---|---|---|
| Nearly two-thirds of surveyed Airbnb users had used it as a substitute for a hotel; Airbnb expected to outperform budget hotels, underperform upscale | Guttentag and Smith (2017), IJHM, n>800 | Medium — 2017, self-reported |
| A 10% rise in Airbnb listings is associated with ~0.5% lower quarterly hotel revenue, concentrated in lower-priced, non-business hotels | Zervas, Proserpio and Byers (2017), JMR, Texas DiD | High for its period, dated for 2026 |
| Consumer surplus ~$41 per transaction; the gain is concentrated where hotels are capacity-constrained, because peer supply expands elastically into demand spikes | Farronato and Fradkin (2022), AER 112(6) | High for its period |
| Airbnb mildly cannibalises hotel sales, concentrated in low-end hotels | Li and Srinivasan (2019), Marketing Science | Medium (magnitude not retrievable) |
| 29% of US paid-lodging summer travellers plan a private-rental stay vs 81% planning at least one hotel stay; overlapping, and 45% planning a paid-lodging trip at all is a six-year low | Deloitte 2026 summer survey, n=4,003, fielded 2-9 Apr 2026 | Medium-high |
| The travelling public is skewing rich: $100k+ households are 55% of it in 2026, from 50% in 2025 and 35% in 2023 | Deloitte 2024 and 2026 surveys | Medium-high |
| Group travel is structurally taking share: UK short-term-rental bookings by property capacity moved from 1-2 guests 43% / 6+ guests 21% in June 2019 to 1-2 guests 29% / 6+ guests 30% in June 2026 | Lighthouse via VisitBritain, June 2026 | Medium-high — independent corroboration of Airbnb's bedroom-nights claim |
| Booking windows are shortening: US bookings made 0-7 days out went from 21% to 27% of all bookings between 2022 and 2025 | PriceLabs via RentalScaleUp, Dec 2025 | Medium |
| Airbnb takes 54% of US vacation-rental-manager reservations and 45% of their revenue; direct is 21% of reservations | Key Data, Q4 2025 | Medium |

### 3.2 The loyalty gap, quantified from the other side

Airbnb has no loyalty programme. The best available quantification of what that costs comes from the
Third Bridge Booking.com call (30-Jul-2026): Booking's direct traffic is high-50s to mid-60s percent,
and **Genius level 2 and 3 members drive high-50s to low-60s percent of Booking's room nights, up about
5 points year over year.** Chesky said in 1Q26 that flights and loyalty are "both on the table"; the
Delta partnership (announced May 2026) is a revenue share, not a loyalty programme, and management said
it is not a take-rate negative. **No sourced statistic on the share of hotel bookings driven by loyalty
points could be found**, so the loyalty gap remains a qualitative argument.

### 3.3 Airbnb's own model of substitution

Chesky, 2Q26 call, is the clearest statement any executive has made on this: there are people who only
stay in homes, people who only stay in hotels, and **most people are willing to stay in both**. He
adds two funnel numbers: about **35% of people who book a hotel on Airbnb for the first time come back
and book a home** (2Q26 call) and **~55% of guests who book a hotel on Airbnb return to book a home**
(1Q26 letter). Rabbu's read of the 2Q26 print is that hotel nights on Airbnb grew roughly three times
faster than home nights. The hotel category on Airbnb is a customer-acquisition channel that happens to
carry a competitive take rate, not a hotel business.

### 3.4 What we could not source

- **Business travel.** No Airbnb-disclosed business-travel share of nights for 2023-2026 exists. The
  only dated figures are ~8% of bookings from corporate travel in 2014 and a 2018 note that nearly 60%
  of Airbnb for Work trips had more than one guest. **Do not put a business-mix number in the model.**
- Age-cohort preference splits from AAA, Bankrate, MMGY, Phocuswright or Statista — all blocked, 404 or
  paywalled. YouGov's 2026 US hotel rankings **explicitly exclude Airbnb and Vrbo**, which is itself
  telling about category framing but yields no comparison.
- A dedicated study on which pandemic-era behaviours persisted. The one hard series we hold is Airbnb's
  own: long-term stays (28+ days) were 20-22% of gross nights in 2021-22, fell to 17% by 1Q24, and
  **the company stopped disclosing the figure after 1Q24**. High-density urban share recovered from a
  2021 trough to 48-51% by 2022-23 and is no longer disclosed either. Both series ended as disclosures,
  not as trends.

---

## 4. Willingness-to-pay evidence

`data/processed/overnight/06_wtp_evidence.csv` and `06_wtp_hedonic_coefs.csv`, from
`analysis/src/overnight/06_wtp_hedonics.py`. 2.85m listing-dumps across 123 city-dumps, 13 cities,
Dec 2022 to Aug 2026, split by price basis. Specification: log(price), demeaned within city-dump (so
currency and market level drop out), on room type, log(capacity), bedrooms, Superhost, Instant Book,
rating bands, licence disclosed, host-portfolio size and whether the listing was reviewed in the last
twelve months. HC1 standard errors. R² 0.39 (2024-25 listed basis, n=951k) and 0.46 (2026 all-in quote
basis, n=1.38m).

| Attribute | Premium, 2026 all-in quote basis | 95% CI | Premium, 2024-25 listed basis |
|---|---|---|---|
| Entire home vs private room (hedonic) | -30.0% for private room | [-30.2, -29.8] | -23.0% |
| Entire home vs private room (raw median) | +119.7% | | +74.0% |
| Guest capacity, per 1% more | **+0.49%** | [+0.487, +0.495] | +0.39% |
| Each extra bedroom, capacity held fixed | **+15.1%** | [+14.9, +15.2] | +19.5% |
| Rating ≥4.9 vs 4.7-4.8 (Guest Favorite proxy) | **+9.5%** | [+9.2, +9.8] | +13.5% |
| Superhost badge | **+1.0%** | [+0.8, +1.2] | -1.2% |
| Instant Book | 0.0% (not identified) | | +8.9% |
| Professional host (>20 listings) vs single-listing | +8.1% | [+7.8, +8.4] | +9.5% |
| Licence disclosed | -23.5% | [-24.0, -23.1] | -10.4% |
| Minimum stay 7+ vs 1-2 nights (raw median) | -37.8% | | -19.7% |

**Read these carefully.**

- **The Superhost premium is a myth of the raw data.** Superhosts command +11.0% on an unadjusted
  median but +1.0% once size, room type, rating and host scale are controlled. The academic WTP
  literature (Gibbs et al. 2018; Chen and Xie 2017; Lorde et al. 2019) all report a positive Superhost
  premium; none of the retrievable abstracts controls for the same covariates. **Superhost status is a
  proxy for a nicer, bigger listing, not a thing guests pay for.**
- **Quality does carry a premium, and it is the rating that carries it, not the badge.** A ≥4.9 rating
  is worth +9.5% on the all-in price. Since Guest Favorites is essentially a rating-and-review screen,
  this is the best available read on what the Guest Favorites programme monetises.
- **Size dominates everything.** A 1% larger capacity is worth +0.49%, and an extra bedroom holding
  capacity fixed is worth +15%. Nothing else in the specification comes close. This is the hedonic
  version of the bedroom-nights disclosure.
- **Instant Book washes out on the 2026 basis.** It was worth +8.9% on asking prices in 2024-25 and is
  unidentified in the fee-inclusive quotes. Do not carry a flexibility premium into the model.
- **Licence-disclosed listings are cheaper**, sharply so in 2026 (-23.5%). This is almost certainly a
  regulatory-regime composition effect (Barcelona, New York, Paris) rather than a discount for
  compliance. Cross-reference workstream on regulation.
- Cross-era comparisons of *levels* are invalid: the 2026 basis includes fees, the older basis does not.
  Comparisons of *ratios* across eras are defensible but not clean.

### 4.1 Host willingness to accept: the discounting series

`06_quote_discount_panel.csv`. Airbnb's public quote endpoint returns the discount applied to a real
short stay (median 2 nights, median 3-6 days out). This is not a weekly or monthly discount — those do
not apply to a 2-night stay — so it captures last-minute and promotional discounting on unsold nights.

| Month 2026 | Cities | Quotes | Share of quotes discounted | Median discount, % of subtotal |
|---|---|---|---|---|
| Mar | 10 | 238,377 | 10.9% | 16.0% |
| Apr | 13 | 254,099 | 10.0% | 15.3% |
| May | 13 | 278,130 | 12.5% | 15.5% |
| Jun | 13 | 316,264 | 18.6% | 15.7% |
| Jul | 13 | 311,786 | 19.8% | 15.0% |
| **Aug** | 13 | 308,734 | **31.4%** | 9.6% |

The rise is present in **every one of the 13 cities**: Austin 9.5% → 33.1%, Nashville 6.2% → 39.6%,
Paris 6.7% → 24.6%, New Orleans 27.5% → 51.3%, Sydney 9.0% → 27.2%. The median discount depth falls in
August because the marginal discounter offers a smaller cut.

**Caveats, and they are serious.** There is no year-ago comparison — the quote block only exists from
March 2026, so this cannot be read as a y/y signal. Seasonality is uncontrolled: an August scrape quotes
early-September shoulder dates, which naturally clear at a discount, while a March scrape quotes
late-March. The quote lead time varies 3-6 days across months. **What this series can support** is that
by August 2026 roughly a third of near-term available Airbnb inventory in large cities was being
discounted at the point of quote, and that this is consistent with the PriceLabs finding that
last-minute bookings rose from 21% to 27% of the total between 2022 and 2025. **What it cannot support**
is a claim that discounting rose year over year. Re-run the script monthly; by March 2027 it becomes a
true y/y series and one of the better proprietary indicators the team has.

### 4.2 The company's own view of host pricing

Chesky, 2Q26 call: Airbnb does not set listing prices; the lever is showing hosts they will earn more
by pricing better. Airbnb is building a new AI pricing model that ingests hotel prices, Airbnb prices,
local events and lead-time patterns, with one-tap acceptance. Mertz called it "dissonant" that Airbnb
has pushed affordability and pricing tips hard while nominal ADR rose, and resolved the dissonance with
bedroom nights. **If the AI pricing tool works as described, it raises host revenue through better
yield management, which supports ADR without a guest-facing price increase — and it also gives Airbnb
an unprecedented amount of influence over the marketplace's price level.**

---

## 5. What the five Third Bridge expert calls say

`06_expert_call_evidence.csv`. All paraphrased; licensed research.

| Call | Date | Expert |
|---|---|---|
| US Vacation Property Rental Management & Airbnb | 2 Jun 2026 | MD, US full-service short-term rental manager |
| UK & Europe Vacation Rental Market (Awaze & Airbnb) | 26 May 2026 | Former C-level, Awaze Vacation Rentals |
| Indian Alternative Accommodation (StayVista, Airbnb, Elivaas) | 19 Aug 2026 | Senior exec, revenue management, MakeMyTrip |
| Booking Holdings — AI & the Connected Trip | 30 Jul 2026 | Former Director, Commercial Excellence Americas, Booking.com |
| OTA AI Disruption, 12-24 month outlook | 14 Aug 2026 | Principal PM, ML & AI, Booking Holdings |

**On guest choice.** The US manager frames vacation rentals as the *value* side of leisure travel,
historically resilient in downturns: a group of six to eight splits the cost of a house and cooks in,
and the stay becomes cheap per person. He says the industry is doing extremely well in 2026 because air
and international travel have got more expensive and people still want a vacation, just a cheaper one.
This is the same mechanism as section 1.4, from the supply side.

**On pricing power.** The India expert is the most useful single data point in the pack: a villa is
about three rooms, branded operators charge a large premium (StayVista ~3x the market average, Elivaas
2-2.5x), but **unbranded villas typically price at the same level as a hotel on a per-room basis**.
Alternative accommodation runs ~40% occupancy against hotels at 60-65%, because the use case is weekend
leisure. The European expert says the category has grown at only very low single digits since 2023,
constrained by household budgets, and that discounts come straight out of the manager's margin once
the price falls below the corridor agreed with the homeowner.

**On host economics.** A US property manager takes 20-25% of rental income (owner keeps 75-80%) and
keeps 100% of housekeeping, damage-waiver and booking fees; the manager's take rate is about 30% on his
own definition, and "the platform" about 40%. Management commission rates have been broadly flat, down
slightly since 2018 when Vacasa and TurnKey competed on fees. In Europe, buy-to-let and second-home
letting is becoming less attractive on tax and owners are exiting — but there are ~18m second homes in
Europe of which only ~3m are in the rental pool, so the latent supply is enormous.

**On channel mix and take-rate room — the bear case, from people who pay the fee.**
- Of a $100 nightly rate, roughly $15 goes to Airbnb (US); 15-16% in Europe.
- The US manager says Airbnb **could not** push to 20% without consequence: it competes with
  Booking.com and Vrbo for supply and has to stay supplier-friendly, and managers would reallocate
  inventory. He says Airbnb has lost the supply exclusivity it once had, that platforms now compete for
  large suppliers with revenue-target rebates and paid placement (Vrbo most aggressively), and that in
  this market **the property managers hold the power because the OTAs need the supply**.
- The European expert says the risk of commission *cuts* is low because Airbnb and the rest have "set a
  plateau", and that managed rentals will always carry a higher take rate because of added services.
- The Booking.com expert puts Booking's net take rate at ~14.5% in 2025 (15-16% pre-pandemic) and says
  nothing pushes OTA take rates materially above the low teens. He is more optimistic than the sell-side
  (which models a 30bp fall to ~13.6%) only because AI-led search converts better.

**Read together: three of five experts independently say the OTA take rate is at a ceiling.** That is
the strongest external check on the single-fee bull case in section 2.

**On AI.** Only ~3% of accommodation bookings are likely to move to AI-native transactions over 12-24
months; the barrier is trust on a >$1,000 purchase. OTAs took ~30 years from 1996 to reach ~50% share.
Booking's structural moat is payments, currency handling and 30 years of supplier connectivity.

---

## 6. Synthesis

### 6.1 Is ADR growth price or mix? About half and half, and the mix half is the durable half

Decomposition for 2Q26 using only disclosed figures:

| Component | 2Q26 | Source |
|---|---|---|
| Reported ADR y/y | +5% | letter |
| less FX | -1pp | letter (ex-FX +4%) |
| = ex-FX ADR | +4% | letter |
| of which bedroom/size mix | ~+2pp | bedroom nights +12% vs nights +10% |
| of which price and other mix | ~+2pp | residual |

The 1Q26 wedge was larger: reported +9%, ex-FX +4%, so 5pp of FX. **Management is now explicitly
arguing that the mix half is not "price" at all** — Mertz called the bedroom-nights component "durable
and really a reflection of incremental value delivered, not just rising prices." She is right on the
economics: selling a three-bedroom house at $250 instead of a studio at $150 is a mix shift, not
inflation, and it does not consume price elasticity. It also does not repeat forever: bedroom nights
have outgrown nights by ~2pp for several years, and the mix can only shift so far.

### 6.2 Can the take rate rise?

| Lever | Size | Timing | Confidence |
|---|---|---|---|
| Single 15.5% host fee, full migration | +40 to +50bps on reported take rate **if** the replaced blended guest fee was ~14.1%; negative if it was 15%+ | 2H26 into 2027 | Medium. Direction is company-guided; magnitude is my arithmetic |
| FX service fee (mid-2024) | +20bps, already in the base | Fully in 2025 | High (company-stated) |
| Guest travel insurance and new insurance products | growing +40% (FY25), +45% (1Q26), +>60% (2Q26) off a small base, in 12 countries | continuing | Medium-high |
| Advertising / host monetisation | asked repeatedly by analysts since 2023; management has never committed | not modelled | Low |
| **Offsets**: RNPL book-vs-stay timing (>20% of GBV), customer incentives for new businesses, geographic mix into lower-ADR markets, and the Delta revenue share | enough to hold the 2026 take rate flat at ~13.2% despite the above | 2026 | High (company-stated) |

The honest answer is **yes, but by tens of basis points, and 2026 already spent it**. The 2027 question
is whether the incentives for services and hotels stop growing faster than the fee benefit. Against
that, three of five expert calls say the OTA take rate is at a ceiling and that supply-side bargaining
power sits with professional managers.

### 6.3 How does a slowdown hit Airbnb vs hotels?

Two natural experiments in the record.

**2022-23.** Hotel prices were rising fast (CPI lodging +7.1% y/y in 1Q23) while Airbnb held ADR flat
(+0.2% in 1Q23, +1.4% in 2Q23) and actively pushed affordability. Airbnb's ADR *underperformed* the
category by 5-7pp and nights kept compounding. The "Airbnbust" was a host-side event; Morning Consult
shows no brand damage. **In a hot-price environment Airbnb chose volume over price.**

**Spring 2025.** North American demand wobbled; ABNB ADR was -0.9% reported in 1Q25 (+1% ex-FX) and
hotel RevPAR turned negative at Hilton (-0.5% in 2Q25, -1.1% in 3Q25). Both suffered; hotels suffered
more on RevPAR because they cannot flex supply. 2025 was the first year since 2020 that US hotel
occupancy and RevPAR both fell, while Airbnb nights grew 7-10% every quarter.

**The mechanism, from Farronato and Fradkin.** Peer supply is elastic and expands into demand spikes,
which caps hotel pricing at peaks. The corollary for a downturn is the reverse: peer supply is slow to
leave, so **Airbnb absorbs a demand shock in price and occupancy while hotels absorb it in RevPAR**.
The US manager's 2009-10 recollection is consistent: some ADR decline, made up on occupancy.

The practical read for 2027: if the consumer weakens, expect Airbnb nights to hold up better than hotel
room-nights (it is the value option, and the Deloitte data says the travelling public is skewing rich
while the marginal traveller drops out), but expect Airbnb ADR to give back the mix gains as groups
shrink and trade down from three-bedroom houses to one-bedroom apartments. **Airbnb's ADR is more
cyclical than it looks, because ADR is size mix and size mix is discretionary.**

### 6.4 The 2027 hotel-vs-Airbnb mix-shift drivers, ranked

1. **Unit-size mix** (up: group travel share is rising in independent UK data and in Airbnb's bedroom
   nights). Positive for ADR, neutral for nights.
2. **Hotels on Airbnb** (up: hotel nights growing ~3x home nights off a tiny base; 35-55% of hotel
   bookers come back for a home). Positive for nights, mildly negative for ADR mix, neutral to positive
   for take rate.
3. **Geographic expansion into Brazil, Japan, India, Mexico** (nights growing 2x the core; India origin
   nights +60% y/y in 2Q26; first-time bookers +11%, best in four years). Positive for nights,
   **negative for ADR**, neutral for take rate.
4. **Hotel pricing normalising to +1.6% in 2027** (CoStar/Tourism Economics). Removes the relative
   price tailwind Airbnb had in 2025.
5. **Supply**: AirDNA US STR supply growth has decelerated to ~2.6% and demand to ~2.0%; occupancy is
   flat. The 2023-24 oversupply that crushed category RevPAR has cleared.
6. **Regulation** — see the regulatory workstream; it is the largest downside tail on supply and hence
   on nights.

---

## 7. For the model

Parameters this workstream supplies. Every figure carries a source; anything I could not source is
listed as such rather than guessed.

| Parameter | Value | Unit | Source |
|---|---|---|---|
| ABNB ADR growth ex-FX, FY26 | +4% | % y/y | 1Q26 and 2Q26 letters (both +4%) |
| ABNB ADR growth ex-FX, FY27 base | **+2.5%** (range +1.5% to +3.5%) | % y/y | ~2pp bedroom mix decaying toward 1.5pp, plus price at hotel-forecast rates (CoStar 2027 ADR +1.6%) |
| of which bedroom/size mix | +1.5 to +2.0pp | pp of ADR | bedroom nights +12% vs nights +10%, 2Q26 letter |
| of which price | +0.5 to +1.5pp | pp of ADR | residual; check against CPI lodging |
| Take rate, FY26 | 13.2-13.3%, flat vs 2025 | % of GBV | 2Q26 letter and call (company-guided) |
| Take rate, FY27 | **13.3% base**, 13.1% bear / 13.6% bull | % of GBV | single-fee arithmetic (+40 to +50bps gross) net of incentives; expert ceiling view caps the bull |
| Single-fee take-rate uplift, gross | +40 to +50bps if the replaced guest fee was 14.1%; sign flips negative above ~14.6% | bps | arithmetic on Airbnb's published fee rates; see 6.2 |
| Insurance revenue growth | +45% to +60% y/y off a small base, 12 countries | % y/y | 1Q26 and 2Q26 letters |
| RNPL share of GBV | >20% | % of GBV | 1Q26 and 2Q26 letters |
| Nights uplift attributable to RNPL + cancellation redesign + single fee | +3pp nights, +4pp GBV | pp of growth | Mertz, 1Q26 call. Company-stated, no counterfactual |
| Bedrooms per booked night (LTM to 2Q26) | ≥1.786 | bedrooms | >1bn LTM bedroom nights / 560m LTM nights, 2Q26 letter |
| ADR per bedroom-night (2Q26) | ≤$102.87 | USD | derived |
| Bedroom-night elasticity of price | +15.1% per extra bedroom, capacity fixed | % | `06_wtp_hedonic_coefs.csv`, n=1.38m |
| Capacity elasticity of price | +0.49% per 1% capacity | elasticity | same |
| Rating ≥4.9 premium (Guest Favorite proxy) | +9.5% | % | same |
| Superhost premium, adjusted | +1.0% | % | same — **do not model a Superhost premium** |
| Own-price elasticity of Airbnb nights | **not estimable**; literature conflicts (inelastic in NYC and Vienna, elastic in Barcelona and Madrid) | — | Gunter et al.; Casamatta et al. Do not put an elasticity in the model without saying it is assumed |
| Hotel-revenue displacement per 10% Airbnb supply | -0.5% quarterly hotel revenue, low-end hotels | % | Zervas et al. (2017) |
| Business-travel share of nights | **not disclosed since 2014** | — | do not model |

Sensitivity table with confidence: `data/processed/overnight/06_elasticities.csv` (25 rows).

---

## 8. For the 5 Nov card (3Q26 print)

Datapoints already in the public record that bear on 3Q26 ADR, and what they imply.

| Datapoint | Value | Status as of 6 Sep 2026 |
|---|---|---|
| CPI lodging away from home, Jul 2026 | **+2.8% y/y** (down from +4.7% in June) | Published |
| CPI lodging away from home, Aug 2026 | — | **Not yet published**; BLS release ~10 Sep 2026 |
| BEA hotels and motels price index, Jul 2026 | +3.6% y/y (from +5.7% in June) | Published |
| CoStar US hotel, Jul 2026 | ADR $171.74 **+5.7%**, RevPAR $119.77 **+8.2%**, occ 69.7% | Published 26 Aug 2026 |
| CoStar US hotel, Aug 2026 full month | — | **Not located**; weekly data only. Week to 15 Aug: ADR +3.5%, RevPAR +6.2%. Week to 22 Aug: ADR **+2.3%**, RevPAR +4.4% |
| AirDNA US STR, Jul 2026 | ADR $317.55 **+6.9%**, RevPAR +7.2%, demand nights +2.0%, supply +2.6% | Published |
| CoStar/Tourism Economics FY26 forecast | RevPAR +4.4%, ADR +3.1% (raised 7 Aug 2026) | Published |
| HLT and MAR FY26 RevPAR guidance | both raised to **+3.0% to +3.5%** at Q2 | Published |
| Airbnb 3Q26 revenue guide | $4.69-4.77bn, +15% to +17% | 2Q26 letter |
| **Our own** discount penetration, Aug 2026 | **31.4% of near-term quotes discounted, up from 19.8% in July**, in all 13 cities | `06_quote_discount_panel.csv` |

**How to read it into the print.** Hotel pricing decelerated sharply through Q3: CPI lodging +4.7% in
June to +2.8% in July, and the CoStar weekly ADR series went +3.5% then +2.3% in the second half of
August. Airbnb's ex-FX ADR has been pinned at +4% for two quarters. If hotel ADR settles near +2-3%,
Airbnb's relative-price tailwind is gone and 3Q26 ADR rests on FX and bedroom mix.

**Two specific things to watch on 5 Nov.**
1. **Does Airbnb repeat the bedroom-nights disclosure?** It is new in 2Q26 and is the cleanest available
   evidence that ADR growth is value, not price. If bedroom-night growth decelerates toward nights
   growth, the durable half of ADR growth is gone. If the company drops the metric, treat that the way
   we treat the disappearance of the hotel-price comparison after 4Q23.
2. **Does the take rate finally move?** Single-fee migration should be near-complete by year-end; 3Q26
   is the first quarter with most listings on it. Management has guided FY26 flat at ~13.2% on RNPL
   timing and new-business incentives. If 3Q26 take rate is up y/y, the fee benefit is beating the
   incentives a quarter early and the 2027 bridge gets easier.

Caveat for the card: FX. The reported-minus-ex-FX wedge was +5pp in 1Q26 and +1pp in 2Q26; check
`data/processed/overnight/10_fx_quarterly.csv` before attributing any 3Q26 ADR move to pricing.

---

## 9. Corrections to existing work

- `research/notes/2026-09-05_margin-drivers.md` section 3.4 says "US hotels priced ahead of Airbnb's
  ex-FX ADR (+4%) in Q2 2026 for the first time since Q4 2024." That is right on CPI and BEA, but the
  July 2026 CoStar print (+5.7% ADR, published 26 Aug 2026, after that note was written) makes the
  point stronger, and the section's July CPI reading of +2.8% is confirmed. No error, but the note
  should be refreshed with the CoStar dollar series in `06_price_gap_monthly.csv`.
- `data/processed/overnight/06_price_per_unit_panel.csv` renames Inside Airbnb's
  `estimated_occupancy_l365d` to `mean_est_nights_booked_l365d`. **That field is estimated nights
  booked in the last 365 days (0-365), not an occupancy percentage.** Anything elsewhere in the repo
  treating it as a percentage is wrong; I did not audit for that.
- A third-party study (AirROI, 2026) claims a 55.9% median markup between Airbnb's advertised nightly
  rate and the checkout total across 28 US markets. Our parse of 1.71m of Airbnb's own quote responses
  finds no separate fee lines at all after the 2025 total-price default. The two cannot both describe
  the same 2026 checkout. Do not cite the 55.9% figure.

## 10. What to build next

1. **Keep `06_quote_panel.py` running monthly.** From March 2027 the discount series becomes a true
   year-over-year indicator of host willingness to accept, built from Airbnb's own pricing endpoint, in
   13 cities. Nothing else we hold measures that.
2. **Add hotel-listing detection to the Inside Airbnb parse.** The `room_type == "Hotel room"` cut
   already exists in the data (it carries a +6.4% premium over entire homes on the 2026 basis) and
   Airbnb's hotel business is the fastest-growing part of the mix. A city-level hotel-listing count from
   the dumps would be an independent read on a business the company only describes qualitatively.
3. **Get the missing STR monthly dollar series** (Jan, Feb, Apr, May, Aug 2026). Every source we tried
   403'd; a CoStar or STR subscription, or the monthly Asian Hospitality archive, would close it.
4. **Estimate a party-size distribution.** Airbnb does not disclose it and no hotel guests-per-occupied-
   room benchmark could be sourced. Inside Airbnb capacity plus the UK Lighthouse capacity-mix series is
   the best proxy available; a proper reconstruction would make the per-person comparison defensible
   enough for a slide.

---

## Files

| File | Contents |
|---|---|
| `analysis/src/overnight/06_price_gap.py` | Builds the price-gap series; carries the hand-entered STR/CoStar and AirDNA externals with citations |
| `analysis/src/overnight/06_wtp_hedonics.py` | Hedonic WTP regressions and the per-unit price panel |
| `analysis/src/overnight/06_quote_panel.py` | Parses Airbnb's fee-inclusive quote JSON for fee lines and discounting |
| `analysis/src/overnight/06_evidence_tables.py` | Emits the five curated evidence CSVs |
| `data/processed/overnight/06_price_gap_series.csv` | Quarterly, 1Q21-2Q26: ADR, ex-FX ADR, CPI/BEA lodging, HLT/MAR RevPAR, per-bedroom normalisation |
| `data/processed/overnight/06_price_gap_monthly.csv` | Monthly 2019-2026: CPI lodging, BEA, STR/CoStar levels, AirDNA, Airbnb's 1BR-vs-hotel claims |
| `data/processed/overnight/06_wtp_evidence.csv` | Attribute premia, hedonic and raw median cuts, both price bases |
| `data/processed/overnight/06_wtp_hedonic_coefs.csv` | Full OLS coefficient tables with CIs |
| `data/processed/overnight/06_price_per_unit_panel.csv` | Per city-dump: price per night, per bedroom-night, per capacity-night, size mix |
| `data/processed/overnight/06_quote_discount_panel.csv` | Per city-dump 2026: discount penetration and depth, fee-line frequency, quote lead time |
| `data/processed/overnight/06_quote_line_items.csv` | Raw line-item type frequency by city-dump |
| `data/processed/overnight/06_company_evidence.csv` | 63 rows of Airbnb's own disclosures on price, mix, fees and take rate, evidence vs opinion |
| `data/processed/overnight/06_expert_call_evidence.csv` | 27 rows from the five Third Bridge calls, observed vs opinion |
| `data/processed/overnight/06_choice_drivers.csv` | 37 rows of third-party survey, market and academic evidence with URLs |
| `data/processed/overnight/06_fee_timeline.csv` | 19-row dated fee and total-price-display chronology with source confidence |
| `data/processed/overnight/06_elasticities.csv` | 25 sensitivities with source, basis and confidence |
