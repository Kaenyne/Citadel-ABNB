"""WS02 financial panel for the margin build. Rebuilds every CSV in data/processed/margin_build/02_financial_panel/.

Run from the worktree root:  python "analysis/src/margin_build/02_financial_panel/run.py"      (exit code 0 on success)

Outputs
  02_panel_quarterly.csv        one row per quarter 1Q18-2Q26 (2018-3Q20 flagged pre_ipo), USD millions
  02_panel_provenance.csv       long form: quarter, line, value, source, source_detail, vintage (every source seen)
  02_panel_annual.csv           FY2018-FY2025 from the 10-K / XBRL annual facts, with sum-of-quarters check columns
  02_seasonality.csv            quarter share of FY, margin, cost % of revenue and cost per night by line and year
  02_reconciliation.csv         Adjusted EBITDA rebuilt from lines minus reported; my lines minus the existing repo panels
  02_macro_cycle_episodes.csv   demand-shock episodes with revenue/nights/cost growth and management statements
  02_letter_vintages.csv        every reconciliation value by letter vintage (restatement audit trail)
  02_build_log.txt              warnings and coverage
"""
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from panel_lib import (ROOT, Facts, FCF_ROWS, IS_ROWS, RECON_ROWS, SBC_ROWS, WARNINGS, clean_html, clean_txt,
                       letter_cash_flow, letter_fcf, letter_income_statement, letter_kpis, letter_recon, parse_table,
                       pnum, prev_q, qlabel, qorder, recon_identity_ok, row_after, strip_markers, tenk_row, warn)

OUT = ROOT / "data/processed/margin_build/02_financial_panel"
RAW = ROOT / "data/raw/margin_build/02_financial_panel"
FIG = ROOT / "analysis/figures/margin_build"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)
(ROOT / "data/manifests/margin_build").mkdir(parents=True, exist_ok=True)

QUARTERS = [qlabel(y, q) for y in range(2018, 2027) for q in (1, 2, 3, 4)]
QUARTERS = [q for q in QUARTERS if qorder(q) <= qorder("2Q26")]
YEARS = list(range(2018, 2026))

PROV = []          # long-form provenance rows
VINT = []          # letter vintage rows


def prov(period, line, value, source, detail, vintage=""):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return
    PROV.append({"period": period, "line": line, "value": round(float(value), 4), "source": source,
                 "source_detail": detail, "vintage": vintage})


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# =============================================================================================== 1. XBRL
F = Facts(ROOT / "data/raw/xbrl/ABNB_companyfacts.json")
XQ = {  # line -> (concept, sign)
    "revenue": ("RevenueFromContractWithCustomerExcludingAssessedTax", 1), "cor_gaap": ("CostOfRevenue", 1),
    "pd_gaap": ("ResearchAndDevelopmentExpense", 1), "sm_gaap": ("SellingAndMarketingExpense", 1),
    "ga_gaap": ("GeneralAndAdministrativeExpense", 1), "restr_gaap": ("RestructuringCharges", 1),
    "total_costs": ("CostsAndExpenses", 1), "op_income": ("OperatingIncomeLoss", 1),
    "interest_income": ("InvestmentIncomeNonoperating", 1), "interest_expense": ("InterestIncomeExpenseNonoperatingNet", -1),
    "other_income_expense_xbrl": ("OtherNonoperatingIncomeExpense", 1),
    "pretax_income": ("IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest", 1),
    "tax_provision": ("IncomeTaxExpenseBenefit", 1), "net_income": ("NetIncomeLoss", 1),
    "sbc_total_is": ("AllocatedShareBasedCompensationExpense", 1),
    "buybacks": ("StockRepurchasedAndRetiredDuringPeriodValue", 1),
}
XQ_SHARES = {"shares_diluted_m": "WeightedAverageNumberOfDilutedSharesOutstanding",
             "shares_basic_m": "WeightedAverageNumberOfSharesOutstandingBasic"}
XQ_EPS = {"eps_diluted": "IncomeLossFromContinuingOperationsPerDilutedShare", "eps_basic": "IncomeLossFromContinuingOperationsPerBasicShare"}
XYTD = {"cfo_xbrl": "NetCashProvidedByUsedInOperatingActivities", "capex_xbrl": "PaymentsToAcquirePropertyPlantAndEquipment",
        "change_unearned_fees": "IncreaseDecreaseInDeferredRevenue", "change_funds_receivable_xbrl": "IncreaseDecreaseInClientFundsHeld",
        "rsu_tax_withholding": "PaymentsRelatedToTaxWithholdingForShareBasedCompensation", "income_taxes_paid": "IncomeTaxesPaid",
        "da_cashflow": "OtherDepreciationAndAmortization", "sbc_cashflow": "ShareBasedCompensation",
        "buybacks_cash": "PaymentsForRepurchaseOfCommonStock"}
XINST = {"cash_and_equivalents": "CashAndCashEquivalentsAtCarryingValue", "short_term_investments": "ShortTermInvestments",
         "restricted_cash": "RestrictedCashAndCashEquivalents", "funds_held_on_behalf": "FundsHeldForClients",
         "unearned_fees_balance": "DeferredRevenueCurrent", "long_term_debt_noncurrent": "LongTermDebtNoncurrent",
         "long_term_debt_current": "LongTermDebtCurrent"}

xq = {}
for line, (concept, sign) in XQ.items():
    d = F.quarterly(concept)
    xq[line] = {q: (sign * v[0], v[1], sign * v[2], v[3]) for q, v in d.items()}
for line, concept in XQ_SHARES.items():
    xq[line] = {q: (v[0], v[1], v[2], v[3]) for q, v in F.quarterly(concept, unit="shares", scale=1e-6, allow_derived=False).items()}
