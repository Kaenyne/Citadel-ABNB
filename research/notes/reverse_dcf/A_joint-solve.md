# A. What each share price implies for ABNB's FY27 revenue growth, EBITDA and nights

Workstream A of the 12-13 Sep 2026 overnight run. Branch `krish/reverse-dcf`. Scripts `analysis/src/reverse_dcf/A_common.py`, `A_01_multiple_regressions.py`, `A_02_market_implied_solves.py`, `A_03_decomposition_comparison.py` (run in that order with `py -3.13` from the repo root). Outputs under `data/processed/reverse_dcf/A/`. Anchors are from `docs/reverse_dcf/BRIEF.md` and are not re-derived. Labels: ANCHOR (brief), MEASURED (computed here, source named), JUDGEMENT (mine, reason given). Revised 13 Sep after the audit (`research/notes/reverse_dcf/audit_A.md`, pass with fixes): the band is now the fitted-line band, FY27 is quoted as a range across the two legitimate mappings, the realised-units reading is in the headline, the tails are labelled JUDGEMENT, and the minor corrections are applied (section 8 lists them).

## 1. The answer

The one MEASURED number is in NTM terms: at $170.19 the market pays for NTM (3Q26 to 2Q27) revenue growth of 12.9% in guide-proxy units (1 s.e. fitted-line band 11.5 to 14.3%) at 17.7x EV/NTM EBITDA. Translated to FY27, that is revenue of $15.7 to 15.9bn (+10.4 to +11.5% on the delivered FY26 base of $14,231m, depending on the mapping), adj. EBITDA of $5.69 to 5.75bn at a 36.2% margin, EV/FY27 EBITDA of 16.0 to 16.2x, GAAP EPS of about $6.00, and FY27 nights growth of +8 to +9% (ADR ex-FX +3%, FX -0.6pp, take rate flat). That is the Street ($15.75bn) to the team base ($15.8bn), 1.1 to 2.2pp below management's delivered case (+12.6%), which the joint solve prices at $175, about $5 above the price. In realised-growth units (the guide proxy has run 1.4pp above realised NTM growth) the FY27 reading is about a point lower, +9.0 to +10.1%, which puts the price on or just below the Street, with the delivered case still $5 above.

Headline table. Primary method: joint solve, spec A, on its native NTM basis; FY27 as the range between the proportional mapping and the mapping chained through the Street's 2H26; growth on the delivered FY26 base $14,231m; margin 36.2%; nights at ADR ex-FX +3.0%, FX -0.6pp, take rate flat, residual 0. The NTM column is MEASURED; every FY27 column is JUDGEMENT on that solve; the $150 and $220 rows are JUDGEMENT compounded (slope, mapping and base convention, see 3.1) and should be quoted as ranges.

| Price | What it is | NTM revenue growth (1 s.e. band) | FY27 revenue $bn | FY27 revenue growth (mapping range) | FY27 adj. EBITDA $bn | EV / FY27 EBITDA | FY27 nights growth | FY27 growth, realised units | Nearest case |
|---|---|---|---|---|---|---|---|---|---|
| $150.00 | bear tape | 8.6% (7.3 to 10.0) | 14.4 to 15.3 | 1.4 to 7.2 (10.2 base-consistent) | 5.22 to 5.52 | 14.5 to 15.3x | -1 to +5% | 0 to 6% | below Literal (9.8%) |
| $165.00 | p25 target | 11.8% (10.5 to 13.2) | 15.4 to 15.7 | 8.1 to 10.4 | 5.57 to 5.69 | 15.6 to 16.0x | 5.6 to 7.9% | 6.7 to 9.1% | Literal to Street |
| $170.19 | price, 11 Sep | 12.9% (11.5 to 14.3) | 15.7 to 15.9 | 10.4 to 11.5 (12.1 base-consistent) | 5.69 to 5.75 | 16.0 to 16.2x | 7.8 to 8.9% | 9.0 to 10.1% | Street to team base |
| $179.50 | mean target | 14.8% (13.2 to 16.5) | 16.1 to 16.3 | 13.4 to 14.4 | 5.84 to 5.89 | 16.6 to 16.7x | 10.8 to 11.7% | 12.0 to 13.0% | Delivered (12.6%) |
| $185.00 | median yfinance target | 15.9% (14.2 to 17.8) | 16.3 to 16.6 | 14.5 to 16.7 | 5.90 to 6.01 | 16.8 to 17.1x | 11.9 to 14.0% | 13.1 to 15.3% | Delivered to Ambition |
| $197.50 | p75 target | 18.4% (16.2 to 20.6) | 16.6 to 17.3 | 17.0 to 21.9 | 6.03 to 6.28 | 17.3 to 18.0x | 14.3 to 19.0% | 15.6 to 20.5% | Ambition (18.0%) |
| $220.00 | top target | 22.7% (19.6 to 25.7) | 17.3 to 18.6 | 21.2 to 30.8 (16.2 base-consistent) | 6.25 to 6.74 | 18.1 to 19.5x | 18 to 28% | 20 to 29% | above Ambition |

MEASURED and JUDGEMENT as labelled (`A_headline.csv`, `A_joint_solve.csv`, `A_implied_nights.csv`). Point estimates on the proportional mapping, for anyone who needs one number per price: FY27 growth 7.2 / 10.4 / 11.5 / 13.4 / 14.5 / 17.0 / 21.2%, EBITDA $5.52 / 5.69 / 5.75 / 5.84 / 5.90 / 6.03 / 6.25bn, nights 4.7 / 7.9 / 8.9 / 10.8 / 11.9 / 14.3 / 18.4%. The management cases on the same base: Literal 9.8% (11.0% on its own FY26), Delivered 12.6%, Ambition 18.0% (17.0% on its own FY26); Street 10.6% (11.4% on its own FY26 of $14,130m); team base 11.05% (11.6% on its own FY26). Growth rates on a fixed base are a level index: the base-consistent mapping (which lets the FY26 base move with the same scaling) compresses the tails to 10.2% at $150 and 16.2% at $220 and gives 12.1% at the price.

Three things the reader should carry away. First, the joint solve and the simple holds agree at the price and disagree violently at the tails: holding 16.5x and solving for revenue gives +8.2% at $170.19 but -5.9% at $150 and +43% at $220, because on a fixed multiple each turn of EV/EBITDA is worth 6.6pp of FY27 growth. The joint solve splits a move between the multiple and EBITDA about 70/30 at the price (per point of NTM growth the multiple moves 2.2% and EBITDA 0.9%), which is the economically sensible structure and the reason it is kept as the primary method despite the weak regression (section 2). Second, a point of FY27 nights growth is worth about $4.90 a share (2.9%) on the joint solve against $1.54 on a fixed 16.0x multiple, which quantifies the brief's observation that nights acceleration moves the multiple. Third, the slope and level of the fitted line are weakly identified; the NTM band in the table (about +/- 1.4pp at the price, +/- 3pp at $220) is the 1 s.e. band on the fitted line, and the residual scatter around the line is wider still (+/- 5pp at every price, section 2.2).

## 2. Method 1, the joint solve: what the regression says and whether it can be trusted

### 2.1 Re-estimating M(g)

The dependent variable is EV / NTM adj. EBITDA from the WS12 monthly point-in-time panel (`12_abnb_multiples_monthly.csv`), where NTM EBITDA is the NTM revenue proxy times the LTM margin. That is exactly the structure EBITDA(g) = base revenue x (1+g) x margin, so the solve is internally consistent when run on the LTM base ($13,159m, margin 35.1%). The growth variable is WS12's guide-based NTM revenue proxy (caveat C2 in the WS12 note; see 2.3). Newey-West standard errors (6 lags monthly, 12 lags for 12-month changes). Every specification tried is in `A_regression_specs.csv`; the table below is the subset that matters. The implied FY27 column is the NTM solve mapped proportionally (NTM growth less 1.42pp); the CSV also carries the mis-specified direct FY27-basis solve in its own column (3.1).

