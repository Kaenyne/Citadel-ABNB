"""
02_peer_fetch.py - download peer earnings press releases (8-K Item 2.02, exhibit 99.1) and daily closes.

Peers: Booking Holdings (BKNG, CIK 1075531), Expedia Group (EXPE, CIK 1324424),
Marriott (MAR, CIK 1048286), Hilton (HLT, CIK 1585689). Window: filings dated 2021-01-01 onward
(covers the Q4 2020 print through Q2 2026).

Source of truth is SEC EDGAR, not the IR sites: the submissions API lists every 8-K with Item 2.02
(results of operations); the filing's index.json names the EX-99.1 press-release exhibit. Files land in
data/raw/peers/<TICKER>/ (gitignored) with a manifest data/raw/peers/peer_filings_manifest.csv.
Daily closes for the peers, ABNB and QQQ are in data/raw/prices/<TICKER>_daily.csv (Yahoo Finance via
yfinance, saved by the team; stooq.com blocks scripted downloads behind a JavaScript check).

Run: python analysis/src/predictive/02_peer_fetch.py   (skips files already present)
"""
import csv, json, os, re, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "peers"
UA = {"User-Agent": os.environ.get("SEC_USER_AGENT", "Citadel-ABNB student research ksurapaneni@ufl.edu")}
PEERS = {"BKNG": "0001075531", "EXPE": "0001324424", "MAR": "0001048286", "HLT": "0001585689"}
START = "2021-01-01"
PAUSE = 0.35  # SEC asks for <= 10 requests/second; stay well under
# Earnings 8-Ks filed without Item 2.02 (Expedia's Q4 2021 release, 10 Feb 2022, was filed under Item 9.01 only).
EXTRA = {"EXPE": ["0001324424-22-000006"]}


def get(url, binary=False):
    time.sleep(PAUSE)
    data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
    return data if binary else data.decode("utf-8", "replace")


def filings_for(cik):
    """All 8-K filings with Item 2.02 filed on/after START, from the submissions API (recent + archive pages)."""
    sub = json.loads(get(f"https://data.sec.gov/submissions/CIK{cik}.json"))
    pages = [sub["filings"]["recent"]] + [
        json.loads(get(f"https://data.sec.gov/submissions/{f['name']}")) for f in sub["filings"]["files"]
    ]
    out = []
    for f in pages:
        for form, items, fdate, acc, accept, doc in zip(
            f["form"], f["items"], f["filingDate"], f["accessionNumber"], f["acceptanceDateTime"], f["primaryDocument"]
        ):
            if form == "8-K" and fdate >= START and ("2.02" in items or acc in sum(EXTRA.values(), [])):
                out.append(dict(filing_date=fdate, acceptance=accept, accession=acc, primary_doc=doc, items=items))
    return sorted(out, key=lambda r: r["filing_date"])


def exhibit_99(cik, acc, primary_doc):
    """Return (name, url) of the press-release exhibit: the .htm in the filing that is not the 8-K itself.
    Exhibit file names vary by filer (ex991..., earningsrelease-q42020.htm, bnkgq42024earningspressr.htm,
    mar-2020q4earningsreleasee.htm, hiltonjan2021pressrelease.htm), so rank by keyword rather than require 'ex99'."""
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}"
    idx = json.loads(get(base + "/index.json"))
    names = [i["name"] for i in idx["directory"]["item"]]
    cands = [n for n in names if n.lower().endswith((".htm", ".html")) and n != primary_doc
             and "index" not in n.lower() and not re.match(r"R\d+\.htm", n)]
    def score(n):
        n = n.lower()
        return (0 if re.search(r"99[-_.]?0?1", n) else 1 if "99" in n else 2,
                0 if re.search(r"release|press|pr", n) else 1 if "earn" in n else 2, n)
    cands.sort(key=score)
    if not cands:
        return None, base
    return cands[0], f"{base}/{cands[0]}"


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = RAW / "peer_filings_manifest.csv"
    rows = []
    for tk, cik in PEERS.items():
        (RAW / tk).mkdir(exist_ok=True)
        for f in filings_for(cik):
            name, url = exhibit_99(cik, f["accession"], f["primary_doc"])
            local = RAW / tk / f"{f['filing_date']}_{f['accession']}_{name or 'NOEXHIBIT'}"
            if name and not local.exists():
                local.write_bytes(get(url, binary=True))
            rows.append(dict(ticker=tk, cik=cik, **f, exhibit=name or "", exhibit_url=url if name else "",
                             local_path=str(local.relative_to(ROOT)) if name else ""))
            print(tk, f["filing_date"], f["acceptance"], name)
    with open(manifest, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print("manifest ->", manifest, len(rows), "filings")

    # daily closes: already saved by the coordinator from yfinance in data/raw/prices/<TICKER>_daily.csv
    # (date, close, adj_close). Nothing to download; 02_peer_prints_build.py reads them directly.
    print("daily closes: data/raw/prices/{ABNB,BKNG,EXPE,MAR,HLT,QQQ}_daily.csv (yfinance, provided)")


if __name__ == "__main__":
    main()
