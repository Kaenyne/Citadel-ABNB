"""Pull keyless FRED series for WS04 (rates, wages, macro). Run: python analysis/src/margin_build/04_alt_signals/pull_fred.py --pull"""
import sys, hashlib, datetime as dt, urllib.request, pathlib, csv
ROOT = pathlib.Path(__file__).resolve().parents[4]
RAW = ROOT / "data/raw/margin_build/04_alt_signals/fred"; RAW.mkdir(parents=True, exist_ok=True)
SERIES = {
 "DTB3": ("3-month T-bill secondary market, daily", "interest_income"),
 "DGS1": ("1-year Treasury constant maturity, daily", "interest_income"),
 "FEDFUNDS": ("Effective fed funds, monthly", "interest_income"),
 "SOFR": ("SOFR, daily", "interest_income"),
 "ECBDFR": ("ECB deposit facility rate, daily", "interest_income"),
 "UMCSENT": ("UMich consumer sentiment, monthly", "macro_cycle"),
 "DSPIC96": ("Real disposable personal income, monthly", "macro_cycle"),
 "PCEC96": ("Real PCE, monthly", "macro_cycle"),
 "UNRATE": ("US unemployment rate, monthly", "macro_cycle"),
 "CES5051200001": ("Employment, software publishers (thousands), monthly", "product_dev_ga"),
 "CES5051200003": ("Avg hourly earnings, software publishers, monthly", "product_dev_ga"),
 "CES6054150001": ("Employment, computer systems design and related, monthly", "product_dev_ga"),
 "CES6054150003": ("Avg hourly earnings, computer systems design, monthly", "product_dev_ga"),
 "CES5000000003": ("Avg hourly earnings, information sector, monthly", "product_dev_ga"),
 "CUURS49BSA0": ("CPI-U San Francisco-Oakland-Hayward, bimonthly", "product_dev_ga"),
 "ECIWAG": ("Employment cost index wages and salaries private, quarterly", "product_dev_ga"),
 "JTS5100JOL": ("JOLTS job openings, information sector, monthly", "product_dev_ga"),
 "JTS5100LDL": ("JOLTS layoffs and discharges, information, monthly", "product_dev_ga"),
 "CES7072100001": ("Employment, accommodation (thousands), monthly", "macro_cycle"),
 "DEXUSEU": ("USD per EUR, daily", "fx"),
 "DTWEXBGS": ("Broad dollar index, daily", "fx"),
 "CPIAUCSL": ("CPI-U all items, monthly", "macro_cycle"),
 "PCU5182105182105": ("PPI data processing, hosting and related services", "cost_of_revenue"),
 "PCU54151054151011": ("PPI custom computer programming services", "product_dev_ga"),
 "PCU5415105415101": ("PPI computer systems design services", "product_dev_ga"),
 "PCU561422561422": ("PPI telemarketing bureaus and other contact centers", "ops_support"),
 "PCU5614205614201": ("PPI telephone call centers, inbound", "ops_support"),
 "PCU5242105242101": ("PPI insurance agencies and brokerages", "cost_of_revenue"),
 "CES6056142001": ("Employment, business support services (call centres etc.)", "ops_support"),
 "CES6056142003": ("Avg hourly earnings, business support services", "ops_support"),
}
def main(pull):
    man = []
    for sid, (desc, line) in SERIES.items():
        f = RAW / f"{sid}.csv"; url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
        status = "cached"
        if pull or not f.exists():
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "citadel-abnb research ksurapaneni@ufl.edu"})
                data = urllib.request.urlopen(req, timeout=60).read()
                if b"observation_date" not in data[:200] and b"DATE" not in data[:200]:
                    status = "error:" + data[:80].decode(errors="ignore").replace("\n"," "); 
                else:
                    f.write_bytes(data); status = "pulled"
            except Exception as e:
                status = f"error:{type(e).__name__}"
        sha = hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else ""
        n = (sum(1 for _ in open(f)) - 1) if f.exists() else 0
        man.append(dict(series=sid, description=desc, target_line=line, url=url, status=status, rows=n, sha256=sha,
                        pulled_at=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), licence="FRED public domain / BLS public"))
        print(sid, status, n)
    with open(RAW / "_fred_manifest.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(man[0].keys())); w.writeheader(); w.writerows(man)
if __name__ == "__main__":
    main("--pull" in sys.argv)
