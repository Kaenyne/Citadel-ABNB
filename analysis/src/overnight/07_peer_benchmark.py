"""Workstream 07: peer margin benchmark, FY2021..FY2025, ABNB vs BKNG, EXPE, TRIP and platform peers UBER, DASH, META, NFLX, DUOL, SPOT.

Reads
  SEC XBRL company facts JSON per ticker (https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json), cached in
  XBRL_CACHE (default: the workstream scratchpad; set env XBRL_CACHE to another folder). Downloaded with the brief's User-Agent
  if missing. Spotify is an IFRS 20-F filer (EUR); converted at the FRED annual average EUR/USD (AEXUSEU) hardcoded below.
  data/processed/abnb_quarterly_cost_stack_exsbc.csv  ABNB nights, GBV, Adjusted EBITDA (letters)
  data/processed/abnb_fcf_bridge.csv                  ABNB capex by year (XBRL capex tag stops in FY2022)
  Hardcoded with sources: employee counts (each company's 10-K Item 1 / 20-F Item 6), unit volumes (BKNG room nights, UBER trips,
  DASH orders from 10-K key metrics tables), reported adjusted EBITDA where the company publishes one (ABNB letters; BKNG Q4 press
  releases; EXPE, UBER, DASH 10-K reconciliation tables), ABNB brand+performance marketing (10-K split table).

Writes
  data/processed/overnight/07_peer_margin_benchmark.csv   one row per company-year

Run: py -3.13 analysis/src/overnight/07_peer_benchmark.py
"""
import csv, json, os, urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
P = lambda *a: os.path.join(ROOT, *a)
CACHE = os.environ.get("XBRL_CACHE", r"C:\Users\krish\AppData\Local\Temp\claude\C--Users-krish-citadel-abnb\fe93ae72-a37b-4547-991f-690c32a0f6a0\scratchpad\07")
UA = {"User-Agent": "citadel-abnb research ksurapaneni@ufl.edu"}
CIK = {"ABNB": 1559720, "BKNG": 1075531, "EXPE": 1324424, "TRIP": 1526520, "UBER": 1543151, "DASH": 1792789, "META": 1326801, "NFLX": 1065280, "DUOL": 1562088, "SPOT": 1639920}
YEARS = [2021, 2022, 2023, 2024, 2025]
EURUSD = {2021: 1.1830, 2022: 1.0534, 2023: 1.0817, 2024: 1.0820, 2025: 1.1306}  # FRED AEXUSEU annual average

# tag candidates per metric (first with data wins); IFRS names for SPOT
TAGS = {
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "Revenue"],
    "op_income": ["OperatingIncomeLoss", "ProfitLossFromOperatingActivities"],
    "sbc": ["AllocatedShareBasedCompensationExpense", "ShareBasedCompensation", "ExpenseFromSharebasedPaymentTransactionsWithEmployees"],
    "da": ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization"],
    "da_dep_ifrs": ["AdjustmentsForDepreciationExpense"], "da_amort_ifrs": ["AdjustmentsForAmortisationExpense"],
    "sm": ["SellingAndMarketingExpense", "SalesAndMarketingExpense", "MarketingExpense"],
    "marketing_only": ["MarketingExpense", "AdvertisingExpense"],
    "rd": ["ResearchAndDevelopmentExpense"], "ga": ["GeneralAndAdministrativeExpense"], "cor": ["CostOfRevenue", "CostOfSales"],
    "cfo": ["NetCashProvidedByUsedInOperatingActivities", "CashFlowsFromUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities"],
    "buybacks": ["PaymentsForRepurchaseOfCommonStock"],
    "diluted_shares": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
    "interest_income": ["InvestmentIncomeInterest", "InvestmentIncomeNonoperating"],
    "tax": ["IncomeTaxExpenseBenefit"], "net_income": ["NetIncomeLoss"],
}

