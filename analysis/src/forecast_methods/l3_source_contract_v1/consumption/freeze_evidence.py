"""One-time, bounded read-only evidence inventory. Rebuilds use its frozen outputs."""
from __future__ import annotations
import argparse
import ast
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[5]
L4_COMMIT = "29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70"
L3_COMMIT = "8821961853e4068febbfe2712f9a4e1036c9e629"
ORIGINAL = Path("C:/Users/wille/Desktop/Citadel - ABNB")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, stderr=subprocess.DEVNULL)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    stamp = datetime.now(timezone.utc).isoformat()
    paths = [
        "analysis/src/forecast_methods/lane4_revenue_v1/l3_contract.py",
        "analysis/src/forecast_methods/lane4_revenue_v1/adapter.py",
        "analysis/src/forecast_methods/lane4_revenue_v1/run.py",
        "analysis/src/forecast_methods/lane4_revenue_v1/README.md",
        "docs/revenue-forecast-strategy/05_backtests/L4_CLOSE_HANDOFF_v1.md",
        "docs/revenue-forecast-strategy/05_backtests/L4_REVENUE_RECONCILIATION_v1.md",
        "data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1/forecast.csv",
        "data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1/consensus_comparison.csv",
        "data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1/integration_status.json",
    ]
    ledger, bodies = [], {}
    for p in paths:
        data = git("show", f"{L4_COMMIT}:{p}")
        bodies[p] = data.decode("utf-8")
        work = ORIGINAL / ".worktrees/lane4-full" / p
        actual = sha(work.read_bytes()) if work.is_file() else None
        ledger.append(dict(commit=L4_COMMIT, path=p,
                           git_blob=git("rev-parse", f"{L4_COMMIT}:{p}").decode().strip(),
                           sha256=sha(data), bytes=len(data), working_sha256=actual,
                           working_bytes_equal_committed=actual == sha(data)))
    adapter_path = paths[1]
    parsed = ast.parse(bodies[adapter_path])
    functions = {n.name: ast.get_source_segment(bodies[adapter_path], n)
                 for n in parsed.body if isinstance(n, ast.FunctionDef)
                 and n.name in {"quarter", "shift", "number", "dated"}}
    snapshot = dict(audit_timestamp_utc=stamp, l4_commit=L4_COMMIT,
                    source_manifest=ledger,
                    contract_source=bodies[paths[0]], adapter_functions=functions,
                    integration_status=json.loads(bodies[paths[-1]]),
                    forecast_rows=list(csv.DictReader(bodies[paths[-3]].splitlines())),
                    consensus_comparison_rows=list(csv.DictReader(bodies[paths[-2]].splitlines())),
                    runner_consensus_excerpt="\n".join(bodies[paths[2]].splitlines()[236:246]),
                    assurance="Actual Git blobs verified. Working bytes compared but never consumed. Full source hashes bind compact extracts; offline rebuild verifies frozen snapshot hashes.")
    (out / "l4_interface_snapshot.json").write_text(json.dumps(snapshot, indent=2)+"\n", encoding="utf-8")

    inventory, scopes = [], []
    for label, root in [("original_workspace", ORIGINAL), ("l3_worktree", ROOT)]:
        for sub, pattern in [("data/processed/forecast_methods/fee_panels", "*"),
                             ("data/raw/regulatory/quantification", "abnb_*")]:
            directory = root / sub
            files = sorted(p for p in directory.rglob(pattern) if p.is_file())
            scopes.append(dict(workspace=label, absolute_directory=str(directory), pattern=pattern,
                               file_count=len(files), timestamp_utc=stamp))
            for file in files:
                rel = file.relative_to(root).as_posix()
                current = file.read_bytes()
                try:
                    baseline = git("show", f"{L3_COMMIT}:{rel}")
                    baseline_sha = sha(baseline)
                except subprocess.CalledProcessError:
                    baseline_sha = None
                    baseline = None
                content_equal = baseline is not None and current.replace(b"\r\n", b"\n") == baseline.replace(b"\r\n", b"\n")
                inventory.append(dict(workspace=label, path=rel, bytes=len(current),
                                      modification_timestamp_utc=datetime.fromtimestamp(file.stat().st_mtime, timezone.utc).isoformat(),
                                      sha256=sha(current), baseline_commit=L3_COMMIT,
                                      baseline_sha256=baseline_sha,
                                      new_or_changed_bytes=baseline_sha != sha(current),
                                      content_equal_after_CRLF_to_LF=content_equal,
                                      material_new_local_content=not content_equal,
                                      evidence_type="sanctioned_fee_capture_or_support" if "fee_panels" in sub else "existing_primary_disclosure_or_extraction",
                                      timestamp_is="filesystem modification time, not source publication time"))
    result = dict(audit_timestamp_utc=stamp, as_of="2026-09-14", scopes=scopes, files=inventory,
                  changed_files=[r for r in inventory if r["new_or_changed_bytes"]],
                  material_new_content_files=[r for r in inventory if r["material_new_local_content"]],
                  actual_capture_wave_files=[r for r in inventory if "/runs/" in r["path"] and r["path"].endswith(".csv")],
                  interpretation="Bounded local inventory only; no collection, monitor, waiting or broad public-web completeness claim. Dryrun is not a wave. Filesystem dates do not establish publication vintages. Existing later-filing precision is SC-A scope and does not reopen empirical tests.")
    (out / "existing_data_inventory.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")

    context = []
    for name in ["QVS_VARIANCE_AND_PRESENTATION_ARGUMENTS_v1.md", "QVS_GUIDE_BASIS_AND_DECISION_LOGIC_v1.md"]:
        file = ORIGINAL / "docs/revenue-forecast-strategy/05_backtests" / name
        data = file.read_bytes()
        rel = file.relative_to(ORIGINAL).as_posix()
        try:
            pinned = git("show", f"1c87628cedbc94ab8a0e8552743c94485ef353b8:{rel}")
            committed_match = data == pinned
        except subprocess.CalledProcessError:
            committed_match = False
        context.append(dict(path=str(file), sha256=sha(data), bytes=len(data),
                            matches_original_workspace_HEAD=committed_match,
                            role="Explanatory local context; conclusions checked against committed L4 interface and outputs."))
    (out / "qvs_context_manifest.json").write_text(json.dumps(context, indent=2)+"\n", encoding="utf-8")
    files = {p.name: sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()}
    (out / "manifest.json").write_text(json.dumps(dict(frozen_at_utc=stamp, files=files), indent=2)+"\n", encoding="utf-8")
    print(json.dumps(dict(out=str(out), timestamp=stamp, l4_sources=len(ledger), inventory_files=len(inventory), changed_files=len(result["changed_files"]), wave_files=len(result["actual_capture_wave_files"]))))


if __name__ == "__main__":
    main()
