"""
WS-J step 1b: test the calendar listed-price y/y (J1 output) against the like-for-like
pricing residual and disclosed ex-FX ADR.

Two alignments, because a calendar price is a price for a FUTURE stay:
  stay-quarter alignment   the y/y of asking prices for stays in quarter q, as posted at the
                           snapshot, against the residual / ex-FX of quarter q (the quarter in
                           which those stays are realised and reported);
  snapshot-quarter alignment  the 0-90 day forward window at snapshot quarter s against the
                           residual / ex-FX of s (same quarter) and s+1 (one quarter ahead).

With prices ending at the May 2025 vintages, the panel is six pairs on four markets in two
regions and at most five stay quarters, so no walk-forward or permutation test is possible.
Reported: n, Pearson r, sign agreement (both series above their own mean is not meaningful
at n <= 5, so sign agreement is on the level: does the listed-price y/y have the same sign
as the residual, which is positive in every quarter), mean absolute gap, and the plain
statement of the two series side by side. Also tested: the region series against the
disclosed regional ex-FX ADR of that region (NA, EMEA).

Run: py -3.13 analysis/src/adrq3/J1b_calendar_tests.py
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MAIN = r"C:\Users\krish\citadel-abnb"
OUT = os.path.join(HERE, "data", "processed", "adrq3", "J")
QORDER = [f"{q}Q{str(y)[-2:]}" for y in range(2017, 2028) for q in range(1, 5)]
qi = {q: i for i, q in enumerate(QORDER)}

cal = pd.read_csv(os.path.join(OUT, "calendar_price_yoy.csv"))
H = pd.read_csv(os.path.join(HERE, "data", "processed", "q3nowcast", "H", "adr_history_components.csv")).set_index("quarter")
reg = pd.read_csv(os.path.join(MAIN, "data", "processed", "adr", "04_regional_quarterly_wide.csv")).set_index("quarter")
tgt = pd.DataFrame({
    "residual_pricing_pp": H["residual_pricing_pp"],
    "adr_exfx_yoy_pp": H["adr_exfx_yoy_pp"],
    "adr_exfx_na_pp": reg["adr_yoy_exfx_na_pct"],
    "adr_exfx_emea_pp": reg["adr_yoy_exfx_emea_pct"],
})
REGION_TGT = {"global": ["residual_pricing_pp", "adr_exfx_yoy_pp"],
              "na": ["residual_pricing_pp", "adr_exfx_yoy_pp", "adr_exfx_na_pp"],
              "emea": ["residual_pricing_pp", "adr_exfx_yoy_pp", "adr_exfx_emea_pp"]}
STATS = ["median_yoy_pct", "trimmed_mean_yoy_pct", "mean_ratio_yoy_pct"]

rows, side = [], []


def add(region, regime, stat, alignment, pairs_xy, label_q):
    x = np.array([p[0] for p in pairs_xy], float)
    y = np.array([p[1] for p in pairs_xy], float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if len(x) < 2:
        return
    r = float(np.corrcoef(x, y)[0, 1]) if len(x) >= 3 and x.std() > 0 and y.std() > 0 else np.nan
    rows.append({"region": region, "regime": regime, "statistic": stat, "alignment": alignment,
                 "target": label_q, "n": int(len(x)), "pearson_r": r,
                 "sign_agreement": float((np.sign(x) == np.sign(y)).mean()),
                 "mean_gap_pp": float((x - y).mean()), "mean_abs_gap_pp": float(np.abs(x - y).mean()),
                 "listed_price_yoy_mean": float(x.mean()), "target_mean": float(y.mean()),
                 "direction_agreement_on_changes": float((np.sign(np.diff(x)) == np.sign(np.diff(y))).mean()) if len(x) >= 3 else np.nan})


for region, tlist in REGION_TGT.items():
    c = cal[cal.region == region]
    for regime in sorted(c.regime.unique()):
        for stat in STATS:
            # (i) stay-quarter alignment: average across the two snapshots when both cover a stay quarter
            sq = c[(c.regime == regime) & (c.group_type == "stay_quarter")]
            s = sq.groupby("group")[stat].mean()
            s = s[[q for q in s.index if q in qi]]
            s = s.reindex(sorted(s.index, key=lambda q: qi[q]))
            for t in tlist:
                pairs = [(s[q], tgt[t].get(q, np.nan)) for q in s.index if q in tgt.index]
                add(region, regime, stat, "stay_quarter_same", pairs, t)
                for q in s.index:
                    side.append({"region": region, "regime": regime, "statistic": stat, "alignment": "stay_quarter",
                                 "quarter": q, "listed_price_yoy_pct": s[q], "target": t, "target_value": tgt[t].get(q, np.nan)})
            # (ii) snapshot-quarter alignment, 0-90 day window
            sn = c[(c.regime == regime) & (c.group_type == "lead") & (c.group == "0-90")]
            s2 = sn.groupby("snapshot1_quarter")[stat].mean()
            for t in tlist:
                add(region, regime, stat, "snapshot_same_quarter", [(s2[q], tgt[t].get(q, np.nan)) for q in s2.index], t)
                add(region, regime, stat, "snapshot_next_quarter",
                    [(s2[q], tgt[t].get(QORDER[qi[q] + 1], np.nan)) for q in s2.index], t)

res = pd.DataFrame(rows)
res.to_csv(os.path.join(OUT, "calendar_price_tests.csv"), index=False)
pd.DataFrame(side).to_csv(os.path.join(OUT, "J1b_calendar_vs_targets_side_by_side.csv"), index=False)
pd.set_option("display.width", 250)
print(res[(res.statistic == "median_yoy_pct")].round(2).to_string())
sb = pd.DataFrame(side)
print(sb[(sb.statistic == "median_yoy_pct") & (sb.target == "residual_pricing_pp")].pivot_table(
    index="quarter", columns=["region", "regime"], values="listed_price_yoy_pct").round(1).to_string())
