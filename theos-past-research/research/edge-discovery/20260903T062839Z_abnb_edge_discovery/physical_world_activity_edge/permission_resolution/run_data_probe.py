"""Run the single preregistered, aggregate-only NYC 311 data probe."""

from __future__ import annotations

import csv
import hashlib
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "data_probe_manifest.csv"
ASSESSMENTS = HERE / "data_path_assessments.csv"
RESULTS = HERE / "data_probe_results.csv"
CACHE = HERE / "cache" / "data_probe"
STOP_HTTP = {401, 403, 429}
CAPTCHA_MARKERS = (b"captcha", b"cf-chl-", b"cloudflare ray id", b"verify you are human", b"robot check")
FIELDS = (
    "probe_id", "source_id", "requested_safe_url", "effective_safe_url",
    "requested_at_utc", "completed_at_utc", "http_status", "content_type", "bytes",
    "sha256", "cached_payload_path", "outcome", "stop_reason", "endpoint",
    "observed_schema", "row_count", "vintage_assessment", "license_assessment",
)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))


def main() -> None:
    if RESULTS.exists():
        raise SystemExit(f"refusing to overwrite existing results: {RESULTS}")
    manifest = list(csv.DictReader(MANIFEST.open(newline="", encoding="utf-8")))
    decisions = {row["source_id"]: row for row in csv.DictReader(ASSESSMENTS.open(newline="", encoding="utf-8"))}
    assert len(manifest) == 1
    row = manifest[0]
    assert decisions[row["source_id"]]["assessment_allowed"] == "true"
    assert row["authentication"] == "none" and row["personal_data"] == "false"
    CACHE.mkdir(parents=True, exist_ok=False)

    request = urllib.request.Request(
        row["exact_safe_url"], method="GET",
        headers={"User-Agent": row["user_agent"], "Accept": "application/json"},
    )
    requested_at = now_utc()
    status = 0
    content_type = ""
    effective_url = row["exact_safe_url"]
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
    except Exception as error:
        transport_error = f"{type(error).__name__}: {error}"

    digest = hashlib.sha256(body).hexdigest() if body else ""
    cache_path = CACHE / "DP-PW-001.json"
    if body:
        cache_path.write_bytes(body)
    lower = body[:2_000_000].lower()
    captcha = any(marker in lower for marker in CAPTCHA_MARKERS)
    observed_schema = ""
    row_count = ""
    schema_ok = False
    if status == 200 and not captcha:
        try:
            parsed = json.loads(body)
            schema_ok = (
                isinstance(parsed, list)
                and len(parsed) == 1
                and isinstance(parsed[0], dict)
                and set(parsed[0]) == {"request_count"}
            )
            observed_schema = ";".join(sorted(parsed[0])) if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict) else "unexpected"
            row_count = str(len(parsed)) if isinstance(parsed, list) else ""
        except Exception:
            observed_schema = "invalid_json"
    if status in STOP_HTTP:
        outcome, stop_reason = "stopped", f"HTTP {status}; no retry"
    elif captcha:
        outcome, stop_reason = "stopped", "CAPTCHA or human-verification marker detected; no retry"
    elif transport_error:
        outcome, stop_reason = "transport_error", f"{transport_error}; no retry"
    elif status == 200 and schema_ok:
        outcome, stop_reason = "completed", ""
    elif status == 200:
        outcome, stop_reason = "unexpected_schema", "Response did not match the preregistered one-field aggregate schema; no retry"
    else:
        outcome, stop_reason = "unexpected_status", f"HTTP {status}; no retry"

    result = {
        "probe_id": row["probe_id"], "source_id": row["source_id"],
        "requested_safe_url": row["exact_safe_url"], "effective_safe_url": safe_url(effective_url),
        "requested_at_utc": requested_at, "completed_at_utc": now_utc(),
        "http_status": str(status) if status else "", "content_type": content_type,
        "bytes": str(len(body)) if body else "", "sha256": digest,
        "cached_payload_path": str(cache_path.relative_to(HERE)) if body else "",
        "outcome": outcome, "stop_reason": stop_reason,
        "endpoint": "/resource/erm2-nwe9.json",
        "observed_schema": observed_schema, "row_count": row_count,
        "vintage_assessment": "Current aggregate snapshot only; no historical publication vintage or revision timestamp; ineligible for historical replay.",
        "license_assessment": "NYC Open Data policy permits public application/feed use subject to source/version/modification identification; robots permits this path with Crawl-delay: 1.",
    }
    with RESULTS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(result)
    print(row["probe_id"], status or "transport_error", outcome, digest, flush=True)


if __name__ == "__main__":
    main()
