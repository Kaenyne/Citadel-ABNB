"""HTTP acquisition with retry, pacing, and fault classification."""
import time, urllib.parse, urllib.request, urllib.error
from dataclasses import dataclass
from pathlib import Path

UA = "UF-student-research theobmachado@gmail.com"
BACKOFF = (2, 8, 30)
SOURCE_RESTRICTION = {401, 402, 403, 404, 410, 451}


@dataclass
class FetchResult:
    status: object
    bytes: int
    classification: str
    url_final: str


@dataclass
class HeadResult:
    status: object
    content_length: int | None


def encode_url(url: str) -> str:
    """Percent-encode non-ASCII path segments. Idempotent."""
    p = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit(
        (p.scheme, p.netloc, urllib.parse.quote(p.path, safe="/%"), p.query, p.fragment))


def classify(status) -> str:
    return "source-restriction" if status in SOURCE_RESTRICTION else "local-fault"


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


def get(url: str, dest: Path, *, timeout: int = 300, pace: float = 5.0) -> FetchResult:
    last = None
    for delay in (0,) + BACKOFF:
        if delay:
            time.sleep(delay)
        try:
            with urllib.request.urlopen(_req(url, "GET"), timeout=timeout) as r:
                dest.parent.mkdir(parents=True, exist_ok=True)
                data = r.read()
                dest.write_bytes(data)
                if pace:
                    time.sleep(pace)
                return FetchResult(r.status, len(data), "ok", r.url)
        except urllib.error.HTTPError as e:
            last = e.code
            if classify(e.code) == "source-restriction":
                return FetchResult(e.code, 0, "source-restriction", url)
        except Exception:
            last = "ERR"
    return FetchResult(last, 0, "local-fault", url)
