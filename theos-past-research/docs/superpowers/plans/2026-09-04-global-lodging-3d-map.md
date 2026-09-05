# Global Lodging 3D Map Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce an auditable standalone HTML globe comparing Airbnb-derived active listings with mapped hotel establishments across 16 global markets.

**Architecture:** A dependency-free Python model module validates and aggregates cached source files, while one build script handles explicit downloads, Overture extraction, checksums, and HTML generation. The final document embeds the compact model and country geometry so interaction never fetches data at runtime; CDN scripts provide only the 3D rendering library.

**Tech Stack:** Python 3.12 standard library, pytest, DuckDB 1.1+ used ephemerally through `uv`, Globe.gl/Three.js from pinned CDN releases, HTML/CSS/JavaScript.

**Spec:** `docs/superpowers/specs/2026-09-04-global-lodging-3d-map-design.md`

## Global Constraints

- Never query or scrape Airbnb-controlled pages.
- Download each explicit Inside Airbnb CSV once and cache it.
- Query only Overture Places release `2026-08-19.0` bounding boxes required for the 16 selected markets.
- Do not call the metric market share; label it relative presence.
- Keep the standalone HTML self-contained for data and under 1 MB when possible.
- Attribute Inside Airbnb and Overture Maps in the finished map.

---

### Task 1: Lodging market model

**Files:**
- Create: `src/abnb_alt_data/lodging_map.py`
- Create: `tests/test_lodging_map.py`

**Interfaces:**
- Consumes: iterable dictionaries parsed from source CSV/GeoJSON rows.
- Produces: `active_airbnb_count(rows)`, `robust_market_bbox(rows)`, `is_hotel_place(place)`, `relative_presence_indices(markets)`, and `build_market_record(...)`.

- [ ] **Step 1: Write the failing tests**

```python
def test_active_airbnb_count_requires_current_signal():
    rows = [
        {"availability_365": "0", "number_of_reviews_ltm": "0"},
        {"availability_365": "8", "number_of_reviews_ltm": "0"},
        {"availability_365": "0", "number_of_reviews_ltm": "1"},
    ]
    assert active_airbnb_count(rows) == 2

def test_relative_presence_is_centered_on_sample_median():
    rows = [{"airbnb_units": 100, "hotel_properties": 10}, {"airbnb_units": 200, "hotel_properties": 10}, {"airbnb_units": 400, "hotel_properties": 10}]
    assert relative_presence_indices(rows) == [25.0, 50.0, 75.0]
```

- [ ] **Step 2: Run tests to verify RED**

Run: `pytest tests/test_lodging_map.py -q`
Expected: collection fails because `abnb_alt_data.lodging_map` does not exist.

- [ ] **Step 3: Implement the minimal model**

```python
def relative_presence_index(ratio: float, median_ratio: float) -> float:
    return round(max(0.0, min(100.0, 50.0 + 25.0 * math.log2(ratio / median_ratio))), 1)
```

- [ ] **Step 4: Run the model tests**

Run: `pytest tests/test_lodging_map.py -q`
Expected: all lodging-map tests pass.

### Task 2: Auditable source ingestion

**Files:**
- Create: `scripts/build_global_lodging_map.py`
- Modify: `tests/test_lodging_map.py`
- Modify: `research/source_registry.csv`
- Modify: `research/scraping_audit.csv`

**Interfaces:**
- Consumes: explicit Inside Airbnb CSV URLs and Overture GeoParquet release URI.
- Produces: cached raw files, `manifest.json`, `markets.json`, and deterministic inputs for the renderer.

- [ ] **Step 1: Add failing manifest and validation tests**

```python
def test_manifest_rejects_missing_sha256(tmp_path):
    with pytest.raises(ValueError, match="sha256"):
        validate_manifest({"artifacts": [{"path": str(tmp_path / "x.csv")}]})
```

- [ ] **Step 2: Run tests to verify RED**

Run: `pytest tests/test_lodging_map.py -q`
Expected: failure because manifest validation is not implemented.

- [ ] **Step 3: Implement explicit cached downloads and manifest validation**

Use `urllib.request.Request` with the repository user agent, refuse non-HTTPS URLs, never overwrite a valid cached artifact, and record byte size plus SHA-256. Invoke DuckDB once with all market bounding boxes and filter `list_contains(taxonomy.hierarchy, 'hotel')` plus `operating_status IS DISTINCT FROM 'permanently_closed'`.

- [ ] **Step 4: Run the ingestion tests**

Run: `pytest tests/test_lodging_map.py -q`
Expected: all tests pass without a network request.

### Task 3: Standalone 3D globe

**Files:**
- Modify: `scripts/build_global_lodging_map.py`
- Modify: `tests/test_lodging_map.py`
- Create at runtime: `outputs/01a06e7b-6c3c-7083-8038-ecfb7b421062/global-lodging-map/global-lodging-influence.html`

**Interfaces:**
- Consumes: serialized market model and bundled world country geometry.
- Produces: one responsive standalone HTML document.

- [ ] **Step 1: Add failing renderer-contract test**

```python
def test_rendered_html_embeds_data_without_runtime_data_fetch(sample_markets):
    html = render_html(sample_markets, {"type": "FeatureCollection", "features": []})
    assert "const MARKET_DATA =" in html
    assert "fetch(" not in html
    assert "Relative presence" in html
```

- [ ] **Step 2: Run tests to verify RED**

Run: `pytest tests/test_lodging_map.py -q`
Expected: failure because the renderer does not exist.

- [ ] **Step 3: Implement the renderer and interactions**

Embed market data and GeoJSON as JSON literals; configure Globe.gl beacons, hover labels, selection, continent filter, metric selector, reset, and reduced-motion-aware rotation. Use the palette and typography defined by the spec.

- [ ] **Step 4: Run unit and repository tests**

Run: `pytest tests/test_lodging_map.py -q && python scripts/validate_project.py`
Expected: all tests and repository validation pass.

### Task 4: Acquire, build, and verify

**Files:**
- Create at runtime: cached source files and final artifacts under `outputs/01a06e7b-6c3c-7083-8038-ecfb7b421062/global-lodging-map/`

**Interfaces:**
- Consumes: the implemented build CLI and public sources approved in the source registry.
- Produces: final HTML, `markets.json`, `manifest.json`, and cached raw data.

- [ ] **Step 1: Run the build**

Run: `uv run --with duckdb python scripts/build_global_lodging_map.py --output-dir outputs/01a06e7b-6c3c-7083-8038-ecfb7b421062/global-lodging-map`
Expected: 16 market records and a standalone HTML file.

- [ ] **Step 2: Verify artifacts and full tests**

Run: `python scripts/build_global_lodging_map.py --verify-only --output-dir outputs/01a06e7b-6c3c-7083-8038-ecfb7b421062/global-lodging-map && pytest -q`
Expected: checksum verification succeeds and the full test suite has zero failures.

- [ ] **Step 3: Inspect the rendered map**

Serve the output locally, open the exact map URL, confirm country geometry and all 16 beacons render, select at least two markets, change the continent filter and metric, and verify the responsive layout at desktop and mobile widths.
