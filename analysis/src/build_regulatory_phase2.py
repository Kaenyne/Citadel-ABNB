"""Reproducible identifier matching and versioned public performance panel.

Listings and licence text are self-reported. Matches identify candidate exposure,
not a legal determination. Public performance estimates are not Airbnb revenue.
"""
import json, math, re, sqlite3, zipfile, xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'data/raw/regulatory/phase2'
SUP=ROOT/'data/raw/regulatory/quantification'
OUT=ROOT/'research/regulatory/phase2'
OUT.mkdir(parents=True,exist_ok=True)
BCN_URL='https://opendata-ajuntament.barcelona.cat/data/api/3/action/datastore_search?resource_id=b32fa7f6-d464-403b-8a02-0292a64883bf&limit=20000'
MAUI_URL='https://u.realgeeks.media/mauipropety/240725TVRList_WEB_202407252055590080.pdf'

def read(n):return json.loads((RAW/n).read_text(encoding='utf-8'))
def write(n,obj): (OUT/n).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def extract_pdfs():
 for name in ['maui_minatoya_mirror','maui_26110_cd1','maui_26111_cd1','nyc_cra_2025','hawaii_2026-07','hawaii_2025-12']:
  path=RAW/(name+'.json')
  if not path.exists():path.write_text(json.dumps([dict(page=i+1,text=p.extract_text()) for i,p in enumerate(PdfReader(RAW/(name+'.pdf')).pages)],indent=2),encoding='utf-8')
def dist(a,b,c,d):
 a,b,c,d=map(math.radians,[a,b,c,d]);v=math.sin((a-c)/2)**2+math.cos(a)*math.cos(c)*math.sin((b-d)/2)**2
 return 6371000*2*math.asin(min(1,math.sqrt(v)))
def hut(text):return sorted(set(re.findall(r'HUTB[\s-]*(\d{6})(?!\d)',str(text).upper())))

def barcelona():
 data=read('barcelona_datastore.json')['result'];reg=pd.DataFrame(data['records'])
 assert len(reg)==data['total'], 'Registry pagination incomplete'
 keys={}
 for _,r in reg.iterrows():
  for k in hut(r.NUMERO_REGISTRE_GENERALITAT):keys.setdefault(k,[]).append(r)
 df=pd.read_csv(SUP/'barcelona_2026-06-24_listings.csv',dtype={'id':str})
 rows=[]
 for _,r in df.iterrows():
  ks=hut(r.license);matches=[k for k in ks if k in keys]
  distance=None
  if len(ks)==1 and len(matches)==1:
   rr=keys[matches[0]]
   distance=round(min(dist(r.latitude,r.longitude,float(v.LATITUD_Y),float(v.LONGITUD_X)) for v in rr),1)
  rows.append(dict(listing_id=r.id,short_entire=bool(r.minimum_nights<30 and r.room_type=='Entire home/apt'),
                   reviews_ltm=int(r.number_of_reviews_ltm),licences=';'.join(ks),matched_licences=';'.join(matches),
                   single_registry_match=bool(len(ks)==1 and len(matches)==1),distance_m=distance,
                   near_registry=bool(distance is not None and distance<=300)))
 out=pd.DataFrame(rows);s=out[out.short_entire];m=s[s.single_registry_match];near=m[m.near_registry]
 summary=dict(market='Barcelona',snapshot_date='2026-06-24',registry_resource_modified='2026-05-21',
  registry_rows=len(reg),registry_unique_hutb=len(keys),short_entire_listings=len(s),
  short_entire_single_registry_matches=len(m),distinct_matched_licences=m.matched_licences.nunique(),
  matched_with_review_ltm=int(m.reviews_ltm.gt(0).sum()),within_300m_listings=len(near),
  distinct_matched_licences_with_review_ltm=m[m.reviews_ltm.gt(0)].matched_licences.nunique(),
  within_300m_distinct_licences=near.matched_licences.nunique(),beyond_300m_listings=int(m.distance_m.gt(300).sum()),
  all_listing_registry_matches=int(out.single_registry_match.sum()),
  share_short_entire_matched=len(m)/len(s),
  limitations='Self-reported licence match; not current licence validity. Registry lacks active/cancelled status. Its 10,622 HUTB IDs do not reconcile to the announced 10,101 policy licences. 300m is an analyst sensitivity, not a legal boundary.',
  source_url=BCN_URL)
 write('barcelona_listing_matches.json',rows);write('barcelona_match_summary.json',summary)
 return out,summary

