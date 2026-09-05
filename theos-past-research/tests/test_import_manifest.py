import csv
from pathlib import Path

from abnb_alt_data.import_policy import (
    build_omitted_rows,
    build_restricted_rows,
)


def write_file(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def test_restricted_rows_describe_pdf_and_clean_markdown(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    write_file(source_root / "EARNING-TRANSCRIPTS" / "call.pdf", b"pdf bytes")
    write_file(
        source_root / "data/licensed/earnings_transcripts/clean_md/ABNB-2024Q1.md",
        b"clean transcript",
    )
    transcript_index = tmp_path / "transcript_index.csv"
    transcript_index.write_text(
        "source_filename,markdown_path\n"
        "call.pdf,data/licensed/earnings_transcripts/clean_md/ABNB-2024Q1.md\n",
        encoding="utf-8",
    )

    rows = build_restricted_rows(source_root, transcript_index)

    assert {row["asset_type"] for row in rows} == {
        "licensed_pdf",
        "licensed_markdown",
    }
    assert all(len(row["sha256"]) == 64 for row in rows)
    assert {row["tracking_status"] for row in rows} == {"excluded_restricted"}
    assert [row["logical_path"] for row in rows] == [
        "EARNING-TRANSCRIPTS/call.pdf",
        "data/licensed/earnings_transcripts/clean_md/ABNB-2024Q1.md",
    ]


def test_omitted_rows_classify_all_required_asset_families(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    guidance_root = tmp_path / "guidance"
    write_file(
        source_root
        / "research/edge_discovery/20260903T211121Z_50_source_expansion"
        / "processed/new_observations.csv",
        b"panel",
    )
    write_file(
        source_root
        / "outputs/example/global-lodging-map/raw/inside-airbnb/city.csv",
        b"raw lodging download",
    )
    write_file(source_root / "research/raw/source_payload.zip", b"zip")
    write_file(
        guidance_root / "research/abnb_guidance/data/normalized/events.parquet",
        b"parquet",
    )
    write_file(
        guidance_root / "research/abnb_guidance/data/normalized/events.csv",
        b"csv twin",
    )

    rows = build_omitted_rows(source_root, guidance_root)

    assert {row["reason"] for row in rows} == {
        "over_50_mib",
        "raw_global_lodging_download",
        "zip_source_payload",
        "parquet_csv_twin_included",
    }
    parquet_row = next(row for row in rows if row["logical_path"].endswith("events.parquet"))
    assert parquet_row["tracked_replacement"].endswith("events.csv")
    assert all(len(row["sha256"]) == 64 for row in rows)
