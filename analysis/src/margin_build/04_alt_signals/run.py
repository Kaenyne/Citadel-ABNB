"""WS04 alt signals: build the quarterly signal panel from raw pulls and run the pre-registered tests.

Run from the worktree root:  python analysis/src/margin_build/04_alt_signals/run.py
Pulls are separate scripts (pull_fred.py --pull, pull_wayback.py --pull, pull_lseg_peers*.py --pull); this script only reads raw.

Pre-registered test (docs/margin-build/prompts/04_alt_signals.md): Pearson r between the signal's y/y change and the
matching cash cost line's y/y change (per night where a per-unit line makes sense), contemporaneous and led 1-2 quarters,
over 1Q22-2Q26 (cash lines start 1Q21, so y/y starts 1Q22; n <= 18), plus the same against adj. EBITDA margin (y/y pp).
Pass line: |r| >= 0.5, n >= 14, sign as expected -> "candidate"; else "logged, not promising". Every test is written out.
Added (brief standard): the same r on the recent window 1Q24-2Q26 (n <= 10) and an exponentially recency-weighted r
(half-life 4 quarters); a candidate must keep |r| >= 0.5 with the right sign on the recent window too to be "candidate_both".
"""
from __future__ import annotations
import hashlib, html, json, pathlib, re, datetime as dt
import numpy as np, pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[4]
RAW = ROOT / "data/raw/margin_build/04_alt_signals"
OUT = ROOT / "data/processed/margin_build/04_alt_signals"; OUT.mkdir(parents=True, exist_ok=True)
MAN = ROOT / "data/manifests/margin_build"; MAN.mkdir(parents=True, exist_ok=True)
PROC = ROOT / "data/processed"

CAT: list[dict] = []   # catalogue rows
SIG: dict[str, pd.Series] = {}   # series name -> quarterly Series indexed by "YYYYQn"
KNOW: dict[str, pd.Series] = {}  # series name -> knowable_from per quarter
META: dict[str, dict] = {}

def qlabel(ts: pd.Timestamp) -> str:
    return f"{ts.year}Q{(ts.month - 1) // 3 + 1}"

def q_from_fiscal(s: str) -> str:  # "1Q21" -> "2021Q1"
    m = re.match(r"(\d)Q(\d\d)", s); return f"20{m.group(2)}Q{m.group(1)}"

def qend(q: str) -> pd.Timestamp:
    y, n = int(q[:4]), int(q[-1]); return pd.Timestamp(year=y, month=3 * n, day=1) + pd.offsets.MonthEnd(0)

def add(name, series: pd.Series, *, target, source, status, coverage, lag_days=None, knowable=None, licence="public", note="", unit="", family=""):
    """Register a quarterly series (index YYYYQn) plus its catalogue row."""
    s = pd.Series(series).dropna()
    s.index = [str(i) for i in s.index]
    SIG[name] = s
    if knowable is not None:
        KNOW[name] = pd.Series(knowable)
    elif lag_days is not None:
        KNOW[name] = pd.Series({q: (qend(q) + pd.Timedelta(days=lag_days)).date().isoformat() for q in s.index})
    META[name] = dict(target=target, family=family)
    CAT.append(dict(series=name, family=family, target_line=target, status=status, source=source, coverage=coverage if coverage else (f"{s.index.min()}..{s.index.max()} (n={len(s)})" if len(s) else "none"),
                    n_quarters=len(s), unit=unit, licence=licence, knowable_rule=(f"quarter end + {lag_days}d" if lag_days is not None else "per observation"), note=note))

def log_only(name, *, target, source, status, note, family=""):
    CAT.append(dict(series=name, family=family, target_line=target, status=status, source=source, coverage="none", n_quarters=0, unit="", licence="", knowable_rule="", note=note))

# ----------------------------------------------------------------------------------------------------------------- targets
def load_targets() -> pd.DataFrame:
    cs = pd.read_csv(PROC / "abnb_quarterly_cost_stack_exsbc.csv")
    cs["q"] = cs["quarter"].map(q_from_fiscal); cs = cs.set_index("q")
    t = pd.DataFrame(index=cs.index)
    for c in ["cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash"]:
        t[c] = cs[c]
    t["cor_cash_per_night"] = cs["cor_cash"] / cs["nights_m"]
    t["ops_cash_per_night"] = cs["ops_cash"] / cs["nights_m"]
    t["sm_cash_per_night"] = cs["sm_cash"] / cs["nights_m"]
    t["cor_cash_pct_gbv"] = cs["cor_cash"] / (cs["gbv_busd"] * 1000) * 100
    t["adj_ebitda_margin_pct"] = cs["adj_ebitda_margin_pct"]
    t["nights_m"] = cs["nights_m"]; t["revenue_musd"] = cs["revenue_musd"]; t["gbv_busd"] = cs["gbv_busd"]
    # below EBITDA from XBRL
    x = pd.read_csv(RAW / "xbrl/abnb_xbrl_below_ebitda_facts.csv")
    ii = x[(x.tag == "InvestmentIncomeNonoperating") & x.frame.fillna("").str.match(r"CY\d{4}Q\d")].copy()
    ii["q"] = ii["frame"].str.replace("CY", "", regex=False)
    ii = ii.sort_values("filed").drop_duplicates("q", keep="first").set_index("q")["val"] / 1e6
    ii = ii.reindex(t.index)
    # Q4 is not framed quarterly in companyfacts: fill Q4 = FY - (Q1+Q2+Q3) from the CY frame
    fy = x[(x.tag == "InvestmentIncomeNonoperating") & x.frame.fillna("").str.match(r"CY\d{4}$")].sort_values("filed").drop_duplicates("frame", keep="first")
    for _, r in fy.iterrows():
        y = r["frame"][2:]; q4 = f"{y}Q4"
        if q4 in ii.index and pd.isna(ii[q4]) and all(pd.notna(ii.get(f"{y}Q{k}", np.nan)) for k in (1, 2, 3)):
            ii[q4] = r["val"] / 1e6 - sum(ii[f"{y}Q{k}"] for k in (1, 2, 3))
    t["interest_income_musd"] = ii
    def instant(tag):
        b = x[x.tag == tag].sort_values("filed").drop_duplicates("end", keep="first").copy()
        b["q"] = pd.to_datetime(b["end"]).map(qlabel); return (b.set_index("q")["val"] / 1e6).reindex(t.index)
    t["funds_held_musd"] = instant("FundsHeldForClients")
    t["cash_musd"] = instant("CashAndCashEquivalentsAtCarryingValue"); t["sti_musd"] = instant("ShortTermInvestments")
    return t

