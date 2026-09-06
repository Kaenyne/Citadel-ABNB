"""Bridge Adjusted EBITDA to free cash flow, quarter by quarter, from the shareholder letters.

Inputs
  data/raw/letters/<Q>_*.htm            shareholder letters (8-K Ex. 99.1); abnb_exsbc_stack.ensure_letters() downloads them
  data/processed/abnb_quarterly_costlines.csv   revenue by quarter (used only to check the letter's current-quarter column)

From each letter (current quarter = last column of the quarterly tables):
  Adjusted EBITDA reconciliation  net income, provision for income taxes, other (income) expense, interest expense,
                                  interest income, D&A, SBC, other add-backs, Adjusted EBITDA
  Free Cash Flow reconciliation   net cash from operations, purchases of property and equipment, Free Cash Flow
  Balance sheet                   unearned fees and funds payable [prior year-end, quarter-end]; the change in unearned
                                  fees is quarter-end less the prior letter's quarter-end

Bridge (all $M):  Adjusted EBITDA + interest income - interest expense - provision for income taxes
                  - other (income) expense, net + change in unearned fees + other working capital and non-cash (residual)
                  = net cash from operations; less capex = Free Cash Flow.
The provision for income taxes is an accrual proxy for cash taxes; the deferred part (large in 2024 and 2025 after the
2023 valuation-allowance release) lands in the residual. Cash taxes paid per the 10-K are printed as a memo.
Checks: FCF = CFO - capex per the letter; net income + adjustments = Adjusted EBITDA per the reconciliation.

Output: data/processed/abnb_fcf_bridge.csv (quarters 1Q21 to 2Q26, TTM columns, FY2022 to FY2025 rows)
Run: python analysis/src/abnb_fcf_bridge.py
"""
import csv, glob, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from abnb_exsbc_stack import RAW, ROOT, TOK, ensure_letters, isnum, letter_text, pn  # noqa: E402

OUT = os.path.join(ROOT, "data", "processed", "abnb_fcf_bridge.csv")
# Cash taxes paid, 10-K supplemental cash flow disclosure (SEC XBRL IncomeTaxesPaid / IncomeTaxesPaidNet), $M. Memo only.
CASH_TAXES_PAID = {2021: 17, 2022: 68, 2023: 132, 2024: 350, 2025: 232}

LABELS = [  # (key, normalized word sequence that identifies the row label in the Adjusted EBITDA reconciliation)
    ("tax", ("provision", "for")), ("other", ("other", "income")), ("intexp", ("interest", "expense")),
    ("intinc", ("interest", "income")), ("da", ("depreciation",)), ("sbc", ("stockbased",)),
    ("ipo", ("stocksettlement",)), ("acq", ("acquisition",)), ("lodging", ("lodging",)), ("restr", ("restructuring",)),
    ("adj", ("adjusted", "ebitda"))]


def norm(tk):
    return re.sub(r"[^a-z]", "", tk.lower())


def groups(toks, start, ncols=None):
    """Maximal runs of numeric tokens from position start: list of (first_index, values). A footnote marker glued to
    a label ("(1)" or "1") makes a run one token too long; drop it."""
    out, i = [], start
    while i < len(toks):
        if isnum(toks[i]):
            j = i
            while j < len(toks) and isnum(toks[j]):
                j += 1
            vals = toks[i:j]
            if ncols and len(vals) == ncols + 1:  # footnote marker glued to the label before ("(1) 14,063 ...") or after ("... 1 Excludes")
                if re.match(r"^\(?\d\)?$", vals[0]):
                    vals = vals[1:]
                elif re.match(r"^\(?\d\)?$", vals[-1]):
                    vals = vals[:-1]
            out.append((i, [pn(v) for v in vals]))
            i = j
        else:
            i += 1
    return out


def find_label(toks, words, start):
    n = len(words)
    for i in range(start, len(toks) - n + 1):
        if all(norm(t).startswith(w) for t, w in zip(toks[i:i + n], words)):  # prefix: "Acquisition-related" is one token
            return i
    return None


