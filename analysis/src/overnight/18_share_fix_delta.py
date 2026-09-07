"""Workstream 18: what the FY2026 share-count fix (WS17 finding 3) moves.

Runs workstream 13's driver model twice in one process - once with
`13_driver_model.SHARE_ROLL_NETS_1H26 = False` (the pre-fix path: the FULL-YEAR FY2026 buyback and
SBC applied to the 30 Jun 2026 diluted count, which double-counts the 1H26 repurchase) and once with
it True (the fix: FY2026 consumes only the 2H26 buyback and 2H26 SBC, the same deltas the net-cash
line uses) - and tabulates every per-share and price output that moves.

Nothing above the share line changes: revenue, margins, EBITDA, FCF and net cash are identical in
both runs, so they are not in the output.

READS   analysis/src/overnight/13_driver_model.py (imported; it reads the WS02/07/10/11 panels)
WRITES  data/processed/overnight/18_share_fix_delta.csv

RUN   py -3.13 analysis/src/overnight/18_share_fix_delta.py
"""
from __future__ import annotations

import csv
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OD = lambda n: os.path.join(ROOT, "data", "processed", "overnight", n)   # noqa: E731

_spec = importlib.util.spec_from_file_location("dm13", os.path.join(HERE, "13_driver_model.py"))
DM = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(DM)

PER_SHARE = [("shares_end", "Diluted shares, period end", "M", 4),
             ("fcf_per_share", "FCF per share", "$", 4),
             ("sbc_adj_fcf_per_share", "SBC-adjusted FCF per share", "$", 4),
             ("eps", "Earnings proxy per share", "$", 4)]


def run():
    """Return {(kind, scenario, year_or_lens): value} for one setting of the flag."""
    out = {}
    A = {}
    for scen in DM.SCENARIOS:
        ann = DM.build_annual(scen)
        A[scen] = {a["year"]: a for a in ann}
        for a in ann:
            for k, _lab, _u, _d in PER_SHARE:
                out[("annual", scen, f"FY{a['year']}E {_lab}")] = a[k]
        rows, _px, _ = DM.valuation(ann, scen)
        for r in rows:
            if r["price"] != "":
                out[("price", scen, r["lens"])] = r["price"]
    # scenario grid: the base-case FY2027 cell of the sensitivity grid, at the three exit multiples
    b27 = A["Base"][2027]
    for mult in (13.5, 16.5, 18.5, 22.0):
        e = A["Base"][2026]["revenue"] * 1.10 * 0.365          # the grid's +10% / 36.5% cell
        out[("grid", "Base", f"grid cell +10% rev, 36.5% margin, {mult:.1f}x")] = \
            (mult * e + b27["net_cash"]) / b27["shares_end"]
    return out


def main():
    DM.SHARE_ROLL_NETS_1H26 = False
    before = run()
    DM.SHARE_ROLL_NETS_1H26 = True
    after = run()

    rows = []
    for key in before:
        kind, scen, item = key
        b, a = before[key], after[key]
        rows.append(dict(kind=kind, scenario=scen, item=item,
                         before_prefix=round(b, 4), after_fix=round(a, 4),
                         delta=round(a - b, 4),
                         delta_pct=round(100 * (a / b - 1), 3) if b else ""))
    order = {"annual": 0, "price": 1, "grid": 2}
    scen_order = {"Bear": 0, "Base": 1, "Bull": 2}
    rows.sort(key=lambda r: (order[r["kind"]], scen_order[r["scenario"]], r["item"]))
    with open(OD("18_share_fix_delta.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["kind", "scenario", "item", "before_prefix",
                                           "after_fix", "delta", "delta_pct"])
        w.writeheader()
        w.writerows(rows)
    print(f"18_share_fix_delta.csv: {len(rows)} rows")
    for r in rows:
        if r["scenario"] == "Base" and ("Football" in r["item"] or "FY2026E" in r["item"]):
            print(f"  {r['item']:<52} {r['before_prefix']:>10.2f} -> {r['after_fix']:>10.2f} "
                  f"({r['delta_pct']:+.2f}%)")


if __name__ == "__main__":
    main()
