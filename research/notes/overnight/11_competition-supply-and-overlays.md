# Workstream 11: competitive position, supply economics, and the AI and regulatory overlays

**What this is:** the competitive and overlay layer for the driver model. Four questions: is Airbnb gaining or losing share of alternative accommodation; is supply a constraint or an excess; does AI/agentic travel threaten the take rate; and how much do regulation and the new businesses move FY26-28 revenue.

**Compiled:** 2026-09-06. Author: Claude Code for Krishang. Price context: $181.94 (4 Sep 2026 close).
**Script:** `analysis/src/overnight/11_competition_supply_overlays.py` (run `py -3.13 analysis/src/overnight/11_competition_supply_overlays.py` from the repo root).
**Outputs:** `data/processed/overnight/11_alt_accom_share.csv`, `11_alt_accom_share_quarterly.csv`, `11_alt_accom_market_sizing.csv`, `11_supply_economics.csv`, `11_competitor_events.csv` (39 dated events), `11_regulatory_overlay.csv`, `11_regulatory_pending_items.csv`, `11_new_business_scenarios.csv`, `11_ai_exposure_scenarios.csv`; figure `analysis/figures/overnight/11_alt_accom_growth.png`.
**Depends on:** `abnb_quarterly_kpis_from_study.csv`, `inside_airbnb_like_for_like.csv`, `inside_airbnb_city_snapshots.csv`, `cc_listing_survival.csv`, `abnb_regulatory_profile.csv`, `abnb_regulatory_contributions.csv`, `predictive/02_peer_prints.csv`, plus hand-entered disclosures with a source on every row.

---

## 1. Bottom line

1. **Airbnb lost share to Booking.com for three straight years and took it back in 1H26.** Airbnb's share of the two-player alternative-accommodation nights pool fell from 59.4% (2022) to 54.5% (2025) as Booking.com's alt-accom room nights compounded faster. That reversed this year: Booking.com's alt-accom room nights grew +5.5% in Q1'26 and **+4% in Q2'26** against Airbnb's +9.2% and +10.3%. This is the single most useful competitive fact in the workstream, and it is the first time since 2022 that Airbnb has out-grown Booking in the category Booking chose to attack.

