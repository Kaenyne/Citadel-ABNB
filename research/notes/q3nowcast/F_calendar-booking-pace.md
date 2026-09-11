# WS-F: booked-nights pace from Inside Airbnb calendars, and whether it can be validated

Date: 2026-09-12
Author: Krishang Surapaneni (compiled with Claude Code)

## Bottom line

1. The calendar panel is now much bigger than the brief assumed. WS-F probed
   data.insideairbnb.com day by day and found that retention is per object, not a uniform 12
   months: 164 calendar vintages we did not hold are still served, 34 of them from 2024.
   The panel went from 34 markets x 5 vintages (164 files) to 34 markets x 328 vintages,
   2,574mm listing-night rows, 6.32 GB gzip. All downloaded into the main tree with URL, size
   and sha256 recorded. (sourced)

2. No Sep 2026 vintage exists yet. All 374 probes of 1 to 11 Sep 2026 across the 34 markets
   returned 403. The freshest calendar anywhere is late Aug 2026, which is the read we have
   for the quarter in progress and will stay so until the Sep dumps land, most likely after
   the 5 Nov print. (sourced)

3. The year-ago comparison is now same-season rather than three to five weeks off. 28 of 34
   markets have a 2025 vintage within 10 days of the 2026 anniversary, so the y/y can hold
   both horizon and season fixed. Forward blocked share is DOWN y/y in every region on a
   nights-weighted basis: NA -1.8 pp at 0 to 30 days ahead and -4.4 pp at 91 to 180, APAC
   -2.9 and -3.5, EMEA -0.9 and -1.8 (2 markets only), LatAm -0.3 and -0.7 with supply up 6
   to 12 percent. Pooled across the 28 markets, -1.7 pp at 0 to 30 days and -2.5 pp at 91 to
   180. (descriptive)

4. That level decline is not a demand signal. It is partly supply: a new listing arrives with
   an empty calendar and pulls the blocked share down mechanically, and the markets with the
   largest supply growth (LatAm, median listing-nights +6 to +12 percent) show the smallest
   declines, which is the opposite of what a demand story would produce. On the matched
   panel, which holds the listing set fixed, the picture reverses: the same forward stay dates
   in the same listings were being blocked slightly FASTER in 2026 than a year earlier.
   (descriptive, with the composition caveat doing real work)

5. Q3 in progress, the metric with the right basis. For the 11 markets that have a clean
   same-season pair of booking windows, net blocking over roughly 1 Jul to late Aug 2026 ran
   +0.18 pp per 30 days faster than the same window of 2025 (median across markets +0.30 pp),
   with gross new blocks per available night +4.0 percent y/y. By region: APAC +0.26 pp,
   LatAm +0.26 pp, EMEA -0.19 pp (rome only). That is a flat to very slightly positive pace
   read, nothing like an inflection in either direction. (descriptive)

6. A backtest now exists, and the metric fails it. Six quarters have a year-over-year flow
   observation; five have a disclosed nights print to score against. The sign is inverted:
   across those five the flow y/y correlates -0.43 with disclosed nights y/y and -0.53 with
   the acceleration in disclosed nights y/y, and the gross new-block rate correlates -0.56 and
   -0.68. 2Q26 carried the largest disclosed acceleration in the set (nights +10.34 percent,
   2.9 pp faster than 2Q25) and the weakest flow reading (+0.63 pp). With n = 5, only two of
   the five quarters on tight vintage pairs, and the sign backwards, this feature does not
   beat a naive last-quarter carry. Per the backtest protocol that is the report, and it is
   not tuned until it works. (causal claim refused)

7. Therefore: WS-F contributes a descriptive cross-check, not an input to the 3Q26 nights
   number. The honest statement is that the calendar pace is consistent with nights growth
   continuing near the recent run rate and gives no support for either a sharp deceleration
   or an acceleration; it cannot size either. The team baseline of +9.9 percent for 3Q26 is
   neither confirmed nor contradicted by this data, because the data has no units in nights.

8. The one unambiguous deliverable beyond the pace read: Theo's Jun 2026 booking curve is
   reproduced exactly. 140 overlapping market x snapshot x horizon cells on 28 markets, max
   absolute difference 0.0005 pp (his file rounds to five decimals), listing-night counts
   identical to four decimals. His metric and pipeline are correct; what he lacked was a
   second vintage per market, which is what turns a level into a flow, and which now exists.

