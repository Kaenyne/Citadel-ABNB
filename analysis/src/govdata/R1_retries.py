"""R1: reviewer retries of every source V or P eliminated on access, plus the coverage and duplicate
claims that rest on a route, plus up to three official source classes neither survey looked at.

Workstream R, government data survey, 12 Sep 2026. Krishang Surapaneni (compiled with Claude Code).

Every probe is one function that tries a different route from the one V or P recorded (another endpoint,
the JSON or SDMX API instead of the HTML page, a data.gov mirror, a bulk file, a Wayback copy). No paid
key, no registration token. Each probe writes at most one small tidy CSV under
data/processed/govdata/R/raw/ and one row per attempt into raw/MANIFEST.csv (url, access time, status,
bytes, sha256, last period, note). Probes are independent and time-boxed; a failure is recorded, not raised.

Run: py -3.13 analysis/src/govdata/R1_retries.py [probe_name ...]
"""
from __future__ import annotations

import datetime as dt
import hashlib
import io
import json
import os
import re
import sys
import time
import traceback

import pandas as pd
import requests

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "data", "processed", "govdata", "R")
RAW = os.path.join(OUT, "raw")
os.makedirs(RAW, exist_ok=True)
MANIFEST = os.path.join(RAW, "MANIFEST.csv")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.8"}
ROWS: list[dict] = []


def log(*a):
    print(dt.datetime.now().strftime("%H:%M:%S"), *a, flush=True)


def get(url, timeout=40, **kw):
    headers = dict(UA); headers.update(kw.pop("headers", {}))
    return requests.get(url, timeout=timeout, headers=headers, **kw)


def record(source, url, status, payload=b"", cache_file="", last_period="", note="", route=""):
    row = dict(source=source, route=route, url=url, access_utc=dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
               http_status=status, payload_bytes=len(payload) if payload else 0,
               sha256=hashlib.sha256(payload).hexdigest() if payload else "", cache_file=cache_file, last_period=last_period, note=note)
    ROWS.append(row)
    log(f"  [{source}] {status} {len(payload) if payload else 0}B {note[:140]}")
    return row


def save(df: pd.DataFrame, name: str):
    p = os.path.join(RAW, name)
    df.to_csv(p, index=False)
    return "raw\\" + name


def wayback(url):
    try:
        r = get("http://archive.org/wayback/available?url=" + url, timeout=30)
        j = r.json().get("archived_snapshots", {}).get("closest", {})
        return j.get("url"), j.get("timestamp")
    except Exception as e:  # noqa: BLE001
        return None, str(e)[:80]


# ----------------------------------------------------------------------------------------------- V no access
def probe_mexico_datatur():
    src = "mexico_datatur"
    for url in ["https://www.datatur.sectur.gob.mx/SitePages/CompendioEstadistico.aspx", "https://datatur.sectur.gob.mx/SitePages/ActividadHotelera.aspx",
                "http://www.datatur.sectur.gob.mx/"]:
        try:
            r = get(url, timeout=25)
            record(src, url, r.status_code, r.content, note="reached" if r.ok else "not ok", route="direct retry, browser UA")
            if r.ok:
                return
        except Exception as e:  # noqa: BLE001
            record(src, url, type(e).__name__, note=str(e)[:120], route="direct retry, browser UA")
    wb, ts = wayback("datatur.sectur.gob.mx/SitePages/CompendioEstadistico.aspx")
    record(src, "http://archive.org/wayback/available?url=datatur.sectur.gob.mx/SitePages/CompendioEstadistico.aspx", 200 if wb else "none",
           note=f"wayback closest {ts}: {wb}" if wb else f"no wayback snapshot ({ts})", route="wayback availability")
    # datos.gob.mx CKAN mirror
    url = "https://datos.gob.mx/busca/api/3/action/package_search?q=llegada+turistas+internacionales&rows=10"
    try:
        r = get(url, timeout=30)
        j = r.json() if r.ok else {}
        names = [x.get("title") for x in j.get("result", {}).get("results", [])]
        record(src, url, r.status_code, r.content, note="ckan datasets: " + "; ".join(str(n)[:50] for n in names[:8]), route="datos.gob.mx CKAN search")
    except Exception as e:  # noqa: BLE001
        record(src, url, type(e).__name__, note=str(e)[:120], route="datos.gob.mx CKAN search")


def probe_mexico_banxico_inegi():
    src = "mexico_banxico_sie"
    # Banxico SIE public HTML tables carry a CSV export without a token on the SieInternet front end
    for url in ["https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=1&accion=consultarCuadro&idCuadro=CE84&locale=en",
                "https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?accion=consultarSeries&series=SE47180&formato=CSV"]:
        try:
            r = get(url, timeout=40)
            note = "html" if b"<html" in r.content[:500].lower() else "non-html"
            m = re.findall(rb"20\d\d/\d\d", r.content[:200000])
            record(src, url, r.status_code, r.content, note=f"{note}; periods seen {len(m)}; sample {m[-3:] if m else ''}", route="SieInternet front end (keyless)")
        except Exception as e:  # noqa: BLE001
            record(src, url, type(e).__name__, note=str(e)[:120], route="SieInternet front end")
    src = "mexico_inpc_hotel"
    url = "https://datos.gob.mx/busca/api/3/action/package_search?q=viajeros+internacionales&rows=10"
    try:
        r = get(url, timeout=30)
        j = r.json() if r.ok else {}
        res = j.get("result", {}).get("results", [])
        names = [(x.get("title"), [(rr.get("format"), rr.get("url")) for rr in x.get("resources", [])][:2]) for x in res]
        record(src, url, r.status_code, r.content, note="ckan: " + "; ".join(str(n)[:90] for n in names[:5]), route="datos.gob.mx CKAN search (EVI open data)")
    except Exception as e:  # noqa: BLE001
        record(src, url, type(e).__name__, note=str(e)[:120], route="datos.gob.mx CKAN search")


