# The pitch model workbook: `model/ABNB_pitch_model.xlsx`

Krish with Claude (Fable 5.1), 16 Sep 2026. One workbook that shows everything the team has built for forecasting the
upcoming quarters, for a reader who has not seen the repo. Built by `analysis/src/model_workbook/build.py` from the
processed CSVs; nothing is typed in. Excel recalculates it on build so the cached values are present for viewers.

## What it contains

| Tab | Content | Source packages |
|---|---|---|
| Cover | What it is, colour conventions, tab map, the numbers in one table (Street / base / short), the pitch in six lines, provenance and the kill list | all below |
| Income Statement | 1Q23A-4Q27E quarterly and FY23-FY27E: nights, GBV, ADR, revenue, five cash cost lines, adjusted EBITDA, SBC, GAAP operating income, interest, tax, net income, shares, EPS. Scenario dropdown (B3) drives the forecast columns. Street and Short comparison rows underneath | 02_financial_panel, abnb_driver_history_quarterly, 40_line_build |
| Revenue Model | Nights (regional 2026 build, 2027 lap build), ADR ex-FX and FX, GBV, take rate, bridge conversion, revenue and band; bear/bull/short scenario rows; Bloomberg and LSEG consensus on every KPI; the 3Q26 guide in force vs the model; the 4Q26 guide the model implies (cushion arithmetic, base and short); guide history since 4Q21 | h2_bridge_v3, 06_fy27_path_v2 (v2b), 05_fx_schedule, E_street_distribution_vs_team, 03_consensus_pit, abnb_revenue_guidance_vs_actual |
| Margins | Cost stack line by line with the driver sub-lines (fees, chargebacks, hosting, ops variable/fixed, marketing vs field), the 3Q26 sentence reconciliation, the 5 Nov card (calibrated run), FY26 sentence expectation and budget identity, floor breakeven, FY27 revenue x cost grid, sensitivities, macro flex, the short case quarter by quarter, seasonality | 40_line_build, 23_final_model, M3_guide_policy_margin |
| Operating Schedules | Bookings and nights per booking, unit economics, revenue by region, the 2027 nights and ADR builds term by term, three FX paths, unit-cost drivers, below-EBITDA items, the full `40_params.csv` | 40_line_build, 06_fy27_path_v2, 05_fx_schedule, airbnb_regional_revenue_quarterly |
| 5 Nov & Street | Key items side by side (Street / base / short / management delivered) with gaps; the 5 Nov sequence (print vs guide, 4Q26 guide, FY26 sentence); price implications: joint-solve and fixed-multiple prices by case, the short case derived, the reaction-function scenarios, options event sd, the repricing ladder | reverse_dcf/market, A, B, C, E; mgmt_implied_summary |
| Stock Chart | Annotated close since the IPO (11 earnings days of 7%+, every print tick, 5 Nov marked), every print's 1/5/20-day reaction, all 41 big moves by driver, read-across to 5 Nov | abnb_daily_close, abnb_big_moves_7pct, abnb_earnings_reactions, reverse_dcf/E, B |
| Reverse DCF - Mgmt | Literal / Delivered / Ambition annual and quarterly, inputs by case, implied prices by lens, reverse-DCF growth, management statements | reverse_dcf/mgmt_implied_* |
| Reverse DCF - Market | Who is pricing what, cases, price ladder, options, sell-side tape, reaction function, positioning card, caveats | reverse_dcf/market, A-E |
| Scenario Data | The block behind the dropdown: 10 scenarios x 33 lines x 6 quarters | 40_lines_quarterly, 40_short_case_quarterly |

Scenarios in the dropdown: Base (team model); Short case, costs at budget (the pitch); Short case with the 4Q26 marketing
cut that holds the 35.5% floor (derived from `40_short_case_summary.csv`); evidence-only costs; revenue bear/bull; cost
bear/bull; both bear/bull.

## Decisions taken

