"""Independent arithmetic/source-join checks. Imports no candidate/event functions."""
import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]

def read(relative):
    with (ROOT / relative).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(x for x in f if not x.startswith("#")))

def number(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return float("nan")

def cq(q):
    return q if q[:4].isdigit() else f"20{q[-2:]}Q{q[0]}"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True)
    p.add_argument("--model", default="data/processed/forecast_methods/gbv_event_v1/integration_v1/model.json")
    p.add_argument("--events", default="data/processed/forecast_methods/gbv_event_v1/events_v1/run_v2")
    a = p.parse_args()
    if not a.name.replace("_", "").isalnum():
        raise ValueError("new simple output name required")
    output = ROOT / "data/processed/forecast_methods/gbv_event_v1/sources_v1" / a.name
    output.mkdir(parents=True, exist_ok=False)
    checks = []
    def check(scope, cell, observed, expected, tolerance=1e-8):
        delta = abs(observed-expected)
        checks.append(dict(scope=scope, cell=cell, observed=observed, expected=expected,
                           abs_error=delta, tolerance=tolerance, passed=delta <= tolerance))
    model = json.loads((ROOT/a.model).read_text())
    for row in model["forecast"]:
        q = row["quarter"]
        history = sorted((r for r in model["lambda_history"] if int(r["season"]) == int(q[-1])), key=lambda r:r["quarter"])
        w = [math.pow(0.5, (len(history)-1-i)/2) for i in range(len(history))]
        lam = sum(number(r["lambda_pct"])*z for r,z in zip(history,w))/sum(w)/100
        weighted = (2*row["lag1_gbv_musd"]+row["lag2_gbv_musd"])/3
        revenue = lam*weighted
        guide = revenue/(1+row["cushion_decimal"])
        for key, expected in (("lambda_decimal",lam),("weighted_gbv_musd",weighted),("revenue_musd",revenue),("implied_guide_musd",guide)):
            check("integration",f"{q}:{key}",row[key],expected)
    forecasts = {r["quarter"]:r for r in model["forecast"]}
    for row in model["comparisons"]:
        f = forecasts[row["quarter"]]
        c = row["consensus_revenue_musd"]
        check("comparison",row["register_id"]+":revenue_gap",row["revenue_gap_musd"],f["revenue_musd"]-c)
        check("comparison",row["register_id"]+":implied_guide_gap",row["implied_guide_gap_musd"],(f["revenue_musd"]-c)/(1+f["cushion_decimal"]))

    daily_path = "data/processed/forecast_methods/returns_v1/ohlc_daily.csv"
    cal_path = "data/processed/forecast_methods/harness/calendar.csv"
    kpi_path = "data/processed/overnight/02_kpi_panel_quarterly.csv"
    reg_path = "data/processed/forecast_methods/L0/L0_vintage_register.csv"
    prices = read(daily_path)
    by_ticker = {t:sorted((r for r in prices if r["ticker"]==t),key=lambda r:r["date"]) for t in ("ABNB","QQQ")}
    cal = read(cal_path)
    published = {r["print_quarter"]:r["print_date"] for r in cal if r["print_date_basis"]=="ledger"}
    revenue = {cq(r["quarter"]):number(r["revenue_musd"]) for r in read(kpi_path)}
    cushion_history = [(published[r["next_quarter_guided"]],r["next_quarter_guided"],revenue[r["next_quarter_guided"]]/number(r["guide_mid"])-1) for r in cal if r["next_quarter_guided"] in published and math.isfinite(number(r["guide_mid"]))]
    reg = read(reg_path)
    reg_ids = {r["register_id"]:r for r in reg}
    events = read(a.events+"/event_panel.csv")
    for event in events:
        d,q = event["event_date"][:10],event["print_quarter"]
        values = {}
        for t, px in by_ticker.items():
            i = next(i for i,r in enumerate(px) if r["date"]>d)
            pre, op, cl = number(px[i-1]["close"]),number(px[i]["open"]),number(px[i]["close"])
            values[t] = dict(gap=100*(op/pre-1),session=100*(cl/op-1),cc=100*(cl/pre-1),open_5d=100*(number(px[i+4]["close"])/op-1),open_20d=100*(number(px[i+19]["close"])/op-1))
            check("event_date",q+":"+t+":preclose",float(px[i-1]["date"].replace("-","")),float(d.replace("-","")),0)
        for leg in ("gap","session","cc","open_5d","open_20d"):
            check("daily_return",q+":"+leg,number(event[leg+"_excess_pct"]),values["ABNB"][leg]-values["QQQ"][leg])
        eligible = sorted(x for x in cushion_history if x[0]<d)[-8:]
        check("cushion",q+":n",number(event["cushion_n"]),len(eligible),0)
        if len(eligible)>=3:
            check("cushion",q+":median",number(event["preevent_cushion"]),statistics.median(x[2] for x in eligible))
        key = event["consensus_register_id"]
        if key:
            r = reg_ids[key]
            ok = r["role"]=="pre_guide" and r["pit_usable"].lower()=="true" and r["vendor_attributed"].lower()=="true" and r["as_of_timestamp"][:10]<=d
            check("consensus",q+":original_eligible",int(ok),1,0)
            check("consensus",q+":value",number(event["consensus_revenue_musd"]),number(r["value"]))
    early = read(a.events+"/pre_event_forecast_join.csv")
    for row in early:
        origin = row["origin_date"][:10]
        candidates = [r for r in reg if r["vendor"]=="DoltHub post-no-preference/earnings" and r["role"]=="pit_history" and r["metric"]=="revenue" and r["period"]==row["target_quarter"] and r["pit_usable"].lower()=="true" and r["as_of_timestamp"][:10]<origin and number(r["value"])>0]
        if candidates:
            latest = max(candidates,key=lambda r:(r["as_of_timestamp"],r["register_id"]))
            check("origin_consensus",row["target_quarter"]+":id",int(row["origin_consensus_register_id"]==latest["register_id"]),1,0)
            check("origin_consensus",row["target_quarter"]+":value",number(row["origin_consensus_musd"]),number(latest["value"]))
    with (output/"checks.csv").open("x",encoding="utf-8",newline="") as f:
        w = csv.DictWriter(f,fieldnames=list(checks[0]));w.writeheader();w.writerows(checks)
    inputs = [a.model,a.events+"/event_panel.csv",a.events+"/pre_event_forecast_join.csv",daily_path,cal_path,kpi_path,reg_path]
    receipt = dict(checks=len(checks),passed=sum(r["passed"] for r in checks),max_abs_error=max(r["abs_error"] for r in checks),event_n=len(events),earlier_origin_rows=len(early),imports_candidate_functions=False,scope="Arithmetic and source joins only; no new fit, statistical retest, or strategy claim",source_hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in inputs})
    (output/"receipt.json").write_text(json.dumps(receipt,indent=2),encoding="utf-8")
    print(json.dumps(receipt,indent=2))
    if receipt["passed"] != len(checks):
        raise AssertionError("Independent comparison failed; see checks.csv")

if __name__ == "__main__":
    main()
