"""Verify immutable results, dollar identities and exact deterministic rebuild."""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd
import run as core


def verify(first,repeat):
    m=json.loads((first/"manifest.json").read_text(encoding="utf-8"))
    mismatches=[]
    for name,expected in m["outputs"].items():
        if core.sha(first/name)!=expected:mismatches.append(f"original output hash: {name}")
        if not (repeat/name).is_file() or core.sha(repeat/name)!=expected:mismatches.append(f"rebuild output differs: {name}")
    for label,row in m["inputs"].items():
        if core.sha(core.ROOT/row["path"])!=row["sha256"]:mismatches.append(f"input hash: {label}")
    if core.sha(core.__file__)!=m["code_sha256"]:mismatches.append("core code hash")
    a=pd.read_csv(first/"model_matrix.csv")
    assert np.all(a.allocated_revenue_musd>=0)
    np.testing.assert_allclose(a.allocated_revenue_musd,a.effective_forward_fee_per_net_gbv*a.reported_booking_quarter_gbv_musd,rtol=1e-10,atol=1e-8)
    np.testing.assert_allclose(a.allocated_revenue_musd,a.backward_share*a.allocated_column_musd,rtol=1e-10,atol=1e-8)
    for _,g in a.groupby(["window","quarter"]):
        np.testing.assert_allclose(g.actual_revenue_attribution_share.sum()+g.unallocated_residual_share.iloc[0],1,atol=1e-10)
    p=pd.read_csv(first/"pit_predictions.csv")
    assert (pd.to_datetime(p.knowable_from)<=pd.to_datetime(p.origin)).all()
    assert (pd.to_datetime(p.origin)<pd.to_datetime(p.guide_event_date)).all()
    assert all(row.max_training_quarter<=core.qshift(row.quarter,-2) for row in p.itertuples())
    if mismatches:raise AssertionError("; ".join(mismatches))
    return {"status":"PASS","byte_identical_outputs":len(m["outputs"]),"input_hashes_unchanged":len(m["inputs"]),
            "matrix_rows_checked":len(a),"pit_rows_checked":len(p),
            "code_sha256":m["code_sha256"],"first_manifest_sha256":core.sha(first/"manifest.json"),
            "repeat_manifest_sha256":core.sha(repeat/"manifest.json"),
            "note":"no probabilistic inference implied by integrity PASS"}


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--first",type=Path,required=True);p.add_argument("--repeat",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True);args=p.parse_args()
    if args.out.exists():raise FileExistsError("New receipt path required")
    result=verify(args.first,args.repeat)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))
