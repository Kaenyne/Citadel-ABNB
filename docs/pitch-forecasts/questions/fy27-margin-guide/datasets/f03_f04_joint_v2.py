"""F03 + F04 revision 2 (audit A08 response): ONE joint simulation.
F03: FY27 adjusted EBITDA margin guidance bucket at the Feb 2027 print.  F04: P(FY27 S&M ex-SBC / revenue >= 21.9%), FY27 10-K.
Changes vs f03_model.py / f04_model.py (rev 1, left untouched):
  * LITERAL convention (A08-01): only a numeric floor/point/range resolves (a)-(c)/(d)-numeric; qualitative flat/expand sentences and
    'no sentence' resolve (e); explicit down / investment-year framing resolves (d) (option text). Rev-1 mapped qualitative flat to the FY26 bucket.
  * FY26 print A from the C04 rev-2 internal FY26 distribution (mean 35.72, sd 0.58) with C04's own floor-defence rule
    (below 35.5: with p 0.50 a Q4 cost cut restores 35.5 + ~0.1), instead of rev-1's N(35.85,0.55)/85% defence.
  * A latent reinvestment-intensity z ~ N(0,1) drives BOTH the F03 sentence regime (tilts T1/T5 up, T4 down) AND FY27 S&M growth
    (g = 14.5 + 3.0 z + ...), so the F04 conditionals aggregate to the unconditional by construction (A08-06).
  * B12 (literal and material readings) computed from the same draws so F03/B12 are one object.
numpy only. Seed 20260917. Run: python f03_f04_joint_v2.py
Writes f03_v2_summary.csv, f03_v2_sensitivity.csv (here) and f04_v2_summary.csv, f04_v2_conditionals.csv, f04_v2_sensitivity.csv
(in ../../fy27-sm-share-above-219/datasets/)."""
import numpy as np, csv, os
HERE = os.path.dirname(os.path.abspath(__file__)); N = 400_000
F04DIR = os.path.normpath(os.path.join(HERE, '..', '..', 'fy27-sm-share-above-219', 'datasets'))
BASE_W = dict(T1=0.185, T2=0.215, T3=0.345, T4=0.065, T5=0.095, T6=0.075)   # pre-tilt weights, tuned so the REALISED marginals are T1 .20 / T2 .20 / T3 .33 / T4 .08 / T5 .12 / T6 .07
TILT = dict(T1=0.5, T2=0.0, T3=-0.2, T4=-0.7, T5=0.8, T6=0.0)           # log-odds tilt per 1 sd of z


def bucket(level):
    return np.where(level >= 36.5, 'a', np.where(level >= 36.0, 'b', np.where(level >= 35.5, 'c', 'd')))


