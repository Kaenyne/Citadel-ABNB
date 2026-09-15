"""Record completed two-page text/source and visual QA; refuses an existing receipt."""
import hashlib
import json
from pathlib import Path
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[5]
OUT=ROOT/'output/pdf/gbv-event-20260915'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((OUT/'manifest.json').read_text())
for name,digest in manifest['source_hashes'].items():assert sha(ROOT/name)==digest
for name,digest in manifest['artifacts'].items():assert sha(OUT/name)==digest
reader=PdfReader(OUT/'ABNB_GBV_two_pager.pdf')
assert len(reader.pages)==2
links=[]
for page in reader.pages:
    for annotation in page.get('/Annots',[]):
        action=annotation.get_object().get('/A',{})
        if action.get('/URI'):links.append(str(action['/URI']))
assert any('sec.gov/Archives/edgar' in x for x in links)
for n in (1,2):assert (OUT/f'page-{n}.png').stat().st_size>10000
receipt={
    'status':'PASS author source, text, page-count and rendered visual QA; parent independent review requested',
    'page_count':2,'charts':3,'visual_review':'Both final 125-dpi Poppler PNGs inspected. Clean margins, aligned table and charts, readable labels, no clipping, overlap or missing glyphs.',
    'sources':'Every source and authored-output hash rechecked against the build manifest; clickable SEC primary citation confirmed.',
    'metric_labels':'Current conditional EWM path separated from ex-COVID historical candidate. Historical raw and interval metrics named. Daily price legs are not call-only moves. All 23 events included.',
    'attempts':[{'attempt':1,'status':'stopped before PDF creation','reason':'Paragraph height 32.274 points exceeded 31-point limit; empty directory only removed'},
                {'attempt':2,'status':'passed','repair':'Shortened boundary prose and set 10-point leading'}],
    'operation_marker':'Successful exactly once before authoring; expected output count 1, format pdf',
    'render_command':'pdftoppm -png -r 125 output/pdf/gbv-event-20260915/ABNB_GBV_two_pager.pdf output/pdf/gbv-event-20260915/page',
    'primary_links':links,
    'files':{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file()},
    'claim_closure_sha256':sha(ROOT/'data/processed/forecast_methods/gbv_event_v1/sources_v1/closure_v3.json'),
}
with (OUT/'qa_receipt_v1.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2)
print(json.dumps({'status':receipt['status'],'pdf_sha256':sha(OUT/'ABNB_GBV_two_pager.pdf'),'pages':2}))
