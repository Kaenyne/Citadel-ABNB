"""Small, fixed Phase-A collection for the three preregistered no-key signals.

No outcome values are used in signal construction. Network responses are cached.
"""
from __future__ import annotations

import csv
import hashlib
import json
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup
from scrapling.fetchers import Fetcher

ROOT = Path(__file__).resolve().parents[3]
RUN = Path(__file__).resolve().parent
RAW = RUN / "raw"
RAW.mkdir(parents=True, exist_ok=True)
UA = "ABNB-alt-data-research/0.1 (+https://github.com/theomachado05/airbnb-citadel-2026)"
COLLECTED = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


targets = list(csv.DictReader((RUN / "target_panel.csv").open(newline="", encoding="utf-8")))
release_catalog_path = RAW / "h10_releaseDates.json"
release_catalog_bytes = release_catalog_path.read_bytes()
release_catalog = json.loads(release_catalog_bytes)
release_dates = sorted(
    datetime.strptime(raw, "%Y%m%d").date()
    for year in release_catalog
    for month in year["Months"]
    for raw in month["Dates"]
)

# Exactly three dated pages per cutoff: latest and closest releases no later than
# 21 and 28 days before it. This is enough to identify the fixed-window endpoints.
needed: set[date] = set()
for target in targets:
    cutoff = parse_utc(target["guidance_available_at_utc"])
    eligible_releases = [d for d in release_dates if d <= cutoff.date()]
    latest = eligible_releases[-1]
    needed.add(latest)
    for lag in (21, 28):
        candidates = [d for d in eligible_releases if d <= latest - timedelta(days=lag)]
        needed.add(candidates[-1])

h10_observations: list[dict[str, object]] = []
h10_prov: list[dict[str, object]] = []
session = requests.Session()
session.headers.update({"User-Agent": UA})
for i, release_day in enumerate(sorted(needed)):
    url = f"https://www.federalreserve.gov/releases/h10/{release_day:%Y%m%d}/"
    path = RAW / f"h10_{release_day:%Y%m%d}.html"
    if path.exists():
        content = path.read_bytes()
        status = 200
    else:
        response = session.get(url, timeout=30)
        status = response.status_code
        response.raise_for_status()
        content = response.content
        path.write_bytes(content)
        if i + 1 < len(needed):
            time.sleep(6.1)  # never exceed ten requests/minute
    soup = BeautifulSoup(content, "html.parser")
    broad = next((th for th in soup.find_all("th") if th.get_text(" ", strip=True).endswith("BROAD")), None)
    if broad is None:
        raise RuntimeError(f"BROAD row missing from {url}")
    row = broad.parent
    values = [td.get_text(" ", strip=True) for td in row.find_all("td")][1:]
    headers = [th.get_text(" ", strip=True) for th in soup.select("table.statistics thead th")][2:]
    for label, raw_value in zip(headers, values):
        if raw_value in {"ND", "NA", ""}:
            continue
        parsed = datetime.strptime(label.replace(".", ""), "%b %d")
        year = release_day.year
        if parsed.month == 12 and release_day.month == 1:
            year -= 1
        obs_day = date(year, parsed.month, parsed.day)
        released = datetime.combine(release_day, datetime.min.time(), ZoneInfo("America/New_York")).replace(hour=16, minute=15).astimezone(timezone.utc)
        h10_observations.append({
            "source_id": "FED_H10_DTWEXBGS", "observation_date": obs_day.isoformat(),
            "reference_period": obs_day.isoformat(), "first_published_at_utc": released.isoformat().replace("+00:00", "Z"),
            "inferred_available_at_utc": "", "revised_at_utc": "", "vintage_id": release_day.isoformat(), "value": raw_value,
            "unit": "index_Jan_2006_100", "source_url": url, "collected_at_utc": COLLECTED,
            "source_sha256": sha(content),
        })
    h10_prov.append({"source_id": "FED_H10_DTWEXBGS", "artifact_path": str(path.relative_to(ROOT)), "source_url": url, "retrieved_at_utc": COLLECTED, "sha256": sha(content), "http_status": status})

