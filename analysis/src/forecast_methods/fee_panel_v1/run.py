"""Offline consumer for sanctioned fee captures; listed-price association only."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import pandas as pd
from scipy.stats import t
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[4]
WAVES = {'sep': ['2026-09-14','2026-09-16','2026-09-18'],
         'oct': ['2026-10-12','2026-10-14','2026-10-16']}
KEY = ['listing_id','checkin','checkout','nights']
META = ['city','country_iso2','host_region_guess','room_type','bedroom_bucket','host_class','stay_window']

def neutral_log(new_fee, old_fee=0.03):
    if not 0 <= old_fee < 1 or not old_fee < new_fee < 1:
        raise ValueError('invalid fee regime')
    return float(np.log((1-old_fee)/(1-new_fee)))

def load_metadata(path, as_of):
    m = pd.read_csv(path, dtype={'listing_id':str}, keep_default_na=False)
    needed = KEY + META + ['dump_date']
    if set(needed) - set(m):
        raise ValueError(f'metadata missing {set(needed)-set(m)}')
    metadata_dates=pd.to_datetime(m.dump_date, errors='coerce')
    if metadata_dates.isna().any() or (metadata_dates.dt.date > pd.Timestamp(as_of).date()).any():
        raise ValueError('future metadata')
    if m.duplicated(KEY).any():
        raise ValueError('duplicate metadata key')
    m['nights'] = pd.to_numeric(m.nights, errors='raise')
    known=m.host_region_guess.isin(['eea_ch','non_eea'])
    if not m.loc[known,'country_iso2'].str.fullmatch('[A-Z]{2}').all():
        raise ValueError('known residence requires explicit listing country fee regime')
    return m[needed]

def load_captures(paths, metadata, as_of):
    rows=[]
    for path in paths:
        d=pd.read_csv(path, dtype={'listing_id':str}, keep_default_na=False)
        required=KEY+['currency','nightly_price','captured_at','parse_status','city','stay_window']
        if set(required)-set(d):
            raise ValueError(f'{path}: missing {set(required)-set(d)}')
        stamps=pd.to_datetime(d.captured_at, utc=True, errors='raise')
        if stamps.isna().any() or (stamps >= pd.Timestamp(as_of,tz='UTC')+pd.Timedelta(days=1)).any():
            raise ValueError('future or missing capture timestamp')
        d['capture_date']=stamps.dt.strftime('%Y-%m-%d')
        d['nightly_price']=pd.to_numeric(d.nightly_price, errors='coerce')
        d['nights']=pd.to_numeric(d.nights, errors='raise')
        valid=(d.parse_status.eq('ok') & np.isfinite(d.nightly_price) & d.nightly_price.gt(0))
        d=d.loc[valid].copy()
        if not d.currency.str.fullmatch('[A-Z]{3}').all():
            raise ValueError('missing or non-ISO currency')
        d['source_file']=str(path)
        rows.append(d[required+['capture_date','source_file']])
    if not rows:
        return pd.DataFrame()
    d=pd.concat(rows, ignore_index=True)
    if d.duplicated(KEY+['capture_date']).any():
        raise ValueError('duplicate capture key: select one run per date explicitly')
    if (d.groupby(KEY).currency.nunique()>1).any():
        raise ValueError('currency changes within listing/stay')
    # Geography from capture remains descriptive; residence comes only from metadata.
    d=d.rename(columns={'city':'capture_city','stay_window':'capture_stay'})
    d=d.merge(metadata,on=KEY,how='left',validate='many_to_one')
    known_metadata=d.dump_date.notna()
    if (pd.to_datetime(d.loc[known_metadata,'dump_date'],errors='raise') >
            pd.to_datetime(d.loc[known_metadata,'capture_date'],errors='raise')).any():
        raise ValueError('metadata unavailable at capture date')
    if ((d.city.notna()) & (d.city.ne(d.capture_city))).any():
        raise ValueError('capture/metadata geography mismatch')
    d['city']=d.city.fillna(d.capture_city)
    d['stay_window']=d.stay_window.fillna(d.capture_stay)
    for c in ['host_region_guess','room_type','bedroom_bucket','host_class']:
        d[c]=d[c].fillna('unknown').replace('','unknown')
    d['country_iso2']=d.country_iso2.fillna('')
    return d

def overlap_table(d, dates):
    if d.empty:
        return pd.DataFrame(columns=['stratum','value','comparison','n_pre','n_post','n_matched','retention','jaccard','primary_gate'])
    parts=[('pooled','all',d)]
    for cols in [['city','stay_window'],['host_region_guess'],['room_type'],['bedroom_bucket'],['host_class']]:
        for k,g in d.groupby(cols,dropna=False):
            parts.append(('+'.join(cols),'|'.join(str(v) for v in (k if isinstance(k,tuple) else (k,))),g))
    out=[]
    for label,value,g in parts:
        sets=[set(map(tuple,g.loc[g.capture_date.eq(date),KEY].to_numpy())) for date in dates]
        pre=sets[0]
        for name,post in [('pre_post1',sets[1]),('pre_post2',sets[2]),('pre_both_post',sets[1]&sets[2])]:
            matched=len(pre&post)
            out.append(dict(stratum=label,value=value,comparison=name,n_pre=len(pre),n_post=len(post),n_matched=matched,
                            retention=matched/len(pre) if pre else None,jaccard=matched/len(pre|post) if pre|post else None,
                            primary_gate=(len(pre)>0)))
    return pd.DataFrame(out)

def panel_overlaps(d,dates):
    """Retain all descriptive coverage; gate only the residence-known population."""
    all_rows=overlap_table(d,dates)
    all_rows['population']='all_descriptive';all_rows['primary_gate']=False
    known=d if d.empty else d[d.host_region_guess.isin(['eea_ch','non_eea'])]
    primary=overlap_table(known,dates)
    primary['population']='known_residence_primary'
    return pd.concat([all_rows,primary],ignore_index=True)

def estimate(d, dates, wave):
    known=d[d.host_region_guess.isin(['eea_ch','non_eea'])].copy()
    if not known.country_iso2.fillna('').str.fullmatch('[A-Z]{2}').all():
        raise ValueError('missing listing country fee regime')
    overlap=panel_overlaps(d,dates)
    gate=overlap[(overlap.comparison=='pre_both_post') & overlap.primary_gate]
    if gate.empty or (gate.retention < .40).any():
        return {'status':'blocked_overlap','n':0},overlap
    pivot=known.pivot(index=KEY,columns='capture_date',values='nightly_price')
    if not set(dates).issubset(pivot):
        return {'status':'blocked_missing_wave','n':0},overlap
    complete=pivot.dropna(subset=dates)[dates].copy()
    complete['delta']=np.log(complete[dates[1:]]).mean(axis=1)-np.log(complete[dates[0]])
    info=known.drop_duplicates(KEY)[KEY+META].set_index(KEY)
    z=complete[['delta']].join(info).reset_index()
    z['treated']=z.host_region_guess.eq('non_eea' if wave=='sep' else 'eea_ch')
    counts=z.groupby('treated').listing_id.nunique()
    clusters=z.listing_id.nunique()
    if len(counts)!=2 or counts.min()<2 or clusters<4:
        return {'status':'blocked_arm_support','n':len(z),'clusters':clusters},overlap
    z['denominator']=z.country_iso2.map(lambda c: neutral_log(.16 if c in ['MX','BR'] else .155))
    X=pd.concat([pd.Series(1.0,index=z.index,name='intercept'), (z.treated*z.denominator).rename('theta'),
                 pd.get_dummies(z.stay_window,prefix='stay',drop_first=True,dtype=float)],axis=1)
    if len(z)<=X.shape[1] or np.linalg.matrix_rank(X.to_numpy())!=X.shape[1]:
        return {'status':'blocked_rank','n':len(z)},overlap
    fit=sm.OLS(z.delta,X).fit(cov_type='cluster',cov_kwds={'groups':z.listing_id,'use_correction':True})
    coef=float(fit.params['theta']); se=float(fit.bse['theta']); half=float(t.ppf(.975,clusters-1))*se
    width=2*half
    return {'status':'association_precision_pass' if np.isfinite(width) and width<.58 else 'fail_precision',
            'n':len(z),'clusters':clusters,'treated_clusters':int(counts[True]),'control_clusters':int(counts[False]),
            'theta':coef,'lower':coef-half,'upper':coef+half,'interval_width':width,'causal_identified':False,
            'n_parameters':X.shape[1]},overlap

def run(paths, metadata_path, as_of, out):
    out=Path(out)
    if out.exists():
        raise FileExistsError('Use a new immutable output directory: '+str(out))
    metadata=load_metadata(metadata_path,as_of)
    d=load_captures(paths,metadata,as_of)
    out.mkdir(parents=True)
    summary={'information_date':as_of,'implementation':'complete','research':'partial_future_captures',
             'price_basis':'listed_price_only','w1_n':0,'w2_n':0,'captures':len(paths),'waves':{}}
    if not d.empty:
        desc=d.groupby(['city','stay_window','capture_date','currency']).nightly_price.agg(['count','median']).reset_index()
        desc['index_first_available_100']=100*desc['median']/desc.groupby(['city','stay_window','currency'])['median'].transform('first')
        desc.to_csv(out/'descriptive_indices.csv',index=False)
    overlap=[]
    for wave,dates in WAVES.items():
        present=[] if d.empty else sorted(set(d.capture_date)&set(dates))
        if set(dates)!=set(present):
            result={'status':'blocked_future_or_missing_captures','n':0,'missing_dates':sorted(set(dates)-set(present))}
            table=panel_overlaps(d,dates)
        else:
            result,table=estimate(d,dates,wave)
        summary['waves'][wave]=result
        table['wave']=wave;overlap.append(table)
    pd.concat(overlap,ignore_index=True).to_csv(out/'overlap.csv',index=False)
    frame=metadata.drop_duplicates('listing_id')
    frame.groupby('host_region_guess').size().rename('n_listings').to_csv(out/'frame_residence_coverage.csv')
    # Historical dry run measures metadata coverage only, never passes a future-wave gate.
    dry=ROOT/'data/processed/forecast_methods/fee_panels/dryrun_new-orleans_2026-09-11.csv'
    dry_metadata_path=ROOT/'data/processed/forecast_methods/fee_panels/sample_ids.csv'
    dry_metadata=load_metadata(dry_metadata_path,as_of)
    dry_data=load_captures([dry],dry_metadata,as_of)
    summary['dry_run']={'n_rows':len(dry_data),'n_listings':dry_data.listing_id.nunique(),
                        'residence_known_rows':int(dry_data.host_region_guess.isin(['eea_ch','non_eea']).sum()),
                        'source':'frozen_2026-09-11_diagnostic_not_a_wave'}
    pd.DataFrame([{'country_regime':reg,'old_host_fee':.03,'new_host_fee':fee,'log_denominator':neutral_log(fee),
                   'arithmetic_neutral_reprice':.97/(1-fee)-1,'evidence_status':'conditional_mechanics'}
                  for reg,fee in [('standard',.155),('Mexico_Brazil',.16)]]).to_csv(out/'fee_denominators.csv',index=False)
    source_paths=list(dict.fromkeys([Path(metadata_path),dry_metadata_path,dry,Path(__file__),ROOT/'docs/revenue-forecast-strategy/05_backtests/L3_FEE_PREREG_v1.md']+list(paths)))
    pd.DataFrame([{'path':str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),
                   'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in source_paths]).to_csv(out/'source_manifest.csv',index=False)
    pd.DataFrame([{'quarter':q,'metric':'fee_theta_log','scenario':wave,'value':summary['waves'][wave].get('theta'),
                   'lower':summary['waves'][wave].get('lower'),'upper':summary['waves'][wave].get('upper'),'units':'fraction_log_neutral_reprice',
                   'information_date':as_of,'evidence_status':summary['waves'][wave]['status'],
                   'source_reference':'fee_panel_v1/summary.json','treatment':'unavailable_do_not_apply',
                   'baseline_being_replaced':'none','embedded_fx':'none; same-currency within-listing changes'}
                  for q,wave in [('2026Q3','sep'),('2026Q4','oct')]]).to_csv(out/'l4_inputs.csv',index=False)
    (out/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print(json.dumps(summary,indent=2))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--as-of',default='2026-09-13')
    ap.add_argument('--metadata',type=Path,default=ROOT/'data/processed/forecast_methods/fee_panels/sample_ids.csv')
    ap.add_argument('--capture',type=Path,action='append')
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    paths=a.capture if a.capture is not None else sorted((ROOT/'data/processed/forecast_methods/fee_panels/runs').glob('capture*.csv'))
    run(paths,a.metadata,a.as_of,a.out)

if __name__=='__main__':
    main()