for line, concept in XQ_EPS.items():
    d = {}
    latest, first = F.duration_series(concept, "USD/shares")
    for (s, e), (v, filed, form) in latest.items():
        if (s[5:], e[5:]) in (("01-01", "03-31"), ("04-01", "06-30"), ("07-01", "09-30"), ("10-01", "12-31")):
            d[qlabel(int(e[:4]), (int(e[5:7]) - 1) // 3 + 1)] = (v, f"xbrl:{concept} 3M to {e} {form} filed {filed}", v, filed)
    xq[line] = d
# ops & support is not a us-gaap element: total costs minus the other five lines
xq["ops_gaap"] = {}
for q in xq["total_costs"]:
    if all(q in xq[k] for k in ("cor_gaap", "pd_gaap", "sm_gaap", "ga_gaap")):
        r = xq["restr_gaap"].get(q, (0.0, "", 0.0, ""))[0]
        v = xq["total_costs"][q][0] - sum(xq[k][q][0] for k in ("cor_gaap", "pd_gaap", "sm_gaap", "ga_gaap")) - r
        xq["ops_gaap"][q] = (v, "xbrl: CostsAndExpenses less CostOfRevenue, R&D, S&M, G&A, RestructuringCharges (no us-gaap element for operations and support)", v, "")
xytd = {line: F.ytd(concept) for line, concept in XYTD.items()}
xq_cf = {line: F.quarterly(concept) for line, concept in XYTD.items()}
xinst = {line: F.instants(concept) for line, concept in XINST.items()}
xa = {line: F.annual(concept) for line, (concept, sign) in XQ.items()}
for line, (concept, sign) in XQ.items():
    xa[line] = {y: (sign * v[0], v[1], sign * v[2], v[3]) for y, v in xa[line].items()}
xa["shares_diluted_m"] = F.annual("WeightedAverageNumberOfDilutedSharesOutstanding", unit="shares", scale=1e-6)
xa["shares_basic_m"] = F.annual("WeightedAverageNumberOfSharesOutstandingBasic", unit="shares", scale=1e-6)
xa["advertising_expense"] = F.annual("AdvertisingExpense")
xa["income_taxes_paid"] = F.annual("IncomeTaxesPaid")
xa["rsu_tax_withholding"] = F.annual("PaymentsRelatedToTaxWithholdingForShareBasedCompensation")
xa["cfo"] = F.annual("NetCashProvidedByUsedInOperatingActivities")
xa["buybacks_cash"] = F.annual("PaymentsForRepurchaseOfCommonStock")
xa["change_unearned_fees"] = F.annual("IncreaseDecreaseInDeferredRevenue")
xa["sbc_cashflow"] = F.annual("ShareBasedCompensation")
xa["da_cashflow"] = F.annual("OtherDepreciationAndAmortization")
for y, (v, det, fv, ff) in F.annual("IncomeLossFromContinuingOperationsPerDilutedShare", "USD/shares", 1.0).items():
    xa.setdefault("eps_diluted", {})[y] = (v, det, fv, ff)
for y, (v, det, fv, ff) in F.annual("IncomeLossFromContinuingOperationsPerBasicShare", "USD/shares", 1.0).items():
    xa.setdefault("eps_basic", {})[y] = (v, det, fv, ff)
xa["ops_gaap"] = {}
for y in xa["total_costs"]:
    if all(y in xa[k] for k in ("cor_gaap", "pd_gaap", "sm_gaap", "ga_gaap")):
        r = xa["restr_gaap"].get(y, (0.0,))[0]
        v = xa["total_costs"][y][0] - sum(xa[k][y][0] for k in ("cor_gaap", "pd_gaap", "sm_gaap", "ga_gaap")) - r
        xa["ops_gaap"][y] = (v, "xbrl: CostsAndExpenses less the other five lines", v, "")


def de_cumulate(ytd_map):
    """{q: (ytd_value, detail)} -> {q: (quarter_value, detail)}"""
    out = {}
    for q, (v, det) in ytd_map.items():
        if q[0] == "1":
            out[q] = (v, det)
        else:
            p = prev_q(q)
            if p in ytd_map:
                out[q] = (v - ytd_map[p][0], f"{det} less YTD {p}")
    return out


# =============================================================================================== 2. letters
letters = sorted((ROOT / "data/raw/letters").glob("*_*.htm"), key=lambda p: qorder(p.name[:4]))
LET = {}  # letter quarter -> parsed pieces
rev_x = {q: v[0] for q, v in xq["revenue"].items()}
cfo_ytd_latest = {q: v[0] for q, v in xytd["cfo_xbrl"].items()}
cfo_ytd_first = {}
lat, fst = F.duration_series("NetCashProvidedByUsedInOperatingActivities")
for (s, e), (v, filed, form) in fst.items():
    if s.endswith("-01-01") and s[:4] == e[:4] and e[5:] in ("03-31", "06-30", "09-30", "12-31"):
        cfo_ytd_first[qlabel(int(e[:4]), (int(e[5:7]) - 1) // 3 + 1)] = v * 1e-6

recon_v = {}   # quarter -> list of dict(vintage, values)
fcf_v = {}
for p in letters:
    lq = p.name[:4]
    t = clean_html(p)
    src = f"letter {lq} ({p.name})"
    L = {"path": p, "src": src}
    r = letter_recon(t, lq)
    if r:
        cols, rows, method, bad = r
        badc = {c for c, _ in bad}
        for i, c in enumerate(cols):
            if c in badc or c.startswith("FY"):
                if c.startswith("FY") and c not in badc:
                    y = int(c[2:])
                    for k in rows:
                        if rows[k] is not None:
                            VINT.append({"period": c, "line": "recon_" + k, "value": rows[k][i], "letter": lq, "method": method})
                continue
            vals = {k: (rows[k][i] if rows[k] is not None else None) for k in rows}
            recon_v.setdefault(c, []).append({"letter": lq, "src": src, "method": method, "vals": vals})
            for k, v in vals.items():
                if v is not None:
                    VINT.append({"period": c, "line": "recon_" + k, "value": v, "letter": lq, "method": method})
        if bad:
            warn(f"{lq} letter: Adjusted EBITDA reconciliation columns dropped (identity fails): {bad}")
    else:
        warn(f"{lq} letter: Adjusted EBITDA reconciliation table could not be parsed (other letters cover these quarters)")
    f = letter_fcf(t, lq)
    if f:
        cols, rows, method, bad = f
        badc = {c for c, _ in bad}
        for i, c in enumerate(cols):
            if c in badc or c.startswith("FY"):
                continue
            vals = {k: (rows[k][i] if rows.get(k) is not None else None) for k in ("cfo", "capex", "fcf", "revenue")}
            fcf_v.setdefault(c, []).append({"letter": lq, "src": src, "vals": vals})
            for k in ("cfo", "capex", "fcf"):
                VINT.append({"period": c, "line": "fcf_" + k, "value": vals[k], "letter": lq, "method": method})
        if bad:
            warn(f"{lq} letter: FCF reconciliation columns dropped (CFO + capex != FCF): {bad}")
    else:
        warn(f"{lq} letter: FCF reconciliation table could not be parsed")
    isd = letter_income_statement(t)
    L["is"] = isd
    if isd and isd["rows"].get("revenue"):
        rv = isd["rows"]["revenue"]
        cy = [i for i, v in enumerate(rv) if q_rev_match(v, rev_x.get(lq))] if False else [i for i, v in enumerate(rv) if rev_x.get(lq) is not None and abs(v - rev_x[lq]) < 0.6]
        pyq = qlabel(2000 + int(lq[2:4]) - 1, int(lq[0]))
        py = [i for i, v in enumerate(rv) if rev_x.get(pyq) is not None and abs(v - rev_x[pyq]) < 0.6]
        if lq == "4Q20":
            py = [0]   # 4Q19 is not in XBRL; the 4Q20 letter's first column is the Dec-2019 quarter
        L["is_cols"] = {"cy": cy[0] if cy else None, "py": py[0] if py else None, "pyq": pyq}
    else:
        L["is_cols"] = {"cy": None, "py": None, "pyq": None}
    L["cf"] = letter_cash_flow(t)
    L["kpi"] = letter_kpis(t, lq)
    LET[lq] = L

# --- pick the latest vintage for every quarter's reconciliation, and record first-vs-latest
RECON = {}
for q, vs in recon_v.items():
    vs = sorted(vs, key=lambda d: qorder(d["letter"]))
    RECON[q] = {"latest": vs[-1], "first": vs[0], "n": len(vs)}
FCF = {}
for q, vs in fcf_v.items():
    vs = sorted(vs, key=lambda d: qorder(d["letter"]))
    FCF[q] = {"latest": vs[-1], "first": vs[0], "n": len(vs)}

# --- SBC by function per quarter from the letter footnote (column chosen by matching the total to the recon SBC)
SBCQ = {}


def pick_sbc(cands, target_total, target_alt=None):
    tol = 0.6 + 0.001 * abs(target_total)
    for cand in cands:
        tot = cand["sbc_total"]
        for i, v in enumerate(tot):
            if abs(v - target_total) < tol:
                got = {k: (cand[k][i] if cand.get(k) else None) for k in cand}
                parts = [got.get(k) for k in ("sbc_ops", "sbc_pd", "sbc_sm", "sbc_ga")]
                if any(x is None for x in parts):
                    continue
                if abs(sum(parts) + (got.get("sbc_restr") or 0.0) - v) > 2.5 or any(x > v + 0.6 for x in parts):
                    continue        # rows read from the income statement itself (1Q24 letter layout), not the footnote
                return got, i
    return None, None


for lq, L in LET.items():
    isd = L["is"]
    if not isd or not isd.get("sbc_candidates"):
        continue
    for which, qq in (("cy", lq), ("py", L["is_cols"]["pyq"])):
        if qq is None:
            continue
        tot = xq["sbc_total_is"].get(qq, (None,))[0]
        if tot is None and qq in RECON:
            tot = RECON[qq]["latest"]["vals"].get("sbc")
        if tot is None:
            continue
        # the letter footnote total includes restructuring SBC; the recon add-back excludes it. Try both.
        got, col = pick_sbc(isd["sbc_candidates"], tot)
        if got is None and qq in RECON and RECON[qq]["latest"]["vals"].get("sbc") is not None:
            got, col = pick_sbc(isd["sbc_candidates"], RECON[qq]["latest"]["vals"]["sbc"])
        if got is None:
            continue
        SBCQ.setdefault(qq, []).append({"letter": lq, "which": which, "vals": got, "col": col, "src": L["src"]})

# 10-Q fallback for 1Q21 and 2Q21 (no footnote in those letters)
for lq, fname, acc in (("1Q21", "10Q_1Q21_abnb-20210331.htm", "0001628280-21-010389"), ("2Q21", "10Q_2Q21_abnb-20210630.htm", "0001628280-21-016979")):
    p = RAW / fname
    if not p.exists():
        warn(f"{lq}: 10-Q {fname} missing; SBC by function will be absent")
        continue
    t = clean_html(p)
    m = re.search(r"stock-based compensation expense \(in thousands\):", t)
    seg = t[m.end():m.end() + 900]
    n = 2 if lq == "1Q21" else 4
    vals = {k: row_after(seg, rx, n, 1e-3) for k, rx in SBC_ROWS}
    got = {k: (v[1] if v else None) for k, v in vals.items()}
    SBCQ.setdefault(lq, []).insert(0, {"letter": f"10-Q {lq}", "which": "cy", "vals": got, "col": 1, "src": f"10-Q {lq} accession {acc} ({fname}), SBC note, three months ended column"})

# =============================================================================================== 3. 424B4 (1Q18-3Q20 quarterly, FY2018)
P424 = RAW / "424B4_2020-12-11_d81668d424b4.htm"
t424 = clean_html(P424)
SRC424 = "424B4 prospectus 11 Dec 2020 (accession 0001193125-20-315318)"
q424_is = parse_table(t424, r"Quarterly Consolidated Statements of Operations", IS_ROWS, r"Revenue \$",
                      r"Includes stock-based compensation expense as follows", window=6000)
q424_sbc = parse_table(t424, r"Includes stock-based compensation expense as follows: Three Months Ended", SBC_ROWS,
                       r"Operations and support", r"Table of Contents", window=2500)
q424_recon = parse_table(t424, r"Adjusted EBITDA Reconciliation Three Months Ended", RECON_ROWS, r"TTM Revenue|Net income",
                         r"as a percentage of TTM|Excludes stock-based", window=4000, allow_short=("revenue",))
q424_fcf = parse_table(t424, r"Free Cash Flow Reconciliation Three Months Ended", FCF_ROWS, r"TTM Revenue|Net cash provided",
                       r"as a percentage|Other cash flow", window=3000, allow_short=("revenue", "ttm_revenue"))
for name, obj in (("IS", q424_is), ("SBC", q424_sbc), ("recon", q424_recon), ("FCF", q424_fcf)):
    if not obj:
        warn(f"424B4 {name} table not parsed")
if q424_recon:
    bad = recon_identity_ok(q424_recon[0], q424_recon[1])
    if bad:
        warn(f"424B4 recon identity fails: {bad}")
    for i, c in enumerate(q424_recon[0]):
        vals = {k: (q424_recon[1][k][i] if q424_recon[1].get(k) is not None else None) for k in q424_recon[1]}
        recon_v.setdefault(c, []).append({"letter": "424B4", "src": SRC424, "method": q424_recon[2], "vals": vals})
        for k, v in vals.items():
            if v is not None:
                VINT.append({"period": c, "line": "recon_" + k, "value": v, "letter": "424B4", "method": q424_recon[2]})
if q424_fcf:
    for i, c in enumerate(q424_fcf[0]):
        vals = {k: (q424_fcf[1][k][i] if q424_fcf[1].get(k) is not None else None) for k in ("cfo", "capex", "fcf")}
        fcf_v.setdefault(c, []).append({"letter": "424B4", "src": SRC424, "vals": vals})
        for k, v in vals.items():
            VINT.append({"period": c, "line": "fcf_" + k, "value": v, "letter": "424B4", "method": q424_fcf[2]})
# rebuild RECON/FCF including the 424B4 as the earliest vintage. "latest" = the latest letter's value, except that
# when an earlier letter printed the same number in thousands (the letters switched to millions in 1Q22) and it
# agrees with the latest within $0.6M, the thousands figure is kept for precision.
RECON, FCF = {}, {}
order = lambda d: (-1 if d["letter"] == "424B4" else qorder(d["letter"]))


def precise_latest(vs):
    """The latest vintage, unless an earlier letter printed the whole column in thousands and every item agrees
    with the latest within $0.6M: then that earlier column is used in full (never mixed item by item, so the
    NI-to-EBITDA identity stays exact within the chosen vintage)."""
    latest = vs[-1]
    lv = latest["vals"]
    for e in reversed(vs[:-1]):
        ev = e["vals"]
        if not any(v is not None and abs(v - round(v)) > 1e-9 for v in ev.values()):
            continue                      # not a thousands-precision column
        ok = True
        for k, v in lv.items():
            a = 0.0 if v is None else v
            b = 0.0 if ev.get(k) is None else ev[k]
            if abs(a - b) > 0.6:
                ok = False
                break
        if ok:
            out = dict(e)
            out["src"] = e["src"] + f" (thousands-precision column agreeing with the {latest['letter']} letter)"
            return out
    return latest


for q, vs in recon_v.items():
    vs = sorted(vs, key=order)
    RECON[q] = {"latest": precise_latest(vs), "first": vs[0], "n": len(vs), "all": vs}
for q, vs in fcf_v.items():
    vs = sorted(vs, key=order)
    FCF[q] = {"latest": precise_latest(vs), "first": vs[0], "n": len(vs), "all": vs}

# annual 2015-2019 from the 424B4 (FY2018 used; the rest are context)
a424 = {}
m = re.search(r"Adjusted EBITDA to the most comparable GAAP measure, net loss: Year Ended December 31, Nine Months Ended September 30,", t424)
if m:
    seg = strip_markers(t424[m.start():m.start() + 2500])
    for key, rx in RECON_ROWS:
        v = row_after(seg, rx, 7, 1e-3)
        if v:
            a424["recon_" + key] = dict(zip([2015, 2016, 2017, 2018, 2019, "9M19", "9M20"], v))
m = re.search(r"Free Cash Flow to the most comparable GAAP cash flow measure", t424)
if m:
    seg = t424[m.start():m.start() + 1500]
    for key, rx in FCF_ROWS:
        v = row_after(seg, rx, 7, 1e-3)
        if v:
            a424["fcf_" + key] = dict(zip([2015, 2016, 2017, 2018, 2019, "9M19", "9M20"], v))
kpi424 = {}
m = re.search(r"In 2019, we had ([\d.]+) million Nights and Experiences Booked, a \d+% increase from ([\d.]+) million", t424)
if m:
    kpi424["nights_m"] = {2019: float(m.group(1)), 2018: float(m.group(2))}
m = re.search(r"In 2019, our GBV was \$([\d.]+) billion, a \d+% increase from \$([\d.]+) billion in 2018", t424)
if m:
    kpi424["gbv_busd"] = {2019: float(m.group(1)), 2018: float(m.group(2))}

# =============================================================================================== 4. 10-K text
TENK = {}
for fy in range(2020, 2026):
    t = clean_txt(ROOT / f"data/raw/filings/txt/abnb_10k_FY{fy}.txt")
    src = f"10-K FY{fy} (data/raw/filings/txt/abnb_10k_FY{fy}.txt)"
    d = {"src": src}
    # income statement (used for FY2018 only: later years come from XBRL)
    i = t.find("| Cost of revenue |")
    if i < 0:
        i = t.find("Cost of revenue |")
    seg = t[i - 1500:i + 3500]
    hdr = re.search(r"Year Ended December 31, \| \|((?: 20\d\d \|)+)", seg)
    years = [int(y) for y in re.findall(r"20\d\d", hdr.group(1))] if hdr else [fy - 1, fy]
    scale = 1e-3 if "in thousands" in seg[:2500] else 1.0
    pct_layout = "% of Revenue" in seg[:2500]

    def trow(segment, rx, n=len(years), sc=scale, pct=pct_layout):
        if pct:
            v = tenk_row(segment, rx, 2 * n + 1, scale=sc) or tenk_row(segment, rx, 2 * n, scale=sc)
            return v[0::2][:n] if v else None
        return tenk_row(segment, rx, n, scale=sc)

    d["years"] = years
    d["is"] = {k: trow(seg, rx) for k, rx in IS_ROWS}
    j = seg.find("stock-based compensation expense as follows")
    sbcseg = seg[j:j + 1500] if j >= 0 else ""
    sbc_pct = "% of Total" in sbcseg[:300]
    d["sbc"] = {k: trow(sbcseg, rx, pct=sbc_pct) for k, rx in SBC_ROWS}
    # Adjusted EBITDA reconciliation (annual)
    j = t.find("Adjusted to exclude")
    seg2 = t[j - 1200:j + 1800]
    hdr2 = re.search(r"((?:20\d\d \| ){2,}|(?:\| 20\d\d ){2,})", seg2[:1200])
    ryears = [int(y) for y in re.findall(r"20\d\d", hdr2.group(1))] if hdr2 else years
    rscale = 1e-3 if "in thousands" in seg2 else 1.0
    seg2b = seg2[seg2.find("Revenue |"):] if "Revenue |" in seg2 else seg2
    d["recon_years"] = ryears
    d["recon"] = {k: tenk_row(seg2b, rx, len(ryears), scale=rscale) for k, rx in RECON_ROWS}
    # FCF reconciliation (annual)
    k2 = t.find("Purchases of property and equipment")
    seg3 = t[k2 - 900:k2 + 500]
    fscale = 1e-3 if "in thousands" in seg3 else 1.0
    TENK_FCF_ROWS = [("cfo", r"\| Net cash provided by (?:\(used in\) )?operating activities \|"), ("capex", r"\| Purchases of property and equipment \|"), ("fcf", r"\| (?:Free Cash Flow|FCF) \|")]
    d["fcf"] = {k: tenk_row(seg3, rx, len(ryears), scale=fscale) for k, rx in TENK_FCF_ROWS}
    # headcount, hosting commitment
    m = re.search(r"As of December 31, (20\d\d), we had (?:approximately )?([\d,]+) employees", t)
    d["headcount"] = (int(m.group(1)), int(m.group(2).replace(",", ""))) if m else None
    m = re.search(r"committed to spend an aggregate of at least \$\s?([\d.,]+) (million|billion)[^.]{0,60}through (20\d\d)", t)
    if m:
        amt = float(m.group(1).replace(",", "")) * (1000 if m.group(2) == "billion" else 1)
        d["hosting_commitment"] = (amt, int(m.group(3)))
    # revenue by region (MD&A table in FY2021/FY2022; note table FY2023+)
    geo = {}
    m = re.search(r"Revenue Disaggregated by Geographic Region.{0,200}?Year Ended December 31, \|((?: 20\d\d \|)+)", t)
    if m:
        gyears = [int(y) for y in re.findall(r"20\d\d", m.group(1))]
        gseg = t[m.end():m.end() + 800]
        for reg, rx in (("na", r"North America"), ("emea", r"Europe, the Middle East, and Africa|EMEA"), ("latam", r"Latin America"), ("apac", r"Asia Pacific")):
            v = tenk_row(gseg, rx, len(gyears))
            if v:
                geo[reg] = dict(zip(gyears, v))
    else:
        m = re.search(r"\| Revenue \|(?: \|)* North America \| \$ \| ([\d,.]+) \| \| (\d+) \| % \| \| \$ \| ([\d,.]+) \|", t)
        if m:
            gseg = t[m.start():m.start() + 900]
            gyears = years[-2:]
            for reg, rx in (("na", r"North America"), ("emea", r"EMEA"), ("latam", r"Latin America"), ("apac", r"Asia Pacific")):
                cells = [c.strip().replace("$", "").strip() for c in gseg[re.search(rx, gseg).end():].split("|")]
                nums = []
                pending = None
                for c in cells[:16]:
                    if re.fullmatch(r"[\d,]+(?:\.\d+)?", c):
                        pending = pnum(c)
                        nums.append(pending)
                    elif c == "%":
                        nums.pop()          # the number just seen was a percentage share
                    elif c and not re.fullmatch(r"[\d,]+(?:\.\d+)?", c) and nums:
                        break
                if len(nums) >= 2:
                    geo[reg] = dict(zip(gyears, nums[:2]))
    d["geo"] = geo
    TENK[fy] = d

# =============================================================================================== 5. quarterly panel assembly
KPI_REPO = pd.read_csv(ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv").set_index("quarter")
REG = pd.read_csv(ROOT / "data/processed/overnight/10_regional_revenue_xbrl.csv", comment="#")
REG = REG[REG["quarter"].astype(str).str.match(r"^\dQ\d\d$")].set_index("quarter")
BS_4Q19 = {"cash_and_equivalents": 2013.547, "short_term_investments": 1060.726, "restricted_cash": 0.115,
           "funds_held_on_behalf": 3145.457, "unearned_fees_balance": 674.788, "long_term_debt_noncurrent": 0.0,
           "long_term_debt_current": 0.0}

rows = []
for q in QUARTERS:
    r = {"quarter": q, "year": 2000 + int(q[2:4]), "qn": int(q[0]), "pre_ipo": qorder(q) < qorder("4Q20")}
    y = r["year"]
    r["period_end"] = {1: f"{y}-03-31", 2: f"{y}-06-30", 3: f"{y}-09-30", 4: f"{y}-12-31"}[r["qn"]]

    def put(line, value, source, detail):
        r[line] = None if value is None else round(float(value), 3)
        prov(q, line, value, source, detail)

    # --- GAAP P&L: XBRL first, 424B4 for 2018-2019 (and as a check for 1Q20-3Q20)
    gaap_lines = ["revenue", "cor_gaap", "ops_gaap", "pd_gaap", "sm_gaap", "ga_gaap", "restr_gaap", "total_costs", "op_income",
                  "interest_income", "interest_expense", "pretax_income", "tax_provision", "net_income"]
    is424 = {}
    if q424_is and q in q424_is[0]:
        i = q424_is[0].index(q)
        mp = {"revenue": "revenue", "cor_gaap": "cor", "ops_gaap": "ops", "pd_gaap": "pd", "sm_gaap": "sm", "ga_gaap": "ga",
              "restr_gaap": "restr", "total_costs": "total_costs", "op_income": "op_income", "interest_income": "int_inc",
              "interest_expense": "int_exp", "other_income_expense": "other", "pretax_income": "pretax", "tax_provision": "tax", "net_income": "net_income"}
        for line, k in mp.items():
            if q424_is[1].get(k) is not None:
                v = q424_is[1][k][i]
                if line == "interest_expense":
                    v = -v
                is424[line] = v
    for line in gaap_lines:
        if q in xq.get(line, {}):
            v, det, fv, ff = xq[line][q]
            put(line, v, "xbrl", det)
            if abs(v - fv) > 0.05:
                prov(q, line, fv, "xbrl_first_vintage", f"first filed {ff}")
                r[line + "_restated"] = True
            if line in is424:
                prov(q, line, is424[line], "424B4", SRC424 + " quarterly table (cross-check)")
        elif line in is424:
            put(line, is424[line], "424B4", SRC424 + " quarterly consolidated statements of operations (in thousands)")
    if r.get("restr_gaap") is None and qorder(q) >= qorder("1Q23"):
        put("restr_gaap", 0.0, "derived", "no restructuring line in the income statement (XBRL RestructuringCharges not tagged after FY2024)")
    if "other_income_expense" in is424 and q not in xq["pretax_income"]:
        put("other_income_expense", is424["other_income_expense"], "424B4", SRC424 + " quarterly table")
    # --- non-GAAP reconciliation (letters, latest vintage; 424B4 for 2018)
    rc = RECON.get(q)
    if rc:
        v = rc["latest"]["vals"]
        det = f"{rc['latest']['src']} Adjusted EBITDA reconciliation ({rc['n']} vintages, latest {rc['latest']['letter']}, first {rc['first']['letter']})"
        put("adj_ebitda_reported", v["adj_ebitda"], "letter", det)
        put("da", v.get("da"), "letter", det)
        put("sbc_recon", v.get("sbc"), "letter", det)
        put("ipo_settlement", v.get("ipo") or 0.0, "letter", det)
        put("acq_impacts", v.get("acq") or 0.0, "letter", det)
        put("lodging_tax_reserves", v.get("lodging") or 0.0, "letter", det)
        put("restr_recon", v.get("restr") or 0.0, "letter", det)
        put("net_income_letter", v.get("net_income"), "letter", det)
        put("tax_provision_letter", v.get("tax"), "letter", det)
        if v.get("int_exp") is not None:
            put("interest_expense_letter", v["int_exp"], "letter", det)
            if r.get("interest_expense") is None:
                put("interest_expense", v["int_exp"], "letter", det + " (interest expense not separately tagged in XBRL for this quarter)")
        if v.get("other") is not None:
            put("other_income_expense_letter", -v["other"], "letter", det)
        if v.get("int_inc") is not None:
            put("interest_income_letter", -v["int_inc"], "letter", det)
        fv = rc["first"]["vals"]
        for k, line in (("adj_ebitda", "adj_ebitda_reported"), ("da", "da"), ("sbc", "sbc_recon"), ("lodging", "lodging_tax_reserves"), ("other", "other_recon"), ("tax", "tax_provision_letter")):
            if fv.get(k) is not None and v.get(k) is not None and abs(fv[k] - v[k]) > 0.6:
                prov(q, line, fv[k], "letter_first_vintage", f"{rc['first']['src']}")
                r[line + "_restated"] = True
                r.setdefault("restatement_notes", [])
                r["restatement_notes"].append(f"{line}: first {fv[k]:.1f} ({rc['first']['letter']}) -> latest {v[k]:.1f} ({rc['latest']['letter']})")
        r["recon_n_vintages"] = rc["n"]
        r["recon_latest_letter"] = rc["latest"]["letter"]
    # --- other income (expense): derived so that op_income + interest income - interest expense + other = pretax
    if r.get("pretax_income") is not None and r.get("op_income") is not None and r.get("interest_income") is not None:
        nonop = r["pretax_income"] - r["op_income"] - r["interest_income"]
        put("nonop_ex_interest_income", nonop, "derived", "pretax income - operating income - interest income (interest expense plus other income (expense), net)")
        if r.get("interest_expense") is not None:
            put("other_income_expense", nonop + r["interest_expense"], "derived", "nonop_ex_interest_income + interest expense")
        else:
            put("other_income_expense", nonop, "derived", "includes interest expense (not separately disclosed for this quarter as reported)")
            r["other_includes_interest_expense"] = True
    # --- shares, EPS
    for line in ("shares_diluted_m", "shares_basic_m", "eps_diluted", "eps_basic"):
        if q in xq[line]:
            put(line, xq[line][q][0], "xbrl", xq[line][q][1])
    if q[0] == "4" and q in LET and LET[q]["is"] and LET[q]["is_cols"]["cy"] is not None:
        Lq, ci = LET[q]["is"], LET[q]["is_cols"]["cy"]
        for line, k in (("eps_diluted", "eps_diluted"), ("eps_basic", "eps_basic"), ("shares_diluted_m", "shares_diluted"), ("shares_basic_m", "shares_basic")):
            if r.get(line) is None and Lq["rows"].get(k):
                put(line, Lq["rows"][k][ci], "letter", f"{LET[q]['src']} statement of operations, three months ended Dec 31 column (weighted averages are not additive, so no XBRL FY-less-9M derivation)")
    if q == "4Q19":
        L = LET["4Q20"]
        if L["is"] and L["is"]["rows"].get("eps_diluted"):
            put("eps_diluted", L["is"]["rows"]["eps_diluted"][0], "letter", "4Q20 letter statement of operations, three months ended Dec 31 2019 (basic and diluted)")
            put("eps_basic", L["is"]["rows"]["eps_basic"][0], "letter", "4Q20 letter, three months ended Dec 31 2019")
            put("shares_diluted_m", L["is"]["rows"]["shares_diluted"][0], "letter", "4Q20 letter, three months ended Dec 31 2019")
            put("shares_basic_m", L["is"]["rows"]["shares_basic"][0], "letter", "4Q20 letter, three months ended Dec 31 2019")
    # --- SBC by function
    sb = SBCQ.get(q)
    src_sbc = None
    if sb:
        cy = [s for s in sb if s["which"] == "cy"]
        pick = cy[0] if cy else sb[0]
        src_sbc = pick["src"] + (" statement-of-operations footnote, column matched to the quarter's SBC total" if not pick["letter"].startswith("10-Q") else "")
        for k in ("sbc_ops", "sbc_pd", "sbc_sm", "sbc_ga", "sbc_restr"):
            put(k, pick["vals"].get(k) if pick["vals"].get(k) is not None else 0.0, "letter" if not pick["letter"].startswith("10-Q") else "10-Q", src_sbc)
        put("sbc_total_footnote", pick["vals"].get("sbc_total"), "letter" if not pick["letter"].startswith("10-Q") else "10-Q", src_sbc)
        for other in sb:
            if other is not pick:
                for k in ("sbc_ops", "sbc_pd", "sbc_sm", "sbc_ga"):
                    if other["vals"].get(k) is not None:
                        prov(q, k, other["vals"][k], "letter_other_vintage", other["src"] + f" ({other['which']} column)")
    elif q424_sbc and q in q424_sbc[0]:
        i = q424_sbc[0].index(q)
        for k in ("sbc_ops", "sbc_pd", "sbc_sm", "sbc_ga", "sbc_restr", "sbc_total"):
            v = q424_sbc[1][k][i] if q424_sbc[1].get(k) is not None else 0.0
            put(k if k != "sbc_total" else "sbc_total_footnote", v, "424B4", SRC424 + " quarterly SBC-by-function table (in thousands)")
    if r.get("sbc_total_is") is not None:
        r["sbc_total_xbrl"] = r["sbc_total_is"]
    if r.get("sbc_total_footnote") is not None:
        put("sbc_total_is", r["sbc_total_footnote"], "letter/424B4/10-Q", "income statement footnote total (the FY2024-25 10-Ks tag AllocatedShareBasedCompensationExpense only as a rounded $1.4B/$1.6B, so XBRL FY-less-9M is unreliable for Q4; sbc_total_xbrl keeps the XBRL derivation)")
    # --- cash cost lines
    for line, sk in (("cor", None), ("ops", "sbc_ops"), ("pd", "sbc_pd"), ("sm", "sbc_sm"), ("ga", "sbc_ga")):
        g = r.get(line + "_gaap")
        s = 0.0 if sk is None else r.get(sk)
        if g is not None and s is not None:
            put(line + "_cash", g - s, "derived", f"{line}_gaap minus {sk or 'nothing (no SBC in cost of revenue)'}")
    # --- FCF
    fc = FCF.get(q)
    if fc:
        v = fc["latest"]["vals"]
        det = f"{fc['latest']['src']} Free Cash Flow reconciliation ({fc['n']} vintages, latest {fc['latest']['letter']}, first {fc['first']['letter']})"
        put("cfo_letter", v["cfo"], "letter", det)
        put("capex", -v["capex"], "letter", det + " (purchases of property and equipment, shown positive)")
        put("fcf_reported", v["fcf"], "letter", det)
        if abs(fc["first"]["vals"]["cfo"] - v["cfo"]) > 0.6:
            prov(q, "cfo_letter", fc["first"]["vals"]["cfo"], "letter_first_vintage", fc["first"]["src"])
            r["cfo_restated"] = True
            r.setdefault("restatement_notes", []).append(f"cfo: first {fc['first']['vals']['cfo']:.1f} ({fc['first']['letter']}) -> latest {v['cfo']:.1f} ({fc['latest']['letter']})")
    # --- cash-flow YTD lines (XBRL, de-cumulated)
    for line in ("cfo_xbrl", "capex_xbrl", "change_unearned_fees", "change_funds_receivable_xbrl", "rsu_tax_withholding", "income_taxes_paid", "da_cashflow", "sbc_cashflow", "buybacks_cash"):
        if q in xq_cf[line]:
            v, det, fv, ff = xq_cf[line][q]
            put(line, v, "xbrl", det)
    # CFO: the letters' FCF tables are the consistent quarterly series (the 2022 filings re-presented 2020-2021 CFO;
    # companyfacts holds only the original 9M comparatives, so an XBRL FY-less-9M mixes presentations for 4Q20/4Q21)
    if r.get("cfo_letter") is not None:
        put("cfo", r["cfo_letter"], "letter", "letter FCF reconciliation, latest vintage (cfo_xbrl carries the companyfacts derivation)")
    elif r.get("cfo_xbrl") is not None:
        put("cfo", r["cfo_xbrl"], "xbrl", "companyfacts derivation")
    if q in xq["buybacks"]:
        put("buybacks", xq["buybacks"][q][0], "xbrl", xq["buybacks"][q][1])
    elif r.get("buybacks_cash") is not None:
        put("buybacks", r["buybacks_cash"], "xbrl", "PaymentsForRepurchaseOfCommonStock de-cumulated")
    else:
        put("buybacks", 0.0 if qorder(q) < qorder("3Q22") else None, "derived", "no repurchase programme before Aug 2022")
    # change in funds payable from the letter cash-flow statements (YTD, de-cumulated), XBRL to 2021
    if q in LET and LET[q]["cf"]:
        cf = LET[q]["cf"]
        chosen = None
        for orient in ("after", "before"):
            v = cf[orient]["cfo"]
            if v and any(abs(x - cfo_ytd_latest.get(q, -9e9)) < 0.6 or abs(x - cfo_ytd_first.get(q, -9e9)) < 0.6 for x in v):
                chosen = orient
                break
        if chosen:
            colidx = [i for i, x in enumerate(cf[chosen]["cfo"]) if abs(x - cfo_ytd_latest.get(q, -9e9)) < 0.6 or abs(x - cfo_ytd_first.get(q, -9e9)) < 0.6][0]
            LET[q]["cf_pick"] = (chosen, colidx)
            for k in ("cf_funds_payable", "cf_unearned", "cf_da", "cf_sbc", "cf_buybacks", "cf_rsu_tax"):
                v = cf[chosen].get(k)
                if v:
                    LET[q].setdefault("cf_ytd", {})[k] = v[colidx]
                    if colidx == 1 and cf["n"] == 2:
                        LET[q].setdefault("cf_ytd_py", {})[k] = v[0]     # prior-year YTD column, as re-presented
        else:
            warn(f"{q} letter: cash-flow statement column could not be matched to XBRL CFO")
    rows.append(r)

# de-cumulate the letter cash-flow YTD lines. YTD(q) comes from q's own letter (current-year column) or, for 2020,
# from the prior-year column of the letter one year later (the 2021 letters re-present 2020 under the new layout).
def ytd_value(q, k):
    L = LET.get(q)
    if L and "cf_ytd" in L and k in L["cf_ytd"]:
        return L["cf_ytd"][k], f"{L['src']} cash-flow statement YTD"
    nq = qlabel(2000 + int(q[2:4]) + 1, int(q[0]))
    L2 = LET.get(nq)
    if L2 and "cf_ytd_py" in L2 and k in L2["cf_ytd_py"]:
        return L2["cf_ytd_py"][k], f"{L2['src']} cash-flow statement, prior-year YTD column"
    return None, None


for r in rows:
    q = r["quarter"]
    for k, line in (("cf_funds_payable", "change_funds_payable"), ("cf_unearned", "change_unearned_fees_letter"), ("cf_da", "da_cashflow_letter"), ("cf_buybacks", "buybacks_letter"), ("cf_rsu_tax", "rsu_tax_letter")):
        v, det = ytd_value(q, k)
        if v is None:
            continue
        if q[0] != "1":
            pv, pdet = ytd_value(prev_q(q), k)
            if pv is None:
                continue
            v = v - pv
            det += f" less {prev_q(q)} YTD"
        r[line] = round(v, 3)
        prov(q, line, v, "letter", det)

# balance sheet, KPIs, regional revenue
kpi_letter = {}
for lq in ("1Q21", "4Q21"):
    for qq, v in LET[lq]["kpi"].items():
        kpi_letter.setdefault(qq, []).append((lq, v))
for r in rows:
    q = r["quarter"]
    for line in XINST:
        if q in xinst[line]:
            r[line] = round(xinst[line][q][0], 3)
            prov(q, line, r[line], "xbrl", xinst[line][q][1])
        elif q == "4Q19":
            r[line] = BS_4Q19[line]
            prov(q, line, r[line], "letter", "4Q20 letter condensed consolidated balance sheet, Dec 31 2019 column (in thousands)")
    if r.get("cash_and_equivalents") is not None:
        r["cash_and_investments_total"] = round(r["cash_and_equivalents"] + (r.get("short_term_investments") or 0) + (r.get("restricted_cash") or 0), 3)
        prov(q, "cash_and_investments_total", r["cash_and_investments_total"], "derived", "cash + short-term investments + restricted cash (letter definition of 'cash and other liquid assets')")
    if r.get("long_term_debt_noncurrent") is not None:
        r["long_term_debt_total"] = round(r["long_term_debt_noncurrent"] + (r.get("long_term_debt_current") or 0), 3)
    # KPIs
    if q in KPI_REPO.index and not pd.isna(KPI_REPO.loc[q, "nights_m"]):
        for line, col in (("nights_m", "nights_m"), ("gbv_busd", "gbv_busd"), ("adr_usd", "adr_usd")):
            r[line] = float(KPI_REPO.loc[q, col])
            prov(q, line, r[line], "repo_kpi_panel", "data/processed/overnight/02_kpi_panel_quarterly.csv (letter KPI box / summary table, validated in analysis/src/abnb_exsbc_stack.py)")
        if q in kpi_letter:
            for lq, v in kpi_letter[q]:
                if abs(v["nights_m"] - r["nights_m"]) > 0.05 or abs(v["gbv_busd"] - r["gbv_busd"]) > 0.05:
                    warn(f"{q}: {lq} letter KPI table ({v}) disagrees with the repo KPI panel ({r['nights_m']}, {r['gbv_busd']})")
    elif q in kpi_letter:
        lq, v = sorted(kpi_letter[q])[0]
        r["nights_m"], r["gbv_busd"], r["adr_usd"] = v["nights_m"], v["gbv_busd"], v["adr_usd"]
        prov(q, "nights_m", v["nights_m"], "letter", f"{lq} letter quarterly summary table ({v.get('method')})")
        prov(q, "gbv_busd", v["gbv_busd"], "letter", f"{lq} letter quarterly summary table")
        prov(q, "adr_usd", v["adr_usd"], "letter", f"{lq} letter quarterly summary table (GBV per Night and Experience Booked)")
    if q in REG.index:
        for reg in ("na", "emea", "latam", "apac", "us", "non_us"):
            v = REG.loc[q, reg]
            if not pd.isna(v):
                r["rev_" + reg] = float(v)
                prov(q, "rev_" + reg, float(v), "repo_regional_panel", f"data/processed/overnight/10_regional_revenue_xbrl.csv ({REG.loc[q, 'basis']}; XBRL srt:StatementGeographicalAxis)")

# derived per-quarter metrics
for r in rows:
    q = r["quarter"]
    rev = r.get("revenue")
    if rev:
        if r.get("adj_ebitda_reported") is not None:
            r["adj_ebitda_margin_pct"] = round(100 * r["adj_ebitda_reported"] / rev, 2)
        for line in ("cor", "ops", "pd", "sm", "ga"):
            if r.get(line + "_gaap") is not None:
                r[line + "_gaap_pct_rev"] = round(100 * r[line + "_gaap"] / rev, 2)
            if r.get(line + "_cash") is not None:
                r[line + "_cash_pct_rev"] = round(100 * r[line + "_cash"] / rev, 2)
        if r.get("sbc_total_is") is not None:
            r["sbc_pct_rev"] = round(100 * r["sbc_total_is"] / rev, 2)
        if r.get("op_income") is not None:
            r["op_margin_pct"] = round(100 * r["op_income"] / rev, 2)
        if r.get("fcf_reported") is not None:
            r["fcf_margin_pct"] = round(100 * r["fcf_reported"] / rev, 2)
        if r.get("net_income") is not None:
            r["net_margin_pct"] = round(100 * r["net_income"] / rev, 2)
    if r.get("nights_m") and rev:
        r["revenue_per_night_usd"] = round(rev / r["nights_m"], 3)
        for line in ("cor", "ops", "pd", "sm", "ga"):
            if r.get(line + "_cash") is not None:
                r[line + "_cash_per_night_usd"] = round(r[line + "_cash"] / r["nights_m"], 3)
        if r.get("adj_ebitda_reported") is not None:
            r["adj_ebitda_per_night_usd"] = round(r["adj_ebitda_reported"] / r["nights_m"], 3)
    if r.get("gbv_busd") and rev:
        r["take_rate_pct"] = round(100 * rev / (1000 * r["gbv_busd"]), 3)
        if r.get("cor_cash") is not None:
            r["cor_cash_pct_gbv"] = round(100 * r["cor_cash"] / (1000 * r["gbv_busd"]), 3)
    if r.get("pretax_income") is not None and r.get("tax_provision") is not None and r["pretax_income"] != 0:
        r["effective_tax_rate_pct"] = round(100 * r["tax_provision"] / r["pretax_income"], 2)
    # rebuild: revenue - six GAAP lines + D&A + SBC(recon) + IPO + acq + lodging + restructuring(recon)
    need = ("revenue", "cor_gaap", "ops_gaap", "pd_gaap", "sm_gaap", "ga_gaap", "da", "sbc_recon")
    if all(r.get(k) is not None for k in need) and r.get("adj_ebitda_reported") is not None:
        rebuilt = (r["revenue"] - r["cor_gaap"] - r["ops_gaap"] - r["pd_gaap"] - r["sm_gaap"] - r["ga_gaap"] - (r.get("restr_gaap") or 0.0)
                   + r["da"] + r["sbc_recon"] + (r.get("ipo_settlement") or 0.0) + (r.get("acq_impacts") or 0.0)
                   + (r.get("lodging_tax_reserves") or 0.0) + (r.get("restr_recon") or 0.0))
        r["adj_ebitda_rebuilt"] = round(rebuilt, 3)
        r["rebuild_gap"] = round(rebuilt - r["adj_ebitda_reported"], 3)
        r["other_addbacks_total"] = round((r.get("ipo_settlement") or 0.0) + (r.get("acq_impacts") or 0.0) + (r.get("lodging_tax_reserves") or 0.0), 3)
        # cash-cost identity: adj EBITDA = revenue - cash lines - (restr_gaap - restr_recon) + other add-backs + (sbc_recon - sbc_by_line_total)
    if all(r.get(k) is not None for k in ("cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash")):
        r["total_cash_costs"] = round(r["cor_cash"] + r["ops_cash"] + r["pd_cash"] + r["sm_cash"] + r["ga_cash"], 3)
    if r.get("ga_cash") is not None and r.get("lodging_tax_reserves") is not None:
        r["ga_cash_ex_lodging"] = round(r["ga_cash"] - r["lodging_tax_reserves"], 3)   # lodging/withholding tax reserves sit in G&A (10-K)
    if r.get("revenue") is not None and r.get("adj_ebitda_reported") is not None:
        r["adj_cost_total"] = round(r["revenue"] - r["adj_ebitda_reported"], 3)          # every cost that Adjusted EBITDA bears
    if r.get("sbc_recon") is not None and r.get("sbc_total_footnote") is not None:
        r["sbc_footnote_minus_recon"] = round(r["sbc_total_footnote"] - r["sbc_recon"], 3)
    if r.get("cfo") is not None and r.get("capex") is not None and r.get("fcf_reported") is not None:
        r["fcf_check_gap"] = round(r["cfo"] - r["capex"] - r["fcf_reported"], 3)
    if isinstance(r.get("restatement_notes"), list):
        r["restatement_notes"] = "; ".join(r["restatement_notes"])

# y/y growth columns
P = pd.DataFrame(rows).set_index("quarter")
for line in ("revenue", "nights_m", "gbv_busd", "adr_usd", "cor_gaap", "ops_gaap", "pd_gaap", "sm_gaap", "ga_gaap", "cor_cash", "ops_cash",
             "pd_cash", "sm_cash", "ga_cash", "adj_ebitda_reported", "sbc_total_is", "fcf_reported", "revenue_per_night_usd"):
    if line in P:
        P[line + "_yoy_pct"] = (100 * (P[line] / P[line].shift(4) - 1)).round(2)
P["adj_ebitda_margin_yoy_pp"] = (P["adj_ebitda_margin_pct"] - P["adj_ebitda_margin_pct"].shift(4)).round(2)

COLS = ["year", "qn", "period_end", "pre_ipo", "revenue", "cor_gaap", "ops_gaap", "pd_gaap", "sm_gaap", "ga_gaap", "restr_gaap", "total_costs",
        "op_income", "interest_income", "interest_expense", "other_income_expense", "nonop_ex_interest_income", "pretax_income", "tax_provision",
        "net_income", "eps_basic", "eps_diluted", "shares_basic_m", "shares_diluted_m", "effective_tax_rate_pct",
        "sbc_ops", "sbc_pd", "sbc_sm", "sbc_ga", "sbc_restr", "sbc_total_footnote", "sbc_total_is", "sbc_total_xbrl", "sbc_recon", "sbc_footnote_minus_recon",
        "cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash", "ga_cash_ex_lodging", "total_cash_costs", "adj_cost_total",
        "da", "ipo_settlement", "acq_impacts", "lodging_tax_reserves", "restr_recon", "other_addbacks_total",
        "adj_ebitda_reported", "adj_ebitda_rebuilt", "rebuild_gap", "adj_ebitda_margin_pct", "op_margin_pct", "net_margin_pct",
        "cfo", "cfo_xbrl", "capex", "capex_xbrl", "fcf_reported", "fcf_check_gap", "fcf_margin_pct", "change_unearned_fees", "change_unearned_fees_letter",
        "change_funds_payable", "change_funds_receivable_xbrl", "da_cashflow", "sbc_cashflow", "buybacks", "buybacks_cash", "rsu_tax_withholding", "income_taxes_paid",
        "cash_and_equivalents", "short_term_investments", "restricted_cash", "cash_and_investments_total", "funds_held_on_behalf",
        "unearned_fees_balance", "long_term_debt_noncurrent", "long_term_debt_current", "long_term_debt_total",
        "nights_m", "gbv_busd", "adr_usd", "revenue_per_night_usd", "take_rate_pct", "cor_cash_pct_gbv",
        "cor_gaap_pct_rev", "ops_gaap_pct_rev", "pd_gaap_pct_rev", "sm_gaap_pct_rev", "ga_gaap_pct_rev", "sbc_pct_rev",
        "cor_cash_pct_rev", "ops_cash_pct_rev", "pd_cash_pct_rev", "sm_cash_pct_rev", "ga_cash_pct_rev",
        "cor_cash_per_night_usd", "ops_cash_per_night_usd", "pd_cash_per_night_usd", "sm_cash_per_night_usd", "ga_cash_per_night_usd", "adj_ebitda_per_night_usd",
        "rev_na", "rev_emea", "rev_latam", "rev_apac", "rev_us", "rev_non_us",
        "revenue_yoy_pct", "nights_m_yoy_pct", "gbv_busd_yoy_pct", "adr_usd_yoy_pct", "revenue_per_night_usd_yoy_pct", "cor_gaap_yoy_pct", "ops_gaap_yoy_pct", "pd_gaap_yoy_pct",
        "sm_gaap_yoy_pct", "ga_gaap_yoy_pct", "cor_cash_yoy_pct", "ops_cash_yoy_pct", "pd_cash_yoy_pct", "sm_cash_yoy_pct", "ga_cash_yoy_pct",
        "adj_ebitda_reported_yoy_pct", "adj_ebitda_margin_yoy_pp", "sbc_total_is_yoy_pct", "fcf_reported_yoy_pct",
        "recon_n_vintages", "recon_latest_letter", "other_includes_interest_expense", "cfo_restated", "adj_ebitda_reported_restated", "restatement_notes",
        "net_income_letter", "tax_provision_letter", "interest_expense_letter", "other_income_expense_letter", "interest_income_letter"]
for c in COLS:
    if c not in P:
        P[c] = np.nan
P = P[COLS]
P.to_csv(OUT / "02_panel_quarterly.csv", float_format="%.3f")
pd.DataFrame(PROV).to_csv(OUT / "02_panel_provenance.csv", index=False)
V = pd.DataFrame(VINT)
V = V[V["period"].str.match(r"^\dQ\d\d$")]
V["vintage_order"] = V["letter"].map(lambda s: -1 if s == "424B4" else qorder(s))
V = V.sort_values(["period", "line", "vintage_order"])
V.to_csv(OUT / "02_letter_vintages.csv", index=False)

# =============================================================================================== 6. annual panel
arows = []
for y in YEARS:
    a = {"year": y}
    src10k = None

    def puta(line, value, source, detail):
        a[line] = None if value is None else round(float(value), 3)
        prov(f"FY{y}", line, value, source, detail)

    if y >= 2019:
        for line in ("revenue", "cor_gaap", "ops_gaap", "pd_gaap", "sm_gaap", "ga_gaap", "restr_gaap", "total_costs", "op_income", "interest_income",
                     "interest_expense", "pretax_income", "tax_provision", "net_income", "sbc_total_is", "shares_diluted_m", "shares_basic_m",
                     "eps_diluted", "eps_basic", "cfo", "income_taxes_paid", "rsu_tax_withholding", "buybacks_cash", "change_unearned_fees",
                     "sbc_cashflow", "da_cashflow", "advertising_expense"):
            if y in xa.get(line, {}):
                v, det, fv, ff = xa[line][y]
                puta(line, v, "xbrl", det)
                if abs(v - fv) > 0.05:
                    prov(f"FY{y}", line, fv, "xbrl_first_vintage", f"first filed {ff}")
    else:  # FY2018 from the 10-K FY2020 text tables (in thousands)
        d = TENK[2020]
        i = d["years"].index(2018)
        mp = {"revenue": "revenue", "cor_gaap": "cor", "ops_gaap": "ops", "pd_gaap": "pd", "sm_gaap": "sm", "ga_gaap": "ga", "restr_gaap": "restr",
              "total_costs": "total_costs", "op_income": "op_income", "interest_income": "int_inc", "interest_expense": "int_exp",
              "other_income_expense": "other", "pretax_income": "pretax", "tax_provision": "tax", "net_income": "net_income"}
        for line, k in mp.items():
            v = d["is"].get(k)
            if v:
                puta(line, -v[i] if line == "interest_expense" else v[i], "10-K", d["src"] + " results of operations table, 2018 column")
        for k in ("sbc_ops", "sbc_pd", "sbc_sm", "sbc_ga", "sbc_restr", "sbc_total"):
            v = d["sbc"].get(k)
            if v:
                puta(k if k != "sbc_total" else "sbc_total_is", v[i], "10-K", d["src"] + " SBC by function note, 2018 column")
        a["restr_gaap"] = 0.0
        if kpi424:
            puta("nights_m", kpi424["nights_m"][2018], "424B4", SRC424 + " MD&A key business metrics")
            puta("gbv_busd", kpi424["gbv_busd"][2018], "424B4", SRC424 + " MD&A key business metrics")
    # SBC by function from the 10-K note (latest 10-K containing the year)
    for fy in sorted(TENK, reverse=True):
        d = TENK[fy]
        if y in d["years"] and d["sbc"].get("sbc_total"):
            i = d["years"].index(y)
            for k in ("sbc_ops", "sbc_pd", "sbc_sm", "sbc_ga", "sbc_restr"):
                v = d["sbc"].get(k)
                puta(k, v[i] if v else 0.0, "10-K", d["src"] + f" SBC by function note, {y} column")
            puta("sbc_total_footnote", d["sbc"]["sbc_total"][i], "10-K", d["src"] + f" SBC by function note, {y} column")
            break
    if a.get("sbc_total_footnote") is not None:
        a["sbc_total_xbrl"] = a.get("sbc_total_is")
        puta("sbc_total_is", a["sbc_total_footnote"], "10-K", "SBC by function note total (XBRL AllocatedShareBasedCompensationExpense is tagged as a rounded $1.1B/$1.4B/$1.6B in the FY2024-25 10-Ks)")
    # Adjusted EBITDA reconciliation from the 10-K (latest 10-K containing the year); FY2018 from FY2020 10-K
    for fy in sorted(TENK, reverse=True):
        d = TENK[fy]
        if y in d["recon_years"] and d["recon"].get("adj_ebitda"):
            i = d["recon_years"].index(y)
            rr = d["recon"]
            det = d["src"] + f" Adjusted EBITDA reconciliation, {y} column"
            puta("adj_ebitda_reported", rr["adj_ebitda"][i], "10-K", det)
            puta("da", rr["da"][i] if rr.get("da") else None, "10-K", det)
            puta("sbc_recon", rr["sbc"][i] if rr.get("sbc") else None, "10-K", det)
            puta("ipo_settlement", rr["ipo"][i] if rr.get("ipo") else 0.0, "10-K", det)
            puta("acq_impacts", rr["acq"][i] if rr.get("acq") else 0.0, "10-K", det)
            puta("lodging_tax_reserves", rr["lodging"][i] if rr.get("lodging") else 0.0, "10-K", det)
            puta("restr_recon", rr["restr"][i] if rr.get("restr") else 0.0, "10-K", det)
            if rr.get("int_exp"):
                puta("interest_expense_recon", rr["int_exp"][i], "10-K", det)
            if rr.get("other"):
                puta("other_income_expense_recon", -rr["other"][i], "10-K", det)
            a["recon_10k"] = f"FY{fy}"
            break
    for fy in sorted(TENK, reverse=True):
        d = TENK[fy]
        if y in d["recon_years"] and d["fcf"].get("fcf"):
            i = d["recon_years"].index(y)
            det = d["src"] + f" Free Cash Flow reconciliation, {y} column"
            puta("cfo_10k", d["fcf"]["cfo"][i], "10-K", det)
            puta("capex", -d["fcf"]["capex"][i], "10-K", det)
            puta("fcf_reported", d["fcf"]["fcf"][i], "10-K", det)
            break
    if a.get("cfo") is None and a.get("cfo_10k") is not None:
        puta("cfo", a["cfo_10k"], "10-K", "FCF reconciliation")
    if a.get("cfo") is not None and a.get("capex") is not None:
        puta("fcf_latest_vintage", a["cfo"] - a["capex"], "derived", "latest-vintage CFO (XBRL) less capex; differs from fcf_reported for 2019-2020 because the 2022-23 filings re-presented CFO")
    if a.get("restr_gaap") is None and y >= 2023:
        a["restr_gaap"] = 0.0
    for fy, d in TENK.items():
        if d.get("headcount") and d["headcount"][0] == y:
            puta("headcount_dec31", d["headcount"][1], "10-K", d["src"] + " Human Capital section")
        if d.get("hosting_commitment") and fy == y:
            puta("hosting_commitment_remaining", d["hosting_commitment"][0], "10-K", d["src"] + f" commitments note (through {d['hosting_commitment'][1]})")
            a["hosting_commitment_through"] = d["hosting_commitment"][1]
        if d.get("geo"):
            for reg, m in d["geo"].items():
                if y in m and a.get("rev_" + reg) is None:
                    puta("rev_" + reg, m[y], "10-K", d["src"] + f" revenue by geographic region, {y} column")
    if a.get("pretax_income") is not None and a.get("op_income") is not None and a.get("interest_income") is not None:
        nonop = a["pretax_income"] - a["op_income"] - a["interest_income"]
        puta("nonop_ex_interest_income", nonop, "derived", "pretax - operating income - interest income")
        if a.get("interest_expense") is not None:
            puta("other_income_expense", nonop + a["interest_expense"], "derived", "nonop + interest expense")
        elif a.get("interest_expense_recon") is not None:
            puta("interest_expense", a["interest_expense_recon"], "10-K", "Adjusted EBITDA reconciliation row (not tagged separately in XBRL)")
            puta("other_income_expense", nonop + a["interest_expense_recon"], "derived", "nonop + interest expense (recon row)")
        else:
            puta("other_income_expense", nonop, "derived", "includes interest expense (folded into other income (expense), net in the FY2024/FY2025 10-K)")
            a["other_includes_interest_expense"] = True
    for line, sk in (("cor", None), ("ops", "sbc_ops"), ("pd", "sbc_pd"), ("sm", "sbc_sm"), ("ga", "sbc_ga")):
        g = a.get(line + "_gaap")
        s = 0.0 if sk is None else a.get(sk)
        if g is not None and s is not None:
            puta(line + "_cash", g - s, "derived", f"{line}_gaap minus {sk or 'nothing'}")
    # KPIs annual: sum of quarterly nights / GBV; ADR = GBV/nights
    qs = P[P["year"] == y]
    if qs["nights_m"].notna().sum() == 4:
        a["nights_m"] = round(qs["nights_m"].sum(), 1)
        a["gbv_busd"] = round(qs["gbv_busd"].sum(), 1)
    if a.get("nights_m") and a.get("gbv_busd"):
        a["adr_usd"] = round(1000 * a["gbv_busd"] / a["nights_m"], 2)
        a["take_rate_pct"] = round(100 * a["revenue"] / (1000 * a["gbv_busd"]), 3) if a.get("revenue") else None
    if a.get("revenue"):
        if a.get("adj_ebitda_reported") is not None:
            a["adj_ebitda_margin_pct"] = round(100 * a["adj_ebitda_reported"] / a["revenue"], 2)
        for line in ("cor", "ops", "pd", "sm", "ga"):
            if a.get(line + "_gaap") is not None:
                a[line + "_gaap_pct_rev"] = round(100 * a[line + "_gaap"] / a["revenue"], 2)
            if a.get(line + "_cash") is not None:
                a[line + "_cash_pct_rev"] = round(100 * a[line + "_cash"] / a["revenue"], 2)
        if a.get("fcf_reported") is not None:
            a["fcf_margin_pct"] = round(100 * a["fcf_reported"] / a["revenue"], 2)
        if a.get("sbc_total_is") is not None:
            a["sbc_pct_rev"] = round(100 * a["sbc_total_is"] / a["revenue"], 2)
    if all(a.get(k) is not None for k in ("revenue", "cor_gaap", "ops_gaap", "pd_gaap", "sm_gaap", "ga_gaap", "da", "sbc_recon", "adj_ebitda_reported")):
        rebuilt = (a["revenue"] - a["cor_gaap"] - a["ops_gaap"] - a["pd_gaap"] - a["sm_gaap"] - a["ga_gaap"] - (a.get("restr_gaap") or 0)
                   + a["da"] + a["sbc_recon"] + (a.get("ipo_settlement") or 0) + (a.get("acq_impacts") or 0) + (a.get("lodging_tax_reserves") or 0) + (a.get("restr_recon") or 0))
        a["adj_ebitda_rebuilt"] = round(rebuilt, 3)
        a["rebuild_gap"] = round(rebuilt - a["adj_ebitda_reported"], 3)
    # sum-of-quarters checks
    for line in ("revenue", "cor_gaap", "ops_gaap", "pd_gaap", "sm_gaap", "ga_gaap", "restr_gaap", "op_income", "net_income", "sbc_total_is",
                 "sbc_ops", "sbc_pd", "sbc_sm", "sbc_ga", "da", "sbc_recon", "lodging_tax_reserves", "adj_ebitda_reported", "cfo", "capex", "fcf_reported", "tax_provision", "interest_income"):
        if line in qs and qs[line].notna().sum() == 4 and a.get(line) is not None:
            a["soq_minus_annual__" + line] = round(qs[line].sum() - a[line], 3)
    if a.get("fcf_latest_vintage") is not None and qs["fcf_reported"].notna().sum() == 4:
        a["soq_minus_annual__fcf_latest_vintage"] = round(qs["fcf_reported"].sum() - a["fcf_latest_vintage"], 3)
    arows.append(a)
A = pd.DataFrame(arows).set_index("year")
A.to_csv(OUT / "02_panel_annual.csv", float_format="%.3f")

# =============================================================================================== 7. seasonality
srows = []
LINES_S = [("revenue", "revenue"), ("adj_ebitda_reported", "adj_ebitda"), ("cor_gaap", "cor_gaap"), ("ops_gaap", "ops_gaap"), ("pd_gaap", "pd_gaap"),
           ("sm_gaap", "sm_gaap"), ("ga_gaap", "ga_gaap"), ("cor_cash", "cor_cash"), ("ops_cash", "ops_cash"), ("pd_cash", "pd_cash"),
           ("sm_cash", "sm_cash"), ("ga_cash", "ga_cash"), ("ga_cash_ex_lodging", "ga_cash_ex_lodging"), ("total_cash_costs", "total_cash_costs"), ("adj_cost_total", "adj_cost_total"), ("sbc_total_is", "sbc"), ("da", "da"),
           ("nights_m", "nights"), ("gbv_busd", "gbv"), ("fcf_reported", "fcf"), ("cfo", "cfo"), ("interest_income", "interest_income"), ("tax_provision", "tax_provision")]
for y in YEARS:
    qs = P[P["year"] == y]
    if len(qs) < 4:
        continue
    fy_rev = qs["revenue"].sum()
    fy_nights = qs["nights_m"].sum() if qs["nights_m"].notna().all() else np.nan
    fy_cash = qs["adj_cost_total"].sum() if qs["adj_cost_total"].notna().all() else np.nan
    for col, name in LINES_S:
        if col not in qs or qs[col].isna().any():
            continue
        tot = qs[col].sum()
        for q, v in qs[col].items():
            s = {"year": y, "quarter": q, "qn": int(q[0]), "line": name, "value_musd": round(v, 3), "fy_total": round(tot, 3),
                 "q_share_of_fy_pct": round(100 * v / tot, 2) if tot else np.nan,
                 "q_share_of_fy_revenue_pct": round(100 * qs.loc[q, "revenue"] / fy_rev, 2),
                 "pct_of_revenue": round(100 * v / qs.loc[q, "revenue"], 2) if qs.loc[q, "revenue"] else np.nan,
                 "per_night_usd": round(v / qs.loc[q, "nights_m"], 3) if not pd.isna(qs.loc[q, "nights_m"]) and name not in ("nights", "gbv") else np.nan,
                 "q_share_of_fy_nights_pct": round(100 * qs.loc[q, "nights_m"] / fy_nights, 2) if not pd.isna(fy_nights) else np.nan}
            # mechanical vs discretionary: what the quarter's margin would be if every cash cost line were flat across the year
            if name == "adj_ebitda" and not pd.isna(fy_cash):
                flat_cost = fy_cash / 4       # the FY cost that Adjusted EBITDA bears, spread evenly over the four quarters
                mech = 100 * (qs.loc[q, "revenue"] - flat_cost) / qs.loc[q, "revenue"]
                s["margin_actual_pct"] = round(100 * v / qs.loc[q, "revenue"], 2)
                s["margin_if_costs_flat_pct"] = round(mech, 2)
                s["margin_discretionary_timing_pp"] = round(s["margin_actual_pct"] - mech, 2)
            srows.append(s)
S = pd.DataFrame(srows)
# 2023-2025 mean and range per line and quarter
agg = S[S["year"].between(2023, 2025)].groupby(["line", "qn"]).agg(share_mean_2023_25=("q_share_of_fy_pct", "mean"), share_min_2023_25=("q_share_of_fy_pct", "min"),
                                                                    share_max_2023_25=("q_share_of_fy_pct", "max"), pct_rev_mean_2023_25=("pct_of_revenue", "mean"),
                                                                    pct_rev_min_2023_25=("pct_of_revenue", "min"), pct_rev_max_2023_25=("pct_of_revenue", "max"),
                                                                    per_night_mean_2023_25=("per_night_usd", "mean")).round(2).reset_index()
S = S.merge(agg, on=["line", "qn"], how="left")
S.to_csv(OUT / "02_seasonality.csv", index=False)

# =============================================================================================== 8. reconciliation vs existing repo panels
rec = []
for q, r in P.iterrows():
    if not pd.isna(r["rebuild_gap"]):
        rec.append({"quarter": q, "line": "adj_ebitda", "panel": "rebuilt_from_lines", "mine": r["adj_ebitda_rebuilt"], "theirs": r["adj_ebitda_reported"],
                    "diff": r["rebuild_gap"], "explanation": "" if abs(r["rebuild_gap"]) <= 1.0 else "rebuild gap > $1M: see note"})
CL = pd.read_csv(ROOT / "data/processed/abnb_quarterly_costlines.csv").set_index("quarter")
EX = pd.read_csv(ROOT / "data/processed/abnb_quarterly_cost_stack_exsbc.csv").set_index("quarter")
FB = pd.read_csv(ROOT / "data/processed/abnb_fcf_bridge.csv").set_index("period")
KP = KPI_REPO
MAPS = [
    ("abnb_quarterly_costlines.csv", CL, [("revenue", "revenue_musd"), ("cor_gaap", "cost_of_revenue_musd"), ("ops_gaap", "operations_and_support_musd"), ("pd_gaap", "product_development_musd"),
                                          ("sm_gaap", "sales_and_marketing_musd"), ("ga_gaap", "general_and_administrative_musd"), ("restr_gaap", "restructuring_musd"),
                                          ("sbc_total_is", "stock_based_comp_total_musd"), ("op_income", "operating_income_musd"), ("adj_ebitda_reported", "adjusted_ebitda_musd")]),
    ("abnb_quarterly_cost_stack_exsbc.csv", EX, [("revenue", "revenue_musd"), ("nights_m", "nights_m"), ("gbv_busd", "gbv_busd"), ("adr_usd", "adr"), ("cor_cash", "cor_cash"), ("ops_cash", "ops_cash"),
                                                 ("pd_cash", "pd_cash"), ("sm_cash", "sm_cash"), ("ga_cash", "ga_cash"), ("restr_gaap", "restr"), ("sbc_ops", "sbc_ops"), ("sbc_pd", "sbc_pd"),
                                                 ("sbc_sm", "sbc_sm"), ("sbc_ga", "sbc_ga"), ("sbc_total_is", "sbc_total"), ("da", "da"), ("other_addbacks_total", "other_addbacks"), ("adj_ebitda_reported", "adj_ebitda")]),
    ("overnight/02_kpi_panel_quarterly.csv", KP, [("revenue", "revenue_musd"), ("adj_ebitda_reported", "adj_ebitda_musd"), ("sbc_total_is", "sbc_musd"), ("fcf_reported", "fcf_musd"), ("buybacks", "buybacks_musd"),
                                                  ("shares_diluted_m", "diluted_wa_shares_m"), ("rsu_tax_withholding", "rsu_tax_withholding_musd"), ("cor_gaap", "cost_of_revenue_musd"), ("ops_gaap", "ops_support_musd"),
                                                  ("pd_gaap", "product_dev_musd"), ("sm_gaap", "sales_marketing_musd"), ("ga_gaap", "g_and_a_musd"), ("op_income", "operating_income_musd"), ("cfo", "cfo_musd"),
                                                  ("capex", "capex_musd"), ("net_income", "net_income_musd"), ("tax_provision", "income_tax_musd"), ("funds_held_on_behalf", "funds_held_for_clients_musd"),
                                                  ("unearned_fees_balance", "unearned_fees_musd"), ("cash_and_equivalents", "cash_and_equivalents_musd"), ("short_term_investments", "short_term_investments_musd")]),
    ("abnb_fcf_bridge.csv", FB, [("revenue", "revenue"), ("adj_ebitda_reported", "adj_ebitda"), ("interest_income", "interest_income"), ("interest_expense", "interest_expense"), ("tax_provision", "tax_provision"),
                                 ("other_income_expense", "other_income_expense"), ("change_unearned_fees", "change_unearned_fees"), ("cfo", "cfo"), ("capex", "capex"), ("fcf_reported", "fcf"),
                                 ("net_income", "net_income"), ("sbc_total_is", "sbc"), ("da", "da"), ("other_addbacks_total", "other_addbacks"), ("unearned_fees_balance", "unearned_fees_end"), ("funds_held_on_behalf", "funds_payable_end")]),
]
first_vintage = {(p["period"], p["line"]): p["value"] for p in PROV if p["source"] in ("letter_first_vintage", "xbrl_first_vintage")}
for name, df, pairs in MAPS:
    for q in P.index:
        if q not in df.index:
            continue
        for mine_col, their_col in pairs:
            if their_col not in df.columns:
                continue
            mv, tv = P.loc[q, mine_col], df.loc[q, their_col]
            if pd.isna(mv) or pd.isna(tv):
                continue
            tv = float(tv)
            if name == "abnb_fcf_bridge.csv" and their_col in ("interest_expense", "capex", "tax_provision"):
                tv = -tv          # that panel stores expense, tax and capex as negatives
            if name == "overnight/02_kpi_panel_quarterly.csv" and their_col == "capex_musd":
                tv = abs(tv)
            d = round(float(mv) - tv, 3)
            expl = ""
            if abs(d) > 1.0:
                if (q, mine_col) in first_vintage and abs(first_vintage[(q, mine_col)] - tv) <= 1.0:
                    expl = f"vintage: existing panel carries the first-reported value {tv:.1f}; latest filing restates it to {mv:.1f}"
                elif mine_col == "other_addbacks_total" and abs(tv - (float(mv) + (P.loc[q, "restr_recon"] or 0.0))) <= 1.5:
                    expl = "definition: existing panel folds restructuring charges into other add-backs; mine keeps restructuring separate (restr_recon)"
                elif mine_col == "sbc_total_is" and q[0] == "4" and abs(tv - round(tv, -1)) < 0.01:
                    expl = "CORRECTION: existing panel derived Q4 SBC as FY less 9M with a proxy-statement (DEF 14A) FY value rounded to $100M; the 10-K/letter value is used here"
                elif mine_col == "interest_expense" and tv == 0.0:
                    expl = "vintage: interest expense was folded into other income (expense) in the 2024-25 filings; the 2Q26 letter re-presents it separately"
                elif mine_col in ("cfo", "fcf_reported") and qorder(q) <= qorder("4Q22"):
                    expl = "vintage: 2020-2022 CFO/FCF re-presented in the 2022-23 filings (funds-related cash-flow layout); mine is the latest letter vintage, existing panel the first-reported"
                elif mine_col == "shares_diluted_m" and q[0] == "4":
                    expl = "Q4 weighted-average shares from the 4Q letter statement of operations"
                elif mine_col == "other_addbacks_total" and isinstance(P.loc[q, "restatement_notes"], str) and ("lodging" in P.loc[q, "restatement_notes"] or "acq" in P.loc[q, "restatement_notes"]):
                    expl = f"vintage: lodging-tax/acquisition add-backs re-presented in later letters ({P.loc[q, 'restatement_notes']})"
                elif q[0] == "4" and abs(d) < 1.5:
                    expl = "precision: existing panel pairs a later 10-K's FY value rounded to millions with a 9M value in thousands"
                elif mine_col == "interest_expense" and P.loc[q, "other_includes_interest_expense"] is True:
                    expl = "definition: interest expense not separately disclosed in the original filing"
                elif mine_col == "other_income_expense":
                    expl = "definition: mine excludes interest expense where disclosed (derived from pretax - OI - interest income + interest expense); existing panel uses the as-filed 'other' line"
                elif mine_col == "sbc_total_is" and abs(P.loc[q, "sbc_recon"] - tv) <= 1.0:
                    expl = "definition: existing panel uses the reconciliation add-back (excludes restructuring SBC); mine is the income-statement total"
                elif mine_col == "adj_ebitda_reported" and name == "abnb_quarterly_cost_stack_exsbc.csv":
                    expl = "existing panel value keyed from an earlier letter"
                elif mine_col == "buybacks":
                    expl = "definition: mine is shares repurchased and retired (XBRL, accrual); existing panel uses letter cash repurchases"
                elif mine_col == "change_unearned_fees":
                    expl = "vintage/definition: XBRL de-cumulated latest vintage vs letter cash-flow YTD as first reported"
                elif mine_col == "cfo":
                    expl = "vintage: CFO for 2021 quarters was restated in the 2022 filings (presentation change); mine is the latest vintage"
                else:
                    expl = "UNEXPLAINED (> $1M): reviewed in the note"
            rec.append({"quarter": q, "line": mine_col, "panel": name, "mine": round(float(mv), 3), "theirs": round(tv, 3), "diff": d, "explanation": expl})
R = pd.DataFrame(rec)
R.to_csv(OUT / "02_reconciliation.csv", index=False)

# =============================================================================================== 9. macro / cycle episodes
ST = pd.read_csv(ROOT / "data/processed/overnight/31a_mgmt_margin_statements.csv")
EPISODES = [
    ("E0_2019_investment_year", "2019 pre-IPO investment year: S&M and product headcount ramp, margin 5% -> -5%", "1Q19", "4Q19", "4Q18"),
    ("E1_2020_covid", "COVID demand shock: nights -67% in 2Q20, restructuring (May 2020 RIF, 25% of staff), marketing cut to near zero", "1Q20", "1Q21", "4Q19"),
    ("E2_2H22_deceleration_fx", "Post-reopening deceleration and USD strength: revenue growth 58% (2Q22) -> 24% (4Q22); ADR ex-FX flat", "2Q22", "1Q23", "1Q22"),
    ("E3_2023_adr_normalisation", "ADR normalisation year: reported ADR -1% to +3%, take-rate guide 'similar', margin held with cost efficiencies", "1Q23", "4Q23", "4Q22"),
    ("E4_2025_na_slowdown", "2025 North America slowdown and inbound shock: NA nights low-single digit, guide cut in May, brand marketing ramp continued", "1Q25", "4Q25", "4Q24"),
    ("E5_2026_reacceleration", "2026 reacceleration with AI spend and new-business investment (context for the 5 Nov card)", "1Q26", "2Q26", "4Q25"),
]
CUT_THEMES = {"fixed_cost_discipline", "headcount", "marketing", "support_cost", "ai_cost", "ai_productivity", "sbc", "fy_margin_guide", "margin_algorithm"}
erows = []
for eid, desc, q0, q1, pre in EPISODES:
    qs = [q for q in P.index if qorder(q0) <= qorder(q) <= qorder(q1)]
    for q in [pre] + qs:
        if q not in P.index:
            continue
        r = P.loc[q]
        e = {"episode": eid, "description": desc, "quarter": q, "role": "pre_shock_reference" if q == pre else "episode",
             "revenue_musd": r["revenue"], "revenue_yoy_pct": r["revenue_yoy_pct"], "nights_yoy_pct": r["nights_m_yoy_pct"], "gbv_yoy_pct": r["gbv_busd_yoy_pct"],
             "adr_yoy_pct": r["adr_usd_yoy_pct"], "adj_ebitda_margin_pct": r["adj_ebitda_margin_pct"], "adj_ebitda_margin_yoy_pp": r["adj_ebitda_margin_yoy_pp"]}
        for line in ("cor", "ops", "pd", "sm", "ga"):
            e[line + "_cash_yoy_pct"] = r[line + "_cash_yoy_pct"]
            e[line + "_gaap_yoy_pct"] = r[line + "_gaap_yoy_pct"]
            e[line + "_cash_pct_rev"] = r[line + "_cash_pct_rev"]
        e["sbc_yoy_pct"] = r["sbc_total_is_yoy_pct"]
        e["restr_gaap_musd"] = r["restr_gaap"]
        st = ST[(ST["print"] == q) & (ST["theme"].isin(CUT_THEMES))]
        e["mgmt_statement_ids"] = "|".join(st["statement_id"].astype(str))
        e["mgmt_said"] = " || ".join((st["cost_line"].astype(str) + ": " + st["quote"].astype(str).str.slice(0, 160)).tolist())
        erows.append(e)
E = pd.DataFrame(erows)
E.to_csv(OUT / "02_macro_cycle_episodes.csv", index=False)

# =============================================================================================== 10. manifest, log, figures
man = []
for p in sorted(RAW.glob("*")):
    url = {"424B4_2020-12-11_d81668d424b4.htm": "https://www.sec.gov/Archives/edgar/data/1559720/000119312520315318/d81668d424b4.htm",
           "10Q_1Q21_abnb-20210331.htm": "https://www.sec.gov/Archives/edgar/data/1559720/000162828021010389/abnb-20210331.htm",
           "10Q_2Q21_abnb-20210630.htm": "https://www.sec.gov/Archives/edgar/data/1559720/000162828021016979/abnb-20210630.htm"}.get(p.name, "")
    man.append({"file": f"data/raw/margin_build/02_financial_panel/{p.name}", "url": url, "retrieved_utc": "2026-09-14T04:50:00Z",
                "bytes": p.stat().st_size, "sha256": sha256(p), "licence": "SEC EDGAR public filing"})
pd.DataFrame(man).to_csv(ROOT / "data/manifests/margin_build/02_financial_panel.csv", index=False)

cov = P[["revenue", "adj_ebitda_reported", "sbc_ops", "da", "fcf_reported", "nights_m", "interest_expense", "change_funds_payable"]].notna().sum()
with open(OUT / "02_build_log.txt", "w", encoding="utf-8") as f:
    f.write("WS02 financial panel build log\n\nWarnings:\n")
    for w in WARNINGS:
        f.write(" - " + w + "\n")
    f.write(f"\nQuarters: {len(P)} ({P.index[0]} to {P.index[-1]})\nCoverage (non-null quarters):\n{cov.to_string()}\n")
    f.write(f"\nRebuild gap |max| 1Q21-2Q26: {P.loc[[q for q in P.index if qorder(q) >= qorder('1Q21')], 'rebuild_gap'].abs().max():.3f}\n")
    f.write(f"Rebuild gap |max| all: {P['rebuild_gap'].abs().max():.3f}\n")
    f.write("\nAnnual sum-of-quarters checks (|max| per line):\n")
    for c in [c for c in A.columns if c.startswith("soq_minus_annual__")]:
        f.write(f"  {c[18:]}: {A[c].abs().max():.3f}\n")

fig_ok = True
try:
    out = subprocess.run(["py", "-3.13", str(HERE / "figures.py")], capture_output=True, text=True, timeout=300)
    if out.returncode != 0:
        fig_ok = False
        print("figures.py failed (non-fatal):", out.stderr[-800:])
except Exception as ex:  # noqa
    fig_ok = False
    print("figures.py not run (non-fatal):", ex)

print(f"panel: {len(P)} quarters, {P['adj_ebitda_reported'].notna().sum()} with reported Adjusted EBITDA")
print(f"rebuild gap |max| 1Q21-2Q26 = {P.loc[[q for q in P.index if qorder(q) >= qorder('1Q21')], 'rebuild_gap'].abs().max():.3f}")
print(f"warnings: {len(WARNINGS)}; figures: {'ok' if fig_ok else 'skipped'}")
sys.exit(0)
