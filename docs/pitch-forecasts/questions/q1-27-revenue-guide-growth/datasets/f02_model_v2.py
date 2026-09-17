"""F02 revision 2 (audit A08 response): y/y growth implied by the 1Q27 revenue guide midpoint (Feb 2027 letter), base 1Q26 $2,678M.
Changes vs f02_model.py / f02_final_mixture.py (rev 1, left untouched):
  * 3Q26 / 4Q26 nights drawn from the ADOPTED 4Q26 object (R16/B13 blend; same sampler as F01 v2), not N(8.1,1.7)+12% tail.
  * Recognition residual re-based on the C01 rev-2 validated structure: eps ~ N(-0.19%, 2.05%) [kernel last3_ex_covid PIT bias/RMSE],
    RNPL leakage Bernoulli(0.40) x -0.84% [K1 central cell], EEA/CH single-fee step {0, +0.55, +1.11}% at 45/40/15 (fully in force by 1Q27).
    Rev-1 used a single N(-0.5%, 2.5%) tilt with no fee term.
  * Final = 0.70 base + 0.30 pre-registration convention (lambda 12.66 ewm, eps 0, no leakage, no fee, cushion 2.2%), as rev 1.
numpy only. Seed 20260917. Run: python f02_model_v2.py (writes f02_v2_summary.csv, f02_v2_percentiles.csv, f02_v2_sensitivity.csv, f02_v2_hist.csv)."""
import numpy as np, csv, os
HERE = os.path.dirname(os.path.abspath(__file__)); N = 400_000
BASE_1Q26 = 2678.0; BASE_Q4 = 121.9


def q4_adopted(rng, n=N, w=(0.5, 0.3, 0.2), v1_mu=8.1, v1_beta=0.5, v1_sd=1.4, tail_w=0.12, tail_mu=5.5, tail_sd=1.5,
               q3_mu=9.67, q3_sd=1.70, v2_vec=(0.21, 0.19, 0.39, 0.17, 0.04), v2_mids=(10.75, 9.75, 8.0, 6.0), v2_c_mu=0.9, v2_c_sd=1.3,
               v3_mu=9.926, v3_sd=1.23, legacy=False):
    """Identical to F01 v2's sampler (q1-27-nights-guide-above-82/datasets/f01_model_v2.py)."""
    q3 = q3_mu + q3_sd * rng.standard_normal(n)
    if legacy:
        q4 = 8.1 + 1.7 * (0.5 * (q3 - q3_mu) / q3_sd + np.sqrt(0.75) * rng.standard_normal(n)); sh = rng.random(n) < 0.12
        q4 = np.where(sh, 5.5 + 1.5 * rng.standard_normal(n), q4); return q4, q3
    tail = rng.random(n) < tail_w
    q4_v1 = np.where(tail, tail_mu + v1_beta * (q3 - q3_mu) + tail_sd * rng.standard_normal(n),
                     v1_mu + v1_beta * (q3 - q3_mu) + v1_sd * rng.standard_normal(n))
    k = rng.choice(5, size=n, p=np.array(v2_vec) / sum(v2_vec))
    mids = np.array(list(v2_mids) + [np.nan])[k]
    q4_v2 = np.where(k == 4, q4_v1, mids + v2_c_mu + v2_c_sd * rng.standard_normal(n))
    q4_v3 = v3_mu + v3_sd * rng.standard_normal(n)
    u = rng.random(n)
    q4 = np.where(u < w[0], q4_v1, np.where(u < w[0] + w[1], q4_v2, q4_v3))
    q3_alt = q3_mu + 0.45 * (q3_sd / 1.9) * (q4 - 8.7) + q3_sd * np.sqrt(1 - 0.45 ** 2) * rng.standard_normal(n)
    q3 = np.where(u < w[0], q3, q3_alt)
    return q4, q3


