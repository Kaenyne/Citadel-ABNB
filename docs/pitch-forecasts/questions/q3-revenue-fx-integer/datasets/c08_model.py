"""C08 q3-revenue-fx-integer: rebuild the revenue-weighted currency basket on FRED data through the latest
H.10 print, recompute every live 3Q26 revenue-FX construction, and turn a mixture of those constructions into a
probability vector over the letter integer {>=+3, +2, <=+1, not stated}.

Run from the repo root:  py -3.13 docs/pitch-forecasts/questions/q3-revenue-fx-integer/datasets/c08_model.py
numpy/pandas only. Seeded. Reads the FRED pull saved in ../sources/ (fred_fx_daily_*.csv) and the fx_lag_v2
basket weights (data/processed/forecast_methods/fx_lag_v2/01b_basket_weights_used.csv, 02_basket_quarterly.csv).
Writes c08_basket_rebuild.csv, c08_spec_points.csv, c08_integer_mc.csv, c08_sensitivity.csv, c08_guide_track_record.csv.

Letter-integer rule (resolution fine print): the stated points, or round(reported growth) - round(ex-FX growth).
Airbnb prints both growth rates as integers, so a true contribution f maps to integer k with
P(k) = max(0, 1 - |f - k|) when the ex-FX growth's fractional part is uniform (triangular rounding kernel).
"""
from pathlib import Path
import glob, numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SRC = HERE.parent / "sources"
rng = np.random.default_rng(20260917)

# ---- 1. basket rebuild ------------------------------------------------------------------------------------
fx_file = sorted(glob.glob(str(SRC / "fred_fx_daily_*.csv")))[-1]
fx = pd.read_csv(fx_file, parse_dates=["date"])
fx = fx[fx.ccy != "USD_BROAD"].copy()
last_obs = fx.date.max()
w = pd.read_csv(ROOT / "data/processed/forecast_methods/fx_lag_v2/01b_basket_weights_used.csv")
bq = pd.read_csv(ROOT / "data/processed/forecast_methods/fx_lag_v2/02_basket_quarterly.csv")
rev_w = bq.set_index("quarter").loc["3Q26", ["w_na", "w_emea", "w_latam", "w_apac"]].values  # trailing-4 filed shares

def quarter_avg(df, qend_fill=None):
    d = df.copy()
    if qend_fill is not None:      # hold spot from the last observation to the quarter end (business days)
        add = []
        for ccy, g in d.groupby("ccy"):
            lastv = g.sort_values("date").usd_per_unit.iloc[-1]
            days = pd.bdate_range(last_obs + pd.Timedelta(days=1), qend_fill)
            add.append(pd.DataFrame({"date": days, "ccy": ccy, "usd_per_unit": lastv}))
        d = pd.concat([d[["date", "ccy", "usd_per_unit"]]] + add)
    d["q"] = d.date.dt.to_period("Q")
    return d.groupby(["ccy", "q"]).usd_per_unit.mean().unstack(0)

def basket_yoy(qavg):
    yoy = (qavg / qavg.shift(4) - 1) * 100   # currency y/y, % (USD per unit; + = weaker dollar)
    out = {}
    for reg in ["na", "emea", "latam", "apac"]:
        ww = w[w.region == reg]
        val = 0.0
        for _, r in ww.iterrows():
            if r.ccy_used == "USD":
                continue
            val += r.weight * yoy[r.ccy_used]
        out[reg] = val
    b = pd.DataFrame(out)
    b["global"] = b[["na", "emea", "latam", "apac"]].values @ rev_w
    return b

q_qtd = quarter_avg(fx)                                       # 3Q26 = quarter-to-date average
q_held = quarter_avg(fx, qend_fill=pd.Timestamp("2026-09-30"))  # 3Q26 = QTD + spot held
b_qtd, b_held = basket_yoy(q_qtd), basket_yoy(q_held)
rows = []
for q in ["1Q26", "2Q26", "3Q26"]:
    per = pd.Period(f"20{q[2:]}Q{q[0]}")
    rows.append(dict(quarter=q, global_qtd=b_qtd.loc[per, "global"], global_spot_held=b_held.loc[per, "global"],
                     na=b_held.loc[per, "na"], emea=b_held.loc[per, "emea"], latam=b_held.loc[per, "latam"], apac=b_held.loc[per, "apac"],
                     published_fx_lag_v2_to_4sep=float(bq.set_index("quarter").loc[q, "basket_global_rev_wtd_yoy_pct"]),
                     fx_data_through=str(last_obs.date())))
rebuild = pd.DataFrame(rows); rebuild.to_csv(HERE / "c08_basket_rebuild.csv", index=False)
print(rebuild.round(3).to_string())
b1, b2 = rebuild.set_index("quarter").loc["2Q26", "global_spot_held"], rebuild.set_index("quarter").loc["1Q26", "global_spot_held"]
b0 = rebuild.set_index("quarter").loc["3Q26", "global_spot_held"]
phi = (2/3) * b1 + (1/3) * b2

