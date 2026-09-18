"""S04 wrapper: re-runs the shared seeded mixture (tape-lag block included) from the S02 folder and copies
the S04 outputs here; also recomputes the target base rates (target_base_rates.py).
Run from the repo root: py -3.13 docs/pitch-forecasts/questions/sellside-mean-target-cut-by-15dec/datasets/run.py"""
import pathlib, shutil, subprocess, sys
here = pathlib.Path(__file__).resolve().parent
s02 = here.parent.parent / "close-15dec-2026" / "datasets"
subprocess.run([sys.executable, str(s02 / "abnb_path_mixture.py")], check=True)
for f in ("mixture_base_run.json", "sensitivity.csv"):
    shutil.copy(s02 / f, here / f)
subprocess.run([sys.executable, str(here / "target_base_rates.py")], check=True)
print("copied S04 outputs to", here)
