"""Read-only sealed-payload audit and rerun of the existing 20 author tests."""
import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
P = "quant_thesis_validation_v1"
DATA = ROOT / "data/processed/forecast_methods" / P
DOCS = ROOT / "docs/revenue-forecast-strategy" / P
CODE = ROOT / "analysis/src/forecast_methods" / P
ANALYTICAL = "965166c4572fe7c6300c7281e77afc5877411820"
HANDOFF = "b1e8885a6c294e1b212f9b908a9ce5fbeb3c1ec4"
L3 = "8821961853e4068febbfe2712f9a4e1036c9e629"
SCOPES = [str(p.relative_to(ROOT)).replace("\\", "/") for p in (CODE, DATA, DOCS)] + ["docs/revenue-forecast-strategy/05_backtests/QUANT_THESIS_VALIDATION_v1.md"]


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def sha(p):
    absolute = str(p.resolve())
    if os.name == "nt":
        absolute = chr(92) * 2 + "?" + chr(92) + absolute
    with open(absolute, "rb") as handle:
        return digest(handle.read())


def js(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def git(*args, data=None):
    return subprocess.check_output(["git", *args], cwd=ROOT, input=data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    out = ap.parse_args().out.resolve()
    if out.exists() or not out.is_relative_to((DATA / "publication_audit_v1/technical_review").resolve()):
        raise ValueError("Fresh exclusive technical_review output required")
    out.mkdir(parents=True)
    manifest_path = DOCS / "handoff_v1/analytical_manifest.json"
    manifest = js(manifest_path)
    assert manifest["analytical_commit"] == ANALYTICAL
    assert sha(manifest_path) == "e2916691513dbafe3565c21e89205c7d9185b27045c836296902c1684052b30c"
    for ancestor, descendant in [(L3, ANALYTICAL), (ANALYTICAL, HANDOFF)]:
        subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, descendant], cwd=ROOT, check=True)
    tree = {}
    for item in git("ls-tree", "-rz", ANALYTICAL, "--", *SCOPES).split(b"\0"):
        if item:
            meta, path = item.split(b"\t", 1)
            mode, typ, obj = meta.decode().split()
            assert typ == "blob"
            tree[path.decode()] = (mode, obj)
    records = manifest["files"]
    assert len(records) == len(tree) == manifest["file_count"] == 623
    assert {r["path"] for r in records} == set(tree)
    raw = git("cat-file", "--batch", data=("\n".join(tree[r["path"]][1] for r in records) + "\n").encode())
    offset, identity = 0, []
    for r in records:
        end = raw.index(b"\n", offset)
        obj, typ, size = raw[offset:end].decode().split(); size = int(size)
        payload = raw[end + 1:end + 1 + size]; offset = end + size + 2
        assert typ == "blob" and (r["mode"], r["git_blob"]) == tree[r["path"]]
        assert obj == r["git_blob"] and size == r["bytes"]
        assert digest(payload) == r["sha256"] == sha(ROOT / r["path"])
        identity.append(dict(path=r["path"], sha256=digest(payload), bytes=size, passed=True))
    assert sum(r["bytes"] for r in identity) == manifest["total_bytes"] == 13362229
    for line in git("diff", "--name-status", L3, HANDOFF).decode().splitlines():
        action, path = line.split("\t", 1)
        assert action == "A" and any(path == s or path.startswith(s + "/") for s in SCOPES), line
    # Review integrity is verified independently; this does not approve the
    # reviewer's own earlier numerical implementation or renew visual signoff.
    receipts = [
        DATA / "final_contract_review_v1/final_receipt_v1/receipt.json",
        DATA / "final_contract_review_v1/postseal_v1/receipt.json",
        DATA / "adversarial_review_v1/final_prose_closure_v1/receipt.json",
        DATA / "adversarial_review_v1/results_v2/receipt.json",
        DATA / "independent_reproduction_v1/complete_run_v2/independent_completion_receipt.json",
        DATA / "independent_reproduction_v1/complete_run_v2/prospective_review/prospective_independent_receipt.json",
        DATA / "independent_reproduction_v1/complete_run_v2/source_review/source_independent_receipt.json",
    ]
    bindings = []
    for receipt_path in receipts:
        d = js(receipt_path)
        for key in ["bindings_sha256", "bindings", "bound_author_files_sha256", "reviewed_author_file_hashes"]:
            for p, expected in d.get(key, {}).items():
                path = DATA / "economics_v1/results_v2" / p if key == "reviewed_author_file_hashes" else ROOT / p.replace("\\", "/")
                assert path.is_file() and sha(path) == expected, (receipt_path, p)
                bindings.append(dict(receipt=str(receipt_path.relative_to(ROOT)), path=str(path.relative_to(ROOT)), sha256=expected, passed=True))
    acceptance = js(DOCS / "handoff_v1/ACCEPTANCE_FINAL.json")
    prior = acceptance["independent_final_review"]
    assert sha(ROOT / prior["path"]) == prior["sha256"]
    assert acceptance["analytical_commit"] == ANALYTICAL and acceptance["forecast_promotion"] == "FAIL"
    # Recompute protection/source hashes without invoking the parent checker.
    protection_counts = {}
    for name, field in [("protected_manifest", "path"), ("external_manifest", "frozen_path")]:
        rows = js(DATA / "evidence_v3" / (name + ".json"))
        for r in rows:
            assert sha(ROOT / r[field]) == r["sha256"], r[field]
        protection_counts[name] = len(rows)
    # Bind existing successful full execution, without redoing own G calculations.
    full_run_path = DATA / "reproductions/final_v1/run_receipt.json"
    full_run = js(full_run_path)
    assert full_run["status"] == "PASS_complete_bounded_rebuild"
    assert len(full_run["steps"]) == 17 and all(s["exit_code"] == 0 for s in full_run["steps"])
    assert full_run["runner_sha256"] == sha(CODE / "run.py")
    with (DATA / "reproductions/final_v1/canonical_comparison.csv").open(newline="", encoding="utf-8-sig") as f:
        pairs = list(csv.DictReader(f))
    assert len(pairs) == 59
    for row in pairs:
        assert sha(ROOT / row["canonical"]) == row["canonical_sha256"]
        assert sha(ROOT / row["fresh"]) == row["fresh_sha256"] == row["canonical_sha256"]
    stages = []
    for package, pattern, expected_n in [("prospective_v1", "test_prospective.py", 13), ("economics_v1", "test_economics.py", 7)]:
        argv = [sys.executable, "-B", "-X", "utf8", "-m", "unittest", "discover", "-s", str(CODE / package), "-p", pattern, "-v"]
        p = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
        (out / (package + "_tests.log")).write_text(p.stdout, encoding="utf-8")
        assert p.returncode == 0 and re.search(r"Ran " + str(expected_n) + r" tests", p.stdout), p.stdout
        stages.append(dict(label=package, argv=argv, cwd=str(ROOT), exit_code=p.returncode, tests=expected_n))
    # Existing-output and path-traversal guards fail before dependency execution.
    guards = [("existing_output", ["--run-id", "final_v1", "--pdf-python", sys.executable], "Choose an unused run-id"),
              ("path_traversal", ["--run-id", "../escape", "--pdf-python", sys.executable], "run-id must be")]
    for name, args, message in guards:
        argv = [sys.executable, "-B", "-X", "utf8", str(CODE / "run.py"), *args]
        p = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
        (out / (name + ".log")).write_text(p.stdout, encoding="utf-8")
        assert p.returncode != 0 and message in p.stdout
        stages.append(dict(label=name, argv=argv, cwd=str(ROOT), exit_code=p.returncode, expected_rejection=True))
    for name, rows in [("analytical_identity.csv", identity), ("reviewer_bindings.csv", bindings)]:
        with (out / name).open("x", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    bound = [Path(__file__), manifest_path, DOCS / "handoff_v1/L4_HANDOFF.md", DOCS / "handoff_v1/ACCEPTANCE_FINAL.json",
             CODE / "run.py", CODE / "prospective_v1/test_prospective.py", CODE / "economics_v1/test_economics.py", full_run_path, *receipts]
    result = dict(status="PASS_BOUNDED_TECHNICAL_PUBLICATION_AUDIT", reviewer="/root/uncertainty_auditor",
        analytical_commit=ANALYTICAL, handoff_commit=HANDOFF, analytical_files=623, analytical_bytes=13362229,
        reviewer_file_binding_checks=len(bindings), accepted_final_postseal_receipt_bound=True,
        protection_counts=protection_counts, historical_full_runner_stages_verified=17,
        historical_full_runner_exact_pairs_reverified=59, existing_tests_rerun=20, guard_rejections_verified=2,
        material_findings=0, own_G_implementation_independently_certified=False,
        prior_G_receipts_role="hash integrity only; independent parent/I review remains authoritative",
        full_root_rebuild_rerun=False, prior_relocation_limit_retained=True,
        network_calls=0, git_mutations=0, empirical_refits_or_searches=0,
        commands=stages, bindings_sha256={str(p.relative_to(ROOT)):sha(p) for p in bound})
    (out / "receipt.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k not in ("commands", "bindings_sha256")}, indent=2))


if __name__ == "__main__":
    main()
