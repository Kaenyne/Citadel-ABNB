"""C08 q3-revenue-fx-integer, revision 2 (audit response to A05). Reads the revision-1 basket rebuild
(c08_basket_rebuild.csv, FRED through 2026-09-11) and recomputes the letter-integer vector with:
  * the management component widened to sd 1.0 (A05-02: the 4Q22 letter guided 1Q23 FX at -2 and the print was -4;
    numeric-only record n 4, errors -2 / +1 / 0 / +1, mean 0.0, sample sd 1.41; net of the two-integer rounding ~1.35);
  * every model component carrying its OWN point-in-time error (A05-05): H2 on ADR-FX RMSE 0.99 / interval 0.58 (n 10),
    H2b on the basket W2 RMSE 1.32 / interval 0.99, H3 free fit W2 1.82 / 1.43, H0 contemporaneous W2 1.97 / 1.54
    (fx_lag_v2/09c). The point RMSE contains the +-0.5 letter rounding that the kernel adds again, and the interval RMSE
    strips it entirely, so each component sd is the midpoint of the two;
  * sensitivities that hold the mixture weights fixed (A05-04) and a dollar scenario with the right sign;
  * tail probabilities from the same model (A05-15), analytic (triangular kernel) with an MC check.
Run from the repo root:  py -3.13 docs/pitch-forecasts/questions/q3-revenue-fx-integer/datasets/c08_model_v2.py
Writes c08_v2_components.csv, c08_v2_sensitivity.csv, c08_v2_track_record.csv, c08_v2_summary.json.
"""
from pathlib import Path
import json, math
import numpy as np, pandas as pd
from statistics import NormalDist

HERE = Path(__file__).resolve().parent
ND = NormalDist()

reb = pd.read_csv(HERE / "c08_basket_rebuild.csv").set_index("quarter")
b0 = float(reb.loc["3Q26", "global_spot_held"]); b1 = float(reb.loc["2Q26", "global_spot_held"]); b2 = float(reb.loc["1Q26", "global_spot_held"])
phi = (2 / 3) * b1 + (1 / 3) * b2
free_fit = 0.45 * b0 + 0.36 * b1 + 0.03 * b2
contemp = 0.56 * b0 - 0.21
H2_ADRFX = 0.7313 * ((2 / 3) * 1.3 + (1 / 3) * 5.0)     # registered spec, PIT point 1.8527
PHI_0653 = 0.653 * phi                                    # 2.22
PHI_0851 = 0.851 * phi                                    # 2.90
H2B = 0.8807 * phi                                        # 3.00

# ---- analytic triangular rounding kernel: P(integer >= k | f ~ N(mu, sd)) = E[(F-(k-1))+] - E[(F-k)+] ----
def pos_part(mu, sd, a):
    z = (mu - a) / sd
    return (mu - a) * ND.cdf(z) + sd * math.exp(-z * z / 2) / math.sqrt(2 * math.pi)

def p_int_ge(mu, sd, k):
    return pos_part(mu, sd, k - 1) - pos_part(mu, sd, k)

def vec(mu, sd):
    a = p_int_ge(mu, sd, 3); b = p_int_ge(mu, sd, 2) - a
    return dict(p_ge3=a, p_eq2=b, p_le1=1 - a - b, p_ge4=p_int_ge(mu, sd, 4), p_le0=1 - p_int_ge(mu, sd, 1), p_neg=1 - p_int_ge(mu, sd, 0))

def mc_check(mu, sd, n=400_000, seed=5):
    r = np.random.default_rng(seed); f = r.normal(mu, sd, n); g = r.uniform(11, 15, n); k = np.round(g + f) - np.round(g)
    return dict(p_ge3=(k >= 3).mean(), p_eq2=(k == 2).mean(), p_le1=(k <= 1).mean())

