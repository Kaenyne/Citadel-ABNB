"""Audit outgoing Git objects without disclosing candidate secret values or publishing."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, csv, hashlib, json, re, subprocess

ROOT = Path(__file__).resolve().parents[5]

def git(*args, data=None):
    return subprocess.check_output(['git', *args], cwd=ROOT, input=data)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--remote-ref', action='append', required=True)
    args=ap.parse_args()
    out=args.out.resolve()
    allowed=ROOT/'data/processed/forecast_methods/quant_thesis_validation_v1/publication_audit_v1'
    if out.exists() or not out.is_relative_to(allowed):
        raise ValueError('Choose a new output inside the publication audit data directory')
    refs=args.remote_ref
    for ref in refs:
        if not re.fullmatch(r'[a-f0-9]{40}',ref): raise ValueError('Exact advertised commit ids required')
        git('cat-file','-e',ref+'^{commit}')
    head=git('rev-parse','HEAD').decode().strip()
    revisions=[head,'--not',*refs]
    objects=[]
    for line in git('rev-list','--objects',*revisions).decode().splitlines():
        obj,_,path=line.partition(' ')
        objects.append((obj,path))
    payload=git('cat-file','--batch',data=('\n'.join(x[0] for x in objects)+'\n').encode())
    offset=0; files=[]; findings=[]
    secret_patterns={
        'private_key':rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
        'github_token':rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{35,})\b',
        'aws_access_key':rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
        'slack_token':rb'\bxox[baprs]-[0-9A-Za-z-]{20,}\b',
        'credential_literal':rb'(?i)(?:api[_-]?key|access[_-]?token|password|client[_-]?secret)\s*[:=]\s*[\x22\x27][A-Za-z0-9+/=_-]{20,}[\x22\x27]',
    }
    for oid,path in objects:
        end=payload.index(b'\n',offset)
        actual,typ,sz=payload[offset:end].decode().split(); size=int(sz)
        body=payload[end+1:end+1+size];offset=end+size+2
        if actual!=oid: raise AssertionError('Object stream mismatch')
        if typ!='blob': continue
        flags=[]
        if size>50_000_000: flags.append('over_50MB')
        lower=path.lower()
        if any(x in lower for x in ('bloomberg','capiq','factset','third_bridge','third-bridge')):
            flags.append('licensed_source_name_requires_classification')
        if re.search(r'(^|/)(\.env(?:\.[^/]*)?|[^/]+\.(?:pem|key|p12))$',lower):
            flags.append('credential_filename')
        if '/data/raw/' in '/'+lower or '/raw/' in '/'+lower:
            flags.append('raw_path_requires_classification')
        is_text=b'\x00' not in body[:8192]
        if is_text:
            for label,pattern in secret_patterns.items():
                if re.search(pattern,body): flags.append(label)
        row={'git_blob':oid,'path':path,'bytes':size,'sha256':hashlib.sha256(body).hexdigest(),'flags':'|'.join(flags)}
        files.append(row)
        if flags: findings.append(row)
    out.mkdir(parents=True)
    for name,rows in [('outgoing_blobs.csv',files),('review_candidates.csv',findings)]:
        with (out/name).open('x',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['git_blob','path','bytes','sha256','flags']);w.writeheader();w.writerows(rows)
    commits=git('log','--format=%H %s',*revisions).decode().splitlines()
    receipt={'status':'PASS_NO_AUTOMATED_FLAGS' if not findings else 'MANUAL_REVIEW_REQUIRED',
        'observed_at_utc':datetime.now(timezone.utc).isoformat(),'head':head,'advertised_remote_heads':refs,
        'outgoing_commits':commits,'outgoing_commit_count':len(commits),'outgoing_blob_count':len(files),
        'total_outgoing_blob_bytes':sum(r['bytes'] for r in files),'maximum_blob_bytes':max((r['bytes'] for r in files),default=0),
        'flagged_blobs':len(findings),'scope':'Every blob newly reachable from HEAD relative to supplied advertised remote heads, including intermediate versions.',
        'limits':'Pattern scan is not proof of absence; names/raw paths are manually classified. Never print candidate secret values.',
        'source_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'git_mutations':0}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('advertised_remote_heads','outgoing_commits')},indent=2))

if __name__=='__main__': main()
