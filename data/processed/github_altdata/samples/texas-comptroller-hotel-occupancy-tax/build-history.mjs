/**
 * build-history.mjs — compute correct RevPAR for public/hotels.geojson from the
 * Texas Comptroller period files in data/periods/.
 *
 *   node scripts/build-history.mjs
 *
 * Two RevPAR figures, BOTH expressed per available room-night:
 *
 *   T12 RevPAR   = trailing-12-month revenue / rooms / 365
 *                  (last four COMPLETE quarters: 2025Q2 + Q3 + Q4 + 2026Q1).
 *                  This is the headline metric the heatmap buckets / filters /
 *                  sorts on (properties.revpar).
 *
 *   Last-month   = latest reported month's revenue / rooms / days-in-that-month
 *                  (2026-MAY → /31). properties.lastMonthRevpar.
 *
 * Why this script owns RevPAR: the source Comptroller files report revenue PER
 * PERIOD — a single MONTH for the monthly files, a QUARTER for the quarterly
 * files — but their RevPAR column always divides by 90 days. So a single month
 * over 90 days understated monthly RevPAR ~3x. We recompute on the correct
 * day-count basis from the raw revenue.
 *
 * Reads (data/periods/, gitignored, copied from Box "Texan Hotel Analytics"):
 *   2023.csv                 — variable filings per hotel within 2023 → summed to ANNUAL
 *   2024Q2..2025Q4.csv       — one row per hotel per quarter (pre-aggregated)
 *   2026-JAN..2026-MAY.csv   — one row per hotel per month → rolled into 2026Q1 / 2026Q2
 *
 * Hotels are matched to existing geojson features by normalized
 * Location Address + City + 5-digit Zip (the same key the map was built on).
 *
 * Writes (in place):
 *   public/hotels.geojson      — sets properties.revpar = T12 RevPAR (per night),
 *                                properties.lastMonthRevpar, properties.lastMonth,
 *                                properties.revenue = latest-month revenue, and
 *                                re-buckets by the T12 RevPAR distribution.
 *   public/hotel-history.json  — per matched feature (keyed by feature id):
 *                                { history, t12Revenue, t12Revpar,
 *                                  lastMonthRevenue, lastMonthRevpar, lastMonth }
 *
 * Each trend point is a per-night RevPAR for that period (periodRevenue /
 * rooms / daysInPeriod) so every point — quarter, year, or partial — is on the
 * same nightly basis as T12 and the map.
 */
import { parse } from "csv-parse/sync";
import fs from "node:fs";

const PERIOD_DIR = "data/periods";
const GEOJSON = "public/hotels.geojson";
// Trend/T12 live in a separate file loaded on-demand (only when a card opens),
// so the map's initial geojson stays lean. Keyed by the feature's `id`.
const HISTORY = "public/hotel-history.json";

// Data-quality guards (mirror build-data.ts).
const MIN_ROOMS = 2; // 1-room filings are placeholders, not real room counts
const MAX_REVPAR = 2000; // $/night/room ceiling — rejects data errors / bad room counts

// Quarter axis, oldest → newest. 2023 is a single annual baseline point.
const QUARTERS = [
  "2023",
  "2024Q2", "2024Q3", "2024Q4",
  "2025Q1", "2025Q2", "2025Q3", "2025Q4",
  "2026Q1", "2026Q2",
];
// Months that roll up into 2026 quarters.
const MONTH_TO_Q = {
  "2026-JAN": "2026Q1", "2026-FEB": "2026Q1", "2026-MAR": "2026Q1",
  "2026-APRIL": "2026Q2", "2026-MAY": "2026Q2", // 2026Q2 is partial (no June yet)
};
// Actual calendar days in each reporting period — the divisor for per-night
// RevPAR. (2026 is not a leap year; Feb = 28.)
const DAYS_IN = {
  "2023": 365,
  "2024Q2": 91, "2024Q3": 92, "2024Q4": 92, // Apr–Jun, Jul–Sep, Oct–Dec
  "2025Q1": 90, "2025Q2": 91, "2025Q3": 92, "2025Q4": 92,
  "2026Q1": 90, "2026Q2": 61, // 2026Q2 = Apr (30) + May (31) so far
};
// T12 = the last four COMPLETE quarters (2026Q2 is partial, excluded).
// Their day counts sum to exactly 365, so T12 RevPAR = T12 revenue / rooms / 365.
const T12_QUARTERS = ["2025Q2", "2025Q3", "2025Q4", "2026Q1"];

// Latest reported single month — drives "last month" RevPAR.
const LAST_MONTH = { file: "2026-MAY", label: "May 2026", days: 31 };

