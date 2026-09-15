"""Actual frozen-code boundary attacks; no new rule or fitted candidate search."""
from pathlib import Path
import argparse, hashlib, importlib.util, json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[5]
SOURCE=ROOT/'analysis/src/forecast_methods/gbv_decision_0915_v1/horizon_v1/run.py'
spec=importlib.util.spec_from_file_location('gd_horizon_under_test',SOURCE)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
checks=[]
def ck(label,ok):
    checks.append(dict(check=label,passed=bool(ok)))
    if not ok:raise AssertionError(label)
def points(engine,target,date,live=False):
    rows=engine.predict(target,date,live)[0]
    return pd.DataFrame([r for r in rows if not r['model'].endswith('_oracle')]).set_index('model')[['revenue_musd','guide_mid_musd']].sort_index()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve()
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True)
    core=mod.accepted_core();panel,calendar=core.load_inputs()
    for date in ['2023-08-03','2024-02-13','2026-09-15']:
        known=panel[panel.print_date<=pd.Timestamp(date)];last=known.quarter.max()
        original=mod.FrozenForecasts(panel,calendar)
        changed=panel.copy();future=changed.print_date>pd.Timestamp(date)
        changed.loc[future,['gbv_musd','revenue_musd']]*=1000
        changed_calendar=calendar.copy();cf=pd.to_datetime(changed_calendar.print_date)>pd.Timestamp(date)
        changed_calendar.loc[cf,'guide_mid']=999999.
        poisoned=mod.FrozenForecasts(changed,changed_calendar)
        # Also remove future realized KPI rows entirely. Calendar retained for ex-post scoring labels.
        truncated=mod.FrozenForecasts(known,calendar)
        for h in [2,3,4]:
            target=mod.qshift(last,h);base=points(original,target,date,date=='2026-09-15')
            ck(f'future values and future guide poison invariant {date}/{h}',np.allclose(base,points(poisoned,target,date,date=='2026-09-15'),atol=1e-7,rtol=1e-10))
            ck(f'future KPI deletion invariant {date}/{h}',np.allclose(base,points(truncated,target,date,date=='2026-09-15'),atol=1e-7,rtol=1e-10))
        # Positive control: already-issued p+1 guidance changes direct-guide baseline.
        cg=calendar.copy();mask=cg.next_quarter_guided==mod.qshift(last,1);cg.loc[mask,'guide_mid']*=1.1
        altered=mod.FrozenForecasts(panel,cg)
        target=mod.qshift(last,2)
        ck(f'known guide positive control {date}',not np.isclose(points(original,target,date).loc['guide_growth','guide_mid_musd'],points(altered,target,date).loc['guide_growth','guide_mid_musd']))
        # Previous reported GBV is materially used; no test-only future imputation.
        cp=panel.copy();cp.loc[cp.quarter==last,'gbv_musd']*=1.1
        altered=mod.FrozenForecasts(cp,calendar)
        ck(f'known GBV positive control {date}',not np.isclose(points(original,target,date).loc['fixed','guide_mid_musd'],points(altered,target,date).loc['fixed','guide_mid_musd']))
    # Guard horizons outside authorized p+2..4 and retain early joint abstention.
    eng=mod.FrozenForecasts(panel,calendar)
    for target in ['2026Q3','2027Q3']:
        try:eng.predict(target,'2026-09-15');rejected=False
        except ValueError:rejected=True
        ck('out of scope horizon '+target,rejected)
    rows,skips,*_=eng.predict('2023Q1','2022-11-01')
    ck('joint early abstention preserved',not any(r['model']=='joint' for r in rows) and any(s['model']=='joint' for s in skips))
    # Fixed Sept15 cutoff uses same complete all-history fit as preceding accepted live adapter.
    known,train,fit,cushion,nc=eng.origin('2026-09-15')
    ck('live all-history train20',len(train)==20 and train.quarter.min()=='2021Q3' and train.quarter.max()=='2026Q2')
    live=eng.predict('2026Q4','2026-09-15',True)
    ck('live GBV statuses', {x['gbv_quarter']:x['gbv_status'] for x in live[2]}=={'2026Q4':'forecast','2026Q3':'forecast','2026Q2':'reported','2026Q1':'reported','2025Q4':'reported'})
    ck('live no oracle rows',not any(r['model'].endswith('_oracle') for r in live[0]))
    for target in ['2027Q1','2027Q2']:
        ck('unknown future event date remains blank '+target,all(r['guide_event_date']=='' for r in eng.predict(target,'2026-09-15',True)[0]))
    pd.DataFrame(checks).to_csv(out/'checks.csv',index=False)
    receipt=dict(status='PASS',actual_code_checks=len(checks),code_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),review_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),no_new_rule=True)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