## Tables

Full tables, including every market, are in `data/processed/q3nowcast/F/F3_note_tables.md`.

### 1. What the CDN still serves (F0, F0b)

| probe | candidates | served |
|---|---|---|
| 1 to 11 Sep 2026, all 34 markets | 374 | 0 |
| Aug to Oct 2024 window, 13 core cities | 364 | 0 outside the known dump dates |
| known 2024 and early 2025 dump dates, 13 core cities | 52 | 19 |
| dense day-by-day sweep, 2024-03 to 2025-08 | 10,610 | 164 (plus 24 stub objects under 1 MB, skipped) |

Retention is per object and wildly uneven. austin, nashville, paris and rome serve monthly
calendars back to Mar or May 2024. new-york-city, london, sydney and barcelona serve almost
nothing before the vintages we already held: london has 5 vintages in total, new-york-city 5.
That unevenness, not a policy, is what limits every 2024-based comparison to four markets.

### 2. The pace metric, latest vintage pair (Jun to Aug 2026), screened listings

Pooled over 34 markets, 97.4mm matched listing-nights, stay dates 1 to 180 days ahead:
net change in blocked share +4.00 pp, new blocks 14.97 percent of nights that were available,
reopenings 29.77 percent of nights that were blocked.

| region | net change, pp | new block rate, pct | reopen rate, pct |
|---|---|---|---|
| na (7) | +4.15 | 14.13 | 30.09 |
| emea (4) | +4.89 | 16.49 | 25.08 |
| apac (16) | +3.78 | 15.91 | 30.17 |
| latam (7) | +3.34 | 13.44 | 34.44 |

The reopening rate is the number to keep in view. Roughly 30 percent of blocked forward
nights reopen within two months. Whatever mix of cancellations, host reopenings and calendar
edits that is, it is far too large for "blocked" to be read as "booked".

### 3. Year over year blocked share, 2026 vintage against a prior-year vintage within 10 days
of the anniversary, 28 markets

| region | 0-30d | 31-60d | 61-90d | 91-180d | 181-372d | median supply change, pct |
|---|---|---|---|---|---|---|
| na (6) | -1.76 | -2.18 | -3.93 | -4.38 | -5.64 | +0.1 |
| emea (2) | -0.88 | -1.02 | -2.54 | -1.83 | -2.10 | -0.2 |
| apac (15) | -2.93 | -2.66 | -2.73 | -3.54 | -4.88 | +2.2 |
| latam (5) | -0.32 | +0.62 | +0.63 | -0.70 | -2.23 | +12.4 |

Nights-weighted differences in percentage points. The far-horizon buckets decline most in
every region, which is the signature of supply growth and of longer calendars being opened,
not of demand: a 2026 dump has more listings with more open far-dated inventory.

### 4. Q3 in progress: blocked share for the same calendar stay dates, Aug to 30 Sep

30 markets, window trimmed per market to the calendar dates both years cover and to a whole
number of weeks, lead-time offset priced from the market's own forward pair.

| region | markets | 2025 | 2026 | raw y/y, pp | lead-adjusted y/y, pp | mean offset, days |
|---|---|---|---|---|---|---|
| na | 6 | 0.423 | 0.435 | +1.40 | -0.50 | -6.9 |
| emea | 4 | 0.648 | 0.634 | -1.30 | -1.86 | -0.2 |
| apac | 15 | 0.447 | 0.457 | +0.61 | -0.55 | -4.9 |
| latam | 5 | 0.405 | 0.446 | +4.22 | +3.85 | -1.2 |

Pooled across the 30 markets: +0.83 pp raw, -0.13 pp adjusted; median market +2.02 pp raw,
+0.99 pp adjusted; 18 of 30 markets positive after adjustment. The adjustment is doing a lot
of work at a mean offset of 5 to 9 days, and the raw and adjusted figures straddle zero, so
the only defensible reading is "flat". london is the worst case in the table, a 14 day window
and a +27 day offset, because no Aug 2025 London calendar survives.

### 5. Year over year of the booking flow, 3Q26 window, 11 markets, all tight pairs

