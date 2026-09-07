"""Build the first regulatory exposure inventory, scenarios and SQLite extension."""
from pathlib import Path
import json,sqlite3
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'research/regulatory'
OUT=BASE/'quantification'
RAW=ROOT/'data/raw/regulatory/quantification'
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def save(name,data): (OUT/name).write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')

def main():
 snaps=read(OUT/'listing_snapshots.json'); sm={r['market']:r for r in snaps}
 groups=read(OUT/'neighbourhood_counts.json')
 sources={x['id']:x for x in read(BASE/'sources.json')}
 national=pd.read_csv(RAW/'ine_national.csv',sep=';',dtype=str)
 municipal=pd.read_csv(RAW/'ine_municipal.csv',sep=';',dtype=str)
 num=lambda s:int(s.replace('.',''))
 series=[]
 def addseries(name,d):
  vals={r.Periodo:num(r.Total) for r in d.itertuples() if r.Periodo in ['2026M05','2025M05','2025M11','2024M11']}
  series.append(dict(market=name,unit='Tourist dwellings advertised across platforms (INE)',current_period='2026M05',
   current=vals['2026M05'],prior_period='2025M05',prior=vals['2025M05'],change=vals['2026M05']-vals['2025M05'],
   yoy=vals['2026M05']/vals['2025M05']-1,nov2025=vals.get('2025M11'),nov2024=vals.get('2024M11'),
   source_url='https://www.ine.es/jaxiT3/Tabla.htm?L=0&t='+('39363' if 'Municipios' in d else '39364'),
   inference='Descriptive same-month change. Not a causal policy estimate or Airbnb-specific revenue.'))
 v=national[national['Viviendas y plazas'].eq('Viviendas turísticas') & national.Provincias.isna()]
 addseries('Spain',v[v.iloc[:,1].isna()])
 for name,code in [('Canary Islands','05 '),('Balearic Islands','04 ')]: addseries(name,v[v.iloc[:,1].str.startswith(code,na=False)])
 v=municipal[municipal['Viviendas y plazas'].eq('Viviendas turísticas')]
 for name,code in [('Barcelona','08019 '),('Madrid','28079 '),('Malaga','29067 ')]: addseries(name,v[v.Municipios.str.startswith(code,na=False)])
 codes=['07026 ','07046 ','07048 ','07050 ','07054 ']
 ix=v.Municipios.str.startswith(tuple(codes),na=False)
 ib=v[ix].copy();ib['Total']=ib.Total.map(num)
 agg=ib.groupby('Periodo',as_index=False).Total.sum();agg['Total']=agg.Total.astype(str);agg['Municipios']='Five Ibiza municipalities'
 addseries('Ibiza island',agg)
 save('spain_supply_history.json',series)

 marketrows=[]
 def addmarket(name,r,note='',counttype='Airbnb listing IDs in a public snapshot'):
  marketrows.append(dict(market=name,total=r['total_listings'],short_minimum=r.get('short_minimum_listings'),
   short_entire=r.get('short_entire_home_listings'),as_of=r['snapshot_date'],count_type=counttype,
   scope_note=note,source_url=r['source_url']))
 for key,name in [('new-york-city','New York City'),('barcelona','Barcelona'),('athens','Athens'),('paris','Paris'),
  ('amsterdam','Amsterdam'),('montreal','Montreal'),('madrid','Madrid'),('florence','Florence'),
  ('ireland','Ireland'),('london','London'),('edinburgh','Edinburgh'),('vancouver','Vancouver'),('victoria','Victoria'),
  ('mallorca','Mallorca'),('menorca','Menorca'),('crete','Crete')]:
  addmarket(name,sm[key], 'Minimum <30 nights is a screening measure, not confirmed legal operation or actual booked stays.')
 for key,geo,name in [('lisbon','Lisboa','Lisbon municipality'),('porto','Porto','Porto municipality'),
                       ('hawaii','Maui','Maui County'),('thessaloniki','Thessaloniki','Thessaloniki municipality')]:
  r=next(x for x in groups if x['market']==key and x['geography'].casefold()==geo.casefold())
  addmarket(name,r,'Filtered to municipality/county in Inside Airbnb. Remaining legal subareas require finer matching.')
 for s in series:
  if s['market'] not in ['Barcelona','Madrid']:
   addmarket(s['market']+' (INE)',dict(total_listings=s['current'],snapshot_date='2026-05',source_url=s['source_url']),
    'Multi-platform tourist dwellings. Not an Airbnb listing denominator.',s['unit'])
 extras=[('Portugal',119147,'2026-06-11','RNAL active registrations, reported by ALEP via ECO','Includes potentially inactive businesses; 37,000 lacked insurance evidence.',
 'https://eco.sapo.pt/2026/06/11/mais-de-dez-mil-alojamentos-locais-encerrados-pelos-municipios/'),
 ('Greece',203122,'2026-03','Finalized property registrations, ELSTAT','Not unique Airbnb listings or all economically active units.','https://www.statistics.gr/documents/20181/9520c869-6216-4180-2282-d92150044d23'),
 ('Scotland',32317,'2025-12-31','Licences or exemptions in operation','Includes B&B and other accommodation; not Airbnb only.','https://www.gov.scot/news/short-term-lets-licensing-statistics-to-31-december-2025/'),
 ('British Columbia',23000,'2026-06-02','Approximate active STR listings, government report','Source says just over 23,000, down from 28,000; platform mix and exact measurement dates unspecified.','https://archive.news.gov.bc.ca/releases/news_releases_2024-2028/2026HMA0028-000639.pdf'),
 ('Budapest district VI',2226,'2024-08','Legal private and other accommodation establishments','Historical affected policy cohort; current Airbnb download failed.','https://nepszava.hu/3245205_airbnb-terezvaros-betiltas'),
 ('England',None,'2026-09-05','National Airbnb total unresolved','London is only a partial proxy, not England.','https://www.gov.uk/guidance/letting-out-a-self-catering-holiday-home-in-england-rules-and-regulations'),
 ('European Union',None,'2026-09-05','EU Airbnb total unresolved','Must sum distinct EU destinations from a consistent licensed dataset. EMEA is not EU.','https://single-market-economy.ec.europa.eu/news/new-rules-bring-increased-transparency-short-term-rentals-sector-2026-05-20_en')]
 for name,n,date,unit,note,url in extras: addmarket(name,dict(total_listings=n,snapshot_date=date,source_url=url),note,unit)
 save('market_inventory.json',marketrows)
 mm={r['market']:r for r in marketrows}

 # Counts are explicitly identified as events, registered units, or broad screens.
 mapping={
 1:('New York City','Enforced registration',17900,'Historical short-stay listing reduction: 22,500 to 4,600, June–Sep 2023 (AirDNA via Skift).','Existing loss already in current base; current 5,813 short-minimum listings include hosted stays and hotels.','NYC historical','https://skift.com/2023/09/13/airbnbs-nyc-listings-fall-77-big-hotelier-sees-tailwind/'),
 2:('Spain (INE)','Delisting enforcement',65122,'Reported Airbnb ads removed in July 2025; overlaps earlier 65,935 order.','Need ad-to-unit deduplication, prior activity, reinstatement and actual displaced booked nights.','Spain combined',None),
 3:('Spain (INE)','Registration and legal reversal',None,'No verified net removals attributable only to the national register.','May 2026 judgment annulled material registry procedures. Do not reuse original blanket delisting case.','Spain combined',None),
 4:('Athens','Entry freeze and transfer attrition',None,'Districts 1–3 affected. Immediate mandated closure of grandfathered stock: zero from freeze alone.','14,308 citywide short-minimum listings are an outer screen; need district GIS, transfers and new-entry counterfactual.','Athens',None),
 5:('Thessaloniki municipality','Entry freeze and transfer attrition',None,'First municipal community only; existing stock generally survives.','Need first-community boundary and registration dates. City has 4,373 short-minimum listings.','Thessaloniki',None),
 6:('Lisbon municipality','Containment, new registration and transfer limits',None,'12,227 entire-home short-minimum listings are a broad city screen.','Match containment areas, exceptions and transfer/renewal events; add insurance cleanup only once.','Lisbon combined',None),
 7:('Portugal','Partly reversed national restrictions',None,'No unchanged nationwide ban or verified future forced-removal count.','Current RNAL universe is not operating Airbnb supply. Municipal restrictions persist.','Portugal combined',None),
 8:('Paris','Annual cap: 120 to 90 nights',None,'54,280 entire-home short-minimum listings are an outer screen, not verified primary residences.','Count primary homes previously booked >90 nights; lost nights=min(B,120)-min(B,90).','Paris combined',None),
 9:('Amsterdam','Selected-area cap: 30 to 15 nights',None,'Only eight covered neighbourhoods; 8,421 entire-home short-minimum listings citywide.','Need exact polygons, holiday-home vs B&B licence and pre-rule booked nights >15.','Amsterdam',None),
 10:('British Columbia','Principal residence and registry',None,'Active STR listings fell from 28,000 to just over 23,000 per June 2026 government report.','Nearly 5,000 net contraction is descriptive; identify exemptions, compliance and Airbnb share.','British Columbia','https://archive.news.gov.bc.ca/releases/news_releases_2024-2028/2026HMA0028-000639.pdf'),
 11:('Montreal','Seasonal primary-home rentals',None,'4,159 entire-home short-minimum listings are an outer screen.','Must separate primary from commercial licences and count bookings outside Jun 10–Sep 10.','Montreal',None),
 12:('Madrid','Residential land-use enforcement',None,'13,903 entire-home short-minimum listings across city; INE dwellings down 28.9% YoY.','Need historic-centre boundary, building use and operating permissions; supply trend is not a causal effect.','Spain combined',None),
 13:('Malaga (INE)','New-entry moratorium',None,'8,288 tourist dwellings observed by INE in May 2026 across platforms.','Airbnb snapshot download failed. July 2026 also restricted new hotels/apartment blocks on residential land, subject to pipeline exceptions.','Spain combined','https://cadenaser.com/andalucia/2026/07/24/publicada-la-moratoria-para-apartamentos-turisticos-y-hoteles-en-suelo-para-viviendas-en-malaga-ser-malaga/'),
 14:('Florence','Zoning and licence transition',None,'10,640 entire-home short-minimum listings citywide; 9,903 listings of all types in Centro Storico.','Centro Storico is not an exact A1/A3/A4 match; identify property start dates and May 2028 transition cohort.','Florence',None),
 15:('Budapest district VI','Zero-day rule for covered accommodation',2226,'Historical registered private/other accommodation cohort; not Airbnb-only listings.','Current surviving hotels, reclassification and actual closure rate need matching.','Budapest district VI',None),
 16:('Canary Islands (INE)','Planning restrictions and transition',None,'48,356 multi-platform tourist dwellings in May 2026; subset not determined.','Map island/municipal planning, residential use, grandfathering and expiry before any removal assumption.','Spain combined',None),
 17:('European Union','Data sharing and registration checks',None,'Compliance scope is broad; no EU-wide numerical listing cap.','Quantify local enforcement made possible, then subtract overlap with city/national rules.','EU overlay',None),
 18:('Spain (INE)','Condominium approval for new activity',None,'New activity under national condominium law; no universal cancellation of existing stock.','Need new applicants, votes, grandfathered status and separate Catalonia regime.','Spain combined',None),
 19:('Scotland','Licensing',None,'32,317 licences/exemptions operating at Dec 2025; no verified net Airbnb listing loss.','Licence totals include renewals and lodging types; official source advises against time comparisons.','Scotland',None),
 20:('Greece','Operating standards',None,'203,122 registered properties nationally; noncompliant subset unknown.','Join light/ventilation, insurance and inspection outcomes. Do not add Athens twice.','Greece combined',None),
 21:('Ibiza island (INE)','Illegal-supply enforcement',None,'INE tourist dwellings: 2,314 May 2026 vs 3,158 May 2025.','Distinct from industry bed-capacity metric. Need Airbnb-only cohort and enforcement versus seasonality/market demand.','Spain combined',None),
 22:('Barcelona','2028 licence non-renewal',10101,'Tourist-apartment licences in city policy, across platforms.','Airbnb screen: 6,698 entire-home short-minimum listings with HUTB text; not an audited legal match.','Spain combined',None),
 23:('Maui County','Apartment-zone phase-out: 2029/2031',6208,'Active Minatoya units as of May 29, 2024, across channels.','4,519 rezoning candidates may reduce exposure; intersect parcel lists before subtracting.','Maui',None),
 24:('Ireland','December 2026 registration',None,'32,456 Airbnb listings; 32,230 minimum <30. Actual rule includes stays <=21 nights.','Join registration/planning eligibility; unknown failures do not mean all listings disappear.','Ireland',None),
 25:('European Union','Draft framework',None,'Affected housing-stress areas and local actions not determined.','No incremental losses booked until legal scope, probability and implementation dates are specified.','EU overlay',None),
 26:('Paris','Further proposed professional restrictions',None,'Professional multi-owner cohort not identified.','Do not reuse primary-residence cap population without deduplication.','Paris combined',None),
 27:('England','Registry implementation uncertain',None,'National Airbnb denominator and compliance-failure cohort unresolved.','London count available separately; cannot extrapolate to England.','England',None),
 28:('Lisbon municipality','Referendum blocked',0,'Zero incremental mandated removals from the blocked referendum.','Policy could re-emerge; distinguish from operative containment and insurance enforcement.','Lisbon combined',None),
 29:('Spain (INE)','Activism',0,'Zero removals attributable to a separate enacted measure in this factor.','Activism changes scenario probability; do not add existing Spain/Barcelona removals again.','Spain combined',None),
 30:('Canary Islands (INE)','Activism',0,'Zero separate legal removal count.','Later law counted under REG-16; no duplicate loss from protest.','Spain combined',None),
 31:('Portugal','Activism',0,'Zero separate legal removal count.','Track conversion into an operative measure; no arbitrary haircut on all Portugal.','Portugal combined',None),
 32:('Greece','Social pressure',0,'Zero separate legal removal count.','Track concrete proposals; existing restrictions counted under REG-04/05/20.','Greece combined',None),
 }
 rules=[]
 for f in read(BASE/'factors.json'):
  no=int(f['id'].split('-')[1]);market,mechanism,n,definition,gap,overlap,extra=mapping[no];m=mm[market]
  urls=[sources[s]['url'] for s in f['source_ids']]
  if extra:urls.append(extra)
  rules.append(dict(factor_id=f['id'],tier=f['tier'],jurisdiction=f['jurisdiction'],market=market,
   total_inventory=m['total'],inventory_type=m['count_type'],inventory_date=m['as_of'],
   affected_reported_count=n,affected_count_definition=definition,mechanism=mechanism,status=f['status'],
   next_data_needed=gap,overlap_group=overlap,airbnb_revenue_loss_disclosed_musd=None,
   guidance_assessment='No quantified jurisdiction-specific guidance bridge found. Implemented effects may be reflected in operating trends; not separately confirmed.',
   sources=' ; '.join(dict.fromkeys([m['source_url']]+urls))))
 rules.append(dict(factor_id='REG-06-SUPP',tier=1,jurisdiction='Portugal / Lisbon insurance cleanup',market='Lisbon municipality',
   total_inventory=mm['Lisbon municipality']['total'],inventory_type=mm['Lisbon municipality']['count_type'],inventory_date='2026-06-23',
   affected_reported_count=6765,affected_count_definition='Cancelled registrations reported by city in Feb 2026 as inactive. Not 6,765 revenue-producing Airbnb units.',
   mechanism='Insurance evidence / inactive registry cleanup',status='Implemented; supplemental evidence for REG-06/07',
   next_data_needed='Match cancelled licences to active Airbnb IDs before assigning revenue loss.',overlap_group='Lisbon combined',
   airbnb_revenue_loss_disclosed_musd=None,guidance_assessment='No quantified guidance adjustment found.',
   sources='https://informacao.lisboa.pt/en/news/detail/local-authority-cancels-40-of-inactive-local-accommodation-registrations'))
 save('factor_exposures.json',rules)

 guide_path=ROOT/'data/processed/abnb_revenue_guidance_vs_actual.csv'
 archived_guide=OUT/'guidance_input_snapshot.json'
 if guide_path.exists():
  guide=pd.read_csv(guide_path)
  save('guidance_input_snapshot.json',json.loads(guide.to_json(orient='records')))
 else:
  # Preserve the already ingested data if the parallel project reorganizes its source file.
  if not archived_guide.exists():
   prior=read(OUT/'guidance_history.json')
   cols=['guided_quarter','issued_on_call','guide_low_musd','guide_high_musd','guide_mid_musd',
         'range_width_pct_of_mid','actual_musd','actual_vs_mid_pct','actual_vs_high_pct']
   save('guidance_input_snapshot.json',[{k:r.get(k) for k in cols} for r in prior])
  guide=pd.DataFrame(read(archived_guide))
 costs=pd.read_csv(ROOT/'data/processed/abnb_quarterly_costlines.csv')
 costs['guided_quarter']=costs.quarter.map(lambda x:'20'+x[-2:]+'Q'+x[0])
 hist=guide[guide.guided_quarter.ge('2023Q3')].merge(costs[['guided_quarter','adjusted_ebitda_musd','adj_ebitda_margin_pct']],on='guided_quarter',how='left')
 notes={
 '2023Q3':'NYC enforcement began in September. Pre-enforcement guidance; only one month partly affected.',
 '2023Q4':'First full quarter after NYC enforcement. Actual revenue beat issued range; not proof of no NYC loss.',
 '2024Q1':'NYC present in operating base. Quarterly margin is seasonal.',
 '2024Q2':'BC principal-residence rule began May 1. Company margin does not isolate provincial impact.',
 '2024Q3':'NYC anniversary and Paris Olympics confound simple before/after comparisons.',
 '2024Q4':'Portugal national rules partly reversed. No attributed regulatory loss disclosed.',
 '2025Q1':'Athens freeze and Paris 90-night cap began. No separate revenue/margin bridge.',
 '2025Q2':'Spanish delisting orders and BC registry. Strong revenue does not identify counterfactual loss.',
 '2025Q3':'Spanish registry/delistings; revenue was within guidance. Madrid hotel pilot discussed.',
 '2025Q4':'Spain fine headlines. FY25 filing says potential loss neither probable nor estimable.',
 '2026Q1':'Budapest VI rule in force; policy risk remains in base. Hotels target constrained supply.',
 '2026Q2':'Spain surety bond in May; Amsterdam tighter cap. FY26 revenue and margin outlook raised.',
 '2026Q3':'Guidance only, no actual. FY26 growth at least mid teens and adjusted EBITDA margin at least 35.5%.'}
 hist['policy_context']=hist.guided_quarter.map(notes)
 hist['causal_inference']='No quantified causal attribution from consolidated results.'
 hist['source_url']=hist.guided_quarter.map(lambda q:'https://investors.airbnb.com/financials/default.aspx')
 hist.loc[hist.guided_quarter.eq('2026Q3'),'source_url']='https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm'
 save('guidance_history.json',json.loads(hist.to_json(orient='records')))

 # Annualized illustrations; every unit-economics parameter is an assumption, not an estimate.
 # No summation: scenarios overlap and refer to different implementation years.
 scenarios=[
  ('Illustrative unit conversion',10000,1,1,150,200,.155,.50,.70,1,'Neutral scale example; 10,000 actual productive Airbnb listings assumed lost.'),
  ('Barcelona licence cohort',10101,.65,.85,180,220,.155,.50,.70,1,'Full-year after 2028 non-renewal, conditional on implementation. Platform share/activity/nights/ADR/recapture assumed.'),
  ('Barcelona observed HUTB screen',6698,1,.85,180,220,.155,.50,.70,1,'Alternative to licence cohort, not additive. Scraped IDs not validated licences or distinct homes.'),
  ('Maui phase-out before rezoning',6208,.60,1,210,375,.155,.50,.70,1,'Annualized only after respective 2029/2031 phases. Platform share and activity at future date unverified.'),
  ('Maui with assumed 60% exemption',6208,.60,1,210,375,.155,.50,.70,.40,'Alternative scenario: assume 60% of active cohort exempt/reclassified. Not 4,519 automatically subtracted.'),
  ('Spain reported removed ads',65122,1,.35,150,180,.155,.50,.70,1,'Historical reconstruction illustration, not new future guidance downside. 35% unique productive net-lost share assumed.'),
  ('Paris 10,000 cap-binding homes',10000,1,1,30,220,.155,.50,.70,1,'Hypothetical subset previously at 120 nights. Lose 30 nights each, not the full listing.'),
  ('Athens 1,000 blocked new listings',1000,1,1,100,140,.155,.50,.70,1,'Hypothetical annual foregone entrants after partial-year ramp; no existing stock ban assumed.'),
 ]
 sr=[]
 for name,count,share,productive,nights,adr,fee,recapture,margin,enforced,note in scenarios:
  gross=count*share*productive*nights*adr*fee*enforced/1e6;net=gross*(1-recapture)
  sr.append(dict(scenario=name,cohort_count=count,airbnb_channel_share=share,unique_productive_share=productive,
    lost_nights_per_productive_listing=nights,room_adr_usd=adr,fee_on_room_value=fee,revenue_recapture=recapture,
    incremental_contribution_margin=margin,net_scope_enforced_share=enforced,gross_revenue_musd=gross,
    net_revenue_loss_musd=net,ebitda_loss_musd=net*margin,fy25_revenue_share=net/12241,
    standalone_margin_after=(4297-net*margin)/(12241-net),notes=note))
 save('illustrative_scenarios.json',sr)
 with sqlite3.connect(ROOT/'data/processed/abnb_regulatory.sqlite') as db:
  for table,data in [('regulatory_market_inventory',marketrows),('regulatory_factor_exposure',rules),
    ('regulatory_supply_history',series),('regulatory_guidance_history',json.loads(hist.to_json(orient='records'))),
    ('regulatory_illustrative_scenarios',sr)]:
   pd.DataFrame(data).to_sql(table,db,if_exists='replace',index=False)
  assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
 assert len(rules)==33 and len({r['factor_id'] for r in rules})==33
 assert all(r['unique_listing_ids']==r['total_listings'] for r in snaps)
 assert all(r['short_entire_home_listings']<=r['short_minimum_listings']<=r['total_listings'] for r in snaps)
 print('Built',len(marketrows),'inventory rows,',len(rules),'factor rows,',len(series),'Spanish histories,',len(hist),'guidance rows.')
 print('Scenarios:',[(s['scenario'],round(s['net_revenue_loss_musd'],1)) for s in sr])
 print('Spanish YoY:',[(s['market'],s['current'],round(s['yoy']*100,1)) for s in series])

if __name__=='__main__':main()