# ECB no-key SDMX response, with the API's history flag retained in the URL.
ecb_params = {"startPeriod": "2021-01-01", "endPeriod": "2026-08-06", "format": "csvdata", "includeHistory": "true"}
ecb_url = "https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?" + urlencode(ecb_params)
ecb_resp = session.get(ecb_url, timeout=60)
ecb_resp.raise_for_status()
ecb_bytes = ecb_resp.content
ecb_path = RAW / "ecb_exr_d_usd_eur_history.csv"
ecb_path.write_bytes(ecb_bytes)
ecb_rows = list(csv.DictReader(ecb_bytes.decode("utf-8-sig").splitlines()))
ecb_observations: list[dict[str, object]] = []
for row in ecb_rows:
    period = row.get("TIME_PERIOD", "")
    value = row.get("OBS_VALUE", "")
    if not period or not value:
        continue
    obs_day = date.fromisoformat(period)
    # Conservative sensitivity only: 16:00 UTC is one or two hours later than
    # the ECB's usual around-16:00-CET/CEST publication. It is deliberately not
    # written into first_published_at_utc.
    released = datetime.combine(obs_day, datetime.min.time(), timezone.utc).replace(hour=16)
    ecb_observations.append({
        "source_id": "ECB_EXR_USD_EUR", "observation_date": period, "reference_period": period,
        "first_published_at_utc": "", "inferred_available_at_utc": released.isoformat().replace("+00:00", "Z"), "revised_at_utc": "",
        "vintage_id": row.get("ACTION", "includeHistory=true") or "includeHistory=true", "value": value,
        "unit": "USD_per_EUR", "source_url": ecb_url, "collected_at_utc": COLLECTED,
        "source_sha256": sha(ecb_bytes),
    })

# BLS no-key API: retain the response, but deliberately leave release timestamps
# unresolved. Current values are never converted into eligible historical features.
bls_url = "https://api.bls.gov/publicAPI/v1/timeseries/data/CUUR0000SEHB02?startyear=2020&endyear=2026"
bls_resp = session.get(bls_url, timeout=60)
bls_resp.raise_for_status()
bls_bytes = bls_resp.content
bls_path = RAW / "bls_cuur0000sehb02_v1.json"
bls_path.write_bytes(bls_bytes)

# One permitted Scrapling request, only after the deterministic audit gate passed.
bls_doc_url = "https://www.bls.gov/developers/api_faqs.htm"
bls_doc_path = RAW / "bls_api_faqs_scrapling.html"
if bls_doc_path.exists():
    bls_doc_bytes = bls_doc_path.read_bytes()
    bls_doc_status = 403 if b"Access Denied" in bls_doc_bytes else 200
else:
    page = Fetcher.get(bls_doc_url, stealthy_headers=False, headers={"User-Agent": UA}, timeout=30)
    bls_doc_bytes = bytes(page.body)
    bls_doc_status = page.status
    bls_doc_path.write_bytes(bls_doc_bytes)

raw_rows = h10_observations + ecb_observations
raw_fields = ["source_id", "observation_date", "reference_period", "first_published_at_utc", "inferred_available_at_utc", "revised_at_utc", "vintage_id", "value", "unit", "source_url", "collected_at_utc", "source_sha256"]
write_csv(RUN / "raw_observations.csv", raw_fields, raw_rows)

