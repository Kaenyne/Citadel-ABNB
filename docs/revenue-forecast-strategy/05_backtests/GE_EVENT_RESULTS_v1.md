# GE-EVENT results: GBV conversion, guidance comparisons and daily price legs

15 September 2026. Author: chart_auditor. Base commit `2dfe0c2a1852181a246f4b6b9072e05e844d52d5`. Fixed audit plan: `GE_PREREG_v1.md` and `analysis/src/forecast_methods/gbv_event_v1/events/README.md`. Canonical outputs: `data/processed/forecast_methods/gbv_event_v1/events_v1/run_v3/`.

**Completed descriptive audit; no forecast-to-return strategy is promoted.** The full 23-event ledger produces 20 numeric forward guides, 16 original attributed revenue-consensus comparisons and 15 cushion-adjusted comparisons. All twelve primary Holm-adjusted permutation p-values equal 1.0; every primary slope interval includes zero. This establishes neither that guidance has no economic importance nor that a position formed before earnings cannot work. It means these small, reused historical samples do not establish a stable guide-to-price mapping or justify a quantified trading-edge claim. The deliverable can proceed to the four-quarter Excel and two-page memo with conditional event scenarios and explicit falsifiers.

## Definitions and full sample

Let G be the first-issued next-quarter revenue-guide midpoint, C the recorded pre-event consensus for that quarter's eventual revenue, and c the pre-event trailing-eight median of actual revenue / first guide minus one. At least three published actuals are required; every actual publication date must strictly precede the event. The just-reported current quarter is excluded from this cushion calibration.

1. Raw different-object proxy: `100 * (G / C - 1)`.
2. Conditional implied-guide proxy: `100 * (G / (C / (1 + c)) - 1)`.

Both proxies become observable after guidance is published. C is an expectation for eventual revenue, not an observed expectation for management's guide. Dividing C by a historical cushion supplies an assumption, not missing market data. Monetary fields are USD millions; all surprise and return fields are percentage points when differenced or used in regressions.

The primary source is the original L0 `PG-<target>-revenue` row with explicit `pre_guide` role, finite positive value, usable PIT flag, attributed named vendor and eligible timestamp. Missing or quarantined rows remain missing. Of the 20 numeric-guide events, four original comparisons fail this rule: the guides for 2021Q4, 2022Q1, 2022Q2 and 2024Q3. Three earlier events have no numeric forward guide. One otherwise eligible event lacks three prior cushion observations. All 23 events remain visible in `event_panel.csv`; absent comparisons are not silently removed from the ledger.

All currently selected original consensus dates are date-only and rely on the documented morning-of-print convention. The code preserves raw timestamps and separately rejects explicit naive, exact-close or post-close times. Explicit aware times must be strictly before 16:00 New York. This is a conservative pre-event cutoff, not certification of each actual release time. The separately labelled DoltHub mirror panel selects its own latest snapshot strictly before the cutoff and never fills a primary hole.

Event W1/W2 are **print-quarter** slices beginning 2023Q1 / 2024Q1. They are nested and differ from forecast **guide-target-quarter** windows. No sample was selected for large returns, favorable signs or forecast success. Historical events were already examined in prior work; this is not a fresh holdout.

## Price definitions and primary results

The earnings gap runs from the event-date close to the next matched ABNB/QQQ open. The regular session runs from that open to that session's close. Excess return is ABNB simple return minus QQQ simple return. Close-to-close is computed directly and reconciles to gap excess plus session excess plus the difference of each security's cross term. Excess legs must not themselves be compounded as if they were a tradable security.

The gap includes release, call, overnight and premarket effects together. Daily OHLC supplies authentic daily prices but cannot isolate a call leg, reveal wick order or validate intraday stop execution. Five- and twenty-session open-entry returns are separate secondary horizons in the outputs, not substitutes for the two primary legs.

