# Workstream 17: auditing the Excel driver model in Excel

*Overnight run, 6-7 Sep 2026. Subject: `model/ABNB_driver_model.xlsx`, built by workstream 13.*

## Bottom line

The workbook recalculates cleanly in real Excel and its arithmetic is right. Excel 16.0 opened a
copy, ran `Application.CalculateFullRebuild()` and returned **zero error cells out of 5,544**, no
circular reference, iteration off, calculation state `xlDone`. **All 216 named outputs match the
Python mirror to better than 1e-6 relative** (worst 4.2e-15), and so do **all 2,348 formula cells**
when the workbook is re-evaluated by workstream 13's own evaluator - so the evaluator is not
covering for a function Excel would handle differently. The Recon sheet's 216 delta cells all read
exactly 0 inside Excel.

The mechanics around the arithmetic were weaker than the arithmetic. **The scenario selector did
nothing.** Setting `Inputs!B4` (the named range `Scenario`) to 1 and then to 3 and recalculating in
Excel moved 96 and 97 cells - every single one of them in the Inputs sheet's own Active column - and
nothing at all on Revenue, Costs, Cash, Valuation or Card_5Nov, even though the cell's own note said
it "drives the headline blocks on Valuation and Card_5Nov". No formula in the file referenced the
Active column. That is now fixed, along with ten other mechanical defects; the workbook was
regenerated from the builder and every number is unchanged.

**Sixteen findings: 4 high, 8 medium, 4 low, plus 13 checks that came back clean. Eleven fixed,
five left open for a human.** The one that matters most and is *not* fixed: the FY2026 share-count
roll-forward double-counts the 1H26 buyback, which makes every per-share number about 1.5% too
generous.

| | high | medium | low | clean |
|---|---|---|---|---|
| fixed | 3 | 6 | 2 | - |
| open  | 1 | 2 | 2 | - |
| clean | - | - | - | 13 |

## What was run

| Step | Tool | Output |
|---|---|---|
| Real recalculation | PowerShell COM, `New-Object -ComObject Excel.Application`, `Visible=$false`, `DisplayAlerts=$false`, `CalculateFullRebuild()` on a **copy** in the scratchpad | `data/processed/overnight/17_excel_recalc_dump.csv` (5,544 cells: sheet, address, formula, value, error) |
| Excel vs Python vs evaluator | `analysis/src/overnight/17_excel_audit.py` | `17_excel_vs_python.csv` (216 rows), `17_all_formula_cells.csv` (2,348 rows) |
| Scenario switching | selector written to `Inputs!B4` = 1 / 2 / 3, full rebuild each time | `17_scenario_switch.csv` (145 rows, before and after) |
| Static formula review | `17_excel_audit.py` scan + curation in `17_formula_review.py` | `17_auto_scan.csv` (raw), `17_formula_review.csv` (29 rows) |

The recalculated copy was saved to the scratchpad only
(`scratchpad/17/ABNB_driver_model_recalc_check.xlsx`), not to `model/`. `model/` still holds exactly
one workbook. The PowerShell driver is `scratchpad/17/recalc_dump.ps1`.

Note on tolerance: 25 of the 216 outputs "failed" a 1e-6 relative test on the first pass purely
because `13_reconciliation.csv` stores its Python column rounded to four decimals, which is coarser
than 1e-6 on a margin or a per-share number. Re-running the mirror in process at full precision,
all 216 pass. On the 2,348-cell comparison the same care is needed in the other direction: the 116
Recon delta cells compute a difference of two nearly equal numbers, where Excel returns exactly 0
and the Python evaluator returns ~1e-13; the test uses an absolute floor of 1e-6 alongside the
relative one.

## Does the scenario switch work?

Before the fix, no. After the fix, yes.

| Selector | Build | Cells whose value changed vs selector = 2 | Where |
|---|---|---|---|
| 1 (Bear) | before | 96 | Inputs 96 |
| 3 (Bull) | before | 97 | Inputs 97 |
| 1 (Bear) | after | 135 | Inputs 96, Valuation 22, Card_5Nov 17 |
| 3 (Bull) | after | 136 | Inputs 97, Valuation 22, Card_5Nov 17 |

