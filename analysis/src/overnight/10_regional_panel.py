"""Workstream 10: regional and segment decomposition.

Reads
  data/raw/letters/*.htm                                  23 shareholder letters (8-K Ex. 99.1), 4Q20..2Q26
  data/processed/overnight/10_xbrl_revenue_geography.csv  revenue by srt:StatementGeographicalAxis (built by 10_fetch_xbrl_geography.py)
  data/processed/abnb_driver_history_quarterly.csv        total nights, GBV, ADR, revenue and y/y
  data/processed/overnight/10_fx_quarterly.csv            FRED FX quarterly averages and y/y (built by 10_fetch_fx.py)
Writes
  data/processed/overnight/10_regional_quotes.csv         every regional sentence (quarter, category, sentence <=200 chars) for audit
  data/processed/overnight/10_regional_panel_quarterly.csv per-quarter regional panel with derived nights shares and the reconciliation residual
  data/processed/overnight/10_regional_revenue_xbrl.csv    quarterly (incl. derived Q4) and annual revenue by region, US vs non-US
  data/processed/overnight/10_regional_adr_fx.csv          reported vs ex-FX ADR by region from the letters, FX gap, basket-implied gap
  data/processed/overnight/10_fx_basket.csv                currency weights by region and the current y/y of each currency
  analysis/figures/overnight/10_regional_nights_growth.png, 10_regional_revenue_mix.png
Run: py -3.13 analysis/src/overnight/10_regional_panel.py

Method notes
  * Regional nights growth is numeric where the letter gives a number; otherwise the letter's qualitative bucket is mapped to a
    range (low-single digits 1-3, mid-single 4-6, high-single 7-9, low-double 10-12, mid-teens 14-16, high-teens 17-19,
    low-20s 20-23) and the midpoint is used. Raw phrase kept in *_phrase columns. 4Q22..3Q24 North America and EMEA have no
    number; they are derived so that the share-weighted sum equals reported total nights growth, split using the XBRL regional
    revenue growth differential net of the letter's regional ADR growth. Those rows are flagged basis = 'derived'.
  * Nights shares by quarter = regional revenue share (XBRL, recognised at check-in) divided by a regional ADR index, normalised.
    The ADR index is calibrated so that North America averages 30% of nights in 2025 (1Q25, 2Q25, 3Q25 letters: 'North America
    contributes approximately 30% of our Nights and Seats Booked') and ordered as the letters describe (NA highest, APAC lowest).
"""
import re, html, glob, os, json
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "data", "processed", "overnight")
FIG = os.path.join(ROOT, "analysis", "figures", "overnight")
os.makedirs(OUT, exist_ok=True); os.makedirs(FIG, exist_ok=True)

ORDER = ['4Q20','1Q21','2Q21','3Q21','4Q21','1Q22','2Q22','3Q22','4Q22','1Q23','2Q23','3Q23','4Q23','1Q24','2Q24','3Q24','4Q24','1Q25','2Q25','3Q25','4Q25','1Q26','2Q26']