| region | markets | 2025 pace, pp per 30d | 2026 pace, pp per 30d | y/y, pp | new blocks y/y, pct |
|---|---|---|---|---|---|
| apac | 7 | 1.93 | 2.27 | +0.26 | +1.6 |
| emea | 1 | 2.70 | 2.51 | -0.19 | +14.7 |
| latam | 3 | 0.42 | 0.70 | +0.26 | +1.9 |
| pooled | 11 | | | +0.18 | +4.0 |

Eight of 11 markets positive. No NA market appears, and the reason is a gap in Inside
Airbnb's own schedule rather than retention: all seven NA markets have a Jul 2025 calendar but
none has a Jun 2025 one, so the closest reconstructable 2025 window is Jul to Aug 2025 at about
36 days, too short to set against the 64-day 2026 window under the 21-day interval tolerance.
NA is therefore missing from the one-year flow comparison, which matters because NA is the
segment the FY27 lap thesis turns on.

Against two years earlier, where austin, nashville, paris and rome do have a matching Jun to
Aug 2024 window, the 3Q26 pace is clearly faster, which is the expected sign given two years of
disclosed nights growth:

| market | 2024 pace, pp per 30d | 2026 pace, pp per 30d | 2y change, pp | new blocks, pct |
|---|---|---|---|---|
| austin | -0.39 | 1.86 | +2.25 | +2.9 |
| nashville | 1.75 | 3.49 | +1.74 | +2.3 |
| paris | 0.32 | 2.56 | +2.24 | +17.1 |
| rome | 2.50 | 2.51 | +0.01 | -11.7 |

Reading 5 and this table together: versus two years ago the booking pace is plainly faster,
versus one year ago it is flat. That is the shape of growth continuing at a similar rate, which
is all this metric can say.

### 6. Backtest, flow y/y against disclosed nights growth

| quarter | markets | tight | match score, days | flow y/y, pp (wtd) | new blocks y/y, pct | disclosed nights y/y, pct | disclosed accel vs prior year, pp |
|---|---|---|---|---|---|---|---|
| 2025Q1 | 1 | 0 | 68 | +2.69 | +47.3 | 7.92 | -1.58 |
| 2025Q2 | 2 | 1 | 35 | +1.28 | +13.7 | 7.43 | -1.25 |
| 2025Q3 | 4 | 4 | 9 | +1.74 | +5.6 | 8.80 | +0.31 |
| 2026Q1 | 2 | 0 | 34 | +2.46 | +20.0 | 9.15 | +1.24 |
| 2026Q2 | 8 | 4 | 20 | +0.63 | +0.5 | 10.34 | +2.91 |
| 2026Q3 | 11 | 11 | 8 | +0.18 | +4.0 | not yet printed | |

Correlation of the flow y/y with disclosed nights y/y over the five scored quarters is -0.43,
and with the acceleration in disclosed nights y/y is -0.53; for the gross new-block rate, -0.56
and -0.68. Both point the wrong way. A walk-forward RMSE ratio against naive, AR(1) and
prior-year is not computable on five scored observations, and with the sign inverted there is
nothing to salvage by fitting. Note also that market coverage rises monotonically down the
table, from 1 market in 2025Q1 to 11 in 2026Q3, so the early rows are close to single-market
noise and the correlation is not to be read as an estimate of anything.

## Method

Source. Inside Airbnb calendar dumps. A dump taken on snapshot date S carries one row per
live listing per forward stay date with available in {t, f}, out to about 372 days. Provenance
for all 328 files, with sha256, byte count and source URL, is in `F1_provenance.csv`; the 164
files WS-F added are in `F0b_new_vintages_manifest.csv`, where the downloaded byte count
matches the HEAD content length for all 164. Nothing is sampled: every listing in every dump
is used. A deterministic 10 percent sample, identical to overnight-2's WS-A, is available
behind `--sample` for cross-checking but was not needed.

Two metrics, and the difference between them is the whole note.

A level. Blocked share is blocked listing-nights over listing-nights for stay dates in a
horizon bucket measured from that dump's own snapshot date. available='f' is a stock mixing
confirmed bookings, host blocks, inactive listings and long-term-rental calendars. It is not
occupancy and not a booking count. This is Theo's `booking_curves_by_market.csv` metric, and
F1 reproduces it to within his file's rounding.

