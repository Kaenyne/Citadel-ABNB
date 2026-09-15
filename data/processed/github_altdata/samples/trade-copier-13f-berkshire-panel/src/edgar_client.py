"""Pull 13F filings for one filer from SEC EDGAR's official, free JSON
API -- no HTML scraping.

Data sources (all documented, public, free):
  * https://data.sec.gov/submissions/CIK{cik}.json
        -> the filer's complete filing index.
  * https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/index.json
        -> the file listing for one filing.
  * .../{acc}/{infotable}.xml
        -> the structured 13F information table (holdings).

Everything fetched is cached under data/ so re-runs and the backtest do
not re-hit EDGAR. All fetched bytes are REAL SEC data.
"""
import json
import time
from dataclasses import dataclass

import requests

from config import SEC_HEADERS, SEC_REQUEST_SLEEP, DATA_DIR, FILER_CIK


@dataclass
class Filing:
    form: str
    filing_date: str      # YYYY-MM-DD, the date SEC received it
    report_date: str      # YYYY-MM-DD, the quarter-end the holdings are as of
    accession: str        # with dashes, e.g. 0001193125-26-352200
    primary_document: str

    @property
    def acc_nodash(self) -> str:
        return self.accession.replace("-", "")


def _get(url: str) -> requests.Response:
    time.sleep(SEC_REQUEST_SLEEP)
    r = requests.get(url, headers=SEC_HEADERS, timeout=30)
    r.raise_for_status()
    return r


def fetch_submissions(cik: str = FILER_CIK, use_cache: bool = True) -> dict:
    cik = cik.zfill(10)
    cache = DATA_DIR / f"submissions_CIK{cik}.json"
    if use_cache and cache.exists():
        return json.loads(cache.read_text())
    data = _get(f"https://data.sec.gov/submissions/CIK{cik}.json").json()
    cache.write_text(json.dumps(data))
    return data


def list_13f_filings(cik: str = FILER_CIK, include_amendments: bool = False,
                     use_cache: bool = True) -> list[Filing]:
    """Return all 13F-HR filings for the filer, newest first.

    The submissions JSON splits filings into a `recent` block plus, for
    prolific filers, older paginated `files`. We walk both so we get the
    full history, not just the last ~1000 filings.
    """
    data = fetch_submissions(cik, use_cache=use_cache)
    cik = cik.zfill(10)
    forms_wanted = {"13F-HR"} | ({"13F-HR/A"} if include_amendments else set())

    blocks = [data["filings"]["recent"]]
    for extra in data["filings"].get("files", []):
        cache = DATA_DIR / f"submissions_{extra['name']}"
        if use_cache and cache.exists():
            blocks.append(json.loads(cache.read_text()))
        else:
            b = _get(f"https://data.sec.gov/submissions/{extra['name']}").json()
            cache.write_text(json.dumps(b))
            blocks.append(b)

    filings: list[Filing] = []
    for b in blocks:
        for i, form in enumerate(b["form"]):
            if form in forms_wanted:
                filings.append(Filing(
                    form=form,
                    filing_date=b["filingDate"][i],
                    report_date=b["reportDate"][i],
                    accession=b["accessionNumber"][i],
                    primary_document=b["primaryDocument"][i],
                ))
    filings.sort(key=lambda f: f.report_date, reverse=True)
    return filings


def fetch_information_table_xml(filing: Filing, cik: str = FILER_CIK,
                                use_cache: bool = True) -> str:
    """Return the raw information-table XML for a filing.

    The info table has a random numeric filename that differs per
    filing, so we read the filing's index.json and pick the .xml that is
    NOT primary_doc.xml and that actually contains an <informationTable>.
    """
    cik = cik.lstrip("0")
    cache = DATA_DIR / f"infotable_{filing.acc_nodash}.xml"
    if use_cache and cache.exists():
        return cache.read_text()

    idx_url = (f"https://www.sec.gov/Archives/edgar/data/{cik}/"
               f"{filing.acc_nodash}/index.json")
    idx = _get(idx_url).json()
    candidates = [it["name"] for it in idx["directory"]["item"]
                  if it["name"].lower().endswith(".xml")
                  and it["name"].lower() != "primary_doc.xml"]
    if not candidates:
        raise RuntimeError(f"no info-table xml found for {filing.accession}")

    chosen_xml = None
    for name in candidates:
        url = (f"https://www.sec.gov/Archives/edgar/data/{cik}/"
               f"{filing.acc_nodash}/{name}")
        text = _get(url).text
        if "informationTable" in text or "infoTable" in text:
            chosen_xml = text
            break
    if chosen_xml is None:
        raise RuntimeError(f"no <informationTable> in any xml for {filing.accession}")

    cache.write_text(chosen_xml)
    return chosen_xml