# ----------------------------------------------------------------------------------------------------------------- helpers
def fred(sid: str, how="mean") -> pd.Series:
    f = RAW / "fred" / f"{sid}.csv"
    if not f.exists(): return pd.Series(dtype=float)
    d = pd.read_csv(f); d.columns = ["date", "v"]; d["v"] = pd.to_numeric(d["v"], errors="coerce"); d["date"] = pd.to_datetime(d["date"])
    d = d.dropna(); d["q"] = d["date"].map(qlabel)
    g = d.groupby("q")["v"]
    return (g.mean() if how == "mean" else g.sum())

def yoy(s: pd.Series, pct=True) -> pd.Series:
    s = s.copy(); idx = list(s.index)
    out = {}
    for q in idx:
        p = f"{int(q[:4]) - 1}Q{q[-1]}"
        if p in s.index and pd.notna(s[p]) and pd.notna(s[q]):
            out[q] = (s[q] / s[p] - 1) * 100 if pct else (s[q] - s[p])
    return pd.Series(out, dtype=float)

def shift_q(s: pd.Series, lead: int) -> pd.Series:
    """Move signal forward by `lead` quarters (signal at q-lead aligned to target at q)."""
    if lead == 0: return s
    out = {}
    for q, v in s.items():
        y, n = int(q[:4]), int(q[-1]); n += lead
        while n > 4: n -= 4; y += 1
        out[f"{y}Q{n}"] = v
    return pd.Series(out, dtype=float)

def wcorr(x: np.ndarray, y: np.ndarray, w: np.ndarray) -> float:
    w = w / w.sum(); mx, my = (w * x).sum(), (w * y).sum()
    cov = (w * (x - mx) * (y - my)).sum(); vx = (w * (x - mx) ** 2).sum(); vy = (w * (y - my) ** 2).sum()
    return float(cov / np.sqrt(vx * vy)) if vx > 0 and vy > 0 else np.nan

