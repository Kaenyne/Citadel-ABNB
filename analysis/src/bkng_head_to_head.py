"""Airbnb vs Booking Holdings (and Expedia where XBRL allows), FY2021 to FY2025 margin structure.

Inputs
  data/raw/xbrl/ABNB.json, BKNG.json, EXPE.json   SEC XBRL company facts (https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json);
                                                  gitignored, downloaded if missing
  data/processed/abnb_quarterly_cost_stack_exsbc.csv   ABNB GBV, D&A and Adjusted EBITDA by quarter (letters)
  data/processed/abnb_fcf_bridge.csv                   ABNB capex by year (letters; XBRL capex stops at FY2022)

Hardcoded, with sources: ABNB brand and performance marketing (10-K sales-and-marketing split table), BKNG gross
bookings (Booking Holdings Q4 earnings press releases). Expedia gross bookings are not in XBRL, so its take rate is blank.

Metrics per company-year: revenue growth, take rate (revenue / gross bookings), marketing % revenue (ABNB brand and
performance marketing; BKNG marketing expense; EXPE advertising, with total selling and marketing as a memo), personnel
% revenue (BKNG only), SBC % revenue, EBITDA proxy margin = (operating income + D&A + SBC) / revenue, ABNB reported
Adjusted EBITDA margin, FCF margin = (CFO - capex) / revenue, FCF conversion = FCF / EBITDA proxy, buybacks % FCF,
diluted share count change.

Output: data/processed/abnb_vs_bkng_annual.csv
Run: python analysis/src/bkng_head_to_head.py
"""
import csv, json, os, sys, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
XBRL = os.path.join(ROOT, "data", "raw", "xbrl")
OUT = os.path.join(ROOT, "data", "processed", "abnb_vs_bkng_annual.csv")
UA = {"User-Agent": os.environ.get("SEC_USER_AGENT", "Citadel-ABNB student research ksurapaneni@ufl.edu")}
CIK = {"ABNB": 1559720, "BKNG": 1075531, "EXPE": 1324424}
YEARS = [2021, 2022, 2023, 2024, 2025]

# ABNB 10-K, sales and marketing table: brand and performance marketing ($M). FY2021 to FY2025 10-Ks.
ABNB_MARKETING = {2021: 723, 2022: 1030, 2023: 1208, 2024: 1455, 2025: 1595}
# Booking Holdings gross bookings ($B), Q4 earnings press releases (Feb 2023, Feb 2024, Feb 2025, Feb 2026).
BKNG_GROSS_BOOKINGS = {2022: 121.3, 2023: 150.6, 2024: 165.6, 2025: 186.1}

CONCEPTS = {  # metric -> candidate us-gaap concepts, first with data wins
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"],
    "marketing": ["MarketingExpense", "AdvertisingExpense"],
    "selling_and_marketing": ["SellingAndMarketingExpense"],
    "personnel": ["LaborAndRelatedExpense"],
    "op_income": ["OperatingIncomeLoss"],
    "da": ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization"],
    "sbc": ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"],
    "cfo": ["NetCashProvidedByUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment"],
    "buybacks": ["PaymentsForRepurchaseOfCommonStock"],
    "diluted_shares": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
}


def facts(tk):
    path = os.path.join(XBRL, f"{tk}.json")
    if not os.path.exists(path):
        os.makedirs(XBRL, exist_ok=True)
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK[tk]:010d}.json"
        open(path, "wb").write(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read())
    gaap = json.load(open(path))["facts"]["us-gaap"]
    out = {}
    for metric, names in CONCEPTS.items():
        for n in names:
            if n not in gaap:
                continue
            units = gaap[n]["units"]
            u = "USD" if "USD" in units else list(units)[0]
            vals = {int(f["frame"][2:]): f["val"] for f in units[u] if f.get("frame", "").startswith("CY") and len(f["frame"]) == 6}
            vals = {y: v / (1 if metric == "diluted_shares" else 1e6) for y, v in vals.items() if y in YEARS or y == 2020}
            if any(y in vals for y in YEARS):
                out[metric] = vals
                break
    return out


