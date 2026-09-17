"""R11: P(STR/CoStar US hotel RevPAR y/y for 4Q26 (Oct-Dec) >= +4.0%).
numpy/scipy only. Writes r11_path.csv, r11_views.csv, r11_sensitivity.csv.
Inputs (research-log.md claims): monthly/weekly STR prints 2026, the CoStar/TE FY26 forecast (+4.4%, 10 Aug 2026), the June forecast (+2.8%, 2 Jun),
the 4Q25 base (Oct -0.9%, FY25 -0.3%), operator H2 guides, calendar items (midterm week 3 Nov, CR to 11 Dec).
"""
import numpy as np, csv, os
from scipy.stats import norm
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# --- 1. Implied 4Q26 from the FY26 forecast (RevPAR-weighted quarters ~ equal weights; Q3 slightly heavier)
# 2026 monthly reads: Jan-Apr +4.0 (CoStar Jun forecast text; Q1 'highest on record'); Mar +5.9; Jun World Cup (+1.7pp lift Jun-Jul per TE); Jul +8.2;
# Aug weeks +7.3, +7.2, +6.2, +4.4, +1.7, +16.1 (Labor Day pair 1.7/16.1 averages ~+8.9 but the clean mid-Aug slope is +7 -> +4)
q1=3.8; q2_lo,q2_hi=4.5,6.0; q3_lo,q3_hi=4.5,6.0   # Q3: Jul 8.2, Aug ~5.5, Sep ~3 (decel) -> ~5.5; range for uncertainty
w=np.array([0.23,0.26,0.27,0.24])  # RevPAR weights (Q3 highest ADR/occ, Q4 lowest)
rows=[]
for q2 in [q2_lo,5.2,q2_hi]:
    for q3 in [q3_lo,5.2,q3_hi]:
        for fy in [4.0,4.4,4.8]:
            q4=(fy-w[0]*q1-w[1]*q2-w[2]*q3)/w[3]; rows.append((q2,q3,fy,round(q4,2)))
with open('r11_path.csv','w',newline='') as f:
    wr=csv.writer(f); wr.writerow(['q2_assumed','q3_assumed','fy26_forecast','implied_q4']); wr.writerows(rows)
implied=np.array([r[3] for r in rows]); print('implied Q4 from FY26 forecast: mean',implied.mean().round(2),'range',implied.min().round(2),implied.max().round(2))
# --- 2. AR(1) on quarterly US RevPAR y/y (persistence ~0.6 at one quarter, 0.36 at two) from a trend quarter of ~+5.5 (Q3) toward a long-run ~+2 (TE 2027 +2.1)
def ar_path(q3=5.5,phi=0.6,lr=2.0): return lr+phi*(q3-lr)
# --- 3. calendar / base adjustments (pp on 4Q26 y/y): easy 4Q25 comp (Oct -0.9, FY25 -0.3, shutdown Oct-Nov 2025): +0.5 to +1.0;
# midterm election week 3 Nov 2026 vs the Nov 2025 easy election comp (+6.2% early Nov 2025 'came from a straightforward comparison'): -0.7;
# CR expiry 11 Dec 2026 (shutdown risk, DC/gov demand): -0.2 expected; Thanksgiving/Christmas day-of-week: ~0
adj_mu=0.8-0.7-0.2; adj_sd=0.5
views={}
# decomposition: STR-implied centre + AR(1) blend + adjustments
centre_str=implied.mean(); centre_ar=ar_path(); centre=0.5*centre_str+0.5*centre_ar+adj_mu
sd=np.sqrt(1.6**2+adj_sd**2)   # 1.6pp: STR forecast revision scale (FY26 2.8 -> 4.4 in two months) at a 3-4 month horizon
views['decomposition']=(centre,sd,1-norm.cdf((4.0-centre)/sd))
views['str_implied_only']=(centre_str+adj_mu,1.7,1-norm.cdf((4.0-centre_str-adj_mu)/1.7))
views['ar1_only']=(centre_ar+adj_mu,1.8,1-norm.cdf((4.0-centre_ar-adj_mu)/1.8))
# base rate: share of US quarterly RevPAR y/y >= 4% since 2023 (post-recovery): 2023 Q1 ~+12 (recovery), Q2 ~+3, Q3 ~+1.5, Q4 ~+2; 2024 Q1 ~+1, Q2 ~+1, Q3 ~+2, Q4 ~+3; 2025 ~ -1..+1 x4; 2026 Q1 +3.8, Q2 ~+5.2
hist=[12,3,1.5,2,1,1,2,3,0,-0.5,-1,0,3.8,5.2]
views['base_rate_unconditional']=(np.mean(hist[1:]),np.std(hist[1:]),np.mean(np.array(hist[1:])>=4.0))
# regime-conditioned base rate: quarters that followed a quarter >= +5: only 2023Q1 (recovery, excluded) -> use the AR(1) two-step from +5.5: same as ar1_only
with open('r11_views.csv','w',newline='') as f:
    wr=csv.writer(f); wr.writerow(['view','centre_or_mean','sd','p_ge_4'])
    for k,v in views.items(): wr.writerow([k,round(v[0],3),round(v[1],3),round(v[2],4)])
    wr.writerow(['anchor_TE_forecast_implied',round(centre_str,2),1.7,round(1-norm.cdf((4.0-centre_str)/1.7),4)])
