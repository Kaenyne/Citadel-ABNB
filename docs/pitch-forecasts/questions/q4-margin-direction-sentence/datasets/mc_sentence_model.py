"""Decomposition Monte Carlo for C04 (FY26 margin sentence) and C09 (4Q26 margin direction sentence).
Dependency-free (numpy only). Inputs are named constants with their repo source in comments.
"""
import numpy as np, csv, json
rng=np.random.default_rng(20260917)
N=400_000
# --- 1H26 actuals (2Q26 letter; 05_nov2026_scenarios.csv) ---
H1_REV=6286.0; H1_EBITDA=1780.0
# --- 3Q26 print: team 49.94% (23_card_5nov) / line build 50.4%; ceiling 50.085 ('down slightly'); Street 49.78.
# Margin: mixture centred 49.95, sd 1.0 (last-4-quarter combination MAE 0.45pp, W1 conformal qhat80 2.2pp -> sd~1.7; take 1.0 as compromise)
q3_margin=rng.normal(49.95,1.0,N)
# Revenue: team 4,804 (bridge v3), Street 4,744, guide 4,690-4,770; sd 60
q3_rev=rng.normal(4790,60,N)
q3_ebitda=q3_margin/100*q3_rev
# --- 4Q26 revenue guide midpoint (C01 object): team implied 3,059 (bridge v3 / Q4 cushion 3.88%), B2 grid 3,127-3,207 (cushion 1.86%), Street 3,158.
# Take guide mid ~ N(3,110, 55). Management's INTERNAL Q4 revenue = guide mid x (1+c), c ~ N(0.025, 0.01) (trailing cushions 1.9% all-quarter, 3.9% Q4-only)
# C01 agent's provisional MC (q4-revenue-guide-vs-street/datasets/c01_mc_summary.csv, 2026-09-17): guide mean 3,089, sd 80, P(below Street 3,158) 0.80
q4_guide=rng.normal(3090,80,N)
cush=rng.normal(0.025,0.010,N)
q4_rev_int=q4_guide*(1+cush)
# --- Management's internal 4Q26 margin expectation. Street 28.90 (LSEG 11 Sep); team line build 28.3; M3 sentence path 29.9;
# historical Q4 actual vs Street-at-Nov: +3.75, +0.92, +0.30. Budget arithmetic (40_line_build): Aug floor 35.5 + 'down slightly' Q3 => Q4 >= ~28.6 at guide revenue.
# Centre 29.3, sd 1.6 (Street h=1 MAE 1.66pp on Q4 across 3 Novembers; realised Q4 sd 2.9).
# operating leverage: +0.5pp of Q4 margin per +1% of Q4 revenue vs 3,190 (held 0.71, flex ~0.45; M6/23_macro_sensitivity), residual sd 1.4
q4_margin_int=29.3+0.5*(q4_rev_int-3190)/31.9+rng.normal(0,1.4,N)
q4_ebitda_int=q4_margin_int/100*q4_rev_int
fy_int=(H1_EBITDA+q3_ebitda+q4_ebitda_int)/(H1_REV+q3_rev+q4_rev_int)*100
# --- Sentence decision rule (from M3/WS05): with a numeric floor F in force, November says 'approximately F+0.5' (2/2),
# provided internal >= F+0.5 - tol. Observed cushions on the November point: +0.77,+0.90,+0.10 => tol ~ 0.15 (2025 case).
# Rule uncertainty: with prob p_rule the +50bp convention dominates when internal clears F+0.5-tol; otherwise a 'round to 50bp below internal+tol' rule.
F=35.5
def sentence(fy, tol, p_rule_draw):
    # returns option label a..e
    out=np.full(fy.shape,'a',dtype='<U1')
    # candidate levels
    lvl=np.floor((fy+tol)/0.5)*0.5   # largest 50bp multiple <= internal+tol
    # Rule A (+50bp convention when affordable)
    condA=(fy>=F+0.5-tol)
    # Under convention: say 36.0 if affordable, else hold/soften
    # Under rounding rule: say lvl if lvl>F (36.0 -> b, >=36.5 -> c); lvl==F -> 'approximately 35.5' (d) or hold (a); lvl<F -> d
    useA=p_rule_draw
    b_A=condA
    c_A=(fy>=F+1.0+0.4)  # only go to 36.5 if internal comfortably >= 36.9 (needs 2024-style 0.4-0.9 cushion) -- rare
    resA=np.where(c_A,'c',np.where(b_A,'b','x'))
    resB=np.where(lvl>=36.5,'c',np.where(lvl>=36.0,'b','x'))
    res=np.where(useA,resA,resB)
    return res
