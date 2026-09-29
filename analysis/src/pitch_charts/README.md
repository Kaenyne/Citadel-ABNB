# pitch_charts

Candidate charts for the two-pager on three topics, drawn in R (ggplot2 + ragg) in the house style of the thesis-3 set
(`margin_build/47_pitch_charts` on `krish/cost-leg`): Airbnb palette, Figtree (SIL OFL, bundled in `fonts/`).

- `stock/` s01-s08: the day-1 (and 5-, 20-day) move at each print against the next-quarter revenue guide vs consensus,
  the beat vs the guide, the two-gate base rate, and our 4Q26 guide call (pitch-forecasts C01).
- `revenue/` r01-r07: revenue growth split into nights, ADR ex-FX, FX (letters' definition) and take rate, history and
  the official model's 3Q26-4Q27; ours vs the Street; bridges; revenue FX.
- `nights/` n01-n11: nights growth split into underlying, the product bundle (by leg), the World Cup and the Middle
  East; RNPL cancellations (cohort module); unearned fees vs GBV; World Cup host vs control; forecast paths; bridges.

Run from the repo root (both exit 0):

    py -3.13 analysis/src/pitch_charts/prepare_data.py      # datasets into data/processed/pitch_charts/ (SOURCES.json lists each input)
    Rscript analysis/src/pitch_charts/charts.R              # PNGs, 6.5 x 3.6 in, 300 dpi, into deck/figures/pitch_charts/<topic>/

Options: `CHARTS_ONLY=s|r|n` draws one topic. `ADR_LINE` (prepare_data) picks the ADR path: `kl` (default) is the
snapshot in `data/processed/pitch_charts/inputs/` of PR #67's engine v3 with fixes (k) LOS and (l) World Cup, taken from
the `../citadel-abnb-adrfix` working tree on 23 Sep 19:16; `worktree` reads that live file (or `ADR_FILE`); `main` is
engine v2 and reproduces the official workbook; `v3` is PR #67 as committed. Forecast revenue = nights x ADR x take rate
(DEC-0018) and adjusted EBITDA = revenue less the official model's cash costs carried flat in dollars (DEC-0022); the
4Q26 guide call (C01) is re-marked with the C1 guide model ratio at the line's bookings.

Inputs from outside main, quoted as constants with their source: the short-case nights path (`krish/cost-leg` 3065e2f2,
`44_short_case_v2/run.py`) and the World Cup host/control review series (`krish/worldcup-premium`, uncommitted,
`40_v4_reviews.csv`). Known choice: 4Q25's bundle carries the NA fee and cancellation legs (2.2 pts, matching
management's "over 200 basis points"); `nights_v2_design.md` §2.1 carries 1.51.

## Two-pager, short case (28 Sep 2026)

The pitch runs on the short case priced at $108 (krish/cost-leg `44_short_case_v2`, growth-linked multiple). Rebuild:

    python analysis/src/pitch_charts/short_case_inputs.py
    Rscript analysis/src/pitch_charts/two_pager_short.R

Writes `deck/figures/pitch_charts/two_pager_short/graph{1,2,3}_*.png` (7.2 x 4.1 in, 300 dpi). Graph 1 is history only.
Graph 2 forecasts = the short-case nights path (8.5 / 5.0 / 4.0 / 2.0 / 3.0 / 4.0%); underlying is the residual after the bundle,
World Cup and Middle East legs. Graph 3 = the 46 margin bridge on the short-case lines (48.92% / 23.59% / 30.77%), with the +4% RNPL
ops uplift booked in payroll & other. `two_pager.R` (base case) is left as it was.

### Update, same day: the $128 short case and two looks

The pitch moved to `48_short_case_v3` (krish/cost-leg): nights = team line + bear RNPL cancellation tail, $128 at 13.68x FY27
adj. EBITDA. `short_case_inputs.py` now reads 48 and writes the tail as its own component (`cancel`). Two chart sets:

    Rscript analysis/src/pitch_charts/two_pager_refined.R   # Airbnb look, Figtree, "Graph N:" titles, 7.2 x 4.1 in
    Rscript analysis/src/pitch_charts/two_pager_stylemd.R   # repo-root STYLE.md look, Airbnb hues, 7.2 x 4.9 in, captions in DOC_CAPTIONS.md

`two_pager_short.R` (the $108 path) is superseded but kept.

### Update: charts on the team model (Caimanes workbook)

    py -3.13 analysis/src/pitch_charts/caimanes_inputs.py     # reads main-tree model/Caimanes_Citadel_ABNB_Model.xlsx
    Rscript analysis/src/pitch_charts/two_pager_refined.R     # CHART_CASE=caimanes (default) or short128
    Rscript analysis/src/pitch_charts/two_pager_stylemd.R

Outputs go to `deck/figures/pitch_charts/two_pager_{refined,stylemd}_{caimanes,short128}/`. The Caimanes case uses the workbook's
nights totals, Street nights, cost lines, revenue, adj. EBITDA and LSEG Street (13 Sep); margins 48.67 / 26.81 / 32.86% against the
Street's 49.78 / 28.90 / 36.77%. World Cup +0.5pt kept by team decision (28 Sep), so the audit stamp is cleared.

### Update: team model v2 (3Q26 nights 9.2%, RNPL cancellations in the base)

`caimanes_inputs.py` now reads `model/Caimanes_Citadel_ABNB_Model_v2.xlsx` by default (`CAIMANES_XL=Caimanes_Citadel_ABNB_Model.xlsx`
for v1). v2 is a copy of v1 with two edits made in Excel: Nights_Engine B77 = 9.2 (3Q26 all-in; X79 is now the residual) and row 91
= RNPL cancellations (cohort engine central cell −0.93 / −0.85; 2027 = n02 base tail × 1.566), added into row 83. Graph 2 shows
the cancellations as their own part. Outputs are copied to main-tree `deck/Graphs/caimanes_model_v2/`.
