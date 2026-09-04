"""Cross-sectional check: latest air-arrival YoY vs latest STR-demand YoY across popular vacation destinations.
Caveat: STR metrics differ by destination (occupancy / RevPAR / revenue / unit-night demand) and periods differ (monthly vs TTM)."""
import csv, numpy as np
rows=[r for r in csv.DictReader(open('data/processed/destination_air_vs_str_snapshot.csv')) if r['str_yoy_pct']]
a=[float(r['air_yoy_pct']) for r in rows]; b=[float(r['str_yoy_pct']) for r in rows]
print("destination | air yoy | STR yoy (metric)")
for r in rows: print(f"{r['destination']:10s} | {float(r['air_yoy_pct']):+.1f}% | {float(r['str_yoy_pct']):+.1f}% ({r['str_metric']})")
print(f"\nCross-sectional Pearson r across {len(rows)} destinations: {np.corrcoef(a,b)[0,1]:+.2f}")
same=sum(1 for x,y in zip(a,b) if (x>0)==(y>0)); print(f"Same sign: {same}/{len(rows)}")
