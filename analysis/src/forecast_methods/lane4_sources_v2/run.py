"""Verify immutable L3 Git objects and classify their L4 accounting eligibility.

No statistical model is fitted. Original bundle bytes are canonical.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import importlib.util
import json
from pathlib import Path, PurePosixPath
import subprocess

ROOT = Path(__file__).resolve().parents[4]
BUNDLE_COMMIT = '8821961853e4068febbfe2712f9a4e1036c9e629'
RESEARCH_COMMIT = '7fb6fe0f248d5492b899672b9b70545da62d63ee'
BASE_COMMIT = '1c87628cedbc94ab8a0e8552743c94485ef353b8'
BUNDLE_PATH = 'data/processed/forecast_methods/l3_bundle_v1'
EXPECTED_MANIFEST = '9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970'
HANDOFF = 'docs/revenue-forecast-strategy/05_backtests/L3_PUBLICATION_HANDOFF_v1.md'
QVS_NAMES = ('QVS_VARIANCE_AND_PRESENTATION_ARGUMENTS_v1.md', 'QVS_GUIDE_BASIS_AND_DECISION_LOGIC_v1.md')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.run(['git', '-C', str(ROOT), *args], check=True, capture_output=True).stdout


def object_bytes(commit, paths):
    """Read binary Git blobs without shell decoding or checkout conversion."""
    queries = [f'{commit}:{p}' for p in paths]
    stream = io.BytesIO(subprocess.run(
        ['git', '-C', str(ROOT), 'cat-file', '--batch'],
        input=('\n'.join(queries)+'\n').encode(), check=True, capture_output=True).stdout)
    result = {}
    for path in paths:
        header = stream.readline().decode('ascii').strip().split()
        if len(header) != 3 or header[1] != 'blob':
            raise ValueError(f'Missing/non-blob committed object: {path}: {header}')
        data = stream.read(int(header[2]))
        if stream.read(1) != b'\n':
            raise ValueError('Malformed Git batch framing')
        result[path] = data
    if stream.read():
        raise ValueError('Unexpected Git batch trailing data')
    return result


def safe_relative(path):
    p = PurePosixPath(path)
    if p.is_absolute() or '..' in p.parts or '\\' in path or ':' in path:
        raise ValueError(f'Unsafe relative path {path}')
    return Path(*p.parts)


def json_new(path, data):
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


def bytes_new(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as f:
        f.write(data)


def csv_new(path, rows, fields=None):
    rows = list(rows)
    fields = fields or list(rows[0])
    with path.open('x', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def binding_match(data, expected):
    """Distinguish exact-byte bindings from documented CRLF/LF differences."""
    if sha(data) == expected:
        return 'exact'
    try:
        data.decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError('Binary hash mismatch')
    lf = data.replace(b'\r\n', b'\n')
    if b'\r' in lf:
        raise ValueError('Non-newline carriage return in mismatched object')
    if sha(lf) == expected:
        return 'expected_LF_actual_CRLF'
    if sha(lf.replace(b'\n', b'\r\n')) == expected:
        return 'expected_CRLF_actual_LF'
    raise ValueError(f'Content mismatch: actual {sha(data)} expected {expected}')


def payload_for_source(path):
    parts = PurePosixPath(path).parts
    package_map = {'cohort_fx_v2':'cohort_fx', 'fee_panel_v1':'fee_panel',
                   'l3_adr_hotel_v1':'adr_hotel', 'nclh_transfer_v1':'nclh',
                   'conversion_validation_v1':'conversion'}
    if path.startswith('docs/'):
        return 'research_notes/' + parts[-1]
    for src, target in package_map.items():
        if src in parts:
            return f'payload/{target}/{parts[-1]}'
    raise ValueError(f'Unknown source mapping {path}')


def verify_bundle(bundle):
    raw = (bundle/'SHA256SUMS.json').read_bytes()
    if sha(raw) != EXPECTED_MANIFEST:
        raise ValueError('Manifest checksum mismatch')
    manifest = json.loads(raw)
    if len(manifest) != 108:
        raise ValueError('Unexpected manifest file count')
    actual_files = {p.relative_to(bundle).as_posix() for p in bundle.rglob('*') if p.is_file()}
    if actual_files != set(manifest) | {'SHA256SUMS.json'}:
        raise ValueError('Bundle inventory mismatch')
    for path, expected in manifest.items():
        if sha((bundle/safe_relative(path)).read_bytes()) != expected:
            raise ValueError(f'Bundle checksum mismatch: {path}')
    return manifest


def acceptance_bindings(bundle):
    receipt = json.loads((bundle/'payload/conversion/final_review_acceptance.json').read_text())
    pairs = [('accepted_specification', receipt['accepted_specification']['path'], receipt['accepted_specification']['sha256'])]
    pairs += [('review', r['path'], r['sha256']) for r in receipt['review_evidence']]
    pairs += [('source', 'analysis/src/forecast_methods/conversion_validation_v1/'+name, h)
              for name, h in receipt['reviewed_source_sha256'].items()]
    pairs += [('output', 'data/processed/forecast_methods/conversion_validation_v1/results_v2/'+name, h)
              for name, h in receipt['reviewed_output_sha256'].items()]
    if len(pairs) != 32:
        raise ValueError('Unexpected conversion binding count')
    actual = object_bytes(RESEARCH_COMMIT, list(dict.fromkeys(p for _,p,_ in pairs)))
    rows = []
    for kind, path, expected in pairs:
        match = binding_match(actual[path], expected)
        payload = '' if kind == 'source' else payload_for_source(path)
        bundle_hash = sha((bundle/payload).read_bytes()) if payload else ''
        if payload and bundle_hash != expected:
            raise ValueError(f'Canonical bundle acceptance binding mismatch {payload}')
        rows.append({'binding_kind':kind, 'research_commit':RESEARCH_COMMIT,
                     'research_path':path, 'expected_sha256':expected,
                     'git_object_sha256':sha(actual[path]), 'git_binding_status':match,
                     'canonical_bundle_path':payload, 'canonical_bundle_sha256':bundle_hash,
                     'result':'PASS'})
    return rows


def extract(out, qvs_root):
    out.mkdir(parents=True, exist_ok=False)
    git('merge-base', '--is-ancestor', RESEARCH_COMMIT, BUNDLE_COMMIT)
    git('merge-base', '--is-ancestor', BASE_COMMIT, RESEARCH_COMMIT)
    paths = git('ls-tree', '-r', '--name-only', BUNDLE_COMMIT, '--', BUNDLE_PATH).decode().splitlines()
    blobs = object_bytes(BUNDLE_COMMIT, paths + [HANDOFF])
    for path in paths:
        bytes_new(out/'bundle'/safe_relative(path[len(BUNDLE_PATH)+1:]), blobs[path])
    bytes_new(out/'handoff'/Path(HANDOFF).name, blobs[HANDOFF])
    manifest = verify_bundle(out/'bundle')
    metadata = json.loads((out/'bundle/bundle.json').read_text())
    if metadata['research_source_commit'] != RESEARCH_COMMIT or metadata['verified_L1_L2_base'] != BASE_COMMIT:
        raise ValueError('Committed lineage metadata mismatch')
    source_paths = metadata['source_outputs'] + metadata['research_notes']
    source = object_bytes(RESEARCH_COMMIT, source_paths)
    lineage = []
    for path in source_paths:
        payload = payload_for_source(path)
        canonical = (out/'bundle'/payload).read_bytes()
        status = binding_match(source[path], sha(canonical))
        lineage.append({'research_path':path,'research_commit':RESEARCH_COMMIT,
                        'git_object_sha256':sha(source[path]), 'bundle_path':payload,
                        'bundle_sha256':sha(canonical),'byte_comparison':status,'result':'PASS'})
    csv_new(out/'research_lineage.csv', lineage)
    bindings = acceptance_bindings(out/'bundle')
    csv_new(out/'conversion_acceptance_bindings.csv', bindings)
    support = []
    for name in QVS_NAMES:
        path = qvs_root/'docs/revenue-forecast-strategy/05_backtests'/name
        before = path.read_bytes()
        bytes_new(out/'qvs'/name, before)
        if sha(path.read_bytes()) != sha(before):
            raise ValueError('QVS input changed during capture')
        support.append({'source_path':str(path), 'snapshot_path':'qvs/'+name,
                        'sha256':sha(before),'authority':'explicit user supplied supporting note; no L3 worktree followed'})
    json_new(out/'support_manifest.json', support)
    receipt = {'bundle_commit':BUNDLE_COMMIT,'research_commit':RESEARCH_COMMIT,
               'verified_L1_L2_base':BASE_COMMIT,'manifest_sha256':EXPECTED_MANIFEST,
               'verified_bundle_files':len(manifest),'research_lineage_files':len(lineage),
               'conversion_acceptance_bindings':len(bindings),
               'conversion_binding_exact':sum(r['git_binding_status']=='exact' for r in bindings),
               'conversion_binding_newline_only':sum(r['git_binding_status']!='exact' for r in bindings),
               'qvs_inputs':len(support),'integrity_status':'PASS',
               'scope':'Git-object and acceptance hash integrity only; no research refit or statistical replication',
               'canonical_policy':'Bundle bytes preserved; source-object newline-only differences explicit',
               'optional_supplements_accepted':0}
    json_new(out/'integrity_receipt.json', receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--qvs-root', type=Path, required=True)
    parser.add_argument('--stage', choices=('extract','audit','all'), default='all')
    args = parser.parse_args()
    out = args.out.resolve()
    if args.stage in ('extract','all'):
        print(json.dumps(extract(out, args.qvs_root.resolve()), indent=2))
    if args.stage in ('audit','all'):
        spec = importlib.util.spec_from_file_location('_lane4_sources_v2_eligibility', Path(__file__).with_name('eligibility.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(json.dumps(module.audit(out), indent=2))


if __name__ == '__main__':
    main()
