"""ADR audit (C3) - FX leg. Read-only against the engine: imports its modules, writes only to receipts/ADR_AUDIT.
Run from the worktree root:
    PYTHONPATH=analysis/src py -3.13 data/processed/pitch_model_v2/receipts/ADR_AUDIT/audit_fx.py
Post-hoc comparators P1..P5 are NOT promotable under adr_fx_prereg.md section 5; they exist only to test the C3 defence."""
from __future__ import annotations
import json
import pathlib
import numpy as np
import pandas as pd
from pitch_model_v2.adr_engine import config as C, fx_data as F, exposure as E, walkforward as W

R = pathlib.Path(__file__).resolve().parent
daily = F.load_daily(); shares = F.gbv_shares(); tg = F.disclosed_targets(); pdts = F.print_dates()
full = W.build_full_design(daily, shares, tg)
REG = C.REGIONS
POST = np.array([0.994, 1.199, 0.460, 1.266])   # final_adr.md 2.7 posterior means (PyMC not runnable on this machine)

# ---------- 1. forecast quarters under every variant, 21 Sep information set (fits on all 17 quarters) ----------
m1 = E.fit_v1_map(full[REG].values, full.y.values, full.h.values)
a2, b2 = E.fit_ols(full.eur_yoy.values, full.y.values)
a3, b3 = E.fit_ols(full.usd_broad_yoy.values, full.y.values)
fq = {}
for q in ["3Q26", "4Q26", "1Q27", "2Q27"]:
    x = F.design_row(daily, shares, q, None)
    Xt = np.array([x[r] for r in REG])
    fq[q] = {"V0_identity": Xt.sum(), "V1_MAP_all17": float(Xt @ m1["beta"]), "V1_posterior_mean": float(Xt @ POST),
             "V2_eur_ols_all17": a2 + b2 * x["eur_yoy"], "V3_broad_ols_all17": a3 + b3 * x["usd_broad_yoy"],
             "X_na": x["na"], "X_emea": x["emea"], "X_latam": x["latam"], "X_apac": x["apac"],
             "eur_yoy": x["eur_yoy"], "obs_frac": x["obs_frac"]}
fqd = pd.DataFrame(fq).T
print("V1 MAP beta (all 17):", np.round(m1["beta"], 3), "sigma", round(m1["sigma"], 3), "| V2 a,b:", round(a2, 3), round(b2, 3))
print(fqd.round(3).to_string())
fqd.to_csv(R / "C3_forecast_quarters_by_variant.csv")

path = pd.read_csv(C.OUT / "adr_path.csv", index_col=0)
rows = []
for q in ["3Q26", "4Q26"]:
    ex, by = float(path.loc[q, "adr_yoy_exfx_pct"]), float(path.loc[q, "adr_usd_base_year"])
    for v in ["V0_identity", "V1_MAP_all17", "V1_posterior_mean", "V2_eur_ols_all17", "V3_broad_ols_all17"]:
        fx = float(fqd.loc[q, v])
        rows.append({"quarter": q, "variant": v, "fx_pp": fx, "adr_usd": by * (1 + (ex + fx) / 100), "street": C.STREET_ADR[q][0]})
adr_fx = pd.DataFrame(rows); adr_fx["vs_street"] = adr_fx.adr_usd - adr_fx.street
print(adr_fx.round(3).to_string()); adr_fx.to_csv(R / "C3_adr_under_fx_variants.csv", index=False)

# ---------- 2. the identity's miss against its regional components (full information, descriptive) ----------
full["v0"] = full[REG].sum(axis=1); full["v0_err"] = full.v0 - full.y
print("\nfull-information (print-date) design, 17 quarters:")
print(full[["y", "h", "v0", "v0_err", "na", "emea", "latam", "apac", "eur_yoy"]].round(2).to_string())
full[["y", "h", "v0", "v0_err", "na", "emea", "latam", "apac", "eur_yoy", "usd_broad_yoy"]].to_csv(R / "C3_full_design_with_errors.csv")


# ---------- 3. post-hoc comparators on the identical PIT protocol ----------
def ols(A, y):
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return coef


