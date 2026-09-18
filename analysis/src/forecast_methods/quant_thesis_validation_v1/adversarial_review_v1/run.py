"""Independent economic equation/endpoint review; no imports of the author's code."""
import argparse
import csv
import hashlib
import io
import json
import math
import subprocess
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
COMMIT="29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70"
BASE=ROOT/"data/processed/forecast_methods/quant_thesis_validation_v1"
E=BASE/"economics_v1/results_v2"
MODEL="data/processed/forecast_methods/lane4_model_v1/snapshot_v4"
REV="data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1"


def sha(data):return hashlib.sha256(data).hexdigest()
def git(path):return subprocess.check_output(["git","show",f"{COMMIT}:{path}"],cwd=ROOT)
def csvrows(data):return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
def read(name):return csvrows((E/name).read_bytes())
def frac(d,a,b):return max(0,min(1,(d-a).days/(b-a).days))
def dump(path,obj):path.write_text(json.dumps(obj,indent=2)+"\n",encoding="utf-8")


def run(out):
    if out.exists():raise FileExistsError("Review output must be new")
    sources={p:git(p) for p in (MODEL+"/annual.csv",MODEL+"/model_input.json",REV+"/forecast.csv",REV+"/consensus_selection.csv")}
    inp=json.loads(sources[MODEL+"/model_input.json"])
    g=inp["globals"];h1=inp["h1"]
    annual={}
    for r in csvrows(sources[MODEL+"/annual.csv"]):
        annual[(r["scenario"],int(r["year"]))]={k:float(v) for k,v in r.items() if k!="scenario"}
    reference={y:annual[("review_with_k",y)] for y in (2026,2027)}
    forecast=[r for r in csvrows(sources[REV+"/forecast.csv"]) if r["quarter"]=="2026Q4" and r["scenario"]=="review_with_k"][0]
    street=[r for r in csvrows(sources[REV+"/consensus_selection.csv"]) if r["panel_family"]=="LSEG family"][0]
    own=float(forecast["revenue_musd"]);gap=own-float(street["value"])
    checks=[]
    def check(group,key,expected,actual):
        residual=float(actual)-float(expected)
        checks.append(dict(group=group,key=key,n=1,independent=float(expected),published=float(actual),difference=residual,passes=abs(residual)<1e-6))
    # Independently reconstruct annual financial statements and cash/share flow increments.
    for (scenario,y),r in annual.items():
        p=inp["inputs"][str(y)]
        cash_cost=sum(r[k] for k in ("cor","ops","pd","bpm","fop","ga","nb_cost","ai_cost"))
        adj=min(r["revenue"]-cash_cost+r["revenue"]*p["addback_pct"],g["margin_cap"]*r["revenue"])
        op=adj-r["sbc"]-r["revenue"]*p["addback_pct"]
        ni=(op+r["interest_income"]-r["interest_expense"])*(1-p["eff_tax_rate"])
        fcf=adj+r["interest_income"]-r["interest_expense"]+r["revenue"]*(p["d_unearned_pct"]+p["wc_resid_pct"]-p["cash_tax_pct"]-p["capex_pct"])
        prev=annual.get((scenario,y-1))
        cash0=prev["net_cash"] if prev else g["net_cash_2q26"]
        shares0=prev["shares"] if prev else g["shares_2q26"]
        fcf_increment=fcf-(h1["fcf"] if y==2026 else 0)
        bb_increment=r["buybacks"]-(h1["buybacks"] if y==2026 else 0)
        wh_increment=r["sbc"]*g["withholding_pct"]-(h1["withholding"] if y==2026 else 0)
        sbc_increment=r["sbc"]-(h1["sbc"] if y==2026 else 0)
        netcash=cash0+fcf_increment-bb_increment-wh_increment
        shares=shares0+(sbc_increment*(1-g["withholding_pct"])-bb_increment)/r["price"]
        for name,value in (("cash_costs",cash_cost),("adj_ebitda",adj),("op_income",op),("net_income",ni),("fcf",fcf),("sbc_adj_fcf",fcf-r["sbc"]),("net_cash",netcash),("shares",shares)):
            check("annual_source",f"{scenario}:{y}:{name}",value,r[name])
    def endpoint(d):
        # Integrate cash/share flows from source June2026 balances; do not interpolate the author's endpoint outputs.
        a,b=reference[2026],reference[2027]
        h2=frac(d,date(2026,6,30),date(2026,12,31));y27=frac(d,date(2026,12,31),date(2027,12,31))
        cash=g["net_cash_2q26"]+h2*(a["fcf"]-h1["fcf"]-a["buybacks"]+h1["buybacks"]-a["sbc"]*g["withholding_pct"]+h1["withholding"])+y27*(b["fcf"]-b["buybacks"]-b["sbc"]*g["withholding_pct"])
        shares=g["shares_2q26"]+h2*((a["sbc"]-h1["sbc"])*(1-g["withholding_pct"])-(a["buybacks"]-h1["buybacks"]))/a["price"]+y27*(b["sbc"]*(1-g["withholding_pct"])-b["buybacks"])/b["price"]
        return cash,shares,(g["exit_ev_ebitda"]*b["adj_ebitda"]+cash)/shares
    for r in read("cash_share_horizons.csv"):
        cash,shares,value=endpoint(date.fromisoformat(r["endpoint"]))
        for name,v in (("cash_usdm",cash),("shares_m",shares),("conditional_value_usd",value)):
            check("endpoint",r["endpoint"]+":"+name,v,r[name])
    # Recompute lower-revenue counterfactual statement levels, then difference; do not reuse author marginal formulas.
    impacts={}
    for r in read("annual_operating_contrast.csv"):
        y=int(r["year"]);base=reference[y];p=inp["inputs"][str(y)];eta=float(r["cash_cost_response_eta"])
        dg=gap if y==2026 else (gap/own*base["revenue"] if r["persistence"]!="q4_only" else 0)
        rr=base["revenue"]-dg
        countercost=base["cash_costs"]-eta*dg-p["ai_referral_pct"]*dg
        counteraddback=rr*p["addback_pct"]
        counteradj=min(rr-countercost+counteraddback,rr*g["margin_cap"])
        countersbc=base["sbc"]*(rr/base["revenue"]) if r["sbc_response"]=="proportional" else base["sbc"]
        counterop=counteradj-counteraddback-countersbc
        counterni=(counterop+base["interest_income"]-base["interest_expense"])*(1-p["eff_tax_rate"])
        counterfcf=counteradj+base["interest_income"]-base["interest_expense"]+rr*(p["d_unearned_pct"]+p["wc_resid_pct"]-p["cash_tax_pct"]-p["capex_pct"])
        da=base["adj_ebitda"]-counteradj;dn=base["net_income"]-counterni;df=base["fcf"]-counterfcf;ds=base["sbc"]-countersbc
        dcash=df-g["withholding_pct"]*ds
        dissue=ds*(1-g["withholding_pct"])/base["price"]
        key=(r["persistence"],eta,r["sbc_response"],y)
        impacts[key]=(dcash,dissue,da)
        for col,v in (("revenue_gap_usdm",dg),("adj_ebitda_gap_usdm",da),("net_income_gap_usdm",dn),("fcf_gap_usdm",df),("sbc_gap_usdm",ds),("withholding_gap_usdm",g["withholding_pct"]*ds),("net_issuance_gap_m",dissue),("retained_corporate_cash_gap_usdm",dcash)):
            check("operating_counterfactual",str(key)+":"+col,v,r[col])
    for r in read("horizon_operating_contrast.csv"):
        d=date.fromisoformat(r["endpoint"]);basekey=(r["persistence"],float(r["cash_cost_response_eta"]),r["sbc_response"])
        x=impacts[basekey+(2026,)];y=impacts[basekey+(2027,)]
        a=frac(d,date(2026,9,30),date(2026,12,31));b=frac(d,date(2026,12,31),date(2027,12,31))
        cash,shares,value=endpoint(d)
        counter=(g["exit_ev_ebitda"]*(reference[2027]["adj_ebitda"]-y[2])+cash-a*x[0]-b*y[0])/(shares-a*x[1]-b*y[1])
        check("horizon_operating_counterfactual",str(basekey)+":"+str(d),value-counter,r["economic_difference_usd_per_share"])
    for r in read("multiple_cash_share_sensitivity.csv"):
        cash,shares,value=endpoint(date.fromisoformat(r["endpoint"]))
        new=(float(r["multiple"])*reference[2027]["adj_ebitda"]+cash+float(r["cash_change_usdm"]))/ (shares*(1+float(r["share_change_pct"])/100))
        check("multiple_cash_share",r["endpoint"]+":"+r["multiple"]+":"+r["cash_change_usdm"]+":"+r["share_change_pct"],new,r["conditional_value_usd"])
    for r in read("horizon_convention.csv"):
        cash,shares,value=endpoint(date.fromisoformat(r["endpoint"]))
        b=reference[2027]
        for col,v in (("break_even_multiple_to_historical_181_94",(g["price"]*shares-cash)/b["adj_ebitda"]),("per_share_per_multiple_turn",b["adj_ebitda"]/shares),("per_share_per_1bn_cash",1000/shares)):
            check("break_even_convention",r["endpoint"]+":"+col,v,r[col])
    for r in read("repurchase_price_sensitivity.csv"):
        d=date.fromisoformat(r["endpoint"]);cash,_,_=endpoint(d);b=reference[2027]
        at_yearend_shares=endpoint(date(2026,12,31))[1]
        y27=frac(d,date(2026,12,31),date(2027,12,31))
        price=b["price"]*(1+float(r["price_assumption_shift_pct"])/100)
        shares=at_yearend_shares+y27*(b["sbc"]*(1-g["withholding_pct"])-b["buybacks"])/price
        for col,v in (("modeled_shares_m",shares),("corporate_cash_usdm",cash),("conditional_value_usd",(g["exit_ev_ebitda"]*b["adj_ebitda"]+cash)/shares)):
            check("repurchase_price",r["endpoint"]+":"+r["price_assumption_shift_pct"]+":"+col,v,r[col])
    checks_ok=all(x["passes"] for x in checks)
    out.mkdir(parents=True)
    with (out/"independent_checks.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,list(checks[0]));w.writeheader();w.writerows(checks)
    receipt=dict(review="independent counterfactual-level financial and cash-flow integration",
        code_imported_from_author=False,l4_commit=COMMIT,checks=len(checks),all_checks_pass=checks_ok,
        max_absolute_difference=max(abs(x["difference"]) for x in checks),empirical_validation_n=0,estimated_parameters=0,
        q4_revenue_gap_musd=gap,source_hashes={p:sha(b) for p,b in sources.items()},
        reviewed_author_file_hashes={p.name:sha(p.read_bytes()) for p in sorted(E.iterdir()) if p.is_file()},
        source_code_sha256=sha(Path(__file__).read_bytes()),
        source_limitations=["Weighted-average starting shares remain proxy", "No actual future endpoint cash/shares", "Marginal cash-tax and addback conventions drive eta1 artifacts", "No current stock/consensus adoption"])
    dump(out/"receipt.json",receipt)
    if not checks_ok:raise AssertionError("Independent economic comparison failed; evidence preserved")
    print(json.dumps({k:v for k,v in receipt.items() if k not in ("source_hashes","reviewed_author_file_hashes")},indent=2))


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--out",required=True,type=Path)
    run(ap.parse_args().out.resolve())
