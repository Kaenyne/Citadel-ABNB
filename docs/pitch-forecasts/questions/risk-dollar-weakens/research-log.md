# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable 5.1, batch A12 with R11, R15, R16). Reproduction: [datasets/r10_model.py](datasets/r10_model.py) (`py -3.13`, numpy/pandas/scipy, deterministic, ~3 s; reads the FRED and yfinance pulls in `sources/`, writes `r10_summary.csv`, `r10_by_year.csv`, `r10_regime.csv`, `r10_tail.csv`, `r10_sensitivity.csv`).

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
- revision: 1
- agent: fable

## 0b. Question (verbatim)
### Title
Will the Fed's broad trade-weighted dollar index (FRED DTWEXBGS) on 11 Feb 2027 be ≥4% below its 16 Sep 2026 value?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes if DTWEXBGS(2027-02-11 or last available) ≤ 0.96 × DTWEXBGS(2026-09-16). Resolution 11 Feb 2027.
### Fine Print
Impact via the FX schedule: ±2.3 points of FY27 revenue growth per one-sigma dollar move.

Conventions adopted (stated, not changing the question): (1) the 16 Sep 2026 DTWEXBGS value is not yet published (FRED's H.10 week of 14–18 Sep posts on Monday 21 Sep 2026); the forecast uses an estimate of 119.02 (11 Sep 118.21 scaled by the DXY move 11→16 Sep at the measured daily beta 0.57, claim 3) and the monitoring calendar fixes the true threshold on 21 Sep; (2) "last available" means the most recent FRED observation on or before 11 Feb 2027 as of the resolution read (11 Feb 2027 is a Thursday; the value posts on 16 Feb 2027, so the resolver should wait for it rather than read the 6 Feb observation); (3) if FRED revises DTWEXBGS (the index is re-weighted annually in January; levels are chained, revisions are small), the values as displayed on the resolution read govern; (4) "≥4% below" is read on the ratio, i.e. a log change ≤ ln(0.96) = −4.08%.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | DTWEXBGS daily, 2006-01-02 to 2026-09-11 (5,188 observations); 11 Sep 2026 = 118.21; monthly closes 2025: Jan 128.48, Jun 119.41, Dec 119.75; 2026: Mar 121.04, Jun 120.92, Aug 118.57. Trailing 12-month log change −1.6%, 6-month −2.0%, 3-month −1.6% | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTWEXBGS ([sources/fred_DTWEXBGS_20260917T075453Z.csv](sources/fred_DTWEXBGS_20260917T075453Z.csv)) | 2026-09-14 (H.10 release for the week of 8–12 Sep) | 2026-09-17 | yes |
| 2 | ICE DXY closes (yfinance DX-Y.NYB): 11 Sep 99.12, 14 Sep 99.46, 15 Sep 99.65, 16 Sep 100.31, 17 Sep 100.18; EUR/USD 16 Sep 1.154, 17 Sep 1.147 | [sources/yfinance_dxy_daily_20260917T075625Z.csv](sources/yfinance_dxy_daily_20260917T075625Z.csv), [sources/yfinance_EURUSDX_daily_20260917T080502Z.csv](sources/yfinance_EURUSDX_daily_20260917T080502Z.csv) | 2026-09-17 | 2026-09-17 | yes |
| 3 | Daily log-change beta of DTWEXBGS on DXY, 2024-01 to 2026-09: 0.572 (r 0.79; weekly beta 0.64). DXY +1.19% (log) from 11 to 16 Sep → DTWEXBGS(16 Sep) ≈ 119.02; threshold ≈ 114.26 | computed, `datasets/r10_summary.csv` | 2026-09-17 | 2026-09-17 | yes |
| 4 | Empirical distribution of 105-observation-ahead log changes in DTWEXBGS (n 5,083 overlapping windows, 2006–2026): mean +0.37%, sd 3.99%, skew +0.65, excess kurtosis 1.35; P(≤ −4.08%) = 0.122 (2010+ 0.098; 2015+ 0.107). By start year the ≤ −4.08% share is 0 in 12 of 21 years and 26–47% in 2007, 2009, 2010, 2020, 2025 (2017 29%): episodes cluster | computed, `datasets/r10_by_year.csv`, `r10_summary.csv` | 2026-09-17 | 2026-09-17 | yes |
| 5 | Regime conditioning on trailing 252-day realised vol at window start (quintiles): vol 2.8–4.2% → P 0.114 (n 967); 4.2–4.65% → 0.056; 4.65–5.4% → 0.075; 5.4–6.2% → 0.173; >6.2% → 0.224. Current trailing vol: 63d 3.96%, 126d 4.22%, 252d 4.12% (full-sample 5.41%), i.e. the calm quintile; ±1pp band around 4.12%: P 0.072 (n 2,332). Windows starting with a trailing-12m change within ±2pp of today's −1.6%: P 0.121 | computed, `datasets/r10_regime.csv` | 2026-09-17 | 2026-09-17 | yes |
| 6 | Parametric at current realised vol (4.12% ann → 2.66% over 105 obs): normal zero-drift 0.062, consensus drift −0.42% 0.084; Student-t(4) 0.048 / 0.062; at the full-sample vol (5.41%) 0.121; at a 4.8% "implied" vol (judgement, claim 9) 0.094 / 0.119 (t4 0.085) | computed, `datasets/r10_summary.csv`, `r10_sensitivity.csv` | 2026-09-17 | 2026-09-17 | yes |
| 7 | E[log change | ≤ −4.08%] over the empirical tail = −5.6% (median −5.3%, p10 −7.1%, 619 windows) | computed, `datasets/r10_tail.csv` | 2026-09-17 | 2026-09-17 | yes |
| 8 | Reuters FX poll 2 Sep 2026 (55–66 strategists): EUR/USD median 1.16 at 3m, 1.17 at 6m, 1.18 at 12m; bank camps split JPM/HSBC/GS/Citi 1.10–1.14 vs Nomura/Scotia/UBS/ING 1.18–1.25 (2Q27); BofA 1.15 end-2026, 1.20 end-2027; USD/CAD poll 1.39 3m / 1.36 12m. The 05_fx_schedule strong-USD and weak-USD paths are those two camps (EUR 1.13→1.09 vs 1.19→1.25) | `research/notes/overnight/05_macro-outlook-and-transmission.md` §4.3; `data/processed/overnight/05_fx_schedule.csv` | 2026-09-06 (poll dated 2026-09-02) | 2026-09-17 | yes |
| 9 | No live option-implied dollar vol was obtainable: UUP/FXE/FXB/FXY Jan/Mar-2027 chains via yfinance are one-lot markets with bid 0 or ask/bid > 3 (only FXE 101C 20% IV deep ITM, FXB 130C 15%, UUP 30P 49% on a 0.35/4.90 quote), Cboe EVZ last prints 2025-03-05, barchart/investing.com/CME pages return no IV to a fetcher. Judgement input: EUR/USD 6-month implied vol runs ~7% in calm regimes (training), broad-basket beta to EUR ~0.6 plus the non-EUR legs → ~4.8% ann for the broad index, a ~15% premium to realised | [sources/yfinance_fx_etf_options_20260917T075625Z.json](sources/yfinance_fx_etf_options_20260917T075625Z.json); training | unknown | 2026-09-17 | yes |
| 10 | FOMC 16 Sep 2026: unanimous +25bp to 3.75–4.00%, first hike since 2023; Warsh: inflation "too high for too long"; traders price three hikes through June 2027; Bloomberg Dollar Spot +0.5%, best day in three months (search snippets; Bloomberg page not fetched) | https://www.bloomberg.com/news/articles/2026-09-16/dollar-jumps-after-fed-raises-rates-sends-hawkish-signal ; https://investinglive.com/central-banks/fomc-rate-decision-fed-hikes-for-the-first-time-in-three-years/ | 2026-09-16 | 2026-09-17 | yes |
| 11 | ECB expected to hike 25bp on 10 Sep 2026 to 2.50% (57 of 69 economists); "two central banks tightening into each other is why the euro cross is going nowhere"; Fed June dots 3.8% end-2026, 3.6% end-2027; 10y 4.77–4.82% | `research/notes/overnight/05_macro-outlook-and-transmission.md` §4.2 | 2026-09-06 | 2026-09-17 | no |
| 12 | FX transmission: ADR FX −0.715pp per +1% broad USD y/y (r −0.96, n 17); revenue FX lags one to two quarters (Φ kernel ⅔ prior quarter, ⅓ two back; PIT RMSE 0.99pp); +1% broad USD ≈ −0.54pp revenue FX and −0.28pp EBITDA margin through the chain; B4: a ±5% parallel dollar shift ("about one standard deviation of a two-quarter move") moves FY27 revenue FX +2.3 / −2.3pp vs spot-held and 4Q26 by ±0.5pp; the 4Q26 driver is 84% realised FX | `docs/revenue-forecast-strategy/05_backtests/B4_FX_EXHIBIT.md` §3.3; `05_backtests/fx-lag.md`; `data/processed/overnight/05_fx_fits.csv`; `research/notes/overnight/05_macro-outlook-and-transmission.md` §1–2 | 2026-09-11 | 2026-09-17 | yes |
| 13 | FX mix elasticity on nights nets to zero at current spot (overnight2 B: ~0.11pp regional differential per 1pp purchasing power; total nights 0.0, ADR −0.06pp) | `docs/overnight2/SYNTHESIS.md` §2 B | 2026-09-11 | 2026-09-17 | no |
| 14 | Polymarket has only September-2026 DXY "hit" ladders (e.g., DXY ≥101.0 high in September 0.455 yes, ≥102.5 0.295) and daily up/down markets; nothing for 2027. Kalshi KXFXEURO (EUR/USD) has no open markets; KXDXYFOMC is a same-day market | [sources/polymarket_search_dollar_index_20260917T075503Z.json](sources/polymarket_search_dollar_index_20260917T075503Z.json), [sources/kalshi_series_economics_20260917T075503Z.json](sources/kalshi_series_economics_20260917T075503Z.json), [sources/kalshi_KXFXEURO_open_20260917T080502Z.json](sources/kalshi_KXFXEURO_open_20260917T080502Z.json) | 2026-09-17 | 2026-09-17 | no |
| 15 | Brief sensitivities: 1pt of FY27 revenue growth ≈ $158M; FY27 margin 0.66pp per 1pt of revenue (held) / 0.42 (flex); FY27 EPS ≈ $0.0014 per $M of EBITDA; 0.40–0.48 EV/EBITDA turns per point of forward revenue growth, one turn ≈ $9–10/share | `docs/pitch-forecasts/00_BRIEF.md` | 2026-09-16 | 2026-09-17 | yes |
| 16 | Final 72-hour recency check (query 15): the only dollar news is the 16 Sep hike and Warsh's press conference (claim 10); no tariff ruling, intervention or policy event otherwise | WebSearch `FOMC September 16 2026 decision dollar reaction` | 2026-09-17 | 2026-09-17 | no |

Newest load-bearing source: the 17 Sep FRED/yfinance pulls and the 16 Sep FOMC (0–1 days old against a 147-day window).

## 2. Query Log
1. [repo] `docs/pitch-forecasts/00_BRIEF.md`, `QUESTIONS.md`; skill files; example log; finished logs F01, R01, C08, C05, R08
2. [repo] `docs/revenue-forecast-strategy/05_backtests/fx-lag.md`, `B4_FX_EXHIBIT.md`; `research/notes/overnight/05_macro-outlook-and-transmission.md` §2, §4.2–4.3; `data/processed/overnight/05_fx_fits.csv`, `05_fx_schedule.csv`; `docs/overnight2/SYNTHESIS.md`
3. [FRED, py -3.13] fredgraph.csv?id=DTWEXBGS, DEXUSEU, DTWEXAFEGS (2026-09-17T07:54:53Z) → `sources/`
4. [yfinance, py -3.13] DX-Y.NYB daily 2023-09 to 2026-09-17; UUP/FXE/FXB/FXY option chains Jan/Mar 2027 (2026-09-17T07:56:25Z) → `sources/`
5. [yfinance] ^EVZ (stale: last 2025-03-05), ^VXY (delisted), EURUSD=X (2026-09-17T08:05:02Z)
6. [Polymarket public-search] dollar index; DXY; EUR/USD; euro dollar; US dollar (2026-09-17T07:55:03Z)
7. [Kalshi API] series?category=Economics (grep dollar/euro/fx); markets?series_ticker=KXFXEURO (0 open); events?series_ticker=KXFXEURO (0)
8. [computed] `datasets/r10_model.py`
9. WebSearch: EUR/USD implied volatility 6-month September 2026 (no live figure in results)
10. WebFetch: barchart.com Euro FX volatility-greeks (empty), investing.com EUR/USD options (spot only, no IV)
11. WebSearch: FOMC September 16 2026 decision dollar reaction (final 72-hour recency check; result: +25bp hike, hawkish, dollar +0.5%)

WebSearch calls charged to R10: 2 of 5.

## 3. Leading Hypothesis Entities
Federal Reserve, Kevin Warsh, DTWEXBGS, DXY, EUR/USD, ECB, Reuters FX poll, FRED H.10

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Dollar drifts lower on the consensus path (EUR 1.18 in 12m) and a −4% print is a plain tail draw | leading (≈0.09) | consensus drift is worth only −0.4% over the window (claim 8); the tail is set by vol, not drift |
| A 2025-style policy shock (tariff ruling, Fed-independence scare, fiscal event) reproduces the H1-2025 −7% slide | kept inside the tail (episode years 6 of 21, claim 4) | the unconditional empirical 0.12 already contains 2007/2009/2010/2020/2025; the current regime is calm (claim 5) and the Fed has just turned hawkish (claim 10), which argues for the quintile-1 rate (0.11) or below |
| Fed hiking cycle (three more priced) keeps the dollar bid; P near 0.03–0.05 | kept as the lower edge of the interval | the hikes are priced (claim 10); realised-vol normal at zero drift gives 0.06, t(4) 0.05 |
| Hormuz/oil safe-haven unwind or a Warsh reversal delivers a dollar bear camp move (EUR 1.22–1.25) | kept inside the drift sensitivity (drift −1.5% → 0.16) | that camp is a 2Q27 view (claim 8); by 11 Feb only part of it would be realised |
| Market-implied distribution as the anchor (fine print of the method) | kept as the anchor with a judgement vol (claim 9) | no tradable quote obtainable; the 4.8% figure is a training-knowledge premium over measured realised vol and is flagged |
| Resolution flips on the 16 Sep FRED print or a January re-weighting | discarded as immaterial | the threshold moves with the 16 Sep value but so does the distance from today's spot; the annual re-weighting is a chained level (convention 3) |

## 5. Independent Estimates
- base_rate_estimate: 0.10 — the empirical 105-observation distribution 2006–2026 gives 0.122 unconditionally and 0.098–0.107 on 2010+/2015+ windows; conditioned on the current calm-vol regime (quintile 1: 0.114; ±1pp band: 0.072) and the momentum band (0.121): centre 0.10 (claims 4–5)
- decomposition_estimate: 0.07 — parametric with the measured trailing realised vol (4.12% ann, 2.66% over the window), consensus drift −0.42% from the Reuters poll: normal 0.084, Student-t(4) 0.062; zero-drift 0.062 / 0.048; the post-FOMC hawkish regime leans toward zero drift (claims 6, 8, 10)
- anchor_estimate: 0.10 — lognormal at a judgement implied vol of 4.8% (≈15% over realised, claim 9) with consensus drift: normal 0.119, t(4) 0.085; no tradable market exists on the Feb-2027 dollar (claim 14)
- anchor_value: 0.10 (constructed market-implied distribution, 2026-09-17; NO tradable quote — flagged)
- final_estimate: 0.09 (credible interval 0.05–0.15)
- final_minus_anchor: −1 point. NOT_INDEPENDENTLY_DERIVED flag applies in form, not in substance: the "anchor" is itself a construction on the same realised-vol measurement, so the three estimates are not independent draws; what the empirical and parametric legs add is that the historical tail is fatter than a normal at the same vol (kurtosis 1.35, episode clustering) but the current regime sits in the calmest quintile, and those two effects roughly cancel. The number is a vol call, not a dollar call

## 6. Final Numbers
**Binary.** P(DTWEXBGS on 11 Feb 2027 ≤ 0.96 × its 16 Sep 2026 value) = **0.09**, credible interval **0.05–0.15**.
Structure: 0.35 weight on the regime-conditioned empirical (0.10), 0.35 on the parametric at realised vol (0.07), 0.30 on the implied-vol construction (0.10) = 0.089. Required move: −4.08% log from ≈119.0 to ≤114.3 in 105 trading days, i.e. 1.5 sd at realised vol, 1.3 sd at the implied construction.
E[move | Yes] = −5.6% (claim 7): the conditional impact below uses a 5.6% dollar decline, 1.1× the B4 one-sigma shift.
Extreme-probability gate: not triggered (0.09 > 0.05). Resolution-criteria audit anyway: (i) the 16 Sep value is unpublished — threshold fixed 21 Sep (monitoring row 1); (ii) "last available" — wait for the 16 Feb posting of the 11 Feb value; (iii) a FRED re-weighting in January changes levels by chaining only; (iv) no early-resolution route.

## 7. Sensitivity
Rows from `datasets/r10_sensitivity.csv` (parametric leg) and `r10_regime.csv`; the final moves by about 0.7× each leg's move at the weights above.
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| Vol regime stays at the trailing 4.1% | 5.4% (full-sample vol; 2022/2025-style regime): 0.14; 6.0%: 0.17; 3.5% (2013/2021 calm): 0.05 |
| Drift −0.4% over the window (Reuters poll) | −1.5% (dollar-bear camp fully realised by Feb): 0.16; 0 (hawkish Fed holds the dollar): 0.07; +1.0% (three hikes re-price the dollar up): 0.04 |
| Tail shape: mix of normal and t(4) | pure normal at 4.8% implied: 0.12; pure t(4) at realised vol: 0.06 |
| Regime read: vol quintile 1 (0.114) | ±1pp band (0.072): final 0.08; unconditional 2006–2026 (0.122): final 0.10 |
| Joint bear-dollar (vol 5.4%, drift −1.5%) | 0.24 |
| Joint hawkish (vol 3.5%, drift +1.0%) | 0.02 |
| 16 Sep FRED value prints 118.5 instead of 119.0 | threshold 113.8; P unchanged to 2dp (the distance from today's spot is what is priced; the 17 Sep DXY is 0.1% below 16 Sep) |

Pre-mortem ("it is 11 Feb 2027 and the broad dollar is ≥4% below 16 Sep"): (1) a policy shock — a Supreme Court tariff ruling, a Fed-independence episode under Warsh, or a fiscal event — repeated the H1-2025 slide (−7% in five months); priced inside the empirical episode rate (6 of 21 years) and the fat-tail leg, not as a named branch; (2) the hiking cycle ended abruptly (growth scare, Hormuz re-closure hitting US activity) and the differential collapsed; priced through the drift sensitivity (−1.5% → 0.16); (3) the vol regime jumped (a calm quintile-1 start is where 2007 and 2025 also began): the regime conditioning is the weakest link because vol is not persistent over five months; the ±1pp band (0.072) and the unconditional (0.122) bracket it. ("It was flat or stronger"): the modal outcome, 0.91. Asymmetry: the memo's use of R10 is as an FX tailwind that would rescue FY27 revenue growth; under-stating it is cheap (the EV is under $1/share), over-stating it would clutter the risks list with a 1-in-11 macro draw.

## 8. Monitoring Calendar
Hazard arithmetic: with spot unchanged the probability decays as the window shortens — 60 trading days left: ~0.03; 30 days: ~0.005; a −2% move with 60 days left restores ~0.14; −3% with 30 days left ~0.24.
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-21 | FRED H.10 posts the 14–18 Sep week: fix DTWEXBGS(16 Sep) and the threshold (0.96×) | Replace the 119.02 estimate; no probability change unless the print differs from the estimate by >0.5% (then re-run the script with the true spot) |
| 2026-10-02 | Prelim memo freeze | Quote 0.09 (0.05–0.15); impact line as §9 |
| 2026-10-27/28, 2026-12-08/09 | FOMC (Dec with SEP) | A hold with dovish dots: drift → −1.0%, P +0.04; a third hike with hawkish dots: P −0.02 |
| 2026-10-29, 2026-12-17 | ECB | An ECB hike beyond 2.50% with the Fed on hold: +0.02; a pause: −0.01 |
| 2026-11-03 | US midterms | No pre-emptive change; a tariff or fiscal shock after the election is the tail path |
| weekly (Mon) | FRED H.10; re-run `datasets/r10_model.py` with the remaining horizon | Apply the hazard table above; move to ≥0.5 only if spot is within 1% of the threshold with <20 days left |
| 2027-01-26/27 | FOMC | Last scheduled catalyst inside the window |
| 2027-02-16 | FRED posts the 11 Feb observation | Resolve on the ratio to the 16 Sep value |

## 9. Impact
If Yes (E[move | Yes] = −5.6% on the broad dollar between 16 Sep 2026 and 11 Feb 2027, 1.1× B4's one-sigma shift), deltas versus the memo's base case (spot-held FX schedule):

| Item | Delta if R10 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | 0 | quarter closed before the window; FX mix on nights nets to zero (claim 13) |
| 4Q26 nights (pts) | 0 | claim 13 |
| ADR (pts) | +1.5 in 4Q26 (about half the move lands inside Q4), **+4.0 from 1Q27** (0.715pp per 1% of broad USD, claim 12) | `05_fx_fits.csv` |
| 4Q26 revenue ($M) | **+17** (B4: +0.5pp of 4Q26 revenue FX per 5% shift × 1.1 on $3.1bn) | claim 12 |
| FY27 revenue ($M) | **+400** (2.3pp × 1.1 = +2.5pp of FY27 growth × $158M) | claims 12, 15 |
| FY26 adj. EBITDA margin (pp) | +0.1 (4Q26 FX revenue at ~59% flow-through, ¼ FY weight) | brief sensitivity |
| FY27 adj. EBITDA margin (pp) | **+1.6** (0.66pp per 1pt of revenue × 2.5; the macro chain gives −0.28pp per +1% USD × 5.6 = +1.6, same answer) | claims 12, 15 |
| FY27 EPS ($) | **+0.37** (+$400M × 0.66 = $264M EBITDA × $0.0014) | claim 15 |
| Stock ($/share) | **+5 to +10** (2.5pt × 0.40–0.48 turns × $9–10 = $9–12 if the market capitalises FX growth as it does organic growth; the market usually discounts FX, so the memo should carry ~$5) | claim 15 |
| **EV = P × impact** | **0.09 × $5 ≈ $0.5/share** ($0.9 at the joint-solve figure) | |
| Materiality | **Immaterial / borderline** (EV under $1/share at the discounted figure). The memo should keep FX as arithmetic, not as a risk line: the risk that matters is the sign of the FY27 FX line under spot-held (+0.5pp) vs the strong-dollar camp (−1.8pp), which is symmetric and already in the bridge | |

RESUME: the next agent (audit response) should re-run `datasets/r10_model.py` after 21 Sep with the true 16 Sep DTWEXBGS and check three things: (1) the regime conditioning (quintile 0.114 vs band 0.072 — the choice moves the final by ±0.02); (2) the judgement implied vol 4.8% (claim 9; if a live 6m EUR/USD implied vol is obtainable, replace it: each +1pp of broad-basket vol adds ~0.03); (3) the drift convention (−0.42% from the Reuters poll; the post-hike regime may justify zero). The empirical tail mean (−5.6%) drives the impact table only.