Slopes below are excess-return percentage points per one percentage point of the proxy. Confidence intervals are approximate HC1 OLS intervals with t(n-2) critical values. Each regression has two fitted parameters, intercept and slope. Pearson permutation p-values use 19,999 fixed-seed permutations and a plus-one correction; exchangeability is an assumption. Pearson Fisher intervals, Spearman rank correlations and Spearman asymptotic p-values are included in `associations.csv`. Holm covers the twelve rows below, not an undisclosed selection of favorable results.

| Sample | Proxy | Leg | n | Pearson r | Slope | Approximate 95% CI | Permutation p | Holm p |
|---|---|---|---:|---:|---:|---|---:|---:|
| All | G / revenue C | Gap | 16 | 0.324 | 1.117 | [-0.966, 3.200] | 0.221 | 1.000 |
| All | G / revenue C | Session | 16 | 0.310 | 0.514 | [-0.294, 1.321] | 0.241 | 1.000 |
| All | G / implied guide | Gap | 15 | 0.287 | 0.974 | [-1.043, 2.990] | 0.301 | 1.000 |
| All | G / implied guide | Session | 15 | 0.208 | 0.336 | [-0.359, 1.031] | 0.456 | 1.000 |
| W1 print | G / revenue C | Gap | 13 | 0.217 | 0.850 | [-1.977, 3.677] | 0.478 | 1.000 |
| W1 print | G / revenue C | Session | 13 | 0.104 | 0.185 | [-0.999, 1.369] | 0.735 | 1.000 |
| W1 print | G / implied guide | Gap | 13 | 0.130 | 0.550 | [-2.393, 3.494] | 0.671 | 1.000 |
| W1 print | G / implied guide | Session | 13 | 0.071 | 0.136 | [-0.913, 1.185] | 0.819 | 1.000 |
| W2 print | G / revenue C | Gap | 9 | 0.207 | 0.865 | [-3.429, 5.159] | 0.583 | 1.000 |
| W2 print | G / revenue C | Session | 9 | -0.047 | -0.087 | [-1.773, 1.600] | 0.911 | 1.000 |
| W2 print | G / implied guide | Gap | 9 | 0.187 | 0.859 | [-3.828, 5.546] | 0.620 | 1.000 |
| W2 print | G / implied guide | Session | 9 | -0.041 | -0.083 | [-1.947, 1.781] | 0.924 | 1.000 |

All-event sign counts are economically informative. Seven raw negative comparisons have mean gap excess -3.70%, but two of seven have a positive gap; nine raw positives average +0.76%, with only four of nine positive gaps. All fifteen eligible **cushion-adjusted comparisons are positive**; their mean gap excess is -0.77%, with six positive gaps. There is no negative adjusted-proxy subgroup from which to estimate a short-rule hit rate or downside magnitude. A guide that clears a hypothetical cushion-adjusted bar is not sufficient to predict a positive stock response.

`influence.csv` contains every event and year deletion for the primary legs. For the full sample, raw-gap slopes range 0.718 to 2.008 after individual event deletions and 0.621 to 2.098 after year deletions; adjusted-gap slopes range 0.463 to 1.895 and 0.511 to 2.119 respectively. The adjusted-session slope changes sign under year deletion (-0.236 to 0.615). These are sensitivity descriptions, not additional independent tests.

The only optional control is current-print revenue surprise, sourced from the original attributed `AP` row and compared on identical complete rows. There are three fitted parameters. Full-sample controlled gap slopes are 1.114, CI [-1.061, 3.289], for the raw proxy and 1.044, CI [-1.293, 3.382], for the adjusted proxy; both session intervals also include zero. This does not isolate nights guidance, margins, GBV, FX, valuation or other simultaneous news. No conclusion about nights guidance being the unique driver is supported.

## Vendor sensitivity

