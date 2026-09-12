# 03. Insider mechanics: how Airbnb revenue is generated, recognised and guided

**Date:** 2026-09-11. **Author:** Claude Code (ground-truth workstream 01-03, revenue-forecast strategy).
**Audience:** the modelling team and a Citadel PM. **Frame:** what Chesky and Mertz know when they set the range.
**Conventions:** *measured* = computed from a disclosure or a dataset in this repo; *assumed* = an analyst input;
*unidentified* = not separable with public data. Every repo claim cites a path that was opened for this note.
Prices/consensus as of 3-4 Sep 2026 (spot $181.94, 4 Sep close). Next print ~5 Nov 2026.

---

## 0. The one-paragraph version

Airbnb books GBV when a guest *books* and recognises revenue when the guest *checks in*. Everything that is hard
about forecasting this company follows from that single wedge. Nights, GBV and ADR are booking-dated, transaction-
period metrics net of cancellations that occur in the period; revenue is check-in-dated. The quarterly "take rate"
is therefore not a monetisation rate at all — it is the ratio of a check-in-dated numerator to a booking-dated
denominator, and it swings 9.2% / 13.1% / 18.3% / 14.0% through the year (2023-25 means, `02_kpi_panel_quarterly.csv`)
while the LTM rate sits at 13.2%. Because ~two thirds of a quarter's revenue is set by the prior quarter's bookings
and ~one third by the quarter before that, the revenue guide management gives is close to arithmetic: they can see
most of it on the booking ledger on guide day. That is why the revenue range has been beaten 19 times out of 19 by a
small, shrinking margin (median cushion +1.79% over the last 8 prints, `02_guidance_cushion_series.csv`) and why the
stock does not trade on it. What management cannot see on guide day is the *next* quarter's bookings, the FX rate
that will apply to them, and how many of the bookings already on the ledger will cancel. Those three are the entire
forecasting problem.

---

## 1. Recognition mechanics

### 1.1 The accounting policy, verbatim

From the FY2025 10-K (filed 12 Feb 2026, accession 0001559720-26-000004, "Revenue Recognition" in the Significant
Accounting Policies note; retrieved and parsed for this note):

> "The performance obligation, governed by the acceptance of the Company's ToS, is satisfied at the point of check-in
> when the guest begins their stay and the Company obtains an enforceable right to payment. Accordingly, revenue is
> recognized on the consolidated statements of operations, at the point of check-in."

> "The Company's ToS stipulates that a host may cancel a confirmed booking up to the point of check-in. As such, for
> accounting purposes, each booking represents a separate contract between the host and guest, which is not enforceable
> until check-in. As a result, at December 31, 2024 and 2025, there were no partially satisfied or unsatisfied
> performance obligations. Service fees collected from customers prior to check-in are recorded as unearned fees on the
> consolidated balance sheets. **The unearned fees are not considered contract balances, as they are subject to refund
> in the event of a cancellation.**"

Three consequences a PM will test you on:

1. **There is no ASC 606 remaining-performance-obligation disclosure and no unearned-fee rollforward.** Airbnb has
   legally engineered the booking so that nothing is a contract until check-in. So the "backlog" everyone quotes
   (unearned fees) is a *cash* balance, not a booked-revenue balance, and the company never tells you how much of the
   opening balance was recognised in the period. Every backlog conversion ratio in this repo is an estimate.
2. **Long-term stays (28+ nights) are month-to-month contracts.** "Revenue is recognized for the first month upon
   check-in and for subsequent months upon each month's anniversary from the initial check-in date." A 90-night stay
   booked in Q1 and starting in June puts revenue into Q2, Q3 and Q3 again. Long stays were 24% of gross nights in
   1Q21, 17% in 1Q24 (last disclosure, `02_kpi_panel_long.csv`), and the repo's calendar/ALOS build puts the 28+
   share at 13.4% in 2025 falling ~2-2.5pp a year (`research/notes/2026-09-09_los_synthesis.md`). The LTS mix shift is
   therefore *shortening* the recognition tail, a small pro-cyclical accelerant nobody models.
3. **Revenue is net, as agent.** Taxes, cleaning fees and pet fees are in GBV but excluded from revenue and cost of
   revenue. So GBV is a gross-of-tax base and the "take rate" is diluted by whatever the tax and cleaning-fee content
   of GBV is — which moves with geography (EU VAT on rentals since 2023) and with the cleaning-fee purge (roughly 40%
   of listings charge no cleaning fee, TechCrunch 13 Feb 2024, `06_fee_timeline.csv`).

### 1.2 The KPI definitions, verbatim (FY2025 10-K, MD&A "Key Business Metrics")

> "Nights and Seats Booked on our platform in a period represents the sum of the total number of nights booked for
> stays and the total number of seats booked for experiences and services, **net of cancellations and alterations that
> occurred in that period**. For example, a booking made on February 15 would be reflected in Nights and Seats Booked
> for our quarter ended March 31. If, in the example, the booking were canceled on May 15, Nights and Seats Booked
> would be reduced by the cancellation for our quarter ended June 30."

> "GBV represents the dollar value of bookings on our platform in a period and is inclusive of host earnings, service
> fees, cleaning fees, and taxes, net of cancellations and alterations that occurred during that period… Revenue from
> the booking is recognized upon check-in; accordingly, **GBV is a leading indicator of revenue**. The entire amount of
> a booking is reflected in GBV during the quarter in which booking occurs, whether the guest pays the entire amount of
> the booking upfront or elects to use our Pay Less Upfront program."

This is the single most under-modelled sentence in the filing. **Reported nights are a net flow, not a gross flow.**
They contain the current quarter's gross bookings *minus* cancellations of bookings made in *any* prior quarter. A
product that raises gross bookings and also raises cancellations (RNPL) does not show up as one number; it shows up as
a positive in the booking quarter and a drag in every later quarter until the cohort clears. Reported nights can
decelerate with gross demand unchanged.

### 1.3 The backlog identity (write this on the whiteboard)

Let `G_b` = GBV booked in quarter b (gross, before cancellations), `c(b,q)` = share of `G_b` cancelled during quarter q,
`m(b,q)` = share of `G_b` that checks in during quarter q, `tau` = the economic take rate on fee-bearing GBV, and
`p(b)` = the share of fees collected in cash at booking.

**Printed metrics**

```
Nights_q   = GrossNights_q  -  SUM_over_b<=q  CancelledNights(b,q)  +/- Alterations_q
GBV_q      = G_q            -  SUM_over_b<=q  c(b,q) * G_b          +/- Alterations_q
ADR_q      = GBV_q / Nights_q                       (both booking-dated; both net of cancellations)
```

**Revenue**

```
Revenue_q  = tau_eff * SUM_over_b<=q  m(b,q) * G_b
```

**Balance-sheet backlog**

```
UnearnedFees_q = UnearnedFees_{q-1}
                 + tau * p(q) * G_q                     (fee cash received at/after booking, before check-in)
                 - Revenue_q                            (released at check-in)
                 - RefundedFees_q                       (cancellations release the liability to cash, not revenue)
                 +/- FX translation

FundsHeld_q    = FundsHeld_{q-1}
                 + GuestCashReceived_q  (booking amount net of fees)
                 - HostPayouts_q        (disbursed after check-in)
                 - GuestRefunds_q
```

Funds receivable and funds payable are equal and offsetting by construction (both $12,224m at 30 Jun 2026, 2Q26 10-Q),
so only the *level* is informative, never the net.

**Take rate, decomposed:**

```
TakeRate_q = Revenue_q / GBV_q = tau_eff * [ SUM_b m(b,q) * G_b ] / G_q(net)
```

The bracket is a *timing ratio*, not a price. In Q1, `G_q` is at its annual maximum (guests book the summer) while the
numerator is at its minimum (winter check-ins) → 9.2%. In Q3, `G_q` is at its annual minimum (shoulder-season, last-
minute bookings) while the numerator peaks (summer check-ins) → 18.3%. **The LTM take rate (13.2% at 2Q26) is the only
one that approximates `tau_eff`, and even that drifts with the booking-window mix.** Any model that forecasts a
quarterly take rate as a monetisation assumption is forecasting a calendar artefact. Mertz has said exactly this and
refused to elaborate: *"The underlying kind of if you shifted take rate is unchanged. You know, any of the variation in
take rate is just a timing difference between revenue stays versus timing of bookings"* (2Q22 call, John Colantuoni,
`data/processed/abnb_declined_to_quantify.csv`).

