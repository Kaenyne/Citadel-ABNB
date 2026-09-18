"""Pull every Form 4 / 4/A filed under Airbnb (CIK 1559720) since 2022-09 from EDGAR, parse non-derivative
transactions, write form4_transactions.csv. Run: py -3.13 pull_form4.py  (requests only; ~10 req/s; ~4 min)."""
import json, os, re, time, csv, sys, urllib.request, xml.etree.ElementTree as ET
HERE=os.path.dirname(os.path.abspath(__file__)); SRC=os.path.join(HERE,'..','sources'); RAW=os.path.join(SRC,'form4_xml'); os.makedirs(RAW,exist_ok=True)
UA={'User-Agent':'Citadel pitch research krishangbro@gmail.com','Accept-Encoding':'gzip, deflate'}
def get(url):
    req=urllib.request.Request(url,headers=UA)
    for k in range(4):
        try:
            with urllib.request.urlopen(req,timeout=60) as r:
                data=r.read()
                if r.headers.get('Content-Encoding')=='gzip':
                    import gzip; data=gzip.decompress(data)
                return data
        except Exception as e:
            time.sleep(2+2*k); err=e
    raise err
sub=json.load(open(os.path.join(SRC,'sec_submissions_CIK1559720_20260917.json')))
lists=[sub['filings']['recent']]
for f in sub['filings'].get('files',[]):
    p=os.path.join(SRC,f['name'])
    if not os.path.exists(p): open(p,'wb').write(get('https://data.sec.gov/submissions/'+f['name'])); time.sleep(0.15)
    lists.append(json.load(open(p)))
fil=[]
for L in lists:
    for i in range(len(L['form'])):
        if L['form'][i] in ('4','4/A') and L['filingDate'][i]>='2022-09-01':
            fil.append((L['filingDate'][i],L['accessionNumber'][i],L['primaryDocument'][i],L['form'][i]))
fil.sort(); print(len(fil),'Form 4 filings since 2022-09-01')
rows=[]
def txt(el,path):
    x=el.find(path); return (x.text or '').strip() if x is not None else ''
for fd,acc,doc,form in fil:
    accn=acc.replace('-',''); xmlname=doc.split('/')[-1]
    url=f'https://www.sec.gov/Archives/edgar/data/1559720/{accn}/{xmlname}'
    p=os.path.join(RAW,f'{acc}_{xmlname}')
    if not os.path.exists(p):
        try: open(p,'wb').write(get(url)); time.sleep(0.12)
        except Exception as e: print('FAIL',acc,e); continue
    try: root=ET.fromstring(open(p,'rb').read())
    except Exception as e: print('PARSEFAIL',acc,e); continue
    owner=txt(root,'reportingOwner/reportingOwnerId/rptOwnerName'); rel=root.find('reportingOwner/reportingOwnerRelationship')
    title=txt(rel,'officerTitle') if rel is not None else ''; isdir=txt(rel,'isDirector') if rel is not None else ''; isoff=txt(rel,'isOfficer') if rel is not None else ''; isten=txt(rel,'isTenPercentOwner') if rel is not None else ''
    foot={f.get('id'):(f.text or '').strip() for f in root.findall('footnotes/footnote')}
    for t in root.findall('nonDerivativeTable/nonDerivativeTransaction'):
        code=txt(t,'transactionCoding/transactionCode'); d=txt(t,'transactionDate/value')
        sh=txt(t,'transactionAmounts/transactionShares/value'); pr=txt(t,'transactionAmounts/transactionPricePerShare/value'); ad=txt(t,'transactionAmounts/transactionAcquiredDisposedCode/value')
        own=txt(t,'ownershipNature/directOrIndirectOwnership/value'); post=txt(t,'postTransactionAmounts/sharesOwnedFollowingTransaction/value')
        fids=[x.get('id') for x in t.iter('footnoteId')]
        rows.append(dict(filing_date=fd,accession=acc,form=form,owner=owner,title=title,is_director=isdir,is_officer=isoff,is_10pct=isten,txn_date=d,code=code,acq_disp=ad,shares=sh,price=pr,value=(float(sh)*float(pr) if sh and pr else ''),ownership=own,post_shares=post,footnotes=' | '.join(foot.get(i,'') for i in fids)[:1500]))
with open(os.path.join(HERE,'form4_transactions.csv'),'w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows),'transactions written')
