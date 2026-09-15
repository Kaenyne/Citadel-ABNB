"""Frozen-point candidate-specific eligibility sensitivity; no fitting."""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd
import run as model


def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    args=p.parse_args();out=args.out.resolve()
    if out.exists():raise FileExistsError("New output directory required")
    frame=pd.read_csv(args.source/"predictions.csv");frame=frame[~frame.is_live]
    original=pd.read_csv(args.source/"coverage.csv")
    comparisons=[];deletions=[];coverage=[];gates=[]
    for h in [2,3,4]:
        for candidate in ["joint","fixed"]:
            for window,start in model.WINDOWS.items():
                relevant=[candidate,"guide_growth","revenue_growth"]
                d=frame[(frame.horizon_quarters==h)&(frame.target>=start)&frame.model.isin(relevant)]
                wide=d.pivot(index="target",columns="model",values="guide_mid_musd").dropna(subset=relevant).sort_index()
                actual=d.drop_duplicates("target").set_index("target").actual_guide_mid_musd.reindex(wide.index).to_numpy()
                years=np.array([int(t[:4]) for t in wide.index]);uy=np.unique(years)
                common=original[(original.horizon_quarters==h)&(original.window==window)&(original.model==candidate)].iloc[0]
                old_targets=set(str(common.common_targets).split("|"));added=sorted(set(wide.index)-old_targets)
                coverage.append(dict(horizon_quarters=h,window=window,candidate=candidate,n=len(wide),n_primary_common=int(common.n_common),
                                     added_targets="|".join(added),standalone_targets="|".join(wide.index),n_year_clusters=len(uy)))
                rng=np.random.default_rng(model.SEED+h)
                draw=rng.integers(0,len(uy),size=(2000,len(uy)))
                counts=np.stack([(draw==i).sum(axis=1) for i in range(len(uy))],axis=1)
                ec=wide[candidate].to_numpy()-actual
                sc=np.array([np.sum(ec[years==y]**2) for y in uy])
                for reference in ["guide_growth","revenue_growth"]:
                    eb=wide[reference].to_numpy()-actual;sb=np.array([np.sum(eb[years==y]**2) for y in uy])
                    ratios=np.sqrt((counts@sc)/(counts@sb))
                    comparisons.append(dict(horizon_quarters=h,window=window,candidate=candidate,reference=reference,n=len(wide),
                                            n_year_clusters=len(uy),candidate_rmse_musd=np.sqrt(np.mean(ec**2)),
                                            reference_rmse_musd=np.sqrt(np.mean(eb**2)),rmse_ratio=np.sqrt(sum(ec**2)/sum(eb**2)),
                                            ratio_p05=np.quantile(ratios,.05),ratio_p95=np.quantile(ratios,.95),n_bootstrap=2000))
                    for unit,values in [("year",years),("quarter",np.array(wide.index))]:
                        for value in np.unique(values):
                            keep=values!=value
                            if not keep.any():continue
                            deletions.append(dict(horizon_quarters=h,window=window,candidate=candidate,reference=reference,
                                                  deleted_unit=unit,deleted_value=str(value),n=int(keep.sum()),
                                                  guide_rmse_ratio=np.sqrt(sum(ec[keep]**2)/sum(eb[keep]**2))))
    cmp=pd.DataFrame(comparisons);delete=pd.DataFrame(deletions)
    for h in [2,3,4]:
        for candidate in ["joint","fixed"]:
            c=cmp[(cmp.horizon_quarters==h)&(cmp.candidate==candidate)];d=delete[(delete.horizon_quarters==h)&(delete.candidate==candidate)]
            coverage_ok=len(c)==4 and (c.n>=8).all();magnitude=coverage_ok and (c.rmse_ratio<=.9).all()
            stable=(d.guide_rmse_ratio<1).all();ci=(c.loc[c.reference=="guide_growth","ratio_p95"]<1).all()
            gates.append(dict(horizon_quarters=h,candidate=candidate,coverage_pass=bool(coverage_ok),magnitude_pass=bool(magnitude),
                              deletion_pass=bool(stable),paired_guidegrowth_interval_pass=bool(ci),
                              promotion_pass=bool(coverage_ok and magnitude and stable and ci)))
    out.mkdir(parents=True)
    for name,table in {"comparisons":cmp,"deletions":delete,"coverage_change":pd.DataFrame(coverage),"promotion_gates":pd.DataFrame(gates)}.items():table.to_csv(out/f"{name}.csv",index=False)
    source=model.ROOT/"docs/revenue-forecast-strategy/05_backtests/GD_HORIZON_ELIGIBILITY_ADDENDUM_v1.md"
    manifest={"code_sha256":model.sha(__file__),"source_predictions_sha256":model.sha(args.source/"predictions.csv"),
              "prereg_addendum_sha256":model.sha(source),"outputs":{p.name:model.sha(p) for p in sorted(out.iterdir())}}
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(pd.DataFrame(gates).to_string(index=False));print(cmp[(cmp.horizon_quarters==4)&(cmp.candidate=="fixed")].to_string(index=False))


if __name__=="__main__":main()
