# Choice-probability nights driver for the revenue model

Readable version: artifact "Nights Choice Driver" (claude.ai/code/artifact/5e19c458-b7ee-4dba-a6f4-0cc16b308b49). Excel: `docs/nights_choice_driver.xlsx` (Inputs / Calibration_2025 / Projection / Sensitivity / Countries / Global; the first three are live formulas). Python: `analysis/src/choice_nights_driver.py`.

## The idea

Team model: Revenue = Nights × ADR × take rate × FX, Nights is a plug. Replace the plug:

    Nights_ABNB(t) = Σ_g [ N_g(t) + M_g(t) × P_g(t) ]        g = party size {solo, pair, 3–4, 5+}
    N_g  own-category Airbnb nights (62% of guests would NOT have used a hotel — Farronato & Fradkin) → grows with category adoption
    M_g  hotel-contestable party-nights = hotel party-nights + 38% of Airbnb nights → grows with U.S. lodging demand + mix drift
    P_g  P(Airbnb | contestable party):  logit P_g(t) = logit P_g(t−1) − β·[ln(1+ADR_abnb) − ln(1+ADR_hotel)] + product shift
    Revenue = Nights × ADR × take rate × FX  (unchanged)

## 2025 U.S. calibration

| Party | Airbnb nights | own-cat. | contestable | Hotel party-nights | P(Airbnb \| pool) | Airbnb share of all lodging | Airbnb ÷ hotel price |
|---|---|---|---|---|---|---|---|
| Solo (incl. business) | 35.0 | 21.7 | 13.3 | 533.2 | 2.4% | 6.2% | 0.54x |
| Pair | 49.5 | 30.7 | 18.8 | 476.8 | 3.8% | 9.4% | 1.03x |
| 3–4 | 42.3 | 26.3 | 16.1 | 134.7 | 10.7% | 23.9% | 0.69x |
| 5+ | 18.5 | 11.5 | 7.0 | 40.4 | 14.8% | 31.4% | 0.71x |
| Total | 145.4 | 90.1 | 55.2 | 1,185.1 | 4.5% | 10.9% | — |

- Airbnb U.S. nights = NA 158M × 92% (U.S. = 39% of revenue vs NA 43%, FY2025 10-K) split by fitted party distribution (16/36/32/16%) × relative stay length (1.5/0.95/0.9/0.8).
- Hotel party-nights = 1.3B room nights (STR 2024, +1%) → 42% business (AHLA 439M/605M), 80% single-occupancy (Portuguese ledger) → leisure parties 20/54/20/6% (Hawaii + Vegas) with rooms per party 1/1/1.5/2.5.
- Airbnb = 10.9% of U.S. lodging party-nights; share rises 6% → 31% from solo to 5+.

### Price column corrected, 7 Sep 2026 (the guest fee was counted twice)

The price ratios previously read 0.69 / 1.22 / 0.80 / 0.79. They were built by taking the Jun-2026
Inside Airbnb `price` and multiplying by 1.14 for the guest service fee — but Inside Airbnb changed
what `price` means. Through the Sep-2025 dumps it is the host's listed nightly rate (fee excluded);
from the Mar-2026 dumps it *is* `price_quote_price_per_night`, a real stay quote already inclusive of
the service fee and of cleaning amortised over the stay. Verified: in `austin_2026-06-22` the two
columns are identical across 10,321 entire homes. So the fee was added to a price that already had
it, and every ratio was 12.3% too high (= 1 − 1/1.14).

`analysis/src/party_size_crossover.py` now detects the basis per dump and applies the fee only on the
listed basis. On 7 U.S. cities and 52.4k active entire homes the corrected ratios are **0.54 / 1.03 /
0.69 / 0.71**. Nothing in the projection moves: the price-ratio column is descriptive and no formula
reads it (verified against the workbook — column G of the Inputs segment table has zero references).

What does move is the story. The pair segment goes from Airbnb being **22% more expensive** than a
hotel to **3% more expensive** — roughly parity. `party_size_competitive_set.md` called that segment
"the real battleground" on the strength of the 1.22x; at 1.03x the price disadvantage that framing
rested on is mostly gone, and what is left for hotels in the couples segment is the 1–2-night
cleaning-fee penalty and check-in convenience, not the nightly rate.

Two known asymmetries remain, both flagged in the figure: the quote basis includes cleaning while the
hotel side is bare ADR with no taxes or resort fees, and a FY2024 hotel ADR is being compared to 2026
Airbnb prices. Both push the ratio up, so 0.54 / 1.03 / 0.69 / 0.71 is still a ceiling.

Same defect, no consequence: `beta_city_estimate.py` applied the same ×1.14 to the same basis. The
factor is common to every city, so a log regression absorbs it in the intercept and the null stands.

## Base-case projection (U.S.) — beta 5.0, team ADR line (rebased twice 7 Sep 2026)

| | 2025 | 2026 | 2027 | 2028 | 2029 | 2030 |
|---|---|---|---|---|---|---|
| U.S. Airbnb nights (mm) | 145.4 | 150.2 | 153.6 | 159.4 | 165.4 | 171.1 |
| growth | | 3.3% | 2.3% | 3.7% | 3.8% | 3.5% |

History of the base: beta 2.5 + ADR placeholder → 168.3mm; beta 5.0 + placeholder → 162.5mm; beta 5.0 + **team ADR line** → 171.1mm. The team's ex-FX ADR path (+3.5% FY26, +2.5% after — model/assumptions.md WS13) nearly closes the ADR gap vs hotels, so share loss shrinks to ~0 from 2027 even at the doubled beta: **the bear mechanism runs entirely through the ADR gap**.

Inputs: CoStar/TE demand +1.7%/+1.1% then 1.5%; hotel ADR +3.1%/+1.6% then 2.5%; Airbnb ADR = team WS13 base ex-FX (+3.5% 2026, +2.5% after); own-category growth 4% → 3% (grounded — see below); mix drift solo −1%, 3–4 +2%, 5+ +4%; β = 5.0.

## Sensitivity — 2025–30 U.S. nights CAGR (rows β, cols Airbnb ADR growth − hotel ADR growth per year)

| β | −2 pts | 0 | +2 pts | +4 pts |
|---|---|---|---|---|
| 2.5 (bull floor) | 5.5% | 3.7% | 2.2% | 0.9% |
| **5.0 (central)** | 7.6% | 3.7% | 0.9% | −1.1% |
| 7.0 | 9.5% | 3.7% | −0.0% | −2.3% |
| 10.3 (F&F-matched) | 12.8% | 3.7% | −1.2% | −3.5% |

## Switch rate (formerly "beta"): re-anchored 7 Sep 2026

*Renamed `SWITCH_RATE` in code and "Switch rate" in the workbook (7 Sep 2026): "beta" collides with equity beta in a pitch context — it is a demand parameter, not CAPM beta. The β symbol below refers to this same parameter, kept where it cross-references the F&F paper.*

The old central (2.5) had no evidential support, and the −4.27 cited as its anchor is F&F's *own-price elasticity for a single accommodation tier* — a different object from a category-level share response. The right anchor is F&F online Appendix **Table E9** (Demand Cross-Price Elasticities, p.30): a uniform +1% move in all six hotel tiers raises Airbnb demand **+3.76%** (3.72–3.85 across the four Airbnb tiers; own-price −2.45 to −4.39, avg −3.46). This model's analogue is d ln(Nights)/d ln(p_hotel) = 0.38 × β × (1−P) = 0.363β, so matching E9 exactly needs **β = 10.3**. Discounts (all one-directional): tier-level vs category-level; 10 dense-city sample (Austin, Boston, LA, Miami, NY, Oakland, Portland, SF, San Jose, Seattle); 2014 city-night markets vs national annual. Central set to **5.0**, grid 2.5–10.3. Beware secondary sources quoting F&F "3.9 / 1.3" — those are Table 3 *supply* elasticities, not demand.

