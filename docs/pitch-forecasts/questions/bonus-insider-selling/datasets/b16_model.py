"""B16: P(Form 4 open-market sales 17 Sep 2026 - 31 Jan 2027 >= $150M) OR P(a new CEO 10b5-1 plan is disclosed in the window).
Inputs: form4_sales_codeS.csv (EDGAR pull, pull_form4.py), sales_by_owner_and_plan.csv, the 10-Q Item 5 tables (../sources/tenq_item5_10b51_tables.txt).
Monte Carlo over the five selling sources; seed 20260917; numpy/pandas only. Writes b16_summary.json, b16_window_history.csv."""
import numpy as np, pandas as pd, json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
rng=np.random.default_rng(20260917); N=200_000; PX=167.51   # 16 Sep close (brief)
s=pd.read_csv('form4_sales_codeS.csv',parse_dates=['txn_date']); s['owner']=s.owner.str.strip()
# --- history: every 137-day window (17 Sep -> 31 Jan) of code-S value, daily-start windows since 2023-01-01
daily=s.groupby('txn_date').value.sum().reindex(pd.date_range('2022-09-01','2026-09-16'),fill_value=0)
roll=(daily.rolling(137).sum().shift(-136).dropna()/1e6); roll=roll[roll.index>='2023-01-01']
exg=s[~s.owner.str.contains('Gebbia')].groupby('txn_date').value.sum().reindex(daily.index,fill_value=0)
rollx=(exg.rolling(137).sum().shift(-136).dropna()/1e6); rollx=rollx[rollx.index>='2023-01-01']
hist={'windows_n':int(len(roll)),'p_ge150_all':float((roll>=150).mean()),'p_ge150_exGebbia':float((rollx>=150).mean()),'median_all':float(roll.median()),'median_exGebbia':float(rollx.median())}
seasonal={f'{y}-09-17..{y+1}-01-31':dict(all=float(daily[f'{y}-09-17':f'{y+1}-01-31'].sum()/1e6),ex_gebbia=float(exg[f'{y}-09-17':f'{y+1}-01-31'].sum()/1e6)) for y in (2023,2024,2025)}
pd.DataFrame({'window_start':roll.index,'value_musd':roll.values,'value_ex_gebbia_musd':rollx.values}).to_csv('b16_window_history.csv',index=False)
# --- forward components (shares), all under 10b5-1 plans disclosed in 10-Qs or Form 4 footnotes
# A. Blecharczyk, plan 28 Aug 2025 (max 2,224,176; sold 1,627,685 to 14 Sep; expires 20 Nov 2026): remaining 596,491. Execution: Aug-26 pace 1.0m/month; Sep 13.6k so far.
#    P(remaining fully sold by 20 Nov) ~0.55; else partial. Model: fraction sold ~ mixture: 0.55 -> 1.0; 0.45 -> Beta(1.5,2) (mean 0.43)
remA=596_491
fA=np.where(rng.random(N)<0.55,1.0,rng.beta(1.5,2,N))
# B. Chesky, plan 26 Feb 2026 (max 1,785,000; sold 1,260,000 to 7 Aug; expires 25 Nov 2026): remaining 525,000. His Feb-2025 plan sold 24.5k of 649k, Aug-2025 60k of 690k,
#    Feb-2024 plans ~1.06m of 1.146m, Aug-2024 993k of 1.135m, May-2023 1.65m of 2.06m: execution is bimodal. P(rest sold) 0.45; else Beta(1,3) (mean 0.25)
remB=525_000
fB=np.where(rng.random(N)<0.45,1.0,rng.beta(1,3,N))
# C. New Chesky plan adopted Jul-Sep 2026 (cadence: May-23, Feb-24, Aug-24, Feb-25, Aug-25, Feb-26 -> 5 of 6 half-year slots; Laplace 0.75; haircut for the 525k still open -> 0.70)
#    Cooling-off 90 days -> first sales late Nov/Dec; Dec-Jan sales under his Aug-2024 plan $21M, Aug-2025 plan $8M
pC=0.70; newC=rng.random(N)<pC
valC=np.where(newC,rng.lognormal(np.log(15),0.9,N),0.0)   # $M, median 15, p90 ~48
# D. New Gebbia plan adopted Jul-Sep 2026 (cadence Feb-24, Aug-24, Feb-25, Aug-25, Feb-26: 5 of 5; Laplace 0.86; his Feb-26 plan is exhausted, so a new plan is the only route -> 0.75)
#    Dec-Jan sales under his Aug-2024 plan $145M, Aug-2025 plan $38M
pD=0.75; newD=rng.random(N)<pD
valD=np.where(newD,rng.lognormal(np.log(60),0.8,N),0.0)   # $M, median 60, p10 ~21, p90 ~170
# E. Everyone else (Mertz new plan after 5 Aug 2026 expiry, Balogh, Bernstein, directors): Sep-Jan history $5-25M
valE=rng.lognormal(np.log(10),0.6,N)
# F. Non-plan / new-plan by a 10% holder or a Chesky non-plan sale: tail
valF=np.where(rng.random(N)<0.05,rng.lognormal(np.log(80),0.7,N),0.0)
px=PX*np.exp(rng.normal(0,0.12,N))   # price over the window (sd 12%: options 12M sd ~28%, ~4.5 months)
total=(remA*fA+remB*fB)*px/1e6+valC+valD+valE+valF
legA=(total>=150).mean()
legB=pC   # a plan adopted in Q3 is disclosed in the 3Q26 10-Q (~5-6 Nov), inside the window; a Q4 adoption would surface only in the 10-K (~12 Feb 2027) or a footnote after cooling-off (>= late Feb) -> outside
yes=((total>=150)|newC).mean()
legA_given_noC=(total[~newC]>=150).mean()
out=dict(history=hist,seasonal_windows=seasonal,p_legA_sales_ge150=float(legA),p_legB_new_ceo_plan=float(legB),p_legA_given_no_new_ceo_plan=float(legA_given_noC),
         p_yes=float(yes),total_musd_percentiles={str(q):float(np.percentile(total,q)) for q in (5,10,25,50,75,90,95)},
         remaining_capacity_shares=dict(blecharczyk=remA,chesky=remB),price_used=PX)
# sensitivities
sens={}
for name,kw in [('pC 0.5',dict(pC=0.5)),('pC 0.85',dict(pC=0.85)),('pD 0.5',dict(pD=0.5)),('pD 0.9',dict(pD=0.9)),('Blecharczyk full execution',dict(fA=1.0)),('Blecharczyk sells nothing more',dict(fA=0.0)),('Chesky rest fully sold',dict(fB=1.0)),('Chesky sells nothing more',dict(fB=0.0)),('Gebbia new-plan median 30',dict(dmed=30)),('Gebbia new-plan median 120',dict(dmed=120))]:
    pc=kw.get('pC',pC); pdd=kw.get('pD',pD); fa=kw.get('fA',fA); fb=kw.get('fB',fB); dmed=kw.get('dmed',60)
    nC=rng.random(N)<pc; nD=rng.random(N)<pdd
    t=(remA*fa+remB*fb)*px/1e6+np.where(nC,rng.lognormal(np.log(15),0.9,N),0)+np.where(nD,rng.lognormal(np.log(dmed),0.8,N),0)+valE+valF
    sens[name]=dict(p_legA=float((t>=150).mean()),p_yes=float(((t>=150)|nC).mean()))
out['sensitivity']=sens
json.dump(out,open('b16_summary.json','w'),indent=1); print(json.dumps(out,indent=1))
