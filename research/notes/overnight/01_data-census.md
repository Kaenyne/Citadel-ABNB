# 01 - Data census and predictive-mapping matrix

Krish Surapaneni / overnight run, 6-7 Sep 2026. Workstream 01.

Data: `data/processed/overnight/01_data_census.csv` (217 rows, 19 columns).
Script: `analysis/src/overnight/01_data_census.py` (`py -3.13 analysis/src/overnight/01_data_census.py` rebuilds the CSV and prints the tallies below; it also checks that every cited path still exists).

## Bottom line

- **217 distinct series or datasets** are in the team's hands or one script away. 197 are on this machine right now, 10 sit on Theo's external volume or a licensed Drive, 10 are named-but-never-acquired channels.
- **176 are Krish's, 34 are Theo's, 7 belong to nobody** (identified sources that were never pulled).
- **108 have been tested against a KPI, a guide or the stock; 69 were produced tonight and are untested by construction; 40 have never been tested at all.** 154 rows carry a concrete, named untested idea.
- **Five things survive contact with out-of-sample discipline.** Everything else is either in-sample only, a 2023 recovery trend, or a target rather than a feature:
  1. **FX to ADR** (D087/D088/D241/D263): USD broad y/y to the ADR FX effect r -0.95, EUR/USD r +0.97, +0.46 pp per pt; walk-forward RMSE 0.42x AR(1) with 92% sign accuracy. The only mechanical forecast the team owns.
  2. **Guide midpoint plus trailing cushion** as the revenue forecast (D005/D037/D038): MAE 1.1%, beat 19/19.
  3. **Nights-acceleration sign sets the day-1 reaction** (D001/D042/D247): 17 of 21.
  4. **Price index to reported ADR** (D262): walk-forward 0.65x AR(1) - but it is mostly the FX term again.
  5. **Prior-quarter S&M cash deleverage vs the next day-1 excess** (D009): r +0.59, n 17, one hit in ~60 tests. Pre-register it or drop it.
- **The strongest result of the night is a negative one:** of the 233 point-in-time feature-target cells in `08_feature_tests_all.csv` (Trends 152, Eurostat 32, backlog 21, Inside Airbnb 18, components 10), **zero beat an AR(1) walk-forward**. Alt data explains ABNB's KPIs in-sample and forecasts none of them.

## How to read the CSV

One row per series or dataset. Columns: `id` (D001-D297), `name`, `file_or_location` (repo-relative; `MAIN:` = the main tree `C:\Users\krish\citadel-abnb`, `citadel-abnb-predict/` = the predictive worktree), `owner`, `source`, `licence`, `frequency`, `first_date`, `last_date`, `n_obs`, `point_in_time_lag` (when it becomes knowable relative to the print), `maps_to`, `role`, `tested_already` (with the note that tested it), `verdict_so_far` (<=15 words), `untested_idea`, `combinable_with` (other ids), `build_forward` (does it need repeated capture before 5 Nov), `on_disk`.

Sections in the script, in id order: A company KPIs and financials (D001-D024), B guidance (D030-D038), C market data and reactions (D040-D046), D transcripts and text (D050-D057), E peer prints (D060-D062), F macro (D070-D101), G Eurostat and EU platform (D110-D115), H Inside Airbnb 13-city panel (D120-D131), I Theo's Inside Airbnb current cohort (D140-D143), J Common Crawl (D150-D155), K regulatory (D160-D171), L academic replication data (D180-D182), M licensed and off-machine terminal exports (D190-D193), N build-forward and not-yet-acquired channels (D200-D209), O derived analysis panels (D220-D229), P tonight's overnight outputs (D230-D288), Q audit fill-ins (D290-D297).

## Rows by target KPI

A row can map to more than one KPI, so the counts sum to more than 217.