def maui():
 records=[]
 for page in read('maui_minatoya_mirror.json')[:3]:
  for line in page['text'].splitlines():
   m=re.match(r'^(.*?)\s+(\d{12})\s+.*?\s+(\d+)\s*$',line)
   if m:records.append(dict(property_name=m[1],parcel_key=m[2][:8],master_tmk=m[2],listed_units=int(m[3]),source_page=page['page']))
 assert len(records)==104 and sum(x['listed_units'] for x in records)==7167
 props={r['parcel_key']:r for r in records};assert len(props)==len(records)
 proposals={}
 for code in ['26110','26111']:
  text=' '.join(r['text'] for r in read('maui_'+code+'_cd1.json'))
  found=set(''.join(m) for m in re.findall(r'\(2\)\s*(\d)\s*-\s*(\d)\s*-\s*(\d{3})\s*:\s*(\d{3})',text))
  proposals[code]=found
 j=read('maui_26129_parcels.json');assert not j.get('exceededTransferLimit')
 proposals['26129']=set(x['attributes']['cty_tmk'] for x in j['features'])
 for r in records:
  r['proposal_documents']=';'.join(k for k,v in proposals.items() if r['parcel_key'] in v)
  r['phase_out_year']=2029 if r['parcel_key'].startswith('4') else 2031
  r['proposal_status']='Candidate in retrieved proposal; approval and latest amendments unverified' if r['proposal_documents'] else 'No match to retrieved proposal subsets; does not establish exclusion from other amendments'
 df=pd.read_csv(SUP/'hawaii_2026-06-21_listings.csv',dtype={'id':str});df=df[df.neighbourhood_group.eq('Maui')]
 rows=[]
 for _,r in df.iterrows():
  tokens=sorted(set(re.findall(r'(?<!\d)(?:2)?([1-6]\d{11})(?!\d)',str(r.license))))
  matched=[t for t in tokens if t[:8] in props]
  parcel=matched[0][:8] if len(matched)==1 else None
  rows.append(dict(listing_id=r.id,short_entire=bool(r.minimum_nights<30 and r.room_type=='Entire home/apt'),
   reviews_ltm=int(r.number_of_reviews_ltm),tmk_tokens=';'.join(tokens),matched_tmks=';'.join(matched),
   single_parcel_match=parcel is not None,parcel_key=parcel,
   property_name=props[parcel]['property_name'] if parcel else None,
   unit_key=matched[0] if parcel and not matched[0].endswith('0000') else None,
   phase_out_year=props[parcel]['phase_out_year'] if parcel else None,
   proposal_documents=props[parcel]['proposal_documents'] if parcel else None))
 out=pd.DataFrame(rows);s=out[out.short_entire];m=s[s.single_parcel_match]
 summary=dict(market='Maui County',snapshot_date='2026-06-21',registry_date='2024-06-27',registry_parcels=104,registry_units=7167,
  short_entire_listings=len(s),short_entire_matched_listings=len(m),matched_unique_nonzero_unit_keys=m.unit_key.nunique(),
  matched_parcels=m.parcel_key.nunique(),matched_with_review_ltm=int(m.reviews_ltm.gt(0).sum()),
  matched_unique_unit_keys_with_review_ltm=m[m.reviews_ltm.gt(0)].unit_key.nunique(),
  short_entire_without_contiguous_tmk=int(s.tmk_tokens.eq('').sum()),
  west_2029_matched_listings=int(m.phase_out_year.eq(2029).sum()),other_2031_matched_listings=int(m.phase_out_year.eq(2031).sum()),
  listings_in_retrieved_proposal_union=int(m.proposal_documents.ne('').sum()),
  listings_not_in_retrieved_proposal_union=int(m.proposal_documents.eq('').sum()),
  proposal_registry_parcels={k:len(v&set(props)) for k,v in proposals.items()},
  proposal_registry_units={k:sum(props[p]['listed_units'] for p in v if p in props) for k,v in proposals.items()},
  share_short_entire_matched=len(m)/len(s),source_url=MAUI_URL,
  limitations='Historical County list, public mirror. Self-reported contiguous TMKs only; duplicate/incorrect keys possible. Unit exemptions, split zoning, timeshare and parcel portions require review. Proposals are incomplete/versioned subsets, not enacted exemptions; do not subtract their counts as a forecast.')
 write('maui_parcel_register.json',records);write('maui_listing_matches.json',rows);write('maui_match_summary.json',summary)
 return out,summary,records

