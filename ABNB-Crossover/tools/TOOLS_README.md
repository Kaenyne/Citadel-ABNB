# tools/ — scripts copied verbatim from SIG, with what to change for ABNB

All 13 files are byte-identical copies from `SIG/research/data/` and `SIG/research/data/wayback_cache/`. Nothing has been edited. Each still has SIG paths and domains hard-coded; the table says what to swap. Environment verified 2026-09-05: Python 3.13, `yfinance 1.3.0`, `pytrends` importable, `pandas`, `requests`, `matplotlib`.

| Script | What it does | Reuse grade | What to change for ABNB | Gotchas already hit on SIG |
|---|---|---|---|---|
| `options_ledger.py` | yfinance option chains → ATM IV, straddle %, 25Δ skew, P/C ratios, event-implied move by variance differencing; appends to CSV | **Reuse** | `TICKERS` → `["ABNB","BKNG","EXPE","TRIP","MAR","HLT","H","JETS"]`; `NEAR_TARGET`/`FAR_TARGET` → first expiry after the ABNB print and next monthly; `HERE` path | Yahoo IVs; drop quotes without live bid/ask (already done); run weekly and the day before the print |
| `cc_pricing_scraper.py` | Common Crawl: CDX index harvest per crawl × domain → seeded sample → range-fetch WARC → parse embedded state JSON → one row per product; resumable via progress JSON | **Adapt** | `DOMAINS`, the URL regex for listing pages (`/rooms/<id>`), `MIN_LEN`, and the whole `parse()` (SIG parsed SAP-Hybris `priceData`; Airbnb pages embed a different JSON blob — inspect one WARC record first) | Index endpoint 5xx → retry, never mark done; shells vs full renders separated by WARC length; 4 workers is polite; ~10k fetches for 3 domains × 3 years |
| `cc_pricing_aggregate.py` | Turns product rows into breadth × depth "discount factor", median list/sale price, bucket splits, and a two-panel chart | **Adapt** | Column names from your parser; buckets (entire-home / private-room / hotel; urban / non-urban; Superhost) | UBS defines discount factor = share on sale × mean discount; keep the definition so you can compare to Evidence Lab |
| `cc_matched_sku.py` | Matched-panel version: same product IDs in two windows → like-for-like price change, markdown breadth, share with list raised | **Adapt** | Windows to ABNB quarters (calendar); ID regex to listing IDs | Prefer same calendar month in both windows (already implemented); this like-for-like exhibit was the SIG deck's cleanest pricing slide |
| `holiday_capture.py` | Live weekly capture via the site's own public search API (Unbxd keys embedded in page) when the site 403s scrapers; splices onto the CC history | **Idea/adapt** | Airbnb's front end calls an internal API (rotating keys, signed); expect breakage. Alternative live sources: Inside Airbnb quarterly dumps, AirDNA free city pages | Windows Task Scheduler weekly job pattern is documented in the docstring |
| `fetch_commoncrawl.py` | Homepage captures from every monthly crawl (systematic timing, unlike Wayback's trigger-based captures) | **Reuse** | `banners`/host list → `airbnb.com`, `vrbo.com`, `booking.com` | Wayback replay tier went down mid-build on SIG; CC is the fallback and arguably better |
| `fetch_snapshots.py` | Wayback CDX-driven homepage sampling with dense months; resumable; outage detection | **Reuse** | Host list; `DENSE` months (ABNB: Jan booking season, summer, Nov–Dec) | `id_` raw mode URL; IA "temporarily offline" interstitial guard |
| `parse_promos.py` | Regex extraction of promo depth/breadth from archived homepages, with **template-era handling** | **Idea** | Airbnb homepage messaging to track: total-price display, fee language, "Guest Favorites", Experiences/Services launches, host-fee changes | The load-bearing lesson: templates drift; anchoring on one DOM hook silently zero-fills other eras and *manufactures* the trend you want. Extract two regions present in every era, flag non-comparable captures, never zero-fill |
| `analyze_promos.py` | Panel → fiscal-quarter stats, y/y deltas | **Adapt** | `fq()` to calendar quarters | — |
| `forward_exhibits.py` | KPI panel from transcripts with source tags per number; implied-units derivation; matplotlib style helpers and validated palette | **Adapt (style reuse)** | Rows and derivations (ABNB: implied ADR = GBV/nights; take rate = revenue/GBV; FX-neutral flags); `fq_of` to calendar | Every hard-coded number carries `file:line`; keep that discipline — judges grep |
| `deck_charts_v2.py` | Bar strip with hatched "qualitative" bars, print-day move distribution, bear-scoreboard table chart | **Adapt** | Data arrays; the print-day distribution chart is directly reusable with ABNB moves | `esc()` escapes `$` for matplotlib mathtext |
| `exhibit_like_for_like.py` | Two-panel like-for-like price / markdown-breadth chart | **Adapt** | Input CSV names, banner colors | — |
| `elasticity_calc.py` | Log and arc elasticities from P/Q pairs | **Reuse (pattern)** | Inputs: ADR vs nights by region; take-rate changes vs host supply | The SIG result (LGD elasticity ≈ −0.7) came from official customs data; for ABNB the P/Q pairs are in the shareholder letters |

## Scripts that were NEVER saved on SIG (rebuild ~1h each; do it on ABNB from day one)

- Transcript parser: Bloomberg merged PDF → per-call `.txt` → Q&A blocks with speaker canonicalization → `qa_blocks_raw.csv`, `topics_by_call.csv`, `sentiment_by_call.csv`, `analyst_appearances.csv`. Format reference: `SIG/transcripts/FY2027_Q1.txt` (header lists participants; body has speaker lines).
- Print-day reaction and pre-earnings drift study (`00_MASTER_SYNTHESIS.md` §4b): from daily prices + call dates → |move| on print day vs normal, 5d/20d pre-drift, corr(drift, print move). Save it this time.
- XBRL `companyfacts` pull for the peer discrimination table (`pitch_mining_cannibals.md` §0): diluted shares, revenue, GM, CFO, capex, FCF, buybacks, dividends, net debt + Piotroski F-score per FY. For ABNB the peers are BKNG, EXPE, TRIP, MAR, HLT, plus the SBC-vs-buyback cohort (META, NFLX, UBER, DASH). Endpoint: `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json` with a UA header.
- Google Trends pull (`altdata_search_traffic.md` §1.1 has the `pytrends` urllib3 patch; ~7 payloads before 429; cache aggressively).

## BEA extraction snippet (used to build `data/bea_pce_travel_monthly_2015_2026.csv`)

```python
import pandas as pd
xl = pd.ExcelFile(r"C:\Users\krish\BAM_comp\SIG\research\data\bea_Section2All_underlying.xlsx")
want = {"Accommodations (104)":"accommodations","Hotels and motels":"hotels_motels",
        "Air transportation (64)":"air_transportation","Package tours":"package_tours",
        "Foreign travel by U.S. residents (129)":"foreign_travel_by_us_residents",
        "Foreign travel in the United States":"inbound_foreign_travel_in_us",
        "Motor vehicle rental":"motor_vehicle_rental","Food services":"food_services",
        "Recreation services":"recreation_services","Services":"services_total"}
sheets = {"U20405-M":"nominal_saar_musd","U20406-M":"real_chained_2017_musd","U20404-M":"price_index_2017eq100"}
frames = []
for sh, measure in sheets.items():
    df = xl.parse(sh, header=None); dates = df.iloc[7, 3:].astype(str).tolist(); seen = set()
    for i in range(8, len(df)):
        lab = str(df.iloc[i, 1]).strip()
        if lab in want and lab not in seen:
            seen.add(lab)
            frames.append(pd.DataFrame({"period": dates, "series": want[lab], "bea_line": df.iloc[i, 0],
                                        "bea_label": lab, "measure": measure,
                                        "value": pd.to_numeric(df.iloc[i, 3:], errors="coerce").values}))
out = pd.concat(frames)
out["date"] = pd.to_datetime(out["period"].str.replace("M", "-"), format="%Y-%m", errors="coerce")
out = out.dropna(subset=["date", "value"]).sort_values(["measure", "series", "date"])
out["yoy_pct"] = out.groupby(["measure", "series"])["value"].pct_change(12) * 100
```

Row 7 is the header row with `YYYYMmm` period labels from column 3; column 0 is the BEA line number, column 1 the label. "Recreation services" and "Services" appear twice (addenda) — first occurrence is the main table.
