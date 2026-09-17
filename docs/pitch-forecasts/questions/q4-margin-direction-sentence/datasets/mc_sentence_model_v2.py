"""Revision-2 decomposition Monte Carlo for C04 (FY26 margin sentence) and C09 (4Q26 margin direction sentence).
Response to audit A03 (docs/pitch-forecasts/audits/A03-research-audit.md). numpy + scipy.special.erf only. Run from this folder:
    py -3.13 mc_sentence_model_v2.py
Changes vs mc_sentence_model.py (revision 1), each tagged with the finding id:
  A03-05  one final joint: every judgment (hold-and-cut, wording) is applied per draw INSIDE the MC, so the published
          C04 and C09 vectors, the C04xC09 joint and the conditionals on C01 all come from the same draws.
  A03-04  rounding tolerance and required cushion are separate objects: management says 'approximately X' when its
          internal FY margin >= X + c_req, c_req ~ N(0.10, 0.15) (judgment; realised November cushions +0.77/+0.90/+0.10
          are the only observable and do not identify the internal forecast). A minority 'thin-cushion' branch keeps the
          revision-1 optimistic threshold (internal >= 35.85) at weight P_THIN.
  A03-09  hold-and-cut is a cost intervention: when the internal FY is below the 35.5 floor, with prob P_CUT management
          cuts 4Q26 spend (capped at the line build's $177M ~ 5.9pp of Q4 margin) to restore the floor + 0.1, and the
          C09 sentence is generated from the post-cut Q4 margin.
  C01 rev 2  the 4Q26 guide midpoint is drawn from C01's revision-2 mixture histogram (mean 3,101, sd 97; P(<3,161) 0.746)
          instead of N(3,090, 80); the 3Q26 revenue draw is correlated with it (rho 0.5, common GBV shock; 'missed' item).
  A03-08  Q3 margin, Q4 internal margin centre, wording bias and flat band are labelled judgments with sensitivities.
  A03-03/A03-01  (e) no FY sentence 0.05 (3/4 Novembers with a pre-existing FY outlook; 2/2 numeric); (d) no Q4 sentence
          0.05 (20/21 prints; 5/5 Novembers; 9/9 since 2Q24).
"""
import numpy as np, json, csv, os
from scipy.special import erf
SEED = 20260917; N = 400_000
HERE = os.path.dirname(os.path.abspath(__file__))
H1_REV = 6286.0; H1_EBITDA = 1780.0          # 2Q26 letter (05_nov2026_scenarios.csv)
LY = 28.29; F = 35.5; STREET_Q4_REV = 3161.02  # 4Q25 margin; Aug floor; LSEG-family 4Q26 mean (C01 rev 2, 2026-09-17T02:52Z)
CUT_CAP_PP = 5.9                              # 40_short_case_summary: $176.7M cut = 29.55 - 23.59 = 5.96pp of Q4 margin


def load_hist():
    """C01 revision-2 mixture histogram (q4-revenue-guide-vs-street/datasets/c01_v2_final_mixture_hist.csv)."""
    p = os.path.join(HERE, '..', '..', 'q4-revenue-guide-vs-street', 'datasets', 'c01_v2_final_mixture_hist.csv')
    rows = list(csv.DictReader(open(p, encoding='utf-8')))
    lo = np.array([float(r['bin_lo']) for r in rows]); hi = np.array([float(r['bin_hi']) for r in rows])
    m = np.array([float(r['mass']) for r in rows])
    return lo, hi, m / m.sum()


LO, HI, MASS = load_hist(); CDF = np.cumsum(MASS)


def guide_from_u(u):
    idx = np.clip(np.searchsorted(CDF, u), 0, len(LO) - 1)
    prev = np.where(idx > 0, CDF[np.maximum(idx - 1, 0)], 0.0)
    frac = (u - prev) / MASS[idx]
    return LO[idx] + np.clip(frac, 0, 1) * (HI[idx] - LO[idx])


