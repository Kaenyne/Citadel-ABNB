# WS23: Triangulation: the final margin model, its forecasts, the workbook, and SYNTHESIS.md

Read `docs/margin-build/00_BRIEF.md`, then `docs/margin-build/notes/20_scoreboard.md`, `21_red_team.md`, `DISCUSSION.md` (the method agents'
rebuttals and adjustments), then every method note and WS01-06 notes. Slug: `23_triangulate`. Method name for the final registry object: `final-margin`.

## Build `analysis/src/margin_build/23_final_model/` (run.py rebuilds everything; README)

1. **Combination.** Per target and horizon, a weighting over the surviving objects (from WS20's recommendation, adjusted by the discussion
   outcomes): inverse-MAE or stacking weights learned leave-future-out on the PIT by_quarter errors (weights at vintage t use errors before t only),
   with a shrinkage toward equal weights and the guide-implied baseline where a guide exists. Register `final-margin__combined` (PIT replay of
   the combination itself, so the scorer can score it) with conformal quantiles from the PIT combination errors. Publish the weights table.
2. **Line model.** For the workbook and the pitch, the combined forecast must decompose into the six cost lines. Use the best surviving line
   objects (M1/M4 lines, M2 ratio lines, M6 flex for scenarios) and reconcile so lines sum to the combined EBITDA (allocate the residual to the
   discretionary lines in proportion to their PIT error variance, and say so).
3. **Forecast set.** Quarterly 3Q26, 4Q26, 1Q27-4Q27 and annual FY26, FY27, FY28: revenue (from the adopted path), each cash cost line, SBC,
   adj EBITDA and margin, D&A, operating income and margin, interest income, tax, net income, diluted shares, EPS (GAAP and the Street definition),
   FCF and FCF margin; median with 80% and 90% bands; base / bear / bull revenue scenarios with costs flexed (M6) and held; vs consensus (WS03
   LSEG and Bloomberg, with n and dispersion), vs management (floor, the 31b management profile), vs the prior team numbers (WS30 walk, WS31b, WS07).
4. **Cyclicality.** Seasonal profile 2026-27 by quarter with the mechanical/discretionary split; macro sensitivity table (margin change per
   1pt of revenue growth shortfall, by cost-response variant, by year); the FY26 floor break-even.
5. **5 Nov card.** 3Q26 adj EBITDA and margin (distribution), 4Q26 margin implied, FY26 margin vs the 35.5% floor and vs consensus, the
   forecast of the margin sentence (from M3), EPS and FCF for 3Q26, the surprise vs consensus with a probability of beat, and the two or three
   numbers the pitch should quote with their bands. Flag what would be settled on 5 Nov (the 10-Q S&M split, etc.).
6. **Workbook** `model/ABNB_margin_model.xlsx` (new file; openpyxl; formulas where the logic is simple, values with a source column where it is
   not): sheets Inputs (revenue path, parameters with sources), Lines (quarterly history 1Q21-2Q26 + forecasts), Bridge (EBITDA -> EPS -> FCF),
   Scenarios, Consensus (comparison), Seasonality, Weights, README. Every forecast cell traceable to a CSV in `data/processed/margin_build/23_final_model/`.
7. **`docs/margin-build/SYNTHESIS.md`** (this is what Krish reads first): bottom line in ten lines (the margin view, the lines that carry it, the
   consensus gap, the FY27 incremental margin, the biggest risk); how the model is built (one page); the backtest evidence (the combined object's
   scoreboard rows, both windows, both weightings, vs every baseline); the forecast tables; cyclicality; the 5 Nov card; what was tried and failed
   (from all method notes, one line each, with numbers); the alt-data verdict; open items; a "For the pitch" list of quotable statements each
   with its evidence path; file map; RESUME.

## Pass line (pre-registered)

`final-margin__combined` beats `seasonal_naive` on adj EBITDA margin MAE at h=0 and h=1 in both windows and both weightings, and is not worse than
the best single object by more than 10% in either window (otherwise quote the best single object and say the combination does not help).
Workbook opens; run.py exits 0; every number in SYNTHESIS.md traces to a CSV.
