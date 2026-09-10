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

## Simplified nights model — hotels out, RNPL and cancellations in (10 Sep 2026)

`analysis/src/nights_simple.py` → `nights_simple.csv`. **This replaces `choice_nights_driver.py` for forecasting.** The old model had ~15 inputs, most of them about hotels; this has three drivers, all disclosed or management-quantified.

### Why the hotel machinery came out

It didn't move the answer. At the team's near-parity ADR path, moving the switch rate 5.0 → 10.3 changed 2030 nights by **2.1%**. And the reconciliation work found that **neither the switch rate nor the contestable share could close the gap to the team's path at *any* value** — because with Airbnb ADR growing in line with hotels there's no relative-price signal for share to respond to.

The hotel comparison is a **good thesis point** (Airbnb takes 6% of solo lodging but 31% of 5+ parties, confirmed in four datasets). It is not a forecasting mechanism. Keeping it in the model meant carrying a contestable share, rooms per party, two leisure party mixes, a switch rate and a hotel room-night base — six assumptions earning nothing.

### The model

> **Nights(t) = Base(t) × (1 + L(t)) × (1 − C(t)) / (1 − C(0))**

| Driver | Value | Source |
|---|---|---|
| **Base** — underlying demand | **+7.5%/yr** | Disclosed nights growth *before* US RNPL: +7.92% (1Q25), +7.43% (2Q25). Observed, not fitted |
| **L(t)** — product bundle level uplift | 2.0% → 3.0%, then flat | Management sized it: ~2pts nights (4Q25 call), ~3pts (1Q26). Laps 3Q26 / 4Q26 / 1Q27 |
| **C(t)** — cancellation rate | 16.5% → 19.6% | Nights are reported **net of cancellations**. RNPL took the platform rate ~16% → ~17% |

Cancellations decompose exactly as you framed it: `C = (1−s)·c_base + s·c_rnpl`, with **RNPL share rising** *and* **the cohort's own cancel rate rising** (zero-due-at-booking selects progressively more marginal bookers as it scales). `c_base` is pinned at the pre-RNPL 16%, and `c_rnpl` is **derived** from the observed aggregate rather than assumed — at s=50%, a 17% aggregate implies 18%.

### Output

| Year | Underlying | Feature | Cancel | **Total** |
|---|---|---|---|---|
| 2026 | +7.50% | +0.98% | −0.60% | **+7.90%** |
| 2027 | +7.50% | **0.00%** | −0.90% | **+6.52%** |
| 2028 | +7.50% | 0.00% | −0.88% | +6.56% |
| 2030 | +7.50% | 0.00% | −0.65% | +6.80% |

**The whole model is one asymmetry: a one-off level gain against a permanent, compounding drag.** 2026 is the last year the bundle contributes anything; after the laps it adds exactly zero to the growth rate while the cancellation rate it created keeps climbing. Cumulative cancellation drag 2025→2030 is **−3.7% of nights**.

### ADR is now downstream

ADR = GBV ÷ nights, both dated at booking — it *follows* the mix of nights booked. RNPL's own disclosed channels are mix channels ("a slightly nicer listing", shift to 4+ bedroom homes), so the feature that lifts nights also lifts ADR. Management sized the same bundle at **~3pts of nights and ~4pts of GBV** — **the 1pt wedge is the ADR mix effect**, and it laps on the same schedule. ADR is reported as an output, never fed in.

### The only two assumptions left

| Scenario | 2030 cancel rate | 2030 nights | Cumulative drag |
|---|---|---|---|
| RNPL stalls at 50%, cohort flat | 17.0% | 768.1mm | −0.6% |
| **Base** | 19.6% | **744.3mm** | −3.7% |
| RNPL to 95%, cohort to 22% | 21.7% | 724.6mm | −6.2% |

Everything else is disclosed. **Versus 2026 at +7.9%:** Airbnb guides 3Q26 nights at 10–12% (mid 11%) and Krish has FY26 +9.9%, so this is still below both — but the disagreement is now about *one* thing (whether the bundle is worth more than 3pts) rather than about fifteen.