Separate known bias: N (62% of nights) is frozen against price entirely, so the model understates Airbnb's own-price elasticity regardless of β — F&F's −3.46 covers both the hotel-switching and market-exit margins; the model prices only the first.

### Out-of-sample verification: the NYC Local Law 18 natural experiment

Sept 2023: LL18 removed ~90% of NYC Airbnb listings (~22,000 → ~2,300) — a quantity shock, so it tests the **38% contestable/diversion share** directly (and substitution strength generally) rather than β itself. Model's prediction: 5–7M removed Airbnb nights × 38% diversion ÷ ~37M hotel room-nights (NYC hotels near capacity) = +5–7% hotel demand → with hotel demand elasticity 1.1–1.3 (F&F), **ADR +4.0–6.5%**. Observed (diff-in-diff, *European Journal of Political Economy* 2025, "Short-term rental bans and the hotel industry"): **ADR +$14–19/night (+4.7–6.3% on ~$300)**, RevPAR +15.6% vs +0.3% nationally, hotel revenue +$2.1–2.9B over 18 months, quantity roughly flat (capacity-constrained — exactly the F&F mechanism). The model's substitution machinery reproduces the observed price response almost exactly. Caveats: dense-city market (upper end of substitution), and it validates the diversion margin, not the price-response margin — β still lacks a direct estimate. Leads not yet chased: FEDEA dt2026-02 (Spanish STR regulation impacts) for a European check; a proper β estimate needs a market panel with relative-price variation.

## Other countries (data pack, 7 Sep 2026)

`data/processed/country_lodging_nights.csv`. Platform STR guest-nights (Airbnb+Booking+Expedia) vs hotel guest-nights (I551), same statistical frameworks:

| | Platform STR (mm) | Hotel (mm) | STR share of guest-nights |
|---|---|---|---|
| France | 213.0 (2025) | 220.2 (2025) | **49%** |
| Spain | 189.0 (2025) | 363.1 (2024) | 34% |
| Italy | 139.0 (2025) | 288.2 (2025) | 33% |
| Germany | 68.0 (2025) | 299.9 (2024) | 19% |
| UK | 93.8 (Jul24–Jun25, ONS) | TODO | — |
| U.S. (Airbnb only, derived) | — | — | 15% |

- UK: ONS runs the same 3-platform framework as Eurostat (quarterly, with guest origin); +10.2% y/y. No ONS hotel-nights analogue — hotel side needs VisitBritain/STR.
- Greece 52mm platform nights; hotel I551 not yet pulled.
- Canada/Australia: no official platform framework; StatCan works off AirDNA scraping, Australia is commercial-data only (AirDNA/PriceLabs). Japan: minpaku law gives official registrations (40,745 dwellings, capped at 180 nights/yr) and JTA publishes reported minpaku nights — the hotel side (Overnight Travel Statistics) is excellent; nights figure still to pull.
- Caveats: platform nights = 3-platform STR, not Airbnb alone (Airbnb ≈ 69% of French STR listings); Eurostat warns platform and establishment frameworks overlap at the margin; U.S. row is Airbnb-only (excl. Vrbo), so not strictly comparable.

## Europe calibration (7 Sep 2026; supersedes the France-only build)

`analysis/src/choice_nights_driver_countries.py` → `choice_driver_countries_calibration_2025.csv`; also the **Countries** sheet in `docs/nights_choice_driver.xlsx`. Both sides *measured* (unlike the U.S.): Eurostat platform guest-nights (tour_ce_omr) × Airbnb listing share (FR 69% / ES 50% / IT 53% / DE 51%, myDataValue/AirDNA) vs hotel guest-nights (I551). Guest-nights → party-nights via people-per-party (not the U.S. rooms-per-party conversion).

| Airbnb share of lodging party-nights | solo | pair | 3–4 | 5+ | TOTAL |
|---|---|---|---|---|---|
| France | 20% | 29% | 51% | 61% | **31%** |
| Spain | 9% | 14% | 29% | 38% | **15%** |
| Italy | 9% | 13% | 28% | 38% | **15%** |
| Germany | 4% | 7% | 15% | 22% | **7%** |
| U.S. (reference) | 6% | 9% | 24% | 31% | **11%** |

The party-size gradient replicates in every country (~2× per step, same shape as the U.S.), on measured data — the strongest external validation of the segment story so far. France is the outlier market; Spain/Italy sit at U.S. share levels; Germany at two-thirds below. Open items in the script header: Airbnb nights-vs-listing share, framework overlap, transplanted party mixes, ES/DE 2024 hotel vintage, U.S. CONTESTABLE figure.

## New data pulled for this

- Farronato & Fradkin (AER 2022): 62% of Airbnb guests would not have switched to a hotel (87% at peak); accommodation own-price elasticity −4.27 (−2.9 economy Airbnb to −8.6 luxury hotel, SF); hotels in top-10 cities lost 1.3% of nights / 1.5% of revenue in 2014. https://andreyfradkin.com/assets/airbnb_welfare_paper.pdf ; https://www.library.hbs.edu/working-knowledge/the-airbnb-effect-cheaper-rooms-for-travelers-less-revenue-for-hotels
- CoStar / Tourism Economics Aug-2026 U.S. forecast: 2026 demand +1.7%, ADR +3.1%, RevPAR +4.4%, supply +0.4%; 2027 demand +1.1%, ADR +1.6% (+2.1% ex World Cup). https://www.hospitalitynet.org/news/4133888/us-hotel-forecast-assumptions-august-2026.html
- AirDNA 2026 outlook: STR supply +4.6%, ADR +1.5%, occupancy −1%. https://www.prnewswire.com/news-releases/2026-will-be-the-best-year-to-invest-in-short-term-rentals-since-2021-new-airdna-report-finds-302643393.html
- Airbnb Q2 2026: nights +10%, ADR $183.73 (+5%), bedroom nights +12%. https://howtheymake.money/en/blog/abnb-q2-2026-hotels-accelerate
- Everything else: party-size, stay-length, cross-over and hotel notes already in the repo (AHLA, STR 1.3B, Hawaii DBEDT, Las Vegas, Portuguese ledger, Inside Airbnb, Kalibri).

## Wiring

1. Link Inputs!"Airbnb ADR growth" to the model's ADR line (same ADR drives price and share).
2. Replace the NA/U.S. nights growth plug with Projection!"U.S. AIRBNB NIGHTS" (or its growth row). ADR and FX untouched. Check: 2025 U.S. revenue reproduces at $5.0B vs ~$4.8B reported (U.S.-share proxy).
2b. **The take-rate row is no longer flat.** It was hardcoded at 13.4% across 2025–30, which silently assumed the host-only fee migration for FY26 and then never collected the FY27 step. It now runs 13.4% (FY25–26) → 13.6% (FY27 on), per `host_only_fee_history_and_elasticity.md`: the single 15.5% fee is ~+58bp on guest spend, invariant to demand elasticity and to how far hosts re-price; roughly a quarter lands in FY26 and the rest in FY27, against a no-migration path of 12.9–13.1%. FY26 is held at 13.4% because incentives for Services/Experiences/hotels are contra-revenue and management guided FY26 flat. Reconcile with the team model rather than overwriting it blind.
3. Other regions: keep the team's growth for now, or recalibrate with regional hotel nights (Eurostat for EU — Krishang's file).
4. Scenarios: bear = ADR +2–4 pts above hotels, β 5.0–10.3 → nights CAGR +0.9% to −3.5%; bull = ADR parity or below, β 2.5, mix drift +2, positive product shift → 4–6%.

## Caveats

- U.S. nights proxied by revenue share; 38% substitution is 2014 big-city survey data (13% at peak) and is the biggest lever; β is a share response, −4.27 is an upper bound; hotel party-nights are derived, not observed; no explicit supply/regulation channel beyond the product-shift lever.

