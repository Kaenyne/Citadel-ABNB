# Calendar reopening across 34 Inside Airbnb markets: is Rome's rise European, international or idiosyncratic?

Date: 2026-09-11. Author: Krishang Surapaneni (compiled with Claude Code).

## Bottom line

Rome is idiosyncratic. Extending the 10 September three-market calendar pilot to all 34 Inside
Airbnb markets on disk, with the pilot methodology frozen, Rome is the only one of the four
European markets whose short-run reopening rate rises from the early intervals to the late
intervals (Rome plus 1.46 points, London minus 2.34, Paris minus 2.18, Barcelona minus 0.85).
Pooled night-weighted European reopening excluding Rome falls 1.97 points. Rome's June to August
short-run level of 13.3% compares with 6.3% to 8.0% for the other three, and Rome is higher in
every fixed days-to-arrival band. If the 17 February 2026 global Reserve Now Pay Later rollout
were raising calendar reopening in Europe, London and Paris, the two largest European panels
here, should move with Rome. They move the other way.

There is a weak tilt toward non-US markets, but it does not support the rollout reading either.
The market-mean late-minus-early change is plus 2.12 points non-US minus US, with a label
permutation p of 0.259 on 32 markets. It is plus 1.81 points night-weighted and plus 1.93 points
after normalising every interval to 90 days. The tilt is driven by Australia and other Asia
Pacific markets, not Europe: the listing-clustered bootstrap gives Australia minus US plus 3.21
points (2.5 to 97.5 percentile 1.45 to 4.90) and Europe minus US plus 0.90 points (minus 0.45 to
2.18, spanning zero). Australia is the pre-registered opposite-season control, so the largest
increase sits in the hemisphere whose final interval is winter, which is not what a common
February treatment predicts.

Three further results cut against the rollout interpretation. First, in the pre-rollout September
to December interval the US level is already higher, not lower, than the rest of the world (mean
12.59% versus 8.72%), so the cross-sectional level ordering is the opposite of treatment status
and reflects composition. Second, the US change flips sign with interval length: raw minus 1.89
points, but plus 0.77 points once each interval is scaled to 90 days, because the June to August
window is 56 to 67 days while the earlier windows are 90 to 98. Third, San Diego, a market
treated since 3Q25, is one of only five markets whose increase has a bootstrap interval excluding
zero (plus 2.52, 0.25 to 4.75), alongside Rome, Taipei, Western Australia and Barossa Valley.

The tilt is also fragile. Dropping Barossa Valley, which has 29 stable listings and puts 98.6% of
its June to August reopenings in ten listings, moves the non-US market-mean change from plus 0.23
to minus 0.47 points. Restricting to markets with at least 1,000 short-run unavailable nights in
every interval and a top-ten listing share below 80% leaves non-US minus 0.50 and US minus 1.01,
a difference of 0.51 points.

What would have supported the RNPL-cancellation hypothesis: a broad-based non-US increase
concentrated in the two intervals after 17 February, visible in Europe including London and Paris,
absent or smaller in the already-treated US, with no matching increase in the opposite-season
Australian markets, and robust to dropping any single market. What would have weakened it: Rome
standing alone, the increase appearing in already-treated US markets, the increase concentrated in
opposite-season markets, and a pre-existing US level advantage. The second set is what the data
show. No haircut is applied to any nights, revenue or EPS forecast from this workstream, and the
team nights baseline (3Q26 plus 9.9%, 4Q26 plus 8.9%) is unchanged by it.

## Pre-registration (written into this file before `A2_cross_market_analysis.py` was run)

Recorded with only the three pilot markets' numbers known from the 10 September pilot.

- **H1 (primary).** Non-US markets show an increase in short-run reopening in the March to June
  and June to August intervals relative to the September to December and December to March
  intervals that is larger than the change in US markets. Statistic: market-level mean of the
  short-run (`screened_short_run`, `all_future`) reopening rate over intervals 3 and 4 minus the
  mean over intervals 1 and 2, averaged across markets within a group, then differenced non-US
  minus US.
- **H1 predicts** a positive non-US minus US difference if the 17 February 2026 global rollout
  raised the rate at which future unavailable nights become available again outside the US.
