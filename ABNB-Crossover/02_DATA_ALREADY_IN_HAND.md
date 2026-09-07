# Data already on disk that is usable for ABNB

Everything below exists because of the SIG project. Paths are relative to `C:\Users\krish\BAM_comp\`. Copies of the small, directly reusable files are in `ABNB-Crossover/data/`; large files are referenced in place.

## 1. NEW — BEA PCE travel-spend panel (extracted 2026-09-05)

**File:** `ABNB-Crossover/data/bea_pce_travel_monthly_2015_2026.csv` (4,170 rows, tidy: `date, series, measure, value, yoy_pct, bea_line, bea_label`).
**Source:** the SIG download `SIG/research/data/bea_Section2All_underlying.xlsx` (BEA NIPA Underlying Detail, Section 2, published Aug 26, 2026, monthly to **2026M07**). Sheets used: `U20405-M` (nominal, SAAR \$M), `U20406-M` (real, chained 2017 \$M), `U20404-M` (price index, 2017=100).
**Series extracted** (BEA line numbers in the file): Accommodations (104), Hotels and motels, Air transportation (64), Package tours, Foreign travel by U.S. residents (129), Foreign travel in the United States (inbound), Motor vehicle rental, Food services, Recreation services, Services total.

**Refresh:** re-download `https://apps.bea.gov/national/Release/XLS/Underlying/Section2All_xls.xlsx` (monthly, ~end of month, keyless) and re-run the extraction snippet in `tools/TOOLS_README.md` §BEA. Next release covers August 2026 (late September).

**Headline read as of Jul-2026 (nominal y/y, %):**

| Series | Mar | Apr | May | Jun | Jul |
|---|---|---|---|---|---|
| Accommodations | 7.0 | 5.4 | 4.2 | 6.7 | 5.3 |
| Hotels and motels | 8.4 | 6.2 | 4.5 | 7.9 | 6.0 |
| Air transportation | 13.3 | 17.1 | 19.3 | 22.4 | 21.3 |
| Foreign travel by US residents (outbound) | −5.9 | −6.2 | −3.4 | −1.5 | −2.5 |
| Foreign travel in the US (inbound) | 0.6 | −7.3 | 0.7 | 5.8 | 6.1 |
| Services total | 5.7 | 5.9 | 6.4 | 6.5 | 6.3 |

Real accommodations was only +1.8% y/y in July with the price index +3.4%: **US lodging spend is mostly price, not volume**, the same signature the SIG jewelry data showed. Air transportation is running +21% nominal but its price index is +17%, so real air is ~+4%. Outbound US travel has been negative y/y all year while inbound turned positive in June. Levels (Jul-2026 SAAR): accommodations \$207.7B, hotels & motels \$158.8B, air \$232.5B, outbound foreign travel \$273.7B, inbound \$153.8B.

**How SIG used the analog and what to copy:** for SIG, BEA jewelry & watches was "the only live public monthly category series" and the deck used it as a **share test**: category +7.9% nominal vs a +0.5–2.5% comp guide meant the print was a share question. For ABNB: BEA accommodations nominal vs ABNB's US nights/GBV growth is the same share test, and the real-vs-price split is the same "all price" concession. Caveats to carry over verbatim from `SIG/research/macro_trends.md` §4.2: BEA revises (2023 comprehensive benchmark), SAAR monthly is noisy, and PCE accommodations captures US resident spend only (ABNB's inbound guests sit in "Foreign travel in the United States").

## 2. FRED consumer backdrop (copied to `data/`, pulled 2026-08-29)

| File | Series | Use for ABNB |
|---|---|---|
| `fred_UMCSENT_umich_sentiment.csv` | UMich sentiment (monthly; sparse pre-1978) | discretionary backdrop; note Jul-2026 = 55.2 off a 49.5 June trough |
| `fred_PSAVERT_personal_saving_rate.csv` | personal saving rate | same |
| `fred_PCEDG_pce_durable_goods.csv` | PCE durables | goods-vs-services rotation framing |
| `fred_RSXFS_retail_sales_exfood.csv` | retail sales ex food services | same |
| `fred_PCEPI_pce_price_index.csv`, `fred_CPIAUCSL_cpi.csv` | deflators | deflate ADR / GBV |
| `fred_ECOMSA_ecomm_sales_sa.csv`, `fred_ECOMPCTSA_ecomm_pct_of_retail.csv` | e-commerce share | probably not needed |

