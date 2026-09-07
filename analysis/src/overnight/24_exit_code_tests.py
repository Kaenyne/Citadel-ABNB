"""Workstream 24: prove that the workbook audits fail loudly (audit finding A13).

Runs `17_excel_audit.py` and `17_scenario_switch.py` as separate PROCESSES against (a) the clean
shipped evidence and (b) deliberately broken copies, and records the exit status of each. A passing
process exit must mean a passing model audit; that is the whole point of A13, and it can only be
demonstrated at the process boundary.

The negative control for the Excel audit is a real one: a scratch copy of the workbook has one
required output cell overwritten with a wrong constant, and the copy is recalculated by real Excel
through `17_recalc_dump.ps1` before the audit reads it. Nothing under model/ or
data/processed/overnight is modified - every broken artifact lives in a temporary directory.

READS   model/ABNB_driver_model.xlsx
        data/processed/overnight/17_excel_recalc_dump.csv, 17_dump_after_scen1.csv,
        17_dump_after_scen3.csv, 13_reconciliation.csv
WRITES  data/processed/overnight/24_exit_code_tests.csv

RUN     py -3.13 analysis/src/overnight/24_exit_code_tests.py
        exit 0 = every case returned the exit status it should have.

Needs Windows + desktop Excel (COM) for case 2 only; the other cases are pure Python.
"""
from __future__ import annotations

import csv
import os
import shutil
import subprocess
import sys
import tempfile

import pandas as pd
from openpyxl import load_workbook

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OD = os.path.join(ROOT, "data", "processed", "overnight")
PY = [sys.executable]

# the cell the negative control breaks: one of the 216 named outputs of 13_reconciliation.csv
TARGET_ITEM = "Bear 4Q27 ADR ($)"


def run(cmd, cwd=ROOT):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def first_failure_line(log):
    for line in log.splitlines():
        if line.startswith("FAIL:"):
            return line.strip()[:400]
    for line in log.splitlines():
        if line.startswith("PASS:"):
            return line.strip()[:400]
    return log.strip().splitlines()[-1][:400] if log.strip() else ""


