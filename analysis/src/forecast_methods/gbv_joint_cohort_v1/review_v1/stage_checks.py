"""Independent check of parent's prepared registry rows; never writes a registry."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[5]
BASE=ROOT/"data/processed/forecast_methods/gbv_joint_cohort_v1"


def main(stage,out):
    stage=Path(stage).resolve();out=Path(out).resolve()
    if not out.is_relative_to(BASE/"review_v1") or out.exists():raise ValueError("New review directory required")
    receipt=json.loads((stage/"receipt.json").read_text())
    source=Path(receipt["source"]);pred=pd.read_csv(source);pred=pred[pred.spec.eq("tail34")].set_index("quarter")
    check=[]
    def yes(name,condition):check.append({"check":name,"passed":bool(condition)})
    yes("prepared only",receipt["mode"]=="prepared_only")
    yes("source hash",hashlib.sha256(source.read_bytes()).hexdigest()==receipt["source_sha256"])
    frames=[]
    for name,expected in receipt["staged_sha256"].items():
        path=stage/"prepared_registry"/name
        yes("stage hash "+name,hashlib.sha256(path.read_bytes()).hexdigest()==expected)
        frames.append(pd.read_csv(path,comment="#"))
    table=pd.concat(frames,ignore_index=True)
    yes("42 rows",len(table)==42)
    yes("unique method/object/quarter/window",not table.duplicated(["method","object","quarter","window"]).any())
    for row in table.itertuples():
        r=pred.loc[row.quarter];guide=row.target=="guide_mid";expected=r.candidate_guide_musd if guide else r.candidate_revenue_musd
        key=f"{row.object}:{row.window}:{row.quarter}:"
        yes(key+"point",np.isclose(row.point,expected,atol=1e-8,rtol=1e-10) and row.q50==row.point)
        yes(key+"origin",pd.Timestamp(row.vintage_date)==pd.Timestamp(r.origin) and pd.Timestamp(row.knowable_from)<=pd.Timestamp(row.vintage_date)<pd.Timestamp(r.guide_event_date))
        horizon=pd.Period(row.quarter,freq="Q").ordinal-pd.Timestamp(row.vintage_date).to_period("Q").ordinal
        yes(key+"horizon",row.horizon_q==horizon)
        yes(key+"counts",row.n_params==(8 if guide else 7) and row.n_train==r.n_train)
        yes(key+"basis",row.prior_basis=="PIT" and "point-only" in row.notes and "same-origin" in row.notes)
        yes(key+"no bands",all(pd.isna(getattr(row,c)) for c in ["q05","q10","q25","q75","q90","q95"] if hasattr(row,c)))
    for obj,d in table.groupby("object"):
        yes(obj+"window counts",d.window.value_counts().to_dict()=={"W1":11,"W2":10})
    out.mkdir(parents=True)
    pd.DataFrame(check).to_csv(out/"checks.csv",index=False)
    result={"checks":len(check),"passed":sum(c["passed"] for c in check),"rows":len(table),
            "status":"prepared registry accepted for retention of research candidate, not forecast promotion",
            "scope":"points, source hashes, source counts, information dates, calendar horizon, PIT windows, guide8/revenue7 parameters, absent bands",
            "frozen_scorer_ratios_are_not_same_origin_validation":True,
            "sha256":{str((stage/"receipt.json").relative_to(ROOT)):hashlib.sha256((stage/"receipt.json").read_bytes()).hexdigest(),
                      str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}
    (out/"receipt.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result))
    if result["checks"]!=result["passed"]:raise AssertionError("Registry stage checks failed")


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--stage",required=True);p.add_argument("--out",required=True);a=p.parse_args();main(a.stage,a.out)
