"""Generate portable manifests for intentionally omitted import assets."""

import argparse
import csv
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from abnb_alt_data.import_policy import (  # noqa: E402
    MANIFEST_FIELDS,
    build_omitted_rows,
    build_restricted_rows,
)


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: row["logical_path"]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--guidance-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()

    transcript_index = args.source_root / "research/transcripts/transcript_index.csv"
    restricted_rows = build_restricted_rows(args.source_root, transcript_index)
    omitted_rows = build_omitted_rows(args.source_root, args.guidance_root)
    write_manifest(args.output_root / "restricted-data-manifest.csv", restricted_rows)
    write_manifest(args.output_root / "omitted-data-manifest.csv", omitted_rows)
    print(f"Wrote {len(restricted_rows)} restricted and {len(omitted_rows)} omitted rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
