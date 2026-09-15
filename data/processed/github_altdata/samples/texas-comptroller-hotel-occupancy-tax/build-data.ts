/**
 * build-data.ts — Texas hotel RevPAR pipeline.
 *
 * Reads the Texas Comptroller hotel-occupancy-tax export (data/hotels.csv),
 * computes/normalizes RevPAR, geocodes each hotel, buckets it by RevPAR
 * percentile, and writes public/hotels.geojson for the map to render.
 *
 *   npm run build-data                 # geocode via Mapbox if a token is set, else Census
 *   GEOCODER=census npm run build-data # force the free, no-key US Census batch geocoder
 *   npm run build-data -- --limit 200  # only process the first 200 rows (quick test)
 *   npm run build-data -- --no-geocode # skip geocoding entirely (use cache only)
 *
 * Reruns reuse data/geocache.json so we never re-hit a geocoding API for an
 * address we've already resolved.
 */

import { parse } from "csv-parse/sync";
import * as fs from "node:fs";
import * as path from "node:path";
import * as dotenv from "dotenv";

dotenv.config({ path: ".env.local" });
dotenv.config();

// ---------------------------------------------------------------------------
// CONFIG — tune these.
// ---------------------------------------------------------------------------
const CONFIG = {
  inputCsv: "data/hotels.csv",
  outputGeojson: "public/hotels.geojson",
  geocacheFile: "data/geocache.json",

  // Only keep hotels physically located in this state (set to null to keep all).
  stateFilter: "TX",

  // Days in the source file's reporting period. data/hotels.csv is the latest
  // single MONTH (currently May, 31 days), so this is the per-night divisor for
  // the provisional RevPAR computed here. NOTE: build-history.mjs runs after
  // this and REPLACES properties.revpar with the headline T12 RevPAR
  // (trailing-12mo revenue / rooms / 365); the value set here only stands in if
  // build-history is never run.
  daysInPeriod: 31,

  // Data-quality guards. The Comptroller file is full of aggregate / non-hotel
  // filers that pollute "top performers" and skew the percentile cutoffs:
  //   - city/county tax-collection rollups ("CITY OF GALVESTON")
  //   - 1-room placeholder filings where rooms is a stand-in, not a count
  //   - implausible RevPAR (a real TX hotel tops out near $15k/mo per room)
  // Government rollups are dropped entirely; the others have RevPAR nulled
  // (-> gray, sinks to the bottom of the list) rather than removed.
  excludeNamePattern: /^\s*(city|county|town|village|state)\s+of\b/i,
  minRooms: 2, // 1-room filings are placeholders, not real room counts

  // The site only shows real hotels, defined as MORE THAN this many rooms.
  // The Comptroller file is mostly sub-scale filers (vacation rentals, single
  // condos, RV sites, B&Bs) — dropping <= this count removes ~half the rows
  // while keeping essentially every branded/real hotel.
  dropAtOrUnderRooms: 10,
  maxRevpar: 2000, // per-night RevPAR ceiling ($/room/night) — rejects data errors



  // RevPAR bucket cutoffs, expressed as percentiles of the portfolio's RevPAR
  // distribution. >= red cutoff -> red (top third); >= yellow cutoff -> yellow
  // (middle third); everything else, plus missing data -> gray (bottom third).
  bucketPercentiles: {
    red: 0.6667, // top third
    yellow: 0.3333, // middle third
  },

  // "google" (rooftop, needs a key), "mapbox" (needs a token), or "census" (free
  // US Census batch geocoder, no key). Defaults to google when a Google key is
  // set, else mapbox when a Mapbox token is set, else census.
  geocoder:
    (process.env.GEOCODER as "google" | "mapbox" | "census" | undefined) ??
    null,

  googleKey:
    process.env.GOOGLE_GEOCODING_API_KEY ||
    process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY ||
    "",
  googleConcurrency: 12,

  // Rooftop refinement (keyless): the Census geocoder only interpolates along
  // street centerlines, so pins land ~100m–1km off the actual building. Photon
  // (Komoot, OpenStreetMap, no key) is queried by hotel NAME + address, anchored
  // to the Census coordinate. A refined point is accepted only when it's a
  // building/lodging POI within `photonAcceptKm` of the anchor — otherwise we
  // keep the Census coordinate. Results cache to photonCacheFile (resumable).
  refineWithPhoton: true,
  photonCacheFile: "data/photoncache.json",
  photonAcceptKm: 4,
  photonConcurrency: 4,

  mapboxToken:
    process.env.MAPBOX_GEOCODING_TOKEN ||
    process.env.NEXT_PUBLIC_MAPBOX_TOKEN ||
    "",

  mapboxConcurrency: 10,
} as const;

