"""Build the ex-SBC (cash) cost stack per quarter and reconcile it to Adjusted EBITDA.

Inputs
  data/processed/abnb_quarterly_costlines.csv   GAAP lines incl. SBC (from abnb_costlines_from_xbrl.py)
  data/processed/abnb_quarterly_kpis_from_study.csv  nights, GBV, ADR, take rate (from the earnings-call study)
  data/raw/letters/<Q>_*.htm   shareholder letters (8-K Ex. 99.1); downloaded from EDGAR if missing

From each letter we parse (a) the SBC-by-function footnote under the income statement and
(b) the Adjusted EBITDA reconciliation (D&A, acquisition-related impacts, lodging-tax reserves,
restructuring, IPO stock-settlement). Cash cost per line = GAAP line minus that line's SBC.
Identity checked per quarter: revenue - total costs + SBC + D&A + other add-backs = Adjusted EBITDA.

Output: data/processed/abnb_quarterly_cost_stack_exsbc.csv
Run: python analysis/src/abnb_exsbc_stack.py
"""
import csv, glob, html, json, os, re, sys, time, urllib.request

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
RAW = os.path.join(ROOT, "data", "raw", "letters")
UA = {"User-Agent": os.environ.get("SEC_USER_AGENT", "Citadel-ABNB student research ksurapaneni@ufl.edu")}

# Earnings-day 8-K accession numbers (Ex. 99.1 is the shareholder letter).
LETTERS = {
    "4Q20": "0001193125-21-056952", "1Q21": "0001193125-21-160458", "2Q21": "0001193125-21-244643",
    "3Q21": "0001193125-21-320113", "4Q21": "0001193125-22-043371", "1Q22": "0001193125-22-138654",
    "2Q22": "0001193125-22-210001", "3Q22": "0001193125-22-274904", "4Q22": "0001193125-23-039008",
    "1Q23": "0001193125-23-139392", "2Q23": "0001193125-23-202832", "3Q23": "0001193125-23-268164",
    "4Q23": "0001193125-24-033706", "1Q24": "0001193125-24-134183", "2Q24": "0001193125-24-194849",
    "3Q24": "0001193125-24-253103", "4Q24": "0001193125-25-026054", "1Q25": "0001193125-25-109934",
    "2Q25": "0001193125-25-174438", "3Q25": "0001193125-25-269432", "4Q25": "0001193125-26-048670",
    "1Q26": "0001193125-26-211816", "2Q26": "0001193125-26-337928"}

TOK = re.compile(r"\(\s*[\d,]+(?:\.\d+)?\s*\)|\$?\s*[\d,]+(?:\.\d+)?|—|-|[A-Za-z][A-Za-z()’',./-]*")


def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()


def ensure_letters():
    os.makedirs(RAW, exist_ok=True)
    for q, acc in LETTERS.items():
        if glob.glob(os.path.join(RAW, f"{q}_*.htm")):
            continue
        nd = acc.replace("-", "")
        idx = json.loads(fetch(f"https://www.sec.gov/Archives/edgar/data/1559720/{nd}/index.json"))
        name = next(i["name"] for i in idx["directory"]["item"] if re.search(r"ex99", i["name"], re.I))
        open(os.path.join(RAW, f"{q}_{name}"), "wb").write(fetch(f"https://www.sec.gov/Archives/edgar/data/1559720/{nd}/{name}"))
        time.sleep(0.2)


def letter_text(path):
    raw = open(path, "rb").read().decode("utf-8", "ignore")
    txt = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(txt))


def pn(s):
    s = s.strip()
    if s in ("-", "—"):
        return 0.0
    v = float(re.sub(r"[^\d.]", "", s))
    return -v if "(" in s else v


def isnum(tk):
    return bool(re.match(r"^(\(\s*[\d,.]+\s*\)|\$?\s*[\d,.]+|—|-)$", tk))


