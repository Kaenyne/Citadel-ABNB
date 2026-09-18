"""S04 revision-2 wrapper: re-runs the shared v2 mixture (tape block included) from the S02 folder, copies the
outputs here, and recomputes the revision-2 base rates (exact thresholds, -36/+26 windows, hybrid residual).
Run from the repo root: py -3.13 docs/pitch-forecasts/questions/sellside-mean-target-cut-by-15dec/datasets/run_v2.py"""
import pathlib, shutil, subprocess, sys
here = pathlib.Path(__file__).resolve().parent
s02 = here.parent.parent / "close-15dec-2026" / "datasets"
subprocess.run([sys.executable, str(s02 / "abnb_path_mixture_v2.py")], check=True)
for f in ("mixture_base_run_v2.json", "sensitivity_v2.csv"):
    shutil.copy(s02 / f, here / f)
subprocess.run([sys.executable, str(here / "target_base_rates_v2.py")], check=True)
print("copied S04 v2 outputs to", here)
