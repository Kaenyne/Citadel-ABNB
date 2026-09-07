"""Enumerate exact-URL archive history for the eight fixed pilot leads.

Uses the documented Internet Archive CDX API. A zero result is unknown, and an
indexed HTTP 200 does not prove that the captured page contains a rental offer.
Never substitute a requested timestamp for the actual capture timestamp.
"""
import csv
from datetime import datetime, timezone
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request

from probe_listing_archives import ROOT, TARGETS, capture_timing

FROM = "20220101"
TO = "20260907"
LIMIT = 100


def indexed_rows(payload, label, case_id, sample):
    if not payload:
        return []
    fields, *records = payload
    required = {"timestamp", "original", "statuscode"}
    if not required.issubset(fields):
        raise ValueError("Archive index lacks required columns")
    result = []
    for record in records:
        if len(record) != len(fields):
            raise ValueError("Archive index row has wrong column count")
        row = dict(zip(fields, record))
        result.append({
            "case_id": case_id,
            "label": label,
            "archived_timestamp": row["timestamp"],
            "original_url": row["original"],
            "archived_url": "https://web.archive.org/web/" + row["timestamp"] + "/" + row["original"],
            "statuscode": row["statuscode"],
            "digest": row.get("digest", ""),
            "actual_timing": capture_timing(row["timestamp"], sample["last_present"], sample["first_terminal_absence"]),
            "interpretation": "Indexed response only; content requires separate inspection",
        })
    return result


def write_csv(path, rows, fields):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    raw = ROOT / "data/raw/listing_platform_history"
    out = ROOT / "data/processed/listing_platform_history"
    raw.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    with (ROOT / "data/raw/listing_churn_execution/destination_sample.csv").open(encoding="utf-8-sig", newline="") as handle:
        sample = {row["case_id"]: row for row in csv.DictReader(handle)}
    captures, log = [], []
    stop_network = False
    for label, (case_id, url) in TARGETS.items():
        query = "https://web.archive.org/cdx/search/cdx?" + urllib.parse.urlencode({
            "url": url, "output": "json", "fl": "timestamp,original,mimetype,statuscode,digest",
            "filter": "statuscode:200", "from": FROM, "to": TO,
            "limit": str(LIMIT), "gzip": "false",
        })
        path = raw / (label + "_cdx.json")
        record = dict(label=label, query_url=query, response_observed_at_utc="", loaded_from_cache=path.exists(),
                      query_status="", captures="", possibly_truncated="", sha256="", error="")
        try:
            if path.exists():
                body = path.read_bytes()
                # Cache file mtime is a fallback observation time, not a capture date.
                observed = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
            elif stop_network:
                record["query_status"] = "not_requested_after_access_limit"
                log.append(record)
                continue
            else:
                time.sleep(1)
                request = urllib.request.Request(query, headers={"User-Agent": "Citadel-ABNB public listing research"})
                with urllib.request.urlopen(request, timeout=30) as handle:
                    body = handle.read()
                path.write_bytes(body)
                observed = datetime.now(timezone.utc)
            payload = json.loads(body)
            rows = indexed_rows(payload, label, case_id, sample[case_id])
            captures.extend(rows)
            record.update(response_observed_at_utc=observed.isoformat(),
                          query_status="captures_indexed" if rows else "no_capture_returned",
                          captures=len(rows), possibly_truncated=len(rows) >= LIMIT,
                          sha256=hashlib.sha256(body).hexdigest())
        except Exception as exc:
            record.update(query_status="query_failed", error=f"{type(exc).__name__}: {exc}")
            if isinstance(exc, urllib.error.HTTPError) and exc.code in (401, 403, 429):
                stop_network = True
        log.append(record)
        print(label, record["query_status"], record["captures"], flush=True)
    fields = ["case_id", "label", "archived_timestamp", "original_url", "archived_url", "statuscode", "digest", "actual_timing", "interpretation"]
    write_csv(out / "archive_capture_index.csv", captures, fields)
    write_csv(out / "cdx_query_log.csv", log, list(log[0]))


if __name__ == "__main__":
    main()
