"""Deterministic document text extraction and excerpt checks."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import tempfile
import unicodedata

from .records import SourceDocument, SourceExcerpt
from .storage import ValidationFinding


@dataclass(frozen=True)
class ExtractedDocument:
    document_id: str
    text: str
    pages: dict[int, str]


@dataclass(frozen=True)
class TextSpan:
    heading: str
    text: str
    start_line: int
    end_line: int


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
        elif tag in {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth:
            self._skip_depth -= 1
        elif tag in {"p", "div", "li", "h1", "h2", "h3", "h4", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self.parts.append(data)


def normalize_for_match(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("—", "-").replace("–", "-").replace("−", "-")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _extract_pdf(path: Path, document_id: str) -> ExtractedDocument:
    with tempfile.TemporaryDirectory() as temporary_directory:
        output = Path(temporary_directory) / "document.txt"
        subprocess.run(
            ["pdftotext", "-layout", str(path), str(output)],
            check=True,
            capture_output=True,
            text=True,
        )
        raw = output.read_text(encoding="utf-8", errors="replace")
    page_texts = raw.split("\f")
    pages = {number: page.strip() for number, page in enumerate(page_texts, 1) if page.strip()}
    return ExtractedDocument(document_id=document_id, text="\n".join(pages.values()), pages=pages)


def _extract_html(path: Path, document_id: str) -> ExtractedDocument:
    parser = _VisibleTextParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    lines = [normalize_for_match(line) for line in "".join(parser.parts).splitlines()]
    text = "\n".join(line for line in lines if line)
    return ExtractedDocument(document_id=document_id, text=text, pages={})


def extract_text(document: SourceDocument) -> ExtractedDocument:
    if not document.local_path:
        raise ValueError(f"document has no local_path: {document.document_id}")
    path = Path(document.local_path)
    if not path.exists():
        raise FileNotFoundError(path)
    mime = document.mime_type or ""
    if mime == "application/pdf" or path.suffix.lower() == ".pdf":
        return _extract_pdf(path, document.document_id)
    if mime in {"text/html", "application/xhtml+xml"} or path.suffix.lower() in {".htm", ".html"}:
        return _extract_html(path, document.document_id)
    return ExtractedDocument(
        document_id=document.document_id,
        text=path.read_text(encoding="utf-8", errors="replace"),
        pages={},
    )


def verify_excerpt(excerpt: SourceExcerpt, document: ExtractedDocument) -> bool:
    if excerpt.document_id != document.document_id:
        return False
    haystack = document.text
    if excerpt.page_number is not None and document.pages:
        haystack = document.pages.get(excerpt.page_number, "")
    return normalize_for_match(excerpt.exact_excerpt) in normalize_for_match(haystack)


_OUTLOOK_HEADINGS = {"outlook", "guidance", "business outlook", "financial outlook"}
_STOP_HEADINGS = {
    "appendix",
    "financial statements",
    "non-gaap financial measures",
    "forward-looking statements",
    "questions and answers",
}


def find_outlook_sections(document: ExtractedDocument) -> list[TextSpan]:
    lines = [line.strip() for line in document.text.splitlines()]
    spans: list[TextSpan] = []
    for index, line in enumerate(lines):
        if line.casefold() not in _OUTLOOK_HEADINGS:
            continue
        content: list[str] = []
        end = index + 1
        for end in range(index + 1, len(lines)):
            candidate = lines[end]
            if candidate.casefold() in _STOP_HEADINGS:
                break
            if candidate:
                content.append(candidate)
        spans.append(
            TextSpan(
                heading=line,
                text="\n".join(content).strip(),
                start_line=index + 2,
                end_line=end,
            )
        )
    return spans


def excerpt_compliance_findings(
    excerpts: list[SourceExcerpt], documents: list[SourceDocument]
) -> list[ValidationFinding]:
    documents_by_id = {document.document_id: document for document in documents}
    totals: dict[str, int] = {}
    findings: list[ValidationFinding] = []
    for excerpt in excerpts:
        document = documents_by_id.get(excerpt.document_id)
        is_third_party = (
            excerpt.copyright_handling == "third_party_transcript"
            or (document is not None and document.document_type == "third_party_transcript")
        )
        if not is_third_party:
            continue
        word_count = len(excerpt.exact_excerpt.split())
        totals[excerpt.document_id] = totals.get(excerpt.document_id, 0) + word_count
        if word_count > 25:
            findings.append(
                ValidationFinding(
                    code="third_party_excerpt_too_long",
                    table="source_excerpts",
                    record_id=excerpt.source_excerpt_id,
                    message=f"third-party transcript excerpt has {word_count} words; maximum is 25",
                )
            )
    for document_id, word_count in totals.items():
        if word_count > 100:
            findings.append(
                ValidationFinding(
                    code="third_party_source_total_too_long",
                    table="source_excerpts",
                    record_id=document_id,
                    message=f"third-party transcript excerpts total {word_count} words; maximum is 100",
                )
            )
    return findings