// Column name aliases — the resolver matches the FIRST header whose normalized
// name contains any of these tokens, so it survives other export shapes.
const COLUMN_ALIASES: Record<string, string[]> = {
  name: ["location name", "hotel name", "property name", "name"],
  address: ["location address", "property address", "street", "address"],
  city: ["location city", "city"],
  state: ["location state", "state"],
  zip: ["location zip", "zip", "postal"],
  rooms: ["rooms", "room count", "roomcount", "units"],
  revenue: ["room revenue", "revenue", "room rev"],
  revpar: ["revpar", "rev par"],
  adr: ["adr", "average daily rate"],
  occupancy: ["occupancy", "occ"],
  photo: ["photo", "image", "img", "picture"],
  lat: ["latitude", "lat"],
  lng: ["longitude", "long", "lng", "lon"],
};

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
type Bucket = "red" | "yellow" | "gray";

interface Hotel {
  name: string;
  address: string;
  city: string;
  state: string;
  zip: string;
  rooms: number | null;
  revenue: number | null;
  revpar: number | null;
  adr: number | null;
  occupancy: number | null;
  photo: string | null;
  lat: number | null;
  lng: number | null;
  flagged: boolean;
  bucket: Bucket;
}

type GeoCache = Record<string, { lng: number; lat: number } | null>;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, "");

function resolveColumns(headers: string[]): Record<string, string | null> {
  const map: Record<string, string | null> = {};
  const normalized = headers.map((h) => ({ raw: h, n: norm(h) }));
  for (const [key, aliases] of Object.entries(COLUMN_ALIASES)) {
    const aliasNs = aliases.map(norm);
    // Prefer exact normalized match, then "contains".
    const exact = normalized.find((h) => aliasNs.includes(h.n));
    const contains =
      exact ?? normalized.find((h) => aliasNs.some((a) => h.n.includes(a)));
    map[key] = contains ? contains.raw : null;
  }
  return map;
}

function cleanNumber(v: unknown): number | null {
  if (v == null) return null;
  const s = String(v).replace(/[^0-9.\-]/g, "");
  if (s === "" || s === "-" || s === ".") return null;
  const n = Number(s);
  return Number.isFinite(n) ? n : null;
}

function cleanOccupancy(v: unknown): number | null {
  const n = cleanNumber(v);
  if (n == null) return null;
  // Express as a 0–1 fraction whether the source used 0.75 or 75(%).
  return n > 1 ? n / 100 : n;
}

const clean = (v: unknown) => String(v ?? "").trim();
const titleAddrKey = (h: Hotel) =>
  norm(`${h.address}|${h.city}|${h.zip}|${h.name}`);
const geoKey = (h: Hotel) =>
  norm(`${h.address}|${h.city}|${h.state}|${h.zip}`);

function haversineM(
  aLat: number,
  aLng: number,
  bLat: number,
  bLng: number
): number {
  const R = 6371000;
  const dLat = ((bLat - aLat) * Math.PI) / 180;
  const dLng = ((bLng - aLng) * Math.PI) / 180;
  const la1 = (aLat * Math.PI) / 180;
  const la2 = (bLat * Math.PI) / 180;
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(la1) * Math.cos(la2) * Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}

function quantile(sortedAsc: number[], p: number): number {
  if (sortedAsc.length === 0) return 0;
  const idx = p * (sortedAsc.length - 1);
  const lo = Math.floor(idx);
  const hi = Math.ceil(idx);
  if (lo === hi) return sortedAsc[lo];
  return sortedAsc[lo] + (sortedAsc[hi] - sortedAsc[lo]) * (idx - lo);
}