The Bear / Base / Bull columns were always right - they read the Inputs scenario columns directly
and never depended on the selector. At all three settings the six valuation lenses and the football
field low / high / mean in the new Active column match the Python mirror's bear / base / bull values
exactly (0 mismatches over 145 comparisons in `17_scenario_switch.csv`); e.g. bear DCF $78.69, base
$185.35, bull $285.28, and the base football-field mean $162.65.

## The four high-severity findings

**1. The scenario selector was inert (fixed).** 126 `CHOOSE` cells in `Inputs!F` were the only
consumers of `Inputs!B4`, and nothing consumed column F. Fixed by adding an *Active (Inputs!B4)*
column - column E - to Valuation sections 1, 2, 3 and 4 and to Card_5Nov, each cell
`=CHOOSE(Inputs!$B$4,B{r},C{r},D{r})` - 23 cells on Valuation, 18 on Card_5Nov. No existing
cell moved. (The file goes from 2,303 to 2,348 formula cells across all eleven fixes: these 41,
the two reverse-DCF check cells and two new History anchor formulas.)

**2. The reverse-DCF answer was a paste (fixed).** `Valuation!B64/C64` - "solved implied 10-year
growth at spot", 8.51% on reported FCF and 14.42% on SBC-adjusted FCF - is an offline bisection.
The value ladder above it is live off `Inputs!D11/D12`, so a change to the cost of equity would
have left the headline number quietly wrong. (Those two numbers are right: at the model's own 10.5%
cost of equity they are 8.51% / 14.42%; the 7.50% / 13.32% quoted in the workstream-13 note is the
same solve at a 10.0% cost of equity, and both appear in `13_valuation_summary.csv`.) Fixed by
marking the two cells as inputs and adding a live check row `B65/C65` that prices the same stream at
the solved growth and subtracts spot. It reads **0.00** in Excel today.

**3. The FY2026 share count double-counts 1H26 (OPEN).** `Cash` row 23 (and its two copies) rolls
the share count forward as
`= 2Q26 shares - FY26 buybacks / price + FY26 SBC / price x (1 - withholding)`,
while the net-cash row three lines below correctly nets the 1H26 actuals out of every flow. The
1H26 buyback ($2,139M = 11.8M shares) is therefore subtracted twice, less 3.2M of double-counted
issuance:

| | as built | on a 2H26-only roll-forward | difference |
|---|---|---|---|
| FY2026E diluted shares (base) | 580.47M | 589.02M | +8.55M (+1.47%) |
| FY2027E diluted shares | 566.05M | 574.60M | +1.51% |
| FY2028E diluted shares | 552.98M | 561.53M | +1.55% |
| Base football-field mean | $162.65 | $160.22 | -1.5% |

All six lenses divide by the share count, so all six fall about 1.5%. This was **not** fixed: it
moves published outputs, and the identical line exists in the Python mirror
(`13_driver_model.py`, `shares = shares - I["buybacks"] / px + sbc / px * (1 - withholding)`), so
fixing one without the other would break the reconciliation. The Cash sheet header now states the
asymmetry and points here.

**4. A units trap on the FY2028 FX inputs (fixed).** `Inputs!C95:E96` carried the unit "pp", the
same label as the twelve quarterly FX rows - but the quarterly rows hold plain percentage-point
numbers divided by 100 where they are used, while these two hold a fraction consumed with no
divisor (`Revenue!K25 = Inputs!$C$96`). Typing 1.5 meaning +1.5pp would have applied +150%. Zero in
all three scenarios today, so nothing is wrong in the current file. Relabelled, with the convention
spelled out in the source cell.

## What was fixed, and the proof nothing moved

Every fix is in `analysis/src/overnight/13_excel_builder.py`; the workbook was regenerated by
`py -3.13 analysis/src/overnight/13_driver_model.py`.

