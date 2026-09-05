# ABNB Alt-Data Extraction Plan (v2) — excluding WRDS

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Acquire, verify, and package every lawfully-free ABNB-relevant dataset needed to calibrate a nights/ADR nowcast against reported KPIs, plus the licensed terminal exports, into a provenance-complete v2 release that never touches frozen v1.

**Architecture:** One shared acquisition library handles fetch → SHA-256 → structural validation → append-only manifest, so every source uses identical provenance plumbing. Sources are acquired into per-source cohorts under `raw_expansion/v2_2026-09-05/`, kept separate until a documented compatibility test passes. Licensed sources (Bloomberg, STR) live in a physically separate, non-redistributable subtree. A final build produces normalized DuckDB tables mirroring v1's schema discipline.

**Tech Stack:** Python 3.12 stdlib (`urllib`, `csv`, `json`, `gzip`, `hashlib`, `zipfile`) + `duckdb` 1.5.5 (already installed). No third-party HTTP libraries — matches v1's stdlib-only convention.

**Spec:** This plan. Superseding context: `A_LEVEL_AIRBNB_DATA_EXPANSION_HANDOFF.md` (currently unreadable — see Task 1).

---

## Global Constraints

Every task's requirements implicitly include this section.

- **v1 is immutable.** Never write to, rename, or delete `raw/`, `metadata/source_manifest.csv`, `metadata/file_inventory.csv`, `processed/airbnb_quant_panel_v1/`, `processed/airbnb_quant_panel_v1.duckdb`. Open DuckDB with `read_only=True`. Re-verify all 53 v1 hashes at start and end of every task that writes anything.
- **Lawful, no-cost only.** No payment, no trial, no CAPTCHA solving, no paywall or access-control circumvention, no credential sharing. Do not scrape Airbnb's live consumer site.
- **HTTP 403 is a source access decision.** Log as `access-restricted-by-source`, record the exact URL and timestamp, and stop. No retry campaign, no alternate route, no proxy, no user-agent rotation to evade.
- **Retry policy.** Every fetch retries 3× with exponential backoff (2s, 8s, 30s) on 5xx / timeout / connection error only. Classify each terminal failure as `local-fault` (fix and retry) or `source-restriction` (log and stop). Never record a local fault as an access blocker — this was v1's single largest process failure.
- **Pacing.** Maximum 4 concurrent requests per host; minimum 5s between requests to `data.insideairbnb.com` and `web.archive.org`. Identify with `User-Agent: UF-student-research <email>`.
- **Disk guardrail.** Abort any batch when free space < 5 GB. Check before every batch. Current free space at plan time: 7.9 GiB.
- **Licensing tiers.** Every fact row carries BOTH `comparability_tier` (statistical) and `license_tier` (legal). `license_tier ∈ {public_domain, cc_by_4_0, open_gov, unlicensed_mirror, licensed_norestribute}`. Rows with `licensed_norestribute` never enter a shareable release and never join a CC BY 4.0 table.
- **Append-only.** `metadata/expansion/expansion_source_manifest.csv`, `expansion_file_inventory.csv`, and `expansion_log.md` are append-only. Never rewrite a prior row.
- **Raw means raw.** `raw_expansion/` holds original bytes only. Derived tables go to `processed/airbnb_quant_panel_v2_staging/`.

---

## Verified Reconnaissance (facts this plan rests on)

Established by live probing on 2026-09-05. Do not re-litigate these; do re-verify before bulk runs.

| Fact | Value |
|---|---|
| Inside Airbnb current snapshots published | 120 city-snapshots, 7 file types = 861 URLs |
| Currently held | 45 `listings.csv.gz` only (12.2% of core quant files) |
| Missing US markets | **34, all of them** |
| Missing current calendar/reviews | 246 files, available for all 45 held cities |
| Historical URL catalog recovered | **4,917 URLs, 2021–2026** (`inside_airbnb_catalog/historical_url_catalog.json`) |
| Historical live rate | ~37–45%, **country-consistent** not random |
| Historical US availability | **0% — every US probe returned 403** |
| Wayback holds data files? | **No.** Index pages only (366 monthly captures) |
| Eurostat `tour_ce_*` | 8 datasets, 2018–2026 monthly, 32 countries — **acquired** |
| SEC EDGAR ABNB | CIK 1559720, 20 quarterly revenue + 23 deferred points — **acquired** |
| N&EB / GBV in XBRL? | **No.** Standard `us-gaap` tags only |

**Three defects observed during probing that every downloader must handle:**

1. **Non-ASCII paths raise on `urllib`.** `ciudad-autónoma-de-buenos-aires` and `közép-magyarország` fail. Percent-encode the path with `urllib.parse.quote(path, safe='/')`.
2. **HTTP 200 with a tiny body is a stub, not data.** `china/beijing/2023-03-29/listings.csv.gz` returned 200 with `Content-Length: 511`. Reject any `.csv.gz` under 2,048 bytes.
3. **403 is country-consistent.** Austria, Brazil, Chile, Czechia, Denmark restricted; Australia, Belgium, Belize, China, France open. Probe one date per country first to avoid wasting a 5s-paced budget.

---

## File Structure

```
processing/
  acquisition/
    __init__.py          # package marker
    fetch.py             # HTTP with retry/backoff/pacing/classification
    integrity.py         # SHA-256, gzip/zip/CSV/JSON structural validation
    manifest.py          # append-only manifest + inventory writers
    sources/
      inside_airbnb.py   # current + historical URL builders and probe
      municipal.py       # Socrata/CKAN paged extractor
      macro.py           # FRED / TSA / BTS extractors
      edgar.py           # EDGAR submissions + document fetch
  build_quant_panel_v2.py  # v2 normalizer (extends v1 adapters)
tests/acquisition/
  test_fetch.py  test_integrity.py  test_manifest.py
  test_inside_airbnb.py  test_municipal.py
raw_expansion/v2_2026-09-05/
  inside_airbnb_current/  inside_airbnb_historical/  municipal/
  macro/  sec_edgar/  eurostat/  inside_airbnb_catalog/
raw_expansion_licensed/v2_2026-09-05/     # NEVER shareable
  bloomberg/  str_costar/
```

---

## Phase 0 — Preflight

### Task 1: Clear blockers and establish the immutability baseline

