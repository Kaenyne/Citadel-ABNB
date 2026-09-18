"""Independent arithmetic replay; imports no author forecasting/statistics code."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[5]
BASE=ROOT/'data/processed/forecast_methods/gbv_decision_0915_v1'
checks=[]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ck(label, actual, expected=True, atol=1e-7):
    if isinstance(expected,(str,bool)): ok=actual==expected;delta=None
    else:
        a,b=np.asarray(actual,float),np.asarray(expected,float)
        ok=bool(np.allclose(a,b,rtol=1e-9,atol=atol,equal_nan=True))
        delta=float(np.nanmax(abs(a-b))) if a.size and np.isfinite(a-b).any() else None
    checks.append(dict(check=label,passed=bool(ok),max_abs_delta=delta))
    if not ok: raise AssertionError((label,actual,expected))
def qs(q,k):return str(pd.Period(q,freq='Q')+k)
def rmse(e):return np.sqrt(np.mean(np.asarray(e)**2))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--horizon',default='results_v2');args=ap.parse_args()
    out=args.out.resolve()
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True)
    h=BASE/'horizon_v1'/args.horizon
    m=json.loads((h/'manifest.json').read_text())
    for name,digest in m['outputs'].items():ck('horizon hash '+name,sha(h/name),digest)
    for name,digest in m['source_hashes'].items():ck('source hash '+name,sha(ROOT/m['source_paths'][name]),digest)
    ck('author code hash',sha(ROOT/'analysis/src/forecast_methods/gbv_decision_0915_v1/horizon_v1/run.py'),m['code_sha256'])
    raw=pd.read_csv(ROOT/'data/processed/overnight/02_kpi_panel_quarterly.csv')
    raw['quarter']=raw.quarter.map(lambda q:f'20{q[2:]}Q{q[0]}')
    cal=pd.read_csv(ROOT/'data/processed/forecast_methods/harness/calendar.csv')
    raw['print_date']=pd.to_datetime(raw.quarter.map(cal.set_index('print_quarter').print_date))
    raw=raw.sort_values('quarter').set_index('quarter')
    guide=cal.dropna(subset=['next_quarter_guided','guide_mid']).set_index('next_quarter_guided')
    pred=pd.read_csv(h/'predictions.csv');inputs=pd.read_csv(h/'gbv_inputs.csv');parts=pd.read_csv(h/'gbv_contributions.csv')
    fits=pd.read_csv(h/'origin_fits.csv').set_index('origin_date')
    ck('unique points',not pred.duplicated(['origin_date','target','model']).any())
    for r in inputs.itertuples():
        known=raw[raw.print_date<=pd.Timestamp(r.origin_date)]
        latest=known.index.max();vals=known.gbv_musd.to_dict();growth=vals[latest]/vals[qs(latest,-4)]
        status='reported' if r.gbv_quarter in vals else 'forecast'
        for q in pd.period_range(pd.Period(latest,freq='Q')+1,pd.Period(r.target,freq='Q'),freq='Q'):
            vals[str(q)]=vals[str(q-4)]*growth
        ck('GBV status '+str(r.Index),r.gbv_status,status)
        ck('GBV value '+str(r.Index),r.gbv_musd,vals[r.gbv_quarter])
        ck('GBV publication '+str(r.Index),r.last_company_publication,str(known.print_date.max().date()))
    for origin,fit in fits.iterrows():
        known=raw[raw.print_date<=pd.Timestamp(origin)];training=[]
        for q in known.index:
            if all(qs(q,-k) in known.index for k in range(5)):training.append(q)
        ck('fit training '+origin,fit.training_quarters,'|'.join(training));ck('fit n '+origin,fit.n_train,len(training))
        phi=np.array([fit[f'weight_group_{k}'] for k in range(4)])
        ck('fit nonnegative '+origin,bool((phi>=0).all()));ck('fit simplex '+origin,phi.sum(),1.)
        for s in range(1,5):
            qq=[q for q in training if q.endswith(str(s))]
            x=np.array([[known.loc[q,'gbv_musd'],known.loc[qs(q,-1),'gbv_musd'],known.loc[qs(q,-2),'gbv_musd'],np.mean([known.loc[qs(q,-k),'gbv_musd'] for k in [3,4]])] for q in qq])
            scale=np.average(known.loc[qq,'revenue_musd'].values/(x@phi),weights=2.**(-np.arange(len(qq)-1,-1,-1)/2))
            ck('joint season '+origin+str(s),fit[f'lambda_Q{s}_pct'],100*scale)
    for r in pred.itertuples():
        label=f'{r.origin_date}/{r.target}/{r.model}'
        known=raw[raw.print_date<=pd.Timestamp(r.origin_date)];latest=known.index.max()
        completed=[q for q in known.index if q in guide.index][-8:]
        ck('cushion timing '+label,all(pd.Timestamp(guide.loc[q,'print_date'])<=pd.Timestamp(r.origin_date) for q in completed))
        cushion=np.mean([known.loc[q,'revenue_musd']/guide.loc[q,'guide_mid']-1 for q in completed])
        ck('cushion '+label,r.cushion_divisor,1+cushion);ck('cushion n '+label,r.n_cushion,len(completed))
        ck('R to G '+label,r.guide_mid_musd,r.revenue_musd/(1+cushion))
        ck('last p '+label,r.last_reported_quarter,latest)
        ck('horizon '+label,r.horizon_quarters,pd.Period(r.target,freq='Q').ordinal-pd.Period(latest,freq='Q').ordinal)
        if not r.is_live:
            ck('actual R '+label,r.actual_revenue_musd,raw.loc[r.target,'revenue_musd'])
            ck('actual G '+label,r.actual_guide_mid_musd,guide.loc[r.target,'guide_mid'])
        if r.model.replace('_oracle','') in ['joint','fixed']:
            base=r.model.replace('_oracle','');z=inputs[(inputs.origin_date==r.origin_date)&(inputs.target==r.target)].sort_values('lag')
            gv=z.gbv_musd.values if not r.model.endswith('_oracle') else z.oracle_realized_gbv_musd.values
            if base=='joint':
                f=fits.loc[r.origin_date];w=np.array([f.weight_group_0,f.weight_group_1,f.weight_group_2,f.weight_group_3/2,f.weight_group_3/2]);lam=f[f'lambda_Q{r.target[-1]}_pct']/100
                ck('joint n '+label,r.n_train,f.n_train)
            else:
                qq=[q for q in known.index if q[-1]==r.target[-1] and all(qs(q,-k) in known.index for k in [1,2])]
                ratios=[known.loc[q,'revenue_musd']/(2/3*known.loc[qs(q,-1),'gbv_musd']+1/3*known.loc[qs(q,-2),'gbv_musd']) for q in qq]
                lam=np.average(ratios,weights=2.**(-np.arange(len(qq)-1,-1,-1)/2));w=np.array([0,2/3,1/3,0,0]);ck('fixed n '+label,r.n_train,len(qq))
            ck('coefficient '+label,r.seasonal_lambda_pct,100*lam);ck('point arithmetic '+label,r.revenue_musd,lam*(w@gv))
            if not r.model.endswith('_oracle'):
                knownshare=(lam*w*gv)[z.gbv_status.values=='reported'].sum()/r.revenue_musd
                ck('known exposure '+label,r.known_gbv_dollar_share,knownshare)
                ck('exposure complement '+label,r.projected_gbv_dollar_share,1-knownshare)
            elif 'point_in_time_eligible' in pred:
                ck('oracle ineligible '+label,bool(r.point_in_time_eligible),False)
                ck('oracle actual availability '+label,r.knowable_from,str(raw.loc[r.target,'print_date'].date()))
        elif r.model=='revenue_growth':
            value=known.loc[qs(r.target,-4),'revenue_musd']*known.loc[latest,'revenue_musd']/known.loc[qs(latest,-4),'revenue_musd']
            ck('revenue baseline '+label,r.revenue_musd,value)
        elif r.model=='guide_growth':
            available=guide[pd.to_datetime(guide.print_date)<=pd.Timestamp(r.origin_date)]
            last=max(q for q in available.index if qs(q,-4) in available.index)
            value=available.loc[qs(r.target,-4),'guide_mid']*available.loc[last,'guide_mid']/available.loc[qs(last,-4),'guide_mid']
            ck('guide baseline '+label,r.guide_mid_musd,value);ck('latest guide anchor '+label,r.latest_growth_target,last)
    for r in parts.itertuples():
        ck('contribution '+str(r.Index),r.revenue_contribution_musd,r.gbv_musd*r.exposure_weight*r.seasonal_lambda_pct/100)
        ck('guide contribution '+str(r.Index),r.guide_contribution_musd,r.revenue_contribution_musd/r.cushion_divisor)
    common=pd.read_csv(h/'common_predictions.csv')
    for (hh,ww),d in common.groupby(['horizon_quarters','window']):
        lower='2023Q1' if ww=='W1' else '2024Q1'
        native=pred[(~pred.is_live)&(pred.horizon_quarters==hh)&(pred.target>=lower)&pred.model.isin(['joint','fixed','guide_growth','revenue_growth'])]
        expect=set(native.groupby('target').filter(lambda x:x.model.nunique()==4).target)
        ck(f'common sample {hh}/{ww}',set(d.target)==expect)
    for r in pd.read_csv(h/'scores_common.csv').itertuples():
        d=common[(common.horizon_quarters==r.horizon_quarters)&(common.window==r.window)&(common.model==r.model)]
        col='guide_mid_musd' if r.object=='guide' else 'revenue_musd';act='actual_'+col
        e=d[col]-d[act]
        for name,val in dict(n=len(d),n_year_clusters=d.year.nunique(),rmse_musd=rmse(e),mae_musd=abs(e).mean(),bias_musd=e.mean(),error_sd_musd=e.std(ddof=1),worst_abs_miss_musd=abs(e).max(),relative_rmse_pct=100*rmse(e/d[act])).items():ck('score '+str(r.Index)+name,getattr(r,name),val)
    comparisons=pd.read_csv(h/'paired_comparisons.csv');deletions=pd.read_csv(h/'score_deletions.csv')
    for r in comparisons.itertuples():
        d=common[(common.horizon_quarters==r.horizon_quarters)&(common.window==r.window)]
        col='guide_mid_musd' if r.object=='guide' else 'revenue_musd';m=d.pivot(index='target',columns='model',values=col).sort_index()
        a=d.drop_duplicates('target').set_index('target')['actual_'+col].reindex(m.index)
        ec=m[r.candidate]-a;eb=m[r.reference]-a;years=np.array([int(q[:4]) for q in m.index]);uy=np.unique(years)
        rng=np.random.default_rng(20260915+r.horizon_quarters);draws=rng.choice(uy,size=(2000,len(uy)),replace=True)
        ratios=[];loss=[]
        for draw in draws:
            ix=np.concatenate([np.where(years==y)[0] for y in draw]);c=ec.iloc[ix].values;b=eb.iloc[ix].values
            ratios.append(rmse(c)/rmse(b));loss.append(np.mean(c*c-b*b))
        for name,val in dict(n=len(m),rmse_ratio=rmse(ec)/rmse(eb),ratio_p05=np.quantile(ratios,.05),ratio_p95=np.quantile(ratios,.95),loss_difference_p05_musd2=np.quantile(loss,.05),loss_difference_p95_musd2=np.quantile(loss,.95)).items():ck('paired '+str(r.Index)+name,getattr(r,name),val)
    for r in deletions.itertuples():
        d=common[(common.horizon_quarters==r.horizon_quarters)&(common.window==r.window)]
        d=d[d.year.astype(str)!=str(r.deleted_value)] if r.deleted_unit=='year' else d[d.target!=r.deleted_value]
        e={k:(z.guide_mid_musd-z.actual_guide_mid_musd).values for k,z in d.groupby('model')}
        ck('deletion '+str(r.Index),r.guide_rmse_ratio,rmse(e[r.candidate])/rmse(e[r.reference]))
    for r in pd.read_csv(h/'promotion_gates.csv').itertuples():
        p=comparisons[(comparisons.horizon_quarters==r.horizon_quarters)&(comparisons.candidate==r.model)&(comparisons.object=='guide')&comparisons.reference.isin(['guide_growth','revenue_growth'])]
        d=deletions[(deletions.horizon_quarters==r.horizon_quarters)&(deletions.candidate==r.model)&deletions.reference.isin(['guide_growth','revenue_growth'])]
        gates=dict(coverage_pass=len(p)==4 and (p.n>=8).all(),magnitude_pass=(p.rmse_ratio<=.9).all(),deletion_pass=(d.guide_rmse_ratio<1).all(),paired_guidegrowth_interval_pass=(p[p.reference=='guide_growth'].ratio_p95<1).all())
        gates['promotion_pass']=all(gates.values())
        for k,v in gates.items():ck('gate '+str(r.Index)+k,bool(getattr(r,k)),bool(v))
    diag=[];regime=[]
    for (hh,ww),d in common.groupby(['horizon_quarters','window']):
        m=d.pivot(index='target',columns='model',values='guide_mid_musd').sort_index();a=d.drop_duplicates('target').set_index('target').actual_guide_mid_musd.reindex(m.index)
        for model in ['joint','fixed']:
            x=m[model]-m[model+'_oracle'];z=m[model+'_oracle']-a;e=m[model]-a
            rec=dict(horizon=hh,window=ww,model=model,n=len(e),input_mean=x.mean(),remaining_mean=z.mean(),input_rms=rmse(x),remaining_rms=rmse(z),total_rmse=rmse(e),input_mse=np.mean(x*x),remaining_mse=np.mean(z*z),twice_cross_moment=2*np.mean(x*z),total_mse=np.mean(e*e),input_variance=x.var(ddof=1),remaining_variance=z.var(ddof=1),twice_covariance=2*np.cov(x,z,ddof=1)[0,1],total_variance=e.var(ddof=1))
            ck(f'MSE identity {hh}/{ww}/{model}',rec['total_mse'],rec['input_mse']+rec['remaining_mse']+rec['twice_cross_moment'])
            ck(f'variance identity {hh}/{ww}/{model}',rec['total_variance'],rec['input_variance']+rec['remaining_variance']+rec['twice_covariance'])
            diag.append(rec)
        for model in m:
            e=m[model]-a
            for label,mask in [('before_2025Q3',m.index<'2025Q3'),('2025Q3_onward',m.index>='2025Q3')]:
                v=e[mask];regime.append(dict(horizon=hh,window=ww,model=model,period=label,n=len(v),targets='|'.join(v.index),bias_musd=v.mean(),rmse_musd=rmse(v),positive_error_count=int((v>0).sum()),mean_relative_error_pct=100*(v/a[mask]).mean()))
    pd.DataFrame(diag).to_csv(out/'covariance_reconciliation.csv',index=False)
    pd.DataFrame(regime).to_csv(out/'regime_descriptive.csv',index=False)
    pd.DataFrame(checks).to_csv(out/'checks.csv',index=False)
    receipt=dict(status='PASS',independent_arithmetic_checks=len(checks),source_manifest_sha256=sha(h/'manifest.json'),horizon_path=str(h.relative_to(ROOT)),review_code_sha256=sha(__file__),imports_author_code=False,no_new_fit=True,limitations=['fitted shape coefficients audited conditional on saved fit; boundary tests are separate','reused history; nested and sometimes identical windows','raw guide-midpoint errors, distinct from interval harness scores'])
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