# ----------------------------------------------------------------------------------------------------------------- signals
def build_signals(t: pd.DataFrame):
    fm = pd.read_csv(RAW / "fred/_fred_manifest.csv").set_index("series")
    def F(sid, name, target, family, lag, unit="", note="", how="mean"):
        s = fred(sid, how)
        if len(s) == 0:
            log_only(name, target=target, source=f"FRED {sid}", status="unreachable", note="FRED returned no CSV for this id (see _fred_manifest.csv)", family=family); return
        add(name, s, target=target, source=f"FRED {sid}: {fm.loc[sid,'description'] if sid in fm.index else ''}", status="pulled", coverage=None, lag_days=lag, unit=unit, family=family, note=note)
    # rates -> interest income
    F("DTB3", "rate_tbill3m", "interest_income", "rates", 1, "pct")
    F("DGS1", "rate_ust1y", "interest_income", "rates", 1, "pct")
    F("FEDFUNDS", "rate_fedfunds", "interest_income", "rates", 7, "pct")
    F("SOFR", "rate_sofr", "interest_income", "rates", 1, "pct")
    F("ECBDFR", "rate_ecb_deposit", "interest_income", "rates", 1, "pct")
    # wages / labour -> product dev, G&A
    F("CES5051200001", "emp_software_publishers", "pd_cash", "labour", 7, "thousands", "BLS CES employment, software publishers (NAICS 5112)")
    F("CES6054150001", "emp_computer_systems_design", "pd_cash", "labour", 7, "thousands")
    F("CES5000000003", "ahe_information", "pd_cash", "labour", 7, "USD/h", "avg hourly earnings, information sector")
    F("ECIWAG", "eci_wages_private", "pd_cash", "labour", 30, "index")
    F("CUURA422SA0", "cpi_sf_bay", "ga_cash", "labour", 14, "index", "CPI-U San Francisco-Oakland-Hayward, bimonthly")
    F("CES6056140001", "emp_business_support_services", "ops_cash", "labour", 7, "thousands", "BLS CES employment, business support services (NAICS 5614, call centres)")
    F("ICSA", "initial_claims", "macro", "macro", 7, "persons")
    F("UNRATE", "unemployment_rate", "macro", "macro", 7, "pct")
    # PPIs -> cost of revenue / ops
    F("PCU518210518210", "ppi_data_hosting", "cor_cash", "prices", 14, "index", "PPI computing infrastructure, data processing, hosting (NAICS 518210)")
    F("PCU5182105182105", "ppi_hosting_related", "cor_cash", "prices", 14, "index")
    F("PCU5242105242101", "ppi_insurance_brokerage", "ops_cash", "prices", 14, "index", "PPI insurance agencies and brokerages (host liability insurance premium proxy)")
    # macro cycle
    F("UMCSENT", "umich_sentiment", "macro", "macro", 0, "index")
    F("DSPIC96", "real_disposable_income", "macro", "macro", 30, "USD bn")
    F("PCEC96", "real_pce", "macro", "macro", 30, "USD bn")
    F("CPIAUCSL", "cpi_all", "macro", "macro", 14, "index")
    F("CES7072100001", "emp_accommodation", "macro", "macro", 7, "thousands")
    F("DEXUSEU", "fx_usd_per_eur", "cor_cash", "fx", 1, "USD/EUR")
    F("DTWEXBGS", "fx_broad_dollar", "cor_cash", "fx", 1, "index")
    for sid in ["CES5051200003", "CES6054150003", "JTS5100JOL", "JTS5100LDL", "PCU561422561422", "PCU5614205614201", "CES6056142001", "CES6056142003", "PCU54151054151011"]:
        log_only(f"fred_{sid}", target="pd_cash/ops_cash", source=f"FRED {sid}", status="unreachable", note="404 from fredgraph.csv (id not on FRED or renamed after NAICS 2022 revision); 24 alternative ids tried, see pull log", family="labour")

    # TSA throughput
    tsa = pd.read_csv(RAW / "tsa/tsa_daily_parsed.csv", parse_dates=["date"]); tsa["q"] = tsa["date"].map(qlabel)
    add("tsa_throughput", tsa.groupby("q")["throughput"].sum(), target="macro", source="https://www.tsa.gov/travel/passenger-volumes/{year}", status="pulled", coverage=None, lag_days=1, unit="passengers/quarter", family="macro")

    # Google Trends (repo pull, 6 Sep 2026)
    tr = pd.read_csv(PROC / "overnight/08_trends_weekly.csv", parse_dates=["date"])
    tr = tr[tr.payload == "P1_peers"]; tr["q"] = tr["date"].map(qlabel)
    for geo in ["WW", "US"]:
        g = tr[tr.geo == geo].pivot_table(index="q", columns="term", values="value_stitched", aggfunc="mean")
        add(f"trends_airbnb_{geo.lower()}", g["airbnb"], target="sm_cash", source="Google Trends via pytrends, repo data/processed/overnight/08_trends_weekly.csv (pulled 6 Sep 2026)", status="pulled", coverage=None, lag_days=1, unit="index", family="marketing")
        share = g["airbnb"] / (g["airbnb"] + g["booking.com"] + g["expedia"] + g["vrbo"])
        add(f"trends_airbnb_share_{geo.lower()}", share * 100, target="sm_cash", source="same; airbnb / (airbnb+booking.com+expedia+vrbo), same-payload stitched values", status="pulled", coverage=None, lag_days=1, unit="pct", family="marketing")

    # Wayback careers open roles
    cp = pd.read_csv(RAW / "wayback/_careers_parse_raw.csv", dtype=str)
    roles = {}; know = {}
    for _, r in cp.iterrows():
        c = str(r["count_candidates"]) if pd.notna(r["count_candidates"]) else ""
        m = re.search(r"(\d[\d,]*)\s+(roles|Open Positions|open jobs)", c, flags=re.I)
        if not m: continue
        v = float(m.group(1).replace(",", ""))
        if r["page"] == "careers_home" or r["quarter"] not in roles:
            roles[r["quarter"]] = v; know[r["quarter"]] = pd.Timestamp(r["capture_ts"][:8]).date().isoformat()
    add("careers_open_roles", pd.Series(roles), target="pd_cash", source="Wayback captures of careers.airbnb.com (home 'N roles' 2019-2023, 'N Open Positions' 2024-26; positions page 'N open jobs' fills gaps)", status="partial", coverage=None, knowable=know, unit="open roles", family="labour", note="capture nearest quarter end; 2020Q2 = 7 roles (hiring freeze)")

    # App Store ratings (cumulative count -> new ratings per quarter, normalised per day)
    rows = []
    for f in sorted((RAW / "wayback/appstore").glob("*.html")):
        x = html.unescape(f.read_text(encoding="utf-8", errors="ignore"))
        m = re.search(r'"reviewCount":\s*"?(\d+)', x); rk = re.search(r"#(\d+)\s+in\s+Travel", x); rt = re.search(r'"ratingValue":\s*"?([\d.]+)', x)
        if m: rows.append(dict(q=f.stem.split("_")[0], ts=pd.Timestamp(f.stem.split("_")[1][:8]), cum=float(m.group(1)), rank=float(rk.group(1)) if rk else np.nan, rating=float(rt.group(1)) if rt else np.nan))
    ap = pd.DataFrame(rows).sort_values("ts")
    ap["new_per_day"] = ap["cum"].diff() / ap["ts"].diff().dt.days
    ap["gap_days"] = ap["ts"].diff().dt.days
    ap.loc[ap["gap_days"] > 200, "new_per_day"] = np.nan   # skip spans across missing captures
    ap.to_csv(OUT / "04_appstore_parsed.csv", index=False)
    add("appstore_new_ratings_per_day", ap.set_index("q")["new_per_day"], target="ops_cash", source="Wayback captures of apps.apple.com/us/app/airbnb/id401626263 (schema.org reviewCount)", status="pulled", coverage=None, knowable=ap.set_index("q")["ts"].dt.date.astype(str), unit="ratings/day", family="support", note="cumulative US rating count differenced between consecutive quarterly captures")
    add("appstore_travel_rank", ap.set_index("q")["rank"], target="sm_cash", source="same (#N in Travel, US)", status="pulled", coverage=None, knowable=ap.set_index("q")["ts"].dt.date.astype(str), unit="rank", family="marketing")

    # Glassdoor review count (partial, blocked after 2023)
    rows = []
    for f in sorted((RAW / "wayback/glassdoor").glob("*.html")):
        x = html.unescape(f.read_text(encoding="utf-8", errors="ignore"))
        m = re.search(r'"reviewCount":\s*"?(\d{3,6})', x)
        if m: rows.append((f.stem.split("_")[0], float(m.group(1)), pd.Timestamp(f.stem.split("_")[1][:8]).date().isoformat()))
    gd = pd.DataFrame(rows, columns=["q", "reviews", "know"]).drop_duplicates("q").set_index("q")
    add("glassdoor_reviews_cum", gd["reviews"], target="pd_cash", source="Wayback captures of glassdoor.com Airbnb overview (schema.org reviewCount)", status="partial", coverage=None, knowable=gd["know"], unit="reviews", family="labour", note="captures after 2023Q3 are bot-wall pages without counts")

    # Trustpilot / Sitejabber / Play Store parses (if captures exist)
    for key, pats, name, unit in [
        ("trustpilot", [r'"reviewCount":\s*"?(\d+)', r'([\d,]+)\s+(?:total )?reviews', r'"numberOfReviews":\s*(\d+)'], "trustpilot_reviews_cum", "reviews"),
        ("sitejabber", [r'"reviewCount":\s*"?(\d+)', r'([\d,]+)\s+reviews'], "sitejabber_reviews_cum", "reviews"),
        ("playstore", [r'"ratingCount":\s*"?(\d+)', r'([\d,.]+[KM]?)\s+reviews', r'\[\[null,(\d{6,})\]'], "playstore_ratings_cum", "ratings"),
    ]:
        d = RAW / "wayback" / key
        rows = []
        for f in sorted(d.glob("*.html")) if d.exists() else []:
            x = html.unescape(f.read_text(encoding="utf-8", errors="ignore"))
            for p in pats:
                m = re.search(p, x)
                if m:
                    v = m.group(1).replace(",", "")
                    mult = 1e6 if v.endswith("M") else 1e3 if v.endswith("K") else 1
                    try: rows.append((f.stem.split("_")[0], float(v.rstrip("KM")) * mult, pd.Timestamp(f.stem.split("_")[1][:8]))); break
                    except ValueError: pass
        if rows:
            df = pd.DataFrame(rows, columns=["q", "cum", "ts"]).drop_duplicates("q").sort_values("ts")
            df["new_per_day"] = df["cum"].diff() / df["ts"].diff().dt.days
            df.loc[df["ts"].diff().dt.days > 200, "new_per_day"] = np.nan
            df.to_csv(OUT / f"04_{key}_parsed.csv", index=False)
            add(name.replace("_cum", "_new_per_day"), df.set_index("q")["new_per_day"], target="ops_cash", source=f"Wayback captures of {key} Airbnb page", status="partial" if len(df) < 20 else "pulled", coverage=None, knowable=df.set_index("q")["ts"].dt.date.astype(str), unit=f"{unit}/day", family="support")
        else:
            log_only(name, target="ops_cash", source=f"Wayback {key}", status="partial" if d.exists() and any(d.iterdir()) else "unreachable", note="captures fetched but no review count parseable (JS-rendered or bot wall)" if d.exists() and any(d.iterdir()) else "no 200 captures in CDX", family="support")

    # LinkedIn: only 2 captures with counts, and they are LinkedIn member self-reports, not headcount
    log_only("linkedin_employees_on_linkedin", target="pd_cash", source="Wayback www.linkedin.com/company/airbnb", status="partial", note="11 captures 2023Q3-2026Q2; only 2024Q4 (44,959) and 2025Q2 (55,686) rendered a count, and it is LinkedIn member self-reports (includes hosts/contractors), not headcount; not usable", family="labour")
    log_only("bbb_complaints", target="ops_cash", source="Wayback bbb.org Airbnb profile", status="unreachable", note="CDX returned no 200 captures for the BBB profile URL pattern", family="support")
    log_only("downdetector_reports", target="ops_cash", source="Wayback downdetector.com/status/airbnb", status="out_of_rules", note="captures exist (2018+) but the page shows only a live 24h chart image; no time series recoverable", family="support")
    log_only("meta_ad_library_spend", target="sm_cash", source="https://www.facebook.com/ads/library/report/", status="unreachable", note="fetch hung up (socket); report is JS-rendered and only covers political/issue ads in the US anyway", family="marketing")
    log_only("google_ads_transparency", target="sm_cash", source="https://adstransparency.google.com/", status="unreachable", note="JS-rendered SPA; no spend figures in static HTML; no archive", family="marketing")
    log_only("layoffs_fyi_airbnb", target="pd_cash", source="Wayback layoffs.fyi", status="partial", note="captures exist; Airbnb rows are the May 2020 cut (1,900) and Mar 2023 recruiting cut only; used as events E10, no series", family="labour")

    # Peer opex from LSEG (licensed: only derived y/y goes to processed)
    p1 = pd.read_csv(RAW / "misc/lseg_peer_opex_quarterly.csv"); p2 = pd.read_csv(RAW / "misc/lseg_peer_sm_quarterly.csv")
    p1["q"] = pd.to_datetime(p1["Period End Date"]).map(qlabel); p2["q"] = pd.to_datetime(p2["Period End Date"]).map(qlabel)
    pulled = p1["pulled_at"].iloc[0]
    for ric, tag in [("BKNG.O", "bkng"), ("EXPE.O", "expe")]:
        a = p1[p1.ric == ric].set_index("q"); b = p2[p2.ric == ric].set_index("q")
        opex_ex_cor = pd.to_numeric(a["Total Operating Expense"], errors="coerce") - pd.to_numeric(a["Cost of Revenue, Total"], errors="coerce").fillna(0)
        add(f"peer_{tag}_opex_ex_cor_yoy", yoy(opex_ex_cor / 1e6), target="sm_cash", source=f"LSEG TR.TotalOperatingExpense - TR.CostOfRevenueTotal, {ric}, pulled {pulled}", status="pulled", coverage=None, lag_days=40, unit="y/y pct", family="peers", licence="LSEG (derived y/y only)")
        add(f"peer_{tag}_sga_yoy", yoy(pd.to_numeric(b["Selling/General/Administrative Expense, Total"], errors="coerce") / 1e6), target="sm_cash", source=f"LSEG TR.SGAExpenseTotal {ric}, pulled {pulled}", status="pulled", coverage=None, lag_days=40, unit="y/y pct", family="peers", licence="LSEG (derived y/y only)")
        adv = pd.to_numeric(b["Advertising Expense"], errors="coerce") / 1e6
        if adv.notna().sum() >= 8:
            add(f"peer_{tag}_advertising_yoy", yoy(adv), target="sm_cash", source=f"LSEG TR.AdvertisingExpense {ric}, pulled {pulled}", status="pulled", coverage=None, lag_days=40, unit="y/y pct", family="peers", licence="LSEG (derived y/y only)")
        fte = pd.to_numeric(b["Employees - Full-Time/Full-Time Equivalents - Period End"], errors="coerce")
        if fte.notna().sum() >= 8:
            add(f"peer_{tag}_fte_yoy", yoy(fte), target="pd_cash", source=f"LSEG TR.F.EmpFTEEquivPrdEnd {ric}, pulled {pulled}", status="pulled", coverage=None, lag_days=40, unit="y/y pct", family="peers", licence="LSEG (derived y/y only)")
        else:
            log_only(f"peer_{tag}_fte_yoy", target="pd_cash", source="LSEG TR.F.EmpFTEEquivPrdEnd", status="partial", note=f"{int(fte.notna().sum())} non-null quarters; annual only", family="peers")

    # Hotel RevPAR (repo)
    pp = pd.read_csv(PROC / "predictive/02_peer_prints.csv")
    pp["q"] = pp["quarter"].str.replace("Q", "Q")  # already YYYYQn
    for col, name in [("mar_revpar_yoy", "hotel_mar_revpar_yoy"), ("hlt_revpar_yoy", "hotel_hlt_revpar_yoy")]:
        if col in pp.columns:
            add(name, pp.set_index("q")[col], target="macro", source="repo data/processed/predictive/02_peer_prints.csv (MAR/HLT prints)", status="pulled", coverage=None, lag_days=35, unit="y/y pct", family="macro")

    # Inside Airbnb supply (repo dump metrics; fixed-city median y/y of listings)
    ia = pd.read_csv(PROC / "overnight/08_ia_dump_metrics.csv", parse_dates=["dump_date"])
    ia = ia[~ia["partial_scope"].astype(bool)]; ia["q"] = ia["dump_date"].map(qlabel)
    piv = ia.groupby(["city", "q"])["listings"].mean().unstack("q")
    yy = {}
    for q in piv.columns:
        p = f"{int(q[:4]) - 1}Q{q[-1]}"
        if p in piv.columns:
            both = piv[[p, q]].dropna()
            if len(both) >= 3: yy[q] = float(((both[q] / both[p] - 1) * 100).median())
    add("ia_listings_yoy_median_city", pd.Series(yy), target="sm_cash", source="repo data/processed/overnight/08_ia_dump_metrics.csv (Inside Airbnb, CC-BY 4.0), median city y/y, >=3 cities", status="partial", coverage=None, lag_days=45, unit="y/y pct", family="supply", note="composition changes by quarter; see note 08")

    # Funds held for clients (pay-in volume proxy; also interest income base)
    add("funds_held_musd", t["funds_held_musd"], target="interest_income", source="SEC XBRL FundsHeldForClients (data/raw/xbrl/ABNB_companyfacts.json)", status="pulled", coverage=None, lag_days=40, unit="USD m", family="balance_sheet")
    # Implied yield on funds held + own cash is a derived diagnostic, not a signal (uses the target); computed in tests section.

    # Annual 10-K drivers (step series; annual, held per quarter of the fiscal year, knowable at 10-K filing)
    tk = pd.read_csv(RAW / "misc/tenk_annual_drivers.csv")
    for item, target, fam in [("employees_year_end", "pd_cash", "labour"), ("contingent_support_workers", "ops_cash", "support"), ("chargeback_expense_musd", "cor_cash", "payments"),
                              ("hosting_commitment_remaining_musd", "cor_cash", "hosting")]:
        s = tk[tk.item == item].set_index("fiscal_year")["value"]; kn = tk[tk.item == item].set_index("fiscal_year")["knowable_from"]
        qs = {f"{y}Q4": v for y, v in s.items()}; kq = {f"{y}Q4": kn[y] for y in s.index}
        add(f"tenk_{item}", pd.Series(qs), target=target, source="10-K text extraction (data/raw/filings/abnb_10k_FY*.htm), table data/raw/margin_build/04_alt_signals/misc/tenk_annual_drivers.csv", status="pulled", coverage=None, knowable=kq, unit="annual", family=fam, note="annual; placed on Q4 of the fiscal year; n too small for the quarterly test")

    # Event step dummies
    ev = pd.read_csv(RAW / "misc/events_step_dummies.csv", parse_dates=["date"])
    allq = list(t.index)
    for _, e in ev.iterrows():
        s = pd.Series({q: float(qend(q) >= e["date"]) for q in allq})
        add(f"event_{e['event_id']}_{e['cost_line']}", s, target=e["cost_line"], source=e["source"], status="pulled", coverage=None, knowable={q: e["knowable_from"] for q in allq}, unit="0/1", family="events", note=e["event"])