### 1.4 The booking-to-check-in lag: what is known, inferable and unknown

**Airbnb has never disclosed lead time.** Not once in 23 letters or 23 calls. It is the single most consequential
undisclosed series — the repo's H1-to-H2 note shows the two occasions the seasonal pattern broke for reasons invisible
from outside were *both* lead-time changes (2Q24 shortening, which produced the −13.4% print on 7 Aug 2024; 2025
lengthening under RNPL, which produced the +2 to +3pp ADR ex-FX surprise in 3Q25/4Q25). See
`research/notes/2026-09-10_h1-to-h2-bridge.md` §5.

What can be inferred, ranked by hardness:

| Estimator | Value | Basis | Status |
|---|---|---|---|
| Non-negative lag fit of revenue on lagged GBV | ~2/3 weight on GBV(t-1), ~1/3 on GBV(t-2); blended conversion ~14% | post-COVID quarterly regression, `research/airbnb_earnings_call_study.md` §8.4 | **measured**, n≈20 |
| Q3 conversion of lagged GBV | 17.4% / 17.1% / 17.2% for the last three Q3s | `data/processed/h2_bridge/h2_bridge_gbv_lag_conversion.csv` via `research/notes/2026-09-10_h1-to-h2-bridge.md` §4 | **measured**, remarkably stable |
| Q4 conversion of lagged GBV | 12.0% / 12.1% / 12.0% | same | **measured** |
| Unearned-fee coverage of next-quarter revenue | Q1-end 0.880, Q2-end 0.697, Q3-end 0.661, Q4-end 0.676 (2023-25 means) | computed here from `data/processed/abnb_backlog_indicators.csv` | **measured**, now broken (§1.5) |
| Average nights per booking (a LOS, not lead-time, proxy) | 3.7 global FY25 (3.8 FY24); NA 4.1, EMEA 3.8, LatAm 3.6, APAC 3.3 | FY2025 10-K MD&A Geographic Mix | **measured**, disclosed annually |
| Calendar blocked-rate booking curve | one vintage per market (Jul-Aug 2026), 120 markets, h000_030 / h031_060 / … horizons | `data/processed/booking_curves_by_market.csv` (601 rows), `booking_curve_daily.csv` (44,380 rows) | **assumed** as a level; **unusable** for y/y — single vintage, host blocks included, calendars carry no price |
| Lead time by region and stay length | — | — | **unidentified** |
| RNPL cohort cancellation curve | — | — | **unidentified**; see §1.6 |

The honest statement for the memo: *the booking→check-in transition matrix `m(b,q)` is estimated, not observed; its
first two columns (2/3, 1/3) are stable enough that the Q3 and Q4 revenue conversions have a 0.3pp range over three
years; nothing in the public record pins its tail.*

**Share of next-quarter revenue already determined at the guide date.** Two estimators, which now disagree, and the
disagreement is itself the finding:

- *Econometric:* a non-negative fit with **no same-quarter GBV term** explains 3Q revenue to within 0.3-0.6%. Applied
  to 6 Aug 2026: lagged GBV = (2/3)($27.2bn) + (1/3)($29.2bn) = **$27.87bn**; at the 17.1-17.4% Q3 conversion that is
  **$4.78-4.85bn**, point $4.80bn. So on the booking ledger alone, management could see essentially the whole quarter.
  Call it **85-90% determined**, with the residual being same-quarter last-minute bookings and cancellations.
- *Balance sheet:* unearned fees of $2,831m at 30 Jun 2026 against a $4,730m guide midpoint is **59.9% pre-funded**,
  versus a 2023-25 Q2-end norm of **69.7%**. That is a 9.9pp break.

The gap between the two estimators is RNPL and the fee-structure migration, and it is now large enough to invalidate
the cleanest backlog indicator in the model. Quantified below.

### 1.5 The backlog indicator is broken, and by a measurable, dated amount

Take the 2023-25 seasonal coverage ratios as the pre-RNPL norm and back out the unearned-fee balance that *would* have
been required to deliver the actual (or guided) next-quarter revenue. Computed here from
`data/processed/abnb_backlog_indicators.csv` and the 2Q26 guide midpoint:

| Quarter-end | Reported unearned fees | Norm coverage | Pro-forma balance implied by next-Q revenue | Gap | Gap % of reported |
|---|---|---|---|---|---|
| 3Q25 | $1,820m | 0.661 | $1,836m | $16m | **0.9%** |
| 4Q25 | $1,743m | 0.676 | $1,810m | $67m | **3.8%** |
| 1Q26 | $2,733m | 0.880 | $3,175m | $442m | **16.2%** |
| 2Q26 | $2,831m | 0.697 | $3,297m (at the $4,730m guide mid) | $466m | **16.5%** |

Restated on this basis, unearned fees grew **+16.6% y/y in 1Q26** (against GBV +19.2%) and **+15.4% in 2Q26** (against
GBV +15.7%) — i.e. the backlog is fine and the reported series is an accounting artefact. Reported unearned fees were
**+0.4% and −0.9%**. The distortion ramps exactly with the RNPL global rollout (Feb 2026) and the single-fee migration
(Oct 2025 → ~25% of listings at 1Q26 → ~50% at 2Q26).

Funds held is distorted by roughly a third as much: $12,224m at 2Q26 is +10.5% y/y against GBV +15.7%, a 5.2pt
shortfall, $581m or **4.8%** of the balance. The asymmetry is the mechanism: funds held is booking-amount-denominated
(~87% of GBV) and only RNPL defers it; unearned fees are fee-denominated (~13-15% of GBV) and are hit by RNPL *and*,
plausibly, by the single-fee migration moving fee collection from the guest at booking to the host's payout after
check-in. **Management attributes it entirely to RNPL** ("management says both would have grown absent RNPL",
`research/airbnb_earnings_call_study.md` §3.2, from the 1Q26/2Q26 letters). The fee-structure leg is *unidentified*
and is a question for the 5 Nov call and for the 3Q26 10-Q.

**Modelling instruction:** carry `unearned_fees_restated = reported / (1 − d_q)` with `d_q` the dated distortion
series above (0.9 / 3.8 / 16.2 / 16.5%), and run the backlog regressions on the restated series. The repo's survivor
test (`data/processed/overnight/08_backlog_tests.csv`) has unearned-fee y/y against next-quarter revenue growth at
r = 0.968 in sample (n=18) but a walk-forward RMSE ratio of **1.17x naive and 1.28x AR(1)** — i.e. it does *not* beat
the naive on revenue. It does beat naive on **nights** (0.90x naive, 0.65x AR(1), sign accuracy 0.64). That is the
version of the claim to make: *the backlog predicts volume, not dollars, and only after restatement.*

### 1.6 Reserve Now, Pay Later: what it does to the plumbing

Mechanics (`research/airbnb_earnings_call_study.md` §8.2; Airbnb Help Center 2143):
guest pays **$0 at booking**; the card is charged on a scheduled date shown at checkout — at US launch, eight days
before the end of the listing's free-cancellation window. Not a loan, no credit check. Eligibility is Airbnb's choice:
**flexible or moderate cancellation policies only**, which is why the Oct 2025 retirement of Strict and migration to
Firm was a *precondition*, not a coincidence.

Rollout (dated, `research/notes/2026-09-10_rnpl-conversion-framework.md`):

| Date | Event |
|---|---|
| Beginning 3Q25 | US domestic launch; ~70% take-up when offered |
| 14 Aug 2025 | Public US announcement |
| 4Q25 | Merchandised up-funnel |
| 17 Feb 2026 | Global (domestic + international), eligible listings |
| 1Q26 | ~20% of global GBV; longer booking windows, higher-priced home mix |
| Jul 2026 | Eligible booking types expanded; >20% of 2Q26 GBV |

Effects, separated by evidence class:

- **Measured / disclosed:** aggregate cancellation rate moved from *"roughly 16% historically versus 17%"* (4Q25 call),
  higher within the RNPL cohort. ~70% adoption among eligible. >20% of GBV.
