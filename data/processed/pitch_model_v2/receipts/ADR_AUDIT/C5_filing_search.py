"""C5 - adversarial search of SEC-filed documents for any magnitude attached to the product bundle
(Reserve Now Pay Later / cancellation-policy redesign / single fee).

Run from anywhere:  py -3.13 C5_filing_search.py [--fetch]

--fetch downloads at most two filed documents from www.sec.gov that are not on disk in either tree
(3Q25 10-Q, 2026 DEF 14A), logs each request in C5_fetch_log.json and saves the raw bytes under this folder.
The User-Agent is the one the repo already uses in analysis/src/pitch_model_v2/adr_engine/sizemix_adjudication.py.

Outputs (same folder): C5_filing_hits.csv, C5_term_counts.csv, C5_fetch_log.json.
Nothing outside this folder is written.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = Path(r"C:\Users\krish\citadel-abnb")
AUDIT = Path(r"C:\Users\krish\citadel-abnb-adraudit")

UA = "Citadel-ABNB-research theobmachado@gmail.com"  # verbatim from sizemix_adjudication.py line 63

FETCH_TARGETS = [
    ("10-Q 3Q25 (filed 2025-11-06, acc 0001559720-25-000030)",
     "https://www.sec.gov/Archives/edgar/data/1559720/000155972025000030/abnb-20250930.htm",
     HERE / "C5_fetched_abnb_2025q3_10q.html"),
    ("DEF 14A 2026 (filed 2026-04-24, acc 0001193125-26-175062)",
     "https://www.sec.gov/Archives/edgar/data/1559720/000119312526175062/d936646ddef14a.htm",
     HERE / "C5_fetched_abnb_2026_def14a.html"),
]

# (label, path, filed?)  -- filed = the document is itself an SEC filing or an exhibit to one
DOCS = [
    ("letter 2Q25 (8-K Ex99.1, 2025-08-06)", MAIN / "data/raw/letters/2Q25_d17531dex991.htm", True),
    ("letter 3Q25 (8-K Ex99.1, 2025-11-06)", MAIN / "data/raw/letters/3Q25_d40503dex991.htm", True),
    ("letter 4Q25 (8-K Ex99.1, 2026-02-12)", MAIN / "data/raw/letters/4Q25_d58192dex991.htm", True),
    ("letter 1Q26 (8-K Ex99.1, 2026-05-07)", MAIN / "data/raw/letters/1Q26_d23351dex991.htm", True),
    ("letter 2Q26 (8-K Ex99.1, 2026-08-06)", MAIN / "data/raw/letters/2Q26_d70413dex991.htm", True),
    ("10-K FY2025 (2026-02-12)", MAIN / "data/raw/filings/abnb_10k_FY2025.htm", True),
    ("10-Q 3Q25 (2025-11-06) [fetched]", FETCH_TARGETS[0][2], True),
    ("10-Q 1Q26 (2026-05-07)", AUDIT / "data/raw/regulatory/quantification/abnb_2026q1_10q.html", True),
    ("10-Q 2Q26 (2026-08-06)", MAIN / "data/raw/regulatory/quantification/abnb_2026q2_10q.html", True),
    ("DEF 14A 2026 (2026-04-24) [fetched]", FETCH_TARGETS[1][2], True),
    # transcripts: NOT filings; included only to verify the two quoted sentences verbatim
    ("transcript 3Q25 call (NOT a filing)", MAIN / "data/raw/transcripts/web/3Q25.html", False),
    ("transcript 4Q25 call (NOT a filing)", MAIN / "data/raw/transcripts/web/4Q25.html", False),
    ("transcript 1Q26 call (NOT a filing)", MAIN / "data/raw/transcripts/web/1Q26.html", False),
    ("transcript 2Q26 call (NOT a filing)", MAIN / "data/raw/transcripts/web/2Q26.html", False),
]

TERMS = {
    "RNPL": r"\bRNPL\b",
    "Reserve Now": r"reserve\s+now",
    "Pay Later": r"pay\s*,?\s*later",
    "pay less upfront": r"pay\s+less\s+upfront",
    "flexible payment": r"flexible\s+payment",
    "deferred payment": r"deferred\s+payment",
    "payment program": r"payment\s+program",
    "cancellation": r"cancell?ation",
    "single fee": r"single[\s-]+fee",
    "host-only fee": r"host[\s-]+only\s+fee",
    "simplified fee/pricing": r"simplif\w*\s+(fee|pricing|checkout)",
    "fee structure": r"fee\s+structure",
    "service fee": r"service\s+fee",
    "total price": r"total\s+price",
    "guest fee": r"guest\s+fee",
}
NUMBER = re.compile(
    r"(\d[\d,]*\.?\d*\s*(%|percent|percentage points?|points?|bps?|basis points?|x\b|times\b)"
    r"|\$\s?\d[\d,]*\.?\d*\s*(million|billion|thousand)?"
    r"|\b(one|two|three|four|five|six|seven|eight|nine|ten|twenty|thirty|forty|fifty)\s+"
    r"(percent|points?|basis points?|hundred basis points)"
    r"|\b\d{2,3}\s*basis\s*points?)",
    re.I,
)
MAG_HINT = re.compile(r"basis point|points? of|percentage point|contribut|deliver|drove|driven|helped|accelerat|"
                      r"headwind|tailwind|impact|growth|share of|% of|percent of", re.I)


def classify(s: str, nums_in_sent: list, matched: list) -> str:
    """Rule-based label. A 'bundle magnitude' would be a number in the SAME sentence that quantifies the
    contribution of RNPL / cancellation redesign / single fee to ADR, GBV, nights or revenue growth."""
    sl = s.lower()
    feature = bool(re.search(r"reserve now|pay later|rnpl|flexible payment|deferred payment|payment program|"
                             r"cancellation polic|single (service )?fee|fee structure|simplif", sl))
    if not nums_in_sent:
        return "no number in the sentence itself (number only in +/-2 sentence window)"
    if "these three features" in sl and re.search(r"basis points|points of", sl):
        return "BUNDLE MAGNITUDE (growth contribution) -- transcript, NOT a filing"
    if re.search(r"70% adoption", sl):
        return "RNPL adoption share of ELIGIBLE bookings (GBV basis) -- a share, not a contribution"
    if re.search(r"20% of (global|our total) gbv", sl):
        return "RNPL share of GBV -- a share, not a contribution"
    if re.search(r"installments", sl) or "brazil" in sl:
        return "Brazil installment-payments share of bookings value -- not RNPL, not the bundle"
    if re.search(r"\$0", sl) and feature:
        return "product parameter ($0 upfront) -- not a magnitude"
    if re.search(r"15\.5%|3% fee", sl):
        return "fee-rate parameter (3% / 15.5%) -- not a magnitude"
    if re.search(r"fcf increased 30%", sl):
        return "FCF growth with RNPL as a timing offset -- no magnitude for RNPL"
    if re.search(r"100 basis point", sl):
        return "interest-rate sensitivity boilerplate -- unrelated"
    if not feature:
        return "unrelated number (KPI table, definition, financial statement) -- keyword is generic"
    return "feature named; number in sentence is not a contribution magnitude (check by hand)"


def html_to_text(raw: bytes) -> str:
    try:
        from bs4 import BeautifulSoup  # type: ignore
        soup = BeautifulSoup(raw, "lxml")
        for t in soup(["script", "style"]):
            t.decompose()
        text = soup.get_text(" ")
    except Exception:
        text = re.sub(r"<[^>]+>", " ", raw.decode("utf-8", "ignore"))
    import html as _h
    text = _h.unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text)
    return text


def sentences(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text)
    # split on sentence enders followed by space+capital/quote/digit; keep abbreviations like U.S. together
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(\u201c])", flat)
    out = []
    for p in parts:
        p = p.strip()
        if p:
            out.append(p)
    return out


def fetch(log: list) -> None:
    for label, url, dest in FETCH_TARGETS:
        if dest.exists():
            log.append({"label": label, "url": url, "status": "already on disk", "bytes": dest.stat().st_size})
            continue
        t0 = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity",
                                                   "Host": "www.sec.gov"})
        entry = {"label": label, "url": url, "utc": t0}
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                entry["status"] = r.status
                entry["bytes"] = len(data)
                dest.write_bytes(data)
        except Exception as e:  # noqa
            entry["status"] = f"error: {e}"
            entry["bytes"] = 0
        log.append(entry)
        print(json.dumps(entry))


def main() -> int:
    log = []
    if "--fetch" in sys.argv:
        fetch(log)
        (HERE / "C5_fetch_log.json").write_text(json.dumps(log, indent=2), encoding="utf-8")

    hits = []
    counts = []
    for label, path, filed in DOCS:
        if not path.exists():
            counts.append({"document": label, "filed": filed, "path": str(path), "status": "MISSING"})
            continue
        text = html_to_text(path.read_bytes())
        sents = sentences(text)
        row = {"document": label, "filed": filed, "path": str(path), "status": "ok", "n_sentences": len(sents)}
        for name, pat in TERMS.items():
            row[name] = len(re.findall(pat, text, re.I))
        counts.append(row)
        seen = set()
        for i, s in enumerate(sents):
            matched = [n for n, p in TERMS.items() if re.search(p, s, re.I)]
            if not matched:
                continue
            lo, hi = max(0, i - 2), min(len(sents), i + 3)
            window = " ".join(sents[lo:hi])
            nums_in_sent = [m.group(0).strip() for m in NUMBER.finditer(s)]
            nums_in_window = [m.group(0).strip() for m in NUMBER.finditer(window)]
            if not nums_in_window:
                continue
            key = (label, s[:120])
            if key in seen:
                continue
            seen.add(key)
            hits.append({
                "document": label,
                "filed": filed,
                "sentence_index": i,
                "terms": ";".join(matched),
                "numbers_in_sentence": " | ".join(nums_in_sent),
                "numbers_in_window": " | ".join(nums_in_window),
                "magnitude_hint": bool(MAG_HINT.search(s)),
                "sentence": s[:600],
                "window": window[:1500],
                "classification": classify(s, nums_in_sent, matched),
            })

    with open(HERE / "C5_filing_hits.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(hits[0].keys()) if hits else ["document"])
        w.writeheader()
        w.writerows(hits)
    with open(HERE / "C5_term_counts.csv", "w", newline="", encoding="utf-8") as f:
        keys = ["document", "filed", "path", "status", "n_sentences"] + list(TERMS)
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(counts)

    print(f"{len(hits)} hit rows; {len(counts)} documents")
    for c in counts:
        print(c["document"], c["status"], {k: c.get(k) for k in ("RNPL", "Reserve Now", "Pay Later", "deferred payment",
                                                                  "flexible payment", "cancellation", "single fee",
                                                                  "service fee", "fee structure")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
