"""QA: count formula errors per sheet (data_only), print key cells, export each sheet to PDF for a visual check."""
import sys, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from openpyxl import load_workbook

def main(path, pdf_dir=None):
    path = Path(path).resolve()
    wb = load_workbook(path, data_only=True)
    for ws in wb.worksheets:
        errs, empties = [], 0
        for r in ws.iter_rows():
            for c in r:
                if isinstance(c.value, str) and c.value.startswith("#") and c.value[1:4].isupper():
                    errs.append((c.coordinate, c.value))
        print(f"{ws.title:22s} rows {ws.max_row:4d} cols {ws.max_column:3d} errors {len(errs)} {errs[:6]}")
    if pdf_dir:
        import win32com.client, pythoncom, win32process, time
        pythoncom.CoInitialize()
        xl = win32com.client.DispatchEx("Excel.Application"); xl.Visible = False; xl.DisplayAlerts = False
        pid = win32process.GetWindowThreadProcessId(xl.Hwnd)[1]
        try:
            w = xl.Workbooks.Open(str(path), UpdateLinks=0)
            Path(pdf_dir).mkdir(parents=True, exist_ok=True)
            for sh in w.Worksheets:
                sh.PageSetup.Zoom = False
                sh.PageSetup.FitToPagesWide = 1
                sh.PageSetup.FitToPagesTall = False
                sh.PageSetup.Orientation = 2  # landscape
                out = Path(pdf_dir) / (sh.Name.replace(" ", "_").replace("&", "and") + ".pdf")
                sh.ExportAsFixedFormat(0, str(out))
                print("pdf", out)
            w.Close(SaveChanges=False)
        finally:
            xl.Quit(); time.sleep(1); subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
