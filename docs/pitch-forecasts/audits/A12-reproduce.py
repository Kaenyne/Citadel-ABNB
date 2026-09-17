"""A12 read-only reproduction (R10, R11, R15, R16 + the B13/B15/F01 coherence checks).
Run from the repository root: python -B docs/pitch-forecasts/audits/A12-reproduce.py
Requires stdlib + pandas only (no numpy, no scipy). Writes nothing; uses no network.
"""
from pathlib import Path
import csv, datetime as dt, json, math, random, statistics as st
import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
R10 = Q / "risk-dollar-weakens"
R11 = Q / "risk-q4-us-revpar-strong"
R15 = Q / "risk-world-cup-quantified-small"
R16 = Q / "risk-q4-nights-print-meets-street"
B13 = Q / "bonus-q4-nights-print-weak"
B15 = Q / "bonus-q4-us-revpar-soft"


def Phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def npdf(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def psd(xs):
    return st.pstdev(xs) if len(xs) > 1 else 0.0


# ======================================================================= R10
print("=" * 78)
print("R10 / 1. FRED snapshot, spot, threshold")
f = sorted((R10 / "sources").glob("fred_DTWEXBGS_2026*.csv"))[-1]
rows = list(csv.DictReader(f.open(encoding="utf-8")))
dates = [r["observation_date"] for r in rows if r["DTWEXBGS"].strip()]
vals = [float(r["DTWEXBGS"]) for r in rows if r["DTWEXBGS"].strip()]
print("  file rows %d | non-null %d (log claim 1: 5,188) | last %s = %.4f"
      % (len(rows), len(vals), dates[-1], vals[-1]))
lv = [math.log(v) for v in vals]
dl = [lv[i + 1] - lv[i] for i in range(len(lv) - 1)]
for k, lbl in ((252, "12m"), (126, "6m"), (63, "3m")):
    print("  trailing %s log change %+.4f" % (lbl, lv[-1] - lv[-1 - k]))
dxf = sorted((R10 / "sources").glob("yfinance_dxy_daily_2026*T0756*.csv"))[-1]
dx = {r[0]: float(r[1]) for r in list(csv.reader(dxf.open(encoding="utf-8")))[1:]}
bmap = dict(zip(dates, vals))
pairs = [(math.log(bmap[d] / bmap[p]), math.log(dx[d] / dx[p]))
         for p, d in zip(dates, dates[1:]) if d >= "2024-01-01" and d in dx and p in dx]
mb = st.mean([a for a, _ in pairs])
mx = st.mean([b for _, b in pairs])
cov = sum((a - mb) * (b - mx) for a, b in pairs) / (len(pairs) - 1)
varx = sum((b - mx) ** 2 for _, b in pairs) / (len(pairs) - 1)
beta = cov / varx
s16 = vals[-1] * math.exp(beta * math.log(dx["2026-09-16"] / dx["2026-09-11"]))
print("  beta(broad on DXY, 2024+) %.4f n=%d | s16 est %.4f | threshold %.4f"
      % (beta, len(pairs), s16, 0.96 * s16))
print("  model values: 0.57216 / 119.02255 / 114.26164")

print("R10 / 2. horizon: FRED observations 16 Sep 2026 to 11 Feb 2027")
hol = {dt.date(2026, 10, 12), dt.date(2026, 11, 11), dt.date(2026, 11, 26),
       dt.date(2026, 12, 25), dt.date(2027, 1, 1), dt.date(2027, 1, 18)}
d, nobs = dt.date(2026, 9, 16), 0
while d < dt.date(2027, 2, 11):
    d += dt.timedelta(1)
    if d.weekday() < 5 and d not in hol:
        nobs += 1
print("  business days net of federal holidays = %d   (the model hard-codes H = 105)" % nobs)

print("R10 / 3. empirical windows and the effective sample size")
THR = math.log(0.96)
for H in (100, 105):
    r = [lv[i + H] - lv[i] for i in range(len(lv) - H)]
    k = sum(1 for x in r if x <= THR)
    blk = r[::H]
    kb = sum(1 for x in blk if x <= THR)
    pb = kb / len(blk)
    print("  H=%3d n=%4d P=%.4f mean=%+.4f sd=%.4f | non-overlapping n=%d P=%.4f se=%.4f"
          % (H, len(r), k / len(r), st.mean(r), psd(r), len(blk), pb,
             math.sqrt(pb * (1 - pb) / len(blk))))
H = 105
r105 = [lv[i + H] - lv[i] for i in range(len(lv) - H)]
tail = [x for x in r105 if x <= THR]
print("  tail: n=%d mean=%.4f median=%.4f   (log claim 7: 619 / -0.056 / -0.0527)"
      % (len(tail), st.mean(tail), st.median(tail)))
byyr = {}
for i, x in enumerate(r105):
    byyr.setdefault(dates[i][:4], []).append(x)
zero = sorted(y for y, xs in byyr.items() if not any(x <= THR for x in xs))
print("  years with ZERO sub-threshold windows: %d of %d -> %s" % (len(zero), len(byyr), zero))
print("  log claim 4 says 12 of 21")

print("R10 / 4. vol regime: trailing 252d vol vs the FORWARD 105d vol")
trail = [psd(dl[i - 252:i]) * math.sqrt(252) if i >= 252 else None for i in range(len(dl))]
fwd = [psd(dl[i:i + H]) * math.sqrt(252) if i + H <= len(dl) else None for i in range(len(dl))]
pr2 = [(t, g, r105[i]) for i, (t, g) in enumerate(zip(trail, fwd))
       if t is not None and g is not None and i < len(r105)]
cur = psd(dl[-252:]) * math.sqrt(252)
print("  current trailing vols: 63d %.4f 126d %.4f 252d %.4f full %.4f"
      % (psd(dl[-63:]) * math.sqrt(252), psd(dl[-126:]) * math.sqrt(252), cur,
         psd(dl) * math.sqrt(252)))
for lo, hi, lbl in ((0.0, 0.042, "quintile 1 (<=4.20%)"),
                    (cur - .01, cur + .01, "band +/-1pp"),
                    (0.0, 9.0, "all windows")):
    sel = [(t, g, x) for t, g, x in pr2 if lo <= t < hi]
    print("  %-22s n=%5d  P(<=-4.08%%) %.4f  mean FORWARD vol %.4f  ratio %.2f"
          % (lbl, len(sel), sum(1 for _, _, x in sel if x <= THR) / len(sel),
             st.mean([g for _, g, _ in sel]), st.mean([g / t for t, g, _ in sel])))
print("  => a calm start does not stay calm; the forward-vol input should be ~4.6%, not 4.12%")

print("R10 / 5. drift: what the Reuters poll actually implies")
spot = 1.153762
path = ((0, spot), (3, 1.16), (6, 1.17), (12, 1.18))
tm = 4.85
eur = spot
for (m0, v0), (m1, v1) in zip(path, path[1:]):
    if m0 <= tm <= m1:
        eur = v0 + (v1 - v0) * (tm - m0) / (m1 - m0)
print("  EUR/USD 16 Sep %.4f -> poll-interpolated at %.2f months %.4f = %+.4f log"
      % (spot, tm, eur, math.log(eur / spot)))
print("  broad at beta -0.6 = %+.4f ; the log uses -0.0042" % (-0.6 * math.log(eur / spot)))


def pn(vol, drift, hh=105):
    return Phi((THR - drift) / (vol * math.sqrt(hh / 252)))


for vol in (0.0412, 0.046, 0.048):
    print("  vol %.4f: drift 0 -> %.4f | -0.0042 -> %.4f | -0.0066 -> %.4f"
          % (vol, pn(vol, 0.0), pn(vol, -0.0042), pn(vol, -0.0066)))
print("  published blend 0.35*0.10 + 0.35*0.07 + 0.30*0.10 = %.4f"
      % (0.35 * 0.10 + 0.35 * 0.07 + 0.30 * 0.10))
print("  repaired blend 0.35*0.10 + 0.35*0.11 + 0.30*0.115 = %.4f"
      % (0.35 * 0.10 + 0.35 * 0.11 + 0.30 * 0.115))

print("R10 / 6. impact arithmetic (B4 exhibit section 5.2 + brief)")
FY26R, FY27R, FY27E = 14268.0, 15829.0, 5483.0
base_m = 100 * FY27E / FY27R
print("  FY27 line build: revenue %.0f EBITDA %.0f margin %.3f%%" % (FY27R, FY27E, base_m))
dpp = 2.3 * 5.6 / 5.0
for basis, lbl in ((FY26R / 100.0, "142.9 per pt = 1% of FY26 revenue (B4 5.2)"),
                   (158.0, "158.0 per pt = 1% of FY27 revenue (the brief)")):
    dR = dpp * basis
    print("  %-44s dRev %+6.0fM  margin %+.2fpp  EPS %+.3f"
          % (lbl, dR, 100 * (FY27E + dR) / (FY27R + dR) - base_m, dR * 0.0014))
print("  the log publishes dRev +400M, margin +1.6pp, EPS +0.37 = 400 x 0.66 x 0.0014,")
print("  i.e. 0.66 is used twice: once as pp-per-pt for the margin row and again as a dollar rate")

# ======================================================================= R11
print("=" * 78)
print("R11 / 1. FY-implied Q4 grid, AR(1) leg, blend")
w = (0.23, 0.26, 0.27, 0.24)
q1 = 3.8
grid = [(fy - w[0] * q1 - w[1] * q2 - w[2] * q3) / w[3]
        for q2 in (4.5, 5.2, 6.0) for q3 in (4.5, 5.2, 6.0) for fy in (4.0, 4.4, 4.8)]
c_str = st.mean(grid)
c_ar = 2.0 + 0.6 * (5.5 - 2.0)
adj = 0.8 - 0.7 - 0.2
centre = 0.5 * c_str + 0.5 * c_ar + adj
sdv = math.sqrt(1.6 ** 2 + 0.5 ** 2)
z = (4.0 - centre) / sdv
print("  FY-implied mean %.3f (n=%d) | AR(1) one step %.2f | adj %+.1f | centre %.3f sd %.3f"
      % (c_str, len(grid), c_ar, adj, centre, sdv))
print("  P(>=4.0) %.4f  P(<=1.0) %.4f  E[x|>=4] %.2f   (log: 0.3866 / 0.07 / 5.2)"
      % (1 - Phi(z), Phi((1.0 - centre) / sdv), centre + sdv * npdf(z) / (1 - Phi(z))))
print("  section 5 and the JSON call the AR leg a 'two-step'; r11_model.py applies one step")
c2 = centre - 0.8
print("  DROP the +0.8 easy-comp credit (the CoStar FY26 forecast already embeds the 4Q25 base):")
print("    centre %.3f -> P(>=4.0) %.4f  P(<=1.0) %.4f   [not in section 7]"
      % (c2, 1 - Phi((4.0 - c2) / sdv), Phi((1.0 - c2) / sdv)))

print("R11 / 2. the claim-10 base rate is a hand-entered list, not a repo series")
hist = [12, 3, 1.5, 2, 1, 1, 2, 3, 0, -0.5, -1, 0, 3.8, 5.2]
print("  r11_model.py line 36 hist =", hist)
print("  >=4%%: %d of %d | <=1%%: %d of %d (B15 claims 6 of 13)"
      % (sum(1 for x in hist[1:] if x >= 4), len(hist) - 1,
         sum(1 for x in hist[1:] if x <= 1), len(hist) - 1))
try:
    g = pd.read_csv(ROOT / "data/processed/q3nowcast/G/G_quarterly_panel.csv").rename(
        columns={"Unnamed: 0": "q"})
    print("  the only hotel RevPAR series in the repo are OPERATOR, GLOBAL, system-wide:")
    print(g[g.q >= "2023Q1"][["q", "mar_revpar_full", "hlt_revpar_full"]].to_string(index=False))
except Exception as exc:
    print("  panel unavailable:", exc)

print("R11 / 3. sources")
print("  R11 sources/ contents:", sorted(p.name for p in (R11 / "sources").glob("*")))
print("  B15 sources/ raw html bytes:",
      {p.name: p.stat().st_size for p in (B15 / "sources").glob("*.html")})

print("R11 / 4. mirror-question coherence with B15")
tw, tc, ts, sw, sc, ss = 0.90, 3.7, 1.6, 0.10, 0.8, 1.8
mix4 = tw * (1 - Phi((4.0 - tc) / ts)) + sw * (1 - Phi((4.0 - sc) / ss))
mix1 = tw * Phi((1.0 - tc) / ts) + sw * Phi((1.0 - sc) / ss)
print("  B15 mixture 0.9*N(3.7,1.6)+0.1*N(0.8,1.8): P(>=4) %.4f P(<=1) %.4f mean %.2f"
      % (mix4, mix1, tw * tc + sw * sc))
print("  R11 section 6 states P(<=1) = 0.07; B15 publishes 0.10 for the same quantity")

# ======================================================================= R15
print("=" * 78)
print("R15 / event record, Laplace variants, tree replay")
rec = list(csv.DictReader((R15 / "datasets/r15_event_record.csv").open(encoding="utf-8")))
n_pts = sum(1 for x in rec if x["points_figure"] != "no points")
n_size = sum(1 for x in rec if x["size_language"].startswith("relatively small"))
print("  event discussions %d | with a points figure %d | with qualifying size language %d"
      % (len(rec), n_pts, n_size))
print("  Laplace(points)/discussion %.4f | Laplace(size language)/discussion %.4f"
      % ((n_pts + 1) / (len(rec) + 2), (n_size + 1) / (len(rec) + 2)))
for lbl, p1 in (("log's implicit per-print rate 0.05", 0.05),
                ("raw size-language frequency 1/8", n_size / len(rec)),
                ("Laplace size language 2/10", (n_size + 1) / (len(rec) + 2))):
    print("    %-38s over two prints -> %.4f" % (lbl, 1 - (1 - p1) ** 2))
tree = {"A_nov": 0.02, "A_feb": 0.04, "B_nov": 0.05, "B_feb": 0.05}
prod = 1.0
for v in tree.values():
    prod *= (1 - v)
print("  tree replay 1 - prod(1-p) = %.4f   (r15_tree.csv: 0.1509)" % (1 - prod))
print("  section 5 claims 1-(0.95)^2 = %.4f, which uses 0.05/print, not the 0.10 Laplace it cites"
      % (1 - 0.95 ** 2))
c05 = json.loads((Q / "bundle-attribution-quantified/forecasts/2026-09-17-forecast.json")
                 .read_text(encoding="utf-8"))
print("  C05 revision %s p_any_quantification = %s ; R15 claim 10 and its anchor quote 0.27"
      % (c05["revision"], c05["p_any_quantification"]))

# ================================================================== R16 / B13
print("=" * 78)
print("R16 / B13 / stdlib replay of the three views and of the mixture")
BASE, THRH, THRL, Q3REF = 121.9, 134.0, 131.0, 9.67
print("  thresholds: %.1fm = %+.4f%%  |  %.1fm = %+.4f%%"
      % (THRH, 100 * (THRH / BASE - 1), THRL, 100 * (THRL / BASE - 1)))


def v1(q3_mu=9.67, q3_sd=1.70, q4_mu=8.1, beta=0.5, res_sd=1.4, tail_w=0.12,
       n=400000, seed=12):
    rng = random.Random(seed)
    hi = lo = 0
    tot = 0.0
    for _ in range(n):
        q3 = rng.gauss(q3_mu, q3_sd)
        if rng.random() < tail_w:
            q4 = 5.5 + beta * (q3 - Q3REF) + rng.gauss(0, 1.5)
        else:
            q4 = q4_mu + beta * (q3 - Q3REF) + rng.gauss(0, res_sd)
        tot += q4
        nights = round(BASE * (1 + q4 / 100), 1)
        hi += nights >= THRH
        lo += nights <= THRL
    return hi / n, lo / n, tot / n


def v2(vec, cm=1.2, cs=1.3, fall=(0.1219, 0.4211), n=200000, seed=13):
    rng = random.Random(seed)
    mids = (10.75, 9.75, 8.0, 6.0, None)
    ph = pl = 0.0
    for wgt, m in zip(vec, mids):
        if m is None:
            ph += wgt * fall[0]
            pl += wgt * fall[1]
            continue
        a = b = 0
        for _ in range(n):
            x = m + rng.gauss(cm, cs)
            nights = round(BASE * (1 + x / 100), 1)
            a += nights >= THRH
            b += nights <= THRL
        ph += wgt * a / n
        pl += wgt * b / n
    return ph, pl


V3 = (0.50, Phi((THRL - 134.0) / 1.5))
base = v1()
print("  V1 (Q3 9.67, res_sd 1.4): P>=134 %.4f  P<=131 %.4f  mean %.3f" % base)
print("     models give 0.1219 / 0.4211 / 7.788")
print("  V3 Street N(134.0,1.5): P>=134 %.4f  P<=131 %.4f   (models: 0.50 / 0.0245)" % V3)
C02v1 = (0.21, 0.19, 0.39, 0.17, 0.04)
C02v2 = (0.18, 0.17, 0.30, 0.31, 0.04)
for lbl, vec, cm in (("C02 rev 1, cushion N(1.2,1.3)   [the models]", C02v1, 1.2),
                     ("C02 rev 1, cushion N(0.78,1.3)  [R16 hand 0.40]", C02v1, 0.78),
                     ("C02 rev 2, cushion N(1.2,1.3)", C02v2, 1.2)):
    gg, ll = v2(vec, cm=cm)
    print("  %-46s V2 %.4f / %.4f -> blend %.4f / %.4f"
          % (lbl, gg, ll, 0.5 * base[0] + 0.3 * gg + 0.2 * V3[0],
             0.5 * base[1] + 0.3 * ll + 0.2 * V3[1]))
print("  published: R16 0.27, B13 0.26; F01 rev 2 carries 0.29 / 0.27, mean 8.70, sd 2.05")
print("  B13 section 5 states V2 0.18 and anchor 0.05: 0.5*0.4211+0.3*0.18+0.2*0.05 = %.4f"
      % (0.5 * 0.4211 + 0.3 * 0.18 + 0.2 * 0.05))
print("  b13_views.csv 0.2622 needs V2 = 0.1558 and V3 = 0.0245: %.4f"
      % (0.5 * 0.4211 + 0.3 * 0.1558 + 0.2 * 0.0245))
v2mean = 0.21 * 11.95 + 0.19 * 10.95 + 0.39 * 9.2 + 0.17 * 7.2 + 0.04 * 7.788
print("  mixture mean = 0.5*7.788 + 0.3*%.3f + 0.2*9.926 = %.3f   (B13 asserts about 8.3)"
      % (v2mean, 0.5 * 7.788 + 0.3 * v2mean + 0.2 * 9.926))

print("R16 / V1 residual sd vs the historical Q3->Q4 sequential change")
seq = [20.163 - 25.094, 12.018 - 13.541, 12.348 - 8.481, 9.820 - 8.795]
print("  observed Q3->Q4 changes %s  mean %+.2f sd %.2f (n=4); V1 total sd is 1.85"
      % ([round(x, 2) for x in seq], st.mean(seq), st.stdev(seq)))
for rs in (1.4, 2.0, 2.6):
    a, b, _ = v1(q3_mu=9.5, res_sd=rs, seed=14)
    print("    Q3 centre 9.5 (R01 rev 2), res_sd %.1f -> P>=134 %.4f  P<=131 %.4f" % (rs, a, b))

print("R16 / impact arithmetic")
dR = 250.0
print("  +250M of FY27 revenue, costs held -> margin %+.2fpp, EPS %+.3f"
      % (100 * (FY27E + dR) / (FY27R + dR) - base_m, dR * 0.0014))
print("  the log publishes +1.05pp and +0.23, where 0.23 = 250 x 0.66 x 0.0014")

# ================================================================ registers
print("=" * 78)
print("Cross-question register")
for slug in ("risk-dollar-weakens", "risk-q4-us-revpar-strong",
             "risk-world-cup-quantified-small", "risk-q4-nights-print-meets-street",
             "bonus-q4-nights-print-weak", "bonus-q4-us-revpar-soft",
             "q1-27-nights-guide-above-82", "risk-q3-nights-meets-guide",
             "q4-nights-bucket", "bundle-attribution-quantified"):
    o = json.loads((Q / slug / "forecasts/2026-09-17-forecast.json").read_text(encoding="utf-8"))
    fin = o["final"]
    head = fin.get("p", fin.get("vector"))
    line = "  %-9s rev %s  final %s" % (o["question_id"], o["revision"], head)
    imp = o.get("impact")
    if imp:
        line += " | stock %s EV %s material %s | EV check %.3f" % (
            imp["stock_usd_per_share"], imp["ev_stock_usd_per_share"], imp["material"],
            round(fin["p"] * imp["stock_usd_per_share"], 3))
    print(line)

print("Kalshi snapshot fields the R16 log reports as null")
kj = json.loads((R16 / "sources/kalshi_KXABNBA_open_20260917T075503Z.json")
                .read_text(encoding="utf-8"))
for m in sorted(kj["markets"], key=lambda x: x["floor_strike"]):
    print("  >%3dm bid %s ask %s last %s volume_fp %s open_interest_fp %s updated %s"
          % (m["floor_strike"] / 1e6, m["yes_bid_dollars"], m["yes_ask_dollars"],
             m["last_price_dollars"], m["volume_fp"], m["open_interest_fp"],
             m["updated_time"][:10]))