def read_xlsx_cells(path):
 ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
 with zipfile.ZipFile(path) as z:
  strings=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
  sh=ET.fromstring(z.read('xl/worksheets/sheet1.xml'));out={}
  for cell in sh.findall('s:sheetData/s:row/s:c',ns):
   value=cell.find('s:v',ns)
   if value is not None:out[cell.attrib['r']]=strings[int(value.text)] if cell.attrib.get('t')=='s' else float(value.text)
 return out

def hawaii():
 rows=[];ytd=[]
 for p in sorted(RAW.glob('hawaii_*.xlsx')):
  vintage=p.stem[-7:];y=int(vintage[:4]);cells=read_xlsx_cells(p)
  for addr,label in cells.items():
   if not re.fullmatch(r'A\d+',addr) or not isinstance(label,str):continue
   r=int(addr[1:]);label=label.strip()
   if label not in ['Maui County','State of Hawai‘i','State of Hawai’i','O‘ahu','O’ahu','Island of Hawai‘i','Island of Hawai’i','Kaua‘i','Kaua’i']:continue
   for year,cols in [(y,['B','E','H','K']),(y-1,['C','F','I','L'])]:
    vals=[cells.get(c+str(r)) for c in cols]
    if not all(isinstance(v,(int,float)) for v in vals):continue
    supply,demand,occ,rate=vals
    assert supply>=demand>=0 and rate>0
    assert abs(demand/supply-occ)<1e-8
    target=rows if r<23 else ytd
    target.append(dict(market=label.replace('‘',"'").replace('’',"'"),month=f'{year}-{vintage[-2:]}',
     report_vintage=vintage,supply_nights=supply,demand_nights=demand,occupancy=occ,total_rate_usd=rate,
     implied_total_rate_value_usd=demand*rate,
     basis='All-channel Lighthouse estimate; total rate includes fees; not Airbnb GBV/revenue',
     methodology='2026 observations subject to July 2026 cross-listing restatement; compare vintages before splicing',
     source_url=f'https://files.hawaii.gov/dbedt/economic/tourism/vacation-rental/hawaii-vacation-rental-performance-{vintage}.xlsx'))
 assert rows,'No monthly metrics parsed'
 frame=pd.DataFrame(rows);latest=frame.sort_values('report_vintage').drop_duplicates(['market','month'],keep='last')
 latest['causal_use']='Not a causal estimate; 2026 monthly vintages do not reconcile to July restated YTD'
 checks=[]
 for r in [x for x in ytd if x['report_vintage']=='2026-07' and x['month']=='2026-07']:
  subset=latest[latest.market.eq(r['market'])&latest.month.str.startswith('2026-')]
  s=float(subset.demand_nights.sum())
  checks.append(dict(market=r['market'],monthly_sum_demand=s,july_report_ytd_demand=r['demand_nights'],
   difference=s-r['demand_nights'],reconciles=abs(s-r['demand_nights'])<1,
   interpretation='Use same-report YTD values; do not splice the monthly vintages for causal analysis'))
 write('hawaii_ytd_vintages.json',ytd);write('hawaii_reconciliation.json',checks)
 write('hawaii_monthly_vintages.json',rows);write('hawaii_monthly_latest.json',latest.to_dict('records'))
 return frame,latest

