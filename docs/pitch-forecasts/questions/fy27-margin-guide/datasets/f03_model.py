"""F03: FY27 adjusted EBITDA margin guidance bucket at the Feb 2027 print.
FY26 actual A (known at the print) x sentence regime T -> level -> option.
T1 numeric floor with a 100-200bp haircut (Feb 2024/2025 form); T2 numeric floor at the print rounded down to 0.5 (0-25bp haircut);
T3 qualitative flat ("stable"/"maintain"/"in line", Feb 2022/2023/2026 form) -> bucket of the FY26 reported margin;
T4 expansion language -> bucket of A + 0.5; T5 explicit down / investment year -> (d); T6 no FY27 margin sentence -> (e).
numpy only. Seed 20260917. Run: python f03_model.py (writes f03_sensitivity.csv)."""
import numpy as np, csv, os
HERE = os.path.dirname(os.path.abspath(__file__)); N = 400_000


def bucket(level):
    return np.where(level >= 36.5, 'a', np.where(level >= 36.0, 'b', np.where(level >= 35.5, 'c', 'd')))


def run(seed=20260917, A_mu=35.85, A_sd=0.55, p_defend=0.85, miss_mu=35.4, miss_sd=0.4,
        w=None, h1=(1.0, 2.0), h2=(0.0, 0.25), strict_qual_to_e=False):
    if w is None: w = dict(T1=0.20, T2=0.22, T3=0.30, T4=0.08, T5=0.10, T6=0.10)
    rng = np.random.default_rng(seed)
    A = A_mu + A_sd * rng.standard_normal(N)
    defend = rng.random(N) < p_defend
    A = np.where(defend, np.maximum(A, 35.5 + np.abs(rng.normal(0, 0.12, N))), miss_mu + miss_sd * rng.standard_normal(N))
    keys = list(w.keys()); probs = np.array([w[k] for k in keys]); probs = probs / probs.sum()
    T = rng.choice(len(keys), size=N, p=probs)
    h = rng.uniform(h1[0], h1[1], N); f1 = np.floor((A - h) / 0.5) * 0.5          # T1 floor, rounded down to 0.5
    hh = rng.uniform(h2[0], h2[1], N); f2 = np.floor((A - hh) / 0.5) * 0.5       # T2 floor, rounded down to 0.5
    A_r = np.round(A, 1)
    lvl = np.where(T == 0, f1, np.where(T == 1, f2, np.where(T == 2, A_r, np.where(T == 3, A_r + 0.5, np.nan))))
    opt = bucket(lvl); opt = np.where(T == 4, 'd', opt); opt = np.where(T == 5, 'e', opt)
    if strict_qual_to_e: opt = np.where((T == 2) | (T == 3), 'e', opt)
    vec = {o: float((opt == o).mean()) for o in 'abcde'}
    return dict(vec=vec, A=A, T=T, opt=opt, keys=keys)


if __name__ == '__main__':
    r = run(); A = r['A']
    print('FY26 actual: mean %.2f, P<35.5 %.3f, 35.5-35.9 %.3f, 36.0-36.4 %.3f, >=36.5 %.3f'
          % (A.mean(), (A < 35.5).mean(), ((A >= 35.5) & (A < 36)).mean(), ((A >= 36) & (A < 36.5)).mean(), (A >= 36.5).mean()))
    print('base vector', {k: round(v, 3) for k, v in r['vec'].items()})
    for i, k in enumerate(r['keys']):
        sel = r['T'] == i
        print(k, 'weight %.2f' % sel.mean(), {o: round(float((r['opt'][sel] == o).mean()), 3) for o in 'abcde'})
    sens = [('strict convention: qualitative sentences resolve (e)', dict(strict_qual_to_e=True)),
            ('FY26 actual centred 35.6', dict(A_mu=35.6)), ('FY26 actual centred 36.1', dict(A_mu=36.1)),
            ('FY26 actual centred 36.4', dict(A_mu=36.4)),
            ('haircut regime dominant (T1 0.40, T3 0.15)', dict(w=dict(T1=0.40, T2=0.20, T3=0.15, T4=0.05, T5=0.12, T6=0.08))),
            ('flat regime dominant (T3 0.45, T1 0.10)', dict(w=dict(T1=0.10, T2=0.22, T3=0.45, T4=0.08, T5=0.08, T6=0.07))),
            ('investment-year 0.25', dict(w=dict(T1=0.20, T2=0.18, T3=0.22, T4=0.05, T5=0.25, T6=0.10))),
            ('expand 0.20 (bull)', dict(w=dict(T1=0.15, T2=0.22, T3=0.25, T4=0.20, T5=0.08, T6=0.10))),
            ('no floor defence (p_defend 0.5)', dict(p_defend=0.5)), ('haircut 1.5-2.0 only', dict(h1=(1.5, 2.0)))]
    with open(os.path.join(HERE, 'f03_sensitivity.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['case', 'a', 'b', 'c', 'd', 'e'])
        w.writerow(['base'] + [round(r['vec'][o], 3) for o in 'abcde'])
        for name, kw in sens:
            v = run(**kw)['vec']; w.writerow([name] + [round(v[o], 3) for o in 'abcde'])
            print('%-55s' % name, {o: round(v[o], 3) for o in 'abcde'})
