"""Workstream 07: cost-line deep dive, quarterly 1Q21..2Q26 plus the annual components management discloses.

Reads
  data/processed/abnb_quarterly_costlines.csv          GAAP cost lines from XBRL (incl. SBC)
  data/processed/abnb_quarterly_cost_stack_exsbc.csv   cash (ex-SBC) cost stack, nights, GBV, SBC by line, D&A, add-backs
  data/processed/abnb_fcf_bridge.csv                   interest income, tax provision, unearned fees, CFO, capex, FCF (letters)
  data/raw/xbrl/ABNB_companyfacts.json                 annual XBRL items not in the costlines CSV (AdvertisingExpense,
                                                       IncomeTaxesPaidNet, current/deferred tax, LeaseCost, PurchaseObligation,
                                                       DefinedContributionPlanCostRecognized, Depreciation)
  Hardcoded with sources (10-K / 10-Q MD&A sentences, cited in the DISCLOSED block below): payment processing cost, cloud,
  insurance, third-party support, employee and contingent-worker counts, brand vs performance marketing, field ops & policy.

Writes
  data/processed/overnight/07_cost_lines_per_night.csv      quarterly: each line GAAP and cash, $M, per night, per $100 GBV,
                                                            % revenue, y/y; SBC by line; D&A; interest income; tax; FCF;
                                                            the quarterly sales-and-marketing split (brand and performance
                                                            marketing vs field operations and policy) from the 10-Q/10-K tables
  data/processed/overnight/07_cost_components_annual.csv    annual FY2020..FY2025 (+1H26 where disclosed) components

Run: py -3.13 analysis/src/overnight/07_cost_lines_per_night.py
"""
import csv, json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
P = lambda *a: os.path.join(ROOT, *a)
OUT_DIR = P("data", "processed", "overnight")
os.makedirs(OUT_DIR, exist_ok=True)


def rd(path):
    return list(csv.DictReader(open(path, newline="", encoding="utf-8")))


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def q_index(q):  # '1Q21' -> (2021, 1)
    return 2000 + int(q[2:]), int(q[0])


# ---------------------------------------------------------------- quarterly
lines = {r["quarter"]: r for r in rd(P("data", "processed", "abnb_quarterly_costlines.csv"))}
stack = {r["quarter"]: r for r in rd(P("data", "processed", "abnb_quarterly_cost_stack_exsbc.csv"))}
fcf = {r["period"]: r for r in rd(P("data", "processed", "abnb_fcf_bridge.csv"))}

LINES = [  # key, GAAP column in costlines, cash column in stack, SBC column in stack
    ("cor", "cost_of_revenue_musd", "cor_cash", None),
    ("ops", "operations_and_support_musd", "ops_cash", "sbc_ops"),
    ("pd", "product_development_musd", "pd_cash", "sbc_pd"),
    ("sm", "sales_and_marketing_musd", "sm_cash", "sbc_sm"),
    ("ga", "general_and_administrative_musd", "ga_cash", "sbc_ga"),
]

# Sales-and-marketing split, quarterly, $M GAAP. Source: the "Brand and performance marketing / Field operations and policy"
# table in every 10-Q (three-month column) and 10-K (full year). Q4 of each year = the 10-K full year less the three 10-Q quarters.
SM_SPLIT = {  # quarter: (brand_and_performance, field_operations_and_policy)
    "1Q22": (231, 114), "2Q22": (282, 97), "3Q22": (259, 124), "4Q22": (258, 151),   # 4Q derived from FY2022 10-K (1,030 / 486)
    "1Q23": (307, 143), "2Q23": (361, 125), "3Q23": (264, 139), "4Q23": (276, 148),  # FY2023 10-K (1,208 / 555)
    "1Q24": (370, 144), "2Q24": (384, 189), "3Q24": (332, 182), "4Q24": (369, 178),  # FY2024 10-K (1,455 / 693)
    "1Q25": (378, 185), "2Q25": (446, 245), "3Q25": (380, 259), "4Q25": (391, 304),  # FY2025 10-K (1,595 / 993)
    "1Q26": (512, 239), "2Q26": (579, 296),
}