- **Disclosed but mis-attributed everywhere:** the *"approximately 3 points of nights growth and 4 points of GBV growth"*
  in 1Q26 (and ~2/~3 in 4Q25) is the **combined** effect of RNPL + the cancellation-policy redesign + simplified fees.
  It is **not** an RNPL-only or a US-only number. Anyone subtracting 3 points for a US RNPL anniversary is double-
  counting (1Q26 call, printed p.6; the H1/H2 bridge carries a status banner correcting this).
- **Unidentified:** night-weighted RNPL cancellation curve; platform eligibility share; the cancellation-lag
  distribution. The framework note gives the conditional arithmetic: if RNPL alone explains a 1-point platform
  cancellation rise, its excess cancellation probability is `0.01 / p_nights` — 6.7pp at a 15% nights share, 5.0pp at
  20%, 4.0pp at 25%. And the GBV→nights conversion `p_nights = s / [r(1-s) + s]`: a 20% GBV share at a 25% ADR premium
  is **16.7% of nights** and, at 1.5x dwell time, **23.1% of the live backlog**.
- **Sensitivity that matters for the 5 Nov card:** on 3Q25's 133.6m and 4Q25's 121.9m bases, one million extra net lost
  nights is **−0.75pp** on Q3 growth and **−0.82pp** on Q4.

---

## 2. Every revenue lever, its term, its 2025-26 magnitude, its lead indicator, and whether it is disclosed

The identity the levers attach to (as implemented in `model/ABNB_driver_model.xlsx` / `analysis/src/overnight/13_driver_model.py`):

```
Revenue = [ SUM_region  PriorYearNights x (1 + growth - regulatory drag) ] x ADR_exFX x (1 + ADR_FX)   = GBV
        x TakeRate_quarterly x (1 + FX timing wedge)                                                   = core revenue
        + new business outside GBV (ads)
```

### 2.1 Volume levers (hit nights / seats)

| Lever | Term | 2025-26 magnitude | Lead indicator | Disclosed? |
|---|---|---|---|---|
| **RNPL + cancellation redesign + single fee (bundle)** | nights, GBV, ADR mix, timing | +2pp nights / +3pp GBV (4Q25); **+3pp / +4pp (1Q26)**, mgmt's own estimate, bundle not RNPL-alone | RNPL GBV share (>20%); eligibility expansions (Feb 2026, Jul 2026) | Partially — bundle only, never decomposed |
| **RNPL cancellation drag** | nights (net of cancellations), backlog | platform cancellation ~16% → ~17%; RNPL cohort higher, size undisclosed | unearned fees vs GBV growth; funds-held gap | No |
| **Supply growth** | nights (co-moving, not causal) | **Nights per average active listing = 62.5 / 62.7 / 62.6 / 62.7 in 2022-25.** Four years of listings exactly absorbing nights | listings level ("over 9 million", 4Q25); Inside Airbnb 982k-listing store | Level only since 1Q24; growth % dropped |
| **Quality removals** | nights (small), ADR (positive mix) | >550,000 listings removed since 2023 (3Q25); Guest Favorites ≈ half of bookings (4Q25) | cumulative removal count | Occasionally |
| **Host churn** | supply base | year-ago listing retention 75.5% → 73.4% on six cities ex-Austin; new listings a flat 25.4% of the ending base; Common Crawl survival 86-88% since 2023 | `data/processed/overnight/11_supply_economics.csv`; monthly Inside Airbnb | No |
| **Expansion markets** | nights (+), ADR (−, lower-ADR geographies) | origin nights growing **~2x core for six-plus consecutive quarters**; India origin nights +50-60%; Brazil top-10 → top-5 | regional nights bands; no market-level data | Qualitative only |
| **Cross-border** | nights, ADR (+), FX exposure | 46% of gross nights at 1Q24, **series stopped**; AirDNA: US international inbound STR demand **−12% vs spring 2025, Canada −32%** (Jul 2026) | national tourism boards; TSA/BTS/IATA in repo | **Stopped 1Q24** |
| **Urban recovery** | nights, ADR (+ in cities), LOS (−) | 51% of gross nights at 4Q23 vs 59% in 4Q19, **series stopped** | Inside Airbnb urban panel | **Stopped 4Q23** |
| **App share / first-time bookers** | nights (conversion) | app 64% of nights (2Q26), app nights +23%; first-time bookers **+8% → +10% → +11%** (4Q25/1Q26/2Q26), "highest in four years" | disclosed quarterly since 4Q25 | Yes |
| **Hotels / HotelTonight** | nights (+, dilutive to ADR and take rate) | single-digit % of nights; growing **~3x homes** (2Q26); thousands of hotels in 20+ destinations; ~35% of first-time hotel guests book a home within a year | 15% Airbnb credit **expires 31 Dec 2026** — Q3 is the last subsidised quarter | Qualitative only; no unit economics |
| **Experiences / Services seats** | seats in the denominator (dilutive to ADR) | Experiences supply **+80% y/y** (2Q26); seats "immaterial" (2Q25); seats share of denominator 1.3% FY25 → 2.8% FY27 base | supply growth rate; any absolute number would be a disclosure upgrade | No absolute figures |
| **Events** | nights (+1-2% of a quarter) | Paris Olympics ~700k guests (3Q24); Milan Olympics (1Q26); World Cup ended 19 Jul 2026, **>150,000 first-time-host listings** | dated years ahead | Qualitative |
| **Regulation** | nights (−), regional | median revenue drag 0.15% (2026), 0.45% (2027), 0.86% (2028); **mean** 0.25 / 0.75 / 1.24%; p95 0.89 / 2.67 / 4.01%; 93% European. EMEA nights −0.36 / −1.07 / −2.03% | `11_regulatory_pending_items.csv`; EU AHA draft (9 Sep 2026); **EU Reg 2024/1028 applies 20 May 2026** (registration numbers, monthly platform data reporting) | No |
| **Macro** | nights | **zero.** 1,408 macro pairs tested, no incremental forecast value; nights macro-sensitivity is not distinguishable from zero | — | n/a |

### 2.2 Price levers (hit ADR)

Reported ADR y/y decomposes as **geographic mix + FX + within-region ex-FX**, and the within-region term further into
LOS mix, unit-size mix, seats dilution and a jointly unidentified pricing/sub-regional residual
(`research/notes/2026-09-07_adr-decomposition.md`, `model/ADR_decomposition.xlsx`).

| Lever | Term | 2025-26 magnitude | Lead indicator | Disclosed? |
|---|---|---|---|---|
| **FX on ADR** | ADR, mechanical | fitted `0.52 − 0.72 x broad USD y/y`, reconstructed to 1Q20 at **r 0.988**, raw RMSE 0.68pp. Realised: +2.7 (3Q25), +2.9 (4Q25), **+5.0 (1Q26), +1.3 (2Q26)** | FRED DTWEXBGS / DEXUSEU, daily, fully observable | Yes, stated each quarter |
| **Geographic mix** | ADR, negative every year since 2021 | −0.5, −2.8, −1.1, −1.2, **−1.6pp (2025)** and worsening. NA nights share 39.1% → 29.6%; LatAm+APAC 25.9% → 30.0% | 10-K Geographic Mix table (annual, hard) | Yes, annually |
| **Unit-size mix / Bedroom Nights** | ADR | measured **+0.63pp** on 29 markets (2Q26 window). The Street reads +2pp from the bedroom-nights disclosure; **bedroom-count elasticity is 0.23**, so a +2pp bedroom-night wedge is worth ~+1.26pp, not +2pp | "Bedroom Nights Booked +12%" vs nights +10% (new metric, 2Q26); Inside Airbnb size panel | New in 2Q26 — **one data point** |
| **Seats + hotel dilution** | ADR, negative | FY25 −0.18pp → **FY26 −0.48, FY27 −0.57, FY28 −0.62pp** base; ADR-bear (business-bull) −0.75 / −1.05 / −1.32 | tied to the new-business case; ticket prices assumed | No |
| **Length of stay** | ADR | 28+ share 20.2% (2022) → **13.4% (2025)**, −2 to −2.5pp a year; per-night ratios 1.00 / 0.966 / 0.852; term **+0.3pp a year** | calendar run-length panel; avg nights per booking (10-K, annual) | Share stopped 1Q24; avg nights/booking continues |
| **Party size / capacity** | ADR | capacity elasticity +0.49% per 1% capacity; party-size term in ADR ≈ **0.0**, no seasonal signal | review-based party-size panel (6 shards) in repo | No |
| **Like-for-like pricing** | ADR | **not measurable post-2023.** CPI lodging r +0.05, BEA hotels +0.01, MAR+HLT RevPAR +0.13 against ABNB ADR ex-FX on 2023Q1+ (all p≈1.00) | none that works | n/a |
| **Pricing tools / discounts / total-price display** | ADR (−), conversion (+) | total price display became the global **default Apr 2025** (was a Dec 2022 toggle); discount penetration in Airbnb's own quotes rose 10.9% (Mar 2026) → **31.4% (Aug 2026)**, median discount ~15% of the nightly subtotal | Inside Airbnb `price_quote_raw` — but **no year-ago comparison exists** and a taxes-line schema change contaminates it | No |
| **AI host-pricing model** | ADR | Chesky (2Q26): *"many multiples bigger than RNPL."* Zero quantification, zero launch date | none | No |
| **Single-fee repricing artefact** | ADR (mechanical, **unmodelled**) | if migrating hosts reprice to hold payout, listed prices rise **~14.8%** (payout-neutral) for that cohort and flow into ADR. Migration completes **15 Sep 2026 (ex-EEA) / 13 Oct 2026 (EEA+CH)** — *inside 3Q26 and 4Q26* | host-facing notices; Inside Airbnb listed-price panel | No |