# ----------------------------------------------------------------------------------------------------------------- tests
SIGN = {  # (signal prefix, target) -> expected sign of r between signal y/y and target y/y
    ("rate_", "interest_income_musd"): "+", ("funds_held_musd", "interest_income_musd"): "+",
    ("emp_software", "pd_cash"): "+", ("emp_computer", "pd_cash"): "+", ("ahe_information", "pd_cash"): "+", ("eci_wages", "pd_cash"): "+", ("cpi_sf", "ga_cash"): "+", ("cpi_sf", "pd_cash"): "+",
    ("careers_open_roles", "pd_cash"): "+", ("careers_open_roles", "ga_cash"): "+", ("careers_open_roles", "sm_cash"): "+", ("glassdoor", "pd_cash"): "+", ("tenk_employees", "pd_cash"): "+",
    ("peer_bkng_fte", "pd_cash"): "+", ("peer_expe_fte", "pd_cash"): "+",
    ("emp_business_support", "ops_cash"): "+", ("ppi_insurance", "ops_cash"): "+", ("appstore_new_ratings", "ops_cash"): "+", ("trustpilot", "ops_cash"): "+", ("sitejabber", "ops_cash"): "+", ("playstore", "ops_cash"): "+",
    ("tenk_contingent", "ops_cash"): "+", ("event_E05", "ops_cash"): "-", ("event_E07", "ops_cash"): "-", ("event_E08", "ops_cash"): "-",
    ("ppi_data_hosting", "cor_cash"): "+", ("ppi_hosting", "cor_cash"): "+", ("fx_broad", "cor_cash"): "+", ("fx_usd_per_eur", "cor_cash"): "-", ("funds_held_musd", "cor_cash"): "+",
    ("event_E02", "cor_cash"): "+", ("event_E03", "cor_cash"): "+", ("event_E04", "cor_cash"): "-", ("event_E06", "cor_cash"): "-", ("event_E09", "cor_cash"): "+", ("tenk_chargeback", "cor_cash"): "+", ("tenk_hosting", "cor_cash"): "+",
    ("trends_airbnb_share", "sm_cash"): "either", ("trends_airbnb_ww", "sm_cash"): "either", ("trends_airbnb_us", "sm_cash"): "either", ("appstore_travel_rank", "sm_cash"): "either",
    ("peer_bkng_opex", "sm_cash"): "+", ("peer_expe_opex", "sm_cash"): "+", ("peer_bkng_sga", "sm_cash"): "+", ("peer_expe_sga", "sm_cash"): "+", ("peer_bkng_adv", "sm_cash"): "+", ("peer_expe_adv", "sm_cash"): "+",
    ("ia_listings", "sm_cash"): "-", ("event_E01", "sm_cash"): "either", ("event_E10", "pd_cash"): "-",
}
MACRO = ["umich_sentiment", "real_disposable_income", "real_pce", "cpi_all", "emp_accommodation", "tsa_throughput", "hotel_mar_revpar_yoy", "hotel_hlt_revpar_yoy", "initial_claims", "unemployment_rate"]
MARGIN_SIGN_MACRO = {"umich_sentiment": "+", "real_disposable_income": "+", "real_pce": "+", "cpi_all": "either", "emp_accommodation": "+", "tsa_throughput": "+", "hotel_mar_revpar_yoy": "+", "hotel_hlt_revpar_yoy": "+", "initial_claims": "-", "unemployment_rate": "-"}

