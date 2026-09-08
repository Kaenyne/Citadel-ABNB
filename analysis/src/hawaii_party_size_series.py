"""Hawaii DBEDT party size by accommodation type, 2000-2024, from the Annual Visitor Research
Report Excel tables (data/raw/hawaii_dbedt/*-annual-visitor.xls*), plus the monthly
'Visitor Highlights' workbooks (data/raw/hawaii_dbedt/monthly/YYYY-MM.xlsx).

Source pages: https://dbedt.hawaii.gov/economic/tourism/annual-reports/ (2024) and
https://dbedt.hawaii.gov/economic/tourism/tourism-archive/ (2000-2023); monthly at
https://dbedt.hawaii.gov/economic/tourism/monthly-statistics/ . Files are gitignored.

Each 'X-Only Visitor Characteristics: YYYY vs. YYYY-1' table reports visitor counts (people,
not parties) in parties of One / Two / Three or more, plus Avg Party Size. Parties are backed
out as visitors / party size; the 3+ average party size is solved from the mean.
"""
import re, glob, os
import pandas as pd, numpy as np

RAW = 'data/raw/hawaii_dbedt'
OUT = 'data/processed'
SEGMENTS = {
    'hotel': r'hotel[- ]only',
    'condo': r'condo[- ]only',
    'timeshare': r'timeshare[- ]only',
    'rental_house': r'rental house[- ]only',
    'bnb': r'bed (and|&) breakfast[- ]only',
    'all_air': r'summary of (air )?visitor characteristics:',   # TABLE 2 carries party size only to 2015
    'us_west': r'^table \d+[:. ]+u\.?s\.? west mma',
    'us_east': r'^table \d+[:. ]+u\.?s\.? east mma',
    'japan': r'^table \d+[:. ]+japan mma (air )?visitor characteristics:',
    'canada': r'^table \d+[:. ]+canada mma (air )?visitor characteristics:',
    'europe': r'^table \d+[:. ]+europe mma',
    'oceania': r'^table \d+[:. ]+oceania mma',
    'other_asia': r'^table \d+[:. ]+other asia mma',
    'latin_america': r'^table \d+[:. ]+latin america mma',
    'other_mma': r'^table \d+[:. ]+other mma',
    'family': r'^table \d+[:. ]+family (air )?visitor',
    'first_time': r'^table \d+[:. ]+first[- ]time (air )?visitor',
    'repeat': r'^table \d+[:. ]+repeat (air )?visitor',
}
ROWS = {
    'visitors': r'^total visitors( arrivals)?$|^visitor arrivals$',
    'visitor_days': r'^total visitor days$',
    'party_1': r'^one$',
    'party_2': r'^two$',
    'party_3plus': r'^three or more$',
    'avg_party_size': r'^avg\.? party size$',
    'los_statewide': r'^statewide( \(days\))?$',
    'first_time_visitors': r'^first[- ]time$',
    'repeat_visitors': r'^repeat$',
}

def find_sheet(x, pat):
    for s in x.sheet_names:
        try: t = x.parse(s, header=None, nrows=2)
        except Exception: continue
        title = ' '.join(str(v) for v in t.values.flatten() if pd.notna(v))
        if re.search(pat, title, re.I) and 'percentage' not in title.lower():
            return s, title
    return None, None

def parse_table(df):
    """Return {col_year: {row_key: value}} for the TOTAL block (first two year columns)."""
    lab = df[0].astype(str).str.strip().str.lower()
    # header row: first row with >=2 cells that look like years
    hdr = None
    for i in range(min(10, len(df))):
        yrs = []
        for j, v in enumerate(df.iloc[i]):
            if j == 0: continue
            m = re.fullmatch(r'\s*((?:19|20)\d\d)(?:\.0)?\s*[A-Za-z*/ 1]*', str(v))
            if m: yrs.append((j, int(m.group(1))))
        if len(yrs) >= 2: hdr = yrs[:2]; break
    if hdr is None: return {}
    out = {}
    for j, yr in hdr:
        rec = {}
        for k, pat in ROWS.items():
            hits = lab[lab.str.match(pat)].index
            if k == 'los_statewide':
                # statewide LOS sits under LENGTH OF STAY; take the first match after that header
                los = lab[lab.str.contains('length of stay')].index
                hits = [h for h in hits if len(los) and h > los[0]]
            for h in hits:
                v = pd.to_numeric(df.iloc[h, j], errors='coerce')
                if pd.notna(v): rec[k] = float(v); break
        out[yr] = rec
    return out

def derive(rec):
    v, aps = rec.get('visitors'), rec.get('avg_party_size')
    p1, p2, p3 = rec.get('party_1'), rec.get('party_2'), rec.get('party_3plus')
    if not all(pd.notna(z) for z in [v, aps, p1, p2, p3]) or not aps: return rec
    parties = v / aps
    parties_1, parties_2 = p1, p2 / 2
    parties_3 = parties - parties_1 - parties_2
    rec.update(parties=parties, share_visitors_1=p1 / v, share_visitors_2=p2 / v, share_visitors_3plus=p3 / v,
               share_parties_1=parties_1 / parties, share_parties_2=parties_2 / parties,
               share_parties_3plus=parties_3 / parties, avg_party_size_3plus=p3 / parties_3 if parties_3 > 0 else np.nan)
    return rec

