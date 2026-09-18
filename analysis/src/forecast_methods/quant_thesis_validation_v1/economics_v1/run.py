"""Independent L4 equation audit and small conditional economic bridge; stdlib only."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = Path(__file__).resolve().parent
BASE = ROOT / 'data/processed/forecast_methods/quant_thesis_validation_v1'
EVIDENCE = BASE / 'evidence_v3'
L4 = EVIDENCE / 'l4'
MODEL = L4 / 'data/processed/forecast_methods/lane4_model_v1/snapshot_v4'
TOL = 1e-6
CASE = 'review_with_k'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_rows(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def write_rows(path, rows):
    if not rows:
        raise ValueError('Refuse empty output table')
    with Path(path).open('x', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def dump(path, obj):
    with Path(path).open('x', encoding='utf-8') as handle:
        json.dump(obj, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write('\n')


def finite(value, name):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f'Nonfinite {name}')
    return result


def positive(value, name):
    result = finite(value, name)
    if result <= 0:
        raise ValueError(f'Nonpositive {name}')
    return result


def load_inputs():
    paths = [MODEL / 'annual.csv', MODEL / 'valuation.csv', MODEL / 'model_input.json',
             BASE / 'expectations_v1/same_basis.csv',
             ROOT / 'docs/revenue-forecast-strategy/quant_thesis_validation_v1/CHAIN_PROTOCOL_v1.md',
             ROOT / 'docs/revenue-forecast-strategy/quant_thesis_validation_v1/economics_v1/ASSUMPTIONS_v1.md']
    manifest = json.loads((EVIDENCE / 'external_manifest.json').read_text(encoding='utf-8-sig'))
    expected = {str((ROOT / r['frozen_path']).resolve()): r['sha256'] for r in manifest}
    identities = []
    for path in paths:
        digest = sha(path)
        key = str(path.resolve())
        if key in expected and digest != expected[key]:
            raise ValueError(f'Committed evidence hash mismatch: {path}')
        identities.append({'path': str(path.relative_to(ROOT)), 'sha256': digest,
                           'verified_external_binding': key in expected})
    inp = json.loads(paths[2].read_text(encoding='utf-8-sig'))
    annual = []
    seen = set()
    for raw in read_rows(paths[0]):
        row = {k: (v if k == 'scenario' else finite(v, k)) for k, v in raw.items()}
        row['year'] = int(row['year'])
        key = (row['scenario'], row['year'])
        if key in seen:
            raise ValueError(f'Duplicate annual key {key}')
        seen.add(key)
        positive(row['shares'], 'shares')
        positive(row['price'], 'price')
        annual.append(row)
    expected_keys = {(name, year) for name in inp['case_names'] for year in (2026, 2027, 2028)}
    if seen != expected_keys:
        raise ValueError('Annual table coverage differs from committed seven-case three-year contract')
    comparison = [r for r in read_rows(paths[3]) if r['panel_family'] == 'LSEG family']
    if len(comparison) != 1:
        raise ValueError('Need one uniquely identified captured LSEG-family comparator')
    return inp, annual, read_rows(paths[1]), comparison[0], identities


def reconcile(inp, annual, valuations):
    checks = []
    g, h1 = inp['globals'], inp['h1']
    lookup = {(r['scenario'], r['year']): r for r in annual}
    quarters = {c['scenario']: c['quarters'] for c in inp['cases']}
    def check(r, name, calculated, observed, unit='USDm'):
        delta = calculated-observed
        checks.append(dict(scenario=r['scenario'], year=r['year'], equation=name, n=1,
                           unit=unit, calculated=calculated, observed=observed,
                           difference=delta, passes=abs(delta) <= TOL))
    for r in annual:
        year, scenario = r['year'], r['scenario']
        i = inp['inputs'][str(year)]
        previous = lookup.get((scenario, year-1))
        costs = sum(r[k] for k in ('cor', 'ops', 'pd', 'bpm', 'fop', 'ga', 'nb_cost', 'ai_cost'))
        check(r, 'cash_cost_sum', costs, r['cash_costs'])
        check(r, 'adjusted_ebitda_uncapped', r['revenue']-costs+r['addbacks'], r['adj_uncapped'])
        check(r, 'adjusted_ebitda_cap', min(r['adj_uncapped'], r['revenue']*g['margin_cap']), r['adj_ebitda'])
        check(r, 'total_addbacks', r['revenue']*i['addback_pct'], r['addbacks'])
        check(r, 'D_and_A_included_in_total_addbacks', r['revenue']*i['da_pct'], r['da'])
        check(r, 'SBC_growth', (previous['sbc'] if previous else inp['fy25']['sbc'])*(1+i['sbc_growth']), r['sbc'])
        check(r, 'operating_income', r['adj_ebitda']-r['sbc']-r['addbacks'], r['op_income'])
        check(r, 'pretax', r['op_income']+r['interest_income']-r['interest_expense'], r['pretax'])
        check(r, 'net_income', r['pretax']*(1-i['eff_tax_rate']), r['net_income'])
        check(r, 'cash_tax', r['revenue']*i['cash_tax_pct'], r['cash_taxes'])
        check(r, 'unearned_cash', r['revenue']*i['d_unearned_pct'], r['d_unearned'])
        check(r, 'capex', r['revenue']*i['capex_pct'], r['capex'])
        check(r, 'other_working_capital', r['revenue']*i['wc_resid_pct'], r['wc_resid'])
        fcf = r['adj_ebitda']+r['interest_income']-r['interest_expense']-r['cash_taxes']+r['d_unearned']+r['wc_resid']-r['capex']
        check(r, 'FCF', fcf, r['fcf'])
        check(r, 'SBC_adjusted_FCF', fcf-r['sbc'], r['sbc_adj_fcf'])
        check(r, 'withholding', r['sbc']*g['withholding_pct'], r['withholding'])
        check(r, 'opening_cash', previous['net_cash'] if previous else g['net_cash_2q26'], r['opening_cash'])
        check(r, 'opening_share_proxy', previous['shares'] if previous else g['shares_2q26'], r['opening_shares'], 'million shares')
        check(r, 'remaining_FCF', r['fcf']-(h1['fcf'] if year == 2026 else 0), r['delta_fcf'])
        check(r, 'remaining_buybacks', r['buybacks']-(h1['buybacks'] if year == 2026 else 0), r['delta_buybacks'])
        check(r, 'remaining_withholding', r['withholding']-(h1['withholding'] if year == 2026 else 0), r['delta_withholding'])
        check(r, 'corporate_net_cash_roll', r['opening_cash']+r['delta_fcf']-r['delta_buybacks']-r['delta_withholding'], r['net_cash'])
        check(r, 'buyback_shares', r['delta_buybacks']/r['price'], r['buyback_shares'], 'million shares')
        issue_sbc = r['sbc']-(h1['sbc'] if year == 2026 else 0)
        check(r, 'net_issuance_share_proxy', issue_sbc*(1-g['withholding_pct'])/r['price'], r['issuance_shares'], 'million shares')
        check(r, 'share_roll', r['opening_shares']-r['buyback_shares']+r['issuance_shares'], r['shares'], 'million shares')
        check(r, 'ending_share_EPS_proxy', r['net_income']/r['shares'], r['eps'], 'USD/share')
        if year in (2026, 2027):
            qrows = [x for x in quarters[scenario] if int(x['quarter'][:4]) == year]
            check(r, 'annual_revenue_from_quarters', sum(x['revenue'] for x in qrows), r['revenue'])
    for row in valuations:
        if row['lens'] == '1':
            r = lookup[(row['scenario'], 2027)]
            value = (g['exit_ev_ebitda']*r['adj_ebitda']+r['net_cash'])/r['shares']
            check(r, 'FY27_end_EBITDA_lens', value, float(row['price']), 'USD/share')
    return checks


def fraction(at, start, end):
    if end <= start:
        raise ValueError('Empty time interval')
    return max(0.0, min(1.0, (at-start).days/(end-start).days))


def endpoint(at, r26, r27, multiple):
    if not date(2026, 6, 30) <= at <= date(2027, 12, 31):
        raise ValueError('Endpoint outside explicit interpolation contract')
    if at <= date(2026, 12, 31):
        f = fraction(at, date(2026, 6, 30), date(2026, 12, 31))
        cash = r26['opening_cash']+f*(r26['net_cash']-r26['opening_cash'])
        shares = r26['opening_shares']+f*(r26['shares']-r26['opening_shares'])
    else:
        f = fraction(at, date(2026, 12, 31), date(2027, 12, 31))
        cash = r26['net_cash']+f*(r27['net_cash']-r26['net_cash'])
        shares = r26['shares']+f*(r27['shares']-r26['shares'])
    positive(shares, 'endpoint shares')
    value = (multiple*r27['adj_ebitda']+cash)/shares
    return cash, shares, value


def impact(row, inputs, globals_, revenue_gap, eta, sbc_case):
    """Own minus counterfactual; the counterfactual has revenue lower by revenue_gap."""
    if eta not in (0., .5, 1.):
        raise ValueError('Cash-cost response outside preregistered finite grid')
    if sbc_case not in ('fixed', 'proportional'):
        raise ValueError('Unknown SBC scenario')
    R = row['revenue']
    positive(R-revenue_gap, 'counterfactual revenue')
    addback = inputs['addback_pct']*revenue_gap
    ai = inputs['ai_referral_pct']*revenue_gap
    dcost = eta*revenue_gap+ai
    counter_uncapped = row['adj_uncapped']-(revenue_gap-dcost+addback)
    counter_adj = min(counter_uncapped, (R-revenue_gap)*globals_['margin_cap'])
    adj = row['adj_ebitda']-counter_adj
    sbc = (row['sbc']/R*revenue_gap) if sbc_case == 'proportional' else 0.
    op = adj-addback-sbc
    ni = op*(1-inputs['eff_tax_rate'])
    tax = revenue_gap*inputs['cash_tax_pct']
    unearned = revenue_gap*inputs['d_unearned_pct']
    wc = revenue_gap*inputs['wc_resid_pct']
    capex = revenue_gap*inputs['capex_pct']
    fcf = adj-tax+unearned+wc-capex
    withheld = globals_['withholding_pct']*sbc
    issuance = (1-globals_['withholding_pct'])*sbc/row['price']
    cash = fcf-withheld
    eps = row['net_income']/row['shares']-(row['net_income']-ni)/positive(row['shares']-issuance, 'counter shares')
    return dict(revenue_gap_usdm=revenue_gap, cash_core_cost_gap_usdm=eta*revenue_gap,
                ai_cost_gap_usdm=ai, addback_gap_usdm=addback, adj_ebitda_gap_usdm=adj,
                sbc_gap_usdm=sbc, operating_income_gap_usdm=op, net_income_gap_usdm=ni,
                annual_ending_share_eps_gap_usd=eps, cash_tax_gap_usdm=tax,
                unearned_cash_gap_usdm=unearned, other_wc_gap_usdm=wc, capex_gap_usdm=capex,
                fcf_gap_usdm=fcf, sbc_adjusted_fcf_gap_usdm=fcf-sbc,
                withholding_gap_usdm=withheld, net_issuance_gap_m=issuance,
                retained_corporate_cash_gap_usdm=cash, incremental_buybacks_usdm=0.)


def run(out):
    out = Path(out).resolve()
    allowed = (BASE / 'economics_v1').resolve()
    if out == allowed or allowed not in out.parents:
        raise ValueError('Output must be a fresh child under the exclusive economics_v1 data directory')
    if out.exists():
        raise FileExistsError(f'Immutable output already exists: {out}')
    inp, annual, valuations, comparison, identities = load_inputs()
    checks = reconcile(inp, annual, valuations)
    if not all(r['passes'] for r in checks):
        out.mkdir(parents=True)
        write_rows(out/'FAILED_reconciliation.csv', checks)
        raise AssertionError('L4 equation mismatch; failure evidence preserved')
    rows = {r['year']: r for r in annual if r['scenario'] == CASE}
    r26, r27 = rows[2026], rows[2027]
    g = inp['globals']
    gap = finite(comparison['revenue_gap_musd'], 'same-basis revenue gap')
    own_q4 = finite(comparison['own_revenue_musd'], 'own Q4 revenue')
    ratio = gap/own_q4
    ends = [(3, date(2026,12,13)), (6, date(2027,3,13)),
            (12,date(2027,9,13)), (None,date(2027,12,31))]
    horizon_rows, convention_rows, perturbations, buybacks, cash_share = [], [], [], [], []
    for months, at in ends:
        cash, shares, value = endpoint(at,r26,r27,g['exit_ev_ebitda'])
        cash_share.append(dict(endpoint=str(at), months=months, n=1,
                               cash_usdm=cash, shares_m=shares,
                               fy27_ebitda_usdm=r27['adj_ebitda'], multiple=g['exit_ev_ebitda'],
                               conditional_value_usd=value,
                               outside_3_to_12_month_horizon=months is None,
                               basis='Uniform modeled cash/share flows; fixed FY27 earnings and multiple'))
        original = next(float(x['price']) for x in valuations if x['scenario']==CASE and x['lens']=='1')
        convention_rows.append(dict(endpoint=str(at),n=1,original_dec2027_value=original,
                                    actual_endpoint_balance_value=value, prematurely_used_future_balances_effect=original-value,
                                    break_even_multiple_to_historical_181_94=(g['price']*shares-cash)/r27['adj_ebitda'],
                                    per_share_per_multiple_turn=r27['adj_ebitda']/shares,
                                    per_share_per_1bn_cash=1000/shares,
                                    historical_price_reference=g['price'], reference_date='2026-09-04'))
        for multiple in (13.5,16.5,18.5):
            for cash_change in (-1000.,0.,1000.):
                for share_change in (-.01,0.,.01):
                    nv=(multiple*r27['adj_ebitda']+cash+cash_change)/(shares*(1+share_change))
                    perturbations.append(dict(endpoint=str(at),n=1,multiple=multiple,cash_change_usdm=cash_change,
                                              share_change_pct=100*share_change,conditional_value_usd=nv,
                                              difference_from_same_endpoint_base=nv-value,
                                              evidence_status='Deterministic unit sensitivity; no probability'))
        if at >= date(2026,12,31):
            fy27_frac=fraction(at,date(2026,12,31),date(2027,12,31))
            for price_shift in (-.2,0.,.2):
                price=r27['price']*(1+price_shift)
                ns=r26['shares']+fy27_frac*(-r27['buybacks']+r27['sbc']*(1-g['withholding_pct']))/price
                buybacks.append(dict(endpoint=str(at),n=1,price_assumption_shift_pct=price_shift*100,
                                     transaction_price_usd=price,buyback_cash_usdm=fy27_frac*r27['buybacks'],
                                     withholding_cash_usdm=fy27_frac*r27['withholding'],
                                     modeled_shares_m=ns,corporate_cash_usdm=cash,
                                     conditional_value_usd=(g['exit_ev_ebitda']*r27['adj_ebitda']+cash)/ns))
    annual_impacts=[]
    for persistence in ('q4_only','same_fraction_sustained_fy27'):
        for eta in (0.,.5,1.):
            for sbc_case in ('fixed','proportional'):
                d26=impact(r26,inp['inputs']['2026'],g,gap,eta,sbc_case)
                d27=impact(r27,inp['inputs']['2027'],g,ratio*r27['revenue'] if persistence!='q4_only' else 0.,eta,sbc_case)
                for year,d in ((2026,d26),(2027,d27)):
                    annual_impacts.append(dict(persistence=persistence,cash_cost_response_eta=eta,sbc_response=sbc_case,
                                               year=year,n=1,**d))
                for months,at in ends:
                    cash,shares,base_value=endpoint(at,r26,r27,g['exit_ev_ebitda'])
                    q4_frac=fraction(at,date(2026,9,30),date(2026,12,31))
                    fy27_frac=fraction(at,date(2026,12,31),date(2027,12,31))
                    dcash=q4_frac*d26['retained_corporate_cash_gap_usdm']+fy27_frac*d27['retained_corporate_cash_gap_usdm']
                    dshares=q4_frac*d26['net_issuance_gap_m']+fy27_frac*d27['net_issuance_gap_m']
                    dev=g['exit_ev_ebitda']*d27['adj_ebitda_gap_usdm']
                    counter=(g['exit_ev_ebitda']*r27['adj_ebitda']-dev+cash-dcash)/positive(shares-dshares,'counterfactual shares')
                    horizon_rows.append(dict(persistence=persistence,cash_cost_response_eta=eta,sbc_response=sbc_case,
                                             endpoint=str(at),n=1,months=months,q4_flow_fraction=q4_frac,fy27_flow_fraction=fy27_frac,
                                             revenue_contrast_basis='Own minus counterfactual matching historical captured Q4 LSEG revenue',
                                             retained_cash_gap_usdm=dcash,net_issuance_gap_m=dshares,
                                             capitalized_fy27_ebitda_gap_usdm=d27['adj_ebitda_gap_usdm'],enterprise_value_gap_usdm=dev,
                                             own_fixed_metric_value_usd=base_value,counterfactual_value_usd=counter,
                                             economic_difference_usd_per_share=base_value-counter,
                                             evidence_status='Conditional arithmetic; n is one scenario and empirical validation n=0'))
    asymmetry=r26['delta_withholding']-(r26['sbc']-inp['h1']['sbc'])*g['withholding_pct']
    diagnostics=[dict(check='FY26_H2_withholding_residual_less_35pct_H2_SBC',n=1,value=asymmetry,unit='USDm',
                      interpretation='Actual H1 withholding differs from 35pct of H1 SBC; existing mixed conventions retained'),
                 dict(check='FY27_SBC_adjusted_FCF_less_buybacks',n=1,value=r27['sbc_adj_fcf']-r27['buybacks'],unit='USDm',
                      interpretation='Economic-compensation cash proxy less buybacks; not corporate cash roll'),
                 dict(check='FY27_net_cash_generation_after_buybacks_withholding',n=1,value=r27['fcf']-r27['buybacks']-r27['withholding'],unit='USDm',
                      interpretation='Actual model cash-roll increment; do not subtract full SBC again')]
    out.mkdir(parents=True)
    tables={'equation_checks.csv':checks,'cash_share_horizons.csv':cash_share,
            'horizon_convention.csv':convention_rows,'annual_operating_contrast.csv':annual_impacts,
            'horizon_operating_contrast.csv':horizon_rows,'multiple_cash_share_sensitivity.csv':perturbations,
            'repurchase_price_sensitivity.csv':buybacks,'accounting_diagnostics.csv':diagnostics}
    for name,table in tables.items():
        write_rows(out/name,table)
    dump(out/'source_hashes.json',identities)
    summary=dict(l4_commit='29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70',
                 evidence_scenario=CASE,statement='Conditional economic bridge; no production or investment adoption',
                 equation_count=len(checks),scenario_year_count=len(annual),max_equation_delta=max(abs(r['difference']) for r in checks),
                 captured_comparator=comparison,q4_revenue_gap_usdm=gap,sustained_fraction_of_own_revenue=ratio,
                 unit='USD million except explicit per-share share-count ratio fields',
                 source_hashes=identities,source_code_sha256=sha(__file__),
                 output_hashes={name:sha(out/name) for name in tables},
                 empirical_validation_n=0,estimated_parameters=0)
    dump(out/'receipt.json',summary)
    print(json.dumps(dict(output=str(out),equations=len(checks),max_delta=summary['max_equation_delta'],gap_usdm=gap),indent=2))
    return summary


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True,help='Fresh child directory under economics_v1 data directory')
    run(parser.parse_args().out)