EMPLOYEES = {  # Dec 31 headcount, 10-K Item 1 (SPOT: average full-time employees, 20-F Item 6)
    "ABNB": {2021: 6132, 2022: 6811, 2023: 6907, 2024: 7300, 2025: 8200},
    "BKNG": {2021: 20300, 2022: 21600, 2023: 23600, 2024: 24300, 2025: 24300},
    "EXPE": {2021: 14800, 2022: 16500, 2023: 17100, 2024: 16500, 2025: 16000},
    "TRIP": {2021: 2691, 2022: 3100, 2023: 2845, 2024: 2860, 2025: 2590},
    "UBER": {2021: 29300, 2022: 32800, 2023: 30400, 2024: 31100, 2025: 34000},
    "DASH": {2021: 8600, 2022: 16800, 2023: 19300, 2024: 23700, 2025: 31400},
    "META": {2021: 71970, 2022: 86482, 2023: 67317, 2024: 74067, 2025: 78865},
    "NFLX": {2021: 11300, 2022: 12800, 2023: 13000, 2024: 14000, 2025: 16000},
    "DUOL": {2021: 500, 2022: 600, 2023: 720, 2024: 830, 2025: 900},
    "SPOT": {2021: 6617, 2022: 8359, 2023: 9123, 2024: 7691, 2025: 7287},
}
UNITS = {  # millions; ABNB nights booked (letters), BKNG room nights (10-K), UBER trips (10-K), DASH total orders (10-K)
    "BKNG": ("room nights", {2021: 591, 2022: 896, 2023: 1049, 2024: 1144, 2025: 1235}),
    "UBER": ("trips", {2021: 6368, 2022: 7642, 2023: 9448, 2024: 11273, 2025: 13567}),
    "DASH": ("orders", {2021: 1390, 2022: 1736, 2023: 2161, 2024: 2583, 2025: 3172}),
}
REPORTED_ADJ_EBITDA = {  # $M, company definition
    "BKNG": {2022: 5300, 2023: 7100, 2025: 9900},     # Q4 press releases (Feb 2023, Feb 2024; FY2025 from the margin note S32 citing the Feb 2026 release).
                                                      # FY2024 is deliberately blank: the Q4 2024 release text is in images and the FY2025 10-K only gives the SEGMENT measure
                                                      # ("Segment Adjusted EBITDA less Capex" $9,852 / $8,179 / $7,020 for 2025 / 2024 / 2023, plus additions to property and
                                                      # equipment $350 / $445 / $395), which is not the same definition: segment 2023 = $7,415M against $7,100M in the release.
                                                      # Use ebitda_proxy_margin_pct for any cross-company comparison; it is computed the same way for all ten names.
    "EXPE": {2021: 1477, 2022: 2349, 2023: 2680, 2024: 2934, 2025: 3501},  # 10-K FY2023 and FY2025 reconciliation tables
    "UBER": {2022: 1713, 2023: 4052, 2024: 6484, 2025: 8730},              # 10-K FY2023 and FY2025
    "DASH": {2021: 289, 2022: 361, 2023: 1190, 2024: 1900, 2025: 2779},    # 10-K FY2023 and FY2025
    "TRIP": {2021: 100, 2022: 295, 2023: 334, 2024: 339, 2025: 319},       # 10-K FY2023 and FY2025 "Other financial data: Adjusted EBITDA"
}
# TRIP tags capex as "Capital expenditures, including capitalized website development" and stopped using the standard XBRL tag after 2020;
# values read from the FY2023 and FY2025 10-K cash-flow statements ($M).
TRIP_CAPEX = {2021: 54, 2022: 56, 2023: 63, 2024: 74, 2025: 82}
ABNB_BRAND_PERF = {2021: 723, 2022: 1030, 2023: 1208, 2024: 1455, 2025: 1595}
BKNG_GROSS_BOOKINGS = {2022: 121.3, 2023: 150.6, 2024: 165.6, 2025: 186.1}  # $B, Q4 press releases (as in bkng_head_to_head.py)


def facts(tk):
    path = os.path.join(CACHE, f"{tk}.json")
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK[tk]:010d}.json"
        open(path, "wb").write(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read())
    fs = json.load(open(path))["facts"]
    g = fs.get("us-gaap") or fs.get("ifrs-full")
    if tk == "SPOT":
        g = fs["ifrs-full"]
    out = {}
    for metric, names in TAGS.items():
        for n in names:
            if n not in g:
                continue
            units = g[n]["units"]; u = "USD" if "USD" in units else ("EUR" if "EUR" in units else list(units)[0])
            vals = {int(fc["frame"][2:]): fc["val"] for fc in units[u] if fc.get("frame", "").startswith("CY") and len(fc["frame"]) == 6}
            vals = {y: v for y, v in vals.items() if y in YEARS}
            if vals:
                out[metric] = {y: (v if metric == "diluted_shares" else v / 1e6) for y, v in vals.items()}
                break
    return out


