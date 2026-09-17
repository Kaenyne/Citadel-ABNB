"""C03 fy26-revenue-guide-language: reproduces the arithmetic, the three estimates and the final vector.
Run: python docs/pitch-forecasts/questions/fy26-revenue-guide-language/datasets/decomposition.py
Dependency-free (standard library only)."""
import csv, os, math
here = os.path.dirname(os.path.abspath(__file__))
opts = ['a','b','c','d','e']
Phi = lambda z: 0.5*(1+math.erf(z/math.sqrt(2)))

# ---- Arithmetic: FY26 growth implied by 9M actual + 4Q26 revenue guide midpoint
FY25 = 12241.0; H1 = 6286.0
q3_mean, q3_sd = 4795.0, 40.0      # team 4,804 / cushion-adjusted 4,820 / LSEG 4,744; 19/19 beats of the guide mid
q4_mean, q4_sd = 3085.0, 80.0      # bridge v3 3,178 / (1 + Q4 cushion): 3,059 (5-yr mean 3.85%), 3,084 (last-3 3.04%), 3,120 (trailing-8 1.86%)
fy_mean = H1 + q3_mean + q4_mean; fy_sd = math.hypot(q3_sd, q4_sd)
g_mean = (fy_mean/FY25 - 1)*100; g_sd = fy_sd/FY25*100
P = lambda lo, hi: Phi((hi-g_mean)/g_sd) - Phi((lo-g_mean)/g_sd)
print('FY26 implied by 9M + Q4 guide mid: %.0f -> %.2f%%  sd %.2fpp' % (fy_mean, g_mean, g_sd))
p_ge165 = 1-Phi((16.5-g_mean)/g_sd); p_155_165 = P(15.5,16.5); p_145_155 = P(14.5,15.5); p_lt145 = Phi((14.5-g_mean)/g_sd)
p_ge16 = 1-Phi((16.0-g_mean)/g_sd); p_15_16 = P(15.0,16.0); p_lt15 = Phi((15.0-g_mean)/g_sd)
print('nearest-integer rounding: >=16.5 %.2f | 15.5-16.5 %.2f | 14.5-15.5 %.2f | <14.5 %.2f' % (p_ge165,p_155_165,p_145_155,p_lt145))
print('round-down convention:    >=16 %.2f | 15-16 %.2f | <15 %.2f' % (p_ge16,p_15_16,p_lt15))
# numeric-sentence conditional = average of the two rounding conventions
num = {'a': 0.5*(p_ge165+p_155_165) + 0.5*p_ge16, 'c': 0.5*p_145_155 + 0.5*p_15_16, 'd': 0.5*p_lt145 + 0.5*p_lt15}
num['b'] = 0.02; s = sum(num.values()); num = {k: v/s for k,v in num.items()}; num['e']=0.0
print('given numeric sentence:', {k: round(v,3) for k,v in num.items()})

# ---- Decomposition: P(format) x P(option | format)
p_numeric, p_descr, p_none = 0.55, 0.35, 0.10
descr = dict(a=.30, b=.45, c=.15, d=.10, e=0.0)
dec = {o: p_numeric*num.get(o,0) + p_descr*descr[o] for o in opts}; dec['e'] = p_none
dec = {k: v/sum(dec.values()) for k,v in dec.items()}

# ---- Base rate: FY-guide action at Q3 prints (margin FY23/24/25: 3/3 floor -> 'approximately' point above the floor; FY26 revenue guide 2/2 raised at updates)
base = dict(a=.45, b=.12, c=.30, d=.03, e=.10)
# ---- Anchor: LSEG FY26 consensus 14,190 (+15.9%) and Street-implied guide 14,105 (+15.2%, kappa 0.6%)
anchor = dict(a=.30, b=.18, c=.35, d=.07, e=.10)
final = dict(a=.37, b=.18, c=.28, d=.08, e=.09)
for name,v in [('base',base),('decomposition',dec),('anchor',anchor),('final',final)]:
    assert abs(sum(v.values())-1) < 1e-6, (name, sum(v.values()))
out = os.path.join(here,'decomposition_output.csv')
with open(out,'w',newline='') as f:
    w = csv.writer(f); w.writerow(['estimate']+opts)
    for name,v in [('base_rate',base),('decomposition',dec),('anchor',anchor),('final',final)]:
        w.writerow([name]+[round(v[o],3) for o in opts])
for name,v in [('base_rate',base),('decomposition',dec),('anchor',anchor),('final',final)]:
    print(name, {o: round(v[o],3) for o in opts})
print('written', out)
