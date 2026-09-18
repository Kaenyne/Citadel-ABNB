"""A17 audit reproduction - B11, B12, B13. stdlib + pandas only; writes nothing.
Run from the repository root:  python -B docs/pitch-forecasts/audits/A17-reproduce.py
None of the three forecast models is executed (all write into their own datasets/ folders); each is
re-implemented here from source. The Monte Carlos use random.Random at 120,000 draws rather than numpy
at 400,000-1,000,000, so they reproduce the seeded numpy figures to about +/-0.005; every block prints
the file's own numbers underneath for comparison. Runtime ~3 minutes."""
from pathlib import Path
from statistics import mean, stdev
import math
import random
import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
N = 120_000


def hdr(s):
    print("\n" + "=" * 10 + " " + s + " " + "=" * 10)


def pct(v, q):
    s = sorted(v)
    k = (len(s) - 1) * q
    lo = int(k)
    return s[lo] if lo + 1 >= len(s) else s[lo] + (k - lo) * (s[lo + 1] - s[lo])


# ------------------------------------------------------------------ B11 tape facts
hdr("B11  the downgrade feed and every base rate in claims 2-4")
feed = pd.read_csv(Q / "bonus-sellside-downgrades/datasets/feed_downgrades_all.csv", parse_dates=["date"])
raw = pd.read_csv(Q / "bonus-sellside-downgrades/sources/yfinance_upgrades_downgrades_20260917T082155Z.csv")
print("feed pull rows %d, action mix %s" % (len(raw), raw.Action.value_counts().to_dict()))
print("down rows %d, all to Hold/Sell %s, by year %s"
      % (len(feed), bool(feed.to_hold_or_sell.all()), feed.date.dt.year.value_counts().sort_index().to_dict()))
print("last downgrade %s -> %d days to 2026-09-16; largest earlier gap %d days"
      % (feed.date.max().date(), (pd.Timestamp("2026-09-16") - feed.date.max()).days, feed.date.diff().dt.days.max()))
print("same-calendar 17 Sep - 15 Dec: %s"
      % {y: int(((feed.date >= pd.Timestamp(y, 9, 17)) & (feed.date <= pd.Timestamp(y, 12, 15))).sum())
         for y in range(2021, 2026)})
for start, lab in [("2021-01-01", "2021+"), ("2023-01-01", "2023+"), ("2024-01-01", "2024+")]:
    starts = pd.date_range(pd.Timestamp(start), pd.Timestamp("2026-09-16") - pd.Timedelta(days=90))
    c = [int(((feed.date >= t) & (feed.date < t + pd.Timedelta(days=90))).sum()) for t in starts]
    print("  90-day windows %-6s n %4d  mean %.4f  P(>=3) %.4f  P(>=2) %.4f  max %d"
          % (lab, len(c), mean(c), sum(x >= 3 for x in c) / len(c), sum(x >= 2 for x in c) / len(c), max(c)))
rx = pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv", parse_dates=["reaction_date"])
ns = [int(((feed.date >= d - pd.Timedelta(days=49)) & (feed.date <= d + pd.Timedelta(days=39))).sum())
      for d in rx.reaction_date]
n23 = [n for n, d in zip(ns, rx.reaction_date) if d >= pd.Timestamp("2023-01-01")]
print("  print-shaped (-49/+39d) counts %s" % ns)
print("  all n %d mean %.4f P(>=3) %.4f | 2023+ n %d mean %.3f P(>=3) %.4f"
      % (len(ns), mean(ns), sum(x >= 3 for x in ns) / len(ns), len(n23), mean(n23), sum(x >= 3 for x in n23) / len(n23)))
sgn = {"up>=5": [], "small": [], "down<=-5": []}
for n, r in zip(ns, rx.abnb_1d_pct):
    sgn["up>=5" if r >= 5 else ("down<=-5" if r <= -5 else "small")].append(n)
print("  by day-1 sign: %s" % {k: "n %d mean %.3f P(>=3) %.3f" % (len(v), mean(v), sum(x >= 3 for x in v) / len(v))
                               for k, v in sgn.items()})
