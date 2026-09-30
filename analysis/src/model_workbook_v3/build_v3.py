"""Team model v3 = model v2 with analyst-facing labels, Times New Roman on the working sheets, and a Valuation sheet for the
memo v5 FY27 bridge. Cover is not touched. Runs through Excel (COM) so charts survive and Excel re-points every reference
when rows are deleted. Run from the repo root with Excel closed on the file:
    py -3.13 analysis/src/model_workbook_v3/build_v3.py
Input: model/Caimanes_Citadel_ABNB_Model_v2.xlsx (read only). Output: model/Caimanes_Citadel_ABNB_Model_v3.xlsx.
"""
import re
import shutil
from pathlib import Path

import win32com.client as win32

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "model/Caimanes_Citadel_ABNB_Model_v2.xlsx"
OUT = ROOT / "model/Caimanes_Citadel_ABNB_Model_v3.xlsx"
FONT = "Times New Roman"

LABELS = {
    "Income_Statement": {
        "A1": "Airbnb — Income Statement (USD millions unless stated)",
        "A6": None,
        "A37": "Street Comparison",
        "A46": "Cost Build — Assumptions",
        "A56": "    Chargeback overlay, $ per booking (bear case)",
        "A57": "    Hosting & AI compute, FY25 ($m)",
        "A58": "    Hosting & AI compute step, 2H26 ($m per half vs 2H25)",
        "A59": "    Hosting & AI compute, FY27 ($m, before reconciliation)",
        "A65": "    RNPL ops uplift per completed booking (%, bear case)",
        "A79": "    4Q26 marketing cut ($m, bear case)",
        "A80": "    Reconcile 3Q26 to management's margin guidance (1 = on)",
        "A82": "    3Q26 margin vs 3Q25 per guidance, 'down slightly' (pp)",
        "A83": "    3Q26 nights used in the reconciliation (m)",
        "A84": "    3Q26 GBV used in the reconciliation ($bn)",
        "A99": "Quarterly Build (3Q26–4Q27)",
        "A105": "Derived Budgets ($m)",
        "A108": "    Field 1H26 = S&M 1H26 − marketing 1H26",
        "A116": "    Reconciliation: 3Q26 bookings (m)",
        "A117": "    Reconciliation: 3Q26 cost of revenue before reconciliation",
        "A118": "    Reconciliation: 3Q26 ops & support before reconciliation",
        "A119": "    Reconciliation: 3Q26 PD + S&M + G&A before reconciliation",
        "A120": "    Reconciliation: 3Q26 cash costs before reconciliation",
        "A121": "    Reconciliation: 3Q26 cash costs implied by guidance",
        "A122": "    Reconciliation: cost gap to guidance",
        "A123": "    3Q26 marketing step = cost gap × marketing share",
        "A124": "    Hosting & AI compute step per half, incl. reconciliation",
        "A125": "    Marketing FY27 = FY26 × growth",
        "A127": "Cost Lines by Quarter ($m)",
        "A132": "    CoR: hosting & AI compute",
        "A134": "Cost of revenue (cash)",
        "A139": "Operations & support (cash)",
        "A140": "Product development (cash)",
        "A143": "Sales & marketing (cash)",
        "A144": "General & administrative (cash, ex reserves)",
        "A145": "Stock-based compensation",
        "A148": "Interest income",
        "A149": "Diluted shares (m)",
        "A151": "Margin vs the Street",
        "A153": "Street adj. EBITDA margin",
        "A158": "FY26 margin vs 35.5% guidance floor (pp)",
    },
    "Nights_Engine": {
        "A1": "Airbnb — Nights Model",
        "A5": "A. Reported Nights",
        "A9": "B. Stays Index — regional stays growth from review counts, weighted by stay mix",
        "W19": None,
        "A20": "C. Mapping to Reported Nights — nights y/y = a + b × index (fitted 1Q23–2Q25)",
        "A21": "Intercept a",
        "A22": "Slope b",
        "A27": "C1. Backtest W1 — scored 1Q23–2Q26",
        "A28": "  prediction (refit each quarter)",
        "A31": "  RMSE model / RMSE naive",
        "E31": "ratio vs naive",
        "A33": "C2. Backtest W2 — scored 1Q24–2Q26",
        "A34": "  prediction (refit each quarter)",
        "A37": "  RMSE model / RMSE naive",
        "E37": "ratio vs naive",
        "A39": "C3. Error Band — pre-RNPL quarters, scored 1Q24–2Q25",
        "A40": "  prediction (refit each quarter)",
        "A43": "  RMSE model / RMSE naive",
        "E43": "ratio vs naive",
        "F43": "← RMSE = error band (± pp)",
        "A46": "D. 3Q26 Read — quarter to date, through the mapping",
        "D47": "← 3Q26 stay-mix weight", "D48": "← 3Q26 stay-mix weight",
        "D49": "← 3Q26 stay-mix weight", "D50": "← 3Q26 stay-mix weight",
        "A54": "  3Q26 stays read, nights y/y (%)",
        "D54": "± band",
        "A57": "E. RNPL Timing — reported nights = stays + booking gap",
        "A58": "  Scenario: no gap",
        "E58": "← nights y/y and level",
        "A59": "  Scenario: average post-RNPL gap",
        "A60": "  Scenario: largest post-RNPL gap",
        "A62": "  y/y booking-gap term (pp)",
        "A63": "  Base nights y/y (%)",
        "A65": "  Booking lead time: share of each quarter's stays booked 0–3 quarters earlier",
        "A70": "  RNPL cancellations landing, by booking quarter (pp)",
        "A75": "    written 3Q26 (base)",
        "A77": "  3Q26 nights y/y, all-in (%) — stays read, external series, traffic (8.0–9.9% range)",
        "A78": "F. Forward Path",
        "A82": "  events (pp) — World Cup, Middle East",
        "A83": "  NIGHTS y/y (%)",
        "A84": "  Nights (m)",
        "A91": "  RNPL cancellations (pp)",
        "A92": "G. RNPL Unearned Fees vs GBV",
        "A96": "  z vs pre-RNPL spread (1Q23–2Q25)",
        "A111": "  Chart data: reported nights y/y (%)",
        "A112": "  Chart data: our view (reported, then forecast)",
        "A113": "  Chart data: Street y/y",
        "A114": "  Chart data: stays-implied / stays path",
    },
    "ADR_Engine": {
        "A1": "Airbnb — ADR Model (reported ADR y/y = ex-FX + FX)",
        "A5": "A. Reported ADR and FX Effect",
        "A6": "ADR ($, GBV ÷ nights)",
        "A8": "    ex-FX y/y, as reported (%)",
        "A9": "    FX effect on ADR (pp), as reported",
        "A11": "B. FX Translation — FX pp = Σ region GBV share × currency basket y/y",
        "A21": "    share of quarter's business days observed",
        "A33": "Currency Basket Weights by Region",
        "A43": "Regional GBV Shares (10-K, latest year before each print)",
        "A50": "FX effect on ADR — translation (pp)",
        "A51": "    error vs reported (pp)",
        "A53": "    RMSE translation / RMSE naive, 1Q23–2Q26",
        "F53": "ratio vs naive",
        "A55": "    FX range P10 (pp)",
        "A56": "    FX range P50 (pp)",
        "A57": "    FX range P90 (pp)",
        "A59": "C. Ex-FX ADR Build — core + bundle + mix + unit size + length of stay + seats + interaction",
        "A60": "Reported ex-FX ADR y/y (pp)",
        "A69": "    bundle: RNPL North America, laps 3Q26",
        "A70": "    bundle: cancellation redesign + single fee, laps 4Q26",
        "A71": "    bundle: RNPL outside North America (unsized)",
        "A72": "    bundle total (pp)",
        "A74": "EX-FX ADR y/y (pp)",
        "A76": "C1. Geographic Mix — regional nights growth; base-quarter shares and ADRs held",
        "A92": "D. Reported ADR Path",
        "A93": "    FX effect on ADR (pp) — blended 3Q26–4Q26, translation 2027",
        "A96": "    range half-width (pp)",
        "A101": "    z: (ours − Street) / range",
        "A103": "    nights (m)",
        "A104": "    GBV ($bn) = nights × ADR",
        "A145": "Chart data: ADR $ (reported, then forecast)",
        "A146": "Chart data: Street ADR $",
        "A147": "Chart data: FX translation (pp)",
        "A148": "Chart data: FX as reported (pp)",
        "A168": "H. ADR Adjustments",
        "A169": "    construction basis adjustment (pp)",
        "A170": "    World Cup premium in the 2Q26 core (pp)",
        "A171": "    World Cup lap (pp)",
        "A172": "    core, 1Q23–2Q26 average ex World Cup (pp)",
        "A173": "    FX, euro-based estimate (pp)",
        "A174": "    FX used for 3Q26/4Q26 = average of translation and euro-based (pp)",
    },
}
# rows removed (audit / reference blocks that nothing outside themselves uses; checked before deletion)
DELETE = {
    "Income_Statement": [42, 43, 44, 47],
    "Nights_Engine": list(range(98, 110)),
    "ADR_Engine": list(range(106, 117)) + list(range(118, 143)) + list(range(175, 180)),
}


