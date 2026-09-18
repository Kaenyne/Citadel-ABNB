"""Independent eligibility-scope and calendar-flight source/formula verification."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[5];BASE=ROOT/'data/processed/forecast_methods/gbv_decision_0915_v1'
checks=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ck(label,a,b=True):
    ok=a==b if isinstance(b,(str,bool)) else np.allclose(a,b,rtol=1e-9,atol=1e-7,equal_nan=True)
    checks.append(dict(check=label,passed=bool(ok)))
    if not ok:raise AssertionError((label,a,b))
def rms(e):return np.sqrt(np.mean(np.asarray(e)**2))
def qs(q,k):return str(pd.Period(q,freq='Q')+k)
def audit_eligibility():
    folder=BASE/'horizon_v1/eligibility_audit_v1';m=json.loads((folder/'manifest.json').read_text())
    for name,digest in m['outputs'].items():ck('eligibility output hash '+name,sha(folder/name),digest)
    full=pd.read_csv(BASE/'horizon_v1/results_v2/predictions.csv');full=full[~full.is_live]
    cmp=pd.read_csv(folder/'comparisons.csv');delete=pd.read_csv(folder/'deletions.csv');gates=pd.read_csv(folder/'promotion_gates.csv')
    matrices={}
    for r in pd.read_csv(folder/'coverage_change.csv').itertuples():
        d=full[(full.horizon_quarters==r.horizon_quarters)&(full.target>=('2023Q1' if r.window=='W1' else '2024Q1'))&full.model.isin([r.candidate,'guide_growth','revenue_growth'])]
        w=d.pivot(index='target',columns='model',values='guide_mid_musd').dropna().sort_index();a=d.drop_duplicates('target').set_index('target').actual_guide_mid_musd.reindex(w.index)
        ck('standalone targetset '+str(r.Index),r.standalone_targets,'|'.join(w.index));ck('standalone n '+str(r.Index),r.n,len(w));matrices[(r.horizon_quarters,r.window,r.candidate)]=w.sub(a,axis=0)
    for r in cmp.itertuples():
        e=matrices[(r.horizon_quarters,r.window,r.candidate)];years=np.array([q[:4] for q in e.index]);uy=np.unique(years)
        rng=np.random.default_rng(20260915+r.horizon_quarters);draw=rng.choice(uy,size=(2000,len(uy)))
        counts=np.stack([(draw==y).sum(axis=1) for y in uy],axis=1);ec=e[r.candidate].values;eb=e[r.reference].values
        c=np.array([np.sum(ec[years==y]**2) for y in uy]);b=np.array([np.sum(eb[years==y]**2) for y in uy]);lo,hi=np.quantile(np.sqrt((counts@c)/(counts@b)),[.05,.95])
        for k,v in dict(rmse_ratio=rms(ec)/rms(eb),candidate_rmse_musd=rms(ec),reference_rmse_musd=rms(eb),ratio_p05=lo,ratio_p95=hi).items():ck('standalone statistic '+str(r.Index)+k,getattr(r,k),v)
    for r in delete.itertuples():
        e=matrices[(r.horizon_quarters,r.window,r.candidate)];keep=e.index.str[:4]!=str(r.deleted_value) if r.deleted_unit=='year' else e.index!=r.deleted_value;e=e[keep]
        ck('standalone deletion '+str(r.Index),r.guide_rmse_ratio,rms(e[r.candidate])/rms(e[r.reference]))
    for r in gates.itertuples():
        c=cmp[(cmp.horizon_quarters==r.horizon_quarters)&(cmp.candidate==r.candidate)];d=delete[(delete.horizon_quarters==r.horizon_quarters)&(delete.candidate==r.candidate)]
        values=dict(coverage_pass=len(c)==4 and (c.n>=8).all(),magnitude_pass=(c.rmse_ratio<=.9).all(),deletion_pass=(d.guide_rmse_ratio<1).all(),paired_guidegrowth_interval_pass=(c[c.reference=='guide_growth'].ratio_p95<1).all())
        values['promotion_pass']=all(values.values())
        for k,v in values.items():ck('standalone gate '+str(r.Index)+k,bool(getattr(r,k)),bool(v))
    return sha(folder/'manifest.json')
def audit_flights():
    folder=BASE/'calendar_flights_v1/results_v1';m=json.loads((folder/'manifest.json').read_text())
    for name,digest in m['outputs'].items():ck('flight output hash '+name,sha(folder/name),digest)
    for name,obj in m['inputs'].items():ck('flight input hash '+name,sha(ROOT/obj['path']),obj['sha256'])
    raw=pd.read_csv(ROOT/m['inputs']['panel']['path'])[['quarter','gbv_musd','revenue_musd']].copy();raw.quarter=raw.quarter.map(lambda q:f'20{q[2:]}Q{q[0]}')
    cal=pd.read_csv(ROOT/m['inputs']['company_calendar']['path']);raw['print_date']=pd.to_datetime(raw.quarter.map(cal.set_index('print_quarter').print_date));raw=raw.set_index('quarter').sort_index()
    flights=pd.read_csv(ROOT/m['inputs']['flights']['path']);line=pd.read_csv(ROOT/m['inputs']['flight_lineage']['path']);flights=flights.merge(line[['quarter','committed_utc','commit_full']],on='quarter',validate='one_to_one');flights.quarter=flights.quarter.map(lambda q:f'20{q[2:]}Q{q[0]}');flights['utc']=pd.to_datetime(flights.committed_utc,utc=True)
    def select(date,latest):
        z=flights[(flights.utc<=pd.Timestamp(date,tz='UTC'))&(flights.days_cur_present>=75)&np.isfinite(flights.eu40_flt_da_yoy)].sort_values(['quarter','commit_date'])
        if z.empty:return None
        row=z.iloc[-1]
        if pd.Period(latest,freq='Q').ordinal-pd.Period(row.quarter,freq='Q').ordinal>2:return None
        return row
    saved=pd.read_csv(folder/'training_pairs.csv');feat=pd.read_csv(folder/'features.csv');points=pd.read_csv(folder/'predictions.csv');fits=pd.read_csv(ROOT/m['inputs']['fits']['path']).set_index('origin_date');originpoints=pd.read_csv(ROOT/m['inputs']['calendar_points']['path'])
    for r in feat.itertuples():
        known=raw[raw.print_date<=pd.Timestamp(r.origin_date)];latest=known.index.max();row=select(r.origin_date,latest)
        ck('flight chosen '+str(r.Index),r.flight_commit_full,row.commit_full);ck('flight current quarter '+str(r.Index),bool(r.current_unprinted_quarter),row.quarter==qs(latest,1))
        expected=[]
        for q,outcome in raw[raw.print_date<pd.Timestamp(r.origin_date)].iterrows():
            date=(pd.Period(q,freq='Q')+1).start_time-pd.Timedelta(days=16);k=raw[raw.print_date<=date];p=k.index.max() if len(k) else None
            if p!=qs(q,-1) or any(v not in k.index for v in [qs(p,-4),qs(q,-4)]):continue
            f=select(str(date.date()),p)
            if f is None:continue
            g=k.loc[p,'gbv_musd']/k.loc[qs(p,-4),'gbv_musd']-1
            expected.append(dict(target=q,x=f.eu40_flt_da_yoy/100-g,y=outcome.gbv_musd/k.loc[qs(q,-4),'gbv_musd']-1,commit=f.commit_full,date=str(date.date())))
        z=saved[saved.evaluation_target==r.target].sort_values('target');ck('all eligible flight train '+str(r.Index),'|'.join(z.target),'|'.join(x['target'] for x in expected));ck('flight train n '+str(r.Index),r.n_training_pairs,len(expected))
        for a,b in zip(z.itertuples(),expected):
            ck('feature date '+str(r.Index)+a.target,a.feature_origin,b['date']);ck('feature commit '+str(r.Index)+a.target,a.flight_commit_full,b['commit']);ck('flight train x '+str(r.Index)+a.target,a.x,b['x']);ck('flight train y '+str(r.Index)+a.target,a.y,b['y'])
            ck('outcome strict before origin '+str(r.Index)+a.target,a.outcome_publication<r.origin_date)
        x=np.array([z['x'] for z in expected]);y=np.array([z['y'] for z in expected]);beta=np.clip((x@y)/(x@x),-2,2);ck('flight beta '+str(r.Index),r.beta,beta)
        growth=known.loc[latest,'gbv_musd']/known.loc[qs(latest,-4),'gbv_musd']-1;adjusted=growth+beta*(row.eu40_flt_da_yoy/100-growth);ck('adjusted growth '+str(r.Index),r.adjusted_growth_pct,100*adjusted)
        ps=points[points.target==r.target].set_index('model');ref=originpoints[(originpoints.target==r.target)&(originpoints.origin_date==r.origin_date)].set_index('model');fit=fits.loc[ref.loc['joint','source_origin_date']]
        values=known.gbv_musd.to_dict()
        for q in pd.period_range(pd.Period(latest,freq='Q')+1,r.target,freq='Q'):values[str(q)]=values[str(q-4)]*(1+adjusted)
        vec=np.array([values[r.target],values[qs(r.target,-1)],values[qs(r.target,-2)],np.mean([values[qs(r.target,-3)],values[qs(r.target,-4)]])]);phi=np.array([fit[f'weight_group_{k}'] for k in range(4)])
        jr=(vec@phi)*ref.loc['joint','seasonal_lambda_pct']/100;fr=(2/3*values[qs(r.target,-1)]+1/3*values[qs(r.target,-2)])*ref.loc['fixed','seasonal_lambda_pct']/100
        for model,value in [('joint_flight',jr),('fixed_flight',fr)]:ck('flight revenue '+r.target+model,ps.loc[model,'revenue_musd'],value);ck('flight guide '+r.target+model,ps.loc[model,'guide_mid_musd'],value/ref.loc['joint','cushion_divisor'])
        for model in ['joint','fixed']:ck('no flight binding '+r.target+model,ps.loc[model+'_noflight','guide_mid_musd'],ref.loc[model,'guide_mid_musd'])
    ck('two genuine current flight features',int(feat.current_unprinted_quarter.sum()),2)
    for r in pd.read_csv(folder/'scores.csv').itertuples():
        d=points[(points.target>=('2023Q1' if r.window=='W1' else '2024Q1'))&(points.model==r.model)];e=d.guide_mid_musd-d.actual_guide_mid_musd
        for k,v in dict(n=len(d),rmse_musd=rms(e),mae_musd=abs(e).mean(),bias_musd=e.mean(),error_sd_musd=e.std(ddof=1),worst_abs_miss_musd=abs(e).max()).items():ck('flight score '+str(r.Index)+k,getattr(r,k),v)
    matrices={ww:d.pivot(index='target',columns='model',values='guide_mid_musd').sub(d.drop_duplicates('target').set_index('target').actual_guide_mid_musd,axis=0).sort_index() for ww,d in [('W1',points[points.target>='2023Q1']),('W2',points[points.target>='2024Q1'])]}
    rng=np.random.default_rng(20260915);comparisons=pd.read_csv(folder/'paired_comparisons.csv');deletions=pd.read_csv(folder/'deletions.csv')
    for r in comparisons.itertuples():
        e=matrices[r.window];years=e.index.str[:4].values;uy=np.unique(years);draw=rng.choice(uy,size=(2000,len(uy)));counts=np.stack([(draw==y).sum(axis=1) for y in uy],axis=1);ec=e[r.candidate].values;eb=e[r.baseline].values
        c=np.array([np.sum(ec[years==y]**2) for y in uy]);b=np.array([np.sum(eb[years==y]**2) for y in uy]);lo,hi=np.quantile(np.sqrt((counts@c)/(counts@b)),[.05,.95])
        for k,v in dict(rmse_ratio=rms(ec)/rms(eb),ratio_p05=lo,ratio_p95=hi).items():ck('flight paired '+str(r.Index)+k,getattr(r,k),v)
    for r in deletions.itertuples():
        e=matrices[r.window];e=e[e.index.str[:4]!=str(r.excluded)] if r.deletion_kind=='year' else e[e.index!=r.excluded]
        ck('flight deletion '+str(r.Index),r.rmse_ratio,rms(e[r.candidate])/rms(e[r.baseline]))
    for r in pd.read_csv(folder/'remedy_gates.csv').itertuples():
        own=r.candidate.replace('flight','noflight');c=comparisons[(comparisons.window==r.window)&(comparisons.candidate==r.candidate)].set_index('baseline');d=deletions[(deletions.window==r.window)&(deletions.candidate==r.candidate)&(deletions.baseline==own)]
        expected=len(matrices[r.window])>=8 and c.loc[own,'rmse_ratio']<=.9 and (d.rmse_ratio<1).all() and c.loc['guide_growth','rmse_ratio']<1
        ck('flight gate '+str(r.Index),bool(r.pass_window),bool(expected))
    return sha(folder/'manifest.json')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve()
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);e=audit_eligibility();n=len(checks);f=audit_flights()
    pd.DataFrame(checks).to_csv(out/'checks.csv',index=False)
    receipt=dict(status='PASS',eligibility_checks=n,calendar_flight_checks=len(checks)-n,no_author_imports=True,eligibility_manifest_sha256=e,flight_manifest_sha256=f,review_code_sha256=sha(__file__),no_new_model_fit=True)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
