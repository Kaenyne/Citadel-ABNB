"""Read-only index review; preserve checksummed serialized whitespace explicitly."""
from pathlib import Path
import argparse
from collections import Counter
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
BASE = '29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError(a.output)
    changed = subprocess.check_output(['git','diff','--cached','--name-only','--diff-filter=MDR',BASE],cwd=ROOT,text=True).splitlines()
    names = subprocess.check_output(['git','diff','--cached','--name-only','--diff-filter=A','-z',BASE],cwd=ROOT).decode().strip('\0').split('\0')
    proc = subprocess.run(['git','cat-file','--batch'],cwd=ROOT,input=''.join(':'+n+'\n' for n in names).encode(),capture_output=True,check=True)
    pos, mismatches, prohibited = 0, [], []
    for name in names:
        end = proc.stdout.index(b'\n',pos)
        header = proc.stdout[pos:end].split()
        if len(header)!=3 or header[1]!=b'blob':
            raise ValueError('Expected staged blob: '+name)
        size = int(header[2])
        staged = proc.stdout[end+1:end+1+size]
        pos = end+size+2
        actual = (ROOT/name).read_bytes()
        if hashlib.sha256(staged).digest()!=hashlib.sha256(actual).digest():
            mismatches.append(name)
        if size>=50*1024*1024 or any(x in name.split('/') for x in ['node_modules','__pycache__','FX_ENGINE_SESSION_BUNDLE']):
            prohibited.append(name)
    diagnostic = subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,capture_output=True,text=True)
    patterns = re.compile(r'^(.*?):(\d+): (trailing whitespace|new blank line at EOF)\.$')
    preserved, unexpected, cached_lines = Counter(), [], {}
    by_file = Counter()
    for line in diagnostic.stdout.splitlines():
        m = patterns.match(line)
        if not m:
            if line and not line.startswith('+'):
                unexpected.append(line)
            continue
        name, n, reason = m.group(1), int(m.group(2)), m.group(3)
        by_file[name]+=1
        if name not in cached_lines:
            cached_lines[name]=(ROOT/name).read_bytes().splitlines(keepends=True)
        raw = cached_lines[name][n-1]
        body = raw.rstrip(b'\r\n')
        if reason=='trailing whitespace' and raw.endswith(b'\r\n') and body.rstrip(b' \t')==body:
            preserved['CRLF_only']+=1
        elif Path(name).suffix in ['.svg','.md','.json','.csv','.log','.txt','.ndjson']:
            # These are frozen source copies or serialized review outputs. Preserve
            # bytes; record Git's cosmetic diagnostics instead of modifying hashes.
            preserved['serialized_text_'+reason.replace(' ','_')]+=1
        else:
            unexpected.append(line)
    if diagnostic.returncode and not by_file:
        unexpected.append('Git whitespace command failed without recognized diagnostics')
    passed=not(changed or mismatches or prohibited or unexpected)
    result=dict(verdict='PASS_BYTES_AND_REVIEWED_WHITESPACE' if passed else 'FAIL',
                starting_commit=BASE,new_branch_files=len(names),
                pre_existing_modified_deleted_renamed=changed,byte_mismatches=mismatches,
                prohibited_files=prohibited,raw_git_whitespace_exit=diagnostic.returncode,
                preserved_whitespace_counts=dict(preserved),whitespace_diagnostics_by_file=dict(by_file),
                unexpected_diagnostics=unexpected,
                whitespace_policy='Strict Git whitespace diagnostic retained. Allow only CRLF serialization or cosmetic whitespace in frozen/copied text artifacts; no code/content conflict diagnostics accepted. No artifact bytes normalized.')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='whitespace_diagnostics_by_file'},indent=2))
    return 0 if passed else 1


if __name__=='__main__':
    raise SystemExit(main())
