# ADR line v2 — pre-registration: the sub-regional (country-level) geographic mix, from the Inside Airbnb panel

Date 2026-09-22, written before any mix term is computed or scored. Theo's direction: the pivotal change in
Airbnb's composition is growth shifting toward lower-ADR countries (India origin +50–60%, Brazil origin +21–31%,
Latin America ~+20%, expansion markets "roughly twice core"), which the four disclosed regional buckets cannot see
inside each region; the repo's annual decomposition already leaves a jointly unidentified "pricing + sub-regional
mix" term. This registration builds the sub-regional layer from the 123-market stays panel and market price levels,
tests whether it explains part of the like-for-like residual, and states in advance how it enters the line.
**DEC-0016 stands**: the term is measured and reported whichever way it lands; no weight or window is chosen after
seeing the 4Q26 ADR.

## 1. Objects

- **Stays by destination market and country**, vintage-matched y/y, 1Q22–3Q26 QTD: `stays_yoy_by_country.csv`,
  `stays_yoy_by_market.csv` (built before this file; same construction as the reviews index: latest dump vs the
  dump 300–430 days older, posting lag 2 months trimmed). 123 markets, 37 countries; coverage is biased (34 US,
  11 Australian, 10 Italian, 9 Spanish markets; no India; one market each in Thailand, Japan, Mexico, Turkey…).
- **USD price level by market**: the median quoted/listed nightly price of established listings (`M2_new_listing_
  premium.csv`, `median_old`, entire-home, first-review age field), converted at the quarter-average FRED rate of
  the market's currency (`fx_daily_2026-09-21.csv` + `fx_daily_extra_2026-09-22.csv`). Markets whose currency FRED
  does not carry (ARS, COP, CLP, TRY, HUF, CZK, KES) take their region's median USD level (stated imputation).
  Price levels are a **relative-level proxy** (asking/quoted prices, not booked ADR); the mix term needs relative
  levels only.
- **Within-region country mix**, per region r and quarter t:
  `mix_r(t) = [Σ_c s_c(t−4)(1+g_c(t)) P_c] / [(1+g_r(t)) Σ_c s_c(t−4) P_c] − 1`, shares s_c = the country's share of
  the region's panel stays in the base quarter, g_c = country stays y/y, g_r the panel-weighted region growth, P_c
  the USD price level. The **sub-regional geo term** = Σ_r w_r · mix_r(t), w_r the region's GBV share (10-K).
- The **four-region term** stays the disclosed-bucket arithmetic of `adr_v1_design.md` §3.3. The two layers add.

## 2. Hypotheses and pass lines (fixed now)

- **H1 (attribution).** The sub-regional term is negative on average over 1Q23–2Q26 (growth inside regions tilts to
  cheaper countries) and its magnitude is ≥ 0.25pp in absolute mean. Reported either way; no promotion hangs on it.
- **H2 (forecast content).** Define `core2(t) = residual(t) − bundle(t) − subgeo(t)`. Walk-forward, targets 1Q24–2Q26
  (W1, n 10) and 1Q25–2Q26 (W2, n 6): predict `residual(t)` as `core2(t−1) + bundle(t) + subgeo(t)` where
  `subgeo(t)` uses the **quarter-to-date** stays panel available before the print (E's partial-quarter files) — if
  that is not available for history, use `subgeo(t−1)` and say so. Compare with the residual carry (naive) and
  with `core(t−1) + bundle(t)` (the v1 construction). **Pass line**: RMSE ratio to the residual carry ≤ 0.75 on both
  windows. Pass → the sub-regional term enters the base and `core` is redefined as `core2`. Fail → the term is
  carried as a labelled attribution row (H1) and a forward scenario, not in the base.
- **H3 (forward).** Regardless of H2, the forward sub-regional term 3Q26–4Q27 is computed under a stated rule — each
  country's growth differential to its region carried at its 2H25–1H26 average, shares rolled — and shown as a
  scenario "sub-regional mix persists" beside the base, with its 4Q26 ADR.
- **Coverage check.** The panel's country shares are compared with the disclosed regional statements (India origin,
  Brazil origin, LatAm ~20%, APAC high-teens, expansion markets twice core). Where the panel has no destination
  (India), the term cannot see it and the design says so; origin-side effects inside a destination (an Indian
  traveller booking a cheaper listing in Bangkok) are outside this object's reach and are not claimed.

## 3. What will not be done

No price source or FX vintage chosen after results; no country dropped for its sign; no scenario selected by its
4Q26 ADR; nothing under the frozen lanes written. Everything above §4 is fixed before the first score.

## 4. Results (filed after the run)

