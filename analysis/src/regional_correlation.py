"""Regional test: Airbnb revenue growth by listing region vs IATA RPK growth by airline region.
Quarterly, 2024Q1-2026Q2 (IATA regional series collected from Jan 2024)."""
import csv, numpy as np
from collections import defaultdict
rev={r['quarter']:r for r in csv.DictReader(open('data/processed/airbnb_regional_revenue_quarterly.csv'))}
regions={'north_america':'north_america_usd_m','europe':'emea_usd_m','latin_america':'latam_usd_m','asia_pacific':'apac_usd_m'}
def yoy(q,col):
    y=int(q[:4]); p=f"{y-1}{q[4:]}"
    return (float(rev[q][col])/float(rev[p][col])-1)*100 if p in rev else None
iata=defaultdict(list)
for r in csv.DictReader(open('data/processed/iata_rpk_yoy_by_region_monthly.csv')):
    y,m=r['month'].split('-'); q=f"{y}Q{(int(m)-1)//3+1}"
    for reg in regions: iata[(reg,q)].append(float(r[reg]))
quarters=[f"{y}Q{i}" for y in (2024,2025,2026) for i in (1,2,3,4) if f"{y}Q{i}"<="2026Q2"]
print("Region | quarters | r(air RPK yoy, Airbnb regional revenue yoy) | avg air yoy | avg Airbnb yoy")
for reg,col in regions.items():
    a=[];b=[]
    for q in quarters:
        if (reg,q) in iata and len(iata[(reg,q)])>=2 and yoy(q,col) is not None:
            a.append(np.mean(iata[(reg,q)])); b.append(yoy(q,col))
    r=np.corrcoef(a,b)[0,1]
    print(f"{reg:14s} | n={len(a)} | r={r:+.2f} | {np.mean(a):+.1f}% | {np.mean(b):+.1f}%")
print("\nQuarterly detail (air RPK yoy -> Airbnb revenue yoy):")
for q in quarters:
    row=[q]
    for reg,col in regions.items():
        row.append(f"{reg[:5]} {np.mean(iata[(reg,q)]):+.1f}->{yoy(q,col):+.1f}")
    print("  ".join(row))
# cross-sectional: do regions with faster air growth have faster Airbnb growth (averages 2024Q1-2026Q2)?
avg_air=[];avg_ab=[]
for reg,col in regions.items():
    a=[np.mean(iata[(reg,q)]) for q in quarters]; b=[yoy(q,col) for q in quarters]
    avg_air.append(np.mean(a)); avg_ab.append(np.mean(b))
print(f"\nCross-sectional (4 regions, 2024-26 averages): r={np.corrcoef(avg_air,avg_ab)[0,1]:+.2f}")
