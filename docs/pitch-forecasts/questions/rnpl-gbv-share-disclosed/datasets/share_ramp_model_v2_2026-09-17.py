"""Revision-2 Monte Carlo of the true 3Q26 RNPL share of GBV (C06), after audit A04-07/A04-08/A04-09.
Run from repo root: py -3.13 docs/pitch-forecasts/questions/rnpl-gbv-share-disclosed/datasets/share_ramp_model_v2_2026-09-17.py
Every input is an ASSUMPTION (labelled), not a disclosed quantity. Structure (v2 base):
  s1  ~ U(19, 21)        1Q26 true share behind 'roughly 20%' (D031)
  d12 ~ U(0.5, 3.5)      1Q26->2Q26 increment (the ex-US rollout going from ~6 of 13 weeks to a full quarter, plus adoption ramp);
                         s2 = s1 + d12 is REJECTED unless in [20.5, 23.5], the range 'over 20%' (D043) can cover before management's
                         vocabulary would switch to 'nearly a quarter' (milestone habit, D022/D031/D041/D043/D047)
  ramp = U(0, 0.5) * d12 residual ex-US ramp in Q3 as a fraction of the observed Q2 step (D033, D036); ties the ramp to the one
                         observed increment instead of an unanchored U(0,2)
  exp ~ 0.75*Exp(1.4) + 0.25*Exp(3.5), capped 8   July 2026 eligibility expansion (D044: types unnamed, size unquantified);
                         rev-1 was Exp(1.4) alone; the mixture keeps the large-expansion case in view (audit A04-08)
  mix ~ U(-1, +1)        Q3 booking-mix noise, SYMMETRIC; replaces rev-1's directional U(-2,0) 'lead-time' penalty, which had no
                         independent evidence (Q3 is not the lowest-GBV quarter: 2023-25 means Q3 $20.4bn vs Q4 $17.8bn; lead time undisclosed)
The balance-sheet backlog solve (14-23% unpaid share) is NOT used as a constraint on the flow share (A04-09).
Writes share_ramp_model_v2_2026-09-17.csv next to this file."""
import random, csv, pathlib
def sim(n=200000, seed=7, s1=(19, 21), d12=(0.5, 3.5), s2_ok=(20.5, 23.5), ramp_frac=(0, 0.5),
        exp_mix=((0.75, 1.4), (0.25, 3.5)), cap=8, mix=(-1, 1), fixed_s2=None, fixed_ramp=None):
    rng = random.Random(seed); c = [0, 0, 0]; tot = 0
    while tot < n:
        if fixed_s2 is None:
            a = rng.uniform(*s1); d = rng.uniform(*d12); s2 = a + d
            if not (s2_ok[0] <= s2 <= s2_ok[1]):
                continue
            ramp = rng.uniform(*ramp_frac) * d
        else:
            s2 = rng.uniform(*fixed_s2); ramp = rng.uniform(*fixed_ramp)
        s = s2 + ramp
        u = rng.random(); acc = 0
        for w, mean in exp_mix:
            acc += w
            if u <= acc:
                s += min(cap, rng.expovariate(1 / mean)); break
        s += rng.uniform(*mix)
        c[0 if s >= 24.5 else 1 if s >= 20.5 else 2] += 1; tot += 1
    return [x / n for x in c]
def wording(p, disclose):
    """disclose: P(disclosed as a 3Q26 GBV share | true bucket) for (>=25, 21-24, <=20).
    Language map (assumption): true>=24.5 -> (a) 0.85, (b) 0.05 ('nearly a quarter' understatement), (c) 0.10 ('over 20%' repeated);
    21-24 -> (b) 0.45, (c) 0.55; <=20 -> (c) 1.0"""
    hi, mid, lo = p; dh, dm, dl = disclose
    a = dh * 0.85 * hi
    b = dh * 0.05 * hi + dm * 0.45 * mid
    c = dh * 0.10 * hi + dm * 0.55 * mid + dl * lo
    return [a, b, c, 1 - (a + b + c)]
FLAT = (0.70, 0.70, 0.70)
LEVEL = (0.75, 0.68, 0.55)   # milestone habit (assumption): 'a quarter of GBV' likelier to be stated than a 22% reading; overall ~0.70
variants = [
    ("v2 base", dict()),
    ("v2 expansion Exp(1.4) only", dict(exp_mix=((1.0, 1.4),))),
    ("v2 expansion Exp(3.5) only (large)", dict(exp_mix=((1.0, 3.5),))),
    ("v2 no July expansion", dict(exp_mix=((1.0, 1e-9),))),
    ("v2 no residual ramp", dict(ramp_frac=(0, 0))),
    ("v2 full residual ramp (0-100% of Q2 step)", dict(ramp_frac=(0, 1.0))),
    ("v2 with rev-1 directional penalty U(-2,0)", dict(mix=(-2, 0))),
    ("v2 s2 capped at 22.5 ('over 20%' read narrowly)", dict(s2_ok=(20.5, 22.5))),
    ("audit no-season benchmark (rev-1 inputs, no penalty)", dict(fixed_s2=(21, 23), fixed_ramp=(0, 2), exp_mix=((1.0, 1.4),), cap=6, mix=(0, 0))),
    ("rev-1 as published", dict(fixed_s2=(21, 23), fixed_ramp=(0, 2), exp_mix=((1.0, 1.4),), cap=6, mix=(-2, 0))),
]
rows = []
for name, kw in variants:
    p = sim(**kw); wf = wording(p, FLAT); wl = wording(p, LEVEL)
    rows.append([name] + [round(x, 4) for x in p] + [round(x, 4) for x in wf] + [round(x, 4) for x in wl])
    print(f"{name:55s} true>=25 {p[0]:.4f} 21-24 {p[1]:.4f} <=20 {p[2]:.4f} | flat0.70 a/b/c/d {wf[0]:.3f}/{wf[1]:.3f}/{wf[2]:.3f}/{wf[3]:.3f} | level-gate {wl[0]:.3f}/{wl[1]:.3f}/{wl[2]:.3f}/{wl[3]:.3f}")
p = sim()
for g in (0.50, 0.67, 0.74, 0.77, 0.81, 0.90):
    w = wording(p, (g, g, g)); print(f"v2 base, flat gate {g:.2f}: a/b/c/d {w[0]:.3f}/{w[1]:.3f}/{w[2]:.3f}/{w[3]:.3f}")
w = wording(p, LEVEL); print("v2 base, level gate, precise-figure map (21-24 -> b 0.65):", [round(x, 3) for x in [w[0], LEVEL[1]*0.65*p[1] + LEVEL[0]*0.05*p[0], LEVEL[0]*0.10*p[0] + LEVEL[1]*0.35*p[1] + LEVEL[2]*p[2]]], "d", round(w[3], 3))
with open(pathlib.Path(__file__).with_suffix('.csv'), 'w', newline='') as f:
    wr = csv.writer(f)
    wr.writerow(['variant', 'p_true_ge25', 'p_true_21_24', 'p_true_le20', 'a_flat70', 'b_flat70', 'c_flat70', 'd_flat70', 'a_level', 'b_level', 'c_level', 'd_level'])
    wr.writerows(rows)
    wr.writerow(['inputs', 'see docstring: s1 U(19,21); d12 U(0.5,3.5) with s2 in [20.5,23.5]; ramp U(0,0.5)*d12; exp 0.75*Exp(1.4)+0.25*Exp(3.5) cap 8; mix U(-1,1); N=200000 seed 7; level gate (0.75,0.68,0.55)'])