- **Pre-declared ways H1 could be weakened.** A difference near zero or negative; a positive
  average driven by one or two markets with Rome an outlier among the four European markets; or a
  September to December level difference already favouring non-US markets before the rollout.
- **Seasonality check, pre-specified.** The eleven Australian markets sit in the opposite
  hemisphere season. A rollout effect should appear there too; a seasonal artefact should reverse
  or vanish there.
- **Europe dispersion, pre-specified.** Report Barcelona, London, Paris and Rome individually and
  state whether Rome is an outlier.
- **Pre-rollout level test, pre-specified.** Compare the September to December short-run level US
  versus non-US. A large gap there is evidence that composition, not treatment, drives levels.
- **Uncertainty.** Listing-clustered bootstrap, 2,000 resamples of listings within market, on the
  June to August rate and on the change statistic.
- **No haircut** regardless of sign.

Post hoc additions, labelled as such below: duration normalisation to 90 days, the deep-cohort
screen, leave-one-out influence, and the interval 4 minus interval 1 variant.

## Tables

### Reproduction of the pilot before extending

| Check | Result |
|---|---|
| `--self-test` on venv Python 3.11.14 / pandas 3.0.5 | passed |
| `--self-test` on py -3.13 (3.13.14 / pandas 2.3.3) | passed |
| austin, rome, sydney `pairs`: 108 records, 1,512 field comparisons each | identical to pilot JSONs |
| austin, rome, sydney `triples`: 80 records, 880 field comparisons each | identical |
| austin, rome, sydney `coverage` and `provenance` (including SHA-256) | identical |
| austin recomputed on py -3.13 with pandas 2.3.3 | identical to the pandas 3.0.5 pilot output |

Every `pairs` and `triples` number for the three pilot markets reproduces exactly, on both
interpreters. The extension was only started after that check.

### Pre-registered primary statistic, by group

Change is the market-level mean of (interval 3 rate plus interval 4 rate) / 2 minus (interval 1
rate plus interval 2 rate) / 2, in percentage points of short-run reopening.

| Group | Markets | Mean change | Median | SD | Min | Max | Share positive | Mean I1 | Mean I4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| US | 7 | -1.89 | -1.56 | 3.58 | -7.20 | 2.52 | 0.43 | 12.59 | 9.77 |
| non-US | 25 | 0.23 | -0.38 | 4.52 | -6.37 | 17.00 | 0.48 | 8.72 | 11.18 |
| Europe (EMEA) | 4 | -0.98 | -1.52 | 1.76 | -2.34 | 1.46 | 0.25 | 11.02 | 8.89 |
| APAC Australia | 11 | 1.38 | 0.65 | 5.79 | -6.37 | 17.00 | 0.64 | 5.96 | 11.04 |
| APAC non-Australia | 5 | 1.12 | 0.75 | 3.63 | -3.99 | 4.65 | 0.60 | 11.76 | 13.46 |
| LatAm | 5 | -2.20 | -2.81 | 3.07 | -5.37 | 2.56 | 0.20 | 9.91 | 11.06 |
| non-US minus US difference | 32 | **2.12** | | | | | permutation p = **0.259** | | |

Bogota and Sao Paulo have two vintages, so one June to August interval each. They are excluded
from the change statistic and from the pre-rollout level comparison, and appear in
`A2_market_interval_table.csv` and the per-market bootstrap table.

### Europe dispersion: Rome against the other three

| Market | I1 Sep to Dec | I2 Dec to Mar | I3 Mar to Jun | I4 Jun to Aug | Change | Bootstrap interval on change |
|---|---:|---:|---:|---:|---:|---|
| rome | 11.60 | 7.79 | 9.00 | 13.32 | **+1.46** | 0.41 to 2.57 |
| barcelona | 9.00 | 6.38 | 7.42 | 6.25 | -0.85 | -2.37 to 0.62 |
| paris | 12.60 | 8.40 | 8.60 | 8.04 | -2.18 | -3.65 to -0.83 |
| london | 10.89 | 10.54 | 8.81 | 7.94 | -2.34 | -3.38 to -1.26 |

