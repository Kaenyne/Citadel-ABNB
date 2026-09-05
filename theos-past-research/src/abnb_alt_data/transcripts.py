"""Deterministic conversion of user-provided FactSet transcripts to Markdown."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from typing import Mapping, Sequence


_SECTION_LABELS = {
    "MANAGEMENT DISCUSSION SECTION": ("Management discussion", "MD"),
    "QUESTION AND ANSWER SECTION": ("Question and answer", "QA"),
}
_HEADER_PATTERNS = (
    re.compile(r"^FactSet CallStreet, LLC$", re.IGNORECASE),
    re.compile(r"^.*\(ABNB(?:-[A-Z]+)?\)$"),
    re.compile(r"^Q[1-4]\s+\d{4}\s+Earnings Call$", re.IGNORECASE),
    re.compile(r"^.*\(ABNB(?:-[A-Z]+)?\).*Corrected Transcript$", re.IGNORECASE),
    re.compile(
        r"^Q[1-4]\s+\d{4}\s+Earnings Call\s+\d{2}-[A-Za-z]{3}-\d{4}$",
        re.IGNORECASE,
    ),
    re.compile(r"^(Corrected|Edited|Preliminary) Transcript$", re.IGNORECASE),
    re.compile(r"^\d{2}-[A-Za-z]{3}-\d{4}$"),
    re.compile(r"^\d+$"),
)
_DISCLAIMER_PREFIXES = (
    "copyright ©",
    "copyright (c)",
    "the information herein is based on sources",
)
_PDF_TIMEZONES = {
    "UTC": timezone.utc,
    "GMT": timezone.utc,
    "EST": timezone(timedelta(hours=-5)),
    "EDT": timezone(timedelta(hours=-4)),
    "CST": timezone(timedelta(hours=-6)),
    "CDT": timezone(timedelta(hours=-5)),
    "MST": timezone(timedelta(hours=-7)),
    "MDT": timezone(timedelta(hours=-6)),
    "PST": timezone(timedelta(hours=-8)),
    "PDT": timezone(timedelta(hours=-7)),
}


@dataclass(frozen=True)
class SpeakerTurn:
    turn_id: str
    speaker: str
    role: str
    text: str


@dataclass(frozen=True)
class TranscriptSection:
    name: str
    turns: tuple[SpeakerTurn, ...]


@dataclass(frozen=True)
class TranscriptMetadata:
    transcript_id: str
    ticker: str
    fiscal_period: str
    event_date: str
    event_at: str | None
    corrected_transcript_created_at: str | None
    pdf_creation_at: str | None
    published_at: str | None
    retrieved_at_utc: str | None
    indexed_at_utc: str
    point_in_time_usable_after: str | None
    availability_status: str
    source_provider: str
    source_filename: str
    source_sha256: str
    transcript_status: str
    license_status: str
    page_count: int
    word_count: int


def parse_pdfinfo(output: str) -> dict[str, str]:
    """Parse Poppler's ``pdfinfo`` key/value output without reinterpreting it."""
    parsed: dict[str, str] = {}
    for line in output.splitlines():
        key, separator, value = line.partition(":")
        if separator:
            parsed[key.strip()] = value.strip()
    return parsed


