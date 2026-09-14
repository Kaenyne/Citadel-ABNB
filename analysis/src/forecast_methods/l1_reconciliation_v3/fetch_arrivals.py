"""Explicit public downloads; no crawling, credentials, raw stores or paid data.

Raw payloads live in memory. Only normalized monthly aggregates and manifests
are written. Current revisions carry retrieval dates, never invented vintages.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import io
import json
import re
import zipfile
import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data/processed/forecast_methods/l1_reconciliation_v3"
SOURCES = {
    "ntto": "https://www.trade.gov/sites/default/files/2024-06/Monthly%20Arrivals%202000%20to%20Present%20%E2%80%93%20Country%20of%20Residence%20%28COR%29_1.xlsx",
    "jnto": "https://www.jnto.go.jp/statistics/data/_files/20260819_1615-5.xlsx",
    "datatur": "https://datatur.sectur.gob.mx/Documentoscompartidos/cuentaviajeros/BD_CuentaViajeros_descarga.zip",
}
for country in ["ES", "FR", "IT", "DE"]:
    SOURCES[f"eurostat_{country}"] = f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tour_occ_nim?lang=en&geo={country}&unit=NR&c_resid=FOR&nace_r2=I551-I553&sinceTimePeriod=2021-01"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat()
    rows, manifest = [], []
    for name, url in SOURCES.items():
        item = dict(series=name, url=url, retrieved_at=stamp, vintage_basis="current_revised_download; not historical release", raw_retained=False)
        start = len(rows)
        try:
            r = requests.get(url, timeout=35)
            item.update(http_status=r.status_code, bytes=len(r.content), sha256=hashlib.sha256(r.content).hexdigest())
            r.raise_for_status()
            def add(month, value, region, unit="persons"):
                if pd.notna(value) and float(value)>0 and str(month)[:4]>="2021":
                    rows.append(dict(series=name, region=region, month=str(month)[:7], value=float(value), unit=unit, knowable_from=stamp[:10], source_url=url, vintage_basis=item["vintage_basis"]))
            if name == "ntto":
                d = pd.read_excel(io.BytesIO(r.content), sheet_name="Monthly", header=None)
                ix = d.index[d[1].astype(str).str.strip() == "TOTAL ALL COUNTRIES"]
                if len(ix)!=1: raise ValueError("NTTO total row is ambiguous")
                for j in range(3, d.shape[1]):
                    m = re.match(r"^(20\d\d)-(\d{1,2})", str(d.iloc[0,j]))
                    if m: add(f"{m[1]}-{int(m[2]):02}", pd.to_numeric(d.iloc[ix[0],j],errors="coerce"), "na")
                item["coverage"]="All source countries to US; arrivals by country of residence; aggregate proxy excludes domestic and non-US NA"
            elif name == "jnto":
                x = pd.ExcelFile(io.BytesIO(r.content))
                for year in [s for s in x.sheet_names if s.isdigit() and int(s)>=2021]:
                    d=pd.read_excel(x,sheet_name=year,header=None)
                    ix=d.index[d[0].astype(str).str.strip()=="総数"]
                    if len(ix)!=1: raise ValueError("JNTO total row is ambiguous")
                    for month in range(1,13): add(f"{year}-{month:02}",pd.to_numeric(d.iloc[ix[0],2*month],errors="coerce"),"apac")
                item["coverage"]="Japan inbound all origins; excludes domestic Japan and rest of APAC"
            elif name.startswith("eurostat"):
                d=r.json(); item["api_updated"]=d.get("updated")
                if np.prod(d["size"][:-1])!=1: raise ValueError("Unexpected Eurostat dimensions")
                time=d["dimension"]["time"]["category"]["index"]
                for month,i in time.items(): add(month,d["value"].get(str(i),np.nan),"emea","accommodation_nights_nonresidents")
                item["coverage"]="Nonresident accommodation nights; destination-specific proxy, not ABNB bookings or visitor arrivals"
            else:
                z=zipfile.ZipFile(io.BytesIO(r.content)); x=next(n for n in z.namelist() if n.endswith('.xlsx'))
                d=pd.read_excel(io.BytesIO(z.read(x)))
                item["tipo_values"]=sorted(d.Tipo.astype(str).unique().tolist())
                # This advertised workbook is receipts, not a count. Never mix units.
                item["rejected_reason"]="Downloaded Cuenta de Viajeros workbook reports monetary receipts/expenses; no verified count-unit series admitted"
        except Exception as exc:
            item["error"]=f"{type(exc).__name__}: {str(exc)[:250]}"
        item["normalized_rows"]=len(rows)-start
        manifest.append(item)
        print(name,item.get("http_status"),item["normalized_rows"],item.get("rejected_reason",item.get("error","ok")),flush=True)
    # These complementary series are omitted, not imputed from different regions.
    manifest.extend([dict(series="Australia_ABS",url="https://www.abs.gov.au/statistics/industry/tourism-and-transport/overseas-arrivals-and-departures-australia",normalized_rows=0,rejected_reason="Not pulled; JNTO is not treated as a full APAC proxy"),
                     dict(series="Brazil",url="https://www.gov.br/turismo/pt-br/assuntos/dados-e-fatos",normalized_rows=0,rejected_reason="No dated monthly count series integrated in this run; Latin America remains without an arrivals coefficient")])
    pd.DataFrame(rows).to_csv(OUT/"arrivals_monthly_current.csv",index=False)
    (OUT/"arrivals_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf8")


if __name__=="__main__": main()
