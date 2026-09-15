"""Verify index bytes before publishing the new, checksum-backed L4 branch."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[4]
BASE = '1c87628cedbc94ab8a0e8552743c94485ef353b8'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError(a.output)
    changed = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '--diff-filter=MDR', BASE], cwd=ROOT, text=True).splitlines()
    names = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '--diff-filter=A', '-z', BASE], cwd=ROOT).decode().strip('\0').split('\0')
    proc = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                          input=''.join(':' + n + '\n' for n in names).encode(), capture_output=True, check=True)
    pos, mismatches, prohibited = 0, [], []
    for name in names:
        end = proc.stdout.index(b'\n', pos)
        header = proc.stdout[pos:end].split()
        if len(header) != 3 or header[1] != b'blob':
            raise ValueError(f'Expected ordinary staged file: {name}')
        size = int(header[2])
        staged = proc.stdout[end + 1:end + 1 + size]
        pos = end + size + 2
        actual = (ROOT / name).read_bytes()
        if hashlib.sha256(staged).digest() != hashlib.sha256(actual).digest():
            mismatches.append(name)
        if len(actual) >= 50 * 1024 * 1024 or any(x in name.split('/') for x in ('node_modules', '__pycache__', 'FX_ENGINE_SESSION_BUNDLE')):
            prohibited.append(name)
    check = subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT, capture_output=True, text=True)
    passed = not (changed or mismatches or prohibited or check.returncode)
    receipt = dict(verdict='PASS' if passed else 'FAIL', new_branch_files=len(names),
                   pre_existing_modified_deleted_renamed=changed, byte_mismatches=mismatches,
                   prohibited_files=prohibited, whitespace_check_exit=check.returncode,
                   whitespace_check_excerpt=check.stdout[:2000], starting_commit=BASE)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in receipt.items() if k not in ('byte_mismatches', 'whitespace_check_excerpt')}, indent=2))
    print(f'Byte mismatches: {len(mismatches)}; complete receipt: {a.output}')
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
