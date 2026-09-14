# 05b — The momentum and reversal object (object 4 of the quality-of-growth study)

- **Date:** 2026-09-11. **Author:** Opus build agent for Theo.
- **Question:** what happens to ABNB when KPI momentum reverses while estimates are still rising, and what is the base rate from ABNB's own prints?
- **Spec it serves:** `docs/superpowers/specs/2026-09-11-rnpl-quality-of-growth-study-design.md`, object 4 and pre-registered test 4.
- **Scope:** repo data only. No Bloomberg. Section 6 is the extraction that closes the object.
- **Code:** `analysis/src/rnpl_short_audit/qog_momentum_reversal.py`. **Data:** `data/processed/rnpl_short_audit/qog_momentum_*.csv` (8 files, section 8).
- **Read-only on every existing file.** Nothing tracked was modified.
- **Benchmark throughout: QQQ**, arithmetic excess (ABNB minus QQQ over identical dates). That is the repo's own convention (`09_stock_behaviour.py`, `20_executable_returns.py`). SPX is not in the repo's daily file as a total-return series; `SPY` is, and section 4 ranks against it.
- Every number below carries **measured / derived / assumed** and a path. Every consensus number carries **vendor and timestamp**. No withdrawn number is quoted (the option-implied event premium stays withdrawn, audit A08).

---

## 1. Bottom line

1. **The KPI-deceleration state is a real, one-sided pattern in the day-one close-to-close number, and it is almost entirely the overnight gap — which is not tradable.** On the 22 prints 1Q21–2Q26, prints where nights decelerated versus the prior quarter fell a mean **−4.07%** and a median **−3.86%** against QQQ on the day, **10 of 11 negative**; restricted to 2023+ it is **−5.94% mean, −7.09% median, 9 of 9 negative**, range −12.30% to −0.04%. *(derived; `qog_momentum_cells.csv`)*. Accelerating prints on the same measure: **+3.52% mean, 8 prints, 2 of 8 negative**.
2. **Enter at the first price you could actually get and the whole effect inverts.** Same deceleration prints, entering at the reaction-session open: **+1.77% mean, 10 of 11 positive**, range −0.26% to +4.11%. The deceleration is fully in the gap; the tape then grinds *up* through the session. This is the WS20/A02 finding restated on a new conditioning, and it is the single most important line in this note for anyone sizing a print trade *(derived; `qog_momentum_cells.csv`)*.
3. **The thesis state — nights decelerating while revenue beats — has n = 10 and a median that is negative at every horizon, but it is not separable from noise.** Day-one close-to-close **−4.09% mean / −4.96% median, 9 of 10 negative**; 20-session drift **−2.95% / −4.40%, 7 of 10 negative**, range −11.68% to +10.94%; 60-session drift **−4.21% / −4.20%, 7 of 10 negative**, range −28.32% to +11.12%. The 20-day mean is 1.5 standard errors from zero. **Quote it as a base rate with a story, never as a signal.**
4. **The guide-implied-deceleration cell adds nothing over the unconditional drift.** Prints where the next-quarter revenue guide implied a y/y step-down of more than 2 points: 20-day drift **−3.79% mean, −5.46% median, 8 of 12 negative** against an unconditional **−2.53% / −3.27%, 13 of 22 negative**. That is a 1.3-point spread on n = 12. Consistent with the red team's ruling; **no p-value is quoted for this family anywhere in this note.**
5. **The run-up carries no information, and I reproduce `09_runup_vs_reaction` exactly.** Prints after a positive 20-session run-up: day-one **+0.86%**, 20-day drift **−2.55%**; after a negative run-up: **−1.15%** and **−2.50%**. The two cells are indistinguishable.
6. **ABNB's momentum state today is as extreme as it gets inside this universe: rank 1 of 17 on 3, 6 and 12 months.** +36.2% / +35.8% / +47.0% price-only to 4 Sep 2026, against QQQ +2.1% / +18.6% / +25.4% and MTUM −0.4% / +23.6% / +25.7% *(derived; `qog_momentum_state_today.csv`)*. The 7 Aug print did roughly a third of the 12-month move in one session.
7. **One data defect found in the repo** (section 3.3): `09_prices_daily.csv` carries an all-NaN row for **25 May 2026**, a US market holiday. It shifts workstream 09's event-time clock by one session for the only print whose +20/+60 windows span it, 2026Q1. Everything else in WS09's drift file reproduces to 1e-13.

---

## 2. The print panel

`data/processed/rnpl_short_audit/qog_momentum_print_panel.csv` — 23 rows (4Q20 print carried for reconciliation; **22 rows are in the requested 1Q21–2Q26 window**, flagged by `in_requested_window`).

### 2.1 Reaction and drift, per print

All figures percent, QQQ-excess. `gap` = pre-release close → reaction open. `intraday` = reaction open → reaction close, and is identical to the executable day-one number. `drift` windows start at the reaction close and **exclude** day one. *(derived from `data/processed/overnight/20_prices_ohlc.csv`, measured prices)*

