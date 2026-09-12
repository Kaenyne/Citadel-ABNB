"""V1: pull every free, keyless, machine-readable official travel VOLUME series that was
not already pulled by workstream G (see data/processed/q3nowcast/G/source_inventory.csv)
and could nowcast or corroborate Airbnb nights, total or by region.

Workstream V, government data survey, 12 Sep 2026. Krishang Surapaneni (compiled with Claude Code).

Writes small monthly or quarterly CSVs to data/processed/govdata/V/raw/ (aggregated before
saving; nothing over 5 MB is kept) and a MANIFEST.csv with url, access date, bytes, sha256,
last period and HTTP status. Blocked pulls are recorded with the exact status or exception
so the candidate survives as "no access" instead of vanishing.

All figures are SOURCED from the agency payloads unless a note says otherwise.
Run: py -3.13 analysis/src/govdata/V1_collect.py [source ...]
"""
from __future__ import annotations

import hashlib
import io
import os
import re
import sys
import time
import zipfile
from datetime import date

import pandas as pd
import requests

ACCESS_DATE = "2026-09-12"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "data", "processed", "govdata", "V")
RAW = os.path.join(OUT, "raw")
os.makedirs(RAW, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127 Safari/537.36"}
MANIFEST: list[dict] = []


def log(*a):
    print(*a, flush=True)


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def note(source, url, path, status, last_period, comment="", payload_bytes=None):
    """One manifest row. bytes = size of the payload actually downloaded (not the cache)."""
    sz = os.path.getsize(path) if path and os.path.exists(path) else 0
    MANIFEST.append(dict(source=source, url=url, access_date=ACCESS_DATE, http_status=status,
                         payload_bytes=payload_bytes if payload_bytes is not None else sz,
                         cache_file=os.path.relpath(path, OUT) if path else "", cache_bytes=sz,
                         sha256=sha(path) if path and os.path.exists(path) else "",
                         last_period=last_period, comment=comment))
    log(f"  [{status}] {source}: last {last_period} {comment[:90]}")


def get(url, timeout=90, tries=2, **kw):
    last = None
    for i in range(tries):
        try:
            r = requests.get(url, headers=UA, timeout=timeout, **kw)
            if r.status_code == 200:
                return r, 200
            last = r.status_code
        except Exception as e:  # noqa: BLE001
            last = repr(e)[:110]
        time.sleep(2 + 3 * i)
    return None, last


def save(df, fn):
    p = os.path.join(RAW, fn)
    df.to_csv(p, index=False)
    return p


def eurostat_flatten(d):
    dims, sizes = d["id"], d["size"]
    idx = {k: {vv: kk for kk, vv in d["dimension"][k]["category"]["index"].items()} for k in dims}
    rows = []
    for flat, val in d["value"].items():
        flat = int(flat)
        coords = []
        for s in reversed(sizes):
            coords.append(flat % s)
            flat //= s
        rec = {k: idx[k][c] for k, c in zip(dims, reversed(coords))}
        rec["value"] = val
        rows.append(rec)
    return pd.DataFrame(rows)


# ------------------------------------------------------------ 1. Eurostat nights, NACE split
EU_GEOS = ["EU27_2020", "ES", "IT", "FR", "PT", "EL", "HR", "DE", "NL", "AT", "IE", "PL", "DK", "SE", "CZ", "HU"]


def eurostat_nim():
    log("[eurostat_nim] tour_occ_nim, nights by NACE (I551 hotels, I552 holiday and short-stay, I553 camping), monthly")
    base = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tour_occ_nim?format=JSON&lang=EN&unit=NR&c_resid=TOTAL&sinceTimePeriod=2015-01"
    frames = []
    for nace in ["I551", "I552", "I553", "I551-I553"]:
        url = base + f"&nace_r2={nace}" + "".join(f"&geo={g}" for g in EU_GEOS)
        r, st = get(url, timeout=180)
        if r is None:
            note(f"eurostat_nim_{nace}", url, "", st, "", "FETCH FAILED")
            continue
        df = eurostat_flatten(r.json())
        df["updated"] = r.json().get("updated")
        frames.append(df)
        time.sleep(1)
    if not frames:
        return
    df = pd.concat(frames, ignore_index=True)
    df = df.rename(columns={"time": "period"})[["geo", "nace_r2", "period", "value", "updated"]].sort_values(["geo", "nace_r2", "period"])
    p = save(df, "eurostat_tour_occ_nim_monthly.csv")
    last = df.dropna(subset=["value"]).groupby(["geo", "nace_r2"])["period"].max()
    note("eurostat_tour_occ_nim", base + "&nace_r2=I552&geo=...", p, 200, str(last.max()),
         f"{df.geo.nunique()} geos x {df.nace_r2.nunique()} NACE; EU27 I552 last {last.get(('EU27_2020', 'I552'), '')}; dataset updated {df.updated.iloc[0]}",
         payload_bytes=sum(len(f) for f in frames) * 40)


def eurostat_ninat():
    log("[eurostat_ninat] tour_occ_ninat, nights by residents / non-residents, ANNUAL only (checked)")
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tour_occ_ninat?format=JSON&lang=EN&unit=NR&nace_r2=I551-I553&sinceTimePeriod=2015" + "".join(f"&geo={g}" for g in EU_GEOS)
    r, st = get(url, timeout=180)
    if r is None:
        note("eurostat_tour_occ_ninat", url, "", st, "", "FETCH FAILED")
        return
    df = eurostat_flatten(r.json()).rename(columns={"time": "period"})
    p = save(df[["geo", "c_resid", "period", "value"]], "eurostat_tour_occ_ninat_annual.csv")
    note("eurostat_tour_occ_ninat", url, p, 200, str(df.dropna(subset=["value"]).period.max()),
         "freq dimension is A only: annual series, no monthly split by residence in this table", payload_bytes=len(r.content))


def eurostat_avia():
    log("[eurostat_avia] avia_paoc, air passengers carried, monthly")
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/avia_paoc?format=JSON&lang=EN&unit=PAS&tra_meas=PAS_CRD&tra_cov=TOTAL&schedule=TOTAL&freq=M&sinceTimePeriod=2015-01" + "".join(f"&geo={g}" for g in EU_GEOS)
    r, st = get(url, timeout=180)
    if r is None:
        note("eurostat_avia_paoc", url, "", st, "", "FETCH FAILED")
        return
    df = eurostat_flatten(r.json()).rename(columns={"time": "period"})
    df = df[df.period.str.len() == 7]
    p = save(df[["geo", "period", "value"]].sort_values(["geo", "period"]), "eurostat_avia_paoc_monthly.csv")
    note("eurostat_avia_paoc", url, p, 200, str(df.dropna(subset=["value"]).period.max()),
         f"dataset updated {r.json().get('updated')}", payload_bytes=len(r.content))


# ------------------------------------------------------------ 2. Spain INE EOAP tourist apartments
def ine_eoap():
    log("[ine_eoap] Spain INE EOAP tourist-apartment travellers and overnight stays by country of residence (table 1998)")
    url = "https://servicios.ine.es/wstempus/js/EN/DATOS_TABLA/1998?nult=200"
    r, st = get(url, timeout=180)
    if r is None:
        note("ine_eoap_1998", url, "", st, "", "FETCH FAILED")
        return
    rows = []
    for s in r.json():
        for v in s.get("Data", []):
            per = v.get("FK_Periodo")
            if per is None or not (1 <= int(per) <= 12):
                continue
            rows.append(dict(name=s.get("Nombre"), year=int(v["Anyo"]), month=int(per), value=v.get("Valor")))
    df = pd.DataFrame(rows)
    df["period"] = df.year.astype(str) + "-" + df.month.map(lambda m: f"{m:02d}")
    keep = df[df.name.str.contains("Holiday apartments", regex=False) & ~df.name.str.contains("Percentage", regex=False)]
    if keep.empty:
        keep = df
    p = save(keep[["name", "period", "value"]].sort_values(["name", "period"]), "ine_eoap_1998_monthly.csv")
    note("ine_eoap_1998", url, p, 200, keep.period.max(), f"{keep.name.nunique()} national series kept of {df.name.nunique()}; operation EOAP id 239",
         payload_bytes=len(r.content))


# ------------------------------------------------------------ 3. StatCan frontier counts
STATCAN_COORDS = {
    "1.1.1": "international_travellers_total",
    "1.2.1": "nonresident_visitors_total",
    "1.2.3": "nonresident_visitors_overnight",
    "1.3.1": "us_residents_entering_total",
    "1.3.3": "us_residents_entering_overnight",
    "1.18.1": "other_country_residents_entering_total",
    "1.18.3": "other_country_residents_entering_overnight",
    "1.42.1": "canadians_returning_from_us_total",
    "1.42.3": "canadians_returning_from_us_overnight",
    "1.57.1": "canadians_returning_from_other_total",
    "1.57.3": "canadians_returning_from_other_overnight",
}


def statcan():
    log("[statcan] 24-10-0053-01 international travellers entering or returning to Canada, monthly, via the WDS coordinate API")
    url = "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromCubePidCoordAndLatestNPeriods"
    body = [{"productId": 24100053, "coordinate": c + ".0.0.0.0.0.0.0", "latestN": 140} for c in STATCAN_COORDS]
    try:
        r = requests.post(url, json=body, headers=UA, timeout=180)
        st = r.status_code
    except Exception as e:  # noqa: BLE001
        note("statcan_24100053", url, "", repr(e)[:100], "", "POST FAILED")
        return
    if st != 200:
        note("statcan_24100053", url, "", st, "", "POST FAILED")
        return
    rows = []
    for o in r.json():
        if o.get("status") != "SUCCESS":
            continue
        ob = o["object"]
        c = ".".join(ob["coordinate"].split(".")[:3])
        for pnt in ob.get("vectorDataPoint", []):
            rows.append(dict(series=STATCAN_COORDS.get(c, c), vector=ob.get("vectorId"), period=pnt["refPer"][:7], value=pnt.get("value")))
    df = pd.DataFrame(rows).sort_values(["series", "period"])
    p = save(df, "statcan_24100053_monthly.csv")
    note("statcan_24100053", url + " (productId 24100053, coordinates " + ", ".join(STATCAN_COORDS) + ")", p, 200, df.period.max(),
         f"{df.series.nunique()} series; the full-table zip is 450 MB so the coordinate API is used", payload_bytes=len(r.content))


LIIA_COORDS = {  # 24-10-0056-01 leading indicator, air, Canada total (geo member 1)
    "1.1.1": "liia_air_intl_visitors_and_returning_total",
    "1.1.3": "liia_air_intl_visitors_and_returning_overnight",
    "1.2.1": "liia_air_nonresident_visitors_total",
    "1.2.3": "liia_air_nonresident_visitors_overnight",
    "1.3.1": "liia_air_us_residents_total",
    "1.3.3": "liia_air_us_residents_overnight",
    "1.4.1": "liia_air_other_country_residents_total",
    "1.4.3": "liia_air_other_country_residents_overnight",
}


def statcan_liia():
    log("[statcan_liia] 24-10-0056-01 leading indicator of international visitors entering or returning to Canada by air (released 11 Sep 2026, to Aug 2026) and 24-10-0058-01 vehicles by licence plate")
    url = "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromCubePidCoordAndLatestNPeriods"
    # the table is DAILY: 3,300 points reaches back to about Aug 2017
    body = [{"productId": 24100056, "coordinate": c + ".0.0.0.0.0.0.0", "latestN": 3300} for c in LIIA_COORDS]
    body += [{"productId": 24100058, "coordinate": "125.65.4.0.0.0.0.0.0.0", "latestN": 3300},
             {"productId": 24100058, "coordinate": "125.66.4.0.0.0.0.0.0.0", "latestN": 3300}]
    try:
        r = requests.post(url, json=body, headers=UA, timeout=180)
        st = r.status_code
    except Exception as e:  # noqa: BLE001
        note("statcan_liia", url, "", repr(e)[:100], "", "POST FAILED")
        return
    if st != 200:
        note("statcan_liia", url, "", st, "", "POST FAILED")
        return
    rows = []
    for o in r.json():
        if o.get("status") != "SUCCESS":
            log("   failed coordinate", o)
            continue
        ob = o["object"]
        c = ".".join(ob["coordinate"].split(".")[:3])
        name = LIIA_COORDS.get(c) or {"125.65.4": "liia_land_vehicles_entering_total", "125.66.4": "liia_land_us_plated_vehicles_entering"}.get(c, c)
        for pnt in ob.get("vectorDataPoint", []):
            rows.append(dict(series=name, vector=ob.get("vectorId"), date=pnt["refPer"][:10], value=pnt.get("value")))
    dd = pd.DataFrame(rows)
    dd["value"] = pd.to_numeric(dd["value"], errors="coerce")
    dd["period"] = dd.date.str[:7]
    g = dd.groupby(["series", "period"], as_index=False).agg(vector=("vector", "first"), value=("value", "sum"), days=("date", "nunique"))
    dl = pd.to_datetime(g.period + "-01").dt.days_in_month
    g = g[g.days == dl]  # complete months only
    df = g[["series", "vector", "period", "value", "days"]].sort_values(["series", "period"])
    p = save(df, "statcan_liia_monthly.csv")
    note("statcan_liia", url + " (productIds 24100056 and 24100058, daily, summed to complete months)", p, 200, df.period.max(),
         f"{df.series.nunique()} series from {df.period.min()}; leading indicator published about 10 days after month end; Aug 2026 released 11 Sep 2026", payload_bytes=len(r.content))


# ------------------------------------------------------------ 4. Census QSS
def census_qss():
    log("[census_qss] Quarterly Services Survey NAICS 721 and 7211 revenue")
    url = "https://www.census.gov/econ_getzippedfile/?programCode=QSS"
    r, st = get(url, timeout=180)
    if r is None:
        note("census_qss", url, "", st, "", "FETCH FAILED")
        return
    z = zipfile.ZipFile(io.BytesIO(r.content))
    txt = z.read("QSS-mf.csv").decode("utf-8", "replace").replace("\r", "")

    def section(name):
        i = txt.find("\n" + name + "\n")
        j = txt.find("\n\n", i + 1)
        body = txt[i + len(name) + 2: j if j > 0 else None]
        return pd.read_csv(io.StringIO(body))

    cats = section("CATEGORIES")
    pers = section("TIME PERIODS")
    dts = section("DATA TYPES")
    data = txt.split("\nDATA\n")[1]
    d = pd.read_csv(io.StringIO(data))
    want = cats[cats.cat_code.isin(["721T", "7211T", "7212T"])]
    d = d[d.cat_idx.isin(want.cat_idx) & d.dt_idx.isin([1, 5, 9])].merge(want, on="cat_idx").merge(pers, left_on="per_idx", right_on="per_idx").merge(dts, on="dt_idx")
    d["quarter"] = d.per_name.map(lambda s: f"{s[1]}Q{s[-2:]}")
    d = d[["quarter", "per_name", "cat_code", "cat_desc", "dt_code", "is_adj", "val"]].sort_values(["cat_code", "dt_code", "is_adj", "per_idx" if "per_idx" in d else "per_name"]) if False else d[["quarter", "per_name", "cat_code", "cat_desc", "dt_code", "is_adj", "val"]]
    p = save(d, "census_qss_721_quarterly.csv")
    upd = re.search(r"DATA UPDATED ON\n([^\n]+)", txt)
    last = d.dropna(subset=["val"]).sort_values("quarter", key=lambda s: s.str[2:] + s.str[0]).quarter.iloc[-1]
    note("census_qss", url, p, 200, last, f"data updated {upd.group(1) if upd else ''}; 3Q26 advance is scheduled 19 Nov 2026",
         payload_bytes=len(r.content))


# ------------------------------------------------------------ 5. Japan: JNTO arrivals and JTA nights
def jnto():
    log("[jnto] JNTO visitor arrivals by market, monthly, from the annual-sheet workbook")
    page = "https://www.jnto.go.jp/statistics/data/visitors-statistics/"
    r, st = get(page)
    if r is None:
        note("jnto_arrivals", page, "", st, "", "landing page failed")
        return
    links = re.findall(r'href="(/statistics/data/_files/[^"]+\.xlsx)"', r.text)
    if not links:
        note("jnto_arrivals", page, "", 200, "", "no xlsx link on the landing page")
        return
    url = "https://www.jnto.go.jp" + links[0]
    r2, st = get(url, timeout=180)
    if r2 is None:
        note("jnto_arrivals", url, "", st, "", "xlsx fetch failed")
        return
    xl = pd.ExcelFile(io.BytesIO(r2.content))
    rows = []
    markets = {"総数": "total", "韓国": "korea", "中国": "china", "台湾": "taiwan", "香港": "hong_kong", "米国": "usa", "豪州": "australia", "アジア計": "asia_total", "欧州計": "europe_total", "北米計": "north_america_total"}
    for sh in xl.sheet_names:
        if not re.fullmatch(r"\d{4}", sh):
            continue
        d = xl.parse(sh, header=None)
        for i in range(len(d)):
            name = str(d.iat[i, 0]).strip()
            if name in markets:
                for m in range(12):
                    v = pd.to_numeric(d.iat[i, 2 + 2 * m], errors="coerce")
                    if pd.notna(v):
                        rows.append(dict(market=markets[name], period=f"{sh}-{m + 1:02d}", arrivals=float(v)))
    df = pd.DataFrame(rows).drop_duplicates(["market", "period"]).sort_values(["market", "period"])
    p = save(df, "jnto_arrivals_monthly.csv")
    note("jnto_arrivals", url, p, 200, df.period.max(), f"{df.market.nunique()} markets; Aug 2026 is due about 17 Sep; values for the latest two months are JNTO estimates",
         payload_bytes=len(r2.content))


def jta_nights():
    log("[jta_nights] Japan Tourism Agency accommodation survey: total and foreign guest nights, monthly")
    page = "https://www.mlit.go.jp/kankocho/tokei_hakusyo/shukuhakutokei.html"
    r, st = get(page)
    if r is None:
        note("jta_nights", page, "", st, "", "landing page failed")
        return
    links = re.findall(r'href="(/kankocho/content/\d+\.xlsx)"', r.text)
    url = None
    for l in links[:6]:
        rr, st = get("https://www.mlit.go.jp" + l, timeout=180)
        if rr is None:
            continue
        xl = pd.ExcelFile(io.BytesIO(rr.content))
        if "旧1-2" in xl.sheet_names and "1-1" in xl.sheet_names:
            url = "https://www.mlit.go.jp" + l
            break
        time.sleep(1)
    if url is None:
        note("jta_nights", page, "", 200, "", "time-series workbook not identified among the first six xlsx links")
        return
    rows = []
    era = {"平成": 1988, "令和": 2018}

    def year_of(label):
        m = re.match(r"(平成|令和)(元|\d+)年", str(label))
        if not m:
            return None
        n = 1 if m.group(2) == "元" else int(m.group(2))
        return era[m.group(1)] + n

    for sh, tag in [("旧1-2", "total_nights"), ("旧3-2", "foreign_nights"), ("1-1", "total_nights"), ("3-1", "foreign_nights")]:
        d = xl.parse(sh, header=None)
        nat = d.index[d.iloc[:, 0].astype(str).str.replace("　", "").str.strip() == "全国"]
        if not len(nat):
            continue
        row = d.loc[nat[0]]
        yr = None
        for c in range(1, d.shape[1]):
            y = year_of(d.iat[2, c])
            if y:
                yr = y
            mm = re.fullmatch(r"(\d{1,2})月", str(d.iat[3, c]).strip())
            v = pd.to_numeric(row[c], errors="coerce")
            if yr and mm and pd.notna(v):
                rows.append(dict(series=tag, period=f"{yr}-{int(mm.group(1)):02d}", value=float(v), basis="new (Jan 2026 stratification change)" if not sh.startswith("旧") else "old"))
    # first-release file (第1表) carries the newest month one release ahead of the time-series workbook
    for l in links[:6]:
        rr2, st = get("https://www.mlit.go.jp" + l, timeout=180)
        if rr2 is None:
            continue
        xl2 = pd.ExcelFile(io.BytesIO(rr2.content))
        sh = [s for s in xl2.sheet_names if s.startswith("第1表")]
        if not sh or len(xl2.sheet_names) > 8:
            continue
        d = xl2.parse(sh[0], header=None)
        for i in range(len(d)):
            m = re.match(r"令和(\d+)年(\d{1,2})月", str(d.iat[i, 0]).strip())
            if m:
                per = f"{2018 + int(m.group(1))}-{int(m.group(2)):02d}"
                tot, fo = pd.to_numeric(d.iat[i, 1], errors="coerce"), pd.to_numeric(d.iat[i, 2], errors="coerce")
                if pd.notna(tot):
                    rows.append(dict(series="total_nights", period=per, value=float(tot), basis="new, first release " + l.split("/")[-1]))
                if pd.notna(fo):
                    rows.append(dict(series="foreign_nights", period=per, value=float(fo), basis="new, first release " + l.split("/")[-1]))
        break
    df = pd.DataFrame(rows).drop_duplicates(["series", "period"]).sort_values(["series", "period"])
    p = save(df, "jta_accommodation_nights_monthly.csv")
    note("jta_nights", url, p, 200, df.period.max(),
         "national total and foreign guest nights (person-nights); Jan 2026 methodology change flagged by JTA (stratification by rooms, not employees); Jul 2026 preliminary 54.67m total is in a separate first-release file", payload_bytes=len(rr.content))


# ------------------------------------------------------------ 6. Australia ABS overseas arrivals
def abs_arrivals():
    log("[abs] ABS 3401.0 overseas arrivals, table 1, monthly")
    page = "https://www.abs.gov.au/statistics/industry/tourism-and-transport/overseas-arrivals-and-departures-australia/latest-release"
    r, st = get(page)
    if r is None:
        note("abs_340101", page, "", st, "", "landing page failed")
        return
    m = re.search(r'href="(/statistics/industry/tourism-and-transport/overseas-arrivals-and-departures-australia/[^"]+/340101\.xlsx)"', r.text)
    if not m:
        note("abs_340101", page, "", 200, "", "340101.xlsx link not found")
        return
    url = "https://www.abs.gov.au" + m.group(1)
    r2, st = get(url, timeout=180)
    if r2 is None:
        note("abs_340101", url, "", st, "", "xlsx fetch failed")
        return
    d = pd.read_excel(io.BytesIO(r2.content), sheet_name="Data1", header=None)
    hdr = d.iloc[0].astype(str)
    cols = {}
    for i, h in hdr.items():
        if "Short-term Visitors arriving" in h and i not in cols:
            cols.setdefault("st_visitors_arriving", i)
        if "Short-term Residents returning" in h:
            cols.setdefault("st_residents_returning", i)
        if "Total Arrivals" in h:
            cols.setdefault("total_arrivals", i)
    body = d[pd.to_datetime(d.iloc[:, 0], errors="coerce").notna()]
    rows = []
    for tag, i in cols.items():
        for _, rw in body.iterrows():
            v = pd.to_numeric(rw[i], errors="coerce")
            if pd.notna(v):
                rows.append(dict(series=tag, period=pd.to_datetime(rw[0]).strftime("%Y-%m"), value=float(v)))
    df = pd.DataFrame(rows).sort_values(["series", "period"])
    p = save(df, "abs_340101_arrivals_monthly.csv")
    note("abs_340101", url, p, 200, df.period.max(), "original (not SA) columns; release month in the URL", payload_bytes=len(r2.content))


# ------------------------------------------------------------ 7. Hawaii DBEDT vacation rental performance
def hawaii_vr():
    log("[hawaii_vr] DBEDT Hawaii vacation rental performance, monthly xlsx per month (rate limited: 8 s between calls)")
    base = "https://files.hawaii.gov/dbedt/economic/tourism/vacation-rental/hawaii-vacation-rental-performance-{ym}.xlsx"
    months = pd.period_range("2024-01", "2026-08", freq="M")
    rows, got, miss = [], 0, []
    for pm in months:
        ym = pm.strftime("%Y-%m")
        url = base.format(ym=ym)
        r, st = None, None
        for attempt in range(3):
            try:
                rr = requests.get(url, headers=UA, timeout=90)
                st = rr.status_code
                if st == 200:
                    r = rr
                    break
                if st == 404:
                    break
            except Exception as e:  # noqa: BLE001
                st = repr(e)[:60]
            time.sleep(15)
        time.sleep(8)
        if r is None:
            miss.append(f"{ym}:{st}")
            continue
        got += 1
        try:
            d = pd.read_excel(io.BytesIO(r.content), header=None)
        except Exception as e:  # noqa: BLE001
            miss.append(f"{ym}:parse {e!r}"[:40])
            continue
        # header row 3 holds the current and prior year labels; row 5 is the state total
        cur = int(pd.to_numeric(d.iat[3, 1], errors="coerce"))
        prv = int(pd.to_numeric(d.iat[3, 2], errors="coerce"))
        st_rows = d.index[d.iloc[:, 0].astype(str).str.contains("State of Hawai", regex=False)]
        if not len(st_rows):
            miss.append(f"{ym}:no state row")
            continue
        rw = d.loc[st_rows[0]]
        mth = ym[-2:]
        for tag, ci in [("unit_supply", 1), ("unit_demand", 4), ("occupancy", 7), ("adr", 10)]:
            for yr, off in [(cur, 0), (prv, 1)]:
                v = pd.to_numeric(rw[ci + off], errors="coerce")
                if pd.notna(v):
                    rows.append(dict(series=tag, period=f"{yr}-{mth}", value=float(v), from_report=ym))
    if not rows:
        note("hawaii_vacation_rental", base, "", "; ".join(miss[:6]), "", "no monthly file parsed")
        return
    df = pd.DataFrame(rows).sort_values(["series", "period", "from_report"]).drop_duplicates(["series", "period"], keep="last")
    p = save(df, "hawaii_vacation_rental_monthly.csv")
    note("hawaii_vacation_rental", base, p, 200, df.period.max(),
         f"{got} monthly reports parsed, each carrying current and prior-year values; missing {len(miss)}: {'; '.join(miss[:8])}; DBEDT compiles Transparent Intelligence listing data (Airbnb, Vrbo, Booking, TripAdvisor)")


# ------------------------------------------------------------ 8. NTTO country level (Canada, Mexico)
def ntto_country():
    log("[ntto_country] NTTO I-94 arrivals by country of residence: Canada and Mexico rows (G holds world regions only)")
    url = "https://www.trade.gov/sites/default/files/2024-06/Monthly%20Arrivals%202000%20to%20Present%20%E2%80%93%20Country%20of%20Residence%20%28COR%29_1.xlsx"
    r, st = get(url, timeout=240)
    if r is None:
        note("ntto_country", url, "", st, "", "FETCH FAILED")
        return
    d = pd.read_excel(io.BytesIO(r.content), sheet_name="Monthly", header=None)
    hdr = d.iloc[0]
    cols = {}
    for i, v in hdr.items():
        if hasattr(v, "year") and hasattr(v, "month"):
            cols[i] = f"{v.year}-{v.month:02d}"
        elif isinstance(v, str):
            t = v.strip().splitlines()[0] if v.strip() else ""
            if len(t) == 7 and t[4] == "-":
                cols[i] = t
    lab = d.iloc[:, 1].astype(str).str.strip().str.upper()
    rows = []
    for key in ["CANADA", "MEXICO", "TOTAL ALL COUNTRIES", "OVERSEAS", "UNITED KINGDOM", "GERMANY", "JAPAN", "BRAZIL", "AUSTRALIA", "FRANCE", "INDIA", "CHINA"]:
        idx = lab[lab == key].index
        if not len(idx):
            idx = lab[lab.str.startswith(key)].index
        if not len(idx):
            continue
        row = d.loc[idx[0]]
        for i, per in cols.items():
            v = pd.to_numeric(row[i], errors="coerce")
            if pd.notna(v):
                rows.append(dict(country=key, period=per, arrivals=float(v)))
    df = pd.DataFrame(rows).sort_values(["country", "period"])
    p = save(df[df.period >= "2015-01"], "ntto_arrivals_by_country_monthly.csv")
    note("ntto_country", url, p, 200, df.period.max(), f"{df.country.nunique()} countries kept from 2015-01; same vendor xlsx G pulled on 11 Sep, re-read for country rows",
         payload_bytes=len(r.content))


# ------------------------------------------------------------ 9. Brazil ANAC air passengers
def anac():
    log("[anac] ANAC Brazil air transport statistics, 10-year base (15.7 MB zip, 99 MB csv), aggregated to monthly domestic / international paying passengers")
    url = "https://www.gov.br/anac/pt-br/assuntos/dados-e-estatisticas/dados-estatisticos/arquivos/Base_10_anos.zip"
    r, st = get(url, timeout=600)
    if r is None:
        note("anac_brazil", url, "", st, "", "FETCH FAILED")
        return
    z = zipfile.ZipFile(io.BytesIO(r.content))
    name = z.namelist()[0]
    with z.open(name) as f:
        d = pd.read_csv(f, sep=";", encoding="latin-1", usecols=["ANO", "MÊS", "NATUREZA", "GRUPO DE VOO", "PASSAGEIROS PAGOS", "RPK"], low_memory=False)
    d["PASSAGEIROS PAGOS"] = pd.to_numeric(d["PASSAGEIROS PAGOS"], errors="coerce")
    d["RPK"] = pd.to_numeric(d["RPK"], errors="coerce")
    g = d.groupby(["ANO", "MÊS", "NATUREZA"], as_index=False)[["PASSAGEIROS PAGOS", "RPK"]].sum()
    g["period"] = g.ANO.astype(int).astype(str) + "-" + g["MÊS"].astype(int).map(lambda m: f"{m:02d}")
    g = g.rename(columns={"NATUREZA": "nature", "PASSAGEIROS PAGOS": "paying_passengers", "RPK": "rpk"})[["period", "nature", "paying_passengers", "rpk"]].sort_values(["nature", "period"])
    p = save(g, "anac_brazil_passengers_monthly.csv")
    note("anac_brazil", url, p, 200, g.period.max(), f"aggregated in memory from {len(d):,} flight-month rows; raw csv not kept", payload_bytes=len(r.content))


# ------------------------------------------------------------ 10. Colombia foreign arrivals (Migracion Colombia, datos.gov.co)
def colombia():
    log("[colombia] Migracion Colombia foreign entries by month, Socrata aggregate")
    url = "https://www.datos.gov.co/resource/96sh-4v8d.json?$select=a_o,mes,sum(total)&$group=a_o,mes&$order=a_o,mes&$limit=1000"
    r, st = get(url, timeout=120)
    if r is None:
        note("colombia_migracion", url, "", st, "", "FETCH FAILED")
        return
    mm = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}
    rows = []
    for x in r.json():
        m = mm.get(str(x.get("mes", "")).strip().lower())
        if m and x.get("a_o"):
            rows.append(dict(period=f"{int(x['a_o'])}-{m:02d}", foreign_entries=float(x["sum_total"])))
    df = pd.DataFrame(rows).sort_values("period")
    p = save(df, "colombia_foreign_entries_monthly.csv")
    note("colombia_migracion", url, p, 200, df.period.max(), "dataset 96sh-4v8d, updated 20 Aug 2026 per catalog", payload_bytes=len(r.content))


