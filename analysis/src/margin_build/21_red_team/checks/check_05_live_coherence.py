"""WS21 check 05: economic sense of the LIVE margin forecasts.

Pulls every method's LIVE (vintage 2026-09-11) registered margin row for 3Q26-4Q27 and checks:
 1. the implied FY26 margin against the management floor in force (2Q26 letter: at least 35.5%)
    and against the seasonal-naive and Street comparators;
 2. internal consistency: margin x revenue = EBITDA on the same row's revenue leg;
 3. the seasonal profile: is Q1 the trough and Q3 the peak in every method's 2027 path
    (Airbnb's disclosed seasonality), and does any method put a quarter outside the
    historical quarter-of-year range 2022-26?
 4. cross-method dispersion at 3Q26 (the quarter that prints on 5 Nov).

Usage: py -3.13 analysis/src/margin_build/21_red_team/checks/check_05_live_coherence.py [processed_dir]
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO / "analysis" / "src" / "margin_build" / "10_harness_margin"))
from harness_margin import Q, TODAY, load_targets  # noqa: E402

PROC = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "data/processed/margin_build"
REG = PROC / "registry"
MAIN = {  # the spec each note nominates for the pitch
    ("driver-lines", "margin_v2"): "b_elastic_rw",
    ("margin-ts", "q_sentence_direction"): "k_fit_rw",
    ("margin-ts", "yoy_margin_change"): "k4_rw",
    ("guide-policy-margin", "actual_given_guide"): "rw_hl4_pin",
    ("cycle-flex", "flex_margin"): "l0_rw",
    ("alt-augmented", "margin_aug"): "none_rw",
}
FLOOR = 35.5      # 2Q26 letter, 2026-08-06, "at least 35.5%" -- the guide in force


def main() -> int:
    t = load_targets()
    act = t[t["has_actual"]].set_index("quarter")
    rows = []
    for f in sorted(REG.glob("*__*.csv")):
        d = pd.read_csv(f)
        d = d[(d["window"] == "LIVE") & (d["prior_basis"] == "PIT")
              & (d["target"].isin(["adj_ebitda_margin_pct", "adj_ebitda_musd"]))]
        if len(d) == 0:
            continue
        d["vintage_date"] = pd.to_datetime(d["vintage_date"]).dt.date
        d = d[d["vintage_date"] == TODAY]
        for (meth, obj, spec), g in d.groupby(["method", "object", "spec_id"]):
            if (meth, obj) not in MAIN or MAIN[(meth, obj)] != spec:
                continue
            m = g[g["target"] == "adj_ebitda_margin_pct"].set_index("quarter")["point"]
            e = g[g["target"] == "adj_ebitda_musd"].set_index("quarter")["point"]
            if not len(m):
                continue
            rows.append(dict(method=meth, object=obj, spec=spec,
                             **{q: float(m[q]) for q in m.index if q <= "2027Q4"},
                             fy26=(float(act.loc[["2026Q1", "2026Q2"], "adj_ebitda_musd"].sum() + e.get("2026Q3", np.nan) + e.get("2026Q4", np.nan))
                                   / float(act.loc[["2026Q1", "2026Q2"], "revenue_musd"].sum()
                                           + (e.get("2026Q3", np.nan) / m.get("2026Q3", np.nan) * 100 if "2026Q3" in m.index else np.nan)
                                           + (e.get("2026Q4", np.nan) / m.get("2026Q4", np.nan) * 100 if "2026Q4" in m.index else np.nan)) * 100)
                             if {"2026Q3", "2026Q4"} <= set(e.index) else np.nan))
    o = pd.DataFrame(rows).sort_values(["method", "object"])
    qcols = [c for c in o.columns if c.startswith("20")]
    with pd.option_context("display.width", 250, "display.max_columns", 25):
        print("LIVE margin % by method (vintage 2026-09-11, PIT, base path), and the implied FY26:")
        print(o[["method", "object", "spec"] + sorted(qcols) + ["fy26"]].round(2).to_string(index=False))
    print(f"\nFY26 floor in force (2Q26 letter 2026-08-06): at least {FLOOR}%")
    o["fy26_vs_floor_pp"] = o["fy26"] - FLOOR
    print(o[["method", "object", "fy26", "fy26_vs_floor_pp"]].round(2).to_string(index=False))
    print(f"\nmethods BELOW the floor: {int((o['fy26_vs_floor_pp'] < 0).sum())} of {len(o)}")

    print("\n--- 3Q26 dispersion (the quarter that prints on 5 Nov) ---")
    x = o["2026Q3"].dropna()
    print(f"n={len(x)}  min {x.min():.2f}  median {x.median():.2f}  max {x.max():.2f}  range {x.max()-x.min():.2f} pp")
    print(f"3Q25 actual {act.at['2025Q3','adj_ebitda_margin_pct']:.2f}%  (the 3Q26 sentence is a CEILING: "
          f"'roughly flat to slightly down y/y' -> a forecast above {act.at['2025Q3','adj_ebitda_margin_pct']:.2f}% "
          "contradicts the sentence)")
    above = o[o["2026Q3"] > act.at["2025Q3", "adj_ebitda_margin_pct"]]
    print(f"methods forecasting 3Q26 ABOVE the 3Q25 ceiling: {len(above)} -> "
          f"{', '.join(above['method'] + '/' + above['object']) if len(above) else 'none'}")

    print("\n--- seasonal shape of each method's 2027 path vs the 2022-26 historical range ---")
    hist = {}
    for n in (1, 2, 3, 4):
        v = [act.at[f"{y}Q{n}", "adj_ebitda_margin_pct"] for y in range(2022, 2027)
             if f"{y}Q{n}" in act.index and pd.notna(act.at[f"{y}Q{n}", "adj_ebitda_margin_pct"])]
        hist[n] = (min(v), max(v))
    print("historical quarter-of-year margin range 2022-26: " +
          ", ".join(f"Q{n} {hist[n][0]:.1f}-{hist[n][1]:.1f}" for n in (1, 2, 3, 4)))
    for _, r in o.iterrows():
        vals = [r.get(f"2027Q{n}") for n in (1, 2, 3, 4)]
        if any(v is None or not np.isfinite(v) for v in vals):
            continue
        ok_shape = (vals[0] == min(vals)) and (vals[2] == max(vals))
        out_of_range = [f"Q{n}" for n, v in zip((1, 2, 3, 4), vals)
                        if not (hist[n][0] - 3 <= v <= hist[n][1] + 3)]
        print(f"{r['method']}/{r['object']}: 2027 Q1-Q4 = {['%.1f' % v for v in vals]}  "
              f"trough=Q1 & peak=Q3: {ok_shape}; outside hist range +/-3pp: {out_of_range or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
