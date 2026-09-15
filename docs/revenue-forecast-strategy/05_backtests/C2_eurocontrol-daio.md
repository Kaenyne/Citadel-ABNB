# C2: EUROCONTROL daio daily flights as an EMEA nights feature

Agent/session: Claude Code (Fable 5.1) subagent, orchestrated run (build C of the GitHub alt-data integration plan). Date: 14 September 2026. Branch: `krish/github-altdata-catalog` (worktree `C:/Users/krish/citadel-abnb-ghcat`). Packages touched, all new: `analysis/src/govdata_v2/` (copy of the govdata V protocol), `data/processed/govdata_v2/`, raw cache `data/raw/eurocontrol_daio/` (gitignored), git mirror `C:/Users/krish/abnb_ia_capture/euctrl_daio_git/` (outside the repo), this note, one WORKBOARD row. Nothing under `analysis/src/govdata/`, `data/processed/govdata/`, the harness or any tracked data file was modified. Time spent: about 1.5 hours.

## Verdict

SHORT-WINDOW SURVIVOR, not a survivor, against the pre-registered line, and a duplicate of the held Eurostat air-passenger series on history. `eu40_flt_da_full` beats naive on the 2023Q1+ window (walk-forward RMSE ratio 0.816, wf_n 10, slope positive, permutation p 0.002, jackknife max 0.92 with 10 of 10 drops below 1) and fails on the 2022Q1+ window (1.118, wf_n 12, jackknife min 1.01, 0 of 12 below 1); `eu_core_flt_da_full` does the same (0.825 / 1.189). The n came out exactly as pre-registered (12 and 10 on EMEA nights, 14 and 10 on total nights). T0: r = 0.994 (eu40) and 0.986 (eu_core) against `avia_eu27_full` on 1Q23 to 4Q25 (n 12), above the 0.97 line, so the feature is labelled "duplicate of avia_paoc on history, new for the live quarter": on the scored history it is the same information as the Eurostat passenger series that the govdata run scored at 0.93 / 0.75, and what it adds is a reading for 3Q26 that no held series gives. The stated prior (corroboration) was too pessimistic on the short window and right on the long one. Live reading, current vintage as of the 14 Sep 2026 commit: 3Q26 qtd75 (1 Jul to 13 Sep) eu40 +3.04 % y/y, eu_core +2.65 %, against 2Q26 full +1.22 % / +1.53 % and 1Q26 +3.19 % / +2.96 %; monthly inside the quarter July +3.4 %, August +2.7 %, 1 to 13 September +3.0 % (eu40). Flights re-accelerated by about 2 pp from 2Q26 while the panel's EMEA nights mid went 5 (1Q26) to 8 (2Q26). The in-sample OLS on 1Q23 to 2Q26 maps the +3.0 % to an EMEA nights y/y of 6.5 (naive 8.0); read as corroboration of a mid-to-high-single-digit EMEA print, not as a level input. Git-history revisions are nil beyond the last day in a file (median absolute revision 0 flights over the last 7 days; last day median 2 flights, 0.004 %), so the live number is quoted as it stands. No EMEA target exists in the harness, so nothing is registered; a harness change request is below.

## Pre-registration (written 14 Sep 2026 before the pull)

### Source and grain

`https://github.com/euctrl-pru/daio`, yearly CSVs `daio_2019.csv` to `daio_2026.csv`, grain country x UTC day, 40 EUROCONTROL states, columns `flt_d`, `flt_a`, `flt_da` (departures plus arrivals), `flt_i`, `flt_o` (overflights), `flt_daio`. The sample already held (`data/processed/github_altdata/samples/eurocontrol-daio-daily-flights/`, 2025-01-01 to 2026-09-13) was inspected before this note; nothing else had been pulled. The measure is `flt_da` only: flights to or from the state. Overflights (`flt_o`, which carries revision negatives, 253 rows below zero in the sample) and internal flights are excluded. Flights, not passengers: load-factor drift is an acknowledged wedge and is not corrected.

### Aggregates

- `eu40`: sum of `flt_da` over all 40 states.
- `eu_core`: EU27 plus the United Kingdom, Switzerland and Norway. In the file's naming that is 29 rows (Belgium and Luxembourg are one row): Austria, Belgium and Luxembourg, Bulgaria, Croatia, Cyprus, Czech Republic, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Ireland, Italy, Latvia, Lithuania, Malta, Netherlands, Poland, Portugal, Romania, Slovakia, Slovenia, Spain, Sweden, United Kingdom, Switzerland, Norway. Excluded (11): Israel, Morocco, Ukraine, Moldova, Georgia, Armenia, Turkiye, Albania, Serbia and Montenegro, Bosnia-Herzegovina, North Macedonia (airspace driven by war or geopolitics rather than leisure demand).

### Features (quarterly, keyed `3Q26` style to join the regional panel)