| Target KPI / line | Rows | Tested | Produced tonight | Never tested | What actually works |
|---|---:|---:|---:|---:|---|
| Nights | 82 | 35 | 26 | 14 | Nothing forecasts the level. Accel *sign* sets day-1 (D001). Hotel RevPAR, Eurostat, Trends, IA all coincident only |
| ADR / price | 45 | 17 | 18 | 8 | FX channel (D087/D088/D241/D269/D271). Claims-to-ADR-ex-FX is a WATCH (D078), not promoted |
| Revenue | 36 | 18 | 16 | 1 | Guide + cushion (D038). Funds-held backlog is in-sample only (D259) |
| Stock reaction / positioning | 28 | 13 | 9 | 6 | Nights-accel sign; S&M deleverage tilt (weak). New tonight: 466 analyst actions (D267), short interest (D268), FF factors (D266) |
| Supply | 26 | 16 | 4 | 5 | Descriptive only. Supply index r -0.14 with nights (D260) |
| Regulation | 25 | 17 | 1 | 5 | Bottom-up cohort losses (D296) into a Monte Carlo (D161) and a 3-line model overlay (D280) |
| Guidance | 25 | 14 | 4 | 5 | Guide behaviour is highly regular (beat 19/19, FY floors 4/4); what management *says* is not yet coded (D235 is new) |
| GBV | 21 | 7 | 11 | 2 | Nothing. The one macro hit (real PCE) flips sign across windows |
| Cost lines / EBITDA margin | 20 | 9 | 10 | 1 | Margin nowcast needs print-day S&M (D007); lagged inputs only tie the guide |
| Regional nights | 16 | 6 | 7 | 2 | Now numeric for 23 quarters (D270/D271/D272) but never tested |
| Take rate | 8 | 6 | 1 | 0 | A timing line, guided flat; RNPL broke the backlog relationship from 3Q25 |
| SBC / share count | 7 | 5 | 2 | 0 | Fully mapped; -3% to -4% shares a year, SBC 13.1% of revenue |
| Valuation | 7 | 1 | 6 | 0 | New tonight (D282-D288); ABNB 1% to 95% above fitted peers depending on spec |
| FCF | 5 | 2 | 1 | 2 | FCF/EBITDA 105-111% is float plus interest income; nobody models it |
| Metadata / provenance | 15 | 1 | 7 | 7 | Coverage register, disclosure log, source excerpts, acquisition manifests |

Coverage by frequency: 50 quarterly, 33 monthly, 18 per print, 16 one-off, 13 test-result tables, 11 annual, 8 event, 7 daily, 5 weekly, 4 per Inside Airbnb dump.

Licences: 111 public (SEC/company), 32 public domain (FRED/BEA/EDGAR), 20 CC BY 4.0 (Inside Airbnb - attribute on slides), 7 Yahoo-terms (do not redistribute), 4 licensed (Third Bridge, LSEG, FactSet, Bloomberg - do not quote at length), 3 Eurostat re-use (attribute).

## Gaps: KPIs with no data

These are the places where the model has to assume rather than measure.

1. **Consensus at each call (D036).** All 23 rows of Theo's `consensus_snapshots.csv` are empty. Without it "beat vs consensus" cannot be separated from "beat vs guide", and no crowding measure exists. Plan-of-attack branch 3 (Hough Hall terminal) is still open. Tonight's 466 analyst actions (D267) are the closest substitute and are a proxy, not consensus.
2. **Occupancy.** Nothing in the repo measures it. `booking_curves_by_market.csv` and D292 are a *blocked-night rate*, which moves for reasons unrelated to demand. Inside Airbnb's own nights/revenue estimates (D129) are model output, not data.
3. **Quarterly ADR ex-FX before 4Q25 (D004).** Only three quarters are letter-stated; everything earlier is derived from an annual FX impact. The FX mechanism - the team's single best relationship - is fitted on n 14.
4. **Take-rate mechanics.** RNPL share of GBV is disclosed only as ">20% in Q2 26"; single-fee migration dates are not in any file. Take rate is the KPI with the most bulls and the least data.
5. **Segment revenue.** Experiences, Services and Hotels have no disclosed revenue line; D279's scenarios are assumptions with a source, not measurements. Management has declined to quantify Experiences attach, hotels scale, AI spend and long-term margin across four years of calls (D053).
6. **Brand vs performance marketing split.** S&M went 18.0% to 24.3% of revenue between 2Q22 and 2Q26 and the team cannot say which half moved. The 10-K gives an annual hint that nobody has extracted (D008).
7. **Headcount and SBC per employee.** Needed to forecast the FY27 SBC guide; not extracted (D010).
8. **Cross-border share of gross nights stops at 2024Q1 (D245).** This is exactly the number that sizes FX exposure, and Airbnb stopped giving it. See D232/D233 for the full list of stopped disclosures.
9. **Regional nights in numbers.** Airbnb gives bands and adjectives; D270 converts 23 quarters of phrases into bands, which is the best available and still not an actual series.
10. **8-K acceptance timestamps for all 23 prints (D033).** Theo's log has 14 (D293); the remaining 9 mean the point-in-time cutoff for a third of the sample is a webcast-start proxy.
11. **US daily demand.** TSA throughput (D101) 403s to non-browser clients; the substitute (air RPM, D085) lands three months late and is useless before a print.
12. **Card panel, app downloads, web traffic, AirDNA, NTTO arrivals (D201-D205).** All identified in the Crossover access map, none captured.