**Files:**
- Create: `metadata/expansion/preflight_report.md`

**Interfaces:**
- Produces: a verified-clean starting state that every later task assumes.

- [ ] **Step 1: Restore the three unreadable files**

Three files fail OneDrive hydration (reads time out in ~0.09s, 0 bytes):
`A_LEVEL_AIRBNB_DATA_EXPANSION_HANDOFF.md`, `processing/build_duckdb.py`, `tests/test_build_duckdb.py`.

In Finder: right-click the `AIRBNB DATA` folder → **Always Keep on This Device**. Wait for OneDrive to report "Up to date."

- [ ] **Step 2: Verify they now read**

```bash
for f in A_LEVEL_AIRBNB_DATA_EXPANSION_HANDOFF.md processing/build_duckdb.py tests/test_build_duckdb.py; do
  timeout 30 head -c 200 "$f" >/dev/null 2>&1 && echo "OK   $f" || echo "FAIL $f"
done
```

Expected: three `OK` lines. If any still `FAIL`, those files never finished uploading to OneDrive and must be regenerated — record that in the preflight report and continue; the DuckDB builder can be rewritten from `processed/airbnb_quant_panel_v1.duckdb`'s existing schema.

- [ ] **Step 3: Verify v1 integrity**

```bash
python3 -c "
import hashlib,csv
bad=n=0
for r in csv.DictReader(open('metadata/file_inventory.csv')):
    h=hashlib.sha256(open(r['local_path'],'rb').read()).hexdigest(); n+=1
    if h!=r['sha256']: print('MISMATCH',r['local_path']); bad+=1
print(f'v1 files: {n}, mismatches: {bad}')
assert n==53 and bad==0
"
```

Expected: `v1 files: 53, mismatches: 0`

- [ ] **Step 4: Confirm disk headroom**

```bash
df -g . | awk 'NR==2{print "free GB:",$4; if($4<15) print "WARNING: under 15GB, Task 5 will need pruning"}'
```

- [ ] **Step 5: Write the preflight report and commit**

Record: hydration outcome per file, v1 hash result, free GB, timestamp.

---

## Phase 1 — Shared acquisition library

### Task 2: Fetch, integrity, and manifest primitives

**Files:**
- Create: `processing/acquisition/__init__.py`, `fetch.py`, `integrity.py`, `manifest.py`
- Test: `tests/acquisition/test_fetch.py`, `test_integrity.py`, `test_manifest.py`

**Interfaces:**
- Produces:
  - `fetch.get(url: str, dest: Path, *, timeout=60) -> FetchResult` where `FetchResult` has `.status: int|str`, `.bytes: int`, `.classification: str` in `{"ok","source-restriction","local-fault"}`, `.url_final: str`
  - `fetch.head(url: str) -> HeadResult` with `.status`, `.content_length: int|None`
  - `fetch.encode_url(url: str) -> str` — percent-encodes non-ASCII path segments
  - `integrity.sha256_file(path: Path) -> str`
  - `integrity.validate(path: Path) -> ValidationResult` with `.ok: bool`, `.detail: str`, `.row_count: int|None`
  - `manifest.append_source(row: dict) -> None`, `manifest.append_files(rows: list[dict]) -> None`

- [ ] **Step 1: Write the failing tests**

```python
# tests/acquisition/test_fetch.py
from processing.acquisition import fetch

def test_encode_url_handles_non_ascii_path():
    u = "https://data.insideairbnb.com/argentina/ciudad-autónoma-de-buenos-aires/x/2024-04-28/data/listings.csv.gz"
    out = fetch.encode_url(u)
    assert "aut%C3%B3noma" in out
    assert out.startswith("https://data.insideairbnb.com/")

def test_encode_url_is_idempotent():
    u = "https://data.insideairbnb.com/hungary/k%C3%B6z%C3%A9p/x/2024-01-01/data/listings.csv.gz"
    assert fetch.encode_url(fetch.encode_url(u)) == fetch.encode_url(u)

def test_classify_403_is_source_restriction():
    assert fetch.classify(403) == "source-restriction"

def test_classify_404_is_source_restriction():
    assert fetch.classify(404) == "source-restriction"

def test_classify_503_is_local_fault_retryable():
    assert fetch.classify(503) == "local-fault"
```

```python
# tests/acquisition/test_integrity.py
import gzip
from processing.acquisition import integrity

def test_rejects_tiny_gzip_stub(tmp_path):
    p = tmp_path / "listings.csv.gz"
    p.write_bytes(b"x" * 511)
    assert integrity.validate(p).ok is False

def test_accepts_valid_gzip_csv(tmp_path):
    p = tmp_path / "listings.csv.gz"
    with gzip.open(p, "wt") as f:
        f.write("id,price\n1,100\n2,200\n")
    r = integrity.validate(p)
    assert r.ok is True and r.row_count == 2

def test_sha256_is_stable(tmp_path):
    p = tmp_path / "a.txt"; p.write_bytes(b"hello")
    assert integrity.sha256_file(p) == (
        "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/acquisition -v`
Expected: FAIL with `ModuleNotFoundError: processing.acquisition`

- [ ] **Step 3: Implement the minimal modules**

```python
# processing/acquisition/fetch.py
import time, urllib.parse, urllib.request, urllib.error
from dataclasses import dataclass
from pathlib import Path

UA = "UF-student-research theobmachado@gmail.com"
BACKOFF = (2, 8, 30)
SOURCE_RESTRICTION = {401, 402, 403, 404, 410, 451}

@dataclass
class FetchResult:
    status: object; bytes: int; classification: str; url_final: str

@dataclass
class HeadResult:
    status: object; content_length: int | None

def encode_url(url: str) -> str:
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit(
        (p.scheme, p.netloc, urllib.parse.quote(p.path, safe="/%"), p.query, p.fragment))

def classify(status) -> str:
    if status in SOURCE_RESTRICTION:
        return "source-restriction"
    return "local-fault"

def _req(url, method):
    return urllib.request.Request(encode_url(url), method=method, headers={"User-Agent": UA})

def head(url: str, timeout: int = 30) -> HeadResult:
    try:
        with urllib.request.urlopen(_req(url, "HEAD"), timeout=timeout) as r:
            cl = r.headers.get("Content-Length")
            return HeadResult(r.status, int(cl) if cl else None)
    except urllib.error.HTTPError as e:
        return HeadResult(e.code, None)
    except Exception:
        return HeadResult("ERR", None)

def get(url: str, dest: Path, *, timeout: int = 60, pace: float = 5.0) -> FetchResult:
    last = None
    for attempt, delay in enumerate((0,) + BACKOFF):
        if delay: time.sleep(delay)
        try:
            with urllib.request.urlopen(_req(url, "GET"), timeout=timeout) as r:
                dest.parent.mkdir(parents=True, exist_ok=True)
                data = r.read()
                dest.write_bytes(data)
                time.sleep(pace)
                return FetchResult(r.status, len(data), "ok", r.url)
        except urllib.error.HTTPError as e:
            last = e.code
            if classify(e.code) == "source-restriction":
                return FetchResult(e.code, 0, "source-restriction", url)
        except Exception:
            last = "ERR"
    return FetchResult(last, 0, "local-fault", url)
```

