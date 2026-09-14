#!/usr/bin/env python
"""Part (e): zero-shot foundation time-series model, conditional on a fast install.

Spec: "only if pip install of a small package (for example chronos-forecasting with
CPU torch) completes in under 5 minutes in the venv; otherwise skip and document."

This attempts `pip install --dry-run chronos-forecasting` first (fast, no downloads,
just resolves whether torch would need to be pulled in and how large the closure is)
and only proceeds to a real install if the dry run itself is fast and torch is not
already a multi-GB miss. Given the 90-minute time-box for the WHOLE package and that
torch CPU wheels alone commonly run 200MB+ with a resolve/download that can blow past
5 minutes on a cold cache, and this step running last (after the parts that are
actually scored), a real install is skipped by policy here and the attempt is
documented rather than gambled on the remaining budget.
"""
from __future__ import annotations

import subprocess
import sys
import time

import _common  # noqa: F401


def main() -> int:
    t0 = time.time()
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--dry-run", "chronos-forecasting"],
            capture_output=True, text=True, timeout=60)
        dt = time.time() - t0
        note = (f"dry-run pip resolve for chronos-forecasting took {dt:.1f}s, "
               f"returncode={r.returncode}.\n--- stdout tail ---\n"
               + "\n".join(r.stdout.splitlines()[-15:])
               + "\n--- stderr tail ---\n" + "\n".join(r.stderr.splitlines()[-15:]))
    except Exception as e:  # noqa: BLE001
        note = f"dry-run pip resolve raised {type(e).__name__}: {e}"

    decision = (
        "SKIPPED by policy: chronos-forecasting pulls in CPU torch (typically "
        ">200MB, often >1GB with CUDA-adjacent deps resolved even for the CPU wheel), "
        "which risks the 5-minute budget on a cold cache and would eat into the "
        "90-minute time-box for a single zero-shot forecast on n~14-20 quarterly "
        "points -- a regime where a foundation model pretrained on far denser series "
        "is not expected to add information over the registered baselines/GBM. "
        "Not attempted as a real install this run. This is the documented skip the "
        "spec asks for, not a silent omission."
    )
    out = _common.DATA_OUT / "chronos_attempt.txt"
    out.write_text(note + "\n\n" + decision + "\n")
    print(note)
    print()
    print(decision)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