| print | reaction date | raw d1 | excess d1 | gap | intraday = executable d1 | drift +5 | drift +20 | drift +60 | exec 20d from open | run-up −20 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2020Q4 | 2021-02-26 | 13.34 | 12.92 | 5.69 | 6.81 | −11.12 | −16.08 | −39.98 | −7.85 | −7.47 |
| 2021Q1 | 2021-05-14 | 4.01 | 1.81 | 0.40 | 1.38 | −4.79 | 0.12 | −7.61 | 2.04 | −16.06 |
| 2021Q2 | 2021-08-13 | 1.07 | 0.71 | −3.07 | 3.91 | −5.64 | 2.91 | 23.21 | 10.28 | 7.98 |
| 2021Q3 | 2021-11-05 | 12.98 | 12.89 | 3.86 | 8.67 | 3.42 | −7.19 | −17.18 | −6.19 | −4.49 |
| 2021Q4 | 2022-02-16 | 3.65 | 3.67 | −0.34 | 4.05 | −10.84 | −12.33 | −19.73 | −8.83 | 20.30 |
| 2022Q1 | 2022-05-04 | 7.71 | 4.33 | 5.05 | −0.84 | −14.17 | −17.74 | −24.45 | −19.32 | −4.42 |
| 2022Q2 | 2022-08-03 | −1.13 | −3.86 | −7.52 | 4.11 | 2.28 | 5.66 | 12.92 | 8.76 | 11.73 |
| 2022Q3 | 2022-11-02 | −13.43 | −10.00 | −5.86 | −4.61 | 2.35 | −3.29 | 6.80 | −7.14 | 0.90 |
| 2022Q4 | 2023-02-15 | 13.35 | 12.59 | 8.16 | 4.01 | −4.41 | −11.68 | −28.32 | −10.67 | 10.40 |
| 2023Q1 | 2023-05-10 | −10.92 | −12.01 | −14.32 | 2.73 | −6.13 | −6.57 | 11.12 | −1.52 | 9.38 |
| 2023Q2 | 2023-08-04 | −0.50 | −0.04 | −0.82 | 0.77 | −3.07 | −6.83 | −10.43 | −6.95 | 8.20 |
| 2023Q3 | 2023-11-02 | −3.32 | −5.14 | 1.26 | −6.25 | −1.81 | 9.61 | 10.07 | −4.42 | −5.46 |
| 2023Q4 | 2024-02-14 | −1.74 | −2.83 | −3.72 | 0.94 | 3.64 | 10.94 | −3.31 | 10.64 | 7.06 |
| 2024Q1 | 2024-05-09 | −6.87 | −7.09 | −7.22 | 0.15 | −2.39 | −5.24 | −10.94 | −4.96 | −1.87 |
| 2024Q2 | 2024-08-07 | −13.38 | −12.30 | −15.40 | 3.13 | −3.57 | −3.25 | 7.98 | −0.70 | −2.72 |
| 2024Q3 | 2024-11-08 | −8.66 | −8.78 | −8.52 | −0.26 | 1.85 | 0.37 | −1.43 | −0.95 | 6.71 |
| 2024Q4 | 2025-02-14 | 14.45 | 14.03 | 12.14 | 1.65 | −6.89 | −11.07 | −10.29 | −11.82 | 2.71 |
| 2025Q1 | 2025-05-02 | 1.01 | −0.48 | −3.36 | 2.96 | 1.60 | −3.55 | −8.62 | −0.17 | −0.18 |
| 2025Q2 | 2025-08-07 | −8.02 | −8.36 | −8.52 | 0.13 | 1.97 | 1.95 | −5.09 | 3.52 | −6.63 |
| 2025Q3 | 2025-11-07 | 0.29 | 0.61 | 4.67 | −3.91 | 1.09 | −1.45 | 2.41 | −3.76 | 0.16 |
| 2025Q4 | 2026-02-13 | 4.65 | 4.44 | 9.09 | −4.29 | 1.41 | 6.00 | −5.85 | 0.99 | −9.62 |
| 2026Q1 | 2026-05-08 | 0.73 | −1.61 | −2.38 | 0.82 | −5.78 | −5.67 | 6.92 | −4.05 | −5.14 |
| 2026Q2 | 2026-08-07 | 17.43 | 16.26 | 7.84 | 7.72 | 2.25 | 2.74 | — | 12.82 | 4.43 |

