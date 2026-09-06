# 12. What multiple the market pays ABNB, and why

Workstream 12 of the 6-7 Sep 2026 overnight run. Prices to 4 Sep 2026 ($181.94). All ABNB fundamentals are as-reported
(shareholder letters + XBRL); peer fundamentals are XBRL/yfinance at 4 Sep 2026; consensus is yfinance/stockanalysis.com.

---

## Bottom line

1. **The multiple, not the fundamentals, has been the whole stock since 2021.** From 4Q21 to today ABNB's LTM adj. EBITDA
   is up **+190%** and the share price is up **+9%**: EV/LTM adj. EBITDA went 55.6x -> 21.4x (-61%). Every regime in the
   table below is a re-rating story with a fundamental story attached, not the other way round.
2. **The 2021-24 de-rating was growth normalisation plus rates; the 2026 re-rating is growth re-acceleration.** ABNB's own
   2023-26 monthly line says **each point of forward revenue growth is worth about half a turn of EV/EBITDA**
   (b = +0.48, t 8.3, R² 0.68 with margin, 10y and the Nasdaq-100 multiple; but Durbin-Watson 0.93, so read the
   12-month-change specs, where the growth coefficient is +0.49, t 5.6, R² 0.45). Margin does **not** move the multiple
   (t 0.3 in the time series, t 1.3-1.5 in the cross-section). This is the single most important finding for the model.
3. **The driver model's 18 / 22 / 25.5x exit multiples are not supported by any of the three independent methods.**
   Time series, cross-section and a fade-DCF at the FY27 exit all land lower. Recommended set:
   **13.5x bear / 16.5x base / 18.5x bull**, giving **$137 / $191 / $242** against the model's $176 / $248 / $325.
   At the model's multiples a 25/50/25 weighting is worth $249 (+37%); at the evidence-based set it is $190 (+5%).
   **Nearly all of the pitch's stated upside currently sits in the exit multiple, not in the operating case.**
4. **Cross-section: ABNB is the most expensive travel name on every EBITDA and revenue metric, and average once you
   burden FCF with SBC.** EV/NTM adj. EBITDA 18.5x vs a travel/marketplace median of 13.9x and BKNG 12.8x; EV/NTM
   revenue 6.5x vs 3.3x. But EV/NTM SBC-adjusted FCF 27.3x vs a peer median of 27.2x - dead on. The premium is a
   statement about ABNB's SBC (12.9% of revenue vs a 3.1% peer median), not about its quality.
5. **The lens the stock actually tracks is forward revenue per share, i.e. the guide - not cash flow.** 2023-26,
   correlation of 12-month log changes in price with the per-share lens: NTM revenue proxy **0.72**, LTM revenue 0.62,
   GAAP net income 0.51, adj. EBITDA 0.43, SBC-adjusted FCF 0.41, FCF 0.29.
6. **Print days are re-ratings.** Across 19 prints the day-1 move correlates +0.84 with the change in the EV/NTM-revenue
   multiple and +0.11 with the change in the NTM revenue estimate. On the nine moves of 7% or more, 84% of the absolute
   move is multiple. On 5 Nov the estimate will barely move; the multiple will.
7. **The Street is now behind the stock.** Spot $181.94 is **above** the mean target ($179.55 across 31 live targets;
   stockanalysis.com has $178.96 across 46 on 3 Sep). 55% of targets sit below spot. Since the 2Q26 print there have
   been **22 raises and 0 cuts** (median +12.6%) and the stock still outran them. The mean target implies only
   **15.4x** FY27E base-case EBITDA; the highest target on the Street ($220, Rosenblatt / DA Davidson) implies 19.3x.
   **No sell-side target on the tape implies anything like 22x, let alone 25.5x.**

---

## 1. ABNB's multiple history

