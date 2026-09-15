"""PIT NCLH deposit-stock kernel. Offline, deterministic, immutable outputs."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "data/processed/forecast_methods/nclh_transfer_v1"
INPUT = BASE / "inputs_v3"
ATS = "advance_ticket_sales_current_usd_m"
TARGETS = ["passenger_ticket_revenue_usd_m", "total_revenue_usd_m"]
PREREG = ROOT / "docs/revenue-forecast-strategy/05_backtests/L3_NCLH_PREREG_v1.md"
ABNB = ROOT / "data/processed/forecast_methods/kernel_lambda/01_lambda_table.csv"
GRID = np.array([(i / 10, j / 10, (10-i-j) / 10) for i in range(11) for j in range(11-i)])


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_panel(input_dir=INPUT):
    obs = pd.read_csv(input_dir / "observations.csv")
    if obs.duplicated(["quarter", "metric"]).any():
        raise ValueError("Duplicate quarter/metric inputs")
    obs["published_at"] = pd.to_datetime(obs.published_at, utc=True, errors="coerce")
    if obs.published_at.isna().any():
        raise ValueError("Missing or invalid per-row publication timestamp")
    if (obs.source_reference.isna().any() or obs.source_reference.astype(str).str.strip().eq("").any()
            or not obs.source_sha256.astype(str).str.fullmatch(r"[0-9a-fA-F]{64}").all()):
        raise ValueError("Missing provenance")
    if (obs.published_at >= pd.Timestamp("2026-09-14", tz="UTC")).any():
        raise ValueError("Future source publication")
    if not pd.api.types.is_numeric_dtype(obs.value) or not np.isfinite(obs.value).all():
        raise ValueError("Nonfinite or nonnumeric observation value")
    expected_units={ATS:"USD million",**{m:"USD million" for m in TARGETS},
                    "onboard_other_revenue_usd_m":"USD million","capacity_days":"days", "occupancy_pct":"percent",
                    "net_yield_usd_per_capacity_day":"USD per capacity day"}
    if not obs.metric.isin(expected_units).all() or not obs.units.eq(obs.metric.map(expected_units)).all():
        raise ValueError("Metric unit mismatch")
    values = obs.pivot(index="quarter", columns="metric", values="value")
    metadata = obs.groupby("quarter").agg(published_at=("published_at", "max"), source_reference=("source_reference", "first"),
                                          publication_dates=("published_at", "nunique"))
    if metadata.publication_dates.ne(1).any():
        raise ValueError("Quarter contains inconsistent source publications")
    panel = values.join(metadata).sort_index()
    panel.index = pd.PeriodIndex(panel.index, freq="Q")
    required = [ATS, *TARGETS, "onboard_other_revenue_usd_m"]
    if panel[required].isna().any().any() or (panel[required] < 0).any().any():
        raise ValueError("Missing or negative core financial observations")
    if not np.allclose(panel.total_revenue_usd_m, panel.passenger_ticket_revenue_usd_m + panel.onboard_other_revenue_usd_m, atol=.002, rtol=0):
        raise ValueError("Passenger + onboard does not reconcile to total revenue")
    if np.any(np.diff(panel.index.asi8) != 1):
        raise ValueError("Noncontiguous input panel")
    return panel


def features(panel, target, asof):
    """Calendar lags 1–3; gate each individual source timestamp."""
    qs = [target-k for k in (1, 2, 3)]
    if any(q not in panel.index for q in qs):
        raise ValueError("Missing lagged ATS quarter")
    rows = panel.loc[qs]
    if (rows.published_at > asof).any():
        raise ValueError("Lagged ATS unavailable at vintage")
    x = rows[ATS].to_numpy(float)
    if not np.isfinite(x).all() or (x <= 0).any():
        raise ValueError("ATS denominator must be finite and positive")
    return x, rows.published_at.max(), ";".join(map(str, qs))


def eligible_quarter(q, exclude2022=False):
    excluded = {2020, 2021, *([2022] if exclude2022 else [])}
    return q.year not in excluded and all((q-k).year not in (2020, 2021) for k in (1,2,3))


def training(panel, metric, asof, exclude2022=False):
    rows = []
    for q, row in panel.iterrows():
        if row.published_at > asof or not eligible_quarter(q, exclude2022):
            continue
        try:
            x, latest, lags = features(panel, q, asof)
        except ValueError:
            continue
        rows.append({"quarter": str(q), "season": q.quarter, "actual": row[metric],
                     "x1": x[0], "x2": x[1], "x3": x[2], "known_at": max(row.published_at, latest)})
    return pd.DataFrame(rows)


def fit_kernel(train, fixed=None):
    counts = train.groupby("season").size() if not train.empty else pd.Series(dtype=int)
    if len(train) < 8 or len(counts) != 4 or counts.min() < 2:
        raise ValueError("Need eight eligible observations and two per season")
    x, y, season = train[["x1", "x2", "x3"]].to_numpy(), train.actual.to_numpy(), train.season.to_numpy()
    best = None
    for w in GRID if fixed is None else [np.asarray(fixed)]:
        if not np.isclose(w.sum(), 1) or (w < 0).any():
            raise ValueError("Weights must lie on simplex")
        den = x @ w
        lam = np.array([np.mean(y[season == s]/den[season == s]) for s in range(1,5)])
        pred = lam[season-1] * den
        loss = np.mean(((pred-y)/y)**2)
        if best is None or loss < best[0]:
            best = (float(loss), w.copy(), lam)
    return best


def baselines(panel, metric, q, asof, exclude2022=False):
    known = panel.loc[panel.published_at <= asof]
    def val(p):
        return float(known.loc[p, metric]) if p in known.index else np.nan
    naive = val(q-4)
    growth = val(q-1)/val(q-5) if val(q-5) > 0 else np.nan
    trailing = np.mean([val(q-k) for k in range(1,5)])
    pairs = [(val(p-1), val(p)) for p in known.index if p-1 in known.index
             and p.year not in (2020,2021) and (p-1).year not in (2020,2021)
             and (not exclude2022 or (p.year != 2022 and (p-1).year != 2022))]
    ar = np.nan
    if len(pairs) >= 8:
        z = np.array(pairs)
        beta = np.linalg.lstsq(np.c_[np.ones(len(z)),z[:,0]],z[:,1],rcond=None)[0]
        ar = beta[0] + beta[1]*val(q-1)
    return {"seasonal_naive": naive, "seasonal_naive_recent_growth": naive*growth,
            "trailing_four": trailing, "ar1": ar}


def evaluate(panel):
    predictions, coeffs, exclusions = [], [], []
    for metric in TARGETS:
        for exclude22 in (False, True):
            scenario = "primary_include_2022" if not exclude22 else "sensitivity_exclude_2022"
            for q in panel.index[(panel.index >= "2023Q1") & (panel.index <= "2026Q2")]:
                asof = panel.loc[q-1,"published_at"]
                try:
                    x, latest, lags = features(panel,q,asof)
                    train = training(panel,metric,asof,exclude22)
                    loss,w,lam = fit_kernel(train)
                    _,wf,lamf = fit_kernel(train,fixed=(2/3,1/3,0))
                    if train.known_at.max() > asof:
                        raise ValueError("Training information leakage")
                    models = {"kernel_simplex": lam[q.quarter-1]*(x@w),
                              "kernel_fixed_2_3_1_3": lamf[q.quarter-1]*(x@wf),
                              **baselines(panel,metric,q,asof,exclude22)}
                    for model,pred in models.items():
                        predictions.append({"metric":metric,"scenario":scenario,"quarter":str(q),
                            "vintage":asof.isoformat(),"model":model,"prediction":pred,"actual":panel.loc[q,metric],
                            "train_n":len(train),"latest_training_publication":train.known_at.max().isoformat(),
                            "latest_feature_publication":latest.isoformat(),"feature_quarters":lags,
                            "actual_published_at":panel.loc[q,"published_at"].isoformat(),
                            "source_reference":panel.loc[q,"source_reference"],"units":"USD million"})
                    coeffs.append({"metric":metric,"scenario":scenario,"quarter":str(q),"vintage":asof.isoformat(),
                        "phi1":w[0],"phi2":w[1],"phi3":w[2],"lambda1":lam[0],"lambda2":lam[1],"lambda3":lam[2],"lambda4":lam[3],
                        "training_loss":loss,"train_n":len(train),"train_quarters":";".join(train.quarter),
                        "free_parameters":6})
                except ValueError as e:
                    exclusions.append({"metric":metric,"scenario":scenario,"quarter":str(q),"reason":str(e)})
    return pd.DataFrame(predictions),pd.DataFrame(coeffs),pd.DataFrame(exclusions,columns=["metric","scenario","quarter","reason"])


def score(predictions):
    out=[]
    for (metric,scenario),group in predictions.groupby(["metric","scenario"]):
        for window,start in (("W1","2023Q1"),("W2","2024Q1")):
            g=group[group.quarter>=start]
            wide=g.pivot(index="quarter",columns="model",values="prediction")
            actual=g.groupby("quarter").actual.first()
            # Same complete available folds for every numerical baseline/model.
            complete=wide.dropna().index
            g=g[g.quarter.isin(complete)]
            naive=wide.loc[complete,"seasonal_naive"]-actual.loc[complete]
            naive_rmse=float(np.sqrt(np.mean(naive**2)))
            for model,rows in g.groupby("model"):
                err=rows.prediction-rows.actual
                rmse=float(np.sqrt(np.mean(err**2)))
                out.append({"metric":metric,"scenario":scenario,"window":window,"model":model,"n":len(rows),
                    "rmse_usd_m":rmse,"mae_usd_m":float(np.mean(abs(err))),"bias_usd_m":float(err.mean()),
                    "rmse_ratio_seasonal_naive":rmse/naive_rmse if naive_rmse>0 else np.nan,
                    "forecast_hurdle_pass":bool(rmse/naive_rmse<.6) if naive_rmse>0 else False})
            for model in ("guide_plus_trailing8_cushion","vintage_matched_street"):
                out.append({"metric":metric,"scenario":scenario,"window":window,"model":model,"n":0,
                            "status":"UNAVAILABLE: no metric-matched quarterly GAAP revenue guide/consensus"})
    return pd.DataFrame(out)


def stability(panel):
    values=[]
    cutoff=pd.Timestamp("2023-01-01",tz="UTC")
    for metric in TARGETS:
        train=training(panel,metric,cutoff)
        _,w,_=fit_kernel(train)
        for q in panel.index[(panel.index>="2023Q1") & (panel.index<="2025Q4")]:
            x,_,_=features(panel,q,panel.loc[q-1,"published_at"])
            values.append({"issuer":"NCLH","metric":metric,"quarter":str(q),"season":q.quarter,
                          "lambda_pct":100*panel.loc[q,metric]/(x@w),"phi1":w[0],"phi2":w[1],"phi3":w[2],
                          "weight_fit_cutoff":cutoff.isoformat(),"weight_train_n":len(train),
                          "evidence_status":"realized_full_sample_diagnostic_frozen_pre2023_weights"})
    vals=pd.DataFrame(values)
    stats=vals.groupby(["metric","season"]).agg(n=("lambda_pct","size"),lambda_min_pct=("lambda_pct","min"),
            lambda_max_pct=("lambda_pct","max"),lambda_mean_pct=("lambda_pct","mean")).reset_index()
    stats["lambda_range_pp"]=stats.lambda_max_pct-stats.lambda_min_pct
    stats["stability_hurdle_pass"]=(stats.n==3)&(stats.lambda_range_pp<.5)
    return vals,stats


def figure(vals,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ab=pd.read_csv(ABNB)
    qcol=next(x for x in ab if x.lower() in ("quarter","q","period"))
    lcol="lam_w23"
    ab=ab[(ab[qcol]>="2023Q1")&(ab[qcol]<="2025Q4")].copy()
    ab["season"]=pd.PeriodIndex(ab[qcol],freq="Q").quarter
    ab["year"]=pd.PeriodIndex(ab[qcol],freq="Q").year
    # Existing lambda table is in percent; detect its explicit column units below.
    if not np.allclose(ab[lcol],100*ab.revenue_musd/ab.base_w23):
        raise ValueError("ABNB lambda percent units do not reproduce")
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout="constrained")
    for year,color in zip((2023,2024,2025),("#345b8c","#ce7e20","#428566")):
        a=ab[ab.year==year].sort_values("season")
        axes[0].plot(a.season,a[lcol],marker="o",label=str(year),color=color)
        n=vals[(vals.metric==TARGETS[0])&vals.quarter.str.startswith(str(year))].sort_values("season")
        axes[1].plot(n.season,n.lambda_pct,marker="o",label=str(year),color=color)
    for ax,title in zip(axes,("ABNB: revenue / lagged GBV flow","NCLH: ticket revenue / lagged current ATS stock")):
        ax.set_title(title,fontsize=10); ax.set_xticks([1,2,3,4],["Q1","Q2","Q3","Q4"])
        ax.set_ylabel("Realized seasonal lambda (%)"); ax.grid(alpha=.2); ax.legend(frameon=False)
    fig.suptitle("Seasonal conversion diagnostic; different denominators and vertical scales",fontsize=11)
    fig.savefig(out/"lambda_comparison.png",dpi=170)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,default=INPUT)
    parser.add_argument("--out",type=Path,default=BASE/"results_v4")
    args=parser.parse_args()
    if args.out.exists() and any(args.out.iterdir()):
        raise FileExistsError("Immutable output: supply a NEW --out directory")
    panel=load_panel(args.input)
    predictions,coeffs,exclusions=evaluate(panel)
    scores=score(predictions)
    vals,stats=stability(panel)
    args.out.mkdir(parents=True,exist_ok=True)
    for name,frame in (("panel",panel.reset_index()),("predictions",predictions),("coefficients",coeffs),
            ("exclusions",exclusions),("scores",scores),("lambda_values",vals),("stability",stats)):
        frame.to_csv(args.out/f"{name}.csv",index=False,float_format="%.12g")
    verdict={}
    evidence=[]
    for metric in TARGETS:
        s=scores[(scores.metric==metric)&(scores.scenario=="primary_include_2022")&(scores.model=="kernel_simplex")]
        stable=bool(stats[stats.metric==metric].stability_hurdle_pass.all())
        forecast=bool(len(s)==2 and s.forecast_hurdle_pass.all())
        verdict[metric]={"stability":"PASS" if stable else "FAIL","forecast_both_windows":"PASS" if forecast else "FAIL",
            "guide_surprise":"UNAVAILABLE_metric_matched_guidance_and_consensus","kernel_transfer":"PASS" if stable and forecast else "FAIL"}
        for row in s.itertuples():
            evidence.append({"quarter":"2023Q1-2026Q2" if row.window=="W1" else "2024Q1-2026Q2",
                "metric":f"NCLH_{metric}_kernel_rmse_ratio","scenario":row.window,"value":row.rmse_ratio_seasonal_naive,
                "lower_bound":np.nan,"upper_bound":np.nan,"units":"ratio to seasonal naive; USD-level RMSE",
                "information_date":panel.published_at.max().isoformat(),"evidence_status":"research_fail_no_ABNB_adoption",
                "source_reference":"data/processed/forecast_methods/nclh_transfer_v1/results_v4/scores.csv",
                "replacement_vs_incremental":"neither; cross-issuer diagnostic only","treatment":"No ABNB forecast or valuation adjustment"})
        for row in stats[stats.metric==metric].itertuples():
            evidence.append({"quarter":f"2023Q{row.season}-2025Q{row.season}",
                "metric":f"NCLH_{metric}_lambda_range","scenario":f"season_Q{row.season}_frozen_pre2023_weights",
                "value":row.lambda_range_pp,"lower_bound":np.nan,"upper_bound":np.nan,
                "units":"percentage points; realized seasonal range; no uncertainty interval",
                "information_date":panel.loc[pd.Period("2025Q4",freq="Q"),"published_at"].isoformat(),
                "evidence_status":"research_fail_descriptive_n3_per_season",
                "source_reference":"data/processed/forecast_methods/nclh_transfer_v1/results_v4/stability.csv",
                "replacement_vs_incremental":"neither; cross-issuer diagnostic only","treatment":"No ABNB forecast or valuation adjustment"})
    pd.DataFrame(evidence).to_csv(args.out/"l4_evidence.csv",index=False,float_format="%.12g")
    (args.out/"verdict.json").write_text(json.dumps(verdict,indent=2)+"\n")
    figure(vals,args.out)
    dependencies=[*sorted(args.input.glob("*")),PREREG,ABNB,*sorted(Path(__file__).parent.glob("*.py"))]
    manifest={"inputs":[{"path":str(p.relative_to(ROOT)).replace("\\","/"),"sha256":digest(p)} for p in dependencies if p.is_file()],
              "outputs":[{"path":p.name,"sha256":digest(p)} for p in sorted(args.out.iterdir()) if p.is_file()],
              "as_of_date":"2026-09-13","research_verdict":verdict,"raw_source_storage":"temporary cache; manifests only in Git"}
    (args.out/"run_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(verdict,indent=2))


if __name__=="__main__":
    main()
