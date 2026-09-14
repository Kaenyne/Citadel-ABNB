"""Read-only F power audit; never imports or reruns the package or scorers."""
from pathlib import Path
import csv
import json
import math
from statistics import NormalDist
from scipy.stats import binom
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'data/processed/forecast_methods/refute_f_power_v1'
BASE = ROOT / 'data/processed/forecast_methods/rnpl_v2'

def read(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))

def wilson(k, n):
    z = NormalDist().inv_cdf(0.975)
    p = k / n
    den = 1 + z*z/n
    mid = (p + z*z/(2*n))/den
    half = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/den
    return [100*max(0,mid-half), 100*min(1,mid+half)]

def detect(n):
    null, alpha, power = 0.05, 0.05, 0.80
    cutoff = next(k for k in range(1,n+1) if binom.sf(k-1,n,null) <= alpha)
    p = brentq(lambda p: binom.sf(cutoff-1,n,p)-power, null, 1)
    return {'n':n, 'null_p':null, 'alpha':alpha, 'target_power':power,
            'rejection_count_at_least':cutoff, 'actual_size':float(binom.sf(cutoff-1,n,null)),
            'minimum_detectable_p':p, 'minimum_increase_pp':100*(p-null),
            'power_at_9pct_p':float(binom.sf(cutoff-1,n,0.09))}

def main():
    stock = read(BASE/'paid_backlog.csv')
    endpoints = []
    for quarter in ('2025Q4','2026Q1','2026Q2'):
        row = next(r for r in stock if r['quarter']==quarter)
        # Recompute the same-season norm directly from frozen stock rows.
        norm_rows = [r for r in stock if '2022Q1' <= r['quarter'] <= '2025Q2'
                     and r['season']==row['season']]
        norm = sum(1-float(r['unearned_fees_musd'])/float(r['kernel_fee_stock_musd'])
                   for r in norm_rows)/len(norm_rows)
        excess = 100*(1-float(row['unearned_fees_musd'])/float(row['kernel_fee_stock_musd'])-norm)
        assert abs(excess-float(row['excess_unpaid_pp'])) < 1e-9
        endpoints.append({'quarter':quarter,'n_recent':1,'n_norm':len(norm_rows),
                          'excess_unpaid_pp_recomputed':excess})

    d1 = read(ROOT/'data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv')
    axes = ('share_path','adr_ratio','delta_scenario','lead_time','lead_uplift','rebook_offset')
    counts = {a:len(set(r[a] for r in d1)) for a in axes}
    assert math.prod(counts.values())==len(d1)==2025
    central = [r for r in d1 if all(r[k]==v for k,v in dict(share_path='share_central',
               adr_ratio='adr_plus25',delta_scenario='delta_4pp',lead_time='lead_2.2',
               lead_uplift='uplift_7',rebook_offset='0.25').items())]
    assert len(central)==1
    central=central[0]
    live=read(BASE/'live_scenarios.csv')
    team=next(r for r in live if r['nights_variant']=='team' and r['quarter']=='2026Q4')
    nights_share=float(central['rnpl_nights_share_4q26_pct'])/100
    gbv_share=1.25*nights_share/(1-nights_share+1.25*nights_share)
    loss=gbv_share*float(central['delta_pp_applied'])/100
    revenue=float(team['pure_kernel_revenue_musd'])*(1-loss)
    assert abs(revenue-float(team['registered_revenue_musd']))<1e-8

    grid=read(BASE/'leakage_grid.csv')
    registry=read(ROOT/'data/processed/forecast_methods/registry/rnpl-v2__revenue_next_q.csv')
    alarms=read(BASE/'lambda_chronological_alarms.csv')
    alarm_quarters=[r['quarter'] for r in alarms]
    assert len(set(alarm_quarters))==len(alarms)==6
    assert all(q >= '2024Q1' for q in alarm_quarters)
    sample_counts=[]
    for n,k,label in ((2,1,'pre-RNPL alarms W1 and W2 same cells'),
                      (6,1,'all chronological alarms W1 and W2 same cells'),
                      (3,0,'fixed Q3 rule W1 retrospective'),
                      (2,0,'fixed Q3 rule W2 subset')):
        sample_counts.append({'label':label,'n':n,'k':k,'rate_pct':100*k/n,
                              'wilson_95_pct':wilson(k,n)})
    ranges={}
    for q in ('2026Q3','2026Q4'):
        vals=[float(r['L']) for r in grid if r['quarter']==q]
        ranges[q]={'rows':len(vals),'unique_L_rounded_12dp':len(set(round(x,12) for x in vals)),
                   'min_L':min(vals),'max_L':max(vals)}
    q4low=float(team['pure_kernel_revenue_musd'])*(1-ranges['2026Q4']['max_L'])
    summary={'endpoints':endpoints,'endpoint_increase_pp':endpoints[-1]['excess_unpaid_pp_recomputed']-endpoints[0]['excess_unpaid_pp_recomputed'],
             'D1_grid_n':len(d1),'D1_axis_counts':counts,'grid_ranges':ranges,
             'central_q4':{'raw_nights_share':nights_share,'derived_gbv_share':gbv_share,
                           'delta_pp':float(central['delta_pp_applied']), 'L':loss,
                           'pure_kernel_musd':float(team['pure_kernel_revenue_musd']),
                           'stress_musd':revenue,'loss_musd':float(team['pure_kernel_revenue_musd'])-revenue,
                           'all_D1_grid_revenue_min_musd':q4low,
                           'all_D1_grid_revenue_max_musd':float(team['pure_kernel_revenue_musd'])},
             'registry':{'n_rows':len(registry),'windows':sorted(set(r['window'] for r in registry)),
                         'replay_labels':sorted(set(r['prior_basis'] for r in registry)),
                         'n_spec_quarter':len(set((r['spec_id'],r['quarter']) for r in registry)),
                         'historical_W1':sum(r['window']=='W1' for r in registry),
                         'historical_W2':sum(r['window']=='W2' for r in registry),
                         'n_unique_quarter_point':len(set((r['quarter'],float(r['point'])) for r in registry))},
             'alarm_quarters':alarm_quarters,'alarm_intervals':sample_counts,
             'MDE_design':[detect(n) for n in (2,3,6)],
             'limits':'No sampling model for excess share or stress; alarm MDE is an illustrative independent Bernoulli design.'}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'audit.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