`data/processed/overnight/12_abnb_multiples_history.csv` (quarterly, quarter-end price on that quarter's own LTM),
`12_abnb_multiples_monthly.csv` (month-ends, point-in-time: price against the last **reported** quarter, so the panel is
tradeable). EV = diluted market cap - (cash + short-term investments - debt). **Funds held for clients ($12.2B at 2Q26)
are excluded from net cash** - the model's convention, and the right one; see caveat C6 for what it does to peer
comparisons. Figure: `analysis/figures/overnight/12_abnb_multiples_history.png`.

| Quarter | Price | EV/LTM rev | EV/LTM EBITDA | EV/LTM FCF | P/LTM SBC-adj FCF | EV/NTM EBITDA | LTM growth | NTM growth (guide) | LTM margin | SBC % rev | Buyback yield | 10y | NDX fwd P/E |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4Q21 | 166 | 14.8x | 55.6x | 38.7x | 68.3x | 31.9x | 77% | 74% | 26.6% | 15.0% | 0.0% | 1.52 | 27.5 |
| 4Q22 | 86 | 6.4x | 18.6x | 15.9x | 24.9x | 15.3x | 40% | 22% | 34.6% | 11.1% | 2.4% | 3.88 | 21.0 |
| 1Q24 | 165 | 9.7x | 25.9x | 23.7x | 35.8x | 23.0x | 18% | 13% | 37.3% | 11.3% | 2.3% | 4.20 | 26.5 |
| 4Q24 | 131 | 6.7x | 18.5x | 16.7x | 27.4x | 17.2x | 12% | 8% | 36.4% | 13.0% | 4.1% | 4.58 | 26.4 |
| 3Q25 | 121 | 5.5x | 15.4x | 14.4x | 25.4x | 13.9x | 10% | 10% | 35.8% | 13.2% | 4.7% | 4.16 | 28.1 |
| 1Q26 | 126 | 5.3x | 15.3x | 14.8x | 26.5x | 13.0x | 13% | 18% | 34.8% | 12.9% | 5.3% | 4.30 | 23.2 |
| **4 Sep 26** | **182** | **7.5x** | **21.4x** | **20.5x** | **34.7x** | **18.2x** | **14%** | **18%** | **35.1%** | **12.9%** | **3.8%** | **4.77** | **25.0** |

Monthly trough was **Nov 2025: 13.3x EV/NTM EBITDA at $117**. Today 18.2x at $182 - the forward multiple is +37% from
the trough and the price +56%.

### Regime decomposition (`12_regime_decomposition.csv`)

Because EV = multiple x LTM EBITDA exactly, the split is arithmetic, not a model.

| Window | Price | Multiple (EV/LTM EBITDA) | LTM EBITDA | Diluted shares | Context |
|---|---|---|---|---|---|
| 4Q21 -> 4Q22 | **-49%** | **-67%** (55.6x -> 18.6x) | +82% | +27% | 10y 1.5 -> 3.9%; NDX fwd P/E 27.5 -> 21.0; guide-implied growth 74% -> 22% |
| 4Q22 -> 1Q24 | **+93%** | **+39%** (18.6x -> 25.9x) | +31% | -9% | margin 34.6 -> 37.3%; NDX 21.0 -> 26.5 |
| 1Q24 -> 1Q26 | **-23%** | **-41%** (25.9x -> 15.3x) | +15% | -7% | nights growth to single digits; margin 37.3 -> 34.8% |
| 1Q26 -> 4 Sep 26 | **+44%** | **+40%** (15.3x -> 21.4x) | +5% | -2% | guide-implied growth 18%; 2Q26 print +17.4% in a day |
| 4Q21 -> 4 Sep 26 | **+9%** | **-61%** | **+190%** | +5% | the whole story |

**What explains the 2021-24 de-rating:** roughly two thirds growth normalisation (guide-implied NTM growth 74% -> 13%,
worth ~29 turns on the 0.48 turns-per-point slope) and the rest a market/rates regime change (10y +2.4pts, NDX fwd P/E -6.5 turns from 4Q21 to 4Q22). Margin expansion (26.6% -> 37.3%) paid for none of it.

**What explains the 2026 re-rating:** almost entirely the return of forward growth. Guide-implied NTM growth stepped
from 10.4% (as known through Jan 2026) to 17.1% after the 4Q25 print on 13 Feb 2026, and to 17.8% after 2Q26;
the multiple followed with a lag; the 2Q26 print on
7 Aug delivered +17.4% in one session with essentially **no** change in the NTM revenue estimate (-0.2%). LTM EBITDA is
up only 5% over the whole window and the margin is flat.

### Regressions (`12_abnb_multiple_regressions.csv`, 30 specifications, all reported)

Monthly point-in-time, Newey-West:

| Sample | Dependent | growth | margin | 10y | NDX fwd P/E | n | R² | DW |
|---|---|---|---|---|---|---|---|---|
| 2021-26 | EV/LTM EBITDA | +0.39 (5.6) LTM | -0.27 (-0.4) | +4.02 (3.3) | +1.13 (2.1) | 47 | 0.49 | 0.74 |
| **2023-26** | **EV/LTM EBITDA** | **+0.48 (8.3) LTM** | **+0.16 (0.3)** | **+4.69 (4.5)** | **+0.58 (1.7)** | **45** | **0.68** | **0.93** |
| 2023-26 | EV/LTM EBITDA | +0.74 (3.4) NTM | - | -1.92 (-1.2) | +0.53 (0.7) | 45 | 0.41 | 0.61 |
| 2023-26 | EV/LTM FCF | +0.34 (7.4) LTM | -0.07 (-0.6) FCF mgn | +4.42 (3.2) | +0.68 (2.2) | 45 | 0.52 | 1.04 |
| 12m changes | d EV/LTM EBITDA | **+0.49 (5.6) NTM** | - | +3.38 (3.7) | +0.87 (1.9) | 35 | 0.45 | 1.30 |
| 12m changes | d EV/LTM EBITDA | -0.04 (-0.3) LTM | -0.82 (-3.1) | +3.94 (2.6) | +0.13 (0.2) | 35 | 0.27 | 0.96 |
| 12m changes | d EV/LTM FCF | +0.08 (0.6) LTM | -0.16 (-0.8) FCF mgn | +4.74 (2.8) | +0.46 (0.7) | 35 | 0.33 | 1.00 |

Read: **forward growth is the only fundamental that moves ABNB's multiple.** The LTM-growth version survives in levels
but dies in 12-month changes (t -0.3) while the NTM-guide version strengthens (t +5.6) - i.e. the market prices the
guide, not the trailing print. Margin has no explanatory power in any specification, and in 12m changes its sign is
negative. The 10-year yield coefficient is **positive** in every spec, which is backwards from theory; 2023-26 is a
regime in which yields and risk appetite rose together, so treat it as a regime marker, not a discount-rate channel.

**Autocorrelation caveat:** Durbin-Watson is 0.53-1.06 on every level regression, so the level t-statistics are badly
overstated (the honest effective n is closer to the 15-20 independent quarters than to 45-47 months). The 12m-change
rows are the ones to quote. The quarterly (n=16-23) versions of the same specs are in the CSV and give the same signs
with smaller t-statistics. **Tests run in this workstream: 30 time-series specifications, 24 cross-sectional fits,
18 lens correlations, 5 print-attribution cuts. Treat any single t-statistic accordingly.**

---

## 2. Cross-section, 4 Sep 2026 (`12_peer_multiples.csv`, `12_peer_regressions.csv`, figure `12_peer_crosssection.png`)

18 peers plus ABNB. LTM from XBRL 10-Q/10-K where available, yfinance statements for the 20-F filers (TCOM, SPOT, MMYT);
TCOM (CNY) and SPOT (EUR) statements, debt and consensus converted to USD at the 4-6 Sep 2026 rate. NTM revenue is
time-weighted consensus FY0/FY1; **NTM EBITDA and NTM FCF hold each company's LTM margin on NTM revenue** (no free
EBITDA consensus exists), so cross-company differences reflect growth and today's margin, not consensus margin change.

