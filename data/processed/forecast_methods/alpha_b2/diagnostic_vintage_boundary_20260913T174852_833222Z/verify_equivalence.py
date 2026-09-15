"""Reproduce the timestamp repair's read-only result/registry comparisons."""
from pathlib import Path
import csv
import hashlib
import io
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
BASE = ROOT / "data/processed/forecast_methods/alpha_b2"
REFERENCE = BASE / "run_20260913T171654_499731Z"
REBUILT = BASE / "run_20260913T175201_016865Z"
REGISTRY = ROOT / "data/processed/forecast_methods/registry/alpha-b2__revenue_q_plus_2.csv"


def sha(data):
    return hashlib.sha256(data).hexdigest()


comparisons = {}
for name in ("cells", "historical_term_structure", "statistics", "revision_baselines",
             "return_statistics", "live_term_structure", "current_consensus_comparisons",
             "registry_candidate"):
    actual = (REBUILT / (name + ".csv")).read_bytes()
    expected = (REFERENCE / (name + ".csv")).read_bytes()
    assert actual == expected, name
    comparisons[name] = {"byte_identical": True, "sha256": sha(actual)}

prior_hashes = json.loads((HERE / "pre_rebuild_hashes.json").read_text(encoding="utf-8"))
for path, expected in prior_hashes.items():
    assert sha((ROOT / path).read_bytes()) == expected, path

candidate_bytes = (REBUILT / "registry_candidate.csv").read_bytes()
registry_bytes = REGISTRY.read_bytes()
candidate = pd.read_csv(io.BytesIO(candidate_bytes))
registered = pd.read_csv(io.BytesIO(registry_bytes))
pd.testing.assert_frame_equal(candidate, registered[list(candidate.columns)], check_exact=True)

# Registry writer adds the documented optional columns and FORMAT marker.
# Preserve candidate lexical values while expanding only those empty fields.
rows = list(csv.DictReader(io.StringIO(candidate_bytes.decode("utf-8"))))
registry_reader = csv.DictReader(io.StringIO(registry_bytes.decode("utf-8")))
columns = registry_reader.fieldnames
extra = set(columns) - set(rows[0])
assert extra - {"format_version"} == {"q05", "q10", "q25", "q75", "q90", "q95", "sd",
    "base_ar1", "base_trailing4", "base_guide_cushion", "base_street", "street_vendor", "street_as_of"}
assert registered[list(extra - {"format_version"})].isna().all().all()
assert registered.format_version.astype(str).eq("1.1").all()
buffer = io.StringIO(newline="")
writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\r\n")
writer.writeheader()
for row in rows:
    writer.writerow({**row, "format_version": "1.1"})
expanded = buffer.getvalue().encode("utf-8")
assert expanded == registry_bytes, "Expanded FORMAT preview must be byte-identical to the current registry"

manifest = json.loads((REBUILT / "input_manifest.json").read_text(encoding="utf-8"))
dependencies = {}
for key in ("kernel_kpi_panel", "kernel_cushions"):
    record = manifest[key]
    assert sha((ROOT / record["path"]).read_bytes()) == record["sha256"]
    dependencies[key] = record

report = {"reference_run": str(REFERENCE.relative_to(ROOT)),
          "rebuild_run": str(REBUILT.relative_to(ROOT)), "research_and_preview": comparisons,
          "current_registry_byte_identical_to_expanded_preview": True,
          "current_registry_sha256": sha(registry_bytes),
          "preserved_reference_registry_preregistration_files": len(prior_hashes),
          "kernel_transitive_input_hashes": dependencies, "registry_write": False, "scorer_run": False}
# First execution writes new evidence; subsequent checks never overwrite it.
for filename, data in (("registry_preview_FORMAT_1_1.csv", expanded),
                       ("equivalence_verification.json", json.dumps(report, indent=2).encode("utf-8"))):
    target = HERE / filename
    if target.exists():
        assert target.read_bytes() == data, filename
    else:
        target.write_bytes(data)
print(json.dumps(report, indent=2))
