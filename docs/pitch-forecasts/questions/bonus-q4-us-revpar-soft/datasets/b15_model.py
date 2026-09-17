"""B15: P(STR/CoStar US hotel RevPAR y/y for 4Q26 <= +1.0%). Reuses the R11 distribution (centre +3.5, sd 1.7, normal) and
adds an explicit left-tail branch for discrete downside shocks (CR-expiry shutdown 11 Dec, a consumer/airfare-rationing
recession, a full unwind of the summer premium). Constraint: P(>= +4) must stay ~0.38 so R11 and B15 remain one object.
numpy/scipy only; writes b15_views.csv, b15_sensitivity.csv."""
import numpy as np, csv, os
from scipy.stats import norm
os.chdir(os.path.dirname(os.path.abspath(__file__)))
R11_C, R11_SD = 3.5, 1.7   # research-log R11 claim 9
def p_le(x,c,s): return norm.cdf((x-c)/s)
def p_ge(x,c,s): return 1-norm.cdf((x-c)/s)
views={}
views['r11_normal']=dict(p_le1=p_le(1.0,R11_C,R11_SD),p_ge4=p_ge(4.0,R11_C,R11_SD),p_le0=p_le(0,R11_C,R11_SD))
# mixture: (1-w) x normal(c1,s1) 'trend' + w x normal(c2,s2) 'shock' (shutdown/recession/summer premium fully unwound)
def mix(w,c1,s1,c2,s2):
    return dict(p_le1=(1-w)*p_le(1,c1,s1)+w*p_le(1,c2,s2), p_ge4=(1-w)*p_ge(4,c1,s1)+w*p_ge(4,c2,s2), p_le0=(1-w)*p_le(0,c1,s1)+w*p_le(0,c2,s2),
                mean=(1-w)*c1+w*c2)
base=dict(w=0.10,c1=3.7,s1=1.6,c2=0.8,s2=1.8)
views['mixture_base']=mix(**base)
# base rate: post-recovery quarters (R11 claim 10 list, 2023Q2-2026Q2) with y/y <= +1
hist=[3,1.5,2,1,1,2,3,0,-0.5,-1,0,3.8,5.2]
views['base_rate_2023Q2_2026Q2']=dict(p_le1=float(np.mean(np.array(hist)<=1.0)),n=len(hist))
views['base_rate_2024_2025']=dict(p_le1=float(np.mean(np.array(hist[3:11])<=1.0)),n=8)
# what a <=1 quarter needs: given Oct-25 -0.9 / Nov-25 ~+1 / Dec-25 ~ -1 (FY25 -0.3), a 4Q26 y/y of +1 means RevPAR level ~flat vs 4Q24, i.e. the
# Q4 level falls back to the 2024 level despite ADR inflation ~+2: demand (occupancy) about -1 to -2 y/y.
with open('b15_views.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['view','p_le1','p_ge4','p_le0','mean_or_n'])
    for k,v in views.items(): w.writerow([k,round(v.get('p_le1',float('nan')),4),round(v.get('p_ge4',float('nan')),4),round(v.get('p_le0',float('nan')),4),v.get('mean',v.get('n',''))])
sens=[('base',base)]
for name,kw in [('shock weight 0.05',dict(base,w=0.05)),('shock weight 0.20',dict(base,w=0.20)),('shock centre 0.0',dict(base,c2=0.0)),('shock centre +1.5',dict(base,c2=1.5)),
                ('trend centre 3.1 (FY-implied only)',dict(base,c1=3.1)),('trend centre 4.0 (AR path)',dict(base,c1=4.0)),('trend sd 1.2',dict(base,s1=1.2)),('trend sd 2.2',dict(base,s1=2.2)),
                ('December shutdown realised (trend -1.6)',dict(base,c1=2.1)),('October prints <= +2',dict(base,c1=2.0,s1=1.2)),('October prints >= +4',dict(base,c1=4.6,s1=1.2)),
                ('joint bear (w .2, c1 3.1, c2 0)',dict(base,w=0.2,c1=3.1,c2=0.0)),('joint bull (w .05, c1 4.0)',dict(base,w=0.05,c1=4.0))]:
    sens.append((name,kw))
with open('b15_sensitivity.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['case','w','c1','s1','c2','s2','p_le1','p_ge4'])
    for name,kw in sens:
        r=mix(**kw); w.writerow([name,kw['w'],kw['c1'],kw['s1'],kw['c2'],kw['s2'],round(r['p_le1'],4),round(r['p_ge4'],4)])
print(open('b15_views.csv').read()); print(open('b15_sensitivity.csv').read())