# ---- revision-2 components: (label, centre, sd, weight) ----
# sd rule: management = numeric-pair record widened to 1.0 (pre-registered in the rev-1 RESUME); models = midpoint of the
# point RMSE and the interval RMSE of the spec's own PIT record (W2 for basket specs; H2 has one record)
MIX = [
    ("management guide ~3 (6 Aug letter); numeric-pair record n 4, errors -2/+1/0/+1", 3.0, 1.00, 0.38),
    ("Phi x 0.851 / H2b on the basket (2.9-3.0); H2b W2 RMSE 1.32, interval 0.99", PHI_0851, 1.15, 0.20),
    ("H2 on disclosed ADR-FX (registered, 1.85) / Phi x 0.653 (2.2) / WS05 (1.98); H2 RMSE 0.99, interval 0.58", 2.05, 0.80, 0.27),
    ("Object-A free fit, stated weights on the spot-held basket (1.26); H3 W2 RMSE 1.82, interval 1.43", free_fit, 1.60, 0.12),
    ("contemporaneous x 0.56 less hedge (0.13); H0 W2 RMSE 1.97, interval 1.54", contemp, 1.75, 0.03),
]
P_NS = 0.02

def mixture(mix, pns=P_NS):
    acc = {k: 0.0 for k in ("p_ge3", "p_eq2", "p_le1", "p_ge4", "p_le0", "p_neg")}
    for lab, mu, sd, w in mix:
        v = vec(mu, sd)
        for k in acc: acc[k] += w * v[k]
    wsum = sum(m[3] for m in mix)
    out = {k: v / wsum * (1 - pns) for k, v in acc.items()}
    out["d_not_stated"] = pns; out["weight_sum"] = wsum
    return out

rows = []
for lab, mu, sd, w in MIX:
    v = vec(mu, sd); m = mc_check(mu, sd)
    rows.append(dict(component=lab, centre=round(mu, 3), sd=sd, weight=w, **{k: round(x, 4) for k, x in v.items()},
                     mc_p_ge3=round(m["p_ge3"], 4), mc_p_eq2=round(m["p_eq2"], 4), mc_p_le1=round(m["p_le1"], 4)))
base = mixture(MIX)
rows.append(dict(component="MIXTURE rev 2 (x 0.98) + 0.02 not stated", centre=None, sd=None, weight=1.0,
                 **{k: round(base[k], 4) for k in ("p_ge3", "p_eq2", "p_le1", "p_ge4", "p_le0", "p_neg")}))