| | NTM growth | Adj. EBITDA mgn | SBC % rev | FCF mgn | FCF/EBITDA | Net cash % mcap | Buyback yld | EV/NTM rev | EV/NTM adj EBITDA | EV/NTM GAAP EBITDA | EV/NTM FCF | EV/NTM SBC-adj FCF | NTM P/E |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **ABNB** | **15.7%** | **35.1%** | **12.9%** | **36.7%** | **105%** | **+8.8%** | **3.8%** | **6.5x** | **18.5x** | **29.3x** | **17.7x** | **27.3x** | **30.5x** |
| BKNG | 10.9% | 37.0% | 2.1% | 33.8% | 91% | -2.6% | 7.2% | 4.8x | 12.8x | 13.6x | 14.1x | 15.0x | 16.2x |
| EXPE | 8.7% | 24.3% | 2.6% | 28.4% | 117% | +4.0% | 5.4% | 2.0x | 8.3x | 9.3x | 7.1x | 7.8x | 12.7x |
| TRIP | -8.8% | 12.8% | 5.0% | 7.4% | 58% | -4.7% | 43.7%* | 0.7x | 5.4x | 8.9x | 9.4x | 28.8x | 9.2x |
| TCOM | 13.0% | 32.4% | 3.6% | 21.8% | 67% | +28.6% | 2.6% | 1.7x | 5.2x | 5.9x | 7.8x | 9.3x | 10.1x |
| MMYT | 23.5% | 19.8% | 2.2% | 14.4% | 73% | -12.6% | 60.8%* | 4.5x | 22.8x | 25.6x | 31.3x | 36.9x | 24.8x |
| UBER | 17.0% | 17.0% | 3.5% | 18.3% | 108% | -6.0% | 4.5% | 2.5x | 14.9x | 18.8x | 13.9x | 17.2x | 17.6x |
| DASH | 29.4% | 17.8% | 7.0% | 13.5% | 76% | +2.2% | 1.1% | 4.4x | 24.5x | 40.5x | 32.4x | 67.6x | 52.9x |
| META | 28.2% | 58.0% | 10.5% | 18.0% | 31% | -1.4% | 0.2% | 5.4x | 9.4x | 11.5x | 30.3x | 72.7x | 18.5x |
| GOOGL | 31.0% | 45.7% | 6.9% | 11.9% | 26% | +2.9% | 0.4% | 6.9x | 15.1x | 17.7x | 57.6x | 136.5x | 20.8x |
| AMZN | 18.2% | 24.3% | 2.5% | -1.5% | -6% | -4.6% | 0.0% | 3.2x | 13.1x | 14.6x | n.m. | n.m. | 23.5x |
| NFLX | 14.9% | 31.5% | 1.0% | 23.1% | 73% | -2.3% | 3.0% | 6.0x | 19.1x | 19.7x | 26.0x | 27.2x | 20.8x |
| SPOT | 19.3% | 16.7% | 1.5% | 18.0% | 108% | +9.3% | 1.0% | 4.0x | 24.1x | 26.5x | 22.3x | 24.4x | 31.7x |
| DUOL | 15.9% | 26.8% | 12.6% | 34.7% | 129% | +17.1% | 1.0% | 4.5x | 16.8x | 31.7x | 13.0x | 20.4x | 20.9x |
| MAR | 8.0% | 19.2% | 0.7% | 11.6% | 61% | -19.7% | 4.1% | 3.6x | 18.9x | 19.6x | 31.1x | 33.2x | 26.3x |
| HLT | 11.1% | 26.4% | 1.5% | 15.5% | 59% | -18.6% | 4.7% | 6.0x | 22.7x | 24.1x | 38.6x | 42.6x | 30.8x |
| H | 6.3% | 12.5% | 1.0% | 3.5% | 28% | -25.0% | 1.9% | 2.6x | 20.5x | 22.3x | 72.9x | 102.6x | 36.5x |
| ETSY | 3.0% | 27.5% | 8.0% | 21.5% | 78% | -27.8% | 9.2% | 3.0x | 11.1x | 15.6x | 14.2x | 22.7x | 18.2x |
| EBAY | 9.4% | 29.8% | 5.4% | 20.2% | 68% | -8.3% | 4.5% | 3.8x | 12.7x | 15.5x | 18.8x | 25.6x | 15.7x |
| **Peer median** | 13.9% | 25.3% | 3.1% | 18.0% | 70% | -3.6% | 3.6% | 3.9x | 15.0x | 18.3x | 20.6x | 27.2x | 20.8x |
| **Travel+mkt median** | 10.2% | 22.1% | 3.1% | 16.9% | 70% | -7.2% | 4.6% | 3.3x | 13.9x | 17.2x | 16.5x | 27.2x | 17.9x |

