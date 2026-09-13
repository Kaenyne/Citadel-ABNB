"""Rebuild the new L4 model without altering source workbooks or prior outputs."""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, math, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
PACKAGE=Path(__file__).resolve().parent
DEFAULT_NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
CASES=['review_with_k','review_without_k','k0_conditional','nights_case_a','adr_mean_reversion',
       'review_with_k_fx_down_sensitivity','review_with_k_fx_up_sensitivity']
LABELS=['Review with fee mechanics','Review without fee mechanics','K0 conditional GBV',
        'Alternative nights A','ADR mean reversion','Illustrative revenue −1%','Illustrative revenue +1%']
YEARS=[2026,2027,2028]
QKEYS=[f'{y}Q{q}' for y in [2026,2027] for q in range(1,5)]
def read_csv(p):
    with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(p,rows):
    with open(p,'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def dump(p,obj):p.write_text(json.dumps(obj,indent=2,allow_nan=False),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def oldq(q):return f'{q[-1]}Q{q[2:4]}'
def load_legacy():
    s=importlib.util.spec_from_file_location('l4_legacy_readonly',ROOT/'analysis/src/overnight/13_driver_model.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def dcf_factor(start,terminal,coe):
    if coe<=terminal:raise ValueError('Cost of equity must exceed terminal growth')
    flow,pv=1.,0.
    for t in range(1,11):
        flow*=1+start+(terminal-start)*(t-1)/9
        pv+=flow/(1+coe)**t
    return pv+flow*(1+terminal)/(coe-terminal)/(1+coe)**10
def replicate_legacy():
    """Independent of original build: published annual CSV and explicit six-lens equations."""
    rows={int(r['year']):{k:float(v) for k,v in r.items() if k!='scenario'}
          for r in read_csv(ROOT/'data/processed/overnight/13_model_annual.csv') if r['scenario']=='Base'}
    a,b=rows[2027],rows[2028]
    prices=[(16.5*a['adj_ebitda']+a['net_cash'])/a['shares_end'],
            (14.3*a['fcf']+a['net_cash'])/a['shares_end'],
            19.5*a['sbc_adj_fcf']/a['shares_end'],19.5*a['net_income']/a['shares_end'],
            (16.5*b['adj_ebitda']+b['net_cash'])/b['shares_end']/1.105,
            (a['fcf']*dcf_factor(.09,.03,.105)+a['net_cash'])/a['shares_end']]
    assert abs(prices[0]-180.876286)<.001
    assert abs(sum(prices)/6-156.786845)<.001
    return {'method':'Independent equations on published annual CSV; input precision four decimals',
            'lenses':prices,'ebitda_lens':prices[0],'six_lens_mean':sum(prices)/6,
            'tolerance_usd_per_share':.001,'legacy_target_label':'Approximately 30 September 2027; FY27-end balances',
            'new_target_convention':'31 December 2027; FY27-end balances; no adopted target'}
def build_financial(quarters,inputs,globals_,fy25,h1,nb_cost):
    out=[];prev=dict(fy25);shares=globals_['shares_2q26'];cash=globals_['net_cash_2q26']
    for year in YEARS:
        i=inputs[str(year)]
        if year<2028:
            qs=[q for q in quarters if q['quarter'].startswith(str(year))]
            revenue=sum(q['revenue'] for q in qs);nights=sum(q['nights'] for q in qs);gbv=sum(q['gbv'] for q in qs)
        else:
            revenue=prev['rev']*(1+i['inherited_revenue_growth'])
            nights=prev['nights']*(1+i['inherited_nights_growth'])
            gbv=prev['gbv']*(1+i['inherited_gbv_growth'])
        cor=prev['cor']/prev['gbv']*(1+i['cor_per_gbv'])*gbv
        ops=prev['ops']/prev['nights']*(1+i['ops_cpn'])*nights
        fixed={k:prev[k]*(1+i[inp]) for k,inp in [('pd','pd_cash'),('bpm','bpm_cash'),('fop','fop_cash'),('ga','ga_cash')]}
        ai=revenue*i['ai_referral_pct'];addback=revenue*i['addback_pct']
        costs=cor+ops+sum(fixed.values())+nb_cost[str(year)]+ai
        uncapped=revenue-costs+addback;adj=min(uncapped,revenue*globals_['margin_cap'])
        sbc=prev['sbc']*(1+i['sbc_growth']);da=revenue*i['da_pct']
        op=adj-sbc-addback;pretax=op+i['int_income']-i['int_expense'];ni=pretax*(1-i['eff_tax_rate'])
        tax=revenue*i['cash_tax_pct'];unearned=revenue*i['d_unearned_pct'];capex=revenue*i['capex_pct'];wc=revenue*i['wc_resid_pct']
        fcf=adj+i['int_income']-i['int_expense']-tax+unearned+wc-capex
        price=globals_['price']*(1+globals_['price_growth'])**(year-2026);wh=sbc*globals_['withholding_pct']
        dfcf=fcf-(h1['fcf'] if year==2026 else 0);bb=i['buybacks']-(h1['buybacks'] if year==2026 else 0)
        dwh=wh-(h1['withholding'] if year==2026 else 0);sbc_issue=sbc-(h1['sbc'] if year==2026 else 0)
        opening_cash=cash;opening_shares=shares
        shares+=-bb/price+sbc_issue/price*(1-globals_['withholding_pct']);cash+=dfcf-bb-dwh
        if shares<=0:raise ValueError('Share schedule produces nonpositive shares')
        r=dict(year=year,revenue=revenue,nights=nights,gbv=gbv,cor=cor,ops=ops,**fixed,nb_cost=nb_cost[str(year)],ai_cost=ai,
          cash_costs=costs,addbacks=addback,adj_uncapped=uncapped,adj_ebitda=adj,margin=adj/revenue,sbc=sbc,da=da,
          op_income=op,pretax=pretax,net_income=ni,eps=ni/shares,interest_income=i['int_income'],interest_expense=i['int_expense'],
          cash_taxes=tax,d_unearned=unearned,capex=capex,wc_resid=wc,fcf=fcf,sbc_adj_fcf=fcf-sbc,
          buybacks=i['buybacks'],withholding=wh,price=price,opening_cash=opening_cash,delta_fcf=dfcf,delta_buybacks=bb,
          delta_withholding=dwh,net_cash=cash,opening_shares=opening_shares,buyback_shares=bb/price,
          issuance_shares=sbc_issue/price*(1-globals_['withholding_pct']),shares=shares)
        out.append(r);prev={**r,'rev':revenue}
    return out
def value(fin,g):
    a,b=fin[1:];ev=g['exit_ev_ebitda']*a['adj_ebitda'];eq=ev+a['net_cash']
    lenses=[eq/a['shares'],(g['exit_ev_fcf']*a['fcf']+a['net_cash'])/a['shares'],g['exit_p_sbcfcf']*a['sbc_adj_fcf']/a['shares'],
            g['exit_p_earnings']*a['eps'],(g['exit_ev_ebitda']*b['adj_ebitda']+b['net_cash'])/b['shares']/(1+g['cost_of_equity']),
            (a['fcf']*dcf_factor(g['dcf_start_growth'],g['terminal_growth'],g['cost_of_equity'])+a['net_cash'])/a['shares']]
    return dict(enterprise_value_musd=ev,equity_value_musd=eq,value_per_share=lenses[0],six_lens_mean=sum(lenses)/6,lenses=lenses)
def prepare(revenue_dir):
    replication=replicate_legacy() # MUST pass before any new model calculation.
    m=load_legacy();oldannual={a['year']:a for a in m.build_annual('Base')};oldqs={r['quarter']:r for r in m.quarterly_pl('Base',list(oldannual.values()))}
    base_inputs={str(y):{k:v[1] for k,v in m.ANNUAL_INPUTS[y].items() if k not in ['take_bps','reg_mult','new_business']} for y in YEARS}
    for y in YEARS:
        prior=oldannual[y-1] if y>2026 else m.FY25
        for key in ['revenue','nights','gbv']:
            base_inputs[str(y)]['inherited_'+key+'_growth']=oldannual[y][key]/(prior.get('rev') if key=='revenue' and y==2026 else prior[key])-1
    globals_={k:v[1] for k,v in m.VAL_INPUTS.items() if k not in ['nb_incr_margin','dcf_years']}
    nb_cost={str(y):oldannual[y]['nb_cost'] for y in YEARS}
    forecasts=read_csv(revenue_dir/'forecast.csv');oprows=read_csv(revenue_dir/'operating_inputs.csv')
    fidx={(r['scenario'],r['quarter']):r for r in forecasts}
    if len(fidx)!=len(forecasts):raise ValueError('Duplicate scenario-quarter forecast key')
    # Operating inputs use the same scenario + quarter key as forecasts.
    oidx={(r['scenario'],r['quarter']):r for r in oprows}
    cases=[]
    for case,label in zip(CASES,LABELS):
        source_case=case if '_sensitivity' not in case else 'review_with_k'
        adjustment=-.01 if 'down_sensitivity' in case else .01 if 'up_sensitivity' in case else None
        quarters=[]
        for q in QKEYS:
            if q in ['2026Q1','2026Q2']:
                p=m.PANEL[oldq(q)];qr=dict(quarter=q,nights=float(p['nights_m']),gbv=float(p['gbv_musd']),revenue=float(p['revenue_musd']),guide=None,kind='Actual')
            else:
                prior=next((x for x in quarters if x['quarter']==str(int(q[:4])-1)+q[4:]),None)
                oq=oldqs[oldq(q)]
                nights=oq['nights'] if prior is None else prior['nights']*(1+oq['nights_yoy_pct']/100)
                gbv=oq['gbv'] if prior is None else prior['gbv']*(1+oq['gbv_yoy_pct']/100)
                op=oidx.get((source_case,q))
                if op:
                    cost_nights=op.get('nights_m') or op.get('nights')
                    if not cost_nights:
                        cost_nights=oidx[('review_with_k',q)]['nights_m']
                    nights=float(cost_nights)
                    gbv=float(op.get('gbv_musd') or op.get('gbv'))
                f=fidx.get((source_case,q))
                if f:
                    raw=float(f['revenue_musd']);revenue=raw*(1+(adjustment or 0));cushion=float(f['cushion_decimal'])
                    qr=dict(quarter=q,nights=nights,gbv=gbv,revenue=revenue,guide=revenue/(1+cushion),kind='Kernel covered',
                        base_revenue=raw,cushion=cushion,incremental_adjustment=adjustment,source_case=source_case)
                else:
                    if q in ['2026Q3','2026Q4','2027Q1']:raise ValueError(f'Missing covered forecast {source_case}/{q}')
                    old_prior=oldqs.get(oldq(str(int(q[:4])-1)+q[4:]))
                    growth=oq['revenue']/(old_prior['revenue'] if old_prior else oq['prior_revenue'])-1
                    qr=dict(quarter=q,nights=nights,gbv=gbv,revenue=prior['revenue']*(1+growth),guide=None,kind='Inherited growth',
                            inherited_growth=growth,source_case=source_case)
            quarters.append(qr)
        annual=build_financial(quarters,base_inputs,globals_,m.FY25,m.H1_26,nb_cost);valuation=value(annual,globals_)
        cases.append(dict(scenario=case,label=label,source_scenario=source_case,adjustment=adjustment,quarters=quarters,annual=annual,valuation=valuation))
    return dict(as_of='2026-09-13',case_names=CASES,replication=replication,inputs=base_inputs,globals=globals_,fy25=m.FY25,h1=m.H1_26,
      nb_cost=nb_cost,cases=cases,legacy_annual=oldannual,legacy_quarters=oldqs,forecasts=forecasts,operating_inputs=oprows,
      fx_status='Pending explicit L3 version/commit and checksums. Baseline excludes an additional timing adjustment; its value is not estimated.',
      scope='Kernel replaces consolidated total revenue in Q3:26, Q4:26 and Q1:27. No legacy take-rate/FX wedge or separate new-business revenue overlay.',
      horizon='31 December 2027 convention; FY27-end net cash and diluted share proxy. Q2:27 onward and FY28 growth are inherited assumptions.')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--revenue-dir',type=Path,default=ROOT/'data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1')
    ap.add_argument('--run-id',default=datetime.now(timezone.utc).strftime('run_%Y%m%dT%H%M%SZ'));ap.add_argument('--no-workbook',action='store_true');args=ap.parse_args()
    args.revenue_dir=args.revenue_dir.resolve()
    data=prepare(args.revenue_dir)
    out=ROOT/'data/processed/forecast_methods/lane4_model_v1'/args.run_id
    book=ROOT/'model/lane4_v1/outputs/lane4_model'/args.run_id
    out.mkdir(parents=True,exist_ok=False);book.mkdir(parents=True,exist_ok=False)
    data['data_dir']=str(out);data['book_dir']=str(book)
    dump(out/'model_input.json',data);dump(out/'legacy_replication.json',data['replication'])
    annual=[];summary=[];valuation=[]
    for c in data['cases']:
        annual.extend([dict(scenario=c['scenario'],**a) for a in c['annual']]);a=c['annual'][1];v=c['valuation']
        summary.append(dict(scenario=c['scenario'],scenario_label=c['label'],q4_guide_musd=c['quarters'][3]['guide'],
            fy26_revenue_musd=c['annual'][0]['revenue'],fy27_revenue_musd=a['revenue'],fy27_ebitda_musd=a['adj_ebitda'],
            fy27_net_income_musd=a['net_income'],fy27_fcf_musd=a['fcf'],fy27_net_cash_musd=a['net_cash'],fy27_shares_m=a['shares'],
            exit_multiple=data['globals']['exit_ev_ebitda'],**{k:v[k] for k in ['enterprise_value_musd','equity_value_musd','value_per_share','six_lens_mean']}))
        valuation.extend(dict(scenario=c['scenario'],lens=j+1,price=p) for j,p in enumerate(v['lenses']))
    write_csv(out/'annual.csv',annual);write_csv(out/'scenario_summary.csv',summary);write_csv(out/'valuation.csv',valuation)
    sources=[ROOT/'analysis/src/overnight/13_driver_model.py',ROOT/'model/ABNB_driver_model.xlsx',ROOT/'model/assumptions.md',
       ROOT/'data/processed/overnight/13_model_annual.csv',ROOT/'data/processed/overnight/13_model_quarterly.csv',
       ROOT/'data/processed/overnight/13_valuation_summary.csv',args.revenue_dir/'forecast.csv',args.revenue_dir/'operating_inputs.csv']
    sources+=list((ROOT/'data/processed/overnight').glob('0[257]_*.csv'))
    sources+=list((ROOT/'data/processed/overnight').glob('1[012]_*.csv'))
    sources.append(ROOT/'data/processed/abnb_capital_return_quarterly.csv')
    dump(out/'input_manifest.json',[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(set(sources))])
    if not args.no_workbook:
        subprocess.run([str(DEFAULT_NODE),str(PACKAGE/'build.mjs'),str(out/'model_input.json')],check=True,cwd=ROOT)
    print(json.dumps({'data_dir':str(out),'workbook_dir':str(book),'legacy':data['replication'],'scenario_summary':summary},indent=2))
if __name__=='__main__':main()
