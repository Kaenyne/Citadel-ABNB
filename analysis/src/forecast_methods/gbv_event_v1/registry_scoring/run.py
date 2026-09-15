"""Register seven conditional LIVE rows and redirect both unchanged scorers."""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import importlib
import io
import json
import math
import os
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[5]
METHOD="gbv-event-v1"
KEYS=["method","object","target","window","prior_basis"]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path,obj):path.write_text(json.dumps(obj,indent=2,allow_nan=False)+"\n",encoding="utf-8")


def rows_from_model(model):
    if model["as_of"]!="2026-09-15" or model["parameter_cutoff"]!="2026-09-13":raise ValueError("Unexpected vintage/cutoff")
    forecasts=model["forecast"]
    if [r["quarter"] for r in forecasts]!=["2026Q3","2026Q4","2027Q1","2027Q2"]:raise ValueError("Exactly four ordered quarters required")
    rows=[]
    for i,r in enumerate(forecasts):
        value=float(r["revenue_musd"]);guide=float(r["implied_guide_musd"])
        if not all(math.isfinite(x) and x>0 for x in (value,guide,r["lambda_decimal"],r["weighted_gbv_musd"])):raise ValueError("Invalid numerical forecast")
        if abs(r["weight"]-2/3)>1e-12:raise ValueError("Fixed lag policy changed")
        if abs(value-r["weighted_gbv_musd"]*r["lambda_decimal"])>1e-8 or abs(guide-value/(1+r["cushion_decimal"]))>1e-8:raise ValueError("Revenue/guide arithmetic mismatch")
        if r["lambda_n_train"]!=(5 if i<2 else 6) or r["cushion_n"]!=8:raise ValueError("Unexpected estimator sample sizes")
        if r["parameter_cutoff"]!="2026-09-13" or r["prepared_at"]!="2026-09-15":raise ValueError("Row vintage changed")
        if r["guide_kind"]!=("already_issued_diagnostic" if i==0 else "conditional_future_guide"):raise ValueError("Guide availability mismatch")
        common=dict(method=METHOD,quarter=r["quarter"],vintage_date="2026-09-15",horizon_q=i,window="LIVE",prior_basis="PIT",
            n_params=5,n_train=int(r["lambda_n_train"]),knowable_from="2026-09-13",spec_id="conditional_fixed_kernel_four_quarters_v1")
        note=(f"Conditional scenario not promoted; point-only q50 format field is not calibrated probability; "
              f"path has four seasonal lambdas plus shared cushion=5; n_train is lambda observations {r['lambda_n_train']}; "
              f"cushion observations 8; unprinted GBV assumptions explicit; no Street consumed; integration_v2")
        rows.append(dict(**common,object="four-quarter-revenue",target="revenue_musd",point=value,q50=value,notes=note))
        if i:rows.append(dict(**common,object="forward-guide",target="guide_mid",point=guide,q50=guide,notes=note+"; first-issued future guide only"))
    return pd.DataFrame(rows)


def protected_paths():
    paths=[]
    for rel in ["analysis/src/forecast_methods/harness","analysis/src/forecast_methods/harness_v1_1",
                "data/processed/forecast_methods/harness","data/processed/forecast_methods/harness_v1_1",
                "data/processed/forecast_methods/registry"]:
        paths.extend(p for p in (ROOT/rel).rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    return sorted(set(paths))


def score_to(module,out):
    out.mkdir(parents=True,exist_ok=False)
    paths=module.P
    mapping={"OUT_CONFORMAL_GRID":out/"conformal_attainable_grid.csv","OUT_SCOREBOARD":out/"scoreboard.csv","OUT_SCOREBOARD_MD":out/"scoreboard.md"}
    old={k:getattr(paths,k) for k in mapping}
    log=io.StringIO()
    try:
        for k,v in mapping.items():setattr(paths,k,v)
        with contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):exit_code=module.main()
    finally:
        for k,v in old.items():setattr(paths,k,v)
        (out/"scorer.log").write_text(log.getvalue(),encoding="utf-8")
    if exit_code!=0:raise RuntimeError("Unchanged scorer failed")
    return pd.read_csv(out/"scoreboard.csv")


def comparison(a,b,label):
    aa=a.set_index(KEYS).sort_index();bb=b.set_index(KEYS).sort_index()
    changes=[]
    for key in aa.index.union(bb.index):
        if key not in aa.index or key not in bb.index:
            changes.append(dict(comparison=label,**dict(zip(KEYS,key)),column="ROW",before="present" if key in aa.index else "absent",after="present" if key in bb.index else "absent"));continue
        for c in aa.columns.union(bb.columns):
            x=aa.loc[key,c] if c in aa else np.nan;y=bb.loc[key,c] if c in bb else np.nan
            if pd.isna(x) and pd.isna(y):continue
            if pd.isna(x) or pd.isna(y):same=False
            elif isinstance(x,(int,float,np.number)) and isinstance(y,(int,float,np.number)):same=bool(np.isclose(x,y,rtol=0,atol=1e-9))
            else:same=str(x)==str(y)
            if not same:changes.append(dict(comparison=label,**dict(zip(KEYS,key)),column=c,before=str(x),after=str(y)))
    return changes


