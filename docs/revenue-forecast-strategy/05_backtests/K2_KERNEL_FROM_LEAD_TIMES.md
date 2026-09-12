# K2 — The recognition kernel measured bottom-up from booking lead times

**Task:** measure phi_k, the share of a stay quarter's revenue that was booked k quarters
earlier, from *booking behaviour* rather than by fitting 22 quarters of revenue.
**Author's note:** this is the independent arm of a two-arm test. The time-series arm (K1)
was not read and is not referenced except to state the number it is being compared against.

**Code:** `analysis/src/forecast_methods/kernel_leadtime_v2/K2_0{1..6}_*.py`
**Outputs:** `data/processed/forecast_methods/kernel_leadtime_v2/`
**Figure:** `K2_leadtime_cdf_by_season.png`

---

## 1. Plain-language summary

**The source.** There is exactly one dataset on this machine that contains a real booking
date next to a real stay date: the Melbourne short-term-rental daily panels from Harvard
Dataverse `doi:10.7910/DVN/1XPDEU` ("To Airbnb: A Question of Revenues"). They are
property × calendar-night records with `Status`, `Price`, `Booked Date` and `Reservation ID`,
covering 2014-10-01 to 2017-02-28, 11.09m unique property-nights after de-duplicating the two
overlapping panels. Collapsed to the reservation grain and restricted to a clean 12-month
window this gives **268,110 reservations with an observed booking-to-check-in lead time**.
Everything else in the tree measures *blocked* nights, not *booked* ones, and cannot do this
job — see §6.

**The lead-time picture.** Airbnb booking is a short-dated business with a long thin tail.
Per booking, the median lead is **26 days** and the mean **46 days**. Per booking *dollar*
the median is **36 days** and the mean **58 days**, because long, expensive, multi-night
stays are booked much further ahead. That value-weighted 58 days ≈ 1.9 months sits just
under the **2.0–2.6 months** implied independently by Airbnb's own balance sheet (opening
unearned fees ÷ quarterly revenue, 0.66–0.88 quarters). Two completely unrelated sources —
a 2016 Melbourne reservation panel and Airbnb's 2020-25 unearned-fee disclosure — agree on
the central tendency. That is the single most reassuring fact in this note.

**The measured split by season.** Because revenue is recognised at check-in, a stay
quarter's revenue *is* its realised stays; grouping them by the quarter in which they were
booked gives phi directly. Value-weighted, in northern-hemisphere seasonal roles:

| stay quarter | phi_0 (in-quarter) | phi_1 | phi_2 | phi_3+ | **booked before the quarter began** |
|---|---|---|---|---|---|
| **Q3** peak summer | **0.463** | 0.389 | 0.095 | 0.052 | **53.7%** |
| **Q4** | **0.502** | 0.353 | 0.117 | 0.028 | **49.8%** |
| **Q1** winter trough | **0.558** | 0.314 | 0.100 | 0.027 | **44.2%** |
| **Q2** | **0.498** | 0.361 | 0.082 | 0.059 | **50.2%** |

**The headline answers.** About **54% of a Q3 stay quarter's revenue is already booked before
the quarter begins** — 39 points of it in Q2 and 15 points two or more quarters earlier.
For Q4 the figure is **50%**, split 35 points from Q3 and 15 points from earlier. Peak summer
is the most forward-booked quarter and the winter trough the least: the in-quarter share
swings roughly **10 points** across the seasonal cycle, which is a bigger seasonal effect than
most kernels in this repo allow for.

**Dollar weighting matters, and always in the same direction.** Moving from a per-booking to
a per-dollar weighting shifts about **10 points** of weight out of the current quarter into
earlier ones (pooled phi_0 falls from 0.60 to 0.50). Longer stays are booked further ahead
(mean lead 37 days for 1–2-night stays, 68 days for 28+-night stays) and they carry more
dollars per booking. Any kernel calibrated on booking *counts* will be too short.

