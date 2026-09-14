# B. What the options market prices for ABNB: 5 Nov implied move, skew, 12-month distribution, print base rates

Workstream B of the 12-13 Sep 2026 market-implied run. Brief: `docs/reverse_dcf/BRIEF.md`. Scripts: `analysis/src/reverse_dcf/B_pull_chains.py`, `B_options_implied.py`, `B_bloomberg_summary.py`, `B_tables.py`. Outputs: `data/processed/reverse_dcf/B/`. Live chain pulled 12 Sep 2026 04:49 UTC from yfinance, i.e. Friday 11 Sep closing quotes, spot $170.19 (ANCHOR). Bloomberg workbook built 4 Sep 2026 at spot $181.94 (licensed; read and summarised, derived numbers only). The two snapshots straddle the 8-10 Sep fall of 7.8%; section 6 says what changed.

Revised 12 Sep after the audit (`research/notes/reverse_dcf/audit_B.md`, pass with fixes). Changes: the realised print series is now reported as raw close-to-close alongside the QQQ-excess series the earlier draft mislabelled as raw; the headline 12-month quartiles are the lognormal ones with the skew-adjusted density as a sensitivity; the Bloomberg-derived CSVs no longer allow raw IV levels to be reconstructed; the event sd carries its quote uncertainty; JUDGEMENT sentences are labelled.

Labels: ANCHOR (from the brief), MEASURED (computed, source given), JUDGEMENT (mine, reason given).

## 1. The numbers

| Item | Value | Label | Source |
|---|---|---|---|
| First expiry after the 5 Nov print | 20 Nov 2026 (70 days); no 6 Nov weekly listed yet, so the expiry carries 15 post-print days | MEASURED | chain |
| 20 Nov $170 straddle | $23.05 = 13.5% of spot, the mid of a 12.0-15.0% market (the 170 put is quoted 8.85 / 12.30); smile-model ATM straddle 13.4% | MEASURED | `B_term_structure.csv` |
| 0.85 x that straddle | 11.5%: an upper bound on the print move, not the print move; the straddle covers 70 days of diffusion plus the print | MEASURED | same |
| 16 Oct $170 straddle (last liquid pre-print expiry, 35 days) | $13.15 = 7.7% of spot | MEASURED | same |
| ATM IV, own Black-76 from mids: 16 Oct / 20 Nov / 18 Dec / 15 Jan / 12M | 31.1 / 38.4 / 37.1 / 36.5 / 39.5% | MEASURED | same |
| Implied 5 Nov event standard deviation, pair 16 Oct vs 20 Nov | 9.9%; plus or minus 1 vol point on either leg gives 8.4-11.2% | MEASURED | `B_event_variance.csv`, `B_event_sd_leg_sensitivity.csv` |
| Same, least squares on the five single-print-or-fewer expiries | 9.2% (leave-one-out 8.0-10.1) | MEASURED | same |
| Same, all 11 maturities with five prints and a sloped background | 9.7% (LOO 9.1-10.3) | MEASURED | same |
| Same, two post-print expiries only (20 Nov vs 18 Dec) | 8.3% | MEASURED | same |
| Central implied event sd / expected absolute move | 9.5% (range 8.5-10.5) / 7.6% (6.8-8.4) | JUDGEMENT | middle of the identified 8.3-11.0, about 0.7 pt of sd per vol point of quote error |
| Same method on the 4 Sep Bloomberg chain (spot $181.94) | 9.8% pair, 10.0% LS, inside the noise of the 11 Sep reading | MEASURED | `B_bbg_event_fit_4sep_chain.csv` |
| Historical implied event sd, Bloomberg 30D IV crush at each of the 23 prints | mean 10.5%, median 10.4%, last eight 10.0% (an upper-bound style measure, section 3.3) | MEASURED | `B_bbg_print_implied_vs_realised_summary.csv` |
| Historical implied event sd, 30D vs 60D kink 45 days before each print (same horizon as today) | mean 8.5% | MEASURED | same |
| Realised print move, 23 prints, raw close-to-close (pre-print close to reaction close) | rms 8.9%, mean abs 7.1%, median abs 6.9%, 48% at 7%+, 35% at 10%+, 13 up / 10 down | MEASURED | `B_print_base_rates.csv` |
| Same, QQQ-excess (the series in `20_executable_returns.legacy_1d_pct` that earlier notes used) | rms 8.5%, mean abs 6.8%, median abs 5.1%, 48% at 7%+, 30% at 10%+, 11 up / 12 down | MEASURED | same |
| Realised rms over historical implied crush sd | 0.85 raw, 0.81 excess | MEASURED | same |
| 25-delta risk reversal, 20 Nov (call IV minus put IV) | -3.5 vol pts; own-method 90/110 skew 3.3 pts at 70 days (the Bloomberg 30D constant-maturity series has a 2021-26 median of 4.4 but reads about 1 pt above the own method, so the comparison is approximate) | MEASURED | `B_skew.csv`, `B_bbg_iv_history_summary.csv` |
| 10% OTM put vs 10% OTM call, 20 Nov | put $4.60, call $5.29; a flat smile would price the call at 1.36x the put, the market prices 1.15x, 15.5% below flat, i.e. the put is 1.18x richer relative to the call than under a flat smile | MEASURED | `B_skew.csv` |
| Risk-neutral P(above spot) at 20 Nov / P(above forward) | 0.49 / 0.48 | MEASURED | same |
| 12-month implied price, HEADLINE, lognormal at 39.5% ATM IV, forward $177.1: p10 / p25 / p50 / p75 / p90 | $99 / $126 / $164 / $214 / $272 | MEASURED, risk-neutral | `B_dist_12m_percentiles.csv` |
| Same, sensitivity, skew-adjusted RND: p25 / p50 / p75 | $124 / $167 / $217 (its p10 and p90 are extrapolated beyond quoted strikes and are not quoted) | MEASURED at the quartiles | same |
| 12M risk-neutral P(above $179.5 / $185 / $197.5 / $220) | 0.41-0.43 / 0.38-0.40 / 0.32-0.34 / 0.23-0.24 (lognormal to skew RND) | MEASURED, risk-neutral | `B_price_points_for_synthesis.csv` |
| 12M risk-neutral P(below $150 / $125) | 0.40-0.41 / 0.25-0.26 | MEASURED, risk-neutral | same |
| Bloomberg 30-day monthly straddles, print months: implied vs realised to expiry | 11.8% vs 13.3% (23 months, realised > implied in 57%) | MEASURED | `B_bbg_monthly_straddles_summary.csv` |
| Same, non-print months | 9.8% vs 9.5% (42 months, 38%) | MEASURED | same |

