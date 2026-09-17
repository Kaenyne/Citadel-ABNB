"""X01 scenario-probabilities (batch A19), revision 1: ONE joint simulation over
    3Q26 nights print (latent y/y %) x C01 (4Q26 revenue guide below Street) x C02 (4Q26 nights bucket)
    x C04 (FY26 margin sentence) x day-1 return (S01 cells) x 15 Dec close (S02 branches),
classified into the four X01 options. numpy + stdlib only; seeded (20260917); n = 1,000,000.
Run from the repo root:  py -3.13 docs/pitch-forecasts/questions/scenario-probabilities/datasets/x01_joint.py

Inputs (all read from disk, paths relative to the repo root; every one is a revision-2 object):
  - questions/risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json   (print: N(9.5, 1.70); R01/R02 thresholds)
  - questions/q4-nights-bucket/datasets/decomposition_v2_output.csv             (C02 rev 2: final vector and branch x option joint)
  - questions/fy26-margin-sentence/datasets/mc_joint_and_conditionals_v2.json   (C04 rev 2: C04 | C01 below / not below)
  - questions/q4-revenue-guide-vs-street/forecasts/2026-09-17-forecast.json     (C01 rev 2: 0.72)
  - questions/day1-move-5nov/datasets/s01_v2_cells.csv                          (S01 rev 2: twelve (state x C01 x C02) return cells)
  - questions/close-15dec-2026/datasets/mixture_base_run_v2.json, final_blend_v2.json (S02 rev 2: branch 15 Dec medians, final median)
  - data/processed/reverse_dcf/C/C_print_panel.csv + questions/q4-nights-bucket/datasets/nights_descriptor_vs_printed_and_comp_v2.csv
    (base-rate construction: the 16 ex-reopening prints 3Q22-2Q26 classified into the four cells)

Option definitions (QUESTIONS.md X01, operationalised per the A19 brief; precedence breaker > short > base > none):
  thesis breaker : printed nights >= 10.6% (latent >= 10.5913, R02) AND C02 = (a)
  short case     : printed nights <= 8.5% (latent < 8.55) OR C02 = (d) OR C04 = (d)
  base           : print < 10.6% AND (C02 in {b, c} OR C01 below) AND not short
  none           : everything else
Alternative 'material' reading of the short case (reported, not the headline): explicit mid-single bucket only
  (C02 rev 2 sub-split: 0.12 of the 0.31 is the explicit bucket, 0.19 the directional 'moderate' sentence) OR nights <= 8.5 OR C04 (d).
"""
import csv, json, math, pathlib
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
QDIR = HERE.parents[1]            # docs/pitch-forecasts/questions
ROOT = HERE.parents[4]            # repo root
SEED = 20260917
N = 1_000_000
OPTS = ["thesis breaker", "base", "short case", "none of the above"]
C02_OPTS = ["a", "b", "c", "d", "e"]
C04_OPTS = ["a", "b", "c", "d", "e"]


def Phi(z):
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def phi(z):
    return math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)


# ------------------------------------------------------------------ inputs
adopted = json.load(open(QDIR / "risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json", encoding="utf-8"))
PRINT_CENTRE = adopted["parametric"]["centre"]          # 9.5
PRINT_SD = adopted["parametric"]["sd"]                  # 1.70
THR_R01 = adopted["events"]["R01_printed_ge_147_0m"]["threshold_pct"]   # 9.9925
THR_R02 = adopted["events"]["R02_printed_ge_147_8m"]["threshold_pct"]   # 10.5913
S01_DECEL_THR, S01_ACCEL_THR = 10.09, 10.59             # S01 rev-2 dead band on 2Q26's 10.34
SHORT_NIGHTS_THR = 8.55                                 # printed rate (one decimal) <= 8.5%

c01 = json.load(open(QDIR / "q4-revenue-guide-vs-street/forecasts/2026-09-17-forecast.json", encoding="utf-8"))
P_C01 = c01["final"]["p"]                               # 0.72

c04 = json.load(open(QDIR / "fy26-margin-sentence/datasets/mc_joint_and_conditionals_v2.json", encoding="utf-8"))
C04_GIVEN_BELOW = np.array([c04["c04_given_below"][o] for o in C04_OPTS])
C04_GIVEN_NOT = np.array([c04["c04_given_not_below"][o] for o in C04_OPTS])

