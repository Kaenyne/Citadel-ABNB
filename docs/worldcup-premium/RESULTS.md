# World Cup premium inside the 2Q26 ADR core — results

**22 September 2026.** Pre-registration: `PREREG.md` (blob `e2dda559…` after the §11 amendments, logged in
`data/processed/worldcup_premium/00_prereg_hash.txt` before any outcome was computed). Package
`analysis/src/worldcup_premium/`. Every number below is in `data/processed/worldcup_premium/`.

**Reproduce**

```bash
PYTHONPATH=analysis/src py -3.13 -m worldcup_premium.run        # pre-registered; exit 0, about 12.5 min
PYTHONPATH=analysis/src py -3.13 -m worldcup_premium.posthoc    # post-hoc checks, section 3; exit 0, about 4 min
```

Raw inputs are read from the main worktree's `data/raw` (gitignored), or from `$ABNB_RAW`.

## 1. Answer

**Yes, there was a World Cup price premium, but at Airbnb's scale it is worth about 0.05–0.30pp of 2Q26 ADR. That
is $0.04–$0.51 on 4Q26 ADR, below the audit's break-even of 0.44–1.02pp.** It does not put 4Q26 ADR below the
Street's $171.33.

The most bearish consistent combination stacks three things:

- the audit's most bearish consistent row, $172.07 (one-construction terms plus V1 FX weights);
- the largest World Cup scenario, −$0.51;
- nothing else.

That gives **$171.56, still $0.23 above the Street.** The central scenarios land at $171.7–$172.0. The C2 answer
in the audit stands: a below-Street 4Q26 is a core call, not a composition call. The World Cup narrows the gap
but does not close it.

**Common Crawl could not help.** Airbnb search pages carry no usable quotes after September 2024, and the
2025–26 crawls hold only 1–30 host-city pages each. Everything below is Inside Airbnb.

## 2. What the pre-registered run found

| # | test | result | n |
|---|---|---|---|
| **P1** (primary price) | same-listing quote panel, hosts (Los Angeles, Mexico City) against controls (Chicago, Austin, Nashville, New Orleans), March–August 2026 | premium on a stay wholly in the tournament: **+11.1%** (listing-clustered 90% interval 10.8–11.5%); LA +12.1%, Mexico City +10.2%. Decomposition: host × tournament +7.4%, plus +9.9% per full match-night share. Leave-one-control-out 9.2–12.5%. The true host pair ranks **1st of 15** permutations. P3 robustness: 10.7%. | 362,470 quotes, 76,615 listings |
| **P2** (match nights) | within-snapshot cross-section, 17 host markets against 16 control markets | match-night premium net of placebo **+8.9%** per full match-night share (90% interval 2.6–15.2%, 33 market clusters). Placebo in controls +0.5% (p 0.83). Leave-one-host-out 5.0% (without Mexico City) to 11.3% (without LA). | 164,637 quotes |
| **V1** (booked share, T nights vs adjacent, host minus controls) | calendar availability | LA +2.0pp (4 Dec, before the draw), +4.9pp (March), +1.6pp (June). Mexico City +5.2 / +3.5 / **−4.4pp**. 2025 placebo for LA at the March lead: +1.2pp. Net of the placebo, LA's March excess is about +3.7pp of listings. | 6 markets × 3 rounds |
| **V2** (match-night booked-share spike) | calendar availability | Mexico City +1.6pp (Dec), +3.0pp (Mar), **+8.3pp (Jun)**, p ≤ 0.002. LA +0.3 / +0.5 / −0.7pp. Control placebos all insignificant. | 39 dates per round |
| **V3** (booking timing) | **failed** | On the common date set the June excess is ≤ 0 (LA −1.1pp, Mexico City −8.9pp), so the timing shares fall outside [0, 1] (LA 2Q26 share 1.38). They cannot be interpreted. | — |
| **V4** (realised stays, reviews) | host minus control, vintage-matched y/y | hosts +10.9% (March–May) → **+15.0%** (June–July); controls +4.9% → +1.1%. **DiD +7.9pp.** By month, hosts ran 6.8 / 8.0 / 17.3 / 15.7 / 14.3%. | 19 host + 19 control markets |
| **A1** (Paris 2024 analog) | price: **artefact**; availability: usable | Price DiD +0.03% in every round, because 99.8–100% of listings have one calendar price for every date (`price` is a static base rate). Availability: Olympic nights were **1.0–2.5pp *less* booked** than adjacent nights, relative to Rome, in the March–June 2024 snapshots. | 58–71k Paris listings |
| **Translation** (§8 as registered) | **invalid** | It mechanically returns 2Q26 +0.18 / +0.26 / +0.42pp and the label "measured composition term". It is built on the failed V3 shares (f_2Q26 = 1.38 for LA), so it is **not reported as a result.** | — |