// ---------------------------------------------------------------------------
// Geocoders
// ---------------------------------------------------------------------------
async function geocodeMapbox(
  query: string
): Promise<{ lng: number; lat: number } | null> {
  const url =
    `https://api.mapbox.com/geocoding/v5/mapbox.places/` +
    `${encodeURIComponent(query)}.json?limit=1&country=US&autocomplete=false` +
    `&access_token=${CONFIG.mapboxToken}`;
  for (let attempt = 0; attempt < 4; attempt++) {
    const res = await fetch(url);
    if (res.status === 429) {
      await new Promise((r) => setTimeout(r, 1500 * (attempt + 1)));
      continue;
    }
    if (!res.ok) return null;
    const json: any = await res.json();
    const f = json.features?.[0];
    if (!f) return null;
    const [lng, lat] = f.center;
    return { lng, lat };
  }
  return null;
}

/** Google Geocoding API — rooftop accuracy. Returns the best match's location. */
async function geocodeGoogle(
  query: string
): Promise<{ lng: number; lat: number } | null> {
  const url =
    `https://maps.googleapis.com/maps/api/geocode/json` +
    `?address=${encodeURIComponent(query)}&region=us&key=${CONFIG.googleKey}`;
  for (let attempt = 0; attempt < 4; attempt++) {
    let res: Response;
    try {
      res = await fetch(url);
    } catch {
      await new Promise((r) => setTimeout(r, 1000 * (attempt + 1)));
      continue;
    }
    if (!res.ok) {
      await new Promise((r) => setTimeout(r, 800 * (attempt + 1)));
      continue;
    }
    const json: any = await res.json();
    if (json.status === "OVER_QUERY_LIMIT") {
      await new Promise((r) => setTimeout(r, 2000 * (attempt + 1)));
      continue;
    }
    if (json.status === "REQUEST_DENIED") {
      const msg: string = json.error_message ?? "";
      // A freshly-enabled API can report "not activated" for a minute or two
      // while it propagates — retry those rather than aborting the whole run.
      if (/activat/i.test(msg) && attempt < 3) {
        await new Promise((r) => setTimeout(r, 4000 * (attempt + 1)));
        continue;
      }
      throw new Error(`Google geocoding denied: ${msg}`);
    }
    const r = json.results?.[0];
    if (!r) return null;
    const loc = r.geometry?.location;
    if (!loc) return null;
    return { lng: loc.lng, lat: loc.lat };
  }
  return null;
}

/** US Census batch geocoder — free, no key, up to 10k addresses per request. */
async function geocodeCensusBatch(
  hotels: Hotel[]
): Promise<Map<number, { lng: number; lat: number }>> {
  const out = new Map<number, { lng: number; lat: number }>();
  const CHUNK = 5000;
  for (let start = 0; start < hotels.length; start += CHUNK) {
    const chunk = hotels.slice(start, start + CHUNK);
    const lines = chunk.map(
      (h, i) =>
        `${start + i},"${h.address}","${h.city}","${h.state}","${h.zip}"`
    );
    const csv = lines.join("\n");
    const form = new FormData();
    form.append("benchmark", "Public_AR_Current");
    form.append(
      "addressFile",
      new Blob([csv], { type: "text/csv" }),
      "addresses.csv"
    );
    process.stdout.write(
      `  census batch ${start}–${start + chunk.length}... `
    );
    try {
      const res = await fetch(
        "https://geocoding.geo.census.gov/geocoder/locations/addressbatch",
        { method: "POST", body: form }
      );
      const text = await res.text();
      // Response rows: id,input,status,matchType,matchedAddr,"lng,lat",...
      const rows = parse(text, {
        relax_column_count: true,
        skip_empty_lines: true,
      }) as string[][];
      let matched = 0;
      for (const row of rows) {
        const id = Number(row[0]);
        const status = row[2];
        if (status === "Match" && row[5]) {
          const [lng, lat] = row[5].split(",").map(Number);
          if (Number.isFinite(lng) && Number.isFinite(lat)) {
            out.set(id, { lng, lat });
            matched++;
          }
        }
      }
      console.log(`${matched} matched`);
    } catch (e) {
      console.log(`failed (${(e as Error).message})`);
    }
  }
  return out;
}