print("  NOTE: both >=3 windows (Feb 2022, Nov 2023) followed SMALL day-1 moves (+3.6, -3.3);")
print("        0 of 6 windows around a day-1 <= -5pct print ever reached 3 - the model's mechanism has no positive case")


# ------------------------------------------------------------------ B11 model
def b11(seed=20260917, n=N, weights=(.24, .14, .10, .52), d1=(4., -1., -2.5, -6.), d1sd=7.5,
        post_drift=(-2., -1., -1., -2.5), spre=35, spost=27, bg=.29, drift=.03, spot=167.51,
        pre_mu=.35, k_pre=3.0, post_mu=(.15, .5, .7, 1.1), beta=.06, k_post=3.0,
        od=1.6, capture=.85, pool=1.0):
    g = random.Random(seed)
    dt = 1 / 252
    cum, acc = [], 0.
    for w in weights:
        acc += w
        cum.append(acc)
    f = 21 / spre

    def nb(m):
        lam = m if od <= 1.0 else g.gammavariate(m / (od - 1.0), od - 1.0)
        k, term, cdf, u = 0, math.exp(-lam), math.exp(-lam), g.random()
        while u > cdf and k < 60:
            k += 1
            term *= lam / k
            cdf += term
        return k

    cnt, dec, yes = [], [], []
    for _ in range(n):
        u = g.random()
        z = next(i for i, c in enumerate(cum) if u <= c)
        rpre = (drift - .5 * bg * bg) * spre * dt + bg * math.sqrt(spre * dt) * g.gauss(0, 1)
        day1 = d1[z] / 100 + d1sd / 100 * g.gauss(0, 1)
        rpost = (math.log1p(post_drift[z] / 100) + (drift - .5 * bg * bg) * spost * dt
                 + bg * math.sqrt(spost * dt) * g.gauss(0, 1))
        p1 = f * rpre + math.sqrt(f * (1 - f)) * bg * math.sqrt(spre * dt) * g.gauss(0, 1)
        m_pre = pre_mu * pool * math.exp(-k_pre * min(p1, 0.0))
        m_post = post_mu[z] * pool * math.exp(-beta * (day1 * 100 - d1[z])) * math.exp(-k_post * min(rpost, 0.0))
        c = nb(m_pre) + nb(m_post)
        if capture < 1.0:
            c = sum(1 for _ in range(c) if g.random() < capture)
        cnt.append(c)
        dec.append(spot * math.exp(rpre + math.log1p(day1) + rpost))
        yes.append(c >= 3)
    return dict(p=sum(yes) / n, mean=mean(cnt), p_ge2=sum(c >= 2 for c in cnt) / n,
                E_dec_yes=mean(d for d, y in zip(dec, yes) if y), E_dec=mean(dec))


_m2 = .32 * 4 + .10 * -1 + .13 * -2.5 + .45 * -6
_between = (.32 * (4. - _m2) ** 2 + .10 * (-1. - _m2) ** 2 + .13 * (-2.5 - _m2) ** 2 + .45 * (-6. - _m2) ** 2)
S02R2 = dict(weights=(.32, .10, .13, .45), post_drift=(-1.5, -.5, -.5, -1.), spre=36, spost=26,
             bg=.30, drift=.0697, d1sd=math.sqrt(9.5 ** 2 - _between))
hdr("B11  published model, the revision-2 parameter swap, and the two corrections")
print("  S02 revision-2 within-branch day-1 sd from the variance identity: %.3f (S02 v2 solves 8.451)" % S02R2["d1sd"])
for name, kw in [("published (S02 revision 1, capture 0.85)", {}),
                 ("no modulation at all (k_pre = k_post = beta = 0)", dict(k_pre=0., k_post=0., beta=0.)),
                 ("S02 revision-2 parameters", S02R2),
                 ("rev2 + capture 1.0 (base rates are ALREADY feed counts)", dict(S02R2, capture=1.0)),
                 ("rev2 + feed print-window post means .02/.55/.55/.83", dict(S02R2, post_mu=(.02, .55, .55, .83))),
                 ("rev2 + capture 1.0 + feed post means", dict(S02R2, capture=1.0, post_mu=(.02, .55, .55, .83))),
                 ("rev2 + pre 0.26 (2023+ OFF-print 49-day rate)", dict(S02R2, pre_mu=.26)),
                 ("rev2 + capture 1.0 + pre 0.26 + feed post means",
                  dict(S02R2, capture=1.0, pre_mu=.26, post_mu=(.02, .55, .55, .83)))]:
    r = b11(**kw)
    print("  %-52s P %.4f  mean %.3f (= %.2f/yr)  E[Dec|Yes] %.1f vs %.1f"
          % (name, r["p"], r["mean"], r["mean"] * 365 / 89, r["E_dec_yes"], r["E_dec"]))
