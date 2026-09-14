"""
WS-P step 1: collect official travel PRICE series worldwide that could nowcast or corroborate
Airbnb ADR (reported y/y, ex-FX y/y, the like-for-like pricing residual, regional ex-FX ADR).

Every pull is recorded in data/processed/govdata/P/raw/MANIFEST.csv (url, access date, http
status, bytes, sha256, last period). Blocked or record-only candidates get a status probe row so
the reviewer can see the exact response. Raw caches are small tidy CSVs; the Hawaii DBEDT xlsx
and pdf vintages are cached in the session scratchpad (not committed) and reduced to one CSV.

Pulled here (all keyless):
  eurostat_hicp      prc_hicp_minr, ECOICOP v2 CP112 accommodation services and the 5-digit
                     sub-items CP11201 hotels, CP11202 holiday centres/camping/hostels,
                     CP11209 other accommodation services; all geos; RCH_A and I15; 2015-01 on
  eurostat_sppi      sts_sepp_q services producer prices NACE I55 accommodation; all geos;
                     PCH_SM y/y and I21 index; 2015-Q1 on
  ine_es             INE Spain: 1989 holiday-dwellings price index (IPAP/HDPI), 2007 rural
                     tourism accommodation price index, 1990 campsite price index, 2058 hotel
                     ADR national by category, 2056 hotel RevPAR national; last 150 months
  bls                PPI 721110 hotels and motels, PPI 7211 traveler accommodation, CPI SEHB02
                     other lodging away from home incl hotels and motels (NSA and SA)
  statcan            CPI traveller accommodation, Canada, vector v41691191, monthly
  abs                CPI quarterly index for 30033 holiday travel and accommodation, 40101
                     domestic, 40102 international; plus the monthly CPI_M for the same items
  ibge               IPCA item 7201090 hospedagem (hotel), monthly and 12-month rate; tables
                     7060 (2020 on) and 1419 (2012-2019)
  fred_bea           BEA NIPA 4.2.4 price indexes, exports of travel (B646RG3Q086SBEA) and
                     imports of travel (B647RG3Q086SBEA), quarterly, via FRED csv
  ons                UK CPI index 11.2 accommodation services (d7cx), 11.2.0.1 hotels (l7ie),
                     11.2.0.3 other establishments (l7ik), 11.2 annual rate (d7hb)
  hawaii_dbedt       Hawaii vacation rental performance report (Transparent / Lighthouse data),
                     monthly unit supply, demand, occupancy and ADR, statewide and by county;
                     xlsx vintages 2024-01 to 2026-07, pdf vintages 2019-09 to 2023-12
  japan_estat        Japan CPI 2025-base item index, hotel charges (宿泊料), Japan, monthly
  nz_statsnz         Stats NZ CPI June 2026 quarter index numbers csv, accommodation classes

Record-only (probed, not pulled; reason in the manifest note): Portugal INE, Mexico INEGI and
Banxico (token walls), StatCan TASPI (terminated 2019), LVCVA (403), Singapore STB and Hong
Kong HKTB (dashboards/login), MBIE ADP (no price measure), Croatia eVisitor and MLIT minpaku
(volume only), lodging-tax collections (dollars, no nights), Italy and France tourist tax.

Run: py -3.13 analysis/src/govdata/P1_collect.py
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(HERE, "data", "processed", "govdata", "P")
RAW = os.path.join(OUT, "raw")
os.makedirs(RAW, exist_ok=True)
SCRATCH = os.environ.get("P_SCRATCH", os.path.join(os.environ.get("TEMP", HERE), "govdata_P_cache"))
os.makedirs(SCRATCH, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) citadel-abnb research (krishangbro@gmail.com)"}
MANIFEST = []
SERIES = []  # tidy rows: source, series, freq, period (YYYY-MM or YYYY-Qn), value, unit
HICP_GEOS = ["EA", "EU27_2020", "DE", "ES", "FR", "IT", "PT", "NL", "EL", "HR", "AT", "IE", "PL", "CH", "NO", "TR", "UK", "SE", "DK", "CZ", "HU", "BE"]
SPPI_GEOS = ["EA20", "EU27_2020", "DE", "ES", "FR", "IT", "PT", "NL", "AT", "SE", "DK", "PL", "UK", "NO", "IE", "HR", "EL"]


def log(*a):
    print(datetime.now().strftime("%H:%M:%S"), *a, flush=True)


def manifest(source, url, status, content: bytes | None, last_period="", cache_file="", note=""):
    MANIFEST.append({"source": source, "url": url, "access_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                     "http_status": status, "bytes": len(content) if content is not None else 0,
                     "sha256": hashlib.sha256(content).hexdigest() if content else "", "last_period": last_period,
                     "cache_file": cache_file, "note": note})


def get(source, url, method="GET", timeout=90, cache_name=None, **kw):
    """Fetch with a manifest row. Returns (status, bytes). Caches binary files under SCRATCH if cache_name."""
    path = os.path.join(SCRATCH, cache_name) if cache_name else None
    if path and os.path.exists(path) and os.path.getsize(path) > 0:
        b = open(path, "rb").read()
        manifest(source, url, "cached", b, cache_file=cache_name, note="served from session cache")
        return 200, b
    try:
        r = requests.request(method, url, headers={**UA, **kw.pop("headers", {})}, timeout=timeout, **kw)
        b = r.content
        if path and r.status_code == 200:
            open(path, "wb").write(b)
        manifest(source, url, r.status_code, b if r.status_code == 200 else None, cache_file=cache_name or "",
                 note="" if r.status_code == 200 else f"body[:120]={b[:120]!r}")
        return r.status_code, b
    except Exception as e:  # noqa: BLE001
        manifest(source, url, "error", None, note=str(e)[:200])
        return 0, b""


def add(source, series, freq, period, value, unit=""):
    if value is None or (isinstance(value, float) and not np.isfinite(value)):
        return
    SERIES.append({"source": source, "series": series, "freq": freq, "period": period, "value": float(value), "unit": unit})


def set_last(source, url):
    """Back-fill last_period in the manifest row for a url from SERIES."""
    per = [s["period"] for s in SERIES if s["source"] == source]
    for m in MANIFEST:
        if m["source"] == source and m["url"] == url and not m["last_period"] and per:
            m["last_period"] = max(per)


# ----------------------------------------------------------------------------------------------
# JSON-stat helper (Eurostat)
# ----------------------------------------------------------------------------------------------
def jsonstat_rows(d):
    ids = d["id"]; sizes = d["size"]
    cats = {i: d["dimension"][i]["category"]["index"] for i in ids}
    inv = {i: {v: k for k, v in cats[i].items()} for i in ids}
    rows = []
    for k, v in d["value"].items():
        k = int(k); idx = []
        for s in reversed(sizes):
            idx.append(k % s); k //= s
        idx = idx[::-1]
        rows.append({**{i: inv[i][j] for i, j in zip(ids, idx)}, "value": v})
    return pd.DataFrame(rows)


def eurostat(source, dataset, params):
    url = f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset}?" + "&".join(params) + "&lang=EN"
    st, b = get(source, url, timeout=180)
    if st != 200:
        return None
    df = jsonstat_rows(json.loads(b))
    return df, url


def pull_eurostat_hicp():
    frames = []
    for unit in ("RCH_A", "I15"):
        params = ["coicop18=CP112", "coicop18=CP11201", "coicop18=CP11202", "coicop18=CP11209", f"unit={unit}", "sinceTimePeriod=2015-01"]
        r = eurostat("eurostat_hicp", "prc_hicp_minr", params)
        if r is None:
            continue
        df, url = r
        df["unit"] = unit
        df = df[df.geo.isin(HICP_GEOS)]  # keep the raw cache small: the geos tested in P2
        frames.append(df)
        for _, x in df.iterrows():
            add("eurostat_hicp", f"hicp_{x['coicop18']}_{x['geo']}_{unit}", "M", x["time"], x["value"], unit)
        set_last("eurostat_hicp", url)
    if frames:
        pd.concat(frames).to_csv(os.path.join(RAW, "eurostat_hicp_cp112_family_monthly.csv"), index=False)


def pull_eurostat_sppi():
    frames = []
    for unit in ("PCH_SM", "I21"):
        r = eurostat("eurostat_sppi", "sts_sepp_q", ["nace_r2=I55", f"unit={unit}", "s_adj=NSA", "sinceTimePeriod=2015-Q1"])
        if r is None:
            continue
        df, url = r
        df = df[df.geo.isin(SPPI_GEOS)]
        frames.append(df)
        for _, x in df.iterrows():
            add("eurostat_sppi", f"sppi_I55_{x['geo']}_{unit}", "Q", x["time"], x["value"], unit)
        set_last("eurostat_sppi", url)
    if frames:
        pd.concat(frames).to_csv(os.path.join(RAW, "eurostat_sppi_i55_quarterly.csv"), index=False)


# ----------------------------------------------------------------------------------------------
def pull_ine_es():
    tables = {1989: "hdpi_holiday_dwellings", 2007: "rtapi_rural", 1990: "tcpi_campsite", 2058: "hotel_adr", 2056: "hotel_revpar"}
    rows = []
    for t, name in tables.items():
        url = f"https://servicios.ine.es/wstempus/js/EN/DATOS_TABLA/{t}?nult=150"
        for attempt in range(4):
            st, b = get("ine_es", url, timeout=120)
            try:
                d = json.loads(b)
            except Exception:  # noqa: BLE001
                d = None
            if isinstance(d, list):
                break
            log("INE table", t, "not ready, retry", attempt, (d or {}).get("status") if isinstance(d, dict) else st)
            time.sleep(20)
        if not isinstance(d, list):
            continue
        for s in d:
            for x in s["Data"]:
                rows.append({"table": t, "table_name": name, "cod": s["COD"], "name": s["Nombre"], "year": x["Anyo"], "month": x["FK_Periodo"], "value": x["Valor"]})
                per = f"{x['Anyo']}-{int(x['FK_Periodo']):02d}"
                add("ine_es", f"ine_{name}_{s['COD']}", "M", per, x["Valor"], "index_or_rate")
        set_last("ine_es", url)
    pd.DataFrame(rows).to_csv(os.path.join(RAW, "ine_es_price_tables_monthly.csv"), index=False)


def pull_bls():
    ids = ["PCU721110721110", "PCU7211--7211--", "CUUR0000SEHB02", "CUSR0000SEHB02"]
    rows = []
    for y0, y1 in ((2012, 2021), (2022, 2026)):
        url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
        payload = json.dumps({"seriesid": ids, "startyear": str(y0), "endyear": str(y1)})
        st, b = get("bls", url + f"#{y0}-{y1}", method="POST", data=payload, headers={"Content-Type": "application/json"}, timeout=120)
        if st != 200:
            continue
        d = json.loads(b)
        for s in d["Results"]["series"]:
            for x in s["data"]:
                if not x["period"].startswith("M") or x["period"] == "M13":
                    continue
                per = f"{x['year']}-{x['period'][1:]}"
                try:
                    v = float(x["value"])
                except ValueError:  # BLS prints '-' for unavailable months
                    continue
                rows.append({"series_id": s["seriesID"], "month": per, "value": v})
                add("bls", f"bls_{s['seriesID']}", "M", per, v, "index")
        set_last("bls", url + f"#{y0}-{y1}")
    pd.DataFrame(rows).drop_duplicates().to_csv(os.path.join(RAW, "bls_ppi_cpi_lodging_monthly.csv"), index=False)


def pull_statcan():
    url = "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods"
    st, b = get("statcan", url + "#v41691191", method="POST", data=json.dumps([{"vectorId": 41691191, "latestN": 175}]),
                headers={"Content-Type": "application/json"}, timeout=120)
    if st != 200:
        return
    d = json.loads(b)[0]["object"]
    rows = []
    for x in d["vectorDataPoint"]:
        per = x["refPer"][:7]
        rows.append({"vector": "v41691191", "month": per, "value": x["value"], "release": x.get("releaseTime")})
        add("statcan", "statcan_cpi_traveller_accommodation", "M", per, x["value"], "index_2002eq100")
    set_last("statcan", url + "#v41691191")
    pd.DataFrame(rows).to_csv(os.path.join(RAW, "statcan_cpi_traveller_accommodation_monthly.csv"), index=False)
    # TASPI: terminated, probe only
    get("statcan_taspi", "https://www150.statcan.gc.ca/t1/wds/rest/getCubeMetadata#18100250", method="POST",
        data=json.dumps([{"productId": 18100250}]), headers={"Content-Type": "application/json"})
    MANIFEST[-1]["note"] = "Traveller accommodation services price index, quarterly; cubeEndDate 2019-10-01, no longer updated"
    MANIFEST[-1]["last_period"] = "2019-Q4"


def pull_abs():
    rows = []
    # CPI_M is the 2017-2025 monthly indicator (ends 2025-09); the complete monthly CPI from Nov 2025 sits in the CPI
    # dataflow with FREQ=M (suffix Mc). P2 splices the two on y/y.
    for flow, freq, start, suffix in (("CPI,2.0.0", "Q", "2015-Q1", "Q"), ("CPI_M,1.2.0", "M", "2017-01", "M"), ("CPI,2.0.0", "M", "2017-01", "Mc")):
        for idx in ("30033", "40101", "40102"):
            url = f"https://data.api.abs.gov.au/rest/data/ABS,{flow}/1.{idx}.10.50.{freq}?startPeriod={start}&format=csv"
            st, b = get("abs", url, headers={"Accept": "text/csv"}, timeout=120)
            if st != 200:
                continue
            df = pd.read_csv(io.BytesIO(b))
            for _, x in df.iterrows():
                per = str(x["TIME_PERIOD"])
                rows.append({"flow": flow, "index": idx, "period": per, "value": x["OBS_VALUE"]})
                add("abs", f"abs_cpi_{idx}_{suffix}", freq, per, x["OBS_VALUE"], "index")
            set_last("abs", url)
    pd.DataFrame(rows).to_csv(os.path.join(RAW, "abs_cpi_holiday_travel_accommodation.csv"), index=False)


def pull_ibge():
    rows = []
    for t, item in ((7060, 47659), (1419, 7753)):
        url = f"https://apisidra.ibge.gov.br/values/t/{t}/n1/all/v/63,2265/p/all/c315/{item}?formato=json"
        st, b = get("ibge", url, timeout=120)
        if st != 200:
            continue
        d = json.loads(b)
        for r in d[1:]:
            per = f"{r['D3C'][:4]}-{r['D3C'][4:6]}"
            var = "mom" if r["D2C"] == "63" else "yoy12m"
            try:
                v = float(r["V"])
            except ValueError:
                continue
            rows.append({"table": t, "item": item, "variable": var, "month": per, "value": v})
            add("ibge", f"ibge_ipca_hospedagem_{var}", "M", per, v, "pct")
        set_last("ibge", url)
    pd.DataFrame(rows).to_csv(os.path.join(RAW, "ibge_ipca_hospedagem_monthly.csv"), index=False)


def pull_fred():
    rows = []
    for sid, name in (("B646RG3Q086SBEA", "bea_export_travel_price"), ("B647RG3Q086SBEA", "bea_import_travel_price")):
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
        st, b = get("fred_bea", url)
        if st != 200:
            continue
        df = pd.read_csv(io.BytesIO(b))
        for _, x in df.iterrows():
            d = pd.to_datetime(x["observation_date"])
            per = f"{d.year}-Q{(d.month - 1) // 3 + 1}"
            try:
                v = float(x[sid])
            except (ValueError, TypeError):
                continue
            rows.append({"series": sid, "quarter": per, "value": v})
            add("fred_bea", name, "Q", per, v, "index_2017eq100")
        set_last("fred_bea", url)
    pd.DataFrame(rows).to_csv(os.path.join(RAW, "fred_bea_travel_price_quarterly.csv"), index=False)


def pull_ons():
    rows = []
    for cdid, name in (("d7cx", "cpi_112_accommodation_index"), ("l7ie", "cpi_11201_hotels_index"),
                       ("l7ik", "cpi_11203_other_establishments_index"), ("d7hb", "cpi_112_annual_rate")):
        url = f"https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/{cdid}/mm23/data"
        st, b = get("ons", url)
        if st != 200:
            continue
        d = json.loads(b)
        for x in d.get("months", []):
            dt = pd.to_datetime(x["date"], format="%Y %b")
            per = dt.strftime("%Y-%m")
            rows.append({"cdid": cdid, "name": name, "month": per, "value": float(x["value"])})
            add("ons", f"ons_{name}", "M", per, float(x["value"]), "index_or_pct")
        set_last("ons", url)
    pd.DataFrame(rows).to_csv(os.path.join(RAW, "ons_cpi_accommodation_monthly.csv"), index=False)


# ----------------------------------------------------------------------------------------------
# Hawaii DBEDT vacation rental performance report
# ----------------------------------------------------------------------------------------------
HI_REGIONS = ["State of Hawai", "O‘ahu", "Maui County", "Island of Hawai", "Kaua‘i"]


def _hi_num(s):
    s = s.replace("$", "").replace(",", "").replace("%", "")
    try:
        return float(s)
    except ValueError:
        return np.nan


def hawaii_xlsx(b, ym):
    df = pd.read_excel(io.BytesIO(b), header=None)
    out = []
    # header row with years: first row where col1 is a year and col2 is a year
    yrs = None
    for r in range(min(8, len(df))):
        v1, v2 = df.iat[r, 1], df.iat[r, 2]
        try:
            if 1990 < float(v1) < 2100 and 1990 < float(v2) < 2100:
                yrs = (int(float(v1)), int(float(v2))); break
        except (TypeError, ValueError):
            continue
    if yrs is None:
        return out
    for r in range(len(df)):
        lab = df.iat[r, 0]
        if not isinstance(lab, str) or r > 20:
            continue
        lab = lab.replace("‘", "‘").replace("ʻ", "‘").replace("'", "‘")
        if any(lab.startswith(p) for p in HI_REGIONS):
            out.append({"vintage": ym, "region": lab.strip(), "year_cur": yrs[0], "year_cmp": yrs[1],
                        "supply_cur": df.iat[r, 1], "supply_cmp": df.iat[r, 2], "demand_cur": df.iat[r, 4], "demand_cmp": df.iat[r, 5],
                        "occ_cur": df.iat[r, 7], "occ_cmp": df.iat[r, 8], "adr_cur": df.iat[r, 10], "adr_cmp": df.iat[r, 11],
                        "adr_pct_change_reported": df.iat[r, 12], "file_type": "xlsx"})
    return out


def hawaii_pdf(b, ym):
    import pdfplumber
    out = []
    with pdfplumber.open(io.BytesIO(b)) as p:
        for pg in p.pages:
            t = pg.extract_text() or ""
            if "Unit Average Daily Rate" not in t and "Average Daily Rate" not in t:
                continue
            m = re.search(r"(20\d\d)\s+(20\d\d)\s+Change", t)
            if not m:
                continue
            yrs = (int(m.group(1)), int(m.group(2)))
            for line in t.splitlines():
                ln = line.replace("‘", "‘").replace("ʻ", "‘").replace("'", "‘")
                if any(ln.startswith(p) for p in HI_REGIONS):
                    toks = re.findall(r"-?\$?[\d,]+\.?\d*%?", ln)
                    toks = [x for x in toks if re.search(r"\d", x)]
                    dollars = [x for x in toks if x.startswith("$") or x.startswith("-$")]
                    if len(toks) < 8 or len(dollars) < 2:
                        continue
                    nums = [_hi_num(x) for x in toks]
                    di = toks.index(dollars[0])
                    out.append({"vintage": ym, "region": re.split(r"\s-?\$?\d", ln)[0].strip(), "year_cur": yrs[0], "year_cmp": yrs[1],
                                "supply_cur": nums[0], "supply_cmp": nums[1], "demand_cur": nums[3], "demand_cmp": nums[4],
                                "occ_cur": nums[6] / 100 if nums[6] > 1.5 else nums[6], "occ_cmp": nums[7] / 100 if nums[7] > 1.5 else nums[7],
                                "adr_cur": nums[di], "adr_cmp": nums[di + 1],
                                "adr_pct_change_reported": nums[di + 2] / 100 if di + 2 < len(nums) else np.nan, "file_type": "pdf"})
            if out:
                break
    return out


def pull_hawaii():
    rows = []
    # P_HI_START / P_HI_END restrict the vintages fetched (files.hawaii.gov rate-limits bursts with a 429 challenge)
    months = pd.period_range(os.environ.get("P_HI_START", "2019-09"), os.environ.get("P_HI_END", "2026-07"), freq="M")
    for pm in months:
        ym = str(pm)
        y = pm.year
        cands = []
        if y >= 2025:
            cands.append((f"https://files.hawaii.gov/dbedt/economic/tourism/vacation-rental/hawaii-vacation-rental-performance-{ym}.xlsx", "xlsx"))
        if y == 2024:
            cands.append((f"https://files.hawaii.gov/dbedt/visitor/vacation-rental/hawaii-vacation-rental-performance-{ym}.xlsx", "xlsx"))
            cands.append((f"https://files.hawaii.gov/dbedt/economic/archive/tourism/vacation-rental/hawaii-vacation-rental-performance-{ym}.xlsx", "xlsx"))
        cands.append((f"https://files.hawaii.gov/dbedt/visitor/vacation-rental/hawaii-vacation-rental-performance-{ym}.pdf", "pdf"))
        cands.append((f"https://files.hawaii.gov/dbedt/economic/archive/tourism/vacation-rental/hawaii-vacation-rental-performance-{ym}.pdf", "pdf"))
        cands.append((f"https://files.hawaii.gov/dbedt/economic/tourism/vacation-rental/hawaii-vacation-rental-performance-{ym}.pdf", "pdf"))
        got = []
        for url, kind in cands:
            for attempt in range(4):  # files.hawaii.gov sits behind Cloudflare: pace requests, back off on 429
                cached = os.path.exists(os.path.join(SCRATCH, f"hi_{ym}.{kind}"))
                st, b = get("hawaii_dbedt", url, cache_name=f"hi_{ym}.{kind}", timeout=60)
                if not cached:
                    time.sleep(float(os.environ.get("P_HI_PACE", "6")))
                if st == 429:
                    log("hawaii 429 on", ym, kind, "attempt", attempt); time.sleep(120 * (attempt + 1))
                    continue
                break
            if st != 200 or len(b) < 1000:
                continue
            try:
                got = hawaii_xlsx(b, ym) if kind == "xlsx" else hawaii_pdf(b, ym)
            except Exception as e:  # noqa: BLE001
                MANIFEST[-1]["note"] = f"parse error {e}"[:200]
                got = []
            MANIFEST[-1]["last_period"] = ym
            if got:
                MANIFEST[-1]["note"] = f"{len(got)} region rows parsed"
                break
            MANIFEST[-1]["note"] = "fetched, no rows parsed"
        for g in got:
            g["month"] = ym
            rows.append(g)
        # trim manifest noise: drop 404 probe rows for the same month once a file was found
        if got:
            MANIFEST[:] = [m for m in MANIFEST if not (m["source"] == "hawaii_dbedt" and f"performance-{ym}." in m["url"] and m["http_status"] in (404, 429))]
    df = pd.DataFrame(rows)
    if not len(df):
        return
    # sanity: a comparison ADR outside 0.5x to 2x of the current ADR is a table-parse slip (footnote tokens); drop the row
    df["parse_ok"] = (df.adr_cmp > 0.5 * df.adr_cur) & (df.adr_cmp < 2.0 * df.adr_cur) & (df.adr_cur > 50) & (df.adr_cur < 2000)
    df.to_csv(os.path.join(RAW, "hawaii_dbedt_vacation_rental_monthly.csv"), index=False)
    df = df[df.parse_ok]
    # tidy: statewide level series from current-year columns (one per vintage), and y/y where the comparison year is the prior year
    st = df[df.region.str.startswith("State")].sort_values("month")
    for _, x in st.iterrows():
        add("hawaii_dbedt", "hawaii_vr_adr_state_usd", "M", x["month"], x["adr_cur"], "usd")
        add("hawaii_dbedt", "hawaii_vr_demand_state_unit_nights", "M", x["month"], x["demand_cur"], "unit_nights")
        add("hawaii_dbedt", "hawaii_vr_occ_state", "M", x["month"], x["occ_cur"], "share")
        if x["year_cmp"] == x["year_cur"] - 1 and np.isfinite(x["adr_cmp"]) and x["adr_cmp"] > 0:
            add("hawaii_dbedt", "hawaii_vr_adr_state_yoy_reported_pct", "M", x["month"], 100 * (x["adr_cur"] / x["adr_cmp"] - 1), "pct")
            # prior-year level (fills 2018-09 to 2019-08 from the 2019-20 vintages' comparison columns)
            pm = str(pd.Period(x["month"], "M") - 12)
            if not ((st.month == pm).any()):
                add("hawaii_dbedt", "hawaii_vr_adr_state_usd", "M", pm, x["adr_cmp"], "usd")
                add("hawaii_dbedt", "hawaii_vr_demand_state_unit_nights", "M", pm, x["demand_cmp"], "unit_nights")
    for reg in ("Maui County", "O‘ahu", "Kaua‘i", "Island of Hawai"):
        sub = df[df.region.str.startswith(reg)].sort_values("month")
        key = reg.split()[0].replace("‘", "").lower()
        for _, x in sub.iterrows():
            add("hawaii_dbedt", f"hawaii_vr_adr_{key}_usd", "M", x["month"], x["adr_cur"], "usd")
            if x["year_cmp"] == x["year_cur"] - 1 and np.isfinite(x["adr_cmp"]) and x["adr_cmp"] > 0:
                add("hawaii_dbedt", f"hawaii_vr_adr_{key}_yoy_reported_pct", "M", x["month"], 100 * (x["adr_cur"] / x["adr_cmp"] - 1), "pct")


# ----------------------------------------------------------------------------------------------
def pull_japan():
    rows = []
    found = False
    for sid in ("000040491332", "000040491331", "000040491330"):
        url = f"https://www.e-stat.go.jp/en/stat-search/file-download?statInfId={sid}&fileKind=4"
        st, b = get("japan_estat", url, cache_name=f"jp_{sid}.xlsx", timeout=180)
        if st != 200:
            continue
        x = pd.ExcelFile(io.BytesIO(b))
        for sh in x.sheet_names:
            df = x.parse(sh, header=None)
            hdr = None
            for r in range(5, 12):
                labs = df.iloc[r].tolist()
                if any(isinstance(v, str) and v.strip() == "宿泊料" for v in labs):
                    hdr = r; col = [i for i, v in enumerate(labs) if isinstance(v, str) and v.strip() == "宿泊料"][0]
                    break
            if hdr is None:
                continue
            found = True
            year = None
            # the year-month column differs between files (7 or 8): take the first column holding 'YYYY年'
            ymcol = next(c for c in range(0, 12) if isinstance(df.iat[hdr + 3, c], str) and re.match(r"\s*\d{4}年", df.iat[hdr + 3, c]))
            for r in range(hdr + 3, len(df)):
                s = df.iat[r, ymcol]
                if not isinstance(s, str):
                    continue
                m = re.match(r"\s*(\d{4})年\s*(\d{1,2})月", s)
                if m:
                    year, month = int(m.group(1)), int(m.group(2))
                elif re.match(r"^\s*(\d{1,2})\s*$", s) and year:
                    month = int(s.strip())
                else:
                    continue
                v = df.iat[r, col]
                try:
                    v = float(v)
                except (ValueError, TypeError):
                    continue
                per = f"{year}-{month:02d}"
                rows.append({"statInfId": sid, "sheet": sh, "month": per, "value": v})
                add("japan_estat", "japan_cpi_hotel_charges_index", "M", per, v, "index_2025eq100")
            MANIFEST[-1]["note"] = f"宿泊料 column {col} in sheet {sh}"
            set_last("japan_estat", url)
            break
        if found:
            break
    if rows:
        pd.DataFrame(rows).drop_duplicates(["month"]).to_csv(os.path.join(RAW, "japan_cpi_hotel_charges_monthly.csv"), index=False)


def pull_nz():
    url = ("https://www.stats.govt.nz/assets/Uploads/Consumers-price-index/Consumers-price-index-June-2026-quarter/"
           "Download-data/consumers-price-index-june-2026-quarter-index-numbers.csv")
    st, b = get("nz_statsnz", url, cache_name="nz_cpi_jun26.csv", timeout=120)
    if st != 200:
        return
    df = pd.read_csv(io.BytesIO(b))
    m = df.apply(lambda r: any("ccommodation" in str(v) for v in (r["Series_title_1"], r["Series_title_2"], r["Group"])), axis=1)
    sub = df[m].copy()
    sub.to_csv(os.path.join(RAW, "nz_cpi_accommodation_quarterly.csv"), index=False)
    for _, x in sub.iterrows():
        per = str(x["Period"])
        y, mth = per.split(".")
        q = f"{y}-Q{(int(mth) - 1) // 3 + 1}"
        name = re.sub(r"[^a-z0-9]+", "_", f"{x['Series_title_1']}_{x['Series_title_2']}".lower()).strip("_")
        add("nz_statsnz", f"nz_cpi_{x['Series_reference']}_{name}", "Q", q, x["Data_value"], "index")
    set_last("nz_statsnz", url)


# ----------------------------------------------------------------------------------------------
# record-only probes
# ----------------------------------------------------------------------------------------------
PROBES = [
    ("portugal_ine", "https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0008579&lang=EN", "API keyed by indicator id; catalogue endpoint (xml_indic.jsp?opc=3) lists 326 indicators without the monthly ADR/RevPAR; monthly flash PDF only"),
    ("portugal_ine_flash", "https://www.ine.pt/ngt_server/attachfileu.jsp?look_parentBoui=801040375&att_display=n&att_download=y", "May 2026 flash PDF (ADR, RevPAR y/y); July 2026 flash published late Aug 2026, PDF"),
    ("mexico_inegi", "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/628229/es/0700/false/BIE/2.0/TOKEN?type=json", "free registration token required; not held"),
    ("mexico_banxico", "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SP30578/datos/oportuno", "free registration token required; not held"),
    ("lvcva", "https://www.lvcva.com/research/visitor-statistics/", "monthly Las Vegas hotel ADR (hotel class); site returns 403 to fetchers"),
    ("singapore_stb", "https://www.stb.gov.sg/statistics-and-market-insights/hotel-statistics", "monthly hotel ARR; Tableau dashboard, page moved (404), data.gov.sg search does not list it"),
    ("hongkong_hktb", "https://partnernet.hktb.com/en/research_statistics/latest_statistics/index.html", "monthly hotel achieved room rate; PartnerNet login"),
    ("nz_mbie_adp", "https://www.mbie.govt.nz/immigration-and-tourism/tourism-research-and-data/tourism-data-releases/accommodation-data-programme", "guest nights, occupancy, capacity; no price measure"),
    ("croatia_evisitor", "https://www.htz.hr/en-GB/tourism-in-numbers/evisitor", "arrivals and nights; no price"),
    ("japan_mlit_minpaku", "https://www.mlit.go.jp/kankocho/minpaku/business/host/index.html", "minpaku notification-system nights and guests, bimonthly; no price"),
    ("ons_stl_pilot", "https://www.ons.gov.uk/businessindustryandtrade/tourismindustry/datasets/shorttermletsinenglandscotlandandwales", "short-term lets nights and guests from platform data; no price"),
    ("florida_dor_tdt", "https://floridarevenue.com/taxes/taxesfees/Pages/local_option.aspx", "tourist development tax collections, dollars by county; no nights"),
    ("vermont_tax_mr", "https://tax.vermont.gov/data-and-statistics", "meals and rooms tax receipts incl short-term rental line, dollars; no nights"),
    ("texas_comptroller_hot", "https://comptroller.texas.gov/transparency/local/hotel-receipts/", "hotel occupancy tax receipts by city, dollars; no nights"),
    ("nyc_dof_hotel_tax", "https://www.nyc.gov/site/finance/business/business-hotel-room-occupancy-tax.page", "hotel room occupancy tax collections, dollars; no nights"),
    ("colorado_dor", "https://cdor.colorado.gov/data-and-reports", "sales and lodging tax collections, dollars; no nights"),
    ("italy_mef_tourist_tax", "https://www.finanze.gov.it/it/fiscalita-regionale-e-locale/", "imposta di soggiorno, annual municipal collections, dollars; no nights"),
    ("france_tourist_tax", "https://www.data.gouv.fr/fr/datasets/?q=taxe+de+sejour", "taxe de sejour, annual collections by commune; no nights"),
    ("us_census_qss_721", "https://www.census.gov/services/qss/qss-current.html", "NAICS 721 accommodation revenue, quarterly; revenue not price; 3Q26 advance 19 Nov"),
]


def probes():
    for sid, url, note in PROBES:
        st, b = get(sid, url, timeout=30)
        MANIFEST[-1]["note"] = note
        if st == 200:
            MANIFEST[-1]["bytes"] = len(b)
            MANIFEST[-1]["sha256"] = ""  # html pages: no cache kept


# ----------------------------------------------------------------------------------------------
def main():
    steps = [("eurostat_hicp", pull_eurostat_hicp), ("eurostat_sppi", pull_eurostat_sppi), ("ine_es", pull_ine_es), ("bls", pull_bls),
             ("statcan", pull_statcan), ("abs", pull_abs), ("ibge", pull_ibge), ("fred_bea", pull_fred), ("ons", pull_ons),
             ("nz", pull_nz), ("japan", pull_japan), ("hawaii", pull_hawaii), ("probes", probes)]
    only = sys.argv[1:]
    for name, fn in steps:
        if only and name not in only:
            continue
        log("start", name)
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            log("FAILED", name, repr(e)[:300])
            MANIFEST.append({"source": name, "url": "", "access_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                             "http_status": "error", "bytes": 0, "sha256": "", "last_period": "", "cache_file": "", "note": repr(e)[:200]})
        log("done", name, "series rows so far", len(SERIES))
    man = pd.DataFrame(MANIFEST)
    mpath = os.path.join(RAW, "MANIFEST.csv")
    if only and os.path.exists(mpath):
        old = pd.read_csv(mpath)
        old = old[~old.source.isin(man.source.unique())]
        man = pd.concat([old, man], ignore_index=True)
    man.to_csv(mpath, index=False)
    ser = pd.DataFrame(SERIES).drop_duplicates(["source", "series", "period"])
    spath = os.path.join(OUT, "P_series_tidy.csv")
    if only and os.path.exists(spath):
        old = pd.read_csv(spath)
        old = old[~old.source.isin(ser.source.unique())]
        ser = pd.concat([old, ser], ignore_index=True)
    ser.to_csv(spath, index=False)
    print(ser.groupby(["source", "freq"]).agg(n_series=("series", "nunique"), first=("period", "min"), last=("period", "max")).to_string())


if __name__ == "__main__":
    main()