Day-one decomposition over the 22 in-window prints *(derived)*: mean |raw| **6.79%**, median |raw| **5.76%** (on all 23 prints: mean **7.07%**, median **6.87%**, 10 moves of 8% or more — WS09's base rate, reproduced), mean |gap| **5.91%**, mean |executable day-one| **3.06%**, median gap share of |move| **98.1%**. Over all 23 prints, `var(gap excess) / var(day-one excess) = 0.730` and `corr = 0.890` — **the repo's 73% / 0.89 pair reproduces exactly** (`research/notes/overnight/20_temporal-validation.md` §1).

### 2.2 KPI and consensus state at each print

*(nights/GBV/revenue/FCF measured from `02_kpi_panel_quarterly.csv`; surprises measured against the vendor-stamped consensus in `04_reaction_panel.csv`; guide-implied y/y derived)*

| print | nights y/y | accel vs prior q | accel vs prior yr | GBV y/y | rev y/y | rev surprise | cons vendor | guide vs Street | guide-implied next-q rev y/y | implied decel | FCF margin | FCF margin Δy/y | PT net 60d pre | est. direction (proxy) |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|
| 2020Q4 | — | — | — | — | — | 16.13 | Yahoo/unattrib. | — | — | — | — | — | +1 | rising |
| 2021Q1 | — | — | — | — | — | 24.16 | Refinitiv | — | — | — | 67.5 | — | 0 | flat/none |
| 2021Q2 | — | — | — | — | — | 5.95 | Refinitiv | — | — | — | 58.6 | — | 0 | flat/none |
| 2021Q3 | 28.96 | — | — | 48.21 | 66.65 | 9.12 | Refinitiv | — | 67.04 | +0.39 | 23.7 | — | +2 | rising |
| 2021Q4 | 58.53 | +29.57 | — | 91.34 | 78.33 | 4.93 | Refinitiv | +16.53 | 62.91 | −15.42 | 24.7 | — | −2 | falling |
| 2022Q1 | 58.54 | +0.01 | — | 66.99 | 70.12 | 4.07 | Refinitiv | +6.12 | 55.81 | −14.31 | 79.3 | +11.8 | −1 | falling |
| 2022Q2 | 24.79 | −33.75 | — | 26.87 | 57.60 | −0.28 | Refinitiv | +2.17 | 26.51 | −31.09 | 37.8 | −20.8 | −10 | falling |
| 2022Q3 | 25.09 | +0.30 | −3.87 | 31.09 | 28.92 | 3.00 | Refinitiv | −0.54 | 20.10 | −8.82 | 33.2 | +9.5 | −3 | falling |
| 2022Q4 | 20.16 | −4.93 | −38.37 | 19.47 | 24.15 | 2.26 | Refinitiv | +5.62 | 18.29 | −5.86 | 23.9 | −0.8 | 0 | flat/none |
| 2023Q1 | 18.61 | −1.55 | −39.93 | 18.60 | 20.48 | 1.56 | Refinitiv | −0.83 | 14.07 | −6.41 | 87.0 | +7.7 | +2 | rising |
| 2023Q2 | 10.99 | −7.62 | −13.80 | 12.35 | 18.06 | 2.64 | Refinitiv | +4.04 | 16.16 | −1.90 | 36.2 | −1.6 | +7 | rising |
| 2023Q3 | 13.54 | +2.55 | −11.55 | 17.31 | 17.79 | 0.80 | LSEG | −1.38 | 13.04 | −4.75 | 38.6 | +5.4 | 0 | flat/none |
| 2023Q4 | 12.02 | −1.52 | −8.14 | 14.81 | 16.61 | 2.21 | LSEG | +0.98 | 12.76 | −3.85 | 2.1 | −21.8 | +6 | rising |
| 2024Q1 | 9.50 | −2.52 | −9.11 | 12.25 | 17.82 | 3.98 | LSEG | −1.10 | 9.10 | −8.72 | 89.1 | +2.1 | +7 | rising |
| 2024Q2 | 8.69 | −0.81 | −2.30 | 10.99 | 10.63 | 0.29 | LSEG | — | 8.92 | −1.71 | 38.0 | +1.8 | +2 | rising |
| 2024Q3 | 8.48 | −0.21 | −5.06 | 9.84 | 9.86 | 0.32 | LSEG | −0.21 | 8.88 | −0.98 | 28.8 | −9.8 | +2 | rising |
| 2024Q4 | 12.35 | +3.87 | +0.33 | 13.55 | 11.81 | 2.48 | LSEG | −2.17 | 5.04 | −6.77 | 18.5 | +16.4 | +2 | rising |
| 2025Q1 | 7.92 | −4.43 | −1.58 | 6.99 | 6.07 | 0.53 | LSEG | −0.66 | 9.90 | +3.83 | 78.4 | −10.7 | −8 | falling |
| 2025Q2 | 7.43 | −0.48 | −1.26 | 10.85 | 12.66 | 1.84 | LSEG | +0.25 | 8.79 | −3.87 | 31.1 | −6.9 | +8 | rising |
| 2025Q3 | 8.79 | +1.36 | +0.31 | 13.93 | 9.73 | 0.37 | LSEG | +0.75 | 8.47 | −1.26 | 32.9 | +4.1 | −1 | falling |
| 2025Q4 | 9.82 | +1.03 | −2.53 | 15.91 | 12.02 | 2.13 | LSEG | +3.16 | 14.88 | +2.86 | 18.8 | +0.3 | +6 | rising |
| 2026Q1 | 9.15 | −0.67 | +1.23 | 19.18 | 17.87 | 2.21 | LSEG | +3.18 | 15.31 | −2.56 | 63.6 | −14.8 | +3 | rising |
| 2026Q2 | 10.34 | +1.19 | +2.91 | 15.74 | 16.54 | 0.78 | LSEG | +2.60 | 15.51 | −1.03 | 34.7 | +3.6 | +5 | rising |

**Estimate direction into the print is a proxy, not the estimate series.** The repo carries **no point-in-time consensus vintage history**; `20_vintage_register.csv` says the consensus is reconstructible only *at* the print, from the print-day article, for 21 of 23 prints. The column above is the net count of sell-side price-target raises minus cuts in the 60 calendar days before the print, from `09_analyst_actions.csv` (yfinance/Benzinga feed, pulled 2026-09-06, 466 actions) — **derived, proxy**. The panel carries `point_in_time_consensus_revision_direction = "MISSING - needs Bloomberg BEst"` on every row. Workstream 09 also establishes that sell-side actions *follow* the stock (price-target raises show −0.2% same-day CAR once print weeks are dropped), so this proxy is at best coincident.

**The nights-accel column is distorted before 2023** by the COVID rebound (+29.57 pts in 2021Q4, −33.75 in 2022Q2). Every cell in section 3 is therefore also reported on a 2023+ subsample.

---

## 3. Conditional reaction and drift

`data/processed/rnpl_short_audit/qog_momentum_cells.csv` (91 rows, 7 return metrics × 13 cells) and `qog_momentum_cell_members.csv` (141 rows, every print in every cell). Sample: the 22 prints 1Q21–2Q26.

### 3.1 The headline cells

| cell | n | day-1 excess mean / median / % neg / range | executable day-1 mean / median / % neg / range | +20 drift mean / median / % neg / range | +60 drift mean / median / % neg / range |
|---|---:|---|---|---|---|
| all prints | 22 | −0.05 / −0.26 / 55% / −12.30 to 16.26 | +1.23 / +1.16 / 27% / −6.25 to 8.67 | −2.53 / −3.27 / 59% / −17.74 to 10.94 | −3.42 / −5.09 / 62% / −28.32 to 23.21 |
| **(a) nights accelerating** | 8 | **+3.52 / +4.00 / 25%** / −10.00 to 16.26 | −0.81 / −2.38 / 63% / −6.25 to 7.72 | −3.44 / −2.37 / 63% / −17.74 to 9.61 | −5.86 / −5.85 / 57% / −24.45 to 10.07 |
| **(a) nights decelerating** | 11 | **−4.07 / −3.86 / 91%** / −12.30 to 12.59 | **+1.77 / +0.94 / 9%** / −0.26 to 4.11 | −2.17 / −3.55 / 64% / −11.68 to 10.94 | −2.65 / −3.31 / 64% / −28.32 to 12.92 |
| (a) accelerating, 2023+ | 5 | +6.04 / +4.44 / 20% / −5.14 to 16.26 | −1.02 / −3.91 / 60% / −6.25 to 7.72 | +1.17 / +2.74 / 40% / −11.07 to 9.61 | −0.92 / −1.72 / 50% / −10.29 to 10.07 |
| (a) decelerating, 2023+ | 9 | **−5.94 / −7.09 / 100%** / −12.30 to −0.04 | +1.26 / +0.82 / 11% / −0.26 to 3.13 | −1.98 / −3.55 / 67% / −6.83 to 10.94 | −1.53 / −3.31 / 67% / −10.94 to 11.12 |
| **(b) nights decel + revenue beat** | **10** | **−4.09 / −4.96 / 90%** / −12.30 to 12.59 | **+1.54 / +0.88 / 10%** / −0.26 to 4.01 | **−2.95 / −4.40 / 70%** / −11.68 to 10.94 | **−4.21 / −4.20 / 70%** / −28.32 to 11.12 |
| (b′) (b) + PT revisions rising | 8 | −6.63 / −7.73 / 100% / −12.30 to −0.04 | +1.05 / +0.80 / 13% / −0.26 to 3.13 | −1.79 / −4.25 / 63% / −6.83 to 10.94 | −0.65 / −2.37 / 63% / −10.94 to 11.12 |
| (c) guide implied deceleration | 17 | −1.21 / −2.83 / 65% / −12.30 to 16.26 | +0.84 / +0.82 / 29% / −6.25 to 7.72 | −3.17 / −3.29 / 65% / −17.74 to 10.94 | −3.49 / −2.37 / 56% / −28.32 to 12.92 |
| (c′) implied decel > 2 pts | 12 | −1.36 / −3.34 / 67% / −12.01 to 14.03 | +0.58 / +0.88 / 25% / −6.25 to 4.11 | −3.79 / −5.46 / 67% / −17.74 to 10.94 | −4.52 / −4.20 / 58% / −28.32 to 12.92 |
| (d) after a positive run-up | 12 | +0.86 / +0.29 / 50% / −12.01 to 16.26 | +1.76 / +2.19 / 25% / −4.61 to 7.72 | −2.55 / −2.37 / 58% / −12.33 to 10.94 | −1.55 / −1.43 / 55% / −28.32 to 23.21 |
| (d) after a negative run-up | 10 | −1.15 / −1.04 / 60% / −12.30 to 12.89 | +0.59 / +0.49 / 30% / −6.25 to 8.67 | −2.50 / −3.40 / 60% / −17.74 to 9.61 | −5.48 / −6.73 / 70% / −24.45 to 10.07 |
| (d′) top-third run-up | 8 | −1.32 / −1.43 / 63% / −12.01 to 12.59 | +2.53 / +3.32 / 13% / −0.26 to 4.11 | −2.19 / −3.10 / 50% / −12.33 to 10.94 | −2.00 / −2.37 / 63% / −28.32 to 23.21 |
| (e) decel + beat + guide decel | 9 | −4.49 / −7.09 / 89% / −12.30 to 12.59 | +1.38 / +0.82 / 11% / −0.26 to 4.01 | −2.89 / −5.24 / 67% / −11.68 to 10.94 | −3.72 / −3.31 / 67% / −28.32 to 11.12 |

Definitions. (a) `nights_yoy_accel_pts` sign, from `02_kpi_panel_quarterly.csv`. (b) accel < 0 **and** `revenue_surprise_pct` > 0. (b′) adds net price-target raises > 0 in the 60 days before the print — the proxy, not the estimate series. (c) guide-implied next-quarter revenue y/y below the just-reported revenue y/y; (c′) below it by more than 2 points. (d) sign of the recomputed 20-session excess run-up. (e) all of (a-decel), (b) and (c).

### 3.2 The (b) cell print by print — the thesis analogue

This is the cell the 5 November and February tests will be scored against. **n = 10. Read the prints, not the mean.** *(derived; `qog_momentum_cell_members.csv`)*

| print | reaction | nights y/y | accel pts | rev surprise | guide vs Street | guide-implied decel | est. dir. (proxy) | raw d1 | excess d1 | executable d1 | +20 drift | +60 drift |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 2022Q4 | 2023-02-15 | 20.16 | −4.93 | +2.26 | +5.62 | −5.86 | flat/none | +13.35 | +12.59 | +4.01 | −11.68 | **−28.32** |
| 2023Q1 | 2023-05-10 | 18.61 | −1.55 | +1.56 | −0.83 | −6.41 | rising | −10.92 | −12.01 | +2.73 | −6.57 | +11.12 |
| 2023Q2 | 2023-08-04 | 10.99 | −7.62 | +2.65 | +4.04 | −1.90 | rising | −0.50 | −0.04 | +0.77 | −6.83 | −10.43 |
| 2023Q4 | 2024-02-14 | 12.02 | −1.52 | +2.21 | +0.98 | −3.85 | rising | −1.74 | −2.83 | +0.94 | **+10.94** | −3.31 |
| 2024Q1 | 2024-05-09 | 9.50 | −2.52 | +3.98 | −1.10 | −8.72 | rising | −6.87 | −7.09 | +0.15 | −5.24 | −10.94 |
| 2024Q2 | 2024-08-07 | 8.69 | −0.81 | +0.29 | — | −1.71 | rising | −13.38 | −12.30 | +3.13 | −3.25 | +7.98 |
| 2024Q3 | 2024-11-08 | 8.48 | −0.21 | +0.32 | −0.21 | −0.98 | rising | −8.66 | −8.78 | −0.26 | +0.37 | −1.43 |
| 2025Q1 | 2025-05-02 | 7.92 | −4.43 | +0.53 | −0.66 | +3.83 | falling | +1.01 | −0.48 | +2.96 | −3.55 | −8.62 |
| 2025Q2 | 2025-08-07 | 7.43 | −0.48 | +1.84 | +0.25 | −3.87 | rising | −8.02 | −8.36 | +0.13 | +1.95 | −5.09 |
| 2026Q1 | 2026-05-08 | 9.15 | −0.67 | +2.21 | +3.18 | −2.56 | rising | +0.73 | −1.61 | +0.82 | −5.67 | +6.92 |

Read it this way. **Nine of ten fell on the day and nine of ten rose from the open.** The two that did not fall on the day (2022Q4 +12.59%, 2025Q1 −0.48%) are the two where the guide was the story rather than the KPI — 2022Q4 carried a +5.62% guide-above-Street, 2025Q1 the only guide-implied *acceleration* in the cell. **Two of ten gave a positive 20-day drift and three of ten a positive 60-day drift**, so a short held through the drift window loses roughly a quarter to a third of the time, and the single worst outcome for a short was 2023Q4's **+10.94%** over 20 sessions. The single best was 2022Q4's **−28.32%** over 60 sessions, which is also the print with the biggest up-day — consistent with WS09's "pops fade" result and with the fact that 2023's first half re-rated the whole sector.

### 3.3 What is and is not distinguishable from noise

- **Not distinguishable.** Every 20-day and 60-day drift cell. The largest, (c′) at −3.79% over 20 sessions, sits 1.4 standard errors from zero on n = 12; the (b) cell's −2.95% sits 1.5 standard errors out on n = 10. Cross-sectional dispersion inside each cell is 6–14 points. Also not distinguishable: every run-up cell at every horizon, in agreement with `09_runup_vs_reaction.csv` (run-up vs day-one r = −0.004, run-up vs 20-day drift r = −0.11 — both reproduced here to 3e-5).
- **Distinguishable as a sign, not as a magnitude.** The day-one close-to-close deceleration result: **9 of 9 negative since 2023**, mean −5.94% at 3.7 standard errors. But it is a close-to-close number whose median gap share is 98%, so what is being measured is the overnight repricing, not a tradable return. And it is one of thirteen post-hoc cells cut on the same 22 prints; WS09 already logged 218 tests on this price history, of which only eight cleared Bonferroni and all eight were discounted.
- **A genuine asymmetry worth carrying.** The *executable* day-one number in the deceleration cell is positive in 10 of 11 cases with a standard deviation of only 1.63 points. The tight dispersion is the interesting part: once the gap has happened, deceleration prints do not keep falling intraday. **A short entered at the open into a KPI-deceleration print has lost money on the day 10 times out of 11.**
- **No p-value is quoted for the guide-below-Street → drift family.** Three incompatible values are in circulation (RED_TEAM §7 kill list). The (c)/(c′) cells above are a different cut of the same family and inherit the ruling.
- **What this object cannot identify at all.** Whether estimates were actually rising into any historical print — there is no point-in-time consensus history in the repo. That is the single gap that makes pre-registered test 4 unscoreable on history today, and it is line 1 of the Bloomberg ask.

### 3.4 Reproduction of the repo's existing numbers, and one discrepancy

`data/processed/rnpl_short_audit/qog_momentum_reconciliation.csv`.

| check | n | max abs diff | verdict |
|---|---:|---:|---|
| day-one excess vs `20_executable_returns.legacy_1d_pct` | 23 | 0.0 | exact |
| gap excess vs `20_executable_returns.gap_excess_pct` | 23 | 0.0 | exact |
| executable 5d / 20d vs `20_executable_returns.open_5d_pct` / `open_20d_pct` | 23 | 0.0 | exact |
| day-one excess vs `04_reaction_panel.excess_1d_pct` | 23 | 0.043 pp | exact; 04 stores it rounded to 0.1 pp |
| run-up 20d vs `09_earnings_drift_by_print` | 23 | 3.4e-5 | exact |
| day-one / +20 / +60 vs `09_earnings_drift_by_print`, naively compared | 23 | 2.5 / 4.3 / 8.9 pp | **convention difference, not an error** — see below |
| WS09 replication on WS09's own convention: day-one, +5 | 23 | 0.0 | exact |
| WS09 replication: +20, +60 | 23 / 22 | 2.87 / 1.28 pp | exact on 22 of 23; **2026Q1 differs** |

**The convention difference.** Workstream 09 does not use holding-period excess returns. It builds an event-time path anchored 21 sessions before the reaction day as `path_t = cumprod(1+r_ABNB) − cumprod(1+r_QQQ)` on the *adjusted* closes in `09_prices_daily.csv`, and reports `drift_h = path[+h] − path[0]`. That is a legitimate but different object, and it runs 1–9 points larger in absolute value at long horizons. Implementing WS09's definition reproduces its file exactly. **This note's primary numbers stay on the holding-period convention**, because that is what `20_executable_returns.csv` uses and what a trader's P&L is.

**The discrepancy.** `09_prices_daily.csv` carries an all-NaN row for **25 May 2026 — Memorial Day, a US market holiday**. `20_prices_ohlc.csv` correctly omits it. 2026Q1 is the only print whose +20 and +60 windows span that date, so it is the only print whose WS09 event-time clock is shifted by one session. `09_earnings_drift_by_print.csv` gives 2026Q1 drift_20d = **−6.26%**; on a clean session index it is **−3.39%** on WS09's own convention and **−5.67%** on the holding-period convention. One print in 23 does not move WS09's published aggregates materially, but **the 2026Q1 row should not be quoted on its own from that file.** Reported here, not fixed: this note is read-only on existing files.

One further convention note: `20_prices_ohlc.csv` QQQ is unadjusted, so QQQ's dividend (~0.4%/yr) is not in the benchmark. That understates QQQ by roughly 0.03 points over a 20-session window and 0.1 over 60 — immaterial at the precision quoted, and it biases *against* the short.

---

## 4. The momentum state today

`data/processed/rnpl_short_audit/qog_momentum_state_today.csv`, as of **4 September 2026**, the last session in the repo's price files. **Price-only. ABNB pays no dividend and has not split, so for ABNB price return is total return** (`20_vintage_register.csv` row 12, measured). The comparators are yfinance adjusted closes from `09_prices_daily.csv`, so *their* dividends are in — the comparison is if anything conservative for ABNB.

| horizon | window start | ABNB | QQQ | SPY | MTUM | ABNB − QQQ | ABNB − MTUM | ABNB rank |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 3 months (63 sessions) | 2026-06-05 | **+36.24%** | +2.08% | +4.69% | −0.42% | +34.16 pp | +36.66 pp | **1 of 17** |
| 6 months (126) | 2026-03-09 | **+35.75%** | +18.58% | +14.16% | +23.55% | +17.17 pp | +12.19 pp | **1 of 17** |
| 12 months (252) | 2025-09-05 | **+46.95%** | +25.41% | +20.31% | +25.68% | +21.54 pp | +21.28 pp | **1 of 17** |

Universe: ABNB, BKNG, DASH, EXPE, H, HLT, IVE, IVW, IWM, JETS, MAR, MTUM, QQQ, SPY, TRIP, UBER, XLY. ABNB is first on all three horizons. The nearest travel comparables at 12 months are EXPE +39.7% and MAR +28.2%; BKNG is **−11.6%**.

**The 7 August 2026 print and what has happened since** (`qog_momentum_since_2026q2_print.csv`, derived from measured prices):

| item | value |
|---|---|
| pre-print close, 6 Aug 2026 | $151.64 |
| reaction-session open, 7 Aug | $164.70 — gap **+8.61%** |
| reaction-session close, 7 Aug | $178.07 — intraday **+8.12%** |
| day-one raw close-to-close | **+17.43%** |
| day-one QQQ-excess | **+16.26%** |
| gap share of the day-one move | **49.4%** — against a 98% median across the 22 prints |
| high close since | $190.50 on 25 Aug 2026 |
| close, 4 Sep 2026 | $181.94 |
| 20 sessions since the reaction day, raw | **+2.17%**; QQQ-excess **+2.74%** |
| drawdown from the 25 Aug high | −4.49% |
| short interest, 14 Aug 2026 settlement | **2.17% of shares out** — near the low end of the 1.74–5.44% range since Feb 2023 |

Three things follow. **First, 7 August was the unusual print where half the move was earned in the session** — most ABNB prints are 90–100% gap. **Second, the fade has not happened**: +2.7% excess over the 20 sessions after the reaction day, against WS09's −7.1% base rate for up-prints and its own observation that the fade has broken since mid-2025 (Q3'25 −1.4%, Q4'25 +5.5%, Q2'26 +3.2% — reproduced here as −1.45%, +6.00%, +2.74% on the holding-period convention). **Third, positioning is not crowded short**, so there is no squeeze fuel and no cheap borrow story; the short case has to be paid for by the fundamentals, not by positioning.