def main():
    shutil.copyfile(SRC, OUT)
    xl = win32.DispatchEx("Excel.Application")
    xl.Visible = False
    xl.DisplayAlerts = False
    try:
        wb = xl.Workbooks.Open(str(OUT))
        for name, labels in LABELS.items():
            ws = wb.Worksheets(name)
            for addr, text in labels.items():
                ws.Range(addr).Value = "" if text is None else text
        # ADR sheet: column B held source/derivation notes only; clear text, keep any numbers
        ws = wb.Worksheets("ADR_Engine")
        for r in range(1, 180):
            c = ws.Cells(r, 2)
            if isinstance(c.Value, str) and not c.HasFormula:
                c.Value = ""
            a = ws.Cells(r, 1)
            if isinstance(a.Value, str) and "business days; forward = spot held" in a.Value:
                a.Value = re.sub(r"\s*\(business days; forward = spot held[^)]*\)", " (forward: spot held)", a.Value)
        for name, rows in DELETE.items():
            ws = wb.Worksheets(name)
            for r in sorted(rows, reverse=True):
                ws.Rows(r).Delete()
        for name in LABELS:
            ws = wb.Worksheets(name)
            ws.UsedRange.Font.Name = FONT
            for co in ws.ChartObjects():
                co.Chart.ChartArea.Font.Name = FONT
        add_valuation(wb)
        # Cover: target price now comes from the FY27 bridge (memo v5); every other Cover cell is left as in v2
        cover = wb.Worksheets("Cover")
        cover.Range("E35").Formula = "=Valuation!C20"
        cover.Range("A2").Formula = '="Target Price: $" & ROUND(Valuation!C20,2)'
        xl.CalculateFull()
        wb.Save()
        wb.Close(False)
    finally:
        xl.Quit()
    print("wrote", OUT)


