"""Workstream 17: does the scenario selector on `Inputs!B4` (named range `Scenario`) actually
switch the workbook in Excel?

The three Excel dumps it reads are produced by the PowerShell COM driver
(scratchpad/17/recalc_dump.ps1), which opens a copy of `model/ABNB_driver_model.xlsx`, writes 1 / 2
/ 3 into `Inputs!B4`, calls `Application.CalculateFullRebuild()` and dumps every non-empty cell:

  17_dump_after_scen1.csv  selector = 1 (Bear)
  17_excel_recalc_dump.csv selector = 2 (Base, the file as shipped)  [data/processed/overnight]
  17_dump_after_scen3.csv  selector = 3 (Bull)

WRITES  data/processed/overnight/17_scenario_switch.csv

RUN   py -3.13 analysis/src/overnight/17_scenario_switch.py [dump_dir]
"""
from __future__ import annotations

import importlib.util
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OD = lambda n: os.path.join(ROOT, "data", "processed", "overnight", n)      # noqa: E731
DEFAULT_DUMPS = os.path.join(
    os.environ.get("TEMP", "."), "claude", "C--Users-krish-citadel-abnb",
    "fe93ae72-a37b-4547-991f-690c32a0f6a0", "scratchpad", "17")

_a = importlib.util.spec_from_file_location("wa17", os.path.join(HERE, "17_excel_audit.py"))
AU = importlib.util.module_from_spec(_a)
_a.loader.exec_module(AU)

SCEN = {1: "Bear", 2: "Base", 3: "Bull"}


def load(path):
    d = pd.read_csv(path)
    d["formula"] = d["formula"].fillna("")
    out = {}
    for r in d.itertuples():
        try:
            out[(r.sheet, r.address)] = float(r.value)
        except (TypeError, ValueError):
            out[(r.sheet, r.address)] = None
    return d, out


def main():
    dd = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DUMPS
    paths = {1: os.path.join(dd, "17_dump_after_scen1.csv"),
             2: OD("17_excel_recalc_dump.csv"),
             3: os.path.join(dd, "17_dump_after_scen3.csv")}
    dumps = {k: load(p) for k, p in paths.items()}
    pym, _ = AU.python_mirror()

    # the Valuation / Card_5Nov rows the selector is meant to drive: column E, a CHOOSE formula
    base_df = dumps[2][0]
    active = {}
    for sh in ("Valuation", "Card_5Nov"):
        lab = base_df[(base_df.sheet == sh) & (base_df.col == 1)].set_index("row")["value"]
        sub = base_df[(base_df.sheet == sh) & (base_df.col == 5)
                      & (base_df.formula.str.contains("CHOOSE"))]
        for r in sub.itertuples():
            active[(sh, r.address)] = str(lab.get(r.row, ""))

    # the same measure in the scenario's own column: B = Bear, C = Base, D = Bull on Valuation,
    # B / C / D on Card_5Nov
    rows = []
    for sel, scen in SCEN.items():
        _df, val = dumps[sel]
        for (sh, addr), label in sorted(active.items()):
            r = int(addr[1:])
            own = val.get((sh, {1: "B", 2: "C", 3: "D"}[sel] + str(r)))
            act = val.get((sh, addr))
            ok = own is not None and act is not None and abs(act - own) <= 1e-9 * max(1.0, abs(own))
            rows.append(dict(selector=sel, scenario=scen, sheet=sh, active_cell=f"{sh}!{addr}",
                             measure=label.strip(),
                             active_column_value=act,
                             scenario_column_value=own,
                             active_matches_scenario_column="yes" if ok else "NO"))
    # the six valuation lenses and the football field, against the Python mirror
    lens_rows = {"E19": "EV / adj. EBITDA, FY27E", "E20": "EV / FCF, FY27E",
                 "E21": "P / SBC-adjusted FCF, FY27E", "E22": "P / earnings proxy, FY27E",
                 "E23": "EV / adj. EBITDA, FY28E", "E39": "DCF on FCF",
                 "E43": "Football field low", "E44": "Football field high",
                 "E45": "Football field mean"}
    for sel, scen in SCEN.items():
        _df, val = dumps[sel]
        for addr, name in lens_rows.items():
            key = f"{scen} {name}" if name.startswith("Football") else f"{scen} price: {name}"
            p = pym.get(key)
            x = val.get(("Valuation", addr))
            rows.append(dict(selector=sel, scenario=scen, sheet="Valuation",
                             active_cell=f"Valuation!{addr}", measure=f"vs Python mirror: {name}",
                             active_column_value=x, scenario_column_value=p,
                             active_matches_scenario_column=(
                                 "yes" if (x is not None and p is not None
                                           and abs(x - p) <= 1e-9 * max(1.0, abs(p))) else "NO")))

    # how many cells the selector moves, by sheet
    b = dumps[2][0].set_index(["sheet", "address"])["value"].astype(str)
    for sel, scen in SCEN.items():
        if sel == 2:
            continue
        o = dumps[sel][0].set_index(["sheet", "address"])["value"].astype(str)
        common = b.index.intersection(o.index)
        diff = b.loc[common] != o.loc[common]
        by = pd.Series([i[0] for i in common[diff]]).value_counts().to_dict()
        rows.append(dict(selector=sel, scenario=scen, sheet="(all)",
                         active_cell="(cells whose value changed vs selector = 2)",
                         measure="; ".join(f"{k}: {v}" for k, v in sorted(by.items())),
                         active_column_value=int(diff.sum()), scenario_column_value=len(common),
                         active_matches_scenario_column=""))

    out = pd.DataFrame(rows)
    out.insert(0, "build", "after (the WS17 fix: Active columns on Valuation and Card_5Nov)")

    # the same count on the pre-fix workbook, if its dumps are still in the scratch directory
    pre = {1: os.path.join(dd, "17_dump_scen1.csv"), 2: os.path.join(dd, "before",
                                                                    "17_excel_recalc_dump.csv"),
           3: os.path.join(dd, "17_dump_scen3.csv")}
    if all(os.path.exists(v) for v in pre.values()):
        pb = load(pre[2])[0].set_index(["sheet", "address"])["value"].astype(str)
        extra = []
        for sel, scen in SCEN.items():
            if sel == 2:
                continue
            po = load(pre[sel])[0].set_index(["sheet", "address"])["value"].astype(str)
            common = pb.index.intersection(po.index)
            diff = pb.loc[common] != po.loc[common]
            by = pd.Series([i[0] for i in common[diff]]).value_counts().to_dict()
            extra.append(dict(build="before (selector drove only the Inputs Active column)",
                              selector=sel, scenario=scen, sheet="(all)",
                              active_cell="(cells whose value changed vs selector = 2)",
                              measure="; ".join(f"{k}: {v}" for k, v in sorted(by.items())),
                              active_column_value=int(diff.sum()),
                              scenario_column_value=len(common),
                              active_matches_scenario_column=""))
        out = pd.concat([pd.DataFrame(extra), out], ignore_index=True)
    out.to_csv(OD("17_scenario_switch.csv"), index=False)
    bad = (out.active_matches_scenario_column == "NO").sum()
    print(f"17_scenario_switch.csv: {len(out)} rows, {bad} mismatches")
    if bad:
        print(out[out.active_matches_scenario_column == "NO"].to_string())
    print(out[out.sheet == "(all)"][["scenario", "measure", "active_column_value"]].to_string())


if __name__ == "__main__":
    main()
