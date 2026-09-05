#!/usr/bin/env python3
"""Generate or verify the approved source-boundary inventory."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from abnb_alt_data.source_boundary import build_inventory_rows, inventory_text  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--guidance-root", required=True, type=Path)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "research/provenance/source-boundary-inventory.csv",
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rows = build_inventory_rows(args.source_root, args.guidance_root, args.project_root)
    unreconciled = [row["source_path"] for row in rows if row["classification"] == "unreconciled"]
    if unreconciled:
        print(f"Unreconciled source paths ({len(unreconciled)}):", file=sys.stderr)
        print("\n".join(unreconciled), file=sys.stderr)
        return 1
    expected = inventory_text(rows)
    if args.check:
        try:
            actual = args.output.read_text(encoding="utf-8")
        except OSError as error:
            print(f"Cannot read {args.output}: {error}", file=sys.stderr)
            return 1
        if actual != expected:
            print(f"Source-boundary inventory is stale: {args.output}", file=sys.stderr)
            return 1
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(expected, encoding="utf-8", newline="")

    counts = Counter(row["classification"] for row in rows)
    print(f"Verified {len(rows)} source rows: {dict(sorted(counts.items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