const norm = (s) => String(s ?? "").toLowerCase().replace(/[^a-z0-9]/g, "");
const zip5 = (s) => String(s ?? "").trim().slice(0, 5);
const keyOf = (addr, city, zip) => `${norm(addr)}|${norm(city)}|${zip5(zip)}`;
const money = (v) => {
  const n = Number(String(v ?? "").replace(/[^0-9.\-]/g, ""));
  return Number.isFinite(n) ? n : 0;
};

function loadPeriod(file) {
  const raw = fs.readFileSync(`${PERIOD_DIR}/${file}`, "utf8");
  return parse(raw, {
    columns: (h) => h.map((x) => x.trim()),
    skip_empty_lines: true,
    relax_column_count: true,
    trim: true,
  });
}

// revByQuarter: Map<hotelKey, Map<quarter, revenue>>
const revByQuarter = new Map();
function addRevenue(hotelKey, quarter, revenue) {
  let m = revByQuarter.get(hotelKey);
  if (!m) revByQuarter.set(hotelKey, (m = new Map()));
  m.set(quarter, (m.get(quarter) ?? 0) + revenue);
}
// revLastMonth: Map<hotelKey, revenue> for the latest single month only.
const revLastMonth = new Map();

console.log("Reading period files from", PERIOD_DIR, "...");

// 2023 — sum every filing row per hotel into the annual figure.
for (const r of loadPeriod("2023.csv")) {
  addRevenue(keyOf(r["Location Address"], r["Location City"], r["Location Zip"]), "2023", money(r[" Revenue "] ?? r["Revenue"]));
}
// Quarterly files — one row per hotel; sum on the off chance a key repeats.
for (const q of ["2024Q2", "2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3", "2025Q4"]) {
  for (const r of loadPeriod(`${q}.csv`)) {
    addRevenue(keyOf(r["Location Address"], r["Location City"], r["Location Zip"]), q, money(r[" Revenue "] ?? r["Revenue"]));
  }
}
// 2026 monthly files — roll each month into its quarter, and capture the latest
// reported month separately for last-month RevPAR.
for (const [file, q] of Object.entries(MONTH_TO_Q)) {
  for (const r of loadPeriod(`${file}.csv`)) {
    const k = keyOf(r["Location Address"], r["Location City"], r["Location Zip"]);
    const rev = money(r[" Revenue "] ?? r["Revenue"]);
    addRevenue(k, q, rev);
    if (file === LAST_MONTH.file) revLastMonth.set(k, (revLastMonth.get(k) ?? 0) + rev);
  }
}

console.log("Hotels with any historical revenue:", revByQuarter.size.toLocaleString());

// Mutate geojson in place + build a SEPARATE history file keyed by feature id,
// so the map never downloads the trend data up front.
const geo = JSON.parse(fs.readFileSync(GEOJSON, "utf8"));
const round = (n) => Math.round(n);
const round2 = (n) => Math.round(n * 100) / 100;
const historyOut = {}; // id -> { history, t12Revenue, t12Revpar, lastMonth* }

let anyHist = 0, fullT12 = 0, withLastMonth = 0;