recs = []
for q in C.WINDOWS["W1"]:
    for o, d in F.origin_dates(q, pdts).items():
        if d is None:
            continue
        tr = full[full.print_date <= d]
        if len(tr) < 3:
            continue
        xt = F.design_row(daily, shares, q, d); Xt = np.array([xt[r] for r in REG]); v0t = Xt.sum()
        yv = tr.y.values; v0tr = tr[REG].sum(axis=1).values
        em_tr = tr.latam.values + tr.apac.values; em_t = xt["latam"] + xt["apac"]
        preds = {"V0_translation": v0t,
                 "P1_identity_plus_intercept": v0t + float(np.mean(yv - v0tr)),
                 "P2_scaled_identity": float(ols(v0tr[:, None], yv)[0]) * v0t}
        c = ols(np.c_[np.ones(len(tr)), tr.eur_yoy.values, em_tr], yv) if len(tr) >= 4 else None
        preds["P3_eur_plus_LatAmAPAC_ols"] = float(c @ np.r_[1, xt["eur_yoy"], em_t]) if c is not None else np.nan
        c = ols(np.c_[tr.emea.values, tr.na.values + tr.latam.values + tr.apac.values], yv)
        preds["P4_two_block_EMEA_vs_rest"] = float(c @ np.r_[xt["emea"], xt["na"] + xt["latam"] + xt["apac"]])
        preds["P5_posterior_mean_weights_HINDSIGHT"] = float(Xt @ POST)
        a2t, b2t = E.fit_ols(tr.eur_yoy.values, yv); preds["V2_eur_ols"] = a2t + b2t * xt["eur_yoy"]
        preds["naive_last_disclosed"] = float(tr.y.iloc[-1])
        y = float(full.loc[q, "y"])
        for v, p in preds.items():
            recs.append({"quarter": q, "origin": o, "variant": v, "pred": p, "y": y, "err": p - y, "n_train": len(tr)})
wf = pd.DataFrame(recs); wf.to_csv(R / "C3_posthoc_walkforward.csv", index=False)
out = []
for w, qs in C.WINDOWS.items():
    for o in ["O1", "O2", "O3"]:
        s = wf[(wf.origin == o) & wf.quarter.isin(qs)]
        nv = s[s.variant == "naive_last_disclosed"].set_index("quarter").err
        for v, g in s.groupby("variant"):
            g = g.set_index("quarter").err.dropna(); en = nv.loc[g.index]
            out.append({"window": w, "origin": o, "variant": v, "n": len(g), "rmse": float(np.sqrt((g ** 2).mean())),
                        "ratio": float(np.sqrt((g ** 2).mean()) / np.sqrt((en ** 2).mean())), "bias": float(g.mean())})
sc = pd.DataFrame(out); sc.to_csv(R / "C3_posthoc_scores.csv", index=False)
print("\nRMSE ratio to naive (post-hoc comparators, identical PIT protocol):")
print(sc[sc.origin.isin(["O2", "O3"])].pivot_table(index="variant", columns=["window", "origin"], values="ratio").round(3).to_string())
print("\nbias (pp):")
print(sc[sc.origin.isin(["O2", "O3"])].pivot_table(index="variant", columns=["window", "origin"], values="bias").round(3).to_string())

# ---------- 4. error by episode ----------
w0 = pd.read_csv(C.OUT / "fx_pit_walkforward.csv")
ep = {"2023": ["1Q23", "2Q23", "3Q23", "4Q23"], "2024": ["1Q24", "2Q24", "3Q24", "4Q24"],
      "2025": ["1Q25", "2Q25", "3Q25", "4Q25"], "1H26": ["1Q26", "2Q26"], "4Q25-2Q26": ["4Q25", "1Q26", "2Q26"]}
r4 = []
for v in ["V0_translation", "V1_passthrough", "V2_eur_ols"]:
    for o in ["O2", "O3"]:
        for k, qs in ep.items():
            e = w0[(w0.variant == v) & (w0.origin == o) & w0.quarter.isin(qs)].err_pp
            r4.append({"variant": v, "origin": o, "episode": k, "mean_err": float(e.mean())})
r4 = pd.DataFrame(r4).pivot_table(index=["variant", "origin"], columns="episode", values="mean_err")[list(ep)]
print("\nmean error by episode (pred - disclosed, pp):"); print(r4.round(2).to_string()); r4.to_csv(R / "C3_bias_by_episode.csv")

# ---------- 5. divergence quarters: LatAm+APAC pp opposite in sign to EMEA pp ----------
full["div"] = np.sign(full.latam + full.apac) != np.sign(full.emea)
w3 = w0[(w0.origin == "O3") & w0.quarter.isin(C.WINDOWS["W1"])].pivot(index="quarter", columns="variant", values="err_pp")
w3 = w3.join(full[["div", "latam", "apac", "emea"]])
print("\nO3 errors, W1 quarters, split by divergence (LatAm+APAC opposite sign to EMEA):")
print(w3[["V0_translation", "V1_passthrough", "V2_eur_ols", "latam", "apac", "emea", "div"]].round(2).to_string())
g = w3.groupby("div")[["V0_translation", "V1_passthrough", "V2_eur_ols"]]
print(pd.concat({"mean": g.mean(), "rmse": g.apply(lambda d: np.sqrt((d ** 2).mean())), "n": g.count()}, axis=1).round(2).to_string())
json.dump({"v1_map_beta_all17": list(map(float, m1["beta"])), "v1_sigma": m1["sigma"], "v2_a": a2, "v2_b": b2, "v3_a": a3, "v3_b": b3},
          open(R / "C3_fits.json", "w"), indent=1)
