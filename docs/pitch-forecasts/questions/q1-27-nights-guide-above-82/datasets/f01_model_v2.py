"""F01 revision 2 (audit A08 response): P(1Q27 nights descriptor in the Feb 2027 letter implies >= +8.2% y/y on 156.2m).
Changes vs f01_model.py (rev 1, left untouched):
  * 4Q26 print drawn from the ADOPTED 4Q26 object (R16/B13 blend: 0.5 decomposition V1 + 0.3 guide route V2 + 0.2 Street V3),
    not the rev-1 N(8.1,1.6)+12% tail.
  * 'higher than Q4' resolves Yes only if the Q4 print itself is >= 8.2 (A08-02); rev-1 used 7.5.
  * 'nearly as strong as Q4' (4Q22 form) modelled explicitly: Yes iff Q4 print >= near_floor (9.2, a stated convention; sensitivity 8.7 / never).
numpy only. Seed 20260917. Run: python f01_model_v2.py (writes f01_v2_summary.csv, f01_v2_sensitivity.csv, q4_adopted_v2_summary.csv)."""
import numpy as np, csv, os
HERE = os.path.dirname(os.path.abspath(__file__)); N = 400_000
BASE = 121.9


def q4_adopted(rng, n=N, w=(0.5, 0.3, 0.2), v1_mu=8.1, v1_beta=0.5, v1_sd=1.4, tail_w=0.12, tail_mu=5.5, tail_sd=1.5,
               q3_mu=9.67, q3_sd=1.70, v2_vec=(0.21, 0.19, 0.39, 0.17, 0.04), v2_mids=(10.75, 9.75, 8.0, 6.0), v2_c_mu=0.9, v2_c_sd=1.3,
               v3_mu=9.926, v3_sd=1.23, legacy=False):
    """Adopted 4Q26 nights growth (pts) with the 3Q26 print alongside. Mirrors r16_model.py / b13_model.py:
    V1: q3 ~ N(9.67,1.70); q4 = 8.1 + 0.5(q3-9.67) + N(0,1.4); 12% short tail 5.5 +/- 1.5.
    V2: C02 bucket vector x midpoint + cushion N(0.9,1.3) (R16 'V2 used' sits between its 0.6 and 1.2 cushion rows); 'none' -> V1.
    V3: Street bar N(9.926, 1.23) (MODL 134.0m +/- 1.5m).  legacy=True reproduces the rev-1 F01 print mixture."""
    q3 = q3_mu + q3_sd * rng.standard_normal(n)
    if legacy:
        q4 = 8.1 + 1.6 * rng.standard_normal(n); sh = rng.random(n) < 0.12
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
    # q3 for V2/V3 draws: keep the 0.5 pass-through structure by re-drawing q3 conditional on q4 (corr ~0.45)
    q3_alt = q3_mu + 0.45 * (q3_sd / 1.9) * (q4 - 8.7) + q3_sd * np.sqrt(1 - 0.45 ** 2) * rng.standard_normal(n)
    q3 = np.where(u < w[0], q3, q3_alt)
    return q4, q3


def run(seed=20260917, d_mu=-0.4, d_sd=1.2, p_bucket=0.72, p_dir=0.24, k_mu=1.0, k_sd=0.9,
        yes_mid=0.45, yes_low=0.10, yes_vlow=0.02, stable_band=0.75, up_floor=8.2, near_floor=9.2, p_near=0.35,
        q4_kw=None, legacy=False):
    rng = np.random.default_rng(seed)
    n4, _ = q4_adopted(rng, legacy=legacy, **(q4_kw or {}))
    n4 = np.round(BASE * (1 + n4 / 100), 1) / BASE * 100 - 100          # printed to 0.1m
    m = n4 + d_mu + d_sd * rng.standard_normal(N)                        # management's internal 1Q27 expectation
    u = rng.random(N)
    fmt = np.where(u < p_bucket, 0, np.where(u < p_bucket + p_dir, 1, 2))
    d = m - (k_mu + k_sd * rng.standard_normal(N))                       # stated bucket midpoint
    r = rng.random(N)
    yes_bucket = np.where(d >= 9.5, 1.0, np.where(d >= 8.5, yes_mid, np.where(d >= 7.5, yes_low, yes_vlow)))
    bucket_yes = r < yes_bucket
    near = (rng.random(N) < p_near) & (m < n4)                            # 'nearly as strong' wording inside the stable band
    similar_yes = np.where(near, n4 >= near_floor, n4 >= 8.2)
    dir_yes = np.where(np.abs(m - n4) < stable_band, similar_yes, np.where(m > n4 + stable_band, n4 >= up_floor, False))
    yes = np.where(fmt == 0, bucket_yes, np.where(fmt == 1, dir_yes, False))
    return dict(p=float(yes.mean()), n4=n4, m=m, d=d, fmt=fmt, yes=yes)


