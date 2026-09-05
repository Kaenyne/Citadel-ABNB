from __future__ import annotations

import csv
from hashlib import sha256
from pathlib import Path
import subprocess

import pytest

from abnb_alt_data.import_policy import MANIFEST_FIELDS
from abnb_alt_data.schemas import CSV_SCHEMAS, TRANSCRIPT_INDEX_FIELDS, write_empty_csv
from abnb_alt_data.validation import validate_project
from scripts.validate_project import main


MARKDOWN = "data/licensed/earnings_transcripts/clean_md/ABNB-2026Q2.md"
PDF = "EARNING-TRANSCRIPTS/sample.pdf"


def run_git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    )


def write_restricted_manifest(
    root: Path,
    *,
    pdf_sha256: str,
    markdown_sha256: str,
) -> None:
    path = root / "research/provenance/restricted-data-manifest.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for asset_type, logical_path, digest in (
        ("licensed_pdf", PDF, pdf_sha256),
        ("licensed_markdown", MARKDOWN, markdown_sha256),
    ):
        rows.append(
            {
                "asset_type": asset_type,
                "source_branch": "main",
                "logical_path": logical_path,
                "reason": "licensed_factset_callstreet_transcript",
                "bytes": "1",
                "sha256": digest,
                "tracked_replacement": "research/transcripts/transcript_index.csv",
                "rebuild_command": "Obtain through an approved private channel.",
                "tracking_status": "excluded_restricted",
            }
        )
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_project(root: Path) -> dict[str, str]:
    for relative, fields in CSV_SCHEMAS.items():
        write_empty_csv(root / relative, fields)

    agent = root / ".codex/agents/abnb_alt_data.toml"
    agent.parent.mkdir(parents=True, exist_ok=True)
    agent.write_text(
        'name = "abnb_alt_data"\n'
        'description = "ABNB research"\n'
        'model = "gpt-5.6-sol"\n'
        'model_reasoning_effort = "high"\n'
        'sandbox_mode = "workspace-write"\n'
        'developer_instructions = "Point-in-time research."\n',
        encoding="utf-8",
    )

    markdown = root / MARKDOWN
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text(
        "## Management discussion\n\n"
        '<a id="ABNB-2026Q2-MD-001"></a>\n'
        "### ABNB-2026Q2-MD-001 — Example\n\nSynthetic text.\n\n"
        "## Question and answer\n\n"
        '<a id="ABNB-2026Q2-QA-001"></a>\n'
        "### ABNB-2026Q2-QA-001 — Example\n\nSynthetic answer.\n",
        encoding="utf-8",
    )
    row = {field: "" for field in TRANSCRIPT_INDEX_FIELDS}
    row.update(
        transcript_id="ABNB-2026Q2",
        ticker="ABNB",
        fiscal_period="2026Q2",
        event_date="2026-08-06",
        event_at="2026-08-06T20:00:00Z",
        indexed_at_utc="2026-09-02T15:00:00Z",
        point_in_time_usable_after="2026-08-06T20:00:00Z",
        availability_status="verified",
        source_provider="Synthetic",
        source_filename="sample.pdf",
        source_sha256="a" * 64,
        transcript_status="corrected",
        license_status="synthetic",
        page_count="2",
        word_count="4",
        markdown_path=MARKDOWN,
    )
    index = root / "research/transcripts/transcript_index.csv"
    with index.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRANSCRIPT_INDEX_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerow(row)

    write_restricted_manifest(
        root,
        pdf_sha256=row["source_sha256"],
        markdown_sha256=sha256(markdown.read_bytes()).hexdigest(),
    )

    (root / ".gitignore").write_text(
        "EARNING-TRANSCRIPTS/\n"
        "data/licensed/earnings_transcripts/clean_md/\n"
        ".env\n"
        ".env.*\n"
        "!.env.example\n",
        encoding="utf-8",
    )
    run_git(root, "init", "-q")
    return row


def finding_codes(root: Path, expected: int = 1) -> set[str]:
    return {item.code for item in validate_project(root, expected)}


def test_validator_accepts_consistent_project(tmp_path: Path) -> None:
    build_project(tmp_path)

    assert validate_project(tmp_path, expected_transcript_count=1) == []
    assert main(["--root", str(tmp_path), "--expected-transcripts", "1"]) == 0


def test_validator_reports_agent_and_schema_errors(tmp_path: Path) -> None:
    build_project(tmp_path)
    agent = tmp_path / ".codex/agents/abnb_alt_data.toml"
    agent.write_text(agent.read_text().replace("gpt-5.6-sol", "wrong-model"))
    (tmp_path / "research/source_registry.csv").write_text("wrong,header\n")

    codes = finding_codes(tmp_path)

    assert "agent_config" in codes
    assert "csv_schema" in codes


def test_validator_reports_missing_markdown_and_count_mismatch(tmp_path: Path) -> None:
    build_project(tmp_path)
    (tmp_path / MARKDOWN).unlink()

    codes = finding_codes(tmp_path, expected=2)

    assert "transcript_count" in codes
    assert "missing_markdown" in codes


