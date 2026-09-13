"""Rebuild the R package from repo inputs and optional manifested public downloads."""
from pathlib import Path
import sys
import time
import json
import argparse
import hashlib
import numpy as np
import pandas as pd
from scipy.optimize._numdiff import approx_derivative
from threadpoolctl import threadpool_limits

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from l1_reconciliation_v3 import data as D
from l1_reconciliation_v3.refresh import AnchoredRecon, annual_decomposition, complete_quarter_arrivals, covariate_fit, strict_slice
from l1_reconciliation_v3.model import block_bootstrap, Recon
from kernel_engine_v2 import pit_lambda
from harness import load_calendar

OUT=D.OUT
ASOF="2026-09-12"
WEIGHTS=[0.33,0.5,2/3]
REGIONS=D.REGIONS


def inputs(as_of=ASOF):
    exact=strict_slice(D.load_exact_regional_revenue(),as_of)
    iv=strict_slice(D.load_intervals(),as_of)
    kpi=D.load_kpi()
    dates=load_calendar().set_index("print_quarter").print_date.to_dict()
    kpi["knowable_from"]=kpi.quarter.map(dates)
    kpi=strict_slice(kpi,as_of)
    qs=sorted(exact.groupby("quarter").filter(lambda x: set(x.region)==set(REGIONS)).quarter.unique())
    qs=[q for q in qs if q in set(kpi.quarter)]
    denom=D.denominator_identity(kpi,qs)
    fx=D.fx_pp_table(iv,pd.Timestamp(as_of).date())
    return qs,exact,iv,kpi,denom,fx


def forward_scenario(panel, scenario="base"):
    f=pd.read_csv(D.DATA/"overnight/10_regional_forecast.csv")
    f=f[f.scenario==scenario].set_index(["period","region"])
    d=panel.set_index(["quarter","region"])
    rows=panel[panel.quarter.isin(["2026Q1","2026Q2"])][["quarter","region","nights_m","adr_reported_usd","gbv_musd"]].to_dict("records")
    future=["2026Q3","2026Q4"]+[f"2027Q{i}" for i in range(1,5)]
    for q in future:
        period=D.to_short(q) if q.startswith("2026") else "FY27"
        price=float(f.loc[(period,"TOTAL"),"adr_exfx_yoy_pct"])
        for region in REGIONS:
            baseq=D.qadd(q,-4)
            if (baseq,region) in d.index:
                base=d.loc[(baseq,region)]
            else:
                base=next(x for x in rows if x["quarter"]==baseq and x["region"]==region)
            n=float(base["nights_m"])*(1+float(f.loc[(period,region),"nights_yoy_pct"])/100)
            a=float(base["adr_reported_usd"])*(1+price/100)
            rows.append(dict(quarter=q,region=region,nights_m=n,adr_reported_usd=a,gbv_musd=n*a))
    return pd.DataFrame(rows)


def factor(panel):
    p=panel.copy();p["year"]=p.quarter.str[:4].astype(int)
    a=p.groupby(["year","region"])[["nights_m","gbv_musd"]].sum()
    a["adr"]=a.gbv_musd/a.nights_m
    x,y=a.loc[2026],a.loc[2027]
    n0,n1=x.nights_m.sum(),y.nights_m.sum();g0,g1=x.gbv_musd.sum(),y.gbv_musd.sum()
    s0,s1=x.nights_m/n0,y.nights_m/n1;ad0,ad1=g0/n0,g1/n1
    mix=100*((s1-s0)*x.adr).sum()/ad0;within=100*(s0*(y.adr-x.adr)).sum()/ad0
    return dict(nights_growth_pp=100*(n1/n0-1),adr_growth_pp=100*(ad1/ad0-1),gbv_growth_pp=100*(g1/g0-1),geo_mix_pp=mix,within_pp=within,cross_mix_price_pp=100*(ad1/ad0-1)-mix-within)