Rome's June to August short-run rate by fixed days to arrival, against the other three European
markets in the same interval:

| Market | 1 to 30 days | 31 to 60 | 61 to 90 | 91 to 180 |
|---|---:|---:|---:|---:|
| rome | 11.9 | 11.0 | 15.2 | 16.7 |
| london | 8.7 | 7.6 | 8.8 | 5.8 |
| paris | 8.9 | 5.9 | 8.0 | 9.4 |
| barcelona | 5.7 | 4.3 | 6.8 | 9.2 |

### Night-weighted pooled rates

Pooling all short-run reopenings and denominators in the group, rather than averaging market
rates, in percent.

| Group | I1 | I2 | I3 | I4 | Pooled change | I4 denominator nights |
|---|---:|---:|---:|---:|---:|---:|
| US | 11.19 | 11.57 | 9.94 | 9.87 | -1.48 | 40,747 |
| non-US | 8.97 | 9.92 | 9.55 | 10.00 | +0.33 | 269,515 |
| Europe | 11.39 | 8.42 | 8.70 | 9.83 | -0.64 | 103,609 |
| Europe excluding Rome | 11.27 | 8.88 | 8.52 | 7.70 | **-1.97** | 64,372 |
| Rome alone | 11.60 | 7.79 | 9.00 | 13.32 | **+1.46** | 39,237 |
| APAC Australia | 6.19 | 9.71 | 8.64 | 8.99 | +0.86 | 81,196 |
| APAC non-Australia | 11.07 | 12.25 | 13.69 | 12.11 | +1.24 | 42,153 |
| LatAm | 8.45 | 14.92 | 10.21 | 10.25 | -1.45 | 42,557 |

### Listing-clustered bootstrap, 2,000 resamples

| Contrast | Markets A / B | Point | 2.5th | 97.5th |
|---|---|---:|---:|---:|
| June to August level, non-US minus US | 25 / 7 | +1.38 | 0.02 | 2.72 |
| Change, non-US minus US | 25 / 7 | +2.06 | 0.69 | 3.47 |
| Change, Australia minus US | 11 / 7 | +3.21 | 1.45 | 4.90 |
| Change, Europe minus US | 4 / 7 | +0.90 | -0.45 | 2.18 |

This bootstrap resamples listings inside each market. It covers listing clustering only. It does
not cover between-market heterogeneity, which the permutation test does, and the two disagree: the
bootstrap interval on the non-US minus US change excludes zero while the market-label permutation
p is 0.259. The permutation test is the honest one for a claim about geographies, because the unit
that would carry a rollout effect is the market, not the listing.

Markets whose change interval excludes zero: barossa-valley +17.00 (5.09 to 26.97),
western-australia +3.81 (2.00 to 5.56), san-diego +2.52 (0.25 to 4.75), taipei +4.65 (1.27 to
8.35), rome +1.46 (0.41 to 2.57). Markets with intervals excluding zero on the downside include
chicago -7.20, buenos-aires -5.37, los-angeles -4.51, austin -4.34, santiago -4.14,
mornington-peninsula -6.37, london -2.34, paris -2.18, mexico-city -2.81.

### Pre-rollout level, September to December interval

Restricted to the 32 markets with five captures; Bogota and Sao Paulo have no pre-rollout interval.

| Group | Markets | Mean | Median | SD |
|---|---:|---:|---:|---:|
| non-US | 25 | 8.72 | 7.49 | 5.07 |
| US | 7 | 12.59 | 12.01 | 5.45 |

The US, already treated since 3Q25, starts the panel with the higher short-run reopening level.
That ordering is the opposite of treatment status. It is a reason not to read a later convergence
as a treatment effect, and it says the level of this proxy is set by market composition, which
this panel does not decompose.

### Robustness ladder on the non-US minus US difference

