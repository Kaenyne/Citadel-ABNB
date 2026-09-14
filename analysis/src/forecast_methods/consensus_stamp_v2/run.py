"""Capture public ABNB consensus and verify a byte-preserving L0 append.

Run from the repository root; see README.md. Never print environment secrets.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data/processed/forecast_methods/consensus_stamp_v2"
REGISTER = ROOT / "data/processed/forecast_methods/L0/L0_vintage_register.csv"


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def write_new(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="") as f:
        f.write(text)


def read_register(raw: bytes) -> list[dict]:
    return list(csv.DictReader(line for line in raw.decode("utf-8-sig").splitlines() if not line.startswith("#")))


def logical_sha256(raw: bytes) -> str:
    """Match Git text after CRLF->LF only; never rewrite register or backup."""
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()


def capture() -> None:
    import requests
    import yfinance as yf
    from bs4 import BeautifulSoup

    started = utc()
    directory = OUT / ("capture_" + started.replace("-", "").replace(":", ""))
    directory.mkdir(parents=True, exist_ok=False)
    records = []
    ticker = yf.Ticker("ABNB")
    for attribute in ("revenue_estimate", "earnings_estimate"):
        item = {"provider": "Yahoo Finance / LSEG family", "capture_method": "yfinance.Ticker(ABNB)." + attribute,
                "url": "https://finance.yahoo.com/quote/ABNB/analysis/", "capture_started_utc": utc()}
        try:
            frame = getattr(ticker, attribute)
            item.update(status="ok" if frame is not None and not frame.empty else "empty", captured_utc=utc())
            if frame is not None:
                path = directory / ("yfinance_" + attribute + ".csv")
                write_new(path, frame.to_csv())
                item.update(path=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), rows=len(frame))
        except Exception as exc:
            item.update(status="error", captured_utc=utc(), error_type=type(exc).__name__)
        records.append(item)

    pages = {
        "zacks": "https://www.zacks.com/stock/quote/ABNB/detailed-earning-estimates",
        "stockanalysis": "https://stockanalysis.com/stocks/abnb/forecast/",
    }
    for provider, url in pages.items():
        item = {"provider": provider, "url": url, "capture_method": "requests.get public HTML; BeautifulSoup visible text", "capture_started_utc": utc()}
        try:
            response = requests.get(url, timeout=25, headers={"User-Agent": "Mozilla/5.0"})
            item.update(http_status=response.status_code, captured_utc=utc(), response_sha256=hashlib.sha256(response.content).hexdigest())
            item["status"] = "ok" if response.ok else "http_error"
            if response.ok:
                soup = BeautifulSoup(response.content, "html.parser")
                for element in soup(["script", "style", "nav", "header", "footer"]):
                    element.decompose()
                path = directory / (provider + "_visible_text.txt")
                write_new(path, soup.get_text("\n", strip=True))
                item["path"] = path.relative_to(ROOT).as_posix()
                # Full raw responses are deliberately not saved or committed.
        except Exception as exc:
            item.update(status="error", captured_utc=utc(), error_type=type(exc).__name__)
        records.append(item)

    av_key = os.environ.get("ALPHAVANTAGE_API_KEY")
    item = {"provider": "Alpha Vantage / LSEG family", "url": "https://www.alphavantage.co/query?function=EARNINGS_ESTIMATES&symbol=ABNB", "capture_started_utc": utc()}
    if not av_key:
        item.update(status="skipped", reason="ALPHAVANTAGE_API_KEY absent")
    else:
        try:
            response = requests.get("https://www.alphavantage.co/query", params={"function": "EARNINGS_ESTIMATES", "symbol": "ABNB", "apikey": av_key}, timeout=25)
            payload = response.json()
            item.update(status="ok" if response.ok else "http_error", http_status=response.status_code, captured_utc=utc(), response_sha256=hashlib.sha256(response.content).hexdigest(), capture_method="Alpha Vantage EARNINGS_ESTIMATES API")
            path = directory / "alphavantage_estimates.json"
            write_new(path, json.dumps(payload, indent=2))
            item["path"] = path.relative_to(ROOT).as_posix()
        except Exception as exc:
            item.update(status="error", error_type=type(exc).__name__, captured_utc=utc())
    records.append(item)
    write_new(directory / "manifest.json", json.dumps({"started_utc": started, "finished_utc": utc(), "records": records}, indent=2))
    print(json.dumps({"output": directory.relative_to(ROOT).as_posix(), "records": records}, indent=2))


def append(candidates: Path, backup: Path) -> None:
    old = backup.read_bytes()
    current = REGISTER.read_bytes()
    if current != old:
        raise ValueError("Register differs from backup: concurrent modification or this run already appended")
    previous = read_register(old)
    candidate_rows = json.loads(candidates.read_text(encoding="utf-8"))
    if not candidate_rows:
        raise ValueError("No admissible rows; do not claim a vacuous append pass")
    fieldnames = list(previous[0])
    known_ids = {r["register_id"] for r in previous}
    rows = []
    for candidate in candidate_rows:
        row = {k: candidate[k] for k in fieldnames}
        if row["register_id"] in known_ids:
            raise ValueError("Duplicate register_id")
        known_ids.add(row["register_id"])
        if row["role"] != "current" or row["pit_usable"] is not True or row["vendor_attributed"] is not True:
            raise ValueError("New rows must be current and vendor attributed")
        if not row["vendor"] or not row["url"] or not row["source_path"] or not candidate["capture_method"]:
            raise ValueError("Incomplete provenance")
        if int(row["n_estimates"]) <= 0 or int(row["n_estimates"]) != float(row["n_estimates"]):
            raise ValueError("Missing or invalid analyst count")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z", row["as_of_timestamp"]):
            raise ValueError("Timestamp must be UTC to the minute")
        if row["as_of_timestamp"][:10] != utc()[:10]:
            raise ValueError("A current capture cannot be backdated")
        if not (ROOT / row["source_path"]).is_file():
            raise ValueError("Capture source missing")
        if not float("-inf") < float(row["value"]) < float("inf"):
            raise ValueError("Nonfinite value")
        rows.append(row)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writerows(rows)
    addition = ("" if old.endswith(b"\n") else "\n").encode() + buffer.getvalue().encode("utf-8")
    with REGISTER.open("ab") as f:
        f.write(addition)
    after = REGISTER.read_bytes()
    receipt = {
        "created_utc": utc(), "backup": backup.relative_to(ROOT).as_posix(),
        "candidates": candidates.relative_to(ROOT).as_posix(),
        "before_count": len(previous), "after_count": len(read_register(after)), "added": len(rows),
        "before_sha256": hashlib.sha256(old).hexdigest(), "after_sha256": hashlib.sha256(after).hexdigest(),
        "before_lf_sha256": logical_sha256(old), "after_lf_sha256": logical_sha256(after),
        "original_bytes_unchanged": after[:len(old)] == old,
        "august_row_byte_identical": [x for x in old.splitlines(keepends=True) if x.startswith(b"PG-2026Q3-revenue,")] == [x for x in after.splitlines(keepends=True) if x.startswith(b"PG-2026Q3-revenue,")],
        "added_by_vendor": {vendor: sum(r["vendor"] == vendor for r in rows) for vendor in sorted({r["vendor"] for r in rows})},
    }
    assert receipt["original_bytes_unchanged"] and receipt["august_row_byte_identical"]
    write_new(OUT / "append_receipt.json", json.dumps(receipt, indent=2))
    print(json.dumps(receipt, indent=2))


def verify() -> None:
    receipt = json.loads((OUT / "append_receipt.json").read_text(encoding="utf-8"))
    original = (ROOT / receipt["backup"]).read_bytes()
    current = REGISTER.read_bytes()
    assert current[:len(original)] == original, "An original byte changed"
    raw_match = hashlib.sha256(current).hexdigest() == receipt["after_sha256"] and hashlib.sha256(original).hexdigest() == receipt["before_sha256"]
    assert logical_sha256(original) == receipt["before_lf_sha256"], "Backup logical contents changed"
    assert logical_sha256(current) == receipt["after_lf_sha256"], "Register logical contents changed after append"
    assert len(read_register(current)) == receipt["after_count"]
    print(json.dumps({"status": "PASS", "rebuild_encoding_mode": "raw_capture_bytes" if raw_match else "git_text_normalized", **receipt}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", action="store_true")
    parser.add_argument("--append", type=Path)
    parser.add_argument("--backup", type=Path)
    arguments = parser.parse_args()
    if arguments.capture:
        capture()
    elif arguments.append:
        if not arguments.backup:
            parser.error("--backup required for append")
        append(arguments.append.resolve(), arguments.backup.resolve())
    else:
        verify()