1. **Base and Short both run through the workbook.** The 15 Sep short case is the pitch and is the dropdown default (changed 16 Sep at Krish's request); the base is the team model
   it is measured against. Consensus is a comparison column only, per the rule. The management-delivered case appears
   on the 5 Nov & Street tab for FY26/FY27.
2. **Consensus and the guidance expectation live inside the Revenue Model and Margins tabs** (as Krish suggested), with
   a compact 5 Nov & Street tab that brings the key items and the price implication together.
3. **History G&A is on the ex-lodging-reserve basis** (`ga_cash_ex_lodging`), so 4Q23's ~$1bn reserve sits in the
   "other GAAP items" reconciling line, not in the cash stack; the residual "other add-backs" line is then within
   $15M every quarter and adjusted EBITDA ties to the reported figure.
4. **Adjusted EBITDA = revenue - cash costs + D&A** in both history and forecast (the line build's identity); GAAP
   operating income = adjusted EBITDA - D&A - SBC (+ reconciling items in history).
5. **Short-case price** is not in the reverse-DCF run (which predates it); the tab derives it two ways, labelled: a
   linear interpolation between the team bear and Street rows on FY27 revenue for the joint solve ($140), and the
   fixed 16.5x arithmetic on its own FY27 EBITDA ($148). Both are indicative.
6. **FY28** is excluded from the income statement (the line build's FY28 is a roll-forward); it appears only on the
   Margins comparison table, flagged.

## Checks

- `qa.py`: zero formula-error cells on all ten sheets after Excel recalculation.
- Ties: 3Q26 adjusted EBITDA $2,419.6M (line build), FY26 $5,098.5M, FY27 $5,644.2M, EPS $2.91 / $5.28 / $5.93;
  FY23 adjusted EBITDA $3,653M, FY24 $4,041M, FY25 $4,297M (reported); implied 4Q26 guide midpoint $3,059M (bridge v3
  quotes the same); gaps vs Street: 3Q26 +$58M, 4Q26 -$15M, FY27 -$122M base, -$1,005M short.
- The FY26E total cash costs sum ($9,249M) differs from `40_annual.csv` ($9,250M) by the 1H26 other add-backs ($1M).

## How to rebuild and extend

```
py -3.13 analysis/src/model_workbook/build.py            # full build + Excel recalculation
py -3.13 analysis/src/model_workbook/build.py --only tab_is tab_scenarios --no-recalc --out <path>   # one tab, for testing
py -3.13 analysis/src/model_workbook/qa.py model/ABNB_pitch_model.xlsx [pdf_dir]   # error scan, optional PDF export per sheet
```

Each tab is a module in `analysis/src/model_workbook/tabs/` exposing `build(wb)`; `style.py` holds the conventions,
`data.py` the shared frames. `tab_scenarios` must build first (the Income Statement lookups need its ranges); the
build script reorders the sheets on save. When the line build or the bridge is re-run, re-run the build script and the
numbers flow through. If a new scenario is added to `40_lines_quarterly.csv`, add it to `data.SCENARIOS`.

Known limits: the dropdown drives only the tabs that have per-scenario lines (Income Statement, Margins, Operating
Schedules); the Revenue Model's decomposition exists only for base/bear/bull (06 v2b) and the short path's nights and
ADR. Regional nights exist for 2026 only. The stock chart is a matplotlib PNG (`model/figures/`), not a native chart.

## RESUME

Done: workbook built and checked. Next agent: (1) the short case is now the dropdown default; consider adding a short-case FY27 revenue decomposition (nights/ADR/FX/take by quarter) to the Revenue
Model, which today is a scaling of the team path; (2) re-run `build.py` after the September Inside Airbnb dumps
narrow the 3Q26 nights band (T trigger) and after any bridge/line-build re-run; (3) if the reverse-DCF run is refreshed
in late September (options re-pull), the 5 Nov & Street tab picks up the new CSVs automatically, but the short-case
price interpolation should be replaced by a proper joint-solve row in that run.