- `eu40_flt_da_full`, `eu_core_flt_da_full`: calendar-quarter sum of daily `flt_da`, guarded to complete quarters (every day of the quarter present), y/y % against the same quarter one year earlier.
- `eu40_flt_da_lag1`, `eu_core_flt_da_lag1`: the prior quarter's `_full` value (always knowable).
- `eu40_flt_da_qtd75`, `eu_core_flt_da_qtd75`: days 1 to 75 of the quarter (for Q3: 1 Jul to 13 Sep) against the same 75 calendar days a year earlier, y/y %. Two versions are built: `_qtd75` from today's file (current vintage, one number per quarter) and `_qtd75pit` read from the git commit nearest the 75th day of each quarter since 1Q23 (true point-in-time; the vintage that would have been observable on the 75th day). The PIT version is the one that counts for the live-quarter variant; the current-vintage version is reported for comparison and as the fallback where git history does not reach.
- No seasonal adjustment (y/y on identical calendar windows). Easter shift touches Q1 and Q2 only; Q3 is clean. Day-of-week is not aligned in the primary (same calendar days); a 364-day-shifted comparison is reported for the 3Q26 live reading only, as a sensitivity.
- Vs-2019 sensitivity: for 2022 quarters a second column `_vs2019` (2022 quarter sum against the same quarter of 2019) is written, used only in the sensitivity described below.

### Targets

Primary `emea_nights_yoy_mid` from `data/processed/overnight/10_regional_panel_quarterly.csv` (starts 3Q22: 3Q22 and 4Q22 are numeric letter points 20 and 25; 1Q23 numeric 21; 2Q23 to 3Q24 derived residual intervals with the mid used, plus or minus 2 pp; 4Q24 to 2Q26 management buckets, mid used). Secondary `total_nights_yoy` = `nights_m_yoy_pct` from `data/processed/abnb_driver_history_quarterly.csv` (starts 1Q22).

### Protocol and windows (copy of `analysis/src/govdata/V2_backtests.py`, which calls `analysis/src/adrq3/I0_protocol.py`)

Expanding OLS refit strictly before each scored quarter, `walkforward(min_fit=4)`, RMSE ratio vs naive last quarter, vs prior year, vs AR(1); 1,000-shuffle permutation p on Pearson r (seed 20260911 as in I0); jackknife of the naive ratio dropping each scored quarter in turn; knowable flag "yes (daily, about 1-day lag)". Windows exactly as the govdata run so the result lands on the same scoreboard: W1 = "2022Q1+" (feature and target rows 1Q22 to 2Q26, walk-forward scored from 1Q23) and W2 = "2023Q1+" (rows 1Q23 to 2Q26, scored from 1Q24).

Scored-quarter counts, written down before the run. On `emea_nights_yoy_mid` the target starts 3Q22, so with `min_fit=4` the first quarter with four finite fit points is 3Q23: W1 wf_n = 12 (3Q23 to 2Q26), W2 wf_n = 10 (1Q24 to 2Q26). Permutation n: W1 16 (3Q22 to 2Q26), W2 14. On `total_nights_yoy` (target from 1Q22): W1 wf_n = 14, W2 wf_n = 10. Any other n in the results tables means a feature row was missing and is explained there.

The 2022 rows. The 2022 flight y/y (against 2021) is a reopening base effect of roughly +50 to +100 %, and the two 2022 target rows (20, 25) are letter points, so the walk-forward fits on W1 start at 1Q23 in the sense of the protocol (the first refit that is scored happens at 1Q23; the first scored quarter with four fit points is 3Q23) and the 3Q22 and 4Q22 rows sit inside the first fits. That is the primary, and it is what gives wf_n = 12 on W1. Two sensitivities are reported alongside, never as the primary: (A) the 2022 feature rows replaced by the vs-2019 growth; (B) the 2022 feature rows dropped, which makes the first scoreable quarter on W1 equal to W2's (1Q24) so it cannot serve as a second window and is shown only to make the base-effect dependence visible.

### T0, duplicate check against the held Eurostat avia_paoc (before the backtest)

Pearson r of `eu_core_flt_da_full` y/y against the held `avia_eu27_full` y/y (from `data/processed/govdata/V/V_feature_panel.csv`, EU27 air passengers carried, ends 2025-12) on the overlapping quarters 1Q23 to 4Q25 (n = 12; also reported on every overlapping quarter from 1Q20 as a second line). Pre-registered rule: if r > 0.97 on the 1Q23 to 4Q25 overlap the feature is labelled "duplicate of avia_paoc on history, new for the live quarter" and any survivor verdict is qualified that way; the red team's looser 0.90 line is reported as well. Note for the reader, written before the number: `avia_eu27_full` was itself scored in the govdata run at 0.93 (W1, wf_n 10) and 0.75 (W2, wf_n 8) on `emea_nights_yoy_mid`, verdict "no coverage" because it ends 2025-12.

### Pass lines (govdata vocabulary)

- SURVIVOR: `wf_ratio_vs_naive` < 1.0 on BOTH windows against `emea_nights_yoy_mid`, with wf_n >= 6 on each and a positive full-window OLS slope on both.
- SHORT-WINDOW SURVIVOR: < 1.0 on "2023Q1+" only.
- Otherwise CORROBORATION (the series carries a 3Q26 EMEA reading no held series gives).
- Reported, not part of the line: permutation p, jackknife max ratio and count below 1, ratio vs AR(1) and vs prior year, sign accuracy. The verdict is by the `_full` feature; `_lag1` and `_qtd75` results are reported on their own rows and cannot upgrade the verdict, because `_lag1` is a different information set and `_qtd75` history is short or partly current-vintage.
- Stated prior before running: corroboration, not survivor. Flight counts move 1 to 4 pp y/y while EMEA nights move 5 to 25 pp; the target rows 2Q23 to 3Q24 are derived residual intervals.