print("  the file's numpy run (b11_summary.json): P 0.15393 mean 1.169 E[Dec|Yes] 148.05 vs 161.11")
print("  measured rates: 3.51/yr (2021+), 3.51 (2023+), 2.59 (2024+), 0 trailing 12m;")
print("  print-shaped-window mean 0.74 per 89 days = 3.03/yr")


# ------------------------------------------------------------------ B12
hdr("B12  the five February letters and the literal / material record")
fs = pd.read_csv(Q / "bonus-fy27-investment-year/datasets/feb_fy_margin_sentences.csv")
for _, r in fs.iterrows():
    print("  %s %s  prior %.2f  floor_vs_prior %+d bp  literal %s material %s  [%s]"
          % (r.letter, r.letter_date, r.prior_fy_actual_pct, int(r.floor_vs_prior_bp),
             r.b12_literal, r.b12_material, r.form))
print("  literal 2 of 5 = %.3f (Laplace %.3f); a numeric floor given at all 2 of 5; explicit 'down' 0 of 5 (Laplace %.3f)"
      % (2 / 5, 3 / 7, 1 / 7))
print("  NOTE the 4Q20 (Feb 2021) letter also carries a forward FY margin sentence - 'focused on ... expanding our")
print("  Adjusted EBITDA margin as we scale' - so the reference class can be read as 2 of 6 = %.3f" % (2 / 6))


def b12(seed=20260917, n=N, A_mu=35.85, A_sd=.55, p_defend=.85, miss=(35.4, .4),
        w=(("T1", .20), ("T2", .22), ("T3", .30), ("T4", .08), ("T5", .10), ("T6", .10)),
        h1=(1.0, 2.0), h2=(0.0, .25), material=.5):
    g = random.Random(seed)
    keys = [k for k, _ in w]
    tot = sum(p for _, p in w)
    cum, acc = [], 0.
    for _, p in w:
        acc += p / tot
        cum.append(acc)
    lit = mat = t2flat = 0
    gaps = []
    for _ in range(n):
        A = A_mu + A_sd * g.gauss(0, 1)
        A = max(A, 35.5 + abs(g.gauss(0, .12))) if g.random() < p_defend else miss[0] + miss[1] * g.gauss(0, 1)
        A_r = round(A, 1)
        u = g.random()
        T = keys[next(i for i, c in enumerate(cum) if u <= c)]
        if T == "T1":
            lvl = math.floor((A - g.uniform(*h1)) / .5) * .5
        elif T == "T2":
            lvl = math.floor((A - g.uniform(*h2)) / .5) * .5
        else:
            lvl = None
        yl = (T == "T5") or (lvl is not None and A_r - lvl > 1e-9)
        ym = (T == "T5") or (lvl is not None and A_r - lvl >= material - 1e-9)
        lit += yl
        mat += ym
        t2flat += (T in ("T5", "T1"))
        if yl and lvl is not None:
            gaps.append(A_r - lvl)
    return dict(literal=lit / n, material=mat / n, t2_as_flat=t2flat / n, gap_mean=mean(gaps),
                gap_p50=pct(gaps, .5), gap_p90=pct(gaps, .9), share_lt_50bp=sum(x < .5 for x in gaps) / lit)


hdr("B12  published model, and what the T5 and T2 regimes are doing")
r = b12()
print("  published rebuild: literal %.4f material %.4f T2-as-flat %.4f gap mean %.2f p50 %.2f p90 %.2f share<50bp %.2f"
      % (r["literal"], r["material"], r["t2_as_flat"], r["gap_mean"], r["gap_p50"], r["gap_p90"], r["share_lt_50bp"]))