def probe_mexico_upm():
    src = "mexico_upm_boletin"
    for url in ["https://portales.segob.gob.mx/es/PoliticaMigratoria/CuadrosBOLETIN?Anual=2026&Secc=3", "http://www.politicamigratoria.gob.mx/es/PoliticaMigratoria/Boletines_Estadisticos"]:
        try:
            r = get(url, timeout=25)
            record(src, url, r.status_code, r.content, note="reached" if r.ok else "not ok", route="alternate host / http")
            if r.ok:
                return
        except Exception as e:  # noqa: BLE001
            record(src, url, type(e).__name__, note=str(e)[:120], route="alternate host / http")
    wb, ts = wayback("www.politicamigratoria.gob.mx/es/PoliticaMigratoria/CuadrosBOLETIN?Anual=2026&Secc=3")
    record(src, "wayback:politicamigratoria", 200 if wb else "none", note=f"wayback closest {ts}: {wb}" if wb else f"no snapshot ({ts})", route="wayback availability")


def probe_korea():
    src = "korea_kto_datalab"
    urls = ["https://datalab.visitkorea.or.kr/datalab/portal/main/getMainForm.do",
            "https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=1655",
            "https://kto.visitkorea.or.kr/eng/tourismStatics/keyFacts/KoreaMonthlyStatistics/eng/inout/inout.kto"]
    for url in urls:
        try:
            r = get(url, timeout=30, allow_redirects=True)
            txt = r.text if r.ok else ""
            hit = len(re.findall(r"2026", txt))
            record(src, url, r.status_code, r.content, note=f"final url {r.url[:80]}; '2026' occurrences {hit}", route="datalab / e-nara index / KTO english")
        except Exception as e:  # noqa: BLE001
            record(src, url, type(e).__name__, note=str(e)[:120], route="datalab / e-nara index / KTO english")


def probe_greece():
    src = "greece_bank_of_greece"
    for url in ["https://www.bankofgreece.gr/en/statistics/external-sector/balance-of-payments/travel-services",
                "https://www.bankofgreece.gr/RelatedDocuments/Travel_Services.xlsx"]:
        try:
            r = get(url, timeout=30)
            record(src, url, r.status_code, r.content, note="reached with browser UA" if r.ok else "blocked", route="browser UA retry")
        except Exception as e:  # noqa: BLE001
            record(src, url, type(e).__name__, note=str(e)[:120], route="browser UA retry")
    src = "greece_hcaa"
    for url in ["https://www.ypa.gr/en/profile/statistics/yearstats/", "https://www.aia.gr/company-and-business/the-company/facts-and-figures/traffic-statistics"]:
        try:
            r = get(url, timeout=30)
            record(src, url, r.status_code, r.content, note="reached" if r.ok else "blocked", route="browser UA retry / Athens airport")
        except Exception as e:  # noqa: BLE001
            record(src, url, type(e).__name__, note=str(e)[:120], route="browser UA retry / Athens airport")


def probe_eurostat_bop_travel():
    """Gap class: BoP travel credits (tourism receipts) monthly by member state, Eurostat bop_c6_m. Also the
    keyless route to the Bank of Greece travel receipts (Greece reports them to Eurostat)."""
    src = "eurostat_bop_c6_m_travel"
    geos = ["EU27_2020", "EA20", "ES", "IT", "FR", "PT", "EL", "HR", "DE", "AT", "NL", "IE", "PL"]
    base = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/bop_c6_m?format=JSON&lang=EN&freq=M&currency=MIO_EUR&bop_item=SD&sector10=S1&sectpart=S1&partner=WRL_REST&stk_flow=CRE&sinceTimePeriod=2015-01"
    url = base + "".join(f"&geo={g}" for g in geos)
    try:
        r = get(url, timeout=90)
        if not r.ok:
            record(src, url, r.status_code, r.content, note=r.text[:160], route="Eurostat JSON API")
            return
        j = r.json()
        rows = jsonstat_to_rows(j)
        df = pd.DataFrame(rows)
        if df.empty:
            record(src, url, r.status_code, r.content, note="no rows parsed", route="Eurostat JSON API")
            return
        cf = save(df, "eurostat_bop_c6_m_travel_credit_monthly.csv")
        lp = df.dropna(subset=["value"]).groupby("geo").time.max().to_dict()
        record(src, url, r.status_code, r.content, cf, max(lp.values()), note="travel credit MIO_EUR by geo; last by geo " + json.dumps(lp)[:300], route="Eurostat JSON API")
    except Exception as e:  # noqa: BLE001
        record(src, url, type(e).__name__, note=traceback.format_exc()[-200:], route="Eurostat JSON API")


def jsonstat_to_rows(j):
    """Flatten a JSON-stat 2.0 payload to rows of dimension labels plus value."""
    dims = j["id"]; sizes = j["size"]
    cats = {d: list(j["dimension"][d]["category"]["index"].keys()) if isinstance(j["dimension"][d]["category"]["index"], dict)
            else j["dimension"][d]["category"]["index"] for d in dims}
    vals = j["value"]
    rows = []
    total = 1
    for s in sizes:
        total *= s
    strides = []
    acc = 1
    for s in reversed(sizes):
        strides.insert(0, acc); acc *= s
    for k in (vals.keys() if isinstance(vals, dict) else range(len(vals))):
        idx = int(k)
        v = vals[k] if isinstance(vals, dict) else vals[idx]
        row = {}
        rem = idx
        for d, s, st in zip(dims, sizes, strides):
            i = rem // st; rem = rem % st
            row[d] = cats[d][i]
        row["value"] = v
        rows.append(row)
    return rows


