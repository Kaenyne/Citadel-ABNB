"""F04: P(FY27 sales & marketing ex-SBC / FY27 revenue >= 21.9%), FY27 10-K basis.
FY27 revenue R (WS06 v2 base with a short-case tail) ; FY26 S&M ex-SBC S26 ; FY27 S&M growth g with partial flex to revenue.
numpy only. Seed 20260917. Run: python f04_model.py (writes f04_summary.csv, f04_sensitivity.csv)."""
import numpy as np, csv, os
HERE = os.path.dirname(os.path.abspath(__file__)); N = 400_000


def run(seed=20260917, R_mu=15829., R_sd=450., R_short_w=0.25, R_short_mu=15100., R_short_sd=500.,
        S26_mu=3040., S26_sd=60., g_mu=14.5, g_sd=5.5, beta=0.30, g_shift=0.0, thr=0.219):
    rng = np.random.default_rng(seed)
    R = R_mu + R_sd * rng.standard_normal(N); sh = rng.random(N) < R_short_w
    R = np.where(sh, R_short_mu + R_short_sd * rng.standard_normal(N), R)
    rg = (R / 14268. - 1) * 100
    S26 = S26_mu + S26_sd * rng.standard_normal(N)
    g = g_mu + g_shift + beta * (rg - 10.94) + g_sd * rng.standard_normal(N)
    S27 = S26 * (1 + g / 100); ratio = S27 / R
    return dict(p=float((ratio >= thr).mean()), ratio=ratio, R=R, g=g, S27=S27)


if __name__ == '__main__':
    r = run(); ratio = r['ratio']
    pct = np.percentile(ratio * 100, [5, 10, 25, 50, 75, 90, 95])
    print('P(>=21.9) = %.3f ; ratio pct 5/10/25/50/75/90/95 = %s ; S27 median %.0f ; R median %.0f ; g mean %.2f'
          % (r['p'], np.round(pct, 2), np.median(r['S27']), np.median(r['R']), r['g'].mean()))
    with open(os.path.join(HERE, 'f04_summary.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['stat', 'value']); w.writerow(['p_ge_21.9', round(r['p'], 4)])
        for p_, v in zip([5, 10, 25, 50, 75, 90, 95], pct): w.writerow(['ratio_p%d' % p_, round(float(v), 2)])
        w.writerow(['sm27_median_musd', round(float(np.median(r['S27'])), 0)])
        w.writerow(['rev27_median_musd', round(float(np.median(r['R'])), 0)])
    cond = [('F03 (a) >=36.5 guide', dict(g_shift=-4.5, R_short_w=0.10)), ('F03 (b) 36.0-36.4', dict(g_shift=-2.0, R_short_w=0.15)),
            ('F03 (c) 35.5-35.9', dict(g_shift=0.0)), ('F03 (d) <35.5 / down / investment year', dict(g_shift=3.5, R_short_w=0.35)),
            ('F03 (e) no numeric guide', dict(g_shift=0.5, R_short_w=0.30))]
    sens = [('base', {}), ('no short-revenue tail', dict(R_short_w=0)), ('short-revenue tail 0.5', dict(R_short_w=0.5)),
            ('S&M growth centred 22% (run allocation 23.5%)', dict(g_mu=22.0)), ('S&M growth centred 10% (cost bull)', dict(g_mu=10.0)),
            ('S&M growth centred 20% (cost bear)', dict(g_mu=20.0)), ('S&M growth sd 3', dict(g_sd=3.0)), ('S&M growth sd 8', dict(g_sd=8.0)),
            ('beta 0 (no flex)', dict(beta=0.0)), ('beta 0.6 (strong flex)', dict(beta=0.6)),
            ('FY26 S&M 3,100 (2H26 +30%)', dict(S26_mu=3100.)), ('FY26 S&M 2,980 (2H26 +20%)', dict(S26_mu=2980.))]
    with open(os.path.join(HERE, 'f04_sensitivity.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['case', 'p_ge_21.9', 'ratio_p50'])
        for name, kw in sens + cond:
            rr = run(**kw); w.writerow([name, round(rr['p'], 3), round(float(np.median(rr['ratio']) * 100), 2)])
            print('%-50s P %.3f  median ratio %.2f' % (name, rr['p'], np.median(rr['ratio']) * 100))
