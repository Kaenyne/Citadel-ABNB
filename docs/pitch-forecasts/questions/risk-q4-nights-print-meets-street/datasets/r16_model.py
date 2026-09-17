"""R16: P(4Q26 Nights and Seats Booked >= 134.0m, i.e. >= +9.93% y/y on 121.9m).
numpy only. Seed 20260917. Writes r16_summary.csv, r16_sensitivity.csv, r16_conditional.csv.
Inputs (all repo-sourced, see research-log.md claims):
  Q3 print distribution: R01 final-calibrated N(9.67, 1.70)   (P(>=10.0)=0.42)
  Q4 centre given Q3 = team case B 8.1 (RNPL module 7.61; case A 8.9; Street 9.93)
  Q3->Q4 pass-through beta (corr) 0.5 (F01 convention), residual sd 1.4
  Short tail: 12% mass at 5.5 +/- 1.5 (F01), correlated with Q3 via the same draw
"""
import numpy as np, csv
rng=np.random.default_rng(20260917); N=400_000
BASE=121.9; THR=134.0; thr_g=(THR/BASE-1)*100  # 9.926
REF=9.67  # Q3 reference centre the Q4 centres are conditioned on
def run(q3_mu=9.67,q3_sd=1.70,q4_mu=8.1,beta=0.5,res_sd=1.4,tail_w=0.12,tail_mu=5.5,tail_sd=1.5,q3_cond=None):
    q3=rng.normal(q3_mu,q3_sd,N)
    if q3_cond is not None:
        lo,hi=q3_cond; keep=(q3>=lo)&(q3<hi); q3=q3[keep]
    n=len(q3)
    tail=rng.random(n)<tail_w
    q4=q4_mu+beta*(q3-REF)+rng.normal(0,res_sd,n)
    q4_tail=tail_mu+0.5*(q3-REF)+rng.normal(0,tail_sd,n)
    q4=np.where(tail,q4_tail,q4)
    nights=BASE*(1+q4/100)
    p=(nights>=THR-0.05).mean()   # printed to 0.1m: 134.0 resolves Yes
    return p, q4.mean(), q4.std(), (q4[nights>=THR-0.05].mean() if p>0 else np.nan), n
base=run()
rows=[("base",)+base]
sens=[
 ("q4 centre = RNPL module 7.61",dict(q4_mu=7.61)),
 ("q4 centre = case A NA-only lap 8.9",dict(q4_mu=8.9)),
 ("q4 centre = Street bar 9.93, no short tail",dict(q4_mu=9.93,tail_w=0.0)),
 ("q4 centre = bridge pattern no-lap 10.6",dict(q4_mu=10.6,tail_w=0.0)),
 ("no short tail",dict(tail_w=0.0)),
 ("short tail 25%",dict(tail_w=0.25)),
 ("beta 0.3",dict(beta=0.3)),("beta 0.8",dict(beta=0.8)),
 ("residual sd 1.0",dict(res_sd=1.0)),("residual sd 2.0",dict(res_sd=2.0)),
 ("Q3 centre 9.2 (external stack)",dict(q3_mu=9.2)),("Q3 centre 9.9 (team baseline)",dict(q3_mu=9.9)),
 ("Q3 sd 2.16 (naive)",dict(q3_sd=2.16)),
 ("joint bull: q4 8.9, beta 0.8, no tail, Q3 9.9",dict(q4_mu=8.9,beta=0.8,tail_w=0.0,q3_mu=9.9)),
 ("joint bear: q4 7.61, tail 25%, Q3 9.2",dict(q4_mu=7.61,tail_w=0.25,q3_mu=9.2)),
]
with open("r16_sensitivity.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["case","p_yes","q4_mean","q4_sd","e_q4_given_yes","n"])
    w.writerow(["base"]+[round(x,4) for x in base])
    for name,kw in sens:
        r=run(**kw); w.writerow([name]+[round(x,4) for x in r])
# conditional on Q3 bands
with open("r16_conditional.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["q3_band","p_yes","q4_mean","e_q4_given_yes","n"])
    for lo,hi in [(-99,9.0),(9.0,10.0),(10.0,10.6),(10.6,99)]:
        r=run(q3_cond=(lo,hi)); w.writerow([f"[{lo},{hi})",round(r[0],4),round(r[1],3),round(r[3],3),r[4]])
with open("r16_summary.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["item","value"])
    w.writerow(["threshold_growth_pct",round(thr_g,3)]); w.writerow(["p_yes_base",round(base[0],4)])
    w.writerow(["q4_mean",round(base[1],3)]); w.writerow(["q4_sd",round(base[2],3)]); w.writerow(["e_q4_given_yes",round(base[3],3)])
print("threshold growth",thr_g); print("base",base)
for name,kw in sens: print(name, run(**kw)[:2])
