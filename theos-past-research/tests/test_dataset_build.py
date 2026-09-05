from datetime import UTC, datetime
from pathlib import Path

from abnb_guidance.dataset import build_research_dataset
from abnb_guidance.storage import load_table, validate_dataset


def test_dataset_build_writes_valid_normalized_tables(tmp_path: Path):
    result = build_research_dataset(
        tmp_path,
        retrieved_at=datetime(2026, 9, 2, 16, tzinfo=UTC),
    )

    assert result["event_count"] == 23
    assert result["numeric_revenue_guidance_count"] == 20
    assert len(load_table("quarterly_actuals", tmp_path)) == 23
    assert len(load_table("consensus_snapshots", tmp_path)) == 23
    assert len(load_table("evidence_claims", tmp_path)) > 50
    assert validate_dataset(tmp_path) == []


def test_dataset_build_registers_transcripts_without_copying_them(tmp_path: Path):
    transcript_dir = tmp_path / "transcripts"
    transcript_dir.mkdir()
    transcript = transcript_dir / "q3.pdf"
    transcript.write_bytes(b"user supplied")

    result = build_research_dataset(
        tmp_path / "research",
        transcript_directory=transcript_dir,
        transcript_filenames={"2025Q3": "q3.pdf"},
        retrieved_at=datetime(2026, 9, 2, 16, tzinfo=UTC),
    )
    documents = load_table("source_documents", tmp_path / "research")

    assert result["transcript_count"] == 1
    assert len(documents[documents["document_type"] == "third_party_transcript"]) == 1
    assert not (tmp_path / "research" / "raw_transcripts").exists()
