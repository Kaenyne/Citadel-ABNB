"""WS20 step 8: the M4 warning, tested.

M4 warned that a line-level improvement can make the MARGIN worse, because the line errors
of a driver model partly cancel. This re-scores every line-level claim on
adj_ebitda_margin_pct: for each (method, spec) it puts the mean line-level MAE ratio to
seasonal_naive across the five cash lines next to the margin-level ratio of the SAME method
and spec (the margin object built on those lines).

Object pairing: M1 lines_v2 -> margin_v2, M4 lines_aug -> margin_aug,
M6 flex_lines -> flex_margin, M2 pct_rev_seasonal / per_night_seasonal / sarima_margin
register both the lines and the margin under one object.
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data" / "processed" / "margin_build" / "20_scoreboard"
LINES = ["cor_cash_musd", "ops_cash_musd", "pd_cash_musd", "sm_cash_musd",
         "ga_cash_ex_reserves_musd"]
PAIR = {"lines_v2": "margin_v2", "lines_aug": "margin_aug", "flex_lines": "flex_margin",
        "pct_rev_seasonal": "pct_rev_seasonal", "per_night_seasonal": "per_night_seasonal",
        "sarima_margin": "sarima_margin"}
ORACLE = "revknown|nightsknown|ebitda_known"


def main():
    m = pd.read_csv(OUT / "20_scoreboard_master.csv")
    m = m[(m.horizon_q == 0) & (~m.spec_id.str.contains(ORACLE, case=False, na=False))]

    rows = []
    for (meth, obj_l, spec, win, w), g in m[m.target.isin(LINES)].groupby(
            ["method", "object", "spec_id", "window", "weighting"]):
        obj_m = PAIR.get(obj_l)
        if obj_m is None:
            continue
        mm = m[(m.method == meth) & (m.object == obj_m) & (m.spec_id == spec)
               & (m.window == win) & (m.weighting == w)
               & (m.target == "adj_ebitda_margin_pct")]
        if mm.empty:
            continue
        rows.append(dict(method=meth, lines_object=obj_l, margin_object=obj_m, spec_id=spec,
                         window=win, weighting=w, n_lines=len(g),
                         mean_line_mae_ratio_naive=g.ratio_seasonal_naive.mean(),
                         best_line_mae_ratio_naive=g.ratio_seasonal_naive.min(),
                         worst_line_mae_ratio_naive=g.ratio_seasonal_naive.max(),
                         margin_mae=float(mm.mae.iloc[0]),
                         margin_mae_ratio_naive=float(mm.ratio_seasonal_naive.iloc[0]),
                         margin_mae_ratio_street=float(mm.ratio_street.iloc[0])
                         if pd.notna(mm.ratio_street.iloc[0]) else np.nan,
                         margin_survives_both=mm.survives_both_windows.iloc[0],
                         n_params=int(mm.n_params.iloc[0])))
    d = pd.DataFrame(rows)
    d["line_win_margin_loss"] = (d.mean_line_mae_ratio_naive < 1.0) & (d.margin_mae_ratio_naive >= 1.0)
    d = d.sort_values(["window", "weighting", "mean_line_mae_ratio_naive"])
    d.to_csv(OUT / "20_line_vs_margin.csv", index=False)

    sub = d[(d.window == "W2") & (d.weighting == "equal")]
    if len(sub) > 2:
        c = np.corrcoef(sub.mean_line_mae_ratio_naive, sub.margin_mae_ratio_naive)[0, 1]
    else:
        c = np.nan
    print("rows", len(d), "| W2 equal: corr(mean line ratio, margin ratio) =", round(float(c), 3))
    print(sub[["method", "lines_object", "spec_id", "mean_line_mae_ratio_naive",
               "margin_mae", "margin_mae_ratio_naive", "line_win_margin_loss"]].to_string(index=False))


if __name__ == "__main__":
    main()