print("  the file's numpy run: literal 0.517 material 0.388 t2-as-flat 0.299 gap mean 1.04 p50 0.7 p90 2.1 share 0.25")
for name, kw in [("F03 rev-2 FY26 print N(35.72,0.58), 50pct defence",
                  dict(A_mu=35.72, A_sd=.58, p_defend=.50, miss=(35.72, .58))),
                 ("F03 rev-2 realised regime weights (T1 .20 T2 .20 T3 .33 T4 .08 T5 .12 T6 .07)",
                  dict(w=(("T1", .20), ("T2", .20), ("T3", .33), ("T4", .08), ("T5", .12), ("T6", .07)))),
                 ("T5 as a LANGUAGE OVERLAY on T1, not a separate regime (T5 0.02)",
                  dict(w=(("T1", .20), ("T2", .22), ("T3", .38), ("T4", .08), ("T5", .02), ("T6", .10)))),
                 ("T2 halved to 0.11 (no February letter has ever used that form)",
                  dict(w=(("T1", .20), ("T2", .11), ("T3", .41), ("T4", .08), ("T5", .10), ("T6", .10)))),
                 ("T2 = 0", dict(w=(("T1", .20), ("T2", .0), ("T3", .52), ("T4", .08), ("T5", .10), ("T6", .10))))]:
    v = b12(**kw)
    print("  %-62s literal %.4f  material %.4f" % (name, v["literal"], v["material"]))
print("  the whole literal-vs-material wedge is T2: at T2 = 0 the two readings coincide.")
print("  F03 revision 2's own joint model (f03_f04_joint_v2.py, A08 response) publishes literal 0.5086 / material 0.3748.")


# ------------------------------------------------------------------ B13
hdr("B13  the published blend, its mean, and the ADOPTED 4Q26 object")
BASE, LO, HI = 121.9, 131.0, 134.0
thr_lo, thr_hi = (LO / BASE - 1) * 100, (HI / BASE - 1) * 100
print("  thresholds: <=131.0m = %.4f pct y/y ; >=134.0m = %.4f pct y/y" % (thr_lo, thr_hi))


def mixture(seed=20260917, n=N, q3_mu=9.67, q3_sd=1.70, q3_ref=9.67, q4_mu=8.1, beta=.5, res_sd=1.4,
            tail_w=.12, vec=(.21, .19, .39, .17, .04), cushion=(1.2, 1.3), street_sd=1.23,
            w=(.5, .3, .2)):
    g = random.Random(seed)
    mids = (10.75, 9.75, 8.0, 6.0, None)
    cv, acc = [], 0.
    for p in vec:
        acc += p
        cv.append(acc)
    wv, acc = [], 0.
    for p in w:
        acc += p
        wv.append(acc)
    q3s, q4s, v1s, v2s, v3s = [], [], [], [], []
    for _ in range(n):
        q3 = g.gauss(q3_mu, q3_sd)
        v1 = (5.5 + beta * (q3 - q3_ref) + g.gauss(0, 1.5)) if g.random() < tail_w \
            else (q4_mu + beta * (q3 - q3_ref) + g.gauss(0, res_sd))
        u = g.random()
        b = next(i for i, c in enumerate(cv) if u <= c)
        v2 = v1 if mids[b] is None else mids[b] + g.gauss(*cushion)
        v3 = g.gauss(thr_hi, street_sd)
        u = g.random()
        k = next(i for i, c in enumerate(wv) if u <= c)
        q3s.append(q3)
        v1s.append(v1)
        v2s.append(v2)
        v3s.append(v3)
        q4s.append((v1, v2, v3)[k])

    def st_(x):
        nights = [round(BASE * (1 + v / 100), 1) for v in x]
        return (sum(v <= LO for v in nights) / len(x), sum(v >= HI for v in nights) / len(x), mean(x))
    lo_, hi_, m_ = st_(q4s)
    nights = [round(BASE * (1 + v / 100), 1) for v in q4s]
    le = [(a, b) for a, b, c in zip(q4s, q3s, nights) if c <= LO]
    return dict(p_le_131=lo_, p_ge_134=hi_, mean=m_, sd=stdev(q4s),
                V1=st_(v1s), V2=st_(v2s), V3=st_(v3s),
                E_q4_le=mean(a for a, b in le), E_q3_le=mean(b for a, b in le), E_q3=mean(q3s))


