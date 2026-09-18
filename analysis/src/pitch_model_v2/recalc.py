"""Open the workbook in the installed Microsoft Excel, force a full calculation, save.
Used so that viewers without a calc engine (and openpyxl data_only reads) see values."""
from __future__ import annotations
import shutil, subprocess, sys
from pathlib import Path

SCRIPT = '''
tell application "Microsoft Excel"
    set wbk to open workbook workbook file name POSIX file "{path}"
    try
        calculate full rebuild
    on error
        try
            calculate
        end try
    end try
    save wbk
    close wbk saving no
end tell
'''

def _excel_available() -> bool:
    return Path("/Applications/Microsoft Excel.app").exists() and shutil.which("osascript") is not None

def _escape(path: str) -> str:
    return path.replace("\\", "\\\\").replace('"', '\\"')

def recalc(path: str | Path) -> bool:
    p = Path(path).resolve()
    if not _excel_available():
        print("Excel or osascript not available; skipping recalculation"); return False
    try:
        r = subprocess.run(["osascript", "-e", SCRIPT.format(path=_escape(str(p)))], capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        print("recalc timed out after 300s; workbook left with fullCalcOnLoad"); return False
    if r.returncode != 0:
        print("recalc failed:", r.stderr.strip()); return False
    return True

if __name__ == "__main__":
    sys.exit(0 if recalc(sys.argv[1]) else 1)
