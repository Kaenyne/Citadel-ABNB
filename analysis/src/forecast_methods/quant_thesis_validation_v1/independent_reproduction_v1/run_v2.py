"""Rebuild both author packages and independent reviews into a fresh destination."""
import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
DATA = ROOT / "data/processed/forecast_methods/quant_thesis_validation_v1"
CODE = ROOT / "analysis/src/forecast_methods/quant_thesis_validation_v1"
BASELINE = "8821961853e4068febbfe2712f9a4e1036c9e629"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    out = parser.parse_args().out.resolve()
    if out.exists() or not out.is_relative_to((DATA / "independent_reproduction_v1").resolve()):
        raise ValueError("Require a fresh destination inside independent_reproduction_v1")
    out.mkdir(parents=True)
    commands = [
        [str(CODE / "source_audit_v1/run.py"), "--out", str(out / "source_rebuild")],
        [str(CODE / "prospective_v1/run.py"), "--out", str(out / "prospective_rebuild")],
        [str(CODE / "independent_reproduction_v1/source_review.py"), "--out", str(out / "source_review")],
        [str(CODE / "independent_reproduction_v1/prospective_review.py"), "--out", str(out / "prospective_review")],
    ]
    for args in commands:
        subprocess.run([sys.executable, "-B", "-X", "utf8", *args], cwd=ROOT, check=True)
    # Individual reviewers also bind the first retained reruns; here verify this
    # invocation's fresh author output independently, including every output file.
    byte_checks = []
    for canonical, rebuilt in [(DATA / "source_audit_v1/results_v3", out / "source_rebuild"),
                               (DATA / "prospective_v1/results_v1", out / "prospective_rebuild")]:
        for p in sorted(canonical.rglob("*")):
            if p.is_file():
                same = p.read_bytes() == (rebuilt / p.relative_to(canonical)).read_bytes()
                assert same, p
                byte_checks.append(dict(canonical=str(p.relative_to(ROOT)), sha256=sha(p), byte_identical=same))
    input_manifest = DATA / "prospective_v1/results_v1/forecast/input_manifest.json"
    bindings = []
    for row in json.loads(input_manifest.read_text()):
        path = ROOT / row["path"]
        local_sha = sha(path)
        git_sha = None
        if row["source"] == BASELINE:
            original = subprocess.check_output(["git", "show", BASELINE + ":" + row["path"]], cwd=ROOT)
            git_sha = hashlib.sha256(original).hexdigest()
            assert git_sha == row["sha256"], row
        if row["source"] == BASELINE:
            # Git stores LF; Windows checkout uses CRLF. Verify raw Git identity
            # and allow only that explicitly recorded checkout transformation.
            normalized_equal = path.read_bytes().replace(b"\r\n", b"\n") == original.replace(b"\r\n", b"\n")
            assert normalized_equal, row
        else:
            normalized_equal = None
            assert local_sha == row["sha256"], row
        bindings.append(dict(**row, local_sha256=local_sha, git_baseline_sha256=git_sha,
                             local_raw_matches_manifest=local_sha == row["sha256"],
                             local_text_matches_baseline_after_CRLF_to_LF=normalized_equal, verified=True))
    v2 = DATA / "source_audit_v1/results_v2/observation_availability.csv"
    v3 = DATA / "source_audit_v1/results_v3/observation_availability.csv"
    assert v2.read_bytes() == v3.read_bytes()
    semantic_path = DATA / "prospective_v1/author_handoff_v1/SEMANTIC_CORRECTION_v1.json"
    semantic = json.loads(semantic_path.read_text())
    assert semantic["forecast_or_score_change"] is False
    assert semantic["original_receipt_sha256"] == sha(DATA / "prospective_v1/results_v1/evaluation/evaluation_receipt.json")
    assert semantic["forecast_csv_sha256"] == sha(DATA / "prospective_v1/results_v1/forecast/predictions.csv")
    named = [input_manifest, semantic_path,
             ROOT / "docs/revenue-forecast-strategy/quant_thesis_validation_v1/prospective_v1/RECEIPT_WORDING_CORRECTION_v1.md",
             *sorted((CODE / "independent_reproduction_v1").glob("*.py")),
             out / "source_review/source_independent_receipt.json",
             out / "prospective_review/prospective_independent_receipt.json"]
    receipt = dict(
        reviewer="/root/uncertainty_auditor", reviewed_author="/root/source_auditor",
        status="PASS_independent_reproduction; original_research_hurdle_FAIL_retained",
        source_files_verified=len(bindings), fresh_author_files_byte_identical=len(byte_checks),
        source_availability_v2_v3_byte_identical=True,
        semantic_finding="CLOSED: points/input ledger frozen before scoring and target-outcome join; full source tables loaded earlier; functional filtering and adversarial checks verified",
        physical_blinding_claim=False,
        parent_adjudication_required=True,
        bindings={str(p.relative_to(ROOT)): sha(p) for p in named})
    (out / "source_binding_checks.json").write_text(json.dumps(bindings, indent=2) + "\n")
    (out / "independent_completion_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    with (out / "fresh_byte_reproduction.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(byte_checks[0])); writer.writeheader(); writer.writerows(byte_checks)
    print(json.dumps({k: v for k, v in receipt.items() if k != "bindings"}, indent=2))


if __name__ == "__main__":
    main()
