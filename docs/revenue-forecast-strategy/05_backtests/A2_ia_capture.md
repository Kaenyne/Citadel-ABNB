# A2 -- Daily Inside Airbnb capture (listings + calendar + reviews, 120 markets)

**Final status: the first daily run completed successfully at 2026-09-11 16:23:32 ET
(started 15:50 ET, ran 33.5 minutes under nohup, PID 24485).** All 360 files (120 markets x
listings/calendar/reviews) were fetched with `status=ok` -- zero failures, zero rejections,
zero source-restrictions, zero skips. 10.22 GB downloaded, comfortably inside the 15 GB cap
and the disk's headroom. (An earlier draft of this note, written mid-run at 15:54 ET while
watching the job progress, reported partial numbers; those are superseded by the final tally
below.)

## What the script does

`analysis/src/acquisition/ia_daily_capture.py` reuses the existing acquisition layer
(`analysis/src/acquisition/fetch.py`, `integrity.py`, `sources/inside_airbnb.py`) instead of
reinventing it:

1. **Market list**: loads the 120 `(country, region, city)` triples from
   `../raw_expansion/v2_2026-09-05/inside_airbnb_current_manifest.csv` (falls back to the
   `Theo Data/metadata/` mirror). Verified byte-identical (md5) to the Theo Data copy.
2. **Discovery**: fetches `https://insideairbnb.com/get-the-data/` once per run (cached to
   `data/manifests/ia_get_the_data_cache.html`, reused for 6h so repeat/test runs don't
   hammer the site) and parses it with `sources.inside_airbnb.parse_index()` -- the same
   regex-based parser `run_inside_airbnb.py` already uses. The page embeds direct CDN links
   for the **current** dump of every market, so this one fetch both discovers the latest
   dump date per market and gives the exact download URL. Confirmed: the live page currently
   lists exactly the same 120 markets as the manifest (differ only by Unicode NFC/NFD
   normalization of accented city/region names, e.g. "são-paulo"), so results are filtered
   to the 120-market list defensively but nothing is dropped today.
3. **Fetch**: HEAD-polls each expected URL (up to 3 attempts, 2s apart) before GET-ing it,
   with `fetch.py`'s existing retry/backoff and a real User-Agent
   (`UF-student-research theobmachado@gmail.com`), plus a 1.2s pace between GET requests.
4. **Manifest**: appends one row per file to
   `data/manifests/ia_daily_capture_manifest.csv` with columns
   `market, geo_id, dump_date, file, url, bytes, sha256, captured_at, status`.
5. **Idempotent**: a `(geo_id, dump_date, file)` already recorded `status=ok` in the manifest
   is skipped without a network call, provided the local file still exists at the expected
   path with the recorded byte size (cheap size check rather than a full re-hash, since a
   fixed dump URL is immutable on the CDN).
6. **Flags**: `--dry-run` (plans only, no downloads/manifest writes) and `--max-gb` (default
   15) which caps total bytes downloaded per run; the run also aborts early if free disk
   space on the capture volume drops below a 3 GB safety reserve.
7. Always exits 0 (so launchd never sees a "crashed" job) and writes a structured log to
   `data/manifests/ia_capture.log`, independent of how it's invoked.

Priority order inside one run: (0) listings + reviews for all 120 markets, (1) calendar for
the 13 "quote cities" found in `data/processed/overnight/06_quote_line_items.csv` /
`08_ia_dump_metrics.csv` (austin, barcelona, chicago, london, los-angeles, mexico-city,
nashville, new-orleans, new-york-city, paris, rome, san-diego, sydney), (2) calendar for the
remaining 107 markets.

## Commands run

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"

# 1. Storage check (no external Inside Airbnb volume was mounted -- only "Macintosh HD")
ls /Volumes
df -h

# 2. Dry run -- confirmed the full 360-file plan (120 markets x 3 kinds) needs only
#    ~10.2 GB, comfortably inside the 15 GB cap
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/acquisition/ia_daily_capture.py --dry-run --max-gb 15

# 3. Real run, backgrounded with nohup (downloads can run long; see "how to check" below)
mkdir -p ~/abnb_ia_capture
nohup /Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/acquisition/ia_daily_capture.py --max-gb 15 \
  > "data/manifests/ia_capture_nohup_run1.out" 2>&1 &
