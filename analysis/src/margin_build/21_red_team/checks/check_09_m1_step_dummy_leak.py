"""WS21 check 09: M1 spec `d_steps_rw` uses WS04 step dummies WITHOUT the knowable_from gate.

M1 (`analysis/src/margin_build/M1_driver_lines/run.py`) builds the step columns into the module-level
PANEL and then, in `design_rows` and `forecast_quarter`, reads the step LEVEL for a quarter straight
out of that panel. It never consults `04_signal_knowable_from.csv`. WS04 dates one of the steps M1
uses -- `event_E09_cor_cash` (the hosting re-cut) -- as turning on in 2025Q1 but only KNOWABLE from
2026-02-12. Every PIT refit and forecast at a vintage between 2025Q1 and 2026-02-12 therefore carries
a regressor the public did not have. (M4 gates the same signals correctly, via `known(ks[q], vd)`.)

This check enumerates the affected (vintage, quarter) pairs and their weight in the registered rows.

Usage: py -3.13 analysis/src/margin_build/21_red_team/checks/check_09_m1_step_dummy_leak.py
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO / "analysis" / "src" / "margin_build" / "10_harness_margin"))
from harness_margin import Q, GUIDE_DATES_W1, GUIDE_DATES_W2  # noqa: E402

WS04 = REPO / "data" / "processed" / "margin_build" / "04_alt_signals"
M1_STEPS = {"cor": ["event_E02_cor_cash", "event_E09_cor_cash"], "ops": ["event_E05_ops_cash"],
            "pd": ["event_E10_pd_cash"]}


def main() -> int:
    p = pd.read_csv(WS04 / "04_signal_panel_quarterly.csv")
    p["quarter"] = p["quarter"].map(Q.canon)
    p = p.set_index("quarter")
    k = pd.read_csv(WS04 / "04_signal_knowable_from.csv")
    k["quarter"] = k["quarter"].map(Q.canon)
    k = k.set_index("quarter")
    cols = sorted({c for v in M1_STEPS.values() for c in v})
    print("WS04 step columns M1 uses, first quarter ON vs the date they became knowable:")
    for c in cols:
        on = p[p[c].fillna(0) > 0].index.min()
        kf = pd.to_datetime(k[c].dropna()).dt.date.max() if c in k.columns else None
        print(f"  {c:24s} first ON {on}   knowable_from {kf}   "
              f"{'<-- HINDSIGHT DATING' if (on and kf and pd.Timestamp(kf) > pd.Timestamp(on[:4] + '-' + str(3*int(on[-1])-2).zfill(2) + '-01')) else ''}")
    print("\nFit/forecast observations that use a step value not yet knowable at the vintage:")
    bad = []
    for vd in sorted(set(GUIDE_DATES_W1) | set(GUIDE_DATES_W2)):
        for c in cols:
            kf = pd.to_datetime(k[c].dropna()).dt.date.max() if c in k.columns else None
            if kf is None or kf <= vd:
                continue
            on_qs = [q for q in p.index if pd.notna(p.at[q, c]) and p.at[q, c] > 0]
            # quarters in the fit window (printed on or before the vintage) that already carry the step
            q0 = Q.quarter_of_date(vd)
            used = [q for q in on_qs if Q.to_index(q) <= Q.to_index(q0) + 2]
            if used:
                bad.append(dict(vintage_date=vd, signal=c, knowable_from=kf,
                                n_quarters_with_step=len(used), first=min(used), last=max(used),
                                windows=("W1" if vd in GUIDE_DATES_W1 else "") + ("/W2" if vd in GUIDE_DATES_W2 else "")))
    b = pd.DataFrame(bad)
    if len(b):
        print(b.to_string(index=False))
        print(f"\nAFFECTED VINTAGES: {b['vintage_date'].nunique()} of {len(set(GUIDE_DATES_W1))} W1 guide dates "
              f"({b[b['windows'].str.contains('W2')]['vintage_date'].nunique()} of {len(set(GUIDE_DATES_W2))} W2). "
              "Spec `d_steps_rw` (and only that spec) is affected; `a_unit`, `b_elastic`, `c_mix`, `e_revknown` "
              "do not use the step columns.")
    else:
        print("  none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