### 2.3 Monetisation levers (hit take rate)

| Lever | Term | 2025-26 magnitude | Lead indicator | Disclosed? |
|---|---|---|---|---|
| **Single 15.5% host-only fee** | take rate (+) | arithmetic **+40 to +50bps on a fully migrated book** (split 14.1% guest + 3% host on a fee-inclusive GBV base ≈ 15.0%; single fee 15.5%). ~25% of listings at 1Q26, **~half at 2Q26**, all by end-2026. Rate went 15.0% → 15.5% on 1 Dec 2025 | published deadlines; `06_fee_timeline.csv`; listing-level fee data not available | Share disclosed; bps effect never quantified |
| **Host-fee pilot, 6-10% on host-originated direct links** | take rate (−) | announced **29 Aug 2026**. If it reaches 10% of nights at an 8pt discount that is **−0.8pt of blended take rate — larger than the entire single-fee benefit** | Skift 29 Aug 2026; scope undisclosed | Not in any filing |
| **Cross-currency / FX service fee** | take rate (+) | **+20bps y/y in 2025** (Mertz, 4Q24 call). Cross-currency ≈ **20% of GBV** (1Q25) | disclosed once each | Once, then dropped |
| **Travel insurance** | take rate (+), small | revenue +40% (4Q25), **+45% (1Q26)**; available in 12 largest countries | disclosed in some letters | Growth only, no level |
| **New-business incentives** | take rate (−) | take rate guided flat FY26 *"accounting for higher customer incentives related to new businesses"*: hotel price-match + up to 15% Airbnb credit; Delta SkyMiles 3 miles/$ (5 May 2026, "no negative take-rate impact") | credit expiry 31 Dec 2026 | Qualitative |
| **Hotels / Experiences / Services take-rate mix** | blended take rate (−/+) | hotels ~11% commission (assumed; "best-in-class", undisclosed), Experiences 20% host fee, Services 15% + $6 minimum, stays ~13.4% FY25. Hotels dilute, seats accrete, on tiny GBV | none | No |
| **Sponsored listings / ads** | revenue outside GBV | **$0 today.** "On the horizon" (Chesky, 18 Feb 2026); repo base case: 2027 launch, 0.3% of GBV by FY28 ($350m) | product announcements | No |
| **Long-term-stay fee reduction** | take rate (−) | lower guest service fee after 3 months on long stays (2023 Summer Release); LTS 13-17% of nights | LTS share (stopped 1Q24) | Stopped |
| **Take-rate guide reliability** | — | this is the **one guide type that has actually missed**: 4Q25 guided take rate "up slightly y/y" for 1Q26, delivered **−0.10pts**; 2Q25 guided 0.0 for 3Q25, delivered −0.69 | — | — |

### 2.4 FX, hedging and timing

- **Revenue FX lags spot by one to two quarters** because the USD value of a booking is largely fixed at booking while
  revenue lands at check-in. Stripping the hedge out and refitting on EUR/USD y/y: r 0.76 (lag 0), **0.86 (lag 1)**,
  0.58 (lag 2), n=14 (`research/notes/overnight/28_fx-hedge-disclosures.md`).
- **The hedge is small and currently a drag.** Designated notional $0.5bn (1Q23) → **$3.4bn (2Q26)**, ~46% of LTM
  non-USD revenue (56% of revenue is non-USD). Reclassified into revenue: **−$42m (3Q25), −$23m (4Q25), −$15m (1Q26),
  −$19m (2Q26)** = −1.1 / −0.9 / −0.7 / −0.6pp of revenue growth. The 2Q26 10-Q expects **~$26m of deferred net losses**
  to reach revenue over the next twelve months (~−0.2pp a quarter). AOCI on hedges flipped −$59m (4Q25) → **+$39m
  (2Q26)**. Policy: cash-flow hedges of forecast revenue "typically for up to 18 months", 1Q23 onward.
- **So "an approximate three percentage point FX tailwind after factoring in our hedging program" (3Q26 guide) is
  ~+3.2pp gross of the hedge.** The hedge is on the loss side. Any note that says the hedge creates the tailwind is
  wrong.
- **Regional FX pass-throughs:** EMEA 1.04 (independently re-tested at 1.07), LatAm 0.62 (0.63), APAC 0.86 (0.82), NA
  not identified, carried at 1.0.
- **4Q26 FX is already ~82% observed and turns negative.** Driver (two-prior-quarter EUR/USD mean) = +0.5% → fitted
  revenue FX **−0.4pp**, against +3.0pp guided for Q3. Guide-anchored step **−3.4pp**; fit-to-fit **−2.6pp**; LOO error
  ±2.3pp. Identical on strong-dollar, consensus and weak-dollar euro paths, because the driver is already in the past.
- **Margin read-across:** one point of FX on revenue ≈ **0.47 points of Adjusted EBITDA margin** at Airbnb's dollar cost
  base. So the Q4 FX step is ~−1.6 margin points before any marketing decision.

### 2.5 Disintermediation and referral cost

Airbnb's traffic is ~90% direct/unpaid and the app is 64% of nights. Booking disclosed **AI tools drove <1% of room
nights in 2Q26**; the Third Bridge AI expert (Booking ML/AI PM, 14 Aug 2026) puts ~3% of accommodation bookings moving
AI-native in 12-24 months with **no EBITDA impact** in that window. Repo scenario grid at a 5% referral fee: FY27 cost
0.38 / 1.14 / 2.28% of revenue; FY28 0.77 / 1.92 / **3.83%** (= 2.1 / 5.3 / 10.6% of Adjusted EBITDA). Google rolled
agentic hotel booking into AI Mode on **27 Aug 2026** with Booking, Expedia, Marriott, Hilton and others — **Airbnb is
not a launch partner, by choice**. The correct bear framing is *"AI converts 5-10% of Airbnb's free traffic into paid
traffic by 2028"* — a multiple story, not an earnings story. And the 6-10% host-fee pilot tells you what management
thinks a leaked booking is worth: **5-9 points of take rate**.

---

## 3. Guidance policy: how the range is built and communicated

### 3.1 The mechanics of the range

**The quarterly revenue range is a floor dressed as a forecast.** 19 scoreable revenue guides (4Q21-2Q26 targets):
15 of 19 finished **above the top** of the range, 0 below the bottom, mean beat vs midpoint **+2.54%**, median +2.52%
(`data/processed/overnight/02_guidance_ledger.csv`, `02_guidance_accuracy.csv`). Two trends matter:

| Era | Mean beat vs midpoint | Range width as % of midpoint |
|---|---|---|
| First 11 prints | **+3.04%** | 4.9% |
| Last 8 prints | **+1.86%** (median +1.79%) | 1.9% |
| 2Q26 → 3Q26 guide | — | **1.68%** ($4.69-4.77bn) |

Use the trailing-8 cushion, not the full history. 25th-75th percentile of the last 8: **+0.95% to +2.63%**.

