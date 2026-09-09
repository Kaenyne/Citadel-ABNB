# LOS step 3: booked-run length buckets from Inside Airbnb calendars

`analysis/src/adr/14c_los_runs_panel.py` (`discover` / `download` / `aggregate`).
Method is the repo's existing booked-run extraction (`analysis/src/kitchen_wholehome_stay_length.py`):
a run is a contiguous block of `available == 'f'` nights per listing, active listings only
(`number_of_reviews_ltm > 0`). Cap raised from 30 to 90 so a 28+ bucket exists; both caps reported.

## What was pulled

164 of 170 target market-quarters, **2.88 GB**, dumps 2025-08-31 to 2026-08-31, 34 markets x five
snapshots (nearest Sep-25 / Dec-25 / Mar-26 / Jun-26 / Aug-26). The CDN has purged almost nothing:
every date probed inside a year came back 206. 128 snapshots used dump dates already on disk; day-by-day
probing recovered **36 new dumps** (mostly Dec-25 and Mar-26 for APAC/LatAm markets never captured by
Wayback), and their listings files were fetched alongside. Only Bogota and Sao Paulo are missing
pre-Jun-2026 — those scrapes do not exist. **11.2m booked runs.** Manifest:
`data/processed/adr/14c_calendar_manifest.csv`; per-listing runs in `14c_los_runs_by_listing/`; panel in
`14c_los_runs_panel.csv`.

## Bucket shares (nights, 90-cap, regional ex NYC/LA)

| region | snapshot | <7 | 7-27 | 28+ | 28+ occ-weighted | mean run (30-cap) |
|---|---|---|---|---|---|---|
| NA | Sep-25 → Aug-26 | .423 → .445 | .299 → .296 | .277 → **.259** | .138 → .135 | 4.80 → 4.67 |
| EMEA | Sep-25 → Aug-26 | .264 → .285 | .399 → .390 | .337 → **.324** | .198 → .181 | 6.12 → 5.85 |
| LatAm | Sep-25 → Aug-26 | .237 → .304 | .381 → .379 | .382 → **.317** | .172 → .123 | 6.04 → 5.70 |
| APAC | Sep-25 → Aug-26 | .267 → .293 | .433 → .424 | .300 → **.283** | .189 → .167 | 6.09 → 5.87 |

The direction is the same everywhere and it is small: the 28+ nights share falls 1.3-6.5pp over the year,
the <7 share rises, and mean run length shortens. LatAm moves most (-6.5pp), NA least. Global 10-K-weighted
28+ nights share: 32.2% → 29.8% unweighted, **17.4% → 15.5% occupancy-weighted** — the weighted series is
the one that lines up with Airbnb's disclosed ~17-18% of nights in 28+ stays, so weighting on
`estimated_occupancy_l365d` is doing real work, not cosmetic.

## Contamination and caveats

- **Host blocks.** 8.4-10.0% of runs exceed 90 nights and 12-14% exceed 30; the 90-cap raises mean run
  length by 1.6-2.3 nights over the 30-cap. Contamination is similar across regions, so cross-region
  differences survive it; levels do not.
- **Twelve Mar-26 dumps are short-stay-only scrapes** (every listing `minimum_nights <= 7`, scope 30-89% of
  the market's largest dump: Chicago, Nashville, Sydney, Melbourne, Singapore, Hong Kong, Belize and five
  Australian regionals). They structurally cannot contain a 28+ booking. Flagged `short_stay_only` and
  excluded from all aggregates; a `region_fullscope` block re-runs on scope >= 80% dumps only and moves the
  Mar-26 28+ share by under 3pp.
- **Regulatory minimums.** NYC (LL18) 57.7% of listings at min_nights >= 28, 50.1% of nights in 28+, mean run
  10.5. LA 26.8% / 32.8% / 7.8. Both kept in the market table, flagged, excluded from every aggregate.

## Versus the 10-K

Mean run (30-cap) vs disclosed 2025 ALOS: NA 4.91 vs 4.1 (1.20x), EMEA 5.97 vs 3.8 (1.57x), LatAm 6.04 vs
3.6 (1.68x), APAC 6.07 vs 3.3 (1.84x). The level bias is known, but the **rank order inverts** (Spearman
-1.0): Airbnb's longest-stay region is NA, the calendar proxy's is APAC/LatAm. The inflation factor is not a
constant, so this panel supports **within-region change over time**, not cross-region level comparison, and
must not be used to rebase regional ALOS.