The uniformly selected DoltHub mirror is a secondary panel, not a new independent vendor family or an automatic repair of the primary sample. Raw-gap n=20 gives r=0.402 and slope 0.771, CI [-0.222, 1.763]. Adjusted-gap n=16 gives r=0.543 and slope 1.547, CI [0.314, 2.780]. This favorable secondary interval is retained openly in `vendor_sensitivity.csv`; it changes both values and coverage, including the large negative 2024Q2-print event whose original primary consensus was quarantined. It does not override the primary family or prove a stable strategy. Its session intervals include zero. Cross-panel results cannot be attributed only to vendor choice without matching the event sets.

## Earlier-origin GBV forecast comparison

`pre_event_forecast_join.csv` preserves all 21 frozen candidate rows: seven abstentions, thirteen historical forecasts with an observed guide event and one live unmatched Q4 2026 forecast. Missing outcomes are not dropped from that table. These are chronologically reconstructed forecasts, not timestamped archived trades. The origin-specific consensus is the explicit DoltHub snapshot strictly before the forecast origin, not the event-morning value. The historical origin lead is recorded per event.

Candidate guide and Street implied guide use the same origin cushion divisor d. Therefore:

`(candidate_revenue / d) / (origin_Street_revenue / d) - 1 = candidate_revenue / origin_Street_revenue - 1`.

The common cushion cancels. The early-origin adjusted comparison is revenue disagreement expressed on a hypothetical common guide basis; it supplies no independent information about market expectations for management's guide. The separate candidate-guide versus revenue-consensus proxy retains its different-object label. Published realized proxies remain separate from candidate predictions.

The expanded target sample includes the guide for Q3 2026 issued on 6 August and has W1/W2 n=13/11. The frozen forecast-validation endpoint remains Q2 2026, n=12/10. Both are supplied explicitly to prevent sample substitution. The following secondary results use the common-cushion signal:

| Target window | Leg | n | Pearson r | Slope | Approximate 95% CI |
|---|---|---:|---:|---:|---|
| W1 through Q3 2026 | Gap | 13 | 0.374 | 1.220 | [-0.447, 2.888] |
| W1 through Q3 2026 | Session | 13 | 0.378 | 0.514 | [-0.687, 1.714] |
| W2 through Q3 2026 | Gap | 11 | 0.546 | 1.757 | [0.214, 3.300] |
| W2 through Q3 2026 | Session | 11 | 0.203 | 0.247 | [-1.104, 1.598] |
| Frozen W1 through Q2 2026 | Gap | 12 | 0.222 | 0.856 | [-1.769, 3.481] |
| Frozen W1 through Q2 2026 | Session | 12 | 0.021 | 0.029 | [-1.265, 1.323] |
| Frozen W2 through Q2 2026 | Gap | 10 | 0.446 | 1.750 | [-0.558, 4.058] |
| Frozen W2 through Q2 2026 | Session | 10 | -0.437 | -0.500 | [-1.283, 0.283] |

The favorable expanded-W2 gap interval is secondary and does not survive the requirement to establish the relation in both windows. In expanded W1, deleting calendar 2026 changes the gap slope to -0.376 (n=10). All event and year deletions are supplied in `pre_event_signal_influence.csv`. Origin-close to next-open/next-close excess-return associations are also supplied so an early position is not credited only with its final isolated earnings gap. For expanded W1 these slopes are 2.494, CI [-0.261, 5.249], and 3.100, CI [-0.621, 6.820]; the frozen-endpoint versions are 0.934, CI [-1.389, 3.257], and 0.916, CI [-1.496, 3.328]. No signed sizing, transaction-cost or borrow-cost strategy has been run, and these are not P&L backtest results. Post-announcement drift is not a prerequisite for the pre-event thesis.

## Reproduction and acceptance