Why the cushion is structurally small and shrinking: §1.4. Management can see 85-90% of the quarter on the booking
ledger when they set the range, so the range is mostly an FX-and-cancellation band, not a demand forecast. The three
narrowest beats in the series (+0.86%, +0.86%, +0.98%) are all 2024-25 prints.

**Guide types and their hit rates** (n=159 scored):

| Type | n | met/within | above | below | Read |
|---|---|---|---|---|---|
| Range (revenue $) | 39 | 11 | **28** | **0** | a floor |
| Bucket (nights/GBV) | 5 | 0 | **5** | 0 | **the most beatable line in the letter**; 4Q25 guided "mid-single digit" nights and delivered +9.8% |
| Floor ("at least") | 36 | 35 | — | 1 | +4.4pts of average cushion |
| Ceiling ("down slightly") | 14 | 12 | — | 2 | −0.95pts |
| Point ("approximately") | 22 | 3 at point | 14 | 5 | the misses are **all expense lines** |
| Directional | 43 | 35 | — | 7 | 5 of the 7 misses are in the company's favour |

**The guides that actually go wrong are monetisation and expense, not the top line:** FY24 SBC guided +20% then +25%,
delivered **+30.8%**; FY24 tax guided "mid-to-high teens" then ~20%, delivered 20.5%; 1Q23 S&M guided +150bps of
revenue, delivered +190bps; the take-rate guide missed in 3Q25 (−0.69 vs 0.0) and 1Q26 (−0.10 vs "up slightly").

**ADR direction calls go wrong when FX moves after the guide is set** — 2 of 17, both in 2023, both "slightly lower ADR"
that came in +0.2% and +1.4%. Model ADR from the FX basket and regional mix, never from the guide's ADR sentence.

### 3.2 The vocabulary, and what each word has meant

The letters guide nights and GBV in named buckets. The repo's bucket→range map (`02_guidance_ledger.py`) and the
realised outcomes:

