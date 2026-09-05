# Codex handoff — ABNB alt-data extraction, phase 2 (compute-heavy)

You are continuing an in-progress alternative-data build for a Harvard FAC x Citadel
intercollegiate stock pitch on **Airbnb (NASDAQ: ABNB)**. The objective is a
**guidance nowcast**: predict ABNB's next-quarter revenue and Nights & Seats Booked
ahead of the print, calibrated against reported actuals, and positioned against Street
consensus.

Phase 1 (acquisition breadth) is largely done. Your job is the compute-heavy half:
finish the long-tail pulls, normalise ~540M+ fact rows, and build the versioned v2
release. Budget generously — this is expected to run for hours.

---

## 0. Get the code

```bash
git clone https://github.com/Kaenyne/Citadel-ABNB.git
cd Citadel-ABNB
git fetch origin theo/alt-data-acquisition && git checkout theo/alt-data-acquisition
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The reusable acquisition layer is `analysis/src/acquisition/` (`fetch.py`,
`integrity.py`, `sources/inside_airbnb.py`, `run_*.py`). **Read
`analysis/src/acquisition/README.md` before writing any fetch code** — it documents
three client-side bug classes that each looked exactly like an access restriction.

The data work happens in the local project folder, not the repo:
`~/Library/CloudStorage/OneDrive-UniversityofFlorida/AIRBNB DATA`

---

## 1. Hard rules — non-negotiable

**Immutability.** `raw/`, `metadata/source_manifest.csv`, `metadata/file_inventory.csv`,
`processed/airbnb_quant_panel_v1/`, and `processed/airbnb_quant_panel_v1.duckdb` are
frozen. Never overwrite, rename, delete or modify them. Open DuckDB with
`read_only=True`. Re-verify all 53 v1 SHA-256 hashes at the start and end of every task
that writes anything:

```bash
python3 -c "
import hashlib,csv
bad=n=0
for r in csv.DictReader(open('metadata/file_inventory.csv')):
    n+=1
    if hashlib.sha256(open(r['local_path'],'rb').read()).hexdigest()!=r['sha256']: bad+=1
