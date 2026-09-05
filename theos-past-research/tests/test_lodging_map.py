from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys

import pytest

from abnb_alt_data.lodging_map import (
    active_airbnb_count,
    build_market_record,
    is_hotel_place,
    relative_presence_indices,
    render_html,
    robust_market_bbox,
    validate_manifest,
)


def test_active_airbnb_count_requires_current_signal() -> None:
    rows = [
        {"availability_365": "0", "number_of_reviews_ltm": "0"},
        {"availability_365": "8", "number_of_reviews_ltm": "0"},
        {"availability_365": "0", "number_of_reviews_ltm": "1"},
        {"availability_365": "", "number_of_reviews_ltm": ""},
    ]

    assert active_airbnb_count(rows) == 2


def test_robust_market_bbox_trims_single_extreme_outlier() -> None:
    rows = [
        {"latitude": str(40.0 + index / 100), "longitude": str(-74.0 + index / 100)}
        for index in range(20)
    ]
    rows.append({"latitude": "80", "longitude": "140"})

    south, west, north, east = robust_market_bbox(rows, padding_ratio=0.0)

    assert south == pytest.approx(40.01)
    assert west == pytest.approx(-73.99)
    assert north == pytest.approx(40.19)
    assert east == pytest.approx(-73.81)


def test_hotel_place_recognizes_taxonomy_and_excludes_closed() -> None:
    open_hotel = {
        "basic_category": "hotel",
        "taxonomy_hierarchy": ["lodging", "hotel", "boutique_hotel"],
        "operating_status": "open",
    }
    closed_hotel = {**open_hotel, "operating_status": "permanently_closed"}
    restaurant = {
        "basic_category": "restaurant",
        "taxonomy_hierarchy": ["food_and_drink", "restaurant"],
        "operating_status": "open",
    }

    assert is_hotel_place(open_hotel) is True
    assert is_hotel_place(closed_hotel) is False
    assert is_hotel_place(restaurant) is False


def test_relative_presence_is_centered_on_sample_median() -> None:
    markets = [
        {"airbnb_units": 100, "hotel_properties": 10},
        {"airbnb_units": 200, "hotel_properties": 10},
        {"airbnb_units": 400, "hotel_properties": 10},
    ]

    assert relative_presence_indices(markets) == [25.0, 50.0, 75.0]


def test_build_market_record_keeps_counts_comparable() -> None:
    record = build_market_record(
        slug="paris",
        city="Paris",
        country="France",
        continent="Europe",
        snapshot_date="2026-06-16",
        airbnb_rows=[
            {
                "availability_365": "10",
                "number_of_reviews_ltm": "0",
                "latitude": "48.85",
                "longitude": "2.35",
            },
            {
                "availability_365": "0",
                "number_of_reviews_ltm": "0",
                "latitude": "48.86",
                "longitude": "2.36",
            },
        ],
        hotel_properties=4,
    )

    assert record["airbnb_units"] == 1
    assert record["hotel_properties"] == 4
    assert record["airbnb_per_hotel"] == 0.25
    assert record["center"] == {"lat": 48.855, "lng": 2.355}


def test_manifest_rejects_missing_sha256(tmp_path: Path) -> None:
    artifact = tmp_path / "x.csv"
    artifact.write_text("x", encoding="utf-8")

    with pytest.raises(ValueError, match="sha256"):
        validate_manifest({"artifacts": [{"path": str(artifact)}]})


def test_manifest_accepts_matching_artifact(tmp_path: Path) -> None:
    artifact = tmp_path / "x.csv"
    artifact.write_bytes(b"lodging")
    digest = hashlib.sha256(b"lodging").hexdigest()

    validate_manifest(
        {
            "artifacts": [
                {"path": str(artifact), "bytes": 7, "sha256": digest}
            ]
        }
    )


def test_rendered_html_embeds_data_without_runtime_data_fetch() -> None:
    markets = [
        {
            "slug": "paris",
            "city": "Paris",
            "country": "France",
            "continent": "Europe",
            "snapshot_date": "2026-06-16",
            "airbnb_units": 100,
            "hotel_properties": 20,
            "airbnb_per_hotel": 5.0,
            "relative_presence_index": 50.0,
            "center": {"lat": 48.85, "lng": 2.35},
            "bbox": [48.7, 2.1, 49.0, 2.6],
        }
    ]
    topology = {"type": "Topology", "objects": {}, "arcs": []}

    html = render_html(markets, topology, generated_at="2026-09-04T00:00:00Z")

    assert "const MARKET_DATA =" in html
    assert "const WORLD_TOPOLOGY =" in html
    assert "fetch(" not in html
    assert "Relative presence" in html
    assert "Source-covered markets" in html
    assert "Paris" in html


def test_overture_sql_scans_remote_source_once(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_global_lodging_map.py"
    spec = importlib.util.spec_from_file_location("global_lodging_map_script", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    boxes = [
        {"slug": "alpha", "bbox": [1.0, 2.0, 3.0, 4.0]},
        {"slug": "beta", "bbox": [5.0, 6.0, 7.0, 8.0]},
    ]

    sql = module.build_overture_sql(boxes, tmp_path / "hotels.csv")

    assert sql.count("read_parquet(") == 1
    assert "WHEN bbox.xmin BETWEEN 2.0 AND 4.0" in sql
    assert "WHEN bbox.xmin BETWEEN 6.0 AND 8.0" in sql


def test_overture_download_command_uses_spatial_indexed_bbox(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "build_global_lodging_map.py"
    spec = importlib.util.spec_from_file_location("global_lodging_map_download", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    command = module.overture_download_command(
        {"bbox": [48.81, 2.26, 48.92, 2.42]}, tmp_path / "paris.parquet"
    )

    assert command[:4] == ["uvx", "--from", "overturemaps", "overturemaps"]
    assert "--bbox=2.26,48.81,2.42,48.92" in command
    assert "--stac" in command
    assert "-f" in command
    assert "geoparquet" in command
    assert "--format=geoparquet" not in command
    assert "--type=place" in command
    assert "--release=2026-08-19.0" in command
