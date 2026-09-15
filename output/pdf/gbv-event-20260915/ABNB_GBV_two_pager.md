# Airbnb: the guide, the gap, and the evidence

Prepared 15 September 2026. Scope: Q3 2026 through Q2 2027. Conditional operating scenario, not a promoted forecasting or trading strategy.

The four-quarter model turns lagged GBV into revenue and then a first-guide estimate. Its Q4 implied guide is $3,123.4m, compared with $3,105.4m when dated Yahoo/LSEG revenue expectations receive the same cushion: +$18.0m, +0.58%. Comparing our guide directly with eventual-revenue consensus would compare different objects. Applying the same cushion makes the revenue and guide gap percentages identical by construction.

| Target | Weighted GBV ($m) | Conversion | Revenue ($m) | Implied guide ($m) | Status |
|---|---:|---:|---:|---:|---|
| 2026Q3 | 27,866.7 | 17.255% | 4,808.4 | 4,723.8 | Already-issued diagnostic |
| 2026Q4 | 26,405.7 | 12.040% | 3,179.3 | 3,123.4 | Conditional future guide |
| 2027Q1 | 24,008.4 | 12.728% | 3,055.7 | 3,001.9 | Conditional future guide |
| 2027Q2 | 29,285.7 | 13.824% | 4,048.4 | 3,977.2 | Conditional future guide |

The Q3 guide is already observed: $4,690-4,770m, midpoint $4,730m, in the [6 August SEC letter](https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm). The Q3 model comparison is not an earlier forecast of that announcement. No quarterly Q1/Q2 2027 Street revenue or directly observed guide-expectation panel is available in the reviewed register.

## Model and source boundaries

Revenue = season-specific conversion x (2/3 x prior-quarter GBV + 1/3 x two-quarter-prior GBV). Implied guide = revenue / (1 + cushion). Same-season EWM conversion has a two-year half-life and a 13 September cutoff, n=5/5/6/6. The common cushion is the median of eight prior observations, 1.7905%. Q3/Q4 GBV working inputs were originally component-derived and carry shared-input uncertainty; Q1 2027 GBV is an inherited, unvalidated assumption. Q2 2027 now uses explicit lagged-GBV conversion. There is no second RNPL haircut or extra FX/fee overlay. Precise-filed-GBV substitution is a separate sensitivity, not a silent rebasing.

Yahoo/LSEG revenue expectations were captured 13 September at 15:20:58Z: Q3 $4,744.88187m and Q4 $3,161.02149m, n=36 each. S&P Q4 $3,160m is dated 10 September; Zacks $3,200m is dated 11 September. DoltHub mirrors Zacks, while Yahoo/Alpha Vantage are channels of the same LSEG family; channels are not independent panels. With a common cushion, S&P and Zacks imply Q4 guide proxies of $3,104.4m and $3,143.7m. The sign versus our forecast changes with the panel. These are dated snapshots, not September 15 live refreshes.

Holding the chosen Yahoo/LSEG panel and other inputs fixed, Q4 conversion below 11.970980% (base 12.040367%) or Q3 GBV below $25,780.296790m (base $26,008.556m) puts our guide below the common-cushion proxy. These are algebraic zero-gap boundaries, not calibrated entry thresholds. Consensus revenue divided by our weighted GBV is a break-even conversion conditional on our GBV, not an observed Street conversion forecast.

## Forecast validation and uncertainty

The frozen candidate fails the promotion hurdle. Matched guide-target W1 is 2023Q1-2026Q2, n=12; W2 is 2024Q1-2026Q2, n=10 and nested. The earlier origin is target-quarter start minus 18 calendar days, aligned to the preceding eligible QQQ session. Candidate interval RMSE is $63.4m/$63.7m versus guide-growth B1 $74.3m/$60.8m. Raw candidate RMSE is $63.9m/$64.1m. The audit candidate uses the ex-COVID conversion variant, while the current four-quarter scenario uses inherited same-season EWM: the historical error figures do not directly validate this different variant and horizon. The midpoint +/-$0.5m convention is administrative, not the source endpoint interval or the full guide range. Frozen-panel reconstruction is not an archived live forecast; these are repeated earlier-origin first-guide tests, not empirical validation of a four-quarter path.