\* MMYT's 60.8% and TRIP's 43.7% buyback yields are one-off transactions (MMYT's ~$3.1B repurchase of Trip.com's stake,
FY to Mar-26; TRIP's $501M in FY25), not run-rates. DESP was taken private by Prosus in May 2025 and is not listed.

**Where ABNB sits.** Highest EV/NTM revenue of the 19 except GOOGL; highest EV/NTM adj. EBITDA in the OTA set by 45%
over BKNG. Fitted vs actual (log-linear, ABNB excluded from the fit, leave-one-out range in the CSV):

| Fit | n | R² | ABNB actual | ABNB fitted | Premium |
|---|---|---|---|---|---|
| EV/NTM adj. EBITDA on growth, all peers | 18 | 0.19 | 18.5x | 14.4x | +29% |
| EV/NTM adj. EBITDA on growth, travel+mkt | 12 | 0.35 | 18.5x | 15.6x | +19% |
| EV/NTM revenue on growth + margin, all peers | 18 | 0.53 | 6.5x | 3.9x | **+65%** |
| EV/NTM GAAP (SBC-burdened) EBITDA on growth + margin | 18 | 0.51 | 29.3x | 18.0x | **+63%** |
| EV/NTM FCF on growth + FCF margin + SBC | 17 | 0.59 | 17.7x | 7.9x | +125% |
| **EV/NTM SBC-adjusted FCF on growth, all peers** | 17 | 0.18 | **27.3x** | **31.8x** | **-14%** |
| EV/NTM SBC-adjusted FCF on rule-of-40 (SBC-adj), all peers | 17 | 0.02 | 27.3x | 27.2x | **+0.4%** |
| NTM P/E on growth, all peers | 18 | 0.23 | 30.5x | 21.5x | +42% |

**A trap worth naming.** Regressing EV/EBITDA on the EBITDA margin gives a *negative* coefficient (-0.024 per point,
t -4.3). That is almost exactly the mechanical -1/margin = -0.027: a higher margin makes the denominator bigger at
unchanged EV/revenue. The fit is measuring the artefact, not the market's view of margin. Use EV/**revenue** on growth
+ margin when you want to price margin expansion; there the margin coefficient is +0.011 to +0.024 per point but
**t 1.3-1.5, i.e. not significant**. Conclusion either way: *the cross-section does not pay for margin.* This kills
the intuition that ABNB's 36.5% FY27 margin earns it a premium multiple.

**The single most useful comparable.** BKNG today: 10.9% consensus growth, 37.0% adj. EBITDA margin, 91% FCF
conversion, 12.8x EV/NTM adj. EBITDA. ABNB's **base-case FY27** is 12.3% growth and a 36.5% margin - practically the
same company - and the model exits it at 22x. The three defensible differences are ABNB's net cash (+8.8% of market cap
vs BKNG -2.6%; the 11.4-point gap is $12.4B, about **+2.3 turns**), its slightly higher growth (FY27 base 12.3% vs
BKNG's 10.9% today, **+0.7 turns** on the 0.48 slope) and its optionality (Experiences, Services, hotels -
unquantified). Against that, SBC: putting ABNB on BKNG's SBC-burdened multiple (13.6x EV/NTM GAAP EBITDA) implies
**8.6x** on ABNB's adj. EBITDA - **4 turns below BKNG's own 12.8x**, because ABNB gives back 12.9 points of revenue
to SBC and BKNG gives back 2.1. Net of all three, a defensible ABNB multiple is BKNG's 12.8x plus ~3 turns for balance
sheet and growth, less whatever you charge for SBC: **12-16x**, with anything above that being an explicit,
separately-argued payment for optionality.

---

## 3. Exit multiples for the FY27 grid

`12_exit_multiple_evidence.csv` (39 method x scenario rows), `12_exit_multiple_recommendation.csv`,
`12_price_sensitivity.csv`, figure `12_exit_multiple_evidence.png`. FY27E grid from `abnb_valuation_scenarios.csv`
(bear/base/bull revenue growth 4.3 / 12.3 / 15.3%; adj. EBITDA margin 33.8 / 36.5 / 39.8%).

| Method | Bear | Base | Bull | Note |
|---|---|---|---|---|
| Time series: 2023-26 months with matching NTM growth, median | 15.9x | 16.8x | 18.3x | n = 18 / 24 / 32 months |
| Time series: OLS on NTM growth + margin, 2023-26 monthly | 12.7x | 17.5x | 20.3x | b_growth +0.48 (t 2.3), b_margin +0.39 (t 0.4) |
| Cross-section: EV/NTM EBITDA on growth, all peers | 11.4x | 13.4x | 14.3x | R² 0.19 |
| Cross-section: EV/NTM EBITDA on growth, travel+mkt | 10.7x | 13.9x | 15.4x | R² 0.35 |
| Cross-section: EV/NTM revenue on growth + margin, restated | 7.9x | 9.8x | 10.3x | all peers; travel+mkt gives 8.7 / 11.5 / 12.8x |
| Cross-section: 4 nearest travel comps by growth, median | 15.0x | 12.8x | 13.9x | observed multiples, no fit |
| Intrinsic: 10y fade DCF at the FY27 exit, WACC 10% / g 3% | 15.1x | 19.7x | 23.1x | range over WACC 9-11%, g 2.5-3.0%: 12.6-17.7 / 16.3-23.1 / 19.0-27.1x |
| *Same DCF on SBC-adjusted FCF* | *8.3x* | *12.7x* | *16.4x* | *the SBC-honest version* |
| *Cross-section, four regressors incl. SBC and conversion* | *4.9-6.7x* | *6.4-8.7x* | *7.0-9.3x* | *diagnostic only; n=12-18 cannot carry 4 regressors* |
| Today's multiple (18.2x EV/NTM EBITDA) | 18.2x | 18.2x | 18.2x | 2023-26 monthly range 13.3-27.3x, median 18.0x |
| **Model's assumption** | **18.0x** | **22.0x** | **25.5x** | |
| **Recommended** | **13.5x** | **16.5x** | **18.5x** | mean of the time-series, cross-section and intrinsic family medians |

