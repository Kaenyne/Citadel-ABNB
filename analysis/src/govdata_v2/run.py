"""Rebuild build C (EUROCONTROL daio as an EMEA nights feature) end to end. Exit code 0 on success.

    python analysis/src/govdata_v2/run.py            # pull if missing, vintages from the git mirror, backtests, rank
    python analysis/src/govdata_v2/run.py --no-git   # skip C2 (uses the qtd75_pit.csv already on disk)

The git mirror (C2) must exist at ~/abnb_ia_capture/euctrl_daio_git (or $DAIO_GIT):
    git clone https://github.com/euctrl-pru/daio ~/abnb_ia_capture/euctrl_daio_git
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
steps = ["C1_collect.py"] + ([] if "--no-git" in sys.argv else ["C2_vintages.py"]) + ["C3_backtests.py", "C4_rank.py"]
t0 = time.time()
for s in steps:
    t = time.time()
    print(f"\n===== {s} =====", flush=True)
    rc = subprocess.call([sys.executable, os.path.join(HERE, s)])
    print(f"===== {s} exit {rc} in {time.time() - t:.0f}s =====", flush=True)
    if rc != 0:
        sys.exit(rc)
print(f"\nall steps done in {time.time() - t0:.0f}s")
