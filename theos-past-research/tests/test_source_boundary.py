from __future__ import annotations

import csv
from pathlib import Path

from abnb_alt_data.source_boundary import (
    INVENTORY_FIELDS,
    build_inventory_rows,
    inventory_text,
)


ROOT = Path(__file__).resolve().parents[1]
COMMITTED = ROOT / "research/provenance/source-boundary-inventory.csv"


def test_source_boundary_classifies_imports_renames_and_raw_omissions(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    guidance = tmp_path / "guidance"
    project = tmp_path / "project"
    (source / "tests/fixtures").mkdir(parents=True)
    (project / "tests/fixtures").mkdir(parents=True)
    (source / "tests/fixtures/factset_sample.txt").write_text("synthetic")
    (project / "tests/fixtures/synthetic_callstreet_layout.txt").write_text("synthetic")
    raw = source / "research/readiness/20260903T053309Z_abnb_readiness/raw/page.html"
    raw.parent.mkdir(parents=True)
    raw.write_text("raw")
    replacement = (
        project
        / "research/readiness/20260903T053309Z_abnb_readiness/collection_provenance.csv"
    )
    replacement.parent.mkdir(parents=True)
    replacement.write_text("source_id\n")

    rows = build_inventory_rows(source, guidance, project)

    assert [row["classification"] for row in rows] == [
        "excluded_raw_payload",
        "included_renamed",
    ]
    assert inventory_text(rows).startswith(",".join(INVENTORY_FIELDS) + "\n")


def test_committed_source_boundary_is_complete_and_references_tracked_files() -> None:
    with COMMITTED.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert rows
    assert tuple(rows[0]) == INVENTORY_FIELDS
    assert not [row for row in rows if row["classification"] == "unreconciled"]
    assert {row["source_branch"] for row in rows} == {
        "main",
        "abnb-guidance-intelligence",
    }
    assert all(len(row["source_sha256"]) == 64 for row in rows)
    omissions = [row for row in rows if row["classification"].startswith("excluded_")]
    assert omissions
    assert [
        row["tracked_replacement"]
        for row in omissions
        if not (ROOT / row["tracked_replacement"]).exists()
    ] == []
