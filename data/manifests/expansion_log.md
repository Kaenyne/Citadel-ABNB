# Expansion Log — v2

## 2026-09-05 (session 2)

Frozen v1 untouched. `raw/`, `metadata/source_manifest.csv`, `metadata/file_inventory.csv`,
`processed/airbnb_quant_panel_v1/`, and `processed/airbnb_quant_panel_v1.duckdb` were opened
read-only; the DuckDB connection used `read_only=True`. No v1 byte was rewritten.

### Acquired

- **Eurostat `tour_ce_*`** (8 JSON-stat datasets, 6.8 MB). Guest nights / stays at short-stay
  accommodation booked via collaborative-economy platforms (Airbnb, Booking, Expedia,
  TripAdvisor), supplied to Eurostat under platform agreement. 2018–2025 annual,
  2018–2026 monthly, 32 countries, NUTS 1/2/3 and city level.
  Method: public HTTP API, no auth. License: Eurostat re-use policy (attribution).
- **SEC EDGAR XBRL companyfacts, ABNB (CIK 1559720)** (2 JSON, 1.4 MB).
  20 quarterly revenue points and 23 deferred-revenue points, 2020-Q1 .. 2026-Q2.
  Method: public HTTP API with identifying User-Agent. License: US Government work.

### Access boundaries observed (not circumvented)

- `data.insideairbnb.com` retired snapshots: ~37% of sampled URLs return HTTP 200,
  the remainder return **403**. Paced 6-second retries confirmed the 403s are a persistent
  source access decision, not rate limiting. They are logged and respected. No retry
  campaign, no alternate route, no credential use.
- Every US historical snapshot probed returned 403. The US gap cannot be closed this way;
  municipal STR registries remain the route.

### Known limits

- Nights & Experiences Booked and GBV are **not XBRL-tagged**; only standard `us-gaap` tags
  exist. Those KPIs require shareholder-letter text, WRDS, or Bloomberg.
- Eurostat 2026 monthly values are not yet published for June/July. History supports
  calibration; the current period must be nowcast, not looked up.
- Q4 revenue is absent from the quarterly XBRL series (10-K reports FY); derive as FY − 9M.

### In progress

- Inside Airbnb historical URL catalog harvest from archived index pages (metadata only,
  no bulk download). Wayback holds the **index pages** (366 monthly captures, 2015–2026)
  but holds **no** `data.insideairbnb.com` files.
