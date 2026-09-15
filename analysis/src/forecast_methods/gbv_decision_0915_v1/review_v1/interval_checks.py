"""Independent guide rounding sensitivity audit using projection onto actual bounds."""
from pathlib import Path
import argparse, hashlib, importlib.util, json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[5];BASE=ROOT/'data/processed/forecast_methods/gbv_decision_0915_v1';checks=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ck(label,a,b=True):
    ok=a==b if isinstance(b,(str,bool)) else np.allclose(a,b,atol=1e-8,rtol=1e-10,equal_nan=True)
    checks.append(dict(check=label,passed=bool(ok)))
    if not ok:raise AssertionError((label,a,b))
def rms(e):return np.sqrt(np.mean(np.asarray(e)**2))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve()
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);folder=BASE/'interval_v1/results_v1';m=json.loads((folder/'manifest.json').read_text())
    for key,obj in m['inputs'].items():ck('input hash '+key,sha(ROOT/obj['path']),obj['sha256'])
    for name,digest in m['outputs'].items():ck('output hash '+name,sha(folder/name),digest)
    source=ROOT/'analysis/src/forecast_methods/gbv_decision_0915_v1/interval_v1/run.py';ck('code hash',sha(source),m['code_sha256'])
    hp=pd.read_csv(ROOT/m['inputs']['horizon_predictions']['path']);hp=hp[~hp.is_live];fp=pd.read_csv(ROOT/m['inputs']['flight_predictions']['path'])
    scores=pd.read_csv(folder/'scores.csv');comp=pd.read_csv(folder/'comparisons.csv');deletions=pd.read_csv(folder/'deletions.csv');gates=pd.read_csv(folder/'gates.csv')
    cache={}
    def errors(scope,h,window,candidate,basis):
        key=(scope,h,window,candidate,basis)
        if key in cache:return cache[key]
        d=fp if scope=='calendar_flight' else hp[hp.horizon_quarters==h]
        d=d[d.target>=('2023Q1' if window=='W1' else '2024Q1')]
        names=['joint_flight','joint_noflight','fixed_flight','fixed_noflight','guide_growth','revenue_growth'] if scope=='calendar_flight' else ['joint','fixed','guide_growth','revenue_growth'] if scope=='common4' else [candidate,'guide_growth','revenue_growth']
        d=d[d.model.isin(names)];wide=d.pivot(index='target',columns='model',values='guide_mid_musd').dropna().sort_index();actual=d.drop_duplicates('target').set_index('target').actual_guide_mid_musd.reindex(wide.index)
        e=wide.sub(actual,axis=0)
        if basis=='integer_interval':
            # Independent geometric definition: prediction minus nearest point in [actual-.5, actual+.5].
            nearest=np.minimum(np.maximum(wide.to_numpy(),actual.to_numpy()[:,None]-.5),actual.to_numpy()[:,None]+.5)
            e=pd.DataFrame(wide.to_numpy()-nearest,index=wide.index,columns=wide.columns)
        cache[key]=e;return e
    for r in scores.itertuples():
        e=errors(r.scope,r.horizon_quarters,r.window,r.candidate_sample,r.scoring);v=e[r.model].values
        ck('sample targets '+str(r.Index),r.targets,'|'.join(e.index))
        for name,value in dict(n=len(v),n_year_clusters=len(set(e.index.str[:4])),rmse_musd=rms(v),mae_musd=np.mean(abs(v)),signed_distance_bias_musd=v.mean()).items():ck('score '+str(r.Index)+name,getattr(r,name),value)
        raw=errors(r.scope,r.horizon_quarters,r.window,r.candidate_sample,'raw_midpoint')[r.model]
        ck('inside rounding count '+str(r.Index),r.within_rounding_interval,int((abs(raw)<=.5).sum()))
    # Exact original pair-level RNG progression for flight, separately from horizon reseeding.
    flight_draws={};rng=np.random.default_rng(20260915)
    for window in ['W1','W2']:
        e=errors('calendar_flight',2,window,'all_six','raw_midpoint');ny=len(set(e.index.str[:4]))
        for candidate in ['joint_flight','fixed_flight']:
            for reference in [candidate.replace('flight','noflight'),'guide_growth','revenue_growth']:
                flight_draws[(window,candidate,reference)]=rng.integers(0,ny,size=(2000,ny))
    for r in comp.itertuples():
        e=errors(r.scope,r.horizon_quarters,r.window,r.candidate_sample,r.scoring);ec=e[r.candidate].values;eb=e[r.reference].values;years=e.index.str[:4].to_numpy();uy=np.unique(years)
        draw=flight_draws[(r.window,r.candidate,r.reference)] if r.scope=='calendar_flight' else np.random.default_rng(20260915+r.horizon_quarters).integers(0,len(uy),size=(2000,len(uy)))
        counts=np.stack([(draw==i).sum(axis=1) for i in range(len(uy))],axis=1);c=np.array([sum(ec[years==y]**2) for y in uy]);b=np.array([sum(eb[years==y]**2) for y in uy]);lo,hi=np.quantile(np.sqrt((counts@c)/(counts@b)),[.05,.95])
        for name,value in dict(n=len(e),candidate_rmse_musd=rms(ec),reference_rmse_musd=rms(eb),rmse_ratio=rms(ec)/rms(eb),ratio_p05=lo,ratio_p95=hi).items():ck('comparison '+str(r.Index)+name,getattr(r,name),value)
        if r.scoring=='raw_midpoint':
            key={'common4':'common_pairs','candidate_specific':'eligible_pairs','calendar_flight':'flight_pairs'}[r.scope];old=pd.read_csv(ROOT/m['inputs'][key]['path']).rename(columns={'baseline':'reference'})
            old=old[(old.window==r.window)&(old.candidate==r.candidate)&(old.reference==r.reference)]
            if r.scope!='calendar_flight':old=old[old.horizon_quarters==r.horizon_quarters]
            if 'object' in old:old=old[old.object=='guide']
            ck('one original raw comparison '+str(r.Index),len(old),1)
            for name in ['rmse_ratio','ratio_p05','ratio_p95']:ck('original raw match '+str(r.Index)+name,getattr(r,name),old.iloc[0][name])
    for r in deletions.itertuples():
        e=errors(r.scope,r.horizon_quarters,r.window,r.candidate_sample,r.scoring);e=e[e.index.str[:4]!=str(r.deleted_value)] if r.deleted_unit=='year' else e[e.index!=r.deleted_value]
        ck('deletion '+str(r.Index),r.rmse_ratio,rms(e[r.candidate])/rms(e[r.reference]));ck('deletion n '+str(r.Index),r.n,len(e))
    for r in gates.itertuples():
        p=comp[(comp.scope==r.scope)&(comp.horizon_quarters==r.horizon_quarters)&(comp.candidate==r.candidate)&(comp.scoring==r.scoring)]
        d=deletions[(deletions.scope==r.scope)&(deletions.horizon_quarters==r.horizon_quarters)&(deletions.candidate==r.candidate)&(deletions.scoring==r.scoring)]
        if r.scope=='calendar_flight':
            p=p[p.window==r.window].set_index('reference');d=d[(d.window==r.window)&(d.reference==r.candidate.replace('flight','noflight'))];own=p.loc[r.candidate.replace('flight','noflight')]
            vals=dict(coverage_pass=own.n>=8,magnitude_pass=own.rmse_ratio<=.9,deletion_pass=(d.rmse_ratio<1).all(),direct_guidegrowth_pass=p.loc['guide_growth','rmse_ratio']<1)
        else:
            p=p[p.reference.isin(['guide_growth','revenue_growth'])];d=d[d.reference.isin(['guide_growth','revenue_growth'])]
            vals=dict(coverage_pass=len(p)==4 and (p.n>=8).all(),magnitude_pass=(p.rmse_ratio<=.9).all(),deletion_pass=(d.rmse_ratio<1).all(),paired_guidegrowth_interval_pass=(p[p.reference=='guide_growth'].ratio_p95<1).all())
        vals['promotion_pass']=all(vals.values())
        for name,value in vals.items():ck('gate '+str(r.Index)+name,bool(getattr(r,name)),bool(value))
    for key,d in gates.groupby(['scope','horizon_quarters','candidate','window']):
        raw=d[d.scoring=='raw_midpoint'].iloc[0];iv=d[d.scoring=='integer_interval'].iloc[0]
        for name in ['coverage_pass','magnitude_pass','deletion_pass','paired_guidegrowth_interval_pass','direct_guidegrowth_pass','promotion_pass']:
            ck('raw interval unchanged '+str(key)+name,True if pd.isna(raw[name]) and pd.isna(iv[name]) else raw[name]==iv[name])
    arithmetic_count=len(checks)
    # Separate tiny actual-code checks; statistical replay above did not import author functions.
    spec=importlib.util.spec_from_file_location('interval_under_test',source);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    for err,expected in [(-2,-1.5),(-.500001,-.000001),(-.5,0),(-.2,0),(0,0),(.2,0),(.5,0),(.500001,.000001),(2,1.5)]:ck('actual code interval edge '+str(err),mod.residual([err])[0],expected)
    ck('zero width raw identity',mod.residual([-2,0,.3],0),[-2,0,.3])
    for inp,width in [([1],-1),([float('nan')],.5),([1],float('inf'))]:
        try:mod.residual(inp,width);reject=False
        except ValueError:reject=True
        ck('invalid interval input '+str(inp)+str(width),reject)
    pd.DataFrame(checks).to_csv(out/'checks.csv',index=False)
    receipt=dict(status='PASS',independent_saved_arithmetic_checks=arithmetic_count,actual_code_edge_checks=len(checks)-arithmetic_count,interval_manifest_sha256=sha(folder/'manifest.json'),review_code_sha256=sha(__file__),actual_halfwidth_musd=.5,changed_gate_components=0,changed_promotion_outcomes=0,conclusion_unchanged=True,raw_replication=True,no_fit=True,interval_is_rounding_not_prediction=True)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