## Indexes worth building

Ranked by expected value, given tonight's zero-of-233 result.

1. **FX contribution index (already half-built).** D242's schedule turns today's spot into next year's ADR and revenue points using D269's Airbnb-weighted 22-currency basket instead of the broad dollar. Beats AR(1) 0.42x. Refresh weekly to 5 Nov. This is the one index the pitch should quote.
2. **Guide-plus-cushion baseline as the house forecast.** Not glamorous, MAE 1.1%, and it beats everything the team built.
3. **A positioning index** from D267 (net upgrades minus downgrades, mean PT drift in the 30 days before a print), D268 (short-interest change) and D044 (implied move). Never tested, plausible on the day-1 target, and cheap.
4. **Call-tone index** from D235's 60 features across 23 calls, pre-registered against the next guide direction and day-1 sign. The one text idea that has never been tried on ABNB.
5. **A stopped-disclosure watchlist** from D232/D233: every series the model depends on whose definition changed or ended mid-sample.
6. **Do not build:** a broader demand index. D261 and D263 show the equal-weight version loses to AR(1) by 1.28-2.07x, and the NNLS version that "wins" does so on 12 folds with weights that move every quarter.

## Theo's off-machine bulk data

Ten rows sit on Theo's external volume (`/Volumes/PortableSSD/ABNB_DATA_EXPANSION`) or a licensed Drive, with manifests in `data/manifests/`. What each would allow if it were copied over:

| id | What it is | What it would allow |
|---|---|---|
| D140 | Inside Airbnb current listings, 120 markets / 35 countries, 982k listings | Global supply coverage instead of 13 cities; the IA tests (D257) fail partly on coverage |
| D142 | Inside Airbnb reviews, 120 markets, 67.5M review rows with dates | A true review-velocity demand proxy at global scale, monthly, back years |
| D143 | `license_text` on ~46% of listings across 18 countries | Direct measurement of registration compliance - the regulatory case's weakest link |
| D170 | 25 municipal STR registries / 17 portals / 109,343 rows | Enforcement measurement (registered vs listed) beyond Barcelona and Maui |
| D113 / D114 / D115 | Full Eurostat `tour_ce_*` set plus 41 tourism products, UK CAA, StatCan, DataSF | Capacity and total-nights denominators so EU platform nights become a share, not a level |
| D180-D182 | Harvard Dataverse, Zenodo academic panels (Melbourne, Rio, NZ, Barcelona, Brazil, Vienna) | Historical ADR and revenue at listing level for periods Inside Airbnb no longer serves |
| D190 | Bloomberg exports, 6,365 rows of consensus estimates, revisions and comps | Closes the single largest gap in the whole census (D036) |
| D191 | FactSet CallStreet PDFs of all 23 calls | Cleaner transcript text than the stockanalysis.com scrape for 2020-22 |
| D098 | Theo's FRED cohort, 11,516 observations | Nothing new: duplicates D070-D087 |

Priority if only one can be moved: **D190** (consensus), then **D142** (reviews at scale), then **D170** (enforcement).

## Corrections to existing work

Recorded here rather than edited into other people's files, per the brief.

1. `data/processed/overnight/02_crosscheck.csv` is **empty** (2 bytes, no header) as of 01:41. The letter-vs-XBRL cross-check is the only thing validating the reconciled KPI panel `02_kpi_panel_quarterly.csv`. Workstream 02 should re-run.
2. `data/processed/overnight/10_regional_revenue_xbrl.csv` has a **comment as its first line**, so pandas reads the comment as the header. Any downstream read of that file is wrong. Workstream 10 should re-write with a proper header.
3. The backlog headline in `2026-09-05_eu-platform-and-backlog.md` ("unearned fees R^2 0.96 on next-quarter revenue growth") is **in-sample only**. Tonight's walk-forward (`08_backlog_tests.csv`, D259) puts funds-held y/y lag 1 at RMSE 1.85x AR(1). The relationship should be described as coincident, not predictive, before it reaches a slide.
4. `research/sources/README.md` **reuses S-numbers**: S30, S32, S33, S34, S35, S36 and S37 each appear twice with different meanings (e.g. S32 is both the 10-K geographic note and Inside Airbnb; S33 is both peer XBRL and Common Crawl). Citations of the form "(S33)" are ambiguous. Renumber before the deck cites sources.
5. `theos-past-research/research/transcripts/*.csv` (D057) are **empty schemas** - `guidance_facts`, `reported_metrics`, `management_themes` were never populated. Anything relying on them needs another source.