Reading. The market prices the 5 Nov print at an event standard deviation of about 9.5% (expected absolute move about 7.6%), which is the raw realised rms of the 23 prints (8.9%) plus about half a point, and about one point above where ABNB prints were priced at the same 55-day distance in the past (8.5%). The implied distribution gives a 46% chance of a 7%+ move and 29% of a 10%+ move against realised raw shares of 48% and 35%. JUDGEMENT: the print is priced at its own history, not above it. The skew: puts are 3.5 vol points richer than calls at 25 delta and a 10% OTM put costs 1.18x what a flat smile would charge relative to the call; the near-dated skew steepened by about 1.5 points on the 8-10 Sep fall (same method, 4 Sep vs 11 Sep) but sits inside ABNB's normal range. JUDGEMENT: the market is paying its usual premium for downside, not an unusual one. Over 12 months the risk-neutral distribution is wide (39.5% ATM IV, roughly the 40th percentile of ABNB's own 12M IV history, an approximate cross-method comparison): the interquartile range is $126-214 and the risk-neutral probability of being above the $179.5 mean sell-side target in a year is 0.41-0.43, above the $220 top target 0.23-0.24, below $150 0.40-0.41, below the $125 Morgan Stanley target 0.25-0.26. None of those is a real-world probability (section 9).

## 2. Data and cleaning

Chain. 15 listed expiries, 800 contracts, pulled 12 Sep 2026 04:49 UTC (`raw_chain_20260912T044930Z.csv`, `B_pull_meta.json`). Quotes are Friday 11 Sep closing bid/ask; bid and ask, not last trade, are used throughout, so a last trade earlier in the week (several 20 Nov strikes last traded 9-10 Sep) does not matter. Filters for anything used numerically: two-sided quote (bid > 0, ask >= bid), relative spread <= 60%, mid >= $0.10, |ln(K/F)| <= 0.45, and out-of-the-money only for the smile (calls above the forward, puts below). 197 quotes survive across 15 expiries (`B_chain_clean.csv`, column `usable`). The 23 Oct weekly has no usable quote (2 two-sided calls, 5 puts, open interest 40) and is excluded; 25 Sep and 2 Oct have three each and are not used in fits. The 20 Nov expiry has 12 usable OTM quotes and 4,581 open interest; 16 Oct has 10 and 14,709; Jun 2027 has 22 and 16,813.

Forward and put-call parity. For each expiry the forward is the median of K + (C - P) e^{rT} across near-ATM strikes with both sides quoted (`B_forwards.csv`). The parity forward sits 0.06-0.19% below spot carry at every expiry to Mar 2027 (a small negative basis consistent with borrow cost or the after-close quotes) and 0.3-0.6% above at the LEAPS, where spreads are wide. Two checks were run. The weak one: the spot-carry forward lies inside the bid-ask parity band at all 118 strike-expiry pairs (`B_parity_check.csv`), but that band is 0.5-6% of spot wide (median 2.5%), so passing it is necessary, not sufficient. The informative one: the within-expiry dispersion of strike-by-strike mid forwards is 0.25-0.8% of spot to Jan 2027 and 0.9-1.5% at Mar 2027 and the LEAPS, which is the noise floor for those expiries. At 20 Nov the 170 put is quoted 8.85 / 12.30 (33% relative spread) and puts that strike's forward 0.43% above the median, and the 170 call and put mid IVs differ by 2.5 points (40.2 vs 37.7); this is why the headline straddle is quoted as a mid on a 12.0-15.0% market and why the smile at the forward (13.4%) rather than the single-strike straddle is used for anything downstream.

Implied volatilities. yfinance's `impliedVolatility` column is not used numerically: on the 197 usable quotes it sits 1.9 vol points above my Black-76 mid IV on average with a standard deviation of 3.5 points (range -6.4 to +8.8), and it disagrees between a call and a put at the same strike by several points, which is impossible for a consistent forward. Every IV here is recomputed from mids on the parity forward with r = 4.0% (the 3-month T-bill ^IRX closed 3.91% on 11 Sep; the brief says 4.0-4.2%; moving r by 0.5 pt moves ATM IV by 0.02-0.05 pt) and no dividend. The ATM IV per expiry is a quadratic smile in log-moneyness fitted by weighted least squares to the OTM IVs and read at the forward; the fit RMSE is 0.5-0.7 vol points at the expiries that matter (`B_term_structure.csv`, `smile_rmse_volpts`).

Term structure, 11 Sep close (own IV; straddle = same-strike $170 call + put, mid):

| Expiry | Days | Prints inside | Forward | ATM IV | Straddle % spot (bid / mid / ask) | Usable OTM quotes |
|---|---|---|---|---|---|---|
| 18 Sep | 7 | 0 | 170.04 | 28.9% | 2.6 / 3.2 / 3.8 | 6 |
| 9 Oct | 28 | 0 | 170.55 | 30.6% | 5.0 / 6.8 / 8.5 | 4 |
| 16 Oct | 35 | 0 | 170.75 | 31.1% | 7.5 / 7.7 / 8.0 | 10 |
| 23 Oct | 42 | 0 | 171.02 | n/a | 9.5 / 11.4 / 13.3 (185 strike, unusable) | 0 |
| 20 Nov | 70 | 1 | 171.19 | 38.4% | 12.0 / 13.5 / 15.0 | 12 |
| 18 Dec | 98 | 1 | 171.76 | 37.1% | 14.7 / 15.5 / 16.2 | 16 |
| 15 Jan 27 | 126 | 1 | 172.41 | 36.5% | 16.4 / 17.6 / 18.9 | 19 |
| 19 Mar 27 | 189 | 2 | 173.54 | 38.3% | 19.9 / 21.6 / 23.3 | 20 |
| 17 Jun 27 | 279 | 3 | 175.52 | 39.3% | 25.9 / 27.4 / 28.8 | 22 |
| 17 Sep 27 | 371 | 4 | 177.71 | 39.1% | 29.4 / 31.4 / 33.5 | 18 |
| 17 Dec 27 | 462 | 5 | 180.05 | 39.7% | 33.2 / 35.0 / 36.7 | 22 |
| 21 Jan 28 | 497 | 5 | 180.66 | 39.6% | 33.8 / 36.1 / 38.5 | 25 |

"Prints inside" counts the 5 Nov 2026 print (Zacks expected date, not company-confirmed) and pattern-estimated prints on about 11 Feb, 6 May, 5 Aug and 4 Nov 2027. The kink is visible in the raw data: ATM IV steps from 31.1% at 16 Oct to 38.4% at 20 Nov and then falls back to 36.5% by January as the same event variance is spread over more days.