A flow. For a pair of vintages, restricted to listings present in both dumps and to stay dates
strictly after the later snapshot date, WS-F counts nights that went available to blocked (new
blocks), blocked to available (reopenings), and the change in blocked share. Listing set and
stay dates are held identical, so the change is a flow over the window between the dumps and
is the closest object in this data to net bookings made in that window. Reported Nights and
Seats Booked is also a booking-window metric, bookings minus cancellations in the quarter, so
the flow is the only construction here with the right basis. It is still not the same thing: a
new block can be a host closing a date, a reopening can be a cancellation or a host reopening
or a calendar edit, and the three cannot be separated.

Two regimes. "all" is every matched listing. "screened", the headline, drops listings whose
matched-future blocked share is 0.95 or higher in either vintage, since an inactive listing or
a long-term-rental calendar reads as permanently blocked and cannot transition. The screen
keeps a median 84 percent of matched listings. Median matched-row retention between vintages
is 87.7 percent, tenth percentile 65.1 percent.

Implementation. F1 makes one pass over the raw dumps and writes two daily aggregates, blocked
nights by market and vintage and stay date, and matched transitions by market and vintage pair
and stay date. Every horizon, month, quarter and window in F2 is built from those, so 6.3 GB
of gzip is read once. Matching is a dense listing by stay-date state matrix rather than a
sort-merge join, about ten times faster on the large markets, and verified to reproduce the
join byte for byte on all 21 austin pairs. Pair selection is consecutive vintages plus, for
each pair ending in 2026, the closest pair one and two years earlier when both ends fall
within 21 days of the anniversary and the interval is within 21 days; 321 pairs.

Vintage dates are not anniversaries, and two corrections are applied in the open. For
horizon-bucketed comparisons the horizon is identical by construction and only the stay-date
season shifts, so every row carries `vintage_offset_days` and a `tight_pair` flag at 10 days
or less, and the tight subset is the headline. For the fixed calendar window read, the prior
year uses the vintage closest in month and day to the current one rather than its own latest,
the window is trimmed to the calendar dates both years cover and to a whole number of weeks so
the weekday mix cannot move the answer, and the residual lead-time difference is priced with a
slope measured on the same market's own forward pair over the same stay dates. Using the prior
year's latest vintage instead, which is the obvious choice, flips the sign of the rome read
from -10.9 pp to +6.8 pp; the lead-time mismatch is that powerful, and any calendar y/y that
does not handle it explicitly is measuring the dump schedule.

Theo's other calendar assets were checked. `processed/airbnb_quant_panel_v3/calendar_daily.parquet`
is listed in his manifest but is not in the local copy of the share. `airbnb_quant_panel_v1/calendar_daily.csv.gz`
is on disk, 5.8mm rows, but it is a legacy 2016 to 2020 GitHub scrape of Boston, San Francisco
and Seattle with three snapshot dates and his own tier marked `supplemental_historical` and
`source_contained_descriptive_only`: no usable snapshot date means no horizon, so no pace
metric. His `inside_airbnb_current_manifest.csv` confirms 120 calendar files, all one vintage
per market dated Jun to Aug 2026, which is why his work stops at the level.

## What this can and cannot identify

A blocked-share level cannot be validated against reported Nights and Seats Booked, and no
amount of care with this data changes that. The level is a stock mixing bookings with host
blocks in an unobservable proportion. The panel is 34 markets chosen by Inside Airbnb's own
city coverage, which is not Airbnb's geographic mix and over-weights regulated urban markets.
And a level has no units in nights: there is no disclosed market-level nights series to
calibrate against, so the mapping from blocked share to nights does not exist. Any nights
number derived from a blocked-share level has assumed that mapping.

The y/y change in a matched flow has the right basis and, on the evidence here, no skill.
Five scored quarters, sign inverted, market coverage rising through the sample. Reasons it is weak are structural, not fixable by tuning: the
matched panel excludes every listing that entered or left between vintages, so it excludes
exactly where supply growth shows up; the flow is normalised per 30 days, which assumes a
locally linear booking build; and the 34 markets are not Airbnb.

