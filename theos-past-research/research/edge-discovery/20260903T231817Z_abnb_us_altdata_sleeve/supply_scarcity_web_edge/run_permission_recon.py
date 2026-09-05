"""One-pass permission-only collector for preregistered official pages."""

from __future__ import annotations

import argparse
import csv
import hashlib
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "permission_request_manifest.csv"
RESULTS = ROOT / "permission_request_results.csv"
CACHE = ROOT / "raw_cache" / "permission"
UA = "ABNB-altdata-research/1.0 (+https://github.com/theomachado05/airbnb-citadel-2026)"
MIN_INTERVAL = 7.0
MAX_BYTES = 8_000_000
FIELDS = (
    "recon_id", "source_id", "requested_url", "requested_at_utc", "effective_url",
    "http_status", "content_type", "response_bytes", "sha256", "body_cache_path",
    "headers_cache_path", "captcha_detected", "stop_status", "error",
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def append(row: dict[str, object]) -> None:
    new = not RESULTS.exists()
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if new:
            writer.writeheader()
        writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", nargs="+", required=True)
    args = parser.parse_args()
    wanted = set(args.ids)
    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        rows = [r for r in csv.DictReader(handle) if r["recon_id"] in wanted]
    if wanted != {r["recon_id"] for r in rows}:
        raise SystemExit("Every requested ID must be preregistered")
    existing: set[str] = set()
    if RESULTS.exists():
        with RESULTS.open(newline="", encoding="utf-8") as handle:
            existing = {r["recon_id"] for r in csv.DictReader(handle)}
    stopped_hosts: set[str] = set()
    last_by_host: dict[str, float] = {}
    CACHE.mkdir(parents=True, exist_ok=True)
    for row in rows:
        rid = row["recon_id"]
        url = row["exact_official_url"]
        host = urllib.parse.urlsplit(url).hostname or ""
        if rid in existing:
            print(rid, "already_recorded")
            continue
        if host in stopped_hosts:
            append({
                "recon_id": rid, "source_id": row["source_id"], "requested_url": url,
                "requested_at_utc": "", "effective_url": "", "http_status": "",
                "content_type": "", "response_bytes": 0, "sha256": "",
                "body_cache_path": "", "headers_cache_path": "", "captcha_detected": False,
                "stop_status": "not_requested_after_host_stop",
                "error": "prior request to host triggered stop rule",
            })
            continue
        elapsed = time.monotonic() - last_by_host.get(host, 0.0)
        if elapsed < MIN_INTERVAL:
            time.sleep(MIN_INTERVAL - elapsed)
        req = urllib.request.Request(url, method="GET", headers={
            "User-Agent": UA,
            "Accept": "text/html,text/plain,application/json;q=0.9,*/*;q=0.1",
            "Accept-Encoding": "identity", "Connection": "close",
        })
        requested_at = now()
        status: int | str = ""
        effective = ""
        ctype = ""
        headers = ""
        body = b""
        error = ""
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                last_by_host[host] = time.monotonic()
                status = response.status
                effective = response.geturl()
                ctype = response.headers.get("Content-Type", "")
                headers = str(response.headers)
                body = response.read(MAX_BYTES + 1)
                if len(body) > MAX_BYTES:
                    body = body[:MAX_BYTES]
                    error = f"truncated at {MAX_BYTES} bytes"
        except urllib.error.HTTPError as exc:
            last_by_host[host] = time.monotonic()
            status = exc.code
            effective = exc.geturl()
            ctype = exc.headers.get("Content-Type", "") if exc.headers else ""
            headers = str(exc.headers or "")
            body = exc.read(MAX_BYTES)
            error = f"HTTPError {exc.code}"
        except Exception as exc:
            last_by_host[host] = time.monotonic()
            error = f"{type(exc).__name__}: {exc}"
        body_path = CACHE / f"{rid}.body"
        headers_path = CACHE / f"{rid}.headers.txt"
        if body:
            body_path.write_bytes(body)
        headers_path.write_text(headers, encoding="utf-8")
        digest = hashlib.sha256(body).hexdigest() if body else ""
        sample = body[:250_000].lower()
        captcha = any(x in sample for x in (b"captcha", b"recaptcha", b"hcaptcha"))
        stop = "completed"
        if status in {401, 403, 429}:
            stop = f"stopped_http_{status}"
            stopped_hosts.add(host)
        elif captcha:
            stop = "stopped_captcha_detected"
            stopped_hosts.add(host)
        elif not status:
            stop = "stopped_network_error"
            stopped_hosts.add(host)
        append({
            "recon_id": rid, "source_id": row["source_id"], "requested_url": url,
            "requested_at_utc": requested_at, "effective_url": effective,
            "http_status": status, "content_type": ctype, "response_bytes": len(body),
            "sha256": digest,
            "body_cache_path": str(body_path.relative_to(ROOT)) if body else "",
            "headers_cache_path": str(headers_path.relative_to(ROOT)),
            "captcha_detected": captcha, "stop_status": stop, "error": error,
        })
        print(rid, status, stop, len(body), digest)


if __name__ == "__main__":
    main()
