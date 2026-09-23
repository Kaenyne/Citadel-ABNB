"""Independent stdlib review of C's accepted-evidence arithmetic; no author imports."""
import argparse
import csv
import hashlib
import json
import math
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / 'data/processed/forecast_methods/quant_thesis_validation_v1'
CONV = ROOT / 'data/processed/forecast_methods/l3_bundle_v1/payload/conversion'
REVIEWED = BASE / 'uncertainty_audit_v1/results_v2'


def rows(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def covariance(a, b):
    ma, mb = st.mean(a), st.mean(b)
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/(len(a)-1)


def main(out):
    if not out.resolve().is_relative_to((BASE/'final_contract_review_v1').resolve()):
        raise ValueError('Output must stay in exclusive review directory')
    if out.exists():
        raise FileExistsError(out)
    checks = []
    bound = {}
    def read(p):
        bound[str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
        return rows(p)
    def check(label, actual, expected):
        delta = abs(float(actual)-float(expected))
        checks.append(dict(check=label, actual=actual, expected=expected, delta=delta, passes=delta < 2e-7))
    panel = read(ROOT/'data/processed/overnight/02_kpi_panel_quarterly.csv')
    panel = sorted(panel, key=lambda r: r['quarter'][2:]+r['quarter'][0])
    hist = []
    for i,r in enumerate(panel[2:], 2):
        g1, g2 = float(panel[i-1]['gbv_musd']), float(panel[i-2]['gbv_musd'])
        hist.append(dict(quarter='20'+r['quarter'][2:]+'Q'+r['quarter'][0],
            season=int(r['quarter'][0]), g1=g1, g2=g2, base_musd=(2*g1+g2)/3,
            a_pp=200*g1/(2*g1+g2), lambda_pct=300*float(r['revenue_musd'])/(2*g1+g2)))
    authored = read(REVIEWED/'historical_arithmetic.csv')
    lookup = {r['quarter']:r for r in authored}
    for r in hist:
        for col in ('g1','g2','base_musd','a_pp','lambda_pct'):
            check(r['quarter']+':'+col, r[col], lookup[r['quarter']][col])
    for r in read(REVIEWED/'arithmetic_window_summary.csv'):
        start = dict(ALL='2021',EX2021='2022',W1='2023',W2='2024')[r['window']]
        sub = [h for h in hist if h['quarter'][:4] >= start]
        vals = [h[r['variable']] for h in sub]
        groups = [[h[r['variable']] for h in sub if h['season']==s] for s in range(1,5)]
        within_ss = sum(sum((x-st.mean(v))**2 for x in v) for v in groups)
        total_ss = sum((x-st.mean(vals))**2 for x in vals)
        metrics = dict(n=len(vals),mean=st.mean(vals),variance=st.variance(vals),sd=st.stdev(vals),
            minimum=min(vals),maximum=max(vals),pooled_within_season_sd=math.sqrt(within_ss/(len(vals)-4)),
            season_explained_ss_fraction=1-within_ss/total_ss)
        for col,v in metrics.items():check(r['window']+':'+r['variable']+':'+col,v,r[col])
    paths = read(CONV/'chronological_paths.csv')
    for r in read(REVIEWED/'accepted_score_reproduction.csv'):
        sub=[p for p in paths if p['quarter'] >= ('2023Q1' if r['window']=='W1' else '2024Q1') and p['model']==r['model']]
        err=[float(p['point'])-float(p['actual']) for p in sub]
        for col,v in dict(n=len(err),rmse_musd=math.sqrt(st.mean([e*e for e in err])),
                          mae_musd=st.mean([abs(e) for e in err]),bias_musd=st.mean(err)).items():
            check(r['window']+':'+r['model']+':'+col,v,r[col])
    for r in read(REVIEWED/'accepted_interval_reproduction.csv'):
        sub=[p for p in paths if p['quarter'] >= ('2023Q1' if r['window']=='W1' else '2024Q1') and p['model']==r['model'] and p['q10']]
        metrics=dict(n_eligible=len(sub),n_covered=sum(float(p['q10'])<=float(p['actual'])<=float(p['q90']) for p in sub),
            mean_full_width_pct=st.mean([100*(float(p['q90'])-float(p['q10']))/float(p['point']) for p in sub]))
        for col,v in metrics.items():check(r['window']+':'+r['model']+':'+col,v,r[col])
    draws=read(CONV/'parameter_bootstrap.csv')
    w=[float(d['w']) for d in draws]
    for r in read(REVIEWED/'joint_parameter_compensation.csv'):
        s=int(r['season']); sub=[h for h in hist if h['season']==s]
        ratio=st.mean([h['g1']/h['g2'] for h in sub])
        lam=[float(d[f'lambda_Q{s}_pct'])/100 for d in draws]
        effective=[l*(1+x*(ratio-1)) for l,x in zip(lam,w)]
        tl=[(1+st.mean(w)*(ratio-1))*(l-st.mean(lam)) for l in lam]
        tw=[st.mean(lam)*(ratio-1)*(x-st.mean(w)) for x in w]
        interaction=[(ratio-1)*(x-st.mean(w))*(l-st.mean(lam)) for x,l in zip(w,lam)]
        metrics=dict(n_historical_ratio=len(sub),r_season_mean=ratio,draws=len(w),
            corr_w_lambda=covariance(w,lam)/(st.stdev(w)*st.stdev(lam)),lambda_sd_pct=100*st.stdev(lam),
            effective_slope_sd_pct=100*st.stdev(effective),marginal_linear_variance=st.variance(tl)+st.variance(tw),
            twice_covariance=2*covariance(tl,tw),joint_linear_variance=st.variance([a+b for a,b in zip(tl,tw)]),
            exact_joint_variance=st.variance(effective),interaction_sd=st.stdev(interaction))
        for col,v in metrics.items():check(f'Q{s}:'+col,v,r[col])
    receipt=dict(reviewer='/root/test_designer',author='/root/uncertainty_auditor',
        status='PASS_INDEPENDENT_ACCEPTED_ARITHMETIC_REVIEW',numeric_checks=len(checks),
        max_difference=max(c['delta'] for c in checks),tolerance=2e-7,failures=[c for c in checks if not c['passes']],
        new_models=0,new_resamples=0,empirical_regimes_added=0,author_functions_imported=False,
        own_economics_reviewed=False,bound_inputs_and_reviewed_outputs_sha256=bound)
    out.mkdir(parents=True)
    with (out/'checks.csv').open('x',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(checks[0]));writer.writeheader();writer.writerows(checks)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='bound_inputs_and_reviewed_outputs_sha256'},indent=2))
    if receipt['failures']:raise AssertionError('Independent arithmetic review failed')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    main(parser.parse_args().out)