# ------------------------------------------------------------ 11. Brazil IBGE PMS accommodation volume index
def ibge_pms():
    log("[ibge_pms] IBGE monthly services survey, volume index, accommodation (alojamento) and accommodation+food")
    url = "https://apisidra.ibge.gov.br/values/t/8688/n1/all/v/7167,7168/p/all/c11046/56726/c12355/56692,106870,107071"
    r, st = get(url, timeout=180)
    if r is None:
        note("ibge_pms_8688", url, "", st, "", "FETCH FAILED")
        return
    rows = []
    for x in r.json()[1:]:
        rows.append(dict(variable=x["D2N"], activity=x["D5N"], period=f"{x['D3C'][:4]}-{x['D3C'][4:]}", value=pd.to_numeric(x["V"], errors="coerce")))
    df = pd.DataFrame(rows).sort_values(["activity", "variable", "period"])
    p = save(df, "ibge_pms_accommodation_monthly.csv")
    note("ibge_pms_8688", url, p, 200, df.period.max(), "SIDRA table 8688, volume index 2022=100, NSA (7167) and SA (7168)", payload_bytes=len(r.content))


# ------------------------------------------------------------ 12. New Zealand MBIE Accommodation Data Programme
def nz_adp():
    log("[nz_adp] MBIE Accommodation Data Programme, all measures CSV from the TEIC site (mbie.govt.nz itself is behind Incapsula)")
    url = "https://teic.mbie.govt.nz/assets/adp/ADP_All_Measures.csv"
    r, st = get(url, timeout=180)
    if r is None:
        note("nz_mbie_adp", url, "", st, "", "FETCH FAILED; www.mbie.govt.nz returned an Incapsula block page on 12 Sep 2026")
        return
    d = pd.read_csv(io.BytesIO(r.content))
    log("   columns:", list(d.columns), len(d))
    d["period"] = pd.to_datetime(d["Month"], dayfirst=True, errors="coerce").dt.strftime("%Y-%m")
    keep = ["Total guest nights", "Domestic guest nights", "International guest nights", "Stay unit nights occupied", "Guest arrivals", "Number of active establishments"]
    sub = d[(d["Area type"] == "RTO") & d.Measure.isin(keep)].copy()
    sub["Value"] = pd.to_numeric(sub["Value"], errors="coerce")
    g = sub.groupby(["period", "Property", "Measure"], as_index=False)["Value"].sum().rename(columns={"Property": "property", "Measure": "measure", "Value": "value"})
    p = save(g.sort_values(["property", "measure", "period"]), "nz_adp_national_monthly.csv")
    old = os.path.join(RAW, "nz_adp_all_measures.csv")
    if os.path.exists(old):
        os.remove(old)
    note("nz_mbie_adp", url, p, 200, g.period.max(),
         f"34.7 MB CSV aggregated to national (sum of RTOs) by property type; properties {sorted(g.property.unique())}; no holiday-home category in this file (commercial accommodation only)",
         payload_bytes=len(r.content))