print(n,bad); assert n==53 and bad==0"
```

**Lawful and free only.** No payment, no trials, no CAPTCHA solving, no paywall or
access-control circumvention, no credential sharing, no user-agent spoofing to evade
bot protection. Do not scrape Airbnb's live consumer site — Inside Airbnb and Common
Crawl are third-party archives and are fine.

**HTTP 403/401/451 is a source decision.** Log as `access-restricted-by-source` with URL
and timestamp, then stop. No retry campaign, no alternate route.

**Licensing tiers.** Every fact row carries `comparability_tier` (statistical) AND
`license_tier` (legal). `license_tier ∈ {public_domain, cc_by_4_0, open_gov, open_repo,
unlicensed_mirror, licensed_norestribute}`. Rows tagged `licensed_norestribute`
(FactSet transcripts, Bloomberg exports) must never enter a shareable release, never
join a CC BY 4.0 table, and never be committed to the **public** GitHub repo. Enforce
with a build assertion.

**Storage.** Bulk data goes to the external SSD, never OneDrive — OneDrive dehydrates
files mid-pipeline and three files in this project became unreadable that way.

```
/Volumes/PortableSSD/ABNB_DATA_EXPANSION/     ~854 GB free
```

Abort any batch when free space < 5 GB.

---

## 2. Verified reconnaissance — do NOT re-derive these

Established by live probing 2026-09-05. Re-verify before a bulk run; do not re-discover.

| Fact | Value |
|---|---|
| Inside Airbnb current snapshots published | 120 city-snapshots x 3 core file types = 360 |
| Historical URL catalog already built | **4,917 URLs, 2021-2026** |
| Historical live rate (72-URL paced sample) | **61%**, strong recency gradient |
| ...by year | 2021: 42% · 2022: 42% · 2023: 50% · 2024: 58% · **2025: 83% · 2026: 92%** |
| Historical mean `listings.csv.gz` | 4.6 MB |
| Historical US availability | **0% — every US probe returned 403** |
| Countries fully open (historical) | australia, belgium, belize, china, france, germany, greece |
| Countries mostly 403 | austria, brazil, chile, czech-republic, denmark |
| Wayback holds IA data files? | **No.** Index pages only (366 monthly captures, 2015-2026) |
| Common Crawl `airbnb.com/rooms/*` | **58 records / 52 listings per monthly crawl** — 0.008% of panel |
| Common Crawl payload quality | Excellent — verified `ratingValue`, `reviewCount`, `latitude`, `roomType`, `personCapacity` |
| Eurostat `tour_ce_*` | 8 datasets, 2018-2026 monthly, 32 countries, NUTS 1/2/3 + cities |
| SEC EDGAR | CIK **1559720**; N&EB and GBV are **not** XBRL-tagged (standard `us-gaap` only) |
| **Current `calendar.csv.gz` schema** | **5 cols: `listing_id, date, available, minimum_nights, maximum_nights` — NO PRICE.** Verified across 8 markets on 3 continents |
| **Calendar forward horizon** | **372 days per listing** — this is a booking curve, not a price series |
| Legacy calendars (2019-20 SF) | 7 cols, DID carry price. Do not generalise from them |
| Asking price | `listings.csv.gz` only (90 cols), ~76% populated, format `$1,234.56` |

**Catalog file:** `raw_expansion/v2_2026-09-05/inside_airbnb_catalog/historical_url_catalog.json`

---

## 3. Known defect classes — guard against all four

These are observed, not hypothetical. Each initially looked like an access restriction.

1. **Non-ASCII paths raise.** `ciudad-autónoma-de-buenos-aires`, `közép-magyarország`.
   Use `fetch.encode_url()` (percent-encodes path, idempotent).
2. **HTTP 200 can be a stub.** `china/beijing/2023-03-29/listings.csv.gz` returned 200
   with a **511-byte** body. `integrity.validate()` rejects `.csv.gz` under 2,048 bytes.
3. **Socrata federates its catalog.** A query against `data.sfgov.org` returns dataset
   IDs hosted on *other* domains. Always request from `metadata.domain` of each result.
4. **Dataverse wants header auth.** `X-Dataverse-key: <token>`, not `?key=`. Passing it
   as a query parameter returns 403 on every file and looks like a permission wall.

**Heuristic: uniform failure across an entire source is almost always your client.
Scattered failure is the source.** Inside Airbnb's 403s are scattered by country, so
those are real. Never record a client bug as an access blocker — that is precisely how
the previous iteration lost 75 cities.

**Also guard: keyword filters over-match.** A Dataverse search for "airbnb" pulled a
CNN socioeconomic-bias image dataset (Arkansas.zip, 1.07 GB). Check that a candidate is
listing/calendar/review data *before* downloading, and enforce a per-file size ceiling
with an explicit relevance check.

---

## 4. Current state

**Done (in `raw_expansion/v2_2026-09-05/` unless noted):**

| Cohort | Volume | Licence |
|---|---|---|
| Inside Airbnb current (SSD) | **COMPLETE 315/315**, 10 GB, 120 markets / 35 countries incl. **all 34 US**. **982,188 listing rows, 588,120,594 calendar rows, 67,500,188 review rows = 656,602,970 total** | cc_by_4_0 |
| Municipal registries | 25 datasets, 17 portals, 109,343 rows | open_gov |
| Eurostat `tour_ce_*` | 8 datasets, 485,144 values | open_gov |
| FRED | 10 series, 11,516 obs | public_domain |
| SEC EDGAR | XBRL companyfacts + 14 10-Q/10-K documents, 368 KPI sentences | public_domain |
| Zenodo / Figshare | 4 files | open_repo |
| Harvard Dataverse | 21 files incl. **`str_daily_1.tab` (210 MB)** and **`str_daily_2.csv` (370 MB)** — daily STR replication data | open_repo |
| Transcripts (LICENSED) | 23 quarters Q4-2020 → Q2-2026 | licensed_norestribute |
| Bloomberg (LICENSED) | 6,365 rows: consensus, revisions, comps, daily px | licensed_norestribute |

**Not started — this is your work:**
- Inside Airbnb **historical** (the 4,917-URL catalog)
- Common Crawl validation cohort
- Parquet conversion
- **The v2 DuckDB build**
- Coverage comparison vs v1, overlap audits, final report

---

## 5. Tasks, in dependency order

### T1 — DONE. Inside Airbnb current is complete (315/315, 0 failures, 0 restrictions).

### T2 — Inside Airbnb historical (compute-heavy, hours)
1. **Country triage first.** Probe one date per country (~35 HEAD requests). Availability
   is country-consistent — this avoids burning a 5s-paced budget on restricted countries.
2. Full HEAD probe of open countries. Write
   `inside_airbnb_catalog/availability_full.csv` with
   `url,country,region,city,snapshot,kind,http,content_length,classification,probed_at_utc`.
3. Classify: `200` + `content_length ≥ 2048` → `available`; `200` + smaller →
   `stub-rejected`; `403/404` → `access-restricted-by-source`.
4. Compute the disk budget from `content_length` **before** downloading.
5. Download in priority order: **2026 and 2025 listings first** (92% and 83% live), then
   2024, then calendars, then reviews. Record the Wayback capture timestamp as lineage.

Expect ~33 GB for the full set; the SSD has 854 GB, so no pruning needed.

### T3 — Common Crawl validation cohort (small, high analytical value)
Not a panel source — 52 listings/crawl. Its job is **independent price validation**:
CC captures are timestamped third-party captures of what Airbnb actually rendered.
Match CC listing IDs to Inside Airbnb IDs within ±45 days and report median absolute
% deviation on price and rating. A large systematic gap is a **finding to report**, not
a bug to hide.

Range-fetch WARC records by byte offset — never download whole WARC files (~1 GB each).
Store extracted *fields only*, never raw HTML. `license_tier=unlicensed_mirror`.

### T4 — Parquet conversion (compute-heavy)
Convert every validated `.csv.gz` to Parquet, **preserving the original SHA-256 in the
manifest before conversion** so provenance survives. Typically 3–5x smaller and far
faster in DuckDB. At ~540M rows, gzipped-CSV parsing is the bottleneck for every
downstream query.

### T5 — Build the v2 release (the main deliverable)
Extend v1's adapter pattern (`processing/build_quant_panel.py`, 2,683 lines — read it;
it is well built and its staged-publish discipline should be reused exactly: build to
temp → validate → copy once → re-hash → rename → refuse to overwrite).

**Separate tables, never one denormalised table:**
`listing_snapshots`, `calendar_daily`, `review_events`, `market_snapshot_panel`,
`registry_records`, `macro_series`, `reported_kpis`, `source_file_provenance`,
`coverage_summary`, `field_availability`, `duplicate_overlap_assessment`,
`transformation_log`, `output_manifest`.

**Every fact row retains:** provenance, original text IDs, record timing, geography,
`source_file_id`, `source_row_number`, `comparability_tier`, `license_tier`,
`wayback_capture_timestamp` (historical rows only).

**Comparability tiers:** `core_current_cross_section`, **`core_historical_panel`** (new —
this is what makes YoY possible), `supplemental_historical`, `supplemental_sample`,
`exclude_synthetic_risk`, `registry_official`, `macro_reference`, `reported_actuals`.

**The test that proves the build worked:**

```python
def test_v2_contains_real_year_over_year_pairs():
    rows = con.execute("""
        select market, count(distinct strftime(record_snapshot_date,'%Y')) yrs,
               count(distinct source_file_id) files
        from listing_snapshots
        where comparability_tier in ('core_current_cross_section','core_historical_panel')
        group by 1 having yrs > 1 and files > 1
    """).fetchall()
    assert len(rows) >= 20, f"only {len(rows)} multi-year markets; v1 had 0"
```

The `files > 1` clause is essential. v1 *appeared* to have 25 two-month markets, but each
came from a **single** scrape spanning a week across a month boundary. Counting distinct
source files is what separates a real repeat observation from a scrape artifact.

```python
def test_no_licensed_rows_in_shareable_release():
    n = con.execute("select count(*) from listing_snapshots "
                    "where license_tier='licensed_norestribute'").fetchone()[0]
    assert n == 0
```

### T6 — THE ALPHA. This is where the token budget belongs.

Everything above is plumbing. T6 is the deliverable. Spend accordingly — expect this to
be the majority of compute and the entire source of pitch edge.

#### T6.1 — Forward booking curve (the crown jewel)

588M calendar rows, each listing observed across a **372-day forward horizon**, one
snapshot per market. For every (market, snapshot) compute the blocked-night rate by
days-ahead bucket:

```sql
-- days_ahead = date - snapshot_date
select market, snapshot_date,
       case when days_ahead <=  30 then 'h000_030'
            when days_ahead <=  60 then 'h031_060'
            when days_ahead <=  90 then 'h061_090'
            when days_ahead <= 180 then 'h091_180'
            else                        'h181_372' end as horizon,
       count(*) filter (where available = 'f')::double / count(*) as blocked_rate,
       count(distinct listing_id) as listings
from calendar_daily group by 1,2,3
```

That vector across horizons **is the booking curve**. Its shape at a point in time is a
level; its change versus the same market a year earlier is the signal. In a Los Angeles
sample the near-horizon blocked rate ran ~40%.

**Critical caveat to carry into every conclusion:** `available='f'` conflates *booked*
with *host-blocked* and *inactive listing*. It is a bounded proxy, not occupancy.
Never label it "occupancy" in output. Estimate the blocked-but-not-booked share by
cross-checking against `number_of_reviews_l30d` in the matching listings file, and
report the sensitivity.

#### T6.2 — Test management's RNPL claim (falsifiable, and nobody else will run it)

On the Q2 2026 call, management said Reserve Now Pay Later "drove more bookings, **longer
booking lead times** and contributed to the increase in ADR," and that RNPL was **over 20%
of Q2 GBV**.

That is a directly testable claim with this data. If lead times genuinely lengthened, the
**far-horizon buckets should be filling faster year-over-year than the near-horizon
buckets**. Compute, for matched markets across vintages:

```
lead_time_shift = Δ_yoy(blocked_rate[h181_372]) - Δ_yoy(blocked_rate[h000_030])
```

Positive and widening ⇒ corroborates management and implies forward bookings are stronger
than the flat deferred-revenue line suggests. Negative ⇒ a genuine variant view worth the
whole pitch, because consensus is currently taking management at their word.

This requires T2 (historical snapshots) for the YoY leg. **Prioritise 2025 vintages of
markets we already hold at 2026** — that pairing is the single highest-value download in
the entire plan, and 2025 is 83% live.

#### T6.3 — Supply growth and host professionalisation

From matched listing snapshots across vintages: listing count growth, share held by
multi-listing hosts (`calculated_host_listings_count > 1`), entire-home share, superhost
share, and new-listing rate (first_review_date within trailing 12 months). Supply growth
is the volume half of GBV; professionalisation is a margin and regulatory-risk signal.

#### T6.4 — Regulatory drag

`license_text` is populated on ~46% of core listings across 18 countries. Join to the 25
municipal registry datasets. Austin gives near-daily active-STR counts on **527 dates**;
California gives Transient Occupancy Tax for **482 cities x 8 fiscal years** (TOT ÷ tax
rate reconstructs taxable lodging revenue). Test whether tightening registration regimes
predict supply contraction, and size the exposure across ABNB's markets.

#### T6.5 — The nowcast, benchmarked against consensus

Chain: market signals → deseasonalise → Nights & Seats Booked → GBV → revenue.

1. **Deseasonalise** against Eurostat `tour_ce_omr` (2018-2026 monthly, 32 countries).
   Without this a single-vintage momentum ratio just ranks markets by hemisphere — the
   Greek islands and Copenhagen top, Australia bottom, purely because the snapshot is
   June/July. This is not a subtlety; it is the difference between signal and calendar.
2. **Fit** `reported_KPI_t ~ f(proxy_t)` over every quarter the panel supports. Validate
   out-of-sample. With few pairs, **report standard errors honestly and say the fit is
   fragile** rather than presenting three decimal places.
3. **Benchmark against consensus, never against zero.** Street consensus for Q3 2026 is
   **$4,744m** against guidance of **$4,690-4,770m**, and FY2026 consensus has been
   revised **up 3.3% in six months** (13,371 → 14,162). A beat needs **>$4,770m, only
   +0.6% above consensus**. Any signal that does not clear that margin is not a call.
4. **State the edge or state that there isn't one.** A well-built panel that concludes
   "we cannot distinguish our estimate from consensus" is an honest and useful result.
   Manufacturing a variant view from a fragile fit is the failure mode to avoid.

#### T6.6 — Data-quality edge (cheap, differentiating)

Common Crawl captures are timestamped third-party captures of what Airbnb actually
rendered. Match CC listing IDs to Inside Airbnb IDs within ±45 days; report median
absolute % deviation on price and rating. **A systematic gap is a finding to publish, not
a bug to hide** — every team using Inside Airbnb would need to know.

#### What is NOT possible — do not attempt or claim

- **Realised ADR.** Current calendars carry no price. `listings.price` is an *asking*
  price for one scrape date. Do not present it as ADR, and do not reconcile it to the
  company's reported ADR without saying plainly what the gap is.
- **Currency-comparable price across markets.** `price_currency` is 0% populated by
  design. Any cross-market price work needs a documented country→currency assumption
  column, never an overwrite of the null.
- **A clean company-level time series from listings alone.** The panel is a convenience
  sample of ~120 markets against a global platform.

## 6. Two analytical traps already identified — do not re-derive them wrong

**Deferred revenue is a contaminated proxy.** It looks like a clean forward-bookings
indicator (guests pay at booking, revenue recognised at check-in), and in 2026 it
diverged sharply from revenue: revenue +17.9%/+16.5% YoY while deferred revenue went
+0.4%/-0.9%. **This is not softening demand.** Q2 2026 call, CFO:

> "absent the impact of Reserve Now, Pay Later bookings, which deferred guest payments
> from the time of booking closer to the date of stay, we expect that unearned fees
> would have grown year-over-year in Q2."

RNPL was **over 20% of Q2 GBV** and *lengthened* booking lead times. Any use of deferred
revenue must adjust for RNPL mix. Track RNPL adoption as its own variable.

**Metric renamed.** "Nights and Experiences Booked" → **"Nights and Seats Booked"**.
Parsers must match both.

---

## 7. Definition of done

- `processed/airbnb_quant_panel_v2/` + `airbnb_quant_panel_v2.duckdb`, built via staged
  publish, refusing to overwrite
- `validation_report.json` — all checks pass, including both assertions in T5
- `coverage_vs_v1.md` — markets added, **US markets added**, calendar/review files added,
  distinct vintages, **YoY pairs created**, rows by `comparability_tier` and `license_tier`
- Source and overlap audits; cohorts kept separate unless timing, geography, schema
  semantics, currency, identifier domain **and** licensing all make merging valid
- Append-only manifests updated; SHA-256 for every file
- v1 re-verified intact (53/53)
- Exact output paths listed
- **Every blocker stated as: exact source + exact lawful access blocker.** Known open ones:
  Harvard Dataverse Guestbook `guestbookID 18` (manual browser form, gates
  `AIRBNB.Listing.csv` at 635 MB); Inside Airbnb historical 403s (~39%, country-consistent);
  TSA passenger volumes 403 to non-browser clients (use FRED `AIRRPMTSID11` instead).

Open a PR against `main` from a `theo/<topic>` branch, fill in
`.github/PULL_REQUEST_TEMPLATE.md`, and **commit no licensed content** — the repo is public
and `CONTRIBUTING.md` forbids it explicitly.

---

## 8. Authentication map — probed live 2026-09-05

The operational question is not "open vs closed" but **"can a headless agent complete the
auth flow?"** A token is a file and works headless. Interactive SSO does not.

### Tier A — no auth, run unattended (all verified HTTP 200)

`data.insideairbnb.com` · Wayback CDX + index pages · Eurostat dissemination API ·
SEC EDGAR (`data.sec.gov`, `/Archives`, User-Agent header only) · Common Crawl index and
WARC range fetch · Socrata portals (NYC, SF, Chicago, Austin, Seattle, New Orleans) ·
Zenodo API · Figshare API · **Dryad API** · **HuggingFace** (ungated) · **OpenAIRE** ·
**DataCite**

### Tier B — free token, must exist BEFORE you start

| Source | Requirement | Status |
|---|---|---|
| FRED | `FRED_API_KEY` env var | provisioned |
| **Kaggle** | `~/.kaggle/kaggle.json` (kaggle.com/settings → API → Create New Token) | **must be created** |
| GitHub API | token — unauthenticated is **60 req/hr** (verified) | `gh` authenticated |
| Socrata app token | optional, raises rate limits | not obtained, not blocking |
| HuggingFace token | only for gated datasets | only if needed |

**Kaggle trap:** the download endpoint returns **HTTP 200 unauthenticated** — but that is
an HTML login page, not a file. This is defect class 2 (200 ≠ success) in its most
expensive form. Validate content-type and size, never the status code alone.

### Tier C — token valid, content still gated

**Harvard Dataverse.** The API token authenticates correctly. Specific files still return:

> `"You may not download this file without the required Guestbook response for guestbookID 18."`

A Guestbook is a depositor-required form (name, institution, intended use). It gates
`AIRBNB.Listing.csv` (**635 MB**) and the AirDNA-derived Venice, Reykjavik and Boston MSA
daily sets. **Do not auto-submit it** without the owner's explicit, specific instruction —
it means entering their personal data and accepting terms as them.

### Tier D — institutional SSO, not automatable headless

| Source | Probe | Note |
|---|---|---|
| **ICPSR** | **403** verified | UF Shibboleth |
| IBISWorld | — | access confirmed, SSO only |
| STR / CoStar | — | entitlement unconfirmed |
| ProQuest / JSTOR / ScienceDirect | — | UF SSO |
| Statista | — | **no institutional access — do not attempt** |

### Tier E — human only

**Bloomberg terminal.** Excel Add-In exports. Sheets 1, 4, 5, 6 already extracted
(6,365 rows); sheets 2 and 3 outstanding.

### Tier F — bot protection, NOT login. Never evade.

| Source | Behaviour | Do this instead |
|---|---|---|
| TSA passenger volumes | 403 to non-browser clients | FRED `AIRRPMTSID11` |
| OECD SDMX | 403 on probed endpoint | verify endpoint before concluding |
| Inside Airbnb historical | ~39% 403, country-consistent | respect; it is a real source decision |

Do not spoof a user agent, rotate IPs, or route around any of these.

---

## 9. Where computer use earns its keep — and where it does not

Browser automation is expensive and slow. Use it **only** where no API exists, never as a
substitute for an HTTP endpoint that already works.

**Worth it:**
- **Tier D sources.** A real browser session is the only way through UF Shibboleth. If the
  owner has authenticated Chrome, ICPSR and IBISWorld become reachable.
- **TSA passenger volumes.** A genuine visible browser download is legitimate; spoofing
  headers from a script is not. Same destination, different legitimacy.
- **Kaggle**, if `kaggle.json` is unavailable — a visible download in an authenticated
  session is the sanctioned path.

**Not worth it:**
- Anything in Tier A. Browser automation there is strictly slower and more fragile than
  the API you already have.
- The Inside Airbnb historical pull. 4,917 URLs at 5s pacing is an HTTP loop, not a
  browser task.

**Requires explicit owner instruction, never assume:**
- The Dataverse Guestbook form. It submits the owner's identity and accepts terms on
  their behalf. Ask first, every time.

---

## 10. Budget guidance

The compute is not evenly distributed. Rough shape:

| Work | Wall-clock | Token cost | Alpha |
|---|---|---|---|
| T2 historical download | Hours (I/O bound, 5s paced) | **Low** | Enabling |
| T4 Parquet conversion | Tens of minutes | **Near zero** | None |
| T5 v2 DuckDB build | Hours | Moderate | Infrastructure |
| **T6 analysis** | Hours | **HIGH — spend here** | **All of it** |

If the budget runs short, cut T3 (Common Crawl) and the pre-2024 half of T2 before
cutting anything in T6. The panel is already 656M rows; another 50M historical rows is
worth less than one properly validated booking-curve regression.
