"""WS03 03_consensus_pit: rebuild end to end.

    python analysis/src/margin_build/03_consensus_pit/run.py

1. Pull raw LSEG history with `py -3.13` (lseg-data) -- SKIPPED when the raw folder already holds the
   35 pull files (licensed, gitignored). Needs the Workspace desktop open and LSEG_APP_KEY in the env.
2. Build every derived table with the interpreter running this script (venv pandas 3 or py -3.13).
3. Figures with `py -3.13` (matplotlib); a missing matplotlib is reported, not fatal.
Exit code 0 when the build succeeds.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
RAW = REPO / "data" / "raw" / "margin_build" / "03_consensus_pit"
N_EXPECTED_RAW = 35


def py313() -> list[str] | None:
    if shutil.which("py"):
        return ["py", "-3.13"]
    return None


def main() -> int:
    have = len(list(RAW.glob("*_D.csv"))) + len(list(RAW.glob("*_M.csv"))) if RAW.exists() else 0
    if have >= N_EXPECTED_RAW:
        print(f"[pull] skipped: {have} raw files present in {RAW}")
    else:
        launcher = py313()
        if launcher is None:
            print("[pull] py -3.13 launcher not found and raw files missing; cannot pull", file=sys.stderr)
            return 2
        print(f"[pull] {have}/{N_EXPECTED_RAW} raw files present; pulling the rest via py -3.13")
        rc = subprocess.call(launcher + [str(HERE / "pull_lseg.py")], cwd=str(REPO))
        if rc != 0:
            print(f"[pull] failed with exit code {rc}", file=sys.stderr)
            return rc
    print("[build] deriving tables")
    rc = subprocess.call([sys.executable, str(HERE / "build.py")], cwd=str(REPO))
    if rc != 0:
        return rc
    launcher = py313()
    if launcher is not None:
        print("[figures] rendering with py -3.13")
        rc = subprocess.call(launcher + [str(HERE / "figures.py")], cwd=str(REPO))
        if rc != 0:
            print(f"[figures] failed (exit {rc}); tables are complete", file=sys.stderr)
    else:
        print("[figures] py -3.13 not found; skipped")
    print("[done] 03_consensus_pit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
