"""Look for dated public archive captures of the fixed cross-platform pilot URLs.

The Wayback availability API returns a nearest capture, not a guaranteed before/after
capture. No archive record is unknown, never evidence that a property was absent.
The actual archived page must be inspected before treating a 200 record as presence.
"""
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import csv
import hashlib
import json
from pathlib import Path
import re
import time
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parents[2]
TARGETS={
    "SD04_vrbo":("SD-04","https://www.vrbo.com/4261004"),
    "SD04_direct":("SD-04","https://www.sandiegochecklist.com/product/7br-massive-beach-retreat-sleeps-26-steps-to-ocean/"),
    "SD04_syndicated":("SD-04","https://agreatertown.com/san-diego-ca/7-br-apartment-vacation-rental-0002131067840"),
    "SD07_direct":("SD-07","https://missionsands.com/481655/"),
    "SD07_expedia":("SD-07","https://www.expedia.com.hk/en/San-Diego-Hotels-Santa-Barbara-Loft.h112381138.Hotel-Information"),
    "SD08_aggregator":("SD-08","https://www.ehotelsreviews.com/spacious-4br-outdoor-kitchen-hot-tub-13778183-zh"),
    "SD09_vrbo":("SD-09","https://www.vrbo.com/4779972"),
    "SD09_syndicated":("SD-09","https://agreatertown.com/san-diego-ca/1-br-condo-vacation-rental-in-san-0002277079791"),
}


def capture_timing(timestamp,last_present,first_absence):
    if not re.fullmatch(r"\d{14}", timestamp):
        raise ValueError("Archive timestamp must contain exactly 14 digits")
    day=datetime.strptime(timestamp,"%Y%m%d%H%M%S").date()
    last=datetime.strptime(last_present,"%Y-%m-%d").date()
    first=datetime.strptime(first_absence,"%Y-%m-%d").date()
    if first<=last:
        raise ValueError("First qualifying absence must be after last presence")
    if day<=last:return "on_or_before_last_airbnb_presence"
    if day<first:return "inside_airbnb_exit_interval"
    return "on_or_after_first_airbnb_absence"


def probe(label,case_id,url,period,target,sample,raw):
    query="https://archive.org/wayback/available?"+urllib.parse.urlencode({"url":url,"timestamp":target})
    path=raw/f"{label}_{period}_wayback.json"
    result=dict(case_id=case_id,label=label,target_url=url,requested_period=period,requested_timestamp=target,
        last_airbnb_present=sample["last_present"],first_airbnb_absent=sample["first_terminal_absence"],
        query_url=query,accessed_at_utc=datetime.now(timezone.utc).isoformat(),query_status="",
        archived_timestamp="",archived_url="",archived_status="",actual_timing="",sha256="",error="")
    try:
        if path.exists():body=path.read_bytes()
        else:
            time.sleep(1)
            request=urllib.request.Request(query,headers={"User-Agent":"Citadel-ABNB listing-history research"})
            with urllib.request.urlopen(request,timeout=30) as h:body=h.read()
            path.write_bytes(body)
        payload=json.loads(body);result["sha256"]=hashlib.sha256(body).hexdigest()
        closest=payload.get("archived_snapshots",{}).get("closest",{})
        if not closest:
            result["query_status"]="no_accessible_capture_returned"
        else:
            result.update(query_status="capture_returned_content_unverified",archived_timestamp=closest["timestamp"],
                archived_url=closest["url"],archived_status=str(closest["status"]),
                actual_timing=capture_timing(closest["timestamp"],sample["last_present"],sample["first_terminal_absence"]))
    except Exception as exc:result.update(query_status="query_failed",error=f"{type(exc).__name__}: {exc}")
    return result


def main():
    raw=ROOT/"data/raw/listing_platform_history";raw.mkdir(exist_ok=True,parents=True)
    out=ROOT/"data/processed/listing_platform_history";out.mkdir(exist_ok=True,parents=True)
    with (ROOT/"data/raw/listing_churn_execution/destination_sample.csv").open(encoding="utf-8-sig",newline="") as h:
        sample={r["case_id"]:r for r in csv.DictReader(h)}
    rows=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs=[pool.submit(probe,label,case,url,period,target,sample[case],raw)
            for label,(case,url) in TARGETS.items() for period,target in (("before","20250901"),("after","20260401"))]
        for job in as_completed(jobs):
            r=job.result();rows.append(r)
            with (out/"archive_probe_log.csv").open("w",encoding="utf-8",newline="") as h:
                w=csv.DictWriter(h,fieldnames=list(r));w.writeheader();w.writerows(sorted(rows,key=lambda x:(x["label"],x["requested_period"])))
            print(r["label"],r["requested_period"],r["query_status"],r["archived_timestamp"],r["error"],flush=True)


if __name__=="__main__":main()
