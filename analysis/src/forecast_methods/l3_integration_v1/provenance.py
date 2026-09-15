"""Hash base-commit files and explicit external dependencies; never modify them."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[4]
BASE = '1c87628cedbc94ab8a0e8552743c94485ef353b8'

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--compare', type=Path)
    ap.add_argument('--external-fx', type=Path)
    a = ap.parse_args()
    if a.out.exists():
        raise FileExistsError(a.out)
    files = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE], cwd=ROOT, text=True).splitlines()
    rows = [{'path': p, 'sha256': digest(ROOT / p), 'scope': 'base_commit'} for p in files]
    if a.external_fx:
        rows += [{'path': p.relative_to(a.external_fx).as_posix(), 'sha256': digest(p), 'scope': 'external_fx_read_only'}
                 for p in sorted(a.external_fx.rglob('*')) if p.is_file()]
    failures = []
    if a.compare:
        old = json.loads(a.compare.read_text())['files']
        current = {(r['scope'], r['path']): r['sha256'] for r in rows}
        failures = [r for r in old if current.get((r['scope'], r['path'])) != r['sha256']]
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({'base_commit': BASE, 'files': rows, 'changed': failures}, indent=2) + '\n')
    print(json.dumps({'files_hashed': len(rows), 'changed': len(failures)}))
    return int(bool(failures))

if __name__ == '__main__':
    raise SystemExit(main())