# ------------------------------------------------------------ 13. FRED mirror of BTS air RPMs (one attempt each)
def fred_air():
    log("[fred_air] FRED mirrors of BTS revenue passenger miles (domestic AIRRPMTSID11, international AIRRPMTSII11)")
    for sid in ["AIRRPMTSID11", "AIRRPMTSII11"]:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
        r, st = get(url, timeout=60, tries=1)
        if r is None:
            note(f"fred_{sid}", url, "", st, "", "FETCH FAILED (fredgraph.csv timed out four times on 12 Sep 2026)")
            continue
        d = pd.read_csv(io.StringIO(r.text))
        d.columns = ["date", "value"]
        d["period"] = d.date.str[:7]
        p = save(d[["period", "value"]], f"fred_{sid}_monthly.csv")
        note(f"fred_{sid}", url, p, 200, d.period.max(), "BTS T-100 derived", payload_bytes=len(r.content))


# ------------------------------------------------------------ 14. Blocked or out-of-scope candidates, probed 12 Sep 2026
BLOCKED = [
    ("mexico_datatur", "https://www.datatur.sectur.gob.mx/SitePages/CompendioEstadistico.aspx", "ConnectionError (max retries, https and http) on 12 Sep 2026", "no access"),
    ("mexico_banxico_sie", "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SE47180/datos", "HTTP 400 without a token; the SIE API needs a free registered token", "no access (free registration wall)"),
    ("mexico_upm_boletin", "https://www.politicamigratoria.gob.mx/es/PoliticaMigratoria/CuadrosBOLETIN?Anual=2026&Secc=3", "ConnectionError (max retries) on 12 Sep 2026", "no access"),
    ("korea_kto_datalab", "https://kto.visitkorea.or.kr/eng/tourismStatics/keyFacts/KoreaMonthlyStatistics.kto", "302 to https://knto.or.kr/eng/index; the monthly xlsx sits behind the datalab login and JS", "no access"),
    ("italy_istat_sdmx", "https://esploradati.istat.it/SDMXWS/rest/dataflow/IT1", "ReadTimeout at 90 s and HTTP 400 on a bare data call; Italy taken from Eurostat tour_occ_nim geo=IT instead", "duplicate of Eurostat IT"),
    ("greece_bank_of_greece", "https://www.bankofgreece.gr/en/statistics/external-sector/balance-of-payments/travel-services", "HTTP 403 to fetchers; Greece taken from Eurostat tour_occ_nim geo=EL", "no access"),
    ("greece_hcaa", "https://www.ypa.gr/en/profile/statistics/yearstats/", "HTTP 403", "no access"),
    ("croatia_evisitor_htz", "https://www.htz.hr/en-GB/tourism-in-numbers/arrivals-and-overnights", "HTTP 404 on both language paths; podaci.dzs.hr tourism page has no machine-readable link; Croatia taken from Eurostat geo=HR", "duplicate of Eurostat HR"),
    ("france_insee_bdm", "https://api.insee.fr/series/BDM/V1/dataflow/FR1/all", "API answers keyless (200) but no dataflow named for hotel or other-accommodation occupancy was found in the 204 KB dataflow list; France taken from Eurostat geo=FR", "duplicate of Eurostat FR"),
    ("portugal_ine_alojamento_local", "https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0008519&lang=EN", "HTTP 500 on the guessed indicator codes 0008519 and 0008537 (the API works: 0011000 returns 200), code for the alojamento local nights series not resolved in the time box; Portugal taken from Eurostat geo=PT", "duplicate of Eurostat PT"),
    ("uk_ons_ott", "https://www.ons.gov.uk/peoplepopulationandcommunity/leisureandtourism/datasets/overseastravelandtourism", "200; the only current file is the annual 2019 to 2023 workbook released 17 May 2024; the monthly series is discontinued (already in G)", "no coverage"),
    ("japan_mlit_minpaku", "https://www.mlit.go.jp/kankocho/minpaku/", "200 landing; the bimonthly private-lodging results are PDF only (no xlsx or csv on the site map)", "no access (PDF only)"),
    ("scotland_stl_licensing", "https://www.gov.scot/publications/?term=short-term+lets+licensing+statistics", "200 search page, no matching publication link; the statistics are licence application counts (supply), quarterly from Oct 2023", "wrong asset class (licence counts, not stays)"),
    ("wales_stl", "https://www.gov.wales/", "no short-term let statistical series exists yet (licensing scheme not live)", "no coverage"),
    ("nyc_ose_registry", "https://www.nyc.gov/site/specialenforcement/registration-law/registration-data.page", "HTTP 404 on the registration-data page; the registry is a count of registered hosts (supply), not stays", "wrong asset class (registry counts)"),
    ("texas_hot", "https://data.texas.gov/api/catalog/v1?q=hotel%20occupancy%20tax", "200; datasets are annual local HOT reporting 2022 to 2025 by municipality; no monthly or quarterly STR series", "no coverage"),
    ("florida_dbpr_vacation_rental", "https://www2.myfloridalicense.com/", "not probed within the time box; DBPR publishes licence counts (supply), not stays", "wrong asset class (licence counts)"),
    ("bts_t100", "https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FIM", "200 but a form-gated download (no direct file URL); PREZIP path returned 404; FRED mirror timed out; TSA daily throughput already tested in G", "no access"),
    ("japan_immigration_moj", "https://www.moj.go.jp/isa/policies/statistics/toukei_ichiran_nyukan.html", "not pulled: JNTO arrivals are compiled from the same immigration counts", "duplicate of JNTO"),
    ("india_mot_fta", "https://tourism.gov.in/", "not probed within the time box; monthly foreign tourist arrivals are PIB press releases (PDF)", "no access (PDF only)"),
    ("statcan_24100045", "https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata (productId 24100045)", "200; Canadian resident trips by destination, quarterly, cube end 2025-10 (released 29 May 2026), so no 2026 data", "no coverage"),
]