def simulate(q4c=29.0, q3c=49.95, q3sd=1.0, q4sd=1.4, c_req_mu=0.10, c_req_sd=0.15, p_thin=0.50, p_cut=0.50,
             bias_mu=0.3, bias_sd=0.4, band_mu=0.7, band_sd=0.25, p_e=0.05, p_d9=0.05, rho=0.5, guide_shift=0.0,
             hold_vs_soft_mid=0.50, hold_vs_soft_high=0.45, b_round_high=0.20, seed=SEED):
    r = np.random.default_rng(seed)
    z1 = r.standard_normal(N); z2 = r.standard_normal(N)
    u = 0.5 * (1 + erf(z1 / np.sqrt(2)))
    q4_guide = guide_from_u(np.clip(u, 1e-9, 1 - 1e-9)) + guide_shift
    # 3Q26 revenue: bridge v3 4,804 / Street 4,744 / guide 4,690-4,770; sd 80 = C01 print sd; R01 centre 9.67 nights ~ +$8M (immaterial)
    q3_rev = 4790 + 80 * (rho * z1 + np.sqrt(1 - rho ** 2) * z2)
    q3_margin = r.normal(q3c, q3sd, N)               # JUDGMENT (A03-08): team card 49.94; ceiling 50.085 ('down slightly'); line build 50.4
    cush = r.normal(0.025, 0.010, N); q4_rev_int = q4_guide * (1 + cush)
    q4_margin_int = q4c + 0.5 * (q4_rev_int - 3190) / 31.9 + r.normal(0, q4sd, N)   # JUDGMENT: 29.0 = mean of the four team-quoted Q4 views (line build 28.3, Street ratio 28.9, combination 29.04, M3 path 29.9)
    q3_ebitda = q3_margin / 100 * q3_rev
    fy_int = (H1_EBITDA + q3_ebitda + q4_margin_int / 100 * q4_rev_int) / (H1_REV + q3_rev + q4_rev_int) * 100
    # ---- C04 sentence (A03-04): strict rule = round (internal - c_req) down to the 50bp grid; thin-cushion branch = rev-1 threshold 35.85
    c_req = r.normal(c_req_mu, c_req_sd, N)
    lvl = np.floor((fy_int - c_req) / 0.5) * 0.5
    thin = r.random(N) < p_thin
    res = np.full(N, 'x', dtype='<U1')
    res = np.where(~thin & (lvl >= 36.5), 'c', res)
    res = np.where(~thin & (lvl == 36.0), 'b', res)
    res = np.where(thin & (fy_int >= 36.9), 'c', res)
    res = np.where(thin & (fy_int >= 35.85) & (fy_int < 36.9), 'b', res)
    x = res == 'x'
    uu = r.random(N)
    # x & internal >= 35.75: hold the floor / rounded-up 'approximately 36%' or a 35.5-36 range (b) / 'approximately 35.5%' (d)
    hi_band = x & (fy_int >= 35.75)
    res = np.where(hi_band & (uu < hold_vs_soft_high), 'a', res)
    res = np.where(hi_band & (uu >= hold_vs_soft_high) & (uu < hold_vs_soft_high + b_round_high), 'b', res)
    res = np.where(hi_band & (uu >= hold_vs_soft_high + b_round_high), 'd', res)
    # x & 35.5 <= internal < 35.75: hold 'at least 35.5%' vs 'approximately 35.5%'
    mid_band = x & (fy_int >= F) & (fy_int < 35.75)
    res = np.where(mid_band & (uu < hold_vs_soft_mid), 'a', np.where(mid_band, 'd', res))
    # x & internal < 35.5 (floor at risk): A03-09 cost intervention before either sentence
    risk = x & (fy_int < F)
    cut = risk & (r.random(N) < p_cut)
    need_pp = np.clip(4.49 * (F + 0.10 - fy_int), 0, CUT_CAP_PP)   # 1pp of FY = 4.49pp of Q4 (23_card_budget_identity)
    q4_margin_post = np.where(cut, q4_margin_int + need_pp, q4_margin_int)
    fy_post = np.where(cut, (H1_EBITDA + q3_ebitda + q4_margin_post / 100 * q4_rev_int) / (H1_REV + q3_rev + q4_rev_int) * 100, fy_int)
    res = np.where(cut, 'a', res)
    nocut = risk & ~cut
    res = np.where(nocut & (uu < 0.85), 'd', np.where(nocut, 'a', res))
    res = np.where(r.random(N) < p_e, 'e', res)      # (e) no FY sentence, exogenous
    # ---- C09 from the post-cut Q4 margin (A03-09); stated = internal - bias; flat band (A03-08 judgments)
    bias = r.normal(bias_mu, bias_sd, N); band = r.normal(band_mu, band_sd, N)
    stated = q4_margin_post - bias - LY
    c09 = np.where(stated > band, 'c', np.where(stated < -band, 'a', 'b'))
    c09 = np.where(r.random(N) < p_d9, 'd', c09)
    return dict(res=res, c09=c09, fy_int=fy_int, fy_post=fy_post, q4_guide=q4_guide, q4_margin_int=q4_margin_int,
                q4_margin_post=q4_margin_post, cut=cut, q3_margin=q3_margin)


