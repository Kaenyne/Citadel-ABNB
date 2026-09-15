"""T1 vendor equivalence (G1b step 7): DoltHub snapshot strictly before the guide / print date
versus the register's press-quote values. Pre-registered pass lines are in the note; this script
only computes. Reads the BACKUP register (the pre-append state), the harness calendar and the
DoltHub weekly panel.

    python analysis/src/forecast_methods/L0_dolthub_v2/t1_vendor_equivalence.py

Writes data/processed/forecast_methods/L0_dolthub_v2/t1_vendor_equivalence.csv and .json.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BACKUP = REPO / "data/processed/forecast_methods/L0/L0_vintage_register.backup_2026-09-14.csv"
CAL = REPO / "data/processed/forecast_methods/harness/calendar.csv"
OUT_DIR = REPO / "data/processed/forecast_methods/L0_dolthub_v2"
PANEL = OUT_DIR / "dolthub_weekly_panel.csv"

PRE_GUIDE_MEDIAN_MAX = 1.0     # % (pre-registered)
PRE_GUIDE_SIGN_MIN = 16        # of 18 (pre-registered)
AT_PRINT_MEDIAN_MAX = 0.5      # % (pre-registered)


def latest_before(panel: pd.DataFrame, period: str, date: str):
    d = panel[(panel["period"] == period) & (panel["date"] < date)]
    if d.empty:
        return None
    r = d.sort_values("date").iloc[-1]
    return {"date": r["date"], "value": float(r["value_musd"]), "n": r["n"], "slot": r["slot"]}


def main() -> int:
    reg = pd.read_csv(BACKUP, comment="#")
    reg["pit_usable"] = reg["pit_usable"].astype(str).str.lower().isin(("true", "1"))
    cal = pd.read_csv(CAL)
    panel = pd.read_csv(PANEL, dtype={"date": str})
    guide_of = {r.next_quarter_guided: (r.guide_date, float(r.guide_mid))
                for r in cal.itertuples() if isinstance(r.next_quarter_guided, str)}
    print_of = {r.print_quarter: r.print_date for r in cal.itertuples()
                if isinstance(r.print_date, str) and r.print_date_basis == "ledger"}

    rows = []
    pg = reg[(reg["role"] == "pre_guide") & reg["pit_usable"] & reg["value"].notna()
             & (reg["metric"] == "revenue")]
    for r in pg.itertuples():
        gdate, gmid = guide_of[r.period]
        dh = latest_before(panel, r.period, gdate)
        diff = (dh["value"] - r.value) / r.value * 100 if dh else None
        s_reg = int(np.sign(gmid - r.value))
        s_dh = int(np.sign(gmid - dh["value"])) if dh else None
        rows.append({"cell": "pre_guide", "register_id": r.register_id, "period": r.period,
                     "event_date": gdate, "guide_mid": gmid,
                     "register_vendor": r.vendor, "register_value": float(r.value),
                     "register_as_of": r.as_of_timestamp,
                     "dolthub_date": dh["date"] if dh else None, "dolthub_value": dh["value"] if dh else None,
                     "dolthub_n": dh["n"] if dh else None, "dolthub_slot": dh["slot"] if dh else None,
                     "diff_pct": diff, "sign_register": s_reg, "sign_dolthub": s_dh,
                     "sign_agree": (s_reg == s_dh) if dh else None})

    ap = reg[(reg["role"] == "at_print") & (reg["metric"] == "revenue") & reg["value"].notna()]
    for r in ap.itertuples():
        pdate = print_of.get(r.period)
        dh = latest_before(panel, r.period, pdate) if pdate else None
        diff = (dh["value"] - r.value) / r.value * 100 if dh else None
        rows.append({"cell": "at_print", "register_id": r.register_id, "period": r.period,
                     "event_date": pdate, "guide_mid": None,
                     "register_vendor": r.vendor, "register_value": float(r.value),
                     "register_as_of": r.as_of_timestamp,
                     "dolthub_date": dh["date"] if dh else None, "dolthub_value": dh["value"] if dh else None,
                     "dolthub_n": dh["n"] if dh else None, "dolthub_slot": dh["slot"] if dh else None,
                     "diff_pct": diff, "sign_register": None, "sign_dolthub": None, "sign_agree": None})

    # the two holes, reported only
    holes = []
    for period in ("2021Q4", "2024Q3"):
        gdate, gmid = guide_of[period]
        dh = latest_before(panel, period, gdate)
        holes.append({"register_id": f"PG-{period}-revenue", "period": period, "guide_date": gdate,
                      "guide_mid": gmid, "dolthub": dh,
                      "sign_guide_minus_street": int(np.sign(gmid - dh["value"])) if dh else None})

    df = pd.DataFrame(rows)
    df.to_csv(OUT_DIR / "t1_vendor_equivalence.csv", index=False)

    g = df[df["cell"] == "pre_guide"]
    gd = g.dropna(subset=["diff_pct"])
    a = df[df["cell"] == "at_print"]
    ad = a.dropna(subset=["diff_pct"])
    summ = {
        "pre_guide": {"n_cells": int(len(g)), "n_with_dolthub": int(len(gd)),
                      "median_abs_diff_pct": float(gd["diff_pct"].abs().median()),
                      "mean_diff_pct": float(gd["diff_pct"].mean()),
                      "max_abs_diff_pct": float(gd["diff_pct"].abs().max()),
                      "sign_agree": int(gd["sign_agree"].sum()), "sign_total": int(len(gd)),
                      "disagreements": gd[~gd["sign_agree"].astype(bool)][
                          ["register_id", "guide_mid", "register_value", "dolthub_value"]].to_dict("records"),
                      "pass": bool(gd["diff_pct"].abs().median() <= PRE_GUIDE_MEDIAN_MAX
                                   and gd["sign_agree"].sum() >= PRE_GUIDE_SIGN_MIN)},
        "at_print": {"n_cells": int(len(a)), "n_with_dolthub": int(len(ad)),
                     "median_abs_diff_pct": float(ad["diff_pct"].abs().median()),
                     "mean_diff_pct": float(ad["diff_pct"].mean()),
                     "max_abs_diff_pct": float(ad["diff_pct"].abs().max()),
                     "missing": a[a["diff_pct"].isna()]["register_id"].tolist(),
                     "pass": bool(ad["diff_pct"].abs().median() <= AT_PRINT_MEDIAN_MAX)},
        "holes": holes,
    }
    summ["T1_PASS"] = summ["pre_guide"]["pass"] and summ["at_print"]["pass"]
    (OUT_DIR / "t1_vendor_equivalence.json").write_text(json.dumps(summ, indent=1, default=str))
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(df.to_string(index=False))
    print(json.dumps(summ, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
