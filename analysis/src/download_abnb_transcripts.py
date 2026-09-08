"""Download company-hosted ABNB transcripts, preserving page locators and hashes."""
import concurrent.futures
import hashlib
import io
import json
import re
from pathlib import Path
import requests
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data/raw/regulatory/transcripts'
OUT.mkdir(parents=True, exist_ok=True)

def download(period):
    year, quarter = period.split('-')
    url = f'https://s26.q4cdn.com/656283129/files/doc_financials/{year}/{quarter.lower()}/Airbnb-{quarter}-{year[2:]}-Earnings-Call-Transcript.pdf'
    r = requests.get(url, timeout=30)
    item = {'period': period, 'url': url, 'http_status': r.status_code}
    if r.ok and r.content.startswith(b'%PDF'):
        reader = PdfReader(io.BytesIO(r.content))
        (OUT / f'{period}.pdf').write_bytes(r.content)
        pages = [{'page': i+1, 'text': page.extract_text()} for i, page in enumerate(reader.pages)]
        (OUT / f'{period}.json').write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding='utf-8')
        item.update(status='downloaded', pages=len(pages), sha256=hashlib.sha256(r.content).hexdigest(), local_path=f'data/raw/regulatory/transcripts/{period}.pdf')
        item['keyword_pages'] = [p['page'] for p in pages if re.search(r'regulat|Spain|Barcelona|New York|housing|tourism|policy', p['text'], re.I)]
    else:
        item['status'] = 'not_downloaded'
    print(f'{period}: {item["status"]}', flush=True)
    return item

if __name__ == '__main__':
    periods = [f'{y}-Q{q}' for y in range(2023,2027) for q in range(1,5) if (y,q) <= (2026,2)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        manifest = list(pool.map(download, periods))
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    r = requests.get('https://investors.airbnb.com/financials/default.aspx', timeout=25)
    (OUT / 'ir_financials.html').write_text(r.text, encoding='utf-8')
    print('IR page status:',r.status_code)