### Revision check (git history)

For the yearly file in the git mirror, take every pair of commits about seven days apart (nearest commit to each commit date plus 7 days, at least 5 and at most 10 days later), compare the last 7 entry_dates present in the earlier commit with the same dates in the later commit, `eu40` daily `flt_da`. Report the median absolute revision in flights and in percent, and the same for `eu_core`. Pre-stated reading rule: median absolute revision below 0.5 % means the live qtd75 can be quoted as it stands; between 0.5 % and 2 % it is quoted with that band; above 2 % the live reading is also recomputed dropping the last 7 days (qtd68) and the two are shown together.

### Live reading

3Q26 qtd75 (1 Jul to 13 Sep 2026 vs 1 Jul to 13 Sep 2025) for `eu40` and `eu_core`, the last complete quarters 1Q26 and 2Q26 `_full`, next to the regional panel's 2Q26 EMEA nights y/y mid (8, bucket "high-single digit") and 1Q26 (5). The red team's own check from the sample, written before this run so it can be compared: eu40 qtd75 +3.04 %, 2Q26 +1.2 %, 1Q26 +3.2 %.

### Harness

Checked before the run: `data/processed/forecast_methods/harness/targets.csv` columns are quarter, print_date, revenue_musd, gbv_musd, nights_m, adr_usd, take_rate_pct, fx_pts_revenue, fx_pts_adr, revenue_yoy, gbv_yoy, nights_yoy, adr_yoy, revenue_yoy_panel, gbv_yoy_panel, guide fields, street fields, cons_at_print fields, has_actual. There is no EMEA or regional nights target. Therefore, whatever the verdict, nothing is registered under `eu-flights-v1` and a harness change request is written in this note. `score.py` is not run because no registry file is added.

### Other deliverables

Country weights table: share of `flt_da` by state, calendar 2025, for WP-X. WP-O line: the repo has no LICENSE (GitHub license = null) and the upstream README carries no terms; raw stays gitignored, only the derived quarterly table, the manifest and the weights table are committed; a memo number needs the WP-O log line.

## What ran

All from the worktree root `C:/Users/krish/citadel-abnb-ghcat`, Python `python` (the repo venv, pandas 3).

1. Pull, 8 files, 6.29 MB, 112,520 rows (40 states x 2,813 days, 2019-01-01 to 2026-09-13), no `flt_da` below zero (674 `flt_o` rows are), `curl -sL --retry 3` per year into `data/raw/eurocontrol_daio/` (gitignored), skip when present. Exit 0, about 8 s. Manifest with sha256 and pull time: `data/processed/govdata_v2/raw_manifest.csv`.
2. `git clone https://github.com/euctrl-pru/daio C:/Users/krish/abnb_ia_capture/euctrl_daio_git`: 1,071 commits, 2022-06-08 to 2026-09-14, `.git` 130 MB. Exit 0, about 40 s.
3. `python analysis/src/govdata_v2/run.py`: C1 (manifest, daily aggregates, country weights) exit 0 in 1 s; C2 (git revision check, PIT qtd75) exit 0 in 28 s; C3 (feature panel, T0, backtests, readings) exit 0 in 1 s; C4 (verdict, live reading) exit 0 in 1 s; total 31 s, exit 0. The first end-to-end run failed in C4 on a pandas boolean-indexing precedence bug of mine (exit 1); fixed and re-run, exit 0. No frozen folder shows in `git status`.

## Results

### Feature panel (y/y %, current vintage except the `_qtd75pit` columns; source: `C_feature_panel.csv`)