# sensitivities
with open('r11_sensitivity.csv','w',newline='') as f:
    wr=csv.writer(f); wr.writerow(['case','centre','sd','p_ge_4'])
    for name,c,s in [('base',centre,sd),('Q3 runs +6.5 (Aug/Sep hold +6)',0.5*((4.4-w[0]*q1-w[1]*5.2-w[2]*6.5)/w[3])+0.5*ar_path(6.5)+adj_mu,sd),
                     ('Q3 runs +4.5 (Sep fades to +2)',0.5*((4.4-w[0]*q1-w[1]*5.2-w[2]*4.5)/w[3])+0.5*ar_path(4.5)+adj_mu,sd),
                     ('FY26 forecast cut to +4.0 in Nov',0.5*((4.0-w[0]*q1-w[1]*5.2-w[2]*5.5)/w[3])+0.5*centre_ar+adj_mu,sd),
                     ('FY26 raised to +4.8',0.5*((4.8-w[0]*q1-w[1]*5.2-w[2]*5.5)/w[3])+0.5*centre_ar+adj_mu,sd),
                     ('no election/CR drag (adj +0.8)',centre+0.9,sd),('shutdown in Dec (adj -1.5)',centre-1.6,sd),
                     ('AR phi 0.8 (persistence high)',0.5*centre_str+0.5*ar_path(phi=0.8)+adj_mu,sd),('AR phi 0.4',0.5*centre_str+0.5*ar_path(phi=0.4)+adj_mu,sd),
                     ('sd 1.2',centre,1.2),('sd 2.2',centre,2.2),('joint bull (Q3 6.5, FY 4.8, no drag, phi 0.8)',0.5*((4.8-w[0]*q1-w[1]*5.2-w[2]*6.5)/w[3])+0.5*ar_path(6.5,0.8)+0.8,sd),
                     ('joint bear (Q3 4.5, FY 4.0, shutdown)',0.5*((4.0-w[0]*q1-w[1]*5.2-w[2]*4.5)/w[3])+0.5*ar_path(4.5)-1.5,sd)]:
        wr.writerow([name,round(c,2),round(s,2),round(1-norm.cdf((4.0-c)/s),4)])
print(open('r11_views.csv').read()); print(open('r11_sensitivity.csv').read())
# conditional mean given yes
c,s=centre,sd; z=(4.0-c)/s; e_yes=c+s*norm.pdf(z)/(1-norm.cdf(z)); print('E[RevPAR|>=4]',round(e_yes,2),'centre',round(c,2),'sd',round(s,2))
