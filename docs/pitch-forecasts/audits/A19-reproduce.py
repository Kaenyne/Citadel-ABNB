"""A19 audit reproduction — X01 scenario-probabilities. Stdlib only; reads, prints, writes nothing."""
import csv, math
from pathlib import Path
from statistics import NormalDist

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
Phi = NormalDist().cdf

CENTRE, SD, GAP_SD, TILT, OR_C02 = 9.5, 1.70, 3.1, 0.66, 2.0
THR_R01, THR_R02, SHORT_THR = 9.9925149701, 10.5913173652, 8.55
P_C01, C04_D_BELOW, C04_D_NOT = 0.72, 0.3171, 0.1524
DECEL_THR = 10.09                      # S01 revision-2 dead band on 2Q26's 10.34
OPTS = ["breaker", "base", "short", "none"]

# ---------------------------------------------------------------- 1. print partition
print("print partition  P(<=8.5) %.4f  P(8.5-10.6) %.4f  P(>=10.6) %.4f" % (
    Phi((SHORT_THR - CENTRE) / SD),
    Phi((THR_R02 - CENTRE) / SD) - Phi((SHORT_THR - CENTRE) / SD),
    1 - Phi((THR_R02 - CENTRE) / SD)))

# ---------------------------------------------------------------- 2. C02 revision-2 branch table
c02_final, branch = [], {}
with open(Q / "q4-nights-bucket/datasets/decomposition_v2_output.csv", encoding="utf-8") as f:
    block = None
    for row in csv.reader(f):
        if not row or not row[0]:
            continue
        if row[0] in ("estimate", "joint_branch"):
            block = row[0]
            continue
        if block == "estimate" and row[0] == "final":
            c02_final = [float(v) for v in row[1:6]]
        if block == "joint_branch":
            mass = float(row[6])
            branch[row[0]] = dict(mass=mass, cond=[float(v) / mass for v in row[1:6]])


def truncated_mean(lo, hi, mu, sd):
    def pdf(z):
        return math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)
    a = None if lo is None else (lo - mu) / sd
    b = None if hi is None else (hi - mu) / sd
    Fa, Fb = (0.0 if a is None else Phi(a)), (1.0 if b is None else Phi(b))
    fa, fb = (0.0 if a is None else pdf(a)), (0.0 if b is None else pdf(b))
    return mu + sd * (fa - fb) / (Fb - Fa)


# anchors at the branch means of the rev-1 normal the C02 tree was built on
ANCHOR_X = [truncated_mean(None, 9.0, 9.67, 1.70),
            truncated_mean(9.0, 10.0, 9.67, 1.70),
            truncated_mean(10.0, None, 9.67, 1.70)]
ANCHOR_L = [[math.log(p) for p in branch[k]["cond"]] for k in ("lt9", "9to10", "ge10")]
print("C02 anchors", [round(v, 3) for v in ANCHOR_X])

# branch-varying explicit-bucket share of option (d), from C02's own conditioning block
DIRECTIONAL = {"lt9": 0.35 * 0.75, "9to10": 0.28 * 0.60, "ge10": 0.25 * 0.55}
EXPLICIT_SHARE = {}
for k in ("lt9", "9to10", "ge10"):
    EXPLICIT_SHARE[k] = 1 - DIRECTIONAL[k] / branch[k]["cond"][3]
print("explicit-bucket share of (d) by branch",
      {k: round(v, 3) for k, v in EXPLICIT_SHARE.items()},
      "  directional-moderate total",
      round(sum(branch[k]["mass"] * DIRECTIONAL[k] for k in DIRECTIONAL), 4))


def logits(x):
    xc = min(max(x, 6.0), 14.0)
    out = []
    for j in range(5):
        s0 = (ANCHOR_L[1][j] - ANCHOR_L[0][j]) / (ANCHOR_X[1] - ANCHOR_X[0])
        s2 = (ANCHOR_L[2][j] - ANCHOR_L[1][j]) / (ANCHOR_X[2] - ANCHOR_X[1])
        if xc <= ANCHOR_X[1]:
            out.append(ANCHOR_L[0][j] + s0 * (xc - ANCHOR_X[0]))
        else:
            out.append(ANCHOR_L[1][j] + s2 * (xc - ANCHOR_X[1]))
    return out


# IPF on the model's own 0.01 grid, so the fitted factors match the published ones
GRID = [4.0 + i * 0.01 for i in range(1201)]
W = [math.exp(-0.5 * ((g - CENTRE) / SD) ** 2) for g in GRID]
W = [w / sum(W) for w in W]
LG = [logits(g) for g in GRID]
FACT = [0.0] * 5
for _ in range(400):
    marg = [0.0] * 5
    for w, lg in zip(W, LG):
        e = [math.exp(lg[j] + FACT[j]) for j in range(5)]
        t = sum(e)
        for j in range(5):
            marg[j] += w * e[j] / t
    for j in range(5):
        FACT[j] += math.log(c02_final[j] / marg[j])