# ---- 2. spec points (after-hedge basis where the target is the stated series) -------------------------------
ADRFX_2Q26, ADRFX_1Q26 = 1.3, 5.0     # disclosed ADR-FX points, 2Q26 and 1Q26 letters
specs = pd.DataFrame([
    dict(spec="management guide, 6 Aug 2026 letter ('approximately three percentage points ... after hedging')", point=3.0, basis="stated"),
    dict(spec="Phi (0,2/3,1/3) x 0.851 on the basket (B4 adopted construction)", point=0.851 * phi, basis="stated"),
    dict(spec="H2b Phi on basket, PIT coefficient 0.8807 (fx_lag_v2 09b, 6 Aug guide date)", point=0.8807 * phi, basis="stated"),
    dict(spec="Phi x 0.653 on the basket (scale fitted to the Phi shape, stated series)", point=0.653 * phi, basis="stated"),
    dict(spec="H2 Phi on disclosed ADR-FX, PIT coefficient 0.7313 (the registered spec)", point=0.7313 * ((2/3) * ADRFX_2Q26 + (1/3) * ADRFX_1Q26), basis="stated"),
    dict(spec="Phi on disclosed ADR-FX at scale 1 (reading A), less 0.21pp hedge", point=((2/3) * ADRFX_2Q26 + (1/3) * ADRFX_1Q26) - 0.21, basis="stated"),
    dict(spec="WS05/B lagged EUR-broad fit, after hedge (overnight2 B table 2.4)", point=1.98, basis="stated"),
    dict(spec="Object-A free fit, stated weights (0.45, 0.36, 0.03) on spot-held basket", point=0.45 * b0 + 0.36 * b1 + 0.03 * b2, basis="stated"),
    dict(spec="contemporaneous x 0.56 (spot-held basket), less 0.21pp hedge", point=0.56 * b0 - 0.21, basis="stated"),
])
specs["implied_integer"] = specs.point.round().astype(int)
specs.to_csv(HERE / "c08_spec_points.csv", index=False)
print(specs.round(2).to_string())

# ---- 3. integer distribution by Monte Carlo ------------------------------------------------------------------
def integer_probs(centre, sd, n=400_000, seed=1):
    r = np.random.default_rng(seed)
    f = r.normal(centre, sd, n)                  # true after-hedge contribution
    g = r.uniform(11.0, 15.0, n)                 # ex-FX growth; only its fractional part matters
    k = np.round(g + f) - np.round(g)            # the letter integer
    return dict(p_ge3=(k >= 3).mean(), p_eq2=(k == 2).mean(), p_le1=(k <= 1).mean(), p_ge4=(k >= 4).mean(), mean_f=f.mean())

# mixture over constructions: weights are the log's judgement (section 5 of the research log)
mix = [
    ("management guide ~3 (booking-ledger information; 2/2 numeric guides printed >= the guided integer)", 3.0, 0.60, 0.30),
    ("Phi x 0.851 / H2b basket (2.9-3.0)", 0.851 * phi, 0.60, 0.20),
    ("Phi x 0.653 / WS05 lagged / H2 PIT on ADR-FX (1.85-2.2)", 2.05, 0.70, 0.30),
    ("free fit, stated (1.3)", 0.45 * b0 + 0.36 * b1 + 0.03 * b2, 0.70, 0.15),
    ("contemporaneous x 0.56 (0.1)", 0.56 * b0 - 0.21, 0.70, 0.05),
]
P_NOT_STATED = 0.02
acc = dict(p_ge3=0, p_eq2=0, p_le1=0, p_ge4=0); out = []
for i, (lab, c, sd, wt) in enumerate(mix):
    pr = integer_probs(c, sd, seed=10 + i)
    out.append(dict(component=lab, centre=round(c, 2), sd=sd, weight=wt, **{k: round(v, 3) for k, v in pr.items()}))
    for k in acc: acc[k] += wt * pr[k]
vec = {"a_ge_plus3": acc["p_ge3"] * (1 - P_NOT_STATED), "b_plus2": acc["p_eq2"] * (1 - P_NOT_STATED),
       "c_le_plus1": acc["p_le1"] * (1 - P_NOT_STATED), "d_not_stated": P_NOT_STATED}
out.append(dict(component="MIXTURE (x (1 - P_not_stated))", centre=None, sd=None, weight=1.0,
                p_ge3=round(vec["a_ge_plus3"], 3), p_eq2=round(vec["b_plus2"], 3), p_le1=round(vec["c_le_plus1"], 3),
                p_ge4=round(acc["p_ge4"] * (1 - P_NOT_STATED), 3), mean_f=None))
mc = pd.DataFrame(out); mc.to_csv(HERE / "c08_integer_mc.csv", index=False)
print(mc.to_string()); print("VECTOR", {k: round(v, 3) for k, v in vec.items()}, "sum", round(sum(vec.values()), 3))

