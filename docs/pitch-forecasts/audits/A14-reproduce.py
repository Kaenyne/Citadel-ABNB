"""A14 audit reproduction - B01, B02, B03. stdlib + pandas only; writes nothing."""
from pathlib import Path
from statistics import NormalDist, mean, pstdev
import csv, glob, html, json, math, os, random, re
import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
nd = NormalDist()
N = 300_000


def hdr(s):
    print("\n" + "=" * 8 + " " + s + " " + "=" * 8)


def text(p):
    s = Path(p).read_text(encoding="utf-8", errors="ignore")
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s)
    for a, b in [("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("–", "-"), ("—", "-"), ("\xa0", " ")]:
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s)


# ------------------------------------------------------------------ B01
hdr("B01  letter base rates and the day-1 classes")
recs = list(csv.DictReader(open(Q / "bonus-moderation-language/datasets/"
                                "b01_letter_language_by_print.csv", encoding="utf-8")))
st = sum(int(r["yes_strict"]) for r in recs)
sy = sum(int(r["yes_with_synonyms"]) for r in recs)
w1 = [r for r in recs if r["print_quarter"] not in ("3Q22", "4Q22")]
w2 = [r for r in recs if r["print_quarter"][-2:] in ("24", "25", "26")]
nov = [r for r in recs if r["print_quarter"].startswith("3Q")]
buck = [r for r in recs if "bucket" in r["descriptor_class"]]
print("n %d  strict %d  synonyms %d | W1 %d/%d  W2 %d/%d | November %d/%d | bucket era %d/%d %s"
      % (len(recs), st, sy, sum(int(r["yes_strict"]) for r in w1), len(w1),
         sum(int(r["yes_strict"]) for r in w2), len(w2),
         sum(int(r["yes_strict"]) for r in nov), len(nov),
         sum(int(r["yes_strict"]) for r in buck), len(buck),
         [r["print_quarter"] for r in buck]))
print("  (the log's Sec 5 says the bucket era is 1/4; 1Q26 is not a bucket letter)")
d1 = sorted(float(r["day1_excess_pct"]) for r in recs if int(r["yes_strict"]))
d1s = [float(r["day1_excess_pct"]) for r in recs if int(r["yes_with_synonyms"])]
d1n = [float(r["day1_excess_pct"]) for r in recs if not int(r["yes_strict"])]
print("strict n6  mean %+.2f  MEDIAN %+.2f  P(<=-8) %d/6" % (mean(d1), (d1[2] + d1[3]) / 2,
                                                             sum(v <= -8 for v in d1)))
print("synonym n8 mean %+.2f  P(<=-8) %d/8 | no-language(strict) mean %+.2f"
      % (mean(d1s), sum(v <= -8 for v in d1s), mean(d1n)))
er = pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv")
key = {"1Q": "Q1", "2Q": "Q2", "3Q": "Q3", "4Q": "Q4"}
bad = [r["print_quarter"] for r in recs
       if abs(float(er[er.quarter == "20" + r["print_quarter"][2:] + key[r["print_quarter"][:2]]]
                    .excess_1d_pct.iloc[0]) - float(r["day1_excess_pct"])) > 0.051]
print("day-1 values disagreeing with abnb_earnings_reactions.csv:", bad or "none")

hdr("B01  tree: published, and with the three corrections")


def tn_mean(mu, sd, lo, hi):
    Phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
    phi = lambda z: math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
    a, b = (lo - mu) / sd, (hi - mu) / sd
    return mu + sd * (phi(a) - phi(b)) / (Phi(b) - Phi(a))


def tree(branches, pl):
    p_dir = {">=10": .25, "9-10": .28, "<9": .35}
    p_mod = {">=10": .55, "9-10": .60, "<9": .75}
    bucket = {">=10": dict(a=.45, b=.20, c=.30, d=.05),
              "9-10": dict(a=.08, b=.22, c=.57, d=.13),
              "<9": dict(a=.02, b=.07, c=.50, d=.41)}
    tot, by = 0.0, {}
    opt = dict(a=0., b=0., c=0., d=0., e=0.)
    om = dict(a=0., b=0., c=0., d=0., e=0.)
    for br, m in branches.items():
        pd_, pn = p_dir[br], 0.03
        pb = 1 - pd_ - pn
        dm, do = pd_ * p_mod[br], pd_ * (1 - p_mod[br])
        l = dm * pl["dir_mod"] + do * pl["dir_other"]
        opt["d"] += m * dm * pl["dir_mod"]
        om["d"] += m * dm
        k = "a" if br == ">=10" else "b"
        opt[k] += m * do * pl["dir_other"]
        om[k] += m * do
        for o, w in bucket[br].items():
            l += pb * w * pl["bucket_" + o]
            opt[o] += m * pb * w * pl["bucket_" + o]
            om[o] += m * pb * w
        l += pn * pl["none"]
        opt["e"] += m * pn * pl["none"]
        om["e"] += m * pn
        by[br] = l
        tot += m * l
    return tot, by, opt, om


PL = dict(dir_mod=.85, dir_other=.10, bucket_a=.05, bucket_b=.15,
          bucket_c=.25, bucket_d=.40, none=.30)
M_pub = {">=10": 0.423, "9-10": 0.230, "<9": 0.347}
p10 = 1 - nd.cdf((10 - 9.5) / 1.70)
p9 = nd.cdf((9 - 9.5) / 1.70)
M_v2 = {">=10": round(p10, 3), "9-10": round(1 - p10 - p9, 3), "<9": round(p9, 3)}
print("R01 rev-2 N(9.5,1.70) masses", M_v2, "| B01/C02 still use N(9.67,1.70)", M_pub)
for lab, M, pl in [("published", M_pub, PL),
                   ("R01 rev-2 masses only", M_v2, PL),
                   ("dir_mod .95 only", M_pub, dict(PL, dir_mod=.95)),
                   ("bucket c/d .20/.35 only", M_pub, dict(PL, bucket_c=.20, bucket_d=.35)),
                   ("AUDITOR (all three)", M_v2, dict(PL, dir_mod=.95, bucket_c=.20, bucket_d=.35))]:
    t, by, opt, om = tree(M, pl)
    print("  %-26s P(Yes)=%.4f  P(Yes|d)=%.2f  P(Yes&d)=%.3f  share of Yes %.2f  branches %s"
          % (lab, t, opt["d"] / om["d"], opt["d"], opt["d"] / t,
             " / ".join("%.2f" % by[b] for b in M)))

hdr("B01  impact: the 9.90-vs-9.67 baseline and the kernel double count")
t, by, _, _ = tree(M_pub, PL)
post = {b: M_pub[b] * by[b] / t for b in M_pub}
mns = {">=10": tn_mean(9.67, 1.7, 10, 30), "9-10": tn_mean(9.67, 1.7, 9, 10),
       "<9": tn_mean(9.67, 1.7, -10, 9)}
e_y = sum(post[b] * mns[b] for b in M_pub)
e_u = sum(M_pub[b] * mns[b] for b in M_pub)
print("E[nights|Yes] %.2f ; tree's own unconditional %.2f -> delta %+.2f "
      "(the log uses 9.90 and publishes %.2f)" % (e_y, e_u, e_y - e_u, e_y - 9.90))
t2, by2, _, _ = tree(M_v2, dict(PL, dir_mod=.95, bucket_c=.20, bucket_d=.35))
post2 = {b: M_v2[b] * by2[b] / t2 for b in M_v2}
m2 = {">=10": tn_mean(9.5, 1.7, 10, 30), "9-10": tn_mean(9.5, 1.7, 9, 10),
      "<9": tn_mean(9.5, 1.7, -10, 9)}
d3 = sum(post2[b] * m2[b] for b in M_v2) - sum(M_v2[b] * m2[b] for b in M_v2)
r3, r4, f27 = d3 * 48, 0.6 * d3 * 30, 0.4 * d3 * 158
print("corrected: d3 %+.2f pt | 3Q26 rev %+.1f | 4Q26 rev %+.1f (kernel term dropped; "
      "published -22) | FY27 rev %+.1f (published -38)" % (d3, r3, r4, f27))
print("           FY26 margin %+.2f pp (published -0.2) | FY27 margin %+.2f pp | EPS %+.3f"
      % ((r3 + r4) * (1 - 0.35727) / 14268.1 * 100, f27 * 0.66 / 15828.6 * 100,
         f27 * 0.66 * 0.0014))

hdr("B01  every quoted letter fragment, checked against data/raw/letters")
QUOTES = {
    "3Q22": ["Nights and Experiences Booked growth will moderate slightly relative to Q3 2022"],
    "4Q22": ["nearly as strong as Q4 2022"],
    "1Q23": ["growth in Nights and Experiences Booked in Q2 2023 to be lower than our revenue growth"],
    "2Q23": ["modest sequential increase"],
    "3Q23": ["greater volatility early in Q4",
             "monitoring macroeconomic trends and geopolitical conflicts that may impact travel demand",
             "nights booked growth in Q4 2023 to moderate"],
    "4Q23": ["growth rate of nights booked in Q1 2024 to moderate relative to Q4 2023"],
    "1Q24": ["relatively stable to that of Q1 2024"],
    "2Q24": ["sequential moderation",
             "shorter booking lead times globally and some signs of slowing demand from U.S. guests"],
    "3Q24": ["higher than Q3 2024"],
    "4Q24": ["relatively stable compared to Q1 2024"],
    "1Q25": ["moderate relative to Q1 2025", "relatively softer results",
             "broader economic uncertainties", "broad macro uncertainty"],
    "2Q25": ["relatively stable compared to Q2 2025", "tougher year-over-year comparison",
             "putting pressure on growth rates later in the year"],
    "3Q25": ["mid-single-digit", "challenging Q4 2024 comparison",
             "strength in longer lead time bookings"],
    "4Q25": ["high-single-digit", "moderate increase in ADR"],
    "1Q26": ["slightly decelerate",
             "roughly 100bps headwind related to the conflict in the Middle East",
             "navigating a period of macroeconomic and geopolitical uncertainty"],
    "2Q26": ["low double-digit", "moderate increase in ADR"],
}
LET = {os.path.basename(f)[:4]: f for f in glob.glob("data/raw/letters/*.htm")}
miss = [(q, s) for q, ss in QUOTES.items() for s in ss if s.lower() not in text(LET[q]).lower()]
print("letter fragments checked %d ; not found: %s"
      % (sum(len(v) for v in QUOTES.values()), miss or "none"))

hdr("B01  do any 'no language' letters in fact carry a forward softening phrase?")
PAT = re.compile(r"moderat|lead time|soften|softer|softness|decelerat|macro", re.I)
for q in ["1Q24", "2Q23", "3Q24", "4Q24", "4Q22", "3Q25", "4Q25", "2Q26"]:
    hits = [s.strip() for s in re.split(r"(?<=[.!?]) +", text(LET[q]))
            if PAT.search(s) and "known and unknown risks" not in s and "Adjusted EBITDA is defined" not in s]
    print(" ", q, "|", " || ".join(h[:110] for h in hits[:3]) or "(none)")

# ------------------------------------------------------------------ B03
hdr("B03  cross-question inputs: what is actually on disk")
c04 = json.load(open(Q / "fy26-margin-sentence/forecasts/2026-09-17-forecast.json"))
c09 = json.load(open(Q / "q4-margin-direction-sentence/forecasts/2026-09-17-forecast.json"))
r05 = json.load(open(Q / "risk-q3-margin-sandbagged/forecasts/2026-09-17-forecast.json"))
a04 = [v for k, v in c04["final"]["vector"].items() if k.startswith("(a)")][0]
b04 = [v for k, v in c04["final"]["vector"].items() if k.startswith("(b)")][0]
up09 = [v for k, v in c09["final"]["vector"].items() if k.startswith("(c)")][0]
print("C04 rev%s (a) %.2f (b) %.2f   [B03 quotes 0.26 / 0.42]" % (c04["revision"], a04, b04))
print("C09 rev%s (c) up %.2f          [B03 quotes 0.40]" % (c09["revision"], up09))
print("R05 rev%s p %.2f                [B03 quotes 0.17; R05's RESUME kills its rev-1 "
      "S&M <= $706M / +20.7%% threshold]" % (r05["revision"], r05["final"]["p"]))
for lab, ps in [("B03 as published", (0.40 * 0.30, 0.08, 0.26 * 0.20, 0.04)),
                ("rev-2 inputs, same conditionals", (up09 * 0.30, 0.08, a04 * 0.20, 0.04)),
                ("AUDITOR (.27/.09/.20/.07)", (up09 * 0.27, 0.09, a04 * 0.20, 0.07))]:
    u = 1.0
    for p in ps:
        u *= (1 - p)
    print("  %-32s A %.3f B %.3f C %.3f D %.3f -> union %.3f"
          % (lab, ps[0], ps[1], ps[2], ps[3], 1 - u))
print("anchor: 0.5*C04(a)+0.25*C04(b) = %.3f on rev 2 (published used rev 1 -> %.3f)"
      % (0.5 * a04 + 0.25 * b04, 0.5 * 0.26 + 0.25 * 0.42))
print("stock line: EPS +0.254 x 27x = $%.1f ; the run's 16x EV/EBITDA on +$179M = $%.2f ; "
      "published -$3" % (0.254 * 27, 179 * 16 / 591.7))

hdr("B03  S&M history and the 'eight consecutive quarters' claim")
cl = pd.read_csv(ROOT / "data/processed/abnb_quarterly_costlines.csv").set_index("quarter")
qs = ["3Q22", "4Q22", "1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24", "3Q24", "4Q24",
      "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]
run = 0
for i in range(4, len(qs)):
    a, b = qs[i], qs[i - 4]
    if a not in cl.index or b not in cl.index:
        continue
    s = 100 * (cl.loc[a, "sales_and_marketing_musd"] / cl.loc[b, "sales_and_marketing_musd"] - 1)
    r = 100 * (cl.loc[a, "revenue_musd"] / cl.loc[b, "revenue_musd"] - 1)
    run = run + 1 if s > r else 0
    print("  %s S&M %+6.1f%%  revenue %+6.1f%%  %s (run %d)"
          % (a, s, r, "FASTER" if s > r else "slower", run))
print("  -> the streak is %d quarters, not the eight claim 3 states" % run)

hdr("B03  every forward ADR/marketing guide sentence, from the raw letters")
for f in sorted(glob.glob("data/raw/letters/*.htm")):
    q = os.path.basename(f)[:4]
    if q[-2:] not in ("24", "25", "26"):
        continue
    for s in re.split(r"(?<=[.!?]) +", text(f)):
        if re.search(r"\bADR\b", s) and re.search(r"we expect|we anticipate|estimate that", s, re.I):
            print(" ", q, "|", s[:190])

# ------------------------------------------------------------------ B02
hdr("B02  AR(1) on the residual, and its small-sample bias")
h = pd.read_csv(ROOT / "data/processed/q3nowcast/H/adr_history_components.csv")
r = list(h.residual_pricing_pp.values)
x, y = r[:-1], r[1:]
sx, sy = mean(x), mean(y)
b1 = sum((a - sx) * (c - sy) for a, c in zip(x, y)) / sum((a - sx) ** 2 for a in x)
b0 = sy - b1 * sx
res = [c - (b0 + b1 * a) for a, c in zip(x, y)]
isd = (sum(v * v for v in res) / (len(res) - 2)) ** 0.5
ar1 = b0 + b1 * r[-1]
rho_c = min(0.999, b1 + (1 + 3 * b1) / len(r))
ar1c = (1 - rho_c) * (b0 / (1 - b1)) + rho_c * r[-1]
print("OLS      const %.3f rho %.3f innov %.3f -> 3Q26 point %.3f  (log: 0.750/0.747/0.94/4.37)"
      % (b0, b1, isd, ar1))
print("Kendall  rho %.3f -> 3Q26 point %.3f  (the branch's mean reversion is mostly small-sample bias)"
      % (rho_c, ar1c))
d = [y1 - x1 for x1, y1 in zip(x, y)]
print("residual one-quarter changes: mean %+.3f sd %.3f min %.3f n %d"
      % (mean(d), pstdev(d) * (len(d) / (len(d) - 1)) ** 0.5, min(d), len(d)))

hdr("B02  joint model reproduction and the branches that matter")


def mc(mix_mu=-1.16, mix_sd=0.35, k=0.17, bias=0.15, w=(.45, .15, .25, .15),
       res_=None, wf=(.50, .25, .25), seed=7):
    res_ = res_ or [(4.85, .55), (5.35, .55), (ar1, isd), (3.6, .7)]
    fx = [(-0.43, .33), (0.26, .42), (-1.12, .46)]
    g = random.Random(seed)
    cw = [sum(w[:i + 1]) for i in range(4)]
    cf = [sum(wf[:i + 1]) for i in range(3)]
    out = []
    for _ in range(N):
        m = g.gauss(mix_mu, mix_sd)
        u = g.random()
        i = 0 if u < cw[0] else 1 if u < cw[1] else 2 if u < cw[2] else 3
        rr = g.gauss(*res_[i])
        v = g.random()
        j = 0 if v < cf[0] else 1 if v < cf[1] else 2
        out.append(m + k + rr + g.gauss(*fx[j]) + bias)
    out.sort()
    return out


def rep(lab, s):
    print("  %-44s P(<=2.0)=%.4f  P(>=4.4)=%.4f  med=%.3f  sd=%.3f"
          % (lab, sum(1 for v in s if v <= 2.0) / len(s),
             sum(1 for v in s if v >= 4.4) / len(s), s[len(s) // 2], pstdev(s)))


rep("published joint model (target .119/.172)", mc())
rep("Kendall-corrected AR(1) branch", mc(res_=[(4.85, .55), (5.35, .55), (ar1c, isd), (3.6, .7)]))
rep("mix sd 0.60 (claim 7's own mapping RMSE)", mc(mix_sd=0.60))
rep("bias -0.07 (log's ex-POST decel split)", mc(bias=-0.07))
rep("bias +0.58 (implementable ex-ANTE split)", mc(bias=0.58))
rep("FX weights .76/.12/.12 (empirical rate)", mc(wf=(.76, .12, .12)))
AUD = mc(wf=(.63, .185, .185), mix_sd=0.50,
         res_=[(4.85, .55), (5.35, .55), (4.60, isd), (3.6, .7)])
rep("AUDITOR structural (A14-05, -11, -12 repaired)", AUD)
a_lo = sum(1 for v in AUD if v <= 2.0) / len(AUD)
a_hi = sum(1 for v in AUD if v >= 4.4) / len(AUD)
for m_, s_ in [(3.43, .927), (3.50, 1.00), (3.58, .927), (3.50, 1.05)]:
    print("  gaussian N(%.2f, %.3f): P(<=2.0)=%.4f  P(>=4.4)=%.4f"
          % (m_, s_, nd.cdf((2.0 - m_) / s_), 1 - nd.cdf((4.4 - m_) / s_)))
print("AUDITOR blend 0.55 structural + 0.45 N(3.50,1.00): B02 %.3f  R07 %.3f"
      % (0.55 * a_lo + 0.45 * nd.cdf((2.0 - 3.50) / 1.00),
         0.55 * a_hi + 0.45 * (1 - nd.cdf((4.4 - 3.50) / 1.00))))

hdr("B02  the direction split: ex-post (used) vs ex-ante (implementable)")
p = pd.read_csv(ROOT / "data/processed/adrv3/P/P1_card_v3_backtest_paths.csv")
q = p[(p.target == "t2_reported_usd_yoy") & (p.fx_estimator == "midpoint")].copy()
hist = h.set_index("quarter").adr_yoy_reported_pp
q["prior"] = [hist.get(pq) for pq in ["4Q23", "1Q24", "2Q24", "3Q24", "4Q24",
                                      "1Q25", "2Q25", "3Q25", "4Q25", "1Q26"]]
q["err"] = q.v3_point_last_q_plus_K_line_measured_mix - q.actual
for lab, s in [("EX-POST decel", q[q.actual < q.prior]),
               ("EX-POST accel", q[q.actual >= q.prior]),
               ("EX-ANTE decel", q[q.v3_point_last_q_plus_K_line_measured_mix < q.prior]),
               ("EX-ANTE accel", q[q.v3_point_last_q_plus_K_line_measured_mix >= q.prior])]:
    e = list(s.err)
    se = (sum((v - mean(e)) ** 2 for v in e) / (len(e) - 1)) ** 0.5 / len(e) ** 0.5
    print("  %-14s n %d  mean %+.3f  rmse %.3f  SE %.3f  %s"
          % (lab, len(e), mean(e), (sum(v * v for v in e) / len(e)) ** 0.5, se, list(s.quarter)))
print("  pooled bias %+.3f ; 3Q26 is an ex-ante decel quarter (model 3.4 vs 2Q26 actual %.2f)"
      % (mean(q.err), hist["2Q26"]))

hdr("B02  reference classes, re-counted")
print("reported <= 2.0: %d of %d" % (int((h.adr_yoy_reported_pp <= 2.0).sum()), len(h)))
print("FX >= -0.5: %d quarters (log says 7); of those <= 2.0: %d"
      % (int((h.fx_effect_pp >= -0.5).sum()),
         int(((h.fx_effect_pp >= -0.5) & (h.adr_yoy_reported_pp <= 2.0)).sum())))
print("residual >= 3.50: %d quarters -> <= 2.0 in %d"
      % (int((h.residual_pricing_pp >= 3.5).sum()),
         int(((h.residual_pricing_pp >= 3.5) & (h.adr_yoy_reported_pp <= 2.0)).sum())))
print("residual >= 3.45 (1Q23 rounded in, as the log's parenthesis does): %d -> <= 2.0 in %d"
      % (int((h.residual_pricing_pp >= 3.45).sum()),
         int(((h.residual_pricing_pp >= 3.45) & (h.adr_yoy_reported_pp <= 2.0)).sum())))

hdr("B02  is the FX branch calibrated? (17 quarters of disclosed FX)")
fxq = pd.read_csv(ROOT / "data/processed/adrv3/N/N1_fx_estimator_by_quarter.csv")
spread = (fxq.est_from_eur - fxq.est_from_regional_baskets).abs()
e = fxq.err_est_from_midpoint          # estimate - disclosed
print("euro-baskets spread: mean %.3f max %.3f (%s) ; 3Q26's 1.38 is outside the range"
      % (spread.mean(), spread.max(), fxq.quarter_h[spread.idxmax()]))
print("midpoint |err| mean %.3f max %.3f ; corr(|err|, spread) = %+.3f "
      "(the error does NOT widen when the estimators disagree)"
      % (e.abs().mean(), e.abs().max(), e.abs().corr(spread)))
print("a disclosed FX <= -1.0 needs err >= +0.69pp: that happened in %d of %d = %.3f "
      "(Laplace %.3f) ; the mixture puts 0.171 there"
      % (int((e >= 0.69).sum()), len(e), (e >= 0.69).mean(), 2 / (len(e) + 2)))
print("disclosed outside the eur-baskets interval (|err| >= spread/2): %d of %d ; "
      "signed >= +spread/2: %d of %d"
      % (int((e.abs() >= spread / 2).sum()), len(e), int((e >= spread / 2).sum()), len(e)))

hdr("B02 / R07  impact: a level shift is not a growth shift")
v = pd.read_csv(ROOT / "data/processed/margin_build/23_final_model/23_vs_consensus.csv").set_index("period")
fy26, fy27 = float(v.loc["FY26", "model_revenue_musd"]), float(v.loc["FY27", "model_revenue_musd"])
g0 = 100 * (fy27 / fy26 - 1)
for lab, d26, d27, pub in [("B02 Yes", -145.0, -302.0, 12.0), ("R07 Yes", 125.0, 260.0, 10.0)]:
    g1 = 100 * ((fy27 + d27) / (fy26 + d26) - 1)
    mult = abs(g1 - g0) * 0.44 * 9.5
    lev = abs(d27) * 16 / 591.7
    print("  %s: FY27 growth %.2f%% -> %.2f%% (delta %+.2f pt; the log assumes 1.9 / 1.65)"
          % (lab, g0, g1, g1 - g0))
    print("     multiple $%.2f + level $%.2f = $%.2f ; x0.70 = $%.2f  (published $%.0f)"
          % (mult, lev, mult + lev, (mult + lev) * 0.70, pub))

hdr("B02  MODL anchor")
ed = pd.read_csv(ROOT / "data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv")
a = ed[(ed.quarter == "3Q26") & (ed.metric == "adr_usd")].iloc[0]
sd = (a.street_high_growth - a.street_low_growth) / 4
print("n %d low/mean/high %.3f / %.3f / %.3f ; range/4 sd %.3f -> P(<=2.0) %.4f ; "
      "at RMSE 0.927 %.4f ; 174.72 at %.1f%% of range"
      % (a.n_estimates, a.street_low_growth, a.street_mean_growth, a.street_high_growth, sd,
         nd.cdf((2.0 - a.street_mean_growth) / sd), nd.cdf((2.0 - a.street_mean_growth) / 0.927),
         100 * (174.72 - a.street_low) / (a.street_high - a.street_low)))