def probe_minpaku():
    src = "japan_mlit_minpaku"
    idx = "https://www.mlit.go.jp/kankocho/minpaku/business/host/index.html"
    try:
        r = get(idx, timeout=40)
        links = re.findall(r'href="([^"]+\.pdf)"', r.text)
        links = [l if l.startswith("http") else ("https://www.mlit.go.jp" + l if l.startswith("/") else idx.rsplit("/", 1)[0] + "/" + l) for l in links]
        record(src, idx, r.status_code, r.content, note=f"{len(links)} pdf links; first {links[:3]}", route="host index page, pdf links")
        if not links:
            # try the site search for the periodic report page
            for alt in ["https://www.mlit.go.jp/kankocho/minpaku/business/host/reporting.html", "https://www.mlit.go.jp/kankocho/minpaku/business/host/teiki_houkoku.html"]:
                r2 = get(alt, timeout=30)
                l2 = re.findall(r'href="([^"]+\.pdf)"', r2.text) if r2.ok else []
                record(src, alt, r2.status_code, r2.content, note=f"{len(l2)} pdf links", route="periodic report page guess")
                if l2:
                    links = [l if l.startswith("http") else "https://www.mlit.go.jp" + l for l in l2]
                    break
        if not links:
            return
        import pdfplumber  # noqa: PLC0415
        cand = [l for l in links if "content" in l][:1] or links[:1]
        url = cand[0]
        r = get(url, timeout=60)
        with pdfplumber.open(io.BytesIO(r.content)) as pdf:
            text = "\n".join((p.extract_text() or "") for p in pdf.pages[:6])
        nums = re.findall(r"(20\d\d年\d+月[^\n]{0,40})", text)
        record(src, url, r.status_code, r.content, note=f"pdf parsed, {len(text)} chars; period strings {nums[:4]}", route="pdf parse (pdfplumber)")
        with open(os.path.join(RAW, "japan_minpaku_latest_report_text.txt"), "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:  # noqa: BLE001
        record(src, idx, type(e).__name__, note=traceback.format_exc()[-200:], route="host index page")


def probe_bts_fred():
    src = "bts_t100_fred_rpm"
    for sid in ["AIRRPMTSID11", "AIRRPMTSII11"]:
        for url in [f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}", f"https://fred.stlouisfed.org/data/{sid}.txt"]:
            try:
                r = get(url, timeout=60)
                if r.ok and (b"DATE" in r.content[:200] or b"observation_date" in r.content[:200] or b"VALUE" in r.content[:2000]):
                    if url.endswith(".csv"):
                        df = pd.read_csv(io.BytesIO(r.content))
                        df.columns = ["date", "value"]
                    else:
                        txt = r.text
                        body = txt[txt.index("DATE"):] if "DATE" in txt else txt
                        df = pd.read_csv(io.StringIO(body), sep=r"\s+", names=["date", "value"], skiprows=1)
                    df["value"] = pd.to_numeric(df["value"], errors="coerce")
                    df["period"] = df["date"].astype(str).str[:7]
                    cf = save(df[["period", "value"]], f"fred_{sid}_monthly.csv")
                    record(src, url, r.status_code, r.content, cf, str(df.dropna().period.max()), note=f"{sid} {len(df)} rows", route="FRED fredgraph / data txt retry")
                    break
                record(src, url, r.status_code, r.content, note="unexpected body " + r.text[:80].replace("\n", " "), route="FRED retry")
            except Exception as e:  # noqa: BLE001
                record(src, url, type(e).__name__, note=str(e)[:120], route="FRED retry")
    # BTS Socrata monthly transportation statistics (keyless)
    url = "https://data.bts.gov/resource/crem-w557.json?$limit=1&$order=date%20DESC"
    try:
        r = get(url, timeout=40)
        keys = list(r.json()[0].keys()) if r.ok and r.json() else []
        air = [k for k in keys if "airline" in k or "air_" in k]
        record(src, url, r.status_code, r.content, note=f"socrata MTS keys with air: {air[:8]}", route="data.bts.gov Socrata MTS")
        if air:
            cols = ",".join(["date"] + air[:6])
            url2 = f"https://data.bts.gov/resource/crem-w557.json?$select={cols}&$order=date&$limit=1000"
            r2 = get(url2, timeout=60)
            df = pd.DataFrame(r2.json())
            cf = save(df, "bts_mts_airline_traffic_monthly.csv")
            record(src, url2, r2.status_code, r2.content, cf, str(df.date.max())[:7], note=f"{len(df)} rows; cols {list(df.columns)[:6]}", route="data.bts.gov Socrata MTS")
    except Exception as e:  # noqa: BLE001
        record(src, url, type(e).__name__, note=str(e)[:120], route="data.bts.gov Socrata MTS")


def probe_india():
    src = "india_mot_fta"
    for url in ["https://tourism.gov.in/statistics", "https://tourism.gov.in/monthly-statistics", "https://www.tourism.gov.in/market-research-and-statistics"]:
        try:
            r = get(url, timeout=30)
            xl = re.findall(r'href="([^"]+\.(?:xlsx|xls|pdf))"', r.text) if r.ok else []
            record(src, url, r.status_code, r.content, note=f"{len(xl)} file links; sample {xl[:3]}", route="MoT statistics pages")
        except Exception as e:  # noqa: BLE001
            record(src, url, type(e).__name__, note=str(e)[:120], route="MoT statistics pages")


# ----------------------------------------------------------------------------------------------- P no access
def probe_lvcva():
    src = "lvcva_adr"
    url = "https://www.lvcva.com/research/visitor-statistics/"
    try:
        r = get(url, timeout=30)
        record(src, url, r.status_code, r.content, note="reached with browser UA" if r.ok else "blocked", route="browser UA retry")
    except Exception as e:  # noqa: BLE001
        record(src, url, type(e).__name__, note=str(e)[:120], route="browser UA retry")
    wb, ts = wayback("www.lvcva.com/research/visitor-statistics/")
    record(src, "wayback:lvcva", 200 if wb else "none", note=f"wayback {ts}: {wb}" if wb else f"no snapshot ({ts})", route="wayback availability")


def probe_singapore_hk():
    src = "singapore_stb_arr"
    for url in ["https://api-production.data.gov.sg/v2/public/api/datasets?query=hotel", "https://data.gov.sg/api/action/package_search?q=hotel"]:
        try:
            r = get(url, timeout=30)
            txt = r.text[:3000]
            titles = re.findall(r'"name"\s*:\s*"([^"]{0,80})"', txt)
            record(src, url, r.status_code, r.content, note=f"titles {titles[:6]}", route="data.gov.sg API search")
        except Exception as e:  # noqa: BLE001
            record(src, url, type(e).__name__, note=str(e)[:120], route="data.gov.sg API search")
    src = "hongkong_hktb_arr"
    for url in ["https://data.gov.hk/en-data/dataset?q=hotel+room+occupancy", "https://www.censtatd.gov.hk/api/get.php?id=650-80001&lang=en&param=N4Ig"]:
        try:
            r = get(url, timeout=30)
            n = len(re.findall(r"hotel", r.text, flags=re.I)) if r.ok else 0
            record(src, url, r.status_code, r.content, note=f"'hotel' occurrences {n}", route="data.gov.hk search / C&SD API")
        except Exception as e:  # noqa: BLE001
            record(src, url, type(e).__name__, note=str(e)[:120], route="data.gov.hk search")


# ----------------------------------------------------------------------------------------------- coverage and duplicate routes
def probe_eurostat_cp11203():
    """P21 said CP11209 is not published past 2024-12. In the coicop18 (ECOICOP v2) code list the sub-class for
    accommodation of other establishments (private short-term lets) is CP11203, not CP11209. Pull it."""
    src = "eurostat_hicp_cp11203"
    geos = ["EA", "EU27_2020", "DE", "ES", "FR", "IT", "PT", "NL", "EL", "HR", "AT", "IE", "PL", "UK", "SE", "DK", "CZ", "HU", "BE", "CH", "NO"]
    url = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_minr?format=JSON&lang=EN&unit=RCH_A&coicop18=CP11203&sinceTimePeriod=2015-01"
           + "".join(f"&geo={g}" for g in geos))
    try:
        r = get(url, timeout=90)
        if not r.ok:
            record(src, url, r.status_code, r.content, note=r.text[:200], route="Eurostat JSON API, coicop18=CP11203")
            # fall back: list the coicop18 codes under CP112
            u2 = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_minr?format=JSON&lang=EN&unit=RCH_A&geo=EA&sinceTimePeriod=2026-06&coicop18=CP112&coicop18=CP11201&coicop18=CP11202&coicop18=CP11203&coicop18=CP11209"
            r2 = get(u2, timeout=60)
            record(src, u2, r2.status_code, r2.content, note=r2.text[:200], route="Eurostat JSON API, code check")
            return
        df = pd.DataFrame(jsonstat_to_rows(r.json()))
        cf = save(df, "eurostat_hicp_cp11203_monthly.csv")
        lp = df.dropna(subset=["value"]).groupby("geo").time.max().to_dict()
        record(src, url, r.status_code, r.content, cf, max(lp.values()) if lp else "", note="CP11203 RCH_A; last by geo " + json.dumps(lp)[:400], route="Eurostat JSON API, coicop18=CP11203")
    except Exception as e:  # noqa: BLE001
        record(src, url, type(e).__name__, note=traceback.format_exc()[-200:], route="Eurostat JSON API, coicop18=CP11203")


