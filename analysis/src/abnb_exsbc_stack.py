"""Build the ex-SBC (cash) cost stack per quarter and reconcile it to Adjusted EBITDA.

Inputs
  data/processed/abnb_quarterly_costlines.csv   GAAP lines incl. SBC (from abnb_costlines_from_xbrl.py)
  data/processed/abnb_quarterly_kpis_from_study.csv  nights, GBV, ADR from the earnings-call study; cross-check only
  data/raw/letters/<Q>_*.htm   shareholder letters (8-K Ex. 99.1); downloaded from EDGAR if missing

From each letter we parse (a) the SBC-by-function footnote under the income statement, (b) the Adjusted EBITDA
reconciliation (D&A, acquisition-related impacts, lodging-tax reserves, restructuring, IPO stock-settlement) and
(c) the quarter's nights, GBV and ADR from the "Business and Financial Performance" box and the quarterly summary
table. Letter KPIs are validated against the study CSV (nights and GBV equal, implied ADR = GBV / nights within
$0.50 of the letter ADR); the script stops if any quarter fails. The 1Q21 and 2Q21 letters have no SBC-by-function
footnote, so those two quarters come from the 10-Q footnotes (SBC_FALLBACK).
Cash cost per line = GAAP line minus that line's SBC.
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

# SBC by function for the two quarters whose letters carry no footnote, from the 10-Q notes ($M; 10-Q figures are in
# thousands). 1Q21: 10-Q accession 0001628280-21-010389 (ops 11,412; PD 143,715; S&M 25,901; G&A 48,457; restructuring (11);
# total 229,474). 2Q21: 10-Q accession 0001628280-21-016979 (ops 14,236; PD 143,812; S&M 24,064; G&A 50,728; restructuring 23;
# total 232,863). Totals exclude the restructuring line, matching the letters' footnote convention.
SBC_FALLBACK = {
    "1Q21": {"sbc_ops": 11.4, "sbc_pd": 143.7, "sbc_sm": 25.9, "sbc_ga": 48.5, "sbc_total_fn": 229.5},
    "2Q21": {"sbc_ops": 14.2, "sbc_pd": 143.8, "sbc_sm": 24.1, "sbc_ga": 50.7, "sbc_total_fn": 232.8}}

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


def parse_kpis(t):
    """Current-quarter nights (M), GBV ($B) and ADR ($) from a letter. Nights and GBV come from the KPI box on the
    "Business and Financial Performance" page ("148.3M $27.2B Nights and Seats Booked Gross Booking Value"; the first
    match is the quarter, a second match in Q4 letters is the full year). ADR is the last value of the quarterly summary
    row "Gross Booking Value per Night ... (or ADR)", whose columns end with the current quarter (the 3Q25 and 4Q25
    letters break the label after "per")."""
    box = re.search(r"(\d+\.\d)\s*M\s+\$\s*(\d+\.\d)\s*B\s+Nights (?:and|&) (?:Experiences|Seats) Booked\s+Gross Booking Value", t)
    adr = re.search(r"Gross Booking Value per(?: Night)?[^$]{0,80}((?:\$\s*\d{2,3}\.\d{2}\s*){2,})", t)
    if not box or not adr:
        return None
    return {"nights_m": float(box.group(1)), "gbv_busd": float(box.group(2)),
            "adr": float(re.findall(r"\d{2,3}\.\d{2}", adr.group(1))[-1])}


def main():
    ensure_letters()
    lines = {r["quarter"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data/processed/abnb_quarterly_costlines.csv")))}
    kpis = {r["quarter"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data/processed/abnb_quarterly_kpis_from_study.csv")))}
    rev_to_q = {round(float(r["revenue_musd"])): q for q, r in lines.items()}

    recon, sbcf, lk = {}, {}, {}
    for path in sorted(glob.glob(os.path.join(RAW, "*_*.htm"))):
        q = os.path.basename(path)[:4]
        t = letter_text(path)
        # (c) nights, GBV, ADR for the quarter, validated against the study CSV
        k = parse_kpis(t)
        if k and q in kpis:
            st = kpis[q]
            implied = 1000 * k["gbv_busd"] / k["nights_m"]
            ok = (abs(k["nights_m"] - float(st["nights_m"])) < 0.05 and abs(k["gbv_busd"] - float(st["gbv_b"])) < 0.05
                  and abs(implied - k["adr"]) <= 0.50 and abs(k["adr"] - float(st["adr"])) < 0.01)
            if not ok:
                raise SystemExit(f"{q}: letter KPIs {k} (implied ADR {implied:.2f}) do not match the study CSV {dict(st)}")
            lk[q] = k
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

    for q, fb in SBC_FALLBACK.items():
        sbcf.setdefault(q, dict(fb))
    missing = [q for q in kpis if q not in lk]
    if missing:
        raise SystemExit(f"letter KPI parse failed for {missing}; fix parse_kpis or fall back to the study CSV")
    print(f"letter KPIs parsed and validated for {len(lk)} quarters (nights, GBV, ADR match the study CSV; implied ADR within $0.50)")

    out = []
    for q, x in lines.items():
        if q not in recon or q not in sbcf:
            continue
        g = lambda k: float(x[k]) if x[k] not in ("", None) else 0.0
        r, s, k = recon[q], sbcf[q], lk.get(q, {})
        rev = g("revenue_musd")
        cash = {"cor": g("cost_of_revenue_musd"), "ops": g("operations_and_support_musd") - (s["sbc_ops"] or 0),
                "pd": g("product_development_musd") - (s["sbc_pd"] or 0), "sm": g("sales_and_marketing_musd") - (s["sbc_sm"] or 0),
                "ga": g("general_and_administrative_musd") - (s["sbc_ga"] or 0), "restr": g("restructuring_musd")}
        da = r.get("da", 0.0)
        other = (r.get("acq") or r.get("acq2") or 0.0) + (r.get("lodging") or r.get("lodging2") or 0.0) + (r.get("restr") or 0.0) + (r.get("ipo") or 0.0)
        # Adj. EBITDA implied by the stack: revenue minus cash costs, adding back D&A (inside the lines) and other add-backs
        implied = rev - sum(cash.values()) + da + other
        adj = float(x["adjusted_ebitda_musd"]) if x["adjusted_ebitda_musd"] else r.get("adj")
        row = {"quarter": q, "revenue_musd": rev, "nights_m": k.get("nights_m"), "gbv_busd": k.get("gbv_busd"), "adr": k.get("adr"),
               "take_rate_pct": round(rev / (1000 * k["gbv_busd"]) * 100, 1) if k else None,
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
