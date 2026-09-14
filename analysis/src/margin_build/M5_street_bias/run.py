"""Rebuild M5 (street-bias) end to end. Interpreter: py -3.13.

    py -3.13 analysis/src/margin_build/M5_street_bias/run.py

Registers three objects through the margin harness, writes every table under
data/processed/margin_build/M5_street_bias/ and three figures, then prints the
scorer command. Exit code 0.
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def step(script):
    print(f"\n=== {script} ===", flush=True)
    r = subprocess.run([sys.executable, str(HERE / script)], cwd=str(REPO))
    if r.returncode != 0:
        raise SystemExit(f"{script} failed with {r.returncode}")


if __name__ == "__main__":
    step("build.py")
    step("analyse.py")
    step("figures.py")
    print("\nNow rescore:  py -3.13 analysis/src/margin_build/10_harness_margin/score.py")
