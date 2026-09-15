"""Create local L4 review artifacts from explicitly verified immutable snapshots.

No estimation, registrations, adopted target, probabilities or trade actions.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, shutil, subprocess
from collections import Counter
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from pypdf import PdfReader
from render import render

ROOT=Path(__file__).resolve().parents[4]
PKG=Path(__file__).resolve().parent
SOURCE=ROOT/'data/processed/forecast_methods/lane4_sources_v2/snapshot_v1'
POPPLER=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe'
CONVERSION='Validation complete; free-weight promotion FAIL W1/W2; existing fixed 2/3 K0 seasonal policy retained.'
FX='Verified source; current financial application ineligible: pre-hedge baseline and H/H_new missing. Q3 only; no Q4/Q1 extrapolation.'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write_csv(p,rows):
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def dump(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf-8')
def num(r,k):
    v=float(r[k])
    if not math.isfinite(v):raise ValueError(f'Nonfinite {k}')
    return v
def one(rows,**key):
    rs=[r for r in rows if all(r[k]==v for k,v in key.items())]
    if len(rs)!=1:raise ValueError(f'Expected unique {key}; got {len(rs)}')
    return rs[0]
def markdown_table(rows,columns):
    return '\n'.join(['| '+' | '.join(label for _,label in columns)+' |','| '+' | '.join('---' for _ in columns)+' |']+
                     ['| '+' | '.join(str(r.get(k,'')) for k,_ in columns)+' |' for r in rows])

def verify(mrows,annual,expectations,eligibility,dispositions):
    checks=[]
    for r in mrows:
        a=one(annual,scenario=r['scenario'],year='2026');b=one(annual,scenario=r['scenario'],year='2027')
        cash=num(a,'net_cash')+256/365*(num(b,'net_cash')-num(a,'net_cash'))
        shares=num(a,'shares')+256/365*(num(b,'shares')-num(a,'shares'))
        ev=num(r,'exit_multiple')*num(b,'adj_ebitda')
        for k,expected in [('horizon_net_cash_musd',cash),('horizon_shares_m',shares),('enterprise_value_musd',ev),
                           ('equity_value_musd',ev+cash),('value_per_share',(ev+cash)/shares),
                           ('december_value_per_share',(ev+num(b,'net_cash'))/num(b,'shares'))]:
            delta=num(r,k)-expected
            if abs(delta)>.001:raise ValueError(f'{r["scenario"]}/{k}: {delta}')
            checks.append({'scenario':r['scenario'],'metric':k,'delta':delta})
        for y in ['2026','2027','2028']:
            f=one(annual,scenario=r['scenario'],year=y)
            cf=num(f,'adj_ebitda')+num(f,'interest_income')-num(f,'interest_expense')-num(f,'cash_taxes')+num(f,'d_unearned')+num(f,'wc_resid')-num(f,'capex')
            if abs(cf-num(f,'fcf'))>.001:raise ValueError('FCF mismatch')
            if abs(num(f,'op_income')-(num(f,'adj_ebitda')-num(f,'sbc')-num(f,'addbacks')))>.001:raise ValueError('D&A double count')
    e=one(expectations,scenario='review_with_k',quarter='2026Q4',vendor_family='LSEG family',consensus_as_of_timestamp='2026-09-13T15:20Z')
    if abs(num(e,'own_revenue_musd')-num(e,'revenue_consensus_musd')-num(e,'revenue_gap_musd'))>1e-6:raise ValueError('Same-basis gap mismatch')
    if e['guide_expectations_status'].lower().find('unavailable')<0:raise ValueError('Unexpected guide-expectations adoption')
    if len(dispositions)!=1187 or len({r['row_id'] for r in dispositions})!=1187:raise ValueError('Source ledger incomplete')
    if eligibility['central_fx_financial_eligibility'] or eligibility['estimated_incremental_fx_musd'] is not None:raise ValueError('Unidentified FX promoted')
    if eligibility['free_weight_promotion']!='FAIL_BOTH_MATCHED_W1_W2':raise ValueError('Conversion status changed')
    return checks

def make_card(out,forecast,summary):
    card=json.loads((ROOT/'deck/drafts/lane4_v1/review_v4/unsigned_card.json').read_text())
    for r in card['rules']:
        r['conversion_status']=CONVERSION
        r['fx_status']=FX
        r['id']=r['id'].replace('L4-C','L4v2-C')
        if r['id']=='L4v2-C02':
            r['score']='Compare published guide midpoint and rounding interval with frozen own guide scenarios. Compare with explicit, dated guide expectations only if available. Revenue-consensus comparisons are separately labelled different-object diagnostics; never scored as guide surprise.'
            r['source']='Q3 letter Q4 guide; fixed L4 v2 scenarios. Explicit guide expectations unavailable at frozen 13 Sep 2026 snapshot.'
        if r['id']=='L4v2-C09':
            r['reference']='L3 source accepted; incremental FX remains unestimated. Source matches Q3 baseline only; Q4/Q1 cohort inputs absent.'
            r['definition']='Stated reported revenue FX contribution, its hedge wording, and separately labelled conditional L3 timing scenarios.'
            r['status']='INELIGIBLE FINANCIAL APPLICATION; null is not zero.'
            r['score']='Record stated contribution as a rounding interval. Require certified matching pre-hedge baseline R-H, signed baseline H and scenario H_new before R_new=m*(R-H)+H_new. No comparison against a missing central estimate and no full FX overlay on USD GBV.'
    card['rules'].append({'id':'L4v2-C12','metric':'Explicit Q4 management-guide expectations','unit':'USD millions; vendor/timestamp',
       'definition':'A source explicitly forecasting management revenue-guide midpoint, distinct from analyst revenue estimate',
       'reference':'UNAVAILABLE at frozen 13 Sep 2026 15:20 UTC snapshot',
       'score':'Keep ABSENT until direct source, object, horizon, vendor and pre-release timestamp are captured. S/(1+c) remains hypothetical, never observed consensus.',
       'source':'Direct dated guide-expectations source if obtained','rounding':'Source precision; no fabricated interval','status':'UNSIGNED',
       'observed_value':None,'outcome':'NOT YET SCORED','publication_path':None,'page_or_table':None,'retrieved_at_utc':None,
       'restatement_version':None,'conversion_status':CONVERSION,'fx_status':FX})
    card['information_date']='2026-09-13';card['source_bundle_commit']='8821961853e4068febbfe2712f9a4e1036c9e629'
    dump(out/'unsigned_card.json',card);write_csv(out/'unsigned_card.csv',card['rules'])
    text='# Airbnb | Unsigned November review card\n\nStatus: UNSIGNED. No direction, target, probabilities or execution authority. '+CONVERSION+' '+FX+'\n\n'
    text+='The inherited project event date is 5 November 2026; verify issuer schedule before use. Score after complete publications on 6 November. Preserve primary file/URL, page/table, units, precision, publication and extraction timestamps, and restatement version. Missing is ABSENT. Freeze any new pre-letter comparator separately; the September revenue consensus remains a historical comparator.\n\n'
    text+='The fixed Q3 card denominator is (2*27200+29200)/3 = 27,866.666667 USDm. Warning 17.09% corresponds to 4,762.413333 USDm; escalation 16.93% to 4,717.826667 USDm. These are proposed diagnostic rules, not newly calibrated structural thresholds.\n\n'
    for r in card['rules']:
        text+=f'## {r["id"]}: {r["metric"]}\n\n'+ '\n\n'.join(f'**{label}:** {r[key]}' for key,label in [('unit','Units'),('definition','Definition'),('reference','Reference'),('score','Rule'),('source','Source'),('rounding','Precision'),('status','Standing')])+'\n\n'
    (out/'unsigned_november_card.md').write_text(text,encoding='utf-8')
    return card

def decisions(mrows,e,annual):
    b=one(mrows,scenario='review_with_k');soft=one(mrows,scenario='joint_soft');firm=one(mrows,scenario='joint_firm')
    definitions=[
      ('D01','Q4 revenue same-basis comparison',f"R {num(e,'own_revenue_musd'):.6f}; S {num(e,'revenue_consensus_musd'):.6f}; R-S {num(e,'revenue_gap_musd'):+.6f} USDm / {num(e,'revenue_gap_pct'):+.6f}%",'Yahoo / LSEG-family revenue; 13 Sep 2026 15:20 UTC','Calculated conditional n=1; historical validation n=0','No long/short inference; refresh comparable object and timestamp before decision'),
      ('D02','Guide expectations',f"G {num(e,'own_guide_mid_musd'):.6f}; G-S {num(e,'guide_minus_revenue_diagnostic_musd'):+.6f}; S/(1+c) {num(e,'hypothetical_street_guide_musd'):.6f} USDm",'Q4 2026; shared cushion illustration only','Explicit guide expectations UNAVAILABLE; mixed-object G-S diagnostic','Obtain direct dated guide expectations or retain unavailable; do not call G-S a guide surprise'),
      ('D03','Conversion policy','Free/fixed USD RMSE 1.165407 W1 n14 and 1.015513 W2 n10; all22 w=0.786478 descriptive','Matched letter-close chronological fixed-OLS comparator; 2023Q1+/2024Q1+','Promotion FAIL; W2 nested; operational K0 estimator is distinct','Retain existing fixed 2/3 K0 seasonal policy; no new fit adopted'),
      ('D04','Conditional operating-conversion-cushion envelope',f"Q4 guide {num(soft,'q4_guide_musd'):.2f} to {num(firm,'q4_guide_musd'):.2f}; September value {num(soft,'value_per_share'):.2f} to {num(firm,'value_per_share'):.2f} USD/share",'Three main envelope cases within nine-case model; isolated net sensitivities excluded; fixed weight; lambda stress +/-0.10pp','Assumed envelope, not confidence or prediction interval','No probabilities; no generic net FX factor combined with lambda stress; cushion changes guide only'),
      ('D05','Twelve-month horizon',f"13 Sep 2027 = 256/365 FY27 flows; cash {num(b,'horizon_net_cash_musd'):.3f} USDm; shares {num(b,'horizon_shares_m'):.3f}m",'Frozen information 13 Sep 2026; full FY27 EBITDA','Uniform within-year net cash/share flows assumption','Approve/replace cash timing assumption explicitly; show December comparison separately'),
      ('D06','Conditional valuation',f"16.5x FY27 EBITDA; Sep {num(b,'value_per_share'):.6f}; Dec {num(b,'december_value_per_share'):.6f}; date-only difference {num(b,'date_only_value_difference'):.6f} USD/share",'Inherited 7 Sep 2026 driver model; price path $181.94 from 4 Sep only for share mechanics','Conditional financial bridge; no adopted target','No mechanical average, +0.48 causal multiple rule, probability or return claim'),
      ('D07','Cohort FX application','1080 source rows; 180 arithmetic scenarios; 5 Q3 baseline identities; 0 financially eligible current baselines','Q3 2026 only versus Q3 2025; Q4/Q1 absent','Accepted implementation; RNPL/currency/recognition exposures unidentified','Require certified R-H and H_new; retain null incremental FX, never estimated zero'),
      ('D08','Executable expectation edge','A2 legacy guide-minus-revenue sign 7/8 W1, 6/7 W2; return tests do not establish executable edge','L2 committed A2; legacy guide-minus-revenue comparator is not explicit guide expectations','PARTIAL; no established executable edge','Do not rebrand historical sign score as measured management-guide surprise'),
      ('D09','Revenue revision test','B2 revision hurdle 5/9 W1 and 4/7 W2 versus 70% hurdle','L2 committed B2; preserved historical scope','FAIL','No claim that the guide diagnostic predicts a reliable revision/trade'),
      ('D10','ADR and RNPL','Corrected unpaid-stock proxies 2.0 / 8.0 / 9.7pp; no identified migration coefficient','Committed Lane2 F evidence; ADR variants replace entire inputs','Stocks not recognized revenue-flow shares; ADR/FX/fee overlap controlled','Keep RNPL effect unidentified; never convert unpaid stocks directly to revenue losses'),
      ('D11','Fee, hotel and cross-issuer evidence','Fee theta unavailable, 0/6 scheduled captures; NCLH transfer FAIL; hotel comparator only','Accepted immutable L3 bundle, 13 Sep 2026','No ABNB adjustment from these sources','Wait for valid fee identification/current ABNB evidence before adjustment'),
      ('D12','November unsigned decision rules','Lambda warning17.09%, escalation16.93%; proposed UF-minus-GBV >-8pp AND explicit low-double-digit nights wording','Frozen F diagnostic denominator 27,866.666667 USDm','UNSIGNED; round printed integers +/-0.5; missing ABSENT','No automatic cover, reverse, trade, or inverse-thesis validation'),
      ('D13','Original team D-01: Q3 revenue choice','Kernel4808.362929 USDm; issued4730 times(1+median cushion)=4814.690226 (+6.327296); mean alternative4817.823947 (+9.461017)','Q3 2026 already issued guide midpoint4730 USDm; trailing-eight realized cushion; L4 v2 issued-guide comparison','OPEN decision; alternatives to kernel, not independent forecasts or added revenue','Retain kernel for this review; replacement by issued-guide times cushion requires explicit adoption and rerun; never stack'),
    ]
    return [dict(decision_id='L4v2-'+i,object=o,quantified_evidence=q,period_benchmark_vintage=p,status=s,decision_or_required_evidence=d,adoption='UNSIGNED') for i,o,q,p,s,d in definitions]

def memo(mrows,annual,e,scores):
    b=one(mrows,scenario='review_with_k');a=one(annual,scenario='review_with_k',year='2027')
    soft=one(mrows,scenario='joint_soft');firm=one(mrows,scenario='joint_firm')
    table=[]
    for label,r in [('Soft envelope',soft),('Reference',b),('Firm envelope',firm)]:
        table.append({'case':label,'r':f"{num(r,'fy27_revenue_musd'):,.0f}",'eb':f"{num(r,'fy27_ebitda_musd'):,.0f}",'cf':f"{num(r,'fy27_fcf_musd'):,.0f}",'p':f"${num(r,'value_per_share'):.2f}"})
    chron=[]
    for window in ['W1','W2']:
        f=one(scores,window=window,model='free_w_usd');x=one(scores,window=window,model='fixed_2_3_usd')
        chron.append({'w':window+' (n='+f['n']+')','f':f"{num(f,'rmse_musd'):.2f}",'x':f"{num(x,'rmse_musd'):.2f}",'r':f"{num(f,'ratio_to_fixed_ols'):.4f} / FAIL"})
    return f'''# Airbnb | Revenue, guide and value

Status: UNSIGNED local review. Information frozen 13 September 2026; execution date 14 September. No adopted direction, target or probabilities.

**Our conditional Q4 revenue is $3,179.3m, $18.3m (+0.58%) above the captured Street revenue estimate.** The $3,123.4m implied guide uses a separate cushion assumption. Comparing that guide directly with revenue consensus does not establish a negative guide surprise. Explicit expectations for management's guide remain unavailable. [R,Q]

## Compare the same forecast object

| Q4 2026 object | USDm | Interpretation |
| --- | --- | --- |
| Own revenue R / Street revenue S | {num(e,'own_revenue_musd'):,.3f} / {num(e,'revenue_consensus_musd'):,.3f} | Yahoo / LSEG-family revenue; 13 Sep 15:20 UTC |
| Revenue gap R - S | {num(e,'revenue_gap_musd'):+,.3f} | {num(e,'revenue_gap_pct'):+.4f}% of Street revenue; same basis |
| Own implied guide G | {num(e,'own_guide_mid_musd'):,.3f} | R / (1+c); c={100*num(e,'cushion_decimal'):.4f}%, trailing-eight median |
| G - S | {num(e,'guide_minus_revenue_diagnostic_musd'):+,.3f} | Different objects; diagnostic, not guide surprise |
| Hypothetical Street guide S / (1+c) | {num(e,'hypothetical_street_guide_musd'):,.3f} | Assumes our cushion; not observed consensus |

## Retain the tested fixed rule

Revenue = seasonal lambda x [2/3 prior-quarter GBV + 1/3 two-quarters-prior GBV]. L3 accepted implementation and completed validation; estimating a shared lag weight failed its preregistered promotion hurdle. Existing K0 seasonal estimation stays in production. The all22 weight 0.786478 and newly fitted fixed-OLS coefficients are descriptive only. [C]

{markdown_table(chron,[('w','Chronological window'),('f','Free RMSE, USDm'),('x','Matched fixed OLS'),('r','Free/fixed; result')])}

Notes: W1 is 2023Q1-2026Q2; W2 is 2024Q1-2026Q2 and nested. Origins are letter-close with newly printed GBV. Errors do not measure pre-release guide skill or include today's forecast-Q3-GBV and cushion risk. The shared weight is not a measured booking-cohort probability. Three full accepted charts and their limitations accompany this memo. [C,Q]

<!-- PAGEBREAK -->

# The financial consequence is conditional

## Operating assumptions flow into cash and value

{markdown_table(table,[('case','Conditional case'),('r','FY27 revenue, $m'),('eb','EBITDA, $m'),('cf','FCF, $m'),('p','13 Sep 2027 / share')])}

Soft uses ADR mean reversion, lambda -0.10pp and 3.88% Q4 cushion; firm uses alternative nights A, lambda +0.10pp and the median cushion. Weight stays 2/3. These are assumed envelopes, not CIs or probability cases. Separate +/-1% net after-hedge revenue sensitivities affect Q3/Q4 2026 and Q1 2027, then propagate changed annual bases; they are not measured FX and are not combined with lambda stresses. [R,M]

Q4 implied guides are ${num(soft,'q4_guide_musd'):,.1f}m / ${num(b,'q4_guide_musd'):,.1f}m / ${num(firm,'q4_guide_musd'):,.1f}m for soft / reference / firm. Cushion changes the guide only; it does not change revenue, earnings or cash. [R,M]

**The reference is ${num(b,'value_per_share'):.2f} per share at 13 September 2027**, twelve months from the frozen information date: 16.5x full FY27 EBITDA plus ${num(b,'horizon_net_cash_musd'):,.1f}m net cash, divided by {num(b,'horizon_shares_m'):,.2f}m diluted-share proxy. Cash and shares use FY26 end plus 256/365 of FY27 net flows, assumed uniform within year. The later 31 December value is ${num(b,'december_value_per_share'):.2f}; the ${num(b,'date_only_value_difference'):.2f} difference changes only balance timing. The multiple is inherited and conditional. [M,V]

Notes: FY27 net income ${num(a,'net_income'):,.0f}m. FCF = adjusted EBITDA + net interest - cash taxes + change in unearned fees + working-capital residual - capex. Cash taxes ${num(a,'cash_taxes'):,.0f}m; capex ${num(a,'capex'):,.0f}m; unearned change {num(a,'d_unearned'):,.0f}. Total EBITDA addbacks include D&A; GAAP operating proxy subtracts SBC and total addbacks once. Customer funds are excluded. Share mechanics inherit the $181.94 price anchor dated 4 Sep 2026; it is not a return denominator. Later-quarter growth and costs remain inherited assumptions. [M,V]

## Evidence that can and cannot change the decision

L3's 108-file bundle and 1,187 row dispositions are verified. FX scenario arithmetic reconciles, but matching pre-hedge baseline, signed H/H_new, and RNPL recognition exposures remain unidentified. Current cohort inputs cover Q3 only, not Q4/Q1. Incremental FX stays null, not measured zero. Fee theta is unavailable (0/6 scheduled captures); NCLH transfer fails and supplies no ABNB adjustment; hotels remain comparators. [S]

A2 remains PARTIAL with no established executable edge; its historical sign test compares guide with revenue expectations, not explicit guide expectations. B2 fails (5/9 and 4/7 versus 70%). The unsigned November card preserves rounding-aware lambda, payment-balance, ADR and exact management-wording tests. Missing evidence is ABSENT; no rule automatically trades or validates the opposite thesis. [E,F]

Sources: [R] L4 revenue v2 frozen bridge and dated expectations; [M] linked L4 model v2 and independent tieout; [C,S] accepted L3 bundle 8821961853e4, research 7fb6fe0f248d, source audit v2; [Q] 13 Sep QVS basis/variance notes; [E,F] committed L2 A2/B2 and corrected RNPL notes; [V] inherited driver model, 7 Sep 2026. Full paths, hashes, units, statuses and decision alternatives are in the source ledger and unsigned register.
'''

def appendix(out,assets,source,descriptive):
    path=out/'accepted_L3_exhibits.pdf';c=canvas.Canvas(str(path),pagesize=(792,612))
    c.setTitle('Airbnb | Accepted L3 exhibits and interpretation limits')
    limits=[
      ['Accepted all22 descriptive fit (2021Q1-2026Q2), not operational coefficient adoption.',
       'Four seasonal coefficients and one shared fitted weight; fixed and free fits are descriptive.',
       'Seasonal stability does not identify physical booking-to-revenue cohort probabilities.'],
      ['Identification and year sensitivity; six historical year blocks provide limited independent information.',
       'Keep weight and seasonal coefficients jointly paired. Marginal extremes are not coherent cases.',
       'All22 w=0.786478 is descriptive; neither this weight nor new fixed OLS replaces existing K0 policy.'],
      ['Letter-close chronological validation; W1 n14, W2 n10 is nested, not independent replication.',
       'Free-weight promotion FAILED. Matched fixed OLS differs from operational K0 and other chart baselines.',
       'Post-guide/cushion rows use supplied guide: no pre-release guide claim. Upstream GBV/cushion risk omitted.']]
    for i,p in enumerate(assets):
        c.setFillColor(HexColor('#142D44'));c.setFont('Helvetica-Bold',16)
        c.drawString(32,578,f'Accepted L3 exhibit {i+1} | '+['Seasonal calibration','Weight identification','Chronological validation'][i])
        c.setFont('Helvetica',9);c.drawString(32,560,'Source chart preserved in full; accepted implementation does not adopt a financial forecast.')
        iw,ih=ImageReader(str(p)).getSize();scale=min(728/iw,405/ih)
        c.drawImage(str(p),(792-iw*scale)/2,142+(405-ih*scale)/2,width=iw*scale,height=ih*scale,mask='auto')
        c.setFillColor(HexColor('#176C70'));c.setFont('Helvetica-Bold',10);c.drawString(32,122,'Interpretation limits')
        c.setFillColor(HexColor('#142D44'));c.setFont('Helvetica',9)
        for j,line in enumerate(limits[i]):c.drawString(32,106-j*14,line)
        c.setFont('Helvetica',7.5);c.drawString(32,24,f'Bundle 8821961853e4068 | {p.name} | SHA256 {sha(p)[:20]} | {i+1}/3')
        c.showPage()
    c.save()
    if len(PdfReader(str(path)).pages)!=3:raise ValueError('Appendix page count')
    return path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model-dir',type=Path,required=True);ap.add_argument('--revenue-dir',type=Path,required=True)
    ap.add_argument('--run-id',required=True);ap.add_argument('--render-source',type=Path);ap.add_argument('--render-pages',action='store_true');args=ap.parse_args()
    md=args.model_dir.resolve();rd=args.revenue_dir.resolve()
    data=ROOT/'data/processed/forecast_methods/lane4_review_v2'/args.run_id;out=ROOT/'deck/drafts/lane4_v2'/args.run_id
    data.mkdir(parents=True,exist_ok=False);out.mkdir(parents=True,exist_ok=False)
    inputs=data/'inputs';inputs.mkdir()
    sourcepaths=[md/x for x in ['annual.csv','scenario_summary.csv','horizon.json','legacy_replication.json','input_manifest.json','workbook_tieout.json','model_input.json']]
    sourcepaths += [rd/x for x in ['forecast.csv','operating_inputs.csv','expectations_comparison.csv','joint_scenarios.csv','descriptive_joint_extremes.csv','issued_guide_comparison.csv']]
    sourcepaths += [SOURCE/x for x in ['integrity_receipt.json','row_dispositions.csv','accounting_eligibility.json','accounting_interface.csv']]
    sourcepaths += [SOURCE/'bundle/payload/conversion'/x for x in ['chronological_scores.csv','summary.json','claim_ledger.csv']]
    sourcepaths += [ROOT/'deck/drafts/lane4_v1/review_v4/unsigned_card.json']
    sourcepaths += list((SOURCE/'qvs').glob('*.md'))
    # Versioned L2/F public notes support historical evidence only; no new online retrieval.
    for name in ['LANE2_MEMO_READY_CLAIMS.md','ALPHA_F_RNPL.md']:
        candidates=list((ROOT/'docs/revenue-forecast-strategy').rglob(name))
        if candidates:sourcepaths.append(candidates[0])
    manifest=[]
    for i,p in enumerate(sourcepaths):
        if not p.is_file():raise FileNotFoundError(p)
        before=sha(p);dest=inputs/f'{i:02d}_{p.name}';shutil.copyfile(p,dest)
        if sha(dest)!=before or sha(p)!=before:raise ValueError('Changed snapshot input')
        manifest.append({'path':str(p.relative_to(ROOT)),'sha256':before,'snapshot':str(dest.relative_to(data))})
    mrows=read_csv(md/'scenario_summary.csv');annual=read_csv(md/'annual.csv');e=read_csv(rd/'expectations_comparison.csv')
    eligibility=json.loads((SOURCE/'accounting_eligibility.json').read_text());dispositions=read_csv(SOURCE/'row_dispositions.csv')
    checks=verify(mrows,annual,e,eligibility,dispositions);ref=one(e,scenario='review_with_k',quarter='2026Q4',vendor_family='LSEG family',consensus_as_of_timestamp='2026-09-13T15:20Z')
    scores=read_csv(SOURCE/'bundle/payload/conversion/chronological_scores.csv')
    text=args.render_source.read_text(encoding='utf-8') if args.render_source else memo(mrows,annual,ref,scores)
    (out/'review_memo.md').write_text(text,encoding='utf-8');render(out/'review_memo.md',out/'review_memo.pdf')
    card=make_card(out,read_csv(rd/'forecast.csv'),mrows)
    dec=decisions(mrows,ref,annual);write_csv(out/'decision_register.csv',dec)
    (out/'decision_register.md').write_text('# L4 quantified decision register | UNSIGNED\n\n'+markdown_table(dec,[(k,k.replace('_',' ')) for k in dec[0]])+'\n',encoding='utf-8')
    ledger=list(dispositions)
    for r in mrows:
        for k,v in r.items():
            if k in ['scenario','scenario_label']:continue
            period='2026Q4' if k.startswith('q4_') else 'FY2026' if k.startswith('fy26_') else 'FY2027' if k.startswith('fy27_') else '2027-12-31' if k.startswith('december_') else '2027-09-13'
            unit='USD millions' if k.endswith('_musd') else 'million diluted-share proxy' if k.endswith('_m') else 'USD/share' if k.endswith('per_share') or k=='date_only_value_difference' else 'EV / FY27 adjusted EBITDA, x' if k=='exit_multiple' else 'calendar-year fraction' if k=='horizon_fraction' else 'ISO date'
            ledger.append({'row_id':f'MODEL-{r["scenario"]}-{k}','quarter':period,'metric':k,'scenario':r['scenario'],'value':v,
              'units':unit,'information_date':'2026-09-13','integration_disposition':'conditional','financial_eligibility':'conditional_model_output',
              'source_ref':str((md/'scenario_summary.csv').relative_to(ROOT)),'source_row_sha256':sha(md/'scenario_summary.csv'),
              'limitations':'Inherited financial drivers; full-year EBITDA and exact horizon flows; no adopted target/probabilities'})
    model_inputs=json.loads((md/'model_input.json').read_text(encoding='utf-8'))
    for year,items in list(model_inputs['inputs'].items())+[('capital_and_valuation',model_inputs['globals'])]:
        for k,v in items.items():
            unit='USD millions' if k in ['int_income','int_expense','buybacks','net_cash_2q26'] else 'million diluted-share proxy' if k=='shares_2q26' else 'USD/share' if k=='price' else 'multiple, x' if k.startswith('exit_') else 'decimal fraction'
            ledger.append({'row_id':f'ASSUMPTION-{year}-{k}','quarter':year,'metric':k,'scenario':'all_cases','value':v,
             'units':unit,'information_date':'2026-09-07 inherited model; price anchor2026-09-04','integration_disposition':'conditional',
             'financial_eligibility':'inherited_assumption','source_ref':'analysis/src/overnight/13_driver_model.py; '+str((md/'model_input.json').relative_to(ROOT)),
             'source_row_sha256':sha(md/'model_input.json'),'limitations':'Editable inherited base assumption; no new fit or investment adoption'})
    for r in annual:
        for k in ['net_income','cash_taxes','d_unearned','wc_resid','capex','sbc','da','addbacks','fcf','sbc_adj_fcf','buybacks','withholding']:
            ledger.append({'row_id':f'CASH-{r["scenario"]}-{r["year"]}-{k}','quarter':'FY'+r['year'],'metric':k,'scenario':r['scenario'],'value':r[k],
             'units':'USD millions','information_date':'2026-09-13','integration_disposition':'conditional','financial_eligibility':'conditional_model_output',
             'source_ref':str((md/'annual.csv').relative_to(ROOT)),'source_row_sha256':sha(md/'annual.csv'),
             'limitations':'D&A included within total addbacks; customer funds excluded; change in unearned fees assumption not RNPL identification'})
    write_csv(out/'source_assumption_ledger.csv',ledger)
    write_csv(out/'same_basis_expectations.csv',e);write_csv(out/'financial_scenarios.csv',mrows)
    shutil.copyfile(rd/'descriptive_joint_extremes.csv',out/'rejected_free_weight_descriptive_extremes.csv')
    assets=[]
    for name in ['01_seasonal_conversion','02_weight_identification','03_chronological_validation']:
        for suffix in ['.png','.svg']:
            p=SOURCE/'bundle/payload/conversion'/(name+suffix);dest=out/(name+suffix);shutil.copyfile(p,dest)
            if sha(p)!=sha(dest):raise ValueError('Chart bytes changed')
            manifest.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'snapshot':str(dest.relative_to(ROOT))})
            if suffix=='.png':assets.append(dest)
    appendix(out,assets,SOURCE,rd/'descriptive_joint_extremes.csv')
    if args.render_pages:
        for pdf,prefix in [('review_memo.pdf','memo'),('accepted_L3_exhibits.pdf','exhibit')]:
            subprocess.run([str(POPPLER),'-r','110','-png',str(out/pdf),str(data/prefix)],check=True)
    for r in manifest:
        if sha(ROOT/r['path'])!=r['sha256']:raise ValueError('Source changed during build')
    dump(data/'input_manifest.json',manifest);dump(data/'consistency_checks.json',checks)
    dump(data/'receipt.json',{'status':'GENERATED_PENDING_VISUAL_AND_INDEPENDENT_REVIEW','pages':2,'exhibit_pages':3,
        'row_dispositions':len(dispositions),'source_ledger_rows':len(ledger),'model_cases':len(mrows),'financial_checks':len(checks),
        'conversion':CONVERSION,'fx':FX,'model_snapshot':str(md.relative_to(ROOT)),'revenue_snapshot':str(rd.relative_to(ROOT)),
        'new_fitted_parameters':0,'registrations':0,'outputs':[{'file':p.name,'sha256':sha(p)} for p in out.iterdir() if p.is_file()]})
    print(json.dumps({'artifacts':str(out),'data':str(data),'pages':2,'model_cases':len(mrows),'checks':len(checks)},indent=2))
if __name__=='__main__':main()
