"""S03 wrapper: re-runs the shared seeded mixture and blend from the S02 folder and copies the S03 outputs here.
Run from the repo root: py -3.13 docs/pitch-forecasts/questions/close-12feb-2027/datasets/run.py"""
import pathlib, shutil, subprocess, sys
here = pathlib.Path(__file__).resolve().parent
s02 = here.parent.parent / "close-15dec-2026" / "datasets"
for f in ("abnb_path_mixture.py", "final_blend.py"):
    subprocess.run([sys.executable, str(s02 / f)], check=True)
for f in ("mixture_base_run.json", "sensitivity.csv", "final_blend.json", "S03_hist.csv", "S03_final_cdf.csv"):
    shutil.copy(s02 / f, here / f)
print("copied S03 outputs to", here)