def run_poppler(
    pdf_path: Path,
    pdftotext_bin: str = "pdftotext",
    pdfinfo_bin: str = "pdfinfo",
) -> tuple[str, dict[str, str]]:
    """Extract layout-preserving text and metadata using Poppler binaries."""
    text_result = subprocess.run(
        [pdftotext_bin, "-layout", str(pdf_path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    info_result = subprocess.run(
        [pdfinfo_bin, str(pdf_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return text_result.stdout, parse_pdfinfo(info_result.stdout)


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _utc_string(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("timestamps must include a timezone")
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00", "Z"
    )


def _parse_pdf_creation(value: str | None) -> str | None:
    if not value:
        return None
    compact = " ".join(value.split())
    match = re.fullmatch(
        r"(?P<body>[A-Za-z]{3} [A-Za-z]{3} \d{1,2} \d{2}:\d{2}:\d{2} \d{4}) (?P<zone>[A-Z]{3})",
        compact,
    )
    if match and match.group("zone") in _PDF_TIMEZONES:
        parsed = datetime.strptime(match.group("body"), "%a %b %d %H:%M:%S %Y")
        return _utc_string(parsed.replace(tzinfo=_PDF_TIMEZONES[match.group("zone")]))
    iso_match = re.fullmatch(
        r"D:(?P<date>\d{14})(?P<offset>Z|[+-]\d{2}'?\d{2}'?)?", compact
    )
    if iso_match:
        parsed = datetime.strptime(iso_match.group("date"), "%Y%m%d%H%M%S")
        offset = iso_match.group("offset")
        if offset == "Z":
            return _utc_string(parsed.replace(tzinfo=timezone.utc))
        if offset:
            clean = offset.replace("'", "")
            sign = 1 if clean[0] == "+" else -1
            delta = timedelta(hours=int(clean[1:3]), minutes=int(clean[3:5]))
            return _utc_string(parsed.replace(tzinfo=timezone(sign * delta)))
    return None


def _extract_labeled_timestamp(raw_text: str, label: str) -> str | None:
    match = re.search(
        rf"^{re.escape(label)}\s*:\s*(.+?)\s*$", raw_text, flags=re.IGNORECASE | re.MULTILINE
    )
    if not match:
        return None
    candidate = match.group(1).strip()
    try:
        parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
    except ValueError:
        return None
    return _utc_string(parsed)


def parse_factset_metadata(
    raw_text: str,
    pdfinfo: Mapping[str, str],
    source_path: Path,
    retrieved_at: datetime | None,
    indexed_at: datetime,
) -> TranscriptMetadata:
    """Extract only metadata directly supported by the source artifact."""
    ticker_match = re.search(r"\(([A-Z]{1,6})(?:-[A-Z]+)?\)", raw_text)
    period_match = re.search(
        r"\bQ([1-4])\s+(20\d{2})\s+Earnings Call\b", raw_text, re.IGNORECASE
    )
    date_match = re.search(r"\b(\d{2}-[A-Za-z]{3}-20\d{2})\b", raw_text)
    if not ticker_match or not period_match or not date_match:
        raise ValueError(f"cannot establish ticker, fiscal period, and event date: {source_path}")

    ticker = ticker_match.group(1).upper()
    quarter, year = period_match.groups()
    fiscal_period = f"{year}Q{quarter}"
    event_date = datetime.strptime(date_match.group(1), "%d-%b-%Y").date().isoformat()
    transcript_status = (
        "corrected" if re.search(r"Corrected Transcript", raw_text, re.IGNORECASE) else "unknown"
    )

    return TranscriptMetadata(
        transcript_id=f"{ticker}-{fiscal_period}",
        ticker=ticker,
        fiscal_period=fiscal_period,
        event_date=event_date,
        event_at=None,
        corrected_transcript_created_at=_extract_labeled_timestamp(
            raw_text, "Corrected transcript created at"
        ),
        pdf_creation_at=_parse_pdf_creation(pdfinfo.get("CreationDate")),
        published_at=_extract_labeled_timestamp(raw_text, "Published at"),
        retrieved_at_utc=_utc_string(retrieved_at),
        indexed_at_utc=_utc_string(indexed_at) or "",
        point_in_time_usable_after=None,
        availability_status="unverified",
        source_provider="FactSet CallStreet",
        source_filename=source_path.name,
        source_sha256=_sha256(source_path),
        transcript_status=transcript_status,
        license_status="user_provided_restricted",
        page_count=int(pdfinfo.get("Pages", "0") or 0),
        word_count=0,
    )


def _is_artifact(line: str) -> bool:
    stripped = line.strip()
    if any(pattern.fullmatch(stripped) for pattern in _HEADER_PATTERNS):
        return True
    if "1-877-FACTSET" in stripped.upper() or "www.callstreet.com" in stripped.casefold():
        return True
    return stripped.casefold().startswith(_DISCLAIMER_PREFIXES)


def _block_to_turn(
    block: list[str], transcript_id: str, section_code: str, ordinal: int
) -> SpeakerTurn | None:
    while block and not block[0].strip():
        block.pop(0)
    while block and not block[-1].strip():
        block.pop()
    if not block:
        return None

    inline = re.match(r"^(?P<speaker>[^:]{1,100}):\s+(?P<speech>.+)$", block[0])
    if inline:
        speaker = inline.group("speaker").strip()
        role = ""
        speech_lines = [inline.group("speech").strip(), *block[1:]]
    else:
        if len(block) < 3:
            return None
        speaker = block[0].strip()
        role = block[1].strip()
        speech_lines = block[2:]

    paragraphs: list[str] = []
    paragraph: list[str] = []

    def join_wrapped(lines: list[str]) -> str:
        joined = lines[0]
        for continuation in lines[1:]:
            separator = ""
            if not (joined.endswith("-") and continuation[:1].islower()):
                separator = " "
            joined += separator + continuation
        return joined

    for line in speech_lines:
        if line.strip():
            paragraph.append(line.strip())
        elif paragraph:
            paragraphs.append(join_wrapped(paragraph))
            paragraph = []
    if paragraph:
        paragraphs.append(join_wrapped(paragraph))
    text = "\n\n".join(paragraphs).strip()
    if not text:
        return None
    return SpeakerTurn(
        turn_id=f"{transcript_id}-{section_code}-{ordinal:03d}",
        speaker=speaker,
        role=role,
        text=text,
    )


def clean_factset_text(
    raw_text: str, transcript_id: str
) -> tuple[TranscriptSection, ...]:
    """Remove page artifacts while preserving ordered, cited speaker turns."""
    sections: list[TranscriptSection] = []
    current_name: str | None = None
    current_code = "OTHER"
    blocks: list[list[str]] = []
    block: list[str] = []

    def flush_block() -> None:
        nonlocal block
        if block:
            blocks.append(block)
            block = []

    def flush_section() -> None:
        nonlocal blocks
        flush_block()
        if current_name is None:
            blocks = []
            return
        turns: list[SpeakerTurn] = []
        for candidate in blocks:
            turn = _block_to_turn(candidate, transcript_id, current_code, len(turns) + 1)
            if turn is not None:
                turns.append(turn)
        if turns:
            sections.append(TranscriptSection(current_name, tuple(turns)))
        blocks = []

    for raw_line in raw_text.splitlines():
        stripped = raw_line.strip()
        label = _SECTION_LABELS.get(stripped.upper())
        if label:
            flush_section()
            current_name, current_code = label
            continue
        if current_name is None:
            continue
        if re.fullmatch(r"\.{8,}", stripped):
            flush_block()
            continue
        if _is_artifact(stripped):
            continue
        if not stripped:
            if block and block[-1] != "":
                block.append("")
            continue
        block.append(stripped)
    flush_section()
    return tuple(sections)


def _yaml_value(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def render_markdown(
    metadata: TranscriptMetadata, sections: Sequence[TranscriptSection]
) -> str:
    """Render deterministic Markdown with source metadata and stable anchors."""
    lines = ["---"]
    for key, value in asdict(metadata).items():
        lines.append(f"{key}: {_yaml_value(value)}")
    lines.extend(["---", "", f"# {metadata.ticker} {metadata.fiscal_period} Earnings Call", ""])
    for section in sections:
        lines.extend([f"## {section.name}", ""])
        for turn in section.turns:
            lines.append(f'<a id="{turn.turn_id}"></a>')
            lines.append(f"### {turn.turn_id} — {turn.speaker}")
            lines.append("")
            if turn.role:
                lines.extend([f"*{turn.role}*", ""])
            lines.extend([turn.text, ""])
    return "\n".join(lines).rstrip() + "\n"


def _word_count(sections: Sequence[TranscriptSection]) -> int:
    return sum(
        len(re.findall(r"\b[\w'-]+\b", turn.text))
        for section in sections
        for turn in section.turns
    )


def convert_pdf(
    pdf_path: Path,
    output_dir: Path,
    retrieved_at: datetime | None,
    indexed_at: datetime,
    pdftotext_bin: str = "pdftotext",
    pdfinfo_bin: str = "pdfinfo",
) -> dict[str, str]:
    """Convert one PDF and return its canonical transcript-index row."""
    raw_text, pdfinfo = run_poppler(pdf_path, pdftotext_bin, pdfinfo_bin)
    metadata = parse_factset_metadata(
        raw_text, pdfinfo, pdf_path, retrieved_at=retrieved_at, indexed_at=indexed_at
    )
    sections = clean_factset_text(raw_text, metadata.transcript_id)
    if not sections:
        raise ValueError(f"no transcript sections found: {pdf_path}")
    metadata = replace(metadata, word_count=_word_count(sections))

    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = output_dir / f"{metadata.transcript_id}.md"
    markdown_path.write_text(render_markdown(metadata, sections), encoding="utf-8")

    row = {key: "" if value is None else str(value) for key, value in asdict(metadata).items()}
    row["markdown_path"] = markdown_path.as_posix()
    return row