**The survival adjustment runs the other way, and partly cancels the dollar effect.** The STR
panel only records stays that actually happened, so the phi above is *already* net of
cancellation — it is the revenue weight, which is what you want. But the GBV line Airbnb
reports is struck at booking. Grossing the same cohort back up to booking time with a
lead-dependent cancellation hazard calibrated to Airbnb's ~16% platform rate, GBV's own
distribution is longer-dated than the revenue it eventually produces: for Q3 the two-or-more-
quarters-ago bucket is **17.4% of the GBV cohort but only 14.7% of the revenue**. So the
weight a modeller should put on GBV_{q-2} is about **2.7 points lower** than that GBV's raw
share, and the gap widens with the cancellation rate. RNPL makes this worse in both
directions at once — it lengthens lead times *and* raises cancellations.

**Recommended prior.** Use the value-weighted table above, with the bands in §3, as a prior
on phi. It puts **phi_0 in the 0.46–0.56 range depending on season, centred near 0.50**. That
is materially *higher* than the 0.23–0.41 the time-series arm reports and materially *lower*
than the ⅔–⅓ kernel used elsewhere in the repo. If the two arms must be reconciled, note that
the bottom-up estimate is a *stay-timing* measurement and carries no macro or supply
confound, while the time-series fit is estimated on 22 quarters spanning COVID.

---

## 2. What had to be fixed to get a clean measurement

Two data problems dominate this exercise and both bias lead times **downward** if ignored.

**(a) The booking date is not captured from the start of the panel.** `Booked Date` is
populated only on `R` (reserved) rows and only from **2015-08-17**. Coverage by stay month
ramps 14.6% (Aug-15) → 66% (Sep-15) → 90.5% (Nov-15) → 94%+ (Dec-15 on). That ramp is not
patchy collection: it is exactly the fraction of the lead distribution that fits inside the
elapsed window, which is how we identified the mechanism.

**(b) There are two capture regimes with different forward horizons.** Comparing the modelled
and observed maximum lead month by month recovers the rule exactly:

> a reservation's booking date is captured **iff** `booked_date >= 2016-02-05`
> **or** (`booked_date >= 2015-09-01` **and** `lead <= 180`)

so the largest lead observable for a stay on day *d* is
`W(d) = max(d − 2016-02-05, min(180, d − 2015-09-01))`.
Modelled `W` reproduces the observed maximum lead in every stay month to within a day or two
(208 / 238 / 269 / 299 / 330 / 359 for Aug-16…Jan-17) and only **0.25%** of reservations
violate it. Before 2016-02-05 the vendor evidently saw only ~180 days forward; after it, the
full ~365-day calendar.

Ignoring this is not a small matter: the naive mean lead is **28.7 days** on stays with a
short window versus **52.3 days** on stays with a long one. The whole "are lead times
lengthening?" question can be manufactured out of this artifact alone.

**What we did.** Restrict to a 12-month window (stays **2016-03-01 → 2017-02-28**, each
calendar month appearing exactly once, `W` from 180 to 389 days); correct residual truncation
with the Lynden-Bell / Efron-Petrosian NPMLE and inverse-probability weights `1/F(W)`; and
build phi by integrating a per-stay-month lead-time CDF over the days of the quarter rather
than by counting booking-quarter labels, so that every quarter is treated identically.

**What is and is not identified.** For a stay at offset *a* in its quarter,
phi_0 = F(a) with a ≤ 91, and phi_0+phi_1 = F(a+91) with a+91 ≤ 182. Every stay month sees
leads out to at least 174–180 days, so **phi_0, phi_1 and the combined phi_2+phi_3 are
identified for all four quarters.** Splitting phi_2 from phi_3 needs F out to ~273 days,
which only Melbourne Oct–Feb stays observe; for the other months that tail is imported from
the Dec-16–Feb-17 reference panel and is the main source of the bands in §3.