def revenue_path(panel,kpi,lam,w):
    g=kpi.set_index("quarter").gbv_musd.to_dict();g.update(panel.groupby("quarter").gbv_musd.sum().to_dict())
    rev={q:float(kpi.set_index("quarter").loc[q,"revenue_musd"]) for q in ["2026Q1","2026Q2"]}
    for q in ["2026Q3","2026Q4"]+[f"2027Q{i}" for i in range(1,5)]:
        rev[q]=lam[int(q[-1])]/100*(w*g[D.qadd(q,-1)]+(1-w)*g[D.qadd(q,-2)])
    r0=sum(v for q,v in rev.items() if q.startswith("2026"));r1=sum(v for q,v in rev.items() if q.startswith("2027"))
    return rev,r0,r1,100*(r1/r0-1)


def local_candidate_rows(revenue, kpi, n_params, n_train):
    """Describe a reconstruction without inventing a historical issuance date.

    These are deliberately not harness rows: the analysis input cutoff and the
    actual creation timestamp are separate, and no ``vintage_date`` is asserted.
    """
    created = pd.Timestamp.now(tz="UTC").isoformat()
    historical = kpi.set_index("quarter").revenue_musd.to_dict()
    rows = []
    for q, value in revenue.items():
        if q in ["2026Q1", "2026Q2"]:
            continue
        prior = D.qadd(q, -4)
        prev = float(historical[prior] if prior in historical else revenue[prior])
        for obj, target, point in [("fy27_revenue", "revenue_musd", value),
                                   ("fy27_growth", "revenue_yoy", 100 * (value / prev - 1))]:
            rows.append(dict(method="l1-reconciliation-v3", object=obj, target=target,
                             quarter=q, point=point, n_params=n_params, n_train=n_train,
                             prior_basis="full_sample", analysis_input_cutoff=ASOF,
                             reconstruction_created_at_utc=created,
                             registration_status="UNREGISTERED_LOCAL_CANDIDATE",
                             notes="Conditional supplied-growth scenario, not a historical issuance. "
                                   "Only 2027 rows comprise FY27. Arrivals excluded; no predictive interval."))
    return pd.DataFrame(rows)


