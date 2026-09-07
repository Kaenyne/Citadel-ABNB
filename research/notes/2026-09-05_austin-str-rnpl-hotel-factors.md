# Austin daily STR counts, RNPL, and what decides Airbnb-vs-hotel

**Author:** Jessie (with Claude). **Date:** 2026-09-05.
**Data:** `data/processed/austin_active_str_daily.csv`, `austin_str_by_type_monthly_raw.csv`, `austin_str_by_type_monthly_avg.csv`, `austin_str_by_district_type_snapshots.csv`.
**Code:** `analysis/src/austin_str_daily.py` (figures 05–07), `analysis/src/count_reviews_duckdb.py` (for Theo).
**Status:** research notes, not memo language.

---

## 1. Can we count the "thank-you reviews" from Theo's data?

Yes, but not from the cloud session. The 258 Inside Airbnb files (7.4 GB, 120 markets incl. all 34 US) are on Theo's external volume (`/Volumes/PortableSSD/ABNB_DATA_EXPANSION/...`), only the manifest is in the repo, and `data.insideairbnb.com` refuses the sandbox. The count therefore has to run on Theo's machine.

`analysis/src/count_reviews_duckdb.py` does it: reads `data/manifests/inside_airbnb_download_log.csv`, takes the latest `reviews.csv.gz` per market, and has DuckDB count reviews per market per quarter straight from the gzipped files (only `date` is projected, text is never loaded — Austin's 643k-row file takes seconds). It drops the partial last quarter of each snapshot (a 2026-06-22 snapshot keeps Q1-26 as its last full quarter) and writes:

- `data/processed/inside_airbnb_reviews_by_market_quarter.csv` — market, quarter, reviews, YoY
- `data/processed/inside_airbnb_reviews_us_total_quarter.csv` — US sum + YoY (comparable to Airbnb's North America line)

Tested on synthetic files with the same layout (multi-line comment fields, mixed snapshot dates). Run: `python analysis/src/count_reviews_duckdb.py` (add `--countries united-states` for US only).

What it will tell us: review count ≈ completed stays × review rate (~50% per Inside Airbnb's assumption), so its YoY is a *realised-demand* proxy per city that Airbnb never discloses. Join US total YoY to North America revenue YoY (`airbnb_regional_revenue_quarterly.csv`) and test the one-quarter lead. Caveat: reviews lag *bookings* by the lead time (weeks), and reviews.csv only covers listings alive at the snapshot — delisted units' reviews vanish, which biases older quarters down a little.

---

## 2. Austin daily active STR licences — what the series says

Source: City of Austin Development Services, Socrata `mydx-h5dy` ("Active Short Term Rental Counts"), one row per date × licence type × council district. 527 daily dates, 2025-03-13 → 2026-09-05 (plus one 2025-02-28 point). Counts are **licences**, not listings: Inside Airbnb shows ~11.3k Austin listings (2026-06-22 snapshot) against 2.9k licences, so most Austin supply is unlicensed and outside this data.

**Level:** 2,268 (13 Mar 2025) → 2,920 (5 Sep 2026), **+29% in 18 months**, about 1.4% a month. Almost no day-to-day noise (licences expire and renew slowly), so steps are real events, not sampling.

**Timing of the steps** (month-end changes): +146 Mar-25, ~+60–70/month Apr–Jun-25, *−43/−26 Jul–Aug-25*, +88 Sep-25, +78 Oct-25, +8 Nov-25, **+131 Dec-25** (of which +129 between 11 and 19 Dec), ~0 Jan–Feb-26, +26/+34 Mar–Apr-26, **+97 May-26**, ~0 Jun-26, +49 Jul-26, ~0 Aug-26.

**Policy context (from austintexas.gov/department/short-term-rentals, verified):**
- Feb 2025: Council made STRs an accessory use to all residential uses in all zoning districts, provided the unit holds a valid operating licence. This re-legalised licensing of non-owner-occupied units in residential zones.
- Oct 2025: revised rules took effect — licences run two years instead of one, Certificate of Occupancy and proof of insurance no longer required, tenants may operate with landlord permission, density limits (single-family: up to two units per operator; multifamily: greater of one unit or 10% of units), neighbour notice at every renewal.
- 1 Jul 2026: platforms must show a licence field and remove unlicensed listings on the city's request.

The Sep–Dec 2025 acceleration lines up with the Oct 2025 rule change (cheaper, easier, longer licences), and the Dec-25 and May-26 jumps look like processing batches rather than demand events — hedge accordingly. The Jul-2026 platform rule has *not* produced a visible surge yet (Jul +49, Aug ~0), which is itself informative: either enforcement hasn't started or hosts are waiting.

**Composition — the finding (fig 06):** 13 Mar 2025 → 5 Sep 2026

| Type (Austin LDC 25-2-788..791) | Mar-25 | Sep-26 | Change |
|---|---|---|---|
| Type 1 — owner-occupied | 830 | 770 | −7% |
| Type 1-A | 104 | 96 | −8% |
| Type 1-Secondary (ADU on owner's lot) | 212 | 193 | −9% |
| Type 2 Commercial (non-owner-occupied, commercial zoning) | 37 | 24 | −35% |
| **Type 2 Residential (non-owner-occupied, residential zoning)** | 615 | **1,097** | **+78%** |
| **Type 3 (multifamily units)** | 470 | **740** | **+57%** |

Every owner-occupied category *shrank*. All of the +652 net growth (and more) is investor-owned single-family homes in neighbourhoods (+482) and apartment units (+270). Type 2 Residential grew every month from March 2025 — the Feb 2025 zoning change is the obvious driver; Type 3 stepped up Nov–Dec 2025 and Jul 2026, consistent with the Oct 2025 multifamily density rule. (Type definitions: Type 1/2/3 split is from the Land Development Code; the 1-A / 1-Secondary sub-definitions are not in the dataset metadata — verify wording before quoting.)

**Geography (fig 07):** D3 +243 (465→708) and D1 +139 (271→410) — East Austin — take 59% of the net growth; D9 (downtown/UT, largest at 727) +82; D2 +79 (97→176, +81%); D8 −17 is the only decline. Supply is spreading east and south from the core.

**Why it matters for ABNB:**
- Direction: legal, professional supply in a top-10 US Airbnb market is growing ~20%/yr while national reported nights grow 7–10%. Supply growth is a *bullish* input for a marketplace (more selection → conversion, ADR discipline).
- Mix: growth is professional/investor hosts, not "a family renting a spare room." Professional hosts are more likely to multi-home across Airbnb, Vrbo and direct booking → take-rate and share pressure over time. This is the same shift Airbnb's own hotel/pro-host push is responding to.
- Regulation cuts both ways: Austin is a *loosening* story (2025) with an *enforcement* step (Jul 2026). Compare NYC (LL18, listings 41k→10k) — the 34 US Inside Airbnb markets let us build a loosening-vs-tightening scorecard.
- Limit: licences ≠ demand. This is a supply series; pair it with the review counts (section 1) for Austin demand.

---

## 3. Is Reserve Now, Pay Later good for ABNB?

Evidence base: `research/airbnb_earnings_call_study.md` §8.2 (Krishang; management statements Q3-25 → Q2-26), plus the unearned-fees series (`data/processed/abnb_edgar_quarterly_kpis.csv` (Theo, XBRL deferred_revenue column), 10-Q balance sheets).

**What it is.** Eligible guests pay $0 at booking; the card is charged on a scheduled date (US launch: eight days before the free-cancellation window closes). No credit, no interest, not a loan. Listings need flexible/moderate cancellation policies. US launch start of Q3 2025 → merchandised up-funnel Q4 2025 → most of the world Q1 2026 → more booking types Jul 2026. ~70% adoption among eligible; >20% of total GBV in Q1–Q2 2026.

**For (management's four channels, quantified where they gave numbers):**
1. Conversion — removes the upfront charge that stops hesitant and first-time bookers (first-time bookers +11% in Q2-26, though not attributed solely to RNPL).
2. Longer lead times — "locking in earlier calendar share" before guests shop Booking/Vrbo.
3. Higher ADR / mix — guests "choose a slightly nicer listing"; mix shifts toward 4+ bedroom homes.
4. Reopened the cancellation-policy lever (Strict retired → Firm), which itself lifts conversion.
The RNPL + cancellation + single-fee bundle: ~2 pts nights / ~3 pts GBV (Q4-25) and ~3 pts / ~4 pts (Q1-26). Chesky: "a uniquely large bullet." Nights growth went from ~7% to 9–10% over this period.

**Against (the costs, all visible in filings):**
1. **Float drain.** Unearned fees were $2,733M (Mar-26) and $2,831M (Jun-26), **flat YoY while GBV grew +19% / +16%**. Had unearned fees tracked GBV they would be ~$0.5B higher — cash Airbnb no longer holds early. At ~4% on $0.5B that is on the order of $20M/yr of forgone interest income — immaterial to earnings; the bigger point is the **unearned-fees leading indicator is broken** as a read on next-quarter revenue.
2. **Cancellations +1 pt** (aggregate ~16% → ~17%, higher within the RNPL cohort). A booking that cancels before payment date was never revenue; GBV "growth" includes bookings that will not convert. Reported GBV is gross of future cancellations, so the headline GBV lift overstates the revenue lift.
3. **Pull-forward / comp risk.** US laps Q3-26 (now), global Q1-27. FY26 guide (≥ mid-teens revenue) needs Q4 to hold Q3's rate while lapping the launch. This is the single most important near-term risk for a 3–12-month long.
4. Host risk: late cancellation when a card fails; management says host terms/payouts unchanged, so Airbnb absorbs friction.
5. Take-rate optics: revenue recognised at check-in, so the timing gap between GBV and revenue widens.

**Verdict (research view, not memo language):** RNPL is net positive for the *business* — it is a conversion tool that costs Airbnb float and ~1 pt of cancellations, and it has not lowered take rate. It is a **risk for the stock** on a 3–12-month horizon because (a) the lift is about to lap, (b) reported GBV/nights growth flatters underlying demand by the cancellation delta, and (c) the deferred-revenue tell we would normally use to check management's guide has gone quiet. Whether long or short, the pitch has to state how much of the 2025–26 reacceleration is RNPL (management: 2–4 pts of a 9–10% print, i.e. a quarter to a third of it) and what nights growth looks like ex-RNPL in Q4-26 — the honest answer today is "6–8%, uncertain."

Things we could still measure: (i) cancellation rate proxies from Inside Airbnb `calendar.csv.gz` (dates that flip booked→available); (ii) lead time from `reviews` vs `calendar`; (iii) US vs international nights growth Q3-25 → Q2-26 (RNPL was US-only until Q1-26 — a natural experiment; the Airbnb regional revenue file already lets us compare NA vs EMEA growth through the launch).

---

## 4. What decides Airbnb vs hotel — data we can actually get

Question: party size, gender, location, travel purpose — which matter? Findings from a literature/data sweep (subagent, 2026-09-05; re-verify each figure at the link before quoting in a memo).

**Ranked by strength of evidence:**

| Factor | Direction | Evidence | Data we can download |
|---|---|---|---|
| **Party size / group & family travel** | Strongest driver toward Airbnb | Upgraded Points survey (Oct 2025, n≈2,193): STR chosen for space 75%, kitchen 68%, groups 56%. NerdWallet/Harris: parents 65% vs non-parents 45% prefer rentals. Airbnb itself: mix shifting to 4+ bedroom homes (Q4-25/Q1-26 calls). | Inside Airbnb `listings` → `accommodates`, `bedrooms` distribution and their review velocity by city; BLS/NHTS trip party-size tables. |
| **Length of stay** | Longer → Airbnb | Airbnb: 28+ night stays 17–21% of nights (~2% of bookings). Kitchen/laundry economics dominate past ~4 nights. | Airbnb 10-K/letters (long-stay share); Inside Airbnb `minimum_nights`, calendar gaps. |
| **Travel purpose** | Leisure → Airbnb; business → hotel | Guttentag (2018): practical attributes (cost, location, amenities) dominate, "authenticity" secondary. Business travel ~15% of Airbnb bookings (2018, stale). Hotels win on loyalty points, expensing, predictability. | GBTA / Deloitte corporate-travel surveys; Airbnb for Work disclosures (thin). No clean public split. |
| **Location / market type** | Urban → hotel share rising; suburban, drive-to, rural → Airbnb | CoStar (2025): urban STR demand −16% vs 2019, suburban +43%; urban STR ~25% cheaper than hotels, suburban ~5% pricier. Zervas et al. (2017): +10% Airbnb supply → −0.35% hotel revenue in Austin; Farronato & Fradkin (AER 2022): 62% of Airbnb guests would not have booked a hotel (87% in capacity-constrained periods) — Airbnb *expands* the market more than it steals. | STR/CoStar (paid; Bloomberg has hotel RevPAR by market — see docs/terminal_guide.md); Inside Airbnb city snapshots vs local hotel occupancy from tourism boards (Hawaii DBEDT, LVCVA, Orlando). |
| **Price / fees** | Cleaning fees push people to hotels | Upgraded Points: hotels preferred 61–62% overall; top hotel reasons amenities 73%, no cleaning fees 62%; 63% say they have avoided Airbnb because of cleaning fees. Skift: 89% of US listings charge a cleaning fee (~$96 avg). Airbnb's single-service-fee and total-price display are direct responses. | Inside Airbnb has nightly `price` but **not** cleaning fees since 2023 — need AirDNA/PriceLabs (paid) or scrape. |
| **Age / life stage** | Younger, families → Airbnb; 55+ → hotel | Multiple surveys (Morning Consult, NerdWallet). Loyalty members more likely to *also* use Airbnb (36% vs 15%, 2016 — stale). | Morning Consult travel tracker (free summaries); Phocuswright US STR usage 24% → 30% incidence. |
| **Gender** | **No usable evidence.** | Surveys report gender splits of respondents but none finds gender as a choice driver; safety concerns skew female in qualitative work only. | Nothing public. Don't put it in the memo. |

**Market-share context:** Airbnb's share of STR-platform bookings 28% → 44% (Skift, 2019–2024); US STR usage incidence 24% → 30% (Phocuswright). Both say the Airbnb-vs-hotel question is increasingly "Airbnb vs Vrbo/Booking" within STR, not STR vs hotel.

**What this means for the ABNB pitch:**
- The controllable drivers Airbnb is attacking (fees → single fee/total price; predictability → Guest Favorites, hotels on platform; business → Airbnb for Work) map exactly onto the top hotel-preference reasons. That's the bull case in one line: the reasons people pick hotels are fixable product problems.
- The structural driver (groups/families/long stays) is where Airbnb wins and hotels can't follow; it is also the segment RNPL and the 4+ bedroom mix shift are feeding.
- Urban softness is the risk: the biggest Airbnb cities (Paris, London, NYC, Rome) are the ones with regulation and hotel competition; the growth is drive-to and suburban.
- Gender: no data, drop the question.

**Free datasets to pull next (in rough priority):** Inside Airbnb `listings` (accommodates, bedrooms, minimum_nights, review_scores) across the 34 US markets — Theo already has them; Hawaii DBEDT monthly (hotel vs vacation-rental occupancy and ADR, official, same source); LVCVA and Visit Orlando monthly hotel occupancy; Eurostat `tour_occ_*` (hotel nights) next to `tour_ce_*` (platform nights) for a hotel-vs-platform share by country — Theo has the platform side already; Morning Consult / Deloitte travel survey PDFs for the survey layer.

---

## Sources

- City of Austin Development Services, Active Short Term Rental Counts, Socrata `mydx-h5dy` (pulled 2026-09-05 via SoQL; queries in `analysis/src/austin_str_daily.py`). Ordinance timeline: austintexas.gov/department/short-term-rentals (fetched 2026-09-05).
- Airbnb 10-Q Q1/Q2 2026 balance sheets (unearned fees); Airbnb shareholder letters and earnings calls Q3-25 → Q2-26 via `research/airbnb_earnings_call_study.md`.
- Farronato & Fradkin, "The Welfare Effects of Peer Entry: The Case of Airbnb and the Accommodation Industry," AER 2022. Zervas, Proserpio & Byers, "The Rise of the Sharing Economy: Estimating the Impact of Airbnb on the Hotel Industry," JMR 2017. Guttentag et al., "Why Tourists Choose Airbnb," JTR 2018.
- Upgraded Points hotel-vs-vacation-rental survey (Oct 2025); NerdWallet/Harris travel survey; CoStar/STR urban vs suburban STR demand (2025); Skift Research (cleaning fees; STR platform share); Phocuswright US Traveler Technology Survey. All via subagent sweep 2026-09-05 — verify URLs and exact figures before quoting.
