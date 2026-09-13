#!/usr/bin/env python
"""Rebuild the margin harness end to end: targets, guides, street, revenue leg, seasonal shares,
the seven baseline objects (method `baselines-margin`), and the scoreboard.

  cd "<worktree root>"
  python analysis/src/margin_build/10_harness_margin/run.py

Exit code 0 on success. Overwrites only its own outputs under
data/processed/margin_build/10_harness_margin/ and the baselines-margin__*.csv registry files;
never touches another method's registry file.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness_margin import paths as P                      # noqa: E402
from harness_margin.frozen import W, TODAY                 # noqa: E402
from harness_margin.panel import build_targets, load_targets   # noqa: E402
from harness_margin.guides import build_guides             # noqa: E402
from harness_margin.street import build_street             # noqa: E402
from harness_margin.baselines import (build_revenue_leg, build_seasonal_shares,   # noqa: E402
                                      build_all_baselines)
from harness_margin.registry import register               # noqa: E402
from harness_margin.score import main as score_main        # noqa: E402


def main() -> int:
    P.ensure_dirs()
    print("== margin harness (WS10) on frozen FORMAT 1.0 ==")
    print(f"repo root: {P.REPO_ROOT}")
    print(f"W1 {len(W.GUIDE_DATES_W1)} guide dates, W2 {len(W.GUIDE_DATES_W2)}, LIVE vintages "
          f"{W.GUIDE_DATE_LIVE} and TODAY={TODAY} (the only non-guide date the frozen validator accepts)")

    print("\n[1/6] targets")
    t, info = build_targets(write=True)
    from harness_margin import panel
    panel._CACHE.clear()
    t = load_targets(refresh=True)
    n_act = int(t["has_actual"].sum())
    print(f"  source={info['source']}; {len(t)} quarters {t['quarter'].iloc[0]}..{t['quarter'].iloc[-1]}, "
          f"{n_act} with actuals; WS02 problems: {info.get('ws02_validation_problems')}")
    assert n_act == 26, f"expected 26 actual quarters 1Q20-2Q26, got {n_act}"

    print("\n[2/6] guides")
    g = build_guides(write=True)
    print(f"  {len(g)} numeric margin guides ({int(g['is_fy'].sum())} FY, {int((~g['is_fy']).sum())} quarterly)")

    print("\n[3/6] street (WS03)")
    s = build_street(write=True)
    print(f"  {len(s)} vintage-stamped Street values, {s['target'].nunique() if len(s) else 0} targets, "
          f"{s['vintage_date'].nunique() if len(s) else 0} vintages")

    print("\n[4/6] revenue leg + seasonal shares")
    rl = build_revenue_leg(write=True)
    ss = build_seasonal_shares(write=True)
    print(f"  revenue leg rows {len(rl)}: {rl['leg'].value_counts().to_dict()}")
    fs = ss[ss['prior_basis'] == 'full_sample'].iloc[0]
    print(f"  seasonal EBITDA shares full_sample {fs['years']}: "
          + ", ".join(f"Q{n} {100*fs[f'share_q{n}']:.1f}%" for n in (1, 2, 3, 4)))

    print("\n[5/6] baselines -> registry")
    frames, grid = build_all_baselines(t, verbose=True)
    grid.to_csv(P.OUT_BASELINE_GRID, index=False)
    for obj, df in frames.items():
        register(df, quiet=False)
    # pass line: every object covers all 14 W1 and 10 W2 guide dates for adj EBITDA margin at h=0
    for obj, df in frames.items():
        for win, want in (("W1", 14), ("W2", 10)):
            for tgt in ("adj_ebitda_margin_pct", "adj_ebitda_musd"):
                x = df[(df["window"] == win) & (df["horizon_q"] == 0) & (df["target"] == tgt)
                       & (df["prior_basis"] == "PIT")]
                n = x["vintage_date"].nunique()
                if len(x):
                    flag = "PASS" if n == want else "SHORT"
                    print(f"  coverage {obj:22s} {tgt:22s} {win} h=0: {n:2d}/{want} {flag}")

    print("\n[6/6] scoreboard")
    rc = score_main(verbose=True)
    print("\nDONE")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