if __name__ == '__main__':
    rng = np.random.default_rng(1)
    q4, q3 = q4_adopted(rng); nights = np.round(BASE * (1 + q4 / 100), 1)
    stats = dict(mean=q4.mean(), sd=q4.std(), median=np.median(q4), p_ge_134=(nights >= 134.0).mean(), p_le_131=(nights <= 131.0).mean(),
                 p_ge_8_2=(q4 >= 8.2).mean(), p_lt_7_5=(q4 < 7.5).mean(), p_7_5_8_5=((q4 >= 7.5) & (q4 < 8.5)).mean(),
                 p_8_5_9_5=((q4 >= 8.5) & (q4 < 9.5)).mean(), p_ge_9_5=(q4 >= 9.5).mean(), q3_mean=q3.mean(), corr_q3_q4=np.corrcoef(q3, q4)[0, 1])
    q4l, _ = q4_adopted(rng, legacy=True); stats.update(legacy_mean=q4l.mean(), legacy_p_ge_134=(np.round(BASE * (1 + q4l / 100), 1) >= 134.0).mean())
    print('ADOPTED 4Q26 object:', {k: round(float(v), 4) for k, v in stats.items()})
    with open(os.path.join(HERE, 'q4_adopted_v2_summary.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['stat', 'value']); [w.writerow([k, round(float(v), 4)]) for k, v in stats.items()]
    r = run(); n4 = r['n4']; m = r['m']; yes = r['yes']
    print('P(yes) = %.4f ; n4 mean %.2f ; P(m>=8.2) %.3f ; P(n4>=8.2) %.3f' % (r['p'], n4.mean(), (m >= 8.2).mean(), (n4 >= 8.2).mean()))
    rows = []
    for lo, hi in [(-99, 7.5), (7.5, 8.5), (8.5, 9.5), (9.5, 99)]:
        sel = (n4 >= lo) & (n4 < hi); rows.append(('4Q26 print in [%s,%s)' % (lo, hi), float(sel.mean()), float(yes[sel].mean()))); print(rows[-1])
    for f_, name in [(0, 'bucket'), (1, 'directional'), (2, 'none')]:
        sel = r['fmt'] == f_; rows.append(('format ' + name, float(sel.mean()), float(yes[sel].mean()))); print(rows[-1])
    with open(os.path.join(HERE, 'f01_v2_summary.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['slice', 'weight', 'p_yes']); w.writerow(['all', 1.0, round(r['p'], 4)])
        for a, b, c in rows: w.writerow([a, round(b, 4), round(c, 4)])
    sens = [('base (adopted 4Q26 object, up_floor 8.2, near_floor 9.2)', {}),
            ('rev-1 print mixture N(8.1,1.6)+12% tail (legacy)', dict(legacy=True)),
            ('rev-1 print mixture AND up_floor 7.5 (rev-1 resolver)', dict(legacy=True, up_floor=7.5, p_near=0.0)),
            ('up_floor 7.5 (rev-1 resolver) on the adopted object', dict(up_floor=7.5)),
            ("'nearly as strong' never Yes", dict(near_floor=99.0)), ("'nearly as strong' Yes iff Q4 >= 8.7", dict(near_floor=8.7)),
            ('4Q26 V1 centre 7.61 (RNPL module)', dict(q4_kw=dict(v1_mu=7.61))), ('4Q26 V1 centre 8.9 (case A NA-only lap)', dict(q4_kw=dict(v1_mu=8.9))),
            ('4Q26 = Street bar 9.93 certain-centred, no tail (V1 only)', dict(q4_kw=dict(w=(1.0, 0, 0), v1_mu=9.93, tail_w=0.0))),
            ('4Q26 decomposition only (V1, weights 1/0/0)', dict(q4_kw=dict(w=(1.0, 0, 0)))),
            ('4Q26 weights 0.34/0.33/0.33', dict(q4_kw=dict(w=(0.34, 0.33, 0.33)))),
            ('delta +0.1 (WS06 v2)', dict(d_mu=0.1)), ('delta -1.1 (RNPL module)', dict(d_mu=-1.1)), ('delta -2.5 (PR32 global lap)', dict(d_mu=-2.5)),
            ('bucket cushion 0 (guide at expectation)', dict(k_mu=0.0)), ('bucket cushion 2.0 (3Q25/4Q25 style)', dict(k_mu=2.0)),
            ('directional-only share 0.45', dict(p_bucket=0.51, p_dir=0.45)), ('bucket share 0.90', dict(p_bucket=0.90, p_dir=0.07)),
            ('8.5-9.5 midpoint resolves Yes 0.25', dict(yes_mid=0.25)), ('8.5-9.5 midpoint resolves Yes 0.65', dict(yes_mid=0.65)),
            ('joint bull: Street-centred V1 9.9 no tail, delta +0.1, cushion 0.5', dict(q4_kw=dict(v1_mu=9.9, tail_w=0.0), d_mu=0.1, k_mu=0.5)),
            ('joint bear: V1 6.5, delta -1.1, cushion 2.0', dict(q4_kw=dict(v1_mu=6.5), d_mu=-1.1, k_mu=2.0)),
            ('5 Nov bucket low double digits (V2 mid 10.75 certain)', dict(q4_kw=dict(w=(0, 1.0, 0), v2_vec=(1, 0, 0, 0, 0)))),
            ('5 Nov bucket around 10 (V2 mid 9.75 certain)', dict(q4_kw=dict(w=(0, 1.0, 0), v2_vec=(0, 1, 0, 0, 0)))),
            ('5 Nov bucket high single digits (V2 mid 8.0 certain)', dict(q4_kw=dict(w=(0, 1.0, 0), v2_vec=(0, 0, 1, 0, 0)))),
            ('5 Nov bucket mid single / moderate (V2 mid 6.0 certain)', dict(q4_kw=dict(w=(0, 1.0, 0), v2_vec=(0, 0, 0, 1, 0))))]
    with open(os.path.join(HERE, 'f01_v2_sensitivity.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['case', 'p_yes'])
        for name, kw in sens:
            p = run(**kw)['p']; w.writerow([name, round(p, 4)]); print('%-70s %.4f' % (name, p))
