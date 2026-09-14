#!/usr/bin/env python
"""WS21 red team: run every reproducible check and write the findings table.

    cd "C:\\Users\\krish\\citadel-abnb-margins"
    py -3.13 analysis/src/margin_build/21_red_team/run.py                  # all checks, ~3 min, exit 0
    py -3.13 analysis/src/margin_build/21_red_team/run.py --snapshot DIR   # score a snapshot of data/processed/margin_build

Each check is a standalone script under `checks/` and can be run on its own; this driver runs them in
order, captures their output to `data/processed/margin_build/21_red_team/21_check_output.txt`, and
records a one-line verdict per check in `21_check_index.csv`. It writes nothing outside
`data/processed/margin_build/21_red_team/`. It does NOT fix anything and does not touch the registry.

The replay of every other package's `run.py` (the reproducibility evidence in 21_reproducibility.csv)
is a separate, slower step; the command used is recorded in the note and in that CSV's `command` column.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OUT = REPO / "data" / "processed" / "margin_build" / "21_red_team"

CHECKS = [
    ("check_01_registry_pit_rules.py", "mechanical PIT rules over every registry file"),
    ("check_02_skill_significance.py", "paired-loss significance of every margin survivor"),
    ("check_03_sentence_rule_information.py", "information in M2's sentence rule; where M3's pin win comes from"),
    ("check_04_killlist_and_licence.py", "kill-list phrases, banned language, licensed-data exposure"),
    ("check_05_live_coherence.py", "economic sense of the LIVE margin paths"),
    ("check_06_lines_vs_margin_and_coverage.py", "line claims re-scored on the margin; interval calibration"),
    ("check_07_survivor_placebo.py", "sign-flip null for survives_both_windows"),
    ("check_08_reproducibility_inputs.py", "can each run.py rebuild from a clean checkout"),
    ("check_09_m1_step_dummy_leak.py", "M1 d_steps_rw step dummies are not gated by knowable_from"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", default=None,
                    help="a copy of data/processed/margin_build to score instead of the live one")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    log, index = [], []
    for name, what in CHECKS:
        p = HERE / "checks" / name
        cmd = [sys.executable, str(p)]
        if a.snapshot and name not in ("check_04_killlist_and_licence.py",
                                       "check_08_reproducibility_inputs.py",
                                       "check_09_m1_step_dummy_leak.py"):
            cmd.append(str(Path(a.snapshot) / "registry") if name == "check_01_registry_pit_rules.py"
                       else str(a.snapshot))
        t0 = time.time()
        r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
        secs = time.time() - t0
        head = f"\n{'=' * 100}\n{name}  --  {what}\n{'=' * 100}\n"
        log.append(head + r.stdout + (("\nSTDERR:\n" + r.stderr) if r.returncode else ""))
        index.append(f"{name},{r.returncode},{secs:.1f},\"{what}\"")
        print(f"{name:46s} exit={r.returncode} {secs:6.1f}s  {what}")
    (OUT / "21_check_output.txt").write_text("\n".join(log), encoding="utf-8")
    (OUT / "21_check_index.csv").write_text("check,exit_code,seconds,what\n" + "\n".join(index) + "\n",
                                            encoding="utf-8")
    print(f"\noutput -> {(OUT / '21_check_output.txt').relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