def blocked():
    for src, url, why, verdict in BLOCKED:
        note(src, url, "", why.split(";")[0][:60], "", f"{verdict}: {why}")


def main():
    which = sys.argv[1:] or ["eurostat_nim", "eurostat_ninat", "eurostat_avia", "ine_eoap", "statcan", "statcan_liia", "census_qss", "jnto", "jta_nights",
                             "abs", "hawaii_vr", "ntto_country", "anac", "colombia", "ibge_pms", "nz_adp", "fred_air", "blocked"]
    fns = dict(eurostat_nim=eurostat_nim, eurostat_ninat=eurostat_ninat, eurostat_avia=eurostat_avia, ine_eoap=ine_eoap, statcan=statcan, statcan_liia=statcan_liia,
               census_qss=census_qss, jnto=jnto, jta_nights=jta_nights, abs=abs_arrivals, hawaii_vr=hawaii_vr, ntto_country=ntto_country,
               anac=anac, colombia=colombia, ibge_pms=ibge_pms, nz_adp=nz_adp, fred_air=fred_air, blocked=blocked)
    for w in which:
        try:
            fns[w]()
        except Exception as e:  # noqa: BLE001
            log(f"  !! {w} raised {e!r}")
            note(w, "", "", "exception", "", f"collector raised {e!r}"[:200])
    inv = pd.DataFrame(MANIFEST)
    p = os.path.join(RAW, "MANIFEST.csv")
    if os.path.exists(p):
        old = pd.read_csv(p)
        inv = pd.concat([old[~old.source.isin(inv.source)], inv], ignore_index=True)
    inv.to_csv(p, index=False)
    log(f"\nwrote {p} ({len(inv)} rows)")
    print(inv[["source", "http_status", "last_period", "cache_bytes"]].to_string(index=False))


if __name__ == "__main__":
    main()
