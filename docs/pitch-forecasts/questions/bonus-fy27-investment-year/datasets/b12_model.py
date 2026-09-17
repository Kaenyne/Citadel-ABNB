"""B12: P(at the Feb 2027 print the FY27 adj. EBITDA margin floor/point is below the FY26 reported margin, or management says
FY27 margin will be down/lower / frames 2027 as an investment year with margin below FY26).
Extends F03's model (../../fy27-margin-guide/datasets/f03_model.py: same FY26 print distribution, same sentence regimes, same seed)
with the two resolution readings:
  literal  : Yes if the numeric floor/point < FY26 reported margin (letter prints to one decimal), or T5 explicit down / investment year;
  material : Yes if the floor/point is >= 50bp below the FY26 print (the FY24/FY25 haircut form), or T5.
Regimes: T1 haircut floor (A - U(1,2), rounded down to 0.5); T2 floor at the print rounded down to 0.5 (0-25bp haircut);
T3 qualitative flat; T4 expand; T5 explicit down / investment year; T6 no sentence. Also reports P(Yes) with T2 read as flat
(the reading F03 used for its implied B12 of 0.35). numpy only. Seed 20260917. Run: py -3.13 .../b12_model.py
"""
import numpy as np, csv, os
HERE = os.path.dirname(os.path.abspath(__file__)); N = 400_000

def run(seed=20260917, A_mu=35.85, A_sd=0.55, p_defend=0.85, miss_mu=35.4, miss_sd=0.4, w=None, h1=(1.0, 2.0), h2=(0.0, 0.25), material_bp=0.5):
    if w is None: w = dict(T1=0.20, T2=0.22, T3=0.30, T4=0.08, T5=0.10, T6=0.10)
    rng = np.random.default_rng(seed)
    A = A_mu + A_sd*rng.standard_normal(N)
    defend = rng.random(N) < p_defend
    A = np.where(defend, np.maximum(A, 35.5 + np.abs(rng.normal(0, 0.12, N))), miss_mu + miss_sd*rng.standard_normal(N))
    keys = list(w.keys()); probs = np.array([w[k] for k in keys]); probs = probs/probs.sum()
    T = rng.choice(len(keys), size=N, p=probs)
    A_r = np.round(A, 1)                                                     # the letter prints the FY26 margin to one decimal
    f1 = np.floor((A - rng.uniform(h1[0], h1[1], N))/0.5)*0.5                # T1 floor
    f2 = np.floor((A - rng.uniform(h2[0], h2[1], N))/0.5)*0.5                # T2 floor
    lvl = np.where(T == 0, f1, np.where(T == 1, f2, np.where(T == 2, A_r, np.where(T == 3, A_r + 0.5, np.nan))))
    gap = A_r - lvl                                                          # positive = floor below the print
    literal = (T == 4) | ((T <= 1) & (gap > 1e-9))
    material = (T == 4) | ((T <= 1) & (gap >= material_bp - 1e-9))
    t2_as_flat = (T == 4) | (T == 0)                                         # F03's implied-B12 reading
    out = dict(p_literal=float(literal.mean()), p_material=float(material.mean()), p_t2_as_flat=float(t2_as_flat.mean()),
               p_T5=float((T == 4).mean()), p_T1=float((T == 0).mean()), p_T2_yes_literal=float(((T == 1) & literal).mean()),
               p_T2_yes_material=float(((T == 1) & material).mean()),
               gap_given_yes_literal={"mean": float(gap[literal & (T <= 1)].mean()), "p10": float(np.percentile(gap[literal & (T <= 1)], 10)),
                                      "p50": float(np.percentile(gap[literal & (T <= 1)], 50)), "p90": float(np.percentile(gap[literal & (T <= 1)], 90))},
               share_yes_literal_with_gap_lt_50bp=float(((T <= 1) & literal & (gap < 0.5)).sum()/literal.sum()),
               A_mean=float(A.mean()), P_A_lt_355=float((A < 35.5).mean()),
               by_A_bucket={lab: {"literal": float(literal[m].mean()), "material": float(material[m].mean())} for lab, m in
                            [("A<35.5", A < 35.5), ("35.5-35.9", (A >= 35.5) & (A < 36.0)), ("36.0-36.4", (A >= 36.0) & (A < 36.5)), ("A>=36.5", A >= 36.5)]},
               f03_vector={o: float((np.where(T == 4, 'd', np.where(T == 5, 'e', np.where(lvl >= 36.5, 'a', np.where(lvl >= 36.0, 'b', np.where(lvl >= 35.5, 'c', 'd'))))) == o).mean()) for o in 'abcde'})
    return out

if __name__ == '__main__':
    r = run(); import json; print(json.dumps(r, indent=1))
    sens = [('base', {}),
            ('FY26 actual centred 35.6', dict(A_mu=35.6)), ('FY26 actual centred 36.1', dict(A_mu=36.1)), ('FY26 actual centred 36.4', dict(A_mu=36.4)),
            ('haircut regime dominant (T1 0.40, T3 0.15)', dict(w=dict(T1=0.40, T2=0.20, T3=0.15, T4=0.05, T5=0.12, T6=0.08))),
            ('flat regime dominant (T3 0.45, T1 0.10)', dict(w=dict(T1=0.10, T2=0.22, T3=0.45, T4=0.08, T5=0.08, T6=0.07))),
            ('investment-year 0.25', dict(w=dict(T1=0.20, T2=0.18, T3=0.22, T4=0.05, T5=0.25, T6=0.10))),
            ('investment-year 0.04 (never said down for a full year)', dict(w=dict(T1=0.22, T2=0.24, T3=0.32, T4=0.08, T5=0.04, T6=0.10))),
            ('expand 0.20 (bull)', dict(w=dict(T1=0.15, T2=0.22, T3=0.25, T4=0.20, T5=0.08, T6=0.10))),
            ('no floor defence (p_defend 0.5)', dict(p_defend=0.5)), ('haircut 1.5-2.0 only', dict(h1=(1.5, 2.0))),
            ('T2 haircut 0-50bp (floor rounded down from a wider band)', dict(h2=(0.0, 0.5))),
            ('material threshold 100bp', dict(material_bp=1.0)),
            ('numeric-floor regimes 0.55 (T1 0.28, T2 0.27), flat 0.20', dict(w=dict(T1=0.28, T2=0.27, T3=0.20, T4=0.07, T5=0.10, T6=0.08)))]
    with open(os.path.join(HERE, 'b12_sensitivity.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['case', 'p_literal', 'p_material', 'p_t2_as_flat', 'p_T5', 'f03_d'])
        for name, kw in sens:
            v = run(**kw); w.writerow([name, round(v['p_literal'], 3), round(v['p_material'], 3), round(v['p_t2_as_flat'], 3), round(v['p_T5'], 3), round(v['f03_vector']['d'], 3)])
            print('%-70s literal %.3f  material %.3f  t2-as-flat %.3f  F03(d) %.3f' % (name, v['p_literal'], v['p_material'], v['p_t2_as_flat'], v['f03_vector']['d']))
