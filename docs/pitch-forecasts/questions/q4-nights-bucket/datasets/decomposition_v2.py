"""C02 q4-nights-bucket, revision 2 (audit response to A02): reproduces the three estimates and the final vector.
Run: py -3.13 docs/pitch-forecasts/questions/q4-nights-bucket/datasets/decomposition_v2.py
Dependency-free (standard library only). Deterministic: no random draws are used, so the seed below only
guards the optional Monte-Carlo check of the closed-form tree.
Changes from decomposition.py: (1) base rate re-counted on the corrected 17-row dataset (4Q24 = down, pending
2Q26 descriptor included; A02-02) and mapped onto the question's own option labels instead of a 2:1 (c):(d)
split of 'down'; (2) Q3-print branch masses taken from R01/R02's implied distribution N(9.67, 1.70) instead of
hard-coded 0.38/0.42/0.20 (A02-03); (3) each branch's conditional is built as format x content so the
directional-'moderate' -> (d) path is explicit and varied (A02-06, A02-09); (4) the anchor is a stated
level-to-language mapping of the Street bar, labelled a dependent judgmental construction (A02-06, A02-08)."""
import csv, os, math, random
from collections import Counter
here = os.path.dirname(os.path.abspath(__file__))
opts = ['a', 'b', 'c', 'd', 'e']
Phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
random.seed(20260917)

def norm(v):
    s = sum(v.values()); return {k: v[k] / s for k in opts}

def fmt(v):
    return {o: round(v.get(o, 0.0), 3) for o in opts}

# ---- 1. Base rate: the 17 observable next-quarter nights descriptors (2Q22-2Q26 prints) mapped onto the
#         question's option labels (directional-down -> d; stable/up -> a if the printed rate >= 10 else b;
#         bucket -> its level). Windows per CLAUDE.md rule 2 (W1 prints 1Q23+, W2 prints 1Q24+).
rows = list(csv.DictReader(open(os.path.join(here, 'nights_descriptor_vs_printed_and_comp_v2.csv'))))
def counts(sub):
    c = Counter(r['question_option'] for r in sub); n = len(sub)
    return n, {o: c[o] / n for o in opts}
key = lambda q: (2000 + int(q[-2:])) * 4 + int(q[0])
windows = {'all_17': rows, 'W1_1Q23plus': [r for r in rows if key(r['print_quarter']) >= key('1Q23')],
           'W2_1Q24plus': [r for r in rows if key(r['print_quarter']) >= key('1Q24')],
           'bucket_era_3Q25plus': [r for r in rows if key(r['print_quarter']) >= key('3Q25')],
           'november_prints': [r for r in rows if r['print_quarter'].startswith('3Q')]}
print('== base-rate counts on the question labels')
for name, sub in windows.items():
    n, f = counts(sub); print('  %-20s n=%2d' % (name, n), {o: round(f[o], 2) for o in opts})
cls = Counter(r['cls'] for r in rows)
print('  class counts (all 17): down %d stable %d up %d' % (cls['down'], cls['stable'], cls['up']))
# Regime conditioning: the bucket era (3 of the last 4 guides are buckets) shifts mass from the directional
# 'moderate' sentence (d) to a level bucket. P(directional) = Laplace on the bucket era, (1+1)/(4+2) = 0.33,
# shaded to 0.30 because the one directional guide carried a quantified exogenous headwind (1Q26 letter).
p_dir = 0.30
p_down_given_dir = 8 / 14          # directional-era down share (3Q22, 1Q23, 3Q23, 4Q23, 2Q24, 4Q24, 1Q25, 1Q26)
p_q3_ge10 = 0.42                   # R01 revision 1 (blend of alt data, outside view, market)
p_mid_single_given_bucket = 1 / 3  # 3Q25 mid-single of three buckets (harder comp by 3.5pt then; 1.0pt now)
p_high_single_given_bucket = 0.45
p_ge_around10_given_bucket = 1 - p_mid_single_given_bucket - p_high_single_given_bucket
base = {'a': p_dir * (1 - p_down_given_dir) * p_q3_ge10 + (1 - p_dir) * p_ge_around10_given_bucket * 0.5,
        'b': p_dir * (1 - p_down_given_dir) * (1 - p_q3_ge10) + (1 - p_dir) * p_ge_around10_given_bucket * 0.5,
        'c': (1 - p_dir) * p_high_single_given_bucket,
        'd': p_dir * p_down_given_dir + (1 - p_dir) * p_mid_single_given_bucket,
        'e': 0.03}
base = norm(base)
print('== base rate (regime-conditioned; unconditional all-17 mapping is the first row above)')
print('  ', fmt(base))