# PID: 24485
```

## Storage location

- **No external volume** holding Theo's existing Inside Airbnb store was mounted at run
  time (`ls /Volumes` showed only `Macintosh HD`). The script's `find_external_store()`
  scans `/Volumes` for a directory containing `inside_airbnb` on every run and will
  automatically switch to `<volume>/ia_daily_capture/` the day that drive is plugged in --
  no code change needed.
- Today's capture root: **`~/abnb_ia_capture/`** (i.e.
  `/Users/theomachado/abnb_ia_capture/`), **outside** the OneDrive tree as required.
  Layout: `<root>/<country>/<region>/<city>/<dump_date>/<listings|calendar|reviews>.csv.gz`.
- Free space on `/` (same physical volume as `~`): **~31 GiB before** the run started,
  **~20 GiB after** (down ~11 GB, of which 10.22 GB is the capture payload; the remainder is
  unrelated OS/app activity during the run). Still well above the script's 3 GB hard-floor
  reserve, with 20 GiB of headroom for tomorrow's run.

## What was fetched (final -- run completed 16:23:32 ET)

Every one of the 360 planned files (120 markets x 3 kinds) succeeded on the first attempt:

| file type | files ok | GB | markets covered |
|---|---|---|---|
| listings | 120 / 120 | 0.918 | 120 / 120 |
| reviews | 120 / 120 | 7.898 | 120 / 120 |
| calendar | 120 / 120 | 1.406 | 120 / 120 |
| **total** | **360 / 360** | **10.222** | **120 / 120** |

Priority order was followed exactly (log shows listings+reviews for all 120 markets
completing first, then the 13 quote-city calendars, then the remaining 107 calendars,
finishing with `washington-dc/calendar`), but because the whole job fit inside the 15 GB cap
with 4.8 GB of budget to spare, **the lower-priority tiers were reached too -- nothing had to
be skipped.**

**Nothing was skipped.** `skipped_cached=0`, `skipped_budget=0`, `skipped_low_disk=0`,
`rejected=0`, `restricted=0`, `failed=0`, `head_failed=0` (from the log's final `DONE` line).
Every dump date pulled was the single current dump listed on `insideairbnb.com/get-the-data/`
at run time (no historical backfill attempted -- that's a separate, larger effort given 28 of
73 historical CDN probes are already dead per the runbook).

## How to check the capture (PID 24485 has already exited -- run is done)

```bash
# Confirm it's finished (should show nothing / no such PID)
ps -p 24485

# Full row count should be 361 (360 data rows + header)
wc -l "data/manifests/ia_daily_capture_manifest.csv"

# Final summary line
tail -5 "data/manifests/ia_capture.log"
# -> DONE ok=360 skipped_cached=0 skipped_budget=0 skipped_low_disk=0 rejected=0
#    restricted=0 failed=0 head_failed=0 dry_run_would_fetch=0 budget_used=10.22GB of max 15.0GB

# Bytes on disk
du -sh ~/abnb_ia_capture   # -> 9.5G
```

## Schedule

`~/Library/LaunchAgents/com.citadel-abnb.ia-capture.plist` -- runs
`/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/acquisition/ia_daily_capture.py --max-gb 15`
daily at **06:00 local time**, `WorkingDirectory` set to the repo root, `StandardOutPath` /
`StandardErrorPath` both pointed at `data/manifests/ia_capture.log` (per spec; note this
means launchd-triggered runs show each log line twice in that file -- once from the script's
own file handle, once from the inherited stdout/stderr redirect -- this is intentional
belt-and-suspenders so the log stays populated even if the script dies before opening its
own handle, not a bug).

Loaded and confirmed:

```bash
launchctl load ~/Library/LaunchAgents/com.citadel-abnb.ia-capture.plist
launchctl list | grep ia-capture
# ->  -    0    com.citadel-abnb.ia-capture       (exit status 0, not currently running)
```

`RunAtLoad` is `false` (today's first pull was run manually/backgrounded instead, since
6:00 AM had already passed) -- the **next scheduled run is tomorrow, 2026-09-12 at 06:00
ET**.

### How Theo verifies tomorrow morning that the 06:00 run happened

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"

# 1. launchd ran it (look for a recent "Last exit code")
launchctl list | grep ia-capture

# 2. The log has a fresh entry for today, ending in a DONE line
grep "$(date +%Y-%m-%d)" data/manifests/ia_capture.log | tail -30

# 3. The manifest has new rows with today's captured_at date
awk -F, -v d="$(date +%Y-%m-%d)" '$0 ~ d' data/manifests/ia_daily_capture_manifest.csv | wc -l

# 4. Spot-check a file's hash against its manifest row
shasum -a 256 ~/abnb_ia_capture/united-states/tx/austin/<latest-date>/listings.csv.gz
```

If `launchctl list` shows a non-zero last exit code, or the log has no entry for today, the
job did not fire (check System Settings > Privacy & Security > Background items, and that
the Mac was awake/logged-in at 06:00 -- launchd agents do not run while the machine is
asleep or logged out) -- fall back to running the script manually and re-load the agent.

## Files touched

- `analysis/src/acquisition/ia_daily_capture.py` (new)
- `~/Library/LaunchAgents/com.citadel-abnb.ia-capture.plist` (new)
- `data/manifests/ia_daily_capture_manifest.csv` (new, append-only)
- `data/manifests/ia_capture.log` (new)
- `data/manifests/ia_get_the_data_cache.html` (new, discovery cache, refreshed every 6h)
- `data/manifests/ia_capture_nohup_run1.out` (new, raw stdout capture of today's manual run)
- `~/abnb_ia_capture/...` (new, outside the repo/OneDrive -- the actual `.csv.gz` payload)

No files under `analysis/src/forecast_methods/harness` or `/L0` were touched. No git commits
were made.
