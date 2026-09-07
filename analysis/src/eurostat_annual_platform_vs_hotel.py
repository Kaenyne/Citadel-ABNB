"""Rebuild data/processed/eurostat_platform_vs_hotel_by_country_2019_2024.csv from the Eurostat API.

platform nights  tour_ce_oam   (accommod=TOTAL)          2019, 2024
hotel nights     tour_occ_ninat (nace_r2=I551, c_resid=TOTAL, unit=NR)
hotel bed places tour_cap_nat  (nace_r2=I551, accomunit=BEDPL, unit=NR)
Run from repo root: python analysis/src/eurostat_annual_platform_vs_hotel.py   (needs internet)
"""
import json, urllib.request
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[2]
API = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
NAMES = {"EU27_2020": "EU27", "BE": "Belgium", "BG": "Bulgaria", "CZ": "Czechia", "DK": "Denmark", "DE": "Germany", "EE": "Estonia", "IE": "Ireland", "EL": "Greece", "ES": "Spain", "FR": "France", "HR": "Croatia", "IT": "Italy", "CY": "Cyprus", "LV": "Latvia", "LT": "Lithuania", "LU": "Luxembourg", "HU": "Hungary", "MT": "Malta", "NL": "Netherlands", "AT": "Austria", "PL": "Poland", "PT": "Portugal", "RO": "Romania", "SI": "Slovenia", "SK": "Slovakia", "FI": "Finland", "SE": "Sweden", "IS": "Iceland", "LI": "Liechtenstein", "NO": "Norway", "CH": "Switzerland"}


def get(query):
    with urllib.request.urlopen(API + query, timeout=120) as r:
        js = json.load(r)
    gi = js["dimension"]["geo"]["category"]["index"]; v = js["value"]
    return {g: v.get(str(i)) for g, i in gi.items()}   # single-value-per-geo queries only


rows = []
for y in ("2019", "2024"):
    ce = get(f"tour_ce_oam?format=JSON&lang=EN&time={y}&accommod=TOTAL")
    hn = get(f"tour_occ_ninat?format=JSON&lang=EN&time={y}&nace_r2=I551&c_resid=TOTAL&unit=NR")
    bp = get(f"tour_cap_nat?format=JSON&lang=EN&time={y}&nace_r2=I551&unit=NR&accomunit=BEDPL")
    for g, name in NAMES.items():
        rows.append(dict(geo=g, country=name, year=y, platform_nights=ce.get(g), hotel_nights=hn.get(g), hotel_bedplaces=bp.get(g)))
d = pd.DataFrame(rows).pivot(index=["geo", "country"], columns="year")
d.columns = [f"{a}_{b}" for a, b in d.columns]; d = d.reset_index()
for y in ("2019", "2024"):
    d[f"platform_share_{y}"] = d[f"platform_nights_{y}"] / (d[f"platform_nights_{y}"] + d[f"hotel_nights_{y}"])
    d[f"hotel_bed_occupancy_{y}"] = d[f"hotel_nights_{y}"] / (d[f"hotel_bedplaces_{y}"] * 365)
    d[f"platform_nights_per_hotel_bed_{y}"] = d[f"platform_nights_{y}"] / d[f"hotel_bedplaces_{y}"]
d["platform_share_chg_pts"] = (d.platform_share_2024 - d.platform_share_2019) * 100
d["hotel_occ_chg_pts"] = (d.hotel_bed_occupancy_2024 - d.hotel_bed_occupancy_2019) * 100
d["platform_growth_19_24"] = d.platform_nights_2024 / d.platform_nights_2019 - 1
d["hotel_growth_19_24"] = d.hotel_nights_2024 / d.hotel_nights_2019 - 1
d.to_csv(ROOT / "data/processed/eurostat_platform_vs_hotel_by_country_2019_2024.csv", index=False)
print(d.round(3).to_string())
