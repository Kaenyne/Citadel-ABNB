from __future__ import annotations

import csv
from pathlib import Path

import pytest

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


def test_permission_cache_omissions_name_tracked_ledgers_and_retrieval_guidance(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    guidance = tmp_path / "guidance"
    project = tmp_path / "project"
    physical_base = Path(
        "research/edge_discovery/20260903T062839Z_abnb_edge_discovery/"
        "physical_world_activity_edge/permission_resolution"
    )
    supply_base = Path(
        "research/edge_discovery/20260903T062839Z_abnb_edge_discovery/"
        "supply_scarcity_web_edge/permission_resolution"
    )
    source_files = (
        physical_base / "cache/data_probe/DP-PW-001.json",
        physical_base / "cache/permission_recon_retry/PR-PW-R001.txt",
        supply_base / "cache/PR-001.body",
    )
    for relative in source_files:
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("cached response")

    normalized_physical = Path(
        *physical_base.parts[:1], "edge-discovery", *physical_base.parts[2:]
    )
    normalized_supply = Path(
        *supply_base.parts[:1], "edge-discovery", *supply_base.parts[2:]
    )
    for relative in (
        normalized_physical / "data_probe_results.csv",
        normalized_physical / "permission_recon_retry_results.csv",
        normalized_supply / "permission_recon_results.csv",
    ):
        path = project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("request_id,sha256\n")

    rows = {
        row["source_path"]: row
        for row in build_inventory_rows(source, guidance, project)
    }

    assert rows[source_files[0].as_posix()]["tracked_replacement"] == (
        "research/edge-discovery/20260903T062839Z_abnb_edge_discovery/"
        "physical_world_activity_edge/permission_resolution/data_probe_results.csv"
    )
    assert rows[source_files[1].as_posix()]["tracked_replacement"] == (
        "research/edge-discovery/20260903T062839Z_abnb_edge_discovery/"
        "physical_world_activity_edge/permission_resolution/permission_recon_retry_results.csv"
    )
    assert rows[source_files[2].as_posix()]["tracked_replacement"] == (
        "research/edge-discovery/20260903T062839Z_abnb_edge_discovery/"
        "supply_scarcity_web_edge/permission_resolution/permission_recon_results.csv"
    )
    assert all(row["reconstruction_reference"] for row in rows.values())


def test_unknown_cache_omission_fails_instead_of_emitting_blank_references(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source"
    cache_file = source / "research/unknown/cache/response.json"
    cache_file.parent.mkdir(parents=True)
    cache_file.write_text("cached response")

    with pytest.raises(ValueError, match="No omission reference"):
        build_inventory_rows(source, tmp_path / "guidance", tmp_path / "project")


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
    assert all(row["tracked_replacement"] for row in omissions)
    assert all(row["reconstruction_reference"] for row in omissions)
    assert [
        row["tracked_replacement"]
        for row in omissions
        if not (ROOT / row["tracked_replacement"]).is_file()
    ] == []
