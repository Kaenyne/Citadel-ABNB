# ABNB statistical analysis (R / RStudio)

An RStudio project that reads the live driver model (`model/ABNB_driver_model.xlsx`) and the historicals
workbook (`model/ABNB_historicals.xlsx`) plus the model's CSV outputs, and produces 27 figures, 24 tables and
an HTML report. Nothing under `model/` or `data/` is modified (repo rule 1).

**Note on the source file.** The request named "ABNB official model complete". No file by that name exists on
this Mac, OneDrive, iCloud, Google Drive, Gmail or claude.ai artifacts as of 22 Sep 2026. Per `model/README.md`
the live workbook is `ABNB_driver_model.xlsx` (7 Sep 2026 overnight build), so that and `ABNB_historicals.xlsx`
are used. If the official model is a different file, drop it in `model/` and point `R/01_load.R` at it; the
loader keys on row labels, not cell addresses, so a workbook with the same sheet layout needs no other change.

## Run it

```r
# RStudio: File > Open Project > analysis/r_stats/ABNB_stats.Rproj, then
source("run_all.R")        # ~100 s: rebuilds data/, figures/, tables/ and knits ABNB_stats_report.html
```
or from a terminal: `cd analysis/r_stats && Rscript run_all.R`. Each script in `R/` also runs on its own
after `R/01_load.R` has been run once (it caches everything in `data/abnb_tidy.rds`).

Packages: tidyverse, readxl, broom, sandwich, lmtest, car, forecast, strucchange, tseries, gt, patchwork,
scales, zoo (all installed on this machine, R 4.5.2).

## What is in each script

| Script | Question | Methods | Outputs |
|---|---|---|---|
| `01_load.R` | Get the workbooks into tidy frames | label-keyed parse of the Historicals sheet (22 quarters x 90 variables), Earnings sheet (23 prints), driver-model History and Street sheets, model CSVs, daily closes | `data/abnb_quarterly.csv`, `data/abnb_earnings_prints.csv`, `data/abnb_tidy.rds` |
| `02_descriptives.R` | What do the KPIs look like, how seasonal are they, what moves together | summary stats, CAGR, small multiples, seasonal-subseries plot, quarter shares, Spearman correlation matrix, regional growth | figs 01-05, tables 01-03 |
| `03_growth_decomposition.R` | What is revenue growth made of; what moved the margin | log decomposition (nights / ADR ex-FX / FX / take rate) from the workbook, cost-line margin bridge, unit-cost vs revenue-per-night split, cost ratios | figs 06-09, table 04 |
| `04_regressions.R` | Operating leverage, scale economies, seasonality, marketing efficiency, take-rate drivers | log-log elasticities of each cash cost line to revenue with quarter dummies and Newey-West SE; margin on log revenue; Durbin-Watson, Breusch-Pagan, Shapiro, VIF; ANOVA and Kruskal-Wallis by quarter; cross-correlation of S&M growth and nights growth; take rate on quarter, trend, FX | figs 10-12, tables 05-10 |
| `05_time_series.R` | What do pure time-series models say about 3Q26-4Q27 vs the driver model and guide | ETS and auto-ARIMA on log revenue and log nights with 80% intervals, seasonal naive, STL decomposition, rolling-origin backtest (MAPE at h = 1, 2), Andrews supF mean-shift tests, BIC breakpoints, ADF and KPSS | figs 13-16, tables 11-15 |
| `06_earnings_reaction.R` | What moves the stock on print day | reaction summary; Wilcoxon signed-rank, sign test, t-test; Fisher exact and rank-sum on beat / guide-above-Street vs up day; univariate OLS with HC3 SE, bootstrap CI and Spearman for six surprise features at 1, 5, 20 sessions; multivariate OLS; logit for P(up day) | figs 17-19, tables 16-19 |
| `07_scenarios_montecarlo.R` | How wide is the valuation range and which driver matters | football field from the model's valuation summary; growth x margin x multiple heatmap from the 441-cell grid; net cash and share count backed out of the grid; 20,000-draw Monte Carlo with PERT distributions around bear / base / bull (13.5 / 16.5 / 18.5x exit EV/EBITDA) and a Gaussian copula (rho 0.5); tornado; model vs Street | figs 20-23, tables 20-22 |
| `08_event_study.R` | How the stock behaves around prints, and how much riskier a print session is | cumulative return paths -10 to +20 sessions for 23 prints with t and Wilcoxon tests; print-session vs ordinary-session dispersion (variance ratio, Levene, Mann-Whitney); rolling realised vol; price history | figs 24-27, tables 23-24 |

## Headline results (22 Sep 2026 run)