**Validation.** Melbourne Q4-2016 is the one quarter whose own observation window identifies
every bucket exactly. Its exact label count is phi = (0.510, 0.362, 0.080, 0.049); the
method used everywhere else returns (0.498, 0.361, 0.082, 0.059) — a **maximum error of 1.16
points**, which is the amount by which every band in §3 has been widened.

---

## 3. Tables

### 3.1 Lead-time distribution (12-month window, n = 268,110, truncation-corrected)

| weighting | mean | p25 | median | p75 | p90 | p95 |
|---|---|---|---|---|---|---|
| per booking | 45.6 d | 9 | **26** | 62 | 118 | 159 |
| per night | 52.2 d | 11 | 31 | 72 | 137 | 168 |
| **per booking dollar** | **58.2 d** | 14 | **36** | 81 | 148 | 182 |

Share of bookings made within X days of check-in, value-weighted, by northern seasonal role:

| stay quarter | 30 d | 91 d | 182 d | 273 d |
|---|---|---|---|---|
| Q3 peak summer | 0.433 | 0.782 | 0.942 | 0.974 |
| Q4 | 0.437 | 0.740 | 0.917 | 0.967 |
| Q1 winter trough | 0.482 | 0.789 | 0.926 | 0.967 |
| Q2 | 0.399 | 0.750 | 0.911 | 0.974 |

Full curves: `K2_leadtime_cdf_by_season.csv`, figure `K2_leadtime_cdf_by_season.png`.

### 3.2 phi_k by season and weighting — the count / value / survival comparison

Central estimates. Northern seasonal roles (see §5 for the mapping).

| stay quarter | weighting | phi_0 | phi_1 | phi_2 | phi_3+ | booked before quarter |
|---|---|---|---|---|---|---|
| **Q3** | count | 0.572 | 0.332 | 0.064 | 0.032 | 0.428 |
| | nights | 0.510 | 0.371 | 0.079 | 0.041 | 0.490 |
| | **value** | **0.463** | **0.389** | **0.095** | **0.052** | **0.537** |
| | *GBV booking share (moderate survival)* | *0.437* | — | — | *0.174 (k≥2)* | — |
| **Q4** | count | 0.602 | 0.315 | 0.065 | 0.018 | 0.398 |
| | nights | 0.534 | 0.336 | 0.107 | 0.023 | 0.466 |
| | **value** | **0.502** | **0.353** | **0.117** | **0.028** | **0.498** |
| | *GBV booking share (moderate survival)* | *0.476* | — | — | *0.168 (k≥2)* | — |
| **Q1** | count | 0.647 | 0.265 | 0.071 | 0.017 | 0.353 |
| | nights | 0.593 | 0.294 | 0.091 | 0.022 | 0.407 |
| | **value** | **0.558** | **0.314** | **0.100** | **0.027** | **0.442** |
| **Q2** | count | 0.572 | 0.330 | 0.057 | 0.041 | 0.428 |
| | nights | 0.535 | 0.349 | 0.066 | 0.051 | 0.465 |
| | **value** | **0.498** | **0.361** | **0.082** | **0.059** | **0.502** |

Source: `K2_recommended_prior.csv`, `K2_survival_adjustment.csv`.

### 3.3 Bands on the value-weighted prior

Bands span the tail-import bracket (lower = no tail beyond each month's own data; upper =
the peak-season reference tail) widened by the 1.16-point validation error of §2.

| stay quarter | phi_0 | phi_2 | booked before quarter |
|---|---|---|---|
| Q3 | 0.463 **[0.443–0.484]** | 0.095 [0.078–0.113] | 0.537 **[0.516–0.557]** |
| Q4 | 0.502 **[0.468–0.535]** | 0.117 [0.096–0.139] | 0.498 **[0.465–0.532]** |
| Q1 | 0.558 **[0.529–0.587]** | 0.100 [0.086–0.114] | 0.442 **[0.413–0.471]** |
| Q2 | 0.498 **[0.482–0.514]** | 0.082 [0.070–0.095] | 0.502 **[0.486–0.518]** |

### 3.4 Lead time by stay length — why dollar weighting lengthens the kernel