2. **Supply is not the constraint and is not in excess — it tracks demand almost exactly.** Nights per average active listing has been **62.5, 62.7, 62.6, 62.7** in 2022, 2023, 2024, 2025. Four years of listings growth exactly absorbing nights growth. Management's own language moved from "supply-constrained top markets" (Q2'25) to "strength in both supply-constrained markets and in non-supply-constrained markets" (Q2'26). Supply is a co-moving input, not an independent lever; do not model it as one.

3. **Host churn is high and rising, but it is churn out of the tail, not out of the business.** Inside Airbnb year-ago retention across seven cities with a clean 2025 and 2026 read fell from **75.4% to 71.1%**, with new listings replacing them at a steady 25-26% of the ending base. Common Crawl re-fetch survival is flatter (90% in 2022, 85-88% since). Roughly a quarter of listings turn over every year and always have; the platform grows because gross adds exceed exits, and matched-listing review volumes are still rising (+4 to +13% y/y in 2026 in every city except Austin, roughly flat, and Paris, +1%).

4. **AI disintermediation is a 2028+ problem sized at 1-2% of revenue, not a 2026-27 one.** Booking disclosed that AI tools drove **<1% of room nights** in Q2'26. The Third Bridge AI expert (T2, Booking.com ML/AI PM, 14 Aug 2026) puts ~3% of accommodation bookings moving to AI-native transactions in 12-24 months with **no EBITDA impact** in that window. My scenario grid: at a mid case (5% of GBV arriving via a paid AI referral in 2028) and a 5%-of-booking-value referral fee, the cost is **$329m, 1.9% of revenue, 5.3% of Adj. EBITDA**. Airbnb's ~90% direct/unpaid mix and 64%-of-nights app share are both the defence and the exposure: it has more to lose than Booking because it has more free traffic.

5. **Regulation is a ~0.15% revenue drag in 2026 rising to ~0.87% in 2028 at the median, and it is 93% European.** In nights terms that is roughly **-1.1% on EMEA nights in 2027 and -2.1% in 2028**, versus -0.08% and -0.15% on North America. The tail is what matters: the 95th percentile is 2.7% of revenue in 2027 and 4.0% in 2028, and 68% of the variance is two EU items (EU-AHA and the EU tail).

6. **The new businesses are real but small through FY28.** Hotels, Experiences, Services and a hypothetical ads product together move from ~$392m FY25 revenue to **$717m bear / $1,426m base / $2,511m bull** in FY28. Netting out what would have grown anyway with the platform, the genuinely incremental FY28 contribution is **$235m / $914m / $1,987m** — i.e. **1.4% / 5.4% / 11.7%** on a ~$17bn FY28 base. Management's "easily $1 billion revenue opportunity" (Feb 2025) is a base-case FY27-28 statement, not a FY26 one.

7. **The take rate has an asymmetric risk this cycle and it is not the one the sell side is watching.** The single 15.5% host-only fee is now on ~50% of listings and reaches all of them by end-2026, which is the positive. The offset announced 29 Aug 2026 is a pilot cutting the host fee to **6-10%** on bookings arriving through a host's own direct link. That is Airbnb pricing its own disintermediation risk, and it caps the fee-migration tailwind that the driver model's bull case relies on.

---

## 2. Share of alternative accommodation

### 2.1 The two-player pool (nights)

| Year | Airbnb nights (m) | Airbnb y/y | BKNG total room nights (m) | BKNG alt-accom mix | BKNG alt-accom nights (m) | Airbnb share of the two |
|---|---|---|---|---|---|---|
| 2019 | 326.9 | | 845 | | | |
| 2022 | 393.7 | +31.0% | 896 | 30% | 269 | **59.4%** |
| 2023 | 448.2 | +13.8% | 1,049 | 33% | 346 | **56.4%** |
| 2024 | 491.5 | +9.7% | 1,143 | 35% | 400 | **55.1%** |
| 2025 | 533.0 | +8.4% | 1,235 | 36% | 445 | **54.5%** |
| 1H26 | 304.5 | +9.7% | | ~37.5% | | (Booking alt-accom +5.5% Q1, +4% Q2) |

Sources: Airbnb nights from `data/processed/abnb_quarterly_kpis_from_study.csv` (shareholder letters); 2019 from the S-1. Booking total room nights from the FY2019/22/23 10-Ks and the Q4'24 (+9%, "1.1 billion") and Q4'25 ("over 1.2 billion", +8%) releases, with 2024-25 levels derived from the growth rates. Alt-accom mix from the [BKNG FY2025 10-K](https://www.sec.gov/Archives/edgar/data/1075531/000107553126000009/bkng-20251231.htm) ("approximately 36%" 2025 vs "approximately 35%" 2024) and from the calls for earlier years. Full row-level sourcing in `11_alt_accom_share.csv`.

**Caveat:** Booking's alt-accom mix is disclosed as a rounded approximation and its quarterly prints bounce between 33% and 38% (mix is seasonal — European summer is alt-accom heavy). The annual mixes above are the FY figures management cites. The share level is therefore ±1-2 pts; the *trend* is robust.

### 2.2 Quarterly, where Booking disclosed alt-accom growth

| Quarter | BKNG alt-accom nights y/y | BKNG total room nights y/y | Airbnb nights y/y | EXPE room nights y/y | BKNG alt-accom listings (m) |
|---|---|---|---|---|---|
| 3Q24 | +14% | +8% | +8.5% | +9.1% | |
| 4Q24 | +19% | +13% | +12.3% | +11.6% | 7.9 (+8%) |
| 2Q25 | +10% | +8% | +7.4% | +6.7% | 8.4 (+8%) |
| 3Q25 | +10% | +8% | +8.8% | +11.1% | 8.6 (+10%) |
| 1Q26 | +5.5% | +6% | +9.2% | +5.8% | 8.8 (+9%) |
| 2Q26 | **+4%** | +5% | **+10.3%** | +5.7% | 9.1 (+8%) |

Sources: `11_alt_accom_share_quarterly.csv`; BKNG/EXPE totals from `data/processed/predictive/02_peer_prints.csv`; alt-accom lines from the BKNG calls via [RentalScaleUp](https://www.rentalscaleup.com/booking-com-q2-2026-earnings/) and the [Q2'26 8-K](https://www.sec.gov/Archives/edgar/data/0001075531/000107553126000036/q2-26bkngearningsrelease.htm). Figure: `analysis/figures/overnight/11_alt_accom_growth.png`.

**Read.** Booking's alt-accom growth premium over its own total room nights was +6 pts in 3Q24 and is now **-1 pt** in 2Q26. Its listing count still grows +8%, so the deceleration is demand per listing, not supply. Booking's own CEO said in Q2'26 that he wants US alt-accom share "a lot higher" — Booking's weakness is the US, which is Airbnb's strength.

### 2.3 The market, and the share-cap arithmetic

| Period | Source | Metric | Value |
|---|---|---|---|
| 2019 | Skift Research | Airbnb / Booking.com / Vrbo share of global STR revenue | 28% / 14% / 11% |
| 2024 | Skift Research | Airbnb / Booking.com / Vrbo share of global STR revenue | **44% / 18% / 9%** (big-3 = 71%) |
| 2024 | Skift Research | Global STR revenue | $183bn |
| 2025 | Phocuswright (Aug 2026) | Global STR gross bookings | $219.9bn |
| 2029 | Phocuswright (Aug 2026) | Global STR gross bookings forecast (5.3% CAGR) | $270.6bn |
| 2025 | Phocuswright | North America STR gross bookings | $78.0bn (+4%); 2026E $81.8bn (+5%) |
| 2026 | AirDNA (Jul 2026) | US STR demand growth forecast | +2.7% |
| 2026 | Vrbo | bookable listings | "over 2 million" |
| 2025 | Marriott | Homes & Villas by Marriott Bonvoy | 180,000+ homes |

Sources in `11_alt_accom_market_sizing.csv`: [Skift](https://skift.com/2025/03/14/short-term-rentals-airbnbs-dominance-and-bookings-gains-in-1-chart/), [Phocuswright Aug 2026](https://www.phocuswright.com/Travel-Research/Research-Updates/2026/shortterm-rentals-enter-a-new-phase-of-scrutiny-and-structural-growth), [AirDNA midyear](https://www.prnewswire.com/news-releases/steady-demand-and-slower-new-supply-define-us-short-term-rentals-in-2026-airdna-finds-302820776.html).

Airbnb's FY25 GBV of $91.3bn is **41.5%** of Phocuswright's $219.9bn 2025 pool. Running the driver-model scenarios forward (nights growth from `model/assumptions.md`, ADR growth backed out from the scenario revenue growth at the scenario take rate) against Phocuswright's 5.3% market CAGR:

| Implied Airbnb share of global STR gross bookings | 2026 | 2027 | 2028 | 2029 |
|---|---|---|---|---|
| Bear | 45.3% | 45.2% | 44.6% | 43.6% |
| Base | 45.8% | 48.8% | **51.5%** | **53.9%** |
| Bull | 46.2% | 50.2% | 54.0% | **57.6%** |

**This is the share cap for the model.** The base case requires Airbnb to add ~2.5 pts of global STR share every year for four years. It did add ~3.2 pts a year from 2019 to 2024 on Skift's revenue basis, so it is not unprecedented — but that was the post-COVID platform-consolidation window with the long tail of independent and regional players collapsing onto the big three. The base case is only reachable if either (a) Phocuswright's 5.3% is too low, or (b) platform penetration of the un-intermediated long tail keeps running. **The bull case (57.6% by 2029) I would not underwrite.**

**Honest tension worth stating in the pitch.** Airbnb is *gaining* share of the total STR market on Skift's series while *losing* share to Booking.com on the two-player nights series (section 2.1). Both can be true: the long tail is consolidating onto platforms faster than Booking is taking share from Airbnb. But the two series answer different questions, and an analyst who quotes the Skift 44% without the Booking comparison is telling half the story.

### 2.4 Professional-manager channel mix (Third Bridge, paraphrased)

The five licensed expert calls in `data/raw/licensed/third-bridge/` are summarised in `research/notes/2026-09-05_third-bridge-transcripts.md`; paraphrases only below (do not quote at length; see the compliance note in that file).

- **US (T5, MD of a full-service US STR manager, 2 Jun 2026):** ~2m professionally managed US rentals across ~20,000 firms averaging ~100 units; all PE roll-ups combined are only ~10% share. Managers allocate inventory across Airbnb, Vrbo and Booking and are not exclusive to any. Owner retention 80-85% a year. Paid placement and rebates already exist on the host side.
- **Europe (T4, 26 May 2026):** ~18m second homes, ~3m let out, ~1m urban; manager portfolios flat; owner churn ~15% a year; non-exclusive listings are **double-counted across platforms**, which is a direct caution against comparing Airbnb's 9m listings to Booking's 9.1m alt-accom listings as if they were disjoint. Awaze pays Airbnb "15-16%" (later "16-17%") and treats it as one channel among Vrbo, HomeToGo, Google and its own site. The expert rates the risk of owners forcing commissions down as low: "Airbnb and the rest have set a plateau."
- **India (T3):** Airbnb is moving standalone hosts from a lower commission plus guest fee to the higher host-only commission, which pushes supply toward aggregators.

**Implication:** the ~9m listing counts on both sides overlap materially. Nights, not listings, is the only clean share metric — which is why section 2.1 is built on nights.

---

## 3. Supply economics: constraint or excess?

### 3.1 The listings history and the occupancy identity

| Year end | Active listings | Listings y/y | Nights (m) | Nights y/y | **Nights per average listing** |
|---|---|---|---|---|---|
| 2020 | 5.6m | | | | |
| 2021 | 6.0m | +7% | 300.6 | | 51.8 |
| 2022 | 6.6m ex-China | +10% | 393.7 | +31% | **62.5** |
| 2023 | 7.7m | +17% | 448.2 | +14% | **62.7** |
| 2024 | 8.0m | +4%* | 491.5 | +10% | **62.6** |
| 2025 | 9.0m | +12%* | 533.0 | +8% | **62.7** |

*Levels are as disclosed ("over 8 million", "over 9 million"), so the 2024 and 2025 growth rates are rounding artefacts of each other; the true path is smoother. Sources: 10-K FY2020; 4Q21, 4Q22, 2Q23, 4Q23, 4Q24, 4Q25 shareholder letters; 2Q24 call. Rows in `11_supply_economics.csv`.

**Four years at 62.5-62.7 nights per average active listing.** Whatever demand does, supply follows within a year. This is the cleanest single answer to "is supply the constraint": it is neither a constraint nor an excess — it is endogenous. Management says the same thing in three different ways across three years: occupancy is "pretty stable ... on a global basis" (Q3'23); "global occupancy on Airbnb is so much lower than hotels ... not even close to high occupancy" (Q1'24); and in Q1'26 the strategy is explicitly "concentrating our acquisition efforts on the markets and geographies where underlying demand exists ... encouraging existing hosts to open up more of their calendar," i.e. deliberately not chasing listing count.

**What this means for the model:** do not add a separate supply variable. If you want a supply-driven upside case, it has to work through mix (Superhost/Guest Favorite nights growing faster than the base: +15% Q1'25, +12% Q2'25; Superhost-managed listings +26% in Q2'24) or through calendar availability, not through listing count.

### 3.2 Hosts, host earnings, and the Co-Host Network

| Date | Metric | Value | Source |
|---|---|---|---|
| Mar 2021 | Hosts | 4.0m | 1Q21 letter |
| Dec 2023 | Hosts | 5.0m | 4Q23 letter |
| May 2026 | Hosts | 5.5m | [2026 Summer Release](https://news.airbnb.com/airbnb-2026-summer-release) |
| 2023 | Host earnings | >$57bn (78% of $73.3bn GBV) | 4Q23 letter and call |
| 2025 | Host earnings (derived) | ~$71bn (78% of $91.3bn GBV) | not disclosed since 2023; my estimate |
| Q1'23 | Individual (non-professional) host share | ~90% of hosts | 1Q23 letter |
| Oct 2024 | Co-Host Network launch | 10,000 co-hosts, 10 countries | 3Q24 letter |
| Feb 2025 | Co-Host Network | ~100,000 listings in 4 months; 15,000 co-hosts | 4Q24 letter and call |
| Aug 2025 | Co-Host Network | >100,000 listings, >10m nights booked | 2Q25 letter |
| Jun 2025 | Listings removed since 2023 quality push | >500,000 | 2Q25 letter |
| Aug 2026 | World Cup first-time-host listings | >150,000 | 2Q26 letter |

**Airbnb stopped disclosing host earnings after 2023.** That is the single most conspicuous disclosure gap in the supply story and it coincides with the take-rate migration. Ask about it on 5 Nov.

**Co-Host Network earns Airbnb nothing directly** — management confirmed on the Q1'25 call that there is no incremental take rate on co-hosted listings. Its value is supply quality: co-hosted new listings earn roughly 2x comparable listings. Model it as zero revenue and a small positive on nights per new listing.

### 3.3 Host churn: Inside Airbnb and Common Crawl

Year-ago matched-listing retention, partial-scope dumps excluded (Inside Airbnb changed the geographic scope of several 2026 monthlies; including them halves the apparent retention — the 25 dropped pairs average 0.489 against 0.726 for the 78 kept, so this exclusion is not cosmetic):

| City | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| Austin | | | 0.745 | **0.509** |
| Barcelona | | | | 0.630 |
| Chicago | | | 0.759 | 0.739 |
| London | | | | 0.710 |
| Los Angeles | | | 0.762 | 0.693 |
| Mexico City | | | | 0.737 |
| Nashville | | | 0.771 | 0.740 |
| New Orleans | | | | 0.733 |
| New York City | | | | 0.699 |
| Paris | | | 0.714 | 0.755 |
| Rome | 0.816 | 0.803 | 0.765 | 0.796 |
| San Diego | | | 0.794 | 0.716 |
| Sydney | | | | 0.753 |

On the seven cities with a clean read in both years, mean retention fell **75.4% → 71.1%**, with the new-listing share of the ending base steady at 25.4% → 25.8%. Source: `inside_airbnb_like_for_like.csv` filtered on `pair_type=year_ago`, partial-scope flag from `inside_airbnb_city_snapshots.csv`.

**Austin is a genuine outlier, not an artefact.** Both endpoints of every Austin 2026 pair are full-scope dumps. Austin listings fell from 15,187 (Jun 2025) to 11,295 (Jun 2026), -26%, while the reviewed-in-LTM share rose from 0.60 to 0.73 — the profile of an inactive-listing purge or enforcement, not a geographic scope change. Worth a sentence in the pitch as evidence that the 500,000-listing quality removal programme is visible in the data.

Common Crawl re-fetch survival (informative crawls only, `cc_listing_survival.csv`):

| Year | Re-fetched | Removed | Survival |
|---|---|---|---|
| 2022 | 75,888 | 5,277 | 90.1% |
| 2023 | 63,903 | 9,125 | 84.8% |
| 2024 | 99,992 | 13,845 | 85.6% |
| 2025 | 91,496 | 10,973 | 87.6% |
| 2026 | 81,046 | 9,721 | 87.7% |

Two independent panels, two different answers on level (Inside Airbnb ~71-75% annual retention, Common Crawl ~86-88% per-crawl survival — different windows and different universes), but the same answer on direction: **churn stepped up in 2023 and has been stable since**. Nothing in either panel signals a supply cliff.

### 3.4 US STR industry conditions, 2024-26

| Date | Source | Reading |
|---|---|---|
| 2022-24 | AirDNA | US new-listing growth +22.1% (2022), +14.4% (2023), **+6.8% (2024)** — three years of deceleration |
| Dec 2025 | AirDNA 2026 outlook | listings +4.6%, ADR +1.5%, occupancy -1%; STR-over-hotel price premium highest since 2022 |
| Jul 2026 | AirDNA midyear | demand +2.7%, listings +2.7%, occupancy 57.4%, ADR ~+3%, RevPAR +2.9%; new-listing growth cut from 4.6% to 2.7% on mortgage rates >6%; **international inbound STR demand -12% vs spring 2025, Canada -32%** |
| Jun 2026 | Key Data (July 4 week) | professionally managed US STRs: occupancy +6.5%, ADR +5.5%, RevPAR +12.4%; 22 of 25 markets positive |
| Jul 2026 | Key Data (Q2'26) | RevPAR +2.1% to $119.27; occupancy **-1.5% to 48.4%** — "rate, not demand, is driving growth" |
| Apr 2025 | AirDNA via a bear pitch | US host occupancy 57% (2024) → 50% (spring 2025) on 1.76m listings |

Sources in `11_supply_economics.csv`. **Read:** the US STR industry is supply-disciplined for the first time since 2021 (mortgage rates are keeping new hosts out) and rate-led, with occupancy flat to slightly down. That is a *supportive* backdrop for Airbnb's US ADR but not for US nights, and it is consistent with Airbnb's Q2'26 North America nights growing only high-single-digit. The -12% international inbound reading is the specific US risk for 2H26.

---

## 4. Competitor and AI moves, dated

Thirty-nine dated events in `data/processed/overnight/11_competitor_events.csv`. The ones that matter:

**Booking Holdings.** AI Trip Planner launched Jun 2023. Alt-accom listings 7.9m → 9.1m over six quarters at a steady +8-10%, while alt-accom nights growth collapsed from +19% (4Q24) to +4% (2Q26). Connected trip: FY25 flights +37%, attractions +80%, multi-component travellers +20%; but Q2'26 connected-trip transactions are only "low double digits" of the total and the T1 expert says ~50% is "10 years best case." Genius L2/L3 members drive high-50s to low-60s % of room nights (T1) — the loyalty asset Airbnb does not have. Host-only ("no commission from guest") is Booking's structure in most of Europe, which is what Airbnb has been migrating toward with the single 15.5% fee.

**Expedia / Vrbo.** One Key earn rates on Vrbo cut in May 2025 (Blue earns nothing). Q2'26: room nights +6%, B2C bookings +8% and the fastest US growth in 15 quarters; **supplier-funded promotions are >40% of Vrbo bookings** and the May sale exceeded $1bn — Vrbo is buying volume with host money. "Answer engine optimisation" is Expedia's fastest-growing channel and it is testing ChatGPT and Claude channels. On 2 Sep 2026 Vrbo began auto-enrolling hosts in "Members Only Deals" (automatic discounts) with a 10 Sep opt-out deadline. Vrbo's global STR revenue share fell 11% (2019) → 9% (2024) on Skift's numbers; it is not the competitive threat.

**Google.** Vacation Rentals price display (Nov 2023) — Airbnb declined to respond and separately chose not to join Google Hotel Finder (Q3'25 call). Agentic hotel booking confirmed in testing 7 Aug 2026 and rolled into AI Mode on **27 Aug 2026** with Booking.com, Expedia, Hotels.com, Priceline, Trip.com, Marriott, Hilton, IHG, Wyndham and Choice as launch partners. **Airbnb is not a partner.** The hotel or OTA stays merchant of record, so this is lead-gen, not disintermediation — but it is the first agentic channel at scale and Airbnb is outside it by choice.

**AI agents.** OpenAI Operator (Jan 2025) launched with Booking.com, Priceline, Tripadvisor; shut 31 Aug 2025. ChatGPT Apps (Oct 2025) launched with Expedia and Booking.com; Airbnb absent. Chesky's position has moved: 2023 "we were supposed to be a launch partner, we declined"; Aug 2025 "open to it, chatbots are not the new Google, yet"; Oct 2025 ChatGPT apps are "not quite robust enough"; Nov 2025 and Feb 2026 "**ChatGPT traffic converts higher than Google traffic**" and AI companies are "top-of-funnel traffic generators ... just like Google was." Chesky is also founding an independent AI lab (Jun 2026) while remaining CEO, and told an Aug 2026 interviewer that AI-native search is coming to Airbnb within a year. Perplexity added hotel booking via Selfbook/Tripadvisor in Mar 2025.

**Hotels as the counter-attack.** Airbnb has been building the hotel channel since HotelTonight (2019). Q4'25: direct partnerships with boutique hotels in NYC, LA, Madrid, SF; >100 NYC hotels / 20,000 rooms. Q1'26: hotels growing >2x the platform, ~55% of hotel bookers go on to book a home. Q2'26: hotel nights ~3x homes growth, thousands of hotels in 20+ destinations, a 15% Airbnb credit running to 31 Dec 2026 plus a price-match guarantee, and 35% of first-time hotel guests book a home within a year. Lark Hotels (75+ boutique properties) added Aug 2026. Two senior hires from Booking.com in four months: Andrea D'Amico (VP Hotels, May 2026) and **Pepijn Rijvers as Chief Business Officer over Homes, Hotels and Global Markets (1 Sep 2026)**. Meanwhile Hilton announced Apartment Collection (Dec 2025) and Marriott's Homes & Villas is 180,000 homes — the hotels are coming the other way, but at 1/50th of Airbnb's scale.

### 4.1 Quantified disintermediation exposure

Anchors: Airbnb's traffic is ~90% direct or unpaid (Chesky, Q1'23 call) and the app is **64% of nights** (Q2'26). Booking's B2C direct is mid-60s% (Q2'26) and AI tools were **<1% of room nights**. The T2 expert's estimate is ~3% of accommodation bookings moving AI-native in 12-24 months, no EBITDA impact, and the specific Airbnb exposure is that its huge direct traffic is the thing an LLM front-end would intercept.

Cost if a share of GBV arrives via a paid AI referral instead of direct (referral fee at 5% of booking value; grid over 3%, 5% and 8% in `11_ai_exposure_scenarios.csv`):

| Year | Share of GBV via paid AI referral | Cost ($m) | % of revenue | % of Adj. EBITDA |
|---|---|---|---|---|
| 2026 | 0.5% / 1% / 2% | 26 / 52 / 105 | 0.19 / 0.38 / 0.75 | 0.5 / 1.0 / 2.1 |
| 2027 | 1% / 3% / 6% | 59 / 176 / 353 | 0.38 / 1.14 / 2.28 | 1.1 / 3.2 / 6.3 |
| 2028 | 2% / 5% / 10% | 132 / 329 / 659 | 0.77 / 1.92 / 3.83 | 2.1 / 5.3 / **10.6** |

GBV base $105bn FY26 growing 12%; revenue base $13.96bn FY26 growing 11%; 36% Adj. EBITDA margin. **The bear framing that survives scrutiny is not "AI kills Airbnb" — it is "AI turns 5-10% of Airbnb's free traffic into paid traffic by 2028, worth 5-11% of EBITDA."** That is a multiple story, not an earnings story, and it is the honest way to carry the risk.

**Airbnb's own hedge is priced.** The 29 Aug 2026 pilot cutting the host fee to 6-10% on host-originated direct links is Airbnb explicitly accepting a lower take rate to keep a booking on-platform. It tells you what management thinks a leaked booking is worth: about 5-9 pts of take rate.

---

## 5. Regulatory overlay

Built from the Monte Carlo in `data/processed/abnb_regulatory_profile.csv` and the per-event expected losses in `abnb_regulatory_contributions.csv` (see `research/notes/2026-09-05_regulatory-forecast-profile.md`). The profile gives end-2027 and end-2030 run-rates; I interpolate 2026 as one third of the 2027 run-rate (the items already in force — Paris co-property rule, Greek freezes, partial Spanish regional removals) and 2028 linearly toward 2030. Nights drag assumes the loss is volume, not price, and is grossed up by the regional revenue share (NA 42%, EMEA 39%, per the pitch landscape).

| Year | Revenue drag, median | mean | p95 | Europe share of the drag | **EMEA nights drag (median)** | **NA nights drag (median)** | **Global nights drag (median)** |
|---|---|---|---|---|---|---|---|
| 2026 | 0.15% | 0.25% | 0.92% | 93% | **-0.36%** | -0.03% | **-0.15%** |
| 2027 | 0.45% | 0.75% | 2.74% | 93% | **-1.07%** | -0.08% | **-0.45%** |
| 2028 | 0.87% | 1.23% | 3.96% | 93% | **-2.07%** | -0.15% | **-0.87%** |

Output: `11_regulatory_overlay.csv`. The mean exceeds the median by 60-70% because the distribution is right-skewed: P(revenue loss >1%) is 19.5% by 2027 and 70.7% by 2030. Two events carry 68% of the 2027 variance — EU-AHA (p=12% by 2027, 1.53% loss if in force) and the EU tail (p=2%, 3.81% loss).

**Use the mean, not the median, in the base case.** The median understates a right-skewed distribution and a diversified book should carry the expectation.

### 5.1 Top pending items before December 2026

| Date | Item | Region | What it does | Model link | Status, 6 Sep 2026 |
|---|---|---|---|---|---|
| **9 Sep 2026** | EU Affordable Housing Act proposal presented (Ribera) | EMEA | Enabling framework: authorities may restrict STRs in housing-stress areas on a price-to-income test; quantitative limits or grandfathering; primary residences exempt. Must pass Council and Parliament (EU median ~18 months) | **EU-AHA, p(2030)=45%, 1.54% loss if in force.** Move to 60% if binding caps or primary residences are included | Draft leaked 4 Sep matches the "proportionate enabling" reading. No probability change |
| Sep-Oct 2026 | NYC OSE FY26 registration report and October renewals; Int 879-2026 (owner-occupied 1-2 family loosening) | NA | **Upside only:** 20% chance of loosening by 2027 | NYC-LOOSEN, -0.14% i.e. a gain | No hearing scheduled as of 31 Aug 2026 |
| 2H 2026, undated | Spain's replacement for the annulled national registry (Supreme Court voided RD 1312/2024 on 19 May 2026; regional registers and platform data-sharing survive) | EMEA | A replacement with platform verification re-enables mass removals | ES-REMOVE, p=35% by 2027, 0.25% loss | No replacement text found as of 6 Sep |
| 1 Dec 2026 | Ireland STR register launch | EMEA | Planning-compliance enforcement could remove >20% of Irish listings within a year | IE-REG, p=35%, 0.09% | Launch date has already slipped once |
| 31 Dec 2026 | Greek ministerial decision on extending the Athens/Thessaloniki registration freezes into 2027 | EMEA | Attrition via the transfer rule | GR-FREEZE, p=70%, 0.06% | Undecided |

Beyond 2026: the May 2027 Barcelona municipal election ahead of the Nov 2028 licence lapse (10,101 licences, BCN-2028, p=45%, 0.24% at 2030) and the 1 Jan 2029 Maui West Maui phase-out (MAUI, p=40%, 0.08% at 2030). Full table with sources in `11_regulatory_pending_items.csv`.

### 5.2 News since 5 September 2026

A Google News sweep on 6 Sep of "Airbnb regulation" over the trailing week returned nothing that changes a probability. The material item is the **4 Sep leak of the EU draft** (Reuters, "Proposed EU rules would curb Airbnb, short-term rental homes, draft shows"; [Skift](https://skift.com/2026/09/04/european-commission-short-term-rental-crackdown/); Euractiv), which is already modelled as EU-AHA and whose "enabling, primary residences exempt" shape is the benign reading. The rest is routine US municipal activity that sits inside the US-CITY bucket (p=30% by 2027, 0.22% loss if it occurs): Hillsborough County FL rules into law (2-3 Sep), Richardson TX distance and fee rules effective 4 Sep, Pennsylvania caps, Ventura CA permit cap and fee hike, and Italy enforcing new STR tax rules. Recorded as a row in `11_regulatory_pending_items.csv` so the sweep is auditable.

---

## 6. New businesses: bear / base / bull, FY26-FY28

All figures USD m of **revenue** (not GBV). "Incremental" = FY28 revenue minus what the FY25 base would have become growing at the scenario's platform nights growth — i.e. what is *not* already inside the driver model's nights path. Full assumption text per row in `11_new_business_scenarios.csv`.

| Business | Case | FY25E | FY26E | FY27E | FY28E | FY28 incremental |
|---|---|---|---|---|---|---|
| Hotels | bear / base / bull | 290 | 348 / 392 / 464 | 400 / 509 / 696 | 448 / 636 / 974 | 91 / 257 / 587 |
| Experiences | bear / base / bull | 90 | 112 / 135 / 162 | 135 / 196 / 275 | 155 / 274 / 441 | 45 / 156 / 320 |
| Services | bear / base / bull | 12 | 24 / 42 / 60 | 38 / 92 / 180 | 54 / 166 / 396 | 39 / 151 / 380 |
| Sponsored listings / ads | bear / base / bull | 0 | 0 | 0 / 120 / 250 | 60 / 350 / 700 | 60 / 350 / 700 |
| **Total** | **bear** | **392** | **484** | **573** | **717** | **235** |
| **Total** | **base** | **392** | **569** | **917** | **1,426** | **914** |
| **Total** | **bull** | **392** | **686** | **1,401** | **2,511** | **1,987** |

**How the FY25 bases were built (all estimates, all disclosed inputs):**
- **Hotels ~$290m.** "Single-digit percentage of nights booked" (Q4'25 and Q2'26 letters) — assume 3.5% of 533m nights = 18.7m nights, x ~$140 hotel ADR x ~11% commission ("best-in-class" per the Q3'25 call; not disclosed). Growth: Q2'26 hotel nights ran ~3x homes; base fades 35/30/25%; bear reverts to 2x the platform once the 15% guest credit expires 31 Dec 2026; bull holds 3-5x. Jefferies has hotels at ~$1bn by 2030, which sits between my base and bull.
- **Experiences ~$90m.** ~40,000 experiences, assumed ~$450m GBV at the disclosed 20% take. Q2'26 supply +80% y/y with seats booked accelerating both y/y and q/q; management explicitly said "thousands of markets ... not this year" (Q2'26 call). Nearly half of Experiences bookings are not attached to a stay (3Q25/4Q25 letters), which is what makes it incremental rather than attach.
- **Services ~$12m.** Ten categories in 260 cities from May 2025 at a 15% host fee with a $6 minimum; assumed ~$80m GBV. The 2026 Summer Release additions (Instacart grocery in 25+ US cities, airport pickups in 160+ cities, luggage storage at 15,000 locations, car rentals) are **referral economics** — management said on the Q2'26 call they "do not think they'll incur a lot of costs." Management's own timeline to materiality is 3-5 years.
- **Ads $0 today.** Not launched. Wedbush expects sponsored listings in 2027 (pitch catalogue); Skift sized an Airbnb ad platform at $1.2bn by 2026 in 2023 and it did not happen. Base assumes a 2027 launch reaching 0.3% of GBV by FY28. Vrbo and Booking already sell placement, and T5 confirms paid placement and rebates already exist on the host side, so the product risk is low and the timing risk is high.

**Not modelled as separate revenue, with reasons:**
- **Co-Host Network:** zero incremental take rate (Q1'25 call). Value is supply quality only.
- **Long-term stays:** 17-18% of nights (2023-24 disclosures), inside core nights, lower take rate after month three. Not incremental.
- **Reserve Now Pay Later:** ~20% of global GBV by Q1'26 and worth **+3 pts of nights growth in Q1'26**, with a +1 pt cancellation rate and a working-capital drag through unearned fees. No fee revenue. It laps from Q3'26 in the US — this is the single biggest reason to be careful about extrapolating 1H26's +9-10% nights.
- **Airbnb for Work:** last disclosed at ~700,000 companies in 2019. No nights share since. Not modellable.

**Sanity check against management.** Feb 2025: $200-250m of FY25 spend to launch and scale the new businesses, described as "easily a $1 billion revenue opportunity." My base reaches $917m in FY27 and $1,426m in FY28. That is consistent, and it means the guidance is a 2027-28 statement.

---

## 7. Synthesis: what the competitive picture actually says

Airbnb's competitive position in 2026 is better than it was in 2024 and the improvement is measurable in one number: Booking.com's alt-accom room-night growth premium over its own total room nights has gone from +6 pts to -1 pt while Airbnb's nights accelerated to +10.3%. Booking is still adding listings at +8% and still has the loyalty asset (Genius L2/L3 = high-50s to low-60s % of room nights) that Airbnb lacks, but it is no longer taking share in nights.

The supply side is boringly stable and that is the finding: 62.5-62.7 nights per average listing for four years, churn of ~25-29% a year that has been flat since 2023, and a US industry that is finally supply-disciplined because mortgage rates keep new hosts out. Nobody should model supply as an independent driver.

The two overlays pull in opposite directions and both are second-order through 2028. Regulation costs 0.15% of revenue in 2026 and 0.87% in 2028 at the median (0.25% and 1.23% at the mean), 93% of it European, with a p95 tail of 4% that is essentially one EU legislative outcome. AI costs nothing in 2026, 1.1% of revenue in 2027 and 1.9% in 2028 in my mid case — and its real form is a conversion of free traffic into paid traffic, not a loss of bookings. The new businesses add 1.4% to 11.7% of FY28 revenue depending on the case. Net across the three, in the base case: **-1.2% revenue from regulation, -1.9% from AI referral costs, +5.4% from new businesses in FY28** — roughly a wash, with a fat left tail and a modest right one.

The thing that should worry a bull is section 2.3. The base case, run against Phocuswright's market forecast, needs Airbnb to be **51.5% of global STR gross bookings by 2028**. That is a big number to underwrite on a 5.3%-CAGR market, and it is the arithmetic a good push-back will use.

---

## 8. For the model

Parameters this workstream supplies to the driver model. Sources are the files listed at the top.

| Parameter | Value | Unit | Where it goes | Source |
|---|---|---|---|---|
| **Nights-growth share cap** | Airbnb GBV / global STR gross bookings: 41.5% (2025) → 51.5% (base 2028), 54.0% (bull 2028) | share | Sanity check on the nights path. Base is defensible; **cap the bull nights path at +9% FY27-28** rather than +10% unless the market forecast is challenged | `11_alt_accom_market_sizing.csv` (derived rows); Phocuswright Aug 2026; 4Q25 letter |
| **Two-player alt-accom nights share** | 59.4% (2022) → 54.5% (2025); reversing in 1H26 | share | Competitive slide; the metric to update after every BKNG print | `11_alt_accom_share.csv` |
| **Regulatory nights drag, EMEA** | -0.36% (2026), **-1.07% (2027)**, -2.07% (2028), median | % of EMEA nights | Subtract from the EMEA nights build | `11_regulatory_overlay.csv` |
| **Regulatory nights drag, NA** | -0.03% / -0.08% / -0.15% (2026/27/28), median | % of NA nights | Subtract from the NA nights build | same |
| **Regulatory revenue drag, global** | median 0.15 / 0.45 / 0.87%; **mean 0.25 / 0.75 / 1.23%**; p95 0.92 / 2.74 / 3.96% (2026/27/28) | % of revenue | Use the **mean** in the base case, p95 in the bear | same |
| **New-business revenue, total** | FY26 484 / 569 / 686; FY27 573 / 917 / 1,401; FY28 717 / 1,426 / 2,511 (bear/base/bull) | USD m | Add on top of the core nights x ADR x take-rate build, net of the "incremental" column to avoid double-counting | `11_new_business_scenarios.csv` |
| **New-business incremental, FY28** | 235 / 914 / 1,987 = 1.4% / 5.4% / 11.7% of a ~$17bn FY28 revenue base | USD m and % | The genuinely additive piece | same |
| **AI referral cost** | FY27 0.38 / 1.14 / 2.28% of revenue; FY28 0.77 / 1.92 / 3.83% (low/mid/high, at a 5% referral fee) | % of revenue | A cost line, or an EBITDA-margin haircut of 1.1 / 3.2 / 6.3 pts-of-EBITDA in FY27 | `11_ai_exposure_scenarios.csv` |
| **Take-rate constraint (upside)** | Single 15.5% host-only fee on ~50% of listings at Q2'26, all listings by end-2026 | share | Supports the bull-case take rate of 13.46% FY26 / 13.56% FY27 | Q2'26 call; Q1'26 call (~25% at Q1'26) |
| **Take-rate constraint (downside)** | 6-10% host fee pilot on host-originated direct links (announced 29 Aug 2026) | % | **Caps the fee-migration tailwind.** If it scales to 10% of nights at an 8-pt fee discount, that is ~-0.8 pts on the blended take rate — larger than the whole single-fee benefit | [Skift 29 Aug 2026](https://skift.com/2026/08/29/airbnb-is-testing-lower-fees-for-hosts-who-bring-their-own-guests/); Bloomberg 31 Aug 2026 |
| **Take-rate floor (evidence)** | European professional managers pay Airbnb 15-17% and rate the risk of forcing commissions down as low ("Airbnb and the rest have set a plateau") | % | Supports the base case's flat take rate rather than compression | Third Bridge T4 (paraphrase) |
| **Supply** | Nights per average active listing flat at 62.5-62.7 for 2022-25 | nights/listing/yr | **Do not model supply as an independent driver.** Listings ≈ nights growth | `11_supply_economics.csv` |
| **Host churn** | Year-ago listing retention 75.4% (2025) → 71.1% (2026) on seven cities; gross adds 25-26% of the ending base | share | Background; no model line, but it is the answer to "is the supply base eroding" (no) | `11_supply_economics.csv` |
| **RNPL lap** | +3 pts of nights growth in Q1'26 from Reserve Now Pay Later; laps in the US from Q3'26 | pts | **Subtract from the FY27 nights path.** This is the main reason the bear FY27 nights case (+6%) is not absurd | 1Q26 letter |

---

## 9. For the 5 November card

1. **Booking's Q2'26 alt-accom read-through is the pre-print anchor and it is favourable.** Booking.com's alt-accom room nights grew +4% in Q2'26 against Airbnb's +10.3%, and Booking guided Q3 total room nights to +3-5%. Booking reports Q3 before Airbnb (it has led by 8-9 days in every quarter of `predictive/02_peer_prints.csv`). **If Booking's Q3 alt-accom growth is again below its total room-night growth, the Airbnb share story holds and the risk to Airbnb's Q3 nights is to the upside.** If Booking's alt-accom re-accelerates above its total, that is the first sign the 1H26 flip was a comp effect.

2. **Experiences and Services metrics to expect.** Q2'26 gave Experiences **supply +80% y/y** with seats booked accelerating both y/y and q/q, and no absolute number. The Q3 letter should give either (a) another supply growth rate — anything below +50% is a deceleration worth flagging — or (b) the first absolute bookings or GBV figure, which would be the disclosure upgrade the sell side wants. On Services, watch for a partner-services metric (grocery, airport pickup, luggage, car rental all launched 20 May 2026, so Q3 is the first full quarter) and for whether management repeats "3-5 years to materiality." A change in that language is the signal, not the numbers.

3. **Hotels.** Q2'26: hotel nights ~3x homes growth, thousands of hotels in 20+ destinations, 35% of first-time hotel guests booking a home within a year. The **15% Airbnb credit expires 31 Dec 2026**, so Q3 is the last clean quarter of subsidised growth. Ask what hotel growth looks like without it. Two Booking.com hotel executives now run the business (D'Amico from May 2026, Rijvers as CBO from 1 Sep 2026) — expect a strategic framing on the call.

4. **The take-rate question to ask.** The single 15.5% fee reaches all listings by end-2026 (positive) but the 6-10% direct-link pilot went live 29 Aug 2026 (negative). Management guided FY26 take rate flat in Aug 2026, down from "modest upside" in May 2026. **Ask for the pilot's scope and for the blended take-rate bridge.** This is the highest-information unanswered question going into the print, and per the transcript-analytics note management has declined to quantify take rate repeatedly.

5. **Two disclosure gaps to press.** Host earnings has not been disclosed since 2023 ($57bn). Active-listing growth has been given only as "in line with nights" since Q3'25. Both stopped being quantified at exactly the moment the take-rate migration began.

6. **What is not a Q3 issue.** AI: Booking put AI tools at <1% of room nights in Q2'26 and the Third Bridge AI expert sees no EBITDA impact for 12-24 months. Regulation: the median 2026 drag is 0.15% of revenue. Neither will move the Q3 print. The EU proposal on 9 Sep will generate headlines and possibly a stock move; the modelled expected value of it is 0.18% of 2027 revenue.

---

## 10. Caveats and what I could not verify

- **Booking's alt-accom nights are derived, not disclosed.** Booking gives total room nights and an approximate alt-accom percentage, separately and sometimes only on the call. The 2024 and 2025 total room-night *levels* are themselves derived from disclosed growth rates ("1.1 billion", "over 1.2 billion"). Treat section 2.1's share levels as ±1-2 pts.
- **Listing counts are not comparable across platforms.** T4 states that European manager inventory is listed non-exclusively and therefore double-counted on Airbnb, Vrbo and Booking. Airbnb's 9m and Booking's 9.1m overlap by an unknown amount.
- **Nights per listing uses rounded disclosures.** "Over 8 million" and "over 9 million" are treated as 8.0 and 9.0, so the 2024 (+4%) and 2025 (+12%) listing growth rates are rounding artefacts of each other. The *level* of ~62.6 is robust because the errors are small relative to the base; the year-to-year listing growth rates are not.
- **The new-business FY25 bases are my estimates, not disclosures.** Airbnb has never given revenue for hotels, Experiences or Services. Every base in section 6 is a nights-x-ADR-x-take construction from disclosed qualitative statements, and each is stated with its inputs so a reviewer can substitute their own.
- **The AI referral-fee assumption (3-8% of booking value) is an analyst assumption**, anchored on metasearch CPC economics. No AI platform has published accommodation referral economics. Both the share and the fee are uncertain, so read the grid, not a point.
- **Regulatory timing is interpolated.** The underlying Monte Carlo produces end-2027 and end-2030 run-rates only. The 2026 and 2028 figures come from my one-third / linear rule, stated in the CSV's note column. The 93% Europe share applies the mean-based regional split to the median total, which is an approximation.
- **Web search budget was exhausted** for this session, so the post-5-Sep news scan ran through Google News RSS and direct fetches rather than search. It covered the trailing week for "Airbnb regulation" and specific checks on the EU draft and Vrbo. A fuller sweep before the pitch is worth doing.

## 11. Corrections to existing work

- `analysis/src/overnight/11_competition_supply_overlays.py` as it stood before this session had three defects, now fixed and re-run: (i) the merge key against `predictive/02_peer_prints.csv` was built as `Q324` against this file's `3Q24`, so the BKNG and EXPE total room-night columns were entirely null; (ii) the AI cost-as-%-of-revenue calculation divided a USD-m revenue base by a further 1,000, understating every percentage by 1000x; (iii) the Inside Airbnb year-ago retention means included partial-scope dumps. That third one mattered most: 25 of 103 year-ago pairs touch a partial-scope dump and they average 0.489 retention against 0.726 for the 78 clean pairs, so the un-excluded means implied a supply collapse that is an artefact of Inside Airbnb changing city boundaries in 2026.
- Not a defect, but a note for whoever owns the Inside Airbnb panel: **Austin's `partial_scope` flag looks like a false positive** on the Sep 2025 and Dec 2025 dumps. Austin's listing count fell from 15,187 (Jun 2025) to 11,295 (Jun 2026) across two *unflagged* dumps while the reviewed-in-LTM share rose from 0.60 to 0.73 — the signature of an inactive-listing purge, not a boundary change. The flag may be catching a real event.
