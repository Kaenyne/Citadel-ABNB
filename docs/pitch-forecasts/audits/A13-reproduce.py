"""A13 audit reproduction - R12, R13, R14. stdlib + pandas only; writes nothing."""
from pathlib import Path
from statistics import NormalDist, mean, stdev
import json
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


# ------------------------------------------------------------------ R14 (A)
hdr("R14  day-1 record and the S1 Q4 residual")
rx = pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv")
rx["lbl"] = rx.quarter.map(lambda q: q[5] + "Q" + q[2:4])
ACC = {"3Q22", "3Q23", "4Q24", "3Q25", "4Q25", "2Q26"}
DEC = {"4Q22", "1Q23", "2Q23", "4Q23", "1Q24", "2Q24", "1Q25", "2Q25", "1Q26"}
FLT = {"3Q24"}
rx["sign"] = rx.lbl.map(lambda s: 1 if s in ACC else (-1 if s in DEC else (0 if s in FLT else None)))
rx["resid"] = rx.excess_1d_pct - (-0.67 + 3.35 * rx["sign"].astype(float))
q4 = rx[rx.quarter.str.endswith("Q4")]
print("Q4 day-1 raw:", dict(zip(q4.quarter, q4.abnb_1d_pct)))
print("Q4: positive %d/6, >=5%% %d/6, >=3.5%% %d/6, mean %.3f, median %.2f"
      % ((q4.abnb_1d_pct > 0).sum(), (q4.abnb_1d_pct >= 5).sum(),
         (q4.abnb_1d_pct >= 3.5).sum(), q4.abnb_1d_pct.mean(), q4.abnb_1d_pct.median()))
for lo, name in [("2020Q4", "all 23"), ("2022Q3", "3Q22+ (16)"), ("2023Q1", "post-2022 (14)")]:
    s = rx[rx.quarter >= lo]
    print("  %-16s n %2d  >=+5%% %d  rate %.3f  Laplace %.3f"
          % (name, len(s), (s.abnb_1d_pct >= 5).sum(), (s.abnb_1d_pct >= 5).mean(),
             ((s.abnb_1d_pct >= 5).sum() + 1) / (len(s) + 2)))
print("  log/JSON claim post-2022 '3 of 14 (0.21)' -> the file gives",
      int((rx[rx.quarter >= "2023Q1"].abnb_1d_pct >= 5).sum()), "of 14")
r16 = rx[rx["sign"].notna()]
a = r16[r16.lbl.str.startswith("4Q")]
b = r16[~r16.lbl.str.startswith("4Q")]
print("S1 residual: Q4 mean %.3f (sd %.3f, n %d), non-Q4 %.3f, gap %.3f, Welch t %.3f"
      % (a.resid.mean(), a.resid.std(), len(a), b.resid.mean(),
         a.resid.mean() - b.resid.mean(),
         (a.resid.mean() - b.resid.mean())
         / math.sqrt(a.resid.var() / len(a) + b.resid.var() / len(b))))

hdr("R14  the Q4 uplift is already inside the S01 cells")
CELLS = {"aa": ["3Q25", "4Q25", "2Q26"], "ab": ["3Q22", "3Q23", "4Q24"], "fl": ["3Q24"],
         "da": ["4Q22", "2Q23", "4Q23", "2Q25", "1Q26"],
         "db": ["1Q23", "1Q24", "2Q24", "1Q25"]}
raw = dict(zip(r16.lbl, r16.abnb_1d_pct))
exq4 = {}
dev = []
for k, v in CELLS.items():
    ex = [q for q in v if not q.startswith("4Q")]
    exq4[k] = mean(raw[q] for q in ex)
    print("  cell %-3s full %6.2f (n%d)   ex-Q4 %6.2f (n%d)"
          % (k, mean(raw[q] for q in v), len(v), exq4[k], len(ex)))
    dev += [(q, raw[q] - exq4[k]) for q in v if q.startswith("4Q")]
print("  Q4 deviations from ex-Q4 cell means:", [(q, round(d, 2)) for q, d in dev],
      "-> leave-one-out premium %.2f (the log uses the S1 gap 10.29)" % mean(d for _, d in dev))

