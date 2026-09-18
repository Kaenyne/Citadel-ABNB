"""C02 q4-nights-bucket: reproduces the three estimates and the final vector.
Run: python docs/pitch-forecasts/questions/q4-nights-bucket/datasets/decomposition.py
Dependency-free (standard library only)."""
import csv, json, os, math
here = os.path.dirname(os.path.abspath(__file__))
opts = ['a','b','c','d','e']

# ---- 1. Base rate: next-quarter nights descriptor vs the just-printed rate (ledger, 2Q22-2Q26)
rows = list(csv.DictReader(open(os.path.join(here,'nights_descriptor_vs_printed_and_comp.csv'))))
cls = []
for r in rows:
    if r['outcome']=='pending': continue
    if r['cls']=='bucket':
        d = float(r['mid_minus_printed'])
        cls.append('down' if d < -0.5 else ('stable' if d <= 0.5 else 'up'))
    else:
        cls.append(r['cls'])
n = len(cls); down = cls.count('down')/n; stable = cls.count('stable')/n; up = cls.count('up')/n
# map to options given the team band on the 3Q26 print: P(Q3 >= 10.0) = 0.38
p_q3_ge10 = 0.38
base = {'a': up + stable*p_q3_ge10, 'b': stable*(1-p_q3_ge10), 'c': down*2/3, 'd': down/3, 'e': 0.0}
base['e'] = 0.02; s = sum(base.values()); base = {k: v/s for k,v in base.items()}

# ---- 2. Decomposition: scenario tree on the 3Q26 print (team nowcast band) x descriptor given the print
pQ3 = {'ge10': 0.38, '9to10': 0.42, 'lt9': 0.20}
cond = {'ge10': dict(a=.42,b=.20,c=.28,d=.08,e=.02),
        '9to10': dict(a=.10,b=.22,c=.50,d=.15,e=.03),
        'lt9':  dict(a=.05,b=.10,c=.40,d=.40,e=.05)}
dec = {o: sum(pQ3[s]*cond[s][o] for s in pQ3) for o in opts}

# ---- 3. Anchor: Street 4Q26 nights bar (Bloomberg MODL 134.0m = +9.9%, 12 Sep) less the bucket cushion (1-3 pts)
anchor = dict(a=.12,b=.25,c=.45,d=.15,e=.03)

# ---- 4. Final (stated in the log); check sums
final = dict(a=.21,b=.19,c=.39,d=.17,e=.04)
for name,v in [('base',base),('decomposition',dec),('anchor',anchor),('final',final)]:
    assert abs(sum(v.values())-1) < 1e-6, name
out = os.path.join(here,'decomposition_output.csv')
with open(out,'w',newline='') as f:
    w = csv.writer(f); w.writerow(['estimate']+opts)
    for name,v in [('base_rate',base),('decomposition',dec),('anchor',anchor),('final',final)]:
        w.writerow([name]+[round(v[o],3) for o in opts])
print('descriptor classes n=%d down=%.3f stable=%.3f up=%.3f' % (n,down,stable,up))
for name,v in [('base_rate',base),('decomposition',dec),('anchor',anchor),('final',final)]:
    print(name, {o: round(v[o],3) for o in opts})
print('written', out)

# ---- 5. Sensitivities (research-log.md section 7)
def tree(p, c=cond):
    return {o: round(sum(p[s]*c[s][o] for s in p),3) for o in opts}
print('S1 P(Q3>=10)=0.60 (Street/Kalshi view):', tree({'ge10':.60,'9to10':.28,'lt9':.12}))
print('S1 P(Q3>=10)=0.25 (team-low view):     ', tree({'ge10':.25,'9to10':.45,'lt9':.30}))
g = dict(final); tot = g['a']+g['b']+g['c']
for k in 'abc': g[k] -= 0.20*final[k]/tot
g['d'] += 0.12; g['b'] += 0.06; g['a'] += 0.02
print('S2 directional-only 0.25 -> 0.45:      ', {k: round(v,3) for k,v in g.items()})
c3 = dict(cond); c3['9to10'] = dict(a=.12,b=.32,c=.42,d=.11,e=.03); c3['lt9'] = dict(a=.05,b=.15,c=.42,d=.33,e=.05)
print('S3 case A 8.9 as the point:            ', tree(pQ3, c3))
c4 = dict(cond); c4['ge10'] = dict(a=.60,b=.20,c=.15,d=.03,e=.02)
print('S4 comp ignored on a strong October:   ', tree(pQ3, c4))
