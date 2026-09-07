"""Apply verified follow-up source updates without changing the original factor IDs."""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[2]/'research/regulatory'
sources=json.loads((P/'sources.json').read_text(encoding='utf-8'))
updates=[
 ('REG-S45','Airbnb Q2 2026 10-Q: Spain fine and surety bond','2026-08-06','https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm','company filing'),
 ('REG-S46','BC housing update: active STR listings from 28,000 to just over 23,000','2026-06-02','https://archive.news.gov.bc.ca/releases/news_releases_2024-2028/2026HMA0028-000639.pdf','government'),
 ('REG-S47','Lisbon: cancellation of 6,765 inactive local accommodation registrations',None,'https://informacao.lisboa.pt/en/news/detail/local-authority-cancels-40-of-inactive-local-accommodation-registrations','government'),
 ('REG-S48','Malaga: publication of moratorium on new tourist apartments and hotels on residential land','2026-07-24','https://cadenaser.com/andalucia/2026/07/24/publicada-la-moratoria-para-apartamentos-turisticos-y-hoteles-en-suelo-para-viviendas-en-malaga-ser-malaga/','news'),
]
for sid,title,date,url,typ in updates:
 if not any(s['id']==sid for s in sources):sources.append(dict(id=sid,title=title,publication_date=date,url=url,type=typ,accessed='2026-09-05'))
factors=json.loads((P/'factors.json').read_text(encoding='utf-8')); byid={f['id']:f for f in factors}
f=byid['REG-02'];f['status']='Implemented enforcement; fine disputed; May 2026 surety bond suspends enforcement pending court proceedings'
f['observed_evidence']='Ministry reported 65,122 offending advertisements removed by July 2025. The December 2025 fine was EUR64,055,311. A March 2026 request to stay payment was denied, but the Q2 2026 Form 10-Q subsequently discloses a EUR70m ($80m) surety bond obtained in May 2026 to suspend enforcement pending resolution. Airbnb describes the fine at approximately EUR65m ($76m) and the potential loss as neither probable nor estimable.'
f['limitations']='Ads are not necessarily unique productive properties. Removal orders overlap. Bond face value is not a recognized expense or proof of equal cash payment; bond premium/collateral not quantified here. Do not assume the consumer fine is automatically excluded from adjusted EBITDA.'
f['next_catalyst']='Court resolution, bond conditions, and changes in accounting recognition or cash settlement.'
for sid in ['REG-S45']:
 if sid not in f['source_ids']:f['source_ids'].append(sid)
f=byid['REG-10'];f['observed_evidence']='January 2025 government statement described an approximately 10% decline in entire-home listings from March 2024. A newer June 2, 2026 government release reports active STR listings declining from 28,000 to just over 23,000. These are different metric/time references and neither isolates a causal Airbnb revenue loss.'
if 'REG-S46' not in f['source_ids']:f['source_ids'].append('REG-S46')
f=byid['REG-06']
addition=' Follow-up: city reported cancellation of 6,765 registrations described as inactive because required insurance evidence was missing. This is a separate compliance-cleanup cohort, not 6,765 demonstrated productive Airbnb removals.'
if addition not in f['observed_evidence']:f['observed_evidence']+=addition
if 'REG-S47' not in f['source_ids']:f['source_ids'].append('REG-S47')
f=byid['REG-13']
addition=' July 2026 follow-up: publication on July 24 of a separate moratorium on new hotels and tourist-apartment blocks on residential land, with pipeline exceptions, further constrains replacement accommodation supply.'
if addition not in f['rule']:f['rule']+=addition
if 'REG-S48' not in f['source_ids']:f['source_ids'].append('REG-S48')
(P/'sources.json').write_text(json.dumps(sources,indent=2,ensure_ascii=False),encoding='utf-8')
(P/'factors.json').write_text(json.dumps(factors,indent=2,ensure_ascii=False),encoding='utf-8')
print('Updated four factors and added four follow-up sources.')