def expected_sign(sig, target):
    for (pre, tg), s in SIGN.items():
        if sig.startswith(pre) and tg == target: return s
    if target == "adj_ebitda_margin_pct":
        if sig in MARGIN_SIGN_MACRO: return MARGIN_SIGN_MACRO[sig]
        # a cost-line signal with expected + on the line is expected - on margin
        for (pre, tg), s in SIGN.items():
            if sig.startswith(pre) and tg != "interest_income_musd": return {"+": "-", "-": "+", "either": "either"}.get(s, "either")
    if target in ("nights_m",): return "+"
    return "either"

def target_change(t: pd.DataFrame, col: str) -> pd.Series:
    if col == "adj_ebitda_margin_pct": return yoy(t[col], pct=False)
    return yoy(t[col])

def signal_change(name: str, s: pd.Series) -> pd.Series:
    if name.startswith("event_") or name.endswith("_yoy") or name.startswith("hotel_"): return s   # already a change / dummy
    if name.startswith("rate_"): return yoy(s, pct=False)   # rates: y/y change in pp
    if name in ("appstore_travel_rank",): return yoy(s, pct=False)
    return yoy(s)

def run_tests(t: pd.DataFrame) -> pd.DataFrame:
    rows = []
    pairs = []
    for name in SIG:
        fam = META[name]["family"]; tg = META[name]["target"]
        targets = []
        if tg == "interest_income": targets = ["interest_income_musd"]
        elif tg == "macro": targets = ["adj_ebitda_margin_pct", "nights_m", "sm_cash_per_night", "ops_cash_per_night"]
        else:
            targets = [tg]
            if tg == "cor_cash": targets += ["cor_cash_per_night", "cor_cash_pct_gbv"]
            if tg == "ops_cash": targets += ["ops_cash_per_night"]
            if tg == "sm_cash": targets += ["sm_cash_per_night", "nights_m"]
            if tg == "pd_cash" and name.startswith(("careers", "emp_", "ahe_", "eci_", "cpi_sf")): targets += ["ga_cash"]
            targets += ["adj_ebitda_margin_pct"]
        for target in dict.fromkeys(targets): pairs.append((name, target))
    full_q = [q for q in t.index if q >= "2022Q1"]; recent_q = [q for q in t.index if q >= "2024Q1"]
    for name, target in pairs:
        sc = signal_change(name, SIG[name]); tc = target_change(t, target)
        for lead in (0, 1, 2):
            x = shift_q(sc, lead)
            for win, qs in (("1Q22-2Q26", full_q), ("1Q24-2Q26", recent_q)):
                idx = [q for q in qs if q in x.index and q in tc.index and pd.notna(x[q]) and pd.notna(tc[q])]
                n = len(idx)
                if n < 4 or np.std(x[idx]) == 0 or np.std(tc[idx]) == 0:
                    r = np.nan; rw = np.nan
                else:
                    xv, yv = x[idx].values.astype(float), tc[idx].values.astype(float)
                    r = float(np.corrcoef(xv, yv)[0, 1])
                    age = np.array([(2026 - int(q[:4])) * 4 + (2 - int(q[-1])) for q in idx], dtype=float)
                    rw = wcorr(xv, yv, 0.5 ** (age / 4.0))
                # partial r controlling for volume (nights y/y for cost lines, revenue y/y for margin and interest income)
                ctrl_col = "revenue_musd" if target in ("adj_ebitda_margin_pct", "interest_income_musd") else "nights_m"
                rp = np.nan
                if n >= 6 and target != "nights_m":
                    cc = yoy(t[ctrl_col]); idx2 = [q for q in idx if q in cc.index and pd.notna(cc[q])]
                    if len(idx2) >= 6:
                        xv2, yv2, cv = x[idx2].values.astype(float), tc[idx2].values.astype(float), cc[idx2].values.astype(float)
                        A = np.column_stack([np.ones(len(cv)), cv])
                        rx = xv2 - A @ np.linalg.lstsq(A, xv2, rcond=None)[0]; ry = yv2 - A @ np.linalg.lstsq(A, yv2, rcond=None)[0]
                        if np.std(rx) > 0 and np.std(ry) > 0: rp = float(np.corrcoef(rx, ry)[0, 1])
                es = expected_sign(name, target)
                sign_ok = (es == "either") or (es == "+" and r > 0) or (es == "-" and r < 0)
                partial_ok = pd.notna(rp) and abs(rp) >= 0.5 and ((es == "either") or (es == "+" and rp > 0) or (es == "-" and rp < 0))
                verdict = "candidate" if (pd.notna(r) and abs(r) >= 0.5 and n >= 14 and sign_ok) else ("logged, not promising" if pd.notna(r) else "insufficient n")
                if win == "1Q24-2Q26" and pd.notna(r):
                    verdict = "recent-window pass" if (abs(r) >= 0.5 and sign_ok and n >= 8) else "recent-window fail"
                rows.append(dict(series=name, family=META[name]["family"], line=target, lead_q=lead, window=win, n=n, r=round(r, 3) if pd.notna(r) else np.nan,
                                 r_recency_hl4=round(rw, 3) if pd.notna(rw) else np.nan, r_partial_volume=round(rp, 3) if pd.notna(rp) else np.nan, partial_ok=bool(partial_ok),
                                 sign_expected=es, sign_ok=bool(sign_ok) if pd.notna(r) else np.nan, verdict=verdict))
    df = pd.DataFrame(rows)
    # combine: candidate_both = candidate on full window AND recent-window pass at the same lead
    key = ["series", "line", "lead_q"]
    full = df[df.window == "1Q22-2Q26"].set_index(key); rec = df[df.window == "1Q24-2Q26"].set_index(key)
    both = full["verdict"].eq("candidate") & rec["verdict"].reindex(full.index).eq("recent-window pass")
    df = df.set_index(key); df["candidate_both"] = both.reindex(df.index).fillna(False).astype(bool); df = df.reset_index()
    df.loc[df.window == "1Q24-2Q26", "candidate_both"] = df.loc[df.window == "1Q24-2Q26", ["series", "line", "lead_q"]].apply(lambda r: bool(both.get((r["series"], r["line"], r["lead_q"]), False)), axis=1)
    # candidate_ex_volume: candidate_both AND partial r (controlling for volume) keeps |r|>=0.5 with the right sign on the full window
    pk = full["partial_ok"].reindex(df.set_index(key).index).fillna(False).astype(bool).values
    df["candidate_ex_volume"] = df["candidate_both"].values & pk
    return df

