"""Lawful source-capture controls and provenance helpers."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import hashlib
from pathlib import Path
import tempfile
import time
from urllib.parse import urlparse

import requests

from .records import SourceDocument


ALLOWED_OFFICIAL_HOSTS = frozenset(
    {
        "investors.airbnb.com",
        "airbnb2020ipo.q4web.com",
        "s26.q4cdn.com",
        "www.sec.gov",
        "sec.gov",
    }
)


def is_allowed_source(url: str, document_type: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_OFFICIAL_HOSTS:
        return False
    return document_type != "third_party_transcript"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def detect_duplicate_document(records: list[SourceDocument]) -> dict[str, list[str]]:
    by_digest: dict[str, list[str]] = defaultdict(list)
    for record in records:
        if record.sha256:
            by_digest[record.sha256].append(record.document_id)
    return {
        digest: sorted(document_ids)
        for digest, document_ids in sorted(by_digest.items())
        if len(document_ids) > 1
    }


def _require_sec_user_agent(url: str, user_agent: str) -> None:
    hostname = urlparse(url).hostname
    if hostname in {"sec.gov", "www.sec.gov"}:
        if "@" not in user_agent or len(user_agent.strip()) < 8:
            raise ValueError("SEC capture requires an identifying user agent with contact email")


def capture_official_document(
    record: SourceDocument,
    destination: Path,
    user_agent: str,
    *,
    session: requests.Session | None = None,
    timeout_seconds: int = 30,
) -> SourceDocument:
    if not is_allowed_source(record.source_url, record.document_type):
        raise ValueError(f"source is not approved for capture: {record.source_url}")
    _require_sec_user_agent(record.source_url, user_agent)
    if urlparse(record.source_url).hostname in {"sec.gov", "www.sec.gov"}:
        time.sleep(1.0)

    client = session or requests.Session()
    response = client.get(
        record.source_url,
        headers={"User-Agent": user_agent},
        timeout=timeout_seconds,
        stream=True,
    )
    response.raise_for_status()
    if not is_allowed_source(response.url, record.document_type):
        raise ValueError(f"redirect left approved hosts: {response.url}")

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=destination.parent, prefix=f".{destination.name}.", delete=False
        ) as handle:
            temporary_path = Path(handle.name)
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
        temporary_path.replace(destination)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    content_type = response.headers.get("Content-Type", "").split(";", 1)[0] or None
    return record.model_copy(
        update={
            "canonical_url": response.url,
            "retrieved_at_utc": datetime.now().astimezone(),
            "mime_type": content_type,
            "local_path": destination.as_posix(),
            "sha256": sha256_file(destination),
        }
    )
