import csv
from hashlib import sha256
from pathlib import Path

from abnb_alt_data.import_policy import (
    build_omitted_rows,
    build_restricted_rows,
)
from scripts.build_import_manifests import main as build_manifests


ROOT = Path(__file__).resolve().parents[1]


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


def test_omitted_rows_include_workbook_inspection_evidence_deterministically(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "source"
    guidance_root = tmp_path / "guidance"
    evidence = (
        source_root
        / "outputs/01a065f3-9f9d-7c33-a034-621059cc8c6f"
        / "ABNB_edge_guidance_stock_reaction.xlsx.inspect.ndjson"
    )
    payload = ('{"source":"/' + 'private/tmp/local-workbook.xlsx"}\n').encode()
    write_file(evidence, payload)

    first = build_omitted_rows(source_root, guidance_root)
    second = build_omitted_rows(source_root, guidance_root)

    assert first == second
    assert first == [
        {
            "asset_type": "workbook_inspection_evidence",
            "source_branch": "main",
            "logical_path": evidence.relative_to(source_root).as_posix(),
            "reason": "absolute_local_path",
            "bytes": str(len(payload)),
            "sha256": sha256(payload).hexdigest(),
            "tracked_replacement": (
                "outputs/workbooks/ABNB_edge_guidance_stock_reaction.xlsx"
            ),
            "rebuild_command": (
                "Generate local inspection evidence from the tracked workbook; "
                "do not commit machine-local inspection output."
            ),
            "tracking_status": "excluded_machine_local",
        }
    ]


def test_manifest_cli_check_requires_exact_regeneration(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    guidance_root = tmp_path / "guidance"
    output_root = tmp_path / "manifests"
    write_file(source_root / "EARNING-TRANSCRIPTS/call.pdf", b"pdf")
    write_file(
        source_root / "data/licensed/earnings_transcripts/clean_md/ABNB-2024Q1.md",
        b"markdown",
    )
    index = source_root / "research/transcripts/transcript_index.csv"
    index.parent.mkdir(parents=True)
    index.write_text(
        "source_filename,markdown_path\n"
        "call.pdf,data/licensed/earnings_transcripts/clean_md/ABNB-2024Q1.md\n",
        encoding="utf-8",
    )
    arguments = [
        "--source-root",
        str(source_root),
        "--guidance-root",
        str(guidance_root),
        "--output-root",
        str(output_root),
    ]

    assert build_manifests(arguments) == 0
    first = (output_root / "restricted-data-manifest.csv").read_bytes()
    assert build_manifests([*arguments, "--check"]) == 0
    (output_root / "restricted-data-manifest.csv").write_text("stale\n")
    assert build_manifests([*arguments, "--check"]) == 1
    assert first != b"stale\n"


def test_committed_omissions_have_existing_replacements_and_runnable_commands() -> None:
    path = ROOT / "research/provenance/omitted-data-manifest.csv"
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 32
    assert [
        row["tracked_replacement"]
        for row in rows
        if not (ROOT / row["tracked_replacement"]).exists()
    ] == []
    global_rows = [row for row in rows if row["asset_type"] == "raw_global_lodging_download"]
    assert len(global_rows) == 17
    assert all("--output-dir outputs/global-lodging-map" in row["rebuild_command"] for row in global_rows)
    panel = next(row for row in rows if row["asset_type"] == "oversized_observation_panel")
    assert "research/edge-discovery/" in panel["tracked_replacement"]
    assert "README.md" in panel["rebuild_command"]
