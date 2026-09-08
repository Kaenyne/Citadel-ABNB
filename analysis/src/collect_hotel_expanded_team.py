"""Freeze and inventory visible team evidence for the expanded hotel audit.

File/row counts describe coverage, never independent booking observations.
Existing licensed files are referenced in place and are not copied to outputs.
"""
from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
REVISION = 'e3055e627f4b7952c592939a03849f5fc32b9235'
REPOSITORY = 'Kaenyne/Citadel-ABNB'
RAW = ROOT / 'data/raw/hotel_expanded_research'
OUT = ROOT / 'data/processed/hotel_expanded_research'
GH = shutil.which('gh') or str(Path.home() / 'AppData/Local/Programs/GitHub CLI/bin/gh.exe')
TEXT_TYPES = {'.md', '.csv', '.json', '.txt'}
MAX_BYTES = 5_000_000


def api(path: str) -> dict:
    result = subprocess.run([str(GH), 'api', f'repos/{REPOSITORY}/{path}'],
                            check=True, capture_output=True, timeout=60)
    return json.loads(result.stdout)


def write_csv(name: str, rows: list[dict], fields: list[str]) -> None:
    with (OUT / name).open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def extract_urls(text: str, location: str) -> set[str]:
    # Parse CSV cells first: scanning a serialized row swallows following columns
    # into the URL because commas are otherwise valid URL characters.
    chunks = [text]
    if location.lower().endswith('.csv'):
        chunks = [cell for row in csv.reader(io.StringIO(text)) for cell in row]
    return {url.rstrip(').,;') for chunk in chunks
            for url in re.findall(r'https?://[^\s<>"\]|]+', chunk)}


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    tree_path = RAW / f'team_tree_{REVISION}.json'
    if not tree_path.exists():
        tree_path.write_text(json.dumps(api(f'git/trees/{REVISION}?recursive=1'), indent=2), encoding='utf-8')
    tree = json.loads(tree_path.read_text(encoding='utf-8'))
    if tree.get('truncated'):
        raise RuntimeError('Remote tree truncated; evidence inventory is incomplete.')
    selected = [item for item in tree['tree'] if item['type'] == 'blob' and (
        item['path'].startswith('research/notes/') and item['path'].endswith('.md')
        or item['path'] == 'research/sources/README.md'
        or item['path'].startswith('data/processed/') and item['path'].endswith('.csv')
        and any(word in item['path'].lower() for word in ['hotel', 'consensus', 'guidance', '11_new_business', '27_', '28_'])
    )]
    fetch_errors: list[dict] = []

    def fetch(item: dict) -> tuple[str, str, bytes] | None:
        target = RAW / 'team_review' / item['path']
        try:
            if not target.exists():
                obj = api(f"git/blobs/{item['sha']}")
                content = base64.b64decode(obj['content'])
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            content = target.read_bytes()
            if item.get('size') is not None and len(content) != item['size']:
                raise ValueError('Cached/downloaded size differs from immutable tree.')
            git_sha = hashlib.sha1(f'blob {len(content)}\0'.encode() + content).hexdigest()
            if git_sha != item['sha']:
                raise ValueError('Cached/downloaded blob SHA differs from immutable tree.')
            return 'github', f"https://github.com/{REPOSITORY}/blob/{REVISION}/{item['path']}", content
        except Exception as exc:
            fetch_errors.append({'path': item['path'], 'error': str(exc)})
            return None

    with ThreadPoolExecutor(max_workers=6) as pool:
        documents = [value for value in pool.map(fetch, selected) if value is not None]

    for zip_path in sorted(ROOT.glob('*.zip')):
        with zipfile.ZipFile(zip_path) as archive:
            for entry in archive.infolist():
                if Path(entry.filename).suffix.lower() in TEXT_TYPES and entry.file_size <= MAX_BYTES:
                    documents.append(('local_zip', f'{zip_path.name}::{entry.filename}', archive.read(entry)))

    for directory in ['research', 'model', 'citadel-abnb-files 2/research', 'theos-past-research/research']:
        for path in sorted((ROOT / directory).rglob('*')):
            if path.is_file() and path.suffix.lower() in TEXT_TYPES and path.stat().st_size <= MAX_BYTES:
                # Exclude this active multi-agent output, not older team evidence.
                if any(tag in path.name for tag in ['absolute-disclosure-search', 'absolute_disclosure_search',
                    'channel-data-expansion', 'channel_data_expansion', 'rollout-economics-expansion',
                    'rollout_economics_expansion', 'expanded-research-results', 'expanded_research_sources']):
                    continue
                documents.append(('local', path.relative_to(ROOT).as_posix(), path.read_bytes()))

    manifest: list[dict] = []
    urls: list[dict] = []
    hotel_hits: list[dict] = []
    first_hash: dict[str, str] = {}
    for origin, location, raw in documents:
        digest = hashlib.sha256(raw).hexdigest()
        text = raw.decode('utf-8-sig', errors='replace')
        numeric_hotel_lines = [i for i, line in enumerate(text.splitlines(), start=1)
                               if re.search(r'hotel', line, re.I) and re.search(r'\d', line)]
        csv_rows = ''
        if location.lower().endswith('.csv'):
            try:
                csv_rows = max(0, sum(1 for _ in csv.reader(io.StringIO(text))) - 1)
            except csv.Error:
                csv_rows = 'parse_error'
        manifest.append({'origin': origin, 'location': location, 'sha256': digest, 'bytes': len(raw),
                         'duplicate_of': first_hash.get(digest, ''), 'csv_data_rows': csv_rows,
                         'numeric_hotel_line_count': len(numeric_hotel_lines)})
        first_hash.setdefault(digest, location)
        for line in numeric_hotel_lines:
            hotel_hits.append({'location': location, 'sha256': digest, 'line_number': line})
        for url in sorted(extract_urls(text, location)):
            urls.append({'location': location, 'url': url, 'sha256': digest})

    write_csv('team_evidence_manifest.csv', manifest, ['origin', 'location', 'sha256', 'bytes', 'duplicate_of', 'csv_data_rows', 'numeric_hotel_line_count'])
    write_csv('team_source_urls.csv', urls, ['location', 'url', 'sha256'])
    write_csv('team_numeric_hotel_locations.csv', hotel_hits, ['location', 'sha256', 'line_number'])
    write_csv('team_fetch_errors.csv', fetch_errors, ['path', 'error'])
    summary = {'as_of': '2026-09-07', 'main_revision': REVISION,
               'selected_remote_files': len(selected), 'remote_fetch_errors': len(fetch_errors),
               'document_instances': len(manifest), 'unique_content_hashes': len(first_hash),
               'duplicate_content_instances': len(manifest) - len(first_hash),
               'numeric_hotel_line_references': len(hotel_hits), 'url_references': len(urls),
               'limitation': 'Visible current main, local research and root ZIP text files up to 5MB. No assertion about unshared work, inaccessible branches or statistical independence.'}
    (OUT / 'team_evidence_summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
