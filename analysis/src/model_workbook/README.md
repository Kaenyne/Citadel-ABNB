# model_workbook: builds `model/ABNB_pitch_model.xlsx`

```
py -3.13 analysis/src/model_workbook/build.py                 # full build, then Excel (COM) recalculates and saves cached values
py -3.13 analysis/src/model_workbook/build.py --no-recalc     # skip the Excel step
py -3.13 analysis/src/model_workbook/build.py --only tab_scenarios tab_is --out <path>   # a subset, for testing
py -3.13 analysis/src/model_workbook/qa.py model/ABNB_pitch_model.xlsx [pdf_dir]          # formula-error scan; optional per-sheet PDF export
py -3.13 analysis/src/model_workbook/verify.py <xlsx> "<sheet>" "<row label>" ...         # recalc and print rows by label
```

- `style.py`: fonts, fills, number formats and the row/table writers (blue = source value, black = formula, green = link).
- `data.py`: the shared frames (history from the financial panel, scenario blocks from the line build, revenue path, consensus, guide items).
- `tabs/tab_*.py`: one module per sheet, each exposing `build(wb)`. `tab_scenarios` runs first; the build script reorders sheets on save.
- Requires `py -3.13` (openpyxl, pandas, matplotlib for the stock chart, pywin32 for the recalculation step).
- Never edit the workbook by hand for anything you want to keep: change the source CSV or the tab module and rebuild.

Write-up: `docs/2026-09-16_pitch-model-workbook.md`.