## Files

- `analysis/src/choice_nights_driver.py`, `analysis/src/build_nights_driver_xlsx.py`
- `docs/nights_choice_driver.xlsx`, `docs/nights_choice_driver.html`
- `data/processed/choice_driver_calibration_2025.csv`, `choice_driver_projection.csv`, `choice_driver_sensitivity.csv`

## 7 Sep 2026 (later): direct beta attempt, category adoption grounded, global build, team ADR wired

- **Beta, direct estimate — honest null.** `analysis/src/beta_city_estimate.py`: cross-city regression of Airbnb utilisation (booked nights per active listing, Inside Airbnb Jun-2026) on the relative price vs city hotel ADR, n=5–6 (Denver/New Orleans excluded — no defensible ADR; DC flagged). Result eps = −0.3 (se 0.5, R² 0.1): wrong sign, statistically zero. Recorded as the expected cross-sectional failure (desirable cities are pricier AND busier; no instrument). The F&F Table E9 anchor stands. Fix = panel version on Inside Airbnb's archived quarterly snapshots (city FE) — scaffolded in the script.
- **Category adoption grounded.** Inverting the model on disclosed NA nights (146→154→158mm, FY23–25 10-Ks) implies own-category growth **7.9% (2024) → 4.5% (2025)**; the model's 4%→3% path = observed exit rate + continued fade. EMEA implied ~10%. `data/processed/category_adoption_evidence.csv`.
- **Rest-of-world plug replaced.** `analysis/src/choice_nights_driver_global.py` → `choice_driver_global_projection.csv` + **Global** sheet: US (full model) + EMEA (4-country calibration scaled to 215mm, category 7%→5% vs ~10% implied) + NA-ex-US (tracks US) + LatAm/APAC explicit fades from +18%/+15%. Global: 533 → 743mm by 2030.
- **Team ADR line wired** (`model/assumptions.md`, WS13 base, ex-FX): FY26 ~+3.5%, FY27/28 +2.5%. Replaces the +5%/+3% placeholder and narrows the ADR gap → US 2030 nights **171.1mm (3.3% CAGR)** — higher than the old base despite beta doubling to 5.0. The bear mechanism runs entirely through the ADR gap, and the team's base case has almost none.
- **Reconciliation vs team model:** WS13 base total nights FY26 +9.9 / FY27 +8.9 / FY28 +7.4%; this build +7.1 / +7.2 / +7.1%. The gap is nearly all North America — the choice model says NA at the team's pace needs share gains or category adoption above the 2025 exit rate.

## 7 Sep 2026 (validation pass): three corrections to earlier claims

**1. "Booking is winning European STR supply" — WRONG, retracted.** Verified by direct fetch of each country page (Airbnb snapshot 2026-07-07 / Booking 2026-06-17):

| | Airbnb | Booking | Airbnb share |
|---|---|---|---|
| France | 802,763 | 360,653 | **69.0%** |
| Spain | 234,413 | 238,087 | 49.6% |
| Italy | 454,258 | 395,275 | 53.5% |
| Germany | 241,989 | 228,579 | 51.4% |

Airbnb *leads* in three of four; Booking leads only in Spain, by 3,674 listings (1.5%). The correct statement is "France is an Airbnb stronghold; elsewhere the two are at parity." Vrbo is absent from this dataset, so every share is Airbnb-vs-Booking only and is an **upper bound** on Airbnb's share of all platform supply.