def run(seed=20260917, A_mu=35.72, A_sd=0.58, p_cut=0.50, w=None, tilt=None, h1=(0.5, 2.0), h2=(0.0, 0.25), legacy_qual_map=False,
        R_mu=15829., R_sd=450., R_short_w=0.25, R_short_mu=15100., R_short_sd=500., S26_mu=3040., S26_sd=60.,
        g_mu=14.5, g_z=3.0, g_sd=4.5, beta=0.30, thr=0.219, z_short=0.0, s26_a=40.0, h_z=0.4):
    w = dict(BASE_W if w is None else w); tilt = dict(TILT if tilt is None else tilt)
    rng = np.random.default_rng(seed)
    # --- FY26 print (C04 rev 2 internal + floor defence) ---
    zA = rng.standard_normal(N); A = A_mu + A_sd * zA                     # zA: FY26 print surprise (also lowers the FY26 S&M base below)
    cut = (A < 35.5) & (rng.random(N) < p_cut)
    A = np.where(cut, 35.5 + 0.1 + np.abs(rng.normal(0, 0.1, N)), A)
    A_r = np.round(A, 1)
    # --- latent reinvestment intensity ---
    z = rng.standard_normal(N)
    keys = list(w.keys()); lw = np.log(np.array([w[k] for k in keys]))[None, :] + z[:, None] * np.array([tilt[k] for k in keys])[None, :]
    P = np.exp(lw - lw.max(axis=1, keepdims=True)); P /= P.sum(axis=1, keepdims=True)
    T = (rng.random(N)[:, None] > np.cumsum(P, axis=1)).sum(axis=1)
    # --- sentence -> level -> option ---
    hc = np.clip(0.5 * (h1[0] + h1[1]) + h_z * z + rng.uniform(-0.5 * (h1[1] - h1[0]), 0.5 * (h1[1] - h1[0]), N), 0.25, 3.0)
    f1 = np.floor((A - hc) / 0.5) * 0.5                                    # T1 haircut floor (Feb 2024/2025 form); haircut grows with z
    f2 = np.floor((A - rng.uniform(h2[0], h2[1], N)) / 0.5) * 0.5           # T2 floor at the print rounded down (Nov 2025 'at least 35.5' form)
    lvl = np.where(T == 0, f1, np.where(T == 1, f2, np.nan))
    opt = bucket(np.nan_to_num(lvl, nan=99.0))
    opt = np.where(T == 2, 'e', opt); opt = np.where(T == 3, 'e', opt)      # literal: qualitative flat / expand -> (e)
    opt = np.where(T == 4, 'd', opt); opt = np.where(T == 5, 'e', opt)      # explicit down / investment year -> (d); none -> (e)
    if legacy_qual_map:                                                      # rev-1 convention, for reference only
        opt = np.where(T == 2, bucket(A_r), opt); opt = np.where(T == 3, bucket(A_r + 0.5), opt)
    floor_ = np.where(T <= 1, lvl, np.nan)
    b12_lit = (T == 4) | ((T <= 1) & (floor_ < A_r))
    b12_mat = (T == 4) | ((T <= 1) & (floor_ <= A_r - 0.5))
    # --- F04: FY27 S&M share ---
    sh = rng.random(N) < np.clip(R_short_w + z_short * z, 0, 1)
    R = np.where(sh, R_short_mu + R_short_sd * rng.standard_normal(N), R_mu + R_sd * rng.standard_normal(N))
    rg = (R / 14268. - 1) * 100
    S26 = S26_mu - s26_a * zA + S26_sd * rng.standard_normal(N)             # a higher FY26 print came with a lower 2H26 S&M base
    g = g_mu + g_z * z + beta * (rg - 10.94) + g_sd * rng.standard_normal(N)
    ratio = S26 * (1 + g / 100) / R
    f04 = ratio >= thr
    vec = {o: float((opt == o).mean()) for o in 'abcde'}
    cond = {o: float(f04[opt == o].mean()) for o in 'abcde'}
    return dict(vec=vec, p_f04=float(f04.mean()), cond=cond, A=A, T=T, opt=opt, keys=keys, ratio=ratio, g=g, z=z, f04=f04,
                b12_lit=float(b12_lit.mean()), b12_mat=float(b12_mat.mean()), reg_w={k: float((T == i).mean()) for i, k in enumerate(keys)})


def street_anchor(seed=7, rev=15819.3392, ebitda=5766.0, disp=154.22275, realise=175.0, other=6807.3146, other_sd=200.0, da=82.5359, thr=0.219):
    """F04 anchor (A08-04/05): Street-implied FY27 S&M = revenue - EBITDA + D&A - other cash lines, with an explicit uncertainty model:
    EBITDA ~ N(5,766, sqrt(disp^2 + realise^2)) [analyst dispersion + a one-year-ahead realisation error, judgment $175M ~3%],
    other lines ~ N(6,807, 200) [team line-build assumptions]. Returns P(share >= 21.9%) and the dispersion-only illustration."""
    rng = np.random.default_rng(seed); n = 400_000
    e = ebitda + np.sqrt(disp ** 2 + realise ** 2) * rng.standard_normal(n); o = other + other_sd * rng.standard_normal(n)
    sm = rev - e + da - o; share = sm / rev
    e2 = ebitda + disp * rng.standard_normal(n); share2 = (rev - e2 + da - other) / rev
    return dict(point_share=100 * (rev - ebitda + da - other) / rev, p_anchor=float((share >= thr).mean()), p_dispersion_only=float((share2 >= thr).mean()),
                share_sd_pp=float(100 * share.std()))