def run(seed=20260917, a3_mu=3.3, a3_sd=1.3, a4_mu=4.0, a4_sd=1.5, lam=12.612, eps_mu=-0.19, eps_sd=2.05,
        leak_p=0.40, leak=0.84, fee_w=(0.45, 0.40, 0.15), fee_v=(0.0, 0.55, 1.11), c_mu=2.5, c_sd=1.2, q4_kw=None, legacy=False):
    rng = np.random.default_rng(seed)
    n4, n3 = q4_adopted(rng, legacy=legacy, **(q4_kw or {}))
    a3 = a3_mu + a3_sd * rng.standard_normal(N)
    gbv3 = 133.6 * (1 + n3 / 100) * 171.29 * (1 + a3 / 100)              # $M
    a4 = a4_mu + a4_sd * rng.standard_normal(N)
    gbv4 = 20400.0 * (1 + n4 / 100) * (1 + a4 / 100)
    L = (2 / 3) * gbv4 + (1 / 3) * gbv3
    eps = eps_mu + eps_sd * rng.standard_normal(N)
    lk = np.where(rng.random(N) < leak_p, leak, 0.0)
    fee = np.array(fee_v)[rng.choice(3, size=N, p=np.array(fee_w) / sum(fee_w))]
    print_ = lam / 100 * (1 + (eps - lk + fee) / 100) * L
    c = c_mu + c_sd * rng.standard_normal(N)
    guide = np.round(print_ / (1 + c / 100) / 5) * 5
    g = (guide / BASE_1Q26 - 1) * 100
    return dict(g=g, print_=print_, guide=guide, gbv3=gbv3, gbv4=gbv4, n4=n4, n3=n3, L=L)


def summ(g):
    pct = np.percentile(g, [5, 10, 25, 50, 75, 90, 95])
    return dict(mean=g.mean(), sd=g.std(), p5=pct[0], p10=pct[1], p25=pct[2], p50=pct[3], p75=pct[4], p90=pct[5], p95=pct[6],
                p_lt10=(g < 10).mean(), p_lt9_4=(g < 9.4).mean(), p_ge12=(g >= 12).mean(), p_lt8=(g < 8).mean(), p_ge14=(g >= 14).mean(),
                p_lt5=(g < 5).mean(), p_lt0=(g < 0).mean(), p_gt20=(g > 20).mean())


PREREG = dict(seed=20260918, lam=12.66, eps_mu=0.0, leak_p=0.0, fee_w=(1, 0, 0), c_mu=2.2)


def final(**kw):
    """0.70 x base(kw) + 0.30 x pre-registration convention (same 4Q26 object)."""
    rA = run(**kw); kwB = dict(PREREG); kwB.update({k: v for k, v in kw.items() if k in ('q4_kw', 'legacy')})
    rB = run(**kwB); k = int(0.7 * N)
    g = np.concatenate([rA['g'][:k], rB['g'][:N - k]]); guide = np.concatenate([rA['guide'][:k], rB['guide'][:N - k]])
    return g, guide, rA, rB


