"""WS23 final model — rebuild everything end to end.

    py -3.13 analysis/src/margin_build/23_final_model/run.py

Steps
  1 combine.py      the leave-future-out combination; registers final-margin__combined
  2 diagnostics.py  leave-one-member-out, Street-independent variant, shock vs calm
  3 forecast.py     line decomposition, the full forecast set, cyclicality, the 5 Nov card
  4 workbook.py     model/ABNB_margin_model.xlsx
  5 score.py        the margin harness scorer, run ONCE (skip with MARGIN_SKIP_SCORE=1)

Never run this while another agent is running a method package: several of them shell
out to score.py and the two collide (WS20 section 10).
"""
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PY = [sys.executable]
SCORE = ROOT / "analysis" / "src" / "margin_build" / "10_harness_margin" / "score.py"


def step(name, args):
    t0 = time.time()
    print(f"\n=== {name} ===", flush=True)
    r = subprocess.run(PY + args, cwd=str(ROOT))
    if r.returncode != 0:
        print(f"!! {name} exited {r.returncode}")
        sys.exit(r.returncode)
    print(f"--- {name} ok ({time.time() - t0:.0f}s)")


def main():
    step("1 combine", [str(HERE / "combine.py")])
    step("2 diagnostics", [str(HERE / "diagnostics.py")])
    step("3 forecast", [str(HERE / "forecast.py")])
    step("4 workbook", [str(HERE / "workbook.py")])
    if os.environ.get("MARGIN_SKIP_SCORE") == "1":
        print("\n=== 5 score.py SKIPPED (MARGIN_SKIP_SCORE=1) ===")
    else:
        step("5 score.py", [str(SCORE)])
    print("\nWS23 done.")


if __name__ == "__main__":
    main()