quarters = [q for q in stack if q in lines]
quarters.sort(key=q_index)
rows = []
for q in quarters:
    s, l, b = stack[q], lines[q], fcf.get(q, {})
    rev, nights, gbv = f(s["revenue_musd"]), f(s["nights_m"]), f(s["gbv_busd"]) * 1000
    r = {"quarter": q, "revenue_musd": rev, "nights_m": nights, "gbv_musd": gbv, "adr": f(s["adr"]), "take_rate_pct": round(100 * rev / gbv, 2),
         "rev_per_night": round(rev / nights, 2), "adj_ebitda_musd": f(s["adj_ebitda"]), "adj_ebitda_margin_pct": f(s["adj_ebitda_margin_pct"]),
         "operating_income_musd": f(l["operating_income_musd"]), "gaap_op_margin_pct": round(100 * f(l["operating_income_musd"]) / rev, 1),
         "sbc_total_musd": f(s["sbc_total"]), "sbc_pct_rev": round(100 * f(s["sbc_total"]) / rev, 1), "da_musd": f(s["da"]), "other_addbacks_musd": f(s["other_addbacks"]),
         "interest_income_musd": f(b.get("interest_income")), "tax_provision_musd": f(b.get("tax_provision")), "fcf_musd": f(b.get("fcf")),
         "fcf_margin_pct": f(b.get("fcf_margin_pct")), "unearned_fees_change_musd": f(b.get("change_unearned_fees"))}
    total_cash = 0.0
    for k, gcol, ccol, scol in LINES:
        g, c = f(l[gcol]), f(s[ccol])
        total_cash += c
        r[f"{k}_gaap_musd"], r[f"{k}_cash_musd"] = g, c
        r[f"{k}_sbc_musd"] = f(s[scol]) if scol else 0.0
        r[f"{k}_gaap_pct_rev"], r[f"{k}_cash_pct_rev"] = round(100 * g / rev, 1), round(100 * c / rev, 1)
        r[f"{k}_gaap_per_night"], r[f"{k}_cash_per_night"] = round(g / nights, 2), round(c / nights, 2)
        r[f"{k}_cash_per_100gbv"] = round(100 * c / gbv, 2)
    bp, fo = SM_SPLIT.get(q, (None, None))
    r["sm_brand_perf_musd"], r["sm_field_ops_musd"] = bp, fo
    r["sm_brand_perf_pct_rev"] = round(100 * bp / rev, 1) if bp else None
    r["sm_field_ops_pct_rev"] = round(100 * fo / rev, 1) if fo else None
    r["sm_brand_perf_per_night"] = round(bp / nights, 2) if bp else None
    r["sm_field_ops_per_night"] = round(fo / nights, 2) if fo else None
    r["sm_brand_perf_per_100gbv"] = round(100 * bp / gbv, 2) if bp else None
    r["total_cash_cost_musd"] = round(total_cash, 1)
    r["total_cash_cost_per_night"] = round(total_cash / nights, 2)
    r["interest_income_pct_fcf"] = round(100 * r["interest_income_musd"] / r["fcf_musd"], 1) if r["interest_income_musd"] is not None and r["fcf_musd"] else None
    rows.append(r)

# y/y on the per-night and $ series
by_q = {r["quarter"]: r for r in rows}
for r in rows:
    y, qq = q_index(r["quarter"])
    prev = by_q.get(f"{qq}Q{str(y - 1)[2:]}")
    for key in ["revenue_musd", "nights_m", "gbv_musd", "rev_per_night", "adj_ebitda_musd", "sbc_total_musd", "interest_income_musd", "total_cash_cost_per_night",
                "sm_brand_perf_musd", "sm_field_ops_musd", "sm_brand_perf_per_night", "sm_field_ops_per_night"] + \
               [f"{k}_{m}" for k, *_ in LINES for m in ("gaap_musd", "cash_musd", "cash_per_night", "cash_per_100gbv")]:
        v0 = prev.get(key) if prev else None
        r[f"{key}_yoy_pct"] = round(100 * (r[key] / v0 - 1), 1) if v0 not in (None, 0) and r.get(key) is not None else None
    r["adj_ebitda_margin_yoy_pts"] = round(r["adj_ebitda_margin_pct"] - prev["adj_ebitda_margin_pct"], 1) if prev else None

