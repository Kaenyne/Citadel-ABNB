import csv
from pathlib import Path


MANIFEST = (
    Path(__file__).resolve().parents[1]
    / "research/guidance/data/manifests/source_documents.csv"
)


def test_user_supplied_transcript_manifest_uses_portable_locators() -> None:
    with MANIFEST.open(encoding="utf-8", newline="") as manifest_file:
        transcripts = [
            row
            for row in csv.DictReader(manifest_file)
            if row["document_type"] == "third_party_transcript"
        ]

    assert transcripts
    assert all(row["source_url"].startswith("user-supplied://") for row in transcripts)
    assert all(row["canonical_url"].startswith("user-supplied://") for row in transcripts)
    assert all(not row["local_path"].startswith("/") for row in transcripts)
