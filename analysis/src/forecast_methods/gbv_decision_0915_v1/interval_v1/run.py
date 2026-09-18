"""Additive integer-letter guide loss sensitivity from immutable saved points."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
DATA = ROOT / 'data/processed/forecast_methods/gbv_decision_0915_v1'
NOTES = ROOT / 'docs/revenue-forecast-strategy/05_backtests'
WINDOWS = {'W1': '2023Q1', 'W2': '2024Q1'}
SEED = 20260915
PRODUCTION = ['joint', 'fixed', 'guide_growth', 'revenue_growth']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def residual(error, width=0.5):
    error = np.asarray(error, dtype=float)
    if width < 0 or not np.isfinite(width) or not np.isfinite(error).all():
        raise ValueError('Finite errors and a finite nonnegative interval half-width required')
    return np.sign(error) * np.maximum(np.abs(error) - width, 0)


def ratio(candidate_sse, reference_sse):
    if np.any(np.asarray(reference_sse) <= 0):
        raise ValueError('Zero reference loss: ratio undefined; cannot treat as a pass')
    return np.sqrt(candidate_sse / reference_sse)


def sample(frame, models):
    if frame.duplicated(['target', 'model']).any():
        raise ValueError('Ambiguous target-model row')
    if frame.groupby('target').origin_date.nunique().gt(1).any():
        raise ValueError('Different origins on a paired target')
    if frame.groupby('target').actual_guide_mid_musd.nunique().gt(1).any():
        raise ValueError('Inconsistent actual midpoint')
    wide = frame.pivot(index='target', columns='model', values='guide_mid_musd')
    wide = wide.reindex(columns=models).dropna().sort_index()
    if wide.empty:
        raise ValueError('No paired observations; no scoring or promotion available')
    actual = frame.drop_duplicates('target').set_index('target').actual_guide_mid_musd.reindex(wide.index)
    if not np.isfinite(wide.to_numpy()).all() or not np.isfinite(actual).all():
        raise ValueError('Nonfinite observations')
    return wide.sub(actual, axis=0)


def stats(errors, context, output):
    for basis in ['raw_midpoint', 'integer_interval']:
        e = errors if basis == 'raw_midpoint' else pd.DataFrame(residual(errors), index=errors.index, columns=errors.columns)
        for model in e:
            a = e[model].to_numpy()
            output.append(dict(**context, scoring=basis, model=model, n=len(a),
                               n_year_clusters=len(set(t[:4] for t in e.index)),
                               rmse_musd=float(np.sqrt(np.mean(a*a))), mae_musd=float(np.mean(abs(a))),
                               signed_distance_bias_musd=float(np.mean(a)),
                               within_rounding_interval=int((abs(errors[model]) <= .5).sum()),
                               targets='|'.join(e.index)))


def compare(errors, candidate, reference, draw, context, pairs, deletions):
    years = np.array([int(t[:4]) for t in errors.index]); unique = np.unique(years)
    counts = np.stack([(draw == i).sum(axis=1) for i in range(len(unique))], axis=1)
    for basis in ['raw_midpoint', 'integer_interval']:
        ec = errors[candidate].to_numpy(); eb = errors[reference].to_numpy()
        if basis == 'integer_interval':
            ec, eb = residual(ec), residual(eb)
        sc = np.array([sum(ec[years == y]**2) for y in unique])
        sb = np.array([sum(eb[years == y]**2) for y in unique])
        boot = ratio(counts @ sc, counts @ sb)
        drs = []
        for unit, values in [('year', years), ('quarter', np.array(errors.index))]:
            for value in np.unique(values):
                keep = values != value
                if not keep.any():
                    continue
                dr = float(ratio(sum(ec[keep]**2), sum(eb[keep]**2))); drs.append(dr)
                deletions.append(dict(**context, scoring=basis, candidate=candidate, reference=reference,
                                      deleted_unit=unit, deleted_value=str(value), n=int(keep.sum()), rmse_ratio=dr))
        pairs.append(dict(**context, scoring=basis, candidate=candidate, reference=reference, n=len(ec),
                          n_year_clusters=len(unique), n_bootstrap=len(draw),
                          candidate_rmse_musd=float(np.sqrt(np.mean(ec**2))),
                          reference_rmse_musd=float(np.sqrt(np.mean(eb**2))),
                          rmse_ratio=float(ratio(sum(ec**2), sum(eb**2))),
                          ratio_p05=float(np.quantile(boot,.05)), ratio_p95=float(np.quantile(boot,.95)),
                          worst_deletion_ratio=max(drs), any_deletion_reversal=max(drs)>=1,
                          targets='|'.join(errors.index)))


def run_horizon(frame, scores, pairs, deletions):
    frame = frame[~frame.is_live & frame.model.isin(PRODUCTION)]
    for h in [2,3,4]:
        for window, lower in WINDOWS.items():
            d = frame[(frame.horizon_quarters == h) & (frame.target >= lower)]
            for scope, candidates in [('common4', ['joint','fixed']), ('candidate_specific', ['joint','fixed'])]:
                for candidate in candidates:
                    models = PRODUCTION if scope == 'common4' else [candidate,'guide_growth','revenue_growth']
                    e = sample(d[d.model.isin(models)], models)
                    context = dict(scope=scope,horizon_quarters=h,window=window,candidate_sample=candidate)
                    stats(e,context,scores)
                    ny = len(set(t[:4] for t in e.index))
                    draw = np.random.default_rng(SEED+h).integers(0,ny,size=(2000,ny))
                    references = ['fixed','guide_growth','revenue_growth'] if scope == 'common4' else ['guide_growth','revenue_growth']
                    for reference in references:
                        if reference != candidate:
                            compare(e,candidate,reference,draw,context,pairs,deletions)


def run_flight(frame, scores, pairs, deletions):
    models = ['joint_flight','joint_noflight','fixed_flight','fixed_noflight','guide_growth','revenue_growth']
    rng = np.random.default_rng(SEED)
    for window,lower in WINDOWS.items():
        e = sample(frame[frame.target >= lower],models)
        ny = len(set(t[:4] for t in e.index))
        context = dict(scope='calendar_flight',horizon_quarters=2,window=window,candidate_sample='all_six')
        stats(e,context,scores)
        for candidate in ['joint_flight','fixed_flight']:
            for reference in [candidate.replace('flight','noflight'),'guide_growth','revenue_growth']:
                draw = rng.integers(0,ny,size=(2000,ny))
                compare(e,candidate,reference,draw,context,pairs,deletions)


def gates(pairs):
    records=[]
    for (scope,h,candidate,basis),d in pairs.groupby(['scope','horizon_quarters','candidate','scoring'],sort=True):
        if scope == 'calendar_flight':
            for window,x in d.groupby('window'):
                own=x[x.reference == candidate.replace('flight','noflight')].iloc[0]
                direct=x[x.reference == 'guide_growth'].iloc[0]
                coverage=bool(own.n>=8); magnitude=bool(own.rmse_ratio<=.9)
                deletion=bool(not own.any_deletion_reversal); direct_pass=bool(direct.rmse_ratio<1)
                records.append(dict(scope=scope,horizon_quarters=h,candidate=candidate,scoring=basis,window=window,
                                    coverage_pass=coverage,magnitude_pass=magnitude,deletion_pass=deletion,
                                    paired_guidegrowth_interval_pass=None,direct_guidegrowth_pass=direct_pass,
                                    promotion_pass=coverage and magnitude and deletion and direct_pass))
        else:
            x=d[d.reference.isin(['guide_growth','revenue_growth'])]
            coverage=bool(len(x)==4 and (x.n>=8).all())
            magnitude=bool(coverage and (x.rmse_ratio<=.9).all())
            deletion=bool(len(x)>0 and (~x.any_deletion_reversal).all())
            guide=x[x.reference=='guide_growth']
            ci=bool(len(guide)==2 and (guide.ratio_p95<1).all())
            records.append(dict(scope=scope,horizon_quarters=h,candidate=candidate,scoring=basis,window='both',
                                coverage_pass=coverage,magnitude_pass=magnitude,deletion_pass=deletion,
                                paired_guidegrowth_interval_pass=ci,direct_guidegrowth_pass=None,
                                promotion_pass=coverage and magnitude and deletion and ci))
    return pd.DataFrame(records)


def verify_raw(pairs,gate,source):
    checks=0
    mapping={'common4':source['common_pairs'],'candidate_specific':source['eligible_pairs'],'calendar_flight':source['flight_pairs']}
    for scope,path in mapping.items():
        old=pd.read_csv(path).rename(columns={'baseline':'reference'})
        if 'object' in old:
            old=old[(old.object=='guide') & old.candidate.isin(['joint','fixed'])]
        new=pairs[(pairs.scope==scope)&(pairs.scoring=='raw_midpoint')]
        keys=['window','candidate','reference'] + ([] if scope=='calendar_flight' else ['horizon_quarters'])
        joined=new.merge(old,on=keys,suffixes=('_new','_old'),validate='one_to_one')
        assert len(joined)==len(old)==len(new)
        for col in ['n','n_year_clusters','rmse_ratio','ratio_p05','ratio_p95']:
            np.testing.assert_allclose(joined[col+'_new'],joined[col+'_old'],rtol=1e-12,atol=1e-12)
            checks+=len(joined)
    for scope,key in [('common4','common_gates'),('candidate_specific','eligible_gates'),('calendar_flight','flight_gates')]:
        old=pd.read_csv(source[key]).rename(columns={'model':'candidate','pass_window':'promotion_pass'})
        new=gate[(gate.scope==scope)&(gate.scoring=='raw_midpoint')]
        keys=['window','candidate'] if scope=='calendar_flight' else ['horizon_quarters','candidate']
        joined=new.merge(old,on=keys,suffixes=('_new','_old'),validate='one_to_one')
        assert len(joined)==len(old)==len(new)
        cols=['promotion_pass'] if scope=='calendar_flight' else ['coverage_pass','magnitude_pass','deletion_pass','paired_guidegrowth_interval_pass','promotion_pass']
        for col in cols:
            assert joined[col+'_new'].eq(joined[col+'_old']).all(), (scope,col)
            checks+=len(joined)
    return checks


def self_tests():
    np.testing.assert_allclose(residual([-2,-.5,-.3,0,.3,.5,2]),[-1.5,0,0,0,0,0,1.5])
    np.testing.assert_allclose(residual([-2,.1,1],0),[-2,.1,1])
    np.testing.assert_allclose(residual([5,-5]),-residual([-5,5]))
    for args in [([1],-1),([np.nan],.5),([1],np.inf)]:
        try: residual(*args)
        except ValueError: pass
        else: raise AssertionError('Invalid loss input accepted')
    try: ratio(1,0)
    except ValueError: pass
    else: raise AssertionError('Undefined ratio treated as valid')
    np.testing.assert_allclose(ratio(4,16),.5)
    return 8


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    out=args.out.resolve()
    if out.exists(): raise FileExistsError('A new output folder is required')
    h=DATA/'horizon_v1'; f=DATA/'calendar_flights_v1/results_v1'
    source={'horizon_predictions':h/'results_v2/predictions.csv','flight_predictions':f/'predictions.csv',
            'common_pairs':h/'results_v2/paired_comparisons.csv','common_gates':h/'results_v2/promotion_gates.csv',
            'eligible_pairs':h/'eligibility_audit_v1/comparisons.csv','eligible_gates':h/'eligibility_audit_v1/promotion_gates.csv',
            'flight_pairs':f/'paired_comparisons.csv','flight_gates':f/'remedy_gates.csv',
            'harness_v1':ROOT/'analysis/src/forecast_methods/harness/score.py',
            'harness_v1_1':ROOT/'analysis/src/forecast_methods/harness_v1_1/score.py',
            'prereg':NOTES/'GD_GUIDE_INTERVAL_PREREG_v1.md'}
    hashes={k:sha(p) for k,p in source.items()};tests=self_tests()
    scores=[];pairs=[];deletions=[]
    run_horizon(pd.read_csv(source['horizon_predictions']),scores,pairs,deletions)
    run_flight(pd.read_csv(source['flight_predictions']),scores,pairs,deletions)
    pairs=pd.DataFrame(pairs);gate=gates(pairs)
    raw_checks=verify_raw(pairs,gate,source)
    keys=['scope','horizon_quarters','candidate','window']
    raw=gate[gate.scoring=='raw_midpoint'].drop(columns='scoring')
    interval=gate[gate.scoring=='integer_interval'].drop(columns='scoring')
    change=raw.merge(interval,on=keys,suffixes=('_raw','_interval'),validate='one_to_one')
    flags=['coverage_pass','magnitude_pass','deletion_pass','paired_guidegrowth_interval_pass','direct_guidegrowth_pass','promotion_pass']
    for col in flags:
        change[col+'_changed']=change[col+'_raw'].fillna('NA').ne(change[col+'_interval'].fillna('NA'))
    assert hashes=={k:sha(p) for k,p in source.items()},'Immutable input changed'
    out.mkdir(parents=True)
    outputs={'scores':pd.DataFrame(scores),'comparisons':pairs,'deletions':pd.DataFrame(deletions),
             'gates':gate,'gate_changes':change}
    for name,table in outputs.items(): table.to_csv(out/(name+'.csv'),index=False)
    receipt={'self_tests_passed':tests,'raw_replication_numeric_and_gate_checks':raw_checks,'sources_unchanged':True,
             'new_parameter_count':0,'bootstrap_draws_per_pair':2000,'interval_halfwidth_musd':.5,
             'changed_promotion_outcomes':int(change.promotion_pass_changed.sum()),
             'changed_gate_components':int(change[[x+'_changed' for x in flags]].to_numpy().sum()),
             'live_forecasts_changed':False,'harness_changed':False,'registered_scores_changed':False,
             'limitations':['Rounding sensitivity only; no predictive interval','Few independent years; W1/W2 overlap',
                            'Scoring accepted reused-history results; no new holdout','Frozen harness still uses raw midpoint loss']}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    manifest={'code_sha256':sha(__file__),'inputs':{k:{'path':str(p.relative_to(ROOT)),'sha256':hashes[k]} for k,p in source.items()},
              'outputs':{p.name:sha(p) for p in sorted(out.iterdir())}}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(receipt,indent=2));print(change[keys+['promotion_pass_raw','promotion_pass_interval']].to_string(index=False))


if __name__=='__main__': main()