| quarter | eu40 full | eu40 qtd75 | eu40 qtd75 PIT | eu_core full | eu_core qtd75 | eu_core qtd75 PIT | total nights y/y | EMEA nights mid |
|---|---|---|---|---|---|---|---|---|
| 3Q22 | 38.22 | 39.25 | 39.25 | 41.44 | 42.71 | 42.71 | 25.09 | 20.0 |
| 4Q22 | 20.91 | 22.13 | 22.13 | 21.42 | 23.11 | 23.11 | 20.16 | 25.0 |
| 1Q23 | 26.37 | 28.79 | 28.79 | 25.33 | 27.90 | 27.90 | 18.61 | 21.0 |
| 2Q23 | 8.49 | 8.51 | 8.51 | 7.24 | 7.15 | 7.15 | 10.99 | 11.94 |
| 3Q23 | 8.11 | 7.78 | 7.78 | 7.56 | 7.17 | 7.17 | 13.54 | 10.54 |
| 4Q23 | 8.89 | 8.75 | 8.75 | 9.32 | 9.12 | 9.12 | 12.02 | 12.29 |
| 1Q24 | 7.65 | 6.38 | 6.38 | 8.05 | 6.77 | 6.77 | 9.50 | 10.0 |
| 2Q24 | 7.25 | 7.59 | 7.59 | 7.42 | 7.81 | 7.81 | 8.69 | 5.76 |
| 3Q24 | 5.01 | 5.04 | 5.04 | 5.42 | 5.51 | 5.51 | 8.48 | 6.58 |
| 4Q24 | 5.11 | 5.17 | 5.17 | 4.54 | 4.62 | 4.62 | 12.35 | 11.0 |
| 1Q25 | 4.96 | 6.65 | 6.65 | 4.32 | 5.99 | 5.99 | 7.92 | 5.0 |
| 2Q25 | 4.48 | 4.98 | 4.98 | 4.01 | 4.26 | 4.26 | 7.43 | 5.0 |
| 3Q25 | 3.91 | 3.95 | 3.95 | 3.28 | 3.38 | 3.38 | 8.80 | 5.0 |
| 4Q25 | 5.72 | 5.53 | 5.53 | 4.67 | 4.43 | 4.43 | 9.82 | 8.0 |
| 1Q26 | 3.19 | 2.93 | 2.93 | 2.96 | 2.56 | 2.56 | 9.15 | 5.0 |
| 2Q26 | 1.22 | 0.84 | 0.84 | 1.53 | 1.34 | 1.34 | 10.34 | 8.0 |
| 3Q26 | (incomplete) | 3.04 | 3.04 | (incomplete) | 2.65 | 2.65 | (5 Nov) | (5 Nov) |

1Q22 and 2Q22 `_full` are +165 % and +161 % (eu40), the reopening base; they enter only the `total_nights_yoy` W1 fits. The PIT qtd75 values equal the current-vintage ones to two decimals in every quarter, which is the revision result below seen from the other side.

### T0 duplicate check (source: `C_t0_duplicate_check.csv`)

| feature | held series | overlap | n | r | > 0.97 (pre-registered) | > 0.90 (red team) |
|---|---|---|---|---|---|---|
| eu_core_flt_da_full | avia_eu27_full | 1Q23 to 4Q25 | 12 | 0.986 | yes | yes |
| eu_core_flt_da_full | avia_eu27_full | 1Q20 to 4Q25 | 24 | 0.946 | no | yes |
| eu40_flt_da_full | avia_eu27_full | 1Q23 to 4Q25 | 12 | 0.994 | yes | yes |
| eu40_flt_da_full | avia_eu27_full | 1Q20 to 4Q25 | 24 | 0.962 | no | yes |
| eu_core_flt_da_full | avia_es_full | 1Q23 to 4Q25 | 12 | 0.993 | yes | yes |
| eu_core_flt_da_full | avia_it_full | 1Q23 to 4Q25 | 12 | 0.989 | yes | yes |

Label applied: duplicate of avia_paoc on history, new for the live quarter. The 1Q20 to 4Q25 line falls below 0.97 only because the 2020 to 2022 pandemic quarters separate flights from passengers (load factors collapsed and recovered); on the scored history they are the same series.

### Backtests, primary target `emea_nights_yoy_mid` (source: `C_backtests.csv`; every row wf_n as pre-registered)