| stay length | n | share of nights | share of value | mean lead | median | value-wtd mean lead |
|---|---|---|---|---|---|---|
| 1–2 nights | 99,396 | 13.2% | 14.1% | 37.4 d | 18 | 42.3 d |
| 3–6 | 123,169 | 41.6% | 44.2% | 48.3 d | 29 | 55.6 d |
| 7–13 | 34,213 | 24.8% | 24.0% | 54.3 d | 34 | 62.7 d |
| 14–27 | 8,156 | 12.2% | 10.7% | 60.8 d | 40 | 68.7 d |
| **28+ (long-term)** | 3,176 | 8.2% | 7.0% | **68.2 d** | 45 | **75.3 d** |

Lead time rises monotonically with stay length. This matters for Airbnb beyond the weighting
point: 28+-night stays recognise revenue *monthly*, and their share of nights has fallen from
20.2% (2022) to 13.4% (2025) on this repo's own estimates. Both effects — fewer long stays,
and long stays being the most forward-booked — **shorten** the kernel over time.

### 3.5 The M matrix (D)

`revenue_q = Σ_k phi_k · GBV_{q−k}`, value-weighted central estimates, northern roles:

| stay quarter | GBV_q | GBV_{q−1} | GBV_{q−2} | GBV_{q−3} |
|---|---|---|---|---|
| Q3 | 0.463 | 0.389 | 0.095 | 0.052 |
| Q4 | 0.502 | 0.353 | 0.117 | 0.028 |
| Q1 | 0.558 | 0.314 | 0.100 | 0.027 |
| Q2 | 0.498 | 0.361 | 0.082 | 0.059 |

Implied mean lag: **0.74 quarters (Q3)**, 0.67 (Q4), 0.60 (Q1), 0.70 (Q2). Two caveats on
using this against reported GBV. First, reported GBV is itself *net of cancellations
processed in that quarter*, including cancellations of bookings made earlier, so GBV_{q−2} has
already been reduced by some of the attrition this kernel prices — applying the full survival
haircut on top would double-count. Second, these weights sum to 1 by construction; the level
(the take rate) is a separate parameter.

### 3.6 Sensitivity to a 10% change in lead times (E)

| stay quarter | phi_0, −10% | phi_0, base | phi_0, +10% | d(phi_0) per +10% |
|---|---|---|---|---|
| Q3 | 0.488 | 0.463 | 0.441 | **−2.26 pp** |
| Q4 | 0.529 | 0.502 | 0.477 | −2.45 pp |
| Q1 | 0.581 | 0.558 | 0.537 | −2.14 pp |
| Q2 | 0.529 | 0.498 | 0.470 | −2.79 pp |

**A 10% lengthening of lead times moves the in-quarter share down by roughly 2.2–2.8 points**
and pushes about the same amount into the two-and-more-quarters-earlier buckets. For scale,
the only lead-time number Airbnb has ever quantified is "**down about 7% year-over-year**"
(Mertz, on April 2025), so a 10% move is slightly larger than what management calls a large
shift. The kernel is not violently sensitive to lead-time drift: a 7% move is worth about
1.5–2 points of phi_0.

---

## 4. What moves the weights (E)

**Direction of travel: lengthening, since 3Q25, and management says why.** Airbnb has flagged
longer lead times in four consecutive prints, each time attributing it to Reserve Now Pay
Later: *"Average lead times were up slightly on a year-over-year basis, particularly in North
America in part driven by the launch of our Reserve Now, Pay Later offering"* (3Q25 letter);
*"it's also led to longer booking lead times"* (4Q25 call); *"a lengthening of lead times
across all regions"* (1Q26 letter); *"longer booking lead times"* (2Q26 call). **No magnitude
has ever been given.** The only quantified lead-time move on record is the *pre*-RNPL "down
about 7%" of April 2025. Before that, the 2Q24 letter warned of *"shorter booking lead times
globally"* — the sentence that cost the stock 12–13% in a day. Lead time is the highest-torque
undisclosed series Airbnb has.

