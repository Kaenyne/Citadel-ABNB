from abnb_guidance.extraction import (
    ExtractedDocument,
    excerpt_compliance_findings,
    find_outlook_sections,
    normalize_for_match,
    verify_excerpt,
)
from abnb_guidance.records import SourceDocument, SourceExcerpt


def excerpt(excerpt_id: str, text: str, handling: str = "official_document") -> SourceExcerpt:
    return SourceExcerpt.model_validate(
        {
            "source_excerpt_id": excerpt_id,
            "document_id": "DOC1",
            "page_number": 1,
            "section_heading": "Outlook",
            "exact_excerpt": text,
            "excerpt_word_count": len(text.split()),
            "context_paraphrase": "Forward outlook evidence",
            "copyright_handling": handling,
            "extraction_method": "manual_verified",
            "verified_against_source": True,
        }
    )


def transcript_document() -> SourceDocument:
    return SourceDocument.model_validate(
        {
            "document_id": "DOC1",
            "document_type": "third_party_transcript",
            "title": "Q3 call transcript",
            "publisher": "Licensed publisher",
            "source_url": "https://publisher.example/transcript",
            "canonical_url": "https://publisher.example/transcript",
            "capture_method": "metadata_and_excerpt_only",
            "rights_or_access_note": "No full-text retention",
            "version_status": "current",
        }
    )


def test_normalization_preserves_words_while_collapsing_layout_noise():
    assert normalize_for_match("Revenue\n  will be $2.0—$2.1 billion") == (
        "Revenue will be $2.0-$2.1 billion"
    )


def test_excerpt_must_exist_in_its_document():
    document = ExtractedDocument(
        document_id="DOC1",
        text="Revenue should grow in the fourth quarter.",
        pages={1: "Revenue should grow in the fourth quarter."},
    )

    assert verify_excerpt(excerpt("EX1", "language absent from source"), document) is False
    assert verify_excerpt(excerpt("EX2", "Revenue should grow"), document) is True


def test_outlook_section_is_found_without_consuming_following_heading():
    document = ExtractedDocument(
        document_id="DOC1",
        text="Results\nStrong quarter.\nOutlook\nRevenue will grow.\nAppendix\nTables",
        pages={},
    )

    spans = find_outlook_sections(document)

    assert len(spans) == 1
    assert spans[0].heading == "Outlook"
    assert spans[0].text == "Revenue will grow."


def test_third_party_transcript_excerpt_over_25_words_is_flagged():
    too_long = " ".join(f"word{i}" for i in range(26))

    findings = excerpt_compliance_findings(
        [excerpt("EX1", too_long, "third_party_transcript")],
        [transcript_document()],
    )

    assert any(f.code == "third_party_excerpt_too_long" for f in findings)


def test_third_party_event_total_over_100_words_is_flagged():
    excerpts = [
        excerpt(f"EX{i}", " ".join(f"w{i}_{j}" for j in range(25)), "third_party_transcript")
        for i in range(5)
    ]

    findings = excerpt_compliance_findings(excerpts, [transcript_document()])

    assert any(f.code == "third_party_source_total_too_long" for f in findings)
