"""Aggregate test: US/global air traffic growth vs Airbnb KPIs and stock, quarterly.
Reads data/*.csv. Run: python analysis/aggregate_correlation.py"""
import csv, numpy as np
from collections import defaultdict
def qtr(m): y,mm=m.split('-'); return f"{y}Q{(int(mm)-1)//3+1}"
# TSA: sum months -> quarter, then YoY (needs 3 full months)
tsa_m=defaultdict(list)
for r in csv.DictReader(open('data/processed/tsa_checkpoint_monthly.csv')): tsa_m[qtr(r['month'])].append(int(r['travelers_screened']))
tsa_lvl={q:sum(v)/1e6 for q,v in tsa_m.items() if len(v)==3}
tsa_yoy={q:(v/tsa_lvl[f"{int(q[:4])-1}{q[4:]}"]-1)*100 for q,v in tsa_lvl.items() if f"{int(q[:4])-1}{q[4:]}" in tsa_lvl}
# BTS: avg of reported simple YoY (NSA, from 2023-03)
bts_m=defaultdict(list)
for r in csv.DictReader(open('data/processed/bts_us_airline_passengers_monthly.csv')):
    if r['month']>='2023-03' and r['yoy_pct_as_reported']: bts_m[qtr(r['month'])].append(float(r['yoy_pct_as_reported']))
bts={q:np.mean(v) for q,v in bts_m.items()}
iata_t=defaultdict(list); iata_i=defaultdict(list)
for r in csv.DictReader(open('data/processed/iata_rpk_yoy_monthly.csv')):
    iata_t[qtr(r['month'])].append(float(r['total_rpk_yoy_pct'])); iata_i[qtr(r['month'])].append(float(r['international_rpk_yoy_pct']))
iata_t={q:np.mean(v) for q,v in iata_t.items() if len(v)==3}; iata_i={q:np.mean(v) for q,v in iata_i.items() if len(v)==3}
nights={};gbv={};rev={};nl={}
for r in csv.DictReader(open('data/processed/airbnb_quarterly_kpis.csv')):
    nights[r['quarter']]=float(r['nights_yoy_pct']); gbv[r['quarter']]=float(r['gbv_yoy_pct_as_reported']); rev[r['quarter']]=float(r['revenue_yoy_pct_as_reported']); nl[r['quarter']]=float(r['nights_and_seats_booked_m'])
px={}
for r in csv.DictReader(open('data/processed/abnb_monthly_close.csv')):
    if r['month'][5:] in ('03','06','09','12'): px[qtr(r['month'])]=float(r['close_usd'])
labs=[f"{y}Q{i}" for y in range(2021,2027) for i in range(1,5)]
ret={b:(px[b]/px[a]-1)*100 for a,b in zip(labs[:-1],labs[1:]) if a in px and b in px}
def corr(x,y,keys):
    ks=[k for k in keys if k in x and k in y]
    return (np.corrcoef([x[k] for k in ks],[y[k] for k in ks])[0,1] if len(ks)>=4 else float('nan')), len(ks)
full=[k for k in labs if "2023Q1"<=k<="2026Q2"]; post=[k for k in labs if "2024Q1"<=k<="2026Q2"]
series={"TSA yoy":tsa_yoy,"BTS yoy":bts,"IATA total":iata_t,"IATA intl":iata_i}
targets={"Nights yoy":nights,"GBV yoy":gbv,"Rev yoy":rev,"Stock qtr ret":ret}
print("Same-quarter Pearson r (n): 2023Q1-2026Q2 | 2024Q1-2026Q2")
for sn,s in series.items():
    for tn,t in targets.items():
        (r1,n1),(r2,n2)=corr(s,t,full),corr(s,t,post)
        print(f"{sn:11s} vs {tn:14s}: {r1:+.2f} (n={n1}) | {r2:+.2f} (n={n2})")
print("\nLead/lag: air yoy (t) vs Nights yoy (t+1), 2023-2026")
for sn,s in series.items():
    lag={labs[i+1]:s[labs[i]] for i in range(len(labs)-1) if labs[i] in s}
    r,n=corr(lag,nights,full); print(f"{sn:11s}: {r:+.2f} (n={n})")
r,n=corr(tsa_lvl,nl,full); print(f"\nLevels: TSA quarterly screenings vs nights booked: r={r:+.2f} (n={n})")
print("\nQuarter, TSA, BTS, IATAtot, IATAintl, Nights, GBV, Rev, StockRet")
for k in full:
    g=lambda d: f"{d[k]:+.1f}" if k in d else "-"
    print(k, g(tsa_yoy), g(bts), g(iata_t), g(iata_i), g(nights), g(gbv), g(rev), g(ret))
