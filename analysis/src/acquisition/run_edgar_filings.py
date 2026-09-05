"""Download ABNB 10-Q/10-K primary documents and extract KPI sentences."""
import csv, datetime, json, os, re, sys
from pathlib import Path
sys.path.insert(0, os.getcwd())
from processing.acquisition import fetch, integrity

OUT = Path('raw_expansion/v2_2026-09-05/sec_edgar/filings')
LOG = Path('metadata/expansion/edgar_filings_log.csv')
DER = Path('processed/airbnb_quant_panel_v2_staging/derived/abnb_filing_kpis.csv')
CIK = '1559720'

def strip_html(h):
    h = re.sub(r'(?is)<(script|style).*?</\1>', ' ', h)
    h = re.sub(r'(?s)<[^>]+>', ' ', h)
    h = (h.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&#8217;', "'")
          .replace('&#8212;', '-').replace('&#160;', ' ').replace('&quot;', '"'))
    return re.sub(r'\s+', ' ', h)

def main():
    sub = json.load(open('raw_expansion/v2_2026-09-05/sec_edgar/abnb_submissions.json'))
    r = sub['filings']['recent']
    rows = list(zip(r['accessionNumber'], r['form'], r['primaryDocument'],
                    r['filingDate'], r['reportDate']))
    tgt = [x for x in rows if x[1] in ('10-Q', '10-K')]
    print(f'10-Q/10-K filings to fetch: {len(tgt)}', flush=True)

    new = not LOG.exists()
    lf = open(LOG, 'a', newline='')
    w = csv.DictWriter(lf, fieldnames=['acquired_at_utc','accession','form','filing_date','report_date',
                                       'bytes','sha256','local_path','http_status','classification','license_tier'])
    if new: w.writeheader()

    kpi_rows, ok = [], 0
    PATS = {
        'nights_booked': r'Nights and (?:Experiences|Seats) Booked[^.]{0,240}\.',
        'gbv':           r'(?:Gross Booking Value|GBV)[^.]{0,240}\.',
        'adr':           r'\bADR\b[^.]{0,200}\.',
        'take_rate':     r'take rate[^.]{0,200}\.',
        'rnpl':          r'Reserve Now, Pay Later[^.]{0,240}\.',
    }
    for accn, form, doc, fdate, rdate in tgt:
        a = accn.replace('-', '')
        url = f'https://www.sec.gov/Archives/edgar/data/{CIK}/{a}/{doc}'
        dest = OUT / accn / doc
        res = fetch.get(url, dest, pace=0.6, timeout=180)
        row = dict(acquired_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
                   accession=accn, form=form, filing_date=fdate, report_date=rdate,
                   bytes=res.bytes, sha256='', local_path=str(dest),
                   http_status=res.status, classification=res.classification,
                   license_tier='public_domain')
        if res.classification == 'ok' and res.bytes > 1000:
            row['sha256'] = integrity.sha256_file(dest); ok += 1
            txt = strip_html(dest.read_text(encoding='utf-8', errors='replace'))
            hits = 0
            for label, pat in PATS.items():
                for m in re.finditer(pat, txt, re.I):
                    s = m.group(0).strip()
                    if 40 < len(s) < 400:
                        kpi_rows.append(dict(accession=accn, form=form, report_date=rdate,
                                             metric=label, excerpt=s))
                        hits += 1
            print(f'  OK  {form:<5} {rdate}  {res.bytes/1e6:>5.2f}MB  kpi_sentences={hits}', flush=True)
        else:
            print(f'  {res.status}  {form} {rdate}  {res.classification}', flush=True)
        w.writerow(row); lf.flush()
    lf.close()

    seen, ded = set(), []
    for k in kpi_rows:
        sig = (k['report_date'], k['metric'], k['excerpt'][:90])
        if sig in seen: continue
        seen.add(sig); ded.append(k)
    DER.parent.mkdir(parents=True, exist_ok=True)
    with open(DER, 'w', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=['accession','form','report_date','metric','excerpt'])
        wr.writeheader(); wr.writerows(sorted(ded, key=lambda z: (z['report_date'], z['metric'])))
    import collections
    print(f'\nDONE filings={ok}/{len(tgt)}  kpi sentences={len(ded)}', flush=True)
    print('  by metric:', dict(collections.Counter(k['metric'] for k in ded)), flush=True)

if __name__ == '__main__':
    main()