# ---- 2. Decomposition: Q3-print branches from R01/R02's implied distribution x (format x content | branch)
mu, sd = 9.67, 1.70   # R01 revision 1 section 6: N(9.67, 1.70) calibrated to P(>=10.0) = 0.42; R02 P(>=10.6) = 0.32 (normal 0.29)
pQ3 = {'ge10': 1 - Phi((10 - mu) / sd), '9to10': Phi((10 - mu) / sd) - Phi((9 - mu) / sd), 'lt9': Phi((9 - mu) / sd)}
print('== Q3 branch masses from N(%.2f, %.2f):' % (mu, sd), {k: round(v, 3) for k, v in pQ3.items()},
      ' P(>=10.6) %.3f' % (1 - Phi((10.6 - mu) / sd)))
# format | branch: bucket / directional / none. Directional is likelier when the print is noisy (3Q23 precedent).
fmt_by_branch = {'ge10': dict(bucket=.72, directional=.25, none=.03),
                 '9to10': dict(bucket=.69, directional=.28, none=.03),
                 'lt9': dict(bucket=.62, directional=.35, none=.03)}
# bucket content | branch. E[Q3 | >=10] = 11.2, E[Q3 | 9-10] = 9.5, E[Q3 | <9] = 8.0 under the normal; the 4Q26
# comp is 1.0pt harder than Q3's; the bucket era set the bucket midpoint -3.8 / -1.8 / +0.7 vs the printed rate.
bucket_content = {'ge10': dict(a=.45, b=.20, c=.30, d=.05),
                  '9to10': dict(a=.08, b=.22, c=.57, d=.13),
                  'lt9': dict(a=.02, b=.07, c=.50, d=.41)}
# directional content | branch: P(moderate/decelerate) -> (d); the remainder is stable/higher -> (a) if Q3 >= 10 else (b)
p_moderate = {'ge10': .55, '9to10': .60, 'lt9': .75}
def cond(branch, f=fmt_by_branch, bc=bucket_content, pm=p_moderate):
    fb, c, m = f[branch], bc[branch], pm[branch]
    v = {o: fb['bucket'] * c[o] for o in 'abcd'}
    v['d'] += fb['directional'] * m
    v['a' if branch == 'ge10' else 'b'] += fb['directional'] * (1 - m)
    v['e'] = fb['none']
    return v
def tree(p=pQ3, **kw):
    c = {b: cond(b, **kw) for b in p}
    return {o: sum(p[b] * c[b][o] for b in p) for o in opts}, c
dec, cond_tab = tree()
print('== conditionals (format x content) by branch')
for b in pQ3: print('  %-6s' % b, fmt(cond_tab[b]))
print('== decomposition', fmt(dec))
# sub-categories carried for X01 (A02-09)
d_directional = sum(pQ3[b] * fmt_by_branch[b]['directional'] * p_moderate[b] for b in pQ3)
b_similar = sum(pQ3[b] * fmt_by_branch[b]['directional'] * (1 - p_moderate[b]) for b in pQ3 if b != 'ge10')
print('  (d) split: directional-moderate %.3f | explicit mid-single bucket %.3f' % (d_directional, dec['d'] - d_directional))
print('  (b) split: directional similar/higher with Q3<10 %.3f | around-10 / hyphenated bucket %.3f' % (b_similar, dec['b'] - b_similar))
print('  P(Q3>=10 | a) = %.3f' % (pQ3['ge10'] * cond_tab['ge10']['a'] / dec['a']))
joint = {b: {o: pQ3[b] * cond_tab[b][o] for o in opts} for b in pQ3}
# optional seeded Monte-Carlo check of the tree (10^5 draws)
N = 100000; hits = Counter()
for _ in range(N):
    q3 = random.gauss(mu, sd); b = 'ge10' if q3 >= 10 else ('9to10' if q3 >= 9 else 'lt9')
    r = random.random(); acc = 0.0
    for o in opts:
        acc += cond_tab[b][o]
        if r < acc: hits[o] += 1; break
print('  MC check (seed 20260917, n=%d):' % N, {o: round(hits[o] / N, 3) for o in opts})