if __name__ == '__main__':
    an = street_anchor(); print('F04 Street-residual anchor:', {k: round(v, 4) for k, v in an.items()})
    r = run(); A = r['A']; vec = r['vec']
    fy26 = dict(mean=A.mean(), sd=A.std(), p_lt_35_5=(A < 35.5).mean(), p_35_5_35_9=((A >= 35.5) & (A < 36)).mean(),
                p_36_0_36_4=((A >= 36) & (A < 36.5)).mean(), p_ge_36_5=(A >= 36.5).mean())
    print('FY26 print:', {k: round(float(v), 4) for k, v in fy26.items()})
    print('regime weights realised:', {k: round(v, 3) for k, v in r['reg_w'].items()})
    print('F03 vector (literal):', {k: round(v, 4) for k, v in vec.items()})
    print('F04 unconditional %.4f ; conditionals %s ; check sum(w*c) = %.4f' % (r['p_f04'], {k: round(v, 3) for k, v in r['cond'].items()}, sum(vec[o] * r['cond'][o] for o in 'abcde')))
    print('B12 literal %.4f material %.4f' % (r['b12_lit'], r['b12_mat']))
    for i, k in enumerate(r['keys']):
        sel = r['T'] == i; print(k, 'w %.3f' % sel.mean(), {o: round(float((r['opt'][sel] == o).mean()), 3) for o in 'abcde'}, 'P(F04|T) %.3f' % r['f04'][sel].mean())
    pct = np.percentile(r['ratio'] * 100, [5, 10, 25, 50, 75, 90, 95]); print('F04 ratio pct', np.round(pct, 2))
    leg = run(legacy_qual_map=True); print('F03 under the rev-1 mapping convention (reference):', {k: round(v, 3) for k, v in leg['vec'].items()})
    with open(os.path.join(HERE, 'f03_v2_summary.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['item', 'value'])
        for k, v in fy26.items(): w.writerow(['fy26_print_' + k, round(float(v), 4)])
        for k, v in r['reg_w'].items(): w.writerow(['regime_weight_' + k, round(v, 4)])
        for o in 'abcde': w.writerow(['p_' + o, round(vec[o], 4)])
        for o in 'abcde': w.writerow(['p_' + o + '_rev1_mapping_reference', round(leg['vec'][o], 4)])
        w.writerow(['b12_literal', round(r['b12_lit'], 4)]); w.writerow(['b12_material', round(r['b12_mat'], 4)])
    os.makedirs(F04DIR, exist_ok=True)
    with open(os.path.join(F04DIR, 'f04_v2_summary.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['stat', 'value']); w.writerow(['p_ge_21.9', round(r['p_f04'], 4)])
        for p_, v in zip([5, 10, 25, 50, 75, 90, 95], pct): w.writerow(['ratio_p%d' % p_, round(float(v), 2)])
        w.writerow(['g_mean', round(float(r['g'].mean()), 3)]); w.writerow(['g_sd', round(float(r['g'].std()), 3)])
        for k, v in an.items(): w.writerow(['anchor_' + k, round(v, 4)])
    with open(os.path.join(F04DIR, 'f04_v2_conditionals.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['f03_option', 'p_f03', 'p_f04_given_f03'])
        for o in 'abcde': w.writerow([o, round(vec[o], 4), round(r['cond'][o], 4)])
        w.writerow(['sum_w_x_c', 1.0, round(sum(vec[o] * r['cond'][o] for o in 'abcde'), 4)])
    sens3 = [('base', {}),
             ('rev-1 FY26 print N(35.85,0.55) with 85% defence proxy (A_mu 35.85, sd 0.55, p_cut 0.85)', dict(A_mu=35.85, A_sd=0.55, p_cut=0.85)),
             ('FY26 print centred 35.6', dict(A_mu=35.6)), ('FY26 print centred 36.1', dict(A_mu=36.1)), ('FY26 print centred 36.4', dict(A_mu=36.4)),
             ('no floor defence (p_cut 0)', dict(p_cut=0.0)), ('floor always defended (p_cut 1)', dict(p_cut=1.0)),
             ('numeric dominant (T1 0.30, T2 0.25, T3 0.20, T4 0.05, T5 0.12, T6 0.08)', dict(w=dict(T1=0.30, T2=0.25, T3=0.20, T4=0.05, T5=0.12, T6=0.08))),
             ('qualitative dominant (T1 0.12, T2 0.12, T3 0.45, T4 0.10, T5 0.10, T6 0.11)', dict(w=dict(T1=0.12, T2=0.12, T3=0.45, T4=0.10, T5=0.10, T6=0.11))),
             ('investment-year 0.25 (T5)', dict(w=dict(T1=0.20, T2=0.16, T3=0.25, T4=0.05, T5=0.25, T6=0.09))),
             ('expand 0.20 (T4, bull)', dict(w=dict(T1=0.15, T2=0.20, T3=0.25, T4=0.20, T5=0.10, T6=0.10))),
             ('haircut 1.0-2.0 only (rev-1 T1)', dict(h1=(1.0, 2.0))), ('no z tilt on regimes', dict(tilt=dict(T1=0, T2=0, T3=0, T4=0, T5=0, T6=0))),
             ('rev-1 mapping convention (qualitative flat -> FY26 bucket), reference only', dict(legacy_qual_map=True))]
    with open(os.path.join(HERE, 'f03_v2_sensitivity.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['case', 'a', 'b', 'c', 'd', 'e', 'b12_literal', 'b12_material', 'p_f04'])
        for name, kw in sens3:
            rr = run(**kw); w.writerow([name] + [round(rr['vec'][o], 4) for o in 'abcde'] + [round(rr['b12_lit'], 4), round(rr['b12_mat'], 4), round(rr['p_f04'], 4)])
            print('%-95s' % name, {o: round(rr['vec'][o], 3) for o in 'abcde'}, 'B12 %.3f/%.3f' % (rr['b12_lit'], rr['b12_mat']), 'F04 %.3f' % rr['p_f04'])
    sens4 = [('base', {}), ('no short-revenue tail', dict(R_short_w=0)), ('short-revenue tail 0.5', dict(R_short_w=0.5)),
             ('S&M growth centred 22% (run allocation 23.5%)', dict(g_mu=22.0)), ('S&M growth centred 10% (cost bull)', dict(g_mu=10.0)),
             ('S&M growth centred 20% (cost bear)', dict(g_mu=20.0)), ('S&M growth centred 12%', dict(g_mu=12.0)), ('S&M growth centred 17%', dict(g_mu=17.0)),
             ('total growth sd ~3 (g_z 1.5, g_sd 2.6)', dict(g_z=1.5, g_sd=2.6)), ('total growth sd ~8 (g_z 4, g_sd 7)', dict(g_z=4.0, g_sd=7.0)),
             ('beta 0 (no flex)', dict(beta=0.0)), ('beta 0.6 (strong flex)', dict(beta=0.6)),
             ('FY26 S&M 3,100 (2H26 +30%)', dict(S26_mu=3100.)), ('FY26 S&M 2,980 (2H26 +20%)', dict(S26_mu=2980.)),
             ('z also raises the short-revenue tail (z_short 0.08)', dict(z_short=0.08)), ('no z link to S&M (g_z 0, g_sd 5.4)', dict(g_z=0.0, g_sd=5.4)),
             ('FY27 revenue base 15,500 (RNPL-aware +8.6%)', dict(R_mu=15500.)), ('FY27 revenue base 16,100 (bull)', dict(R_mu=16100.))]
    with open(os.path.join(F04DIR, 'f04_v2_sensitivity.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['case', 'p_ge_21.9', 'ratio_p50', 'cond_a', 'cond_b', 'cond_c', 'cond_d', 'cond_e'])
        for name, kw in sens4:
            rr = run(**kw); w.writerow([name, round(rr['p_f04'], 4), round(float(np.median(rr['ratio']) * 100), 2)] + [round(rr['cond'][o], 3) for o in 'abcde'])
            print('%-60s P %.4f  median ratio %.2f  cond %s' % (name, rr['p_f04'], np.median(rr['ratio']) * 100, {o: round(rr['cond'][o], 3) for o in 'abcde'}))