Bloomberg workbook (`ABNB_Options_Bloomberg_Pull (1).xlsx`, 4 Sep 2026). Sheets: README and Inputs (field dictionary, spot 181.94); Underlying_Hist (daily close, Bloomberg call/put implied vol, 30D and 90D realised vol, put-call volume and open-interest ratios, 10 Dec 2020 to 4 Sep 2026, 1,436 days); IV_Surface_Hist (daily constant-maturity ATM IV at 30D, 60D, 6M, 12M, the 90D column is empty, plus 30D IV at 90, 95, 105 and 110% moneyness); Current_Chain (full chain at 21:28 UTC on 4 Sep, 1,255 contracts with bid, ask, IV and Greeks); Hist_Chain_AsOf (chain on 17 Dec 2021, not used); Contract_Hist (six example contracts, not used); Monthly_Straddles (for each third-Friday expiry Jan 2021 to Sep 2026, the ATM straddle bought about 30 calendar days before expiry, implied move = straddle / spot, realised move = |spot at expiry / spot at entry - 1|; 65 of 68 months have prices, Apr 2022, Apr 2025 and Jun 2026 do not). The 4 Sep chain was re-priced with the same Black-76 and smile method as the live chain so the two snapshots are comparable (`B_bbg_chain_4sep_term_structure.csv`). Licensing: the CSVs under `data/processed/reverse_dcf/B/` carry fits, averages, ratios and per-print derived sds only; the per-print file no longer carries the IV crush in vol points (with the sd it would have reconstructed the raw levels) and the per-month straddle file carries only the realised/implied ratio.

Prices. Daily OHLC refreshed to 11 Sep 2026 (`B_prices_daily.csv`): 4 Sep 181.94, 8 Sep 174.54, 9 Sep 169.63, 10 Sep 167.65, 11 Sep 170.19.

## 3. Implied move for the 5 Nov print

### 3.1 Straddles

The 20 Nov $170 straddle costs 13.5% of spot at mid, on a 12.0-15.0% market. It is not an earnings straddle: the expiry is 70 days out and contains 35 days of ordinary diffusion before the print and 15 after it. The 16 Oct $170 straddle, which contains no print, costs 7.7%. The usual "implied move = 0.85 x straddle" rule applies to a straddle expiring the day after the print; applied to 20 Nov it gives 11.5%, which is an upper bound on the print move and must not be quoted as the print move. There is no listed expiry that isolates the print: weeklies currently run to 23 Oct, and weeklies list about six weeks ahead, so the 6 Nov weekly should appear in the last week of September. Re-run `B_pull_chains.py` and `B_options_implied.py` then; the 6 Nov straddle will give the print move directly.

### 3.2 Term-structure method, and a correction to the formula in the brief

Model: for expiry i with time T_i and ATM IV sigma_i, sigma_i^2 T_i = b T_i + E n_i, where b is the annualised background (diffusive) variance, E is the variance of the one-day print return and n_i is the number of prints inside expiry i. For one pre-print expiry (n = 0) and one post-print expiry (n = 1):

E = T_post (sigma_post^2 - sigma_pre^2).

The brief's formula, T_after sigma_after^2 - T_before sigma_before^2, is the forward variance between the two expiry dates, which equals E + b (T_after - T_before): it includes the 35 days of ordinary diffusion between 16 Oct and 20 Nov. On today's quotes that forward variance is 0.0190, which would be called a 13.8% event sd; subtracting the diffusion term 0.0093 (b = 31.1%^2 times 35/365) leaves E = 0.0098, an event sd of 9.9%. The rewritten `analysis/src/abnb_options_ledger.py` (6 Sep) fits the correct model by least squares; its maths is right and its estimator was reused here with two changes: the ATM IV is my own from mids rather than yfinance's, and expiries with more than one print are allowed with n_i > 1 rather than dropped.

Identification assumption, stated plainly: b is the same across the maturities used. Everything below depends on it. The sensitivity table (`B_event_sensitivity.csv`) holds the 20 Nov quote fixed and sweeps the assumed background:

| Assumed background vol | 29% | 30% | 31% | 32% | 33% | 34% | 35% | 36% | 37% | 38% | 39%+ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Implied event sd | 11.0% | 10.5% | 9.9% | 9.3% | 8.6% | 7.8% | 6.9% | 5.9% | 4.5% | 2.5% | none |

The pre-print expiries with usable quotes have ATM IVs of 28.9% (7 days), 30.6% (28 days) and 31.1% (35 days), so the directly observed background range gives 9.9-11.0%. The post-print expiries imply a slightly higher background: if E were 9.5% sd, the 15 Jan IV of 36.5% implies b = 32.7%. The term structure of the background is mildly upward sloping, which the constant-b pair estimator ignores; allowing b to slope with T (the `slope_bg` specification) gives 9.7%.

Quote uncertainty on top of that. The pair estimate moves by about 0.7 pt of event sd per 1 vol point of either leg's ATM IV (dE/dsigma_post = 2 T_post sigma_post = 0.147 per unit of vol, dE/dsigma_pre = -0.119). The smile fit RMSE is 0.5-0.7 vol points and the 170-strike call and put disagree by 2.5 points, so plus or minus 1 point on either leg is a fair error bar: it maps the 9.9% pair estimate onto 8.4-11.2% (`B_event_sd_leg_sensitivity.csv`, nine combinations), which is the same width as the leave-one-out range of the five-expiry fit (8.0-10.1).

Results (`B_event_variance.csv`):

| Specification | Maturities | Background vol | Event sd | Expected abs move | Range |
|---|---|---|---|---|---|
| Pair 16 Oct (pre) vs 20 Nov (post) | 2 | 31.1% | 9.9% | 7.9% | 8.4-11.2 (plus or minus 1 vol pt per leg) |
| Pair 9 Oct (pre) vs 20 Nov | 2 | 30.6% | 10.2% | 8.1% | |
| Pair 16 Oct vs 18 Dec | 2 | 31.1% | 10.4% | 8.3% | |
| LS, 18 Sep, 16 Oct, 20 Nov, 18 Dec, 15 Jan (one print max) | 5 | 32.7% | 9.2% | 7.3% | LOO 8.0-10.1 |
| LS, all 11 usable maturities, constant b, five prints | 11 | 32.9% | 11.0% | 8.8% | LOO 9.6-12.6 |
| LS, all 11, b allowed to slope with T | 11 | 31.9% at T = 0 | 9.7% | 7.8% | LOO 9.1-10.3 |
| Pair 20 Nov vs 18 Dec (both contain the print) | 2 | 33.4% | 8.3% | 6.6% | |