geo.features.forEach((f, i) => {
  const p = f.properties;
  p.id = i;
  // Drop any trend fields baked in by an earlier run — they live in HISTORY now.
  delete p.history;
  delete p.t12Revenue;
  delete p.t12Revpar;

  const key = keyOf(p.address, p.city, p.zip);
  const m = revByQuarter.get(key);
  const rooms = Number(p.rooms) || 0;
  const validRooms = rooms >= MIN_ROOMS;

  // --- Last-month RevPAR (month revenue / rooms / days-in-month) -----------
  const lastMonthRevenue = revLastMonth.has(key) ? round(revLastMonth.get(key)) : null;
  let lastMonthRevpar = null;
  if (validRooms && lastMonthRevenue != null && lastMonthRevenue > 0) {
    const v = lastMonthRevenue / (rooms * LAST_MONTH.days);
    if (v <= MAX_REVPAR) lastMonthRevpar = round2(v);
  }
  // Keep properties.revenue as the latest reported month (the card labels it so).
  if (lastMonthRevenue != null) p.revenue = lastMonthRevenue;
  p.lastMonthRevpar = lastMonthRevpar;
  p.lastMonth = LAST_MONTH.label;
  if (lastMonthRevpar != null) withLastMonth++;

  if (!m) {
    // No quarterly history → no T12. Heatmap RevPAR is null (gray).
    p.revpar = null;
    if (lastMonthRevenue != null) {
      historyOut[i] = {
        history: [],
        t12Revenue: null,
        t12Revpar: null,
        lastMonthRevenue,
        lastMonthRevpar,
        lastMonth: LAST_MONTH.label,
      };
    }
    return;
  }

  // --- Trend: one per-night RevPAR point per quarter that reported ---------
  const history = [];
  for (const q of QUARTERS) {
    if (!m.has(q)) continue;
    const revenue = m.get(q);
    const revpar = validRooms ? revenue / (rooms * DAYS_IN[q]) : null;
    const pt = { q, revenue: round(revenue), revpar: revpar == null ? null : round2(revpar) };
    if (q === "2023") pt.annual = true;
    if (q === "2026Q2") pt.partial = true;
    history.push(pt);
  }

  // --- T12 RevPAR (trailing 12mo revenue / rooms / 365) -------------------
  const hasAll = T12_QUARTERS.every((q) => m.has(q));
  let t12Revenue = null, t12Revpar = null;
  if (hasAll) {
    const t12 = T12_QUARTERS.reduce((s, q) => s + m.get(q), 0);
    t12Revenue = round(t12);
    if (validRooms) {
      const v = t12 / (rooms * 365);
      if (v > 0 && v <= MAX_REVPAR) t12Revpar = round2(v);
    }
    fullT12++;
  }

  // T12 RevPAR drives the heatmap. Rounded to a whole dollar for buckets/filters.
  p.revpar = t12Revpar == null ? null : Math.round(t12Revpar);

  if (history.length || t12Revenue != null || lastMonthRevenue != null) {
    historyOut[i] = {
      history,
      t12Revenue,
      t12Revpar,
      lastMonthRevenue,
      lastMonthRevpar,
      lastMonth: LAST_MONTH.label,
    };
    if (history.length) anyHist++;
  }
});

// --- Re-bucket by tertiles of the new T12 RevPAR distribution -------------
function quantile(sorted, p) {
  if (!sorted.length) return 0;
  const idx = p * (sorted.length - 1);
  const lo = Math.floor(idx);
  const hi = Math.ceil(idx);
  if (lo === hi) return sorted[lo];
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo);
}
const vals = geo.features
  .map((f) => f.properties.revpar)
  .filter((v) => v != null && v > 0)
  .sort((a, b) => a - b);
const RED_P = 0.6667, YELLOW_P = 0.3333;
const redCut = quantile(vals, RED_P);
const yellowCut = quantile(vals, YELLOW_P);

const tally = { red: 0, yellow: 0, gray: 0 };
for (const f of geo.features) {
  const v = f.properties.revpar;
  let bucket;
  if (v == null || v <= 0) bucket = "gray";
  else if (v >= redCut) bucket = "red";
  else if (v >= yellowCut) bucket = "yellow";
  else bucket = "gray";
  f.properties.bucket = bucket;
  tally[bucket]++;
}

fs.writeFileSync(GEOJSON, JSON.stringify(geo));
fs.writeFileSync(HISTORY, JSON.stringify(historyOut));

const n = geo.features.length;
const pct = (x) => `${((100 * x) / n).toFixed(1)}%`;
const median = vals.length ? vals[Math.floor(vals.length / 2)] : 0;
const avg = vals.length ? Math.round(vals.reduce((s, v) => s + v, 0) / vals.length) : 0;
console.log("\n=== RevPAR recomputed (T12 = revenue / rooms / 365) ===");
console.log(`features:               ${n.toLocaleString()}`);
console.log(`with T12 RevPAR:        ${vals.length.toLocaleString()} (${pct(vals.length)})`);
console.log(`with last-month RevPAR: ${withLastMonth.toLocaleString()} (${pct(withLastMonth)})`);
console.log(`with any trend history: ${anyHist.toLocaleString()} (${pct(anyHist)})`);
console.log(`with full T12 revenue:  ${fullT12.toLocaleString()} (${pct(fullT12)})`);
console.log(`median T12 RevPAR:      $${median.toLocaleString()}`);
console.log(`avg T12 RevPAR:         $${avg.toLocaleString()}`);
console.log(`bucket cutoffs:         yellow >= $${Math.round(yellowCut)}, red >= $${Math.round(redCut)}`);
console.log(`buckets:                red ${tally.red}  yellow ${tally.yellow}  gray ${tally.gray}`);
console.log(`geojson (lean):         ${GEOJSON} (${(fs.statSync(GEOJSON).size / 1e6).toFixed(1)} MB)`);
console.log(`history (on-demand):    ${HISTORY} (${(fs.statSync(HISTORY).size / 1e6).toFixed(1)} MB)`);