def probe_ine_portugal():
    """V14 and P13: INE Portugal monthly nights by accommodation type (alojamento local) and ADR. Route: the
    indicator catalogue XML, then json_indicador with the discovered varcd."""
    src = "portugal_ine_alojamento_local"
    cat = "https://www.ine.pt/ine/xml_indic.jsp?opc=3&lang=EN"
    try:
        r = get(cat, timeout=60)
        txt = r.text
        ents = re.findall(r"<indicator>(.*?)</indicator>", txt, flags=re.S)
        found = []
        for e in ents:
            code = re.search(r"<varcd>(\d+)</varcd>", e)
            title = re.search(r"<title>(.*?)</title>", e, flags=re.S)
            per = re.search(r"<periodicity>(.*?)</periodicity>", e, flags=re.S)
            t = (title.group(1) if title else "").strip()
            if re.search(r"night|guest|overnight|accommodat|tourist|lodging|revpar|average daily", t, flags=re.I):
                found.append((code.group(1) if code else "", t[:100], (per.group(1) if per else "").strip()))
        record(src, cat, r.status_code, r.content, note=f"{len(ents)} indicators; tourism-like {len(found)}: " + " | ".join(f"{c} {t} [{p}]" for c, t, p in found[:12]), route="INE PT catalogue XML")
        if not found:
            # the catalogue may use different tags; dump codes near 'Dormidas'
            hits = re.findall(r"(\d{7})[^<]{0,20}</varcd>.{0,300}?(?:Dormidas|Nights|nights)", txt, flags=re.S)
            record(src, cat, r.status_code, note=f"regex fallback hits {hits[:10]}", route="INE PT catalogue XML")
        pd.DataFrame(found, columns=["varcd", "title", "periodicity"]).to_csv(os.path.join(RAW, "ine_pt_catalogue_tourism_indicators.csv"), index=False)
        monthly = [c for c, t, p in found if re.search(r"month", p, flags=re.I) and re.search(r"night|overnight|guest", t, flags=re.I)]
        for code in monthly[:4]:
            u = f"https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd={code}&lang=EN"
            r2 = get(u, timeout=60)
            if not r2.ok:
                record(src, u, r2.status_code, r2.content, note="indicator call failed", route="INE PT json_indicador")
                continue
            j = r2.json()
            rows = []
            for blk in j:
                dados = blk.get("Dados", {})
                for per, lst in dados.items():
                    for it in lst:
                        rows.append(dict(varcd=code, period=per, **{k: v for k, v in it.items() if k in ("geocod", "geodsg", "dim_3", "dim_3_t", "dim_4", "dim_4_t", "valor")}))
            df = pd.DataFrame(rows)
            cf = save(df, f"ine_pt_{code}_monthly.csv")
            record(src, u, r2.status_code, r2.content, cf, str(df.period.max()) if len(df) else "", note=f"{len(df)} rows; dims {sorted(df.get('dim_3_t', pd.Series(dtype=str)).dropna().unique()[:8].tolist()) if len(df) else ''}", route="INE PT json_indicador")
    except Exception as e:  # noqa: BLE001
        record(src, cat, type(e).__name__, note=traceback.format_exc()[-200:], route="INE PT catalogue XML")