**Reverse DCF cross-check** (`abnb_reverse_dcf.csv`, driver-model note s.6). Today's $99.0B EV on LTM reported FCF
requires **7.5%** ten-year growth at WACC 10% / terminal 3%; on SBC-adjusted FCF it requires **13.3%**. Both are
today's numbers, so they bound the exit: a base case that grows 12.3% in FY27 and 11% in FY28 is worth roughly
today's multiple - not a higher one - and only if you keep ignoring SBC.

### Price sensitivity (`12_price_sensitivity.csv`), FY2027E, on EV / adj. EBITDA

| Exit x | Bear ($4.94B EBITDA, 575M sh, $12.0B net cash) | Base ($5.83B, 567M, $12.4B) | Bull ($6.64B, 562M, $13.4B) |
|---|---|---|---|
| 12x | 124 | 145 | 166 |
| 14x | 141 | 166 | 189 |
| 16x | 158 | 186 | 213 |
| **16.5x** | 163 | **191** | 219 |
| 18x | **176 (model bear)** | 207 | 236 |
| **18.5x** | 180 | 212 | **242 (recommended bull)** |
| 20x | 193 | 227 | 260 |
| 22x | 210 | **248 (model base)** | 284 |
| 24x | 227 | 268 | 307 |
| 26x | 244 | 289 | 331 |
| **13.5x (recommended bear)** | **137** | 160 | 183 |

Each turn of EV/EBITDA is worth **$8.6 / $10.3 / $11.8** per share in bear / base / bull, i.e. **5-6% of today's price
per turn**. Going from the model's 22x base to the evidence-based 16.5x removes $57 of the $66 of base-case upside.

### Recommendation for the deck

Use **13.5 / 16.5 / 18.5x** as the headline and show 18 / 22 / 25.5x as an explicit "market pays for optionality"
sensitivity, labelled as such. If the pitch is a long, it must be argued on (a) FY27 revenue above $16.0B, (b) SBC
falling below ~10% of revenue, or (c) a named optionality bucket priced separately - **not** on the exit multiple.
The alternative honest framing: at 16.5x the base case is $191, +5%, and the trade is a coin flip; the pitch needs a
reason the multiple goes to 20x+ and that reason has to be forward growth, because nothing else has ever moved it.

---

## 4. Which lens tracks the stock, and the SBC debate

`12_abnb_lens_tracking.csv`, `12_abnb_print_decomposition.csv`, `12_print_move_attribution.csv`,
figures `12_abnb_lens_tracking.png`, `12_analyst_targets.png` (right panel).

**Per-share lenses vs the share price** (all fundamentals divided by the diluted count of the last reported quarter,
because buybacks have cut it ~4%/yr since 2023):

| Lens | corr(log price, log lens) 2023-26 | corr of 12m log changes 2023-26 | 12m changes 2022-26 | slope of log price on log lens |
|---|---|---|---|---|
| **NTM revenue per share (guide proxy)** | 0.40 | **0.72** | 0.40 | 0.27 |
| LTM revenue per share | 0.35 | 0.62 | 0.35 | 0.22 |
| LTM GAAP net income per share | 0.38 | 0.51 | 0.57 | 0.12 |
| LTM adj. EBITDA per share | 0.36 | 0.43 | -0.01 | 0.21 |
| LTM SBC-adjusted FCF per share | 0.36 | 0.41 | 0.25 | 0.41 |
| LTM FCF per share | 0.33 | 0.29 | 0.07 | 0.27 |

Two readings. (i) The **guide** is the lens: forward revenue per share beats every backward-looking cash measure, in
both windows. (ii) **Every slope is far below 1** (0.12-0.41), which is the same statement as "the multiple does the
work": a 10% rise in the fundamental has historically moved the stock 1-4%.

