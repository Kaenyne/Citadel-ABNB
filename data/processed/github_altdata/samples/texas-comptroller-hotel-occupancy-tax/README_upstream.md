# TX Hotel Heatmap

A full-screen CRE mapping tool that plots Texas hotels by **RevPAR** (revenue per
available room), built from Texas Comptroller hotel-occupancy-tax data. Hotels are
bucketed red / yellow / gray by RevPAR percentile and rendered as clustered colored
pins or a true Google Maps density heatmap.

**Requires a Google Maps API key** (Maps JavaScript API + Geocoding API).

![stack](https://img.shields.io/badge/Next.js-14-black) ![stack](https://img.shields.io/badge/Google%20Maps-JS%20API-green) ![stack](https://img.shields.io/badge/@vis.gl-react--google--maps-blue)

## Features

- **Full-screen Google Map** centered on Texas (Roadmap / Satellite / Terrain),
  with clustering via @googlemaps/markerclusterer.
- **Colored markers by RevPAR bucket** — red (top third), yellow (middle third),
  gray (bottom third + missing data). Points cluster when zoomed out and expand
  on click.
- **Property card** — click any hotel for a CRE-style card: photo, name, address,
  `{rooms} Rooms · Hospitality`, RevPAR, ADR, and occupancy.
- **Heatmap layer** — the left-rail *Layers* button toggles between colored pins
  and a Google Maps (visualization) density heatmap weighted by RevPAR.
- **Filter + legend** — the legend doubles as a filter: tap a bucket to show only
  red / yellow / gray hotels.
- **Tool rail** — Location (recenter), Polygon, Radius, Layers, Map type. Zoom and
  compass controls sit bottom-right.

## Quick start

```bash
npm install
cp .env.local.example .env.local   # add your Google Maps API key(s)
npm run build-data                 # generates public/hotels.geojson
npm run dev                        # http://localhost:3000
```

## Environment variables

| Variable | Where | Purpose |
| --- | --- | --- |
| `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` | browser (build + runtime) | Renders the Google map. Needs **Maps JavaScript API**. Ships to the client — **restrict it by HTTP referrer** in Google Cloud. |
| `GOOGLE_GEOCODING_API_KEY` | `build-data` script only | Rooftop geocoding via the **Geocoding API**. Server-side only; can be the same key or a separate IP-restricted one. Falls back to the free US Census geocoder if unset. |

> **On Vercel:** add `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` under Project → Settings →
> Environment Variables (Production + Preview). Without it the app shows a
> "Google Maps key missing" notice.

## Data pipeline

`/data/hotels.csv` is the input file — drop the Box **"Texan Hotel Analytics"**
export there (the Texas Comptroller hotel-occupancy-tax CSV: taxpayer + location
columns, `Rooms`, `Revenue`, `RevPAR`). Then:

```bash
npm run build-data
```

`scripts/build-data.ts`:

1. **Parses** `data/hotels.csv`, resolving columns by name so it tolerates other
   export shapes (hotel name, address, city, state, zip, rooms, room revenue, and
   ADR/occupancy if present).
2. **Computes RevPAR** — uses the `RevPAR` column when present, otherwise derives
   `revenue / (rooms × daysInPeriod)`. Rows missing key inputs are `flagged`.
3. **Geocodes** any hotel without lat/lng and caches results (per-geocoder cache
   file) so reruns never re-hit the API. Geocoders:
   - **Google** (default when a Google key is set) — rooftop accuracy via the
     Geocoding API. Pins land on the actual building.
   - **Mapbox** (`GEOCODER=mapbox`) — via the Mapbox Geocoding API (needs a token).
   - **US Census batch** (`GEOCODER=census`) — free, no key, but street-level
     (interpolated); pins can be ~100m–1km off.
4. **Buckets** every hotel red / yellow / gray by RevPAR percentile across the
   portfolio (top third red, middle yellow, bottom third + no-data gray).
5. **Writes** `public/hotels.geojson` with `name, address, rooms, revpar, adr,
   occupancy, revenue, bucket, photo, flagged` properties.

All thresholds live in a `CONFIG` object at the top of the script:

```ts
const CONFIG = {
  daysInPeriod: 31,
  bucketPercentiles: { red: 0.6667, yellow: 0.3333 }, // tune the red/yellow cutoffs
  stateFilter: "TX",
  // ...
};
```

Useful flags:

```bash
npm run build-data                        # Google if a key is set, else Census
GEOCODER=census npm run build-data        # force the free Census geocoder
npm run build-data -- --google            # force Google (rooftop)
npm run build-data -- --limit 200         # only the first 200 rows (quick test)
npm run build-data -- --no-geocode        # use the cache only, skip API calls
npm run build-history                     # recompute RevPAR + trend from data/periods/
```

`build-history` is the source of truth for RevPAR. It reads the per-period
Comptroller files in `data/periods/` and writes two **per-night** figures:

- **T12 RevPAR** = trailing-12-month revenue ÷ rooms ÷ 365 (last four complete
  quarters). This is the headline metric the heatmap buckets, filters, and
  sorts on (`properties.revpar`).
- **Last-month RevPAR** = the latest reported month's revenue ÷ rooms ÷
  days-in-month (`properties.lastMonthRevpar`).

Run `build-data` first (geocoding + base geojson), then `build-history` to lay
the correct RevPAR on top.

### Notes on this dataset

- The Comptroller files report revenue **per period** — a single month for the
  monthly files, a quarter for the quarterly files — but their `RevPAR` column
  always divides by 90 days. `build-history` ignores that column and recomputes
  RevPAR per night from the raw revenue on the correct day count.
- The export has **no ADR, occupancy, lat/lng, or photo** columns — those render
  as "—"/no-photo. The pipeline still supports them for richer exports.
- `data/hotels.csv` and `data/geocache.json` are git-ignored (large / owner PII).
  The generated `public/hotels.geojson` **is** committed so Vercel renders without
  needing a geocoding step at deploy time.

## Deploy (Vercel)

This repo is set up for Vercel auto-deploy: push to `main` and Vercel builds and
deploys. Set `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` in the project's environment
variables so the deployed map renders.

## Tech

Next.js 14 (App Router, TypeScript) · Tailwind CSS · @vis.gl/react-google-maps +
Google Maps JS API · @googlemaps/markerclusterer · `tsx` for the data pipeline.
