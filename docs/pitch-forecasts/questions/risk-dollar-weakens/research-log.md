# RESEARCH LOG

Revision 2 (2026-09-17, audit response to `audits/A12-research-audit.md`, Fable 5.1; revision 1 of 2026-09-17 was the initial forecast, batch A12 with R11, R15, R16). Reproduction: [datasets/r10_model_v2.py](datasets/r10_model_v2.py) (`py -3.13`, numpy/pandas/scipy, deterministic, ~5 s; reads the FRED, yfinance and 03:50 option pulls in `sources/`, writes `r10_v2_summary.csv`, `r10_v2_regime.csv`, `r10_v2_sensitivity.csv`, `r10_v2_hazard.csv`). Revision-1 `r10_model.py` and its CSVs are left in place as the audit trail.

## 0. Metadata
- question_name: risk-dollar-weakens
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § R10)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-16
- close_date: 2027-02-11
- resolution_date: 2027-02-11
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 2
- revised: 2026-09-17
- agent: fable

## 0b. Question (verbatim)
### Title
Will the Fed's broad trade-weighted dollar index (FRED DTWEXBGS) on 11 Feb 2027 be ≥4% below its 16 Sep 2026 value?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if DTWEXBGS(2027-02-11 or last available) ≤ 0.96 × DTWEXBGS(2026-09-16). Resolution 11 Feb 2027.
### Fine Print
Impact via the FX schedule: ±2.3 points of FY27 revenue growth per one-sigma dollar move.