feature_rows: list[dict[str, object]] = []
for target in targets:
    cutoff = parse_utc(target["guidance_available_at_utc"])
    for signal_id, source_id, observations, expected, unit, geography, strict in [
        ("H-001", "FED_H10_DTWEXBGS", h10_observations, "negative", "percent", "broad_trade_weighted_USD", True),
        ("H-002", "ECB_EXR_USD_EUR", ecb_observations, "positive", "percent", "euro_area_proxy", False),
    ]:
        availability_field = "first_published_at_utc" if strict else "inferred_available_at_utc"
        eligible_obs = [o for o in observations if o[availability_field] and parse_utc(str(o[availability_field])) < cutoff]
        latest_day = max(date.fromisoformat(str(o["observation_date"])) for o in eligible_obs)
        window_start = latest_day - timedelta(days=28)
        window = sorted((o for o in eligible_obs if date.fromisoformat(str(o["observation_date"])) >= window_start), key=lambda o: str(o["observation_date"]))
        first, last = window[0], window[-1]
        transformed = (float(last["value"]) / float(first["value"]) - 1.0) * 100.0
        feature_rows.append({
            "prediction_id": target["prediction_id"], "cohort": target["cohort"],
            "issuing_fiscal_period": target["issuing_fiscal_period"], "guided_fiscal_period": target["guided_fiscal_period"],
            "guidance_cutoff_at_utc": target["guidance_available_at_utc"], "signal_id": signal_id, "source_id": source_id,
            "fixed_formula": "pct_change_first_to_last_eligible_observation_fixed_28_calendar_days",
            "observation_window_start": window_start.isoformat(), "observation_window_end": latest_day.isoformat(),
            "latest_eligible_release_utc": last["first_published_at_utc"],
            "inferred_sensitivity_available_at_utc": last["inferred_available_at_utc"], "vintage": last["vintage_id"],
            "raw_first_value": first["value"], "raw_last_value": last["value"], "feature_value": f"{transformed:.8f}",
            "unit": unit, "geography": geography, "expected_direction": expected, "eligible": "true" if strict else "false",
            "exclusion_reason": "" if strict else "strict PIT ineligible: API response does not expose exact initial publication timestamp; 16:00 Europe/Frankfurt is retained only as a pre-fixed sensitivity assumption",
            "sensitivity_eligible": "true", "sensitivity_rule": "" if strict else "conservatively assume availability at 16:00 UTC on observation day, later than usual around-16:00 CET/CEST publication",
            "availability_evidence_url": last["source_url"], "collected_at_utc": COLLECTED,
            "source_sha256": last["source_sha256"],
        })
    feature_rows.append({
        "prediction_id": target["prediction_id"], "cohort": target["cohort"],
        "issuing_fiscal_period": target["issuing_fiscal_period"], "guided_fiscal_period": target["guided_fiscal_period"],
        "guidance_cutoff_at_utc": target["guidance_available_at_utc"], "signal_id": "H-003", "source_id": "BLS_CPI_LODGING",
        "fixed_formula": "delta_latest_eligible_yoy_cpi_vs_prior_quarter_cutoff", "observation_window_start": "",
        "observation_window_end": "", "latest_eligible_release_utc": "", "inferred_sensitivity_available_at_utc": "", "vintage": "", "raw_first_value": "",
        "raw_last_value": "", "feature_value": "", "unit": "percentage_points", "geography": "US_city_average",
        "expected_direction": "positive", "eligible": "false",
        "exclusion_reason": "historical BLS release timestamp not independently verified; current API values cannot be backfilled",
        "sensitivity_eligible": "false", "sensitivity_rule": "none; release calendar unavailable for lawful automated historical reconstruction",
        "availability_evidence_url": "https://www.bls.gov/schedule/news_release/cpi.htm", "collected_at_utc": COLLECTED,
        "source_sha256": sha(bls_bytes),
    })

feature_fields = list(feature_rows[0])
write_csv(RUN / "point_in_time_feature_panel.csv", feature_fields, feature_rows)
prov_rows = h10_prov + [
    {"source_id": "ECB_EXR_USD_EUR", "artifact_path": str(ecb_path.relative_to(ROOT)), "source_url": ecb_url, "retrieved_at_utc": COLLECTED, "sha256": sha(ecb_bytes), "http_status": ecb_resp.status_code},
    {"source_id": "BLS_CPI_LODGING", "artifact_path": str(bls_path.relative_to(ROOT)), "source_url": bls_url, "retrieved_at_utc": COLLECTED, "sha256": sha(bls_bytes), "http_status": bls_resp.status_code},
    {"source_id": "BLS_CPI_LODGING", "artifact_path": str(bls_doc_path.relative_to(ROOT)), "source_url": bls_doc_url, "retrieved_at_utc": COLLECTED, "sha256": sha(bls_doc_bytes), "http_status": bls_doc_status},
    {"source_id": "FED_H10_DTWEXBGS", "artifact_path": str(release_catalog_path.relative_to(ROOT)), "source_url": "https://www.federalreserve.gov/releases/h10/", "retrieved_at_utc": COLLECTED, "sha256": sha(release_catalog_bytes), "http_status": 200},
]
write_csv(RUN / "collection_provenance.csv", ["source_id", "artifact_path", "source_url", "retrieved_at_utc", "sha256", "http_status"], prov_rows)

print(json.dumps({"collected_at": COLLECTED, "h10_pages": len(h10_prov), "h10_observations": len(h10_observations), "ecb_observations": len(ecb_observations), "feature_rows": len(feature_rows), "bls_eligible_rows": 0, "scrapling_sha256": sha(bls_doc_bytes)}))
