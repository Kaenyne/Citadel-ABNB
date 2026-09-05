from __future__ import annotations

import csv
from pathlib import Path

import pytest

from scripts.convert_transcripts import main


FIXTURE = Path(__file__).parent / "fixtures/factset_sample.txt"


def make_fake_poppler(tmp_path: Path) -> tuple[Path, Path]:
    pdftotext = tmp_path / "fake-pdftotext"
    pdftotext.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "import sys\n"
        "pdf = Path(sys.argv[-2])\n"
        "print(pdf.with_suffix('.txt').read_text(encoding='utf-8'))\n",
        encoding="utf-8",
    )
    pdfinfo = tmp_path / "fake-pdfinfo"
    pdfinfo.write_text(
        "#!/usr/bin/env python3\n"
        "print('Pages: 2')\n"
        "print('CreationDate: Thu Aug  6 16:30:00 2026 EDT')\n",
        encoding="utf-8",
    )
    pdftotext.chmod(0o755)
    pdfinfo.chmod(0o755)
    return pdftotext, pdfinfo


def add_source(source_dir: Path, name: str, quarter: str, date: str) -> Path:
    source_dir.mkdir(parents=True, exist_ok=True)
    pdf = source_dir / f"{name}.pdf"
    pdf.write_bytes(f"PDF:{name}".encode())
    text = FIXTURE.read_text(encoding="utf-8")
    text = text.replace("Q2 2026", quarter).replace("06-Aug-2026", date)
    pdf.with_suffix(".txt").write_text(text, encoding="utf-8")
    return pdf


def cli_args(
    source_dir: Path,
    output_dir: Path,
    index: Path,
    pdftotext: Path,
    pdfinfo: Path,
) -> list[str]:
    return [
        "--source-dir",
        str(source_dir),
        "--output-dir",
        str(output_dir),
        "--index",
        str(index),
        "--indexed-at",
        "2026-09-02T15:00:00Z",
        "--pdftotext",
        str(pdftotext),
        "--pdfinfo",
        str(pdfinfo),
    ]


def test_cli_converts_sorts_and_reruns_deterministically(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    output_dir = tmp_path / "clean"
    index = tmp_path / "research/transcript_index.csv"
    q2_pdf = add_source(source_dir, "later", "Q2 2026", "06-Aug-2026")
    q1_pdf = add_source(source_dir, "earlier", "Q1 2026", "01-May-2026")
    original_bytes = {path.name: path.read_bytes() for path in (q1_pdf, q2_pdf)}
    pdftotext, pdfinfo = make_fake_poppler(tmp_path)
    arguments = cli_args(source_dir, output_dir, index, pdftotext, pdfinfo)

    assert main(arguments) == 0
    first_index = index.read_bytes()
    assert main(arguments) == 0

    with index.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["fiscal_period"] for row in rows] == ["2026Q1", "2026Q2"]
    assert sorted(path.name for path in output_dir.glob("*.md")) == [
        "ABNB-2026Q1.md",
        "ABNB-2026Q2.md",
    ]
    assert index.read_bytes() == first_index
    assert {path.name: path.read_bytes() for path in (q1_pdf, q2_pdf)} == original_bytes


def test_cli_rejects_duplicate_fiscal_periods(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    output_dir = tmp_path / "clean"
    index = tmp_path / "transcript_index.csv"
    add_source(source_dir, "first", "Q2 2026", "06-Aug-2026")
    add_source(source_dir, "second", "Q2 2026", "06-Aug-2026")
    pdftotext, pdfinfo = make_fake_poppler(tmp_path)

    with pytest.raises(ValueError, match="duplicate fiscal period 2026Q2"):
        main(cli_args(source_dir, output_dir, index, pdftotext, pdfinfo))

    assert not index.exists()


def test_cli_rejects_timezone_naive_timestamp(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    output_dir = tmp_path / "clean"
    index = tmp_path / "transcript_index.csv"
    add_source(source_dir, "only", "Q2 2026", "06-Aug-2026")
    pdftotext, pdfinfo = make_fake_poppler(tmp_path)
    arguments = cli_args(source_dir, output_dir, index, pdftotext, pdfinfo)
    arguments[arguments.index("2026-09-02T15:00:00Z")] = "2026-09-02T15:00:00"

    with pytest.raises(ValueError, match="timezone"):
        main(arguments)