# ---- 4. sensitivities ---------------------------------------------------------------------------------------
sens = []
def add(label, mixture, pns=P_NOT_STATED):
    a = dict(p_ge3=0, p_eq2=0, p_le1=0)
    for i, (lab, c, sd, wt) in enumerate(mixture):
        pr = integer_probs(c, sd, seed=100 + i)
        for k in a: a[k] += wt * pr[k]
    sens.append(dict(assumption=label, a_ge3=round(a["p_ge3"] * (1 - pns), 3), b_eq2=round(a["p_eq2"] * (1 - pns), 3),
                     c_le1=round(a["p_le1"] * (1 - pns), 3), d_not_stated=pns))
add("BASE mixture", mix)
add("management + Phi x 0.851 only (kernel view)", [(m[0], m[1], m[2], 0.6) for m in mix[:1]] + [(mix[1][0], mix[1][1], mix[1][2], 0.4)])
add("short-lag view only (free fit 0.6, contemporaneous 0.4)", [(mix[3][0], mix[3][1], mix[3][2], 0.6), (mix[4][0], mix[4][1], mix[4][2], 0.4)])
add("middle cluster only (Phi x 0.653 / H2 PIT 1.85-2.2)", [mix[2][:3] + (1.0,)])
add("all component sds doubled", [(m[0], m[1], m[2] * 2, m[3]) for m in mix])
add("all component sds halved", [(m[0], m[1], m[2] / 2, m[3]) for m in mix])
add("management centre 3.5 (2Q26-style +1 overshoot repeats)", [("mgmt", 3.5, 0.6, 0.30)] + [m[:3] + (m[3],) for m in mix[1:]])
add("management weight 0.50, others rescaled", [("mgmt", 3.0, 0.6, 0.50)] + [(m[0], m[1], m[2], m[3] * 0.50 / 0.70) for m in mix[1:]])
add("management weight 0.15, others rescaled", [("mgmt", 3.0, 0.6, 0.15)] + [(m[0], m[1], m[2], m[3] * 0.85 / 0.70) for m in mix[1:]])
add("not-stated 5%", mix, pns=0.05)
add("dollar -5% for the rest of the quarter (basket lag-0 term only; Phi specs unchanged)",
    [mix[0], mix[1], mix[2], ("free fit", 0.45 * (b0 - 0.8) + 0.36 * b1 + 0.03 * b2, 0.7, 0.15), ("contemp", 0.56 * (b0 - 0.8) - 0.21, 0.7, 0.05)])
s = pd.DataFrame(sens); s.to_csv(HERE / "c08_sensitivity.csv", index=False); print(s.to_string())

# ---- 5. management guided-FX track record (from the letters; integers = printed reported minus ex-FX growth) ---
track = pd.DataFrame([
    dict(guide_letter="2Q23", target="3Q23", guided="14-18% growth, 'a few points lower excluding the impact of FX' (~+2 to +3)", guided_num=2.5, printed=4),
    dict(guide_letter="3Q23", target="4Q23", guided="12-14% growth, 'relatively stable ... excluding the impact of FX' (implies ~+2)", guided_num=2.0, printed=3),
    dict(guide_letter="1Q24", target="2Q24", guided="'significant sequential headwind ... impact of FX rate changes' (headwind, small)", guided_num=-0.5, printed=0),
    dict(guide_letter="2Q24", target="3Q24", guided="'inclusive of a modest foreign exchange headwind'", guided_num=-0.5, printed=0),
    dict(guide_letter="3Q24", target="4Q24", guided="'inclusive of a modest foreign exchange tailwind'", guided_num=0.5, printed=0),
    dict(guide_letter="4Q24", target="1Q25", guided="4-6% growth, 'or 7% to 9% excluding the impact of FX' (-3)", guided_num=-3.0, printed=-2),
    dict(guide_letter="2Q25", target="3Q25", guided="'inclusive of minimal foreign exchange impact after factoring in our hedging program'", guided_num=0.0, printed=0),
    dict(guide_letter="3Q25", target="4Q25", guided="'inclusive of a small foreign exchange tailwind after factoring in our hedging program'", guided_num=0.5, printed=1),
    dict(guide_letter="4Q25", target="1Q26", guided="'inclusive of an approximate three point foreign exchange tailwind after factoring in our hedging program'", guided_num=3.0, printed=3),
    dict(guide_letter="1Q26", target="2Q26", guided="'inclusive of an approximate 3% FX tailwind after factoring in our hedging program'", guided_num=3.0, printed=4),
    dict(guide_letter="2Q26", target="3Q26", guided="'inclusive of an approximate three percentage point FX tailwind after factoring in our hedging program'", guided_num=3.0, printed=np.nan),
])
track["error_printed_minus_guided"] = track.printed - track.guided_num
track.to_csv(HERE / "c08_guide_track_record.csv", index=False)
t = track.dropna(); print(t[["target", "guided_num", "printed", "error_printed_minus_guided"]].to_string())
print("n", len(t), "mean err", round(t.error_printed_minus_guided.mean(), 2), "sd", round(t.error_printed_minus_guided.std(), 2),
      "printed >= guided:", int((t.printed >= t.guided_num).sum()), "printed < guided - 1:", int((t.printed < t.guided_num - 1).sum()))