## For the model

Exact parameters this workstream supplies. All are pointers into the census; the census is the deliverable.

| Parameter | Value | Unit | Source |
|---|---|---|---|
| Series available to the driver model | 217 | count | `data/processed/overnight/01_data_census.csv` |
| Series with a surviving out-of-sample signal | 5 | count | D001, D005/D038, D087/D088/D241, D262, D009 |
| FX effect on ADR per +1 pt USD broad y/y | -0.59 | pp | D240 (`05_macro_sensitivities.csv`), n 14, r -0.95, perm p 0.001 |
| FX effect on ADR per +1 pt EUR/USD y/y | +0.46 | pp | D241 (`05_fx_fits.csv`), n 14, r 0.97 |
| FX effect on revenue per +1 pt USD broad y/y | -0.44 | pp | D240, n 13, r -0.81 |
| Revenue forecast rule | guide midpoint + trailing-4 cushion | MAE 1.1% | D037/D038 |
| Mean revenue beat vs midpoint | +2.5% (post-2022 +2.2%, sd 1.15) | % | D037 |
| Point-in-time alt-data features beating AR(1) | 0 of 233 | count | D252 (`08_feature_tests_all.csv`) |
| Indexes beating AR(1) walk-forward | 2 of 21 (FX 0.42x, price 0.65x) | ratio | D263 (`08_index_backtests.csv`) |
| Model input table to use | `02_kpi_panel_quarterly.csv` (24 quarters, 30 metrics) | - | D230, pending the D234 cross-check |
| Regulatory overlay | apply D280's drag to EMEA nights, not global revenue | % | D280 / D161 |

## For the 5 Nov card

Nine rows are frozen forecasts that can be scored on print day. Score all of them; that is how the team learns which of tonight's work was real.

- **D264** `08_q3_2026_nowcast.csv`: 13 point forecasts with bands. Nights 22.9% (14.8-31.0) against a naive 10.3% - implausibly high, and the honest reason to score rather than quote it.
- **D242** `05_fx_schedule.csv`: 3Q26 FX lift on ADR ~+0.8 pp (vs +1.3 in 2Q26). The single number most likely to be right.
- **D015**: funds-held read implies 3Q26 revenue $4.56B against a $4.69-4.77B guide. If it misses, drop the series.
- **D007**: margin nowcast 49.1-49.8% against the 50.1% ceiling.
- **D262 / D254**: price index and Trends nights nowcast.
- **D009**: the pre-registered prior-quarter S&M-deleverage tilt on day-1 direction.
- **D001**: does 3Q26 nights y/y accelerate past 2Q26's 10%, and does the accel-sign rule hold again (17 of 21 so far).

Forty rows are flagged `build_forward = yes`: they need repeated capture between now and 5 Nov (options ledger, Trends weekly, FX daily, IA dumps, analyst actions, peer multiples, regulatory catalysts). Those captures are the difference between a scoreable card and a story.

## Method and honesty notes

- Row counts, first and last dates and column lists were read with pandas (`py -3.13`) from the files themselves on 6 Sep 2026; off-machine rows are described from `data/manifests/`, `theos-past-research/docs/` and `ABNB-Crossover/03_ACCESS_MAP.md` and are marked `on_disk = off-machine` or `n/a`.
- **No new statistical tests were run.** Every `verdict_so_far` is either quoted from an existing note or read directly out of an existing results table (`08_index_backtests.csv`, `08_feature_tests_all.csv`, `05_macro_sensitivities.csv`, `12_peer_regressions.csv`). Where a verdict comes from tonight's still-unwritten workstreams the row is marked `in flight (ws NN)` and the note author has not seen their reasoning, only their output.
- The 69 `in flight` rows will need their verdicts rewritten once workstreams 02-12 publish their notes. The census is built to be re-run: edit the row table in the script, re-run, and the CSV and tallies regenerate.
