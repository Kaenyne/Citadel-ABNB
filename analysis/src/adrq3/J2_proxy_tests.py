"""
WS-J step 2: proxies for the 3Q26 like-for-like pricing residual.

Every candidate that has July-September 2026 coverage is turned into a quarterly y/y
history back to 2018-2023 and tested against two targets with the note-08 protocol:
  target A  residual_pricing_pp   (H card reconstruction, 1Q23-2Q26, n = 14)
  target B  adr_exfx_yoy_pp       (disclosed ex-FX ADR, 2Q22-2Q26, n = 17)
plus, as a secondary line, the disclosed regional ex-FX ADR of the region the proxy
covers (NA for US series, EMEA for euro-area and Spanish series).

Candidates
  cpi_lodging_sa        BLS CUSR0000SEHB, lodging away from home, SA, monthly to Aug 2026
  cpi_lodging_nsa       BLS CUUR0000SEHB, NSA, monthly to Aug 2026
  cpi_hotels_motels_nsa BLS CUUR0000SS62031, other lodging incl hotels/motels, NSA
  bea_hotels_price      BEA PCE price index, hotels and motels, monthly to Jul 2026
  hicp_ea_accommodation Eurostat prc_hicp_minr (ECOICOP v2), EA, CP112, monthly to Jul 2026
  ine_iph_spain         INE hotel price index, national, y/y, monthly to Jul 2026
  mar_revpar, hlt_revpar  worldwide comparable constant-currency RevPAR, quarterly to 2Q26
                        (reported 1-8 days before ABNB; no 3Q26 reading today)
  mgmt_adr_guide        management's ADR outlook wording for the quarter, coded on an
                        ordinal scale from the prior quarter's shareholder letter
  str_us_hotel_adr      CoStar/STR US hotel ADR y/y: 3Q26 readings only (G), one history
                        point (1Q26). No testable history is held; reported as a reading.
  ia_quote_seq          Inside Airbnb 13-city stay-quote per night, matched listings,
                        Jun -> Aug 2026 (2026 basis), with the Jun -> Sep 2025 listed-rate
                        analogue. Two points on two bases: descriptive only, not tested.

Transforms: level (quarter mean of monthly y/y) and first difference; lags 0 and 1.
Protocol per pair: Pearson r and p, Spearman, 1,000-shuffle permutation p, expanding
walk-forward OLS from 2024Q1 (fit strictly before t) scored by RMSE against naive
last quarter, prior year and AR(1) refit the same way, sign accuracy of the predicted
change, Bonferroni p over the tests run on that target, and a knowable-before-print flag.

Run: py -3.13 analysis/src/adrq3/J2_proxy_tests.py
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MAIN = r"C:\Users\krish\citadel-abnb"
OUT = os.path.join(HERE, "data", "processed", "adrq3", "J")
os.makedirs(OUT, exist_ok=True)
EXT = os.path.join(MAIN, "data", "raw", "external_prices")
RNG = np.random.default_rng(20260911)

QORDER = [f"{q}Q{str(y)[-2:]}" for y in range(2017, 2028) for q in range(1, 5)]
qi = {q: i for i, q in enumerate(QORDER)}


def to_q(month_str):
    d = pd.to_datetime(month_str)
    return f"{(d.month - 1) // 3 + 1}Q{str(d.year)[-2:]}"


# ----------------------------------------------------------------------------------
# 1. targets
# ----------------------------------------------------------------------------------
H = pd.read_csv(os.path.join(HERE, "data", "processed", "q3nowcast", "H", "adr_history_components.csv"))
hist = pd.read_csv(os.path.join(MAIN, "data", "processed", "adr", "02b_adr_history_extended.csv"))
reg = pd.read_csv(os.path.join(MAIN, "data", "processed", "adr", "04_regional_quarterly_wide.csv"))
targets = pd.DataFrame({"quarter": QORDER}).set_index("quarter")
targets["residual_pricing_pp"] = H.set_index("quarter")["residual_pricing_pp"]
targets["adr_exfx_yoy_pp"] = hist.set_index("quarter")["adr_yoy_exfx_final"]
targets["adr_reported_yoy_pp"] = hist.set_index("quarter")["adr_yoy_reported_pct"]
targets["adr_exfx_na_pp"] = reg.set_index("quarter")["adr_yoy_exfx_na_pct"]
targets["adr_exfx_emea_pp"] = reg.set_index("quarter")["adr_yoy_exfx_emea_pct"]
targets = targets[(targets.index.map(qi) >= qi["1Q22"]) & (targets.index.map(qi) <= qi["2Q26"])]

# ----------------------------------------------------------------------------------
# 2. monthly proxies -> quarterly y/y, plus the 3Q26 quarter-to-date reading
# ----------------------------------------------------------------------------------
monthly = {}

bls = pd.read_csv(os.path.join(HERE, "data", "processed", "q3nowcast", "G", "raw", "bls_cpi_travel_monthly.csv"))
for sid, name in (("CUSR0000SEHB", "cpi_lodging_sa"), ("CUUR0000SEHB", "cpi_lodging_nsa"),
                  ("CUUR0000SS62031", "cpi_hotels_motels_nsa")):
    s = bls[bls.series_id == sid].set_index(pd.to_datetime(bls[bls.series_id == sid].month))["value"].sort_index()
    monthly[name] = (100 * (s / s.shift(12) - 1)).dropna()

bea = pd.read_csv(os.path.join(MAIN, "data", "raw", "bea", "bea_pce_travel_monthly_2015_2026.csv"))
b = bea[(bea.series == "hotels_motels") & (bea.measure == "price_index_2017eq100")]
s = b.set_index(pd.to_datetime(b.date))["value"].sort_index()
monthly["bea_hotels_price"] = (100 * (s / s.shift(12) - 1)).dropna()

with open(os.path.join(EXT, "eurostat_prc_hicp_minr_EA_CP112_RCH_A.json")) as h:
    d = json.load(h)
inv = {str(i): k for k, i in d["dimension"]["time"]["category"]["index"].items()}
s = pd.Series({pd.to_datetime(inv[k]): v for k, v in d["value"].items()}).sort_index()
monthly["hicp_ea_accommodation"] = s

with open(os.path.join(EXT, "ine_iph_12157.json")) as h:
    d = json.load(h)
ser = [x for x in d if x["COD"] == "EOT14625"][0]["Data"]
s = pd.Series({pd.Timestamp(year=x["Anyo"], month=x["FK_Periodo"], day=1): x["Valor"] for x in ser}).sort_index()
monthly["ine_iph_spain"] = s

mon = pd.DataFrame(monthly)
mon.index.name = "month"
mon.to_csv(os.path.join(OUT, "J2_proxy_monthly.csv"))

panel = pd.DataFrame(index=targets.index)
readings = []
for name, s in monthly.items():
    s = s[s.index >= "2018-01-01"]
    qs = s.groupby(s.index.map(lambda t: f"{(t.month - 1) // 3 + 1}Q{str(t.year)[-2:]}"))
    full = qs.mean()
    cnt = qs.count()
    panel[name] = full.reindex(panel.index)
    # 3Q26 reading: whatever months are in
    q3 = s[(s.index >= "2026-07-01") & (s.index <= "2026-09-30")]
    readings.append({"proxy": name, "quarter": "3Q26", "reading_yoy_pct": float(q3.mean()) if len(q3) else np.nan,
                     "months_in": ",".join(t.strftime("%b") for t in q3.index),
                     "last_2q26_full_quarter": float(full.get("2Q26", np.nan)),
                     "knowable_before_5nov": "yes, September value publishes before 5 Nov"})

# quarterly-only proxies
mp = pd.read_csv(os.path.join(MAIN, "data", "processed", "adr", "06_measured_price_quarterly.csv")).set_index("quarter")
panel["mar_revpar"] = mp["mar_revpar_yoy"].reindex(panel.index)
panel["hlt_revpar"] = mp["hlt_revpar_yoy"].reindex(panel.index)
for name in ("mar_revpar", "hlt_revpar"):
    readings.append({"proxy": name, "quarter": "3Q26", "reading_yoy_pct": np.nan, "months_in": "",
                     "last_2q26_full_quarter": float(panel.at["2Q26", name]),
                     "knowable_before_5nov": "yes (reported 1-8 days before ABNB) but not held today"})

# management ADR outlook wording, coded from the prior quarter's letter (data/raw/letters)
# scale: -1 lower / slightly lower / pressure; 0 flat; 0.5 flat-to-slightly-up or stable-to-slightly-up;
#        1 slightly higher / modest(ly) up; 2 moderate increase. Reported-ADR basis unless noted.
GUIDE = [
    ("3Q22", 1, "slightly higher ADRs than Q3 2021", "2Q22 letter"),
    ("4Q22", -1, "ADR will face some pressure from FX headwinds and business mix", "3Q22 letter"),
    ("1Q23", -1, "slightly lower ADR than Q1 2022", "4Q22 letter"),
    ("2Q23", -1, "slightly lower ADR in Q2 2023 than Q2 2022", "1Q23 letter"),
    ("3Q23", 1, "drive a year-over-year increase in ADR in Q3 2023", "2Q23 letter"),
    ("4Q23", 0.5, "stable to slightly up", "3Q23 letter"),
    ("1Q24", 0.5, "flat to slightly up", "4Q23 letter"),
    ("2Q24", 1, "modestly up ... due to mix shift, partially offset by FX", "1Q24 letter"),
    ("3Q24", 1, "increase modestly", "2Q24 letter"),
    ("4Q24", 1, "increase modestly ... larger and higher priced listings, small FX benefit", "3Q24 letter"),
    ("1Q25", -1, "decline slightly, largely FX; ex-FX a slight increase (+0.5 ex-FX)", "4Q24 letter"),
    ("2Q25", 0, "approximately flat", "1Q25 letter"),
    ("3Q25", 1, "increase modestly, primarily driven by FX", "2Q25 letter"),
    ("4Q25", 1, "modest increase, primarily price appreciation and FX", "3Q25 letter"),
    ("1Q26", 2, "moderate increase in ADR due to price appreciation and FX", "4Q25 letter"),
    ("2Q26", 2, "moderate increase in ADR", "1Q26 letter"),
    ("3Q26", 2, "moderate increase in ADR due to mix shift and price appreciation", "2Q26 letter"),
]
g = pd.DataFrame(GUIDE, columns=["quarter", "code", "wording", "source"]).set_index("quarter")
g.to_csv(os.path.join(OUT, "J2_mgmt_adr_guide_coded.csv"))
panel["mgmt_adr_guide"] = g["code"].reindex(panel.index)
readings.append({"proxy": "mgmt_adr_guide", "quarter": "3Q26", "reading_yoy_pct": 2.0,
                 "months_in": "6 Aug letter", "last_2q26_full_quarter": 2.0,
                 "knowable_before_5nov": "yes (given 6 Aug)"})

# STR: readings only
strw = pd.read_csv(os.path.join(HERE, "data", "processed", "q3nowcast", "G", "str_weekly_us_3q26.csv"))
readings.append({"proxy": "str_us_hotel_adr_july_month", "quarter": "3Q26",
                 "reading_yoy_pct": float(strw.iloc[0]["adr_yoy_pct"]), "months_in": "Jul",
                 "last_2q26_full_quarter": np.nan, "knowable_before_5nov": "yes; no held history to test"})
aug = strw[(strw.week_start >= "2026-08-02") & (strw.week_start <= "2026-08-23")]["adr_yoy_pct"].dropna()
readings.append({"proxy": "str_us_hotel_adr_aug_weeks_mean", "quarter": "3Q26",
                 "reading_yoy_pct": float(aug.mean()), "months_in": "Aug weeks 2-29 (Labor Day week excluded)",
                 "last_2q26_full_quarter": np.nan, "knowable_before_5nov": "yes; no held history to test"})

panel.to_csv(os.path.join(OUT, "J2_proxy_quarterly_panel.csv"))

# ----------------------------------------------------------------------------------
# 3. Inside Airbnb sequential stay-quote drift, Jun -> Aug 2026 and Jun -> Sep 2025 (descriptive)
# ----------------------------------------------------------------------------------
import pyarrow.parquet as pq
IA = os.path.join(MAIN, "data", "raw", "inside_airbnb")
files = sorted(f for f in os.listdir(IA) if f.endswith("_listings.parquet"))


def dumps_for(market, ym):
    return sorted(f for f in files if f.startswith(market + "_" + ym))


def med_seq(fa, fb):
    a = pq.read_table(os.path.join(IA, fa), columns=["id", "price", "room_type", "price_basis"]).to_pandas()
    b = pq.read_table(os.path.join(IA, fb), columns=["id", "price", "room_type", "price_basis"]).to_pandas()
    m = a.merge(b, on="id", suffixes=("_a", "_b"))
    m = m[(m.price_a > 0) & (m.price_b > 0) & m.price_a.notna() & m.price_b.notna()]
    out = {}
    for seg, mm in (("all", m), ("entire", m[m.room_type_a.str.startswith("Entire")])):
        r = np.log(mm.price_b / mm.price_a)
        out[seg] = (100 * (np.exp(r.median()) - 1), int(len(r)))
    return out, str(a.price_basis.iloc[0]), str(b.price_basis.iloc[0])


seq = []
markets = sorted({f.split("_")[0] for f in files})
for mk in markets:
    for ya, yb, label in (("2025-06", "2025-09", "jun_sep_2025_listed"), ("2026-06", "2026-08", "jun_aug_2026_quote")):
        A, B = dumps_for(mk, ya), dumps_for(mk, yb)
        if not A or not B:
            continue
        try:
            o, ba, bb = med_seq(A[-1], B[-1])
        except Exception as e:  # noqa: BLE001
            print("skip", mk, label, e)
            continue
        for seg, (v, n) in o.items():
            seq.append({"market": mk, "window": label, "dump_a": A[-1], "dump_b": B[-1], "basis_a": ba, "basis_b": bb,
                        "segment": seg, "matched_listings": n, "median_seq_change_pct": v})
seq = pd.DataFrame(seq)
seq.to_csv(os.path.join(OUT, "J2_ia_quote_sequential.csv"), index=False)
if len(seq):
    for (w, sgm), gg in seq.groupby(["window", "segment"]):
        readings.append({"proxy": f"ia_quote_seq_{w}_{sgm}", "quarter": "3Q26" if "2026" in w else "3Q25",
                         "reading_yoy_pct": float(gg.median_seq_change_pct.mean()),
                         "months_in": f"{gg.market.nunique()} markets, mean of market medians",
                         "last_2q26_full_quarter": np.nan,
                         "knowable_before_5nov": "sequential only; no y/y and no history; not tested"})
pd.DataFrame(readings).to_csv(os.path.join(OUT, "J2_proxy_readings_3q26.csv"), index=False)

# ----------------------------------------------------------------------------------
# 4. note-08 protocol tests
# ----------------------------------------------------------------------------------
KNOWABLE = {"cpi_lodging_sa": "yes", "cpi_lodging_nsa": "yes", "cpi_hotels_motels_nsa": "yes",
            "bea_hotels_price": "yes (advance Q estimate ~30 Oct; Jul-Aug monthly by end-Sep)",
            "hicp_ea_accommodation": "yes", "ine_iph_spain": "yes",
            "mar_revpar": "yes, reports before ABNB", "hlt_revpar": "yes, reports before ABNB",
            "mgmt_adr_guide": "yes, prior print"}
SECONDARY = {"cpi_lodging_sa": "adr_exfx_na_pp", "cpi_lodging_nsa": "adr_exfx_na_pp",
             "cpi_hotels_motels_nsa": "adr_exfx_na_pp", "bea_hotels_price": "adr_exfx_na_pp",
             "hicp_ea_accommodation": "adr_exfx_emea_pp", "ine_iph_spain": "adr_exfx_emea_pp"}


def perm_p(x, y, n=1000):
    r0 = abs(np.corrcoef(x, y)[0, 1])
    cnt = 0
    for _ in range(n):
        if abs(np.corrcoef(RNG.permutation(x), y)[0, 1]) >= r0:
            cnt += 1
    return (cnt + 1) / (n + 1)


def walk_forward(x, y, start_q, min_train=4):
    """x, y indexed by quarter (aligned, no NaN). Expanding OLS from start_q."""
    qs = list(y.index)
    rows = []
    for t in qs:
        if qi[t] < qi[start_q]:
            continue
        prior = [q for q in qs if qi[q] < qi[t]]
        if len(prior) < min_train:
            continue
        b1, b0 = np.polyfit(x[prior].values, y[prior].values, 1)
        pred = b0 + b1 * x[t]
        naive = y[prior[-1]]
        py = y.get(QORDER[qi[t] - 4], np.nan)
        yy = y[prior].values
        a1, a0 = np.polyfit(yy[:-1], yy[1:], 1) if len(yy) >= 4 else (0.0, yy.mean())
        ar1 = a0 + a1 * y[prior[-1]]
        rows.append({"quarter": t, "actual": y[t], "pred": pred, "naive": naive, "prior_year": py, "ar1": ar1})
    w = pd.DataFrame(rows)
    if len(w) < 4:
        return None, w
    rm = lambda c: float(np.sqrt(((w[c] - w.actual) ** 2).mean()))  # noqa: E731
    res = {"wf_n": len(w), "wf_rmse_model": rm("pred"), "wf_rmse_naive": rm("naive"),
           "wf_rmse_prior_year": rm("prior_year"), "wf_rmse_ar1": rm("ar1")}
    res["wf_ratio_vs_naive"] = res["wf_rmse_model"] / res["wf_rmse_naive"]
    res["wf_ratio_vs_ar1"] = res["wf_rmse_model"] / res["wf_rmse_ar1"]
    res["wf_ratio_vs_prior_year"] = res["wf_rmse_model"] / res["wf_rmse_prior_year"]
    sgn = np.sign(w.pred - w.naive) == np.sign(w.actual - w.naive)
    res["wf_sign_accuracy"] = float(sgn[(w.actual - w.naive) != 0].mean()) if ((w.actual - w.naive) != 0).any() else np.nan
    return res, w


tests, paths = [], []
for feat in [c for c in panel.columns]:
    for transform in ("level", "diff"):
        f = panel[feat].astype(float)
        if transform == "diff":
            f = f.diff()
        for lag in (0, 1):
            fl = f.shift(lag)
            tlist = ["residual_pricing_pp", "adr_exfx_yoy_pp"]
            if feat == "mgmt_adr_guide":
                tlist.append("adr_reported_yoy_pp")
            if feat in SECONDARY:
                tlist.append(SECONDARY[feat])
            for tgt in tlist:
                for window in ("2023Q1+", "2022Q1+"):
                    if tgt == "residual_pricing_pp" and window == "2022Q1+":
                        continue
                    lo = "1Q23" if window == "2023Q1+" else "1Q22"
                    df = pd.DataFrame({"x": fl, "y": targets[tgt]}).dropna()
                    df = df[df.index.map(qi) >= qi[lo]]
                    if len(df) < 6:
                        continue
                    r, p = stats.pearsonr(df.x, df.y)
                    rs = stats.spearmanr(df.x, df.y).correlation
                    pp = perm_p(df.x.values, df.y.values)
                    wf, w = walk_forward(df.x, df.y, "1Q24")
                    row = {"feature": feat, "transform": transform, "lag": lag, "target": tgt, "window": window,
                           "n": len(df), "first_q": df.index[0], "last_q": df.index[-1],
                           "pearson_r": r, "p": p, "spearman_r": rs, "perm_p": pp,
                           "knowable_before_print": KNOWABLE.get(feat, "")}
                    if wf:
                        row.update(wf)
                        w["feature"], w["transform"], w["lag"], w["target"], w["window"] = feat, transform, lag, tgt, window
                        paths.append(w)
                    tests.append(row)
tests = pd.DataFrame(tests)
for tgt, gg in tests.groupby("target"):
    tests.loc[gg.index, "n_tests_on_target"] = len(gg)
    tests.loc[gg.index, "p_bonferroni"] = np.minimum(1.0, gg.p * len(gg))
tests["flagged_r"] = (tests.pearson_r.abs() > 0.5) & (tests.perm_p < 0.05)
tests["beats_naive"] = tests.get("wf_ratio_vs_naive", np.nan) < 1
tests["beats_naive_and_ar1"] = (tests.get("wf_ratio_vs_naive", np.nan) < 1) & (tests.get("wf_ratio_vs_ar1", np.nan) < 1)
tests["survivor"] = tests.flagged_r & tests.beats_naive_and_ar1 & (tests.get("wf_n", 0) >= 6)
tests = tests.sort_values(["target", "wf_ratio_vs_naive"])
tests.to_csv(os.path.join(OUT, "proxy_tests.csv"), index=False)
pd.concat(paths, ignore_index=True).to_csv(os.path.join(OUT, "J2_walk_forward_paths.csv"), index=False)

pd.set_option("display.width", 250)
print("\n3Q26 readings\n", pd.DataFrame(readings).to_string())
print("\nquarterly panel tail\n", panel.tail(8).round(2).to_string())
cols = ["feature", "transform", "lag", "target", "window", "n", "pearson_r", "perm_p", "p_bonferroni",
        "wf_n", "wf_ratio_vs_naive", "wf_ratio_vs_ar1", "wf_sign_accuracy", "flagged_r", "survivor"]
print("\nresidual tests (2023Q1+)\n", tests[tests.target == "residual_pricing_pp"][cols].round(3).to_string())
print("\nex-FX tests (2023Q1+)\n", tests[(tests.target == "adr_exfx_yoy_pp") & (tests.window == "2023Q1+")][cols].round(3).to_string())
print("\nsurvivors:", int(tests.survivor.sum()), "of", len(tests), "tests; beat naive:", int(tests.beats_naive.sum()),
      "; beat naive and AR1:", int(tests.beats_naive_and_ar1.sum()), "; flagged:", int(tests.flagged_r.sum()))
print(tests[tests.survivor][cols].round(3).to_string())