| Phrase | Mapped range | Realised |
|---|---|---|
| "high-single-digit growth in Nights and Seats Booked" (4Q25 → 1Q26) | 7-9% | **9.15%** (above) |
| "low double-digit growth in Nights and Seats Booked" (2Q26 → 3Q26) | 10-12% | pending |
| "GBV to increase in the low teens" (4Q25 → 1Q26) | 12-14% | **19.18%** (above) |
| "GBV to increase in the low double digits" (1Q26 → 2Q26) | 10-12% | **15.74%** (above) |
| "year-over-year GBV growth to be in the mid teens" (2Q26 → 3Q26) | 14-16% | pending |
| "a moderate increase in ADR due to mix shift and price appreciation" | ADR floor >0 | 8 of 8 "ADR up" floors met |
| "nights growth to slightly decelerate" (1Q26 → 2Q26) | directional down | **accelerated 9.1% → 10.3%** (missed, in the company's favour) |
| "implied take rate… relatively in-line year-over-year" | ±0 | the only guide family that misses |
| "Adjusted EBITDA Margin to be down slightly compared to Q3 2025" | ceiling | 9 of 10 such ceilings met, by a mean of 1.4pts |
| "at least X%" (FY margin) | floor | **8 of 8 cleared**, FY24 by 140bps, FY25 by 60bps |

**The FY guide has only ever been raised, never cut, and the raise lands at the Q3 print.** FY24 margin 35.0% floor
(4Q23/1Q24/2Q24) → "approximately 35.5%" (3Q24) → 36.4% actual. FY25 34.5% floor → ~35% (3Q25) → 35.1% actual. FY26 is
already ahead of that cadence: margin "stable y/y" (4Q25) → "at least 35%" (1Q26) → **"at least 35.5%" (2Q26)**; and the
first-ever FY revenue-growth guide went "at least low double digits" (4Q25) → "low to mid teens" (1Q26) → **"at least
mid teens" (2Q26)** against 1H26 actual of +17.1%.

### 3.3 How far out they guide, and what they will not say

Numeric guides per print: **0-1 (2020-21) → 8-10 (2024-26)**. Horizon collapsed to one quarter when the revenue $ range
appeared (3Q21); FY margin became a hard floor at 4Q23; the FY revenue-growth guide is brand new (4Q25). Two-quarter-
ahead guides exist but are rare and unreliable (1Q24 promised 3Q24 acceleration and got deceleration).

**On FY2027 management has said nothing.** Asked directly by Eric Sheridan (Goldman) on the 2Q26 call about long-term
incremental margins: *"So I'm not going to give you a specific guide for 2027 and beyond, but I think looking at our
track record, you can even see a couple of things."* (`data/processed/abnb_declined_to_quantify.csv`). The FY27 guide
arrives with the Q4 print, **~Feb 2027 — after the competition finals.** The pitch is therefore a bet on the *Q4 guide
and the FY26 raise* on 5 Nov, plus the Street's FY27 revision path, not on an FY27 guide.

The standing refusal list is itself a tell — 36 catalogued refusals, clustered on: take-rate detail (3), market-level
economics of expansion markets (3), contribution margin of new businesses (5), long-term margin target (2),
consensus/guidance detail (7). Mertz's 2Q25 answer on seats is the template: *"we have not historically broken out
nights booked versus experiences booked. We were not going to do that today. What I can tell you is that the seats
booked today are indeed immaterial."*

### 3.4 The 2026 guidance calendar

| Date | Event | What is guided |
|---|---|---|
| 12 Feb 2026 | 4Q25 print | 1Q26 range; **first-ever FY26 revenue-growth guide**; FY26 margin "stable" |
| 7 May 2026 | 1Q26 print | 2Q26 range; FY26 raised to "low to mid teens" / "at least 35%" |
| **6 Aug 2026** | 2Q26 print | **3Q26 range $4.69-4.77bn (+15-17%, ~3pt FX after hedging)**; FY26 raised to "at least mid teens" / "at least 35.5%"; stock +17.4% |
| **~5 Nov 2026** | 3Q26 print | **4Q26 range; expected FY26 raise (base rate: the Q3 print is when the raise lands)** |
| ~Feb 2027 | 4Q26 print | **FY27 guide** — the first, and outside the pitch window |

### 3.5 The guide does not predict the print-day move — and that is a finding, not a gap

17 regressions of day-1 and day-20 excess returns on the beat, the raw guide vs naive, the cushion-aware guide
surprise, the FY guide action and the margin-guide direction. **Every one has a negative leave-one-out R².** The best
in-sample (day-20 vs cushion-aware guide surprise, R² 0.166, t 1.61) has LOO R² −0.135. The revenue beat's *sign* hit
rate against the day-1 excess is **0.37 — below a coin flip**. The only feature with a respectable sign hit rate is
**nights acceleration: 0.79 (15/19)**. And the one executable rule that survived is asymmetric: "guide below Street" →
20-day drift **9/9 negative, mean −4.2% on a next-open entry** (n=9, base-rate p 0.038).

Mechanism: everyone knows the range is a floor, so beating it is priced. The reaction is set by the volume trajectory
and by whether the *next* guide is above or below where the Street sits.

---

## 4. What changed in 2025-2026 that a 2021-2024-trained model would get wrong (dated)

| Date | Change | Why a 2021-24 model breaks |
|---|---|---|
| 4Q23 | FY margin guide becomes a hard floor ("at least 35%"), reiterated all year | the guide's information content changes; a "beat" is now structural |
| 1Q24 | **Cross-border share and growth, long-term-stay share, active-listings growth % all last disclosed** | any model needing those series has 2024 as its last hard data point |
| 4Q23 | High-density urban share last disclosed | same |
| 3Q24 | **Regional nights growth stops being an exact % and becomes buckets** for all four regions | `10_regional_panel_quarterly.csv` is low/high/mid bands from 3Q22; the regional build has ±1.1pp reconciliation error by construction |
| Mid-2024 | FX service fee on cross-currency transactions launched | +20bps of take rate in 2025 with no volume driver — a level shift in `tau` |
| 13 May 2025 | Summer Release: Services + Experiences relaunch; **KPI renamed "Nights and Seats Booked"** | seats enter the denominator of both nights and ADR. ADR is now GBV / (nights + seats). Seats dilution −0.18pp (FY25) → **−0.48 (FY26), −0.57 (FY27)** |
| Q3 2025 | **RNPL launches (US)** | breaks the unearned-fee backlog ratio, lengthens lead times, raises cancellations 16% → 17%, shifts mix to larger homes. All four are new regimes |
| Oct 2025 | **Cancellation-policy redesign: Strict retired, migration to Firm** | this is what made RNPL eligible inventory; policy mix is now a demand lever |
| Oct 2025 | **Single 15.5% host-only fee migration begins** (software-connected hosts first) | changes who pays, when the fee cash arrives, and the listed price. ~25% of listings 1Q26, ~50% 2Q26 |
| 1 Dec 2025 | Single fee rate steps 15.0% → 15.5% | a +50bp rate change inside the migration |
| 4Q25 | **First-ever FY revenue-growth guide**; first-time-booker growth disclosed | new guide family with n=3 |
| 4Q25 | AI customer support: ~a third of contacts self-resolved → >40% (1Q26) → ~45% (2Q26); support cost per booking −16% | margin now has an opex engine unrelated to volume |
| 12 Feb 2026 | Q4'25 print: "Project Hawaii" — small teams shipping hundreds of conversion improvements | attribution becomes diffuse by design |
| 17 Feb 2026 | **RNPL goes global** | the US anniversary (3Q26) and the global anniversary (1Q27) are different laps |
| 12-19 Mar 2026 | IG ratings (S&P A-, Moody's Baa1); **$2.5bn senior notes**; 2026 converts repaid | capital structure changes; interest income falls |
| 20 May 2026 | **EU Regulation 2024/1028 applies**: mandatory registration numbers, platform verification, monthly data reporting via national single digital entry points | first EU-wide compliance regime; enables enforcement at scale |
| 20 May 2026 | 2026 Summer Release: boutique/independent hotels in 20 cities with a **price-match guarantee and up to 15% Airbnb credit**; car rentals, airport pickup, luggage storage, grocery; AI review highlights; global support assistant in 11 languages | new-business incentives now sit *against* the take rate |
| 2Q26 | **"Bedroom Nights Booked" introduced** (+12% vs nights +10%) | a brand-new metric with exactly one observation, being mapped 1:1 into ADR by the Street. The elasticity is 0.23, not 1.0 |
| Jul 2026 | RNPL eligible booking types expanded; most remaining hosts to migrate to the single fee during 2026 | Q3 has a US lap *and* fresh treatment expansion simultaneously |
| 27 Aug 2026 | Google agentic hotel booking in AI Mode; **Airbnb not a launch partner** | first agentic channel at scale |
| **29-31 Aug 2026** | **Host-fee pilot: 6-10% (vs 15.5%) on bookings hosts bring via their own links** | the first explicit take-rate concession. Caps the fee-migration tailwind |
| 1 Sep 2026 | Pepijn Rijvers (13 yrs Booking.com, ex-Viator president) named CBO over Homes, Hotels, Global Markets; Dave Stephenson leaves at end-2026 | hotels-first mandate; second C-suite exit in nine months |
| **15 Sep / 13 Oct 2026** | Single-fee migration deadlines: ex-EEA / EEA+CH, by host residence | **inside 3Q26 and 4Q26**. Listed prices may rise ~14.8% for the migrating cohort if hosts reprice to hold payout — unmodelled anywhere |
| 31 Dec 2026 | 15% hotel credit expires | 4Q26 is the last subsidised hotel quarter |

Structural regime changes a 2021-24 panel cannot see: (i) the take rate is now a *policy* variable with both a positive
(single fee) and a negative (direct-link pilot) lever pulling at once; (ii) the backlog indicator has a ~16% dated
distortion; (iii) the ADR denominator changed; (iv) nights are increasingly a blend of homes, hotel rooms and seats
with different prices and different take rates.

---

## 5. Current state of play, 11 September 2026

### 5.1 2Q26 actuals (reported 6 Aug 2026)

| Metric | 2Q26 | y/y | Note |
|---|---|---|---|
| Nights and Seats Booked | **148.3m** | **+10.3%** | accelerated from 9.1% in 1Q26, against a guide of "slightly decelerate" |
| GBV | **$27.2bn** | **+15.7%** | +15% ex-FX |
| ADR | **$183.73** | **+5.3%** | **+4% ex-FX, +1.3pp FX** |
| Revenue | **$3,608m** | **+16.5%** | **+13% ex-FX, ~+4pp FX**; above the $3.54-3.60bn range |
| Take rate (quarterly) | **13.26%** | +0.09pt | LTM 13.2% |
| Adj. EBITDA / margin | **$1,261m / 35.0%** | +1.3pts | |
| Regional nights | NA **+8%**, EMEA **+8%**, LatAm **+20%**, APAC **+18%** | | bucket midpoints, not measured |
| Unearned fees | **$2,831m** | **−0.9%** | restated for RNPL/fee mix: ~+15.4% |
| Funds held | **$12,224m** | **+10.5%** | |
| App share of nights | 64% | app nights +23% | |
| First-time bookers | — | **+11%** | "highest in four years" |
| Bedroom Nights Booked | — | **+12%** | new metric |
| Experiences supply | — | **+80%** | |
| Single fee | ~50% of listings | | ~25% at 1Q26 |
| RNPL | >20% of GBV | ~70% adoption when offered | |
| 1H26 | revenue +17.1%, adj. EBITDA margin 28.32% (vs 27.20% 1H25) | | |

Stock reaction: **+17.4% on 7 Aug 2026.**

### 5.2 The 3Q26 guide (given 6 Aug 2026, verbatim from the 2Q26 letter via `02_guidance_ledger.csv`)

| Item | Guide |
|---|---|
| Revenue | **"$4.69 billion to $4.77 billion"**, **"year-over-year growth of 15% to 17%, inclusive of an approximate three percentage point FX tailwind after factoring in our hedging program"** |
| Nights and Seats | **"low double-digit growth"** (10-12%) |
| GBV | **"mid teens"** (14-16%) |
| ADR | **"a moderate increase in ADR due to mix shift and price appreciation"** |
| Take rate | **"relatively in-line year-over-year"** (3Q25 = 17.88%) |
| Adj. EBITDA margin | **"down slightly compared to Q3 2025"** (50.1%), **"due to timing of investments"** |
| FY26 revenue growth | **"at least mid teens"** (raised from "low to mid teens") |
| FY26 adj. EBITDA margin | **"at least 35.5%"** (raised from "at least 35%") |
| FY26 tax rate | **"high teens"** (17-19%) |

**Management's stated FX assumption for Q3 is +3pp after hedging** (~+3.2pp gross; the hedge contributes ~−0.2pp).

### 5.3 Where the Street is

| Period | Zacks (4 Sep 2026) | S&P Global (3 Sep 2026) | n |
|---|---|---|---|
| 3Q26 revenue | **$4,740m** (range 4,720-4,770) | — | 7 |
| 4Q26 revenue | **$3,200m** (range **3,050-3,700**, a 21% spread; the mean is skewed by one high estimate) | — | 10 |
| FY26 revenue | **$14,100m** (13,960-14,210) | **$14,160m** (13,800-14,300) | 8 / 43 |
| FY27 revenue | **$15,730m** (14,990-16,290) | **$15,760m** | 13 |
| FY26 adj. EPS | $5.23 | $5.28 | 13 / 43 |
| NTM price target | — | **$178.96** (125-220) vs $181.94 spot | 46 |

At the 6 Aug guide date, the Street's next-quarter number was **$4,610m (LSEG)**, so the guide came in **+2.6% above
consensus** — the feature that is frozen into the pre-registered 5 Nov card (`20_frozen_q3_2026.csv`).

No published 3Q26 nights or adjusted-EBITDA consensus was retrievable. The implied nights bar from the breakeven file
is **144-146m**; the designated frozen forecast is **+1.83% nights surprise on a 145m bar = 147.6m**, and **+1.37%
revenue surprise on $4,740m = $4,805m**.

### 5.4 What management said about H2 comps

- Mertz has flagged **"tougher comps in the back half"** (3Q25 call context) — the RNPL US anniversary from 3Q26 and the
  global anniversary from 1Q27.
- The 1Q26 call's *"approximately 3 points of nights growth and 4 points of GBV growth"* is the bundle (RNPL +
  cancellation redesign + simplified fees), not RNPL alone, and is the number the lap arithmetic must respect.
- The 2Q26 guide of "low double digits" nights **was set on 6 August with July bookings in hand**, so it already
  contains management's own view of the lap and of the World Cup residual (the tournament ended 19 Jul 2026, so its
  contribution sits in July bookings only; its lap lands in 3Q27).
