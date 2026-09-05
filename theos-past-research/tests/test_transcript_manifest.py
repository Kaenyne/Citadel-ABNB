from datetime import UTC, datetime
from pathlib import Path

from abnb_guidance.transcripts import build_transcript_manifest


def test_user_supplied_transcript_manifest_has_stable_period_mapping(tmp_path: Path):
    for period, filename in {
        "2020Q4": "q4.pdf",
        "2021Q1": "q1.pdf",
    }.items():
        (tmp_path / filename).write_bytes(f"{period} transcript".encode())

    records = build_transcript_manifest(
        tmp_path,
        {"2020Q4": "q4.pdf", "2021Q1": "q1.pdf"},
        retrieved_at=datetime(2026, 9, 2, 16, tzinfo=UTC),
    )

    assert [record.fiscal_period for record in records] == ["2020Q4", "2021Q1"]
    assert all(record.document_type == "third_party_transcript" for record in records)
    assert all(record.sha256 and len(record.sha256) == 64 for record in records)
    assert all("User-supplied" in record.rights_or_access_note for record in records)


def test_missing_transcript_is_not_silently_ignored(tmp_path: Path):
    try:
        build_transcript_manifest(
            tmp_path,
            {"2020Q4": "missing.pdf"},
            retrieved_at=datetime(2026, 9, 2, 16, tzinfo=UTC),
        )
    except FileNotFoundError as error:
        assert "missing.pdf" in str(error)
    else:
        raise AssertionError("missing transcript should fail manifest construction")
