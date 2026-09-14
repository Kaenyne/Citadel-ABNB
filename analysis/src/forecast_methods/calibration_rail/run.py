#!/usr/bin/env python
"""calibration-rail entry point. Rebuilds every output of this package end to end.

  python analysis/src/forecast_methods/calibration_rail/run.py

Steps (each is idempotent and writes progressively, so a crash mid-run still leaves
whatever ran before it):
  1. harness/run.py       -- rebuild calendar/targets/baselines (owned by harness;
                              re-run here only so this package is runnable standalone)
  2. reference_scoreboard.py -- extra baseline coverage (nights_yoy, adr_yoy, gbv_yoy,
                              take_rate_pct) + claim-confirmation exhibits
  3. gbm_challenger.py     -- monotone GBM challenger, 2 objects, both replays
  4. pit_crps_ledger.py    -- PIT/CRPS on the 391-row prediction ledger
  5. chronos_attempt.py    -- part (e): only if pip install finishes in <5 min
  6. harness/score.py      -- re-score the registry now that this package's objects
                              (and whatever other packages have registered) are in it
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parent
FM_SRC = PKG_DIR.parent
PY = sys.executable

STEPS = [
    ("harness baselines", FM_SRC / "harness" / "run.py"),
    ("reference scoreboard (part a)", PKG_DIR / "reference_scoreboard.py"),
    ("gbm challenger (part b)", PKG_DIR / "gbm_challenger.py"),
    ("pit/crps on ledger (part d)", PKG_DIR / "pit_crps_ledger.py"),
    ("chronos attempt (part e)", PKG_DIR / "chronos_attempt.py"),
    ("harness scorer (rescoring after registration)", FM_SRC / "harness" / "score.py"),
]


def main() -> int:
    failures = []
    for label, script in STEPS:
        print(f"\n{'='*70}\n[{label}] {script.name}\n{'='*70}")
        t0 = time.time()
        r = subprocess.run([PY, str(script)], cwd=str(FM_SRC.parents[2]))
        dt = time.time() - t0
        status = "OK" if r.returncode == 0 else f"FAILED (exit {r.returncode})"
        print(f"[{label}] {status} in {dt:.1f}s")
        if r.returncode != 0:
            failures.append(label)
    print("\n" + "=" * 70)
    if failures:
        print(f"calibration-rail run.py: {len(failures)} step(s) failed: {failures}")
        print("(other steps still wrote their progressive outputs)")
        return 1
    print("calibration-rail run.py: all steps OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
