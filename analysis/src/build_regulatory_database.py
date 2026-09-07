"""Build the ABNB regulatory research database and readable registers (stdlib only).

Inputs are curated, source-linked research, not automatically inferred legal status.
Run after editing research/regulatory/*.json. Raw licensed texts are excluded.
"""
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / 'research/regulatory'
OUT = ROOT / 'data/processed/abnb_regulatory.sqlite'
TIERS = {
    1: 'Implemented regulation and enforcement (including subsequent reversals)',
    2: 'Adopted policy or scheduled regulation with future impact',
    3: 'Proposals, uncertain implementation and blocked initiatives',
    4: 'Activism and social pressure without a separate operative measure',
}

def read(name):
    return json.loads((DIR/name).read_text(encoding='utf-8'))

def build():
    factors = sorted(read('factors.json'), key=lambda x: (x['tier'],x['priority']))
    sources = read('sources.json')
    observations = read('earnings_observations.json')
    manifest = json.loads((ROOT/'data/raw/regulatory/transcripts/manifest.json').read_text())
    src = {s['id']:s for s in sources}
    ids = {f['id'] for f in factors}
    assert len(ids)==len(factors)
    assert len(src)==len(sources)
    assert len({(f['tier'],f['priority']) for f in factors})==len(factors)
    for f in factors:
        assert f['source_ids'] and all(s in src for s in f['source_ids'])
        assert all(i in ids for i in f['related_ids'])
        assert f['tier'] in TIERS
    for o in observations:
        assert all(i in ids for i in o['related_ids'])
        assert o['period'] in {m['period'] for m in manifest}
    with sqlite3.connect(OUT) as db:
        db.execute('PRAGMA foreign_keys=ON')
        for name in ['factor_search','factor_sources','factor_relationships','observations','transcripts','factors','sources','metadata']:
            db.execute(f'DROP TABLE IF EXISTS {name}')
        db.execute('CREATE TABLE metadata (key TEXT PRIMARY KEY,value TEXT)')
        db.executemany('INSERT INTO metadata VALUES (?,?)',[
            ('as_of','2026-09-05'),('scope','Housing displacement, local quality of life and overtourism-driven STR policy; curated international research universe'),
            ('ranking','Tier first, then qualitative research priority; not a predicted stock-price ranking'),
            ('currency','Fine amounts retain original currency; no FX conversion assumed'),
            ('exposure','NYC approximately 1% is a historical pre-September-2023 revenue share; NULL elsewhere means unknown, not zero')])
        db.execute('CREATE TABLE sources (id TEXT PRIMARY KEY,title TEXT,publication_date TEXT,url TEXT,type TEXT,accessed TEXT)')
        db.executemany('INSERT INTO sources VALUES (:id,:title,:publication_date,:url,:type,:accessed)',sources)
        fields=[k for k in factors[0] if k not in ('source_ids','related_ids')]
        types={'tier':'INTEGER','priority':'INTEGER','global_revenue_exposure_pct':'REAL'}
        db.execute('CREATE TABLE factors ('+','.join(k+' '+types.get(k,'TEXT')+(' PRIMARY KEY' if k=='id' else '') for k in fields)+')')
        db.executemany('INSERT INTO factors VALUES ('+','.join(':'+k for k in fields)+')',factors)
        db.execute('CREATE TABLE factor_sources (factor_id TEXT REFERENCES factors(id),source_id TEXT REFERENCES sources(id),PRIMARY KEY(factor_id,source_id))')
        db.executemany('INSERT INTO factor_sources VALUES (?,?)',[(f['id'],s) for f in factors for s in f['source_ids']])
        db.execute('CREATE TABLE factor_relationships (factor_id TEXT REFERENCES factors(id),related_id TEXT REFERENCES factors(id),PRIMARY KEY(factor_id,related_id))')
        db.executemany('INSERT INTO factor_relationships VALUES (?,?)',[(f['id'],i) for f in factors for i in f['related_ids']])
        db.execute('CREATE TABLE transcripts (period TEXT PRIMARY KEY,url TEXT,status TEXT,local_path TEXT,sha256 TEXT,pages INTEGER,keyword_pages TEXT)')
        db.executemany('INSERT INTO transcripts VALUES (?,?,?,?,?,?,?)',[(m['period'],m['url'],m['status'],m.get('local_path'),m.get('sha256'),m.get('pages'),json.dumps(m.get('keyword_pages',[]))) for m in manifest])
        db.execute('CREATE TABLE observations (id TEXT PRIMARY KEY,period TEXT REFERENCES transcripts(period),call_date TEXT,speaker TEXT,locator TEXT,summary TEXT,pitch_use TEXT,related_ids TEXT,classification TEXT)')
        db.executemany('INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?)',[(o['id'],o['period'],o['call_date'],o['speaker'],o['locator'],o['summary'],o['pitch_use'],json.dumps(o['related_ids']),o['classification']) for o in observations])
        db.execute('CREATE VIRTUAL TABLE factor_search USING fts5(id UNINDEXED,jurisdiction,title,rule,observed_evidence,abnb_implication,limitations,next_catalyst)')
        db.executemany('INSERT INTO factor_search VALUES (?,?,?,?,?,?,?,?)',[(f['id'],f['jurisdiction'],f['title'],f['rule'],f['observed_evidence'],f['abnb_implication'],f['limitations'],f['next_catalyst']) for f in factors])
        assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert not db.execute('PRAGMA foreign_key_check').fetchall()
        assert db.execute("SELECT COUNT(*) FROM factor_search WHERE factor_search MATCH 'housing'").fetchone()[0]>0
    lines=['# ABNB regulatory factor register','', 'As of **5 September 2026**. See [research memo and methodology](README.md). Each factor separates the rule, observed evidence and analyst inference. Source dates can be unknown or month-only; access dates do not establish publication dates.','']
    for tier,label in TIERS.items():
        lines += [f'## Tier {tier}: {label}','']
        for f in [f for f in factors if f['tier']==tier]:
            lines += [f"### {f['id']} | {f['jurisdiction']} | {f['title']}",'',f"**Priority within tier:** {f['priority']} · **Status:** {f['status']}",'',f"**Dates:** {f['dates']}",'']
            for key,label in [('rule','Rule / event'),('observed_evidence','Observed evidence'),('abnb_implication','ABNB implication (analysis)'),('limitations','Limits on inference'),('next_catalyst','Next catalyst')]:
                lines += [f'**{label}:** {f[key]}','']
            lines += ['**Sources:** '+ '; '.join(f"[{s}: {src[s]['title']}]({src[s]['url']})" for s in f['source_ids']), '']
            if f['related_ids']: lines += ['**Related factors:** '+', '.join(f['related_ids']),'']
    (DIR/'factor_register.md').write_text('\n'.join(lines),encoding='utf-8')
    lines=['# Regulatory evidence from ABNB earnings calls','','14 quarterly calls archived: 13 company-hosted PDF transcripts (Q1 2023-Q1 2026) and the Q2 2026 public HTML fallback. The company-hosted PDFs are FactSet CallStreet corrected transcripts. Full text remains in gitignored data/raw. Targeted keyword screening was followed by review of the relevant Q&A/context; this is not a claim that every sentence received legal analysis.','', '## Most useful passages','']
    for o in observations:
        m=next(m for m in manifest if m['period']==o['period'])
        lines += [f"### {o['id']} | {o['period']} | {o['call_date']}",'',f"**Speaker:** {o['speaker']} · **Locator:** {o['locator']}",'',o['summary'],'',f"**Pitch use:** {o['pitch_use']}",'',f"**Evidence type:** {o['classification']}",'',f"[Transcript source]({m['url']}) · Related: {', '.join(o['related_ids'])}",'']
    lines += ['## Complete archive index','','| Period | Format/status | Pages | Keyword-hit pages | Source |','|---|---|---:|---|---|']
    for m in manifest:
        lines += [f"| {m['period']} | {m['status']} | {m.get('pages','HTML')} | {', '.join(map(str,m.get('keyword_pages',[])))} | [Open]({m['url']}) |"]
    lines += ['', 'Keyword-hit pages are navigation aids, not evidence by themselves. The queries include regulation, Spain, Barcelona, New York, housing, tourism and policy; some hits concern international growth rather than regulation. The Q2 2026 fallback has HTML text locators instead of PDF page numbers.']
    (DIR/'earnings_digest.md').write_text('\n'.join(lines),encoding='utf-8')
    # Public index contains document identifiers/hashes, never licensed text.
    (DIR/'transcript_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    lines=['# Source index','','As of 2026-09-05. Null dates in JSON mean no reliable exact publication date was established. Government statements describe policy and agency claims; they are not automatically independent evidence of housing outcomes. Reuters/LSEG links require a licensed desktop; full text is retained privately in data/raw.','','| ID | Source | Publication date | Type | Link |','|---|---|---|---|---|']
    lines += [f"| {s['id']} | {s['title']} | {s['publication_date'] or 'Not established'} | {s['type']} | [Open]({s['url']}) |" for s in sources]
    (DIR/'source_index.md').write_text('\n'.join(lines),encoding='utf-8')
    print(f'Built {OUT.name}: {len(factors)} factors, {len(sources)} sources, {len(manifest)} transcripts, {len(observations)} observations. Integrity, references and FTS checks passed.')

if __name__=='__main__': build()