tol=rng.normal(0.15,0.10,N)
p_rule=rng.random(N)<0.65
res=sentence(fy_int,tol,p_rule)
print('P(guide<Street 3158)=%.3f'%(q4_guide<3158).mean())
# 'x' = cannot say 36: split between hold 'at least 35.5' (a) and 'approximately 35.5' (d) and genuine cut (d)
x=(res=='x')
# Among x: if internal < 35.5 (floor genuinely at risk) -> d with 0.85, a 0.15; else hold vs 'approx 35.5': a 0.55 / d 0.45
u=rng.random(N)
risk=fy_int<35.5
res=np.where(x&risk, np.where(u<0.85,'d','a'), res)
res=np.where(x&~risk, np.where(u<0.55,'a','d'), res)
# 'no FY margin sentence' (e): every November with a numeric floor gave one; 3/3 with any FY sentence; assign 2% exogenously
e_draw=rng.random(N)<0.02
res=np.where(e_draw,'e',res)
labels=['a','b','c','d','e']
vec={k:float((res==k).mean()) for k in labels}
print('C04 decomposition vector',vec)
print('internal FY26: mean %.2f sd %.2f p10 %.2f p50 %.2f p90 %.2f'%(fy_int.mean(),fy_int.std(),*np.percentile(fy_int,[10,50,90])))
for th in [35.5,35.75,35.85,36.0,36.25,36.5]: print(' P(internal >= %.2f) = %.3f'%(th,(fy_int>=th).mean()))
# --- C09: Q4 margin direction sentence vs 4Q25 28.29 ---
# Management describes its internal Q4 margin vs LY. Wording bands: |d|<=0.6 -> 'approximately flat/similar'; d>0.6 -> up; d<-0.6 -> down.
# Historical: sentences were 'flat'-family when realised was within about +/-1.3pp (1Q26 'approx flat' realised +1.0; 1Q25 'flat to down slightly' realised +1.2; 4Q22 'slightly down' realised -0.8).
# Note the quarterly sentence is set conservatively (ceiling): realised beat the sentence in most quarters; management's stated direction sits BELOW its internal by ~0.5-1pp. Model: stated = internal - bias, bias ~ N(0.7,0.5).
LY=28.29
bias=rng.normal(0.3,0.4,N)  # quarterly sentence not sandbagged: W2 realised-minus-sentence mean -0.19pp, above in 4/10 (margin build WS22 A)
stated=q4_margin_int-bias-LY
band=rng.normal(0.6,0.2,N)
c09=np.where(stated>band,'c',np.where(stated<-band,'a','b'))
noq=rng.random(N)<0.05  # no Q4 margin sentence (5/5 Novembers had one; every quarter since 2Q21 had one)
c09=np.where(noq,'d',c09)
vec9={k:float((c09==k).mean()) for k in ['a','b','c','d']}
print('C09 decomposition vector',vec9)
# coupling: sentence (b) given C09 up etc.
for k in ['a','b','c']:
    m=c09==k
    print(' P(C04 in b|c09=%s)=%.3f  P(C04 in a or d|c09=%s)=%.3f'%(k,((res=='b')|(res=='c'))[m].mean(),k,((res=='a')|(res=='d'))[m].mean()))
# conditional on Q4 guide below Street 3158
below=q4_guide<3158
print('P(guide<Street)=%.3f; P(C04=b or c | below)=%.3f ; | not below=%.3f'%(below.mean(),((res=='b')|(res=='c'))[below].mean(),((res=='b')|(res=='c'))[~below].mean()))
# sensitivities
def run(q4c=29.3,q3c=49.95,prule=0.65,tolc=0.15,gm=3090,gsd=80):
    q3m=rng.normal(q3c,1.0,N); q3r=rng.normal(4790,60,N); q4g=rng.normal(gm,gsd,N); cu=rng.normal(0.025,0.01,N)
    q4r=q4g*(1+cu); q4m=q4c+0.5*(q4r-3190)/31.9+rng.normal(0,1.4,N)
    fy=(H1_EBITDA+q3m/100*q3r+q4m/100*q4r)/(H1_REV+q3r+q4r)*100
    tl=rng.normal(tolc,0.10,N); pr=rng.random(N)<prule
    r=sentence(fy,tl,pr); xx=(r=='x'); uu=rng.random(N); rk=fy<35.5
    r=np.where(xx&rk,np.where(uu<0.85,'d','a'),r); r=np.where(xx&~rk,np.where(uu<0.55,'a','d'),r)
    r=np.where(rng.random(N)<0.02,'e',r)
    return {k:round(float((r==k).mean()),3) for k in labels}
sens={'base':run(),'q4_internal_28.3(line build)':run(q4c=28.3),'q4_internal_30.0(M3 path)':run(q4c=30.0),'q3_49.4(slightly=0.7)':run(q3c=49.4),'q3_50.4(line build)':run(q3c=50.4),'p_rule_0.85':run(prule=0.85),'p_rule_0.40':run(prule=0.40),'tol_0.0':run(tolc=0.0),'tol_0.30':run(tolc=0.30),'guide_mid_3059(bridge v3 implied)':run(gm=3059),'guide_mid_3160(at Street)':run(gm=3160),'guide_mid_2985(C01 p10)':run(gm=2985),'guide_mid_3190(C01 p90)':run(gm=3190),'q3_52.4(evidence build)':run(q3c=52.4)}
for k,v in sens.items(): print(k,v)
with open('mc_sentence_results.json','w') as f: json.dump({'c04_decomposition':vec,'c09_decomposition':vec9,'sensitivities':sens,'internal_fy26':{'mean':float(fy_int.mean()),'sd':float(fy_int.std()),'p10':float(np.percentile(fy_int,10)),'p50':float(np.percentile(fy_int,50)),'p90':float(np.percentile(fy_int,90))},'N':N,'seed':20260917},f,indent=1)