def annual():
    rows = []
    for f in sorted(glob.glob(f'{RAW}/*-annual-visitor.xls*')):
        report_year = int(os.path.basename(f)[:4]); x = pd.ExcelFile(f)
        for seg, pat in SEGMENTS.items():
            s, title = find_sheet(x, pat)
            if s is None: continue
            tab = parse_table(x.parse(s, header=None))
            for yr, rec in tab.items():
                rec = derive(rec)
                rows.append(dict(segment=seg, year=yr, report_year=report_year, sheet=s, **rec))
    df = pd.DataFrame(rows)
    return df

# ---------------------------------------------------------------- monthly Visitor Highlights
MONTHS = ['JANUARY','FEBRUARY','MARCH','APRIL','MAY','JUNE','JULY','AUGUST','SEPTEMBER','OCTOBER','NOVEMBER','DECEMBER']
ACCOM_ROWS = ['Plan to stay in Hotel','Hotel only','Plan to stay in Condo','Condo only','Plan to stay in Timeshare',
              'Timeshare only','Cruise Ship','Friends/Relatives','Bed & Breakfast','Rental House','Hostel',
              'Camp Site, Beach','Private Room in Private Home','Shared Room/Space in Private Home','Other']

def monthly():
    rows = []
    files = sorted(glob.glob(f'{RAW}/monthly_legacy/20??-??.xls*')) + sorted(glob.glob(f'{RAW}/monthly/*.xlsx'))
    for f in files:
        ym = os.path.basename(f)[:7]; x = pd.ExcelFile(f)
        for sheet, market in [('HL','all'),('US Total','us_total'),('US West','us_west'),('US East','us_east'),('Japan','japan'),('Canada','canada')]:
            if sheet not in x.sheet_names: continue
            d = x.parse(sheet, header=None); lab = d[0].astype(str).str.strip()
            blocks = list(lab[lab.str.contains(r'VISITORS BY AIR\s*$|VISITORS ON DOMESTIC FLIGHTS\s*$|VISITORS ON INTERNATIONAL FLIGHTS\s*$', regex=True)].index)
            blocks = [b for b in blocks if '(CONT' not in lab[b].upper()]
            names = ['total','domestic','international']
            for bi, b in enumerate(blocks[:3]):
                end = blocks[bi+1] if bi+1 < len(blocks) else len(d)
                seg = d.iloc[b:end]; sl = seg[0].astype(str).str.strip()
                hdr = seg[sl.str.upper().isin(MONTHS) | seg[1].astype(str).str.upper().isin(MONTHS)]
                aps = seg[sl.str.match(r'^Ave\.? Party Size', case=False)]
                vis = seg[sl.str.match(r'^(TOTAL )?VISITORS$', case=False)]
                days = seg[sl.str.match(r'^(TOTAL )?VISITOR DAYS$', case=False)]
                if aps.empty: continue
                r = dict(ym=ym, market=market, flight=names[bi], source=os.path.basename(f),
                         party_size_month=aps.iloc[0,1], party_size_month_py=aps.iloc[0,2],
                         party_size_ytd=aps.iloc[0,4], party_size_ytd_py=aps.iloc[0,5])
                if not vis.empty: r.update(visitors_month=vis.iloc[0,1], visitors_month_py=vis.iloc[0,2], visitors_ytd=vis.iloc[0,4], visitors_ytd_py=vis.iloc[0,5])
                if not days.empty: r.update(visitor_days_month=days.iloc[0,1], visitor_days_ytd=days.iloc[0,4])
                for a in ACCOM_ROWS:
                    hit = seg[sl.str.replace(r'\*+$','',regex=True).str.strip().str.lower() == a.lower()]
                    if not hit.empty:
                        key = re.sub(r'[^a-z0-9]+','_',a.lower()).strip('_')
                        r[f'acc_{key}_month'] = hit.iloc[0,1]; r[f'acc_{key}_ytd'] = hit.iloc[0,4]
                rows.append(r)
    return pd.DataFrame(rows)


