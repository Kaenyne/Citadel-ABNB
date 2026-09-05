from pathlib import Path

from abnb_guidance.records import SourceDocument
from abnb_guidance.sources import (
    detect_duplicate_document,
    is_allowed_source,
    sha256_file,
)


def source(document_id: str, sha256: str | None) -> SourceDocument:
    return SourceDocument.model_validate(
        {
            "document_id": document_id,
            "document_type": "shareholder_letter",
            "title": document_id,
            "publisher": "Airbnb",
            "source_url": "https://investors.airbnb.com/financials/",
            "canonical_url": "https://investors.airbnb.com/financials/",
            "capture_method": "https_download",
            "sha256": sha256,
            "rights_or_access_note": "Public issuer document",
            "version_status": "current",
        }
    )


def test_official_domains_are_allowed_and_unknown_host_is_not():
    assert is_allowed_source(
        "https://investors.airbnb.com/financials/", "shareholder_letter"
    )
    assert is_allowed_source(
        "https://www.sec.gov/Archives/edgar/data/1559720/x.htm", "sec_filing"
    )
    assert is_allowed_source(
        "https://s26.q4cdn.com/656283129/files/doc_financials/a.pdf",
        "shareholder_letter",
    )
    assert not is_allowed_source(
        "https://example.com/abnb-transcript", "third_party_transcript"
    )


def test_sha256_is_stable(tmp_path: Path):
    path = tmp_path / "doc.txt"
    path.write_bytes(b"ABNB")

    assert sha256_file(path) == (
        "6d50f3cd55fb1bba76aabc8edc12a886c70509b2887e95b4bd49ab5443ccaa31"
    )


def test_duplicate_document_hashes_are_reported():
    digest = "a" * 64
    duplicates = detect_duplicate_document(
        [source("DOC_A", digest), source("DOC_B", digest), source("DOC_C", "b" * 64)]
    )

    assert duplicates == {digest: ["DOC_A", "DOC_B"]}
