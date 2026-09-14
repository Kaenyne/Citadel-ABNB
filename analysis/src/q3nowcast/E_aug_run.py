"""
Q3 2026 nowcast, workstream E, August-batch refresh: run the committed E pipeline (E3 counting, E4
index, E4b stable listing, E5 backtest, E6 nowcast, E7 report) unchanged, but with every output path
redirected from data/processed/q3nowcast/E to data/processed/q3nowcast/E_aug, so the committed E
outputs are not overwritten and the two runs can be diffed.

How: each script's source is read, the single string "data/processed/q3nowcast/E" is replaced with
"data/processed/q3nowcast/E_aug", and the result is executed as __main__ with the original __file__
(so WT / MAIN resolve the same way). Nothing else in the scripts changes. E3 runs single-process
(its per-file cache in E_aug/cache/ is a copy of the q3nowcast worktree cache plus the new files).

Run: py -3.13 analysis/src/q3nowcast/E_aug_run.py --steps E1,E3,E4,E4b,E5,E6,E7
     E1 is run with --skip-probe (local inventory only; the CDN probe is E_aug1_probe.py).
     E3 accepts the same flags as E3_review_counts.py through --e3-args, e.g. --e3-args "--only 2026-08".
"""
import argparse, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = {"E1": "E1_inventory_and_discover.py", "E3": "E3_review_counts.py", "E4": "E4_build_index.py", "E4b": "E4b_stable_listing.py",
           "E5": "E5_backtest.py", "E6": "E6_nowcast.py", "E7": "E7_report.py"}
OLD, NEW = '"data/processed/q3nowcast/E"', '"data/processed/q3nowcast/E_aug"'
# E7 section 2 reads the download bookkeeping; in E_aug those files carry the _aug2026 suffix
E7_EXTRA = {'"download_manifest.csv"': '"download_manifest_aug2026.csv"',
            '"download_gaps.csv"': '"download_gaps_aug2026.csv"',
            '"download_plan.csv"': '"download_plan_aug2026.csv"'}


def log(m):
    print(f"{time.strftime('%H:%M:%S')} [E_aug_run] {m}", flush=True)


def run(step, argv):
    p = HERE / SCRIPTS[step]
    src = p.read_text(encoding="utf-8")
    n = src.count(OLD)
    if n == 0:
        raise SystemExit(f"{p.name}: output path string not found, refusing to run")
    src = src.replace(OLD, NEW)
    if step == "E7":
        for k, v in E7_EXTRA.items():
            src = src.replace(k, v)
    log(f"{p.name}: {n} output-path replacement(s), argv {argv}")
    sys.argv = [str(p)] + argv
    g = {"__name__": "__main__", "__file__": str(p), "__builtins__": __builtins__}
    t0 = time.time()
    exec(compile(src, str(p), "exec"), g)
    log(f"{p.name} done in {(time.time() - t0) / 60:.1f} min")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", default="E3,E4,E4b,E5,E6,E7")
    ap.add_argument("--e3-args", default="")
    a = ap.parse_args()
    for s in a.steps.split(","):
        s = s.strip()
        argv = a.e3_args.split() if (s == "E3" and a.e3_args) else []
        if s == "E1":
            argv = ["--skip-probe"]
        run(s, argv)