| feature | window | n | wf_n | first scored | r | perm p | OLS slope (window) | WF slope range | ratio vs naive | vs prior yr | vs AR(1) | sign acc | jackknife min / max | jk n < 1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| eu40_flt_da_full | 2022Q1+ | 16 | 12 | 3Q23 | 0.842 | 0.001 | 0.529 | 0.24 to 0.54 | **1.118** | 0.542 | 1.086 | 0.583 | 1.012 / 1.260 | 0 / 12 |
| eu40_flt_da_full | 2023Q1+ | 14 | 10 | 1Q24 | 0.876 | 0.002 | 0.650 | 0.53 to 0.70 | **0.816** | 0.564 | 0.867 | 0.600 | 0.732 / 0.920 | 10 / 10 |
| eu_core_flt_da_full | 2022Q1+ | 16 | 12 | 3Q23 | 0.825 | 0.001 | 0.486 | 0.21 to 0.49 | **1.189** | 0.577 | 1.154 | 0.583 | 1.075 / 1.351 | 0 / 12 |
| eu_core_flt_da_full | 2023Q1+ | 14 | 10 | 1Q24 | 0.873 | 0.003 | 0.668 | 0.54 to 0.71 | **0.825** | 0.570 | 0.877 | 0.600 | 0.725 / 0.946 | 10 / 10 |
| eu40_flt_da_lag1 | 2022Q1+ | 16 | 12 | 3Q23 | 0.581 | 0.039 | 0.093 | | 1.807 | 0.876 | 1.755 | 0.417 | 1.635 / 2.056 | 0 / 12 |
| eu40_flt_da_lag1 | 2023Q1+ | 14 | 10 | 1Q24 | 0.687 | 0.019 | 0.452 | | 0.956 | 0.661 | 1.017 | 0.600 | 0.863 / 1.083 | 8 / 10 |
| eu_core_flt_da_lag1 | 2022Q1+ | 16 | 12 | 3Q23 | 0.580 | 0.032 | 0.085 | | 1.807 | 0.876 | 1.755 | 0.417 | 1.638 / 2.055 | 0 / 12 |
| eu_core_flt_da_lag1 | 2023Q1+ | 14 | 10 | 1Q24 | 0.711 | 0.013 | 0.466 | | 0.927 | 0.641 | 0.986 | 0.600 | 0.819 / 1.059 | 9 / 10 |
| eu40_flt_da_qtd75pit | 2022Q1+ | 16 | 12 | 3Q23 | 0.840 | 0.002 | 0.500 | 0.25 to 0.51 | 1.133 | 0.550 | 1.100 | 0.583 | 1.045 / 1.240 | 0 / 12 |
| eu40_flt_da_qtd75pit | 2023Q1+ | 14 | 10 | 1Q24 | 0.845 | 0.004 | 0.569 | 0.46 to 0.61 | 0.897 | 0.620 | 0.953 | 0.600 | 0.807 / 0.962 | 10 / 10 |
| eu_core_flt_da_qtd75pit | 2022Q1+ | 16 | 12 | 3Q23 | 0.830 | 0.002 | 0.462 | 0.21 to 0.47 | 1.178 | 0.572 | 1.145 | 0.583 | 1.083 / 1.305 | 0 / 12 |
| eu_core_flt_da_qtd75pit | 2023Q1+ | 14 | 10 | 1Q24 | 0.846 | 0.004 | 0.585 | 0.47 to 0.61 | 0.895 | 0.619 | 0.952 | 0.700 | 0.785 / 0.975 | 10 / 10 |
| eu40_flt_da_qtd75 (current vintage) | 2022Q1+ / 2023Q1+ | 16 / 14 | 12 / 10 | | 0.840 / 0.845 | 0.003 / 0.002 | | | 1.133 / 0.897 | | | | | identical to PIT |
| eu_core_flt_da_qtd75 (current vintage) | 2022Q1+ / 2023Q1+ | 16 / 14 | 12 / 10 | | 0.830 / 0.846 | 0.001 / 0.005 | | | 1.178 / 0.895 | | | | | identical to PIT |

Walk-forward RMSEs behind the primary rows (pp): W1 model 3.41 (eu40) / 3.62 (eu_core) vs naive 3.05, prior year 6.28, AR(1) 3.14; W2 model 2.66 / 2.69 vs naive 3.26, prior year 4.72, AR(1) 3.07.

### Sensitivities on the 2022 rows, `emea_nights_yoy_mid` (pre-registered as sensitivities, not the primary)

| variant | window | n | wf_n | r | ratio vs naive | jackknife max | jk n < 1 |
|---|---|---|---|---|---|---|---|
| (A) eu40 2022 rows = growth vs 2019 | 2022Q1+ | 16 | 12 | -0.190 | 2.225 | 2.522 | 0 / 12 |
| (A) eu_core 2022 rows = growth vs 2019 | 2022Q1+ | 16 | 12 | -0.204 | 2.217 | 2.508 | 0 / 12 |
| (B) eu40 2022 rows dropped | 2022Q1+ | 14 | 10 | 0.876 | 0.816 | 0.920 | 10 / 10 |
| (B) eu_core 2022 rows dropped | 2022Q1+ | 14 | 10 | 0.873 | 0.825 | 0.946 | 10 / 10 |
| pure vs-2019 growth, eu40 | 2022Q1+ / 2023Q1+ | 16 / 14 | 12 / 10 | -0.866 / -0.794 | 1.320 / 1.045 | 1.585 / 1.246 | 0 / 2 |

(A) is far worse than the primary because a 2022 value near zero (vs 2019) next to a 20 to 25 target point drags the early fits the wrong way; (B) reproduces W2 exactly, as pre-stated, and shows that the whole W1 failure is the two 2022 rows sitting inside the first eight fits (the walk-forward slope on W1 runs 0.24 to 0.54 against 0.53 to 0.70 on W2). The level of flights relative to 2019 has the wrong sign against nights growth and is not a candidate.

### Secondary target `total_nights_yoy`

| feature | window | n | wf_n | first scored | r | perm p | ratio vs naive | vs AR(1) | jackknife max | jk n < 1 |
|---|---|---|---|---|---|---|---|---|---|---|
| eu40_flt_da_full | 2022Q1+ | 18 | 14 | 1Q23 | 0.849 | 0.001 | 1.254 | 0.904 | 1.521 | 0 / 14 |
| eu40_flt_da_full | 2023Q1+ | 14 | 10 | 1Q24 | 0.836 | 0.004 | 0.884 | 0.906 | 1.099 | 9 / 10 |
| eu_core_flt_da_full | 2022Q1+ | 18 | 14 | 1Q23 | 0.851 | 0.001 | 1.258 | 0.907 | 1.537 | 0 / 14 |
| eu_core_flt_da_full | 2023Q1+ | 14 | 10 | 1Q24 | 0.828 | 0.010 | 0.911 | 0.934 | 1.148 | 9 / 10 |
| eu40_flt_da_qtd75pit | 2022Q1+ | 16 | 12 | 3Q23 | 0.932 | 0.001 | 0.931 | 0.651 | 1.059 | 10 / 12 |
| eu40_flt_da_qtd75pit | 2023Q1+ | 14 | 10 | 1Q24 | 0.814 | 0.010 | 0.931 | 0.954 | 1.104 | 8 / 10 |
| eu_core_flt_da_qtd75pit | 2022Q1+ | 16 | 12 | 3Q23 | 0.936 | 0.001 | 0.939 | 0.656 | 1.080 | 10 / 12 |
| eu_core_flt_da_qtd75pit | 2023Q1+ | 14 | 10 | 1Q24 | 0.812 | 0.014 | 0.944 | 0.967 | 1.136 | 8 / 10 |
| eu40_flt_da_lag1 | 2022Q1+ / 2023Q1+ | 18 / 14 | 14 / 10 | | 0.722 / 0.551 | 0.004 / 0.063 | 1.855 / 1.104 | | | 0 / 1 |