def scenarios(bs,ms):
 rows=[]
 for market,units in [('Barcelona matched licences',bs['distinct_matched_licences']),('Maui matched unit identifiers',ms['matched_unique_nonzero_unit_keys'])]:
  for value in [30000,60000,90000]:
   for recapture in [.25,.5,.75]:
    gross=units*value*.155/1e6;net=gross*(1-recapture);ebitda=net*.7
    rows.append(dict(market=market,matched_identifiers=units,annual_room_value_per_identifier_usd=value,
     fee_rate=.155,recapture=recapture,contribution_margin=.7,retained_legal_scope_fraction=1,
     gross_fee_exposure_musd=gross,net_revenue_loss_musd=net,adjusted_ebitda_loss_musd=ebitda,
     fy25_revenue_pct=net/12241,fy25_margin_compression_bps=(4297/12241-(4297-ebitda)/(12241-net))*10000,
     interpretation='Annualized sensitivity after applicable phase-out. Room value is assumed per matched identifier, averaging zero-production units. No forecast probability. Maui assumes full phase-out before exemptions; Barcelona identifiers may include invalid licences. Rows are alternatives, not additive.'))
 write('matched_cohort_scenarios.json',rows)
 return pd.DataFrame(rows)

def nyc():
 source='https://news.airbnb.com/wp-content/uploads/sites/4/2025/05/The-Costs-of-STR-Restrictions.pdf'
 rows=[dict(market='New York City',period='Sep 2022-Aug 2023',metric='Airbnb guest-nights stayed',value=6560000,unit='guest-nights',source_page=9),
  dict(market='New York City',period='Sep 2023-Aug 2024',metric='Airbnb guest-nights stayed',value=2880000,unit='guest-nights',source_page=9),
  dict(market='New York City',period='Sep 2023-Aug 2024 versus prior year',metric='Reported lost gross host earnings',value=351000000,unit='USD',source_page=16)]
 for r in rows:r.update(source_url=source,method='Airbnb-commissioned CRA report dated Dec 20 2024. LL18 estimate is a YoY comparison, not the synthetic-control estimate used elsewhere. Guest-nights count people times nights. Gross host earnings are not platform fee revenue.',regulatory_revenue_loss=None)
 write('nyc_activity_benchmark.json',rows);return pd.DataFrame(rows)

if __name__=='__main__':
 extract_pdfs();b,bs=barcelona();m,ms,parcels=maui();hv,hl=hawaii();sc=scenarios(bs,ms);nb=nyc()
 with sqlite3.connect(ROOT/'data/processed/abnb_regulatory.sqlite') as con:
  for name,df in [('regulatory_barcelona_listing_matches',b),('regulatory_maui_listing_matches',m),('regulatory_maui_parcels',pd.DataFrame(parcels)),('regulatory_hawaii_monthly_vintages',hv),('regulatory_hawaii_monthly_latest',hl),('regulatory_matched_cohort_scenarios',sc),('regulatory_nyc_activity_benchmark',nb),('regulatory_hawaii_ytd_vintages',pd.DataFrame(json.loads((OUT/'hawaii_ytd_vintages.json').read_text(encoding='utf-8'))))]:
   df.to_sql(name,con,if_exists='replace',index=False)
  assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
 write('phase2_validation.json',dict(barcelona_registry_complete=True,maui_104_parcels_7167_units=True,occupancy_identity_checked=True,sqlite_integrity='ok',hawaii_vintage_rows=len(hv),hawaii_latest_rows=len(hl)))
 print(json.dumps(dict(barcelona=bs,maui=ms,hawaii_rows=len(hl)),indent=2))
