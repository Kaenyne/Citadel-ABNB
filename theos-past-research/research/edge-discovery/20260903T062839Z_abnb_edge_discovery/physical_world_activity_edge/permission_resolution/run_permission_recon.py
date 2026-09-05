"""Fetch only preregistered official permission/metadata pages, once each.

No authentication, cookies, data endpoints, retries, or personal data are used.
Responses are cached and checksummed. A global 6.2-second spacing keeps the
request rate below ten requests per minute.
"""

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
MANIFEST = HERE / "permission_recon_manifest.csv"
RESULTS = HERE / "permission_recon_results.csv"
CACHE = HERE / "cache" / "permission_recon"
RATE_SECONDS = 6.2
STOP_HTTP = {401, 403, 429}
CAPTCHA_MARKERS = (
    b"captcha",
    b"cf-chl-",
    b"cloudflare ray id",
    b"verify you are human",
    b"robot check",
)

FIELDS = (
    "recon_id",
    "source_ids",
    "requested_url",
    "effective_safe_url",
    "requested_at_utc",
    "completed_at_utc",
    "http_status",
    "content_type",
    "bytes",
    "sha256",
    "cached_body_path",
    "outcome",
    "stop_reason",
)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))


def main() -> None:
    if RESULTS.exists():
        raise SystemExit(f"refusing to overwrite existing results: {RESULTS}")
    rows = list(csv.DictReader(MANIFEST.open(newline="", encoding="utf-8")))
    assert len(rows) == 26
    assert len({row["official_url"] for row in rows}) == 26
    CACHE.mkdir(parents=True, exist_ok=False)

    blocked_sources: set[str] = set()
    results: list[dict[str, str]] = []
    last_request_monotonic: float | None = None
    for row in rows:
        source_ids = set(row["source_ids"].split("|"))
        if source_ids and source_ids <= blocked_sources:
            results.append(
                {
                    "recon_id": row["recon_id"],
                    "source_ids": row["source_ids"],
                    "requested_url": row["official_url"],
                    "effective_safe_url": "",
                    "requested_at_utc": "",
                    "completed_at_utc": now_utc(),
                    "http_status": "",
                    "content_type": "",
                    "bytes": "",
                    "sha256": "",
                    "cached_body_path": "",
                    "outcome": "not_requested_source_stopped",
                    "stop_reason": "A prior permission GET for every linked source hit a stop condition; no retry or further request.",
                }
            )
            continue

        if last_request_monotonic is not None:
            remaining = RATE_SECONDS - (time.monotonic() - last_request_monotonic)
            if remaining > 0:
                time.sleep(remaining)

        request = urllib.request.Request(
            row["official_url"],
            method="GET",
            headers={
                "User-Agent": row["user_agent"],
                "Accept": "text/plain,text/html,application/json,application/xml;q=0.9,*/*;q=0.1",
            },
        )
        requested_at = now_utc()
        last_request_monotonic = time.monotonic()
        status = 0
        content_type = ""
        effective_url = row["official_url"]
        body = b""
        transport_error = ""
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status = response.status
                content_type = response.headers.get("Content-Type", "")
                effective_url = response.geturl()
                body = response.read()
        except urllib.error.HTTPError as error:
            status = error.code
            content_type = error.headers.get("Content-Type", "") if error.headers else ""
            effective_url = error.geturl()
            body = error.read()
            transport_error = f"HTTPError {error.code}"
        except Exception as error:  # one attempt only; no retry
            transport_error = f"{type(error).__name__}: {error}"

        digest = hashlib.sha256(body).hexdigest() if body else ""
        suffix = ".txt"
        if "json" in content_type.lower():
            suffix = ".json"
        elif "html" in content_type.lower():
            suffix = ".html"
        cache_path = CACHE / f"{row['recon_id']}{suffix}"
        if body:
            cache_path.write_bytes(body)

        lower = body[:2_000_000].lower()
        captcha = any(marker in lower for marker in CAPTCHA_MARKERS)
        if status in STOP_HTTP:
            outcome = "stopped"
            stop_reason = f"HTTP {status}; no retry"
            blocked_sources.update(source_ids)
        elif captcha:
            outcome = "stopped"
            stop_reason = "CAPTCHA or human-verification marker detected; no retry"
            blocked_sources.update(source_ids)
        elif transport_error:
            outcome = "transport_error"
            stop_reason = f"{transport_error}; no retry"
        elif 200 <= status < 300:
            outcome = "completed"
            stop_reason = ""
        else:
            outcome = "unexpected_status"
            stop_reason = f"HTTP {status}; no retry"

        results.append(
            {
                "recon_id": row["recon_id"],
                "source_ids": row["source_ids"],
                "requested_url": row["official_url"],
                "effective_safe_url": safe_url(effective_url),
                "requested_at_utc": requested_at,
                "completed_at_utc": now_utc(),
                "http_status": str(status) if status else "",
                "content_type": content_type,
                "bytes": str(len(body)) if body else "",
                "sha256": digest,
                "cached_body_path": str(cache_path.relative_to(HERE)) if body else "",
                "outcome": outcome,
                "stop_reason": stop_reason,
            }
        )
        print(row["recon_id"], row["source_ids"], status or "transport_error", outcome, flush=True)

    with RESULTS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(results)
    print(f"wrote {len(results)} rows to {RESULTS}")


if __name__ == "__main__":
    main()