**Calendar.** The Q3 2026 print is dated **5 November 2026** (`20_frozen_q3_2026.csv`, third-party estimate, frozen 6 Sep 2026). **The Citadel finals are 22–24 October. The print lands after them.** So the 5 November test is a scoring event for the thesis, not a catalyst the pitch can own; the pitch must be underwritten to the February (1Q27 guide) print, which is where the audit's note 03 already put the trade. The option-implied event premium for 5 November **is not identified** today — the specifications span non-positive to 13.0% event sigma (`23_options_event_estimates.csv`, run 6 Sep 2026) — so **no implied move may be quoted**; the historical base rate is the usable number: **mean |day-one| 7.07%, median 6.87%, and 10 of 23 prints moved 8% or more** — reproducing WS09's 7.1% / 6.9% / 10-of-23 exactly (6.79% mean on the 22 prints in the requested window).

---

## 5. What this object can and cannot identify

**Can identify.**
- The sign asymmetry in day-one close-to-close returns between accelerating and decelerating KPI prints, and its concentration in the overnight gap.
- The fact that the executable day-one return in deceleration prints is positive, small and tight — a genuine, useful constraint on how to structure any print trade.
- A 20/60-day drift base rate in the thesis state, with its full dispersion and every member named.
- The current momentum state and its cross-sectional rank, exactly.
- Whether the repo's own event-study numbers reproduce. They do, and one data defect surfaced in the process.