def annual_highlights():
    """YYYY-highlights.xls(x): final (revised) monthly figures for one calendar year, JAN..DEC in columns."""
    rows = []
    for f in sorted(glob.glob(f'{RAW}/monthly_legacy/annual-*-highlights.xls*')):
        year = int(re.search(r'annual-(\d{4})', f).group(1)); x = pd.ExcelFile(f)
        sheet = 'State' if 'State' in x.sheet_names else x.sheet_names[0]
        d = x.parse(sheet, header=None)
        # label column = the one holding 'Ave. Party Size'
        lc = next((c for c in d.columns if d[c].astype(str).str.strip().str.match(r'^Ave\.? Party Size', case=False).any()), None)
        if lc is None: continue
        lab = d[lc].astype(str).str.strip()
        hdr = d[d.iloc[:, lc+1:lc+13].astype(str).apply(lambda r: list(r.str.upper().str[:3]) == ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'], axis=1)].index
        if len(hdr) == 0: continue
        mcols = list(range(lc+1, lc+13))
        aps_rows = list(lab[lab.str.match(r'^Ave\.? Party Size', case=False)].index)
        for bi, ar in enumerate(aps_rows[:3]):
            start = hdr[bi] if bi < len(hdr) else (aps_rows[bi-1] + 1)
            seg = d.iloc[start:ar+1]; sl = seg[lc].astype(str).str.strip()
            vis = seg[sl.str.match(r'^(TOTAL |DOMESTIC |INTERNATIONAL )?VISITORS$', case=False)]
            for mi, c in enumerate(mcols):
                r = dict(ym=f'{year}-{mi+1:02d}', market='all', flight=['total','domestic','international'][bi],
                         source=os.path.basename(f), party_size_final=pd.to_numeric(d.iloc[ar, c], errors='coerce'))
                if not vis.empty: r['visitors_final'] = pd.to_numeric(vis.iloc[0, c], errors='coerce')
                for a in ACCOM_ROWS:
                    hit = seg[sl.str.replace(r'\*+$', '', regex=True).str.strip().str.lower() == a.lower()]
                    if not hit.empty:
                        key = re.sub(r'[^a-z0-9]+', '_', a.lower()).strip('_')
                        r[f'acc_{key}_final'] = pd.to_numeric(hit.iloc[0, c], errors='coerce')
                rows.append(r)
    return pd.DataFrame(rows)


def monthly_series(m, a):
    """One row per ym x flight (market=all): party size with provenance.
    Priority: final annual-highlights value > current-month preliminary > prior-year column of the next year's release."""
    cur = m[m.market.eq('all')][['ym','flight','party_size_month','visitors_month','source'] + [c for c in m.columns if c.startswith('acc_') and c.endswith('_month')]].copy()
    cur.columns = [c.replace('_month','') for c in cur.columns]; cur['provenance'] = 'monthly_prelim'
    py = m[m.market.eq('all')][['ym','flight','party_size_month_py','visitors_month_py','source']].copy()
    py['ym'] = py.ym.map(lambda s: f'{int(s[:4])-1}-{s[5:]}'); py.columns = ['ym','flight','party_size','visitors','source']; py['provenance'] = 'monthly_prior_year_col'
    fin = a[['ym','flight','party_size_final','visitors_final','source'] + [c for c in a.columns if c.startswith('acc_')]].copy()
    fin.columns = [c.replace('_final','') for c in fin.columns]; fin['provenance'] = 'annual_highlights_final'
    allrows = pd.concat([fin, cur, py], ignore_index=True)
    allrows = allrows[allrows.party_size.notna()]
    allrows['rank'] = allrows.provenance.map({'annual_highlights_final':0,'monthly_prelim':1,'monthly_prior_year_col':2})
    out = allrows.sort_values(['ym','flight','rank']).groupby(['ym','flight']).head(1).drop(columns='rank')
    return out.sort_values(['flight','ym']).reset_index(drop=True)



if __name__ == '__main__':
    pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
    df = annual()
    df.to_csv(f'{OUT}/hawaii_party_size_annual_raw_vintages.csv', index=False)
    # tidy: latest vintage that still carries party size (the following year's report revises the prior year;
    # from the 2016 report the summary and MMA tables dropped the party-size block, so keep the original vintage there)
    ok = df[df.avg_party_size.notna()].sort_values(['segment', 'year', 'report_year'])
    tidy = ok.groupby(['segment', 'year']).tail(1).drop(columns=['sheet'])
    tidy.to_csv(f'{OUT}/hawaii_party_size_annual.csv', index=False)
    wide = tidy.pivot(index='year', columns='segment', values='avg_party_size').round(4)
    wide.to_csv(f'{OUT}/hawaii_party_size_annual_wide.csv')
    print(wide.to_string())
    m = monthly()
    m.to_csv(f'{OUT}/hawaii_party_size_monthly_raw.csv', index=False)
    a = annual_highlights()
    a.to_csv(f'{OUT}/hawaii_party_size_monthly_final_raw.csv', index=False)
    ms = monthly_series(m, a)
    ms.to_csv(f'{OUT}/hawaii_party_size_monthly.csv', index=False)
    t = ms[ms.flight.eq('total')]
    print(t.groupby(t.ym.str[:4]).agg(n=('ym','size'), party_size=('party_size','mean'), prov=('provenance', lambda x: ','.join(sorted(set(x))))).to_string())
    print(m[m.market.eq('all')][['ym','flight','party_size_month','party_size_month_py','party_size_ytd','visitors_month','acc_rental_house_month','acc_hotel_only_month']].to_string())
