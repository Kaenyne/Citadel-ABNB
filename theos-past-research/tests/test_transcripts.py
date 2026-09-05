from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from abnb_alt_data.transcripts import (
    clean_factset_text,
    convert_pdf,
    parse_factset_metadata,
    parse_pdfinfo,
    render_markdown,
)


FIXTURE = Path(__file__).parent / "fixtures/synthetic_callstreet_layout.txt"


def fixture_text() -> str:
    return FIXTURE.read_text(encoding="utf-8")


def test_parse_pdfinfo_preserves_reported_fields() -> None:
    parsed = parse_pdfinfo(
        "Title: Sample\nPages:          2\nCreationDate: Thu Aug  6 16:30:00 2026 EDT\n"
    )

    assert parsed == {
        "Title": "Sample",
        "Pages": "2",
        "CreationDate": "Thu Aug  6 16:30:00 2026 EDT",
    }


def test_metadata_keeps_pdf_creation_separate_from_public_availability(
    tmp_path: Path,
) -> None:
    pdf = tmp_path / "ABNB Q2 2026.pdf"
    pdf.write_bytes(b"synthetic-pdf")

    metadata = parse_factset_metadata(
        fixture_text(),
        {"Pages": "2", "CreationDate": "Thu Aug  6 16:30:00 2026 EDT"},
        pdf,
        retrieved_at=None,
        indexed_at=datetime(2026, 9, 2, 15, 0, tzinfo=timezone.utc),
    )

    assert metadata.transcript_id == "ABNB-2026Q2"
    assert metadata.ticker == "ABNB"
    assert metadata.fiscal_period == "2026Q2"
    assert metadata.event_date == "2026-08-06"
    assert metadata.event_at is None
    assert metadata.pdf_creation_at is not None
    assert metadata.point_in_time_usable_after is None
    assert metadata.availability_status == "unverified"
    assert metadata.source_sha256 == sha256(b"synthetic-pdf").hexdigest()


def test_cleaning_preserves_speech_sections_and_indiscernible_marker() -> None:
    sections = clean_factset_text(fixture_text(), "ABNB-2026Q2")

    assert [section.name for section in sections] == [
        "Management discussion",
        "Question and answer",
    ]
    turns = [turn for section in sections for turn in section.turns]
    assert [turn.turn_id for turn in turns] == [
        "ABNB-2026Q2-MD-001",
        "ABNB-2026Q2-MD-002",
        "ABNB-2026Q2-QA-001",
        "ABNB-2026Q2-QA-002",
    ]
    assert [turn.speaker for turn in turns] == [
        "Operator",
        "Alex Example",
        "Jamie Analyst",
        "Alex Example",
    ]
    assert turns[1].role == "AirStay, Inc. - Co-Founder & Chief Executive Officer"
    assert "[indiscernible]" in turns[1].text
    assert "year-over-year" in turns[1].text
    assert "year- over-year" not in turns[1].text
    assert "This second paragraph belongs to Alex's same speaker turn." in turns[1].text

    combined = "\n".join(turn.text for turn in turns)
    assert "Good afternoon" in combined
    assert "Booking windows were stable" in combined
    assert "FactSet CallStreet" not in combined
    assert "All rights reserved" not in combined
    assert "...." not in combined


def test_markdown_render_is_stable_and_uses_null_for_unknown_timestamps(
    tmp_path: Path,
) -> None:
    pdf = tmp_path / "ABNB Q2 2026.pdf"
    pdf.write_bytes(b"synthetic-pdf")
    metadata = parse_factset_metadata(
        fixture_text(),
        {"Pages": "2"},
        pdf,
        retrieved_at=None,
        indexed_at=datetime(2026, 9, 2, 15, 0, tzinfo=timezone.utc),
    )
    sections = clean_factset_text(fixture_text(), metadata.transcript_id)

    first = render_markdown(metadata, sections)
    second = render_markdown(metadata, sections)

    assert first == second
    assert "event_at: null" in first
    assert "published_at: null" in first
    assert "point_in_time_usable_after: null" in first
    assert f'source_sha256: "{sha256(b"synthetic-pdf").hexdigest()}"' in first
    assert '<a id="ABNB-2026Q2-QA-001"></a>' in first


def test_convert_pdf_writes_markdown_and_returns_index_row(
    tmp_path: Path, monkeypatch
) -> None:
    pdf = tmp_path / "ABNB Q2 2026.pdf"
    pdf.write_bytes(b"synthetic-pdf")
    output = tmp_path / "clean"

    monkeypatch.setattr(
        "abnb_alt_data.transcripts.run_poppler",
        lambda *_args, **_kwargs: (fixture_text(), {"Pages": "2"}),
    )

    row = convert_pdf(
        pdf,
        output,
        retrieved_at=None,
        indexed_at=datetime(2026, 9, 2, 15, 0, tzinfo=timezone.utc),
    )

    markdown = output / "ABNB-2026Q2.md"
    assert markdown.exists()
    assert row["transcript_id"] == "ABNB-2026Q2"
    assert row["markdown_path"].endswith("ABNB-2026Q2.md")
    assert row["word_count"] == "41"
