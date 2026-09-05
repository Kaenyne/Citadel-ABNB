# Peer read-through: do BKNG, EXPE, MAR and HLT prints predict Airbnb's print and reaction?

- Date: 2026-09-06
- Author: Krishang Surapaneni (compiled with Claude Code)
- Question: peers report 1 to 3 weeks before Airbnb in some quarters. Does anything in those prints (room nights, gross bookings, RevPAR, the peer's own stock reaction) predict Airbnb's nights growth, its revenue beat versus the guide midpoint, or its day-1 excess return?
- Scripts: `analysis/src/predictive/02_peer_fetch.py` (downloads), `02_peer_prints_build.py` (parses the releases into `data/processed/predictive/02_peer_prints.csv`, `02_peer_prints_long.csv`, `02_peer_sources.csv`), `02_peer_readthrough_tests.py` (writes `02_peer_readthrough_results.csv`, `02_peer_readthrough_loo.csv`, `02_peer_readthrough_panel.csv`).

## Sources

| What | Where | Notes |
|---|---|---|
| Peer earnings press releases, Q4 2020 to Q2 2026 (93 filings) | SEC EDGAR 8-K Item 2.02, exhibit 99.1, via the submissions API (`https://data.sec.gov/submissions/CIK##########.json`) and each filing's `index.json`. BKNG CIK 1075531, EXPE 1324424, MAR 1048286, HLT 1585689. Local copies in `data/raw/peers/<TICKER>/` (gitignored), manifest `data/raw/peers/peer_filings_manifest.csv` | Chosen over the IR sites because file names are stable and the filing timestamp gives the release time. Expedia's Q4 2021 release (10 Feb 2022) was filed under Item 9.01 only and is added explicitly. Hilton's 19 Jan 2021 Item 2.02 8-K (preliminary update) is skipped. Every parsed number has its exhibit URL and the extracted sentence or table row in `02_peer_sources.csv` (256 rows). |
| Peer revenue cross-check | SEC XBRL companyfacts `data/raw/xbrl/BKNG.json`, `EXPE.json` (`Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`; Q4 = FY less Q1 to Q3) | Release-stated revenue growth matches XBRL within rounding in every quarter (`bkng_rev_yoy` vs `bkng_rev_yoy_xbrl`). |
| Daily closes ABNB, BKNG, EXPE, MAR, HLT, QQQ | `data/raw/prices/<TICKER>_daily.csv` (Yahoo Finance via yfinance, saved by the team) | stooq.com sits behind a JavaScript check and returns no CSV to scripts. |
| ABNB nights, GBV 1Q21 to 2Q26 | `data/processed/abnb_quarterly_kpis_from_study.csv` (shareholder letters) | 2019 to 2020 quarterly nights and GBV parsed from the Q4 2021 letter's history table (`data/raw/letters/4Q21_d251410dex991.htm`) so 2021 y/y and the seasonal-naive baseline exist. |
| ABNB revenue guide vs actual | `data/processed/abnb_revenue_guidance_vs_actual.csv` | Beat versus midpoint, 2021Q4 on. |
| ABNB and QQQ reactions | `data/external/abnb_earnings_reactions.csv` | 1-day excess return per print. ABNB release date taken as the trading day before the reaction date (ABNB reports after the close). |

## Bottom line

1. **The calendar rarely cooperates.** Under a strict point-in-time rule (peer 8-K filed before Airbnb's release, or the same morning), BKNG is usable in 12 of 22 quarters, EXPE in 11, MAR in 18, HLT in 20. In every Q4 print (February) BKNG reports 6 to 9 days *after* Airbnb, and from 2024 on EXPE has reported the same afternoon as Airbnb or later in 7 of 10 quarters. Marriott is usually 1 to 7 days ahead; Hilton 1 to 2 weeks ahead.
2. **Level correlations look spectacular and mean little.** Over 2021Q1 to 2026Q2 BKNG gross bookings y/y vs ABNB nights y/y has r = 0.999 (n = 12) and HLT RevPAR y/y r = 0.93 (n = 20): the COVID base year drives everything. Drop 2021 and 2022 and the Spearman rank correlation of BKNG room nights y/y with ABNB nights y/y falls to 0.12 (n = 9, p = 0.76); the Pearson 0.95 survives only because of 2023Q1 (BKNG +38%, ABNB +19%). From 2024Q1 the same pair is r = -0.46 (n = 8). Nothing from BKNG passes a permutation test once the recovery quarters are out.
3. **The hotel RevPAR prints are the only pre-print numbers with a stable read-through to Airbnb's growth.** 2023Q1 to 2026Q2: MAR worldwide RevPAR y/y vs ABNB nights y/y r = 0.91, Spearman 0.74 (p = 0.006), permutation p = 0.004, n = 12; HLT system-wide RevPAR y/y r = 0.88, Spearman 0.78 (p = 0.002), permutation p = 0.001, n = 13. Their quarter-on-quarter *changes* also line up with Airbnb's nights acceleration (MAR accel r = 0.77, p = 0.003, n = 12; HLT accel r = 0.61, p = 0.03, n = 13), and change-concordance is 56 to 73 percent. From 2024Q1 (n = 9) the coefficients stay positive (r = 0.50 to 0.56) but lose significance.
4. **Even the good signals do not beat "last quarter's number".** Leave-one-out OLS of ABNB nights y/y on a peer signal, 2023Q1 to 2026Q2: MAR RevPAR y/y MAE 1.19 pp vs 1.90 pp for the naive prior-quarter forecast and 7.2 pp for the seasonal naive (n = 12); HLT 1.20 vs 2.23 (n = 13). BKNG room nights y/y is *worse* than naive (3.01 vs 1.47, n = 9). From 2024Q1 ABNB nights growth has sat in a 7.4 to 12.4 percent band, and a plain leave-one-out mean (MAE 0.75 to 1.19 pp) beats every peer model and every baseline. Adding a peer signal to an AR(1) helps mainly in the regime with big swings (2021 to 2022, better for 11 of 15 signals); in 2024Q1 on it makes the AR(1) worse for 10 of the 11 signals with enough data.
5. **Nothing predicts the beat or the stock reaction.** Against ABNB revenue beat vs midpoint (2023Q1 on): every peer signal |r| < 0.35 except EXPE gross bookings (r = -0.78, n = 6, wrong sign, q = 0.38). Against ABNB day-1 excess return: the best is BKNG's own day-1 excess return, r = 0.60 (n = 9, p = 0.09, permutation p = 0.06, BH q = 0.41), sign concordance only 44 percent; all others |r| < 0.53 and none is significant. Over the full sample every reaction cell has p > 0.2.
6. **For the 5 Nov 2026 print, the usable pre-print inputs are HLT (about 21 to 22 Oct), BKNG (about 27 to 28 Oct, with a quantified Q4 room-nights guide since Jul 2025) and MAR (about 3 Nov).** EXPE will not be usable: it reported the same afternoon as Airbnb in Q3 2025 and Q3 2024. Treat MAR and HLT RevPAR as a sanity check on the direction of ABNB nights growth (positive change-concordance of 56 to 73 percent), not as a point forecast, and treat BKNG's number as a headline-risk indicator only: it has not predicted Airbnb's growth, beat or reaction since 2023.

## Peer print calendar (who reports first, days of lead over Airbnb's release)

Lead = Airbnb release date minus peer 8-K filing date. Positive means the peer printed first. BKNG and EXPE file after the close (about 20:00 to 21:00 UTC), MAR and HLT before the open, so a lead of 0 is usable only for the pre-market filers (the one case is EXPE on 3 Aug 2023, filed 13:01 UTC).

| Quarter | ABNB release | BKNG (lead) | EXPE (lead) | MAR (lead) | HLT (lead) | First to print |
|---|---|---|---|---|---|---|
| 2021Q1 | 2021-05-13 | 05-05 (+8) | 05-06 (+7) | 05-10 (+3) | 05-05 (+8) | BKNG, HLT |
| 2021Q2 | 2021-08-12 | 08-04 (+8) | 08-05 (+7) | 08-03 (+9) | 07-29 (+14) | HLT |
| 2021Q3 | 2021-11-04 | 11-03 (+1) | 11-04 (0, after close) | 11-03 (+1) | 10-27 (+8) | HLT |
| 2021Q4 | 2022-02-15 | 02-23 (-8) | 02-10 (+5) | 02-15 (0, pre-mkt) | 02-16 (-1) | EXPE |
| 2022Q1 | 2022-05-03 | 05-04 (-1) | 05-02 (+1) | 05-04 (-1) | 05-03 (0, pre-mkt) | EXPE |
| 2022Q2 | 2022-08-02 | 08-03 (-1) | 08-04 (-2) | 08-02 (0, pre-mkt) | 07-27 (+6) | HLT |
| 2022Q3 | 2022-11-01 | 11-02 (-1) | 11-03 (-2) | 11-03 (-2) | 10-26 (+6) | HLT |
| 2022Q4 | 2023-02-14 | 02-23 (-9) | 02-09 (+5) | 02-14 (0, pre-mkt) | 02-09 (+5) | EXPE, HLT |
| 2023Q1 | 2023-05-09 | 05-04 (+5) | 05-04 (+5) | 05-02 (+7) | 04-26 (+13) | HLT |
| 2023Q2 | 2023-08-03 | 08-03 (0, after close) | 08-03 (0, pre-mkt) | 08-01 (+2) | 07-26 (+8) | HLT |
| 2023Q3 | 2023-11-01 | 11-02 (-1) | 11-02 (-1) | 11-02 (-1) | 10-25 (+7) | HLT |
| 2023Q4 | 2024-02-13 | 02-22 (-9) | 02-08 (+5) | 02-13 (0, pre-mkt) | 02-07 (+6) | HLT |
| 2024Q1 | 2024-05-08 | 05-02 (+6) | 05-02 (+6) | 05-01 (+7) | 04-24 (+14) | HLT |
| 2024Q2 | 2024-08-06 | 08-01 (+5) | 08-08 (-2) | 07-31 (+6) | 08-07 (-1) | MAR |
| 2024Q3 | 2024-11-07 | 10-30 (+8) | 11-07 (0, after close) | 11-04 (+3) | 10-23 (+15) | HLT |
| 2024Q4 | 2025-02-13 | 02-20 (-7) | 02-06 (+7) | 02-11 (+2) | 02-06 (+7) | EXPE, HLT |
| 2025Q1 | 2025-05-01 | 04-29 (+2) | 05-08 (-7) | 05-06 (-5) | 04-29 (+2) | BKNG, HLT |
| 2025Q2 | 2025-08-06 | 07-29 (+8) | 08-07 (-1) | 08-05 (+1) | 07-23 (+14) | HLT |
| 2025Q3 | 2025-11-06 | 10-28 (+9) | 11-06 (0, after close) | 11-04 (+2) | 10-22 (+15) | HLT |
| 2025Q4 | 2026-02-12 | 02-18 (-6) | 02-12 (0, after close) | 02-10 (+2) | 02-11 (+1) | MAR |
| 2026Q1 | 2026-05-07 | 04-28 (+9) | 05-07 (0, after close) | 05-06 (+1) | 04-28 (+9) | BKNG, HLT |
| 2026Q2 | 2026-08-06 | 08-04 (+2) | 08-05 (+1) | 08-03 (+3) | 07-28 (+9) | HLT |

Usable quarters under the point-in-time rule: BKNG 12, EXPE 11 (only 6 since 2023, 3 since 2024), MAR 18 (12 since 2023), HLT 20 (13 since 2023). BKNG and EXPE both usable in the same quarter: 5 (2021Q1, 2021Q2, 2023Q1, 2024Q1, 2026Q2), so the OTA composite is not testable.

## Peer prints data (`02_peer_prints.csv`, one row per quarter)

Per peer: report date and filing time, room nights y/y (BKNG as stated; EXPE computed from the booked-nights table, stayed-night growth for 2021Q1 to 2022Q1 where that is all Expedia disclosed, flagged in `expe_room_nights_basis`), gross bookings y/y (BKNG reported and constant currency where the release gives it; EXPE from the table), revenue y/y (release and XBRL), Adjusted EBITDA margin (BKNG from the reconciliation table through 2024 and the stated margin from 2025; EXPE from the table over revenue), MAR and HLT RevPAR y/y, each peer's day-1 stock and excess return, q/q accelerations, and the next-quarter direction where the release quantifies a guide. Extraction was complete for all 22 quarters and all four peers; the console check `MISSING ... none` confirms it. Known limits:

- BKNG constant-currency gross bookings blank where the release did not state it: 2021Q4, 2022Q1, 2022Q2, 2023Q2, 2023Q4, 2024Q1, 2024Q3.
- EXPE 2025Q4 room nights (9%) read from the highlights bullet rather than the table (the table row did not parse), so it is a rounded figure.
- Next-quarter direction exists only from mid-2025, when both companies started quantifying the next quarter in the release: BKNG from Q2 2025 (room-nights growth guide, 5 quarters, all "decelerate" versus the quarter just printed; in the 4 cases with a known outcome BKNG landed above the top of the range 3 times and at the midpoint once, Q1 2026); EXPE from Q2 2025 (gross-bookings guide, 5 quarters: stable, decelerate, stable, decelerate, decelerate). Before that both gave guidance on the call only, so the column is blank by construction, not missing.

## Results

Cells from `02_peer_readthrough_results.csv` (255 cells: 17 signals x 5 targets x 3 samples; every cell carries n and the quarters used). Sign concordance is trivially near 1 for two always-positive y/y series, so read change-concordance (share of consecutive quarters in which peer and ABNB moved the same way) for the level pairs. BH q is the Benjamini-Hochberg value within the sample block.

### Target: ABNB nights y/y

| Signal | Sample | n | Pearson r (p) | Spearman rho (p) | Perm p | BH q | Change concord (n) |
|---|---|---|---|---|---|---|---|
| BKNG room nights y/y | 2021Q1+ | 12 | 0.996 (<0.001) | 0.38 (0.22) | 0.002 | 0.000 | 0.50 (6) |
| BKNG room nights y/y | 2023Q1+ | 9 | 0.948 (<0.001) | 0.12 (0.76) | 0.099 | 0.002 | 0.25 (4) |
| BKNG room nights y/y | 2024Q1+ | 8 | -0.456 (0.26) | -0.27 (0.52) | 0.25 | 0.82 | 0.25 |
| BKNG gross bookings y/y | 2023Q1+ | 9 | 0.924 (<0.001) | 0.44 (0.23) | 0.056 | 0.006 | 0.40 (5) |
| BKNG gross bookings y/y cc | 2023Q1+ | 7 | 0.960 (<0.001) | 0.16 (0.73) | 0.110 | 0.008 | 1.00 (2) |
| BKNG day-1 excess return | 2023Q1+ | 9 | -0.280 (0.47) | -0.12 (0.77) | 0.47 | 0.76 | 0.60 (5) |
| EXPE room nights y/y | 2021Q1+ | 11 | 0.954 (<0.001) | 0.84 (0.001) | 0.001 | 0.000 | 0.60 (5) |
| EXPE room nights y/y | 2023Q1+ | 6 | 0.984 (<0.001) | 0.94 (0.005) | 0.009 | 0.006 | 1.00 (2) |
| EXPE gross bookings y/y | 2023Q1+ | 6 | 0.846 (0.03) | 0.83 (0.04) | 0.023 | 0.25 | 1.00 (2) |
| MAR RevPAR y/y | 2021Q1+ | 18 | 0.911 (<0.001) | 0.79 (<0.001) | 0.001 | 0.000 | 0.62 (13) |
| MAR RevPAR y/y | 2023Q1+ | 12 | 0.911 (<0.001) | 0.74 (0.006) | 0.004 | 0.000 | 0.56 (9) |
| MAR RevPAR y/y | 2024Q1+ | 9 | 0.498 (0.17) | 0.44 (0.23) | 0.17 | 0.68 | 0.43 |
| HLT RevPAR y/y | 2021Q1+ | 20 | 0.930 (<0.001) | 0.83 (<0.001) | 0.001 | 0.000 | 0.71 (17) |
| HLT RevPAR y/y | 2023Q1+ | 13 | 0.884 (<0.001) | 0.78 (0.002) | 0.001 | 0.002 | 0.73 (11) |
| HLT RevPAR y/y | 2024Q1+ | 9 | 0.545 (0.13) | 0.52 (0.15) | 0.12 | 0.68 | 0.71 |

### Target: ABNB nights acceleration (pp q/q)

| Signal | Sample | n | Pearson r (p) | Spearman rho (p) | Perm p | BH q |
|---|---|---|---|---|---|---|
| BKNG room nights accel | 2021Q1+ | 12 | 0.990 (<0.001) | 0.79 (0.002) | 0.001 | 0.000 |
| BKNG room nights accel | 2023Q1+ | 9 | 0.626 (0.07) | 0.50 (0.17) | 0.083 | 0.38 |
| BKNG room nights accel | 2024Q1+ | 8 | 0.637 (0.09) | 0.52 (0.19) | 0.092 | 0.68 |
| EXPE room nights accel | 2023Q1+ | 6 | 0.822 (0.04) | 0.64 (0.17) | 0.064 | 0.31 |
| EXPE room nights accel | 2021Q1+ | 11 | 0.971 (<0.001) | 0.77 (0.005) | 0.003 | 0.000 |
| MAR RevPAR accel | 2023Q1+ | 12 | 0.773 (0.003) | 0.35 (0.27) | 0.018 | 0.034 |
| MAR RevPAR accel | 2024Q1+ | 9 | 0.515 (0.16) | 0.32 (0.41) | 0.16 | 0.68 |
| HLT RevPAR accel | 2023Q1+ | 13 | 0.606 (0.03) | 0.24 (0.43) | 0.047 | 0.24 |
| HLT RevPAR accel | 2024Q1+ | 9 | 0.502 (0.17) | 0.45 (0.22) | 0.18 | 0.68 |

### Target: ABNB revenue beat vs guide midpoint (%), 2023Q1 to 2026Q2

| Signal | n | Pearson r (p) | Spearman rho (p) | Perm p | BH q |
|---|---|---|---|---|---|
| BKNG room nights y/y | 9 | 0.03 (0.94) | 0.15 (0.69) | 0.94 | 0.99 |
| BKNG gross bookings y/y | 9 | 0.06 (0.87) | 0.35 (0.36) | 0.90 | 0.99 |
| BKNG day-1 excess return | 9 | -0.20 (0.61) | -0.23 (0.56) | 0.62 | 0.81 |
| EXPE room nights y/y | 6 | -0.31 (0.55) | -0.14 (0.79) | 0.52 | 0.76 |
| EXPE gross bookings y/y | 6 | -0.78 (0.07) | -0.83 (0.04) | 0.066 | 0.38 |
| MAR RevPAR y/y | 12 | 0.01 (0.97) | 0.39 (0.21) | 0.97 | 0.99 |
| HLT RevPAR y/y | 13 | 0.00 (1.00) | 0.22 (0.46) | 1.00 | 1.00 |

Full sample (2021Q1+): EXPE room nights y/y r = 0.74 (n = 9, p = 0.02, q = 0.05) and MAR RevPAR y/y r = 0.54 (n = 15, p = 0.04, q = 0.08) look interesting but both vanish once 2021 to 2022 are dropped, and the Spearman values (0.37, 0.43) were never significant.

### Target: ABNB day-1 excess return vs QQQ, 2023Q1 to 2026Q2

| Signal | n | Pearson r (p) | Spearman rho (p) | Perm p | BH q | Sign concord (n) |
|---|---|---|---|---|---|---|
| BKNG day-1 excess return | 9 | 0.60 (0.09) | 0.53 (0.14) | 0.064 | 0.41 | 0.44 (9) |
| BKNG room nights y/y | 9 | -0.42 (0.26) | -0.48 (0.19) | 0.13 | 0.70 | |
| BKNG gross bookings y/y | 9 | -0.28 (0.46) | 0.05 (0.90) | 0.32 | 0.76 | |
| EXPE day-1 excess return | 6 | 0.46 (0.35) | 0.26 (0.62) | 0.33 | 0.70 | 0.60 (5) |
| EXPE room nights y/y | 6 | -0.53 (0.28) | -0.49 (0.33) | 0.29 | 0.70 | |
| MAR day-1 excess return | 12 | -0.25 (0.44) | -0.06 (0.86) | 0.47 | 0.76 | 0.64 (11) |
| MAR RevPAR y/y | 12 | -0.33 (0.30) | -0.22 (0.50) | 0.31 | 0.70 | |
| HLT day-1 excess return | 13 | 0.29 (0.33) | 0.44 (0.13) | 0.33 | 0.70 | 0.67 (12) |
| HLT RevPAR y/y | 13 | -0.32 (0.28) | -0.10 (0.73) | 0.27 | 0.70 | |

Full sample: BKNG excess vs ABNB excess r = 0.38 (n = 12, p = 0.23); EXPE excess r = 0.36 (n = 11, p = 0.28); every other reaction cell |r| < 0.2.

### Leave-one-out forecast of ABNB nights y/y (MAE in percentage points; all models scored on the same quarters)

| Signal | Sample | n | Peer OLS | Naive (prior q) | Seasonal naive | AR(1) | AR(1)+peer | LOO mean | Peer / naive |
|---|---|---|---|---|---|---|---|---|---|
| BKNG room nights y/y | 2021Q1+ | 12 | 8.4 | 34.7 | 35.6 | 38.1 | 21.2 | 31.1 | 0.24 |
| BKNG gross bookings y/y | 2021Q1+ | 12 | 4.7 | 34.7 | 35.6 | 38.1 | 6.2 | 31.1 | 0.13 |
| EXPE room nights y/y | 2021Q1+ | 11 | 20.1 | 26.2 | 51.1 | 35.8 | 21.0 | 39.8 | 0.77 |
| MAR RevPAR y/y | 2021Q1+ | 18 | 16.0 | 27.5 | 42.1 | 26.4 | 14.5 | 24.3 | 0.58 |
| HLT RevPAR y/y | 2021Q1+ | 20 | 13.2 | 23.6 | 36.0 | 23.9 | 7.7 | 21.9 | 0.56 |
| BKNG room nights y/y | 2023Q1+ | 9 | 3.01 | 1.47 | 7.08 | 2.12 | 3.06 | 2.30 | 2.05 |
| BKNG gross bookings y/y | 2023Q1+ | 9 | 2.18 | 1.47 | 7.08 | 2.12 | 1.95 | 2.30 | 1.48 |
| BKNG day-1 excess return | 2023Q1+ | 9 | 2.86 | 1.47 | 7.08 | 2.12 | 2.41 | 2.30 | 1.95 |
| EXPE room nights y/y | 2023Q1+ | 6 | 0.78 | 3.04 | 12.37 | 3.30 | 0.95 | 2.54 | 0.26 |
| MAR RevPAR y/y | 2023Q1+ | 12 | 1.19 | 1.90 | 7.24 | 1.98 | 1.38 | 2.17 | 0.63 |
| HLT RevPAR y/y | 2023Q1+ | 13 | 1.20 | 2.23 | 7.52 | 2.24 | 1.61 | 2.35 | 0.54 |
| BKNG room nights y/y | 2024Q1+ | 8 | 0.88 | 1.46 | 2.97 | 0.92 | 1.20 | 0.75 | 0.60 |
| BKNG gross bookings y/y | 2024Q1+ | 8 | 0.83 | 1.46 | 2.97 | 0.92 | 0.96 | 0.75 | 0.57 |
| MAR RevPAR y/y | 2024Q1+ | 9 | 1.33 | 1.35 | 2.78 | 1.23 | 1.68 | 1.11 | 0.99 |
| HLT RevPAR y/y | 2024Q1+ | 9 | 1.22 | 1.75 | 2.70 | 1.41 | 1.40 | 1.19 | 0.70 |

Reading: in the recovery regime anything correlated with "travel is reopening" crushes the naive forecast, which is why the full-sample numbers are not evidence of read-through. In 2023Q1 on, among signals with at least 9 usable quarters, MAR and HLT RevPAR y/y are the only ones that beat both the naive and the AR(1) (MAE 1.2 pp vs 1.9 to 2.2 pp); EXPE room nights (0.78) and EXPE gross bookings (2.34) also beat both baselines but rest on 6 quarters, 3 of them in 2023. From 2024Q1 a leave-one-out mean of ABNB's own growth (0.75 to 1.19 pp) is the best forecast on every row, so the honest prior for Q3 2026 nights growth is "about the recent average, 8 to 10 percent", and no peer number has moved that.

## What is and is not usable before the 5 November 2026 print

Actual 2025 pattern for the Q3 prints: HLT 22 Oct (Wed, pre-market), BKNG 28 Oct (Tue, after close), MAR 4 Nov (Tue, pre-market), ABNB 6 Nov (Thu, after close), EXPE 6 Nov (Thu, after close, same evening as ABNB). Q3 2024: HLT 23 Oct, BKNG 30 Oct, MAR 4 Nov, ABNB 7 Nov, EXPE 7 Nov (same evening). Q3 2023: HLT 25 Oct, ABNB 1 Nov, then BKNG, EXPE and MAR all on 2 Nov, after Airbnb.

- **Usable, with the caveats above:** HLT system-wide RevPAR y/y (expect about 21 to 22 Oct) and MAR worldwide RevPAR y/y (expect about 3 Nov): the direction of their q/q change has matched the direction of ABNB's nights acceleration in 56 to 73 percent of quarters since 2023, and their level has tracked ABNB nights y/y (Spearman 0.74 to 0.78). They are a sanity check on the 8 to 10 percent prior, not a forecast that beats it.
- **Usable as context only:** BKNG room nights and gross bookings (expect about 27 to 28 Oct): no correlation with ABNB's growth, beat or reaction since 2023 (Spearman 0.12, 0.15, -0.48 respectively, n = 9). BKNG's own day-1 excess return has the highest correlation with ABNB's day-1 excess return of anything tested (r = 0.60, n = 9) but with p = 0.09, q = 0.41 and 44 percent sign agreement it is not tradeable. New since Jul 2025: BKNG publishes a Q4 room-nights growth guide in the release; it has guided a deceleration every quarter and then printed at or above the top of the range in 3 of 4 known cases, so read it as a conservative floor for BKNG, not as a read on Airbnb.
- **Not usable:** EXPE. Since 2024 it has printed the same evening as Airbnb or later in 7 of 10 quarters (before Airbnb only in 2024Q1, 2024Q4 and 2026Q2) and is expected around 5 to 6 Nov 2026. The 6-quarter EXPE cells above (r = 0.98 with ABNB nights) should not be quoted as a signal; they mostly describe 2023Q1 and are unavailable in real time anyway.
- **Not usable for the reaction:** nothing. No peer KPI or peer stock move predicts ABNB's day-1 excess return at conventional significance in any sample.

## Caveats

- n is 6 to 13 in the post-2022 samples and 9 to 20 in the full sample; the point-in-time rule removes 10 of 22 BKNG quarters and 11 of 22 EXPE quarters. Confidence intervals on r at n = 9 span roughly plus or minus 0.6.
- Multiple comparisons: 255 cells. At the 5 percent level about 13 would be significant by chance. Only the level correlations with the hotel RevPAR series and the recovery-regime cells survive Benjamini-Hochberg; none of the beat or reaction cells do (minimum q = 0.38).
- Growth-rate regimes: 2021 to 2022 y/y figures are lapping COVID troughs (ABNB nights +197% in 2021Q2, BKNG room nights +458%), so all series co-move mechanically. Both samples are reported; conclusions are drawn from 2023Q1 on, with 2024Q1 on as a robustness check because 2023Q1 (BKNG +38%, MAR +34%, ABNB +19%) is a leverage point in the 2023+ sample.
- Level series that are always positive give sign concordance near 1 by construction; the change-concordance column is the informative one, and it sits at 25 to 73 percent, i.e. not far from a coin flip for the OTAs.
- Measurement differences: Airbnb reports nights *booked*; Booking reports room nights booked; Expedia reported *stayed* room-night growth until Q1 2022 and booked nights after; Marriott and Hilton RevPAR is a *stayed*, constant-currency hotel metric. Peer gross bookings are reported in USD with FX effects unless a cc figure is given.
- Report-date rule: 8-K filing date and time are used for the release moment. Airbnb's release date is inferred as the trading day before its reaction date. Same-day pairs are only counted when the peer filed pre-market.
- Guidance direction covers 5 quarters per company and is descriptive only.
- Reactions are 1-day close-to-close excess over QQQ; no intraday or pre-announcement drift is measured.