def run(model_path,out,mode):
    if out.exists():raise FileExistsError("New scoring output directory required")
    model=json.loads(model_path.read_text());frame=rows_from_model(model)
    os.environ["CITADEL_ABNB_RUN_DATE"]="2026-09-15"
    sys.path.insert(0,str(ROOT/"analysis/src/forecast_methods"))
    registry=importlib.import_module("harness_v1_1.registry")
    scorers={"format_1_0":importlib.import_module("harness.score"),"format_1_1":importlib.import_module("harness_v1_1.score")}
    known_targets=pd.read_csv(scorers["format_1_0"].P.OUT_TARGETS,nrows=0).columns
    if not set(frame.target).issubset(known_targets):raise ValueError("Unknown harness target")
    original_registry=registry.P.REGISTRY_DIR
    planned=[original_registry/f"{METHOD}__{obj}.csv" for obj in frame.object.unique()]
    if mode=="register" and any(p.exists() for p in planned):raise FileExistsError("Registry object already exists; never overwrite")
    if mode=="audit-existing" and not all(p.exists() for p in planned):raise FileNotFoundError("Existing registration required")
    protected={str(p.relative_to(ROOT)).replace("\\","/"):sha(p) for p in protected_paths()}
    out.mkdir(parents=True)
    dump(out/"protection_before.json",protected)
    dump(out/"model_source.json",dict(path=str(model_path.relative_to(ROOT)).replace("\\","/"),sha256=sha(model_path),as_of=model["as_of"],parameter_cutoff=model["parameter_cutoff"]))
    # Authoritative FORMAT1.1 validator/writer produces staged bytes. Exclusive copy then adds new registry files.
    prepared=out/"prepared_registry";prepared.mkdir()
    try:
        registry.P.REGISTRY_DIR=prepared
        for obj,g in frame.groupby("object",sort=False):registry.register(g,quiet=True)
    finally:registry.P.REGISTRY_DIR=original_registry
    for p in planned:
        expected=(prepared/p.name).read_bytes()
        if mode=="audit-existing" and p.read_bytes()!=expected:raise ValueError("Existing registry object differs from exact model output")
    before={name:score_to(module,out/("before_"+name)) for name,module in scorers.items()}
    if mode=="register":
        for p in planned:
            with p.open("xb") as f:f.write((prepared/p.name).read_bytes())
    after={name:score_to(module,out/("after_"+name)) for name,module in scorers.items()}
    diffs=[]
    for name in scorers:
        delta=comparison(before[name],after[name],name+"_before_after")
        diffs.extend(delta)
        if delta:raise ValueError("LIVE registration changed historical scores")
        if (after[name].method==METHOD).any():raise ValueError("LIVE object entered historical scoreboard")
    cross=comparison(after["format_1_0"],after["format_1_1"],"formats_after");diffs.extend(cross)
    if cross:raise ValueError("Both formats disagree on historical scoring")
    drift=[]
    for name,module in scorers.items():
        checked=pd.read_csv(module.P.OUT_SCOREBOARD)
        drift.extend(comparison(checked,before[name],name+"_checked_in_vs_before"))
    pd.DataFrame(drift,columns=["comparison"]+KEYS+["column","before","after"]).to_csv(out/"preexisting_scoreboard_drift.csv",index=False)
    preservation=[dict(path=rel,before=h,after=sha(ROOT/rel),unchanged=sha(ROOT/rel)==h) for rel,h in protected.items()]
    if not all(x["unchanged"] for x in preservation):raise ValueError("A pre-existing protected file changed")
    pd.DataFrame(preservation).to_csv(out/"preservation.csv",index=False)
    actual=pd.concat([pd.read_csv(p) for p in planned],ignore_index=True)
    if len(actual)!=7 or not actual.window.eq("LIVE").all() or actual.target.eq("guide_mid").sum()!=3:raise ValueError("Unexpected final registration")
    receipt=dict(status="PASS",mode=mode,method=METHOD,registry_rows=7,revenue_rows=4,future_guide_rows=3,
        vintage="2026-09-15",parameter_cutoff="2026-09-13",format_version="1.1",parameter_count_path=5,
        n_train_definition="Seasonal lambda observations5/6; cushion uses8 separately; not independent total sample",
        point_only=True,calibrated_probability=False,forecast_promoted=False,historical_score_changes=0,
        scorer_exit_codes={name:{"before":0,"after":0} for name in scorers},
        historical_rows={name:len(after[name]) for name in scorers},preexisting_drift_cells=len(drift),
        protected_files_unchanged=len(preservation),registry_files={str(p.relative_to(ROOT)).replace("\\","/"):sha(p) for p in planned},
        model_sha256=sha(model_path),wrapper_sha256=sha(Path(__file__)),
        notes=["Unchanged main functions executed with only runtime output paths redirected",
            "Checked-in scoreboard drift is measured before adding LIVE rows and not repaired here",
            "No Q3 guide forecast is registered because guidance is already issued",
            "No historical forecast replay or empirical probabilities added"])
    dump(out/"receipt.json",receipt)
    dump(out/"manifest.json",{str(p.relative_to(out)).replace("\\","/"):sha(p) for p in sorted(out.rglob("*")) if p.is_file()})
    return receipt


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model",type=Path,default=ROOT/"data/processed/forecast_methods/gbv_event_v1/integration_v2/model.json")
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--mode",choices=["register","audit-existing"],required=True)
    a=ap.parse_args();print(json.dumps(run(a.model.resolve(),a.out.resolve(),a.mode),indent=2))
