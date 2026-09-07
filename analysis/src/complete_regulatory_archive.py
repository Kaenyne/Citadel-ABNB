"""Fetch remaining public-source documents; never sends credentials externally."""
from pathlib import Path
import hashlib
import json
import re
from html.parser import HTMLParser
import requests

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'data/raw/regulatory/transcripts'

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'): self.skip += 1
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip and data.strip(): self.parts.append(data.strip())

if __name__ == '__main__':
    url='https://www.fool.com/earnings/call-transcripts/2026/08/13/airbnb-abnb-q2-2026-earnings-call-transcript/'
    r=requests.get(url,timeout=30); r.raise_for_status()
    parser=TextParser(); parser.feed(r.text)
    text='\n'.join(parser.parts)
    if 'Full Conference Call Transcript' not in text or 'Brian Chesky' not in text:
        raise RuntimeError('Transcript verification failed')
    (OUT/'2026-Q2.html').write_text(r.text,encoding='utf-8')
    (OUT/'2026-Q2.txt').write_text(text,encoding='utf-8')
    manifest=json.loads((OUT/'manifest.json').read_text())
    latest=next(x for x in manifest if x['period']=='2026-Q2')
    latest.update(status='downloaded_public_html_fallback',url=url,local_path='data/raw/regulatory/transcripts/2026-Q2.html',http_status=r.status_code,sha256=hashlib.sha256((OUT/'2026-Q2.html').read_bytes()).hexdigest(),provider='Motley Fool; not LSEG full text')
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Q2 2026 full transcript saved and verified')
    src=json.loads((ROOT/'research/regulatory/sources.json').read_text())
    docs=ROOT/'data/raw/regulatory/documents'; docs.mkdir(parents=True,exist_ok=True)
    for item in src:
        if item['id'] not in ['REG-S02','REG-S07','REG-S10','REG-S11','REG-S21','REG-S44']: continue
        try:
            response=requests.get(item['url'],timeout=20)
            response.raise_for_status()
            (docs/(item['id']+'.html')).write_text(response.text,encoding='utf-8')
            print(item['id'],'saved')
        except requests.RequestException as exc:
            print(item['id'],type(exc).__name__)