def write_local_candidates(rows, output):
    """Write only inside the caller's R output directory; no registry access."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    rows.to_csv(output / "UNREGISTERED_fy27_candidates.csv", index=False)
    status = dict(status="UNREGISTERED_LOCAL_CANDIDATE", rows=len(rows),
                  shared_registry_files_written=0,
                  analysis_input_cutoff=ASOF,
                  reconstruction_created_at_utc=rows.reconstruction_created_at_utc.iloc[0],
                  reason="Frozen harness does not admit this reconstruction's actual date. "
                         "An earlier date must not be used as a format slot. "
                         "Parent must obtain a suitable dated schema before registration.")
    (output / "registration_status.json").write_text(json.dumps(status, indent=2), encoding="utf8")
    return status


def main(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument("--bootstrap",type=int,default=40)
    ap.add_argument("--candidates-only", action="store_true",
                    help="Rebuild local unregistered candidates from existing fitted outputs; no model refits")
    args=ap.parse_args(argv)
    if args.candidates_only:
        forecast=pd.read_csv(OUT/"fy27_regional_scenario.csv")
        diag=json.loads((OUT/"diagnostics.json").read_text(encoding="utf8"))
        _,_,_,kpi,_,_=inputs()
        lam={s:pit_lambda(s,ASOF,variant="ewm")["lambda_pct"] for s in [1,2,3,4]}
        rp,_,_,_=revenue_path(forecast,kpi,lam,2/3)
        rows=local_candidate_rows(rp,kpi,diag["n_params"]+diag["kernel_coefficients"],diag["n_quarters"])
        print(json.dumps(write_local_candidates(rows,OUT),indent=2),flush=True)
        return 0
    if args.bootstrap<20: raise ValueError("At least 20 bootstrap refits required; still descriptive at this size")
    start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    qs,ex,iv,kpi,den,fx=inputs()
    rec=AnchoredRecon(qs,ex,den,iv,fx,as_of=ASOF)
    theta,opt=rec.fit(max_nfev=1200)
    if not opt.success: raise RuntimeError(f"Anchor fit failed: {opt.message}")
    panel=rec.panel(theta);panel["knowable_from"]=ex.groupby("quarter").knowable_from.max().reindex(panel.quarter).to_numpy()
    panel.to_csv(OUT/"regional_panel_v3.csv",index=False)
    residual=rec.residual_report(theta);residual.to_csv(OUT/"disclosure_residuals.csv",index=False)
    exact=residual[residual.cls=="exact_regional_revenue"]
    assert len(exact)==72 and exact.resid.abs().max()<1e-9,"G2 exact cells failed"
    assert np.allclose(panel.groupby("quarter").gbv_musd.sum(),kpi.set_index("quarter").loc[qs,"gbv_musd"],atol=1e-7)
    decomp=annual_decomposition(panel,fx);decomp.to_csv(OUT/"annual_adr_residuals.csv",index=False)
    print("G2: 72/72 exact cells; max error",exact.resid.abs().max(),flush=True)
    print(decomp[["year","within_exfx_pp","adr_note_exfx_pp","residual_pp"]].to_string(index=False),flush=True)
    # Draws reweight disclosure residuals in four-quarter blocks. Exact identity
    # residuals themselves are zero; resampling those cannot estimate uncertainty.
    boot=block_bootstrap(rec,theta,n_rep=args.bootstrap,block=4,seed=20260912,max_nfev=250)
    if len(boot)!=args.bootstrap: raise RuntimeError("Bootstrap refit failed; do not silently drop draws")
    samples=np.array([x[3] for x in boot])
    bounds=np.quantile(samples,[.1,.5,.9],axis=0)
    intervals=[]
    for i,q in enumerate(qs):
        for j,r in enumerate(REGIONS):
            lo,mid,hi=bounds[:,i,j]
            intervals.append(dict(quarter=q,region=r,q10=lo,q50=mid,q90=hi,relative_halfwidth_pct=100*(hi-lo)/(2*mid),n_draws=len(boot),basis="conditional_disclosure_block_bootstrap"))
    bi=pd.DataFrame(intervals);bi.to_csv(OUT/"regional_adr_intervals.csv",index=False)
    # Sensitivity includes removal of the new ADR anchor; not just small prior nudges.
    sensitivity=[]
    for sigma in [.025,.10,1e6]:
        alt=AnchoredRecon(qs,ex,den,iv,fx,anchor_sigma=sigma,as_of=ASOF)
        th,fit=alt.fit(theta0=theta,max_nfev=1000)
        if not fit.success: raise RuntimeError("Anchor sensitivity fit failed")
        pp=alt.panel(th)
        pp["anchor_sigma"]=sigma
        sensitivity.append(pp)
    sens=pd.concat(sensitivity,ignore_index=True);sens.to_csv(OUT/"anchor_sensitivity.csv",index=False)
    # Only observational interval residuals; smoothing and take-rate ridge omitted.
    nobs=rec.n_obs()
    jac=approx_derivative(lambda t: Recon.residuals(rec,t)[:nobs],theta)
    singular=np.linalg.svd(jac,compute_uv=False);rank=int((singular>max(singular)*1e-7).sum())
    np.savetxt(OUT/"observational_jacobian_singular_values.csv",singular,delimiter=",",header="singular_value",comments="")
    # The conditional fit is descriptive. All arrival candidates must independently
    # pass strict availability before a historical coefficient can exist.
    monthly_path=OUT/"arrivals_monthly_current.csv"
    monthly=pd.read_csv(monthly_path) if monthly_path.exists() else pd.DataFrame(columns=["series","region","month","value","knowable_from"])
    aq=complete_quarter_arrivals(monthly);aq.to_csv(OUT/"arrivals_quarterly_current.csv",index=False)
    dates=load_calendar().rename(columns={"print_quarter":"quarter"});dates=dates[dates.quarter.between("2023Q1","2026Q2")]
    # Guide origin for target q is the preceding quarter's print date.
    origin=load_calendar().set_index("print_quarter").print_date.to_dict()
    vintage_rows=[]
    for row in dates.itertuples():
        cut=str(origin[D.qadd(row.quarter,-1)])[:10]
        coeff=covariate_fit(panel,monthly,cut)
        vintage_rows.append(dict(quarter=row.quarter,as_of=cut,n_admissible_arrivals_quarters=len(complete_quarter_arrivals(monthly,cut)),n_coefficients=len(coeff),basis="strictly_before_origin"))
    vint=pd.DataFrame(vintage_rows);vint.to_csv(OUT/"arrivals_vintage_audit.csv",index=False)
    assert vint.n_coefficients.sum()==0,"Unexpected historical availability in current-only download"
    current_coeff=covariate_fit(panel,monthly,"2026-09-14")
    current_coeff["basis"]="retrospective_current_revision_descriptive_only"
    current_coeff.to_csv(OUT/"arrivals_descriptive_coefficients.csv",index=False)
    forecast=forward_scenario(panel);forecast.to_csv(OUT/"fy27_regional_scenario.csv",index=False)
    fac=factor(forecast)
    boot_factors=[];boot_paths=[]
    lam={s:pit_lambda(s,ASOF,variant="ewm")["lambda_pct"] for s in [1,2,3,4]}
    for _,nn,gg,aa in boot:
        pp=panel.copy();pp["nights_m"]=nn.ravel();pp["gbv_musd"]=gg.ravel();pp["adr_reported_usd"]=aa.ravel()
        fp=forward_scenario(pp);boot_factors.append(factor(fp));boot_paths.append(fp)
    bf=pd.DataFrame(boot_factors);bf.to_csv(OUT/"fy27_bootstrap_factors.csv",index=False)
    attribution=[]
    for line,key in [("geographic mix","geo_mix_pp"),("within-region reported ADR","within_pp"),("mix x price cross","cross_mix_price_pp"),("blended ADR subtotal","adr_growth_pp")]:
        lo,hi=bf[key].quantile([.1,.9]);attribution.append(dict(level="L1",line=line,pp=fac[key],q10=lo,q90=hi,basis="computed_conditional_composition",weight_in_revenue_total=0,n_draws=len(boot)))
    # These are fixed source-note assumptions and therefore have scenario bounds,
    # not sampling intervals. Seats are held flat in the actual projection.
    for line,value in [("unit-size mix carried",.63),("LOS carried",.04),("seats/hotel composition held flat",0.),("FX flat-yoy carry",0.)]:
        attribution.append(dict(level="L2",line=line,pp=value,q10=value,q90=value,basis="fixed_assumption_not_confidence_interval",weight_in_revenue_total=0,n_draws=0))
    rem=fac["within_pp"]-.63-.04
    attribution.append(dict(level="L2",line="price plus subregional mix remainder",pp=rem,q10=rem,q90=rem,basis="unidentified_joint_remainder_conditional_on_assumptions",weight_in_revenue_total=0,n_draws=0))
    pd.DataFrame(attribution).to_csv(OUT/"fy27_attribution.csv",index=False)
    bands=[];candidates=None
    for w in WEIGHTS:
        rp,r0,r1,growth=revenue_path(forecast,kpi,lam,w)
        vals=np.array([[revenue_path(fp,kpi,lam,w)[2],revenue_path(fp,kpi,lam,w)[3]] for fp in boot_paths])
        q10,q90=np.quantile(vals,[.1,.9],axis=0)
        bands.append(dict(kernel_w=w,fy26_revenue_musd=r0,fy27_revenue_musd=r1,fy27_growth_pct=growth,revenue_q10=q10[0],revenue_q90=q90[0],growth_q10=q10[1],growth_q90=q90[1],n_draws=len(boot),basis="conditional_composition_only_not_predictive",lambda_variant="K0_v2_ewm_fixed_across_weight_sensitivity"))
        if w==2/3:
            candidates=local_candidate_rows(rp,kpi,rec.n_params+4,len(qs))
    band=pd.DataFrame(bands);band.to_csv(OUT/"fy27_kernel_band.csv",index=False)
    registration_status=write_local_candidates(candidates,OUT)
    ids=rec.residual_report(theta)
    window=[]
    for name,first in [("W1","2023Q1"),("W2","2024Q1")]:
        d=ids[ids.quarter.between(first,"2026Q2")];v=vint[vint.quarter>=first]
        window.append(dict(window=name,guide_origins=len(v),arrivals_admissible_origins=int((v.n_coefficients>0).sum()),exact_cells=len(d[d.cls=="exact_regional_revenue"]),max_exact_error_musd=d[d.cls=="exact_regional_revenue"].resid.abs().max(),basis="full_sample_identity_reproduction; no PIT forecast test",forecast_result="underpowered",reason="Current arrivals revisions and annual live scenario do not provide a historical forecast replay"))
    pd.DataFrame(window).to_csv(OUT/"window_summary.csv",index=False)
    joined=sens.merge(panel[["quarter","region","adr_reported_usd"]],on=["quarter","region"],suffixes=("","_base"))
    diag=dict(verdict="partial",exact_cells=len(exact),g2_max_error_musd=float(exact.resid.abs().max()),n_quarters=len(qs),n_params=rec.n_params,kernel_coefficients=4,n_disclosure_constraints=nobs,n_annual_adr_anchors=len(rec.anchors),observational_interval_jacobian_rank=rank,observational_local_null_dimensions=rec.n_params-rank,exfx_max_abs_residual_pp=float(decomp.residual_pp.abs().max()),exfx_under_08_every_year=bool((decomp.residual_pp.abs()<.8).all()),max_conditional_adr_halfwidth_pct=float(bi.relative_halfwidth_pct.max()),max_anchor_sensitivity_pct=float((100*(joined.adr_reported_usd/joined.adr_reported_usd_base-1)).abs().max()),adr_identification_pass=False,adr_identification_reason="Conditional ADR halfwidth exceeds 10 percent and anchor sensitivity exceeds 10 percent; full local Jacobian rank does not imply a narrow identified set",bootstrap_requested=args.bootstrap,bootstrap_retained=len(boot),identity_residual_bootstrap_width=0,arrivals_earned=[],monthly_public_rows=len(monthly),runtime_seconds=time.perf_counter()-start,as_of=ASOF,registration_status=registration_status)
    (OUT/"diagnostics.json").write_text(json.dumps(diag,indent=2),encoding="utf8")
    source_files=[D.L0/"L0_exact_regional_revenue.csv",D.L0/"L0_interval_observations.csv",D.DATA/"adr/01_regional_annual.csv",D.DATA/"overnight/10_regional_forecast.csv",D.DATA/"overnight/02_kpi_panel_quarterly.csv",D.DATA/"overnight/10_fx_quarterly.csv",D.DATA/"overnight/10_regional_fx_passthrough.csv",D.DATA/"forecast_methods/harness/calendar.csv"]
    if monthly_path.exists():source_files.append(monthly_path)
    hashes={str(p.relative_to(D.REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
    (OUT/"input_manifest.json").write_text(json.dumps(hashes,indent=2),encoding="utf8")
    print(band.to_string(index=False),flush=True);print(json.dumps(diag,indent=2),flush=True)
    return 0


if __name__=="__main__":
    # Tiny dense fits are much slower with a large BLAS thread pool.
    with threadpool_limits(limits=1):
        raise SystemExit(main())