Exact successful commands from the worktree root:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -m pytest analysis/src/forecast_methods/gbv_event_v1/events/test_events.py -q
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/gbv_event_v1/events/run.py --out data/processed/forecast_methods/gbv_event_v1/events_v1/run_v3
```

Both exited 0; twelve focused tests passed. They cover per-security compounding, benchmark date mismatch, primary vendor and chronology rejection, no silent DoltHub fallback, cushion future/current-event exclusion, surprise definitions, Holm behavior, degenerate regression and explicit before/at/after-close timestamp boundaries. All 115 comparisons to the frozen return table pass; the maximum compounding residual is approximately 4.31e-14 percentage points. The receipt binds source and output SHA256 hashes. For a new replay use a new output directory such as `run_replay_v1`; overwrite is refused.

The initial `run_v1` attempt exited 1 before statistical output because the guide-source adapter used an incorrect metric name. `run_v1/ATTEMPT_FAILURE.json` retains the failure and repair. `run_v2` then completed. Source review identified a future-data guard edge case: timestamp normalization could admit an explicit post-close time under a date-only morning convention. The final code preserves raw timestamps and treats those cases separately. Run_v3 primary association, control, cushion, guide tieout, influence, sign-group, vendor, forecast-join and return-tieout CSVs are byte-identical to run_v2. The event panel adds two raw timestamp columns and more explicit eligibility labels. Supplementary forecast statistics add fixed-endpoint windows and the complete influence table. No historical numeric input was changed.

Independent peers reproduced 736 saved-source checks and 316 source/arithmetic checks against run_v2 without importing the author's calculation functions. Final-version closure in `GE_EVENT_INDEPENDENT_REVIEW_v2.md` passes twelve focused tests and 2,004 separate source/output/OLS/influence checks, binding the exact run_v3 receipt, code and tests. The source peer's `data/processed/forecast_methods/gbv_event_v1/sources_v1/review_v2/receipt.json` also records 314 of 314 source/arithmetic checks against run_v3 event and earlier-origin tables, with maximum absolute error 3.64e-12. These additive reviews preserve the original review and accept the bounded descriptive scope, not a trading strategy. Engineering check counts are not extra historical observations. `events_v1/canonical_v1.json` binds the final code, tests, README and numerical receipt for reproduction.

No existing tracked file, registry, scorer, shared model, source data or commit was modified by this package. No new forecast registration was created, so harness rescoring is outside this package. The parent owns the workboard status update and final publication review.

## Workbook and memo handoff

Use `event_panel.csv` for complete per-event eligibility, original source labels, two distinctly named published-guide proxies, daily ABNB/QQQ prices and return legs. Use `associations.csv` for primary uncertainty/multiplicity, `sign_groups.csv` for counts, `influence.csv` for all deletions and `current_print_control.csv` for matched controls. The separate vendor and pre-event files must retain their sensitivity/reconstruction labels. `chart_data.json` provides the primary event/association/sign/vendor records; forecast records are the separately named CSVs. The primary chart universe is 23 ledger events with signal-specific eligible n, not 23 fully observed guide comparisons.

A defensible display is a pair of scatter plots for gap and session, complete event labels, confidence intervals and transparent missing-data counts. Daily OHLC candles may be drawn as daily candles only. There is no timestamped call-price panel in the held evidence. This package does not establish the cause of a candle leg, does not forecast a guaranteed short return and does not require a 12-month valuation target to evaluate the pre-earnings position.

## RESUME

GE-EVENT is complete for its descriptive scope. Consume canonical run_v3 in the Q3 2026–Q2 2027 Excel and two-page memo alongside GE-FORECAST and GE-SOURCE, preserving the common-cushion identity and distinct expectation/origin/sample definitions. The useful next step is a transparent four-quarter GBV-conversion model with conditional guide and event scenarios, falsifiers and source dates. If a later deliverable claims a measured trading edge, preregister the actual information-at-entry, sizing, exit and cost rules and show qualifying event counts and event/year robustness. Do not manufacture guide expectations, intraday data or an affirmative short conclusion to fill the current evidence gaps.