L4 = list('abcde'); L9 = list('abcd')


def vec(a, labels):
    return {k: round(float((a == k).mean()), 4) for k in labels}


def summarise(S):
    res, c09 = S['res'], S['c09']
    out = {'c04': vec(res, L4), 'c09': vec(c09, L9)}
    below = S['q4_guide'] < STREET_Q4_REV
    out['p_guide_below_street'] = round(float(below.mean()), 4)
    out['c04_given_below'] = vec(res[below], L4); out['c04_given_not_below'] = vec(res[~below], L4)
    out['c09_given_below'] = vec(c09[below], L9); out['c09_given_not_below'] = vec(c09[~below], L9)
    out['c09_given_c04'] = {k: vec(c09[res == k], L9) for k in L4}
    out['c04_given_c09'] = {k: vec(res[c09 == k], L4) for k in L9}
    out['joint_C04xC09'] = {a + b: round(float(((res == a) & (c09 == b)).mean()), 6) for a in L4 for b in L9}
    return out


if __name__ == '__main__':
    S = simulate(); base = summarise(S)
    fy = S['fy_int']; q4 = S['q4_margin_int']
    print('C01 rev-2 guide draw: mean %.1f sd %.1f P(<3161) %.3f' % (S['q4_guide'].mean(), S['q4_guide'].std(), base['p_guide_below_street']))
    print('internal FY26 (pre-cut): mean %.3f sd %.3f p10 %.2f p50 %.2f p90 %.2f' % (fy.mean(), fy.std(), *np.percentile(fy, [10, 50, 90])))
    for th in [35.5, 35.75, 35.85, 36.0, 36.1, 36.25, 36.5, 36.7, 36.9]:
        print('  P(internal >= %.2f) = %.4f' % (th, (fy >= th).mean()))
    print('internal 4Q26 margin (pre-cut): mean %.2f sd %.2f P(>LY) %.3f P(<27.7) %.3f; cut branch %.4f of draws, mean cut %.2fpp'
          % (q4.mean(), q4.std(), (q4 > LY).mean(), (q4 < 27.7).mean(), S['cut'].mean(), (S['q4_margin_post'] - q4)[S['cut']].mean()))
    print('C04 final vector', base['c04']); print('C09 final vector', base['c09'])
    print('C04 | guide below Street', base['c04_given_below'], ' | not below', base['c04_given_not_below'])
    print('C09 | guide below Street', base['c09_given_below'], ' | not below', base['c09_given_not_below'])
    print('C09 | C04', base['c09_given_c04']); print('C04 | C09', base['c04_given_c09'])
    sens = {}
    grid = {'q4_internal_28.3(line build)': dict(q4c=28.3), 'q4_internal_28.8(Aug floor arithmetic)': dict(q4c=28.8), 'q4_internal_29.3(rev-1 centre)': dict(q4c=29.3),
            'q4_internal_30.0(M3 path)': dict(q4c=30.0), 'q4_internal_30.9(M3 modal)': dict(q4c=30.9),
            'q3_49.4(slightly=0.7, below ceiling)': dict(q3c=49.4), 'q3_50.4(line build)': dict(q3c=50.4),
            'q3_52.4(evidence build)': dict(q3c=52.4), 'q3_sd_1.6(card 80% band)': dict(q3sd=1.6),
            'c_req_0.0': dict(c_req_mu=0.0), 'c_req_0.25': dict(c_req_mu=0.25), 'p_thin_0.0(strict only)': dict(p_thin=0.0), 'p_thin_0.35': dict(p_thin=0.35),
            'p_thin_0.65(rev-1 weight)': dict(p_thin=0.65), 'p_cut_0.0': dict(p_cut=0.0), 'p_cut_1.0': dict(p_cut=1.0),
            'guide_-97(C01 -1sd)': dict(guide_shift=-97), 'guide_+97(C01 +1sd)': dict(guide_shift=97),
            'guide_at_Street(+60)': dict(guide_shift=60), 'guide_3059(bridge implied)': dict(guide_shift=-42),
            'rho_0': dict(rho=0.0), 'bias_0.0': dict(bias_mu=0.0), 'bias_0.7': dict(bias_mu=0.7), 'band_0.4': dict(band_mu=0.4),
            'band_1.0': dict(band_mu=1.0), 'q4sd_1.0': dict(q4sd=1.0), 'q4sd_2.0': dict(q4sd=2.0),
            'hold_vs_soft_high_0.65': dict(hold_vs_soft_high=0.65, b_round_high=0.20), 'b_round_high_0.0': dict(b_round_high=0.0),
            'p_e_0.03': dict(p_e=0.03)}
    for k, kw in grid.items():
        s = summarise(simulate(**kw)); sens[k] = {'c04': s['c04'], 'c09': s['c09']}
        print(k, 'C04', s['c04'], 'C09', s['c09'])
    json.dump({'base': base, 'sensitivities': sens,
               'internal_fy26': {'mean': float(fy.mean()), 'sd': float(fy.std()), 'p10': float(np.percentile(fy, 10)),
                                 'p50': float(np.percentile(fy, 50)), 'p90': float(np.percentile(fy, 90)),
                                 'p_ge': {str(t): float((fy >= t).mean()) for t in [35.5, 35.75, 35.85, 36.0, 36.1, 36.25, 36.5, 36.7, 36.9]}},
               'internal_4q26': {'mean': float(q4.mean()), 'sd': float(q4.std()), 'p_gt_ly': float((q4 > LY).mean()), 'p_lt_27.7': float((q4 < 27.7).mean())},
               'params': dict(q4c=29.0, q3c=49.95, q3sd=1.0, q4sd=1.4, c_req='N(0.10,0.15)', p_thin=0.50, p_cut=0.50, bias='N(0.3,0.4)',
                              band='N(0.7,0.25)', p_e=0.05, p_d9=0.05, rho=0.5, hold_vs_soft_mid=0.5, hold_vs_soft_high=0.45,
                              b_round_high=0.20, cut_cap_pp=CUT_CAP_PP),
               'N': N, 'seed': SEED}, open(os.path.join(HERE, 'mc_sentence_results_v2.json'), 'w'), indent=1)
    json.dump({k: base[k] for k in ['joint_C04xC09', 'c04_given_below', 'c04_given_not_below', 'c09_given_below',
                                    'c09_given_not_below', 'c09_given_c04', 'c04_given_c09', 'p_guide_below_street']},
              open(os.path.join(HERE, 'mc_joint_and_conditionals_v2.json'), 'w'), indent=1)