Same shape as the primary: short window only. The `_qtd75pit` rows on total nights read below 1.0 on both windows, but that is not a survivor claim: the PIT series starts 3Q22 (first commit June 2022), so its W1 scored set is 3Q23 to 2Q26 (wf_n 12), not 1Q23 to 2Q26 (wf_n 14), and it drops the two quarters (1Q23, 2Q23) on which the `_full` feature loses. It is the same 2022-base-effect dependence in another form, and the jackknife max is above 1 on both windows.

### Revision check (source: `revision_summary.csv`, `revision_check.csv`; 144 commit pairs 5 to 10 days apart, 998 day observations, 2022-06 to 2026-09)

| subset | pairs | days | eu40 median abs rev (flights) | eu40 median abs rev % | eu40 p90 abs rev % | share non-zero | eu_core median abs rev % | eu_core p90 abs rev % |
|---|---|---|---|---|---|---|---|---|
| all last-7 days | 144 | 998 | 0 | 0.000 | 0.003 | 12.8 % | 0.000 | 0.003 |
| last day in file only | 144 | 144 | 2 | 0.004 | 0.014 | 81.9 % | 0.003 | 0.010 |
| 2025 onward | 66 | 452 | 0 | 0.000 | 0.003 | 14.4 % | 0.000 | 0.003 |

Revisions are effectively nil: below the 0.5 % line, so the live qtd75 is quoted as it stands. One outlier in 998: the 23 Mar 2026 commit carried 22 Mar 2026 as a partial day (698 flights against 35,060 a week later), which is why the last day in any vintage should be checked for completeness before it is quoted; the 13 Sep 2026 value in the 14 Sep commit (47,639 eu40) sits inside its neighbours (45,047 to 48,107) and is complete. The qtd68 variant (dropping the last week) reads +3.08 % / +2.68 %, within 0.05 pp of qtd75.

### PIT qtd75 vintages (source: `qtd75_pit.csv`)

| quarter | day 75 | commit | commit date | lag (days) | eu40 qtd75 PIT | eu_core qtd75 PIT |
|---|---|---|---|---|---|---|
| 3Q22 | 2022-09-13 | 55f13a3f26 | 2022-09-14 | 1 | 39.25 | 42.71 |
| 4Q22 | 2022-12-14 | 14d3f98f26 | 2022-12-15 | 1 | 22.13 | 23.11 |
| 1Q23 | 2023-03-16 | 1d85aa6c93 | 2023-03-17 | 1 | 28.79 | 27.90 |
| 2Q23 | 2023-06-14 | 2ab5196f4d | 2023-06-29 | 15 | 8.51 | 7.15 |
| 3Q23 | 2023-09-13 | 0b189dd87c | 2023-09-14 | 1 | 7.78 | 7.17 |
| 4Q23 | 2023-12-14 | b184f11994 | 2023-12-15 | 1 | 8.75 | 9.12 |
| 1Q24 | 2024-03-15 | e52e4f1e69 | 2024-03-16 | 1 | 6.38 | 6.77 |
| 2Q24 | 2024-06-14 | 0d5ae5a101 | 2024-06-15 | 1 | 7.59 | 7.81 |
| 3Q24 | 2024-09-13 | 3586eac74d | 2024-09-16 | 3 | 5.04 | 5.51 |
| 4Q24 | 2024-12-14 | 61e3185236 | 2024-12-15 | 1 | 5.17 | 4.62 |
| 1Q25 | 2025-03-16 | c7ac5abe87 | 2025-03-17 | 1 | 6.65 | 5.99 |
| 2Q25 | 2025-06-14 | aaa8c4d85e | 2025-06-15 | 1 | 4.98 | 4.26 |
| 3Q25 | 2025-09-13 | b675376366 | 2025-09-22 | 9 | 3.95 | 3.38 |
| 4Q25 | 2025-12-14 | 4942c23722 | 2025-12-15 | 1 | 5.53 | 4.43 |
| 1Q26 | 2026-03-16 | 758ed71019 | 2026-03-17 | 1 | 2.93 | 2.56 |
| 2Q26 | 2026-06-14 | 4085819131 | 2026-06-30 | 16 | 0.84 | 1.34 |
| 3Q26 | 2026-09-13 | c3d58c5cd2 | 2026-09-14 | 1 | 3.04 | 2.65 |