| Spec | Window | n | Slope (turns per pt of NTM growth) | t (NW) | Margin coefficient (t) | R2 | DW | NTM growth the $170.19 EV implies |
|---|---|---|---|---|---|---|---|---|
| A. levels, growth only (primary) | Jan 2023 to Sep 2026 | 45 | +0.396 | 3.06 | | 0.23 | 0.53 | 12.9% |
| B. levels, growth + margin | same | 45 | +0.477 | 2.29 | +0.39 (0.37) | 0.24 | 0.55 | 13.5% |
| C. levels, growth + margin + 10y + NDX fwd P/E (WS12 spec) | same | 45 | +0.554 | 2.14 | +0.39 (0.39) | 0.29 | 0.63 | 15.3% |
| Log multiple on growth | same | 45 | +0.0207 per pt (log) | 2.91 | | 0.23 | 0.48 | 13.4% |
| Levels, growth only | Nov 2022 to Sep 2026 | 47 | +0.281 | 2.34 | | 0.14 | 0.53 | 12.9% |
| Levels, growth only | Jan 2024 to Sep 2026 | 33 | +0.139 | 0.60 | | 0.03 | 0.31 | 14.9% |
| Levels, growth + margin | Jan 2024 to Sep 2026 | 33 | +0.536 | 2.69 | +2.81 (3.72) | 0.53 | 0.83 | 18.2% |
| Levels, growth only, ex Aug-Sep 2026 (post-2Q26 re-rating) | 2023-26 | 43 | +0.407 | 3.10 | | 0.24 | 0.52 | 12.9% |
| D. levels, growth only, 2023-25 only (2026 out of sample) | Jan 2023 to Dec 2025 | 36 | +0.555 | 5.33 | | 0.52 | 1.03 | 11.9% |
| Levels, growth only, ex Jul 2023 (27.3x month) | 2023-26 | 44 | +0.375 | 2.97 | | 0.25 | 0.45 | 13.2% |
| E. one observation per print (first month after each print) | 2023-26 | 16 | +0.310 | 2.63 | | 0.22 | 1.07 | 13.7% |
| One observation per print (last month before each print) | 2023-26 | 16 | +0.353 | 3.79 | | 0.22 | 1.22 | 12.4% |
| 12m changes: d(EV/NTM EBITDA) on d(NTM growth) | Jan 2023 to Sep 2026 (series starts Nov 2021) | 45 | +0.072 | 1.30 | | 0.06 | 0.83 | n.a. |
| 12m changes: + d margin | same | 45 | -0.119 | -0.77 | -1.31 (-1.12) | 0.20 | 0.73 | n.a. |
| 12m changes: + d margin + d 10y + d NDX | same | 45 | +0.016 | 0.18 | -1.21 (-1.86); 10y +3.16 (3.02); NDX +1.31 (4.13) | 0.54 | 1.30 | n.a. |
| 12m changes: d(EV/LTM EBITDA) on d(NTM growth) (WS12's +0.49 spec, no controls) | same | 45 | +0.365 | 4.05 | | 0.42 | 0.83 | n.a. |
| Levels: EV/LTM EBITDA on NTM growth (WS12's +0.74 spec, no controls) | 2023-26 | 45 | +0.639 | 4.16 | | 0.37 | 0.53 | 10.0% |
| Levels: EV/LTM EBITDA on LTM growth (WS12's headline +0.48, no controls) | 2023-26 | 45 | +0.333 | 4.57 | | 0.59 | 0.68 | 9.4% (not a meaningful inversion: LTM growth is known, 13.6%) |
| Quarterly panel, quarter-end price on that quarter's own guide (not point-in-time) | 4Q22 to 2Q26 | 15 | -0.009 | -0.04 | | 0.00 | 0.67 | n.a. |

MEASURED. Reading:

1. The WS12 coefficients are reproduced in kind but not in strength. WS12's +0.48 (t 8.3) is EV/LTM EBITDA on LTM growth with three controls; on the forward multiple against forward growth, which is what the solve needs (the multiple as a function of the growth being solved for, on the EBITDA it divides), the slope is +0.40 to +0.55 with t 2.1 to 3.1 and R2 0.23 to 0.29. The margin coefficient is +0.39 turns per point with t 0.4, confirming WS12: margin does not move the multiple, so the margin sensitivities in section 3 run through EBITDA only.
2. In 12-month changes the forward multiple does not respond to the guide: +0.07 turns (t 1.3). WS12's +0.49 (t 5.6) is the trailing multiple. The difference is mechanical and informative: when the guide rises, NTM EBITDA rises with it, and EV/NTM EBITDA only rises if the price outruns the guide. It has not, on average: over 12-month windows the price has moved roughly one for one with the guide and the forward multiple has been close to flat. The level relationship therefore describes the slow 2023 to 2025 de-rating (20%+ growth at 20x+ to 10% growth at 14-16x), not a within-year law.
3. Window sensitivity is large. The 24-month rolling slope runs from +0.94 (window ending Jan 2026; Dec 2025 is +0.93) to -0.18 (window ending Jun 2026), and 2024-26 alone gives +0.14 (t 0.6) (`A_regression_rolling.csv`). Adding margin to the 2024-26 window produces a margin coefficient of 2.8 turns per point (t 3.7), which is an overfit to the 2026 months and not usable. The expanding window has been stable since mid-2025 (slope 0.48 to 0.63 with margin, 0.40 to 0.57 without) and converges on the full-sample answer.
4. The 2Q26 re-rating does not drive the slope. Dropping Aug-Sep 2026 moves it from 0.396 to 0.407. The opposite is the case: from Feb to Jul 2026 the multiple sat 3.7 to 5.9 turns below the fitted line (proxy 17-18% growth, multiple 13.6-15.9x), and the 2Q26 print moved it to 1.2-1.4 turns below (`A_regression_fitted_residuals.csv`). The market did not pay the fitted multiple for the 17% guide for six months.
5. Dropping Jul 2023 (the 27.3x month) barely matters (0.375). One observation per print (n 16, DW 1.1-1.2, the honest independent-observation count) keeps the slope at 0.31-0.35 with t 2.6-3.8. The quarter-end-price panel, where the price predates the guide it is matched to, has a slope of zero: the relationship exists only point-in-time, which is the same statement as WS12's "the market prices the guide".
6. Leave-one-out (`A_regression_loo.csv`): dropping any single month moves the implied NTM growth at $170.19 between 12.7% and 13.2% (spec A) and the slope between 0.37 and 0.43; dropping any whole reported-quarter block (all months sharing a guide) gives 12.5% to 13.4% and slopes 0.33 to 0.47. The point at the price is stable because $170.19 lands near the sample mean (18.3x at 14.7% proxy growth); the stability does not extend to the tails.

### 2.2 The solve and its band

EV(P) = P x 597.0m - $9,593m (ANCHOR: 2Q26 diluted shares and net cash ex float); $92,010m at $170.19. Solve (a + b g) x $13,159m x (1 + g) x 35.1% = EV(P) for g (NTM, regression-native), then map to FY27 (3.1). The multiple is a linear function of growth so the equation is a quadratic with one root in range (the other root is at about -145%); every specification gives a monotone answer in price and an answer at $170.19 inside the 8-16% band the brief set as the sensibility test (`A_joint_solve_checks.csv`).

The band is the 1 s.e. band on the fitted line: the delta-method standard error of the fitted multiple at the solved growth, sqrt(x' V x) with V the Newey-West covariance of intercept and slope, and the solve re-run on the line shifted up and down by that amount. It carries both the level and the slope uncertainty (the audit's finding 1: the earlier slope-only band, rotated about the sample means, collapsed to nothing at $179.50 because the solve there lands on the pivot; those rows remain in `A_joint_solve.csv` labelled SUPERSEDED). The fitted-line s.e. is 0.74 to 1.74 turns across the tape (0.78 at the price). The residual standard deviation of the regression, 2.95 turns, is the different question of where the market sits relative to the line and is quoted once, here: it is +/- 5pp of NTM growth at every price (7.7 to 18.4% at $170.19), which is the honest statement of how much the regression can say about growth from the price alone.

| Spec | $150 | $165 | $170.19 | $179.5 | $185 | $197.5 | $220 |
|---|---|---|---|---|---|---|---|
| A. growth only (primary), NTM | 8.6% | 11.8% | 12.9% | 14.8% | 15.9% | 18.4% | 22.7% |
| A, fitted-line 1 s.e. band, NTM | 7.3 to 10.0 | 10.5 to 13.2 | 11.5 to 14.3 | 13.2 to 16.5 | 14.2 to 17.8 | 16.2 to 20.6 | 19.6 to 25.7 |
| A, +/- 1 residual s.d. (2.95 turns), NTM | 3.3 to 14.1 | 6.5 to 17.3 | 7.7 to 18.4 | 9.6 to 20.2 | 10.7 to 21.3 | 13.2 to 23.7 | 17.6 to 27.9 |
| B. growth + margin, NTM (band) | 9.8% (7.0 to 12.5) | 12.5% | 13.5% (11.5 to 15.4) | 15.2% (13.4 to 16.9) | 16.1% | 18.3% | 22.0% (19.4 to 24.6) |
| C. WS12 controls, NTM (band) | 12.0% (9.6 to 14.4) | 14.5% | 15.3% (13.2 to 17.4) | 16.8% (14.6 to 18.9) | 17.6% | 19.5% | 22.8% (19.5 to 26.3) |
| D. 2023-25 fit, 2026 out of sample, NTM (band) | 8.6% (7.4 to 9.7) | 11.1% | 11.9% (11.1 to 12.7) | 13.4% (12.7 to 14.1) | 14.3% | 16.2% | 19.6% (18.6 to 20.6) |
| E. one obs per print, NTM (band) | 8.6% (6.4 to 10.7) | 12.4% | 13.6% (11.9 to 15.4) | 15.9% (14.0 to 17.8) | 17.2% | 20.1% | 25.1% (21.6 to 28.6) |
| F. WS12's published 0.48 through the 4 Sep point (18.2x, 17.8%), NTM | 12.0% | 14.8% | 15.7% | 17.4% | 18.3% | 20.4% | 24.1% |
| SUPERSEDED slope-only band on A (for the record) | 6.8 to 9.8 | 11.0 to 12.4 | 12.4 to 13.3 | 14.8 to 14.9 | 15.7 to 16.3 | 17.7 to 19.5 | 21.2 to 25.0 |
| Implied EV / NTM EBITDA, spec A | 15.9x | 17.2x | 17.7x | 18.4x | 18.8x | 19.8x | 21.5x |

MEASURED (`A_joint_solve.csv`). At the price the specifications span 11.9% to 15.7% NTM. Spec F is the exception worth understanding: anchoring WS12's 0.48 slope through today's point assumes the market was on the line on 4 Sep with the 17.8% guide proxy; that is the "the market believes the guide" reading, and it returns 15.7% at $170.19 (the 7.8% fall since 4 Sep then reads as 2pp of growth). Specs A to E say the market has sat below the line all year and returns 12-13.5%. The brief's instruction was to treat the price as fair value, so the sample-fitted line is the right one, and the gap between A and F (2.8pp at the price) is, with the level uncertainty above, the largest model-choice uncertainty in this note.

### 2.3 Units: the proxy is not consensus

MEASURED, with a JUDGEMENT on how to apply it. The growth variable is the guide-implied NTM proxy (`12_abnb_multiples_history.py`: next-quarter guide midpoint grossed up by the trailing four-print beat cushion, with the guide-implied growth applied to the following three quarters), which today reads 17.8% against 15.7% consensus (WS12 caveat C2). Comparing the proxy with realised NTM revenue growth for the 12 vintages where the following four quarters are known (3Q22 to 2Q25, `A_ntm_proxy_vs_realised.csv`): mean error +1.4pp, RMSE 2.9pp, range -2.9 to +4.8pp; it overstated by 1.5 to 4.8pp in 2022-24 and understated by 1 to 3pp in 2025, so the bias is not stable either. The implied growth numbers in this note are in proxy units. The headline table now carries a realised-units column that subtracts the 1.4pp mean bias: 12.9% NTM reads as about 11.6% realised, and the FY27 range 10.4 to 11.5% as 9.0 to 10.1%. In those units the price sits on or just below the Street (Literal to Street), with the delivered case still about $5 above; the difference between "team base" and "Street" is within a point either way.

### 2.4 Cross-section peer fit: not usable for this purpose

MEASURED (`A_joint_solve_peer_crosssection.csv`). The WS12 log-linear fits (ln EV/NTM EBITDA = a + b x growth; all 18 peers b 0.021, t 1.9, R2 0.19; 12 travel and marketplace names b 0.033, t 4.9, R2 0.35) solved jointly at $170.19 return NTM growth of 21.6% (all peers) and 18.2% (travel), and 16.8% / 14.8% even at $150. Those are above the ambition case and above the guide proxy, so the peer line cannot explain ABNB's price by growth at any price on the tape: ABNB trades 19-29% (4-5 turns) above what peers with its growth get, as WS12 found. Holding that premium constant and re-solving gives 13.1% / 14.0% at $170.19, but that is circular (the premium was measured at the 4 Sep price). Conclusion: the cross-section is a statement about the premium, not a solve for growth. Reported and set aside.

### 2.5 Verdict on method 1

JUDGEMENT. Against the criteria I set before running: (i) slope t above 2 in levels, yes (3.1 NW; 2.6-3.8 on independent observations); (ii) same sign in 12-month changes of the forward multiple, no (+0.07, t 1.3); (iii) answer at $170.19 inside 8-16% and monotone, yes on all eight specs; (iv) leave-one-out range within 3pp, yes (0.9pp); (v) stable across sub-windows, no (24-month rolling slopes from -0.18 to +0.94). The joint solve passes at the price and fails on robustness of the slope. I keep it as the primary method for the range because the alternative (a fixed multiple) gives answers at the tails that no market participant holds (FY27 revenue -6% at $150, +43% at $220; 6.6pp of growth per turn), while the joint solve's tails (7% and 21% on the proportional mapping) are at least the kind of numbers bears and bulls say. The band in the headline table is the fitted-line 1 s.e. band and should be quoted with the point estimate; the tails should be quoted as the mapping ranges. At the price itself, the two methods agree on the multiple rather than on growth: the joint solve's fitted 16.0 to 16.2x FY27 EBITDA is inside the team's 13.5 / 16.5 / 18.5x band and next to today's 15.9x on the delivered case, while the hold at the team's mid 16.5x gives 8.2% growth. So the $170.19 reading (Street to team base, delivered $5 above) rests on the joint solve; what does not depend on the regression is that the price pays 15.9 to 16.1x for the Street's or management's FY27 EBITDA (3.3).

## 3. Mapping NTM to FY27, and the simple holds

### 3.1 The mappings

The regression identifies NTM growth (3Q26 to 2Q27) on the LTM base with the LTM margin. FY27 is 1Q27 to 4Q27, so everything in FY27 terms is a JUDGEMENT about the quarterly path. MEASURED arithmetic (`A_joint_solve.csv`):

| Mapping | How | $150 | $165 | $170.19 | $179.5 | $185 | $197.5 | $220 | Status |
|---|---|---|---|---|---|---|---|---|---|
| Proportional | FY27 growth = NTM growth less the delivered case's NTM-to-FY27 spread (14.0% - 12.6% = 1.42pp); the shortfall vs management is spread evenly over 3Q26-4Q27; growth on the fixed base $14,231m | 7.2% | 10.4% | 11.5% | 13.4% | 14.5% | 17.0% | 21.2% | legitimate as a level; the fixed base makes the rate a level index |
| Chained through the Street's 2H26 | implied NTM revenue less Street 3Q26 $4,744m and 4Q26 $3,177m = implied 1H27 revenue; FY27 grows at the 1H27 rate | 1.4% | 8.1% | 10.4% | 14.4% | 16.7% | 21.9% | 30.8% | legitimate if the brief's anchored quarters are taken as given; extreme at the tails by construction |
| Chained through the delivered 2H26 ($7,945m) | same with management's 2H26 | 1.0% | 7.7% | 10.0% | 14.0% | 16.3% | 21.5% | 30.4% | variant of the above |
| Base-consistent proportional | scale the whole delivered path (3Q26 to 4Q27) by implied NTM / delivered NTM, so the FY26 base moves too; FY27 growth on that base | 10.2% | 11.6% | 12.1% | 13.0% | 13.4% | 14.5% | 16.2% | the growth rate the market would actually expect for FY27 under the same scaling; compresses the tails |
| Direct FY27 basis | apply the NTM-fitted multiple to FY27 EBITDA ($14,231m x (1+g) x 36.2%) | 5.5% | 8.5% | 9.5% | 11.3% | 12.4% | 14.7% | 18.7% | mis-specified: FY27 EBITDA at any g is 11.6% larger than NTM EBITDA at the same g and at a margin the line was not fitted on, so the multiple over-values EBITDA and forces g down about 2pp; kept in the CSV only to show that gap |

JUDGEMENT: the headline quotes FY27 as the range between the proportional and the Street-chained mappings, with the base-consistent figure as the third number where it falls outside that range. At the price the two legitimate mappings differ by 1.1pp, the same size as the gap between the team base and the delivered case, so a point estimate over-states precision; at the tails they differ by 6-10pp and the base-consistent figure sits on the other side of the proportional one, which is why the tail rows are labelled JUDGEMENT and why the fixed-base convention should be understood as inflating the tail spread. The FY27 revenue level is the better headline quantity ($15.7 to 15.9bn at the price).

### 3.2 Method 2a: hold the multiple and the margin, solve for FY27 revenue growth

MEASURED (`A_simple_holds_grid.csv`, `A_simple_holds_long.csv`). Spot EV convention (597.0m shares, $9,593m net cash). Growth on the delivered FY26 base. P/E rows translate EPS to revenue through the delivered-case FY27 P&L (577.1m average diluted shares, 18% tax, SBC $1,936m, D&A 0.65% of revenue, net interest +$516m); EV/FCF rows use the delivered FY27 FCF/EBITDA of 1.024.

| Lens held | $150 | $165 | $170.19 | $179.5 | $185 | $197.5 | $220 |
|---|---|---|---|---|---|---|---|
| EV / FY27 EBITDA 13.5x, margin 36.2% | 15.0% | 27.8% | 32.3% | 40.3% | 45.0% | 55.7% | 75.0% |
| EV / FY27 EBITDA 15.86x (today's, delivered case), 36.2% | -2.1% | 8.8% | 12.6% | 19.4% | 23.4% | 32.6% | 49.0% |
| EV / FY27 EBITDA 16.5x, 36.2% | -5.9% | 4.6% | 8.2% | 14.8% | 18.6% | 27.4% | 43.2% |
| EV / FY27 EBITDA 16.5x, 35.5% | -4.1% | 6.7% | 10.4% | 17.0% | 21.0% | 29.9% | 46.0% |
| EV / FY27 EBITDA 16.5x, 37.0% | -8.0% | 2.3% | 5.9% | 12.3% | 16.1% | 24.7% | 40.1% |
| EV / FY27 EBITDA 18.5x, 36.2% | -16.1% | -6.7% | -3.5% | 2.4% | 5.8% | 13.6% | 27.7% |
| P / FY27 GAAP EPS 22x | 22.9% | 32.4% | 35.7% | 41.6% | 45.0% | 52.9% | 67.2% |
| P / FY27 GAAP EPS 27x | 5.3% | 13.1% | 15.7% | 20.5% | 23.4% | 29.8% | 41.4% |
| P / FY27 GAAP EPS 30x | -2.4% | 4.6% | 7.0% | 11.3% | 13.8% | 19.6% | 30.1% |
| EV / FY27 FCF 14x | 8.2% | 20.4% | 24.6% | 32.1% | 36.5% | 46.6% | 64.8% |
| EV / FY27 FCF 17x | -10.8% | -0.9% | 2.6% | 8.8% | 12.4% | 20.8% | 35.8% |
| EV / FY27 FCF 20x | -24.2% | -15.7% | -12.8% | -7.5% | -4.4% | 2.6% | 15.4% |
| EV / FY27 EBITDA 16.5x, end-FY27 convention (570.7m shares, $10.6bn net cash; the management note's target-price convention) | -11.8% | -1.7% | 1.8% | 8.0% | 11.7% | 20.1% | 35.2% |
| Joint solve, spec A, proportional (for comparison) | 7.2% | 10.4% | 11.5% | 13.4% | 14.5% | 17.0% | 21.2% |

Reading. At $170.19 the hold returns anything from -3.5% (18.5x) to +32% (13.5x) on the EBITDA lens alone: 6.6pp of FY27 growth per turn. The three mid multiples (16.5x, 27x, 17x) give 8.2%, 15.7% and 2.6%; their average, 8.8%, is below the joint solve's range because 16.5x and 17x are above the 16.0x and 15.5x the price actually pays on the delivered case. The hold is useful in one direction only: it says which multiple the price pays for a given case (3.3), not what growth the price implies. The end-FY27 convention row shows why the management note's $186 for the delivered case at 16.5x and this note's 16.0x at $170.19 are consistent: rolling the share count and net cash to end-FY27 is worth about one turn, which on the hold is 6pp of growth. All growth figures in this note use the spot convention, as the brief's 15.9x anchor does.

### 3.3 Method 2b: hold the Street's (or management's) FY27, solve for the multiple

MEASURED (`A_implied_multiples.csv`). Street FY27 revenue $15,745m (Zacks $15,730m 4 Sep, S&P $15,760m 3 Sep), EBITDA at 36.2% = $5,700m (no EBITDA consensus exists), EPS $6.08 (Zacks $6.02, S&P $6.14).

| Price | EV / FY27 EBITDA, Street | EV / FY27 EBITDA, Delivered ($5,801m) | EV / FY27 EBITDA, Team base ($5,758m) | P / FY27 EPS, Street $6.08 | EV / FY27 FCF, Delivered ($5,941m) | EV / FY27 SBC-adjusted FCF, Delivered ($4,005m) | EV / NTM EBITDA, Delivered |
|---|---|---|---|---|---|---|---|
| $150.00 | 14.0x | 13.8x | 13.9x | 24.7x | 13.5x | 20.0x | 14.9x |
| $165.00 | 15.6x | 15.3x | 15.4x | 27.1x | 15.0x | 22.2x | 16.6x |
| $170.19 | 16.1x | 15.9x | 16.0x | 28.0x | 15.5x | 23.0x | 17.1x |
| $179.50 | 17.1x | 16.8x | 17.0x | 29.5x | 16.4x | 24.4x | 18.2x |
| $185.00 | 17.7x | 17.4x | 17.5x | 30.4x | 17.0x | 25.2x | 18.8x |
| $197.50 | 19.0x | 18.7x | 18.8x | 32.5x | 18.2x | 27.1x | 20.2x |
| $220.00 | 21.4x | 21.0x | 21.1x | 36.2x | 20.5x | 30.4x | 22.7x |

The tape from $150 to $220 is 14.0x to 21.4x on the Street's FY27 EBITDA, 24.7x to 36.2x on its EPS. The team's 13.5 / 16.5 / 18.5x set maps to roughly $146 / $174 / $193 on the Street's FY27 (spot convention). $220 on the Street's numbers is 21.4x, above WS12's bull 18.5x and above every implied multiple in the live target tape (WS12: 10.1x to 19.3x on the driver model's base EBITDA); on this note's convention the top targets only work with FY27 EBITDA of about $6.25 to 6.7bn (the joint solve's $220 row) or a multiple the cross-section does not support.

### 3.4 Method 3: reverse DCF at each price

MEASURED (`A_reverse_dcf.csv`). Same fade DCF as the management note (`mgmt_implied_model.py`: PV at 30 Sep 2026 of FY27-FY36 FCF with FY28 growth fading linearly to terminal by FY36, mid-year discounting, Gordon terminal), reproduced exactly: at $170.19 with WACC 10% and terminal 3% the required FY28 starting growth is 4.61% on delivered reported FCF $5,941m and 15.95% on SBC-adjusted FCF $4,005m (management note: 4.6% / 16.0%); Literal 5.60%, Ambition 2.74% (note: 5.6 / 2.7). Extended:

| FY27 FCF basis, WACC / terminal | $150 | $165 | $170.19 | $179.5 | $185 | $197.5 | $220 |
|---|---|---|---|---|---|---|---|
| Delivered reported $5,941m, 10% / 3.0% | 0.6% | 3.6% | 4.6% | 6.3% | 7.2% | 9.3% | 12.6% |
| same, 9% / 3.0% | -3.4% | | 0.4% | | | | 8.1% |
| same, 11% / 3.0% | 4.4% | | 8.5% | | | | 16.8% |
| same, 10% / 2.5% | 2.1% | | 6.1% | | | | 14.2% |
| same, 10% / 3.5% | -0.9% | | 3.0% | | | | 10.9% |
| Delivered SBC-adjusted $4,005m, 10% / 3.0% | 11.9% | 15.0% | 16.0% | 17.7% | 18.6% | 20.7% | 24.2% |
| same, 9% / 3.0% | 7.4% | | 11.3% | | | | 19.3% |
| same, 11% / 3.0% | 16.0% | | 20.2% | | | | 28.8% |
| same, 10% / 2.5% | 13.5% | | 17.6% | | | | 26.0% |
| same, 10% / 3.5% | 10.2% | | 14.2% | | | | 22.4% |
| Literal reported $5,738m, 10% / 3.0% | 1.6% | 4.6% | 5.6% | 7.3% | 8.2% | 10.3% | 13.6% |
| Ambition reported $6,347m, 10% / 3.0% | -1.2% | 1.8% | 2.7% | 4.4% | 5.3% | 7.4% | 10.7% |

Reading. On reported FCF the whole tape requires FY28 FCF growth of 0.6% to 12.6%, all below the FY27 revenue growth the same prices imply through the multiple: on reported FCF the stock is not expensive at any point on the tape, and the $150 end prices ABNB as an ex-growth cash flow. On SBC-adjusted FCF the requirement is 12% to 24%, above the implied revenue growth at every price. The WACC sensitivity (9% to 11%) is worth about 8pp of required growth at every price, larger than the whole spread between the bear and mean targets; the terminal growth sensitivity is about 3pp. The reported-vs-SBC-adjusted gap (11pp at every price) is the SBC debate and it does not move with the price.

## 4. Method 4: decomposing implied revenue growth into nights, ADR, FX and take rate

### 4.1 Does the identity hold in history?

MEASURED (`A_decomposition_history_check.csv`, `_annual.csv`; `02_kpi_panel_quarterly.csv`, 1Q23 to 2Q26). Two checks. The exact identity revenue = nights x reported ADR x reported take rate holds to a mean absolute residual of 0.17pp in logs (disclosure rounding of nights and GBV). Management's decomposition, nights + ADR ex-FX + revenue FX after hedging with the take rate flat, leaves a residual that is the RNPL book-versus-stay timing gap plus any true take-rate change:

| Quarter | Revenue y/y | Nights | ADR ex-FX | Revenue FX pp | Sum (logs) | Residual pp | Reported take rate y/y |
|---|---|---|---|---|---|---|---|
| 3Q24 | 9.9% | 8.5% | 2.0% | 0.0 | 10.7% | -0.7 | +0.1% |
| 4Q24 | 11.8% | 12.4% | 2.0% | 0.0 | 14.6% | -2.5 | -1.5% |
| 1Q25 | 6.1% | 7.9% | 1.0% | -2.0 | 6.8% | -0.7 | -0.9% |
| 2Q25 | 12.7% | 7.4% | 1.0% | 0.0 | 8.5% | +3.8 | +1.6% |
| 3Q25 | 9.7% | 8.8% | 2.0% | 0.0 | 11.0% | -1.1 | -3.7% |
| 4Q25 | 12.0% | 9.8% | 3.0% | +1.0 | 14.3% | -2.0 | -3.3% |
| 1Q26 | 17.9% | 9.2% | 4.0% | +3.0 | 16.9% | +0.8 | -1.1% |
| 2Q26 | 16.5% | 10.3% | 4.0% | +4.0 | 19.3% | -2.4 | +0.7% |
| 1Q23-2Q26 mean / s.d. | | | | | | +0.5 / 2.7 | |
| Trailing four / eight quarters | | | | | | -1.2 / -0.6 | |
| FY24 | 12.0% | 9.7% | 2.3% | 0.0 | | -0.2 | |
| FY25 | 10.3% | 8.4% | 1.8% | -0.1 | | 0.0 | |
| 1H26 | 17.1% | 9.7% | 4.0% | +3.6 | | -0.9 | |

The quarterly residual is large and noisy (s.d. 2.7pp; the arithmetic sum overstates the log sum by 0.2-1.0pp when the components are big, so the log form matters at 2026 growth rates). At the annual level it nets to within a point (FY24 -0.2, FY25 0.0, 1H26 -0.9), so the FY27 assumption of a zero residual and a flat take rate is defensible, with 1H26's -0.9 the warning that RNPL has been pulling it negative. ADR ex-FX and revenue FX in the panel are the letters' rounded figures. The 3Q25 take-rate baseline uses the management model's exact 3Q25 GBV ($22,892m); the panel rounds it to $22.9bn, a 1bp difference.

### 4.2 The Street's 3Q26 and 4Q26 components (ANCHOR: Bloomberg FA 4 Sep, in the brief)

MEASURED (`A_quarterly_consensus_decomposition.csv`). ADR FX points +0.3 / -0.4 and revenue FX +3.0 / -0.4pp are the management-model and WS29 assumptions. The case rows give each case's own nights and ADR ex-FX and the log-identity residual its revenue implies; the residual each builder quotes is in the CSV's `case_stated_residual_pp` column (the management model's multiplicative timing term; WS29's arithmetic-sum residual for the team, whose 3Q26 base is about -0.5 at ADR ex-FX 3.5 and whose 4Q26 base is -0.5; the -1.5 in `29_bridge_assumptions.csv` is the guide-implied residual at nights 11 and ADR 3, not the team base).

| | 3Q26 Street | 4Q26 Street | 3Q26 Delivered / Team base | 4Q26 Delivered / Team base |
|---|---|---|---|---|
| Revenue $m (y/y) | 4,744 (+15.9%) | 3,154-3,200, mid 3,177 (+14.4%) | 4,815 (+17.6%) / 4,771 (+16.5%) | 3,130 (+12.7%) / 3,111 (+12.0%) |
| Nights m (y/y) | 148.9 (+11.45% on 133.6m; the page says +11.1%) | 134.2 (+10.1%) | +11.5% / +9.9% | +10.5% / +8.9% |
| GBV $m (y/y) | 26,350 (+15.1%); nights x ADR 26,355 | 23,000 (+12.7%); nights x ADR 22,988 | | |
| ADR (y/y reported; ex-FX) | $177.0 (+3.3%; +3.0%) | $171.3 (+2.4%; +2.8%) | ex-FX +3.5% / +3.5% | +3.0% / +3.0% |
| Implied take rate vs prior year | 18.00% vs 17.89% (+12bp, +0.65%) | 13.81% vs 13.62% (+20bp, +1.4%) | | |
| Exact identity: nights + ADR + take rate | 15.9% (matches) | 14.3% (matches) | | |
| Management decomposition: nights + ADR ex-FX + FX | 18.2% | 12.7% | | |
| Residual, log identity (timing / take rate) | -2.0pp | +1.5pp | -1.1 / -0.6 | -0.6 / +0.2 (WS29 states -0.5 in arithmetic convention) |
| Revenue at a flat take rate on the Street's GBV | 4,714 | 3,132 | | |
| Street revenue above flat-take-rate revenue | +$30m | +$45m | | |
| EBITDA $m (margin) | 2,360 (49.7%) | 915 (28.8%) | | |

Reading. The components are internally consistent (nights x ADR reproduces GBV to 0.05%; nights + ADR + take-rate change reproduces revenue). The 3Q26 growth rate on the Bloomberg page (+11.1%) is 0.35pp below 148.9m / 133.6m; the component level is used here. The important finding is in 4Q26: the Street's revenue needs the take rate up 20bp y/y (residual +1.5pp) while its own 3Q26 has the residual at -2.0pp and the trailing four quarters average -1.2pp. Put the team's 4Q26 residual (-0.5pp) under the Street's own nights (+10.1%) and ADR (+2.8%): 4Q26 revenue is $3,115m (+12.1%), $62m below the Street's midpoint and $4m above the team's $3,111m. The Street's 4Q26 is therefore a take-rate and timing call, not a nights call; the 1.2pt nights gap between the Street (10.1%) and the team (8.9%) is worth only about $30m. Management's FY26 take-rate statement is "relatively flat" and the take rate has printed down y/y in four of the last six quarters.

Do the quarterly components add to the FY consensus? MEASURED (`A_quarterly_consensus_fy_reconciliation.csv`):

| Item | Value | Against |
|---|---|---|
| 1H26 actual $6,286m + Bloomberg FA 3Q26 $4,744m + 4Q26 mid $3,177m | $14,207m (+16.1%) | FY26 consensus $14,100-14,160m: the quarters sum $50-110m above the FY ($126m on Zacks' own Q3 + Q4 vs its FY $14,100m) |
| 1H26 + 3Q26 guide mid $4,730m + 4Q26 at the FY floor (15%) | $14,077m, 4Q26 $3,061m | the guide floor is $116m below the Street's Q4 midpoint |
| FY26 nights from the components | 587.6m (+10.2%) | Delivered 588.2m (+10.3%) |
| FY26 GBV from the components | $105.75bn (+15.8%) | Delivered $106.06bn |
| FY26 ADR from the components | $179.97 (+5.1%) | Delivered $180.32 |
| FY26 take rate from the components | 13.435% (+0.2%, +3bp) | FY25 13.409%; "relatively flat" |
| Street FY27 $15,745m | +11.4% on its own FY26 mid $14,130m | +10.6% on the delivered FY26 base used in this note |
| Street FY27 EPS $6.08 through the delivered P&L at 36.2% | needs revenue of $16,029m | or a 36.8% margin on $15,745m: the Street's EPS is about 60bp of margin richer than its revenue (or the vendors' EPS is partly non-GAAP; S&P's note says its EPS is adjusted) |

So the Street's quarterly components and FY numbers are not the same panel: the quarters sum to a FY26 about $80m above the FY consensus and land on the delivered case for nights, GBV and ADR, with revenue $24m below it. The Street FY26 is the delivered case; the Street FY27 is 2pp below it. The FY27 nights figure the Street would need for its own revenue at this note's decomposition is +8.1% (on the delivered FY26 base; +8.8% on its own FY26 base).

### 4.3 Implied nights at each price

JUDGEMENT on the MEASURED solve (`A_implied_nights.csv`, `A_implied_nights_sensitivity.csv`). FY27 revenue growth from the primary joint solve; ADR ex-FX +3.0% (ANCHOR: management "moderate increase" and team H note); revenue FX -0.6pp (ANCHOR: WS29 consensus EUR path); take rate flat; residual 0. Nights base FY26 delivered 588.2m (the Street's components give 587.6m, 0.1% lower).

| Price | FY27 revenue growth (mapping range) | FY27 nights growth, proportional, ADR +2% | ADR +3% (base) | ADR +4% | Fitted-line 1 s.e. band (ADR 3%) | Chained-Street mapping | Realised units | If residual at the trailing-four mean (-1.2pp) | FY27 nights m (base) | 1H27 nights growth if the Street's 2H26 is taken as given (FX -0.9pp) |
|---|---|---|---|---|---|---|---|---|---|---|
| $150.00 | 1.4 to 7.2% | 5.7% | 4.7% | 3.7% | 3.4 to 6.0 | -1.0% | 3.4% | 5.9% | 616 | -0.7% |
| $165.00 | 8.1 to 10.4% | 8.9% | 7.9% | 6.8% | 6.6 to 9.2 | 5.6% | 6.5% | 9.1% | 634 | 5.9% |
| $170.19 | 10.4 to 11.5% | 10.0% | 8.9% | 7.9% | 7.5 to 10.3 | 7.8% | 7.6% | 10.2% | 641 | 8.2% |
| $179.50 | 13.4 to 14.4% | 11.9% | 10.8% | 9.7% | 9.2 to 12.4 | 11.7% | 9.4% | 12.1% | 652 | 12.1% |
| $185.00 | 14.5 to 16.7% | 13.0% | 11.9% | 10.8% | 10.1 to 13.6 | 14.0% | 10.5% | 13.2% | 658 | 14.3% |
| $197.50 | 17.0 to 21.9% | 15.4% | 14.3% | 13.2% | 12.1 to 16.5 | 19.0% | 12.9% | 15.6% | 672 | 19.4% |
| $220.00 | 21.2 to 30.8% | 19.6% | 18.4% | 17.3% | 15.5 to 21.4 | 27.7% | 17.1% | 19.8% | 697 | 28.1% |
| Reference: Literal / Delivered / Ambition | 9.8 / 12.6 / 18.0% | | 9.0 / 10.0 / 12.0% (management's own nights) | | | | | | 636 / 647 / 662 | |
| Reference: Street $15,745m / Team base $15,804m | 10.6 / 11.05% | | 8.1% (derived) / 9.2% (WS10 build) | | | | | | | |

Reading. At $170.19 the market prices FY27 nights growth of about 8 to 9% (7.8 to 8.9 across the mappings, 7.5 to 10.3 on the fitted-line band, 7.9 to 10.0 on ADR +4 / +2, about 7.6% in realised units), which is the Street's implied 8.1%, the guide-literal 9.0% and the team's 9.2%, and a deceleration from FY26's 10.2-10.3%; it is a point or more below the delivered case's 10%. The mean sell-side target ($179.5) prices nights at 10.8 to 11.7%, i.e. no deceleration from FY26, which is the delivered case. The $150 bear tape prices nights at -1 to +5% depending on the mapping (the team's WS29 bear has 5.8% but with FX at -2.6pp and ADR at +1%, so its revenue is +0.6% and the joint solve prices it at $121); $220 prices 18 to 28% nights growth, which no management statement supports and which the ambition case (12%) reaches only with a 20bp take-rate lift and a 37% margin. Every point of ADR is a point of nights in the other direction; the residual at its trailing mean adds 1.2-1.4pt of nights at every price. If the Street's 2H26 is taken as given, the price implies 1H27 nights growth of 8.2% (FX -0.9pp from the WS29 path), and $150 implies 1H27 nights flat to down.

Cross-check against the elasticity anchor (1pt of 3Q26 nights = ~$46m revenue): a point of FY27 nights is 1% of FY27 revenue, $159m, $57m of EBITDA, worth $1.54 a share on the price's fixed 16.0x multiple ($1.59 at 16.5x) and about $4.90 a share (2.9%) on the joint solve, where the same point also moves the NTM multiple by 0.4 turns ($4.82 per point of revenue growth; `A_joint_solve_checks.csv`). Between $165 and $179.5 the table moves 2.9pp of FY27 growth for $14.50, i.e. $5.00 a point, consistent with WS12's one turn = $9.11 a share.

## 5. Method 5: comparison table and where the price sits

MEASURED arithmetic on JUDGEMENT mappings (`A_comparison_table.csv`, `A_case_implied_prices.csv`, `A_nearest_case_by_price.csv`). All FY27 growth on the delivered FY26 base $14,231m. Price-point rows show the mapping range (proportional to chained-Street); the case-implied prices use the proportional mapping.

| Case or price | FY27 revenue $bn | FY27 growth | FY27 adj. EBITDA $bn (margin) | FY27 EPS | FY27 nights growth | NTM revenue growth | EV / FY27 EBITDA at $170.19 | Price at which the joint solve returns this case |
|---|---|---|---|---|---|---|---|---|
| $150 (JUDGEMENT, tail) | 14.4 to 15.3 | 1.4 to 7.2% | 5.22 to 5.52 (36.2%) | 5.69 | -1 to 4.7% | 8.6% | 14.5 to 15.3x at $150 | |
| $165 | 15.4 to 15.7 | 8.1 to 10.4% | 5.57 to 5.69 | 5.92 | 5.6 to 7.9% | 11.8% | 15.6 to 16.0x at $165 | |
| $170.19 | 15.7 to 15.9 | 10.4 to 11.5% | 5.69 to 5.75 | 6.00 | 7.8 to 8.9% | 12.9% | 16.0 to 16.2x | |
| $179.50 | 16.1 to 16.3 | 13.4 to 14.4% | 5.84 to 5.89 | 6.14 | 10.8 to 11.7% | 14.8% | 16.6 to 16.7x at $179.5 | |
| $185 | 16.3 to 16.6 | 14.5 to 16.7% | 5.90 to 6.01 | 6.22 | 11.9 to 14.0% | 15.9% | 16.8 to 17.1x at $185 | |
| $197.50 | 16.6 to 17.3 | 17.0 to 21.9% | 6.03 to 6.28 | 6.39 | 14.3 to 19.0% | 18.4% | 17.3 to 18.0x at $197.5 | |
| $220 (JUDGEMENT, tail) | 17.3 to 18.6 | 21.2 to 30.8% | 6.25 to 6.74 | 6.70 | 18.4 to 27.7% | 22.7% | 18.1 to 19.5x at $220 | |
| Management Literal | 15.63 | 9.8% (11.0% own base) | 5.55 (35.5%) | 5.72 | 9.0% | 12.1% | 16.6x | $162 (-5%) |
| Management Delivered | 16.02 | 12.6% | 5.80 (36.2%) | 6.08 | 10.0% | 14.0% | 15.9x | $175 (+3%) |
| Management Ambition | 16.79 | 18.0% (17.0% own base) | 6.21 (37.0%) | 6.68 | 12.0% | 17.1% | 14.8x | $203 (+19%) |
| Street (Bloomberg FA / Zacks / S&P, 3-4 Sep) | 15.75 (range 14.99-16.29, 13 estimates) | 10.6% (11.4% own base) | 5.70 (36.2% assumed) | 6.08 | 8.1% (derived) | n.a. | 16.1x | $166 (-2.5%) |
| Team base (WS29 / WS30) | 15.80 | 11.05% (11.6% own base) | 5.76 (36.4%) | 5.90 | 9.2% | n.a. | 16.0x | $168 (-1%) |
| Team bear / bull (WS29) | 14.32 / 16.91 | 0.6% / 18.8% | | | 5.8% / 11.5% | | | $121 / $207 |

Plainly: the current price is the Street to the team base, within half a point of growth on either mapping, and 1.1 to 2.2pp (about $5 a share) below the delivered case; in realised-growth units it is on or just below the Street. The sell-side mean ($179.5) is the delivered case plus 1 to 2pp; the sell-side p75 ($197.5) is the ambition case; the top target ($220) is 3 to 13pp above the ambition case depending on the mapping and needs 18 to 28% nights growth or a multiple of 18 to 19.5x FY27 EBITDA on ambition-level numbers. The $150 bear tape is 2.6 to 8.4pp below the guide-literal case: it assumes management's FY26 floor is delivered and FY27 then decelerates to somewhere between +1% and +7% revenue (nights -1 to +5%), i.e. that the 2025-26 re-acceleration (RNPL, the three product features, the World Cup) is lapped and not replaced; on the base-consistent mapping it is 10.2%, which shows how much of the tail spread is the fixed-base convention. It is not as bearish as the team's WS29 bear, which the joint solve prices at $121 and the lowest live target (Morgan Stanley $125) matches.

## 6. What would change these conclusions

1. A consensus-based NTM series instead of the guide proxy (WS12's own first recommendation). If the multiple is regressed on consensus growth the intercept and slope both change; my expectation (JUDGEMENT) is a similar slope and an implied growth at the price about a point lower, which is what the realised-units column already shows. It would not change the tails.
2. The 5 Nov print. A 4Q26 guide implying 18%+ revenue growth would put the Aug-Sep 2026 points on the fitted line and would validate spec F (the "market believes the guide" line), under which $170.19 already prices 15.7% NTM growth and the upside from growth is small; a guide at or below the Street's $3,154-3,200m leaves the price 1-3 turns below the line and the joint solve's reading (12.9%) stands. Either way the print will move the multiple more than the estimate (WS12: 71-84% of print-day moves are multiple).
3. Margin. The joint solve runs at 36.2% for FY27. At 35.5% the implied FY27 growth at the price is about 2pp higher on the hold (10.4% at 16.5x) and the implied nights about 2pt higher; at 37.0% about 2pp lower. The regression says the market does not pay for margin, so the margin enters through EBITDA only.
4. The residual. If RNPL timing keeps the revenue residual at -1pp through FY27 (1H26 was -0.9), every implied nights figure in section 4.3 is about 1.3pt too low; if the take rate rises 20bp (the Street's 4Q26 and the ambition case), they are about 1.5pt too high.
5. The regression's identification. A longer sample (another two years of 2026-28 data with the guide and the multiple moving) would settle whether the 0.4 slope is a law or the 2023-to-2025 de-rating in disguise; until then the band, not the point, is the quotable number, and at the tails the mapping range on top of it.

## 7. Caveats, in order of importance

1. The slope and level are weakly identified. t 3.1 with Durbin-Watson 0.53 (about 16 independent observations), insignificant in 12-month changes of the forward multiple (+0.07, t 1.3), sign-unstable across 24-month rolling windows (-0.18 to +0.94) and near zero in 2024-26 alone (+0.14, t 0.6). The fitted-line 1 s.e. band is +/- 1.4pp of NTM growth at the price and +/- 3pp at $220; the residual scatter about the line is +/- 5pp at every price. The point estimate at $170.19 is robust to leave-one-out (+/- 0.5pp) only because the price sits near the sample mean.
2. Units. The growth variable is the guide proxy, which has overstated realised NTM growth by 1.4pp on average (RMSE 2.9pp, n 12, sign unstable) and reads 17.8% today against 15.7% consensus; the implied growth is in proxy units, and the realised-units column subtracts the mean bias. The regression cannot distinguish "12.9% growth at 17.7x" from "17.8% growth at 16.9x, not believed"; specs A and F in 2.2 are those two readings and differ by 2.8pp at the price.
3. FY27 and nights are JUDGEMENT on the MEASURED NTM solve and stack three assumptions on it: the NTM-to-FY27 mapping (1.1pp at the price, 6-10pp at the tails, with the fixed-base growth convention inflating the tail spread), the ADR ex-FX assumption (one point of ADR is one point of nights), and the zero residual (annual residuals have been within a point but quarterly ones have a 2.7pp standard deviation and the Street's own 4Q26 needs +1.5pp).
4. Convention. Spot EV (597.0m shares, $9,593m net cash) throughout, which matches the brief's 15.9x anchor; the management note's target prices use end-FY27 shares and net cash, which is worth about one turn (6pp of growth on a fixed multiple). The margin sensitivities run through EBITDA only because the regression finds no margin effect. Street FY27 EBITDA is revenue x 36.2% because no EBITDA consensus exists; the Street's EPS ($6.08) is about 60bp of margin richer than its revenue on the delivered P&L mechanics, or partly non-GAAP.
5. The Bloomberg 3Q26 nights growth on the page (+11.1%) does not match 148.9m / 133.6m (+11.45%); the component level is used. Zacks' and Bloomberg's quarterly revenue estimates sum to a FY26 $50-126m above the FY consensus.
6. Tests run in this workstream: 28 regression specifications, 90 leave-one-out fits, 108 rolling and expanding fits, 8 joint-solve specifications at 7 prices, 2 peer fits, 14 hold lenses, 36 reverse-DCF cells. The one result that survives the count is the monotone, in-band answer at the price; the slope's size and the tail numbers should be read as descriptive.

## 8. Changes made after the audit

Audit: `research/notes/reverse_dcf/audit_A.md`, findings in `data/processed/reverse_dcf/audit/audit_A_findings.csv`; verdict pass with fixes, all outputs reproduced. Applied: (1) the band is the fitted-line 1 s.e. band from the Newey-West covariance (delta method), added to `A_joint_solve.csv` for every regression spec as `implied_ntm_growth_lo_pct` / `_hi_pct` and `fy27_growth_proportional_lo_pct` / `_hi_pct`, with the residual-s.d. band alongside; the slope-only A-low / A-high rows remain, labelled SUPERSEDED. (2) FY27 is quoted as the range between the proportional and the chained-Street mappings, with the base-consistent proportional added (`fy27_growth_base_consistent_pct`); the direct FY27-basis solve is dropped from the headline and footnoted in the CSV as mis-specified; `implied_fy27_growth_at_170.19_pct` in `A_regression_specs.csv`, `A_regression_loo.csv` and `A_regression_rolling.csv` now carries the proportional value (11.51 for spec A) and the direct solve is in `implied_fy27_growth_direct_basis_at_170.19_pct`. (3) The realised-units reading is in the headline table and `A_headline.csv`; the nearest case at the price is "Street to team base". (4) The $150 and $220 rows are labelled JUDGEMENT and quoted as ranges. (5) Minor: $1.54 per nights point on the fixed multiple; 70/30 multiple-to-EBITDA split at the price (72/28 measured); 12-month-change window Jan 2023 to Sep 2026; rolling maximum in the window ending Jan 2026; the team 3Q26 / 4Q26 residuals recomputed from the team's own inputs and added to `A_quarterly_consensus_decomposition.csv` with the builders' stated residuals and their convention; the 3Q25 GBV source noted. Existing file and column names are unchanged; columns were added.

## Files written

Scripts (run in order with `py -3.13` from the repo root): `analysis/src/reverse_dcf/A_common.py` (anchors, OLS with Newey-West returning the covariance, solvers, mappings, fade DCF identical to the management model), `A_01_multiple_regressions.py`, `A_02_market_implied_solves.py`, `A_03_decomposition_comparison.py`.

Data, all under `data/processed/reverse_dcf/A/`:

| File | Contents |
|---|---|
| `A_regression_specs.csv` | 28 specifications: window, n, coefficients, Newey-West t, R2, Durbin-Watson, fitted multiple at 12.6% growth, implied NTM growth at $170.19, implied FY27 growth (proportional mapping) and the direct-basis solve in its own column |
| `A_regression_loo.csv` | leave-one-month-out and leave-one-reported-quarter-block-out fits for the two primary specs |
| `A_regression_rolling.csv` | rolling 24-month and expanding-window fits |
| `A_regression_fitted_residuals.csv` | monthly fitted multiple and residual, 2023-26 |
| `A_ntm_proxy_vs_realised.csv` | the guide proxy against realised NTM revenue growth by vintage |
| `A_price_points.csv` | the seven price points: market cap, EV (spot and end-FY27 conventions), multiples on each case |
| `A_joint_solve.csv` | joint solve by spec and price: NTM growth with the fitted-line and residual-s.d. bands, multiple, NTM revenue and EBITDA, realised-units growth, the FY27 mappings (proportional with band, chained Street with band, chained Delivered, base-consistent with band, mapping range, direct basis footnoted), FY27 revenue and EBITDA at three margins, EPS |
| `A_joint_solve_checks.csv` | monotonicity and 8-16% band checks by spec; EV-move split between multiple and EBITDA; value per point of growth on the joint solve and on a fixed multiple |
| `A_joint_solve_peer_crosssection.csv` | the same solve on the WS12 peer fits, with and without ABNB's premium |
| `A_simple_holds_grid.csv`, `A_simple_holds_long.csv` | price x lens grid of implied FY27 growth; long form with revenue, EBITDA, EPS, FCF and nights |
| `A_implied_multiples.csv` | multiples each price pays on the Street, management and team FY27 numbers |
| `A_reverse_dcf.csv` | FY28 starting FCF growth required at each price, four FCF bases, WACC 9-11%, terminal 2.5-3.5% |
| `A_decomposition_history_check.csv`, `A_decomposition_history_check_annual.csv` | the identity against 1Q23-2Q26 history, quarterly and annual |
| `A_quarterly_consensus_decomposition.csv` | Bloomberg FA 3Q26 / 4Q26 components decomposed, with the management and team cases' own components, log-identity residuals and stated residuals alongside |
| `A_quarterly_consensus_fy_reconciliation.csv` | do the quarterly components add to the FY consensus |
| `A_implied_nights.csv`, `A_implied_nights_sensitivity.csv` | implied FY27 and 1H27 nights by price: proportional point, fitted-line band, chained and base-consistent mappings, realised units, ADR and residual sensitivities |
| `A_comparison_table.csv`, `A_case_implied_prices.csv`, `A_nearest_case_by_price.csv`, `A_headline.csv` | section 5 and the headline, with the range, realised-units and label columns added |
