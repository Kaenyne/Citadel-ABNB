"""F01: P(1Q27 nights descriptor in the Feb 2027 letter implies >= +8.2% y/y on 156.2m, i.e. >= 169.0m).
Tree: 4Q26 print n4 -> management's internal 1Q27 expectation m = n4 + delta -> format (bucket / directional / none)
-> language -> resolution under the question's convention ("high single digits" alone = No; "low double digits" = Yes;
"high single to low double digits" / "approximately 9%" = Yes; "similar to Q4" = Yes iff the 4Q26 print >= 8.2%).
numpy only. Seed 20260917. Run: python f01_model.py (writes f01_summary.csv, f01_sensitivity.csv)."""
import numpy as np, csv, os
HERE = os.path.dirname(os.path.abspath(__file__)); N = 400_000


def run(seed=20260917, n4_mu=8.1, n4_sd=1.6, short_w=0.12, short_mu=5.5, short_sd=1.5,
        d_mu=-0.4, d_sd=1.2, p_bucket=0.72, p_dir=0.24, k_mu=1.0, k_sd=0.9,
        yes_mid=0.45, yes_low=0.10, yes_vlow=0.02, stable_band=0.75, up_floor=7.5):
    rng = np.random.default_rng(seed)
    n4 = n4_mu + n4_sd * rng.standard_normal(N)
    short = rng.random(N) < short_w
    n4 = np.where(short, short_mu + short_sd * rng.standard_normal(N), n4)
    m = n4 + d_mu + d_sd * rng.standard_normal(N)            # management's internal 1Q27 expectation
    u = rng.random(N)
    fmt = np.where(u < p_bucket, 0, np.where(u < p_bucket + p_dir, 1, 2))   # 0 bucket, 1 directional, 2 none
    d = m - (k_mu + k_sd * rng.standard_normal(N))            # bucket midpoint stated (expectation less cushion)
    r = rng.random(N)
    yes_bucket = np.where(d >= 9.5, 1.0, np.where(d >= 8.5, yes_mid, np.where(d >= 7.5, yes_low, yes_vlow)))
    bucket_yes = r < yes_bucket
    # directional: 'stable / similar to Q4' if |m - n4| < band -> Yes iff n4 >= 8.2 ;
    # 'moderate / lower than Q4' if m < n4 - band -> No ; 'higher than Q4' if m > n4 + band -> Yes iff n4 >= up_floor
    dir_yes = np.where(np.abs(m - n4) < stable_band, n4 >= 8.2, np.where(m > n4 + stable_band, n4 >= up_floor, False))
    yes = np.where(fmt == 0, bucket_yes, np.where(fmt == 1, dir_yes, False))
    return dict(p=float(yes.mean()), n4=n4, m=m, d=d, fmt=fmt, yes=yes)


if __name__ == '__main__':
    r = run(); n4 = r['n4']; m = r['m']; yes = r['yes']
    print('P(yes) = %.3f ; n4 mean %.2f sd %.2f ; m mean %.2f ; P(m>=8.2) %.3f ; P(n4>=8.2) %.3f'
          % (r['p'], n4.mean(), n4.std(), m.mean(), (m >= 8.2).mean(), (n4 >= 8.2).mean()))
    rows = []
    for lo, hi in [(-99, 7.5), (7.5, 8.5), (8.5, 9.5), (9.5, 99)]:
        sel = (n4 >= lo) & (n4 < hi)
        rows.append(('4Q26 print in [%s,%s)' % (lo, hi), float(sel.mean()), float(yes[sel].mean()))); print(rows[-1])
    for f_, name in [(0, 'bucket'), (1, 'directional'), (2, 'none')]:
        sel = r['fmt'] == f_
        rows.append(('format ' + name, float(sel.mean()), float(yes[sel].mean()))); print(rows[-1])
    with open(os.path.join(HERE, 'f01_summary.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['slice', 'weight', 'p_yes']); w.writerow(['all', 1.0, round(r['p'], 4)])
        for a, b, c in rows: w.writerow([a, round(b, 4), round(c, 4)])
    sens = [('base', {}), ('4Q26 centred 7.6 (RNPL module)', dict(n4_mu=7.6)),
            ('4Q26 centred 9.9 (Street), no short tail', dict(n4_mu=9.9, short_w=0)),
            ('4Q26 short case 5.0 certain', dict(n4_mu=5.0, n4_sd=1.2, short_w=0)), ('no short tail', dict(short_w=0)),
            ('delta +0.1 (WS06 v2: 8.21 vs 8.12)', dict(d_mu=0.1)), ('delta -1.1 (RNPL module 6.47 vs 7.61)', dict(d_mu=-1.1)),
            ('delta -2.5 (PR32 global lap)', dict(d_mu=-2.5)),
            ('bucket cushion 0 (guide at expectation)', dict(k_mu=0.0)), ('bucket cushion 2.0 (3Q25/4Q25 style)', dict(k_mu=2.0)),
            ('directional-only share 0.45', dict(p_bucket=0.51, p_dir=0.45)), ('bucket share 0.90', dict(p_bucket=0.90, p_dir=0.07)),
            ('8.5-9.5 midpoint resolves Yes 0.25', dict(yes_mid=0.25)), ('8.5-9.5 midpoint resolves Yes 0.65', dict(yes_mid=0.65)),
            ('joint bull: n4 9.9, delta +0.1, cushion 0.5', dict(n4_mu=9.9, short_w=0, d_mu=0.1, k_mu=0.5)),
            ('joint bear: n4 6.5, delta -1.1, cushion 2.0', dict(n4_mu=6.5, d_mu=-1.1, k_mu=2.0))]
    with open(os.path.join(HERE, 'f01_sensitivity.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['case', 'p_yes'])
        for name, kw in sens:
            p = run(**kw)['p']; w.writerow([name, round(p, 3)]); print('%-50s %.3f' % (name, p))