def test_metadata_only_validation_allows_absent_restricted_text(tmp_path: Path) -> None:
    build_project(tmp_path)
    (tmp_path / MARKDOWN).unlink()

    findings = validate_project(
        tmp_path,
        expected_transcript_count=1,
        require_licensed_text=False,
    )

    assert not [
        finding
        for finding in findings
        if finding.code in {"missing_markdown", "invalid_guidance"}
    ]
    assert main(
        [
            "--root",
            str(tmp_path),
            "--expected-transcripts",
            "1",
            "--metadata-only",
        ]
    ) == 0


def test_metadata_only_reports_malformed_restricted_manifest(tmp_path: Path) -> None:
    build_project(tmp_path)
    manifest = tmp_path / "research/provenance/restricted-data-manifest.csv"
    manifest.write_text("wrong,header\nvalue,row\n", encoding="utf-8")

    findings = validate_project(
        tmp_path,
        expected_transcript_count=1,
        require_licensed_text=False,
    )

    assert "restricted_manifest" in {finding.code for finding in findings}


def test_private_checksum_validation_reports_missing_inputs(tmp_path: Path) -> None:
    build_project(tmp_path)
    (tmp_path / MARKDOWN).unlink()

    findings = validate_project(
        tmp_path,
        expected_transcript_count=1,
        verify_private_checksums=True,
    )

    missing = [
        finding.message
        for finding in findings
        if finding.code == "missing_restricted_input"
    ]
    assert missing == [f"missing {PDF}", f"missing {MARKDOWN}"]


def test_private_checksum_validation_reports_mismatch(tmp_path: Path) -> None:
    build_project(tmp_path)
    pdf = tmp_path / PDF
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"different private PDF")

    findings = validate_project(
        tmp_path,
        expected_transcript_count=1,
        verify_private_checksums=True,
    )

    mismatches = [
        finding.message
        for finding in findings
        if finding.code == "restricted_checksum_mismatch"
    ]
    assert mismatches == [f"checksum mismatch: {PDF}"]


def test_private_checksum_validation_accepts_matching_inputs(tmp_path: Path) -> None:
    build_project(tmp_path)
    pdf = tmp_path / PDF
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"matching private PDF")
    pdf_digest = sha256(pdf.read_bytes()).hexdigest()
    markdown_digest = sha256((tmp_path / MARKDOWN).read_bytes()).hexdigest()

    index = tmp_path / "research/transcripts/transcript_index.csv"
    with index.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows[0]["source_sha256"] = pdf_digest
    with index.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRANSCRIPT_INDEX_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    write_restricted_manifest(
        tmp_path,
        pdf_sha256=pdf_digest,
        markdown_sha256=markdown_digest,
    )

    assert validate_project(
        tmp_path,
        expected_transcript_count=1,
        verify_private_checksums=True,
    ) == []
    assert main(
        [
            "--root",
            str(tmp_path),
            "--expected-transcripts",
            "1",
            "--private-checksums",
        ]
    ) == 0


def test_validation_cli_rejects_conflicting_transcript_modes() -> None:
    with pytest.raises(SystemExit):
        main(["--metadata-only", "--private-checksums"])


def test_validator_reports_duplicate_fiscal_period(tmp_path: Path) -> None:
    row = build_project(tmp_path)
    duplicate = dict(row)
    duplicate["transcript_id"] = "ABNB-2026Q2-DUPLICATE"
    index = tmp_path / "research/transcripts/transcript_index.csv"
    with index.open("a", encoding="utf-8", newline="") as handle:
        csv.DictWriter(
            handle, fieldnames=TRANSCRIPT_INDEX_FIELDS, lineterminator="\n"
        ).writerow(duplicate)

    assert "duplicate_fiscal_period" in finding_codes(tmp_path, expected=2)


def test_validator_reports_invalid_guidance_turn(tmp_path: Path) -> None:
    build_project(tmp_path)
    guidance_path = tmp_path / "research/transcripts/guidance_facts.csv"
    with guidance_path.open("a", encoding="utf-8", newline="") as handle:
        csv.writer(handle, lineterminator="\n").writerow(
            [
                "G-1", "2026Q2", "2026-08-06T20:00:00Z",
                "2026-08-06T20:00:00Z", "2026Q3", "revenue", "range",
                "140", "160", "150", "", "USD millions", "USD",
                "reported", MARKDOWN, "MISSING-TURN", "false", "verified",
                "high", "",
            ]
        )

    assert "invalid_guidance" in finding_codes(tmp_path)


def test_validator_flags_staged_proprietary_and_secret_paths(tmp_path: Path) -> None:
    build_project(tmp_path)
    proprietary = tmp_path / "EARNING-TRANSCRIPTS/source.pdf"
    proprietary.parent.mkdir(parents=True)
    proprietary.write_bytes(b"restricted")
    secret = tmp_path / ".env"
    secret.write_text("TOKEN=synthetic\n", encoding="utf-8")
    run_git(tmp_path, "add", "-f", "EARNING-TRANSCRIPTS/source.pdf", ".env")

    codes = finding_codes(tmp_path)

    assert "proprietary_staged" in codes
    assert "credential_staged" in codes


def test_validator_reports_unignored_environment_secrets(tmp_path: Path) -> None:
    build_project(tmp_path)
    (tmp_path / ".gitignore").write_text(
        "EARNING-TRANSCRIPTS/\n"
        "data/licensed/earnings_transcripts/clean_md/\n",
        encoding="utf-8",
    )

    assert "ignore_policy" in finding_codes(tmp_path)
