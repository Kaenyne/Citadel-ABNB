"""Read-only Git identity audit plus additive local handoff generation; never commits."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[4]
BASE = '8821961853e4068febbfe2712f9a4e1036c9e629'
L4 = '29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70'
SCOPES = [
    'analysis/src/forecast_methods/quant_thesis_validation_v1',
    'data/processed/forecast_methods/quant_thesis_validation_v1',
    'docs/revenue-forecast-strategy/quant_thesis_validation_v1',
    'docs/revenue-forecast-strategy/05_backtests/QUANT_THESIS_VALIDATION_v1.md',
]


def git(*args, data=None):
    return subprocess.check_output(['git', *args], cwd=ROOT, input=data)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def allowed(path):
    return any(path == p or path.startswith(p + '/') for p in SCOPES)


def inspect(commit=None):
    if commit:
        changes = git('diff', '--name-status', BASE, commit).decode().splitlines()
        entries = git('ls-tree', '-r', '-z', commit, '--', *SCOPES)
    else:
        changes = git('diff', '--cached', '--name-status', BASE).decode().splitlines()
        entries = git('ls-files', '--stage', '-z', '--', *SCOPES)
    for line in changes:
        action, path = line.split('\t', 1)
        if action != 'A' or not allowed(path):
            raise AssertionError(f'Only new scoped files are permitted: {line}')
    files = []
    for item in entries.split(b'\0'):
        if not item:
            continue
        meta, raw_path = item.split(b'\t', 1)
        parts = meta.decode().split()
        if commit:
            mode, typ, obj = parts
            if typ != 'blob':
                raise AssertionError((typ, raw_path))
        else:
            mode, obj, stage = parts
            if stage != '0':
                raise AssertionError(('unmerged', raw_path))
        files.append({'path': raw_path.decode(), 'mode': mode, 'git_blob': obj})
    if not files:
        raise AssertionError('No scoped files found')
    raw = git('cat-file', '--batch', data=('\n'.join(p['git_blob'] for p in files)+'\n').encode())
    offset = 0
    for record in files:
        end = raw.index(b'\n', offset)
        obj, typ, size_text = raw[offset:end].decode().split()
        size = int(size_text)
        if obj != record['git_blob'] or typ != 'blob':
            raise AssertionError('Unexpected batch object')
        payload = raw[end+1:end+1+size]
        offset = end + size + 2
        path = ROOT / record['path']
        if path.read_bytes() != payload:
            raise AssertionError(f'Git/index bytes differ from reviewed disk file: {path}')
        record.update(bytes=size, sha256=sha(payload))
    return files


def write_new(path, obj):
    with path.open('x', encoding='utf-8') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--commit', help='Full analytical commit; omit to inspect staged files only')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    if not out.is_relative_to(ROOT) or out.exists():
        raise ValueError('Choose a new destination within this worktree')
    commit = git('rev-parse', args.commit+'^{commit}').decode().strip() if args.commit else None
    if commit:
        subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, commit], cwd=ROOT, check=True)
    records = inspect(commit)
    out.mkdir(parents=True)
    manifest = {'analytical_commit': commit, 'baseline_L3': BASE, 'baseline_L4': L4,
                'files': records, 'file_count': len(records), 'total_bytes': sum(r['bytes'] for r in records)}
    write_new(out/'analytical_manifest.json', manifest)
    write_new(out/'seal_receipt.json', {
        'status': 'PASS', 'mode': 'committed_analytical_payload' if commit else 'staged_index_audit',
        'analytical_commit': commit, 'files_exactly_equal_to_reviewed_disk': len(records),
        'only_additions_in_authorized_scopes': True,
        'manifest_sha256': sha((out/'analytical_manifest.json').read_bytes()),
        'script_sha256': sha(Path(__file__).read_bytes()), 'git_mutations_performed': 0})
    print(json.dumps({'status': 'PASS', 'files': len(records), 'bytes': manifest['total_bytes'],
                      'analytical_commit': commit, 'out': str(out)}, indent=2))


if __name__ == '__main__':
    main()
