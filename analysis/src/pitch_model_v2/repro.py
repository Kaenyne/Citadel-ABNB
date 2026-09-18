"""Run a reproduction command without dirtying the tree, and write a receipt.

Usage:
  python3 analysis/src/pitch_model_v2/repro.py --id D1 \
      --watch data/processed/forecast_methods/kernel_lambda \
      --cmd "python3 analysis/src/forecast_methods/kernel_lambda/run.py"
"""
from __future__ import annotations
import argparse, io, json, os, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

RECEIPTS = Path("data/processed/pitch_model_v2/receipts")

def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True).stdout

def _tracked(root: Path, watch: list[str]) -> set[str]:
    out = _git(root, "ls-files", "--", *watch)
    return set(l for l in out.splitlines() if l)

def _all_files(root: Path, watch: list[str]) -> set[str]:
    found = set()
    for w in watch:
        p = root / w
        if p.is_file():
            found.add(w)
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file():
                    found.add(str(f.relative_to(root)))
    return found

def _csv_diff(root: Path, path: str) -> tuple[dict, pd.DataFrame | None]:
    head_txt = _git(root, "show", f"HEAD:{path}")
    try:
        a = pd.read_csv(io.StringIO(head_txt)); b = pd.read_csv(root / path)
    except Exception as e:  # not a parseable CSV
        return {"kind": "text", "max_abs_diff": None, "rows_head": None, "rows_new": None,
                "cols_added": [], "cols_removed": [], "note": f"not parsed: {e}"}, None
    num = [c for c in a.columns if c in b.columns and pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c])]
    n = min(len(a), len(b))
    mad = 0.0; rows = []
    for c in num:
        d = (b[c].iloc[:n].astype(float).to_numpy() - a[c].iloc[:n].astype(float).to_numpy())
        d = pd.Series(d).abs().fillna(0.0)
        if len(d):
            mad = max(mad, float(d.max()))
            for i in d[d > 0].index[:200]:
                rows.append({"row": int(i), "col": c, "head": float(a[c].iloc[i]), "new": float(b[c].iloc[i]), "diff": float(d[i])})
    info = {"kind": "csv", "max_abs_diff": mad, "rows_head": int(len(a)), "rows_new": int(len(b)),
            "cols_added": [c for c in b.columns if c not in a.columns],
            "cols_removed": [c for c in a.columns if c not in b.columns]}
    return info, (pd.DataFrame(rows) if rows else None)

def run(id: str, cmd: str, watch: list[str], timeout: int = 1800, restore: bool = True, root: str | Path | None = None) -> dict:
    root = Path(root or Path.cwd()).resolve()
    for extra in ("data/processed/forecast_methods/registry", "data/processed/margin_build/10_harness_margin"):
        if (root / extra).is_dir() and extra not in watch:
            watch = [*watch, extra]
    rdir = root / RECEIPTS / id; (rdir / "diffs").mkdir(parents=True, exist_ok=True)
    tracked = _tracked(root, watch)
    before = _all_files(root, watch)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    t0 = time.time()
    proc = subprocess.run(cmd, shell=True, cwd=root, capture_output=True, text=True, timeout=timeout)
    wall = round(time.time() - t0, 1)
    (rdir / "stdout.txt").write_text(proc.stdout); (rdir / "stderr.txt").write_text(proc.stderr)
    after = _all_files(root, watch)
    modified = [l for l in _git(root, "status", "--porcelain", "--", *watch).splitlines() if l[:2].strip() in ("M", "MM", "AM")]
    changed_paths = sorted(l[3:] for l in modified if l[3:] in tracked)
    changed = []
    for p in changed_paths:
        info, rows = _csv_diff(root, p) if p.endswith(".csv") else ({"kind": "binary_or_text", "max_abs_diff": None, "rows_head": None, "rows_new": None, "cols_added": [], "cols_removed": []}, None)
        info["path"] = p; changed.append(info)
        if rows is not None:
            rows.to_csv(rdir / "diffs" / Path(p).name, index=False)
    new_files = sorted(after - before)
    restored = False
    if restore:
        if changed_paths:
            subprocess.run(["git", "checkout", "--", *changed_paths], cwd=root, check=True)
        for nf in new_files:
            (root / nf).unlink(missing_ok=True)
        restored = True
    rec = {"id": id, "commit": _git(root, "rev-parse", "HEAD").strip(), "cmd": cmd, "cwd": str(root), "started": started,
           "exit_code": proc.returncode, "wall_s": wall, "watch": watch, "changed": changed, "new_files": new_files,
           "restored": restored, "interpreter": sys.executable}
    (rdir / "receipt.json").write_text(json.dumps(rec, indent=2))
    return rec

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True); ap.add_argument("--cmd", required=True)
    ap.add_argument("--watch", action="append", required=True); ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--no-restore", action="store_true")
    a = ap.parse_args(argv)
    rec = run(a.id, a.cmd, a.watch, a.timeout, restore=not a.no_restore)
    print(json.dumps({k: rec[k] for k in ("id", "exit_code", "wall_s", "restored")}))
    print("changed:", [(c["path"], c.get("max_abs_diff")) for c in rec["changed"]])
    print("new_files:", rec["new_files"])
    return 0 if rec["exit_code"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
