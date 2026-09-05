"""Provenance manifests and repository-boundary checks for the import."""

import csv
import hashlib
import os
import re
from collections.abc import Iterable
from pathlib import Path


MANIFEST_FIELDS = (
    "asset_type",
    "source_branch",
    "logical_path",
    "reason",
    "bytes",
    "sha256",
    "tracked_replacement",
    "rebuild_command",
    "tracking_status",
)
MAX_BYTES = 50 * 1024 * 1024
BLOCKED_PARTS = {
    ".venv",
    ".pytest_cache",
    ".superpowers",
    ".worktrees",
    "__pycache__",
}
BLOCKED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".parquet",
    ".zip",
    ".aux",
    ".fdb_latexmk",
    ".fls",
    ".log",
    ".out",
}
TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".toml",
    ".csv",
    ".json",
    ".ndjson",
    ".yaml",
    ".yml",
    ".txt",
    ".tex",
    ".mjs",
}
PANEL_PATH = Path(
    "research/edge_discovery/20260903T211121Z_50_source_expansion"
    "/processed/new_observations.csv"
)
SECRET_NAMES = (
    "API_" + "KEY",
    "AWS_" + "SECRET_ACCESS_KEY",
    "OPENAI_" + "API_KEY",
    "ANTHROPIC_" + "API_KEY",
    "GITHUB_" + "TOKEN",
    "FACTSET_" + "API_KEY",
    "FRED_" + "API_KEY",
)
SECRET_ASSIGNMENT_RE = re.compile(
    rf"(?m)^\s*(?:{'|'.join(SECRET_NAMES)})\s*=\s*(?!\s*(?:#|$))"
)
ABSOLUTE_PATH_MARKERS = ("/" + "Users/", "/" + "opt/", "C:" + "\\Users\\")


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file without loading it all at once."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest_row(
    *,
    asset_type: str,
    source_branch: str,
    logical_path: str,
    reason: str,
    path: Path,
    tracked_replacement: str,
    rebuild_command: str,
    tracking_status: str,
) -> dict[str, str]:
    return {
        "asset_type": asset_type,
        "source_branch": source_branch,
        "logical_path": logical_path,
        "reason": reason,
        "bytes": str(path.stat().st_size),
        "sha256": sha256_file(path),
        "tracked_replacement": tracked_replacement,
        "rebuild_command": rebuild_command,
        "tracking_status": tracking_status,
    }


def build_restricted_rows(
    source_root: Path, transcript_index: Path
) -> list[dict[str, str]]:
    """Describe the licensed PDFs and cleaned Markdown named in an index."""
    rows: list[dict[str, str]] = []
    with transcript_index.open(newline="", encoding="utf-8") as handle:
        for transcript in csv.DictReader(handle):
            pdf_logical_path = Path("EARNING-TRANSCRIPTS") / transcript["source_filename"]
            markdown_logical_path = Path(transcript["markdown_path"])
            for asset_type, logical_path in (
                ("licensed_pdf", pdf_logical_path),
                ("licensed_markdown", markdown_logical_path),
            ):
                path = source_root / logical_path
                rows.append(
                    _manifest_row(
                        asset_type=asset_type,
                        source_branch="main",
                        logical_path=logical_path.as_posix(),
                        reason="licensed_factset_callstreet_transcript",
                        path=path,
                        tracked_replacement="research/transcripts/transcript_index.csv",
                        rebuild_command=(
                            "Obtain through an approved institutional or private team "
                            "channel, then validate against research/transcripts/"
                            "transcript_index.csv."
                        ),
                        tracking_status="excluded_restricted",
                    )
                )
    return sorted(rows, key=lambda row: row["logical_path"])


def _source_files(root: Path, suffix: str) -> Iterable[Path]:
    for directory, directory_names, filenames in os.walk(root):
        directory_names[:] = [
            name
            for name in directory_names
            if name not in {".git", ".venv", ".worktrees", "__pycache__"}
        ]
        for filename in filenames:
            path = Path(directory) / filename
            if path.suffix.lower() == suffix:
                yield path


def _is_raw_global_lodging_file(path: Path, source_root: Path) -> bool:
    parts = path.relative_to(source_root).parts
    return "global-lodging-map" in parts and "raw" in parts


def _raw_global_lodging_files(source_root: Path) -> Iterable[Path]:
    outputs_root = source_root / "outputs"
    if not outputs_root.is_dir():
        return
    for directory, _, filenames in os.walk(outputs_root):
        for filename in filenames:
            path = Path(directory) / filename
            if _is_raw_global_lodging_file(path, source_root):
                yield path


def _guidance_logical_path(path: Path, guidance_root: Path) -> Path:
    relative = path.relative_to(guidance_root)
    source_prefix = ("research", "abnb_guidance")
    if relative.parts[:2] == source_prefix:
        return Path("research", "guidance", *relative.parts[2:])
    return relative