**RNPL plausibly lengthens the window and certainly raises cancellations.** The mechanism is
explicit: no cash at booking, payment due just before the free-cancellation deadline, so the
option to book early is cheap. Management: RNPL lets hosts *"lock in earlier calendar share."*
On the other side, the 2Q26 10-Q states that RNPL bookings *"have experienced higher
cancellation rates than historic bookings"* and — the sentence a kernel modeller should
paste above their desk — *"the timing among GBV, revenue, and cash receipts may become less
correlated."* Platform cancellation is put at *"an average of maybe 16% ... going to 17%."*
RNPL was >20% of GBV by 2Q26. Both forces push the same way for this note: **a longer, leakier
tail, meaning lower phi_0 and a bigger wedge between GBV's booking share and its revenue
weight.** Against them runs the shrinking 28+-night share, which shortens the tail.

**Vintage evidence on whether pace is actually drifting.** Krish's Inside Airbnb pickup
workstream (28 markets, ~800m matched listing-nights, consecutive 2024–25 vintages) finds
**essentially no change in booking pace between 2024 and 2025** — under 2 points at every
horizon. There is no clean 2026 comparison because Inside Airbnb went quarterly. So the
lengthening management describes is not yet visible in third-party calendar data, and the
2014–17 Melbourne baseline is too distant to date a trend against.

**Geography.** The same workstream finds North America books *latest* and EMEA *earliest*,
but the gap is only ~6 points at 90 days — smaller than the market-level spread, where big
urban gateways (Santiago, Singapore, Bangkok, LA, Hong Kong) book latest and leisure /
vacation-rental markets (Belize, Tasmania, Tokyo, Western Australia) book earliest, a ~25-point
range at 90 days. **Melbourne is a big urban market**, which places it on the late-booking side
of that distribution, so the prior here is more likely to be too *short* than too long for
Airbnb's leisure-heavy global mix.

---

## 5. The seasonal mapping, stated plainly

The panel is **Melbourne: southern hemisphere**. Its peak leisure quarter is Jan–Mar (and the
Dec build-up), the role northern Jul–Sep plays for Airbnb. We therefore shift the calendar six
months — Melbourne month *m* → northern month ((m+5) mod 12)+1 — which maps whole quarters
onto whole quarters and preserves position-within-quarter (the mechanical effect whereby a
stay early in a quarter has little time to be booked in-quarter). Both bases are in
`K2_phi_kernel_analytic.csv`.

**Where the mapping is good:** the summer/winter axis. Melbourne Jan–Mar (peak summer, school
holidays) → northern Q3 is a close analogue, as is Melbourne Jul–Sep (winter trough) → northern Q1.

**Where it breaks:** Christmas and New Year do not swap hemispheres. Melbourne Oct–Dec carries
*both* the spring shoulder and the Christmas peak, and it maps to northern Q2 (Apr–Jun), which
has no such holiday. Symmetrically, northern Q4 inherits Melbourne's Apr–Jun autumn, which has
no year-end holiday. **So the Q2 estimate here is probably too long-dated and the Q4 estimate
too short-dated.** A modeller who cares mainly about Q4 should consider the Melbourne-calendar
Q4 row (phi_0 = 0.494 value-weighted) as the holiday-containing alternative. The two quarters
to trust most are **Q3 and Q1**.

---

## 6. Caveats

1. **Blocked is not booked — which is why the other sources could not be used.** Theo's
   120-market booking curves and Krish's calendar levels both measure `available='f'`, which
   conflates confirmed bookings, host blocks and inactive listings. Both curves are
   **U-shaped in horizon** — the blocked share falls to a trough near 90 days then rises
   ~12–20 points out to 365 days. A booking-pace curve cannot do that; bookings only
   accumulate. That right-hand limb is host blocks and unopened calendars, and it puts a floor
   of ~12–20 points of contamination on any "share booked by lead X" read off a calendar level.
   Krish's *gross new-block hazard* is the one usable pace object there, and it implies only
   ~62% of blocking inside 90 days against 85% of *bookings* inside 90 days here — the gap is
   the contamination, and it runs in the direction of making lead times look longer than they
   are. The STR panel is used precisely because it has an actual booking date.
