"""Independently verify prepared rows without author adapter or registry writes."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[5];BASE=ROOT/'data/processed/forecast_methods/gbv_decision_0915_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve()
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);checks=[]
    def ck(label,ok):
        checks.append(dict(check=label,passed=bool(ok)))
        if not ok:raise AssertionError(label)
    stage=BASE/'control_v1/prepared_v1';receipt=json.loads((stage/'receipt.json').read_text());source=BASE/'horizon_v1/results_v2/predictions.csv'
    ck('source hash',sha(source)==receipt['source_sha256'])
    tables=[]
    for name,digest in receipt['staged_sha256'].items():
        path=stage/'prepared_registry'/name;ck('stage hash '+name,sha(path)==digest);tables.append(pd.read_csv(path))
    d=pd.concat(tables,ignore_index=True);p=pd.read_csv(source);p=p[p.model.isin(['joint','fixed','guide_growth','revenue_growth'])]
    expected=[]
    for r in p.itertuples():
        for obj in ['guide']+(['revenue'] if r.model in ['joint','fixed'] else []):
            for ww in ['LIVE'] if r.is_live else ['W1']+(['W2'] if r.target>='2024Q1' else []):
                expected.append((f'{r.model}-p{r.horizon_quarters}-{obj}',r.target,r.origin_date,ww))
    ck('exact expanded point universe',set(expected)==set(map(tuple,d[['object','quarter','vintage_date','window']].values)))
    ck('421 unique rows',len(d)==421 and not d.duplicated(['object','quarter','vintage_date','window']).any());ck('18 objects',d.object.nunique()==18);ck('18 live rows',int((d.window=='LIVE').sum())==18)
    ck('no manufactured bands',d[['q05','q10','q25','q75','q90','q95','sd']].isna().all().all())
    lookup=p.set_index(['origin_date','target','model'])
    cal=pd.read_csv(ROOT/'data/processed/forecast_methods/harness/calendar.csv');real_dates=set(cal[cal.is_forecast_row==False].print_date)
    for r in d.itertuples():
        model,h,obj=r.object.split('-');src=lookup.loc[(r.vintage_date,r.quarter,model)];label=str(r.Index)
        col='guide_mid_musd' if obj=='guide' else 'revenue_musd';params=src['n_params_guide' if obj=='guide' else 'n_params_revenue']
        ck('point '+label,np.isclose(r.point,src[col],atol=1e-7,rtol=1e-10));ck('q50 placeholder '+label,r.q50==r.point)
        ck('params '+label,r.n_params==params);ck('train count '+label,r.n_train==src.n_train)
        ck('information eligibility '+label,bool(src.point_in_time_eligible) and not bool(src.oracle_future_information_used) and r.knowable_from<=r.vintage_date)
        ck('registry quarter horizon '+label,r.horizon_q==pd.Period(r.quarter,freq='Q').ordinal-pd.Timestamp(r.vintage_date).to_period('Q').ordinal)
        ck('target object '+label,r.target==('guide_mid' if obj=='guide' else 'revenue_musd'))
        ck('release-only historical origin '+label,(r.vintage_date in real_dates and r.vintage_date<src.guide_event_date) if r.window!='LIVE' else r.vintage_date=='2026-09-15' and r.quarter in ['2026Q4','2027Q1','2027Q2'])
    pd.DataFrame(checks).to_csv(out/'checks.csv',index=False)
    final=dict(status='PASS_FOR_RESEARCH_REGISTRATION',checks=len(checks),rows=len(d),objects=d.object.nunique(),stage_receipt_sha256=sha(stage/'receipt.json'),source_sha256=sha(source),review_code_sha256=sha(__file__),promotion=False,calibrated_intervals=False,shared_registry_written_by_reviewer=False)
    (out/'receipt.json').write_text(json.dumps(final,indent=2));print(json.dumps(final,indent=2))
if __name__=='__main__':main()