| Specification | non-US | US | Difference |
|---|---:|---:|---:|
| Pre-registered market means | +0.23 | -1.89 | **+2.12** (p = 0.259) |
| Night-weighted pooled | +0.33 | -1.48 | +1.81 |
| Duration-normalised to 90 days (post hoc) | +2.70 | +0.77 | +1.93 |
| Interval 4 minus interval 1 only (post hoc) | +2.46 | -2.82 | +5.28 (p = 0.139) |
| Intervals 55 to 105 days only | +0.24 | -2.63 | +2.87 |
| Deep cohorts: every interval at least 1,000 nights and top-ten share below 80% (post hoc) | -0.50 | -1.01 | **+0.51** |
| Excluding barossa-valley | -0.47 | -1.89 | +1.43 |
| Excluding chicago (largest single-market influence) | | | +1.24 |

No specification reaches conventional significance on a market-level permutation test, and the
specification that removes thin and host-concentrated cohorts removes three quarters of the
difference.

### Fixed days-to-arrival bands, pooled by group

| Group | Band | I1 | I2 | I3 | I4 | Change |
|---|---|---:|---:|---:|---:|---:|
| US | 1 to 30 | 9.02 | 7.65 | 8.52 | 9.99 | +0.92 |
| US | 31 to 60 | 14.91 | 11.81 | 9.68 | 9.76 | -3.64 |
| US | 61 to 90 | 11.61 | 12.31 | 9.29 | 9.06 | -2.79 |
| US | 91 to 180 | 12.17 | 12.48 | 10.55 | 9.54 | -2.28 |
| non-US | 1 to 30 | 6.78 | 7.78 | 8.20 | 9.84 | +1.74 |
| non-US | 31 to 60 | 9.73 | 8.95 | 11.00 | 9.10 | +0.71 |
| non-US | 61 to 90 | 9.36 | 10.23 | 10.53 | 10.19 | +0.56 |
| non-US | 91 to 180 | 9.93 | 11.33 | 9.15 | 9.95 | -1.08 |
| Europe | 1 to 30 | 8.93 | 6.08 | 6.45 | 9.75 | +0.59 |
| Europe | 31 to 60 | 14.49 | 7.17 | 9.90 | 8.29 | -1.73 |
| APAC Australia | 1 to 30 | 5.15 | 9.31 | 10.10 | 10.29 | +2.96 |
| APAC Australia | 31 to 60 | 7.07 | 9.24 | 13.77 | 9.41 | +3.44 |
| LatAm | 1 to 30 | 6.65 | 11.67 | 9.73 | 8.94 | +0.17 |
| LatAm | 31 to 60 | 8.28 | 17.30 | 8.62 | 9.89 | -3.53 |

The nearest band, 1 to 30 days to arrival, rises in the final interval in both the US and the rest
of the world. A movement present in the already-treated group is not evidence of the February
rollout. The full table for all groups and bands is in `A2_days_to_arrival_bands.csv`, and every
market by interval by band is in `A2_market_interval_table.csv`.

### Panel retention and reclosure across 34 markets

| Interval | Matched future rows retained, min / mean / max | Initially unavailable rows retained | Short-run reclosure by the next capture, min / mean / max |
|---|---|---|---|
| I1 Sep to Dec | 62.3 / 89.6 / 100.0 | 55.0 / 87.4 / 100.0 | 0.0 / 41.4 / 83.3 (31 markets) |
| I2 Dec to Mar | 26.0 / 70.8 / 94.1 | 27.5 / 62.9 / 95.1 | 0.0 / 35.5 / 59.4 (30) |
| I3 Mar to Jun | 77.4 / 90.9 / 96.6 | 66.3 / 88.7 / 97.5 | 6.2 / 33.4 / 51.0 (32) |
| I4 Jun to Aug | 89.5 / 94.0 / 100.0 | 88.8 / 93.0 / 100.0 | no later capture exists |

The December to March interval has the weakest panel, losing on average 37% of its initially
unavailable future rows. That interval sits inside the pre-registered early mean, so part of the
early-versus-late comparison rests on the least-retained interval. Roughly a third of short-run
reopenings become unavailable again by the next capture, which is the same order as the pilot and
is still not a measured rebooking offset.

## Method

