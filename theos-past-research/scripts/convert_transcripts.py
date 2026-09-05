#!/usr/bin/env python3
"""Convert the local ABNB transcript corpus and write its compact index."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import sys
import tempfile
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from abnb_alt_data.schemas import TRANSCRIPT_INDEX_FIELDS  # noqa: E402
from abnb_alt_data.transcripts import convert_pdf  # noqa: E402


def parse_timestamp(value: str | None, field_name: str) -> datetime | None:
    if value is None or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{field_name} must be an ISO 8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field_name} must include a timezone")
    return parsed.astimezone(timezone.utc)


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_existing_index(path: Path) -> dict[tuple[str, str], str]:
    if not path.exists() or not path.stat().st_size:
        return {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != list(TRANSCRIPT_INDEX_FIELDS):
            raise ValueError(f"unexpected transcript index header: {path}")
        return {
            (row["source_filename"], row["source_sha256"]): row["indexed_at_utc"]
            for row in reader
            if row["source_filename"] and row["source_sha256"] and row["indexed_at_utc"]
        }


def write_index(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        writer = csv.DictWriter(
            handle, fieldnames=TRANSCRIPT_INDEX_FIELDS, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=Path("EARNING-TRANSCRIPTS"))
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/licensed/earnings_transcripts/clean_md"),
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=Path("research/transcripts/transcript_index.csv"),
    )
    parser.add_argument("--retrieved-at")
    parser.add_argument("--indexed-at")
    parser.add_argument("--pdftotext", default="pdftotext")
    parser.add_argument("--pdfinfo", default="pdfinfo")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    retrieved_at = parse_timestamp(args.retrieved_at, "--retrieved-at")
    indexed_override = parse_timestamp(args.indexed_at, "--indexed-at")
    source_paths = sorted(
        path
        for path in args.source_dir.iterdir()
        if path.is_file() and path.suffix.casefold() == ".pdf"
    )
    if not source_paths:
        raise ValueError(f"no PDF files found in {args.source_dir}")

    existing_times = read_existing_index(args.index)
    new_indexed_at = indexed_override or datetime.now(timezone.utc)
    args.output_dir.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(
        dir=args.output_dir.parent, prefix=".transcript-conversion-"
    ) as staging_name:
        staging = Path(staging_name)
        for source_path in source_paths:
            checksum = file_sha256(source_path)
            previous = existing_times.get((source_path.name, checksum))
            indexed_at = (
                parse_timestamp(previous, "indexed_at_utc")
                if indexed_override is None and previous
                else new_indexed_at
            )
            if indexed_at is None:
                raise ValueError("indexed timestamp cannot be empty")
            row = convert_pdf(
                source_path,
                staging,
                retrieved_at=retrieved_at,
                indexed_at=indexed_at,
                pdftotext_bin=args.pdftotext,
                pdfinfo_bin=args.pdfinfo,
            )
            final_markdown = args.output_dir / f"{row['transcript_id']}.md"
            row["markdown_path"] = final_markdown.as_posix()
            rows.append(row)

        transcript_ids: set[str] = set()
        fiscal_periods: set[str] = set()
        for row in rows:
            if row["fiscal_period"] in fiscal_periods:
                raise ValueError(f"duplicate fiscal period {row['fiscal_period']}")
            if row["transcript_id"] in transcript_ids:
                raise ValueError(f"duplicate transcript ID {row['transcript_id']}")
            transcript_ids.add(row["transcript_id"])
            fiscal_periods.add(row["fiscal_period"])

        rows.sort(key=lambda row: (row["fiscal_period"], row["source_filename"]))
        args.output_dir.mkdir(parents=True, exist_ok=True)
        expected_names = {f"{row['transcript_id']}.md" for row in rows}
        for stale in args.output_dir.glob("*.md"):
            if stale.name not in expected_names:
                stale.unlink()
        for row in rows:
            name = f"{row['transcript_id']}.md"
            (staging / name).replace(args.output_dir / name)

    write_index(args.index, rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
