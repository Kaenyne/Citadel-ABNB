"""Preregistered year/quarter deletion and untuned zero-sign accounting."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[5]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--paired",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args();out=a.out.resolve()
    if out.exists():raise FileExistsError(out)
    data=pd.read_csv(a.paired)
    rows=[];signs=[];counts=[]
    for (arm,h,model),g in data.groupby(["arm","horizon_quarters","model"]):
        for window,start in [("W1","2023Q1"),("W2","2024Q1")]:
            for kind in ["guide_common_cushion_proxy","revenue_same_object","guide_vs_raw_revenue_different_objects"]:
                tc,mc,sc=("actual_revenue_musd","revenue_musd","street_revenue_musd") if kind=="revenue_same_object" else ("actual_guide_mid_musd","guide_mid_musd","street_implied_guide_musd" if kind=="guide_common_cushion_proxy" else "street_revenue_musd")
                z=g[g.target>=start].dropna(subset=[tc,mc,sc]).copy()
                base=dict(arm=arm,horizon_quarters=h,model=model,window=window,comparison=kind)
                counts.append(dict(**base,n_paired=len(z),n_row_specific_asof_proof=int(z.row_specific_asof_proof.sum()),strict_original_row_proof_status="UNAVAILABLE" if not z.row_specific_asof_proof.any() else "partial; see stored raw date timezone"))
                if not len(z):continue
                actual=np.sign(z[tc]-z[sc]);pred=np.sign(z[mc]-z[sc]);maj=actual.value_counts().max()/len(z)
                for ac in [-1,0,1]:
                    for pc in [-1,0,1]:
                        signs.append(dict(**base,n_total=len(z),actual_sign=ac,predicted_sign=pc,n_cell=int(((actual==ac)&(pred==pc)).sum()),always_majority_sign_accuracy=maj))
                for dimension in ["target_quarter","target_year"]:
                    vals=z.target if dimension=="target_quarter" else z.target.str[:4]
                    for value in vals.unique():
                        rem=z[vals!=value]
                        if not len(rem):continue
                        me=rem[mc]-rem[tc];se=rem[sc]-rem[tc]
                        mr=np.sqrt(np.mean(me**2));sr=np.sqrt(np.mean(se**2))
                        rows.append(dict(**base,dropped_dimension=dimension,dropped_value=value,n_retained=len(rem),model_rmse_musd=mr,street_rmse_musd=sr,rmse_ratio=mr/sr if sr else np.nan))
    out.mkdir(parents=True)
    pd.DataFrame(rows).to_csv(out/"deletions.csv",index=False)
    pd.DataFrame(signs).to_csv(out/"sign_confusion.csv",index=False)
    pd.DataFrame(counts).to_csv(out/"strict_proof_coverage.csv",index=False)
    d=pd.DataFrame(rows)
    summ=d.groupby(["arm","horizon_quarters","model","window","comparison","dropped_dimension"]).rmse_ratio.agg(["min","max","count"]).reset_index()
    summ.to_csv(out/"deletion_summary.csv",index=False)
    receipt=dict(input_path=str(a.paired.resolve()),input_sha256=hashlib.sha256(a.paired.read_bytes()).hexdigest(),deletion_rows=len(rows),sign_cells=len(signs),classification="zero is its own sign; no optimized thresholds; majority rate exposes class imbalance",new_parameters=0)
    (out/"manifest.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2))


if __name__=="__main__":main()
