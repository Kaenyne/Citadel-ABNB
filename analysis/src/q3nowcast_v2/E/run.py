"""
WP-K reviews index 2023 vintage: rebuild the package end to end. Exit code 0 on success.

Steps (each a separate script in this folder, run in order):
  V1_download_vintage2023.py       pull the 114 usable HF mirror files (resumable; --verify-only re-checks
                                   gzip integrity and rewrites the manifest without downloading)
  V2_review_counts_two_folders.py  E3 logic on the held store + the 2023 store, v1 caches copied
  V3_build_index.py                E4 copy on the v2 folder (wedges incl. 2023 pairs; index unchanged)
  V4_tests_T1_T2.py                pre-registered T1 and T2
  V5_nyc_ll18_bracket.py           NYC LL18 bracket and T3
Run from the worktree root: python analysis/src/q3nowcast_v2/E/run.py [--skip-download] [--workers 3]
"""
import argparse, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
WT = HERE.parents[3]


def run(script, *args):
    t0 = time.time()
    cmd = [sys.executable, "-X", "utf8", str(HERE / script), *args]
    print(f"== {script} {' '.join(args)}", flush=True)
    rc = subprocess.run(cmd, cwd=WT).returncode
    print(f"== {script} exit {rc} in {time.time() - t0:.0f}s", flush=True)
    if rc != 0:
        sys.exit(rc)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-download", action="store_true", help="only re-verify the raw store and rewrite the manifest")
    ap.add_argument("--workers", default="3")
    a = ap.parse_args()
    run("V1_download_vintage2023.py", *(["--verify-only"] if a.skip_download else []))
    run("V2_review_counts_two_folders.py", "--workers", a.workers)
    run("V3_build_index.py")
    run("V4_tests_T1_T2.py")
    run("V5_nyc_ll18_bracket.py")
    import pandas as pd
    t1 = pd.read_csv(WT / "data/processed/q3nowcast_v2/E/t1_wedge_constancy.csv")
    if not bool(t1.overall_pass.iloc[0]):
        print("T1 failed its pre-registered line: running the E5 substitution re-run (V6)", flush=True)
        run("V6_backtest_substituted.py")
    print("run.py complete, exit 0")
