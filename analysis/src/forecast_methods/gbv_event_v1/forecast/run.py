"""Reproduce the frozen preannouncement candidate; audit error without refitting."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
SOURCE_HEAD = "4533811d8405403b7f465bda3b69790e4367b2d6"
PACKAGE = "data/processed/forecast_methods/quant_thesis_validation_v1/prospective_v1/results_v1"
SCRIPT = "analysis/src/forecast_methods/quant_thesis_validation_v1/prospective_v1/run.py"
METHODS = ["candidate_k0_gbv", "B1_guide_growth", "B2_revenue_naive_cushion"]
FACTORS = ["gbv_shapley_musd", "conversion_shapley_musd", "cushion_shapley_musd"]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def clean(x):
    if isinstance(x, dict):
        return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.bool_,)):
        return bool(x)
    if isinstance(x, (np.floating, float)):
        return float(x) if math.isfinite(x) else None
    return x


def write_json(path, data):
    path.write_text(json.dumps(clean(data), indent=2, allow_nan=False) + "\n", encoding="utf-8")


def csv(path, data):
    (data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)).to_csv(path, index=False, float_format="%.15g", lineterminator="\n")


def metrics(values):
    x = np.asarray(values, dtype=float)
    if not len(x) or not np.isfinite(x).all():
        raise ValueError("Empty or nonfinite scored errors")
    return dict(n=len(x), bias_musd=float(x.mean()), mae_musd=float(np.abs(x).mean()),
                rmse_musd=float(np.sqrt(np.mean(x*x))), mse_musd2=float(np.mean(x*x)),
                population_variance_musd2=float(np.var(x)), sample_sd_musd=float(np.std(x, ddof=1)) if len(x)>1 else None)


def shapley(observed, predicted):
    """Exact symmetric attribution for product(X, lambda, policy), in USDm."""
    observed = np.asarray(observed, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    if len(observed)!=3 or len(predicted)!=3 or not np.isfinite(np.r_[observed,predicted]).all():
        raise ValueError("Three finite factors required")
    result = np.zeros(3)
    for ordering in itertools.permutations(range(3)):
        state = observed.copy()
        previous = float(np.prod(state))
        for j in ordering:
            state[j] = predicted[j]
            following = float(np.prod(state))
            result[j] += (following-previous)/6
            previous = following
    if abs(result.sum()-(np.prod(predicted)-np.prod(observed)))>1e-8:
        raise ValueError("Shapley identity failed")
    return result


def interval_error(prediction, midpoint):
    return prediction-np.clip(prediction,midpoint-.5,midpoint+.5)


def run(source, out, python):
    if out.exists():
        raise FileExistsError("Use a NEW immutable output directory")
    if not (source/SCRIPT).is_file():
        raise FileNotFoundError("Preserved quant source worktree required")
    out.mkdir(parents=True)
    git_env=os.environ.copy()
    config_index=int(git_env.get("GIT_CONFIG_COUNT","0"))
    git_env["GIT_CONFIG_COUNT"]=str(config_index+1)
    git_env[f"GIT_CONFIG_KEY_{config_index}"]="safe.directory"
    git_env[f"GIT_CONFIG_VALUE_{config_index}"]=str(source).replace("\\","/")
    source_manifest=[]
    needed=[SCRIPT, "analysis/src/forecast_methods/quant_thesis_validation_v1/prospective_v1/test_prospective.py"]
    needed += [str(p.relative_to(source)).replace("\\","/") for p in (source/PACKAGE).rglob("*") if p.is_file()]
    for rel in sorted(needed):
        committed=subprocess.check_output(["git","show",f"{SOURCE_HEAD}:{rel}"],cwd=source,env=git_env)
        disk=(source/rel).read_bytes()
        if committed!=disk and committed.replace(b"\r\n",b"\n")!=disk.replace(b"\r\n",b"\n"):
            raise ValueError("Source differs from pinned Git object: "+rel)
        source_manifest.append(dict(path=rel,commit=SOURCE_HEAD,git_sha256=digest(committed),disk_sha256=digest(disk),exact_bytes=committed==disk))
    csv(out/"source_manifest.csv", source_manifest)
    commands=[([python,"-B","-X","utf8",str(source/SCRIPT),"--out",str(out/"reproduction")],"frozen_reproduction"),
              ([python,"-B","-X","utf8",str(source/needed[1])],"frozen_adversarial_tests")]
    receipts=[]
    for argv,label in commands:
        p=subprocess.run(argv,cwd=source,capture_output=True,text=True,encoding="utf-8",errors="replace",env=git_env)
        (out/(label+".log")).write_text(p.stdout+p.stderr,encoding="utf-8")
        receipts.append(dict(command=argv,exit_code=p.returncode,log=label+".log"))
        if p.returncode:
            write_json(out/"execution_failure.json",receipts)
            raise RuntimeError(label+" failed; retained log")
    comparisons=[]
    for p in sorted((source/PACKAGE).rglob("*.csv")):
        rel=p.relative_to(source/PACKAGE)
        rebuilt=out/"reproduction"/rel
        exact=p.read_bytes()==rebuilt.read_bytes()
        comparisons.append(dict(file=str(rel).replace("\\","/"),exact_bytes=exact,original_sha256=digest(p.read_bytes()),rebuild_sha256=digest(rebuilt.read_bytes())))
        if not exact:
            raise ValueError("Frozen CSV did not reproduce exactly: "+str(rel))
    csv(out/"reproduction_comparison.csv",comparisons)
    fdir=out/"reproduction/forecast"; edir=out/"reproduction/evaluation"
    predictions=pd.read_csv(fdir/"predictions.csv")
    errors=pd.read_csv(edir/"errors.csv")
    contributions=pd.read_csv(edir/"contributions.csv")
    original_scores=pd.read_csv(edir/"scores.csv")
    predictions.to_csv(out/"pre_event_forecasts.csv",index=False,float_format="%.15g",lineterminator="\n")
    origin_map=predictions.drop_duplicates("quarter").set_index("quarter").origin_date
    timing=[]
    for filename,datecols in {
        "panel_inputs.csv":["available_date"],"guide_inputs.csv":["available_date"],
        "lambda_training.csv":["revenue_available_date","gbv1_available_date","gbv2_available_date"],
        "cushion_inputs.csv":["actual_available_date"],
        "gbv_inputs.csv":["source_anchor_available_date","latest_actual_available_date"],
    }.items():
        table=pd.read_csv(fdir/filename)
        for row in table.to_dict("records"):
            origin=pd.Timestamp(origin_map[row["quarter"]])
            for field in datecols:
                value=pd.to_datetime(row[field],errors="coerce")
                passed=bool(pd.notna(value) and value<origin)
                timing.append(dict(quarter=row["quarter"],ledger=filename,input_quarter=row.get("input_quarter",row.get("training_quarter")),field=field,available_date=row[field],origin_date=str(origin.date()),strictly_before=passed))
                if not passed:
                    raise ValueError("Input not strictly before origin")
    candidate=errors[(errors.method==METHODS[0]) & errors.quarter.between("2023Q1","2026Q2")].copy()
    for r in candidate.itertuples():
        if not pd.Timestamp(r.origin_date)<pd.Timestamp(r.guide_issuance_date):
            raise ValueError("Guide was already issued at forecast origin")
        if r.n_unprinted_gbv != 1:
            raise ValueError("Historical candidate missing-GBV count changed")
    csv(out/"timing_checks.csv",timing)
    event=candidate.merge(contributions,on="quarter",validate="one_to_one",suffixes=("","_decomp"))
    for idx,r in event.iterrows():
        observed=[r.actual_base_musd,r.lambda_star,r.value_mid/r.actual_revenue_musd]
        predicted=[r.base_hat_musd,r.lambda_pct/100,1/r.cushion_divisor]
        parts=shapley(observed,predicted)
        # Independently compare permutation definition with polynomial interactions.
        polynomial=[r.U+.5*r.UC+.5*r.UP+r.UCP/3,
                    r.C+.5*r.UC+.5*r.CP+r.UCP/3,
                    r.P+.5*r.UP+.5*r.CP+r.UCP/3]
        if not np.allclose(parts,polynomial,rtol=0,atol=1e-8):
            raise ValueError("Independent Shapley construction disagreement")
        for key,value in zip(FACTORS,parts):event.loc[idx,key]=value
        oracle_revenue=r.actual_base_musd*r.lambda_pct/100
        oracle_guide=oracle_revenue/r.cushion_divisor
        event.loc[idx,"oracle_gbv_revenue_musd"]=oracle_revenue
        event.loc[idx,"oracle_gbv_guide_musd"]=oracle_guide
        event.loc[idx,"oracle_guide_raw_error_musd"]=oracle_guide-r.value_mid
        event.loc[idx,"oracle_guide_interval_error_musd"]=interval_error(oracle_guide,r.value_mid)
        event.loc[idx,"candidate_revenue_raw_error_musd"]=r.revenue_point_musd-r.actual_revenue_musd
        event.loc[idx,"oracle_conversion_revenue_error_musd"]=oracle_revenue-r.actual_revenue_musd
        event.loc[idx,"gbv_unavailable_increment_musd"]=r.point_musd-oracle_guide
        event.loc[idx,"shapley_reconciliation_residual_musd"]=sum(parts)-r.error_raw_musd
        event.loc[idx,"oracle_status"]="ex_post_actual_GBV_substitution_holds_pre_event_lambda_and_cushion_not_executable"
    csv(out/"per_event_decomposition.csv",event)
    summary=[];moments=[];reconciliation=[];influence=[];paired=[];seasons=[]
    for win,start in [("W1","2023Q1"),("W2","2024Q1")]:
        z=event[event.quarter>=start];qs=set(z.quarter)
        for name,column,target,basis in [
            ("candidate_guide","error_raw_musd","first_issued_guide","raw"),
            ("candidate_guide","error_interval_musd","first_issued_guide","midpoint_plusminus_0_5"),
            ("oracle_GBV_guide","oracle_guide_raw_error_musd","first_issued_guide","raw"),
            ("oracle_GBV_guide","oracle_guide_interval_error_musd","first_issued_guide","midpoint_plusminus_0_5"),
            ("candidate_revenue","candidate_revenue_raw_error_musd","actual_revenue","raw"),
            ("oracle_GBV_conversion_revenue","oracle_conversion_revenue_error_musd","actual_revenue","raw"),
        ]:
            summary.append(dict(window=win,method=name,target=target,basis=basis,**metrics(z[column])))
        raw=z.error_raw_musd.to_numpy(); diagonal=0.;cross=0.;variance_diagonal=0.;variance_cross=0.
        for a,b in itertools.combinations_with_replacement(FACTORS,2):
            x=z[a].to_numpy();y=z[b].to_numpy();mult=1 if a==b else 2
            second=float(np.mean(x*y));cov=float(np.mean((x-x.mean())*(y-y.mean())))
            moments.append(dict(window=win,n=len(z),factor_a=a,factor_b=b,multiplier=mult,
                mean_a=float(x.mean()),mean_b=float(y.mean()),raw_second_moment=second,
                contribution_to_raw_mse=mult*second,population_covariance=cov,contribution_to_population_variance=mult*cov,
                correlation=float(np.corrcoef(x,y)[0,1])))
            if a==b:diagonal+=second;variance_diagonal+=cov
            else:cross+=2*second;variance_cross+=2*cov
        mse=float(np.mean(raw*raw));var=float(np.var(raw))
        if abs(diagonal+cross-mse)>1e-7 or abs(variance_diagonal+variance_cross-var)>1e-7:
            raise ValueError("Covariance-aware variance/MSE failed")
        reconciliation.append(dict(window=win,n=len(z),raw_mse=mse,diagonal_second_moments=diagonal,cross_moments=cross,
            raw_population_variance=var,diagonal_population_variance=variance_diagonal,covariance_contribution=variance_cross,
            naive_independent_sd_musd=math.sqrt(variance_diagonal),observed_population_sd_musd=math.sqrt(var),
            mse_residual=diagonal+cross-mse,variance_residual=variance_diagonal+variance_cross-var,independence_assumed=False))
        for term in FACTORS:
            summary.append(dict(window=win,method=term,target="raw_guide_error_attribution",basis="Shapley_diagnostic",**metrics(z[term])))
        for r in z.itertuples():
            left=z[z.quarter!=r.quarter]
            influence.append(dict(window=win,omitted_quarter=r.quarter,n=len(left),omitted_raw_error_musd=r.error_raw_musd,
                omitted_share_of_raw_squared_error=r.error_raw_musd**2/float(np.sum(raw*raw)),**{k:v for k,v in metrics(left.error_raw_musd).items() if k!="n"},refit=False))
            for baseline in METHODS[1:]:
                bl=errors[(errors.method==baseline)&errors.quarter.isin(set(left.quarter))]
                x=metrics(left.error_interval_musd);y=metrics(bl.error_interval_musd)
                paired.append(dict(window=win,baseline=baseline,omitted_quarter=r.quarter,n=len(left),
                    candidate_rmse=x["rmse_musd"],baseline_rmse=y["rmse_musd"],mse_delta=x["mse_musd2"]-y["mse_musd2"],
                    lower_mse=x["mse_musd2"]<y["mse_musd2"]-1e-9,refit=False))
        for season,s in z.groupby("season"):
            seasons.append(dict(window=win,season=int(season),quarters=";".join(s.quarter),**metrics(s.error_raw_musd)))
    csv(out/"score_summary.csv",summary);csv(out/"shapley_cross_moments.csv",moments)
    csv(out/"variance_reconciliation.csv",reconciliation);csv(out/"event_influence.csv",influence)
    csv(out/"paired_event_deletion.csv",paired);csv(out/"season_scores.csv",seasons)
    for filename in ["year_deletion.csv","hurdle_checks.csv","prediction_bands.csv","band_coverage.csv","coverage.csv","scores.csv"]:
        shutil.copyfile(edir/filename,out/("frozen_"+filename))
    verdict=json.loads((edir/"verdict.json").read_text())
    compact=dict(source_commit=SOURCE_HEAD,forecast_verdict=verdict["verdict"],new_fits=0,
        matched_scores=original_scores[(original_scores.scope=="all_three")].to_dict("records"),
        diagnostics=summary,variance=reconciliation,
        timing_checks=len(timing),timing_pass=all(x["strictly_before"] for x in timing),
        csv_files_exactly_reproduced=len(comparisons),execution=receipts,
        candidate_parameters=5,band_coverage=pd.read_csv(edir/"band_coverage.csv").query("method == 'candidate_k0_gbv'").to_dict("records"),
        caveats=["W2 nested in W1; matched n12/n10, two W1 candidate abstentions",
            "No four-quarter empirical forecast validation: these are fixed earlier origins for first-issued guide of each target",
            "Frozen-panel reconstruction, not original archived forecast or untouched holdout",
            "Shapley assigns interactions symmetrically; diagnostic accounting attribution, not causal mechanisms",
            "Oracle actual-GBV substitution retains early-origin lambda/cushion and is unavailable before release",
            "Six band outcomes do not establish calibrated 80 percent probabilities",
            "Year and event deletion hold predictions fixed, without refitting",
            "Guide midpoint +/-0.5 is an administrative scoring convention, not management full-range coverage"])
    write_json(out/"forecast_audit.json",compact)
    write_json(out/"output_manifest.json",{str(p.relative_to(out)).replace("\\","/"):digest(p.read_bytes()) for p in sorted(out.rglob("*")) if p.is_file()})
    return dict(verdict=verdict["verdict"],timing_checks=len(timing),csv_exact=len(comparisons),output=str(out))


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source",type=Path,default=ROOT.parent/"quant-thesis-validation-v1")
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--python",default=sys.executable)
    args=ap.parse_args()
    print(json.dumps(run(args.source.resolve(),args.out.resolve(),args.python),indent=2))