All identified specifications land between 8.3% and 11.0%, with the better-conditioned ones (the one-print LS and the sloped-background LS) at 9.2-9.7%. JUDGEMENT: the central reading is 9.5% sd with a range of 8.5-10.5, and 7.6% (6.8-8.4) expected absolute move, quoted as a range and not a point. Two things inflate it relative to the pure day-1 jump: the 20 Nov expiry holds 15 post-print sessions, and realised volatility after ABNB prints is elevated (the 09 note documents the post-print drift), so some of that excess lands in E; and the constant-b estimators lean on the lowest-IV short expiries for the background. Both push the same way, so 9.5% is if anything a touch high for the day-1 move alone.

On the 4 Sep Bloomberg chain, re-priced with the same method at spot $181.94, the 16 Oct vs 20 Nov pair gives 9.8% and the one-print LS 10.0% (`B_bbg_event_fit_4sep_chain.csv`), inside the plus or minus 1 pt noise of the 11 Sep reading. The constant-maturity surface on 4 Sep (30D and 60D both pre-print; 6M with two prints; 12M with four) fitted with the same model gives 9.0% per print, and the 60D vs 6M pair 6.5%, the 30D vs 6M pair 9.8% (`B_bbg_event_fit_4sep_surface.csv`). The 6 Sep estimate of 2.3% in `09_implied_move_live.json` came from the 23 Oct weekly as the pre-print leg, whose yfinance IV was 37.8% on a chain with open interest of 40; that leg was never usable and the 23 Oct expiry is excluded here for the same reason.

### 3.3 How the market has priced ABNB prints before

Two historical measures from the Bloomberg surface, 23 prints Feb 2021 to Aug 2026 (`B_bbg_print_implied_vs_realised.csv`). The realised series is the raw close-to-close move (pre-print close to reaction-day close, `entry_postclose_px / pre_close - 1` in `20_executable_returns.csv`), because that is what an option on ABNB pays on; the QQQ-excess version (`legacy_1d_pct`, the series earlier notes used) is reported alongside.

IV crush: the 30D ATM IV at the print-date close contains the event, the 30D ATM IV at the reaction-date close does not; E = (30/365)(sigma_before^2 - sigma_after^2). This attributes the whole reaction-day drop in 30D IV to the event and treats the constant-maturity window as exactly 30 days, so it is an upper-bound style measure. Mean implied event sd 10.5%, median 10.4%, last eight prints 10.0%, range 5.5-14.6%. Realised rms over the same 23 prints 8.9% raw (8.5% excess), mean absolute 7.1% (6.8%). Ratio of realised rms to mean implied sd 0.85 raw (0.81 excess). Realised absolute raw move exceeded the implied expected absolute move in 39% of prints and exceeded the implied sd in 30%. The correlation between the implied sd and the realised absolute raw move across prints is 0.05 (-0.03 on excess): the option market's pre-print pricing has had no information about the size of the coming move, which matches the 09 note's finding that the size is unforecastable from its own history.

Kink at 45 days: 30D vs 60D IV on the nearest date 45 days before each print, when the print sits inside the 60D window but outside the 30D one; E = (60/365)(sigma_60^2 - sigma_30^2). Mean 8.5%, positive in 23 of 23. JUDGEMENT: this is the measure comparable with today's reading (today is 55 days before the print and the same two-expiry construction is used); the current 9.2-9.9% is about one point above the historical average at the same distance, and the raw realised rms over the kink measure is 1.05.

Implied distribution of the print move against the realised one (`B_implied_vs_realised_print.csv`; implied shares assume a normal day-1 return with the stated sd):

| Source | Event sd | P(abs move >= 5%) | >= 7% | >= 10% | >= 15% |
|---|---|---|---|---|---|
| Live, pair 16 Oct / 20 Nov | 9.9% | 0.61 | 0.48 | 0.31 | 0.13 |
| Live, LS one-print expiries | 9.2% | 0.59 | 0.45 | 0.28 | 0.10 |
| Live, two post-print expiries | 8.3% | 0.55 | 0.40 | 0.23 | 0.07 |
| Central reading (JUDGEMENT) | 9.5% | 0.60 | 0.46 | 0.29 | 0.11 |
| History, mean IV crush | 10.5% | 0.63 | 0.50 | 0.34 | 0.15 |
| History, mean 45-day kink | 8.5% | 0.56 | 0.41 | 0.24 | 0.08 |
| Realised, 23 prints, raw close-to-close | rms 8.9% | 0.52 | 0.48 | 0.35 | 0.04 |
| Realised, 23 prints, QQQ-excess | rms 8.5% | 0.52 | 0.48 | 0.30 | 0.04 |

The live pricing reproduces the realised frequency of 7%+ moves and sits 6 points under the realised frequency of 10%+ raw moves, and overstates the 15%+ tail (realised 1 of 23, the +17.4% of Aug 2026; a normal at 9.5% sd gives 11%). The realised distribution is fat in the middle and thin in the extreme tail relative to the implied normal.

