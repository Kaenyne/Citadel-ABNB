#!/usr/bin/env python
"""Rebuild the whole harness: spine, windows, baselines, scoreboard.

  python analysis/src/forecast_methods/harness/run.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import paths as P                       # noqa: E402
from harness import windows as W                     # noqa: E402
from harness import metrics as M                     # noqa: E402
from harness.spine import build_calendar, build_targets   # noqa: E402
from harness.loaders import clear_cache               # noqa: E402
from harness.baselines import build_all_baselines     # noqa: E402
from harness.registry import register                 # noqa: E402
from harness.score import main as score_main          # noqa: E402


def main() -> int:
    P.ensure_dirs()
    print(f"== harness v{P.FORMAT_VERSION} ==")
    print(f"repo root: {P.REPO_ROOT}")

    print("\n[1/5] windows")
    W.assert_matches_ledger()
    wf = W.windows_frame()
    wf.to_csv(P.OUT_WINDOWS, index=False)
    print(f"  W1 = {len(W.GUIDE_DATES_W1)} guide dates (targets "
          f"{W.W1_TARGETS[0]}..{W.W1_TARGETS[-1]})")
    print(f"  W2 = {len(W.GUIDE_DATES_W2)} guide dates (targets "
          f"{W.W2_TARGETS[0]}..{W.W2_TARGETS[-1]})")
    print(f"  LIVE = {W.GUIDE_DATE_LIVE} -> {W.LIVE_TARGETS} (enters no metric)")

    print("\n[2/5] calendar")
    cal = build_calendar()
    cal.to_csv(P.OUT_CALENDAR, index=False)
    print(f"  {len(cal)} events {cal['print_quarter'].iloc[0]}..{cal['print_quarter'].iloc[-1]}"
          f"; {int(cal['is_forecast_row'].sum())} forecast row(s); "
          f"{cal['filing_date'].notna().sum()} with an EDGAR filing date")

    print("\n[3/5] targets")
    tgt = build_targets(cal)
    tgt.to_csv(P.OUT_TARGETS, index=False)
    clear_cache()
    print(f"  {len(tgt)} quarters, {int(tgt['has_actual'].sum())} with a printed revenue; "
          f"{tgt['guide_mid'].notna().sum()} revenue guides; "
          f"{tgt['street_pre_guide_musd'].notna().sum()} pre-guide Street values")
    c = tgt["actual_over_guide_mid"].dropna()
    print(f"  cushion actual/guide_mid over {len(c)} realised guides: "
          f"mean {100*(c.mean()-1):+.3f}%, median {100*(c.median()-1):+.3f}%, "
          f"sd {100*c.std():.3f}pp")

    # ACCEPTANCE TEST: the chief of staff's cushion (mean +1.856%, median +1.790%,
    # sd 1.006pp) is the TRAILING-8 window as of the 2026-08-06 guide date, not the
    # full 19-guide sample. Reproducing it is how the harness proves both its cushion
    # construction and its same-day information-set convention.
    import numpy as _np
    pool = tgt[tgt["actual_over_guide_mid"].notna() & tgt["print_date"].notna()]
    pool = pool[pool["print_date"].map(lambda d: pd.notna(d) and d <= W.GUIDE_DATE_LIVE)]
    t8 = 100.0 * (pool.sort_values("quarter")["actual_over_guide_mid"].to_numpy()[-8:] - 1.0)
    got = (float(t8.mean()), float(_np.median(t8)), float(t8.std(ddof=1)))
    want = (1.856, 1.790, 1.006)
    ok = all(abs(a - b) < 0.005 for a, b in zip(got, want))
    print(f"  ACCEPTANCE trailing-8 cushion @ {W.GUIDE_DATE_LIVE}: "
          f"mean {got[0]:+.4f}% median {got[1]:+.4f}% sd {got[2]:.4f}pp  "
          f"(target {want[0]:+.3f}/{want[1]:+.3f}/{want[2]:.3f}) -> "
          f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        raise AssertionError(f"cushion acceptance test failed: got {got}, want {want}")

    print("\n[4/5] baselines -> registry")
    frames, refusals = build_all_baselines(verbose=True)
    for obj, df in frames.items():
        register(df, quiet=False)
    if refusals:
        pd.DataFrame({"refusal": refusals}).to_csv(
            P.HARNESS_OUT / "street_vintage_refusals.csv", index=False)

    print("\n[5/5] conformal grid + scoreboard")
    pd.DataFrame(M.attainable_coverage_grid()).to_csv(P.OUT_CONFORMAL_GRID, index=False)
    rc = score_main()
    print("\nDONE")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