# ---- 3. Anchor: Street 4Q26 nights bar +9.9% (Bloomberg MODL, 12 Sep; range +6.6 to +11.6, n 28) and the Street's
#         own 3Q26 bar +11.5% (>=10, so a directional 'similar' would resolve (a)), passed through a stated mapping:
#         bucket = Street level less a 0-2pt cushion (sensitivity assumption, A02-08) -> high-single 0.45,
#         around-10 0.33, low-double 0.12, mid-single 0.10; format split as the 9-10 branch. Dependent construction.
anchor_fmt = dict(bucket=.70, directional=.27, none=.03)
anchor_bucket = dict(a=.12, b=.33, c=.45, d=.10)
anchor = {o: anchor_fmt['bucket'] * anchor_bucket[o] for o in 'abcd'}
anchor['d'] += anchor_fmt['directional'] * .60; anchor['a'] += anchor_fmt['directional'] * .40; anchor['e'] = anchor_fmt['none']
print('== anchor (Street level -> language, dependent construction)', fmt(anchor))

# ---- 4. Final: stated blend 0.5 decomposition + 0.3 base rate + 0.2 anchor, (e) set to 0.04 by the section-6
#         resolution audit (the 0.01 comes from (c)); rounded to 2dp; sums to 1.
w = dict(dec=.5, base=.3, anchor=.2)
blend = {o: w['dec'] * dec[o] + w['base'] * base[o] + w['anchor'] * anchor[o] for o in opts}
print('== blend (0.5/0.3/0.2)', fmt(blend))
final = dict(a=.19, b=.18, c=.30, d=.29, e=.04)
for name, v in [('base', base), ('decomposition', dec), ('anchor', anchor), ('final', final)]:
    assert abs(sum(v.values()) - 1) < 1e-6, (name, sum(v.values()))
print('== final', fmt(final))
print('  literal unions: P(a or b) %.2f | P(c or d) %.2f' % (final['a'] + final['b'], final['c'] + final['d']))
out = os.path.join(here, 'decomposition_v2_output.csv')
with open(out, 'w', newline='') as f:
    wr = csv.writer(f); wr.writerow(['estimate'] + opts)
    for name, v in [('base_rate', base), ('decomposition', dec), ('anchor', anchor), ('blend', blend), ('final', final)]:
        wr.writerow([name] + [round(v[o], 3) for o in opts])
    wr.writerow([]); wr.writerow(['joint_branch'] + opts + ['branch_mass'])
    for b in pQ3: wr.writerow([b] + [round(joint[b][o], 4) for o in opts] + [round(pQ3[b], 4)])
print('written', out)

# ---- 5. Sensitivities (research-log.md section 7); each row is the decomposition re-run with one input reversed
def show(label, p=pQ3, **kw):
    d, _ = tree(p, **kw); print('  %-58s' % label, fmt(d))
print('== sensitivities (decomposition only)')
def bins(m, s): return {'ge10': 1 - Phi((10 - m) / s), '9to10': Phi((10 - m) / s) - Phi((9 - m) / s), 'lt9': Phi((9 - m) / s)}
show('S1a Street/Kalshi view N(11.0, 1.7): P(>=10) 0.72', bins(11.0, 1.7))
show('S1b team baseline N(9.9, 1.48): P(>=10) 0.47', bins(9.9, 1.48))
show('S1c external stack N(9.2, 1.7): P(>=10) 0.32', bins(9.2, 1.7))
show('S1d audit normal N(9.5, 1.48): P(>=10) 0.37', bins(9.5, 1.48))
fl = {b: dict(bucket=1 - .20 - .03, directional=.20, none=.03) for b in pQ3}; show('S2a P(directional) 0.20 in every branch', f=fl)
fh = {b: dict(bucket=1 - .40 - .03, directional=.40, none=.03) for b in pQ3}; show('S2b P(directional) 0.40 in every branch', f=fh)
show('S3a P(moderate | directional) 0.45/0.50/0.65', pm={'ge10': .45, '9to10': .50, 'lt9': .65})
show('S3b P(moderate | directional) 0.65/0.70/0.85', pm={'ge10': .65, '9to10': .70, 'lt9': .85})
bc = {k: dict(v) for k, v in bucket_content.items()}; bc['9to10'] = dict(a=.12, b=.30, c=.48, d=.10); bc['lt9'] = dict(a=.04, b=.12, c=.52, d=.32)
show('S4 case A (8.9) as the Q4 point; Street bar less 1pt', bc=bc)
bc2 = {k: dict(v) for k, v in bucket_content.items()}; bc2['ge10'] = dict(a=.60, b=.15, c=.20, d=.05)
show('S5 comp ignored on a strong October (a|>=10 bucket 0.60)', bc=bc2)
bc3 = {k: dict(v) for k, v in bucket_content.items()}; bc3['lt9'] = dict(a=.02, b=.07, c=.65, d=.26)
show('S6 no mid-single bucket unless Q3 < 8 (lt9 bucket d 0.26)', bc=bc3)