comp = pd.DataFrame(rows); comp.to_csv(HERE / "c08_v2_components.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
print(comp.to_string())
print("\nREV-2 VECTOR a/b/c/d:", round(base["p_ge3"], 3), round(base["p_eq2"], 3), round(base["p_le1"], 3), P_NS,
      "sum", round(base["p_ge3"] + base["p_eq2"] + base["p_le1"] + P_NS, 4),
      "| within: P(>=4)", round(base["p_ge4"], 3), "P(<=0)", round(base["p_le0"], 3), "P(<0)", round(base["p_neg"], 3))

# ---- sensitivities: weights held fixed unless the row says otherwise; every row sums to 1 ----
sens = []
def add(label, mix, pns=P_NS):
    m = mixture(mix, pns)
    sens.append(dict(assumption=label, a_ge3=round(m["p_ge3"], 3), b_eq2=round(m["p_eq2"], 3), c_le1=round(m["p_le1"], 3),
                     d_not_stated=pns, p_ge4=round(m["p_ge4"], 3), vector_sum=round(m["p_ge3"] + m["p_eq2"] + m["p_le1"] + pns, 4)))
def with_(i, **kw):
    out = []
    for j, (lab, mu, sd, w) in enumerate(MIX):
        if j == i: out.append((lab, kw.get("mu", mu), kw.get("sd", sd), kw.get("w", w)))
        else: out.append((lab, mu, sd, w))
    return out
def reweight(w0):   # management weight w0, others rescaled to 1 - w0
    rest = 1 - MIX[0][3]
    return [(MIX[0][0], MIX[0][1], MIX[0][2], w0)] + [(l, m, s, w * (1 - w0) / rest) for l, m, s, w in MIX[1:]]

add("BASE rev 2", MIX)
add("rev-1 sds restored (0.6/0.6/0.7/0.7/0.7), rev-2 weights", [(l, m, s0, w) for (l, m, s, w), s0 in zip(MIX, [0.6, 0.6, 0.7, 0.7, 0.7])])
add("management sd 0.6 (rev 1)", with_(0, sd=0.6))
add("management sd 1.35 (numeric-pair sd net of rounding, no hedge-regime discount)", with_(0, sd=1.35))
add("management centre 3.5 (2Q26-style overshoot), weights fixed", with_(0, mu=3.5))
add("management centre 2.6 (approximately three was a rounded 2.6), weights fixed", with_(0, mu=2.6))
add("management weight 0.50, others rescaled", reweight(0.50))
add("management weight 0.25, others rescaled", reweight(0.25))
add("management weight 0.15, others rescaled", reweight(0.15))
add("model-only (management weight 0)", [(l, m, s, w) for l, m, s, w in MIX[1:]])
add("kernel view only: management 0.6 + Phi x 0.851 0.4", [MIX[0][:3] + (0.6,), MIX[1][:3] + (0.4,)])
add("short-lag view only: free fit 0.6 + contemporaneous 0.4", [MIX[3][:3] + (0.6,), MIX[4][:3] + (0.4,)])
add("middle cluster only (H2 / Phi x 0.653)", [MIX[2][:3] + (1.0,)])
add("all sds x 1.5", [(l, m, s * 1.5, w) for l, m, s, w in MIX])
add("all sds x 0.75", [(l, m, s * 0.75, w) for l, m, s, w in MIX])
add("not-stated 5%", MIX, pns=0.05)
# dollar scenarios: 79% of the quarter observed at 11 Sep (73 of 92 days); a 5% move over the remaining 21% shifts the
# quarter-average basket y/y by 0.21 x 5 = 1.05pp. Basket is USD per unit: + = weaker dollar. Only lag-0 loadings move.
d = 0.21 * 5.0
add("dollar -5% (weaker) for the rest of the quarter: basket +1.05pp on lag-0 terms only, weights fixed",
    [MIX[0], MIX[1], MIX[2], (MIX[3][0], free_fit + 0.45 * d, MIX[3][2], MIX[3][3]), (MIX[4][0], contemp + 0.56 * d, MIX[4][2], MIX[4][3])])
add("dollar +5% (stronger) for the rest of the quarter: basket -1.05pp on lag-0 terms only, weights fixed",
    [MIX[0], MIX[1], MIX[2], (MIX[3][0], free_fit - 0.45 * d, MIX[3][2], MIX[3][3]), (MIX[4][0], contemp - 0.56 * d, MIX[4][2], MIX[4][3])])
add("hedge reclassification surprise -0.6pp on every component (designated notional kept growing)", [(l, m - 0.6, s, w) for l, m, s, w in MIX])
add("Astra comparison: management N(3,1) 0.50 / H2 N(1.8527,0.9936) 0.25 / H2b N(2.9960,1.3155) 0.25",
    [("mgmt", 3.0, 1.0, 0.50), ("H2", 1.8527, 0.9936, 0.25), ("H2b", 2.9960, 1.3155, 0.25)])
add("Astra weights with rev-2 sds (H2 0.80, H2b 1.15)", [("mgmt", 3.0, 1.0, 0.50), ("H2", 1.8527, 0.80, 0.25), ("H2b", 2.9960, 1.15, 0.25)])
s = pd.DataFrame(sens); s.to_csv(HERE / "c08_v2_sensitivity.csv", index=False); print("\n" + s.to_string())
assert (s.vector_sum.sub(1).abs() < 1e-6).all()

# ---- track record, revision 2: explicit numeric guides separated from analyst-coded qualitative phrases ----
track = pd.DataFrame([
    dict(guide_letter="4Q22", target="1Q23", cls="numeric", guided="16-21% growth, on an ex-FX basis between 18% and 23% -> FX -2", guided_num=-2.0, printed=-4, coding_note="explicit; printed 20% / 24% ex-FX"),
    dict(guide_letter="2Q23", target="3Q23", cls="qualitative", guided="14-18% growth, a few points lower excluding the impact of FX", guided_num=2.5, printed=4, coding_note="a few coded 2-3; judgement"),
    dict(guide_letter="3Q23", target="4Q23", cls="ambiguous", guided="12-14% growth, relatively stable growth compared to Q3 2023 excluding the impact of FX", guided_num=np.nan, printed=3, coding_note="rev 1 coded +2; the natural reading (4Q23 ex-FX ~ 3Q23 ex-FX 14%, reported 12-14) gives -1 to 0; not uniquely specified; dropped (A05-02)"),
    dict(guide_letter="1Q24", target="2Q24", cls="ambiguous", guided="significant sequential headwind ... Easter, Leap Day, and the impact of FX rate changes", guided_num=np.nan, printed=0, coding_note="combined headwind; FX share not specified; dropped (A05-02)"),
    dict(guide_letter="2Q24", target="3Q24", cls="qualitative", guided="inclusive of a modest foreign exchange headwind", guided_num=-0.5, printed=0, coding_note="modest coded -0.5; judgement"),
    dict(guide_letter="3Q24", target="4Q24", cls="qualitative", guided="inclusive of a modest foreign exchange tailwind", guided_num=0.5, printed=0, coding_note="modest coded +0.5; judgement"),
    dict(guide_letter="4Q24", target="1Q25", cls="numeric", guided="4-6% growth, or 7% to 9% excluding the impact of FX -> FX -3", guided_num=-3.0, printed=-2, coding_note="explicit; printed 6% / 8% ex-FX"),
    dict(guide_letter="2Q25", target="3Q25", cls="qualitative", guided="minimal foreign exchange impact after factoring in our hedging program", guided_num=0.0, printed=0, coding_note="minimal coded 0"),
    dict(guide_letter="3Q25", target="4Q25", cls="qualitative", guided="a small foreign exchange tailwind after factoring in our hedging program", guided_num=0.5, printed=1, coding_note="small coded +0.5"),
    dict(guide_letter="4Q25", target="1Q26", cls="numeric", guided="an approximate three point foreign exchange tailwind after factoring in our hedging program", guided_num=3.0, printed=3, coding_note="explicit"),
    dict(guide_letter="1Q26", target="2Q26", cls="numeric", guided="an approximate 3% FX tailwind after factoring in our hedging program", guided_num=3.0, printed=4, coding_note="explicit"),
    dict(guide_letter="2Q26", target="3Q26", cls="numeric", guided="an approximate three percentage point FX tailwind after factoring in our hedging program", guided_num=3.0, printed=np.nan, coding_note="live"),
])
track["error"] = track.printed - track.guided_num
track.to_csv(HERE / "c08_v2_track_record.csv", index=False)
num = track[(track.cls == "numeric") & track.printed.notna()]
qual = track[(track.cls == "qualitative") & track.printed.notna()]
allc = pd.concat([num, qual])
w2 = num[num.target.str[-2:].astype(int) >= 24]
summ = dict(
    numeric_n=int(len(num)), numeric_errors=num.error.tolist(), numeric_mean=float(num.error.mean()), numeric_sd=float(num.error.std(ddof=1)),
    numeric_ge_guide=int((num.error >= 0).sum()), numeric_within_half=int((num.error.abs() <= 0.5).sum()),
    numeric_sd_net_of_rounding=float(math.sqrt(max(num.error.var(ddof=1) - 1 / 6, 0))),
    qualitative_n=int(len(qual)), qualitative_errors=qual.error.tolist(), qualitative_mean=float(qual.error.mean()), qualitative_sd=float(qual.error.std(ddof=1)),
    all_coded_n=int(len(allc)), all_coded_mean=float(allc.error.mean()), all_coded_sd=float(allc.error.std(ddof=1)), all_ge_guide=int((allc.error >= 0).sum()),
    numeric_W1_ge=f"{int((num.error >= 0).sum())}/{len(num)}", numeric_W2_ge=f"{int((w2.error >= 0).sum())}/{len(w2)}",
)
print("\nTRACK RECORD v2:", json.dumps(summ, indent=1))
out = dict(basket=dict(b0_3q26_spot_held=b0, b1_2q26=b1, b2_1q26=b2, phi=phi), spec_points=dict(free_fit=free_fit, contemp=contemp, h2_adrfx=H2_ADRFX, phi_0653=PHI_0653, phi_0851=PHI_0851, h2b=H2B),
           vector=dict(a_ge_plus3=round(base["p_ge3"], 3), b_plus2=round(base["p_eq2"], 3), c_le_plus1=round(base["p_le1"], 3), d_not_stated=P_NS),
           within=dict(p_ge_plus4=round(base["p_ge4"], 3), p_le_0=round(base["p_le0"], 3), p_negative=round(base["p_neg"], 3)), track=summ)
(HERE / "c08_v2_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
