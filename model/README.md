# Model

- **Live model:** `ABNB_model.xlsx` (one editor at a time - announce in group chat)
- **Assumptions:** `assumptions.md` - every driver, its value in bull/base/bear, and the source
- **Versioning:** through git. Don't create copies with `_v2`, `_final`, etc.

Suggested tabs: Cover / Summary / Historicals / Drivers / IS / BS / CF / DCF / Comps / Sensitivities / Scenarios

**Update, 7 Sep 2026 (overnight run, workstream 13):** the live workbook is now
`ABNB_driver_model.xlsx` (built by `analysis/src/overnight/13_driver_model.py` +
`13_excel_builder.py`, with a Python mirror and a 216-check reconciliation). Sheets: Inputs /
History / Revenue / Costs / Cash / Valuation / Street / Card_5Nov / Recon. `ABNB_model.xlsx`
was never created. Rebuild the workbook with `py -3.13 analysis/src/overnight/13_driver_model.py`
rather than editing it in place if the inputs change; ad-hoc edits in Excel are fine for flexing
assumptions but will be overwritten by the next rebuild.