print("C02 IPF factors", [round(v, 3) for v in FACT], " target", c02_final)

# ---------------------------------------------------------------- 3. C01 intercept
def mean_p_below(g0):
    return sum(w * Phi(-(g0 + TILT * (g - CENTRE)) / GAP_SD) for w, g in zip(W, GRID))


lo, hi = -10.0, 10.0
for _ in range(100):
    mid = 0.5 * (lo + hi)
    lo, hi = (mid, hi) if mean_p_below(mid) > P_C01 else (lo, mid)
G0 = 0.5 * (lo + hi)
print("C01 g0 %.4f  implied P(below) %.4f" % (G0, mean_p_below(G0)))
print("C01 slope check: 2/3 weight on GBV = %.4f" % (
    (2 / 3 * 25.88) / (2 / 3 * 25.88 + 1 / 3 * 27.20)),
    " per point of nights growth = %.3f" % (0.6556 / 1.095))


def cd_split(marginal, p_below, odds_ratio):
    """P(c or d | below), P(c or d | not below) with the given odds ratio and marginal."""
    lo, hi = 1e-9, 1 - 1e-9
    for _ in range(80):
        pa = 0.5 * (lo + hi)
        pb = odds_ratio * pa / (1 - pa + odds_ratio * pa)
        lo, hi = (lo, pa) if p_below * pb + (1 - p_below) * pa > marginal else (pa, hi)
    pa = 0.5 * (lo + hi)
    return odds_ratio * pa / (1 - pa + odds_ratio * pa), pa


# ---------------------------------------------------------------- 4. the vector, by quadrature
FINE = [2.0 + i * 0.0005 for i in range(32001)]
FW = [math.exp(-0.5 * ((g - CENTRE) / SD) ** 2) for g in FINE]
FW = [w / sum(FW) for w in FW]
FLG = [logits(g) for g in FINE]


def vector(base_thr=THR_R02, reading="literal", precedence="breaker_first",
           short_thr=SHORT_THR, breaker_thr=THR_R02,
           c04_d_below=C04_D_BELOW, c04_d_not=C04_D_NOT, use_c04=True):
    total = {o: 0.0 for o in OPTS}
    for w, g, lg in zip(FW, FINE, FLG):
        if w < 1e-13:
            continue
        e = [math.exp(lg[j] + FACT[j]) for j in range(5)]
        pc = [v / sum(e) for v in e]
        p_cd = pc[2] + pc[3]
        d_share = pc[3] / max(p_cd, 1e-12)
        p_below = Phi(-(G0 + TILT * (g - CENTRE)) / GAP_SD)
        cd_b, cd_a = cd_split(p_cd, p_below, OR_C02)
        share = (EXPLICIT_SHARE["lt9"] if g < 9.0 else
                 EXPLICIT_SHARE["9to10"] if g < 10.0 else
                 EXPLICIT_SHARE["ge10"]) if reading == "material" else 1.0
        for below, pb in ((True, p_below), (False, 1 - p_below)):
            if pb <= 0:
                continue
            cd = cd_b if below else cd_a
            rest = (1 - cd) / max(1 - p_cd, 1e-12)
            opts = {"a": rest * pc[0], "b": rest * pc[1], "e": rest * pc[4],
                    "c": cd * (1 - d_share), "d": cd * d_share}
            p_c04d = (c04_d_below if below else c04_d_not) if use_c04 else 0.0
            for o2, p2 in opts.items():
                for c04d, p4 in ((True, p_c04d), (False, 1 - p_c04d)):
                    for frac, d_gate in ([(share, True), (1 - share, False)]
                                         if o2 == "d" else [(1.0, False)]):
                        m = w * pb * p2 * p4 * frac
                        if m <= 0:
                            continue
                        breaker = (g >= breaker_thr) and o2 == "a"
                        short = (g < short_thr) or d_gate or c04d
                        base = (g < base_thr) and (o2 in ("b", "c") or below) and not short
                        if precedence == "breaker_first":
                            o = ("breaker" if breaker else "short" if short
                                 else "base" if base else "none")
                        else:
                            o = ("short" if short else "breaker" if breaker
                                 else "base" if base else "none")
                        total[o] += m
    return {k: round(v, 4) for k, v in total.items()}