Composition bites hardest in the level y/y. LatAm shows the smallest blocked-share decline and
the largest supply growth; NA shows the largest decline at long horizons with flat supply. Read
naively that says NA demand is deteriorating and LatAm is not. The matched flow for the same
markets says the opposite ordering at the margin. When the two disagree the matched flow is the
one to trust on direction, and neither is to be trusted on magnitude.

What would validate it. A Jun 2025 calendar for the NA markets, which would let the 3Q25
booking window be reconstructed for the region that matters; Inside Airbnb appears not to have
dumped those markets in Jun 2025 at all, and WS-F probed every day of Mar to Aug 2025 for all
seven. Or two more years of vintages
for enough markets to score the flow y/y on ten-plus quarters instead of four. Or a
reservation-level sample, which nothing public provides. Failing all three, the flow y/y stays
a direction-only cross-check.

Basis breaks. The Mar 2026 price basis change and the Dec 2025 to Feb 2026 missing-price
months affect price fields, not the availability column, so they do not touch this work. The
partial-scope monthly dumps do bite: a market simply has no vintage in a month it was not
dumped, which is why the pair plan is built per market from what exists. Twenty-four of the 188
served keys in the dense probe are stub objects of a few hundred bytes and are excluded by a
1 MB floor.

## Next evidence

1. Re-run F0b after the Sep 2026 dumps appear, which on the 2025 cadence is mid to late Sep.
   A Sep 2026 vintage turns the 3Q26 flow window into a complete quarter instead of one ending
   25 Aug, and it is the single highest-value addition before the print.
2. Ask Inside Airbnb directly for Jun 2025 calendars for the seven NA markets, and for any
   2024 calendars for new-york-city, london, sydney and barcelona. The NYC pre-LL18 request
   precedent in the team memory says requests are answered. Without the Jun 2025 NA files the
   region carrying the FY27 lap thesis has no one-year flow comparison.
3. Cross-check the matched flow against WS-E's review-based index at market level. Reviews are
   a stay-date metric and the flow is a booking-date metric, so a market where both move the
   same way is worth more than either alone. WS-F deliberately did not touch reviews.
4. Do not spend more time trying to make the level y/y work. It is contaminated by supply in a
   way that the data cannot undo, and the contamination runs in the direction that would
   flatter a bearish read.

## Files

Scripts, all in `analysis/src/q3nowcast/`:
- `F0_cdn_probe.py`: first CDN probe, Sep 2026 and the 2024 window for the 13 core cities.
- `F0b_cdn_dense_probe.py`: dense day-by-day probe and the downloader that put 164 new
  vintages into the main tree.
- `F1_calendar_pace.py`: one pass over the raw dumps to daily levels and matched transitions,
  with a self-test covering elapsed-night exclusion, the transition identity, the
  always-blocked screen, the deterministic sample and pair selection.
- `F2_pace_metrics.py`: horizon buckets, Theo reconciliation, y/y levels, y/y flows, the Q3
  window read, region roll-ups, backtest.
- `F3_report_tables.py`: the tables above.

Outputs, all in `data/processed/q3nowcast/F/`:
- `F0_cdn_probe.csv`, `F0b_cdn_dense_probe.csv`: every probed URL with status and size.
- `F0b_new_vintages_manifest.csv`: the 164 downloaded files with URL, bytes, sha256, local path.
- `F1_provenance.csv`: all 328 vintages read, with sha256, bytes, rows, listings, source URL.
- `F1_daily_levels.csv.gz`, `F1_daily_transitions.csv.gz`, `F1_pairs.csv`: the daily aggregates
  everything else is built from.
- `F2_levels_by_horizon.csv`, `F2_theo_reconciliation.csv`, `F2_transitions_by_horizon.csv`,
  `F2_yoy_levels.csv`, `F2_yoy_flows.csv`, `F2_q3_in_progress.csv`, `F2_region_summary.csv`,
  `F2_backtest.csv`.
- `F3_note_tables.md`: per-market and per-region tables behind this note.
- `markets/` holds one checkpoint file per market, 27 MB, and is deliberately not committed:
  it is regenerated by rerunning F1, and everything in it is already in the two combined
  daily tables.

Raw data added to the main tree (gitignored there):
`C:\Users\krish\citadel-abnb\data\raw\inside_airbnb_calendar\`, 164 new
`<market>_<date>_calendar.csv.gz` files, 3.44 GB, taking that directory from 164 to 328 files.