def colmap(vals_by_col, lines, q, ncols):
    """Map table columns to quarters by matching the Revenue row to the costlines revenue; without a Revenue row
    (1Q21 and 2Q21 letters) only the last column is used, as the current quarter."""
    if vals_by_col is None:
        return {ncols - 1: q}
    rev_to_q = {round(v): qq for qq, v in lines.items()}
    return {i: rev_to_q[round(v)] for i, v in enumerate(vals_by_col) if round(v) in rev_to_q}


def parse_recon(t, q, lines):
    """Adjusted EBITDA reconciliation, all columns. Labels sit before their numbers in most letters, after them in the
    1Q25-style layout and split around them in the 4Q23 layout, so rows are matched by order: the k-th label after
    Net income belongs to the k-th numeric group after Net income. Returns {quarter: rows} or {} if the table does not
    parse (the 2Q24 letter runs cells together, e.g. "amortization292613131198161414")."""
    m = re.search(r"Adjusted EBITDA Reconciliation", t)
    seg = t[m.start():m.start() + 4500]
    scale = 1e-3 if re.search(r"\(in thousands", seg[:200]) else 1.0
    toks = [x.strip() for x in TOK.findall(seg)]
    ni = find_label(toks, ("net", "income"), 0)
    g = groups(toks, ni)
    ncols = len(g[0][1])
    g = [x for x in groups(toks, ni, ncols) if len(x[1]) == ncols]
    r = find_label(toks, ("revenue",), 0)
    revs = [v * scale for v in groups(toks, r, ncols)[0][1]] if r is not None and r < ni else None
    labels = []
    for key, words in LABELS:
        pos = find_label(toks, words, g[0][0] + ncols)
        if pos is not None:
            labels.append((pos, key))
    labels.sort()
    labels = labels[:[k for _, k in labels].index("adj") + 1]
    if len(g) < len(labels) + 1:
        return {}
    out = {}
    for i, qq in colmap(revs, lines, q, ncols).items():
        rows = {"ni": g[0][1][i] * scale, "letter": q}
        for (pos, key), (gi, vals) in zip(labels, g[1:]):
            rows[key] = vals[i] * scale
        for k in ("ipo", "acq", "lodging", "restr", "other", "tax", "intexp", "intinc", "da", "sbc"):
            rows.setdefault(k, 0.0)
        check = rows["ni"] + sum(rows[k] for k in ("tax", "other", "intexp", "intinc", "da", "sbc", "ipo", "acq", "lodging", "restr"))
        if abs(check - rows["adj"]) > 1.5:
            return {}
        out[qq] = rows
    return out


def parse_fcf(t, q, lines):
    """Free Cash Flow reconciliation, all columns: CFO, capex, FCF. Columns follow the Adjusted EBITDA reconciliation
    of the same letter; the table has its own Revenue row from 4Q22 on."""
    m = re.search(r"Free Cash Flow Reconciliation", t)
    seg = t[m.start():m.start() + 3000]
    scale = 1e-3 if re.search(r"\(in thousands", seg[:200]) else 1.0
    toks = [x.strip() for x in TOK.findall(seg)]
    lab = find_label(toks, ("net", "cash", "provided", "by"), 0)
    g = groups(toks, lab)
    ncols = len(g[0][1])
    g = [x for x in g if len(x[1]) == ncols][:3]
    r = find_label(toks, ("revenue",), 0)
    revs = [v * scale for v in groups(toks, r, ncols)[0][1]] if r is not None and r < lab else None
    out = {}
    for i, qq in colmap(revs, lines, q, ncols).items():
        cfo, capex, fcf = (x[1][i] * scale for x in g)
        if abs(cfo + capex - fcf) > 0.6:
            return {}
        out[qq] = {"cfo": cfo, "capex": capex, "fcf": fcf, "fcf_letter": q}
    return out