Shapley assigns interaction effects symmetrically among GBV, conversion and cushion. It does not identify causes. In W2, diagonal population variances sum to 7,759.7 and covariance contributes -3,662.7, leaving 4,097.0 (USDm squared). Do not assume components independent or add their RMSEs. With actual GBV substituted ex post while retaining early-origin conversion/cushion, raw guide RMSE falls to $36.4m/$38.7m. This oracle is unavailable before release and does not establish a trade. The $18m Q4 proxy gap is not a calibrated probability or a share-price target.

## Daily earnings legs and entry choices

All 23 held ledger events are displayed, reported quarters 2020Q4-2026Q2. Twenty have numeric first guides; 16 have admissible original pre-guide revenue consensus, and 15 also have a strictly prior-data cushion. W1/W2 event print windows begin 2023Q1/2024Q1, with proxy n=13/9, distinct from forecast target windows. Twelve primary tests cover two expectation proxies, two daily legs and three windows; all Holm-adjusted p-values are 1.00. This does not prove no effect; it supplies no established guide-surprise trading edge. Published-guide association is a post-release diagnostic.

The full held daily source contains 2,895 ticker-days (ABNB 1,444; QQQ 1,451), with 115 event-return tieouts. Preclose-to-nextopen includes release, call, overnight and premarket. Nextopen-to-close is the regular session. Simple returns compound within each security before subtracting QQQ; excess gap and excess session cannot themselves be compounded. Daily OHLC gives neither true call bars nor wick order, fills or stop execution. No held timestamped ABNB/QQQ intraday panel was found.

- Before release: use only the frozen early-origin forecast and contemporaneous expectations, bearing all intervening price risk. Reconstructed signal association is not archived strategy performance.
- At next open: the guide and call are public; the gap is no longer available to a new position. Evaluate only subsequent returns under an ex-ante rule and costs.
- During call: require consistently sourced timestamped ABNB and QQQ bars, exact publication/call-start/call-end clocks, timezone/DST and adjustment metadata. Held daily data do not support this entry test.

## Missing evidence and falsifiers

A short would require a dated direct guide-expectation panel, a GBV/conversion downside robust to credible vendor/cushion choices, and a preregistered net-of-cost executable entry test. RNPL cancellation/timing risk requires matched evidence before a numerical haircut. The case weakens if net realized growth and conversion hold through rollout laps, the issued guide matches the market's actual expectations, or a negative guide surprise fails to predict returns still available after entry.

Refresh the named expectation panel at decision time; validate future GBV assumptions; obtain intraday data only for a call-entry question. November 5 remains a project expected/planning date rather than a company future schedule verified in this audit. The latest SEC letter specifies the completed August 6 call at 17:00 New York. An inherited 2025Q3 L3 webcast/public-by proxy at 21:30Z differs from the [official 17:00 ET / 22:00Z schedule](https://investors.airbnb.com/press-releases/news-details/2025/Airbnb-to-Announce-Third-Quarter-2025-Results/default.aspx); it must not become a precise call boundary.

## Reproducible version trail

Model: integration_v2/model.json. Events: events_v1/run_v3. Forecast diagnostics: forecast_v1/results_v1. Independent arithmetic/source joins: sources_v1/review_v2 (314/314 checks, maximum absolute error 3.64e-12). Source inventory and dates: GE_SOURCE_RESULTS_v2.md. Exact input/output hashes accompany the PDF. The daily CSV's raw CRLF SHA differs from the retained LF-normalized hash only by line endings; both are documented in the source note. No new research fits or registry changes were performed by the memo builder.