# C02 revision 2: final vector and the branch x option joint (branches under the rev-1 normal N(9.67, 1.70))
c02_final, c02_branch = {}, {}
with open(QDIR / "q4-nights-bucket/datasets/decomposition_v2_output.csv", encoding="utf-8") as f:
    block = None
    for row in csv.reader(f):
        if not row or not row[0]:
            continue
        if row[0] == "estimate":
            block = "est"; continue
        if row[0] == "joint_branch":
            block = "joint"; continue
        if block == "est" and row[0] == "final":
            c02_final = {o: float(v) for o, v in zip(C02_OPTS, row[1:6])}
        if block == "joint":
            c02_branch[row[0]] = dict(mass=float(row[6]), cond=np.array([float(v) for v in row[1:6]]) / float(row[6]))
C02_FINAL = np.array([c02_final[o] for o in C02_OPTS])
C02_D_EXPLICIT_SHARE = 0.12 / 0.31                       # C02 rev 2 forecast JSON 'subsplits'


def branch_mean(lo, hi, mu, sd):
    a = -np.inf if lo is None else (lo - mu) / sd
    b = np.inf if hi is None else (hi - mu) / sd
    Fa = 0.0 if lo is None else Phi(a); Fb = 1.0 if hi is None else Phi(b)
    fa = 0.0 if lo is None else phi(a); fb = 0.0 if hi is None else phi(b)
    return mu + sd * (fa - fb) / (Fb - Fa)


C02_ANCHORS = [  # (nights at which the branch conditional is anchored, conditional vector)
    (branch_mean(None, 9.0, 9.67, 1.70), c02_branch["lt9"]["cond"]),
    (branch_mean(9.0, 10.0, 9.67, 1.70), c02_branch["9to10"]["cond"]),
    (branch_mean(10.0, None, 9.67, 1.70), c02_branch["ge10"]["cond"]),
]

