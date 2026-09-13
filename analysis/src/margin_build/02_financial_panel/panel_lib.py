"""Parsers for the WS02 financial panel (margin build, 13-14 Sep 2026).

Sources handled here:
  * SEC companyfacts JSON (data/raw/xbrl/ABNB_companyfacts.json): quarterly de-cumulation, latest-vintage selection.
  * Shareholder letters (data/raw/letters/<Q>_*.htm, 8-K Ex. 99.1, 4Q20-2Q26): Adjusted EBITDA reconciliation
    (6 to 13 quarter columns per letter, so every quarter has several vintages), Free Cash Flow reconciliation,
    condensed statement of operations (current and prior-year quarter), SBC-by-function footnote, YTD cash-flow lines,
    quarterly KPI summary table (nights, GBV, ADR).
  * 424B4 prospectus (data/raw/margin_build/02_financial_panel/424B4_*.htm): quarterly income statement, SBC by
    function, Adjusted EBITDA and FCF reconciliations for 1Q18-3Q20; annual 2015-2019.
  * 10-K text (data/raw/filings/txt/abnb_10k_FY*.txt): annual income statement, SBC note, Adjusted EBITDA and FCF
    reconciliations, revenue by geography, headcount, hosting commitment.
  * 10-Q 1Q21 / 2Q21 (data/raw/margin_build/02_financial_panel/10Q_*.htm): SBC by function (no letter footnote then).

The letters are PDF-to-HTML conversions: numbers always come out in row order, but labels are sometimes emitted
before or after the block of numbers (1Q25, 4Q24 letters), and footnote markers ("1", "(1)") are glued to the
stock-based compensation row. Table parsing therefore reads the numbers as one sequential block, checks that the count
equals rows x columns, and validates every column with the accounting identity (net income + adjustments = Adjusted
EBITDA; CFO + capex = FCF). A table that fails validation is dropped with a warning; every quarter is covered by
several letters, so coverage is unaffected.

Every parser returns plain dicts keyed by quarter label ("1Q19") or fiscal year (2019); values are USD millions.
"""
import datetime as dt
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

MONTH_Q = {"Mar": 1, "Jun": 2, "Sep": 3, "Sept": 3, "Dec": 4}
NUM_RE = r"\(\s*[\d,]+(?:\.\d+)?\s*\)|[\d,]*\d(?:\.\d+)?"
TOK = re.compile(NUM_RE + r"|-|[A-Za-z][A-Za-z()’',./-]*")
WARNINGS = []


def warn(msg):
    WARNINGS.append(msg)
    print("WARN:", msg)


def qlabel(y, q):
    return f"{q}Q{str(y)[2:]}"


def qorder(q):
    return int(q[2:4]) * 4 + int(q[0])


def prev_q(q):
    y, n = 2000 + int(q[2:4]), int(q[0])
    return qlabel(y - 1, 4) if n == 1 else qlabel(y, n - 1)