def probe_ine_portugal_history():
    """The catalogue names 0012088 (monthly nights by establishment type, last period June 2026). The API returns one
    period per call, so the national series is assembled month by month for Portugal (Dim2=PT), 2015-01 to the last
    period, with a short pause between calls."""
    src = "portugal_ine_alojamento_local"
    rows = []
    n_ok = 0
    # the indicator answers "Dim1 not valid" before 2022-02 (checked 2019-07 and 2021-07), so the loop starts at 2022-01;
    # the endpoint intermittently returns a non-JSON body, so each period is retried up to five times
    periods = [p.strftime("%Y%m") for p in pd.period_range("2022-01", "2026-08", freq="M")]
    for per in periods:
        url = f"https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0012088&Dim1=S3A{per}&Dim2=PT&lang=EN"
        for attempt in range(5):
            try:
                r = get(url, timeout=40)
                if not r.ok:
                    time.sleep(1.5); continue
                j = r.json()
                dados = j[0].get("Dados", {}) if j else {}
                for plabel, lst in dados.items():
                    for it in lst:
                        if str(it.get("geocod")) != "PT":
                            continue
                        rows.append(dict(period=f"{per[:4]}-{per[4:]}", period_label=plabel, type_code=it.get("dim_3"), type=it.get("dim_3_t"), value=it.get("valor")))
                n_ok += 1
                break
            except Exception:  # noqa: BLE001
                time.sleep(1.5)
        time.sleep(0.4)
    df = pd.DataFrame(rows)
    if df.empty:
        record(src, "https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0012088&Dim1=S3A{yyyymm}&Dim2=PT&lang=EN", "empty", note="no rows", route="INE PT json_indicador per period")
        return
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    tidy = df.pivot_table(index="period", columns="type", values="value").reset_index()
    tidy.columns = ["period"] + [re.sub(r"[^a-z0-9]+", "_", c.lower()).strip("_") for c in tidy.columns[1:]]
    long = tidy.melt(id_vars="period", var_name="series", value_name="value").dropna()
    cf = save(long, "ine_pt_nights_by_type_monthly.csv")
    record(src, "https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0012088&Dim1=S3A{yyyymm}&Dim2=PT&lang=EN", 200, long.to_csv(index=False).encode(), cf, str(long.period.max()),
           note=f"{n_ok} monthly calls ok; series {sorted(long.series.unique())}; national (PT) nights by establishment type", route="INE PT json_indicador per period")


def probe_croatia_dzs():
    src = "croatia_evisitor_htz"
    for url in ["https://podaci.dzs.hr/en/podaci/turizam/", "https://podaci.dzs.hr/en/podaci/turizam/dolasci-i-nocenja-turista/"]:
        try:
            r = get(url, timeout=40)
            xl = re.findall(r'href="([^"]+\.(?:xlsx|xls|csv))"', r.text) if r.ok else []
            xl = [x if x.startswith("http") else "https://podaci.dzs.hr" + x for x in xl]
            tour = [x for x in xl if re.search(r"tur|nocenj|arrival|night|4-3", x, flags=re.I)]
            record(src, url, r.status_code, r.content, note=f"{len(xl)} file links, tourism-like {len(tour)}; {tour[:4]}", route="DZS open data pages")
            if tour:
                u = tour[0]
                r2 = get(u, timeout=60)
                cf = ""
                if r2.ok:
                    with open(os.path.join(RAW, "croatia_dzs_tourism_latest.bin"), "wb") as f:
                        f.write(r2.content)
                    cf = "raw\\croatia_dzs_tourism_latest.bin"
                record(src, u, r2.status_code, r2.content, cf, note="latest DZS tourism file downloaded (format inspected in R2)", route="DZS file")
                return
        except Exception as e:  # noqa: BLE001
            record(src, url, type(e).__name__, note=str(e)[:120], route="DZS open data pages")