def interest_income_diagnostic(t: pd.DataFrame) -> pd.DataFrame:
    """Implied annualised yield on funds held (interest income / avg funds held), vs 3m T-bill. Diagnostic for M7, not a signal test."""
    d = pd.DataFrame({"interest_income_musd": t["interest_income_musd"], "funds_held_musd": t["funds_held_musd"], "cash_musd": t["cash_musd"], "sti_musd": t["sti_musd"],
                      "tbill3m": SIG["rate_tbill3m"].reindex(t.index), "ust1y": SIG["rate_ust1y"].reindex(t.index)})
    d["earning_base_musd"] = d["funds_held_musd"] + d["cash_musd"] + d["sti_musd"]
    d["avg_earning_base_musd"] = (d["earning_base_musd"] + d["earning_base_musd"].shift(1)) / 2
    d["implied_yield_pct"] = d["interest_income_musd"] * 4 / d["avg_earning_base_musd"] * 100
    d["yield_minus_tbill_pp"] = d["implied_yield_pct"] - d["tbill3m"]
    d["yield_over_tbill_ratio"] = d["implied_yield_pct"] / d["tbill3m"]
    return d

def write_manifest():
    rows = []
    for f in sorted(RAW.rglob("*")):
        if f.is_file():
            rows.append(dict(file=str(f.relative_to(ROOT)).replace("\\", "/"), bytes=f.stat().st_size, sha256=hashlib.sha256(f.read_bytes()).hexdigest(),
                             mtime_utc=dt.datetime.fromtimestamp(f.stat().st_mtime, dt.timezone.utc).isoformat(timespec="seconds")))
    m = pd.DataFrame(rows)
    # attach URLs where known
    wb = RAW / "wayback/_wayback_manifest.csv"
    url = {}
    if wb.exists():
        w = pd.read_csv(wb).dropna(subset=["file"]); url.update({str(r["file"]).replace("\\", "/"): r["url"] for _, r in w.iterrows()})
    fm = RAW / "fred/_fred_manifest.csv"
    if fm.exists():
        for _, r in pd.read_csv(fm).iterrows(): url[f"data/raw/margin_build/04_alt_signals/fred/{r['series']}.csv"] = r["url"]
    for f in m["file"]:
        if "/tsa/tsa_" in f and f.endswith(".html"):
            y = f.split("tsa_")[-1].replace(".html", ""); url[f] = "https://www.tsa.gov/travel/passenger-volumes" + ("" if y == "current" else f"/{y}")
        if "/wayback/cdx_" in f: url[f] = "http://web.archive.org/cdx/search/cdx?url=... (see pull_wayback.py / pull log)"
        if "lseg_" in f: url[f] = "LSEG Workspace desktop API (licensed; raw not committed)"
        if "/xbrl/" in f: url[f] = "derived from data/raw/xbrl/ABNB_companyfacts.json (SEC companyfacts API)"
    m["url"] = m["file"].map(url).fillna("hand-built table; sources inside the file")
    m["licence"] = np.where(m["file"].str.contains("lseg"), "LSEG licensed, gitignored", np.where(m["file"].str.contains("wayback"), "Internet Archive capture of a public page; gitignored raw", "public"))
    m.to_csv(MAN / "04_alt_signals.csv", index=False)
    return m

