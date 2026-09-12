#!/usr/bin/env python
"""tracker-backlog entry point. Rebuilds everything; writes outputs progressively so a
crash still leaves partial results. Exit code 0 on success.

    /Users/theomachado/.venvs/citadel-abnb/bin/python \
        analysis/src/forecast_methods/tracker_backlog/run.py

Order matters: circularity (T1) MUST run first per the standing instruction, even
though nothing downstream depends on its numbers -- it is the gate on whether the
restated series may appear anywhere else, and it must be visible first if anything
fails partway through.
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import ensure_out_dir, OUT_DIR


def main() -> int:
    ensure_out_dir()
    failures = []

    print("=" * 70)
    print("STEP 1/4: T1 circularity test (run first, per standing instruction)")
    print("=" * 70)
    try:
        import circularity
        df, fv, verdict = circularity.run()
        print(df.to_string(index=False))
        print(verdict["ruling"])
    except Exception:
        traceback.print_exc()
        failures.append("circularity")

    print("\n" + "=" * 70)
    print("STEP 2/4: (a) backlog rebuild since 4Q20")
    print("=" * 70)
    try:
        import rebuild
        out, n_mismatch = rebuild.run()
        print(f"{len(out)} quarters rebuilt; {n_mismatch} coverage-recompute mismatch "
              f"(expected: the 2Q26 row, whose next-quarter revenue is not yet printed)")
    except Exception:
        traceback.print_exc()
        failures.append("rebuild")

    print("\n" + "=" * 70)
    print("STEP 3/4: (c) Gate G1 -- raw + RNPL-scenario walk-forward, harness registration")
    print("=" * 70)
    try:
        import gate_g1
        summary, reg_all, ratios = gate_g1.run()
        print(f"{len(reg_all)} registry rows written across {reg_all.object.nunique()} objects")
    except Exception:
        traceback.print_exc()
        failures.append("gate_g1")

    print("\n" + "=" * 70)
    print("STEP 4/4: (d) booking-curve Dirichlet-style prior for kernel-lambda")
    print("=" * 70)
    try:
        import booking_curve_prior
        agg, by_region, caveat = booking_curve_prior.run()
        print(agg.to_string(index=False))
    except Exception:
        traceback.print_exc()
        failures.append("booking_curve_prior")

    print("\n" + "=" * 70)
    if failures:
        print(f"FAILED steps: {failures}")
        print(f"Outputs written so far are in: {OUT_DIR}")
        return 1
    print(f"All steps OK. Outputs in: {OUT_DIR}")
    print("(e) inside-airbnb monthly capture is a SPEC ONLY -- not run. See "
          "docs/revenue-forecast-strategy/05_backtests/tracker-backlog.md sec (e).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
