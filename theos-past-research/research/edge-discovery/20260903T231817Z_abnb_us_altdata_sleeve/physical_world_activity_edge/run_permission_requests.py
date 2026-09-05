"""One-shot permission reconnaissance for canonical TSA and BTS sources."""

from __future__ import annotations

import csv
import hashlib
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "permission_request_manifest.csv"
RESULTS = HERE / "permission_request_results.csv"
CACHE = HERE / "raw_cache" / "permission_new"
SPACING_SECONDS = 6.7
STOP_HTTP = {401, 403, 429}
MARKERS = (b"captcha", b"cf-chl-", b"verify you are human", b"robot check")
FIELDS = (
    "request_id", "source_id", "requested_url", "effective_safe_url", "requested_at_utc",
    "completed_at_utc", "http_status", "content_type", "bytes", "sha256",
    "cached_path", "outcome", "stop_reason",
)


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe(url: str) -> str:
    p = urlsplit(url)
    return urlunsplit((p.scheme, p.netloc, p.path, p.query, ""))


def main() -> None:
    if RESULTS.exists():
        raise SystemExit(f"refusing to overwrite {RESULTS}")
    rows = list(csv.DictReader(MANIFEST.open(newline="", encoding="utf-8")))
    assert len(rows) == 11
    CACHE.mkdir(parents=True, exist_ok=False)
    stopped: set[str] = set()
    output: list[dict[str, str]] = []
    last: float | None = None
    for row in rows:
        if row["source_id"] in stopped:
            output.append({
                "request_id": row["request_id"], "source_id": row["source_id"],
                "requested_url": row["official_url"], "effective_safe_url": "",
                "requested_at_utc": "", "completed_at_utc": now(), "http_status": "",
                "content_type": "", "bytes": "", "sha256": "", "cached_path": "",
                "outcome": "not_requested_source_stopped",
                "stop_reason": "Prior permission request for source reached stop condition; no further request.",
            })
            continue
        if last is not None:
            delay = SPACING_SECONDS - (time.monotonic() - last)
            if delay > 0:
                time.sleep(delay)
        request = urllib.request.Request(row["official_url"], method="GET", headers={
            "User-Agent": row["user_agent"],
            "Accept": "text/plain,text/html,application/json;q=0.9,*/*;q=0.1",
        })
        started = now()
        last = time.monotonic()
        status = 0
        content_type = ""
        effective = row["official_url"]
        body = b""
        error_text = ""
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status = response.status
                content_type = response.headers.get("Content-Type", "")
                effective = response.geturl()
                body = response.read()
        except urllib.error.HTTPError as error:
            status = error.code
            content_type = error.headers.get("Content-Type", "") if error.headers else ""
            effective = error.geturl()
            body = error.read()
            error_text = f"HTTPError {error.code}"
        except Exception as error:
            error_text = f"{type(error).__name__}: {error}"
        digest = hashlib.sha256(body).hexdigest() if body else ""
        suffix = ".json" if "json" in content_type.lower() else ".html" if "html" in content_type.lower() else ".txt"
        cache = CACHE / f"{row['request_id']}{suffix}"
        if body:
            cache.write_bytes(body)
        lower = body[:2_000_000].lower()
        marker = any(value in lower for value in MARKERS)
        if status in STOP_HTTP:
            outcome, reason = "stopped", f"HTTP {status}; no retry"
            stopped.add(row["source_id"])
        elif marker:
            outcome, reason = "stopped", "CAPTCHA/human-verification marker detected; no retry"
            stopped.add(row["source_id"])
        elif error_text:
            outcome, reason = "transport_error", f"{error_text}; no retry"
        elif 200 <= status < 300:
            outcome, reason = "completed", ""
        else:
            outcome, reason = "unexpected_status", f"HTTP {status}; no retry"
            stopped.add(row["source_id"])
        output.append({
            "request_id": row["request_id"], "source_id": row["source_id"],
            "requested_url": row["official_url"], "effective_safe_url": safe(effective),
            "requested_at_utc": started, "completed_at_utc": now(),
            "http_status": str(status) if status else "", "content_type": content_type,
            "bytes": str(len(body)) if body else "", "sha256": digest,
            "cached_path": str(cache.relative_to(HERE)) if body else "",
            "outcome": outcome, "stop_reason": reason,
        })
        print(row["request_id"], row["source_id"], status or "transport_error", outcome, flush=True)
    with RESULTS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output)
    print(f"wrote {len(output)} rows")


if __name__ == "__main__":
    main()