def q_of_end(end):
    d = dt.date.fromisoformat(end)
    return qlabel(d.year, (d.month - 1) // 3 + 1)


# --------------------------------------------------------------------------------------------- text utilities
def clean_html(path):
    raw = Path(path).read_text(encoding="utf-8", errors="ignore")
    t = re.sub(r"<[^>]+>", " ", raw)
    t = html.unescape(t)
    t = t.replace("—", "-").replace("–", "-").replace("�", "-").replace("−", "-")
    t = re.sub(r"(\d),\s+(\d{3})", r"\1,\2", t)          # "$314, 024" in the 4Q20 letter
    t = re.sub(r"\)\s*\$", ") $", t)
    t = re.sub(r"(\d)\$", r"\1 $", t)                    # "$1,509$2,104" (2Q24 letter)
    t = re.sub(r"(\d)([A-Z][a-z])", r"\1 \2", t)         # "2022Jun 30"
    t = re.sub(r"\)(\d)", r") \1", t)
    t = re.sub(r"([A-Za-z])(\d)", r"\1 \2", t)           # "Mar31" (1Q25 letter)
    t = re.sub(r"\s+", " ", t)
    return t


def clean_txt(path):
    t = Path(path).read_text(encoding="utf-8", errors="ignore")
    t = t.replace("—", "-").replace("–", "-").replace("�", "-")
    return re.sub(r"\s+", " ", t)


def pnum(s):
    s = s.strip()
    if s == "-":
        return 0.0
    v = float(re.sub(r"[^\d.]", "", s))
    return -v if "(" in s else v


def isnum(tk):
    return bool(re.fullmatch(r"(\(\s*[\d,]+(?:\.\d+)?\s*\)|[\d,]*\d(?:\.\d+)?|-)", tk))


def toks(seg):
    return [x.strip() for x in TOK.findall(seg)]


def strip_markers(seg):
    """Remove footnote markers glued to table labels: 'expense 1 14,063', 'expense (1) Acquisition',
    'Operations and support (1) 127,789', 'compensation expense (1) 39,566'."""
    seg = re.sub(r"(expense)\s+\(?1\)?\s+(?=[\d($-])", r"\1 ", seg)
    seg = re.sub(r"(\d)\s+expense\s+\(1\)", r"\1 expense", seg)
    seg = re.sub(r"(support|development|marketing|administrative|charges|expense)\s+\(\d\)\s+", r"\1 ", seg)
    seg = re.sub(r"\(1\) (Excludes|Includes)", r"", seg)
    return seg


def numbers_in(seg):
    return [x for x in toks(seg) if isnum(x)]


# --------------------------------------------------------------------------------------------- XBRL
class Facts:
    def __init__(self, path):
        self.us = json.load(open(path))["facts"]["us-gaap"]

    def obs(self, concept, unit=None):
        c = self.us.get(concept)
        if not c:
            return []
        if unit is None:
            unit = list(c["units"].keys())[0]
        return c["units"][unit]

    def duration_series(self, concept, unit=None):
        latest, first = {}, {}
        for f in self.obs(concept, unit):
            if "start" not in f:
                continue
            k = (f["start"], f["end"])
            if k not in latest or f["filed"] > latest[k][1]:
                latest[k] = (f["val"], f["filed"], f["form"])
            if k not in first or f["filed"] < first[k][1]:
                first[k] = (f["val"], f["filed"], f["form"])
        return latest, first

    def instant_series(self, concept, unit=None):
        latest = {}
        for f in self.obs(concept, unit):
            if "start" in f:
                continue
            k = f["end"]
            if k not in latest or f["filed"] > latest[k][1]:
                latest[k] = (f["val"], f["filed"], f["form"])
        return latest

    def quarterly(self, concept, unit=None, scale=1e-6):
        """Discrete quarters: direct 3-month facts first, else YTD differences (Q4 = FY - 9M).
        Returns {q: (value, detail, first_value, first_filed)}."""
        latest, first = self.duration_series(concept, unit)
        out = {}
        years = sorted({int(e[:4]) for _, e in latest})
        for y in years:
            bounds = {1: (f"{y}-01-01", f"{y}-03-31"), 2: (f"{y}-04-01", f"{y}-06-30"),
                      3: (f"{y}-07-01", f"{y}-09-30"), 4: (f"{y}-10-01", f"{y}-12-31")}
            ytd = {1: (f"{y}-01-01", f"{y}-03-31"), 2: (f"{y}-01-01", f"{y}-06-30"),
                   3: (f"{y}-01-01", f"{y}-09-30"), 4: (f"{y}-01-01", f"{y}-12-31")}
            for q in (1, 2, 3, 4):
                if bounds[q] in latest:
                    v, filed, form = latest[bounds[q]]
                    fv = first.get(bounds[q], (v, filed, form))
                    out[qlabel(y, q)] = (v * scale, f"xbrl:{concept} 3M to {bounds[q][1]} {form} filed {filed}",
                                         fv[0] * scale, fv[1])
                elif q > 1 and ytd[q] in latest and ytd[q - 1] in latest:
                    a, b = latest[ytd[q]], latest[ytd[q - 1]]
                    fa, fb = first.get(ytd[q], a), first.get(ytd[q - 1], b)
                    out[qlabel(y, q)] = ((a[0] - b[0]) * scale,
                                         f"xbrl:{concept} YTD {ytd[q][1]} ({a[2]} filed {a[1]}) less YTD {ytd[q-1][1]} ({b[2]} filed {b[1]})",
                                         (fa[0] - fb[0]) * scale, max(fa[1], fb[1]))
        return out

    def ytd(self, concept, unit=None, scale=1e-6):
        """Year-to-date values keyed by the quarter they end in (cash-flow statement lines)."""
        latest, first = self.duration_series(concept, unit)
        out = {}
        for (s, e), (v, filed, form) in latest.items():
            if s.endswith("-01-01") and s[:4] == e[:4] and e[5:] in ("03-31", "06-30", "09-30", "12-31"):
                out[q_of_end(e)] = (v * scale, f"xbrl:{concept} YTD to {e} {form} filed {filed}")
        return out

    def annual(self, concept, unit=None, scale=1e-6):
        latest, first = self.duration_series(concept, unit)
        out = {}
        for (s, e), (v, filed, form) in latest.items():
            if s.endswith("-01-01") and e.endswith("-12-31") and s[:4] == e[:4]:
                fv = first[(s, e)]
                out[int(e[:4])] = (v * scale, f"xbrl:{concept} FY{e[:4]} {form} filed {filed}", fv[0] * scale, fv[1])
        return out

    def instants(self, concept, unit=None, scale=1e-6):
        out = {}
        for end, (v, filed, form) in self.instant_series(concept, unit).items():
            if end[5:] in ("03-31", "06-30", "09-30", "12-31"):
                out[q_of_end(end)] = (v * scale, f"xbrl:{concept} as of {end} {form} filed {filed}")
        return out


# --------------------------------------------------------------------------------------------- generic tables
def parse_header_columns(head, letter_q=None):
    """Column labels from a 'Three Months Ended ...' header: quarter labels plus 'FY2019'-style labels for
    full-year columns. If the years are missing (1Q25 letter), the months are the run ending at letter_q."""
    months = re.findall(r"\b(Mar|Jun|Sept|Sep|Dec)\b", head)
    years = [int(y) for y in re.findall(r"\b(20\d\d)\b", head)]
    cols = []
    if months and len(years) >= len(months):
        for mth, y in zip(months, years[:len(months)]):
            cols.append(qlabel(y, MONTH_Q[mth]))
        for y in years[len(months):]:
            cols.append(f"FY{y}")
    elif months and letter_q:
        q = letter_q
        for _ in months:
            cols.append(q)
            q = prev_q(q)
        cols = cols[::-1]
        exp = [MONTH_Q[m] for m in months]
        if [int(c[0]) for c in cols] != exp:
            return []
    return cols


def parse_table(text, title_re, rows, anchor_re, stop_re, letter_q=None, window=5000, scale=None, allow_short=()):
    """Sequential-block table parser. Returns (cols, {key: [values]}, method) or None.
    rows: [(key, label_regex)] in canonical order; only labels found in the segment count as present.
    Method 'block': all numbers between the anchor and stop_re, count == n_rows * n_cols, assigned in label order.
    Method 'rows': per-row (numbers after each label), used when the block count does not fit."""
    m = re.search(title_re, text)
    if not m:
        return None
    seg = text[m.start():m.start() + window]
    if scale is None:
        scale = 1e-3 if re.search(r"in thousands", seg[:400]) else 1.0
    seg = strip_markers(seg)
    a = re.search(anchor_re, seg)
    if not a:
        return None
    head = seg[:a.start()]
    cols = parse_header_columns(head, letter_q)
    if not cols:
        return None
    n = len(cols)
    body = seg[a.start():]
    st = re.search(stop_re, body)
    body = body[:st.start()] if st else body
    body = re.sub(r"\(?\d+\)?\s*%", " ", body)               # margin rows ("6%", "(16)%") carry no table values
    present = []
    for key, rx in rows:
        mm = re.search(rx, body)
        if mm:
            present.append((mm.start(), key))
    present.sort()
    keys = [k for _, k in present]
    nums = numbers_in(body)
    if len(nums) == n * len(keys):
        out = {k: [pnum(v) * scale for v in nums[i * n:(i + 1) * n]] for i, k in enumerate(keys)}
        return cols, out, "block"
    # per-row fallback
    out = {}
    for i, (pos, key) in enumerate(present):
        nxt = present[i + 1][0] if i + 1 < len(present) else len(body)
        vals = numbers_in(body[pos:nxt])
        if len(vals) >= n:
            out[key] = [pnum(v) * scale for v in vals[:n]]
        elif key in allow_short or key in ("restr", "ipo", "acq"):
            out[key] = None                      # dashes collapsed by the PDF conversion; column identity decides
        else:
            return None
    return cols, out, "rows"


RECON_ROWS = [("revenue", r"\bRevenue\b"), ("net_income", r"Net (?:income|loss)"), ("tax", r"Provision for"),
              ("other", r"Other \(income\)|Other (?:expense|income)"), ("int_exp", r"Interest expense"),
              ("int_inc", r"Interest income"), ("da", r"Depreciation"), ("sbc", r"Stock-based"),
              ("ipo", r"Stock-settlement"), ("acq", r"Acquisition"), ("lodging", r"[Ll]odging"),
              ("restr", r"Restructuring"), ("adj_ebitda", r"Adjusted EBITDA")]
RECON_ADJ = ("tax", "other", "int_exp", "int_inc", "da", "sbc", "ipo", "acq", "lodging", "restr")


def recon_identity_ok(cols, rows, tol_m=3.0, tol_k=0.01):
    bad = []
    for i, c in enumerate(cols):
        s = rows["net_income"][i] + sum(rows[k][i] for k in RECON_ADJ if rows.get(k))
        gap = s - rows["adj_ebitda"][i]
        tol = tol_k if abs(rows["adj_ebitda"][i]) != round(abs(rows["adj_ebitda"][i])) else tol_m
        if abs(gap) > tol:
            bad.append((c, round(gap, 3)))
    return bad


def letter_recon(text, letter_q):
    r = parse_table(text, r"Adjusted EBITDA Reconciliation", RECON_ROWS, r"\bRevenue\b|Net (?:income|loss)",
                    r"[Mm]argin|Excludes stock-based|The following is a reconciliation", letter_q)
    if not r:
        return None
    cols, rows, method = r
    if "adj_ebitda" not in rows or "net_income" not in rows:
        return None
    bad = recon_identity_ok(cols, rows)
    return cols, rows, method, bad


FCF_ROWS = [("revenue", r"\bRevenue\b"), ("ttm_revenue", r"TTM Revenue"), ("cfo", r"Net cash provided"),
            ("capex", r"Purchases of property"), ("fcf", r"Free Cash Flow|FCF")]


def letter_fcf(text, letter_q):
    r = parse_table(text, r"Free Cash Flow Reconciliation", FCF_ROWS, r"\bRevenue\b|Net cash provided",
                    r"[Mm]argin|Other cash flow components|TTM Net cash|as a percentage", letter_q, window=3000,
                    allow_short=("ttm_revenue",))
    if not r:
        return None
    cols, rows, method = r
    if not all(k in rows and rows[k] for k in ("cfo", "capex", "fcf")):
        return None
    bad = [(c, round(rows["cfo"][i] + rows["capex"][i] - rows["fcf"][i], 3)) for i, c in enumerate(cols)
           if abs(rows["cfo"][i] + rows["capex"][i] - rows["fcf"][i]) > (0.01 if abs(rows["fcf"][i]) != round(abs(rows["fcf"][i])) else 1.5)]
    return cols, rows, method, bad


# --------------------------------------------------------------------------------------------- statement of operations
IS_ROWS = [("revenue", r"Revenue"), ("cor", r"Cost of revenue"), ("ops", r"Operations and support"),
           ("pd", r"Product development"), ("sm", r"Sales and marketing"), ("ga", r"General and administrative"),
           ("restr", r"Restructuring charges"), ("total_costs", r"Total costs and expenses"),
           ("op_income", r"(?:Income|Loss|Income \(loss\)) from operations"), ("int_inc", r"Interest income"),
           ("int_exp", r"Interest expense"), ("other", r"Other (?:income|expense|\(income\))"),
           ("pretax", r"(?:Income|Loss|Income \(loss\)) before income taxes"), ("tax", r"Provision for"),
           ("net_income", r"Net (?:income|loss)")]
SBC_ROWS = [("sbc_ops", r"Operations and support"), ("sbc_pd", r"Product development"), ("sbc_sm", r"Sales and marketing"),
            ("sbc_ga", r"General and administrative"), ("sbc_restr", r"Restructuring charges"),
            ("sbc_total", r"(?:Total s|S)tock-based compensation expense")]


def row_after(seg, label_re, n, scale):
    m = re.search(label_re, seg)
    if not m:
        return None
    vals = []
    for x in toks(seg[m.end():m.end() + 800]):
        if isnum(x):
            vals.append(x)
        elif vals:
            break
    return [pnum(v) * scale for v in vals[:n]] if len(vals) >= n else None


def row_before(seg, label_re, n, scale):
    m = re.search(label_re, seg)
    if not m:
        return None
    tk = toks(seg[max(0, m.start() - 400):m.start()])
    vals = []
    for x in reversed(tk):
        if isnum(x):
            vals.append(x)
        elif vals:
            break
    vals = vals[::-1]
    return [pnum(v) * scale for v in vals[-n:]] if len(vals) >= n else None


def letter_income_statement(text):
    """Statement of operations columns from a letter. Columns are validated by the caller against XBRL revenue
    (the 3-month current-year column is the one whose revenue equals the quarter's XBRL revenue)."""
    m = re.search(r"Statements of Operations", text)
    if not m:
        return None
    seg = strip_markers(text[m.start():m.start() + 5000])
    scale = 1e-3 if re.search(r"in thousands", seg[:300]) else 1.0
    a = re.search(r"Revenue \$", seg)
    if not a:
        return None
    head = seg[:a.start()]
    years = re.findall(r"\b(20\d\d)\d?\b", head)
    n = len(years)
    if n == 0:
        return None
    body = seg[a.start():]
    stop = re.search(r"Balance Sheets", body)
    body = body[:stop.start()] if stop else body
    out = {key: row_after(body, rx, n, scale) for key, rx in IS_ROWS}
    ps = re.search(r"per share attributable", body)
    if ps:
        sub = body[ps.start():ps.start() + 700]
        if re.search(r"basic and diluted", sub[:200], re.I):
            v = row_after(sub, r"basic and diluted", n, 1.0)
            out["eps_basic"], out["eps_diluted"] = v, v
        else:
            out["eps_basic"] = row_after(sub, r"Basic", n, 1.0)
            out["eps_diluted"] = row_after(sub, r"Diluted", n, 1.0)
        sh = re.search(r"Weighted-average shares", body)
        if sh:
            sub2 = body[sh.start():sh.start() + 600]
            if re.search(r"basic and diluted", sub2[:250], re.I):
                v = row_after(sub2, r"basic and diluted", n, scale)
                out["shares_basic"], out["shares_diluted"] = v, v
            else:
                out["shares_basic"] = row_after(sub2, r"Basic", n, scale)
                out["shares_diluted"] = row_after(sub2, r"Diluted", n, scale)
    sbc_candidates = []
    for fn in re.finditer(r"stock-based compensation expense as follows", seg, re.I):
        sub = seg[fn.end():fn.end() + 1200]
        cand = {key: row_after(sub, rx, n, scale) for key, rx in SBC_ROWS}
        if cand.get("sbc_total") and cand.get("sbc_pd"):
            sbc_candidates.append(cand)
    return {"n": n, "scale": scale, "rows": out, "sbc_candidates": sbc_candidates, "years": years}


# --------------------------------------------------------------------------------------------- cash-flow statement (YTD)
CF_ROWS = [("cf_da", r"Depreciation and amortization"), ("cf_sbc", r"Stock-based compensation expense"),
           ("cf_unearned", r"Unearned fees"), ("cfo", r"Net cash provided by (?:\(used in\) )?operating activities"),
           ("cf_capex", r"Purchases of property and equipment"), ("cf_funds_payable", r"Change in funds payable"),
           ("cf_buybacks", r"Repurchases of common stock|Share repurchases"), ("cf_rsu_tax", r"Taxes paid related to"),
           ("cf_debt_proceeds", r"Proceeds from issuance of (?:long-term debt|convertible)"),
           ("cf_debt_repay", r"Principal repayment of long-term debt")]


def letter_cash_flow(text):
    """Both orientations (numbers after the label; numbers before the label, as in the 2Q26 letter) are returned;
    the caller keeps the one whose CFO matches XBRL."""
    m = re.search(r"Statements of Cash Flows", text)
    if not m:
        return None
    seg = text[m.start():m.start() + 6000]
    scale = 1e-3 if re.search(r"in thousands", seg[:300]) else 1.0
    a = re.search(r"Cash flows from operating activities", seg)
    if not a:
        return None
    head = seg[:a.start()]
    years = re.findall(r"\b(20\d\d)\d?\b", head)
    n = len(years)
    body = seg[a.start():]
    stop = re.search(r"Key Business Metrics|Cash, cash equivalents, and restricted cash, end", body)
    body = body[:stop.end()] if stop else body
    after = {key: row_after(body, rx, n, scale) for key, rx in CF_ROWS}
    before = {key: row_before(body, rx, n, scale) for key, rx in CF_ROWS}
    return {"n": n, "scale": scale, "after": after, "before": before, "years": years}


# --------------------------------------------------------------------------------------------- KPI summary table
def letter_kpis(text, letter_q):
    """Quarterly nights (M), GBV ($B) and ADR ($) from the letter's quarterly summary table, mapped to quarters
    with the year/quarter header printed after the table ('2019 2021 2022 Q1 Q2 Q3 Q4 Q1 ... Q1'). Used for the
    1Q19-2Q20 quarters (1Q21 and 4Q21 letters); later quarters come from the repo KPI panel."""
    out = {}
    best = None
    for m in re.finditer(r"Nights and (?:Experiences|Seats) Booked\s+((?:\d+\.\d\s*M\s+){4,})", text):
        vals = re.findall(r"\d+\.\d", m.group(1))
        if best is None or len(vals) > len(best[1]):
            best = (m, vals)
    if not best:
        return out
    m, nights = best
    seg = text[m.end():m.end() + 1500]
    g = re.search(r"Gross Booking Value\s+((?:\$\s*\d+\.\d\s*B\s+){2,})", seg)
    a = re.search(r"(?:or ADR\)|Experience Booked)\s+((?:\$\s*\d{2,3}\.\d{2}\s*){2,})", seg)
    h = re.search(r"((?:20\d\d\s+){1,5})((?:Q\d\s+){2,})", seg)
    if not (g and h):
        return out
    gbv = [float(x) for x in re.findall(r"\d+\.\d", g.group(1))]
    adr = [float(x) for x in re.findall(r"\d{2,3}\.\d{2}", a.group(1))] if a else []
    years = [int(y) for y in re.findall(r"20\d\d", h.group(1))]
    qs = [int(x[1]) for x in re.findall(r"Q\d", h.group(2))]
    k = len(nights)
    if len(gbv) != k or len(qs) != k:
        return out
    labels, yi, last = [], 0, 0
    for qn in qs:
        if qn <= last:
            yi += 1
        labels.append(qlabel(years[min(yi, len(years) - 1)], qn))
        last = qn
    for i, qq in enumerate(labels):
        out[qq] = {"nights_m": float(nights[i]), "gbv_busd": gbv[i], "adr_usd": adr[i] if len(adr) == k else None}
    return out


# --------------------------------------------------------------------------------------------- 10-K pipe tables
def tenk_row(text, label_re, ncols, start=0, scale=1.0):
    m = re.search(label_re, text[start:])
    if not m:
        return None
    seg = text[start + m.end(): start + m.end() + 800]
    vals, skipped = [], 0
    for cell in seg.split("|"):
        c = cell.strip().replace("$", "").strip()
        if c == "":
            continue
        if re.fullmatch(r"\(\d\)", c) and not vals:
            continue                                   # footnote marker "(1)" after the label
        if re.fullmatch(r"\(?[\d,]+(?:\.\d+)?\)?|-", c):
            vals.append(pnum(c) * scale)
            if len(vals) == ncols:
                break
        elif c == "%":
            continue
        elif vals:
            break
        elif skipped < 2:
            skipped += 1                               # remainder of a label split by the regex
        else:
            break
    return vals if len(vals) == ncols else None