def abnb_letters():
    stack = list(csv.DictReader(open(P("data", "processed", "abnb_quarterly_cost_stack_exsbc.csv"))))
    nights, gbv, adj, da_abnb = {}, {}, {}, {}
    for r in stack:
        y = 2000 + int(r["quarter"][2:])
        nights[y] = nights.get(y, 0) + float(r["nights_m"]); gbv[y] = gbv.get(y, 0) + float(r["gbv_busd"]); adj[y] = adj.get(y, 0) + float(r["adj_ebitda"])
        da_abnb[y] = da_abnb.get(y, 0) + float(r["da"])
    capex = {int(r["period"][2:]): -float(r["capex"]) for r in csv.DictReader(open(P("data", "processed", "abnb_fcf_bridge.csv"))) if r["period"].startswith("FY")}
    return nights, gbv, adj, capex, da_abnb


def main():
    nights, gbv_abnb, adj_abnb, capex_abnb, da_abnb = abnb_letters()
    rows = []
    for tk in CIK:
        d = facts(tk)
        fx = EURUSD if tk == "SPOT" else {y: 1.0 for y in YEARS}
        for y in YEARS:
            g = lambda m: (d.get(m, {}).get(y) * fx[y]) if d.get(m, {}).get(y) is not None else None
            rev = g("revenue")
            if rev is None:
                continue
            oi, sbc = g("op_income"), g("sbc")
            da = g("da") if g("da") is not None else ((g("da_dep_ifrs") or 0) + (g("da_amort_ifrs") or 0) if tk == "SPOT" else None)
            if tk == "ABNB":
                da = da_abnb.get(y)  # XBRL D&A tag stops in FY2022; the letters' reconciliation carries every year
            sm = g("sm"); mkt = g("marketing_only")
            cfo = g("cfo")
            capex = capex_abnb.get(y) if tk == "ABNB" else (TRIP_CAPEX.get(y) if tk == "TRIP" else g("capex"))
            fcfv = (cfo - capex) if cfo is not None and capex is not None else None
            ebitda = (oi + (da or 0) + (sbc or 0)) if oi is not None else None
            sh = d.get("diluted_shares", {}).get(y)
            if tk == "NFLX" and sh and sh < 1000e6:
                sh *= 10  # pre-split years to post-split basis (10-for-1, Nov 2025)
            prev_rev = d.get("revenue", {}).get(y - 1)
            emp = EMPLOYEES[tk].get(y); emp_prev = EMPLOYEES[tk].get(y - 1)
            r = {"company": tk, "year": y, "currency_note": "EUR converted at FRED AEXUSEU" if tk == "SPOT" else "USD",
                 "revenue_musd": round(rev), "revenue_growth_pct": round(100 * (rev / (prev_rev * fx.get(y - 1, 1)) - 1), 1) if prev_rev else None,
                 "gaap_op_margin_pct": round(100 * oi / rev, 1) if oi is not None else None,
                 "sbc_musd": round(sbc) if sbc is not None else None, "sbc_pct_rev": round(100 * sbc / rev, 1) if sbc is not None else None,
                 "da_pct_rev": round(100 * da / rev, 1) if da is not None else None,
                 "ebitda_proxy_musd": round(ebitda) if ebitda is not None else None, "ebitda_proxy_margin_pct": round(100 * ebitda / rev, 1) if ebitda is not None else None,
                 "ebitda_proxy_ex_sbc_margin_pct": round(100 * (oi + (da or 0)) / rev, 1) if oi is not None else None,
                 "reported_adj_ebitda_musd": None, "reported_adj_ebitda_margin_pct": None,
                 "sm_musd": round(sm) if sm is not None else None, "sm_pct_rev": round(100 * sm / rev, 1) if sm is not None else None,
                 "marketing_only_musd": round(mkt) if mkt is not None else None, "marketing_only_pct_rev": round(100 * mkt / rev, 1) if mkt is not None else None,
                 "rd_pct_rev": round(100 * g("rd") / rev, 1) if g("rd") is not None else None, "ga_pct_rev": round(100 * g("ga") / rev, 1) if g("ga") is not None else None,
                 "cor_pct_rev": round(100 * g("cor") / rev, 1) if g("cor") is not None else None,
                 "cfo_musd": round(cfo) if cfo is not None else None, "capex_musd": round(capex) if capex is not None else None,
                 "fcf_musd": round(fcfv) if fcfv is not None else None, "fcf_margin_pct": round(100 * fcfv / rev, 1) if fcfv is not None else None,
                 "fcf_conversion_pct": round(100 * fcfv / ebitda, 1) if fcfv is not None and ebitda else None,
                 "sbc_adj_fcf_margin_pct": round(100 * (fcfv - sbc) / rev, 1) if fcfv is not None and sbc is not None else None,
                 "interest_income_musd": round(g("interest_income")) if g("interest_income") is not None else None,
                 "buybacks_musd": round(g("buybacks")) if g("buybacks") is not None else None,
                 "buybacks_pct_fcf": round(100 * g("buybacks") / fcfv, 1) if g("buybacks") is not None and fcfv else None,
                 "diluted_shares_m": round(sh / 1e6, 1) if sh else None,
                 "employees": emp, "employees_yoy_pct": round(100 * (emp / emp_prev - 1), 1) if emp and emp_prev else None,
                 "revenue_per_employee_kusd": round(1000 * rev / emp) if emp else None,
                 "opex_ex_sbc_per_employee_kusd": round(1000 * (rev - oi - sbc) / emp) if emp and oi is not None and sbc is not None else None,
                 "sbc_per_employee_kusd": round(1000 * sbc / emp) if emp and sbc is not None else None,
                 "unit_name": None, "units_m": None, "revenue_per_unit_usd": None, "opex_ex_sbc_per_unit_usd": None, "take_rate_pct": None, "marketing_pct_gbv": None}
            if tk == "ABNB":
                r["reported_adj_ebitda_musd"] = round(adj_abnb[y]); r["reported_adj_ebitda_margin_pct"] = round(100 * adj_abnb[y] / rev, 1)
                r["unit_name"], r["units_m"] = "nights and seats booked", round(nights[y], 1)
                r["marketing_only_musd"], r["marketing_only_pct_rev"] = ABNB_BRAND_PERF[y], round(100 * ABNB_BRAND_PERF[y] / rev, 1)
                r["take_rate_pct"] = round(100 * rev / (1000 * gbv_abnb[y]), 2); r["marketing_pct_gbv"] = round(100 * ABNB_BRAND_PERF[y] / (1000 * gbv_abnb[y]), 2)
            elif tk in UNITS:
                r["unit_name"], r["units_m"] = UNITS[tk][0], UNITS[tk][1].get(y)
            if tk in REPORTED_ADJ_EBITDA and y in REPORTED_ADJ_EBITDA[tk]:
                r["reported_adj_ebitda_musd"] = REPORTED_ADJ_EBITDA[tk][y]; r["reported_adj_ebitda_margin_pct"] = round(100 * REPORTED_ADJ_EBITDA[tk][y] / rev, 1)
            if tk == "BKNG" and y in BKNG_GROSS_BOOKINGS:
                r["take_rate_pct"] = round(100 * rev / (1000 * BKNG_GROSS_BOOKINGS[y]), 2); r["marketing_pct_gbv"] = round(100 * mkt / (1000 * BKNG_GROSS_BOOKINGS[y]), 2) if mkt else None
            if r["units_m"]:
                r["revenue_per_unit_usd"] = round(rev / r["units_m"], 2)
                if oi is not None and sbc is not None:
                    r["opex_ex_sbc_per_unit_usd"] = round((rev - oi - sbc) / r["units_m"], 2)
            rows.append(r)
    out = P("data", "processed", "overnight", "07_peer_margin_benchmark.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"{'co':5s} {'yr':4s} {'rev':>7s} {'gr%':>5s} {'opm':>5s} {'sbc%':>5s} {'ebitdaP':>7s} {'adj':>5s} {'sm%':>5s} {'fcf%':>5s} {'conv':>5s} {'emp':>6s} {'rev/emp':>7s} {'opex/unit':>9s}")
    for r in rows:
        if r["year"] in (2022, 2025):
            print(f"{r['company']:5s} {r['year']:4d} {r['revenue_musd']:7d} {str(r['revenue_growth_pct']):>5s} {str(r['gaap_op_margin_pct']):>5s} {str(r['sbc_pct_rev']):>5s} {str(r['ebitda_proxy_margin_pct']):>7s} {str(r['reported_adj_ebitda_margin_pct']):>5s} {str(r['sm_pct_rev']):>5s} {str(r['fcf_margin_pct']):>5s} {str(r['fcf_conversion_pct']):>5s} {str(r['employees']):>6s} {str(r['revenue_per_employee_kusd']):>7s} {str(r['opex_ex_sbc_per_unit_usd']):>9s}")


if __name__ == "__main__":
    main()