// Lodging / building POI types we trust as rooftop-accurate from Photon.
const PHOTON_BUILDING_VALUES = new Set([
  "hotel",
  "motel",
  "guest_house",
  "hostel",
  "resort",
  "chalet",
  "apartment",
  "apartments",
  "house",
  "commercial",
  "retail",
]);

/** Result of a Photon lookup: a coordinate, or `null` (no precise match), or
 *  the sentinel `UNREACHABLE` when the service didn't respond (timeout / error).
 *  Callers treat UNREACHABLE differently so we don't cache a transient outage. */
const UNREACHABLE = Symbol("unreachable");
type PhotonResult = { lng: number; lat: number } | null | typeof UNREACHABLE;

/** Photon (OSM, keyless) refiner. Returns a precise building/POI coordinate,
 *  null when the best match isn't building-precise, or UNREACHABLE on failure.
 *  Each request has a hard timeout so a slow/overloaded public instance can't
 *  hang the whole run. */
async function geocodePhoton(
  query: string,
  anchorLng: number,
  anchorLat: number,
  timeoutMs = 6000
): Promise<PhotonResult> {
  const url =
    `https://photon.komoot.io/api/?limit=1&lang=en` +
    `&lat=${anchorLat}&lon=${anchorLng}&q=${encodeURIComponent(query)}`;
  for (let attempt = 0; attempt < 2; attempt++) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    try {
      const res = await fetch(url, { signal: ctrl.signal });
      clearTimeout(timer);
      if (res.status === 429 || res.status >= 500) {
        await new Promise((r) => setTimeout(r, 1500 * (attempt + 1)));
        continue;
      }
      if (!res.ok) return null;
      const json: any = await res.json();
      const f = json.features?.[0];
      if (!f) return null;
      const props = f.properties ?? {};
      const isBuilding =
        props.osm_key === "building" ||
        PHOTON_BUILDING_VALUES.has(props.osm_value) ||
        props.housenumber != null;
      if (!isBuilding) return null;
      const [lng, lat] = f.geometry.coordinates;
      return { lng, lat };
    } catch {
      clearTimeout(timer);
      // timeout or network error — try once more, then report unreachable
    }
  }
  return UNREACHABLE;
}