def probe_ons_stl():
    src = "ons_stl_pilot"
    for url in ["https://api.beta.ons.gov.uk/v1/search?q=short-term+lets&limit=10",
                "https://www.ons.gov.uk/search?q=short-term+lets"]:
        try:
            r = get(url, timeout=40)
            if url.startswith("https://api"):
                j = r.json() if r.ok else {}
                items = [(it.get("description", {}).get("title"), it.get("uri"), it.get("description", {}).get("releaseDate", "")[:10]) for it in j.get("items", [])]
                record(src, url, r.status_code, r.content, note="; ".join(f"{t} {u} {d}" for t, u, d in items[:6])[:600], route="ONS search API")
            else:
                uris = re.findall(r'href="(/[^"]*short[^"]*let[^"]*)"', r.text, flags=re.I) if r.ok else []
                record(src, url, r.status_code, r.content, note=f"uris {list(dict.fromkeys(uris))[:6]}", route="ONS site search")
        except Exception as e:  # noqa: BLE001
            record(src, url, type(e).__name__, note=str(e)[:120], route="ONS search")


def probe_texas_hot():
    src = "texas_hot"
    url = "https://api.us.socrata.com/api/catalog/v1?domains=data.texas.gov&q=hotel%20occupancy%20tax&limit=15"
    try:
        r = get(url, timeout=40)
        j = r.json() if r.ok else {}
        res = [(x["resource"]["name"], x["resource"]["id"], x["resource"].get("updatedAt", "")[:10]) for x in j.get("results", [])]
        record(src, url, r.status_code, r.content, note="; ".join(f"{n} ({i}, {u})" for n, i, u in res[:10])[:700], route="Socrata catalog search")
        quarterly = [x for x in res if re.search(r"quarter", x[0], flags=re.I)]
        if quarterly:
            i = quarterly[0][1]
            u2 = f"https://data.texas.gov/resource/{i}.json?$limit=3"
            r2 = get(u2, timeout=40)
            record(src, u2, r2.status_code, r2.content, note=f"sample keys {list(r2.json()[0].keys())[:12] if r2.ok and r2.json() else ''}", route="Socrata resource sample")
    except Exception as e:  # noqa: BLE001
        record(src, url, type(e).__name__, note=str(e)[:120], route="Socrata catalog search")


# ----------------------------------------------------------------------------------------------- gap classes
def probe_bcb_brazil_travel():
    """Gap class: central bank BoP travel receipts and expenses, monthly, Banco Central do Brasil SGS API (keyless).
    Candidate codes are probed and the ones that look like monthly USD millions are kept."""
    src = "bcb_sgs_travel"
    kept = []
    for code in [22701, 22702, 22703, 23071, 23072, 23073, 22885, 22886]:
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=json&dataInicial=01/01/2015"
        try:
            r = get(url, timeout=40)
            if not r.ok:
                record(src, url, r.status_code, r.content, note=r.text[:100], route="BCB SGS API")
                continue
            j = r.json()
            df = pd.DataFrame(j)
            df["value"] = pd.to_numeric(df["valor"].str.replace(",", "."), errors="coerce")
            df["period"] = pd.to_datetime(df["data"], format="%d/%m/%Y").dt.strftime("%Y-%m")
            note = f"code {code}: {len(df)} rows, last {df.period.max()}, last value {df.value.iloc[-1]:.1f}, mean {df.value.mean():.1f}"
            record(src, url, r.status_code, r.content, note=note, route="BCB SGS API")
            kept.append(df[["period", "value"]].assign(code=code))
        except Exception as e:  # noqa: BLE001
            record(src, url, type(e).__name__, note=str(e)[:120], route="BCB SGS API")
    if kept:
        save(pd.concat(kept), "bcb_sgs_travel_candidates_monthly.csv")


def probe_bea_monthly_travel_trade():
    """Gap class: US monthly trade in services, travel exports and imports (BEA/Census FT-900 exhibit 3)."""
    src = "us_monthly_travel_trade"
    for url in ["https://www.bea.gov/sites/default/files/2026-09/trad-time-series-0726.xlsx",
                "https://www.bea.gov/sites/default/files/2026-09/trad0726.xlsx",
                "https://www.census.gov/foreign-trade/Press-Release/current_press_release/exh3.xlsx"]:
        try:
            r = get(url, timeout=60)
            if r.ok and len(r.content) > 5000:
                with open(os.path.join(RAW, os.path.basename(url)), "wb") as f:
                    f.write(r.content)
                record(src, url, r.status_code, r.content, "raw\\" + os.path.basename(url), note="xlsx saved; parsed in R2", route="BEA / Census press files")
            else:
                record(src, url, r.status_code, r.content, note="not available", route="BEA / Census press files")
        except Exception as e:  # noqa: BLE001
            record(src, url, type(e).__name__, note=str(e)[:120], route="BEA / Census press files")


def probe_heathrow_aena():
    """Gap class: airport authority monthly traffic (fast, September lands mid October)."""
    src = "airport_authority_traffic"
    for url in ["https://www.heathrow.com/company/investor-centre/reports/traffic-statistics",
                "https://www.aena.es/en/statistics/home.html"]:
        try:
            r = get(url, timeout=40)
            xl = re.findall(r'href="([^"]+\.(?:xlsx|xls|csv))"', r.text) if r.ok else []
            record(src, url, r.status_code, r.content, note=f"{len(xl)} file links; {xl[:3]}", route="airport stats pages")
        except Exception as e:  # noqa: BLE001
            record(src, url, type(e).__name__, note=str(e)[:120], route="airport stats pages")


