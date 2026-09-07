"""Workstream 10. Reads data/raw/xbrl/ABNB_companyfacts.json for the list of 10-Q/10-K accessions,
fetches each filing's XBRL instance from EDGAR and extracts revenue by srt:StatementGeographicalAxis
(US vs international; country split in 10-Ks). Writes data/processed/overnight/10_xbrl_revenue_geography.csv.
Run: py -3.13 analysis/src/overnight/10_fetch_xbrl_geography.py
"""
import json, re, time, sys, os
import requests, pandas as pd
UA={'User-Agent':'citadel-abnb research ksurapaneni@ufl.edu'}
ROOT=os.path.dirname(os.path.abspath(__file__))+'/../../..'
j=json.load(open(f'{ROOT}/data/raw/xbrl/ABNB_companyfacts.json'))
facts=j['facts']['us-gaap']['RevenueFromContractWithCustomerExcludingAssessedTax']['units']['USD']
accns=sorted({(f['accn'],f['form'],f['filed']) for f in facts if f['form'] in ('10-Q','10-K')}, key=lambda x:x[2])
cik='1559720'
rows=[]
for accn,form,filed in accns:
    nodash=accn.replace('-','')
    idx=f'https://www.sec.gov/Archives/edgar/data/{cik}/{nodash}/'
    r=requests.get(idx+'index.json',headers=UA,timeout=60); time.sleep(0.15)
    if r.status_code!=200:
        print('index fail',accn,r.status_code); continue
    items=[it['name'] for it in r.json()['directory']['item']]
    inst=[n for n in items if re.match(r'abnb-\d{8}(_htm)?\.xml$',n) and 'cal' not in n and 'def' not in n and 'lab' not in n and 'pre' not in n]
    if not inst:
        inst=[n for n in items if n.endswith('_htm.xml')]
    if not inst:
        print('no instance',accn,items[:10]); continue
    x=requests.get(idx+inst[0],headers=UA,timeout=120).text; time.sleep(0.15)
    # contexts
    ctx={}
    for m in re.finditer(r'<(?:xbrli:)?context id="([^"]+)">(.*?)</(?:xbrli:)?context>',x,re.S):
        cid,body=m.group(1),m.group(2)
        st=re.search(r'startDate>([^<]+)<',body); en=re.search(r'endDate>([^<]+)<',body)
        dims=re.findall(r'explicitMember dimension="([^"]+)">([^<]+)<',body)
        ctx[cid]=dict(start=st.group(1) if st else None,end=en.group(1) if en else None,dims=dims)
    for m in re.finditer(r'<us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax([^>]*)>([^<]+)<',x):
        attrs,val=m.group(1),m.group(2)
        cid=re.search(r'contextRef="([^"]+)"',attrs).group(1)
        c=ctx.get(cid)
        if not c: continue
        geo=[v for d,v in c['dims'] if 'StatementGeographicalAxis' in d]
        other=[(d,v) for d,v in c['dims'] if 'StatementGeographicalAxis' not in d]
        if not geo or other: continue
        rows.append(dict(accn=accn,form=form,filed=filed,start=c['start'],end=c['end'],geo=geo[0],value_usd=float(val)))
    print(accn,form,filed,inst[0],len([r for r in rows if r['accn']==accn]))
df=pd.DataFrame(rows).drop_duplicates()
df.to_csv(f'{ROOT}/data/processed/overnight/10_xbrl_revenue_geography.csv',index=False)
print(df.groupby(['form','geo']).size())