2. **One city, 2014–17, third-party academic panel.** Melbourne is not Airbnb's mix: no
   cross-border split is observable, no region breakdown is possible (the STR tables carry no
   coordinates or neighbourhood), and the period predates RNPL, COVID, and the current
   long-term-stay mix. Treat the *shape* as transferable and the *level* as an anchor to be
   tested, not as a measurement of Airbnb today.
3. **The far tail is imported, not measured, for two of the four quarters.** Melbourne Mar–Jul
   stays have their observation window pinned at 180 days, so their >180-day mass comes from
   the Dec-16–Feb-17 reference panel. Those reference months are peak summer and have the
   fattest tail in the sample, so the imported tail is more likely an over- than an
   under-statement; the bands in §3.3 bracket it, and the no-tail lower bound is in the CSVs.
4. **Survivorship, in the useful direction.** The panel records only stays that happened, so
   cancelled bookings are invisible. That is exactly what a *revenue* kernel wants — but it
   means the gross booking distribution in §3.2 is modelled, not observed. The three survival
   calibrations (flat / moderate / strong) span a value-weighted cancellation rate of 10–16%
   and are pinned to management's ~16% platform figure, which is itself hedged three ways and
   has no stated unit of account.
5. **Price units are unverified.** `Price` has no local codebook; it is presumably nightly AUD.
   ADR is winsorised at the 99.5th percentile (517) because the raw maximum is 736,279. Value
   weighting uses nightly price × nights, which is a booking-value proxy, not GBV: it excludes
   cleaning fees, service fees and taxes, all of which Airbnb's GBV includes.
6. **Panel de-duplication.** The two STR files share 5,292,284 property-nights and disagree on
   price for 186,812 of them and on booked date for 2,691. We prefer the later panel on shared
   keys. Status never disagrees, and the booked-date disagreement rate (0.05%) is too small to
   move any number here.
7. **Two quarters rest on a single calendar year each.** The 12-month window means Q2 and Q3
   (Melbourne) are observed once, and Melbourne Q1 is assembled from Mar-2016 plus
   Jan–Feb-2017. There is no year-over-year averaging and no standard error from repeated
   seasons; the bands are identification bands, not sampling bands.

---

## 7. Recommended prior for the modeller

Use the **value-weighted, northern-role** table as a Dirichlet-style prior on phi, with the
§3.3 bands as roughly ±1 s.d.:

```
Q3 (peak summer): phi = (0.46, 0.39, 0.10, 0.05)   before-quarter 0.54  [0.52-0.56]
Q4              : phi = (0.50, 0.35, 0.12, 0.03)   before-quarter 0.50  [0.47-0.53]
Q1 (trough)     : phi = (0.56, 0.31, 0.10, 0.03)   before-quarter 0.44  [0.41-0.47]
Q2              : phi = (0.50, 0.36, 0.08, 0.06)   before-quarter 0.50  [0.49-0.52]
```

Adjustments a modeller should apply on top:
- **Shift phi_0 down** if weighting anything other than dollars, and down again for a
  leisure-heavier mix than urban Melbourne.
- **−2.3 points of phi_0 per +10% lead time**, so roughly −1.6 points for the RNPL-era
  lengthening if it is of the same order as the 7% move management has quantified before.
- **Do not apply a further survival haircut to reported GBV** without checking §3.5: reported
  GBV is already net of in-period cancellations.
- The bottom-up phi_0 of ~0.50 is **above** the 0.23–0.41 the time-series arm reports and
  **below** the ⅔ used elsewhere. The disagreement with the time-series arm is the finding, not
  a defect: this estimate has no macro or supply confound and no COVID window in it, and it
  is corroborated to within a couple of weeks by Airbnb's own unearned-fee ratio.