```python
# processing/acquisition/integrity.py
import csv, gzip, hashlib, io, json, zipfile
from dataclasses import dataclass
from pathlib import Path

MIN_GZ_BYTES = 2048

@dataclass
class ValidationResult:
    ok: bool; detail: str; row_count: int | None = None

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def validate(path: Path) -> ValidationResult:
    p = Path(path); name = p.name
    if name.endswith(".csv.gz"):
        if p.stat().st_size < MIN_GZ_BYTES:
            return ValidationResult(False, f"stub: {p.stat().st_size}b < {MIN_GZ_BYTES}")
        try:
            with gzip.open(p, "rt", encoding="utf-8", errors="replace") as f:
                rd = csv.reader(f); next(rd)
                return ValidationResult(True, "gzip csv ok", sum(1 for _ in rd))
        except Exception as e:
            return ValidationResult(False, f"gzip error: {e}")
    if name.endswith(".json"):
        try:
            json.loads(p.read_text(encoding="utf-8"))
            return ValidationResult(True, "json ok")
        except Exception as e:
            return ValidationResult(False, f"json error: {e}")
    if name.endswith(".zip"):
        try:
            with zipfile.ZipFile(p) as z:
                bad = z.testzip()
                return ValidationResult(bad is None, f"zip members={len(z.namelist())}")
        except Exception as e:
            return ValidationResult(False, f"zip error: {e}")
    if name.endswith(".csv"):
        try:
            with open(p, newline="", encoding="utf-8", errors="replace") as f:
                rd = csv.reader(f); next(rd)
                return ValidationResult(True, "csv ok", sum(1 for _ in rd))
        except Exception as e:
            return ValidationResult(False, f"csv error: {e}")
    return ValidationResult(True, "unchecked type")
```

```python
# processing/acquisition/manifest.py
import csv, os
from pathlib import Path

SRC = Path("metadata/expansion/expansion_source_manifest.csv")
INV = Path("metadata/expansion/expansion_file_inventory.csv")

def _append(path: Path, rows: list[dict]) -> None:
    if not rows: return
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        if new: w.writeheader()
        w.writerows(rows)

def append_source(row: dict) -> None: _append(SRC, [row])
def append_files(rows: list[dict]) -> None: _append(INV, rows)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/acquisition -v`
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git add processing/acquisition tests/acquisition
git commit -m "feat(acquisition): shared fetch, integrity, and manifest primitives"
```

---

## Phase 2 — Free sources

### Task 3: Inside Airbnb current — 34 US markets + all calendars and reviews

Highest coverage value in the plan. Closes the US gap and supplies the only realized-ADR and occupancy inputs available for free.

**Files:**
- Create: `processing/acquisition/sources/inside_airbnb.py`
- Test: `tests/acquisition/test_inside_airbnb.py`
- Output: `raw_expansion/v2_2026-09-05/inside_airbnb_current/<country>/<region>/<city>/<date>/{listings,calendar,reviews}.csv.gz`

**Interfaces:**
- Consumes: `fetch.get`, `fetch.head`, `integrity.validate`, `manifest.append_files`
- Produces: `inside_airbnb.parse_index(html: str) -> list[Snapshot]` where `Snapshot` is a NamedTuple `(country, region, city, date, kind, url)`; `inside_airbnb.plan_downloads(snapshots, held: set) -> list[Snapshot]`

- [ ] **Step 1: Write the failing test**

```python
# tests/acquisition/test_inside_airbnb.py
from processing.acquisition.sources import inside_airbnb as ia

HTML = '''<a href="https://data.insideairbnb.com/united-states/ny/new-york-city/2026-08-10/data/listings.csv.gz">l</a>
<a href="https://data.insideairbnb.com/united-states/ny/new-york-city/2026-08-10/data/calendar.csv.gz">c</a>
<a href="https://data.insideairbnb.com/france/ile-de-france/paris/2026-06-16/data/reviews.csv.gz">r</a>'''

def test_parse_index_extracts_all_three_kinds():
    s = ia.parse_index(HTML)
    assert len(s) == 3
    assert {x.kind for x in s} == {"listings", "calendar", "reviews"}

def test_parse_index_captures_geography_and_date():
    nyc = [x for x in ia.parse_index(HTML) if x.city == "new-york-city"][0]
    assert (nyc.country, nyc.region, nyc.date) == ("united-states", "ny", "2026-08-10")

def test_plan_downloads_skips_already_held():
    held = {("france", "ile-de-france", "paris", "2026-06-16", "reviews")}
    todo = ia.plan_downloads(ia.parse_index(HTML), held)
    assert all(t.city != "paris" for t in todo)
    assert len(todo) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/acquisition/test_inside_airbnb.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# processing/acquisition/sources/inside_airbnb.py
import re
from typing import NamedTuple

class Snapshot(NamedTuple):
    country: str; region: str; city: str; date: str; kind: str; url: str

PAT = re.compile(
    r'https?://data\.insideairbnb\.com/([^/"\']+)/([^/"\']+)/([^/"\']+)/'
    r'(\d{4}-\d{2}-\d{2})/data/(listings|calendar|reviews)\.csv\.gz')

def parse_index(html: str) -> list[Snapshot]:
    out, seen = [], set()
    for m in PAT.finditer(html):
        c, r, city, d, kind = m.groups()
        key = (c, r, city, d, kind)
        if key in seen: continue
        seen.add(key)
        out.append(Snapshot(c, r, city, d, kind, m.group(0)))
    return out

