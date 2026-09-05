"""Harvard Dataverse acquisition using header authentication."""
import csv, datetime, json, os, sys, time, urllib.parse, urllib.request
from pathlib import Path
sys.path.insert(0, os.getcwd())
from processing.acquisition import integrity

BASE=Path('raw_expansion/v2_2026-09-05/harvard_dataverse')
LOG=Path('metadata/expansion/dataverse_log.csv')
COLS=['acquired_at_utc','global_id','title','file_name','bytes','sha256','local_path',
      'http_status','classification','license','license_tier']
TOK=os.environ.get('DATAVERSE_API_TOKEN','')
HDR={'X-Dataverse-key':TOK,'User-Agent':'UF-student-research theobmachado@gmail.com'}
MAX=2_000_000_000
OK_EXT=('.csv','.tsv','.zip','.json','.jsonl','.gz','.xlsx','.tab','.parquet')

def api(url, binary=False, timeout=180):
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers=HDR),timeout=timeout) as r:
            return r.status, (r.read() if binary else json.loads(r.read()))
    except urllib.error.HTTPError as e: return e.code, None
    except Exception: return 'ERR', None

def main():
    st,me=api('https://dataverse.harvard.edu/api/users/:me')
    print(f'auth: {st} {me["data"]["displayName"] if me else ""}',flush=True)
    seen=set(); new=not LOG.exists()
    lf=open(LOG,'a',newline=''); w=csv.DictWriter(lf,fieldnames=COLS)
    if new: w.writeheader()
    ok=0
    for q in ['airbnb','short-term rental','inside airbnb','vacation rental listings']:
        st,d=api(f'https://dataverse.harvard.edu/api/search?q={urllib.parse.quote(q)}&type=dataset&per_page=40')
        if not d: print(f'  search "{q}" -> {st}',flush=True); continue
        items=d['data']['items']
        print(f'  "{q}" -> {len(items)} datasets',flush=True)
        for it in items:
            gid=it.get('global_id','')
            if not gid or gid in seen: continue
            blob=(it.get('name','')+' '+it.get('description','')).lower()
            if 'airbnb' not in blob and 'short-term rental' not in blob: continue
            seen.add(gid)
            st,dd=api(f'https://dataverse.harvard.edu/api/datasets/:persistentId/?persistentId={gid}')
            if not dd: print(f'    {st}  {gid}',flush=True); continue
            lv=dd['data']['latestVersion']; lic=lv.get('license',{})
            lic=lic.get('name','') if isinstance(lic,dict) else str(lic)
            for fm in lv.get('files',[])[:6]:
                df=fm.get('dataFile',{}); fn=df.get('filename','')
                if not fn.lower().endswith(OK_EXT): continue
                if df.get('filesize',0)>MAX:
                    print(f'    SKIP {fn} {df["filesize"]/1e9:.1f}GB',flush=True); continue
                st,blob_b=api(f'https://dataverse.harvard.edu/api/access/datafile/{df["id"]}',
                              binary=True,timeout=900)
                dest=BASE/gid.replace('/','_').replace(':','')/fn
                row=dict(acquired_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
                         global_id=gid,title=it.get('name','')[:100],file_name=fn,bytes=0,sha256='',
                         local_path=str(dest),http_status=st,classification='',license=lic[:60],
                         license_tier='open_repo')
                if st==200 and blob_b and len(blob_b)>512:
                    dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(blob_b)
                    v=integrity.validate(dest)
                    row['bytes']=len(blob_b); row['classification']='ok' if v.ok else 'rejected-'+v.detail[:30]
                    if v.ok:
                        row['sha256']=integrity.sha256_file(dest); ok+=1
                        print(f'    OK  {len(blob_b)/1e6:>7.2f}MB  {fn[:40]:<40} {it.get("name","")[:38]}',flush=True)
                    else: dest.unlink(missing_ok=True)
                else:
                    row['classification']='source-restriction' if st in (401,403,404) else 'local-fault'
                    print(f'    {st}  {fn[:40]}',flush=True)
                w.writerow(row); lf.flush()
                time.sleep(1.5)
    lf.close(); print(f'\nDONE dataverse files: {ok}',flush=True)

if __name__=='__main__': main()
