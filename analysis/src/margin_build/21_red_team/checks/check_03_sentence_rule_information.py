"""WS21 check 03: how much information is in M2's q_sentence_direction rule, and where M3's pin win comes from.

Part 1. The quarterly margin sentence in the guidance ledger, quarter by quarter, for the W1 and W2
target quarters: direction (ceiling -1, floor +1, point 0), the realised y/y margin change, and the
seasonal-naive error. Counts how often the direction actually varies -- the rule's only input.
Part 2. Quarter-by-quarter loss differential for the two guide-policy pin specs against seasonal naive,
to show whether the MAE win is broad or carried by one or two quarters.

Usage: py -3.13 analysis/src/margin_build/21_red_team/checks/check_03_sentence_rule_information.py [processed_dir]
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO / "analysis" / "src" / "margin_build" / "10_harness_margin"))
from harness_margin import Q, W, load_targets, q_guide_in_force  # noqa: E402

PROC = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "data/processed/margin_build"
DIR = {"ceiling": -1, "floor": 1, "point": 0}


def main() -> int:
    t = load_targets()
    act = t[t["has_actual"]].set_index("quarter")
    print("=== Part 1: the sentence, quarter by quarter (W1 target quarters) ===")
    rows = []
    for q in W.W1_TARGETS:
        # the guide for q is issued at the print of q-1: use that print date as the vintage
        prev = Q.shift(q, -1)
        vd = act.at[prev, "print_date"] if prev in act.index else None
        g = q_guide_in_force(vd, q, t) if vd is not None else None
        d = DIR.get(g["guide_type"]) if g and g.get("guide_type") else None
        lag = Q.shift(q, -4)
        m, m4 = act.at[q, "adj_ebitda_margin_pct"], act.at[lag, "adj_ebitda_margin_pct"]
        rows.append(dict(quarter=q, guide_date=vd, guide_type=(g or {}).get("guide_type"), direction=d,
                         level_pct=(g or {}).get("level_pct"), margin=m, margin_lag4=m4, yoy_pp=m - m4,
                         sign_agrees=(None if d in (None, 0) else bool(np.sign(m - m4) == d)),
                         in_W2=q in W.W2_TARGETS))
    o = pd.DataFrame(rows)
    with pd.option_context("display.width", 220, "display.max_columns", 20):
        print(o.round(2).to_string(index=False))
    for lab, sub in (("W1", o), ("W2", o[o["in_W2"]])):
        nz = sub[sub["direction"].isin([-1, 1])]
        print(f"\n{lab}: n={len(sub)}; sentences with a non-zero direction {len(nz)}; "
              f"directions -1/+1 = {int((nz['direction'] == -1).sum())}/{int((nz['direction'] == 1).sum())}; "
              f"sign agrees {int(nz['sign_agrees'].sum())}/{len(nz)}; "
              f"number of sign FLIPS along the sequence = {int((nz['direction'].diff() != 0).sum() - 1)}")
        print(f"   if the rule were 'always -k' it would agree {int((nz['yoy_pp'] < 0).sum())}/{len(nz)} times")

    print("\n=== Part 2: where the guide-policy pin win comes from ===")
    bq = pd.read_csv(PROC / "10_harness_margin" / "scoreboard_by_quarter.csv")
    for spec in ("rw_hl4_pin", "last_pin", "rw_hl4"):
        for win in ("W1", "W2"):
            g = bq[(bq["method"] == "guide-policy-margin") & (bq["object"] == "actual_given_guide")
                   & (bq["target"] == "adj_ebitda_margin_pct") & (bq["spec_id"] == spec)
                   & (bq["horizon_q"] == 0) & (bq["prior_basis"] == "PIT") & (bq["window"] == win)].sort_values("quarter")
            if len(g) == 0:
                continue
            d = (g["abs_err"] - g["seasonal_naive_abs_err"]).to_numpy(dtype=float)
            worst = g.iloc[int(np.argmin(d))]
            print(f"{spec:12s} {win}: n={len(d)} mean d={d.mean():+.3f}pp, quarters better {int((d<0).sum())}/{len(d)}; "
                  f"biggest single-quarter gain {d.min():+.2f}pp in {worst['quarter']}; "
                  f"mean d EXCLUDING that quarter {np.delete(d, int(np.argmin(d))).mean():+.3f}pp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