**Defects of the pre-registration, stated plainly.**

- The Dallas placebo was impossible by construction (amendment 2, before results).
- V3 assumed the June excess would be positive. It was not, because the June comparison window (late July–August)
  is the dead season in New Orleans, Austin and Nashville, which inflates the controls' contrast.
- The translation had no fallback for a failed timing input.
- The Paris price test relied on calendar prices that turned out to be static.

## 3. Post-hoc checks (added after seeing the results)

**3a. Is P1 seasonality?** `posthoc.event_study`, `60_posthoc_event_*.csv`. This is the same sample and FE as P1,
minus the week FE and the treatment terms. The table shows the gap to the controls by check-in week.

| series | before T (Apr – early Jun) | during T | after T (late Jul – Aug) | T minus mean of before/after |
|---|---:|---:|---:|---:|
| Mexico City minus controls | −5.2% | +8.7% | −2.3% | **+12.4%** |
| Los Angeles minus controls | −4.5% | +5.2% | +2.0% | +6.5% |
| Los Angeles minus Chicago only | +4.0% | 0.0% | −5.6% | **+0.8%** |

- **Mexico City's premium is event-shaped.** It jumps +18.7% in the opening-match week (8–14 June) and is gone by
  the week of 13 July, after the city's last match on 5 July.
- **LA's is mostly seasonal.** Its gap to the pooled controls climbs steadily from −12% in March to 0 by late May,
  which is LA's summer peak against the controls' summer trough. Against Chicago, whose summer is high season like
  LA's, there is no tournament premium.
- **Chicago is not a clean control either.** The LA − Chicago series drops −16% in the Lollapalooza week (27 July).
- **P1 with Chicago as the only control: +3.2%** (2.4–3.9%).

**Reading.** The premium is concentrated in the smaller, more event-exposed market (Mexico City, 10–12%) and on
match nights (P2, about 9%). In a market as large as LA, whose centroid is 12 km from SoFi, the city-wide
premium is 0–6%. The pre-registered pooled 11.1% overstates the host-wide average.

**3b. Translation with bounded timing** (`61_posthoc_translation.csv`). This replaces the invalid §8 run.

effect_2Q26 = Σ host-metro tournament nights × f_2Q26 × (regional ADR / global ADR) × premium / 148.3m.

- **Nights.** Covered host-metro tournament nights are 1.53m, from Inside Airbnb `estimated_occupancy_l365d` ×
  39/365. Mexico City is priced at the LatAm ratio 0.56, the rest at the NA ratio 1.53.
