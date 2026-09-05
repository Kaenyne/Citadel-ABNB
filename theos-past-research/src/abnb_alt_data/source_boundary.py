"""Deterministic reconciliation of the approved historical-research sources."""

from __future__ import annotations

import csv
import hashlib
import os
from collections.abc import Iterable
from pathlib import Path


INVENTORY_FIELDS = (
    "source_branch",
    "source_path",
    "destination_path",
    "classification",
    "reason",
    "source_bytes",
    "source_sha256",
    "destination_sha256",
    "tracked_replacement",
    "reconstruction_reference",
)
MAIN_SOURCE_COMMIT = "cebd7f3a3fca93dd92f7a04ee3692ec809990505"
GUIDANCE_SOURCE_COMMIT = "580b7b9b981b1c8fab617eaae63f52692e3f180b"
PANEL = Path(
    "research/edge_discovery/20260903T211121Z_50_source_expansion/"
    "processed/new_observations.csv"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _walk_files(root: Path) -> Iterable[Path]:
    for directory, directory_names, filenames in os.walk(root):
        directory_names[:] = sorted(
            name
            for name in directory_names
            if name not in {".git", ".venv", ".worktrees", "__pycache__"}
            and not name.endswith(".egg-info")
        )
        for filename in sorted(filenames):
            path = Path(directory) / filename
            if path.suffix.lower() not in {".pyc", ".pyo", ".pyd"}:
                yield path


def iter_main_source_files(root: Path) -> Iterable[Path]:
    """Yield the plan-defined main-source boundary, including direct exclusions."""
    pruned = {
        ".git",
        ".pytest_cache",
        ".superpowers",
        ".venv",
        ".worktrees",
        "EARNING-TRANSCRIPTS",
        "output",
        "outputs",
    }
    for directory, directory_names, filenames in os.walk(root):
        relative_directory = Path(directory).relative_to(root)
        if not relative_directory.parts:
            directory_names[:] = [name for name in directory_names if name not in pruned]
        directory_names[:] = sorted(
            name
            for name in directory_names
            if name != "__pycache__" and not name.endswith(".egg-info")
        )
        if relative_directory.parts[:4] == (
            "data",
            "licensed",
            "earnings_transcripts",
            "clean_md",
        ):
            directory_names[:] = []
            continue
        for filename in sorted(filenames):
            path = Path(directory) / filename
            if path.suffix.lower() not in {".pyc", ".pyo", ".pyd"}:
                yield path


def iter_guidance_source_files(root: Path) -> Iterable[Path]:
    """Yield exactly the guidance paths named by the approved import plan."""
    exact = (
        ".codex/agents/abnb_guidance_intelligence.toml",
        "docs/superpowers/plans/2026-09-02-abnb-guidance-intelligence.md",
        "docs/superpowers/specs/2026-09-02-abnb-guidance-intelligence-design.md",
    )
    for relative in exact:
        path = root / relative
        if path.is_file():
            yield path
    for relative in ("src/abnb_guidance", "research/abnb_guidance", "tests"):
        path = root / relative
        if path.is_dir():
            yield from _walk_files(path)


def destination_path(source_branch: str, relative: Path) -> Path:
    if source_branch == "main":
        if relative.parts[:2] == ("research", "edge_discovery"):
            return Path("research", "edge-discovery", *relative.parts[2:])
        if relative.as_posix() == "tests/fixtures/factset_sample.txt":
            return Path("tests/fixtures/synthetic_callstreet_layout.txt")
        return relative
    if relative.parts[:2] == ("research", "abnb_guidance"):
        return Path("research", "guidance", *relative.parts[2:])
    if relative.as_posix() == "tests/test_agent_config.py":
        return Path("tests/test_guidance_agent_config.py")
    if relative.as_posix() == "tests/test_leakage.py":
        return Path("tests/test_guidance_leakage.py")
    return relative


def _main_exclusion(relative: Path) -> tuple[str, str] | None:
    if relative.name == ".DS_Store":
        return "excluded_nonportable_metadata", "finder_metadata"
    if relative.suffix.lower() == ".zip":
        return "excluded_archive", "zip_source_payload"
    if relative == PANEL:
        return "excluded_oversized", "over_50_mib"
    parts = set(relative.parts)
    if parts & {"cache", "raw_cache", ".artifact_tool"}:
        return "excluded_runtime_cache", "retrieval_or_render_cache"
    if "raw" in parts:
        return "excluded_raw_payload", "raw_retrieval_payload"
    if "tmp" in parts:
        return "excluded_temporary", "temporary_collection_artifact"
    if "previews" in parts or relative.suffix.lower() in {".png", ".jpg", ".jpeg"}:
        return "excluded_preview", "regenerable_render_preview"
    if relative.name.endswith(".inspect.ndjson"):
        return "excluded_inspection", "machine_local_inspection_evidence"
    if relative.name == "postfreeze_event_replay.xlsx":
        return "excluded_review_binary", "review_binary_with_tracked_data_twin"
    return None


def _omission_reference(relative: Path, classification: str) -> tuple[str, str]:
    normalized = destination_path("main", relative)
    value = normalized.as_posix()
    if relative == PANEL:
        base = "research/edge-discovery/20260903T211121Z_50_source_expansion"
        return (
            f"{base}/processed/new_source_manifest.csv",
            f"Follow {base}/README.md acquisition steps, then run python {base}/build_50_source_panel.py",
        )
    if relative.suffix.lower() == ".zip":
        base = "research/edge-discovery/20260903T204950Z_broad_scrape"
        return (
            f"{base}/processed/raw_file_manifest.csv",
            f"Follow {base}/README.md acquisition steps, then run python {base}/process_scrapes.py",
        )
    if ".artifact_tool" in relative.parts:
        base = (
            "research/edge-discovery/20260903T062839Z_abnb_edge_discovery/"
            "supply_scarcity_web_edge/e1_disposition"
        )
        return (
            f"{base}/build_postfreeze_replay.mjs",
            f"node {base}/build_postfreeze_replay.mjs",
        )
    if "20260903T204950Z_broad_scrape" in value:
        base = "research/edge-discovery/20260903T204950Z_broad_scrape"
        return f"{base}/processed/raw_file_manifest.csv", f"python {base}/process_scrapes.py"
    if "20260903T211121Z_50_source_expansion" in value:
        base = "research/edge-discovery/20260903T211121Z_50_source_expansion"
        return f"{base}/processed/raw_file_manifest.csv", f"Follow {base}/README.md"
    if "20260903T231817Z_abnb_us_altdata_sleeve" in value:
        base = "research/edge-discovery/20260903T231817Z_abnb_us_altdata_sleeve"
        return f"{base}/artifact_manifest.csv", f"python {base}/build_combined_sleeve.py"
    if "20260904T012519Z_abnb_adr_pilot_001" in value:
        base = "research/edge-discovery/20260904T012519Z_abnb_adr_pilot_001"
        return f"{base}/raw_file_manifest.csv", f"python {base}/build_adr_pilot.py"
    if "research/readiness/20260903T053309Z_abnb_readiness" in value:
        base = "research/readiness/20260903T053309Z_abnb_readiness"
        return f"{base}/collection_provenance.csv", f"python {base}/collect_phase_a.py"
    if "20260903T224632Z_50_source_guidance_format/previews" in value:
        base = "research/forecasting/runs/20260903T224632Z_50_source_guidance_format"
        return "outputs/workbooks/abnb_50_source_guidance_comparison.xlsx", f"node {base}/build_workbook.mjs"
    if "20260903T233712Z_us_europe_guidance_comparison/previews" in value:
        base = "research/forecasting/runs/20260903T233712Z_us_europe_guidance_comparison"
        return "outputs/workbooks/abnb_us_europe_guidance_comparison.xlsx", f"node {base}/build_workbook.mjs"
    if classification in {"excluded_review_binary", "excluded_inspection"}:
        base = (
            "research/edge-discovery/20260903T062839Z_abnb_edge_discovery/"
            "supply_scarcity_web_edge/e1_disposition"
        )
        return f"{base}/postfreeze_event_replay.csv", f"node {base}/build_postfreeze_replay.mjs"
    if classification == "excluded_nonportable_metadata":
        return "research/provenance/source-boundary-inventory.csv", "No reconstruction required."
    return "", ""


def _row(
    *,
    source_branch: str,
    source_root: Path,
    source_path: Path,
    project_root: Path,
) -> dict[str, str]:
    relative = source_path.relative_to(source_root)
    destination_relative = destination_path(source_branch, relative)
    destination = project_root / destination_relative
    source_digest = sha256_file(source_path)
    classification_reason = (
        _main_exclusion(relative) if source_branch == "main" else None
    )
    if source_branch != "main" and relative.suffix.lower() == ".parquet":
        classification_reason = ("excluded_binary_csv_twin", "parquet_csv_twin_included")

    if classification_reason is not None:
        classification, reason = classification_reason
        if classification == "excluded_binary_csv_twin":
            replacement = destination_relative.with_suffix(".csv").as_posix()
            reconstruction = "Use the tracked CSV twin for the imported snapshot."
        else:
            replacement, reconstruction = _omission_reference(relative, classification)
        destination_digest = ""
    elif destination.is_file():
        destination_digest = sha256_file(destination)
        if relative.as_posix() == "tests/fixtures/factset_sample.txt":
            classification, reason = "included_renamed", "safe_synthetic_fixture_name"
        elif source_digest == destination_digest:
            classification, reason = "included_identical", "byte_identical_import"
        else:
            classification, reason = "included_modified", "intentional_portability_or_integration_change"
        replacement = destination_relative.as_posix()
        reconstruction = "Tracked destination file."
    else:
        classification, reason = "unreconciled", "missing_without_classification"
        replacement = reconstruction = destination_digest = ""

    return {
        "source_branch": source_branch,
        "source_path": relative.as_posix(),
        "destination_path": destination_relative.as_posix(),
        "classification": classification,
        "reason": reason,
        "source_bytes": str(source_path.stat().st_size),
        "source_sha256": source_digest,
        "destination_sha256": destination_digest,
        "tracked_replacement": replacement,
        "reconstruction_reference": reconstruction,
    }


def build_inventory_rows(
    main_root: Path,
    guidance_root: Path,
    project_root: Path,
) -> list[dict[str, str]]:
    rows = [
        _row(
            source_branch="main",
            source_root=main_root,
            source_path=path,
            project_root=project_root,
        )
        for path in iter_main_source_files(main_root)
    ]
    rows.extend(
        _row(
            source_branch="abnb-guidance-intelligence",
            source_root=guidance_root,
            source_path=path,
            project_root=project_root,
        )
        for path in iter_guidance_source_files(guidance_root)
    )
    return sorted(rows, key=lambda row: (row["source_branch"], row["source_path"]))


def inventory_text(rows: list[dict[str, str]]) -> str:
    from io import StringIO

    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=INVENTORY_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