hdr("R14  Feb event sd from the Jan / Mar 2027 expiries")
ts = pd.read_csv(Q / "close-15dec-2026/datasets/implied_term_structure_20260917T031221Z.csv")
jan = ts[ts.expiry == "2027-01-15"].iloc[0]
mar = ts[ts.expiry == "2027-03-19"].iloc[0]
vj = (jan.atm_iv / 100) ** 2 * jan["T"]
vm = (mar.atm_iv / 100) ** 2 * mar["T"]
for bg in (29.0, 32.3, 33.85, 36.0):
    print("  background %5.2f%% -> event sd %.3f%%"
          % (bg, 100 * math.sqrt(max(vm - vj - (bg / 100) ** 2 * (mar["T"] - jan["T"]), 0))))
for sd in (8.5, 9.0, 9.5):
    print("  anchor at sd %.1f: P(>=+5%%) %.4f at mode -0.4, %.4f at mean 0"
          % (sd, 1 - NormalDist().cdf((5 + 0.4) / sd), 1 - NormalDist().cdf(5 / sd)))


def r14(seed=7, n=N, n3=(9.55, 1.48), n4=(8.1, 1.6), tw=.12, tail=(5.5, 1.5), corr=.5,
        band=.25, p_guide=.33, cells=None, shrink=.65, uplift=3.0, rsd=8.5, df=5,
        qqq=1.3, unc=-1.0):
    g = random.Random(seed)
    if cells is None:
        cells = dict(aa=7.4, ab=-0.8, fl=-8.7, da=0.8, db=-7.6)
    k = math.sqrt(df / (df - 2))
    out = []
    for _ in range(n):
        z1 = g.gauss(0, 1)
        z2 = corr * z1 + math.sqrt(1 - corr ** 2) * g.gauss(0, 1)
        x3 = n3[0] + n3[1] * z1
        x4 = n4[0] + n4[1] * z2
        if g.random() < tw:
            x4 = tail[0] + tail[1] * g.gauss(0, 1)
        d = x4 - x3
        ge = g.random() < p_guide
        if d >= band:
            m = cells["aa"] if ge else cells["ab"]
        elif d > -band:
            m = cells["fl"]
        else:
            m = cells["da"] if ge else cells["db"]
        mu = unc + shrink * (m - unc) + uplift
        c2 = sum(g.gauss(0, 1) ** 2 for _ in range(df))
        t = g.gauss(0, 1) / math.sqrt(c2 / df)
        out.append(mu + rsd * t / k + qqq * g.gauss(0, 1))
    up = [r for r in out if r >= 5]
    dn = [r for r in out if r <= -5]
    return dict(p_ge5=len(up) / n, p_le_m5=len(dn) / n,
                p_lt0=sum(r < 0 for r in out) / n, mean=mean(out), sd=stdev(out),
                E_up=mean(up), E_dn=mean(dn),
                pctiles={q: round(pct(out, q / 100), 2) for q in (5, 25, 50, 75, 95)})


hdr("R14  published mixture, and the two corrections")
pub = r14()
print("published (full cells, uplift 3.0, p_guide 0.33):",
      json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in pub.items()}))
print("  the file's numpy run: p_ge5 0.2574, mean -0.13, sd 9.09, E[r|>=5] +10.84, E[r|<=-5] -10.66")
print("F02 revision 2 (p_guide 0.45)                   : p_ge5 %.4f" % r14(p_guide=.45)["p_ge5"])
print("ex-Q4 cells + leave-one-out uplift 8.85 x 0.3   : p_ge5 %.4f" % r14(cells=exq4, uplift=2.66)["p_ge5"])
aud = r14(cells=exq4, uplift=2.66, p_guide=.45)
print("both corrections (auditor mixture)              :",
      json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in aud.items()}))
print("  up-tail EV %+.2f pts vs down-tail EV %+.2f pts: they net to the mean (A13-02)"
      % (pub["p_ge5"] * pub["E_up"], pub["p_le_m5"] * pub["E_dn"]))