def parse_balance(t):
    m = re.search(r"Balance Sheets", t)
    scale = 1e-3 if re.search(r"\(in thousands", t[m.start():m.start() + 200]) else 1.0
    uf = re.search(r"Unearned fees\s+((?:\$?\s*[\d,]+\s+){2})Total current liabilities", t)
    fp = re.search(r"Funds payable and amounts payable to customers\s+((?:\$?\s*[\d,]+\s+){2})", t[m.start():])
    uf = [pn(x) * scale for x in uf.group(1).split()]
    fp = [pn(x) * scale for x in fp.group(1).split()]
    return {"uf_prior_ye": uf[0], "uf": uf[1], "fp_prior_ye": fp[0], "fp": fp[1]}


def qsort(q):
    return (int(q[2:]), int(q[0]))


def main():
    ensure_letters()
    lines = {r["quarter"]: float(r["revenue_musd"]) for r in csv.DictReader(open(os.path.join(ROOT, "data/processed/abnb_quarterly_costlines.csv")))}
    data, recon, fcf = {}, {}, {}
    for path in sorted(glob.glob(os.path.join(RAW, "*_*.htm")), key=lambda p: qsort(os.path.basename(p)[:4])):
        q = os.path.basename(path)[:4]
        t = letter_text(path)
        data[q] = parse_balance(t)
        if q == "4Q20":  # the 4Q20 tables end with full-year columns; only its balance sheet is needed
            continue
        # a quarter's own letter is preferred; a later letter fills in when the own letter's table does not parse (2Q24)
        for qq, rows in parse_recon(t, q, lines).items():
            if qq not in recon or qq == q:
                recon[qq] = rows
        for qq, rows in parse_fcf(t, q, lines).items():
            if qq not in fcf or qq == q:
                fcf[qq] = rows
    for q in data:
        if q == "4Q20":
            continue
        if q not in recon or q not in fcf:
            raise SystemExit(f"{q}: no parsable reconciliation ({q in recon}) or FCF table ({q in fcf})")
        data[q].update(recon[q]); data[q].update(fcf[q])
        if data[q]["letter"] != q:
            print(f"note: {q} reconciliation taken from the {data[q]['letter']} letter (own letter does not parse)")
        if data[q]["fcf_letter"] != q:
            print(f"note: {q} FCF table taken from the {data[q]['fcf_letter']} letter")

    qs = [q for q in sorted(data, key=qsort) if q != "4Q20"]
    rows = []
    for i, q in enumerate(qs):
        d, prev = data[q], data[qs[i - 1]] if i else data["4Q20"]
        rev = lines[q]
        d_uf = d["uf"] - prev["uf"]
        pre_wc = d["adj"] - d["intinc"] - d["intexp"] - d["tax"] - d["other"]  # intinc is negative in the reconciliation
        resid = d["cfo"] - pre_wc - d_uf
        r = {"period": q, "revenue": rev, "adj_ebitda": d["adj"], "interest_income": -d["intinc"], "interest_expense": -d["intexp"],
             "tax_provision": -d["tax"], "other_income_expense": -d["other"], "change_unearned_fees": d_uf,
             "other_wc_and_noncash_residual": resid, "cfo": d["cfo"], "capex": d["capex"], "fcf": d["fcf"],
             "fcf_check_gap": d["cfo"] + d["capex"] - d["fcf"], "source_letter": d["letter"], "net_income": d["ni"], "sbc": d["sbc"], "da": d["da"],
             "other_addbacks": d["acq"] + d["lodging"] + d["restr"] + d["ipo"], "unearned_fees_end": d["uf"],
             "funds_payable_end": d["fp"], "adj_ebitda_margin_pct": 100 * d["adj"] / rev, "fcf_margin_pct": 100 * d["fcf"] / rev}
        if i >= 3:
            w = rows[-3:] + [r]
            trev, tadj, tfcf = (sum(x[k] for x in w) for k in ("revenue", "adj_ebitda", "fcf"))
            r.update({"ttm_revenue": trev, "ttm_adj_ebitda": tadj, "ttm_fcf": tfcf, "ttm_adj_ebitda_margin_pct": 100 * tadj / trev,
                      "ttm_fcf_margin_pct": 100 * tfcf / trev, "ttm_fcf_to_adj_ebitda_pct": 100 * tfcf / tadj})
        rows.append(r)
    fy_rows = []
    for y in (2021, 2022, 2023, 2024, 2025):
        w = [r for r in rows if r["period"].endswith(str(y)[2:])]
        if len(w) != 4:
            continue
        f = {"period": f"FY{y}"}
        for k in ("revenue", "adj_ebitda", "interest_income", "interest_expense", "tax_provision", "other_income_expense", "change_unearned_fees",
                  "other_wc_and_noncash_residual", "cfo", "capex", "fcf", "fcf_check_gap", "net_income", "sbc", "da", "other_addbacks"):
            f[k] = sum(r[k] for r in w)
        f["unearned_fees_end"], f["funds_payable_end"] = w[-1]["unearned_fees_end"], w[-1]["funds_payable_end"]
        f["adj_ebitda_margin_pct"], f["fcf_margin_pct"] = 100 * f["adj_ebitda"] / f["revenue"], 100 * f["fcf"] / f["revenue"]
        f["cash_taxes_paid_10k"] = CASH_TAXES_PAID.get(y)
        fy_rows.append(f)
    cols = ["period", "revenue", "adj_ebitda", "interest_income", "interest_expense", "tax_provision", "other_income_expense", "change_unearned_fees",
            "other_wc_and_noncash_residual", "cfo", "capex", "fcf", "fcf_check_gap", "adj_ebitda_margin_pct", "fcf_margin_pct",
            "ttm_revenue", "ttm_adj_ebitda", "ttm_fcf", "ttm_adj_ebitda_margin_pct", "ttm_fcf_margin_pct", "ttm_fcf_to_adj_ebitda_pct",
            "net_income", "sbc", "da", "other_addbacks", "unearned_fees_end", "funds_payable_end", "cash_taxes_paid_10k", "source_letter"]
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows + fy_rows:
            w.writerow({k: (round(v, 1) if isinstance(v, float) else v) for k, v in r.items() if k in cols})
    print(f"wrote {len(rows)} quarters and {len(fy_rows)} fiscal years to {os.path.normpath(OUT)}")
    print("\nperiod | adj EBITDA | +int inc | -int exp | -tax | -other | +dUF | +resid | = CFO | capex | FCF | FCF chk | adj m% | FCF m% | TTM FCF m%")
    for r in rows + fy_rows:
        print(f"{r['period']:7s}| {r['adj_ebitda']:7.0f} | {r['interest_income']:6.0f} | {r['interest_expense']:6.0f} | {r['tax_provision']:6.0f} | "
              f"{r['other_income_expense']:6.0f} | {r['change_unearned_fees']:6.0f} | {r['other_wc_and_noncash_residual']:6.0f} | {r['cfo']:6.0f} | "
              f"{r['capex']:5.0f} | {r['fcf']:6.0f} | {r['fcf_check_gap']:4.1f} | {r['adj_ebitda_margin_pct']:5.1f} | {r['fcf_margin_pct']:5.1f} | "
              f"{r.get('ttm_fcf_margin_pct', float('nan')):5.1f}")
    print("\nFY bridge as % of revenue")
    for f in fy_rows:
        rv = f["revenue"]
        print(f"{f['period']}: adj {100*f['adj_ebitda']/rv:.1f} | int inc {100*f['interest_income']/rv:+.1f} | int exp {100*f['interest_expense']/rv:+.1f} | "
              f"tax {100*f['tax_provision']/rv:+.1f} | other {100*f['other_income_expense']/rv:+.1f} | dUF {100*f['change_unearned_fees']/rv:+.1f} | "
              f"resid {100*f['other_wc_and_noncash_residual']/rv:+.1f} | capex {100*f['capex']/rv:+.1f} | FCF {100*f['fcf']/rv:.1f} | "
              f"cash taxes paid {f['cash_taxes_paid_10k']} | SBC {f['sbc']:.0f}")


if __name__ == "__main__":
    sys.exit(main())