def plan_downloads(snapshots, held: set) -> list[Snapshot]:
    return [s for s in snapshots
            if (s.country, s.region, s.city, s.date, s.kind) not in held]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/acquisition/test_inside_airbnb.py -v`
Expected: 3 passed

- [ ] **Step 5: Refresh the index and build the download plan**

The preserved copy at `metadata/discovery/inside_airbnb_get_the_data.html` is from the v1 pass. Fetch a current one — snapshot dates roll.

```bash
python3 -c "
from pathlib import Path
from processing.acquisition import fetch
from processing.acquisition.sources import inside_airbnb as ia
p = Path('raw_expansion/v2_2026-09-05/inside_airbnb_catalog/get_the_data_current.html')
fetch.get('https://insideairbnb.com/get-the-data/', p, pace=0)
snaps = ia.parse_index(p.read_text(encoding='utf-8', errors='replace'))
print('snapshots on page:', len(snaps))
import collections; print(collections.Counter(s.kind for s in snaps))
"
```

Expected: ~360 snapshots, roughly 120 of each kind.

- [ ] **Step 6: Download in priority order with the disk guardrail**

Priority: (1) all 34 US `listings`, (2) all US `calendar` + `reviews`, (3) `calendar` for the 45 already-held cities, (4) `reviews` for those 45, (5) remaining non-US cities.

Between each batch:

```bash
df -g . | awk 'NR==2{if($4<5){print "ABORT: free GB",$4; exit 1}}' || exit 1
```

For every file: `fetch.get` → `integrity.validate` → reject and delete if `.ok is False` → `sha256_file` → `manifest.append_files`. Record `license_tier=cc_by_4_0` and attribute Inside Airbnb.

- [ ] **Step 7: Verify counts and commit**

```bash
find raw_expansion/v2_2026-09-05/inside_airbnb_current -name '*.csv.gz' | wc -l
python3 -c "
import csv
rows=[r for r in csv.DictReader(open('metadata/expansion/expansion_file_inventory.csv'))
      if 'inside_airbnb_current' in r['local_path']]
assert all(len(r['sha256'])==64 for r in rows)
print('inventoried:',len(rows),'bytes:',sum(int(r['bytes']) for r in rows))
"
git add -A raw_expansion metadata/expansion processing tests
git commit -m "feat(data): Inside Airbnb current US markets, calendars, and reviews"
```

---

### Task 4: Inside Airbnb historical — probe the 4,917-URL catalog, download the open subset

**Files:**
- Modify: `processing/acquisition/sources/inside_airbnb.py` (add `probe_catalog`)
- Output: `raw_expansion/v2_2026-09-05/inside_airbnb_catalog/availability_full.csv`, then `inside_airbnb_historical/<...>/`

**Interfaces:**
- Consumes: `historical_url_catalog.json` (4,917 URLs, already built), `fetch.head`
- Produces: `availability_full.csv` with columns `url,country,region,city,snapshot,kind,http,content_length,classification,probed_at_utc`

- [ ] **Step 1: Probe one date per country first**

Availability is country-consistent. Probing one date per country (~35 requests, ~3 min at 5s pacing) tells you which countries are worth a full probe and avoids burning hours on restricted ones.

```bash
python3 -c "
import json,collections
cat=json.load(open('raw_expansion/v2_2026-09-05/inside_airbnb_catalog/historical_url_catalog.json'))
from processing.acquisition.sources.inside_airbnb import parse_index
snaps=parse_index('\n'.join(cat))
bycountry=collections.defaultdict(list)
for s in snaps:
    if s.kind=='listings': bycountry[s.country].append(s)
print('countries:',len(bycountry))
"
```

- [ ] **Step 2: Full probe of open countries only**

HEAD every catalog URL whose country passed Step 1. Write `availability_full.csv`. Classify: `200` + `content_length >= 2048` → `available`; `200` + smaller → `stub-rejected`; `403/404` → `access-restricted-by-source`; else `local-fault` (retry once).

- [ ] **Step 3: Compute the disk budget before downloading**

```bash
python3 -c "
import csv
rows=[r for r in csv.DictReader(open('raw_expansion/v2_2026-09-05/inside_airbnb_catalog/availability_full.csv'))
      if r['classification']=='available' and r['content_length']]
tot=sum(int(r['content_length']) for r in rows)
print(f'available files: {len(rows)}  total: {tot/1e9:.2f} GB')
import collections
for k,v in sorted(collections.Counter(r['kind'] for r in rows).items()): print(' ',k,v)
"
```

If the total exceeds free space minus 5 GB, download `listings` for all available snapshots first, then `calendar`, then `reviews` (largest). Reviews are the least useful per byte for a nowcast — cut them first.

- [ ] **Step 4: Download, validate, hash, inventory**

Same pipeline as Task 3 Step 6. Record `wayback_capture_timestamp` (from the catalog value) as lineage on every row — this is how a reader knows which archived index vouched for the URL.

- [ ] **Step 5: Log every restriction and commit**

Append one `expansion_log.md` entry stating: countries probed, count available, count `access-restricted-by-source`, and the explicit note that no circumvention was attempted.

```bash
git add -A raw_expansion metadata/expansion
git commit -m "feat(data): Inside Airbnb historical snapshots, open subset only"
```

---

### Task 5: Municipal STR registries — the only route to US supply history

Every US historical Inside Airbnb probe returned 403. Registries are the substitute, and they are genuinely better for the regulatory thesis: official, licensed-open, and already time series.

**Files:**
- Create: `processing/acquisition/sources/municipal.py`
- Test: `tests/acquisition/test_municipal.py`
- Output: `raw_expansion/v2_2026-09-05/municipal/<city>/<dataset_id>_<retrieved_date>.csv`

**Interfaces:**
- Produces: `municipal.socrata_pages(domain: str, dataset_id: str, page: int = 50000) -> Iterator[str]` yielding CSV text pages; `municipal.REGISTRY` — the target list.

Targets (verify each dataset id on the portal before running; ids change):

| City | Portal domain | What to pull |
|---|---|---|
| New York City | `data.cityofnewyork.us` | Short-term rental registrations (LL18) |
| San Francisco | `data.sfgov.org` | Short-term residential rental registry |
| Los Angeles | `data.lacity.org` | Home-sharing registrations |
| Chicago | `data.cityofchicago.org` | Shared housing units |
| New Orleans | `data.nola.gov` | Short-term rental licenses |
| Boston | `data.boston.gov` (CKAN) | Short-term rental registrations |
| Seattle | `data.seattle.gov` | Short-term rental licenses |
| Denver | `denvergov.org` (ArcGIS) | STR licenses |
| Austin | `data.austintexas.gov` | STR licenses |
| Nashville | `data.nashville.gov` | STR permits |
| Barcelona | `opendata-ajuntament.barcelona.cat` | HUT tourist apartments |
| Amsterdam | `data.amsterdam.nl` | Vacation rental registrations |

- [ ] **Step 1: Write the failing test**

```python
# tests/acquisition/test_municipal.py
from processing.acquisition.sources import municipal