def probe_datatur_files():
    """DATATUR answered 200 on the retry (V recorded a ConnectionError on 12 Sep). The monthly hotel monitoring zips (70
    destinations, rooms available and occupied, current month against the two prior years) and the UPM migration
    bulletins (mirrored as PDFs) are listed here and the latest hotel zip is parsed for the June 2026 reading."""
    src = "mexico_datatur"
    try:
        r = get("https://www.datatur.sectur.gob.mx/SitePages/hoteleria.aspx", timeout=40)
        mes = sorted(set(l for l in re.findall(r'href="([^"]+)"', r.text) if "MES" in l and l.endswith(".zip")))
        record(src, "https://www.datatur.sectur.gob.mx/SitePages/hoteleria.aspx", r.status_code, r.content, note=f"{len(mes)} monthly hotel monitoring zips {mes[0].rsplit('/', 1)[-1]} .. {mes[-1].rsplit('/', 1)[-1]}", route="DATATUR hoteleria page")
        import zipfile  # noqa: PLC0415
        import openpyxl  # noqa: PLC0415
        u = "https://www.datatur.sectur.gob.mx" + mes[-1]
        z = get(u, timeout=60)
        zf = zipfile.ZipFile(io.BytesIO(z.content))
        xl = [n for n in zf.namelist() if n.lower().endswith(".xlsx")][0]
        wb = openpyxl.load_workbook(io.BytesIO(zf.read(xl)), read_only=True, data_only=True)
        ws = wb["ExcelMes"]
        rows = [row for row in ws.iter_rows(values_only=True) if row[1] == "Total"]
        tot = rows[0]
        out = pd.DataFrame([dict(month=mes[-1].rsplit("/", 1)[-1][:11], measure="rooms_available", y2024=tot[2], y2025=tot[3], y2026=tot[4]),
                            dict(month=mes[-1].rsplit("/", 1)[-1][:11], measure="rooms_occupied", y2024=tot[9], y2025=tot[10], y2026=tot[11])])
        cf = save(out, "datatur_hotel_monitoring_latest_month.csv")
        yo = (float(tot[11]) / float(tot[10]) - 1) * 100
        record(src, u, z.status_code, z.content, cf, mes[-1].rsplit("/", 1)[-1][:11], note=f"70-destination hotel monitoring, total rooms occupied y/y {yo:+.1f}% (rooms available {(float(tot[4]) / float(tot[3]) - 1) * 100:+.1f}%)", route="DATATUR monthly zip")
        r2 = get("https://www.datatur.sectur.gob.mx/SitePages/upmresidencia.aspx", timeout=40)
        pdfs = sorted(set(l for l in re.findall(r'href="([^"]+)"', r2.text) if l.endswith(".pdf")))
        record("mexico_upm_boletin", "https://www.datatur.sectur.gob.mx/SitePages/upmresidencia.aspx", r2.status_code, r2.content, note=f"UPM entries by residence mirrored as {len(pdfs)} monthly PDFs, latest {pdfs[-1].rsplit('/', 1)[-1] if pdfs else ''}; 2024 onward on this mirror", route="DATATUR mirror of the UPM bulletin")
    except Exception as e:  # noqa: BLE001
        record(src, "https://www.datatur.sectur.gob.mx/SitePages/hoteleria.aspx", type(e).__name__, note=traceback.format_exc()[-200:], route="DATATUR hoteleria page")


def probe_ons_stl_dataset():
    """The ONS search found the bulletin family; the monthly dataset (guest nights, nights, stays from Airbnb, Booking
    and Expedia data) is downloaded and the UK rows kept."""
    src = "ons_stl_pilot"
    try:
        import openpyxl  # noqa: PLC0415
        page = "https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/guestnightsnightsandstaysforshorttermletsmonthlyuk"
        p = get(page, timeout=40)
        links = sorted(set(re.findall(r'href="(/file\?uri=[^"]+\.xlsx)"', p.text)))
        latest = [l for l in links if "quarter42025" in l] or links[-1:]
        u = "https://www.ons.gov.uk" + latest[0].replace("&amp;", "&")
        r = get(u, timeout=60)
        with open(os.path.join(RAW, "ons_stl_monthly_guestnights.xlsx"), "wb") as f:
            f.write(r.content)
        wb = openpyxl.load_workbook(io.BytesIO(r.content), read_only=True, data_only=True)
        out = []
        for sn, lab in [("1a", "guest_nights"), ("2a", "nights"), ("3a", "stays"), ("1b", "guest_nights_domestic"), ("1c", "guest_nights_international")]:
            rows = list(wb[sn].iter_rows(values_only=True)); hdr = rows[2]; uk = [x for x in rows if x[0] == "K02000001"][0]
            for c, v in zip(hdr[2:], uk[2:]):
                if c and v is not None:
                    out.append(dict(series=lab, period=str(c)[:7], value=float(v)))
        df = pd.DataFrame(out)
        cf = save(df, "ons_stl_uk_monthly.csv")
        n = df[df.series == "nights"].set_index("period").value
        yo = ((n / n.shift(12) - 1) * 100).dropna()
        record(src, u, r.status_code, r.content, cf, str(df.period.max()), note=f"UK platform short-term lets, monthly {df.period.min()} to {df.period.max()}; nights y/y last six months {yo.tail(6).round(1).to_dict()}; bulletin 'July 2023 to December 2025' released 24 June 2026", route="ONS dataset xlsx")
    except Exception as e:  # noqa: BLE001
        record(src, "ons dataset", type(e).__name__, note=traceback.format_exc()[-200:], route="ONS dataset xlsx")


