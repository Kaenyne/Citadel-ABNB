"""C1: pull the EUROCONTROL daio yearly CSVs (raw.githubusercontent.com, keyless), write the
manifest, build the daily eu40 / eu_core flt_da aggregates and the 2025 country weights.

Build C of the GitHub alt-data integration plan, 14 Sep 2026 (compiled with Claude Code).
Copy of the govdata V protocol (analysis/src/govdata/V1_collect.py) narrowed to one source;
nothing under analysis/src/govdata/ or data/processed/govdata/ is touched.

Raw: data/raw/eurocontrol_daio/daio_YYYY.csv (gitignored; no LICENSE upstream, see the note).
Outputs (committed): data/processed/govdata_v2/raw_manifest.csv, daio_daily_aggregates.csv,
country_weights_2025.csv.
Run: python analysis/src/govdata_v2/C1_collect.py
"""
from __future__ import annotations

import hashlib
import os
import sys
import time
from datetime import datetime, timezone

import pandas as pd
import requests

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RAW = os.path.join(ROOT, "data", "raw", "eurocontrol_daio")
OUT = os.path.join(ROOT, "data", "processed", "govdata_v2")
os.makedirs(RAW, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
YEARS = list(range(2019, 2027))
URL = "https://raw.githubusercontent.com/euctrl-pru/daio/HEAD/daio_{y}.csv"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) citadel-abnb govdata_v2"}

# EU27 + UK + CH + NO in the file's own naming (Belgium and Luxembourg are one row): 29 rows.
EU_CORE = [
    "Austria", "Belgium and Luxembourg", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia",
    "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Malta",
    "Netherlands", "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden",
    "United Kingdom", "Switzerland", "Norway",
]
# excluded from eu_core (11): airspace driven by war or geopolitics rather than leisure demand
EXCLUDED = ["Israel", "Morocco", "Ukraine", "Moldova", "Georgia", "Armenia", "Turkiye", "Albania",
            "Serbia & Montenegro", "Bosnia-Herzegovina", "North Macedonia"]


def log(*a):
    print(*a, flush=True)


def read_daio(path_or_buf):
    """The files are UTF-8 except for one country name that some vintages carry in latin-1."""
    try:
        d = pd.read_csv(path_or_buf, encoding="utf-8")
    except UnicodeDecodeError:
        if hasattr(path_or_buf, "seek"):
            path_or_buf.seek(0)
        d = pd.read_csv(path_or_buf, encoding="latin-1")
    d["country_name"] = d["country_name"].astype(str).str.replace("Türkiye", "Turkiye", regex=False).str.replace("T�rkiye", "Turkiye", regex=False).str.replace("TÃ¼rkiye", "Turkiye", regex=False)
    d["entry_date"] = pd.to_datetime(d["entry_date"])
    return d


def pull():
    rows = []
    for y in YEARS:
        p = os.path.join(RAW, f"daio_{y}.csv")
        url = URL.format(y=y)
        if not (os.path.exists(p) and os.path.getsize(p) > 100_000):
            for attempt in range(3):
                try:
                    r = requests.get(url, headers=UA, timeout=120)
                    if r.status_code == 200:
                        with open(p, "wb") as f:
                            f.write(r.content)
                        break
                    log(f"  {y}: HTTP {r.status_code}")
                except Exception as e:  # noqa: BLE001
                    log(f"  {y}: {e!r}")
                time.sleep(3 + 3 * attempt)
        b = open(p, "rb").read()
        rows.append(dict(url=url, file=f"daio_{y}.csv", bytes=len(b), sha256=hashlib.sha256(b).hexdigest(),
                         pulled_at=datetime.fromtimestamp(os.path.getmtime(p), tz=timezone.utc).isoformat(timespec="seconds"),
                         rows=b.count(b"\n") - 1))
    man = pd.DataFrame(rows)
    man.to_csv(os.path.join(OUT, "raw_manifest.csv"), index=False)
    log(man[["file", "bytes", "rows"]].to_string(index=False))
    return man


def aggregates():
    d = pd.concat([read_daio(os.path.join(RAW, f"daio_{y}.csv")) for y in YEARS], ignore_index=True)
    names = set(d.country_name.unique())
    missing = [c for c in EU_CORE if c not in names]
    extra = sorted(names - set(EU_CORE) - set(EXCLUDED))
    assert not missing, f"eu_core names not in file: {missing}"
    assert not extra, f"states neither in eu_core nor excluded: {extra}"
    assert len(names) == 40, len(names)
    assert (d.flt_da < 0).sum() == 0, "negative flt_da"
    core = d[d.country_name.isin(EU_CORE)]
    agg = pd.DataFrame({
        "eu40_flt_da": d.groupby("entry_date").flt_da.sum(),
        "eu_core_flt_da": core.groupby("entry_date").flt_da.sum(),
        "eu40_flt_o": d.groupby("entry_date").flt_o.sum(),
        "n_states": d.groupby("entry_date").country_name.nunique(),
    }).sort_index()
    assert (agg.n_states == 40).all()
    agg.index.name = "entry_date"
    agg.to_csv(os.path.join(OUT, "daio_daily_aggregates.csv"), date_format="%Y-%m-%d")
    log(f"daily aggregates {agg.index.min().date()} to {agg.index.max().date()}, {len(agg)} days")
    # country weights, calendar 2025 (for WP-X)
    y25 = d[d.entry_date.dt.year == 2025].groupby(["country_icao_code", "country_name"], as_index=False).flt_da.sum()
    y25["share_pct_eu40"] = 100 * y25.flt_da / y25.flt_da.sum()
    y25["in_eu_core"] = y25.country_name.isin(EU_CORE)
    y25["share_pct_eu_core"] = (100 * y25.flt_da / y25.loc[y25.in_eu_core, "flt_da"].sum()).where(y25.in_eu_core)
    y25 = y25.sort_values("flt_da", ascending=False).reset_index(drop=True)
    y25.insert(0, "rank", range(1, len(y25) + 1))
    y25.to_csv(os.path.join(OUT, "country_weights_2025.csv"), index=False)
    log(y25.head(12).to_string(index=False))
    return agg


def main():
    pull()
    aggregates()


if __name__ == "__main__":
    main()