async function mapWithConcurrency<T>(
  items: T[],
  limit: number,
  fn: (item: T, index: number) => Promise<void>
): Promise<void> {
  let i = 0;
  const workers = Array.from({ length: limit }, async () => {
    while (i < items.length) {
      const idx = i++;
      await fn(items[idx], idx);
    }
  });
  await Promise.all(workers);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
async function main() {
  const args = process.argv.slice(2);
  const limitArg = args.find((a) => a.startsWith("--limit"));
  const limit = limitArg
    ? Number(limitArg.split("=")[1] ?? args[args.indexOf(limitArg) + 1])
    : Infinity;
  const noGeocode = args.includes("--no-geocode");
  const forcedGeocoder = args.includes("--google")
    ? "google"
    : args.includes("--census")
    ? "census"
    : args.includes("--mapbox")
    ? "mapbox"
    : null;

  const geocoder =
    forcedGeocoder ??
    CONFIG.geocoder ??
    (CONFIG.googleKey ? "google" : CONFIG.mapboxToken ? "mapbox" : "census");

  console.log(`\n▶ tx-hotel-heatmap build-data`);
  console.log(`  input:    ${CONFIG.inputCsv}`);
  console.log(`  geocoder: ${geocoder}${noGeocode ? " (skipped)" : ""}`);

  if (!fs.existsSync(CONFIG.inputCsv)) {
    console.error(
      `\n✖ Missing ${CONFIG.inputCsv}. Drop the Box "Texan Hotel Analytics" export there first.`
    );
    process.exit(1);
  }

  // 1) Parse ----------------------------------------------------------------
  const raw = fs.readFileSync(CONFIG.inputCsv, "utf8");
  const records = parse(raw, {
    columns: (header: string[]) => header.map((h) => h.trim()),
    trim: true,
    skip_empty_lines: true,
    relax_column_count: true,
    relax_quotes: true,
  }) as Record<string, string>[];
  console.log(`\n  parsed ${records.length.toLocaleString()} rows`);

  const headers = Object.keys(records[0] ?? {});
  const col = resolveColumns(headers);
  console.log(
    `  columns -> ` +
      Object.entries(col)
        .filter(([, v]) => v)
        .map(([k, v]) => `${k}:"${v}"`)
        .join("  ")
  );

  const get = (rec: Record<string, string>, key: string) =>
    col[key] ? rec[col[key]!] : undefined;

  // 2) Normalize + compute RevPAR ------------------------------------------
  let flaggedCount = 0;
  let hotels: Hotel[] = records.map((rec) => {
    const rooms = cleanNumber(get(rec, "rooms"));
    const revenue = cleanNumber(get(rec, "revenue"));
    // Provisional per-night RevPAR for the source file's single month:
    // revenue / rooms / daysInPeriod. The source RevPAR column always divides
    // by 90 days regardless of the actual period, so we don't trust it and
    // recompute on the correct day count. build-history.mjs later REPLACES this
    // with the headline T12 RevPAR (trailing-12mo revenue / rooms / 365).
    let revpar =
      revenue != null && rooms && rooms > 0
        ? revenue / (rooms * CONFIG.daysInPeriod)
        : null;
    // Reject untrusted RevPAR: 1-room placeholders and implausible highs.
    if (
      (rooms != null && rooms < CONFIG.minRooms) ||
      (revpar != null && revpar > CONFIG.maxRevpar)
    ) {
      revpar = null;
    }
    const flagged = revpar == null || rooms == null || revenue == null;
    if (flagged) flaggedCount++;
    return {
      name: clean(get(rec, "name")),
      address: clean(get(rec, "address")),
      city: clean(get(rec, "city")),
      state: clean(get(rec, "state")).toUpperCase(),
      zip: clean(get(rec, "zip")).slice(0, 5),
      rooms,
      revenue,
      revpar,
      adr: cleanNumber(get(rec, "adr")),
      occupancy: cleanOccupancy(get(rec, "occupancy")),
      photo: clean(get(rec, "photo")) || null,
      lat: cleanNumber(get(rec, "lat")),
      lng: cleanNumber(get(rec, "lng")),
      flagged,
      bucket: "gray",
    };
  });

  // Filter to the target state.
  if (CONFIG.stateFilter) {
    const before = hotels.length;
    hotels = hotels.filter(
      (h) => !h.state || h.state === CONFIG.stateFilter
    );
    console.log(
      `  state filter (${CONFIG.stateFilter}): kept ${hotels.length.toLocaleString()} of ${before.toLocaleString()}`
    );
  }

  // Drop rows with no usable address, no name, or that are government tax
  // rollups rather than actual hotels.
  hotels = hotels.filter(
    (h) => h.name && h.address && !CONFIG.excludeNamePattern.test(h.name)
  );

  // Keep only real hotels: more than dropAtOrUnderRooms rooms. Strips the
  // thousands of vacation-rental / single-condo / RV-site filings that aren't
  // hotels. A null room count is treated as sub-scale and dropped.
  {
    const before = hotels.length;
    hotels = hotels.filter(
      (h) => h.rooms != null && h.rooms > CONFIG.dropAtOrUnderRooms
    );
    console.log(
      `  room filter (> ${CONFIG.dropAtOrUnderRooms} rooms): kept ${hotels.length.toLocaleString()} of ${before.toLocaleString()}`
    );
  }

  // Dedupe by location, keeping the highest-revenue filing.
  const byLoc = new Map<string, Hotel>();
  for (const h of hotels) {
    const k = titleAddrKey(h);
    const prev = byLoc.get(k);
    if (!prev || (h.revenue ?? 0) > (prev.revenue ?? 0)) byLoc.set(k, h);
  }
  hotels = [...byLoc.values()];
  console.log(`  deduped to ${hotels.length.toLocaleString()} unique hotels`);
  console.log(`  flagged (missing data): ${flaggedCount.toLocaleString()}`);

  if (Number.isFinite(limit)) {
    hotels = hotels.slice(0, limit);
    console.log(`  --limit applied: ${hotels.length} hotels`);
  }

  // 3) Geocode --------------------------------------------------------------
  // Cache per-geocoder so street-level Census coords never get reused when we
  // switch to rooftop Google (and vice-versa).
  const cacheFile =
    geocoder === "census"
      ? CONFIG.geocacheFile
      : CONFIG.geocacheFile.replace(/\.json$/, `.${geocoder}.json`);
  const cache: GeoCache = fs.existsSync(cacheFile)
    ? JSON.parse(fs.readFileSync(cacheFile, "utf8"))
    : {};

  // Apply cache + any lat/lng already present in the source.
  const needGeocode: Hotel[] = [];
  for (const h of hotels) {
    if (h.lat != null && h.lng != null) continue;
    const cached = cache[geoKey(h)];
    if (cached !== undefined) {
      if (cached) {
        h.lng = cached.lng;
        h.lat = cached.lat;
      }
    } else if (!noGeocode) {
      needGeocode.push(h);
    }
  }
  console.log(`\n  geocoding ${needGeocode.length.toLocaleString()} hotels...`);

  if (needGeocode.length > 0 && !noGeocode) {
    if (geocoder === "census") {
      const results = await geocodeCensusBatch(needGeocode);
      needGeocode.forEach((h, i) => {
        const r = results.get(i);
        cache[geoKey(h)] = r ?? null;
        if (r) {
          h.lng = r.lng;
          h.lat = r.lat;
        }
      });
    } else if (geocoder === "google") {
      if (!CONFIG.googleKey) {
        console.error(
          "✖ No Google key. Set GOOGLE_GEOCODING_API_KEY (or NEXT_PUBLIC_GOOGLE_MAPS_API_KEY)."
        );
        process.exit(1);
      }
      let done = 0;
      let saved = 0;
      await mapWithConcurrency(
        needGeocode,
        CONFIG.googleConcurrency,
        async (h) => {
          const q = `${h.name}, ${h.address}, ${h.city}, ${h.state} ${h.zip}`;
          const r = await geocodeGoogle(q);
          cache[geoKey(h)] = r ?? null;
          if (r) {
            h.lng = r.lng;
            h.lat = r.lat;
          }
          if (++done % 250 === 0) {
            console.log(`    ${done}/${needGeocode.length}`);
            // Checkpoint so a long paid run is resumable.
            if (done - saved >= 1000) {
              fs.writeFileSync(cacheFile, JSON.stringify(cache));
              saved = done;
            }
          }
        }
      );
    } else {
      if (!CONFIG.mapboxToken) {
        console.error(
          "✖ No Mapbox token. Set MAPBOX_GEOCODING_TOKEN or use GEOCODER=census."
        );
        process.exit(1);
      }
      let done = 0;
      await mapWithConcurrency(
        needGeocode,
        CONFIG.mapboxConcurrency,
        async (h) => {
          const q = `${h.address}, ${h.city}, ${h.state} ${h.zip}`;
          const r = await geocodeMapbox(q);
          cache[geoKey(h)] = r ?? null;
          if (r) {
            h.lng = r.lng;
            h.lat = r.lat;
          }
          if (++done % 250 === 0)
            console.log(`    ${done}/${needGeocode.length}`);
        }
      );
    }
    fs.mkdirSync(path.dirname(cacheFile), { recursive: true });
    fs.writeFileSync(cacheFile, JSON.stringify(cache));
    console.log(`  cache saved -> ${cacheFile}`);
  }

  const placed = hotels.filter((h) => h.lat != null && h.lng != null);
  console.log(
    `  placed ${placed.length.toLocaleString()} / ${hotels.length.toLocaleString()} hotels`
  );

  // 3b) Rooftop refinement via Photon (keyless) ----------------------------
  // Skipped when geocoding with Google, which is already rooftop-accurate.
  if (CONFIG.refineWithPhoton && geocoder !== "google" && !noGeocode) {
    const pcache: Record<string, { lng: number; lat: number } | null> =
      fs.existsSync(CONFIG.photonCacheFile)
        ? JSON.parse(fs.readFileSync(CONFIG.photonCacheFile, "utf8"))
        : {};

    const need = placed.filter((h) => pcache[geoKey(h)] === undefined);
    console.log(
      `\n  refining ${need.length.toLocaleString()} pins via Photon (rooftop)...`
    );

    let done = 0;
    let lastSave = 0;
    let consecutiveUnreachable = 0;
    let aborted = false;
    await mapWithConcurrency(need, CONFIG.photonConcurrency, async (h) => {
      if (aborted) return; // circuit broken — skip remaining (keep Census)
      const q = `${h.name}, ${h.address}, ${h.city}, ${h.state} ${h.zip}`;
      const r = await geocodePhoton(q, h.lng!, h.lat!);
      if (r === UNREACHABLE) {
        // Don't cache an outage; trip the breaker if the service is clearly down.
        if (++consecutiveUnreachable >= 30 && !aborted) {
          aborted = true;
          console.log(
            "  ⚠ Photon unreachable (30x in a row) — skipping refinement, keeping Census coords."
          );
        }
        return;
      }
      consecutiveUnreachable = 0;
      pcache[geoKey(h)] = r;
      done++;
      if (done % 200 === 0) console.log(`    ${done}/${need.length}`);
      if (done - lastSave >= 500) {
        fs.writeFileSync(CONFIG.photonCacheFile, JSON.stringify(pcache));
        lastSave = done;
      }
    });
    fs.writeFileSync(CONFIG.photonCacheFile, JSON.stringify(pcache));

    // Apply: accept a refined point only when it's near the Census anchor.
    let refined = 0;
    for (const h of placed) {
      const r = pcache[geoKey(h)];
      if (
        r &&
        haversineM(h.lat!, h.lng!, r.lat, r.lng) <= CONFIG.photonAcceptKm * 1000
      ) {
        h.lng = r.lng;
        h.lat = r.lat;
        refined++;
      }
    }
    console.log(
      `  refined ${refined.toLocaleString()} / ${placed.length.toLocaleString()} pins to rooftop (rest kept Census)`
    );
  }

  // 4) Bucket by RevPAR percentile -----------------------------------------
  const revparVals = placed
    .map((h) => h.revpar)
    .filter((v): v is number => v != null && v > 0)
    .sort((a, b) => a - b);
  const redCut = quantile(revparVals, CONFIG.bucketPercentiles.red);
  const yellowCut = quantile(revparVals, CONFIG.bucketPercentiles.yellow);
  console.log(
    `\n  RevPAR cutoffs -> yellow >= $${yellowCut.toFixed(0)}, red >= $${redCut.toFixed(0)}`
  );

  const tally: Record<Bucket, number> = { red: 0, yellow: 0, gray: 0 };
  for (const h of placed) {
    if (h.revpar == null || h.revpar <= 0) h.bucket = "gray";
    else if (h.revpar >= redCut) h.bucket = "red";
    else if (h.revpar >= yellowCut) h.bucket = "yellow";
    else h.bucket = "gray";
    tally[h.bucket]++;
  }
  console.log(
    `  buckets -> red ${tally.red}  yellow ${tally.yellow}  gray ${tally.gray}`
  );

  // 5) Write GeoJSON --------------------------------------------------------
  const geojson = {
    type: "FeatureCollection" as const,
    features: placed.map((h) => ({
      type: "Feature" as const,
      geometry: { type: "Point" as const, coordinates: [h.lng, h.lat] },
      properties: {
        name: h.name,
        address: h.address,
        city: h.city,
        state: h.state,
        zip: h.zip,
        rooms: h.rooms,
        revpar: h.revpar != null ? Math.round(h.revpar) : null,
        adr: h.adr != null ? Math.round(h.adr) : null,
        occupancy: h.occupancy,
        revenue: h.revenue != null ? Math.round(h.revenue) : null,
        bucket: h.bucket,
        photo: h.photo,
        flagged: h.flagged,
      },
    })),
  };

  fs.mkdirSync(path.dirname(CONFIG.outputGeojson), { recursive: true });
  fs.writeFileSync(CONFIG.outputGeojson, JSON.stringify(geojson));
  const kb = (fs.statSync(CONFIG.outputGeojson).size / 1024).toFixed(0);
  console.log(
    `\n✔ wrote ${geojson.features.length.toLocaleString()} features -> ${CONFIG.outputGeojson} (${kb} KB)\n`
  );
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