# S01 revision-2 cells: (state, c01_below, c02_cd) -> summary; quantile function rebuilt from the published table
s01_cells = {}
with open(QDIR / "day1-move-5nov/datasets/s01_v2_cells.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        s01_cells[(r["state"], r["c01_below"] == "True", r["c02_cd"] == "True")] = {k: float(v) for k, v in r.items() if k not in ("state", "c01_below", "c02_cd")}


def cell_quantile_fn(c):
    pts = [(-60.0, 0.0), (-40.0, c["below_m40"]), (-25.0, c["p_lt_m25"]), (-15.0, c["p_lt_m15"]),
           (c["p5"], 0.05), (c["p10"], 0.10), (-8.0, c["p_le_m8"]), (-5.0, c["p_le_m5"]), (c["p25"], 0.25), (0.0, c["p_lt_0"]),
           (c["p50"], 0.50), (5.0, 1 - c["p_ge_5"]), (c["p75"], 0.75), (10.0, 1 - c["p_ge_10"]), (c["p90"], 0.90), (c["p95"], 0.95),
           (17.0, 1 - c["p_ge_17"]), (40.0, 1 - c["above_p40"]), (60.0, 1.0)]
    pts.sort()
    xs = np.array([p[0] for p in pts]); Fs = np.maximum.accumulate(np.array([p[1] for p in pts]))
    Fs = Fs + np.arange(len(Fs)) * 1e-9   # break ties for interpolation
    return lambda u: np.interp(u, Fs, xs)


S01_Q = {k: cell_quantile_fn(v) for k, v in s01_cells.items()}

# S02 revision 2: branch 15 Dec medians (decomposition) rescaled so the four-branch mixture reproduces the published final median
s02_run = json.load(open(QDIR / "close-15dec-2026/datasets/mixture_base_run_v2.json", encoding="utf-8"))
s02_blend = json.load(open(QDIR / "close-15dec-2026/datasets/final_blend_v2.json", encoding="utf-8"))
S02_BRANCH_MED = {"accel": s02_run["by_scenario"]["accel (3Q26 nights >= 10.6%)"]["dec_median"],
                  "flat": s02_run["by_scenario"]["flat (10.0-10.6%)"]["dec_median"],
                  "decel_ok": s02_run["by_scenario"]["decel, 4Q26 guide at/above Street"]["dec_median"],
                  "decel_below": s02_run["by_scenario"]["decel, 4Q26 guide below Street"]["dec_median"]}
S02_SCALE = s02_blend["S02"]["percentiles"]["50"] / s02_run["S02_close_15dec"]["percentiles"]["50"]
S02_WITHIN_LOGSD = math.sqrt((0.30 * math.sqrt(62 / 252)) ** 2 + (s02_run["day1_sd_within_pct"] / 100) ** 2)   # diffusion + within-branch event sd
SPOT = s02_run["params"]["spot"]

# ------------------------------------------------------------------ the C02 | nights construction
GRID = np.linspace(4.0, 16.0, 1201)


def c02_base_logits(x):
    """piecewise-linear log-odds in nights through the three C02 rev-2 branch anchors; linear extrapolation, clamped to [6, 14]."""
    xc = np.clip(x, 6.0, 14.0)
    xs = np.array([a[0] for a in C02_ANCHORS])
    L = np.log(np.array([a[1] for a in C02_ANCHORS]))   # (3, 5)
    out = np.empty((len(xc), 5))
    for j in range(5):
        lo = xc <= xs[0]; hi = xc >= xs[2]; mid = ~lo & ~hi
        s0 = (L[1, j] - L[0, j]) / (xs[1] - xs[0]); s2 = (L[2, j] - L[1, j]) / (xs[2] - xs[1])
        out[lo, j] = L[0, j] + s0 * (xc[lo] - xs[0])
        out[hi, j] = L[2, j] + s2 * (xc[hi] - xs[2])
        out[mid, j] = np.interp(xc[mid], xs, L[:, j])
    return out


def fit_c02_factors(target, centre, sd, iters=200):
    """IPF-style column factors so that E_x[P(o | x)] under N(centre, sd) equals the target vector."""
    w = np.exp(-0.5 * ((GRID - centre) / sd) ** 2); w /= w.sum()
    logits = c02_base_logits(GRID)
    f = np.zeros(5)
    for _ in range(iters):
        p = np.exp(logits + f); p /= p.sum(1, keepdims=True)
        m = (w[:, None] * p).sum(0)
        f += np.log(target / m)
    p = np.exp(logits + f); p /= p.sum(1, keepdims=True)
    return f, (w[:, None] * p).sum(0)


def c02_probs(x, f):
    p = np.exp(c02_base_logits(x) + f); return p / p.sum(1, keepdims=True)


def solve_g0(p_c01, tilt, gap_sd, centre, sd):
    w = np.exp(-0.5 * ((GRID - centre) / sd) ** 2); w /= w.sum()
    lo, hi = -10.0, 10.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        pb = sum(w * np.array([Phi(-(mid + tilt * (x - centre)) / gap_sd) for x in GRID]))
        if pb > p_c01:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def c02_split(marg, p_below, orr):
    """p_b, p_a with p_below*p_b + (1-p_below)*p_a = marg and odds(p_b) = orr * odds(p_a) (vectorised bisection)."""
    lo = np.full_like(marg, 1e-9); hi = np.full_like(marg, 1 - 1e-9)
    for _ in range(60):
        pa = 0.5 * (lo + hi)
        pb = orr * pa / (1 - pa + orr * pa)
        tot = p_below * pb + (1 - p_below) * pa
        hi = np.where(tot > marg, pa, hi); lo = np.where(tot > marg, lo, pa)
    pa = 0.5 * (lo + hi)
    return orr * pa / (1 - pa + orr * pa), pa


# ------------------------------------------------------------------ the joint
P = dict(centre=PRINT_CENTRE, sd=PRINT_SD, p_c01=P_C01, gap_sd=3.1, tilt=0.66, or_c02=2.0,
         c02_target=C02_FINAL.copy(), c04_below=C04_GIVEN_BELOW.copy(), c04_not=C04_GIVEN_NOT.copy(),
         c04_d_or_short_print=1.0,          # optional odds multiplier on C04 (d) when the print is <= 8.5 (1.0 = C04 independent of the print given C01)
         short_reading="literal",           # 'literal' (C02 = d) or 'material' (explicit mid-single bucket only)
         precedence="breaker_first",        # or 'short_first'
         short_thr=SHORT_NIGHTS_THR, breaker_thr=THR_R02)


def simulate(p, n=N, seed=SEED):
    rng = np.random.default_rng(seed)
    x = rng.normal(p["centre"], p["sd"], n)                                   # latent 3Q26 nights y/y %
    # C01
    g0 = solve_g0(p["p_c01"], p["tilt"], p["gap_sd"], p["centre"], p["sd"])
    gap = rng.normal(g0 + p["tilt"] * (x - p["centre"]), p["gap_sd"], n)
    below = gap < 0
    # C02 | x, C01
    f, marg = fit_c02_factors(p["c02_target"], p["centre"], p["sd"])
    pc = c02_probs(x, f)                                                       # (n, 5) P(o | x)
    p_cd = pc[:, 2] + pc[:, 3]
    p_below_x = np.array([Phi(-(g0 + p["tilt"] * (xx - p["centre"])) / p["gap_sd"]) for xx in GRID])
    pbx = np.interp(x, GRID, p_below_x)
    pb, pa = c02_split(p_cd, pbx, p["or_c02"])
    cd = rng.random(n) < np.where(below, pb, pa)
    u = rng.random(n)
    d_share = pc[:, 3] / np.maximum(p_cd, 1e-12)                               # within the c/d block
    c02 = np.empty(n, dtype="<U1")
    c02[cd] = np.where(u[cd] < d_share[cd], "d", "c")
    nb = ~cd
    a_share = pc[:, 0] / np.maximum(1 - p_cd, 1e-12); b_share = pc[:, 1] / np.maximum(1 - p_cd, 1e-12)
    c02[nb] = np.where(u[nb] < a_share[nb], "a", np.where(u[nb] < (a_share + b_share)[nb], "b", "e"))
    explicit_d = (c02 == "d") & (rng.random(n) < C02_D_EXPLICIT_SHARE)         # explicit mid-single bucket (vs directional 'moderate')
    # C04 | C01 (optionally tilted on a short print)
    v = np.where(below[:, None], p["c04_below"][None, :], p["c04_not"][None, :]).copy()
    if p["c04_d_or_short_print"] != 1.0:
        sp = x < p["short_thr"]
        od = v[sp, 3] / (1 - v[sp, 3]) * p["c04_d_or_short_print"]; nd = od / (1 + od)
        rest = v[sp][:, [0, 1, 2, 4]]; rest = rest / rest.sum(1, keepdims=True) * (1 - nd)[:, None]
        v[sp, 3] = nd; v[np.ix_(sp, [0, 1, 2, 4])] = rest
    c04 = np.array(C04_OPTS)[(rng.random(n)[:, None] > np.cumsum(v, 1)).sum(1).clip(0, 4)]
    # classification
    accel = x >= p["breaker_thr"]
    breaker = accel & (c02 == "a")
    d_gate = explicit_d if p["short_reading"] == "material" else (c02 == "d")
    short = (x < p["short_thr"]) | d_gate | (c04 == "d")
    base = (~accel) & (np.isin(c02, ["b", "c"]) | below) & ~short
    opt = np.full(n, 3)
    if p["precedence"] == "breaker_first":
        opt[short] = 2; opt[base] = 1; opt[breaker] = 0
    else:
        opt[base] = 1; opt[breaker] = 0; opt[short] = 2
    # S01 day-1 return from the twelve rev-2 cells
    state = np.where(x >= S01_ACCEL_THR, "accel", np.where(x >= S01_DECEL_THR, "flat", "decel"))
    r = np.empty(n)
    uu = rng.random(n)
    for k, qf in S01_Q.items():
        m = (state == k[0]) & (below == k[1]) & (cd == k[2])
        r[m] = qf(uu[m])
    # S02 15 Dec close from the four rev-2 branches
    br = np.where(state == "accel", "accel", np.where(state == "flat", "flat", np.where(below, "decel_below", "decel_ok")))
    med = np.array([S02_BRANCH_MED[b] for b in ("accel", "flat", "decel_ok", "decel_below")])
    bi = np.select([br == "accel", br == "flat", br == "decel_ok"], [0, 1, 2], 3)
    close = np.exp(np.log(med[bi] * S02_SCALE) + S02_WITHIN_LOGSD * rng.standard_normal(n))
    return dict(x=x, below=below, c02=c02, explicit_d=explicit_d, c04=c04, opt=opt, breaker=breaker, short=short, base=base,
                r=r, close=close, state=state, g0=g0, c02_factors=f, c02_marg=marg, accel=accel, cd=cd)


def vec(J):
    return {o: float((J["opt"] == i).mean()) for i, o in enumerate(OPTS)}


def summarise(J):
    out = dict(vector=vec(J))
    tab = {}
    for i, o in enumerate(OPTS):
        m = J["opt"] == i
        rr, cc = J["r"][m], J["close"][m]
        tab[o] = dict(p=round(float(m.mean()), 4), day1_median=round(float(np.median(rr)), 2), day1_mean=round(float(rr.mean()), 2),
                      day1_p_le_m8=round(float((rr <= -8).mean()), 3), day1_p_ge_5=round(float((rr >= 5).mean()), 3), day1_p_lt_0=round(float((rr < 0).mean()), 3),
                      day1_p10=round(float(np.percentile(rr, 10)), 2), day1_p90=round(float(np.percentile(rr, 90)), 2),
                      dec15_median=round(float(np.median(cc)), 1), dec15_mean=round(float(cc.mean()), 1),
                      dec15_p25=round(float(np.percentile(cc, 25)), 1), dec15_p75=round(float(np.percentile(cc, 75)), 1),
                      dec15_p_le_150=round(float((cc <= 150).mean()), 3), dec15_p_ge_180=round(float((cc >= 180).mean()), 3),
                      nights_mean=round(float(J["x"][m].mean()), 2), p_c01_below=round(float(J["below"][m].mean()), 3),
                      c02=[round(float((J["c02"][m] == o2).mean()), 3) for o2 in C02_OPTS],
                      c04=[round(float((J["c04"][m] == o4).mean()), 3) for o4 in C04_OPTS])
    out["scenario_table"] = tab
    out["pw_dec15_close_of_conditional_medians"] = round(float(sum(tab[o]["p"] * tab[o]["dec15_median"] for o in OPTS)), 1)
    out["dec15_unconditional_median"] = round(float(np.median(J["close"])), 1)
    out["dec15_unconditional_mean"] = round(float(J["close"].mean()), 1)
    out["day1_unconditional_median"] = round(float(np.median(J["r"])), 2)
    out["day1_unconditional_p_le_m8"] = round(float((J["r"] <= -8).mean()), 3)
    out["day1_unconditional_p_ge_5"] = round(float((J["r"] >= 5).mean()), 3)
    x = J["x"]
    out["marginal_checks"] = dict(
        print_p_lt_10_0=round(float((x < THR_R01).mean()), 4), print_p_10_0_to_10_6=round(float(((x >= THR_R01) & (x < THR_R02)).mean()), 4),
        print_p_ge_10_6=round(float((x >= THR_R02).mean()), 4), print_p_le_8_5=round(float((x < SHORT_NIGHTS_THR).mean()), 4),
        s01_states=dict(decel=round(float((J["state"] == "decel").mean()), 4), flat=round(float((J["state"] == "flat").mean()), 4), accel=round(float((J["state"] == "accel").mean()), 4)),
        c01_p_below=round(float(J["below"].mean()), 4),
        c01_p_below_given=dict(le_8_5=round(float(J["below"][x < SHORT_NIGHTS_THR].mean()), 3), lt_10_0=round(float(J["below"][x < THR_R01].mean()), 3),
                               s01_decel=round(float(J["below"][J["state"] == "decel"].mean()), 3), s01_flat=round(float(J["below"][J["state"] == "flat"].mean()), 3),
                               s01_accel=round(float(J["below"][J["state"] == "accel"].mean()), 3), ge_10_6=round(float(J["below"][x >= THR_R02].mean()), 3)),
        c02_vector={o: round(float((J["c02"] == o).mean()), 4) for o in C02_OPTS},
        c02_given_state={s: {o: round(float((J["c02"][J["state"] == s] == o).mean()), 3) for o in C02_OPTS} for s in ("decel", "flat", "accel")},
        c02_p_ge_10_0_given_a=round(float((x[J["c02"] == "a"] >= THR_R01).mean()), 3),
        c02_p_lt_9_given_d=round(float((x[J["c02"] == "d"] < 9.0).mean()), 3),
        c02_cd_given_below=round(float(J["cd"][J["below"]].mean()), 3), c02_cd_given_not_below=round(float(J["cd"][~J["below"]].mean()), 3),
        c04_vector={o: round(float((J["c04"] == o).mean()), 4) for o in C04_OPTS},
        c04_d_given_below=round(float((J["c04"][J["below"]] == "d").mean()), 3), c04_d_given_not_below=round(float((J["c04"][~J["below"]] == "d").mean()), 3),
        s01_base_case_cell=round(float(((J["state"] == "decel") & J["below"] & J["cd"]).mean()), 4),
        s01_breaker_cell=round(float(((J["state"] == "accel") & ~J["below"]).mean()), 4),
        c01_g0=round(float(J["g0"]), 3), c02_factors=[round(float(v), 3) for v in J["c02_factors"]])
    # decomposition of the short case and of 'none'
    sm = J["opt"] == 2
    out["short_case_composition"] = dict(
        p=round(float(sm.mean()), 4),
        nights_le_8_5_only=round(float((sm & (x < SHORT_NIGHTS_THR) & (J["c02"] != "d") & (J["c04"] != "d")).mean()), 4),
        c02_d_only=round(float((sm & (x >= SHORT_NIGHTS_THR) & (J["c02"] == "d") & (J["c04"] != "d")).mean()), 4),
        c04_d_only=round(float((sm & (x >= SHORT_NIGHTS_THR) & (J["c02"] != "d") & (J["c04"] == "d")).mean()), 4),
        two_or_more_gates=round(float((sm & (((x < SHORT_NIGHTS_THR).astype(int) + (J["c02"] == "d") + (J["c04"] == "d")) >= 2)).mean()), 4),
        c02_d_directional_moderate_share_of_short=round(float(((J["c02"] == "d") & ~J["explicit_d"] & sm).mean() / sm.mean()), 3),
        breaker_and_short_overlap=round(float((J["breaker"] & J["short"]).mean()), 4),
        short_with_print_ge_10_0=round(float((sm & (x >= THR_R01)).mean()), 4))
    nm = J["opt"] == 3
    out["none_composition"] = dict(
        p=round(float(nm.mean()), 4),
        accel_print_not_a=round(float((nm & J["accel"]).mean()), 4),
        flat_or_decel_c02_a_c01_not_below=round(float((nm & ~J["accel"] & (J["c02"] == "a") & ~J["below"]).mean()), 4),
        flat_or_decel_c02_e_c01_not_below=round(float((nm & ~J["accel"] & (J["c02"] == "e") & ~J["below"]).mean()), 4))
    # joint table option x print state
    states4 = {"<=8.5": x < SHORT_NIGHTS_THR, "8.5-10.0": (x >= SHORT_NIGHTS_THR) & (x < THR_R01), "10.0-10.6": (x >= THR_R01) & (x < THR_R02), ">=10.6": x >= THR_R02}
    out["joint_option_x_print"] = {s: {o: round(float((m & (J["opt"] == i)).mean()), 4) for i, o in enumerate(OPTS)} for s, m in states4.items()}
    out["joint_option_x_c02"] = {o2: {o: round(float(((J["c02"] == o2) & (J["opt"] == i)).mean()), 4) for i, o in enumerate(OPTS)} for o2 in C02_OPTS}
    out["joint_option_x_c01"] = {"below": {o: round(float((J["below"] & (J["opt"] == i)).mean()), 4) for i, o in enumerate(OPTS)},
                                 "not_below": {o: round(float((~J["below"] & (J["opt"] == i)).mean()), 4) for i, o in enumerate(OPTS)}}
    out["joint_option_x_c04"] = {o4: {o: round(float(((J["c04"] == o4) & (J["opt"] == i)).mean()), 4) for i, o in enumerate(OPTS)} for o4 in C04_OPTS}
    return out


# ------------------------------------------------------------------ base rate: the 16 ex-reopening prints classified into the four cells
def base_rate_panel():
    desc = {}
    with open(QDIR / "q4-nights-bucket/datasets/nights_descriptor_vs_printed_and_comp_v2.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            desc[r["print_quarter"]] = r
    rows = []
    with open(ROOT / "data/processed/reverse_dcf/C/C_print_panel.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["sample_ex_reopening"] != "True":
                continue
            q = r["print_quarter"]; short_q = q[5] + "Q" + q[2:4]
            d = desc.get(short_q)
            accel_pts = float(r["nights_yoy_accel_pts"]); below = float(r["guide_below_street"]) == 1.0
            opt2 = d["question_option"] if d else None
            explicit_bucket_d = bool(d and d["guide_type"] == "bucket" and opt2 == "d")
            softened = r["fy_margin_action"] in ("lowered", "softened")   # never in the record
            accel = accel_pts >= 0.25                       # S01 dead band
            deep_decel = accel_pts <= -(10.34 - 8.5)        # analogue of a <= 8.5% print after 10.34%

            def classify(material):
                d_gate = explicit_bucket_d if material else (opt2 == "d")
                breaker = accel and opt2 == "a"
                short = deep_decel or d_gate or softened
                base = (not accel) and (opt2 in ("b", "c") or below) and not short
                if breaker:
                    return "thesis breaker"
                if short:
                    return "short case"
                if base:
                    return "base"
                return "none of the above"
            rows.append(dict(print_quarter=short_q, print_date=r["print_date"], nights_yoy=float(r["nights_yoy_pct"]), accel_pts=accel_pts,
                             descriptor_option=opt2, descriptor_type=(d["guide_type"] if d else None), guide_below_street=below,
                             fy_margin_action=r["fy_margin_action"], ret_1d_raw=float(r["ret_1d_cc_raw_pct"]), ret_1d_excess=float(r["ret_1d_cc_excess_pct"]),
                             cell_literal=classify(False), cell_material=classify(True)))

    def freq(sub, key):
        n = len(sub); return {o: round(sum(1 for r in sub if r[key] == o) / n, 3) for o in OPTS}, n
    windows = {"all_16_3Q22plus": rows, "W1_1Q23plus": [r for r in rows if r["print_date"] >= "2023-05-01"],
               "W2_1Q24plus": [r for r in rows if r["print_date"] >= "2024-05-01"], "bucket_era_3Q25plus": [r for r in rows if r["print_date"] >= "2025-11-01"],
               "november_prints": [r for r in rows if r["print_quarter"].startswith("3Q")]}
    summary = {}
    for wn, sub in windows.items():
        fl, n = freq(sub, "cell_literal"); fm, _ = freq(sub, "cell_material")
        summary[wn] = dict(n=n, literal=fl, material=fm,
                           day1_raw_mean_by_literal_cell={o: (round(float(np.mean([r["ret_1d_raw"] for r in sub if r["cell_literal"] == o])), 2) if any(r["cell_literal"] == o for r in sub) else None) for o in OPTS},
                           day1_raw_mean_by_material_cell={o: (round(float(np.mean([r["ret_1d_raw"] for r in sub if r["cell_material"] == o])), 2) if any(r["cell_material"] == o for r in sub) else None) for o in OPTS})
    return rows, summary


# ------------------------------------------------------------------ run
if __name__ == "__main__":
    J = simulate(P)
    S = summarise(J)
    S["params"] = {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in P.items()}
    S["inputs"] = dict(print=dict(centre=PRINT_CENTRE, sd=PRINT_SD, thr_r01=THR_R01, thr_r02=THR_R02, short_thr=SHORT_NIGHTS_THR),
                       c01=P_C01, c02_final=C02_FINAL.tolist(), c02_anchors=[(round(a, 3), v.round(4).tolist()) for a, v in C02_ANCHORS],
                       c04_given_below=C04_GIVEN_BELOW.tolist(), c04_given_not=C04_GIVEN_NOT.tolist(),
                       s02_branch_medians=S02_BRANCH_MED, s02_scale=round(S02_SCALE, 4), s02_within_logsd=round(S02_WITHIN_LOGSD, 4))
    print("VECTOR:", {k: round(v, 4) for k, v in S["vector"].items()})
    print("marginal checks:", json.dumps(S["marginal_checks"], indent=None))
    print("scenario table:", json.dumps(S["scenario_table"], indent=None))
    print("short composition:", S["short_case_composition"]); print("none composition:", S["none_composition"])
    print("PW 15 Dec (conditional medians):", S["pw_dec15_close_of_conditional_medians"], " unconditional median", S["dec15_unconditional_median"])

    # base rate
    rows, brs = base_rate_panel()
    with open(HERE / "x01_base_rate_panel.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    S["base_rate"] = brs
    print("base rate:", json.dumps(brs, indent=None))

    # sensitivities: single-assumption reruns of the same joint
    sens = []

    def variant(name, seed=SEED, **kw):
        q = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in P.items()}
        q.update(kw)
        Jv = simulate(q, seed=seed); Sv = summarise(Jv)
        d = dict(variant=name, **{o: round(Sv["vector"][o], 4) for o in OPTS}, pw_dec15=Sv["pw_dec15_close_of_conditional_medians"],
                 short_day1_median=Sv["scenario_table"]["short case"]["day1_median"], base_day1_median=Sv["scenario_table"]["base"]["day1_median"],
                 breaker_day1_median=Sv["scenario_table"]["thesis breaker"]["day1_median"])
        sens.append(d); print(d); return Sv
    variant("BASE (revision 1)")
    variant("seed 20260918 (Monte Carlo error)", seed=SEED + 1)
    for c in (9.0, 9.2, 9.9, 10.0):
        variant(f"print centre {c} (sd 1.70)", centre=c)
    for s in (1.475, 2.159):
        variant(f"print sd {s}", sd=s)
    variant("C01 tilt 0.32 %/pt (S01 rev-2 value)", tilt=0.32)
    variant("C01 tilt 1.0 %/pt (steeper)", tilt=1.0)
    variant("C01 P(below) 0.62 (Astra)", p_c01=0.62)
    variant("C01 P(below) 0.82", p_c01=0.82)
    variant("C02 OR 1 (independent of C01 within print)", or_c02=1.0)
    variant("C02 OR 4", or_c02=4.0)
    for dmass, lab in ((0.23, "C02 (d) 0.23, (c) 0.38 (C02 low end)"), (0.36, "C02 (d) 0.36, (c) 0.25 (C02 high end)")):
        t = C02_FINAL.copy(); t[3] = dmass; t[2] = 0.61 - dmass
        variant(lab, c02_target=t)
    ta = C02_FINAL.copy(); ta[0] = 0.13; ta[1] = 0.22; variant("C02 (a) 0.13, (b) 0.22 (base-rate (a))", c02_target=ta)
    ta = C02_FINAL.copy(); ta[0] = 0.24; ta[1] = 0.11; variant("C02 (a) 0.24, (b) 0.11 (breaker language likelier)", c02_target=ta)
    c04_variants = {}
    for dd, lab in ((0.20, "C04 (d) 0.20"), (0.35, "C04 (d) 0.35")):
        cb = C04_GIVEN_BELOW.copy(); cn = C04_GIVEN_NOT.copy()
        k = dd / 0.27
        for arr in (cb, cn):
            arr[3] *= k; rest = np.array([0, 1, 2, 4]); arr[rest] *= (1 - arr[3]) / arr[rest].sum()
        c04_variants[dd] = (cb, cn)
        variant(lab, c04_below=cb, c04_not=cn)
    variant("C04 (d) odds x2 when the print is <= 8.5", c04_d_or_short_print=2.0)
    variant("short case beats thesis breaker (precedence)", precedence="short_first")
    variant("MATERIAL short case: explicit mid-single bucket only (C02 d x 0.39) OR nights <= 8.5 OR C04 (d)", short_reading="material")
    variant("MATERIAL short case AND C04 (d) 0.20", short_reading="material", c04_below=c04_variants[0.20][0], c04_not=c04_variants[0.20][1])
    variant("short nights gate 8.0 (latent < 8.05)", short_thr=8.05)
    variant("short nights gate 9.0 (latent < 9.05)", short_thr=9.05)
    variant("breaker gate 10.0 (R01) instead of 10.6", breaker_thr=THR_R01)
    with open(HERE / "x01_sensitivity.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sens[0].keys())); w.writeheader(); w.writerows(sens)
    S["sensitivity"] = sens

    # joint table csv
    with open(HERE / "x01_joint_table.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["dimension", "level"] + OPTS + ["row_total"])
        for dim in ("joint_option_x_print", "joint_option_x_c01", "joint_option_x_c02", "joint_option_x_c04"):
            for lvl, d in S[dim].items():
                w.writerow([dim.replace("joint_option_x_", ""), lvl] + [d[o] for o in OPTS] + [round(sum(d.values()), 4)])
    with open(HERE / "x01_scenario_table.csv", "w", newline="", encoding="utf-8") as f:
        keys = ["p", "day1_median", "day1_mean", "day1_p10", "day1_p90", "day1_p_le_m8", "day1_p_ge_5", "day1_p_lt_0", "dec15_median", "dec15_mean", "dec15_p25", "dec15_p75", "dec15_p_le_150", "dec15_p_ge_180", "nights_mean", "p_c01_below"]
        w = csv.writer(f); w.writerow(["option"] + keys)
        for o in OPTS:
            w.writerow([o] + [S["scenario_table"][o][k] for k in keys])
    json.dump(S, open(HERE / "x01_joint_summary.json", "w", encoding="utf-8"), indent=1)
    print("written: x01_joint_summary.json, x01_joint_table.csv, x01_scenario_table.csv, x01_sensitivity.csv, x01_base_rate_panel.csv")
