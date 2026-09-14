"""Independent audit of changed v2 definitions and deterministic propagation."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def read(p):
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--revenue-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError(a.output)
    checks, max_delta = 0, 0.

    def close(actual, expected, label, tol=1e-8):
        nonlocal checks, max_delta
        x, y = float(actual), float(expected)
        if not math.isfinite(x) or not math.isfinite(y) or abs(x-y) > tol:
            raise AssertionError(f'{label}: {x} versus {y}')
        checks += 1
        max_delta = max(max_delta, abs(x-y))

    manifest = json.loads((a.revenue_dir/'SHA256SUMS.json').read_text())
    for name, h in manifest.items():
        if hashlib.sha256((a.revenue_dir/name).read_bytes()).hexdigest() != h:
            raise AssertionError('Output hash mismatch: '+name)
    sources = read(a.revenue_dir/'source_ledger.csv')
    for s in sources:
        if hashlib.sha256((ROOT/s['path']).read_bytes()).hexdigest() != s['sha256']:
            raise AssertionError('Source changed: '+s['path'])
    current = read(a.revenue_dir/'forecast.csv')
    old = {(r['scenario'], r['quarter']):r for r in read(ROOT/'data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1/forecast.csv')}
    if len(current) != 15 or len(old) != 15:
        raise AssertionError('Baseline inventory differs')
    ref = {r['quarter']:r for r in current if r['scenario']=='review_with_k'}
    for r in current:
        for k in ['revenue_musd','guide_musd','lambda_pct','kernel_base_musd','cushion_decimal']:
            close(r[k],old[r['scenario'],r['quarter']][k],'Preserved baseline '+k)
    for r in read(a.revenue_dir/'expectations_comparison.csv')+read(a.revenue_dir/'joint_expectations.csv'):
        R,G,S,c,sc = [float(r[k]) for k in ['own_revenue_musd','own_guide_mid_musd','revenue_consensus_musd','cushion_decimal','hypothetical_street_cushion_decimal']]
        for k, expected in [('revenue_gap_musd',R-S),('revenue_gap_pct',100*(R/S-1)),
                            ('guide_minus_revenue_diagnostic_musd',G-S),('hypothetical_street_guide_musd',S/(1+sc)),
                            ('hypothetical_like_basis_guide_gap_musd',G-S/(1+sc))]:
            close(r[k],expected,'Expectations '+k)
        close(G,R/(1+c),'Own guide identity')
        if r['guide_expectations_status'] != 'explicit_dated_guide_expectations_unavailable' or r['cross_object_status'] != 'different_objects_not_guide_surprise':
            raise AssertionError('Evidence labels confuse guide and revenue expectations')
    joint = read(a.revenue_dir/'joint_scenarios.csv')
    if len(joint) != 9:
        raise AssertionError('Expected three joint cases across three quarters')
    for r in joint:
        close(r['kernel_weight'],2/3,'Fixed production kernel')
        close(r['net_revenue_factor'],1,'No overlapping generic net overlay')
        R = float(r['lambda_pct'])/100*(2/3*float(r['lag1_gbv_musd'])+1/3*float(r['lag2_gbv_musd']))
        close(r['revenue_musd'],R,'Joint revenue')
        close(r['guide_musd'],R/(1+float(r['cushion_decimal'])),'Joint guide')
        close(r['delta_revenue_vs_reference_musd'],R-float(ref[r['quarter']]['revenue_musd']),'Joint delta')
    b = read(a.revenue_dir/'joint_scenario_bridge.csv')
    for scenario in {r['scenario'] for r in b}:
        for q in ref:
            steps = sorted([r for r in b if r['scenario']==scenario and r['quarter']==q],key=lambda r:int(r['step']))
            for kind in ['revenue','guide']:
                close(sum(float(s['delta_'+kind+'_musd']) for s in steps),float(steps[-1][kind+'_musd'])-float(steps[0][kind+'_musd']),'Attribution telescopes')
    source_dir = ROOT/'data/processed/forecast_methods/lane4_sources_v2/snapshot_v1'
    source_draws = {int(r['draw']):r for r in read(source_dir/'bundle/payload/conversion/parameter_bootstrap.csv')}
    draw_rows = read(a.revenue_dir/'descriptive_joint_draws.csv')
    if len(draw_rows)!=3000:
        raise AssertionError('Missing descriptive draw-quarter rows')
    for r in draw_rows:
        d = source_draws[int(r['source_draw'])]
        close(r['kernel_weight'],d['w'],'Accepted weight unchanged')
        for q in range(1,5):
            close(r[f'lambda_Q{q}_pct'],d[f'lambda_Q{q}_pct'],'Joint tuple remains intact')
        w=float(d['w'])
        R=float(d[f"lambda_Q{r['quarter'][-1]}_pct"])/100*(w*float(r['lag1_gbv_musd'])+(1-w)*float(r['lag2_gbv_musd']))
        close(r['revenue_musd'],R,'Descriptive tuple propagation')
        close(r['guide_musd'],R/(1+float(ref[r['quarter']]['cushion_decimal'])),'Descriptive fixed-cushion context')
    for r in read(a.revenue_dir/'net_revenue_sensitivity.csv'):
        close(r['revenue_musd'],float(ref[r['quarter']]['revenue_musd'])*float(r['net_revenue_factor']),'Isolated net sensitivity')
        if 'not_estimated_FX' not in r['evidence_status']:
            raise AssertionError('Net sensitivity relabelled measured FX')
    fx = json.loads((a.revenue_dir/'accounting_eligibility.json').read_text())
    if fx['central_fx_financial_eligibility'] or fx['estimated_incremental_fx_musd'] is not None:
        raise AssertionError('Unidentified financial FX presented as eligible')
    result = dict(verdict='PASS',arithmetic_checks=checks,max_abs_difference=max_delta,
                  output_hashes_verified=len(manifest),source_hashes_verified=len(sources),
                  preserved_baseline_rows=15,joint_scenario_rows=len(joint),
                  descriptive_joint_rows=len(draw_rows),new_fits=0,
                  scope='Audit of changed integration arithmetic and evidence labels; no L3 re-estimation or repeated historical test',
                  manifest_sha256=hashlib.sha256((a.revenue_dir/'SHA256SUMS.json').read_bytes()).hexdigest())
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