**Day-1 moves are re-ratings** (`12_print_move_attribution.csv`; NTM revenue estimate before the print is the prior
quarter's guide-implied path rolled one quarter, after is the new guide, both with the same trailing cushion):

| Sample | n | mean day-1 | mean abs estimate change | mean abs multiple change | share of abs move from multiple | corr(ret, estimate) | corr(ret, multiple) |
|---|---|---|---|---|---|---|---|
| All prints | 19 | -0.3% | 3.5% | 8.5% | 71% | +0.11 | +0.84 |
| Up days | 9 | +7.0% | 3.0% | 8.5% | 74% | -0.51 | +0.94 |
| Down days | 10 | -6.8% | 3.9% | 8.4% | 68% | -0.18 | +0.71 |
| Moves >= 7% | 9 | -0.2% (11.9% abs) | 2.5% | 13.6% | **84%** | +0.02 | **+0.99** |
| 2023-26 prints | 15 | -0.1% | 2.1% | 7.5% | 78% | +0.09 | **+0.97** |

The three biggest up-days make the point on their own: 2Q26 (+17.4%) came with an estimate change of **-0.2%**;
4Q24 (+14.5%) with **-3.6%**; 4Q22 (+13.4%) with **-2.3%**. In all three the stock re-rated 17-20% in a session on
numbers that were flat or down. This is consistent with the predictive study's finding that beat-vs-guide has no
print-day alpha - the reaction is about positioning and language, and it shows up as a multiple.

### The SBC debate, with numbers

- LTM SBC **$1,696M = 12.9% of revenue** (2Q26). Peer median 3.1%; ABNB is the highest of the 19 names, above DUOL
  (12.6%) and META (10.5%), and 6x BKNG (2.1%).
- LTM FCF $4,827M (36.7% margin) becomes **$3,131M (23.8%)** SBC-adjusted. The multiple goes from EV/NTM FCF 17.7x to
  EV/NTM SBC-adjusted FCF **27.3x**, and P/LTM SBC-adjusted FCF is **34.7x**.
- **The bear case is not that the SBC-adjusted multiple is high - it is that it is average.** ABNB's 27.3x sits on the
  peer median of 27.2x, so once SBC is charged, the market pays ABNB nothing for being ABNB. Every dollar of the
  premium visible on EBITDA and revenue is an SBC add-back.
- **The bull rebuttal, and it is a real one:** ABNB actually funds the dilution. LTM buybacks are $4.1B (3.8% of market
  cap) and net cash return - buybacks plus RSU tax withholding less SBC - is **+2.75% of market cap**, positive in every
  quarter since 3Q22. The diluted count fell from 649M (2Q24) to **597M (2Q26), -8% in two years**. So SBC is
  economically a cash cost that is being paid, not an open-ended dilution; the argument is about *which* multiple you
  quote, not about whether shareholders are being diluted (they are not).
- **How to settle it in the deck:** quote EV/adj. EBITDA and EV/SBC-adjusted FCF side by side, and note that the DCF
  on SBC-adjusted FCF supports a **12.7x** FY27 base exit versus 19.7x on reported FCF. The gap - about 7 turns, ~$70
  per share - *is* the SBC debate, priced.

---

## 5. Sell-side target dispersion and rating mix

`12_analyst_targets.csv`, `12_analyst_target_summary.csv`, figure `12_analyst_targets.png`. Source: the
Yahoo Finance / Benzinga upgrades-downgrades feed pulled by workstream 09 on 6 Sep 2026
(`data/processed/overnight/09_analyst_actions.csv`, 466 actions since Dec 2020); the book is the latest action per firm
with an action in the last 12 months. Cross-check: stockanalysis.com/stocks/abnb/forecast (3 Sep 2026) shows average
$178.96, high $220, low $125, 46 analysts, 21 Strong Buy / 4 Buy / 18 Hold / 1 Sell / 2 Strong Sell - consistent with
the 31 live targets below.

| | Value |
|---|---|
| Firms with an action in the last 12 months / with a live target | 34 / 31 |
| Mean / median target | **$179.55 / $175.00** |
| High / low | **$220** (Rosenblatt 1 Sep 26, DA Davidson 31 Aug 26) / **$125** (Morgan Stanley 30 Jul 26, Underweight) |
| High-to-low spread, dispersion (sd/mean) | 1.76x, 0.13 |
| Mean target vs spot $181.94 | **-1.3%** (spot is above the average target) |
| Share of targets below spot | **55%** |
| Rating mix | **21 Buy (62%), 11 Hold (32%), 2 Sell (6%)** - Goldman Sachs (Sell, $155, 20 Jul 26) and Morgan Stanley (Underweight, $125, 30 Jul 26) |
| Revisions since the 2Q26 print (7 Aug 26) | **22 raises, 0 cuts**, median **+12.6%**, mean +14.1%, range +2.8% to +31.6% |
| Stock on the 2Q26 print day | **+17.4%** - the tape outran the revisions |

**Implied multiples in the targets** (on FY2027E base-case adj. EBITDA $5.83B, net cash $12.4B, 567M diluted shares):

| Target | Firms | Implied EV/FY27E adj. EBITDA | Implied P/FY27E SBC-adj FCF |
|---|---|---|---|
| $220 (high) | Rosenblatt, DA Davidson | **19.3x** | 33.3x |
| $217 | Bernstein | 19.0x | 32.8x |
| $200 | Susquehanna, Wedbush, Evercore, Canaccord | 17.4x | 30.2x |
| $179.55 (mean) | - | **15.4x** | 27.1x |
| $175 (median) | Jefferies, Baird, BofA, Mizuho | 14.9x | 26.5x |
| $155 | Goldman Sachs (Sell) | 13.0x | 23.4x |
| $125 (low) | Morgan Stanley (Underweight) | **10.1x** | 18.9x |

**The most important number in this section:** the entire sell-side target distribution implies **10.1x to 19.3x**
FY27 EV/EBITDA. The driver model's base 22x and bull 25.5x sit **outside the range of every published target**,
including the highest one on the Street. Cross-referenced to the pitch landscape note, the same picture holds among
independent write-ups: Truist 20x 2027E, Bernstein 25.5x, TIKR NTM 13.7-15.4x, LongYield 26x trailing vs BKNG 14-18x.
The dispersion is a *multiple* argument on a consensual ~10-12% growth path
(`research/notes/2026-09-04_abnb-pitch-landscape.md`, s. "Implication for our deck"), which this workstream confirms
from the data.

---

## Caveats

- **C1. Autocorrelation.** DW 0.53-1.30 on every level regression. Level t-statistics are overstated; the 12-month
  change specifications are the honest ones and they still put forward growth first. n is 45-47 months but at most
  ~15-20 independent observations.
- **C2. The NTM proxy is the guide, not consensus.** ABNB's NTM revenue in the history panel is the next-quarter guide
  mid grossed up by a trailing 4-quarter beat cushion, with that implied growth applied to the following three
  quarters. It currently reads **17.8%** against sell-side consensus of **15.7%**, so the panel's forward multiple
  (18.2x) is ~1.5 turns *lower* than a consensus-based one would be. The method column is in the CSV row by row.
- **C3. The Nasdaq-100 forward P/E series** is Siblis Research quarterly values from Dec 2023 on, and chart-read
  approximations (+/- 1 turn) for 2021-mid-2023, linearly interpolated to daily. Every market-multiple coefficient
  depends on that; treat the NDX terms as indicative only. Values and their provenance are hard-coded in
  `12_abnb_multiples_history.py` (`NDX_FWD_PE`).
- **C4. Peer NTM EBITDA/FCF hold today's margin.** No free forward EBITDA consensus exists, so a peer expected to
  expand margin (or ABNB itself) is understated on the forward EBITDA multiple. Only NTM revenue and NTM EPS are true
  consensus.
- **C5. TCOM and MMYT LTM** partly come from annual statements scaled to LTM by the revenue ratio (flagged
  `yfinance-FY-scaled` in the `sources` column). MMYT and TRIP buyback yields are one-off transactions.
- **C6. Customer float treatment is not uniform.** ABNB's cash line already excludes funds held for clients, so its EV
  is float-clean; BKNG's and EXPE's reported cash includes merchant prepayments, so their EVs are slightly understated
  and their multiples slightly flattered. For BKNG the effect is well under half a turn (~$4B of deferred merchant
  bookings on a $149B EV), so it does not change the conclusion, but the comparison is directionally against ABNB.
- **C7. The intrinsic exit multiple is a model, not a market observation.** It fades the scenario's FY28 growth to
  terminal over ten years at the scenario's own FCF conversion. It is most fragile in the bull case, where FY27
  conversion is 105% on guest-float growth; if GBV growth stalls, conversion falls before EBITDA does (driver-model
  caveat) and the bull exit multiple drops toward the base.
- **C8. Multiple comparison problem.** 30 time-series specs + 24 cross-sectional fits + 18 lens correlations +
  5 attribution cuts = 77 tests. The two results that survive that count are the growth coefficient (consistent sign
  and size across levels, changes, quarterly and monthly, and in the cross-section) and the multiple-vs-estimate split
  on print days (corr 0.97 on the 2023-26 sample). Everything else - rates, market multiple, margin, SBC coefficients
  - should be read as descriptive.
- **C9. Not corrected:** the peer set excludes private and non-US-listed comps (Despegar, Trivago, Yanolja, Oyo) and
  any lodging REIT. Adding hotel owners would push the travel median up (asset-heavy, high EV/EBITDA) for the wrong
  reason.

## Corrections to existing work

- None. The driver model's 18 / 22 / 25.5x football field is not an error - it is an assumption, sourced in
  `research/notes/2026-09-05_driver-model.md` s.5 as a choice. This note is the evidence against it, and section 3
  proposes the replacement. The driver-model note's own observation that "moving the multiple from 18x to 25.5x on the
  base case is worth $77 while moving FY27 growth from 4% to 16% is worth $24" is confirmed and is the reason this
  matters.

## What to build next

1. **Replace the guide-based NTM proxy with workstream 04's per-print consensus.** `04_consensus_at_print.csv` now has
   revenue consensus at 23/23 prints and next-quarter consensus at 18/23. Rebuilding `12_abnb_multiples_monthly.csv` on
   that basis would give a true EV/NTM-consensus-revenue series, would remove caveat C2, and would sharpen the
   print-day decomposition (which currently measures the change in the *guide-implied* path, not in consensus).
   `04_current_consensus.csv` corroborates today's numbers independently: Zacks FY26 $14.10B / FY27 $15.73B and
   S&P Global $14.16B / $15.76B, against the $15.23B NTM used here.
2. **Get an EBITDA consensus for the peer set.** Every peer forward EBITDA multiple here holds today's margin on
   consensus revenue. A Bloomberg or Visible Alpha pull of NTM EBITDA would turn the cross-section from indicative into
   quotable, and is the one input that could move the recommended exit multiple materially.
3. **Price the optionality separately.** The gap between the recommended 16.5x and any higher number has to be a
   named, sized bucket (Experiences, Services, hotels, ads), the way Eremos and Byte Alchemist do it in the pitch
   landscape. Adding turns to the core multiple to smuggle in optionality is the thing this note argues against.
4. **A float-consistent peer EV.** Strip customer float from BKNG, EXPE, TCOM and MMYT as well as ABNB (caveat C6).
   The effect is small but the deck should not be open to the objection.

## For the model

| Parameter | Value | Unit | Source |
|---|---|---|---|
| Exit multiple, bear (FY27E) | **13.5** | x EV / adj. EBITDA | `12_exit_multiple_recommendation.csv`, blend of time-series 14.3x, cross-section 10.7x, intrinsic 15.1x |
| Exit multiple, base (FY27E) | **16.5** | x EV / adj. EBITDA | same; time-series 17.2x, cross-section 12.8x, intrinsic 19.7x |
| Exit multiple, bull (FY27E) | **18.5** | x EV / adj. EBITDA | same; time-series 19.3x, cross-section 13.9x, intrinsic 23.1x |
| SBC-adjusted exit multiple, base | 12.7 | x EV / adj. EBITDA | fade DCF on SBC-adjusted FCF, WACC 10% / g 3% |
| Sensitivity of the multiple to forward growth | **+0.48** | turns of EV/EBITDA per pt of NTM revenue growth | 2023-26 monthly, t 8.3 (levels), +0.49 t 5.6 (12m changes) |
| Sensitivity of the multiple to margin | **0.0** | turns per pt | not significant in any spec (t 0.3 time series, t 1.3-1.5 cross-section) |
| Value of one turn of exit multiple | **$8.6 / $10.3 / $11.8** | USD per share, bear / base / bull | `12_price_sensitivity.csv` |
| Cost of equity | **10.3%** | % | CAPM: 10y 4.77% (FRED DGS10, 4 Sep 26) + beta 1.161 (yfinance) x 4.75% ERP |
| WACC | **~10%** | % | net cash $9.6B ex float vs $2.5B debt: effectively all-equity, so WACC = CoE |
| Terminal growth | 2.5-3.0% | % | used in the exit-multiple DCF and the reverse DCF |
| Diluted share path (FY26/27/28E) | 584 / 575 / 567 (bear), 581 / 567 / 554 (base), 579 / 562 / 547 (bull) | M shares | `abnb_valuation_scenarios.csv`; actual 649M (2Q24) -> 597M (2Q26) |
| Net cash ex float (FY27E) | **$12.0 / $12.4 / $13.4B** | USD | `abnb_valuation_scenarios.csv` |
| Net cash ex float, today | **$9,593M** | USD | 2Q26 XBRL; funds held for clients $12,224M excluded |
| Today's multiples at $181.94 | 21.4x LTM EBITDA, 18.2x NTM EBITDA, 20.5x LTM FCF, 34.7x P/LTM SBC-adj FCF, 7.5x LTM revenue | x | `12_abnb_multiples_history.csv` row 3Q26 |
| Implied price, recommended multiples | **$137 / $191 / $242** | USD | vs the model's $176 / $248 / $325 |

## For the 5 Nov card

- **Expect a re-rating, not an estimate change.** Over the last 15 prints (2023-26) the day-1 move correlates **+0.97**
  with the change in the EV/NTM-revenue multiple and **+0.09** with the change in the NTM revenue estimate. Mean
  absolute estimate change on a print day: **2.1%**. Mean absolute multiple change: **7.5%**.
- **The arithmetic to carry.** At $181.94, EV is $99.05B on an NTM EBITDA proxy of $5.44B. **One turn of EV/NTM EBITDA
  = $9.11 per share = 5.0%.** A typical print therefore moves the forward multiple about 1.5 turns.
- **Good prints:** on the nine up-days the multiple rose **+7.7%** on average while estimates rose **+0.3%**. The three
  biggest (2Q26 +17.4%, 4Q24 +14.5%, 4Q22 +13.4%) all came with **flat-to-down** NTM revenue estimates. A +17% day does
  not require a number; it requires positioning to be wrong.
- **Bad prints:** on the ten down-days the multiple fell **-3.8%** and estimates **-3.5%** - down-days are the only
  ones where the numbers actually move, and they move roughly half the damage.
- **Positioning going in is now unhelpful for a long.** Spot is 1.3% **above** the mean sell-side target, 55% of
  targets are below spot, and the Street already raised 22 times with 0 cuts after 2Q26 - the easy revisions are spent.
  The forward multiple has gone 13.3x (Nov 2025) to 18.2x, its 2023-26 range being 13.3-27.3x (the 27.3x was Jul 2023, on a 16% guide) with a median of 18.0x. **ABNB enters 5 Nov at its median post-2022 forward multiple with the guide implying 17.8% growth against
  15.7% consensus** - i.e. the cushion is thinner than it looks, and the asymmetry has flipped versus the last two
  prints.
- **The one number that would justify a higher exit multiple:** a Q4 guide implying **>18%** revenue growth. On the
  0.48-turns-per-point slope that is worth ~2 turns, ~$20 per share, and would be the first evidence since 2021 that
  the growth regime has genuinely changed rather than lapped an easy comparison.

---

### Files written

Scripts: `analysis/src/overnight/12_abnb_multiples_history.py`, `12_peer_multiples.py`, `12_exit_multiples_and_targets.py`
(run in that order with `py -3.13` from the repo root).

Data: `data/processed/overnight/12_abnb_multiples_history.csv`, `12_abnb_multiples_monthly.csv`,
`12_abnb_multiple_regressions.csv`, `12_abnb_lens_tracking.csv`, `12_abnb_print_decomposition.csv`,
`12_regime_decomposition.csv`, `12_print_move_attribution.csv`, `12_peer_multiples.csv`, `12_peer_regressions.csv`,
`12_exit_multiple_evidence.csv`, `12_exit_multiple_recommendation.csv`, `12_price_sensitivity.csv`,
`12_analyst_targets.csv`, `12_analyst_target_summary.csv`.

Figures: `analysis/figures/overnight/12_abnb_multiples_history.png`, `12_abnb_multiple_drivers.png`,
`12_abnb_lens_tracking.png`, `12_peer_crosssection.png`, `12_exit_multiple_evidence.png`, `12_analyst_targets.png`.
