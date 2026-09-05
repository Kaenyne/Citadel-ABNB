"""Model and render a transparent Airbnb-versus-hotel presence map."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from statistics import median
from typing import Any, Iterable, Mapping, MutableMapping, Sequence


def _number(value: object, default: float = 0.0) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def active_airbnb_count(rows: Iterable[Mapping[str, object]]) -> int:
    """Count listings with current availability or a recent review signal."""
    return sum(
        1
        for row in rows
        if _number(row.get("availability_365")) > 0
        or _number(row.get("number_of_reviews_ltm")) > 0
    )


def _trimmed_limits(values: Sequence[float]) -> tuple[float, float]:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("market rows contain no valid coordinates")
    if len(ordered) < 20:
        return ordered[0], ordered[-1]
    lower_index = math.floor((len(ordered) - 1) * 0.05)
    upper_index = math.ceil((len(ordered) - 1) * 0.95)
    return ordered[lower_index], ordered[upper_index]


def robust_market_bbox(
    rows: Iterable[Mapping[str, object]], *, padding_ratio: float = 0.08
) -> tuple[float, float, float, float]:
    """Return a 5th–95th percentile market box with proportional padding."""
    coordinates: list[tuple[float, float]] = []
    for row in rows:
        latitude = _number(row.get("latitude"), math.nan)
        longitude = _number(row.get("longitude"), math.nan)
        if math.isfinite(latitude) and math.isfinite(longitude):
            if -90 <= latitude <= 90 and -180 <= longitude <= 180:
                coordinates.append((latitude, longitude))
    if not coordinates:
        raise ValueError("market rows contain no valid coordinates")

    south, north = _trimmed_limits([pair[0] for pair in coordinates])
    west, east = _trimmed_limits([pair[1] for pair in coordinates])
    lat_padding = max((north - south) * padding_ratio, 0.02)
    lon_padding = max((east - west) * padding_ratio, 0.02)
    if padding_ratio == 0:
        lat_padding = 0.0
        lon_padding = 0.0
    return (
        round(max(-90.0, south - lat_padding), 6),
        round(max(-180.0, west - lon_padding), 6),
        round(min(90.0, north + lat_padding), 6),
        round(min(180.0, east + lon_padding), 6),
    )


def is_hotel_place(place: Mapping[str, object]) -> bool:
    """Recognize an open hotel from normalized Overture place fields."""
    if place.get("operating_status") == "permanently_closed":
        return False
    hierarchy = place.get("taxonomy_hierarchy") or []
    if not isinstance(hierarchy, (list, tuple)):
        hierarchy = []
    return place.get("basic_category") == "hotel" or "hotel" in hierarchy


def relative_presence_indices(
    markets: Sequence[MutableMapping[str, Any]],
) -> list[float]:
    """Return median-centered log-ratio indices for comparable markets."""
    if not markets:
        return []
    ratios = [
        max(_number(market.get("airbnb_units")), 0.0)
        / max(_number(market.get("hotel_properties")), 1.0)
        for market in markets
    ]
    positive = [ratio for ratio in ratios if ratio > 0]
    baseline = median(positive) if positive else 1.0
    return [
        round(
            max(
                0.0,
                min(
                    100.0,
                    50.0 + 25.0 * math.log2(max(ratio, 1e-9) / baseline),
                ),
            ),
            1,
        )
        for ratio in ratios
    ]


def build_market_record(
    *,
    slug: str,
    city: str,
    country: str,
    continent: str,
    snapshot_date: str,
    airbnb_rows: Sequence[Mapping[str, object]],
    hotel_properties: int,
) -> dict[str, Any]:
    """Aggregate one market while retaining its comparable footprint."""
    coordinates = [
        (_number(row.get("latitude"), math.nan), _number(row.get("longitude"), math.nan))
        for row in airbnb_rows
    ]
    coordinates = [
        pair
        for pair in coordinates
        if math.isfinite(pair[0])
        and math.isfinite(pair[1])
        and -90 <= pair[0] <= 90
        and -180 <= pair[1] <= 180
    ]
    if not coordinates:
        raise ValueError(f"{city} contains no valid coordinates")
    airbnb_units = active_airbnb_count(airbnb_rows)
    hotels = max(int(hotel_properties), 0)
    return {
        "slug": slug,
        "city": city,
        "country": country,
        "continent": continent,
        "snapshot_date": snapshot_date,
        "airbnb_units": airbnb_units,
        "hotel_properties": hotels,
        "airbnb_per_hotel": round(airbnb_units / max(hotels, 1), 2),
        "center": {
            "lat": round(median(pair[0] for pair in coordinates), 5),
            "lng": round(median(pair[1] for pair in coordinates), 5),
        },
        "bbox": list(robust_market_bbox(airbnb_rows)),
    }


def validate_manifest(manifest: Mapping[str, object]) -> None:
    """Validate that every cached artifact exists and matches its manifest."""
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("manifest artifacts are missing")
    for entry in artifacts:
        if not isinstance(entry, Mapping):
            raise ValueError("manifest artifact entry is invalid")
        path = Path(str(entry.get("path", "")))
        expected_digest = str(entry.get("sha256", ""))
        if len(expected_digest) != 64:
            raise ValueError(f"sha256 is missing for {path}")
        if not path.is_file():
            raise ValueError(f"artifact is missing: {path}")
        payload = path.read_bytes()
        if len(payload) != int(entry.get("bytes", -1)):
            raise ValueError(f"byte size mismatch for {path}")
        if hashlib.sha256(payload).hexdigest() != expected_digest:
            raise ValueError(f"sha256 mismatch for {path}")


def _safe_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )


def render_html(
    markets: Sequence[Mapping[str, object]],
    world_topology: Mapping[str, object],
    *,
    generated_at: str,
) -> str:
    """Render the complete standalone 3D globe document."""
    market_json = _safe_json(markets)
    topology_json = _safe_json(world_topology)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Airbnb-derived active listings compared with Overture hotel establishments across source-covered global markets.">
  <title>Global lodging currents</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Manrope:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      color-scheme: dark;
      --abyss: #07131f;
      --bathymetry: #10283b;
      --hotel: #47b8e8;
      --balance: #9673ff;
      --airbnb: #ff6b5f;
      --parchment: #edf4f7;
      --muted: #9bb0bd;
      --line: rgba(155, 176, 189, .24);
      --glass: rgba(7, 19, 31, .78);
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; min-height: 100%; background: var(--abyss); color: var(--parchment); }}
    body {{
      font-family: "Manrope", sans-serif;
      background:
        radial-gradient(circle at 35% 45%, rgba(71, 184, 232, .12), transparent 28rem),
        linear-gradient(145deg, #07131f 0%, #06101a 65%, #0b1d2b 100%);
    }}
    button, select {{ font: inherit; }}
    .app {{ min-height: 100vh; display: grid; grid-template-rows: auto minmax(0, 1fr) auto; }}
    header {{
      display: flex; align-items: end; justify-content: space-between; gap: 1.5rem;
      padding: 1.25rem 1.5rem .75rem; border-bottom: 1px solid var(--line);
    }}
    h1 {{ font-family: "DM Serif Display", Georgia, serif; font-size: clamp(1.8rem, 4vw, 3.45rem); font-weight: 400; margin: 0; letter-spacing: -.025em; }}
    .dek {{ color: var(--muted); max-width: 38rem; margin: 0; line-height: 1.55; font-size: .83rem; }}
    main {{ min-height: 0; display: grid; grid-template-columns: minmax(0, 1fr) 20rem; }}
    .globe-shell {{ min-width: 0; min-height: 36rem; position: relative; overflow: hidden; }}
    #globe {{ position: absolute; inset: 0; }}
    #globe canvas {{ outline: none; }}
    .legend {{
      position: absolute; left: 1.5rem; bottom: 1rem; z-index: 2;
      display: flex; gap: .65rem; align-items: center; padding: .55rem .7rem;
      background: rgba(7, 19, 31, .72); backdrop-filter: blur(12px); border: 1px solid var(--line);
      border-radius: .35rem; font-size: .72rem; color: var(--muted);
    }}
    .gradient {{ width: 7rem; height: .42rem; background: linear-gradient(90deg, var(--hotel), var(--balance), var(--airbnb)); border-radius: 99px; }}
    aside {{
      border-left: 1px solid var(--line); padding: 1.25rem; background: linear-gradient(180deg, rgba(16, 40, 59, .45), rgba(7, 19, 31, .7));
      display: flex; flex-direction: column; gap: 1.15rem;
    }}
    .controls {{ display: grid; gap: .8rem; }}
    label {{ display: grid; gap: .35rem; color: var(--muted); font-size: .72rem; }}
    select, button {{
      color: var(--parchment); background: rgba(7, 19, 31, .74); border: 1px solid var(--line);
      border-radius: .3rem; padding: .68rem .75rem;
    }}
    button {{ cursor: pointer; text-align: left; }}
    button:hover, select:hover {{ border-color: rgba(237, 244, 247, .5); }}
    button:focus-visible, select:focus-visible {{ outline: 2px solid var(--hotel); outline-offset: 2px; }}
    .button-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: .55rem; }}
    .readout {{ border-top: 1px solid var(--line); padding-top: 1rem; }}
    .readout h2 {{ font-family: "DM Serif Display", Georgia, serif; font-size: 1.7rem; font-weight: 400; margin: 0 0 .1rem; }}
    .country {{ color: var(--muted); font-size: .78rem; margin: 0 0 1rem; }}
    .dial {{ display: flex; align-items: baseline; gap: .55rem; margin-bottom: .9rem; }}
    .dial strong {{ font-family: "DM Serif Display", Georgia, serif; font-size: 3.4rem; font-weight: 400; line-height: 1; }}
    .dial span {{ color: var(--muted); font-size: .72rem; max-width: 7rem; }}
    dl {{ margin: 0; display: grid; grid-template-columns: 1fr auto; gap: .55rem .8rem; font-size: .78rem; }}
    dt {{ color: var(--muted); }} dd {{ margin: 0; font-variant-numeric: tabular-nums; }}
    .method {{ margin-top: auto; color: var(--muted); font-size: .68rem; line-height: 1.55; }}
    .method strong {{ color: var(--parchment); font-weight: 500; }}
    footer {{
      display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
      padding: .65rem 1.5rem; border-top: 1px solid var(--line); color: var(--muted); font-size: .64rem;
    }}
    footer a {{ color: var(--parchment); }}
    .sr-only {{ position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }}
    @media (max-width: 760px) {{
      header {{ align-items: start; flex-direction: column; }}
      main {{ grid-template-columns: 1fr; }}
      .globe-shell {{ min-height: 31rem; }}
      aside {{ border-left: 0; border-top: 1px solid var(--line); }}
      .method {{ margin-top: .5rem; }}
    }}
  </style>
</head>
<body>
  <div class="app">
    <header>
      <h1>Global lodging currents</h1>
      <p class="dek">Airbnb-derived active listings against mapped hotel establishments. Beacon height shows observed lodging presence; color shows which form is relatively stronger.</p>
    </header>
    <main>
      <section class="globe-shell" aria-label="Interactive three-dimensional lodging map">
        <div id="globe" role="img" aria-label="Rotatable globe with lodging market beacons"></div>
        <div class="legend" aria-label="Relative presence legend">
          <span>Hotels</span><span class="gradient" aria-hidden="true"></span><span>Airbnb</span>
        </div>
      </section>
      <aside>
        <div class="controls" aria-label="Map controls">
          <label>Beacon height
            <select id="metric">
              <option value="total">Observed lodging presence</option>
              <option value="airbnb">Active Airbnb listings</option>
              <option value="hotel">Hotel establishments</option>
            </select>
          </label>
          <label>Source-covered markets
            <select id="continent"><option value="All">All continents</option></select>
          </label>
          <div class="button-row">
            <button id="rotate" type="button" aria-pressed="true">Pause rotation</button>
            <button id="reset" type="button">Reset view</button>
          </div>
        </div>
        <section class="readout" aria-live="polite">
          <h2 id="city">Select a beacon</h2>
          <p class="country" id="country">Drag to rotate · scroll to zoom</p>
          <div class="dial"><strong id="index">—</strong><span>Relative presence index</span></div>
          <dl>
            <dt>Active Airbnb listings</dt><dd id="airbnb">—</dd>
            <dt>Hotel establishments</dt><dd id="hotels">—</dd>
            <dt>Listings per hotel</dt><dd id="ratio">—</dd>
            <dt>Airbnb snapshot</dt><dd id="snapshot">—</dd>
          </dl>
        </section>
        <p class="method"><strong>How to read it.</strong> Relative presence is median-centered across these markets: 50 is the sample median. It compares active listings with hotel properties—not rooms, bookings, revenue, occupancy, or market share. Market boxes are trimmed Airbnb footprints; source coverage is uneven.</p>
      </aside>
    </main>
    <footer>
      <span>Generated {generated_at} · 16 source-covered markets · Overture release 2026-08-19.0</span>
      <span>Data: <a href="https://insideairbnb.com/get-the-data/">Inside Airbnb</a> · <a href="https://overturemaps.org/">Overture Maps Foundation</a></span>
    </footer>
  </div>
  <p class="sr-only" id="map-summary">Source-covered markets are shown as colored vertical beacons on a rotatable globe.</p>
  <script src="https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/globe.gl@2.45.0/dist/globe.gl.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js"></script>
  <script>
    const MARKET_DATA = {market_json};
    const WORLD_TOPOLOGY = {topology_json};
    const palette = {{ hotel: '#47b8e8', balance: '#9673ff', airbnb: '#ff6b5f' }};
    const root = document.getElementById('globe');
    const metric = document.getElementById('metric');
    const continent = document.getElementById('continent');
    const rotateButton = document.getElementById('rotate');
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const countries = WORLD_TOPOLOGY.objects.countries
      ? topojson.feature(WORLD_TOPOLOGY, WORLD_TOPOLOGY.objects.countries).features
      : [];
    const formatter = new Intl.NumberFormat('en-US');

    function mix(start, end, amount) {{
      const a = start.match(/\\w\\w/g).map(hex => parseInt(hex, 16));
      const b = end.match(/\\w\\w/g).map(hex => parseInt(hex, 16));
      return '#' + a.map((value, i) => Math.round(value + (b[i] - value) * amount).toString(16).padStart(2, '0')).join('');
    }}
    function colorFor(index) {{
      return index <= 50 ? mix(palette.hotel, palette.balance, index / 50) : mix(palette.balance, palette.airbnb, (index - 50) / 50);
    }}
    function metricValue(row) {{
      if (metric.value === 'airbnb') return row.airbnb_units;
      if (metric.value === 'hotel') return row.hotel_properties;
      return row.airbnb_units + row.hotel_properties;
    }}
    function visibleMarkets() {{
      return MARKET_DATA.filter(row => continent.value === 'All' || row.continent === continent.value);
    }}
    function pointHeight(row) {{
      const visible = visibleMarkets();
      const values = visible.map(metricValue);
      const maximum = Math.max(...values, 1);
      return .035 + .38 * Math.log1p(metricValue(row)) / Math.log1p(maximum);
    }}
    function selectMarket(row) {{
      document.getElementById('city').textContent = row.city;
      document.getElementById('country').textContent = `${{row.country}} · ${{row.continent}}`;
      document.getElementById('index').textContent = row.relative_presence_index.toFixed(1);
      document.getElementById('index').style.color = colorFor(row.relative_presence_index);
      document.getElementById('airbnb').textContent = formatter.format(row.airbnb_units);
      document.getElementById('hotels').textContent = formatter.format(row.hotel_properties);
      document.getElementById('ratio').textContent = row.airbnb_per_hotel.toFixed(2);
      document.getElementById('snapshot').textContent = row.snapshot_date;
    }}

    [...new Set(MARKET_DATA.map(row => row.continent))].sort().forEach(name => {{
      const option = document.createElement('option');
      option.value = name;
      option.textContent = name;
      continent.appendChild(option);
    }});

    const globe = Globe()(root)
      .backgroundColor('rgba(0,0,0,0)')
      .showAtmosphere(true)
      .atmosphereColor('#47b8e8')
      .atmosphereAltitude(.14)
      .polygonsData(countries)
      .polygonCapColor(() => 'rgba(16,40,59,.72)')
      .polygonSideColor(() => 'rgba(7,19,31,.22)')
      .polygonStrokeColor(() => 'rgba(155,176,189,.25)')
      .polygonAltitude(.008)
      .pointsData(MARKET_DATA)
      .pointLat(row => row.center.lat)
      .pointLng(row => row.center.lng)
      .pointAltitude(pointHeight)
      .pointRadius(.42)
      .pointColor(row => colorFor(row.relative_presence_index))
      .pointLabel(row => `<strong>${{row.city}}</strong><br>${{formatter.format(row.airbnb_units)}} Airbnb · ${{formatter.format(row.hotel_properties)}} hotels`)
      .onPointClick(row => {{
        selectMarket(row);
        globe.pointOfView({{ lat: row.center.lat, lng: row.center.lng, altitude: 1.55 }}, prefersReducedMotion ? 0 : 750);
      }});

    function sizeGlobe() {{
      globe.width(root.clientWidth).height(root.clientHeight);
    }}
    new ResizeObserver(sizeGlobe).observe(root);
    sizeGlobe();
    globe.controls().autoRotate = !prefersReducedMotion;
    globe.controls().autoRotateSpeed = .38;
    rotateButton.textContent = prefersReducedMotion ? 'Start rotation' : 'Pause rotation';
    rotateButton.setAttribute('aria-pressed', String(!prefersReducedMotion));
    selectMarket(MARKET_DATA[0]);

    function refreshPoints() {{
      globe.pointsData(visibleMarkets()).pointAltitude(pointHeight);
      const first = visibleMarkets()[0];
      if (first) selectMarket(first);
    }}
    metric.addEventListener('change', refreshPoints);
    continent.addEventListener('change', refreshPoints);
    rotateButton.addEventListener('click', () => {{
      globe.controls().autoRotate = !globe.controls().autoRotate;
      rotateButton.setAttribute('aria-pressed', String(globe.controls().autoRotate));
      rotateButton.textContent = globe.controls().autoRotate ? 'Pause rotation' : 'Start rotation';
    }});
    document.getElementById('reset').addEventListener('click', () => {{
      globe.pointOfView({{ lat: 16, lng: 0, altitude: 2.15 }}, prefersReducedMotion ? 0 : 800);
    }});
  </script>
</body>
</html>
"""
