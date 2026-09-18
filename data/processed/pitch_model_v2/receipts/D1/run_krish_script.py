"""D1 digger shim: run one of Krish's q3nowcast scripts on this machine.

The scripts were written on Windows and hard-code
    MAIN = r"C:\\Users\\krish\\citadel-abnb"
for the two or three main-tree CSVs they read (abnb_driver_history_quarterly.csv,
predictive/02_peer_prints.csv, eurostat_platform_nights_monthly.csv).  On this
clone those files live at the repo root, so the only edit is that one constant.
Nothing else in the source is touched; the script is exec'd as __main__ with its
real __file__, so every relative path (WT/ROOT/OUT) resolves exactly as it would
if the file were run directly.  The source file itself is never modified.

Usage: python3 <this> analysis/src/q3nowcast/E5_backtest.py
"""
from __future__ import annotations
import re, runpy, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]          # repo root
target = (ROOT / sys.argv[1]).resolve()
src = target.read_text(encoding="utf-8")

pat = re.compile(r'^MAIN\s*=\s*(?:Path\()?r?"[^"]*"\)?\s*$', re.M)
new_main = ('MAIN = Path(r"%s")' % ROOT) if "MAIN = Path(" in src else ('MAIN = r"%s"' % ROOT)
src2, n = pat.subn(new_main, src)
if n != 1:
    raise SystemExit(f"expected exactly one MAIN assignment in {target}, found {n}")
print(f"[shim] {target.name}: repointed MAIN -> {ROOT}", flush=True)

g = {"__name__": "__main__", "__file__": str(target), "__package__": None}
sys.argv = [str(target)] + sys.argv[2:]
exec(compile(src2, str(target), "exec"), g)
