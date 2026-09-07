"""
02_peer_prints_build.py - build data/processed/predictive/02_peer_prints.csv and 02_peer_sources.csv.

Inputs (all local, see 02_peer_fetch.py for provenance):
  data/raw/peers/peer_filings_manifest.csv and the EX-99.1 press releases under data/raw/peers/<TICKER>/
  data/raw/xbrl/BKNG.json, EXPE.json      SEC companyfacts, quarterly revenue cross-check and margin denominators
  data/raw/prices/<TICKER>_daily.csv      yfinance daily closes (ABNB, BKNG, EXPE, MAR, HLT, QQQ)
  data/external/abnb_earnings_reactions.csv   ABNB reaction dates (release is the prior trading day)

What is parsed, and from where in each release
  BKNG  room nights y/y, gross bookings y/y (reported, constant currency), revenue y/y (reported, cc): the
        highlights sentences/bullets; Adjusted EBITDA: the GAAP-to-non-GAAP reconciliation table (2021-2024) or the
        stated "Adjusted EBITDA margin of x%" (2025 on); next-quarter direction: the Outlook table's room-night
        growth guide (Feb 2026 on) or gross-bookings guide (Jul 2025 on) vs the quarter just reported. Before
        Jul 2025 Booking gave guidance only on the call, so the release carries no direction.
  EXPE  the "Financial Summary & Operating Metrics" table: booked room nights (stayed-night growth before Q2 2022,
        flagged), gross bookings, revenue, Adjusted EBITDA; next-quarter direction from the Business Outlook table
        (Aug 2025 on) gross-bookings guide vs the quarter just reported.
  MAR   "comparable systemwide constant dollar RevPAR increased/declined x percent worldwide" (first bullet).
  HLT   "System-wide comparable RevPAR increased/decreased x percent, on a currency neutral basis" (first bullet).
Anything the regexes do not find is left blank and listed in the console summary. Nothing is filled from memory.

Report-date and reaction conventions
  report_date = 8-K filing date (same day as the release). BKNG and EXPE file after the close (about 20:00-21:00 UTC),
  so day-1 reaction is the next trading day; MAR and HLT file pre-market (10:00-13:00 UTC), reaction is the same day.
  Rule used: acceptance time >= 16:00 UTC -> next trading day. Excess return = ticker 1-day % minus QQQ 1-day %.
  ABNB release date = trading day before the reaction_date in abnb_earnings_reactions.csv (ABNB reports after close).
  lead_days = ABNB release date minus peer report date (positive = peer printed first).

Run: python analysis/src/predictive/02_peer_prints_build.py
"""
import html
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "peers"
OUT = ROOT / "data" / "processed" / "predictive"
PRICES = ROOT / "data" / "raw" / "prices"