**The defensible version of the claim is in nights, not listings** — see `emea_nowcast.py`: Airbnb EMEA grew +7.0% in 2025 against an EU platform market of +11.5%, undergrowing by 4.5pp (and by 11.5pp in 2024, though that year is contaminated by Tripadvisor's exit).

**2. The Eurostat "nowcast edge" — WRONG, retracted.** Eurostat's country-level platform series had reached only Q1-2026 as of Sep-2026; Airbnb reported Q1-2026 in May-2026 and Q2-2026 on 13 Aug. **Eurostat lags Airbnb by ~4 months and cannot front-run a print.** What it does give: an official-statistics read on Airbnb's share trend, and country detail Airbnb never discloses (it reports one EMEA aggregate).

**3. France 31% is denominator-dependent and should be quoted as a range.** Hotels (I551, 220.2mm guest-nights) are only **47% of French tourist-accommodation capacity**. France is Europe's camping superpower — 154mm camping nights in 2025, 37.2% of all EU camping — plus ~97.5mm holiday/short-stay (I552) nights:

| Denominator | Airbnb share |
|---|---|
| Hotels only (as published) | 29.6% |
| + camping | 22.6% |
| + camping + holiday/short-stay | 19.7% |
| joint stress (Airbnb 55% of platform + full denominator) | **16.4%** |

I552 overlaps Airbnb's own supply, so the full-denominator figure double-counts — the honest range is **~20-30%, not a point estimate of 31%**. Every correction pushes the same way: down. France is still the highest-share market in the set, but the gap to Spain/Italy is narrower than the headline implies.

## Party size over time — the mix thesis needs restating

`analysis/src/party_size_time_series.py` → `airbnb_party_size_time_series.csv`. Differencing Airbnb's cumulative guest-arrival milestones against bookings in the same window gives a genuine non-overlapping series:

| Window | Years | Guests/booking |
|---|---|---|
| Aug-18 → Mar-19 | 0.6 | 2.33 |
| Mar-19 → Sep-20 | 1.5 | 3.22 |
| Sep-20 → Oct-21 | 1.0 | 2.52 |
| Oct-21 → Oct-24 | 3.0 | **3.05** |
| Oct-24 → Dec-25 | 1.2 | **2.92** |

Windows under ~2.5yr are dominated by the arrival-vs-booking lead-time mismatch (hence 2.33 next to 3.22). The ten long windows (≥2.5yr) span 2.81–3.05, mean **2.96**.

**Average party size is ~2.95 and has no measurable trend.** The six long windows that do *not* depend on the 2025 figure (anchored on the 2-billionth-arrival event, which Airbnb dated precisely) span 2.81–3.05, mean **2.953**.

**Correction (an earlier draft of this section overclaimed a decline).** The 10-K says "over 2.5 billion" cumulative arrivals — a floor, not a point. At exactly 2.50bn the final window is 2.92; at 2.55bn it is 3.22; at 2.60bn, 3.51. **A ~4% error in one rounded disclosure flips the conclusion from "falling 4%" to "rising 5%."** The level is solid; the direction is not identified by the milestones Airbnb publishes.

Provenance note (Airbnb IPO'd Dec-2020, so the pre-IPO inputs deserve scrutiny): nights booked 2017–19 come from the **S-1**, which discloses three years of pre-IPO history as any IPO filing must — SEC-filed. The 400mm (Aug-18) and 500mm (Mar-19) arrival milestones are **Newsroom press releases from the private period** — unaudited marketing announcements. 825mm and 2.5bn are both quoted as "over", i.e. floors.

Reconciling with the group-travel narrative (multigenerational travel 47% of travellers in 2026, +17% vs 2024; 4+ bedroom homes the fastest-growing category; Bedroom Nights +12% vs Nights +10%): bedrooms per stay is rising ~1.8%/yr while guests per booking shows no trend, so **guests per bedroom is probably falling ~1.8%/yr — the same size group booking more space** (this rests on the stable level, not on a measured decline). Consistent with Inside Airbnb (guests fill ~half of listed capacity). Also consistent with a *polarising* distribution at a constant mean: solo travel rising (~25% of Airbnb guests travel solo) and multigenerational rising, hollowing the middle.

**Implication for the pitch: "group travel" shows up in ADR, not in nights.** That is bullish for revenue per booking and bearish-to-neutral for the nights line — closer to the bear thesis than the bull one. The model's MIX_DRIFT (5+ at +4%/yr) is defensible only as a *distribution-widening* assumption, not as rising mean party size; it should be re-derived, and the 5+ drift is a candidate to cut.

## Stay length made an explicit lever (8 Sep 2026)

The model's machinery (N, M, P) is denominated in party-**nights**, so trip **intensity** had no home: a change in nights per booking could only enter by silently contaminating the category- and market-growth terms. It is now a separate multiplicative index in `choice_nights_driver.py` (`STAY_LENGTH`, with `_BEAR` / `_BULL` paths), applied after the share step, and a fifth term in the growth decomposition.

**Nights per booking, FY20–FY25 10-K MD&A:**

| | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | Δ |
|---|---|---|---|---|---|---|---|
| North America | 4.4 | 4.3 | 4.2 | 4.1 | 4.1 | 4.1 | −7%, **flat since 2023** |
| EMEA | 4.4 | 4.4 | 4.2 | 3.9 | 3.8 | 3.8 | −14% |
| Latin America | 4.4 | 4.3 | 4.2 | 3.9 | 3.7 | 3.6 | −18% |
| Asia Pacific | 2.8 | 2.7 | 3.2 | 3.3 | 3.3 | 3.3 | **+18%** |
| Global | 4.1 | 4.1 | 4.1 | 3.9 | 3.8 | 3.7 | −2.0%/yr |

The global −2%/yr drag cost **~58mm nights in 2025 (10.8% of the year's total)** — but it is *not* a U.S. phenomenon. NA has held 4.1 for three years, so **the U.S. base case carries no drag**; the decline is EMEA/LatAm, and APAC is rising.

**U.S. sensitivity (2030 nights, CAGR):** base flat 4.1 → 171.1mm, +3.31% · bear −2%/yr → **154.8mm, +1.27%** · bull +1%/yr → 179.8mm, +4.35%. A stay-length assumption is worth ~±1.5pts of CAGR — comparable to the switch rate, and previously invisible.

**EMEA** now carries its own path in `choice_nights_driver_global.py` (`EMEA_STAY_LENGTH`, 3.80 → 3.63, fading the recent −2.6%/yr to −1.0%/yr on the view that the COVID long-stay unwind is mostly done). Global nights: **533 → 730mm by 2030, FY26 +6.7%** (was +7.1% before the lever), vs the team's WS13 base of +9.9%.

**Caveat, and it cuts both ways:** the 2020–22 plateau at 4.1–4.4 was COVID long-stay inflation, so part of the global fall is normalisation rather than deterioration — and normalisation is self-limiting. Against 2019 (US reservation panel, 3.7 nights) today's level is not obviously abnormal. What argues structural: the decline has run three full years past reopening and is concentrated in the two largest Western regions. The lever exists so this can be argued explicitly rather than assumed away.

**Workbook:** "Stay length, nights per booking (NA)" is now a yellow lever row on Inputs. Note this required a builder fix — the year-path writer hardcoded a "—" in the 2025 column and percent-formatted every row, which would have rendered 4.1 as "410.0%"; level rows are now handled separately.

## Full model audit, 8 Sep 2026 (with Krish's party-size series merged)

**What Krish's series is** (`abnb_party_size_reviews_quarterly.csv`, PR #33): party composition parsed from **Inside Airbnb review text** — 74m reviews, 123 markets, 35 countries, quarterly 2011Q1–2026Q2, global + 4 regions, with fixed-2019 market weights so new cities can't masquerade as a trend. Reviews that state who travelled (solo / couple / family / friends-group; 6–13% of reviews, ~2% give a head-count) are converted to an implied party size. Validated against Hawaii DBEDT rental-house party size at **r = 0.96–0.99** for direction; the *level* is biased high (~3.5 vs 2.5 observed) because couples under-state and families over-state. It is an index of composition, not a calibrated level.

**It resolves my open question — and it does not contradict the milestone work.**

| Source | Party-size trend |
|---|---|
| Krish review proxy, 2018–25 (post mention-rate stabilisation) | **+0.62%/yr** |
| Krish review proxy, 2012–25 | +0.88%/yr |
| Hawaii DBEDT rental house, observed, 2013–24 (2.28 → 2.49) | **+0.80%/yr** |
| My guest-arrival milestone method | flat; noise band ±4% |

A +0.6–0.9%/yr trend is ~+4.4% over seven years — exactly at the edge of what the milestone method can resolve. So "no trend detectable" (mine) and "+0.8%/yr" (his) are **consistent**; his method simply has the resolution mine lacks. My earlier phrasing ("no evidence party size is rising") was too strong and is corrected: **party size is rising, slowly.** Composition is families replacing couples (couple share 50% → 25%, family 31% → 46%, 2012 → 2025), and the size rise is a *capacity-mix* story — guests booking bigger homes — while within any given home size parties got slightly smaller.

### Audit findings

**1. `MIX_DRIFT` is validated — the flag I raised is cleared.** The vector implies mean party size growing **+0.98%/yr** vs +0.62% (reviews) and +0.80% (Hawaii observed). ~1.2x observed: modestly aggressive, right order of magnitude. Also note Hawaii *hotel* parties drift up too (+0.34%/yr) and the model applies the same vector to both pools, which is **conservative** — the observed Airbnb-vs-hotel divergence (0.80 vs 0.34) is wider than modelled.

**2. US nights are ~4% too high, and the model's own reconciliation says so.** `US_SHARE_OF_NA = 0.92` is a *revenue* share used as a *nights* share — exact only if revenue per night is identical in the US and Canada/Mexico. It isn't (Mexico is materially cheaper), so US ADR sits above the NA blend and the US nights share must sit below the US revenue share. 145.4mm × $255 NA ADR × 13.4% = **$4.97bn vs $4.76bn reported, +4.4%**. Implied US nights ≈ **139mm, not 145.4mm**. Added `US_ADR_PREMIUM` as an explicit lever (left at 1.00 so nothing moves silently; 1.05 clears the gap → 138.4mm). Levels scale; the growth decomposition is unaffected.

**3. The switch rate is now nearly inert in the base case.** With the team's ex-FX ADR path (near hotel parity), moving it 5.0 → 10.3 costs only **−2.1%** of 2030 nights. It only bites when an ADR gap opens. **The bear case has to be argued through ADR, not through the switch rate** — worth knowing before defending 5.0 in a meeting.

**4. Lever ranking (2030 nights, US):** stay length −2%/yr **−9.5%** · category growth −1pt −3.1% · mix drift halved −2.3% · switch rate 10.3 −2.1% · market growth −0.5pt −0.8%. Stay length, added yesterday, is now the largest single lever.

**5. Checks that passed:** hotel party-nights reconvert to the input room-nights exactly (760.9 vs 760.9); the five-term growth decomposition sums to published growth to 0.00e+00; **workbook and script agree on every input** (13 scalars, 3 year-paths, 4×5 segment table).

**6. Dead code annotated:** `NPB_NA` and `HOTEL_ALOS` are declared with sources but never referenced — now labelled NOT USED rather than left looking load-bearing (hotel nights enter as room-nights via `ROOMS_PER_PARTY`, so ALOS never enters). `STAY_LENGTH_BEAR/BULL` are now wired into `main()` output.

### Still unsourced / still assumed (unchanged, and now the top of the list)

- **`ROOMS_PER_PARTY` (1/1/1.5/2.5) has no citation anywhere** and sets the hotel denominator. Highest-priority gap.
- `LEIS_NIGHTS_REL` — Portuguese ledger applied to US leisure.
- Market growth and hotel ADR beyond 2027 — past CoStar's forecast horizon.
- `CATEGORY_GROWTH` entry rate is grounded; the *fade* to 3% is judgment.
- `PRODUCT_SHIFT` all zero — regulation and product enter nowhere, despite LL18 giving a measured magnitude.
- `CONTESTABLE = 0.38` — 2014 San Francisco survey, still the single most load-bearing input.
- Group/meetings (~25% of hotel nights, contracted, non-contestable) still sit inside the leisure pool.

## Model edited on Krish's data, 8 Sep 2026

**1. `US_ADR_PREMIUM` set to 1.05.** Clears the revenue reconciliation ($4.97bn modelled vs $4.76bn reported). **U.S. nights 145.4 → 138.4mm.** Every level scales ~−4.8%; the growth decomposition is unchanged. NA-ex-US rises to 19.6mm in the global build, so global 2025 still ties to the disclosed 533mm.

**2. Mix drift split into two vectors.** One vector was previously applied to *both* pools, assuming Airbnb and hotel parties grow at the same rate. Hawaii DBEDT is the only source observing both in one market and says they don't:

| 2013 → 2024 | | |
|---|---|---|
| Rental house | 2.28 → 2.49 | **+0.80%/yr** |
| Hotel | 2.22 → 2.30 | **+0.34%/yr** |

Rental parties drift **2.35× faster**. Calibration: the *level* from Krish's global review proxy (+0.62%/yr, 2018–25, the window after the mention rate stabilised at ~6%); the *relative* rate from the Hawaii ratio → hotel +0.26%/yr.

| | solo | pair | 3–4 | 5+ | implied mean party growth |
|---|---|---|---|---|---|
| Old (both pools) | −0.010 | 0 | 0.020 | 0.040 | +0.98%/yr |
| `MIX_DRIFT_ABNB` (→ N) | −0.0063 | 0 | 0.0127 | 0.0253 | **+0.62%/yr** |
| `MIX_DRIFT_HOTEL` (→ M) | −0.0027 | 0 | 0.0054 | 0.0107 | **+0.26%/yr** |

**The previous setup was flattering the forecast** by drifting the whole contestable pool at Airbnb's rate. Mix contribution falls from ~0.9pp to ~0.45pp/yr.

**Combined effect: 2030 U.S. nights 171.1 → 159.3mm, CAGR +3.31% → +2.84%.** Global 533 → 726mm, FY26 +6.6% (vs the team's WS13 base +9.9%).

**3. The Airbnb ADR path is flagged PROVISIONAL.** It currently points at the WS13 overnight base, not the team's final ADR line, which is still outstanding. This is the largest swing factor left — and note the switch rate only bites when an ADR gap opens (5.0 → 10.3 costs just 2.1% at parity), so **the ADR line, not the switch rate, decides the bear case.** Re-point `ABNB_ADR_GROWTH` when it lands.

## Beyond Hawaii: how far does the rental-vs-hotel party gap generalise? (8 Sep 2026)

`analysis/src/party_size_rental_vs_hotel.py` → `party_size_rental_vs_hotel_by_country.csv`. The split mix-drift rests on one number — Hawaii's 2.35× rental-vs-hotel growth ratio — so this tests it against every other source available. **The two claims have very different evidence.**

### Level gap: strongly validated, 40 countries

Booking.com rectour24 (1.63m stays, 2023), whole-home analogues (Holiday home / Villa / Chalet / Country house / Apartment) vs Hotel, ≥500 reviews each side:

- **Rental parties larger in 39 of 40 countries** · mean gap **+0.35 people (1.131×)** · paired **t = 10.2**
- Only exception: Thailand (0.929×)
- Widest: Switzerland 1.310×, Iceland 1.258×, Czechia 1.253×, Ireland 1.231×, Japan 1.213×

### Trend divergence: still one market

Hawaii DBEDT remains the only source observing both types on the same instrument over a long horizon (rental +0.80%/yr vs hotel +0.34%/yr, 2013–24). What I tried and why each failed:

- **Booking 515k** (Europe hotels, 2015-08→2017-08): 25 months, ~2 summers, so month dummies and a trend aren't jointly identified. Returns +3.9%/yr — not credible next to Hawaii's +0.34%; treated as noise, not a contradiction.
- **rectour24**: single year, speaks only to the level.
- **Tourism Research Australia / VisitBritain GBTS / Statistics Canada NTS**: all three collect party size *and* accommodation type but publish separate marginals — the cross-tab appears to sit in microdata (PUMF / data request). **That's the next pull if this needs hardening.**

### The caveat that matters most

**The gap is weakest exactly where the model needs it.** The U.S. ranks **33rd of 40 at 1.051×** against a 1.131× mean; Hawaii (1.080×) is also below the mean. Two readings, both worth stating:

1. Booking's U.S. whole-home sample is thin and unrepresentative — 2,165 reviews vs 134,537 hotel, skewed to aparthotel/extended-stay rather than the detached homes Airbnb sells. On that read the U.S. figure is understated.
2. If it isn't understated, **the U.S. mix tailwind is genuinely weaker than the global number implies** and `MIX_DRIFT_ABNB` should be cut below +0.62%/yr.

Unresolved. Treat +0.62%/yr as the optimistic end of the U.S. range.

**Counter-signal:** VisitBritain reports UK solo overnight trips at **28% in 2024, +3pp on 2023 and +4pp on 2022**. Rising solo travel pushes mean party size down and is a genuine offset in at least one large market.

**Licence:** rectour24 is CC BY-SA 4.0, **non-commercial**. Fine for internal validation; it must not be reproduced in anything client-facing.

## TRA / VisitBritain / StatCan pulled (8 Sep 2026)

| Source | Outcome |
|---|---|
| **Tourism Research Australia** | ❌ The party-size × accommodation cross-tab exists only in **TRA Online, a paid subscriber portal**. Also note the National Visitor Survey ended Dec-2024 and is replaced by Domestic Tourism Statistics from Jan-2025, so any TRA series breaks there regardless. |
| **Statistics Canada NTS** | ❌ Public tables carry party size and accommodation type as **separate marginals**; StatCan's own guidance is to email tourism@statcan.gc.ca for the cross-tab. Not obtainable without a data request. |
| **VisitBritain GBTS** | ✅ **Partial success.** The 2022–24 pivot workbook contains 28k weighted trip-level records with `Main Accommodation Type` × `Children on trip`. No party-size field, but children-on-trip is the sharper family measure — and the thesis is about families. → `data/processed/gbts_children_by_accommodation.csv` |

### What the UK data says

Share of GB overnight trips including a child, weighted:

| Year | Commercial property rental | Serviced accommodation | Gap | Ratio |
|---|---|---|---|---|
| 2022 | 37.7% | 25.3% | 12.4pp | 1.49× |
| 2023 | 39.2% | 23.9% | 15.3pp | 1.64× |
| 2024 | 33.7% | 22.3% | 11.4pp | 1.51× |

**LEVEL: confirmed, and more sharply than the Booking cross-section** — UK rental trips are ~1.5× more likely to include children than hotel trips, in a second market on a single instrument.

**TREND: not confirmed.** The gap widened then narrowed and ends **1.0pp lower in 2024 than 2022**. Both categories' family share fell in 2024, consistent with VisitBritain's separate finding that solo trips rose to 28% (+4pp vs 2022; full distribution 28 / 35 / 24 / 9 / 3% for solo / 2 / 3–4 / 5–9 / 10+). Three years, one a COVID-recovery year — this can't refute Hawaii, but it doesn't support the divergence either.

### Net read after all three pulls

- **Level gap: three independent confirmations** — Hawaii (observed), 40-country Booking cross-section (39/40, t = 10.2), UK trip survey (1.5×). This is now solid.
- **Trend divergence: one market for (Hawaii), one market against (UK).** The model's 2.35× mix-drift ratio is annotated in the code as **the optimistic case, not an established fact**.

The thesis should lean on the level gap, which is well-evidenced, and treat the widening as a hypothesis rather than a finding.

## Spain INE microdata — the fourth source, and it settles the divergence question (8 Sep 2026)

`analysis/src/ine_spain_party_size.py` → `ine_spain_party_size_by_accommodation.csv`. **129 monthly microdata files, 2015–2026, free from INE**, weighted trip records with `MIEMV` (household members on the trip = party size) and `ALOJAPRIN` coding hotel (1) separately from whole-home rental (3). This is the strongest instrument in the set: official, weighted, 11 full years, both accommodation types, real party size.

*(Two gotchas for anyone re-running it: the month in the URL is **not zero-padded** (`datos_9_23.zip`), and INE writes decimals with a **comma** — without `decimal=","` the weight column parses as text, every weight becomes NaN and the sample silently vanishes.)*

| | Rental ÷ hotel |
|---|---|
| Level, mean across 12 years | **1.167×** (range 1.09–1.22, stable) |
| Trend in the ratio, 2015–2025 | **+0.04%/yr, se 0.35, t = +0.12 → flat** |
| Level change | rental −0.17%/yr, hotel −0.21%/yr — **both fell**, opposite to Hawaii |

### The divergence scoreboard is now 1 for, 2 against

| Market | Years | Verdict on rental parties growing faster |
|---|---|---|
| Hawaii | 11 | **FOR** — 2.31× |
| **Spain** | **11** | **AGAINST** — ratio flat, t = 0.12 |
| UK | 3 | AGAINST — gap narrower in 2024 than 2022 |

**The strongest dataset is one of the two against.** The model's split mix-drift (`MIX_DRIFT_ABNB` +0.62%/yr vs `MIX_DRIFT_HOTEL` +0.26%/yr) is therefore **not an established fact** and is annotated as such in the code. Impact of the alternatives on 2030 U.S. nights: both vectors at the Airbnb rate 160.2mm (+0.6%); both at the hotel rate 157.6mm (−1.1%); **mix drift off entirely — the Spain/UK reading — 155.7mm (−2.2%, CAGR 2.84% → 2.38%)**. Left at the split for continuity; a reviewer who takes Spain at face value should zero both.

**What survives, and it is the more important half:** the level gap now has **four independent confirmations** — Hawaii, the 40-country Booking cross-section, the UK trip survey, and Spain. Rentals genuinely serve larger, more family-weighted parties everywhere it can be measured. The thesis should lean on that structural fact and treat the widening as an open question.

## Regional breakdown (8 Sep 2026)

`choice_driver_regional_projection.csv` and a new block on the workbook's **Global** sheet.

| mm nights | 2025 | 2030 | CAGR | Share 2025 → 2030 |
|---|---|---|---|---|
| North America | 158.0 | 181.8 | **+2.85%** | 29.6% → 25.0% |
| EMEA | 215.0 | 263.8 | **+4.18%** | 40.3% → 36.3% |
| LatAm | 90.0 | 162.8 | **+12.59%** | 16.9% → 22.4% |
| APAC | 70.0 | 117.9 | **+10.99%** | 13.1% → 16.2% |
| **Total** | **533.0** | **726.3** | **+6.38%** | |

Contribution to the 36.3% five-year total: LatAm +13.7pp (37.7% of all growth), EMEA +9.2pp (25.2%), APAC +9.0pp (24.8%), North America +4.5pp (12.3%).

**The confidence gradient runs backwards to the growth.** North America is the full segment choice model; EMEA is calibrated on measured Eurostat platform and hotel nights for FR/ES/IT/DE and scaled. **LatAm and APAC are growth fades off disclosed 2025 rates with no hotel-side data and no choice model at all — yet they are 30% of 2025 nights and 62% of the 2025–30 growth.** That is the least evidenced part of the forecast and the first place to spend more research.

## Regional models on region-specific data (8 Sep 2026)

`analysis/src/choice_nights_driver_regional.py` → `choice_driver_regional_detail.csv`. Nights are now built the same way ADR is — one calibration per Airbnb reporting segment — so the two multiply region by region without a mix error.

**The regions are not variants of one market.** 2025 anchors, all from the FY2025 10-K regional table:

| | Nights | ADR | Stay length | 2025 nights growth | GBV check |
|---|---|---|---|---|---|
| North America | 158.0 | **$255.03** | 4.1 (flat since 2023) | +2.6% | $40.29bn |
| EMEA | 215.0 | $158.89 | 3.8 (**−14%** since 2020) | +7.0% | $34.16bn |
| LatAm | 90.0 | **$94.91** | 3.6 (**−18%**, falling fastest) | +18.4% | $8.54bn |
| APAC | 70.0 | $118.20 | 3.3 (**+18%**, the only riser) | +14.8% | $8.27bn |

ADR spans 2.7×, stay length moves in opposite directions, and nights growth spans 2.6% to 18.4%. A single global path cannot represent that.

### Output

| | 2025 | 2030 | CAGR | Share |
|---|---|---|---|---|
| North America | 158.0 | 175.5 | **+2.13%** | 29.6% → 24.5% |
| EMEA | 215.0 | 264.3 | **+4.22%** | 40.3% → 36.9% |
| LatAm | 90.0 | 154.7 | **+11.44%** | 16.9% → 21.6% |
| APAC | 70.0 | 122.5 | **+11.84%** | 13.1% → 17.1% |
| **Total** | **533.0** | **717.1** | **+6.11%** | |

### The finding that matters most

**The confidence gradient runs backwards to the growth.**

| Region | Evidence base | Share of 2025–30 growth |
|---|---|---|
| North America | Full choice model — STR room nights, AHLA business split, Hawaii/Vegas party mix, CoStar forecasts | 9.5% |
| EMEA | Measured Eurostat platform + hotel nights (FR/ES/IT/DE), Spain INE party size by accommodation | 26.8% |
| LatAm | **No hotel-side data. Growth model only.** | 35.2% |
| APAC | **No hotel-side data. Growth model only.** | 28.5% |

**64% of all forecast growth comes from the two regions where we have no hotel-side data and no calibrated share.** All the analytical effort so far — the switch rate, the contestable share, the party-size work, the NYC validation — sits on the 36% that grows slowest. That is the single largest research gap in the nights work, and the first place to spend the next hour.

What *is* region-specific for LatAm/APAC even without a hotel side: disclosed nights growth, ADR level and growth, and stay-length direction (LatAm −2.7%/yr vs APAC +0.6%/yr). Japan's minpaku law also caps a property at 180 nights/yr and lets municipalities zero it out, so APAC supply has a legal ceiling the other regions lack.

**Flagged as provisional:** regional ADR here is GBV ÷ nights from the 10-K, which **includes FX**, while the share equation wants ex-FX. Replace `ABNB_ADR` with the team's regional ex-FX line when it lands. Only NA and EMEA have a hotel ADR comparator, so only those two run a price-driven share term at all.

## Source pulls attempted 8 Sep 2026 — outcomes

| Source | Outcome |
|---|---|
| **Spain INE ETR** | ✅ 129 monthly microdata files, free, 2015–2026 — the one open trip-level microdata source |
| **VisitBritain GBTS** | ✅ 28k weighted trip records, children × accommodation |
| **TripAdvisor Content API** | ⚠️ **Actionable, needs you.** 5,000 free calls/month, `trip_types` breakdown (business/couples/family/solo) per property, covers hotels *and* rentals. Requires account signup + a credit card for overage — a billing commitment I shouldn't make on your behalf. Best remaining source by far: one instrument, both accommodation types, many markets. |
| **Germany FUR Reiseanalyse** | ❌ Commercial study (~8,000 respondents/yr since 1970). Only selected summary publications are free; the cross-tab is in the paid product. |
| **France INSEE SDT** | ⚠️ Aggregate tables free on INSEE/data.gouv (accommodation and party published as separate marginals). Trip-level detail files are on **Progedo/ADISP**, which needs an account and a stated research purpose. |
| **Netherlands CBS** | ❌ Open OData API works and needs no key, but the cross-tab doesn't exist: accommodation tables (71080ned, 84368NED) have no party dimension, and the party-size table (71337ned) crosses party against *trip purpose*, not accommodation. |
| **US states** | ❌ Colorado's Longwoods PDF link is dead; Texas publishes person-days rather than party size; Virginia's portal has lodging volumes, not party composition. No free state-level cross-tab found. |

### How to request the Statistics Canada NTS cross-tab

The public tables carry party size and accommodation type only as separate marginals; the cross-tab is a custom tabulation. Route:

1. **Email `tourism@statcan.gc.ca`** — this is the address StatCan's own NTS documentation directs users to, and the fastest route for a straightforward cross-tab.
2. Ask specifically for: *National Travel Survey, person-trips and person-nights by **type of accommodation** × **size of travel party**, domestic overnight trips, annual, 2016–2025.* Naming the survey, both variables, the unit, and the year range avoids a scoping round-trip.
3. Custom tabulations are **cost-recoverable** — expect a quote first. Simple cross-tabs are usually modest; ask for the estimate before approving.
4. Free alternative if the quote is unattractive: the **NTS Public Use Microdata File**, which carries both variables at record level. It's distributed through the Data Liberation Initiative (free at any DLI-member university) or purchasable directly. If anyone on the team has a university affiliation, that's the zero-cost path.
5. Turnaround is typically a few weeks, so start it now if it's wanted for the deck rather than after.

## LatAm / APAC hotel-side evidence (8 Sep 2026) — the biggest gap, partly closed

`analysis/src/latam_apac_hotel_evidence.py` → `latam_apac_hotel_evidence.csv`, `latam_apac_hotel_series.csv`.

Two national statistical offices publish free, usable hotel-side series:

**Mexico — DATATUR / SECTUR, *Turismo en Cifras*, Dec-2025**

| | 2023 | 2024 | 2025 |
|---|---|---|---|
| Average occupied rooms | 419,768 | 438,624 | **466,958** (+6.5%) |
| National occupancy | 52.2% | 51.4% | 54.1% |
| Implied room-nights | 153.2mm | 160.1mm | **170.4mm** |

Plus 89.8mm arrivals to hotel rooms in 2025 (67.6mm domestic / 22.2mm international) → **1.90 nights per arrival**.

**Japan — JTA Overnight Travel Statistics, 2025 preliminary annual**

Total guest-nights **653.48mm, −0.8% y/y** (domestic 475.61mm, −3.8%; international 177.87mm, +8.2%). Occupancy by type: ryokan 38.4%, resort 56.9%, business 75.3%, city 74.2%; all types 61.8%.

### Why this matters more than it looks

The regional model's contestable-pool growth for these two regions was a **pure guess** (3.0% / 3.5%). These are the first observations against it, and they point in **opposite directions**:

| | Hotel-side proxy | Observed | Old model | Airbnb 2025 | Airbnb − market |
|---|---|---|---|---|---|
| LatAm | Mexico room-nights | **+6.5%** | +3.0% | +18.4% | +11.9pp |
| APAC | Japan guest-nights | **−0.8%** | +3.5% | +14.8% | +15.6pp |

- **LatAm raised 3.0% → 5.0%.** The market is growing roughly twice as fast as assumed, so *less* of Airbnb's +18.4% has to be share gain. This makes the LatAm path **more** robust, not less.
- **APAC cut 3.5% → 1.0%.** Japan's hotel nights *fell*. If Japan is representative, essentially **all** of APAC's +14.8% is share gain against a flat market — the most fragile position in the model, and the reason APAC now carries the steepest fade.

Updated regional output: NA +2.13%, EMEA +4.22%, **LatAm +11.97%**, **APAC +11.15%**, total +6.11% CAGR.

### What is still missing

Neither country publishes party size by accommodation type, so **P(Airbnb | contestable) still cannot be calibrated outside NA and EMEA** — these are market-growth anchors, not choice models. Mexico is not LatAm and Japan is not APAC. **Brazil is the highest-value remaining pull** (LatAm's largest Airbnb market; IBGE publishes capacity via SIDRA but no clean guest-nights series), followed by China, India, Korea and Australia — all unpulled.

Units differ and must not be added: Mexico publishes **room**-nights, Japan publishes **guest**-nights.

## Five more markets pulled: Brazil, China, India, Korea, Australia (8 Sep 2026)

Seven markets now in `latam_apac_hotel_evidence.py`, in two tiers.

**Tier 1 — national census, usable directly:** Mexico (DATATUR) and Japan (JTA), as above.

**Tier 2 — partial or sample-based, directional only:**

| Market | What it says | Why it's Tier 2 |
|---|---|---|
| **Brazil** | Occupancy +2.1%, ADR +10.5%, RevPAR +12.8% (FY25); urban occupancy 60.8% (2024) | FOHB panel of 583 chain hotels / ~91k rooms — not a census, urban-chain skewed. Occupancy is a *rate*, so room-nights ≈ supply + occupancy growth → plausibly **+4–5%**, consistent with Mexico |
| **China** | 7,586 star-rated hotels; occupancy 49.2% → **46.8%** (−4.9%); domestic trips 6.522bn (+16.2%) | **Largely irrelevant — Airbnb exited domestic China in July 2022.** Enters only via outbound travellers. Note the internal tension: trips +16.2% while star-rated occupancy fell, i.e. Chinese travellers moving *away* from star-rated hotels |
| **Korea** | Inbound +15.2%; Seoul occupancy 80.8–81.6%; ADR +14.6% | City-level, inbound-led; no national room-nights series |
| **India** | Occupancy 67.5% FY24 (from ~66%); premium 70–72% → 72–74% FY26 | Occupancy **rising**; FHRAI/ICRA industry estimates, not official statistics |
| **Australia** | 418mm domestic visitor nights 2025 (91mm business) | **Series break** — NVS ended Dec-2024, DoTS replaces it Jan-2025. ABS survey covers 15+ room establishments only |

### This changed the APAC call — Japan alone was a trap

My first read cut APAC market growth to **1.0%** on Japan's −0.8%. The other four markets say Japan is not representative: Korea inbound +15.2%, India occupancy rising, Australia roughly flat, and China nearly irrelevant. **APAC revised to 2.0%.** LatAm stays at 5.0% — Brazil's implied +4–5% corroborates Mexico's +6.5% rather than contradicting it.

Updated regional output: NA +2.13%, EMEA +4.22%, **LatAm +11.97%**, **APAC +11.42%**, total **+6.15%** CAGR.

### Three limits that apply to all seven

1. **None of the seven publishes party size by accommodation type.** P(Airbnb | contestable) still cannot be calibrated outside NA and EMEA. Every figure here is a market-*growth* anchor, not a choice model.
2. **Units are not comparable** — Mexico room-nights, Japan guest-nights, Brazil an occupancy rate on a chain panel, China star-rated only, Australia 15+ room establishments. Never add them.
3. **Coverage bias runs one way everywhere.** Official surveys count registered establishments and systematically exclude the small-operator segment Airbnb competes with, so hotel-side growth measured this way likely **understates** total lodging demand.

Brazil still lacks a clean national guest-nights series (IBGE publishes capacity via SIDRA) — the highest-value single remaining pull in LatAm.

## Is the model bottom-up or top-down? — correcting my own description (8 Sep 2026)

**It is top-down, and I described it wrongly earlier.** When I reconciled against the team model I called this "the bottom-up build." That was sloppy and worth fixing, because the distinction matters for how much independent validation it provides.

What actually goes in:

| Step | Source | Direction |
|---|---|---|
| U.S. hotel room nights (1.3bn) | STR/CoStar national aggregate | **top-down** |
| Business/leisure split (42/58) | AHLA national aggregate | **top-down** |
| Leisure party mix (20/54/20/6) | Hawaii + Vegas surveys, applied nationally | **top-down** |
| Rooms per party | assumption, now checked against Japan | assumption |
| Airbnb U.S. nights | disclosed NA total × a revenue-share proxy | **top-down** |
| Forward years | growth rates applied to those aggregates | **top-down** |

So it is a **market-sizing / share model with a party-size decomposition** — top-down throughout. Nothing is built up from units.

A genuinely bottom-up nights model would be `listings × availability × occupancy × stay length`, which is what AirDNA does. **We have the ingredients and do not use them**: Inside Airbnb gives listings, booked run lengths and active-listing counts for 8–13 U.S. cities. Building that would be a real independent check on the *level* — currently the level rests entirely on the 10-K regional table and the revenue-share proxy, which is exactly the input the audit found to be ~4% too high. That is the most valuable unbuilt piece in the nights work after the LatAm/APAC share calibration.

## Party size across 122 world cities — the divergence question, answered per city

`analysis/src/party_size_divergence_by_city.py` → `party_size_trend_by_market.csv`. Uses Krish's per-market review panel (no new pull): 122 markets, 36 countries, ≥400 stated compositions/year, ≥8 years, log-linear trend with a t-stat per market.

| Region | n | Mean | Median | Significant (t>2) | Positive |
|---|---|---|---|---|---|
| **North America** | 42 | **+0.66%** | +0.71% | **52%** | **81%** |
| EMEA | 57 | −0.01% | +0.02% | 12% | 51% |
| LatAm | 7 | +0.26% | +0.17% | 14% | 57% |
| APAC | 16 | −0.19% | −0.10% | 19% | 38% |
| **All** | 122 | +0.21% | +0.12% | 27% | 60% |

**Two conclusions, pulling opposite ways:**

1. **The U.S. model's mix drift is validated.** `MIX_DRIFT_ABNB` implies +0.62%/yr; North America's 42 markets average **+0.66%/yr**, with half individually significant and 81% positive. Independent cut of the data, close agreement.
2. **The global "+0.62%" was really a North America number.** EMEA is flat (−0.01%, only 12% significant) — which **independently corroborates the Spain INE microdata**, two different instruments reaching the same answer. APAC is flat to slightly negative.

Dispersion is the other headline: **sd 0.73%/yr**, from Salem OR +3.8% to Singapore −2.8%. Anglo markets lead (US +0.67, Canada +0.60, UK +0.52); continental Europe is flat to negative (Italy −0.08, France −0.05, Switzerland −0.27). "Party sizes are rising" is a North American fact, not a global one.

## ROOMS_PER_PARTY — was the top unsourced input, now has two supportive checks

It implies leisure guests-per-occupied-room of 2.00 (pair), 2.27 (3–4), 2.20 (5+).

1. **Japan, computed from two official sources:** JTA total guest-nights 653.48mm ÷ room-nights (MHLW stock 1.44mm rooms × 365 × JTA occupancy 61.8% = 325mm) = **2.01 guests per occupied room**. That is a *blended* figure including business travel, so the leisure-only implication here (2.2–2.3) correctly sits above it.
2. **Industry "double occupancy factor":** ~1.2 business hotels, ~1.5 spa, **1.8–2.5 holiday hotels**. The vector's leisure implication sits mid-range of the holiday band — the right band, since business is added separately at 1 room/party.

Still not a U.S.-specific measurement (no U.S. source publishes guests per occupied room), but no longer uncited, and both checks say the level is right rather than convenient.

## CONTESTABLE = 0.38 — challenged, and the challenge should be carried

No newer substitution survey exists; F&F's 2014 figure is still the only direct estimate. But **Airbnb's own commissioned economists reach the opposite conclusion from the NYC event this model validates against**. Charles River Associates, *The Cost of STR Restrictions* (Dec-2024):

> "Limited substitution from STRs to hotels is supported by hotel occupancy data, which shows no material increase in NYC hotel occupancy rates following LL18."

They separately adjust lost-nights estimates down by **70% (NYC)** and 60–62% (Boston, New Orleans, Philadelphia) for substitution to alternative accommodation *generally* — so their view is that displaced guests did substitute, just not to hotels.

**The disagreement is entirely about whether NYC hotels were capacity-constrained.** At ~84% occupancy the EJPE 2025 reading — that the shift appeared in **price** (ADR +$14–19) rather than occupancy — is the more coherent one, and it is what this model reproduces. But the NYC validation is contested by a party with sight of Airbnb's own data, and **should not be presented as uncontested.**

## Brazil hotel side — still not found

IBGE's *Pesquisa de Serviços de Hospedagem* (SIDRA tables 3435, 6517, 6518) publishes **capacity only** — establishments, housing units, beds — for capitals and metropolitan regions. No guest-nights or occupancy series. The FOHB chain panel remains the only demand-side read (occupancy +2.1%, ADR +10.5% in FY25), and it is a 583-hotel urban-chain sample, not a census. **Brazil remains the largest unmeasured piece of the fastest-growing region.**

## Bottom-up fact-check of the top-down level (8 Sep 2026)

`analysis/src/bottom_up_nights_check.py` → `bottom_up_nights_check.csv`. The U.S. nights level rests on one unvalidated chain — disclosed NA total × a revenue-share proxy — so this tests it from the supply side using `nights = listings × 365 × availability × occupancy`.

**The trap worth naming first:** AirDNA's occupancy is booked ÷ **available** nights, not booked ÷ 365. A naive `2.25mm × 365 × 55%` gives **452mm U.S. nights — more than Airbnb's entire global total of 533mm**. The availability term does most of the work and nobody publishes it cleanly.

**Test 1 — what availability does the top-down number imply?**

2.25mm U.S. listings × 365 = 821mm listing-days. Top-down 138.4mm nights = **16.9% of all calendar days**.

| AirDNA occupancy | Implied availability | Nights offered/listing |
|---|---|---|
| 50% | 33.7% | 123 |
| 55% | 30.6% | 112 |
| 60% | 28.1% | 103 |

**Plausible.** A mix of professional hosts (near year-round) and casual hosts (a few weeks) lands exactly there. The level is not contradicted by the supply base.

**Test 2 — nights per listing** (needs no availability term, so it's the cleaner check):

| | Nights/listing/yr |
|---|---|
| Global @ 8.0mm listings | 66.6 |
| Global @ 9.5mm listings | 56.1 |
| **U.S. @ 2.25mm** | **61.5** |

Inside the range, but at the **low end** — and that is mildly uncomfortable, because U.S. supply skews whole-home and professional and should be *more* utilised than a global mix heavy in private rooms and casual hosts. Held the other way, 67–85 nights/listing would imply **1.63–2.07mm** U.S. listings rather than 2.25mm.

**Verdict: not contradicted, not confirmed.** Both tests place the top-down level inside a plausible band, but every input carries wide uncertainty (global listing counts vary 8.0–9.5mm by source; availability is unpublished). This is a sanity check that the level is not absurd, not a validation of the specific number. The residual tension in Test 2 leans **the same way the revenue reconciliation did** — if anything U.S. nights are high relative to the supply base, which is consistent with the `US_ADR_PREMIUM` correction already applied.

### Why this isn't the strong version, and what would be

Inside Airbnb calendars would give a genuinely independent build, but the repo's extract can't support it:

- A "booked run" there is a contiguous unavailable block **capped at 30 nights** to strip host blocks. That makes mean run length usable but total booked nights **systematically undercounted** — every run over 30 nights is dropped.
- The calendars are **365-day forward snapshots**, so far-dated months look empty simply because those bookings haven't happened yet.

Together these give ~**9.7% implied occupancy** across the eight cities against AirDNA's ~55% — about one eighth. The fix is to recompute from raw `calendar.csv.gz` using only a near window (0–30 days out, where booking is largely complete) with no 30-night cap, then correct for residual pickup. `data/raw` is gitignored and the gz files aren't on this machine, so that's a follow-up.
