"""Registry baseline (G1b step 8): the DoltHub next-quarter revenue snapshot strictly before each
guide date as a vintage-stamped Street value, in harness FORMAT 1.0.

    python analysis/src/forecast_methods/L0_dolthub_v2/register_street_dolthub.py

Writes data/processed/forecast_methods/registry/l0-dolthub-v2__street_dolthub.csv through
harness.register() (validator enforces the PIT rules). Method = this package's name, object =
street_dolthub. Mirrors harness.baselines.baseline_street: point = q50 = the Street value,
n_params = 0, Gaussian ladder from the sd of trailing actual/Street ratios (PIT: quarters printed
on or before the vintage date, last 8; full_sample: all quarters with an actual).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "analysis/src/forecast_methods"))

from harness import windows as W, quarters as Q, register, load_targets  # noqa: E402
from harness.baselines import _wrap  # noqa: E402

PANEL = REPO / "data/processed/forecast_methods/L0_dolthub_v2/dolthub_weekly_panel.csv"
METHOD, OBJECT = "l0-dolthub-v2", "street_dolthub"
VENDOR = "DoltHub post-no-preference/earnings"
N_CAL = 8


def latest_before(panel: pd.DataFrame, period: str, date) -> tuple[str, float, int] | None:
    d = panel[(panel["period"] == period) & (panel["date"] < str(date))]
    if d.empty:
        return None
    r = d.sort_values("date").iloc[-1]
    return str(r["date"]), float(r["value_musd"]), int(r["n"])


def main() -> int:
    panel = pd.read_csv(PANEL, dtype={"date": str})
    t = load_targets()
    actual = {r.quarter: float(r.revenue_musd) for r in t.itertuples() if pd.notna(r.revenue_musd)}
    printed = {r.quarter: r.print_date for r in t.itertuples() if pd.notna(r.print_date)}

    # DoltHub pre-guide Street for every guided quarter (the calibration history)
    street = {}
    for gdate, tq in W.GUIDE_EVENTS_ALL:
        hit = latest_before(panel, tq, gdate)
        if hit:
            street[tq] = hit
    hist_all = [(tq, actual[tq] / street[tq][1], printed[tq]) for tq in street
                if tq in actual and tq in printed]

    rows = []
    for gdate, tq in W.GUIDE_EVENTS_ALL:
        wins = W.window_of_target(tq)
        if not wins or tq not in street:
            continue
        as_of, val, n = street[tq]
        for basis in ("PIT", "full_sample"):
            if basis == "PIT":
                ratios = [r for _, r, pdte in hist_all if pdte <= gdate][-N_CAL:]
            else:
                ratios = [r for _, r, _ in hist_all]
            ratios = np.asarray(ratios, dtype=float)
            sigma = float(np.std(ratios, ddof=1)) if len(ratios) >= 3 else 0.03
            d = _wrap(val, sigma, True, int(len(ratios)), 0,
                      f"DoltHub next-quarter snapshot {as_of} (n={n}) strictly before guide date {gdate}; "
                      f"sigma from {len(ratios)} actual/street ratios ({basis})")
            d["q50"] = val
            d["street_vendor"] = VENDOR
            d["street_as_of"] = as_of
            d["knowable_from"] = as_of
            for win in wins:
                row = {"method": METHOD, "object": OBJECT, "target": "revenue_musd", "quarter": tq,
                       "vintage_date": gdate,
                       "horizon_q": Q.to_index(tq) - Q.to_index(Q.quarter_of_date(gdate)),
                       "window": win, "prior_basis": basis,
                       "spec_id": f"{OBJECT}|revenue_musd|{basis}"}
                row.update(d)
                rows.append(row)
    df = pd.DataFrame(rows)
    path = register(df)
    print(f"{len(df)} rows -> {path}")
    print(df[["quarter", "vintage_date", "window", "prior_basis", "point", "street_as_of", "n_train"]]
          .drop_duplicates(["quarter", "window", "prior_basis"]).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
