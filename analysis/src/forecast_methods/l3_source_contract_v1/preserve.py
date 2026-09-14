"""Verify real immutable Git objects and relevant frozen worktree bytes; read only."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[4]
BASE = '8821961853e4068febbfe2712f9a4e1036c9e629'
SOURCE = '7fb6fe0f248d5492b899672b9b70545da62d63ee'
BUNDLE = 'data/processed/forecast_methods/l3_bundle_v1/'
MANIFEST_SHA = '9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def blobs(ref, paths):
    """One batch process, preserving exact binary object contents."""
    paths=list(dict.fromkeys(paths))
    request=''.join(f'{ref}:{p}\n' for p in paths).encode()
    result=subprocess.run(['git','cat-file','--batch'],input=request,stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,cwd=ROOT,check=True).stdout
    offset=0; out={}
    for p in paths:
        end=result.index(b'\n',offset); header=result[offset:end].split()
        if len(header)!=3 or header[1]!=b'blob':
            raise ValueError(f'Required committed blob unavailable: {ref}:{p}')
        size=int(header[2]);start=end+1
        out[p]=result[start:start+size]
        if result[start+size:start+size+1]!=b'\n':raise ValueError('Invalid batch object boundary')
        offset=start+size+1
    return out

def verify():
    for commit in [BASE,SOURCE]:
        if git('cat-file','-t',commit).strip()!=b'commit':raise ValueError('Not a commit object')
    subprocess.run(['git','merge-base','--is-ancestor',SOURCE,BASE],cwd=ROOT,check=True)
    protected=['analysis/src/forecast_methods','data/processed/forecast_methods',
               'docs/revenue-forecast-strategy','model','data']
    existing_changes=git('diff','--name-only','--diff-filter=CDMRTUXB',BASE,'--',*protected)
    if existing_changes.strip():
        raise ValueError('Existing protected files changed from accepted base: '+existing_changes.decode())
    manifest=blobs(BASE,[BUNDLE+'SHA256SUMS.json'])[BUNDLE+'SHA256SUMS.json']
    if sha(manifest)!=MANIFEST_SHA:raise ValueError('Original manifest identity changed')
    expected=json.loads(manifest)
    original=blobs(BASE,[BUNDLE+p for p in expected])
    for name,digest in expected.items():
        if sha(original[BUNDLE+name])!=digest:raise ValueError('Committed bundle checksum: '+name)
        if sha((ROOT/BUNDLE/name).read_bytes())!=digest:raise ValueError('Working bundle checksum: '+name)
    actual={p.relative_to(ROOT/BUNDLE).as_posix() for p in (ROOT/BUNDLE).rglob('*') if p.is_file()}
    if actual!=set(expected)|{'SHA256SUMS.json'}:raise ValueError('Original bundle file inventory changed')
    if (ROOT/BUNDLE/'SHA256SUMS.json').read_bytes()!=manifest:raise ValueError('Working manifest changed')
    metadata=json.loads(original[BUNDLE+'bundle.json'])
    if metadata['research_source_commit']!=SOURCE:raise ValueError('Research commit differs')
    sources=blobs(SOURCE,metadata['source_outputs']+metadata['research_notes'])
    routing={'cohort_fx_v2':'cohort_fx','fee_panel_v1':'fee_panel','l3_adr_hotel_v1':'adr_hotel',
             'nclh_transfer_v1':'nclh','conversion_validation_v1':'conversion'}
    for path in metadata['source_outputs']:
        package=next(v for k,v in routing.items() if '/'+k+'/' in path)
        target=BUNDLE+'payload/'+package+'/'+Path(path).name
        if sources[path]!=original[target]:raise ValueError('Payload not from specified research commit: '+path)
    for path in metadata['research_notes']:
        if sources[path]!=original[BUNDLE+'research_notes/'+Path(path).name]:raise ValueError('Review note source changed')
    core=['data/processed/overnight/02_kpi_panel_quarterly.csv',
          'data/processed/forecast_methods/harness/calendar.csv','data/processed/forecast_methods/harness/targets.csv',
          'data/processed/forecast_methods/L0/L0_vintage_register.csv',
          'analysis/src/forecast_methods/harness/score.py','analysis/src/forecast_methods/harness_v1_1/score.py',
          'analysis/src/forecast_methods/kernel_engine_v2/engine.py']
    core+=git('ls-tree','-r','--name-only',BASE,'data/processed/forecast_methods/registry').decode().splitlines()
    # Git may normalize text in older files; compare worktree bytes to the start receipt,
    # and separately report their immutable object identities instead of conflating them.
    core_blobs=blobs(BASE,core)
    if git('diff','--name-only',BASE,'--',*core).strip():
        raise ValueError('A frozen core file differs from the accepted base commit')
    return {'base_commit':BASE,'base_tree':git('rev-parse',BASE+'^{tree}').decode().strip(),
            'research_commit':SOURCE,'research_tree':git('rev-parse',SOURCE+'^{tree}').decode().strip(),
            'original_manifest_sha256':MANIFEST_SHA,'bundle_exact_files_verified':len(expected),
            'payload_sources_verified':len(metadata['source_outputs']),
            'review_sources_verified':len(metadata['research_notes']),
            'protected_worktree_sha256':{p:sha((ROOT/p).read_bytes()) for p in core},
            'protected_git_blob_sha256':{p:sha(core_blobs[p]) for p in core},
            'status':'PASS'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--compare',type=Path)
    a=ap.parse_args()
    if a.out.exists():raise FileExistsError('Use a NEW receipt path')
    result=verify()
    if a.compare:
        old=json.loads(a.compare.read_text())
        if old!=result:raise ValueError('Protected source identities or bytes changed since start')
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if not isinstance(v,dict)}))

if __name__=='__main__':main()
