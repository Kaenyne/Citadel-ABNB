"""WS20 scoreboard: rebuild every scoreboard product end to end.

    py -3.13 analysis/src/margin_build/20_scoreboard/run.py

Reads the margin harness outputs (data/processed/margin_build/10_harness_margin/) and the
registry (data/processed/margin_build/registry/); writes to
data/processed/margin_build/20_scoreboard/. It does NOT re-run score.py or any method run.py
(WS20 is an overseer, it compares, it does not rebuild); run those first if the registry has
changed:

    py -3.13 analysis/src/margin_build/10_harness_margin/score.py
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = ["build_master.py", "build_rankings.py", "build_live.py", "build_correlations.py",
         "build_combination.py", "build_parameter_budget.py", "build_line_vs_margin.py",
         "build_digest.py"]


def main():
    for s in STEPS:
        print(f"=== {s}", flush=True)
        r = subprocess.run([sys.executable, str(HERE / s)])
        if r.returncode != 0:
            print(f"FAILED: {s} exit {r.returncode}")
            return r.returncode
    print("WS20 scoreboard rebuilt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
