"""C03 fy26-revenue-guide-language, revision 2 (audit response to A02): reproduces the arithmetic, the three
estimates and the final vector.
Run: py -3.13 docs/pitch-forecasts/questions/fy26-revenue-guide-language/datasets/decomposition_v2.py
Dependency-free (standard library only). Deterministic; the seed only guards the Monte-Carlo check of the
closed-form normal probabilities.
Changes from decomposition.py: (1) the FY predictive sd carries a stated Q3-print / Q4-guide correlation
(rho 0.5 base; 0 and 0.8 as sensitivities) (A02-07); (2) the anchor deflates only the 4Q26 consensus by kappa,
not the whole FY, and is labelled a dependent level-to-language construction (A02-01, A02-06); (3) P(no FY
revenue sentence) is 0.12, carrying the 3Q22 omission of an existing FY sentence (A02-04); (4) the base rate is
the November reference class 3/4 conversions + 1/4 omission, regime-conditioned, and is labelled analogical
(A02-04); (5) the bridge min/max is named a conversion envelope, not an 80% interval (A02-07)."""
import csv, os, math, random
here = os.path.dirname(os.path.abspath(__file__))
opts = ['a', 'b', 'c', 'd', 'e']
Phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
random.seed(20260917)
def fmt(v): return {o: round(v.get(o, 0.0), 3) for o in opts}

FY25 = 12241.0; H1 = 6286.0           # driver history (claim 5)
LSEG = dict(q3=4744.32212, q4=3161.81627, fy=14189.55705, q3_sd=24.27626, q4_sd=48.55902, n_rev=37)  # 03_current_consensus.csv, obs 2026-09-07, row 2026-09-11
KAPPA = 0.006; KAPPA_SD = 0.003     # L0 at-print consensus vs quarterly guide midpoint: mean 0.604%, n 12, sd 0.30pp; trailing-8 0.516%

# ---- Arithmetic: FY26 growth implied by 9M actual + 4Q26 guide midpoint. Q3 ~ N(4,795, 40) (team 4,804 / cushion-
#      adjusted 4,820 / LSEG 4,744); Q4 mid ~ N(3,085, 80) (bridge v3 3,178 deflated by the Q4 cushion 3.0-3.9%).
#      The $40M / $80M are ASSUMED sds; rho is the shared-demand dependence between the Q3 print and the Q4 guide.
def implied(q3m=4795.0, q3s=40.0, q4m=3085.0, q4s=80.0, rho=0.5):
    mu = H1 + q3m + q4m; sd = math.sqrt(q3s ** 2 + q4s ** 2 + 2 * rho * q3s * q4s)
    return (mu / FY25 - 1) * 100, sd / FY25 * 100, mu, sd

def numeric_conditional(g, gs, rounddown_w=0.5):
    """P(option | a numeric FY sentence) averaged over nearest-integer and round-down wording conventions."""
    Pr = lambda lo, hi: Phi((hi - g) / gs) - Phi((lo - g) / gs)
    near = dict(a=1 - Phi((15.5 - g) / gs), c=Pr(14.5, 15.5), d=Phi((14.5 - g) / gs))
    rd = dict(a=1 - Phi((16 - g) / gs), c=Pr(15, 16), d=Phi((15 - g) / gs))
    nm = {k: (1 - rounddown_w) * near[k] + rounddown_w * rd[k] for k in 'acd'}
    nm['b'] = 0.02; s = sum(nm.values()); nm = {k: v / s for k, v in nm.items()}; nm['e'] = 0.0
    return nm

g, gs, fy_mu, fy_sd = implied()
print('FY26 implied by 9M + Q4 guide mid: $%.0fM -> %.2f%%  sd %.2fpp (rho 0.5; rho 0 gives %.2fpp)' % (fy_mu, g, gs, implied(rho=0)[1]))
print('  P(>=16.0) %.3f | P(15.0-16.0) %.3f | P(<15.0) %.3f' % (1 - Phi((16 - g) / gs), Phi((16 - g) / gs) - Phi((15 - g) / gs), Phi((15 - g) / gs)))
print('  P(>=15.5) %.3f | P(14.5-15.5) %.3f | P(<14.5) %.3f' % (1 - Phi((15.5 - g) / gs), Phi((15.5 - g) / gs) - Phi((14.5 - g) / gs), Phi((14.5 - g) / gs)))
num = numeric_conditional(g, gs)
print('  given a numeric sentence:', fmt(num))
# seeded Monte-Carlo check of the closed form (bivariate normal with rho 0.5)
N = 200000; hits = dict(ge16=0, b15=0, ge155=0)
for _ in range(N):
    z1 = random.gauss(0, 1); z2 = 0.5 * z1 + math.sqrt(1 - 0.25) * random.gauss(0, 1)
    fy = H1 + 4795 + 40 * z1 + 3085 + 80 * z2; gr = (fy / FY25 - 1) * 100
    hits['ge16'] += gr >= 16; hits['b15'] += gr < 15; hits['ge155'] += gr >= 15.5
print('  MC check (seed 20260917, n=%d): P(>=16) %.3f  P(<15) %.3f  P(>=15.5) %.3f' % (N, hits['ge16'] / N, hits['b15'] / N, hits['ge155'] / N))

# ---- Decomposition: P(format) x P(option | format)
p_numeric, p_descr, p_none = 0.55, 0.33, 0.12
descr = dict(a=.30, b=.45, c=.15, d=.10, e=0.0)
def combine(nm, pn=p_numeric, pd=p_descr, p0=p_none):
    v = {o: pn * nm.get(o, 0) + pd * descr[o] for o in 'abcd'}; v['e'] = p0; s = sum(v.values())
    return {k: x / s for k, x in v.items()}