# ----------------------------------------------------------------------------------------------------------------
def text_of(path):
    s = Path(path).read_text(encoding="utf-8", errors="replace")
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", s, flags=re.S | re.I)
    s = re.sub(r"</(p|div|tr|li|h\d)>", "\n", s, flags=re.I)
    s = re.sub(r"<br[^>]*>", "\n", s, flags=re.I)
    s = re.sub(r"</t[dh]>", " | ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s


def quarter_of_filing(filing_date):
    """Earnings 8-K filed in month m reports the quarter that ended before it."""
    y, m = int(filing_date[:4]), int(filing_date[5:7])
    q = {1: 4, 2: 4, 3: 4, 4: 1, 5: 1, 6: 1, 7: 2, 8: 2, 9: 2, 10: 3, 11: 3, 12: 3}[m]
    return f"{y - 1 if q == 4 else y}Q{q}"


def num(s):
    """'(40)' -> -40.0, '1,086' -> 1086.0, '(17.1)' -> -17.1"""
    s = s.strip().replace(",", "").replace("$", "").rstrip("%").strip()
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()%")
    return -float(s) if neg else float(s)


def pct_change_phrase(window):
    """First growth phrase in a sentence: 'an increase of 129%', 'a 65% decrease', 'grew 14%', 'increased 8%'.
    Returns (value, matched_text) or (None, None)."""
    pats = [
        r"(?:an?\s+)?(increase|decrease)\s+of\s+(\d+(?:\.\d+)?)%",
        r"(?:an?\s+)?(?:approximately\s+)?(\d+(?:\.\d+)?)%\s+(increase|decrease)",
        r"\b(grew|increased|decreased|declined)\s+(\d+(?:\.\d+)?)%",
    ]
    best = None
    for p in pats:
        m = re.search(p, window, flags=re.I)
        if m and (best is None or m.start() < best.start()):
            best = m
    if not best:
        return None, None
    g = best.groups()
    word, val = (g[0], g[1]) if not g[0][0].isdigit() else (g[1], g[0])
    sign = -1 if word.lower() in ("decrease", "decreased", "declined") else 1
    return sign * float(val), best.group(0)


def cc_phrase(window):
    """Constant-currency growth in the same sentence, e.g. '(approximately a 52% increase on a constant-currency
    basis)' or ', or 10% on a constant currency basis'. Returns value or None."""
    m = re.search(r"(?:approximately\s+)?(?:an?\s+)?(\d+(?:\.\d+)?)%\s+(increase|decrease)\s+on\s+a\s+constant[- ]currency", window, re.I)
    if m:
        return (-1 if m.group(2).lower() == "decrease" else 1) * float(m.group(1))
    m = re.search(r",?\s+or\s+(?:approximately\s+)?(\d+(?:\.\d+)?)%\s+on\s+a\s+constant[- ]currency", window, re.I)
    if m:
        return float(m.group(1))
    return None


STOP_DEFAULT = r"(?:\.\s+(?=[A-Z●•])|[●•]|\n|Room nights|Total revenues|Revenue grew)"


def sentence_after(text, start_pat, stop_pat=STOP_DEFAULT, maxlen=600):
    m = re.search(start_pat, text, flags=re.I)
    if not m:
        return None
    w = text[m.start(): m.start() + maxlen]
    stop = re.search(stop_pat, w[len(m.group(0)):])
    return w[: len(m.group(0)) + stop.start()] if stop else w


def compact(s, n=220):
    return re.sub(r"\s+", " ", s or "")[:n]


# ----------------------------------------------------------------------------------------------------------------
def parse_bkng(t):
    r, src = {}, {}
    # room nights
    m = re.search(r"Room nights(?: booked)?(?: in the \d(?:st|nd|rd|th) quarter(?: of \d{4})?)?\s+(increased|decreased|grew|declined)\s+(\d+)%", t)
    if m:
        r["room_nights_yoy"] = (-1 if m.group(1) in ("decreased", "declined") else 1) * float(m.group(2))
        src["room_nights"] = compact(m.group(0))
    # gross bookings
    s = sentence_after(t, r"(?:gross travel bookings|Gross bookings grew)")
    if s:
        v, _ = pct_change_phrase(s)
        r["gb_yoy"], r["gb_yoy_cc"], src["gross_bookings"] = v, cc_phrase(s), compact(s)
        if v is not None and re.search(r"both an as-reported and constant-currency", s):
            r["gb_yoy_cc"] = v
        gbm = re.search(r"\$(\d+(?:\.\d+)?)\s+billion", s)
        if gbm:
            r["gb_usd_b"] = float(gbm.group(1))
    # revenue
    s = sentence_after(t, r"(?:total revenues(?: for the \d(?:st|nd|rd|th) quarter of \d{4})? were|Revenue grew)",
                       stop_pat=r"(?:\.\s+(?=[A-Z●•])|[●•]|\n)")
    if s:
        v, _ = pct_change_phrase(s)
        r["rev_yoy"], r["rev_yoy_cc"], src["revenue"] = v, cc_phrase(s), compact(s)
        if v is not None and re.search(r"both an as-reported and constant-currency", s):
            r["rev_yoy_cc"] = v
    # adjusted EBITDA: reconciliation table (exact $M) -> stated margin (2025+) -> rounded highlight
    m = re.search(r"Adjusted EBITDA \|(?: \|)* \$ \| (\(?[\d,]+\)?)", t)
    if m:
        r["adj_ebitda_musd"] = num(m.group(1))
        src["adj_ebitda"] = compact(m.group(0))
    m2 = re.search(r"Adjusted EBITDA margin of (\d+(?:\.\d+)?)%", t)
    if m2:
        r["adj_ebitda_margin_stated"] = float(m2.group(1))
        src["adj_ebitda_margin"] = compact(m2.group(0))
    m3 = re.search(r"Adjusted EBITDA as a % of Total Revenues \|(?: \|)* (\(?[\d.]+\)?) \| %", t)
    if m3:
        r["adj_ebitda_margin_stated"] = num(m3.group(1))
        src["adj_ebitda_margin"] = compact(m3.group(0))
    # outlook (Jul 2025 on): room-nights guide preferred, else gross bookings guide
    o = re.search(r"Room Nights? Growth\s+(\d+(?:\.\d+)?)%\s*-\s*(\d+(?:\.\d+)?)%", t)
    g = re.search(r"Gross Bookings Growth\s+(\d+(?:\.\d+)?)%\s*-\s*(\d+(?:\.\d+)?)%", t)
    if o:
        r["guide_next_lo"], r["guide_next_hi"], r["guide_metric"] = float(o.group(1)), float(o.group(2)), "room nights y/y"
        src["outlook"] = compact(t[max(0, o.start() - 120): o.end() + 60])
    elif g:
        r["guide_next_lo"], r["guide_next_hi"], r["guide_metric"] = float(g.group(1)), float(g.group(2)), "gross bookings y/y (reported)"
        src["outlook"] = compact(t[max(0, g.start() - 120): g.end() + 60])
    return r, src


def table_row(t, label_pat):
    """Return list of cell strings for the first table row whose first cell matches label_pat."""
    # label may sit on its own line with the cells on the next ('Gross bookings /  | $15,422 | ...' in 2021-2023)
    m = re.search(r"(?:^|\n|\| )\s*(" + label_pat + r")[^|\n]*\n?\s*\|([^\n]*)", t, flags=re.I)
    if not m:
        return None, None
    cells = [c.strip() for c in m.group(2).split("|")]
    cells = [c for c in cells if c not in ("", "$")]
    return cells, compact(m.group(0))


def parse_expe(t_full):
    r, src = {}, {}
    # restrict the KPI rows to the summary table so 'Revenue' does not hit a segment table further down
    h = re.search(r"Financial Summary\s*&\s*Operating Metrics", t_full)
    t = t_full[h.start(): h.start() + 3000] if h else t_full
    cells, s = table_row(t, r"Booked room nights")
    if cells and len(cells) >= 3 and re.match(r"^[\d.]+$", cells[0]):
        cur, prev = float(cells[0]), float(cells[1])
        r["room_nights_yoy"] = round((cur / prev - 1) * 100, 1)
        r["room_nights_m"], r["room_nights_basis"], src["room_nights"] = cur, "booked", s
    else:
        cells, s = table_row(t, r"(?:Stayed )?[Rr]oom night growth")
        if cells:
            r["room_nights_yoy"], r["room_nights_basis"], src["room_nights"] = num(cells[0]), "stayed (growth only)", s
    if "room_nights_yoy" not in r:  # fall back to the highlights bullet, e.g. 'Booked room nights grew 9% in the fourth quarter'
        m = re.search(r"Booked [Rr]oom [Nn]ights grew (\d+(?:\.\d+)?)%", t_full)
        if m:
            r["room_nights_yoy"], r["room_nights_basis"], src["room_nights"] = float(m.group(1)), "booked (bullet, rounded)", compact(m.group(0))
    for key, lab in [("gb", r"Gross bookings"), ("rev", r"Revenue")]:
        cells, s = table_row(t, lab)
        if cells and len(cells) >= 2:
            cur, prev = num(cells[0]), num(cells[1])
            r[f"{key}_yoy"] = round((cur / prev - 1) * 100, 1)
            r[f"{key}_musd"] = cur
            src["gross_bookings" if key == "gb" else "revenue"] = s
    cells, s = table_row(t, r"Adjusted EBITDA\*?(?:\(\d\))?")
    if cells:
        r["adj_ebitda_musd"], src["adj_ebitda"] = num(cells[0]), s
    # Business Outlook (Aug 2025 on): next-quarter gross bookings growth range
    o = re.search(r"Business Outlook(.{0,900})", t_full, flags=re.S)
    if o:
        blk = re.sub(r"\s+", " ", o.group(1))
        # 'Gross bookings | 2-4% | 3-5% | 5-7% |' (last range is the quarter) or 'Gross bookings | $34.6 - $35.2B / +10 - 12% /'
        row = re.search(r"Gross [Bb]ookings \|(.*?)(?:Revenue \|)", blk)
        if row:
            ranges = re.findall(r"\+?(\d+)\s*-\s*(\d+)%|(?<![\d.\-])(\d+)%(?!\s*-)", row.group(1))
            hdr = re.search(r"Metric \| ([^|]+) \| ([^|]+) \|", blk)
            cand = [(float(a), float(b)) if a else (float(c), float(c)) for a, b, c in ranges]
            if cand:
                # quarter column is first when the header starts with 'Qn yyyy', else it is the last column
                pick = cand[0] if (hdr and hdr.group(1).strip().startswith("Q")) else cand[-1]
                r["guide_next_lo"], r["guide_next_hi"], r["guide_metric"] = pick[0], pick[1], "gross bookings y/y"
                src["outlook"] = compact(row.group(0), 260)
    return r, src


def parse_mar(t):
    m = re.search(r"RevPAR1?\s+(increased|declined|decreased)\s+(\d+(?:\.\d+)?)\s+percent\s+worldwide", t)
    if not m:
        return {}, {}
    v = (-1 if m.group(1) != "increased" else 1) * float(m.group(2))
    return {"revpar_yoy": v}, {"revpar": compact(t[max(0, m.start() - 80): m.end() + 40])}


def parse_hlt(t):
    m = re.search(r"System-wide comparable RevPAR\s+(increased|decreased|declined)\s+(\d+(?:\.\d+)?)\s+percent", t)
    if not m:
        return {}, {}
    v = (-1 if m.group(1) != "increased" else 1) * float(m.group(2))
    return {"revpar_yoy": v}, {"revpar": compact(t[m.start(): m.end() + 140])}


PARSERS = {"BKNG": parse_bkng, "EXPE": parse_expe, "MAR": parse_mar, "HLT": parse_hlt}
# Non-earnings Item 2.02 8-Ks to skip (ticker, filing_date): Hilton 19 Jan 2021 was a preliminary Q4 2020 update.
SKIP = {("HLT", "2021-01-19")}


# ----------------------------------------------------------------------------------------------------------------
def xbrl_quarterly_revenue(tk, tag):
    d = json.load(open(ROOT / "data" / "raw" / "xbrl" / f"{tk}.json"))
    rows = d["facts"]["us-gaap"][tag]["units"]["USD"]
    q = {r["frame"][2:]: r["val"] for r in rows if re.fullmatch(r"CY\d{4}Q\d", r.get("frame", ""))}
    fy = {r["frame"][2:]: r["val"] for r in rows if re.fullmatch(r"CY\d{4}", r.get("frame", ""))}
    for y, v in fy.items():
        if all(f"{y}Q{i}" in q for i in (1, 2, 3)) and f"{y}Q4" not in q:
            q[f"{y}Q4"] = v - sum(q[f"{y}Q{i}"] for i in (1, 2, 3))
    return {k: v / 1e6 for k, v in q.items()}


def load_prices():
    px = {}
    for tk in ["ABNB", "BKNG", "EXPE", "MAR", "HLT", "QQQ"]:
        s = pd.read_csv(PRICES / f"{tk}_daily.csv", parse_dates=["date"]).set_index("date")["close"]
        px[tk] = s
    return pd.DataFrame(px).sort_index()


def one_day_reaction(px, tk, filing_date, acceptance):
    d = pd.Timestamp(filing_date)
    hour = int(acceptance[11:13])
    idx = px.index
    if hour >= 16:  # after the close -> next trading day
        pos = idx.searchsorted(d, side="right")
    else:           # pre-market -> same day (or next session if a holiday)
        pos = idx.searchsorted(d, side="left")
    if pos >= len(idx) or pos == 0:
        return None, None, None, None
    day, prev = idx[pos], idx[pos - 1]
    r = (px[tk][day] / px[tk][prev] - 1) * 100
    q = (px["QQQ"][day] / px["QQQ"][prev] - 1) * 100
    return day.date().isoformat(), round(r, 2), round(q, 2), round(r - q, 2)


def direction(rep, guide_lo, guide_hi, tol=0.5):
    if rep is None or guide_lo is None or np.isnan(rep):
        return ""
    mid = (guide_lo + guide_hi) / 2
    return "accelerate" if mid > rep + tol else "decelerate" if mid < rep - tol else "stable"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    man = pd.read_csv(RAW / "peer_filings_manifest.csv", dtype=str).fillna("")
    px = load_prices()
    xrev = {"BKNG": xbrl_quarterly_revenue("BKNG", "Revenues"),
            "EXPE": xbrl_quarterly_revenue("EXPE", "RevenueFromContractWithCustomerExcludingAssessedTax")}

    # ABNB print dates
    rx = pd.read_csv(ROOT / "data" / "external" / "abnb_earnings_reactions.csv", parse_dates=["reaction_date"])
    abnb_dates = {}
    for _, row in rx.iterrows():
        pos = px.index.searchsorted(row["reaction_date"], side="left")
        abnb_dates[row["quarter"]] = dict(abnb_release_date=px.index[pos - 1].date().isoformat(),
                                          abnb_reaction_date=row["reaction_date"].date().isoformat())

    long_rows, src_rows, missing = [], [], []
    for _, f in man.iterrows():
        tk = f["ticker"]
        if (tk, f["filing_date"]) in SKIP or not f["local_path"]:
            continue
        qtr = quarter_of_filing(f["filing_date"])
        t = text_of(ROOT / f["local_path"])
        r, src = PARSERS[tk](t)
        day, r1, q1, ex1 = one_day_reaction(px, tk, f["filing_date"], f["acceptance"])
        rec = dict(quarter=qtr, ticker=tk, report_date=f["filing_date"], acceptance_utc=f["acceptance"][11:16],
                   reaction_date=day, stock_1d_pct=r1, qqq_1d_pct=q1, excess_1d_pct=ex1, **r)
        if tk in xrev:
            cur, prev = xrev[tk].get(qtr), xrev[tk].get(f"{int(qtr[:4]) - 1}{qtr[4:]}")
            rec["rev_musd_xbrl"] = round(cur, 1) if cur else None
            rec["rev_yoy_xbrl"] = round((cur / prev - 1) * 100, 1) if cur and prev else None
            if rec.get("adj_ebitda_musd") is not None and cur:
                rec["adj_ebitda_margin_pct"] = round(rec["adj_ebitda_musd"] / cur * 100, 1)
            elif rec.get("adj_ebitda_margin_stated") is not None:
                rec["adj_ebitda_margin_pct"] = rec["adj_ebitda_margin_stated"]
            basis = rec.get("room_nights_yoy") if rec.get("guide_metric", "").startswith("room") else rec.get("gb_yoy")
            rec["next_q_direction"] = direction(basis, rec.get("guide_next_lo"), rec.get("guide_next_hi"))
            if not rec["next_q_direction"]:
                rec["next_q_note"] = "no quantified next-quarter guide in the release (given on the call)"
            else:
                rec["next_q_note"] = (f"{rec['guide_metric']} guide {rec['guide_next_lo']:g}-{rec['guide_next_hi']:g}% "
                                      f"vs {basis:g}% just reported")
        long_rows.append(rec)
        for k, v in src.items():
            src_rows.append(dict(quarter=qtr, ticker=tk, metric=k, report_date=f["filing_date"], accession=f["accession"],
                                 exhibit_url=f["exhibit_url"], extracted_text=v))
        want = {"BKNG": ["room_nights_yoy", "gb_yoy", "rev_yoy", "adj_ebitda_margin_pct"],
                "EXPE": ["room_nights_yoy", "gb_yoy", "rev_yoy", "adj_ebitda_margin_pct"],
                "MAR": ["revpar_yoy"], "HLT": ["revpar_yoy"]}[tk]
        for k in want:
            if rec.get(k) is None or (isinstance(rec.get(k), float) and np.isnan(rec[k])):
                missing.append((qtr, tk, k))

    long = pd.DataFrame(long_rows)
    long = long[(long["quarter"] >= "2020Q4") & (long["quarter"] <= "2026Q2")].sort_values(["quarter", "ticker"])

    # wide table, one row per quarter, 2021Q1..2026Q2 (2020Q4 kept for the prior-quarter acceleration)
    quarters = sorted(long["quarter"].unique())
    wide = []
    cols_by_tk = [
        ("BKNG", ["report_date", "acceptance_utc", "room_nights_yoy", "gb_yoy", "gb_yoy_cc", "rev_yoy", "rev_yoy_cc", "rev_yoy_xbrl",
                  "adj_ebitda_margin_pct", "next_q_direction", "next_q_note", "reaction_date", "stock_1d_pct", "qqq_1d_pct", "excess_1d_pct"]),
        ("EXPE", ["report_date", "acceptance_utc", "room_nights_yoy", "room_nights_basis", "gb_yoy", "rev_yoy", "rev_yoy_xbrl",
                  "adj_ebitda_margin_pct", "next_q_direction", "next_q_note", "reaction_date", "stock_1d_pct", "qqq_1d_pct", "excess_1d_pct"]),
        ("MAR", ["report_date", "acceptance_utc", "revpar_yoy", "reaction_date", "stock_1d_pct", "excess_1d_pct"]),
        ("HLT", ["report_date", "acceptance_utc", "revpar_yoy", "reaction_date", "stock_1d_pct", "excess_1d_pct"]),
    ]
    for q in quarters:
        row = dict(quarter=q, **abnb_dates.get(q, dict(abnb_release_date=None, abnb_reaction_date=None)))
        for tk, cols in cols_by_tk:
            sub = long[(long["quarter"] == q) & (long["ticker"] == tk)]
            for c in cols:
                row[f"{tk.lower()}_{c}"] = sub.iloc[0][c] if len(sub) and c in sub.columns else None
            if len(sub) and row["abnb_release_date"]:
                row[f"{tk.lower()}_lead_days"] = (pd.Timestamp(row["abnb_release_date"]) - pd.Timestamp(sub.iloc[0]["report_date"])).days
            else:
                row[f"{tk.lower()}_lead_days"] = None
        wide.append(row)
    wide = pd.DataFrame(wide)
    # accelerations (pp vs prior quarter), computed on the wide table so 2020Q4 seeds 2021Q1
    for c in ["bkng_room_nights_yoy", "bkng_gb_yoy", "expe_room_nights_yoy", "expe_gb_yoy", "mar_revpar_yoy", "hlt_revpar_yoy"]:
        wide[c.replace("_yoy", "_accel_pp")] = wide[c].astype(float).diff().round(1)
    wide = wide[wide["quarter"] >= "2021Q1"]
    wide.to_csv(OUT / "02_peer_prints.csv", index=False)
    pd.DataFrame(src_rows).sort_values(["ticker", "quarter", "metric"]).to_csv(OUT / "02_peer_sources.csv", index=False)
    long.to_csv(OUT / "02_peer_prints_long.csv", index=False)

    pd.set_option("display.width", 250)
    print(wide[["quarter", "abnb_release_date", "bkng_report_date", "bkng_lead_days", "bkng_room_nights_yoy", "bkng_gb_yoy", "bkng_gb_yoy_cc",
                "bkng_rev_yoy", "bkng_rev_yoy_xbrl", "bkng_adj_ebitda_margin_pct", "bkng_next_q_direction", "bkng_excess_1d_pct"]].to_string())
    print(wide[["quarter", "expe_report_date", "expe_lead_days", "expe_room_nights_yoy", "expe_room_nights_basis", "expe_gb_yoy", "expe_rev_yoy",
                "expe_rev_yoy_xbrl", "expe_adj_ebitda_margin_pct", "expe_next_q_direction", "expe_excess_1d_pct"]].to_string())
    print(wide[["quarter", "mar_report_date", "mar_lead_days", "mar_revpar_yoy", "mar_excess_1d_pct", "hlt_report_date", "hlt_lead_days",
                "hlt_revpar_yoy", "hlt_excess_1d_pct"]].to_string())
    print("\nMISSING (quarter, ticker, field):", missing if missing else "none")
    print(long[long.ticker.isin(["BKNG", "EXPE"])][["quarter", "ticker", "next_q_note"]].tail(10).to_string())


if __name__ == "__main__":
    main()
