#!/usr/bin/env python
"""Run every red-team audit script in order. Exit 0 on success."""
import subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
PY = sys.executable  # portable: whatever interpreter runs this file
for s in ("rt_recompute.py", "rt_fx.py", "rt_fx2.py"):
    print(f"\n{'='*70}\n{s}\n{'='*70}")
    r = subprocess.run([PY, str(HERE / s)])
    if r.returncode != 0:
        sys.exit(r.returncode)
print("\nred_team: all audit scripts completed.")
