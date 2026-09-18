"""F02: y/y growth implied by the 1Q27 revenue guide midpoint (Feb 2027 letter), base 1Q26 $2,678M.
Kernel: print_1Q27 = lambda_Q1 x (1+eps) x [2/3 GBV_4Q26 + 1/3 GBV_3Q26]; guide = print / (1 + cushion), on a $5M grid.
numpy only. Seed 20260917. Run: python f02_model.py  (writes f02_summary.csv, f02_percentiles.csv, f02_sensitivity.csv)"""
import numpy as np, csv, os
HERE=os.path.dirname(os.path.abspath(__file__))
N=400_000
BASE_1Q26=2678.0
def run(seed=20260917, n3_mu=9.5, n3_sd=1.6, a3_mu=3.3, a3_sd=1.3,
        n4_mu=8.1, n4_sd=1.7, n4_short_w=0.12, n4_short_mu=5.5, n4_short_sd=1.5, rho34=0.5,
        a4_mu=4.0, a4_sd=1.5, lam=12.612, eps_mu=-0.5, eps_sd=2.5, c_mu=2.5, c_sd=1.2, p_noguide=0.01):
    rng=np.random.default_rng(seed)
    z3=rng.standard_normal(N); n3=n3_mu+n3_sd*z3
    a3=a3_mu+a3_sd*rng.standard_normal(N)
    gbv3=133.6*(1+n3/100)*171.29*(1+a3/100)            # $M (133.6m nights x $171.29 = $22,884M base)
    z4=rho34*z3+np.sqrt(1-rho34**2)*rng.standard_normal(N)
    n4=n4_mu+n4_sd*z4
    short=rng.random(N)<n4_short_w
    n4=np.where(short, n4_short_mu+n4_short_sd*rng.standard_normal(N), n4)
    a4=a4_mu+a4_sd*rng.standard_normal(N)
    gbv4=20400.0*(1+n4/100)*(1+a4/100)
    L=(2/3)*gbv4+(1/3)*gbv3
    eps=eps_mu+eps_sd*rng.standard_normal(N)
    print_=lam/100*(1+eps/100)*L
    c=c_mu+c_sd*rng.standard_normal(N)
    guide=np.round(print_/(1+c/100)/5)*5
    g=(guide/BASE_1Q26-1)*100
    return dict(g=g, print_=print_, guide=guide, gbv3=gbv3, gbv4=gbv4, n4=n4, L=L)
def summ(g):
    pct=np.percentile(g,[5,10,25,50,75,90,95])
    return dict(mean=g.mean(), sd=g.std(), p5=pct[0],p10=pct[1],p25=pct[2],p50=pct[3],p75=pct[4],p90=pct[5],p95=pct[6],
                p_lt10=(g<10).mean(), p_lt9_4=(g<9.4).mean(), p_ge12=(g>=12).mean(), p_lt8=(g<8).mean(), p_ge14=(g>=14).mean(),
                p_lt5=(g<5).mean(), p_gt18=(g>18).mean())
if __name__=='__main__':
    r=run(); s=summ(r['g'])
    print('base: guide median $%.0fM, print median $%.0fM, GBV3 %.0f, GBV4 %.0f, L %.0f, n4 mean %.2f'%(np.median(r['guide']),np.median(r['print_']),np.median(r['gbv3']),np.median(r['gbv4']),np.median(r['L']),r['n4'].mean()))
    for k,v in s.items(): print(f'{k}: {v:.3f}')
    with open(os.path.join(HERE,'f02_summary.csv'),'w',newline='') as f:
        w=csv.writer(f); w.writerow(['stat','value']); [w.writerow([k,round(v,4)]) for k,v in s.items()]
        w.writerow(['guide_median_musd',round(float(np.median(r['guide'])),1)]); w.writerow(['print_median_musd',round(float(np.median(r['print_'])),1)])
    with open(os.path.join(HERE,'f02_percentiles.csv'),'w',newline='') as f:
        w=csv.writer(f); w.writerow(['percentile','growth_pct','guide_musd'])
        for p in [5,10,25,50,75,90,95]: w.writerow([p, round(float(np.percentile(r['g'],p)),2), round(float(np.percentile(r['guide'],p)),0)])
    hist,edges=np.histogram(r['g'],bins=np.arange(-2,24,1.0))
    with open(os.path.join(HERE,'f02_hist.csv'),'w',newline='') as f:
        w=csv.writer(f); w.writerow(['bin_lo','bin_hi','share']); [w.writerow([edges[i],edges[i+1],round(hist[i]/N,4)]) for i in range(len(hist))]
    sens=[('base',{}),
          ('n4 centred 7.6 (RNPL module)',dict(n4_mu=7.6)),('n4 centred 9.9 (Street bar), no short tail',dict(n4_mu=9.9,n4_short_w=0)),
          ('n4 short case 5.0 certain',dict(n4_mu=5.0,n4_sd=1.2,n4_short_w=0)),
          ('GBV_3Q26 at Kalshi/MODL (nights 11.0)',dict(n3_mu=11.0)),('GBV_3Q26 nights 8.5',dict(n3_mu=8.5)),
          ('lambda_Q1 12.66 (ewm) unbiased eps',dict(lam=12.66,eps_mu=0.0)),('lambda_Q1 12.72 (2023-25 mean), eps 0',dict(lam=12.72,eps_mu=0.0)),
          ('eps -1.4 (top of RNPL leakage)',dict(eps_mu=-1.4)),('eps sd 1.5 (tight)',dict(eps_sd=1.5)),('eps sd 3.5 (1Q25-type miss)',dict(eps_sd=3.5)),
          ('cushion 1.86 (trailing-8 all-quarter)',dict(c_mu=1.86)),('cushion 2.87 (five Q1 guides mean)',dict(c_mu=2.87)),('cushion 4.0 (1Q22/1Q24-type)',dict(c_mu=4.0)),
          ('ADR_4Q26 +2.5',dict(a4_mu=2.5)),('ADR_4Q26 +5.5',dict(a4_mu=5.5)),
          ('joint bull: n4 9.9, a4 5.0, eps +0.5, cushion 1.86',dict(n4_mu=9.9,n4_short_w=0,a4_mu=5.0,eps_mu=0.5,c_mu=1.86)),
          ('joint bear: n4 6.5, a4 2.5, eps -1.4, cushion 3.0',dict(n4_mu=6.5,a4_mu=2.5,eps_mu=-1.4,c_mu=3.0))]
    with open(os.path.join(HERE,'f02_sensitivity.csv'),'w',newline='') as f:
        w=csv.writer(f); w.writerow(['case','p50','p5','p95','p_lt10','p_lt9_4','p_ge12','guide_median_musd'])
        for name,kw in sens:
            rr=run(**kw); ss=summ(rr['g'])
            w.writerow([name,round(ss['p50'],2),round(ss['p5'],2),round(ss['p95'],2),round(ss['p_lt10'],3),round(ss['p_lt9_4'],3),round(ss['p_ge12'],3),round(float(np.median(rr['guide'])),0)])
            print(f"{name:55s} p50 {ss['p50']:6.2f}  p5 {ss['p5']:6.2f} p95 {ss['p95']:6.2f}  P<10 {ss['p_lt10']:.3f} P<9.4 {ss['p_lt9_4']:.3f} P>=12 {ss['p_ge12']:.3f}")
