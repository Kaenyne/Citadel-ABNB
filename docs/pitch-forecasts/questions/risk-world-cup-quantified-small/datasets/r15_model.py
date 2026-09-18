"""R15: P(by the Feb 2027 print management quantifies the 2026 World Cup's contribution to nights/GBV at <=1pt, or states it was immaterial).
Pure arithmetic (no randomness). Writes r15_tree.csv, r15_sensitivity.csv, r15_event_record.csv.
"""
import csv, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# Event-discussion record (letters + calls), coded: points figure given? size language?
rec=[("1Q24 letter/call","Paris 2024 / Euro Cup / eclipse","nights booked 5x / 2x; 500k eclipse guests; listings +40%","no points","none"),
     ("2Q24 letter/call","Paris 2024","nights >2x; 400k-430k guests; listings +37%; 'impact of a single city for a limited duration is relatively small compared to total nights booked in a region'","no points","relatively small (region)"),
     ("3Q24 letter/call","Paris 2024","'slight acceleration in EMEA buoyed by the Games'; 700k guests; supply +35%","no points","none"),
     ("4Q24 call","Paris 2024","700k guests; 100k->150k homes","no points","none"),
     ("3Q25 letter","Paris lap","'slightly unfavorable year-over-year comparison within the region due to the Paris Games'","no points","qualitative headwind"),
     ("4Q25 call","World Cup / Milan preview","'biggest event on Earth'; events 'incremental but not primary growth' (Q&A, Anmuth)","no points","none"),
     ("1Q26 letter/call","Milan 2026 / World Cup","200k guests, supply +30%, GBV >3x in host markets; WC 'largest event in Airbnb's history'; Q&A (Nick Jones) answered qualitatively","no points","none"),
     ("2Q26 letter/call","World Cup","'millions of guest arrivals', 150k first-time listings; 'bookings from any single event may be temporary'; 'no single product'","no points","temporary (not sized)")]
with open('r15_event_record.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['print','event','statements','points_figure','size_language']); w.writerows(rec)
n_points=sum(1 for r in rec if r[3]!='no points'); n=len(rec)
laplace=(n_points+1)/(n+2)
# Tree: routes to Yes across the two prints (5 Nov 2026, ~11 Feb 2027) incl. Q&A and 10-Q/10-K
p={
 'A_nov_points_le1':0.02,   # a <=1pt WC figure for 2Q/3Q26 in the 5 Nov letter/call (record 0/8; Middle-East-style quantification is for exogenous drags)
 'A_feb_points_le1':0.04,   # a quantified 2Q27/3Q27 WC lap headwind <=1pt in the Feb letter/call FY27 framing (management flags laps qualitatively; ME '~100bps' precedent is next-quarter)
 'B_nov_immaterial':0.05,   # 'not a meaningful driver'/'relatively small' applied to the WC's growth contribution (2Q24 precedent for Paris; Q&A ask likely on the 3Q26 deceleration)
 'B_feb_immaterial':0.05,   # same at Feb when the 2Q27 comp is discussed; incentive to defuse the comp
}
p_any=1-(1-p['A_nov_points_le1'])*(1-p['A_feb_points_le1'])*(1-p['B_nov_immaterial'])*(1-p['B_feb_immaterial'])
with open('r15_tree.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['route','p'])
    for k,v in p.items(): w.writerow([k,v])
    w.writerow(['P_yes_any_route',round(p_any,4)]); w.writerow(['laplace_points_per_event_discussion',round(laplace,3)]); w.writerow(['n_event_discussions',n]); w.writerow(['n_with_points',n_points])
def tot(**kw):
    q=dict(p); q.update(kw); return 1-(1-q['A_nov_points_le1'])*(1-q['A_feb_points_le1'])*(1-q['B_nov_immaterial'])*(1-q['B_feb_immaterial'])
sens=[('base',{}),('lenient resolver: "may be temporary"/"relatively small" style counts (B routes x2)',dict(B_nov_immaterial=0.10,B_feb_immaterial=0.10)),
      ('strict resolver: only explicit "not material/meaningful to growth" (B routes /2)',dict(B_nov_immaterial=0.025,B_feb_immaterial=0.025)),
      ('management turns numeric on laps (Feb points 0.10)',dict(A_feb_points_le1=0.10)),
      ('3Q26 decelerates sharply and analysts press for attribution (Nov routes x2)',dict(A_nov_points_le1=0.04,B_nov_immaterial=0.10)),
      ('WC figure given but >1pt (resolves No; A routes 0)',dict(A_nov_points_le1=0.0,A_feb_points_le1=0.0)),
      ('joint bull (lenient, numeric, pressed)',dict(A_nov_points_le1=0.04,A_feb_points_le1=0.10,B_nov_immaterial=0.12,B_feb_immaterial=0.12)),
      ('joint bear (strict, no numbers)',dict(A_nov_points_le1=0.01,A_feb_points_le1=0.02,B_nov_immaterial=0.02,B_feb_immaterial=0.02))]
with open('r15_sensitivity.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['case','p_yes'])
    for name,kw in sens: w.writerow([name,round(tot(**kw),4)])
print(open('r15_tree.csv').read()); print(open('r15_sensitivity.csv').read())