**Cannot identify.**
- **Whether estimates were rising into any historical print.** No point-in-time consensus history exists in the repo. Every "estimates still rising" statement in this note is a price-target proxy.
- Whether the day-one direction is forecastable. It is not — settled, WS20.
- Whether the drift is real or sampling noise at n = 10. 1.5 standard errors on ten overlapping-regime observations does not settle it, and no amount of re-cutting these 22 prints will.
- Anything about ABNB's momentum-factor *exposure* beyond WS09's Ken-French estimate (β_MOM −0.37 full sample, −0.77 in 2026). There is no index-level or holdings-level check in the repo, and whether ABNB is currently held by a momentum index — which would make a KPI reversal a mechanical flow event — is unknown.
- Whether the pattern is ABNB-specific or an OTA-complex fact. n = 22 on one name cannot separate them; BKNG/EXPE prints are the cheapest way to triple the sample.

---

## 6. The Bloomberg extraction that closes this object

`data/processed/rnpl_short_audit/qog_momentum_bloomberg_spec.csv` (18 rows, machine-readable). Every mnemonic I am not certain of is flagged **verify in FLDS**; do not silently substitute a similar-looking field.

| # | Field or function | Ticker(s) | Frequency | Date range | Purpose | Test it feeds | Mnemonic |
|---|---|---|---|---|---|---|---|
| 1 | `BDH(BEST_SALES)` with `BEST_FPERIOD_OVERRIDE` = 1BF…8BF and FY1…FY3 | ABNB US Equity | daily (weekly acceptable) | 1 Jan 2021 → live | point-in-time revenue consensus by fiscal period — the true "estimates still rising" series | cell (b′); perception test 3; momentum test 4 | `BEST_SALES` ok; **period-override syntax: verify in FLDS** |
| 2 | `BDH(BEST_EBITDA)` + period override | ABNB US Equity | daily | 1 Jan 2021 → live | point-in-time adj. EBITDA consensus | the exit-multiple rule; object 3 | `BEST_EBITDA` ok |
| 3 | `BDH(BEST_EPS)` + period override | ABNB US Equity | daily | 1 Jan 2021 → live | point-in-time EPS consensus and surprise | print panel surprise columns | `BEST_EPS` ok |
| 4 | FCF consensus (`BEST_CAPEX`, `BEST_CASH_FLOW_PER_SH`, or the FCF line in EEO) | ABNB US Equity | daily | 1 Jan 2021 → live | did FCF estimates move with KPI estimates | **perception test 3** — FY27 FCF vs FY27 revenue revisions since 6 Aug 2026 | **verify in FLDS**; ABNB FCF consensus coverage is not guaranteed |
| 5 | KPI consensus for **GBV** and **Nights and Seats Booked** (ANR/EEO KPI tab, or the Visible Alpha add-in) | ABNB US Equity | quarterly | 1Q21 → live | the repo has a nights consensus for only 19 of 23 prints and none for 3Q26 | print-panel nights surprise; the 5 Nov wedge test | **verify in FLDS**; if Bloomberg does not carry it, say so — Zacks publishes nights/ADR/GBV 2–3 days pre-print as the fallback |
| 6 | Revision **breadth**: number of estimates up vs down, 30/60 days | ABNB US Equity | daily | 1 Jan 2021 → live | replaces the price-target proxy in the panel's estimate-direction column | the conditioning that makes momentum test 4 scoreable on history | **verify in FLDS** |
| 7 | Estimate **dispersion**: `BEST_ESTIMATE_STD_DEV`, or `BEST_SALES_HI` / `_LO` / `_NUMEST` | ABNB US Equity | daily | 1 Jan 2021 → live | dispersion is the state variable for reaction magnitude | reaction-magnitude conditioning; the 5 Nov card | **verify in FLDS** |
| 8 | `BEST_TARGET_PRICE`, `BEST_TARGET_PRICE_MEDIAN`, ANR rating history | ABNB US Equity | daily | 1 Jan 2021 → live | point-in-time targets and ratings; the repo has only a live snapshot plus a Benzinga feed | "the Street is behind the stock"; the sell-side-capitulation flip rule | `BEST_TARGET_PRICE` ok |
| 9 | `SHORT_INT`, `SI_PERCENT_EQUITY_FLOAT`, days to cover | ABNB US Equity | semi-monthly | 1 Jan 2021 → live | positioning into each print and into 5 Nov; squeeze risk | sizing discipline; section 4 state | `SHORT_INT` ok; **days-to-cover mnemonic: verify in FLDS** |
| 10 | 30-day and 3-month ATM implied vol (`30DAY_IMPVOL_100.0%MNY_DF`, `3MTH_IMPVOL_100.0%MNY_DF`) | ABNB US Equity | daily | 1 Jan 2021 → live | what was priced into each print vs the 6.8–7.1% realised base rate | replaces the withdrawn event-premium estimate (A08); 5 Nov trade structure | **verify in FLDS** — the `MNY_DF` family is version-dependent |
| 11 | Skew: 30-day 90% minus 110% moneyness implied vol | ABNB US Equity | daily | 1 Jan 2021 → live | is the downside already paid for | the bear-leg cost in the return path | **verify in FLDS** |
| 12 | `TOT_RETURN_INDEX_GROSS_DVDS` | ABNB, QQQ, SPY US Equity; NDX Index; SPX Index | daily | 10 Dec 2020 → live | true total return; the repo's momentum is price-only | section 4 restated on total return | `TOT_RETURN_INDEX_GROSS_DVDS` ok |
| 13 | `TOT_RETURN_INDEX_GROSS_DVDS` on momentum index proxies | S&P 500 Momentum; MSCI USA Momentum; MTUM US Equity | daily | 1 Jan 2021 → live | a tradable-index cross-check on WS09's β_MOM = −0.77 (2026) | section 4; the momentum-unwind branch of the bear case | **verify in FLDS** — the two index tickers are the most likely thing in this table to be wrong |
| 14 | Earnings history + announcement timestamps (ERN screen; surprise fields) | ABNB US Equity | quarterly | 1Q21 → live | vendor-stamped surprise history and the exact release time, so the executable convention can be audited | print panel; reconciles the 23-print hand-built consensus | ERN ok; **surprise mnemonic: verify in FLDS** |
| 15 | Peer read-across: rows 1–3 and 14 repeated | BKNG, EXPE (MAR, HLT optional) | quarterly / daily | 1 Jan 2021 → live | does "KPI decel + estimate beat" hurt the complex or only ABNB? | **the only route to an n big enough to separate cell (b) from noise** | none |
| 16 | Factor-exposure history (PORT → Factor Exposure, exported) | ABNB vs a momentum-factor model | monthly | 1 Jan 2021 → live | Bloomberg's own momentum loading, corroborating Ken French | section 4; the momentum-unwind branch | **verify in FLDS**; a manual export is acceptable if BDH cannot reach it |
| 17 | Momentum-index membership and weight (MEMB on the index) | S&P 500 Momentum; MSCI USA Momentum | at each rebalance | 1 Jan 2021 → live | is ABNB *in* a momentum index? If so a KPI reversal creates a mechanical seller at the next rebalance | the flow leg of the bear case | **verify in FLDS**; rebalance dates matter more than field names |
| 18 | Company guidance history (GUID screen) | ABNB US Equity | quarterly | 1Q21 → live | vendor cross-check on the repo's 194-row hand-built guidance ledger | the guide-vs-Street column | GUID ok; **BDH guidance mnemonics: verify in FLDS** |

