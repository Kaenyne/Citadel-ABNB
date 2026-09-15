"""Read-only independent source admission and same-object Street comparison audit."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[5]
BASE=ROOT/'data/processed/forecast_methods/gbv_decision_0915_v1'
checks=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ck(label,a,b=True):
    ok=(a==b) if isinstance(b,(str,bool)) else bool(np.allclose(a,b,atol=1e-7,rtol=1e-9,equal_nan=True))
    checks.append(dict(check=label,passed=bool(ok)))
    if not ok:raise AssertionError((label,a,b))
def rms(x):return np.sqrt(np.mean(np.asarray(x)**2))
def band(ec,eb,years):
    uy=np.unique(years);rng=np.random.default_rng(20260915);draws=rng.choice(uy,size=(2000,len(uy)))
    count=np.stack([(draws==y).sum(axis=1) for y in uy],axis=1)
    c=np.array([np.sum(ec[years==y]**2) for y in uy]);b=np.array([np.sum(eb[years==y]**2) for y in uy])
    return np.quantile(np.sqrt((count@c)/(count@b)),[.05,.95])
def cols(kind):return ('actual_revenue_musd','revenue_musd','street_revenue_musd') if kind=='revenue_same_object' else ('actual_guide_mid_musd','guide_mid_musd','street_implied_guide_musd' if kind=='guide_common_cushion_proxy' else 'street_revenue_musd')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve()
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True)
    p=BASE/'street_v1/results_v3';manifest=json.loads((p/'manifest.json').read_text())
    for path,digest in manifest['input_sha256'].items():ck('source hash '+path,sha(ROOT/Path(path)),digest)
    raw=pd.read_csv(ROOT/'data/processed/github_altdata/samples/dolthub-post-no-preference-earnings-consensus-vintages/sales_estimate_ABNB_BKNG_EXPE.csv')
    raw=raw[(raw.act_symbol=='ABNB')&raw.period.isin(['Current Quarter','Next Quarter'])&raw.consensus.gt(0)&raw['count'].gt(0)].copy()
    raw['target']=pd.to_datetime(raw.period_end_date).dt.to_period('Q').astype(str)
    cal=pd.read_csv(ROOT/'data/processed/forecast_methods/harness/calendar.csv');cal=cal[cal.is_forecast_row==False]
    origins=pd.read_csv(p/'origin_consensus.csv');pairs=pd.read_csv(p/'paired_rows.csv');metrics=pd.read_csv(p/'paired_metrics.csv')
    pred=pd.read_csv(BASE/'horizon_v1/results_v2/predictions.csv').set_index(['origin_date','target','model'])
    ck('84 preserved origin arms',len(origins),84)
    for r in origins.itertuples():
        z=raw[(raw.target==r.target)&(raw.date<r.origin_date)].sort_values('date')
        ck('availability '+str(r.Index),bool(r.street_available),len(z)>0)
        ck('last company print '+str(r.Index),r.last_reported_quarter,cal[cal.print_date<=r.origin_date].print_quarter.max())
        if r.arm=='calendar_minus16':
            date=(pd.Period(r.last_reported_quarter,freq='Q')+2).start_time-pd.Timedelta(days=16)
            ck('fixed calendar rule '+str(r.Index),r.origin_date,str(date.date()))
            ck('no intervening company print '+str(r.Index),len(cal[(cal.print_date>r.release_origin_date)&(cal.print_date<=r.origin_date)]),0)
            ck('no intervening initial guide '+str(r.Index),len(cal[(cal.guide_date>r.release_origin_date)&(cal.guide_date<=r.origin_date)]),0)
        if len(z):
            s=z.iloc[-1];ck('selected snapshot '+str(r.Index),r.street_snapshot_date,s.date);ck('selected revenue '+str(r.Index),r.street_revenue_musd,s.consensus/1e6)
            ck('snapshot age '+str(r.Index),r.snapshot_age_days,(pd.Timestamp(r.origin_date)-pd.Timestamp(s.date)).days)
            ck('explicit inherited vendor '+str(r.Index),r.vendor,'DoltHub post-no-preference/earnings')
        ck('row-specific proof remains unavailable '+str(r.Index),bool(r.row_specific_asof_proof),False)
    for r in pairs.itertuples():
        source=pred.loc[(r.release_origin_date,r.target,r.model)]
        for name in ['revenue_musd','guide_mid_musd','cushion_divisor','actual_revenue_musd','actual_guide_mid_musd']:ck('point binding '+str(r.Index)+name,getattr(r,name),source[name])
        if r.street_available:
            ck('implied guide '+str(r.Index),r.street_implied_guide_musd,r.street_revenue_musd/r.cushion_divisor)
            ck('shared cushion cancellation '+str(r.Index),r.common_cushion_predicted_gap_pct,100*(r.revenue_musd/r.street_revenue_musd-1))
            ck('raw signal '+str(r.Index),r.raw_predicted_guide_minus_street_revenue_pct,100*(r.guide_mid_musd/r.street_revenue_musd-1))
            ck('realized proxy surprise '+str(r.Index),r.common_cushion_actual_guide_gap_pct,100*(r.actual_guide_mid_musd/r.street_implied_guide_musd-1))
    for r in metrics.itertuples():
        lower='2023Q1' if r.window=='W1' else '2024Q1'
        z=pairs[(pairs.arm==r.arm)&(pairs.horizon_quarters==r.horizon_quarters)&(pairs.model==r.model)&(pairs.target>=lower)]
        ac,mc,sc=cols(r.comparison);z=z.dropna(subset=[ac,mc,sc]);ck('metric n '+str(r.Index),r.n_paired,len(z))
        if not len(z):ck('missing metric not zero '+str(r.Index),bool(pd.isna(r.rmse_ratio)));continue
        e=(z[mc]-z[ac]).values;b=(z[sc]-z[ac]).values;lo,hi=band(e,b,z.target.str[:4].values)
        actualgap=z[ac]-z[sc];predgap=z[mc]-z[sc]
        vals=dict(model_rmse_musd=rms(e),street_rmse_musd=rms(b),rmse_ratio=rms(e)/rms(b),model_mae_musd=np.mean(abs(e)),street_mae_musd=np.mean(abs(b)),model_bias_musd=e.mean(),street_bias_musd=b.mean(),gap_sign_accuracy=np.mean(np.sign(actualgap)==np.sign(predgap)),actual_gap_mean_musd=actualgap.mean(),predicted_gap_mean_musd=predgap.mean(),rmse_ratio_year_bootstrap90_lo=lo,rmse_ratio_year_bootstrap90_hi=hi)
        for k,v in vals.items():ck('metric '+str(r.Index)+k,getattr(r,k),v)
    cm=pd.read_csv(BASE/'street_v1/common_v1/common_model_metrics.csv');cr=pd.read_csv(BASE/'street_v1/common_v1/common_model_rows.csv')
    for r in cm.itertuples():
        z=cr[(cr.window==r.window)&(cr.comparison==r.comparison)]
        ac,mc,sc=cols(r.comparison)
        if r.model=='DoltHub':z=z.drop_duplicates(['origin_date','target']);e=(z[sc]-z[ac]).values
        else:z=z[z.model==r.model];e=(z[mc]-z[ac]).values
        ck('common metrics n '+str(r.Index),r.n,len(z));ck('common metrics rmse '+str(r.Index),r.rmse_musd,rms(e));ck('common metrics bias '+str(r.Index),r.bias_musd,e.mean())
    live=pd.read_csv(BASE/'street_v1/common_v1/live_comparison.csv')
    # Pin supplemental outputs exactly even where fields are presentation-only.
    pd.DataFrame(checks).to_csv(out/'checks.csv',index=False)
    receipt=dict(status='PASS',independent_source_arithmetic_checks=len(checks),no_author_import=True,canonical_street_manifest_sha256=sha(p/'manifest.json'),canonical_horizon_manifest_sha256=sha(BASE/'horizon_v1/results_v2/manifest.json'),bound_supplements={str(q.relative_to(BASE)):sha(q) for q in (BASE/'street_v1/common_v1').glob('*') if q.is_file()},review_code_sha256=sha(__file__),source_admission='inherited snapshots conditional; zero selected row-specific AS OF proof',not_measured_guide_expectations=True)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
