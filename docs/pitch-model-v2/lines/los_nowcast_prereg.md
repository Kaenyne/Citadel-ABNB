# LOS and seats nowcast for 3Q26 and 4Q26: pre-registration

Krish with Claude Code, 23 Sep 2026, branch `krish/adr-audit-fixes` (PR #67). Filed before any number below is
computed. The blob hash is logged in `data/processed/pitch_model_v2/los_nowcast/00_prereg_hash.txt`. Later changes
are appended as dated amendments and nothing is deleted.

## 1. Question

`adr_engine_v3` holds the length-of-stay (LOS) term at 0.30pp and the seats term at −0.483pp in 2Q26, 3Q26 and 4Q26.

- **2Q26 values:** both are assumed fills in the H decomposition, not measurements.
- **Why they cancel:** the carried 2Q26 core is disclosed ex-FX minus those fills, so they cancel in the forecast.
- **What that implies:** the forecast assumes the true LOS and seats terms do not change from 2Q26 to 3Q26/4Q26.

This registration replaces that assumption with a measured change, wherever the team's existing data can measure one.

No new data is downloaded. The inputs are:
- the raw Inside Airbnb calendars already in the main tree (`data/raw/inside_airbnb_calendar`, 34 markets);
- their listings dumps (`data/raw/inside_airbnb`).

## 2. LOS

**Object.** Δ = L(3Q26) − L(2Q26), the change in the LOS mix term between 2Q26 and 3Q26 bookings, in pp of ADR. Each
L is a y/y term.
- **Forward LOS:** 3Q26 = 0.30 + Δ, and 4Q26 = the 3Q26 value. No 4Q26 bookings exist yet, so the Q3 read is carried.
- **2027 quarters:** unchanged by this registration.
- **The core:** unchanged. The 2Q26 fill stays in the history, so only the measured change enters the forecast.

**Construction F: flow of new bookings (booking-dated, like ADR).**
- **Pairs:** for a market and two same-year vintages v1 < v2, a newly blocked night is a listing-night present in both
  calendars that is available (`t`) in v1 and unavailable (`f`) in v2, for stay dates in [v2 + 1, v1 + 364].
- **Runs:** a run is a maximal block of newly blocked nights with consecutive dates for one listing.
- **Dropped:**
  - runs touching either edge of the observed date range (censored);
  - runs over 90 nights (host blocks, the 14c cap);
  - every run of a listing with more than 180 newly blocked nights in the pair (calendar closure).
- **Buckets:** under 7, 7–27, and 28–90 nights, by run length.
- **Quarter mapping:** 2Q26 = the market's March 2026 vintage to its June 2026 vintage. 3Q26 = June 2026 to August 2026.
- **Prior year:** the 2025 pair whose v1 and v2 each fall within ±31 days of the 2026 dates minus 364. If more than
  one qualifies, take the smallest summed gap. A market without a qualifying pair drops out of that quarter.

**Construction S: stock (I2b's lead-matched window, recomputed).**
- **Runs:** runs start 7 to 97 days after the vintage, with I2a's run definition and the 90-night cap.
- **Vintages:** June 2026 vintages are 2Q26 and August 2026 vintages are 3Q26.
- **Prior year:** the 2025 vintage nearest to the vintage date minus 364, within ±45 days.
- **Reproduction gate:** S must reproduce `data/processed/adrq3/I/I2_los_term.csv` (global lead-matched rows, both
  weightings, June and August) to within 0.02pp. If it does not, the run stops and the failure is written up.

**Weighting.**
- **W1, occupancy-weighted (14c convention):**
  - only active listings count (`number_of_reviews_ltm` > 0);
  - each listing's weight is `estimated_occupancy_l365d`, clipped at 0.7 × 365;
  - that weight is split across buckets in proportion to the listing's in-scope run nights;
  - the listings dump used is the one nearest v2 (F) or the vintage (S), within 60 days.
- **W0, unweighted:** nights shares.

**Term.** LOS pp = Σ_b Δshare_b × (ratio_b − 1), with ratios 1.000 / 0.966 / 0.852 (14a).
- Regional shares pool weighted nights across the region's markets.
- The global figure uses the 10-K FY25 nights weights (NA 0.296, EMEA 0.403, LatAm 0.169, APAC 0.131), renormalised
  over the regions covered.
- NYC and LA are excluded from every aggregate: they have regulatory night minimums (the I2 and 14c convention).
- Δ is computed on the same-market panel within each construction: markets present in both quarters.

**Point and band (fixed here).**
- **Point:** Δ\* = the mean of F-W1 and S-W1.
- **Fallback:** if F's same-market panel has fewer than 12 markets, F is dropped and Δ\* = S-W1.
- **Band:** the union of the min–max over {F, S} × {W1, W0}, and the 10th–90th percentile of a market bootstrap of Δ\*
  (2,000 draws, markets resampled within region, seed 7).

**What this cannot do.** It cannot be backtested. Airbnb last disclosed the global 28+ share in 1Q24, and our
calendars start in 2024 with four markets. This is a measurement replacing an assumption, not a tested forecast, and
it is labelled that way. A blocked run is not a booking, because host blocks are mixed in. The y/y difference cancels
host blocking that is stable within a market, but not a change in it.

## 3. World Cup and LOS

**Hosts in the panel:** Los Angeles and Mexico City. NYC has no June 2025 vintage.
**Controls:** the non-host NA and LatAm markets, with pooled nights.

**Test (construction S, June 2026 vintages against 2025, W1).**
- **Tournament window:** runs starting between the vintage + 7 days and 19 Jul.
- **Post-tournament window:** runs starting 1 Aug to 15 Sep.
- **DDD** = [host (tournament − post), y/y] − [control (tournament − post), y/y], in LOS pp.
- **Hypothesis:** the World Cup shortened host-city stays, so DDD > 0.

**Translation.**
- **Formula:** global 2Q26 LOS effect = DDD × (host-metro tournament nights ÷ 148.3m 2Q26 nights).
- **Nights:** 1.53m covered, or 2.31m scaled by 104/69, from `docs/worldcup-premium/RESULTS.md` §3b.
- **Timing:** f_2Q26 of 1.0 or 0.5.
- **Materiality rule:** the result is added to Δ only if its central value is at least 0.02pp in absolute terms.
  Otherwise it is reported as immaterial.
- **Stated expectation:** under 0.05pp.

## 4. Seats

No data in the repo measures seats. Experiences and services volumes are not disclosed. On the 2Q25 call Airbnb
declined to break them out and called them immaterial. The 2Q26 letter is qualitative only: "seats booked
accelerating year-over-year and quarter-over-quarter" and "hotel nights booked grew approximately three times as
fast as our homes business".

One proxy was checked before this registration, and it is stated here because it was looked at first. It was the
count of Inside Airbnb "Hotel room" listings and their trailing reviews. It did not rise in NYC, Paris, Rome or London
through August 2026, although the 2Q26 letter reports thousands of hotels added in those cities. So Inside Airbnb does
not see the hotel business, and there is no hotel proxy.

**Registered rule:**
- seats stays at the FY26 base scenario (−0.483) in 3Q26 and 4Q26;
- its uncertainty stays in the band at the business-case range (−0.75 to −0.23, `CARD_BANDS`);
- the receipt for the hotel check is written by this package, `seats_check.csv`.

## 5. Engine wiring

This goes into `adr_engine_v3` behind `LOS_NOWCAST` (default True once the run passes the reproduction gate):
- forward `los_mix` = 0.30 + Δ\* in 3Q26 and 4Q26;
- `CARD_BANDS["los_mix"]` for those quarters becomes the §2 band, re-centred on the new point;
- `LOS_NOWCAST=False` reproduces the current v3.

The World Cup core adjustment (0.05pp point, 0.20pp bound, post-hoc translation from the World Cup run) is separate.
It sits behind its own switch, `WC_CORE_ADJ`, and is reported as its own row. It is not decided by this registration.

## Amendment 1 (23 Sep 2026, after listing the qualifying pairs, before any run or result was computed)

Construction F's prior-year rule let a 2025 interval of about 30 days stand in for a 2026 interval of about 62 days
(3Q26), and 131 days for 89 days (2Q26). That is 19 of 45 pairs.

A new-booking flow over a longer interval catches more long-lead bookings. Long-lead bookings skew toward long stays,
so unequal lengths bias the y/y. The fix: a 2025 pair qualifies only if its length is within 14 days of the 2026 pair's
length, in addition to the ±31-day endpoint rule. Among qualifying pairs, the smallest summed endpoint gap is taken, as
before. `pairs_F.csv` is rewritten, and the list printed before this amendment is not kept.

**Correction to amendment 1, same session and still before any result was computed:** the rule affected 21 of 43
pairs, not "19 of 45". After the amendment there are 42 F pairs.

## Amendment 2 (23 Sep 2026, after the run): correction to §4

§4 said Inside Airbnb "Hotel room" listings "did not rise in NYC, Paris, Rome or London". The receipt
(`seats_check.csv`) shows that is wrong for NYC and LA.
- **Rose:** NYC hotel-room listings went from 331 to 486 (Dec 2025 → Aug 2026), and their trailing reviews from 499
  to 686. LA went from 302 to 412.
- **Fell:** Paris, Rome and Barcelona.
- **Flat:** London.
- **Caveat:** the counts are in the hundreds per city, and partial-scope monthly dumps distort the levels. Paris's
  March 2026 dump, for example, has half its usual listing count.

The conclusion is unchanged, and it is checked against the one disclosed number: "hotel nights booked grew
approximately three times as fast as our homes business" (2Q26). This is exploratory, not registered. The table uses
the four cities with a June 2025 dump. It compares y/y growth in trailing-12-month reviews, June 2025 to June 2026:

| city | hotel-room listings | all other listings |
|---|---:|---:|
| Paris | −15.0% | −0.4% |
| Rome | +5.7% | +8.0% |
| LA | +6.8% | +4.9% |
| Mexico City | +2.5% | +17.4% |

Hotel-room reviews never grow at three times the rest, so Inside Airbnb does not see Airbnb's hotel growth. Seats
stays as registered.
