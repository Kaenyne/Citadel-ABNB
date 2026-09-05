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
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="validate tracked metadata without requiring licensed transcript text",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    findings = validate_project(
        args.root,
        args.expected_transcripts,
        require_licensed_text=not args.metadata_only,
    )
    if findings:
        for finding in findings:
            print(f"{finding.code}: {finding.message}")
        return 1
    print("ABNB alt-data project validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
