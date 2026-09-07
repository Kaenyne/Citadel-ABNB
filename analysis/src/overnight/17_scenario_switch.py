"""Workstream 17: does the scenario selector on `Inputs!B4` (named range `Scenario`) actually
switch the workbook in Excel?

The three Excel dumps it reads are produced by `analysis/src/overnight/17_recalc_dump.ps1`, the
in-repo PowerShell COM driver, which opens `model/ABNB_driver_model.xlsx`, writes 1 / 2 / 3 into
`Inputs!B4`, calls `Application.CalculateFullRebuild()` and dumps every non-empty cell:

  17_dump_after_scen1.csv  selector = 1 (Bear)
  17_excel_recalc_dump.csv selector = 2 (Base, the file as shipped)  [data/processed/overnight]
  17_dump_after_scen3.csv  selector = 3 (Bull)

WRITES  data/processed/overnight/17_scenario_switch.csv

REGENERATE THE DUMPS (Windows + desktop Excel; ~20 s each)
  powershell -NoProfile -ExecutionPolicy Bypass -File analysis/src/overnight/17_recalc_dump.ps1 \
      -ScenarioValue 1 -OutCsv <dir>\17_dump_after_scen1.csv
  ... -ScenarioValue 3 -OutCsv <dir>\17_dump_after_scen3.csv

RUN   py -3.13 analysis/src/overnight/17_scenario_switch.py [--dump-dir DIR] [--root ROOT]

EXIT  0 = the selector drives the workbook and every comparison matches;
      1 = a failed scenario comparison or an inert selector;
      2 = a required dump is missing.
"""
from __future__ import annotations

import argparse
import importlib.util
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OD = lambda n: os.path.join(ROOT, "data", "processed", "overnight", n)      # noqa: E731

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


def build_parser():
    p = argparse.ArgumentParser(
        description="Check that the Inputs!B4 scenario selector actually switches the workbook in "
                    "real Excel. Exit 1 on a failed comparison or an inert selector, 2 on a "
                    "missing dump.")
    p.add_argument("--root", default=ROOT,
                   help="project root (default: found relative to this script file)")
    p.add_argument("--dump-dir", default=None,
                   help="directory holding 17_dump_after_scen1.csv / _scen3.csv (default: "
                        "<root>/data/processed/overnight, or $ABNB_EXCEL_DUMP_DIR)")
    return p


def main(argv=None):
    # WS24 / audit findings A07 + A13 (6 Sep 2026): the previous default was one user's session
    # scratch directory, which is not a reproducibility contract. The default is now inside the
    # project; an explicit --dump-dir or ABNB_EXCEL_DUMP_DIR still wins, and a missing dump is a
    # loud failure (exit 2) rather than a silent fall-back to a stale file.
    args = build_parser().parse_args(argv)
    root = os.path.abspath(args.root)
    global OD
    OD = lambda n: os.path.join(root, "data", "processed", "overnight", n)   # noqa: E731
    dd = args.dump_dir or os.environ.get("ABNB_EXCEL_DUMP_DIR") or OD("")
    paths = {1: os.path.join(dd, "17_dump_after_scen1.csv"),
             2: OD("17_excel_recalc_dump.csv"),
             3: os.path.join(dd, "17_dump_after_scen3.csv")}
    missing = [v for v in paths.values() if not os.path.exists(v)]
    if missing:
        print("FAIL: missing Excel dump(s): " + "; ".join(missing)
              + "\nRegenerate them with analysis/src/overnight/17_recalc_dump.ps1 (see this "
                "script's docstring), then pass --dump-dir or set ABNB_EXCEL_DUMP_DIR.")
        return 2
    print(f"dump directory: {dd}")
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
    # The six valuation lenses and the football field, against the Python mirror. WS26 (7 Sep 2026):
    # the row numbers used to be hard-coded here, so inserting the undiscounted-FY2028E sensitivity
    # row on the Valuation sheet silently pointed four of them one row off and produced 12 spurious
    # mismatches. They are now resolved from 13_reconciliation.csv's own cell_reference column, which
    # 13_excel_builder.py writes, so a layout change on Valuation can no longer break this check.
    recon = pd.read_csv(OD("13_reconciliation.csv"))
    lens_rows = {}
    for name in ["EV / adj. EBITDA, FY27E", "EV / FCF, FY27E", "P / SBC-adjusted FCF, FY27E",
                 "P / earnings proxy, FY27E", "EV / adj. EBITDA, FY28E", "DCF on FCF",
                 "Football field low", "Football field high", "Football field mean"]:
        item = f"Base {name}" if name.startswith("Football") else f"Base price: {name}"
        hit = recon[recon["item"] == item]
        if hit.empty:
            print(f"FAIL: '{item}' is not in 13_reconciliation.csv; re-run 13_driver_model.py")
            return 1
        lens_rows["E" + str(hit.iloc[0]["cell_reference"]).rsplit("$", 1)[-1]] = name
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
    compared = int((out.active_matches_scenario_column != "").sum())
    summary = len(out) - compared
    print(f"17_scenario_switch.csv: {len(out)} rows = {compared} comparisons + {summary} "
          f"change-count summaries; {bad} mismatches")
    if bad:
        print(out[out.active_matches_scenario_column == "NO"].to_string())
    print(out[out.sheet == "(all)"][["scenario", "measure", "active_column_value"]].to_string())

    # WS19 / audit finding A13 (6 Sep 2026): return a failing status so a broken selector cannot pass
    # for a clean run. A scenario that moves no cells at all is also a failure - that was the original
    # WS17 defect and a silent regression would otherwise look identical to a pass.
    inert = out[(out.sheet == "(all)")
                & (out.build.str.startswith("after"))
                & (out.active_column_value.astype(float) == 0)]
    if bad or compared == 0 or len(inert):
        msgs = []
        if bad:
            msgs.append(f"{bad} of {compared} scenario comparisons mismatch")
        if compared == 0:
            msgs.append("no scenario comparisons were made")
        if len(inert):
            msgs.append(f"selector moves 0 cells for: {sorted(set(inert.scenario))}")
        print("\nFAIL: " + "; ".join(msgs))
        return 1
    print(f"\nPASS: {compared} scenario comparisons, 0 mismatches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