# ------------------------------------------------------------------ R12
hdr("R12  feed, live targets, D panel")
feed = pd.read_csv(Q / "risk-sellside-upgrades/datasets/feed_upgrades_all.csv")
print("feed 'up' rows since 2021: %d, to Buy-equivalent: %d" % (len(feed), feed.to_buy.sum()))
print("to-Buy by year:", feed[feed.to_buy].date.str[:4].value_counts().sort_index().to_dict())
lt = pd.read_csv(ROOT / "data/processed/reverse_dcf/D/D_live_targets_2026-09-12.csv")
print("live targets n %d  mean %.4f  median %.1f  buckets %s"
      % (len(lt), lt.target.mean(), lt.target.median(), lt.rating_bucket.value_counts().to_dict()))
ms = float(lt.loc[lt.Firm == "Morgan Stanley", "target"].iloc[0])
base_ms = lt.target.mean() + (170 - ms) / len(lt)
print("Morgan Stanley is in the feed at $%.0f -> replacing with $170 gives base %.5f; $190 needs %+.2f%%"
      % (ms, base_ms, 100 * (190 / base_ms - 1)))

p = pd.read_csv(ROOT / "data/processed/reverse_dcf/D/D_target_panel_daily.csv", parse_dates=["date"])
p = p[p.n_targets >= 10].reset_index(drop=True)
prints = set(pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv",
                         parse_dates=["reaction_date"]).reaction_date)
lnT = [math.log(v) for v in p.mean_target]
thr = math.log(190 / 183.22)
print("panel n_targets>=10: %d rows, %s to %s; threshold +%.3f%%"
      % (len(p), p.date.min().date(), p.date.max().date(), 100 * (math.exp(thr) - 1)))
for W in (63, 35):
    ends, maxs, hp, d23 = [], [], [], []
    for i in range(len(p) - W):
        seg = lnT[i:i + W + 1]
        ends.append(seg[-1] - seg[0])
        maxs.append(max(seg) - seg[0])
        hp.append(any(d in prints for d in list(p.date[i:i + W + 1])))
        d23.append(p.date[i] >= pd.Timestamp("2023-01-01"))
    pe = sum(e >= thr for e in ends) / len(ends)
    pm = sum(m >= thr for m in maxs) / len(maxs)
    e2 = [e for e, f in zip(ends, d23) if f]
    m2 = [m for m, f in zip(maxs, d23) if f]
    pe2 = sum(e >= thr for e in e2) / len(e2)
    pm2 = sum(m >= thr for m in m2) / len(m2)
    npw = [e for e, f in zip(ends, hp) if not f]
    wpw = [e for e, f in zip(ends, hp) if f]
    print("  %ds all n %4d P(end) %.4f P(max) %.4f ratio %.3f | 2023+ n %4d %.4f / %.4f ratio %.3f"
          % (W, len(ends), pe, pm, pm / pe, len(e2), pe2, pm2, pm2 / pe2))
    print("      no print in window n %4d P(end) %.4f mean %+.3f%% sd %.3f%% | with print n %4d P(end) %.4f"
          % (len(npw), sum(e >= thr for e in npw) / len(npw), 100 * mean(npw),
             100 * stdev(npw), len(wpw), sum(e >= thr for e in wpw) / len(wpw)))
print("  claim 5 reports the 35s 'with prints inside' as 0.22 / 0.26: those are the ALL-window figures")


