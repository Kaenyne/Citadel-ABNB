"""B14: Cat 3+ (>=96 kt) hurricane landfalls ('L' records, status HU) in Florida, Texas, North Carolina, South Carolina
from HURDAT2 (NHC best track, ../sources/hurdat2-1851-2025.txt). Window 17 Sep - 31 Dec. Writes b14_landfalls.csv, b14_base_rates.csv."""
import csv, os, collections
os.chdir(os.path.dirname(os.path.abspath(__file__)))
lines=open('../sources/hurdat2-1851-2025.txt').read().splitlines()
storms=[]; cur=None
for ln in lines:
    p=[x.strip() for x in ln.split(',')]
    if p[0].startswith('AL'): cur={'id':p[0],'name':p[1],'rows':[]}; storms.append(cur)
    else: cur['rows'].append(p)
def region(lat,lon):
    if -97.9<=lon<=-93.8 and 25.8<=lat<=30.2: return 'TX'
    if -87.6<=lon<=-79.8 and 24.4<=lat<=31.0: return 'FL'
    if -81.7<=lon<=-80.7 and 30.7<=lat<=32.1: return 'GA'
    if -81.1<=lon<=-78.4 and 32.0<=lat<=33.95: return 'SC'
    if -78.6<=lon<=-75.3 and 33.8<=lat<=36.6: return 'NC'
    return None
ev=[]
for s in storms:
    for r in s['rows']:
        if r[2]!='L' or r[3]!='HU': continue
        lat=float(r[4][:-1])*(1 if r[4][-1]=='N' else -1); lon=float(r[5][:-1])*(-1 if r[5][-1]=='W' else 1); w=int(r[6]); reg=region(lat,lon)
        if w>=96 and reg in ('FL','TX','NC','SC'): ev.append(dict(year=int(r[0][:4]),date=r[0],storm=s['name'],state=reg,wind_kt=w,lat=lat,lon=lon))
with open('b14_landfalls.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=ev[0].keys()); w.writeheader(); w.writerows(ev)
yrs=collections.defaultdict(list)
for e in ev: yrs[e['year']].append(e)
last=2025
out=[]
for start in (1851,1900,1950,1966,1991,2000):
    n=last-start+1
    for cut,lab in (('0917','after 17 Sep'),('1001','after 1 Oct'),('1015','after 15 Oct'),('1101','after 1 Nov')):
        hit=sum(1 for y in range(start,last+1) if any(e['date'][4:]>=cut for e in yrs.get(y,[])))
        out.append(dict(period=f'{start}-{last}',window=lab,years_hit=hit,years=n,rate=round(hit/n,3)))
    hit=sum(1 for y in range(start,last+1) if yrs.get(y)); out.append(dict(period=f'{start}-{last}',window='any month',years_hit=hit,years=n,rate=round(hit/n,3)))
with open('b14_base_rates.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=out[0].keys()); w.writeheader(); w.writerows(out)
for o in out: print(o)
print('window (>=17 Sep) years since 1950:',sorted({e['year'] for e in ev if e['year']>=1950 and e['date'][4:]>='0917'}))
print('events in window since 1950:',[(e['date'],e['storm'],e['state'],e['wind_kt']) for e in ev if e['year']>=1950 and e['date'][4:]>='0917'])
# El Nino analog years (ASO RONI >= 1.0 per CPC table in the Fall Cup log claim 17): 1957,1963,1965,1972,1982,1987,1994,1997,2002,2015,2023
en=[1957,1963,1965,1972,1982,1987,1994,1997,2002,2015,2023]
print('El Nino analogs with Cat3+ FL/TX/NC/SC landfall after 17 Sep:',[y for y in en if any(e['date'][4:]>='0917' for e in yrs.get(y,[]))],'of',len(en))
print('El Nino analogs with any Cat3+ FL/TX/NC/SC landfall:',[y for y in en if yrs.get(y)])
