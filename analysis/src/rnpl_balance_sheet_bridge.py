"""RNPL: two-line balance-sheet triangulation and the 3Q26/4Q26 nights bridge.
Reads only data/processed/overnight/02_kpi_panel_quarterly.csv and overnight2/D outputs. Writes nothing to the repo."""
import csv, statistics as st
R={r['quarter']:r for r in csv.DictReader(open('data/processed/overnight/02_kpi_panel_quarterly.csv',encoding='utf-8-sig'))}
f=lambda q,k: float(R[q][k])
Q=['1Q23','2Q23','3Q23','4Q23','1Q24','2Q24','3Q24','4Q24','1Q25','2Q25','3Q25','4Q25','1Q26','2Q26']
nxt={Q[i]:Q[i+1] for i in range(len(Q)-1)}
REV_3Q26=4800.0; REV_4Q26=3166.0
def nrev(q): return f(nxt[q],'revenue_musd') if q in nxt else REV_3Q26

# ---- 1. y/y growth gaps: the fee-migration signature ----
print("## 1. Growth of the two prepaid-customer lines versus GBV (y/y, %)")
print("quarter | GBV | unearned fees | gap UF-GBV | funds payable | gap FH-GBV | UF gap minus FH gap")
for q in ['1Q25','2Q25','3Q25','4Q25','1Q26','2Q26']:
    g=f(q,'gbv_yoy_pct'); u=f(q,'unearned_fees_yoy_pct'); h=f(q,'funds_held_yoy_pct')
    print(f"{q} | {g:5.1f} | {u:5.1f} | {u-g:6.1f} | {h:5.1f} | {h-g:6.1f} | {(u-g)-(h-g):6.1f}")

# ---- 2. ratios to next-quarter revenue and pre-RNPL seasonal norms ----
uf_r={q:f(q,'unearned_fees_musd')/nrev(q) for q in Q}
fh_r={q:f(q,'funds_held_for_clients_musd')/nrev(q) for q in Q}
norm={}
for s in '1234':
    base=[q for q in Q if q[0]==s and (int(q[-2:])<=24 or (q[-2:]=='25' and s in '12'))]
    norm[s]=(st.mean(uf_r[q] for q in base), st.mean(fh_r[q] for q in base), base)
print("\n## 2. Pre-RNPL seasonal norms (stock / next-quarter revenue)")
for s in '1234': print(f"Q{s}: UF {norm[s][0]:.3f}  FH {norm[s][1]:.3f}  from {norm[s][2]}")

# ---- 3. joint solve: UF ratio=(1-u)(1-m)*B ; FH ratio=(1-u)(1+k m)*B ----
G_SPLIT=0.124      # guest fee / GBV under split fee (14.2% of subtotal)
K=G_SPLIT/(1-G_SPLIT)   # migration inflow to funds payable per $ of migrated backlog
print("\n## 3. Joint solve for unpaid RNPL share u and single-fee share m of the backlog")
print(f"model: UF_ratio=(1-u)(1-m)B ; FH_ratio=(1-u)(1+{K:.3f}m)B ; B = backlog scale vs norm (1.00 unless stated)")
print("quarter | UF ratio | FH ratio | B | m (single-fee share) | u (unpaid RNPL share) | unpaid GBV $B | unpaid nights M @1.33xADR")
rows=[]
for q in ['3Q25','4Q25','1Q26','2Q26']:
    s=q[0]; ufr=uf_r[q]/norm[s][0]; fhr=fh_r[q]/norm[s][1]
    for B in (1.00,1.05,1.10):
        a=ufr/B; b=fhr/B            # a=(1-u)(1-m), b=(1-u)(1+Km)
        m=(b-a)/(a*K+b)             # from b/a=(1+Km)/(1-m)
        u=1-a/(1-m)
        Bexp=norm[s][0]*nrev(q)/G_SPLIT*B   # paid-equivalent backlog GBV, $M
        unpaid=u*Bexp
        nights=unpaid/(f(q,'adr_usd')*1.33)
        rows.append((q,B,m,u,unpaid,nights))
        print(f"{q} | {ufr:.3f} | {fhr:.3f} | {B:.2f} | {100*m:5.1f}% | {100*u:5.1f}% | {unpaid/1000:5.1f} | {nights:5.1f}")
print("Reference flow: RNPL GBV booked per quarter at the disclosed share: 1Q26 ~$5.8B (20%), 2Q26 ~$5.7B (21%).")