def add_valuation(wb):
    ws = wb.Worksheets.Add(After=wb.Worksheets(wb.Worksheets.Count))
    ws.Name = "Valuation"
    blue, black, green = 0xFF0000, 0x000000, 0x008000   # Excel colours are BGR
    rows = [
        ("Airbnb — Valuation (FY27 basis)", None, None, None),
        (None, None, None, None),
        ("Share price ($)", "=Cover!P2", green, "$#,##0.00"),
        ("Diluted shares (m)", "=Cover!P3", green, "#,##0.0"),
        ("Market cap ($m)", "=B3*B4", black, "$#,##0"),
        ("Cash ($m)", "=Cover!P6", green, "$#,##0"),
        ("Debt ($m)", "=Cover!P5", green, "$#,##0"),
        ("Net cash ($m)", "=B6-B7", black, "$#,##0"),
        ("Enterprise value ($m)", "=B5-B8", black, "$#,##0"),
        (None, None, None, None),
        ("Adj. EBITDA ($m)", "Ours", None, None),
        ("NTM (3Q26–2Q27)", "=SUM(Income_Statement!P23:S23)", green, "$#,##0"),
        ("FY27", "=SUM(Income_Statement!R23:U23)", green, "$#,##0"),
        (None, None, None, None),
        ("EV / NTM EBITDA", "=B9/B12", black, "0.0x"),
        ("EV / FY27 EBITDA", "=B9/B13", black, "0.0x"),
        (None, None, None, None),
        ("Price Bridge", "Multiple", None, None),
        ("Estimate reset: consensus FY27 multiple on our FY27 EBITDA", "=C16", black, "0.0x"),
        ("Target: multiple compresses", 12.5, blue, "0.0x"),
        ("Bull case: 7 Aug 2026 close after the 2Q26 print", None, None, None),
    ]
    for i, (label, val, color, fmt) in enumerate(rows, start=1):
        if label is not None:
            ws.Cells(i, 1).Value = label
        if val is not None:
            ws.Cells(i, 2).Value = val
            if color is not None:
                ws.Cells(i, 2).Font.Color = color
            if fmt:
                ws.Cells(i, 2).NumberFormat = fmt
    # Street column
    ws.Range("C11").Value = "Street"
    for addr, f, fmt in [("C12", "=SUM(Income_Statement!P40:S40)", "$#,##0"), ("C13", "=SUM(Income_Statement!R40:U40)", "$#,##0"),
                         ("C15", "=B9/C12", "0.0x"), ("C16", "=B9/C13", "0.0x")]:
        ws.Range(addr).Value = f
        ws.Range(addr).NumberFormat = fmt
    ws.Range("C12:C13").Font.Color = green
    ws.Range("D11").Value = "Ours vs Street"
    for addr, f in [("D12", "=B12/C12-1"), ("D13", "=B13/C13-1")]:
        ws.Range(addr).Value = f
        ws.Range(addr).NumberFormat = "0.0%"
    # bridge: price and return per row
    ws.Range("C18").Value = "Price ($)"
    ws.Range("D18").Value = "Return"
    for r in (19, 20):
        ws.Range(f"C{r}").Value = f"=(B{r}*$B$13+$B$8)/$B$4"
        ws.Range(f"C{r}").NumberFormat = "$#,##0.00"
        ws.Range(f"D{r}").Value = f"=C{r}/$B$3-1"
        ws.Range(f"D{r}").NumberFormat = "0.0%"
    ws.Range("C21").Value = 178
    ws.Range("C21").Font.Color = blue
    ws.Range("C21").NumberFormat = "$#,##0.00"
    ws.Range("D21").Value = "=C21/$B$3-1"
    ws.Range("D21").NumberFormat = "0.0%"
    ws.Range("A23").Value = "Share of downside from estimate reset"
    ws.Range("B23").Value = "=(C19-B3)/(C20-B3)"
    ws.Range("B23").NumberFormat = "0%"
    ws.Range("A24").Value = "Multiple compression (turns)"
    ws.Range("B24").Value = "=B19-B20"
    ws.Range("B24").NumberFormat = "0.0x"
    for addr in ("A1", "A11", "B11", "C11", "D11", "A18", "B18", "C18", "D18"):
        ws.Range(addr).Font.Bold = True
    ws.Range("A1").Font.Size = 12
    ws.UsedRange.Font.Name = FONT
    ws.Columns("A").ColumnWidth = 58
    ws.Columns("B:D").ColumnWidth = 14


if __name__ == "__main__":
    main()