def abnb_from_letters():
    stack = list(csv.DictReader(open(os.path.join(ROOT, "data/processed/abnb_quarterly_cost_stack_exsbc.csv"))))
    gbv, da, adj = {}, {}, {}
    for r in stack:
        y = 2000 + int(r["quarter"][2:])
        gbv[y] = gbv.get(y, 0) + float(r["gbv_busd"])
        da[y] = da.get(y, 0) + float(r["da"])
        adj[y] = adj.get(y, 0) + float(r["adj_ebitda"])
    capex = {int(r["period"][2:]): -float(r["capex"]) for r in csv.DictReader(open(os.path.join(ROOT, "data/processed/abnb_fcf_bridge.csv")))
             if r["period"].startswith("FY")}
    return gbv, da, adj, capex


def pct(a, b):
    return round(100 * a / b, 1) if a is not None and b else None


def main():
    gbv_abnb, da_abnb, adj_abnb, capex_abnb = abnb_from_letters()
    rows = []
    for tk in ("ABNB", "BKNG", "EXPE"):
        f = facts(tk)
        if tk == "ABNB":
            f["da"] = da_abnb
            f["capex"] = {**f.get("capex", {}), **capex_abnb}
            f["marketing"] = ABNB_MARKETING
        for y in YEARS:
            g = lambda m, yy=y: f.get(m, {}).get(yy)
            rev, rev0 = g("revenue"), g("revenue", y - 1)
            gross = {"ABNB": gbv_abnb.get(y), "BKNG": BKNG_GROSS_BOOKINGS.get(y), "EXPE": None}[tk]
            ebitda = g("op_income") + g("da") + g("sbc")
            fcf = g("cfo") - g("capex")
            sh, sh0 = g("diluted_shares"), g("diluted_shares", y - 1)
            r = {"company": tk, "year": y, "revenue_musd": round(rev), "revenue_growth_pct": pct(rev - rev0, rev0) if rev0 else None,
                 "gross_bookings_busd": round(gross, 1) if gross else None, "take_rate_pct": round(100 * rev / (gross * 1000), 2) if gross else None,
                 "marketing_musd": round(g("marketing")), "marketing_pct_rev": pct(g("marketing"), rev),
                 "selling_and_marketing_pct_rev": pct(g("selling_and_marketing"), rev) if g("selling_and_marketing") else None,
                 "personnel_pct_rev": pct(g("personnel"), rev) if g("personnel") else None,
                 "sbc_musd": round(g("sbc")), "sbc_pct_rev": pct(g("sbc"), rev),
                 "op_income_musd": round(g("op_income")), "op_margin_pct": pct(g("op_income"), rev),
                 "da_musd": round(g("da")), "ebitda_proxy_musd": round(ebitda), "ebitda_proxy_margin_pct": pct(ebitda, rev),
                 "reported_adj_ebitda_margin_pct": pct(adj_abnb.get(y), rev) if tk == "ABNB" else None,
                 "cfo_musd": round(g("cfo")), "capex_musd": round(g("capex")), "fcf_musd": round(fcf), "fcf_margin_pct": pct(fcf, rev),
                 "fcf_conversion_pct": pct(fcf, ebitda), "buybacks_musd": round(g("buybacks")), "buybacks_pct_fcf": pct(g("buybacks"), fcf),
                 "diluted_shares_m": round(sh / 1e6, 1), "diluted_shares_change_pct": pct(sh - sh0, sh0) if sh0 else None}
            rows.append(r)
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows([{k: ("" if v is None else v) for k, v in r.items()} for r in rows])
    print(f"wrote {len(rows)} rows to {os.path.normpath(OUT)}")
    keys = ["revenue_growth_pct", "take_rate_pct", "marketing_pct_rev", "selling_and_marketing_pct_rev", "personnel_pct_rev", "sbc_pct_rev",
            "op_margin_pct", "ebitda_proxy_margin_pct", "reported_adj_ebitda_margin_pct", "fcf_margin_pct", "fcf_conversion_pct", "buybacks_pct_fcf", "diluted_shares_change_pct"]
    for k in keys:
        print(f"\n{k}")
        for tk in ("ABNB", "BKNG", "EXPE"):
            print(f"  {tk}: " + "  ".join(f"{y}={next(r[k] for r in rows if r['company'] == tk and r['year'] == y)}" for y in YEARS))


if __name__ == "__main__":
    sys.exit(main())
