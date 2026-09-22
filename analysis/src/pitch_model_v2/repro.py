"""Run a reproduction command without dirtying the tree, and write a receipt.

Usage:
  python3 analysis/src/pitch_model_v2/repro.py --id D1 \
      --watch data/processed/forecast_methods/kernel_lambda \
      --cmd "python3 analysis/src/forecast_methods/kernel_lambda/run.py"

Per-file row-level diffs are written to diffs/<path-with-"/"-replaced-by-"__">
(not just the basename), so two changed files that share a basename in
different watched directories never collide.
"""
from __future__ import annotations
import argparse, io, json, os, signal, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

RECEIPTS = Path("data/processed/pitch_model_v2/receipts")

def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True).stdout

def _tracked(root: Path, watch: list[str]) -> set[str]:
    # -z avoids git's default C-style quoting of non-ASCII/space paths, so
    # this matches the raw paths _changed_paths() also gets via `-z`.
    out = _git(root, "ls-files", "-z", "--", *watch)
    return set(p for p in out.split("\0") if p)

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

def _changed_paths(root: Path, watch: list[str], tracked: set[str]) -> tuple[list[str], set[str]]:
    """Which watched paths did the command touch, and which of those git can
    `checkout` back from HEAD.

    Uses `git status --porcelain -z` (NUL-separated, no C-style quoting of
    filenames) so names with spaces or non-ASCII characters parse correctly,
    and treats any tracked path with a non-"??" status as changed -- not just
    ("M", "MM", "AM") -- so a deletion (" D") is not silently dropped. Rename
    records ("R"/"C") carry a second NUL-separated field (the old path); both
    the old and new path are treated as changed.
    """
    raw = subprocess.run(
        ["git", "status", "--porcelain", "-z", "--untracked-files=all", "--", *watch],
        cwd=root, capture_output=True, text=True,
    ).stdout
    tokens = raw.split("\0")
    changed: set[str] = set()
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        i += 1
        if not tok:
            continue
        code, path = tok[:2], tok[3:]
        is_rename = ("R" in code) or ("C" in code)
        old_path = None
        if is_rename and i < len(tokens):
            old_path = tokens[i]
            i += 1
        if code == "??":
            continue
        if path in tracked or is_rename:
            changed.add(path)
        if old_path and old_path in tracked:
            changed.add(old_path)
    checkoutable = {p for p in changed if p in tracked}
    return sorted(changed), checkoutable

def _csv_diff(root: Path, path: str) -> tuple[dict, pd.DataFrame | None]:
    head_txt = _git(root, "show", f"HEAD:{path}")
    try:
        a = pd.read_csv(io.StringIO(head_txt)); b = pd.read_csv(root / path)
    except Exception as e:  # not a parseable CSV
        return {"kind": "text", "max_abs_diff": None, "rows_head": None, "rows_new": None,
                "cols_added": [], "cols_removed": [], "note": f"not parsed: {e}"}, None
    num = [c for c in a.columns if c in b.columns and pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c])]
    n = min(len(a), len(b))
    mad = 0.0
    nan_change = False
    rows = []
    for c in num:
        av = a[c].iloc[:n].astype(float)
        bv = b[c].iloc[:n].astype(float)
        a_na = av.isna(); b_na = bv.isna()
        mismatch_na = a_na != b_na
        both_na = a_na & b_na
        d = (bv - av).abs().mask(both_na, 0.0)
        for i in d.index:
            if mismatch_na.loc[i]:
                nan_change = True
                rows.append({"row": int(i), "col": c,
                             "head": (None if a_na.loc[i] else float(av.loc[i])),
                             "new": (None if b_na.loc[i] else float(bv.loc[i])),
                             "diff": "nan_change"})
            else:
                di = d.loc[i]
                if pd.notna(di) and di > 0:
                    mad = max(mad, float(di))
                    rows.append({"row": int(i), "col": c, "head": float(av.loc[i]), "new": float(bv.loc[i]), "diff": float(di)})
    rows = rows[:200]  # cap per file (across all columns), not per column
    if nan_change:
        mad = float("inf")  # a number<->NaN change can never count as "matches"
    info = {"kind": "csv", "max_abs_diff": mad, "rows_head": int(len(a)), "rows_new": int(len(b)),
            "cols_added": [c for c in b.columns if c not in a.columns],
            "cols_removed": [c for c in a.columns if c not in b.columns]}
    return info, (pd.DataFrame(rows) if rows else None)

def _run_cmd(cmd: str, root: Path, timeout: int) -> tuple[int, str, str]:
    """Run `cmd` in its own process group so a timeout can kill the whole
    tree (shell=True only kills the shell itself, not its children)."""
    proc = subprocess.Popen(
        cmd, shell=True, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, start_new_session=True,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return proc.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        stdout, stderr = proc.communicate()
        stderr = (stderr or "") + f"\ntimed out after {timeout}s"
        return 124, stdout or "", stderr

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
    exit_code, stdout, stderr = _run_cmd(cmd, root, timeout)
    wall = round(time.time() - t0, 1)
    (rdir / "stdout.txt").write_text(stdout)
    stderr_path = rdir / "stderr.txt"
    stderr_path.write_text(stderr)

    changed: list[dict] = []
    new_files: list[str] = []
    restored = False
    try:
        after = _all_files(root, watch)
        changed_paths, checkoutable = _changed_paths(root, watch, tracked)
        for p in changed_paths:
            if not (root / p).exists():
                info, rows = {"kind": "deleted", "max_abs_diff": None, "rows_head": None,
                              "rows_new": None, "cols_added": [], "cols_removed": []}, None
            elif p.endswith(".csv"):
                info, rows = _csv_diff(root, p)
            else:
                info, rows = ({"kind": "binary_or_text", "max_abs_diff": None, "rows_head": None,
                               "rows_new": None, "cols_added": [], "cols_removed": []}, None)
            info["path"] = p; changed.append(info)
            if rows is not None:
                rows.to_csv(rdir / "diffs" / p.replace("/", "__"), index=False)
        new_files = sorted(after - before)
        if restore:
            try:
                if checkoutable:
                    subprocess.run(["git", "checkout", "--", *sorted(checkoutable)], cwd=root,
                                    check=True, capture_output=True, text=True)
                for p in changed_paths:
                    if p not in checkoutable:
                        (root / p).unlink(missing_ok=True)
                for nf in new_files:
                    (root / nf).unlink(missing_ok=True)
                restored = True
            except subprocess.CalledProcessError as e:
                restored = False
                with stderr_path.open("a") as f:
                    f.write(f"\nrestore failed: git checkout error: {e.stderr}\n")
    finally:
        rec = {"id": id, "commit": _git(root, "rev-parse", "HEAD").strip(), "cmd": cmd, "cwd": str(root), "started": started,
               "exit_code": exit_code, "wall_s": wall, "watch": watch, "changed": changed, "new_files": new_files,
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