# ---- 4. what 3Q26 balance-sheet lines look like under deferral only (no cancellation effect) ----
print("\n## 4. 3Q26 quarter-end lines under deferral-only scenarios (score sheet for 5 Nov)")
uf25=f('3Q25','unearned_fees_musd'); fh25=f('3Q25','funds_held_for_clients_musd')
UFn=norm['3'][0]*REV_4Q26; FHn=norm['3'][1]*REV_4Q26
print(f"pre-RNPL, pre-migration expectation: UF ${UFn:,.0f}M ({100*(UFn/uf25-1):+.1f}% y/y), FH ${FHn:,.0f}M ({100*(FHn/fh25-1):+.1f}% y/y)")
print("u (unpaid share) | m (single-fee share) | UF $M | UF y/y | FH $M | FH y/y")
for u,m,label in [(0.07,0.09,'2Q26 solved values carried'),(0.10,0.12,'RNPL share 22-23%, migration ~60% listings'),(0.12,0.18,'July expansion + migration ~80%'),(0.07,0.00,'no migration effect at all'),(0.15,0.00,'UF hole all RNPL, no migration')]:
    uf=UFn*(1-u)*(1-m); fh=FHn*(1-u)*(1+K*m)
    print(f"{100*u:4.0f}% | {100*m:4.0f}% | {uf:5.0f} | {100*(uf/uf25-1):+5.1f}% | {fh:6.0f} | {100*(fh/fh25-1):+5.1f}%   <- {label}")

# ---- 5. marginal ADR ratio of the bundle, from disclosure ----
print("\n## 5. Marginal ADR of bundle-driven bookings, pinned by 4Q25 and 1Q26 disclosures")
for lab,n,g in [('4Q25 >200bp nights / ~300bp GBV',2.0,3.0),('1Q26 ~3pts nights / ~4pts GBV',3.0,4.0)]:
    print(f"{lab}: marginal ADR / average ADR = {g/n:.2f}x")
s=0.21; r=1.33; p=s/(r*(1-s)+s); print(f"RNPL nights share at 21% GBV share and r=1.33: {100*p:.1f}%  (r=1.00: 21.0%, r=1.25: {100*0.21/(1.25*0.79+0.21):.1f}%)")

# ---- 6. pull-forward reversal in 3Q26 y/y ----
print("\n## 6. One-time pull-forward in 3Q25 (US launch) that reverses in the 3Q26 comp")
n3q25=f('3Q25','nights_m')
for rnpl_share_3q25 in (0.033,0.05):        # nights share, central 4% GBV / 1.2 ADR -> 3.3%
    for uplift in (0.07,0.15):               # RNPL lead-time uplift on 2.2 months
        dl=2.2*uplift                        # extra months of lead
        pf=rnpl_share_3q25*(dl/3.0)          # share of quarterly nights pulled forward
        print(f"3Q25 RNPL nights share {100*rnpl_share_3q25:.1f}%, lead uplift {100*uplift:.0f}%: pull-forward {100*pf:.2f}% of 3Q25 nights = {pf*n3q25:.2f}M -> 3Q26 y/y {-100*pf:+.2f} pts")

# ---- 7. Krish's D1 central cell, read from the grid ----
D=list(csv.DictReader(open('data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv',encoding='utf-8-sig')))
print("\n## 7. D1 central cell (share_central, adr_plus25, lead_2.2, uplift_7, rebook 0.25): y/y growth points")
for d in D:
    if d['share_path']=='share_central' and d['adr_ratio']=='adr_plus25' and d['lead_time']=='lead_2.2' and d['lead_uplift']=='uplift_7' and d['rebook_offset']=='0.25':
        print(f"  {d['delta_scenario']:>12} (+{d['delta_pp_applied']}pp): 3Q26 {float(d['3Q26_growth_delta_pts']):+.2f} -> {d['3Q26_growth_pct']}% | 4Q26 {float(d['4Q26_growth_delta_pts']):+.2f} -> {d['4Q26_growth_pct']}%")

# ---- 8. the bridge ----
print("\n## 8. 3Q26 / 4Q26 nights bridge (growth points)")
base3,base4=9.89,8.90
tail3=(-0.31,-0.62,-0.93); tail4=(-0.28,-0.57,-0.85)   # D1 central cell at +2/+4/+6pp
pf3=(-0.1,-0.2,-0.3)
july=(0.3,0.2,0.1)
exna4=(-0.70,-0.79,-0.88)   # Krish D point 5
print("scenario | 3Q26 | nights M | 4Q26 | nights M")
for i,lab in enumerate(['mild (+2pp tail, small pull-fwd, July +0.3)','central (+4pp tail, July +0.2)','heavy (+6pp mgmt-implied, July +0.1)']):
    g3=base3+tail3[i]+pf3[i]+july[i]; g4=base4+tail4[i]+exna4[i]+july[i]*0.5
    print(f"{lab} | {g3:.2f}% | {133.6*(1+g3/100):.1f} | {g4:.2f}% | {121.9*(1+g4/100):.1f}")
print("reviews-index read (stay-date, cannot see the booking-date tail): 9.5 (8.5-11.0); minus central tail 0.62 -> 8.9")
