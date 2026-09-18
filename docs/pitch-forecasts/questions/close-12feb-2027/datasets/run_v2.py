"""S03 revision-2 wrapper: re-runs the shared v2 anchor, mixture and blend from the S02 folder, the measured
15 Dec -> pre-release window here, and copies the S03 v2 outputs here.
Run from the repo root: py -3.13 docs/pitch-forecasts/questions/close-12feb-2027/datasets/run_v2.py"""
import pathlib, shutil, subprocess, sys
here = pathlib.Path(__file__).resolve().parent
s02 = here.parent.parent / "close-15dec-2026" / "datasets"
subprocess.run([sys.executable, str(here / "dec_to_prerelease_window.py")], check=True)
for f in ("implied_dist_v2.py", "abnb_path_mixture_v2.py", "final_blend_v2.py"):
    subprocess.run([sys.executable, str(s02 / f)], check=True)
for f in ("implied_dist_v2.json", "anchor_cdf_v2.csv", "mixture_base_run_v2.json", "sensitivity_v2.csv", "final_blend_v2.json", "S03_hist_v2.csv", "S03_final_cdf_v2.csv"):
    shutil.copy(s02 / f, here / f)
print("copied S03 v2 outputs to", here)