def find_row(toks, words, scale, ncols=None):
    n = len(words)
    for i in range(len(toks) - n):
        if [w.rstrip(",").lower() for w in toks[i:i + n]] == [w.rstrip(",").lower() for w in words]:
            j = i + n
            while j < len(toks) and re.match(r"^\(\d\)$", toks[j]):
                j += 1
            vals = []
            while j < len(toks) and isnum(toks[j]):
                vals.append(pn(toks[j]) * scale)
                j += 1
            if vals and (ncols is None or len(vals) == ncols):
                return vals
    return None


def main():
    ensure_letters()
    lines = {r["quarter"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data/processed/abnb_quarterly_costlines.csv")))}
    kpis = {r["quarter"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data/processed/abnb_quarterly_kpis_from_study.csv")))}
    rev_to_q = {round(float(r["revenue_musd"])): q for q, r in lines.items()}

    recon, sbcf = {}, {}
    for path in sorted(glob.glob(os.path.join(RAW, "*_*.htm"))):
        q = os.path.basename(path)[:4]
        t = letter_text(path)
        # (a) reconciliation table: columns are quarters, identified by matching the Revenue row
        m = re.search(r"Adjusted EBITDA Reconciliation", t)
        if m:
            seg = t[m.start():m.start() + 3500]
            scale = 1e-3 if re.search(r"\(in thousands", seg[:200]) else 1.0
            toks = [x.strip() for x in TOK.findall(seg)]
            revs = find_row(toks, ["Revenue"], scale)
            if revs:
                n = len(revs)
                rows = {"da": ["Depreciation", "and", "amortization"], "acq": ["Acquisition-related", "impacts"],
                        "acq2": ["Acquisition-", "related", "impacts"], "lodging": ["Net", "changes", "in", "lodging", "tax", "reserves"],
                        "lodging2": ["Lodging", "taxes,", "host", "withholding", "taxes,"], "restr": ["Restructuring", "charges"],
                        "ipo": ["Stock-settlement", "obligations"], "adj": ["Adjusted", "EBITDA"]}
                data = {k: find_row(toks, w, scale, n) for k, w in rows.items()}
                for i, rv in enumerate(revs):
                    qq = rev_to_q.get(round(rv))
                    if qq:
                        d = recon.setdefault(qq, {})
                        for k, vals in data.items():
                            if vals:
                                d[k] = vals[i]
        # (b) SBC by function footnote; the phrase also appears as a footnote marker inside the income
        # statement, so take the occurrence that is followed by the function rows. Column = the one whose
        # total equals the quarter's GAAP SBC (Q1 letters have 2 columns, others 4, plus a stray page number).
        if q in lines and lines[q]["stock_based_comp_total_musd"]:
            target = float(lines[q]["stock_based_comp_total_musd"])
            for mm in re.finditer(r"stock-based compensation expense as follows \(in (thousands|millions)\)", t, re.I):
                scale = 1e-3 if mm.group(1) == "thousands" else 1.0
                toks = [x.strip() for x in TOK.findall(t[mm.end():mm.end() + 3000])]
                # locate every "Stock-based compensation expense <numbers>" total row and read the four function rows
                # in the 60 tokens just before it (the income statement above uses the same labels with footnote marks)
                found = False
                for i in range(len(toks) - 3):
                    if [w.lower() for w in toks[i:i + 3]] != ["stock-based", "compensation", "expense"] or i + 3 >= len(toks) or not isnum(toks[i + 3]):
                        continue
                    sl = toks[max(0, i - 60):i + 12]
                    fn = {k: find_row(sl, w, scale) for k, w in [("sbc_ops", ["Operations", "and", "support"]), ("sbc_pd", ["Product", "development"]),
                                                                 ("sbc_sm", ["Sales", "and", "marketing"]), ("sbc_ga", ["General", "and", "administrative"])]}
                    tot = find_row(sl, ["Stock-based", "compensation", "expense"], scale)
                    if not tot or any(v is None for v in fn.values()):
                        continue
                    ncols = min(len(v) for v in fn.values())
                    tot = tot[:ncols]
                    idx = min(range(ncols), key=lambda i2: abs(tot[i2] - target))
                    # Q4 quarters derived from XBRL (FY less 9M) differ from the letter's quarterly SBC by up to ~10%
                    if abs(tot[idx] - target) > 0.15 * target:
                        continue
                    sbcf[q] = {"sbc_total_fn": round(tot[idx], 1), **{k: round(v[idx], 1) for k, v in fn.items()}}
                    found = True
                    break
                if found:
                    break

    out = []
    for q, x in lines.items():
        if q not in recon or q not in sbcf:
            continue
        g = lambda k: float(x[k]) if x[k] not in ("", None) else 0.0
        r, s, k = recon[q], sbcf[q], kpis.get(q, {})
        rev = g("revenue_musd")
        cash = {"cor": g("cost_of_revenue_musd"), "ops": g("operations_and_support_musd") - (s["sbc_ops"] or 0),
                "pd": g("product_development_musd") - (s["sbc_pd"] or 0), "sm": g("sales_and_marketing_musd") - (s["sbc_sm"] or 0),
                "ga": g("general_and_administrative_musd") - (s["sbc_ga"] or 0), "restr": g("restructuring_musd")}
        da = r.get("da", 0.0)
        other = (r.get("acq") or r.get("acq2") or 0.0) + (r.get("lodging") or r.get("lodging2") or 0.0) + (r.get("restr") or 0.0) + (r.get("ipo") or 0.0)
        # Adj. EBITDA implied by the stack: revenue minus cash costs, adding back D&A (inside the lines) and other add-backs
        implied = rev - sum(cash.values()) + da + other
        adj = float(x["adjusted_ebitda_musd"]) if x["adjusted_ebitda_musd"] else r.get("adj")
        row = {"quarter": q, "revenue_musd": rev, "nights_m": k.get("nights_m"), "gbv_busd": k.get("gbv_b"), "adr": k.get("adr"),
               "take_rate_pct": k.get("take_rate_pct"),
               "cor_cash": round(cash["cor"], 1), "ops_cash": round(cash["ops"], 1), "pd_cash": round(cash["pd"], 1),
               "sm_cash": round(cash["sm"], 1), "ga_cash": round(cash["ga"], 1), "restr": round(cash["restr"], 1),
               "sbc_ops": s["sbc_ops"], "sbc_pd": s["sbc_pd"], "sbc_sm": s["sbc_sm"], "sbc_ga": s["sbc_ga"], "sbc_total": g("stock_based_comp_total_musd"), "sbc_total_letter": s["sbc_total_fn"],
               "da": round(da, 1), "other_addbacks": round(other, 1), "adj_ebitda": adj,
               "adj_ebitda_implied": round(implied, 1), "identity_gap": round(implied - adj, 1)}
        for key in ("cor", "ops", "pd", "sm", "ga"):
            row[f"{key}_cash_pct_rev"] = round(100 * cash[key] / rev, 1)
        row["adj_ebitda_margin_pct"] = round(100 * adj / rev, 1)
        if k.get("nights_m"):
            nights = float(k["nights_m"])
            for key in ("cor", "ops", "pd", "sm", "ga"):
                row[f"{key}_cash_per_night"] = round(cash[key] / nights, 2)
            row["rev_per_night"] = round(rev / nights, 2)
        out.append(row)
    path = os.path.join(ROOT, "data", "processed", "abnb_quarterly_cost_stack_exsbc.csv")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(f"wrote {len(out)} quarters to {os.path.normpath(path)}")
    print("q | cor ops pd sm ga (cash % rev) | SBC% | adj margin | identity gap $M")
    for r in out:
        print(r["quarter"], "|", r["cor_cash_pct_rev"], r["ops_cash_pct_rev"], r["pd_cash_pct_rev"], r["sm_cash_pct_rev"], r["ga_cash_pct_rev"],
              "|", round(100 * r["sbc_total"] / r["revenue_musd"], 1), "|", r["adj_ebitda_margin_pct"], "|", r["identity_gap"])


if __name__ == "__main__":
    sys.exit(main())