- **Coverage.** Covered only, the midpoint, or scaled × 104/69 matches.
- **Timing.** f_2Q26 of 1.0 (the nights line's "bulk in 2Q26") or 0.5.

| premium source | f_2Q26 = 1.0 | f_2Q26 = 0.5 |
|---|---|---|
| P1 pooled 11.1% (upper, seasonality included) | 0.16 / **0.20** / 0.31pp | 0.08 / 0.10 / 0.15pp |
| P1, Chicago only, 3.2% | 0.04 / 0.06 / 0.09pp | 0.02 / 0.03 / 0.04pp |
| P2 match nights only (8.9% × 0.32 match share) | 0.04 / 0.05 / 0.08pp | 0.02 / 0.03 / 0.04pp |

Each cell reads covered / central / scaled-with-summer-factor-1.3.

The **full range is 0.02–0.31pp** on 2Q26 ADR, which is $0.04–$0.51 on 4Q26 ADR. A defensible central value is
about **0.05–0.20pp** ($0.08–$0.33).

The timing evidence cuts *downward*. Net of its 2025 placebo, LA's booked-share excess was already about +3.7pp
of listings by 16 March. That suggests a material share of World Cup bookings were made in 1Q26, not 2Q26, and
1Q26 bookings inflate the 1Q26 core rather than the carried 2Q26 core. The pre-draw excess (+2.0pp on 4 Dec)
means some were made in 2025, which toughens the 4Q26 comparison a little.

**3c. Volume cross-check against the nights line.**

- The V4 DiD (+7.9pp of host-market stays) on 1.53m covered tournament nights is about 120k excess nights, and
  about 180k scaled. That is **roughly 0.1pt of global 2Q26 nights growth**.
- The nights line books +0.5pt in 2Q26 and a −0.5pt lap in 2Q27 (`final_nights.md:931`).
- Inside Airbnb's occupancy model may understate nights, but it would have to be low by about 4× to reconcile.
- This points to the 2Q27 World Cup lap being **too large**. That cuts against the short on 2Q27 nights, and is
  flagged for the nights-line owners, not acted on here.

## 4. What this does to the ADR audit

- **Finding F5 is now measured.** The World Cup premium inside the carried 2Q26 core is about 0.05–0.20pp
  (range 0.02–0.31pp). The composition term is real and small. It is ranked below the one-construction basis
  correction (F2) and the FX weights (F1), and does not change C2's "no".
- **Break-even, updated.** Starting from the audit's most bearish consistent 4Q26 row ($172.07), the remaining
  gap to the Street is $0.74, or 0.44pp. The World Cup covers 0.05–0.31pp of it. Nothing else in composition is
  left to close it.
- **Paris 2024 as a precedent.** The mega-event in the same data type *displaced* bookings on event nights rather
  than adding them. That supports management's line that event effects are "relatively small compared to the
  total nights booked in a region".

## 5. Limits

- **Asking prices, not realised ADR.** Quotes are asking prices of unbooked inventory, pre-fee. Realised event
  nights may have priced higher (booked early at high asks) or lower (hosts discounted unsold nights).
- **Unavailable includes blocks.** Calendar "unavailable" includes host blocks.
- **Coverage.** Two host metros have calendars and 17 host markets have one price snapshot. Atlanta, Houston,
  Kansas City, Philadelphia, Guadalajara, Monterrey and Miami-Dade proper are not in the data; the scaled rows
  cover them by match count.
- **Nights model.** Host nights come from Inside Airbnb's review-based occupancy model, not bookings.
- **Timing is unmeasured.** Booking timing is scenario-bounded, because V3 failed.

## RESUME

**Numbers to carry.** If the ADR line adopts this, use a labelled composition row: "World Cup premium inside the
2Q26 core, −0.05 to −0.20pp from 4Q26 (range −0.02 to −0.31), asking-price basis". Carry the event-study table as
the seasonality evidence.

**Next agent: timing.** A timing measure that survives would need the September 2026 calendar snapshots (their
T nights are past, so no) or a same-listing booked-date series (not available). Treat timing as a scenario.

**Next agent: the nights-line 2Q27 lap.** It deserves its own look. 3c suggests +0.1pt, not +0.5pt.

**Commit order.** Commit `PREREG.md` alone first, then re-run both commands (deterministic) and commit the
results, so the ordering is visible in git.

## Update, 23 Sep 2026: how the ADR line uses this

This is a dated addendum. The sections above are unchanged.

**Adopted as fix (l) in `adr_engine_v3` (PR #67, DEC-0050).**
- **Point:** 0.05pp comes out of the carried 2Q26 core in every forecast quarter. That is the Chicago-controlled
  and match-night estimate.
- **Bound:** 0.20pp. The pooled estimate includes summer seasonality.
- **2Q27:** it also laps the 2Q26 base.
- **Label:** the translation (§3b) is post-hoc.

**Where the line stands now.** The line moved after this study, for reasons other than the World Cup:
- **Fix (j):** the FX leg became the card-method midpoint.
- **Fix (k):** LOS was measured from the repo's calendars and fell 0.25pp between 2Q26 and 3Q26 bookings.
- **Result:** on that line, 4Q26 is $171.04 before the World Cup row and $170.96 after it, against a Street of
  $171.33.

§1's statement, that the World Cup does not by itself put 4Q26 below the Street, still holds. The line is below the
Street because of FX and LOS. The World Cup adds −$0.08.

**The World Cup and length of stay (PR #67, `los_nowcast`).**
- **Local effect:** it shortened host-city stays, +0.46pp of the LOS term in LA and Mexico City against controls.
- **Global effect:** 0.005pp, below the materiality line, so it is not added.

**Nights (§3c) is still open for the nights-line owners.** The 2Q27 World Cup lap of −0.5pt looks about 4× too
large.