# ----------------------------------------------------------------------------------------------- 1. letter text and quotes
def letter_text(path):
    raw = open(path, encoding="utf-8", errors="ignore").read()
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", raw, flags=re.S | re.I)
    t = re.sub(r"<br\s*/?>|</p>|</div>|</tr>|</li>|</h\d>", "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t).replace("\xa0", " ")
    t = re.sub(r"\s+", " ", t)
    cut = re.search(r"Forward-Looking Statements", t)
    return t[: cut.start()] if cut else t

CATS = [
    ("north_america", r"North America|\bU\.S\.|United States|Canada|Canadian"),
    ("emea", r"\bEMEA\b|Europe|Germany|France|U\.K\.|\bUK\b|Spain|Italy|Paris|Olympic|Middle East"),
    ("latin_america", r"Latin America|Brazil|Mexico|Chile|Peru|Ecuador"),
    ("asia_pacific", r"Asia Pacific|\bAPAC\b|Japan|Korea|China|India|Australia|Taiwan|Thailand|Indonesia|Philippines"),
    ("cross_border", r"cross[- ]border|international travel|inbound"),
    ("urban", r"urban"),
    ("long_term_stays", r"long-term stays?|28 (days|nights)"),
    ("expansion_markets", r"expansion markets?|core markets?"),
    ("domestic", r"domestic"),
    ("events", r"World Cup|Olympic|Euro Cup|Games"),
]
rows = []
texts = {}
for f in sorted(glob.glob(os.path.join(ROOT, "data", "raw", "letters", "*.htm"))):
    q = os.path.basename(f)[:4]
    t = letter_text(f); texts[q] = t
    for s in re.split(r"(?<=[.!?])\s+(?=[A-Z¦•])", t):
        s = s.strip()
        if len(s) < 30: continue
        cats = [c for c, p in CATS if re.search(p, s)]
        if not cats: continue
        rows.append(dict(quarter=q, categories="|".join(cats), sentence=s[:200]))
quotes = pd.DataFrame(rows)
quotes["qi"] = quotes.quarter.map({q: i for i, q in enumerate(ORDER)})
quotes = quotes.sort_values(["qi"]).drop(columns="qi")
quotes.to_csv(os.path.join(OUT, "10_regional_quotes.csv"), index=False)
print("quotes", len(quotes))

# ----------------------------------------------------------------------------------------------- 2. hand-read regional table
BUCKET = {  # phrase -> (lo, hi)
    "low-single digits": (1, 3), "low-single digit": (1, 3), "mid-single digits": (4, 6), "mid-single digit": (4, 6),
    "high-single digit": (7, 9), "low-double digits": (10, 12), "mid-teens": (14, 16), "high-teens": (17, 19),
    "low-20s": (20, 23), "approximately 20%": (19, 21),
}
def val(x):
    """numeric -> (x, x, 'numeric'); bucket phrase -> (lo, hi, 'bucket'); None -> (nan, nan, 'none')"""
    if x is None: return (np.nan, np.nan, "none")
    if isinstance(x, (int, float)): return (float(x), float(x), "numeric")
    lo, hi = BUCKET[x]; return (float(lo), float(hi), "bucket")

# (quarter): NA, EMEA, LatAm, APAC nights y/y as given in that quarter's letter; None = not given (derived below)
REG = {
 '3Q22': dict(na=20, emea=20, latam=33, apac=65, na_phrase="increasing 20% above the level achieved in the same quarter of 2021", emea_phrase="grew 20% compared to Q3 2021", latam_phrase="33% higher than Q3 2021", apac_phrase="APAC increased the most with 65% more Nights"),
 '4Q22': dict(na=None, emea=25, latam=23, apac=40, na_phrase="remained strong with continued growth; cross-border to NA +35%", emea_phrase="grew 25% compared to Q4 2021", latam_phrase="23% higher than Q4 2021", apac_phrase="40% growth compared to a year ago"),
 '1Q23': dict(na=None, emea=21, latam=22, apac=48, na_phrase="stable growth compared to the prior quarter; cross-border to NA +34%", emea_phrase="grew 21% compared to Q1 2022; ADR +8%", latam_phrase="22% higher than Q1 2022", apac_phrase="Asia Pacific once again increased the most with 48% growth"),
 '2Q23': dict(na=None, emea=None, latam=22, apac=24, na_phrase="acceleration in y/y growth compared to the prior quarter; ADR -1%", emea_phrase="hard comparison, deceleration relative to Q1 2023; ADR +8%", latam_phrase="22% higher than Q2 2022", apac_phrase="24% year-over-year growth"),
 '3Q23': dict(na=None, emea=None, latam=24, apac=27, na_phrase="modest acceleration compared to the prior quarter; ADR -1%", emea_phrase="sequential improvement in the y/y growth rate; ADR ex-FX +6%", latam_phrase="24% higher than Q3 2022", apac_phrase="sequential acceleration in y/y growth of 27%"),
 '4Q23': dict(na=None, emea=None, latam=22, apac=22, na_phrase="continued solid growth; ADR flat (-2% ex-FX and mix)", emea_phrase="stable growth compared to the prior quarter; ADR ex-FX +6%", latam_phrase="22% higher than Q4 2022", apac_phrase="increased 22% on a year-over-year basis"),
 '1Q24': dict(na=None, emea=None, latam=19, apac=21, na_phrase="domestic travel was stable; ADR +3% (flat ex-FX and mix)", emea_phrase="relative strength in non-urban and group; ADR +7% (+4% ex-FX and mix)", latam_phrase="grew 19% in Q1 2024", apac_phrase="increased 21% on a year-over-year basis"),
 '2Q24': dict(na=None, emea=None, latam=17, apac=19, na_phrase="slight acceleration of y/y growth relative to Q1 2024; ADR +4% (+1% ex-FX and mix)", emea_phrase="relatively stable y/y growth compared to the prior quarter; ADR +4% (+3%)", latam_phrase="grew 17% in Q2 2024", apac_phrase="increased 19% on a year-over-year basis"),
 '3Q24': dict(na=None, emea=None, latam=15, apac=19, na_phrase="continued growth on a y/y basis; ADR +3% (+1% ex-FX and mix)", emea_phrase="slight acceleration compared to the prior quarter, buoyed by the Paris Games; ADR +6% (+3%)", latam_phrase="grew 15% in Q3 2024", apac_phrase="increased 19% y/y, stable with the prior quarter"),
 '4Q24': dict(na="mid-single digits", emea="low-double digits", latam="low-20s", apac="low-20s", na_phrase="mid-single digits growth, an acceleration relative to Q3 2024", emea_phrase="low-double digits growth", latam_phrase="low-20s growth; domestic nights +30%", apac_phrase="low-20s growth; cross-border nights +27%"),
 '1Q25': dict(na="low-single digits", emea="mid-single digits", latam="low-20s", apac="mid-teens", na_phrase="low-single digits growth; softness Canada to U.S. late in Q1", emea_phrase="mid-single digits growth", latam_phrase="low-20s growth; Brazil origin +27%", apac_phrase="mid-teens growth; Japan domestic >20%"),
 '2Q25': dict(na="low-single digit", emea="mid-single digit", latam="high-teens", apac="mid-teens", na_phrase="low-single digit growth; U.S. destination nights accelerated each month", emea_phrase="mid-single digit growth; Germany double-digit", latam_phrase="high-teens growth; Brazil origin high-teens", apac_phrase="mid-teens growth; Japan accelerated"),
 '3Q25': dict(na="mid-single digit", emea="mid-single digit", latam="low-20s", apac="mid-teens", na_phrase="mid-single digit growth, sequential acceleration (Reserve Now Pay Later)", emea_phrase="mid-single digit growth; unfavourable Paris 2024 comparison", latam_phrase="low-20s growth; Brazil origin >20%", apac_phrase="mid-teens growth; Japan domestic +27%"),
 '4Q25': dict(na="mid-single digit", emea="high-single digit", latam="high-teens", apac="mid-teens", na_phrase="mid-single digit growth; domestic and longer lead times", emea_phrase="high-single digit growth, acceleration vs Q3 (UK, Spain, Italy)", latam_phrase="high-teens growth; Brazil >20%, Mexico high-teens", apac_phrase="mid-teens growth; India origin +50%"),
 '1Q26': dict(na="high-single digit", emea="mid-single digit", latam="high-teens", apac="high-teens", na_phrase="high-single digit growth, modest acceleration vs Q4 2025", emea_phrase="mid-single digit growth; Middle East conflict cancellations weighed", latam_phrase="high-teens growth; Brazil >20% third consecutive quarter", apac_phrase="high-teens growth; India ~50%"),
 '2Q26': dict(na="high-single digit", emea="high-single digit", latam="approximately 20%", apac="high-teens", na_phrase="high-single digit growth, highest in almost three years", emea_phrase="high-single digit growth, accelerating from Q1 2026; steady recovery from Middle East", latam_phrase="approximately 20% growth; Brazil origin >30%", apac_phrase="high-teens growth; Japan origin high-teens, India +60%"),
}
# pre-3Q22 letters give levels vs 2019, not y/y; recorded as phrases only
PRE = {
 '4Q20': dict(na_phrase="nights booked (gross) close to Q4 2019 levels", emea_phrase="most affected (lockdowns, cross-border restrictions)", latam_phrase="below 2019 levels but relatively stable", apac_phrase="recovery continues to take time"),
 '1Q21': dict(na_phrase="gross nights slightly above Q1 2019", emea_phrase="steady improvement led by U.K. and France", latam_phrase="resilience in Mexico and Brazil", apac_phrase="modest recovery in Australia and Korea"),
 '2Q21': dict(na_phrase="about 25% above Q2 2019", emea_phrase="still below Q2 2019; +85% q/q", latam_phrase="about 15% above Q2 2019", apac_phrase="depressed vs Q2 2019"),
 '3Q21': dict(na_phrase="over 10% above Q3 2019", emea_phrase="nearly recovered to 2019 levels", latam_phrase="approximately 20% above Q3 2019", apac_phrase="depressed vs Q3 2019; ex-APAC nights above 2019"),
 '4Q21': dict(na_phrase="20% above Q4 2019", emea_phrase="slightly below 2019 (Omicron)", latam_phrase="22% above Q4 2019", apac_phrase="depressed; +22% q/q; ex-APAC +8% vs 2019"),
 '1Q22': dict(na_phrase="nearly 55% above Q1 2019 and 25% above Q1 2021", emea_phrase="approximately 20% above Q1 2019", latam_phrase="about 65% above Q1 2019", apac_phrase="depressed vs Q1 2019; ex-APAC nearly 40% above 2019"),
 '2Q22': dict(na_phrase="37% above Q2 2019", emea_phrase="+11% q/q, 26% above Q2 2019", latam_phrase="42% higher than Q2 2021 and 64% above Q2 2019", apac_phrase="19% growth vs a year ago; still depressed vs 2019"),
}
# segment series from the letters (share of gross nights booked, %, or y/y growth, %)
SEG = {
 'cross_border_share_pct': {'1Q21':20,'2Q21':27,'3Q21':33,'4Q21':34,'1Q22':39,'3Q22':43,'4Q22':44,'1Q23':45,'2Q23':45,'3Q23':45,'4Q23':44,'1Q24':46},
 'cross_border_growth_pct': {'2Q22':100,'3Q22':58,'4Q22':49,'1Q23':36,'2Q23':16,'3Q23':17,'4Q23':13,'1Q24':10},
 'cross_border_to_na_growth_pct': {'4Q22':35,'1Q23':34,'2Q23':20,'3Q23':25,'4Q23':15},
 'cross_border_to_apac_growth_pct': {'1Q23':160,'2Q23':80,'4Q23':29,'1Q24':28,'2Q24':22,'3Q24':23,'4Q24':27},
 'cross_border_to_emea_growth_pct': {'2Q23':15,'3Q23':11},
 'urban_share_pct': {'1Q21':41,'2Q21':41,'3Q21':46,'4Q21':49,'1Q22':46,'2Q22':47,'3Q22':48,'4Q22':51,'1Q23':48,'2Q23':48,'3Q23':49,'4Q23':51},
 'urban_growth_pct': {'1Q22':80,'3Q22':27,'4Q22':22,'1Q23':20,'2Q23':13,'3Q23':15,'4Q23':11},
 'long_term_stay_share_pct': {'1Q21':24,'3Q21':20,'4Q21':22,'1Q22':21,'2Q22':19,'3Q22':20,'4Q22':21,'1Q23':18,'2Q23':18,'3Q23':18,'4Q23':19,'1Q24':17},
 'domestic_share_pct': {'1Q21':80,'2Q21':73},
 'na_share_of_nights_pct_disclosed': {'1Q25':30,'2Q25':30,'3Q25':30},
 'ex_na_nights_growth_pct_disclosed': {'1Q25':11},
 'latam_domestic_growth_pct': {'2Q24':24,'3Q24':21,'4Q24':30},
 'brazil_origin_growth_pct': {'4Q24':21,'1Q25':27,'2Q25':18,'3Q25':21,'4Q25':21,'1Q26':21,'2Q26':31},
 'india_origin_growth_pct': {'4Q25':50,'1Q26':50,'2Q26':60},
 'japan_domestic_growth_pct': {'1Q25':21,'3Q25':27},
 'china_outbound_growth_pct': {'3Q23':100,'4Q23':90,'1Q24':80,'4Q24':25},
 'first_time_booker_growth_pct': {'1Q26':10,'2Q26':11},
}
EXPANSION = {'1Q24':"more than double core markets",'2Q24':"significantly outperformed core",'3Q24':"more than double core",'4Q24':"more than twice core",'1Q25':"significantly outperformed core (5 quarters)",'2Q25':"about twice core (6 quarters)",'3Q25':"twice core, LTM",'4Q25':"roughly twice core",'1Q26':"roughly twice core, LTM",'2Q26':"roughly twice core, LTM; core markets US, France, UK, Australia also accelerated"}
EVENTS = {'1Q24':"Paris Olympics nights booked 5x a year ago; Euro Cup Germany ~2x",'2Q24':"July 4 week highest NA revenue week ever; Paris Olympics >400k guests",'3Q24':"Paris Games ~700k guests; EMEA acceleration",'3Q25':"EMEA faced Paris 2024 comparison",'1Q26':"World Cup: 100k+ first-time host homes in 16 cities; Milan Olympics ~200k guests; Middle East conflict ~100 bp nights headwind",'2Q26':"World Cup: 150k+ first-time host listings; NA high-single digit, highest in ~3 years; Middle East impact less than anticipated"}

# regional ADR y/y from the letters: reported and ex-FX (ex-FX-and-mix where that is what the letter gives, flagged)
ADR = {  # quarter: {region: (reported, exfx)}
 '1Q23': dict(emea=(8,None)), '2Q23': dict(na=(-1,None), emea=(8,None)), '3Q23': dict(na=(-1,None), emea=(None,6)),
 '4Q23': dict(na=(0,-2), emea=(None,6)), '1Q24': dict(na=(3,0), emea=(7,4)), '2Q24': dict(na=(4,1), emea=(4,3)),
 '3Q24': dict(na=(3,1), emea=(6,3)), '4Q24': dict(na=(3,None), emea=(6,6), latam=(-5,4), apac=(None,2)),
 '1Q25': dict(na=(2,3), emea=(2,4), latam=(-7,2), apac=(-1,3)), '2Q25': dict(na=(3,None), emea=(9,3), latam=(-3,2), apac=(2,1)),
 '3Q25': dict(na=(5,None), emea=(10,4), latam=(4,3), apac=(2,3)), '4Q25': dict(na=(5,None), emea=(12,4), latam=(9,3), apac=(2,2)),
 '1Q26': dict(na=(7,None), emea=(15,4), latam=(10,3), apac=(6,2)), '2Q26': dict(na=(7,None), emea=(7,5), latam=(9,2), apac=(1,None)),
}
GLOBAL_ADR_EXFX = {'4Q22':5,'1Q23':3,'2Q23':2,'3Q23':0.5,'4Q23':0.5,'1Q24':2,'2Q24':3,'3Q24':2,'4Q24':2,'1Q25':1,'2Q25':1,'3Q25':2,'4Q25':3,'1Q26':4,'2Q26':4}

# ----------------------------------------------------------------------------------------------- 3. XBRL revenue by region
x = pd.read_csv(os.path.join(OUT, "10_xbrl_revenue_geography.csv"))
x["start"] = pd.to_datetime(x.start); x["end"] = pd.to_datetime(x.end); x["days"] = (x.end - x.start).dt.days
GEO = {"srt:NorthAmericaMember": "na", "us-gaap:EMEAMember": "emea", "srt:LatinAmericaMember": "latam", "srt:AsiaPacificMember": "apac", "country:US": "us", "us-gaap:NonUsMember": "non_us", "country:FR": "fr"}
x["region"] = x.geo.map(GEO)
def qlabel(ts): return f"{ts.quarter}Q{str(ts.year)[2:]}"
qtr = x[x.days < 100].copy(); qtr["quarter"] = qtr.end.map(qlabel)
ytd9 = x[(x.days > 250) & (x.days < 300)].copy(); ytd9["year"] = ytd9.end.dt.year
ann = x[x.days > 300].copy(); ann["year"] = ann.end.dt.year
pq = qtr.pivot_table(index="quarter", columns="region", values="value_usd", aggfunc="first") / 1e6
p9 = ytd9.pivot_table(index="year", columns="region", values="value_usd", aggfunc="first") / 1e6
pa = ann.pivot_table(index="year", columns="region", values="value_usd", aggfunc="first") / 1e6
# derived Q4 = FY - 9M
for y in p9.index:
    if y in pa.index:
        q4 = pa.loc[y] - p9.loc[y]
        lab = f"4Q{str(y)[2:]}"
        for r in ["na", "emea", "latam", "apac", "us", "non_us"]:
            if r in q4.index and pd.notna(q4[r]) and (lab not in pq.index or pd.isna(pq.loc[lab, r]) if lab in pq.index else True):
                pq.loc[lab, r] = q4[r]
pq = pq.reindex([q for q in ORDER if q in pq.index])
rev = pq[["na", "emea", "latam", "apac", "us", "non_us"]].copy()
rev["total_regions"] = rev[["na", "emea", "latam", "apac"]].sum(axis=1, min_count=4)
for r in ["na", "emea", "latam", "apac", "us", "non_us"]:
    rev[f"{r}_share_pct"] = (rev[r] / rev[["na", "emea", "latam", "apac"]].sum(axis=1, min_count=4) * 100).round(2) if r in ["na","emea","latam","apac"] else (rev[r] / (rev["us"] + rev["non_us"]) * 100).round(2)
    rev[f"{r}_yoy_pct"] = (rev[r] / rev[r].shift(4) - 1).mul(100).round(2)
rev.index.name = "quarter"
rev_out = rev.reset_index(); rev_out.insert(1, "basis", rev_out.quarter.map(lambda q: "derived Q4 = FY - 9M YTD" if q.startswith("4Q") else "10-Q quarterly"))
annual = pa.copy(); annual.index.name = "year"
for r in ["na", "emea", "latam", "apac", "us", "non_us"]:
    if r in annual: annual[f"{r}_yoy_pct"] = (annual[r] / annual[r].shift(1) - 1).mul(100).round(2)
annual["na_share_pct"] = (annual.na / annual[["na","emea","latam","apac"]].sum(axis=1) * 100).round(2)
annual["us_share_pct"] = (annual.us / (annual.us + annual.non_us) * 100).round(2)
with open(os.path.join(OUT, "10_regional_revenue_xbrl.csv"), "w", newline="") as fh:
    fh.write("# quarterly revenue by region, USD m; source 10-Q/10-K XBRL srt:StatementGeographicalAxis (EDGAR); 4Q rows derived as FY less 9M YTD\n")
    rev_out.round(1).to_csv(fh, index=False)
    fh.write("\n# annual revenue by region and US vs non-US, USD m (10-K)\n")
    annual.round(1).reset_index().to_csv(fh, index=False)
print(annual[["na", "emea", "latam", "apac", "us", "non_us", "na_share_pct", "us_share_pct"]].round(0).to_string())

# ----------------------------------------------------------------------------------------------- 4. panel
drv = pd.read_csv(os.path.join(ROOT, "data", "processed", "abnb_driver_history_quarterly.csv")).set_index("quarter")
fxq = pd.read_csv(os.path.join(OUT, "10_fx_quarterly.csv"), header=[0, 1], index_col=0)

# ADR index calibration: nights share_r = rev share_r / idx_r, normalised. Solve idx so 2025 average NA share = 30%,
# with EMEA/LatAm/APAC relative ADR set from the letters' ordering (NA highest; APAC lowest; LatAm below EMEA).
IDX = {"na": 1.42, "emea": 0.97, "latam": 0.68, "apac": 0.59}
def nights_shares(q):
    """trailing-four-quarter revenue by region (check-in basis is strongly seasonal; bookings are not) / ADR index, normalised"""
    if q not in rev.index: return None
    i = list(rev.index).index(q); win = rev.iloc[max(0, i - 3): i + 1][["na", "emea", "latam", "apac"]].dropna()
    if len(win) == 0: return None
    tot = win.sum()
    w = {r: tot[r] / IDX[r] for r in IDX}
    s = sum(w.values()); return {r: w[r] / s for r in w}
# check calibration
s25 = pd.DataFrame([nights_shares(q) for q in ["1Q25", "2Q25", "3Q25", "4Q25"]]).mean()
print("2025 average derived nights shares:", s25.round(3).to_dict())

panel = []
for q in ORDER:
    row = dict(quarter=q)
    row["total_nights_yoy_pct"] = round(drv.loc[q, "nights_m_yoy_pct"], 2) if q in drv.index and pd.notna(drv.loc[q, "nights_m_yoy_pct"]) else np.nan
    row["total_gbv_yoy_pct"] = round(drv.loc[q, "gbv_musd_yoy_pct"], 2) if q in drv.index else np.nan
    row["total_revenue_yoy_pct"] = round(drv.loc[q, "revenue_musd_yoy_pct"], 2) if q in drv.index else np.nan
    row["global_adr_exfx_yoy_pct"] = GLOBAL_ADR_EXFX.get(q, np.nan)
    src = REG.get(q, {}); pre = PRE.get(q, {})
    for r in ["na", "emea", "latam", "apac"]:
        lo, hi, basis = val(src.get(r)) if q in REG else (np.nan, np.nan, "none")
        row[f"{r}_nights_yoy_lo"] = lo; row[f"{r}_nights_yoy_hi"] = hi
        row[f"{r}_nights_yoy_mid"] = (lo + hi) / 2 if pd.notna(lo) else np.nan
        row[f"{r}_basis"] = basis
        row[f"{r}_phrase"] = src.get(f"{r}_phrase", pre.get(f"{r}_phrase", ""))
        a = ADR.get(q, {}).get(r, (None, None))
        row[f"{r}_adr_yoy_reported_pct"] = a[0] if a[0] is not None else np.nan
        row[f"{r}_adr_yoy_exfx_pct"] = a[1] if a[1] is not None else np.nan
    sh = nights_shares(q)
    for r in ["na", "emea", "latam", "apac"]:
        row[f"{r}_nights_share_est_pct"] = round(sh[r] * 100, 1) if sh else np.nan
        row[f"{r}_revenue_musd"] = round(rev.loc[q, r], 0) if q in rev.index else np.nan
        row[f"{r}_revenue_yoy_pct"] = rev.loc[q, f"{r}_yoy_pct"] if q in rev.index else np.nan
        row[f"{r}_revenue_share_pct"] = rev.loc[q, f"{r}_share_pct"] if q in rev.index else np.nan
    row["us_revenue_musd"] = round(rev.loc[q, "us"], 0) if q in rev.index and pd.notna(rev.loc[q, "us"]) else np.nan
    row["non_us_revenue_musd"] = round(rev.loc[q, "non_us"], 0) if q in rev.index and pd.notna(rev.loc[q, "non_us"]) else np.nan
    row["us_revenue_share_pct"] = rev.loc[q, "us_share_pct"] if q in rev.index else np.nan
    for k, d in SEG.items(): row[k] = d.get(q, np.nan)
    row["expansion_market_growth_vs_core"] = EXPANSION.get(q, "")
    row["events_and_shocks"] = EVENTS.get(q, "")
    panel.append(row)
panel = pd.DataFrame(panel).set_index("quarter")

# derive NA / EMEA where missing (4Q22..3Q24) so that share-weighted sum = total; split by revenue-growth differential
for q in panel.index:
    if q not in REG: continue
    sh = nights_shares(q)
    if sh is None: continue
    tot = panel.loc[q, "total_nights_yoy_pct"]
    known = {r: panel.loc[q, f"{r}_nights_yoy_mid"] for r in ["na", "emea", "latam", "apac"]}
    miss = [r for r in known if pd.isna(known[r])]
    if not miss: continue
    rest = tot - sum(sh[r] * known[r] for r in known if r not in miss)
    if len(miss) == 1:
        panel.loc[q, f"{miss[0]}_nights_yoy_mid"] = rest / sh[miss[0]]
        panel.loc[q, f"{miss[0]}_basis"] = "derived (residual to total)"
    else:  # na and emea: blended growth b; NA = b + d*s_e, EMEA = b - d*s_n  (share-weighted), d from revenue growth net of ADR
        b = rest / (sh["na"] + sh["emea"])
        g_na = rev.loc[q, "na_yoy_pct"]; g_em = rev.loc[q, "emea_yoy_pct"]
        a_na = panel.loc[q, "na_adr_yoy_reported_pct"]; a_em = panel.loc[q, "emea_adr_yoy_reported_pct"]
        if pd.isna(a_na): a_na = panel.loc[q, "na_adr_yoy_exfx_pct"]
        if pd.isna(a_em): a_em = panel.loc[q, "emea_adr_yoy_exfx_pct"]
        diff = (g_na - (0 if pd.isna(a_na) else a_na)) - (g_em - (0 if pd.isna(a_em) else a_em))  # NA minus EMEA implied nights growth gap
        diff = float(np.clip(diff, -12, 12))
        w = sh["na"] / (sh["na"] + sh["emea"])
        panel.loc[q, "na_nights_yoy_mid"] = b + diff * (1 - w)
        panel.loc[q, "emea_nights_yoy_mid"] = b - diff * w
        panel.loc[q, "na_basis"] = "derived (residual to total; NA-EMEA gap from XBRL revenue growth net of regional ADR)"
        panel.loc[q, "emea_basis"] = panel.loc[q, "na_basis"]
    for r in miss:
        panel.loc[q, f"{r}_nights_yoy_lo"] = panel.loc[q, f"{r}_nights_yoy_mid"] - 2
        panel.loc[q, f"{r}_nights_yoy_hi"] = panel.loc[q, f"{r}_nights_yoy_mid"] + 2

# weighted-average check
for q in panel.index:
    sh = nights_shares(q)
    mids = [panel.loc[q, f"{r}_nights_yoy_mid"] for r in ["na", "emea", "latam", "apac"]]
    if sh and not any(pd.isna(m) for m in mids):
        wa = sum(sh[r] * panel.loc[q, f"{r}_nights_yoy_mid"] for r in sh)
        panel.loc[q, "weighted_avg_nights_yoy_pct"] = round(wa, 2)
        panel.loc[q, "residual_vs_total_pp"] = round(panel.loc[q, "total_nights_yoy_pct"] - wa, 2)
        panel.loc[q, "ex_na_nights_yoy_est_pct"] = round(sum(sh[r] * panel.loc[q, f"{r}_nights_yoy_mid"] for r in ["emea", "latam", "apac"]) / (1 - sh["na"]), 2)
        panel.loc[q, "na_contribution_pp"] = round(sh["na"] * panel.loc[q, "na_nights_yoy_mid"], 2)
        panel.loc[q, "emea_contribution_pp"] = round(sh["emea"] * panel.loc[q, "emea_nights_yoy_mid"], 2)
        panel.loc[q, "latam_contribution_pp"] = round(sh["latam"] * panel.loc[q, "latam_nights_yoy_mid"], 2)
        panel.loc[q, "apac_contribution_pp"] = round(sh["apac"] * panel.loc[q, "apac_nights_yoy_mid"], 2)
for r in ["na", "emea", "latam", "apac"]:
    panel[f"{r}_nights_yoy_mid"] = panel[f"{r}_nights_yoy_mid"].astype(float).round(2)
panel.reset_index().to_csv(os.path.join(OUT, "10_regional_panel_quarterly.csv"), index=False)
cols = ["total_nights_yoy_pct"] + [f"{r}_nights_yoy_mid" for r in ["na","emea","latam","apac"]] + [f"{r}_nights_share_est_pct" for r in ["na","emea","latam","apac"]] + ["weighted_avg_nights_yoy_pct","residual_vs_total_pp","ex_na_nights_yoy_est_pct"]
print(panel.loc["3Q22":, cols].to_string())

# ----------------------------------------------------------------------------------------------- 5. FX basket by region
# currency weights by region: judgement anchored on the 10-K country split (US 39% of revenue; France second country) and
# the letters' country call-outs; documented in the note. USD-per-unit y/y from FRED.
W = {
 "na":    {"USD": 0.90, "CAD": 0.08, "MXN": 0.02},
 "emea":  {"EUR": 0.62, "GBP": 0.25, "USD": 0.05, "OTHER_EUR_LINKED": 0.08},
 "latam": {"BRL": 0.45, "MXN": 0.38, "USD": 0.07, "OTHER_LATAM": 0.10},
 "apac":  {"AUD": 0.40, "JPY": 0.20, "KRW": 0.10, "INR": 0.07, "USD": 0.08, "OTHER_APAC": 0.15},
}
PROXY = {"OTHER_EUR_LINKED": "EUR", "OTHER_LATAM": "BRL", "OTHER_APAC": "AUD"}
yoy = fxq["yoy_pct"]
def basket_yoy(region, q):
    tot = 0.0
    for c, w in W[region].items():
        cc = PROXY.get(c, c)
        if cc == "USD": continue
        v = yoy.loc[q, cc] if q in yoy.index and cc in yoy.columns else np.nan
        if pd.isna(v): return np.nan
        tot += w * v
    return tot
adr_rows = []
for q in ORDER:
    for r in ["na", "emea", "latam", "apac"]:
        rep = panel.loc[q, f"{r}_adr_yoy_reported_pct"]; ex = panel.loc[q, f"{r}_adr_yoy_exfx_pct"]
        b = basket_yoy(r, q)
        adr_rows.append(dict(quarter=q, region=r, adr_yoy_reported_pct=rep, adr_yoy_exfx_pct=ex, fx_gap_pp=(rep - ex) if pd.notna(rep) and pd.notna(ex) else np.nan, basket_fx_yoy_pct=round(b, 2) if pd.notna(b) else np.nan))
adrfx = pd.DataFrame(adr_rows)
fit = adrfx.dropna(subset=["fx_gap_pp", "basket_fx_yoy_pct"])
print("\nFX gap vs basket by region:")
for r, g in fit.groupby("region"):
    if len(g) >= 3:
        slope = np.polyfit(g.basket_fx_yoy_pct, g.fx_gap_pp, 1)
        print(r, "n", len(g), "r", round(np.corrcoef(g.basket_fx_yoy_pct, g.fx_gap_pp)[0, 1], 2), "slope", round(slope[0], 2), "intercept", round(slope[1], 2))
adrfx.to_csv(os.path.join(OUT, "10_regional_adr_fx.csv"), index=False)

# basket table: weights, current y/y (3Q26 QTD to 28 Aug), 2Q26, 1Q26, and the regional weighted y/y
rows = []
latest_q = [q for q in yoy.index if q.startswith("3Q26")]
for r in W:
    for c, w in W[r].items():
        cc = PROXY.get(c, c)
        rec = dict(region=r, currency=c, proxy_series=cc if c != cc else "", weight=w, fred_id="" if cc == "USD" else {"EUR":"DEXUSEU","GBP":"DEXUSUK","BRL":"DEXBZUS","MXN":"DEXMXUS","JPY":"DEXJPUS","AUD":"DEXUSAL","KRW":"DEXKOUS","CAD":"DEXCAUS","INR":"DEXINUS"}[cc])
        for q in ["1Q26", "2Q26", "3Q26"]:
            rec[f"usd_per_unit_yoy_{q}_pct"] = 0.0 if cc == "USD" else round(yoy.loc[q, cc], 2)
        rows.append(rec)
    for q in ["1Q26", "2Q26", "3Q26"]:
        pass
basket = pd.DataFrame(rows)
summ = pd.DataFrame([dict(region=r, currency="BASKET", proxy_series="", weight=1.0, fred_id="", **{f"usd_per_unit_yoy_{q}_pct": round(basket_yoy(r, q), 2) for q in ["1Q26", "2Q26", "3Q26"]}) for r in W])
basket = pd.concat([basket, summ], ignore_index=True)
# revenue weights for a global basket
rw = {r: float(annual.loc[2025, r] / annual.loc[2025, ["na","emea","latam","apac"]].sum()) for r in ["na","emea","latam","apac"]}
glob = {q: round(sum(rw[r] * basket_yoy(r, q) for r in rw), 2) for q in ["1Q26", "2Q26", "3Q26"]}
basket = pd.concat([basket, pd.DataFrame([dict(region="global_revenue_weighted", currency="BASKET", proxy_series="", weight=1.0, fred_id="", **{f"usd_per_unit_yoy_{q}_pct": glob[q] for q in glob})])], ignore_index=True)
basket["note"] = "3Q26 = quarter-to-date average to 28 Aug 2026 vs 3Q25 average; weights are judgement (see note), USD legs carry 0 y/y"
basket.to_csv(os.path.join(OUT, "10_fx_basket.csv"), index=False)
print("\nregional FX basket y/y:", summ.to_string())
print("global revenue-weighted basket y/y:", glob, "revenue weights", {k: round(v, 3) for k, v in rw.items()})

# ----------------------------------------------------------------------------------------------- 6. figures
qs = [q for q in ORDER if q >= "3Q22" or ORDER.index(q) >= ORDER.index("3Q22")]
qs = ORDER[ORDER.index("3Q22"):]
fig, ax = plt.subplots(figsize=(11, 5))
for r, c in zip(["na", "emea", "latam", "apac"], ["#1f4e79", "#2e8b57", "#c0392b", "#8e44ad"]):
    y = panel.loc[qs, f"{r}_nights_yoy_mid"]; lo = panel.loc[qs, f"{r}_nights_yoy_lo"]; hi = panel.loc[qs, f"{r}_nights_yoy_hi"]
    ax.plot(qs, y, marker="o", color=c, label=r.upper())
    ax.fill_between(qs, lo, hi, color=c, alpha=0.12)
ax.plot(qs, panel.loc[qs, "total_nights_yoy_pct"], color="black", lw=2, ls="--", label="Total (reported)")
ax.set_ylim(0, 70); ax.set_ylabel("Nights booked y/y, %"); ax.set_title("ABNB nights growth by region (letters; band = disclosed range; 4Q22-3Q24 NA/EMEA derived)")
ax.legend(); ax.grid(alpha=0.3); plt.xticks(rotation=45)
fig.text(0.01, 0.005, "Source: Airbnb shareholder letters 3Q22-2Q26; XBRL regional revenue; Citadel-ABNB analysis", fontsize=7, color="grey")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "10_regional_nights_growth.png"), dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(10, 5))
yrs = annual.index.tolist()
bottom = np.zeros(len(yrs))
for r, c in zip(["na", "emea", "latam", "apac"], ["#1f4e79", "#2e8b57", "#c0392b", "#8e44ad"]):
    v = (annual[r] / annual[["na","emea","latam","apac"]].sum(axis=1) * 100).values
    ax.bar(yrs, v, bottom=bottom, color=c, label=r.upper()); bottom += v
ax.set_ylabel("Share of revenue, %"); ax.set_title("ABNB revenue mix by region (10-K XBRL)"); ax.legend(loc="upper right"); ax.grid(axis="y", alpha=0.3)
fig.text(0.01, 0.005, "Source: Airbnb 10-K XBRL srt:StatementGeographicalAxis; Citadel-ABNB analysis", fontsize=7, color="grey")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "10_regional_revenue_mix.png"), dpi=150); plt.close(fig)
print("done")
