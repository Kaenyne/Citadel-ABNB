"""Exact, historical-snapshot same-basis expectations and break-even arithmetic."""
from pathlib import Path
from decimal import Decimal as D
import argparse
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
PKG = ROOT / 'data/processed/forecast_methods/quant_thesis_validation_v1'
SRC = PKG / 'evidence_v3/l4/data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1'

def rows(name):
    with (SRC/name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def single(data, **keys):
    selected = [x for x in data if all(x[k] == v for k,v in keys.items())]
    if len(selected) != 1:
        raise ValueError(f'Expected unique row: {keys}; found {len(selected)}')
    return selected[0]

def write_csv(path, data):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)

def build(out):
    out = Path(out).resolve()
    if out.exists():
        raise FileExistsError(out)
    if not out.is_relative_to(ROOT):
        raise ValueError('Output must be within this worktree')
    f = single(rows('forecast.csv'), quarter='2026Q4', scenario='review_with_k')
    a = single(rows('cohort_weights.csv'), target_quarter='2026Q4', lag='1', scenario='review_with_k')
    b = single(rows('cohort_weights.csv'), target_quarter='2026Q4', lag='2', scenario='review_with_k')
    g1, g2, lam, c = D(a['gbv_musd']), D(b['gbv_musd']), D(f['lambda_pct'])/100, D(f['cushion_decimal'])
    w = D(2)/3
    base = w*g1+(1-w)*g2
    revenue = lam*base
    guide = revenue/(1+c)
    if abs(revenue-D(f['revenue_musd'])) > D('0.000001') or abs(guide-D(f['guide_musd'])) > D('0.000001'):
        raise AssertionError('Committed L4 identity does not reconcile')
    panels = rows('consensus_selection.csv')
    cushion = {x['statistic']: D(x['cushion_decimal']) for x in rows('cushion_inputs.csv')}
    bridge, thresholds, policy = [], [], []
    for p in panels:
        street = D(p['value'])
        if p['metric'] != 'revenue' or p['unit'] != 'musd' or street <= 0:
            raise ValueError('Consensus basis invalid')
        header = dict(panel_family=p['panel_family'], vendor=p['vendor'], observed_timestamp=(p['observed_timestamp'] if p['panel_family']=='LSEG family' else p['observed_timestamp'][:10]), observation_precision=('minute; raw capture15:20:58Z' if p['panel_family']=='LSEG family' else 'date only; exact time unavailable'),
                      quarter='2026Q4', source_url=p['url'], n=1, empirical_validation_n=0)
        bridge.append(dict(**header, own_revenue_musd=revenue, street_revenue_musd=street,
                           revenue_gap_musd=revenue-street, revenue_gap_pct=100*(revenue/street-1),
                           own_cushion_pct=100*c, own_guide_musd=guide,
                           different_object_guide_minus_revenue_musd=guide-street,
                           hypothetical_street_guide_musd=street/(1+c),
                           hypothetical_common_cushion_guide_gap_musd=(revenue-street)/(1+c),
                           observed_guide_consensus_musd='', evidence_status='conditional historical snapshot'))
        gstar = (street/lam-(1-w)*g2)/w
        thresholds.append(dict(**header, g1_reference_musd=g1, g1_break_even_musd=gstar,
            g1_break_even_change_pct=100*(gstar/g1-1), lambda_reference_pct=100*lam,
            lambda_break_even_pct=100*street/base, lambda_break_even_change_pp=100*(street/base-lam),
            residual_revenue_factor_break_even=street/revenue,
            residual_revenue_change_pct=100*(street/revenue-1),
            own_cushion_break_even_pct=100*(revenue*(1+c)/street-1),
            own_cushion_change_from_reference_pp=100*(revenue*(1+c)/street-1-c),
            interpretation='One input at a time; conditional thresholds, not probability estimates'))
        for name, cs in [('zero',D(0)),('median',cushion['median']),('mean',cushion['mean']),('legacy_q4',D('.0388'))]:
            policy.append(dict(**header, imposed_street_cushion=name, street_cushion_pct=100*cs,
                hypothetical_street_guide_musd=street/(1+cs), own_guide_musd=guide,
                hypothetical_gap_musd=guide-street/(1+cs),
                own_cushion_at_equality_pct=100*(revenue*(1+cs)/street-1),
                status='Analytical construction; explicit guide expectations unavailable'))
    lstreet = D(single(panels, panel_family='LSEG family')['value'])
    stress = []
    for gpct in [-5,-3,-1,0,1,3,5]:
        for lpp in ['-.30','-.10','0','.10','.30']:
            gs, ls = g1*(1+D(gpct)/100), lam+D(lpp)/100
            rs = ls*(w*gs+(1-w)*g2)
            stress.append(dict(g1_change_pct=gpct, lambda_change_pp=lpp, g1_musd=gs, lambda_pct=100*ls,
                revenue_musd=rs, guide_musd=rs/(1+c), revenue_gap_to_lseg_musd=rs-lstreet,
                hypothetical_guide_gap_to_lseg_musd=(rs-lstreet)/(1+c),
                probability='', meaning='joint deterministic stress; no calibration'))
    out.mkdir(parents=True)
    for name, data in [('same_basis.csv',bridge),('break_even.csv',thresholds),('cushion_policy.csv',policy),('stress_surface.csv',stress)]:
        write_csv(out/name,data)
    manifest = {x:hashlib.sha256((SRC/x).read_bytes()).hexdigest() for x in
                ['forecast.csv','cohort_weights.csv','consensus_selection.csv','cushion_inputs.csv']}
    summary = dict(status='research arithmetic complete; no investment adoption', n_reference=1, n_new_parameters=0,
        revenue_musd=str(revenue),guide_musd=str(guide),g1_musd=str(g1),g2_musd=str(g2),
        lambda_pct=str(100*lam),cushion_pct=str(100*c), source_commit='29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70',
        source_sha256=manifest, live_market_refresh=False, scenarios=35,
        protocol_sha256=hashlib.sha256((ROOT/'docs/revenue-forecast-strategy/quant_thesis_validation_v1/CHAIN_PROTOCOL_v1.md').read_bytes()).hexdigest())
    (out/'receipt.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=PKG/'expectations_v2')
    build(parser.parse_args().out)