- Offsets management has named: global RNPL ramp, the July 2026 eligibility expansion, hotels growing ~3x homes,
  first-time bookers +11%, Experiences supply +80%.

### 5.5 The team's own numbers, for the record

| | 3Q26 | 4Q26 | FY26 | FY27 |
|---|---|---|---|---|
| Driver model base | **$4,801m (+17.2%)** | **$3,145m (+13.2%)** | **$14,233m** | **$15,842m** |
| H1→H2 bridge (lagged-GBV conversion) | $4,778-4,846m (pt $4,804m, +17.3%) | $3,144-3,189m (+14.0%) | $14.26bn (+16.5%) | — |
| Q4/FY27 bridge (FX-anchored walk) | — | **$3,111m (+12.0%)**; bear $2,961m / bull $3,241m | +15.7% | **+11.6% ($15,804m)**; bear +3.2% / bull +17.0% |
| Cushion-adjusted from the guide | $4.82bn (+17.6%) on trailing-8; $4.85bn on full history | — | — | — |
| Street | $4,740m | $3,200m | $14,100-14,160m | $15,730-15,760m |

Three constructions land within a point on FY27. **The disagreement with the Street is not the annual number, it is the
shape:** base-case 1Q27 +9.9% against 1Q26's +17.9%, and 2Q27 +10.7% against +16.5%. If the Street phases FY27 like
FY26, its first half is too high.

**What a good Q4 guide looks like:** midpoint implying ≥+14% y/y (≥$3.17bn), nights guided "low double digit" again,
FY26 revenue growth raised a notch to "high teens" or a point estimate, and the FY26 margin floor replaced by
"approximately X%" with X ≥ 36%.

**What a bad one looks like:** a midpoint implying <+12%, nights dropped back to "high-single digit", the FY26 revenue
guide merely reiterated (the first non-raise since the guide existed), or — the real red flag — a **take-rate-down guide
alongside a margin ceiling**, which would say monetisation and cost are moving the wrong way together.

**And the trap:** the base case is a Q4 midpoint near **$3.05-3.10bn**, roughly **4% below the current $3.20bn Street
mean**, on FX arithmetic that is already 82% observed. If that guide arrives **without an FX sentence**, it is the
"guide below Street, misread as demand" setup — 9 of 9 negative 20-day drifts, mean −4.2%.

---

## 6. Unknowns that matter, and how an insider triangulates them

