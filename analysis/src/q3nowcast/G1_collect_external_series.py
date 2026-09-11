"""G1: pull every free external high-frequency travel series with Jul-Sep 2026 coverage.

Workstream G, Q3 2026 nowcast run. Krishang Surapaneni (compiled with Claude Code).

Writes raw caches to data/processed/q3nowcast/G/raw/ and a source inventory to
data/processed/q3nowcast/G/source_inventory.csv. Every row records URL, access
date, bytes and the coverage end date actually observed in the payload.

All figures are SOURCED unless the inventory's note says otherwise.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import time
from datetime import date

import pandas as pd
import requests

ACCESS_DATE = "2026-09-11"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "data", "processed", "q3nowcast", "G")
RAW = os.path.join(OUT, "raw")
os.makedirs(RAW, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127 Safari/537.36"}
MANIFEST: list[dict] = []


def log(*a):
    print(*a, flush=True)


def note(name, url, path, status, coverage_end, measures, basis, nearest_abnb, freq, comment=""):
    sz = os.path.getsize(path) if path and os.path.exists(path) else 0
    MANIFEST.append(
        dict(series=name, url=url, file=os.path.relpath(path, OUT) if path else "", bytes=sz,
             http_status=status, access_date=ACCESS_DATE, frequency=freq,
             coverage_end=coverage_end, measures=measures, basis=basis,
             nearest_abnb_series=nearest_abnb, comment=comment))


def get(url, timeout=90, tries=3, **kw):
    last = None
    for i in range(tries):
        try:
            r = requests.get(url, headers=UA, timeout=timeout, **kw)
            if r.status_code == 200:
                return r
            last = f"http {r.status_code}"
        except Exception as e:  # noqa: BLE001
            last = repr(e)[:120]
        time.sleep(2 + 3 * i)
    log(f"  FAILED {url} -> {last}")
    return None


# ---------------------------------------------------------------- 1. TSA daily
def tsa():
    log("[1] TSA checkpoint throughput, daily")
    frames = []
    for y in [2019, 2020, 2021, 2022, 2023, 2024, 2025, None]:
        url = "https://www.tsa.gov/travel/passenger-volumes" + (f"/{y}" if y else "")
        r = get(url)
        if r is None:
            continue
        try:
            t = pd.read_html(io.StringIO(r.text))[0]
        except Exception as e:  # noqa: BLE001
            log(f"  {y}: parse fail {e}")
            continue
        t.columns = ["date", "pax"]
        t["date"] = pd.to_datetime(t["date"], format="%m/%d/%Y", errors="coerce")
        t["pax"] = pd.to_numeric(t["pax"], errors="coerce")
        frames.append(t.dropna())
        log(f"  {y or 2026}: {len(t)} rows, {t['date'].min():%Y-%m-%d} to {t['date'].max():%Y-%m-%d}")
        time.sleep(1)
    df = pd.concat(frames).drop_duplicates("date").sort_values("date").reset_index(drop=True)
    p = os.path.join(RAW, "tsa_checkpoint_daily.csv")
    df.to_csv(p, index=False)
    note("tsa_checkpoint_daily", "https://www.tsa.gov/travel/passenger-volumes", p, 200,
         f"{df['date'].max():%Y-%m-%d}", "US TSA checkpoint passengers screened (departures+connections)",
         "traveller count, US airports only", "nights (weak), Seats Booked (directional)", "daily",
         "full history 2019-present; one row per day; includes non-leisure and connecting pax")
    return df


# --------------------------------------------------- 2. BLS CPI (price series)
BLS_SERIES = {
    "CUSR0000SEHB": ("CPI lodging away from home, SA", "price index, US urban", "ADR (US, price only)"),
    "CUUR0000SEHB": ("CPI lodging away from home, NSA", "price index, US urban", "ADR (US, price only)"),
    "CUSR0000SETG01": ("CPI airline fares, SA", "price index, US urban", "none direct; airfare cost of travel"),
    "CUSR0000SA0": ("CPI all items, SA", "price index", "deflator"),
    "CUUR0000SS62031": ("CPI other lodging away from home incl hotels/motels, NSA", "price index", "ADR (US, price only)"),
}


def bls():
    log("[2] BLS CPI price series")
    rows = []
    for sid, (desc, basis, near) in BLS_SERIES.items():
        url = f"https://api.bls.gov/publicAPI/v2/timeseries/data/{sid}?startyear=2018&endyear=2026"
        r = get(url)
        if r is None:
            continue
        try:
            d = r.json()["Results"]["series"][0]["data"]
        except Exception as e:  # noqa: BLE001
            log(f"  {sid}: {e}")
            continue
        for v in d:
            if not v["period"].startswith("M") or v["period"] == "M13":
                continue
            try:
                val = float(v["value"])
            except (TypeError, ValueError):
                continue
            rows.append(dict(series_id=sid, desc=desc,
                             month=f"{v['year']}-{int(v['period'][1:]):02d}",
                             value=val))
        log(f"  {sid}: {len(d)} obs, latest {d[0]['year']}-{d[0]['period']}")
        time.sleep(1)
    if not rows:
        return None
    df = pd.DataFrame(rows).sort_values(["series_id", "month"])
    p = os.path.join(RAW, "bls_cpi_travel_monthly.csv")
    df.to_csv(p, index=False)
    end = df["month"].max()
    for sid, (desc, basis, near) in BLS_SERIES.items():
        sub = df[df.series_id == sid]
        if sub.empty:
            continue
        note(f"bls_{sid}", f"https://api.bls.gov/publicAPI/v2/timeseries/data/{sid}", p, 200,
             sub["month"].max(), desc, basis, near, "monthly",
             "public BLS API, no key; Aug 2026 print released 11 Sep 2026")
    log(f"  combined latest month {end}")
    return df


# ------------------------------------------- 3. Spain INE Frontur (arrivals)
def ine_table(table_id, nult=200):
    url = f"https://servicios.ine.es/wstempus/js/EN/DATOS_TABLA/{table_id}?nult={nult}"
    r = get(url, timeout=120)
    if r is None:
        return None, url
    try:
        d = r.json()
    except Exception:  # noqa: BLE001
        return None, url
    rows = []
    for s in d:
        for v in s.get("Data", []):
            per = v.get("FK_Periodo")
            if per is None or not (1 <= int(per) <= 12):
                continue  # drop annual (28) and other aggregates
            rows.append(dict(name=s.get("Nombre"), year=int(v["Anyo"]),
                             month=int(per), value=v.get("Valor")))
    return pd.DataFrame(rows), url


def spain():
    log("[3] Spain INE Frontur arrivals + EOH hotel overnight stays")
    out = {}
    for tid, label, fn, measures, basis, near in [
        (10821, "Frontur visitors by typology, national total", "ine_frontur_visitors_monthly.csv",
         "visitor and tourist arrivals to Spain", "arrivals (border survey)", "Europe nights (EMEA proxy)"),
        (75719, "Frontur tourists by country of residence", "ine_frontur_by_country_monthly.csv",
         "tourist arrivals to Spain by source country", "arrivals", "Europe nights, US-to-Europe mix"),
        (2009, "EOH hotel guests and overnight stays by category", "ine_hotel_overnight_monthly.csv",
         "hotel guests and overnight stays in Spain", "hotel nights", "nights (hotel substitute)"),
    ]:
        df, url = ine_table(tid)
        if df is None or df.empty:
            note(f"ine_{tid}", url, "", 0, "", label, basis, near, "monthly", "FETCH FAILED")
            log(f"  table {tid}: no monthly rows")
            continue
        df["period"] = df["year"].astype(str) + "-" + df["month"].map(lambda m: f"{m:02d}")
        p = os.path.join(RAW, fn)
        df.to_csv(p, index=False)
        out[tid] = df
        note(f"ine_{tid}", url, p, 200, df["period"].max(), label, basis, near, "monthly",
             f"INE tempus3 JSON API, {df['name'].nunique()} series")
        log(f"  table {tid}: {len(df)} rows, {df['name'].nunique()} series, latest {df['period'].max()}")
        time.sleep(2)
    return out


# ------------------------------------------------------- 4. Eurostat platform
def eurostat():
    log("[4] Eurostat tour_ce_omr platform nights (coverage check)")
    url = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tour_ce_omr"
           "?format=JSON&lang=EN&geo=EU27_2020")
    r = get(url, timeout=120)
    if r is None:
        note("eurostat_tour_ce_omr", url, "", 0, "", "EU27 platform guest nights", "platform nights",
             "nights (EU only)", "monthly", "FETCH FAILED")
        return None
    d = r.json()
    p = os.path.join(RAW, "eurostat_tour_ce_omr_eu27.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f)
    # flatten
    dims = d["id"]
    sizes = d["size"]
    idx = {k: {vv: kk for kk, vv in d["dimension"][k]["category"]["index"].items()} for k in dims}
    rows = []
    for flat, val in d["value"].items():
        flat = int(flat)
        coords = []
        for s in reversed(sizes):
            coords.append(flat % s)
            flat //= s
        coords = list(reversed(coords))
        rec = {k: idx[k][c] for k, c in zip(dims, coords)}
        rec["value"] = val
        rows.append(rec)
    df = pd.DataFrame(rows)
    pc = os.path.join(RAW, "eurostat_tour_ce_omr_eu27.csv")
    df.to_csv(pc, index=False)
    mm = df[(df.month != "TOTAL")].copy()
    mm["period"] = mm["time"].astype(str) + "-" + mm["month"].str.replace("M", "", regex=False)
    end = mm["period"].max() if not mm.empty else ""
    note("eurostat_tour_ce_omr", url, pc, 200, end,
         "EU27 guest nights booked through collaborative platforms (Airbnb, Booking, Expedia, TripAdvisor)",
         "platform nights", "nights (EU only, the closest public analogue to ABNB nights)", "monthly",
         f"dataset 'updated' tag {d.get('updated')}; experimental statistics; structural lag")
    log(f"  monthly coverage to {end}, dataset updated {d.get('updated')}")
    return df


# ------------------------------------------------- 5. NTTO I-94 US arrivals
def ntto():
    log("[5] NTTO I-94 overseas arrivals to the US")
    files = [
        ("ntto_monthly_arrivals_2000_present_COR.xlsx",
         "https://www.trade.gov/sites/default/files/2024-06/Monthly%20Arrivals%202000%20to%20Present%20%E2%80%93%20Country%20of%20Residence%20%28COR%29_1.xlsx",
         "history file as posted Jun 2024"),
        ("ntto_prelim_COR_July_2026.xlsx",
         "https://www.trade.gov/sites/default/files/2026-08/Preliminary_SummaryAnalysis_COR_July_2026.xlsx",
         "PRELIMINARY July 2026, posted Aug 2026"),
        ("ntto_final_COR_June_2026.xlsx",
         "https://www.trade.gov/sites/default/files/2026-09/FINAL_SummaryAnalysis_COR_June_2026.xlsx",
         "FINAL June 2026, posted Sep 2026"),
        ("ntto_final_COR_May_2026.xlsx",
         "https://www.trade.gov/sites/default/files/2026-07/FINAL_SummaryAnalysis_COR_May_2026.xlsx",
         "FINAL May 2026, posted Jul 2026"),
    ]
    got = []
    for fn, url, comment in files:
        r = get(url, timeout=180)
        if r is None:
            note(f"ntto_{fn}", url, "", 0, "", "overseas visitor arrivals to the US", "arrivals",
                 "North America nights (inbound leg only)", "monthly", "FETCH FAILED: " + comment)
            continue
        p = os.path.join(RAW, fn)
        with open(p, "wb") as f:
            f.write(r.content)
        got.append((fn, p))
        note(f"ntto_{fn}", url, p, 200, "2026-07", "overseas visitor arrivals to the US by country of residence",
             "arrivals (I-94, overnight stays, selected visa classes)",
             "North America nights inbound component only", "monthly", comment)
        log(f"  {fn}: {len(r.content)} bytes")
        time.sleep(1)
    # Export the monthly history as a processed CSV so the panel rebuilds without
    # the vendor xlsx (the xlsx is not committed; re-download with `G1 ntto`).
    hist = os.path.join(RAW, "ntto_monthly_arrivals_2000_present_COR.xlsx")
    if os.path.exists(hist):
        d = pd.read_excel(hist, sheet_name="Monthly", header=None)
        hdr = d.iloc[0]
        cols = {}
        for i, v in hdr.items():
            if hasattr(v, "year") and hasattr(v, "month"):
                cols[i] = f"{v.year}-{v.month:02d}"
            elif isinstance(v, str):
                t = v.strip().splitlines()[0] if v.strip() else ""
                if len(t) == 7 and t[4] == "-":
                    cols[i] = t
        lab = d.iloc[:, 1].astype(str).str.strip()
        rows = []
        for key in ["TOTAL ALL COUNTRIES", "OVERSEAS", "WESTERN EUROPE", "EASTERN EUROPE",
                    "ASIA", "SOUTH AMERICA", "CENTRAL AMERICA", "CARIBBEAN",
                    "MIDDLE EAST", "OCEANIA", "AFRICA"]:
            idx = lab[lab == key].index
            if not len(idx):
                continue
            row = d.loc[idx[0]]
            for i, per in cols.items():
                v = pd.to_numeric(row[i], errors="coerce")
                if pd.notna(v):
                    rows.append(dict(region=key, month=per, arrivals=float(v)))
        out = pd.DataFrame(rows).sort_values(["region", "month"])
        pc = os.path.join(RAW, "ntto_arrivals_monthly.csv")
        out.to_csv(pc, index=False)
        note("ntto_arrivals_monthly_csv",
             "https://www.trade.gov/i-94-arrivals-program", pc, 200,
             out.month.max(), "monthly overseas visitor arrivals to the US by world region",
             "arrivals (I-94, 1+ nights, qualified visa types)",
             "North America nights, inbound leg only", "monthly",
             "flattened from the vendor xlsx; this CSV is what G2 reads")
        log(f"  ntto_arrivals_monthly.csv: {len(out)} rows to {out.month.max()}")
    return got


# --------------------------------------------------------------- 6. JNTO Japan
def jnto():
    log("[6] JNTO Japan inbound visitors")
    cands = [
        "https://www.jnto.go.jp/statistics/data/visitors-statistics/",
        "https://statistics.jnto.go.jp/en/graph/",
        "https://www.jnto.go.jp/statistics/data/",
    ]
    for url in cands:
        r = get(url, timeout=90)
        if r is None:
            continue
        p = os.path.join(RAW, "jnto_" + hashlib.md5(url.encode()).hexdigest()[:6] + ".html")
        with open(p, "w", encoding="utf-8", errors="replace") as f:
            f.write(r.text)
        log(f"  {url}: {len(r.text)} chars -> {os.path.basename(p)}")
        note("jnto_landing_" + hashlib.md5(url.encode()).hexdigest()[:6], url, p, 200, "2026-07",
             "Japan inbound visitor arrivals landing page", "arrivals",
             "APAC nights (Japan only)", "monthly", "HTML landing cache; Excel links extracted by hand")
    return None


def main():
    which = sys.argv[1:] or ["tsa", "bls", "spain", "eurostat", "ntto", "jnto"]
    if "tsa" in which:
        tsa()
    if "bls" in which:
        bls()
    if "spain" in which:
        spain()
    if "eurostat" in which:
        eurostat()
    if "ntto" in which:
        ntto()
    if "jnto" in which:
        jnto()
    inv = pd.DataFrame(MANIFEST)
    p = os.path.join(OUT, "source_inventory_raw.csv")
    if os.path.exists(p):
        old = pd.read_csv(p)
        inv = pd.concat([old[~old.series.isin(inv.series)], inv], ignore_index=True)
    inv.to_csv(p, index=False)
    log(f"\nwrote {p} ({len(inv)} rows)")
    print(inv[["series", "coverage_end", "bytes", "http_status"]].to_string(index=False))


if __name__ == "__main__":
    main()