Refresh with `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>` (keyless). ABNB-specific FRED series to add the same way: none directly for lodging (STR data is paid), but CPI "Other lodging away from home including hotels and motels" (`CUSR0000SEHB`) and "Airline fares" (`CUSR0000SETG01`) are free and monthly.

## 3. Options ledger baseline (`data/options_ledger.csv`, run 2026-09-02)

Rows for SIG, GAP, M, URBN, ANF, AEO, BRLT, XRT for two expiries: ATM IV, straddle % of spot, 25Δ put/call IVs and skew, P/C ratios, event-implied move. Useful only as a **format and calibration reference** (what a retail-tape skew looks like: XRT put skew +13 vs SIG call skew −7). Re-run `tools/options_ledger.py` with ABNB tickers; the CSV appends, so start a new file.

## 4. Bloomberg consensus-at-call (`data/bb_consensus_at_call.csv`)

Extracted from the page headers of the 1,134-page Bloomberg transcript PDF (`SIG/BB_Merged_Docs_20260828_204005.pdf`): per call, market cap, price, YTD change, consensus EPS (Q and FY), consensus sales (Q and FY). **The point for ABNB:** a Bloomberg transcript export carries the consensus snapshot at each call date for free, so the "estimates vs stock" exhibit (SIG: 2016–18 the stock fell *with* estimates; 2025–26 estimates rise and the stock doesn't) comes out of the same export you need anyway for the transcripts. Schema is the template.

## 5. SimilarWeb snapshot format (`data/web_traffic_snapshot_2026-08.csv`)

Nineteen-column schema for a monthly SimilarWeb free-tier capture (visits 3-mo aggregate, MoM, ranks, bounce, pages/visit, duration, top channel, retrieval date, URL, note). Clone the schema for airbnb.com, vrbo.com, booking.com, expedia.com, hotels.com, and do it monthly from day one; the SIG lesson was that the free tier gives no y/y and no history, so the series has to be built forward.

## 6. Large files still in `SIG/` worth knowing about

| Path | What | ABNB relevance |
|---|---|---|
| `SIG/research/data/bea_Section2All_underlying.xlsx` (12 MB) | Full BEA underlying detail, Section 2 | Source of §1; also has Table 2.3.x (major type), 2.4.3U quantity indexes |
| `SIG/research/data/Section2All_xls.xlsx` (4.9 MB) | BEA Section 2 standard tables | Quarterly/annual PCE by major type |
| `SIG/research/data/mrtssales92-present.xlsx`, `marts_current.xlsx` | Census MRTS | Not relevant (no lodging line) — but proves the download path |
| `SIG/20260829_UBS_SIG_...2Q_Preview.pdf` + `research/data/ubs_pages/*.png` | A UBS Evidence Lab note, transcribed | Template for what an Evidence Lab note contains; UBS covers ABNB and publishes app/web/pricing panels — pull the ABNB equivalent at the terminal |
| `SIG/research/data/qa_blocks_raw.csv`, `analyst_call_blocks.csv`, `topics_by_call.csv`, `sentiment_by_call.csv` | Transcript analytics outputs | Schemas to replicate (see `templates/TEMPLATES_README.md`) |
| `SIG/transcripts/*.txt` | 50 per-quarter transcripts parsed from the Bloomberg PDF | Format reference for the ABNB parse |

## 7. Datasets SIG identified but never captured that ALSO matter for ABNB

From `SIG/DATA_INVENTORY_2026-09-01.md` §11d: card-panel access (Earnest Dash, Hough Hall `ECAN`), the Placer education tier (useless for ABNB), Indeed hiring counts via Wayback (ABNB analog: host-support / trust-and-safety postings, weak), and the AlphaSense transcript library (strong for ABNB — hosts, property managers, ex-employees, OTA executives).