- **Operating leverage is real everywhere except marketing.** Cost elasticities to revenue (1Q22-2Q26): ops & support 0.53, G&A 0.49, cost of revenue 0.86, product development 0.87, total cash cost 0.90. Sales & marketing is 1.41 and SBC 1.37, both growing faster than revenue. The margin bridge shows S&M as the only line that has been a drag since 2024.
- **Seasonality dominates scale.** Quarter-of-year is significant for every KPI (ANOVA p < 1e-8; Kruskal-Wallis p < 0.003). Q3 carries about 32% of annual revenue; the STL seasonal factors are 0.90 / 1.00 / 1.24 / 0.88 for Q1-Q4.
- **Growth regimes.** supF rejects a constant mean for nights, revenue and ADR y/y. The BIC break for nights and revenue is after 4Q22 (nights y/y mean 32% before, 10.5% after); ADR's break is after 2Q25 (2.0% to 6.1%). Take-rate change shows no break.
- **Time-series forecasts sit on top of the driver model's base case.** For 3Q26 revenue: ETS $4,801M, ARIMA $4,772M, model base $4,801M, guide $4,690-4,770M, Street $4,740M. The statistical models are inside the guide-to-base gap, so the base case is not a stretch on the data alone. Backtest: a "repeat last y/y growth" rule (equivalently ARIMA (0,1,0)(0,1,0)) has one-quarter-ahead MAPE 3.4%; ETS 5.3%; seasonal naive 10.7%.
- **Guide-vs-Street is the reaction variable that matters, revenue surprise is not.** When the next-quarter guide midpoint is above Street the mean day-1 excess return is +2.3%; below, -5.2% (rank-sum p = 0.02). Revenue-beat vs up-day is not significant (Fisher p = 0.59). No feature is significant in a multivariate OLS with n = 19, and the day-1 move fades: mean 20-session excess return is -3.5%.
- **A print session is an 11x-variance event.** Mean absolute move 7.0% vs 2.0% on ordinary days (Levene p ~ 1e-33); 52% of prints moved more than 5%; 84% of the day-1 move happens in the overnight gap, so it is not tradeable after the open.
- **Valuation.** With the model's own driver ranges, the Monte Carlo median FY27E value is $176 (P5 $146, P95 $204), P(above $181.94 spot) = 37%, expected upside -4%. The exit multiple is the biggest swing ($151 to $201), then margin ($147 to $190), then growth ($167 to $194). Base case revenue is 0.9% above Street for FY26 and 0.7% above for FY27.

## Menu: analyses this data supports

Already built are the eight scripts above. The same frames support these next, without new data:

1. **Guide-forecasting model** (the pitch's actual question): regress the next-quarter revenue guide midpoint on the current quarter's nights growth, ADR, FX pp and prior guide cushion; score it point-in-time on W1 / W2 per the repo rules. Inputs are all in `earn` and `q`.
2. **Margin-guide cushion analysis**: management's "at least" margin floors vs actuals (FY guides sheet, 51 rows): distribution of the beat, trend in cushion, probability of a raise.
3. **Quantile regression of the day-1 move** on guide-vs-Street to describe tails, not the mean (n = 19 is thin but quantreg handles it).
4. **Regional nights panel**: fixed-effects regression of regional nights growth on regional ADR growth where both are disclosed (NA / EMEA have 8-13 quarters).
5. **Take-rate decomposition**: booking-to-stay timing (unearned fees y/y vs revenue y/y) as the explanation for take-rate seasonality; a lagged regression with unearned fees is a two-line addition.
6. **Buyback and share-count model**: shares ~ buybacks / price + SBC-driven issuance, to test the model's 575M FY27 share assumption against history.
7. **Reverse-DCF grid** already in `13_valuation_summary.csv`: plot implied FCF growth vs cost of equity.
8. **Bayesian shrinkage of the reaction regressions** (small n): the repo has pymc; in R, `brms` or `rstanarm` would give honest intervals on the guide-vs-Street slope.

Analyses that need data not yet in the workbooks:

- **Consensus at each call** (Bloomberg session, noted as missing in `model/assumptions.md`) would make the reaction study point-in-time and let the surprise regressions use morning-of-print consensus.
- **Options-implied moves** per print (`analysis/src/abnb_options_ledger.py` exists): implied vs realised move would say whether prints are systematically over- or under-priced.
- **QQQ daily closes** for a proper market-model event study (currently only 1 / 5 / 20-day QQQ returns exist, so the event paths are raw).
- **Inside Airbnb supply panel** (listings, same-listing prices) to regress ADR ex-FX on supply growth and mix.
- **Hotel RevPAR / STR data** for a hotel-vs-Airbnb ADR co-integration test.

## Folder layout

```
analysis/r_stats/
  ABNB_stats.Rproj          open this in RStudio
  run_all.R                 rebuilds everything and knits the report
  ABNB_stats_report.Rmd     the report source; ABNB_stats_report.html is the knitted output
  R/00_setup.R ... 08_event_study.R
  data/                     tidy CSVs and abnb_tidy.rds (generated)
  figures/                  27 PNGs, 150 dpi (generated)
  tables/                   24 tables as CSV and standalone HTML (generated)
```
