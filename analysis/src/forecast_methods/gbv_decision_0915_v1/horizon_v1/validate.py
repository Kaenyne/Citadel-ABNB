"""Independent arithmetic, origin safeguards and deterministic-output checks."""
from pathlib import Path
import argparse
import json
import numpy as np
import pandas as pd
import run as model


def validate(first,rebuild):
    manifest=json.loads((first/"manifest.json").read_text())
    for name,value in manifest["outputs"].items():
        assert model.sha(first/name)==value,name
        assert model.sha(rebuild/name)==value,name
    for name,value in manifest["source_hashes"].items():
        assert model.sha(model.ROOT/manifest["source_paths"][name])==value,name
    assert model.sha(model.__file__)==manifest["code_sha256"]
    core=model.accepted_core();panel,calendar=core.load_inputs()
    pred=pd.read_csv(first/"predictions.csv");inputs=pd.read_csv(first/"gbv_inputs.csv")
    parts=pd.read_csv(first/"gbv_contributions.csv");fits=pd.read_csv(first/"origin_fits.csv")
    anchors=pd.read_csv(first/"baseline_source_anchors.csv");variances=pd.read_csv(first/"error_variance_decomposition.csv")
    tol=1e-7;checks=0
    for row in inputs.itertuples():
        known=panel[panel.print_date<=pd.Timestamp(row.origin_date)].set_index("quarter")
        latest=known.index.max()
        if row.gbv_status=="reported":
            assert row.gbv_quarter in known.index
            expected=known.loc[row.gbv_quarter,"gbv_musd"]
        else:
            assert row.gbv_quarter not in known.index
            growth=known.loc[latest,"gbv_musd"]/known.loc[model.qshift(latest,-4),"gbv_musd"]
            expected=known.loc[model.qshift(row.gbv_quarter,-4),"gbv_musd"]*growth
        assert abs(expected-row.gbv_musd)<tol;checks+=1
    for fit in fits.itertuples():
        known=panel[panel.print_date<=pd.Timestamp(fit.origin_date)].set_index("quarter")
        train=fit.training_quarters.split("|")
        assert len(train)==fit.n_train
        assert max(train)<=fit.last_reported_quarter
        phi=np.array([getattr(fit,f"weight_group_{k}") for k in range(4)])
        assert np.isclose(phi.sum(),1,atol=tol) and (phi>=-tol).all()
        for s in range(1,5):
            ratios=[]
            for q in train:
                if int(q[-1])!=s:continue
                g=[known.loc[model.qshift(q,-k),"gbv_musd"] for k in range(5)]
                exposure=phi[0]*g[0]+phi[1]*g[1]+phi[2]*g[2]+phi[3]*(g[3]+g[4])/2
                ratios.append(known.loc[q,"revenue_musd"]/exposure)
            weights=np.power(2.,-np.arange(len(ratios)-1,-1,-1)/2)
            expected=100*np.sum(np.array(ratios)*weights)/sum(weights)
            assert abs(expected-getattr(fit,f"lambda_Q{s}_pct"))<tol;checks+=1
    for row in anchors.itertuples():
        assert pd.Timestamp(row.source_publication)<=pd.Timestamp(row.origin_date);checks+=1
    for row in pred.itertuples():
        origin=pd.Timestamp(row.origin_date)
        if row.point_in_time_eligible:
            assert not row.oracle_future_information_used
            assert pd.Timestamp(row.knowable_from)<=origin
        else:
            assert row.model.endswith("_oracle") and row.oracle_future_information_used
            assert pd.Timestamp(row.knowable_from)>origin
        if pd.notna(row.guide_event_date):assert pd.Timestamp(row.guide_event_date)>origin
        assert np.isclose(row.cushion_divisor,1+row.cushion_pct/100,atol=tol)
        assert abs(row.revenue_musd/row.cushion_divisor-row.guide_mid_musd)<tol
        if row.model in ["joint","fixed"]:
            a=parts[(parts.origin_date==row.origin_date)&(parts.target==row.target)&(parts.model==row.model)]
            assert len(a)==5
            values=a.gbv_musd*a.exposure_weight*a.seasonal_lambda_pct/100
            np.testing.assert_allclose(values,a.revenue_contribution_musd,atol=tol)
            assert abs(sum(values)-row.revenue_musd)<tol
            known=float(a.loc[a.gbv_status=="reported","revenue_contribution_musd"].sum())
            assert abs(known/row.revenue_musd-row.known_gbv_dollar_share)<tol
        if row.model in ["guide_growth","revenue_growth"]:
            a=anchors[(anchors.origin_date==row.origin_date)&(anchors.target==row.target)&(anchors.model==row.model)].set_index("anchor_quarter")
            expected=a.loc[row.target_year_ago_anchor,"value_musd"]*a.loc[row.latest_growth_target,"value_musd"]/a.loc[model.qshift(row.latest_growth_target,-4),"value_musd"]
            actual=row.guide_mid_musd if row.model=="guide_growth" else row.revenue_musd
            assert abs(expected-actual)<tol
        checks+=1
    assert variances.identity_error_musd2.abs().max()<1e-7
    # Prior unchanged primary output is a separate frozen regression check for h2.
    previous=pd.read_csv(model.ROOT/"data/processed/forecast_methods/gbv_joint_cohort_v1/quant_v1/results_v1/pit_predictions.csv")
    previous=previous[previous.spec=="tail34"]
    for row in previous.itertuples():
        for name,old in [("joint",row.candidate_guide_musd),("fixed",row.baseline_guide_musd)]:
            new=pred[(pred.origin_date==row.origin)&(pred.target==row.quarter)&(pred.model==name)].iloc[0].guide_mid_musd
            assert abs(old-new)<tol;checks+=1
    # All three advance horizons share this genuine prior release. Poison every future
    # actual and issued guide, keeping publication stamps: production points must not move.
    # Use authoritative Q2 release date rather than guessing the day.
    origin=str(calendar.set_index("print_quarter").loc["2024Q2","print_date"])
    poisoned=panel.copy();poisoned.loc[poisoned.print_date>pd.Timestamp(origin),["gbv_musd","revenue_musd"]]*=10000
    altered=calendar.copy();mask=pd.to_datetime(altered.print_date)>pd.Timestamp(origin)
    altered.loc[mask,"guide_mid"]=1e10
    original_engine=model.FrozenForecasts(panel,calendar);poisoned_engine=model.FrozenForecasts(poisoned,altered)
    for h in [2,3,4]:
        target=model.qshift("2024Q2",h)
        one=pd.DataFrame(original_engine.predict(target,origin)[0]);two=pd.DataFrame(poisoned_engine.predict(target,origin)[0])
        one=one[one.model.isin(model.MODELS)].sort_values("model");two=two[two.model.isin(model.MODELS)].sort_values("model")
        np.testing.assert_allclose(one[["revenue_musd","guide_mid_musd"]],two[["revenue_musd","guide_mid_musd"]],atol=tol)
        checks+=len(one)
    return {"status":"PASS","saved_arithmetic_origin_checks":checks,"byte_identical_outputs":len(manifest["outputs"]),
            "preserved_sources":len(manifest["source_hashes"]),"three_horizon_future_actual_and_guide_poison":"PASS",
            "accepted_prior_h2_regression":"PASS","covariance_identity":"PASS",
            "original_manifest_sha256":model.sha(first/"manifest.json"),"rebuild_manifest_sha256":model.sha(rebuild/"manifest.json")}


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--first",type=Path,required=True);p.add_argument("--rebuild",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True);args=p.parse_args()
    if args.out.exists():raise FileExistsError("New receipt path required")
    result=validate(args.first,args.rebuild);args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(result,indent=2))
