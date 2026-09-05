# Global Lodging 3D Map Design

## Objective

Build a standalone interactive HTML globe that compares Airbnb-derived short-term-rental presence with hotel presence across a transparent, cross-continental sample of markets.

## Scope and data

- Use one current summary `listings.csv` snapshot for each selected Inside Airbnb market. Download each explicit file once and cache it locally. Do not crawl Airbnb or recursively scrape Inside Airbnb.
- Cover 16 markets across Africa, Asia, Europe, North America, South America, and Oceania. Label the result as a source-covered market sample, not as exhaustive worldwide Airbnb inventory.
- Use Overture Maps Places release `2026-08-19.0` for hotel establishments. Query only the bounding box derived from each corresponding Airbnb market and retain places whose taxonomy hierarchy contains `hotel`, excluding permanently closed places.
- Preserve raw downloads, request metadata, collection timestamps, and SHA-256 checksums in the run directory.

## Model

An active Airbnb unit is a listing with positive availability in the next 365 days or at least one review in the last twelve months. Hotel presence is the number of distinct Overture hotel establishments in the comparable market bounding box.

The map must not present listing counts and hotel establishments as equivalent rooms. Its comparison metric is a relative-presence index:

1. Calculate each market's Airbnb-units-per-hotel ratio.
2. Calculate the median ratio across all covered markets.
3. Define `index = 50 + 25 × log2(market ratio / median ratio)`, clipped to `[0, 100]`.

An index of 50 therefore means the covered-market median. Higher values mean Airbnb is more prevalent relative to mapped hotel establishments; lower values mean hotels are more prevalent. It is not booking, revenue, occupancy, or market share.

## Experience

The first viewport is a full 3D globe. Each market appears as a vertical beacon whose height encodes total observed lodging presence and whose color encodes the relative-presence index from hotel blue through balanced violet to Airbnb coral. Selecting a beacon opens one compact detail panel containing the two source counts, ratio, index, snapshot dates, and geographic footprint.

Controls are limited to a metric selector, continent filter, auto-rotate toggle, and reset-view action. A concise legend and methodology disclosure remain visible. The layout must work at desktop and mobile widths, support keyboard controls, honor reduced-motion preferences, and include source attribution.

## Visual direction

- Palette: abyss `#07131f`, bathymetry `#10283b`, hotel current `#47b8e8`, balance `#9673ff`, Airbnb current `#ff6b5f`, parchment `#edf4f7`.
- Type: `Manrope` for interface text and `DM Serif Display` for the restrained editorial title.
- Layout: the globe dominates; a narrow, translucent navigation-instrument rail holds controls and the selected-market readout.
- Distinctive motif: market beacons read like depth soundings on a navigational globe, fitting a geographic market-intelligence instrument rather than a generic dashboard.

## Validation

- Unit-test active-listing classification, robust bounding boxes, hotel-category recognition, median-relative index behavior, and model serialization.
- Validate every downloaded CSV/GeoJSON before use and checksum every raw artifact.
- Verify the generated HTML contains no external data requests, contains all model rows inline, and renders a nonblank globe with working selection/filter controls.