Commit gaps (no pushes April to May 2023, November 2023, most of June 2026) push three vintages 9 to 16 days late; since revisions are nil the values are the same as the day-76 vintage would have been, but the reader should know those three readings were not on GitHub on day 76.

### Live reading (source: `C_live_reading.csv`; current vintage, 14 Sep 2026 commit)

| aggregate | 3Q26 qtd75 y/y (1 Jul to 13 Sep vs same days 2025) | same, 364-day aligned | qtd68 | July | August | 1 to 13 Sep | 2Q26 full | 1Q26 full | EMEA nights mid 2Q26 / 1Q26 (panel) | total nights 2Q26 |
|---|---|---|---|---|---|---|---|---|---|---|
| eu40 | **+3.04 %** (3,569,229 vs 3,463,875 flights) | +3.02 % | +3.08 % | +3.41 % | +2.71 % | +2.95 % | +1.22 % | +3.19 % | 8.0 / 5.0 | 10.34 |
| eu_core | **+2.65 %** (3,116,606 vs 3,036,265) | +2.63 % | +2.68 % | +3.05 % | +2.28 % | +2.55 % | +1.53 % | +2.96 % | 8.0 / 5.0 | 10.34 |

The red team's sample check (+3.04 %, +1.2 %, +3.2 %) is reproduced to the decimal. In-sample OLS on 1Q23 to 2Q26 (not a forecast, a translation): `eu40_flt_da_qtd75` +3.04 maps to EMEA nights y/y 6.5 (naive 8.0) and to total nights y/y 9.0 (naive 10.3); `eu_core` 6.4 and 8.9. The short-window walk-forward RMSE of the `_full` feature on EMEA nights is 2.7 pp, so the mapped 6.5 carries roughly a plus or minus 3 pp band even before the duplicate caveat.

### Country weights, share of `flt_da` by state, calendar 2025 (source: `country_weights_2025.csv`, for WP-X)

| rank | state | flt_da 2025 | share of eu40 % | in eu_core | share of eu_core % |
|---|---|---|---|---|---|
| 1 | United Kingdom | 1,763,705 | 12.54 | yes | 14.22 |
| 2 | Germany | 1,559,483 | 11.09 | yes | 12.57 |
| 3 | Spain | 1,432,886 | 10.19 | yes | 11.55 |
| 4 | France | 1,215,633 | 8.65 | yes | 9.80 |
| 5 | Italy | 1,141,691 | 8.12 | yes | 9.20 |
| 6 | Turkiye | 895,406 | 6.37 | no | |
| 7 | Netherlands | 574,953 | 4.09 | yes | 4.63 |
| 8 | Switzerland | 464,198 | 3.30 | yes | 3.74 |
| 9 | Poland | 445,649 | 3.17 | yes | 3.59 |
| 10 | Greece | 430,125 | 3.06 | yes | 3.47 |
| 11 | Portugal | 396,922 | 2.82 | yes | 3.20 |
| 12 | Belgium and Luxembourg | 394,303 | 2.80 | yes | 3.18 |
| 13 | Austria | 312,048 | 2.22 | yes | 2.52 |
| 14 | Ireland | 310,184 | 2.21 | yes | 2.50 |
| 15 | Denmark | 288,949 | 2.06 | yes | 2.33 |
| 16 | Morocco | 229,418 | 1.63 | no | |
| 17 | Sweden | 222,457 | 1.58 | yes | 1.79 |
| 18 | Norway | 213,790 | 1.52 | yes | 1.72 |
| 19 | Romania | 187,904 | 1.34 | yes | 1.51 |
| 20 | Czech Republic | 160,416 | 1.14 | yes | 1.29 |
| 21 | Finland | 146,323 | 1.04 | yes | 1.18 |
| 22 | Hungary | 144,129 | 1.03 | yes | 1.16 |
| 23 | Israel | 138,965 | 0.99 | no | |
| 24 | Croatia | 121,113 | 0.86 | yes | 0.98 |
| 25 | Serbia and Montenegro | 106,214 | 0.76 | no | |
| 26 | Cyprus | 103,598 | 0.74 | yes | 0.83 |
| 27 | Bulgaria | 89,243 | 0.63 | yes | 0.72 |
| 28 | Georgia | 72,903 | 0.52 | no | |
| 29 | Malta | 72,608 | 0.52 | yes | 0.59 |
| 30 | Albania | 70,023 | 0.50 | no | |
| 31 | Latvia | 63,105 | 0.45 | yes | 0.51 |
| 32 | Lithuania | 58,086 | 0.41 | yes | 0.47 |
| 33 | Moldova | 44,600 | 0.32 | no | |
| 34 | Armenia | 42,671 | 0.30 | no | |
| 35 | Estonia | 37,574 | 0.27 | yes | 0.30 |
| 36 | Slovakia | 31,496 | 0.22 | yes | 0.25 |
| 37 | Bosnia-Herzegovina | 26,818 | 0.19 | no | |
| 38 | North Macedonia | 26,171 | 0.19 | no | |
| 39 | Slovenia | 24,648 | 0.18 | yes | 0.20 |
| 40 | Ukraine | 60 | 0.00 | no | |