keys = list(rows[0].keys())
with open(os.path.join(OUT_DIR, "07_cost_lines_per_night.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)

# ---------------------------------------------------------------- annual components
xb = json.load(open(P("data", "raw", "xbrl", "ABNB_companyfacts.json")))["facts"]["us-gaap"]


def annual(tag):
    if tag not in xb:
        return {}
    u = xb[tag]["units"]; uu = list(u)[0]
    out = {}
    for fct in u[uu]:
        fr = fct.get("frame", "")
        if fr.startswith("CY") and len(fr) == 6:
            out[int(fr[2:])] = fct["val"] / 1e6
    return out


YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
fy = {}
for y in YEARS:
    qs = [f"{i}Q{str(y)[2:]}" for i in (1, 2, 3, 4)]
    if all(q in stack for q in qs):
        S = [stack[q] for q in qs]
        fy[y] = {"revenue": sum(f(s["revenue_musd"]) for s in S), "nights": sum(f(s["nights_m"]) for s in S), "gbv": 1000 * sum(f(s["gbv_busd"]) for s in S),
                 **{k: sum(f(s[c]) for s in S) for k, _, c, _ in LINES}, "sbc": sum(f(s["sbc_total"]) for s in S), "adj": sum(f(s["adj_ebitda"]) for s in S),
                 "sm_gaap": sum(f(lines[q]["sales_and_marketing_musd"]) for q in qs)}
    elif y == 2020:
        fy[y] = {"revenue": 3378.2, "nights": 193.2, "gbv": 23900.0, "sm_gaap": 1175.3}  # FY2020 10-K; nights and GBV from the 4Q20 letter

# Disclosed components. Source key: 10-K FY = Airbnb 10-K for that year, MD&A results of operations unless noted.
DISCLOSED = {
    "employees_dec31": {2020: 5597, 2021: 6132, 2022: 6811, 2023: 6907, 2024: 7300, 2025: 8200,
                        "source": "10-K Item 1 Human Capital: 'As of December 31, YYYY, we had [approximately] N employees' (2024 and 2025 given as approximately)"},
    "third_party_support_workers": {2022: 11000, 2023: 11000, 2024: 11000, 2025: 13000,
                                    "source": "10-K Item 1: 'global network of approximately N third-party (contingent) workers to handle the vast majority of our community support contacts'"},
    "brand_and_performance_marketing": {2019: 1140.4, 2020: 478.6, 2021: 723.2, 2022: 1030, 2023: 1208, 2024: 1455, 2025: 1595,
                                        "source": "10-K sales and marketing split table (FY2021 10-K for 2019 to 2021; each later 10-K)"},
    "field_operations_and_policy": {2019: 481.2, 2020: 696.7, 2021: 463.2, 2022: 486, 2023: 555, 2024: 693, 2025: 993,
                                    "source": "10-K sales and marketing split table"},
    "advertising_expense_xbrl": {**annual("AdvertisingExpense"), "source": "XBRL us-gaap:AdvertisingExpense (10-K note; FY2025 value of 843 is as tagged and sits below the 1,595 brand and performance figure)"},
    "payment_processing_cost": {2020: 600.2, 2021: 844.4, 2022: 1194.1, 2023: 1367.1, 2024: 1506.1, 2025: 1665.1,
                                "source": "FY2021 10-K: merchant fees and chargebacks $600.2M (2020) and $844.4M (2021), 3% and 2% of GBV. Later years accumulate the MD&A deltas: 2022 +313.9 fees +35.8 chargebacks; 2023 +163 +10; 2024 +173 -34; 2025 +188 -29. Levels after 2021 are derived, not disclosed"},
    "cloud_hosting_cost_delta": {2022: 24.9, 2023: 31, 2024: 26, 2025: 27,
                                 "source": "10-K MD&A cost of revenue: year-over-year increase in cloud computing / data hosting costs (level never disclosed). 1H26 10-Q: +$15M server costs, reserved-instance amortization"},
    "insurance_cost_delta": {2021: 41.9, 2022: 29.8, 2023: 16, 2024: 25, 2025: 14,
                             "source": "10-K MD&A operations and support: increase in insurance costs (Host Liability Insurance premiums scale with nights). 1H26 10-Q: +$9M"},
    "third_party_support_and_customer_relations_delta": {2022: 130.7, 2023: 105, 2024: 25, 2025: -18,
                                                         "source": "10-K MD&A operations and support: 2022 and 2023 combine third-party community support personnel and customer relations; 2024 is customer relations only (+25); 2025 customer relations -18 (lower refunds and credits); 9M25 10-Q third-party customer service -25 (partner site optimization); 1H26 10-Q third-party -15 (AI) and customer relations +14 (make-goods, case reserves)"},
    "pd_payroll_delta": {2024: 288, 2025: 293, "source": "10-K MD&A product development: increase in payroll-related expenses (headcount)"},
    "sm_marketing_activities_delta": {2024: 294, 2025: 163, "source": "10-K MD&A sales and marketing: increase in marketing activities; 1H26 10-Q +258 (paid growth in emerging markets and partnerships)"},
    "sm_third_party_service_provider_delta": {2024: 26, 2025: 102, "source": "10-K MD&A sales and marketing: consultant / third-party service provider costs (2025: product launch and supply acquisition for Experiences and Services)"},
    "ga_non_income_taxes_delta": {2024: -656, 2025: 74, "source": "10-K MD&A G&A: non-income taxes (2023 Italy withholding settlement reversed in 2024); 1H26 10-Q -38"},
    "interest_income": {**{y: f(fcf[f"FY{y}"]["interest_income"]) for y in YEARS if f"FY{y}" in fcf}, "source": "letters' Adjusted EBITDA reconciliation via abnb_fcf_bridge.csv (XBRL InvestmentIncomeNonoperating matches)"},
    "income_tax_provision": {**{y: -f(fcf[f"FY{y}"]["tax_provision"]) for y in YEARS if f"FY{y}" in fcf}, "source": "abnb_fcf_bridge.csv (provision; 2023 includes the -$2.9B valuation allowance release)"},
    "cash_taxes_paid": {2020: 15, 2021: 17, 2022: 68, 2023: 132, 2024: 350, 2025: 232, "source": "XBRL IncomeTaxesPaid / IncomeTaxesPaidNet (10-K supplemental cash flow)"},
    "current_tax_expense": {**annual("CurrentIncomeTaxExpenseBenefit"), "source": "XBRL CurrentIncomeTaxExpenseBenefit"},
    "deferred_tax_expense": {**annual("DeferredIncomeTaxExpenseBenefit"), "source": "XBRL DeferredIncomeTaxExpenseBenefit (2024 433, 2025 376: the released DTA being consumed)"},
    "lease_cost": {**annual("LeaseCost"), "source": "XBRL LeaseCost (total lease cost, 10-K leases note)"},
    "purchase_obligations_dec31": {2022: 1068, 2023: 934, 2024: 719, 2025: 1749,
                                   "source": "10-K Note 13 Commitments and Contingencies, non-cancelable purchase obligations (web hosting and other) at Dec 31. XBRL PurchaseObligation carries no CY frames, so these are read from the note"},
    "data_hosting_commitment_total": {2022: 941.7, 2023: 842, 2024: 672, 2025: 1700,
                                      "source": "10-K Note 13: 'committed to spend an aggregate of at least $X for vendor services through YYYY' with the data-hosting provider: $941.7M through 2027 (FY2022), $842M through 2027 (FY2023), $672M through 2027 (FY2024), $1.7B through 2031 (FY2025). The 2025 step-up is committed compute that has not yet reached cost of revenue"},
    "defined_contribution_plan_cost": {**annual("DefinedContributionPlanCostRecognized"), "source": "XBRL DefinedContributionPlanCostRecognized (401k match, a headcount proxy)"},
    "depreciation": {**annual("Depreciation"), "source": "XBRL Depreciation (PP&E only; total D&A is in the letters' reconciliation)"},
    "capex": {**{y: -f(fcf[f"FY{y}"]["capex"]) for y in YEARS if f"FY{y}" in fcf}, "source": "abnb_fcf_bridge.csv"},
    "fcf": {**{y: f(fcf[f"FY{y}"]["fcf"]) for y in YEARS if f"FY{y}" in fcf}, "source": "abnb_fcf_bridge.csv"},
    "new_business_investment_guided": {2025: 225, "source": "4Q24 letter and call: $200M to $250M in 2025 to launch and scale new businesses (refined to about $200M on the Q2 2025 call); lands in S&M field operations and product development, mostly headcount and go-to-market"},
}

arows = []
for name, d in DISCLOSED.items():
    row = {"component": name, "source": d["source"]}
    for y in [2019] + YEARS:
        v = d.get(y)
        row[f"fy{y}"] = round(v, 1) if isinstance(v, (int, float)) else None
    # ratios where the denominator exists
    for y in YEARS:
        v = d.get(y)
        if isinstance(v, (int, float)) and y in fy:
            row[f"fy{y}_pct_rev"] = round(100 * v / fy[y]["revenue"], 2)
            if "gbv" in fy[y] and name == "payment_processing_cost":
                row[f"fy{y}_pct_gbv"] = round(100 * v / fy[y]["gbv"], 2)
    arows.append(row)

# derived headcount productivity rows
for label, fn in [("revenue_per_employee_kusd", lambda y: 1000 * fy[y]["revenue"] / DISCLOSED["employees_dec31"][y]),
                  ("nights_per_employee_k", lambda y: 1000 * fy[y]["nights"] / DISCLOSED["employees_dec31"][y]),
                  ("sbc_per_employee_kusd", lambda y: 1000 * fy[y]["sbc"] / DISCLOSED["employees_dec31"][y]),
                  ("employees_yoy_pct", lambda y: 100 * (DISCLOSED["employees_dec31"][y] / DISCLOSED["employees_dec31"][y - 1] - 1)),
                  ("revenue_yoy_pct", lambda y: 100 * (fy[y]["revenue"] / fy[y - 1]["revenue"] - 1)),
                  ("brand_perf_marketing_pct_rev", lambda y: 100 * DISCLOSED["brand_and_performance_marketing"][y] / fy[y]["revenue"]),
                  ("field_ops_policy_pct_rev", lambda y: 100 * DISCLOSED["field_operations_and_policy"][y] / fy[y]["revenue"]),
                  ("brand_perf_marketing_per_night", lambda y: DISCLOSED["brand_and_performance_marketing"][y] / fy[y]["nights"]),
                  ("field_ops_policy_per_night", lambda y: DISCLOSED["field_operations_and_policy"][y] / fy[y]["nights"]),
                  ("payment_processing_pct_gbv", lambda y: 100 * DISCLOSED["payment_processing_cost"][y] / fy[y]["gbv"]),
                  ("cor_cash_ex_payments_musd", lambda y: fy[y]["cor"] - DISCLOSED["payment_processing_cost"][y]),
                  ("interest_income_pct_fcf", lambda y: 100 * DISCLOSED["interest_income"][y] / DISCLOSED["fcf"][y]),
                  ("cash_tax_pct_provision", lambda y: 100 * DISCLOSED["cash_taxes_paid"][y] / DISCLOSED["income_tax_provision"][y] if DISCLOSED["income_tax_provision"][y] > 0 else None)]:
    row = {"component": label, "source": "derived from the rows above and the cash cost stack"}
    for y in YEARS:
        try:
            v = fn(y)
            row[f"fy{y}"] = round(v, 2) if v is not None else None
        except (KeyError, ZeroDivisionError, TypeError):
            row[f"fy{y}"] = None
    arows.append(row)

akeys = ["component"] + [f"fy{y}" for y in [2019] + YEARS] + [f"fy{y}_pct_rev" for y in YEARS] + [f"fy{y}_pct_gbv" for y in YEARS] + ["source"]
with open(os.path.join(OUT_DIR, "07_cost_components_annual.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=akeys, extrasaction="ignore"); w.writeheader(); w.writerows(arows)

# console summary
print("quarters:", len(rows), rows[0]["quarter"], "..", rows[-1]["quarter"])
for r in rows[-6:]:
    print(r["quarter"], "rev/night", r["rev_per_night"], "cash cost/night", r["total_cash_cost_per_night"], "ops cash/night", r["ops_cash_per_night"], f"({r['ops_cash_per_night_yoy_pct']}% y/y)",
          "S&M cash/night", r["sm_cash_per_night"], f"({r['sm_cash_per_night_yoy_pct']}%)", "COR/100GBV", r["cor_cash_per_100gbv"], "int inc", r["interest_income_musd"])
for a in arows:
    if a["component"] in ("employees_dec31", "revenue_per_employee_kusd", "payment_processing_pct_gbv", "brand_perf_marketing_pct_rev", "field_ops_policy_pct_rev", "cash_tax_pct_provision", "interest_income_pct_fcf"):
        print(a["component"], {y: a.get(f"fy{y}") for y in YEARS})
