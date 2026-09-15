"""Manifested public travel covariates; no credentials and no Airbnb requests.

Every invocation writes a new directory. Unknown publication dates stay null;
retrieval timestamps never masquerade as historical release dates.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import sys
import unicodedata
import zipfile

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = ROOT / "data/processed/forecast_methods/macro_pulls"
COLS = ["series", "period", "destination", "origin", "origin_basis", "metric", "unit", "value",
        "published_on", "publication_basis", "release_source_url", "knowable_from", "pit_usable",
        "vintage_basis", "source_url"]
NTTO = "https://www.trade.gov/sites/default/files/2024-06/Monthly%20Arrivals%202000%20to%20Present%20%E2%80%93%20Country%20of%20Residence%20%28COR%29_1.xlsx"
EURO = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
SOURCES = [
    dict(series="ntto", url=NTTO, cadence="monthly", lag="Advance/preliminary/final around 8/18/28 of release month; exact historical dates unresolved", release_url="https://www.trade.gov/i-94-arrivals-program"),
    dict(series="jnto", url="https://www.jnto.go.jp/statistics/data/_files/20260819_1615-5.xlsx", cadence="monthly", lag="July 2026 released 19 August: 19 days after month end", release_url="https://www.jnto.go.jp/en/news/20260819.pdf"),
    dict(series="datatur", url="https://datatur.sectur.gob.mx/Documentoscompartidos/cuentaviajeros/BD_CuentaViajeros_descarga.zip", cadence="monthly", lag="About 6 weeks; June release visible August; exact count-series release calendar unresolved", release_url="https://datatur.sectur.gob.mx/SitePages/cuentaviajeros.aspx"),
    dict(series="ine_frontur", url="https://servicios.ine.es/wstempus/js/EN/DATOS_TABLA/75719?nult=200", cadence="monthly", lag="July 2026 released 1 September: 32 days after month end", release_url="https://www.ine.es/dyngs/Prensa/en/FRONTUR0726.htm"),
    dict(series="ine_egatur", url="https://servicios.ine.es/wstempus/js/EN/DATOS_TABLA/13938?nult=200", cadence="monthly", lag="July 2026 released 1 September: 32 days after month end", release_url="https://www.ine.es/dyngs/Prensa/en/EGATUR0726.htm"),
    dict(series="fred_cpi_lodging", url="https://fred.stlouisfed.org/graph/graph.csv?id=CUSR0000SEHB&cosd=2018-01-01", cadence="monthly", lag="BLS generally 10-14 days after month end; August 2026 released 11 September", release_url="https://www.bls.gov/schedule/news_release/cpi.htm"),
    dict(series="bls_cpi_lodging", url="https://api.bls.gov/publicAPI/v2/timeseries/data/CUSR0000SEHB?startyear=2018&endyear=2026", cadence="monthly", lag="BLS generally 10-14 days after month end; August 2026 released 11 September", release_url="https://www.bls.gov/schedule/news_release/cpi.htm"),
    dict(series="istat", url="https://esploradati.istat.it/SDMXWS/rest/data/IT1,122_54_DF_DCSC_TUR_13,1.0/all?startPeriod=2021-01", cadence="monthly observations; quarterly releases", lag="Q1 2026 released 26 May (56 days after quarter end); next release 14 September", release_url="https://www.istat.it/comunicato-stampa/i-flussi-turistici-i-trimestre-2026/"),
    dict(series="costar_us_weekly", url="https://www.costar.com/products/str-benchmark/resources/press-releases/us-hotel-results-week-ending-1-august", cadence="weekly", lag="Week ended 1 August 2026 released 6 August: 5 days", release_url="https://www.costar.com/products/str-benchmark/resources/press-releases/us-hotel-results-week-ending-1-august"),
]
for geo in ["EU27_2020", "ES", "FR", "IT", "DE"]:
    SOURCES.append(dict(series=f"eurostat_platform_{geo}", url=EURO + f"tour_ce_omr?lang=en&geo={geo}&indic_to=NGT_SP&unit=NR", cadence="monthly observations; quarterly releases", lag="Q1 2026 released 2 July (93 days after quarter end); January lag 152 days", release_url="https://ec.europa.eu/eurostat/web/tourism/"))


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ascii_fold(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(text)) if not unicodedata.combining(c))


def month_from_header(value) -> str | None:
    if isinstance(value, (pd.Timestamp, datetime)):
        return f"{value.year:04}-{value.month:02}"
    match = re.match(r"^(20\d{2})-(0?[1-9]|1[0-2])(?:\D|$)", str(value).strip())
    return f"{match[1]}-{int(match[2]):02}" if match else None


def parse_ntto(payload: bytes) -> list[dict]:
    d = pd.read_excel(io.BytesIO(payload), sheet_name="Monthly", header=None)
    months = {j: month_from_header(d.iloc[0, j]) for j in range(3, d.shape[1])}
    months = {j: m for j, m in months.items() if m and m >= "2018-01"}
    if len(set(months.values())) != len(months):
        raise ValueError("Duplicate NTTO month headers; comparison columns must be resolved explicitly")
    groups = {"TOTAL ALL COUNTRIES", "OVERSEAS", "WESTERN EUROPE", "EASTERN EUROPE", "ASIA", "SOUTH AMERICA", "CENTRAL AMERICA", "CARIBBEAN", "MIDDLE EAST", "OCEANIA", "AFRICA", "NORTH AMERICA"}
    rows = []
    for _, r in d.iloc[1:].iterrows():
        if pd.isna(r.iloc[1]):
            continue
        origin = str(r.iloc[1]).strip()
        for j, month in months.items():
            val = pd.to_numeric(r.iloc[j], errors="coerce")
            if pd.notna(val) and val >= 0:
                rows.append(dict(period=month, value=float(val), destination="US", origin=origin,
                                 origin_basis="residence_group" if origin in groups else "residence",
                                 metric="international_arrivals", unit="persons"))
    return rows


def parse_jnto(payload: bytes) -> list[dict]:
    x = pd.ExcelFile(io.BytesIO(payload))
    rows = []
    for year in [s for s in x.sheet_names if s.isdigit() and int(s) >= 2018]:
        d = pd.read_excel(x, sheet_name=year, header=None)
        for _, r in d.iloc[4:].iterrows():
            if pd.isna(r.iloc[0]):
                continue
            origin = str(r.iloc[0]).strip()
            for m in range(1, 13):
                if m * 2 >= len(r):
                    continue
                val = pd.to_numeric(r.iloc[m * 2], errors="coerce")
                if pd.notna(val) and val >= 0:
                    rows.append(dict(period=f"{year}-{m:02}", value=float(val), destination="JP", origin=origin,
                                     origin_basis="nationality_or_source_group", metric="inbound_visitors", unit="persons"))
    return rows


def parse_datatur(payload: bytes) -> list[dict]:
    z = zipfile.ZipFile(io.BytesIO(payload))
    names = [n for n in z.namelist() if n.lower().endswith(".xlsx")]
    if len(names) != 1:
        raise ValueError("Expected one DATATUR workbook")
    d = pd.read_excel(io.BytesIO(z.read(names[0])))
    # Tipo is inflow/outflow, NOT the unit. Level03 separates money and persons.
    mask = d.DescripcionNivel03.map(ascii_fold).str.strip().eq("Numero de Viajeros")
    d = d[mask & d.Tipo.eq("Ingresos")]
    if d.empty:
        raise ValueError("No verified incoming traveler count rows")
    months = dict(zip(["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"], range(1, 13)))
    rows = []
    for _, r in d.iterrows():
        if pd.isna(r.Valor):
            continue  # published blank placeholders are missing, not zero travelers
        m = months[str(r.MesText).strip().lower()]
        rows.append(dict(period=f"{int(r.kano)}-{m:02}", value=float(r.Valor), destination="MX", origin="ALL",
                         origin_basis="incoming; residence unavailable", metric=" | ".join(str(r[c]) for c in ["DescripcionNivel04", "DescripcionNivel05", "DescripcionNivel06"]), unit="persons"))
    return rows


def parse_ine(payload: bytes, series: str) -> list[dict]:
    rows = []
    egatur_names = {
        "Total expenditure. National Total. Tourist. Base data.",
        "Tourist. Expenditure not included in package tour. National Total. Base data.",
        "Tourist. Expenditure on maintenance. National Total. Base data.",
        "Tourist. International transport expenditure. National Total. Base data.",
        "Tourist. Other expense. National Total. Base data.",
        "Tourist. Spending on accommodation. National Total. Base data.",
        "Tourist. Spending on activities. National Total. Base data.",
        "Tourist. Spending on tourism packages. National Total. Base data.",
    }
    for s in json.loads(payload):
        name = s.get("Nombre", "").strip()
        # Keep levels; do not mix annual rates with arrivals or expenditure.
        if "Base data" not in name:
            continue
        if "Annual variation" in name or "Cumulative" in name or "Percentage" in name:
            continue
        if series == "ine_egatur" and name not in egatur_names:
            continue  # reject average spend / duration or newly added unknown units
        for r in s.get("Data", []):
            m = r.get("FK_Periodo")
            if m is None or not 1 <= int(m) <= 12 or r.get("Valor") is None:
                continue
            month = f"{int(r['Anyo'])}-{int(m):02}"
            if month < "2018-01":
                continue
            rows.append(dict(period=month, value=float(r["Valor"]), destination="ES", origin=name,
                             origin_basis="residence" if series == "ine_frontur" else "expenditure_category",
                             metric="international_tourists" if series == "ine_frontur" else "tourist_expenditure",
                             unit="persons" if series == "ine_frontur" else "EUR_millions"))
    return rows


def flatten_eurostat(d: dict) -> list[dict]:
    maps = {k: {v: key for key, v in d["dimension"][k]["category"]["index"].items()} for k in d["id"]}
    out = []
    for i, val in d.get("value", {}).items():
        flat = int(i)
        coords = []
        for size in reversed(d["size"]):
            coords.append(flat % size)
            flat //= size
        rec = {k: maps[k][c] for k, c in zip(d["id"], reversed(coords))}
        if not re.fullmatch(r"M\d{2}", rec.get("month", "")):
            continue
        out.append(dict(period=f"{rec['time']}-{rec['month'][1:]}", destination=rec["geo"], origin=rec["c_resid"],
                        origin_basis="residence_domestic_foreign_total", metric="platform_guest_nights", unit="guest_nights", value=float(val)))
    return out


def parse_costar(payload: bytes) -> list[dict]:
    soup = BeautifulSoup(payload, "html.parser")
    txt = soup.get_text(" ", strip=True)
    if not re.search(r"6 August 2026", txt) or "26 July through 1 August 2026" not in txt:
        raise ValueError("Expected dated 1 August 2026 weekly release")
    rows = []
    for name, pattern in [("adr", r"Average daily rate \(ADR\):\s*US\$([\d,.]+)\s*\(([+-]?[\d.]+)%\)"),
                          ("revpar", r"Revenue per available room \(RevPAR\):\s*US\$([\d,.]+)\s*\(([+-]?[\d.]+)%\)")]:
        m = re.search(pattern, txt)
        if not m:
            raise ValueError(f"Missing national {name}")
        for metric, val, unit in [(name, m[1], "USD"), (name + "_yoy", m[2], "percent")]:
            rows.append(dict(period="2026-08-01", destination="US", origin="ALL", origin_basis="hotel_week_ended",
                             metric=metric, unit=unit, value=float(val.replace(",", "")), published_on="2026-08-06"))
    return rows


def parse_payload(spec: dict, payload: bytes) -> tuple[list[dict], dict]:
    name = spec["series"]
    metadata = {}
    if name == "ntto":
        rows = parse_ntto(payload)
    elif name == "jnto":
        rows = parse_jnto(payload)
    elif name == "datatur":
        rows = parse_datatur(payload)
        metadata["unit_filter"] = "Tipo=Ingresos AND DescripcionNivel03=Numero de Viajeros (accent-folded)"
    elif name.startswith("ine_"):
        rows = parse_ine(payload, name)
    elif name.startswith("eurostat_platform_"):
        d = json.loads(payload)
        metadata["provider_updated_at"] = d.get("updated")
        rows = flatten_eurostat(d)
    elif name == "costar_us_weekly":
        rows = parse_costar(payload)
    elif name == "bls_cpi_lodging":
        d = json.loads(payload)
        if d.get("status") != "REQUEST_SUCCEEDED":
            raise ValueError(str(d.get("message")))
        rows = [dict(period=f"{r['year']}-{int(r['period'][1:]):02}", destination="US", origin="ALL", origin_basis="urban_consumers",
                     metric="CUSR0000SEHB", unit="index_1982_1984_100", value=float(r["value"]))
                for r in d["Results"]["series"][0]["data"] if re.fullmatch(r"M(0[1-9]|1[0-2])", r["period"])
                and pd.notna(pd.to_numeric(r["value"], errors="coerce"))]
    elif name == "fred_cpi_lodging":
        d = pd.read_csv(io.BytesIO(payload))
        if "CUSR0000SEHB" not in d:
            raise ValueError("FRED response lacks requested series")
        rows = [dict(period=str(r.iloc[0])[:7], destination="US", origin="ALL", origin_basis="urban_consumers", metric="CUSR0000SEHB",
                     unit="index_1982_1984_100", value=float(r.CUSR0000SEHB)) for _, r in d.iterrows() if pd.notna(pd.to_numeric(r.CUSR0000SEHB, errors="coerce"))]
    elif name == "istat":
        d = pd.read_csv(io.BytesIO(payload))
        selectors = {"FREQ": "M", "REF_AREA": "IT", "ADJUSTMENT": "N", "TYPE_ACCOMMODATION": "ALL", "ECON_ACTIVITY_NACE_2007": "551_553",
                     "LOCALITY_TYPE": "ALL", "URBANIZ_DEGREE": "ALL", "COASTAL_AREA": "ALL", "SIZE_BY_NUMBER_ROOMS": "TOT"}
        for k, v in selectors.items():
            d = d[d[k].eq(v)]
        d = d[d.DATA_TYPE.isin(["AR", "NI"]) & d.COUNTRY_RES_GUESTS.isin(["IT", "WORLD", "WRL_X_ITA"])]
        rows = [dict(period=str(r.TIME_PERIOD), destination="IT", origin=r.COUNTRY_RES_GUESTS,
                     origin_basis="domestic_world_foreign_residence", metric="accommodation_arrivals" if r.DATA_TYPE == "AR" else "accommodation_nights",
                     unit="arrivals" if r.DATA_TYPE == "AR" else "guest_nights", value=float(r.OBS_VALUE)) for _, r in d.iterrows() if pd.notna(r.OBS_VALUE)]
        metadata["dimension_filter"] = selectors
    else:
        raise ValueError(f"Unknown adapter {name}")
    return rows, metadata


def finalize_rows(spec: dict, rows: list[dict], stamp: str) -> pd.DataFrame:
    out = []
    cpi_dates = {"2025-11": "2025-12-18", "2025-12": "2026-01-13", "2026-01": "2026-02-13", "2026-02": "2026-03-11",
                 "2026-03": "2026-04-10", "2026-04": "2026-05-12", "2026-05": "2026-06-10", "2026-06": "2026-07-14",
                 "2026-07": "2026-08-12", "2026-08": "2026-09-11"}
    for row in rows:
        published = row.get("published_on")
        if spec["series"] == "jnto" and row["period"] == "2026-07":
            published = "2026-08-19"
        if spec["series"].startswith("ine_") and row["period"] == "2026-07":
            published = "2026-09-01"
        if spec["series"].startswith("eurostat_platform_") and row["period"] in ["2026-01", "2026-02", "2026-03"]:
            published = "2026-07-02"
        if spec["series"].endswith("cpi_lodging"):
            published = cpi_dates.get(row["period"])
        if spec["series"] == "istat" and row["period"] in ["2026-01", "2026-02", "2026-03"]:
            published = "2026-05-26"
        # Retrospective data may have changed since their first publication.
        # Published_on is a calendar fact, not a certification of this vintage.
        row.update(series=spec["series"], published_on=published,
                   publication_basis="verified_source_calendar_or_dated_release" if published else "unknown_exact_release_date",
                   release_source_url=spec["release_url"], knowable_from=stamp[:10], pit_usable=False,
                   vintage_basis="current_download; historical_release_values_not_verified", source_url=spec["url"])
        if not np.isfinite(row["value"]):
            raise ValueError("Non-finite normalized value")
        out.append(row)
    d = pd.DataFrame(out, columns=COLS)
    if len(d) and d.duplicated(["series", "period", "origin", "metric"]).any():
        raise ValueError("Duplicate normalized observation keys")
    return d.sort_values(["period", "origin", "metric"]).reset_index(drop=True)


def fetch_one(spec: dict) -> tuple[pd.DataFrame, dict]:
    stamp = datetime.now(timezone.utc).isoformat()
    meta = {**spec, "pulled_at_utc": stamp, "http_status": None, "rows": 0, "response_sha256": None, "bytes": 0,
            "attempts": 1, "raw_retained": False}
    try:
        headers = {"User-Agent": "Public academic travel data research; no credentials"}
        if spec["series"] == "istat":
            headers["Accept"] = "text/csv"
        r = requests.get(spec["url"], timeout=(10, 35), headers=headers)
        meta.update(http_status=r.status_code, final_url=r.url, bytes=len(r.content), response_sha256=sha(r.content))
        r.raise_for_status()
        rows, extra = parse_payload(spec, r.content)
        meta.update(extra)
        d = finalize_rows(spec, rows, stamp)
        meta.update(rows=len(d), status="ok" if len(d) else "empty", published_rows=int(d.published_on.notna().sum()),
                    first_period=d.period.min() if len(d) else None, last_period=d.period.max() if len(d) else None)
    except Exception as exc:
        d = pd.DataFrame(columns=COLS)
        meta.update(status="failed", error=f"{type(exc).__name__}: {str(exc)[:450]}", published_rows=0)
    return d, meta


def ntto_features(d: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    for origin, tag in [("TOTAL ALL COUNTRIES", "ntto_total"), ("OVERSEAS", "ntto_overseas")]:
        s = d[d.origin.eq(origin)].set_index("period").value.sort_index()
        s.index = pd.PeriodIndex(s.index, freq="M")
        if s.index.duplicated().any():
            raise ValueError("Duplicate NTTO source months")
        # Reindex before yoy: missing calendar months must not shift the year comparator.
        if s.empty:
            continue
        s = s.reindex(pd.period_range(s.index.min(), s.index.max(), freq="M"))
        q = s.groupby(s.index.asfreq("Q")).sum(min_count=3)
        m1 = s[s.index.month.isin([1, 4, 7, 10])]
        m1.index = m1.index.asfreq("Q")
        out[tag + "_full"] = (q / q.shift(4) - 1) * 100
        out[tag + "_qtd1m"] = (m1 / m1.shift(4) - 1) * 100
    return out


def backtest(ntto: pd.DataFrame, outdir: Path) -> dict:
    sys.path.insert(0, str(ROOT / "analysis/src/forecast_methods"))
    from harness import load_targets, baseline_naive, baseline_ar1, baseline_trailing4
    targets = load_targets()
    t = targets.set_index("quarter")
    old = pd.read_csv(ROOT / "data/processed/q3nowcast/G/G_quarterly_panel.csv", index_col=0)
    old.index = pd.PeriodIndex(old.index, freq="Q")
    feature_sets = {"legacy_cached_features": old.filter(regex=r"^ntto_(total|overseas)_")}
    if len(ntto):
        feature_sets["new_download_calendar_aligned"] = ntto_features(ntto)
    selected = ["ntto_total_full", "ntto_total_qtd1m", "ntto_overseas_qtd1m"]
    paths = []
    for origin, features in feature_sets.items():
        panel = features.join(old[["nights_m_yoy_pct"]], how="outer")
        for window, train_start, test_start in [("W1", "2022Q1", "2023Q1"), ("W2", "2023Q1", "2024Q1")]:
            panelw = panel.loc[train_start:"2026Q2"]
            for feature in selected:
                if feature not in panelw:
                    continue
                for q, cell in panelw.loc[test_start:].iterrows():
                    hist = panelw.loc[panelw.index < q, [feature, "nights_m_yoy_pct"]].dropna()
                    if len(hist) < 4 or pd.isna(cell[feature]) or pd.isna(cell.nights_m_yoy_pct):
                        continue
                    X = np.column_stack([np.ones(len(hist)), hist[feature]])
                    beta = np.linalg.lstsq(X, hist.nights_m_yoy_pct, rcond=None)[0]
                    pred = float(beta[0] + beta[1] * cell[feature])
                    yhist = panelw.loc[panelw.index < q, "nights_m_yoy_pct"].dropna()
                    guide_date = t.loc[str(q), "guide_date"]
                    prior_level = float(t.loc[str(q - 4), "nights_m"])
                    bases = {name: fn(guide_date, str(q), "nights_m", "PIT", targets=targets)
                             for name, fn in [("naive", baseline_naive), ("ar1", baseline_ar1), ("trailing4", baseline_trailing4)]}
                    paths.append(dict(source=origin, window=window, feature=feature, quarter=str(q), vintage_date=str(guide_date)[:10],
                                      n_train=len(hist), n_params=2, pred_growth=pred, actual_growth=float(cell.nights_m_yoy_pct),
                                      legacy_naive_growth=float(yhist.iloc[-1]), pred_nights_m=prior_level * (1 + pred / 100),
                                      actual_nights_m=float(t.loc[str(q), "nights_m"]),
                                      **{f"harness_{name}_nights_m": v["point"] if v else np.nan for name, v in bases.items()},
                                      historical_pit_admissible=False, admission_reason="current-quarter feature and historical release vintages unavailable at guide date"))
    path = pd.DataFrame(paths)
    if "new_download_calendar_aligned" in set(path.source):
        keys = ["window", "feature", "quarter"]
        oldkeys = path[path.source.eq("legacy_cached_features")][keys]
        matched = path[path.source.eq("new_download_calendar_aligned")].merge(oldkeys, on=keys, how="inner")
        matched["source"] = "new_download_matched_legacy_test_cells"
        path = pd.concat([path, matched], ignore_index=True)
        comparison = old[selected].join(feature_sets["new_download_calendar_aligned"][selected], how="outer", lsuffix="_legacy", rsuffix="_current")
        comparison.loc["2022Q1":"2026Q2"].to_csv(outdir / "ntto_feature_comparison.csv")
    path.to_csv(outdir / "ntto_replay_cells.csv", index=False)
    results = []
    def rmse(x):
        return float(np.sqrt(np.mean(np.asarray(x, dtype=float) ** 2)))
    for keys, cells in path.groupby(["source", "window", "feature"]):
        numerator = rmse(cells.pred_growth - cells.actual_growth)
        denom = rmse(cells.legacy_naive_growth - cells.actual_growth)
        results.append(dict(source=keys[0], window=keys[1], feature=keys[2], target="nights_growth_pct", baseline="legacy_last_growth",
                            n=len(cells), rmse=numerator, baseline_rmse=denom, ratio=numerator / denom, historical_pit_admissible=False))
        for baseline in ["naive", "ar1", "trailing4"]:
            bcol = f"harness_{baseline}_nights_m"
            c = cells.dropna(subset=[bcol])
            if c.empty:
                continue
            numerator = rmse(c.pred_nights_m - c.actual_nights_m)
            denom = rmse(c[bcol] - c.actual_nights_m)
            results.append(dict(source=keys[0], window=keys[1], feature=keys[2], target="nights_m", baseline=f"frozen_harness_{baseline}",
                                n=len(c), rmse=numerator, baseline_rmse=denom, ratio=numerator / denom, historical_pit_admissible=False))
    pd.DataFrame(results).to_csv(outdir / "ntto_replay_summary.csv", index=False)
    admission = dict(W1_required=14, W2_required=10, W1_admitted=0, W2_admitted=0, verdict="FAIL: retrospective descriptive replay only; no historical PIT forecast registered",
                     n_params=2, explanation="The original 0.72-0.74 was on y/y growth using current-quarter features. Guide-date availability and historical revisions are not established. Level scoring changes the error weights; the frozen naive uses its own vintage slice.")
    (outdir / "ntto_pit_admission.json").write_text(json.dumps(admission, indent=2), encoding="utf8")
    return admission


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="Must be a new or empty directory")
    parser.add_argument("--offline-from", type=Path, help="Rebuild analysis from a manifested prior normalized capture; no HTTP")
    parser.add_argument("--refresh-series", help="Comma-separated adapters to pull once while reusing --offline-from for other captures")
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out = args.output_dir or (BASE if not BASE.exists() else BASE / "runs" / stamp)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f"Refusing to overwrite nonempty output directory: {out}")
    out.mkdir(parents=True, exist_ok=True)
    captures = []
    if args.offline_from:
        oldmanifest = json.loads((args.offline_from / "manifest.json").read_text(encoding="utf8"))
        refresh = set(args.refresh_series.split(",")) if args.refresh_series else set()
        known = {s["series"] for s in SOURCES}
        if refresh - known:
            raise ValueError(f"Unknown refresh series: {refresh - known}")
        for meta in oldmanifest["sources"]:
            src = args.offline_from / meta["normalized_file"]
            if sha(src.read_bytes()) != meta["normalized_sha256"]:
                raise ValueError(f"Normalized capture hash mismatch: {src}")
            if meta["series"] in refresh:
                newdata, newmeta = fetch_one(next(s for s in SOURCES if s["series"] == meta["series"]))
                newmeta["prior_capture_receipt"] = str(args.offline_from / "manifest.json")
                captures.append((newdata, newmeta))
            else:
                captures.append((pd.read_csv(src), {**meta, "offline_replay_of": str(src)}))
    else:
        if args.refresh_series:
            raise ValueError("--refresh-series requires --offline-from")
        with ThreadPoolExecutor(max_workers=4) as executor:
            captures = list(executor.map(fetch_one, SOURCES))
    manifest, ntto = [], pd.DataFrame(columns=COLS)
    for data, meta in captures:
        if data.empty and meta["series"] == "costar_us_weekly":
            excerpt_file = HERE / "public_web_extracts.csv"
            excerpt = pd.read_csv(excerpt_file)
            excerpt = excerpt[excerpt.source_url.eq(meta["url"]) & excerpt.series.eq(meta["series"])]
            if len(excerpt):
                spec = next(s for s in SOURCES if s["series"] == meta["series"])
                data = finalize_rows(spec, excerpt.to_dict("records"), datetime.now(timezone.utc).isoformat())
                meta.update(status="web_excerpt_fallback", published_rows=int(data.published_on.notna().sum()),
                            first_period=data.period.min(), last_period=data.period.max(),
                            fallback_basis="Four national figures transcribed from official dated page through web fetch; static excerpt, not an automated weekly refresh",
                            excerpt_path=str(excerpt_file.relative_to(ROOT)), excerpt_sha256=sha(excerpt_file.read_bytes()))
        file = f"{meta['series']}.csv"
        data.to_csv(out / file, index=False)
        meta.update(normalized_file=file, normalized_sha256=sha((out / file).read_bytes()), rows=len(data))
        manifest.append(meta)
        if meta["series"] == "ntto":
            ntto = data
        print(f"{meta['series']}: HTTP {meta.get('http_status')} {len(data)} rows; {meta['status']}", flush=True)
    admission = backtest(ntto, out)
    record = dict(created_at_utc=datetime.now(timezone.utc).isoformat(), schema_version="C2-1.0", sources=manifest,
                  command="python analysis/src/forecast_methods/macro_pulls/run.py", code_sha256=sha(Path(__file__).read_bytes()),
                  pit_admission=admission, raw_payloads_retained=False,
                  input_hashes={str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in [ROOT / "data/processed/q3nowcast/G/G_quarterly_panel.csv", ROOT / "data/processed/forecast_methods/harness/targets.csv"]})
    (out / "manifest.json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf8")
    print(f"Output: {out}", flush=True)


if __name__ == "__main__":
    main()