def main():
    t = load_targets()
    build_signals(t)
    panel = pd.DataFrame({k: v for k, v in SIG.items()}).reindex(sorted(set().union(*[set(v.index) for v in SIG.values()]) | set(t.index)))
    panel = panel[[c for c in panel.columns]]
    panel.index.name = "quarter"
    panel = panel.loc[[q for q in panel.index if q >= "2019Q1"]]
    # targets on the right for convenience
    for c in ["cor_cash", "ops_cash", "pd_cash", "sm_cash", "ga_cash", "cor_cash_per_night", "ops_cash_per_night", "sm_cash_per_night", "cor_cash_pct_gbv", "adj_ebitda_margin_pct", "interest_income_musd", "nights_m"]:
        panel[f"target__{c}"] = t[c].reindex(panel.index)
    panel.round(4).to_csv(OUT / "04_signal_panel_quarterly.csv")
    kn = pd.DataFrame({k: v for k, v in KNOW.items()}).reindex(panel.index); kn.index.name = "quarter"
    kn.to_csv(OUT / "04_signal_knowable_from.csv")
    tests = run_tests(t); tests.to_csv(OUT / "04_signal_tests.csv", index=False)
    cat = pd.DataFrame(CAT); cat.to_csv(OUT / "04_signal_catalogue.csv", index=False)
    interest_income_diagnostic(t).round(3).to_csv(OUT / "04_interest_income_yield_diagnostic.csv")
    write_manifest()
    # summary to stdout
    full = tests[tests.window == "1Q22-2Q26"]
    print(f"series in panel: {len(SIG)}; catalogue rows: {len(cat)}; tests: {len(tests)} ({len(full)} full-window, {tests.window.eq('1Q24-2Q26').sum()} recent-window)")
    print("verdicts (full window):"); print(full.verdict.value_counts().to_string())
    print("candidate_both:"); print(tests[(tests.window == "1Q22-2Q26") & tests.candidate_both][["series", "line", "lead_q", "n", "r", "r_recency_hl4", "r_partial_volume", "candidate_ex_volume"]].to_string())
    print("candidate_ex_volume (survives both windows and the volume control):")
    print(tests[(tests.window == "1Q22-2Q26") & tests.candidate_ex_volume][["series", "line", "lead_q", "n", "r", "r_recency_hl4", "r_partial_volume"]].to_string())
    print("\ncandidates (full window only):")
    print(full[full.verdict == "candidate"].sort_values("r", key=abs, ascending=False)[["series", "line", "lead_q", "n", "r", "r_recency_hl4", "sign_expected"]].to_string())

if __name__ == "__main__":
    main()