| # | Fix | Effect on numbers |
|---|---|---|
| 1 | Active column driven by the selector on Valuation and Card_5Nov; the Inputs note corrected (it also said `B3` where the selector is `B4`) | none |
| 2 | Reverse-DCF solved cells marked as inputs + a live staleness check row | none |
| 3 | FY2028 FX unit relabelled | none |
| 4 | 33 FY2025A literals (`=161`, `=705`, `=-232`, `=3789`, ...) replaced by 11 sourced anchors at the foot of History, traced to `data/processed/abnb_fcf_bridge.csv` and WS07; buybacks and withholding are now formulas over the History table | none |
| 5 | Scenario grid reads its own axis cells instead of restating 0.04 / 0.32 as literals | none |
| 6 | DCF fade weights and discount exponents read the year number in column A | none |
| 7 | FY2028 core revenue points at the take-rate row instead of restating it | none |
| 8 | `DCF fade period (years)` marked LAYOUT-FIXED (it resizes nothing) | none |
| 9 | Two Cash rows relabelled: their "FY2025A" column holds 2Q26 actuals | none |
| 10 | Inputs banner now names every category of hard number in the file | none |
| 11 | The wide source column on Street and Card_5Nov was one column to the right of the text | none |

Proof: `13_model_annual.csv`, `13_model_quarterly.csv`, `13_valuation_summary.csv`,
`13_scenario_grid.csv` and `13_reconciliation.csv` are **byte-identical** before and after
(including the `cell_reference` column - no row moved). After regeneration the workbook re-passes
everything: 0 Excel errors in 5,544 cells, 216/216 outputs matching, 2,348/2,348 formula cells
matching, 216/216 Recon deltas exactly 0. Numeric literals inside formulas fell from **121 cells to
3** (the three 5 Sep memo multiples).

## The static review, item by item

Full table: `data/processed/overnight/17_formula_review.csv` (29 rows: sheet, cell, issue_type,
severity, description, suggested_fix, status).

### Checks that came back clean

- **Ranges that stop short**: none. Every `SUM` in the file is `E:H` on a single row - the four 2027
  quarters - and the FY2026 column adds the 1H26 actual to 3Q26 and 4Q26 explicitly.
- **References to empty cells**: none, over all 2,348 formulas.
- **Formula consistency across the three scenario blocks**: after shifting each block's row offset
  (Revenue 41, Costs 30, Cash 25) and blinding the Inputs scenario column, the Bear, Base and Bull
  blocks are identical formula for formula - **0 mismatches**. Valuation columns B / C / D likewise
  over rows 6-49. The raw row-by-row scan flags 273 "neighbour differs" hits, but every one is by
  design: 3Q27/4Q27 chain off the 2026 quarter rather than off History, and the annual columns I/J/K
  are a different basis from the quarterly columns C..H.
- **Seasonality and mix shares sum to 100%**: seasonal share of full-year nights 1Q-4Q sums to
  exactly 1.000000; the four regional shares sum to exactly 1.000000 for 3Q25, 4Q25, 1Q26, 2Q26 and
  FY2025.
- **Football-field weights**: `MIN` / `MAX` / `AVERAGE` over exactly six equally weighted lens cells,
  matching the Python mirror's `core` set. The SBC-adjusted DCF and the 5 Sep memo multiples are
  excluded from both, as documented.
- **The FX timing wedge**: `(1 + revenue FX) / (1 + ADR FX) - 1` in all six quarterly columns and in
  FY2028E. It is absent from the FY2026E and FY2027E columns by construction, because those revenues
  are sums of quarters that already carry it.
- **Sign conventions**: interest expense, cash taxes and capex arrive negative; FCF is a straight
  sum; SBC-adjusted FCF = FCF - SBC; buybacks and RSU withholding reduce both net cash and the share
  count. Net cash rolls 9,593 -> 8,793 (bear FY26) on the 2H26 flows only.
- **Units**: every Inputs reference divides by 100 where the unit is a percentage-point number, by
  10,000 where it is bps, and not at all where it is a fraction - after finding 4 above.
- **Named ranges**: `Scenario` -> `Inputs!$B$4` (2), `SharePrice` -> `$F$8` (181.94), `CostOfEquity`
  -> `$F$11` (0.105), `ExitMultiple` -> `$F$14` (16.5). All four land on the Active cell of the row
  their name claims. Note they point at the *Active* column, so `CostOfEquity` follows the selector.
- **Sheet-to-sheet links**: every cross-sheet reference resolves to a number, never to a label.

### Usability

- **Every Inputs row has a source.** 0 of the rows carrying a value are missing a source string in
  column G, and 0 History anchors carry a hard value with no source note.
