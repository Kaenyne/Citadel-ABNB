"""Retrieve published statistical tables and filing evidence for quantification."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,re
from html.parser import HTMLParser
import requests
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'data/raw/regulatory/quantification'
URLS={
 'ine_national.csv':'https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/39364.csv',
 'ine_municipal.csv':'https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/39363.csv',
 'abnb_2025_10k.pdf':'https://stocklight.com/stocks/us/nasdaq-abnb/airbnb/annual-reports/nasdaq-abnb-2026-10K-26626095.pdf',
 'greece_2025.pdf':'https://www.statistics.gr/documents/20181/9520c869-6216-4180-2282-d92150044d23',
 'abnb_2026q2_10q.html':'https://cdn.yahoofinance.com/prod/sec-filings/0001559720/000155972026000027/abnb-20260630.htm',
}
def pull(item):
 name,url=item; p=OUT/name
 try:
  if not p.exists():
   r=requests.get(url,timeout=60);r.raise_for_status();p.write_bytes(r.content)
  if name.endswith('.pdf'):
   pages=[dict(page=i+1,text=p.extract_text()) for i,p in enumerate(PdfReader(p).pages)]
   p.with_suffix('.json').write_text(json.dumps(pages,indent=2),encoding='utf-8')
  print(name,p.stat().st_size,flush=True)
 except Exception as e: print(name,type(e).__name__,flush=True)
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=4) as ex: list(ex.map(pull,URLS.items()))