def main():
    rows = []
    tmp = tempfile.mkdtemp(prefix="ws24_exit_")

    def record(case, script, expected, rc, log, detail):
        ok = rc == expected
        rows.append(dict(case=case, script=script, expected_exit=expected, actual_exit=rc,
                         result="PASS" if ok else "FAIL", detail=detail,
                         report_line=first_failure_line(log)))
        print(f"[{'PASS' if ok else 'FAIL'}] {case}: expected exit {expected}, got {rc}")
        print(f"        {first_failure_line(log)}")
        return ok

    # ---------------------------------------------------------------- 1. clean workbook passes
    rc, log = run(PY + [os.path.join(HERE, "17_excel_audit.py")])
    record("clean workbook reconciles", "17_excel_audit.py", 0, rc, log,
           "the shipped workbook, dump and reconciliation, unmodified")

    # ------------------------------------------- 2. a required output altered -> failing status
    recon = pd.read_csv(os.path.join(OD, "13_reconciliation.csv"))
    row = recon[recon.item == TARGET_ITEM].iloc[0]
    sheet, coord = row.cell_reference.split("!")
    coord = coord.replace("$", "")
    good = float(row.python_value)
    bad = round(good * 1.02, 4)                     # 2% wrong: far outside any tolerance

    broken_xlsx = os.path.join(tmp, "ABNB_driver_model_BROKEN.xlsx")
    shutil.copyfile(os.path.join(ROOT, "model", "ABNB_driver_model.xlsx"), broken_xlsx)
    wb = load_workbook(broken_xlsx)
    wb[sheet][coord] = bad                          # replace the formula with a wrong constant
    wb.save(broken_xlsx)

    broken_dump = os.path.join(tmp, "17_excel_recalc_dump.csv")
    ps = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
          os.path.join(HERE, "17_recalc_dump.ps1"), "-InPath", broken_xlsx,
          "-OutCsv", broken_dump]
    rc_ps, log_ps = run(ps)
    if rc_ps != 0 or not os.path.exists(broken_dump):
        print("Excel COM recalculation of the broken copy failed; cannot run case 2")
        rows.append(dict(case="altered required output is detected", script="17_excel_audit.py",
                         expected_exit=1, actual_exit="", result="SKIPPED",
                         detail="Excel COM unavailable: " + log_ps.strip()[:200], report_line=""))
    else:
        shutil.copyfile(os.path.join(OD, "13_reconciliation.csv"),
                        os.path.join(tmp, "13_reconciliation.csv"))
        rc, log = run(PY + [os.path.join(HERE, "17_excel_audit.py"),
                            "--workbook", broken_xlsx, "--dump", broken_dump,
                            "--out-dir", tmp])
        record("altered required output is detected", "17_excel_audit.py", 1, rc, log,
               f"{row.cell_reference} ({TARGET_ITEM}) forced from {good} to {bad} in a scratch "
               f"copy, recalculated by Excel via 17_recalc_dump.ps1")
        # the report has to name the cell, not just count failures
        vs = pd.read_csv(os.path.join(tmp, "17_excel_vs_python.csv"))
        hit = vs[vs["pass"] == "no"]
        named = TARGET_ITEM in set(hit.output)
        rows.append(dict(case="the failure report names the altered output",
                         script="17_excel_audit.py", expected_exit="report", actual_exit="report",
                         result="PASS" if named else "FAIL",
                         detail=f"{len(hit)} of {len(vs)} named outputs flagged; "
                                f"'{TARGET_ITEM}' among them: {named}",
                         report_line="; ".join(sorted(hit.output)[:4])))
        print(f"[{'PASS' if named else 'FAIL'}] the failure report names the altered output "
              f"({len(hit)} of {len(vs)} outputs flagged)")

    # --------------------------------------------------- 3. a missing required input -> exit 2
    rc, log = run(PY + [os.path.join(HERE, "17_excel_audit.py"),
                        "--dump", os.path.join(tmp, "does_not_exist.csv"), "--out-dir", tmp])
    record("missing Excel dump is not a silent pass", "17_excel_audit.py", 2, rc, log,
           "a required input path that does not exist")

    # ---------------------------------------------------------- 4. clean scenario switch passes
    rc, log = run(PY + [os.path.join(HERE, "17_scenario_switch.py")])
    record("clean scenario selector passes", "17_scenario_switch.py", 0, rc, log,
           "the three shipped dumps in data/processed/overnight")

    # ---------------------------------- 5. an inert selector (the original WS17 defect) -> exit 1
    inert = os.path.join(tmp, "inert")
    os.makedirs(inert, exist_ok=True)
    for n in ("17_dump_after_scen1.csv", "17_dump_after_scen3.csv"):
        # a selector that moves nothing looks exactly like the base dump
        shutil.copyfile(os.path.join(OD, "17_excel_recalc_dump.csv"), os.path.join(inert, n))
    rc, log = run(PY + [os.path.join(HERE, "17_scenario_switch.py"), "--dump-dir", inert])
    record("inert scenario selector is detected", "17_scenario_switch.py", 1, rc, log,
           "Bear and Bull dumps replaced by copies of the Base dump, i.e. a selector that "
           "moves 0 cells - the original WS17 defect")

    # -------------------------------------------------- 6. missing scenario dumps -> exit 2
    rc, log = run(PY + [os.path.join(HERE, "17_scenario_switch.py"),
                        "--dump-dir", os.path.join(tmp, "nowhere")])
    record("missing scenario dumps are not a silent pass", "17_scenario_switch.py", 2, rc, log,
           "a dump directory that does not exist")

    out = os.path.join(OD, "24_exit_code_tests.csv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["case", "script", "expected_exit", "actual_exit",
                                           "result", "detail", "report_line"])
        w.writeheader()
        w.writerows(rows)
    nfail = sum(1 for r in rows if r["result"] == "FAIL")
    print(f"\n{len(rows) - nfail}/{len(rows)} cases as expected -> {out}")
    shutil.rmtree(tmp, ignore_errors=True)
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