Conventions adopted (stated, not changing the question): (1) the 16 Sep 2026 DTWEXBGS value is not yet published (FRED's H.10 week of 14–18 Sep posts on Monday 21 Sep 2026); the forecast uses an estimate of 119.02 (11 Sep 118.21 scaled by the DXY move 11→16 Sep at the measured daily beta 0.57, claim 3) and the monitoring calendar fixes the true threshold on 21 Sep; (2) "last available" means the most recent FRED observation on or before 11 Feb 2027 as of the resolution read (11 Feb 2027 is a Thursday; the value posts on 16 Feb 2027, so the resolver should wait for it rather than read the 6 Feb observation); (3) if FRED revises DTWEXBGS (the index is re-weighted annually in January; levels are chained, revisions are small), the values as displayed on the resolution read govern; (4) "≥4% below" is read on the ratio, i.e. a log change ≤ ln(0.96) = −4.08%; (5) **the horizon is 100 FRED observations** (weekdays 17 Sep 2026 – 11 Feb 2027 inclusive, net of Columbus Day, Veterans Day, Thanksgiving, Christmas, New Year and MLK; the analogous window a year earlier, 17 Sep 2025 – 11 Feb 2026, carries exactly 100 non-null observations in the saved file) — revision 1's 105 was wrong by five (A12-15).

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | DTWEXBGS daily, 2006-01-02 to 2026-09-11 (5,188 observations); 11 Sep 2026 = 118.21; monthly closes 2025: Jan 128.48, Jun 119.41, Dec 119.75; 2026: Mar 121.04, Jun 120.92, Aug 118.57. Trailing 12-month log change −1.6%, 6-month −2.0%, 3-month −1.6% | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTWEXBGS ([sources/fred_DTWEXBGS_20260917T075453Z.csv](sources/fred_DTWEXBGS_20260917T075453Z.csv)) | 2026-09-14 (H.10 release for the week of 8–12 Sep) | 2026-09-17 | yes |
| 2 | ICE DXY closes (yfinance DX-Y.NYB): 11 Sep 99.12, 14 Sep 99.46, 15 Sep 99.65, 16 Sep 100.31, 17 Sep 100.18; EUR/USD 16 Sep 1.154, 17 Sep 1.147; FRED DEXUSEU last observation 11 Sep 1.1604 | [sources/yfinance_dxy_daily_20260917T075603Z.csv](sources/yfinance_dxy_daily_20260917T075603Z.csv), [sources/yfinance_EURUSDX_daily_20260917T075708Z.csv](sources/yfinance_EURUSDX_daily_20260917T075708Z.csv), [sources/fred_DEXUSEU_20260917T075453Z.csv](sources/fred_DEXUSEU_20260917T075453Z.csv) | 2026-09-17 | 2026-09-17 | yes |
| 3 | Daily log-change beta of DTWEXBGS on DXY, 2024-01 to 2026-09: 0.572 (r 0.79; weekly beta 0.64). DXY +1.19% (log) from 11 to 16 Sep → DTWEXBGS(16 Sep) ≈ 119.02; threshold ≈ 114.26. **Daily beta of DTWEXBGS on EUR/USD (FRED DEXUSEU), 2024+: −0.620 (r −0.88, n 675); on 12-month changes 2006+: −0.587** | computed, `datasets/r10_v2_summary.csv` | 2026-09-17 | 2026-09-17 | yes |
| 4 | Empirical distribution of **100**-observation-ahead log changes in DTWEXBGS (n 5,088 overlapping windows, 2006–2026): mean +0.36%, sd 3.88%; P(≤ −4.08%) = **0.117** (2010+ 0.096; 2015+ 0.107). By start year the ≤ −4.08% share is **zero in 10 of 21 years** (2006, 2008, 2013, 2014, 2015, 2018, 2019, 2021, 2023, 2026) and 26–47% in 2007, 2009, 2010, 2020, 2025 (2017 ~29%): episodes cluster. **Effective sample: the windows are 100-day overlaps, so there are 51 non-overlapping blocks; the block estimate ranges 0.059–0.196 across the 100 possible phases (mean 0.117), binomial SE ≈ 4.5pp** — the width of the published interval, and its source (A12-21). Revision 1's "12 of 21" and H = 105 are withdrawn | computed, `datasets/r10_v2_summary.csv` | 2026-09-17 | 2026-09-17 | yes |
| 5 | Regime conditioning on trailing 252-day realised vol at window start (quintiles, H = 100): vol 2.8–4.2% → P **0.095** (n 968); 4.2–4.65% → 0.054; 4.65–5.4% → 0.070; 5.4–6.2% → 0.187; >6.2% → 0.208. Current trailing vol: 63d 3.96%, 126d 4.22%, 252d 4.12% (full-sample 5.41%), i.e. the calm quintile; ±1pp band around 4.12%: P 0.059 (n 2,337). Windows starting with a trailing-12m change within ±2pp of today's −1.6%: P 0.104. **The forward vol actually realised over the next 100 observations after a calm-quintile start averages 4.62% (ratio 1.12 to the quintile's own trailing readings, 1.32 to the 3.5% median start); after a ±1pp-band start 4.80%; after any start 5.18%: a calm start does not stay calm** (A12-05) | computed, `datasets/r10_v2_regime.csv` | 2026-09-17 | 2026-09-17 | yes |
| 6 | Parametric at the **forward** vol 4.62% (2.91% over 100 obs): normal 0.120 / Student-t(4) 0.086 with the poll drift; zero drift 0.080 / 0.059. At the trailing 4.12% (revision 1's input): 0.094 with the poll drift, 0.058 zero-drift. At the 4.8% implied construction: 0.129 / 0.093 (poll), 0.089 zero-drift | computed, `datasets/r10_v2_summary.csv`, `r10_v2_sensitivity.csv` | 2026-09-17 | 2026-09-17 | yes |
| 7 | E[log change | ≤ −4.08%] over the empirical tail at H = 100 = **−5.5%** (median −5.3%, 594 windows) | computed, `datasets/r10_v2_summary.csv` | 2026-09-17 | 2026-09-17 | yes |
| 8 | Reuters FX poll 2 Sep 2026 (55–66 strategists): EUR/USD median 1.16 at 3m, 1.17 at 6m, 1.18 at 12m; bank camps split JPM/HSBC/GS/Citi 1.10–1.14 vs Nomura/Scotia/UBS/ING 1.18–1.25 (2Q27); BofA 1.15 end-2026, 1.20 end-2027; USD/CAD poll 1.39 3m / 1.36 12m. The 05_fx_schedule strong-USD and weak-USD paths are those two camps (EUR 1.13→1.09 vs 1.19→1.25). **Drift for this question: interpolate the poll path from the 16 Sep spot (1.1538, yfinance) through 3m 1.16 / 6m 1.17 to the 4.86-month resolution point → 1.1662, +1.07% log; at the measured broad/EUR beta −0.62 that is −0.66% over the window** (revision 1's −0.42% took the 3m→12m leg as a 12-month move and dropped the spot→3m leg: A12-06) | `research/notes/overnight/05_macro-outlook-and-transmission.md` §4.3; `data/processed/overnight/05_fx_schedule.csv`; computed | 2026-09-06 (poll dated 2026-09-02) | 2026-09-17 | yes |
| 9 | **Option evidence (03:50 pull, the one with real quotes; the 07:56 pull returned zero bids, asks and open interest and is superseded):** UUP (DXY-like basket, spot 28.40) January-2027 chain: 28C bid 0.40 / ask 0.75 (OI 6,924, volume 59), 30C OI 16,342 (volume 177), 28P bid 0.30 / ask 1.15 (OI 2,180). Black–Scholes on the 28-strike: call IV 0.6% (bid) / 5.2% (mid) / 8.1% (ask); put IV 7.3% / 14.1% / 20.7% — a straddle band of roughly 5–14% that cannot pin a number. Realised: DXY 252d 5.25% vs broad 4.12%, ratio 1.27, so a UUP implied vol in the 5–6% range maps to ~4–4.7% on the broad index. Cboe EVZ last prints 2025-03-05; barchart/investing.com/CME pages return no IV to a fetcher. **Judgement input kept at 4.8% for the broad index (4.12% × a 10–15% implied-over-realised premium), now bracketed by the UUP band and coincident with the forward-vol evidence in claim 5** | [sources/yfinance_fx_etf_options_20260917T0350Z.json](sources/yfinance_fx_etf_options_20260917T0350Z.json) (superseded: [sources/yfinance_fx_etf_options_20260917T075603Z.json](sources/yfinance_fx_etf_options_20260917T075603Z.json)) | 2026-09-16 close | 2026-09-17 | yes |
| 10 | FOMC 16 Sep 2026: unanimous +25bp to 3.75–4.00%, first hike since 2023; Warsh: inflation "too high for too long"; traders price three hikes through June 2027; Bloomberg Dollar Spot +0.5%, best day in three months (search snippets; Bloomberg page not fetched; corroborated by DXY 99.65 → 100.31, +0.66%, in the saved yfinance file) | https://www.bloomberg.com/news/articles/2026-09-16/dollar-jumps-after-fed-raises-rates-sends-hawkish-signal ; https://investinglive.com/central-banks/fomc-rate-decision-fed-hikes-for-the-first-time-in-three-years/ | 2026-09-16 | 2026-09-17 | yes |
| 11 | ECB expected to hike 25bp on 10 Sep 2026 to 2.50% (57 of 69 economists); "two central banks tightening into each other is why the euro cross is going nowhere"; Fed June dots 3.8% end-2026, 3.6% end-2027; 10y 4.77–4.82% | `research/notes/overnight/05_macro-outlook-and-transmission.md` §4.2 | 2026-09-06 | 2026-09-17 | no |
| 12 | FX transmission: ADR FX −0.715pp per +1% broad USD y/y (r −0.96, n 17); revenue FX lags one to two quarters (Φ kernel ⅔ prior quarter, ⅓ two back; PIT RMSE 0.99pp); +1% broad USD ≈ −0.54pp revenue FX and −0.28pp EBITDA margin through the chain; B4: a ±5% parallel dollar shift ("about one standard deviation of a two-quarter move") moves FY27 revenue FX +2.3 / −2.3pp vs spot-held and 4Q26 by ±0.5pp; the 4Q26 driver is 84% realised FX. **B4 §5.2 conversion: 1pp of FY27 growth = 1% of FY26 revenue = $142.9M (FY26 base $14,293M); its own weak-USD scenario prices +2.5pp as +$354M.** The brief's $158M/pt is 1% of FY27 revenue, a different object (A12-20). **B4's scenario is an immediate parallel shift; this question's event is a drift that completes on 11 Feb, so the FY27 pass-through below is a ceiling** | `docs/revenue-forecast-strategy/05_backtests/B4_FX_EXHIBIT.md` §3.3, §5.2; `05_backtests/fx-lag.md`; `data/processed/overnight/05_fx_fits.csv`; `research/notes/overnight/05_macro-outlook-and-transmission.md` §1–2 | 2026-09-11 | 2026-09-17 | yes |
| 13 | FX mix elasticity on nights nets to zero at current spot (overnight2 B: ~0.11pp regional differential per 1pp purchasing power; total nights 0.0, ADR −0.06pp) | `docs/overnight2/SYNTHESIS.md` §2 B | 2026-09-11 | 2026-09-17 | no |
| 14 | Polymarket has only September-2026 DXY "hit" ladders (e.g., DXY ≥101.0 high in September 0.455 yes, ≥102.5 0.295) and daily up/down markets; nothing for 2027. Kalshi KXFXEURO (EUR/USD) has no open markets; KXDXYFOMC is a same-day market | [sources/polymarket_search_dollar_index_20260917T075503Z.json](sources/polymarket_search_dollar_index_20260917T075503Z.json), [sources/kalshi_series_economics_20260917T075503Z.json](sources/kalshi_series_economics_20260917T075503Z.json), [sources/kalshi_KXFXEURO_open_20260917T075611Z.json](sources/kalshi_KXFXEURO_open_20260917T075611Z.json) | 2026-09-17 | 2026-09-17 | no |
| 15 | Brief sensitivities: 1pt of FY27 revenue growth ≈ $158M (1% of FY27 revenue); FY27 margin 0.66pp per 1pt of revenue (held) / 0.42 (flex); FY27 EPS ≈ $0.0014 per $M of EBITDA; 0.40–0.48 EV/EBITDA turns per point of forward revenue growth, one turn ≈ $9–10/share. Line build: FY26 revenue $14,268M / adj. EBITDA $5,098M (35.73%); FY27 $15,829M / $5,483M (34.64%) | `docs/pitch-forecasts/00_BRIEF.md`; `docs/margin-build/SYNTHESIS.md` annual table | 2026-09-16 | 2026-09-17 | yes |
| 16 | Final 72-hour recency check (query 15): the only dollar news is the 16 Sep hike and Warsh's press conference (claim 10); no tariff ruling, intervention or policy event otherwise | WebSearch `FOMC September 16 2026 decision dollar reaction` | 2026-09-17 | 2026-09-17 | no |

Newest load-bearing source: the 17 Sep FRED/yfinance pulls and the 16 Sep FOMC (0–1 days old against a 147-day window).

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`; skill files; example log; finished logs F01, R01, C08, C05, R08
2. [repo] `docs/revenue-forecast-strategy/05_backtests/fx-lag.md`, `B4_FX_EXHIBIT.md`; `research/notes/overnight/05_macro-outlook-and-transmission.md` §2, §4.2–4.3; `data/processed/overnight/05_fx_fits.csv`, `05_fx_schedule.csv`; `docs/overnight2/SYNTHESIS.md`
3. [FRED, py -3.13] fredgraph.csv?id=DTWEXBGS, DEXUSEU, DTWEXAFEGS (2026-09-17T07:54:53Z) → `sources/`
4. [yfinance, py -3.13] DX-Y.NYB daily 2023-09 to 2026-09-17; UUP/FXE/FXB/FXY option chains Jan/Mar 2027 (03:50Z and 07:56:03Z) → `sources/`
5. [yfinance] ^EVZ (stale: last 2025-03-05), ^VXY (delisted), EURUSD=X (2026-09-17T07:57:08Z)
6. [Polymarket public-search] dollar index; DXY; EUR/USD; euro dollar; US dollar (2026-09-17T07:55:03Z)
7. [Kalshi API] series?category=Economics (grep dollar/euro/fx); markets?series_ticker=KXFXEURO (0 open); events?series_ticker=KXFXEURO (0)
8. [computed] `datasets/r10_model.py` (revision 1)
9. WebSearch: EUR/USD implied volatility 6-month September 2026 (no live figure in results)
10. WebFetch: barchart.com Euro FX volatility-greeks (empty), investing.com EUR/USD options (spot only, no IV)
11. WebSearch: FOMC September 16 2026 decision dollar reaction (final 72-hour recency check; result: +25bp hike, hawkish, dollar +0.5%)
12. [revision 2, repo] `audits/A12-research-audit.md`; `audits/A12-reproduce.py` run (`py -3.13 -B`); `B4_FX_EXHIBIT.md` §5.2 (the $142.9M conversion); `docs/margin-build/SYNTHESIS.md` annual table
13. [revision 2, computed] `numpy.busday_count` 17 Sep 2026 – 11 Feb 2027 net of six federal holidays = 100; the 2025–26 analogue window in the saved FRED file = 100 non-null rows; Black–Scholes IVs on the 03:50 UUP chain; broad/EUR daily beta from the saved DEXUSEU file; `datasets/r10_model_v2.py`

WebSearch calls charged to R10: 2 of 5 (none added in revision 2).

## 3. Leading Hypothesis Entities
Federal Reserve, Kevin Warsh, DTWEXBGS, DXY, EUR/USD, ECB, Reuters FX poll, FRED H.10

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Dollar drifts lower on the consensus path (EUR 1.18 in 12m) and a −4% print is a plain tail draw | leading (≈0.10) | consensus drift is worth −0.66% over the window (claim 8); the tail is set by vol, not drift |
| A 2025-style policy shock (tariff ruling, Fed-independence scare, fiscal event) reproduces the H1-2025 −7% slide | kept inside the tail (episode years 6 of 21, claim 4) | the unconditional empirical 0.117 already contains 2007/2009/2010/2020/2025; the current regime is calm (claim 5) and the Fed has just turned hawkish (claim 10), which argues for the quintile-1 rate (0.095) — but calm starts realise a 4.6% forward vol, and 2007 and 2025 both began in the calm quintile |
| Fed hiking cycle (three more priced) keeps the dollar bid; P near 0.03–0.05 | kept as the lower edge of the interval | the hikes are priced (claim 10); forward-vol normal at zero drift gives 0.08, t(4) 0.06 |
| Hormuz/oil safe-haven unwind or a Warsh reversal delivers a dollar bear camp move (EUR 1.22–1.25) | kept inside the drift sensitivity (drift −1.5% → 0.14) | that camp is a 2Q27 view (claim 8); by 11 Feb only part of it would be realised |
| Market-implied distribution as the anchor (fine print of the method) | kept as the anchor with a judgement vol (claim 9) | the 03:50 UUP chain has real quotes but a 5–14% straddle band; the 4.8% figure is a premium over measured realised vol, bracketed by that band and by the forward-vol evidence |
| Trailing realised vol as the forward vol | **discarded (A12-05)** | on this series, windows that start in the calm quintile go on to realise 4.6%, not 4.1%; using the trailing reading understates the tail by about a quarter |
| Resolution flips on the 16 Sep FRED print or a January re-weighting | discarded as immaterial | the threshold moves with the 16 Sep value but so does the distance from today's spot; the annual re-weighting is a chained level (convention 3) |

## 5. Independent Estimates
- base_rate_estimate: 0.10 — the empirical 100-observation distribution 2006–2026 gives 0.117 unconditionally and 0.096–0.107 on 2010+/2015+ windows; conditioned on the current calm-vol regime (quintile 1: 0.095; ±1pp band: 0.059) and the momentum band (0.104): centre 0.10, effective-sample SE ≈ 4.5pp (claims 4–5)
- decomposition_estimate: 0.10 — parametric with the **forward** vol that calm starts realise (4.62% ann, 2.91% over the window) and the correctly interpolated poll drift −0.66%: normal 0.120, Student-t(4) 0.086, mixed 0.103; at zero drift (the post-FOMC hawkish reading) 0.080 / 0.059 (claims 5, 6, 8, 10). Revision 1's 0.07 used the trailing 4.12% and a −0.42% drift
- anchor_estimate: 0.11 — lognormal/t(4) at the judgement implied vol of 4.8% (claim 9) with the poll drift: normal 0.129, t(4) 0.093, mixed 0.111; no tradable market exists on the Feb-2027 dollar (claim 14); the UUP straddle band (5–14% on a 1.27× more volatile basket) brackets the input without pinning it
- anchor_value: 0.11 (constructed market-implied distribution, 2026-09-17; NO tradable quote — flagged)
- final_estimate: 0.10 (credible interval 0.06–0.17)
- final_minus_anchor: −1 point. NOT_INDEPENDENTLY_DERIVED flag applies in form, not in substance: the "anchor" is itself a construction on the same realised-vol measurement, so the three estimates are not independent draws; what the empirical and parametric legs add is that the historical tail is fatter than a normal at the same vol (kurtosis 1.35, episode clustering) while the current regime sits in the calmest quintile. Revision 1 let those two effects "roughly cancel" at a trailing vol; they do not cancel once the forward vol is used, which is the whole of the move from 0.09 to 0.10. The number is a vol call, not a dollar call. Audit A12's independent number is 0.11 (0.06–0.18) at H = 105; this revision's 0.104 at H = 100 rounds to 0.10

## 6. Final Numbers
**Binary.** P(DTWEXBGS on 11 Feb 2027 ≤ 0.96 × its 16 Sep 2026 value) = **0.10**, credible interval **0.06–0.17**.
Structure: 0.35 weight on the regime-conditioned empirical (0.10), 0.35 on the parametric at the forward vol (0.103), 0.30 on the implied-vol construction (0.111) = 0.104. Required move: −4.08% log from ≈119.0 to ≤114.3 in 100 trading days, i.e. 1.4 sd at the forward vol, 1.35 sd at the implied construction (1.5 sd at revision 1's trailing vol).
E[move | Yes] = −5.5% (claim 7): the conditional impact below uses a 5.5% dollar decline, 1.1× the B4 one-sigma shift.
Extreme-probability gate: not triggered (0.10 > 0.05). Resolution-criteria audit anyway: (i) the 16 Sep value is unpublished — threshold fixed 21 Sep (monitoring row 1); (ii) "last available" — wait for the 16 Feb posting of the 11 Feb value; (iii) a FRED re-weighting in January changes levels by chaining only; (iv) no early-resolution route.

## 7. Sensitivity
Rows from `datasets/r10_v2_sensitivity.csv` (normal/t(4) mix at the stated vol and drift) and `r10_v2_regime.csv`; the final moves by 0.65× a move applied to both parametric legs and 0.35× a move in the empirical leg.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Forward vol 4.6% (calm-quintile forward realisation) | trailing 4.1% held (revision 1): 0.09; 4.8% (band forward): 0.11; 5.4% (full-sample; 2022/2025-style regime): 0.12; 6.0%: 0.14; 3.5% (2013/2021 calm persists): 0.07 |
| Drift −0.66% over the window (Reuters poll, interpolated) | −1.5% (dollar-bear camp fully realised by Feb): 0.14; 0 (hawkish Fed holds the dollar): 0.08; +1.0% (three hikes re-price the dollar up): 0.06 |
| Tail shape: mix of normal and t(4) | pure normal at 4.8% implied: 0.12; pure t(4) at the forward vol: 0.09 |
| Regime read: vol quintile 1 (0.095) | ±1pp band (0.059): final 0.09; unconditional 2006–2026 (0.117): 0.11; block-estimate phase range 0.06–0.20: 0.09–0.14 |
| Horizon 100 observations | 105 (revision 1): +0.004 |
| Joint bear-dollar (vol 5.4%, drift −1.5%, unconditional empirical) | 0.20 |
| Joint hawkish (vol 3.5%, drift +1.0%, band empirical) | 0.03 |
| 16 Sep FRED value prints 118.5 instead of 119.0 | threshold 113.8; P unchanged to 2dp (the distance from today's spot is what is priced; the 17 Sep DXY is 0.1% below 16 Sep) |

Pre-mortem ("it is 11 Feb 2027 and the broad dollar is ≥4% below 16 Sep"): (1) a policy shock — a Supreme Court tariff ruling, a Fed-independence episode under Warsh, or a fiscal event — repeated the H1-2025 slide (−7% in five months); priced inside the empirical episode rate (6 of 21 years) and the fat-tail leg, not as a named branch; (2) the hiking cycle ended abruptly (growth scare, Hormuz re-closure hitting US activity) and the differential collapsed; priced through the drift sensitivity (−1.5% → 0.14); (3) the vol regime jumped: this is now priced directly — a calm quintile-1 start is where 2007 and 2025 also began, and the forward vol after such starts is 4.6%, not 4.1%. ("It was flat or stronger"): the modal outcome, 0.90. Asymmetry: the memo's use of R10 is as an FX tailwind that would rescue FY27 revenue growth; under-stating it is cheap (the EV is under $1/share), over-stating it would clutter the risks list with a 1-in-10 macro draw.

## 8. Monitoring Calendar
Hazard arithmetic (`datasets/r10_v2_hazard.csv`, forward vol, poll drift pro-rated): with spot unchanged the probability decays as the window shortens — 80 observations left: 0.09; 60: 0.05; 40: 0.02; 30: 0.007; a −2% move with 60 left restores 0.23; −3% with 30 left 0.29; −3% with 10 left 0.13.
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-21 | FRED H.10 posts the 14–18 Sep week: fix DTWEXBGS(16 Sep) and the threshold (0.96×) | Replace the 119.02 estimate; no probability change unless the print differs from the estimate by >0.5% (then re-run `r10_model_v2.py` with the true spot) |
| 2026-10-02 | Prelim memo freeze | Quote 0.10 (0.06–0.17); impact line as §9; FX stays bridge arithmetic |
| 2026-10-27/28, 2026-12-08/09 | FOMC (Dec with SEP) | A hold with dovish dots: drift → −1.0%, P +0.03; a third hike with hawkish dots: P −0.02 |
| 2026-10-29, 2026-12-17 | ECB | An ECB hike beyond 2.50% with the Fed on hold: +0.02; a pause: −0.01 |
| 2026-11-03 | US midterms | No pre-emptive change; a tariff or fiscal shock after the election is the tail path |
| weekly (Mon) | FRED H.10; re-run `datasets/r10_model_v2.py` with the remaining horizon | Apply the hazard table above; move to ≥0.5 only if spot is within 1% of the threshold with <20 observations left |
| 2027-01-26/27 | FOMC | Last scheduled catalyst inside the window |
| 2027-02-16 | FRED posts the 11 Feb observation | Resolve on the ratio to the 16 Sep value |

## 9. Impact
If Yes (E[move | Yes] = −5.5% on the broad dollar between 16 Sep 2026 and 11 Feb 2027, 1.1× B4's one-sigma shift), deltas versus the memo's base case (spot-held FX schedule). Two conventions are stated so the rows agree with each other (A12-02, A12-19, A12-20): growth points are converted at B4's own $142.9M per point (1% of FY26 revenue); the margin and EPS rows use ONE flow-through (costs held: the revenue delta reaches EBITDA in full, which is the brief's 0.66pp-per-point slope), with the flex (0.42pp) pair beside it. **The ADR row is a booking-date effect on the quarter's bookings; the revenue row is the kernel-recognised effect on the quarter's revenue (⅔ prior quarter, ⅓ two back); they are different objects and are not additive.**

| Item | Delta if R10 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | quarter closed before the window; FX mix on nights nets to zero (claim 13) |
| 4Q26 nights (pts) | 0 | claim 13 |
| ADR (pts) | +1.5 in 4Q26 (booking-date; about half the move lands inside Q4), **+3.9 from 1Q27** (0.715pp per 1% of broad USD × 5.5, claim 12) | `05_fx_fits.csv` |
| 4Q26 revenue ($M) | **+17** (B4: +0.5pp of 4Q26 revenue FX per 5% shift × 1.1 on $3,178M; recognition-lagged, so most of the move reaches 1Q27–2Q27) | claim 12 |
| FY27 revenue ($M) | **+362** (2.3pp × 1.1 = +2.53pp of FY27 growth × $142.9M; a ceiling, because B4's shift is immediate and this event completes on 11 Feb) | claims 12, 15 |
| FY26 adj. EBITDA margin (pp) | +0.08 held ((5,098 + 17) / (14,268 + 17) vs 35.73%); flex +0.05 | claim 15 line build |
| FY27 adj. EBITDA margin (pp) | **+1.46** held ((5,483 + 362) / (15,829 + 362) = 36.10% vs 34.64%); flex +0.93 (the macro chain's −0.28pp per +1% USD × 5.5 = +1.5 agrees with the held row) | claims 12, 15 |
| FY27 EPS ($) | **+0.51** held ($362M × $0.0014); flex +$0.32 (revision 1's +$0.37 applied 0.66 as a dollar flow-through on top of the held margin row: withdrawn) | claim 15 |
| Stock ($/share) | **+5 to +10** (2.5pt × 0.40–0.48 turns × $9–10 = $9–12 if the market capitalises FX growth as it does organic growth; the market usually discounts FX, so the memo should carry ~$5) | claim 15 |
| **EV = P × impact** | **0.10 × $5 ≈ $0.5/share** ($1.0 at the joint-solve figure) | |
| Materiality | **Immaterial / borderline** (EV under $1/share at the discounted figure). The memo should keep FX as arithmetic, not as a risk line: the risk that matters is the sign of the FY27 FX line under spot-held (+0.5pp) vs the strong-dollar camp (−1.8pp), which is symmetric and already in the bridge | |

## 10. Revision notes
| Change | Finding | Effect |
|---|---|---|
| Horizon 105 → 100 FRED observations (weekday count net of six holidays; the 2025–26 analogue window in the saved file has 100); convention 5 added | A12-15 | −0.004 |
| Parametric leg at the forward vol calm starts realise (4.62%) instead of the trailing 4.12%; claim 5 carries the forward-vol column; the trailing-vol hypothesis moved to §4 as discarded | A12-05 | decomposition 0.07 → 0.10 |
| Poll drift re-derived on the interpolated spot → 3m → 6m → 12m path at the measured broad/EUR beta −0.62: −0.42% → −0.66%; claim 3 carries the EUR beta | A12-06 | +0.015 on the parametric legs |
| Claim 9 rewritten on the 03:50 UUP chain (real quotes, five-figure OI, straddle IV band 5–14%); DXY/broad realised ratio 1.27; the 4.8% construction kept, now bracketed; 07:56 pull marked superseded | A12-13 | anchor 0.10 → 0.11 |
| Claim 4: zero-episode years 10 of 21 (list at H = 100); effective sample 51 blocks, phase range 0.06–0.20, SE 4.5pp stated as the interval's source | A12-21 | interval 0.05–0.15 → 0.06–0.17 |
| §9: FY27 revenue at B4's $142.9M/pt (+$362M, not +$400M); the row labelled a ceiling; the immediate-shift vs drift caveat added | A12-20, coherence ruling | — |
| §9: EPS on the held convention ($362M × 0.0014 = +$0.51), flex pair stated; margin rows from the line build; the 0.66 no longer applied twice | A12-02 | EPS +$0.37 → +$0.51 (held) |
| §9: the booking-date (ADR) vs recognition-lag (revenue) sentence added; both numbers kept | A12-19 | — |
| E[move | Yes] −5.6% → −5.5% at H = 100; blend 0.089 → 0.104; final 0.09 → 0.10; hazard table rebuilt at the forward vol | A12-05/15 | +0.01 |

RESUME: the next agent should re-run `datasets/r10_model_v2.py` after 21 Sep with the true 16 Sep DTWEXBGS, and check two things: (1) the forward-vol input (4.62% is the calm-quintile mean; the ±1pp band gives 4.80%; each +0.5pp of vol adds ~0.015 to the final); (2) the drift convention (−0.66% from the poll; the post-hike regime may justify zero, which is the 0.08 row). The tail mean (−5.5%) drives the impact table only. The immaterial verdict is robust to every row in §7.