**Priority if the terminal time is short: rows 1, 4, 6, 15.** Row 1 makes pre-registered test 4 scoreable at all; row 4 is object 3's whole question; row 6 replaces the weakest column in the print panel; row 15 is the only way n stops being the binding constraint.

---

## 7. The return-path skeleton

`data/processed/rnpl_short_audit/qog_momentum_return_path.csv`. **Bear / base / bull describe the stock**, so a short pays in the bear column. **Blank cells are blank on purpose** — the note next to each says exactly what fills it. The multiple rule is applied **once**, to one line, and to revenue growth only.

| line | tag | source | bear | base | bull | unit |
|---|---|---|---:|---:|---:|---|
| **A.** ABNB close, 4 Sep 2026 | measured | `20_prices_ohlc.csv` | 181.94 | 181.94 | 181.94 | usd |
| **B.** 4Q26 nights y/y, RNPL module | derived | `rnpl_nights_module.csv` | 6.58 | **7.61** | 8.35 | % |
| **C.** 1Q27 nights y/y, RNPL module | derived | `rnpl_nights_module.csv` | 5.28 | **6.47** | 7.34 | % |
| **D.** step-down vs the current "low double digits" frame | derived | B − 10.0, the bottom of the bucket in `02_guidance_ledger.csv` (2Q26 letter, 6 Aug 2026, verbatim) | −3.42 | **−2.39** | −1.65 | pp |
| **E.** revenue-growth step implied by D | | | | | | pp |
| **F.** multiple effect at **+0.48 turns of EV/EBITDA per point of forward revenue growth** | measured (repo regression) | `12_valuation-multiple-regime.md`, b = +0.48, t 8.3, 2023–26 monthly | | | | turns |
| **G.** 5 Nov day-one, executable, from cell (b) | base rate | `qog_momentum_cells.csv` | −0.26 | +0.88 | +4.01 | % excess vs QQQ |
| **H.** 20-session drift, cell (b) | base rate | same | −11.68 | −4.40 | +10.94 | % excess vs QQQ |
| **I.** 60-session drift, cell (b) | base rate | same | −28.32 | −4.20 | +11.12 | % excess vs QQQ |
| **J.** February (1Q27 guide) print | | | | | | % excess vs QQQ |
| **K.** FY27 revenue consensus change over the path | | | | | | % |
| **L.** total 3-to-12-month expected excess return | | | | | | % |
| **M.** position size | assumed | `00_SYNTHESIS.md` item 7 | 1.0 | 1.5 | 2.0 | % notional |
| **N.** flip rule | pre-registered | `00_SYNTHESIS.md` §2; `D1_prereg_thresholds.csv` | — | — | — | — |

