"""Rebuild data/processed/abnb_quarterly_costlines.csv from SEC XBRL company facts.

Source: https://data.sec.gov/api/xbrl/companyfacts/CIK0001559720.json (Airbnb, CIK 1559720).
GAAP lines (cost of revenue, product development = ResearchAndDevelopmentExpense,
sales & marketing, G&A, restructuring, total costs, operating income, total SBC) come from
the API. Q4 = FY minus nine-month; Q2/Q3 are derived from YTD values where a discrete quarter
is missing. Operations & support is not a us-gaap tag, so it is backed out as
CostsAndExpenses minus the other five lines. Adjusted EBITDA is not in XBRL; it is keyed in
from the quarterly shareholder letters (8-K Ex. 99.1) and cross-checked against
research/airbnb_earnings_call_study.md.

Run: python analysis/src/abnb_costlines_from_xbrl.py
"""
import csv, datetime as dt, json, os, sys, urllib.request

CIK = "0001559720"
UA = os.environ.get("SEC_USER_AGENT", "Citadel-ABNB student research ksurapaneni@ufl.edu")
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "abnb_quarterly_costlines.csv")

TAGS = {"rev": "RevenueFromContractWithCustomerExcludingAssessedTax", "cor": "CostOfRevenue",
        "pd": "ResearchAndDevelopmentExpense", "sm": "SellingAndMarketingExpense",
        "ga": "GeneralAndAdministrativeExpense", "restr": "RestructuringCharges",
        "tot": "CostsAndExpenses", "opinc": "OperatingIncomeLoss",
        "sbc": "AllocatedShareBasedCompensationExpense"}

# Adjusted EBITDA ($M) as reported in each quarter's shareholder letter.
ADJ_EBITDA = {"1Q20": -334, "2Q20": -397, "3Q20": 501, "4Q20": -21, "1Q21": -59, "2Q21": 217,
              "3Q21": 1101, "4Q21": 333, "1Q22": 229, "2Q22": 711, "3Q22": 1457, "4Q22": 506,
              "1Q23": 262, "2Q23": 819, "3Q23": 1834, "4Q23": 738, "1Q24": 424, "2Q24": 894,
              "3Q24": 1958, "4Q24": 765, "1Q25": 417, "2Q25": 1043, "3Q25": 2051, "4Q25": 786,
              "1Q26": 519, "2Q26": 1261}


def fetch():
    req = urllib.request.Request(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json",
                                 headers={"User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=60))["facts"]["us-gaap"]


def series(facts, tag):
    out = {}
    for f in facts[tag]["units"]["USD"]:
        if "start" in f:
            out[(dt.date.fromisoformat(f["start"]), dt.date.fromisoformat(f["end"]))] = f["val"]
    return out


def main():
    facts = fetch()
    S = {k: series(facts, v) for k, v in TAGS.items()}

    def val(k, s, e):
        return S[k].get((s, e))

    def qval(k, y, q):
        qs = {1: (dt.date(y, 1, 1), dt.date(y, 3, 31)), 2: (dt.date(y, 4, 1), dt.date(y, 6, 30)),
              3: (dt.date(y, 7, 1), dt.date(y, 9, 30)), 4: (dt.date(y, 10, 1), dt.date(y, 12, 31))}
        s, e = qs[q]
        v = val(k, s, e)
        if v is not None:
            return v
        j1 = dt.date(y, 1, 1)
        pairs = {4: (dt.date(y, 12, 31), dt.date(y, 9, 30)), 3: (dt.date(y, 9, 30), dt.date(y, 6, 30)),
                 2: (dt.date(y, 6, 30), dt.date(y, 3, 31))}
        if q in pairs:
            a, b = val(k, j1, pairs[q][0]), val(k, j1, pairs[q][1])
            if a is not None and b is not None:
                return a - b
        return None

    rows = []
    for y in range(2020, dt.date.today().year + 1):
        for q in range(1, 5):
            r = {k: qval(k, y, q) for k in TAGS}
            if r["rev"] is None:
                continue
            core = ("tot", "cor", "pd", "sm", "ga")
            r["ops"] = (r["tot"] - (r["cor"] + r["pd"] + r["sm"] + r["ga"] + (r["restr"] or 0))
                        if all(r[k] is not None for k in core) else None)
            r["q"] = f"{q}Q{str(y)[2:]}"
            rows.append(r)

    def m(r, k):
        return "" if r.get(k) is None else round(r[k] / 1e6, 1)

    def p(r, k):
        return "" if r.get(k) is None else round(100 * r[k] / r["rev"], 1)

    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quarter", "revenue_musd", "cost_of_revenue_musd", "operations_and_support_musd",
                    "product_development_musd", "sales_and_marketing_musd", "general_and_administrative_musd",
                    "restructuring_musd", "stock_based_comp_total_musd", "operating_income_musd",
                    "adjusted_ebitda_musd", "cor_pct_rev", "ops_pct_rev", "pd_pct_rev", "sm_pct_rev",
                    "ga_pct_rev", "sbc_pct_rev", "adj_ebitda_margin_pct"])
        for r in rows:
            ae = ADJ_EBITDA.get(r["q"], "")
            w.writerow([r["q"], round(r["rev"] / 1e6, 1), m(r, "cor"), m(r, "ops"), m(r, "pd"), m(r, "sm"),
                        m(r, "ga"), m(r, "restr"), m(r, "sbc"), m(r, "opinc"), ae, p(r, "cor"), p(r, "ops"),
                        p(r, "pd"), p(r, "sm"), p(r, "ga"), p(r, "sbc"),
                        round(100 * ae / (r["rev"] / 1e6), 1) if ae != "" else ""])
    print(f"wrote {len(rows)} quarters to {os.path.normpath(OUT)}")


if __name__ == "__main__":
    sys.exit(main())