Total eu40 2025: 14,060,468 flights; eu_core 88.2 % of it; the top five states carry 50.6 %. These are flight movements at the destination or origin state, so a flight between two member states counts once in each; they are destination volume weights, not passenger or nights weights, and Spain's Canary Islands are folded into Spain (upstream note).

## What failed or could not be done, and why

- SURVIVOR was not reached: the 2022Q1+ window fails (1.118 / 1.189) on both aggregates, with every jackknife drop above 1. The failure is entirely the two 2022 rows in the first eight fits (sensitivity B shows W1 collapsing to W2's 0.82 once they are dropped), which is a property of the target's start date and the reopening base, not of the 2026 data; but the pre-registered line says both windows, so it is a short-window survivor and nothing more.
- T0 marked the feature a duplicate of `avia_paoc` on history (r 0.986 to 0.994). The short-window ratios (0.82 / 0.83) are close to what `avia_eu27_full` scored on the same window (0.75) in the govdata run; the flights series does not add information about the past, it adds the live quarter.
- The PIT history of `_qtd75` starts 3Q22 (repo created June 2022), so on total nights its W1 scored set is shorter than the `_full` feature's; three PIT vintages (2Q23, 3Q25, 2Q26) sit 9 to 16 days after day 75 because of commit gaps.
- The harness has no EMEA nights target; nothing registered, `score.py` not run (pre-stated).
- The WP-O licence question is open (no LICENSE upstream); the raw files are not committed.
- The first end-to-end `run.py` exited 1 on a C4 boolean-indexing precedence bug; fixed, re-run exit 0.

## Interpretation

The daily flight counts are a clean, unrevised, one-day-lag measure of EMEA air travel volume and they track the regional nights bucket about as well as anything held (r 0.87 on 1Q23+, walk-forward 0.82 against naive on the short window, ten of ten jackknife drops below 1, permutation p 0.002). They do not survive the long window, and on the scored history they are the Eurostat passenger series by another name (r 0.99). What they are worth is the one thing the held series cannot give: a reading for the quarter in progress. That reading says European air traffic re-accelerated by about 2 pp from 2Q26 (+1.2 %) to the first 75 days of 3Q26 (+3.0 % eu40, +2.7 % eu_core), with July the strongest month (+3.4 %) and August and early September at +2.7 to +3.0 %. Management's 2Q26 phrase was "high-single digit growth, accelerating from Q1 2026; steady recovery from Middle East"; the Q1 to Q2 step in flights (3.2 to 1.2) went the other way from the step in nights (5 to 8), which is a reminder that the two series share a level and a trend but not their quarter-to-quarter moves (sign accuracy 0.58 to 0.60). Read the +3.0 % as corroboration that EMEA volume in 3Q26 is at least as firm as in 2Q26, consistent with a mid-to-high-single-digit EMEA nights print, and not as a number to put in the guide. The country weights are the WP-X deliverable: five states (UK, Germany, Spain, France, Italy) carry half of EMEA destination flight volume; Turkiye is the sixth and sits outside eu_core.

## Harness change requests

1. `targets.csv` carries no regional nights target. Add `emea_nights_yoy_mid` (and the other three regional mids) from `data/processed/overnight/10_regional_panel_quarterly.csv` as target metrics, with a basis column (numeric / derived / bucket) so the scorer can down-weight the derived 2Q23 to 3Q24 rows. Until then regional features cannot be registered through FORMAT 1.0 and stay on the govdata V2/G scoreboard, which is where this build lands.
2. If (1) is done, register `eu-flights-v1__emea_nights_yoy_next_q` with the `_qtd75pit` vintages as the PIT information set at each guide date (the guide dates fall about 35 to 40 days after quarter end, so the full quarter is in the file by then; the qtd75 vintage is the conservative choice that matches what the team sees on 14 Sep). n_params 2 (OLS slope and intercept).
3. `nights_m` is a harness target; the secondary result on total nights (0.88 / 0.91 short window, 1.25 long window) does not pass the two-window rule, so no registration is requested on it.

## RESUME

The build is complete and reproducible with `python analysis/src/govdata_v2/run.py` (exit 0, 31 s, needs the git mirror at `C:/Users/krish/abnb_ia_capture/euctrl_daio_git`). The next agent should (i) get the WP-O licence line logged before any of these numbers goes into a memo exhibit (EUROCONTROL network data via the PRU repo, no LICENSE file); (ii) refresh the pull on 1 October when 3Q26 is complete (`curl` the 2026 file, re-run, the `_full` row for 3Q26 will appear) and again on 4 November for the 4Q26 QTD read, and quote the eu40 and eu_core full-quarter y/y next to the 2Q26 +1.2 % in the corroboration slide, never as a level input; (iii) if the harness gains a regional nights target, register `eu-flights-v1` from `C_feature_panel.csv` and `qtd75_pit.csv` as described above; (iv) hand `country_weights_2025.csv` to WP-X as the EMEA destination volume weights, with the caveat that they are flights, not nights. Do not re-test this source on the same construction; the short-window result is a duplicate of avia_paoc's and will not change.