r1 = mixture()
print("  revision-1 parameters (the published B13): V1 %.4f  V2 %.4f  V3 %.4f  ->  blend P(<=131.0m) %.4f"
      % (r1["V1"][0], r1["V2"][0], r1["V3"][0], r1["p_le_131"]))
print("    file: V1 0.4211  V2 0.1558  V3 0.0245  blend 0.2622 -> published 0.26")
print("    BLEND MEAN %.3f, sd %.3f  <-- the log's sections 3 and 5 assert 'mean ~ 8.3'" % (r1["mean"], r1["sd"]))
print("    blend P(>=134.0m) %.4f -> middle mass %.4f, not the log's 0.47"
      % (r1["p_ge_134"], 1 - r1["p_le_131"] - r1["p_ge_134"]))
ADOPT = dict(q3_mu=9.5, q3_ref=9.5, res_sd=2.0, vec=(.18, .17, .30, .31, .04), cushion=(1.0, 1.3))
r2 = mixture(**ADOPT)
print("  ADOPTED object (adopted_q4_states_v2.json, R16 rev 2): V1 %.4f  V2 %.4f  V3 %.4f  -> P(<=131.0m) %.4f"
      % (r2["V1"][0], r2["V2"][0], r2["V3"][0], r2["p_le_131"]))
print("    file: V1 0.4514  V2 0.2585  V3 0.0248  blend 0.3089  mean 8.6122  sd 2.2782")
print("    my rebuild mean %.3f sd %.3f ; E[Q4|Yes] %.3f (file 5.925) ; E[Q3|Yes] %.3f (file 9.091) ; E[Q3] %.3f"
      % (r2["mean"], r2["sd"], r2["E_q4_le"], r2["E_q3_le"], r2["E_q3"]))
for name, kw in [("cushion 1.5", dict(cushion=(1.5, 1.3))), ("cushion 2.0", dict(cushion=(2.0, 1.3))),
                 ("Q4 centre 7.61 (RNPL module)", dict(q4_mu=7.61)), ("Q4 centre 8.9 (case A)", dict(q4_mu=8.9)),
                 ("blend 0.4/0.4/0.2", dict(w=(.4, .4, .2))), ("equal thirds", dict(w=(1 / 3, 1 / 3, 1 / 3)))]:
    kk = dict(ADOPT)
    kk.update(kw)
    print("    %-32s P(<=131.0m) %.4f" % (name, mixture(**kk)["p_le_131"]))

hdr("B13  the section-9 impact arithmetic on the adopted object")
dq4 = r2["E_q4_le"] - 8.1
dq3 = r2["E_q3_le"] - 9.5
print("  4Q26 nights  %+.2f pt   (log: -2.0)" % dq4)
print("  3Q26 nights  %+.2f pt   (log: -0.9, measured against 9.9 rather than R01 revision 2's 9.5)" % dq3)
print("  4Q26 revenue %+.0f M    (log: -60)   [1pt = $30M]" % (dq4 * 30))
print("  FY27 revenue %+.0f M    (log: -220)  [70pct persistence x $158M/pt]" % (.7 * dq4 * 158))
print("  FY27 margin  %+.2f pp   (log: -0.92) [0.66pp per pt, HELD costs]" % (.66 * .7 * dq4))
print("  FY27 EPS held-cost %+.3f  flex-cost %+.3f   (log: -0.20, from $220M x 0.66 x $0.0014)"
      % (.7 * dq4 * 158 * .0014, .7 * dq4 * 158 * .78 * .0014))
print("  the log books the HELD margin coefficient (0.66pp/pt) and a 66pct dollar flow-through in the same table;")
print("  held costs = 100pct flow-through; the brief's flex case solves to 78pct. Either way the EPS line is understated.")
print("  stock, joint solve %+.2f  (log: -6.9 on 1.4pt); the -$3 February reaction is that same repricing, not an addition"
      % (.7 * dq4 * 4.90))
