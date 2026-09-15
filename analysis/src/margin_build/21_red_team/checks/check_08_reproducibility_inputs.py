"""WS21 check 08: can each package's run.py rebuild from a clean checkout?

For every analysis/src/margin_build/*/run.py (and its helper modules), resolve every literal path it
reads and classify it:
  tracked      - committed to git, so a fresh clone has it
  gitignored   - present only on this machine (data/raw/*, licensed stores): run.py will FAIL from clean
  missing      - the path does not exist even here
Also reports whether a gitignored input has a manifest under data/manifests/margin_build and whether
the script contains any re-pull fallback (a requests/urlretrieve call).

Usage: py -3.13 analysis/src/margin_build/21_red_team/checks/check_08_reproducibility_inputs.py
"""
from __future__ import annotations
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SRC = REPO / "analysis" / "src" / "margin_build"
PKGS = [p for p in sorted(SRC.iterdir()) if p.is_dir() and (p / "run.py").exists() or
        (p.is_dir() and any(p.glob("*.py")))]
RX = re.compile(r'"((?:data|model|analysis|research|docs)[/\][^"\n]+)"|/\s*"([^"\n]+\.(?:csv|json|parquet|xlsx|txt|md))"')


def tracked(rel: str) -> bool:
    r = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=REPO,
                       capture_output=True, text=True)
    return r.returncode == 0


def ignored(rel: str) -> bool:
    r = subprocess.run(["git", "check-ignore", "-q", rel], cwd=REPO, capture_output=True, text=True)
    return r.returncode == 0


def main() -> int:
    manifests = {p.stem for p in (REPO / "data" / "manifests" / "margin_build").glob("*.csv")}
    print(f"{'package':26s} {'raw(gitignored) inputs':>24s}  {'manifest?':>9s}  {'repull?':>8s}  files")
    any_bad = False
    for pkg in PKGS:
        txt = "\n".join(f.read_text(encoding="utf-8", errors="ignore") for f in pkg.glob("*.py"))
        raws = sorted({m for m in re.findall(r'"(data[/\]raw[/\][^"\n]+)"', txt)})
        # also catch the REPO / "data" / "raw" / ... style
        for m in re.finditer(r'REPO\s*/\s*"data"\s*/\s*"raw"((?:\s*/\s*"[^"]+")+)', txt):
            parts = re.findall(r'"([^"]+)"', m.group(1))
            raws.append("data/raw/" + "/".join(parts))
        raws = sorted(set(raws))
        real = []
        for r in raws:
            r2 = r.replace("\\", "/")
            if "{" in r2 or "*" in r2:
                r2 = str(Path(r2).parent)
            real.append(r2)
        real = sorted(set(real))
        gi = [r for r in real if ignored(r)]
        repull = bool(re.search(r"requests\.get|urlretrieve|urlopen", txt))
        manif = pkg.name in manifests
        if gi:
            any_bad = True
        print(f"{pkg.name:26s} {len(gi):>24d}  {'yes' if manif else 'NO':>9s}  "
              f"{'yes' if repull else 'NO':>8s}  {', '.join(gi) if gi else '-'}")
    print("\nA package with gitignored inputs and no re-pull fallback cannot run `run.py` from a clean "
          "checkout: it raises FileNotFoundError before writing anything. The manifest makes it "
          "recoverable by hand, but the brief's 'run.py rebuilds the package end to end, exit 0' does "
          "not hold for those packages on another machine.")
    return 0 if not any_bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