def build_omitted_rows(source_root: Path, guidance_root: Path) -> list[dict[str, str]]:
    """Describe oversized, raw, archive, and Parquet files kept out of Git."""
    rows: list[dict[str, str]] = []
    panel = source_root / PANEL_PATH
    if panel.is_file():
        rows.append(
            _manifest_row(
                asset_type="oversized_observation_panel",
                source_branch="main",
                logical_path=PANEL_PATH.as_posix(),
                reason="over_50_mib",
                path=panel,
                tracked_replacement=(
                    "research/edge_discovery/20260903T211121Z_50_source_expansion/"
                    "processed/new_source_manifest.csv"
                ),
                rebuild_command=(
                    "python research/edge_discovery/20260903T211121Z_50_source_expansion/"
                    "build_50_source_panel.py"
                ),
                tracking_status="excluded_oversized",
            )
        )

    for path in _raw_global_lodging_files(source_root):
        logical_path = path.relative_to(source_root).as_posix()
        rows.append(
            _manifest_row(
                asset_type="raw_global_lodging_download",
                source_branch="main",
                logical_path=logical_path,
                reason="raw_global_lodging_download",
                path=path,
                tracked_replacement="outputs/reproducibility/global-lodging-map-inputs.csv",
                rebuild_command="python scripts/build_global_lodging_map.py",
                tracking_status="excluded_raw",
            )
        )

    for path in _source_files(source_root, ".zip"):
        logical_path = path.relative_to(source_root).as_posix()
        rows.append(
            _manifest_row(
                asset_type="zip_source_payload",
                source_branch="main",
                logical_path=logical_path,
                reason="zip_source_payload",
                path=path,
                tracked_replacement="research/edge-discovery/",
                rebuild_command="Reacquire from the documented source manifest.",
                tracking_status="excluded_archive",
            )
        )

    for path in _source_files(guidance_root, ".parquet"):
        logical_path = _guidance_logical_path(path, guidance_root)
        csv_twin = logical_path.with_suffix(".csv")
        rows.append(
            _manifest_row(
                asset_type="guidance_parquet",
                source_branch="abnb-guidance-intelligence",
                logical_path=logical_path.as_posix(),
                reason="parquet_csv_twin_included",
                path=path,
                tracked_replacement=csv_twin.as_posix(),
                rebuild_command="Use the tracked CSV twin for the imported snapshot.",
                tracking_status="excluded_binary",
            )
        )
    return sorted(rows, key=lambda row: row["logical_path"])


def _relative_path(project_root: Path, candidate_path: Path) -> Path:
    if candidate_path.is_absolute():
        return candidate_path.resolve().relative_to(project_root.resolve())
    return candidate_path


def _text_violations(path: Path, display_path: str) -> list[str]:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return []
    content = path.read_text(encoding="utf-8", errors="replace")
    violations: list[str] = []
    if any(marker in content for marker in ABSOLUTE_PATH_MARKERS):
        violations.append(f"{display_path}: absolute local path in text")
    if path.name != ".env.example" and SECRET_ASSIGNMENT_RE.search(content):
        violations.append(f"{display_path}: nonblank secret assignment in tracked text")
    return violations


def collect_violations(
    project_root: Path, candidate_paths: Iterable[Path]
) -> list[str]:
    """Return every import-policy violation in the supplied candidate set."""
    violations: list[str] = []
    for candidate_path in candidate_paths:
        try:
            relative_path = _relative_path(project_root, candidate_path)
        except ValueError:
            violations.append(f"{candidate_path}: path is outside the project root")
            continue
        path = candidate_path if candidate_path.is_absolute() else project_root / candidate_path
        display_path = relative_path.as_posix()
        parts = relative_path.parts
        suffix = path.suffix.lower()
        if any(part in BLOCKED_PARTS for part in parts):
            violations.append(f"{display_path}: blocked cache or environment path")
        if any(part.endswith(".egg-info") for part in parts):
            violations.append(f"{display_path}: editable-install metadata is prohibited")
        if suffix in BLOCKED_SUFFIXES:
            violations.append(f"{display_path}: prohibited file suffix {suffix}")
        if "EARNING-TRANSCRIPTS" in parts:
            violations.append(f"{display_path}: licensed transcript PDF directory is prohibited")
        if any(
            parts[index : index + 4]
            == ("data", "licensed", "earnings_transcripts", "clean_md")
            for index in range(len(parts))
        ):
            violations.append(f"{display_path}: licensed cleaned-transcript directory is prohibited")
        if not path.is_file():
            continue
        if path.stat().st_size > MAX_BYTES:
            violations.append(f"{display_path}: file exceeds 50 MiB import limit")
        violations.extend(_text_violations(path, display_path))
    return violations