dec = combine(num)
print('decomposition', fmt(dec))

# ---- Base rate (analogical, A02-04): November letters with an existing same-year FY guide: 3Q22 omitted (a
#      qualitative y/y margin sentence), 3Q23/3Q24/3Q25 converted to an 'approximately' point above the floor
#      (+150bp qualitative, +50bp, +50bp); 0 of 4 reiterated. Raw Laplace over {convert, omit, reiterate}:
raw = dict(convert=(3 + 1) / 7, omit=(1 + 1) / 7, reiterate=(0 + 1) / 7)
# Regime-conditioned: both numeric-floor years (FY24, FY25) converted 2/2 and the two 2026 letters lead the FY
# section with the revenue bullet, so the omission share is shaded from 0.29 to 0.15 and reiteration to 0.15.
reg = dict(convert=0.70, omit=0.15, reiterate=0.15)
# The analogy carries no level: the +0.5pp margin steps map to 'approximately 15.5%' (c) or a rounded
# 'approximately 16%' (a); split the conversion 0.47 (a) / 0.47 (c) / 0.06 (d, a point below 15).
base = dict(a=reg['convert'] * .47, b=reg['reiterate'], c=reg['convert'] * .47, d=reg['convert'] * .06, e=reg['omit'])
print('base rate raw Laplace', {k: round(v, 3) for k, v in raw.items()}, '| regime-conditioned vector', fmt(base))

# ---- Anchor (A02-01 corrected): Street-implied FY guide = H1 actual + LSEG 3Q26 (proxy for the print) +
#      LSEG 4Q26 deflated by kappa on the Q4 quarter only; sd from the Q3 print error (~$50M, the 19-print
#      actual-vs-consensus), kappa sd and the Q4 consensus dispersion; then the same level-to-language mapping.
anchor_mu = H1 + LSEG['q3'] + LSEG['q4'] / (1 + KAPPA)
anchor_sd = math.sqrt(50 ** 2 + (KAPPA_SD * LSEG['q4']) ** 2 + LSEG['q4_sd'] ** 2)
ag, ags = (anchor_mu / FY25 - 1) * 100, anchor_sd / FY25 * 100
anchor = combine(numeric_conditional(ag, ags))
print('anchor: Street-implied FY guide $%.1fM -> %.3f%% (sd %.2fpp); whole-FY deflation (rev 1, wrong) $%.1fM -> %.2f%%' % (
    anchor_mu, ag, ags, LSEG['fy'] / (1 + KAPPA), (LSEG['fy'] / (1 + KAPPA) / FY25 - 1) * 100))
print('anchor vector (dependent construction)', fmt(anchor))

# ---- Final: stated blend 0.5 decomposition + 0.3 base + 0.2 anchor, rounded to 2dp
w = dict(dec=.5, base=.3, anchor=.2)
blend = {o: w['dec'] * dec[o] + w['base'] * base[o] + w['anchor'] * anchor[o] for o in opts}
print('blend (0.5/0.3/0.2)', fmt(blend))
final = dict(a=.36, b=.16, c=.28, d=.08, e=.12)
for name, v in [('base', base), ('decomposition', dec), ('anchor', anchor), ('final', final)]:
    assert abs(sum(v.values()) - 1) < 1e-6, (name, sum(v.values()))
print('final', fmt(final), '| P(a or c) %.2f  P(a or b or c) %.2f' % (final['a'] + final['c'], final['a'] + final['b'] + final['c']))
out = os.path.join(here, 'decomposition_v2_output.csv')
with open(out, 'w', newline='') as f:
    wr = csv.writer(f); wr.writerow(['estimate'] + opts)
    for name, v in [('base_rate', base), ('decomposition', dec), ('anchor', anchor), ('blend', blend), ('final', final)]:
        wr.writerow([name] + [round(v[o], 3) for o in opts])
print('written', out)

# ---- Sensitivities (research-log.md section 7): decomposition re-run with one input reversed
def sens(label, q3m=4795.0, q3s=40.0, q4m=3085.0, q4s=80.0, rho=0.5, pn=p_numeric, pd=p_descr, p0=p_none, rdw=0.5):
    g, gs, _, _ = implied(q3m, q3s, q4m, q4s, rho); nm = numeric_conditional(g, gs, rdw); v = combine(nm, pn, pd, p0)
    print('  %-52s FY %.2f%% +/- %.2f  num %s  -> %s' % (label, g, gs, fmt(nm), fmt(v)))
print('sensitivities')
sens('S0 base (rho 0.5)')
sens('S1 B2 kernel Q4 mid N(3161, 117)', q4m=3161, q4s=117)
sens('S2 Street-centred Q3 N(4744, 30)', q3m=4744, q3s=30)
sens('S2b Street-implied Q4 guide mid 3,143 (kappa on Q4)', q4m=3143)
sens('S3a P(numeric) 0.75 (descriptive 0.13)', pn=.75, pd=.13)
sens('S3b P(numeric) 0.35 (descriptive 0.53)', pn=.35, pd=.53)
sens('S4 round-down only', rdw=1.0)
sens('S4b nearest-integer only', rdw=0.0)
sens('S5 P(no sentence) 0.25 (numeric 0.45, descr 0.30)', pn=.45, pd=.30, p0=.25)
sens('S6a rho 0 (independent errors)', rho=0.0)
sens('S6b rho 0.8', rho=0.8)
