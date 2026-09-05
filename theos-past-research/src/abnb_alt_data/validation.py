"""End-to-end validation for the ABNB alternative-data research workspace."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import tomllib

from .leakage import validate_guidance_row
from .schemas import CSV_SCHEMAS, validate_csv_header


@dataclass(frozen=True)
class ValidationFinding:
    code: str
    message: str


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


def _validate_agent(root: Path, findings: list[ValidationFinding]) -> None:
    path = root / ".codex/agents/abnb_alt_data.toml"
    try:
        with path.open("rb") as handle:
            config = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as error:
        findings.append(ValidationFinding("agent_config", f"cannot parse {path}: {error}"))
        return
    expected = {
        "name": "abnb_alt_data",
        "model": "gpt-5.6-sol",
        "model_reasoning_effort": "high",
        "sandbox_mode": "workspace-write",
    }
    errors = [
        f"{key}={config.get(key)!r}, expected {value!r}"
        for key, value in expected.items()
        if config.get(key) != value
    ]
    for key in ("description", "developer_instructions"):
        if not str(config.get(key, "")).strip():
            errors.append(f"{key} is missing")
    if errors:
        findings.append(ValidationFinding("agent_config", "; ".join(errors)))


def _validate_schemas(root: Path, findings: list[ValidationFinding]) -> set[str]:
    valid: set[str] = set()
    for relative, fields in CSV_SCHEMAS.items():
        try:
            validate_csv_header(root / relative, fields)
            valid.add(relative)
        except (OSError, ValueError) as error:
            findings.append(ValidationFinding("csv_schema", str(error)))
    return valid


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _resolve_markdown(root: Path, value: str) -> Path | None:
    candidate = Path(value)
    path = candidate if candidate.is_absolute() else root / candidate
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None
    return resolved


def _validate_transcripts(
    root: Path,
    expected_transcript_count: int,
    require_licensed_text: bool,
    valid_schemas: set[str],
    findings: list[ValidationFinding],
) -> tuple[dict[str, dict[str, str]], dict[str, set[str]]]:
    relative = "research/transcripts/transcript_index.csv"
    if relative not in valid_schemas:
        return {}, {}
    rows = _read_csv(root / relative)
    if len(rows) != expected_transcript_count:
        findings.append(
            ValidationFinding(
                "transcript_count",
                f"transcript index has {len(rows)} rows; expected {expected_transcript_count}",
            )
        )

    seen_ids: set[str] = set()
    seen_periods: set[str] = set()
    index_by_markdown: dict[str, dict[str, str]] = {}
    turns_by_markdown: dict[str, set[str]] = {}
    for row in rows:
        transcript_id = row.get("transcript_id", "")
        fiscal_period = row.get("fiscal_period", "")
        if transcript_id in seen_ids:
            findings.append(
                ValidationFinding("duplicate_transcript_id", f"duplicate {transcript_id}")
            )
        if fiscal_period in seen_periods:
            findings.append(
                ValidationFinding("duplicate_fiscal_period", f"duplicate {fiscal_period}")
            )
        seen_ids.add(transcript_id)
        seen_periods.add(fiscal_period)

        markdown_value = row.get("markdown_path", "")
        index_by_markdown[markdown_value] = row
        markdown_path = _resolve_markdown(root, markdown_value)
        if markdown_path is None:
            findings.append(
                ValidationFinding(
                    "markdown_outside_root", f"Markdown path leaves project: {markdown_value}"
                )
            )
            continue
        if not markdown_path.exists():
            if require_licensed_text:
                findings.append(
                    ValidationFinding("missing_markdown", f"missing {markdown_value}")
                )
            continue
        text = markdown_path.read_text(encoding="utf-8")
        if "## Management discussion" not in text or "## Question and answer" not in text:
            findings.append(
                ValidationFinding(
                    "invalid_markdown", f"missing required sections: {markdown_value}"
                )
            )
        turn_ids = re.findall(r'<a id="([^"]+)"></a>', text)
        if not turn_ids or len(turn_ids) != len(set(turn_ids)):
            findings.append(
                ValidationFinding(
                    "invalid_turn_ids", f"missing or duplicate turn IDs: {markdown_value}"
                )
            )
        turns_by_markdown[markdown_value] = set(turn_ids)

    if expected_transcript_count == 23:
        expected_periods = {
            f"{year}Q{quarter}"
            for year in range(2020, 2027)
            for quarter in range(1, 5)
            if (year, quarter) >= (2020, 4) and (year, quarter) <= (2026, 2)
        }
        if seen_periods != expected_periods:
            missing = sorted(expected_periods - seen_periods)
            extra = sorted(seen_periods - expected_periods)
            findings.append(
                ValidationFinding(
                    "fiscal_period_coverage", f"missing={missing}; extra={extra}"
                )
            )
    return index_by_markdown, turns_by_markdown


def _validate_guidance(
    root: Path,
    require_licensed_text: bool,
    valid_schemas: set[str],
    index_by_markdown: dict[str, dict[str, str]],
    turns_by_markdown: dict[str, set[str]],
    findings: list[ValidationFinding],
) -> None:
    relative = "research/transcripts/guidance_facts.csv"
    if relative not in valid_schemas:
        return
    for row_number, row in enumerate(_read_csv(root / relative), start=2):
        try:
            source_markdown = row.get("source_markdown", "")
            turns = turns_by_markdown
            if not require_licensed_text and source_markdown not in turns:
                turns = dict(turns)
                turns[source_markdown] = {row.get("source_turn_id", "")}
            validate_guidance_row(row, index_by_markdown, turns)
        except ValueError as error:
            findings.append(
                ValidationFinding("invalid_guidance", f"row {row_number}: {error}")
            )


def _validate_ignore_policy(root: Path, findings: list[ValidationFinding]) -> None:
    for representative in (
        "EARNING-TRANSCRIPTS/example.pdf",
        "data/licensed/earnings_transcripts/clean_md/example.md",
        ".env",
        ".env.local",
        ".env.production",
    ):
        if _git(root, "check-ignore", "-q", representative).returncode != 0:
            findings.append(
                ValidationFinding("ignore_policy", f"path is not ignored: {representative}")
            )
    if _git(root, "check-ignore", "-q", ".env.example").returncode == 0:
        findings.append(
            ValidationFinding("ignore_policy", "environment template is ignored: .env.example")
        )


def _validate_staging(root: Path, findings: list[ValidationFinding]) -> None:
    result = _git(
        root,
        "diff",
        "--cached",
        "--name-only",
        "--relative",
        "--diff-filter=ACMR",
    )
    if result.returncode != 0:
        findings.append(
            ValidationFinding("git_unavailable", result.stderr.strip() or "git diff failed")
        )
        return
    for value in result.stdout.splitlines():
        path = value.strip()
        if path.startswith("EARNING-TRANSCRIPTS/") or path.startswith(
            "data/licensed/earnings_transcripts/clean_md/"
        ):
            findings.append(
                ValidationFinding("proprietary_staged", f"restricted path staged: {path}")
            )
        name = Path(path).name.casefold()
        if name in {".env", ".env.local", ".env.production"} or Path(name).suffix in {
            ".key",
            ".pem",
            ".p12",
        }:
            findings.append(
                ValidationFinding("credential_staged", f"possible credential staged: {path}")
            )


def validate_project(
    root: Path,
    expected_transcript_count: int = 23,
    require_licensed_text: bool = True,
) -> list[ValidationFinding]:
    """Return every detected project-integrity issue without mutating files."""
    root = root.resolve()
    findings: list[ValidationFinding] = []
    _validate_agent(root, findings)
    valid_schemas = _validate_schemas(root, findings)
    index, turns = _validate_transcripts(
        root, expected_transcript_count, require_licensed_text, valid_schemas, findings
    )
    _validate_guidance(root, require_licensed_text, valid_schemas, index, turns, findings)
    _validate_ignore_policy(root, findings)
    _validate_staging(root, findings)
    return findings