def r12(seed=11, n=N, weights=(.24, .14, .10, .52), d1=(4., -1., -2.5, -6.), d1sd=7.5,
        post_drift=(-2., -1., -1., -2.5), spre=35, spost=27, bg=.29, drift=.03,
        rsd=.035, base=183.22, pre_mu=.7, post_mu=(2., 1., .7, .35), beta=.06,
        od=1.6, thrT=190., ratio=1.15, any_day=True, capture=1.0):
    g = random.Random(seed)
    dt = 1 / 252
    kl = (.13 + .10) * (-.068) + .10 * .206 + 3 * .0005
    b0, b1, b2, chase, stale = .075, .13, .10, .40, .005
    cum, acc = [], 0.
    for w in weights:
        acc += w
        cum.append(acc)
    ka = round(spost * 13 / 27)
    kb = spost - ka
    f = 21 / spre

    def nb(m):
        lam = m if od <= 1.0 else g.gammavariate(m / (od - 1.0), od - 1.0)
        k, term, cdf, u = 0, math.exp(-lam), math.exp(-lam), g.random()
        while u > cdf and k < 60:
            k += 1
            term *= lam / k
            cdf += term
        return k

    T, dec, up_leg = [], [], []
    for _ in range(n):
        u = g.random()
        z = next(i for i, c in enumerate(cum) if u <= c)
        rpre = (drift - .5 * bg * bg) * spre * dt + bg * math.sqrt(spre * dt) * g.gauss(0, 1)
        day1 = d1[z] / 100 + d1sd / 100 * g.gauss(0, 1)
        rd1 = math.log1p(day1)
        pdr = math.log1p(post_drift[z] / 100)
        rpa = pdr * (ka / spost) + (drift - .5 * bg * bg) * ka * dt + bg * math.sqrt(ka * dt) * g.gauss(0, 1)
        rpb = pdr * (kb / spost) + (drift - .5 * bg * bg) * kb * dt + bg * math.sqrt(kb * dt) * g.gauss(0, 1)
        p1 = f * rpre + math.sqrt(f * (1 - f)) * bg * math.sqrt(spre * dt) * g.gauss(0, 1)
        p2 = rpre - p1
        ln = (kl + (b0 + b1 + b2) * p1 + (b0 + b1) * p2 + chase * rd1
              + (b0 + .5 * b1) * (rpa + rpb) + stale + rsd * g.gauss(0, 1))
        T.append(base * math.exp(ln))
        dec.append(167.51 * math.exp(rpre + rd1 + rpa + rpb))
        cnt = nb(pre_mu * capture) + nb(post_mu[z] * math.exp(beta * (day1 * 100 - d1[z])) * capture)
        up_leg.append(cnt >= 3)
    pend = sum(t >= thrT for t in T) / n
    lo = pct(T, 1 - min(ratio * pend, .999)) if any_day else thrT
    tleg = [t >= lo for t in T]
    yes = [a or b for a, b in zip(up_leg, tleg)]
    return dict(p=sum(yes) / n, p_up=sum(up_leg) / n, p_T=sum(tleg) / n, p_T_end=pend,
                E_dec_yes=mean(d for d, y in zip(dec, yes) if y), E_dec=mean(dec))


hdr("R12  published parameters vs the revision-2 parameters of S02 and S04")
REV2 = dict(weights=(.32, .10, .13, .45), post_drift=(-1.5, -.5, -.5, -1.),
            spre=36, spost=26, bg=.30, drift=.0697, d1sd=8.451, rsd=.05)
for name, kw in [("published (S02/S04 revision 1)", {}),
                 ("S02 rev2 weights + post drifts", dict(weights=(.32, .10, .13, .45),
                                                         post_drift=(-1.5, -.5, -.5, -1.))),
                 ("S04 rev2 tape residual sd 5.0%", dict(rsd=.05)),
                 ("all revision-2 parameters", REV2),
                 ("revision-2 + B11 feed capture 0.85", dict(REV2, capture=.85)),
                 ("revision-2 + capture + empirical post means",
                  dict(REV2, capture=.85, post_mu=(1.67, .9, .5, .2)))]:
    r = r12(**kw)
    print("  %-44s P %.4f | up %.4f  T %.4f (15 Dec %.4f) | E[Dec|Yes] %.1f vs %.1f"
          % (name, r["p"], r["p_up"], r["p_T"], r["p_T_end"], r["E_dec_yes"], r["E_dec"]))
print("  the file's numpy run: P 0.4314, up 0.2454, T 0.2861 (15 Dec 0.2488), E[Dec|Yes] 175.7 vs 161.1")
print("  S04 revision 2 publishes P(mean target >= 190 on 15 Dec) = 0.32: the rebuild lands on it")

# ------------------------------------------------------------------ R13
hdr("R13  series, windows, AR(1), and the jump double count")
h = pd.read_csv(Q / "risk-short-interest-crowding/datasets/si_history_2022_2026.csv",
                parse_dates=["date"]).sort_values("date")
nas = json.loads((Q / "risk-short-interest-crowding/sources/"
                  "nasdaq_short_interest_20260917T080127Z.json").read_text())
