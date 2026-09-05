#!/usr/bin/env python3
"""Validate ABNB agent configuration, research tables, and local provenance."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from abnb_alt_data.validation import validate_project  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--expected-transcripts", type=int, default=23)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--metadata-only",
        action="store_true",
        help="validate tracked metadata without requiring licensed transcript text",
    )
    modes.add_argument(
        "--private-checksums",
        action="store_true",
        help=(
            "validate acquired private PDFs and cleaned Markdown against the "
            "tracked index and restricted-data manifest"
        ),
    )
    parser.add_argument(
        "--private-input-root",
        type=Path,
        help="root containing EARNING-TRANSCRIPTS and data/licensed inputs",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.private_input_root is not None and not args.private_checksums:
        parser.error("--private-input-root requires --private-checksums")
    findings = validate_project(
        args.root,
        args.expected_transcripts,
        require_licensed_text=not args.metadata_only,
        verify_private_checksums=args.private_checksums,
        private_input_root=args.private_input_root,
    )
    if findings:
        for finding in findings:
            print(f"{finding.code}: {finding.message}")
        return 1
    print("ABNB alt-data project validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
