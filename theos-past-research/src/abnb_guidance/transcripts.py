"""Metadata-only registration for user-supplied earnings-call transcripts."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from .records import SourceDocument
from .sources import sha256_file


TRANSCRIPT_FILENAMES: dict[str, str] = {
    "2020Q4": "Airbnb,-Inc.Q42020EarningsCall-(1).pdf",
    "2021Q1": "ABNB_Q12021_EarningsCall_Transcript.pdf",
    "2021Q2": "Q2-2021_ABNB-Transcript_8.12.21.pdf",
    "2021Q3": "ABNB_Q32021_EarningsCall_Transcript.pdf",
    "2021Q4": "CORRECTED-TRANSCRIPT-Airbnb,-Inc.(ABNB-US),-Q4-2021-Earnings-Call-15-Feb-22.pdf",
    "2022Q1": "ABNBQ12022EarningsCall.pdf",
    "2022Q2": "Q2-2022-Earnings-Call_2022-08-02-20-30-00_Transcript-(1).pdf",
    "2022Q3": "ABNB-Corrected-Transcript-(1).pdf",
    "2022Q4": "Airbnb-Q4'22-Earnings-Call-Transcript.pdf",
    "2023Q1": "Airbnb-Q1-23-Earnings-Call-Transcript.pdf",
    "2023Q2": "Airbnb-Q2-23-Earnings-Call-Transcript.pdf",
    "2023Q3": "Airbnb-Q3-23-Earnings-Call-Transcript.pdf",
    "2023Q4": "Airbnb-Q4-23-Earnings-Call-Transcript.pdf",
    "2024Q1": "Airbnb-Q1-24-Earnings-Call-Transcript.pdf",
    "2024Q2": "Airbnb-Q2-24-Earnings-Call-Transcript.pdf",
    "2024Q3": "Airbnb-Q3-24-Earnings-Call-Transcript-1.pdf",
    "2024Q4": "Airbnb-Q4-24-Earnings-Call-Transcript.pdf",
    "2025Q1": "Airbnb-Q1-25-Earnings-Call-Transcript.pdf",
    "2025Q2": "Airbnb-Q2-25-Earnings-Call-Transcript.pdf",
    "2025Q3": "CORRECTED-TRANSCRIPT_-Airbnb-Inc-ABNB-US-Q3-2025-Earnings-Call-6-November-2025-5_00-PM-ET.pdf",
    "2025Q4": "Airbnb-Q4-25-Earnings-Call-Transcript.pdf",
    "2026Q1": "Airbnb-Q1-26-Earnings-Call-Transcript.pdf",
    "2026Q2": "Airbnb-Q2-2026-Earnings-Call-Transcript.pdf",
}


def build_transcript_manifest(
    transcript_directory: Path,
    filenames: dict[str, str] | None = None,
    *,
    retrieved_at: datetime,
) -> list[SourceDocument]:
    """Register local transcripts without copying or retaining their full text."""
    if retrieved_at.tzinfo is None or retrieved_at.utcoffset() is None:
        raise ValueError("retrieved_at must be timezone-aware")
    directory = Path(transcript_directory)
    mapping = filenames or TRANSCRIPT_FILENAMES
    documents: list[SourceDocument] = []
    for period, filename in sorted(mapping.items()):
        path = directory / filename
        if not path.is_file():
            raise FileNotFoundError(path)
        source_url = f"user-supplied://abnb-transcript/{quote(filename)}"
        documents.append(
            SourceDocument(
                document_id=f"ABNB-{period}-CALL-TRANSCRIPT",
                document_type="third_party_transcript",
                title=f"Airbnb {period} Earnings Call Corrected Transcript",
                publisher="FactSet CallStreet (user-supplied copy)",
                source_url=source_url,
                canonical_url=source_url,
                fiscal_period=period,
                document_date=None,
                published_at_utc=None,
                retrieved_at_utc=retrieved_at,
                capture_method="user-supplied local PDF; metadata, hash, and minimal excerpts only",
                mime_type="application/pdf",
                local_path=str(path.resolve()),
                sha256=sha256_file(path),
                rights_or_access_note="User-supplied research copy; do not redistribute or retain full extracted text in the repository.",
                version_status="user_supplied_corrected_or_as_received",
            )
        )
    return documents