print("published gates            ", vector())
print("decelerating base gate     ", vector(base_thr=DECEL_THR))
print("strict decel (<10.34)      ", vector(base_thr=10.34))
print("short-first precedence     ", vector(precedence="short_first"))
print("material (branch shares)   ", vector(reading="material"))
print("material + decel gate      ", vector(base_thr=DECEL_THR, reading="material"))
print("no C04 leg                 ", vector(use_c04=False))
print("C04 (d) at 0.20            ", vector(c04_d_below=0.3171 * 0.20 / 0.27,
                                            c04_d_not=0.1524 * 0.20 / 0.27))

# ---------------------------------------------------------------- 5. base-rate panel
rows = list(csv.DictReader(open(
    Q / "scenario-probabilities/datasets/x01_base_rate_panel.csv", encoding="utf-8")))
for r in rows:
    r["accel_pts"] = float(r["accel_pts"])
    r["nights_yoy"] = float(r["nights_yoy"])
    r["raw"] = float(r["ret_1d_raw"])
    r["excess"] = float(r["ret_1d_excess"])
    r["below"] = r["guide_below_street"] == "True"


def classify(r, base_thr=0.25, material=False, level_gate=False):
    opt = r["descriptor_option"]
    d_gate = (r["descriptor_type"] == "bucket" and opt == "d") if material else opt == "d"
    nights = (r["nights_yoy"] <= 8.5) if level_gate else (r["accel_pts"] <= -1.84)
    short = nights or d_gate or r["fy_margin_action"] in ("lowered", "softened")
    if (r["accel_pts"] >= 0.25) and opt == "a":
        return "breaker"
    if short:
        return "short"
    if (r["accel_pts"] < base_thr) and (opt in ("b", "c") or r["below"]) and not short:
        return "base"
    return "none"


WINDOWS = {"all16": lambda r: True,
           "W1": lambda r: r["print_date"] >= "2023-05-01",
           "W2": lambda r: r["print_date"] >= "2024-05-01"}
for thr, gl in ((0.25, "published base gate"), (-0.25, "decelerating base gate")):
    for material in (False, True):
        for level in (False, True):
            for wname, wf in WINDOWS.items():
                sub = [r for r in rows if wf(r)]
                cells = [classify(r, thr, material, level) for r in sub]
                print(gl, "material" if material else "literal",
                      "level-gate" if level else "sequential-gate", wname, "n", len(sub),
                      {o: round(cells.count(o) / len(cells), 3) for o in OPTS})

print("FY margin actions, November prints",
      [(r["print_quarter"], r["fy_margin_action"]) for r in rows
       if r["print_quarter"].startswith("3Q")])
print("descriptor options: (d) count", sum(1 for r in rows if r["descriptor_option"] == "d"),
      " of which explicit buckets",
      sum(1 for r in rows if r["descriptor_option"] == "d"
          and r["descriptor_type"] == "bucket"))


# ---------------------------------------------------------------- 6. reaction regressions
def ols(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    return sxy / sxx, my - (sxy / sxx) * mx, sxy / math.sqrt(sxx * syy)


deep = [r for r in rows if r["accel_pts"] <= -1.84]
print("deep decelerations n", len(deep),
      "mean raw %.2f" % (sum(r["raw"] for r in deep) / len(deep)),
      [(r["print_quarter"], r["raw"]) for r in deep])
deep_w1 = [r for r in deep if r["print_date"] >= "2023-05-01"]
print("  in W1 only: n", len(deep_w1),
      "mean raw %.2f" % (sum(r["raw"] for r in deep_w1) / len(deep_w1)))
for wname, wf in WINDOWS.items():
    sub = [r for r in rows if wf(r)]
    b, a, rho = ols([r["accel_pts"] for r in sub], [r["excess"] for r in sub])
    print(wname, "all prints  n", len(sub), "slope %.2f corr %.3f" % (b, rho))
    dec = [r for r in sub if r["accel_pts"] < 0]
    b, a, rho = ols([r["accel_pts"] for r in dec], [r["excess"] for r in dec])
    print(wname, "decelerators n", len(dec),
          "slope %.2f intercept %.2f corr %.3f" % (b, a, rho))

# ---------------------------------------------------------------- 7. memo arithmetic
scen = {"breaker": (0.1394, 175.1, 177.7), "base": (0.2231, 162.3, 164.8),
        "short": (0.5547, 161.9, 164.4), "none": (0.0828, 173.1, 175.7)}
print("PW 15 Dec by conditional median %.1f (published 164.8)"
      % sum(p * m for p, m, _ in scen.values()))
print("PW 15 Dec by conditional mean   %.1f (= the joint's unconditional mean)"
      % sum(p * mu for p, _, mu in scen.values()))
print("memo breaker 0.25 needs P(a | >=10.6) = %.3f against the joint's 0.535"
      % (0.25 / (1 - Phi((THR_R02 - CENTRE) / SD))))