def probe_bcb_named():
    """Gap class: central bank BoP travel receipts and expenses. The BCB open-data catalogue names the SGS codes
    (22741 receipts, 22742 expenses, personal tourism 22756 and 22757, card-based 22759 and 22760), monthly USD millions."""
    src = "bcb_sgs_travel"
    try:
        r = get("https://dadosabertos.bcb.gov.br/api/3/action/package_search?q=Viagens+mensal&rows=40", timeout=40)
        codes = {}
        for x in r.json().get("result", {}).get("results", []):
            t = x.get("title", ""); n = x.get("name", "")
            m = re.match(r"(\d+)-", n)
            if t.lower().startswith("viagens") and m:
                codes[re.sub(r"[^a-z0-9]+", "_", t.lower()).strip("_")] = int(m.group(1))
        record(src, "https://dadosabertos.bcb.gov.br/api/3/action/package_search?q=Viagens+mensal", r.status_code, r.content, note=f"{len(codes)} named travel series: {json.dumps(codes)[:500]}", route="BCB open-data catalogue")
        keep = []
        for nm, c in codes.items():
            u = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{c}/dados?formato=json&dataInicial=01/01/2015"
            rr = get(u, timeout=40)
            df = pd.DataFrame(rr.json())
            df["value"] = pd.to_numeric(df["valor"].str.replace(",", "."), errors="coerce")
            df["period"] = pd.to_datetime(df["data"], format="%d/%m/%Y").dt.strftime("%Y-%m")
            keep.append(df[["period", "value"]].assign(series=nm, code=c))
            time.sleep(0.3)
        out = pd.concat(keep)
        cf = save(out, "bcb_sgs_travel_selected_monthly.csv")
        d = out[out.series == "viagens_mensal_despesa"].set_index("period").value
        record(src, "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{code}/dados?formato=json&dataInicial=01/01/2015", 200, out.to_csv(index=False).encode(), cf, str(out.period.max()),
               note=f"{len(codes)} series, USD millions, monthly to {out.period.max()}; travel expenses (Brazilians abroad) Jul 2026 {d.iloc[-1]:.0f} vs Jul 2025 {d.iloc[-13]:.0f} ({(d.iloc[-1] / d.iloc[-13] - 1) * 100:+.1f}%)", route="BCB SGS API")
    except Exception as e:  # noqa: BLE001
        record(src, "bcb", type(e).__name__, note=traceback.format_exc()[-200:], route="BCB SGS API")


def probe_us_trade_exh3():
    """Gap class: monthly US trade in services, travel exports (inbound visitor spend). The FT-900 exhibit 3 carries 2024
    to the latest month only, so this is a reading, not a testable history (BEA's time-series file was 404 today)."""
    src = "us_monthly_travel_trade"
    try:
        import openpyxl  # noqa: PLC0415
        p = os.path.join(RAW, "exh3.xlsx")
        if not os.path.exists(p):
            r = get("https://www.census.gov/foreign-trade/Press-Release/current_press_release/exh3.xlsx", timeout=60)
            with open(p, "wb") as f:
                f.write(r.content)
        wb = openpyxl.load_workbook(p, read_only=True, data_only=True); ws = wb["3"]
        mon = {m: i + 1 for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])}
        part, year, out = "exports", None, []
        for row in ws.iter_rows(values_only=True):
            s = str(row[0]) if row[0] is not None else ""
            if "Part B" in s:
                part = "imports"
            if re.fullmatch(r"\d{4}", s.strip()):
                year = int(s.strip())
            m = s.strip().split(" ")[0]
            if m in mon and year and row[4] is not None:
                try:
                    out.append(dict(series=f"travel_{part}_sa", period=f"{year}-{mon[m]:02d}", value=float(row[4])))
                except (TypeError, ValueError):
                    pass
        df = pd.DataFrame(out)
        cf = save(df, "us_monthly_travel_trade.csv")
        e = df[df.series == "travel_exports_sa"].set_index("period").value
        yo = ((e / e.shift(12) - 1) * 100).dropna()
        record(src, "https://www.census.gov/foreign-trade/Press-Release/current_press_release/exh3.xlsx", 200, df.to_csv(index=False).encode(), cf, str(df.period.max()),
               note=f"travel exports SA USD mn, {df.period.min()} to {df.period.max()}; y/y last four months {yo.tail(4).round(1).to_dict()}; history in this file starts 2024 so no walk-forward", route="Census FT-900 exhibit 3")
    except Exception as e:  # noqa: BLE001
        record(src, "exh3", type(e).__name__, note=traceback.format_exc()[-200:], route="Census FT-900 exhibit 3")


PROBES = {
    "datatur_files": probe_datatur_files, "ons_stl_dataset": probe_ons_stl_dataset, "bcb_named": probe_bcb_named, "us_trade_exh3": probe_us_trade_exh3,
    "mexico_datatur": probe_mexico_datatur, "mexico_banxico_inegi": probe_mexico_banxico_inegi, "mexico_upm": probe_mexico_upm,
    "korea": probe_korea, "greece": probe_greece, "eurostat_bop": probe_eurostat_bop_travel, "minpaku": probe_minpaku,
    "bts_fred": probe_bts_fred, "india": probe_india, "lvcva": probe_lvcva, "singapore_hk": probe_singapore_hk,
    "eurostat_cp11203": probe_eurostat_cp11203, "ine_portugal": probe_ine_portugal, "ine_portugal_history": probe_ine_portugal_history, "croatia": probe_croatia_dzs,
    "ons_stl": probe_ons_stl, "texas_hot": probe_texas_hot, "bcb": probe_bcb_brazil_travel, "bea_trade": probe_bea_monthly_travel_trade,
    "airports": probe_heathrow_aena,
}


def main(names):
    names = names or list(PROBES)
    for n in names:
        log("probe", n)
        t0 = time.time()
        try:
            PROBES[n]()
        except Exception as e:  # noqa: BLE001
            record(n, "", type(e).__name__, note=traceback.format_exc()[-200:], route="probe crashed")
        log(f"  done {n} in {time.time() - t0:.0f}s")
        flush()


def flush():
    new = pd.DataFrame(ROWS)
    if os.path.exists(MANIFEST):
        old = pd.read_csv(MANIFEST)
        allr = pd.concat([old, new], ignore_index=True)
    else:
        allr = new
    allr = allr.drop_duplicates(subset=["source", "url", "access_utc"], keep="last")
    allr.to_csv(MANIFEST, index=False)


if __name__ == "__main__":
    main(sys.argv[1:])