Inputs are the 164 Inside Airbnb calendar dumps already on disk at
`C:\Users\krish\citadel-abnb\data\raw\inside_airbnb_calendar`, read-only, covering 34 markets. The
main tree was not modified. Thirty-two markets have five captures roughly quarterly from September
2025 to August 2026; Bogota and Sao Paulo have two (June and August 2026) because no earlier dump
was served. Source URLs, byte sizes and regions come from
`data/processed/adr/14c_calendar_manifest.csv`.

`A1_calendar_reopening_all_markets.py` is a generalisation of `analysis/src/rnpl_calendar_pilot.py`
with the analytical code copied verbatim: the SplitMix64 listing hash retaining one bucket in ten,
the run and edge construction, the exact listing-by-stay-date one-to-one join keeping only stay
dates strictly after the later capture, the four regimes (`all_matched`, `stable_all_five`,
`screened`, `screened_short_run`), the seven windows (`all_future`, four fixed days-to-arrival
bands, Q3 2026 and Q4 2026 stay windows), and `summarize_pair`. The only changes are operational:
markets are discovered from filenames, `source_url` is read from the manifest instead of a
hard-coded path table, a market with k captures yields k minus 1 pairs and max(k minus 2, 0)
triples so two-vintage markets do not crash, and each market writes one JSON checkpoint so a run
resumes. The regime key `stable_all_five` is kept for byte-level comparability and means present in
every capture the market has. All three pilot markets were rerun and every number in `pairs`,
`triples`, `coverage` and `provenance` matched the 10 September JSONs before the other 31 markets
were started. The run used the venv Python 3.11.14 with pandas 3.0.5 that produced the pilot;
Austin was additionally recomputed on py -3.13 with pandas 2.3.3 and produced identical numbers,
so the results are not pandas-version dependent.

All 34 markets were processed in three background processes balanced by compressed bytes, with
15.1 GB free of 31.7 GB at launch and a peak resident set of about 800 MB for London, the largest
panel.

`A2_cross_market_analysis.py` has two steps. The listing pass re-reads the raw calendars and
writes, per market, the per-listing initial-unavailable and reopened counts for the
`screened_short_run` / `all_future` cohort in every interval, importing the cohort definitions from
A1 and asserting that the per-listing sums equal the A1 aggregates for every market and interval
(all 34 passed). The analysis step assembles the 130-row market by interval table, computes the
pre-registered group differences, a 20,000-draw permutation test on the US label, the Australian
seasonality check, European dispersion, the pre-rollout level comparison, and the 2,000-resample
listing-clustered bootstrap. Intervals are aligned by index, not by calendar date, because capture
dates differ by up to five weeks across markets; interval length is carried in every row and varies
from 26 days (Mid North Coast interval 1) to 129 days.

Sourced facts used here are only the rollout anchors in `docs/RNPL_HANDOFF.md`: US RNPL began
during 3Q25, global eligible availability was announced 17 February 2026 with currency exceptions.
Everything else in this note is a descriptive statistic on availability transitions. Region labels
are destinations, not guest origins, and country is not exact treatment assignment because of the
currency exceptions.

## What this can and cannot identify

A reopening is one thing only: the same listing and the same future stay date was marked
unavailable at one capture and available at the next. It can be a guest cancellation, a host
removing a block, a host opening dates after a minimum-stay or pricing change, a channel-manager
sync, a relisting, or a data artefact. The files carry no RNPL label, no booking or cancellation
timestamp, no guest origin, no currency, no cancellation policy and no reservation identifier, so
nothing here assigns treatment or measures a cancellation. Reclosure is not a confirmed replacement
booking. The short-run screen narrows the cohort to interior unavailable runs of 1 to 14 days, but
short runs can still be host blocks and genuine long bookings are excluded by construction, so the
screened rate is a different population, not a more accurate estimate of the same population.

The panel starts in September 2025, after US RNPL launched, so there is no US pre-treatment period
and no 2024 baseline. That alone prevents a difference-in-differences design with the US as the
control: the US is treated in every interval observed. The non-US comparison straddles 17 February
2026, but it also straddles two seasons, different interval lengths, the April to August European
and Australian booking curves, World Cup demand in some markets, and any other product or policy
change in the same window. The capture dates are 60 to 100 days apart and the final interval is
roughly 30% shorter than the others, which moves the measured rate mechanically.