Filed 2026-09-22 after the run. Inputs as registered, with two source amendments made **before** any score:
(i) market price levels come from the capture store's June 2026 listings files for all 120 markets (entire-home,
reviewed in the last twelve months, median listed price; the M2 medians cover only 34), (ii) CZK, HUF and TRY
rates from the ECB reference series and the Belize peg, so only Argentina, Chile, Colombia, Kenya and Malta (plus
Switzerland, whose files carry zero prices) are imputed at their region's median — 2% of EMEA panel stays, 38% of
LatAm, 30% of APAC (New Zealand). Files: `country_price_levels_usd.csv`, `geomix_within_region.csv`,
`geomix_country_contributions.csv`, `geomix_subregional_term.csv`, `geomix_h2_scores.csv`,
`geomix_*_forward.csv`, `geo_mix_tilt_sensitivity.csv`.

**H1 (attribution): passes as a historical fact, but the term is fading.** Sub-regional mix, GBV-weighted:
1Q23–2Q26 mean **−0.45pp** (≥ 0.25 line met); 1Q24–2Q26 −0.30; 3Q25–2Q26 **−0.15**; 1Q26 −0.26, 2Q26 −0.10.
Within-region: APAC −9.2 → −0.8pp (2023 was Thailand/Taiwan/Japan reopening against an Australia-heavy panel; 2026
is Australia at +0.7% vs Singapore/Thailand/Taiwan at +4–14%); NAM −0.4 to −0.8 in 2023–24, −0.5 in 2Q26 (Canada
+16% at 0.70 of US price); EMEA oscillates around zero and is **+0.43 in 2Q26** (UK +7.7% at 1.46× the regional
price, Italy +4%, France −3%, Portugal −3%); LatAm ±1 (Brazil +15% at 0.70× vs Mexico/Argentina +24–25% at 1.11×).
**Consequence for the core:** net of the sub-regional term, `core2` runs 4.41 / 3.54 / 1.63 / 1.50 / 2.73 / 3.55 /
2.25 / 3.26 / 2.61 / 2.45 / 2.57 / 2.69 / 3.63 / **3.95** — the 2026 step in like-for-like price is *smaller* once
the fading mix drag is removed (3.95 vs a 2023–25 core2 mean of 2.77, a 1.2pp step, against 1.45pp on `core`).
The sub-regional data therefore explain part of the 2026 acceleration as a mix headwind that went away; they do
not support a larger forward drag.

**H2 (forecast content): FAIL.** With the sub-regional term only knowable one quarter late for history, the v2
prediction is arithmetically identical to v1 (ratios 0.91 W1 / 0.72 W2 vs the residual carry; W1 above 0.75).
Not promoted; the term enters as an attribution row and a forward scenario.

**H3 (forward):** with each country's growth differential to its region carried at its 2H25–1H26 average and shares
rolled, the sub-regional term is **−0.13 (3Q26) → −0.18pp (4Q27)**, almost all of it Canada outgrowing the United
States at 0.70× its price. Adding it to the base moves 4Q26 ADR by **−$0.24** ($173.03 → $172.79).

**What the panel cannot see, stated:** it has no Indian, Emirati, Malaysian, Indonesian or Vietnamese market and one
each in Thailand and Singapore, so the destination side of the India-origin story (+50/+50/+60% y/y in 4Q25–2Q26,
letters) is invisible to it; Australia is 57% of the panel's APAC stays but a much smaller share of Airbnb's APAC
nights, so the APAC within-region term is Australia-vs-the-rest. Origin-side composition inside a destination (a
cheaper listing booked by a cross-border guest) is outside this object entirely. Those channels live, if anywhere,
in the four-region term through the disclosed LatAm/APAC buckets — see the tilt sensitivity in `adr_v1_design.md`.

**Origin proxy, descriptive (added after the inventory `dossiers/ADR_D_origin_destination_inventory.md`):** the only
Airbnb-side origin object in the git is reviewer language (`abnb_party_size_reviews_v2_language_year_shard*.csv`, 8
buckets, annual, latest dump per market; `origin_proxy_review_language_by_region_year.csv`, figure
`adr_origin_language_shares`). Across the 123 markets, English fell from **71% of reviews in 2022 to 58% in 2026**
(to the June dumps); Spanish 11 → 16%, "other" 7 → 10%, Portuguese 1.8 → 3.5%, Chinese/Japanese/Korean 1.1 → 2.8%.
2025 review growth: Portuguese +45%, other +39%, Spanish +37%, East-Asian +30%, **English +17%**. By destination:
EMEA English 63 → 50% (other 8 → 13%, German 5 → 7%), APAC East-Asian 5 → 10%, LatAm Spanish 42 → 48% with English
24 → 15%, North America English 93 → 89%. This is the composition change Theo describes, measured on Airbnb's own
guests, and it is the direction the tilt-B scenario assumes. What it does **not** give is a price: an origin group's
spend per night inside a destination is not observed (Indian guests write in English and are invisible here), so
the exhibit corroborates the four-region tilt and does not enter the term. Coverage caveat: all years from the
latest dump, so absolute growth rates carry delisting attrition; the *shares* within a year do not.
