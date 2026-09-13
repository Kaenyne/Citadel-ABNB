# WS03 — Point-in-time consensus for EBITDA, margin, EPS, FCF; surprise history

Slug `03_consensus_pit`. Written 13 Sep 2026 (Sat night) from the LSEG Workspace desktop session (`py -3.13`, lseg-data 2.1.1)
and the local Bloomberg long file. Rebuild: `python analysis/src/margin_build/03_consensus_pit/run.py` (exit 0; skips the pull when raw exists).

## Bottom line

1. **A full daily point-in-time Street panel now exists for ABNB** (adjusted EBITDA mean/median/high/low/sd/n, revenue, EPS, EBIT (= operating
   income), net income, FCF, COGS, gross income, pre-tax, capex, and LSEG's own EBITDA-margin mean) for every fiscal period 4Q20-2Q27 and
   FY2020-FY2028, one row per trading day 4 Jan 2021 - 11 Sep 2026, with the last-revision date of every field. Raw stays in `data/raw` (licensed);
   values stamped at the 23 print/guide dates plus 12 Sep 2026 are in `03_consensus_at_dates.csv` (241 stamped rows), and a 400-row
   proposed L0 append (`03_L0_append_candidates.csv`, L0 schema, never merged by me) carries EBITDA / revenue / EPS / FCF / operating income
   at print, pre-guide and current.
2. **Pass line met.** 22/22 prints 1Q21-2Q26 have an at-print EBITDA consensus; 21/22 observations are no older than 7 days (1Q26 is 9 days;
   test asked for >=18). All 7 comparable repo rows (`16_consensus_at_print_merged.csv`, 4Q22-2Q26) agree within 0.71%; the eighth (4Q20, an
   unattributed press number, -$132.8M) sits outside the window and LSEG says -$122.1M (8% apart). The 6 Aug 2026 pre-guide 3Q26 revenue
   on LSEG is **$4,609.85M** — the L0 hard rule ($4,610M) to the dollar.
3. **The Street has under-called the adjusted EBITDA margin at 21 of 22 prints** (only 1Q23 missed, by 0.07 pt). In the windows that count the
   beat is small and shrinking: W1 (1Q23-2Q26, n=14) mean **+1.82 pt** (sd 1.41), W2 (1Q24-2Q26, n=10) **+1.70 pt** (sd 1.41); recency-weighted
   (half-life 4 q) +1.36 / +1.26; the last four prints averaged **+0.43 pt** (+0.11, +0.16, +0.87, +0.59). In dollars the W2 EBITDA beat is
   +9.2% on average, median +6.3%, and it has NOT been a function of the revenue beat: regressing the $ EBITDA surprise on the $ revenue surprise
   gives beta 0.57 (t 1.4) in W1 and 0.43 (t 0.96) in W2 with an intercept of ~$36-39M — a fixed cost under-shoot, not flow-through.
4. **Street margin errors are not exploitable as a series**: lag-1 autocorrelation 0.26 (se 0.21 under the null), lag-4 0.15; in W2 lag-1 0.31,
   lag-4 -0.21. The sign is persistent only because almost everything is a beat.
5. **The Street anchors on the FY floor.** Five trading days after each of the 10 numeric FY margin guides (FY24 x4, FY25 x4, FY26 x2) the
   consensus FY margin sat within 0.5 pt of the floor 8 times (mean gap +0.49 pt). Actual FY24 beat its floor by 1.4 pt, FY25 by 0.6. Today
   (11 Sep) FY26 consensus is **35.62%** on mean/mean (34.66% on LSEG's margin-mean field) against the ">= 35.5%" floor; FY27 36.45% / 35.06%.
6. **Bloomberg local file is pull-date anchored** (repo memory confirmed): `obs_date` is a true revision history of the periods that were 1FQ/2FQ/1FY/2FY
   on 5 Sep 2026 (3Q26, 4Q26, FY26, FY27), not a rolling next-period series. Against LSEG's fixed-period series the BEST values match to
   0.07-1.2% MAPE (n 3-11 overlapping obs); against the rolling series they are 50-900% off. Use it only for FY26/FY27/3Q26 revision history since 2024.

## What ran (exact commands)

```bash
cd "C:\Users\krish\citadel-abnb-margins"
py -3.13 analysis/src/margin_build/03_consensus_pit/pull_lseg.py     # 35 raw files, ~4 min, manifest with sha256
python   analysis/src/margin_build/03_consensus_pit/build.py         # all derived tables + pass line
py -3.13 analysis/src/margin_build/03_consensus_pit/figures.py       # 3 PNGs
python   analysis/src/margin_build/03_consensus_pit/run.py           # the three above, exit 0
```

Raw: `data/raw/margin_build/03_consensus_pit/` (33 LSEG CSVs + `derived_daily_revision_paths_LICENSED.csv`), manifest
`data/manifests/margin_build/03_consensus_pit.csv` (35 rows: file, ric, group, period, frequency, fields, pull timestamp UTC, rows, sha256).

## Field-discovery log (LSEG, ABNB.O, `ld.get_data`, ~25 min)

Verified behaviours that matter for point-in-time use:

* `Period=FQ1` is **relative to the row date** and rolls to the next quarter **on the print date itself** (2023-02-14 already shows `FY2023Q1`).
  So "consensus at print" for the printed quarter = the FQ1 row of the **previous trading day**; the print-day FQ1 row is the pre-guide value for
  the guided quarter (its last-revision date is <= the print date), and post-guide revisions arrive from D+1. After a print, `FQ0` holds the
  frozen pre-print mean (1Q26: 484.04 vs the repo's 485.0).
* `.calcdate` = row date; `.fperiod` = absolute period (`FY2023Q1`, `FY2026`); `.periodenddate`; `.date` = last change of that field.
  Staleness at the stamped dates: median 0-1 day, max 9 (1Q26 EBITDA) and 12 (one next-quarter pre-guide row).
* Daily frames hold trading days (1,430 rows for the window).

| field | returns | note |
|---|---|---|
| `TR.EBITDAMean/Median/High/Low/StdDev` | yes | Street adjusted basis: `TR.EBITDAActValue` equals the letter's adjusted EBITDA (diff <= $0.4M in 2021, zero since) |
| `TR.EBITDANumOfEst` | yes | `TR.EBITDANumberOfEstimates` errors |
| `TR.EBITDAMarginMean` | yes from 2Q24 only | mean of analysts' margins; sits 0.1-1.0 pt below mean/mean for FY periods (FY26 34.66 vs 35.62) |
| `TR.EBITDAReportedMean` | yes | a different basis (3Q26 $2,289M vs $2,362M adjusted) — not used |
| `TR.EBITDAActValue`, `.date` | yes | `.date` is the report timestamp (2026-08-06 16:03) |
| `TR.RevenueMean/Median/High/Low/StdDev/NumOfEst/ActValue` | yes | |
| `TR.EPSMean/Median/StdDev/NumOfEst/NumberOfEstimates/ActValue` | yes | |
| `TR.EBITMean`, `TR.EBITNumOfEst`, `TR.EBITActValue` | yes | operating income proxy (2Q26 cons 759 vs actual 758) |
| `TR.NetProfitMean` (= `TR.NetIncomeMean`), `TR.NetProfitNumOfEst`, `TR.PreTaxProfitMean` | yes | |
| `TR.FCFMean`, `TR.FCFActValue` | yes | no NumOfEst field |
| `TR.COGSMean`, `TR.GrossIncomeMean`, `TR.CAPEXMean`, `TR.DPSMean` | yes | COGS is the only cost line with estimates |
| `TR.OPRMean`, `TR.OperatingIncomeMean`, `TR.SGAExpMean`, `TR.RDExpMean`, `TR.EBITDAAdjMean`, `TR.EPSPreExceptionalsMean`, `TR.OperatingMarginMean`, `TR.*ActReportDate` | **no** | error or all-null |

Peers BKNG.O / EXPE.O: EBITDA mean/n, revenue mean/n, EBITDA-margin mean, actuals; monthly FQ1/FY1/FY2, Jan 2021 - Aug 2026 (68 obs each).

## Surprise history, 1Q21-2Q26 (n = 22) — `03_surprise_history.csv`

Consensus = LSEG mean one trading day before the print; actual = letter adjusted EBITDA (`abnb_quarterly_cost_stack_exsbc.csv`, cross-checked to
`TR.EBITDAActValue`). Street margin = mean EBITDA / mean revenue.

| print | actual EBITDA $M | Street $M | n | stale d | EBITDA surp $M | % | rev surp % | Street mgn % | actual mgn % | **mgn surp pt** | incr. mgn on surprise % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1Q21 | -59 | -362 | 27 | 0 | +303 | +84 | +24.1 | -50.7 | -6.7 | +44.0 | 176 |
| 2Q21 | 217 | 42 | 28 | 2 | +175 | +412 | +6.3 | 3.4 | 16.3 | +12.9 | 220 |
| 3Q21 | 1,101 | 817 | 29 | 3 | +284 | +35 | +9.1 | 39.9 | 49.2 | +9.3 | 152 |
| 4Q21 | 333 | 278 | 29 | 7 | +55 | +20 | +5.2 | 19.1 | 21.7 | +2.6 | 72 |
| 1Q22 | 229 | 74 | 30 | 0 | +155 | +209 | +4.0 | 5.1 | 15.2 | +10.1 | 270 |
| 2Q22 | 711 | 591 | 30 | 0 | +120 | +20 | -0.1 | 28.1 | 33.8 | +5.7 | n/a |
| 3Q22 | 1,457 | 1,387 | 30 | 0 | +70 | +5 | +1.4 | 48.8 | 50.5 | +1.8 | 172 |
| 4Q22 | 506 | 435 | 30 | 0 | +71 | +16 | +2.1 | 23.4 | 26.6 | +3.2 | 179 |
| 1Q23 | 262 | 259 | 28 | 0 | +3 | +1 | +1.5 | 14.5 | 14.4 | **-0.1** | 10 |
| 2Q23 | 819 | 728 | 30 | 2 | +91 | +12 | +2.6 | 30.1 | 33.0 | +2.9 | 143 |
| 3Q23 | 1,834 | 1,747 | 29 | 1 | +87 | +5 | +0.8 | 51.8 | 54.0 | +2.2 | 320 |
| 4Q23 | 738 | 644 | 31 | 0 | +94 | +15 | +2.5 | 29.8 | 33.3 | +3.5 | 174 |
| 1Q24 | 424 | 327 | 33 | 1 | +97 | +30 | +4.0 | 15.9 | 19.8 | +3.9 | 120 |
| 2Q24 | 894 | 862 | 32 | 1 | +32 | +4 | +0.3 | 31.5 | 32.5 | +1.0 | n/a |
| 3Q24 | 1,958 | 1,859 | 34 | 1 | +99 | +5 | +0.4 | 50.0 | 52.5 | +2.5 | 662 |
| 4Q24 | 765 | 653 | 34 | 2 | +112 | +17 | +2.5 | 27.0 | 30.8 | +3.9 | 187 |
| 1Q25 | 417 | 363 | 33 | 0 | +54 | +15 | +0.6 | 16.1 | 18.4 | +2.3 | 427 |
| 2Q25 | 1,043 | 971 | 32 | 7 | +72 | +7 | +2.0 | 32.0 | 33.7 | +1.7 | 119 |
| 3Q25 | 2,051 | 2,038 | 34 | 1 | +13 | +1 | +0.4 | 50.0 | 50.1 | +0.1 | 76 |
| 4Q25 | 786 | 764 | 34 | 1 | +22 | +3 | +2.3 | 28.1 | 28.3 | +0.2 | 35 |
| 1Q26 | 519 | 484 | 35 | 9 | +35 | +7 | +2.4 | 18.5 | 19.4 | +0.9 | 56 |
| 2Q26 | 1,261 | 1,229 | 35 | 7 | +32 | +3 | +0.9 | 34.4 | 35.0 | +0.6 | 101 |

("incr. mgn on surprise" = EBITDA surprise / revenue surprise, shown only when |revenue surprise| >= $10M.)

Other lines in the same file: EPS (LSEG actual vs mean: W2 surprises -0.13 to +0.17, 5 beats / 4 misses / 1 in line), FCF (W2 surprises
-$498M to +$879M, sd ~$400M — the Street cannot time working capital; 5 misses in 10), EBIT/operating income (W2 mean beat +$38M,
0-136), consensus at the prior guide date and 5 trading days after it, guide-implied margin and both distances.

## Surprise statistics — `03_surprise_stats.csv/.json`, `03_flowthrough_regressions.csv`

**Margin surprise (actual minus Street margin, pts)**

| slice | n | mean EW | sd EW | mean RW (hl 4q) | sd RW | median | share beats | EBITDA % surp mean EW / RW | rev % surp mean (sd) |
|---|---|---|---|---|---|---|---|---|---|
| all 1Q21-2Q26 | 22 | +5.24 | 9.30 | +1.81 | 3.39 | +2.54 | 95% | +42.1 / +11.8 | +3.43 (5.12) |
| W1 1Q23-2Q26 | 14 | **+1.82** | 1.41 | +1.36 | 1.27 | +1.93 | 93% | +8.9 / +7.2 | +1.66 (1.11) |
| W2 1Q24-2Q26 | 10 | **+1.70** | 1.41 | +1.26 | 1.24 | +1.37 | 100% | +9.2 / +7.0 | +1.58 (1.23) |
| last 8 (3Q24-2Q26) | 8 | +1.51 | 1.32 | | | | 100% | +7.3 | |
| last 4 (3Q25-2Q26) | 4 | **+0.43** | 0.38 | | | | 100% | +3.4 | +1.5 |
| by Q of year, Q1 | 6 | +10.19 | 16.96 | +2.54 | 6.12 | +3.12 | 83% | | +6.09 |
| Q2 | 6 | +4.14 | 4.66 | +1.43 | 1.96 | +2.29 | 100% | | +2.02 |
| Q3 | 5 | +3.16 | 3.57 | +1.38 | 2.02 | +2.15 | 100% | | +2.44 |
| Q4 | 5 | +2.68 | 1.48 | +1.83 | 1.95 | +3.24 | 100% | | +2.93 |
| by year 2021 / 22 / 23 / 24 / 25 / 26H1 | 4 each (2 in 2026) | +17.2 / +5.2 / +2.1 / +2.8 / +1.1 / +0.7 | | | | | | | |

Equal- and recency-weighted numbers disagree on the full sample (2021 dominates EW) and agree in W1/W2 (the RW mean is 0.4-0.5 pt lower
because the 2025-26 beats are smaller). **Seasonality of the surprise is not established**: the Q1 number is 2021-22 noise; within W2 the
quarter-of-year means are +2.0 (Q1, n 3), +1.1 (Q2, 3), +1.3 (Q3, 2), +2.0 (Q4, 2) — indistinguishable at these n. Q3 (the 5 Nov print) has
the smallest recent beats: +2.5, +0.1 in 3Q24/3Q25.

**Flow-through of revenue beats to EBITDA beats** (OLS, `EBITDA surprise = a + b * revenue surprise`)

| spec | n | a | b | se(b) | t | R2 |
|---|---|---|---|---|---|---|
| $M, all | 22 | 20 | 1.33 | 0.23 | 5.9 | 0.63 (2021 leverage) |
| $M, all, recency-weighted | 22 | 23 | 0.73 | 0.32 | 2.3 | 0.21 |
| $M, W1 | 14 | **36** | 0.57 | 0.41 | 1.4 | 0.14 |
| $M, W2 | 10 | **39** | 0.43 | 0.45 | 1.0 | 0.10 |
| %, W1 | 14 | 0.5 | 5.07 | 1.52 | 3.3 | 0.48 |
| %, W2 | 10 | 1.2 | 5.06 | 1.87 | 2.7 | 0.48 |
| margin pts on rev %, W1 | 14 | 0.80 | 0.61 | 0.32 | 1.9 | 0.24 |
| margin pts on rev %, W2 | 10 | 0.85 | 0.54 | 0.36 | 1.5 | 0.22 |

Reading: in the windows that count, a 1% revenue beat is worth roughly +0.5-0.6 pt of margin surprise (not significant at n 10-14), and there is
a constant ~$35-40M / ~+0.8 pt beat that revenue does not explain — the cost lines come in below the Street. The % specification's beta of ~5 is
the arithmetic of low-margin quarters (Q1/Q4) and should not be read as operating leverage.

**Street's implied incremental margin vs actual**

| measure | n | median | mean | IQR |
|---|---|---|---|---|
| implied on the surprise (EBITDA surp / revenue surp), all | 20 | 162% | 183% | 95-195 |
| same, W2 | 9 | **119%** | | |
| Street's own revision guide->print (dEBITDA cons / dRevenue cons) | 17 | 47% | 79% | 33-109 |
| actual y/y incremental margin (dEBITDA / dRevenue, y/y) | 18 | 40% | 37% | |

The Street revises EBITDA roughly in line with the true y/y incremental margin (~40-47%) when it revises revenue, but the realised beat carries an
incremental margin above 100%: the beat is cost-side.

**Autocorrelation of the margin error**: lag-1 0.26, lag-4 0.15 (n 22, se under the null 0.21); W2 lag-1 0.31, lag-4 -0.21. EBITDA % error lag-1 0.12.
Not distinguishable from zero; nothing to model.

**Street vs guide-implied margin** (n 17 quarters with a numeric or y/y-anchored margin guide): Street sits 0.76 pt **below** the guide-implied
level on average (above it 8/17), the actual 1.38 pt above it (above 10/17). In W2: 2Q25 guide 32.5 ceiling / Street 32.0 / actual 33.7;
3Q25 floor 49.3 / 50.0 / 50.1; 4Q25 ceiling 30.8 / 28.1 / 28.3; 1Q26 point 18.4 / 18.5 / 19.4; 2Q26 floor 33.7 / 34.4 / 35.0. When the guide is a
y/y "down" (ceiling), the Street goes well below it (4Q24 -6.3, 3Q24 -4.0, 1Q25 -3.8 pt) and the actual lands between.

**FY floor anchoring** (`03_fy_floor_anchoring.csv`)

| guide date | FY | floor | cons margin +5td | gap pt | n |
|---|---|---|---|---|---|
| 2024-02-13 | FY24 | >=35.0 | 36.36 | +1.36 | 40 |
| 2024-05-08 | FY24 | >=35.0 | 36.24 | +1.24 | 42 |
| 2024-08-06 | FY24 | >=35.0 | 35.44 | +0.44 | 41 |
| 2024-11-07 | FY24 | ~35.5 | 35.55 | +0.05 | 43 |
| 2025-02-13 | FY25 | >=34.5 | 34.91 | +0.41 | 43 |
| 2025-05-01 | FY25 | >=34.5 | 34.83 | +0.33 | 43 |
| 2025-08-06 | FY25 | >=34.5 | 34.97 | +0.47 | 43 |
| 2025-11-06 | FY25 | ~35.0 | 35.10 | +0.10 | 43 |
| 2026-05-07 | FY26 | >=35.0 | 35.41 | +0.41 | 42 |
| 2026-08-06 | FY26 | >=35.5 | 35.61 | +0.11 | 43 |

Within 0.5 pt of the floor 8/10, within 1 pt 8/10 (the two misses are the early-2024 rows when the Street still carried FY23's 36.1%). Actual FY24 36.4
(+1.4 vs floor), FY25 35.1 (+0.6). The Street treats the floor as the point; management has beaten its floor both years, by less in 2025.

**Revision paths** (`03_revision_paths.csv`; 20 guided quarters 4Q21-3Q26 and FY2021-FY2026)

| | median | mean | share < 0 |
|---|---|---|---|
| guide jump, EBITDA cons, D-1 -> D+5td | +1.55% | | 35% |
| drift D+5td -> print eve | **+0.13%** | +0.07% | 35% |
| total D-1 -> print eve | +2.2% | | |
| margin change guide -> print (mean/mean) | +0.34 pt | | |

The guide sets the level in the first week; drift afterwards is under 1% in 17 of 20 quarters. Post-guide jumps in W2: -6.8% (2Q24), -7.7% (3Q24),
-9.6% (4Q24), -3.5% (1Q25), +1.8, +1.3, +1.5, +2.9, +4.5, **+1.6% (3Q26)**. 3Q26: pre-guide $2,323.8M -> $2,360.1M at D+5 -> $2,361.5M on 11 Sep
(n 34 -> 36; 27 trading days, 3 mean changes since D+5).
FY paths (pre-guide at the prior Q4 print eve -> FY print eve): FY22 +53%, FY23 +12.6%, FY24 **-2.9%** (36.6% -> 35.6% margin), FY25 +2.2%
(34.5% -> 35.1%), FY26 so far +6.4% (35.4% -> 35.6%).

## Current consensus, as of 12 Sep 2026 (LSEG row 11 Sep; `03_current_consensus.csv`)

| period | EBITDA mean $M | median | n | sd | high / low | last chg | revenue mean $M (n) | margin mean/mean | LSEG margin field | EPS (n, sd) | FCF $M | EBIT $M | NI $M | COGS $M |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3Q26 | **2,361.5** | 2,357.8 | 36 | 20.0 | 2,420 / 2,323 | 7 Sep | 4,744.3 (37) | **49.78%** | 49.93 | 2.85 (34, 0.15) | 1,736 | 1,909 | 1,703 | 632 |
| 4Q26 | **913.7** | 909.5 | 36 | 26.5 | 974 / 871 | 7 Sep | 3,161.8 (37) | **28.90%** | 28.06 | 0.86 (34, 0.13) | 724 | 454 | | 551 |
| FY26 | **5,053.7** | 5,052.0 | 44 | 40.2 | 5,144 / 4,946 | 7 Sep | 14,189.6 (44) | **35.62%** | 34.66 | 5.31 (43, 0.18) | 4,918 | 3,235 | | 2,394 |
| FY27 | **5,766.1** | 5,776.0 | 44 | 154.2 | 6,255 / 5,493 | 10 Sep | 15,819.3 (44) | **36.45%** | 35.06 | 6.23 (43, 0.46) | 5,353 | 3,804 | | 2,658 |
| FY28 | 6,602.7 | 6,563.8 | 26 | 271.9 | 7,063 / 6,041 | 8 Sep | 17,535.1 (27) | 37.65% | 35.11 | 7.52 (26, 0.80) | 5,771 | 4,510 | | 2,945 |
| Bloomberg 3Q26 (pull 5 Sep) | 2,359.9 | | | | | | 4,743.7 | 49.75% | | 2.86 | | | | |
| Bloomberg FY26 | 5,046.8 | | | | | | 14,161.9 | 35.64% | | 5.29 | | | | |
| Bloomberg 4Q26 / FY27 | n/a | | | | | | 3,154.0 / 15,760.2 | | | | | | | |
| Management (6 Aug) | 3Q26 revenue $4.69-4.77B; 3Q26 margin "down slightly" vs 50.1%; FY26 margin **>= 35.5%** | | | | | | | | | | | | | |

The two vendors agree within 0.2% on every overlapping number. Arithmetic the model must reconcile: 3Q26 + 4Q26 consensus EBITDA (3,275) plus
1H26 actual (1,780) = 5,055 = FY26 consensus; 3Q26 Street margin 49.8% vs 50.1% a year ago is exactly "down slightly"; 4Q26 28.9% vs 28.3%
is +0.6 pt y/y; FY27 implies +0.8 pt margin expansion on +11.5% revenue. Note the gap between mean/mean and LSEG's margin-mean field widens
with horizon (FY26 1.0 pt, FY28 2.5 pt): the analysts with high EBITDA are the ones with high revenue.

## Bloomberg anchoring test (`03_bloomberg_anchoring_test.csv`)

| BEST field / fperiod | n obs | MAPE vs LSEG rolling next-period | n overlap fixed | MAPE vs LSEG fixed period (3Q26/4Q26/FY26/FY27) |
|---|---|---|---|---|
| EBITDA 1FQ | 23 | 767% | 4 | **0.28%** |
| EBITDA 1FY | 23 | 239% | 11 | **0.54%** |
| SALES 1FQ / 2FQ | 23 / 23 | 118% / 50% | 4 / 3 | 0.07% / 0.17% |
| SALES 1FY / 2FY | 23 / 23 | 60% / 58% | 11 / 7 | 0.22% / 0.21% |
| EPS 1FQ / 1FY | 23 / 23 | 893% / 142% | 4 / 11 | 1.16% / 1.10% |

Verdict: fixed-period, pull-date anchored. The 2021-23 values (e.g. 1FQ EBITDA $2,015M on 31 Mar 2021) are early long-range estimates for
3Q26/FY26 from one or two brokers, not the then-next-quarter Street. Do not use the Bloomberg file for any at-print or pre-guide value.

## Peers (`03_peer_consensus_monthly.csv`, monthly, Jan 2021 - Aug 2026)

FY26 consensus EBITDA margin (mean/mean) as of Aug/Sep 2026: **ABNB 35.6%, BKNG 37.1%, EXPE 25.5%**; FY27: 36.4 / 38.5 / 26.1. Levels, n and the
LSEG margin field per month are in the file for M6's cyclicality comparison (BKNG/EXPE FQ1 also there).

## Caveats

* **Licence.** LSEG and Bloomberg values are licensed. Only date-stamped values, per-quarter summaries and statistics are in `data/processed`;
  the daily series (including the derived index paths) stay under `data/raw`. Do not paste the daily files into the deck.
* **Vendor differences vs the repo.** `16_consensus_at_print_merged.csv` EBITDA rows vs LSEG at print eve: 4Q22 432.0 vs 435.1 (+0.7%),
  4Q23 645.0 vs 644.0 (-0.2%), 1Q24 326.0 vs 326.5 (+0.2%), 3Q24 1,860 vs 1,859 (-0.1%), 4Q24 653.5 vs 653.0 (-0.1%), 1Q26 485.0 vs 484.0
  (-0.2%), 2Q26 1,225.6 (TIKR-derived) vs 1,228.6 (+0.2%); 4Q20 -132.8 (unattributed press) vs -122.1 (+8%, outside the pass window).
  Revenue rows: all within 0.4% except 3Q22 (repo Refinitiv 2,800 vs LSEG 2,843, +1.5%; the repo note already flags a Zacks 2,853) and
  1Q21 (714.4 vs 714.4). EPS at print matches the repo to the cent in every W2 quarter.
* **Basis.** LSEG "EBITDA" is the adjusted basis (actuals equal the letters). `TR.EBITDAReportedMean` is a different basis and is not used.
  LSEG EPS actual is the Street-comparable adjusted EPS; the repo's GAAP-flagged quarters (3Q23, 4Q23) are handled by LSEG's own actual.
* **Print-day rows.** The print-day FQ1 row (`guided_q_print_day`) can already contain same-evening revisions; the strictly pre-print value is
  `guided_q_pre_guide` (D-1). Both are in `03_consensus_at_dates.csv`; the L0 candidates use D-1.
* **Staleness.** Max 9 days on the EBITDA mean at print (1Q26); the revenue mean is fresher. Pre-2021 dates (the 2020-11-15 calendar row) are
  before the pull window and are marked `found=False` (10 rows).
* **n is small.** 22 prints, 14 in W1, 10 in W2, 4 since the margin beat shrank. Every regression above is descriptive.
* **The harness calendar** lives at `data/processed/forecast_methods/harness/calendar.csv` (the prompt's `analysis/src/.../calendar.csv` path does not exist).
* No file outside `docs/margin-build/`, `analysis/src/margin_build/`, `data/{processed,raw,manifests}/margin_build/`, `analysis/figures/margin_build/` was touched.
  L0 was **not** edited; `03_L0_append_candidates.csv` is a proposal for a human merge.

## Corrections to existing work

None required. `16_consensus_at_print_merged.csv` is vindicated for every vendor-attributed row; its 4Q20 EBITDA consensus (-$132.8M,
unattributed) should be treated as low confidence — LSEG had -$122.1M (n 26) on 24 Feb 2021. The `04_current_consensus.csv` line "no
published 3Q26 adjusted-EBITDA consensus retrievable" is now superseded: LSEG has $2,361.5M (n 36).

## For the model

| name | value | unit | source |
|---|---|---|---|
| `street_3q26_ebitda` | 2,361.5 (median 2,357.8; sd 20.0; n 36; range 2,323-2,420) | $M | LSEG TR.EBITDAMean FQ1, row 2026-09-11, last change 2026-09-07 |
| `street_3q26_margin` | 49.78 (mean/mean); 49.93 (LSEG margin-mean field) | % | same + TR.RevenueMean 4,744.3 |
| `street_4q26_ebitda` / margin | 913.7 (n 36, sd 26.5) / 28.90 | $M, % | LSEG FQ2 |
| `street_fy26_ebitda` / margin | 5,053.7 (n 44, sd 40.2) / 35.62 (field 34.66) | $M, % | LSEG FY1 |
| `street_fy27_ebitda` / margin | 5,766.1 (n 44, sd 154.2) / 36.45 (field 35.06) | $M, % | LSEG FY2 |
| `street_fy28_ebitda` / margin | 6,602.7 (n 26) / 37.65 | $M, % | LSEG FY3 |
| `street_eps_3q26 / 4q26 / fy26 / fy27` | 2.85 / 0.86 / 5.31 / 6.23 | $ | LSEG TR.EPSMean |
| `street_fcf_3q26 / fy26 / fy27` | 1,736 / 4,918 / 5,353 | $M | LSEG TR.FCFMean |
| `street_ebit_3q26 / fy26 / fy27` | 1,909 / 3,235 / 3,804 | $M | LSEG TR.EBITMean (operating income) |
| `margin_surprise_W2_mean / sd` | +1.70 / 1.41 (RW +1.26 / 1.24); last-4 +0.43 | pt | `03_surprise_stats.csv` |
| `ebitda_surprise_W2_mean_pct / median` | +9.2 / +6.3 | % | same |
| `flowthrough_W2` | intercept +$39M, slope 0.43 (t 1.0) on $ revenue surprise; +0.85 pt + 0.54 x rev% (t 1.5) on margin | | `03_flowthrough_regressions.csv` |
| `fy_floor_gap_post_guide` | +0.49 mean, 8/10 within 0.5 pt | pt | `03_fy_floor_anchoring.csv` |
| `post_guide_jump_median` / `drift_median` | +1.55% / +0.13% | % | `03_revision_paths.csv` |
| free parameters | 0 (all objects are data; the four regressions have 2 each and are descriptive only) | | |

Consensus is the comparison column, never an input (except an explicit M5 object).

## For the 5 Nov card

* Street 3Q26: adj. EBITDA **$2,361M**, margin **49.8%** (-0.3 pt y/y, i.e. exactly management's "down slightly"), revenue $4,744M (top of the
  $4.69-4.77B guide), EPS $2.85, FCF $1.74B. Dispersion is tight (sd $20M, high-low $97M): a print above ~$2,420M beats every estimate.
* Historical prior for the print vs Street: margin beat +1.7 pt (W2 mean) but the last four beats averaged +0.4 pt and the 3Q beats were
  +2.5 (3Q24) and +0.1 (3Q25). A 3Q26 margin of 50.1-50.6% is "in the range of recent beats"; above 51% would be a 2023-24-style beat.
* Street 4Q26 margin 28.9% (+0.6 pt y/y) and FY26 35.6% are where the guide will be judged: the 4Q26 guide needs to imply >= ~$914M EBITDA
  / >= ~$3,162M revenue to avoid a cut; the FY floor will be read literally (Street sits 0.1 pt above 35.5%).
* Do not quote the Bloomberg file for any at-print or pre-guide value; use the LSEG stamped rows.

## Tests counted

Pre-registered: 2 (freshness >= 18/22: **pass** 21/22; agreement with repo rows within 3%: **pass** 7/7). Descriptive (not pass/fail): 10 regressions
(flow-through x 7, margin-on-revenue x 3), 2 autocorrelation checks, 1 anchoring test (Bloomberg, 8 series), 1 FY-floor anchoring tally.

## Files written

Scripts: `analysis/src/margin_build/03_consensus_pit/{pull_lseg.py, build.py, figures.py, run.py, README.md}`.
Processed: `data/processed/margin_build/03_consensus_pit/{03_consensus_at_dates.csv, 03_L0_append_candidates.csv, 03_surprise_history.csv,
03_revision_paths.csv, 03_surprise_stats.csv, 03_surprise_stats.json, 03_flowthrough_regressions.csv, 03_fy_floor_anchoring.csv,
03_current_consensus.csv, 03_bloomberg_anchoring_test.csv, 03_bloomberg_anchoring_test_rows.csv, 03_peer_consensus_monthly.csv, 03_pass_line.json}`.
Raw (gitignored): `data/raw/margin_build/03_consensus_pit/` (34 files). Manifest: `data/manifests/margin_build/03_consensus_pit.csv`.
Figures: `analysis/figures/margin_build/03_consensus_pit_{margin_surprise, revision_paths, fy_floor}.png`. Note: this file.

## RESUME

WS03 is complete; nothing is pending. The next agent should (a) have a human merge `03_L0_append_candidates.csv` into the frozen L0 register
(backup first; 400 rows, ids `LSEG-{AT_PRINT|PRE_GUIDE|CURRENT}-<period>-<metric>-<rowdate>`), (b) point every stage-2 margin method's
`base_street` at `03_consensus_at_dates.csv` (`target_role` = `printed_q_at_print` for the print comparison, `guided_q_pre_guide` for the
pre-guide Street, `fy_current_pre_guide` for the FY floor test), (c) use `03_surprise_history.csv` columns `margin_surprise_pts`,
`ebitda_surprise_musd`, `revenue_surprise_musd` as the ground truth for any "beat the Street" backtest, and (d) if a fresh consensus is
needed after 12 Sep, delete only `abnb_*_D.csv` in the raw folder and re-run `run.py` with the Workspace open (about 4 minutes). The daily
raw stays licensed; never copy it into `data/processed` or a deck.
