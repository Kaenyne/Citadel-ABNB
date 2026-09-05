"""Generate portable manifests for intentionally omitted import assets."""

import argparse
import csv
from io import StringIO
import sys
from pathlib import Path
from typing import Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from abnb_alt_data.import_policy import (  # noqa: E402
    MANIFEST_FIELDS,
    build_omitted_rows,
    build_restricted_rows,
)


def render_manifest(rows: list[dict[str, str]]) -> str:
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=MANIFEST_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(sorted(rows, key=lambda row: row["logical_path"]))
    return output.getvalue()


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_manifest(rows), encoding="utf-8", newline="")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--guidance-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if either committed manifest differs from exact regeneration",
    )
    args = parser.parse_args(argv)

    transcript_index = args.source_root / "research/transcripts/transcript_index.csv"
    restricted_rows = build_restricted_rows(args.source_root, transcript_index)
    omitted_rows = build_omitted_rows(args.source_root, args.guidance_root)
    manifests = {
        args.output_root / "restricted-data-manifest.csv": restricted_rows,
        args.output_root / "omitted-data-manifest.csv": omitted_rows,
    }
    if args.check:
        stale = [
            path
            for path, rows in manifests.items()
            if not path.is_file()
            or path.read_text(encoding="utf-8") != render_manifest(rows)
        ]
        if stale:
            print("Stale import manifest(s): " + ", ".join(str(path) for path in stale))
            return 1
        verb = "Verified"
    else:
        for path, rows in manifests.items():
            write_manifest(path, rows)
        verb = "Wrote"
    print(f"{verb} {len(restricted_rows)} restricted and {len(omitted_rows)} omitted rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
