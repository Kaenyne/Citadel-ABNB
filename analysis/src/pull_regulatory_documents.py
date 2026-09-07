"""Retrieve ABNB regulatory news/transcript metadata through the local LSEG session.

Raw licensed material stays in gitignored data/raw/regulatory. Never logs keys.
Run: .venv/Scripts/python.exe analysis/src/pull_regulatory_documents.py
"""
import json
import os
from pathlib import Path
import signal
import threading

OUT = Path(__file__).resolve().parents[2] / 'data/raw/regulatory/lseg'
OUT.mkdir(parents=True, exist_ok=True)

def main():
    import eikon as ek
    # A watchdog also bounds desktop-session discovery, which can otherwise hang.
    timer = threading.Timer(150, lambda: os._exit(124))
    timer.daemon = True
    timer.start()
    key = os.environ.get('LSEG_APP_KEY') or os.environ.get('REFINITIV_APP_KEY')
    if not key:
        raise RuntimeError('LSEG_APP_KEY / REFINITIV_APP_KEY not present')
    print('Opening desktop session; credential present', flush=True)
    ek.set_timeout(25)
    ek.set_app_key(key)
    queries = {
        'transcripts': 'Source:TRANS AND R:ABNB.O',
        'regulatory_news': 'R:ABNB.O AND (regulation OR rental OR housing OR tourism) AND Language:LEN',
    }
    status = {}
    for name, query in queries.items():
        try:
            data = ek.get_news_headlines(query, count=100, date_from='2023-01-01', date_to='2026-09-05T23:59:59')
            data.to_json(OUT / f'{name}_headlines.json', orient='records', date_format='iso', indent=2)
            print(f'{name}: {len(data)} headlines', flush=True)
            status[name] = {'count': len(data), 'query': query}
            selected = data.head(20) if name == 'transcripts' else data[data['text'].str.contains('EU rules|Supreme Court|Florence|Ibiza|fines Airbnb|targets 120|Mississippi|Indonesia|Milan', case=False)].drop_duplicates('storyId')
            if len(selected):
                for i, row in selected.iterrows():
                    sid = row['storyId']
                    story = ek.get_news_story(sid)
                    filename = sid.replace(':', '_').replace('/', '_') + '.html'
                    (OUT / filename).write_text(story, encoding='utf-8')
                print(f'{name}: {len(selected)} story bodies saved', flush=True)
        except Exception as exc:
            # Do not log exception bodies, which may include request credentials.
            status[name] = {'error_type': type(exc).__name__, 'query': query}
            print(f'{name}: {type(exc).__name__}', flush=True)
    (OUT / 'retrieval_status.json').write_text(json.dumps(status, indent=2), encoding='utf-8')
    timer.cancel()

if __name__ == '__main__':
    main()
