"""Run the unchanged frozen scorer in a disposable, byte-identical input copy.

python analysis/src/forecast_methods/lane1_control_v2/run.py --stage after-a
Outputs a NEW stage folder; refuses to overwrite an existing checkpoint.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True)
    args = parser.parse_args()
    if not args.stage.replace("-", "").replace("_", "").isalnum():
        parser.error("stage must contain letters, digits, hyphens or underscores")
    out = ROOT / "data/processed/forecast_methods/lane1_control_v2" / args.stage
    if out.exists():
        raise FileExistsError(f"Checkpoint exists: {out}; select a new stage name")
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    prefixes = ("analysis/src/forecast_methods/harness/", "data/processed/forecast_methods/harness/",
                "data/processed/forecast_methods/registry/", "data/processed/forecast_methods/L0/",
                "data/processed/overnight/")
    names = {n for n in tracked if n and n.startswith(prefixes)}
    # Include new method registrations, never other untracked user files.
    registry = ROOT / "data/processed/forecast_methods/registry"
    names.update(p.relative_to(ROOT).as_posix() for p in registry.glob("*.csv"))
    before = {n:digest(ROOT/n) for n in sorted(names)}
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="lane1-scorer-") as directory:
        copy = Path(directory)
        for n in sorted(names):
            dest = copy/n
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT/n, dest)
        for n, expected in before.items():
            if digest(copy/n) != expected:
                raise RuntimeError(f"Copy differs: {n}")
        env = dict(os.environ, PYTHONUTF8="1")
        command = [sys.executable, "-X", "utf8", "analysis/src/forecast_methods/harness/score.py"]
        result = subprocess.run(command, cwd=copy, env=env, text=True, encoding="utf-8",
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
        if any(digest(ROOT/n) != h for n,h in before.items()):
            raise RuntimeError("An input changed while scoring; do not accept this checkpoint")
        out.mkdir(parents=True)
        (out/"score_output.txt").write_text(result.stdout, encoding="utf-8")
        for filename in ("scoreboard.csv", "scoreboard.md", "conformal_attainable_grid.csv"):
            source = copy/"data/processed/forecast_methods/harness"/filename
            if source.exists():
                shutil.copy2(source, out/filename)
    receipt = dict(stage=args.stage, command=command[3:], exit_code=result.returncode,
                   run_seconds=time.perf_counter()-started, input_sha256=before,
                   frozen_sources_unchanged=True, output_policy="new folder only")
    (out/"receipt.json").write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
    print(result.stdout)
    print(f"Receipt: {out.relative_to(ROOT).as_posix()}/receipt.json")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
