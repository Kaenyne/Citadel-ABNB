#!/usr/bin/env python3
"""Download governed lodging snapshots and build a standalone 3D globe."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from typing import Any
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor

from abnb_alt_data.lodging_map import (
    build_market_record,
    relative_presence_indices,
    render_html,
    validate_manifest,
)


USER_AGENT = (
    "ABNB-altdata-research/1.0 "
    "(+https://github.com/theomachado05/airbnb-citadel-2026)"
)
OVERTURE_RELEASE = "2026-08-19.0"
OVERTURE_URI = (
    "s3://overturemaps-us-west-2/release/"
    f"{OVERTURE_RELEASE}/theme=places/type=place/*"
)
WORLD_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json"
MARKETS = (
    {"slug": "cape-town", "city": "Cape Town", "country": "South Africa", "continent": "Africa", "snapshot": "2026-06-29", "url": "https://data.insideairbnb.com/south-africa/wc/cape-town/2026-06-29/visualisations/listings.csv"},
    {"slug": "nairobi", "city": "Nairobi", "country": "Kenya", "continent": "Africa", "snapshot": "2026-06-15", "url": "https://data.insideairbnb.com/kenya/nairobi/nairobi/2026-06-15/visualisations/listings.csv"},
    {"slug": "bangkok", "city": "Bangkok", "country": "Thailand", "continent": "Asia", "snapshot": "2026-06-29", "url": "https://data.insideairbnb.com/thailand/central-thailand/bangkok/2026-06-29/visualisations/listings.csv"},
    {"slug": "istanbul", "city": "Istanbul", "country": "Türkiye", "continent": "Asia", "snapshot": "2026-06-30", "url": "https://data.insideairbnb.com/turkey/marmara/istanbul/2026-06-30/visualisations/listings.csv"},
    {"slug": "singapore", "city": "Singapore", "country": "Singapore", "continent": "Asia", "snapshot": "2026-06-29", "url": "https://data.insideairbnb.com/singapore/sg/singapore/2026-06-29/visualisations/listings.csv"},
    {"slug": "tokyo", "city": "Tokyo", "country": "Japan", "continent": "Asia", "snapshot": "2026-06-30", "url": "https://data.insideairbnb.com/japan/kant%C5%8D/tokyo/2026-06-30/visualisations/listings.csv"},
    {"slug": "london", "city": "London", "country": "United Kingdom", "continent": "Europe", "snapshot": "2026-06-19", "url": "https://data.insideairbnb.com/united-kingdom/england/london/2026-06-19/visualisations/listings.csv"},
    {"slug": "paris", "city": "Paris", "country": "France", "continent": "Europe", "snapshot": "2026-06-16", "url": "https://data.insideairbnb.com/france/ile-de-france/paris/2026-06-16/visualisations/listings.csv"},
    {"slug": "rome", "city": "Rome", "country": "Italy", "continent": "Europe", "snapshot": "2026-06-20", "url": "https://data.insideairbnb.com/italy/lazio/rome/2026-06-20/visualisations/listings.csv"},
    {"slug": "los-angeles", "city": "Los Angeles", "country": "United States", "continent": "North America", "snapshot": "2026-06-15", "url": "https://data.insideairbnb.com/united-states/ca/los-angeles/2026-06-15/visualisations/listings.csv"},
    {"slug": "mexico-city", "city": "Mexico City", "country": "Mexico", "continent": "North America", "snapshot": "2026-06-15", "url": "https://data.insideairbnb.com/mexico/df/mexico-city/2026-06-15/visualisations/listings.csv"},
    {"slug": "new-york-city", "city": "New York City", "country": "United States", "continent": "North America", "snapshot": "2026-08-10", "url": "https://data.insideairbnb.com/united-states/ny/new-york-city/2026-08-10/visualisations/listings.csv"},
    {"slug": "rio-de-janeiro", "city": "Rio de Janeiro", "country": "Brazil", "continent": "South America", "snapshot": "2026-06-24", "url": "https://data.insideairbnb.com/brazil/rj/rio-de-janeiro/2026-06-24/visualisations/listings.csv"},
    {"slug": "sao-paulo", "city": "São Paulo", "country": "Brazil", "continent": "South America", "snapshot": "2026-06-14", "url": "https://data.insideairbnb.com/brazil/sp/s%C3%A3o-paulo/2026-06-14/visualisations/listings.csv"},
    {"slug": "melbourne", "city": "Melbourne", "country": "Australia", "continent": "Oceania", "snapshot": "2026-06-16", "url": "https://data.insideairbnb.com/australia/vic/melbourne/2026-06-16/visualisations/listings.csv"},
    {"slug": "sydney", "city": "Sydney", "country": "Australia", "continent": "Oceania", "snapshot": "2026-06-16", "url": "https://data.insideairbnb.com/australia/nsw/sydney/2026-06-16/visualisations/listings.csv"},
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download_once(url: str, destination: Path) -> None:
    if destination.is_file() and destination.stat().st_size > 0:
        return
    if not url.startswith("https://"):
        raise ValueError(f"refusing non-HTTPS download: {url}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": USER_AGENT})
    partial = destination.with_suffix(destination.suffix + ".part")
    with urlopen(request, timeout=120) as response, partial.open("wb") as handle:
        while block := response.read(1024 * 1024):
            handle.write(block)
    partial.replace(destination)


def load_airbnb_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {"latitude", "longitude", "availability_365"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"invalid Inside Airbnb summary file: {path}")
    return rows


def build_overture_sql(boxes: list[dict[str, Any]], destination: Path) -> str:
    assignments = []
    conditions = []
    for box in boxes:
        south, west, north, east = box["bbox"]
        slug = str(box["slug"]).replace("'", "''")
        condition = (
            f"bbox.xmin BETWEEN {west} AND {east} "
            f"AND bbox.ymin BETWEEN {south} AND {north}"
        )
        assignments.append(f"WHEN {condition} THEN '{slug}'")
        conditions.append(f"({condition})")
    case_expression = "\n         ".join(assignments)
    spatial_filter = "\n      OR ".join(conditions)
    query = "\n".join(
        [
            "SELECT CASE",
            f"         {case_expression}",
            "       END AS slug,",
            "       id, names.primary AS hotel_name,",
            "       bbox.ymin AS latitude, bbox.xmin AS longitude,",
            "       confidence, operating_status, basic_category",
            f"FROM read_parquet('{OVERTURE_URI}', filename=true, hive_partitioning=1)",
            "WHERE (",
            f"      {spatial_filter}",
            "      )",
            "  AND (basic_category = 'hotel' OR list_contains(taxonomy.hierarchy, 'hotel'))",
            "  AND operating_status IS DISTINCT FROM 'permanently_closed'",
            "  AND coalesce(confidence, 0) >= 0.55",
        ]
    )
    escaped = str(destination).replace("'", "''")
    return "\n".join(
        [
            "INSTALL httpfs;",
            "LOAD httpfs;",
            "SET s3_region='us-west-2';",
            f"COPY ({query}) TO '{escaped}' (HEADER, DELIMITER ',');",
        ]
    )


def overture_download_command(box: dict[str, Any], destination: Path) -> list[str]:
    south, west, north, east = box["bbox"]
    return [
        "uvx",
        "--from",
        "overturemaps",
        "overturemaps",
        "download",
        f"--bbox={west},{south},{east},{north}",
        "-f",
        "geoparquet",
        "--type=place",
        f"--release={OVERTURE_RELEASE}",
        "--stac",
        f"--output={destination}",
    ]


def build_local_overture_sql(
    sources: list[tuple[str, Path]], destination: Path
) -> str:
    selects = []
    for slug, source in sources:
        safe_slug = slug.replace("'", "''")
        safe_source = str(source).replace("'", "''")
        selects.append(
            "\n".join(
                [
                    f"SELECT '{safe_slug}' AS slug, id, names.primary AS hotel_name,",
                    "       bbox.ymin AS latitude, bbox.xmin AS longitude,",
                    "       confidence, operating_status, basic_category",
                    f"FROM read_parquet('{safe_source}')",
                    "WHERE (basic_category = 'hotel' OR list_contains(taxonomy.hierarchy, 'hotel'))",
                    "  AND operating_status IS DISTINCT FROM 'permanently_closed'",
                    "  AND coalesce(confidence, 0) >= 0.55",
                ]
            )
        )
    safe_destination = str(destination).replace("'", "''")
    return (
        f"COPY ({' UNION ALL '.join(selects)}) TO '{safe_destination}' "
        "(HEADER, DELIMITER ',');"
    )


def query_overture(boxes: list[dict[str, Any]], destination: Path) -> None:
    if destination.is_file() and destination.stat().st_size > 0:
        return
    try:
        import duckdb
    except ImportError as error:
        raise RuntimeError(
            "DuckDB is required for Overture extraction; run with uv --with duckdb"
        ) from error
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(".part.csv")
    if partial.exists():
        partial.unlink()
    with tempfile.TemporaryDirectory(prefix="overture-hotels-") as temp_name:
        temp_dir = Path(temp_name)
        sources = [
            (str(box["slug"]), temp_dir / f"{box['slug']}.parquet") for box in boxes
        ]

        def download_market(item: tuple[dict[str, Any], tuple[str, Path]]) -> None:
            box, (_, path) = item
            subprocess.run(
                overture_download_command(box, path),
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        with ThreadPoolExecutor(max_workers=4) as executor:
            list(executor.map(download_market, zip(boxes, sources, strict=True)))

        sql = build_local_overture_sql(sources, partial)
        connection = duckdb.connect()
        try:
            connection.execute(sql)
        finally:
            connection.close()
    partial.replace(destination)


def hotel_counts(path: Path) -> dict[str, int]:
    counts = {str(market["slug"]): 0 for market in MARKETS}
    seen: dict[str, set[str]] = {slug: set() for slug in counts}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            slug = row.get("slug", "")
            if slug in seen and row.get("id"):
                seen[slug].add(row["id"])
    return {slug: len(ids) for slug, ids in seen.items()}


def manifest_entry(path: Path, *, source_url: str, role: str) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "role": role,
        "source_url": source_url,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def build(output_dir: Path) -> None:
    raw_airbnb = output_dir / "raw" / "inside-airbnb"
    raw_overture = output_dir / "raw" / "overture"
    raw_geometry = output_dir / "raw" / "geometry"
    output_dir.mkdir(parents=True, exist_ok=True)

    preliminary: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []
    for index, market in enumerate(MARKETS):
        csv_path = raw_airbnb / f"{market['slug']}-{market['snapshot']}.csv"
        existed = csv_path.exists()
        download_once(str(market["url"]), csv_path)
        rows = load_airbnb_rows(csv_path)
        preliminary.append(
            build_market_record(
                slug=str(market["slug"]),
                city=str(market["city"]),
                country=str(market["country"]),
                continent=str(market["continent"]),
                snapshot_date=str(market["snapshot"]),
                airbnb_rows=rows,
                hotel_properties=0,
            )
        )
        artifacts.append(
            manifest_entry(csv_path, source_url=str(market["url"]), role="airbnb_snapshot")
        )
        if not existed and index < len(MARKETS) - 1:
            time.sleep(6.2)

    hotels_path = raw_overture / f"hotels-{OVERTURE_RELEASE}.csv"
    query_overture(preliminary, hotels_path)
    counts = hotel_counts(hotels_path)
    artifacts.append(
        manifest_entry(hotels_path, source_url=OVERTURE_URI, role="hotel_extract")
    )

    markets = []
    for market, record in zip(MARKETS, preliminary, strict=True):
        record["hotel_properties"] = counts[str(market["slug"])]
        record["airbnb_per_hotel"] = round(
            record["airbnb_units"] / max(record["hotel_properties"], 1), 2
        )
        markets.append(record)
    for record, index in zip(markets, relative_presence_indices(markets), strict=True):
        record["relative_presence_index"] = index

    topology_path = raw_geometry / "countries-110m.json"
    download_once(WORLD_URL, topology_path)
    topology = json.loads(topology_path.read_text(encoding="utf-8"))
    if topology.get("type") != "Topology" or "countries" not in topology.get("objects", {}):
        raise ValueError("invalid world topology")
    artifacts.append(
        manifest_entry(topology_path, source_url=WORLD_URL, role="world_geometry")
    )

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    markets_path = output_dir / "markets.json"
    markets_path.write_text(json.dumps(markets, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    html_path = output_dir / "global-lodging-influence.html"
    html_path.write_text(
        render_html(markets, topology, generated_at=generated_at), encoding="utf-8"
    )
    artifacts.extend(
        [
            manifest_entry(markets_path, source_url="derived", role="market_model"),
            manifest_entry(html_path, source_url="derived", role="standalone_map"),
        ]
    )
    manifest = {
        "generated_at": generated_at,
        "model": "median-centered relative presence; not market share",
        "market_count": len(markets),
        "overture_release": OVERTURE_RELEASE,
        "artifacts": artifacts,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    validate_manifest(manifest)
    print(f"built {len(markets)} markets: {html_path}")


def verify(output_dir: Path) -> None:
    manifest_path = output_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    markets = json.loads((output_dir / "markets.json").read_text(encoding="utf-8"))
    if len(markets) != int(manifest["market_count"]):
        raise ValueError("market count does not match manifest")
    if any(market.get("relative_presence_index") is None for market in markets):
        raise ValueError("relative presence index is missing")
    print(f"verified {len(markets)} markets and {len(manifest['artifacts'])} artifacts")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if args.verify_only:
        verify(args.output_dir)
    else:
        build(args.output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
