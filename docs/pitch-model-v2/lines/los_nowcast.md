# LOS and seats nowcast for 3Q26 and 4Q26: fixes (k) and (l) in adr_engine_v3

**23 September 2026.** Krish with Claude Code, branch `krish/adr-audit-fixes` (PR #67).
- **Pre-registration:** `los_nowcast_prereg.md`, filed before any computation. Amendment 1 (the length-match rule)
  was filed before any run. Amendment 2 corrects a factual line about hotels after the run.
- **Hashes:** `data/processed/pitch_model_v2/los_nowcast/00_prereg_hash.txt`.

## The question

The engine held the length-of-stay (LOS) term at 0.30pp and seats at −0.483pp in 2Q26, 3Q26 and 4Q26. Both 2Q26
values are assumed fills, and they cancel against the carried core. The forecast was therefore assuming that neither
term changes after 2Q26.

- **LOS:** measured from the Inside Airbnb calendars already in the main tree (34 markets). Nothing new was pulled.
- **Seats:** cannot be measured from anything the team holds (section 4).

## What ran

```bash
PYTHONPATH=analysis/src py -3.13 -m pitch_model_v2.los_nowcast.run --workers 3        # exit 0, ~10 min cold
PYTHONPATH=analysis/src py -3.13 -m pitch_model_v2.adr_engine_v3.run --no-posterior --no-workbook --no-refresh-prices   # exit 0
PYTHONPATH=analysis/src py -3.13 -m pytest analysis/src/pitch_model_v2/adr_engine_v3/tests analysis/src/pitch_model_v2/los_nowcast/tests -q   # 55 pass
```

The two constructions:

- **F, flow (booking-dated, like ADR).** A newly booked night is one that was available in the earlier dump and
  blocked in the later one. So 2Q26 is the bookings made between the March and June 2026 dumps, and 3Q26 is June to
  August. Each is compared with the matching 2025 interval, matched on dates (±31 days) and on length (±14 days).
- **S, stock.** I2b's lead-matched blocked runs, recomputed from the raw calendars.

Both are computed with occupancy weights (W1) and without (W0).
- The term is the change in nights shares by stay length, times the 14a price discount.
- The global figure is 10-K weighted. NYC and LA are excluded, because of their night minimums.

## Results

**Gate: S reproduces I2** (`reproduction_I2.csv`). All four global rows match to within 0.0003pp. The pre-registered
limit was 0.02pp.

**The change in the LOS term, 2Q26 → 3Q26** (`delta_by_construction.csv`, same-market panels):

| construction | n markets | 2Q26 LOS pp | 3Q26 LOS pp | change |
|---|---:|---:|---:|---:|
| F flow, W1 (occupancy-weighted) | 16 | +0.32 | +0.06 | **−0.26** |
| F flow, W0 | 16 | +0.54 | +0.16 | −0.38 |
| S stock, W1 | 24 | +0.26 | +0.01 | **−0.25** |
| S stock, W0 | 24 | +0.29 | +0.12 | −0.17 |

- **Point (registered: the mean of F-W1 and S-W1): −0.253pp.**
- **Band:** −0.38 to −0.17. The market bootstrap alone gives p10/p90 of −0.32/−0.19.
- **Forward LOS:** 3Q26 and 4Q26 are 0.30 − 0.253 = **+0.047pp** (band −0.08 to +0.13).

**What the numbers say:**
- **All four constructions agree on the sign.**
- **The drop is broad.** 75% of markets fall in both constructions, with medians of −0.26 (F) and −0.12 (S).
- **No single market drives it.**
- **EMEA carries the most weight (0.403), from Paris and Rome only.** Both fall in both constructions: Paris −0.37 and
  −0.42, Rome −0.50 and −0.52.
- **NA falls in S (−0.17) and is flat in F.** LatAm is flat.

**Reading it.** The 2Q26 letter says short stays "continued to outpace long-term stays ... a mix-shift trend we have
now seen for over a year". That trend was worth about +0.3pp of ADR in 2Q26 bookings on both constructions. In
3Q26 bookings it has almost stopped, so this ADR tailwind is fading. Case B of fix (c) had assumed this without a
same-construction 2Q26 value. It is now measured: +0.047 here, against I's +0.056.

**World Cup** (`worldcup_los_ddd.csv`). The test is S, June 2026 dumps, W1: host cities (LA, Mexico City) against
7 NA and LatAm controls, tournament window against the post-tournament window, y/y.

| | tournament | post | difference |
|---|---:|---:|---:|
| host LOS term y/y | +0.24 | +0.04 | +0.20 |
| control LOS term y/y | −0.26 | −0.01 | −0.26 |
| **DDD** | | | **+0.46pp** (LA +0.40, Mexico City +0.54) |

- **The effect is real locally.** The World Cup shortened stays in host cities. Their short-stay share (under 7
  nights) rose from 0.586 to 0.635, while it fell in the controls.
- **Globally it is 0.005pp.** Host-metro tournament nights are about 1% of 2Q26 nights (1.53m of 148.3m), so the
  global LOS effect is +0.0047pp, or 0.007pp scaled. That is below the registered 0.02pp materiality line, so it is
  not added.
- **The broad LOS drop is not a World Cup effect.** It is centred on EMEA and APAC, and the hosts are outside the
  aggregate.

**Seats** (`seats_check.csv`, prereg §4 and amendment 2). Nothing in the repo measures seats:
- Experiences and services volumes are undisclosed. Airbnb declined to break them out on the 2Q25 call.
- The only candidate proxy was Inside Airbnb "Hotel room" listings. It fails the one disclosed number. In the four
  cities with a June 2025 dump, hotel-room reviews grew −15% to +7% y/y, never three times the rest (the letter says
  "approximately three times as fast as our homes business").
- So seats stays at −0.483pp. Its uncertainty is already in the band at the business-case range (−0.75 to −0.23,
  ±0.26pp).
- The 2Q26 letter's "seats booked accelerating year-over-year" points to more dilution, not less. That is a
  direction, not a size.

## What it does to the line

`los_wc_ladder.csv` shows each fix switched on in turn, on the midpoint FX leg.

| step | 3Q26 ADR | P(≥ Street $177.06) | 4Q26 ADR | P(≥ Street $171.33) | FY27 |
|---|---:|---:|---:|---:|---:|
| v3 through fix (j) (LOS carried) | $176.18 | 0.31 | $171.46 | 0.52 | $184.36 |
| **+ (k) LOS measured** | $175.75 | 0.22 | $171.04 | 0.46 | $184.16 |
| **+ (l) World Cup premium out of the core (0.05pp)** | **$175.66** | **0.21** | **$170.96** | **0.45** | **$184.00** |
| same, identity FX | $177.07 | 0.50 | $172.44 | 0.64 | |
| same, V1 FX | $176.41 | 0.35 | $172.05 | 0.59 | |

- **Fix (k) is worth about −$0.43 in each quarter. Fix (l) is about −$0.09.**
- **On the recommended FX leg, 4Q26 is now $0.37 below the Street**, where it was $0.13 above. 3Q26 is $1.40 below.
- **On the identity FX, 3Q26 sits exactly on the Street ($177.07) and 4Q26 is $1.11 above.**
- **FX is still the largest swing.**
- **4Q26 mix-only rows on the midpoint leg:** the base ($170.96), the sub-regional row ($170.88) and the measured
  origin–destination tilt ($171.28) all sit below the Street. Only the K line ($171.58) and the card v3 carry
  ($172.70) sit above.

## What failed or is weak, stated plainly

1. **There is no backtest.** Airbnb last disclosed the 28+ share in 1Q24, and our calendars start in 2024. This is a
   measurement replacing an assumption. It is not a tested forecast.
2. **A blocked run is not a booking.** Host blocks are mixed in. Year-on-year differencing removes stable blocking
   within a market, but not a change in it.
3. **EMEA is two markets carrying 40% of the weight.** Both agree, but two is two.
4. **4Q26 carries the 3Q26 read.** No 4Q26 bookings exist yet, and past Q3→Q4 LOS moves were +0.06, +0.18 and −0.09
   (H history).
5. **2027 LOS stays at the 0.30 fill** (unchanged by the registration). 3Q27 and 4Q27 now chain on lower 3Q26 and
   4Q26 levels and still add 0.30 y/y. A 2027 rule for LOS belongs with the 2027 core rule (open choice 4).
6. **The World Cup core adjustment (fix l) is a post-hoc translation.** It is labelled as such. The point is 0.05pp,
   the Chicago-controlled and match-night estimates. The band runs from 0 to the 0.20pp pooled bound (±0.10pp in the
   envelope).
7. **Amendment 2 corrects the pre-registration's hotel sentence.** NYC and LA hotel-room listings did rise. The
   conclusion stands, on the 3× test.

**Parameter count.** None fitted.
- **Registered constants:** the 14a price ratios (3), the 10-K weights (4), the 90-night cap, the 180-night closure
  rule, the lead window (7–97) and the pairing tolerances (31, 14, 45).
- **Fix (l):** one post-hoc value (0.05pp).

## RESUME

The next agent should do these in order:

1. **Before 5 Nov, rerun on the September dumps.** When the September 2026 calendars land in
   `data/raw/inside_airbnb_calendar`, a Jun→Sep flow is a better 3Q26 read than Jun→Aug. It needs a
   pre-registration amendment first, then a rerun of `los_nowcast.run` and the engine.
2. **Decide 2027 LOS together with the 2027 core rule** (corrections note, choice 4).
3. **The switches revert one fix each:**
   - `exfx.LOS_NOWCAST=False` reverts (k);
   - `exfx.WC_CORE_ADJ=False` reverts (l).
4. **The seats term stays an assumption until Airbnb discloses seats.** If the 5 Nov letter gives any number,
   replace the scenario with it.