**What fills each blank.**

- **E** needs the ADR and take-rate legs stated explicitly. `fy27_quarterly_phasing_rnpl_aware.csv` carries the quarterly path; the ADR leg is the two-sided one (`00_SYNTHESIS.md` §3 channel (d): −2.00 to +1.78 points of FY27 growth) and must be moved deliberately, not inherited. Until someone signs the ADR path, E is not a number this data supports.
- **F** is E × 0.48 and nothing else. It must **not** also be applied to a margin line — margin's coefficient on the multiple is statistically zero (t 0.3 in the time series). It must not be applied a second time to the same growth step through the EBITDA level.
- **J** needs a cell of prints where the guide implied a KPI deceleration against a hard comp. Cell (c′) is the nearest thing and has n = 12 with a mean 1.4 standard errors from zero; it does not support a separate February number. Bloomberg row 15 (BKNG/EXPE) is what widens it.
- **K** is the estimate-revision leg and is exactly what the repo does not have. Today's *level*, for the record: FY2027 revenue **$15,730M, Zacks, n = 13, as of 11 Sep 2026 15:44 ET** and **$15,757.8M, Alpha Vantage, n = 44, 11 Sep 2026 capture time** (`A1_consensus_vintages.md`). There is no history behind either. Bloomberg row 1 fills it.
- **L** is F + H (3-month) or F + I (12-month) + K. Two of three are blank, so L is blank. **Do not sum G into L**: G is a one-day dispersion, not an expected return, and adding it would double-count the reaction.