Monthly straddles (Bloomberg sheet, 30-day ATM straddles, realised move measured to expiry rather than on day 1; `B_bbg_monthly_straddles_summary.csv`, `B_bbg_print_month_straddles.csv`): all 65 months, implied 10.5% vs realised 10.8% (the sheet's own 10.4 vs 10.7 headline); print months (23), implied 11.8% vs realised 13.3%, realised exceeded implied in 57%, average realised/implied 1.16; non-print months (42), implied 9.8% vs realised 9.5%, 38%; since 2024, print months 10.5 vs 12.5 and non-print months 7.4 vs 6.2; the five November print months 11.6 vs 9.7. Subtracting the non-print-month implied variance from the print-month implied variance gives an implied event sd of 7.4% over the whole sample and 9.3% since 2024. So on a 30-day horizon buying the print month has paid (the realised to-expiry move runs above implied) while buying non-print months has not, and at the same time the one-day IV crush says the market paid about 15% too much in sd terms for the day-1 jump. Both are true: the extra realised variance in print months has come in the weeks after the print, not on the day, which is the post-print drift the 09 note documents.

## 4. Skew and asymmetry

`B_skew.csv`. Strikes and IVs for 25 delta come from the fitted smile; the 10% OTM prices are Black-76 on the smile at exactly 0.9 and 1.1 times spot, with the nearest listed strikes (155 and 185) alongside.

| Expiry | Days | ATM IV | 25d put K / IV | 25d call K / IV | RR25 (call - put) | 90/110 skew, own | 10% call / 10% put, market | Same, flat smile | Ratio vs flat | P(above spot), RND |
|---|---|---|---|---|---|---|---|---|---|---|
| 16 Oct | 35 | 31.1% | 160 / 32.6% | 183 / 30.6% | -2.0 | 3.5 | 1.11 | 1.54 | 0.72 | 0.50 |
| 20 Nov | 70 | 38.4% | 154 / 40.4% | 193 / 36.9% | -3.5 | 3.3 | 1.15 | 1.36 | 0.85 | 0.49 |
| 18 Dec | 98 | 37.1% | 153 / 39.2% | 198 / 35.6% | -3.6 | 3.1 | 1.20 | 1.40 | 0.86 | 0.50 |
| 19 Mar 27 | 189 | 38.3% | 149 / 40.3% | 215 / 37.1% | -3.2 | 2.1 | 1.32 | 1.44 | 0.92 | 0.48 |
| 17 Jun 27 | 279 | 39.3% | 147 / 40.8% | 231 / 37.2% | -3.5 | 1.7 | 1.40 | 1.49 | 0.94 | 0.49 |
| 17 Sep 27 | 371 | 39.1% | 146 / 41.1% | 248 / 38.1% | -3.0 | 1.8 | 1.46 | 1.56 | 0.94 | 0.47 |
| 21 Jan 28 | 497 | 39.6% | 147 / 41.2% | 267 / 37.4% | -3.8 | 1.4 | 1.55 | 1.63 | 0.95 | 0.47 |

What it says. The dollar ratio of a 10% OTM call to a 10% OTM put is above 1 at every expiry, but that is what a symmetric lognormal produces: strikes 10% either side of spot in dollars sit 9.4% above and 11.1% below the forward in log terms, so the benchmark is mostly strike geometry, and the skew is the shortfall against it. At 20 Nov the market prices the call at 1.15x the put where a flat smile would give 1.36x: the market ratio is 15.5% below flat, equivalently the put is 1.18x richer relative to the call than symmetric pricing, and the 25-delta put trades 3.5 vol points over the 25-delta call. The slope is steepest in the short expiries (own-method 90/110 skew 3.1-3.5 points to December, 1.4-2.1 points beyond March), which is the normal shape. Against ABNB's own history the comparison is approximate because it is cross-method: the Bloomberg 30D constant-maturity 90/110 skew has a 2021-26 median of 4.4 points (p25 2.4, p75 6.4) and read 4.5 on 4 Sep (51st percentile), while the own method on the same 4 Sep chain gave 3.0-3.7 at the 28-35 day expiries, about 1 point below Bloomberg. Mapped onto Bloomberg's scale the 11 Sep near-dated skew is roughly 4.5-5.0, around the 55th-60th percentile. The like-for-like change is own method 4 Sep to 11 Sep: 16 Oct 2.8 to 3.5, 20 Nov 1.8 to 3.3, so the fall to $170 steepened the near-dated skew by about 1.5 points. Risk-neutral probabilities of finishing above spot are 0.49-0.50 to December and 0.47 at the LEAPS; the asymmetry is in the tails, not the centre. JUDGEMENT: the market is paying its usual premium for ABNB downside into the print, slightly more than a week ago and nothing like a crowded hedge; the 1.18x figure is that usual premium, not evidence of positioning.

## 5. Twelve-month implied distribution

Expiry choice. 17 Sep 2027 is exactly 12 months out but thin (18 usable quotes, open interest 2,374, most of it in two strikes). The 12-month point is therefore built by interpolating total variance strike-by-strike between 17 Jun 2027 (279 days, 22 usable quotes, OI 16,813) and 17 Dec 2027 (462 days, 22 quotes, OI 10,649); the direct Sep 2027 lognormal is reported as a check and differs from the interpolated one by less than $1 at every percentile. Forward for 11 Sep 2027 at r = 4.0%: $177.14. Interpolated ATM IV 39.5%, 10%-down IV 40.3%, 10%-up IV 38.8%.

Methods (`B_dist_12m_percentiles.csv`). (a) Lognormal at the ATM IV: two numbers (39.5% and $177.1) anyone can reproduce, mean equal to the forward by construction. (b) Two-sided lognormal: the 10%-down IV below the forward, the 10%-up IV above. (c) Skew-adjusted risk-neutral density: Breeden-Litzenberger second derivative of the Black-76 call price curve generated by the fitted smile, flat extrapolation beyond the quoted strike range (Jun 2027 quotes run $115-250, log-moneyness -0.42 to +0.35), clipped negative mass 1.7%, density mean $175.7 against the $177.1 forward (a 0.8% shortfall from the clipping and renormalising). (d) Breeden-Litzenberger directly on observed mids at Jun 2027 and Jan 2028, as a check on (c).

| Method | p5 | p10 | p25 | p50 | p75 | p90 | p95 |
|---|---|---|---|---|---|---|---|
| Lognormal, 39.5% (HEADLINE) | 86 | 99 | 126 | 164 | 214 | 272 | 314 |
| Lognormal, Sep 2027 direct, 39.1% | 86 | 99 | 126 | 165 | 215 | 272 | 314 |
| Two-sided lognormal | 84 | 98 | 125 | 164 | 214 | 270 | 311 |
| Skew-adjusted RND (sensitivity; p5, p10, p90, p95 extrapolated, do not quote) | 81 | 94 | 124 | 167 | 217 | 264 | 302 |

The headline is the lognormal (JUDGEMENT, following the audit): at the quartiles the two methods agree within $2-4, which is below the noise from the LEAPS forward (0.5-1.5% of spot) and bid-ask (8-15% of mid), and the skew RND's tails come from the extrapolated part of the smile that the model-free check cannot validate. The direct Breeden-Litzenberger on raw mids is not clean: at Jun 2027 the second differences of the spline produce negative density mass of 14% and at Jan 2028 of 30%, because LEAPS spreads are 8-15% of mid. Where the direct density is well behaved it agrees with the smile model within $5 at p25, p50 and p75 (Jun 2027: $126 / $165 / $206 direct against $130 / $168 / $211 model; `B_bl_check_2027-06-17.csv`), and it disagrees at p10 where the direct version has too little lower-tail mass. The skew RND respects the measured -3.0 to -3.8 point risk reversals at the long expiries, which is real, but it moves the quartiles by less than the method noise and P(below $150) by 0.01.

Three properties of these numbers. They are risk-neutral: the median is below spot ($164 lognormal, $167 skew RND, against $170.19) because the risk-neutral drift is the 4% carry less half the variance (39.5% vol costs 7.8% of median per year); this is mechanical, not a bearish reading, and P(above spot in a year) is 0.46-0.48. They are wide because ABNB's implied vol is high in absolute terms, although ordinary for ABNB: 39.5% is about the 40th percentile of the stock's own 12M IV history (Bloomberg series, median 41.6%, p25 37.3%; the own method read 0.4-0.8 pt above Bloomberg's 12M on 4 Sep, so the percentile is approximate) and matches 2026 realised vol of 39%. And they carry no view on direction beyond the skew: the market assigns 0.40-0.41 to being below $150 and 0.41-0.43 to being above $179.5.

Probabilities at the brief's price points (`B_price_points_for_synthesis.csv`; the 20 Nov column is the risk-neutral distribution at the print expiry, 70 days; all risk-neutral):

| Price | Brief label | vs spot | P(above) 20 Nov | P(above) 12M, lognormal | P(above) 12M, skew RND |
|---|---|---|---|---|---|
| $125 | Morgan Stanley target | -26.6% | 0.95 | 0.75 | 0.74 |
| $150 | bear tape | -11.9% | 0.75 | 0.59 | 0.60 |
| $165 | p25 target | -3.0% | 0.57 | 0.49 | 0.51 |
| $170.19 | price | 0 | 0.49 | 0.46 | 0.48 |
| $179.5 | mean target | +5.5% | 0.37 | 0.41 | 0.43 |
| $185 | median yfinance target | +8.7% | 0.30 | 0.38 | 0.40 |
| $197.5 | p75 target | +16.0% | 0.17 | 0.32 | 0.34 |
| $220 | top target | +29.3% | 0.05 | 0.23 | 0.24 |
| $126 | options 12M p25, lognormal (headline) | -26.3% | 0.95 | 0.75 | 0.74 |
| $164 | options 12M p50, lognormal (headline) | -3.8% | 0.58 | 0.50 | 0.52 |
| $214 | options 12M p75, lognormal (headline) | +25.7% | 0.07 | 0.25 | 0.26 |
| $124 | options 12M p25, skew RND (sensitivity) | -27.3% | 0.96 | 0.76 | 0.75 |
| $167 | options 12M p50, skew RND (sensitivity) | -2.0% | 0.54 | 0.48 | 0.50 |
| $217 | options 12M p75, skew RND (sensitivity) | +27.6% | 0.06 | 0.24 | 0.25 |

## 6. What changed between 4 Sep (Bloomberg) and 11 Sep (yfinance)

Same method on both chains (own Black-76 IV on the parity forward, quadratic smile, same-strike straddle nearest spot). Spot fell from $181.94 to $170.19 (-6.5%) with no company news around the 8 Sep Communacopia fireside (ANCHOR).

| Expiry | ATM IV 4 Sep | ATM IV 11 Sep | Straddle % spot 4 Sep | 11 Sep | 90/110 skew 4 Sep | 11 Sep |
|---|---|---|---|---|---|---|
| 16 Oct | 29.8% (42d) | 31.1% (35d) | 8.2 | 7.7 | 2.8 | 3.5 |
| 20 Nov | 36.6% | 38.4% | 13.4 | 13.5 | 1.8 | 3.3 |
| 18 Dec | 36.0% | 37.1% | 15.7 | 15.5 | 1.8 | 3.1 |
| 15 Jan 27 | 35.5% | 36.5% | 17.0 | 17.6 | 1.7 | |
| 17 Jun 27 | 38.3% | 39.3% | 27.1 | 27.4 | 1.7 | 1.7 |
| 17 Sep 27 | 38.7% | 39.1% | 31.2 | 31.4 | 1.4 | 1.8 |
| 21 Jan 28 | 39.2% | 39.6% | 36.7 | 36.1 | 1.4 | 1.4 |
| Event sd, 16 Oct vs 20 Nov pair | 9.8% | 9.9% | | | | |
| Event sd, one-print LS | 10.0% | 9.2% | | | | |

The fall added 1.0-1.8 vol points to every expiry out to January and 0.4-1.0 points to the LEAPS, steepened the near-dated 90/110 skew by about 1.5 points, and left the straddles as a share of the (lower) spot essentially unchanged. The implied event variance for the print is unchanged to within its noise: 9.8-10.0% before, 9.2-9.9% after, against a plus or minus 1 pt error bar on each. JUDGEMENT: the market re-priced the level and the near-term downside tail, not the print. The 6 Sep yfinance ledger (`abnb_options_ledger.csv`) showed 20 Nov ATM IV 38.2% and straddle 13.4% at spot $181.94; with yfinance's IV running about 2 points above the Black-76 mid IV, that is consistent with the 36.6% measured on the Bloomberg chain two days earlier.

## 7. Historical print reactions (base rates)

`B_print_moves.csv`, `B_print_base_rates.csv`. Two series per print, both from `20_executable_returns.csv`: `raw_cc_1d_pct` = `entry_postclose_px / pre_close - 1`, the raw pre-print-close to reaction-close move, which is what an option pays on; and `excess_cc_1d_pct` = `legacy_1d_pct`, which the WS20 note defines as the day-1 return less QQQ. The earlier draft of this note called the excess series "close-to-close"; that was wrong. Reconciliation with the older `abnb_earnings_reactions.csv` (`B_reconcile_reaction_files.csv`): raw matches its `abnb_1d_pct` to 0.05 pt on every print, excess matches its `excess_1d_pct` to 0.04 pt, and raw minus excess equals its `qqq_1d_pct` to 0.05 pt. The 7.07% mean absolute move quoted in the 09 note is the raw series; 2Q26 is +17.4% raw and +16.3% excess (QQQ +1.2% that day), and the brief's +17.4% anchor is raw. The overnight gap (close to next open) and the executable next-open-to-close return are also carried.

| Sample | n | Series | Mean abs | Median abs | RMS | Mean signed | Share 7%+ | Share 10%+ | Up / down | Mean up | Mean down | p25 | p75 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| All 23 prints | 23 | raw | 7.1% | 6.9% | 8.9% | +1.2% | 48% | 35% | 13 / 10 | +7.3% | -6.8% | -5.1% | +6.2% |
| | | excess | 6.8% | 5.1% | 8.5% | +0.5% | 48% | 30% | 11 / 12 | +7.7% | -6.0% | -6.1% | +4.4% |
| Last 8 | 8 | raw | 6.9% | 6.3% | 9.2% | +2.7% | 50% | 25% | 6 / 2 | +6.4% | -8.3% | -1.8% | +7.1% |
| | | excess | 6.8% | 6.4% | 8.9% | +2.0% | 50% | 25% | 4 / 4 | +8.8% | -4.8% | -3.3% | +6.8% |
| Since 2024 | 11 | raw | 7.0% | 6.9% | 9.1% | 0.0% | 45% | 27% | 6 / 5 | +6.4% | -7.7% | -7.5% | +2.8% |
| | | excess | 7.0% | 7.1% | 8.7% | -0.6% | 55% | 27% | 4 / 7 | +8.8% | -5.9% | -7.7% | +2.5% |
| Q3 prints (Nov), 2021-25 | 5 | raw | 7.7% | 8.7% | 9.3% | -2.4% | 60% | 40% | 2 / 3 | +6.6% | -8.5% | | |
| Revenue beat above median (2.2%) | 12 | raw | 7.7% | 7.3% | 9.4% | +4.2% | 50% | 42% | 9 / 3 | +7.9% | -6.9% | +0.4% | +13.1% |
| Revenue beat below median | 11 | raw | 6.4% | 4.7% | 8.4% | -2.2% | 45% | 27% | 4 / 7 | +5.8% | -6.7% | -8.3% | +0.7% |
| Nights yoy accelerated in the reported quarter (> 0) | 8 | raw | 8.1% | 6.2% | 10.0% | +3.9% | 50% | 38% | 6 / 2 | +8.0% | -8.4% | -0.6% | +9.4% |
| | | excess | 7.3% | 4.8% | 8.9% | +3.5% | 38% | 25% | 6 / 2 | +7.2% | -7.6% | -0.8% | +6.8% |
| Nights yoy decelerated (<= 0) | 11 | raw | 6.0% | 6.9% | 7.8% | -3.3% | 45% | 27% | 3 / 8 | +5.0% | -6.4% | -8.3% | +0.1% |
| | | excess | 6.4% | 7.1% | 7.8% | -4.1% | 55% | 27% | 1 / 10 | +12.6% | -5.7% | -8.6% | -1.0% |
| Next-quarter revenue guide above street | 11 | raw | 5.4% | 3.7% | 7.7% | +3.3% | 36% | 18% | 7 / 4 | +6.8% | -2.9% | -0.8% | +6.2% |
| Guide below street | 8 | raw | 9.0% | 9.8% | 10.1% | -1.8% | 63% | 50% | 3 / 5 | +9.5% | -8.6% | -9.2% | +4.0% |
| Nights beat | 12 | raw | 5.1% | 4.3% | 6.5% | +0.4% | 33% | 8% | 7 / 5 | | | | |
| Nights miss or in line | 6 | raw | 5.4% | 2.4% | 7.8% | +4.9% | 33% | 33% | 4 / 2 | | | | |

Last eight prints, raw (excess in brackets): 3Q24 -8.7% (-8.8), 4Q24 +14.5% (+14.0), 1Q25 +1.0% (-0.5), 2Q25 -8.0% (-8.4), 3Q25 +0.3% (+0.6), 4Q25 +4.6% (+4.4), 1Q26 +0.7% (-1.6), 2Q26 +17.4% (+16.3). The mean absolute gap (close to next open) is 6.0% and the mean absolute open-to-close 3.2%: most of the move is in the gap, and the executable next-open entry captures on average less than half of the close-to-close move.

Conditional splits. The size of the move does not depend much on the direction of the news (raw mean absolute 7.7% vs 6.4% by revenue-surprise half, 8.1% vs 6.0% by nights acceleration), but the sign does. On raw returns, prints where nights growth accelerated year on year went up 6 of 8 (mean +3.9%) and prints where it decelerated went down 8 of 11 (mean -3.3%). On QQQ-excess returns the decelerating bucket is 1 up / 10 down: the difference is 1Q25 (raw +1.0%) and 1Q26 (raw +0.7%), both small up days on which QQQ rose 1.5-2.3%, so the lopsided excess count is driven by the choice of return series rather than by the threshold. Workstream C codes the same column with a plus or minus 0.25 point dead band, which moves 1Q22 (+0.01 pt, raw +7.7%) and 3Q24 (-0.21 pt, raw -8.7%) into a flat bucket; on that coding the split is 5 / 2 accelerating, 1 / 1 flat, 3 / 7 decelerating raw (1 / 9 excess). The one large raw up-move in the decelerating bucket is 4Q22 (+13.4%, first profitable full year and a Q1 guide above the street). Guides below the street produce larger moves (9.0% vs 5.4% raw mean absolute, 63% vs 36% at 7%+). These are base rates on n of 8-12, not a model; workstream C owns the reaction function. The conditional base rate the brief asks for "given a revenue beat" is weak because ABNB has beaten revenue consensus at 22 of 23 prints (the exception is 2Q22), so the split is above versus below the median beat.

Against the implied move. The market's 9.5% event sd (7.6% expected absolute move) sits above the realised raw mean absolute move (7.1%) and median (6.9%) and about half a point above the realised raw rms (8.9%). On the frequency of large moves it is close: implied 46% chance of 7%+ against 48% realised, 29% of 10%+ against 35%. The realised distribution is bimodal (seven of 23 raw moves were under 2%, eleven were over 7%), so the mean and median understate what a straddle buyer faces and the rms is the fair comparison. By that comparison the print is priced about half a point of sd above its raw history, which is less than ABNB's own historical pre-print premium (IV crush 10.5% against realised raw rms 8.9%, ratio 0.85) and about a point above the same-horizon historical measure (8.5% at 45 days before past prints against 9.2-9.9% today).

## 8. What can and cannot be identified

Can. The straddle prices and ATM IVs are quoted, two-sided, parity-consistent numbers. The event variance is identified under the flat-background assumption and its sensitivity to that assumption and to quote error is tabulated; four independent specifications agree to within 8.3-11.0%, and the 4 Sep chain gives the same answer at a different spot. The skew is measured at every expiry with a 0.5-0.7 point fit error. The 12-month quartiles are robust to method (within $2-4 between lognormal and RND). The historical implied-versus-realised record exists for 23 prints from the Bloomberg constant-maturity surface.

Cannot. (1) The pure one-day print variance cannot be separated from the 15 post-print sessions inside the 20 Nov expiry until the 6 Nov weekly lists; the 9.5% includes whatever excess post-print volatility the market expects. (2) The background term structure is not flat; the constant-b estimators use the lowest short-dated IVs and overstate E by up to a point relative to the sloped-background fit. (3) All distributions are risk-neutral; converting P(above $179.5) = 0.41-0.43 into a real-world probability needs an equity risk premium and a variance risk premium that are not estimated here (an equity premium of about 5% would shift the one-year median up by roughly $8; the historical implied-versus-realised ratio of 0.85 on the print is one piece of the variance premium, not the whole). (4) The direct Breeden-Litzenberger density is too noisy on this chain (negative mass 14-30%) to be used on its own; the smile-model RND is a parametric smoothing, not a model-free density, and its tails beyond the quoted strikes are extrapolation. (5) yfinance IVs are biased about 2 points high and inconsistent across puts and calls; any earlier number in the repo built on them (the 6 Sep ledger's 38.15% at 20 Nov, the 2.3% event estimate from the 23 Oct leg) should be read with that in mind. (6) The 5 Nov date is Zacks' expected date, not company-confirmed; all expiries used sit at least 13 days either side of it, so eligibility does not depend on the exact day, but the pattern-estimated 2027 print dates only matter for the multi-print fits. (7) The Bloomberg monthly straddle sheet measures the realised move to expiry, not on day 1, so its "implied avg 10.4% vs realised 10.7%" is a statement about 30-day straddles, not about the print. (8) The skew and 12M IV comparisons against Bloomberg's constant-maturity history are cross-method and approximate (own method about 1 pt below on skew, 0.4-0.8 pt above on 12M IV).

## 9. For the synthesis

Use these, with these labels:

| Item | Value | Label |
|---|---|---|
| 20 Nov $170 straddle | 13.5% of spot, mid of a 12.0-15.0 market; a 70-day total, not the print move | MEASURED |
| Implied 5 Nov event sd | 9.5%, range 8.5-10.5 (identified specs 8.3-11.0); expected absolute move 7.6% (6.8-8.4) | JUDGEMENT on MEASURED inputs |
| 25-delta risk reversal, 20 Nov | -3.5 vol pts (puts richer); 10% OTM put 1.18x richer than flat relative to the call | MEASURED; "ordinary for ABNB" is JUDGEMENT |
| 12-month price band | lognormal p25 / p50 / p75 = $126 / $164 / $214 (headline); skew RND $124 / $167 / $217 (sensitivity); both risk-neutral | MEASURED |
| 12-month risk-neutral P(above $179.5) | 0.41-0.43; P(above $220) 0.23-0.24; P(below $150) 0.40-0.41; P(below $125) 0.25-0.26 | MEASURED, risk-neutral |
| Realised base rate, raw close-to-close, 23 prints | rms 8.9%, mean abs 7.1%, median 6.9%, 48% at 7%+, 35% at 10%+, 13 up / 10 down | MEASURED |
| Same, QQQ-excess | rms 8.5%, mean abs 6.8%, median 5.1%, 11 up / 12 down | MEASURED |
| Nights accelerated vs decelerated (n 8 / 11, threshold 0) | raw 6 up / 2 down vs 3 up / 8 down; excess 6 / 2 vs 1 / 10; C's dead band 5 / 2, 1 / 1 flat, 3 / 7 raw | MEASURED, base rate not model |
| Historical implied event sd, Bloomberg | crush 10.5% mean (upper-bound style), kink at 45 days 8.5% mean; realised raw rms 8.9% (ratio 0.85 to crush), excess 8.5% (0.81) | MEASURED |

Do not use:

1. Any P(above X) or P(below X) as a real-world probability. They are risk-neutral. The band width is the usable object, not the level of a tail probability.
2. The one-year median below spot ($164-167 vs $170.19) as a bearish signal; it is the risk-neutral drift (4% carry less half of 39.5% squared) and is mechanical.
3. The 0.85 x straddle figure of 11.5% as the print move; it is the 70-day upper bound.
4. The skew RND's p5, p10, p90, p95 ($81, $94, $264, $302); they are extrapolated beyond the quoted strikes.
5. "1 up / 10 down" for decelerating prints without saying it is on QQQ-excess returns with n 11 and threshold 0 (raw 3 up / 8 down).
6. "The put is 18% richer" as evidence of a crowded hedge; it is the usual ABNB premium.
7. The 4 Sep to 11 Sep event-variance comparison as more than approximately unchanged; 9.8-10.0 vs 9.2-9.9 is inside the plus or minus 1 pt noise.

## 10. Files

Scripts: `analysis/src/reverse_dcf/B_pull_chains.py` (pull and save raw chains, refresh prices), `B_options_implied.py` (clean, IVs, forwards, parity, term structure, event variance and its sensitivities, skew, 12M distribution, BL check, base rates on both return series), `B_bloomberg_summary.py` (licensed workbook summaries, derived numbers only), `B_tables.py` (headline and synthesis tables).

Outputs in `data/processed/reverse_dcf/B/`: `raw_chain_20260912T044930Z.csv` (untouched since the pull), `B_pull_meta.json`, `B_prices_daily.csv`, `B_chain_clean.csv`, `B_forwards.csv`, `B_parity_check.csv`, `B_term_structure.csv`, `B_event_variance.csv`, `B_event_sensitivity.csv`, `B_event_sd_leg_sensitivity.csv`, `B_skew.csv`, `B_dist_12m_percentiles.csv`, `B_dist_12m_price_points.csv`, `B_dist_12m_meta.json`, `B_rnd_12m_grid.csv`, `B_bl_check_2027-06-17.csv`, `B_bl_check_2028-01-21.csv`, `B_print_moves.csv`, `B_print_base_rates.csv`, `B_bbg_term_structure_4sep.csv`, `B_bbg_event_fit_4sep_surface.csv`, `B_bbg_chain_4sep_term_structure.csv`, `B_bbg_event_fit_4sep_chain.csv`, `B_bbg_monthly_straddles_summary.csv`, `B_bbg_print_month_straddles.csv`, `B_bbg_print_implied_vs_realised.csv`, `B_bbg_print_implied_vs_realised_summary.csv`, `B_bbg_iv_history_summary.csv`, `B_headline.csv`, `B_price_points_for_synthesis.csv`, `B_implied_vs_realised_print.csv`, `B_reconcile_reaction_files.csv`.

Re-run order: `B_pull_chains.py` (only when a fresh pull is wanted; it writes a new timestamped raw file and updates `B_pull_meta.json`), `B_options_implied.py`, `B_bloomberg_summary.py`, `B_tables.py` (the last from `analysis/src/reverse_dcf/` since it imports `B_options_implied`). Re-pull in the last week of September or the first days of October, once the 6 Nov weekly lists.
