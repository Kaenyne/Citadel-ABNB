"""Hashing and structural validation. Rejects stub responses."""
import csv, gzip, hashlib, json, zipfile
from dataclasses import dataclass
from pathlib import Path

MIN_GZ_BYTES = 2048


@dataclass
class ValidationResult:
    ok: bool
    detail: str
    row_count: int | None = None


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def validate(path) -> ValidationResult:
    p = Path(path)
    n = p.name
    if n.endswith(".csv.gz"):
        if p.stat().st_size < MIN_GZ_BYTES:
            return ValidationResult(False, f"stub: {p.stat().st_size}b < {MIN_GZ_BYTES}")
        try:
            with gzip.open(p, "rt", encoding="utf-8", errors="replace") as f:
                rd = csv.reader(f)
                next(rd)
                return ValidationResult(True, "gzip csv ok", sum(1 for _ in rd))
        except Exception as e:
            return ValidationResult(False, f"gzip error: {e}")
    if n.endswith(".json") or n.endswith(".jsonl"):
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
            if n.endswith(".json"):
                json.loads(txt)
            return ValidationResult(True, "json ok")
        except Exception as e:
            return ValidationResult(False, f"json error: {e}")
    if n.endswith(".zip"):
        try:
            with zipfile.ZipFile(p) as z:
                return ValidationResult(z.testzip() is None, f"zip members={len(z.namelist())}")
        except Exception as e:
            return ValidationResult(False, f"zip error: {e}")
    if n.endswith(".csv") or n.endswith(".html"):
        return ValidationResult(p.stat().st_size > 512, f"{p.stat().st_size}b")
    return ValidationResult(True, "unchecked type")