rows = nas["data"]["shortInterestTable"]["rows"]
latest = float(rows[0]["interest"].replace(",", ""))
print("Nasdaq latest settlement %s: %d shares" % (rows[0]["settlementDate"], int(latest)))
for so in (592.0, 598.785682):
    print("  on %.3fm shares: %.4f%% of shares; 5%% needs %.3fm shares (x%.3f of the latest)"
          % (so, latest / (so * 1e6) * 100, .05 * so, .05 * so * 1e6 / latest))
x = list(h.si_pct_used) + [latest / (592.0 * 1e6) * 100]
ov = h.dropna(subset=["si_pct_shares"])
rat = ov.shares_m_est / (ov.short_interest_shares / 1e6)
print("MarketBeat reconstruction vs the repo series: n %d, ratio mean %.4f sd %.4f"
      % (len(rat), rat.mean(), rat.std()))
print("series n %d, mean %.3f, median %.3f, max %.3f, min %.3f, latest at the %.0fth percentile"
      % (len(x), mean(x), pct(x, .5), max(x), min(x),
         100 * sum(v < x[-1] for v in x) / len(x)))
W = 8
win = [(x[i - 1], max(x[i:i + W])) for i in range(1, len(x) - W + 1)]
for name, sub in [("all", win), ("prior level < 3.0", [w for w in win if w[0] < 3.0]),
                  ("prior level < 2.5", [w for w in win if w[0] < 2.5])]:
    print("  8-settlement windows %-18s n %2d  P(max>=5) %.4f  P(max>=4) %.4f  largest rise %.2fpt"
          % (name, len(sub), sum(m >= 5 for _, m in sub) / len(sub),
             sum(m >= 4 for _, m in sub) / len(sub), max(m - p0 for p0, m in sub)))
print("  the rise now required is %.2fpt: no window in the series delivers it" % (5 - x[-1]))
ch = [x[i + 1] - x[i] for i in range(len(x) - 1)]
print("  per-step sd %.4f, %d steps, rises >= 0.9pt: %s (both the Sep 2023 S&P 500 inclusion)"
      % (stdev(ch), len(ch), [round(c, 2) for c in ch if c >= 0.9]))
sx, sy = x[:-1], x[1:]
mx, my = mean(sx), mean(sy)
slope = sum((u - mx) * (v - my) for u, v in zip(sx, sy)) / sum((u - mx) ** 2 for u in sx)
icept = my - slope * mx
res = [v - (slope * u + icept) for u, v in zip(sx, sy)]
clean = [r for r in res if abs(r) < 0.75]
print("  AR(1) slope %.4f, intercept %.4f, long-run mean %.4f, residual sd %.4f (clean pool n %d sd %.4f)"
      % (slope, icept, icept / (1 - slope), stdev(res), len(clean), stdev(clean)))


def ar1(pool, seed=3, n=60_000, jq=0.0, op=0.0, opts=0.7):
    g = random.Random(seed)
    hit5 = hit4 = 0
    for _ in range(n):
        v = x[-1]
        ov = g.random() < op
        m = -9.9
        for k in range(9):
            v = slope * v + icept + pool[g.randrange(len(pool))]
            if jq and g.random() < jq:
                v += g.uniform(0.9, 1.5)
            if op and (k - 1) in (3, 4):
                v += ov * opts / 2
            if k >= 1:
                m = max(m, v)
        hit5 += m >= 5
        hit4 += m >= 4
    return hit5 / n, hit4 / n


for name, pool, jq, op in [("AR(1) only", res, 0.0, 0.0),
                           ("AR(1) + jump 2/99", res, 2 / 99, 0.0),
                           ("AR(1) + jump + down-print overlay (published)", res, 2 / 99, 0.41),
                           ("episode shocks removed from the pool, + jump", clean, 2 / 99, 0.0),
                           ("episode shocks removed, + jump + overlay", clean, 2 / 99, 0.41)]:
    p5, p4 = ar1(pool, jq=jq, op=op)
    print("  %-46s P(max>=5) %.4f  P(max>=4) %.4f" % (name, p5, p4))
print("  the file's numpy run: 0.0051 / 0.0176 / 0.0307 for the first three")
```