if __name__ == '__main__':
    gF, guideF, rA, rB = final(); sA, sB, sF = summ(rA['g']), summ(rB['g']), summ(gF)
    print('base: guide median $%.0fM, print median $%.0fM, GBV3 %.0f, GBV4 %.0f, L %.0f, n4 mean %.2f, n3 mean %.2f'
          % (np.median(rA['guide']), np.median(rA['print_']), np.median(rA['gbv3']), np.median(rA['gbv4']), np.median(rA['L']), rA['n4'].mean(), rA['n3'].mean()))
    for name, s in [('base', sA), ('prereg', sB), ('FINAL', sF)]:
        print(name, {k: round(float(v), 3) for k, v in s.items()})
    with open(os.path.join(HERE, 'f02_v2_summary.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['component', 'stat', 'value'])
        for name, s in [('base', sA), ('prereg', sB), ('final', sF)]:
            for k, v in s.items(): w.writerow([name, k, round(float(v), 4)])
        w.writerow(['base', 'guide_median_musd', round(float(np.median(rA['guide'])), 1)]); w.writerow(['base', 'print_median_musd', round(float(np.median(rA['print_'])), 1)])
        w.writerow(['final', 'guide_median_musd', round(float(np.median(guideF)), 1)])
    with open(os.path.join(HERE, 'f02_v2_percentiles.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['percentile', 'growth_pct_final', 'guide_musd_final', 'growth_pct_base'])
        for p in [5, 10, 25, 50, 75, 90, 95]:
            w.writerow([p, round(float(np.percentile(gF, p)), 2), round(float(np.percentile(guideF, p)), 0), round(float(np.percentile(rA['g'], p)), 2)])
    hist, edges = np.histogram(gF, bins=np.arange(-2, 24, 1.0))
    with open(os.path.join(HERE, 'f02_v2_hist.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['bin_lo', 'bin_hi', 'share']); [w.writerow([edges[i], edges[i + 1], round(hist[i] / N, 4)]) for i in range(len(hist))]
    sens = [('final (adopted 4Q26 object, C01 rev-2 residual)', {}),
            ('rev-1 4Q26 print mixture (legacy), rev-2 residual', dict(legacy=True)),
            ('rev-1 residual N(-0.5,2.5), no leak/fee, adopted object', dict(eps_mu=-0.5, eps_sd=2.5, leak_p=0.0, fee_w=(1, 0, 0))),
            ('no fee step', dict(fee_w=(1, 0, 0))), ('fee step full +1.11 certain', dict(fee_w=(0, 0, 1))),
            ('no RNPL leakage branch', dict(leak_p=0.0)), ('leakage certain -0.84', dict(leak_p=1.0)), ('leakage top of K1 -1.39 certain', dict(leak_p=1.0, leak=1.39)),
            ('4Q26 decomposition only (V1)', dict(q4_kw=dict(w=(1.0, 0, 0)))), ('4Q26 Street-centred V1 9.93 no tail', dict(q4_kw=dict(w=(1.0, 0, 0), v1_mu=9.93, tail_w=0.0))),
            ('4Q26 V1 centre 7.61 (RNPL module)', dict(q4_kw=dict(v1_mu=7.61))), ('4Q26 short case 5.0 certain', dict(q4_kw=dict(w=(1.0, 0, 0), v1_mu=5.0, v1_sd=1.2, tail_w=0.0))),
            ('3Q26 nights centre 11.0 (Kalshi/MODL)', dict(q4_kw=dict(q3_mu=11.0))), ('3Q26 nights centre 8.5', dict(q4_kw=dict(q3_mu=8.5))),
            ('lambda 12.72 (2023-25 mean) eps 0 in base', dict(lam=12.72, eps_mu=0.0)), ('eps sd 1.5', dict(eps_sd=1.5)), ('eps sd 3.5 (1Q25-type miss)', dict(eps_sd=3.5)),
            ('cushion 1.86 (trailing-8 all-quarter)', dict(c_mu=1.86)), ('cushion 2.87 (five-Q1 mean)', dict(c_mu=2.87)), ('cushion 4.0 (1Q22/1Q24-type)', dict(c_mu=4.0)),
            ('ADR_4Q26 +2.5', dict(a4_mu=2.5)), ('ADR_4Q26 +5.5', dict(a4_mu=5.5)),
            ('joint bull: Street V1 9.9 no tail, ADR 5.0, eps +0.5, no leak, full fee, cushion 1.86', dict(q4_kw=dict(v1_mu=9.9, tail_w=0.0), a4_mu=5.0, eps_mu=0.5, leak_p=0.0, fee_w=(0, 0, 1), c_mu=1.86)),
            ('joint bear: V1 6.5, ADR 2.5, leak certain -1.39, no fee, cushion 3.0', dict(q4_kw=dict(v1_mu=6.5), a4_mu=2.5, leak_p=1.0, leak=1.39, fee_w=(1, 0, 0), c_mu=3.0)),
            ('5 Nov bucket low double digits (V2 mid 10.75 certain)', dict(q4_kw=dict(w=(0, 1.0, 0), v2_vec=(1, 0, 0, 0, 0)))),
            ('5 Nov bucket high single digits (V2 mid 8.0 certain)', dict(q4_kw=dict(w=(0, 1.0, 0), v2_vec=(0, 0, 1, 0, 0)))),
            ('5 Nov bucket mid single / moderate (V2 mid 6.0 certain)', dict(q4_kw=dict(w=(0, 1.0, 0), v2_vec=(0, 0, 0, 1, 0))))]
    with open(os.path.join(HERE, 'f02_v2_sensitivity.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['case', 'p50', 'p5', 'p95', 'p_lt10', 'p_lt9_4', 'p_ge12', 'guide_median_musd'])
        for name, kw in sens:
            g, guide, _, _ = final(**kw); s = summ(g)
            w.writerow([name, round(s['p50'], 2), round(s['p5'], 2), round(s['p95'], 2), round(s['p_lt10'], 3), round(s['p_lt9_4'], 3), round(s['p_ge12'], 3), round(float(np.median(guide)), 0)])
            print(f"{name:80s} p50 {s['p50']:6.2f}  p5 {s['p5']:6.2f} p95 {s['p95']:6.2f}  P<10 {s['p_lt10']:.3f} P<9.4 {s['p_lt9_4']:.3f} P>=12 {s['p_ge12']:.3f}")
