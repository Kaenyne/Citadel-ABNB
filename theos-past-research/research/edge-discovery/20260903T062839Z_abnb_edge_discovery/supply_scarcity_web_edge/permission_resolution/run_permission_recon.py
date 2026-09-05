"""Fetch preregistered official permission evidence with no retries or cookies."""

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
MANIFEST = ROOT / "permission_recon_manifest.csv"
RESULTS = ROOT / "permission_recon_results.csv"
CACHE = ROOT / "cache"
UA = "ABNB-Edge-Research/1.0 (institutional research; contact: repository-owner)"
MIN_HOST_INTERVAL_SECONDS = 7.0
MAX_BYTES = 8_000_000
RESULT_FIELDS = [
    "recon_id",
    "source_ids",
    "requested_url",
    "requested_at_utc",
    "effective_url",
    "http_status",
    "content_type",
    "response_bytes",
    "sha256",
    "body_cache_path",
    "headers_cache_path",
    "captcha_detected",
    "stop_status",
    "error",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def append_result(row: dict[str, object]) -> None:
    new_file = not RESULTS.exists()
    with RESULTS.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", nargs="+", required=True)
    args = parser.parse_args()
    wanted = set(args.ids)

    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        manifest = [row for row in csv.DictReader(handle) if row["recon_id"] in wanted]
    missing = wanted - {row["recon_id"] for row in manifest}
    if missing:
        raise SystemExit(f"Unregistered recon IDs: {sorted(missing)}")

    existing: set[str] = set()
    if RESULTS.exists():
        with RESULTS.open(newline="", encoding="utf-8") as handle:
            existing = {row["recon_id"] for row in csv.DictReader(handle)}

    last_request_by_host: dict[str, float] = {}
    stopped_hosts: set[str] = set()
    for row in manifest:
        recon_id = row["recon_id"]
        url = row["exact_official_url"]
        host = urllib.parse.urlsplit(url).hostname or ""
        if recon_id in existing:
            print(recon_id, "already_recorded")
            continue
        if host in stopped_hosts:
            append_result(
                {
                    "recon_id": recon_id,
                    "source_ids": row["source_ids"],
                    "requested_url": url,
                    "requested_at_utc": "",
                    "effective_url": "",
                    "http_status": "",
                    "content_type": "",
                    "response_bytes": 0,
                    "sha256": "",
                    "body_cache_path": "",
                    "headers_cache_path": "",
                    "captcha_detected": False,
                    "stop_status": "not_requested_after_host_stop",
                    "error": "prior request to this host triggered stop rule",
                }
            )
            continue

        elapsed = time.monotonic() - last_request_by_host.get(host, 0.0)
        if elapsed < MIN_HOST_INTERVAL_SECONDS:
            time.sleep(MIN_HOST_INTERVAL_SECONDS - elapsed)

        request = urllib.request.Request(
            url,
            method="GET",
            headers={
                "User-Agent": UA,
                "Accept": "text/html,text/plain,application/json,application/pdf;q=0.8,*/*;q=0.1",
                "Accept-Encoding": "identity",
                "Connection": "close",
            },
        )
        requested_at = utc_now()
        status = ""
        effective_url = ""
        content_type = ""
        body = b""
        headers_text = ""
        error = ""
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                last_request_by_host[host] = time.monotonic()
                status = response.status
                effective_url = response.geturl()
                content_type = response.headers.get("Content-Type", "")
                headers_text = str(response.headers)
                body = response.read(MAX_BYTES + 1)
                if len(body) > MAX_BYTES:
                    body = body[:MAX_BYTES]
                    error = f"response truncated at {MAX_BYTES} bytes"
        except urllib.error.HTTPError as exc:
            last_request_by_host[host] = time.monotonic()
            status = exc.code
            effective_url = exc.geturl()
            content_type = exc.headers.get("Content-Type", "") if exc.headers else ""
            headers_text = str(exc.headers or "")
            body = exc.read(MAX_BYTES)
            error = f"HTTPError {exc.code}"
        except Exception as exc:  # no retry by design
            last_request_by_host[host] = time.monotonic()
            error = f"{type(exc).__name__}: {exc}"

        digest = hashlib.sha256(body).hexdigest() if body else ""
        body_path = CACHE / f"{recon_id}.body"
        headers_path = CACHE / f"{recon_id}.headers.txt"
        if body:
            body_path.write_bytes(body)
        headers_path.write_text(headers_text, encoding="utf-8")
        sample = body[:250_000].lower()
        captcha = any(token in sample for token in (b"captcha", b"recaptcha", b"hcaptcha"))
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
        append_result(
            {
                "recon_id": recon_id,
                "source_ids": row["source_ids"],
                "requested_url": url,
                "requested_at_utc": requested_at,
                "effective_url": effective_url,
                "http_status": status,
                "content_type": content_type,
                "response_bytes": len(body),
                "sha256": digest,
                "body_cache_path": str(body_path.relative_to(ROOT)) if body else "",
                "headers_cache_path": str(headers_path.relative_to(ROOT)),
                "captcha_detected": captcha,
                "stop_status": stop,
                "error": error,
            }
        )
        print(recon_id, status, stop, len(body), digest)


if __name__ == "__main__":
    main()