- **Are yellow cells the only hard-codes?** Not quite, and now the banner says so. Outside the 455
  yellow input cells there are: the History quarterly actuals table (507 cells, sheet-level source),
  the Recon sheet's Python-mirror column (216, by design), the Street consensus bars (17, each with
  a vendor and a date) and the Card_5Nov context block (8, each with a workstream source). All are
  legitimate, none are model assumptions in disguise.
- **Card_5Nov pulls, it does not paste.** All 72 formula cells are live off Revenue and
  Costs; the guide and Street columns are external bars with named sources.
- **Recon passes inside Excel.** All 216 `=C-B` delta cells read exactly 0 after the real
  recalculation - not "approximately zero".

## To-do list for a human reviewer

1. **Decide the FY2026 share-count roll-forward.** Either fix it in both `13_excel_builder.py` and
   `13_driver_model.py` (net the 1H26 buyback and SBC out of the FY26 flows, as the net-cash line
   does) and accept ~-1.5% on every lens, or write the convention down. It is the only finding that
   changes a number in the pitch.
2. **Decide the DCF's valuation date.** The strip values FY2028 onwards discounted one year, i.e. a
   value as of end-FY2027, against a 4 Sep 2026 spot. Either discount back to today, or label the
   DCF lens a forward value in the football field.
3. **Give the 5 Sep memo multiples an Inputs row** (18 / 22 / 25.5x) so no formula in the file
   contains a numeric literal.
4. **Get FY2025 interest expense** from the 10-K if the FY2025A memo column is ever shown; the
   bridge CSV reports zero for all four quarters because the coupon sits in other income/(expense).
5. **Consider a dynamic DCF strip** if anyone wants the `DCF fade period` input to do anything;
   today it is documented as inert.
6. **Consider whether the regulatory drag should be quarterly.** A full-year pp of nights growth is
   applied at full size to each quarter of that year.
7. Re-run the whole audit after any change: `13_driver_model.py`, then `scratchpad/17/recalc_dump.ps1`,
   then `17_excel_audit.py`, `17_scenario_switch.py`, `17_formula_review.py`.

## Corrections to existing work

- `research/notes/overnight/13_driver-model-build.md` says the workbook could not be recalculated
  because LibreOffice and the `formulas` package are unavailable. Excel 16.0 itself is reachable
  over COM from PowerShell on this machine and does the job. The workbook's own caveat (`Recon!A2`)
  has been rewritten to say the file was rebuilt in Excel 16.0 and agrees to 4.2e-15; the WS13 note
  still carries the old claim and should be amended by its author.
- The workstream-13 builder docstring said the selector is on `Inputs!$B$3`; it is `B4`. Corrected.

## For the model

Nothing in the model's economics changed. The parameters this workstream supplies are mechanical:

| Name | Value | Unit | Source |
|---|---|---|---|
| FY2026E diluted shares, if the roll-forward nets 1H26 | 589.02 (base) | M | this note, section "high findings" |
| Share-count overstatement of the buyback shrink | 8.55 | M shares | 1H26 buybacks $2,139M / $181.94 less 1H26 SBC issuance |
| Base football-field mean on the corrected share count | 160.22 | $ | vs $162.65 as built |

## Files

- `analysis/src/overnight/17_excel_audit.py` - Excel vs Python vs evaluator, plus the raw static scan
- `analysis/src/overnight/17_scenario_switch.py` - the selector test, before and after
- `analysis/src/overnight/17_formula_review.py` - the curated review table
- `data/processed/overnight/17_excel_recalc_dump.csv` - 5,544 cells after a real Excel rebuild
- `data/processed/overnight/17_excel_vs_python.csv` - the 216 named outputs, three ways
- `data/processed/overnight/17_all_formula_cells.csv` - all 2,348 formula cells, Excel vs evaluator
- `data/processed/overnight/17_scenario_switch.csv` - 145 rows
- `data/processed/overnight/17_formula_review.csv` - 29 findings
- `data/processed/overnight/17_auto_scan.csv` - the raw static scan the review is curated from
- scratchpad only: `recalc_dump.ps1`, `ABNB_driver_model_recalc_check.xlsx`, the before/after dumps