| # | Unknown | Why it matters | Triangulation |
|---|---|---|---|
| 1 | **Booking lead-time distribution** | sets `m(b,q)`; both invisible pattern breaks in five years were lead-time changes | Inside Airbnb calendars captured **monthly** (the CDN retains ~1 year; every missed month is unrecoverable): measure unavailable→available transitions at matched days-to-arrival. Cross-check against nights-per-booking in the 10-K and the ALOS bucket build |
| 2 | **RNPL cohort cancellation curve** | 1pt of platform cancellation = ~0.75-0.82pp of quarterly nights growth | A property-manager / channel-manager reservation-event panel with booking date, stay dates, cancellation date, policy and RNPL flag. Use the staggered rollout (US-only → Feb 2026 global → Jul 2026 expansion) as a cohort DiD. Report conditional (not ultimate) cancellation probability, handle right-censoring |
| 3 | **Whether the single-fee migration, not just RNPL, is depressing unearned fees** | decides whether the 16% restatement is permanent or reverses when migration completes (15 Sep / 13 Oct 2026) | Regress the dated distortion series (0.9 / 3.8 / 16.2 / 16.5%) on the disclosed single-fee penetration (0 / 15 / ~25 / ~50%) and the RNPL GBV share. Ask on the call. Check the 3Q26 10-Q's unearned-fee balance against a post-migration prior |
| 4 | **Hotel commission rate and hotel night volume** | hotels dilute both ADR (0.81x a home night) and take rate (~11% assumed vs 13.4% stays) while growing ~3x homes | Only anchors are "single-digit % of nights" and "3x homes". Triangulate via the Lark Hotels / boutique partnership counts, HotelTonight-era disclosures, and OTA commission benchmarks (Booking's net take ~14.5%) |
| 5 | **Seats volume and ticket price** | the whole seats-dilution term (−0.48 to −1.32pp of ADR) rests on assumed $75/$120 tickets | Sensitivity is already gridded ($50-100 / $80-180): FY27 drag −0.30 to −1.01pp. Push for an absolute Experiences number on 5 Nov; supply +80% with no volume figure is the tell |
| 6 | **The "pricing + sub-regional mix" residual (+3.6pp of 2025 ADR)** | the largest single term in ADR and it is **jointly unidentified** — Airbnb discloses no country-level ADR | Bound it: expansion-market origin nights ~2x core and those markets are lower-ADR, so it carries a real negative mix component. Backfill AirDNA US STR ADR (the only same-asset-class price series; four months exist). Do **not** use CPI lodging, BEA hotels or MAR/HLT RevPAR — all have r≈0 against ABNB ADR ex-FX post-2023 |
| 7 | **Whether Bedroom Nights Booked is repeated on 5 Nov** | one data point; the Street maps it 1:1 into ADR; the true elasticity is 0.23 | Watch the letter. Airbnb has form for dropping metrics that stop flattering: the 1BR-vs-hotel comparison died after 4Q23, LTS share after 1Q24, cross-border after 1Q24, listings growth after 1Q24 |
| 8 | **Scope and take-up of the 6-10% direct-link host-fee pilot** | at 10% of nights and an 8pt discount it is **−0.8pt of blended take rate — bigger than the whole single-fee benefit** | Ask for the blended take-rate bridge. Monitor host forums and PMS vendor notices; check whether listings begin carrying off-platform links |
| 9 | **Point-in-time consensus** | the only executable rule found (guide-below-Street → −4.2% over 20 days) needs consensus *as of the print*, not a later vintage | Bloomberg/LSEG PIT pull. Zacks $4,740m (4 Sep) is a **later vintage** than the $4,610m LSEG figure that set the 6 Aug guide-vs-Street feature; do not mix them |
| 10 | **Regional nights are bands, not numbers** | the whole regional build inherits ±1.1pp of reconciliation error, and WS10's LatAm/APAC ADR index was **swapped** (LatAm nights share understated by 3.3pp) | The 10-K discloses regional nights, GBV and revenue **annually and exactly** (2025: NA 158m/$40.3bn/$5,196m; EMEA 215m/$34.2bn/$4,729m; LatAm 90m/$8.5bn/$1,160m; APAC 70m/$8.3bn/$1,156m). RAS the quarterly bands to the annual totals — that correction is already made in `data/processed/adr/` |
| 11 | **Host earnings (last disclosed 2023: >$57bn)** and **active-listing growth %** (last given 1Q24) | both stopped **exactly** when the take-rate migration began | Press on 5 Nov. Derive host earnings as GBV less fees less taxes; the 78%-of-GBV 2023 ratio is the anchor |
| 12 | **AI referral economics** | no AI platform has published accommodation referral terms; the 3-8% fee grid is an analyst assumption | Anchor on metasearch CPC economics and on what Airbnb itself pays to keep a booking (the 5-9pt implied value of the direct-link pilot) |

---

## 7. How this note changes the model

1. **Stop forecasting quarterly take rate as a monetisation assumption.** Forecast `tau_eff` on an LTM basis (13.2%)
   and let the quarterly print fall out of the booking→check-in transition matrix. Carry the fee levers (single fee
   +40-50bps on a fully migrated book; direct-link pilot −0 to −80bps; FX service fee +20bps in 2025) as changes to
   `tau_eff`, not to the quarterly ratio.
2. **Restate unearned fees before using them.** The dated distortion is 0.9 / 3.8 / 16.2 / 16.5% for 3Q25-2Q26. On the
   restated series the backlog grows in line with GBV and the indicator works — on **nights**, where it beats naive
   (0.90x) and AR(1) (0.65x); not on revenue dollars, where it does not (1.17x / 1.28x).
3. **Treat printed nights as a net flow with a cancellation term.** Build `N_q = G_q − Σ_b C(b,q) + alterations`.
   Without a cohort panel you cannot separate the terms, so at minimum carry the cancellation rate as an explicit
   named assumption (16% → 17% disclosed) rather than burying it in a growth rate.
4. **Never subtract management's "+3 points" as an RNPL-only lap.** It is a three-feature bundle, and two of the three
   (global RNPL ramp, single-fee completion) are still ramping into the lap.
5. **The FX term is the only arithmetic one — state its observed share.** 4Q26 revenue FX is ~82% determined at −0.4pp
   against +3.0pp guided for Q3; the −3.4pp step is invariant across euro paths.
6. **Model ADR from FX + geographic mix + a bounded within-region term, and carry the seats-dilution drag explicitly.**
   Reported ADR ex-FX of +3-4% is consistent with home pricing of +3.5-4.5%.
7. **Put the Street beside the base case, not inside it.** The Q4 Street mean ($3,200m) has a 21% range and one high
   estimate; the median is nearer $3.15bn.

---

## 8. Sources

### Repo paths opened for this note
- `data/processed/overnight/02_kpi_panel_quarterly.csv` (24 x 119), `02_kpi_panel_long.csv` (1,050 sourced rows)
- `data/processed/overnight/02_guidance_ledger.csv` (194 statements), `02_guidance_tells.csv`, `02_guidance_cushion_series.csv`
- `data/processed/abnb_backlog_indicators.csv`, `data/processed/abnb_declined_to_quantify.csv` (36 refusals)
- `data/processed/overnight/06_fee_timeline.csv`, `06_elasticities.csv`
- `data/processed/overnight/04_current_consensus.csv`, `20_frozen_q3_2026.csv`, `08_backlog_tests.csv`
- `data/processed/booking_curves_by_market.csv`, `booking_curve_daily.csv`, `airbnb_nights_per_booking.csv`,
  `abnb_forward_bookings_pooled.csv`
- `research/airbnb_earnings_call_study.md` (22 calls, KPI table, §8.2 RNPL, §8.3 seasonality, §8.4 backlog)
- `research/notes/2026-09-04_management-timeline.md`, `research/notes/2026-09-07_adr-decomposition.md`,
  `research/notes/2026-09-09_seats-dilution.md`, `research/notes/2026-09-09_revenue-by-line.md`,
  `research/notes/2026-09-09_los_synthesis.md`, `research/notes/2026-09-10_rnpl-conversion-framework.md`,
  `research/notes/2026-09-10_h1-to-h2-bridge.md`, `research/notes/2026-09-07_fee-churn-catalyst.md`,
  `research/notes/2026-09-07_fee-churn-recent-followup.md`, `research/notes/2026-09-05_third-bridge-transcripts.md`
- `research/notes/overnight/02_kpi-panel-and-guidance-ledger.md`, `03_management-language-and-stock.md`,
  `11_competition-supply-and-overlays.md`, `28_fx-hedge-disclosures.md`, `29_q4-fy27-bridge.md`
- `research/regulatory/earnings_digest.md`
- `model/ABNB_driver_model.xlsx`, `model/ADR_decomposition.xlsx`, `model/ABNB_revenue_by_line.xlsx`
- `docs/RNPL_HANDOFF.md`

### Filings (retrieved 2026-09-11 from SEC EDGAR, CIK 0001559720)
- **FY2025 Form 10-K**, filed 12 Feb 2026, accession 0001559720-26-000004, `abnb-20251231.htm` — Revenue Recognition
  policy; Funds Receivable and Funds Payable / Pay Less Upfront; Derivative Instruments and Hedging; Item 1 Seasonality;
  MD&A "Key Business Metrics and Non-GAAP Financial Measures" (Nights and Seats Booked, GBV definitions); MD&A
  "Geographic Mix" table (2024/2025 regional nights, GBV, revenue, nights per booking).
- **2Q26 Form 10-Q**, filed 6 Aug 2026, accession 0001559720-26-000027,
  https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm — balance sheet (unearned fees
  $2,831m; funds receivable/payable $12,224m); derivatives note (designated notional $3.1bn → $3.4bn; AOCI −$59m → +$39m;
  $34m reclassified to revenue in 1H26; **~$26m of deferred net losses expected to be reclassified to revenue over the
  next twelve months**); revenue by geography (2Q26 NA $1,594m, EMEA $1,425m, LatAm $291m, APAC $298m; 1H26 $6,286m).
- **1Q26 Form 10-Q**, filed 7 May 2026, accession 0001559720-26-000014.
- **2Q26 shareholder letter** (8-K Ex. 99.1), https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm
- Earnings-call transcripts, Airbnb IR: Q3'25 (https://s26.q4cdn.com/656283129/files/doc_financials/2025/q3/CORRECTED-TRANSCRIPT_-Airbnb-Inc-ABNB-US-Q3-2025-Earnings-Call-6-November-2025-5_00-PM-ET.pdf),
  Q4'25 (…/2025/q4/Airbnb-Q4-25-Earnings-Call-Transcript.pdf), Q1'26 (…/2026/q1/Airbnb-Q1-26-Earnings-Call-Transcript.pdf);
  Q2'26 public fallback https://www.fool.com/earnings/call-transcripts/2026/08/13/airbnb-abnb-q2-2026-earnings-call-transcript/

### Web (retrieved 2026-09-11 unless dated otherwise)
- Single-fee migration deadlines **15 Sep 2026 (ex-EEA) / 13 Oct 2026 (EEA+CH)**, software-connected hosts fully
  migrated by 13 Apr 2026, rate 15.0% → 15.5% on 1 Dec 2025: RentalScaleUp (https://www.rentalscaleup.com/airbnb-host-fees/),
  Hostaway, Hostfully, Rove Travel, Airbnb host notice https://www.airbnb.com/resources/hosting-homes/a/simplifying-airbnb-service-fees-746
  and https://www.airbnb.com/resources/hosting-homes/a/simplifying-service-fees-on-airbnb-771
- 2026 Summer Release (20 May 2026): https://news.airbnb.com/airbnb-2026-summer-release; TheNextWeb; Skift.
- RNPL: https://news.airbnb.com/reserve-now-pay-later (14 Aug 2025); https://news.airbnb.com/reserve-now-pay-later-is-now-available-worldwide (17 Feb 2026).
- **EU Regulation (EU) 2024/1028 on data collection and sharing for short-term accommodation rental services — applies
  from 20 May 2026**: https://eur-lex.europa.eu/eli/reg/2024/1028/oj/eng
- EU Affordable Housing Act draft leaked 4 Sep 2026, presented 9 Sep 2026: Reuters; https://skift.com/2026/09/04/european-commission-short-term-rental-crackdown/
- Host-fee pilot 6-10% on host-originated links, 29 Aug 2026: https://skift.com/2026/08/29/airbnb-is-testing-lower-fees-for-hosts-who-bring-their-own-guests/
- Q2'26 print and guide coverage: https://www.cnbc.com/2026/08/06/airbnb-abnb-q2-earningsreport.html; guide of
  $4.69-4.77bn against a then-consensus of ~$4.605bn.
- Pepijn Rijvers appointment (1 Sep 2026): https://skift.com/2026/09/01/airbnb-names-ex-booking-com-hotel-boss-and-viator-president-as-chief-business-officer/
- Consensus: Zacks detailed earnings estimates (4 Sep 2026); stockanalysis.com / S&P Global Market Intelligence (3 Sep 2026).

### Data-quality flags raised by this note
- `02_kpi_panel_quarterly.csv` column `single_fee_pct` carries **15.5 at 4Q25**, which is the *fee rate*, not the share
  of listings migrated (the letters give ~25% at 1Q26 and ~50% at 2Q26). The long panel's source quote confirms it:
  *"to a 15.5% single service fee"*. **Rename or re-key before anyone regresses on it.**
- The 2Q26 letter HTML contains filed OCR artefacts ("ee ff ctive"); quotes reproduce the filed text verbatim.
- The 2Q26 row of `abnb_backlog_indicators.csv` has no `next_q_revenue`, so its coverage ratio is blank; the 0.599
  figure in §1.4-1.5 uses the **guide midpoint** as the denominator and is conditional on the guide being met.

*This document is research, not investment advice.*