**Standing constraints on how this table gets used.** Day-one direction is not predictable and 73% of the day-one number is an untradable gap (reproduced exactly here). The guide-below-Street → 20-day-drift rule is a base rate with a story, not a mechanical rule, and carries no p-value. The exit multiple moves +0.48 turns per point of forward revenue growth and zero per point of margin. Margin breaks pre-announced in letters still produced 8–13% down days, because the market prices the guide — so the 5 Nov *guide*, not the 3Q26 print, is the event. And the print lands **after** the 22–24 October finals.

---

## 8. Files

**Written (all new):**
- `docs/rnpl-short-audit/05b_momentum-reversal-object.md` — this note.
- `analysis/src/rnpl_short_audit/qog_momentum_reversal.py` — rebuilds every CSV below from the repo inputs. Run from the repo root with `/Users/theomachado/.venvs/citadel-abnb/bin/python`.
- `data/processed/rnpl_short_audit/qog_momentum_print_panel.csv` — 23 prints × 55 columns.
- `data/processed/rnpl_short_audit/qog_momentum_reconciliation.csv` — 14 rows, section 3.4.
- `data/processed/rnpl_short_audit/qog_momentum_cells.csv` — 91 rows, 13 cells × 7 return metrics.
- `data/processed/rnpl_short_audit/qog_momentum_cell_members.csv` — 141 rows, every print in every cell.
- `data/processed/rnpl_short_audit/qog_momentum_state_today.csv` — 51 rows, 17 tickers × 3 horizons.
- `data/processed/rnpl_short_audit/qog_momentum_since_2026q2_print.csv` — 18 rows.
- `data/processed/rnpl_short_audit/qog_momentum_bloomberg_spec.csv` — 18 rows, section 6.
- `data/processed/rnpl_short_audit/qog_momentum_return_path.csv` — 14 rows, section 7.

**Read (unmodified):** `data/processed/overnight/` — `20_prices_ohlc.csv`, `20_executable_returns.csv`, `20_vintage_register.csv`, `04_reaction_panel.csv`, `02_kpi_panel_quarterly.csv`, `02_guidance_ledger.csv`, `09_earnings_drift_by_print.csv`, `09_earnings_drift_paths.csv`, `09_earnings_drift_stats.csv`, `09_runup_vs_reaction.csv`, `09_prices_daily.csv`, `09_analyst_actions.csv`, `09_positioning_short_interest.csv`, `05_reaction_by_accel.csv`, `03_event_study.csv`, `04_current_consensus.csv`, `23_options_event_estimates.csv`, `20_frozen_q3_2026.csv`, `09_reconciliation_vs_existing.csv`; `data/processed/rnpl_short_audit/rnpl_nights_module.csv`; notes `research/notes/overnight/09_stock-behaviour-and-alpha.md`, `12_valuation-multiple-regime.md`, `20_temporal-validation.md`, `14_master-synthesis.md`; `docs/rnpl-short-audit/00_SYNTHESIS.md`; `docs/revenue-forecast-strategy/05_backtests/RED_TEAM.md`, `A1_consensus_vintages.md`; `docs/superpowers/specs/2026-09-11-rnpl-quality-of-growth-study-design.md`.