def test_socrata_url_builds_with_paging():
    u = municipal.socrata_url("data.cityofnewyork.us", "tjus-cn27", limit=1000, offset=2000)
    assert u.startswith("https://data.cityofnewyork.us/resource/tjus-cn27.csv")
    assert "$limit=1000" in u and "$offset=2000" in u

def test_registry_entries_are_well_formed():
    for e in municipal.REGISTRY:
        assert {"city", "domain", "dataset_id", "kind"} <= set(e)
        assert e["kind"] in {"socrata", "ckan", "arcgis"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/acquisition/test_municipal.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement**

```python
# processing/acquisition/sources/municipal.py
import urllib.parse

REGISTRY = [
    {"city": "new-york-city", "domain": "data.cityofnewyork.us", "dataset_id": "tjus-cn27", "kind": "socrata"},
    {"city": "san-francisco",  "domain": "data.sfgov.org",        "dataset_id": "kctv-5vwv", "kind": "socrata"},
    {"city": "chicago",        "domain": "data.cityofchicago.org","dataset_id": "cs6z-7ows", "kind": "socrata"},
    {"city": "new-orleans",    "domain": "data.nola.gov",         "dataset_id": "en36-xvxg", "kind": "socrata"},
    {"city": "austin",         "domain": "data.austintexas.gov",  "dataset_id": "uzqa-bfe7", "kind": "socrata"},
    {"city": "seattle",        "domain": "data.seattle.gov",      "dataset_id": "sz45-v9xa", "kind": "socrata"},
]

def socrata_url(domain: str, dataset_id: str, *, limit: int = 50000, offset: int = 0) -> str:
    q = urllib.parse.urlencode({"$limit": limit, "$offset": offset})
    return f"https://{domain}/resource/{dataset_id}.csv?{q}"

def socrata_pages(domain: str, dataset_id: str, page: int = 50000):
    from processing.acquisition import fetch
    from pathlib import Path
    import tempfile
    offset = 0
    while True:
        tmp = Path(tempfile.mkstemp(suffix=".csv")[1])
        r = fetch.get(socrata_url(domain, dataset_id, limit=page, offset=offset), tmp, pace=1.0)
        if r.classification != "ok": break
        text = tmp.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        if len(lines) <= 1: break
        yield text
        if len(lines) - 1 < page: break
        offset += page
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/acquisition/test_municipal.py -v`
Expected: 2 passed

- [ ] **Step 5: Verify each dataset id before bulk pulling**

Dataset ids in `REGISTRY` are starting guesses and **must be confirmed**. For each portal, hit the catalog search and correct the id:

```bash
curl -s "https://data.cityofnewyork.us/api/catalog/v1?q=short%20term%20rental&limit=5" \
  | python3 -c "import sys,json;[print(r['resource']['id'],'|',r['resource']['name'][:70]) for r in json.load(sys.stdin)['results']]"
```

Record the confirmed id, row count, and column list in the manifest before downloading. A wrong id silently returns a 404 page, not data — hence the `integrity.validate` gate.

- [ ] **Step 6: Download, validate, hash, inventory, commit**

Record `license_tier=open_gov` and the portal's stated terms per city.

```bash
git add -A raw_expansion/v2_2026-09-05/municipal metadata/expansion processing tests
git commit -m "feat(data): municipal short-term-rental registry extracts"
```

---

### Task 6: Macro demand series — free, high-frequency, real time series

**Files:**
- Create: `processing/acquisition/sources/macro.py`
- Output: `raw_expansion/v2_2026-09-05/macro/{fred,tsa,bts}/...`

**Interfaces:**
- Produces: `macro.fred_series(series_id: str, api_key: str) -> str` (CSV text); `macro.FRED_SERIES` list.

Targets:

| Source | Series / endpoint | Why |
|---|---|---|
| FRED | `CUSR0000SEHB` — CPI: Lodging away from home | ADR proxy, monthly, long history |
| FRED | `CUSR0000SS62031` — CPI: Housing at school/away | secondary lodging price |
| FRED | `USLAH` — All employees, leisure & hospitality | US travel-sector activity |
| FRED | `DSPIC96`, `PCEC96` | real income / consumption backdrop |
| FRED | `UMCSENT` | consumer sentiment, leads discretionary travel |
| TSA | `tsa.gov/travel/passenger-volumes` | daily US air throughput — highest-frequency demand read |
| BTS | `transtats.bts.gov` T-100 | international passenger flows |

FRED requires a **free** API key (`fred.stlouisfed.org/docs/api/api_key.html`) — registration only, no payment. Store it in the environment, never in the repo:

```bash
export FRED_API_KEY="..."   # add to ~/.zshrc, never commit
```

- [ ] **Step 1: Register the FRED key and verify it**

```bash
curl -s "https://api.stlouisfed.org/fred/series?series_id=CUSR0000SEHB&api_key=$FRED_API_KEY&file_type=json" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['seriess'][0]['title'])"
```

Expected: the series title prints. If it errors, the key is wrong — that is a `local-fault`, not a source restriction.

- [ ] **Step 2: Pull each series to CSV, validate, hash, inventory**

`license_tier=public_domain` for FRED-redistributed federal series and TSA/BTS. Note in the manifest that some FRED series are third-party-sourced with their own terms.

- [ ] **Step 3: Commit**

```bash
git add -A raw_expansion/v2_2026-09-05/macro metadata/expansion processing
git commit -m "feat(data): FRED, TSA, and BTS macro demand series"
```

---

### Task 7: SEC EDGAR — recover Nights & Experiences Booked and GBV from filing text

XBRL carries only standard `us-gaap` tags, so N&EB, GBV, and ADR must be parsed from the 10-Q/10-K MD&A and the quarterly shareholder letters.

**Files:**
- Create: `processing/acquisition/sources/edgar.py`
- Output: `raw_expansion/v2_2026-09-05/sec_edgar/filings/<accession>/<primary_doc>.htm`

**Interfaces:**
- Consumes: `raw_expansion/v2_2026-09-05/sec_edgar/abnb_submissions.json` (already held)
- Produces: `edgar.filing_urls(submissions: dict, forms=("10-Q","10-K")) -> list[tuple[str,str,str]]` of `(accession, form, url)`

- [ ] **Step 1: Enumerate filings from the held submissions file**

```bash
python3 -c "
import json
d=json.load(open('raw_expansion/v2_2026-09-05/sec_edgar/abnb_submissions.json'))
r=d['filings']['recent']
rows=[(a,f,pd) for a,f,pd in zip(r['accessionNumber'],r['form'],r['primaryDocument']) if f in ('10-Q','10-K')]
print('10-Q/10-K filings available:',len(rows))
for a,f,pd in rows[:6]: print(' ',f,a,pd)
"
```

- [ ] **Step 2: Download each primary document**

URL shape: `https://www.sec.gov/Archives/edgar/data/1559720/<accession-no-dashes>/<primaryDocument>`.
Pace 0.5s (EDGAR permits 10 req/s with an identifying User-Agent; stay well under).

- [ ] **Step 3: Extract the KPI table to a derived CSV**

Parse each filing for "Nights and Experiences Booked", "Gross Booking Value", and ADR. Write to `processed/airbnb_quant_panel_v2_staging/derived/abnb_reported_kpis.csv` with columns `metric,period_start,period_end,value,unit,accession,source_excerpt`.

Keep `source_excerpt` — a quoted sentence from the filing — so every number is auditable back to primary source. This is what makes the pitch defensible.

- [ ] **Step 4: Cross-check against XBRL revenue**

Revenue parsed from MD&A text must equal the XBRL value for the same period. Any mismatch is a parse bug, not a data discrepancy.

```bash
python3 -c "
import csv
x={r['end']:float(r['val_usd']) for r in csv.DictReader(open('processed/airbnb_quant_panel_v2_staging/derived/abnb_quarterly_kpis_derived.csv')) if r['metric']=='revenue_q'}
t={r['period_end']:float(r['value']) for r in csv.DictReader(open('processed/airbnb_quant_panel_v2_staging/derived/abnb_reported_kpis.csv')) if r['metric']=='revenue'}
bad=[k for k in set(x)&set(t) if abs(x[k]-t[k])>1e6]
print('compared:',len(set(x)&set(t)),'mismatches:',len(bad),bad)
assert not bad
"
```

- [ ] **Step 5: Commit**

```bash
git add -A raw_expansion/v2_2026-09-05/sec_edgar processed/airbnb_quant_panel_v2_staging processing
git commit -m "feat(data): ABNB filing documents and reported-KPI extraction"
```

---

## Phase 3 — Licensed sources (human-in-the-loop, non-redistributable)

### Task 8: Bloomberg terminal exports

Bloomberg cannot be driven agentically from this machine. A human runs the exports on the terminal; the agent ingests the resulting files. **The data is licensed and must never enter a shareable release.**

**Files:**
- Output: `raw_expansion_licensed/v2_2026-09-05/bloomberg/*.csv`
- Create: `raw_expansion_licensed/README.md` stating the non-redistribution rule

**What to export** (Bloomberg Excel Add-In, `=BDH()` for time series, `=BDP()` for point values):

| Export | Formula shape | Why it matters |
|---|---|---|
| Consensus revenue estimates | `=BDH("ABNB US Equity","BEST_SALES",start,end,"BEST_FPERIOD_OVERRIDE","1FQ")` | **The forecast benchmark** — a pitch is a variant view *against consensus* |
| Consensus EBITDA | `BEST_EBITDA` | margin guidance |
| Estimate revision history | `BEST_SALES` across vintages | shows which way the Street is drifting |
| Actual vs estimate surprise | `EARN_SURP_PCT` | calibrates how much surprise moves the stock |
| Guidance history | `GUIDANCE` fields / `ERN` screen | what management actually guided each quarter |
| Comps | same fields for `BKNG US`, `EXPE US`, `MAR US`, `HLT US`, `H US` | relative positioning |
| Price / volume | `PX_LAST`, `PX_VOLUME` daily | event studies around prints |

- [ ] **Step 1: Create the licensed subtree with its guard file**

```bash
mkdir -p raw_expansion_licensed/v2_2026-09-05/bloomberg
cat > raw_expansion_licensed/README.md <<'EOF'
Contents are licensed, non-redistributable terminal exports.
NEVER include in a published release, shared dataset, or CC BY 4.0 table.
Use for analysis and cited figures only. license_tier=licensed_norestribute.
EOF
printf 'raw_expansion_licensed/\n' >> .gitignore
```

- [ ] **Step 2: Human runs the exports, saves CSVs into the subtree**

- [ ] **Step 3: Agent validates, hashes, and inventories with the licensed tier**

Same `integrity.validate` → `sha256_file` → `manifest.append_files` pipeline, but every row gets `license_tier=licensed_norestribute` and `local_path` under `raw_expansion_licensed/`.

- [ ] **Step 4: Add a build-time assertion that licensed rows never leak**

```python
def test_no_licensed_rows_in_shareable_release():
    import duckdb
    con = duckdb.connect("processed/airbnb_quant_panel_v2/airbnb_quant_panel_v2.duckdb", read_only=True)
    n = con.execute(
        "select count(*) from listing_snapshots where license_tier='licensed_norestribute'").fetchone()[0]
    assert n == 0, f"{n} licensed rows leaked into the shareable release"
```

- [ ] **Step 5: Commit (metadata only — the data itself is gitignored)**

```bash
git add metadata/expansion .gitignore raw_expansion_licensed/README.md
git commit -m "feat(data): Bloomberg licensed cohort with non-redistribution guard"
```

---

### Task 9: STR / CoStar hotel benchmarks via UF library

Confirm entitlement first — UF's hospitality program may have STR SHARE, which is free to member institutions. If UF does not have it, mark this task `blocked: no-entitlement` and move on; nothing downstream hard-depends on it.

**Files:**
- Output: `raw_expansion_licensed/v2_2026-09-05/str_costar/*.csv`

**What to pull:** monthly hotel occupancy, ADR, and RevPAR by market, for the markets overlapping your Airbnb panel.

**Why it earns its place:** it is the denominator for a share-shift thesis. "Airbnb supply grew X% while hotel RevPAR grew Y% in the same market" is a far stronger claim than either number alone, and no free source provides the hotel side.

- [ ] **Step 1: Verify entitlement** via the UF library database A–Z list or the hospitality school's data desk.
- [ ] **Step 2: Export the overlapping markets** to CSV.
- [ ] **Step 3: Validate, hash, inventory** with `license_tier=licensed_norestribute`.
- [ ] **Step 4: Record the outcome in `expansion_log.md`** — including a clean "blocked: no-entitlement" if that is the answer.

---

## Phase 4 — Build

### Task 10: v2 release with cohort separation and coverage comparison

**Files:**
- Create: `processing/build_quant_panel_v2.py` (extends v1's adapter pattern)
- Output: `processed/airbnb_quant_panel_v2/` + `airbnb_quant_panel_v2.duckdb`

**Interfaces:**
- Consumes: every inventoried file from Tasks 3–9
- Produces: DuckDB tables `listing_snapshots`, `calendar_daily`, `review_events`, `market_snapshot_panel`, `macro_series`, `registry_records`, `reported_kpis`, `source_file_provenance`, `coverage_summary`, `field_availability`, `duplicate_overlap_assessment`, `transformation_log`, `output_manifest`

- [ ] **Step 1: Extend the row schema with the two new required columns**

Every fact row keeps v1's 59 columns plus:
- `license_tier` — legal handling (see Global Constraints)
- `wayback_capture_timestamp` — lineage for Task 4 rows, empty otherwise

- [ ] **Step 2: Keep incompatible cohorts separate**

Do **not** merge historical Inside Airbnb into the current cross-section by default. Assign `comparability_tier`:
- `core_current_cross_section` — current Inside Airbnb, one schema
- `core_historical_panel` — historical Inside Airbnb passing schema check, **the new tier that makes YoY possible**
- `supplemental_historical`, `supplemental_sample`, `exclude_synthetic_risk` — as in v1
- `registry_official`, `macro_reference`, `reported_actuals` — new non-listing tables

- [ ] **Step 3: Write the YoY pair assertion — the test that proves the plan worked**

```python
def test_v2_contains_real_year_over_year_pairs():
    import duckdb
    con = duckdb.connect("processed/airbnb_quant_panel_v2/airbnb_quant_panel_v2.duckdb", read_only=True)
    rows = con.execute("""
        select market, count(distinct strftime(record_snapshot_date,'%Y')) yrs,
               count(distinct source_file_id) files
        from listing_snapshots
        where comparability_tier in ('core_current_cross_section','core_historical_panel')
        group by 1 having yrs > 1 and files > 1
    """).fetchall()
    assert len(rows) >= 20, f"only {len(rows)} markets have multi-year coverage; v1 had 0"
```

The `files > 1` clause matters: v1 appeared to have 25 two-month markets, but each came from a **single** scrape spanning a week. Counting distinct source files is what separates a real repeat observation from a scrape artifact.

- [ ] **Step 4: Run it to verify it fails before the build**

Run: `python3 -m pytest tests/test_build_v2.py::test_v2_contains_real_year_over_year_pairs -v`
Expected: FAIL — the v2 database does not exist yet.

- [ ] **Step 5: Build, then run the full validation suite**

Reuse v1's staged-publish discipline exactly: build to temp → validate → copy once → re-hash → rename → refuse to overwrite.

- [ ] **Step 6: Write the coverage comparison versus v1**

`processed/airbnb_quant_panel_v2/coverage_vs_v1.md` must state, with numbers: markets added, US markets added, calendar/review files added, distinct snapshot vintages, YoY pairs created, and rows by `comparability_tier` and `license_tier`.

- [ ] **Step 7: Verify v1 is still untouched, then commit**

```bash
python3 -c "
import hashlib,csv
bad=n=0
for r in csv.DictReader(open('metadata/file_inventory.csv')):
    h=hashlib.sha256(open(r['local_path'],'rb').read()).hexdigest(); n+=1
    if h!=r['sha256']: bad+=1
print(f'v1 files: {n}, mismatches: {bad}'); assert n==53 and bad==0
"
git add -A processed/airbnb_quant_panel_v2 processing tests metadata/expansion
git commit -m "feat(panel): v2 release with historical cohort and license tiering"
```

---

## Disk Budget (measured, not estimated)

From the 72-URL paced probe: **61% of historical URLs are live**, mean `listings.csv.gz` = **4.6 MB**. Availability rises sharply with recency.

| Year | Live rate |
|---|---|
| 2021 | 42% |
| 2022 | 42% |
| 2023 | 50% |
| 2024 | 58% |
| 2025 | **83%** |
| 2026 | **92%** |

Catalog is 4,917 URLs ≈ 1,639 per kind. Projected full historical download:

| Kind | Live files | Mean size | Total |
|---|---:|---:|---:|
| listings | ~1,000 | 4.6 MB | **~4.6 GB** |
| calendar | ~1,000 | ~8 MB | ~8 GB |
| reviews | ~1,000 | ~20 MB | ~20 GB |
| **Total** | | | **~33 GB** |

**Free space is 7.9 GB.** Therefore:

1. **Take listings for 2024–2026 only** (58–92% live, most decision-relevant) ≈ 1.9 GB. This alone creates the YoY pairs.
2. **Convert each validated file to Parquet and delete the CSV.gz** — typically 3–5× smaller and far faster in DuckDB. Preserve the original SHA-256 in the manifest before conversion so provenance survives.
3. **Defer calendar and reviews history** until external storage is attached. Current-vintage calendars (Task 3) are the priority; historical reviews are the least useful per byte.
4. **Attach an external drive** and point `raw_expansion/` at it if you want the full 33 GB.

---

## Known Defects Every Downloader Must Handle

Observed live, not hypothetical:

1. **Non-ASCII paths raise.** All 6 Argentina probes returned `ERR` purely from `ciudad-autónoma-de-buenos-aires`. `fetch.encode_url` fixes this; `test_encode_url_handles_non_ascii_path` guards it. Hungary (`közép-magyarország`) has the same shape.
2. **HTTP 200 stubs.** `china/beijing/2023-03-29` returned 200 with 511 bytes. `integrity.validate` rejects `.csv.gz` under 2,048 bytes.
3. **403 is country-consistent.** 100% live: australia, belgium, belize, china, france, germany, greece. Mostly restricted: austria, brazil, chile, czech-republic, denmark. Probe one date per country before committing a paced budget.

---

## Self-Review

**Spec coverage:** Preflight (T1) → shared library (T2) → Inside Airbnb current incl. US (T3) → Inside Airbnb historical (T4) → municipal registries (T5) → macro (T6) → EDGAR KPIs (T7) → Bloomberg (T8) → STR (T9) → v2 build (T10). WRDS is deliberately excluded per instruction; nothing in T1–T10 depends on it. When WRDS access arrives it slots in beside T8 as an additional `licensed_norestribute` cohort with no rework.

**Interface consistency:** `fetch.get`/`fetch.head`/`fetch.encode_url`/`fetch.classify`, `integrity.validate`/`sha256_file`, `manifest.append_source`/`append_files` are named identically in every task that consumes them. `Snapshot` fields `(country, region, city, date, kind, url)` are used consistently in T3 and T4.

**Open risks:**
- Municipal dataset ids in T5 `REGISTRY` are unverified starting guesses. T5 Step 5 forces confirmation before bulk pulling — a wrong id returns an HTML 404 page that `integrity.validate` will reject rather than silently store.
- T7's KPI text parsing is the most brittle step; the XBRL cross-check in Step 4 is the guard.
- STR entitlement (T9) is unconfirmed and may end `blocked`. Nothing downstream hard-depends on it.

---

### Task 11: Common Crawl — independent price validation, NOT a panel source

**Measured 2026-09-05, do not re-litigate:**

| Test | Result |
|---|---|
| Crawl collections available | **127**, 2008 → Aug 2026 |
| `airbnb.com/rooms/*` records in CC-MAIN-2026-34 | **58** (42× HTTP 200, 10× 410, 5× 301, 1× 404) |
| Distinct listing ids in that crawl | **52** |
| Domain-wide `airbnb.com/*` | ~14 index blocks — also small |
| Mean captured body | 155 KB |
| Payload quality | **Excellent** — verified extraction of `ratingValue`, `reviewCount`, `latitude`, `roomType`, `personCapacity`, `price`, JSON-LD |

**Verdict:** 52 listings per monthly crawl against 626,612 in the current panel — roughly 0.008%. Common Crawl respects Airbnb's robots.txt, so listing pages are barely crawled. **It cannot serve as a panel source.** Do not build coverage claims on it.

**Two genuine uses that small N supports:**

1. **Independent price/rating validation.** CC captures are timestamped, third-party captures of what Airbnb actually rendered. Match CC listing ids against Inside Airbnb ids for nearby dates and compare `price` and `ratingValue`. This is a *data-quality audit* — 52 matched observations is ample to detect systematic bias in Inside Airbnb's scrape. No other free source can do this.
2. **Delisting evidence.** 10 of 58 records returned **410 Gone** — direct evidence of listing removal at a known timestamp, useful for survivorship-bias work.

**Licensing:** Common Crawl is a lawful public archive and accessing it is fine. The captured page content is Airbnb's copyrighted material — assign `license_tier=unlicensed_mirror`, use for validation only, never redistribute page bodies. Store extracted *fields* (numbers), not raw HTML.

- [ ] **Step 1: Enumerate records across crawls**

```bash
for CC in CC-MAIN-2026-34 CC-MAIN-2025-30 CC-MAIN-2024-33 CC-MAIN-2023-40; do
  curl -s --max-time 120 \
    "https://index.commoncrawl.org/${CC}-index?url=airbnb.com%2Frooms%2F*&output=json" \
    >> raw_expansion/v2_2026-09-05/common_crawl/index_records.jsonl
  sleep 5
done
```

Guard: the index endpoint truncates long responses. Parse defensively — skip unparseable lines rather than aborting:

```python
rows = []
for line in open(path):
    line = line.strip()
    if not line: continue
    try: rows.append(json.loads(line))
    except Exception: pass   # truncated tail line is expected
```

- [ ] **Step 2: Range-fetch only HTTP 200 records**

WARC records are byte-range addressable — never download whole WARC files (they are ~1 GB each).

```python
req = urllib.request.Request(
    "https://data.commoncrawl.org/" + r["filename"],
    headers={"Range": f"bytes={r['offset']}-{int(r['offset'])+int(r['length'])-1}",
             "User-Agent": "UF-student-research"})
body = gzip.decompress(urllib.request.urlopen(req, timeout=120).read()).decode("utf-8", "replace")
```

- [ ] **Step 3: Extract fields only, discard the HTML**

Write `processed/airbnb_quant_panel_v2_staging/derived/common_crawl_validation.csv` with
`listing_id, crawl_timestamp, http_status, price, rating_value, review_count, latitude, room_type, person_capacity, crawl_id`.

- [ ] **Step 4: Join to Inside Airbnb and report the delta**

```python
def test_inside_airbnb_prices_match_common_crawl_within_tolerance():
    # matched on listing_id where |date difference| <= 45 days
    # report median absolute % deviation; fail only if median > 25%
    assert median_abs_pct_dev < 25, f"Inside Airbnb price bias vs Common Crawl: {median_abs_pct_dev}%"
```

A large systematic gap is a finding worth reporting, not a bug to hide — it would mean Inside Airbnb's prices diverge from rendered prices, which every team using that data should know.

- [ ] **Step 5: Commit**

```bash
git add -A raw_expansion/v2_2026-09-05/common_crawl processed/airbnb_quant_panel_v2_staging metadata/expansion
git commit -m "feat(data): Common Crawl independent price validation cohort"
```