The sample is a deterministic 10% of listing identifiers in each market. It is not a
population-representative sample, it is not weighted to Airbnb nights, and listing-nights are not
independent observations. Several markets have cohorts small enough for one host to dominate:
Barossa Valley puts 98.6% of its final-interval reopenings in ten listings out of 29 in the stable
panel, and Hong Kong and Singapore also hit a 100% top-ten share in early intervals. Market-level
inference rests on 32 markets, so the permutation p values are the relevant uncertainty statement
and the clustered bootstrap understates it.

Finally, these are stay-date windows. Airbnb's reported Nights and Seats Booked is a booking and
cancellation transaction-date measure that includes seats. Nothing in this note can be multiplied
by a nights forecast, an RNPL GBV share or a backlog, and no haircut was applied.

## Next evidence

1. A reservation-event sample remains the only path that separates cancellation from host blocks.
   The minimum fields are in `docs/RNPL_HANDOFF.md`; a single property manager with Rome and
   London inventory would now be worth more than another 34-market sweep, because the question has
   narrowed to why Rome moves when London and Paris do not.
2. Rome-specific checks that need no new licence: the Lazio or Roma Capitale tourist-tax and
   CIN registration series for a supply or compliance shock in the June to August window, Jubilee
   2025 pilgrimage volumes rolling off into 2026, and the Rome listing-level run-length
   distribution against the other European markets. A supply or event explanation is currently as
   plausible as a cancellation explanation and is cheaper to test.
3. Higher-frequency captures from here forward. Quarterly snapshots miss cancel-and-refill inside
   the interval, which biases every reopening rate downward by an unknown and time-varying amount.
   Weekly or fortnightly captures of four to six markets, including Rome, London, San Diego and one
   Australian market, would let the same screens run on equal-length intervals.
4. A classification validation on any known-booking sample, to quantify how often an unavailable
   run is a booking. Until that exists the level of every rate in this note is uninterpretable even
   though the cross-market comparisons are internally consistent.
5. Reconcile against the currency-exception list if it can be sourced, and re-run the non-US
   contrast excluding markets whose currencies were excluded at the February rollout. That is the
   one refinement that could turn this design into something closer to a treatment comparison.

## Files

Scripts:
- `analysis/src/overnight2/A1_calendar_reopening_all_markets.py`
- `analysis/src/overnight2/A2_cross_market_analysis.py`

Outputs under `data/processed/overnight2/A/`:
- `markets/<market>.json`, 34 files: provenance with SHA-256, coverage, all regime by window pairs,
  all triples. The Austin, Rome and Sydney files are byte-comparable with
  `outputs/rnpl-calendar-pilot-20260910/`.
- `listing_counts/<market>.csv`, 34 files: per-listing short-run initial-unavailable and reopened
  counts by interval, the bootstrap clusters.
- `A2_market_interval_table.csv`: 130 market by interval rows with broad, stable, screened and
  short-run rates, reclosure, retention, top-ten concentration, the four days-to-arrival bands and
  the duration-normalised rate.
- `A2_market_changes.csv`, `A2_group_summary.csv`, `A2_pooled_rates.csv`,
  `A2_pre_rollout_levels.csv`, `A2_days_to_arrival_bands.csv`, `A2_duration_normalised.csv`,
  `A2_leave_one_out.csv`, `A2_bootstrap_markets.csv`, `A2_bootstrap_contrasts.csv`.
- `A2_console_output.txt`: the full printed run.

Read-only inputs: `C:\Users\krish\citadel-abnb\data\raw\inside_airbnb_calendar` (164 files) and
`C:\Users\krish\citadel-abnb\data\processed\adr\14c_calendar_manifest.csv`. Source: Inside Airbnb,
CC BY 4.0.

Reproduce:

```text
python analysis/src/overnight2/A1_calendar_reopening_all_markets.py --self-test
python analysis/src/overnight2/A1_calendar_reopening_all_markets.py
python analysis/src/overnight2/A2_cross_market_analysis.py --listing-pass
python analysis/src/overnight2/A2_cross_market_analysis.py --reps 2000
```
